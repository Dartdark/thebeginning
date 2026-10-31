"""User-requested Twin standalone replay; existing checker simulator, frozen defaults.

Outputs only Codex paths. No shared cache writes, portfolio changes or live access.
Run with the configured Python from repo root. Engine run() is imported, not its CLI.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import sys

import numpy as np
import pandas as pd
from numba import njit

import grid24
import metrics as M
import montecarlo as MC
import resampling as R

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_twin_standalone"
INPUT = ROOT / "agents/codex/inputs/twin_continuation_uploaded.txt"
PRIMARY = pd.Timestamp("2018-06-01")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def executable(text):
    return re.sub(r"\s+", "", re.sub(r"\{.*?\}", "", text, flags=re.S)).lower()


def timestamp(day, hhmm):
    return pd.to_datetime(day) + pd.to_timedelta(hhmm // 100 * 60 + hhmm % 100, unit="m")


@njit
def conditional_exit(D, J, O, H, L, C, i0, ep, side, distance, target_distance, is_mo):
    stop = ep - side * distance
    target = ep + side * target_distance
    for k in range(i0 + 1, len(C)):
        minute = J[k]
        # MO midnight/date-reset this-bar-close exit; scheduled 14:50 next-bar-market exit.
        if is_mo and D[k] != D[i0]:
            return (C[k]-ep)*side*20 - 17.25
        if is_mo and 891 <= minute <= 960:
            return (O[k]-ep)*side*20 - 17.25
        if not is_mo and ((side == 1 and O[k] >= target) or (side == -1 and O[k] <= target)):
            return (O[k]-ep)*side*20 - 12.25
        if (side == 1 and O[k] <= stop) or (side == -1 and O[k] >= stop):
            return (O[k]-ep)*side*20 - 17.25
        if (side == 1 and L[k] <= stop) or (side == -1 and H[k] >= stop):
            return (stop-ep)*side*20 - 17.25
        if not is_mo and ((side == 1 and H[k] >= target) or (side == -1 and L[k] <= target)):
            return (target-ep)*side*20 - 12.25
        if not is_mo and 945 <= minute <= 960:
            return (C[k]-ep)*side*20 - 17.25
    return np.nan


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    prior = ROOT / "checks/candidates/twin_continuation/Twin_Continuation.txt"
    assert executable(INPUT.read_text()) == executable(prior.read_text()), "Upload differs; stop before using old engine"
    spec = importlib.util.spec_from_file_location("twin_checked_replica", ROOT/"checks/candidates/twin_continuation/replica.py")
    engine = importlib.util.module_from_spec(spec); spec.loader.exec_module(engine)
    print("Loading owned grid through existing replica loader; no cache writes", flush=True)
    bars = engine.load_bars()
    D, J, O, H, L, C = bars
    start = pd.Timestamp(str(D[0])); end = pd.Timestamp(str(D[-1]))
    assert PRIMARY >= start + pd.DateOffset(months=6)
    variants = {"combined":{}, "breakout_alone":{"UseMomentum":0}, "momentum_alone":{"UseBreakout":0}}
    frames = {}
    for name, changes in variants.items():
        print(f"Replaying {name}, unchanged defaults except component toggle {changes}", flush=True)
        params = dict(engine.P); params.update(changes)
        t = engine.run(params, bars)
        t["date"] = pd.to_datetime(t.date); t["entry_date"] = pd.to_datetime(t.entry_date)
        t["entry_stamp"] = timestamp(t.entry_date, t.entry_time_ct)
        t["exit_stamp"] = timestamp(t.date, t.exit_time_ct)
        t["primary"] = (t.entry_stamp >= PRIMARY) & (t.date <= end)
        t = t[t.entry_stamp >= "2018-01-01"].copy()
        t["repo_cost"] = np.where(t.kind.eq("limit"), 12.25, 17.25)
        assert np.allclose(t.net, t.pts*20-t.repo_cost)
        t["net_user_cost"] = t.pts*20-6
        t["net_extra_tick_each_fill"] = t.net-10
        t["crosses_calendar_midnight"] = t.date != t.entry_date
        next_midnight = t.entry_date + pd.Timedelta(days=1)
        next_break = t.entry_date + pd.Timedelta(hours=16)
        next_break = next_break.where(t.entry_stamp < next_break, next_break+pd.Timedelta(days=1))
        t["crosses_16ct_break"] = (t.entry_stamp < next_break) & (t.exit_stamp > next_break)
        t["crosses_1559_deadline"] = (t.entry_stamp < next_break-pd.Timedelta(minutes=1)) & (t.exit_stamp > next_break-pd.Timedelta(minutes=1))
        t["initial_stop_risk_per_nq"] = (t.entry-t.stop).abs()*20
        t.to_csv(OUT/f"trades_{name}.csv", index=False)
        frames[name] = t
        print(f"{name} complete; calculating standalone diagnostics", flush=True)
    # Zero weekdays plus any actual weekend exit dates: no closed trade is silently dropped.
    calendar = pd.bdate_range("2018-01-01", end)
    for t in frames.values():
        calendar = calendar.union(pd.DatetimeIndex(t.date.unique()))
    calendar = calendar.sort_values()
    stats, boots, perms, monte, placebo, diagnostics = [], [], [], [], [], {}
    trials_n = len(pd.read_csv(ROOT/"TRIALS.csv")) + 3
    lookup = {(int(d),int(j)):i for i,(d,j) in enumerate(zip(D,J)) if d>=20180101}
    for name, t in frames.items():
        p = t[t.primary].copy()
        daily = p.groupby("date").net.sum().reindex(calendar[calendar>=PRIMARY],fill_value=0.)
        daily.rename(name).to_csv(OUT/f"daily_{name}.csv")
        for period, subset, days in [("primary_all",p,calendar[calendar>=PRIMARY]),
            ("2018-22",p[p.entry_stamp<"2023-01-01"],calendar[(calendar>=PRIMARY)&(calendar<"2023-01-01")]),
            ("2023+_seen",p[p.entry_stamp>="2023-01-01"],calendar[calendar>="2023-01-01"]),
            ("2018_full_short_warmup",t[t.entry_stamp<"2019-01-01"],calendar[calendar<"2019-01-01"])]:
            for side, group in [("all",subset),("long",subset[subset.side==1]),("short",subset[subset.side==-1])]:
                d = group.groupby("date").net.sum().reindex(days,fill_value=0.)
                row = M.perf(d,group.net)
                row.update(variant=name,period=period,side=side,total=float(group.net.sum()),
                           t=float(group.net.mean()/group.net.std()*np.sqrt(len(group))) if len(group)>1 else np.nan,
                           dsr=float(M.deflated_sharpe(d,trials_n)))
                stats.append(row)
        for year in sorted(p.date.dt.year.unique()):
            y = p[p.date.dt.year==year]; days=calendar[(calendar.year==year)&(calendar>=PRIMARY)]
            for side,z in [("all",y),("long",y[y.side==1]),("short",y[y.side==-1])]:
                row=M.perf(z.groupby("date").net.sum().reindex(days,fill_value=0.),z.net)
                row.update(variant=name,period=str(year)+( "_partial" if year==2018 else ""),side=side,total=float(z.net.sum()),
                           t=float(z.net.mean()/z.net.std()*np.sqrt(len(z))) if len(z)>1 else np.nan)
                stats.append(row)
        for side,z in [("all",p),("long",p[p.side==1]),("short",p[p.side==-1])]:
            h=z[z.entry_stamp>="2023-01-01"]
            d=h.groupby("date").net.sum().reindex(calendar[calendar>="2023-01-01"],fill_value=0.)
            b=R.bootstrap(d,n=2000,seed=7).reset_index(names="metric")
            b["variant"],b["side"],b["p_sharpe_le_0"]=name,side,b.attrs.get("p_sharpe_le_0",np.nan)
            boots.append(b)
            perms.append(dict(variant=name,side=side,**R.permutation(d,n=2000,seed=7)))
        for units,scale in [("1_NQ",1.),("1_MNQ_proportional_cost",.1)]:
            monte.append(dict(variant=name,size=units,view="trade_bootstrap",**MC.trade_mc(p.net*scale,n=5000,seed=7)))
            monte.append(dict(variant=name,size=units,view="one_year_daily_blocks",**MC.daily_mc(daily*scale,n=5000,seed=7)))
        # Conditional direction control: paired execution outcomes at the actual timestamps.
        outcomes=[]
        for r in p.itertuples():
            d=int(r.entry_date.strftime("%Y%m%d")); minute=int(r.entry_time_ct)//100*60+int(r.entry_time_ct)%100
            i=lookup[(d,minute)]
            distance=abs(r.entry-r.stop); target_distance=abs(r.tgt-r.entry) if r.setup=="BO" else 0.
            outcomes.append([conditional_exit(D,J,O,H,L,C,i,r.entry,s,distance,target_distance,r.setup=="MO") for s in (1,-1)])
        outcomes=np.array(outcomes); actual=outcomes[np.arange(len(p)),np.where(p.side==1,0,1)]
        same_side_error=float(np.max(np.abs(actual-p.net.to_numpy())))
        rng=np.random.default_rng(7); means=np.where(rng.integers(0,2,(1000,len(p)))==0,outcomes[:,0],outcomes[:,1]).mean(axis=1)
        placebo.append(dict(variant=name,runs=1000,actual_mean=float(p.net.mean()),
            conditional_mean=float(means.mean()),p95=float(np.percentile(means,95)),maximum=float(means.max()),
            p_ge_actual=float((1+(means>=p.net.mean()).sum())/(len(means)+1)),same_side_max_error=same_side_error,
            same_side_exact_count=int(np.isclose(actual,p.net,atol=.001).sum()),trades=len(p)))
        p.assign(conditional_long=outcomes[:,0],conditional_short=outcomes[:,1],same_side_replay=actual).to_csv(OUT/f"conditional_{name}.csv",index=False)
        diagnostics[name]=dict(primary_trades=len(p),excluded_short_warmup=len(t)-len(p),
            overnight_calendar_count=int(p.crosses_calendar_midnight.sum()),session_break_count=int(p.crosses_16ct_break.sum()),
            deadline_1559_count=int(p.crosses_1559_deadline.sum()),worst_trade=float(p.net.min()),
            largest_initial_stop_risk=float(p.initial_stop_risk_per_nq.max()),
            median_bo_initial_stop_risk=float(p.loc[p.setup=="BO","initial_stop_risk_per_nq"].median()),
            top_5pct_share=float(p.net.nlargest(max(1,len(p)//20)).sum()/p.net.sum()),
            net_user_cost_mean=float(p.net_user_cost.mean()),extra_tick_each_fill_mean=float(p.net_extra_tick_each_fill.mean()),
            gross_total=float((p.pts*20).sum()))
        print(f"{name}: uncertainty, Monte Carlo and conditional controls complete",flush=True)
    pd.DataFrame(stats).to_csv(OUT/"metrics.csv",index=False)
    pd.concat(boots,ignore_index=True).to_csv(OUT/"bootstrap_seen_2023.csv",index=False)
    pd.DataFrame(perms).to_csv(OUT/"permutation_seen_2023.csv",index=False)
    pd.DataFrame(monte).to_csv(OUT/"monte_carlo.csv",index=False)
    pd.DataFrame(placebo).to_csv(OUT/"conditional_placebo.csv",index=False)
    # Related MC export: corroboration only; its holiday inputs are absent from uploaded code.
    mc=ROOT/"mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute Twin Continuation v2.xlsx"
    st=pd.read_excel(mc,sheet_name="Settings",header=None)
    pd.DataFrame(st).to_csv(OUT/"related_mc_settings.csv",index=False,header=False)
    prior_ledger=pd.read_csv(ROOT/"checks/candidates/twin_continuation/trades_replica.csv")
    base=frames["combined"]
    oldkeys=["entry_date","entry_time_ct","setup","side"]
    prior_ledger["entry_date"]=pd.to_datetime(prior_ledger.entry_date)
    match=base.merge(prior_ledger,on=oldkeys,suffixes=("_new","_old"))
    manifest=dict(plan_commit="8d661f1",executable_matches_checked_source=True,configurations=variants,
        replay_count=3,new_optimized_rules=0,previously_seen_holdout=True,primary_start=str(PRIMARY.date()),
        grid_first=str(start.date()),grid_last=str(end.date()),bar_count=len(D),multiple_testing_n=trials_n,
        prior_replica_rows=len(prior_ledger),fresh_combined_rows=len(base),matched_prior_entry_keys=len(match),
        matched_net_max_error=float((match.net_new-match.net_old).abs().max()),
        diagnostics=diagnostics,assumed_capital=50000,monte_carlo_is_funded_payout_simulation=False,
        limitations=["No MultiCharts execution; SetExitOnClose interpreted at stated 16:00 session end, not verified chart template",
            "Related MC v2 export includes holiday code absent from upload and is not exact parity proof",
            "IOG off: protective orders are absent during entry bar; no repair applied",
            "Primary June 2018 start gives six calendar months of observed warmup; full early 2018 is sensitivity only",
            "Realized closed-trade daily PnL is not marked-to-market account equity",
            "One-MNQ diagnostics proportionally scale NQ costs; broker micro fee schedule not known",
            "Conditional randomized directions keep actual opportunities and can overlap; not a full-system placebo"],
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in [INPUT,prior,ROOT/"checks/candidates/twin_continuation/replica.py",ROOT/"scratch_data/g24.pkl",mc]})
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,default=str)+"\n")
    print(json.dumps(manifest,indent=2,default=str),flush=True)


if __name__=="__main__":
    main()
