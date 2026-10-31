"""Frozen no-fit pre-NFP ES adaptation. Inventory has no return calculations.

The shared grid.execute engine supplies entry-bar stops, gap handling and time
exits. A shifted session view permits one CME session to cross calendar midnight.
No original cache or live files are read or modified.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
from types import SimpleNamespace
import numpy as np
import pandas as pd
from grid24 import Grid24
from grid import execute
import metrics as M

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'agents/codex/inputs/scout_preannouncement_20261029'
OUT = ROOT / 'analysis/outputs/codex_scout_pre_nfp_20261029'
START = 1020  # 17:00 CT in raw calendar-day columns
ENTRY = 6     # open of minute labelled17:06 =17:05 wall clock
EXIT = 865    # completed minute labelled07:25,5min before scheduled news
SEED = 3387172

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

def roll(date):
    return date.month in (3,6,9,12) and 8 <= date.day <= 17

def schedules():
    receipts = json.loads((INPUT/'prospective_schedules.json').read_text())
    out = []
    for row in receipts:
        text = ' '.join(re.sub(r'^L\d+:\s*','',x) for x in row['source_lines'])
        m = re.search(r'scheduled to be released(?: on)?\s+\w+,?\s+(\w+\s+\d{1,2},?\s+\d{4})',text,re.I)
        if not m: raise ValueError('Missing prospective date '+row['event_date'])
        parsed = pd.Timestamp(m.group(1)).date().isoformat()
        if parsed != row['event_date'] or not re.search(r'8:30\s*a\.m\.',text):
            raise ValueError('Prospective date/clock mismatch '+row['event_date'])
        if pd.Timestamp(row['available_by']) >= pd.Timestamp(parsed)-pd.Timedelta(days=1):
            raise ValueError('Schedule not known before entry')
        out.append(dict(date=parsed, available_by=row['available_by'],url=row['url']))
    if len(out)!=60 or len({x['date'] for x in out})!=60: raise ValueError('Expected60unique releases')
    return out

def coverage():
    parts = [pd.read_csv(ROOT/f'data/ES_1min_{y}.csv',usecols=['date','time']) for y in range(2017,2023)]
    raw = pd.concat(parts).drop_duplicates(['date','time'])
    byday = {int(day): set((g.time//100*60+g.time%100).astype(int)) for day,g in raw.groupby('date')}
    events = {x['date'] for x in schedules()}
    rows=[]
    for day in pd.date_range('2018-01-01','2022-12-31'):
        if day.dayofweek>=5: continue
        prev=day-pd.Timedelta(days=1)
        a=byday.get(int(prev.strftime('%Y%m%d')),set());b=byday.get(int(day.strftime('%Y%m%d')),set())
        present={j-START for j in a if j>=START}|{420+j for j in b}
        window=np.array([j in present for j in range(ENTRY,EXIT+1)])
        missing=np.flatnonzero(~window)
        longest=0;streak=0
        for yes in window:
            streak=0 if yes else streak+1;longest=max(longest,streak)
        eligible=ENTRY in present and EXIT in present and window.mean()>=.99 and longest<=5 and not roll(day)
        rows.append(dict(date=day.date().isoformat(),nfp=day.date().isoformat() in events,
                         eligible=bool(eligible),coverage=float(window.mean()),max_missing_run=int(longest),
                         entry_present=ENTRY in present,exit_present=EXIT in present,roll_excluded=roll(day)))
    return pd.DataFrame(rows)

def inventory():
    OUT.mkdir(parents=True,exist_ok=True)
    cal=coverage();cal.to_csv(OUT/'coverage.csv',index=False)
    artifact=INPUT/'local/source_rendering.txt'
    lines=artifact.read_text().splitlines()
    ids={int(m.group(1)) for line in lines if (m:=re.match(r'L(\d+)(?:@P[^:]+)?:',line))}
    if ids!=set(range(2286)):raise ValueError('Incomplete primary-source text rendering')
    inputs=[]
    for path in [INPUT/'prospective_schedules.json']+[ROOT/f'data/ES_1min_{y}.csv' for y in range(2017,2023)]:
        inputs.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),permission='permitted_access',
                           provenance='User-owned MultiCharts ES export' if path.suffix=='.csv' else 'BLS archived previous-month notices captured with connected primary-source reader'))
    result=dict(return_tests_executed=False,source_sha256=sha(artifact),source_lines=len(ids),
                schedules_verified=len(schedules()),eligible_events=int((cal.nfp&cal.eligible).sum()),
                events=int(cal.nfp.sum()),inputs=inputs,planned_sd_es_usd=500,
                t2_net_hurdle_usd=1000/math.sqrt(max(1,(cal.nfp&cal.eligible).sum())))
    (OUT/'inventory.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='inputs'},indent=2))

def session_grid(g,dates):
    index={pd.Timestamp(t).normalize():i for i,t in enumerate(g.ts)}
    kwargs={}
    for field in ('o','h','l','c'):
        raw=getattr(g,field); rows=[]
        for date in dates:
            d=pd.Timestamp(date);a=index[d-pd.Timedelta(days=1)];b=index[d]
            rows.append(np.r_[raw[a,START:],raw[b,:960]])
        kwargs[field]=np.asarray(rows)
    kwargs['ts']=pd.to_datetime(dates).to_numpy();kwargs['last_j']=np.full(len(dates),1379)
    return SimpleNamespace(**kwargs)

def trades(g,dates,atr_by_date):
    dates=list(dates)
    if not dates:return pd.DataFrame()
    s=session_grid(g,dates)
    stops=np.array([atr_by_date[pd.Timestamp(d)-pd.Timedelta(days=1)] for d in dates])
    # ATR known at the previous calendar date's start; deliberately no current-day high/low.
    if not np.isfinite(stops).all() or (stops<=0).any():raise ValueError('Unresolved past-only stop ATR')
    sig=pd.DataFrame(dict(day=np.arange(len(dates)),dj=ENTRY-1,side=1,stop=stops,target=np.inf,exit_j=EXIT))
    t=execute(s,sig,max_trades=1,name='ES_pre_NFP_reopen')
    if len(t)!=len(dates):raise ValueError('Missing engine execution')
    t['gross_es']=t.pnl*2.5;t['commission_es']=5.;t['slippage_es']=25.
    t['net_es']=t.gross_es-30.;t['gross_mes']=t.gross_es*.1
    t['net_mes']=t.gross_mes-1.24-2.50;t['stress_mes']=t.gross_mes-1.24-5.
    t['mae_mes']=t.mae*.25
    return t

def stats(t,days,col):
    x=t[col].to_numpy();daily=pd.Series(x,index=pd.to_datetime(t.date)).groupby(level=0).sum().reindex(days,fill_value=0.)
    row=M.perf(daily,x);row.update(t=float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))) if len(x)>1 and x.std()>0 else None,total=float(x.sum()))
    return row,daily

def design():
    inv=json.loads((OUT/'inventory.json').read_text());cal=pd.read_csv(OUT/'coverage.csv',parse_dates=['date'])
    for item in inv['inputs']:
        if sha(ROOT/item['path'])!=item['sha256']:raise ValueError('Changed input')
    if inv['eligible_events']<40 or inv['eligible_events']/inv['events']<.90:
        raise ValueError('Design data/power gate failed; no returns computed')
    # Two disjoint groups select exactly the six hashed files, even in a full checkout.
    # The engine's trading array is unused; the observed weekday calendar is built below.
    g=Grid24(str(ROOT/'data/ES_1min_201[789].csv'),night_pattern=str(ROOT/'data/ES_1min_202[012].csv'))
    if pd.Timestamp(g.ts[-1])>=pd.Timestamp('2023-01-01'):raise ValueError('Design attempted to open recent outcomes')
    atr=g.daily_atr(15);atr_by_date=dict(zip(pd.to_datetime(g.ts),atr))
    eligible=cal[cal.eligible].copy();event=eligible[eligible.nfp].date
    primary=trades(g,event,atr_by_date);primary.to_csv(OUT/'design_trades.csv',index=False)
    clock=pd.DatetimeIndex(g.ts)
    days=clock[(~np.isnan(g.c).all(axis=1))&(clock.dayofweek<5)&(clock.year>=2018)]
    metric,daily=stats(primary,days,'net_mes')
    if not np.isclose(daily.sum(),primary.net_mes.sum(),atol=.000001):raise ValueError('Trade/daily reconciliation failed')
    daily.rename('net_mes').to_csv(OUT/'design_daily.csv')
    years=[]
    for y in range(2018,2023):
        tt=primary[pd.to_datetime(primary.date).dt.year==y];m,_=stats(tt,days[days.year==y],'net_mes');m['year']=y;years.append(m)
    pd.DataFrame(years).to_csv(OUT/'design_years.csv',index=False)
    pool=eligible[~eligible.nfp];control=trades(g,pool.date,atr_by_date).set_index('date')
    rng=np.random.default_rng(SEED);means=[]
    for _ in range(1000):
        sample=[]
        for d in event:
            candidates=pool[(pool.date.dt.year==d.year)&(pool.date.dt.month==d.month)&(pool.date.dt.dayofweek==d.dayofweek)].date
            if candidates.empty:raise ValueError('No matched-month/weekday control')
            sample.append(pd.Timestamp(candidates.iloc[rng.integers(len(candidates))]))
        means.append(float(control.loc[sample,'net_mes'].mean()))
    pd.DataFrame({'mean_net_mes':means}).to_csv(OUT/'design_controls.csv',index=False)
    rng=np.random.default_rng(SEED+1);boot=[]
    for _ in range(2000):
        ys=rng.choice(np.arange(2018,2023),5,replace=True)
        vals=np.concatenate([primary.loc[pd.to_datetime(primary.date).dt.year==y,'net_mes'].to_numpy() for y in ys])
        boot.append(float(vals.mean()))
    ci=np.percentile(boot,[5,95]);p=(1+sum(x>=metric['avg'] for x in means))/1001
    gates=dict(min_40_trades=len(primary)>=40,positive_native_net=metric['avg']>0,t_at_least_2=metric['t']>=2,
               four_positive_years=sum(x['total']>0 for x in years)>=4,year_bootstrap_low_positive=ci[0]>0,
               matched_placebo_p_le_05=p<=.05,two_tick_each_fill_stress_positive=primary.stress_mes.mean()>0)
    gross,_=stats(primary,days,'gross_es');netes,_=stats(primary,days,'net_es')
    result=dict(phase='design',period='2018-2022',native_size='1 MES',metrics_mes=metric,metrics_es=netes,
                gross_es=gross,placebo_p=p,placebo_average_net_mes=float(np.mean(means)),mean_net_mes_ci90=ci.tolist(),
                stress_mean_mes=float(primary.stress_mes.mean()),gates=gates,passed=bool(all(gates.values())),
                long_only=True,shorts='No short rule registered or run',recent_tested=False,accounts_tested=False)
    (OUT/'design_gate.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps(result,indent=2,allow_nan=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['inventory','design']);a=p.parse_args()
    inventory() if a.phase=='inventory' else design()
