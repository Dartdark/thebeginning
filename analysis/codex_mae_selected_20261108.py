"""Frozen direct-user 0.25% resting-limit experiment. Import/selftest uses no market data.

Original virtual-parent exit intents remain fixed. This is not a regenerated
alpha with newly fill-anchored brackets or a verified native account simulator.
"""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json
import subprocess
from types import SimpleNamespace

import numpy as np
import pandas as pd
import metrics as M
import codex_fast_alpha_books_20261108 as F

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'agents/codex/inputs/mae_selected_20261108'
OUT = ROOT/'analysis/outputs/codex_mae_selected_20261108'


def verify(commit):
    cfg = json.loads((BASE/'config.json').read_text())
    for name in cfg['frozen_files']:
        assert subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT) == (ROOT/name).read_bytes(), name
    for name, expected in cfg['input_sha256'].items():
        assert F.sha(ROOT/name) == expected, name
    p = json.loads((BASE/'progress.json').read_text()); lease = p['lease']
    assert p['program'] == cfg['program'] and lease['owner'] == 'codex-mae-selected'
    assert lease['run_id'] == cfg['program']
    now = dt.datetime.now(dt.timezone.utc)
    assert dt.datetime.fromisoformat(lease['claimed_at']) <= now < dt.datetime.fromisoformat(lease['expires_at'])
    assert dt.datetime.fromisoformat(lease['expires_at'])-dt.datetime.fromisoformat(lease['claimed_at']) <= dt.timedelta(hours=2)
    assert len(p['definitions']) == p['max_definitions'] == cfg['max_definitions'] == 15
    assert {d['id'] for d in p['definitions']} == {i for s in cfg['parents'] for i in s['new_definition_ids']}
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    assert all(head == subprocess.check_output(['git','rev-parse',ref],cwd=ROOT,text=True).strip()
               for ref in ['origin/codex/work','FETCH_HEAD'])
    assert subprocess.check_output(['git','show',head+':'+str((BASE/'progress.json').relative_to(ROOT))],cwd=ROOT) == (BASE/'progress.json').read_bytes()
    return cfg, p, head


def first_limit(a, b, x, side, limit):
    """First executable minute strictly after original entry, before original exit.

    Returns minute, raw fill, entry slippage main/stress, phase, error. Resting
    gap fills use the observed open plus adverse tick costs capped at the limit.
    Intrabar passive fills require one full native tick through, never a touch.
    """
    for k in range(b+1, x):
        if k < 0 or k >= a.end or a.bad[k]: return -1, np.nan, 0., 0., 0., 'unknown_wait'
        if a.closed[k]: continue
        if side*(a.o[k]-limit) <= -a.tick+1e-8:
            room = max(0., side*(limit-a.o[k]))
            return k, float(a.o[k]), min(a.tick,room)*a.pv, min(2*a.tick,room)*a.pv, 0., ''
        crossed = a.l[k] <= limit-a.tick+1e-8 if side > 0 else a.h[k] >= limit+a.tick-1e-8
        if crossed:
            path = F.common_path(np.array([a.o[k],a.h[k],a.l[k],a.c[k]]))
            phase = F.crossing_phase(path,limit)
            if not np.isfinite(phase): return -1, np.nan, 0., 0., 0., 'unknown_fill_phase'
            return k, limit, 0., 0., float(phase), ''
    return -1, np.nan, 0., 0., 0., ''


def changed_roll(a,b,e):
    times = a.start+pd.to_timedelta(np.arange(b,e+1),unit='min')
    old = times.year*100+times.month <= 202203
    day = np.isin(times.month,[3,6,9,12]) & np.where(old,(times.dayofweek==4)&(times.day>=8)&(times.day<=14),
                                                  (times.dayofweek==0)&(times.day>=11)&(times.day<=17))
    return bool((day & np.isin(times.hour*60+times.minute,[212,1021])).any())


def child(t,spec,a,cfg,base,delays=None):
    rows=[];busy=-1
    for r in t.itertuples():
        row = base.iloc[r.ticket_id].to_dict(); row['profile']='LIMIT025' if delays is None else 'RANDOM_TIME'
        row['limit']=np.nan; row['entry_phase']=0.; row['entry_slippage']=0.; row['stress_entry_slippage']=0.
        if row['unknown']:
            rows.append(row); continue
        b=int((r.entry_at-a.start).total_seconds()/60); x=int((r.exit_at-a.start).total_seconds()/60)
        row.update(gross=np.nan,net=np.nan,stress_net=np.nan,fee=0.,slippage=0.,max_adverse=np.nan)
        if b < busy:
            row.update(status='suppressed_previous_hold',missed=1,gross=0.,net=0.,stress_net=0.); rows.append(row); continue
        if delays is None:
            unrounded = float(r.entry)*(1-int(r.side)*cfg['offset'])/a.tick
            limit=(np.floor(unrounded+1e-10) if r.side>0 else np.ceil(unrounded-1e-10))*a.tick
            row['limit']=limit
            e,price,slip,sslip,phase,error=first_limit(a,b,x,int(r.side),float(limit))
        else:
            e=b+int(delays[r.ticket_id]);phase=0.;error=''
            if e>=x: e=-1
            elif F.missing(a,b+1,e): error='unknown_random_wait'
            elif a.closed[e]: e=-1
            price=a.o[e] if e>=0 else np.nan;slip=a.tick*a.pv;sslip=2*slip
        if error:
            row.update(status=error,unknown=1);rows.append(row);continue
        if e<0:
            row.update(status='cancelled_before_parent_exit',missed=1,gross=0.,net=0.,stress_net=0.);rows.append(row);continue
        if F.missing(a,e,x) or not F.fill_match(a,e,price) or changed_roll(a,b,e):
            row.update(status='unknown_held_fill_or_changed_roll',unknown=1);rows.append(row);continue
        exit_slip=float(r.exit_cost_ticks)*a.tick*a.pv
        gross=float(r.source_gross+(r.entry-price)*r.side*a.pv)
        path=F.common_path(np.array([a.o[e],a.h[e],a.l[e],a.c[e]]))
        suffix=np.r_[price,path[np.arange(4)>phase]]
        extreme=np.min(suffix) if r.side>0 else np.max(suffix)
        if x>e:
            later=np.min(a.l[e+1:x+1]) if r.side>0 else np.max(a.h[e+1:x+1])
            extreme=min(extreme,later) if r.side>0 else max(extreme,later)
        row.update(entry_at=a.start+pd.Timedelta(minutes=e),entry=price,entry_delay=e-b,
            entry_phase=phase,entry_slippage=slip,stress_entry_slippage=sslip,
            gross=gross,fee=cfg['commission_RT'],slippage=slip+exit_slip,net=gross-cfg['commission_RT']-slip-exit_slip,
            stress_net=gross-cfg['stress_commission_RT']-sslip-2*exit_slip,
            max_adverse=max(0.,(price-extreme)*r.side*a.pv)+cfg['commission_RT']/2+slip)
        busy=x;rows.append(row)
    return pd.DataFrame(rows)


def setup(cfg):
    F.RUNTIME=ROOT/'agents/codex/runtime/mae_selected_20261108'
    g=F.grid(cfg,'NQ');a=F.market_arrays(g,'NQ',cfg)
    inconsistent=(a.h<a.l)|(a.h<np.maximum(a.o,a.c))|(a.l>np.minimum(a.o,a.c))
    a.bad |= inconsistent & ~a.closed
    a.prefix=np.r_[0,np.cumsum(a.bad,dtype=np.int64)]
    return g,a


def design(commit):
    cfg,p,head=verify(commit);OUT.mkdir(parents=True,exist_ok=True)
    days=pd.bdate_range(cfg['design_start'],cfg['design_end'])
    prior=max(cfg['prior_floor'],int(pd.read_csv(ROOT/'TRIALS.csv').variants.fillna(1).sum()))+cfg['additional_prior_reservations']+cfg['max_definitions']
    g,a=setup(cfg);summaries=[];metrics=[];dispositions=[]
    for spec in cfg['parents']:
        key=spec['key']; print('Design parent',key,flush=True)
        t=F.load_parent(spec,g,cfg);b=F.replay(t,spec,a,cfg,'BASE');c=child(t,spec,a,cfg,b)
        t.to_csv(OUT/f'{key}_parent.csv',index=False);b.to_csv(OUT/f'{key}_BASE.csv',index=False);c.to_csv(OUT/f'{key}_LIMIT025.csv',index=False)
        good=b.unknown.eq(0)&c.unknown.eq(0);bb=b[good];cc=c[good]
        bd=F.daily(bb,days);d=F.daily(cc,days);effect=d-bd
        dropped=bb[cc.missed.to_numpy().astype(bool)]
        row=dict(parent=key,source_tickets=len(t),resolved=int(good.sum()),unknown=int((~good).sum()),
            base_fills=int(bb.status.eq('filled').sum()),limit_fills=int(cc.status.eq('filled').sum()),missed=int(cc.missed.sum()),
            base_net=float(bb.net.sum()),limit_net=float(cc.net.sum()),increment=float(effect.sum()),
            base_gross=float(bb.gross.sum()),limit_gross=float(cc.gross.sum()),
            base_fees=float(bb.fee.sum()),limit_fees=float(cc.fee.sum()),base_slippage=float(bb.slippage.sum()),limit_slippage=float(cc.slippage.sum()),
            base_stress=float(bb.stress_net.sum()),limit_stress=float(cc.stress_net.sum()),stress_increment=float(cc.stress_net.sum()-bb.stress_net.sum()),
            paired_t=F.tstat(effect),dsr=float(M.deflated_sharpe(effect,prior)),t_bar=M.t_threshold(prior),prior_definitions=prior,
            positive_years=int((d.groupby(d.index.year).sum()>0).sum()),
            positive_increment_years=int((effect.groupby(effect.index.year).sum()>0).sum()),
            missed_base_mean=float(dropped.net.mean()) if len(dropped) else None,missed_base_t=F.tstat(dropped.net),
            fill_delay_median=float(cc.loc[cc.status.eq('filled'),'entry_delay'].median()) if cc.status.eq('filled').any() else None)
        row['design_pass']=bool(good.all() and len(bb)>=30 and row['limit_fills']>=30 and row['limit_net']>0 and row['limit_stress']>0
            and row['increment']>0 and row['stress_increment']>0 and row['paired_t']>=row['t_bar'] and row['dsr']>=.95
            and row['positive_years']>=4 and row['positive_increment_years']>=3)
        for profile,q in [('BASE',bb),('LIMIT025',cc),('LIMIT025_STRESS',cc.assign(net=cc.stress_net))]:
            for side,label in [(0,'whole'),(1,'long'),(-1,'short')]:
                for year in ['design',2018,2019,2020,2021,2022]:
                    z=q if not side else q[q.side==side];dd=days if year=='design' else days[days.year==year]
                    if year!='design':z=z[pd.to_datetime(z.exit_at).dt.year==year]
                    vv=F.daily(z,dd);fills=z[z.status.eq('filled')]
                    metrics.append(dict(parent=key,profile=profile,side=label,period=year,opportunities=len(z),missed=int(z.missed.sum()),
                                        trade_t=F.tstat(fills.net),**M.perf(vv,fills.net)))
            daily=F.daily(q,days);daily.to_csv(OUT/f'{key}_{profile}_conditional_daily.csv',header=['net'])
            assert np.isclose(daily.sum(),q.net.sum())
        for q in [bb,cc]:assert np.isclose(q.net.sum(),q.gross.sum()-q.fee.sum()-q.slippage.sum())
        dropped.to_csv(OUT/f'{key}_missed_base.csv',index=False)
        summaries.append(row);dispositions.append(dict(parent=key,status='earned_controls' if row['design_pass'] else 'stop_design',joint_unknown=row['unknown']))
        print(f"{key}: base={row['base_net']:.2f}, limit={row['limit_net']:.2f}, delta={row['increment']:.2f}, unknown={row['unknown']}, pass={row['design_pass']}",flush=True)
    pd.DataFrame(summaries).to_csv(OUT/'design_summary.csv',index=False);pd.DataFrame(metrics).to_csv(OUT/'metrics.csv',index=False)
    F.dump(OUT/'dispositions.json',dispositions)
    F.dump(OUT/'run.json',dict(preregistration_commit=commit,checked_head=head,program=cfg['program'],design_start=cfg['design_start'],design_end=cfg['design_end'],
        executed_economic_definitions=9,controls_run=False,new_2023plus_results=False,account_tests_run=False,
        raw_2017_2022_only=True,source_ledgers_contain_previously_seen_later_rows=True,dispositions=dispositions))


def controls(commit):
    cfg,p,head=verify(commit)
    selected=p.get('selected_for_controls',[]);assert selected,'Design selection must be committed before controls'
    summary=pd.read_csv(OUT/'design_summary.csv').set_index('parent')
    assert all(bool(summary.loc[k,'design_pass']) for k in selected)
    g,a=setup(cfg);days=pd.bdate_range(cfg['design_start'],cfg['design_end']);results=[]
    for spec in cfg['parents']:
        key=spec['key']
        if key not in selected:continue
        t=F.load_parent(spec,g,cfg);b=F.replay(t,spec,a,cfg,'BASE');c=child(t,spec,a,cfg,b)
        assert not b.unknown.any() and not c.unknown.any()
        rng=np.random.default_rng(cfg['seed']+sum(map(ord,key)))
        groups=pd.DataFrame(dict(year=pd.to_datetime(b.exit_at).dt.year,side=b.side)).groupby(['year','side']).indices
        actual=float(c.net.sum());actual_dd=M.perf(F.daily(c,days),c[c.status=='filled'].net)['max_dd']
        for i in range(cfg['controls_repetitions']):
            delayed=child(t,spec,a,cfg,b,delays=rng.integers(1,61,size=len(t)))
            if delayed.unknown.any():raise RuntimeError('Unknown random-time control; dependent inference stops, no imputation')
            dropped=b.copy()
            for indices in groups.values():
                n=int(c.iloc[indices].missed.sum())
                gone=rng.choice(indices,size=n,replace=False)
                dropped.loc[gone,['net','gross','fee','slippage']]=0.
            drop_dd=M.perf(F.daily(dropped,days))['max_dd']
            results.append(dict(parent=key,iteration=i,random_time_net=float(delayed.net.sum()),random_drop_net=float(dropped.net.sum()),random_drop_dd=drop_dd,
                                candidate_net=actual,candidate_dd=actual_dd))
    pd.DataFrame(results).to_csv(OUT/'controls.csv',index=False)
    F.dump(OUT/'controls_run.json',dict(checked_head=head,preregistration_commit=commit,selected=selected,repetitions=cfg['controls_repetitions'],new_definitions=2*len(selected)))


def selftest():
    n=20;o=np.full(n,100.);h=np.full(n,101.);l=np.full(n,100.);c=np.full(n,100.)
    a=SimpleNamespace(o=o,h=h,l=l,c=c,bad=np.zeros(n,bool),closed=np.zeros(n,bool),end=n,tick=.25,pv=2.)
    l[1]=99.75;assert first_limit(a,0,5,1,99.75)[0]==-1
    l[2]=99.5;hit=first_limit(a,0,5,1,99.75);assert hit[0]==2 and hit[1]==99.75 and hit[2]==0
    a.bad[1]=True;assert first_limit(a,0,5,1,99.75)[-1]=='unknown_wait';a.bad[1]=False
    assert first_limit(a,0,2,1,99.75)[0]==-1
    o[1]=99.;l[1]=98.75;h[1]=99.25;c[1]=99.;hit=first_limit(a,0,5,1,99.75)
    assert hit[0]==1 and hit[1]==99. and hit[1]+hit[2]/a.pv<=99.75
    o[1]=100.;h[:]=100.5;l[1]=99.5;c[1]=100.;h[3]=101.
    hit=first_limit(a,0,5,-1,100.75);assert hit[0]==3 and hit[1]==100.75
    a.start=pd.Timestamp('2020-01-02');a.prefix=np.zeros(n+1,dtype=int)
    t=pd.DataFrame([dict(ticket_id=0,entry_at=a.start,exit_at=a.start+pd.Timedelta(minutes=10),
        entry=100.,exit=100.5,side=1,kind='time',source_gross=1.,entry_cost_ticks=1,exit_cost_ticks=1)])
    spec=dict(key='FIXTURE',market='NQ');cfg=dict(offset=.0025,commission_RT=1.24,stress_commission_RT=2.48)
    o[1]=99.;h[1]=99.5;l[1]=98.75;c[1]=99.
    b=F.replay(t,spec,a,cfg,'BASE');q=child(t,spec,a,cfg,b)
    assert np.isclose(b.net.iloc[0],-1.24) and np.isclose(q.net.iloc[0],.76)
    t['exit_at']=a.start+pd.Timedelta(minutes=1);t['exit']=99.;t['source_gross']=-2.
    b=F.replay(t,spec,a,cfg,'BASE');q=child(t,spec,a,cfg,b)
    assert q.missed.iloc[0]==1 and q.net.iloc[0]==0
    a.bad[1]=True;a.prefix=np.r_[0,np.cumsum(a.bad)]
    b=F.replay(t,spec,a,cfg,'BASE');q=child(t,spec,a,cfg,b)
    assert b.unknown.iloc[0]==1 and q.unknown.iloc[0]==1 and np.isnan(q.net.iloc[0])
    print('Nine invented first-passage, touch, missing, expiry, gap-cost, short-limit, accounting, cancellation and UNKNOWN checks passed; no market data loaded.')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['selftest','design','controls']);ap.add_argument('--commit');args=ap.parse_args()
    if args.action=='selftest':selftest()
    elif args.action=='design':design(args.commit)
    else:controls(args.commit)
