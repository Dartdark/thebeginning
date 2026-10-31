"""Extend repo resampling with an explicit initial-zero observation per path."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scratch_data/codex_deps'))
sys.path.insert(0,str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import resampling as R

def bootstrap(daily,n=5000,block=10,seed=20261025):
    # Use the repo's block sampler/statistics, without resampling the initial
    # bookkeeping zero as a market day or omitting it from individual paths.
    paths=R.fan_paths(daily,n=n,block=block,seed=seed)
    sampled={}
    for start in range(0,n,1000):
        part=paths[start:start+1000]
        increments=np.diff(np.c_[np.zeros(len(part)),part],axis=1)
        values=R._stats(np.c_[np.zeros(len(part)),increments],50_000.)
        for key,value in values.items():sampled.setdefault(key,[]).append(value)
    actual={k:v[0] for k,v in R._stats(np.r_[0.,np.asarray(daily)][None,:],50_000.).items()}
    assert np.isclose(actual['max_dd'],R.max_dd(daily))
    rows={k:dict(actual=actual[k],p5=np.nanpercentile(np.concatenate(v),5),
                 p50=np.nanpercentile(np.concatenate(v),50),p95=np.nanpercentile(np.concatenate(v),95)) for k,v in sampled.items()}
    return pd.DataFrame(rows).T

if __name__=='__main__':
    import codex_swing_target as H
    _,days,_=H.setup()
    rows=[]
    for model in ['CODE','CODE_BE']:
        t=pd.read_csv(H.OUT/(model+'_trades.csv'),parse_dates=['date','exit_date'])
        for period,ds in [('2023+',days[days.year>=2023]),('all',days)]:
            z=t[t.date.isin(ds)]
            for side in ['all','long','short']:
                a=z if side=='all' else z[z.side.eq(1 if side=='long' else -1)]
                for metric,r in bootstrap(H.daily(a,ds)).iterrows():
                    rows.append(dict(model=model,period=period,side=side,metric=metric,**r.to_dict()))
    pd.DataFrame(rows).to_csv(H.OUT/'bootstrap.csv',index=False)
    print('Initial-zero block bootstrap: all12 model/period/side cases reconciled.')
