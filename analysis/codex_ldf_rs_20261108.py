"""Preregistered late-day RS design screen, no optimizer or live integration."""
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd
import metrics as M
import resampling as R
import codex_ingredients_three_20261108 as I

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_ldf_rs_20261108'
PLAN='agents/codex/plans/ldf_rs_20261108.md'
CODE='analysis/codex_ldf_rs_20261108.py'
DEPENDENCIES=ROOT/'agents/codex/inputs/ldf_rs_20261108/dependencies.json'
SEED=20261108


def execute(g,day,side,atr,entry_j=841):
    if side not in (-1,1) or not np.isfinite(atr) or atr<=0:raise ValueError('invalid side/ATR')
    if not all(np.isfinite(getattr(g,c)[day,entry_j:871]).all() for c in ('o','h','l','c')):
        raise ValueError('unknown executable or held path')
    raw_entry=float(g.o[day,entry_j]);entry=raw_entry+side*.25
    stop=entry-side*.25*atr;exit_j=870;kind='flat';px=None
    for j in range(entry_j,871):
        hit=g.l[day,j]<=stop if side>0 else g.h[day,j]>=stop
        if hit:
            raw_exit=min(g.o[day,j],stop) if side>0 else max(g.o[day,j],stop)
            px=float(raw_exit-side*.25);exit_j=j;kind='stop';break
    if px is None:raw_exit=float(g.c[day,870]);px=raw_exit-side*.25
    gross=(float(raw_exit)-raw_entry)*side*20
    net=(px-entry)*side*20-7.25
    if abs(net-(gross-17.25))>1e-6:raise RuntimeError('cost bridge')
    return {'day':int(day),'side':int(side),'j0':entry_j,'j1':exit_j,'kind':kind,
            'raw_entry':raw_entry,'raw_exit':float(raw_exit),'entry':entry,'exit':px,'stop':stop,
            'gross':gross,'commission':7.25,'slippage':10.,'net':net,
            'native_mnq_net':gross/10-2.25,'extra_tick_cost_net':net-10.}


def synthetic_checks():
    from types import SimpleNamespace
    g=SimpleNamespace(**{c:np.full((1,1440),100.) for c in ('o','h','l','c')})
    a=execute(g,0,1,4);assert a['kind']=='flat' and a['net']==-17.25 and a['native_mnq_net']==-2.25
    g.l[0,841]=99.;a=execute(g,0,1,4);assert a['kind']=='stop' and a['j1']==841 and a['net']==-32.25
    g.l[0,841]=100.;g.h[0,841]=101.;a=execute(g,0,-1,4);assert a['kind']=='stop' and a['net']==-32.25
    g.h[0,841]=100.;g.o[0,842]=97.;g.l[0,842]=96.;a=execute(g,0,1,4)
    assert a['kind']=='stop' and a['exit']==96.75 and a['j1']==842
    g.c[0,845]=np.nan
    try:execute(g,0,1,4)
    except ValueError:pass
    else:raise AssertionError('missing held path must reject')
    return {'groups_passed':5,'scope':'invented long/short/entry-bar/gap/flatten/missing-path checks only'}


def daily(t,cal,col='net'):
    x=t.groupby('date')[col].sum().reindex(cal,fill_value=0.)
    if abs(x.sum()-t[col].sum())>.005:raise RuntimeError('cash ledger mismatch')
    return x


def tstat(x):return x.mean()/x.std(ddof=1)*np.sqrt(len(x)) if len(x)>1 and x.std()>0 else np.nan
def metric(t,cal):
    d=daily(t,cal);m=M.perf(d,t.net,capital=50000)
    m['max_dd']=R.max_dd(d);m['calmar']=m['annual']/m['max_dd'] if m['max_dd'] else np.nan
    m.update(total=t.net.sum(),gross=t.gross.sum(),commission=t.commission.sum(),slippage=t.slippage.sum(),
             t_trade=tstat(t.net),native_mnq_total=t.native_mnq_net.sum(),worst=t.net.min(),
             native_mnq_worst=t.native_mnq_net.min(),cost_stress_total=t.extra_tick_cost_net.sum(),
             positive_years=int((t.groupby(t.date.dt.year).net.sum()>0).sum()))
    return m


def trade_rows(g,features,which,entry_j=841):
    rows=[]
    for r in features.itertuples():
        side=getattr(r,which)
        if side==0:continue
        a=execute(g,int(r.day),int(side),float(r.atr),entry_j)
        rows.append({'date':r.date,**a})
    columns=['date','day','side','j0','j1','kind','raw_entry','raw_exit','entry','exit','stop','gross',
             'commission','slippage','net','native_mnq_net','extra_tick_cost_net']
    return pd.DataFrame(rows,columns=columns)


def main():
    for p in (PLAN,CODE):
        if subprocess.check_output(['git','show','HEAD:'+p],cwd=ROOT)!=(ROOT/p).read_bytes():
            raise RuntimeError('commit exact plan/script before returns')
    deps=json.loads(DEPENDENCIES.read_text())
    for p,want in deps.items():
        if I.digest(ROOT/p)!=want:raise RuntimeError('frozen dependency changed: '+p)
    OUT.mkdir(parents=True,exist_ok=True)
    I.dump(OUT/'synthetic_checks.json',synthetic_checks())
    g,e,inputs=I.grids('2022-12-30')
    _,rs,lf=I.setup_engines(g,e)
    days,N,E=rs['load']();Z=rs['signals'](days,N,E,decide=1400)
    atr=g.daily_atr(15);rows=[];excluded=[]
    for i,r in enumerate(days.itertuples()):
        date=pd.Timestamp(str(r.date));day=int(r.d)
        if date<pd.Timestamp('2018-01-01'):continue
        reason=None
        if not r.ok:reason='source_RS_calendar_or_session'
        elif not np.isfinite(Z[i]):reason='unavailable_residual'
        elif not np.isfinite(atr[day]) or atr[day]<=0:reason='unavailable_ATR'
        elif not np.isfinite(g.o[day,511]) or not np.isfinite(g.c[day,840]):reason='missing_ownmove_anchor'
        elif not np.isfinite(e.c[int(r.k),840]):reason='missing_ES_decision_close'
        elif not all(np.isfinite(getattr(g,c)[day,841:871]).all() for c in ('o','h','l','c')):
            reason='unknown_execution_or_held_path'
        if reason:excluded.append({'date':date,'reason':reason});continue
        move=float(g.c[day,840]-g.o[day,511]);ownside=int(np.sign(move));rs_side=int(np.sign(Z[i]))
        ldf=ownside if abs(move)>=.4*atr[day] else 0
        late_rs=rs_side if abs(Z[i])>=1.25 else 0
        combined=ldf if ldf and ldf==late_rs else 0
        rows.append({'date':date,'day':day,'atr':atr[day],'own_move':move,'Z1400':Z[i],
                     'LDF':ldf,'LateRS':late_rs,'Combined':combined})
    f=pd.DataFrame(rows);cal=pd.DatetimeIndex(f.date)
    if f.date.duplicated().any():raise RuntimeError('duplicate event date')
    f.to_csv(OUT/'design_features_before_returns.csv',index=False)
    pd.DataFrame(excluded,columns=['date','reason']).to_csv(OUT/'design_exclusions.csv',index=False)
    I.dump(OUT/'no_return_gate.json',{'eligible_sessions':len(f),'signal_counts':{
        x:int(f[x].ne(0).sum()) for x in ['LDF','LateRS','Combined']},
        'exclusions':pd.DataFrame(excluded).reason.value_counts().to_dict() if excluded else {},
        'coverage_is_research_admission_not_a_tradable_future_skip_rule':True})
    # Original LDF baseline receipt and independent baseline parity precede candidate pricing.
    original=lf['trades'](g,.4,.25,j_exit=870)
    original=original[(original.date>='2018-01-01')&(original.date<='2022-12-30')]
    base=trade_rows(g,f,'LDF')
    admitted=original[original.date.isin(cal)]
    mm=base.merge(admitted[['date','side','net']],on='date',how='outer',suffixes=('_new','_source'))
    if not len(mm)==len(base)==len(admitted) or not np.allclose(mm.net_new,mm.net_source) or not np.array_equal(mm.side_new,mm.side_source):
        raise RuntimeError('independent LDF baseline parity failed')
    I.dump(OUT/'baseline_parity.json',{'common_trades':len(base),'exact_net_side_match':True,
        'unrestricted_source_trades':len(original),'unrestricted_source_net':original.net.sum(),
        'source_trades_outside_common_universe':len(original)-len(admitted),
        'source_net_outside_common_universe':original.net.sum()-admitted.net.sum()})
    cases={'LDF':base,'LateRS':trade_rows(g,f,'LateRS'),'Combined':trade_rows(g,f,'Combined'),
           'LateRS_delay1m':trade_rows(g,f,'LateRS',842),'Combined_delay1m':trade_rows(g,f,'Combined',842)}
    metrics=[];bycase={}
    for name,t in cases.items():
        t.to_csv(OUT/(name+'_trades.csv'),index=False)
        d=pd.DataFrame({c:daily(t,cal,c) for c in ['gross','commission','slippage','net','native_mnq_net']})
        d.to_csv(OUT/(name+'_daily.csv'))
        bycase[name]=metric(t,cal)
        for side in ['all','long','short']:
            sub=t if side=='all' else t[t.side.eq(1 if side=='long' else -1)]
            metrics.append({'case':name,'period':'2018-22','side':side,**metric(sub,cal)})
        for year in sorted(cal.year.unique()):
            sub=t[t.date.dt.year==year]
            metrics.append({'case':name,'period':str(year),'side':'all',**metric(sub,cal[cal.year==year])})
    effects={}
    for name in ['LateRS','Combined']:
        delta=daily(cases[name],cal)-daily(base,cal)
        b=R.bootstrap(delta,n=1000,block=20,seed=SEED,chunk=250).loc['annual']
        effects[name]={'total_increment':delta.sum(),'annual_p5':b.p5,'annual_p50':b.p50,'annual_p95':b.p95}
    control=I.filter_control(cases['Combined'],base,cal)
    gates={};benchmark=bycase['LDF']
    for name in ['LateRS','Combined']:
        m=bycase[name]
        q={'trades_ge30':m['trades']>=30,'gross_net_positive':m['gross']>0 and m['total']>0,
           'trade_t_ge2':m['t_trade']>=2,'PF_ge1_2':m['profit_factor']>=1.2,
           'positive_years_ge3':m['positive_years']>=3,'net_beats_LDF':m['total']>benchmark['total'],
           'DD_not_worse_LDF':m['max_dd']<=benchmark['max_dd'],'Sharpe_not_worse_LDF':m['sharpe']>=benchmark['sharpe'],
           'delay1m_positive':bycase[name+'_delay1m']['total']>0,'extra_tick_cost_positive':m['cost_stress_total']>0,
           'paired_annual_p5_positive':effects[name]['annual_p5']>0}
        if name=='Combined':
            q.update(pure_nested_filter=control['pure_nested_filter'],
                     removed_trades_negative=control.get('removed_total',np.nan)<0 and control.get('removed_t',np.nan)<=-1,
                     random_drop_profit=control.get('random_profit_ge_actual',1)<=.05,
                     random_drop_DD=control.get('random_dd_le_actual',1)<=.05)
        gates[name]={'checks':q,'passed':bool(all(q.values()))}
    passed=[x for x in ['LateRS','Combined'] if gates[x]['passed']]
    selected=max(passed,key=lambda x:(bycase[x]['calmar'],bycase[x]['total'],x=='Combined')) if passed else None
    pd.DataFrame(metrics).to_csv(OUT/'metrics.csv',index=False)
    result={'stage':'2018-22 design','rule_definitions':3,'delay_replays':2,'account_tests_run':False,
            'recent_return_tests_run':False,'selected':selected,'results':bycase,'gates':gates,'paired_effects':effects,
            'combined_filter_control':control,'source_snapshot':I.DATA_REF,'inputs':inputs,'dependencies':deps,
            'plan_commit':subprocess.check_output(['git','log','-1','--format=%H','--',PLAN],cwd=ROOT,text=True).strip(),
            'script_sha256':I.digest(ROOT/CODE),'plan_sha256':I.digest(ROOT/PLAN),
            'prior_selection':'new interaction proposed after already-seen ingredient diagnostics; not independent discovery'}
    I.dump(OUT/'results.json',result)
    print(pd.DataFrame(bycase).T[['trades','total','avg','t_trade','sharpe','profit_factor','max_dd','native_mnq_total']].to_string())
    print(json.dumps({'selected':selected,'gates':gates,'paired_effects':effects,'combined_filter_control':control},indent=2,default=float))


if __name__=='__main__':main()
