"""Frozen uncertainty, null, filter and cost checks for Overnight Rebound.

Uses saved primary ledgers after the parent completes design and validation.
No source-engine edits, cache rebuilding or additional economic models.
"""
from __future__ import annotations

from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scratch_data/codex_deps'))
sys.path.insert(0,str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import codex_rebound_run as H
import codex_rebound_engine as E
from codex_swing_bootstrap import bootstrap as initial_zero_bootstrap
from trials import parse_tier_list
import metrics as M
import resampling as R
import montecarlo as MC

OUT=H.OUT
MODELS=('UNIFORM','SUNDAY2','ALLNIGHTS')


def period_slice(t,days,period):
    """CME/account exit dates retain Sunday-entry trades and same-night stops."""
    if period=='2018-22':lo,hi=pd.Timestamp('2018-01-01'),pd.Timestamp('2022-12-31')
    elif period=='2023+':lo,hi=pd.Timestamp('2023-01-01'),pd.Timestamp('2026-10-09')
    elif period=='all':lo,hi=pd.Timestamp('2018-01-01'),pd.Timestamp('2026-10-09')
    else:raise ValueError(period)
    return t[t.account_date.between(lo,hi)].copy(),days[(days>=lo)&(days<=hi)]


def load_ledger(model):
    t=pd.read_csv(OUT/(model+'_trades.csv'),parse_dates=['date','exit_date','account_date'])
    # Reprice only from raw prices and quantities, never double-apply Sunday2.
    z=H.costs(t)
    for col in ['net','gross','native_net_per_mnq','two_ticks_net','four_ticks_net']:
        np.testing.assert_allclose(z[col],t[col],rtol=0,atol=1e-8)
    np.testing.assert_allclose(t.pnl,(t.exit-t.entry)*t.side*20,rtol=0,atol=1e-8)
    assert t.side.eq(1).all() and t.qty.isin([1.,2.]).all()
    return t


def pnl_stats(x):
    x=np.asarray(x,float)
    if not len(x):return dict(trades=0,total=0.,avg=None,t=None,profit_factor=None,max_trade_dd=0.)
    positive=x[x>0].sum();negative=-x[x<0].sum()
    return dict(trades=len(x),total=float(x.sum()),avg=float(x.mean()),
        t=float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))) if len(x)>1 and x.std(ddof=1)>0 else None,
        profit_factor=float(positive/negative) if negative>0 else None,max_trade_dd=R.max_dd(x))


def coverage_audit(g,ledgers):
    """Inventory unobserved held bars without asserting a halt/feed cause."""
    flat={c:getattr(g,c).ravel() for c in 'ohlc'}
    rows=[];intervals=[];reopens=[];summary=[]
    for model,t in ledgers.items():
        total=0;largest=0;pause=weekend=other=0
        for r in t.itertuples():
            reopens.append(dict(model=model,date=str(r.date.date()),entry_j=int(r.j0),submit_j=int(r.entry_submit_j),
                native_1701_present=bool(np.isfinite(g.o[int(r.day),1021])),
                native_1702_present=bool(np.isfinite(g.o[int(r.day),1022]))))
            if not r.unknown_held_minutes:continue
            start=int(r.day)*1440+int(r.j0);end=int(r.exit_day)*1440+int(r.j1)
            finite=np.logical_and.reduce([np.isfinite(a[start:end+1]) for a in flat.values()])
            missing=np.flatnonzero(~finite)+start
            assert len(missing)==int(r.unknown_held_minutes)
            total+=len(missing)
            groups=np.split(missing,np.flatnonzero(np.diff(missing)>1)+1)
            trade_pause=trade_weekend=trade_other=0
            for group in groups:
                largest=max(largest,len(group))
                minute=group%1440
                dates=pd.DatetimeIndex(g.ts[group//1440])
                nominal_pause=(minute>960)&(minute<=1020)
                nominal_weekend=(dates.dayofweek==5)|((dates.dayofweek==6)&(minute<=1020))
                n_pause=int(nominal_pause.sum());n_weekend=int((nominal_weekend&~nominal_pause).sum())
                n_other=len(group)-n_pause-n_weekend
                trade_pause+=n_pause;trade_weekend+=n_weekend;trade_other+=n_other
                first=pd.Timestamp(g.ts[int(group[0])//1440])+pd.Timedelta(minutes=int(group[0])%1440)
                last=pd.Timestamp(g.ts[int(group[-1])//1440])+pd.Timedelta(minutes=int(group[-1])%1440)
                intervals.append(dict(model=model,entry_date=str(r.date.date()),first_missing_ct=str(first),last_missing_ct=str(last),
                    missing_minutes=len(group),nominal_daily_pause_minutes=n_pause,nominal_weekend_minutes=n_weekend,
                    other_unobserved_minutes=n_other,market_or_feed_cause_verified=False))
            pause+=trade_pause;weekend+=trade_weekend;other+=trade_other
            rows.append(dict(model=model,entry_date=str(r.date.date()),exit_date=str(r.exit_date.date()),j0=int(r.j0),j1=int(r.j1),
                reason=r.reason,unknown_held_minutes=len(missing),longest_contiguous_gap=max(len(x) for x in groups),
                nominal_daily_pause_minutes=trade_pause,nominal_weekend_minutes=trade_weekend,
                other_unobserved_minutes=trade_other))
        assert total==int(t.unknown_held_minutes.sum())
        summary.append(dict(model=model,trades_with_unknown_held_minutes=int(t.unknown_held_minutes.gt(0).sum()),
            total_unknown_held_minutes=total,longest_contiguous_gap=largest,nominal_daily_pause_minutes=pause,
            nominal_weekend_minutes=weekend,other_unobserved_minutes=other,
            entry_label_counts={str(int(k)):int(v) for k,v in t.j0.value_counts().items()},
            cause='Unverified: absent native bar can reflect no prints, source omission, feed gap or market restrictions; no classification is assumed'))
    pd.DataFrame(rows).to_csv(OUT/'coverage_tickets.csv',index=False)
    pd.DataFrame(intervals).to_csv(OUT/'coverage_intervals.csv',index=False)
    pd.DataFrame(reopens).to_csv(OUT/'reopen_bar_inventory.csv',index=False)
    H.dump('coverage_summary.json',summary)
    return summary


def fixed_nulls(g,t,model):
    count=len(t)
    output=[];summary=[];counts=[]
    # The cash signal/range is known by15:00, before every random evening entry.
    observed={int(d):np.flatnonzero(np.logical_and.reduce([
        np.isfinite(a[int(d),1022:1203]) for a in [g.o,g.h,g.l,g.c]]))+1022 for d in t.day.unique()}
    if any(not len(x) for x in observed.values()):
        raise ValueError('No observed17:02–20:02 bar on an actual entry date; do not invent a null fill')
    for family in ['random_time','random_side']:
        rng=np.random.default_rng(H.SEED+(0 if family=='random_time' else 1))
        signals=np.empty((500*count,5))
        for run in range(500):
            a=np.c_[t.day.to_numpy(),t.j0.to_numpy(),np.ones(count),t.signal_range.to_numpy(),t.qty.to_numpy()]
            if family=='random_time':a[:,1]=[rng.choice(observed[int(d)]) for d in t.day]
            else:a[:,2]=rng.choice(np.array([-1,1]),size=count)
            signals[run*count:(run+1)*count]=a
        q=E.replay_market(g,signals)
        request=int(q.attrs['requested_signals']);closed=int(q.attrs['closed_signals'])
        missing=list(q.attrs['unclosed_signal_ids'])
        assert request==len(signals) and closed==len(q) and closed+len(missing)==request
        assert q.signal_id.is_unique
        expected_ids=np.setdiff1d(np.arange(request),np.asarray(missing,int),assume_unique=True)
        assert np.array_equal(np.sort(q.signal_id.to_numpy()),expected_ids)
        counts.append(dict(model=model,family=family,requested=request,closed=closed,
            unclosed_count=len(missing),unclosed_signal_ids=missing,runs=500,tickets_per_run=count))
        if missing:
            summary.append(dict(model=model,family=family,status='INCOMPLETE: unclosed nulls retained as missing',
                runs=500,requested=request,closed=closed,unclosed=len(missing)))
            continue
        # Unit stops/market fills pay exactly one RT cost per contract.
        q=q.sort_values('signal_id')
        net=(q.pnl.to_numpy()-17.25)*q.qty.to_numpy()
        native=(q.pnl.to_numpy()/10-2.24)*q.qty.to_numpy()
        p=net.reshape(500,count);p_native=native.reshape(500,count)
        for run in range(500):
            output.append(dict(model=model,family=family,run=run,trades=count,contracts=float(t.qty.sum()),
                total=float(p[run].sum()),avg=float(p[run].mean()),native_total=float(p_native[run].sum()),
                max_trade_dd=R.max_dd(p[run])))
        actual=float(t.net.mean());means=p.mean(1)
        summary.append(dict(model=model,family=family,status='complete',runs=500,requested=request,closed=closed,unclosed=0,
            actual_avg=actual,null_avg=float(means.mean()),null_p5=float(np.percentile(means,5)),
            null_p50=float(np.median(means)),null_p95=float(np.percentile(means,95)),
            tail_at_least_actual=float((1+(means>=actual).sum())/501)))
    return output,summary,counts


def filter_check(g,uniform,all_nights,days):
    cols=['day','j0','exit_day','j1','entry','exit','pnl','net','reason','signal_day','signal_range','account_date']
    pair=uniform[cols].merge(all_nights[cols],on=['day','j0'],how='outer',suffixes=('_down','_all'),indicator=True,validate='one_to_one')
    both=pair._merge.eq('both')
    exact=np.ones(len(pair),bool)
    for col in ['exit_day','j1','entry','exit','pnl','net','signal_day','signal_range']:
        exact &= np.isclose(pair[col+'_down'],pair[col+'_all'],rtol=0,atol=1e-8,equal_nan=False)
    exact &= pair.reason_down.eq(pair.reason_all)
    pair['exact']=both&exact
    pair['status']=np.where(pair._merge.eq('left_only'),'down_only',np.where(pair._merge.eq('right_only'),'control_only',
                         np.where(pair.exact,'matched_exact','matched_different')))
    pair.drop(columns='_merge').to_csv(OUT/'down_filter_pairing.csv',index=False)
    global_complete=bool(pair.loc[~pair.status.eq('control_only'),'status'].eq('matched_exact').all())
    source_open=g.o[all_nights.signal_day.to_numpy(int),511]
    source_close=g.c[all_nights.signal_day.to_numpy(int),900]
    known=np.isfinite(source_open)&np.isfinite(source_close)
    actual_down=source_close<source_open
    all_nights=all_nights.copy()
    all_nights['cash_signal_known']=known
    all_nights['cash_down']=known&actual_down
    down_keys=set(zip(uniform.day,uniform.j0))
    all_nights['retained_by_down_entries']=[(int(d),int(j)) in down_keys for d,j in zip(all_nights.day,all_nights.j0)]
    all_nights['removed_up_flat']=all_nights.cash_signal_known&~all_nights.cash_down
    all_nights.to_csv(OUT/'filter_control_signal_inventory.csv',index=False)
    summaries=[];draws=[]
    for period in ['2018-22','2023+','all']:
        u,ds=period_slice(uniform,days,period)
        a,_=period_slice(all_nights,days,period)
        removed=a[a.removed_up_flat]
        removed_stats=pnl_stats(removed.net)
        # Every sampled subset retains whole tickets, original chronology and
        # actual account-day booking. It is a random-drop comparison, not a model.
        n=len(u)
        if n>len(a):raise ValueError('Down subset larger than its all-night control')
        calendar=ds.union(pd.DatetimeIndex(a.account_date.unique())).union(pd.DatetimeIndex(u.account_date.unique())).sort_values()
        positions=calendar.get_indexer(pd.DatetimeIndex(a.account_date))
        assert (positions>=0).all()
        actual_net=float(u.net.sum());actual_dd=R.max_dd(H.daily(u,calendar))
        control_dd=R.max_dd(H.daily(a,calendar))
        rng=np.random.default_rng(H.SEED)
        sampled_net=[];sampled_dd=[]
        values=a.net.to_numpy()
        for run in range(1000):
            choice=np.sort(rng.choice(len(a),size=n,replace=False))
            d=np.bincount(positions[choice],weights=values[choice],minlength=len(calendar))
            total=float(values[choice].sum());dd=R.max_dd(d)
            sampled_net.append(total);sampled_dd.append(dd)
            draws.append(dict(period=period,run=run,kept_tickets=n,total=total,max_eod_dd=dd))
        sampled_net=np.asarray(sampled_net);sampled_dd=np.asarray(sampled_dd)
        summaries.append(dict(period=period,comparison_identifiable=global_complete,
            down_tickets=n,control_tickets=len(a),removed_up_flat_tickets=len(removed),
            unknown_cash_signal_tickets=int((~a.cash_signal_known).sum()),
            down_total=actual_net,control_total=float(a.net.sum()),down_eod_dd=actual_dd,control_eod_dd=control_dd,
            removed_total=removed_stats['total'],removed_avg=removed_stats['avg'],removed_t=removed_stats['t'],
            removed_should_lose_for_filter_claim=bool(removed_stats['total']<0),random_subsets=1000,
            random_keep_total_p5=float(np.percentile(sampled_net,5)),random_keep_total_p50=float(np.median(sampled_net)),
            random_keep_total_p95=float(np.percentile(sampled_net,95)),
            random_total_at_least_actual=float((1+(sampled_net>=actual_net).sum())/1001),
            random_dd_at_most_actual=float((1+(sampled_dd<=actual_dd).sum())/1001),
            actual_jointly_beats_random_fraction=float(((sampled_net<actual_net)&(sampled_dd>actual_dd)).mean())))
    pd.DataFrame(summaries).to_csv(OUT/'down_filter_summary.csv',index=False)
    pd.DataFrame(draws).to_csv(OUT/'down_filter_random_subsets.csv',index=False)
    H.dump('down_filter_checks.json',dict(all_down_entries_exactly_match=global_complete,
        pairing_counts={k:int(v) for k,v in pair.status.value_counts().items()},
        caveat='If source state/occupied positions alter matching, filter totals are descriptive rather than a pure removal experiment.'))


def main():
    g,days,pc=H.setup()
    # This guard deliberately refuses partial design-only outputs.
    if not (OUT/'manifest.json').exists() or not all((OUT/(model+'_validation_trades.csv')).exists() for model in MODELS):
        raise PermissionError('Complete parent validation ledgers are required before diagnostics')
    import json
    manifest=json.loads((OUT/'manifest.json').read_text())
    assert all(H.sha(ROOT/p)==v for p,v in manifest['hashes'].items())
    ranked=len(parse_tier_list(str(H.INPUT/'tier_list_e1a94f7.md')))
    scopes=[('ranked_plus_three',ranked+3),('ranked_plus_three_plus_336',ranked+3+336)]
    ledgers={model:load_ledger(model) for model in MODELS}
    coverage=coverage_audit(g,ledgers)
    bootrows=[];permutations=[];risk=[];trade_mc=[];significance=[];stress=[]
    nullrows=[];nullsummary=[];nullcounts=[];calendar_checks=[]
    for model,t in ledgers.items():
        assert np.isclose(H.daily(t,days).sum(),t.net.sum())
        sunday=t.entry_et_dow.eq(0)
        calendar_checks.append(dict(model=model,tickets=len(t),contracts=float(t.qty.sum()),
            sunday_tickets=int(sunday.sum()),sunday_entry_net=float(t.loc[sunday,'net'].sum()),
            raw_sunday_calendar_entries=int(t.date.dt.dayofweek.eq(6).sum()),
            daily_net_reconciled=True,deadline_crossings=int(t.crosses_1559_ct.sum())))
        for period in ['2023+','all']:
            z,ds=period_slice(t,days,period)
            d=H.daily(z,ds)
            assert np.isclose(d.sum(),z.net.sum())
            b=initial_zero_bootstrap(d,n=5000,block=10,seed=H.SEED)
            assert np.isclose(b.loc['max_dd','actual'],R.max_dd(d))
            for metric,r in b.iterrows():bootrows.append(dict(model=model,period=period,side='all/long',metric=metric,**r.to_dict()))
            permutations.append(dict(model=model,period=period,**R.permutation(d,n=5000,seed=H.SEED)))
            for scope,n in scopes:
                significance.append(dict(model=model,period=period,scope=scope,trials=n,t_threshold=M.t_threshold(n),
                    t=float(z.net.mean()/z.net.std()*np.sqrt(len(z))),dsr=M.deflated_sharpe(z.net,n),
                    min_trl=M.min_trl(z.net),regime_rho=M.regime_rho(d)[0]))
            tm=MC.trade_mc(z.native_net_per_mnq,n=10000,seed=H.SEED)
            trade_mc.append(dict(model=model,period=period,unit='base1MNQ_qty_weighted_tickets',contracts=float(z.qty.sum()),**tm))
            for size,trail in [(1,2000),(2,4000)]:
                risk.append(dict(model=model,period=period,base_mnq=size,trail=trail,
                    **MC.daily_mc(H.daily(z,ds,col='native_net_per_mnq')*size,horizon=252,n=5000,block=10,seed=H.SEED,trail=trail)))
        for period in ['2018-22','2023+','all']:
            z,ds=period_slice(t,days,period)
            for scenario,col,unit in [('two_ticks_per_fill','two_ticks_net','NQ'),('four_ticks_per_fill','four_ticks_net','NQ'),
                                      ('native_fee_1.04','mnq_fee_1.04','baseMNQ'),('author_1dollar_no_slip','author_1dollar','baseMNQ')]:
                stats=pnl_stats(z[col])
                d=H.daily(z,ds,col=col)
                stress.append(dict(model=model,period=period,scenario=scenario,unit=unit,contracts=float(z.qty.sum()),
                    max_eod_dd=R.max_dd(d),**stats))
        if model in ('UNIFORM','SUNDAY2'):
            nr,ns,nc=fixed_nulls(g,t,model)
            nullrows.extend(nr);nullsummary.extend(ns);nullcounts.extend(nc)
        print(model+' diagnostics complete',flush=True)
    filter_check(g,ledgers['UNIFORM'],ledgers['ALLNIGHTS'],days)
    for name,rows in [('bootstrap.csv',bootrows),('permutation.csv',permutations),('native_daily_mc.csv',risk),
        ('native_trade_mc.csv',trade_mc),('significance.csv',significance),('execution_stress.csv',stress),
        ('placebo_runs.csv',nullrows),('placebo_summary.csv',nullsummary)]:
        pd.DataFrame(rows).to_csv(OUT/name,index=False)
    H.dump('placebo_counts.json',nullcounts)
    H.dump('diagnostic_checks.json',dict(plan_commit=pc,model_count=3,new_economic_models=0,
        primary_hashes_match=True,all_price_pnl_cost_quantity_arithmetic_matches=True,
        calendar_checks=calendar_checks,initial_zero_bootstrap=True,
        coverage_inventory=coverage,
        source_engine_unchanged=True,shared_caches_rebuilt=False,diagnostic_script_sha256=H.sha(Path(__file__)),
        shorts='N/A: source long only; random-side null is a benchmark, not a promoted short strategy',
        null_information_set='Cash down/up state and range are known before all random17:02–20:02 entry times',
        calendar='Actual account exit date, including Sunday-stopped trades assigned to Monday; no weekday-entry deletion'))
    print('All frozen diagnostics saved.',flush=True)


if __name__=='__main__':
    if '--coverage-only' in sys.argv:
        import json
        g,days,pc=H.setup()
        ledgers={model:load_ledger(model) for model in MODELS}
        coverage=coverage_audit(g,ledgers)
        checks=json.loads((OUT/'diagnostic_checks.json').read_text())
        checks.update(coverage_inventory=coverage,diagnostic_script_sha256=H.sha(Path(__file__)))
        H.dump('diagnostic_checks.json',checks)
        print('Coverage inventory reconciles every primary held-minute count.')
    else:main()
