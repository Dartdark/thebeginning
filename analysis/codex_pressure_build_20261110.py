"""Frozen price-impact/repair batch; explicit committed preregistration before returns."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import warnings
import numpy as np
import pandas as pd
import codex_pressure_build_20261110_inputs as I
import codex_pressure_build_20261110_replay as E
import codex_cash_open_repair as C

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'analysis/outputs/codex_pressure_build_20261110'
PLAN = 'agents/codex/plans/pressure_build_20261110.md'
EVIDENCE = 'agents/codex/evidence/pressure_build_20261110.md'
CODE = ['analysis/codex_pressure_build_20261110.py','analysis/codex_pressure_build_20261110_inputs.py',
        'analysis/codex_pressure_build_20261110_replay.py']
MODELS = ['RESID2','PRICE2','NO_CONFIRM']


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, obj):
    C.write(path,json.dumps(obj,indent=2,default=str,allow_nan=True)+'\n')


def model_signals(minutes, grid):
    b=I.complete5min_ohlcv(minutes).copy()
    b['date']=b.index.normalize(); b['j']=b.index.hour*60+b.index.minute
    b['q']=(b.buy-b.sell)/b.volume.replace(0,np.nan)
    q=b.q
    for lag in [1,2]: b[f'q{lag}']=q.reindex(b.index-pd.Timedelta(minutes=lag*5)).to_numpy()
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',RuntimeWarning); atr=grid.daily_atr(15)
    a=pd.Series(atr,index=pd.to_datetime(grid.ts)); b['atr']=b.date.map(a)
    b['raw_y']=(b.close-b.open)/b.atr
    # Eligibility is based on declared date/calendar and closed-bar completeness only.
    calendar=pd.DatetimeIndex([d for d in pd.to_datetime(grid.ts) if C.normal_cash(d)])
    b=b[(b.j>=525)&(b.j<=845)].copy()
    train=b[(b.j<=840)&(b[['q','q1','q2','raw_y','atr']].notna().all(axis=1))&(b.atr>0)]
    rollfree=set(d for d in calendar if not C.roll_guard(d))
    train=train.copy(); train['rollfree']=train.date.isin(rollfree)
    signals={name:[] for name in MODELS}; fits=[]
    columns=['date','day','signal_j','event_j','side','stop_price','max_stop','target_R','exit_j','z','price_z','fit_last_date']
    daymap={pd.Timestamp(d):i for i,d in enumerate(grid.ts)}
    for k,date in enumerate(calendar):
        if k%100==0: print('feature fit',date.date(),'days done',k,flush=True)
        if k<20 or C.roll_guard(date): continue
        prior=calendar[k-20:k]
        hist=train[train.date.isin(prior)&train.rollfree]
        if len(hist)<600 or hist.date.nunique()<15: continue
        season=hist.groupby('j').raw_y.agg(lambda x: np.median(np.abs(x)))
        counts=hist.groupby('j').date.nunique(); season=season[counts>=15]
        center=season.median()
        if not np.isfinite(center) or center<=1e-12: continue
        season=season/center
        h=hist.copy(); h['f']=h.j.map(season); h['y']=h.raw_y/h.f
        h=h[np.isfinite(h.y)&(h.f>1e-12)]
        if len(h)<600 or h.date.nunique()<15: continue
        X=np.column_stack([np.ones(len(h)),h[['q','q1','q2']].to_numpy()]); y=h.y.to_numpy()
        beta,_,rank,_=np.linalg.lstsq(X,y,rcond=None)
        residual=y-X@beta; rms=np.sqrt(np.mean(residual**2)); sd=np.std(y); mean=np.mean(y)
        fit=dict(date=str(date.date()),training_rows=len(h),training_dates=h.date.nunique(),
                 fit_first=str(h.date.min().date()),fit_last=str(h.date.max().date()),beta=beta.tolist(),rms=rms,
                 rank=int(rank),b0_positive=bool(beta[1]>0),normalization_slots=len(season))
        fits.append(fit)
        if rank<4 or beta[1]<=0 or rms<=1e-9 or sd<=1e-9: continue
        assert h.date.max()<date
        today=b[(b.date==date)&(b.j>=540)&(b.j<=840)]
        for stamp,row in today.iterrows():
            f=season.get(row.j,np.nan)
            vals=np.array([row.raw_y,f,row.q,row.q1,row.q2,row.atr],float)
            if not np.isfinite(vals).all() or f<=1e-12: continue
            conf_time=stamp+pd.Timedelta(minutes=5)
            if conf_time not in b.index: continue
            conf=b.loc[conf_time]
            if conf.date!=date: continue
            y0=row.raw_y/f
            z=(y0-np.array([1.,row.q,row.q1,row.q2])@beta)/rms
            zp=(y0-mean)/sd
            for name in MODELS:
                score=zp if name=='PRICE2' else z
                if abs(score)<2: continue
                side=-int(np.sign(score))
                confirmed=side*(conf.close-conf.open)>0 and side*(conf.close-row.close)>0
                if name!='NO_CONFIRM' and not confirmed: continue
                j=int(conf.j)
                stop=min(row.low,conf.low)-.25 if side>0 else max(row.high,conf.high)+.25
                signals[name].append(dict(date=date,day=daymap[date],signal_j=j,event_j=int(row.j),side=side,
                    stop_price=float(stop),max_stop=.15*row.atr,target_R=.3,exit_j=min(j+31,895),
                    z=float(z),price_z=float(zp),fit_last_date=fit['fit_last']))
    return {k:pd.DataFrame(v,columns=columns) for k,v in signals.items()},pd.DataFrame(fits),calendar


def self_check():
    rng=np.random.default_rng(1); X=np.column_stack([np.ones(1000),rng.normal(size=(1000,3))]); beta=np.array([.1,2,-.3,-.2])
    y=X@beta; got=np.linalg.lstsq(X,y,rcond=None)[0]
    np.testing.assert_allclose(got,beta,atol=1e-12)
    return dict(ols_exact=True,input=I.self_check(),replay=E.synthetic_checks())


def design(prereg):
    paths=[PLAN,EVIDENCE]+CODE
    for path in paths:
        frozen=subprocess.check_output(['git','show',f'{prereg}:{path}'],cwd=ROOT)
        if frozen!=(ROOT/path).read_bytes(): raise ValueError(f'Uncommitted/unfrozen protocol: {path}')
    dest=OUT/'batch1_design_qa2'
    if (dest/'results.json').exists(): raise ValueError('Design results already exist; do not overwrite')
    dest.mkdir(parents=True,exist_ok=True)
    dump(dest/'binding.json',dict(prereg=prereg,code={p:digest(ROOT/p) for p in paths},models=MODELS,
        dependencies={p:digest(ROOT/p) for p in ['analysis/grid.py','analysis/grid24.py','analysis/metrics.py','analysis/codex_cash_open_repair.py','analysis/codex_s03_calendar.py','agents/codex/inputs/bridge_native_2018_22_20261108/transfer_manifest.json']},
        prior_families='all raw/AR fades, absorption, participation and jump searches retained; not fresh selection',
        validation_outcomes_read=False,new_economic_definitions=3))
    minute=I.load_design_native(); grid=I.make_grid(minute)
    signals,fits,calendar=model_signals(minute,grid)
    fits.to_csv(dest/'fits.csv.gz',index=False)
    stats={}; ledgers={}; allmetrics=[]
    for name in MODELS:
        signals[name].to_csv(dest/f'{name}_signals.csv.gz',index=False)
        trades,execution=E.replay(signals[name],grid=grid)
        trades.to_csv(dest/f'{name}_trades.csv.gz',index=False); ledgers[name]=trades
        known=not bool(execution['unknown_held_path_trades'])
        table=E.metrics_table(trades,calendar,allow_unknown=not known)
        table['model']=name; allmetrics.append(table)
        s=E.metrics_summary(trades,calendar,allow_unknown=not known)
        micro=E.metrics_summary(trades,calendar,'net_mnq',allow_unknown=not known)
        stress=E.metrics_summary(trades,calendar,'stress_four_ticks',allow_unknown=not known)
        ambiguity=E.metrics_summary(trades,calendar,'stop_first_net',allow_unknown=not known)
        daily=trades.groupby('date').net.sum().reindex(calendar,fill_value=0)
        daily.to_csv(dest/f'{name}_daily.csv',header=['net'])
        stats[name]=dict(summary=s,micro=micro,stress=stress,stop_first=ambiguity,execution=execution,
                         positive_years=int((daily.groupby(daily.index.year).sum()>0).sum()),
                         long_trades=int((trades.side==1).sum()),short_trades=int((trades.side==-1).sum()))
    p=stats['RESID2']; s=p['summary']
    gates=dict(trades=s['trades']>=150,long_count=p['long_trades']>=25,short_count=p['short_trades']>=25,
        net=s['total']>0,trade_t=s['t_trade']>=2,daily_nw5=s['t_nw5']>=1.5,pf=s['profit_factor']>=1.20,
        years=p['positive_years']>=4,micro_net=p['micro']['total']>0,stress_net=p['stress']['total']>0,
        stop_first_net=p['stop_first']['total']>0,
        held_paths=p['execution']['unknown_held_path_trades']==0)
    # A basic pass earns dependent controls/placebos, not immediate validation.
    result=dict(stats=stats,basic_gates=gates,basic_pass=all(gates.values()),selected=None,
                design_gate_complete=False,validation_allowed=False,new_return_definitions=3,prereg=prereg)
    pd.concat(allmetrics,ignore_index=True).to_csv(dest/'metrics.csv',index=False)
    dump(dest/'results.json',result)
    print(pd.DataFrame({k:v['summary'] for k,v in stats.items()}).T.to_string(),flush=True)
    print(json.dumps({'basic_gates':gates,'basic_pass':result['basic_pass']},indent=2),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--phase',choices=['self-check','design'],required=True)
    parser.add_argument('--prereg'); args=parser.parse_args()
    if args.phase=='self-check': print(json.dumps(self_check(),indent=2))
    elif not args.prereg: parser.error('--prereg required before design returns')
    else: design(args.prereg)
