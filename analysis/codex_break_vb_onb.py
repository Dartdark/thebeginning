"""Frozen robustness audit: unchanged VB and evaluation ONB ADX30.

Preregistration 109a752. Five fixed stress families; no best rule selection,
account action, live access or shared-cache write. Reuses repository engines.
"""
from pathlib import Path
import glob
import hashlib
import json
import pickle
import time
import warnings

import numpy as np
import pandas as pd
from numba import njit

from grid24 import Grid24,jof
from grid import execute,_walk
from candidates24 import vault_break24,overnight_bias24,_continuous_adx,_early
from portfolio import load_mc
from param_clusters import trade_net
import metrics as M
import resampling as R

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_break_vb_onb'
SEED=8675309
VB=dict(mult=.30,atr_n=15,first=1000,last=1430,flat=1430,tp_pts=40.,sl_pts=75.,max_trades=3,early_last=1100,early_flat=1130)
ONB=dict(on_start=2300,on_end=830,or_end=845,frac=1/3,adx_n=14,adx_min=30.,atr_n=15,stop_atr=.25,rr=3.,last_entry=1400,flat=1430,early_last=1100,early_flat=1130)
REPORTS={'VB':'mc_reports/Backtesting Strategy Performance Report VB v1.xlsx',
 'ONB_ADX30':'mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx'}


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
    return h.hexdigest()


class ControlledGrid(Grid24):
    """Local, resettable memoization/controlled indicators; no disk cache."""
    def __init__(self,base,style='sma',anchor=None):
        self.__dict__.update(base.__dict__)
        self._bars={};self._atrs={};self._adxs={};self.style=style;self.anchor=anchor
    def bars(self,k):
        if k not in self._bars:self._bars[k]=Grid24.bars(self,k)
        return self._bars[k]
    def daily_atr(self,n=15):
        if n not in self._atrs:
            if self.style=='sma':self._atrs[n]=Grid24.daily_atr(self,n)
            else:
                hi=np.nanmax(self.h,axis=1);lo=np.nanmin(self.l,axis=1);has=~np.isnan(self.c).all(1)
                last=np.array([x[~np.isnan(x)][-1] if ok else np.nan for x,ok in zip(self.c,has)])
                prev=pd.Series(last).where(has).ffill().shift(1).to_numpy()
                tr=np.nanmax(np.c_[hi-lo,abs(hi-prev),abs(lo-prev)],axis=1)
                ix=np.flatnonzero(has&(pd.DatetimeIndex(self.ts).dayofweek<5))
                val=tr[ix];smooth=np.full(len(val),np.nan)
                if len(val)>=n:
                    smooth[n-1]=val[:n].mean()
                    for j in range(n,len(val)):smooth[j]=(smooth[j-1]*(n-1)+val[j])/n
                z=pd.Series(np.nan,index=range(self.D));z.iloc[ix]=smooth
                self._atrs[n]=z.shift(1).ffill().to_numpy()
        return self._atrs[n]
    def vwap_rows(self,b=None,start_j=0):
        # Anchor08:30 means the first included30m bar CLOSES09:00.
        return Grid24.vwap_rows(self,b,jof(self.anchor)+1 if self.anchor is not None else start_j)
    def adx15(self,n):
        if n not in self._adxs:self._adxs[n]=_continuous_adx(self.bars(15),n)
        return self._adxs[n]


@njit
def vb_engine(o,h,l,c,signals,maxtrades,through=1.,delay=0):
    out=np.empty((len(signals),10));n=0;lastday=-1;flat_at=-1;count=0
    for a in signals:
        d=int(a[0]);dj=int(a[1]);sp=a[2];tp=a[3];flat=int(a[4]);last=int(a[5])
        if d!=lastday:lastday=d;flat_at=-1;count=0
        if dj<flat_at or count>=maxtrades:continue
        entryj=dj+delay+1
        if entryj>flat or entryj>last or np.isnan(o[d,entryj]):continue
        ep=o[d,entryj]
        k,px,kind,worst=_walk(o[d],h[d],l[d],c[d],entryj,flat,1,ep-sp,ep+tp,through)
        out[n]=np.array([d,entryj,k,1,ep,px,kind,(px-ep)*20,abs(worst-ep)*20,1.]);n+=1
        flat_at=k;count+=1
    return out[:n]


@njit
def onb_engine(o,h,l,c,bh,bl,bo,bc,A,atr,trading,early,on_start,on_end,or_end,frac,adx_min,stop_atr,rr,
               last_entry,flat,early_last,early_flat,through=1.,delay=0):
    out=np.empty((len(trading),10));n=0
    B=bh.shape[1];H=bh.ravel();L=bl.ravel()
    i_end=on_end//15;i_or=or_end//15
    for d in trading:
        if d==0 or np.isnan(atr[d]):continue
        start=(d-1)*B+on_start//15+1;end=d*B+i_end
        onh=-np.inf;onl=np.inf
        for k in range(max(0,start),end+1):
            if np.isfinite(H[k]):onh=max(onh,H[k]);onl=min(onl,L[k])
        op=bo[d,i_end+1]
        if not(np.isfinite(onh) and np.isfinite(onl) and np.isfinite(op) and onh>onl and np.isfinite(bc[d,i_or])):continue
        position=(op-onl)/(onh-onl)
        side=1 if position>=1-frac else -1 if position<=frac else 0
        if side==0:continue
        orh=-np.inf;orl=np.inf
        for k in range(i_end+1,i_or+1):
            if np.isfinite(bh[d,k]):orh=max(orh,bh[d,k]);orl=min(orl,bl[d,k])
        level=orh if side==1 else orl
        le=early_last if early[d] else last_entry
        fl=early_flat if early[d] else flat
        sp=stop_atr*atr[d]
        for i in range(i_or+delay//15,B-1):
            decision=i-delay//15
            if i*15>=le:break
            if not(A[d,decision]>adx_min):continue
            for j in range(i*15+1,min((i+1)*15,fl)+1):
                op1=o[d,j]
                if np.isnan(op1):continue
                hit=(side==1 and h[d,j]>=level) or (side==-1 and l[d,j]<=level)
                if not hit:continue
                ep=max(op1,level) if side==1 else min(op1,level)
                k,px,kind,worst=_walk(o[d],h[d],l[d],c[d],j,fl,side,ep-side*sp,ep+side*rr*sp,through)
                out[n]=np.array([d,j,k,side,ep,px,kind,(px-ep)*side*20,abs(worst-ep)*20,1.]);n+=1
                break
            else:continue
            break
    return out[:n]


def minute(hhmm):return int(hhmm)//100*60+int(hhmm)%100
def hhmm(m):return int(m)//60*100+int(m)%60


def frame(z,g,slips=1):
    t=pd.DataFrame(z,columns=['day','j0','j1','side','entry','exit','kind','pnl','mae','qty'])
    for k in ['day','j0','j1','side','kind']:t[k]=t[k].astype(int)
    t['date']=pd.to_datetime(g.ts[t.day.to_numpy()]);t['net']=t.pnl-7.25
    # Repository baseline cost, then only the preregistered extra adverse market/stop ticks.
    t['net']=trade_net(t)-(slips-1)*5*(1+t.kind.ne(1).astype(int))
    return t


def run_strategy(g,strategy,p=None,through=1.,slips=1,delay=0):
    if strategy=='VB':
        p=VB.copy() if p is None else p.copy();s,kw=vault_break24(g,**p)
        early=_early(g);last=np.where(early,minute(p['early_last']),minute(p['last']))
        sig=np.c_[s.day,s.dj,s.stop,s.target,np.minimum(s.exit_j,g.last_j[s.day.to_numpy()]),last[s.day.to_numpy()]]
        z=vb_engine(g.o,g.h,g.l,g.c,np.ascontiguousarray(sig,float),p['max_trades'],through,delay)
    else:
        p=ONB.copy() if p is None else p.copy();b=g.bars(15)
        start=p.pop('on_start_unwrapped',minute(p['on_start']))
        z=onb_engine(g.o,g.h,g.l,g.c,b['h'],b['l'],b['o'],b['c'],g.adx15(p['adx_n']),g.daily_atr(p['atr_n']),
          g.trading,_early(g),start,minute(p['on_end']),minute(p['or_end']),p['frac'],p['adx_min'],p['stop_atr'],p['rr'],
          minute(p['last_entry']),minute(p['flat']),minute(p['early_last']),minute(p['early_flat']),through,delay)
    return frame(z,g,slips)


def original(g,strategy):
    if strategy=='VB':s,kw=vault_break24(g);t=execute(g,s,**kw)
    else:t=overnight_bias24(g,adx_min=30,stop_atr=.25)
    t['net']=trade_net(t);return t


def verify_cache(g):
    manifest={'cache_sha256':sha(ROOT/'scratch_data/g24.pkl'),'files':{},'matched_source_rows':0,
      'first_date':int(g.dates[0]),'last_date':int(g.dates[-1]),'warmup_note':'2017 overnight observations only; parity gate compares report overlap'}
    for path in sorted(glob.glob(str(ROOT/'data/NQ_1min_*.csv'))):
        name=Path(path).name
        if not(name[-8:-4].isdigit()):continue
        d=pd.read_csv(path);d=d.drop_duplicates(['date','time'])
        ix=np.searchsorted(g.dates,d.date.to_numpy());ok=(ix<g.D)&(d.date.to_numpy()>=g.dates[0])&(d.date.to_numpy()<=g.dates[-1])
        ix=ix[ok];j=jof(d.time.to_numpy()[ok])
        for col,field in [('open','o'),('high','h'),('low','l'),('close','c'),('volume','v')]:
            assert np.allclose(getattr(g,field)[ix,j],d[col].to_numpy(float)[ok],rtol=0,atol=1e-7,equal_nan=True),('cache/source mismatch',name,col)
        manifest['files'][str(Path(path).relative_to(ROOT))]=sha(path);manifest['matched_source_rows']+=int(ok.sum())
    return manifest


def parity(g,strategy,t):
    path=ROOT/REPORTS[strategy];st=pd.read_excel(path,sheet_name='Settings',header=None)
    settings=dict(zip(st[0].astype(str),st[1]))
    if strategy=='ONB_ADX30':assert float(settings['ADXMin'])==30 and float(settings['StopAtrPct'])==.25 and settings['Compression']=='15 Minutes'
    bar=30 if strategy=='VB' else 15
    assert float(settings['NumContracts'])==1
    mc=load_mc(g,path);mc['net']=trade_net(mc)
    lo=pd.Timestamp(settings['Start Date']);hi=min(pd.Timestamp(settings['End Date']),pd.Timestamp(g.ts[-1])+pd.Timedelta(days=1))
    def keyed(x):
        x=x.copy();stamp=pd.to_datetime(x.date)+pd.to_timedelta(np.ceil(x.j0/bar).astype(int)*bar,unit='m')
        x['entry_bar']=stamp;x=x[(stamp>=lo)&(stamp<=hi)]
        assert not x.duplicated(['date','side','entry_bar']).any()
        return x
    py=keyed(t);mc=keyed(mc)
    paired=py.merge(mc,on=['date','side','entry_bar'],how='outer',suffixes=('_py','_mc'),indicator=True)
    paired.to_csv(OUT/f'{strategy}_baseline_pairing.csv',index=False)
    common=paired[paired._merge=='both'];entry=(common.entry_py-common.entry_mc).abs();pnl=(common.pnl_py-common.pnl_mc).abs()
    corr=common[['pnl_py','pnl_mc']].corr().iloc[0,1]
    stats=dict(py_trades=len(py),mc_trades=len(mc),matched=len(common),entry_within_tick=float((entry<=.250001).mean()),
      gross_within20=float((pnl<=20.000001).mean()),gross_corr=float(corr),mean_net_difference=float(py.net.mean()-mc.net.mean()),
      mc_mean_net=float(mc.net.mean()),report_sha256=sha(path),start=str(lo),end=str(hi))
    checks=dict(matched_py=len(common)>=.98*len(py),matched_mc=len(common)>=.98*len(mc),entry99=stats['entry_within_tick']>=.99,
      gross95=stats['gross_within20']>=.95,correlation98=corr>=.98,
      mean_net_tolerance=abs(stats['mean_net_difference'])<=max(20,.1*abs(mc.net.mean())))
    stats['checks']={k:bool(v) for k,v in checks.items()};stats['pass']=all(checks.values());return stats


def vb_target_diagnostic(g):
    """Inspect reported exit-bar highs, without selecting a substitute fill rule."""
    raw=pd.read_excel(ROOT/REPORTS['VB'],sheet_name='List of Trades',header=2)
    ent=raw[raw.Type.astype(str).str.startswith('Entry')].reset_index(drop=True)
    ex=raw[raw.Type.astype(str).str.startswith('Exit')].reset_index(drop=True);rows=[]
    for i,r in ex.iterrows():
        if 'Profit' not in str(r.Signal) and 'Target' not in str(r.Signal):continue
        tm=pd.Timestamp(r.Date);d=np.searchsorted(g.dates,int(tm.strftime('%Y%m%d')));j=jof(tm.hour*100+tm.minute)
        if d>=g.D:continue
        high=np.nanmax(g.h[d,max(0,j-29):j+1]);target=float(r.Price)
        rows.append(dict(entry_time=str(ent.iloc[i].Date),exit_bar=str(tm),target=target,
          observed_exit_bar_high=high,above_target_points=high-target,through1_present=bool(high>=target+1)))
    pd.DataFrame(rows).to_csv(OUT/'VB_mc_target_bar_diagnostic.csv',index=False)


def metrics(t,g,strategy,run,family,parameters):
    days=pd.DatetimeIndex(g.ts[g.trading]);days=days[days.year>=2018]
    rows=[];t=t[t.date.dt.year>=2018]
    for period in ['2018-26','2018-22','2023+']+[str(y) for y in range(2018,2027)]:
        selected=days if period=='2018-26' else days[days.year<=2022] if period=='2018-22' else days[days.year>=2023] if period=='2023+' else days[days.year==int(period)]
        for side,label in [(0,'all'),(1,'long'),(-1,'short')]:
            z=t if side==0 else t[t.side==side];z=z[z.date.isin(selected)]
            daily=z.groupby('date').net.sum().reindex(selected,fill_value=0.)
            d0=pd.concat([pd.Series([0.],index=[selected[0]-pd.Timedelta(days=1)]),daily])
            m=M.perf(d0,z.net,capital=50_000);sd=z.net.std()
            m.update(strategy=strategy,run=run,family=family,period=period,side=label,total=float(z.net.sum()),
              t=float(z.net.mean()/sd*np.sqrt(len(z))) if len(z)>1 and sd>0 else np.nan,
              parameters=json.dumps(parameters,sort_keys=True))
            if len(z)==0:
                for k in ['win','avg','sharpe','sortino','profit_factor','calmar','ulcer','t']:m[k]=np.nan
            rows.append(m)
    return rows


def noise(base,sd,seed):
    rng=np.random.default_rng(seed);g=ControlledGrid(base)
    mask=np.isfinite(base.c)
    for field in ['o','h','l','c']:
        a=getattr(base,field).copy();a[mask]=np.round((a[mask]+rng.normal(0,sd*.25,int(mask.sum())))/.25)*.25
        setattr(g,field,a)
    g.h=np.maximum(g.h,np.maximum(g.o,g.c));g.l=np.minimum(g.l,np.minimum(g.o,g.c))
    assert np.array_equal(np.isfinite(g.c),mask)
    assert np.all(g.h[mask]>=np.maximum(g.o[mask],g.c[mask])) and np.all(g.l[mask]<=np.minimum(g.o[mask],g.c[mask]))
    return g


def jitter(strategy,rng):
    base=VB if strategy=='VB' else ONB;step=30 if strategy=='VB' else 15;p={};raw={}
    clock={'first','last','flat','early_last','early_flat','on_start','on_end','or_end','last_entry'}
    integers={'atr_n','adx_n','max_trades'}
    rounded=lambda value,unit:np.floor(value/unit+.5)*unit
    for k,v in base.items():
        factor=float(rng.uniform(.9,1.1));raw[k]=factor
        if k in clock:
            m=int(rounded(minute(v)*factor,step))
            if k in {'last','last_entry','flat'}:m=min(m,((15*60+59)//step)*step)
            if k in {'early_last','early_flat'}:m=min(m,(705//step)*step)
            if k=='on_start':p['on_start_unwrapped']=m;p[k]=hhmm(m%1440)
            else:p[k]=hhmm(m)
        elif k in integers:p[k]=max(1,int(rounded(v*factor,1)))
        elif k in {'tp_pts','sl_pts'}:p[k]=float(rounded(v*factor,.25))
        else:p[k]=float(rounded(v*factor,.01 if k=='rr' else .0001))
    reason=''
    if minute(p.get('first',0))>=minute(p.get('last',p.get('last_entry',1400))):reason='first_not_before_last'
    if minute(p.get('last',p.get('last_entry',1400)))>minute(p['flat']):reason='last_after_flat'
    if minute(p['early_last'])>=minute(p['early_flat']):reason='early_last_not_before_flat'
    if strategy!='VB':
        if p['on_start_unwrapped']>=1440+minute(p['on_end']):reason='overnight_start_after_end'
        if minute(p['on_end'])>=minute(p['or_end']):reason='overnight_end_not_before_or_end'
        if minute(p['or_end'])>=minute(p['last_entry']):reason='or_end_not_before_last'
    return p,raw,reason


def summarize(table):
    rows=[]
    for strategy in table.strategy.unique():
        base=table[(table.strategy==strategy)&(table.family=='baseline')&(table.side=='all')].set_index('period')
        for family in ['noise','indicators','timing','jitter','execution']:
            pieces=[]
            for period in ['2018-22','2023+']:
                x=table[(table.strategy==strategy)&(table.family==family)&(table.period==period)&(table.side=='all')]
                sr=float(base.loc[period,'sharpe']);n=len(x)
                if n==0:continue
                shares=float(((x.total>0)&(x.sharpe>=.5*sr)).mean())
                r=dict(strategy=strategy,family=family,period=period,runs=n,median_total=float(x.total.median()),
                  median_avg=float(x.avg.median()),median_t=float(x.t.median()),median_pf=float(x.profit_factor.median()),
                  median_sharpe=float(x.sharpe.median()),median_max_dd=float(x.max_dd.median()),base_sharpe=sr,
                  share_positive=float((x.total>0).mean()),share_positive_t2=float(((x.total>0)&(x.t>2)).mean()),
                  share_positive_half_sharpe=shares,bends_period=bool(sr>0 and shares>.5),
                  breaks_period=bool(x.total.median()<=0 or x.sharpe.median()<sr/3))
                pieces.append(r)
            verdict='BREAKS' if all(p['breaks_period'] for p in pieces) else 'BENDS' if all(p['bends_period'] for p in pieces) else 'MIXED / WATCH'
            for r in pieces:r['verdict']=verdict;rows.append(r)
    return pd.DataFrame(rows)


def engineering_checks():
    from types import SimpleNamespace
    shape=(2,1440);o=np.full(shape,100.);h=o+.5;l=o-.5;c=o.copy()
    signal=np.array([[1,600,10,30,870,870]],float)
    primary=vb_engine(o,h,l,c,signal,3,1.,0)
    delayed=vb_engine(o,h,l,c,signal,3,1.,30)
    assert primary[0,1]==601 and delayed[0,1]==631
    late=signal.copy();late[0,1]=840
    assert len(vb_engine(o,h,l,c,late,3,1.,30))==0
    bh=np.full((2,96),100.5);bl=np.full((2,96),90.);bo=np.full((2,96),100.);bc=bo.copy()
    bh[1,35]=101.;A=np.zeros((2,96));A[1,35]=31.;atr=np.array([np.nan,40.])
    h[1,526]=101.5;h[1,541]=101.5
    args=(o,h,l,c,bh,bl,bo,bc,A,atr,np.array([1]),np.array([False,False]),1380,510,525,1/3,30.,.25,3.,840,870,660,690)
    primary=onb_engine(*args,1.,0);delayed=onb_engine(*args,1.,15)
    assert primary[0,1]==526 and delayed[0,1]==541
    # Extended OR includes both completed bars; future bar extrema do not enter it.
    bh[1,36]=105.;A[1,36:38]=31.;h[1,556]=105.5
    args=list(args);args[14]=540
    extended=onb_engine(*args,1.,0);assert extended[0,1]==556 and extended[0,4]==105.
    bh[1,37]=999.;assert np.allclose(extended,onb_engine(*args,1.,0))
    dates=pd.bdate_range('2020-01-01',periods=40)
    fixture=SimpleNamespace(D=40,ts=dates.to_numpy(),dates=dates.strftime('%Y%m%d').astype(int).to_numpy(),
       o=np.full((40,1440),100.),h=np.full((40,1440),101.),l=np.full((40,1440),99.),c=np.full((40,1440),100.),v=np.ones((40,1440)))
    a=ControlledGrid(fixture,'wilder');old=a.daily_atr(10).copy()
    future=ControlledGrid(fixture,'wilder');future.h=future.h.copy();future.h[30]=1000.
    assert np.allclose(old[:31],future.daily_atr(10)[:31],equal_nan=True)
    assert np.isclose(old[10],2.) and future.daily_atr(10)[31]>old[31]
    ng=noise(fixture,2,123);again=noise(fixture,2,123)
    assert np.array_equal(ng.c,again.c)
    # Simultaneous jitter feasibility/clock caps are decided without returns.
    rng=np.random.default_rng(444);accepted=0
    for _ in range(1000):
        p,raw,reason=jitter('ONB_ADX30',rng)
        if reason:continue
        assert minute(p['flat'])<959 and minute(p['early_flat'])<=705
        assert p['on_start_unwrapped']<1440+minute(p['on_end'])<1440+minute(p['or_end'])
        accepted+=1
    assert accepted>0
    return dict(vb_delay30=True,onb_delay15=True,no_late_delayed_entry=True,extended_or_uses_both_bars=True,
      future_or_extrema_excluded=True,wilder_seed_and_past_only=True,noise_repeatable_and_valid=True,jitter_clock_constraints=True)


def main():
    warnings.filterwarnings('ignore',message='All-NaN slice encountered');warnings.filterwarnings('ignore',message='invalid value encountered in divide')
    OUT.mkdir(parents=True,exist_ok=True);start=time.monotonic()
    (OUT/'engineering_checks.json').write_text(json.dumps(engineering_checks(),indent=2)+'\n')
    g=ControlledGrid(pickle.load((ROOT/'scratch_data/g24.pkl').open('rb')))
    print('Checking configured cache against owned minute exports',flush=True)
    manifest=verify_cache(g);manifest['plan_commit']='109a752';manifest['strategy_robustness_trials']=2
    (OUT/'input_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    tables=[];bases={};parities={}
    for strategy in ['VB','ONB_ADX30']:
        print('Baseline',strategy,flush=True)
        official=original(g,strategy);t=run_strategy(g,strategy)
        cols=['day','j0','j1','side','entry','exit','kind','pnl','net']
        assert len(official)==len(t) and np.allclose(official[cols],t[cols],rtol=0,atol=1e-7,equal_nan=True),'Accelerated baseline differs from original'
        parities[strategy]=parity(g,strategy,t);parities[strategy]['accelerator_exact']=True
        t.to_csv(OUT/f'{strategy}_baseline_trades.csv',index=False);bases[strategy]=t
        tables+=metrics(t,g,strategy,'baseline','baseline',VB if strategy=='VB' else ONB)
        print(strategy,'parity',parities[strategy],flush=True)
    (OUT/'baseline_parity.json').write_text(json.dumps(parities,indent=2)+'\n')
    vb_target_diagnostic(g)
    active=[s for s in bases if parities[s]['pass']]
    pd.DataFrame(tables).to_csv(OUT/'run_metrics.csv',index=False)
    if not active:print('Both parity gates fail; no stress replays',flush=True);return
    def save_run(strategy,name,family,t,params):
        tables.extend(metrics(t,g,strategy,name,family,params))
    seeds=np.random.SeedSequence(SEED).spawn(4)
    noise_seeds=[int(x.generate_state(1)[0]) for x in seeds[0].spawn(100)]
    for i,seed in enumerate(noise_seeds):
        sd=1 if i<50 else 2;ng=noise(g,sd,seed)
        for strategy in active:save_run(strategy,f'noise_{sd}tick_{i%50:02}', 'noise',run_strategy(ng,strategy),dict(sd_ticks=sd,seed=seed))
        if (i+1)%10==0:print('Noise',i+1,'/100 elapsed',round(time.monotonic()-start),flush=True)
    for strategy in active:
        for n,style in [(10,'sma'),(20,'sma'),(10,'wilder'),(15,'wilder'),(20,'wilder')]:
            p=(VB if strategy=='VB' else ONB).copy();p['atr_n']=n
            save_run(strategy,f'atr_{n}_{style}','indicators',run_strategy(ControlledGrid(g,style=style),strategy,p),dict(**p,atr_style=style))
        if strategy=='VB':t=run_strategy(ControlledGrid(g,anchor=830),strategy);params=dict(vwap_anchor=830)
        else:p=ONB.copy();p['or_end']=900;t=run_strategy(g,strategy,p);params=p
        save_run(strategy,'anchor_or_swap','indicators',t,params)
        step=30 if strategy=='VB' else 15
        save_run(strategy,'entry_one_bar_later','timing',run_strategy(g,strategy,delay=step),dict(delay_minutes=step))
        for sign in [-1,1]:
            p=(VB if strategy=='VB' else ONB).copy()
            for k in ['flat','early_flat']:p[k]=hhmm(minute(p[k])+sign*step)
            save_run(strategy,'flat_earlier' if sign==-1 else 'flat_later','timing',run_strategy(g,strategy,p),p)
        rng=np.random.default_rng(seeds[1 if strategy=='VB' else 2]);draws=[];valid=0;candidate=0
        while valid<200:
            p,raw,reason=jitter(strategy,rng);draws.append(dict(candidate=candidate,accepted=not reason,reason=reason,parameters=json.dumps(p),factors=json.dumps(raw)))
            candidate+=1
            if reason:continue
            save_run(strategy,f'jitter_{valid:03}','jitter',run_strategy(g,strategy,p),p);valid+=1
            if valid%50==0:print(strategy,'jitter',valid,'/200 elapsed',round(time.monotonic()-start),flush=True)
        pd.DataFrame(draws).to_csv(OUT/f'{strategy}_jitter_draws.csv',index=False)
        for slips,through in [(2,1),(3,1),(1,2),(2,2),(3,2)]:
            save_run(strategy,f'execution_slip{slips}_through{through}','execution',run_strategy(g,strategy,slips=slips,through=through),dict(slippage_ticks=slips,target_trade_through=through))
        baseline=bases[strategy];days=pd.DatetimeIndex(g.ts[g.trading]);days=days[days.year>=2023]
        boot=[];permutation=[]
        for side,label in [(0,'all'),(1,'long'),(-1,'short')]:
            z=baseline if side==0 else baseline[baseline.side==side];z=z[z.date.dt.year>=2023]
            if z.empty:continue
            daily=z.groupby('date').net.sum().reindex(days,fill_value=0.)
            b=R.bootstrap(daily,n=2000,block=10,seed=SEED).reset_index(names='metric');b['side']=label;boot.append(b)
            permutation.append(dict(side=label,**R.permutation(daily,n=2000,seed=SEED)))
        pd.concat(boot).to_csv(OUT/f'{strategy}_baseline_bootstrap.csv',index=False)
        pd.DataFrame(permutation).to_csv(OUT/f'{strategy}_baseline_permutation.csv',index=False)
        pd.DataFrame(tables).to_csv(OUT/'run_metrics.csv',index=False)
    table=pd.DataFrame(tables);summary=summarize(table);summary.to_csv(OUT/'family_summary.csv',index=False)
    (OUT/'run_manifest.json').write_text(json.dumps(dict(master_seed=SEED,noise_seeds=noise_seeds,
      mechanical_runs=int(table[['strategy','run']].drop_duplicates().shape[0]),active_strategies=active,
      structural_fixed_fields=dict(EntryBufTicks=2,RiskPerTrade=0,NumContracts=1,
          ONB_max_trades_per_day=1,NQ_tick=.25,NQ_point_value=20,holiday_handling=True),
      elapsed_seconds=time.monotonic()-start,code_sha256=sha(__file__)),indent=2)+'\n')
    print(summary.to_string(index=False));print('Complete',round(time.monotonic()-start),'seconds',flush=True)


if __name__=='__main__':main()
