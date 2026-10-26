"""No-return coverage/session-state audit of uploaded Sunday_Opening.txt.

This module must not compute trade returns or forward excursions. It follows the
source's modulo-clock reset, including its treatment of sparse/missing sessions.
"""
import argparse
import hashlib
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'analysis'))


def timestamp(g, flat_index):
    """Actual 1-minute close stamp in the cached calendar-date grid (CT)."""
    d, m = divmod(int(flat_index), 1440)
    return (pd.Timestamp(g.ts[d]) + pd.Timedelta(minutes=m)).isoformat()


def inventory(g):
    closes = np.asarray(g.c).ravel()
    valid = np.flatnonzero(np.isfinite(closes))
    minute = valid % 1440
    sm = (minute - 1020 + 1440) % 1440
    # Source initial SMPrev=-1 is a reset without storing a prior close.
    edges = np.r_[0, np.flatnonzero(np.diff(sm) < 0) + 1]
    edge_flat = valid[edges]
    dates = pd.DatetimeIndex(g.ts)
    sunday_days = np.flatnonzero(dates.dayofweek == 6)
    rows = []
    for d in sunday_days:
        if dates[d] < pd.Timestamp('2018-01-01'):
            continue
        window = np.arange(d * 1440 + 17 * 60 + 17, d * 1440 + 17 * 60 + 23)
        candidate = window[np.isfinite(closes[window])]
        first = int(candidate[0]) if len(candidate) else None
        row = dict(date=dates[d].date().isoformat(), row=int(d),
                   exact_1717_present=bool(np.isfinite(closes[d * 1440 + 17 * 60 + 17])),
                   exact_1912_present=bool(np.isfinite(closes[d * 1440 + 19 * 60 + 12])),
                   entry_window_has_bar=first is not None,
                   first_eligible_flat_index=first,
                   first_eligible_close=timestamp(g, first) if first is not None else None,
                   source_num_sessions=None, source_week_change_pct=None,
                   source_week_filter_down=False, source_week_filter_up=False,
                   session_boundary=None, source_close_timestamps=[],
                   entry_to_1912_present_minutes=0, entry_to_1912_expected_minutes=0)
        if first is not None:
            # Current reset has already shifted SC before the entry is evaluated.
            si = int(np.searchsorted(edge_flat, first, side='right') - 1)
            row['source_num_sessions'] = si
            row['session_boundary'] = timestamp(g, edge_flat[si])
            if si >= 6:
                ends = valid[edges[np.arange(si, si - 6, -1)] - 1]
                sc0, sc5 = closes[ends[0]], closes[ends[-1]]
                row['source_close_timestamps'] = [timestamp(g, v) for v in ends]
                if sc5 > 0:
                    row['source_week_change_pct'] = float((sc0 - sc5) / sc5 * 100)
                    row['source_week_filter_down'] = bool(sc0 <= sc5)
                    row['source_week_filter_up'] = bool(sc0 > sc5)
            last = d * 1440 + 19 * 60 + 12
            row['entry_to_1912_expected_minutes'] = int(last - first + 1)
            row['entry_to_1912_present_minutes'] = int(np.isfinite(closes[first:last + 1]).sum())
        rows.append(row)

    def summary(subset):
        entrants = [r for r in subset if r['entry_window_has_bar']]
        eligible = [r for r in entrants if r['source_week_filter_down']]
        return dict(sundays=len(subset), entry_window_has_bar=len(entrants),
                    missing_entry_window=sum(not r['entry_window_has_bar'] for r in subset),
                    warmup_available=sum(r['source_week_change_pct'] is not None for r in entrants),
                    source_down_week_eligible=len(eligible),
                    source_up_week_eligible=sum(r['source_week_filter_up'] for r in entrants),
                    missing_exact_1717=sum(not r['exact_1717_present'] for r in entrants),
                    missing_exact_1912=sum(not r['exact_1912_present'] for r in entrants),
                    down_week_missing_exact_1912=sum(not r['exact_1912_present'] for r in eligible),
                    down_week_incomplete_entry_to_exit_window=sum(
                        r['entry_to_1912_present_minutes'] != r['entry_to_1912_expected_minutes'] for r in eligible))

    odd_edges = [int(e) for e in edges[1:] if valid[e] % 1440 not in (1020, 1021)]
    # A missing session can cross an unobserved wrap but not trigger the source
    # because the new modulo clock is equal to or above the preceding one.
    clock_aliases = np.flatnonzero((np.diff(valid) > 1440) & (np.diff(sm) >= 0))
    boundary_rows = []
    for r in rows:
        if not r['source_close_timestamps']:
            continue
        # These are descriptive timestamps, not a rewritten weekly filter.
        t0, t5 = pd.Timestamp(r['source_close_timestamps'][0]), pd.Timestamp(r['source_close_timestamps'][5])
        if t0.dayofweek != 4 or t5.dayofweek != 4 or (t0.normalize() - t5.normalize()).days != 7:
            boundary_rows.append(dict(date=r['date'], sc0=r['source_close_timestamps'][0],
                                      sc5=r['source_close_timestamps'][5],
                                      source_week_filter_down=r['source_week_filter_down']))
    return dict(kind='No-return session/coverage inventory', return_trials=0,
                clock='CT; cache bars are close-stamped', actual_bar_count=len(valid),
                initial_bar=timestamp(g, valid[0]), final_bar=timestamp(g, valid[-1]),
                source_session_resets=len(edges),
                summary_all=summary(rows),
                summary_design_2018_22=summary([r for r in rows if r['date'] < '2023-01-01']),
                summary_2023_plus=summary([r for r in rows if r['date'] >= '2023-01-01']),
                by_year={str(y): summary([r for r in rows if r['date'].startswith(str(y))])
                         for y in sorted({int(r['date'][:4]) for r in rows})},
                unusual_reset_count=len(odd_edges),
                unusual_reset_examples=[dict(previous=timestamp(g, valid[e - 1]), current=timestamp(g, valid[e])) for e in odd_edges[:30]],
                greater_than_day_gap_without_reset_count=len(clock_aliases),
                greater_than_day_gap_without_reset_examples=[dict(previous=timestamp(g, valid[e]), current=timestamp(g, valid[e+1])) for e in clock_aliases[:30]],
                sunday_filter_non_friday_to_friday=boundary_rows,
                rows=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', default=str(ROOT / 'scratch_data/g24.pkl'))
    parser.add_argument('--output', default=str(ROOT / 'analysis/outputs/codex_sunday_opening/inventory.json'))
    args = parser.parse_args()
    cache = Path(args.cache)
    with cache.open('rb') as f:
        g = pickle.load(f)
    result = inventory(g)
    result['cache'] = dict(path=str(cache), bytes=cache.stat().st_size,
                           sha256=hashlib.file_digest(cache.open('rb'), 'sha256').hexdigest())
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in {'rows', 'sunday_filter_non_friday_to_friday'}}, indent=2))
    print('non_calendar_week_filter_sundays:', len(result['sunday_filter_non_friday_to_friday']))


if __name__ == '__main__':
    main()
