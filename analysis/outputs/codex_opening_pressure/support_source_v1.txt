"""Shared audit/report helpers for committed standalone t6 studies; no entry rule."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import warnings
import numpy as np
import pandas as pd
import codex_cash_open_repair as C
import codex_flow_absorption as F
from grid24 import Grid24
ROOT=Path(__file__).resolve().parents[1]


def bind(out,plan,prereg,models,symbols,prior,modules):
    assert subprocess.check_output(['git','show',prereg+':'+plan],cwd=ROOT)==(ROOT/plan).read_bytes()
    assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='codex/work'
    paths=[]
    for symbol in symbols:paths+=sorted((ROOT/'data').glob(f'{symbol}_1min_*.csv'))
    paths+=[ROOT/plan]+[ROOT/'analysis'/p for p in ['grid.py','grid24.py','metrics.py','resampling.py','codex_cash_open_repair.py','codex_flow_absorption.py','codex_s03_calendar.py','codex_t6_study_support.py']+modules]
    C.dump(out/'input_binding.json',dict(prereg=prereg,source={str(p.relative_to(ROOT)):C.sha(p) for p in paths},models=models,new_economic_models=len(models),prior_program_models=prior))
    C.write(out/'.gitignore','numba_cache/\n')


def intake(symbol,hi):
    files=sorted(p for p in (ROOT/'data').glob(f'{symbol}_1min_*.csv') if int(p.stem.split('_')[-1])<=hi.year)
    raw=pd.concat([pd.read_csv(p) for p in files],ignore_index=True);raw=raw[raw.date<=int(hi.strftime('%Y%m%d'))]
    dup=raw.duplicated(['date','time'],keep=False)
    fields=['open','high','low','close','volume']
    conflict=int((raw[dup].groupby(['date','time'])[fields].nunique(dropna=False)>1).any(axis=1).sum())
    return dict(symbol=symbol,rows=len(raw),exact_duplicates=int(raw.duplicated().sum()),conflicting_keys=conflict,first=int(raw.date.min()),last=int(raw.date.max()),clock='native CT minute close labels')


def load(symbol,hi):
    # Restrict actual raw inputs to design years for the first stage.
    years='20[12][01289]' if hi.year==2022 else '20*'
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',RuntimeWarning)
        g=Grid24(f'data/{symbol}_1min_{years}.csv',night_pattern=f'data/NQ_1min_ON_{years}.csv' if symbol=='NQ' else '')
        g=C.trim_grid(g,hi);g._flow_atr=g.daily_atr(15)
    return g


def valid(g):
    return (np.isfinite(g.o)&np.isfinite(g.h)&np.isfinite(g.l)&np.isfinite(g.c)&np.isfinite(g.v)&(g.v>=0)
        &(g.h>=np.maximum(g.o,g.c))&(g.l<=np.minimum(g.o,g.c))&(g.h>=g.l))


def sessions(g,lo,hi):
    return pd.DatetimeIndex([pd.Timestamp(t) for t in g.ts if lo<=pd.Timestamp(t)<=hi and C.calendar_status(pd.Timestamp(t))['kind'] not in ('weekend','holiday')])


def evaluate(out,g,sigs,days,phase,prereg,candidates,base_map,prior,independent=False,counts=None):
    ledgers={};daily={};metrics=[];cts={} if counts is None else dict(counts)
    for name,s in sigs.items():
        t,ct=F.replay(g,s);ledgers[name]=t
        cts[name]=dict(input=cts.get(name,{}),execution=ct,signals=len(s),executed=len(t))
        C.csv(out/f'{phase}_{name}_signals.csv',s);C.csv(out/f'{phase}_{name}_trades.csv',t)
        daily[name]=t.groupby('date').net.sum().reindex(days,fill_value=0.)
        for side,label in ((0,'all'),(1,'long'),(-1,'short')):
            tx=t if not side else t[t.side==side]
            for period,ds in [('2018-22' if phase=='design' else '2023+',days)]+[(str(y),days[days.year==y]) for y in sorted(days.year.unique())]:
                tt=tx if '-' in period or '+' in period else tx[tx.date.dt.year==int(period)]
                metrics.append(dict(model=name,period=period,side=label,**C.stats(tt,ds)))
        for col in ('net_mnq','stress_four_ticks'):
            metrics.append(dict(model=name,period='2018-22' if phase=='design' else '2023+',side=col,**C.stats(t,days,column=col)))
    df=pd.DataFrame(metrics);C.csv(out/f'{phase}_metrics.csv',df)
    C.csv(out/f'{phase}_daily.csv',pd.DataFrame(daily).rename_axis('date'),index=True);C.dump(out/f'{phase}_counts.json',cts)
    controls={};cache={}
    for name in candidates:
        if name not in sigs:continue
        base=base_map[name]
        if independent:
            if base not in cache:cache[base]=F.replay(g,sigs[base],independent=True)[0]
            cand=F.replay(g,sigs[name],independent=True)[0];bb=cache[base]
        else:cand,bb=ledgers[name],ledgers[base]
        controls[name]=dict(non_executable_signal_only=independent,**C.filter_controls(cand,bb,days))
        if independent:C.csv(out/f'{phase}_{name}_independent_diagnostic.csv',cand[['day','j0','j1','side','date','net']])
    C.dump(out/f'{phase}_filter_diagnostics.json',controls)
    selected=None
    if phase=='design':
        gates={}
        for name in candidates:
            t=ledgers[name];m=C.stats(t,days);yy=t.groupby(t.date.dt.year).net.sum()
            gates[name]={k:bool(v) for k,v in dict(count=len(t)>=100,net=m['total']>0,t=m['t_trade']>=2,nw5=m['t_nw5']>=1.5,pf=m['profit_factor']>=1.2,years=(yy>0).sum()>=4,micro=t.net_mnq.sum()>0,stress=t.stress_four_ticks.sum()>0).items()}
        passing=[k for k,v in gates.items() if all(v.values())];selected=passing[0] if passing else None
        C.dump(out/'design_gate.json',dict(prereg=prereg,gates=gates,passing=passing,selected=selected,economic_models=len(sigs),cumulative_program_models=prior+len(sigs),program_continues=True))
    print(df[(df.period==('2018-22' if phase=='design' else '2023+'))&(df.side=='all')][['model','trades','total','avg','profit_factor','t_trade','t_nw5','max_dd']].to_string(index=False),flush=True)
    print('Selected:',selected,flush=True)
    return ledgers,df,selected


def table(frame):
    cols=['model','period','side','trades','win','avg','total','t_trade','t_nw5','t_nw20','sharpe','sortino','profit_factor','calmar','ulcer','max_dd','cost','missing_held_minutes']
    lines=['| '+' | '.join(cols)+' |','|'+'|'.join(['---']*len(cols))+'|']
    for _,r in frame.iterrows():lines.append('| '+' | '.join(f'{r[k]:.5g}' if isinstance(r[k],float) else str(r[k]) for k in cols)+' |')
    return '\n'.join(lines)
