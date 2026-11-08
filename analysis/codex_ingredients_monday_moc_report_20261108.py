"""Aggregate the 15 frozen Monday/Bridge/MOC ledgers; no market-price replay."""
import json

import numpy as np
import pandas as pd

import codex_ingredients_monday_moc_20261108 as C


def main():
    out = C.OUT
    whole, yearly, annual, paths = [], [], [], []
    for family, names in C.FAMILIES.items():
        for variant in names:
            trades, calendars = [], []
            stem = family + '__' + variant
            for phase in ('design', 'recent'):
                receipt = json.loads((out / phase / 'summary.json').read_text())
                C.check(receipt['implementation_gates_passed'] and receipt['rule_cases'] == 15,
                        'Unfinished phase or changed candidate count')
                C.check(receipt['script_sha256'] == C.sha(C.ROOT / C.CODE), 'Harness changed')
                t = pd.read_csv(out / phase / (stem + '_trades.csv'), parse_dates=['date'])
                d = pd.read_csv(out / phase / (stem + '_daily.csv'), index_col=0, parse_dates=True).iloc[:, 0]
                C.check(abs(t.net.sum() - d.sum()) < .005, 'Daily ledger does not reconcile')
                C.check(np.allclose(t.gross - t.commission - t.slippage, t.net), 'Cost identity')
                C.check(t.date.is_unique and t.date.is_monotonic_increasing, 'Duplicate or unsorted trades')
                trades.append(t)
                calendars.extend(d.index)
                tail = t.loc[t.source_adverse_mark.idxmin()]
                path = {'family': family, 'variant': variant, 'phase': phase,
                        'worst_mark_date': str(tail.date.date()), 'worst_mark': float(tail.source_adverse_mark),
                        'net_on_worst_mark_trade': float(tail.net),
                        'missing_bars_on_worst_mark_trade': int(tail.missing_held_bars),
                        'missing_bars_total': int(t.missing_held_bars.sum()),
                        'trades_with_missing_bars': int(t.missing_held_bars.gt(0).sum()),
                        'fallback_trades': int(t.last_close_fallback.sum()),
                        'Sunday_exits': int(t.Sunday_exit.sum()),
                        'target_bar_ambiguous_trades': int(t.target_bar_path_ambiguous.sum())}
                if family == 'BR':
                    base = pd.read_csv(out / phase / 'BR__original_trades.csv', parse_dates=['date'])
                    base_dates, case_dates = set(base.date), set(t.date)
                    path['added_vs_original_dates'] = [str(x.date()) for x in sorted(case_dates - base_dates)]
                    path['removed_vs_original_dates'] = [str(x.date()) for x in sorted(base_dates - case_dates)]
                    C.check((t.entry_i_actual // 1440 <= t.day).all(), 'Lost Sunday entry row')
                    C.check((t.exit_i_actual >= t.entry_i_actual).all(), 'Lost actual exit chronology')
                paths.append(path)
            combined = pd.concat(trades, ignore_index=True)
            calendar = pd.DatetimeIndex(calendars)
            C.check(calendar.is_unique and calendar.is_monotonic_increasing, 'Overlapping phase calendars')
            C.check(combined.date.is_unique, 'Overlapping phase trades')
            for side in ('all', 'long', 'short'):
                sub = combined if side == 'all' else combined[combined.side == (1 if side == 'long' else -1)]
                row = {'family': family, 'variant': variant, 'side': side, 'period': '2018-2026-10-09',
                       **C.E.metrics(sub, calendar)}
                whole.append(row)
                year_net = 0.
                for year in sorted(set(calendar.year)):
                    ys = sub[sub.date.dt.year == year]
                    yr = {'family': family, 'variant': variant, 'side': side, 'year': year,
                          **C.E.metrics(ys, calendar[calendar.year == year])}
                    yearly.append(yr)
                    year_net += yr['net_total']
                    if variant == 'original' and side == 'all':
                        annual.append(yr)
                C.check(abs(year_net - row['net_total']) < .005, 'Annual ledger does not reconcile')
    metrics = pd.DataFrame(whole)
    for (family, variant), group in metrics.groupby(['family', 'variant']):
        C.check(abs(group.loc[group.side.eq('all'), 'net_total'].iloc[0]
                    - group.loc[group.side.ne('all'), 'net_total'].sum()) < .005,
                'Long/short totals do not reconcile')
    metrics.to_csv(out / 'whole_metrics.csv', index=False)
    pd.DataFrame(yearly).to_csv(out / 'year_side_metrics.csv', index=False)
    pd.DataFrame(annual).to_csv(out / 'original_year_metrics.csv', index=False)
    C.B.dump(out / 'path_ledger_audit.json', {'all_checks_passed': True, 'cases': paths,
                  'new_returns_or_definitions_computed': False})
    baseline = metrics[metrics.variant.eq('original')]
    print('BASELINES: whole 2018-2026-10-09, fixed one NQ or ES')
    print(baseline[baseline.side.eq('all')][['family', 'trades', 'win', 'avg', 'net_total', 't_trade',
          'sharpe', 'sortino', 'profit_factor', 'calmar', 'ulcer', 'max_dd']].round(2).to_string(index=False))
    print('BASELINE SIDES')
    print(baseline[baseline.side.ne('all')][['family', 'side', 'trades', 'net_total', 'avg',
          't_trade', 'profit_factor']].round(2).to_string(index=False))
    print('BASELINE YEARS')
    print(pd.DataFrame(annual).pivot(index='year', columns='family', values='net_total').round(2).to_string())
    print('BASELINE MICRO AND TAIL SENSITIVITY')
    print(baseline[baseline.side.eq('all')][['family', 'micro_net_total', 'micro_worst_trade',
          'worst_source_adverse_mark', 'extra_tick_cost_total']].round(2).to_string(index=False))


if __name__ == '__main__':
    main()
