"""Frozen price-based FC/ONB/T combination screen. No optimizer or live integration."""
import argparse
import ast
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import numpy as np
import pandas as pd
import metrics as M
import resampling as R
import codex_ingredients_three_20261108 as I
import codex_ingredients_fc_onb_t_20261108 as F

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_opening_handoff_20261108'
PLAN='agents/codex/plans/opening_handoff_20261108.md'
CODE='analysis/codex_opening_handoff_20261108.py'
DEP=ROOT/'agents/codex/inputs/opening_handoff_20261108/dependencies.json'
SEED=20261108
P=dict(ZMin=1.,ZLookback=60,MinWarmup=20,SL=100.,Trail=150.,BER=0.,ExitTime=1458,Early=1130)


def runner(delay=False):
    ns={'np':np,'pd':pd,'PV':20.,'TICK':.25,'COST':17.25,'V1':False,'RS':None,'REF':None,
        'FIXED':{},'P':P.copy(),'AUDIT':{}}
    F.bind('fc_replica.py',['early_close'],ns)
    text=(F.BASE/'fc_replica.py').read_text();tree=ast.parse(text)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run')
    src=ast.get_source_segment(text,fn)
    line=next(x for x in src.splitlines() if x.strip().startswith('ok = warm and'))
    src=src.replace(line,'            ok = int(D[i]) in FIXED and pos == 0\n            dr = FIXED.get(int(D[i]), dr)')
    if delay:
        src=src.replace('if pend[0] == "entry":','if pend[0] == "wait":\n                pend = ("entry", pend[1])\n            elif pend[0] == "entry":')
        src=src.replace('pend = ("entry", dr)','pend = ("wait", dr)')
    src=src.replace('return t, s','AUDIT.update(open_position=int(pos), pending=pend is not None)\n    return t, s')
    exec(compile(src,'<frozen FC v2 exit port, fixed price-derived admission>','exec'),ns)
    return ns


def synthetic_checks():
    # Synthetic prices only, never market observations or variant selection.
    def case(side=1,change=None,date=20200102,delay=False):
        x=pd.DataFrame({'date':date,'time':[900,901,902,1130,1131,1458,1459],
                        'open':1000.,'high':1000.,'low':1000.,'close':1000.,'volume':0.})
        if change:
            for (time,col),v in change.items():x.loc[x.time.eq(time),col]=v
        ns=runner(delay);ns['FIXED']={date:side};t,_=ns['run'](x)
        assert len(t)==1 and ns['AUDIT']['open_position']==0
        return t.iloc[0]
    t=case();assert t.kind=='eod' and t.t_in==901 and t.t_out==1459 and t.net==-17.25
    assert t.gross/10-2.25==-2.25
    t=case(change={(901,'low'):850.});assert t.kind=='backstop' and t.exit==900 and t.net==-2017.25
    t=case(-1,{(901,'high'):1150.});assert t.kind=='backstop' and t.exit==1100 and t.net==-2017.25
    t=case(change={(902,'open'):850.,(902,'low'):840.,(902,'high'):855.,(902,'close'):845.});assert t.exit==850 and t.gross==-3000
    t=case(change={(901,'high'):1200.,(901,'close'):1190.,(902,'open'):1100.,(902,'low'):1040.,(902,'high'):1110.,(902,'close'):1060.});assert t.t_out==902 and t.exit==1050
    t=case(change={(901,'high'):1200.,(901,'close'):1010.,(902,'open'):1005.});assert t.kind=='LX.mkt' and t.exit==1005
    t=case(change={(901,'high'):1070.,(901,'close'):1060.});assert t.kind=='eod' and t.exit==1000
    t=case(date=20200703);assert t.t_out==1131
    t=case(delay=True,change={(901,'low'):850.});assert t.t_in==902 and t.kind=='eod'
    return {'synthetic_groups':9,'passed':True,'scope':'invented stop/gap/trail/fallback/noBE/flatten/delay/cost fixtures'}


def features(g,start,end):
    ns={'np':np,'pd':pd};F.bind('candidates.py',['adx'],ns)
    b=g.bars(15);valid=np.isfinite(b['c']);adx=np.full(b['c'].shape,np.nan)
    adx[valid]=ns['adx'](b['h'][valid],b['l'][valid],b['c'][valid],14)
    cal_ns={};F.bind('fc_replica.py',['early_close'],cal_ns)
    O,H,L,C=(getattr(g,c).ravel() for c in ('o','h','l','c'))
    rows=[];excluded=[];seen=0
    for d in g.trading:
        date=pd.Timestamp(g.ts[d]);seen+=1
        if not pd.Timestamp(start)<=date<=pd.Timestamp(end):continue
        reason=None;flat=691 if cal_ns['early_close'](date) else 899
        if d==0 or seen<=20:reason='warmup'
        elif date.month in (3,6,9,12) and 5<=date.day<=21:reason='declared_quarterly_roll_calendar'
        elif not np.isfinite(g.c[d,509]):reason='missing_night_end'
        elif not all(np.isfinite(getattr(g,c)[d,511:541]).all() for c in ('o','h','l','c')):reason='incomplete_first30'
        elif not np.isfinite(adx[d,36]):reason='ADX_warmup_or_missing'
        elif not all(np.isfinite(getattr(g,c)[d,541:flat+1]).all() for c in ('o','h','l','c')):reason='unknown_execution_path'
        if reason:excluded.append({'date':date,'reason':reason});continue
        n0=(d-1)*1440+1021;n1=d*1440+509;r0=(d-1)*1440+1381;r1=d*1440+510
        night_bars=np.flatnonzero(np.isfinite(O[n0:n1+1])&np.isfinite(C[n0:n1+1]))
        if len(night_bars)<30:excluded.append({'date':date,'reason':'short_observed_night'});continue
        hi=np.nanmax(H[r0:r1+1]);lo=np.nanmin(L[r0:r1+1])
        if not np.isfinite(hi+lo) or hi<=lo:excluded.append({'date':date,'reason':'missing_overnight_range'});continue
        night_first=n0+int(night_bars[0]);move=g.c[d,509]-O[night_first];night=int(np.sign(move))
        drive=int(np.sign(g.c[d,540]-g.o[d,511]));loc=(g.o[d,511]-lo)/(hi-lo)
        bias=1 if loc>=2/3 else -1 if loc<=1/3 else 0
        if not drive:excluded.append({'date':date,'reason':'zero_opening_drive'});continue
        orhi=np.max(g.h[d,511:526]);orlo=np.min(g.l[d,511:526])
        breakout=g.c[d,540]>orhi if drive>0 else g.c[d,540]<orlo
        confirm=bool(adx[d,36]>30 and breakout)
        cont=drive if drive==night==bias and confirm else 0
        rev=drive if drive==-night and bias==night and night!=0 and confirm else 0
        rows.append({'date':date,'day':int(d),'night_move':move,'night_first_flat_index':night_first,'night_side':night,'overnight_high':hi,
                     'overnight_low':lo,'location':loc,'bias':bias,'drive':drive,'ADX':adx[d,36],
                     'or15_high':orhi,'or15_low':orlo,'breakout':bool(breakout),'Parent':drive,
                     'Continuation':cont,'Reversal':rev,'flat_bar':flat,
                     'event_time':'09:00 close-label CT','available_at':'09:00 close-label CT',
                     'decision_time':'09:00 close-label CT','entry_bar':'09:01 close-label OPEN',
                     'label_end':('11:31' if flat==691 else '14:59')+' close-label OPEN CT'})
    return pd.DataFrame(rows),pd.DataFrame(excluded,columns=['date','reason'])


def data_frame(g):
    frames=[]
    for date,x in I.dt_days(g).items():
        x=x.copy();x['date']=date;x['volume']=0. # Unused source flow code: never a substitute for up-tick volume.
        frames.append(x)
    return pd.concat(frames,ignore_index=True)


def replay(g,df,f,name,delay=False):
    ns=runner(delay);ns['FIXED']={int(r.date.strftime('%Y%m%d')):int(getattr(r,name)) for r in f.itertuples() if getattr(r,name)}
    raw,_=ns['run'](df)
    if ns['AUDIT']['open_position'] or ns['AUDIT']['pending']:raise RuntimeError('unclosed position/order')
    if raw.date.ne(raw.exit_date).any():raise RuntimeError('cross-date trade')
    raw['day']=[int(np.searchsorted(g.ts,np.datetime64(d))) for d in raw.date]
    raw['j0']=[F.minute(v) for v in raw.t_in];raw['j1']=[F.minute(v) for v in raw.t_out]
    raw['slippage']=10.
    for col in ['entry','exit','gross','net']:raw[col]=raw[col].astype(float)
    t=F.normalize(raw,g)
    if len(t)!=len(ns['FIXED']):raise RuntimeError('missing admitted execution')
    if t.missing_held_closes.sum():raise RuntimeError('unknown held minute')
    t['extra_tick_cost_net']=t.net-10.
    if not np.allclose(t.native_mnq_net,t.gross/10-2.25):raise RuntimeError('native cost bridge')
    return t


def metric(t,cal):
    m=I.metric(t,cal);m['positive_years']=int((t.groupby(t.date.dt.year).net.sum()>0).sum())
    m['extra_tick_cost_total']=t.extra_tick_cost_net.sum();return m


def control(t,base,cal):
    if not len(t):return {'pure_nested_filter':True,'removed_n':len(base),'removed_total':base.net.sum(),
                            'removed_t':I.tst(base.net),'random_profit_ge_actual':1.,'random_dd_le_actual':1.}
    return I.filter_control(t,base,cal)


def main(phase):
    for p in (PLAN,CODE):
        if subprocess.check_output(['git','show','HEAD:'+p],cwd=ROOT)!=(ROOT/p).read_bytes():raise RuntimeError('commit exact definition first')
    deps=json.loads(DEP.read_text())
    for p,sha in deps.items():
        if I.digest(ROOT/p)!=sha:raise RuntimeError('dependency changed: '+p)
    dest=OUT/phase;dest.mkdir(parents=True,exist_ok=True)
    I.dump(dest/'synthetic_checks.json',synthetic_checks())
    prior=None
    if phase=='recent':
        prior=json.loads((OUT/'design/results.json').read_text())
        if not prior['selected'] or prior['code_sha256']!=I.digest(ROOT/CODE):raise RuntimeError('no frozen design pass')
    start,end=('2018-01-01','2022-12-30') if phase=='design' else ('2023-01-01','2026-10-09')
    g,_,inputs=I.grids(end);f,ex=features(g,start,end);cal=pd.DatetimeIndex(f.date)
    f.to_csv(dest/'features_before_returns.csv',index=False);ex.to_csv(dest/'exclusions.csv',index=False)
    counts={x:int(f[x].ne(0).sum()) for x in ('Parent','Continuation','Reversal')}
    I.dump(dest/'no_return_receipt.json',{'sessions':len(f),'counts':counts,'exclusion_counts':ex.reason.value_counts().to_dict(),
        'power_assumed_SD_per_NQ':2000,'t2_required_net_mean':{k:4000/np.sqrt(v) if v else None for k,v in counts.items()},
        'known_clock':'all feature prices/ADX mature by09:00; no fitted ML or up-tick proxy'})
    df=data_frame(g);names=['Continuation','Reversal'] if phase=='design' else [prior['selected']]
    cases={'Parent':replay(g,df,f,'Parent')}
    for n in names:cases[n]=replay(g,df,f,n);cases[n+'_delay1m']=replay(g,df,f,n,True)
    metrics=[];bycase={}
    for name,t in cases.items():
        t.to_csv(dest/(name+'_trades.csv'),index=False)
        dd=pd.DataFrame({c:I.daily(t,cal,c) for c in ['gross','commission','slippage','net','native_mnq_net']});dd.to_csv(dest/(name+'_daily.csv'))
        bycase[name]=metric(t,cal)
        for side in ['all','long','short']:
            a=t if side=='all' else t[t.side.eq(1 if side=='long' else -1)]
            metrics.append({'case':name,'period':phase,'side':side,**metric(a,cal)})
        for y in sorted(cal.year.unique()):
            metrics.append({'case':name,'period':str(y),'side':'all',**metric(t[t.date.dt.year==y],cal[cal.year==y])})
    gates={};controls={};effects={};base=bycase['Parent']
    for name in names:
        t=cases[name];m=bycase[name];ctl=control(t,cases['Parent'],cal);controls[name]=ctl
        delta=I.daily(t,cal)-I.daily(cases['Parent'],cal)
        z=R.bootstrap(delta,n=1000,block=20,seed=SEED,chunk=250).loc['annual']
        effects[name]={'total':delta.sum(),'annual_p5':z.p5,'annual_p50':z.p50,'annual_p95':z.p95}
        q={'trades_min':len(t)>=(30 if phase=='design' else 20),'gross_net_positive':m['gross']>0 and m['total']>0,
           't_ge2':m['t_trade']>=2,'PF_ge1_2':m['profit_factor']>=1.2,
           'positive_years':m['positive_years']>=(3 if phase=='design' else 2),
           'net_beats_parent':m['total']>base['total'],'DD_not_worse_parent':m['max_dd']<=base['max_dd'],
           'Sharpe_not_worse_parent':m['sharpe']>=base['sharpe'],'pure_nested_filter':ctl['pure_nested_filter'],
           'removed_negative_t':ctl.get('removed_total',np.nan)<0 and ctl.get('removed_t',np.nan)<=-1,
           'random_profit':ctl.get('random_profit_ge_actual',1)<=.05,'random_DD':ctl.get('random_dd_le_actual',1)<=.05,
           'paired_annual_p5':z.p5>0,'delay_positive':bycase[name+'_delay1m']['total']>0,
           'extra_tick_cost_positive':m['extra_tick_cost_total']>0}
        gates[name]={'passed':bool(all(q.values())),'checks':q}
    passed=[n for n in names if gates[n]['passed']]
    selected=max(passed,key=lambda n:(bycase[n]['calmar'],bycase[n]['total'],n=='Continuation')) if passed else None
    pd.DataFrame(metrics).to_csv(dest/'metrics.csv',index=False)
    import importlib.metadata as md
    result={'phase':phase,'selected':selected,'gates':gates,'results':bycase,'filter_controls':controls,
            'paired_effects':effects,'case_count':len(cases),'distinct_family_definitions':5,'inputs':inputs,
            'source_ref':I.DATA_REF,'dependencies':deps,'code_sha256':I.digest(ROOT/CODE),'plan_sha256':I.digest(ROOT/PLAN),
            'plan_commit':subprocess.check_output(['git','log','-1','--format=%H','--',PLAN],cwd=ROOT,text=True).strip(),
            'packages':{p:md.version(p) for p in ['numpy','pandas','numba','openpyxl','scipy','scikit-learn']},
            'recent_return_tests_run':phase=='recent','portfolio_tests_run':False,
            'limits':['price-only interaction; missing native up-tick Volume omitted','no fitted ML','prior ingredients and recent history seen','no promotion or book change']}
    I.dump(dest/'results.json',result)
    print(pd.DataFrame(bycase).T[['trades','total','avg','t_trade','profit_factor','sharpe','max_dd','native_mnq_total']].round(2).to_string(),flush=True)
    print(json.dumps({'selected':selected,'gates':gates,'controls':controls,'effects':effects},indent=2,default=float),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['design','recent'],required=True)
    main(parser.parse_args().phase)
