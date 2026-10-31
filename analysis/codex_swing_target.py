"""Frozen Swing Target source replication. No cache rebuilding or live access."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import pickle
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_swing_target'
sys.path.insert(0,str(ROOT/'scratch_data/codex_deps'))
sys.path.insert(0,str(ROOT/'analysis'))
os.environ['NUMBA_CACHE_DIR']=str(OUT/'numba_cache')
import numpy as np
import pandas as pd
import grid24
import metrics as M
import resampling as R
import montecarlo as MC
from trials import parse_tier_list
import codex_swing_engine as E

PLAN='agents/codex/plans/swing_target.md'
SEED=20261025

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()

def dump(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2,default=lambda v:float(v) if isinstance(v,np.generic) else str(v))+'\n',encoding='utf-8')

def setup():
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'.gitignore').write_text('numba_cache/\n',encoding='utf-8')
    committed=subprocess.check_output(['git','show','HEAD:'+PLAN],cwd=ROOT).decode('utf-8')
    assert committed.replace('\r\n','\n')==(ROOT/PLAN).read_text(encoding='utf-8').replace('\r\n','\n')
    pc=subprocess.check_output(['git','log','-1','--format=%H','--',PLAN],cwd=ROOT,text=True).strip()
    source=Path(r'C:\Users\dmoto\Downloads\Swing_Target_NQ.txt')
    target=ROOT/'agents/codex/inputs/swing_target/Swing_Target_NQ.txt'
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():assert sha(target)==sha(source)
    else:shutil.copyfile(source,target)
    with (ROOT/'scratch_data/g24.pkl').open('rb') as f:g=pickle.load(f)
    days=pd.DatetimeIndex(g.ts[g.trading])
    days=days[days.year>=2018]
    return g,days,pc

def costs(t,g):
    z=t.copy()
    z['date']=pd.to_datetime(g.ts[z.day.to_numpy(int)])
    z['exit_date']=pd.to_datetime(g.ts[z.exit_day.to_numpy(int)])
    z['net']=z.pnl-7.25-5*(1+z.kind.ne(1).astype(int))
    for fee in [1.04,1.24]:z[f'mnq_fee_{fee:.2f}']=z.pnl/10-fee-.5*(1+z.kind.ne(1).astype(int))
    z['native_net_per_mnq']=z['mnq_fee_1.24']
    z['author_cost_per_mnq']=z.pnl/10-1.
    z['extra_tick_net']=z.net-5*(1+z.kind.ne(1).astype(int))
    z['apex_flat_violation']=z.cross_date | z.j0.ge(960) | z.j1.ge(960)
    return z

def daily(t,days,col='net'):
    # A carried trade is recognized on its actual exit date, never backdated.
    outside=pd.DatetimeIndex(t.exit_date.unique()).difference(days)
    calendar=days.union(outside).sort_values()
    return t.groupby('exit_date')[col].sum().reindex(calendar,fill_value=0.)

def metric(t,days,model,period,side='all'):
    if side!='all':t=t[t.side.eq(1 if side=='long' else -1)]
    t=t[t.date.isin(days)]
    if not len(t):return dict(model=model,period=period,side=side,trades=0)
    d=daily(t,days)
    m=M.perf(np.r_[0,d.to_numpy()],t.net)
    m.update(model=model,period=period,side=side,total=float(t.net.sum()),gross=float(t.pnl.sum()),
       cost=float((t.pnl-t.net).sum()),t=float(t.net.mean()/t.net.std()*np.sqrt(len(t))),
       max_trade_dd=R.max_dd(t.net),native_net_per_mnq=float(t.native_net_per_mnq.sum()),
       native_max_trade_dd=R.max_dd(t.native_net_per_mnq),
       average_win=float(t[t.net>0].net.mean()),average_loss=float(-t[t.net<0].net.mean()),
       max_mae_per_mnq=float(t.mae.max()/10),cross_date_trades=int(t.cross_date.sum()),
       missing_held_minutes=int(t.unknown_held_minutes.sum()))
    return m

def metric_rows(t,days,model,design_only=False):
    groups=[('2018-22',days[days.year<=2022])]
    if not design_only:groups += [('2023+',days[days.year>=2023]),('all',days),
       ('author_window',days[(days>='2018-02-01')&(days<='2026-07-31')])]
    groups +=[(str(y),days[days.year==y]) for y in sorted(set(days.year)) if not design_only or y<=2022]
    return [metric(t,ds,model,p,s) for p,ds in groups for s in ['all','long','short'] if len(ds)]

def design():
    g,days,pc=setup()
    rows=[]
    for model,be in [('CODE',False),('CODE_BE',True)]:
        raw,diag=E.replay(g,breakeven=be,start_date='2018-01-01',end_date='2022-12-31')
        t=costs(raw,g)
        t.to_csv(OUT/(model+'_design_trades.csv'),index=False)
        dump(model+'_design_diagnostics.json',diag)
        rows.extend(metric_rows(t,days[days.year<=2022],model,True))
    pd.DataFrame(rows).to_csv(OUT/'design_metrics.csv',index=False)
    dump('design_complete.json',dict(plan_commit=pc,models=['CODE','CODE_BE'],validation_run=False,
        source_sha256=sha(ROOT/'agents/codex/inputs/swing_target/Swing_Target_NQ.txt'),
        engine_sha256=sha(ROOT/'analysis/codex_swing_engine.py'),cache_sha256=sha(ROOT/'scratch_data/g24.pkl')))
    print(pd.DataFrame(rows).query("period=='2018-22'")[["model","side","trades","avg","profit_factor","t","max_dd"]].to_string(index=False),flush=True)

def validate():
    g,days,pc=setup()
    frozen=json.loads((OUT/'design_complete.json').read_text())
    assert frozen['engine_sha256']==sha(ROOT/'analysis/codex_swing_engine.py')
    assert frozen['cache_sha256']==sha(ROOT/'scratch_data/g24.pkl')
    rows=[];gates=[]
    for model,be in [('CODE',False),('CODE_BE',True)]:
        raw,diag=E.replay(g,breakeven=be,start_date='2023-01-01',end_date='2026-10-09')
        t=costs(raw,g)
        t.to_csv(OUT/(model+'_validation_trades.csv'),index=False)
        dump(model+'_validation_diagnostics.json',diag)
        design_t=pd.read_csv(OUT/(model+'_design_trades.csv'),parse_dates=['date','exit_date'])
        all_t=pd.concat([design_t,t],ignore_index=True)
        all_t.to_csv(OUT/(model+'_trades.csv'),index=False)
        rows.extend(metric_rows(all_t,days,model))
        a=metric(design_t,days[days.year<=2022],model,'2018-22')
        b=metric(t,days[days.year>=2023],model,'2023+')
        c=metric(all_t,days,model,'all')
        gate=bool(a['total']>0 and b['total']>0 and a['profit_factor']>=1.2 and c['t']>=2 and t.extra_tick_net.sum()>0)
        cross=int(all_t.cross_date.sum()); violations=int(all_t.apex_flat_violation.sum())
        # Any cross-date trade violates the source's intraday-only Apex premise.
        gates.append(dict(model=model,cheap_pass=gate,apex_source_eligible=bool(gate and violations==0),cross_date_trades=cross,
          apex_flat_violations=violations,
          missing_held_minutes=int(all_t.unknown_held_minutes.sum()),validation_extra_tick_net=float(t.extra_tick_net.sum())))
    frame=pd.DataFrame(rows)
    frame.to_csv(OUT/'metrics.csv',index=False)
    dump('cheap_gate.json',dict(models=gates,source_parity_verified=False,new_models=2,plan_commit=pc,
        original_claims_unverified=True,author_prior_trials_unknown=True))
    dump('manifest.json',dict(plan_commit=pc,python=sys.executable,cache_rebuilt=False,last_complete='2026-10-09',
       hashes={p:sha(ROOT/p) for p in ['scratch_data/g24.pkl','analysis/codex_swing_engine.py','analysis/codex_swing_target.py',PLAN]},
       source_sha256=frozen['source_sha256'],full_session_proxy=True))
    print(frame.query("period in ['2018-22','2023+','all','author_window'] and side=='all'")[["model","period","trades","win","avg","profit_factor","t","max_dd"]].to_string(index=False),flush=True)
    print(json.dumps(gates,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase',choices=['design','validation'],required=True)
    args=p.parse_args();design() if args.phase=='design' else validate()
