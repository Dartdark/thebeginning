"""Frozen standalone diagnostics for the uploaded Night-Volume Switch.

No prices are read at import. Caller supplies committed-rule replay ledgers and
the explicitly audited eligible calendar. Leg/side splits are diagnostics,
never candidates chosen for the portfolio. All net money is calculated from
raw price geometry using the same micro fees as the joint account comparison.
"""
from pathlib import Path
import io
import json
import subprocess

import numpy as np
import pandas as pd
from numba import njit

import metrics as M
import resampling as R
import montecarlo as MC

PIN = "febc65f1573040abf9a697d1d3468e1bce48c4c0"
PERIODS = {
    "2018_22": ("2018-01-01","2023-01-01"),
    "2023_plus": ("2023-01-01","2100-01-01"),
    "2018_plus": ("2018-01-01","2100-01-01"),
}


def tstat(x):
    x=np.asarray(x,float)
    return float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))) if len(x)>1 and x.std(ddof=1)>0 else np.nan


def trial_counts():
    raw=subprocess.check_output(["git","show",PIN+":TRIALS.csv"])
    tbl=pd.read_csv(io.BytesIO(raw))
    n=len(tbl)+2+2
    return dict(pinned_ref=PIN,pinned_ranked_items=len(tbl),pinned_variants=int(tbl.variants.sum()),
                prior_unranked_ORPullback_variants=2,new_strategy_variants=2,
                dsr_n_items=n,t_threshold=M.t_threshold(n),external_source_search_count="unknown")


def net_trades(raw,fee=1.04):
    t=raw.copy()
    t["date"]=pd.to_datetime(t.date)
    if "leg" not in t and "cell" in t:
        t["leg"]=t.cell
    if "gross_points" not in t:
        t["gross_points"]=(t.exit-t.entry)*t.side
    t["net_nq"]=t.gross_points*20-fee*10-10.
    t["net_mnq"]=t.net_nq/10
    t["slips"]=2
    return t


def groups(t):
    """All frozen diagnostics, retaining empty short/leg groups transparently."""
    yield "both",t
    yield "long",t[t.side>0]
    yield "short",t[t.side<0]
    for leg in sorted(t.leg.dropna().unique()):
        yield "leg_"+str(leg),t[t.leg==leg]


def standard_stats(t,dates,n_items):
    rows=[]
    periods=dict(PERIODS)
    for yr in sorted(set(dates.year)):
        if yr>=2018:
            periods[str(yr)]=(f"{yr}-01-01",f"{yr+1}-01-01")
    for period,(lo,hi) in periods.items():
        calendar=dates[(dates>=lo)&(dates<hi)]
        for group,sub in groups(t):
            tt=sub[(sub.date>=lo)&(sub.date<hi)]
            daily=tt.groupby("date").net_nq.sum().reindex(calendar,fill_value=0.)
            row=M.perf(daily,trades=tt.net_nq)
            row.update(period=period,group=group,t=tstat(tt.net_nq),t_daily=tstat(daily),
                       total_nq=tt.net_nq.sum(),total_mnq=tt.net_mnq.sum(),
                       avg_mnq=tt.net_mnq.mean(),days=len(calendar),
                       dsr_items=M.deflated_sharpe(tt.net_nq,n_items),
                       max_dd_including_start=R.max_dd(daily))
            rows.append(row)
    return pd.DataFrame(rows)


@njit(cache=True)
def _exit_event(o,h,l,c,vwap,entry_j,side,cell,stop_pts,literal_delay):
    """Independent arbitrary-event walker; open entry, rounded stop, VWAP exits."""
    entry=o[entry_j]
    raw=entry-side*stop_pts
    stop=np.floor(raw/.25+1e-10)*.25 if side>0 else np.ceil(raw/.25-1e-10)*.25
    flat=525 if cell==0 else 660
    pending=False
    for j in range(entry_j,flat+1):
        if pending or j==flat:
            return j,(o[j]-entry)*side,2,0,stop
        if j>=entry_j+literal_delay:
            gap=o[j]<=stop if side>0 else o[j]>=stop
            hit=l[j]<=stop if side>0 else h[j]>=stop
            if gap:
                return j,(o[j]-entry)*side,0,0,stop
            if hit:
                return j,(stop-entry)*side,0,1,stop
        if cell==1 and j>599:
            if (c[j]<vwap[j] if side>0 else c[j]>vwap[j]):
                pending=True
    raise ValueError("Complete default event must have exited")


@njit(cache=True)
def _event_tables(o,h,l,c,vwap,rows,cells,stops,literal_delay):
    n=len(rows)
    exits=np.full((n,21,2),-1,np.int64)
    points=np.zeros((n,21,2))
    kinds=np.zeros((n,21,2),np.int64)
    phases=np.zeros((n,21,2),np.int64)
    rounded=np.zeros((n,21,2))
    for i in range(n):
        row,cell=rows[i],cells[i]
        start=510 if cell==0 else 600
        count=11 if cell==0 else 21
        for k in range(count):
            for s in range(2):
                side=1 if s else -1
                jx,pnl,kind,phase,stop=_exit_event(o[row],h[row],l[row],c[row],vwap[row],start+k,side,cell,stops[i],literal_delay)
                exits[i,k,s],points[i,k,s],kinds[i,k,s],phases[i,k,s],rounded[i,k,s]=jx,pnl,kind,phase,stop
    return exits,points,kinds,phases,rounded


def run_placebos(g,source_features,replays,eligible_dates_by_mode,out,n=1000):
    """Two fixed null families per mode; no null result is selected for accounts."""
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    summaries=[]
    for mode,result in replays.items():
        dates=pd.DatetimeIndex(eligible_dates_by_mode[mode])
        t=net_trades(result.trades)
        t=t[t.date.isin(dates)].sort_values(["day","entry_j"]).reset_index(drop=True)
        if t.date.duplicated().any():
            raise AssertionError("Expected mutually exclusive default regimes and one event per day")
        rows=t.day.to_numpy(np.int64)
        cells=(t.leg=="OS").to_numpy(np.int64)
        stops=t.stop_pts.to_numpy(float)
        exits,points,kinds,phases,rounded=_event_tables(g.o,g.h,g.l,g.c,source_features.vwap,rows,cells,stops,int(mode=="literal_delay"))
        sides=(t.side>0).to_numpy(int)
        starts=np.where(cells==0,510,600)
        actual_k=t.entry_j.to_numpy(int)-starts
        ii=np.arange(len(t))
        np.testing.assert_array_equal(exits[ii,actual_k,sides],t.exit_j)
        np.testing.assert_array_equal(kinds[ii,actual_k,sides],t.kind)
        np.testing.assert_allclose(points[ii,actual_k,sides],t.gross_points,rtol=0,atol=1e-10)
        np.testing.assert_allclose(rounded[ii,actual_k,sides],t.stop_px,rtol=0,atol=1e-10)
        np.testing.assert_array_equal(phases[ii,actual_k,sides],(t.exit_phase=="intrabar").astype(int))
        money=points*20-20.4
        for control,seed in (("random_side",848),("random_time",849)):
            rng=np.random.default_rng(seed)
            if control=="random_side":
                k=np.broadcast_to(actual_k,(n,len(t)))
                s=rng.integers(0,2,(n,len(t)))
            else:
                k=(rng.random((n,len(t)))*np.where(cells==0,11,21)).astype(int)
                s=np.broadcast_to(sides,(n,len(t)))
            draws=money[np.broadcast_to(ii,k.shape),k,s]
            records=[]
            for period,(lo,hi) in PERIODS.items():
                keep=(t.date>=lo)&(t.date<hi)
                for group,gmask in (("both",np.ones(len(t),bool)),("leg_T",cells==0),("leg_OS",cells==1)):
                    mask=keep.to_numpy()&gmask
                    real=t.loc[mask,"net_nq"].sum()
                    total=draws[:,mask].sum(1)
                    summaries.append(dict(timing=mode,control=control,period=period,group=group,
                                          real_total_nq=real,real_trades=int(mask.sum()),iterations=n,
                                          null_total_p5=np.quantile(total,.05),null_total_p50=np.median(total),
                                          null_total_p95=np.quantile(total,.95),p_null_ge_real=(1+(total>=real).sum())/(n+1),
                                          independent_walker_parity_events=len(t)))
                    records.extend(dict(iteration=j,period=period,group=group,total_nq=total[j]) for j in range(n))
            pd.DataFrame(records).to_csv(out/f"{mode}_{control}_draws.csv",index=False)
    summary=pd.DataFrame(summaries)
    summary.to_csv(out/"placebo_summary.csv",index=False)
    return summary


def all_night_fade_control(g,source_features,replays,eligible_dates_by_mode,out,n=1000):
    """Heavy-vs-quiet removal control and matched total-net/drawdown masks.

    A joint full-calendar draw retains heavy counts separately in design/recent.
    The control is diagnostic: no all-night fade is passed into the portfolio.
    """
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    feature=source_features.daily
    summaries,draw_records=[],[]
    for mode,result in replays.items():
        dates=pd.DatetimeIndex(eligible_dates_by_mode[mode])
        f=feature[feature.date.isin(dates)&feature.has_829&feature.classified&feature.current_night_valid
                  &(feature.night_move!=0)&(feature.atrD>0)].copy()
        f=f.sort_values("date").reset_index(drop=True)
        rows=f.gridrow.to_numpy(np.int64)
        sides=(-np.sign(f.night_move)).to_numpy(np.int64)
        stops=(f.atrD*.4).to_numpy(float)
        records=[]
        for i in range(len(f)):
            row,side=int(rows[i]),int(sides[i])
            jx,points,kind,phase,stop=_exit_event(g.o[row],g.h[row],g.l[row],g.c[row],source_features.vwap[row],510,side,0,stops[i],int(mode=="literal_delay"))
            records.append(dict(timing=mode,date=f.date.iloc[i],day=row,leg="T",side=side,entry_j=510,exit_j=jx,
                                entry=g.o[row,510],exit=g.o[row,510]+side*points,gross_points=points,
                                kind=kind,stop_px=stop,heavy=bool(f.heavy.iloc[i]),stop_pts=stops[i]))
        t=net_trades(pd.DataFrame(records))
        actual=net_trades(result.trades)
        actual=actual[actual.date.isin(dates)&(actual.leg=="T")].sort_values("date")
        heavy=t[t.heavy].sort_values("date")
        np.testing.assert_array_equal(heavy.date.to_numpy(),actual.date.to_numpy())
        np.testing.assert_allclose(heavy.net_nq,actual.net_nq,rtol=0,atol=1e-10)
        t.to_csv(out/f"{mode}_all_night_fade_control.csv",index=False)
        # One random generator and one full-calendar schedule per mode/draw.
        # Independent matched selection in the two fixed periods preserves both counts.
        rng=np.random.default_rng(850)
        period_masks={p:((t.date>=lo)&(t.date<hi)).to_numpy() for p,(lo,hi) in PERIODS.items() if p!="2018_plus"}
        random_totals={p:np.zeros(n) for p in PERIODS}
        random_dd={p:np.zeros(n) for p in PERIODS}
        for iteration in range(n):
            selected=np.zeros(len(t),bool)
            for period,mask in period_masks.items():
                ix=np.flatnonzero(mask)
                count=int((t.heavy.to_numpy()&mask).sum())
                if count:
                    selected[rng.choice(ix,count,replace=False)]=True
            for period,(lo,hi) in PERIODS.items():
                mask=((t.date>=lo)&(t.date<hi)).to_numpy()
                pnl=np.where(selected&mask,t.net_nq.to_numpy(),0.)[mask]
                random_totals[period][iteration]=pnl.sum()
                random_dd[period][iteration]=R.max_dd(pnl)
                draw_records.append(dict(timing=mode,iteration=iteration,period=period,
                                         total_nq=pnl.sum(),max_dd_nq=R.max_dd(pnl)))
        for period,(lo,hi) in PERIODS.items():
            sub=t[(t.date>=lo)&(t.date<hi)]
            selected=sub[sub.heavy]
            removed=sub[~sub.heavy]
            total=selected.net_nq.sum()
            dd=R.max_dd(np.where(sub.heavy,sub.net_nq,0.))
            rt,rd=random_totals[period],random_dd[period]
            summaries.append(dict(timing=mode,period=period,all_events=len(sub),heavy_events=len(selected),
                                  quiet_removed_events=len(removed),heavy_total_nq=total,
                                  heavy_avg_nq=selected.net_nq.mean(),heavy_t=tstat(selected.net_nq),
                                  quiet_total_nq=removed.net_nq.sum(),quiet_avg_nq=removed.net_nq.mean(),
                                  quiet_t=tstat(removed.net_nq),all_total_nq=sub.net_nq.sum(),
                                  heavy_max_dd_nq=dd,iterations=n,null_total_p5=np.quantile(rt,.05),
                                  null_total_p50=np.median(rt),null_total_p95=np.quantile(rt,.95),
                                  p_null_total_ge_real=(1+(rt>=total).sum())/(n+1),
                                  p_null_dd_le_real=(1+(rd<=dd).sum())/(n+1),
                                  fraction_real_beats_both=np.mean((total>rt)&(dd<rd))))
    summary=pd.DataFrame(summaries)
    summary.to_csv(out/"fade_filter_control_summary.csv",index=False)
    pd.DataFrame(draw_records).to_csv(out/"fade_filter_random_masks.csv",index=False)
    return summary


def standalone_diagnostics(replays,eligible_dates_by_mode,out):
    """Standard metrics/bootstrap/MC using only the frozen coverage universe."""
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    trials=trial_counts()
    tables,mc_rows=[],[]
    for timing,result in replays.items():
        raw=result.trades if hasattr(result,"trades") else result
        dates=pd.DatetimeIndex(eligible_dates_by_mode[timing])
        dates=dates[dates>="2018-01-01"].sort_values().drop_duplicates()
        raw=raw.loc[pd.to_datetime(raw.date).isin(dates)].copy()
        t=net_trades(raw)
        t.to_csv(out/f"{timing}_net_trades.csv",index=False)
        for fee in (1.04,1.24):
            stats=standard_stats(net_trades(raw,fee),dates,trials["dsr_n_items"])
            stats.insert(0,"fee_micro",fee)
            stats.insert(0,"timing",timing)
            tables.append(stats)
        for group,sub in groups(t):
            daily=sub.groupby("date").net_nq.sum().reindex(dates,fill_value=0.)
            recent=daily[daily.index>="2023-01-01"]
            if len(recent)>=10:
                R.bootstrap(recent,n=5000,block=10,seed=848).to_csv(out/f"{timing}_{group}_2023_bootstrap.csv")
            for period in ("2018_plus","2023_plus"):
                lo,hi=PERIODS[period]
                day=daily[(daily.index>=lo)&(daily.index<hi)]
                pnl=sub[(sub.date>=lo)&(sub.date<hi)].net_nq.to_numpy()
                if len(day)<11 or not len(pnl):
                    continue
                for size in (1,2):
                    dm=MC.daily_mc(day.to_numpy()*size/10,horizon=252,n=5000,block=10,seed=848)
                    tm=MC.trade_mc(pnl*size/10,n=5000,seed=848)
                    row={"daily_"+k:v for k,v in dm.items()}
                    row.update({"trade_"+k:v for k,v in tm.items()})
                    row.update(timing=timing,group=group,period=period,size_mnq=size,
                               caveat="Standalone EOD-only trail and trade bootstrap; account test uses joint intraday paths")
                    mc_rows.append(row)
    stats=pd.concat(tables,ignore_index=True)
    stats.to_csv(out/"standard_stats.csv",index=False)
    pd.DataFrame(mc_rows).to_csv(out/"standalone_mc.csv",index=False)
    (out/"trial_counts.json").write_text(json.dumps(trials,indent=2)+"\n")
    return stats


def verify_saved_accounts(out):
    """Independent summary-to-simulation arithmetic check; no strategy rerun."""
    out=Path(out)
    summary=pd.read_csv(out/"funded_summary.csv")
    cols=("year1","year1_p5","year1_p95","year2","year2_p5","year2_p95","blown","all6","days6")
    arrays={(fee,cohort):np.load(out/f"funded_results_{fee:.2f}_{cohort}.npz")
            for fee in (1.04,1.24) for cohort in ("2018_plus","2023_plus")}
    for row in summary.itertuples():
        z=arrays[(row.fee,row.cohort)]
        a,b=z[row.config+"__250"],z[row.config+"__500"]
        actual=[a[:,0].mean(),np.percentile(a[:,0],5),np.percentile(a[:,0],95),
                b[:,0].mean(),np.percentile(b[:,0],5),np.percentile(b[:,0],95),
                b[:,3].mean(),(b[:,1]==6).mean(),np.median(np.where(b[:,1]==6,b[:,2],np.inf))]
        np.testing.assert_allclose(actual,[getattr(row,c) for c in cols],rtol=0,atol=1e-10)
    parity=[]
    for path in sorted(out.glob("funded_parity_*.json")):
        parity.extend(json.loads(path.read_text()))
    if len(parity)!=160 or not all(x["exact"] for x in parity):
        raise AssertionError("Expected160 exact original-simulator parity records")
    evaluation=pd.read_csv(out/"evaluation_summary.csv")
    np.testing.assert_allclose(evaluation.passed+evaluation.failed+evaluation.timed_out,1.,rtol=0,atol=1e-12)
    record=dict(funded_rows_reconciled=len(summary),funded_fields_per_row=len(cols),
                exact_original_simulator_records=len(parity),all_original_simulator_records_exact=True,
                evaluation_rows=len(evaluation),evaluation_outcome_shares_sum_to_one=True,
                tolerance=1e-10,review_scope="Independent output arithmetic and account-code inspection; no author MC parity claim")
    (out/"independent_output_audit.json").write_text(json.dumps(record,indent=2)+"\n")
    return record


if __name__ == "__main__":
    import argparse
    import pickle
    from types import SimpleNamespace
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch",default="scratch_data")
    parser.add_argument("--features",default="agents/codex/runtime/night_volume_switch_features.pkl")
    parser.add_argument("--replay-dir",default="analysis/outputs/codex_night_volume_switch/replay")
    parser.add_argument("--out",default="analysis/outputs/codex_night_volume_switch/diagnostics")
    args=parser.parse_args()
    subprocess.check_call(["git","cat-file","-e","affb482:agents/codex/plans/night_volume_switch.md"])
    with open(Path(args.scratch)/"g24.pkl","rb") as f:
        grid=pickle.load(f)
    with open(args.features,"rb") as f:
        prepared=pickle.load(f)
    replay_dir=Path(args.replay_dir)
    replays={}
    for mode in ("literal_delay","immediate_stop"):
        t=pd.read_csv(replay_dir/f"{mode}_trades.csv",parse_dates=["date"])
        a=pd.read_csv(replay_dir/f"{mode}_audit.csv",parse_dates=["date"])
        replays[mode]=SimpleNamespace(trades=t,audit=a)
    common=None
    for result in replays.values():
        eligible=set(result.audit.loc[result.audit.account_eligible,"date"])
        common=eligible if common is None else common.intersection(eligible)
    calendars={mode:pd.DatetimeIndex(sorted(common)) for mode in replays}
    stats=standalone_diagnostics(replays,calendars,args.out)
    print("standard diagnostics complete",flush=True)
    run_placebos(grid,prepared,replays,calendars,args.out)
    print("random side/time controls complete",flush=True)
    all_night_fade_control(grid,prepared,replays,calendars,args.out)
    print("all-night fade and matched-mask controls complete",flush=True)
    print(stats[(stats.group=="both")&(stats.fee_micro==1.04)&stats.period.isin(PERIODS)]
          [["timing","period","trades","avg_mnq","t","sharpe","dsr_items"]].to_string(index=False),flush=True)
