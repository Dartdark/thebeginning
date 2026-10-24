"""Frozen Anson saved-ledger metrics and reexecuted conditional nulls (928c0ea)."""
from pathlib import Path
import io,json,pickle,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'agents/codex/runtime/or_pullback_python'),str(ROOT/'analysis')]
import numpy as np
import pandas as pd
import metrics as M, resampling as R, montecarlo as MC
import codex_anson_personal as P
OUT=ROOT/'analysis/outputs/codex_anson/diagnostics'
REPLAY=OUT.parent/'replay'
PIN='e34d71cd3537a9f019d2521e280fc92f3ffdb4c6'
PERIODS={'2018_22':('2018-01-01','2023-01-01'),'2018_24_author_IS':('2018-01-01','2025-01-01'),
 '2023_plus':('2023-01-01','2100-01-01'),'2025_plus_replication':('2025-01-01','2100-01-01'),
 '2018_plus':('2018-01-01','2100-01-01')}

def tstat(x):
    x=np.asarray(x,float)
    return x.mean()/x.std(ddof=1)*np.sqrt(len(x)) if len(x)>1 and x.std(ddof=1)>0 else np.nan

def intervals_ev(t,days,seed=848,n=5000,block=10):
    pnl=t.groupby('date').net_nq.sum().reindex(days,fill_value=0.).to_numpy()
    count=t.groupby('date').size().reindex(days,fill_value=0).to_numpy()
    rng=np.random.default_rng(seed);means=[]
    for start in range(0,n,100):
        m=min(100,n-start);st=rng.integers(0,len(days)-block+1,(m,int(np.ceil(len(days)/block))))
        idx=(st[:,:,None]+np.arange(block)).reshape(m,-1)[:,:len(days)]
        means.extend(pnl[idx].sum(1)/count[idx].sum(1))
    return np.quantile(means,[.025,.975]).tolist()

def standard(g,loaded):
    trials=pd.read_csv(io.BytesIO(subprocess.check_output(['git','show',PIN+':TRIALS.csv'])))
    nitems=len(trials)+7
    rows=[];mc=[];cis=[]
    years=sorted(pd.DatetimeIndex(g.ts[g.trading]).year.unique())
    periods={**PERIODS,**{str(y):(f'{y}-01-01',f'{y+1}-01-01') for y in years if y>=2018}}
    for model,(raw,audit) in loaded.items():
        dates=pd.DatetimeIndex(g.ts[g.trading]);dates=dates[dates>='2018-01-01']
        t=raw.copy()
        if model=='intended_apex':
            dates=pd.DatetimeIndex(audit.loc[audit.account_eligible,'date'])
            t=t[t.date.isin(dates)].copy()
        for fee in (1.04,1.24):
            t['net_nq']=t.gross_points*20-fee*10-10
            for group,sign in (('both',0),('long',1),('short',-1)):
                s=t if not sign else t[t.side==sign]
                daily,_,_=P.candidate_daily(g,s,dates,fee=fee)
                daily=daily*10
                for period,(lo,hi) in periods.items():
                    d=daily[(daily.index>=lo)&(daily.index<hi)]
                    z=s[(s.date>=lo)&(s.date<hi)]
                    row=M.perf(d,z.net_nq)
                    row.update(model=model,fee_micro=fee,group=group,period=period,t=tstat(z.net_nq),
                        avg_mnq=z.net_nq.mean()/10,total_mnq=z.net_nq.sum()/10,dsr=M.deflated_sharpe(z.net_nq,nitems),
                        author_cost_avg_nq=(z.gross_points*20-7.25).mean(),days=len(d),daily_note='session marks; trade cohort by entry date')
                    rows.append(row)
                if fee==1.04 and model!='defaults_raw':
                    for period in ('2023_plus','2025_plus_replication'):
                        lo,hi=PERIODS[period];d=daily[(daily.index>=lo)&(daily.index<hi)]
                        z=s[(s.date>=lo)&(s.date<hi)]
                        R.bootstrap(d,n=5000,block=10,seed=848).to_csv(OUT/f'{model}_{group}_{period}_bootstrap.csv')
                        # Ratio of whole-day blocks preserves trade clustering/counts.
                        ci=intervals_ev(z,pd.DatetimeIndex(d.index))
                        cis.append(dict(model=model,group=group,period=period,trades=len(z),ev_nq=z.net_nq.mean(),
                                        lo_nq=ci[0],hi_nq=ci[1],method='95% ten-day block ratio-of-trade-sums'))
                        for size in (1,2):
                            r=MC.daily_mc(d.to_numpy()*size/10,horizon=252,n=5000,block=10,seed=848)
                            tm=MC.trade_mc(z.net_nq.to_numpy()*size/10,n=5000,seed=848)
                            mc.append(dict(model=model,group=group,period=period,size_mnq=size,
                                **{'daily_'+k:v for k,v in r.items()},**{'trade_'+k:v for k,v in tm.items()}))
        raw.to_csv(OUT/f'{model}_source_trades.csv',index=False)
    pd.DataFrame(rows).to_csv(OUT/'standard_stats.csv',index=False)
    pd.DataFrame(mc).to_csv(OUT/'standalone_mc.csv',index=False)
    pd.DataFrame(cis).to_csv(OUT/'ev_intervals.csv',index=False)
    (OUT/'trial_counts.json').write_text(json.dumps(dict(ranked_items=len(trials),ranked_variants=int(trials.variants.sum()),
        prior_codex_return_variants=4,new_models=3,dsr_N=nitems,t_threshold=M.t_threshold(nitems),
        author_search_count='unknown; rejected stop/target/size/side/WFO settings count'),indent=2)+'\n')

def placebos(g,t,audit,n=1000):
    dates=pd.DatetimeIndex(audit.loc[audit.account_eligible,'date'])
    t=t[t.date.isin(dates)].sort_values(['date','entry_j']).copy()
    raw=(t.exit-t.entry)*t.side*20
    rng=np.random.default_rng(848)
    side=raw.to_numpy()[None,:]*rng.choice([-1,1],(n,len(t)))-20.4
    output=[]
    periods={k:v for k,v in PERIODS.items() if k in ('2018_22','2023_plus','2025_plus_replication','2018_plus')}
    time_totals={p:np.zeros(n) for p in periods};counts={p:np.zeros(n,int) for p in periods}
    rng=np.random.default_rng(849)
    for date,group in t.groupby('date',sort=True):
        d=int(group.day.iloc[0]);early=bool(group.threshold.iloc[0]) and bool(audit.set_index('date').loc[date,'early_close_proxy'])
        flat=691 if early else 896
        signals=np.arange(510,690 if early else 871,5)
        entries=signals+1
        exits=np.minimum(entries+100,flat)
        points=(g.o[d,exits]-g.o[d,entries])*20
        if not np.isfinite(points).all():raise ValueError('Null event outside complete window')
        sides=group.side.to_numpy()
        sampled=np.sort(np.argsort(rng.random((n,len(entries))),axis=1)[:,:len(group)],axis=1)
        last_exit=np.full(n,-1000);totals=np.zeros(n);kept=np.zeros(n,int)
        for k in range(len(group)):
            ix=sampled[:,k];e=entries[ix];x=exits[ix]
            # A source exit bar must close before a subsequent entry: one flat chart bar.
            ok=e>=last_exit+5
            totals+=np.where(ok,points[ix]*sides[k]-20.4,0.)
            kept+=ok
            last_exit=np.where(ok,x,last_exit)
        for p,(lo,hi) in periods.items():
            if pd.Timestamp(lo)<=date<pd.Timestamp(hi):time_totals[p]+=totals;counts[p]+=kept
    for p,(lo,hi) in periods.items():
        mask=(t.date>=lo)&(t.date<hi);actual=(raw[mask]-20.4).sum()
        for control,draws,ct in (('random_side',side[:,mask].sum(1),np.full(n,int(mask.sum()))),
                                ('random_time',time_totals[p],counts[p])):
            output.append(dict(control=control,period=p,real_trades=int(mask.sum()),real_total_nq=actual,
                null_p5=np.quantile(draws,.05),null_p50=np.median(draws),null_p95=np.quantile(draws,.95),
                p_null_ge_real=(1+(draws>=actual).sum())/(n+1),null_count_min=ct.min(),null_count_mean=ct.mean(),null_count_max=ct.max(),
                caveat='Conditional observed-event-day control; shifted overlapping events can skip; not an independent tradable strategy'))
            pd.DataFrame(dict(total_nq=draws,trades=ct)).to_csv(OUT/f'{control}_{p}_draws.csv',index=False)
    pd.DataFrame(output).to_csv(OUT/'placebo_summary.csv',index=False)

def main():
    subprocess.check_call(['git','cat-file','-e','928c0ea:agents/codex/plans/anson_momentum.md'])
    OUT.mkdir(parents=True,exist_ok=True)
    with (ROOT/'scratch_data/g24.pkl').open('rb') as f:g=pickle.load(f)
    loaded={m:(pd.read_csv(REPLAY/f'{m}_trades.csv',parse_dates=['date']),
               pd.read_csv(REPLAY/f'{m}_audit.csv',parse_dates=['date']))
            for m in ('intended_raw','intended_apex','defaults_raw')}
    standard(g,loaded)
    print('standalone statistics complete',flush=True)
    placebos(g,*loaded['intended_apex'])
    print('conditional nulls complete',flush=True)

if __name__=='__main__':main()
