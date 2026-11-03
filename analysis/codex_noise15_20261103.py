"""Frozen reproduction of the user's 15-minute full-Globex noise-band code.

Inventory reads timestamps/hashes only. Design outcomes require a committed plan
and exact implementation. No source strategy is imported or executed.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import json
import pickle
import subprocess
import sys
import warnings
import numpy as np
import pandas as pd
from numba import njit
from grid24 import Grid24
from grid import _walk
import metrics as M
from codex_s03_v2_replay import source_calendar

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_noise15_20261103'
INPUT=ROOT/'agents/codex/inputs/noise15_20261103'
RUNTIME=ROOT/'agents/codex/runtime/noise15_20261103'
SOURCE=INPUT/'source.txt'
PLAN='agents/codex/plans/noise15_20261103.md'
SCRIPT='analysis/codex_noise15_20261103.py'
DEPS=['analysis/grid24.py','analysis/grid.py','analysis/metrics.py','analysis/codex_s03_v2_replay.py']
FILES=[ROOT/f'data/NQ_1min_{p}{y}.csv' for y in range(2017,2023) for p in ('','ON_')]
COLS=['side','entry_flat','exit_flat','entry_reference','entry_fill','exit_reference','exit_fill',
      'kind','signal_flat','exit_signal_flat','unknown_held_minutes','entry_delay_minutes',
      'tainted_history_samples','gross_nq','slippage_nq','commission_nq','net_nq']

def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def dump(path,obj):
    def clean(x):
        if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
        if isinstance(x,(list,tuple)):return [clean(v) for v in x]
        if isinstance(x,(np.bool_,)):return bool(x)
        if isinstance(x,(np.integer,)):return int(x)
        if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else None
        return x
    Path(path).write_text(json.dumps(clean(obj),indent=2)+'\n')

def inventory():
    INPUT.mkdir(parents=True,exist_ok=True);rows=[]
    for p in FILES:
        d=pd.read_csv(p,usecols=['date','time'])
        rows.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=digest(p),rows=len(d),
                         first_date=int(d.date.min()),last_date=int(d.date.max()),
                         duplicate_timestamps=int(d.duplicated(['date','time']).sum()),
                         permission='owned_export',provenance='Existing repository MultiCharts minute exports; CT close labels. Dated native roll identity not certified.'))
    deps={p:digest(ROOT/p) for p in DEPS}
    dump(INPUT/'inventory.json',dict(scope='timestamps/hash inventory only; no returns/features',
         returns_computed=False,source_sha256=digest(SOURCE),inputs=rows,dependencies=deps,
         versions={n:importlib.metadata.version(n) for n in ['numpy','pandas','numba','scipy']},
         chart=dict(instrument='NQ',interval_minutes=15,timezone='America/Chicago',session='Full Globex, confirmed by user',
                    advertised_period=None,advertised_net=6335,advertised_pf=1.30,advertised_sharpe=3.7)))
    print('Inventory saved:12 hashed owned files; zero returns/features.')

def authorize(commit):
    if not commit or len(commit)!=40:raise ValueError('Full preregistration commit required')
    for name in [PLAN,SCRIPT,'agents/codex/evidence/noise15_20261103.md',
                 'agents/codex/inputs/noise15_20261103/source.txt',
                 'agents/codex/inputs/noise15_20261103/inventory.json',
                 'agents/codex/inputs/noise15_20261103/trials.json']:
        if subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)!=(ROOT/name).read_bytes():
            raise ValueError('Preregistered artifact changed: '+name)
    inv=json.loads((INPUT/'inventory.json').read_text())
    for row in inv['inputs']:
        if digest(ROOT/row['path'])!=row['sha256']:raise ValueError('Input changed')
    for name,sha in inv['dependencies'].items():
        if digest(ROOT/name)!=sha:raise ValueError('Dependency changed')
    return inv

def load_design():
    directory=RUNTIME/'data';directory.mkdir(parents=True,exist_ok=True)
    for p in FILES:
        q=directory/p.name
        if not q.exists():q.symlink_to(p)
        if q.resolve()!=p.resolve():raise ValueError('Unexpected design input')
    if len(list(directory.glob('*.csv')))!=len(FILES):raise ValueError('Unregistered data present')
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',RuntimeWarning)
        g=Grid24(str(directory/'NQ_1min_20*.csv'),str(directory/'NQ_1min_ON_20*.csv'))
        bars=g.bars(15)
    if pd.Timestamp(g.ts[-1]).year>2022:raise ValueError('Later outcomes forbidden at design')
    # Count actual input minutes, including the preceding date for midnight bars.
    obs=np.isfinite(g.o)&np.isfinite(g.h)&np.isfinite(g.l)&np.isfinite(g.c)
    flat=obs.ravel();pad=np.r_[np.zeros(14,dtype=bool),flat]
    pad=np.r_[pad,np.zeros((-len(pad))%15,dtype=bool)]
    counts=pad.reshape(-1,15).sum(1)[:g.D*96].reshape(g.D,96)
    return g,bars,obs,counts

@njit(cache=True)
def feature_bands(bo,bc,counts):
    """Literal date reset, EMA and per-slot insertion AFTER each decision."""
    D,K=bc.shape;upper=np.full((D,K),np.nan);lower=upper.copy();ema_out=upper.copy()
    dirty=np.zeros((D,K),np.int64);hist=np.zeros((22,100));taint=np.zeros((22,100),np.int64)
    n=np.zeros(22,np.int64);ema=np.nan;prev=np.nan;dayopen=np.nan;pc=np.nan
    anchors=np.full((D,3),np.nan)
    for d in range(D):
        first=True;anchor_dirty=0
        for k in range(K):
            close=bc[d,k]
            if not np.isfinite(close):continue
            if first:
                dayopen=bo[d,k];pc=prev;first=False
                anchors[d,0]=k*15;anchors[d,1]=dayopen;anchors[d,2]=pc
                anchor_dirty=counts[d,k]!=15 or k!=0
            ema=close if not np.isfinite(ema) else ema+2./21.*(close-ema)
            ema_out[d,k]=ema
            j=k*15
            if 540<=j<=870 and dayopen>0 and pc>0:
                slot=(j-540)//15
                if slot<22:
                    if n[slot]>=20:
                        avg=0.;bad=anchor_dirty
                        for z in range(20):avg+=hist[slot,z];bad+=taint[slot,z]
                        avg/=20.
                        upper[d,k]=max(dayopen,pc)*(1+avg)
                        lower[d,k]=min(dayopen,pc)*(1-avg)
                        dirty[d,k]=bad
                    for z in range(99,0,-1):
                        hist[slot,z]=hist[slot,z-1];taint[slot,z]=taint[slot,z-1]
                    hist[slot,0]=abs(close/dayopen-1.)
                    taint[slot,0]=int(counts[d,k]!=15 or anchor_dirty)
                    n[slot]=min(n[slot]+1,100)
            prev=close
    return upper,lower,ema_out,dirty,anchors

@njit(cache=True)
def emit(buf,n,side,ef,xf,er,e,xr,x,kind,sig,xsig,unknown,delay,tainted):
    gross=(xr-er)*side*20.;slip=(e-er)*side*20.+(xr-x)*side*20.
    buf[n,:]=np.array([float(side),float(ef),float(xf),er,e,xr,x,float(kind),float(sig),float(xsig),
                      float(unknown),float(delay),float(tainted),gross,slip,7.25,gross-slip-7.25])
    return n+1

@njit(cache=True)
def replay(o,h,l,c,bo,bc,counts,up,lo,ema,dirty,blocked,protected,start,mode,seed):
    """mode0 exact signals; mode1 random side at source opportunities;
    mode2 one random eligible clock/day and side. Controls only after design pass.
    Stops are prearmed and fill-anchored; _walk supplies the repo intraminute path.
    """
    np.random.seed(seed)
    D,K=bc.shape;buf=np.empty((100000,17));n=0;marks=np.full(D,np.nan)
    p=0;e=0.;er=0.;ef=0;sig=-1;tainted=0;unknown=0;delay=0
    pending=0;pending_side=0;pending_sig=-1;total=0;last_total=0;last_profit=0.
    trades_today=0;stops_today=0;cash=0.;started=False
    for d in range(D):
        first=True;random_k=np.random.randint(36,57)
        for k in range(K):
            if not np.isfinite(bc[d,k]):
                if p:unknown+=15
                continue
            end=d*1440+k*15
            first_min=end-14
            if first_min<0:first_min=0
            # The next existing chart bar opens at its first observed minute.
            inds0=-1
            for m in range(first_min,end+1):
                if np.isfinite(o[m]):inds0=m;break
            if inds0<0:continue
            if p:unknown+=inds0-first_min
            if pending:
                if p:
                    xr=o[inds0];x=xr-p*.25
                    if inds0>=start:n=emit(buf,n,p,ef,inds0,er,e,xr,x,2,sig,pending_sig,unknown,delay,tainted)
                    last_profit=(x-e)*p*20.;cash+=last_profit;total+=1;p=0
                if pending_side and inds0>=start:
                    p=pending_side;er=o[inds0];e=er+p*.25;ef=inds0;sig=pending_sig
                    unknown=0;delay=max(0,inds0-sig-1);tainted=dirty[sig//1440,(sig%1440)//15]
                    cash-=7.25;started=True
                pending=0;pending_side=0
            # Source built-in exits are active even outside its signal hours.
            if p:
                st=e-p*50.;target=e+p*25.
                for m in range(inds0,end+1):
                    if not (np.isfinite(o[m]) and np.isfinite(h[m]) and np.isfinite(l[m]) and np.isfinite(c[m])):
                        unknown+=1;continue
                    hitgap=(o[m]-st)*p<=0
                    if hitgap:
                        xr=o[m];kind=0
                    else:
                        _,xr,kind,_=_walk(o,h,l,c,m,m,p,st,target,1.)
                    if kind in (0,1):
                        x=xr-(p*.25 if kind==0 else 0.)
                        if m>=start:n=emit(buf,n,p,ef,m,er,e,xr,x,kind,sig,-1,unknown,delay,tainted)
                        last_profit=(x-e)*p*20.;cash+=last_profit;total+=1;p=0;break
            # Calendar Date reset is evaluated at the completed chart bar,
            # AFTER native built-in exits inside that first bar.
            if first:
                trades_today=0;stops_today=0;last_total=total;first=False
            if total>last_total:
                if last_profit*2<=-2000.:stops_today+=1
                last_total=total
            j=k*15
            allow=(not protected or not blocked[d])
            if end>=start and j<870 and np.isfinite(up[d,k]):
                ls=bc[d,k]>up[d,k] and bc[d,k]>bo[d,k]
                ss=bc[d,k]<lo[d,k] and bc[d,k]<bo[d,k]
                if mode==1 and (ls or ss):
                    ls=np.random.randint(0,2)==1;ss=not ls
                if mode==2:
                    ls=k==random_k and np.random.randint(0,2)==1
                    ss=k==random_k and not ls
                direction=1 if ls else (-1 if ss else 0)
                cap=trades_today<10 and stops_today<3
                if p==0 and j<=840 and direction and cap and allow:
                    pending=1;pending_side=direction;pending_sig=end;trades_today+=1
                elif p and j<=840 and direction==-p:
                    pending=1;pending_sig=end
                    if cap and allow:pending_side=direction;trades_today+=1
                elif p and ((p>0 and bc[d,k]<max(up[d,k],ema[d,k])) or
                            (p<0 and bc[d,k]>min(lo[d,k],ema[d,k]))):
                    pending=1;pending_side=0;pending_sig=end
            # The literal equality stays literal. Protected fallback is separate.
            if p and (j==870 or (protected and j>=870) or (protected and blocked[d] and j>=690)):
                pending=1;pending_side=0;pending_sig=end
            if started:marks[d]=cash+(bc[d,k]-e)*p*20. if p else cash
    return buf[:n],marks,np.array([float(p),e,float(ef),cash,float(pending),float(n)])

def metric(daily,trades):
    r=M.perf(daily,trades)
    def t(x):return float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))) if len(x)>1 and x.std(ddof=1)>0 else np.nan
    r.update(total=float(daily.sum()),daily_t=t(daily),trade_t=t(trades))
    return r

def design(commit):
    inv=authorize(commit);OUT.mkdir(parents=True,exist_ok=True)
    g,b,obs,counts=load_design()
    up,lo,ema,dirty,anchors=feature_bands(b['o'],b['c'],counts)
    holiday,half=source_calendar(g.ts);blocked=holiday|half
    dates=pd.DatetimeIndex(g.ts);start=int(np.searchsorted(dates,pd.Timestamp('2018-02-01')))*1440
    raw={x:getattr(g,x).ravel() for x in ('o','h','l','c')}
    results={};trading=dates[g.trading];trading=trading[(trading>=pd.Timestamp('2018-02-01'))&(trading.year<=2022)]
    audit=pd.DataFrame(dict(date=dates,anchor_bar_j=anchors[:,0],anchor_open=anchors[:,1],
                           anchor_previous_close=anchors[:,2],observed_minutes=obs.sum(1),
                           partial_chart_bars=((counts>0)&(counts<15)).sum(1),cash_calendar_blocked=blocked))
    audit.to_csv(OUT/'design_data_audit.csv',index=False)
    feature_count=int(np.isfinite(up[dates.year>=2018]).sum())
    for model,protected in [('literal_globex',False),('protected_globex',True)]:
        buf,marks,state=replay(raw['o'],raw['h'],raw['l'],raw['c'],b['o'],b['c'],counts,
            up,lo,ema,dirty,blocked,protected,start,0,3112026)
        t=pd.DataFrame(buf,columns=COLS)
        for col in ['side','entry_flat','exit_flat','kind','signal_flat','exit_signal_flat',
                    'unknown_held_minutes','entry_delay_minutes','tainted_history_samples']:t[col]=t[col].astype(int)
        t['entry_date']=dates[t.entry_flat.to_numpy()//1440].to_numpy()
        t['exit_date']=dates[t.exit_flat.to_numpy()//1440].to_numpy()
        # Closed weekend exits belong to the following weekday report. This
        # changes booking only, never a price, entry decision or exit fill.
        rd=pd.DatetimeIndex(t.exit_date)
        t['report_date']=rd+pd.to_timedelta(np.where(rd.dayofweek==6,1,np.where(rd.dayofweek==5,2,0)),unit='D')
        t['entry_j']=t.entry_flat%1440;t['exit_j']=t.exit_flat%1440
        t['cross_date']=t.entry_date!=t.exit_date
        t['path_known']=(t.unknown_held_minutes==0)&(t.entry_delay_minutes==0)
        t['net_1mnq_proxy']=t.gross_nq/10-t.slippage_nq/10-1.24
        t['stress_nq']=t.gross_nq-2*t.slippage_nq-7.25
        t.to_csv(OUT/(model+'_trades.csv'),index=False)
        # Completed-trade outcomes with unknown paths remain explicitly unknown.
        known=t[t.path_known].copy()
        day_bad=set(pd.DatetimeIndex(t.loc[~t.path_known,'entry_date']))|set(pd.DatetimeIndex(t.loc[~t.path_known,'exit_date']))
        valid_days=trading.union(pd.DatetimeIndex(known.report_date)).sort_values()
        # Calendar-date marked equity, sampled at that date's actual final chart
        # close; NOT a broker EOD mark or an executable closing fill.
        fullmarks=pd.Series(marks,index=dates)
        # Difference only consecutive OBSERVED marks. No forward-fill or
        # substitute closing fill; report remains conditional research marks.
        observed_marks=fullmarks.dropna()
        inc=observed_marks.diff();inc.iloc[0]=observed_marks.iloc[0]
        # A mark exists each active observed chart date. Never fill missing marks.
        active=inc[(inc.index>=pd.Timestamp('2018-02-01')) & inc.index.isin(trading)]
        active=active[np.isfinite(active)&(~active.index.isin(list(day_bad)))]
        # All ordinary intraday days coincide with closed-trade accounting;
        # retain separate closed-trade daily results for audit of carry trades.
        # Conditional COMPLETE-TRADE contribution, not a full-strategy daily
        # return when another trade on the same date has an unknown path.
        closed=known.groupby('report_date').net_nq.sum().reindex(valid_days,fill_value=0.)
        sides=[]
        for side,label in [(0,'both'),(1,'long'),(-1,'short')]:
            tt=known if side==0 else known[known.side==side]
            dd=tt.groupby('report_date').net_nq.sum().reindex(valid_days,fill_value=0.)
            rr=metric(dd,tt.net_nq);rr['side']=label;sides.append(rr)
        pd.DataFrame(sides).to_csv(OUT/(model+'_metrics.csv'),index=False)
        years=[]
        for y in range(2018,2023):
            tt=known[pd.DatetimeIndex(known.exit_date).year==y]
            rr=metric(closed[closed.index.year==y],tt.net_nq);rr['year']=y;years.append(rr)
        pd.DataFrame(years).to_csv(OUT/(model+'_years.csv'),index=False)
        daily=pd.DataFrame(dict(date=dates,chart_marked_equity=marks))
        daily.to_csv(OUT/(model+'_marks.csv'),index=False)
        r=sides[0];gross=float(known.gross_nq.sum());slip=float(known.slippage_nq.sum());fee=float(known.commission_nq.sum())
        assert np.isclose(gross-slip-fee,known.net_nq.sum())
        assert np.isclose(closed.sum(),known.net_nq.sum())
        gates=dict(at_least500_complete_trades=len(known)>=500,positive_net=r['total']>0,
            daily_t_ge2=r['daily_t']>=2,trade_t_ge2=r['trade_t']>=2,
            stress_positive=known.stress_nq.sum()>0,
            four_positive_years=sum(x['total']>0 for x in years)>=4,
            at_least995pct_complete_paths=len(known)>=.995*len(t),no_terminal_open_position=state[0]==0,
            no_tainted_selected_histories=bool((known.tainted_history_samples==0).all()))
        results[model]=dict(period='2018-02-01–2022-12-31',metrics=r,by_side=sides,by_year=years,
            all_closed_trades=len(t),complete_closed_trades=len(known),unknown_path_trades=int((~t.path_known).sum()),
            tainted_history_trades=int((t.tainted_history_samples>0).sum()),
            cross_date_trades=int(t.cross_date.sum()),later_than1559=int((t.cross_date|(t.exit_j>=960)).sum()),
            terminal_state=state.tolist(),gross_nq=gross,slippage_nq=slip,commission_nq=fee,
            stress_net_nq=float(known.stress_nq.sum()),one_mnq_proxy_net=float(known.net_1mnq_proxy.sum()),
            breakeven_extra_cost_per_complete_trade=float(known.net_nq.mean()),
            chart_marked_metrics=metric(active,known.net_nq),
            daily_mark_scope='Actual final observed chart close per calendar date; not broker EOD or fictitious liquidation',
            gates=gates,design_pass=all(gates.values()),historical_validation_run=False,accounts_run=False)
        print(model,json.dumps({k:results[model][k] for k in ['complete_closed_trades','unknown_path_trades','gross_nq','design_pass']}))
    dump(OUT/'design_results.json',dict(preregistration_commit=commit,source_sha256=inv['source_sha256'],
         actual_command='design --commit '+commit,script_sha256=digest(__file__),features=feature_count,models=results,
         trial_definitions_executed=['N15_LITERAL_GLOBEX','N15_PROTECTED_GLOBEX'],
         reserved_controls_not_run=['N15_RANDOM_SIDE','N15_RANDOM_TIME'],
         independent_verification='pending',scout_budget_unchanged=True))

def fixtures():
    # Only invented observations. They test real state/clock and fill semantics.
    bo=np.full((23,96),np.nan);bc=bo.copy();counts=np.zeros((23,96),np.int64)
    for d in range(23):
        bo[d,0]=100.;bc[d,0]=100.;counts[d,0]=15
        bo[d,36]=100.;bc[d,36]=101.;counts[d,36]=15
        bo[d,95]=100.;bc[d,95]=100.;counts[d,95]=15
    up,lo,ema,dirty,anchors=feature_bands(bo,bc,counts)
    assert np.isnan(up[20,36]) and np.isclose(up[21,36],101.)
    bc[21,36]=110.
    u2,*_=feature_bands(bo,bc,counts)
    assert np.isclose(u2[21,36],101.) and u2[22,36]>101.
    assert 36*15==540 and (870-540)//15+1==23 #1430 is outside22history slots
    o=np.array([100.]);h=np.array([101.]);l=np.array([99.]);c=np.array([100.])
    _,x,kind,_=_walk(o,h,l,c,0,0,1,99.5,125.,1.)
    assert kind==0 and x==99.5 # built-in stop can trigger on entry minute
    h[0]=126.;l[0]=100.
    _,x,kind,_=_walk(o,h,l,c,0,0,1,50.,125.,1.)
    assert kind==1 and x==125.
    print('PASS: five synthetic clock/history/entry-stop/target checks; no market returns.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['inventory','fixtures','design']);p.add_argument('--commit')
    a=p.parse_args()
    if a.phase=='inventory':inventory()
    elif a.phase=='fixtures':fixtures()
    else:design(a.commit)
