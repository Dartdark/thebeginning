"""Frozen Sunday Opening design screen. Preregistration 2378ca3; no 2023+ returns.

Uses existing Grid24/cache, repository metrics; custom walker is necessary for
source close entries, next-open time exits and conservative same-minute ordering.
"""
import hashlib
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'analysis'))
import metrics as M
from codex_sunday_opening_inventory import inventory

OUT = ROOT / 'analysis/outputs/codex_sunday_opening'
PREREG = '2378ca37c244fcc7bc68dd0ccd8901555bc6c567'


def replay(g, row, close_fill=False, ticks=1, legacy=False):
    """One frozen long; one-point target trade-through, stop-first ambiguity.

    Tick slippage changes actual entry and bracket anchors, rather than being
    charged twice or silently ignored in stop/target levels.
    """
    d = row['row']
    decision = row['first_eligible_flat_index'] - d * 1440
    o, h, l, c = (getattr(g, k)[d] for k in ('o', 'h', 'l', 'c'))
    present = np.flatnonzero(np.isfinite(c) & np.isfinite(o) & np.isfinite(h) & np.isfinite(l))
    after = present[present > decision]
    if not len(after):
        return dict(date=row['date'], status='unresolved_no_entry_bar')
    entry_j = decision if close_fill else int(after[0])
    raw_entry = c[decision] if close_fill else o[entry_j]
    slip_pts = ticks * .25
    entry = raw_entry + slip_pts
    stop, target = entry - 80, entry + 50
    thresholds = present[present >= 19 * 60 + 12]
    time_decision = int(thresholds[0]) if len(thresholds) else None
    if entry_j >= (time_decision if time_decision is not None else 19*60+12):
        return dict(date=row['date'], status='unresolved_entry_at_or_after_exit_threshold')
    exit_candidates = present[present > time_decision] if time_decision is not None else np.array([],dtype=int)
    time_fill = time_decision if close_fill else (int(exit_candidates[0]) if len(exit_candidates) else None)
    # For next-open time exit, prior brackets remain active until that open;
    # scheduled time exit then takes precedence over the rest of its minute.
    scan = present[(present > decision if close_fill else present >= entry_j) & (present <= time_fill if time_fill is not None else True)]
    raw_exit = None
    kind = None
    ambiguous = False
    for j in scan:
        if not close_fill and time_fill is not None and j == time_fill:
            raw_exit, kind = o[j], 'time'
            break
        hit_s = l[j] <= stop
        hit_t = h[j] >= target + 1.0
        if hit_s:
            raw_exit, kind = min(o[j], stop), 'stop'
            ambiguous = bool(hit_t)
            break
        if hit_t:
            raw_exit, kind = max(o[j], target), 'target'
            break
        if close_fill and time_fill is not None and j == time_fill:
            raw_exit, kind = c[j], 'time'
            break
    if raw_exit is None:
        return dict(date=row['date'], status='unresolved_no_exit_decision_or_fill')
    exit_j = int(j)
    pv, fee = (20., 7.25) if legacy else (2., 1.04)
    exit_slip = slip_pts if kind != 'target' else 0.
    gross = (raw_exit - raw_entry) * pv
    slips = (slip_pts + exit_slip) * pv
    net = gross - slips - fee
    start_check = decision + 1 if close_fill else entry_j
    missing = int(np.sum(~(np.isfinite(o[start_check:exit_j + 1]) & np.isfinite(h[start_check:exit_j + 1]) & np.isfinite(l[start_check:exit_j + 1]) & np.isfinite(c[start_check:exit_j + 1]))))
    mult = 1 if legacy else 10
    return dict(date=row['date'], account_date=str((pd.Timestamp(row['date']) + pd.Timedelta(days=1)).date()),
                status='observed_path_estimate', side=1, decision_j=int(decision), entry_j=int(entry_j),
                exit_j=exit_j, raw_entry=float(raw_entry), entry_fill=float(entry),
                entry_missing_minutes_before_fill=0 if close_fill else int(entry_j-decision-1),
                time_exit_threshold_delay_minutes=None if kind!='time' else int(time_decision-(19*60+12)),
                time_exit_missing_minutes_before_fill=None if kind!='time' or close_fill else int(exit_j-time_decision-1),
                raw_exit=float(raw_exit), exit_fill=float(raw_exit-exit_slip),
                stop=float(stop), target=float(target), kind=kind, ambiguous=ambiguous,
                missing_holding_minutes=missing,
                missing_full_window=row['entry_to_1912_expected_minutes']-row['entry_to_1912_present_minutes'],
                gross_nq=float(gross*mult), slippage_nq=float(slips*mult), commission_nq=float(fee*mult),
                net_nq=float(net*mult), net_mnq=float(net/pv*2), down=row['source_week_filter_down'],
                prior_week_change_pct=row['source_week_change_pct'])


def daily_table(t, index):
    x = t.groupby('account_date').net_nq.sum()
    x.index = pd.to_datetime(x.index)
    return x.reindex(index, fill_value=0.)


def stats(t, index):
    if t.empty:
        return {'trades': 0}
    x = t.net_nq
    daily = daily_table(t, index)
    assert abs(daily.sum()-x.sum()) < 1e-7
    p = M.perf(daily, x)
    p.update(total=float(x.sum()), gross_mean=float(t.gross_nq.mean()),
             costs_mean=float((t.slippage_nq+t.commission_nq).mean()),
             t=float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))) if len(x)>1 and x.std()>0 else None,
             years={str(y): {'trades':len(a),'total':float(a.net_nq.sum()),'mean':float(a.net_nq.mean())}
                    for y,a in t.groupby(pd.to_datetime(t.date).dt.year)},
             exit_kinds=t.kind.value_counts().to_dict(),
             ambiguous_minutes=int(t.ambiguous.sum()), missing_holding_trades=int((t.missing_holding_minutes>0).sum()),
             first_date=t.date.min(), last_date=t.date.max())
    return p


def random_removals(all_t, primary, index):
    rng = np.random.default_rng(261026)
    totals, dds = [], []
    yr = pd.to_datetime(all_t.date).dt.year
    desired = pd.to_datetime(primary.date).dt.year.value_counts()
    for _ in range(1000):
        chosen=[]
        for y,n in desired.items():
            pool=all_t.index[yr == y].to_numpy()
            chosen.extend(rng.choice(pool, int(n), replace=False).tolist())
        sample=all_t.loc[chosen].sort_values('date')
        x=daily_table(sample,index).to_numpy()
        equity=np.r_[0.,np.cumsum(x)]
        totals.append(float(x.sum()))
        dds.append(float(np.max(np.maximum.accumulate(equity)-equity)))
    x=daily_table(primary,index).to_numpy()
    equity=np.r_[0.,np.cumsum(x)]
    actual_dd=float(np.max(np.maximum.accumulate(equity)-equity))
    return dict(draws=1000, seed=261026,
                profit_fraction_beaten=float(np.mean(primary.net_nq.sum()>np.array(totals))),
                drawdown_fraction_beaten=float(np.mean(actual_dd<np.array(dds))),
                profit_plus_one_p=float((1+np.sum(np.array(totals)>=primary.net_nq.sum()))/1001),
                drawdown_plus_one_p=float((1+np.sum(np.array(dds)<=actual_dd))/1001),
                actual_total=float(primary.net_nq.sum()), actual_maxdd=actual_dd,
                random_total_p5_p50_p95=np.quantile(totals,[.05,.5,.95]).tolist(),
                random_maxdd_p5_p50_p95=np.quantile(dds,[.05,.5,.95]).tolist())


def main():
    with (ROOT/'scratch_data/g24.pkl').open('rb') as f:
        g=pickle.load(f)
    inv=inventory(g)
    # Crucial: filter BEFORE walking any candidate forward path.
    rows=[r for r in inv['rows'] if '2018-01-01'<=r['date']<'2023-01-01' and r['source_week_change_pct'] is not None]
    index=pd.DatetimeIndex(g.ts[g.trading])
    index=index[(index>='2018-01-01') & (index<='2022-12-31')]
    configs={'V0_source_close':(True,1,True,'down'),
             'V1_primary':(False,1,False,'down'),
             'V2_extra_tick':(False,2,False,'down'),
             'V3_all_sundays':(False,1,False,'all'),
             'V4_removed_up_weeks':(False,1,False,'up')}
    tables={}; results={}; unresolved={}
    OUT.mkdir(parents=True,exist_ok=True)
    for name,(close,ticks,legacy,which) in configs.items():
        eligible=[r for r in rows if which=='all' or r['source_week_filter_down']==(which=='down')]
        walked=[replay(g,r,close,ticks,legacy) for r in eligible]
        unresolved[name]=[r for r in walked if r['status']!='observed_path_estimate']
        t=pd.DataFrame([r for r in walked if r['status']=='observed_path_estimate'])
        t=t.sort_values('date').reset_index(drop=True)
        tables[name]=t
        results[name]=stats(t,index)
        t.to_csv(OUT/(name+'_design_trades.csv'),index=False)
    p=tables['V1_primary']; control=tables['V3_all_sundays']; rem=tables['V4_removed_up_weeks']
    placebo=random_removals(control,p,index)
    s=results['V1_primary']
    first=float(p.loc[p.date<'2021-01-01','net_nq'].sum())
    last=float(p.loc[p.date>='2021-01-01','net_nq'].sum())
    gates=dict(minimum_80_trades=len(p)>=80, positive_net=s['total']>0,
               t_at_least_2=s['t'] is not None and s['t']>=2, pf_at_least_1_20=s['profit_factor']>=1.2,
               both_subperiods_positive=first>0 and last>0,
               extra_tick_positive=results['V2_extra_tick']['total']>0,
               removed_mean_negative=float(rem.net_nq.mean())<0,
               beats_95pct_random_drops_profit=placebo['profit_fraction_beaten']>=.95,
               beats_95pct_random_drops_drawdown=placebo['drawdown_fraction_beaten']>=.95)
    result=dict(preregistration_commit=PREREG, source_sha256=hashlib.sha256((ROOT/'agents/codex/inputs/sunday_opening/Sunday_Opening.txt').read_bytes()).hexdigest(),
                design_start='2018-01-01',design_end='2022-12-31',return_configurations=5,
                placebo_draws=1000,holdout_returns_computed=False,
                inventory_design=inv['summary_design_2018_22'],metrics=results,unresolved=unresolved,
                primary_subperiod_total={'2018_20':first,'2021_22':last},random_removals=placebo,gates=gates,
                design_pass=all(gates.values()),promotion_blockers=['No MultiCharts parity or parameter-search provenance supplied',
                'Minute OHLC cannot establish fills during unobserved intervals; any actual holding gaps require audit'],
                short_side='N/A: submitted defaults are long-only',
                account_status={k:('NOT RUN: preregistered design gate failed' if not all(gates.values()) else 'PENDING: design passed; coverage/parity and conditional validation remain') for k in ['50K evaluation','150K evaluation','50K funded','150K funded','personal ladder/full']})
    (OUT/'design_summary.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    pd.DataFrame(results).T.to_csv(OUT/'design_metrics.csv')
    print(json.dumps({'primary':s,'source_close':results['V0_source_close'], 'removed':results['V4_removed_up_weeks'],
                      'gates':gates,'placebo':placebo,'design_pass':all(gates.values())},indent=2))
    if all(gates.values()):
        print('DESIGN PASSES: conditional holdout/account phase remains to be implemented; not yet cleared.')
    else:
        print('STOP: design gate failed; 2023+ returns and all five account destinations not run.')


if __name__ == '__main__':
    main()
