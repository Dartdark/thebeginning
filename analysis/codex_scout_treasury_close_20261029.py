"""Source-led Treasury index clock screen. inventory reads timestamps only; design requires admission."""
from pathlib import Path
from types import SimpleNamespace
import argparse, hashlib, json
import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar, GoodFriday
from grid24 import Grid24
from grid import execute
import metrics as M
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_scout_treasury_close_20261029'
INPUT=ROOT/'agents/codex/inputs/scout_treasury_close_20261029'
class BondCalendar(USFederalHolidayCalendar):
    rules=USFederalHolidayCalendar.rules+[GoodFriday]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def calendar():
    h=BondCalendar().holidays('2018-01-01','2022-12-31')
    days=pd.date_range('2018-01-01','2022-12-31',freq='B').difference(h).difference(pd.to_datetime(['2018-12-05']))
    seq=pd.Series(np.arange(len(days)),index=days)
    # Three final cash-bond business dates, without selecting on any return.
    last3=seq.groupby(days.to_period('M')).tail(3).index
    return days,last3
def inventory():
    OUT.mkdir(parents=True,exist_ok=True)
    parts=[pd.read_csv(ROOT/f'data/ZN_1min_{y}.csv',usecols=['date','time']) for y in range(2017,2023)]
    raw=pd.concat(parts).drop_duplicates(['date','time'])
    present={int(d):set((r.time//100*60+r.time%100).astype(int)) for d,r in raw.groupby('date')}
    days,last3=calendar();rows=[]
    for d in days:
        close=840 if d<pd.Timestamp('2021-01-14') else 900
        js=present.get(int(d.strftime('%Y%m%d')),set());window=[j in js for j in range(close-59,close+1)]
        missing=0;worst=0
        for yes in window:missing=0 if yes else missing+1;worst=max(worst,missing)
        rows.append(dict(date=d.date().isoformat(),event=d in last3,entry_j=close-59,exit_j=close,
                         coverage=float(np.mean(window)),max_missing_run=worst,
                         eligible=close-59 in js and close in js and np.mean(window)>=.98 and worst<=1))
    c=pd.DataFrame(rows);c.to_csv(OUT/'coverage.csv',index=False)
    paths=[ROOT/f'data/ZN_1min_{y}.csv' for y in range(2017,2023)]
    result=dict(return_tests_executed=False,events=int(c.event.sum()),eligible_events=int((c.event&c.eligible).sum()),
                inputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),permission='permitted_access',provenance='User-owned MultiCharts ZN minute export') for p in paths],
                source_sha256=sha(INPUT/'local/source.txt'))
    (OUT/'inventory.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
def stats(t,days,col):
    daily=t.groupby('date')[col].sum().reindex(days,fill_value=0.)
    x=t[col];m=M.perf(daily,x);m.update(total=float(x.sum()),t=float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))))
    return m,daily
def design():
    inv=json.loads((OUT/'inventory.json').read_text())
    if inv['eligible_events']<150 or inv['eligible_events']/inv['events']<.9:raise ValueError('Data gate failed; no returns')
    for i in inv['inputs']:
        if sha(ROOT/i['path'])!=i['sha256']:raise ValueError('Changed input')
    g=Grid24(str(ROOT/'data/ZN_1min_201[789].csv'),night_pattern=str(ROOT/'data/ZN_1min_202[012].csv'))
    if pd.Timestamp(g.ts[-1]).year>2022:raise ValueError('Recent data forbidden')
    c=pd.read_csv(OUT/'coverage.csv',parse_dates=['date']);c=c[c.eligible].copy()
    lookup={pd.Timestamp(d):i for i,d in enumerate(g.ts)};c['day']=c.date.map(lookup)
    atr=g.daily_atr(15)
    if not np.isfinite(atr[c.day]).all():raise ValueError('Unknown lagged ATR')
    sig=pd.DataFrame(dict(day=c.day,dj=c.entry_j-1,exit_j=c.exit_j,side=1,stop=np.ceil(atr[c.day]*64)/64,target=np.inf))
    # One calendar row / one intraday position. ZN stop rounded outward to its actual tick.
    t=execute(g,sig,max_trades=1,name='ZN_month_end_index_clock')
    if len(t)!=len(c):raise ValueError('Missing engine execution')
    t=t.merge(c[['date','event']],on='date',validate='one_to_one')
    t['gross_zn']=t.pnl*50;t['net_zn']=t.gross_zn-45.75;t['stress_zn']=t.gross_zn-77.
    primary=t[t.event].copy();control=t[~t.event].copy()
    primary.to_csv(OUT/'design_trades.csv',index=False)
    days,_=calendar();m,d=stats(primary,days,'net_zn');d.to_csv(OUT/'design_daily.csv',header=['net_zn'])
    assert np.isclose(d.sum(),primary.net_zn.sum())
    years=[]
    for year in range(2018,2023):
        mm,_=stats(primary[primary.date.dt.year==year],days[days.year==year],'net_zn');mm['year']=year;years.append(mm)
    pd.DataFrame(years).to_csv(OUT/'design_years.csv',index=False)
    rng=np.random.default_rng(3440417);means=[]
    for _ in range(1000):
        selected=[]
        for dt in primary.date:
            pool=control[(control.date.dt.year==dt.year)&(control.date.dt.month==dt.month)&(control.date.dt.dayofweek==dt.dayofweek)]
            if pool.empty:raise ValueError('Missing matched placebo pool')
            selected.append(float(pool.net_zn.iloc[rng.integers(len(pool))]))
        means.append(float(np.mean(selected)))
    pd.DataFrame(dict(mean_net_zn=means)).to_csv(OUT/'design_controls.csv',index=False)
    rng=np.random.default_rng(3440418);boot=[]
    for _ in range(2000):
        ys=rng.choice(np.arange(2018,2023),5,replace=True)
        boot.append(float(np.concatenate([primary.loc[primary.date.dt.year==y,'net_zn'].to_numpy() for y in ys]).mean()))
    ci=np.percentile(boot,[5,95]);p=float((1+sum(x>=m['avg'] for x in means))/1001)
    gates={k:bool(v) for k,v in dict(positive_net=m['avg']>0,t_at_least_2_5=m['t']>=2.5,
        four_positive_years=sum(x['total']>0 for x in years)>=4,bootstrap_lower_positive=ci[0]>0,
        matched_placebo_p_le_05=p<=.05,stress_positive=primary.stress_zn.mean()>0).items()}
    gross,_=stats(primary,days,'gross_zn')
    out=dict(period='2018-2022',size='1 ZN',metrics=m,gross=gross,mean_ci90=ci.tolist(),placebo_p=p,
             placebo_mean=float(np.mean(means)),stress_mean=float(primary.stress_zn.mean()),gates=gates,
             passed=all(gates.values()),recent_tested=False,accounts_tested=False,shorts='not registered')
    (OUT/'design_gate.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps(out,indent=2,allow_nan=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['inventory','design']);a=p.parse_args()
    inventory() if a.phase=='inventory' else design()
