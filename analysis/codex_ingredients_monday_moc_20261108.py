"""Frozen Monday / Bridge / ES MOC ingredient diagnostics; no portfolio or live access."""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import warnings

import numpy as np
import pandas as pd
import metrics as M
import resampling as R
import codex_ingredients_three_20261108 as B
import codex_ingredients_events_20261108 as E

warnings.filterwarnings('ignore', category=RuntimeWarning)
ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'agents/codex/inputs/ingredients_monday_moc_20261108'
OUT = ROOT / 'analysis/outputs/codex_ingredients_monday_moc_20261108'
PLAN = 'agents/codex/plans/ingredients_monday_moc_20261108.md'
CODE = 'analysis/codex_ingredients_monday_moc_20261108.py'
SEED = 80313
B.INPUT, B.SEED = INPUT, SEED
check, sha = E.check, E.sha
FAMILIES = {
    'MON': ['original', 'no_Monday_gate', 'short_direction', 'no_stop', 'exit_1000'],
    'BR': ['original', 'no_ADX_band', 'no_DI_direction', 'no_target', 'RTH_entry'],
    'MOC': ['original', 'no_move_gate', 'fade_direction', 'no_stop', 'hold_1515'],
}


def extracted(name, names, namespace):
    text = (INPUT / name).read_text()
    tree = ast.parse(text)
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    check({n.name for n in nodes} == set(names), 'Source function missing')
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(INPUT / name), 'exec'), namespace)
    return namespace


def function_text(name, function):
    text = (INPUT / name).read_text()
    return ast.get_source_segment(text, next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == function))


def replace_once(source, before, after):
    check(source.count(before) == 1, 'Instrumentation hook mismatch: ' + before)
    return source.replace(before, after)


def namespaces(g, es):
    basic = {'np': np, 'pd': pd, 'PV': 20., 'COST': 7.25, 'TICK': .25,
             'g': g, 'atr': g.daily_atr(15), 'dts_all': pd.DatetimeIndex(g.ts)}
    original_mon = extracted('monday_long_test.py', ['trades'], dict(basic))
    text = function_text('monday_long_test.py', 'trades')
    text = replace_once(text, 'dts_all[d].dayofweek != dow', '(dow is not None and dts_all[d].dayofweek != dow)')
    text = replace_once(text, 'px, j1, kind = None, jx, 0', 'px, j1, kind = None, jx, 2')
    text = replace_once(text, 'j1 = j; break', 'j1 = j; kind = 0; break')
    mon = dict(basic)
    exec(compile(text, '<MON gate/exit metadata only>', 'exec'), mon)
    br0 = extracted('bridge_monday_long_test.py', ['nyse_holidays', 'bridge_adx', 'bridge'],
                    {'np': np, 'pd': pd, 'jof': lambda t: np.asarray(t) // 100 * 60 + np.asarray(t) % 100,
                     'PV': 20., 'TICK': .25, 'COST': 7.25})
    text = function_text('bridge_monday_long_test.py', 'bridge')
    text = replace_once(text, 'sig = (10 <= a < 50) and didiff > 0',
                         'sig = (10 <= a < 50) and didiff > 0\n        if filt == "no_ADX_band": sig = didiff > 0\n        if filt == "no_DI_direction": sig = 10 <= a < 50')
    text = replace_once(text, 'slips=0, date=ts[d], sig=sig, net=',
                         'entry_row=e_row, entry_j_actual=e_j, exit_row=(rr if kind == 1 else d), '
                         'exit_j_actual=(j if kind == 1 else int(ok[-1])), scheduled_exit_j=jof(exit_t), '
                         'slips=0, date=ts[d], sig=sig, net=')
    br = dict(br0)
    exec(compile(text, '<BR separate gates and actual exit metadata>', 'exec'), br)
    moc = extracted('s_rank_es_round1_test.py', ['trades'],
                    {'np': np, 'pd': pd, 'PV': 50., 'COMM': 5., 'TICK': .25})
    return mon, original_mon, br, br0, moc


def feature_admission(g, es, A):
    rows, exclusions = [], []
    ts, atr = pd.DatetimeIndex(g.ts), g.daily_atr(15)
    for d in g.trading:
        day = ts[d]
        if day.dayofweek == 0:
            a, di = A[d - 1]
            rows.append({'family': 'MON/BR', 'date': str(day.date()), 'atr': atr[d],
                         'MON_entry_missing': not np.isfinite(g.o[d, 511]),
                         'previous_state_reference': str(ts[d - 1].date()), 'ADX7': a, 'DI_difference': di,
                         'ADX_band': 10 <= a < 50, 'DI_positive': di > 0,
                         'Sunday_1900_close_missing': not np.isfinite(g.c[d - 1, 1140]),
                         'Monday_0830_close_missing': not np.isfinite(g.c[d, 510]),
                         'source_Monday_1455_close_missing': not np.isfinite(g.c[d, 895])})
            if not np.isfinite(g.o[d, 511]):
                exclusions.append({'family': 'MON', 'date': str(day.date()), 'reason': 'unknown_entry_open'})
    tr = es.trading
    ea = es.daily_atr(15)
    cf = pd.Series(es.c.ravel()).ffill().to_numpy()
    moves = cf[tr * 1440 + 890] - cf[tr * 1440 + 840]
    full = es.last_j[tr] >= 900
    for k, d in enumerate(tr):
        rows.append({'family': 'MOC', 'date': str(pd.Timestamp(es.ts[d]).date()), 'atr': ea[d],
                     'move': moves[k], 'source_full': full[k], 'magnitude_gate': abs(moves[k]) >= .3 * ea[d],
                     'reference_close_missing': not np.isfinite(es.c[d, 840]),
                     'decision_close_missing': not np.isfinite(es.c[d, 890]),
                     'entry_open_missing': not np.isfinite(es.o[d, 891])})
    return rows, exclusions, moves, full


def canonical(t, family, variant, g):
    t = t.copy().reset_index(drop=True)
    check(len(t) > 0, 'Empty source case: ' + family + '/' + variant)
    t['date'] = pd.to_datetime(t.date)
    pv, commission = (50., 5.) if family == 'MOC' else (20., 7.25)
    target = t.kind.eq(1).to_numpy()
    sides = t.side.to_numpy()
    original_net = t.net.copy()
    t['raw_entry'] = t.entry - t.side * .25
    t['raw_exit'] = t.exit + t.side * .25 * (~target)
    t['gross'] = (t.raw_exit - t.raw_entry) * t.side * pv
    t['commission'] = commission
    t['slippage'] = .25 * pv * (1 + (~target).astype(int))
    t['net'] = t.gross - t.commission - t.slippage
    check(np.allclose(t.net, original_net, atol=1e-7), 'Symbol/cost/source identity mismatch')
    check(np.isfinite(t[['entry', 'exit', 'gross', 'net']]).all().all(), 'Nonfinite source execution')
    t['micro_net'] = t.gross / 10 - 1.25 - t.slippage / 10
    t['extra_tick_cost_net'] = t.net - t.slippage
    t['symbol'] = 'ES' if family == 'MOC' else 'NQ'
    adverse, missing, fallback, starts, ends, sunday = [], [], [], [], [], []
    for row in t.itertuples():
        if family == 'BR':
            a = int(row.entry_row) * 1440 + int(row.entry_j_actual)
            first = a + 1  # entry at CLOSE; exclude the earlier entry-bar range
            x = int(row.exit_row) * 1440 + int(row.exit_j_actual)
            scheduled = int(row.day) * 1440 + int(row.scheduled_exit_j)
        else:
            a = int(row.day) * 1440 + int(row.j0)
            first = a
            x = int(row.day) * 1440 + int(row.j1)
            scheduled = int(row.day) * 1440 + (600 if family == 'MON' and variant == 'exit_1000' else
                                             (900 if family == 'MON' or variant != 'hold_1515' else 915))
        check(first <= x, 'Execution time ordering')
        prices = (g.l if row.side > 0 else g.h).ravel()
        stop_exit = row.kind == 0
        end = x if stop_exit else x + 1
        seen = prices[first:end]
        seen = seen[np.isfinite(seen)]
        seen = np.r_[row.raw_entry, seen, row.raw_exit]
        worst = seen.min() if row.side > 0 else seen.max()
        adverse.append(min((worst - row.raw_entry) * row.side * pv - commission - row.slippage, row.net))
        matrix = np.column_stack([getattr(g, col).ravel()[first:x + 1] for col in 'ohlc'])
        missing.append(int((~np.isfinite(matrix)).any(axis=1).sum()))
        fallback.append(bool(row.kind == 2 and x != scheduled))
        starts.append(a); ends.append(x)
        sunday.append(bool(family == 'BR' and int(row.exit_row) < int(row.day)))
    t['source_adverse_mark'] = adverse
    t['missing_held_bars'] = missing
    t['last_close_fallback'] = fallback
    t['entry_i_actual'], t['exit_i_actual'] = starts, ends
    t['Sunday_exit'] = sunday
    t['target_bar_path_ambiguous'] = target
    t['family'], t['variant'] = family, variant
    return t.sort_values('date').reset_index(drop=True)


def fixtures():
    class Tiny:
        def daily_atr(self, n):
            return np.full(self.D, 10.)
    g = Tiny()
    g.D = 2
    g.ts = pd.to_datetime(['2024-01-07', '2024-01-08']).to_numpy()
    g.dates = np.array([20240107, 20240108])
    g.trading = np.array([1])
    for name in 'ohlc':
        setattr(g, name, np.full((2, 1440), 100.))
    g.last_j = np.full(2, 1439)
    mon, mon0, br, br0, moc = namespaces(g, g)
    t = mon['trades']()
    t0 = mon0['trades']()
    check(np.allclose(t.net, t0.net) and t.kind.eq(2).all(), 'MON metadata changed prices')
    g.h[0, 1141] = 201.
    A = {0: (20., 5.), 1: (20., 5.)}
    t = br['bridge'](g, A)
    check(np.allclose(t.net, br0['bridge'](g, A).net), 'BR metadata changed prices')
    c = canonical(t, 'BR', 'original', g)
    check(c.Sunday_exit.all() and (c.exit_i_actual == 1141).all(), 'Sunday target clock lost')
    check(np.allclose(c.gross, 2000) and np.allclose(c.net, 1987.75) and np.allclose(c.micro_net, 198.25), 'Limit cost bridge')
    di_parent = br['bridge'](g, {0: (60., 5.)}, filt='no_ADX_band')
    adx_parent = br['bridge'](g, {0: (20., -5.)}, filt='no_DI_direction')
    check(len(di_parent) == len(adx_parent) == 1, 'Separate gate interventions')
    check(len(br['bridge'](g, {0: (60., 5.)})) == 0, 'Original combined gate changed')
    g.o[1, 892], g.h[1, 892], g.l[1, 892], g.c[1, 892] = 97., 98., 96., 97.
    t = moc['trades'](g, np.array([1]), 1, 891, 900, 2.5)
    c = canonical(t, 'MOC', 'original', g)
    check(np.allclose(c.net, -180) and np.allclose(c.micro_net, -18.75), 'ES multiplier/gap/fee isolation')
    return {'groups_passed': 5, 'market_returns_computed': False}


def run(name):
    dependencies = ['analysis/metrics.py', 'analysis/resampling.py',
                    'analysis/codex_ingredients_three_20261108.py', 'analysis/codex_ingredients_events_20261108.py']
    for path in [PLAN, CODE, 'agents/codex/evidence/ingredients_monday_moc_20261108.md'] + dependencies + [p.relative_to(ROOT).as_posix() for p in INPUT.iterdir()]:
        check(subprocess.check_output(['git', 'show', 'HEAD:' + path], cwd=ROOT) == (ROOT / path).read_bytes(), 'Commit exact definitions/dependencies before returns: ' + path)
    manifest = json.loads((INPUT / 'sources.json').read_text())
    for item in manifest['files']:
        check(sha(INPUT / Path(item['path']).name) == item['sha256'], 'Pinned source differs')
    if name == 'recent':
        design = json.loads((OUT / 'design/summary.json').read_text())
        check(design['implementation_gates_passed'] and design['script_sha256'] == sha(ROOT / CODE), 'Design gate or code changed')
    start, end = ('2018-01-01', '2022-12-30') if name == 'design' else ('2023-01-01', '2026-10-09')
    fixture_receipt = fixtures()
    nq, es, inputs = B.grids(end)
    views = []
    for g in (nq, es):
        view = copy.copy(g)
        dates = pd.DatetimeIndex(g.ts[g.trading])
        view.trading = g.trading[(dates >= start) & (dates <= end)]
        views.append(view)
    g, ge = views
    mon, mon0, br, br0, moc = namespaces(g, ge)
    A = br['bridge_adx'](nq)
    features, exclusions, moves, full = feature_admission(g, ge, A)
    dest = OUT / name
    dest.mkdir(parents=True, exist_ok=False)
    pd.DataFrame(features).to_csv(dest / 'features.csv', index=False)
    B.dump(dest / 'pre_return_admission.json', {'start': start, 'end': end, 'raw_inputs': inputs,
            'source_coverage_not_live_availability': True, 'fixture_receipt': fixture_receipt,
            'before_pricing_exclusions': exclusions, 'dependency_sha256': {p: sha(ROOT / p) for p in dependencies}})
    raw_cases = {}
    for variant in FAMILIES['MON']:
        kwargs = {'dow': None} if variant == 'no_Monday_gate' else ({'side': -1} if variant == 'short_direction' else
                  ({'stop_atr': 0} if variant == 'no_stop' else ({'exit_j': 600} if variant == 'exit_1000' else {})))
        raw_cases['MON/' + variant] = mon['trades'](**kwargs)
    for variant in FAMILIES['BR']:
        kwargs = {'filt': variant} if variant in ('no_ADX_band', 'no_DI_direction') else (
                  {'target': None} if variant == 'no_target' else ({'rth_only': True} if variant == 'RTH_entry' else {}))
        raw_cases['BR/' + variant] = br['bridge'](g, A, **kwargs)
    tr, atr = ge.trading, ge.daily_atr(15)[ge.trading]
    valid = full & np.isfinite(moves) & np.isfinite(atr) & (atr > 0) & (moves != 0)
    for variant in FAMILIES['MOC']:
        mask = valid & ((np.abs(moves) >= .3 * atr) if variant != 'no_move_gate' else True)
        side = np.sign(moves[mask]).astype(int) * (-1 if variant == 'fade_direction' else 1)
        stops = np.full(mask.sum(), np.inf) if variant == 'no_stop' else .25 * atr[mask]
        raw_cases['MOC/' + variant] = moc['trades'](ge, tr[mask], side, 891, 915 if variant == 'hold_1515' else 900, stops)
    originals = {'MON': mon0['trades'](), 'BR': br0['bridge'](g, A)}
    parity = {}
    for family, source in originals.items():
        instrumented = raw_cases[family + '/original']
        joined = instrumented[['date', 'entry', 'exit', 'net']].merge(source[['date', 'entry', 'exit', 'net']], on='date', suffixes=('_new', '_source'))
        check(len(joined) == len(source) == len(instrumented) and all(np.allclose(joined[k + '_new'], joined[k + '_source']) for k in ('entry', 'exit', 'net')), 'Original source-price parity failure')
        parity[family] = len(joined)
    vector = extracted('s_rank_moc_round2_test.py', ['sim'], {'np': np, 'pd': pd})
    moc_mask = valid & (np.abs(moves) >= .3 * atr)
    S = SimpleNamespace(G=ge, tick=.25, full=full, atr=atr, tr=tr, pv=50., comm=5.)
    reference = vector['sim'](S, np.where(moc_mask, np.sign(moves), 0), 891, 900, .25)
    reference = reference.rename_axis('date').reset_index()
    original_moc = raw_cases['MOC/original'].reset_index(drop=True)
    joined = original_moc[['date', 'entry', 'exit', 'net']].merge(reference[['date', 'entry', 'exit', 'net']], on='date', suffixes=('_new', '_source'))
    check(len(joined) == len(original_moc) == len(reference) and all(np.allclose(joined[k + '_new'], joined[k + '_source']) for k in ('entry', 'exit', 'net')), 'MOC independent source-price parity')
    parity['MOC'] = len(joined)
    results, statistics, calendars = {}, [], {}
    for key, t in raw_cases.items():
        family, variant = key.split('/')
        grid = ge if family == 'MOC' else g
        t = canonical(t, family, variant, grid)
        if variant in ('no_stop', 'no_target'):
            check(not t.kind.eq(0 if variant == 'no_stop' else 1).any(), 'Exit intervention not isolated')
        calendar = pd.DatetimeIndex(grid.ts[grid.trading])
        calendars[family] = calendar
        results[key] = t
        stem = key.replace('/', '__')
        t.to_csv(dest / (stem + '_trades.csv'), index=False)
        B.daily(t, calendar).to_csv(dest / (stem + '_daily.csv'), header=['net'])
        for side in ('all', 'long', 'short'):
            sub = t if side == 'all' else t[t.side == (1 if side == 'long' else -1)]
            statistics.append({'family': family, 'variant': variant, 'period': name, 'side': side, **E.metrics(sub, calendar)})
        for year in sorted(set(calendar.year)):
            statistics.append({'family': family, 'variant': variant, 'period': str(year), 'side': 'all',
                               **E.metrics(t[t.date.dt.year == year], calendar[calendar.year == year])})
    effects, controls = [], {}
    for key, t in results.items():
        family, variant = key.split('/')
        calendar = calendars[family]
        if variant == 'original':
            R.bootstrap(B.daily(t, calendar), n=1000, block=20, seed=SEED, chunk=250).loc[['annual', 'sharpe']].to_csv(dest / (family + '_original_bootstrap.csv'))
            continue
        delta = B.daily(results[family + '/original'], calendar) - B.daily(t, calendar)
        bounds = R.bootstrap(delta, n=1000, block=20, seed=SEED, chunk=250).loc['annual']
        effects.append({'family': family, 'intervention': variant, 'base_minus_intervention_net': delta.sum(),
                        'annual_effect_p5': bounds.p5, 'annual_effect_p50': bounds.p50, 'annual_effect_p95': bounds.p95})
    for key in ('MON/no_Monday_gate', 'BR/no_ADX_band', 'BR/no_DI_direction', 'MOC/no_move_gate'):
        family = key.split('/')[0]
        controls[key] = B.filter_control(results[family + '/original'], results[key], calendars[family])
    pd.DataFrame(statistics).to_csv(dest / 'metrics.csv', index=False)
    pd.DataFrame(effects).to_csv(dest / 'paired_effects.csv', index=False)
    summary = {'phase': name, 'start': start, 'end': end, 'rule_cases': 15, 'implementation_gates_passed': True,
               'script_sha256': sha(ROOT / CODE), 'plan_sha256': sha(ROOT / PLAN),
               'plan_commit': subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', PLAN], cwd=ROOT, text=True).strip(),
               'input_data_ref': B.DATA_REF, 'raw_inputs': inputs, 'dependency_sha256': {p: sha(ROOT / p) for p in dependencies},
               'source_price_parity': parity, 'ES_cost_bridge_verified': True, 'pure_filter_controls': controls,
               'source_path_limits': {k: {'missing_held_bars': int(t.missing_held_bars.sum()),
                    'last_close_fallbacks': int(t.last_close_fallback.sum()), 'Sunday_targets_preserved': int(t.Sunday_exit.sum())} for k, t in results.items()},
               'seed': SEED, 'resampling_draws': 1000, 'new_rule_selected': False, 'portfolio_tests_run': False}
    B.dump(dest / 'summary.json', summary)
    print(pd.DataFrame(statistics).query('period==@name and side=="all"')
          [['family', 'variant', 'trades', 'net_total', 't_trade', 'profit_factor', 'max_dd']].round(3).to_string(index=False), flush=True)
    print(json.dumps({'phase': name, 'gates': True, 'source_price_parity': parity}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['fixtures', 'design', 'recent'])
    args = parser.parse_args()
    if args.phase == 'fixtures':
        print(fixtures())
    else:
        run(args.phase)
