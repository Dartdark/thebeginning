"""Frozen EOS/NFP/CL ingredient attribution. No optimizer, broker or account model."""
import argparse
import ast
import glob
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import warnings

import numpy as np
import pandas as pd
import metrics as M
import resampling as R
import codex_ingredients_three_20261108 as B

warnings.filterwarnings('ignore', category=RuntimeWarning)
ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('/workspace/thebeginning')
INPUT = ROOT / 'agents/codex/inputs/ingredients_events_20261108'
OUT = ROOT / 'analysis/outputs/codex_ingredients_events_20261108'
REF = 'fe35af99aa90d7f31b91f8693859251bb44dd9ab'
PLAN = 'agents/codex/plans/ingredients_events_20261108.md'
CODE = 'analysis/codex_ingredients_events_20261108.py'
SEED = 20261109
B.SEED = SEED
GOOD_FRIDAYS = {'2018-03-30', '2019-04-19', '2020-04-10', '2021-04-02', '2022-04-15',
                '2023-04-07', '2024-03-29', '2025-04-18', '2026-04-03'}
CLOSED_EXPIRY = ['2019-04-19', '2022-04-15', '2025-04-18', '2026-06-19']


def check(value, message):
    if not value:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def functions(name, wanted, namespace):
    tree = ast.parse((INPUT / name).read_text())
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in wanted]
    check({n.name for n in nodes} == set(wanted), 'Missing source function')
    for node in nodes:
        node.decorator_list = []
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(INPUT / name), 'exec'), namespace)
    return namespace


def setup():
    basic = {'np': np, 'pd': pd, 'glob': glob, 'NMIN24': 1440}
    G = functions('grid24.py', ['jof', 'Grid24'], basic)['Grid24']
    jof = basic['jof']
    walker = functions('grid.py', ['_walk', 'execute'],
                       {'np': np, 'pd': pd, 'POINT_VALUE': 20., 'COST': 7.25, 'FILL_THROUGH': 1.})
    news = functions('news_meanrev_test.py', ['sim', 'row', 'reaction_trades'],
                     {'np': np, 'pd': pd, 'jof': jof, 'PV': 20., 'TICK': .25, 'COST': 7.25})
    events = functions('event_days.py', ['bar_range', 'release_days'], {'np': np, 'pd': pd, 'jof': jof})
    calendar = functions('calendar_flows.py', ['calendar'],
                         {'np': np, 'pd': pd, 'NYSE_CLOSED_THIRD_FRIDAYS': CLOSED_EXPIRY})
    sunday = functions('s_rank_gap_round2_test.py', ['Sym', 'sunday_frame'],
                       {'np': np, 'pd': pd, 'jof': jof, 'SPEC': {'CL': ('cl', 1000., .01, 7.25)}})
    cl = functions('cl_sunday_fade_confirm.py', ['python_trades'],
                   {'np': np, 'pd': pd, 'jof': jof, 'PV': 1000., 'TICK': .01, 'COMM': 7.25})
    return G, jof, walker, news, events, calendar, sunday, cl


def grids(G, end):
    manifest = {}
    with tempfile.TemporaryDirectory(prefix='ingredients_events_') as temporary:
        temporary = Path(temporary)
        for year in range(2017, pd.Timestamp(end).year + 1):
            for prefix, alias in [('NQ_1min_', 'nq_day_'), ('NQ_1min_ON_', 'nq_night_'), ('CL_1min_', 'cl_')]:
                name = f'{prefix}{year}.csv'
                path = SOURCE / 'data' / name
                raw = path.read_bytes()
                blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
                expected = subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', REF + ':data/' + name], text=True).strip()
                check(blob == expected, 'Raw snapshot mismatch: ' + name)
                clock = pd.read_csv(path, usecols=['date', 'time'])
                check(not clock.duplicated(['date', 'time']).any(), 'Duplicate bars: ' + name)
                manifest[name] = {'bytes': len(raw), 'git_blob': blob, 'sha256': hashlib.sha256(raw).hexdigest()}
                (temporary / f'{alias}{year}.csv').symlink_to(path)
        nq = G(str(temporary / 'nq_day_*.csv'), str(temporary / 'nq_night_*.csv'))
        cl = G(str(temporary / 'cl_*.csv'), night_pattern='')
    for g in (nq, cl):
        n = int(np.searchsorted(pd.DatetimeIndex(g.ts), pd.Timestamp(end), side='right'))
        for name in ('o', 'h', 'l', 'c', 'v', 'ts', 'dates', 'last_j'):
            setattr(g, name, getattr(g, name)[:n])
        g.D = n
        g.trading = g.trading[g.trading < n]
    return nq, cl, manifest


def jobs(nq, cl, tools, start, end):
    _, jof, _, _, E, CF, S, _ = tools
    atr, catr = nq.daily_atr(15), cl.daily_atr(15)
    tr, ts = nq.trading, pd.DatetimeIndex(nq.ts)
    expiry = set(CF['calendar'](nq).query('opex').index.astype(int))
    releases = set(E['release_days'](nq).astype(int))
    records, cases, exclusions = [], {}, []
    for family, names in [('EOS', ['original', 'no_expiry_gate', 'opposite_direction', 'no_stop', 'exit_0900']),
                          ('NFP', ['original', 'no_spike_gate', 'no_payroll_calendar', 'opposite_direction', 'no_stop']),
                          ('CL', ['original', 'no_upgap_gate', 'opposite_direction', 'no_stop', 'exit_0300'])]:
        for variant in names:
            cases[family + '/' + variant] = []

    def admit(key, g, d, day, a, b, side, distance, symbol):
        if not np.isfinite(g.o.ravel()[a]):
            exclusions.append({'case': key, 'date': str(day.date()), 'reason': 'missing_entry_open'})
            return
        cases[key].append({'day': int(d), 'date': day, 'entry_i': int(a), 'scheduled_exit_i': int(b),
                           'side': int(side), 'stop_distance': distance, 'symbol': symbol})

    for d in tr:
        day = ts[d]
        if not start <= str(day.date()) <= end:
            continue
        if not np.isfinite(atr[d]) or atr[d] <= 0:
            exclusions.append({'case': 'NQ/all', 'date': str(day.date()), 'reason': 'missing_past_ATR'})
            continue
        is_exp = d in expiry
        friday = day.dayofweek == 4
        if is_exp or friday:
            records.append({'family': 'EOS', 'date': str(day.date()), 'expiry': is_exp, 'atr': atr[d]})
            for variant in ['original', 'no_expiry_gate', 'opposite_direction', 'no_stop', 'exit_0900']:
                if not (is_exp or variant == 'no_expiry_gate'):
                    continue
                side = 1 if variant == 'opposite_direction' else -1
                stop = None if variant == 'no_stop' else .30 * atr[d]
                exit_j = 540 if variant == 'exit_0900' else 600
                admit('EOS/' + variant, nq, d, day, d * 1440 + 511, d * 1440 + exit_j, side, stop, 'NQ')
        early_friday, spike = friday and day.day <= 10, d in releases
        if not (early_friday or spike):
            continue
        reference, react = nq.c[d, 450], nq.c[d, 465]
        if not np.isfinite(reference) or not np.isfinite(react) or reference == react or str(day.date()) in GOOD_FRIDAYS:
            exclusions.append({'case': 'NFP/all', 'date': str(day.date()), 'reason': 'missing_or_zero_reaction_or_GoodFriday'})
            continue
        side = -int(np.sign(react - reference))
        records.append({'family': 'NFP', 'date': str(day.date()), 'early_friday': early_friday,
                        'spike': spike, 'reaction': react - reference, 'atr': atr[d]})
        for variant in ['original', 'no_spike_gate', 'no_payroll_calendar', 'opposite_direction', 'no_stop']:
            selected = (early_friday and spike) or (variant == 'no_spike_gate' and early_friday) or (variant == 'no_payroll_calendar' and spike)
            if selected:
                stop = None if variant == 'no_stop' else .5 * atr[d]
                admit('NFP/' + variant, nq, d, day, d * 1440 + 466, d * 1440 + 540,
                      -side if variant == 'opposite_direction' else side, stop, 'NQ')

    sym = S['Sym']('CL', g=cl)
    sym.set_rolls([])  # Source MC-confirmed spec has no roll skip, not certified native contracts.
    frame = S['sunday_frame'](sym)
    frame['ok'] &= frame.o_i <= frame.sun * 1440 + jof(1705)
    for row in frame.itertuples():
        day = pd.Timestamp(row.Index)
        if not start <= str(day.date()) <= end:
            continue
        if not row.ok or not np.isfinite(row.atr) or row.atr <= 0:
            exclusions.append({'case': 'CL/all', 'date': str(day.date()), 'reason': 'invalid_or_late_opening_gap_or_ATR'})
            continue
        records.append({'family': 'CL', 'date': str(day.date()), 'atr': row.atr, 'gap_ATR': row.gA,
                        'opening_i': int(row.o_i), 'reference_i': int(row.ref_i)})
        for variant in ['original', 'no_upgap_gate', 'opposite_direction', 'no_stop', 'exit_0300']:
            if not (row.gA >= .1 or variant == 'no_upgap_gate'):
                continue
            side = 1 if variant == 'opposite_direction' else -1
            stop = None if variant == 'no_stop' else .75 * row.atr
            exit_j = 180 if variant == 'exit_0300' else 540
            admit('CL/' + variant, cl, row.mon, day, int(row.sun) * 1440 + 1026,
                  int(row.mon) * 1440 + exit_j, side, stop, 'CL')
    return cases, records, exclusions, frame


def replay(g, job, walker):
    symbol, side, a, b = job['symbol'], job['side'], job['entry_i'], job['scheduled_exit_i']
    pv, tick = (20., .25) if symbol == 'NQ' else (1000., .01)
    raw_entry = g.o.ravel()[a]
    anchor = raw_entry + side * tick if symbol == 'CL' else raw_entry
    stop = anchor - side * job['stop_distance'] if job['stop_distance'] is not None else (-np.inf if side > 0 else np.inf)
    arrays = [getattr(g, c).ravel() for c in 'ohlc']
    x, price, kind, worst = walker(*arrays, a, b, side, stop, np.inf if side > 0 else -np.inf, 1.)
    check(np.isfinite(price) and np.isfinite(raw_entry), 'Unknown actual execution price')
    gross, slips = (price - raw_entry) * side * pv, 2 * tick * pv
    missing = int((~np.isfinite(np.column_stack([v[a:x + 1] for v in arrays]))).any(axis=1).sum())
    return {**job, 'entry': raw_entry, 'exit': price, 'exit_i': int(x), 'kind': 'stop' if kind == 0 else 'time',
            'gross': gross, 'commission': 7.25, 'slippage': slips, 'net': gross - 7.25 - slips,
            'micro_net': gross / 10 - 1.25 - slips / 10,
            'extra_tick_cost_net': gross - 7.25 - 2 * slips,
            'source_adverse_mark': min((worst - raw_entry) * side * pv - 7.25 - slips, gross - 7.25 - slips),
            'missing_held_bars': missing, 'scheduled_exit_missing': bool(not np.isfinite(g.c.ravel()[b])),
            'last_close_fallback': bool(kind != 0 and x != b)}


def metrics(t, calendar):
    d = B.daily(t, calendar)
    z = M.perf(d, t.net, capital=50000.)
    eq = 50000 + d.cumsum().to_numpy()
    peak = np.maximum.accumulate(np.maximum(eq, 50000.))
    z['max_dd'] = R.max_dd(d)
    z['calmar'] = z['annual'] / z['max_dd'] if z['max_dd'] else np.nan
    z['ulcer'] = float(np.sqrt(np.mean(((eq - peak) / peak * 100) ** 2)))
    z.update(net_total=t.net.sum(), gross_total=t.gross.sum(), commission_total=t.commission.sum(),
             slippage_total=t.slippage.sum(), t_trade=B.tst(t.net), worst_trade=t.net.min(),
             micro_net_total=t.micro_net.sum(), micro_worst_trade=t.micro_net.min(),
             worst_source_adverse_mark=t.source_adverse_mark.min(),
             missing_held_bars=t.missing_held_bars.sum(), last_close_fallbacks=t.last_close_fallback.sum(),
             extra_tick_cost_total=t.extra_tick_cost_net.sum())
    return z


def fixtures(tools):
    walk = tools[2]['_walk']
    o, h, l, c = [np.array(a, float) for a in ([100, 97, 99], [101, 99, 101], [99, 96, 98], [100, 98, 100])]
    x, p, k, _ = walk(o, h, l, c, 0, 2, 1, 98, np.inf, 1.)
    check((x, p, k) == (1, 97, 0), 'Long gap stop fixture')
    x, p, k, _ = walk(200-o, 200-l, 200-h, 200-c, 0, 2, -1, 102, -np.inf, 1.)
    check((x, p, k) == (1, 103, 0), 'Short gap stop fixture')
    x, p, k, _ = walk(o, h, l, c, 0, 2, 1, -np.inf, np.inf, 1.)
    check((x, p, k) == (2, 100, 2), 'No stop fixture')
    missing = c.copy(); missing[-1] = np.nan
    check(walk(o, h, l, missing, 0, 2, 1, -np.inf, np.inf, 1.)[:2] == (1, 98), 'Explicit missing-exit fallback fixture')
    for pv, tick, normal, micro in [(20, .25, 17.25, 2.25), (1000, .01, 27.25, 3.25)]:
        check(abs(7.25 + 2 * tick * pv - normal) < 1e-8, 'Standard costs')
        check(abs(1.25 + 2 * tick * pv / 10 - micro) < 1e-8, 'Native sensitivity costs')
    return {'groups_passed': 5, 'market_returns_computed': False}


def phase(name):
    dependencies = ['analysis/metrics.py', 'analysis/resampling.py', 'analysis/codex_ingredients_three_20261108.py']
    committed_paths = [PLAN, CODE, 'agents/codex/evidence/ingredients_events_20261108.md'] + dependencies
    committed_paths += [p.relative_to(ROOT).as_posix() for p in INPUT.iterdir()]
    for path in committed_paths:
        check(subprocess.check_output(['git', 'show', 'HEAD:' + path], cwd=ROOT) == (ROOT / path).read_bytes(),
              'Commit exact plan/evidence/code before returns')
    source_manifest = json.loads((INPUT / 'sources.json').read_text())
    for entry in source_manifest['files']:
        check(sha(INPUT / Path(entry['path']).name) == entry['sha256'], 'Pinned source changed')
    if name == 'recent':
        design = json.loads((OUT / 'design/summary.json').read_text())
        check(design['implementation_gates_passed'] and design['script_sha256'] == sha(ROOT / CODE), 'Design gate/code changed')
    start, end = ('2018-01-01', '2022-12-30') if name == 'design' else ('2023-01-01', '2026-10-09')
    tools = setup()
    fixture_receipt = fixtures(tools)
    nq, cl, inputs = grids(tools[0], end)
    case_jobs, features, exclusions, frame = jobs(nq, cl, tools, start, end)
    dest = OUT / name
    dest.mkdir(parents=True, exist_ok=False)
    pd.DataFrame(features).to_csv(dest / 'features.csv', index=False)
    B.dump(dest / 'pre_return_admission.json', {'start': start, 'end': end,
            'source_policy_not_native_fill_certification': True, 'eligible_counts': {k: len(v) for k, v in case_jobs.items()},
            'excluded_before_pricing': exclusions, 'raw_inputs': inputs, 'fixtures': fixture_receipt,
            'dependency_sha256': {p: sha(ROOT / p) for p in dependencies}})
    results, calendars, all_metrics = {}, {}, []
    for key, jobs_ in case_jobs.items():
        family, variant = key.split('/')
        g = cl if family == 'CL' else nq
        calendar = pd.DatetimeIndex(g.ts[g.trading])
        calendar = calendar[(calendar >= start) & (calendar <= end)]
        calendars[family] = calendar
        t = pd.DataFrame([replay(g, job, tools[2]['_walk']) for job in jobs_])
        check(len(t) > 0, 'Empty diagnostic case: ' + key)
        check(np.isfinite(t[['entry', 'exit', 'gross', 'net']]).all().all(), 'Nonfinite actual trade')
        check(np.allclose(t.net, t.gross - t.commission - t.slippage), 'Cost identity')
        if variant == 'no_stop':
            check(not t.kind.eq('stop').any(), 'No-stop intervention stopped')
        results[key] = t
        stem = key.replace('/', '__')
        t.to_csv(dest / (stem + '_trades.csv'), index=False)
        B.daily(t, calendar).to_csv(dest / (stem + '_daily.csv'), header=['net'])
        for side in ['all', 'long', 'short']:
            sub = t if side == 'all' else t[t.side == (1 if side == 'long' else -1)]
            all_metrics.append({'family': family, 'variant': variant, 'side': side, 'period': name, **metrics(sub, calendar)})
        for year, dates in pd.Series(calendar, index=calendar).groupby(calendar.year):
            all_metrics.append({'family': family, 'variant': variant, 'side': 'all', 'period': str(year),
                                **metrics(t[t.date.dt.year == year], pd.DatetimeIndex(dates.values))})

    # Original-source replay parity, not an independent MC or economic verification.
    original = results['NFP/original']
    oracle = tools[3]['reaction_trades'](nq, original.day.to_numpy(), 730, 745, 900, 'fade', stop_k=.5, atr=nq.daily_atr(15))
    j = original[['date', 'side', 'net']].merge(oracle[['date', 'side', 'net']], on=['date', 'side'], suffixes=('_new', '_source'))
    check(len(j) == len(original) == len(oracle) and np.allclose(j.net_new, j.net_source), 'NFP source-price parity')
    original_cl = results['CL/original']
    oracle_cl = tools[7]['python_trades'](cl, frame[frame.index.isin(original_cl.date)], 900, 1026, False)
    jcl = original_cl[['date', 'entry', 'net']].merge(oracle_cl.reset_index(), on='date')
    check(len(jcl) == len(original_cl) == len(oracle_cl) and np.allclose(jcl.net, jcl.py_net)
          and np.allclose(jcl.entry, jcl.py_entry), 'CL source-price parity')
    original_eos = results['EOS/original']
    sig = pd.DataFrame({'day': original_eos.day, 'dj': 510, 'side': -1,
                        'stop': .3 * nq.daily_atr(15)[original_eos.day.to_numpy()], 'target': np.inf, 'exit_j': 600})
    oracle_eos = tools[2]['execute'](nq, sig, max_trades=1)
    je = original_eos[['date', 'net']].merge(oracle_eos[['date', 'net']], on='date', suffixes=('_new', '_source'))
    check(len(je) == len(original_eos) == len(oracle_eos) and np.allclose(je.net_new, je.net_source - 10), 'EOS source-price parity')

    effects, controls = [], {}
    for key, t in results.items():
        family, variant = key.split('/')
        if variant == 'original':
            R.bootstrap(B.daily(t, calendars[family]), n=1000, block=20, seed=SEED, chunk=250).loc[['annual', 'sharpe']].to_csv(dest / (family + '_original_bootstrap.csv'))
            continue
        base = results[family + '/original']
        delta = B.daily(base, calendars[family]) - B.daily(t, calendars[family])
        bounds = R.bootstrap(delta, n=1000, block=20, seed=SEED, chunk=250).loc['annual']
        effects.append({'family': family, 'intervention': variant, 'base_minus_intervention_net': delta.sum(),
                        'annual_effect_p5': bounds.p5, 'annual_effect_p50': bounds.p50, 'annual_effect_p95': bounds.p95})
    for key in ['EOS/no_expiry_gate', 'NFP/no_spike_gate', 'NFP/no_payroll_calendar', 'CL/no_upgap_gate']:
        family = key.split('/')[0]
        controls[key] = B.filter_control(results[family + '/original'], results[key], calendars[family])
    pd.DataFrame(all_metrics).to_csv(dest / 'metrics.csv', index=False)
    pd.DataFrame(effects).to_csv(dest / 'paired_effects.csv', index=False)
    summary = {'phase': name, 'start': start, 'end': end, 'implementation_gates_passed': True,
               'rule_cases': len(results), 'source_data_ref': REF, 'source_inputs': inputs,
               'script_sha256': sha(ROOT / CODE), 'plan_sha256': sha(ROOT / PLAN),
               'plan_commit': subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', PLAN], cwd=ROOT, text=True).strip(),
               'source_parity': {'EOS': len(je), 'NFP': len(j), 'CL': len(jcl)},
               'pure_filter_controls': controls, 'fixtures': fixture_receipt,
               'resampling_draws': 1000, 'seed': SEED, 'excluded_before_pricing': exclusions,
               'dependency_sha256': {p: sha(ROOT / p) for p in dependencies},
               'portfolio_tests_run': False, 'selected_changed_or_combined_strategy': False,
               'source_policy_missing_path_caveat': {k: {'missing_held_bars': int(t.missing_held_bars.sum()), 'last_close_fallbacks': int(t.last_close_fallback.sum())} for k, t in results.items()}}
    B.dump(dest / 'summary.json', summary)
    print(pd.DataFrame(all_metrics).query("side=='all' and period==@name")
          [['family', 'variant', 'trades', 'net_total', 't_trade', 'profit_factor', 'max_dd']].to_string(index=False), flush=True)
    print(json.dumps({'phase': name, 'implementation_gates_passed': True, 'source_parity': summary['source_parity']}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['fixtures', 'design', 'recent'])
    argument = parser.parse_args()
    if argument.mode == 'fixtures':
        print(fixtures(setup()))
    else:
        phase(argument.mode)
