"""Frozen standalone three-bar participation/resumption study; no old trade inputs."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import warnings
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_participation_resumption'
sys.path.insert(0,str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import codex_cash_open_repair as C
import codex_flow_absorption as F
from grid24 import Grid24
os.environ['NUMBA_CACHE_DIR']=str(OUT/'numba_cache')
PLAN='agents/codex/plans/participation_resumption.md'
CONFIGS={'P5_V15':(5,1.5),'P5_V20':(5,2.),'P15_V15':(15,1.5),'PRICE5':(5,None),'PRICE15':(15,None)}
SIGNAL_COLS=['day','signal_j','dj','side','stop','target','exit_j','delta_fraction','input_last_j','first_entry_j','volume_ratio','pullback_volume_ratio']


def bind(prereg):
    assert subprocess.check_output(['git','show',prereg+':'+PLAN],cwd=ROOT)==(ROOT/PLAN).read_bytes()
    assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='codex/work'
    paths=sorted((ROOT/'data').glob('NQ_1min_*.csv'))+[ROOT/PLAN]+[ROOT/'analysis'/p for p in ('grid.py','grid24.py','metrics.py','codex_cash_open_repair.py','codex_flow_absorption.py','codex_s03_calendar.py')]
    C.dump(OUT/'input_binding.json',dict(prereg=prereg,source={str(p.relative_to(ROOT)):C.sha(p) for p in paths},models=CONFIGS,new_economic_models=5,prior_program_models=10))
    C.write(OUT/'.gitignore','numba_cache/\n')


def audit(cutoff,phase):
    paths=sorted(p for p in (ROOT/'data').glob('NQ_1min_*.csv') if int(p.stem.split('_')[-1])<=cutoff.year)
    raw=pd.concat([pd.read_csv(p) for p in paths],ignore_index=True)
    raw=raw[raw.date<=int(cutoff.strftime('%Y%m%d'))]
    fields=['open','high','low','close','volume'];dup=raw.duplicated(['date','time'],keep=False)
    conflicts=int((raw[dup].groupby(['date','time'])[fields].nunique(dropna=False)>1).any(axis=1).sum())
    report=dict(rows=len(raw),exact_duplicates=int(raw.duplicated().sum()),conflicting_keys=conflicts,clock='native CT minute close labels',future_returns_used=False)
    C.dump(OUT/f'{phase}_intake.json',report)
    if conflicts:raise ValueError('NEEDS DATA: native conflicting duplicates')


def bars(g,frame):
    b=g.bars(frame)
    valid=(np.isfinite(g.o)&np.isfinite(g.h)&np.isfinite(g.l)&np.isfinite(g.c)&np.isfinite(g.v)&(g.v>=0)
        &(g.h>=np.maximum(g.o,g.c))&(g.l<=np.minimum(g.o,g.c))&(g.h>=g.l))
    complete=np.zeros(b['c'].shape,bool)
    for z,j in enumerate(b['j']):
        if j>=frame-1:complete[:,z]=valid[:,j-frame+1:j+1].all(axis=1)
    b['complete']=complete
    eligible=np.array([d for d in range(g.D) if C.normal_cash(pd.Timestamp(g.ts[d]))],int)
    for key,val in (('prior_range',b['h']-b['l']),('prior_volume',b['v'])):
        a=np.full(val.shape,np.nan)
        # Exact prior20normal sessions, never extend past a missing session.
        x=pd.DataFrame(np.where(complete[eligible],val[eligible],np.nan))
        a[eligible]=x.rolling(20,min_periods=15).median().shift(1).to_numpy()
        b[key]=a
    return b


def pattern(a,b,c,range_median,volume_median,threshold):
    ao,ah,al,ac,av=a;bo,bh,bl,bc,bv=b;co,ch,cl,cc,cv=c
    ar,br,cr=ah-al,bh-bl,ch-cl
    if min(ar,br,cr)<=0 or not np.isfinite(range_median) or range_median<=0:return 0
    side=int(np.sign(ac-ao));location=(ac-al)/ar
    if not side or abs(ac-ao)<.6*ar or ar<1.5*range_median:return 0
    if (side>0 and location<.8) or (side<0 and location>.2):return 0
    if np.sign(bc-bo)!=-side or br>.6*ar:return 0
    midpoint=(ah+al)/2
    if (side>0 and bl<midpoint) or (side<0 and bh>midpoint):return 0
    if np.sign(cc-co)!=side or not (cc>bh if side>0 else cc<bl):return 0
    if threshold is not None:
        if not np.isfinite(volume_median) or volume_median<=0 or av<threshold*volume_median or bv>.5*av:return 0
    return side


def signals(g,b,frame,threshold,lo,hi):
    rows=[];counts={'calendar_skip_days':0,'incomplete_or_invalid_triplets':0,'prior_range_warmup':0,'prior_volume_warmup':0,'eligible_complete_triplets':0}
    for d in g.trading:
        date=pd.Timestamp(g.ts[d])
        if not lo<=date<=hi:continue
        if not C.normal_cash(date):counts['calendar_skip_days']+=1;continue
        atr=g._flow_atr[d]
        if not np.isfinite(atr) or atr<=0:continue
        for z,j in enumerate(b['j']):
            if j<540 or j>840 or j-3*frame+1<511:continue
            if not b['complete'][d,z-2:z+1].all():counts['incomplete_or_invalid_triplets']+=1;continue
            rm,vm=b['prior_range'][d,z-2],b['prior_volume'][d,z-2]
            if not np.isfinite(rm):counts['prior_range_warmup']+=1;continue
            # All models use identical prior-data eligibility, including controls.
            if not np.isfinite(vm) or vm<=0:counts['prior_volume_warmup']+=1;continue
            counts['eligible_complete_triplets']+=1
            a,bb,c=[tuple(b[k][d,i] for k in ('o','h','l','c','v')) for i in (z-2,z-1,z)]
            side=pattern(a,bb,c,rm,vm,threshold)
            if not side:continue
            rows.append(dict(day=int(d),signal_j=int(j),dj=int(j),side=side,stop=np.ceil(.10*atr*4)/4,target=np.ceil(.20*atr*4)/4,
                exit_j=min(int(j)+60,895),delta_fraction=np.nan,input_last_j=int(j),first_entry_j=int(j)+1,
                volume_ratio=a[4]/vm,pullback_volume_ratio=bb[4]/a[4] if a[4]>0 else np.nan))
    return pd.DataFrame(rows,columns=SIGNAL_COLS),counts


def engineering():
    a=(100.,110.,100.,109.,200.);b=(109.,109.,106.,107.,80.);c=(107.,112.,106.,111.,120.)
    assert pattern(a,b,c,5.,100.,1.5)==1
    reflect=lambda bar:(-bar[0],-bar[2],-bar[1],-bar[3],bar[4])
    assert pattern(reflect(a),reflect(b),reflect(c),5.,100.,1.5)==-1
    assert pattern(a,b,c,5.,150.,1.5)==0
    assert pattern(a,b,c,5.,150.,None)==1
    assert pattern(a,(109.,109.,106.,107.,120.),c,5.,100.,1.5)==0
    values=pd.DataFrame({'x':np.arange(30.)});prior=values.rolling(20,min_periods=15).median().shift(1)
    values.loc[29,'x']=1e9
    assert prior.loc[29,'x']==values.rolling(20,min_periods=15).median().shift(1).loc[29,'x']
    C.engineering()
    return dict(passed=True,checks=['three-bar long and mirrored short','prior-volume-gate/control','low-participation pullback','prior-only rolling median','cash calendar and shared execution synthetic checks'])


def run(prereg,phase):
    bind(prereg);C.dump(OUT/'engineering_checks.json',engineering())
    lo=pd.Timestamp('2018-01-01' if phase=='design' else '2023-01-01');hi=pd.Timestamp('2022-12-31' if phase=='design' else '2026-10-09')
    chosen=None
    if phase=='validation':
        chosen=json.loads((OUT/'design_gate.json').read_text())['selected']
        if chosen is None:raise ValueError('Local design stop; continue a distinct mechanism')
    audit(hi,phase)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',RuntimeWarning)
        g=C.trim_grid(Grid24(),hi);g._flow_atr=g.daily_atr(15)
        bs={f:bars(g,f) for f in (5,15)}
    days=pd.DatetimeIndex([pd.Timestamp(t) for t in g.ts if lo<=pd.Timestamp(t)<=hi and C.calendar_status(pd.Timestamp(t))['kind'] not in ('weekend','holiday')])
    configs=CONFIGS if chosen is None else {k:CONFIGS[k] for k in (chosen,'PRICE'+str(CONFIGS[chosen][0]))}
    ledgers={};sigs={};counts={};metrics=[];daily={};ind={}
    for name,(frame,threshold) in configs.items():
        s,ct=signals(g,bs[frame],frame,threshold,lo,hi);sigs[name]=s;t,ex=F.replay(g,s);ledgers[name]=t
        counts[name]=dict(input=ct,execution=ex,signals=len(s),executed=len(t))
        C.csv(OUT/f'{phase}_{name}_signals.csv',s);C.csv(OUT/f'{phase}_{name}_trades.csv',t)
        daily[name]=t.groupby('date').net.sum().reindex(days,fill_value=0.)
        for side,label in ((0,'all'),(1,'long'),(-1,'short')):
            tx=t if not side else t[t.side==side]
            for labelperiod,perioddays in [('2018-22' if phase=='design' else '2023+',days)]+[(str(y),days[days.year==y]) for y in sorted(days.year.unique())]:
                tt=tx if '-' in labelperiod or '+' in labelperiod else tx[tx.date.dt.year==int(labelperiod)]
                metrics.append(dict(model=name,period=labelperiod,side=label,**C.stats(tt,perioddays)))
    C.csv(OUT/f'{phase}_metrics.csv',pd.DataFrame(metrics));C.csv(OUT/f'{phase}_daily.csv',pd.DataFrame(daily).rename_axis('date'),index=True);C.dump(OUT/f'{phase}_counts.json',counts)
    filters={}
    for name in (k for k in configs if k.startswith('P') and not k.startswith('PRICE')):
        base='PRICE'+str(CONFIGS[name][0])
        if base not in ind:ind[base]=F.replay(g,sigs[base],independent=True)[0]
        cand=F.replay(g,sigs[name],independent=True)[0]
        filters[name]=dict(non_executable_signal_only=True,**C.filter_controls(cand,ind[base],days))
        C.csv(OUT/f'{phase}_{name}_independent_diagnostic.csv',cand[['day','j0','j1','side','date','net']])
    C.dump(OUT/f'{phase}_filter_diagnostics.json',filters)
    if phase=='design':
        gates={}
        for name in ('P5_V15','P5_V20','P15_V15'):
            t=ledgers[name];m=C.stats(t,days);yy=t.groupby(t.date.dt.year).net.sum()
            gates[name]={k:bool(v) for k,v in dict(count=len(t)>=100,net=m['total']>0,t=m['t_trade']>=2,nw5=m['t_nw5']>=1.5,pf=m['profit_factor']>=1.2,years=(yy>0).sum()>=4,micro=t.net_mnq.sum()>0,stress=t.stress_four_ticks.sum()>0).items()}
        passing=[k for k,v in gates.items() if all(v.values())]
        C.dump(OUT/'design_gate.json',dict(prereg=prereg,gates=gates,passing=passing,selected=passing[0] if passing else None,economic_models=5,cumulative_program_models=15,program_continues=True))
    df=pd.DataFrame(metrics);print(df[(df.period==('2018-22' if phase=='design' else '2023+'))&(df.side=='all')][['model','trades','total','avg','profit_factor','t_trade','t_nw5','max_dd']].to_string(index=False));print('Design pass:',passing if phase=='design' else chosen)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase',choices=['design','validation'],required=True);p.add_argument('--prereg',required=True);a=p.parse_args();run(a.prereg,a.phase)
