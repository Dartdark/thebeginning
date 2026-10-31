"""User-authorized Nocturne adaptation, not a reproduction of withheld rules.
Inventory reads timestamps only; design requires a prior committed protocol.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse, hashlib, json
import numpy as np
import pandas as pd
from grid24 import Grid24
from grid import execute
import metrics as M
from resampling import max_dd
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_nocturne_20261030'
ENTRY,EXIT=6,860
FILES=[ROOT/'data/NQ_1min_ON_2017.csv']+[ROOT/f'data/NQ_1min_{prefix}{year}.csv' for year in range(2018,2023) for prefix in ('','ON_')]
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def roll(d):return d.month in (3,6,9,12) and 8<=d.day<=17
def refs(d):return [d-pd.offsets.BDay(2),d-pd.offsets.BDay(1)]
def present(byday,d):
    a=byday.get(int((d-pd.Timedelta(days=1)).strftime('%Y%m%d')),set())
    b=byday.get(int(d.strftime('%Y%m%d')),set())
    return {j-1020 for j in a if j>=1020}|{420+j for j in b if j<960}
def inventory():
    OUT.mkdir(parents=True,exist_ok=True)
    raw=pd.concat([pd.read_csv(p,usecols=['date','time']) for p in FILES]).drop_duplicates(['date','time'])
    byday={int(d):set((x.time//100*60+x.time%100).astype(int)) for d,x in raw.groupby('date')}
    sessions={d:present(byday,d) for d in pd.bdate_range('2017-12-01','2022-12-31')}
    rows=[]
    for d in pd.bdate_range('2018-01-01','2022-12-31'):
        js=sessions[d];w=[j in js for j in range(ENTRY,EXIT+1)];streak=worst=0
        for yes in w:streak=0 if yes else streak+1;worst=max(worst,streak)
        feature_counts=[sum(j in sessions[r] for j in range(5,1380,5)) for r in refs(d)]
        excluded=any(roll(x) for x in [d]+refs(d))
        night_ok=ENTRY in js and EXIT in js and np.mean(w)>=.98 and worst<=5
        feature_ok=min(feature_counts)>=248
        rows.append(dict(date=d.date().isoformat(),roll_excluded=excluded,night_ok=bool(night_ok),
                         coverage=float(np.mean(w)),max_gap=worst,feature_n1=feature_counts[0],feature_n2=feature_counts[1],
                         feature_ok=feature_ok,eligible=bool(not excluded and night_ok and feature_ok)))
    c=pd.DataFrame(rows);c.to_csv(OUT/'inventory_dates.csv',index=False)
    r=dict(return_tests_executed=False,nonroll_nights=int((~c.roll_excluded).sum()),
           night_coverage=int((~c.roll_excluded&c.night_ok).sum()),eligible_nights=int(c.eligible.sum()),
           inputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=digest(p)) for p in FILES])
    (OUT/'inventory.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
def shifted(g,dates):
    idx={pd.Timestamp(t):i for i,t in enumerate(g.ts)};kw={}
    for f in ('o','h','l','c'):
        a=getattr(g,f)
        kw[f]=np.array([np.r_[a[idx[d-pd.Timedelta(days=1)],1020:],a[idx[d],:960]] for d in dates])
    return SimpleNamespace(**kw,ts=pd.DatetimeIndex(dates).to_numpy(),last_j=np.full(len(dates),1379))
def replay(s):
    sig=pd.DataFrame(dict(day=np.arange(len(s.ts)),dj=ENTRY-1,side=1,stop=np.inf,target=25.,exit_j=EXIT))
    first=execute(s,sig,max_trades=1,name='Nocturne_adaptation');first['leg']=1
    hit=first[first.kind==1].copy();hit['next_j']=((hit.j1.astype(int)+4)//5)*5+1
    hit=hit[hit.next_j<=EXIT]
    sig2=pd.DataFrame(dict(day=hit.day.to_numpy(),dj=hit.next_j.to_numpy()-1,side=1,stop=np.inf,target=25.,exit_j=EXIT))
    second=execute(s,sig2,max_trades=1,name='Nocturne_reentry');second['leg']=2
    t=pd.concat([first,second],ignore_index=True).sort_values(['day','j0'])
    t['gross_mnq']=t.pnl/10
    t['market_fills']=1+(t.kind==2).astype(int)
    t['commission_mnq']=1.24
    t['slippage_mnq']=t.market_fills*.5
    t['net_mnq']=t.gross_mnq-t.commission_mnq-t.slippage_mnq
    t['stress_mnq']=t.gross_mnq-t.commission_mnq-t.market_fills
    t['source_cost_mnq']=t.gross_mnq-.725
    t['net_nq']=t.pnl-7.25-t.market_fills*5
    return t
def metric(daily,trades):
    r=M.perf(daily,trades);x=pd.Series(daily)
    r.update(total=float(x.sum()),daily_t=float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))),max_dd=max_dd(x))
    return r
def safe(x):
    if isinstance(x,dict):return {k:safe(v) for k,v in x.items()}
    if isinstance(x,list):return [safe(v) for v in x]
    if isinstance(x,(np.integer,)):return int(x)
    if isinstance(x,(np.bool_,)):return bool(x)
    if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else None
    return x
def design():
    inv=json.loads((OUT/'inventory.json').read_text());c=pd.read_csv(OUT/'inventory_dates.csv',parse_dates=['date'])
    if inv['night_coverage']/inv['nonroll_nights']<.90 or inv['eligible_nights']<500:raise ValueError('Data gate failed')
    for i in inv['inputs']:
        if digest(ROOT/i['path'])!=i['sha256']:raise ValueError('Input changed')
    discovered=list((ROOT/'data').glob('NQ_1min_20*.csv'))+list((ROOT/'data').glob('NQ_1min_ON_20*.csv'))
    if set(discovered)!=set(FILES):raise ValueError('Isolate precisely the eleven hashed design files before reading prices')
    g=Grid24(str(ROOT/'data/NQ_1min_20*.csv'),night_pattern=str(ROOT/'data/NQ_1min_ON_20*.csv'))
    if pd.Timestamp(g.ts[-1]).year>2022:raise ValueError('Later-year data present; refuse outcomes')
    rows=c[c.eligible];dates=pd.DatetimeIndex(rows.date);s=shifted(g,dates)
    reference_dates=sorted({r for d in dates for r in refs(d)});history=shifted(g,reference_dates)
    hx=dict(zip(reference_dates,history.c[:,5:1380:5]));ranks=[];signs=[]
    xx=np.arange(550,dtype=float)
    for d in dates:
        yy=np.r_[hx[refs(d)[0]],hx[refs(d)[1]]];valid=np.isfinite(yy)
        if valid.sum()<496:raise ValueError('Timestamp/feature mismatch')
        rr=float(np.corrcoef(xx[valid],yy[valid])[0,1]**2) if np.std(yy[valid])>0 else 0.
        ranks.append(rr);signs.append(int(yy[valid][-1]>=yy[valid][0]))
    t=replay(s);nights=pd.DataFrame(dict(date=dates,r2=ranks,prior_sign=signs));nights['kept']=nights.r2>=.3
    t=t.merge(nights,on='date',validate='many_to_one');t.to_csv(OUT/'design_trades.csv',index=False)
    for col in ['gross_mnq','net_mnq','stress_mnq','source_cost_mnq','net_nq']:
        nights[col]=t.groupby('date')[col].sum().reindex(dates).to_numpy()
    if nights.isna().any().any():raise ValueError('Unknown nightly result')
    nights.to_csv(OUT/'design_nights.csv',index=False)
    # Conditional eligible-night metrics; excluded unknown windows are not imputed zero returns.
    days=dates;base=pd.Series(nights.net_mnq.to_numpy(),index=dates)
    kept=nights.kept.to_numpy();filtered=pd.Series(np.where(kept,nights.net_mnq,0),index=dates).reindex(days,fill_value=0.)
    actual=metric(filtered,t.loc[t.kept,'net_mnq']);unfiltered=metric(base,t.net_mnq)
    if not np.isclose(filtered.sum(),t.loc[t.kept,'net_mnq'].sum()):raise ValueError('Trade/day accounting')
    years=[]
    for y in range(2018,2023):
        tt=t[t.kept&(t.date.dt.year==y)];m=metric(filtered[filtered.index.year==y],tt.net_mnq);m['year']=y;years.append(m)
    pd.DataFrame(years).to_csv(OUT/'design_years.csv',index=False)
    rng=np.random.default_rng(30102026);null=[];values=nights.net_mnq.to_numpy()
    cells=[ix.to_numpy() for _,ix in nights.groupby([nights.date.dt.year,nights.prior_sign]).groups.items()]
    for _ in range(1000):
        mask=np.zeros(len(nights),bool)
        for ix in cells:mask[rng.choice(ix,int(kept[ix].sum()),replace=False)]=True
        v=np.where(mask,values,0.);null.append(dict(total=float(v.sum()),max_dd=max_dd(v)))
    nd=pd.DataFrame(null);nd.to_csv(OUT/'design_random_keep.csv',index=False)
    joint=float(((actual['total']>=nd.total)&(actual['max_dd']<=nd.max_dd)).mean())
    removed=values[~kept];removed_t=float(removed.mean()/removed.std(ddof=1)*np.sqrt(len(removed)))
    block=10;nb=int(np.ceil(len(filtered)/block));rng=np.random.default_rng(30102027)
    starts=rng.integers(0,len(filtered)-block+1,(2000,nb));ii=(starts[:,:,None]+np.arange(block)).reshape(2000,-1)[:,:len(filtered)]
    ci=np.percentile(filtered.to_numpy()[ii].mean(1),[5,95])
    gates=dict(at_least300_kept_nights=kept.sum()>=300,positive_net=actual['total']>0,daily_t_at_least2=actual['daily_t']>=2,
        four_positive_years=sum(m['total']>0 for m in years)>=4,block_mean_lower_positive=ci[0]>0,
        stress_positive=nights.loc[kept,'stress_mnq'].sum()>0,
        filtered_total_ge_unfiltered=actual['total']>=unfiltered['total'],
        removed_negative_t_le_minus2=removed.mean()<0 and removed_t<=-2,matched_random_keep_joint_ge95=joint>=.95)
    output=dict(period='2018-2022',replication='assumed adaptation, not author code',native_size='1MNQ',filtered=actual,unfiltered=unfiltered,
        kept_nights=int(kept.sum()),eligible_nights=len(nights),gross_filtered=float(nights.loc[kept,'gross_mnq'].sum()),
        source_cost_filtered=float(nights.loc[kept,'source_cost_mnq'].sum()),stress_filtered=float(nights.loc[kept,'stress_mnq'].sum()),
        removed_mean=float(removed.mean()),removed_t=removed_t,random_keep_joint_win_fraction=joint,mean_daily_ci90=ci.tolist(),
        gates=gates,passed=all(gates.values()),recent_tested=False,accounts_tested=False,shorts='not registered',
        worst_filtered_night=float(nights.loc[kept,'net_mnq'].min()))
    (OUT/'design_gate.json').write_text(json.dumps(safe(output),indent=2)+'\n');print(json.dumps(safe(output),indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['inventory','design']);a=p.parse_args()
    inventory() if a.phase=='inventory' else design()
