"""Check the gold no-return census clock, rank and source invariants; never compute P&L."""
from __future__ import annotations

import json
import subprocess

import numpy as np
import pandas as pd

import codex_gold_crowding_20261110 as study


def main():
    out = study.OUTPUT
    p = pd.read_csv(out / 'position_states_design.csv', parse_dates=['observation', 'available_at'])
    e = pd.read_csv(out / 'event_census_design.csv', parse_dates=['date', 'report_date', 'available_at'])
    summary = json.loads((out / 'census.json').read_text())
    checks = {}
    checks['one_event_per_date'] = bool(not e.date.duplicated().any())
    checks['design_only'] = bool((e.date.dt.year.between(2018, 2022)).all())
    decision = pd.DatetimeIndex(e.date + pd.to_timedelta(e.trigger_j, unit='m')).tz_localize('America/Chicago').tz_convert('UTC')
    available = pd.DatetimeIndex(e.available_at).tz_convert('UTC')
    checks['publication_plus_buffer_precedes_decision'] = bool((available <= decision).all())
    checks['report_age_bounded'] = bool(((e.date - e.report_date).dt.days == e.report_age_days).all() and e.report_age_days.between(0, 14).all())
    checks['crowding_matches_frozen_threshold'] = bool((e.crowded == e['rank'].ge(.80)).all())
    checks['entry_after_trigger_next_bar'] = bool((e.entry_j == e.trigger_j + 1).all())
    checks['planned_horizon_30minutes'] = bool((e.exit_j == e.entry_j + 30).all())
    checks['trigger_in_frozen_window'] = bool(e.trigger_j.between(study.jof(720), study.jof(1100)).all())
    checks['corrected_gold_row_never_admitted'] = bool(not p.loc[p.report_date.eq('2019-03-26'), 'ordinary_admitted'].any())
    checks['juneteenth_delayed_row_never_admitted'] = bool(not p.loc[p.report_date.eq('2021-06-15'), 'ordinary_admitted'].any())
    checks['shutdown_trade_blackout'] = bool(not e.date.between('2018-12-22', '2019-03-31').any())
    checks['only_tuesday_observations_admitted'] = bool(p.loc[p.ordinary_admitted, 'observation'].dt.weekday.eq(1).all())
    admitted = p[p.ordinary_admitted].reset_index(drop=True)
    exact = True
    for i, row in admitted.iterrows():
        if i < 52:
            exact &= bool(pd.isna(row['rank']))
            continue
        expected = np.mean(admitted.net_oi.iloc[i-52:i].to_numpy() <= row.net_oi)
        exact &= bool(np.isclose(expected, row['rank'], atol=1e-12))
    checks['every_rank_recomputed_from_52_prior_admitted_reports'] = exact
    checks['census_counts_reconcile'] = bool(len(e) == summary['base_events'] and int(e.crowded.sum()) == summary['crowded_events'])
    checks['failed_gate_stays_failed'] = bool(not summary['count_gate_pass'] and not all(summary['gates'].values()))
    checks['no_economic_return_columns'] = bool(not {'gross', 'net', 'pnl', 'exit_price', 'return'}.intersection(e.columns) and summary['economic_returns_computed'] is False)
    checks['census_code_matches_recorded_hash'] = bool(study.sha(study.__file__) == summary['script_sha256'])
    checks['input_price_hashes_match'] = bool(all(study.sha(study.ROOT / k) == v for k, v in summary['price_hashes'].items()))
    result = dict(checks=checks, passed=all(checks.values()), check_count=len(checks),
                  current_git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=study.ROOT, text=True).strip(),
                  independent_review=False, economic_returns_computed=False)
    study.write_json(out / 'qa.json', result)
    print(json.dumps(result, indent=2))
    assert result['passed'], 'Census QA failed; do not interpret counts until reconciled.'


if __name__ == '__main__':
    main()
