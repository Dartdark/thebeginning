"""Independent saved-output reconciliation; no candidate replay or new draw."""
import sys, json
from pathlib import Path
sys.path.insert(0, 'agents/codex/runtime/or_pullback_python')
import numpy as np
import pandas as pd

ROOT=Path('analysis/outputs/codex_r2vault')
OUT=ROOT/'accounts'
PERIODS={'2018_plus':('2018-01-01','2100-01-01'), '2018_22':('2018-01-01','2023-01-01'),
         '2018_24':('2018-01-01','2025-01-01'), '2023_plus':('2023-01-01','2100-01-01'),
         '2025_plus':('2025-01-01','2100-01-01')}

def near(a,b): np.testing.assert_allclose(a,b,rtol=0,atol=1e-8,equal_nan=True)

def main():
    reproduction=json.loads((OUT/'reproduction.json').read_text())
    a=pd.read_csv(OUT/'common_day_audit.csv',parse_dates=['date'])
    eligible=a.common_account_eligible.to_numpy(bool)
    dates=pd.DatetimeIndex(a.date)
    assert np.array_equal(eligible,a.et_apex__account_eligible & a.ct_apex__account_eligible)
    expected_complete=np.array([s+21<=len(a) and eligible[s:s+21].all() for s in range(len(a))])
    funded=pd.read_csv(OUT/'funded_summary.csv')
    fp=pd.read_csv(OUT/'funded_paired_differences.csv')
    evaluation=pd.read_csv(OUT/'evaluation_summary.csv')
    ep=pd.read_csv(OUT/'evaluation_paired_differences.csv')
    assert len(funded)==180 and len(evaluation)==180
    assert len(fp)==1440 and len(ep)==1080
    cache={}
    for r in funded.itertuples():
        key=(r.fee,r.context,r.cohort)
        if key not in cache: cache[key]=np.load(OUT/f'funded_results_{r.fee:.2f}_{r.context}_{r.cohort}.npz')
        ar=cache[key]; x,y=ar[r.config+'__250'],ar[r.config+'__500']
        assert x.shape==y.shape==(1000,5)
        near([r.year1,r.year1_p5,r.year1_p95,r.year2,r.year2_p5,r.year2_p95,r.blown,r.all6,r.days6],
             [x[:,0].mean(),np.quantile(x[:,0],.05),np.quantile(x[:,0],.95),y[:,0].mean(),np.quantile(y[:,0],.05),np.quantile(y[:,0],.95),y[:,3].mean(),(y[:,1]==6).mean(),np.median(np.where(y[:,1]==6,y[:,2],np.inf))])
    for r in fp.itertuples():
        ar=cache[(r.fee,r.context,r.cohort)]
        h=250 if r.metric=='year1' else 500
        x,b=ar[r.config+f'__{h}'],ar[r.reference+f'__{h}']
        if r.metric.startswith('year'): delta=x[:,0]-b[:,0]
        elif r.metric=='blown': delta=x[:,3]-b[:,3]
        else: delta=(x[:,1]==6).astype(float)-(b[:,1]==6)
        near(r.delta,delta.mean()); assert r.lo<=r.hi
    for cohort,(lo,hi) in PERIODS.items():
        h=np.load(OUT/f'funded_histories_{cohort}.npy')
        assert h.shape==(1000,500) and eligible[h].all()
        assert ((dates[h.ravel()]>=lo)&(dates[h.ravel()]<hi)).all()
    starts={}
    for fee in [1.04,1.24]:
        for context in ['50K_evaluation','150K_evaluation']:
            df=pd.read_csv(OUT/f'evaluation_starts_{fee:.2f}_{context}.csv',parse_dates=['date','window_last_date'])
            assert np.array_equal(df.date,dates)
            assert np.array_equal(df.common_complete_21day_start,expected_complete)
            expected_last=pd.Series(pd.NaT,index=df.index,dtype='datetime64[ns]')
            expected_last.iloc[:len(df)-20]=dates[20:].to_numpy()
            # CSV parsing can chooseus while the constructed audit usesns;
            # compare timestamps/NaT after explicit precision normalisation.
            assert df.window_last_date.astype('datetime64[ns]').equals(expected_last)
            for cohort,(lo,hi) in PERIODS.items():
                mask=(df.date>=lo)&(df.date<hi)&(df.window_last_date<pd.Timestamp(hi))
                assert np.array_equal(mask,df[cohort+'__whole_window_inside'])
            starts[(fee,context)]=df
    for r in evaluation.itertuples():
        df=starts[(r.fee,r.context)]
        ok=expected_complete & df[r.cohort+'__whole_window_inside'].to_numpy(bool)
        o=df[r.config+'__outcome']; d=df[r.config+'__days']; base=df.BASE__outcome
        near([r.starts,r.passed,r.failed,r.timed_out,r.median_pass_days,r.changed_vs_base],
             [ok.sum(),(o[ok]=='pass').mean(),(o[ok]=='fail').mean(),(o[ok]=='time').mean(),d[ok&(o=='pass')].median(),(o[ok]!=base[ok]).mean()])
    for r in ep.itertuples():
        df=starts[(r.fee,r.context)]
        ok=expected_complete & df[r.cohort+'__whole_window_inside'].to_numpy(bool)
        label={'passed':'pass','failed':'fail','timed_out':'time'}[r.metric]
        delta=(df[r.config+'__outcome']==label).astype(float)-(df[r.reference+'__outcome']==label).astype(float)
        near(r.delta,delta[ok].mean()); assert r.lo<=r.hi
    prod=[]
    for fee in [1.04,1.24]:
        checks=json.loads((OUT/f'funded_parity_{fee:.2f}.json').read_text())
        assert len(checks)==180
        for r in checks:
            assert r['exact']; np.testing.assert_array_equal(r['original'],r['lookup'])
        prod.extend(checks)
    synth=json.loads((OUT/'synthetic_parity.json').read_text())
    assert synth['exact_records']==len(synth['records'])==100
    for r in synth['records']:
        assert r['exact']; np.testing.assert_array_equal(r['original'],r['lookup'])
    daily=0
    for mode in ['et_apex','ct_apex']:
        t=pd.read_csv(ROOT/'replay'/(mode+'_trades.csv'),parse_dates=['date'])
        t=t[t.date.isin(dates[eligible])]
        assert not t.cross_date.any() and not t.unknown_held_minutes.any()
        net=(2*t.gross_points-1.04-.5-np.where(t.kind==1,0.,.5)).groupby(t.date).sum().reindex(dates[eligible],fill_value=0.)
        for context in ['50K_funded','150K_funded']:
            df=pd.read_csv(OUT/f'daily_joint_pnl_{context}.csv',parse_dates=['date']).set_index('date')
            near(df[mode],net); daily+=1
    result=dict(status='PASS',funded_rows=len(funded),funded_paired_deltas=len(fp),evaluation_rows=len(evaluation),evaluation_paired_deltas=len(ep),production_five_output_parity_records=len(prod),synthetic_five_output_parity_records=len(synth['records']),eligible_days=int(eligible.sum()),excluded_days=int((~eligible).sum()),daily_fill_cost_reconciliations=daily,whole_21day_masks_checked=True,new_candidate_variants=0,new_history_draws=0,limits='Saved arithmetic and existing parity evidence; does not independently certify the author source, tick path, or live platform.')
    (OUT/'saved_output_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
