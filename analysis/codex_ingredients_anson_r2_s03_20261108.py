"""Frozen Anson/R2Vault/S03 ingredient grids, using retained source engines."""
import argparse
import ast
import copy
from dataclasses import dataclass
import datetime as dt
import glob
import json
from pathlib import Path
import subprocess
import sys
import types
from typing import Optional
import warnings

import numpy as np
import pandas as pd
from numba import njit

import metrics as M
import resampling as R
import codex_ingredients_three_20261108 as B
import codex_ingredients_s30_s47_kusho_20261108 as H

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT/'agents/codex/inputs/ingredients_anson_r2_s03_20261108'
OUT = ROOT/'analysis/outputs/codex_ingredients_anson_r2_s03_20261108'
PLAN = 'agents/codex/plans/ingredients_anson_r2_s03_20261108.md'
CODE = 'analysis/codex_ingredients_anson_r2_s03_20261108.py'
EVIDENCE = 'agents/codex/evidence/ingredients_anson_r2_s03_20261108.md'
SEED = 80315
B.INPUT, B.SEED = INPUT, SEED
check, sha = H.check, H.sha
FAMILIES = {
    'ANSON':['original','fade_direction','no_strength_gate','hold_6','no_early_adapter'],
    'R2':['original','fade_break','no_R2_gate','no_slope_gate','no_stop'],
    'S03':['original','fade_direction','no_entry_VWAP','no_entry_band','no_sigma_stop'],
}
MODULES = []
warnings.filterwarnings('ignore', category=RuntimeWarning)


def no_cache_jit(*args, **kwargs):
    kwargs['cache'] = False
    return njit(*args, **kwargs)


def source_module(filename, functions=None, namespace=None, transform=None, constants=None):
    """Only definitions/constants; no imports, source main, cache or top-level runner."""
    path = INPUT/filename
    tree = ast.parse(path.read_text())
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == '__future__': nodes.append(node)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if functions is None or node.name in functions: nodes.append(node)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = [x.id for x in getattr(node,'targets',[]) if isinstance(x,ast.Name)]
            if constants is None or any(t in constants for t in targets): nodes.append(node)
    name = 'frozen_ingredients_'+str(len(MODULES))
    mod = types.ModuleType(name);sys.modules[name] = mod;MODULES.append(mod)
    mod.__dict__.update(np=np,pd=pd,dataclass=dataclass,Optional=Optional,njit=no_cache_jit,
                        dt=dt,Path=Path,__file__=str(path),glob=glob)
    mod.__dict__.update(namespace or {})
    text = ast.unparse(ast.Module(body=nodes,type_ignores=[]))
    if transform: text = transform(text)
    exec(compile(text,str(path),'exec'),mod.__dict__)
    return mod


def replace_once(text,before,after):
    check(text.count(before)==1,'Instrumentation hook changed: '+before)
    return text.replace(before,after)


def modules():
    cal = source_module('replica.py',functions={'is_early_close'},constants=set())
    grid = source_module('grid24.py')
    # Source synthetic functions import this retained Grid24 explicitly.
    sys.modules['grid24'] = grid
    a0 = source_module('codex_anson_replay.py',namespace={'is_early_close':cal.is_early_close})
    a = source_module('codex_anson_replay.py',namespace={'is_early_close':cal.is_early_close,'DIRECTION':1},
        transform=lambda text:replace_once(text,'side = int(np.sign(b.momentum))','side = int(np.sign(b.momentum)) * DIRECTION'))
    a.MODELS = {name:dict(threshold=0. if name=='no_strength_gate' else 4.5,
                           hold_bars=6 if name=='hold_6' else 20,
                           early_adapter=name!='no_early_adapter') for name in FAMILIES['ANSON']}
    r0 = source_module('codex_r2vault_replay.py',namespace={
        'prepare_observed_bars':a0.prepare_bars,'_gap_records':a0._gap_records,'is_early_close':cal.is_early_close})
    s0 = s03_module('original',original=True)
    return cal,a0,a,r0,s0


def r2_module(variant,a0,calendar):
    def change(text):
        # Every change below is identity for original SIDE=1 / STOP_POINTS=75.
        text=text.replace('_remaining_path(nodes, o, 1, o, 1)','_remaining_path(nodes, o, SIDE, o, 1)')
        text=text.replace('_remaining_path(nodes, order, 1, order, seg)','_remaining_path(nodes, order, SIDE, order, seg)')
        text=replace_once(text,"state['position']['entry'], 1)","state['position']['entry'], SIDE)")
        text=replace_once(text,"points = float(px) - position['entry']","points = (float(px) - position['entry']) * SIDE")
        text=text.replace('side=1,','side=SIDE,')
        text=text.replace("position['entry'] - float(adverse)","(position['entry'] - float(adverse)) * SIDE")
        text=text.replace("q['entry'] - float(adverse)","(q['entry'] - float(adverse)) * SIDE")
        text=replace_once(text,'stop_px=float(entry) - 75.0, target_px=float(entry) + 40.0,',
                              'stop_px=float(entry) - SIDE * STOP_POINTS, target_px=float(entry) + SIDE * TARGET_POINTS,')
        text=replace_once(text,'mae_points_observed=max(float(entry) - float(adverse), 0.0)',
                              'mae_points_observed=max((float(entry) - float(adverse)) * SIDE, 0.0)')
        if variant=='no_slope_gate':
            text=replace_once(text,'and b.slope > 0:',':')
        return text
    mod=source_module('codex_r2vault_replay.py',namespace={
        'prepare_observed_bars':a0.prepare_bars,'_gap_records':a0._gap_records,
        'is_early_close':calendar.is_early_close,'SIDE':-1 if variant=='fade_break' else 1},transform=change)
    if variant=='no_R2_gate':mod.R2_THRESHOLD=1.
    if variant=='no_stop':mod.STOP_POINTS=np.inf
    return mod


def s03_module(variant,original=False):
    def change(text):
        old='want = 1 if cc > ub and cc > vw and (state[0] != 1) else -1 if cc < lb and cc < vw and (state[0] != -1) else 0'
        new=('virtual = state[0] * DIRECTION\n'
             '                want = 1 if (cc > ub or not USE_BAND) and (cc > vw or not USE_VWAP) and virtual != 1 else '
             '-1 if (cc < lb or not USE_BAND) and (cc < vw or not USE_VWAP) and virtual != -1 else 0')
        text=replace_once(text,old,new)
        text=replace_once(text,'close = state[0] == 1 and cc < max(ub, vw) or (state[0] == -1 and cc > min(lb, vw))',
                              'close = virtual == 1 and cc < max(ub, vw) or (virtual == -1 and cc > min(lb, vw))')
        return replace_once(text,'state[8] = want','state[8] = want * DIRECTION')
    return source_module('codex_s03_v2_replay.py',functions={'source_calendar','features','stop_level','emit','engine','ledger','fixtures'},
        constants={'COLS','REASONS'},namespace={'DIRECTION':-1 if variant=='fade_direction' else 1,
                'USE_BAND':variant!='no_entry_band','USE_VWAP':variant!='no_entry_VWAP'},
        transform=None if original else change)


def parity(new,old):
    check(len(new)==len(old),'Original source count differs')
    for col in ['entry_flat','exit_flat','side','entry','exit','gross_nq']:
        check(np.allclose(new[col],old[col],atol=1e-8),'Original source parity: '+col)


def canonical(t,family,variant,g,calendar):
    t=t.copy().reset_index(drop=True)
    check(len(t)>0,'Empty case')
    t['fm'],t['xm']=t.entry_flat.astype(int),t.exit_flat.astype(int)
    t['entry_date']=pd.to_datetime(g.ts[t.fm//1440]);t['exit_date_actual']=pd.to_datetime(g.ts[t.xm//1440])
    t['date']=t.exit_date_actual.map(H.book_date)
    t['family'],t['variant'],t['symbol']=family,variant,'NQ'
    t['raw_entry'],t['raw_exit']=t.entry,t.exit
    t['market_legs']=1+t.kind.ne(1).astype(int)
    t['gross']=t.gross_nq
    check(np.allclose(t.gross,(t.exit-t.entry)*t.side*20.),'Side/raw gross mismatch')
    t['commission'],t['slippage']=7.25,5.*t.market_legs
    t['net']=t.gross-t.commission-t.slippage
    t['micro_net']=t.gross/10-1.25-t.slippage/10
    t['extra_tick_cost_net']=t.net-t.slippage
    t['terminal']=False;t['Sunday_exit']=t.exit_date_actual.dt.dayofweek.eq(6)
    t['source_adverse_mark']=-t.mae_points_observed*20.-t.commission-t.slippage
    t['source_adverse_mark']=np.minimum(t.source_adverse_mark,t.net)
    t['missing_held_bars']=t.missing_held_minutes.astype(int)
    t['last_close_fallback']=False
    t['target_bar_ambiguous']=False # source causal OHLC convention, still no native-tick certification
    check(np.isfinite(t[['entry','exit','gross','net','source_adverse_mark']]).all().all(),'Nonfinite return/path')
    zero=np.zeros(g.o.size)
    d,marks=H.mark_daily(t,g,zero,calendar,20.)
    return t,d,marks


def filter_control(base,parent,calendar):
    # Multiple entries on the same date: match executable event, never date alone.
    if not base.fm.is_unique or not parent.fm.is_unique:
        return {'pure_nested_filter':False,'reason':'nonunique entry events'}
    q=base.merge(parent,on='fm',how='left',suffixes=('_b','_p'))
    pure=len(q)==len(base) and all(np.allclose(q[c+'_b'],q[c+'_p']) for c in ['side','entry','exit','net'])
    if not pure:return {'pure_nested_filter':False,'reason':'state/entry/exit schedules differ; paired whole-policy result only'}
    if not (base.entry_date.eq(base.exit_date_actual).all() and parent.entry_date.eq(parent.exit_date_actual).all()):
        return {'pure_nested_filter':True,'random_drops_run':False,'reason':'cross-date marks require per-trade contribution paths'}
    removed=parent[~parent.fm.isin(base.fm)];rng=np.random.default_rng(SEED)
    counts=base.groupby(base.date.dt.year).size().to_dict()
    pools={int(y):p for y,p in parent.groupby(parent.date.dt.year)}
    totals,dds=[],[]
    for _ in range(1000):
        chosen=pd.concat([p.iloc[rng.choice(len(p),counts.get(y,0),replace=False)] for y,p in pools.items()],ignore_index=True)
        daily=B.daily(chosen,calendar);totals.append(daily.sum());dds.append(R.max_dd(daily))
    actual=B.daily(base,calendar)
    return {'pure_nested_filter':True,'removed_n':len(removed),'removed_total':removed.net.sum(),
        'removed_mean':removed.net.mean(),'removed_t':B.tst(removed.net),'random_drops':1000,
        'random_profit_ge_actual':float(np.mean(np.array(totals)>=actual.sum())),
        'random_dd_le_actual':float(np.mean(np.array(dds)<=R.max_dd(actual)))}


def fixtures():
    calendar,a0,a,r0,s0=modules()
    a_checks=a0.synthetic_checks();r_checks=r0.synthetic_checks();s_checks=s0.fixtures()
    # Source Anson synthetic prices also establish isolated hold/direction changes.
    G=sys.modules['grid24'].Grid24;g=G.__new__(G);g.D=3;g.ts=pd.date_range('2018-01-01',periods=3).to_numpy()
    g.trading=np.arange(3);g.dates=np.array([20180101,20180102,20180103])
    prices=100.+np.arange(4320).reshape(3,1440)*.5
    g.o,g.c,g.h,g.l,g.v=prices.copy(),prices+.25,prices+1.,prices-1.,np.ones_like(prices)
    p=a0.prepare_bars(g);base=a.replay(g,'original',prepared=p).trades
    parity(base,a0.replay(g,'intended_apex',prepared=p).trades)
    a.DIRECTION=-1;fade=a.replay(g,'fade_direction',prepared=p).trades
    check(np.array_equal(base.entry_flat,fade.entry_flat) and np.allclose(base.gross_nq,-fade.gross_nq),'Anson fade schedule')
    a.DIRECTION=1;short=a.replay(g,'hold_6',prepared=p).trades
    check(short.bars_held.iloc[-1]<=6 and (short.bars_held==6).any(),'Isolated six-bar hold')
    r=r2_module('fade_break',a0,calendar)
    x=r.entering_minute(100.,230.,10.,180.,140.)
    check(x[0] and x[2]==2 and x[3] and x[4]==215. and x[5]==0,'Fade consumes only post-break path')
    rn=r2_module('no_stop',a0,calendar)
    check(not rn.held_minute(100.,110.,-1000.,100.,100.,1)[0],'R2 infinite stop still fires')
    so=s03_module('original');sf=s03_module('fade_direction');sn=s03_module('no_sigma_stop')
    shape=(1,1440);o=np.full(shape,100.);h=o+1;l=o-1;c=o.copy();obs=np.ones(shape,bool)
    f=np.full((1,12,7),np.nan);f[0,0]=[99.,98.,99.,.1,100.,1.,0.]
    initial=np.zeros(14);initial[9]=-1
    b,_=so.engine(o,h,l,c,obs,f,np.zeros(1,bool),0,902,initial,.4,True,0)
    q,_=sf.engine(o,h,l,c,obs,f,np.zeros(1,bool),0,902,initial,.4,True,0)
    check(len(b)==len(q)==1 and b[0,0]==1 and q[0,0]==-1 and b[0,3]==q[0,3],'S03 virtual/actual direction')
    parity_s,_=s0.engine(o,h,l,c,obs,f,np.zeros(1,bool),0,902,initial,.4,True,0)
    check(np.array_equal(b,parity_s,equal_nan=True),'S03 original transform identity')
    # A signal between band and VWAP isolates which entry gate is removed.
    f[0,0]=[101.,98.,99.,.1,100.,1.,0.]
    band_off=s03_module('no_entry_band')
    no,_=so.engine(o,h,l,c,obs,f,np.zeros(1,bool),0,902,initial,.4,True,0)
    yes,_=band_off.engine(o,h,l,c,obs,f,np.zeros(1,bool),0,902,initial,.4,True,0)
    check(len(no)==0 and len(yes)>0,'Band-off entry gate fixture')
    l[0,541]=90.;f[0,0]=[99.,98.,99.,.1,100.,1.,0.]
    stop,_=so.engine(o,h,l,c,obs,f,np.zeros(1,bool),0,542,initial,.4,True,0)
    no_stop,state=sn.engine(o,h,l,c,obs,f,np.zeros(1,bool),0,542,initial,0.,True,0)
    check(len(stop)==1 and len(no_stop)==0 and state[0]==1,'S03 no-stop activation')
    return {'source_anson':a_checks,'source_r2':r_checks,'source_s03':s_checks,
            'new_intervention_checks_passed':7,'market_returns_computed':False}


def run(phase):
    dependencies=['analysis/metrics.py','analysis/resampling.py','analysis/codex_ingredients_three_20261108.py',
        'analysis/codex_ingredients_events_20261108.py','analysis/codex_ingredients_s30_s47_kusho_20261108.py']
    for path in [PLAN,CODE,EVIDENCE]+dependencies+[p.relative_to(ROOT).as_posix() for p in INPUT.iterdir()]:
        check(subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT)==(ROOT/path).read_bytes(),'Commit exact files before returns: '+path)
    for item in json.loads((INPUT/'sources.json').read_text())['files']:
        check(sha(INPUT/item['retained'])==item['sha256'],'Source hash mismatch')
    if phase=='recent':
        saved=json.loads((OUT/'design/summary.json').read_text())
        check(saved['implementation_gates_passed'] and saved['script_sha256']==sha(ROOT/CODE),'Design gate changed')
    start,end=('2018-01-01','2022-12-30') if phase=='design' else ('2023-01-01','2026-10-09')
    checks=fixtures()
    g,unused_es,inputs=B.grids(end);del unused_es
    calendar=pd.bdate_range(start,end)
    cal,a0,a,r0,s0=modules()
    pa=a0.prepare_bars(g,end);pr=r0.prepare(g,end)
    holiday,half=s0.source_calendar(g.ts)
    observed=np.logical_and.reduce([np.isfinite(getattr(g,k)) for k in ('o','h','l','c','v')])
    f,fa=s0.features(g.o,g.h,g.l,g.c,g.v,observed,holiday|half)
    ps={'f':f,'feature_audit':fa,'observed':observed,'known_closed':pr.known_closed}
    early=np.array([cal.is_early_close(x) for x in pd.DatetimeIndex(g.ts)],bool)
    dest=OUT/phase;dest.mkdir(parents=True,exist_ok=False)
    # Feature-only evidence, saved before invoking any real-price replay.
    import hashlib
    feature_hash=lambda x:hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()
    B.dump(dest/'pre_return_admission.json',{'start':start,'end':end,'raw_inputs':inputs,'fixture_receipt':checks,
        'feature_sha256':{'anson':feature_hash(pa.bars[['momentum','average_range','strength']].to_numpy()),
                          'r2':feature_hash(pr.bars[['slope','r2']].to_numpy()),'s03':feature_hash(f)},
        'source_ref':json.loads((INPUT/'sources.json').read_text())['ref'],
        'versions':{n:__import__(n).__version__ for n in ['numpy','pandas','numba','openpyxl','scipy','sklearn']}})
    pa.bars.groupby('date').agg(observed_chart_bars=('bar_index','size'),partial_bars=('observed_minute_count',lambda x:int((x<5).sum()))).to_csv(dest/'five_minute_feature_days.csv')
    pd.DataFrame({'date':pd.to_datetime(g.ts),'source_holiday':holiday,'source_half':half,
                  'first_RTH_j':fa[:,0],'observed_RTH':fa[:,1],'accepted':fa[:,2],'prior_days':fa[:,3]}).to_csv(dest/'S03_feature_days.csv',index=False)
    results,dailies,stats,parities,marks,audits={},{},[],{},{},{}
    for family,names in FAMILIES.items():
        for variant in names:
            if family=='ANSON':
                a.DIRECTION=-1 if variant=='fade_direction' else 1
                result=a.replay(g,variant,end,start_date=start,prepared=pa);raw=result.trades
                check(not result.events.event.eq('unclosed_position_at_cutoff').any(),'Open Anson boundary position')
                if variant=='original':
                    source=a0.replay(g,'intended_apex',end,start_date=start,prepared=pa).trades
                    parity(raw,source);parities[family]=len(raw)
                result.audit.to_csv(dest/(family+'__'+variant+'_source_audit.csv'),index=False)
            elif family=='R2':
                rr=r2_module(variant,a0,cal)
                result=rr.replay(g,'ct_apex',end,start_date=start,prepared=pr);raw=result.trades
                check(len(result.open_positions)==0,'Open R2 boundary position')
                if variant=='original':
                    source=r0.replay(g,'ct_apex',end,start_date=start,prepared=pr).trades
                    parity(raw,source);parities[family]=len(raw)
                if variant=='no_stop':check(raw.kind.ne(0).all(),'Infinite R2 stop executed')
                result.audit.to_csv(dest/(family+'__'+variant+'_source_audit.csv'),index=False)
            else:
                ss=s03_module(variant);initial=np.zeros(14);initial[9]=-1
                first=int(pd.DatetimeIndex(g.ts).searchsorted(start))*1440
                factor=0. if variant=='no_sigma_stop' else .4
                buf,state=ss.engine(g.o,g.h,g.l,g.c,observed,f,early,0,g.o.size,initial,factor,True,first)
                check(state[0]==0,'Open S03 boundary position')
                raw=ss.ledger(g,buf,variant,ps)
                if variant=='original':
                    original,_=s0.engine(g.o,g.h,g.l,g.c,observed,f,early,0,g.o.size,initial,.4,True,first)
                    source=s0.ledger(g,original,'v2_apex',ps);parity(raw,source);parities[family]=len(raw)
                if variant=='no_sigma_stop':check(raw.kind.ne(0).all(),'Disabled sigma stop executed')
            t,d,receipt=canonical(raw,family,variant,g,calendar)
            key,stem=family+'/'+variant,family+'__'+variant
            results[key],dailies[key],marks[key]=t,d,receipt
            t.to_csv(dest/(stem+'_trades.csv'),index=False)
            for side in ('all','long','short'):
                sub=t if side=='all' else t[t.side.eq(1 if side=='long' else -1)]
                sd,_=H.mark_daily(sub,g,np.zeros(g.o.size),calendar,20.)
                sd.to_csv(dest/(stem+'_'+side+'_daily.csv'),index_label='date')
                stats.append({'family':family,'variant':variant,'period':phase,'side':side,**H.metrics(sub,sd)})
                for year in sorted(set(calendar.year)):
                    stats.append({'family':family,'variant':variant,'period':str(year),'side':side,
                                  **H.metrics(sub[sub.date.dt.year.eq(year)],sd[sd.index.year==year])})
            audits[key]={'cross_date':int(t.entry_date.ne(t.exit_date_actual).sum()),
                'unknown_held_minutes':int(t.unknown_held_minutes.sum()),
                'late_after_1559':int(t.late_after_1559.sum()),
                'tainted_history_trades':int(t.tainted_prior_sessions.gt(0).sum()) if family=='S03' else None}
            print(phase,key,len(t),'priced; source gates passed',flush=True)
    effects=[]
    for family,names in FAMILIES.items():
        base=dailies[family+'/original'].net
        R.bootstrap(base,n=1000,block=20,seed=SEED,chunk=250).loc[['annual','sharpe']].to_csv(dest/(family+'_original_bootstrap.csv'))
        for variant in names[1:]:
            delta=base-dailies[family+'/'+variant].net
            ci=R.bootstrap(delta,n=1000,block=20,seed=SEED,chunk=250).loc['annual']
            effects.append({'family':family,'intervention':variant,'base_minus_intervention_net':delta.sum(),
                            'annual_effect_p5':ci.p5,'annual_effect_p50':ci.p50,'annual_effect_p95':ci.p95})
    control_keys=['ANSON/no_strength_gate','R2/no_R2_gate','R2/no_slope_gate','S03/no_entry_VWAP','S03/no_entry_band']
    controls={key:filter_control(results[key.split('/')[0]+'/original'],results[key],calendar) for key in control_keys}
    pd.DataFrame(stats).to_csv(dest/'metrics.csv',index=False)
    pd.DataFrame(effects).to_csv(dest/'paired_effects.csv',index=False)
    B.dump(dest/'marking_receipts.json',marks)
    B.dump(dest/'summary.json',{'phase':phase,'start':start,'end':end,'rule_cases':15,'implementation_gates_passed':True,
        'script_sha256':sha(ROOT/CODE),'plan_sha256':sha(ROOT/PLAN),
        'plan_commit':subprocess.check_output(['git','log','-1','--format=%H','--',PLAN],cwd=ROOT,text=True).strip(),
        'source_price_parity':parities,'filter_controls':controls,'path_audits':audits,
        'seed':SEED,'draws':1000,'dependency_sha256':{p:sha(ROOT/p) for p in dependencies},
        'new_rule_selected':False,'portfolio_tests_run':False})
    print(pd.DataFrame(stats).query('period==@phase and side=="all"')
          [['family','variant','trades','avg','t_trade','net_total','max_dd']].round(2).to_string(index=False))
    print(json.dumps({'phase':phase,'gates':True,'source_price_parity':parities}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('phase',choices=['fixtures','design','recent'])
    args=parser.parse_args()
    if args.phase=='fixtures':print(json.dumps(fixtures(),indent=2))
    else:run(args.phase)
