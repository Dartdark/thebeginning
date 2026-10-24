"""Independently reconcile frozen R2 diagnostic files; no new price replay/draw."""
import sys,json,hashlib
from pathlib import Path
from statistics import NormalDist
sys.path.insert(0,'agents/codex/runtime/or_pullback_python')
import numpy as np
import pandas as pd

ROOT=Path('analysis/outputs/codex_r2vault')
OUT=ROOT/'diagnostics'
PERIODS={'2018_22':('2018-01-01','2023-01-01'),'2018_24':('2018-01-01','2025-01-01'),
         '2023_plus':('2023-01-01','2100-01-01'),'2025_plus':('2025-01-01','2100-01-01'),
         'author_OOS_available':('2025-01-15','2026-09-01'),
         '2018_plus_source_end':('2018-01-01','2026-09-01'),'2018_plus':('2018-01-01','2100-01-01')}

def near(a,b): np.testing.assert_allclose(a,b,rtol=0,atol=3e-7,equal_nan=True)
def stat(x):
    x=np.asarray(x,float)
    return x.mean()/x.std(ddof=1)*np.sqrt(len(x)) if len(x)>1 and x.std(ddof=1)>0 else np.nan
def dsr(x,n):
    x=np.asarray(x,float)
    if len(x)<10 or x.std(ddof=1)==0: return np.nan
    normal=NormalDist(); e=.5772156649
    sr=x.mean()/x.std(ddof=1)
    sr0=((1-e)*normal.inv_cdf(1-1/n)+e*normal.inv_cdf(1-1/(n*np.e)))/np.sqrt(len(x)-1)
    m=x-x.mean(); g3=np.mean(m**3)/x.std(ddof=1)**3; g4=np.mean(m**4)/x.std(ddof=1)**4
    den=np.sqrt(max(1e-12,1-g3*sr+(g4-1)*sr**2/4))
    return normal.cdf((sr-sr0)*np.sqrt(len(x)-1)/den)
def maxdd(x):
    c=np.r_[0.,np.asarray(x,float).cumsum()]
    return (np.maximum.accumulate(c)-c).max()

def main():
    trials=json.loads((OUT/'trial_counts.json').read_text())
    assert trials['effective_n']==311 and trials['preregistered_n']==306
    near(trials['t_threshold'],NormalDist().inv_cdf(1-.05/311))
    stats=pd.read_csv(OUT/'standard_stats.csv')
    ledgers={}; curves={}; rowchecks=0
    for row in stats.itertuples():
        key=(row.model,row.fee_micro)
        if key not in ledgers:
            t=pd.read_csv(OUT/f'{row.model}_fee{row.fee_micro:.3f}_closed_trades.csv',parse_dates=['date','entry_date','exit_date'])
            expected=20*t.gross_points-10*row.fee_micro-5-np.where(t.kind==1,0,5)
            near(t.net_nq,expected);near(t.net_mnq,expected/10)
            ledgers[key]=t
        key2=(row.model,row.fee_micro,row.group)
        if key2 not in curves:
            curves[key2]=pd.read_csv(OUT/f'{row.model}_fee{row.fee_micro:.3f}_{row.group}_daily_nq.csv',index_col=0,parse_dates=True).iloc[:,0]
        t=ledgers[key]; daily=curves[key2]
        if row.group!='both': t=t[t.side==(1 if row.group=='long' else -1)]
        lo,hi=PERIODS.get(row.period,(row.period+'-01-01',str(int(row.period)+1)+'-01-01')) if row.period not in PERIODS else PERIODS[row.period]
        t=t[(t.date>=lo)&(t.date<hi)]; d=daily[(daily.index>=lo)&(daily.index<hi)]
        x=t.net_nq.to_numpy()
        near([row.trades,row.avg,row.total_nq,row.total_mnq,row.avg_mnq,row.t,row.t_daily,row.daily_total_nq,row.days,row.max_dd_including_start,row.dsr_preregistered,row.dsr_conservative_latest,row.n_exits_after_period_end],
             [len(t),x.mean() if len(t) else np.nan,x.sum(),x.sum()/10,x.mean()/10 if len(t) else np.nan,stat(x),stat(d),d.sum(),len(d),maxdd(d),dsr(x,306),dsr(x,311),(t.exit_date>=hi).sum()])
        gain=x[x>0].sum();loss=-x[x<0].sum()
        near(row.profit_factor,gain/loss if loss else np.inf)
        near(row.win,np.mean(x>0) if len(x) else np.nan)
        if row.period=='2018_plus' and row.group=='both': near(row.total_nq,row.daily_total_nq)
        rowchecks+=1
    p=pd.read_csv(OUT/'placebo_summary.csv')
    draws={}; source={}; control_calendars={}; pchecks=0
    for row in p.itertuples():
        key=(row.model,row.control)
        if key not in draws:
            draws[key]=pd.read_csv(OUT/f'{row.model}_{row.control}_draws.csv')
            df=draws[key]
            assert df.groupby('period').size().eq(1000).all()
            near(df.closed_trades+df.open_at_end,df.accepted_entries)
            assert (df.closed_equity_dd_nq>=0).all() and (df.unknown_held_events<=df.accepted_entries).all()
        if row.model not in source:
            source[row.model]=pd.read_csv(ROOT/'replay'/f'{row.model}_trades.csv',parse_dates=['entry_date'])
            a=pd.read_csv(ROOT/'replay'/f'{row.model}_audit.csv',parse_dates=['date'])
            control_calendars[row.model]=set(a.loc[a.control_eligible,'date'])
        lo,hi=PERIODS[row.period]
        t=source[row.model]
        t=t[(t.entry_date>=lo)&(t.entry_date<hi)]
        if row.reference_scope=='actual_entry_days_in_control_calendar': t=t[t.entry_date.isin(control_calendars[row.model])]
        x=20*t.gross_points-10*row.fee_micro-5-np.where(t.kind==1,0,5)
        df=draws[key];df=df[df.period==row.period]
        total=df.closed_net_nq.to_numpy();count=df.closed_trades.to_numpy()
        avg=np.divide(total,count,out=np.full(len(count),np.nan),where=count>0)
        actual_avg=x.mean() if len(x) else np.nan
        near([row.actual_closed_trades,row.actual_closed_total_nq,row.actual_avg_nq,row.actual_closed_equity_dd_nq,row.null_total_p5,row.null_total_p50,row.null_total_p95,row.null_expectancy_p50,row.null_count_min,row.null_count_mean,row.null_count_max,row.null_closed_dd_p50,row.null_closed_dd_p95,row.null_open_at_end_mean,row.null_unrealized_mean,row.null_unknown_held_events_mean,row.p_null_total_ge_actual,row.p_null_expectancy_ge_actual],
             [len(x),x.sum(),actual_avg,maxdd(x),np.quantile(total,.05),np.median(total),np.quantile(total,.95),np.nanmedian(avg),count.min(),count.mean(),count.max(),np.median(df.closed_equity_dd_nq),np.quantile(df.closed_equity_dd_nq,.95),df.open_at_end.mean(),df.terminal_unrealized_nq.mean(),df.unknown_held_events.mean(),(1+(total>=x.sum()).sum())/1001,(1+(avg>=actual_avg).sum())/1001])
        pchecks+=1
    design=pd.read_csv(OUT/'staged_design_closed_trade_stats.csv')
    for row in design.itertuples():
        t=pd.read_csv(ROOT/'replay'/f'{row.model}_2018_22_trades.csv')
        opened=pd.read_csv(ROOT/'replay'/f'{row.model}_2018_22_open_positions.csv')
        x=20*t.gross_points-10*row.fee_micro-5-np.where(t.kind==1,0,5)
        near([row.closed_at_design_cutoff,row.open_at_design_cutoff,row.total_nq,row.avg_nq,row.t,row.dsr311],
             [len(t),len(opened),x.sum(),x.mean(),stat(x),dsr(x,311)])
    ct=stats[(stats.model=='ct_raw')&(stats.group=='both')&(stats.fee_micro==1.04)&(stats.period=='2018_plus')].iloc[0]
    recent=p[(p.model=='ct_raw')&(p.control=='random_time')&(p.period=='2023_plus')]
    result=dict(status='PASS',standard_stat_rows=rowchecks,placebo_summary_rows=pchecks,staged_design_rows=len(design),null_draw_files=len(draws),draws_per_model_family=1000,actual_long_walker_events=3037+3148+2760+2856,trial_lower_bound=311,t_threshold=trials['t_threshold'],ct_raw_full_t=ct.t,ct_raw_full_dsr311=ct.dsr_conservative_latest,ct_raw_recent_time_total_p={r.reference_scope:r.p_null_total_ge_actual for r in recent.itertuples()},new_price_variants=0,new_control_draws=0,limits='Checked saved arithmetic and reviewed scheduling code; replay author is not an independent author-source or tick-path verifier. Bootstrap interval generation and standalone MC inspected, not redrawn.')
    (OUT/'saved_output_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
