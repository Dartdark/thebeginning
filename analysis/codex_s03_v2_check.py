"""Reconcile S03v2 with alternate arithmetic, without new variants or draws.

This is a self-audit, not independent-agent/platform certification. Direct
14-day sums, saved path arrays and source-event exit parity check new code.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"agents/codex/runtime/or_pullback_python"),str(ROOT/"analysis")]
import json
import pickle
import numpy as np
import pandas as pd
import codex_s03_v2_replay as S
import codex_s03_v2_diagnostics as D
BASE=ROOT/"analysis/outputs/codex_s03_v2"


def near(a,b):np.testing.assert_allclose(a,b,rtol=0,atol=3e-7,equal_nan=True)


def main():
    S.authorize()
    with open(ROOT/"scratch_data/g24.pkl","rb") as f:g=pickle.load(f)
    with open(ROOT/"agents/codex/runtime/s03_v2_features.pkl","rb") as f:p=pickle.load(f)
    with open(ROOT/"agents/codex/runtime/anson_personal_baseline.pkl","rb") as f:frame=pickle.load(f)
    accepted=np.flatnonzero(p["feature_audit"][:,2]);checked=set();nfeatures=ntrades=0
    for m in S.MODELS:
        t=pd.read_csv(S.OUT/f"{m}_trades.csv")
        assert not t.cross_date.any() and (t.entry_flat>t.signal_flat).all()
        assert ((t.exit_flat.iloc[:-1].to_numpy()<t.entry_flat.iloc[1:].to_numpy())|
                ((t.exit_flat.iloc[:-1].to_numpy()==t.entry_flat.iloc[1:].to_numpy())&
                 (t.exit_phase.iloc[:-1].to_numpy()=="open"))).all()
        for x in t.itertuples():
            d,j=divmod(x.signal_flat,1440);k=(j-540)//30
            if (d,j)not in checked:
                prior=accepted[accepted<d][-14:];assert len(prior)==14
                values=[]
                for row in prior:
                    a=int(p["feature_audit"][row,0]);assert a>=511
                    values.append(abs(g.c[row,j]/g.o[row,a]-1) if p["observed"][row,j] else 0.)
                mean=np.mean(values);near(mean,p["f"][d,k,3]);near(mean,x.signal_mu)
                a=int(p["feature_audit"][d,0]);op=g.o[d,a];pc=g.c[prior[-1],900]
                near([max(op,pc)*(1+mean),min(op,pc)*(1-mean)],p["f"][d,k,:2])
                seen=p["observed"][d,a:j+1]
                tp=(g.h[d,a:j+1]+g.l[d,a:j+1]+g.c[d,a:j+1])/3
                vol=g.v[d,a:j+1];vw=np.sum(tp[seen]*vol[seen])/np.sum(vol[seen])
                near(vw,p["f"][d,k,2]);checked.add((d,j));nfeatures+=1
            near((x.exit-x.entry)*x.side,x.gross_points)
            if m.startswith("v2"):
                wanted=x.entry-x.side*x.stop_distance
                rounded=np.floor(wanted*4+1e-9)/4 if x.side>0 else np.ceil(wanted*4-1e-9)/4
                near(x.stop_px,rounded)
            if x.kind==0:
                near(x.exit_minute_adverse_px,x.exit)
                if x.exit_phase!="open":near(x.exit,x.stop_px)
            ntrades+=1
    personal=[]
    for m in("v2_raw","v1_raw"):
        t=pd.read_csv(S.OUT/f"{m}_trades.csv",parse_dates=["date"])
        out=BASE/"personal"/m
        daily=pd.read_csv(out/"candidate_daily.csv",index_col=0,parse_dates=True).iloc[:,0]
        net=(2*t.gross_points-2.275).groupby(t.date).sum().reindex(frame.index,fill_value=0.)
        near(daily,net)
        plans=pd.read_csv(out/"daily_portfolios.csv",index_col=0,parse_dates=True)
        near(plans.FULL__BASE,frame.sum(axis=1));near(plans.FULL__ADD_1,frame.sum(axis=1)+daily)
        summary=pd.read_csv(out/"mc_summary.csv");counts=0
        for cohort,lo in(("2018_plus","2018-01-01"),("2025_plus_replication","2025-01-01")):
            ix=np.load(out/f"paired_histories_{cohort}.npy");arrays=np.load(out/f"paired_mc_{cohort}.npz")
            for r in summary[summary.cohort==cohort].itertuples():
                vals=plans.loc[plans.index>=lo,r.config].to_numpy()[ix];cum=vals.cumsum(axis=1)
                dd=(np.maximum.accumulate(np.c_[np.zeros(len(ix)),cum],axis=1)[:,1:]-cum).max(axis=1)
                near(arrays[r.config+"__profit"],cum[:,-1]);near(arrays[r.config+"__dd"],dd)
                near([r.profit_p50,r.dd_p95,r.capital_20pct],[np.median(cum[:,-1]),np.quantile(dd,.95),np.quantile(dd,.95)/.2]);counts+=1
        personal.append(dict(model=m,daily_reconciles=True,summary_rows=counts))
    acct=BASE/"accounts";aud=pd.read_csv(acct/"common_day_audit.csv",parse_dates=["date"])
    eligible=aud.common_account_eligible.to_numpy();dates=pd.DatetimeIndex(aud.date)
    assert np.array_equal(eligible,aud.v2_apex__account_eligible&aud.v1_apex__account_eligible)
    funded=pd.read_csv(acct/"funded_summary.csv");archives={}
    for r in funded.itertuples():
        key=(r.fee,r.context,r.cohort)
        if key not in archives:archives[key]=np.load(acct/f"funded_results_{r.fee:.2f}_{r.context}_{r.cohort}.npz")
        a,b=archives[key][r.config+"__250"],archives[key][r.config+"__500"]
        near([r.year1,r.year2,r.blown,r.all6,r.days6],[a[:,0].mean(),b[:,0].mean(),b[:,3].mean(),(b[:,1]==6).mean(),np.median(np.where(b[:,1]==6,b[:,2],np.inf))])
    evaluation=pd.read_csv(acct/"evaluation_summary.csv");windows={}
    complete=np.array([i+21<=len(eligible)and eligible[i:i+21].all() for i in range(len(eligible))])
    for r in evaluation.itertuples():
        key=(r.fee,r.context)
        if key not in windows:windows[key]=pd.read_csv(acct/f"evaluation_starts_{r.fee:.2f}_{r.context}.csv",parse_dates=["date","window_last_date"])
        v=windows[key];near(v.common_complete_21day_start.to_numpy(),complete)
        lo,hi=D.PERIODS[r.cohort];ok=complete&(v.date>=lo)&(v.window_last_date<pd.Timestamp(hi))
        o=v[r.config+"__outcome"]
        near([r.starts,r.passed,r.failed,r.timed_out],[ok.sum(),(o[ok]=="pass").mean(),(o[ok]=="fail").mean(),(o[ok]=="time").mean()])
    parity=0
    for fee in(1.04,1.24):
        rows=json.loads((acct/f"funded_parity_{fee:.2f}.json").read_text())
        for row in rows:assert row["exact"];near(row["original"],row["lookup"])
        parity+=len(rows)
    synthetic=json.loads((acct/"synthetic_parity.json").read_text())
    assert synthetic["exact_records"]==100
    stats=pd.read_csv(BASE/"diagnostics/standard_stats.csv")
    for r in stats.itertuples():
        t=pd.read_csv(S.OUT/f"{r.model}_trades.csv",parse_dates=["date"])
        if r.group!="both":t=t[t.side==(1 if r.group=="long" else -1)]
        periods={**D.PERIODS,**{str(y):(f"{y}-01-01",f"{y+1}-01-01") for y in range(2018,2027)}}
        lo,hi=periods[r.period];t=t[(t.date>=lo)&(t.date<hi)]
        x=t.gross_points*20-r.fee_micro*10-10
        near([r.trades,r.avg,r.t,r.total_nq],[len(x),x.mean(),D.D.tstat(x),x.sum()])
    result=dict(status="PASS self-audit",independent_review=False,independent_Claude_review="pending",
        direct_sigma_VWAP_checks=nfeatures,source_trades=ntrades,personal=personal,
        funded_rows=len(funded),evaluation_rows=len(evaluation),production_parity=parity,synthetic_parity=100,
        statistics_rows=len(stats),new_variants=0,new_history_draws=0,
        limits="Own maker checking alternate arithmetic and reused original simulators; not a blind checker or platform parity.")
    (BASE/"self_check.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
