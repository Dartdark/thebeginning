"""Frozen hourly RSI/Bollinger futures diagnostic. See committed preregistration.

No Jesse project, broker, credential, shared cache or post-2022 data access.
Uses supplied class, pinned official Rust indicators and repository minute walker.
"""
from pathlib import Path
from types import SimpleNamespace
from importlib.metadata import version
import ast
import hashlib
import json
import glob

import numpy as np
import pandas as pd
import jesse_rust as jr
from numba import njit

from grid24 import Grid24
from grid import _walk
import metrics as M
import resampling as R
from codex_xau_st_break_free import aggregate, HOUR, FOUR

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_rsi_bollinger_screen'
SOURCE=ROOT/'agents/codex/inputs/MeanReversionRSI.py'
SEED=314159
SPECS={'GC':(100.,.1,27.25,.1),'NQ':(20.,.25,17.25,1.)}


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class TA:
    @staticmethod
    def atr(a): return jr.atr_last(np.ascontiguousarray(a[-240:]),14)
    @staticmethod
    def adx(a): return jr.adx(np.ascontiguousarray(a[-240:]),14)[-1]
    @staticmethod
    def rsi(a): return jr.rsi_last(np.ascontiguousarray(a[-240:,2]),14)
    @staticmethod
    def supertrend(a):
        z=jr.supertrend(np.ascontiguousarray(a[-240:]),10,3.)
        return SimpleNamespace(trend=z[0][-1])
    @staticmethod
    def bollinger_bands(a):
        u,m,l=jr.bollinger_bands_last(np.ascontiguousarray(a[-240:,2]),20,2.,2.)
        return SimpleNamespace(upperband=u,middleband=m,lowerband=l)


def source_type():
    class Base:
        exchange,symbol='Owned futures research','specified by caller'
        def get_candles(self,*args):
            assert args[-1]=='4h'
            return self._four_visible
    cls=next(n for n in ast.parse(SOURCE.read_text()).body if isinstance(n,ast.ClassDef))
    ns={'Strategy':Base,'ta':TA,'utils':SimpleNamespace(risk_to_qty=lambda *a,**k:.2)}
    exec(compile(ast.Module(body=[cls],type_ignores=[]),str(SOURCE),'exec'),ns)
    return ns[cls.name]


def load(market):
    pat=str(ROOT/f'data/{market}_1min_20[12][01289].csv')
    night=str(ROOT/'data/NQ_1min_ON_20[12][01289].csv') if market=='NQ' else ''
    files=sorted(glob.glob(pat))+(sorted(glob.glob(night)) if night else [])
    assert files and all(2018<=int(Path(p).stem[-4:])<=2022 for p in files)
    g=Grid24(pat,night_pattern=night)
    keep=np.isfinite(g.c.ravel())
    local=(g.ts.astype('datetime64[m]')[:,None]+np.arange(1440)[None,:].astype('timedelta64[m]')
           -np.timedelta64(1,'m')).ravel()[keep]
    dates=pd.DatetimeIndex(local).tz_localize('America/Chicago',ambiguous='NaT',nonexistent='NaT').tz_convert('UTC')
    assert not dates.isna().any(),'Observed ambiguous timestamp: stop'
    a=np.c_[dates.as_unit('ms').asi8,g.o.ravel()[keep],g.c.ravel()[keep],g.h.ravel()[keep],g.l.ravel()[keep],g.v.ravel()[keep]]
    good=np.isfinite(a).all(1)&(a[:,1:5]>0).all(1)&(a[:,3]>=a[:,1:5].max(1))&(a[:,4]<=a[:,1:5].min(1))
    bad=int((~good).sum());a=a[good];a=a[np.argsort(a[:,0],kind='stable')]
    dupe=np.r_[False,np.diff(a[:,0])==0];duplicates=int(dupe.sum());a=a[~dupe]
    assert np.all(np.diff(a[:,0])>0)
    return np.ascontiguousarray(a),dict(files={str(Path(p).relative_to(ROOT)):sha(p) for p in files},
       observed_minutes=len(a),invalid_removed=bad,duplicate_utc_removed=duplicates)


def features(a,cls):
    h,meta=aggregate(a,HOUR);q,_=aggregate(a,FOUR);s=cls();rows=[]
    for i,b in enumerate(h):
        current=int(b[0])//FOUR*FOUR;k=np.searchsorted(q[:,0],current)
        p=h[np.searchsorted(h[:,0],current):i+1]
        partial=np.array([current,p[0,1],p[-1,2],p[:,3].max(),p[:,4].min(),p[:,5].sum()])
        s.candles=h[max(0,i-239):i+1];s.price=b[2]
        s._four_visible=np.ascontiguousarray(np.vstack([q[max(0,k-239):k],partial]))
        valid=len(s.candles)>=240 and len(s._four_visible)>=240
        signal=0;values=[np.nan]*6
        if valid:
            values=[s.rsi_higher,s.trend,s.adx,s.adx_higher,s.bb.lowerband,s.bb.upperband]
            if np.isfinite(values).all(): signal=1 if s.should_long() else (-1 if s.should_short() else 0)
        time=int(b[0])+HOUR
        rows.append([time,np.searchsorted(a[:,0],time)-1,int(valid),signal,*values])
    return np.asarray(rows,float),h


@njit
def locate(a,start,end,side,limit,through):
    """Causal through-price event on the repository nearest-extreme OHLC path."""
    for j in range(start,end):
        o,c,h,l=a[j,1],a[j,2],a[j,3],a[j,4]
        p=np.array([o,h,l,c]) if h-o<=o-l else np.array([o,l,h,c])
        threshold=limit-side*through
        if (side==1 and o<=threshold) or (side==-1 and o>=threshold):
            return j,0,o,o,o
        hi=lo=o
        for k in range(1,4):
            if (side==1 and p[k]<=threshold and p[k-1]>threshold) or (side==-1 and p[k]>=threshold and p[k-1]<threshold):
                return j,k,threshold,max(hi,threshold),min(lo,threshold)
            hi=max(hi,p[k]);lo=min(lo,p[k])
    return -1,-1,np.nan,np.nan,np.nan


def remaining(a,j,segment,event):
    o,c,h,l=a[j,1:5]
    p=[o,h,l,c] if h-o<=o-l else [o,l,h,c]
    tail=[event]+p[segment:] if segment else p
    return np.array(tail,float)


def fill_candles(a,h,j,event,seen_hi,seen_lo):
    bucket=int(a[j,0])//HOUR*HOUR
    hi=np.searchsorted(h[:,0],bucket)
    first=np.searchsorted(a[:,0],bucket)
    prior=a[first:j]
    op=prior[0,1] if len(prior) else a[j,1]
    hh=max(seen_hi,prior[:,3].max()) if len(prior) else seen_hi
    ll=min(seen_lo,prior[:,4].min()) if len(prior) else seen_lo
    v=prior[:,5].sum() if len(prior) else 0.
    part=np.array([bucket,op,event,hh,ll,v])
    return np.ascontiguousarray(np.vstack([h[max(0,hi-239):hi],part]))


def orders(a,f,h,cls,tick,through,delay):
    # Rows: decision minute, side, limit, entry minute, stop, target, entry-path event,
    # remaining high/low/close, rejected bracket. Both sides precomputed for controls.
    out=np.full((len(f),2,11),np.nan);s=cls()
    counts=dict(signal_hours=int((f[:,3]!=0).sum()),missing_activation=0,unfilled=0,invalid_bracket=0)
    for i in np.flatnonzero(f[:,3]):
        tm=int(f[i,0]);due=tm+delay;start=np.searchsorted(a[:,0],due);end=np.searchsorted(a[:,0],tm+HOUR)
        if start==len(a) or int(a[start,0])!=due:
            counts['missing_activation']+=1;continue
        for col,side in enumerate([1,-1]):
            limit=np.round(f[i,8 if side==1 else 9]/tick)*tick
            j,seg,event,hh,ll=locate(a,start,end,side,limit,through)
            if j<0:
                if side==int(f[i,3]):counts['unfilled']+=1
                continue
            s.candles=fill_candles(a,h,j,event,hh,ll)
            s.position=SimpleNamespace(qty=1,entry_price=limit)
            s.is_long=side==1;s.is_short=side==-1
            s.on_open_position(None)
            stop=np.round(s.stop_loss[1]/tick)*tick;target=np.round(s.take_profit[1]/tick)*tick
            invalid=not(np.isfinite([stop,target]).all() and side*(limit-stop)>0 and side*(target-limit)>0)
            tail=remaining(a,j,seg,event)
            out[i,col]=[f[i,1],side,limit,j,stop,target,event,tail.max(),tail.min(),a[j,2],int(invalid)]
            if invalid:counts['invalid_bracket']+=1
    return out,counts


@njit
def carried_exit(a,start,side,stop,target,through):
    # Extend _walk at every carried open: a crossed resting target was executable
    # before a later adverse extreme in that minute. Do not reorder that gap.
    for j in range(start,len(a)):
        op=a[j,1]
        if (side==1 and op<=stop) or (side==-1 and op>=stop):return j,op,0
        if (side==1 and op>=target+through) or (side==-1 and op<=target-through):return j,target,1
        k,px,kind,worst=_walk(a[:,1],a[:,3],a[:,4],a[:,2],j,j,side,stop,target,through)
        if kind<2:return k,px,kind
    return len(a)-1,a[-1,2],2


@njit
def replay(a,f,order,through,random_sides=None):
    out=np.empty((len(f)+1,8));n=0;flat_at=-1
    for i in range(len(f)):
        if int(f[i,3])==0 or f[i,1]<flat_at:continue
        side=int(f[i,3]) if random_sides is None else int(random_sides[i])
        col=0 if side==1 else 1
        z=order[i,col]
        if np.isnan(z[3]) or z[10]!=0:continue
        j=int(z[3]);ep=z[2];stop=z[4];target=z[5]
        # First entry-minute path excludes all prices before the through-price event.
        gap=(side==1 and z[6]<=stop) or (side==-1 and z[6]>=stop)
        if gap:k,px,kind=j,z[6],0
        else:
            oo=np.array([z[6]]);hh=np.array([z[7]]);ll=np.array([z[8]]);cc=np.array([z[9]])
            k,px,kind,worst=_walk(oo,hh,ll,cc,0,0,side,stop,target,through)
            k=j
        if kind==2 and j+1<len(a):
            k,px,kind=carried_exit(a,j+1,side,stop,target,through)
        out[n]=np.array([j,k,side,ep,px,stop,target,kind]);n+=1;flat_at=k
    return out[:n]


def trade_frame(z,a,pv,cost):
    t=pd.DataFrame(z,columns=['entry_i','exit_i','side','entry','exit','stop','target','reason'])
    for c in ['entry_i','exit_i','side','reason']:t[c]=t[c].astype(int)
    t['entry_time']=pd.to_datetime(a[t.entry_i,0].astype('int64'),unit='ms',utc=True)
    t['exit_time']=pd.to_datetime(a[t.exit_i,0].astype('int64')+60_000,unit='ms',utc=True)
    t['gross']=(t.exit-t.entry)*t.side*pv;t['net']=t.gross-cost;t['terminal']=t.reason.eq(2)
    t['hours']=(t.exit_time-t.entry_time).dt.total_seconds()/3600
    return t


def daily_marks(t,a,pv,cost):
    local=pd.to_datetime(a[:,0].astype('int64'),unit='ms',utc=True).tz_convert('America/Chicago').tz_localize(None)
    sessions=(local+pd.Timedelta(hours=7)).normalize()
    dates=pd.bdate_range('2018-01-01','2022-12-31').union(sessions.unique()).sort_values()
    ids=dates.get_indexer(sessions);out=np.zeros((len(dates),2))
    for z in t.itertuples():
        j,k=z.entry_i,z.exit_i;v=a[j:k+1,2].copy();v[-1]=z.exit
        change=np.diff(v,prepend=z.entry)*z.side*pv
        change[0]-=cost/2;change[-1]-=cost/2
        np.add.at(out[:,0 if z.side==1 else 1],ids[j:k+1],change)
    d=pd.DataFrame({'all':out.sum(1),'long':out[:,0],'short':out[:,1]},index=dates)
    assert np.isclose(d['all'].sum(),t.net.sum())
    return d[d.index>='2018-01-01']


def summaries(t,d,market,variant):
    rows=[]
    for period in ['2018-22']+[str(y) for y in range(2018,2023)]:
        for label,side in [('all',0),('long',1),('short',-1)]:
            tt=t if side==0 else t[t.side==side]
            ds=d[label]
            if period!='2018-22':
                tt=tt[tt.exit_time.dt.tz_convert('America/Chicago').dt.year==int(period)]
                ds=ds[ds.index.year==int(period)]
            closed=tt[~tt.terminal]
            ds0=pd.concat([pd.Series([0.],index=[ds.index[0]-pd.Timedelta(days=1)]),ds])
            m=M.perf(ds0,closed.net,capital=50_000)
            sd=closed.net.std();n=len(closed)
            m.update(market=market,variant=variant,period=period,side=label,total=float(ds.sum()),
               gross_total=float(tt.gross.sum()),gross_avg=float(closed.gross.mean()),trade_sd=float(sd),
               t=float(closed.net.mean()/sd*np.sqrt(n)) if n>1 and sd>0 else np.nan,
               mean_holding_hours=float(closed.hours.mean()),terminal_trades=int(tt.terminal.sum()))
            rows.append(m)
    return rows


def verify(cls):
    a=np.array([[0,100,100,102,98,1],[60_000,108,100,112,94,1]],float)
    # Exact limit touch cannot fill; prior high must not count after a late long entry.
    j,seg,event,hi,lo=locate(a,0,1,1,98.,.1);assert j==-1
    j,seg,event,hi,lo=locate(a,1,2,1,95.,1.);assert j==1 and seg==2 and event==94.
    tail=remaining(a,j,seg,event);assert tail.max()==100. and tail.min()==94.
    # Entry-minute stop remains active, target before fill is excluded.
    f=np.array([[0,-1,1,1,0,0,0,0,95,110]],float)
    o=np.full((1,2,11),np.nan);o[0,0]=[-1,1,95,1,90,110,event,tail.max(),tail.min(),100,0]
    t=replay(a,f,o,1.);assert t[0,7]==2 and t[0,4]==100
    o[0,0,4]=94.5;t=replay(a,f,o,1.);assert t[0,7]==0 and t[0,4]==94.
    # Orders expire before a later-hour touch.
    j,*_=locate(a,0,1,1,95.,1.);assert j==-1
    # A stop reached AFTER the limit event must protect the entry minute.
    b=np.array([[0,100,95,102,90,1]],float)
    jj,seg,event,hh,ll=locate(b,0,1,1,98.,1.)
    tail=remaining(b,jj,seg,event)
    o[0,0]=[-1,1,98,0,94,110,event,tail.max(),tail.min(),95,0]
    t=replay(b,f,o,1.);assert t[0,7]==0 and t[0,4]==94.
    # A later opening gap exits at that opening price, not the stale stop.
    b=np.array([[0,100,100,101,97,1],[60_000,90,91,92,89,1]],float)
    o[0,0]=[-1,1,98,0,94,110,97,100,97,100,0]
    t=replay(b,f,o,1.);assert t[0,1]==1 and t[0,4]==90.
    # A resting target crossed on the open executes before any later bar low.
    b[1]=[60_000,115,100,140,90,1]
    t=replay(b,f,o,1.);assert t[0,1]==1 and t[0,4]==110. and t[0,7]==1
    class Fixture(cls):
        @property
        def atr(self):return 2.
        @property
        def bb(self):return SimpleNamespace(upperband=110.,lowerband=90.)
        @property
        def rsi_higher(self):return self.fixture_rsi
        @property
        def trend(self):return self.fixture_trend
        @property
        def adx(self):return 21.
        @property
        def adx_higher(self):return 41.
    s=Fixture();s.fixture_rsi=71.;s.fixture_trend=1
    assert s.should_long() and not s.should_short()
    s.fixture_rsi=29.;s.fixture_trend=-1;assert s.should_short() and not s.should_long()
    s.position=SimpleNamespace(qty=1,entry_price=100.);s.is_long=True;s.is_short=False
    s.on_open_position(None);assert s.stop_loss==(1,88.) and s.take_profit==(1,110.)
    s.is_long=False;s.is_short=True;s.on_open_position(None)
    assert s.stop_loss==(1,112.) and s.take_profit==(1,90.) and s.should_cancel_entry()
    return dict(source_signals=True,source_fill_brackets=True,strict_limit=True,
      pre_entry_target_excluded=True,entry_stop_active=True,gap_stop_at_open=True,
      gap_target_precedes_later_extreme=True,expiry=True)


def main():
    OUT.mkdir(parents=True,exist_ok=True);cls=source_type();checks=verify(cls)
    pd.DataFrame([dict(n=n,assumed_sd=sd,net_t2_hurdle=2*sd/np.sqrt(n))
       for n in [30,50,100] for sd in [500,1000]]).to_csv(OUT/'planning_power.csv',index=False)
    all_metrics=[];manifests={};gates={}
    for market,(pv,tick,cost,through) in SPECS.items():
        print(market,'loading design-only minute files',flush=True)
        a,manifest=load(market);f,h=features(a,cls)
        # Check a mid-sample partial 4h bucket and an exact boundary by prefix rebuilding.
        boundary=np.flatnonzero((f[:,0]%FOUR==0)&(f[:,2]==1))[10]
        for ix in [boundary,boundary+1]:
            cut=int(f[ix,1])+1;prefix,_=features(a[:cut],cls)
            assert np.allclose(prefix,f[:len(prefix)],equal_nan=True)
        checks[market+'_future_prefix']=True
        variants={};elig=[]
        for name,mult,delay in [('primary',1,0),('stress',2,60_000)]:
            order,counts=orders(a,f,h,cls,tick,through*mult,delay)
            variants[name]=order;counts.update(market=market,variant=name)
            elig.append(counts)
            assert counts['invalid_bracket']==0,'Invalid fill-time bracket: stop for specification review'
        pd.DataFrame(elig).to_csv(OUT/f'{market}_eligibility.csv',index=False)
        cols=['decision_ms','last_minute_i','warm','signal','rsi4','trend','adx1','adx4','lower','upper']
        pd.DataFrame(f,columns=cols).to_csv(OUT/f'{market}_decisions.csv',index=False)
        manifest['first_warm_decision_utc']=str(pd.Timestamp(int(f[np.flatnonzero(f[:,2])[0],0]),unit='ms',tz='UTC'))
        manifest['source_sha']=sha(SOURCE)
        (OUT/f'{market}_pre_return_audit.json').write_text(json.dumps(dict(manifest=manifest,eligibility=elig,checks=checks),indent=2)+'\n')
        print(market,'causal/eligibility checks saved; starting registered return screen',flush=True)
        tables=[];frames={};daily={}
        for name,mult in [('primary',1),('stress',2)]:
            z=replay(a,f,variants[name],through*mult)
            t=trade_frame(z,a,pv,cost);d=daily_marks(t,a,pv,cost)
            t.to_csv(OUT/f'{market}_trades_{name}.csv',index=False);d.to_csv(OUT/f'{market}_daily_{name}.csv')
            frames[name]=t;daily[name]=d;tables+=summaries(t,d,market,name)
            print(market,name,len(t),'trades net',round(t.net.sum(),2),flush=True)
        table=pd.DataFrame(tables);all_metrics+=tables
        t=frames['primary'];closed=t[~t.terminal]
        row=table[(table.variant=='primary')&(table.period=='2018-22')&(table.side=='all')].iloc[0]
        years=daily['primary']['all'].groupby(daily['primary'].index.year).sum()
        gate=dict(support_ge30=len(closed)>=30,net_t_ge2=bool(row.t>=2),
          gross_ge1_5cost=bool(closed.gross.mean()>=1.5*cost),positive_years_ge3=int((years>0).sum())>=3,
          stress_positive=bool(frames['stress'].net.sum()>0),double_cost_positive=bool(t.net.sum()-cost*len(t)>0))
        gate['pass']=all(gate.values());gate['holdout_opened']=False;gates[market]=gate
        (OUT/'design_gates.json').write_text(json.dumps(gates,indent=2)+'\n')
        rng=np.random.default_rng(SEED);control=[]
        print(market,'running 1000 conditional random-side controls',flush=True)
        for k in range(1000):
            sides=rng.choice(np.array([-1,1]),len(f))
            zz=replay(a,f,variants['primary'],through,sides)
            net=float(((zz[:,4]-zz[:,3])*zz[:,2]*pv-cost).sum())
            control.append(dict(draw=k,trades=len(zz),net=net))
        placebo=pd.DataFrame(control);placebo.to_csv(OUT/f'{market}_random_side.csv',index=False)
        manifest['conditional_side_p']=(1+int((placebo.net>=t.net.sum()).sum()))/1001
        bs=[]
        for side in ['all','long','short']:
            b=R.bootstrap(daily['primary'][side],n=2000,block=10,seed=SEED).reset_index(names='metric')
            b['side']=side;bs.append(b)
        pd.concat(bs).to_csv(OUT/f'{market}_bootstrap.csv',index=False)
        manifests[market]=manifest
        pd.DataFrame(all_metrics).to_csv(OUT/'metrics.csv',index=False)
        (OUT/'manifest.json').write_text(json.dumps(manifests,indent=2)+'\n')
    (OUT/'verification.json').write_text(json.dumps(checks,indent=2)+'\n')
    repro={'plan_commit':'d299ce1','versions':{p:version(p) for p in ['numpy','pandas','numba','jesse-rust','scipy']},
       'code_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),ROOT/'analysis/codex_xau_st_break_free.py',SOURCE]},
       'trials':4,'seed':SEED,'holdout_opened':False}
    (OUT/'reproduction.json').write_text(json.dumps(repro,indent=2)+'\n')
    print('Design gates',gates,flush=True)


if __name__=='__main__':main()
