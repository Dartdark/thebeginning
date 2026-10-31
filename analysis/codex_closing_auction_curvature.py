"""Standalone cash-closing-auction curvature shock; signal1/5min, delayedmarket entry."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'analysis/outputs/codex_closing_auction_curvature'
sys.path.insert(0,str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import codex_t6_study_support as S
C=S.C;os.environ['NUMBA_CACHE_DIR']=str(OUT/'numba_cache')
PLAN='agents/codex/plans/closing_auction_curvature.md'
CONFIGS={'AC1_K2':(1,2.),'AC1_K3':(1,3.),'AC5_K2':(5,2.),'BASE1':(1,None),'BASE5':(5,None)}
CANDIDATES=['AC1_K2','AC1_K3','AC5_K2'];BASE={'AC1_K2':'BASE1','AC1_K3':'BASE1','AC5_K2':'BASE5'}
SCOLS=['day','signal_j','dj','side','stop','target','exit_j','delta_fraction','input_last_j','first_entry_j','curvature','shock_ratio','volume_ratio']


def curvature(prices,frame):
    if frame==1:return (prices[-1]-prices[-2])-(prices[-2]-prices[-7])/5.
    return (prices[-1]-prices[-6])-(prices[-6]-prices[-11])


def engineering():
    prices=np.arange(16.)
    assert curvature(prices,1)==0 and curvature(prices,5)==0
    prices[-1]+=5
    assert curvature(prices,1)==5 and curvature(prices,5)==5
    assert curvature(-prices,1)==-5 and curvature(-prices,5)==-5
    # Curvature may oppose a positive lastbar move (deceleration), unlike a lastbar fade.
    x=np.arange(16.)*2;x[-1]=x[-2]+1
    assert x[-1]>x[-2] and curvature(x,1)<0
    C.engineering()
    return dict(passed=True,checks=['constant pace has zero shock','acceleration/short mirrors','deceleration distinct from lastbar sign','extra minute delay','calendar and shared entrybar/gap/through checks'])


def features(g):
    valid=S.valid(g);eligible=[d for d in range(g.D) if C.normal_cash(pd.Timestamp(g.ts[d]))];rows=[]
    for d in eligible:
        good=bool(valid[d,885:901].all());row=dict(day=d,date=pd.Timestamp(g.ts[d]),complete=good,atr=g._flow_atr[d])
        for frame in (1,5):
            row[f'curve{frame}']=curvature(g.c[d,885:901],frame) if good else np.nan
            row[f'volume{frame}']=g.v[d,901-frame:901].sum() if good else np.nan
        rows.append(row)
    f=pd.DataFrame(rows)
    for frame in (1,5):
        f[f'prior_curve{frame}']=f[f'curve{frame}'].abs().rolling(20,min_periods=15).median().shift(1)
        f[f'prior_volume{frame}']=f[f'volume{frame}'].rolling(20,min_periods=15).median().shift(1)
    return f


def signals(feature,frame,k,lo,hi):
    rows=[];cts={'incomplete_window':0,'prior_feature_warmup':0,'eligible_days':0,'shock_or_volume_rejected':0}
    for r in feature.to_dict('records'):
        if not lo<=r['date']<=hi:continue
        if not r['complete']:cts['incomplete_window']+=1;continue
        curve,pc,pv,vol,atr=[r[s] for s in (f'curve{frame}',f'prior_curve{frame}',f'prior_volume{frame}',f'volume{frame}','atr')]
        if not all(np.isfinite(z) for z in (curve,pc,pv,vol,atr)) or min(pc,pv,atr)<=0:cts['prior_feature_warmup']+=1;continue
        cts['eligible_days']+=1
        side=-int(np.sign(curve))
        if not side:continue
        if k is not None and (abs(curve)<k*pc or vol<1.5*pv):cts['shock_or_volume_rejected']+=1;continue
        rows.append(dict(day=r['day'],signal_j=900,dj=901,side=side,stop=np.ceil(.05*atr*4)/4,target=np.ceil(.10*atr*4)/4,
            exit_j=914,delta_fraction=np.nan,input_last_j=900,first_entry_j=902,curvature=curve,shock_ratio=abs(curve)/pc,volume_ratio=vol/pv))
    return pd.DataFrame(rows,columns=SCOLS),cts


def run(prereg,phase):
    S.bind(OUT,PLAN,prereg,CONFIGS,['NQ'],30,['codex_closing_auction_curvature.py']);C.dump(OUT/'engineering_checks.json',engineering())
    lo=pd.Timestamp('2018-01-01' if phase=='design' else '2023-01-01');hi=pd.Timestamp('2022-12-31' if phase=='design' else '2026-10-09')
    chosen=None
    if phase=='validation':
        chosen=json.loads((OUT/'design_complete_gate.json').read_text())['selected']
        if chosen is None:raise ValueError('Local design stop, continue distinct mechanism')
    audit=S.intake('NQ',hi);C.dump(OUT/f'{phase}_intake.json',audit)
    if audit['conflicting_keys']:raise ValueError('NEEDS DATA: conflicting keys')
    g=S.load('NQ',hi);feature=features(g);C.csv(OUT/f'{phase}_features.csv',feature)
    configs=CONFIGS if phase=='design' else {k:CONFIGS[k] for k in (chosen,BASE[chosen])};sigs={};counts={}
    for name,args in configs.items():sigs[name],counts[name]=signals(feature,*args,lo,hi)
    ledgers,df,_=S.evaluate(OUT,g,sigs,S.sessions(g,lo,hi),phase,prereg,CANDIDATES,BASE,30,counts=counts)
    selected=chosen
    if phase=='design':
        basic=json.loads((OUT/'design_gate.json').read_text());filters=json.loads((OUT/'design_filter_diagnostics.json').read_text());gates={}
        for name in CANDIDATES:
            f=filters[name]
            gates[name]={k:bool(v) for k,v in dict(basic=name in basic['passing'],removed_loses=f['removed_avg']<0,kept_total_ge_base=f['kept_net']>=f['base_net'],random_net=f['p_random_net_ge_kept']<=.10,random_joint=f['p_kept_better_net_and_dd']>=.90).items()}
        passing=[k for k,v in gates.items() if all(v.values())];selected=passing[0] if passing else None
        C.dump(OUT/'design_complete_gate.json',dict(prereg=prereg,gates=gates,selected=selected,counted_program_evaluations=35,unique_program_models=34,program_continues=True))
        print('Complete gate:',selected,gates,flush=True)
    return ledgers,df,selected


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase',choices=['design','validation'],required=True);p.add_argument('--prereg',required=True);a=p.parse_args();run(a.prereg,a.phase)
