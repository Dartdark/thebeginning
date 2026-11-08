"""Aggregate the frozen event-ingredient ledgers; no signal or market-data replay."""
import pandas as pd
import codex_ingredients_events_20261108 as E


def main():
    out = E.OUT
    whole, yearly, baseline, annual = [], [], [], []
    for family in ('EOS', 'NFP', 'CL'):
        names = ['original', 'opposite_direction', 'no_stop']
        names += {'EOS': ['no_expiry_gate', 'exit_0900'],
                  'NFP': ['no_spike_gate', 'no_payroll_calendar'],
                  'CL': ['no_upgap_gate', 'exit_0300']}[family]
        for variant in names:
            stem = family + '__' + variant
            trades, days = [], []
            for phase in ('design', 'recent'):
                t = pd.read_csv(out / phase / (stem + '_trades.csv'), parse_dates=['date'])
                d = pd.read_csv(out / phase / (stem + '_daily.csv'), index_col=0, parse_dates=True).iloc[:, 0]
                E.check(abs(t.net.sum() - d.sum()) < .005, 'Daily ledger aggregation mismatch')
                trades.append(t)
                days.extend(d.index)
            t = pd.concat(trades, ignore_index=True)
            calendar = pd.DatetimeIndex(days)
            E.check(calendar.is_unique and calendar.is_monotonic_increasing, 'Combined calendar overlaps')
            for side in ('all', 'long', 'short'):
                sub = t if side == 'all' else t[t.side == (1 if side == 'long' else -1)]
                row = {'family': family, 'variant': variant, 'side': side, 'period': '2018-2026-10-09',
                       **E.metrics(sub, calendar)}
                whole.append(row)
                if variant == 'original':
                    baseline.append(row)
                for year in sorted(set(calendar.year)):
                    ys = sub[sub.date.dt.year == year]
                    yr = {'family': family, 'variant': variant, 'side': side, 'year': year,
                          **E.metrics(ys, calendar[calendar.year == year])}
                    yearly.append(yr)
                    if variant == 'original' and side == 'all':
                        annual.append(yr)
    pd.DataFrame(whole).to_csv(out / 'whole_metrics.csv', index=False)
    pd.DataFrame(yearly).to_csv(out / 'year_side_metrics.csv', index=False)
    pd.DataFrame(annual).to_csv(out / 'original_year_metrics.csv', index=False)
    print('BASELINES, WHOLE HISTORY')
    print(pd.DataFrame(baseline).query("side=='all'")
          [['family', 'trades', 'win', 'avg', 'net_total', 't_trade', 'sharpe', 'sortino', 'profit_factor', 'calmar', 'ulcer', 'max_dd']].round(2).to_string(index=False))
    print('BASELINE SIDES')
    print(pd.DataFrame(baseline).query("side!='all'")
          [['family', 'side', 'trades', 'net_total', 'avg', 't_trade', 'profit_factor']].round(2).to_string(index=False))
    print('BASELINE YEARS')
    print(pd.DataFrame(annual).pivot(index='year', columns='family', values='net_total').round(2).to_string())
    print('ORIGINAL MICRO TOTALS AND MODELED TAILS')
    print(pd.DataFrame(baseline).query("side=='all'")
          [['family', 'micro_net_total', 'micro_worst_trade', 'worst_source_adverse_mark']].round(2).to_string(index=False))


if __name__ == '__main__':
    main()
