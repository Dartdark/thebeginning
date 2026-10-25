"""Frozen source replication; quantities applied once, no research cache writes."""
from pathlib import Path
import argparse,hashlib,json,os,pickle,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_rebound'
INPUT=ROOT/'agents/codex/inputs/rebound'
sys.path.insert(0,str(ROOT/'scratch_data/codex_deps'))
sys.path.insert(0,str(ROOT/'analysis'))
os.environ['NUMBA_CACHE_DIR']=str(OUT/'numba_cache')
import numpy as np
import pandas as pd
import grid24
import metrics as M
import resampling as R
import codex_rebound_engine as E

PLAN='agents/codex/plans/overnight_rebound.md'
MODELS={'UNIFORM':(1,'down'),'SUNDAY2':(2,'down'),'ALLNIGHTS':(1,'all')}
SEED=20261025

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()

def dump(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2,default=lambda v:float(v) if isinstance(v,np.generic) else str(v))+'\n',encoding='utf-8')

def setup():
    OUT.mkdir(parents=True,exist_ok=True);INPUT.mkdir(parents=True,exist_ok=True)
    (OUT/'.gitignore').write_text('numba_cache/\n',encoding='utf-8')
    (INPUT/'.gitattributes').write_text('* -text -whitespace\n',encoding='utf-8')
    committed=subprocess.check_output(['git','show','HEAD:'+PLAN],cwd=ROOT).decode('utf-8')
    assert committed.replace('\r\n','\n')==(ROOT/PLAN).read_text(encoding='utf-8').replace('\r\n','\n')
    pc=subprocess.check_output(['git','log','-1','--format=%H','--',PLAN],cwd=ROOT,text=True).strip()
    source=Path(r'C:\Users\dmoto\Downloads\NQ_Overnight_Rebound_strategy.txt')
    snapshot=INPUT/'NQ_Overnight_Rebound_strategy.txt'
    if snapshot.exists():assert sha(snapshot)==sha(source)
    else:shutil.copyfile(source,snapshot)
    tier=INPUT/'tier_list_e1a94f7.md'
    data=subprocess.check_output(['git','show','e1a94f7:TIER_LIST.md'],cwd=ROOT)
    if tier.exists():assert tier.read_bytes()==data
    else:tier.write_bytes(data)
    with (ROOT/'scratch_data/g24.pkl').open('rb') as f:g=pickle.load(f)
    days=pd.DatetimeIndex(g.ts[g.trading]);days=days[days.year>=2018]
    return g,days,pc

def costs(t):
    t=t.copy()
    submit_date=pd.to_datetime(t.date)+pd.to_timedelta(t.entry_submit_day-t.day,unit='D')+pd.to_timedelta(t.entry_submit_j.ge(1380).astype(int),unit='D')
    t['entry_et_dow']=(submit_date.dt.dayofweek+1)%7
    exit_wall=t.j1-t.exit_phase.eq('open').astype(int)
    t['account_date']=pd.to_datetime(t.exit_date)+pd.to_timedelta(exit_wall.ge(1020).astype(int),unit='D')
    t['unit_net']=t.pnl-17.25
    t['net']=t.unit_net*t.qty
    t['gross']=t.pnl*t.qty
    for fee in [1.04,1.24]:t[f'mnq_fee_{fee:.2f}']=(t.pnl/10-fee-1.)*t.qty
    t['native_net_per_mnq']=t['mnq_fee_1.24']
    t['author_1dollar']=(t.pnl/10-1.)*t.qty
    t['two_ticks_net']=t.net-10*t.qty
    t['four_ticks_net']=t.net-30*t.qty
    return t

def daily(t,days,col='net'):
    ix=days.union(pd.DatetimeIndex(t.account_date.unique())).sort_values()
    return t.groupby('account_date')[col].sum().reindex(ix,fill_value=0.)

def metric(t,days,model,period):
    lo=pd.Timestamp(year=int(min(days.year)),month=1,day=1)
    hi=pd.Timestamp('2026-10-09')
    if period=='2018-22':hi=pd.Timestamp('2022-12-31')
    elif period=='author_window':hi=pd.Timestamp('2026-07-31')
    elif period.isdigit():hi=min(hi,pd.Timestamp(year=int(period),month=12,day=31))
    t=t[t.account_date.between(lo,hi)]
    if not len(t):return dict(model=model,period=period,trades=0)
    d=daily(t,days)
    m=M.perf(np.r_[0.,d.to_numpy()],t.net)
    m.update(model=model,period=period,side='all/long',total=float(t.net.sum()),gross=float(t.gross.sum()),
        costs=float((t.gross-t.net).sum()),t=float(t.net.mean()/t.net.std()*np.sqrt(len(t))),
        contracts=float(t.qty.sum()),max_trade_dd=R.max_dd(t.net),native_total=float(t.native_net_per_mnq.sum()),
        native_max_trade_dd=R.max_dd(t.native_net_per_mnq),worst_native_trade=float(t.native_net_per_mnq.min()),
        max_mae_per_base_mnq=float((t.mae*t.qty/10).max()),average_win=float(t[t.net>0].net.mean()),
        average_loss=float(-t[t.net<0].net.mean()),deadline_violations=int(t.crosses_1559_ct.sum()),
        missing_held_minutes=int(t.unknown_held_minutes.sum()))
    return m

def metric_rows(t,days,model,design=False):
    groups=[('2018-22',days[days.year<=2022])]
    if not design:groups += [('2023+',days[days.year>=2023]),('all',days),('author_window',days[days<='2026-07-31'])]
    groups += [(str(y),days[days.year==y]) for y in sorted(set(days.year)) if not design or y<=2022]
    rows=[metric(t,ds,model,p) for p,ds in groups if len(ds)]
    for label,mask in [('sunday',t.qty.ge(0)&t.entry_et_dow.eq(0)),('weekday',t.entry_et_dow.ne(0))]:
        if not design:rows.append(metric(t[mask],days,model,label))
    return rows

def design():
    g,days,pc=setup();rows=[]
    dump('synthetic_checks.json',E.synthetic_checks())
    for model,(mult,condition) in MODELS.items():
        raw,diag=E.replay(g,sunday_multiplier=mult,condition=condition,start_date='2018-01-01',end_date='2022-12-31')
        t=costs(raw);t.to_csv(OUT/(model+'_design_trades.csv'),index=False);dump(model+'_design_diag.json',diag)
        rows.extend(metric_rows(t,days[days.year<=2022],model,True))
    pd.DataFrame(rows).to_csv(OUT/'design_metrics.csv',index=False)
    dump('design_complete.json',dict(plan_commit=pc,engine_sha256=sha(ROOT/'analysis/codex_rebound_engine.py'),cache_sha256=sha(ROOT/'scratch_data/g24.pkl')))
    print(pd.DataFrame(rows).query("period=='2018-22'")[["model","trades","win","avg","profit_factor","t","max_dd"]].to_string(index=False),flush=True)

def validation():
    g,days,pc=setup();old=json.loads((OUT/'design_complete.json').read_text())
    assert old['engine_sha256']==sha(ROOT/'analysis/codex_rebound_engine.py')
    assert old['cache_sha256']==sha(ROOT/'scratch_data/g24.pkl')
    rows=[];gates=[]
    for model,(mult,condition) in MODELS.items():
        raw,diag=E.replay(g,sunday_multiplier=mult,condition=condition,start_date='2023-01-01',end_date='2026-10-09')
        t=costs(raw);t.to_csv(OUT/(model+'_validation_trades.csv'),index=False);dump(model+'_validation_diag.json',diag)
        d=costs(pd.read_csv(OUT/(model+'_design_trades.csv'),parse_dates=['date','exit_date']))
        z=pd.concat([d,t],ignore_index=True);z.to_csv(OUT/(model+'_trades.csv'),index=False)
        rows.extend(metric_rows(z,days,model))
        a=metric(d,days[days.year<=2022],model,'2018-22');b=metric(z,days,model,'all')
        passing=bool(a['total']>0 and t.net.sum()>0 and a['profit_factor']>=1.15 and b['t']>=2 and t.four_ticks_net.sum()>0)
        gates.append(dict(model=model,control_only=model=='ALLNIGHTS',cheap_pass=passing,
            validation_four_ticks_net=float(t.four_ticks_net.sum()),deadline_violations=int(z.crosses_1559_ct.sum()),
            missing_held_minutes=int(z.unknown_held_minutes.sum()),unclosed=bool(diag['open_position_at_end'])))
    m=pd.DataFrame(rows);m.to_csv(OUT/'metrics.csv',index=False)
    dump('cheap_gate.json',dict(models=gates,plan_commit=pc,new_models=3,author_searches=336))
    dump('manifest.json',dict(plan_commit=pc,python=sys.executable,caches_rebuilt=False,
       hashes={p:sha(ROOT/p) for p in ['scratch_data/g24.pkl','analysis/codex_rebound_engine.py','analysis/codex_rebound_run.py',PLAN]},
       source_sha256=sha(INPUT/'NQ_Overnight_Rebound_strategy.txt'),plan_snapshot='e1a94f7',clock='CT cache normalized to intended ET-display/-60 source semantics'))
    print(m.query("period in ['2018-22','2023+','all','author_window']")[["model","period","trades","win","avg","profit_factor","t","max_dd"]].to_string(index=False),flush=True)
    print(json.dumps(gates,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase',choices=['design','validation'],required=True)
    a=p.parse_args();design() if a.phase=='design' else validation()
