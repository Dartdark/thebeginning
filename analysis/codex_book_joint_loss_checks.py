"""Independent arithmetic and interval checks of the saved descriptive audit."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

P=Path(__file__).resolve().parents[1]/'analysis/outputs/codex_book_joint_losses'
t=pd.read_csv(P/'trades.csv',parse_dates=['date','entry_ts','exit_ts'])
d=pd.read_csv(P/'daily.csv',index_col='date',parse_dates=True)
keys=['ONB30','MON_BR','TWIN','DT','JF','NBL','LDF']
target=t.kind.astype(str).isin(['1','target','tgt'])
commission=.725*t.qty
slip=.5*t.qty*(1+(~target).astype(int))
slip[t.strategy=='NBL']=0
extra=np.where(t.strategy=='JF',.55*t.qty,0)
net=(t.exit-t.entry)*t.side*2*t.qty-commission-slip-extra
assert np.allclose(net,t.net,atol=1e-7)
independent=t.groupby(['date','strategy']).net.sum().unstack().reindex(index=d.index,columns=keys).fillna(0)
assert np.allclose(independent,d[keys])
tails=pd.read_csv(P/'tails.csv')
recent=d[d.index.year>=2023]
ix=recent.BOOK.nsmallest(int(np.ceil(len(recent)*.05))).index
assert np.allclose(recent.loc[ix,keys].mean(),tails[(tails.period=='2023+')&(tails.fraction==.05)].set_index('strategy').reindex(keys).mean_contribution)

# Independent interval intersection, rather than reconstructing dense positions.
overlap=pd.read_csv(P/'overlap.csv');results=[]
a=t[(t.strategy=='ONB30')&(t.date.dt.year>=2023)].sort_values('entry_ts')
for k in ['TWIN','DT','NBL']:
    b=t[t.strategy==k].sort_values('entry_ts')
    both=same=opposed=0
    for x in a.itertuples():
        for y in b[(b.entry_ts<=x.exit_ts)&(b.exit_ts>=x.entry_ts)].itertuples():
            minutes=int((min(x.exit_ts,y.exit_ts)-max(x.entry_ts,y.entry_ts)).total_seconds()/60)+1
            both+=minutes
            if x.side==y.side:same+=minutes
            else:opposed+=minutes
    r=overlap[(overlap.period=='2023+')&(overlap.a=='ONB30')&(overlap.b==k)].iloc[0]
    assert (both,same,opposed)==(r.both_minutes,r.same_side_minutes,r.opposite_minutes)
    results.append(dict(a='ONB30',b=k,both=both,same=same,opposed=opposed))

cross=pd.read_csv(P/'dll_crossings.csv',parse_dates=['date'])
for x in cross.itertuples():
    at=x.date+pd.Timedelta(minutes=x.minute)
    for k in keys:
        active=t[(t.strategy==k)&(t.entry_ts<=at)&(t.exit_ts>=at)]
        assert np.isclose((active.qty*active.side).sum(),getattr(x,k+'_pos'))
assert (cross.book<=-2000).all()
result=dict(cost_reconciliation=True,daily_reconciliation=True,tail_reconciliation=True,
            independently_counted_intersections=results,crossing_position_reconciliation=True,
            crossing_rows_checked=len(cross))
(P/'validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
