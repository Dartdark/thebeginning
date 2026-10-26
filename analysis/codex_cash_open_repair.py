"""New standalone NQ Cash-Open Repair research; never reads existing strategy trades.

Only 5/15-minute signal bars and one-minute execution. Five frozen economic
configurations. Run --phase design first; validation is gated by that artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import warnings

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_cash_open_repair"
os.environ["NUMBA_CACHE_DIR"] = str(OUT / "numba_cache")
sys.path.insert(0, str(ROOT / "analysis"))
import numpy as np
import pandas as pd
import metrics as M
import resampling as R
from grid24 import Grid24
from grid import execute, _walk
from codex_s03_calendar import calendar_status, synthetic_checks as calendar_checks

PLAN = "agents/codex/plans/cash_open_repair.md"
CONFIGS = {"R5_Z1":(5,1.),"R15_Z1":(15,1.),"R5_Z2":(5,2.),"BASE5":(5,None),"BASE15":(15,None)}
SEED = 20261025


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, data):
    path = Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(data,str): data=data.encode()
    if path.exists():
        if path.read_bytes()!=data: raise ValueError("Refuse to replace existing different artifact: "+str(path))
        return
    with path.open("xb") as f: f.write(data)


def dump(path, obj):
    write(path,json.dumps(obj,indent=2,default=str,allow_nan=True)+"\n")


def csv(path, frame, index=False):
    write(path,frame.to_csv(index=index,float_format="%.12g"))


def tstat(x):
    x=np.asarray(x,float)
    return float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))) if len(x)>1 and x.std(ddof=1)>0 else np.nan


def nw(x,lags=5):
    x=np.asarray(x,float);e=x-x.mean();s=float(e@e)
    for k in range(1,min(lags,len(x)-1)+1):s+=2*(1-k/(lags+1))*float(e[k:]@e[:-k])
    return float(x.mean()*len(x)/np.sqrt(s)) if s>0 else np.nan


def roll_guard(date):
    d=pd.Timestamp(date)
    if d.month not in (3,6,9,12): return False
    first=pd.Timestamp(year=d.year,month=d.month,day=1)
    second_thu=first+pd.Timedelta(days=(3-first.weekday())%7+7)
    return d.normalize() in {second_thu+pd.Timedelta(days=n) for n in (0,1,4,5)}


def normal_cash(date):
    d=pd.Timestamp(date)
    return calendar_status(d)["kind"]=="normal" and (d.month,d.day) not in ((7,3),(12,24))


def repair_feature(a,b,history):
    if len(history)<60:return (np.nan,)*4
    h=np.asarray(history[-60:],float)
    vb=np.var(h[:,1],ddof=1)
    if vb<=0:return (np.nan,)*4
    beta=float(np.cov(h[:,0],h[:,1],ddof=1)[0,1]/vb)
    r=h[:,0]-beta*h[:,1];center=float(r.mean());sd=float(r.std(ddof=1))
    z=(a-beta*b-center)/sd if sd>0 else np.nan
    return beta,center,sd,float(z)


def engineering():
    count=calendar_checks()
    assert roll_guard("2024-03-14") and roll_guard("2024-03-19")
    assert not roll_guard("2024-03-13") and not roll_guard("2024-03-20")
    assert not normal_cash("2023-07-03") and not normal_cash("2023-04-07")
    h=[(.001*np.sin(i),.001*np.cos(i)) for i in range(60)]
    first=repair_feature(.01,.002,h)
    # Appending today's input after obtaining z cannot alter that already
    # emitted signal. Extreme future observations do not enter this call.
    saved=list(h); h.append((100.,-100.))
    assert first==repair_feature(.01,.002,saved)
    assert np.isnan(repair_feature(.01,.002,saved[:59])[-1])
    # Source executor protects a market entry during the entry minute.
    o=np.array([100.,100.,100.]);hi=np.array([100.,101.,100.]);lo=np.array([100.,94.,100.]);cl=np.array([100.,100.,100.])
    assert _walk(o,hi,lo,cl,1,2,1,95.,110.,1.)[:3]==(1,95.,0)
    # A stop gap receives the worse native open.
    o=np.array([100.,100.,90.]);hi=np.array([100.,101.,91.]);lo=np.array([100.,99.,89.])
    assert _walk(o,hi,lo,np.array([100.,100.,90.]),1,2,1,95.,110.,1.)[:3]==(2,90.,0)
    # Target must trade one point through; merely touching it is insufficient.
    o=np.array([100.,100.,100.]);hi=np.array([100.,110.,110.5]);lo=np.array([100.,99.,99.]);cl=np.array([100.,105.,106.])
    assert _walk(o,hi,lo,cl,1,2,1,95.,110.,1.)[2]==2
    assert R.max_dd([-10.,5.])==10.
    return dict(passed=True,calendar_checks=count,checks=["predeclared rolls","holiday skip","prior-only beta",
        "60-observation warm-up","entry-bar protection","worse gap stop","one-point target-through","initial-zero DD"])


def verify(prereg):
    subprocess.check_call(["git","-C",str(ROOT),"cat-file","-e",prereg+":"+PLAN])
    committed=subprocess.check_output(["git","-C",str(ROOT),"show",prereg+":"+PLAN])
    assert committed==(ROOT/PLAN).read_bytes()
    assert subprocess.check_output(["git","-C",str(ROOT),"branch","--show-current"],text=True).strip()=="codex/work"
    paths=sorted((ROOT/"data").glob("NQ_1min_*.csv"))+sorted((ROOT/"data").glob("ES_1min_20*.csv"))
    paths += [ROOT/PLAN,ROOT/"analysis/grid.py",ROOT/"analysis/grid24.py",ROOT/"analysis/metrics.py",
              ROOT/"analysis/resampling.py",ROOT/"analysis/codex_s03_calendar.py"]
    dump(OUT/"input_binding.json",dict(prereg=prereg,inputs={str(p.relative_to(ROOT)):sha(p) for p in paths},
         economic_configurations=CONFIGS,prior_family_searches="Unknown; see evidence sheet. No old trade ledger used."))
    write(OUT/".gitignore","numba_cache/\n")
    dump(OUT/"engineering_checks.json",engineering())


def trim_grid(g,cutoff):
    n=int(np.searchsorted(g.dates,int(pd.Timestamp(cutoff).strftime("%Y%m%d")),side="right"))
    for field in ("o","h","l","c","v","last_j","ts","dates"):setattr(g,field,getattr(g,field)[:n])
    g.D=n;g.trading=g.trading[g.trading<n]
    return g


def build_features(g,es):
    erow={int(x):i for i,x in enumerate(es.dates)}
    atr=g.daily_atr(15);previous=None;history=[];rows=[]
    for d,rawdate in enumerate(g.dates):
        date=pd.Timestamp(str(rawdate));cal=calendar_status(date)
        if cal["kind"] in ("weekend","holiday"):continue
        k=erow.get(int(rawdate));reason="eligible";a=b=np.nan
        beta=center=sd=z=np.nan;used_n=len(history)
        if not normal_cash(date):reason="holiday_or_early_close"
        elif roll_guard(date) or (previous is not None and roll_guard(previous[0])):reason="calendar_roll_window"
        elif previous is None:reason="no_prior_full_cash_session"
        elif k is None:reason="missing_ES_date"
        else:
            olddate,nd,ed=previous
            nq_o,es_o=g.o[d,511],es.o[k,511]
            nq_c=g.c[nd,900];es_c=es.c[ed,900] if ed is not None else np.nan
            if not all(np.isfinite(x) and x>0 for x in (nq_o,es_o,nq_c,es_c)):
                reason="missing_exact_anchor"
            else:
                a,b=float(np.log(nq_o/nq_c)),float(np.log(es_o/es_c))
                beta,center,sd,z=repair_feature(a,b,history)
                if not np.isfinite(z):reason="prior_feature_warmup_or_scale"
                history.append((a,b))  # only after computing today's prior-only feature
        rows.append(dict(day=d,date=date,es_day=k,calendar_kind=cal["kind"],eligible=reason=="eligible",reason=reason,
            prior_full_date=str(previous[0].date()) if previous else None,prior_observations=used_n,
            nq_overnight=a,es_overnight=b,beta=beta,residual_center=center,residual_sd=sd,z=z,atr=atr[d]))
        # A missing prior-session close invalidates tomorrow, rather than
        # reaching back to an earlier convenient known price.
        if normal_cash(date):previous=(date,d,k)
    return pd.DataFrame(rows)


def signals(g,features,frame,threshold,lo,hi):
    rows=[];audit=[];decision=510+frame
    for f in features.itertuples():
        if not lo<=f.date<=hi:continue
        reason=f.reason;side=0
        if f.eligible and np.isfinite(f.atr) and f.atr>0:
            values=np.stack([getattr(g,q)[f.day,511:decision+1] for q in ("o","h","l","c")])
            if not np.isfinite(values).all():reason="missing_opening_bar"
            else:
                side=int(np.sign(g.c[f.day,decision]-g.o[f.day,511]))
                if not side:reason="flat_opening_bar"
                elif threshold is not None and (abs(f.z)<threshold or side!=-int(np.sign(f.z))):reason="overnight_filter"
                else:
                    stop=np.ceil(.15*f.atr*4)/4.;target=np.ceil(.30*f.atr*4)/4.
                    rows.append(dict(day=f.day,dj=decision,side=side,stop=stop,target=target,exit_j=660))
                    reason="signal"
        elif f.eligible:reason="invalid_prior_ATR"
        audit.append(dict(date=f.date,reason=reason,side=side,z=f.z,frame=frame,threshold=threshold))
    return pd.DataFrame(rows,columns=["day","dj","side","stop","target","exit_j"]),pd.DataFrame(audit)


def replay(g,s):
    t=execute(g,s,max_trades=1,name="Cash Open Repair")
    slips=1+(t.kind!=1).astype(int)
    t["slips"]=slips;t["gross"]=t.pnl
    t["net"]=t.pnl-7.25-5.*slips
    t["net_mnq"]=t.pnl/10.-1.24-.5*slips
    t["stress_four_ticks"]=t.pnl-7.25-20.*slips
    missing=[]
    for r in t.itertuples():missing.append(int(np.isnan(g.c[r.day,r.j0:r.j1+1]).sum()))
    t["unobserved_held_minutes"]=missing
    assert t.day.value_counts().max()<=1 if len(t) else True
    assert (t.j0<=t.j1).all() and (t.j1<=660).all()
    return t


def stats(t,days,column="net"):
    x=t[column];d=x.groupby(pd.DatetimeIndex(t.date)).sum().reindex(days,fill_value=0.)
    m=M.perf(d,x);eq=50000.+np.r_[0,d.to_numpy().cumsum()];pk=np.maximum.accumulate(eq)
    m["max_dd"]=float((pk-eq).max());m["ulcer"]=float(np.sqrt(np.mean(((eq[1:]-pk[1:])/pk[1:]*100)**2)))
    m["calmar"]=m["annual"]/m["max_dd"] if m["max_dd"] else np.nan
    m["ulcer_perf"]=(m["annual"]/50000*100/m["ulcer"]) if m["ulcer"] else np.nan
    m.update(total=float(x.sum()),t_trade=tstat(x),t_daily=tstat(d),t_nw5=nw(d),t_nw20=nw(d,20),
        sessions=len(days),gross=float(t.pnl.sum()),cost=float((t.pnl-x).sum()),missing_held_minutes=int(t.unobserved_held_minutes.sum()))
    if len(x)==0:
        for key in ("win","avg","sharpe","sortino","profit_factor","calmar","ulcer_perf"):m[key]=np.nan
    return m


def filter_controls(candidate,base,days):
    key=["day","j0","side"]
    kept=base.merge(candidate[key],on=key,how="inner")
    assert len(kept)==len(candidate)
    np.testing.assert_allclose(kept.net.sort_values().to_numpy(),candidate.net.sort_values().to_numpy(),rtol=0,atol=1e-8)
    removed=base.merge(candidate[key].assign(kept=True),on=key,how="left")
    removed=removed[removed.kept.isna()].copy()
    rng=np.random.default_rng(SEED);totals=[];dds=[]
    for _ in range(1000):
        sub=base.iloc[np.sort(rng.choice(len(base),len(candidate),replace=False))]
        daily=sub.groupby("date").net.sum().reindex(days,fill_value=0.)
        totals.append(float(sub.net.sum()));dds.append(R.max_dd(daily))
    own_daily=candidate.groupby("date").net.sum().reindex(days,fill_value=0.)
    net=float(candidate.net.sum());dd=R.max_dd(own_daily)
    return dict(base_trades=len(base),kept_trades=len(candidate),removed_trades=len(removed),base_net=float(base.net.sum()),
        kept_net=net,removed_net=float(removed.net.sum()),removed_avg=float(removed.net.mean()),removed_t=tstat(removed.net),
        random_subsets=1000,random_net_mean=float(np.mean(totals)),p_random_net_ge_kept=float(np.mean(np.asarray(totals)>=net)),
        p_kept_better_net_and_dd=float(np.mean((np.asarray(totals)<net)&(np.asarray(dds)>dd))))


def phase(prereg,name):
    verify(prereg)
    hi=pd.Timestamp("2022-12-31" if name=="design" else "2026-10-09")
    lo=pd.Timestamp("2018-01-01" if name=="design" else "2023-01-01")
    chosen=None
    if name=="validation":
        gate=json.loads((OUT/"design_gate.json").read_text());chosen=gate["chosen"]
        if chosen is None:raise ValueError("Design failed: validation remains closed")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore",RuntimeWarning)
        g=trim_grid(Grid24(),hi)
        es=trim_grid(Grid24("data/ES_1min_20*.csv",night_pattern=""),hi)
        feature=build_features(g,es)
    csv(OUT/f"{name}_features.csv",feature)
    days=pd.DatetimeIndex(feature.loc[(feature.date>=lo)&(feature.date<=hi),"date"])
    frames={};ledgers={};rows=[];filter_results={}
    configs=CONFIGS if name=="design" else {k:CONFIGS[k] for k in (chosen,"BASE"+str(CONFIGS[chosen][0]))}
    for model,(frame,threshold) in configs.items():
        sig,audit=signals(g,feature,frame,threshold,lo,hi)
        t=replay(g,sig);ledgers[model]=t
        csv(OUT/f"{name}_{model}_signals.csv",sig);csv(OUT/f"{name}_{model}_trades.csv",t)
        csv(OUT/f"{name}_{model}_audit.csv",audit)
        frames[model]=t.groupby("date").net.sum().reindex(days,fill_value=0.)
        for side,label in ((0,"all"),(1,"long"),(-1,"short")):
            tx=t if not side else t[t.side==side]
            rows.append(dict(model=model,period="2018-22" if name=="design" else "2023+",side=label,**stats(tx,days)))
            for year in sorted(days.year.unique()):
                rows.append(dict(model=model,period=str(year),side=label,**stats(tx[tx.date.dt.year==year],days[days.year==year])))
    results=pd.DataFrame(rows);csv(OUT/f"{name}_metrics.csv",results)
    csv(OUT/f"{name}_daily.csv",pd.DataFrame(frames,index=days).rename_axis("date"),index=True)
    for model in (k for k in configs if k.startswith("R")):
        filter_results[model]=filter_controls(ledgers[model],ledgers["BASE"+str(CONFIGS[model][0])],days)
    dump(OUT/f"{name}_filter_controls.json",filter_results)
    if name=="design":
        checks={}
        for model in ("R5_Z1","R15_Z1","R5_Z2"):
            t=ledgers[model];m=stats(t,days);yy=t.groupby(t.date.dt.year).net.sum()
            checks[model]=dict(trades=m["trades"]>=100,positive=m["total"]>0,trade_t=m["t_trade"]>=2,
                daily_nw5=m["t_nw5"]>=1.5,pf=m["profit_factor"]>=1.2,positive_years=int((yy>0).sum())>=4,
                micro_net=float(t.net_mnq.sum())>0,four_tick_net=float(t.stress_four_ticks.sum())>0)
        passing=[k for k,v in checks.items() if all(v.values())]
        result=dict(prereg=prereg,configurations_tested=5,gates=checks,passing=passing,
            chosen=passing[0] if passing else None,validation_allowed=bool(passing),
            t6_observed_in_design=bool(any(stats(ledgers[k],days)["t_trade"]>=6 and stats(ledgers[k],days)["t_nw5"]>=6 for k in ("R5_Z1","R15_Z1","R5_Z2"))))
        dump(OUT/"design_gate.json",result)
        print(results[(results.period=="2018-22") & (results.side=="all")][["model","trades","total","avg","profit_factor","t_trade","t_daily","t_nw5","max_dd"]].to_string(index=False))
        print(json.dumps(result,indent=2))
    else:
        print(results[(results.period=="2023+")&(results.side=="all")].to_string(index=False))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase",choices=("design","validation"),required=True)
    parser.add_argument("--prereg",required=True)
    args=parser.parse_args();phase(args.prereg,args.phase)
