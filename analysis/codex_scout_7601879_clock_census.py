"""Inventory ZN raw date/time coverage without loading numeric price columns.

The last observed daytime date is a provisional data endpoint, NOT an authoritative
index calendar or strategy event. Requested late timestamp flags are diagnostic
fields, not expected rebalance bars. No returns, fills or economic selections run.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TIMESTAMPS = (1359, 1459, 1500)


def census(root=ROOT):
    root = Path(root).resolve()
    inventory, months = [], []
    for year in range(2018, 2023):
        path = root / f'data/ZN_1min_{year}.csv'
        frame = pd.read_csv(path, usecols=['date', 'time'],
                            dtype={'date': 'int64', 'time': 'int64'})
        daytime = frame[(frame['time'] >= 721) & (frame['time'] <= 1559)]
        dates = sorted(daytime['date'].unique().tolist())
        last_dates = {}
        for date in dates:
            last_dates[date // 100] = date
        available = set(zip(frame['date'].tolist(), frame['time'].tolist()))
        records = []
        for month, date in sorted(last_dates.items()):
            item = {
                'month': str(month),
                'last_observed_daytime_date': str(date),
                'ordinary_US_index_snapshot_CT_reference': 1400 if date < 20210114 else 1500,
                'raw_timestamp_flags': {str(t): (date, t) in available for t in TIMESTAMPS},
            }
            months.append(item)
            records.append(item)
        inventory.append({
            'path': str(path.relative_to(root)),
            'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'rows_date_time_only': len(frame),
            'daytime_dates': len(dates),
            'observed_months': len(last_dates),
            'raw_endpoint_timestamp_counts': {
                str(t): sum(r['raw_timestamp_flags'][str(t)] for r in records)
                for t in TIMESTAMPS
            },
        })
    missing = [r['last_observed_daytime_date'] for r in months
               if not all(r['raw_timestamp_flags'].values())]
    return {
        'inventory': inventory,
        'month_endpoint_candidates': months,
        'observed_months': len(months),
        'raw_endpoints_with_all_requested_late_timestamps': len(months) - len(missing),
        'raw_endpoints_missing_requested_late_timestamps': missing,
        'calendar_month_ceiling_before_2021_change': 36,
        'calendar_month_ceiling_after_2021_change': 24,
        'numeric_price_columns_loaded': [],
        'environment': {'interpreter': sys.executable, 'pandas': pd.__version__},
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'limits': [
            'Observed last daytime date is not an official index event calendar.',
            'A raw timestamp flag is not proof of an executable fill or a complete window.',
            'No numeric price, volume, return, strategy selection or account calculation is performed.',
            'Raw bar timezone/stamp, holiday/early-close policy, contract IDs and rolls remain unverified.',
            'A date flagged here can be a holiday or early close with a different official index date/time; '
            'these are not counts of missing expected rebalance bars.',
        ],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = census()
    rendered = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding='utf-8')
    print(rendered, end='')
