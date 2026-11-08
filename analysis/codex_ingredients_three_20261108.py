"""Fixed 3-strategy ingredient diagnostics; no optimizer, account model or live access."""
import argparse
import ast
import glob
import hashlib
import json
import re
from pathlib import Path
import subprocess
import tempfile
import warnings

import numpy as np
import pandas as pd
import metrics as M
import resampling as R

warnings.filterwarnings('ignore',category=RuntimeWarning)
ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'agents/codex/inputs/ingredients_three_20261108'
OUT=ROOT/'analysis/outputs/codex_ingredients_three_20261108'
SOURCE=Path('/workspace/thebeginning')
DATA_REF='fe35af99aa90d7f31b91f8693859251bb44dd9ab'
PLAN='agents/codex/plans/ingredients_three_20261108.md'
CODE='analysis/codex_ingredients_three_20261108.py'
SEED=20261108


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,value):
    def clean(x):
        if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
        if isinstance(x,(list,tuple)):return [clean(v) for v in x]
        if isinstance(x,(np.bool_,)):return bool(x)
        if isinstance(x,(np.integer,)):return int(x)
        if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else None
        return x
    Path(p).write_text(json.dumps(clean(value),indent=2)+'\n')


def functions(filename,names,namespace):
    tree=ast.parse((INPUT/filename).read_text())
    nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
    if set(n.name for n in nodes)!=set(names):raise RuntimeError('source function missing')
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(INPUT/filename),'exec'),namespace)
    return namespace


def grids(end):
    manifest={}; last_year=pd.Timestamp(end).year
    G=functions('grid24.py',['jof','Grid24'],{'np':np,'pd':pd,'glob':glob,'NMIN24':1440})['Grid24']
    with tempfile.TemporaryDirectory(prefix='ingredients_three_') as tmp:
        tmp=Path(tmp)
        for year in range(2017,last_year+1):
            for prefix,alias in [('NQ_1min_','nq_day_'),('NQ_1min_ON_','nq_night_'),('ES_1min_','es_')]:
                name=f'{prefix}{year}.csv';p=SOURCE/'data'/name;raw=p.read_bytes()
                expected=subprocess.check_output(['git','-C',str(SOURCE),'rev-parse',DATA_REF+':data/'+name],text=True).strip()
                blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
                if blob!=expected:raise RuntimeError('raw input mismatch: '+name)
                manifest[name]={'blob':blob,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
                check=pd.read_csv(p,usecols=['date','time'])
                if check.duplicated(['date','time']).any():raise RuntimeError('duplicate source bars: '+name)
                (tmp/f'{alias}{year}.csv').symlink_to(p)
        nq=G(str(tmp/'nq_day_*.csv'),str(tmp/'nq_night_*.csv'))
        es=G(str(tmp/'es_*.csv'),night_pattern='')
    for g in (nq,es):
        n=int(np.searchsorted(pd.DatetimeIndex(g.ts),pd.Timestamp(end),side='right'))
        for c in ('o','h','l','c','v','ts','dates','last_j'):setattr(g,c,getattr(g,c)[:n])
        g.D=n;g.trading=g.trading[g.trading<n]
    return nq,es,manifest


def setup_engines(g,e):
    shared={'np':np,'pd':pd,'PV':20.,'TICK':.25,'COST':7.25}
    dt=functions('dual_thrust_test.py',['holiday','setups','trade','run'],dict(shared))
    # Original RS loader's two pickle assignments replaced by supplied in-memory grids.
    rs={'np':np,'pd':pd,'re':re,'jof':lambda hm:(np.asarray(hm)//100)*60+np.asarray(hm)%100,
        'PV':20.,'TICK':.25,'COMM':7.25,'CODE':str(INPUT/'RelStrength_v3.txt'),'g':g,'e':e}
    functions('relative_strength_test.py',['holidays','signals','trades'],rs)
    tree=ast.parse((INPUT/'relative_strength_test.py').read_text())
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='load')
    assert isinstance(fn.body[0],ast.Assign) and isinstance(fn.body[1],ast.Assign)
    assert fn.body[0].targets[0].id=='g' and fn.body[1].targets[0].id=='e'
    fn.body=fn.body[2:]
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'<RS in-memory loader>','exec'),rs)
    lf={'np':np,'pd':pd,'TICK':.25}
    src=(INPUT/'letf_rebalance_test.py').read_text();tree=ast.parse(src)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='trades')
    src=ast.get_source_segment(src,fn)
    # Instrument exit reason; reject zero-direction signals only introduced by K=0.
    src=src.replace('mv = cs - o0','mv = cs - o0\n        if mv == 0: continue')
    src=src.replace('px, j1 = None, j_exit','px, j1 = None, j_exit; stop_hit = False')
    src=src.replace('j1 = j; break','j1 = j; stop_hit = True; break')
    src=src.replace('kind=0, pnl=','kind=0, exit_reason=("stop" if stop_hit else "flat"), pnl=')
    exec(compile(src,'<LDF exit-reason instrumentation>','exec'),lf)
    return dt,rs,lf


def dt_days(g):
    out={}
    for day in g.trading:
        j=np.arange(511,901);m=np.isfinite(g.c[day,j]);j=j[m]
        if not len(j):continue
        x=pd.DataFrame({'time':j//60*100+j%60,**{nm:getattr(g,c)[day,j] for nm,c in
                         [('open','o'),('high','h'),('low','l'),('close','c')]}})
        out[int(g.dates[day])]=x
    return out


def canonical(raw,family,g):
    t=raw.copy().reset_index(drop=True)
    if family=='RS':
        t=t.rename(columns={'pnl':'net'});t['day']=t.day.astype(int)
    elif family=='DT':
        mp={pd.Timestamp(d):i for i,d in enumerate(g.ts)}
        t['day']=[mp[pd.Timestamp(d)] for d in t.date]
        t['j0']=t.sig_time.astype(int)//100*60+t.sig_time.astype(int)%100+1
        t['j1']=t.exit_time.astype(int)//100*60+t.exit_time.astype(int)%100
    else:
        # Source LDF prices already include one tick per market leg; expose that bridge.
        t['gross']=t.pnl+10.
        t['kind']=t.exit_reason
        t['entry']=t.entry-t.side*.25;t['exit']=t.exit+t.side*.25
    t['date']=pd.to_datetime(t.date)
    t=t[t.date>='2018-01-01'].reset_index(drop=True)
    t['commission']=7.25;t['slippage']=t.gross-t.net-7.25
    t['native_mnq_net']=t.gross/10-1.25-t.slippage/10
    if not t.side.isin([-1,1]).all():raise RuntimeError('invalid side')
    if not np.isfinite(t[['entry','exit','gross','net']]).all().all():raise RuntimeError('unknown entry/exit')
    if not np.allclose(t.net,t.gross-t.commission-t.slippage):raise RuntimeError('cost bridge')
    if not np.allclose(t.gross,(t.exit-t.entry)*t.side*20):raise RuntimeError('raw-price gross bridge')
    t['missing_held_closes']=[int(np.isnan(g.c[int(r.day),int(r.j0):int(r.j1)+1]).sum()) for r in t.itertuples()]
    return t


def run_cases(g,e):
    dt,rs,lf=setup_engines(g,e);days=dt_days(g);S=dt['setups'](days)
    cases={}
    for name,s,kw in [('original',S,{}),('no_range_distance',dt['setups'](days,k=0),{}),
                     ('no_band_skip',dt['setups'](days,band=0),{}),('no_target',S,{'tp':0}),
                     ('no_entry_bar_stop',S,{'entry_bar_stop':False})]:
        cases['DT/'+name]=canonical(dt['run'](days,s,**kw),'DT',g)
    d,N,E=rs['load']();Z=rs['signals'](d,N,E);Zo=rs['signals'](d,N,E,beta_mode='own')
    for name,z,kw in [('original',Z,{}),('no_ES',Zo,{}),('no_Z_hurdle',np.where(Z==0,np.nan,Z),{'zmin':0}),
                     ('no_target',Z,{'tgt_f':None})]:
        cases['RS/'+name]=canonical(rs['trades'](d,N,z,**kw),'RS',g)
    for name,kw in [('original',{}),('no_move_hurdle',{'k':0}),('no_stop',{'stop':1e6}),('hold_to_1500',{'j_exit':900})]:
        args={'k':.4,'stop':.25,'j_exit':870};args.update(kw)
        cases['LDF/'+name]=canonical(lf['trades'](g,**args),'LDF',g)
    if (cases['LDF/no_stop'].kind=='stop').any():raise RuntimeError('huge stop unexpectedly hit')
    return cases


def daily(t,calendar,col='net'):
    s=t.groupby('date')[col].sum().reindex(calendar,fill_value=0.)
    if abs(s.sum()-t[col].sum())>.005:raise RuntimeError('daily/trade reconciliation')
    return s


def tst(x):return float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))) if len(x)>1 and x.std()>0 else np.nan
def metric(t,cal):
    d=daily(t,cal);z=M.perf(d,t.net,capital=50000)
    z['max_dd']=R.max_dd(d);z['calmar']=z['annual']/z['max_dd'] if z['max_dd'] else np.nan
    z.update(total=t.net.sum(),gross=t.gross.sum(),commission=t.commission.sum(),slippage=t.slippage.sum(),
             t_trade=tst(t.net),worst_trade=t.net.min(),native_mnq_total=t.native_mnq_net.sum(),
             native_mnq_worst=t.native_mnq_net.min(),missing_held_closes=int(t.missing_held_closes.sum()))
    return z


def filter_control(full,unfiltered,cal):
    matched=full.merge(unfiltered,on='date',suffixes=('_f','_u'),how='left')
    pure=len(matched)==len(full) and all(np.allclose(matched[c+'_f'],matched[c+'_u']) for c in ['side','entry','exit','net'])
    if not pure:return {'pure_nested_filter':False,'reason':'common-date trades differ; paired strategy comparison only'}
    removed=unfiltered[~unfiltered.date.isin(full.date)];rng=np.random.default_rng(SEED)
    counts=full.groupby(full.date.dt.year).size().to_dict()
    pools={int(y):s for y,s in unfiltered.groupby(unfiltered.date.dt.year)}
    totals=[];dds=[]
    for _ in range(1000):
        picked=[]
        for y,p in pools.items():
            n=counts.get(y,0)
            if n:picked.append(p.iloc[rng.choice(len(p),n,replace=False)])
        t=pd.concat(picked,ignore_index=True);s=daily(t,cal)
        totals.append(s.sum());dds.append(R.max_dd(s))
    actual=daily(full,cal);a_dd=R.max_dd(actual)
    return {'pure_nested_filter':True,'removed_n':len(removed),'removed_total':removed.net.sum(),
            'removed_mean':removed.net.mean(),'removed_t':tst(removed.net),'random_drops':1000,
            'actual_total':actual.sum(),'actual_dd':a_dd,'random_total_p5_p50_p95':np.percentile(totals,[5,50,95]).tolist(),
            'random_dd_p5_p50_p95':np.percentile(dds,[5,50,95]).tolist(),
            'random_profit_ge_actual':float(np.mean(np.array(totals)>=actual.sum())),
            'random_dd_le_actual':float(np.mean(np.array(dds)<=a_dd))}


def phase(name):
    for path in (PLAN,CODE):
        if subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT)!=(ROOT/path).read_bytes():
            raise RuntimeError('commit exact plan/script before returns')
    if name=='recent':
        design=json.loads((OUT/'design'/'summary.json').read_text())
        if not design['implementation_gates_passed'] or design['script_sha256']!=digest(ROOT/CODE):
            raise RuntimeError('design gates or exact frozen definition unavailable')
    end='2022-12-30' if name=='design' else '2026-10-09'
    start='2018-01-01' if name=='design' else '2023-01-01'
    g,e,inputs=grids(end);cases=run_cases(g,e)
    cal=pd.DatetimeIndex(g.ts[g.trading]);cal=cal[(cal>=start)&(cal<=end)]
    dest=OUT/name;dest.mkdir(parents=True,exist_ok=True)
    stats=[];effects=[];filters={};case_data={}
    for key,all_t in cases.items():
        t=all_t[(all_t.date>=start)&(all_t.date<=end)].copy();case_data[key]=t
        fam,var=key.split('/');stem=key.replace('/','__')
        t.to_csv(dest/(stem+'_trades.csv'),index=False)
        d=daily(t,cal);d.to_csv(dest/(stem+'_daily.csv'),header=['net'])
        for side in ['all','long','short']:
            sub=t if side=='all' else t[t.side.eq(1 if side=='long' else -1)]
            stats.append({'family':fam,'variant':var,'side':side,**metric(sub,cal)})
        for y,dates in pd.Series(cal,index=cal).groupby(cal.year):
            sub=t[t.date.dt.year==y]
            stats.append({'family':fam,'variant':var,'side':'all','year':int(y),**metric(sub,pd.DatetimeIndex(dates.values))})
    for key,t in case_data.items():
        fam,var=key.split('/')
        if var=='original':continue
        full=case_data[fam+'/original'];delta=daily(full,cal)-daily(t,cal)
        ci=R.bootstrap(delta,n=1000,block=20,seed=SEED,chunk=250).loc['annual']
        effects.append({'family':fam,'removed_component':var,'original_minus_ablation_total':delta.sum(),
                        'annual_effect_p5':ci.p5,'annual_effect_p50':ci.p50,'annual_effect_p95':ci.p95})
    for fam,var in [('DT','no_band_skip'),('RS','no_Z_hurdle'),('LDF','no_move_hurdle')]:
        filters[fam]=filter_control(case_data[fam+'/original'],case_data[fam+'/'+var],cal)
    baseline_nonempty=all(len(case_data[f+'/original'])>0 for f in ['DT','RS','LDF'])
    summary={'phase':name,'start':start,'end':end,'calendar_sessions':len(cal),'implementation_gates_passed':baseline_nonempty,
             'rule_cases':13,'new_candidate_promotion':False,'portfolio_tests_run':False,
             'interpretation':'historical ingredient diagnostics, not untouched holdout or a causal identification experiment',
             'source_data_ref':DATA_REF,'inputs':inputs,'source_sha256':{p.name:digest(p) for p in INPUT.iterdir()},
             'script_sha256':digest(ROOT/CODE),'plan_sha256':digest(ROOT/PLAN),
             'plan_commit':subprocess.check_output(['git','log','-1','--format=%H','--',PLAN],cwd=ROOT,text=True).strip(),
             'resampling_seed':SEED,'resamples':1000,'pure_filter_controls':filters,
             'dependencies':{x:digest(ROOT/'analysis'/x) for x in ['metrics.py','resampling.py']}}
    pd.DataFrame(stats).to_csv(dest/'metrics.csv',index=False)
    pd.DataFrame(effects).to_csv(dest/'paired_effects.csv',index=False)
    dump(dest/'summary.json',summary)
    print(pd.DataFrame(stats).query("side=='all' and year.isna()")[[
        'family','variant','trades','total','avg','t_trade','sharpe','max_dd','worst_trade']].to_string(index=False),flush=True)
    print(pd.DataFrame(effects).to_string(index=False),flush=True)
    print(json.dumps({'phase':name,'implementation_gates_passed':baseline_nonempty,'missing_held_closes':{
        k:int(v.missing_held_closes.sum()) for k,v in case_data.items()}},indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['design','recent'],required=True)
    phase(p.parse_args().phase)
