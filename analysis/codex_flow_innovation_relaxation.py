"""Frozen five-minute NQ flow-innovation fade; no returns are run on import.

Bind --prereg to the committed, clarified plan before actual input processing.
--self-check uses synthetic arrays only. Actual phases preserve immutable artifacts;
an append-only attempt log also retains failures and explicitly named engineering retries.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import traceback
import warnings

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_flow_innovation_relaxation'
PLAN = 'agents/codex/plans/flow_innovation_relaxation.md'
EVIDENCE = 'agents/codex/evidence/flow_innovation_relaxation.md'
os.environ['NUMBA_CACHE_DIR'] = str(OUT / 'numba_cache')
sys.path.insert(0, str(ROOT / 'analysis'))
import numpy as np
import pandas as pd
import codex_cash_open_repair as C
import codex_flow_absorption as F
import codex_t6_study_support as S
import metrics as M
import resampling as R
from grid import _walk
from grid24 import Grid24
import numba
from numba.core.caching import FunctionCache

# Imported historical helpers set their own cache location; restore this task's scope.
os.environ['NUMBA_CACHE_DIR'] = str(OUT / 'numba_cache')
numba.config.CACHE_DIR = str(OUT / 'numba_cache')
_walk._cache = FunctionCache(_walk.py_func)

CONFIGS = {'INNOV15': ('innovation', 1.5), 'INNOV20': ('innovation', 2.0),
           'BASE5': ('innovation', None), 'RAW5': ('raw', 1.5), 'CHANGE5': ('change', 1.5)}
CANDIDATES = ('INNOV15', 'INNOV20')
SEED = 20261026
PRIOR_EVALUATIONS, PRIOR_UNIQUE = 60, 58
Q_CLOSES = np.arange(535, 841, 5, dtype=int)
DECISIONS = Q_CLOSES[1:]
NATIVE_FIELDS = ['open', 'high', 'low', 'close', 'volume']
FLOW_FIELDS = ['upvol', 'downvol', 'close']
SIGCOLS = ['day', 'signal_j', 'dj', 'side', 'stop', 'target', 'exit_j',
           'delta_fraction', 'input_last_j', 'first_entry_j', 'q_current', 'q_previous',
           'residual', 'innovation_z', 'raw_z', 'change_z', 'stratum_year', 'stratum_hour', 'fit_date']


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    """Use the shared immutable writer; never replace a different return artifact."""
    C.write(path, value)


def dump(path, value):
    save(path, json.dumps(value, indent=2, default=str, allow_nan=True) + '\n')


def frame(path, value, index=False, compress=False):
    data = value.to_csv(index=index, float_format='%.12g').encode()
    save(path, gzip.compress(data, mtime=0) if compress else data)


def arrays(path, **values):
    stream = io.BytesIO()
    np.savez_compressed(stream, **values)
    save(path, stream.getvalue())


def append_attempt(value):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / 'attempts.jsonl').open('a') as stream:
        stream.write(json.dumps(value, default=str, allow_nan=True) + '\n')


def native_paths(phase):
    last = 2022 if phase == 'design' else 2026
    # No 2017 warm-up is used; this is allowed by the plan and avoids OF substitution.
    return [ROOT / 'data' / f'NQ_1min_{suffix}{year}.csv'
            for year in range(2018, last + 1) for suffix in ('', 'ON_')]


def flow_paths(phase):
    last = 2022 if phase == 'design' else 2026
    return sorted(path for path in (ROOT / 'data').glob('OF_1min_*.csv')
                  if re.fullmatch(r'OF_1min_\d{4}_[1-4]\.csv', path.name)
                  and 2018 <= int(path.name.split('_')[2]) <= last)


def git_bytes(ref, path):
    return subprocess.check_output(['git', 'show', ref + ':' + path], cwd=ROOT)


def bind(out, prereg, phase, selection_commit=None):
    if subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() != 'codex/work':
        raise ValueError('Research is restricted to codex/work')
    if git_bytes(prereg, PLAN) != (ROOT / PLAN).read_bytes():
        raise ValueError('Working plan differs from the committed preregistration')
    if git_bytes(prereg, EVIDENCE) != (ROOT / EVIDENCE).read_bytes():
        raise ValueError('Working evidence differs from the committed evidence sheet')
    selected = None
    if phase == 'validation':
        if not selection_commit:
            raise ValueError('Validation needs a committed definitive design selection')
        subprocess.check_call(['git', 'merge-base', '--is-ancestor', selection_commit, 'HEAD'], cwd=ROOT)
        gate_path = 'analysis/outputs/codex_flow_innovation_relaxation/design_gate.json'
        committed = git_bytes(selection_commit, gate_path)
        gate = json.loads(committed)
        marker_path = 'analysis/outputs/codex_flow_innovation_relaxation/design_verified_execution.json'
        marker = json.loads(git_bytes(selection_commit, marker_path))
        binding_path = 'analysis/outputs/codex_flow_innovation_relaxation/design_input_binding.json'
        prior_binding_bytes = git_bytes(selection_commit, binding_path)
        if (marker.get('actual_raw_data_execution') is not True or marker.get('phase') != 'design'
                or marker.get('prereg') != prereg or marker.get('models') != list(CONFIGS)
                or marker.get('summary_gate') != gate
                or marker.get('selected') != gate.get('selected')
                or marker.get('design_gate_sha256') != hashlib.sha256(committed).hexdigest()
                or marker.get('input_binding_sha256') != hashlib.sha256(prior_binding_bytes).hexdigest()):
            raise ValueError('Validation requires the matching committed successful design execution marker')
        if gate.get('definitive') is not True or gate.get('prereg') != prereg:
            raise ValueError('Validation requires the definitive gate for this exact preregistration')
        selected = gate.get('selected')
        if selected not in CANDIDATES or not gate.get('validation_allowed'):
            raise ValueError('Frozen design failed; this family must not run validation')
        if not all(gate['gates'][selected].values()):
            raise ValueError('Committed selected candidate has a failed frozen gate')
        save(out / 'committed_design_gate.json', committed)
    inputs = native_paths(phase) + flow_paths(phase)
    missing = [str(p.relative_to(ROOT)) for p in inputs if not p.exists()]
    if missing:
        raise ValueError('Missing required raw files: ' + ', '.join(missing))
    modules = ['grid.py', 'grid24.py', 'metrics.py', 'resampling.py', 'codex_cash_open_repair.py',
               'codex_flow_absorption.py', 'codex_s03_calendar.py', 'replica.py', 'codex_t6_study_support.py',
               Path(__file__).name]
    paths = inputs + [ROOT / PLAN, ROOT / EVIDENCE,
        ROOT/'tools/exporters/NQ_Bar_Exporter.txt',ROOT/'tools/exporters/OFB_OrderFlow_Exporter.txt'] + [ROOT / 'analysis' / name for name in modules]
    binding = dict(prereg=prereg, phase=phase, selection_commit=selection_commit, selected=selected,
        configurations=CONFIGS if phase == 'design' else {k: CONFIGS[k] for k in (selected, 'BASE5')},
        prior_program_evaluations=PRIOR_EVALUATIONS, prior_program_unique_rules=PRIOR_UNIQUE,
        source={str(p.relative_to(ROOT)): sha(p) for p in paths},
        design_raw_years='2018--2022 only; no native 2017 warm-up used',
        validation_label='previously seen historical validation, never a fresh holdout',
        source_receipt='one-minute assumed receipt/order allowance; historical receipt unverified',
        native_micro='NQ-price proxy with separately calculated MNQ fees; not native MNQ fill evidence',
        atr_semantics='shared daily_atr(15): previous15 stored weekday TR observations; shifted, missing dates dropped')
    dump(out / f'{phase}_input_binding.json', binding)
    return binding, selected


def duplicate_audit(raw, fields, label, out, phase):
    duplicates = raw.duplicated(['date', 'time'], keep=False)
    conflicts = raw[duplicates].groupby(['date', 'time'])[fields].nunique(dropna=False)
    bad = conflicts.index[(conflicts > 1).any(axis=1)]
    detail = raw.loc[duplicates].copy()
    if len(detail):
        detail['conflicting_key'] = pd.MultiIndex.from_frame(detail[['date', 'time']]).isin(bad)
    frame(out / f'{phase}_{label}_duplicate_rows.csv.gz', detail, compress=True)
    summary = dict(rows_before=len(raw), exact_duplicate_rows=int(raw.duplicated().sum()),
                   duplicate_key_rows=int(duplicates.sum()), conflicting_keys=len(bad))
    dump(out / f'{phase}_{label}_duplicate_audit.json', summary)
    if len(bad):
        raise ValueError(f'{label}: conflicting duplicate selected-field keys block intake')
    return raw.drop_duplicates(['date', 'time']).sort_values(['date', 'time']).reset_index(drop=True), summary


def load_native(out, phase, hi):
    paths = native_paths(phase)
    raw = pd.concat([pd.read_csv(p, usecols=['date', 'time'] + NATIVE_FIELDS) for p in paths], ignore_index=True)
    raw = raw[raw.date <= int(hi.strftime('%Y%m%d'))].copy()
    clean, audit = duplicate_audit(raw, NATIVE_FIELDS, 'native', out, phase)
    audit.update(first=int(clean.date.min()), last=int(clean.date.max()),
                 cutoff=str(hi.date()), clock='CT minute-close labels', selected_fields=NATIVE_FIELDS)
    dump(out / f'{phase}_native_intake.json', audit)
    # Reuse Grid24's representation and ATR/bar methods. Construct from the audited,
    # cutoff-filtered native frame so later validation dates never enter an array.
    g = Grid24.__new__(Grid24)
    cal = pd.date_range(str(clean.date.min()), str(clean.date.max()), freq='D')
    g.ts = cal.to_numpy(); g.dates = cal.strftime('%Y%m%d').astype(int).to_numpy(); g.D = len(cal)
    row = np.searchsorted(g.dates, clean.date.to_numpy())
    col = (clean.time.to_numpy() // 100) * 60 + clean.time.to_numpy() % 100
    if not ((col >= 0) & (col < 1440) & (clean.time.to_numpy() % 100 < 60)).all():
        raise ValueError('Invalid native minute clock')
    for name in NATIVE_FIELDS:
        values = np.full((g.D, 1440), np.nan)
        values[row, col] = clean[name].to_numpy(float)
        setattr(g, name[0] if name != 'volume' else 'v', values)
    present = np.isfinite(g.c)
    g.last_j = np.where(present.any(axis=1), 1439 - np.argmax(present[:, ::-1], axis=1), -1)
    g.jof = lambda time: (np.asarray(time) // 100) * 60 + np.asarray(time) % 100
    # Compatibility only: eligibility never uses this membership or future bar presence.
    g.trading = np.array([], dtype=int)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        g._flow_atr = g.daily_atr(15)
    return g


def valid_ohlc(g):
    return (np.isfinite(g.o) & np.isfinite(g.h) & np.isfinite(g.l) & np.isfinite(g.c)
            & (g.h >= np.maximum(g.o, g.c)) & (g.l <= np.minimum(g.o, g.c)) & (g.h >= g.l))


def intake(out, g, phase, hi):
    raw = pd.concat([pd.read_csv(p, usecols=['date', 'time'] + FLOW_FIELDS) for p in flow_paths(phase)], ignore_index=True)
    raw = raw[raw.date <= int(hi.strftime('%Y%m%d'))].copy()
    raw, summary = duplicate_audit(raw, FLOW_FIELDS, 'flow', out, phase)
    flow = {name: np.full(g.c.shape, np.nan) for name in ('buy', 'sell', 'close')}
    raw['minute_ct'] = (raw.time // 100) * 60 + raw.time % 100 - 60
    if not (raw.minute_ct.between(0, 1439) & (raw.time % 100).between(0, 59)).all():
        raise ValueError('Invalid source ET minute-close clock')
    row = np.searchsorted(g.dates, raw.date.to_numpy())
    mapped = (row < g.D) & (g.dates[np.minimum(row, g.D - 1)] == raw.date.to_numpy())
    raw['native_date_mapped'] = mapped
    for name, column in (('buy', 'upvol'), ('sell', 'downvol'), ('close', 'close')):
        flow[name][row[mapped], raw.loc[mapped, 'minute_ct'].to_numpy()] = raw.loc[mapped, column].to_numpy(float)
    flow['total'] = flow['buy'] + flow['sell']
    native_price = valid_ohlc(g)
    native_quantity = np.isfinite(g.v) & (g.v >= 0)
    quantity = (np.isfinite(flow['buy']) & np.isfinite(flow['sell']) & (flow['buy'] >= 0)
                & (flow['sell'] >= 0) & (flow['total'] > 0))
    close_match = np.isfinite(flow['close']) & np.isfinite(g.c) & (abs(flow['close'] - g.c) <= .25)
    volume_match = np.isfinite(g.v) & np.isfinite(flow['total']) & (g.v == flow['total'])
    flow['valid'] = native_price & native_quantity & quantity & close_match & volume_match
    for name, mask in (('native_ohlc_valid', native_price), ('native_volume_valid', native_quantity),
                       ('flow_quantities_valid', quantity), ('close_within_one_tick', close_match),
                       ('exact_total_volume_match', volume_match), ('input_minute_valid', flow['valid'])):
        values = np.zeros(len(raw), dtype=bool)
        values[mapped] = mask[row[mapped], raw.loc[mapped, 'minute_ct'].to_numpy()]
        raw[name] = values
    flags = ('native_date_mapped', 'native_ohlc_valid', 'native_volume_valid',
             'flow_quantities_valid', 'close_within_one_tick', 'exact_total_volume_match')
    raw['failure_flags'] = [','.join(name for name, good in zip(flags, values) if not good)
                            for values in raw[list(flags)].itertuples(index=False, name=None)]
    frame(out / f'{phase}_flow_minute_audit.csv.gz', raw, compress=True)
    summary.update(first=int(raw.date.min()), last=int(raw.date.max()), cutoff=str(hi.date()),
        valid_input_minutes=int(flow['valid'].sum()), unmapped_rows=int((~mapped).sum()),
        failed_rows=int((~raw.input_minute_valid).sum()),
        failures_by_flag={key: int((~raw[key]).sum()) for key in ('native_date_mapped', 'native_ohlc_valid',
            'native_volume_valid', 'flow_quantities_valid', 'close_within_one_tick', 'exact_total_volume_match')},
        source_clock='ET minute-close minus60minutes -> CT minute-close; original receipt unverified',
        quantity_semantics='upvol=buy,downvol=sell,total=sum; OF volume is NOT total',
        contract_mapping='individual native contract IDs unavailable; strict observed close/total agreement is limited corroboration')
    dump(out / f'{phase}_flow_intake.json', summary)
    return flow


def audit_atr(out, g, phase, lo, hi):
    """Audit reference dates around the unchanged shared daily_atr calculation."""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        high, low = np.nanmax(g.h, axis=1), np.nanmin(g.l, axis=1)
        has = ~np.isnan(g.c).all(axis=1)
        last = np.array([row[~np.isnan(row)][-1] if good else np.nan for row,good in zip(g.c,has)])
        previous = pd.Series(last).where(has).ffill().shift(1).to_numpy()
        tr = np.nanmax(np.c_[high-low,abs(high-previous),abs(low-previous)],axis=1)
    history, rows = [], []
    for day, stamp in enumerate(g.ts):
        date = pd.Timestamp(stamp); reference = history[-15:]
        if lo <= date <= hi:
            expected = float(np.mean(tr[reference])) if len(reference)==15 else np.nan
            actual = float(g._flow_atr[day])
            np.testing.assert_allclose(actual,expected,rtol=1e-12,atol=1e-10,equal_nan=True)
            rows.append(dict(day=day,date=date,shared_atr=actual,stored_reference_count=len(reference),
                reference_dates=json.dumps([str(pd.Timestamp(g.ts[k]).date()) for k in reference]),
                reference_roll_guard_dates=sum(C.roll_guard(pd.Timestamp(g.ts[k])) for k in reference),
                max_reference_date=str(pd.Timestamp(g.ts[reference[-1]]).date()) if reference else '',
                max_reference_timestamp_ct=str(pd.Timestamp(g.ts[reference[-1]])+pd.Timedelta(minutes=int(g.last_j[reference[-1]]))) if reference else '',
                missing_dates_dropped_by_shared_engine=True,exact20flow_training_is_separate=True))
        if has[day] and date.dayofweek<5 and np.isfinite(tr[day]):
            history.append(day)
    frame(out/f'{phase}_atr_reference_audit.csv.gz',pd.DataFrame(rows),compress=True)


def q_from_sums(buy, sell):
    total = np.sum(buy) + np.sum(sell)
    return float((np.sum(buy) - np.sum(sell)) / total) if total > 0 else np.nan


def q_bars(g, flow):
    q = np.full((g.D, len(Q_CLOSES)), np.nan)
    counts = np.zeros(q.shape, dtype=np.int8)
    for column, j in enumerate(Q_CLOSES):
        valid = flow['valid'][:, j-4:j+1]
        good = valid.all(axis=1)
        counts[:, column] = valid.sum(axis=1)
        buy = flow['buy'][good, j-4:j+1].sum(axis=1)
        sell = flow['sell'][good, j-4:j+1].sum(axis=1)
        q[good, column] = (buy - sell) / (buy + sell)
    return q, counts


def fit_flow(x, y, dates=None):
    x, y = np.asarray(x, float), np.asarray(y, float)
    status = dict(status='insufficient_pairs', pairs=len(x), variance_x=np.nan)
    if len(x) < 600:
        return status
    if dates is not None and len(set(dates)) < 15:
        status['status'] = 'insufficient_dates'; return status
    if not (np.isfinite(x).all() and np.isfinite(y).all()):
        status['status'] = 'nonfinite_training'; return status
    xm, ym = float(x.mean()), float(y.mean())
    centered = x - xm; var = float(np.mean(centered ** 2)); status['variance_x'] = var
    if var <= 1e-12:
        status['status'] = 'degenerate_predictor'; return status
    b_raw = float(np.sum(centered * (y - ym)) / np.sum(centered ** 2))
    b = float(np.clip(b_raw, -.95, .95)); a = ym - b * xm
    residual = y - a - b*x
    sr = float(np.sqrt(np.mean(residual ** 2)))
    sy = float(np.sqrt(np.mean((y - ym) ** 2)))
    change = y - x; md = float(change.mean()); sd = float(np.sqrt(np.mean((change-md) ** 2)))
    status.update(a=a, b=b, b_raw=b_raw, mean_x=xm, mean_y=ym, residual_scale=sr,
                  raw_scale=sy, mean_change=md, change_scale=sd, clipped=b != b_raw,
                  near_zero=abs(b) <= .05, near_difference=b >= .95,
                  raw_near_zero=abs(b_raw) <= .05, raw_near_difference=abs(b_raw-1.) <= .05)
    if not np.isfinite([a, b_raw, b, sr, sy, md, sd]).all() or min(sr, sy, sd) <= 1e-9:
        status['status'] = 'degenerate_training_scale'; return status
    status['status'] = 'fit'
    return status


def training_for_date(today, q, date_to_row, normal_dates):
    position = normal_dates.searchsorted(today)
    slots = normal_dates[max(0, position-20):position]
    if len(slots) != 20:
        raise ValueError('Calendar construction must supply exactly20 prior normal slots')
    xs, ys, paired_dates, slot_audit = [], [], [], []
    valid_dates, max_stamp = [], None
    for date in slots:
        key = int(date.strftime('%Y%m%d')); row = date_to_row.get(key)
        reason = 'pairs'; n = 0
        if C.roll_guard(date):
            reason = 'predeclared_roll_guard'
        elif row is None:
            reason = 'missing_raw_calendar_date'
        else:
            x, y = q[row, :-1], q[row, 1:]
            good = np.isfinite(x) & np.isfinite(y)
            n = int(good.sum())
            if n:
                xs.extend(x[good]); ys.extend(y[good]); paired_dates.extend([str(date.date())]*n)
                valid_dates.append(date)
                stamp = date + pd.Timedelta(minutes=int(DECISIONS[np.flatnonzero(good)[-1]]))
                max_stamp = stamp if max_stamp is None or stamp > max_stamp else max_stamp
            else:
                reason = 'no_complete_adjacent_pairs'
        slot_audit.append(dict(date=str(date.date()), pairs=n, reason=reason))
    fit = fit_flow(xs, ys, paired_dates)
    fit.update(training_slots=json.dumps(slot_audit, sort_keys=True), distinct_pair_dates=len(valid_dates),
        first_training_date=str(valid_dates[0].date()) if valid_dates else '',
        last_training_date=str(valid_dates[-1].date()) if valid_dates else '',
        max_training_timestamp_ct=str(max_stamp) if max_stamp is not None else '',
        training_slot_count=len(slots))
    if max_stamp is not None and max_stamp >= today:
        raise AssertionError('Current/future observations entered the flow fit')
    return fit


def event_quantities(current, previous, fit):
    e = current - fit['a'] - fit['b'] * previous
    return dict(residual=float(e), innovation_z=float(e / fit['residual_scale']),
        raw_z=float((current - fit['mean_y']) / fit['raw_scale']),
        change_z=float(((current-previous) - fit['mean_change']) / fit['change_scale']))


def model_side(values, model):
    kind, threshold = CONFIGS[model]
    value = values[{'innovation': 'innovation_z', 'raw': 'raw_z', 'change': 'change_z'}[kind]]
    if not np.isfinite(value) or value == 0 or (threshold is not None and abs(value) < threshold):
        return 0
    return -int(np.sign(value))


def signals(out, g, flow, phase, lo, hi, models):
    q, constituent_counts = q_bars(g, flow)
    all_dates = pd.date_range(pd.Timestamp(g.ts[0]) - pd.Timedelta(days=100), hi, freq='D')
    normal_dates = pd.DatetimeIndex([d for d in all_dates if C.normal_cash(d)])
    lookup = {int(date): row for row, date in enumerate(g.dates)}
    rows = {name: [] for name in models}; events, training, calendar = [], [], []
    for day, stamp in enumerate(g.ts):
        date = pd.Timestamp(stamp)
        if not lo <= date <= hi:
            continue
        cal = C.calendar_status(date); normal = C.normal_cash(date); roll = C.roll_guard(date)
        atr = g._flow_atr[day]
        calendar.append(dict(day=day, date=date, calendar_kind=cal['kind'], normal_cash=normal,
            roll_guard=roll, atr=float(atr), atr_finite_positive=bool(np.isfinite(atr) and atr > 0),
            complete_q_bars=int(np.isfinite(q[day]).sum()), expected_q_bars=len(Q_CLOSES),
            actual_current_day_data_never_used_to_select_calendar=True))
        if not normal:
            continue
        fit = training_for_date(date, q, lookup, normal_dates)
        training.append(dict(day=day, date=date, entry_roll_guard=roll, **fit))
        for z, j in enumerate(DECISIONS, start=1):
            current, previous = q[day, z], q[day, z-1]
            reason = ('entry_roll_guard' if roll else 'invalid_prior_ATR' if not np.isfinite(atr) or atr <= 0
                else 'training_' + fit['status'] if fit['status'] != 'fit'
                else 'incomplete_current_or_lag_bar' if not np.isfinite([current, previous]).all() else 'eligible')
            event = dict(day=day, date=date, signal_j=int(j), reason=reason,
                q_current=float(current), q_previous=float(previous),
                current_valid_constituents=int(constituent_counts[day, z]),
                previous_valid_constituents=int(constituent_counts[day, z-1]),
                q_side=0 if not np.isfinite(current) or current == 0 else -int(np.sign(current)))
            if reason == 'eligible':
                values = event_quantities(current, previous, fit); event.update(values)
                event['residual_side'] = -int(np.sign(values['residual']))
                for model in models:
                    side = model_side(values, model); event[model + '_side'] = side
                    if not side:
                        continue
                    rows[model].append(dict(day=day, signal_j=int(j), dj=int(j)+1, side=side,
                        stop=float(np.ceil(.10*atr/.25)*.25), target=float(np.ceil(.15*atr/.25)*.25),
                        exit_j=min(int(j)+30, 895), delta_fraction=float(current), input_last_j=int(j),
                        first_entry_j=int(j)+2, q_current=float(current), q_previous=float(previous),
                        stratum_year=date.year, stratum_hour=int(j)//60, fit_date=str(date.date()), **values))
            events.append(event)
    result = {name: pd.DataFrame(values, columns=SIGCOLS) for name, values in rows.items()}
    frame(out / f'{phase}_calendar_audit.csv', pd.DataFrame(calendar))
    frame(out / f'{phase}_training_audit.csv.gz', pd.DataFrame(training), compress=True)
    frame(out / f'{phase}_event_audit.csv.gz', pd.DataFrame(events), compress=True)
    arrays(out / f'{phase}_q_bar_inputs.npz', q=q, valid_constituent_counts=constituent_counts,
           dates=g.dates, close_minutes=Q_CLOSES)
    equality = {}
    sets = {name: set(zip(s.day, s.signal_j, s.side)) for name, s in result.items()}
    if phase == 'design':
        assert sets['INNOV20'] <= sets['INNOV15'] <= sets['BASE5']
    for name in models:
        for other in models:
            equality[name + '__' + other] = dict(exact_event_side_equality=sets[name] == sets[other],
                intersection=len(sets[name] & sets[other]), first=len(sets[name]), second=len(sets[other]))
    fit_frame = pd.DataFrame(training)
    event_frame = pd.DataFrame(events)
    eligible = event_frame[event_frame.reason.eq('eligible')]
    degeneracy = dict(model_equality=equality, equality_is_not_algebraic_unique_rule_proof=True,
        fitted_dates=int(fit_frame.status.eq('fit').sum()) if len(fit_frame) else 0,
        clipped_fits=int(fit_frame.loc[fit_frame.status.eq('fit'), 'clipped'].fillna(False).sum()) if 'clipped' in fit_frame else 0,
        near_zero_fits=int(fit_frame.loc[fit_frame.status.eq('fit'), 'near_zero'].fillna(False).sum()) if 'near_zero' in fit_frame else 0,
        near_difference_fits=int(fit_frame.loc[fit_frame.status.eq('fit'), 'near_difference'].fillna(False).sum()) if 'near_difference' in fit_frame else 0,
        near_difference_boundary='on projected domain b<=.95, abs(b-1)<=.05 iff b>=.95; avoid floating subtraction',
        eligible_current_vs_residual_side_disagreements=int((eligible.q_side != eligible.residual_side).sum()) if len(eligible) else 0,
        side_basis='q_side=-sign(current q);residual_side=-sign(innovation);both are fade sides',
        eligible_events=len(eligible), input_price_direction_never_determines_side=True)
    dump(out / f'{phase}_degeneracy_audit.json', degeneracy)
    return result


def audit_held(g, flow, trades, sig):
    result = trades.copy(); audit = []
    bykey = {(int(r.day), int(r.signal_j), int(r.side)): r for r in sig.itertuples()}
    pv = valid_ohlc(g)
    for trade in trades.itertuples():
        source = bykey[(int(trade.day), int(trade.signal_j), int(trade.side))]
        day, start, end, scheduled = int(trade.day), int(trade.j0), int(trade.j1), int(source.exit_j)
        segment = slice(start, end+1)
        quantities = (np.isfinite(g.v[day, segment]) & (g.v[day, segment] >= 0))
        have_flow = np.isfinite(flow['total'][day, segment])
        quantity_disagreement = have_flow & np.isfinite(g.v[day, segment]) & (flow['total'][day, segment] != g.v[day, segment])
        audit.append(dict(day=day, signal_j=int(trade.signal_j), side=int(trade.side), j0=start, j1=end,
            scheduled_entry_j=int(source.first_entry_j), scheduled_exit_j=scheduled,
            actual_entry_matches_schedule=start == int(source.first_entry_j),
            invalid_held_ohlc_bars=int((~pv[day, segment]).sum()),
            invalid_held_native_volume_bars=int((~quantities).sum()),
            held_missing_flow_quantity_bars=int((~have_flow).sum()),
            held_source_native_volume_disagreements=int(quantity_disagreement.sum()),
            scheduled_exit_ohlc_valid=bool(pv[day, scheduled]),
            time_exit_displaced=bool(trade.kind == 2 and end != scheduled)))
    a = pd.DataFrame(audit, columns=['day','signal_j','side','j0','j1','scheduled_entry_j','scheduled_exit_j',
        'actual_entry_matches_schedule','invalid_held_ohlc_bars','invalid_held_native_volume_bars',
        'held_missing_flow_quantity_bars','held_source_native_volume_disagreements',
        'scheduled_exit_ohlc_valid','time_exit_displaced'])
    for column in a.columns[5:]:
        result[column] = a[column].to_numpy()
    return result, a


def standard_metrics(trades, days, phase, model):
    rows = []
    for side, label in ((0, 'all'), (1, 'long'), (-1, 'short')):
        selected = trades if side == 0 else trades[trades.side == side]
        for period, dates in [(('2018-22' if phase == 'design' else '2023+'), days)] + [(str(y), days[days.year == y]) for y in sorted(days.year.unique())]:
            subset = selected if '-' in period or '+' in period else selected[selected.date.dt.year == int(period)]
            for basis, column, scale in (('NQ', 'net', 1.), ('MNQ_price_proxy', 'net_mnq', .1),
                                        ('NQ_four_tick_stress', 'stress_four_ticks', 1.)):
                normalized = subset.copy(); normalized['pnl'] *= scale
                rows.append(dict(model=model, period=period, side=label, basis=basis,
                                 **C.stats(normalized, dates, column=column)))
    return rows


def independent_relation(candidate, base):
    keys = ['day', 'signal_j', 'side', 'j0']
    if candidate.duplicated(keys).any() or base.duplicated(keys).any():
        raise ValueError('Independent signal keys must be unique')
    mapping = base[keys].reset_index(names='base_row').merge(candidate[keys], on=keys, how='inner', validate='one_to_one')
    if len(mapping) != len(candidate):
        raise ValueError('Independent candidate is not an exact event/side subset of BASE5')
    matched = base.merge(candidate, on=keys, how='inner', suffixes=('_base', '_kept'), validate='one_to_one')
    for column in ('entry','exit','kind','j1','net','pnl','net_mnq','stress_four_ticks'):
        np.testing.assert_allclose(matched[column+'_base'], matched[column+'_kept'], rtol=0, atol=1e-9)
    kept_rows = np.sort(mapping.base_row.to_numpy(np.int32))
    removed = base.iloc[np.setdiff1d(np.arange(len(base)), kept_rows)].copy()
    assert np.isclose(float(candidate.net.sum())-float(base.net.sum()), -float(removed.net.sum()), rtol=0, atol=1e-8)
    return kept_rows, removed


def subset_distribution(base, candidate, days, mode, runs=1000):
    kept_rows, removed = independent_relation(candidate, base)
    rng = np.random.default_rng(SEED)
    base_dates = pd.DatetimeIndex(base.date)
    day_index = days.get_indexer(base_dates)
    if (day_index < 0).any():
        raise ValueError('Independent signal date absent from full daily calendar')
    nbase, nkept = len(base), len(candidate)
    if nkept > nbase:
        raise ValueError('Candidate count exceeds independent base')
    groups, cells = [], []
    if mode == 'matched':
        cell_base = pd.DataFrame(dict(year=base_dates.year, side=base.side.to_numpy(),
                                     signal_hour=(base.signal_j//60).to_numpy()))
        cell_kept = cell_base.iloc[kept_rows]
        for values, count in cell_kept.groupby(['year','side','signal_hour']).size().items():
            mask = np.ones(nbase, dtype=bool)
            for name, value in zip(('year','side','signal_hour'), values):
                mask &= cell_base[name].to_numpy() == value
            available = np.flatnonzero(mask)
            if len(available) < count:
                raise ValueError('Frozen matched subset cell cannot support the kept count')
            groups.append((available, int(count)))
            cells.append(dict(year=int(values[0]), side=int(values[1]), signal_hour=int(values[2]),
                              base=len(available), kept=int(count)))
    elif mode != 'unconditional':
        raise ValueError('Unknown subset mode')
    selections = np.empty((runs, nkept), dtype=np.int32)
    paths = np.zeros((runs, len(days)), dtype=np.float64)
    totals = np.zeros(runs); dds = np.zeros(runs)
    net_values = base.net.to_numpy(float)
    own_path = candidate.groupby('date').net.sum().reindex(days, fill_value=0.).to_numpy(float)
    own_net, own_dd = float(candidate.net.sum()), R.max_dd(own_path)
    for run in range(runs):
        if mode == 'unconditional':
            selected = np.sort(rng.choice(nbase, nkept, replace=False)).astype(np.int32)
        else:
            selected = np.sort(np.concatenate([rng.choice(index, count, replace=False) for index,count in groups])).astype(np.int32) if groups else np.empty(0, np.int32)
        selections[run] = selected
        paths[run] = np.bincount(day_index[selected], weights=net_values[selected], minlength=len(days))
        totals[run] = float(net_values[selected].sum()); dds[run] = R.max_dd(paths[run])
    joint = (totals < own_net) & (dds > own_dd)
    metrics = pd.DataFrame(dict(run=np.arange(runs), net=totals, max_dd=dds,
        kept_strictly_better_net=totals < own_net, kept_strictly_lower_dd=dds > own_dd,
        kept_joint_beat=joint))
    summary = dict(mode=mode, seed=SEED, runs=runs, non_executable_overlapping_signal_diagnostic=True,
        base_signals=nbase, kept_signals=nkept, removed_signals=len(removed),
        base_net=float(base.net.sum()), kept_net=own_net, removed_net=float(removed.net.sum()),
        removed_mean=float(removed.net.mean()), removed_t=C.tstat(removed.net),
        kept_max_dd=own_dd, strict_joint_beats=int(joint.sum()),
        p_kept_better_net_and_dd=float(joint.mean()), random_net_mean=float(totals.mean()),
        p_random_net_ge_kept=float((totals >= own_net).mean()), cells=cells,
        ties_do_not_count=True, random_subsets_same_size=True,
        date_basis='complete chronological cash-session daily vector, including zero days')
    return summary, metrics, selections, paths, own_path, kept_rows, removed


def quality_resolved(tables):
    return all(int(t.invalid_held_ohlc_bars.sum()) == 0 and not t.time_exit_displaced.any()
               and t.actual_entry_matches_schedule.all() for t in tables)


def completed_phase_markers(phase):
    return list(OUT.rglob(f'{phase}_verified_execution.json'))


def run(out, prereg, phase, selection_commit):
    if completed_phase_markers(phase):
        raise ValueError('Completed phase already exists; do not repeat historical strategy outcomes')
    binding, selected = bind(out, prereg, phase, selection_commit)
    lo = pd.Timestamp('2018-01-01' if phase == 'design' else '2023-01-01')
    hi = pd.Timestamp('2022-12-31' if phase == 'design' else '2026-07-07')
    models = list(CONFIGS) if phase == 'design' else [selected, 'BASE5']
    g = load_native(out, phase, hi)
    audit_atr(out, g, phase, lo, hi)
    flow = intake(out, g, phase, hi)
    sigs = signals(out, g, flow, phase, lo, hi, models)
    days = S.sessions(g, lo, hi)
    ledgers, independent, metrics, daily, counts = {}, {}, [], {}, {}
    for name in models:
        sig = sigs[name]
        frame(out / f'{phase}_{name}_signals.csv.gz', sig, compress=True)
        trades, ct = F.replay(g, sig)
        trades, held = audit_held(g, flow, trades, sig)
        ledgers[name] = trades; counts[name] = dict(signals=len(sig), executed=len(trades), execution=ct)
        frame(out / f'{phase}_{name}_trades.csv.gz', trades, compress=True)
        frame(out / f'{phase}_{name}_held_audit.csv.gz', held, compress=True)
        metrics.extend(standard_metrics(trades, days, phase, name))
        for basis, column in (('NQ','net'),('MNQ_price_proxy','net_mnq'),('NQ_four_tick_stress','stress_four_ticks')):
            daily[name+'__'+basis] = trades.groupby('date')[column].sum().reindex(days, fill_value=0.)
    frame(out / f'{phase}_metrics.csv', pd.DataFrame(metrics))
    frame(out / f'{phase}_daily.csv', pd.DataFrame(daily).rename_axis('date'), index=True)
    dump(out / f'{phase}_counts.json', counts)
    filter_results = {}
    if phase == 'design':
        for name in ['BASE5'] + list(CANDIDATES):
            trades, ct = F.replay(g, sigs[name], independent=True)
            trades, held = audit_held(g, flow, trades, sigs[name])
            independent[name] = trades
            frame(out / f'{phase}_{name}_independent_signals_NONEXECUTABLE.csv.gz', trades, compress=True)
            frame(out / f'{phase}_{name}_independent_held_audit.csv.gz', held, compress=True)
            dump(out / f'{phase}_{name}_independent_counts.json', dict(non_executable=True, execution=ct, signals=len(sigs[name]), replayed=len(trades)))
        base = independent['BASE5'].reset_index(drop=True)
        frame(out / 'design_BASE5_independent_row_mapping_NONEXECUTABLE.csv.gz', base.reset_index(names='base_row'), compress=True)
        for name in CANDIDATES:
            filter_results[name] = {}
            for mode in ('unconditional','matched'):
                summary, distribution, indices, paths, own_path, kept_rows, removed = subset_distribution(base, independent[name], days, mode)
                filter_results[name][mode] = summary
                prefix = f'design_{name}_{mode}_NONEXECUTABLE'
                frame(out / (prefix+'_subset_metrics.csv'), distribution)
                arrays(out / (prefix+'_subset_paths_and_indices.npz'),
                    selected_base_rows=indices, daily_net=paths, dates=days.strftime('%Y-%m-%d').to_numpy(dtype='U10'),
                    kept_base_rows=kept_rows, kept_daily_net=own_path,
                    base_daily_net=base.groupby('date').net.sum().reindex(days,fill_value=0.).to_numpy(float),
                    removed_daily_net=removed.groupby('date').net.sum().reindex(days,fill_value=0.).to_numpy(float))
                dump(out / (prefix+'_summary.json'), summary)
            frame(out / f'design_{name}_removed_independent_NONEXECUTABLE.csv.gz', removed, compress=True)
        dump(out / 'design_filter_diagnostics.json', filter_results)
        gates = {}
        for name in CANDIDATES:
            trades = ledgers[name]; m = C.stats(trades, days); years = trades.groupby(trades.date.dt.year).net.sum()
            control = filter_results[name]['unconditional']
            tables = list(ledgers.values()) + list(independent.values())
            gates[name] = {k: bool(v) for k,v in dict(
                count=m['trades']>=100, net=m['total']>0, trade_t=m['t_trade']>=2,
                daily_nw5=m['t_nw5']>=1.5, profit_factor=m['profit_factor']>=1.20,
                positive_years=int((years>0).sum())>=4, micro_cost_proxy_net=trades.net_mnq.sum()>0,
                four_tick_stress_net=trades.stress_four_ticks.sum()>0,
                candidate_executable_zero_invalid_held_ohlc=int(trades.invalid_held_ohlc_bars.sum())==0,
                all_controls_and_diagnostic_held_paths_resolved=quality_resolved(tables),
                removed_independent_net_negative=control['removed_net']<0,
                kept_independent_total_exceeds_base=control['kept_net']>control['base_net'],
                unconditional_joint_beats=filter_results[name]['unconditional']['strict_joint_beats']>=900,
                year_side_signalhour_joint_beats=filter_results[name]['matched']['strict_joint_beats']>=900).items()}
        passing = [name for name in CANDIDATES if all(gates[name].values())]
        gate = dict(definitive=True, prereg=prereg, configurations_tested=5,
            cumulative_evaluations=65, conservative_unique_rules=63,
            unique_rule_note='No deduction solely for identical realized tickets; algebraic-equivalence review is separate.',
            gates=gates, passing=passing, selected=passing[0] if passing else None,
            validation_allowed=bool(passing), program_continues=True,
            cheap_gate_and_frozen_filter_gates_both_required=True,
            diagnostic_paths_are_not_executable_strategy_or_account_returns=True,
            new_full_history_milestone=False)
    else:
        gate = dict(selected=selected, phase='previously seen historical validation',
                    independent_review_and_dependence_checks_still_required=True)
    # Assert inputs unchanged across execution; preserve the attempt on any race.
    if any(sha(ROOT / path) != digest for path,digest in binding['source'].items()):
        raise ValueError('Input changed while running frozen study; results require reconciliation')
    if phase == 'design':
        dump(out / 'design_gate.json', gate)
    marker = dict(completed_utc=utc(), workspace=str(ROOT), interpreter=sys.executable,
        actual_raw_data_execution=True, phase=phase, prereg=prereg, selected=gate.get('selected'),
        models=models, strategy_timeframe_minutes=5, no_2023plus_read=phase=='design',
        input_binding_sha256=sha(out/f'{phase}_input_binding.json'),
        design_gate_sha256=sha(out/'design_gate.json') if phase=='design' else None,
        native_2017_warmup_used=False, raw_data_last_processed_date=str(hi.date()),
        extra_independent_diagnostic_replays=3 if phase=='design' else 0,
        random_subset_diagnostic_paths=4000 if phase=='design' else 0,
        diagnostic_paths_non_executable=True, summary_gate=gate)
    dump(out / f'{phase}_verified_execution.json', marker)
    summary = pd.DataFrame(metrics)
    print(summary[(summary.period==('2018-22' if phase=='design' else '2023+')) & (summary.side=='all') & (summary.basis=='NQ')]
          [['model','trades','total','t_trade','t_nw5','profit_factor']].to_string(index=False))
    print(json.dumps(gate, indent=2))


def self_check():
    # Synthetic only; never open a raw price, flow or strategy ledger.
    C.engineering()
    assert q_from_sums(np.array([90.,0.]), np.array([10.,1.])) == 79./101.
    assert not np.isclose(q_from_sums(np.array([90.,0.]),np.array([10.,1.])), np.mean([.8,-1.]))
    x = np.tile(np.linspace(-.8,.8,61), 20)
    eps = .07*np.sin(np.arange(len(x))*1.7)
    y = .03+.45*x+eps
    fit = fit_flow(x,y,['date'+str(k//61) for k in range(len(x))])
    assert fit['status']=='fit' and not fit['clipped']
    np.testing.assert_allclose(fit['residual_scale'],np.sqrt(np.mean((y-fit['a']-fit['b']*x)**2)),rtol=0,atol=1e-15)
    projected = fit_flow(x,1.2*x+eps,['date'+str(k//61) for k in range(len(x))])
    assert projected['b']==.95 and projected['clipped'] and projected['near_difference']
    assert fit_flow(x[:599],y[:599])['status']=='insufficient_pairs'
    assert fit_flow(x,y,['one']*len(x))['status']=='insufficient_dates'
    assert fit_flow(np.ones(700),np.arange(700),[str(k//40) for k in range(700)])['status']=='degenerate_predictor'
    normal = pd.DatetimeIndex([d for d in pd.date_range('2018-01-01','2018-06-01') if C.normal_cash(d)])
    dates = np.array([int(d.strftime('%Y%m%d')) for d in normal])
    q = np.tile(np.sin(np.arange(len(Q_CLOSES))*.7)*.4,(len(normal),1))
    q += np.arange(len(normal))[:,None]*.0001
    lookup = {int(date):row for row,date in enumerate(dates)}
    today = normal[35]; before = training_for_date(today,q,lookup,normal)
    changed = q.copy(); changed[35:] = 1e9
    after = training_for_date(today,changed,lookup,normal)
    assert before==after and before['training_slot_count']==20
    missing = dict(lookup); missing.pop(int(normal[34].strftime('%Y%m%d')))
    training = training_for_date(today,q,missing,normal)
    assert len(json.loads(training['training_slots']))==20
    assert json.loads(training['training_slots'])[-1]['pairs']==0
    assert before['max_training_timestamp_ct']<str(today)
    # No synthetic pair can link yesterday's last q to today's first q.
    assert len(Q_CLOSES)-1==len(DECISIONS)==61
    zerob=dict(a=.1,b=0.,residual_scale=.3,mean_y=.1,raw_scale=.3,mean_change=0.,change_scale=.4)
    vals=event_quantities(.8,-.4,zerob)
    assert vals['innovation_z']==vals['raw_z']
    oneb=dict(a=.05,b=1.,residual_scale=.4,mean_y=.1,raw_scale=.3,mean_change=.05,change_scale=.4)
    vals=event_quantities(.8,-.4,oneb)
    np.testing.assert_allclose(vals['innovation_z'],vals['change_z'],rtol=0,atol=1e-15)
    assert model_side(dict(innovation_z=2.,raw_z=2.,change_z=2.),'INNOV15')==-1
    assert model_side(dict(innovation_z=1.7,raw_z=2.,change_z=2.),'INNOV20')==0
    assert model_side(dict(innovation_z=0.,raw_z=0.,change_z=0.),'BASE5')==0
    # Shared execution protects the first held minute and uses worse later gaps/through.
    assert 540+2==542 and 542-1==541
    days=pd.date_range('2018-01-02',periods=3,freq='B')
    base=pd.DataFrame(dict(day=[0,0,1,1,2,2],signal_j=[540,545,540,545,540,545],side=[1,-1,1,-1,1,-1],
        j0=[542,547,542,547,542,547],j1=[543,548,543,548,543,548],entry=[100.]*6,exit=[101.]*6,
        kind=[2]*6,net=[10.,-12.,8.,-9.,6.,-11.],pnl=[20.]*6,net_mnq=[1.]*6,stress_four_ticks=[-5.]*6,
        date=np.repeat(days.to_numpy(),2)))
    kept=base.iloc[[0,2,4]].copy()
    for mode in ('unconditional','matched'):
        a=subset_distribution(base,kept,days,mode,runs=12)
        b=subset_distribution(base,kept,days,mode,runs=12)
        np.testing.assert_array_equal(a[2],b[2]);np.testing.assert_array_equal(a[3],b[3])
        assert np.isclose(a[0]['kept_net']-a[0]['base_net'],-a[0]['removed_net'])
        assert a[2].shape==(12,3) and a[3].shape==(12,3)
    same=subset_distribution(base,base,days,'unconditional',runs=5)
    assert same[0]['strict_joint_beats']==0  # equal net/DD is never a beat
    # All held OHLC fields matter even where the close remains present.
    from types import SimpleNamespace
    toy=SimpleNamespace(o=np.full((1,10),100.),h=np.full((1,10),101.),
        l=np.full((1,10),99.),c=np.full((1,10),100.),v=np.full((1,10),10.))
    toy.h[0,4]=np.nan
    toy_signal=pd.DataFrame([dict(day=0,signal_j=1,side=1,first_entry_j=3,exit_j=6)])
    toy_trade=pd.DataFrame([dict(day=0,signal_j=1,side=1,j0=3,j1=6,kind=2)])
    audited,_=audit_held(toy,dict(total=np.full((1,10),10.)),toy_trade,toy_signal)
    assert audited.invalid_held_ohlc_bars.iloc[0]==1 and not quality_resolved([audited])
    # A successful phase in any engineering-attempt directory blocks repetition.
    from unittest.mock import patch
    fake=OUT/'engineering_attempts'/'synthetic'/'validation_verified_execution.json'
    with patch.object(Path,'rglob',return_value=iter([fake])):
        assert completed_phase_markers('validation')==[fake]
    return dict(passed=True,synthetic_only=True,raw_price_or_flow_files_opened=False,
        strategy_return_trials=0,checks=['shared entry-bar/worse-gap/target-through conventions',
        'ratio of summed quantities, not mean signed fractions','projected AR/intercept/RMS-ddof0/scales',
        'exact20normal-calendar slots; missing dates do not stretch; no overnight lag pairs',
        'future/current flow mutation cannot change past-only fit','b0/raw and b1/change algebraic degeneracies',
        'near-difference projected-boundary flag','fade side/zero/threshold nesting',
        'fixed-seed subset reproducibility, accounting and strict tie treatment',
        'held high missing despite valid close blocks quality','phase-success guard spans engineering directories'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-check',action='store_true')
    parser.add_argument('--prereg')
    parser.add_argument('--phase',choices=('design','validation'))
    parser.add_argument('--selection-commit')
    parser.add_argument('--attempt-id',help='Explicit engineering retry directory; old artifacts remain immutable')
    args=parser.parse_args()
    save(OUT/'.gitignore','numba_cache/\n')
    if args.self_check:
        started=utc()
        check_path=OUT/('synthetic_engineering_checks_'+sha(__file__)[:12]+'.json')
        append_attempt(dict(started_utc=started,kind='synthetic_engineering',status='started',strategy_return_trials=0,script_sha256=sha(__file__)))
        try:
            result=self_check()
            dump(check_path,result)
        except BaseException as error:
            append_attempt(dict(started_utc=started,completed_utc=utc(),kind='synthetic_engineering',status='failed',strategy_return_trials=0,error=repr(error),traceback=traceback.format_exc(),script_sha256=sha(__file__)))
            raise
        append_attempt(dict(started_utc=started,completed_utc=utc(),kind='synthetic_engineering',status='passed',strategy_return_trials=0,script_sha256=sha(__file__),artifact=str(check_path.relative_to(ROOT))))
        print(json.dumps(result,indent=2));return
    if not args.phase or not args.prereg:
        parser.error('Actual phases require --phase and --prereg; --self-check needs no raw inputs')
    out=OUT
    if args.attempt_id:
        if not re.fullmatch(r'[A-Za-z0-9_-]+',args.attempt_id):
            parser.error('Unsafe attempt-id')
        out=OUT/'engineering_attempts'/args.attempt_id
    out.mkdir(parents=True,exist_ok=True)
    started=utc()
    append_attempt(dict(started_utc=started,kind='actual_frozen_phase',phase=args.phase,prereg=args.prereg,
        output=str(out.relative_to(ROOT)),status='started',script_sha256=sha(__file__)))
    try:
        run(out,args.prereg,args.phase,args.selection_commit)
    except BaseException as error:
        append_attempt(dict(started_utc=started,completed_utc=utc(),kind='actual_frozen_phase',phase=args.phase,
            output=str(out.relative_to(ROOT)),status='failed',error=repr(error),traceback=traceback.format_exc()))
        raise
    append_attempt(dict(started_utc=started,completed_utc=utc(),kind='actual_frozen_phase',phase=args.phase,
        output=str(out.relative_to(ROOT)),status='completed',configurations=5 if args.phase=='design' else 2))


if __name__=='__main__':
    main()
