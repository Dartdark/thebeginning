"""Frozen historical ingredient diagnostics; no fit, search, account or live action."""
import argparse
import ast
import copy
import json
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd
import codex_ingredients_three_20261108 as I
import metrics as M
import resampling as R

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'agents/codex/inputs/ingredients_fc_onb_t_20261108'
OUT=ROOT/'analysis/outputs/codex_ingredients_fc_onb_t_20261108'
PLAN='agents/codex/plans/ingredients_fc_onb_t_20261108.md'
CODE='analysis/codex_ingredients_fc_onb_t_20261108.py'
SEED=20261108


def bind(file,names,ns):
    tree=ast.parse((BASE/file).read_text())
    nodes=[copy.deepcopy(n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes}==set(names)
    for n in nodes:n.decorator_list=[]
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(BASE/file),'exec'),ns)
    return ns


def hm(j):return int(j)//60*100+int(j)%60
def minute(h):return int(h)//100*60+int(h)%100


def normalize(t,g):
    t=t.copy().reset_index(drop=True)
    t['date']=pd.to_datetime(t.date)
    t=t[t.date>='2018-01-01'].reset_index(drop=True)
    t['commission']=7.25
    if 'slippage' not in t:t['slippage']=5*(1+t.kind.ne(1).astype(int))
    t['net']=t.gross-t.commission-t.slippage
    t['native_mnq_net']=t.gross/10-1.25-t.slippage/10
    if not np.isfinite(t[['entry','exit','gross','net']]).all().all():raise RuntimeError('unknown price')
    assert t.side.isin([-1,1]).all()
    assert np.allclose(t.gross,(t.exit-t.entry)*t.side*20)
    t['missing_held_closes']=[int(np.isnan(g.c[int(r.day),int(r.j0):int(r.j1)+1]).sum()) for r in t.itertuples()]
    if 'cross_date' not in t:t['cross_date']=False
    return t


def parity(t,mc,label):
    mm=t.merge(mc,on='date',suffixes=('_py','_mc'),how='outer',indicator=True)
    common=mm[mm._merge=='both']
    bad=mm[(mm._merge!='both') | (abs(mm.entry_py-mm.entry_mc)>.2500001) | (abs(mm.gross_py-mm.gross_mc)>5.000001) | (mm.side_py!=mm.side_mc)].copy()
    bad.to_csv(OUT/CURRENT_PHASE/(label+'_parity_unmatched.csv'),index=False)
    if not len(common):return {'passed':False,'common':0}
    entry=(abs(common.entry_py-common.entry_mc)<=.2500001).mean()
    gross=(abs(common.gross_py-common.gross_mc)<=5.000001).mean()
    side=bool((common.side_py==common.side_mc).all())
    return {'passed':bool(entry>=.95 and gross>=.95 and side and not t.cross_date.any()),
            'common':len(common),'entry_within_tick':entry,'gross_within_5':gross,'all_sides_equal':side,
            'py_only':int((mm._merge=='left_only').sum()),'mc_only':int((mm._merge=='right_only').sum()),
            'cross_date':int(t.cross_date.sum())}


def fc_cases(g,start,end):
    mc=pd.read_csv(BASE/'fc_mc.csv',parse_dates=['date','exit_date'])
    selected={int(d.strftime('%Y%m%d')):int(s) for d,s in zip(mc.date,mc.side)}
    days=I.dt_days(g);frames=[]
    for date,x in days.items():
        x=x.copy();x['date']=date;row=int(np.searchsorted(g.dates,date))
        j=x.time.to_numpy()//100*60+x.time.to_numpy()%100
        x['volume']=g.v[row,j];frames.append(x)
    df=pd.concat(frames,ignore_index=True)
    ns={'np':np,'pd':pd,'PV':20.,'TICK':.25,'COST':17.25,'V1':False,'RS':None,'REF':None,
        'FIXED':selected,'FC_AUDIT':{},'P':{}}
    bind('fc_replica.py',['early_close'],ns)
    text=(BASE/'fc_replica.py').read_text();tree=ast.parse(text)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run')
    src=ast.get_source_segment(text,fn)
    line=next(s for s in src.splitlines() if s.strip().startswith('ok = warm and'))
    replacement=('            if FIXED is not None:\n'
                 '                ok = int(D[i]) in FIXED and pos == 0\n'
                 '                dr = FIXED.get(int(D[i]), dr)\n'
                 '            else:\n'
                 '                ok = warm and dr != 0 and pos == 0')
    src=src.replace(line,replacement)
    src=src.replace('return t, s','FC_AUDIT.update(open_position=int(pos), pending=pend is not None)\n    return t, s')
    exec(compile(src,'<FC MC admission / exact v2 exits>','exec'),ns)
    out={};audit={};P=dict(ZMin=1.,ZLookback=60,MinWarmup=20,SL=100.,Trail=150.,BER=.66,ExitTime=1458,Early=1130)
    for name,changes in [('original',{}),('no_flow_gate',{}),('no_BE',{'BER':0}),('no_trail',{'Trail':0})]:
        ns['P']={**P,**changes};ns['FIXED']=None if name=='no_flow_gate' else selected
        raw,_=ns['run'](df)
        raw=raw[(raw.date>=start)&(raw.date<=end)].copy()
        raw['day']=[int(np.searchsorted(g.ts,np.datetime64(d))) for d in raw.date]
        raw['j0']=[minute(h) for h in raw.t_in];raw['j1']=[minute(h) for h in raw.t_out]
        raw['cross_date']=raw.date.ne(raw.exit_date);raw['slippage']=10.
        out['FC2B/'+name]=normalize(raw,g);audit[name]=ns['FC_AUDIT'].copy()
    ref=mc[(mc.date>=start)&(mc.date<=end)]
    return out,{'baseline_parity':parity(out['FC2B/original'],ref,'FC2B'),'end_state':audit,
                'volume_scope':'MC-selected dates/sides; no native up-tick reconstruction'}


def score_blocks(g,atr):
    ch=[];oh=[];ah=[];last_month=0;month_count=0;rows=[]
    for d in range(g.D):
        if d>0:
            prev=pd.Timestamp(g.ts[d-1]);a=g.o[d-1,511:526];oc=np.flatnonzero(np.isfinite(a))
            cc=np.flatnonzero(np.isfinite(g.c[d-1,:901]));has=np.isfinite(g.c[d-1,660:916]).any()
            if prev.dayofweek<5 and has and len(oc) and len(cc):
                c=float(g.c[d-1,cc[-1]]);o=float(a[oc[0]])
                if c>0 and o>0:
                    ch.insert(0,c);oh.insert(0,o);ah.insert(0,float(atr[d-1]))
                    ch,oh,ah=ch[:100],oh[:100],ah[:100]
                    month_count=1 if prev.month!=last_month else month_count+1;last_month=prev.month
        date=pd.Timestamp(g.ts[d]);price=vol=calendar=np.nan
        if len(ch)>=59 and np.isfinite(atr[d]) and all(np.isfinite(ah[:59])):
            r1=np.log(ch[0]/ch[1]);r5=np.log(ch[0]/ch[5]);r20=np.log(ch[0]/ch[20]);rth=np.log(ch[0]/oh[0])
            ar=atr[d]/((atr[d]+sum(ah[:59]))/60);dist=np.log(ch[0]/np.mean(ch[:50]))
            r=np.log(np.array(ch[:20])/np.array(ch[1:21]));sd=r.std(ddof=1)
            rv=r[:5].std(ddof=1)/sd if sd>0 else 1.
            dow=date.dayofweek+1;tdm=1 if date.month!=last_month else month_count+1
            fri=date.day+5-dow;opex=int(1<=dow<=5 and 15<=fri<=21)
            price=2.550842376*r1+.05697325462*r5-.08269967616*r20+1.729498386*rth-.3355796551*dist
            vol=-.03608247696*ar-.03976333906*rv
            calendar=sum(w*(dow==k) for k,w in enumerate([.07809504609,-.008560935801,-.02267574106,-.03459885088,-.005544247888],1))+.1654566373*(tdm<=3)-.003794081905*opex
        rows.append({'day':d,'date':date,'price':price,'vol':vol,'calendar':calendar,
                     'score':.05535517974+price+vol+calendar})
    return pd.DataFrame(rows).set_index('day')


def onb_core(g,b,A,atr,early,walk,adx_min=30,stop_atr=.25,both=False,no_target=False):
    rows=[];B=96;H=b['h'].ravel();L=b['l'].ravel()
    for d in g.trading:
        if d==0 or not np.isfinite(atr[d]):continue
        start=(d-1)*B+93;end=d*B+34
        hh=np.nanmax(H[start:end+1]);ll=np.nanmin(L[start:end+1]);op=b['o'][d,35]
        if not(np.isfinite(hh) and np.isfinite(ll) and np.isfinite(op) and hh>ll and np.isfinite(b['c'][d,35])):continue
        position=(op-ll)/(hh-ll);bias=1 if position>=2/3 else -1 if position<=1/3 else 0
        if bias==0 and not both:continue
        up=b['h'][d,35];dn=b['l'][d,35];last=660 if early[d] else 840;flat=690 if early[d] else 870
        dist=stop_atr*atr[d];filled=False
        for i in range(35,95):
            if i*15>=last:break
            if not A[d,i]>adx_min:continue
            for j in range(i*15+1,min((i+1)*15,flat)+1):
                o=g.o[d,j]
                if not np.isfinite(o):continue
                side=bias
                if both:
                    if o>=up:side=1
                    elif o<=dn:side=-1
                    elif g.h[d,j]>=up and g.l[d,j]<=dn:side=1 if g.h[d,j]-o<=o-g.l[d,j] else -1
                    elif g.h[d,j]>=up:side=1
                    elif g.l[d,j]<=dn:side=-1
                    else:continue
                level=up if side==1 else dn
                if not ((side==1 and g.h[d,j]>=level) or (side==-1 and g.l[d,j]<=level)):continue
                entry=max(o,level) if side==1 else min(o,level)
                target=(np.inf if side==1 else -np.inf) if no_target else entry+side*3*dist
                j1,exit,kind,worst=walk(g.o[d],g.h[d],g.l[d],g.c[d],j,flat,side,entry-side*dist,target,1.)
                rows.append({'date':pd.Timestamp(g.ts[d]),'day':int(d),'j0':j,'j1':j1,'side':side,
                             'entry':entry,'exit':exit,'kind':kind,'gross':(exit-entry)*side*20})
                filled=True;break
            if filled:break
    return normalize(pd.DataFrame(rows),g)


def onb_cases(g,start,end):
    ns={'np':np,'pd':pd};bind('grid.py',['_walk'],ns);walk=ns['_walk']
    bind('candidates.py',['adx'],ns);bind('calendar.py',['is_early_close'],ns)
    b=g.bars(15);ok=np.isfinite(b['c']);A=np.full(b['c'].shape,np.nan)
    A[ok]=ns['adx'](b['h'][ok],b['l'][ok],b['c'][ok],14)
    atr=g.daily_atr(15);early=np.array([ns['is_early_close'](pd.Timestamp(d)) for d in g.ts])
    out={};base=onb_core(g,b,A,atr,early,walk)
    # Verify unchanged custom core against original pinned engine before interpreting counterfactuals.
    ref_ns={'np':np,'_walk':walk};bind('onb_engine.py',['onb_engine'],ref_ns)
    ref=ref_ns['onb_engine'](g.o,g.h,g.l,g.c,b['h'],b['l'],b['o'],b['c'],A,atr,g.trading,early,
                            1380,510,525,1/3,30,.25,3,840,870,660,690,1.,0)
    lhs=base[['day','j0','j1','side','entry','exit','kind','gross']].to_numpy(float)
    rhs=ref[g.ts[ref[:,0].astype(int)]>=np.datetime64("2018-01-01"),:8]
    if lhs.shape!=rhs.shape or not np.allclose(lhs,rhs):raise RuntimeError('ONB original core parity')
    for name,t in [('original',base),('no_ADX',onb_core(g,b,A,atr,early,walk,adx_min=-np.inf)),
                   ('no_overnight_bias',onb_core(g,b,A,atr,early,walk,both=True)),
                   ('no_target',onb_core(g,b,A,atr,early,walk,no_target=True))]:out['ONB30/'+name]=t
    parent=onb_core(g,b,A,atr,early,walk,adx_min=20,stop_atr=.30)
    scores=score_blocks(g,atr)
    vals=scores.reindex(parent.day)
    threshold=np.where(parent.side.to_numpy()>0,.03,0.)
    for name,score in [('original',vals.score),('no_ML',vals.score*0+1),
                       ('no_calendar',vals.score-vals.calendar),('no_price',vals.score-vals.price),('no_vol',vals.score-vals.vol)]:
        mask=np.isfinite(vals.score.to_numpy())&(score.to_numpy()>=threshold)
        out['ONBML/'+name]=parent[mask].copy()
    return {k:t[(t.date>=start)&(t.date<=end)].copy() for k,t in out.items()},scores,
    

def t_cases(g,start,end):
    ns={'np':np,'pd':pd,'jof':lambda h:minute(h)};bind('t_features.py',['days'],ns)
    # Exact completed15:00sessions for activev2 ATR, unlike old any1455..1500 approximation.
    text=(BASE/'t_features.py').read_text();tree=ast.parse(text)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='days')
    src=ast.get_source_segment(text,fn)
    src=src.replace('np.isfinite(g.c[r, jof(1455):jof(1500) + 1]).any()',
                    '(np.isfinite(g.c[r, jof(1500)]) and np.isfinite(g.o[r, jof(831)]))')
    exec(compile(src,'<active T prior exact15:00 range>','exec'),ns)
    D=ns['days'](g)
    mc=pd.read_csv(BASE/'t_mc.csv',parse_dates=['date','exit_date']);mc=mc[mc.t_in.eq(830)]
    first=mc.date.min();mc=mc[(mc.date>=start)&(mc.date<=end)]
    fixed={d:int(s) for d,s in zip(mc.date,mc.side)}
    eligible=D[D.valid&(D.med>0)&D.atr.notna()&(D.date>=max(pd.Timestamp(start),first))&(D.date<=end)]
    out={}
    for name in ['original','no_heavy_gate','follow_night','at_bell','no_stop']:
        rows=[]
        for r in eligible.itertuples():
            if name!='no_heavy_gate' and r.date not in fixed:continue
            side=int(-np.sign(r.ret)) if name=='no_heavy_gate' else fixed[r.date]
            if side==0:continue
            if name=='follow_night':side=-side
            j0=511 if name=='at_bell' else 510;j1=525;d=int(r.r)
            if not np.isfinite(g.o[d,j0]) or not np.isfinite(g.o[d,525]):raise RuntimeError('unknown T entry/exit')
            entry=g.o[d,j0];raw=entry-side*.4*r.atr
            stop=(np.floor(raw/.25+1e-10) if side>0 else np.ceil(raw/.25-1e-10))*.25
            exit=g.o[d,525];kind=2
            if name!='no_stop':
                for j in range(j0,525):
                    if not np.isfinite(g.o[d,j]):continue
                    if (side>0 and g.l[d,j]<=stop) or (side<0 and g.h[d,j]>=stop):
                        exit=min(g.o[d,j],stop) if side>0 else max(g.o[d,j],stop);j1=j;kind=0;break
            rows.append({'date':r.date,'day':d,'j0':j0,'j1':j1,'side':side,'entry':entry,'exit':exit,'kind':kind,
                         'gross':(exit-entry)*side*20,'slippage':10.})
        out['Tfade/'+name]=normalize(pd.DataFrame(rows),g)
    return out,{'baseline_parity':parity(out['Tfade/original'],mc,'Tfade'),
                'calendar_start':str(max(pd.Timestamp(start),first).date()),'volume_scope':'MC selection; all-night counterfactual uses no volume hurdle'}


def main(phase):
    global CURRENT_PHASE
    CURRENT_PHASE=phase
    manifest=json.loads((BASE/'source_manifest.json').read_text())
    for name,info in manifest.items():
        if I.digest(BASE/name)!=info['sha256']:raise RuntimeError('input source mismatch: '+name)
    dependency=json.loads((BASE/'dependency_manifest.json').read_text())
    for name,sha in dependency.items():
        if I.digest(ROOT/name)!=sha:raise RuntimeError('dependency mismatch: '+name)
    for path in (CODE,PLAN):
        if subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT)!=(ROOT/path).read_bytes():raise RuntimeError('commit first')
    dest=OUT/phase;dest.mkdir(parents=True,exist_ok=True)
    prior=None
    if phase=='recent':
        prior=json.loads((OUT/'design'/'summary.json').read_text())
        if prior['code_sha256']!=I.digest(ROOT/CODE):raise RuntimeError('frozen definition changed')
    end='2022-12-30' if phase=='design' else '2026-10-09';start='2018-01-01' if phase=='design' else '2023-01-01'
    g,_,inputs=I.grids(end);out={};audit={}
    if prior is None or prior['family_gates']['FC2B']:
        x,a=fc_cases(g,start,end);out.update(x);audit['FC2B']=a
    x,scores=onb_cases(g,start,end);out.update(x);scores.to_csv(dest/'frozen_score_blocks.csv')
    if prior is None or prior['family_gates']['Tfade']:
        x,a=t_cases(g,start,end);out.update(x);audit['Tfade']=a
    cal=pd.DatetimeIndex(g.ts[g.trading]);cal=cal[(cal>=start)&(cal<=end)]
    stats=[];effects=[];filters={}
    for key,t in out.items():
        family,var=key.split('/');stem=key.replace('/','__')
        t.to_csv(dest/(stem+'_trades.csv'),index=False)
        I.daily(t,cal).to_csv(dest/(stem+'_daily.csv'),header=['net'])
        for side in ['all','long','short']:
            sub=t if side=='all' else t[t.side.eq(1 if side=='long' else -1)]
            stats.append({'family':family,'variant':var,'side':side,'period':phase,**I.metric(sub,cal)})
        for year in sorted(cal.year.unique()):
            sub=t[t.date.dt.year==year]
            stats.append({'family':family,'variant':var,'side':'all','period':str(year),**I.metric(sub,cal[cal.year==year])})
    for key,t in out.items():
        family,var=key.split('/')
        if var=='original':continue
        delta=I.daily(out[family+'/original'],cal)-I.daily(t,cal)
        ci=R.bootstrap(delta,n=1000,block=20,seed=SEED,chunk=250).loc['annual']
        effects.append({'family':family,'component_removed':var,'original_minus_variant':delta.sum(),
                        'annual_effect_p5':ci.p5,'annual_effect_p50':ci.p50,'annual_effect_p95':ci.p95})
    for fam,var in [('FC2B','no_flow_gate'),('ONBML','no_ML'),('Tfade','no_heavy_gate')]:
        if fam+'/original' in out:filters[fam]=I.filter_control(out[fam+'/original'],out[fam+'/'+var],cal)
    gates={'ONB30':True,'ONBML':True}
    for fam in ['FC2B','Tfade']:gates[fam]=bool(audit.get(fam,{}).get('baseline_parity',{}).get('passed',False))
    summary={'phase':phase,'source_snapshot':I.DATA_REF,'start':start,'end':end,'case_count':len(out),
             'family_gates':gates,'baseline_audit':audit,'pure_filter_controls':filters,'inputs':inputs,
             'source_sha256':{p.name:I.digest(p) for p in BASE.iterdir()},'code_sha256':I.digest(ROOT/CODE),
             'plan_sha256':I.digest(ROOT/PLAN),'plan_commit':subprocess.check_output(['git','log','-1','--format=%H','--',PLAN],cwd=ROOT,text=True).strip(),
             'portfolio_tests_run':False,'ML_fit_scope':'frozen coefficients fitted on2018–26; both splits in-sample attribution',
             'volume_scope':'FC/T baseline admission from retained MC events; totalTicks not substituted for up-tickVolume'}
    pd.DataFrame(stats).to_csv(dest/'metrics.csv',index=False)
    pd.DataFrame(effects).to_csv(dest/'paired_effects.csv',index=False);I.dump(dest/'summary.json',summary)
    print(pd.DataFrame(stats).query('side=="all" and period==@phase')[['family','variant','trades','total','avg','t_trade','sharpe','max_dd','worst_trade']].round(2).to_string(index=False),flush=True)
    print(json.dumps({'phase':phase,'gates':gates,'audit':audit},indent=2,default=float),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['design','recent'],required=True)
    main(p.parse_args().phase)
