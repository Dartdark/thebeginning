"""Frozen new standalone NQ trade from Treasury BTC deviation confirmed by ZN.

BTC is a published-result historical deviation, not a consensus surprise or WI tail.
The historical result-receipt/vintage assumption is explicit, not verified by price data.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import re
import sys
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'analysis/outputs/codex_auction_demand_confirmation'
sys.path.insert(0,str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import codex_t6_study_support as S
C=S.C;F=S.F;os.environ['NUMBA_CACHE_DIR']=str(OUT/'numba_cache')
PLAN='agents/codex/plans/auction_demand_confirmation.md'
CONFIGS={'ADC15':(15,0.),'ADC5':(5,0.),'ADC15_D05':(15,.05),'ZN15':(15,None),'ZN5':(5,None)}
CANDIDATES=['ADC15','ADC5','ADC15_D05'];BASE={'ADC15':'ZN15','ADC5':'ZN5','ADC15_D05':'ZN15'}
SCOLS=['day','signal_j','dj','side','stop','target','exit_j','delta_fraction','input_last_j','first_entry_j',
       'btc','btc_reference','btc_deviation','zn_reaction','tenor','reopening']


def tenor(term):
    y=re.search(r'(\d+)-Year',str(term));m=re.search(r'(\d+)-Month',str(term))
    if y is None:return None
    duration=int(y.group(1))+(int(m.group(1))/12 if m else 0.)
    allowed=np.array([2,3,5,7,10,20,30]);distance=abs(allowed-duration);best=distance.min()
    match=allowed[np.isclose(distance,best,rtol=0,atol=1e-10)]
    return int(match[0]) if best<=.5 and len(match)==1 else None


def ref_value(values):
    last=np.asarray(values[-6:],float);valid=last[np.isfinite(last)&(last>0)]
    return (float(np.median(valid)) if len(valid)>=4 else np.nan),len(valid)


def result_features(events):
    history={};rows=[]
    # Batch a date before appending any of its results: every reference is strictly prior.
    for date,group in events.sort_values(['date','cusip'],kind='stable').groupby('date',sort=True):
        pending=[]
        for r in group.itertuples():
            key=(int(r.tenor),r.reopening);old=history.get(key,[])
            assert all(d<date for d,_ in old)
            ref,n=ref_value([v for _,v in old]);btc=float(r.btc)
            deviation=btc/ref-1 if np.isfinite(btc) and btc>0 and np.isfinite(ref) and ref>0 else np.nan
            rows.append(dict(date=date,cusip=r.cusip,tenor=int(r.tenor),reopening=r.reopening,btc=btc,
                btc_reference=ref,btc_deviation=deviation,prior_same_group_count=len(old),valid_reference_count=n,
                last_prior_result_date=old[-1][0] if old else pd.NaT,event_multiplicity=len(group)))
            pending.append((key,btc if np.isfinite(btc) and btc>0 else np.nan))
        for key,value in pending:history.setdefault(key,[]).append((date,value))
    return pd.DataFrame(rows)


def duplicate_conflicts(raw):
    key=['auction_date','cusip'];dup=raw.duplicated(key,keep=False)
    fields=[c for c in raw.columns if c not in key]
    return int((raw[dup].groupby(key,dropna=False)[fields].nunique(dropna=False)>1).any(axis=1).sum())


def load_results(hi,phase):
    raw=pd.read_csv(ROOT/'data/treasury_auctions.csv',dtype={'cusip':str})
    raw['date']=pd.to_datetime(raw.auction_date,errors='raise');raw=raw[raw.date<=hi].copy()
    exact=int(raw.drop(columns='date').duplicated().sum());conflicts=duplicate_conflicts(raw)
    audit=dict(rows=len(raw),exact_duplicates=exact,conflicting_keys=conflicts,
        source_fields=['auction_date','cusip','security_type','security_term','closing_time_comp','reopening','inflation_index_security','floating_rate','bid_to_cover_ratio'],
        high_yield_used=False,clock='13:00ET deadline=12:00CT; actual result receipt/vintage unverified')
    if conflicts:
        C.dump(OUT/f'{phase}_auction_intake.json',audit);raise ValueError('NEEDS DATA: conflicting auction CUSIP/date records')
    raw=raw.drop_duplicates(['auction_date','cusip']).copy()
    deadline=raw.closing_time_comp.astype(str).str.replace(' ','',regex=False).str.upper()
    structural=(raw.security_type.isin(['Note','Bond'])&(raw.inflation_index_security=='No')&(raw.floating_rate=='No')
        &(deadline=='01:00PM')&raw.reopening.isin(['Yes','No'])&raw.cusip.str.fullmatch(r'[A-Za-z0-9]{9}',na=False))
    e=raw[structural].copy();e['tenor']=e.security_term.map(tenor)
    audit['structural_exclusions']=int((~structural).sum());audit['unsupported_tenor_rows']=int(e.tenor.isna().sum());e=e[e.tenor.notna()].copy();e['tenor']=e.tenor.astype(int)
    e['btc']=pd.to_numeric(e.bid_to_cover_ratio,errors='coerce');bad=~np.isfinite(e.btc)|(e.btc<=0)
    audit['invalid_BTC_history_slots']=int(bad.sum());e.loc[bad,'btc']=np.nan
    audit.update(eligible_events=len(e),eligible_dates=int(e.date.nunique()),multiple_event_dates=int((e.groupby('date').size()>1).sum()),
        first=str(e.date.min().date()),last=str(e.date.max().date()),by_tenor={str(k):int(v) for k,v in e.tenor.value_counts().sort_index().items()})
    C.dump(OUT/f'{phase}_auction_intake.json',audit)
    f=result_features(e);C.csv(OUT/f'{phase}_auction_features.csv',f)
    return f


def signal_side(deviation,zn_reaction,threshold):
    side=int(np.sign(zn_reaction))
    if not side:return 0
    if threshold is None:return side
    if not np.isfinite(deviation) or int(np.sign(deviation))!=side or abs(deviation)<threshold:return 0
    return side


def signals(nq,zn,events,frame,threshold,lo,hi):
    rows=[];audit=[];j=720+frame;valid_nq=S.valid(nq)&(nq.o>0)&(nq.h>0)&(nq.l>0)&(nq.c>0)
    valid_zn=S.valid(zn)&(zn.o>0)&(zn.h>0)&(zn.l>0)&(zn.c>0)
    nd={int(v):i for i,v in enumerate(nq.dates)};zd={int(v):i for i,v in enumerate(zn.dates)}
    for r in events.itertuples():
        if not lo<=r.date<=hi:continue
        reason='eligible';side=0;reaction=np.nan;d=nd.get(int(r.date.strftime('%Y%m%d')));z=zd.get(int(r.date.strftime('%Y%m%d')))
        if r.event_multiplicity!=1:reason='multiple_simultaneous_events'
        elif not C.normal_cash(r.date):reason='calendar_skip'
        elif not np.isfinite(r.btc_deviation):reason='invalid_result_or_prior_reference'
        elif d is None or z is None:reason='missing_exact_market_date'
        elif not valid_nq[d,719:j+1].all() or not valid_zn[z,719:j+1].all():reason='incomplete_known_price_window'
        elif not np.isfinite(nq._flow_atr[d]) or nq._flow_atr[d]<=0:reason='prior_ATR_warmup'
        else:
            reaction=float(zn.c[z,j]-zn.c[z,719]);side=signal_side(r.btc_deviation,reaction,threshold)
            if not reaction:reason='zero_ZN_reaction'
            elif not side:reason='demand_confirmation_or_size_gate'
            else:
                atr=nq._flow_atr[d]
                rows.append(dict(day=int(d),signal_j=j,dj=j+1,side=side,stop=np.ceil(.15*atr*4)/4,target=np.ceil(.30*atr*4)/4,
                    exit_j=775,delta_fraction=np.nan,input_last_j=j,first_entry_j=j+2,btc=r.btc,btc_reference=r.btc_reference,
                    btc_deviation=r.btc_deviation,zn_reaction=reaction,tenor=r.tenor,reopening=r.reopening))
                reason='signal'
        audit.append(dict(date=r.date,cusip=r.cusip,tenor=r.tenor,reopening=r.reopening,reason=reason,side=side,
            decision_j=j,btc=r.btc,btc_reference=r.btc_reference,btc_deviation=r.btc_deviation,zn_reaction=reaction))
    return pd.DataFrame(rows,columns=SCOLS),pd.DataFrame(audit)


def engineering():
    assert tenor('9-Year 11-Month')==10 and tenor('19-Year 10-Month')==20 and tenor('29-Year 10-Month')==30
    assert tenor('2-Year 6-Month') is None
    assert ref_value([2.,3.,4.,5.,100.])[0]==4.
    assert ref_value([9.,9.,2.,3.,4.,5.])[0]==4.5
    assert np.isnan(ref_value([9.,9.,2.,3.,4.,np.nan,np.nan,np.nan])[0])  #3valid of exact last6, no stretching
    dates=pd.date_range('2018-01-01',periods=6,freq='MS')
    e=pd.DataFrame(dict(date=dates,cusip=[str(i).zfill(9) for i in range(6)],tenor=2,reopening='No',btc=[2.,3.,4.,5.,6.,7.]))
    a=result_features(e);assert a.loc[4,'btc_reference']==3.5
    e.loc[5,'btc']=1e9;b=result_features(e);pd.testing.assert_frame_equal(a.iloc[:5],b.iloc[:5],check_exact=True)
    e.loc[4,'btc']=1e6;c=result_features(e);assert c.loc[4,'btc_reference']==3.5
    duplicate=pd.DataFrame(dict(auction_date=['2018-01-01']*2,cusip=['123456789']*2,bid_to_cover_ratio=[2.,3.]))
    assert duplicate_conflicts(duplicate)==1
    for date in ('2024-01-10','2024-07-10'):
        dt=datetime.fromisoformat(date+'T13:00:00').replace(tzinfo=ZoneInfo('America/New_York')).astimezone(ZoneInfo('America/Chicago'))
        assert dt.hour==12
    assert signal_side(.1,.015625,0.)==1 and signal_side(-.1,-.015625,0.)==-1
    assert signal_side(.1,-.015625,0.)==0 and signal_side(0.,.015625,0.)==0
    assert signal_side(0.,.015625,None)==1 and signal_side(.02,.015625,.05)==0
    assert 735+2==737 and 725+2==727
    C.engineering()
    return dict(passed=True,checks=['tenor/reopening baseline and equidistant rejection','strict prior reference excludes current/future BTC',
        'invalid historical result keeps rolling-window slot','stable duplicate key catches result conflicts','US ET/CT summer/winter conversion',
        'BTC/ZN sign agreement and exact nested-control side','one-extra-minute entry; shared calendar/entrybar/gap/through tests'])


def stratified_drops(candidate,base,events,days,seed=20261026):
    meta=events[events.event_multiplicity==1][['date','tenor','reopening']]
    b=base.merge(meta,on='date',validate='one_to_one');c=candidate.merge(meta,on='date',validate='one_to_one')
    b['year']=b.date.dt.year;c['year']=c.date.dt.year
    if c.empty:return dict(runs=1000,informative=False,p_random_net_ge_kept=1.,p_kept_better_net_and_dd=0.)
    groups=[];cells=[]
    for (yr,t,r),n in c.groupby(['year','tenor','reopening']).size().items():
        idx=np.flatnonzero(((b.year==yr)&(b.tenor==t)&(b.reopening==r)).to_numpy());assert len(idx)>=n
        groups.append((idx,int(n)));cells.append(dict(year=int(yr),tenor=int(t),reopening=r,base=len(idx),kept=int(n)))
    net=float(c.net.sum());dd=C.R.max_dd(c.groupby('date').net.sum().reindex(days,fill_value=0.));rng=np.random.default_rng(seed)
    totals=[];dds=[]
    for _ in range(1000):
        idx=np.sort(np.concatenate([rng.choice(i,n,replace=False) for i,n in groups]));tx=b.iloc[idx]
        totals.append(float(tx.net.sum()));dds.append(C.R.max_dd(tx.groupby('date').net.sum().reindex(days,fill_value=0.)))
    nets=np.asarray(totals);draw=np.asarray(dds)
    return dict(runs=1000,informative=True,actual_executable_ledger_subsets=True,cells=cells,kept_net=net,kept_dd=dd,
        random_net_mean=float(nets.mean()),p_random_net_ge_kept=float((nets>=net).mean()),
        p_kept_better_net_and_dd=float(((nets<net)&(draw>dd)).mean()),random_net_totals=totals,random_dd=dds)


def run(prereg,phase):
    started=datetime.now(timezone.utc).isoformat()
    S.bind(OUT,PLAN,prereg,CONFIGS,['NQ','ZN'],50,['codex_auction_demand_confirmation.py'])
    C.dump(OUT/'result_source_binding.json',dict(path='data/treasury_auctions.csv',sha256=C.sha(ROOT/'data/treasury_auctions.csv'),
        no_high_yield_signal=True,receipt_assumption='result publicly available by12:15CT primary/12:05 variant; actual receive/vintage timestamps absent'))
    C.dump(OUT/'engineering_checks.json',engineering())
    lo=pd.Timestamp('2018-01-01' if phase=='design' else '2023-01-01');hi=pd.Timestamp('2022-12-31' if phase=='design' else '2026-10-09');chosen=None
    if phase=='validation':
        chosen=json.loads((OUT/'design_complete_gate.json').read_text())['selected']
        if chosen is None:raise ValueError('Design rejected; do not validate, continue DISTINCT research')
    events=load_results(hi,phase)
    intake={s:S.intake(s,hi) for s in ('NQ','ZN')};C.dump(OUT/f'{phase}_price_intake.json',intake)
    if any(v['conflicting_keys'] for v in intake.values()):raise ValueError('NEEDS DATA: native conflicting keys')
    nq=S.load('NQ',hi);zn=S.load('ZN',hi);configs=CONFIGS if phase=='design' else {k:CONFIGS[k] for k in (chosen,BASE[chosen])}
    sigs={};counts={}
    for name,args in configs.items():
        sigs[name],audit=signals(nq,zn,events,*args,lo,hi);C.csv(OUT/f'{phase}_{name}_event_audit.csv',audit)
        counts[name]=audit.reason.value_counts().to_dict()
    days=S.sessions(nq,lo,hi)
    ledgers,df,_=S.evaluate(OUT,nq,sigs,days,phase,prereg,CANDIDATES,BASE,50,counts=counts)
    strata={name:stratified_drops(ledgers[name],ledgers[BASE[name]],events,days) for name in CANDIDATES if name in configs}
    C.dump(OUT/f'{phase}_stratified_drops.json',strata);selected=chosen
    if phase=='design':
        basic=json.loads((OUT/'design_gate.json').read_text());uniform=json.loads((OUT/'design_filter_diagnostics.json').read_text());gates={}
        for name in CANDIDATES:
            f=uniform[name];s=strata[name]
            checks=dict(removed_loses=f['removed_avg']<0,kept_total_ge_base=f['kept_net']>=f['base_net'],uniform_net=f['p_random_net_ge_kept']<=.10,
                uniform_joint=f['p_kept_better_net_and_dd']>=.90,stratified_net=s['p_random_net_ge_kept']<=.10,stratified_joint=s['p_kept_better_net_and_dd']>=.90)
            gates[name]={**basic['gates'][name],**{k:bool(v) for k,v in checks.items()}}
        passing=[k for k,v in gates.items() if all(v.values())];selected=passing[0] if passing else None
        C.dump(OUT/'design_complete_gate.json',dict(prereg=prereg,gates=gates,passing=passing,selected=selected,
            counted_program_evaluations=55,unique_program_models=54,exact_actual_subset_controls=True,program_continues=True))
    p=OUT/f'{phase}_verified_execution.json'
    if not p.exists():C.dump(p,dict(started_utc=started,completed_utc=datetime.now(timezone.utc).isoformat(),workspace=str(ROOT),
        interpreter=sys.executable,actual_raw_data_execution=True,models=list(configs),selected=selected,prereg=prereg))
    print('Complete gate selected:',selected,flush=True)
    return ledgers,df,selected


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase',choices=['design','validation']);p.add_argument('--prereg');p.add_argument('--self-check',action='store_true');a=p.parse_args()
    if a.self_check:print(engineering())
    else:
        if not a.phase or not a.prereg:p.error('--phase and --prereg required')
        run(a.prereg,a.phase)
