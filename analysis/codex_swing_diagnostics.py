"""Fixed uncertainty, null and execution checks for the Swing Target audit."""
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scratch_data/codex_deps'))
sys.path.insert(0,str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import codex_swing_target as H
import codex_swing_engine as E
import metrics as M
import resampling as R
import montecarlo as MC
from codex_swing_bootstrap import bootstrap as initial_zero_bootstrap
from trials import parse_tier_list

OUT=H.OUT
TRIALS_PATH=ROOT/'agents/codex/inputs/swing_target/tier_list_e08c353.md'

def significance_only():
    _,days,_=H.setup()
    n=len(parse_tier_list(str(TRIALS_PATH)))+2
    rows=[]
    for model in ['CODE','CODE_BE']:
        t=pd.read_csv(OUT/(model+'_trades.csv'),parse_dates=['date','exit_date'])
        for period,ds in [('2023+',days[days.year>=2023]),('all',days)]:
            z=t[t.date.isin(ds)]
            for side in ['all','long','short']:
                a=z if side=='all' else z[z.side.eq(1 if side=='long' else -1)]
                d=H.daily(a,ds)
                rows.append(dict(model=model,period=period,side=side,ranked_item_plus_two=n,
                    t_threshold=M.t_threshold(n),t=float(a.net.mean()/a.net.std()*np.sqrt(len(a))),
                    dsr=M.deflated_sharpe(a.net,n),min_trl=M.min_trl(a.net),regime_rho=M.regime_rho(d)[0]))
    pd.DataFrame(rows).to_csv(OUT/'significance.csv',index=False)
    print('Significance refreshed at pinned latest ranked-item count:',n)

def main():
    g,days,pc=H.setup()
    freeze=json.loads((OUT/'manifest.json').read_text())
    assert all(H.sha(ROOT/p)==v for p,v in freeze['hashes'].items())
    H.dump('synthetic_checks.json',E.synthetic_checks())
    metrics=pd.read_csv(OUT/'metrics.csv')
    n=len(parse_tier_list(str(TRIALS_PATH)))+2
    bootrows=[]; permutations=[];risk=[];sigrows=[];stress=[];nulls=[];nullsummary=[];coverage=[]
    for model,be in [('CODE',False),('CODE_BE',True)]:
        t=pd.read_csv(OUT/(model+'_trades.csv'),parse_dates=['date','exit_date'])
        # Independent ledger arithmetic and no silently dropped overnight P&L.
        np.testing.assert_allclose(t.pnl,(t.exit-t.entry)*t.side*20,atol=1e-8,rtol=0)
        assert t.groupby('date').size().max()==1
        assert np.isclose(H.daily(t,days).sum(),t.net.sum())
        t[t.cross_date|t.unknown_held_minutes.gt(0)].to_csv(OUT/(model+'_coverage_exceptions.csv'),index=False)
        coverage.append(dict(model=model,cross_date=int(t.cross_date.sum()),
            unknown_minute_trades=int(t.unknown_held_minutes.gt(0).sum()),unknown_minutes=int(t.unknown_held_minutes.sum()),
            unrounded_target_distances=True))
        for period,ds in [('2023+',days[days.year>=2023]),('all',days)]:
            z=t[t.date.isin(ds)]
            for side in ['all','long','short']:
                a=z if side=='all' else z[z.side.eq(1 if side=='long' else -1)]
                daily=H.daily(a,ds)
                b=initial_zero_bootstrap(daily,n=5000,block=10,seed=H.SEED)
                for metric,r in b.iterrows():bootrows.append(dict(model=model,period=period,side=side,metric=metric,**r.to_dict()))
                permutations.append(dict(model=model,period=period,side=side,**R.permutation(daily,n=5000,seed=H.SEED)))
                sigrows.append(dict(model=model,period=period,side=side,ranked_item_plus_two=n,
                    t_threshold=M.t_threshold(n),t=float(a.net.mean()/a.net.std()*np.sqrt(len(a))),
                    dsr=M.deflated_sharpe(a.net,n),min_trl=M.min_trl(a.net),regime_rho=M.regime_rho(daily)[0]))
            for size,trail in [(1,2000),(2,4000)]:
                native=H.daily(z,ds,col='native_net_per_mnq')*size
                risk.append(dict(model=model,period=period,mnq=size,trail=trail,
                    **MC.daily_mc(native,horizon=252,n=5000,block=10,seed=H.SEED,trail=trail)))
            # Full trade-sequence Monte Carlo at native one-micro costs.
            H.dump(model+'_'+period.replace('+','plus')+'_trade_mc.json',MC.trade_mc(z.native_net_per_mnq,n=10000,seed=H.SEED))
        # Fixed opposite minute path, not a source parameter or selected setting.
        raw,diag=E.replay(g,breakeven=be,start_date='2018-01-01',end_date='2026-10-09',path_mode=1)
        x=H.costs(raw,g)
        x.to_csv(OUT/(model+'_opposite_path_trades.csv'),index=False)
        for period,ds in [('2018-22',days[days.year<=2022]),('2023+',days[days.year>=2023]),('all',days)]:
            stress.append(dict(scenario='opposite_minute_path',**H.metric(x,ds,model,period)))
        for scenario,column in [('extra_tick','extra_tick_net'),('native_1.04','mnq_fee_1.04'),('author_1dollar','author_cost_per_mnq')]:
            for period,ds in [('2018-22',days[days.year<=2022]),('2023+',days[days.year>=2023]),('all',days)]:
                z=t[t.date.isin(ds)]
                stress.append(dict(model=model,period=period,scenario=scenario,trades=len(z),total=float(z[column].sum()),
                    avg=float(z[column].mean()),profit_factor=float(z.loc[z[column]>0,column].sum()/-z.loc[z[column]<0,column].sum()),
                    max_trade_dd=R.max_dd(z[column]),unit='MNQ' if scenario!='extra_tick' else 'NQ'))
        # Simulate 500 complete, prespecified null runs in one vector batch.
        for family in ['random_time','random_side']:
            rng=np.random.default_rng(H.SEED+(0 if family=='random_time' else 1))
            count=len(t)
            rows=np.empty((500*count,4),float)
            native_minutes={int(d):np.flatnonzero(np.isfinite(g.o[int(d),526:871]))+526 for d in t.day.unique()}
            for run in range(500):
                block=np.c_[t.day.to_numpy(),t.j0.to_numpy(),t.side.to_numpy(),t.entry_avg_range.to_numpy()]
                if family=='random_time':
                    block[:,1]=[rng.choice(native_minutes[int(d)]) for d in t.day]
                else:block[:,2]=rng.choice(np.array([-1,1]),size=count)
                rows[run*count:(run+1)*count]=block
            q=E.replay_market(g,rows,breakeven=be)
            if len(q)!=len(rows):
                nullsummary.append(dict(model=model,family=family,status='INCOMPLETE: unclosed null paths',expected=len(rows),closed=len(q)))
                continue
            q=H.costs(q,g)
            profits=q.net.to_numpy().reshape(500,count)
            for side in ['all','long','short']:
                mask=np.ones(count,bool) if side=='all' else t.side.eq(1 if side=='long' else -1).to_numpy()
                actual=float(t.loc[mask,'net'].mean())
                for run in range(500):nulls.append(dict(model=model,family=family,side=side,run=run,avg=float(profits[run,mask].mean()),total=float(profits[run,mask].sum())))
                averages=profits[:,mask].mean(1)
                nullsummary.append(dict(model=model,family=family,side=side,status='complete',runs=500,actual_avg=actual,
                    null_avg=float(averages.mean()),null_p5=float(np.percentile(averages,5)),null_p95=float(np.percentile(averages,95)),
                    tail_at_least_actual=float((1+(averages>=actual).sum())/501)))
        print(model,'diagnostics complete',flush=True)
    for name,rows in [('bootstrap.csv',bootrows),('permutation.csv',permutations),('native_daily_mc.csv',risk),
        ('significance.csv',sigrows),('execution_stress.csv',stress),('placebo_runs.csv',nulls),('placebo_summary.csv',nullsummary)]:
        pd.DataFrame(rows).to_csv(OUT/name,index=False)
    H.dump('diagnostic_checks.json',dict(source_plan_commit=pc,ledger_price_pnl_and_daily_sums_pass=True,
        one_trade_per_day_pass=True,coverage=coverage,new_economic_models=2,cache_unchanged=True,
        initial_zero_dd=True,diagnostic_script_sha256=H.sha(Path(__file__)),
        caveat='Nulls condition on actual trade days. Random-time retains the later revealed breakout direction and can enter before that direction was known; it is a descriptive hindsight benchmark, not a tradable alternative. Random-side per-side rows retain original opportunity labels.'))

if __name__=='__main__':significance_only() if '--significance-only' in sys.argv else main()
