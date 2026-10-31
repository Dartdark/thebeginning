"""New overnight low-participation jump rejection; no old strategy return inputs."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys
import warnings
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'analysis/outputs/codex_liquidity_vacuum_refill'
sys.path.insert(0,str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import codex_t6_study_support as S
import codex_participation_resumption as V
C=S.C;os.environ['NUMBA_CACHE_DIR']=str(OUT/'numba_cache')
PLAN='agents/codex/plans/liquidity_vacuum_refill.md'
CONFIGS={'LV5_R2':(5,2.,True),'LV5_R3':(5,3.,True),'LV15_R2':(15,2.,True),'PRICE5':(5,2.,False),'PRICE15':(15,2.,False)}
CANDIDATES=['LV5_R2','LV5_R3','LV15_R2'];BASE={'LV5_R2':'PRICE5','LV5_R3':'PRICE5','LV15_R2':'PRICE15'}
SCOLS=['day','signal_j','dj','side','stop','target','exit_j','delta_fraction','input_last_j','first_entry_j','volume_ratio','range_ratio']


def rejection(a,b,range_median,volume_median,multiple,use_volume):
    ao,ah,al,ac,av=a;bo,bh,bl,bc,bv=b
    ar=ah-al;br=bh-bl
    if ar<=0 or br<=0 or not np.isfinite(range_median) or range_median<=0:return 0
    direction=int(np.sign(ac-ao));location=(ac-al)/ar
    if not direction or abs(ac-ao)<.7*ar or ar<multiple*range_median:return 0
    if direction>0:
        if location<.8 or bh>ah+.25 or bc>=(bo) or bc>(ah+al)/2:return 0
    else:
        if location>.2 or bl<al-.25 or bc<=bo or bc<(ah+al)/2:return 0
    if use_volume and av>volume_median:return 0
    return -direction


def engineering():
    a=(100.,110.,100.,109.,80.);b=(109.,110.,102.,104.,100.)
    reflect=lambda z:(-z[0],-z[2],-z[1],-z[3],z[4])
    assert rejection(a,b,4.,100.,2.,True)==-1
    assert rejection(reflect(a),reflect(b),4.,100.,2.,True)==1
    assert rejection(a,b,4.,50.,2.,True)==0
    assert rejection(a,b,4.,50.,2.,False)==-1
    assert rejection(a,b,4.,100.,3.,True)==0
    assert rejection(a,(109.,110.5,102.,104.,100.),4.,100.,2.,True)==0
    C.engineering()
    return dict(passed=True,checks=['up/down jump rejection mirrors','volume gate/control','range multiple and extension rejection','shared calendar/entrybar/gap/fill-through checks'])


def signals(g,b,frame,multiple,use_volume,lo,hi,valid):
    rows=[];cts={'calendar_skip_days':0,'incomplete_input_windows':0,'prior_feature_warmup':0,'eligible_complete_windows':0}
    for d in g.trading:
        date=pd.Timestamp(g.ts[d])
        if not lo<=date<=hi:continue
        if not C.normal_cash(date):cts['calendar_skip_days']+=1;continue
        atr=g._flow_atr[d]
        if not np.isfinite(atr) or atr<=0:continue
        for z,j in enumerate(b['j']):
            if j<60 or j>390:continue
            first=int(j)-2*frame+1
            if not valid[d,first-30:int(j)+1].all():cts['incomplete_input_windows']+=1;continue
            rm,vm=b['prior_range'][d,z-1],b['prior_volume'][d,z-1]
            if not np.isfinite(rm) or rm<=0 or not np.isfinite(vm) or vm<=0:cts['prior_feature_warmup']+=1;continue
            cts['eligible_complete_windows']+=1
            a,bb=[tuple(b[k][d,i] for k in ('o','h','l','c','v')) for i in (z-1,z)]
            side=rejection(a,bb,rm,vm,multiple,use_volume)
            if not side:continue
            rows.append(dict(day=int(d),signal_j=int(j),dj=int(j),side=side,stop=np.ceil(.08*atr*4)/4,target=np.ceil(.12*atr*4)/4,
                exit_j=min(int(j)+30,445),delta_fraction=np.nan,input_last_j=int(j),first_entry_j=int(j)+1,volume_ratio=a[4]/vm,range_ratio=(a[1]-a[2])/rm))
    return pd.DataFrame(rows,columns=SCOLS),cts


def run(prereg,phase):
    S.bind(OUT,PLAN,prereg,CONFIGS,['NQ'],25,['codex_participation_resumption.py','codex_liquidity_vacuum_refill.py'])
    C.dump(OUT/'engineering_checks.json',engineering());lo=pd.Timestamp('2018-01-01' if phase=='design' else '2023-01-01');hi=pd.Timestamp('2022-12-31' if phase=='design' else '2026-10-09')
    chosen=None
    if phase=='validation':
        chosen=json.loads((OUT/'design_complete_gate.json').read_text())['selected']
        if chosen is None:raise ValueError('Local gate failed; continue a distinct mechanism')
    audit=S.intake('NQ',hi);C.dump(OUT/f'{phase}_intake.json',audit)
    if audit['conflicting_keys']:raise ValueError('NEEDS DATA: conflicting keys')
    g=S.load('NQ',hi);valid=S.valid(g)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',RuntimeWarning);bars={f:V.bars(g,f) for f in (5,15)}
    configs=CONFIGS if phase=='design' else {k:CONFIGS[k] for k in (chosen,BASE[chosen])};sigs={};counts={}
    for name,args in configs.items():sigs[name],counts[name]=signals(g,bars[args[0]],*args,lo,hi,valid)
    ledgers,df,_=S.evaluate(OUT,g,sigs,S.sessions(g,lo,hi),phase,prereg,CANDIDATES,BASE,25,independent=True,counts=counts)
    selected=chosen
    if phase=='design':
        basic=json.loads((OUT/'design_gate.json').read_text());filters=json.loads((OUT/'design_filter_diagnostics.json').read_text());gates={}
        for name in CANDIDATES:
            f=filters[name]
            gates[name]={k:bool(v) for k,v in dict(basic=name in basic['passing'],removed_loses=f['removed_avg']<0,kept_total_ge_base=f['kept_net']>=f['base_net'],random_net=f['p_random_net_ge_kept']<=.10,random_joint=f['p_kept_better_net_and_dd']>=.90).items()}
        passing=[k for k,v in gates.items() if all(v.values())];selected=passing[0] if passing else None
        C.dump(OUT/'design_complete_gate.json',dict(prereg=prereg,gates=gates,selected=selected,counted_program_evaluations=30,unique_program_models=29,independent_diagnostics_not_executable=True,program_continues=True))
        print('Complete gate:',selected,gates,flush=True)
    return ledgers,df,selected


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase',choices=['design','validation'],required=True);p.add_argument('--prereg',required=True);a=p.parse_args();run(a.prereg,a.phase)
