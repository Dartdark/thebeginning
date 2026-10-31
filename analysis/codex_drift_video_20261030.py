"""Frozen transcript reconstruction; shared Grid24/grid execution, no optimization.

Inventory is timestamp-only. Design/recent require a committed plan and code.
The video does not supply code; first-counterbar semantics are explicit assumptions.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, warnings
import numpy as np
import pandas as pd
from grid24 import Grid24
from grid import execute
import metrics as M
import resampling as R
from codex_s03_calendar import calendar_status
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_drift_video_20261030'
PLAN='agents/codex/plans/drift_video_20261030.md'
FEE=1.04
def dump(path,x):
    def conv(z):
        if isinstance(z,(np.integer,np.bool_)):return z.item()
        if isinstance(z,Path):return str(z)
        if isinstance(z,np.ndarray):return z.tolist()
        raise TypeError(type(z).__name__)
    Path(path).write_text(json.dumps(x,indent=2,default=conv)+'\n')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def sources(data,period):
    ys=range(2018,2023) if period=='design' else range(2023,2027)
    return [Path(data)/f'NQ_1min_{y}.csv' for y in ys]
def inventory(data,period):
    OUT.mkdir(parents=True,exist_ok=True)
    files=sources(data,period)
    raw=pd.concat([pd.read_csv(p,usecols=['date','time']) for p in files]).drop_duplicates()
    rows=[]
    for date in pd.bdate_range(f'{2018 if period=="design" else 2023}-01-01',
                               '2022-12-31' if period=='design' else '2026-10-09'):
        cal=calendar_status(date)
        if cal['kind'] in ('holiday','weekend'):continue
        x=raw[raw.date==int(date.strftime('%Y%m%d'))]
        js=set((x.time//100*60+x.time%100).astype(int))
        end=cal['cash_close_j']-5
        needed=set(range(510,end+1)) # hourly-reference08:30 through scheduled flatten
        have=len(needed&js)
        # Complete paths: an expected missing minute is unknown, never zero P&L.
        rows.append(dict(date=date.date().isoformat(),kind=cal['kind'],exit_j=end,
                         minutes=have,required=len(needed),eligible=have==len(needed)))
    frame=pd.DataFrame(rows)
    frame.to_csv(OUT/f'{period}_coverage.csv',index=False)
    result=dict(returns_computed=False,period=period,cash_sessions=len(frame),eligible=int(frame.eligible.sum()),
        coverage=float(frame.eligible.mean()),inputs=[dict(path=str(p),sha256=sha(p)) for p in files],
        assumed_trade_sd_mnq=120.,minimum_mean_for_daily_t2=2*170/np.sqrt(frame.eligible.sum()),
        power_assumption='170 dollars daily SD, illustrative; clustering/multiplicity increase hurdle')
    dump(OUT/f'{period}_inventory.json',result)
    print(json.dumps(result,indent=2))
def committed():
    subprocess.run(['git','cat-file','-e','HEAD:'+PLAN],cwd=ROOT,check=True)
    for p in [PLAN,Path(__file__).relative_to(ROOT).as_posix()]:
        subprocess.run(['git','cat-file','-e','HEAD:'+p],cwd=ROOT,check=True)
        subprocess.run(['git','diff','--exit-code','HEAD','--',p],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
def signals(g,coverage):
    b5,b15=g.bars(5),g.bars(15)
    vw=g.vwap_rows(b15,start_j=525)
    prev=np.roll(vw,1,axis=1);prev[:,0]=np.nan
    close=b15['c'];prior=np.roll(close,4,axis=1);prior[:,:4]=np.nan
    change=close/prior-1
    bias=np.where((close>vw)&(vw>prev)&(change>=.001),1,
           np.where((close<vw)&(vw<prev)&(change<=-.001),-1,0))
    color=np.sign(b5['c']-b5['o']);last=np.roll(color,1,axis=1);last[:,0]=0
    dates={pd.Timestamp(d):i for i,d in enumerate(g.ts)}
    out=[]
    for r in coverage[coverage.eligible].itertuples():
        d=dates[r.date]
        for k,j in enumerate(b5['j']):
            # First complete RTH hour known at09:30CT; last fill14:30CT.
            if not 570<=j<=min(870,r.exit_j-25):continue
            s=int(bias[d,j//15])
            if s and color[d,k]==-s and last[d,k]!=-s:
                out.append(dict(day=d,dj=int(j),side=s,stop=80.,target=40. if s>0 else 50.,exit_j=int(r.exit_j)))
    return pd.DataFrame(out,columns=['day','dj','side','stop','target','exit_j'])
def charge(t):
    t=t.copy()
    t['market_fills']=1+(t.kind!=1).astype(int)
    t['gross_mnq']=t.pnl/10
    t['fees_mnq']=FEE
    t['slippage_mnq']=.5*t.market_fills
    t['net_mnq']=t.gross_mnq-t.fees_mnq-t.slippage_mnq
    t['stress_mnq']=t.gross_mnq-1.24-t.market_fills
    t['net_nq']=t.pnl-7.25-5*t.market_fills
    return t
def replay(g,sig,total=False,loss_col='net_mnq'):
    t=charge(execute(g,sig,max_trades=4,max_losses=99,name='Drift_video'))
    keep=[]
    for _,rows in t.groupby('day'):
        losses=0
        for z in rows.itertuples():
            keep.append(z.Index)
            losses=losses+1 if getattr(z,loss_col)<0 else (losses if total else 0)
            if losses>=2:break
    return t.loc[keep].reset_index(drop=True)
def daily(t,days,col='net_mnq'):
    return t.groupby('date')[col].sum().reindex(days,fill_value=0.)
def metric(t,days,col='net_mnq'):
    d=daily(t,days,col);r=M.perf(d,t[col]);x=t[col]
    fee=1.24*len(t) if col=='stress_mnq' else float(t.fees_mnq.sum())
    slip=float(t.market_fills.sum()) if col=='stress_mnq' else float(t.slippage_mnq.sum())
    r.update(total=float(d.sum()),trade_t=float(x.mean()/x.std()*np.sqrt(len(x))),
        daily_t=float(d.mean()/d.std()*np.sqrt(len(d))),max_dd=R.max_dd(d),days=len(days),
        gross=float(t.gross_mnq.sum()),fees=fee,slippage=slip)
    return r
def run(data,period):
    committed()
    if period=='recent' and not json.loads((OUT/'design_result.json').read_text())['passed']:
        raise RuntimeError('Design failed; historical validation not earned')
    inv=json.loads((OUT/f'{period}_inventory.json').read_text())
    if inv['coverage']<.95:raise RuntimeError('Timestamp coverage gate failed')
    for x in inv['inputs']:
        if sha(x['path'])!=x['sha256']:raise RuntimeError('Input changed')
    # Isolated file pattern prevents accidental access to later prices in design.
    if set(Path(data).glob('NQ_1min_20*.csv'))!=set(sources(data,period)):
        raise RuntimeError('Use a directory containing precisely the registered period files')
    pattern=str(Path(data)/'NQ_1min_20*.csv')
    g=Grid24(pattern,night_pattern='')
    if period=='design' and pd.Timestamp(g.ts[-1]).year>2022:raise RuntimeError('Future prices in design')
    c=pd.read_csv(OUT/f'{period}_coverage.csv',parse_dates=['date'])
    days=pd.DatetimeIndex(c.loc[c.eligible,'date'])
    sig=signals(g,c);sig.to_csv(OUT/f'{period}_signals.csv',index=False)
    t=replay(g,sig);alt=replay(g,sig,total=True);st=replay(g,sig,loss_col='stress_mnq')
    t.to_csv(OUT/f'{period}_trades.csv',index=False);alt.to_csv(OUT/f'{period}_total_losses_trades.csv',index=False)
    st.to_csv(OUT/f'{period}_stress_trades.csv',index=False)
    d=pd.DataFrame({col:daily(t,days,col) for col in ['gross_mnq','fees_mnq','slippage_mnq','net_mnq','stress_mnq','net_nq']})
    d.to_csv(OUT/f'{period}_daily.csv')
    assert abs(d.net_mnq.sum()-t.net_mnq.sum())<1e-7
    rows=[]
    for name,tr in [('all',t),('long',t[t.side>0]),('short',t[t.side<0])]:
        for year in ['all']+sorted(t.date.dt.year.unique().tolist()):
            z=tr if year=='all' else tr[tr.date.dt.year==year]
            ds=days if year=='all' else days[days.year==year]
            rows.append(dict(side=name,year=year,**metric(z,ds)))
    pd.DataFrame(rows).to_csv(OUT/f'{period}_metrics.csv',index=False)
    rng=np.random.default_rng(301034);null=[]
    # One registered family per placebo,100 draws each; not100 selected strategies.
    for family in ['side','time']:
        for i in range(100):
            s=sig.copy()
            if family=='side':
                s['side']=rng.choice([-1,1],len(s));s['target']=np.where(s.side>0,40.,50.)
            else:
                # Same date and number/direction of prospective signals, uniformly
                # random allowed5m decision slots; identical caps/exits remain.
                for _,ix in s.groupby('day').groups.items():
                    end=min(870,int(s.loc[ix,'exit_j'].iloc[0])-25)
                    s.loc[ix,'dj']=np.sort(rng.choice(np.arange(570,end+1,5),len(ix),replace=False))
            z=replay(g,s)
            null.append(dict(family=family,draw=i,total=float(z.net_mnq.sum()),trades=len(z)))
        print('completed',period,family,flush=True)
    nd=pd.DataFrame(null);nd.to_csv(OUT/f'{period}_placebos.csv',index=False)
    pvals={family:float((1+(nd.loc[nd.family==family,'total']>=t.net_mnq.sum()).sum())/101) for family in ['side','time']}
    act=metric(t,days);stress=metric(st,days,'stress_mnq')
    years=t.groupby(t.date.dt.year).net_mnq.sum()
    gates=dict(at_least500_trades=len(t)>=500,positive_native_net=act['total']>0,daily_t_at_least2_5=act['daily_t']>=2.5,
        four_positive_years=int((years>0).sum())>=min(4,len(years)),stress_positive=stress['total']>0,
        side_placebo_p_le05=pvals['side']<=.05,time_placebo_p_le05=pvals['time']<=.05)
    result=dict(period=period,primary=act,total_losses=metric(alt,days),stress=stress,placebo_p=pvals,
        years=years.to_dict(),gates=gates,passed=all(gates.values()),replication='transcript reconstruction, no author code',
        accounts_tested=False,source_code_sha256=sha(__file__),prereg_commit=subprocess.check_output(['git','log','-1','--format=%H','--',PLAN],cwd=ROOT,text=True).strip())
    dump(OUT/f'{period}_result.json',result);print(json.dumps(result,indent=2))
    boot=[]
    for name,tr in [('all',t),('long',t[t.side>0]),('short',t[t.side<0])]:
        bb=R.bootstrap(daily(tr,days),n=5000,block=10,seed=301035).reset_index(names='metric');bb['side']=name;boot.append(bb)
    pd.concat(boot).to_csv(OUT/f'{period}_bootstrap.csv',index=False)
def synthetic():
    from types import SimpleNamespace
    o=np.array([[100.,100.,100.,100.,100.,100.]])
    g=SimpleNamespace(o=o,h=o.copy(),l=o.copy(),c=o.copy(),last_j=np.array([5]),ts=np.array(['2020-01-02'],dtype='datetime64[ns]'))
    g.h[0,1]=140.;g.h[0,2]=141.
    s=pd.DataFrame([dict(day=0,dj=0,side=1,stop=80.,target=40.,exit_j=5)])
    t=replay(g,s);assert t.j1.iloc[0]==2 and t.kind.iloc[0]==1
    assert abs(t.net_mnq.iloc[0]-(80-1.04-.5))<1e-9
    g.h[0,1]=180.;g.l[0,1]=0.
    z=replay(g,s);assert z.j1.iloc[0]==1
    # Clock values must be trailing, never a15m result at an earlier5m close.
    assert (574//15)==(570//15) and (585//15)==(570//15)+1
    print('synthetic_shared_engine_checks=4')
if __name__=='__main__':
    warnings.filterwarnings('ignore',category=RuntimeWarning)
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['inventory','design','recent','synthetic']);p.add_argument('--data',default=str(ROOT/'data'));p.add_argument('--period',default='design',choices=['design','recent']);a=p.parse_args()
    if a.phase=='inventory':inventory(a.data,a.period)
    elif a.phase=='synthetic':synthetic()
    else:run(a.data,a.phase)
