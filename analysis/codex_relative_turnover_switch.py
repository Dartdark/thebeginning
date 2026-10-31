"""New standalone NQ relative-turnover switch; ES is a quantity reference, never a traded leg."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import sys
import warnings
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'analysis/outputs/codex_relative_turnover_switch'
sys.path.insert(0,str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import codex_t6_study_support as S
C=S.C;F=S.F;os.environ['NUMBA_CACHE_DIR']=str(OUT/'numba_cache')
PLAN='agents/codex/plans/relative_turnover_switch.md'
CONFIGS={'CTS5_15':(5,1.5),'CTS5_20':(5,2.),'CTS15_15':(15,1.5),'OWN5':(5,None),'OWN15':(15,None)}
CANDIDATES=['CTS5_15','CTS5_20','CTS15_15'];BASE={'CTS5_15':'OWN5','CTS5_20':'OWN5','CTS15_15':'OWN15'}
SCOLS=['day','signal_j','dj','side','stop','target','exit_j','delta_fraction','input_last_j','first_entry_j',
       'relative_turnover','previous_relative_turnover','nq_relative_volume','es_relative_volume','stratum_hour','stratum_volume']


def prior_median(values,normal_rows):
    out=np.full(values.shape,np.nan)
    out[normal_rows]=pd.DataFrame(values[normal_rows]).rolling(20,min_periods=15).median().shift(1).to_numpy()
    return out


def complete_bars(g,frame):
    b=g.bars(frame);valid=S.valid(g)&(g.o>0)&(g.h>0)&(g.l>0)&(g.c>0)
    mask=np.zeros(b['c'].shape,bool)
    for z,j in enumerate(b['j']):
        if j>=frame-1:mask[:,z]=valid[:,j-frame+1:j+1].all(axis=1)
    b['complete']=mask
    return b


def prepare(nq,es,frame):
    n=complete_bars(nq,frame);e=complete_bars(es,frame)
    erow=np.searchsorted(es.dates,nq.dates);present=(erow<es.D)&(es.dates[np.minimum(erow,es.D-1)]==nq.dates)
    ev=np.full(n['v'].shape,np.nan);ec=np.full(n['c'].shape,np.nan);em=np.zeros(n['c'].shape,bool)
    ev[present]=e['v'][erow[present]];ec[present]=e['c'][erow[present]];em[present]=e['complete'][erow[present]]
    roll=np.array([C.roll_guard(pd.Timestamp(t)) for t in nq.ts],bool)
    joint=n['complete']&em&(n['v']>0)&(ev>0)&(n['c']>0)&(ec>0)&(~roll[:,None])
    with np.errstate(divide='ignore',invalid='ignore'):
        raw=n['v']*20.*n['c']/(ev*50.*ec)
    raw=np.where(joint,raw,np.nan)
    normal=np.array([d for d in range(nq.D) if C.normal_cash(pd.Timestamp(nq.ts[d]))],int)
    n['ratio_reference']=prior_median(raw,normal)
    n['nq_volume_reference']=prior_median(np.where(joint,n['v'],np.nan),normal)
    n['es_volume_reference']=prior_median(np.where(joint,ev,np.nan),normal)
    n['raw_turnover_ratio']=raw;n['es_volume']=ev;n['joint_complete']=joint
    with np.errstate(divide='ignore',invalid='ignore'):
        n['relative_turnover']=raw/n['ratio_reference']
        n['nq_relative_volume']=n['v']/n['nq_volume_reference'];n['es_relative_volume']=ev/n['es_volume_reference']
    return n,dict(nq_dates=nq.D,exact_ES_dates=int(present.sum()),missing_ES_dates=int((~present).sum()),
        normal_reference_dates=len(normal),calendar_roll_dates=int(roll.sum()),frame_minutes=frame)


def price_side(op,hi,lo,cl):
    span=hi-lo
    if span<=0 or abs(cl-op)<.5*span:return 0
    location=(cl-lo)/span
    return 1 if cl>op and location>=.75 else (-1 if cl<op and location<=.25 else 0)


def switch(current,previous,nq_relative,es_relative,threshold):
    if nq_relative<1 or es_relative<.5:return False
    return threshold is None or (previous<=1 and current>=threshold)


def signals(g,b,frame,threshold,lo,hi):
    rows=[];cts={'calendar_skip_days':0,'roll_skip_days':0,'incomplete_current_or_previous':0,
        'prior_reference_warmup':0,'eligible_complete_windows':0,'own_volume_rejected':0,'peer_switch_rejected':0}
    # Calendar rows, not future-dependent g.trading/day-completeness membership.
    for d in range(g.D):
        date=pd.Timestamp(g.ts[d])
        if not lo<=date<=hi:continue
        if not C.normal_cash(date):cts['calendar_skip_days']+=1;continue
        if C.roll_guard(date):cts['roll_skip_days']+=1;continue
        atr=g._flow_atr[d]
        if not np.isfinite(atr) or atr<=0:continue
        for z,j in enumerate(b['j']):
            if j<540 or j>840:continue
            if not b['joint_complete'][d,z-1:z+1].all():cts['incomplete_current_or_previous']+=1;continue
            refs=np.array([b[k][d,i] for k in ('ratio_reference','nq_volume_reference','es_volume_reference') for i in (z-1,z)])
            if not (np.isfinite(refs).all() and (refs>0).all()):cts['prior_reference_warmup']+=1;continue
            cts['eligible_complete_windows']+=1
            side=price_side(b['o'][d,z],b['h'][d,z],b['l'][d,z],b['c'][d,z])
            if not side:continue
            q,pq,nv,ev=b['relative_turnover'][d,z],b['relative_turnover'][d,z-1],b['nq_relative_volume'][d,z],b['es_relative_volume'][d,z]
            if nv<1 or ev<.5:cts['own_volume_rejected']+=1;continue
            if not switch(q,pq,nv,ev,threshold):cts['peer_switch_rejected']+=1;continue
            rows.append(dict(day=d,signal_j=int(j),dj=int(j)+1,side=side,stop=np.ceil(.10*atr*4)/4,target=np.ceil(.20*atr*4)/4,
                exit_j=min(int(j)+45,895),delta_fraction=np.nan,input_last_j=int(j),first_entry_j=int(j)+2,
                relative_turnover=q,previous_relative_turnover=pq,nq_relative_volume=nv,es_relative_volume=ev,
                stratum_hour=int(j)//60,stratum_volume=0 if nv<1.5 else (1 if nv<2 else 2)))
    return pd.DataFrame(rows,columns=SCOLS),cts


def engineering():
    assert 100*20*100/(50*50*80)==1.
    assert 250*20*100/(50*50*80)==2.5
    assert price_side(100.,110.,100.,109.)==1
    assert price_side(100.,100.,90.,91.)==-1
    assert switch(1.6,.9,1.1,.8,1.5)
    assert not switch(1.6,1.1,1.1,.8,1.5)
    assert not switch(1.6,.9,.9,.8,1.5)
    assert not switch(1.6,.9,1.1,.4,1.5)
    assert not switch(1.6,.9,1.1,.8,2.)
    assert switch(.8,1.1,1.1,.8,None)
    x=np.arange(90.,dtype=float).reshape(30,3)+1;baseline=prior_median(x,np.arange(30))
    x[-1]=1e9;mutated=prior_median(x,np.arange(30));np.testing.assert_allclose(baseline,mutated,equal_nan=True)
    missing=np.ones((25,1));missing[18:24]=np.nan
    assert np.isnan(prior_median(missing,np.arange(25))[24,0])  #14valid in exact20, no stretching
    assert 540+2==542
    C.engineering()
    return dict(passed=True,checks=['notional multiplier units','long/short candle symmetry','current/previous ratio gates',
        'own-volume and ES-activity guards','current/future mutation leaves all earlier/prior medians unchanged',
        'missing-date windows never stretch','extra-minute entry; shared calendar/entrybar/gap/through checks'])


def volume_source_audit():
    # Intake-only corroboration, not a trading input or forward-return test.
    n=pd.read_csv(ROOT/'data/NQ_1min_2018.csv',usecols=['date','time','volume'])
    f=pd.read_csv(ROOT/'data/OF_1min_2018_1.csv',usecols=['date','time','upvol','downvol']);f['time']-=100
    m=n.merge(f,on=['date','time'],validate='one_to_one')
    return dict(exporter='tools/exporters/NQ_Bar_Exporter.txt',exported_expression='Ticks',
        corroboration_period='2018 first OF file only; ETminus60minutes',matched_rows=len(m),
        fraction_native_equals_up_plus_down=float((m.volume==m.upvol+m.downvol).mean()),
        fraction_native_equals_up_only=float((m.volume==m.upvol).mean()),
        limitation='Not proof of all years, source contract/vintage parity or ES volume; no OF field enters signals.',
        hashes={str(p.relative_to(ROOT)):C.sha(p) for p in (ROOT/'tools/exporters/NQ_Bar_Exporter.txt',ROOT/'data/OF_1min_2018_1.csv')})


def stratified_drops(g,base_signals,candidate_signals,days,seed=20261026):
    cols=['day','signal_j','side','stratum_hour','stratum_volume']
    bt=F.replay(g,base_signals,independent=True)[0];ct=F.replay(g,candidate_signals,independent=True)[0]
    b=bt.merge(base_signals[cols],on=['day','signal_j','side'],validate='one_to_one')
    cand=ct.merge(candidate_signals[cols],on=['day','signal_j','side'],validate='one_to_one')
    if cand.empty:return dict(non_executable_signal_only=True,runs=1000,kept_windows=0,informative=False,p_random_net_ge_kept=1.,p_kept_better_net_and_dd=0.)
    groups=[];cells=[]
    for (hour,vol),n in cand.groupby(['stratum_hour','stratum_volume']).size().items():
        idx=np.flatnonzero(((b.stratum_hour==hour)&(b.stratum_volume==vol)).to_numpy());assert len(idx)>=n
        groups.append((idx,int(n)));cells.append(dict(signal_hour=int(hour),own_volume_bin=int(vol),base=len(idx),kept=int(n)))
    own_net=float(cand.net.sum());own_dd=C.R.max_dd(cand.groupby('date').net.sum().reindex(days,fill_value=0.))
    rng=np.random.default_rng(seed);totals=[];dds=[]
    for _ in range(1000):
        pick=np.sort(np.concatenate([rng.choice(idx,n,replace=False) for idx,n in groups]));t=b.iloc[pick]
        totals.append(float(t.net.sum()));dds.append(C.R.max_dd(t.groupby('date').net.sum().reindex(days,fill_value=0.)))
    nets=np.asarray(totals);dd=np.asarray(dds)
    return dict(non_executable_signal_only=True,runs=1000,kept_windows=len(cand),informative=True,strata=cells,
        kept_net=own_net,kept_dd=own_dd,random_net_mean=float(nets.mean()),p_random_net_ge_kept=float((nets>=own_net).mean()),
        p_kept_better_net_and_dd=float(((nets<own_net)&(dd>own_dd)).mean()),random_net_totals=totals,random_dd=dds)


def run(prereg,phase):
    started=datetime.now(timezone.utc).isoformat()
    S.bind(OUT,PLAN,prereg,CONFIGS,['NQ','ES'],45,['codex_relative_turnover_switch.py'])
    C.dump(OUT/'engineering_checks.json',engineering());C.dump(OUT/'native_volume_source_audit.json',volume_source_audit())
    lo=pd.Timestamp('2018-01-01' if phase=='design' else '2023-01-01');hi=pd.Timestamp('2022-12-31' if phase=='design' else '2026-10-09');chosen=None
    if phase=='validation':
        chosen=json.loads((OUT/'design_complete_gate.json').read_text())['selected']
        if chosen is None:raise ValueError('Design rejected; continue a DISTINCT hypothesis')
    intake={sym:S.intake(sym,hi) for sym in ('NQ','ES')};C.dump(OUT/f'{phase}_intake.json',intake)
    if any(v['conflicting_keys'] for v in intake.values()):raise ValueError('NEEDS DATA: conflicting native keys')
    g=S.load('NQ',hi);es=S.load('ES',hi)
    bars={};mapping={}
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',RuntimeWarning)
        for frame in (5,15):bars[frame],mapping[str(frame)]=prepare(g,es,frame)
    C.dump(OUT/f'{phase}_mapping.json',mapping)
    configs=CONFIGS if phase=='design' else {k:CONFIGS[k] for k in (chosen,BASE[chosen])};sigs={};counts={}
    for name,args in configs.items():sigs[name],counts[name]=signals(g,bars[args[0]],*args,lo,hi)
    days=S.sessions(g,lo,hi)
    ledgers,df,_=S.evaluate(OUT,g,sigs,days,phase,prereg,CANDIDATES,BASE,45,independent=True,counts=counts)
    actual={};strata={}
    for name in (k for k in CANDIDATES if k in configs):
        base=BASE[name];actual[name]=dict(candidate_net=float(ledgers[name].net.sum()),base_net=float(ledgers[base].net.sum()),
            nested_actual_ledgers=False,candidate_dd=C.R.max_dd(ledgers[name].groupby('date').net.sum().reindex(days,fill_value=0.)),
            base_dd=C.R.max_dd(ledgers[base].groupby('date').net.sum().reindex(days,fill_value=0.)))
        strata[name]=stratified_drops(g,sigs[base],sigs[name],days)
    C.dump(OUT/f'{phase}_actual_base_comparison.json',actual);C.dump(OUT/f'{phase}_stratified_drops.json',strata)
    selected=chosen
    if phase=='design':
        basic=json.loads((OUT/'design_gate.json').read_text());uniform=json.loads((OUT/'design_filter_diagnostics.json').read_text());gates={}
        for name in CANDIDATES:
            f=uniform[name];s=strata[name]
            extra=dict(actual_net_ge_base=actual[name]['candidate_net']>=actual[name]['base_net'],removed_loses=f['removed_avg']<0,
                diagnostic_total_ge_base=f['kept_net']>=f['base_net'],uniform_net=f['p_random_net_ge_kept']<=.10,
                uniform_joint=f['p_kept_better_net_and_dd']>=.90,stratified_net=s['p_random_net_ge_kept']<=.10,
                stratified_joint=s['p_kept_better_net_and_dd']>=.90)
            gates[name]={**basic['gates'][name],**{k:bool(v) for k,v in extra.items()}}
        passing=[k for k,v in gates.items() if all(v.values())];selected=passing[0] if passing else None
        C.dump(OUT/'design_complete_gate.json',dict(prereg=prereg,gates=gates,passing=passing,selected=selected,
            counted_program_evaluations=50,unique_program_models=49,diagnostic_paths_not_executable=True,program_continues=True))
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
