"""Input sanity only: counts stale-value runs and duplicate date labels.

No price returns, portfolio selection, performance, predictive tests or fills.
Equal prices can be real; a flat run is a review flag, not proof of imputation.
"""
import csv
import json
import math
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'agents/codex/inputs/scout_20261101/free_daily_panel'


def main():
    summary = {}
    with (INPUT / 'local/tf_system_data_prices.csv').open(newline='') as f:
        reader = csv.DictReader(f)
        datefield = reader.fieldnames[0]
        states = {k: {'prior': None, 'run': 0, 'max_run': 0, 'nonpositive_design_cells': 0,
                      'design_cells': 0, 'nonfinite_cells': 0} for k in reader.fieldnames[1:]}
        for row in reader:
            day = row[datefield][:10]
            if not '2018-01-01' <= day <= '2022-12-31': continue
            for key, state in states.items():
                raw = row[key].strip()
                if not raw:
                    state['prior'], state['run'] = None, 0
                    continue
                value = float(raw)
                if not math.isfinite(value):
                    state['nonfinite_cells'] += 1
                    state['prior'], state['run'] = None, 0
                    continue
                state['design_cells'] += 1
                state['nonpositive_design_cells'] += int(value <= 0)
                state['run'] = state['run'] + 1 if value == state['prior'] else 1
                state['max_run'] = max(state['max_run'], state['run'])
                state['prior'] = value
        summary = {key: {k: v for k, v in s.items() if k not in {'prior', 'run'}}
                   for key, s in states.items()}
    extras = {}
    for name in ['OATIES.csv', 'OJ.csv']:
        counts = Counter()
        designs = Counter()
        fields = None
        with (INPUT / 'local/carver' / name).open(newline='') as f:
            for row in csv.DictReader(f):
                day = row['DATETIME'][:10]
                counts[day] += 1
                if '2018-01-01' <= day <= '2022-12-31':
                    designs[day] += 1
        extras[name] = {'all_unique_date_labels': len(counts),
                        'all_dates_with_multiple_rows': sum(v > 1 for v in counts.values()),
                        'design_unique_date_labels': len(designs),
                        'design_dates_with_multiple_rows': sum(v > 1 for v in designs.values())}
    result = {'scope': 'data quality only,2018–22for price-value checks; no returns',
              'panel': summary, 'additional_contract_files': extras,
              'limitations': 'No official session/holiday, receipt-time, stale-quote or native-roll certification; flat values may be valid. Never choose daily last rows without a verified clock or turn missing prices into zero returns.'}
    out = ROOT / 'analysis/outputs/codex_scout_panel_quality_20261101'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'quality.json').write_text(json.dumps(result, indent=2) + '\n')
    flagged = {k: s for k, s in summary.items() if s['max_run'] >= 10 or s['nonpositive_design_cells']}
    print(json.dumps({'design_quality_flags': flagged, 'additional_contract_files': extras}, indent=2))


if __name__ == '__main__': main()
