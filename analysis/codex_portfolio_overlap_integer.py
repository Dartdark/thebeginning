"""Integer-aware shared-price overlap sensitivity of the fixed funded books.

Uses only unchanged prior-audit unit ledgers; not an exact tick/fill certificate.
"""
from pathlib import Path
import gc
import json
import os
import pickle
import subprocess
import sys
MECHANICS_ONLY="--mechanics" in sys.argv
import numpy as np
import pandas as pd
import codex_portfolio_audit_config as A

ROOT=A.ROOT;SOURCE=Path("/workspace/scratch/claude_audit_replay")
OUT=ROOT/"analysis/outputs/codex_portfolio_overlap_integer_20261030"
OUT.mkdir(parents=True,exist_ok=True)
os.environ.setdefault("NUMBA_CACHE_DIR",str(A.RUNTIME/"overlap_numba"))
sys.dont_write_bytecode=True
sys.path.insert(0,str(SOURCE/"analysis"));sys.argv=[__file__,str(A.SCRATCH),"library"]
from numba import njit
import funded_sim as F50
import funded_sim150 as F150
import codex_ob_v2_accounts as TABLE
import codex_anson_accounts as ENGINE


@njit(cache=True)
def corrected_minima(W,positions,ranges,eligible,stateq,counts,reference_low,active_days):
    K,D,M=W.shape;out=reference_low.copy()
    for d in range(D):
        if not active_days[d]:continue
        for s in range(counts[d]):
            low=0.
            for j in range(M):
                x=0.;longs=0.;shorts=0.
                for k in range(K):
                    q=stateq[d,s,k]
                    if q>0:
                        x+=q*W[k,d,j]
                        p=q*positions[k,d,j]
                        if p>0:longs+=p
                        else:shorts-=p
                if eligible[d,j]:x+=min(longs,shorts)*ranges[d,j]*2.
                low=min(low,x)
            out[d,s]=low
    return out


def mechanics():
    W=np.array([[[0.,-20.,0.]],[[0.,-20.,0.]]])
    P=np.array([[[0.,1.,0.]],[[0.,-1.,0.]]])
    ranges=np.array([[0.,20.,0.]])
    q=np.array([[[0.,0.],[1.,1.]]]);counts=np.array([2]);old=np.array([[0.,-40.]])
    new=corrected_minima(W,P,ranges,np.ones((1,3),bool),q,counts,old,np.array([True]))
    assert np.array_equal(new,[[0.,0.]])
    blocked=corrected_minima(W,P,ranges,np.zeros((1,3),bool),q,counts,old,np.array([True]))
    assert np.array_equal(blocked,old)
    fixtures=[]
    for base,f in [(np.array([1.,1.]),.5),(np.array([3.,1.]),.75)]:
        exact=np.floor(base*f+1e-9)
        source_credit=np.floor(100*f)/100*min(base)*20*2
        actual_credit=min(exact)*20*2
        assert source_credit>0 and actual_credit==0
        fixtures.append(dict(base=base.tolist(),factor=f,actual_lots=exact.tolist(),
                             source_credit=source_credit,integer_credit=actual_credit))
    A.dump(OUT/"mechanics.json",dict(all_passed=True,zero_lot_and_hedged_fixtures=True,
        event_bar_credit_rejected=True,credit_piece_counterexamples=fixtures))


def run():
    assert subprocess.check_output(["git","-C",str(SOURCE),"rev-parse","HEAD"],text=True).strip()=="88b5e95f5d10f468a0865c693b302fb48cdb956b"
    subprocess.check_call(["git","-C",str(ROOT),"cat-file","-e","HEAD:agents/codex/plans/portfolio_overlap_integer_20261030.md"])
    meta=dict(np.load(A.RUNTIME/"dates_atr.npz"));dates=pd.to_datetime(meta["dates"].astype(str))
    g=pickle.load(open(A.SCRATCH/"g24.pkl","rb"))
    range_all=[]
    for date in dates:
        r=np.searchsorted(g.dates,int(date.strftime("%Y%m%d")))
        range_all.append(np.r_[g.h[r-1,1021:]-g.l[r-1,1021:],g.h[r,:1021]-g.l[r,:1021]])
    range_all=np.asarray(range_all);del g;gc.collect()
    rows=[];parity=[];verified=[];changes=[];inputs={}
    for home in ["funded_50","funded_150"]:
        plan=dict(A.ROSTERS[home])
        if home=="funded_150":
            for key in ["VB_F","MON","BRIDGE"]:plan[key]=1
        keys=list(plan);units=[dict(np.load(A.RUNTIME/(k+".npz"))) for k in keys]
        base=np.array([v[1]/(meta["atr"]*v[2]*2) if isinstance(v,list) else np.full(len(dates),v) for v in plan.values()])
        use=np.flatnonzero(np.logical_and.reduce([u["known"] for u in units])&np.isfinite(base).all(0))
        W=np.ascontiguousarray(np.array([u["W"]-1.04*u["F"]-u["S"] for u in units])[:,use,:])
        C=np.ascontiguousarray(np.array([u["G"]-1.04*u["N"]-u["S"][:,-1] for u in units])[:,use])
        positions=[];event=np.zeros((len(dates),1440),bool)
        for k,u in zip(keys,units):
            t=pd.read_csv(A.OUT/f"{k}_unit_ledger.csv",parse_dates=["date"])
            nq=t.market.iloc[0]=="NQ"
            positions.append(u["Q"] if nq else np.zeros_like(u["Q"]))
            if nq:
                ix=dates.get_indexer(t.date)
                event[ix,t.j0.to_numpy(int)]=True;event[ix,t.j1.to_numpy(int)]=True
            inputs[k]=A.sha(A.RUNTIME/(k+".npz"))
        positions=np.ascontiguousarray(np.asarray(positions)[:,use,:]);ranges=range_all[use]
        eligible=np.ascontiguousarray((~event[use])&np.isfinite(ranges))
        ranges=np.ascontiguousarray(np.nan_to_num(ranges,nan=0.))
        full=np.floor(base[:,use]+1e-9)
        longs=np.sum(full[:,:,None]*np.maximum(positions,0),axis=0)
        shorts=np.sum(full[:,:,None]*np.maximum(-positions,0),axis=0)
        active=np.any((longs>0)&(shorts>0)&eligible,axis=1)
        histdates=np.load(A.OUT/f"{home}_main_history_dates.npy")
        hist=dates[use].get_indexer(pd.to_datetime(histdates.ravel().astype(str))).reshape(histdates.shape)
        assert (hist>=0).all()
        table=TABLE.make_table(W,C,np.ascontiguousarray(base[:,use]))
        F={"funded_50":F50,"funded_150":F150}[home]
        parameters=ENGINE.rules(F,"50K_funded" if home=="funded_50" else "150K_funded")
        assert parameters[0]==(50000 if home=="funded_50" else 150000)
        parity+=ENGINE.parity_check(W,C,table,hist[:2],F,parameters,home)
        low=corrected_minima(W,positions,ranges,eligible,table["Q"],table["counts"],table["low"],active)
        assert np.all(low>=table["low"]-1e-8)
        # Independent NumPy arithmetic at fixed production days/states.
        checked=0
        for d in np.flatnonzero(active)[::max(1,int(active.sum()/12))]:
            for s in [0,int(table["counts"][d])-1]:
                q=table["Q"][d,s]
                marks=np.sum(q[:,None]*W[:,d,:],axis=0)
                p=q[:,None]*positions[:,d,:]
                credit=np.minimum(np.maximum(p,0).sum(0),np.maximum(-p,0).sum(0))*ranges[d]*2
                expected=min(0.,float((marks+np.where(eligible[d],credit,0.)).min()))
                assert np.isclose(expected,low[d,s],rtol=0,atol=1e-7)
                checked+=1
        corrected={**table,"low":low};results={}
        for label,t in [("reference",table),("integer_shared_price",corrected)]:
            r=ENGINE.run_table(t,hist,500,parameters);y1=ENGINE.run_table(t,hist,250,parameters)[:,0]
            ladder=np.r_[0,np.cumsum(parameters[5])]
            assert np.array_equal(r[:,0],ladder[r[:,1].astype(int)])
            results[label]=(r,y1)
            pd.DataFrame(np.c_[r,y1],columns=["paid","payouts","days","blown","first","y1"]).to_csv(OUT/f"{home}_{label}_histories.csv",index=False)
            rows.append(dict(home=home,model=label,n=500,y1=y1.mean(),y2=r[:,0].mean(),failure=r[:,3].mean(),
                all_six=(r[:,1]==6).mean(),median_sixth=np.median(np.where(r[:,1]==6,r[:,2],np.inf))))
        r0,y0=results["reference"];r1,y1=results["integer_shared_price"]
        changed=np.any(r0!=r1,axis=1)|(y0!=y1)
        changes.append(dict(home=home,histories_changed=int(changed.sum()),failures_changed=int((r0[:,3]!=r1[:,3]).sum()),
            y1_changed=int((y0!=y1).sum()),y2_changed=int((r0[:,0]!=r1[:,0]).sum()),
            eligible_opposing_position_days=int(active.sum()),
            reachable_daily_states_with_changed_minimum=int((np.abs(low-table["low"])>1e-7).sum())))
        verified.append(dict(home=home,numpy_minima_checks=checked,close_table_unchanged=True,
                             exact_integer_qty_correction=True,payout_ladder_verified=True,source_plan=plan))
        pd.DataFrame(rows).to_csv(OUT/"summary.csv",index=False);A.dump(OUT/"changes.json",changes)
        print(home,changes[-1],flush=True)
        del units,W,C,positions,table,corrected,low;gc.collect()
    A.dump(OUT/"verification.json",dict(all_passed=True,canonical_parity=parity,corrected_minima=verified,
        unit_cache_hashes=inputs,source_commit="88b5e95f5d10f468a0865c693b302fb48cdb956b",
        script_sha256=A.sha(Path(__file__)),histories="Exact prior-audit500x500 saved history dates per account",
        limits=["OHLC sparse-price model, not tick/broker execution","no overlap credit in entry/exit or missing bars",
                "no change to closed cash or strategies","fixed common history already inspected, not new holdout"] ))


if __name__=="__main__":
    mechanics()
    if not MECHANICS_ONLY:run()
