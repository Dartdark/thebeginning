"""Frozen R2Vault standalone diagnostics and conditional null controls.

No returns load at import. Every figure consumes committed-proxy replay output;
source-PDF claim arithmetic is kept in codex_r2vault_source_audit.py.
"""
from pathlib import Path
import hashlib
import io
import json
import subprocess

import numpy as np
import pandas as pd
from numba import njit

import metrics as M
import montecarlo as MC
import resampling as R

ROOT=Path(__file__).resolve().parents[1]
PREREG="a973f0779b6e10d9c3c29adc6748ed5eba0d5f92"
PIN="172322e5151f45e2cbf1da4dbd9efb20ba12d1a9"
LATEST="1f2d1ffa39fcf59d45b72d92adebecd0153a9151"
NQDB_REF="e8f76b6"
OUT=ROOT/"analysis/outputs/codex_r2vault/diagnostics"
PERIODS={"2018_22":("2018-01-01","2023-01-01"),
         "2018_24":("2018-01-01","2025-01-01"),
         "2023_plus":("2023-01-01","2100-01-01"),
         "2025_plus":("2025-01-01","2100-01-01"),
         "author_OOS_available":("2025-01-15","2026-09-01"),
         "2018_plus_source_end":("2018-01-01","2026-09-01"),
         "2018_plus":("2018-01-01","2100-01-01")}
MAIN_MODELS=("et_raw","et_apex","ct_raw","ct_apex")
ALL_MODELS=MAIN_MODELS+("et_daily_reset_raw",)


def authorize():
    subprocess.check_call(["git","-C",str(ROOT),"cat-file","-e",PREREG+":agents/codex/plans/r2vault.md"])


def tstat(x):
    x=np.asarray(x,float)
    return float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))) if len(x)>1 and x.std(ddof=1)>0 else np.nan


def trial_counts():
    from trials import parse_tier_list
    path=ROOT/"agents/codex/runtime/r2vault_trial_inputs"
    path.mkdir(parents=True,exist_ok=True)
    counts={}
    for name,ref in (("preregistered",PIN),("latest_sensitivity",LATEST)):
        raw=subprocess.check_output(["git","-C",str(ROOT),"show",ref+":TIER_LIST.md"])
        tier=path/(ref+".md")
        tier.write_bytes(raw)
        ranked=len(parse_tier_list(str(tier)))
        csv=pd.read_csv(io.BytesIO(subprocess.check_output(["git","-C",str(ROOT),"show",ref+":TRIALS.csv"])))
        counts[name]=dict(ref=ref,ranked_tier_items=ranked,trial_csv_items=len(csv),
                          n_known_lower_bound=max(ranked,len(csv))+12,tier_sha256=hashlib.sha256(raw).hexdigest())
    external_path="analysis/outputs/codex_nqdb2_test/trial_ledger.csv"
    external_raw=subprocess.check_output(["git","-C",str(ROOT),"show",NQDB_REF+":"+external_path])
    external=pd.read_csv(io.BytesIO(external_raw))
    profile_column=next((c for c in external.columns if str(c).lower() in ("profile","variant","model")),None)
    if profile_column is None:
        raise ValueError("Concurrent trial ledger lacks a profile identifier")
    profiles=sorted(external[profile_column].dropna().unique().tolist())
    if profiles!=["A0","A1","E1","S0","S1"]:
        raise ValueError("Unexpected known concurrent trial profiles")
    n=max(v["n_known_lower_bound"] for v in counts.values())+len(profiles)
    return dict(snapshots=counts,preregistered_unranked_models=12,known_unranked_models=17,
                known_unranked_breakdown=dict(ORPullback=2,NightSwitch=2,Anson=3,R2Vault=5,NQDB2=5),
                effective_n=n,preregistered_n=counts["preregistered"]["n_known_lower_bound"],
                t_threshold=M.t_threshold(n),author_search="PDF claims2versions; full registry unknown",
                concurrent_research=dict(ref=NQDB_REF,path=external_path,profiles=profiles,count=len(profiles),
                                         sha256=hashlib.sha256(external_raw).hexdigest(),
                                         note="Count distinct profiles once; design/recent periods are not separate strategy trials"))


def target_mask(t):
    m=np.zeros(len(t),bool)
    if "kind" in t:
        m|=t.kind.astype(str).str.lower().isin(("1","1.0","target","tp","profit_target","limit")).to_numpy()
    for field in ("exit_reason","reason","kind_label"):
        if field in t:
            m|=t[field].astype(str).str.lower().isin(("target","tp","profit_target","limit")).to_numpy()
    return m


def money_trades(t,fee):
    t=t.copy()
    t["date"]=pd.to_datetime(t.get("entry_date",t.date))
    if "exit_date" in t:
        t["exit_date"]=pd.to_datetime(t.exit_date)
    t["slips"]=1+(~target_mask(t)).astype(int)
    t["net_nq"]=(t.exit-t.entry)*t.side*20-float(fee)*10-t.slips*5
    t["net_mnq"]=t.net_nq/10
    return t


def standard_stats(t,daily,days,trials,universe="all_source_events"):
    rows=[]
    periods=dict(PERIODS)
    for yr in sorted(days.year.unique()):
        periods[str(yr)]=(f"{yr}-01-01",f"{yr+1}-01-01")
    for period,(lo,hi) in periods.items():
        sub=t[(t.date>=lo)&(t.date<hi)]
        d=daily[(days>=lo)&(days<hi)]
        row=M.perf(d,trades=sub.net_nq)
        row.update(period=period,total_nq=sub.net_nq.sum(),total_mnq=sub.net_mnq.sum(),avg_mnq=sub.net_mnq.mean(),
                   t=tstat(sub.net_nq),t_daily=tstat(d),daily_total_nq=d.sum(),days=len(d),
                   max_dd_including_start=R.max_dd(d),universe=universe,
                   dsr_preregistered=M.deflated_sharpe(sub.net_nq,trials["preregistered_n"]) if len(sub)>=10 else np.nan,
                   dsr_conservative_latest=M.deflated_sharpe(sub.net_nq,trials["effective_n"]) if len(sub)>=10 else np.nan,
                   trade_period="entry date; closed trades only",daily_period="marked session date; includes terminal unrealized")
        row["n_exits_after_period_end"]=int((sub.exit_date>=pd.Timestamp(hi)).sum()) if "exit_date" in sub else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def block_mean_total_ci(daily,n=5000,block=20,seed=903):
    x=np.asarray(daily,float)
    rng=np.random.default_rng(seed)
    totals=np.empty(n)
    nb=int(np.ceil(len(x)/block))
    for start in range(0,n,100):
        size=min(100,n-start)
        st=rng.integers(0,len(x)-block,(size,nb))
        ix=(st[:,:,None]+np.arange(block)).reshape(size,-1)[:,:len(x)]
        totals[start:start+size]=x[ix].sum(1)
    lo,hi=np.quantile(totals,[.025,.975])
    return dict(days=len(x),block=block,draws=n,seed=seed,total_actual=x.sum(),total_ci95_lo=lo,total_ci95_hi=hi,
                mean_day_actual=x.mean(),mean_day_ci95_lo=lo/len(x),mean_day_ci95_hi=hi/len(x),
                annualized_mean_ci95_lo=lo/len(x)*252,annualized_mean_ci95_hi=hi/len(x)*252,
                p_total_le_zero=np.mean(totals<=0))


def run_standalone(g,replays,open_positions,out=OUT,days=None):
    """Every frozen model; no timezone, exit or profitable-side selection."""
    from codex_r2vault_personal import candidate_daily
    authorize()
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    days=pd.DatetimeIndex(g.ts[g.trading]) if days is None else pd.DatetimeIndex(days)
    days=days[days>="2018-01-01"]
    trials=trial_counts()
    all_stats,boot,monte=[],[],[]
    cache={}
    for model,result in replays.items():
        raw=result.trades if hasattr(result,"trades") else result
        final=open_positions.get(model,pd.DataFrame())
        fees=(1.04,1.24) if model.endswith("apex") else (1.04,1.24,1.275)
        for fee in fees:
            trades=money_trades(raw,fee)
            trades.to_csv(out/f"{model}_fee{fee:.3f}_closed_trades.csv",index=False)
            for group,sign in (("both",0),("long",1),("short",-1)):
                tt=trades if not sign else trades[trades.side==sign]
                op=final if not sign or not len(final) else final[final.side==sign]
                raw_sub=raw if not sign else raw[raw.side==sign]
                curve,_,mark_audit=candidate_daily(g,raw_sub,days,fee=fee,open_positions=op)
                # The helper's money is perMNQ; metrics here are explicitlyperNQ.
                daily=curve*10
                daily.to_csv(out/f"{model}_fee{fee:.3f}_{group}_daily_nq.csv")
                if group=="both":
                    (out/f"{model}_fee{fee:.3f}_mark_audit.json").write_text(json.dumps(mark_audit,indent=2,default=str)+"\n")
                stats=standard_stats(tt,daily,days,trials)
                stats.insert(0,"fee_micro",fee)
                stats.insert(0,"group",group)
                stats.insert(0,"model",model)
                all_stats.append(stats)
                if group=="short" and not len(tt) and not len(op):
                    continue
                recent=daily[daily.index>="2023-01-01"]
                if len(recent)>20:
                    row=block_mean_total_ci(recent)
                    row.update(model=model,fee_micro=fee,group=group,period="2023_plus")
                    boot.append(row)
                for period in ("2018_plus","2023_plus","2025_plus","author_OOS_available"):
                    lo,hi=PERIODS[period]
                    d=daily[(days>=lo)&(days<hi)]
                    pnl=tt[(tt.date>=lo)&(tt.date<hi)].net_nq.to_numpy()
                    if len(d)<=20 or not len(pnl):
                        continue
                    for size in (1,2):
                        key=(hashlib.sha256(pnl.tobytes()).hexdigest(),hashlib.sha256(d.to_numpy().tobytes()).hexdigest(),size)
                        if key not in cache:
                            dm=MC.daily_mc(d.to_numpy()*size/10,horizon=252,n=5000,block=20,seed=848)
                            tm=MC.trade_mc(pnl*size/10,n=5000,seed=848)
                            cache[key]={**{"daily_"+k:v for k,v in dm.items()},**{"trade_"+k:v for k,v in tm.items()}}
                        monte.append(dict(model=model,fee_micro=fee,group=group,period=period,size_mnq=size,
                                          **cache[key],caveat="Standalone EOD trail/trade bootstrap; full accounts model joint minute risk"))
            print("standalone complete",model,fee,flush=True)
    stats=pd.concat(all_stats,ignore_index=True)
    stats.to_csv(out/"standard_stats.csv",index=False)
    pd.DataFrame(boot).to_csv(out/"bootstrap2023_mean_total_ci95.csv",index=False)
    pd.DataFrame(monte).to_csv(out/"standalone_mc.csv",index=False)
    (out/"trial_counts.json").write_text(json.dumps(trials,indent=2)+"\n")
    return stats


def staged_design_trade_stats(replay_dir,out=OUT):
    """Audit only exits known at the actual design cutoff, before recent prices."""
    rows=[]
    trials=trial_counts()
    for model in ALL_MODELS:
        t=pd.read_csv(Path(replay_dir)/f"{model}_2018_22_trades.csv")
        op=pd.read_csv(Path(replay_dir)/f"{model}_2018_22_open_positions.csv")
        fees=(1.04,1.24) if model.endswith("apex") else (1.04,1.24,1.275)
        for fee in fees:
            net=money_trades(t,fee)
            x=net.net_nq
            gain=x[x>0].sum()
            loss=-x[x<0].sum()
            rows.append(dict(model=model,fee_micro=fee,closed_at_design_cutoff=len(net),
                             open_at_design_cutoff=len(op),total_nq=x.sum(),avg_nq=x.mean(),t=tstat(x),
                             profit_factor=gain/loss if loss else np.nan,win=np.mean(x>0),
                             dsr311=M.deflated_sharpe(x,trials["effective_n"]) if len(x)>=10 else np.nan,
                             scope="Only closes executed before design stage ended; may exclude an older entry later closed in2023"))
    table=pd.DataFrame(rows)
    table.to_csv(Path(out)/"staged_design_closed_trade_stats.csv",index=False)
    return table


@njit(cache=True)
def _schedule_results(schedules,starts,gates,entries,sides,segments,outcomes,period_masks,
                      fee,terminal_price,last_flat,unknown_counts,close_gate,opens,highs,lows,closes):
    """One-position null chronology; DD is explicitly closed-trade equity."""
    n,plans=schedules.shape
    periods=period_masks.shape[1]
    # Closednet,closedcount,accepted,open,overlaps,missing,DD,terminalunrealized,unknown-held-count.
    result=np.zeros((n,periods,9))
    for rep in range(n):
        last_exit=-1
        last_segment=0
        last_price=0.
        cum=np.zeros(periods)
        peak=np.zeros(periods)
        for p in range(plans):
            event=schedules[rep,p]
            if event<0:
                for k in range(periods):
                    if period_masks[p,k]: result[rep,k,5]+=1
                continue
            blocked=last_exit>gates[event]
            # A conditional entry inside a minute cannot precede the earlier
            # null position's exit along the same deterministic path segment.
            if not close_gate and last_exit==starts[event]:
                seg=segments[event]
                if last_segment>seg:
                    blocked=True
                elif last_segment==seg and seg>0:
                    op,hi,lo,cl=opens[starts[event]],highs[starts[event]],lows[starts[event]],closes[starts[event]]
                    if hi-op<=op-lo:
                        nodes=np.array([op,hi,lo,cl])
                    else:
                        nodes=np.array([op,lo,hi,cl])
                    direction=nodes[seg]-nodes[seg-1]
                    blocked=(last_price>entries[event] if direction>0 else last_price<entries[event])
            if blocked:
                for k in range(periods):
                    if period_masks[p,k]: result[rep,k,4]+=1
                continue
            exit_flat=int(outcomes[event,0])
            for k in range(periods):
                if period_masks[p,k]:
                    result[rep,k,2]+=1
                    result[rep,k,8]+=int(unknown_counts[event]>0)
            if exit_flat<0:
                last_exit=last_flat+1
                unrealized=(terminal_price-entries[event])*sides[event]*20-fee*10-5
                for k in range(periods):
                    if period_masks[p,k]:
                        result[rep,k,3]+=1
                        result[rep,k,7]+=unrealized
                continue
            last_exit=exit_flat
            last_segment=int(outcomes[event,3])
            last_price=outcomes[event,1]
            if int(outcomes[event,2])==1 and last_segment>0:
                # Limit fill is atTP, but causal execution waits forTP+/-1.
                # Compare event prices, not favourable accounting fill prices.
                last_price+=sides[event]
            net=outcomes[event,5]*20-fee*10-5-(0 if int(outcomes[event,2])==1 else 5)
            for k in range(periods):
                if period_masks[p,k]:
                    result[rep,k,0]+=net
                    result[rep,k,1]+=1
                    cum[k]+=net
                    peak[k]=max(peak[k],cum[k])
                    result[rep,k,6]=max(result[rep,k,6],peak[k]-cum[k])
    return result


def control_fixtures():
    """Invented schedules test overlap and target-trigger chronology only."""
    schedules=np.array([[0,1]],dtype=np.int64)
    starts=np.array([1,5],dtype=np.int64)
    entries=np.array([60.,100.5])
    sides=np.ones(2,dtype=np.int64)
    segments=np.array([0,2],dtype=np.int64)
    outcomes=np.array([[5.,100.,1.,2.,60.,40.],[8.,140.5,1.,1.,100.5,40.]])
    arrays=[np.full(10,x) for x in (95.,110.,90.,105.)]
    masks=np.ones((2,1),dtype=np.bool_)
    unknown=np.zeros(2,dtype=np.int64)
    r=_schedule_results(schedules,starts,starts,entries,sides,segments,outcomes,masks,
                        1.04,105.,9,unknown,False,*arrays)
    assert r[0,0,1]==1 and r[0,0,4]==1
    # A market order planned atclose4 cannot enter atopen5 if held untilopen5.
    outcomes[0,3]=0
    gates=np.array([0,4],dtype=np.int64)
    r=_schedule_results(schedules,starts,gates,entries,sides,segments,outcomes,masks,
                        1.04,105.,9,unknown,True,*arrays)
    assert r[0,0,1]==1 and r[0,0,4]==1
    # No invented terminal exit when a bracket remains open.
    outcomes[0,0]=-1
    r=_schedule_results(schedules,starts,gates,entries,sides,segments,outcomes,masks,
                        1.04,105.,9,unknown,True,*arrays)
    assert r[0,0,3]==1 and r[0,0,1]==0 and r[0,0,4]==1
    np.testing.assert_allclose(r[0,0,7],(105.-60.)*20-10.4-5,rtol=0,atol=1e-10)
    return dict(invented_prices_only=True,target_through_event_before_fill_comparison=True,
                flat_at_decision_close_required=True,terminal_open_mark_separate=True,no_terminal_executed_fill=True)


def _period_masks(dates):
    dates=pd.DatetimeIndex(dates)
    return np.array([((dates>=lo)&(dates<hi)) for lo,hi in PERIODS.values()]).T


def _flat_arrays(g,prepared):
    end=(prepared.cutoff_row+1)*1440
    arrays=[np.ascontiguousarray(getattr(g,f).ravel()[:end]) for f in ("o","h","l","c")]
    observed=np.ascontiguousarray(prepared.observed.ravel())
    force=np.ascontiguousarray(prepared.force_open[1])
    unknown=(~observed)&(~prepared.known_closed.ravel())
    prefix=np.r_[0,np.cumsum(unknown)]
    last=np.flatnonzero(observed)[-1]
    return arrays,observed,force,prefix,last


def _bulk_outcomes(g,prepared,starts,entries,sides,segments,model):
    from codex_r2vault_replay import walk_fixed_many,MODELS
    arrays,observed,force,prefix,last=_flat_arrays(g,prepared)
    outcomes=walk_fixed_many(*arrays,observed,force,np.asarray(starts,np.int64),np.asarray(entries,float),
                             np.asarray(sides,np.int64),np.asarray(segments,np.int64),MODELS[model]["apex"])
    ends=np.where(outcomes[:,0]>=0,outcomes[:,0],last).astype(int)
    unknown=prefix[ends]-prefix[np.asarray(starts,int)]
    return outcomes,unknown,last,arrays


def _summarize_null(model,control,values,actual,fee,out,extra,eligible_dates=None):
    fields=("closed_net_nq","closed_trades","accepted_entries","open_at_end","overlap_skips",
            "missing_planned_open_skips","closed_equity_dd_nq","terminal_unrealized_nq","unknown_held_events")
    rows,draws=[],[]
    actual=money_trades(actual,fee).sort_values("entry_flat")
    for k,(period,(lo,hi)) in enumerate(PERIODS.items()):
        base=actual[(actual.date>=lo)&(actual.date<hi)]
        total=values[:,k,0]
        count=values[:,k,1]
        expectancy=np.divide(total,count,out=np.full(len(count),np.nan),where=count>0)
        references={"all_source_closed_entries":base}
        if eligible_dates is not None:
            references["actual_entry_days_in_control_calendar"]=base[base.date.isin(eligible_dates)]
        for reference,real in references.items():
            real_total=real.net_nq.sum()
            real_avg=real.net_nq.mean()
            rows.append(dict(model=model,control=control,fee_micro=fee,period=period,iterations=len(values),reference_scope=reference,
                         actual_closed_trades=len(real),actual_closed_total_nq=real_total,actual_avg_nq=real_avg,
                         actual_closed_equity_dd_nq=R.max_dd(real.net_nq) if len(real) else 0.,
                         null_total_p5=np.quantile(total,.05),null_total_p50=np.median(total),null_total_p95=np.quantile(total,.95),
                         null_expectancy_p50=np.nanmedian(expectancy),
                         null_count_min=count.min(),null_count_mean=count.mean(),null_count_max=count.max(),
                         null_closed_dd_p50=np.median(values[:,k,6]),null_closed_dd_p95=np.quantile(values[:,k,6],.95),
                         null_open_at_end_mean=values[:,k,3].mean(),null_unrealized_mean=values[:,k,7].mean(),
                         null_unknown_held_events_mean=values[:,k,8].mean(),
                         p_null_total_ge_actual=(1+(total>=real_total).sum())/(len(values)+1),
                         p_null_expectancy_ge_actual=(1+(expectancy>=real_avg).sum())/(len(values)+1),
                         drawdown_definition="chronological CLOSED-trade equity, not MTM or account risk",
                         **extra))
        for rep in range(len(values)):
            row=dict(model=model,control=control,period=period,iteration=rep)
            row.update({f:values[rep,k,i] for i,f in enumerate(fields)})
            draws.append(row)
    pd.DataFrame(draws).to_csv(Path(out)/f"{model}_{control}_draws.csv",index=False)
    return rows


def run_controls(g,prepared,replays,out=OUT,n=1000,fee=1.04):
    """Mainfour precommitted controls; no actual source-timezone selection."""
    from codex_r2vault_replay import MODELS
    from replica import is_early_close
    authorize()
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    summaries=[]
    for model in MAIN_MODELS:
        result=replays[model]
        raw=result.trades if hasattr(result,"trades") else result
        actual=raw.sort_values("entry_flat").reset_index(drop=True)
        op=result.open_positions if hasattr(result,"open_positions") else pd.DataFrame()
        planned=pd.concat([actual,op],ignore_index=True).sort_values("entry_flat").reset_index(drop=True) if len(op) else actual
        closed=(planned.exit_flat.notna()&(planned.exit_flat>=0)).to_numpy() if "exit_flat" in planned else np.ones(len(planned),bool)
        count=len(planned)
        starts=np.repeat(planned.entry_flat.to_numpy(int),2)
        entries=np.repeat(planned.entry.to_numpy(float),2)
        segments=np.repeat(planned.entry_segment.to_numpy(int),2)
        sides=np.tile(np.array([-1,1]),count)
        outcomes,unknown,last,arrays=_bulk_outcomes(g,prepared,starts,entries,sides,segments,model)
        # The long branch must reproduce allactual fixed entry exits first.
        long=outcomes[1::2]
        checked=planned.loc[closed]
        np.testing.assert_array_equal(long[closed,0].astype(int),checked.exit_flat.to_numpy(int))
        np.testing.assert_allclose(long[closed,1],checked.exit,rtol=0,atol=1e-10)
        np.testing.assert_array_equal(long[closed,2].astype(int),checked.kind.to_numpy(int))
        np.testing.assert_array_equal(long[closed,3].astype(int),checked.exit_segment.to_numpy(int))
        np.testing.assert_allclose(long[closed,5],checked.gross_points,rtol=0,atol=1e-10)
        if (~closed).any():
            np.testing.assert_array_equal(long[~closed,0],-1.)
        rng=np.random.default_rng(848)
        schedules=np.arange(count)[None,:]*2+rng.integers(0,2,(n,count))
        values=_schedule_results(schedules,starts,starts,entries,sides,segments,outcomes,_period_masks(planned.entry_date),
                                 fee,arrays[3][last],last,unknown,False,*arrays)
        summaries+=_summarize_null(model,"random_side",values,actual,fee,out,
                                  dict(scope="event-conditioned side falsifier; prior null holds skip overlapping source events",
                                       actual_long_walker_parity_events=count,actual_terminal_source_entries=len(op)))
        print("side controls complete",model,count,flush=True)

        cfg=MODELS[model]
        bars=prepared.bars
        if not hasattr(result,"audit") or "control_eligible" not in result.audit:
            raise ValueError("Independent coverage-only control calendar is required")
        eligible_audit=result.audit[result.audit.control_eligible & (pd.to_datetime(result.audit.date)>="2018-01-01")]
        trade_rows=set(eligible_audit.gridrow.to_numpy(int))
        valid_dates=pd.DatetimeIndex(pd.to_datetime(eligible_audit.date))
        bar_by_row={int(row):part for row,part in bars.groupby("gridrow",sort=True)}
        planned_dates=[]
        choices=[]
        ts,gs,es,ss,cs=[],[],[],[],[]
        missing_closure_choices=0
        for row in sorted(trade_rows):
            part=bar_by_row.get(row,pd.DataFrame())
            date=pd.Timestamp(g.ts[int(row)])
            end=min(cfg["end"],690) if cfg["apex"] and is_early_close(date) else cfg["end"]
            observed_closes=set(part.close_flat.to_numpy(int)) if len(part) else set()
            day_choices=[]
            for minute in range(cfg["start"],end,5):
                gate=int(row)*1440+minute
                fill=gate+1
                if gate not in observed_closes or fill>=len(arrays[0]) or not prepared.observed.ravel()[fill]:
                    day_choices.append(-1)
                    if fill<len(arrays[0]) and (prepared.known_closed.ravel()[gate] or prepared.known_closed.ravel()[fill]):
                        missing_closure_choices+=1
                    continue
                day_choices.append(len(ts))
                ts.append(fill);gs.append(gate);es.append(arrays[0][fill]);ss.append(1);cs.append(0)
            planned_dates.append(date)
            choices.append(day_choices)
        starts=np.asarray(ts,int);gates=np.asarray(gs,int);entries=np.asarray(es,float)
        sides=np.asarray(ss,int);segments=np.asarray(cs,int)
        outcomes,unknown,last,arrays=_bulk_outcomes(g,prepared,starts,entries,sides,segments,model)
        rng=np.random.default_rng(849)
        schedules=np.empty((n,len(choices)),np.int64)
        for i,options in enumerate(choices):
            options=np.asarray(options,int)
            schedules[:,i]=options[rng.integers(0,len(options),n)]
        values=_schedule_results(schedules,starts,gates,entries,sides,segments,outcomes,_period_masks(planned_dates),
                                 fee,arrays[3][last],last,unknown,True,*arrays)
        summaries+=_summarize_null(model,"random_time",values,actual,fee,out,
                                  dict(scope="one planned decision per independently observed trading day; maxoneposition; missing nextminute open skipped",
                                       independent_planned_days=len(choices),possible_priced_events=len(starts),
                                       actual_long_walker_parity_events=count,possible_known_closure_skip_choices=missing_closure_choices),
                                  eligible_dates=valid_dates)
        print("time controls complete",model,len(choices),len(starts),flush=True)
    table=pd.DataFrame(summaries)
    table.to_csv(out/"placebo_summary.csv",index=False)
    return table


if __name__=="__main__":
    import argparse
    import pickle
    from types import SimpleNamespace
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch",default="scratch_data")
    parser.add_argument("--replay-dir",default="analysis/outputs/codex_r2vault/replay")
    parser.add_argument("--features",default="agents/codex/runtime/r2vault_features.pkl")
    parser.add_argument("--out",default=str(OUT))
    parser.add_argument("--phase",choices=("all","standalone","controls"),default="all")
    args=parser.parse_args()
    authorize()
    out=Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    with open(Path(args.scratch)/"g24.pkl","rb") as f:
        grid=pickle.load(f)
    with open(args.features,"rb") as f:
        prepared=pickle.load(f)
    replay_dir=Path(args.replay_dir)
    replays,opens={},{ }
    for model in ALL_MODELS:
        t=pd.read_csv(replay_dir/f"{model}_trades.csv",parse_dates=["entry_date","date"])
        a=pd.read_csv(replay_dir/f"{model}_audit.csv",parse_dates=["date"])
        op=pd.read_csv(replay_dir/f"{model}_open_positions.csv")
        replays[model]=SimpleNamespace(trades=t,audit=a,open_positions=op)
        opens[model]=op
    fixture=control_fixtures()
    (out/"control_fixtures.json").write_text(json.dumps(fixture,indent=2)+"\n")
    if args.phase in ("all","standalone"):
        run_standalone(grid,replays,opens,out)
        staged_design_trade_stats(replay_dir,out)
    if args.phase in ("all","controls"):
        run_controls(grid,prepared,replays,out)
    files={}
    for model in ALL_MODELS:
        for suffix in ("trades","audit","open_positions"):
            p=replay_dir/f"{model}_{suffix}.csv"
            files[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    reproduction=dict(preregistration=PREREG,calendar_clarification="dab01a8",models=list(ALL_MODELS),
                      controlled_models=list(MAIN_MODELS),null_draws_per_family=1000,side_seed=848,time_seed=849,
                      bootstrap_n=5000,bootstrap_block=20,bootstrap_interval=.95,
                      no_control_time_cap_or_terminal_executed_close=True,
                      null_DD="closed-trade equity only; open unrealized separate; main metrics use MTM",
                      random_time="coverage-only calendar; fixed five-minute slots; missing decision/nextminuteOpen skips; no future rescue",
                      script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),inputs=files,
                      trial_counts=trial_counts())
    (out/"reproduction.json").write_text(json.dumps(reproduction,indent=2)+"\n")
    print("R2Vault diagnostics finished",args.phase,flush=True)
