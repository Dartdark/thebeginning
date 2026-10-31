"""Timestamp-only source coverage audit; never reads 2023+ prices/returns."""
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_choch4h_20261028'

if __name__=='__main__':
    rows=[]
    for p in sorted((ROOT/'data').glob('NQ_1min_ON_*.csv')):
        x=pd.read_csv(p,usecols=['date','time'])
        x=x.drop_duplicates(['date','time'])
        dt=pd.to_datetime(x.date.astype(str))
        # Observed evening dates, excluding the normal Friday/Saturday closure.
        dates=sorted(x.loc[(x.time>=1701)&~dt.dt.dayofweek.isin([4,5]),'date'].unique())
        n=x.loc[x.time.between(1701,1800)].groupby('date').size().reindex(dates,fill_value=0)
        rows.append(dict(year=int(p.stem[-4:]),source=str(p.relative_to(ROOT)),
                         observed_evening_dates=len(dates),opening_hour_complete=int((n==60).sum()),
                         opening_hour_empty=int((n==0).sum()),opening_hour_partial=int(((n>0)&(n<60)).sum()),
                         price_columns_read=False))
    out=pd.DataFrame(rows)
    OUT.mkdir(parents=True,exist_ok=True)
    out.to_csv(OUT/'timestamp_coverage.csv',index=False)
    print(out.to_string(index=False))
