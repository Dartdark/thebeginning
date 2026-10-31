"""Timestamp-only inventory and analytic power arithmetic; never reads price columns.

Source statistics are author claims, not returns reproduced from owned data.
Run with the repository Python environment from any directory.
"""
from pathlib import Path
import hashlib
import json
import math
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_diversification_feasibility_20261030'
ANNOUNCEMENTS = {
    2018: ['01-29', '04-30', '07-30', '10-29'],
    2019: ['01-28', '04-29', '07-29', '10-28'],
    2020: ['02-03', '05-04', '08-03', '11-02'],
    2021: ['02-01', '05-03', '08-02', '11-01'],
    2022: ['01-31', '05-02', '08-01', '10-31'],
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows, inputs = [], []
    # Table 1, author manuscript July16,2025. All design announcements are Mondays;
    # Friday is the provisional prior business date, not a certified as-of calendar.
    for year, dates in ANNOUNCEMENTS.items():
        path = ROOT / f'data/ZN_1min_{year}.csv'
        frame = pd.read_csv(path, usecols=['date', 'time'])
        inputs.append(dict(path=str(path.relative_to(ROOT)),
                           sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                           columns_read=['date', 'time']))
        for monthday in dates:
            announcement = pd.Timestamp(f'{year}-{monthday}')
            assert announcement.dayofweek == 0
            event = announcement - pd.Timedelta(days=3)
            subset = frame[frame.date == int(event.strftime('%Y%m%d'))]
            clock = subset.time // 100 * 60 + subset.time % 100
            # 07:30ET=06:30CT. Labelled minutes only; no executable fill assertion.
            expected = set(range(390, 960))  # through15:59CT, before Apex flatten.
            present = set(clock.tolist())
            window = clock[(clock >= 390) & (clock <= 959)]
            rows.append(dict(announcement=announcement.date().isoformat(),
                             provisional_event=event.date().isoformat(),
                             timestamp_coverage=len(expected & present) / len(expected),
                             missing_minutes=len(expected - present),
                             duplicate_timestamp_rows=int(window.duplicated().sum()),
                             has_0630=390 in present, has_1559=959 in present))
    coverage = pd.DataFrame(rows)
    coverage.to_csv(OUT / 'treasury_timestamp_census.csv', index=False)
    # Table2:10Y cash bonds,129events1991Q4–2023. Not ZN or a design-period estimate.
    mean, sd, n = 12.62, 43.15, len(coverage)
    summary = dict(
        return_tests_executed=False, price_columns_read=False,
        design_opportunities=n, years=[2018, 2022],
        source_mean_cash_bps=mean, source_sd_cash_bps=sd,
        expected_gross_t_if_source_distribution_transfers=mean / sd * math.sqrt(n),
        gross_mean_cash_bps_needed_for_t2=2 * sd / math.sqrt(n),
        gross_events_needed_for_t2=math.ceil((2 * sd / mean) ** 2),
        # Illustrative calendar scaling:4independent events/year,zero excess off-event.
        illustrative_gross_calendar_sharpe=mean / sd * math.sqrt(4),
        illustrative_gross_calendar_return_pct=4 * mean / 100,
        timestamp_complete_events=int((coverage.missing_minutes == 0).sum()),
        endpoints_present=int((coverage.has_0630 & coverage.has_1559).sum()),
        native_zn_round_trip_fee_scenario_usd=7.25,
        native_zn_slippage_one_tick_each_fill_usd=31.25,
        native_zn_total_cost_scenario_usd=38.50,
        costs_status='Assumed fee scenario, not measured user ZN costs; no cash-bond to ZN return conversion.',
        assumptions=['20independent events;source distribution transfers;no cost deduction in power math',
                     'No statistical power target or promotion claim from expected t alone',
                     'No as-of calendar,contract/roll,bar-label or native fill certification',
                     'Calendar Sharpe is an illustration,not reconstruction of Table5'],
        inputs=inputs,
    )
    assert n == 20
    assert summary['native_zn_total_cost_scenario_usd'] == 7.25 + 2 * 15.625
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'inputs'}, indent=2))


if __name__ == '__main__':
    main()
