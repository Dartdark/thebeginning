"""New standalone cross-index opening path consensus; not old strategy tickets."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'analysis/outputs/codex_opening_pressure'
sys.path.insert(0,str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import codex_t6_study_support as S
C=S.C;os.environ['NUMBA_CACHE_DIR']=str(OUT/'numba_cache')
PLAN='agents/codex/plans/opening_pressure.md'
CONFIGS={'CP5':(5,.15,True),'CP15':(15,.15,True),'CP5_HI':(5,.30,True),'OWN5':(5,.15,False),'OWN15':(15,.15,False)}
CANDIDATES=['CP5','CP15','CP5_HI'];BASE={'CP5':'OWN5','CP15':'OWN15','CP5_HI':'OWN5'}
SCOLS=['day','signal_j','dj','side','stop','target','exit_j','delta_fraction','input_last_j','first_entry_j']


def pressure(op,closes,atr):
    diff=np.diff(np.r_[op,closes]);net=closes[-1]-op;path=np.abs(diff).sum()
    return int(np.sign(net)),abs(net)/path if path>0 else 0.,abs(net)/atr if atr>0 else np.nan


def engineering():
    assert pressure(100.,np.array([101.,102.,103.]),10.)==(1,1.,.3)
    assert pressure(100.,np.array([99.,98.,97.]),10.)==(-1,1.,.3)
    assert pressure(100.,np.array([101.,99.,100.]),10.)==(0,0.,0.)
    C.engineering()
    return dict(passed=True,checks=['monotone long/short pressure','flat path rejection','shared clock/calendar/entrybar/gap/fill-through synthetic checks'])


def features(grids,lo,hi):
    nq=grids['NQ'];lookup={sym:{int(v):i for i,v in enumerate(g.dates)} for sym,g in grids.items()};valid={sym:S.valid(g) for sym,g in grids.items()}
    rows=[]
    for d in nq.trading:
        date=pd.Timestamp(nq.ts[d])
        if not lo<=date<=hi:continue
        row=dict(day=int(d),date=date,reason='eligible')
        if not C.normal_cash(date):row['reason']='calendar_skip'
        idx={sym:lookup[sym].get(int(nq.dates[d])) for sym in grids}
        if row['reason']=='eligible' and any(k is None for k in idx.values()):row['reason']='missing_symbol_date'
        if row['reason']=='eligible' and not all(valid[sym][idx[sym],511:541].all() for sym in grids):row['reason']='incomplete_open'
        if row['reason']=='eligible' and not all(np.isfinite(grids[sym]._flow_atr[idx[sym]]) and grids[sym]._flow_atr[idx[sym]]>0 for sym in grids):row['reason']='prior_ATR_warmup'
        if row['reason']=='eligible':
            for frame in (5,15):
                js=np.arange(510+frame,541,frame)
                for sym,g in grids.items():
                    side,eff,mv=pressure(g.o[idx[sym],511],g.c[idx[sym],js],g._flow_atr[idx[sym]])
                    row.update({f'{sym}{frame}_side':side,f'{sym}{frame}_eff':eff,f'{sym}{frame}_move':mv})
            row['atr']=nq._flow_atr[d]
        rows.append(row)
    return pd.DataFrame(rows)


def signal_rows(feature,frame,threshold,confirm):
    rows=[];counts=feature.reason.value_counts().to_dict()
    for r in feature.to_dict('records'):
        if r['reason']!='eligible':continue
        side=r[f'NQ{frame}_side']
        if not side or r[f'NQ{frame}_eff']<.50 or r[f'NQ{frame}_move']<threshold:continue
        if confirm and not all(r[f'{sym}{frame}_side']==side and r[f'{sym}{frame}_eff']>=.25 and r[f'{sym}{frame}_move']>=.05 for sym in ('ES','YM')):continue
        rows.append(dict(day=r['day'],signal_j=540,dj=540,side=side,stop=np.ceil(.15*r['atr']*4)/4,target=np.ceil(.60*r['atr']*4)/4,
            exit_j=895,delta_fraction=np.nan,input_last_j=540,first_entry_j=541))
    return pd.DataFrame(rows,columns=SCOLS),counts


def run(prereg,phase):
    S.bind(OUT,PLAN,prereg,CONFIGS,['NQ','ES','YM'],15,['codex_opening_pressure.py'])
    C.dump(OUT/'engineering_checks.json',engineering())
    lo=pd.Timestamp('2018-01-01' if phase=='design' else '2023-01-01');hi=pd.Timestamp('2022-12-31' if phase=='design' else '2026-10-09')
    chosen=None
    if phase=='validation':
        chosen=json.loads((OUT/'design_gate.json').read_text())['selected']
        if chosen is None:raise ValueError('Design rejected this hypothesis; do not validate')
    audit={sym:S.intake(sym,hi) for sym in ('NQ','ES','YM')};C.dump(OUT/f'{phase}_intake.json',audit)
    if any(a['conflicting_keys'] for a in audit.values()):raise ValueError('NEEDS DATA: conflicting keys')
    grids={sym:S.load(sym,hi) for sym in ('NQ','ES','YM')};feature=features(grids,lo,hi);C.csv(OUT/f'{phase}_features.csv',feature)
    configs=CONFIGS if phase=='design' else {k:CONFIGS[k] for k in (chosen,BASE[chosen])}
    signals={};counts={}
    for name,args in configs.items():signals[name],counts[name]=signal_rows(feature,*args)
    return S.evaluate(OUT,grids['NQ'],signals,S.sessions(grids['NQ'],lo,hi),phase,prereg,CANDIDATES,BASE,15,counts=counts)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase',choices=['design','validation'],required=True);p.add_argument('--prereg',required=True);a=p.parse_args();run(a.prereg,a.phase)
