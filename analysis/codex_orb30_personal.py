"""Frozen one-MNQ portfolio addition/ONB-replacement diagnostics; no caches rebuilt."""
from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scratch_data/codex_deps'),str(ROOT/'analysis')]
import numpy as np
import pandas as pd
import codex_anson_personal as P
import codex_orb30_ema as E
import resampling as R
OUT=E.OUT/'personal19'
PLAN='agents/codex/plans/orb30_ema_personal.md'
REF='7f0800ffc04d56bd878750369a4abc2316ee01d8'
FILES=['personal_strategies/PORTFOLIO.md','analysis/personal_portfolio.py','analysis/personal_variants.py','analysis/outputs/personal_portfolio_output.txt','analysis/outputs/personal_variants_output.txt']

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    assert git('show','HEAD:'+PLAN).replace('\r\n','\n')==(ROOT/PLAN).read_text().strip().replace('\r\n','\n')
    blobs={}
    for p in FILES:
        a=git('rev-parse','afde088:'+p);b=git('rev-parse',REF+':'+p);assert a==b
        blobs[p]=b
    rows=[];effects=[];joint=[];binding={}
    for fee in [1.24,1.04]:
        p=ROOT/f'analysis/outputs/codex_rebound/personal19/UNIFORM/fee_{fee:.2f}/baseline_daily19.csv'
        binding[str(p.relative_to(ROOT))]=E.sha(p)
        frame=pd.read_csv(p,index_col=0,parse_dates=True)
        frame=frame[(frame.index>='2018-01-01')&(frame.index<='2026-10-09')]
        assert frame.shape[1]==19 and frame.index.is_unique
        frame.to_csv(OUT/f'baseline_fee_{fee:.2f}.csv')
        for model in ['FULL185','SELECTED4','SELECTED0']:
            t=pd.read_csv(E.OUT/(model+'_trades.csv'),parse_dates=['date'])
            missing=pd.DatetimeIndex(t.date).difference(frame.index)
            if len(missing):raise ValueError('Candidate dates absent in book: '+str(list(missing)))
            col='mnq_net' if fee==1.24 else 'mnq_net_lowfee'
            candidate=E.daily(t,frame.index,col)
            candidate.to_csv(OUT/(model+f'_candidate_fee_{fee:.2f}.csv'))
            sets={**P.STARTERS,'FULL':list(frame.columns)}
            for cohort,start in [('2018_plus','2018-01-01'),('2023_plus','2023-01-01')]:
                mask=frame.index>=start;dates=frame.index[mask]
                idx=P.histories(int(mask.sum()),n=1000,horizon=252,block=10,seed=E.SEED)
                c=candidate[mask]
                for group,keys in sets.items():
                    base=frame.loc[mask,keys].sum(axis=1)
                    empty=base-frame.loc[mask,'OvernightBiasML']
                    cases={'BASE':base,'ADD1':base+c,'EMPTY_ONB':empty,'REPLACE_ONB':empty+c}
                    results={}
                    for case,d in cases.items():
                        profit,dd=P.simulate_daily(d.to_numpy(),idx);results[case]=(profit,dd)
                        rows.append(dict(model=model,fee=fee,cohort=cohort,group=group,case=case,n_days=len(d),last_date=str(d.index[-1].date()),historical_annual=float(d.mean()*252),historical_dd=R.max_dd(d),mean_profit=float(profit.mean()),median_profit=float(np.median(profit)),dd95=float(np.quantile(dd,.95)),p_loss=float((profit<=0).mean()),profit_over_dd95=float(np.median(profit)/np.quantile(dd,.95))))
                    for case in ['ADD1','REPLACE_ONB']:
                        diff=cases[case]-base;ci=P.historical_annual_effect_interval(diff.to_numpy(),seed=E.SEED,n=5000,block=10)
                        effects.append(dict(model=model,fee=fee,cohort=cohort,group=group,case=case,annual_delta=float(results[case][0].mean()-results['BASE'][0].mean()),dd95_delta=float(np.quantile(results[case][1],.95)-np.quantile(results['BASE'][1],.95)),annual_ci05=float(ci[0]),annual_ci95=float(ci[1])))
                    joint.append(dict(model=model,fee=fee,cohort=cohort,group=group,correlation=float(c.corr(base)),candidate_on_book_loss_days=float(c[base<0].sum()),candidate_mean_on_book_loss_days=float(c[base<0].mean()),book_loss_days=int((base<0).sum())))
    pd.DataFrame(rows).to_csv(OUT/'summary.csv',index=False)
    pd.DataFrame(effects).to_csv(OUT/'paired_effects.csv',index=False)
    pd.DataFrame(joint).to_csv(OUT/'joint_losses.csv',index=False)
    (OUT/'manifest.json').write_text(json.dumps(dict(plan_commit=git('log','-1','--format=%H','--',PLAN),current_reference=REF,unchanged_since='afde088',source_blobs=blobs,input_sha256=binding,script_sha256=E.sha(__file__),seed=E.SEED,histories=1000,block_days=10,horizon=252,limitations=P.LIMITATIONS,full_apex_comparisons='LIMITED: joint baseline overnight paths not causal; no payout/pass estimates',native_platform_parity=False),indent=2)+'\n')
    print(pd.DataFrame(effects).query("fee==1.24 and cohort=='2023_plus' and group=='FULL'").to_string(index=False))
    print(pd.DataFrame(rows).query("fee==1.24 and cohort=='2023_plus' and group=='FULL'")[['model','case','mean_profit','dd95','profit_over_dd95']].to_string(index=False))

if __name__=='__main__':main()
