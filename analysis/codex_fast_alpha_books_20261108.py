"""Bounded user-requested execution study. Import/selftest never reads market data.

Replay the frozen parent signal/fill-event stream, preserving its source price
levels and virtual state. This is an execution wrapper, not a reoptimized alpha.
Every price outcome is guarded by a committed config, code and checked lease.
"""
from pathlib import Path
import argparse
import ast
import datetime as dt
import gc
import hashlib
import importlib.util
import json
import subprocess
from types import SimpleNamespace

import numpy as np
import pandas as pd
from grid24 import Grid24
import metrics as M
from codex_eval_paths_20261104 import common_path, crossing_phase, civil_closure_mask

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'agents/codex/inputs/fast_alpha_books_20261108'
OUT = ROOT / 'analysis/outputs/codex_fast_alpha_books_20261108'
RUNTIME = ROOT / 'agents/codex/runtime/fast_alpha_books_20261108'
SCRIPT = 'analysis/codex_fast_alpha_books_20261108.py'


def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def dump(p, value):
    def clean(x):
        if isinstance(x, dict): return {str(k): clean(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)): return [clean(v) for v in x]
        if isinstance(x, np.generic): return clean(x.item())
        if isinstance(x, float) and not np.isfinite(x): return None
        return x
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(clean(value), indent=2, default=str) + '\n')


def verify(commit):
    cfg = json.loads((BASE / 'config.json').read_text())
    for name in cfg['frozen_files']:
        assert subprocess.check_output(['git', 'show', commit + ':' + name], cwd=ROOT) == (ROOT/name).read_bytes(), name
    for name, expected in cfg['input_sha256'].items():
        assert sha(ROOT/name) == expected, name
    p = json.loads((BASE/'progress.json').read_text())
    lease = p['lease']
    assert p['program'] == cfg['program'] and lease['owner'] == 'codex-fast-alpha-books'
    assert lease['run_id'] == cfg['program']
    assert set(r['id'] for r in p['definitions']) == set(v for s in cfg['parents'] for v in s['new_definition_ids'])
    assert dt.datetime.fromisoformat(lease['claimed_at']) <= dt.datetime.now(dt.timezone.utc)
    assert dt.datetime.fromisoformat(lease['expires_at'])-dt.datetime.fromisoformat(lease['claimed_at']) <= dt.timedelta(hours=2)
    assert dt.datetime.fromisoformat(lease['expires_at']) > dt.datetime.now(dt.timezone.utc)
    assert p['max_definitions'] == len(cfg['parents'])*5 == len(p['definitions'])
    assert len({r['id'] for r in p['definitions']}) == len(p['definitions'])
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    assert head == subprocess.check_output(['git','rev-parse','origin/codex/work'],cwd=ROOT,text=True).strip()
    assert head == subprocess.check_output(['git','rev-parse','FETCH_HEAD'],cwd=ROOT,text=True).strip()
    assert subprocess.check_output(['git','show',head+':'+str((BASE/'progress.json').relative_to(ROOT))],cwd=ROOT) == (BASE/'progress.json').read_bytes()
    return cfg


def grid(cfg, market):
    folder=RUNTIME/'links'/market; folder.mkdir(parents=True,exist_ok=True)
    files=[ROOT/p for p in cfg['raw_files'] if Path(p).name.startswith(market+'_')]
    for p in files:
        dest=folder/p.name
        if not dest.exists(): dest.symlink_to(p)
        assert dest.resolve()==p.resolve()
    assert {p.name for p in folder.glob('*.csv')}=={p.name for p in files}
    return Grid24(str(folder/(market+'_1min_20*.csv')),str(folder/'NQ_1min_ON_20*.csv') if market=='NQ' else '')


def stamp(d, hhmm):
    d=pd.to_datetime(d).dt.normalize(); t=pd.to_numeric(hhmm).astype(int)
    return d+pd.to_timedelta(t//100*60+t%100,unit='min')


def classify(label):
    s=str(label).lower()
    if s in {'0','0.0','stop','stop loss','break_even','breakeven'} or 'stp' in s or 'stop' in s: return 'stop'
    if s in {'1','1.0'} or 'target' in s or 'profit' in s: return 'target'
    if s in {'band/ema exit','reverse exit','reverse','signal'}: return 'signal'
    return 'time'


def kusho_origin(t):
    origins=pd.to_datetime(t.date).dt.normalize()-pd.to_timedelta((t.fm//1440).astype(int),unit='D')
    assert origins.nunique()==1,'Inconsistent explicit Kusho date/index origins'
    return pd.Timestamp(origins.iloc[0])


def generated(spec,g):
    typ=spec['adapter']
    if typ.startswith('twin'):
        p=BASE/'source/analysis/twin_continuation_test.py'
        sp=importlib.util.spec_from_file_location('frozen_fast_twin',p); mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
        b=mod.flatten(g); t=mod.simulate(b,max_stop_mult=1.0 if typ=='twin_cap1' else 0.0,v21=True)
        z=pd.DataFrame(dict(entry_at=pd.to_datetime(t.edate)+pd.to_timedelta(t.ej,unit='min'),
            exit_at=pd.to_datetime(t.date)+pd.to_timedelta(t.xj,unit='min'),entry=t.entry,exit=t.exit,
            side=t.side,kind=t.kind))
        z['setup']=t.setup.to_numpy(); z['source_generated']=True
        return z
    text=(BASE/'source/analysis/bridge_noise_15m_test.py').read_text();tree=ast.parse(text)
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'series','ema','run'}]
    env=dict(g=g,B=g.bars(15),TR=set(g.trading.tolist()),np=np,pd=pd,PV=20.,TICK=.25,COMM=7.25,NTRIAL={'n':0})
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(BASE/'source/analysis/bridge_noise_15m_test.py'),'exec'),env)
    t=env['run'](env['series']('24h'),shorts=False,anchor=(845,1500),early_flat=True,count=False)
    z=pd.DataFrame(dict(entry_at=t.date+pd.to_timedelta(t.j0,unit='min'),exit_at=t.date+pd.to_timedelta(t.j1,unit='min'),
        entry=t.entry-t.side*.25,exit=t.exit+t.side*.25*(t.kind!='target'),side=t.side,kind=t.kind))
    z['source_generated']=True
    return z


def load_parent(spec,g,cfg):
    typ=spec['adapter'];pv=cfg['markets'][spec['market']]['pv'];tick=cfg['markets'][spec['market']]['tick']
    if spec['path']:
        t=pd.read_csv(ROOT/spec['path'])
        origin=kusho_origin(t) if typ=='kusho' else None
        ec='entry_at' if typ=='unit' else 'date'
        xc='exit_at' if typ=='unit' else 'exit_date' if 'exit_date' in t else 'date'
        t=t[(pd.to_datetime(t[ec])>=cfg['design_start'])&(pd.to_datetime(t[xc])<pd.Timestamp(cfg['design_end'])+pd.Timedelta(days=1))].copy()
    if typ=='unit':
        z=t[['entry_at','exit_at','entry','exit','side','kind']].copy()
        z['source_gross']=t.gross/t.qty
    elif typ=='mc_csv':
        z=t[['entry','exit','side','kind']].copy();z['entry_at']=stamp(t.date,t.t_in);z['exit_at']=stamp(t.exit_date,t.t_out)
        if spec['key']=='PT':
            z['entry_at']-=pd.Timedelta(minutes=4)
            z['entry_open_required']=True
    elif typ=='s47':
        z=t[['entry','exit','side','kind']].copy();z['entry_at']=pd.to_datetime(t.date)+pd.to_timedelta(t.j0,unit='min');z['exit_at']=pd.to_datetime(t.date)+pd.to_timedelta(t.j1,unit='min')
    elif typ=='kusho':
        z=t[['entry','exit','side','kind']].copy();start=origin
        z['entry_at']=start+pd.to_timedelta(t.fm,unit='min');z['exit_at']=start+pd.to_timedelta(t.xm,unit='min')
        assert (z.entry_at.dt.normalize()==pd.to_datetime(t.date).dt.normalize()).all(),'Kusho index origin mismatch'
        z['exit']+=t.side*tick*(t.kind!='target')
    elif typ=='s30':
        z=pd.DataFrame(dict(entry_at=pd.to_datetime(t.date)+pd.Timedelta(hours=15,minutes=1),
            exit_at=pd.to_datetime(t.exit_date)+pd.Timedelta(hours=15,minutes=1),entry=t.e_px-t.side*tick,
            exit=t.x_px+t.side*tick,side=t.side,kind='signal'))
        z['source_gross']=(t.net+t.comm+2*tick*(pv*10))/10
    else: z=generated(spec,g)
    z['entry_at']=pd.to_datetime(z.entry_at);z['exit_at']=pd.to_datetime(z.exit_at)
    z=z[(z.entry_at>=cfg['design_start'])&(z.exit_at<pd.Timestamp(cfg['design_end'])+pd.Timedelta(days=1))].copy()
    z=z.sort_values(['entry_at','exit_at'],kind='stable').reset_index(drop=True)
    z['kind']=z.kind.map(classify)
    assert z.side.isin([-1,1]).all() and (z.exit_at>=z.entry_at).all()
    if 'source_gross' not in z:z['source_gross']=(z.exit-z.entry)*z.side*pv
    z['entry_cost_ticks']=0 if typ=='kusho' else 1
    z['exit_cost_ticks']=(z.kind!='target').astype(int)
    z['ticket_id']=np.arange(len(z));z['parent']=spec['key']
    return z


def market_arrays(g,market,cfg):
    o,h,l,c=(getattr(g,k).ravel() for k in ['o','h','l','c'])
    dates=pd.DatetimeIndex(g.ts);dow=np.repeat(dates.dayofweek,1440);j=np.tile(np.arange(1440),g.D)
    rules=json.loads((ROOT/'agents/codex/inputs/eval_audit_20261104/config.json').read_text())['market_closures']
    closed=civil_closure_mask(g,market,rules).ravel()
    closed|=(dow==5)|((dow==6)&(j<=1020))|((dow==4)&(j>960))
    finite=np.isfinite(o)&np.isfinite(h)&np.isfinite(l)&np.isfinite(c)
    bad=(~finite)&(~closed)
    prefix=np.r_[0,np.cumsum(bad,dtype=np.int64)]
    return SimpleNamespace(o=o,h=h,l=l,c=c,closed=closed,bad=bad,prefix=prefix,start=pd.Timestamp(g.ts[0]),end=len(o),pv=cfg['markets'][market]['pv'],tick=cfg['markets'][market]['tick'])


def missing(a,lo,hi):
    if lo<0 or hi>=a.end or hi<lo:return 1
    return int(a.prefix[hi+1]-a.prefix[lo])


def counter(a,start,stop,side,want):
    """A signal bar must end strictly after the source event; next minute OPEN fills."""
    k=(int(start)//5+1)*5
    while k+1<=stop:
        if missing(a,start+1,k+1):return -1,True
        if k>=5 and not a.closed[k] and not missing(a,k-5,k):
            if side*want*(a.c[k]-a.c[k-5])>0:
                q=k+1
                while q<=stop and a.closed[q]:q+=1
                if q>stop:return -1,False
                if np.isfinite(a.o[q]):return q,False
                return -1,True
        k+=5
    return -1,False


def deadline(spec,r,a):
    if spec['deadline_hhmm'] is None:return a.end-2,'none'
    day=pd.Timestamp(r.entry_at).normalize()
    if spec['key'] in {'BRIDGE','CLS'}:day=pd.Timestamp(r.exit_at).normalize()
    if spec['key'].startswith('TWIN'):
        hm=1451 if getattr(r,'setup','BO')=='MO' else 1545
        if r.entry_at.hour*60+r.entry_at.minute>hm//100*60+hm%100:day+=pd.Timedelta(days=1)
    else:hm=spec['deadline_hhmm']
    quote='open' if spec['key'].startswith('TWIN') and getattr(r,'setup','BO')=='MO' else spec['deadline_quote']
    from replica import is_early_close
    if is_early_close(day) and spec['key'] not in {'CLS','MOC','KUSHO','NFP','EOS','TOS','OT'}:
        hm=1131 if spec['key']=='NBL' else 1130
    point=int((day-a.start).total_seconds()/60)+hm//100*60+hm%100
    return point,quote


def fill_match(a,k,p):
    return 0<=k<a.end and not a.closed[k] and np.isfinite(p) and np.isfinite([a.o[k],a.h[k],a.l[k],a.c[k]]).all() and a.l[k]-1e-7<=p<=a.h[k]+1e-7


def replay(t,spec,a,cfg,profile):
    rows=[];busy=-1
    for r in t.itertuples():
        b=int((r.entry_at-a.start).total_seconds()/60);x=int((r.exit_at-a.start).total_seconds()/60)
        row=dict(ticket_id=r.ticket_id,parent=spec['key'],profile=profile,side=r.side,entry_at=r.entry_at,exit_at=r.exit_at,
            original_entry=r.entry,original_exit=r.exit,kind=r.kind,status='filled',missed=0,unknown=0,source_missing=0,entry_delay=0,exit_delay=0,
            entry=r.entry,exit=r.exit,gross=np.nan,fee=0.,slippage=0.,net=np.nan,stress_net=np.nan,max_adverse=np.nan)
        source_missing=missing(a,b,x)
        if source_missing or not fill_match(a,b,r.entry) or not fill_match(a,x,r.exit):
            row.update(status='unknown_source_path_or_fill',unknown=1,source_missing=source_missing);rows.append(row);continue
        if bool(getattr(r,'entry_open_required',False)) and not np.isclose(a.o[b],r.entry,rtol=0,atol=1e-7):
            row.update(status='unknown_required_source_open',unknown=1);rows.append(row);continue
        if b==x:
            path=common_path(np.array([a.o[b],a.h[b],a.l[b],a.c[b]]))
            phase=crossing_phase(path,float(r.entry))
            if not np.isfinite(phase) or not np.isfinite(crossing_phase(path,float(r.exit),lower=phase)):
                row.update(status='unknown_same_minute_order',unknown=1);rows.append(row);continue
        if r.kind=='target':
            through=1.0 if spec['market'] in {'NQ','ES'} else .01
            if (a.h[x]-r.exit if r.side>0 else r.exit-a.l[x])<through-1e-9:
                row.update(status='unknown_target_trade_through',unknown=1);rows.append(row);continue
        eb,ex=b,x;ep,xp=r.entry,r.exit
        eticks,xticks=int(r.entry_cost_ticks),int(r.exit_cost_ticks)
        if profile!='BASE' and b<=busy:
            row.update(status='suppressed_while_previous_execution_pending',missed=1,gross=0.,net=0.,stress_net=0.);rows.append(row);continue
        if profile in {'ENTRY','BOTH'}:
            eb,unknown=counter(a,b,x-1,int(r.side),-1)
            if unknown:
                row.update(status='unknown_entry_wait',unknown=1);rows.append(row);continue
            if eb<0:
                row.update(status='cancelled_at_parent_exit',missed=1,gross=0.,net=0.,stress_net=0.);rows.append(row);continue
            ep=a.o[eb];eticks=1
        if profile=='BOTH' and r.kind in {'stop','signal'}:
            end,quote=deadline(spec,r,a)
            if end<x:
                row.update(status='unknown_source_deadline',unknown=1);rows.append(row);continue
            ex,unknown=counter(a,x,min(end-1,a.end-2),int(r.side),1)
            if unknown:
                row.update(status='unknown_exit_wait',unknown=1);rows.append(row);continue
            if ex<0:
                if end>=a.end or quote=='none':
                    row.update(status='unresolved_terminal_exit',unknown=1);rows.append(row);continue
                ex=end;xp=a.o[ex] if quote=='open' else a.c[ex]
            else:xp=a.o[ex]
            xticks=1
        held_missing=missing(a,eb,ex)
        if held_missing or not np.isfinite([ep,xp]).all():
            row.update(status='unknown_candidate_held_path',unknown=1,source_missing=held_missing);rows.append(row);continue
        # Only the execution endpoints change. Original source roll/cash adjustment is retained.
        # No changed interval may include a potential quarter-roll clock without native roll reconciliation.
        if (eb!=b or ex!=x) and spec['market'] in {'NQ','ES'}:
            changed=np.r_[np.arange(b,eb+1),np.arange(x,ex+1)]
            times=a.start+pd.to_timedelta(changed,unit='min')
            old=times.year*100+times.month<=202203
            rd=np.isin(times.month,[3,6,9,12])&np.where(old,(times.dayofweek==4)&(times.day>=8)&(times.day<=14),(times.dayofweek==0)&(times.day>=11)&(times.day<=17))
            roll_clock=np.isin(times.hour*60+times.minute,[212,1021])
            if (rd&roll_clock).any():
                row.update(status='unknown_changed_roll_interval',unknown=1);rows.append(row);continue
        gross=float(r.source_gross+(r.entry-ep+xp-r.exit)*r.side*a.pv)
        slip=(eticks+xticks)*a.tick*a.pv;fee=cfg['commission_RT']
        adverse=np.nanmin(a.l[eb:ex+1]) if r.side>0 else np.nanmax(a.h[eb:ex+1])
        row.update(entry_at=a.start+pd.Timedelta(minutes=eb),exit_at=a.start+pd.Timedelta(minutes=ex),entry=ep,exit=xp,
            entry_delay=eb-b,exit_delay=ex-x,gross=gross,fee=fee,slippage=slip,net=gross-fee-slip,
            stress_net=gross-cfg['stress_commission_RT']-2*slip,max_adverse=max(0.,(ep-adverse)*r.side*a.pv)+fee/2+eticks*a.tick*a.pv)
        busy=ex;rows.append(row)
    return pd.DataFrame(rows)


def daily(t,days):
    # Conditional complete-ticket contributions. Not a full book or broker-equity series.
    book=pd.DatetimeIndex(pd.to_datetime(t.exit_at)).normalize()
    book=book+pd.to_timedelta(np.where(book.dayofweek==6,1,np.where(book.dayofweek==5,2,0)),unit='D')
    return pd.Series(t.net.to_numpy(),index=book).groupby(level=0).sum().reindex(days,fill_value=0.)


def tstat(x):
    x=np.asarray(x,float);return float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))) if len(x)>2 and x.std(ddof=1)>0 else 0.


def design(commit):
    cfg=verify(commit);OUT.mkdir(parents=True,exist_ok=True)
    days=pd.bdate_range(cfg['design_start'],cfg['design_end']);summary=[];standard=[];dispositions=[]
    prior=max(10000,int(pd.read_csv(ROOT/'TRIALS.csv').variants.fillna(1).sum()))+cfg['max_definitions']+58
    for market in cfg['markets']:
        print('Loading design-only',market,flush=True);g=grid(cfg,market);a=market_arrays(g,market,cfg)
        for spec in [s for s in cfg['parents'] if s['market']==market]:
            key=spec['key']; print('Parent',key,flush=True)
            try:t=load_parent(spec,g,cfg)
            except Exception as exc:
                dispositions.append(dict(parent=key,status='source_adapter_blocked',error=repr(exc)));continue
            t.to_csv(OUT/(key+'_parent_tickets.csv'),index=False)
            streams={name:replay(t,spec,a,cfg,name) for name in ['BASE','ENTRY','BOTH']}
            if len(t)==0:
                dispositions.append(dict(parent=key,status='no_design_tickets'));continue
            good=np.logical_and.reduce([z.unknown.eq(0).to_numpy() for z in streams.values()])
            b=streams['BASE'][good];bd=daily(b,days);full_known=bool(good.all())
            for name,z in streams.items():
                z.to_csv(OUT/(key+'_'+name+'_tickets.csv'),index=False)
                q=z[good];d=daily(q,days);d.to_csv(OUT/(key+'_'+name+'_conditional_daily.csv'),header=['net'])
                perf=M.perf(d,q.net);effect=d-bd
                common=dict(parent=key,profile=name,source_tickets=len(t),common_resolved=int(good.sum()),
                    unknown_this_profile=int(z.unknown.sum()),joint_unknown=int((~good).sum()),missed=int(q.missed.sum()),
                    total=float(q.net.sum()),gross=float(q.gross.sum()),commission=float(q.fee.sum()),slippage=float(q.slippage.sum()),
                    stress_total=float(q.stress_net.sum()),effect_total=float(effect.sum()),effect_annual=float(effect.sum()/(len(days)/252)),
                    paired_daily_t=tstat(effect),effect_dsr=float(M.deflated_sharpe(effect,prior)),multiplicity_t_bar=M.t_threshold(prior),
                    years_positive=int((d.groupby(d.index.year).sum()>0).sum()),**perf)
                assert np.isclose(q.net.sum(),d.sum()),key
                if len(q):assert np.isclose(q.net.sum(),q.gross.sum()-q.fee.sum()-q.slippage.sum()),key
                summary.append(common)
                for side,label in [(0,'whole'),(1,'long'),(-1,'short')]:
                    for year in ['design',2018,2019,2020,2021,2022]:
                        qq=q if side==0 else q[q.side==side]
                        dd=days if year=='design' else days[days.year==year]
                        qq=qq if year=='design' else qq[pd.to_datetime(qq.exit_at).dt.year==year]
                        vv=daily(qq,dd);standard.append(dict(parent=key,profile=name,side=label,period=year,trade_t=tstat(qq.net),**M.perf(vv,qq.net)))
            options=[s for s in summary if s['parent']==key and s['profile']!='BASE']
            for s in options:
                s['cheap_pass']=bool(full_known and s['common_resolved']>=30 and s['total']>0 and s['stress_total']>0 and s['effect_total']>0 and s['paired_daily_t']>=s['multiplicity_t_bar'] and s['effect_dsr']>=.95 and s['years_positive']>=4)
            survivors=[s for s in options if s['cheap_pass']]
            dispositions.append(dict(parent=key,status='earned_controls' if survivors else 'stop_design',
                statistical_survivors=[s['profile'] for s in survivors],joint_unknown=int((~good).sum()),source_tickets=len(t),
                selection='largest paired effect among passing profiles, ENTRY before BOTH on ties',
                selected=max(survivors,key=lambda s:s['effect_total'])['profile'] if survivors else None,
                qualification='Frozen virtual parent-intent study; no actual account/capital recommendation without independent intent/risk parity and earned control/validation/account stages.'))
            pd.DataFrame(summary).to_csv(OUT/'design_summary.csv',index=False)
            dump(OUT/'design_dispositions.json',dispositions)
        del g,a;gc.collect()
    pd.DataFrame(summary).to_csv(OUT/'design_summary.csv',index=False)
    pd.DataFrame(standard).to_csv(OUT/'standard_metrics.csv',index=False)
    dump(OUT/'design_dispositions.json',dispositions)
    dump(OUT/'run.json',dict(program=cfg['program'],preregistration_commit=commit,checked_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        design_start=cfg['design_start'],design_end=cfg['design_end'],future_raw_ohlc_loaded=False,static_parent_ledgers_contain_already_seen_later_rows=True,new_overlay_results_2023plus_computed=False,definition_views_executed=sum(3 for d in dispositions if 'source_tickets' in d),
        controls_run=False,historical_validation_run=False,account_tests_run=False,dispositions=dispositions))


def selftest():
    n=80;o=np.full(n,100.);c=np.full(n,100.);h=np.full(n,101.);l=np.full(n,99.)
    a=SimpleNamespace(o=o,c=c,h=h,l=l,closed=np.zeros(n,bool),bad=np.zeros(n,bool),prefix=np.zeros(n+1,int),end=n,start=pd.Timestamp('2020-01-01'),pv=2.,tick=.25)
    c[10]=99.;assert counter(a,5,30,1,-1)==(11,False)
    assert counter(a,10,30,1,-1)[0]!=11
    assert counter(a,5,10,1,-1)==(-1,False)
    a.bad[10]=True;a.prefix=np.r_[0,np.cumsum(a.bad)];assert counter(a,5,30,1,-1)==(-1,True)
    a.bad[10]=False;a.prefix=np.zeros(n+1,int)
    c[10]=101.;assert counter(a,5,30,-1,-1)==(11,False)
    c[10]=99.;assert counter(a,5,30,-1,1)==(11,False)
    o[11]=np.nan;assert counter(a,5,30,1,-1)==(-1,True)
    assert classify('Profit Target')=='target' and classify('FT.LX.stp')=='stop' and classify('band/EMA exit')=='signal'
    origin=kusho_origin(pd.DataFrame(dict(date=['2018-01-01','2018-01-02'],fm=[31*1440+12,32*1440+13])))
    assert origin==pd.Timestamp('2017-12-01')
    o[11]=99.;o[26]=102.;h[26]=103.;c[25]=101.
    z=pd.DataFrame([dict(ticket_id=0,entry_at=a.start+pd.Timedelta(minutes=5),exit_at=a.start+pd.Timedelta(minutes=20),entry=100.,exit=100.,side=1,kind='stop',source_gross=0.,entry_cost_ticks=1,exit_cost_ticks=1)])
    sp=dict(key='FIXTURE',market='NQ',deadline_hhmm=None,deadline_quote='none')
    cfg=dict(commission_RT=1.24,stress_commission_RT=2.48)
    b=replay(z,sp,a,cfg,'BASE');e=replay(z,sp,a,cfg,'ENTRY');both=replay(z,sp,a,cfg,'BOTH')
    assert np.isclose(b.net.iloc[0],-2.24) and np.isclose(e.net.iloc[0],-.24)
    assert np.isclose(both.net.iloc[0],3.76) and both.exit_delay.iloc[0]==6
    z['exit_at']=a.start+pd.Timedelta(minutes=6)
    skipped=replay(z,sp,a,cfg,'ENTRY');assert skipped.missed.iloc[0]==1 and skipped.net.iloc[0]==0
    print('Invented signal-clock, entry/exit, cancellation, unknown-price and native-fee cases passed; no market data loaded.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['selftest','design']);p.add_argument('--commit');args=p.parse_args()
    if args.action=='selftest':selftest()
    else:design(args.commit)
