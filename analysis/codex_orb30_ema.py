"""Frozen ORB30/EMA reconstruction. Reuses g24; no broker or cache writes.

Run with configured Python: --stage checks/design/validation/diagnostics.
Minute close labels: OR511..540, order first active541, flatten956 open.
"""
from pathlib import Path
import argparse, hashlib, json, pickle, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scratch_data/codex_deps'),str(ROOT/'analysis')]
import numpy as np
import pandas as pd
from numba import njit
import grid24
import metrics as M
import resampling as R
import montecarlo as MC
from codex_s03_calendar import calendar_status, synthetic_checks as calendar_checks
from trials import parse_tier_list

OUT=ROOT/'analysis/outputs/codex_orb30_ema'
PLAN='agents/codex/plans/orb30_ema.md'
SEED=20261027
COLS=['day','j0','j1','entry','exit','risk','kind','gross','mae_points','mfe_points','unknown_held_minutes','unclosed']

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()

def dump(name,x):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(x,indent=2,default=lambda v: v.item() if isinstance(v,np.generic) else str(v))+'\n',encoding='utf-8')

@njit(cache=False)
def simulate(o,h,l,c,hi,lo,allow,rr,start,finish,mode=0,path_mode=0,side=1):
    """mode0 resting breakout; mode1 control market. side-1 mirrored control.
    Controls use OR width from their actual fill; candidate stop stays OR low.
    Returns tickets and a minute-path equity ledger in risk units before costs.
    """
    D=o.shape[0]; out=np.empty((D,12)); n=0
    marks=np.full((D,416),np.nan)  # first541..956; retained for floating audit
    for d in range(D):
        if not allow[d]:continue
        active=False; entry=0.;risk=0.;stop=0.;target=0.;ei=0;worst=0.;best=0.;missing=0
        for j in range(start[d],finish+1):
            oo,hh,ll,cc=o[d,j],h[d,j],l[d,j],c[d,j]
            if not (np.isfinite(oo) and np.isfinite(hh) and np.isfinite(ll) and np.isfinite(cc)):
                if active:missing+=1
                continue
            # At flatten timestamp, order is cancelled BEFORE entry processing.
            if j==finish:
                if active:
                    out[n]=np.array([d,ei,j,entry,oo,risk,0,(oo-entry)*side*20,worst,best,missing,0])
                    marks[d,j-541]=(oo-entry)*side/risk;n+=1;active=False
                break
            points=np.empty(4);points[0]=oo;points[3]=cc
            high_first=(abs(oo-hh)<abs(oo-ll))
            if path_mode:high_first=not high_first
            points[1]=hh if high_first else ll;points[2]=ll if high_first else hh
            entered_here=False
            if not active:
                if mode==1 or oo>=hi[d]:
                    entry=oo if mode==1 else max(hi[d],oo)
                    risk=hi[d]-lo[d] if mode==1 else entry-lo[d]
                    if risk<=0:break
                    stop=entry-side*risk
                    target=(np.ceil((entry+rr*risk)*4)/4 if side>0 else np.floor((entry-rr*risk)*4)/4) if rr>0 else side*1e100
                    active=True;entered_here=True;ei=j
                elif hh<hi[d]:continue
            px=oo;done=False
            if active and not entered_here:
                if (oo-stop)*side<=0:
                    out[n]=np.array([d,ei,j,entry,oo,risk,2,(oo-entry)*side*20,max(worst,(entry-oo)*side),best,missing,0]);n+=1;done=True
                elif rr>0 and (oo-target)*side>=1:
                    out[n]=np.array([d,ei,j,entry,target,risk,1,(target-entry)*side*20,worst,max(best,(target-entry)*side),missing,0]);n+=1;done=True
            if done:
                marks[d,j-541]=(out[n-1,4]-entry)*side/risk;active=False;break
            minute_worst=0.;minute_best=0.
            for k in range(1,4):
                dest=points[k]
                if not active:
                    if mode==0 and dest>=hi[d] and px<hi[d]:
                        entry=hi[d];risk=entry-lo[d]
                        if risk<=0:break
                        stop=lo[d];target=np.ceil((entry+rr*risk)*4)/4 if rr>0 else 1e100
                        active=True;ei=j;px=entry
                    else:px=dest;continue
                hitstop=(dest-stop)*side<=0 and (dest-px)*side<0
                hittarget=rr>0 and (dest-target)*side>=1 and (dest-px)*side>0
                end=stop if hitstop else (target if hittarget else dest)
                worst=max(worst,(entry-end)*side);best=max(best,(end-entry)*side)
                minute_worst=min(minute_worst,(end-entry)*side/risk)
                minute_best=max(minute_best,(end-entry)*side/risk)
                if hitstop or hittarget:
                    kind=2 if hitstop else 1
                    out[n]=np.array([d,ei,j,entry,end,risk,kind,(end-entry)*side*20,worst,best,missing,0]);n+=1;active=False;done=True;break
                px=dest
            if active or done:
                # Close marks retained, plus exact per-ticket MAE/MFE. Full path DD
                # is calculated in a separate path replay, not inferred from MAE.
                marks[d,j-541]=((out[n-1,4] if done else cc)-entry)*side/risk
            if done:break
        if active:
            out[n]=np.array([d,ei,finish,entry,np.nan,risk,0,np.nan,worst,best,missing,1]);n+=1
    return out[:n],marks

def load():
    committed=subprocess.check_output(['git','show','HEAD:'+PLAN],cwd=ROOT,text=True)
    assert committed.replace('\r\n','\n')==(ROOT/PLAN).read_text().replace('\r\n','\n')
    with (ROOT/'scratch_data/g24.pkl').open('rb') as f:g=pickle.load(f)
    ts=pd.DatetimeIndex(g.ts)
    b=g.bars(30)
    # bars() permits partial bars; EMA here explicitly admits complete bars only.
    flat=np.isfinite(g.c).ravel();pad=29;tail=(-(len(flat)+pad))%30
    count=np.r_[np.zeros(pad,bool),flat,np.zeros(tail,bool)].reshape(-1,30).sum(1)[:g.D*48].reshape(g.D,48)
    ema={};alpha=2/21
    for key in ['FULL','CASH']:
        values=np.full(g.D,np.nan);e=np.nan;nb=0
        for d in range(g.D):
            for k in range(48):
                j=k*30
                if count[d,k]!=30 or (key=='CASH' and not 540<=j<=900):continue
                v=b['c'][d,k];e=v if not np.isfinite(e) else alpha*v+(1-alpha)*e;nb+=1
                if j==540 and nb>=20:values[d]=e
        ema[key]=values
    calendar=pd.DataFrame([dict(date=t,**calendar_status(t)) for t in ts])
    normal=calendar.kind.eq('normal').to_numpy()
    complete=np.isfinite(g.c[:,511:541]).all(1)
    hi=np.max(g.h[:,511:541],axis=1);lo=np.min(g.l[:,511:541],axis=1)
    valid=normal&complete&np.isfinite(hi)&np.isfinite(lo)&(hi>lo)&(ts>=pd.Timestamp('2018-01-01'))&(ts<=pd.Timestamp('2026-10-09'))
    gate={k:valid&(g.c[:,540]>e)&np.isfinite(e) for k,e in ema.items()}
    gate['NONE']=valid
    return g,ts,hi,lo,gate,calendar

def replay(g,ts,hi,lo,allow,rr,mode=0,start=None,path_mode=0,side=1):
    if start is None:start=np.full(g.D,541,np.int64)
    raw,marks=simulate(g.o,g.h,g.l,g.c,hi,lo,allow,rr,start,956,mode,path_mode,side)
    t=pd.DataFrame(raw,columns=COLS)
    for k in ['day','j0','j1','kind','unknown_held_minutes','unclosed']:t[k]=t[k].astype(int)
    t['date']=ts[t.day];t['side']=side
    t['commission']=7.25;t['slippage']=5*(1+t.kind.ne(1).astype(int))
    t['net']=t.gross-t.commission-t.slippage
    t['extra_tick_net']=t.net-t.slippage
    t['mnq_net']=t.gross/10-1.24-t.slippage/10
    t['mnq_net_lowfee']=t.gross/10-1.04-t.slippage/10
    t['net_r']=t.net/(20*t.risk);t['mnq_r']=t.mnq_net/(2*t.risk)
    return t,marks

def days_for(ts,gate,period):
    # All scheduled normal opportunities with complete OR, not just passing EMA.
    a=gate['NONE'].copy()
    if period=='design':a&=ts.year<=2022
    if period=='validation':a&=ts.year>=2023
    if str(period).isdigit():a&=ts.year==int(period)
    return ts[a]

def daily(t,days,col='net'):
    return t.groupby('date')[col].sum().reindex(days,fill_value=0.)

def stats(t,days,model,period):
    d=daily(t,days);r=daily(t,days,'net_r')
    z=M.perf(np.r_[0,d.to_numpy()],t.net)
    z.update(model=model,period=period,side='all=long',short_trades=0,total=float(t.net.sum()),gross=float(t.gross.sum()),commission=float(t.commission.sum()),slippage=float(t.slippage.sum()),t=float(d.mean()/d.std()*np.sqrt(len(d))) if d.std()>0 else 0.,r_t=float(r.mean()/r.std()*np.sqrt(len(r))) if r.std()>0 else 0.,r_sharpe=float(r.mean()/r.std()*np.sqrt(252)) if r.std()>0 else 0.,mean_r=float(t.net_r.mean()),mean_r_day=float(r.mean()),extra_tick_total=float(t.extra_tick_net.sum()),mnq_total=float(t.mnq_net.sum()),missing_held=int(t.unknown_held_minutes.sum()),unclosed=int(t.unclosed.sum()),breakeven_extra_cost=float(t.net.mean()))
    z['max_dd']=R.max_dd(d)
    return z

def passes(z,t):
    years=t.groupby(t.date.dt.year).net.sum()
    return bool(z['total']>0 and z['profit_factor']>=1.15 and z['r_t']>=2 and (years>0).sum()>=3 and z['extra_tick_total']>0 and not z['unclosed'])

def equity_audit(g,t):
    """Chronological within-minute path equity, including initial/exit fees.
    Ideal continuous NQ fraction and separately integer MNQ1% balances.
    Entry orders size from known OR distance; gap overshoot remains visible.
    """
    balance=100000.;peak=balance;maxdd=0.;intbal=100000.;intpeak=intbal;intdd=0.;skip=0;maxqty=0;gapovershoot=0;records=[]
    for q in t.itertuples():
        if q.unclosed:continue
        b0=balance;ib0=intbal;weight=b0*.01/(q.risk*20.)
        planned=float(np.max(g.h[q.day,511:541])-np.min(g.l[q.day,511:541]))
        qty=max(0,int(ib0*.01/(planned*2)))
        skip+=qty==0;maxqty=max(maxqty,qty);gapovershoot+=qty*q.risk*2>ib0*.01+1e-8
        fee0=12.25*weight;ifee0=1.74*qty
        def visit(px):
            nonlocal peak,maxdd,intpeak,intdd
            eq=b0+(px-q.entry)*20*weight-fee0
            ieq=ib0+((px-q.entry)*2*qty)-ifee0
            peak=max(peak,eq);maxdd=max(maxdd,1-eq/peak)
            intpeak=max(intpeak,ieq);intdd=max(intdd,1-ieq/intpeak)
        visit(q.entry)
        for j in range(q.j0,q.j1+1):
            oo,hh,ll,cc=(a[q.day,j] for a in [g.o,g.h,g.l,g.c])
            if not np.isfinite(cc):continue
            if j==q.j1 and q.kind==0:visit(q.exit);break
            highfirst=abs(oo-hh)<abs(oo-ll)
            pts=[oo,hh,ll,cc] if highfirst else [oo,ll,hh,cc]
            live=(j!=q.j0 or oo>=q.entry)
            if live:
                if j==q.j1 and ((q.kind==2 and oo<=q.exit) or (q.kind==1 and oo>=q.exit+1)):
                    visit(q.exit);break
                visit(oo)
            prev=oo;done=False
            for dest in pts[1:]:
                if not live:
                    if prev<q.entry<=dest:live=True;prev=q.entry
                    else:prev=dest;continue
                if j==q.j1 and ((q.kind==2 and dest<=q.exit and dest<prev) or (q.kind==1 and dest>=q.exit+1 and dest>prev)):
                    visit(q.exit);done=True;break
                visit(dest);prev=dest
            if done:break
        balance=b0+q.net*weight
        intbal=ib0+q.mnq_net*qty
        peak=max(peak,balance);maxdd=max(maxdd,1-balance/peak)
        intpeak=max(intpeak,intbal);intdd=max(intdd,1-intbal/intpeak)
        records.append(dict(date=q.date,entry_balance=b0,exit_balance=balance,integer_entry_balance=ib0,integer_exit_balance=intbal,mnq_qty=qty,planned_risk=qty*planned*2,actual_stop_risk=qty*q.risk*2))
    return dict(ideal_initial=100000,ideal_terminal=balance,ideal_floating_dd=maxdd,integer_mnq_terminal=intbal,integer_mnq_floating_dd=intdd,integer_zero_lot_skips=skip,max_integer_mnq_qty=maxqty,gap_risk_overshoots=gapovershoot,margin_constraint_applied=False,mark_resolution='nearer-extreme minute OHLC path, not actual ticks',unobserved_held_minutes=int(t.unknown_held_minutes.sum())),pd.DataFrame(records)

def run_design():
    g,ts,hi,lo,gate,cal=load();rows=[];stage=[];tickets={}
    cal.to_csv(OUT/'calendar.csv',index=False)
    for name,key in [('FULL185','FULL'),('CASH185','CASH'),('NOEMA185','NONE')]:
        allow=gate[key]&(ts.year<=2022)
        t,_=replay(g,ts,hi,lo,allow,1.85);tickets[name]=t
        t.to_csv(OUT/(name+'_design_trades.csv'),index=False)
        z=stats(t,days_for(ts,gate,'design'),name,'2018-22');z['design_pass']=passes(z,t);rows.append(z)
    candidates=[z for z in rows[:2] if z['design_pass']]
    chosen=max(candidates,key=lambda z:z['r_sharpe'])['model'][:4] if candidates else None
    # CASH and FULL are both exactly four letters.
    specs={z['model']:[z['model'][:4],1.85] for z in rows[:2]}
    if chosen:
        for name,rr in [('SELECTED4',4.),('SELECTED0',0.)]:
            t,_=replay(g,ts,hi,lo,gate[chosen]&(ts.year<=2022),rr);tickets[name]=t
            t.to_csv(OUT/(name+'_design_trades.csv'),index=False)
            z=stats(t,days_for(ts,gate,'design'),name,'2018-22');z['design_pass']=passes(z,t);rows.append(z);specs[name]=[chosen,rr]
    pd.DataFrame(rows).to_csv(OUT/'design_metrics.csv',index=False)
    eligible=[z['model'] for z in rows if z['design_pass'] and z['model']!='NOEMA185']
    # Only the selected original EMA is eligible for later use; the other is
    # still reported in design, not a validation-dependent choice.
    eligible=[x for x in eligible if x.startswith('SELECTED') or x==str(chosen)+'185']
    binding=dict(chosen_ema=chosen,eligible=eligible,models_executed=len(rows),specs=specs,rows=rows,validation_run=False,code_sha=sha(__file__),cache_sha=sha(ROOT/'scratch_data/g24.pkl'),plan_commit=subprocess.check_output(['git','log','-1','--format=%H','--',PLAN],cwd=ROOT,text=True).strip(),seed=SEED,python=sys.version,numpy=np.__version__,pandas=pd.__version__,calendar_sha=sha(ROOT/'analysis/codex_s03_calendar.py'))
    dump('design_gate.json',binding)
    print(pd.DataFrame(rows)[['model','trades','win','avg','profit_factor','mean_r','r_t','r_sharpe','max_dd','design_pass']].to_string(index=False),flush=True)
    print('CHOSEN',chosen,'ELIGIBLE',eligible,flush=True)

def validate():
    gate_record=json.loads((OUT/'design_gate.json').read_text());assert gate_record['code_sha']==sha(__file__)
    if not gate_record['eligible']:raise SystemExit('STOP: design gate failed; no validation.')
    g,ts,hi,lo,gate,cal=load();rows=[]
    specs={name:gate_record['specs'][name] for name in gate_record['eligible']}
    specs['NOEMA185']=['NONE',1.85]
    for name,(key,rr) in specs.items():
        t,_=replay(g,ts,hi,lo,gate[key]&(ts.year>=2023),rr)
        t.to_csv(OUT/(name+'_validation_trades.csv'),index=False)
        old=pd.read_csv(OUT/(name+'_design_trades.csv'),parse_dates=['date']);all_t=pd.concat([old,t],ignore_index=True)
        all_t.to_csv(OUT/(name+'_trades.csv'),index=False)
        for period in ['design','validation','all']+[str(x) for x in range(2018,2027)]:
            ds=days_for(ts,gate,period);q=all_t[all_t.date.isin(ds)]
            if len(q):rows.append(stats(q,ds,name,period))
    pd.DataFrame(rows).to_csv(OUT/'metrics.csv',index=False)
    dump('validation_complete.json',dict(models=list(specs),selection_frozen=gate_record['chosen_ema'],fresh_holdout=False))
    print(pd.DataFrame(rows).query("period in ['design','validation','all']")[['model','period','trades','win','profit_factor','mean_r','r_t','max_dd']].to_string(index=False))

def checks():
    # Synthetic entry-bar ordering, cancellation, gap risk, protection and target-through.
    shape=(1,1440);a=[np.full(shape,np.nan) for _ in range(4)]
    def setbar(j,o,h,l,c):
        for x,v in zip(a,[o,h,l,c]):x[0,j]=v
    setbar(541,91,101,90,100);setbar(956,100,100,100,100)
    args=[*a,np.array([100.]),np.array([90.]),np.array([True]),1.85,np.array([541]),956]
    z,_=simulate(*args);assert len(z)==1 and z[0,7]==0 # pre-entry low not a stop
    setbar(541,100,101,89,95);z,_=simulate(*args);assert z[0,6]==2 and z[0,4]==90
    setbar(541,105,106,104,105);z,_=simulate(*args);assert z[0,3]==105 and z[0,5]==15
    setbar(541,99,99,98,99);setbar(956,105,120,90,100);z,_=simulate(*args);assert len(z)==0
    setbar(541,100,118.5,100,118);z,_=simulate(*args);assert z[0,6]==0
    setbar(541,100,119.5,100,118);z,_=simulate(*args);assert z[0,6]==1
    x=np.array([.5,-1,1.85,-.3,1]);eq=np.r_[1,np.cumprod(1+.01*x)]
    dd=lambda e:float(np.max(1-e/np.maximum.accumulate(e)))
    assert abs(dd(eq)-dd(eq*2))<1e-12
    sub=np.r_[1,np.cumprod(1+.01*x[2:])];assert dd(sub)<=dd(eq)+1e-12
    dump('synthetic_checks.json',dict(calendar=calendar_checks(),causal_stop=True,entry_gap_risk=True,cancel_before_flat=True,target_through=True,entry_bar_protection=True,scaling_invariant=True,subset_relative_dd_bound=True))
    print('Synthetic checks passed')

def diagnostics():
    b=json.loads((OUT/'design_gate.json').read_text());g,ts,hi,lo,gates,cal=load()
    name=str(b['chosen_ema'])+'185' if b['chosen_ema'] else max(b['rows'][:2],key=lambda z:z['r_sharpe'])['model']
    # On failed screen, diagnostic selection is descriptive and cannot revive it.
    key=name[:4];periods=['design','validation','all'] if (OUT/'validation_complete.json').exists() else ['design']
    modelnames=b['eligible'] if b['eligible'] else [name]
    summaries={};nullrows=[];rng=np.random.default_rng(SEED)
    for period in periods:
        ds=days_for(ts,gates,period);allow=gates[key]&ts.isin(ds)
        for model in modelnames:
            _,rr=b['specs'][model]
            t,marks=replay(g,ts,hi,lo,allow,rr)
            d=daily(t,ds);dr=daily(t,ds,'net_r');dm=daily(t,ds,'mnq_net')
            R.bootstrap(d,n=5000,block=10,seed=SEED).to_csv(OUT/(model+'_'+period+'_bootstrap.csv'))
            R.bootstrap(dr,n=5000,block=10,seed=SEED,capital=100).to_csv(OUT/(model+'_'+period+'_R_bootstrap.csv'))
            perm=R.permutation(dm,n=10000,seed=SEED)
            mc=MC.daily_mc(dm,n=5000,seed=SEED)
            # Pure 1% fractional recomputation: paths always resize from their
            # own current equity, not original dollar P&L from a growing balance.
            x=dr.to_numpy();idx=np.argsort(rng.random((10000,len(x))),axis=1)
            y=x[idx];eq=np.cumprod(1+.01*y,axis=1)
            eq=np.c_[np.ones(len(eq)),eq];dd=(1-eq/np.maximum.accumulate(eq,axis=1)).max(1)
            actual=np.r_[1,np.cumprod(1+.01*x)];actualdd=float((1-actual/np.maximum.accumulate(actual)).max())
            nb=int(np.ceil(len(x)/20));starts=rng.integers(0,len(x)-19,(10000,nb))
            ii=(starts[:,:,None]+np.arange(20)).reshape(10000,-1)[:,:len(x)]
            ee=np.c_[np.ones(10000),np.cumprod(1+.01*x[ii],axis=1)];bdd=(1-ee/np.maximum.accumulate(ee,axis=1)).max(1)
            # Alternate OHLC path is a fixed execution diagnostic, not a model.
            stress,_=replay(g,ts,hi,lo,allow,rr,path_mode=1)
            summaries[model+'_'+period]=dict(trade_permutation_mnq=perm,one_year_mnq=mc,closed_compound_dd=actualdd,compound_terminal=actual[-1],compound_shuffle_dd_quantiles=np.quantile(dd,[.5,.95,.99]).tolist(),p_shuffle_dd_ge_10=float((dd>=.1).mean()),shuffle_rank=float((dd<=actualdd).mean()),compound_block20_dd_quantiles=np.quantile(bdd,[.5,.95,.99]).tolist(),opposite_path_net=float(stress.net.sum()),opposite_path_tickets=len(stress),minute_close_marks_observed=int(np.isfinite(marks).sum()),unobserved_held_minutes=int(t.unknown_held_minutes.sum()))
            eqinfo,eqrecords=equity_audit(g,t)
            summaries[model+'_'+period]['equity_audit']=eqinfo
            eqrecords.to_csv(OUT/(model+'_'+period+'_sizing.csv'),index=False)
        # Matched eligible-day entry tests use chosen185; model restrictions
        # mean these cannot change which session/exit is selected.
        actual,_=replay(g,ts,hi,lo,allow,1.85);adr=daily(actual,ds,'net_r');ad=daily(actual,ds)
        fixed,_=replay(g,ts,hi,lo,allow,1.85,mode=1)
        delta=adr-daily(fixed,ds,'net_r')
        paired_t=float(delta.mean()/delta.std()*np.sqrt(len(delta)))
        null_r=[];null_d=[];side_r=[]
        for n in range(1000):
            start=rng.integers(541,956,g.D,dtype=np.int64)
            q,_=replay(g,ts,hi,lo,allow,1.85,mode=1,start=start)
            null_r.append(float(daily(q,ds,'net_r').sum()));null_d.append(float(q.net.sum()))
            # Same actual breakout timing; random side uses same OR-risk-sized
            # mirrored bracket. Null control, not a short strategy trial.
            if n<1000:
                sd=rng.choice([-1,1],len(actual));total=0.
                for side in [-1,1]:
                    selected=actual[sd==side];sa=np.zeros(g.D,bool);sa[selected.day.to_numpy(int)]=True
                    st=np.full(g.D,541,np.int64);st[selected.day.to_numpy(int)]=selected.j0.to_numpy(int)
                    q,_=replay(g,ts,hi,lo,sa,1.85,mode=1,start=st,side=side)
                    total+=q.net_r.sum()
                side_r.append(float(total))
        nullrows.extend(dict(period=period,run=i,random_time_total_r=null_r[i],random_time_total_dollars=null_d[i],random_side_total_r=side_r[i]) for i in range(1000))
        summaries['entry_'+period]=dict(fixed_market_delta_r_day=float(delta.mean()),paired_t=paired_t,actual_r_total=float(adr.sum()),fixed_r_total=float(daily(fixed,ds,'net_r').sum()),random_time_r_p=float((1+np.sum(np.array(null_r)>=adr.sum()))/1001),random_time_dollar_p=float((1+np.sum(np.array(null_d)>=ad.sum()))/1001),random_side_r_p=float((1+np.sum(np.array(side_r)>=adr.sum()))/1001),random_time_runs=1000,random_side_runs=1000,claim_limitation='Same eligible days; controls use OR-width risk and market entry, not absolute OR-low stop. This tests the whole entry/stop geometry, not isolated trigger causality.')
        # Filter accounting: compare all unfiltered tickets and random drops.
        base,_=replay(g,ts,hi,lo,gates['NONE']&ts.isin(ds),1.85)
        kept=base[base.day.isin(np.flatnonzero(gates[key]))];removed=base[~base.day.isin(kept.day)]
        vals=base.net.to_numpy();kr=R.max_dd(daily(kept,ds));randomtotal=[];randomdd=[]
        for n in range(1000):
            ix=np.sort(rng.choice(len(base),len(kept),replace=False));q=base.iloc[ix]
            randomtotal.append(q.net.sum());randomdd.append(R.max_dd(daily(q,ds)))
        summaries['filter_'+period]=dict(base_total=float(base.net.sum()),kept_total=float(kept.net.sum()),removed_total=float(removed.net.sum()),removed_average=float(removed.net.mean()),removed_t=float(removed.net.mean()/removed.net.std()*np.sqrt(len(removed))) if len(removed)>1 else None,p_random_profit_ge_kept=float((1+np.sum(np.array(randomtotal)>=kept.net.sum()))/1001),p_random_dd_le_kept=float((1+np.sum(np.array(randomdd)<=kr))/1001))
    pd.DataFrame(nullrows).to_csv(OUT/'null_runs.csv',index=False)
    dump('diagnostics.json',summaries)
    print(json.dumps(summaries,indent=2,default=float),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['checks','design','validation','diagnostics'],required=True);args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    {'checks':checks,'design':run_design,'validation':validate,'diagnostics':diagnostics}[args.stage]()
