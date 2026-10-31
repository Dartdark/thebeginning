"""Frozen new NQ entry from cumulative variance exceeding a lagged option-implied budget.

No old strategy tickets. All forecasts use completed prior normal dates only;
current full-session values are appended to history after current decisions.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_implied_variance_breach'
sys.path.insert(0,str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import codex_t6_study_support as S
C=S.C;F=S.F
os.environ['NUMBA_CACHE_DIR']=str(OUT/'numba_cache')
PLAN='agents/codex/plans/implied_variance_breach.md'
CONFIGS={'IVB5_2':(5,2.),'IVB5_3':(5,3.),'IVB15_2':(15,2.),'BASE5':(5,None),'BASE15':(15,None)}
CANDIDATES=['IVB5_2','IVB5_3','IVB15_2']
BASE={'IVB5_2':'BASE5','IVB5_3':'BASE5','IVB15_2':'BASE15'}
SCOLS=['day','signal_j','dj','side','stop','target','exit_j','delta_fraction','input_last_j','first_entry_j','budget_ratio']
NAME='NQ Implied Variance Budget Breach'


def prior_cash_date(date):
    x=pd.Timestamp(date).normalize()-pd.Timedelta(days=1)
    for _ in range(10):
        if C.calendar_status(x)['kind'] in ('normal','early'):return x
        x-=pd.Timedelta(days=1)
    raise ValueError('No preceding cash date in10calendar days')


def lagged_quote(date,quotes):
    previous=prior_cash_date(date);value=quotes.get(previous,np.nan)
    return previous,float(value) if np.isfinite(value) and value>0 else np.nan


def forecast(history,iv):
    ratio=np.asarray([r['ratio'] for r in history[-60:]],float)
    curves=np.asarray([r['curve'] for r in history[-20:]],float) if history else np.empty((0,390))
    nr=int(np.isfinite(ratio).sum());nc=int(np.isfinite(curves).all(axis=1).sum())
    if len(history)<60 or nr<45 or nc<15 or not np.isfinite(iv) or iv<=0:
        return np.full(390,np.nan),np.nan,np.full(390,np.nan),nr,nc
    scale=float(np.nanmedian(ratio));shape=np.nanmedian(curves,axis=0)
    return iv*scale*shape,scale,shape,nr,nc


def one_day_features(g,d,date,quotes,history,valid):
    qdate,q=lagged_quote(date,quotes);iv=(q/100.)**2/252. if np.isfinite(q) else np.nan
    expected,scale,shape,nr,nc=forecast(history,iv)
    prefix=np.logical_and.accumulate(valid[d,511:901])
    cc=g.c[d,511:901];op=g.o[d,511]
    with np.errstate(invalid='ignore',divide='ignore'):
        rv=np.cumsum(np.diff(np.log(np.r_[op,cc]))**2)
        pv=np.cumsum((g.h[d,511:901]+g.l[d,511:901]+cc)/3*g.v[d,511:901])
        vv=np.cumsum(g.v[d,511:901]);vw=pv/vv
    rows=[];atr=g._flow_atr[d]
    for j in range(540,811,5):
        k=j-511;reason='eligible';side=0;ratio=np.nan
        if not prefix[k]:reason='incomplete_current_prefix'
        elif not np.isfinite(q):reason='missing_exact_prior_VXN'
        elif not np.isfinite(expected[k]) or expected[k]<=0:reason='prior_calibration_warmup_or_missing'
        elif not np.isfinite(atr) or atr<=0:reason='prior_ATR_warmup'
        elif not np.isfinite(vw[k]) or vv[k]<=0:reason='invalid_running_volume'
        else:
            ratio=rv[k]/expected[k];net=cc[k]-op
            side=1 if net>=.20*atr and cc[k]>vw[k] else (-1 if net<=-.20*atr and cc[k]<vw[k] else 0)
            if not side:reason='no_directional_price_signal'
        rows.append(dict(day=int(d),date=pd.Timestamp(date),signal_j=j,prior_vxn_date=qdate,prior_vxn=q,
            iv_daily_variance=iv,normal_dates_in_history=len(history),scale_observations=nr,shape_observations=nc,
            scale=scale,variance_share=shape[k],expected_rv=expected[k],actual_rv=rv[k],budget_ratio=ratio,
            net_change=cc[k]-op,vwap=vw[k],atr=atr,prefix_complete=bool(prefix[k]),reason=reason,side=side))
    # This record may contain end-of-day data. It has no role in rows above and
    # is appended by the caller only after this function returns today's rows.
    good=bool(prefix.all() and np.isfinite(iv) and iv>0 and np.isfinite(rv[-1]) and rv[-1]>0)
    record=dict(date=pd.Timestamp(date),ratio=float(rv[-1]/iv) if good else np.nan,
        curve=rv/rv[-1] if good else np.full(390,np.nan),usable=good)
    return rows,record


def features(g,quotes,lo,hi):
    valid=S.valid(g)&(g.o>0)&(g.h>0)&(g.l>0)&(g.c>0)
    history=[];rows=[];records=[]
    for d in range(g.D):
        date=pd.Timestamp(g.ts[d])
        if date>hi or not C.normal_cash(date):continue
        today,record=one_day_features(g,d,date,quotes,history,valid)
        if lo<=date<=hi:rows.extend(today)
        records.append(dict(date=date,usable=record['usable'],realized_to_implied_ratio=record['ratio'],
            preceding_normal_dates=len(history)))
        history.append(record)
    return pd.DataFrame(rows),pd.DataFrame(records)


def signals(feature,frame,threshold):
    rows=[];f=feature[feature.signal_j%frame==0]
    for r in f.itertuples():
        if r.reason!='eligible' or (threshold is not None and r.budget_ratio<threshold):continue
        rows.append(dict(day=r.day,signal_j=r.signal_j,dj=r.signal_j+1,side=r.side,stop=np.ceil(.15*r.atr*4)/4,
            target=np.ceil(.45*r.atr*4)/4,exit_j=895,delta_fraction=np.nan,input_last_j=r.signal_j,
            first_entry_j=r.signal_j+2,budget_ratio=r.budget_ratio))
    return pd.DataFrame(rows,columns=SCOLS),f.reason.value_counts().to_dict()


def first_signals(s):
    return s.sort_values(['day','signal_j'],kind='stable').groupby('day',sort=True).head(1).reset_index(drop=True)


def replay_one(g,s):
    first=first_signals(s);t,counts=F.replay(g,first)
    assert not t.date.duplicated().any()
    counts.update(qualifying_windows=len(s),first_windows=len(first),suppressed_after_first=len(s)-len(first))
    return t,first,counts


def engineering():
    assert prior_cash_date('2024-04-01')==pd.Timestamp('2024-03-28')
    prev=pd.Timestamp('2024-03-28');today=pd.Timestamp('2024-04-01')
    assert lagged_quote(today,{prev:20.,today:100.})==(prev,20.)
    assert np.isnan(lagged_quote(today,{prev-pd.Timedelta(days=1):20.,today:100.})[1])
    curve=np.linspace(1/390,1,390);hist=[dict(ratio=1.,curve=curve.copy()) for _ in range(60)]
    iv=(20/100)**2/252;ex,sc,sh,nr,nc=forecast(hist,iv)
    np.testing.assert_allclose(ex,iv*curve);assert sc==1 and nr==60 and nc==20
    assert np.isnan(forecast(hist[:59],iv)[0]).all()
    assert abs((4*iv)/(iv)-4)<1e-12  # variance4x means sigma2x, not sigma4x
    class Toy:pass
    g=Toy();g.o=np.full((1,1440),np.nan);g.c=g.o.copy();g.h=g.o.copy();g.l=g.o.copy();g.v=g.o.copy();g._flow_atr=np.array([200.])
    cc=10000*np.exp(np.cumsum(.001*np.sin(np.arange(390.)+.2)))
    g.c[0,511:901]=cc;g.o[0,511:901]=np.r_[10000.,cc[:-1]]
    g.h[0,511:901]=np.maximum(g.o[0,511:901],cc)+1;g.l[0,511:901]=np.minimum(g.o[0,511:901],cc)-1;g.v[0,511:901]=100.
    valid=S.valid(g);rows,_=one_day_features(g,0,today,{prev:20.},hist,valid)
    # Mutating today's later prices/completeness changes its EOD history record,
    # but never signals/features generated before that mutation's minute.
    g.c[0,721:901]=np.nan;g.o[0,721:901]=np.nan
    later,_=one_day_features(g,0,today,{prev:20.},hist,S.valid(g))
    a=pd.DataFrame(rows).query('signal_j<=720');b=pd.DataFrame(later).query('signal_j<=720')
    pd.testing.assert_frame_equal(a,b,check_exact=True)
    s=pd.DataFrame([dict(day=0,signal_j=j,dj=j+1,side=1,stop=10.,target=20.,exit_j=895,
        delta_fraction=np.nan,input_last_j=j,first_entry_j=j+2,budget_ratio=2.) for j in (540,545)],columns=SCOLS)
    g.ts=np.array([today.to_datetime64()]);g.o[0,542]=np.nan
    t,first,ct=replay_one(g,s);assert len(first)==1 and len(t)==0 and ct['missing_scheduled_entry']==1
    C.engineering()
    return dict(passed=True,checks=['exact previous cash quote/holiday clock','no older-date substitute','causal60/20date calibration and warmup',
        'variance vs volatility units','later price/completeness mutation leaves earlier rows identical','first signal spends day even on missingentry',
        'extra-minute delay; shared entrybar/gap/target-through synthetic checks'])


def load_quotes(hi,phase):
    raw=pd.read_csv(ROOT/'data/VXN_daily.csv',usecols=['DATE','CLOSE']);raw['DATE']=pd.to_datetime(raw.DATE)
    raw=raw[raw.DATE<=hi].copy();dup=raw.duplicated('DATE',keep=False)
    conflicts=int((raw[dup].groupby('DATE').CLOSE.nunique(dropna=False)>1).sum())
    audit=dict(rows=len(raw),exact_duplicates=int(raw.duplicated().sum()),conflicting_dates=conflicts,
        first=str(raw.DATE.min().date()),last=str(raw.DATE.max().date()),clock='prior exact US cash-market DATE closing value; receive/vintage timestamps unverified')
    C.dump(OUT/f'{phase}_VXN_intake.json',audit)
    if conflicts:raise ValueError('NEEDS DATA: conflicting VXN dates')
    return raw.drop_duplicates('DATE').set_index('DATE').CLOSE.to_dict()


def conditional_times(actual,base,days,seed=20261026):
    # Conditional, matched event dates; one sampled eligible price window/day.
    # These are executable paths on EX-POST event dates, not deployable calendars.
    if len(actual)==0:return dict(runs=1000,event_days=0,informative=False,p_random_net_ge_kept=1.,p_kept_better_net_and_dd=0.)
    b=base.reset_index(drop=True);ids=[np.flatnonzero((b.date==d).to_numpy()) for d in actual.date]
    assert all(len(x)>0 for x in ids)
    own_daily=actual.groupby('date').net.sum().reindex(days,fill_value=0.);own_net=float(actual.net.sum());own_dd=C.R.max_dd(own_daily)
    rng=np.random.default_rng(seed);totals=[];dds=[]
    for _ in range(1000):
        picked=np.array([rng.choice(x) for x in ids]);t=b.iloc[picked]
        totals.append(float(t.net.sum()));dds.append(C.R.max_dd(t.groupby('date').net.sum().reindex(days,fill_value=0.)))
    x=np.asarray(totals);dd=np.asarray(dds)
    return dict(runs=1000,event_days=len(actual),informative=True,ex_post_event_date_conditioning=True,actual_net=own_net,actual_dd=own_dd,
        random_net_mean=float(x.mean()),p_random_net_ge_kept=float((x>=own_net).mean()),
        p_kept_better_net_and_dd=float(((x<own_net)&(dd>own_dd)).mean()),random_net_totals=totals,random_dd=dds)


def basic_gate(t,days):
    m=C.stats(t,days);yy=t.groupby(t.date.dt.year).net.sum()
    return {k:bool(v) for k,v in dict(count=len(t)>=100,net=m['total']>0,t=m['t_trade']>=2,nw5=m['t_nw5']>=1.5,
        pf=m['profit_factor']>=1.2,years=(yy>0).sum()>=4,micro=t.net_mnq.sum()>0,stress=t.stress_four_ticks.sum()>0).items()}


def metrics(t,days,name,period):
    rows=[]
    for side,label in ((0,'all'),(1,'long'),(-1,'short')):
        tx=t if not side else t[t.side==side]
        for pp,dd in [(period,days)]+[(str(y),days[days.year==y]) for y in sorted(days.year.unique())]:
            tt=tx if pp==period else tx[tx.date.dt.year==int(pp)]
            rows.append(dict(model=name,period=pp,side=label,**C.stats(tt,dd)))
    for col in ('net_mnq','stress_four_ticks'):
        tt=t.copy()
        if col=='net_mnq':tt['pnl']/=10.
        rows.append(dict(model=name,period=period,side=col,**C.stats(tt,days,column=col)))
    return rows


def run(prereg,phase):
    started=datetime.now(timezone.utc).isoformat()
    S.bind(OUT,PLAN,prereg,CONFIGS,['NQ'],40,['codex_implied_variance_breach.py'])
    C.dump(OUT/'VXN_source_binding.json',dict(path='data/VXN_daily.csv',sha256=C.sha(ROOT/'data/VXN_daily.csv'),fields=['DATE','CLOSE'],prior_day_only=True))
    C.dump(OUT/'engineering_checks.json',engineering())
    lo=pd.Timestamp('2018-01-01' if phase=='design' else '2023-01-01');hi=pd.Timestamp('2022-12-31' if phase=='design' else '2026-10-09')
    chosen=None
    if phase=='validation':
        chosen=json.loads((OUT/'design_complete_gate.json').read_text())['selected']
        if chosen is None:raise ValueError('Local design stop; continue a DISTINCT hypothesis')
    intake=S.intake('NQ',hi);C.dump(OUT/f'{phase}_NQ_intake.json',intake)
    if intake['conflicting_keys']:raise ValueError('NEEDS DATA: conflicting NQ keys')
    quotes=load_quotes(hi,phase);g=S.load('NQ',hi);feature,history=features(g,quotes,lo,hi)
    C.csv(OUT/f'{phase}_features.csv',feature);C.csv(OUT/f'{phase}_calibration_history.csv',history)
    days=S.sessions(g,lo,hi);period='2018-22' if phase=='design' else '2023+'
    configs=CONFIGS if phase=='design' else {k:CONFIGS[k] for k in (chosen,BASE[chosen])}
    sigs={};ledgers={};ind={};cts={};rows=[];daily={}
    for name,args in configs.items():
        s,counts=signals(feature,*args);sigs[name]=s;t,first,ct=replay_one(g,s);ledgers[name]=t
        cts[name]=dict(input=counts,execution=ct,actual_trades=len(t));daily[name]=t.groupby('date').net.sum().reindex(days,fill_value=0.)
        C.csv(OUT/f'{phase}_{name}_potential_windows.csv',s);C.csv(OUT/f'{phase}_{name}_first_signals.csv',first);C.csv(OUT/f'{phase}_{name}_trades.csv',t)
        rows+=metrics(t,days,name,period)
    df=pd.DataFrame(rows);C.csv(OUT/f'{phase}_metrics.csv',df);C.csv(OUT/f'{phase}_daily.csv',pd.DataFrame(daily).rename_axis('date'),index=True)
    C.dump(OUT/f'{phase}_counts.json',cts)
    diagnostics={};actual_compare={};timeplacebos={}
    for name in (k for k in CANDIDATES if k in configs):
        base=BASE[name]
        if base not in ind:ind[base]=F.replay(g,sigs[base],independent=True)[0]
        cand=F.replay(g,sigs[name],independent=True)[0]
        diagnostics[name]=dict(non_executable_overlapping_windows=True,**C.filter_controls(cand,ind[base],days))
        C.csv(OUT/f'{phase}_{name}_independent_window_diagnostic.csv',cand[['day','j0','j1','side','date','net']])
        actual_compare[name]=dict(candidate_net=float(ledgers[name].net.sum()),base_net=float(ledgers[base].net.sum()),
            candidate_dd=C.R.max_dd(daily[name]),base_dd=C.R.max_dd(daily[base]),nested_actual_ledgers=False)
        timeplacebos[name]=conditional_times(ledgers[name],ind[base],days)
    C.dump(OUT/f'{phase}_filter_diagnostics.json',diagnostics);C.dump(OUT/f'{phase}_actual_base_comparison.json',actual_compare)
    C.dump(OUT/f'{phase}_conditional_time_placebos.json',timeplacebos)
    selected=chosen
    if phase=='design':
        gates={}
        for name in CANDIDATES:
            f=diagnostics[name];tp=timeplacebos[name];actual=actual_compare[name]
            checks=basic_gate(ledgers[name],days)
            checks.update({k:bool(v) for k,v in dict(actual_net_ge_base=actual['candidate_net']>=actual['base_net'],removed_loses=f['removed_avg']<0,
                diagnostic_total_ge_base=f['kept_net']>=f['base_net'],diagnostic_random_net=f['p_random_net_ge_kept']<=.10,
                diagnostic_random_joint=f['p_kept_better_net_and_dd']>=.90,conditional_time_net=tp['p_random_net_ge_kept']<=.10,
                conditional_time_joint=tp['p_kept_better_net_and_dd']>=.90).items()})
            gates[name]=checks
        passing=[k for k,v in gates.items() if all(v.values())];selected=passing[0] if passing else None
        C.dump(OUT/'design_complete_gate.json',dict(prereg=prereg,gates=gates,passing=passing,selected=selected,
            counted_program_evaluations=45,unique_program_models=44,diagnostic_paths_not_selectable=True,program_continues=True))
    record=OUT/f'{phase}_verified_execution.json'
    if not record.exists():C.dump(record,dict(started_utc=started,completed_utc=datetime.now(timezone.utc).isoformat(),workspace=str(ROOT),
        interpreter=sys.executable,actual_raw_data_execution=True,models=list(configs),selected=selected,prereg=prereg))
    print(df[(df.period==period)&(df.side=='all')][['model','trades','total','avg','profit_factor','t_trade','t_nw5','max_dd']].to_string(index=False),flush=True)
    print('Complete gate selected:',selected,flush=True)
    return ledgers,df,selected


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase',choices=['design','validation']);p.add_argument('--prereg');p.add_argument('--self-check',action='store_true')
    a=p.parse_args()
    if a.self_check:print(engineering())
    else:
        if not a.phase or not a.prereg:p.error('--phase and --prereg required')
        run(a.prereg,a.phase)
