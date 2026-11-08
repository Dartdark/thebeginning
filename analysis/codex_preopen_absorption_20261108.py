"""Frozen native overnight signed-flow screen. Audit before returns, no optimizer/live access."""
import argparse
import gzip
import hashlib
import importlib.metadata as md
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import numpy as np
import pandas as pd
import codex_ingredients_three_20261108 as I
import codex_ingredients_fc_onb_t_20261108 as F
import resampling as R

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'agents/codex/inputs/bridge_native_2018_22_20261108'
OUT=ROOT/'analysis/outputs/codex_preopen_absorption_20261108'
PLAN='agents/codex/plans/preopen_absorption_20261108.md'
CODE='analysis/codex_preopen_absorption_20261108.py'
DEP=ROOT/'agents/codex/inputs/preopen_absorption_20261108/dependencies.json'
SEED=20261108
WALK=F.bind('grid.py',['_walk'],{'np':np})['_walk']
COLUMNS=['date','day','j0','j1','side','entry','exit','kind','gross','slippage','stop','adr20']


def load_native():
    manifest=json.loads((DATA/'transfer_manifest.json').read_text());frames=[];audit={}
    for name,info in manifest['files'].items():
        p=DATA/name;compressed=p.read_bytes();raw=gzip.decompress(compressed)
        assert len(compressed)==info['compressed_bytes'] and I.digest(p)==info['compressed_sha256']
        assert len(raw)==info['original_bytes'] and hashlib.sha256(raw).hexdigest()==info['original_sha256']
        import io
        x=pd.read_csv(io.BytesIO(raw));assert x.columns.tolist()==manifest['fields']
        t=pd.to_datetime(x.Date+' '+x.Time,format='%m/%d/%Y %H:%M')
        x['stamp']=t.dt.tz_localize('America/New_York',ambiguous='raise',nonexistent='raise').dt.tz_convert('America/Chicago').dt.tz_localize(None)
        vals=x[['Open','High','Low','Close','Volume','UpVol','DownVol']].to_numpy(float)
        assert np.isfinite(vals).all() and (vals[:,4:]>=0).all()
        assert np.array_equal(vals[:,4],vals[:,5]+vals[:,6])
        assert np.allclose(vals[:,4:],np.round(vals[:,4:]))
        assert ((x.Low<=x.Open)&(x.Low<=x.Close)&(x.High>=x.Open)&(x.High>=x.Close)&(x.Low<=x.High)).all()
        assert np.allclose(vals[:,:4]*4,np.round(vals[:,:4]*4))
        audit[name]={'rows':len(x),'original_sha256':info['original_sha256'],'compressed_sha256':info['compressed_sha256']}
        frames.append(x.drop(columns=['Date','Time']))
    x=pd.concat(frames,ignore_index=True).sort_values('stamp');assert not x.stamp.duplicated().any()
    dates=pd.date_range(x.stamp.min().normalize(),x.stamp.max().normalize(),freq='D');D=len(dates)
    g=SimpleNamespace(ts=dates.to_numpy(),dates=np.array(dates.strftime('%Y%m%d'),dtype=int),D=D)
    day=dates.get_indexer(x.stamp.dt.normalize());j=x.stamp.dt.hour.to_numpy()*60+x.stamp.dt.minute.to_numpy()
    for col,key in [('Open','o'),('High','h'),('Low','l'),('Close','c'),('Volume','v'),('UpVol','buy'),('DownVol','sell')]:
        a=np.full((D,1440),np.nan);a[day,j]=x[col].to_numpy(float);setattr(g,key,a)
    # Preserve the same owned source trading-date calendar, without importing a single price.
    calendars=[];calendar_inputs={}
    for y in range(2018,2023):
        name='NQ_1min_%d.csv'%y;p=I.SOURCE/'data'/name;raw=p.read_bytes()
        want=subprocess.check_output(['git','-C',str(I.SOURCE),'rev-parse',I.DATA_REF+':data/'+name],text=True).strip()
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert blob==want
        z=pd.read_csv(p,usecols=['date']);calendars.extend(z.date.unique())
        calendar_inputs[name]={'blob':blob,'sha256':hashlib.sha256(raw).hexdigest(),'role':'dates only; never price repair'}
    cal=pd.DatetimeIndex(pd.to_datetime(pd.Series(sorted(set(calendars))).astype(str)))
    cal=cal[(cal>='2018-01-01')&(cal<='2022-12-30')&(cal.dayofweek<5)]
    g.trading=np.searchsorted(g.ts,cal.to_numpy());assert (g.ts[g.trading]==cal.to_numpy()).all()
    audit['calendar_inputs']=calendar_inputs;audit['native_rows']=len(x);audit['calendar_sessions']=len(cal)
    audit['transport_status']='byte-exact; continuous-series provenance remains conditional'
    return g,cal,audit


def make_features(g,cal):
    rth_history=[];night_history=[];pressure_history=[];rows=[];ex=[]
    O,H,L,C,V,B,S=(getattr(g,k).ravel() for k in ('o','h','l','c','v','buy','sell'))
    for d in range(g.D):
        date=pd.Timestamp(g.ts[d]);is_weekday=date.dayofweek<5
        complete_rth=all(np.isfinite(getattr(g,k)[d,511:901]).all() for k in ('o','h','l','c'))
        adr=float(np.mean(rth_history[-20:])) if len(rth_history)>=20 else np.nan
        reason=None;decision_valid=False
        if is_weekday:
            a=(d-1)*1440+1021;b=d*1440+508;last=d*1440+508;lo=d*1440+494
            if d==0:reason='no_previous_calendar_date'
            else:
                obs=np.flatnonzero(np.isfinite(C[a:b+1]))
                if len(obs)<836 or not np.isfinite(C[last]):reason='night_coverage_or_decision_close'
                elif not all(np.isfinite(z[lo:last+1]).all() for z in (O,H,L,C,V,B,S)):reason='unknown_last15'
                elif V[lo:last+1].sum()<=0:reason='no_last15_volume'
                else:decision_valid=True
            if decision_valid:
                # All source-priced overnight rows carry verified quantities; absent bars stay absent.
                night= a+obs;night_total=float(V[night].sum());first=int(night[0])
                nightmove=float(C[last]-O[first]);n=int(np.sign(nightmove))
                delta=float((B[lo:last+1]-S[lo:last+1]).sum()/V[lo:last+1].sum())
                pmed=float(np.median(pressure_history[-60:])) if len(pressure_history)>=20 else np.nan
                vmed=float(np.median(night_history[-20:])) if len(night_history)>=20 else np.nan
                stalled=bool(n*(C[last]-O[lo])<=0);fade=-n
                feature={'date':date,'day':d,'night_bars':len(obs),'night_first_index':first,'night_total':night_total,
                         'night_move':nightmove,'night_side':n,'delta15':delta,'pressure_median':pmed,
                         'night_median':vmed,'adr20':adr,'stalled':stalled,
                         'event_time':str(date+pd.Timedelta(hours=8,minutes=28))+' CT',
                         'decision_time':str(date+pd.Timedelta(hours=8,minutes=28))+' CT',
                         'assumed_available_at':str(date+pd.Timedelta(hours=8,minutes=29))+' CT',
                         'entry_time':str(date+pd.Timedelta(hours=8,minutes=29))+' CT',
                         'label_end':str(date+pd.Timedelta(hours=8,minutes=44))+' CT'}
                # Assess before updating today's histories; roll-calendar skips still enter past histories.
                if not np.isfinite(adr) or not np.isfinite(pmed) or not np.isfinite(vmed):reason='prior20_history_warmup'
                elif n==0:reason='zero_night_direction'
                elif date.month in (3,6,9,12) and 5<=date.day<=21:reason='declared_roll_calendar'
                elif not all(np.isfinite(getattr(g,k)[d,510:526]).all() for k in ('o','h','l','c')):reason='unknown_execution_path'
                if reason is None:
                    feature.update(PlainFade=fade,PriceOnly=fade if stalled else 0,
                                   HeavyTotal=fade if night_total>1.4*vmed else 0,
                                   Absorption=fade if stalled and n*delta>0 and abs(delta)>=pmed else 0)
                    rows.append(feature)
                pressure_history.append(abs(delta));night_history.append(night_total)
            if date in cal and reason:ex.append({'date':date,'reason':reason})
        if complete_rth and is_weekday:rth_history.append(float(np.max(g.h[d,511:901])-np.min(g.l[d,511:901])))
    f=pd.DataFrame(rows);f=f[f.date.isin(cal)].copy()
    ex=pd.DataFrame(ex,columns=['date','reason'])
    assert not f.date.duplicated().any() and not ex.date.duplicated().any()
    assert set(f.date)|set(ex.date)==set(cal)
    return f,ex


def execute(g,day,side,adr,j0=510):
    if side not in [-1,1] or adr<=0 or not np.isfinite(adr):raise ValueError('invalid side/range')
    if not all(np.isfinite(getattr(g,k)[day,j0:526]).all() for k in ('o','h','l','c')):raise ValueError('unknown held path')
    entry=float(g.o[day,j0]);raw_stop=entry-side*.4*adr
    stop=(np.floor(raw_stop/.25+1e-10) if side>0 else np.ceil(raw_stop/.25-1e-10))*.25
    target=np.inf if side>0 else -np.inf
    j1,exit,kind,worst=WALK(g.o[day],g.h[day],g.l[day],g.c[day],j0,524,side,stop,target,1.)
    if kind==2:j1=525;exit=float(g.o[day,525])
    return {'day':int(day),'j0':j0,'j1':int(j1),'side':side,'entry':entry,'exit':float(exit),'kind':int(kind),
            'gross':(exit-entry)*side*20,'slippage':10.,'stop':stop,'adr20':adr}


def synthetic_checks():
    def grid():return SimpleNamespace(**{k:np.full((1,1440),1000.) for k in ('o','h','l','c')})
    g=grid();a=execute(g,0,1,10);assert a['kind']==2 and a['j1']==525 and a['gross']==0
    g.l[0,510]=995.;a=execute(g,0,1,10);assert a['kind']==0 and a['exit']==996 and a['j1']==510
    g=grid();g.h[0,510]=1005.;a=execute(g,0,-1,10);assert a['exit']==1004 and a['kind']==0
    g=grid();g.o[0,511]=990.;g.l[0,511]=989.;a=execute(g,0,1,10);assert a['exit']==990
    g=grid();g.o[0,525]=1001.;g.l[0,525]=900.;a=execute(g,0,1,10);assert a['kind']==2 and a['exit']==1001
    g=grid();g.o[0,511]=1002.;a=execute(g,0,1,10,511);assert a['entry']==1002 and a['stop']==998
    assert execute(g,0,1,10.1)['stop']==995.75 and execute(g,0,-1,10.1)['stop']==1004.25
    g=grid();g.c[0,517]=np.nan
    try:execute(g,0,1,10)
    except ValueError:pass
    else:raise AssertionError('unknown path accepted')
    assert (0-7.25-10)==-17.25 and (0/10-1.25-1)==-2.25
    t=pd.Timestamp('2018-01-02 09:28',tz='America/New_York').tz_convert('America/Chicago')
    assert t.hour==8 and t.minute==28
    return {'groups_passed':10,'scope':'invented clock/stop/rounding/gap/exit/delay/missing/cost fixtures only'}


def trades(g,f,name,delay=False):
    rows=[]
    for r in f.itertuples():
        side=int(getattr(r,name))
        if side:rows.append({'date':r.date,**execute(g,int(r.day),side,r.adr20,511 if delay else 510)})
    t=pd.DataFrame(rows,columns=COLUMNS)
    for c in ['entry','exit','gross','slippage']:t[c]=t[c].astype(float)
    t['date']=pd.to_datetime(t.date);t=F.normalize(t,g)
    t['extra_tick_cost_net']=t.net-10
    assert t.missing_held_closes.sum()==0
    return t


def metric(t,cal):
    m=I.metric(t,cal);m['positive_years']=int((t.groupby(t.date.dt.year).net.sum()>0).sum())
    m['extra_tick_cost_total']=t.extra_tick_cost_net.sum();return m


def main(phase):
    for p in (PLAN,CODE):
        if subprocess.check_output(['git','show','HEAD:'+p],cwd=ROOT)!=(ROOT/p).read_bytes():raise RuntimeError('commit first')
    deps=json.loads(DEP.read_text())
    for p,sha in deps.items():
        if I.digest(ROOT/p)!=sha:raise RuntimeError('changed dependency: '+p)
    OUT.mkdir(parents=True,exist_ok=True);dest=OUT/phase;dest.mkdir(exist_ok=True)
    I.dump(dest/'synthetic_checks.json',synthetic_checks())
    g,cal,audit=load_native();f,ex=make_features(g,cal)
    f.to_csv(dest/'features_before_returns.csv',index=False);ex.to_csv(dest/'exclusions.csv',index=False)
    counts={n:int(f[n].ne(0).sum()) for n in ['PlainFade','PriceOnly','HeavyTotal','Absorption']}
    receipt={'phase':phase,'input_audit':audit,'eligible_sessions':len(f),'counts':counts,
             'exclusions':ex.reason.value_counts().to_dict(),'code_sha256':I.digest(ROOT/CODE),'plan_sha256':I.digest(ROOT/PLAN),
             'power_assumed_SD_NQ':1000,'t2_net_mean_hurdle':{k:2000/np.sqrt(v) if v else None for k,v in counts.items()},
             'packages':{p:md.version(p) for p in ['numpy','pandas','numba','openpyxl','scipy','scikit-learn']},
             'returns_computed':False,'source_ref':'f8cd198','calendar_ref':I.DATA_REF,'dependencies':deps}
    I.dump(dest/'no_return_receipt.json',receipt)
    if phase=='audit':print(json.dumps({'counts':counts,'eligible':len(f),'excluded':receipt['exclusions'],'hashes_verified':True},indent=2));return
    prior=json.loads((OUT/'audit/no_return_receipt.json').read_text())
    if prior['code_sha256']!=I.digest(ROOT/CODE) or prior['plan_sha256']!=I.digest(ROOT/PLAN):raise RuntimeError('frozen audit absent/changed')
    if counts!=prior['counts'] or audit!=prior['input_audit']:raise RuntimeError('audit identity mismatch')
    cases={n:trades(g,f,n) for n in counts};cases['Absorption_delay1m']=trades(g,f,'Absorption',True)
    metrics=[];stats={}
    for name,t in cases.items():
        t.to_csv(dest/(name+'_trades.csv'),index=False)
        pd.DataFrame({c:I.daily(t,cal,c) for c in ['gross','commission','slippage','net','native_mnq_net']}).to_csv(dest/(name+'_daily.csv'))
        stats[name]=metric(t,cal)
        for side in ['all','long','short']:
            a=t if side=='all' else t[t.side.eq(1 if side=='long' else -1)]
            metrics.append({'case':name,'period':'design','side':side,**metric(a,cal)})
        for y in sorted(cal.year.unique()):metrics.append({'case':name,'period':str(y),'side':'all',**metric(t[t.date.dt.year==y],cal[cal.year==y])})
    m=stats['Absorption'];gates={'trades_ge30':m['trades']>=30,'gross_net_positive':m['gross']>0 and m['total']>0,
                               't_ge2':m['t_trade']>=2,'PF_ge1_2':m['profit_factor']>=1.2,'positive_years_ge3':m['positive_years']>=3,
                               'delay_positive':stats['Absorption_delay1m']['total']>0,'extra_tick_cost_positive':m['extra_tick_cost_total']>0}
    controls={};effects={}
    for parent in ['PlainFade','PriceOnly']:
        base=stats[parent];t=cases['Absorption'];b=cases[parent]
        ctl=I.filter_control(t,b,cal) if len(t) else {'pure_nested_filter':True,'removed_total':b.net.sum(),'removed_t':I.tst(b.net)}
        controls[parent]=ctl
        delta=I.daily(t,cal)-I.daily(b,cal)
        z=R.bootstrap(delta,n=1000,block=20,seed=SEED,chunk=250).loc['annual']
        effects[parent]={'total':delta.sum(),'annual_p5':z.p5,'annual_p50':z.p50,'annual_p95':z.p95}
        gates.update({parent+'_net_beaten':m['total']>base['total'],parent+'_DD_not_worse':m['max_dd']<=base['max_dd'],
                      parent+'_Sharpe_not_worse':m['sharpe']>=base['sharpe'],parent+'_pure_filter':ctl['pure_nested_filter'],
                      parent+'_removed_negative':ctl.get('removed_total',np.nan)<0 and ctl.get('removed_t',np.nan)<=-1,
                      parent+'_random_profit':ctl.get('random_profit_ge_actual',1)<=.05,parent+'_random_DD':ctl.get('random_dd_le_actual',1)<=.05,
                      parent+'_paired_p5':z.p5>0})
    selected='Absorption' if all(gates.values()) else None
    result={'selected':selected,'checks':gates,'stats':stats,'filter_controls':controls,'paired_effects':effects,
            'cases_run':5,'phase':'2018-22 design','recent_returns_run':False,'portfolio_tests_run':False,
            'code_sha256':I.digest(ROOT/CODE),'plan_sha256':I.digest(ROOT/PLAN),
            'plan_commit':subprocess.check_output(['git','log','-1','--format=%H','--',PLAN],cwd=ROOT,text=True).strip(),
            'prior_selection':'earlier T/flow tests plus18ingredient cases and failed5-case price-only handoff; not fresh discovery'}
    pd.DataFrame(metrics).to_csv(dest/'metrics.csv',index=False);I.dump(dest/'results.json',result)
    print(pd.DataFrame(stats).T[['trades','total','avg','t_trade','profit_factor','sharpe','max_dd','native_mnq_total']].round(3).to_string(),flush=True)
    print(json.dumps({'selected':selected,'checks':gates,'controls':controls,'effects':effects},indent=2,default=float),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['audit','design'],required=True);main(p.parse_args().phase)
