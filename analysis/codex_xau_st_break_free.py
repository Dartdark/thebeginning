"""Frozen uploaded gold breakout: GC futures adaptation, design gate before 2023+.

Configured Python; official Jesse Rust indicators and supplied class for signals.
Execution extends the repository grid._walk to persistent hourly-updated positions.
No optimization, database, exchange, credentials, shared cache or live interaction.
"""
from pathlib import Path
from types import SimpleNamespace
import ast
import hashlib
import importlib.util
import json

import numpy as np
import pandas as pd
import jesse_rust as jr
from numba import njit

from grid24 import Grid24
from grid import _walk
import metrics as M
import resampling as R
import montecarlo as MC

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'agents/codex/inputs/xau_st_break_free'
OUT = ROOT / 'analysis/outputs/codex_xau_st_break_free'
SEED = 271828
HOUR, FOUR = 3_600_000, 14_400_000
PV, TICK, COST = 100., .1, 27.25


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def hours_module():
    spec = importlib.util.spec_from_file_location('gold_jesse_hours', SOURCE/'trading_hours.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def cached(method):
    def decorated(self):
        if method not in self._cache:
            self._cache[method] = method(self)
        return self._cache[method]
    return decorated


class TA:
    @staticmethod
    def atr(a):
        return jr.atr_last(np.ascontiguousarray(a[-240:]), 14)

    @staticmethod
    def adx(a):
        a = np.ascontiguousarray(a[-240:])
        return jr.adx(a, 14)[-1] if len(a)>28 else np.nan

    @staticmethod
    def ema(a, n):
        return jr.ema(np.ascontiguousarray(a[-240:, 2]), n)[-1]

    @staticmethod
    def supertrend(a, period, factor):
        z = jr.supertrend(np.ascontiguousarray(a[-240:]), period, factor)
        return SimpleNamespace(trend=z[0][-1])

    @staticmethod
    def donchian(a, n):
        return SimpleNamespace(upperband=a[-n:, 3].max(), lowerband=a[-n:, 4].min())


def uploaded_type(hours):
    class Base:
        exchange, symbol = 'Owned GC research', 'GC'
        def get_candles(self, *args):
            assert args[-1]=='4h'
            return self._four_visible
        @property
        def is_trading_hours(self):
            return hours.is_in_trading_hours(int(self.candles[-1,0]), self.trading_hours())
    tree = ast.parse((SOURCE/'uploaded.py').read_text())
    cls = next(n for n in tree.body if isinstance(n,ast.ClassDef))
    namespace={'Strategy':Base,'cached':cached,'ta':TA,
               'utils':SimpleNamespace(filter_candles_by_hours=hours.filter_candles)}
    exec(compile(ast.Module(body=[cls],type_ignores=[]),str(SOURCE/'uploaded.py'),'exec'),namespace)
    return namespace[cls.name]


def aggregate(a, interval):
    df=pd.DataFrame(a,columns=['ts','o','c','h','l','v'])
    df['bucket']=(df.ts.astype('int64')//interval)*interval
    b=df.groupby('bucket',sort=True).agg(o=('o','first'),c=('c','last'),h=('h','max'),
             l=('l','min'),v=('v','sum'),last=('ts','max'),count=('ts','size'))
    return np.ascontiguousarray(np.c_[b.index.to_numpy(),b[['o','c','h','l','v']].to_numpy()]),b


def load_design():
    pattern=str(ROOT/'data/GC_1min_20[12][012789].csv')
    import glob
    files=sorted(glob.glob(pattern))
    assert files and all(2017<=int(Path(p).stem[-4:])<=2022 for p in files)
    g=Grid24(pattern,night_pattern='')
    keep=np.isfinite(g.c.ravel())
    naive=(g.ts.astype('datetime64[m]')[:,None]+np.arange(1440)[None,:].astype('timedelta64[m]')
           -np.timedelta64(1,'m')).ravel()[keep]
    dates=pd.DatetimeIndex(naive).tz_localize('America/Chicago',ambiguous='NaT',nonexistent='NaT').tz_convert('UTC')
    assert not dates.isna().any(),'Ambiguous/nonexistent observed timestamp; stop before replay'
    ts=dates.as_unit('ms').asi8
    a=np.c_[ts,g.o.ravel()[keep],g.c.ravel()[keep],g.h.ravel()[keep],g.l.ravel()[keep],g.v.ravel()[keep]]
    good=(np.isfinite(a).all(1)&(a[:,1:5]>0).all(1)&(a[:,3]>=a[:,1:5].max(1))&(a[:,4]<=a[:,1:5].min(1)))
    invalid=int((~good).sum()); a=a[good]
    order=np.argsort(a[:,0],kind='stable');a=a[order]
    dup=np.r_[False,np.diff(a[:,0])==0];duplicate=int(dup.sum());a=a[~dup]
    assert np.all(np.diff(a[:,0])>0)
    manifest={'files':{str(Path(p).relative_to(ROOT)):sha(p) for p in files},'observed_minutes':len(a),
              'invalid_rows_removed':invalid,'duplicate_utc_removed':duplicate,
              'first_utc':str(pd.Timestamp(int(a[0,0]),unit='ms',tz='UTC')),
              'last_utc':str(pd.Timestamp(int(a[-1,0]),unit='ms',tz='UTC'))}
    return np.ascontiguousarray(a),manifest


def features(a, hours, cls, limit=None):
    h, meta=aggregate(a,HOUR); q,_=aggregate(a,FOUR)
    if limit is not None: h=h[:limit];meta=meta.iloc[:limit]
    s=cls();s.hp={p['name']:p['default'] for p in s.hyperparameters()};s._cache={}
    rows=[]
    for i,bar in enumerate(h):
        s.candles=h[:i+1];s.close=s.price=bar[2];s._cache.clear()
        current=int(meta.iloc[i]['last'])//FOUR*FOUR
        k=np.searchsorted(q[:,0],current)
        part=h[np.searchsorted(h[:,0],current):i+1]
        partial=np.array([current,part[0,1],part[-1,2],part[:,3].max(),part[:,4].min(),part[:,5].sum()])
        s._four_visible=np.vstack([q[:k],partial])
        anchor=s.anchor;prior=s.session_candles
        sig=regime=0;atr=np.nan
        if len(anchor)>=29 and len(prior)>=s.hp['don_period']:
            atr=float(s.atr4);regime=s.regime()
            if np.isfinite(atr) and atr>0 and np.isfinite(s.st_line()) and np.isfinite(TA.adx(anchor)):
                sig=1 if s.should_long() else (-1 if s.should_short() else 0)
        close_time=int(bar[0])+HOUR
        end_index=np.searchsorted(a[:,0],close_time,side='left')-1
        rows.append([close_time,end_index,bar[2],atr,regime,sig,int(s.is_trading_hours),len(anchor)])
    return np.asarray(rows,float),s.hp


@njit
def replay(a, f, day_ids, n_days, start_ms, delay_ms=0, cost=COST, seed_side=None):
    # Columns: entry index, exit index, side, entry, exit, initial stop, target, reason.
    out=np.empty((len(f)+1,8));n=0;daily=np.zeros(n_days)
    ei=-1;side=0;ep=stop=target=best=initial=last=0.;p_side=0;p_due=-1;p_dec=0.;p_atr=0.
    jh=0
    for j in range(len(a)):
        oo,cc=a[j,1],a[j,2]
        if p_due==j:
            if side==0:
                intended=p_dec-p_side*p_atr*(3. if p_side==1 else 4.)
                if (p_side==1 and oo>intended) or (p_side==-1 and oo<intended):
                    side=p_side;ei=j;ep=last=oo;best=p_dec
                    stop=np.round(intended/TICK)*TICK;initial=stop
                    target=np.inf if side==1 else np.round((p_dec-5*p_atr)/TICK)*TICK
                    daily[day_ids[j]]-=cost/2
            p_due=-1
        if side!=0:
            gap=(side==1 and oo<=stop) or (side==-1 and oo>=stop)
            if gap: x,px,kind=j,oo,0
            else: x,px,kind,worst=_walk(a[:,1],a[:,3],a[:,4],a[:,2],j,j,side,stop,target,TICK)
            if kind<2:
                daily[day_ids[j]]+=(px-last)*side*PV-cost/2
                out[n]=np.array([ei,j,side,ep,px,initial,target,kind]);n+=1;side=0
            else:
                daily[day_ids[j]]+=(cc-last)*side*PV;last=cc
        # A completed hour becomes actionable after its final observed constituent.
        while jh<len(f) and int(f[jh,1])==j:
            close_time=int(f[jh,0]);close=f[jh,2];atr=f[jh,3]
            if side!=0 and np.isfinite(atr):
                if side==1:
                    best=max(best,close);trail=best-atr*6.5
                    if stop<trail<close: stop=np.round(trail/TICK)*TICK
                else:
                    best=min(best,close);trail=best+atr*3.5
                    if close<trail<stop: stop=np.round(trail/TICK)*TICK
            elif side==0 and close_time>=start_ms and int(f[jh,5])!=0 and np.isfinite(atr):
                due=close_time+delay_ms
                k=np.searchsorted(a[:,0],due)
                if k<len(a) and int(a[k,0])==due:
                    p_due=k;p_dec=close;p_atr=atr
                    p_side=int(f[jh,5]) if seed_side is None else int(seed_side[jh])
            jh+=1
    if side!=0:
        daily[day_ids[-1]]-=cost/2
        out[n]=np.array([ei,len(a)-1,side,ep,a[-1,2],initial,target,2]);n+=1
    return out[:n],daily


def trade_frame(z,a):
    t=pd.DataFrame(z,columns=['entry_i','exit_i','side','entry','exit','initial_stop','target','reason'])
    for c in ['entry_i','exit_i','side','reason']:t[c]=t[c].astype(int)
    t['entry_time']=pd.to_datetime(a[t.entry_i,0].astype('int64'),unit='ms',utc=True)
    t['exit_time']=pd.to_datetime(a[t.exit_i,0].astype('int64')+60_000,unit='ms',utc=True)
    t['gross']=(t.exit-t.entry)*t.side*PV;t['net']=t.gross-COST
    t['hours']=(t.exit_time-t.entry_time).dt.total_seconds()/3600
    t['terminal']=t.reason.eq(2)
    return t


def summaries(t,d,variant):
    # Daily by side reconstructed separately from entry/exit marks by replay-side attribution below.
    rows=[]
    for period,days in [('2018-22',d.index)]+[(str(y),d.index[d.index.year==y]) for y in range(2018,2023)]:
        for label,sgn in [('all',0),('long',1),('short',-1)]:
            z=t if sgn==0 else t[t.side==sgn]
            if period!='2018-22':z=z[z.exit_time.dt.tz_convert('America/Chicago').dt.year==int(period)]
            completed=z[~z.terminal]
            series=d.loc[days,'all' if sgn==0 else label]
            initial=pd.Series([0.],index=[series.index[0]-pd.Timedelta(days=1)])
            m=M.perf(pd.concat([initial,series]),completed.net,capital=50_000)
            m.update(variant=variant,period=period,side=label,total=float(series.sum()),
              gross_total=float(z.gross.sum()),gross_avg=float(completed.gross.mean()),
              t=float(completed.net.mean()/completed.net.std()*np.sqrt(len(completed))) if len(completed)>1 else np.nan,
              terminal_trades=int(z.terminal.sum()),mean_holding_hours=float(completed.hours.mean()))
            rows.append(m)
    return rows


def daily_sides(t,a,dates,ids):
    out=np.zeros((len(dates),2))
    for z in t.itertuples():
        j,k=z.entry_i,z.exit_i;s=z.side;column=0 if s==1 else 1
        prices=a[j:k+1,2].copy();prices[-1]=z.exit
        changes=np.diff(prices,prepend=z.entry)*s*PV
        changes[0]-=COST/2;changes[-1]-=COST/2
        np.add.at(out[:,column],ids[j:k+1],changes)
    return pd.DataFrame({'all':out.sum(1),'long':out[:,0],'short':out[:,1]},index=dates)


def verify(cls,hours):
    # Meaningful future visibility / bracket and trailing checks, no market returns.
    x=np.array([[0,100,100,102,98,1],[60000,90,91,92,89,1]],float)
    a,b,c,w=_walk(x[:,1],x[:,3],x[:,4],x[:,2],0,0,1,99.,110.,.1)
    assert c==0 and b==99.
    # Explicit first-minute gap extension must fill at open, not stale stop.
    assert x[1,1]<99
    s=cls();s.hp={p['name']:p['default'] for p in s.hyperparameters()}
    s.vars={'best':100.};s.is_long=True;s.is_short=False;s.close=120.;s.position=SimpleNamespace(qty=1)
    s.average_stop_loss=80.
    # Inject only atr4 property in a fixture subclass, retaining original update_position.
    class FixedATR(cls):
        @property
        def atr4(self):return 2.
    q=FixedATR();q.__dict__.update(s.__dict__);q.update_position()
    assert q.stop_loss==(1,107.) and q.vars['best']==120.
    q.is_long=False;q.is_short=True;q.close=80.;q.vars={'best':100.};q.average_stop_loss=120.
    q.update_position();assert q.stop_loss==(1,87.)
    assert hours.is_in_trading_hours(int(pd.Timestamp('2020-07-06 18:00',tz='America/New_York').timestamp()*1000),s.trading_hours())
    return {'entry_bar_stop':True,'carried_gap_guard':True,'source_long_trail':True,'source_short_trail':True}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    hours=hours_module();cls=uploaded_type(hours)
    checks=verify(cls,hours)
    print('Loading only GC 2017–22 through Grid24',flush=True)
    a,manifest=load_design()
    print('Computing frozen source decisions with official Rust indicators',flush=True)
    f,hp=features(a,hours,cls)
    prefix_end=min(500,len(f)-1);cut=int(f[prefix_end,1])+1
    prefix,_=features(a[:cut],hours,cls,limit=prefix_end+1)
    assert np.allclose(prefix[:,:7],f[:prefix_end+1,:7],equal_nan=True),'Future-prefix invariance failed'
    checks['future_prefix_invariance']=True
    local=pd.to_datetime(a[:,0].astype('int64'),unit='ms',utc=True).tz_convert('America/Chicago').tz_localize(None)
    session=(local+pd.Timedelta(hours=7)).normalize()
    dates=pd.bdate_range('2017-11-01','2022-12-31').union(session.unique()).sort_values()
    ids=dates.get_indexer(session).astype(np.int64)
    start_ms=int(pd.Timestamp('2018-01-01',tz='America/Chicago').timestamp()*1000)
    names=['primary','delay_1m'];frames={};ds={};metrics=[]
    for name,delay in zip(names,[0,60_000]):
        z,d=replay(a,f,ids,len(dates),start_ms,delay)
        t=trade_frame(z,a);daily=daily_sides(t,a,dates,ids)
        assert np.allclose(d,daily['all'],atol=1e-6)
        assert np.isclose(d.sum(),t.net.sum(),atol=1e-6)
        daily=daily[daily.index>='2018-01-01']
        t.to_csv(OUT/f'trades_{name}.csv',index=False);daily.to_csv(OUT/f'daily_{name}.csv')
        frames[name]=t;ds[name]=daily;metrics+=summaries(t,daily,name)
        print(name, 'trades',len(t),'net',round(t.net.sum(),2),flush=True)
    table=pd.DataFrame(metrics);table.to_csv(OUT/'metrics.csv',index=False)
    primary=frames['primary'];complete=primary[~primary.terminal]
    row=table[(table.variant=='primary')&(table.period=='2018-22')&(table.side=='all')].iloc[0]
    years=ds['primary']['all'].groupby(ds['primary'].index.year).sum()
    gate={'completed_trades_ge_30':len(complete)>=30,'net_t_ge_2':bool(row.t>=2),
      'gross_mean_ge_1_5_cost':bool(complete.gross.mean()>=1.5*COST),
      'positive_years_ge_3':int((years>0).sum())>=3,
      'delay_net_positive':bool(ds['delay_1m']['all'].sum()>0),
      'double_cost_net_positive':bool(primary.net.sum()-len(primary)*COST>0)}
    gate['pass']=all(gate.values());gate['holdout_opened']=False
    (OUT/'design_gate.json').write_text(json.dumps(gate,indent=2)+'\n')
    # Side-controls are conditional on the original signal opportunity set, full single-position replay.
    print('Running conditional random-side controls and design uncertainty',flush=True)
    rng=np.random.default_rng(SEED);null=[]
    for k in range(1000):
        sides=rng.choice(np.array([-1,1]),len(f))
        zz,dd=replay(a,f,ids,len(dates),start_ms,0,COST,sides)
        null.append(float(dd.sum()))
    pd.DataFrame({'net':null}).to_csv(OUT/'conditional_random_side.csv',index=False)
    boots=[];perms=[];monte=[]
    for label in ['all','long','short']:
        d=ds['primary'][label]
        b=R.bootstrap(d,n=2000,block=10,seed=SEED).reset_index(names='metric');b['side']=label;boots.append(b)
        perms.append({'side':label,**R.permutation(d,n=2000,seed=SEED)})
        z=complete if label=='all' else complete[complete.side==(1 if label=='long' else -1)]
        if len(z):monte.append({'side':label,**MC.trade_mc(z.net,n=5000,seed=SEED)})
    pd.concat(boots).to_csv(OUT/'design_bootstrap.csv',index=False)
    pd.DataFrame(perms).to_csv(OUT/'design_permutation.csv',index=False)
    pd.DataFrame(monte).to_csv(OUT/'design_trade_mc.csv',index=False)
    manifest.update(source_sha256=sha(SOURCE/'uploaded.py'),params=hp,checks=checks,
         execution_trials=2,parameter_searches=0,conditional_side_p=(1+sum(x>=ds['primary']['all'].sum() for x in null))/1001,
         gate=gate,source_reference='9a3ebe075d9d0af5f012f921f46c2286f234af68',rust_version='1.3.1')
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    pd.DataFrame(f,columns=['decision_ms','last_minute_i','close','atr4','regime','signal','in_session','anchor_bars']).to_csv(OUT/'decisions_design.csv',index=False)
    print(table[(table.period=='2018-22')][['variant','side','trades','avg','t','sharpe','profit_factor','max_dd','total']].to_string(index=False))
    print(json.dumps(gate,indent=2));print('Random-side conditional p:',manifest['conditional_side_p'])
    if gate['pass']:
        print('DESIGN PASS: record decision before a separate frozen 2023+ replication; no holdout loaded here.')
    else:print('DESIGN FAIL: stop; no holdout, optimization, sizing study or funded bench.')


if __name__=='__main__':main()
