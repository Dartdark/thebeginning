"""One frozen ES reconstruction of the user's Davey screenshot.

Use --audit before the preregistration commit; --run refuses an uncommitted plan.
No parameter search, shared cache, 2023+ read, account or live interaction.
"""
from pathlib import Path
import argparse
import glob
import hashlib
import json
import subprocess
import warnings

import numpy as np
import pandas as pd
from numba import njit

from grid24 import Grid24
from grid import _walk
from replica import is_early_close
from param_clusters import trade_net
import metrics as M
import resampling as R

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_davey_keltner'
PLAN = 'agents/codex/plans/davey_keltner_screen.md'
SEED = 530251
PV, TICK, COMMISSION = 50., .25, 5.
CONFIG = dict(market='ES', bar_minutes=30, momentum_long=20, momentum_short=20,
              channel_length=5, channel_atr=.5, threshold=50., stop_atr_length=15,
              long_stop_atr=4., short_stop_atr=1., session_start=830, session_end=1500,
              early_end=1130, quantity=1, moving_atr_stop=True, pyramiding=False)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, default=lambda x: x.item()) + '\n')


def load(end=2022):
    assert 2017 <= end <= 2022, 'Do not open 2023+ under this design-screen plan'
    paths = [ROOT / f'data/ES_1min_{y}.csv' for y in range(2017, end + 1)]
    # Grid24 accepts a glob; this expression contains exactly 2017..2022.
    pattern = str(ROOT / 'data/ES_1min_20[12][012789].csv')
    assert {str(p) for p in paths} == set(glob.glob(pattern)), 'Unexpected source years'
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        g = Grid24(pattern, night_pattern='')
    assert g.dates.max() <= 20221231
    manifest = dict(files={str(p.relative_to(ROOT)): sha(p) for p in paths},
                    first=int(g.dates.min()), last=int(g.dates.max()),
                    config=CONFIG, seed=SEED)
    # Validate the input rather than silently dropping malformed prices.
    seen = np.isfinite(g.c)
    valid = (np.isfinite(g.o) & np.isfinite(g.h) & np.isfinite(g.l) &
             (g.l <= g.o) & (g.l <= g.c) & (g.h >= g.o) & (g.h >= g.c) & (g.l > 0))
    assert valid[seen].all(), 'Malformed observed OHLC: stop'
    return g, manifest


def features(g):
    """RTH completed bars only; rolling history carries over calendar sessions."""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        b = g.bars(CONFIG['bar_minutes'])
    records = []
    for d in g.trading:
        early = is_early_close(pd.Timestamp(g.ts[d]))
        flat = 690 if early else 900
        for j in range(540, flat + 1, 30):
            present = np.isfinite(g.c[d, j-29:j+1])
            records.append((d, int(g.dates[d]), j, flat, bool(present.all()),
                            b['o'][d,j//30], b['h'][d,j//30],
                            b['l'][d,j//30], b['c'][d,j//30]))
    f = pd.DataFrame(records, columns=['day','date','j','flat','complete','o','h','l','c'])
    # A partial/missing chart bar provides no decision and is not forward-filled.
    obs = f[f.complete].copy()
    prev = obs.c.shift(1)
    tr = pd.concat([obs.h-obs.l, (obs.h-prev).abs(), (obs.l-prev).abs()], axis=1).max(axis=1)
    # The first true range has no preceding RTH close. Require a real predecessor.
    tr.iloc[0] = np.nan
    center = obs.c.rolling(5).mean()
    a5, a15 = tr.rolling(5).mean(), tr.rolling(15).mean()
    lower, upper = center - .5*a5, center + .5*a5
    rank = pd.Series(np.where(upper != lower, 100*(obs.c-lower)/(upper-lower), 0.), index=obs.index)
    momentum = obs.c - obs.c.shift(20)
    obs['atr'] = a15
    obs['rank'] = rank
    obs['momentum'] = momentum
    obs['valid'] = np.isfinite(rank) & np.isfinite(a15) & np.isfinite(momentum) & a15.gt(0)
    obs['signal'] = np.where(obs.valid & momentum.gt(0) & rank.lt(50), 1,
                             np.where(obs.valid & momentum.lt(0) & rank.gt(50), -1, 0))
    obs['exit_long'] = rank.gt(50) & obs.valid
    obs['exit_short'] = rank.lt(50) & obs.valid
    for k in ['atr','rank','momentum','valid','signal','exit_long','exit_short']:
        f[k] = obs[k].reindex(f.index)
    f['valid'] = f.valid.eq(True)
    f['signal'] = f.signal.fillna(0).astype(int)
    f[['exit_long','exit_short']] = f[['exit_long','exit_short']].eq(True)
    return f


def audit(g, manifest, f):
    rows=[]
    for y in range(2017,2023):
        z=f[f.date//10000==y]
        q=z[z.valid & (z.j < z.flat)]
        s=q[q.signal.ne(0)]
        rows.append(dict(year=y, sessions=int(z.day.nunique()), chart_bars=len(z),
                         complete_bars=int(z.complete.sum()), eligible_decisions=len(q),
                         long_opportunities=int((s.signal==1).sum()),
                         short_opportunities=int((s.signal==-1).sum()),
                         missing_activation=int(sum(not np.isfinite(g.o[r.day,r.j+1]) for r in s.itertuples())),
                         missing_scheduled_flat=int(sum(not np.isfinite(g.o[d,int(z[z.day==d].flat.iloc[0])]) for d in z.day.unique()))))
    pd.DataFrame(rows).to_csv(OUT/'pre_return_counts.csv', index=False)
    missing_flats=[]
    for d in g.trading:
        z=f[f.day==d]
        if len(z):
            flat=int(z.flat.iloc[0])
            if not np.isfinite(g.o[d,flat]):
                missing_flats.append(dict(date=int(g.dates[d]),flat=flat,
                  complete_chart_bars=int(z.complete.sum()),signal_opportunities=int(z.signal.ne(0).sum())))
    pd.DataFrame(missing_flats).to_csv(OUT/'missing_flat_audit.csv',index=False)
    decision=f[f.valid & (f.date>=20180101) & (f.j<f.flat)]
    risk=[]
    for label,factor in [('long',4.),('short',1.)]:
        vals=decision.atr*factor*PV
        risk.append(dict(side=label,decision_bar_stop_usd_p50=float(vals.median()),
                         decision_bar_stop_usd_p95=float(vals.quantile(.95)),
                         note='Nominal stop distance proxy, not trade P&L or fill risk'))
    pd.DataFrame(risk).to_csv(OUT/'pre_return_stop_risk.csv',index=False)
    f[f.date>=20180101].to_csv(OUT/'design_decisions.csv', index=False)
    first=f[f.valid].iloc[0]
    manifest.update(first_eligible=dict(date=int(first.date),close_minute=int(first.j)),
                    return_computed=False, audit_note='Signals, eligibility and counts only; no trade outcomes')
    dump(OUT/'pre_return_manifest.json',manifest)
    power=[]
    for n in [100,250,500,1000]:
        for sd in [300.,600.]:
            power.append(dict(assumed_n=n,assumed_trade_sd=sd,
                              net_mean_for_t2=2*sd/np.sqrt(n),
                              gross_mean_for_t2=30+2*sd/np.sqrt(n)))
    pd.DataFrame(power).to_csv(OUT/'planning_power.csv',index=False)
    print(pd.DataFrame(rows).to_string(index=False))


@njit
def engine(o,h,l,c,dates,day_rows,signals,atrs,exit_long,exit_short,flat_minutes):
    """Research extension: moving stop, next-open indicator exit and reversals.

    Uses grid._walk for stop traversal, with an explicit opening-gap guard.
    Array rows correspond to calendar days; 12 possible decisions 09:00..14:30.
    """
    out=np.empty((len(day_rows)*13,13))
    n=0;missing_entry=0;late_flat=0
    for d in day_rows:
        flat=flat_minutes[d]
        side=0;ep=0.;entry_j=0;decision_j=0;worst=0.;stop=0.;initial_stop=0.;widenings=0
        for k in range(12):
            j=540+k*30
            if j>=flat:break
            a=atrs[d,k]
            sig=signals[d,k]
            want_entry=side==0 or (sig!=0 and sig!=side)
            # First observed open after a decision is normally j+1. Missing
            # entry minutes cancel NEW orders. Existing exits wait for data.
            start=j+1
            if side!=0:
                oldstop=stop
                if np.isfinite(a) and a>0:
                    dist=(4. if side==1 else 1.)*a
                    stop=np.round((ep-side*dist)/.25)*.25
                    if side*(oldstop-stop)>1e-9:widenings+=1
                ex=exit_long[d,k] if side==1 else exit_short[d,k]
                reverse=sig!=0 and sig!=side
                action=ex or reverse
                first=start
                while first<min(j+31,flat) and not np.isfinite(o[d,first]):first+=1
                if first<min(j+31,flat):
                    gap=(side==1 and o[d,first]<=stop) or (side==-1 and o[d,first]>=stop)
                    if gap or action:
                        px=o[d,first]
                        worst=min(worst,px) if side==1 else max(worst,px)
                        kind=0 if gap else 3 if reverse else 2
                        out[n]=np.array([d,decision_j,entry_j,first,side,ep,px,kind,
                                          abs(worst-ep)*50,initial_stop,widenings,stop,(px-ep)*side*50]);n+=1
                        side=0
            # No pyramiding. A contrary entry can close and reverse at this open.
            if want_entry and side==0 and sig!=0 and np.isfinite(a) and a>0:
                if np.isfinite(o[d,start]):
                    side=sig;ep=o[d,start];entry_j=start;decision_j=j;worst=ep;widenings=0
                    stop=np.round((ep-side*(4. if side==1 else 1.)*a)/.25)*.25
                    initial_stop=stop
                else:missing_entry+=1
            if side!=0:
                end=min(j+30,flat-1)
                first=start
                while first<=end and not np.isfinite(o[d,first]):first+=1
                if first>end:continue
                gap=(side==1 and o[d,first]<=stop) or (side==-1 and o[d,first]>=stop)
                if gap:
                    xj=first;px=o[d,first];kind=0;wp=px
                else:
                    target=np.inf if side==1 else -np.inf
                    xj,px,kind,wp=_walk(o[d],h[d],l[d],c[d],first,end,side,stop,target,1.)
                worst=min(worst,wp) if side==1 else max(worst,wp)
                if kind==0:
                    out[n]=np.array([d,decision_j,entry_j,xj,side,ep,px,0,
                                      abs(worst-ep)*50,initial_stop,widenings,stop,(px-ep)*side*50]);n+=1
                    side=0
        if side!=0:
            # A scheduled market order at 14:59 / 11:29 CT; column is close stamp.
            xj=flat
            while xj<1440 and not np.isfinite(o[d,xj]):xj+=1
            if xj>=1440:raise ValueError('No observed same-day scheduled exit: stop research')
            if xj!=flat:late_flat+=1
            px=o[d,xj];worst=min(worst,px) if side==1 else max(worst,px)
            out[n]=np.array([d,decision_j,entry_j,xj,side,ep,px,4,
                              abs(worst-ep)*50,initial_stop,widenings,stop,(px-ep)*side*50]);n+=1
    return out[:n],missing_entry,late_flat


def arrays(g,f):
    shape=(g.D,12)
    sig=np.zeros(shape,dtype=np.int64);a=np.full(shape,np.nan)
    el=np.zeros(shape,dtype=np.bool_);es=el.copy()
    flats=np.full(g.D,900,dtype=np.int64)
    for r in f.itertuples():
        flats[r.day]=r.flat
        if r.j>=r.flat or r.j==900:continue
        k=(r.j-540)//30
        sig[r.day,k]=r.signal;a[r.day,k]=r.atr
        el[r.day,k]=r.exit_long;es[r.day,k]=r.exit_short
    days=np.array([d for d in g.trading if 20180101<=g.dates[d]<=20221231],dtype=np.int64)
    return days,sig,a,el,es,flats


def frame(z,g,slips=1):
    t=pd.DataFrame(z,columns=['day','decision_j','j0','j1','side','entry','exit','kind',
                            'mae','initial_stop','stop_widenings','final_stop','gross'])
    for k in ['day','decision_j','j0','j1','side','kind','stop_widenings']:t[k]=t[k].astype(int)
    t['date']=pd.to_datetime(g.ts[t.day.to_numpy()])
    t['qty']=1.
    t['net']=t.gross-COMMISSION
    # trade_net's hardcoded NQ tick is $5: scale ONLY its slippage debit to ES.
    slip_debit=t.net-trade_net(t)
    t['cost']=COMMISSION+slip_debit*(PV*TICK/5.)*slips
    t['net']=t.gross-t.cost
    t['minutes']=t.j1-t.j0
    return t


def daily(t,index,side=0):
    z=t if side==0 else t[t.side==side]
    return z.groupby('date').net.sum().reindex(index,fill_value=0.)


def stat(t,index):
    d=daily(t,index)
    # Prepend zero so repository perf includes loss from starting capital.
    marked=pd.concat([pd.Series([0.],index=[index[0]-pd.Timedelta(days=1)]),d])
    r=M.perf(marked,trades=t.net)
    r.update(total=float(t.net.sum()),gross_total=float(t.gross.sum()),gross_avg=float(t.gross.mean()),
             trade_sd=float(t.net.std()),t=float(t.net.mean()/t.net.std()*np.sqrt(len(t))) if len(t)>1 and t.net.std()>0 else np.nan,
             daily_t=float(d.mean()/d.std()*np.sqrt(len(d))) if len(d)>1 and d.std()>0 else np.nan,
             mean_minutes=float(t.minutes.mean()),worst_trade=float(t.net.min()) if len(t) else np.nan)
    return r


def engineering_checks():
    checks={}
    # Tiny fixtures isolate next-open fills, entry-minute protection and carried gaps.
    def fixture():
        o=np.full((1,1440),100.);h=o+.25;l=o-.25;c=o.copy()
        sig=np.zeros((1,12),dtype=np.int64);a=np.full((1,12),2.)
        el=np.zeros((1,12),dtype=np.bool_);es=el.copy()
        return o,h,l,c,sig,a,el,es
    def run(x):
        o,h,l,c,sig,a,el,es=x
        return engine(o,h,l,c,np.array([20180102]),np.array([0]),sig,a,el,es,np.array([900]))[0]
    x=fixture();x[4][0,0]=1;x[0][0,541]=101.;x[1][0,541]=101.25;x[3][0,541]=101.
    z=run(x);assert z[0,5]==101 and z[0,2]==541 and z[0,3]==900
    checks['next_open_and_scheduled_exit']=True
    x=fixture();x[4][0,0]=1;x[2][0,541]=90.
    z=run(x);assert z[0,3]==541 and z[0,6]==92 and z[0,7]==0
    checks['long_entry_minute_stop']=True
    x=fixture();x[4][0,0]=-1;x[1][0,541]=103.
    z=run(x);assert z[0,3]==541 and z[0,6]==102
    checks['short_asymmetric_stop']=True
    x=fixture();x[4][0,0]=1;x[0][0,572]=88.;x[1][0,572]=88.25;x[2][0,572]=87.75;x[3][0,572]=88.
    z=run(x);assert z[0,3]==572 and z[0,6]==88
    checks['carried_stop_gap_open']=True
    x=fixture();x[4][0,0]=1;x[5][0,1:]=3.;x[2][0,575]=90.
    z=run(x);assert z[0,3]==900 and z[0,10]>0 and z[0,11]==88
    checks['atr_stop_can_widen_only_after_decision']=True
    x=fixture();x[4][0,0]=1;x[6][0,1]=True
    z=run(x);assert z[0,3]==571 and z[0,7]==2
    checks['indicator_exit_next_open']=True
    x=fixture();x[4][0,0]=1;x[4][0,1]=-1;x[6][0,1]=True
    z=run(x);assert len(z)==2 and z[0,3]==571 and z[1,2]==571 and z[1,4]==-1
    checks['single_position_reversal']=True
    x=fixture();x[4][0,:]=1
    z=run(x);assert len(z)==1
    checks['no_pyramiding']=True
    x=fixture();x[4][0,0]=1;x[0][0,541]=np.nan
    z=run(x);assert len(z)==0
    checks['missing_entry_not_queued']=True
    x=fixture();x[4][0,0]=1
    o,h,l,c,sig,a,el,es=x
    z=engine(o,h,l,c,np.array([20180102]),np.array([0]),sig,a,el,es,np.array([690]))[0]
    assert z[0,3]==690
    checks['early_scheduled_exit']=True
    # No re-entry based on knowing that the next open will breach a stop.
    x=fixture();x[4][0,0:2]=1
    for k in [0,1,2,3]:x[k][0,571]=88.
    z=run(x);assert len(z)==1 and z[0,3]==571
    checks['no_future_gap_based_same_side_reentry']=True
    from types import SimpleNamespace
    gg=SimpleNamespace(ts=np.array(['2018-01-02'],dtype='datetime64[D]'))
    tt=frame(z,gg);ss=frame(z,gg,slips=2)
    assert np.allclose(tt.cost,30.) and np.allclose(ss.cost,55.)
    checks['ES_commission_and_slippage_scaling']=True
    return checks


def prereg_commit():
    plan=ROOT/PLAN
    committed=subprocess.check_output(['git','show','HEAD:'+PLAN],cwd=ROOT)
    assert committed==plan.read_bytes(),'Plan must be committed before any return replay'
    return subprocess.check_output(['git','log','-1','--format=%H','--',PLAN],cwd=ROOT,text=True).strip()


def main():
    p=argparse.ArgumentParser();p.add_argument('--audit',action='store_true');p.add_argument('--run',action='store_true')
    args=p.parse_args();assert args.audit != args.run
    OUT.mkdir(parents=True,exist_ok=True)
    plan_commit=prereg_commit() if args.run else None
    g,manifest=load();f=features(g)
    if args.audit:
        audit(g,manifest,f);return
    checks=engineering_checks()
    # Feature prefix invariant: prices after the prefix cannot change past decisions.
    prefix=f[f.date<=20191231].copy()
    cut=np.searchsorted(g.dates,20200101)
    import copy
    short=copy.copy(g)
    for k in ['o','h','l','c','v']:setattr(short,k,getattr(g,k)[:cut].copy())
    short.dates=g.dates[:cut];short.ts=g.ts[:cut];short.D=cut
    short.trading=g.trading[g.trading<cut]
    sf=features(short)
    pd.testing.assert_frame_equal(prefix.reset_index(drop=True),sf.reset_index(drop=True))
    checks['historical_feature_prefix_invariance']=True
    days,sig,a,el,es,flat=arrays(g,f)
    z,missing,late=engine(g.o,g.h,g.l,g.c,g.dates,days,sig,a,el,es,flat)
    t=frame(z,g);stress=frame(z,g,slips=2)
    index=pd.DatetimeIndex(g.ts[days]);rows=[]
    for name,tt in [('primary',t),('two_tick',stress)]:
        tt.to_csv(OUT/f'trades_{name}.csv',index=False)
        pd.DataFrame({s:daily(tt,index,v) for s,v in [('all',0),('long',1),('short',-1)]}).to_csv(OUT/f'daily_{name}.csv',index_label='date')
        for period,ix in [('2018-22',index)]+[(str(y),index[index.year==y]) for y in range(2018,2023)]:
            part=tt[tt.date.isin(ix)]
            for label,v in [('all',0),('long',1),('short',-1)]:
                ss=part if v==0 else part[part.side==v]
                rows.append(dict(variant=name,period=period,side=label,**stat(ss,ix)))
    pd.DataFrame(rows).to_csv(OUT/'metrics.csv',index=False)
    base=stat(t,index);stressstat=stat(stress,index)
    yearly=daily(t,index).groupby(index.year).sum()
    gates=dict(at_least_100_trades=len(t)>=100,net_trade_t_at_least_2=base['t']>=2,
               net_daily_t_at_least_2=base['daily_t']>=2,gross_mean_at_least_45=base['gross_avg']>=45,
               three_positive_years=int((yearly>0).sum())>=3,
               stress_positive=stressstat['total']>0,double_total_cost_positive=float(t.net.sum()-t.cost.sum())>0,
               no_late_flat=late==0,engineering_checks=all(checks.values()))
    gates['pass']=all(gates.values());gates['historical_replication_opened']=False
    dump(OUT/'design_gate.json',gates)
    dump(OUT/'engineering_checks.json',checks)
    # Diagnostic controls are counted and cannot rescue a failed primary gate.
    rng=np.random.default_rng(SEED)
    placebo=[]
    for i in range(1000):
        rs=sig.copy();has=rs!=0
        rs[has]=rng.choice(np.array([-1,1]),size=int(has.sum()))
        zz,mm,ll=engine(g.o,g.h,g.l,g.c,g.dates,days,rs,a,el,es,flat)
        pt=frame(zz,g)
        placebo.append(dict(run=i,trades=len(pt),net=float(pt.net.sum()),missing_entry=mm,late_flat=ll))
    pp=pd.DataFrame(placebo);pp.to_csv(OUT/'conditional_random_side.csv',index=False)
    p_side=float((1+(pp.net>=t.net.sum()).sum())/(len(pp)+1))
    gates['conditional_random_side_p_le_05']=p_side<=.05
    gates['pass']=all(v for k,v in gates.items() if k not in ['pass','historical_replication_opened'])
    dump(OUT/'design_gate.json',gates)
    boots=[];perms=[]
    for label,v in [('all',0),('long',1),('short',-1)]:
        d=daily(t,index,v)
        b=R.bootstrap(d,n=2000,block=10,seed=SEED)
        b=b.reset_index(names='metric');b.insert(0,'side',label);boots.append(b)
        per=R.permutation(d,n=2000,seed=SEED);perms.append(dict(side=label,**per))
    pd.concat(boots,ignore_index=True).to_csv(OUT/'design_bootstrap.csv',index=False)
    pd.DataFrame(perms).to_csv(OUT/'design_permutation.csv',index=False)
    counts=pd.read_csv(OUT/'pre_return_counts.csv')
    manifest.update(plan_commit=plan_commit,return_computed=True,variants=2,
                    analytic_double_cost_rescores=1,conditional_random_side_controls=1000,
                    missing_entry=missing,late_flat=late,
                    placebo_p=p_side,
                    net_if_double_total_cost=float(t.net.sum()-t.cost.sum()),
                    first_trade=str(t.date.min()),last_trade=str(t.date.max()),
                    pre_return_counts_sha256=sha(OUT/'pre_return_counts.csv'))
    dump(OUT/'manifest.json',manifest)
    import sys,importlib.metadata as md
    code=['analysis/codex_davey_keltner.py','analysis/grid24.py','analysis/grid.py',
          'analysis/replica.py','analysis/metrics.py','analysis/param_clusters.py','analysis/resampling.py',PLAN,
          'agents/codex/evidence/davey_keltner.md','agents/codex/inputs/davey_keltner/screenshot_transcription.txt',
          'agents/codex/inputs/davey_keltner/transcript.txt']
    dump(OUT/'reproduction.json',dict(python=sys.executable,
         packages={x:md.version(x) for x in ['numpy','pandas','numba','openpyxl','scipy','scikit-learn']},
         hashes={x:sha(ROOT/x) for x in code},config=CONFIG,seed=SEED))
    print(json.dumps(dict(primary=base,gates=gates,placebo_p=manifest['placebo_p']),indent=2))


if __name__=='__main__':main()
