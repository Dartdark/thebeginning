"""Aggregate already-priced frozen S30/S47/Kusho ledgers, including daily marks."""
import json

import numpy as np
import pandas as pd

import codex_ingredients_s30_s47_kusho_20261108 as C


def main():
    out = C.OUT
    rows, years, audits = [], [], []
    for family, variants in C.FAMILIES.items():
        for variant in variants:
            stem = family + '__' + variant
            all_trades, all_days = [], {side: [] for side in ('all', 'long', 'short')}
            for phase in ('design', 'recent'):
                receipt = json.loads((out / phase / 'summary.json').read_text())
                C.check(receipt['implementation_gates_passed'] and receipt['rule_cases'] == 20
                        and receipt['script_sha256'] == C.sha(C.ROOT / C.CODE), 'Changed or incomplete frozen phase')
                t = pd.read_csv(out / phase / (stem + '_trades.csv'), parse_dates=['date', 'entry_date', 'exit_date_actual'])
                C.check(np.allclose(t.gross - t.commission - t.slippage, t.net), 'Trade cost identity')
                all_trades.append(t)
                sides = {}
                for side in ('all', 'long', 'short'):
                    d = pd.read_csv(out / phase / (stem + '_' + side + '_daily.csv'), index_col=0, parse_dates=True)
                    sub = t if side == 'all' else t[t.side.eq(1 if side == 'long' else -1)]
                    C.check(abs(d.net.sum() - sub.net.sum()) < .005, 'Side marked ledger mismatch')
                    sides[side] = d
                    all_days[side].append(d)
                C.check(np.allclose(sides['all'].net, sides['long'].net + sides['short'].net), 'Daily side attribution')
                worst = t.loc[t.source_adverse_mark.idxmin()]
                weekend = pd.Series([any(x.dayofweek == 5 for x in pd.date_range(a, b))
                                     for a,b in zip(t.entry_date, t.exit_date_actual)], index=t.index)
                audits.append({'family': family, 'variant': variant, 'phase': phase,
                    'trades': len(t), 'terminal_trades': int(t.terminal.sum()),
                    'worst_mark_entry': str(worst.entry_date.date()),
                    'worst_mark_exit': str(worst.exit_date_actual.date()),
                    'worst_mark': float(worst.source_adverse_mark), 'worst_trade_event_net': float(worst.net),
                    'absent_minutes_on_worst_mark': int(worst.missing_held_bars),
                    'absent_calendar_minutes': int(t.missing_held_bars.sum()),
                    'Sunday_exits': int(t.Sunday_exit.sum()),
                    'weekend_held_trades': int(weekend.sum()), 'weekend_held_trade_net': float(t.loc[weekend, 'net'].sum()),
                    'other_trade_net': float(t.loc[~weekend, 'net'].sum()),
                    'nonpositive_swing_risk': int((t.R_initial.le(0) & t.swing).sum()) if family=='KUSHO' else 0,
                    'BE_armed_trades': int(t.be_done.sum()) if family=='KUSHO' else 0})
            t = pd.concat(all_trades, ignore_index=True)
            for side in ('all', 'long', 'short'):
                d = pd.concat(all_days[side])
                C.check(d.index.is_unique and d.index.is_monotonic_increasing, 'Overlapping era calendars')
                sub = t if side == 'all' else t[t.side.eq(1 if side == 'long' else -1)]
                row = {'family': family, 'variant': variant, 'period': '2018-2026-10-09',
                       'side': side, **C.metrics(sub, d)}
                C.check(abs(row['net_total']-row['trade_net_total']) < .005, 'Whole marked/trade mismatch')
                rows.append(row)
                for year in sorted(set(d.index.year)):
                    years.append({'family': family, 'variant': variant, 'side': side, 'year': year,
                                  **C.metrics(sub[sub.date.dt.year.eq(year)], d[d.index.year==year])})
    whole = pd.DataFrame(rows); yearly = pd.DataFrame(years)
    for (family, variant, side), group in yearly.groupby(['family', 'variant', 'side']):
        q = whole[(whole.family==family) & (whole.variant==variant) & (whole.side==side)]
        C.check(abs(group.net_total.sum() - q.net_total.iloc[0]) < .005, 'Yearly marked totals mismatch')
    whole.to_csv(out / 'whole_metrics.csv', index=False)
    yearly.to_csv(out / 'year_side_metrics.csv', index=False)
    yearly[yearly.variant.eq('original') & yearly.side.eq('all')].to_csv(out/'original_year_metrics.csv', index=False)
    C.B.dump(out/'path_ledger_audit.json', {'all_checks_passed': True, 'cases': audits,
                  'new_market_returns_or_definitions': 0,
                  'absent_minutes_include_scheduled_market_closures': True})
    base = whole[whole.variant.eq('original')]
    print('ORIGINALS, whole history, marked daily P&L')
    print(base[base.side.eq('all')][['family','trades','win','net_total','avg','t_trade','sharpe','sortino',
          'profit_factor','calmar','ulcer','max_dd','exit_booked_dd','terminal_trades']].round(2).to_string(index=False))
    print('ORIGINAL SIDES')
    print(base[base.side.ne('all')][['family','side','trades','net_total','avg','t_trade','profit_factor']].round(2).to_string(index=False))
    print('ORIGINAL MARKED YEARS')
    print(yearly[yearly.variant.eq('original') & yearly.side.eq('all')]
          .pivot(index='year',columns='family',values='net_total').round(2).to_string())
    print('MICRO AND OBSERVED PATHS')
    print(base[base.side.eq('all')][['family','micro_net_total','micro_worst_trade','worst_source_adverse_mark',
          'extra_tick_cost_total']].round(2).to_string(index=False))


if __name__ == '__main__':
    main()
