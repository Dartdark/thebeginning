"""Frozen Anson personal-plan comparison; no prices/returns are loaded at import.

The latest personal14-piece baseline is reconstructed from exact pinned inputs,
including Twin's published daily marks. The candidate uses raw intended4.5/20
source fills, marks open positions at observed prices no later than16:00CT,
and has no Apex payout, trail, or daily-loss limits. Research only.
"""
from __future__ import annotations

from pathlib import Path
import importlib.util
import hashlib
import json
import pickle
import subprocess

import numpy as np
import pandas as pd

import metrics as M
import resampling as R

ROOT=Path(__file__).resolve().parents[1]
PIN="e34d71cd3537a9f019d2521e280fc92f3ffdb4c6"
RUNTIME=ROOT/"agents/codex/runtime/anson_personal_inputs"
OUT=ROOT/"analysis/outputs/codex_anson/personal"
EXTRA=.55
CANDIDATE_FEE=1.275
INPUTS=("analysis/personal_portfolio.py","analysis/montecarlo.py","personal_strategies/PORTFOLIO.md",
        "agents/tasks/plan_daily_pnl.csv","checks/candidates/fc_2b/trades.csv",
        "checks/candidates/twin_continuation/trades.csv","checks/candidates/overnight_anomaly/trades.csv",
        "checks/candidates/dual_thrust/trades.csv","analysis/outputs/personal_portfolio_output.txt")
STARTERS={
    "A":["TwinContinuation","OvernightBiasML","BridgeMondayLong","CLSundayFade_perMCL","NFPFade"],
    "B":["TwinContinuation","OvernightBiasML","BridgeMondayLong","CLSundayFade_perMCL","NFPFade","ExpirationOpenShort"],
    "C":["TwinContinuation","OvernightBiasML","BridgeMondayLong","CLSundayFade_perMCL","NFPFade","ExpirationOpenShort","VaultBreak"],
    "D":["TwinContinuation","OvernightBiasML","BridgeMondayLong","CLSundayFade_perMCL","NFPFade","ExpirationOpenShort","VaultBreak","RelativeStrength","ESMOCFollow_perMES"],
}
LIMITATIONS=[
    "Published personal fee convention is preserved: +$0.55 per nonzero plan day, not exact trade counts; VB reentries are undercharged.",
    "Published MOC starts at $0.50/MES rather than $0.725, so its inherited total commission is $1.05 rather than $1.275.",
    "Twin baseline is the committed v1 checker ledger with published16:00 marks; no exact v2.1 ledger exists.",
    "Twin published marking skips dates without a15:30..16:00 observation; candidate uses the last available same-date price at/before16:00.",
    "Candidate observed-bar gaps can reflect closures or feed loss; marks can be stale and no future price fills the gap.",
    "Daily marked drawdown omits intraday margin/liquidation exposure; personal MC has no Apex trail or payout caps.",
]


def git_bytes(*args):
    return subprocess.check_output(["git","-C",str(ROOT),*args])


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def prepare_sources(runtime=RUNTIME):
    """Materialise exact source/input blobs only; safe before preregistration."""
    runtime=Path(runtime)
    if not runtime.resolve().is_relative_to((ROOT/"agents/codex/runtime").resolve()):
        raise ValueError("Research input snapshot must stay in ignored runtime")
    manifest={"reference":PIN,"files":{}}
    for rel in INPUTS:
        data=git_bytes("show",PIN+":"+rel)
        dest=runtime/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(data)
        manifest["files"][rel]={"sha256":sha_bytes(data),"bytes":len(data),
                                "git_blob":git_bytes("rev-parse",PIN+":"+rel).decode().strip()}
    return manifest


def require_prereg(commit,path="agents/codex/plans/anson_momentum.md"):
    if not commit:
        raise ValueError("A committed preregistration is required before returns")
    git_bytes("cat-file","-e",str(commit)+":"+path)


def import_pinned(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_personal(*,scratch,prereg,prereg_path="agents/codex/plans/anson_momentum.md",runtime=RUNTIME):
    """Build only the current14 pieces; execute no historical candidate/search."""
    require_prereg(prereg,prereg_path)
    manifest=prepare_sources(runtime)
    runtime=Path(runtime)
    p=pd.read_csv(runtime/"agents/tasks/plan_daily_pnl.csv",parse_dates=["date"]).set_index("date")
    p=p-EXTRA*(p!=0)
    days=pd.DatetimeIndex(p.index)
    if not days.is_monotonic_increasing or days.has_duplicates:
        raise ValueError("Personal baseline calendar must be ordered and unique")
    counts={}
    def from_trades(rel,name):
        t=pd.read_csv(runtime/rel,parse_dates=["date"])
        t=t[pd.DatetimeIndex(t.date)<=days[-1]]
        x=(t.net/10-EXTRA).to_numpy()
        k=np.minimum(days.searchsorted(pd.DatetimeIndex(t.date)),len(days)-1)
        out=pd.Series(x,index=days[k]).groupby(level=0).sum().reindex(days,fill_value=0.).rename(name)
        if abs(out.sum()-x.sum())>=1e-6:
            raise AssertionError("Trade booking dropped net money: "+name)
        counts[name]=len(t)
        return out
    fc=from_trades("checks/candidates/fc_2b/trades.csv","FC2B")
    # Execute only the pinned reusable helper, never the script's __main__.
    src=import_pinned("codex_anson_pinned_personal",runtime/"analysis/personal_portfolio.py")
    if src.EXTRA!=EXTRA:
        raise ValueError("Pinned personal fee convention changed")
    twin=src.twin_marked(days,path=str(runtime/"checks/candidates/twin_continuation/trades.csv"),
                         sp=str(Path(scratch).resolve())+"/")
    counts["TwinContinuation"]=len(pd.read_csv(runtime/"checks/candidates/twin_continuation/trades.csv"))
    oa=from_trades("checks/candidates/overnight_anomaly/trades.csv","OvernightAnomaly")
    dt=from_trades("checks/candidates/dual_thrust/trades.csv","DualThrust")
    frame=pd.concat([p,fc,twin,oa,dt],axis=1)
    if len(frame.columns)!=14 or frame.isna().any().any():
        raise AssertionError("Expected the complete14-piece baseline without missing marks")
    manifest.update(columns=list(frame),dates={"first":str(days.min().date()),"last":str(days.max().date()),"days":len(days)},
                    trade_counts=counts,limitations=LIMITATIONS,preregistration=str(prereg))
    return frame,manifest


def baseline_reference(frame,runtime=RUNTIME):
    """Reconcile the published full14 baseline before examining a candidate."""
    mc=import_pinned("codex_anson_pinned_personal_mc",Path(runtime)/"analysis/montecarlo.py")
    x=frame.sum(axis=1)
    idx=histories(len(x))
    profit,dd=simulate_daily(x.to_numpy(),idx)
    original=mc.daily_mc(x.to_numpy(),horizon=252,n=5000,block=20,seed=1,trail=1e12)
    for actual,key in ((np.quantile(profit,.05),"pnl_p5"),(np.median(profit),"pnl_p50"),
                       (np.quantile(profit,.95),"pnl_p95"),(np.median(dd),"dd_p50"),
                       (np.quantile(dd,.95),"dd_p95")):
        np.testing.assert_allclose(actual,original[key],rtol=0,atol=1e-8)
    actual=dict(annual=x.sum()/(len(x)/252),max_dd=R.max_dd(x),
                mc_p5=np.quantile(profit,.05),mc_p50=np.median(profit),mc_p95=np.quantile(profit,.95),
                mc_dd_p50=np.median(dd),mc_dd_p95=np.quantile(dd,.95))
    published=dict(annual=24351.,max_dd=5001.,mc_p5=12507.,mc_p50=23698.,mc_p95=37331.,mc_dd_p50=2873.,mc_dd_p95=5001.)
    return dict(actual=actual,published_rounded=published,delta={k:actual[k]-published[k] for k in actual},
                exact_pinned_MC_statistic_parity=True,rounding_match=all(abs(actual[k]-published[k])<=.51 for k in actual),
                note="Published values are rounded; inspect any non-rounding baseline difference before comparison")


def map_session(days,date,minute):
    """Open fills use wall time one minute before their minute close stamp."""
    wall=pd.Timestamp(date).normalize()+pd.Timedelta(minutes=int(minute)-1)
    wall_minute=wall.hour*60+wall.minute
    session=wall.normalize()+pd.Timedelta(days=int(wall_minute>960))
    k=int(days.searchsorted(session))
    return min(k,len(days)-1)


def candidate_daily(g,trades,days,fee=CANDIDATE_FEE):
    """Raw source positions marked with no after16:00 price peek.

    Entry slippage$0.50 is charged in the entry session; commission plus
    exit slippage are charged in the exit session. Price marks allocate the
    change since the prior actual mark; total money equals every trade net.
    """
    days=pd.DatetimeIndex(days)
    out=np.zeros(len(days))
    row_lookup={pd.Timestamp(d).normalize():i for i,d in enumerate(g.ts)}
    marked=[]
    t=trades.copy()
    for x in t.itertuples():
        er=int(x.entry_row) if hasattr(x,"entry_row") else int(x.day)
        xr=int(x.exit_row) if hasattr(x,"exit_row") else int(x.day)
        ej,xj=int(x.entry_j),int(x.exit_j)
        entry_date,exit_date=pd.Timestamp(g.ts[er]),pd.Timestamp(g.ts[xr])
        if (xr*1440+xj)<(er*1440+ej):
            raise ValueError("Exit before entry")
        a=map_session(days,entry_date,ej)
        b=map_session(days,exit_date,xj)
        out[a]-=.5
        last=float(x.entry)
        for k in range(a,b):
            date=days[k]
            row=row_lookup.get(date.normalize())
            if row is None:
                marked.append(dict(trade_index=x.Index,date=date,status="no_calendar_row",mark_j=-1))
                continue
            finite=np.flatnonzero(np.isfinite(g.c[row,:961]))
            if not len(finite):
                marked.append(dict(trade_index=x.Index,date=date,status="no_observed_close_at_or_before16",mark_j=-1))
                continue
            j=int(finite[-1])
            address=row*1440+j
            if address<er*1440+ej or address>=xr*1440+xj:
                # No mark may precede the entry or peek beyond its exit fill.
                continue
            price=float(g.c[row,j])
            pnl=(price-last)*int(x.side)*2.
            out[k]+=pnl
            marked.append(dict(trade_index=x.Index,date=date,status="observed_mark",mark_j=j,
                               minutes_before16=960-j,price=price,pnl_micro=pnl))
            last=price
        out[b]+=(float(x.exit)-last)*int(x.side)*2.-float(fee)-.5
    gross=((t.exit-t.entry)*t.side*2).sum()
    expected=float(gross-len(t)*(float(fee)+1.))
    np.testing.assert_allclose(out.sum(),expected,rtol=0,atol=1e-6)
    return pd.Series(out,index=days,name="Anson"),pd.DataFrame(marked),dict(
        trades=len(t),net_sum=out.sum(),expected_trade_net=expected,commission_micro=fee,
        entry_slippage=.5,exit_slippage=.5,entry_cost_session="entry",exit_fee_and_slippage_session="exit",
        closure_mapping="open-fill wall time after16:00=>nextsession; non-session dates=>next available plan date",
        mark_rule="last observed close on that trading date at/before16:00; no later price or forced rescue fill")


def mark_fixture():
    """Invented closure-spanning positions test marks, fees and session booking."""
    from types import SimpleNamespace
    ts=pd.date_range("2026-10-02",periods=4,freq="D")
    g=SimpleNamespace(ts=ts.to_numpy(),c=np.full((4,1440),np.nan))
    g.c[0,960]=105.
    g.c[0,961]=999.  # A later observed price must not leak into a16:00 mark.
    days=pd.DatetimeIndex([ts[0],ts[3]])
    t=pd.DataFrame([dict(entry_row=0,exit_row=3,entry_j=600,exit_j=600,entry=100.,exit=110.,side=1)])
    x,a,_=candidate_daily(g,t,days)
    np.testing.assert_allclose(x.to_numpy(),[9.5,8.225],rtol=0,atol=1e-12)
    assert a.iloc[0].mark_j==960 and a.iloc[0].price==105.
    # An after16:00 Friday exit books to the next plan session, Monday.
    t.loc[0,["exit_row","exit_j","exit"]]=[0,962,108.]
    x,_,_=candidate_daily(g,t,days)
    np.testing.assert_allclose(x.to_numpy(),[9.5,4.225],rtol=0,atol=1e-12)
    # A missing16:00 observation uses an earlier same-date observation only.
    g.c[0,960]=np.nan
    g.c[0,950]=104.
    x,a,_=candidate_daily(g,t,days)
    assert a.iloc[0].mark_j==950 and a.iloc[0].minutes_before16==10
    np.testing.assert_allclose(x.sum(),16.-2.275,rtol=0,atol=1e-12)
    return dict(invented_prices_only=True,closure_carry_retained=True,no_after16_price_peek=True,
                entry_slip_at_entry=True,commission_and_exit_slip_at_exit=True,
                after16_fill_maps_next_plan_session=True,last_prior_observation_only=True)


def configurations(frame,candidate):
    sets={**STARTERS,"FULL":list(frame.columns)}
    plans={}
    metadata={}
    for group,keys in sets.items():
        base=frame[keys].sum(axis=1)
        choices={"BASE":base,"ADD_1":base+candidate,"ADD_2":base+2*candidate}
        if "VaultBreak" in keys:
            empty=base-frame.VaultBreak
            choices.update(EMPTY_VB=empty,REPLACE_VB_1=empty+candidate)
        for label,series in choices.items():
            name=group+"__"+label
            plans[name]=series
            metadata[name]={"set":group,"allocation":label,"baseline_pieces":keys}
    if len(plans)!=21:
        raise AssertionError("Frozen personal allocation count is21")
    return plans,metadata


def histories(T,n=5000,horizon=252,block=20,seed=1):
    """Exactly the pinned MC.daily_mc noncircular block draw convention."""
    if T<=block:
        raise ValueError("Insufficient cohort for20-day blocks")
    rng=np.random.default_rng(seed)
    starts=rng.integers(0,T-block,(n,int(np.ceil(horizon/block))))
    return (starts[:,:,None]+np.arange(block)).reshape(n,-1)[:,:horizon]


def simulate_daily(x,idx):
    values=np.asarray(x,float)[idx]
    cumulative=values.cumsum(axis=1)
    peak=np.maximum.accumulate(np.concatenate([np.zeros((len(idx),1)),cumulative],axis=1),axis=1)[:,1:]
    return cumulative[:,-1],(peak-cumulative).max(axis=1)


def paired_mean_interval(delta,seed=902,n=5000):
    delta=np.asarray(delta,float)
    rng=np.random.default_rng(seed)
    estimates=np.empty(n)
    for start in range(0,n,100):
        size=min(100,n-start)
        ix=rng.integers(0,len(delta),(size,len(delta)))
        estimates[start:start+size]=delta[ix].mean(1)
    return np.quantile(estimates,[.025,.975])


def historical_annual_effect_interval(delta,seed=903,n=5000,block=20):
    """Uncertainty from finite historical days, distinct from MC sampling error."""
    x=np.asarray(delta,float)
    rng=np.random.default_rng(seed)
    means=np.empty(n)
    blocks=int(np.ceil(len(x)/block))
    for start in range(0,n,100):
        count=min(100,n-start)
        st=rng.integers(0,len(x)-block,(count,blocks))
        idx=(st[:,:,None]+np.arange(block)).reshape(count,-1)[:,:len(x)]
        means[start:start+count]=x[idx].mean(1)*252
    return np.quantile(means,[.025,.975])


def benchmark(frame,candidate,out=OUT):
    """Historical and paired1-year uncapped personal comparisons, no selection."""
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    plans,meta=configurations(frame,candidate)
    days=pd.DatetimeIndex(frame.index)
    rows,diffs,historical=[],[],[]
    periods={"2018_22":("2018-01-01","2023-01-01"),"2018_24_author_IS":("2018-01-01","2025-01-01"),
             "2023_plus":("2023-01-01","2100-01-01"),"2025_plus_replication":("2025-01-01","2100-01-01"),
             "2018_plus":("2018-01-01","2100-01-01")}
    for year in sorted(days.year.unique()):
        periods[str(year)]=(f"{year}-01-01",f"{year+1}-01-01")
    for name,x in plans.items():
        for period,(lo,hi) in periods.items():
            d=x[(days>=lo)&(days<hi)]
            row=M.perf(d,trades=d[d!=0])
            row.update(config=name,period=period,total=d.sum(),days=len(d),max_dd_including_start=R.max_dd(d),
                       group=meta[name]["set"],allocation=meta[name]["allocation"],
                       note="daily portfolio observations, not individual trade statistics")
            historical.append(row)
    npz={}
    historical_ci_cache={}
    for cohort,start in (("2018_plus","2018-01-01"),("2025_plus_replication","2025-01-01")):
        mask=days>=start
        idx=histories(int(mask.sum()))
        np.save(out/f"paired_histories_{cohort}.npy",idx)
        results={}
        for name,x in plans.items():
            profit,dd=simulate_daily(x[mask].to_numpy(),idx)
            results[name]=(profit,dd)
            npz[name+"__profit"]=profit
            npz[name+"__dd"]=dd
            dd95=np.quantile(dd,.95)
            rows.append(dict(cohort=cohort,config=name,group=meta[name]["set"],allocation=meta[name]["allocation"],
                             profit_p5=np.quantile(profit,.05),profit_p50=np.median(profit),profit_p95=np.quantile(profit,.95),
                             profit_mean=profit.mean(),p_losing_year=np.mean(profit<=0),dd_p50=np.median(dd),dd_p95=dd95,
                             capital_20pct=dd95/.2,return_dd_median=np.median(profit)/max(np.median(dd),1e-9),
                             median_profit_over_dd95=np.median(profit)/max(dd95,1e-9),
                             dd95_as_pct_of_10k=dd95/10000.,dd95_as_pct_of_25k=dd95/25000.,histories=len(idx)))
        summary=pd.DataFrame(rows)
        for name,(profit,dd) in results.items():
            group=meta[name]["set"]
            references=[group+"__BASE"]
            if group in ("C","D","FULL"):
                references.append(group+"__EMPTY_VB")
            for ref in references:
                bp,bd=results[ref]
                lo,hi=paired_mean_interval(profit-bp)
                ddlo,ddhi=paired_mean_interval(dd-bd)
                p50_delta=np.median(profit)-np.median(bp)
                dd95_delta=np.quantile(dd,.95)-np.quantile(bd,.95)
                historical_delta=(plans[name][mask]-plans[ref][mask]).to_numpy()
                cache_key=sha_bytes(historical_delta.tobytes())
                if cache_key not in historical_ci_cache:
                    historical_ci_cache[cache_key]=historical_annual_effect_interval(historical_delta)
                annual_lo,annual_hi=historical_ci_cache[cache_key]
                # Equal-risk comparison scales to the baseline's p95 drawdown;
                # this is a continuous research risk budget, not executable size.
                scale=np.quantile(bd,.95)/max(np.quantile(dd,.95),1e-9)
                diffs.append(dict(cohort=cohort,config=name,reference=ref,profit_mean_delta=(profit-bp).mean(),
                                  profit_mean_delta_lo=lo,profit_mean_delta_hi=hi,
                                  dd_mean_delta=(dd-bd).mean(),dd_mean_delta_lo=ddlo,dd_mean_delta_hi=ddhi,
                                  profit_p50_delta=p50_delta,dd_p95_delta=dd95_delta,capital_20pct_delta=dd95_delta/.2,
                                  paired_profit_delta_p5=np.quantile(profit-bp,.05),paired_profit_delta_p50=np.median(profit-bp),
                                  paired_profit_delta_p95=np.quantile(profit-bp,.95),p_paired_profit_delta_le_zero=np.mean(profit<=bp),
                                  historical_annual_mean_delta=historical_delta.mean()*252,
                                  historical_annual_mean_delta_ci95_lo=annual_lo,historical_annual_mean_delta_ci95_hi=annual_hi,
                                  profit_mean_ci_scope="MC sampling precision conditional on observed history; not future-edge confidence",
                                  marginal_p50_return_per_added_dd95=p50_delta/dd95_delta if dd95_delta>0 else np.nan,
                                  same_dd95_continuous_scale=scale,same_dd95_median_profit_delta=np.median(profit)*scale-np.median(bp),
                                  same_dd95_scale_is_executable_contract_count=False,
                                  p_profit_beats_reference=np.mean(profit>bp)+.5*np.mean(profit==bp)))
        np.savez_compressed(out/f"paired_mc_{cohort}.npz",**npz)
        npz={}
    pd.DataFrame(rows).to_csv(out/"mc_summary.csv",index=False)
    pd.DataFrame(diffs).to_csv(out/"paired_effects.csv",index=False)
    pd.DataFrame(historical).to_csv(out/"historical_summary.csv",index=False)
    pd.DataFrame(plans).to_csv(out/"daily_portfolios.csv")
    return pd.DataFrame(rows),pd.DataFrame(diffs),pd.DataFrame(historical)


def raw_personal_stats(g,trades,days,out=OUT):
    """Readily reusable raw rule statistics at the declared personal costs."""
    periods={"2018_22":("2018-01-01","2023-01-01"),"2018_24_author_IS":("2018-01-01","2025-01-01"),
             "2023_plus":("2023-01-01","2100-01-01"),"2025_plus_replication":("2025-01-01","2100-01-01"),
             "2018_plus":("2018-01-01","2100-01-01")}
    for year in sorted(days.year.unique()):
        periods[str(year)]=(f"{year}-01-01",f"{year+1}-01-01")
    t=trades.copy()
    t["date"]=pd.to_datetime(t.date)
    t["net_micro"]=(t.exit-t.entry)*t.side*2-CANDIDATE_FEE-1.
    rows=[]
    for group,sub in (("both",t),("long",t[t.side>0]),("short",t[t.side<0])):
        daily,_,_=candidate_daily(g,sub,days)
        for period,(lo,hi) in periods.items():
            trade=sub[(sub.date>=lo)&(sub.date<hi)].net_micro
            d=daily[(days>=lo)&(days<hi)]
            row=M.perf(d,trades=trade)
            row.update(group=group,period=period,net_total=trade.sum(),t=float(trade.mean()/trade.std()*np.sqrt(len(trade))) if len(trade)>1 and trade.std()>0 else np.nan,
                       daily_total=d.sum(),max_dd_including_start=R.max_dd(d),costs="personal fee1.275+entry.50+exit.50 perMNQ",
                       note="trade periods by entry date; daily P&L uses16:00session marks and fill-specific costs")
            rows.append(row)
    table=pd.DataFrame(rows)
    table.to_csv(Path(out)/"raw_personal_standalone.csv",index=False)
    return table


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prereg",required=True)
    parser.add_argument("--scratch",default="scratch_data")
    parser.add_argument("--ledger",default="analysis/outputs/codex_anson/replay/intended_raw_trades.csv")
    parser.add_argument("--out",default=str(OUT))
    args=parser.parse_args()
    require_prereg(args.prereg)
    out=Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    frame,manifest=load_personal(scratch=args.scratch,prereg=args.prereg)
    reference=baseline_reference(frame)
    (out/"baseline_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    (out/"baseline_reference.json").write_text(json.dumps(reference,indent=2)+"\n")
    frame.to_csv(out/"baseline_daily14.csv")
    if not reference["rounding_match"]:
        raise ValueError("Published personal baseline differs beyond rounding; investigate before candidate comparison")
    with open(Path(args.scratch)/"g24.pkl","rb") as f:
        grid=pickle.load(f)
    ledger=pd.read_csv(args.ledger,parse_dates=["date"])
    candidate,marks,money=candidate_daily(grid,ledger,frame.index)
    candidate.to_csv(out/"candidate_daily.csv")
    marks.to_csv(out/"candidate_marks.csv",index=False)
    money.update(ledger_sha256=sha_bytes(Path(args.ledger).read_bytes()),raw_unknown_gap_trades=int((ledger.unknown_held_minutes>0).sum()),
                 raw_cross_date_trades=int(ledger.cross_date.sum()),synthetic_fixture=mark_fixture(),
                 open_fill_time_rule="wall minute is close-stamped minute minus1; after16:00 maps next session")
    gap_path=Path(args.ledger).with_name(Path(args.ledger).name.replace("_trades.csv","_gaps.csv"))
    if gap_path.exists():
        money["raw_gap_audit_sha256"]=sha_bytes(gap_path.read_bytes())
    (out/"candidate_manifest.json").write_text(json.dumps(money,indent=2)+"\n")
    raw_personal_stats(grid,ledger,frame.index,out)
    print("Personal baseline/marks and standalone complete; paired21-configuration MC starting",flush=True)
    summary,effects,historical=benchmark(frame,candidate,out)
    reproduction=dict(preregistration=args.prereg,plan_ref=PIN,configurations=21,cohorts=["2018_plus","2025_plus_replication"],
                      mc_histories=5000,horizon_days=252,block_days=20,mc_seed=1,paired_mc_mean_ci_resamples=5000,
                      paired_mc_mean_ci_seed=902,historical_effect_block_bootstrap_resamples=5000,historical_effect_ci_seed=903,
                      historical_effect_interval="95%; paired20-day blocks of observed full cohort length; annualized mean delta",
                      mc_mean_interval="95% simulation-precision interval only, conditional on the historical return distribution",
                      no_Apex_limits=True,limitations=LIMITATIONS,
                      script_sha256=sha_bytes(Path(__file__).read_bytes()),ledger_sha256=money["ledger_sha256"],
                      baseline_input_manifest_sha256=sha_bytes((out/"baseline_manifest.json").read_bytes()))
    (out/"reproduction.json").write_text(json.dumps(reproduction,indent=2)+"\n")
    print(summary[(summary.cohort=="2018_plus")&(summary.group=="FULL")].to_string(index=False),flush=True)
    print("Personal benchmark complete",flush=True)
