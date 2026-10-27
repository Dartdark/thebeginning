"""Frozen independent six-leg EUR reconstruction, not author-code parity.

Shared Grid24/calendar/metrics/resampling; new FIFO cash ledger supplies the
multi-day virtual-leg/net-position capability absent from intraday grid.execute.
No actual market data are loaded at import or by --selftest.
"""
from __future__ import annotations
import argparse
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import warnings
from collections import deque

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_six_e_rebuild_20261027"
PLAN = "agents/codex/plans/six_e_rebuild_20261027.md"
os.environ["NUMBA_CACHE_DIR"] = str(OUT / "cache/numba")
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "analysis"))
import numpy as np
import pandas as pd
from grid24 import Grid24, jof
from codex_s03_calendar import calendar_status
import metrics as M
import resampling as R
import montecarlo as MC
from codex_hunt_v2_ldf_delta import tstat
from codex_hunt_v2_ldf_delta_design import nw_t

ASSETS = ("6E", "ZN", "CL", "ES", "GC")
LEGS = ("Macro", "RSI2", "Weekly", "MacroShock", "StockShock", "GoldShock")
FIELDS = ("open", "high", "low", "close", "volume")
PV, FEE, TICK = 12500., 1.20, Decimal("0.0001")


def sha(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda: f.read(4*1024*1024), b""): h.update(b)
    return h.hexdigest()


def clean(x):
    if isinstance(x, dict): return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [clean(v) for v in x]
    if isinstance(x, np.generic): return clean(x.item())
    if isinstance(x, float) and not np.isfinite(x): return None
    return x


def dump(p, x):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("x") as f: json.dump(clean(x), f, indent=2, allow_nan=False); f.write("\n")


def csv(p, frame):
    with Path(p).open("x") as f: frame.to_csv(f, index=False, float_format="%.12g")


def order_price(raw, side):
    if raw <= 0 or side not in (-1, 1): raise ValueError("Invalid EUR fill input")
    mode = ROUND_CEILING if side > 0 else ROUND_FLOOR
    return float((Decimal(str(raw))/TICK).to_integral_value(rounding=mode)*TICK + side*TICK)


def wilder_rsi(values):
    result = np.full(len(values), np.nan)
    up = down = None; seed = []
    for i in range(1, len(values)):
        if not np.isfinite(values[i-1:i+1]).all():
            up = down = None; seed = []; continue
        change = values[i]-values[i-1]; u, d = max(change, 0.), max(-change, 0.)
        if up is None:
            seed.append((u, d))
            if len(seed) < 2: continue
            up, down = np.mean(seed, axis=0)
        else: up, down = .5*up+.5*u, .5*down+.5*d
        result[i] = 50. if up == down == 0 else 100. if down == 0 else 100.-100./(1.+up/down)
    return result


def lag_z(series):
    return (series-series.rolling(60, min_periods=60).mean().shift(1))/series.rolling(60, min_periods=60).std(ddof=1).shift(1)


def features(daily):
    x = daily.copy()
    for s in ASSETS:
        c = x[s+"_close"]
        # pandas sum/mean must not silently drop a missing horizon.
        signs = pd.concat([np.sign(c-c.shift(h)) for h in (10,21,63)], axis=1)
        x[s+"_trend"] = signs.sum(axis=1, min_count=3)/3.
        x[s+"_change"] = c.diff()
        x[s+"_z"] = lag_z(x[s+"_change"])
    x["macro_score"] = (x.ZN_trend-x.CL_trend-x.ES_trend)/3.
    x["eur_vol"] = (x["6E_close"]/x["6E_close"].shift(1)-1).rolling(60,min_periods=60).std(ddof=1)*np.sqrt(252)
    x["vol_multiplier"] = np.minimum(1.5, .05/x.eur_vol)
    x["rsi2"] = wilder_rsi(x["6E_close"].to_numpy())
    x["sma5"] = x["6E_close"].rolling(5,min_periods=5).mean()
    x["reaction_z"] = lag_z(x["eur_reaction"])
    highs, lows = [], []
    for d in x.index:
        start = d-pd.Timedelta(days=d.weekday()+7); end=start+pd.Timedelta(days=6)
        prev = x.loc[(x.index >= start) & (x.index <= end)]
        expected = [t for t in pd.date_range(start,end) if calendar_status(t)["kind"]=="normal"]
        ok = len(prev)==len(expected)>0 and prev[["eur_high","eur_low"]].notna().all().all()
        highs.append(prev.eur_high.max() if ok else np.nan); lows.append(prev.eur_low.min() if ok else np.nan)
    x["week_high"],x["week_low"] = highs,lows
    required = ["macro_score","eur_vol","vol_multiplier","rsi2","sma5","week_high","week_low",
                "ZN_z","ES_z","GC_z","reaction_z","eur_fill"]
    x["ready"] = np.isfinite(x[required]).all(axis=1) & (x.eur_vol > 0)
    return x


def targets(f):
    q = np.zeros((len(f),7),np.int64)
    rsi_pos=weekly_pos=0; rsi_age=weekly_age=0
    for i,row in enumerate(f.itertuples(index=False)):
        # Use named columns, including 6E-prefixed names which itertuples renames.
        a=f.iloc[i]
        if not a.ready:
            rsi_pos=weekly_pos=0; rsi_age=weekly_age=0; continue
        direction=int(np.sign(a.macro_score))
        q[i,0]=int(np.trunc(2*a.macro_score*a.vol_multiplier))
        q[i,6]=int(np.trunc(2*a["6E_trend"]*a.vol_multiplier))
        if rsi_pos:
            rsi_age+=1
            if rsi_age>=10 or (rsi_pos>0 and a["6E_close"]>=a.sma5) or (rsi_pos<0 and a["6E_close"]<=a.sma5):
                rsi_pos=0; rsi_age=0
        elif direction>0 and a.rsi2<10: rsi_pos=1; rsi_age=0
        elif direction<0 and a.rsi2>90: rsi_pos=-1; rsi_age=0
        if weekly_pos:
            weekly_age+=1
            if weekly_age>=10 or (weekly_pos>0 and a["6E_close"]<=a.week_low) or (weekly_pos<0 and a["6E_close"]>=a.week_high):
                weekly_pos=0; weekly_age=0
        elif direction>0 and a["6E_close"]>a.week_high: weekly_pos=1; weekly_age=0
        elif direction<0 and a["6E_close"]<a.week_low: weekly_pos=-1; weekly_age=0
        q[i,1],q[i,2]=rsi_pos,weekly_pos
        z = int(np.sign(a.ZN_z)) if abs(a.ZN_z)>2 else 0
        e = int(np.sign(a.reaction_z)) if abs(a.reaction_z)>2 else 0
        q[i,3]=2*(z or e) if not(z and e and z!=e) else 0
        q[i,4]=int(np.sign(a.ES_z)) if abs(a.ES_z)>2.5 else 0
        q[i,5]=2*int(np.sign(a.GC_z)) if abs(a.GC_z)>2.25 else 0
    # Offline source/sample boundary liquidation, explicitly not an executable
    # prediction of a future outage. It is a LIMIT on promotion, never a filter.
    ends = np.flatnonzero(f.ready.to_numpy() & ~np.r_[f.ready.to_numpy()[1:],False])
    q[ends,:]=0
    return q, ends


def gross_curve(prices, quantities, ready):
    output=np.zeros(len(prices)); old=0; previous=None
    for i in range(len(prices)):
        if not ready[i]:
            assert old==0
            previous=None;continue
        if previous is not None: output[i]=old*(prices[i]-previous)*PV
        old=int(quantities[i]);previous=prices[i]
    assert old==0
    turnover=np.abs(np.diff(np.r_[0,quantities])).sum()
    return output,int(turnover)


def ledger(prices, quantities, ready, dates, model):
    cash=0.;pos=0;previous_nav=0.;previous_raw=None;lots=deque();rows=[];trades=[];orders=[]
    for i in range(len(prices)):
        if not ready[i]:
            assert pos==0 and not lots
            continue
        raw=float(prices[i]);target=int(quantities[i]);delta=target-pos
        carry=pos*(raw-previous_raw)*PV if previous_raw is not None else 0.
        friction=fees=0.
        if delta:
            side=int(np.sign(delta));fill=order_price(raw,side);fees=abs(delta)*FEE
            friction=delta*(fill-raw)*PV
            cash-=delta*fill*PV+fees
            orders.append(dict(model=model,date=str(dates[i].date()),delta=delta,target=target,
                               raw=raw,fill=fill,fee=fees,projection_and_slippage=friction))
            for _ in range(abs(delta)):
                if lots and lots[0][0]!=side:
                    sign,entry,raw_entry,entry_i=lots.popleft()
                    net=(fill-entry)*sign*PV-2*FEE
                    trades.append(dict(model=model,entry_date=str(dates[entry_i].date()),date=str(dates[i].date()),
                        side=sign,contracts=1,entry=entry,exit=fill,raw_entry=raw_entry,raw_exit=raw,
                        gross=(raw-raw_entry)*sign*PV,net=net,hold_decisions=i-entry_i))
                else: lots.append((side,fill,raw,i))
        pos=target;nav=cash+pos*raw*PV;net=nav-previous_nav
        if not np.isclose(net,carry-friction-fees,atol=1e-6): raise ValueError("Cash/mark reconciliation failed")
        rows.append(dict(model=model,date=str(dates[i].date()),position=pos,delta=delta,raw=raw,
                         gross=carry,projection_slippage=friction,fees=fees,net=net,nav=nav))
        previous_nav=nav;previous_raw=raw
    assert pos==0 and not lots
    if not np.isclose(sum(t["net"] for t in trades),sum(r["net"] for r in rows),atol=1e-5):
        raise ValueError("FIFO trades do not reconcile with daily marked PnL")
    return pd.DataFrame(rows),pd.DataFrame(trades,columns=["model","entry_date","date","side","contracts","entry","exit","raw_entry","raw_exit","gross","net","hold_decisions"]),pd.DataFrame(orders)


def selftest():
    p=np.array([1.1,1.11,1.09,1.1]);d=pd.date_range("2030-01-01",periods=4)
    q=np.array([2,-2,-2,0]);ready=np.ones(4,bool)
    a,t,o=ledger(p,q,ready,d,"invented")
    assert o.delta.tolist()==[2,-4,2] and np.isclose(o.fee.sum(),9.6)
    assert len(t)==4 and set(t.side)=={-1,1}
    assert np.isclose(a.net.sum(),t.net.sum())
    assert np.isclose(order_price(1.10005,1),1.1002) and np.isclose(order_price(1.10005,-1),1.0999)
    zero,turn=gross_curve(p,np.zeros(4,int),ready);assert not zero.any() and turn==0
    assert np.isclose(wilder_rsi(np.array([1.,2.,3.,2.]))[2],100)
    q2=np.array([1,0,0,0]);r2=np.array([True,True,False,False]);a2,t2,o2=ledger(p,q2,r2,d,"gap_fixture")
    assert len(t2)==1 and a2.position.iloc[-1]==0
    # Exact integer idle is intentional; no implicit one-contract minimum.
    assert int(np.trunc(2*(1/9)*.5))==0
    # Lagged shock baseline excludes today's extreme observation.
    s=pd.Series(np.sin(np.arange(70,dtype=float)));z=lag_z(s);s.iloc[-1]=1000
    assert np.isclose(z.iloc[-2],lag_z(s).iloc[-2])
    a3,t3,o3=ledger(p,np.array([2,1,-1,0]),ready,d,"partial_FIFO")
    assert len(t3)==3 and np.isclose(o3.fee.sum(),7.2) and np.isclose(t3.net.sum(),a3.net.sum())
    days=pd.bdate_range("2030-01-01",periods=150);idx=np.arange(150.)
    fixture=pd.DataFrame(index=days)
    for k,name in enumerate(ASSETS):fixture[name+"_close"]=1+idx*.001+np.sin(idx+k)*.01
    fixture["CL_close"]=-10+idx*.1  # Crosses zero without log or percent-CL assumptions.
    fixture["eur_fill"]=fixture["6E_close"];fixture["eur_reaction"]=np.sin(idx)*.001
    fixture["eur_high"]=fixture["6E_close"]+.001;fixture["eur_low"]=fixture["6E_close"]-.001
    f=features(fixture);assert f.ready.any()
    future=fixture.copy();future.iloc[120:,0]=1000
    np.testing.assert_allclose(f.iloc[:110].macro_score,features(future).iloc[:110].macro_score,equal_nan=True)
    at=int(np.flatnonzero(f.ready.to_numpy())[0]);f.iloc[at,f.columns.get_loc("ZN_z")]=3
    f.iloc[at,f.columns.get_loc("reaction_z")]=-3
    q,ends=targets(f);assert q[at,3]==0 and (np.abs(q[:,0])<=3).all() and not q[ends].any()
    return dict(passed=True,groups=11,market_inputs=False,integer_reversals=True,FIFO_cash_mark_parity=True,
                adverse_native_grid=True,unknown_block_boundaries_explicit=True)


def load_asset(symbol, paths, calendar, folder):
    parts=[]
    for path in paths:
        x=pd.read_csv(path,usecols=["date","time",*FIELDS]);x["source"]=str(path.relative_to(ROOT));x["line"]=np.arange(len(x))+2;parts.append(x)
    raw=pd.concat(parts,ignore_index=True)
    duplicates=raw[raw.duplicated(["date","time"],keep=False)]
    conflicts=duplicates.groupby(["date","time"])[list(FIELDS)].nunique(dropna=False).gt(1).any(axis=1)
    bad=set(conflicts[conflicts].index.tolist())
    x=raw.drop_duplicates(["date","time"]).sort_values(["date","time"])
    vals=x[list(FIELDS)].to_numpy(float);o,h,l,c,v=vals.T
    valid=np.isfinite(vals).all(axis=1)&(l<=np.minimum(o,c))&(h>=np.maximum(o,c))&(h>=l)&(v>=0)
    if symbol!="CL":valid&=(vals[:,:4]>0).all(axis=1)
    valid&=np.array([(d,t) not in bad for d,t in zip(x.date,x.time)])
    times=x.time.to_numpy();assert ((times%100<60)&(times>=0)&(times<2400)).all()
    csv(folder/(symbol+"_duplicates.csv"),duplicates);csv(folder/(symbol+"_invalid.csv"),x[~valid])
    cache=OUT/"cache"/symbol;cache.mkdir(parents=True,exist_ok=True)
    for source in paths:
        link=cache/source.name
        if link.is_symlink():assert link.resolve()==source.resolve()
        elif link.exists():raise ValueError("Unexpected cache source")
        else:link.symlink_to(source)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore",RuntimeWarning);g=Grid24(str(cache/"*.csv"),night_pattern="")
    rr=np.searchsorted(g.dates,x.date.to_numpy());jj=jof(x.time.to_numpy()).astype(int)
    for name,attr in zip(FIELDS,"ohlcv"):
        assert np.allclose(getattr(g,attr)[rr,jj],x[name].to_numpy(float),equal_nan=True)
    for attr in "ohlcv":getattr(g,attr)[rr[~valid],jj[~valid]]=np.nan
    lookup={int(d):r for r,d in enumerate(g.dates)};records=[];last_cut=None
    for d in calendar:
        r=lookup.get(int(d.strftime("%Y%m%d")));close=fill=reaction=high=low=np.nan;minutes=0
        if r is not None:
            close=g.c[r,900]
            if symbol=="6E":
                fill=g.o[r,902];reaction=g.c[r,510]-g.c[r,449]
                if last_cut is not None:
                    sl=slice(last_cut+1,r*1440+901);hh=g.h.ravel()[sl];ll=g.l.ravel()[sl]
                    minutes=int(np.isfinite(hh).sum())
                    if minutes:high=np.nanmax(hh);low=np.nanmin(ll)
                last_cut=r*1440+900
        elif symbol=="6E":last_cut=None
        records.append(dict(date=d,close=close,fill=fill,reaction=reaction,high=high,low=low,observed_range_minutes=minutes))
    audit=dict(symbol=symbol,source_rows=len(raw),unique_rows=len(x),duplicate_rows=len(duplicates),
        conflicting_keys=len(bad),invalid_observed_rows=int((~valid).sum()),negative_CL_supported=symbol=="CL",
        missing_1500_cuts=int(pd.isna([r["close"] for r in records]).sum()),
        first_native_date=int(x.date.min()),last_native_date=int(x.date.max()),contract_ID_present=False,
        minute_gap_count_not_assumed_to_equal_feed_loss=True)
    return pd.DataFrame(records).set_index("date"),audit


def metrics(daily,trades,model,period):
    m=M.perf(np.r_[0.,daily],trades.net if len(trades) else [])
    actual=M.perf(daily,trades.net if len(trades) else [])
    for k in ("annual","sharpe","sortino"):m[k]=actual[k]
    m["calmar"]=m["annual"]/m["max_dd"] if m["max_dd"] else None
    m.update(model=model,period=period,total=float(daily.sum()),trade_t=tstat(trades.net) if len(trades) else None,
        daily_NW5_t=nw_t(daily.to_numpy()),DSR_N326=M.deflated_sharpe(daily,326) if len(daily)>10 else None,
        DSR_N1000_scenario=M.deflated_sharpe(daily,1000) if len(daily)>10 else None,
        long_units=int(trades.side.eq(1).sum()) if len(trades) else 0,short_units=int(trades.side.eq(-1).sum()) if len(trades) else 0,
        daily_dates=len(daily),trade_units_not_independent_bets=True)
    return m


def run(prereg,public_prereg):
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()=="codex/work"
    subprocess.check_call(["git","merge-base","--is-ancestor",prereg,"HEAD"],cwd=ROOT)
    assert subprocess.check_output(["git","show",prereg+":"+PLAN],cwd=ROOT)==(ROOT/PLAN).read_bytes()
    script="analysis/codex_six_e_rebuild.py"
    assert subprocess.check_output(["git","show","HEAD:"+script],cwd=ROOT)==Path(__file__).read_bytes()
    dest=OUT/"design"
    if dest.exists():raise ValueError("Retained design attempt exists; no automatic overwrite/retry")
    paths={s:[ROOT/f"data/{s}_1min_{y}.csv" for y in range(2017,2023)] for s in ASSETS}
    for group in paths.values():
        for p in group:
            if not p.is_file():raise FileNotFoundError(p)
    deps=[PLAN,script,"analysis/grid24.py","analysis/codex_s03_calendar.py","analysis/metrics.py","analysis/resampling.py","analysis/codex_hunt_v2_ldf_delta_design.py"]
    binding=dict(preregistration_local=prereg,preregistration_public=public_prereg,
        implementation_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        started_utc=datetime.now(timezone.utc).isoformat(),files={str(p.relative_to(ROOT)):dict(sha256=sha(p),bytes=p.stat().st_size) for ps in paths.values() for p in ps},
        code={p:sha(ROOT/p) for p in deps},future2023_values_loaded=False,python=sys.version,numpy=np.__version__,pandas=pd.__version__)
    dest.mkdir(parents=True);dump(dest/"pre_value_binding.json",binding);dump(dest/"synthetic_checks.json",selftest())
    cal=pd.DatetimeIndex([d for d in pd.date_range("2017-12-01","2022-12-31") if calendar_status(d)["kind"]=="normal"])
    source=pd.DataFrame(index=cal);audits=[]
    for s in ASSETS:
        daily,audit=load_asset(s,paths[s],cal,dest);source[s+"_close"]=daily.close;audits.append(audit)
        if s=="6E":
            source["eur_fill"]=daily.fill;source["eur_reaction"]=daily.reaction
            source["eur_high"]=daily.high;source["eur_low"]=daily.low
            source["observed_range_minutes"]=daily.observed_range_minutes
    dump(dest/"source_audit.json",audits);csv(dest/"daily_inputs.csv",source.rename_axis("date").reset_index())
    f=features(source);q,ends=targets(f)
    # Design has no position in2017; warmup values remain causal inputs only.
    active=(f.index.year>=2018)&f.ready.to_numpy();q[~active]=0
    f["active_design"]=active
    for k,name in enumerate((*LEGS,"OwnEURControl")):f[name+"_target"]=q[:,k]
    f["Package_target"]=q[:,:6].sum(axis=1)
    csv(dest/"features_and_targets.csv",f.rename_axis("date").reset_index())
    if active.sum()<2:
        result=dict(status="SOURCE_BLOCKED_NO_DESIGN_RETURNS",active_known_dates=int(active.sum()),
                    expected_design_dates=int((f.index.year>=2018).sum()),future_returns_run=False,
                    source_audit=audits,hunt_v2_changed=False)
        dump(dest/"completed.json",result);print(json.dumps(clean(result),indent=2));return
    modelq={name:q[:,i] for i,name in enumerate((*LEGS,"OwnEURControl"))};modelq["Package"]=q[:,:6].sum(axis=1)
    prices=f.eur_fill.to_numpy();gross_rows=[]
    for name,qty in modelq.items():
        gross,turn=gross_curve(prices,qty,active);rt=turn/2
        gross_rows.append(dict(model=name,total_gross=gross.sum(),equivalent_RT_units=rt,
            gross_per_equivalent_RT=gross.sum()/rt if rt else None,gross_daily_t=tstat(gross[active]),
            minimum_2x_RT_hurdle=9.80,gross_gate_pass=bool(rt>0 and gross.sum()/rt>=9.80)))
    csv(dest/"gross_screen.csv",pd.DataFrame(gross_rows))
    rows=[];by_side=[];netdaily={};alltrades={};order_totals={}
    for name,qty in modelq.items():
        d,t,o=ledger(prices,qty,active,f.index,name)
        if d.empty:
            d=pd.DataFrame(dict(model=name,date=f.index[active].strftime("%Y-%m-%d"),position=0,delta=0,raw=prices[active],gross=0.,projection_slippage=0.,fees=0.,net=0.,nav=0.))
        csv(dest/(name+"_daily.csv"),d);csv(dest/(name+"_trades.csv"),t);csv(dest/(name+"_orders.csv"),o)
        series=d.set_index(pd.to_datetime(d.date)).net
        netdaily[name]=series;alltrades[name]=t;order_totals[name]=float(d.projection_slippage.sum()+d.fees.sum())
        for period in ("2018-22",*map(str,range(2018,2023))):
            mask=np.ones(len(series),bool) if period=="2018-22" else series.index.year==int(period)
            sub=t if period=="2018-22" else t[pd.to_datetime(t.date).dt.year==int(period)]
            rows.append(metrics(series[mask],sub,name,period))
        for side in (1,-1):
            sub=t[t.side==side];booked=sub.groupby("date").net.sum() if len(sub) else pd.Series(dtype=float)
            booked.index=pd.to_datetime(booked.index);sd=booked.reindex(series.index,fill_value=0.)
            by_side.append(dict(side="long" if side==1 else "short",basis="realized exit-date unit PnL, not a daily side-marked equity",**metrics(sd,sub,name,"2018-22")))
    m=pd.DataFrame(rows);csv(dest/"metrics.csv",m);csv(dest/"side_metrics.csv",pd.DataFrame(by_side))
    combined=pd.DataFrame(netdaily);csv(dest/"net_daily.csv",combined.rename_axis("date").reset_index())
    comp=m[(m.period=="2018-22")&m.model.isin(LEGS)]
    pack=m[(m.period=="2018-22")&m.model.eq("Package")].iloc[0]
    positive_years=int(((m.model=="Package")&(m.period!="2018-22")&(m.total>0)).sum())
    allgross=all(g["gross_gate_pass"] for g in gross_rows if g["model"] in LEGS)
    gate=bool(allgross and (comp.total>0).all() and (comp.trades>=30).all() and pack.total>0 and (pack.daily_NW5_t or 0)>=2 and positive_years>=4)
    source_missing=int(f.loc[f.index.year>=2018,[s+"_close" for s in ASSETS]+["eur_fill","eur_reaction"]].isna().any(axis=1).sum())
    blocks=int((active&~np.r_[False,active[:-1]]).sum())
    dump(dest/"cash_reconciliation.json",dict(all_FIFO_vs_daily_checked=True,
        standalone_components_total=sum(float(netdaily[n].sum()) for n in LEGS),net_broker_package_total=float(netdaily["Package"].sum()),
        netting_cost_saving=sum(order_totals[n] for n in LEGS)-order_totals["Package"],
        gross_price_paths_reconcile=bool(np.isclose(sum(pd.read_csv(dest/(n+"_daily.csv")).gross.sum() for n in LEGS),pd.read_csv(dest/"Package_daily.csv").gross.sum(),atol=1e-5))))
    summary=dict(status="DESIGN_INDICATION_SOURCE_LIMITED" if gate else "REJECT_DESIGN_NO_VALIDATION",
        design_gate_pass=gate,all_component_gross_gates_pass=allgross,all_component_net_positive=bool((comp.total>0).all()),
        all_component_min30_closed_units=bool((comp.trades>=30).all()),package=pack.to_dict(),positive_package_years=positive_years,
        expected_normal_design_decisions=int((f.index.year>=2018).sum()),active_known_design_dates=int(active.sum()),
        missing_core_input_decision_dates=source_missing,coherent_blocks=blocks,
        offline_boundary_dates=[str(f.index[i].date()) for i in ends if f.index[i].year>=2018],
        native_M6E_fills_verified=False,individual_contract_rolls_verified=False,promotion_authorized=False,
        source_complete=False,own_economic_series=8,package_configurations=1,control_configurations=1,
        author_trials="UNKNOWN: reported failed families and parameter searches retained",future_returns_run=False,
        hunt_v2_changed=False,automation_changed=False,completed_utc=datetime.now(timezone.utc).isoformat())
    dump(dest/"completed.json",summary)
    print(m[m.period=="2018-22"][["model","trades","total","trade_t","daily_NW5_t","sharpe","max_dd"]].to_string(index=False))
    print(json.dumps(clean(summary),indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--selftest",action="store_true");p.add_argument("--design",action="store_true")
    p.add_argument("--prereg");p.add_argument("--public-prereg");a=p.parse_args()
    if a.selftest:print(json.dumps(selftest()))
    elif a.design and a.prereg and a.public_prereg:run(a.prereg,a.public_prereg)
    else:p.error("Select selftest or design with local/public preregistration")
