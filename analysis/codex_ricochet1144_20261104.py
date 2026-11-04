"""Frozen uploaded Ricochet replay. Actual return work requires --commit.

Uses Grid24 and the repository minute walker. No uploaded code is executed.
Unknown held minutes and incomplete features are retained, never interpolated.
"""
from pathlib import Path
import argparse, hashlib, importlib.metadata, json, re, subprocess, warnings
import numpy as np
import pandas as pd
from numba import njit
from grid24 import Grid24
from grid import _walk
from codex_s03_v2_replay import source_calendar
import metrics as M

ROOT=Path(__file__).resolve().parents[1]
NAME='ricochet1144_20261104'
INPUT=ROOT/'agents/codex/inputs'/NAME
OUT=ROOT/'analysis/outputs'/('codex_'+NAME)
RUNTIME=ROOT/'agents/codex/runtime'/NAME
SCRIPT='analysis/codex_ricochet1144_20261104.py'
PLAN='agents/codex/plans/'+NAME+'.md'
EVIDENCE='agents/codex/evidence/'+NAME+'.md'
DEPS=['analysis/grid24.py','analysis/grid.py','analysis/metrics.py','analysis/codex_s03_v2_replay.py']
FILES=[ROOT/f'data/NQ_1min_{p}{y}.csv' for y in range(2017,2023) for p in ('','ON_')]
COLS=['entry','exit','entry_ref','entry_fill','exit_ref','exit_fill','kind','ordinal',
      'session_row','unknown_minutes','feature_missing','partial_entry_bar','carry_collision','side']

def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def dump(path,obj):
    def clean(x):
        if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
        if isinstance(x,(list,tuple)):return [clean(v) for v in x]
        if isinstance(x,(np.integer,np.bool_)):return x.item()
        if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else None
        return x
    Path(path).write_text(json.dumps(clean(obj),indent=2)+'\n')

def inventory():
    prior=json.loads((ROOT/'agents/codex/inputs/noise15_20261103/inventory.json').read_text())
    rows=[]
    for p in FILES:
        old=next(x for x in prior['inputs'] if x['path']==p.relative_to(ROOT).as_posix())
        assert digest(p)==old['sha256'],p
        rows.append(old)
    src=(INPUT/'source.txt').read_text()
    dates=[19000000+int(x) for x in re.findall(r'Feste\[\d+\]\s*=\s*(\d+)',src)]
    skipped=[19000000+int(x) for x in re.findall(r'Senza830\[\d+\]\s*=\s*(\d+)',src)]
    dump(INPUT/'inventory.json',dict(scope='hash/timestamp facts only; no strategy outcomes',inputs=rows,
         sources={p:digest(INPUT/p) for p in ['source.txt','paper.pdf','paper_text.txt']},
         dependencies={p:digest(ROOT/p) for p in DEPS},holidays=dates,hindsight_skip_dates=skipped,
         chart=dict(interval=5,timezone='America/Chicago',session='17:00–16:00 Globex',
                    continuous='unadjusted as declared by supplied code; native roll identity unverified',
                    iog=False,source_bar_magnifier=False,replay='1-minute chronological path; labeled adaptation'),
         source_count_arithmetic=dict(printed_chain_total=5867006,printed_batch_total=9900000,
                    sum_printed_chain_rows=sum([1,506538,624240,1205280,51840,91424,100])),
         versions={p:importlib.metadata.version(p) for p in ['numpy','pandas','numba','scipy']}))
    print('Inventory:12 unchanged owned design/warm-up files; zero return outcomes.')

def authorize(commit):
    assert commit and len(commit)==40,'Full committed preregistration SHA required'
    for p in [SCRIPT,PLAN,EVIDENCE]+['agents/codex/inputs/'+NAME+'/'+n for n in
                 ['source.txt','paper.pdf','paper_text.txt','inventory.json','trials.json']]:
        assert subprocess.check_output(['git','show',commit+':'+p],cwd=ROOT)==(ROOT/p).read_bytes(),p
    inv=json.loads((INPUT/'inventory.json').read_text())
    for r in inv['inputs']:assert digest(ROOT/r['path'])==r['sha256'],r['path']
    for p,sha in inv['dependencies'].items():assert digest(ROOT/p)==sha,p
    return inv

def load_data():
    folder=RUNTIME/'data';folder.mkdir(parents=True,exist_ok=True)
    for p in FILES:
        q=folder/p.name
        if not q.exists():q.symlink_to(p)
        assert q.resolve()==p.resolve()
    assert len(list(folder.glob('*.csv')))==12
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',RuntimeWarning)
        g=Grid24(str(folder/'NQ_1min_20*.csv'),str(folder/'NQ_1min_ON_20*.csv'))
        b=g.bars(5)
    observed=np.isfinite(g.c).ravel()
    pad=np.r_[np.zeros(4,dtype=bool),observed]
    pad=np.r_[pad,np.zeros((-len(pad))%5,dtype=bool)]
    count=pad.reshape(-1,5).sum(1)[:g.D*288].reshape(g.D,288)
    dates=pd.DatetimeIndex(g.ts)
    return g,b,count,dates

@njit(cache=True)
def run(o,h,l,c,bo,bh,bl,bc,count,holiday,half,sess,start,protected,mode=0,seed=1144):
    """mode0candidate;1no-reentry;2random-side;3random-time. Controls unselectable."""
    np.random.seed(seed)
    D,K=bc.shape
    buf=np.zeros((D*6,14));n=0
    p=0;ef=-1;er=0.;e=0.;ordinal=0;last_exit=-1000;barno=0
    unknown=0;dirty=0;partial=0;collision=0;prevsession=-1;cur_session=-1
    has830=False;has12=False;has15=False;hasreg=False;ro=0.;rh=0.;rl=0.;cl12=0.;cl15=0.
    regcount=0;regend=0;nreg=0;pc=0.;wa=0.;atrdirty=0;po=0.;ph=0.;pl=0.;prevdirty=0;ready=False
    red=False;s1=0.;margin=0.;active=False;ended=False
    for d in range(D):
        random_k=np.random.randint(205,253) #17:05–21:00 CT random-time control
        for k in range(K):
            if not np.isfinite(bc[d,k]):
                if p:unknown+=5
                continue
            j=k*5;idx=d*1440+j;first=max(0,idx-4);barno+=1
            sr=sess[d,k]
            # Prearmed protection operates before this bar's close decisions.
            kind=-1;xr=0.;xf=0.;xit=-1
            if p:
                for m in range(first,idx+1):
                    if not (np.isfinite(o[m]) and np.isfinite(h[m]) and np.isfinite(l[m]) and np.isfinite(c[m])):
                        unknown+=1;continue
                    stop=e-p*50.;target=e+p*100.
                    if (o[m]-stop)*p<=0:xr=o[m];kind=0
                    else:
                        _,xr,kind,_=_walk(o,h,l,c,m,m,p,stop,target,1.)
                    if kind in (0,1):
                        xf=xr-(p*.25 if kind==0 else 0.);xit=m;break
                    kind=-1
            new=sr!=cur_session
            if p and kind<0 and new:
                xr=bc[d,k];xf=xr-p*.25;xit=idx;kind=3;collision=1
            if p and kind>=0:
                buf[n]=np.array([ef,xit,er,e,xr,xf,kind,ordinal,prevsession,unknown,dirty,partial,collision,p]);n+=1
                p=0;last_exit=barno
            if new:
                if has830 and (has12 or has15) and hasreg and not holiday[cur_session]:
                    close=cl15 if has15 else cl12
                    tr=max(rh-rl,abs(rh-pc),abs(rl-pc)) if nreg else rh-rl
                    wa=wa*(13./14.)+tr/14. if nreg else tr
                    nreg+=1;pc=close;po=ro;ph=rh;pl=rl;ready=True
                    expect=390 if has15 else max(210,regend-510)
                    prevdirty=max(0,expect-regcount);atrdirty+=prevdirty
                cur_session=sr;has830=False;has12=False;has15=False;hasreg=False;regcount=0;regend=0
                ordinal=0;ended=False;last_exit=-1000
                red=ready and pc<po
                s1=2.*(ph+pl+pc)/3.-ph
                margin=.15*wa if nreg>=14 else 0.
                active=not holiday[sr]
                if idx<start:active=False
            if j==510:has830=True;ro=bc[d,k]
            if 510<j<=900:
                if not hasreg:rh=bh[d,k];rl=bl[d,k];hasreg=True
                else:rh=max(rh,bh[d,k]);rl=min(rl,bl[d,k])
                regcount+=count[d,k];regend=j
            if j==720:has12=True;cl12=bc[d,k]
            if j==900:has15=True;cl15=bc[d,k]
            # Source column rule: first clock >=15:00 up to16:30; protected known half-day11:30.
            flat=(900<=j<=990) or (protected and half[sr] and 690<=j<=990)
            if flat:
                if p:
                    xr=bc[d,k];xf=xr-p*.25
                    buf[n]=np.array([ef,idx,er,e,xr,xf,2,ordinal,prevsession,unknown,dirty,partial,collision,p]);n+=1;p=0;last_exit=barno
                ended=True
            base=(j==1025) if mode!=3 else (k==random_k)
            if base and ordinal==0 and active and red and not ended:
                p=1 if mode!=2 else (1 if np.random.randint(0,2)==1 else -1)
                ef=idx;er=bc[d,k];e=er+p*.25;ordinal=1;prevsession=sr
                unknown=0;dirty=prevdirty+atrdirty;partial=int(count[d,k]<5)
                # collision remains set for a simultaneous carry-close/new-base event.
            elif not p and ordinal>0 and ordinal<4 and mode!=1 and not ended and active and red:
                if barno>=last_exit+2 and bl[d,k]<=s1+margin and bc[d,k]>s1:
                    p=1 if mode!=2 else (1 if np.random.randint(0,2)==1 else -1)
                    ef=idx;er=bc[d,k];e=er+p*.25;ordinal+=1;prevsession=sr
                    unknown=0;dirty=prevdirty+atrdirty;partial=int(count[d,k]<5);collision=0
            if ordinal==0:collision=0
    return buf[:n],np.array([p,ef,ordinal,unknown,nreg,atrdirty])

def tstat(x):
    x=np.asarray(x);return float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))) if len(x)>1 and x.std(ddof=1)>0 else np.nan

def metrics(df,idx,value='net_nq'):
    daily=df.groupby('account_date')[value].sum().reindex(idx,fill_value=0.)
    # Initial zero must participate in drawdown; perf's other definitions are retained.
    m=M.perf(daily,df[value]);eq=np.r_[0.,daily.cumsum().to_numpy()]
    dd=float(np.max(np.maximum.accumulate(eq)-eq));m['max_dd']=dd
    m['calmar']=m['annual']/dd if dd else np.nan
    wealth=50000.+eq;peak=np.maximum.accumulate(wealth)
    m['ulcer']=float(np.sqrt(np.mean(((wealth[1:]-peak[1:])/peak[1:]*100.)**2)))
    m['ulcer_perf']=m['annual']/50000.*100./m['ulcer'] if m['ulcer'] else np.nan
    m.update(total=float(daily.sum()),daily_t=tstat(daily),trade_t=tstat(df[value]),
             gross=float(df.gross_nq.sum()),commission=float(df.commission_nq.sum()),
             slippage=float(df.slippage_nq.sum()),stress_total=float(df.stress_nq.sum()),
             breakeven_extra_per_trade=float(df[value].mean()) if len(df) else None,
             dsr=M.deflated_sharpe(daily,9900000+len(pd.read_csv(ROOT/'TRIALS.csv'))+5))
    assert np.isclose(daily.sum(),df[value].sum())
    return m,daily

def design(commit):
    inv=authorize(commit);OUT.mkdir(parents=True,exist_ok=True)
    g,b,count,dates=load_data();D=g.D
    sess=np.zeros((D,288),dtype=np.int64)
    for d in range(D):sess[d]=d+(np.arange(288)*5>990)
    ext=dates.append(pd.DatetimeIndex([dates[-1]+pd.Timedelta(days=1)]))
    hol=np.isin(ext.strftime('%Y%m%d').astype(int),inv['holidays'])
    _,half=source_calendar(ext)
    start=int(np.searchsorted(dates,pd.Timestamp('2018-02-01')))*1440
    raw=[getattr(g,x).ravel() for x in ['o','h','l','c']]
    idx=dates[g.trading];idx=idx[(idx>=pd.Timestamp('2018-02-01'))&(idx.year<=2022)]
    output={};threshold=M.t_threshold(9900000+len(pd.read_csv(ROOT/'TRIALS.csv'))+5)
    for name,protected in [('CAUSAL',False),('PROTECTED',True)]:
        arr,terminal=run(*raw,b['o'],b['h'],b['l'],b['c'],count,hol,half,sess,start,protected)
        df=pd.DataFrame(arr,columns=COLS)
        for p in ['entry','exit','kind','ordinal','session_row','unknown_minutes','feature_missing','partial_entry_bar','carry_collision']:df[p]=df[p].astype(int)
        assert (df.exit>=df.entry).all() and df.entry.is_monotonic_increasing
        assert not (df.entry.to_numpy()[1:]<df.exit.to_numpy()[:-1]).any()
        df['gross_nq']=(df.exit_ref-df.entry_ref)*df.side*20.
        df['slippage_nq']=((df.entry_fill-df.entry_ref)+(df.exit_ref-df.exit_fill))*df.side*20.
        df['commission_nq']=7.25;df['net_nq']=df.gross_nq-df.slippage_nq-df.commission_nq
        df['stress_nq']=df.net_nq-5.*(1+(df.kind!=1).astype(int))
        df['net_mnq']=(df.exit_fill-df.entry_fill)*df.side*2.-1.24
        assert np.allclose(df.net_nq,(df.exit_fill-df.entry_fill)*df.side*20.-7.25)
        df['source_session_date']=pd.to_datetime(ext[df.session_row].to_numpy())
        df['account_date']=pd.to_datetime(ext[df.exit//1440+(df.exit%1440>990).astype(int)].to_numpy())
        df['entry_time']=[str(dates[0]+pd.Timedelta(minutes=int(x))) for x in df.entry]
        df['exit_time']=[str(dates[0]+pd.Timedelta(minutes=int(x))) for x in df.exit]
        deadline=(df.entry//1440)*1440+959
        deadline=np.where(deadline<df.entry,deadline+1440,deadline)
        df['crossed_flat_deadline']=df.exit>deadline
        # Separate conditional complete-path figures; never silently delete unknown tickets.
        df['complete']=(df.unknown_minutes==0)&(df.feature_missing==0)&(df.partial_entry_bar==0)&(df.carry_collision==0)
        df.to_csv(OUT/(name.lower()+'_trades.csv'),index=False)
        known=df[df.complete].copy();m,daily=metrics(known,idx)
        diagnostic,observed=metrics(df,idx)
        daily.rename('conditional_complete_net_nq').to_csv(OUT/(name.lower()+'_daily.csv'))
        observed.rename('observed_path_diagnostic_net_nq').to_csv(OUT/(name.lower()+'_observed_daily.csv'))
        years=[]
        for y in range(2018,2023):
            a,_=metrics(known[known.account_date.dt.year==y],idx[idx.year==y]);a['year']=y;years.append(a)
        pd.DataFrame(years).to_csv(OUT/(name.lower()+'_years.csv'),index=False)
        byentry=known.groupby('ordinal').agg(trades=('net_nq','size'),net_nq=('net_nq','sum'),avg_nq=('net_nq','mean'))
        byentry.to_csv(OUT/(name.lower()+'_ordinal.csv'))
        gross_mean=float(known.gross_nq.mean()) if len(known) else -np.inf
        costs=float((known.slippage_nq+known.commission_nq).mean()) if len(known) else np.inf
        gates=dict(power=len(known)>=500,coverage=len(known)>=.995*max(1,len(df)),terminal_flat=terminal[0]==0,
                   gross_vs_cost=gross_mean>2*costs,positive=m['total']>0,daily_t=m['daily_t']>=2,
                   trade_t=m['trade_t']>=2,years=sum(x['total']>0 for x in years)>=4,stress=m['stress_total']>0,
                   multiplicity=m['daily_t']>=threshold and m['dsr']>=.95,
                   protected_deadline=(not protected) or not df.crossed_flat_deadline.any())
        output[name]=dict(complete_path=m,observed_path_diagnostic=diagnostic,closed_trades=len(df),
            complete_trades=len(known),unknown_tickets=int((df.unknown_minutes>0).sum()),
            tainted_feature_tickets=int((df.feature_missing>0).sum()),
            partial_entry_tickets=int((df.partial_entry_bar>0).sum()),carry_exit_tickets=int((df.kind==3).sum()),
            flat_deadline_tickets=int(df.crossed_flat_deadline.sum()),
            terminal=terminal.tolist(),gates=gates,advance=all(gates.values()),
            unknown_held_minutes=int(df.unknown_minutes.sum()))
    dump(OUT/'result.json',dict(program='user-upload-'+NAME,preregistration_commit=commit,
       design='2018-02-01–2022-12-31',source_fulltext_read=True,source_trade_match=False,
       new_executed_definitions=2,scout_budget_spent=0,significance_threshold=threshold,
       source_input_manifest_sha256=digest(INPUT/'inventory.json'),candidates=output,
       controls='Reserved, not run unless a candidate clears all design gates.',validation_run=False,
       account_tests_run=False,independent_verification='pending'))
    # Display-only repair after the first completed run: dump() above has already
    # converted numpy booleans/scalars. No signal, fill, gate or ledger changes.
    saved=json.loads((OUT/'result.json').read_text())
    print(json.dumps({n:{'closed':r['closed_trades'],'complete':r['complete_trades'],
        'conditional':r['complete_path'],'gates':r['gates']}
        for n,r in saved['candidates'].items()},indent=2))

def selftest():
    # Real stop gap; conservative same-minute bracket path; one-point target-through.
    a=np.array([100.,94.]);h=np.array([101.,95.]);l=np.array([99.,93.]);c=np.array([100.,94.])
    x=_walk(a,h,l,c,0,1,1,95.,110.,1.);assert x[1]==94. and x[2]==0
    a=np.array([100.]);h=np.array([110.]);l=np.array([99.]);c=np.array([105.])
    assert _walk(a,h,l,c,0,0,1,95.,110.,1.)[2]==2
    assert _walk(a,h+1,l,c,0,0,1,95.,110.,1.)[2]==1
    assert np.isclose((100.-.25-100.25)*20.-7.25,-17.25)
    assert 2*(110.+90.+100.)/3.-110.==90.
    assert sum([1,506538,624240,1205280,51840,91424,100])==2479423
    D=3;flat=np.full(D*1440,100.);hi=flat+.25;lo=flat-.25;cl=flat.copy()
    for d in range(D):cl[d*1440+510]=101.;hi[d*1440+510]=101.25
    def bars(a,what):
        x=np.r_[np.full(4,np.nan),a,np.nan].reshape(-1,5)[:D*288]
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',RuntimeWarning)
            v=np.nanmax(x,1) if what=='h' else np.nanmin(x,1) if what=='l' else x[:,-1] if what=='c' else x[:,0]
        return v.reshape(D,288)
    b=[bars(flat,'o'),bars(hi,'h'),bars(lo,'l'),bars(cl,'c')]
    count=np.full((D,288),5);ses=np.arange(D)[:,None]+(np.arange(288)[None,:]*5>990)
    hol=np.zeros(D+1,dtype=bool);half=hol.copy();half[1]=True
    normal,_=run(flat,hi,lo,cl,*b,count,hol,half,ses,0,False)
    protected,_=run(flat,hi,lo,cl,*b,count,hol,half,ses,0,True)
    assert normal[0,0]==1025 and normal[0,1]==1440+900
    assert protected[0,0]==1025 and protected[0,1]==1440+690
    hole=flat.copy();hole[1201]=np.nan
    unknown,_=run(hole,hi,lo,cl,*b,count,hol,half,ses,0,False)
    assert unknown[0,9]==1
    print('9 synthetic accounting/path/clock/missing-data checks PASS; no market outcomes.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['inventory','selftest','design']);p.add_argument('--commit')
    a=p.parse_args()
    if a.command=='inventory':inventory()
    elif a.command=='selftest':selftest()
    else:design(a.commit)
