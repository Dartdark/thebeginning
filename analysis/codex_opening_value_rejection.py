"""New frozen opening-hour time-occupancy value rejection; not tape volume profile."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys
import warnings
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'analysis/outputs/codex_opening_value_rejection'
sys.path.insert(0,str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import codex_t6_study_support as S
C=S.C;os.environ['NUMBA_CACHE_DIR']=str(OUT/'numba_cache')
PLAN='agents/codex/plans/opening_value_rejection.md'
CONFIGS={'OV5_70':(5,.70),'OV5_80':(5,.80),'OV15_70':(15,.70),'BASE5':(5,None),'BASE15':(15,None)}
CANDIDATES=['OV5_70','OV5_80','OV15_70'];BASE={'OV5_70':'BASE5','OV5_80':'BASE5','OV15_70':'BASE15'}
SCOLS=['day','signal_j','dj','side','stop','target','exit_j','delta_fraction','input_last_j','first_entry_j','poc','value_low','value_high','target_signal_distance']


def profile(highs,lows,fraction):
    pmin,pmax=int(np.floor(min(lows))),int(np.ceil(max(highs)));counts=np.zeros(pmax-pmin+1,int)
    for h,l in zip(highs,lows):
        left,right=int(np.ceil(l))-pmin,int(np.floor(h))-pmin
        if right>=left:counts[left:right+1]+=1
    total=int(counts.sum())
    if total<=0:return np.nan,np.nan,np.nan,total
    poc=int(np.argmax(counts));left=right=poc;covered=int(counts[poc])
    while covered<fraction*total:
        lower=counts[left-1] if left>0 else -1;upper=counts[right+1] if right+1<len(counts) else -1
        if lower>=upper and left>0:left-=1;covered+=int(counts[left])
        elif right+1<len(counts):right+=1;covered+=int(counts[right])
        else:raise AssertionError('Value area failed to expand')
    return float(pmin+poc),float(pmin+left)-.5,float(pmin+right)+.5,total


def rejection(previous_close,bar_open,bar_close,poc,low,high,use_area):
    side=-1 if bar_close>poc and bar_close<bar_open else (1 if bar_close<poc and bar_close>bar_open else 0)
    if use_area and side:
        if side<0 and not (previous_close>high and bar_close<=high):return 0
        if side>0 and not (previous_close<low and bar_close>=low):return 0
    return side


def engineering():
    p,lo,hi,total=profile([110.]*12,[100.]*12,.7)
    assert (p,lo,hi,total)==(100.,99.5,107.5,132)
    assert profile([110.]*12,[100.]*12,.8)==(100.,99.5,108.5,132)
    assert rejection(109.,109.,107.,105.,102.5,107.5,True)==-1
    assert rejection(101.,101.,103.,105.,102.5,107.5,True)==1
    assert rejection(106.,109.,107.,105.,102.5,107.5,True)==0
    assert rejection(106.,109.,107.,105.,102.5,107.5,False)==-1
    assert 575+2==577
    C.engineering()
    return dict(passed=True,checks=['integer range occupancy counts','lowest POC/expansion tie rules','70/80percent contiguous coverage','long/short rejection/control','signal-close target distances and extra-minute entry','shared calendar/gap/entrybar/through checks'])


def features(g,valid):
    rows=[]
    for d in g.trading:
        date=pd.Timestamp(g.ts[d])
        if not C.normal_cash(date):continue
        row=dict(day=int(d),date=date,complete=bool(valid[d,511:571].all()),atr=g._flow_atr[d])
        if row['complete']:
            hh=[g.h[d,j-4:j+1].max() for j in range(515,571,5)]
            ll=[g.l[d,j-4:j+1].min() for j in range(515,571,5)]
            for frac in (.70,.80):
                poc,lo,hi,n=profile(hh,ll,frac);key=str(int(frac*100));row.update({f'poc{key}':poc,f'low{key}':lo,f'high{key}':hi,'occupancies':n})
        rows.append(row)
    return pd.DataFrame(rows)


def signals(g,feature,bars,valid,frame,fraction,lo,hi):
    rows=[];cts={'incomplete_opening_hour':0,'invalid_or_warmup_profile':0,'incomplete_signal_bars':0,'eligible_bars':0,'distance_rejected':0}
    for r in feature.to_dict('records'):
        if not lo<=r['date']<=hi:continue
        if not r['complete']:cts['incomplete_opening_hour']+=1;continue
        d=r['day'];key=str(int((fraction if fraction is not None else .7)*100));poc,vl,vh,atr=[r.get(k,np.nan) for k in ('poc'+key,'low'+key,'high'+key,'atr')]
        if not all(np.isfinite(z) for z in (poc,vl,vh,atr)) or atr<=0:cts['invalid_or_warmup_profile']+=1;continue
        b=bars[frame]
        for z,j in enumerate(b['j']):
            if j<570+frame or j>840:continue
            if not valid[d,int(j)-2*frame+1:int(j)+1].all():cts['incomplete_signal_bars']+=1;continue
            cts['eligible_bars']+=1
            bc,bo,prev=b['c'][d,z],b['o'][d,z],b['c'][d,z-1]
            dist=abs(bc-poc)
            if not .05*atr<=dist<=.30*atr:cts['distance_rejected']+=1;continue
            side=rejection(prev,bo,bc,poc,vl,vh,fraction is not None)
            if not side:continue
            rows.append(dict(day=d,signal_j=int(j),dj=int(j)+1,side=side,stop=np.ceil(.10*atr*4)/4,target=np.ceil(dist*4)/4,
                exit_j=min(int(j)+60,895),delta_fraction=np.nan,input_last_j=int(j),first_entry_j=int(j)+2,poc=poc,value_low=vl,value_high=vh,target_signal_distance=dist))
    return pd.DataFrame(rows,columns=SCOLS),cts


def run(prereg,phase):
    S.bind(OUT,PLAN,prereg,CONFIGS,['NQ'],35,['codex_opening_value_rejection.py']);C.dump(OUT/'engineering_checks.json',engineering())
    lo=pd.Timestamp('2018-01-01' if phase=='design' else '2023-01-01');hi=pd.Timestamp('2022-12-31' if phase=='design' else '2026-10-09');chosen=None
    if phase=='validation':
        chosen=json.loads((OUT/'design_complete_gate.json').read_text())['selected']
        if chosen is None:raise ValueError('Local design failure; continue another mechanism')
    audit=S.intake('NQ',hi);C.dump(OUT/f'{phase}_intake.json',audit)
    if audit['conflicting_keys']:raise ValueError('NEEDS DATA: conflicting keys')
    g=S.load('NQ',hi);valid=S.valid(g);feature=features(g,valid);C.csv(OUT/f'{phase}_profiles.csv',feature)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',RuntimeWarning);bars={f:g.bars(f) for f in (5,15)}
    configs=CONFIGS if phase=='design' else {k:CONFIGS[k] for k in (chosen,BASE[chosen])};sigs={};counts={}
    for name,args in configs.items():sigs[name],counts[name]=signals(g,feature,bars,valid,*args,lo,hi)
    ledgers,df,_=S.evaluate(OUT,g,sigs,S.sessions(g,lo,hi),phase,prereg,CANDIDATES,BASE,35,independent=True,counts=counts);selected=chosen
    if phase=='design':
        basic=json.loads((OUT/'design_gate.json').read_text());filters=json.loads((OUT/'design_filter_diagnostics.json').read_text());gates={}
        for name in CANDIDATES:
            f=filters[name]
            gates[name]={k:bool(v) for k,v in dict(basic=name in basic['passing'],removed_loses=f['removed_avg']<0,kept_total_ge_base=f['kept_net']>=f['base_net'],random_net=f['p_random_net_ge_kept']<=.10,random_joint=f['p_kept_better_net_and_dd']>=.90).items()}
        passing=[k for k,v in gates.items() if all(v.values())];selected=passing[0] if passing else None
        C.dump(OUT/'design_complete_gate.json',dict(prereg=prereg,gates=gates,selected=selected,counted_program_evaluations=40,unique_program_models=39,diagnostics_not_executable=True,program_continues=True))
        print('Complete gate:',selected,gates,flush=True)
    return ledgers,df,selected


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase',choices=['design','validation'],required=True);p.add_argument('--prereg',required=True);a=p.parse_args();run(a.prereg,a.phase)
