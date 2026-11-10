"""Gold crowding: source QA and no-return census. Economic modes require a later committed plan."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar, GoodFriday

from grid24 import Grid24, jof

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'agents/codex/inputs/gold_crowding_20261110'
OUTPUT = ROOT / 'analysis/outputs/codex_gold_crowding_20261110'
SETTINGS = dict(rank_reports=52, crowding_percentile=.80, max_age_days=14,
                signal_start=720, signal_end=1100, hold_minutes=30,
                reference_min_coverage=.95, roll_jump_atr=.25,
                min_events=40, min_report_clusters=20,
                minimum_30day_any_opportunity_fraction=.25,
                assumed_30min_sd_atr=.12, assumed_gross_effect_atr=.10,
                mgc_point_value=10., tick=.1, fee_roundtrip=3.,
                primary_slippage_ticks_per_fill=1, stress_slippage_ticks_per_fill=2,
                stop_atr=.25, stop_min_oz=.5, stop_max_oz=8., size_mgc=1)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, default=str, allow_nan=False) + '\n')


def positions():
    p = pd.DataFrame(json.loads((INPUT / 'gold_disagg_design.json').read_text()))
    p['observation'] = pd.to_datetime(p.report_date)
    p = p.sort_values('observation').reset_index(drop=True)
    assert p.observation.max() < pd.Timestamp('2023-01-01')
    assert not p.observation.duplicated().any()
    for k in ['open_interest', 'mm_long', 'mm_short', 'mm_spread']:
        assert (p[k] >= 0).all() and np.isfinite(p[k]).all()
    assert (p.open_interest > 0).all()
    assert ((p.mm_long + p.mm_spread) <= p.open_interest).all()
    assert ((p.mm_short + p.mm_spread) <= p.open_interest).all()
    hol = set(USFederalHolidayCalendar().holidays('2016-01-01', '2022-12-31'))
    hol |= set(GoodFriday.dates('2016-01-01', '2022-12-31'))
    hol.add(pd.Timestamp('2018-12-05'))
    flags = []
    for d in p.observation:
        mon = d - pd.Timedelta(days=d.weekday())
        exceptional = pd.Timestamp('2018-12-24') <= d <= pd.Timestamp('2019-03-26')
        holiday_week = any(mon + pd.Timedelta(days=i) in hol for i in range(5))
        flags.append(d.weekday() == 1 and not exceptional and not holiday_week)
    p['ordinary_admitted'] = flags
    p['net_oi'] = (p.mm_long - p.mm_short) / p.open_interest
    p['rank'] = np.nan
    p['available_at'] = pd.NaT
    earlier = []
    for i, row in p.iterrows():
        if not row.ordinary_admitted:
            continue
        # Each admitted report becomes usable after the ordinary release + one hour.
        pub = (row.observation + pd.Timedelta(days=3, hours=16, minutes=30))
        p.loc[i, 'available_at'] = pub
        if len(earlier) >= SETTINGS['rank_reports']:
            window = np.asarray(earlier[-SETTINGS['rank_reports']:])
            p.loc[i, 'rank'] = float(np.mean(window <= row.net_oi))
        earlier.append(row.net_oi)
    # available_at is an Eastern wall-clock timestamp; attach TZ only at the merge.
    return p


def source_audit(p):
    legacy = []
    paths = []
    for year in range(2017, 2023):
        path = ROOT / f'data/cot/deacot{year}.zip'
        paths.append(path)
        with zipfile.ZipFile(path) as z:
            d = pd.read_csv(z.open(z.namelist()[0]), dtype=str, low_memory=False)
        d = d[d.iloc[:, 3].str.strip().eq('088691')]
        for row in d.itertuples(index=False, name=None):
            legacy.append(dict(observation=pd.Timestamp(row[2]), legacy_oi=int(row[7])))
    q = p.merge(pd.DataFrame(legacy), on='observation', how='inner', validate='one_to_one')
    assert (q.open_interest == q.legacy_oi).all()
    sample = p[p.report_date.eq('2018-07-17')].iloc[0]
    expected = dict(open_interest=528278, mm_long=107775, mm_short=134224, mm_spread=51880)
    assert all(int(sample[k]) == v for k, v in expected.items())
    return dict(position_rows=len(p), position_start=str(p.observation.min().date()),
                position_end=str(p.observation.max().date()),
                ordinary_admitted_reports=int(p.ordinary_admitted.sum()),
                reports_with_rank=int(p['rank'].notna().sum()),
                legacy_overlap_rows=len(q), legacy_oi_mismatches=0,
                official_sample_date='2018-07-17', official_sample=expected,
                original_vintages_verified=False,
                input_hashes={str(x.relative_to(ROOT)): sha(x) for x in paths + [INPUT / 'gold_disagg_design.json']})


def load_design():
    # Do not use the shared all-year cache or import a script with top-level tests.
    pattern = 'GC_1min_20[12][012789].csv'
    assert sorted(x.name for x in (ROOT / 'data').glob(pattern)) == [f'GC_1min_{y}.csv' for y in range(2017, 2023)]
    return Grid24(str(ROOT / 'data' / pattern), night_pattern='')


def collect_census(g, p):
    assert pd.Timestamp(g.ts[-1]) < pd.Timestamp('2023-01-01')
    atr = g.daily_atr(15)
    flat = {k: getattr(g, k).ravel() for k in ['o', 'h', 'l', 'c']}
    obs = p[p.ordinary_admitted & p['rank'].notna()].copy()
    obs['utc_available'] = pd.DatetimeIndex(obs.available_at).tz_localize('America/New_York').tz_convert('UTC')
    records, days, exclusions = [], [], {}

    def excluded(reason):
        exclusions[reason] = exclusions.get(reason, 0) + 1

    previous = None
    for r in g.trading:
        d = pd.Timestamp(g.ts[r])
        prev_r, previous = previous, int(r)
        if d < pd.Timestamp('2018-01-01'):
            continue
        days.append(d)
        if pd.Timestamp('2018-12-22') <= d <= pd.Timestamp('2019-03-31'):
            excluded('shutdown_uncertain_trade_date'); continue
        known = (d + pd.Timedelta(hours=7, minutes=20)).tz_localize('America/Chicago').tz_convert('UTC')
        reports = obs[obs.utc_available <= known]
        if reports.empty:
            excluded('rank_warmup_or_no_admitted_report'); continue
        report = reports.iloc[-1]
        age = (d - report.observation).days
        if age > SETTINGS['max_age_days']:
            excluded('report_too_old'); continue
        if prev_r is None or prev_r == 0 or not np.isfinite(atr[r]):
            excluded('reference_or_atr_missing'); continue
        start = (prev_r - 1) * 1440 + jof(1701)
        end = prev_r * 1440 + jof(1559)
        ref_h, ref_l, ref_c = flat['h'][start:end + 1], flat['l'][start:end + 1], flat['c'][start:end + 1]
        coverage = float(np.isfinite(ref_c).mean())
        if coverage < SETTINGS['reference_min_coverage'] or not np.isfinite(ref_c[-1]):
            excluded('reference_session_incomplete'); continue
        level = float(np.nanmin(ref_l))
        first, last = jof(SETTINGS['signal_start']), jof(SETTINGS['signal_end'])
        crossing = np.isfinite(g.c[r, first:last + 1]) & np.isfinite(g.c[r, first - 1:last])
        crossing &= (g.c[r, first:last + 1] < level - 1e-8) & (g.c[r, first - 1:last] >= level - 1e-8)
        js = np.flatnonzero(crossing)
        if not len(js):
            excluded('no_downside_cross'); continue
        trigger = first + int(js[0])
        # Reject suspect continuous-roll discontinuities already observable by decision time.
        stop_i = r * 1440 + trigger
        ii = np.arange(max(1, start), stop_i + 1)
        clock = ii % 1440
        roll_clock = (clock == jof(332)) | (clock == jof(1701))
        jumps = np.abs(flat['o'][ii] - flat['c'][ii - 1]) > SETTINGS['roll_jump_atr'] * atr[r]
        if np.any(roll_clock & jumps):
            excluded('suspect_reference_roll_jump'); continue
        entry = trigger + 1
        exit_j = entry + SETTINGS['hold_minutes']
        # Planned full path, plus a one-minute latency stress: completeness only, no returns.
        held = slice(entry, exit_j + 2)
        if any(not np.isfinite(getattr(g, k)[r, held]).all() for k in ['o', 'h', 'l', 'c']):
            excluded('planned_path_incomplete'); continue
        records.append(dict(date=d, row=int(r), trigger_j=trigger, entry_j=entry, exit_j=exit_j,
                            report_date=report.observation, available_at=report.utc_available,
                            report_age_days=age, net_oi=report.net_oi, rank=report['rank'],
                            crowded=bool(report['rank'] >= SETTINGS['crowding_percentile']),
                            reference_low=level, reference_coverage=coverage, atr=float(atr[r])))
    events = pd.DataFrame(records)
    assert not events.date.duplicated().any()
    crowded = events[events.crowded]
    eligible_days = pd.DatetimeIndex(days)
    counts = []
    for d in eligible_days:
        end = d + pd.Timedelta(days=30)
        if end > eligible_days.max():
            continue
        counts.append(int(((crowded.date >= d) & (crowded.date < end)).sum()))
    # Prior-assumption power arithmetic, not an empirical estimate of return variance.
    n = len(crowded)
    nw = crowded.report_date.nunique()
    independent_unit_hurdle = 2 * SETTINGS['assumed_30min_sd_atr'] / np.sqrt(max(nw, 1))
    cost = SETTINGS['fee_roundtrip'] + 2 * SETTINGS['tick'] * SETTINGS['mgc_point_value']
    cost_atr = cost / (crowded.atr.median() * SETTINGS['mgc_point_value']) if n else None
    expected_fraction = float(np.mean(np.asarray(counts) > 0)) if counts else 0.
    gates = dict(enough_events=n >= SETTINGS['min_events'],
                 enough_report_clusters=nw >= SETTINGS['min_report_clusters'],
                 plausible_assumed_power=bool(n and independent_unit_hurdle + cost_atr <= SETTINGS['assumed_gross_effect_atr']),
                 enough_30day_opportunities=expected_fraction >= SETTINGS['minimum_30day_any_opportunity_fraction'])
    return events, dict(settings=SETTINGS, trading_days=len(days), base_events=len(events), crowded_events=n,
                        independent_report_clusters=int(nw), excluded_days=exclusions,
                        crowded_events_by_year={str(k): int(v) for k, v in crowded.groupby(crowded.date.dt.year).size().items()},
                        windows_30calendar_days=len(counts), fraction_windows_with_event=expected_fraction,
                        median_events_per_window=float(np.median(counts)) if counts else 0.,
                        assumed_sd_atr=SETTINGS['assumed_30min_sd_atr'],
                        assumed_effect_gross_atr=SETTINGS['assumed_gross_effect_atr'],
                        required_net_mean_atr_report_cluster=float(independent_unit_hurdle),
                        assumed_cost_atr_at_median_entry_atr=cost_atr, gates=gates,
                        count_gate_pass=bool(all(gates.values())), economic_returns_computed=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['audit', 'census'], required=True)
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    p = positions()
    audit = source_audit(p)
    write_json(OUTPUT / 'data_audit.json', audit)
    p.to_csv(OUTPUT / 'position_states_design.csv', index=False)
    if args.mode == 'audit':
        print(json.dumps(audit, indent=2)); return
    print('Loading GC 2017–22 only for a no-return census.', flush=True)
    g = load_design()
    events, summary = collect_census(g, p)
    summary['git_head'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    summary['script_sha256'] = sha(__file__)
    summary['price_hashes'] = {str(x.relative_to(ROOT)): sha(x) for x in sorted((ROOT / 'data').glob('GC_1min_20[12][012789].csv'))}
    events.to_csv(OUTPUT / 'event_census_design.csv', index=False)
    write_json(OUTPUT / 'census.json', summary)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
