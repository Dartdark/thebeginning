"""Render the frozen flow-innovation DESIGN report from completed saved artifacts.

This formatter never loads raw prices/flow, executes signals, selects a new rule,
regenerates random subsets, or writes program/notification state. Run it only
after the maker has completed the preregistered design phase.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_flow_innovation_relaxation'
REPORT = ROOT / 'agents/codex/results/flow_innovation_relaxation.md'
PLAN = 'agents/codex/plans/flow_innovation_relaxation.md'
EVIDENCE = 'agents/codex/evidence/flow_innovation_relaxation.md'
ORIGINAL_PREREG = 'a2a0cc7'
CLARIFIED_PREREG = '0f5e49c'
MODELS = ('INNOV15', 'INNOV20', 'BASE5', 'RAW5', 'CHANGE5')
CANDIDATES = MODELS[:2]
BASES = ('NQ', 'MNQ_price_proxy', 'NQ_four_tick_stress')
SIDES = ('all', 'long', 'short')
CONFIGURATIONS = {'INNOV15': ['innovation', 1.5], 'INNOV20': ['innovation', 2.0],
                  'BASE5': ['innovation', None], 'RAW5': ['raw', 1.5], 'CHANGE5': ['change', 1.5]}
METRIC_COLUMNS = ['model', 'period', 'side', 'trades', 'win', 'avg', 'gross', 'cost', 'total',
                  't_trade', 't_nw5', 't_nw20', 'sharpe', 'sortino', 'profit_factor',
                  'calmar', 'ulcer', 'ulcer_perf', 'max_dd', 'missing_held_minutes']


def relative(path):
    return str(Path(path).relative_to(ROOT))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(out, name):
    return json.loads((out / name).read_text())


def cell(value):
    if value is None or (isinstance(value, (float, np.floating)) and np.isnan(value)):
        return 'n/a'
    if isinstance(value, (bool, np.bool_)):
        return 'yes' if value else 'no'
    if isinstance(value, (float, np.floating)):
        return f'{value:.6g}'
    return str(value).replace('|', '\\|').replace('\n', ' ')


def table(data, columns=None):
    frame = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
    if columns is None:
        columns = list(frame.columns)
    if frame.empty:
        return 'No rows.'
    missing = set(columns) - set(frame.columns)
    if missing:
        raise ValueError(f'Missing report columns: {sorted(missing)}')
    lines = ['| ' + ' | '.join(columns) + ' |', '|' + '|'.join(['---'] * len(columns)) + '|']
    lines += ['| ' + ' | '.join(cell(row[name]) for name in columns) + ' |'
              for _, row in frame.iterrows()]
    return '\n'.join(lines)


def json_block(value):
    return '```json\n' + json.dumps(value, indent=2, ensure_ascii=False) + '\n```'


def numeric(value, digits=3):
    return 'n/a' if not np.isfinite(float(value)) else f'{float(value):.{digits}f}'


def one_metric(metrics, model, basis='NQ'):
    rows = metrics[(metrics.model == model) & (metrics.period == '2018-22') &
                   (metrics.side == 'all') & (metrics.basis == basis)]
    if len(rows) != 1:
        raise ValueError(f'Expected one aggregate metric row: {model}/{basis}')
    return rows.iloc[0]


def bool_column(frame, column):
    value = frame[column]
    if len(value) == 0:
        return np.array([], dtype=bool)
    if value.isna().any() or not value.astype(str).isin(['True', 'False']).all():
        raise ValueError(f'Unknown boolean values in audit column {column}')
    return value.astype(str).eq('True').to_numpy()


def validate_completed_design(out):
    gate = read(out, 'design_gate.json')
    marker = read(out, 'design_verified_execution.json')
    binding = read(out, 'design_input_binding.json')
    if (gate.get('definitive') is not True or marker.get('actual_raw_data_execution') is not True or
            marker.get('phase') != 'design' or marker.get('no_2023plus_read') is not True):
        raise ValueError('A completed, definitive design execution is required before report generation')
    if (list(marker.get('models', [])) != list(MODELS) or
            binding.get('configurations') != CONFIGURATIONS or gate.get('configurations_tested') != len(MODELS)):
        raise ValueError('The actual five-model execution does not match the frozen model budget')
    prereg = str(binding.get('prereg', ''))
    if (not prereg.startswith(CLARIFIED_PREREG) or marker.get('prereg') != prereg or gate.get('prereg') != prereg or
            binding.get('phase') != 'design' or marker.get('strategy_timeframe_minutes') != 5):
        raise ValueError('Preregistration, phase or five-minute clock mismatch')
    for path in (PLAN, EVIDENCE):
        if binding['source'].get(path) != digest(ROOT / path):
            raise ValueError(f'Current documentation differs from the executed binding: {path}')
    raw_paths = [name for name in binding['source'] if name.startswith('data/')]
    for name in raw_paths:
        year = re.search(r'20\d{2}', Path(name).name)
        if year is None or not 2018 <= int(year[0]) <= 2022:
            raise ValueError('Design binding contains an unexpected raw-data year')
    # Only inspect filenames here; do not open any validation outcome.
    if any(out.glob('validation_*')) or any(out.glob('full_*')):
        raise ValueError('This design-only formatter refuses to overwrite a report after validation/full outputs appear')
    if marker.get('summary_gate') != gate:
        raise ValueError('Completed execution marker and definitive gate disagree')
    for filename, key in (('design_input_binding.json', 'input_binding_sha256'),
                          ('design_gate.json', 'design_gate_sha256')):
        if marker.get(key) != digest(out / filename):
            raise ValueError(f'Completed execution marker hash mismatch: {filename}')
    if set(gate.get('gates', {})) != set(CANDIDATES):
        raise ValueError('Missing candidate gates')
    for values in gate['gates'].values():
        if not values or not all(isinstance(value, bool) for value in values.values()):
            raise ValueError('Definitive candidate gates must be explicit booleans')
    passing = [name for name in CANDIDATES if all(gate['gates'][name].values())]
    selected = passing[0] if passing else None
    if gate.get('passing') != passing or gate.get('selected') != selected or gate.get('validation_allowed') != bool(passing):
        raise ValueError('Gate violates the frozen selection order')
    if marker.get('selected') != selected:
        raise ValueError('Completed execution marker has a different selected rule')
    prior = int(binding['prior_program_evaluations'])
    prior_unique = int(binding['prior_program_unique_rules'])
    if int(gate['cumulative_evaluations']) != prior + len(MODELS):
        raise ValueError('Cumulative evaluation count does not reconcile to completed models')
    if not prior_unique <= int(gate['conservative_unique_rules']) <= prior_unique + len(MODELS):
        raise ValueError('Unique-rule count is outside the declared search history')
    return gate, marker, binding


def subset_audit(out, diagnostics, days):
    rows = []
    for model in CANDIDATES:
        for mode in ('unconditional', 'matched'):
            summary = diagnostics[model][mode]
            if (summary['runs'] != 1000 or summary['seed'] != 20261026 or
                    summary['non_executable_overlapping_signal_diagnostic'] is not True):
                raise ValueError('Subset budget, seed or nonexecutable label does not match preregistration')
            prefix = f'design_{model}_{mode}_NONEXECUTABLE'
            distribution = pd.read_csv(out / (prefix + '_subset_metrics.csv'))
            if len(distribution) != 1000 or distribution.run.tolist() != list(range(1000)):
                raise ValueError('Every random-subset result must remain saved')
            with np.load(out / (prefix + '_subset_paths_and_indices.npz'), allow_pickle=False) as saved:
                if (saved['daily_net'].shape != (1000, len(days)) or
                        saved['selected_base_rows'].shape != (1000, summary['kept_signals'])):
                    raise ValueError('Saved random subset paths or selected IDs are incomplete')
                if saved['dates'].astype(str).tolist() != days.strftime('%Y-%m-%d').tolist():
                    raise ValueError('Subset paths do not use the complete daily clock')
                # The producer CSV retains12significant digits; the NPZ retains
                # full precision. Allow only the documented serialization loss.
                np.testing.assert_allclose(saved['daily_net'].sum(axis=1), distribution.net,
                                           rtol=1e-11, atol=1e-6)
                np.testing.assert_allclose(saved['base_daily_net'] - saved['kept_daily_net'],
                                           saved['removed_daily_net'], rtol=0, atol=1e-7)
                np.testing.assert_allclose(saved['kept_daily_net'].sum(), summary['kept_net'],
                                           rtol=0, atol=1e-7)
            beats = int(bool_column(distribution, 'kept_joint_beat').sum())
            if beats != summary['strict_joint_beats']:
                raise ValueError('Subset summary and retained path results disagree')
            rows.append({key: summary[key] for key in ('mode', 'seed', 'runs', 'base_signals',
                'kept_signals', 'removed_signals', 'base_net', 'kept_net', 'removed_net',
                'removed_mean', 'removed_t', 'kept_max_dd', 'strict_joint_beats',
                'p_kept_better_net_and_dd', 'p_random_net_ge_kept')} | {'model': model,
                'matching_cells': len(summary.get('cells', [])), 'all_paths_and_ids_retained': True})
    return pd.DataFrame(rows)


def audit_tables(out, metrics, counts, days):
    held_rows, bad_rows = [], []
    ledgers = [(model, 'executable', f'design_{model}_trades.csv.gz',
                f'design_{model}_held_audit.csv.gz') for model in MODELS]
    ledgers += [(model, 'independent_NONEXECUTABLE', f'design_{model}_independent_signals_NONEXECUTABLE.csv.gz',
                 f'design_{model}_independent_held_audit.csv.gz') for model in ('BASE5',) + CANDIDATES]
    for model, kind, ledger_file, held_file in ledgers:
        trades = pd.read_csv(out / ledger_file, parse_dates=['date'])
        held = pd.read_csv(out / held_file)
        expected = (int(one_metric(metrics, model).trades) if kind == 'executable' else
                    int(read(out, f'design_{model}_independent_counts.json')['replayed']))
        if len(trades) != expected or len(held) != len(trades):
            raise ValueError(f'Executable ledger/metrics/count disagreement: {model}')
        if kind == 'executable' and len(trades) != counts[model]['executed']:
            raise ValueError(f'Executable suppression count disagreement: {model}')
        if len(trades) and not trades.date.isin(days).all():
            raise ValueError('Saved trade outside the declared daily design calendar')
        bad = ((held.invalid_held_ohlc_bars > 0) | (held.invalid_held_native_volume_bars > 0) |
               bool_column(held, 'time_exit_displaced') | ~bool_column(held, 'actual_entry_matches_schedule'))
        held_rows.append(dict(model=model, ledger_kind=kind, trades=len(trades), unresolved_native_path_rows=int(bad.sum()),
            invalid_held_ohlc_bars=int(held.invalid_held_ohlc_bars.sum()),
            invalid_held_native_volume_bars=int(held.invalid_held_native_volume_bars.sum()),
            held_missing_flow_quantity_bars=int(held.held_missing_flow_quantity_bars.sum()),
            held_source_native_volume_disagreements=int(held.held_source_native_volume_disagreements.sum()),
            mismatched_scheduled_entries=int((~bool_column(held, 'actual_entry_matches_schedule')).sum()),
            displaced_actual_time_exits=int(bool_column(held, 'time_exit_displaced').sum()),
            invalid_scheduled_exit_slots_including_prior_bracket_exits=int((~bool_column(held, 'scheduled_exit_ohlc_valid')).sum())))
        if bad.any():
            keys = ['day', 'signal_j', 'side', 'j0', 'j1']
            issues = held.loc[bad].reset_index(names='held_audit_row').merge(
                trades[keys + ['date', 'net']], on=keys, how='left', validate='one_to_one')
            if issues.date.isna().any():
                raise ValueError('Unresolved held row lost its saved trade/date identity')
            for row in issues.itertuples():
                label = lambda value: f'{int(value)//60:02d}:{int(value)%60:02d}'
                bad_rows.append(dict(model=model, ledger_kind=kind, held_audit_row=row.held_audit_row,
                    date=str(row.date.date()), signal_close_CT=label(row.signal_j),
                    entry_row_close_label_CT=label(row.j0), actual_exit_close_CT=label(row.j1), side=row.side,
                    invalid_held_ohlc_bars=row.invalid_held_ohlc_bars,
                    invalid_held_native_volume_bars=row.invalid_held_native_volume_bars,
                    held_missing_flow_quantity_bars=row.held_missing_flow_quantity_bars,
                    held_source_native_volume_disagreements=row.held_source_native_volume_disagreements,
                    time_exit_displaced=row.time_exit_displaced, retained_unresolved_NQ_net=row.net))
    training = pd.read_csv(out / 'design_training_audit.csv.gz', parse_dates=['date'])
    slots = []
    for row in training.itertuples():
        observed = json.loads(row.training_slots)
        if len(observed) != 20 or row.training_slot_count != 20 or sum(item['pairs'] for item in observed) != row.pairs:
            raise ValueError('Exact chronological flow training slots do not reconcile')
        if any(pd.Timestamp(item['date']) >= row.date for item in observed):
            raise ValueError('Current/future calendar slot entered flow training')
        slots.extend(observed)
        if pd.notna(row.max_training_timestamp_ct) and pd.Timestamp(row.max_training_timestamp_ct) >= row.date:
            raise ValueError('Current/future flow observation entered a fitted state')
    fitted = training[training.status == 'fit']
    training_summary = dict(calendar_rows=len(training), status_counts=training.status.value_counts().to_dict(),
        fitted_dates=len(fitted), exact_prior_slot_count=20, current_future_training_observations_found=0,
        slot_reason_counts=pd.Series([item['reason'] for item in slots]).value_counts().to_dict(),
        first_fitted_date=str(fitted.date.min().date()) if len(fitted) else None,
        last_fitted_date=str(fitted.date.max().date()) if len(fitted) else None,
        fitted_pair_min=int(fitted.pairs.min()) if len(fitted) else None,
        fitted_pair_max=int(fitted.pairs.max()) if len(fitted) else None)
    calendar = pd.read_csv(out / 'design_calendar_audit.csv', parse_dates=['date'])
    events = pd.read_csv(out / 'design_event_audit.csv.gz', usecols=['reason'])
    atr = pd.read_csv(out / 'design_atr_reference_audit.csv.gz', parse_dates=['date'])
    for row in atr.itertuples():
        if pd.notna(row.max_reference_timestamp_ct) and pd.Timestamp(row.max_reference_timestamp_ct) >= row.date:
            raise ValueError('Current/future date entered a prior ATR reference window')
    return pd.DataFrame(held_rows), pd.DataFrame(bad_rows), training_summary, dict(
        calendar_kind_counts=calendar.calendar_kind.value_counts().to_dict(),
        signal_event_reason_counts=events.reason.value_counts().to_dict(),
        prior_atr_reference_rows=len(atr), current_future_atr_reference_dates_found=0,
        atr_semantics='shared shifted15storedweekday TR observations; missing dates dropped; continuous-roll limits retained')


def reconcile_gate(gate, metrics, held, filters):
    resolved = bool(((held.invalid_held_ohlc_bars == 0) &
                     (held.displaced_actual_time_exits == 0) & (held.mismatched_scheduled_entries == 0)).all())
    for model in CANDIDATES:
        main = one_metric(metrics, model)
        years = metrics[(metrics.model == model) & (metrics.basis == 'NQ') &
                        (metrics.side == 'all') & metrics.period.str.fullmatch(r'20\d{2}')]
        own_held = held[(held.model == model) & (held.ledger_kind == 'executable')].iloc[0]
        control = filters[model]['unconditional']
        expected = dict(count=main.trades >= 100, net=main.total > 0, trade_t=main.t_trade >= 2,
            daily_nw5=main.t_nw5 >= 1.5, profit_factor=main.profit_factor >= 1.20,
            positive_years=int((years.total > 0).sum()) >= 4,
            micro_cost_proxy_net=one_metric(metrics, model, 'MNQ_price_proxy').total > 0,
            four_tick_stress_net=one_metric(metrics, model, 'NQ_four_tick_stress').total > 0,
            candidate_executable_zero_invalid_held_ohlc=own_held.invalid_held_ohlc_bars == 0,
            all_controls_and_diagnostic_held_paths_resolved=resolved,
            removed_independent_net_negative=control['removed_net'] < 0,
            kept_independent_total_exceeds_base=control['kept_net'] > control['base_net'],
            unconditional_joint_beats=filters[model]['unconditional']['strict_joint_beats'] >= 900,
            year_side_signalhour_joint_beats=filters[model]['matched']['strict_joint_beats'] >= 900)
        if {key: bool(value) for key, value in expected.items()} != gate['gates'][model]:
            raise ValueError(f'Definitive gate does not reconcile to retained metrics/paths/subsets: {model}')


def main(input_dir=None):
    out = (OUT if input_dir is None else Path(input_dir)).resolve()
    if not out.is_relative_to(OUT.resolve()):
        raise ValueError('Report input must remain in this study output tree')
    gate, marker, binding = validate_completed_design(out)
    metrics = pd.read_csv(out / 'design_metrics.csv', dtype={'period': str})
    daily = pd.read_csv(out / 'design_daily.csv', parse_dates=['date'])
    days = pd.DatetimeIndex(daily.date)
    if (not days.is_monotonic_increasing or days.has_duplicates or days.isna().any() or
            len(days) == 0 or days.min() < pd.Timestamp('2018-01-01') or days.max() > pd.Timestamp('2022-12-31')):
        raise ValueError('Invalid complete daily design clock')
    periods = ['2018-22'] + [str(year) for year in sorted(days.year.unique())]
    expected = {(m, p, s, b) for m in MODELS for p in periods for s in SIDES for b in BASES}
    observed = list(metrics[['model', 'period', 'side', 'basis']].itertuples(index=False, name=None))
    if len(observed) != len(set(observed)) or set(observed) != expected:
        raise ValueError('Saved standard metrics must cover every model/basis/side/design year')
    counts = read(out, 'design_counts.json')
    held, bad_held, training, calendar = audit_tables(out, metrics, counts, days)
    filters = read(out, 'design_filter_diagnostics.json')
    subsets = subset_audit(out, filters, days)
    reconcile_gate(gate, metrics, held, filters)
    degeneracy = read(out, 'design_degeneracy_audit.json')
    comparisons = []
    for index, model in enumerate(MODELS):
        for other in MODELS[index + 1:]:
            comparisons.append({'first_model': model, 'second_model': other,
                                **degeneracy['model_equality'][model + '__' + other]})
    degeneracy_summary = {key: value for key, value in degeneracy.items() if key != 'model_equality'}
    native = read(out, 'design_native_intake.json')
    flow = read(out, 'design_flow_intake.json')
    selected = gate['selected']
    headline = one_metric(metrics, selected or 'INNOV15')
    evaluations, unique = int(gate['cumulative_evaluations']), int(gate['conservative_unique_rules'])
    verdict = 'DESIGN CANDIDATE; validation and independent review pending' if selected else 'REJECT; continue distinct research'
    decision = (f'The fixed selection order selected {selected}; this is a design result only.' if selected else
                'Neither frozen innovation candidate passed every design gate; reject this family.')
    other = one_metric(metrics, 'INNOV20')
    secondary_summary = (f'INNOV20: {int(other.trades)} trades, net ${other.total:,.2f}/NQ, '
        f'trade t {numeric(other.t_trade)}, dailyNW5 {numeric(other.t_nw5)}.\n') if not selected else ''
    summary = (f'Summary: {decision}\n'
        f'{selected or "Primary INNOV15"}: {int(headline.trades)} executable trades, net ${headline.total:,.2f}/NQ, '
        f'trade t {numeric(headline.t_trade)}, daily Newey-West(5) t {numeric(headline.t_nw5)}.\n'
        + secondary_summary +
        f'All five models are five-minute rules; INNOV15 denotes a 1.5-scale threshold. No2023+ returns appear here.\n'
        f'{evaluations} cumulative evaluations/{unique} conservative unique rules; no full-history t4/4.5/5/6 claim or trading approval.')
    metric_sections = []
    for basis in BASES:
        part = metrics[metrics.basis == basis].copy()
        part['model'] = pd.Categorical(part.model, MODELS, ordered=True)
        part['period'] = pd.Categorical(part.period, periods, ordered=True)
        part['side'] = pd.Categorical(part.side, SIDES, ordered=True)
        part = part.sort_values(['model', 'period', 'side'])
        metric_sections.append(f'### {basis}\n\n' + table(part, METRIC_COLUMNS))
    quality_decision = ('Commit the complete design selection before running only the selected rule and BASE5 once on '
        'previously seen2023+ historical validation. Dependence/selection/placebo checks and a fresh raw-spec checker '
        'remain required before promotion.' if selected else
        'No2023+ validation, post-pass placebos/resampling, promotion checker, account tests or PowerLanguage is '
        'justified by this failed design. Do not invert the fade, retune thresholds or nominate a successful control. '
        'Continue a DISTINCT hypothesis; this failure does not pause the research program.')
    report = f'''# NQ Flow Innovation Relaxation: {verdict}

{summary}

Plan: {PLAN}. Original preregistration {ORIGINAL_PREREG}; clarified before returns at {CLARIFIED_PREREG}.
Executed binding: {binding['prereg']}; evidence: {EVIDENCE}. The clarification made ratio-of-summed quantities
and actual shared-ATR semantics explicit before outcomes; numeric parameters/population scales were already frozen.
Scripts: analysis/codex_flow_innovation_relaxation.py
and analysis/codex_flow_innovation_relaxation_report.py. Output: {relative(out)}/.
Completed execution marker: {relative(out / 'design_verified_execution.json')}.

## Rule and economic hypothesis

At each completed five-minute close09:00–14:00CT, construct q=(sum buy−sum sell)/(sum buy+sum sell) from
the exact five native minutes. Use q from the immediately preceding same-session bar. Before each date,
fit y=a+b*x on complete adjacent flow pairs from the exact previous20normal-cash calendar slots; roll slots
contribute no pairs. Require600pairs from15dates and nondegenerate predictor/scales. Do not stretch missing
slots, link overnight observations or include current-day data. Project the OLS coefficient to[−0.95,0.95],
then recalculate the intercept. Innovation is e=q_current−a−b*q_previous, divided by prior residual RMS.
Raw and centered-change controls use the identical training targets and population/RMS scales(ddof0).

Fade the innovation. The temporary-pressure-relaxation hypothesis is weak: an informed order-flow innovation
may have permanent impact. Dealer inventory, a metaorder, a hedge obligation and compulsory covering are
unobserved. No old strategy ticket, portfolio return, fitted return target, price-body/VWAP/opening-path gate
or second traded leg supplies the entry. The bounded old-definition audit does not establish exhaustive novelty.

| Five-minute model | Frozen role/rule |
|---|---|
| INNOV15 | Primary candidate: fade innovation z when abs(z)>=1.5 |
| INNOV20 | Second candidate: same rule at abs(z)>=2.0 |
| BASE5 | Unselectable matched base: fade every nonzero residual |
| RAW5 | Unselectable control: fade demeaned current-flow z at1.5 |
| CHANGE5 | Unselectable control: fade centered flow-change z at1.5 |

Zero side gives no entry. Selection uses the first candidate passing every frozen gate, never maximal t.
At b=0 the residual becomes raw demeaned flow; at b=1 it becomes centered flow change. Empirical equality
does not by itself prove algebraic duplicate rules; neither AR terminology nor matching tickets establishes
a new independent economic factor. All evaluations and older related searches remain relevant.

## Clocks, execution and costs

Bridge Eastern close labels map to Central labels by subtracting60minutes. Require every input minute:
valid finite native OHLCV, nonnegative buy/sell, positive total, exact native volume=buy+sell and source close
within0.25point of native close. OF volume alone is BUY volume, not total. Use normal cash dates, skip
July3/December24 and the frozen equity roll guard; do not use future-dependent trading-day membership.

Decision close j -> market at the open of row j+2. For09:00 this is the09:02-labelled bar, whose open is
09:01wall time: one whole extra minute for receipt/order allowance, not observed historical receipt evidence.
Missing scheduled open skips that signal. Shared grid._walk/F.replay provides one position, max4tickets/day,
no stale or same-close reentry, entry-bar protection, worse gap opens, the shared both-hit assumption and
one-point target-through. Stop0.10priorATR, target0.15priorATR rounded up to0.25; time exit at signal+30minutes
or14:55, whichever earlier. No BE/trailing/overnight/size fitting. Shared ATR uses15 stored prior weekday true
ranges, shifted; missing dates are dropped by that engine. Its semantics differ from exact20flow-calendar slots.

NQ:20USD/point,7.25USD round-trip fee plus5USD per market/stop fill. MNQ:2USD/point,1.24USD fee plus0.50USD
per such fill, separately repriced on NQ bars. Four-tick NQ stress charges20USD per market/stop fill.
Targets receive no extra exit slippage but require trade-through. These are repository cost assumptions,
not newly verified broker quotes. MNQ rows are NQ-price proxies; prelisting history is hypothetical and no
native MNQ spread/queue/fill parity is established. No proxy-derived account improvement is claimed.

## Saved design metrics

Daily cash-session vector: {days.min().date()}–{days.max().date()}, {len(days)} sessions including zero days.
Every frozen model, both sides and every design year is shown for NQ, the separately fee-repriced micro proxy
and fixed NQ stress. Metrics are the maker's saved shared-engine statistics; drawdowns include initial zero,
daily annualization uses252days and percentage/Ulcer calculations use the research50,000USD account basis.

'''+ '\n\n'.join(metric_sections) + f'''

## Complete frozen design decision

The gate requires100trades, positive NQ/micro-proxy/stress net, trade t>=2, dailyNW5>=1.5,PF>=1.20,
four positive years, resolved held paths and BOTH frozen random-subset tests. A favorable individual metric,
side/year/control or cheap gate alone cannot override a failed condition.

'''+json_block(gate)+'''

## Filter controls: executable versus overlapping diagnostics

The preceding metric tables are executable one-position/max4-per-day ledgers. Candidate and BASE5 capped
ledgers are nonnested; their subtraction is not an executable removed-trade strategy.

Separately replay every independent BASE5/candidate signal with identical exits, ignoring overlap/caps only
for the explicitly NONEXECUTABLE diagnostic. Base/kept/removed profits and removed mean/t below concern
those overlapping signal returns. They do not supply a capitalized strategy or account path.

'''+table(subsets, ['model','mode','seed','runs','base_signals','kept_signals','removed_signals','base_net',
    'kept_net','removed_net','removed_mean','removed_t','kept_max_dd','strict_joint_beats',
    'p_kept_better_net_and_dd','p_random_net_ge_kept','matching_cells','all_paths_and_ids_retained'])+f'''

Each candidate retains1,000unconditional and1,000year×side×signal-hour matched subsets, all with seed20261026.
Strict superiority requires higher profit AND lower daily maximum drawdown; ties do not count. At least900
joint wins are required in each mode. Matched cells cannot borrow observations from other years/sides/hours.
Every subset's metrics, complete zero-filled daily path and selected BASE5 row IDs remain in
design_NAME_MODE_NONEXECUTABLE_subset_metrics.csv and the corresponding subset_paths_and_indices.npz.
Full matching-cell counts and summaries are retained in design_filter_diagnostics.json and per-mode JSONs;
independent base/candidate/removed ledgers remain separately labelled NONEXECUTABLE. These4,000draws and
three independent signal replays are diagnostics, not additional economic configurations.

## Input, training, equality and held-path audits

Native duplicates/coverage and flow duplicates/clock/quantity/close-agreement findings:

'''+json_block({'native_intake':native,'flow_intake':flow})+'''

Every source-minute failure and conflicting/exact-duplicate row remains in its saved audit; no future repair
or profitable-path deletion was used. The producer binding retains source hashes and records its unchanged-input
check. This report consumes the saved binding and outcomes; it is not a fresh independent raw-feed rebuild.

'''+json_block({'training':training,'calendar_and_events':calendar,'execution_counts':counts})+'''

The full training audit retains all20slots, pair counts, first/last dates, maximum timestamp, raw/projected
coefficient and all scales. Current/future fit timestamps were checked when rendering this report. The ATR
reference audit, q-bar input arrays and all event reasons remain saved separately.

'''+json_block(degeneracy_summary)+'''

Exact event/side comparisons against every control:

'''+table(comparisons)+'''

All held-path observations, including invalid bars, are retained:

'''+table(held)+'''

Exact unresolved native held-path rows, retained rather than deleted (audit row IDs are zero-based):

'''+table(bad_held)+f'''

An invalid scheduled exit slot after an earlier bracket exit is distinguished from a displaced actual time exit.
Held source-flow disagreement/missingness is reported separately from native OHLC path validity. Unknown
held prices, displaced time exits or mismatched scheduled entries prevent advancement under the saved gates.
The unresolved-row net column is the retained kernel calculation across an unobserved path, not a validated
price reconstruction or executable account return. Independent rows overlap and must not be counted as
distinct missing market minutes. No row was removed because of its profit or loss.

## Search history, limitations and next action

This phase actually completed{len(MODELS)}models. Binding records{binding['prior_program_evaluations']}prior
evaluations/{binding['prior_program_unique_rules']}unique; the definitive gate records{evaluations}cumulative
evaluations/{unique}conservative unique rules. {gate.get('unique_rule_note','')}
Unknown larger older searches remain part of selection risk. No favorable control can be nominated from
these results, and no design-only statistic creates a full-history4/4.5/5/6milestone.

Continuous-contract mapping, original historical receipt/vintages, exchange halt certification and native
micro execution remain limitations. Native quantity/close agreement is corroboration, not proof of actual
contract IDs or original feed authenticity. Shared prior ATR can inherit roll discontinuities. The research
rule can share daytime NQ trend/reversal losses with existing plan legs; no empty slot or before-breach offset
is established. Whole-contract BASE/ADD/replacement/EMPTY account comparisons require valid joint paths;
missing50K/150K/account chronology is a LIMIT, not permission to invent pass/payout improvements.

{quality_decision}
No live action, deployment, broker/API setting, purchases, external messages or watcher changes follow this report.
The previously reported EIA access blocker remains separate; do not repeat it for routine source/engineering work.

Actual execution completion recorded by the maker: {marker['completed_utc']}.
Execution evidence:

'''+json_block(marker)+f'''

Claude review path: {relative(REPORT)}.
'''
    REPORT.write_text(report)
    print(json.dumps(dict(report=relative(REPORT), verdict=verdict, selected=selected,
                          completed_evaluations=evaluations, conservative_unique_rules=unique,
                          program_or_notification_state_written=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, help='Completed design artifact directory inside this study output tree')
    args = parser.parse_args()
    main(args.input_dir)
