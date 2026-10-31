"""Preregistered, restricted market-beta screen. Never reads 2023+ prices."""
import json, hashlib, sys
from pathlib import Path
import numpy as np
import pandas as pd
import scipy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'analysis'))
import metrics
DATA=ROOT/'scratch_data/factor_sessions'
OUT=ROOT/'analysis/outputs/codex_factor_beta_sessions'
PLAN='f9f53157241d41725c93666c1930874b85be7f01'
CAP=100000.

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def serial(x): return x.item() if isinstance(x,np.generic) else str(x)
def save(name,x): (OUT/name).write_text(json.dumps(x,indent=2,default=serial)+'\n')
def hac(x,lag=20):
    x=np.asarray(x); z=x-x.mean(); n=len(x)
    var=z@z/n
    for j in range(1,min(lag,n-1)+1):var+=2*(1-j/(lag+1))*(z[j:]@z[:-j]/n)
    return float(x.mean()/np.sqrt(max(var,1e-30)/n))
def boot(x):
    rng=np.random.default_rng(4138716); x=np.asarray(x); n=len(x)
    starts=rng.integers(0,n,(2000,(n+19)//20))
    idx=((starts[:,:,None]+np.arange(20))%n).reshape(2000,-1)[:,:n]
    return np.percentile(x[idx].mean(1),[5,95]).tolist()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    expected={'prices.parquet':'e1c518c398c9ebd63b7ead13871343d2a575090513885a42db75406bd6004833',
              'membership_intervals.parquet':'1e22ffca5e15d52872912413c55e64ead85bbb835e2148f5bbaaf84f33ea7cd0'}
    for n,h in expected.items():assert sha(DATA/n)==h,(n,'snapshot changed')
    df=pd.read_parquet(DATA/'prices.parquet',filters=[('date','>=',pd.Timestamp('2017-01-01')),('date','<=',pd.Timestamp('2022-12-31'))])
    assert not df.duplicated(['date','ticker']).any()
    dates=pd.DatetimeIndex(df.loc[df.ticker=='SPY','date'].sort_values())
    names=sorted(df.ticker.unique()); ni={t:i for i,t in enumerate(names)}; di={d:i for i,d in enumerate(dates)}
    def wide(col):return df.pivot(index='date',columns='ticker',values=col).reindex(index=dates,columns=names).to_numpy(float)
    close,op,high,low,adj=[wide(n) for n in ['close','open','high','low','adj_close']]
    good=np.isfinite(op)&np.isfinite(close)&(op>0)&(close>0)&(high>=np.maximum(op,close)-.001)&(low<=np.minimum(op,close)+.001)
    nt=pd.read_csv(DATA/'no_trade_days.csv',parse_dates=['date'])
    for r in nt.itertuples():
        if r.date in di and r.ticker in ni:good[di[r.date],ni[r.ticker]]=False
    prev=np.vstack([np.full((1,len(names)),np.nan),adj[:-1]])
    total=adj/prev-1
    intra=close/op-1
    overnight=(1+total)/(1+intra)-1
    finite=np.isfinite(total)&np.isfinite(intra)&np.isfinite(overnight)
    np.testing.assert_allclose(((1+intra)*(1+overnight))[finite],(1+total)[finite],atol=1e-12)
    spy=ni['SPY']; xr=total[:,spy]
    member=np.zeros_like(good)
    mem=pd.read_parquet(DATA/'membership_intervals.parquet')
    for r in mem.itertuples():
        if r.ticker in ni:member[:,ni[r.ticker]]|=(dates>=r.start)&(dates<r.end if pd.notna(r.end) else True)
    groups={}; selections=[]; months=dates.to_period('M')
    for m in sorted(set(months)):
        first=np.flatnonzero(months==m)[0]; anchor=first-2
        if anchor<200:continue
        ix=np.arange(max(1,anchor-251),anchor+1); bx=xr[ix]
        beta=np.full(len(names),np.nan)
        for k in np.flatnonzero(member[anchor]&good[anchor-19:anchor+1].all(0)&(close[anchor]>=5)):
            y=total[ix,k]; ok=np.isfinite(y)&np.isfinite(bx)
            if ok.sum()<200:continue
            x=bx[ok]; y=y[ok]; dx=x-x.mean();den=dx@dx
            if den>0:beta[k]=(dx@(y-y.mean()))/den
        eligible=np.flatnonzero(np.isfinite(beta))
        if len(eligible)<40:continue
        order=sorted(eligible,key=lambda k:(beta[k],names[k])); lo=np.array(order[:20]); hi=np.array(order[-20:])
        groups[m]=(lo,hi,eligible,beta)
        for leg,indices in [('low',lo),('high',hi)]:
            for k in indices:selections.append(dict(month=str(m),fit_through=str(dates[anchor].date()),ticker=names[k],leg=leg,beta=beta[k]))
    pd.DataFrame(selections).to_csv(OUT/'monthly_selections.csv',index=False)
    rng=np.random.default_rng(4138715); random={}
    for m,(lo,hi,el,beta) in groups.items():
        rr=np.array([rng.choice(el,40,replace=False) for _ in range(1000)])
        random[m]=(rr[:,:20],rr[:,20:])
    rows=[]; nulls={k:[] for k in ['overnight_fractional','overnight_integer','intraday_fractional','intraday_integer']}; unresolved=[]
    for j,d in enumerate(dates):
        if d.year<2018:continue
        for mode in ['overnight','intraday']:
            mm=months[j-1] if mode=='overnight' else months[j]
            if mm not in groups:
                unresolved.append(dict(date=d,mode=mode,reason='no eligible month'));continue
            lo,hi,el,beta=groups[mm]; long,short=(hi,lo) if mode=='overnight' else (lo,hi)
            allidx=np.r_[long,short]; usable=good[j]&good[j-1]&finite[j]
            if not usable[allidx].all():
                unresolved.append(dict(date=d,mode=mode,reason='missing/untradeable selected price',tickers=','.join(names[k] for k in allidx[~usable[allidx]])));continue
            r=overnight[j] if mode=='overnight' else intra[j]
            spyret=r[spy]
            for sizing in ['fractional','integer']:
                entry=prev[j]/(adj[j]/close[j]) if mode=='overnight' else op[j]
                weights=np.full(40,.025)
                if sizing=='integer':weights=np.floor(2500/entry[allidx])*entry[allidx]/CAP
                lr=float(weights[:20]@r[long]); sr=float(-weights[20:]@r[short]);gross=lr+sr
                nominal=weights.sum(); borrowdays=(d-dates[j-1]).days if mode=='overnight' else 1
                borrow=float(weights[20:].sum()*.03*borrowdays/365)
                fee=float(nominal*.0004); stress=float(nominal*.001)
                bexp=float(weights[:20]@beta[long]-weights[20:]@beta[short])
                record=dict(date=d,mode=mode,sizing=sizing,gross=gross,net=gross-fee-borrow,stress_net=gross-stress-borrow,
                            cost=fee,borrow=borrow,gross_notional=nominal,market_beta=bexp,market_adjusted=gross-bexp*spyret,
                            long_gross=lr,short_gross=sr,long_net=lr-weights[:20].sum()*.0004,
                            short_net=sr-weights[20:].sum()*.0004-borrow,
                            eligible_long=float(np.mean(r[el[usable[el]]])))
                rows.append(record)
            # Same-calendar random-basket reference, missing null prices remain unknown.
            rlo,rhi=random[mm]; a,b=(rhi,rlo) if mode=='overnight' else (rlo,rhi)
            ok=usable[a].all(1)&usable[b].all(1)
            entry=prev[j]/(adj[j]/close[j]) if mode=='overnight' else op[j]
            for sizing in ['fractional','integer']:
                wa=np.full(a.shape,.025);wb=np.full(b.shape,.025)
                if sizing=='integer':
                    wa=np.floor(2500/entry[a])*entry[a]/CAP;wb=np.floor(2500/entry[b])*entry[b]/CAP
                v=(wa*r[a]).sum(1)-(wb*r[b]).sum(1)-(wa.sum(1)+wb.sum(1))*.0004-wb.sum(1)*.03*borrowdays/365
                v[~ok]=np.nan;nulls[mode+'_'+sizing].append(v)
    daily=pd.DataFrame(rows);daily.to_csv(OUT/'daily.csv',index=False)
    pd.DataFrame(unresolved).to_csv(OUT/'unresolved.csv',index=False)
    summary=[]; years=[]; target=int((dates.year>=2018).sum())
    for (mode,sizing),g in daily.groupby(['mode','sizing']):
        net=g.net.to_numpy();ci=boot(net);yr=g.groupby(g.date.dt.year).net.sum()
        n=np.array(nulls[mode+'_'+sizing]);nullcount=np.isfinite(n).sum(0)
        paired=np.where(np.isfinite(n),net[:,None]-n,np.nan)
        differences=np.nansum(paired,axis=0)/np.maximum(nullcount,1)
        p=float((1+np.sum(differences<=0))/1001)
        row=dict(mode=mode,sizing=sizing,days=len(g),target_days=target,unresolved_days=target-len(g),gross_bp=g.gross.mean()*1e4,
                 net_bp=net.mean()*1e4,cost_bp=g.cost.mean()*1e4,borrow_bp=g.borrow.mean()*1e4,stress_bp=g.stress_net.mean()*1e4,
                 hac_t=hac(net),ci90_bp=[x*1e4 for x in ci],positive_years=int((yr>0).sum()),random_p=p,
                 null_complete_count=int((nullcount==len(g)).sum()),random_coverage_min=int(nullcount.min()),
                 market_adjusted_bp=g.market_adjusted.mean()*1e4,breakeven_rt_bp=(g.gross.sum()-g.borrow.sum())/g.gross_notional.sum()*1e4,
                 mean_beta=g.market_beta.mean(),eligible_long_bp=g.eligible_long.mean()*1e4,
                 power_t2_mean_bp=2*g.net.std()/np.sqrt(len(g))*1e4)
        for part,col in [('whole','net'),('long','long_net'),('short','short_net')]:
            row[part]=metrics.perf(pd.Series(g[col].to_numpy()*CAP,index=g.date),capital=CAP)
        # Missing-day and random-null completeness constraints are explicit failures.
        gates=dict(coverage=len(g)>=1000 and len(g)/target>.9,no_unresolved=len(g)==target,net_positive=net.mean()>0,
                   hac_t=row['hac_t']>=2,block_lower=ci[0]>0,four_years=(yr>0).sum()>=4,market_adjusted=g.market_adjusted.mean()>0,
                   random=p<=.05 and row['null_complete_count']==1000,stress=g.stress_net.mean()>0)
        row['gates']=gates;row['passes']=all(gates.values());summary.append(row)
        for year,gg in g.groupby(g.date.dt.year):years.append(dict(mode=mode,sizing=sizing,year=int(year),days=len(gg),gross=gg.gross.sum()*CAP,net=gg.net.sum()*CAP))
    pd.DataFrame(years).to_csv(OUT/'years.csv',index=False)
    save('summary.json',summary)
    save('manifest.json',dict(plan=PLAN,script_sha256=sha(__file__),input_hashes={p.name:sha(p) for p in DATA.iterdir() if p.is_file()},
         versions=dict(python=sys.version,numpy=np.__version__,pandas=pd.__version__,scipy=scipy.__version__),
         data_read_end='2022-12-31',recent_opened=False,variants=2,random_seed=4138715,bootstrap_seed=4138716,
         sources=df.source.value_counts().to_dict(),rows=len(df),tickers=len(names),monthly_selections=len(selections),
         decision='DESIGN FAIL; stop before recent' if not any(s['passes'] for s in summary) else 'PASS pending data/borrow verification',
         limitations=['restricted S&P500/SPY-beta proxy','revised third-party mixed-source prices','conditional complete-day diagnostics',
         'no borrow locates or actual auction fills','integer sizes use idealized recorded fill/reference price','not an executable cash ledger']))
    print(json.dumps([{k:v for k,v in s.items() if k not in ['whole','long','short']} for s in summary],indent=2,default=serial))

if __name__=='__main__':main()
