"""Frozen standalone NQ study of modelled ES/ZN correlation-driven risk adjustment.

The covariance portfolio supplies an input only. Its P&L never becomes the NQ ledger.
Actual fund orders, AUM, clocks and vendor contract switch dates are unobserved.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import warnings

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_correlation_risk_budget'
sys.path.insert(0, str(ROOT / 'analysis'))
import numpy as np
import pandas as pd
import codex_t6_study_support as S

C, F = S.C, S.F
os.environ['NUMBA_CACHE_DIR'] = str(OUT / 'numba_cache')
PLAN = 'agents/codex/plans/correlation_risk_budget.md'
CONFIGS = {'CRB005': .005, 'CRB0025': .0025, 'CRB010': .01, 'RP30': None, 'VOL30': 'vol'}
CANDIDATES = ['CRB005', 'CRB0025', 'CRB010']
BASE = {name: 'RP30' for name in CANDIDATES}
SCOLS = ['day', 'signal_j', 'dj', 'side', 'stop', 'target', 'exit_j', 'delta_fraction',
         'input_last_j', 'first_entry_j', 'full_flow', 'vol_flow', 'cov_flow', 'r_es', 'r_zn',
         'es_z', 'vol_sign', 'prior_observations', 'last_prior_observation']


def reference_roll_guard(date):
    date = pd.Timestamp(date)
    if C.roll_guard(date):
        return True
    if date.month not in (2, 5, 8, 11):
        return False
    end = date + pd.offsets.MonthEnd(0)
    start = pd.bdate_range(end=end, periods=12)[0]
    return date.normalize() >= start


def target(cov):
    cov = np.asarray(cov, float)
    if (cov.shape != (2, 2) or not np.isfinite(cov).all() or
            not np.allclose(cov, cov.T, rtol=0, atol=1e-14) or
            (np.diag(cov) <= 0).any() or np.linalg.det(cov) <= 0):
        return None
    sig = np.sqrt(np.diag(cov))
    weights = np.array([sig[1], sig[0]]) / sig.sum()
    vol = np.sqrt(252 * (weights @ cov @ weights))
    if not np.isfinite(vol) or vol <= 0:
        return None
    lev = min(2., .08 / vol)
    return lev * weights


def attribution(cov, returns):
    old = target(cov)
    if old is None:
        return None
    returns = np.asarray(returns, float)
    if not np.isfinite(returns).all() or abs(returns[0]) > .05 or abs(returns[1]) > .03:
        return None
    new = .94 * cov + .06 * np.outer(returns, returns)
    rho = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])
    frozen = new.copy()
    frozen[0, 1] = frozen[1, 0] = rho * np.sqrt(new[0, 0] * new[1, 1])
    full, marginal = target(new), target(frozen)
    nav = 1 + old @ returns
    if full is None or marginal is None or not np.isfinite(nav) or nav <= 0:
        return None
    drift = old[0] * (1 + returns[0]) / nav
    return dict(full_flow=float(full[0] - drift), vol_flow=float(marginal[0] - drift),
                cov_flow=float(full[0] - marginal[0]), r_es=float(returns[0]), r_zn=float(returns[1]),
                es_z=float(abs(returns[0]) / np.sqrt(cov[0, 0])),
                vol_sign=int(np.sign(marginal[0] - drift)), rho_prior=float(rho),
                rho_current=float(new[0, 1] / np.sqrt(new[0, 0] * new[1, 1])),
                old_equity=float(old[0]), old_bond=float(old[1]), new_equity=float(full[0]),
                frozen_equity=float(marginal[0]), drifted_equity=float(drift), model_nav=float(nav))


def model_side(feature, mode):
    if feature is None or abs(feature['full_flow']) < .01 or feature['vol_flow'] == 0:
        return 0
    if mode == 'vol':
        return int(np.sign(feature['vol_flow']))
    side = int(np.sign(feature['full_flow']))
    if mode is None:
        return side
    cov = feature['cov_flow']
    return side if (np.sign(cov) == side and abs(cov) >= .5 * abs(feature['full_flow'])
                    and abs(cov) >= mode) else 0


def covariance_states(observations):
    """Emit state BEFORE each date's observation, including unavailable dates."""
    states = {}
    seed = []
    cov = None
    count, last = 0, None
    for date, ret in observations:
        states[date] = (None if cov is None else cov.copy(), count, last)
        if ret is None:
            continue
        count += 1
        if cov is None:
            seed.append(np.outer(ret, ret))
            if len(seed) == 60:
                cov = np.mean(seed, axis=0)
        else:
            cov = .94 * cov + .06 * np.outer(ret, ret)
        last = date
    return states


def positive_valid(g):
    return S.valid(g) & (g.o > 0) & (g.h > 0) & (g.l > 0) & (g.c > 0)


def reference_history(es, zn, hi):
    maps = [{int(date): i for i, date in enumerate(g.dates)} for g in (es, zn)]
    valid = [positive_valid(g) for g in (es, zn)]
    previous = None
    rows, observations = [], []
    for date in pd.date_range('2017-01-01', hi, freq='D'):
        if C.calendar_status(date)['kind'] in ('weekend', 'holiday'):
            continue
        reason, ret = 'eligible_return', None
        if previous is None:
            reason = 'no_previous_cash_date'
        elif not C.normal_cash(date) or not C.normal_cash(previous):
            reason = 'non_normal_endpoint'
        elif reference_roll_guard(date) or reference_roll_guard(previous):
            reason = 'predeclared_roll_endpoint'
        else:
            positions = [[m.get(int(d.strftime('%Y%m%d'))) for d in (previous, date)] for m in maps]
            if any(i is None for pair in positions for i in pair):
                reason = 'missing_exact_market_date'
            elif not all(v[i, 900] for v, pair in zip(valid, positions) for i in pair):
                reason = 'invalid_exact_1500_endpoint'
            else:
                values = np.array([g.c[p[1], 900] / g.c[p[0], 900] - 1
                                   for g, p in zip((es, zn), positions)])
                if abs(values[0]) > .05 or abs(values[1]) > .03:
                    reason = 'fixed_input_jump_guard'
                else:
                    ret = values
        rows.append(dict(date=date, previous_cash_date=previous, reason=reason,
                         r_es=np.nan if ret is None else ret[0], r_zn=np.nan if ret is None else ret[1]))
        observations.append((date, ret))
        previous = date
    return covariance_states(observations), pd.DataFrame(rows)


def signals(nq, es, zn, states, reference_audit, mode, lo, hi):
    previous = dict(zip(reference_audit.date, reference_audit.previous_cash_date))
    maps = [{int(date): i for i, date in enumerate(g.dates)} for g in (nq, es, zn)]
    valid = [positive_valid(g) for g in (nq, es, zn)]
    rows, audit = [], []
    for date in pd.date_range(lo, hi, freq='D'):
        if C.calendar_status(date)['kind'] in ('weekend', 'holiday'):
            continue
        cov, count, last = states[date]
        prior = previous[date]
        pos = [m.get(int(date.strftime('%Y%m%d'))) for m in maps]
        pp = [m.get(int(prior.strftime('%Y%m%d'))) if pd.notna(prior) else None for m in maps[1:]]
        reason, feature, side = 'eligible', None, 0
        if not C.normal_cash(date) or pd.isna(prior) or not C.normal_cash(prior):
            reason = 'non_normal_endpoint'
        elif reference_roll_guard(date) or reference_roll_guard(prior):
            reason = 'predeclared_roll_endpoint'
        elif cov is None or count < 60:
            reason = 'prior_covariance_warmup'
        elif any(i is None for i in pos + pp):
            reason = 'missing_exact_market_date'
        elif not all(v[i, 841:871].all() for v, i in zip(valid, pos)):
            reason = 'incomplete_known_30min_window'
        elif not all(v[i, 900] for v, i in zip(valid[1:], pp)):
            reason = 'invalid_previous_1500_close'
        elif not np.isfinite(nq._flow_atr[pos[0]]) or nq._flow_atr[pos[0]] <= 0:
            reason = 'prior_ATR_warmup'
        else:
            assert last is not None and last < date
            returns = np.array([g.c[i, 870] / g.c[p, 900] - 1 for g, i, p in zip((es, zn), pos[1:], pp)])
            feature = attribution(cov, returns)
            if feature is None:
                reason = 'invalid_model_or_fixed_partial_jump_guard'
            elif abs(feature['full_flow']) < .01 or feature['vol_flow'] == 0:
                reason = 'shared_full_flow_or_zero_counterfactual_gate'
            else:
                side = model_side(feature, mode)
                reason = 'signal' if side else 'covariance_attribution_or_magnitude_gate'
                if side:
                    atr = nq._flow_atr[pos[0]]
                    rows.append(dict(day=int(pos[0]), signal_j=870, dj=871, side=side,
                                     stop=np.ceil(.10 * atr * 4) / 4, target=np.ceil(.20 * atr * 4) / 4,
                                     exit_j=900, delta_fraction=np.nan, input_last_j=870, first_entry_j=872,
                                     **{k: feature[k] for k in SCOLS if k in feature},
                                     prior_observations=count, last_prior_observation=last))
        audit.append(dict(date=date, previous_cash_date=prior, reason=reason, side=side,
                          prior_observations=count, last_prior_observation=last,
                          decision_j=870, first_entry_j=872, **({} if feature is None else feature)))
    return pd.DataFrame(rows, columns=SCOLS), pd.DataFrame(audit)


def random_drop_paths(candidate, base, days, feature_audit, stratified):
    if stratified:
        meta = feature_audit[['date', 'r_es', 'es_z', 'vol_sign']].copy()
        meta['year'] = meta.date.dt.year
        meta['equity_sign'] = np.sign(meta.r_es).fillna(0).astype(int)
        meta['equity_magnitude_bin'] = np.where(meta.es_z < 1, 0, np.where(meta.es_z < 2, 1, 2))
        cols = ['year', 'equity_sign', 'equity_magnitude_bin', 'vol_sign']
        b = base.merge(meta, on='date', validate='one_to_one')
        kept = candidate.merge(meta, on='date', validate='one_to_one')
        groups, cells = [], []
        for keys, n in kept.groupby(cols).size().items():
            mask = np.ones(len(b), dtype=bool)
            for col, key in zip(cols, keys):
                mask &= b[col].eq(key).to_numpy()
            idx = np.flatnonzero(mask)
            assert len(idx) >= n
            groups.append((idx, int(n)))
            cells.append(dict(zip(cols, [int(k) for k in keys]), base=len(idx), kept=int(n)))
        rng = np.random.default_rng(20261026)
    else:
        b, kept = base, candidate
        groups, cells = [(np.arange(len(base)), len(candidate))], []
        rng = np.random.default_rng(C.SEED)
    if kept.empty:
        return dict(runs=1000, informative=False, p_random_net_ge_kept=1., p_kept_better_net_and_dd=0.)
    totals, dds = [], []
    net = float(kept.net.sum())
    dd = C.R.max_dd(kept.groupby('date').net.sum().reindex(days, fill_value=0.))
    for _ in range(1000):
        idx = np.sort(np.concatenate([rng.choice(i, n, replace=False) for i, n in groups]))
        tx = b.iloc[idx]
        totals.append(float(tx.net.sum()))
        dds.append(C.R.max_dd(tx.groupby('date').net.sum().reindex(days, fill_value=0.)))
    a, draw = np.asarray(totals), np.asarray(dds)
    return dict(runs=1000, informative=True, actual_executable_subsets=True, cells=cells,
                kept_net=net, kept_dd=dd, random_net_mean=float(a.mean()),
                p_random_net_ge_kept=float((a >= net).mean()),
                p_kept_better_net_and_dd=float(((a < net) & (draw > dd)).mean()),
                random_net_totals=totals, random_dd=dds)


def engineering():
    a = np.array([[.0001, -.000025], [-.000025, .000025]])
    b = a.copy(); b[0, 1] = b[1, 0] = .000025
    assert target(b)[0] < target(a)[0]
    assert target(np.ones((2, 2))) is None
    weights = target(a); risk = weights * (a @ weights)
    np.testing.assert_allclose(risk[0], risk[1], rtol=1e-12)
    f = attribution(a, np.array([.01, -.005]))
    np.testing.assert_allclose(f['cov_flow'], f['full_flow'] - f['vol_flow'], rtol=0, atol=1e-14)
    assert model_side(dict(full_flow=.02, vol_flow=.005, cov_flow=.015), .005) == 1
    assert model_side(dict(full_flow=-.02, vol_flow=-.005, cov_flow=-.015), .005) == -1
    assert model_side(dict(full_flow=.02, vol_flow=0., cov_flow=.02), .005) == 0
    assert model_side(dict(full_flow=.02, vol_flow=.03, cov_flow=-.01), .005) == 0
    dates = pd.date_range('2017-01-01', periods=65)
    obs = [(d, np.array([.01*np.sin(i), .005*np.cos(i)])) for i, d in enumerate(dates)]
    original = covariance_states(obs)
    assert original[dates[59]][0] is None and original[dates[60]][1] == 60
    obs[60] = (dates[60], np.array([100., 100.]))
    changed = covariance_states(obs)
    for date in dates[:61]:
        if original[date][0] is not None:
            np.testing.assert_array_equal(original[date][0], changed[date][0])
    obs[61] = (dates[61], None)
    changed = covariance_states(obs)
    assert changed[dates[62]][1] == changed[dates[61]][1]
    assert reference_roll_guard('2024-02-28') and reference_roll_guard('2024-03-14')
    assert not reference_roll_guard('2024-04-15')
    assert 870 + 2 == 872
    C.engineering()
    return dict(passed=True, checks=['two-asset equal risk and correlation attribution',
        'prior state emitted before current/future observations', '60 actual observations; missing update skipped',
        'shared zero-V eligibility and covariance-direction gates', 'separate Treasury/equity roll guards',
        'one-extra-minute entry; shared calendar/entry-bar/worse-gap/target-through'])


def load_reference(symbol, hi):
    # Include December2017 and no2023+ price file during design; S.load deliberately omits2017.
    years = '20[12][012789]' if hi.year == 2022 else '20*'
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        return C.trim_grid(S.Grid24(f'data/{symbol}_1min_{years}.csv', night_pattern=''), hi)


def run(prereg, phase, selection=None):
    started = datetime.now(timezone.utc).isoformat()
    S.bind(OUT, PLAN, prereg, CONFIGS, ['NQ', 'ES', 'ZN'], 55, ['codex_correlation_risk_budget.py'])
    C.dump(OUT / 'engineering_checks.json', engineering())
    selected = None
    if phase == 'validation':
        path = 'analysis/outputs/codex_correlation_risk_budget/design_complete_gate.json'
        gate = json.loads((ROOT / path).read_text())
        selected = gate['selected']
        if selected is None or not selection:
            raise ValueError('Rejected/uncommitted design: historical validation closed')
        assert subprocess.check_output(['git', 'show', f'{selection}:{path}'], cwd=ROOT) == (ROOT / path).read_bytes()
    lo = pd.Timestamp('2018-01-01' if phase == 'design' else '2023-01-01')
    hi = pd.Timestamp('2022-12-31' if phase == 'design' else '2026-10-09')
    intake = {s: S.intake(s, hi) for s in ('NQ', 'ES', 'ZN')}
    C.dump(OUT / f'{phase}_price_intake.json', intake)
    if any(v['conflicting_keys'] for v in intake.values()):
        raise ValueError('NEEDS DATA: conflicting native source keys')
    nq, es, zn = S.load('NQ', hi), load_reference('ES', hi), load_reference('ZN', hi)
    states, ref_audit = reference_history(es, zn, hi)
    C.csv(OUT / f'{phase}_daily_reference_audit.csv', ref_audit)
    configs = CONFIGS if phase == 'design' else {k: CONFIGS[k] for k in (selected, 'RP30')}
    sigs, audits, counts = {}, {}, {}
    for name, mode in configs.items():
        sigs[name], audits[name] = signals(nq, es, zn, states, ref_audit, mode, lo, hi)
        C.csv(OUT / f'{phase}_{name}_event_audit.csv', audits[name])
        counts[name] = audits[name].reason.value_counts().to_dict()
    days = S.sessions(nq, lo, hi)
    ledgers, df, _ = S.evaluate(OUT, nq, sigs, days, phase, prereg, CANDIDATES, BASE, 55, counts=counts)
    uniforms = json.loads((OUT / f'{phase}_filter_diagnostics.json').read_text())
    paths, strata, counterfactual = {}, {}, {}
    for name in CANDIDATES:
        if name not in configs:
            continue
        paths[name] = random_drop_paths(ledgers[name], ledgers['RP30'], days, audits['RP30'], False)
        if paths[name]['informative']:
            for k in ('random_net_mean', 'p_random_net_ge_kept', 'p_kept_better_net_and_dd'):
                np.testing.assert_allclose(paths[name][k], uniforms[name][k], rtol=0, atol=1e-8)
        strata[name] = random_drop_paths(ledgers[name], ledgers['RP30'], days, audits['RP30'], True)
        if phase == 'design':
            tx = ledgers[name]
            other = ledgers['VOL30'][ledgers['VOL30'].date.isin(tx.date)]
            assert len(other) == len(tx) and other.date.nunique() == len(tx)
            counterfactual[name] = dict(candidate_tickets=len(tx), matched_counterfactual_tickets=len(other),
                candidate_net=float(tx.net.sum()), counterfactual_net=float(other.net.sum()),
                same_side_fraction=float(tx[['date', 'side']].merge(other[['date', 'side']], on='date').eval('side_x == side_y').mean()),
                side_changing_whole_rule_comparison=True)
    C.dump(OUT / f'{phase}_uniform_draws.json', paths)
    C.dump(OUT / f'{phase}_stratified_drops.json', strata)
    if phase == 'design':
        C.dump(OUT / 'design_frozen_correlation_comparison.json', counterfactual)
        basic = json.loads((OUT / 'design_gate.json').read_text())
        gates = {}
        for name in CANDIDATES:
            f, s, v = uniforms[name], strata[name], counterfactual[name]
            checks = dict(removed_loses=f['removed_avg'] < 0, kept_total_ge_base=f['kept_net'] >= f['base_net'],
                          uniform_net=f['p_random_net_ge_kept'] <= .10,
                          uniform_joint=f['p_kept_better_net_and_dd'] >= .90,
                          stratified_net=s['p_random_net_ge_kept'] <= .10,
                          stratified_joint=s['p_kept_better_net_and_dd'] >= .90,
                          matched_frozen_correlation=v['candidate_net'] >= v['counterfactual_net'])
            gates[name] = {**basic['gates'][name], **{k: bool(v) for k, v in checks.items()}}
        passing = [k for k, v in gates.items() if all(v.values())]
        selected = passing[0] if passing else None
        C.dump(OUT / 'design_complete_gate.json', dict(prereg=prereg, gates=gates, passing=passing,
            selected=selected, counted_program_evaluations=60, unique_program_models=59,
            exact_actual_subset_controls=True, program_continues=True))
    marker = OUT / f'{phase}_verified_execution.json'
    if not marker.exists():
        C.dump(marker, dict(started_utc=started, completed_utc=datetime.now(timezone.utc).isoformat(),
            workspace=str(ROOT), interpreter=sys.executable, actual_raw_data_execution=True,
            models=list(configs), selected=selected, prereg=prereg))
    print('Complete gate selected:', selected, flush=True)
    return ledgers, df, selected


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['design', 'validation'])
    parser.add_argument('--prereg')
    parser.add_argument('--selection')
    parser.add_argument('--self-check', action='store_true')
    args = parser.parse_args()
    if args.self_check:
        print(engineering())
    else:
        if not args.phase or not args.prereg:
            parser.error('--phase and --prereg required')
        run(args.prereg, args.phase, args.selection)
