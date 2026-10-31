"""Reconcile saved PrimeSync positions/fills and add preregistered recent intervals."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
from codex_primesync import OUT,describe,dump
import resampling as R


def main():
    choice=json.loads((OUT/'selection.json').read_text());mode=choice['chosen_exit']
    checks=[];rows=[];recent_daily=pd.read_csv(OUT/'recent_daily.csv',index_col='date',parse_dates=True)
    for path in sorted(OUT.glob('*_exit*_trades.csv')):
        t=pd.read_csv(path,parse_dates=['date']);pv=2 if '_NQ_' in path.name else 5
        assert not t.unresolved.any()
        np.testing.assert_allclose(t.gross-t.commission-t.slippage,t.net,atol=1e-8)
        assert (t.qty%3==0).all() and ((t.risk*pv+5)*t.qty<=500+1e-8).all()
        fills=pd.read_csv(Path(str(path).replace('_trades.csv','_fills.csv')))
        sums=fills.groupby('trade').quantity.sum().reindex(range(len(t)))
        np.testing.assert_array_equal(sums,t.qty)
        checks.append(dict(file=path.name,positions=len(t),reconciled=True))
    recent_metrics=[];all_metrics=[];all_years=[]
    for context in ('NQ_15','NQ_30','ES_15','ES_30'):
        name=f'{context}_exit{mode}'
        design=pd.read_csv(OUT/f'design_{name}_trades.csv',parse_dates=['date'])
        recent=pd.read_csv(OUT/f'recent_{name}_trades.csv',parse_dates=['date'])
        both=pd.concat([design,recent],ignore_index=True)
        days=pd.bdate_range('2018-01-02','2026-10-09')
        for side,part in [('whole',both),('long',both[both.side>0]),('short',both[both.side<0])]:
            m,_=describe(part,days);all_metrics.append(dict(context=context,side=side,**m))
        for year,part in both.groupby(both.date.dt.year):
            m,_=describe(part,days[days.year==year]);all_years.append(dict(context=context,year=year,**m))
        for side,part in [('whole',recent),('long',recent[recent.side>0]),('short',recent[recent.side<0])]:
            days=recent_daily.index
            _,daily=describe(part,days)
            b=R.bootstrap(daily,n=1000,block=20,seed=2702,chunk=100)
            for metric,r in b.iterrows():rows.append(dict(context=context,side=side,metric=metric,**r.to_dict()))
            recent_metrics.append(dict(context=context,side=side,p_sharpe_le_zero=b.attrs['p_sharpe_le_0']))
    pooled=recent_daily.mean(axis=1)
    b=R.bootstrap(pooled,n=1000,block=20,seed=2702,chunk=100)
    for metric,r in b.iterrows():rows.append(dict(context='equal_context_score',side='whole',metric=metric,**r.to_dict()))
    recent_metrics.append(dict(context='equal_context_score',side='whole',p_sharpe_le_zero=b.attrs['p_sharpe_le_0']))
    pd.DataFrame(rows).to_csv(OUT/'recent_bootstrap.csv',index=False)
    pd.DataFrame(all_metrics).to_csv(OUT/'selected_full_metrics.csv',index=False)
    pd.DataFrame(all_years).to_csv(OUT/'selected_full_by_year.csv',index=False)
    dump(OUT/'reconciliation.json',dict(checks=checks,all_passed=True,bootstrap=recent_metrics,
        bootstrap_runs=1000,block=20,seed=2702,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
    print('Reconciled',len(checks),'position/fill ledgers; recent bootstrap completed.')


if __name__=='__main__':main()
