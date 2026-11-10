"""Frozen funding/fear strategy batch. No live interfaces. Design gate precedes validation."""
from pathlib import Path
import hashlib
import json
import subprocess
import warnings

import numpy as np
import pandas as pd
import numba

from grid24 import Grid24
from grid import _walk
from candidates24 import _early
from portfolio import load_mc
import metrics as M

ROOT=Path(__file__).resolve().parents[1]
INP=ROOT/'agents/codex/inputs/new_data_strategies_20261110'
PRIMARY=ROOT/'agents/codex/inputs/new_data_primary_local_20261108/normalized'
OUT=ROOT/'analysis/outputs/codex_new_data_strategies_20261110'
PLAN='agents/codex/plans/new_data_strategies_20261110.md'
RAW=Path('/workspace/vb_loss_split_source/data')
RAW_REF='fe35af99aa90d7f31b91f8693859251bb44dd9ab'
SEED=20261110
MODELS={
 'FUND_CONTROL':('fund',-1,541,600,False),
 'FUND_SHORT':('fund',-1,541,600,True),
 'EARLY_CONTROL':('fear',1,451,509,False),
 'FEAR_EARLY':('fear',1,451,509,True),
 'MORNING_CONTROL':('fear',1,541,600,False),
 'FEAR_MORNING':('fear',1,541,600,True),
}
CANDIDATES={'FUND_SHORT':'FUND_CONTROL','FEAR_EARLY':'EARLY_CONTROL','FEAR_MORNING':'MORNING_CONTROL'}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def dump(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2,default=str)+'\n')


def clock_features(dates,rates,vix9d,vix):
    """Use core rates after their next-day revision window, fear closes two sessions old."""
    r=rates[rates.type.isin(['EFFR','SOFR'])].copy()
    r['effectiveDate']=pd.to_datetime(r.effectiveDate)
    next_dates={}
    for kind in ['EFFR','SOFR']:
        ds=pd.DatetimeIndex(sorted(r.loc[r.type.eq(kind),'effectiveDate'].unique()))
        next_dates[kind]=pd.Series(ds[1:].to_numpy(),index=ds[:-1])
    p=r.pivot(index='effectiveDate',columns='type',values='percentRate').dropna(subset=['EFFR','SOFR'])
    n=pd.concat([s.reindex(p.index).rename(k) for k,s in next_dates.items()],axis=1)
    valid=n.notna().all(axis=1)
    p=p[valid].copy()
    available=n[valid].max(axis=1)+pd.Timedelta(hours=15)
    p['available_at']=pd.DatetimeIndex(available).tz_localize('America/New_York').tz_convert('UTC')
    p['source_date']=p.index
    p['spread_bp']=(p.SOFR-p.EFFR)*100
    d=pd.DataFrame({'date':dates})
    d['decision_at']=(dates+pd.Timedelta(hours=7,minutes=30)).tz_localize('America/Chicago').tz_convert('UTC')
    # Both proposed families can know this by07:30, even though funding enters later.
    z=pd.merge_asof(d,p.sort_values('available_at'),left_on='decision_at',right_on='available_at',direction='backward')
    age=(z.date-z.source_date).dt.days
    good=z.spread_bp.notna()&age.le(7)&age.ge(0)
    z['fund_state']=np.where(good,(z.spread_bp>=5-1e-8).astype(float),np.nan)
    ratio=(vix9d/vix).replace([np.inf,-np.inf],np.nan)
    refs=pd.Series(dates,index=dates).shift(2)
    values=ratio.reindex(pd.DatetimeIndex(refs)).to_numpy()
    z['fear_source_date']=refs.to_numpy()
    z['fear_ratio']=values
    z['fear_state']=np.where(np.isfinite(values),(values>1).astype(float),np.nan)
    return z.set_index('date')


def clock_checks():
    days=pd.bdate_range('2020-01-06',periods=7)
    rates=pd.DataFrame([dict(effectiveDate=str(d.date()),type=k,percentRate=v)
                        for d in days for k,v in [('EFFR',1.5),('SOFR',1.6)]])
    a=pd.Series(20.,index=days);b=pd.Series(15.,index=days)
    z=clock_features(days,rates,a,b)
    assert pd.isna(z.fund_state.iloc[0]) and pd.isna(z.fund_state.iloc[1])
    assert z.fund_state.iloc[2]==1 and z.fear_ratio.iloc[2]==20/15
    assert z.source_date.iloc[2]==days[0]
    changed=rates.copy(); changed.loc[changed.effectiveDate>=str(days[4].date()),'percentRate']=99.
    zz=clock_features(days,changed,a,b)
    assert np.allclose(z.fund_state.iloc[:5],zz.fund_state.iloc[:5],equal_nan=True)
    aa=a.copy();aa.loc[days[0]]=np.nan
    zz=clock_features(days,rates,aa,b)
    assert pd.isna(zz.fear_state.iloc[2])
    assert (z.loc[z.available_at.notna(),'available_at']<=z.loc[z.available_at.notna(),'decision_at']).all()
    # Gap stop, target trade-through, and entry-minute protection use the canonical engine.
    o=np.array([100.,40.]);h=np.array([105.,45.]);l=np.array([95.,35.]);c=np.array([100.,42.])
    assert _walk(o,h,l,c,0,1,1,50.,200.,1.)[1:3]==(40.,0)
    assert _walk(np.array([100.]),np.array([200.5]),np.array([99.]),np.array([190.]),0,0,1,50.,200.,1.)[2]==2
    assert _walk(np.array([100.]),np.array([105.]),np.array([40.]),np.array([45.]),0,0,1,50.,200.,1.)[2]==0
    return {'availability_no_effective_day_trade':True,'future_value_prefix':True,
            'unknown_is_not_off':True,'two_session_fear_lag':True,'canonical_exit_fixtures':True}


def roll_dates(years):
    result=set()
    for year in years:
        for month in [3,6,9,12]:
            first=pd.Timestamp(year,month,1)
            friday=first+pd.Timedelta(days=(4-first.weekday())%7+14)
            result.add(friday-pd.Timedelta(days=8))
    return result


def run(g,features,name,lo='2018-01-01',hi='2023-01-01',opposite=False,restrict=None):
    family,side,j0,jend,gated=MODELS[name]
    if opposite:side=-side
    early=_early(g); rolls=roll_dates(range(2017,2027))
    rows=[];unknown=[];counts={'source_unknown':0,'overnight_price_unknown':0,'calendar_skip':0,'state_off':0,'price_condition_off':0}
    f=features.reindex(pd.DatetimeIndex(g.ts[g.trading]))
    for d,day in zip(g.trading,f.index):
        if day<pd.Timestamp(lo) or day>=pd.Timestamp(hi):continue
        if restrict is not None and day not in restrict:continue
        state=f.loc[day,'fund_state' if family=='fund' else 'fear_state']
        if not np.isfinite(state):counts['source_unknown']+=1;continue
        if early[d] or day in rolls:counts['calendar_skip']+=1;continue
        if family=='fear':
            p0,p1=g.o[d,1],g.c[d,450]
            if not np.isfinite(p0+p1):counts['overnight_price_unknown']+=1;continue
            if p1>=p0:counts['price_condition_off']+=1;continue
        if gated and state!=1:counts['state_off']+=1;continue
        seg=slice(j0,jend+1)
        if any(not np.isfinite(getattr(g,k)[d,seg]).all() for k in ['o','h','l','c']):
            unknown.append({'model':name,'date':day,'reason':'held_window_price_unknown'})
            continue
        ep=g.o[d,j0]
        j1,px,kind,worst=_walk(g.o[d],g.h[d],g.l[d],g.c[d],j0,jend,side,ep-side*50,ep+side*100,1.)
        gross=(px-ep)*side*2
        legs=1+int(kind!=1)
        rows.append(dict(model=name,date=day,day=int(d),j0=j0,j1=int(j1),side=side,entry=ep,exit=px,kind=int(kind),
                         gross=gross,commission=1.25,slippage=.5*legs,net=gross-1.25-.5*legs,
                         stress_net=gross-2.50-1.*legs,mae=abs(worst-ep)*2))
    cols=['model','date','day','j0','j1','side','entry','exit','kind','gross','commission','slippage','net','stress_net','mae']
    return pd.DataFrame(rows,columns=cols),{'counts':counts,'unknown_paths':unknown}


def measure(t,days,model,period='design',side='all'):
    z=t if side=='all' else t[t.side.eq(1 if side=='long' else -1)]
    z=z[z.date.isin(days)]
    if not len(z):return dict(model=model,period=period,side=side,trades=0,net=0.)
    x=z.net;daily=z.groupby('date').net.sum().reindex(days,fill_value=0.)
    daily=pd.concat([pd.Series([0.],index=[days[0]-pd.Timedelta(days=1)]),daily])
    m=M.perf(daily,x)
    return dict(model=model,period=period,side=side,net=float(x.sum()),gross=float(z.gross.sum()),
                commission=float(z.commission.sum()),slippage=float(z.slippage.sum()),
                stress_net=float(z.stress_net.sum()),t=float(x.mean()/x.std()*np.sqrt(len(x))) if x.std() else 0.,
                positive_years=int(x.groupby(z.date.dt.year).sum().gt(0).sum()),**m)


def drawdown(x):
    s=np.r_[0.,np.cumsum(x)]
    return float((np.maximum.accumulate(s)-s).max())


def reference_screen(g,features):
    path=ROOT/'analysis/outputs/codex_rebound/personal19/UNIFORM/fee_1.24/baseline_daily19.csv'
    p=pd.read_csv(path,parse_dates=['date']).set_index('date')
    for name,file in [('FINRA','finra_python_trades.csv'),('ZT125','zt_python_trades.csv')]:
        t=pd.read_csv(INP/file,parse_dates=['date'])
        p[name]=(t.net/10-.525).groupby(t.date).sum().reindex(p.index,fill_value=0.)
    t=load_mc(g,ROOT/'mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx')
    net=(t.exit-t.entry)*t.side*2-1.25-.5*(1+t.kind.ne(1).astype(int))
    p['ONB30']=net.groupby(t.date).sum().reindex(p.index,fill_value=0.)
    p=p[p.index<'2023-01-01']
    rows=[]
    for state in ['fund_state','fear_state']:
        v=features[state].reindex(p.index)
        for piece in p.columns:
            x=p[piece];known=v.notna()&x.ne(0)
            a=x[known&v.eq(1)];b=x[known&v.eq(0)]
            if len(a)>=10 and len(b)>=10:
                se=np.sqrt(a.var()/len(a)+b.var()/len(b));tt=float((a.mean()-b.mean())/se) if se else 0.
            else:tt=np.nan
            rows.append(dict(state=state,piece=piece,n_on=len(a),n_off=len(b),
                             unknown_active=int((v.isna()&x.ne(0)).sum()),
                             on_mean=float(a.mean()),off_mean=float(b.mean()),t=tt))
    result=pd.DataFrame(rows);assert len(result)==44
    bar=M.t_threshold(44)
    result['lead']=result.t.abs().ge(bar)
    result.to_csv(OUT/'reference_screen_design.csv',index=False)
    return dict(streams=len(p.columns),comparisons=44,t_threshold=bar,leads=int(result.lead.sum()),
                source_path=str(path.relative_to(ROOT)),source_sha256=sha(path),
                limit='Archived reference versions/costs; not a current intraday book replay.')


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--fixtures-only',action='store_true');args=parser.parse_args()
    checks=clock_checks();print('Mechanical checks',checks,flush=True)
    if args.fixtures_only:return
    for p in [PLAN,str(Path(__file__).relative_to(ROOT))]:
        assert subprocess.check_output(['git','show','HEAD:'+p],cwd=ROOT)==(ROOT/p).read_bytes(),'Commit exact plan/code first'
    OUT.mkdir(parents=True,exist_ok=True)
    receipt={'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
             'code_sha256':sha(__file__),'plan_sha256':sha(ROOT/PLAN),'raw_ref':RAW_REF,
             'claude_cutoff':'08544017aa5796e11d61b3b125ef0b14977956f5','inputs':{},'checks':checks,
             'dependencies':{m.__name__:m.__version__ for m in [np,pd,numba]}}
    for year in range(2017,2027):
        for prefix in ['NQ_1min_','NQ_1min_ON_']:
            rel=f'data/{prefix}{year}.csv';p=RAW/Path(rel).name;raw=p.read_bytes()
            actual=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            expected=subprocess.check_output(['git','rev-parse',RAW_REF+':'+rel],cwd=ROOT,text=True).strip()
            assert actual==expected,rel
            receipt['inputs'][rel]={'git_blob':actual,'sha256':sha(p)}
    warnings.filterwarnings('ignore',category=RuntimeWarning)
    g=Grid24(str(RAW/'NQ_1min_20*.csv'),str(RAW/'NQ_1min_ON_20*.csv'))
    dates=pd.DatetimeIndex(g.ts[g.trading])
    rates=pd.DataFrame(json.loads((PRIMARY/'nyfed_rates.json').read_text()))
    a=pd.read_csv(PRIMARY/'VIX9D.csv',parse_dates=['date']).set_index('date').close_index_points
    b=pd.read_csv(ROOT/'data/VIX_daily.csv',parse_dates=['DATE']).set_index('DATE').CLOSE
    features=clock_features(dates,rates,a,b)
    features[features.index<'2023-01-01'].to_csv(OUT/'design_feature_clocks.csv')
    dump('reference_screen.json',reference_screen(g,features))
    days=dates[(dates.year>=2018)&(dates.year<=2022)]
    trades={};status={};metrics=[]
    for name in MODELS:
        t,st=run(g,features,name);trades[name]=t;status[name]=st
        t.to_csv(OUT/(name+'_design_trades.csv'),index=False)
        metrics.extend(measure(t,days,name,side=s) for s in ['all','long','short'])
        metrics.extend(measure(t,days[days.year==y],name,period=str(y)) for y in range(2018,2023))
        print(name,metrics[-8],flush=True)
    pd.DataFrame(metrics).to_csv(OUT/'design_metrics.csv',index=False)
    gate=[]
    for name,control in CANDIDATES.items():
        t=trades[name];c=trades[control];m=measure(t,days,name)
        removed=c[~c.date.isin(t.date)]
        mu=float(removed.net.mean()) if len(removed) else np.nan
        tt=float(removed.net.mean()/removed.net.std()*np.sqrt(len(removed))) if len(removed)>1 and removed.net.std() else np.nan
        tests=dict(count=m['trades']>=60,net=m['net']>0,pf=m.get('profit_factor',0)>=1.2,t=m.get('t',0)>=2.5,
                   positive_years=m.get('positive_years',0)>=3,stress=m.get('stress_net',0)>0,
                   removed_mean_negative=bool(mu<0))
        gate.append(dict(candidate=name,control=control,tests=tests,cheap_pass=all(tests.values()),
                         removed_count=len(removed),removed_net=float(removed.net.sum()),removed_mean=mu,removed_t=tt,
                         control_total=float(c.net.sum()),candidate_total=m['net'],
                         unresolved_paths=len(status[name]['unknown_paths'])))
    survivors=[];nulls=[]
    for family in [['FUND_SHORT'],['FEAR_EARLY','FEAR_MORNING']]:
        eligible=[x for x in gate if x['candidate'] in family and x['cheap_pass']]
        if not eligible:continue
        selected=max(eligible,key=lambda x:measure(trades[x['candidate']],days,x['candidate'])['calmar'])
        name=selected['candidate'];t=trades[name];c=trades[selected['control']]
        rng=np.random.default_rng(SEED);n=len(t);tot=[];dd=[]
        for _ in range(1000):
            ix=np.sort(rng.choice(len(c),n,replace=False));xx=c.net.to_numpy()[ix]
            tot.append(xx.sum());dd.append(drawdown(xx))
        opposite,_=run(g,features,name,opposite=True,restrict=set(t.date))
        assert np.array_equal(t.date,opposite.date)
        signs=rng.integers(0,2,(1000,n));random_side=np.where(signs,t.net.to_numpy(),opposite.net.to_numpy()).sum(axis=1)
        passed=(t.net.sum()>np.percentile(tot,95) and drawdown(t.net.to_numpy())<=np.median(dd)
                and t.net.sum()>np.percentile(random_side,95))
        nulls.append(dict(candidate=name,random_drop_net_p95=float(np.percentile(tot,95)),
                          random_drop_dd_median=float(np.median(dd)),random_side_net_p95=float(np.percentile(random_side,95)),
                          real_net=float(t.net.sum()),real_dd=drawdown(t.net.to_numpy()),passes=bool(passed)))
        if passed:survivors.append(name)
    dump('design_gate.json',dict(candidates=gate,selected_nulls=nulls,survivors=survivors,
         status='DESIGN SURVIVOR: advance unchanged' if survivors else 'STOP: all new definitions fail design',
         hypotheses=2,candidate_arms=3,candidate_control_definitions=6,conditional_null_definitions=len(nulls),
         alternative_2023_outcomes_run=False,standing_screen_comparisons=44))
    dump('eligibility.json',status)
    for p in [PRIMARY/'nyfed_rates.json',PRIMARY/'VIX9D.csv',ROOT/'data/VIX_daily.csv',
              INP/'finra_python_trades.csv',INP/'zt_python_trades.csv',ROOT/'analysis/grid.py',ROOT/'analysis/grid24.py',
              ROOT/'analysis/candidates24.py',ROOT/'analysis/metrics.py']:
        receipt['inputs'][str(p.relative_to(ROOT))]={'sha256':sha(p)}
    dump('manifest.json',receipt)
    print('GATE',gate,'survivors',survivors,flush=True)


if __name__=='__main__':main()
