"""S03v2 statistics and frozen causal side/time controls; no import-time IO."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"agents/codex/runtime/or_pullback_python"),str(ROOT/"analysis")]
import argparse
import io
import json
import pickle
import subprocess
from types import SimpleNamespace
import numpy as np
import pandas as pd
from numba import njit
import codex_s03_v2_replay as S
import codex_r2vault_diagnostics as D
import codex_r2vault_personal as Q
import metrics as M
from trials import parse_tier_list
OUT=ROOT/"analysis/outputs/codex_s03_v2/diagnostics"
PERIODS={"2018_22":("2018-01-01","2023-01-01"),"2018_24":("2018-01-01","2025-01-01"),
         "2023_plus":("2023-01-01","2100-01-01"),"2025_plus":("2025-01-01","2100-01-01"),
         "source_claim_available":("2018-01-01","2026-08-01"),"2018_plus":("2018-01-01","2100-01-01")}


def trial_counts():
    context=json.loads((OUT.parent/"context.json").read_text())
    ref=context["reference"]
    data=subprocess.check_output(["git","show",ref+":TIER_LIST.md"],cwd=ROOT)
    target=ROOT/"agents/codex/runtime/s03_v2_tier.md";target.write_bytes(data)
    ranked=len(parse_tier_list(str(target)));n=ranked+21
    return dict(effective_n=n,preregistered_n=n,ranked_items=ranked,prior_unranked=17,new_rule_models=4,
        breakdown=dict(ORPullback=2,NightSwitch=2,Anson=3,NQDB2=5,R2Vault=5,S03v2=4),
        t_threshold=M.t_threshold(n),reference=ref,author_search="claimed anchoredWFO selection, no supplied full trial registry")


@njit(cache=True)
def null_walk(o,h,l,c,observed,f,early,start,entry,side,distance,apex):
    """A single fixed entry: same stops/check-close exits, no new entry signals."""
    stop=S.stop_level(entry,side,distance);pending=False
    for minute in range(start,len(o)):
        if not observed[minute]:continue
        d,j=minute//1440,minute%1440
        if pending:return minute,o[minute],2,0,o[minute],(o[minute]-entry)*side
        adverse=l[minute] if side>0 else h[minute]
        if np.isfinite(stop) and (o[minute]-stop)*side<=0:
            return minute,o[minute],0,0,o[minute],(o[minute]-entry)*side
        if np.isfinite(stop) and (adverse-stop)*side<=0:
            return minute,stop,0,1,stop,(stop-entry)*side
        if j==960:return minute,c[minute],2,3,adverse,(c[minute]-entry)*side
        if 540<=j<=870 and(j-540)%30==0:
            k=(j-540)//30
            if f[d,k,5]==1:
                ub,lb,vw=f[d,k,0],f[d,k,1],f[d,k,2]
                if(side==1 and c[minute]<max(ub,vw))or(side==-1 and c[minute]>min(lb,vw)):pending=True
        if j==900 or(apex and j>=(690 if early[d] else 955)):pending=True
    return -1,np.nan,-1,-1,np.nan,np.nan


@njit(cache=True)
def bulk(o,h,l,c,observed,f,early,starts,entries,sides,distances,apex):
    out=np.empty((len(starts),6))
    for i in range(len(starts)):
        minute,price,kind,segment,adverse,points=null_walk(o,h,l,c,observed,f,early,starts[i],entries[i],sides[i],distances[i],apex)
        out[i,0]=minute;out[i,1]=price;out[i,2]=kind;out[i,3]=segment;out[i,4]=adverse;out[i,5]=points
    return out


def configure():
    D.PERIODS=PERIODS;D.OUT=OUT;D.authorize=S.authorize;D.trial_counts=trial_counts
    D.ALL_MODELS=tuple(S.MODELS);D.MAIN_MODELS=tuple(S.MODELS)


def load():
    S.authorize();configure();OUT.mkdir(parents=True,exist_ok=True)
    with open(ROOT/"scratch_data/g24.pkl","rb") as handle:g=pickle.load(handle)
    with open(ROOT/"agents/codex/runtime/s03_v2_features.pkl","rb") as handle:p=pickle.load(handle)
    replays={}
    for m in S.MODELS:
        t=pd.read_csv(S.OUT/f"{m}_trades.csv",parse_dates=["date","entry_date"])
        a=pd.read_csv(S.OUT/f"{m}_audit.csv",parse_dates=["date"])
        op=pd.read_csv(S.OUT/f"{m}_open_positions.csv")
        replays[m]=SimpleNamespace(trades=t,audit=a,open_positions=op)
    return g,p,replays


def standalone(g,p,replays):
    counts=trial_counts();extra=[]
    days=pd.DatetimeIndex(g.ts[g.trading]);days=days[days>="2018-01-01"]
    all_stats=[];boots=[];monte=[];cache={}
    for model,result in replays.items():
        fees=(1.04,1.24) if model.endswith("apex") else(1.04,1.24,1.275)
        for fee in fees:
            trades=D.money_trades(result.trades,fee)
            for group,sign in(("both",0),("long",1),("short",-1)):
                tt=trades if not sign else trades[trades.side==sign]
                raw=result.trades if not sign else result.trades[result.trades.side==sign]
                op=result.open_positions
                if len(op) and sign:op=op[op.side==sign]
                curve,_,money=Q.candidate_daily(g,raw,days,fee=fee,open_positions=op)
                daily=curve*10
                daily.to_csv(OUT/f"{model}_fee{fee:.3f}_{group}_daily_nq.csv",index_label="date")
                stats=D.standard_stats(tt,daily,days,counts)
                stats.insert(0,"fee_micro",fee);stats.insert(0,"group",group);stats.insert(0,"model",model)
                all_stats.append(stats)
                recent=daily[daily.index>="2023-01-01"]
                boot=D.block_mean_total_ci(recent)
                boot.update(model=model,group=group,fee_micro=fee,period="2023_plus");boots.append(boot)
                for period in("2018_plus","2023_plus","2025_plus"):
                    lo,hi=PERIODS[period]
                    dd=daily[(days>=lo)&(days<hi)]
                    x=tt[(tt.date>=lo)&(tt.date<hi)].net_nq.to_numpy()
                    for size in(1,2):
                        key=(x.tobytes(),dd.to_numpy().tobytes(),size)
                        if key not in cache:
                            dm=D.MC.daily_mc(dd.to_numpy()*size/10,horizon=252,n=5000,block=20,seed=848)
                            tm=D.MC.trade_mc(x*size/10,n=5000,seed=848)
                            cache[key]={**{"daily_"+k:v for k,v in dm.items()},**{"trade_"+k:v for k,v in tm.items()}}
                        monte.append(dict(model=model,group=group,fee_micro=fee,period=period,size_mnq=size,**cache[key]))
            print("standalone",model,fee,flush=True)
    pd.concat(all_stats).to_csv(OUT/"standard_stats.csv",index=False)
    pd.DataFrame(boots).to_csv(OUT/"bootstrap2023_mean_total_ci95.csv",index=False)
    pd.DataFrame(monte).to_csv(OUT/"standalone_mc.csv",index=False)
    (OUT/"trial_counts.json").write_text(json.dumps(counts,indent=2)+"\n")
    for m,r in replays.items():
        # Uploaded source's claimed actual NQ commission$5RT ->0.50/MNQ-equivalent.
        t=D.money_trades(r.trades,.5)
        curve,_,_=Q.candidate_daily(g,r.trades,days,fee=.5,open_positions=r.open_positions)
        stats=D.standard_stats(t,curve*10,days,counts)
        stats.insert(0,"model",m);stats["fee_micro_equivalent"]=.5;extra.append(stats)
    pd.concat(extra).to_csv(OUT/"source_claim_cost_stats.csv",index=False)
    # Reexecuted stop attribution: common/new/disappeared entries, no fixed-list assumption.
    rows=[]
    for suffix in("raw","apex"):
        a=D.money_trades(replays["v1_"+suffix].trades,1.04)
        b=D.money_trades(replays["v2_"+suffix].trades,1.04)
        ak=set(zip(a.entry_flat,a.side));bk=set(zip(b.entry_flat,b.side))
        for period,(lo,hi) in PERIODS.items():
            for name,t,other in(("v1",a,bk),("v2",b,ak)):
                sub=t[(t.date>=lo)&(t.date<hi)].copy()
                common=np.array([(f,s)in other for f,s in zip(sub.entry_flat,sub.side)])
                for label,mask in(("all",np.ones(len(sub),bool)),("common_entry",common),("only_this_version",~common),
                                    ("tainted_history",sub.tainted_prior_sessions.to_numpy()>0)):
                    x=sub.loc[mask,"net_nq"]
                    rows.append(dict(adapter=suffix,version=name,period=period,group=label,trades=len(x),
                        total_nq=x.sum(),avg_nq=x.mean(),t=D.tstat(x)))
    pd.DataFrame(rows).to_csv(OUT/"stop_attribution.csv",index=False)


def controls(g,p,replays):
    from replica import is_early_close
    arrays=[np.ascontiguousarray(getattr(g,k).ravel()) for k in("o","h","l","c")]
    observed=p["observed"].ravel();early=np.array([is_early_close(x) for x in pd.DatetimeIndex(g.ts)],bool)
    last=np.flatnonzero(observed)[-1];unknown=(~observed)&(~p["known_closed"].ravel())
    prefix=np.r_[0,np.cumsum(unknown)];summaries=[];parity=[]
    for m,(factor,apex) in S.MODELS.items():
        r=replays[m];t=r.trades.sort_values("entry_flat").reset_index(drop=True)
        if len(r.open_positions):raise ValueError("Terminal source position needs explicit event extension")
        count=len(t);starts=np.repeat(t.entry_flat.to_numpy(int),2);entries=np.repeat(t.entry.to_numpy(float),2)
        sides=np.tile([-1,1],count).astype(np.int64);distances=np.repeat(t.stop_distance.to_numpy(float),2)
        gates=np.repeat(t.signal_flat.to_numpy(int),2);segments=np.zeros(len(starts),np.int64)
        outcomes=bulk(*arrays,observed,p["f"],early,starts,entries,sides,distances,apex)
        chosen=np.arange(count)*2+(t.side.to_numpy(int)>0)
        # Actual own-side branch must match the complete source ledger.
        np.testing.assert_array_equal(outcomes[chosen,0].astype(int),t.exit_flat)
        np.testing.assert_allclose(outcomes[chosen,1],t.exit,rtol=0,atol=1e-8)
        np.testing.assert_array_equal(outcomes[chosen,2].astype(int),t.kind)
        parity.append(dict(model=m,events=count,all_actual_side_exits_exact=True))
        ends=np.where(outcomes[:,0]>=0,outcomes[:,0],last).astype(int)
        bad=prefix[ends]-prefix[starts]
        rng=np.random.default_rng(848);schedules=np.arange(count)[None,:]*2+rng.integers(0,2,(1000,count))
        values=D._schedule_results(schedules,starts,gates,entries,sides,segments,outcomes,D._period_masks(t.entry_date),
            1.04,arrays[3][last],last,bad,True,*arrays)
        summaries+=D._summarize_null(m,"random_side",values,t,1.04,OUT,
            dict(scope="conditional source event side; flat at signal close; same future source exits",actual_side_parity=count))
        a=r.audit[r.audit.control_eligible];valid_dates=pd.DatetimeIndex(a.date)
        starts=[];entries=[];sides=[];distances=[];gates=[];choices=[]
        for row in a.gridrow.to_numpy(int):
            options=[]
            for k in range(12):
                gate=row*1440+540+30*k;fill=gate+1
                for side in(-1,1):
                    if p["f"][row,k,5]!=1 or not observed[fill]:options.append(-1);continue
                    options.append(len(starts));starts.append(fill);entries.append(arrays[0][fill]);sides.append(side)
                    distances.append(factor*p["f"][row,k,3]*p["f"][row,k,4]);gates.append(gate)
            choices.append(options)
        starts=np.asarray(starts,np.int64);entries=np.asarray(entries);sides=np.asarray(sides,np.int64)
        gates=np.asarray(gates,np.int64);segments=np.zeros(len(starts),np.int64);distances=np.asarray(distances)
        outcomes=bulk(*arrays,observed,p["f"],early,starts,entries,sides,distances,apex)
        ends=np.where(outcomes[:,0]>=0,outcomes[:,0],last).astype(int);bad=prefix[ends]-prefix[starts]
        rng=np.random.default_rng(849);schedules=np.empty((1000,len(choices)),np.int64)
        for i,options in enumerate(choices):
            opts=np.asarray(options,np.int64);schedules[:,i]=opts[rng.integers(0,len(opts),1000)]
        values=D._schedule_results(schedules,starts,gates,entries,sides,segments,outcomes,D._period_masks(valid_dates),
            1.04,arrays[3][last],last,bad,True,*arrays)
        summaries+=D._summarize_null(m,"random_time",values,t,1.04,OUT,
            dict(scope="independent uniform checktime and50/50side,one/day,flat at decision,coverage-onlycalendar",
                 planned_days=len(choices),priced_events=len(starts)),eligible_dates=valid_dates)
        print("controls complete",m,flush=True)
    pd.DataFrame(summaries).to_csv(OUT/"placebo_summary.csv",index=False)
    (OUT/"control_parity.json").write_text(json.dumps(parity,indent=2)+"\n")


if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--phase",choices=["all","standalone","controls"],default="all");args=ap.parse_args()
    g,p,replays=load()
    if args.phase in("all","standalone"):standalone(g,p,replays)
    if args.phase in("all","controls"):controls(g,p,replays)
    manifest=dict(preregistration=S.PREREG,trials=trial_counts(),phase=args.phase,script_sha256=S.sha(__file__),
        standalone_complete=(OUT/"standard_stats.csv").exists(),controls_complete=(OUT/"placebo_summary.csv").exists(),
        replay_manifest_sha256=S.sha(S.OUT/"manifest.json"),new_rule_models=4,
        helpers={n:S.sha(ROOT/"analysis"/n) for n in("codex_r2vault_diagnostics.py","codex_r2vault_personal.py")},
        nulls=dict(draws=1000,side_seed=848,time_seed=849,oneposition=True,no_forced_terminal_close=True),
        review="Self-checked arithmetic only; independent Claude/strategy-checker review pending")
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
