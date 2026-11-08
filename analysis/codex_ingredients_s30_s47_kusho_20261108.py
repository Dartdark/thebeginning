"""Frozen S30/S47/Kusho component attribution; no accounts or live-system access."""
import argparse
import ast
import copy
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

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'agents/codex/inputs/ingredients_s30_s47_kusho_20261108'
OUT = ROOT / 'analysis/outputs/codex_ingredients_s30_s47_kusho_20261108'
PLAN = 'agents/codex/plans/ingredients_s30_s47_kusho_20261108.md'
CODE = 'analysis/codex_ingredients_s30_s47_kusho_20261108.py'
EVIDENCE = 'agents/codex/evidence/ingredients_s30_s47_kusho_20261108.md'
SEED = 80314
B.INPUT, B.SEED = INPUT, SEED
check, sha = E.check, E.sha
FAMILIES = {
    'S30_NQ': ['original', 'no_low_IBS_entry', 'fixed_5_session_exit', 'opposite_same_schedule', 'close_strength'],
    'S30_ES': ['original', 'no_low_IBS_entry', 'fixed_5_session_exit', 'opposite_same_schedule', 'close_strength'],
    'S47': ['original', 'no_NY_agreement', 'NY_only', 'opposite_direction', 'no_stop'],
    'KUSHO': ['original', 'no_wick', 'no_EMA', 'no_break_even', 'flat_1545'],
}
warnings.filterwarnings('ignore', category=RuntimeWarning)


def extracted(filename, names, namespace):
    tree = ast.parse((INPUT / filename).read_text())
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    check({n.name for n in nodes} == set(names), 'Missing source functions')
    exec(compile(ast.Module(body=nodes, type_ignores=[]), filename, 'exec'), namespace)
    return namespace


def function_text(filename, name):
    text = (INPUT / filename).read_text()
    node = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(text, node)


def replace_once(text, before, after):
    check(text.count(before) == 1, 'Source instrumentation hook differs: ' + before)
    return text.replace(before, after)


def namespaces():
    from datetime import datetime
    from zoneinfo import ZoneInfo
    base = {'np': np, 'pd': pd, 'jof': lambda t: np.asarray(t) // 100 * 60 + np.asarray(t) % 100}
    roll = extracted('overnight_round.py', ['roll_minutes'], {**base,
          'SWITCH': [(1700, 1705), (330, 335), (520, 530)],
          'WIN': {'NQ': ((3, 6, 9, 12), 3, 20), 'ES': ((3, 6, 9, 12), 3, 20)}})['roll_minutes']
    s0 = extracted('s30_ibs_test.py', ['sessions', 'run'], dict(base))
    s = dict(s0)
    text = function_text('s30_ibs_test.py', 'run')
    text = replace_once(text, 'mirror=False):', 'mirror=False, variant="original"):')
    text = replace_once(text, 'side = -1 if mirror else 1',
        'side = -1 if (mirror or variant == "opposite_same_schedule") else 1\n'
        '        if variant == "no_low_IBS_entry": enter = True\n'
        '        if variant == "close_strength": enter, leave = x.ibs > 0.8, x.ibs < 0.2\n'
        '        if variant == "fixed_5_session_exit": leave = pos != 0 and i - e_i >= 5')
    text = replace_once(text, 'e_px=e_px, x_px=px, comm=comm, jumps=jumps',
                         'e_px=e_px, x_px=px, comm=comm, jumps=jumps, kind="signal"')
    text = replace_once(text, 'return pd.DataFrame(out)',
        'if pos != 0:\n'
        '        valid = S.full & np.isfinite(S.ibs) & np.isfinite(S.nxt) & (S.hi > S.lo)\n'
        '        i = int(S.index[valid][-1]); x = S.loc[i]; px = x.nxt - pos * tick\n'
        '        m0, m1 = int(S.r[e_i]) * 1440 + 901, int(x.r) * 1440 + 901\n'
        '        jump = jump_points(g, rolls, m0, m1)\n'
        '        out.append(dict(date=S.date[e_i], exit_date=x.date, side=pos, net=((px-e_px)*pos-jump*pos)*pv-comm,\n'
        '                        days=(x.date-S.date[e_i]).days, i0=e_i, i1=i, e_px=e_px, x_px=px, comm=comm,\n'
        '                        jumps=[], kind="terminal"))\n'
        '    return pd.DataFrame(out)')
    s['jump_points'] = jump_points
    exec(compile(text, '<S30 frozen interventions and terminal accounting>', 'exec'), s)
    s47 = extracted('s47_test.py', ['eu_min', 'skip_day', 'build', 'last_close', 'run'],
                   {**base, 'PV': 20., 'TICK': .25, 'COST': 7.25, 'datetime': datetime, 'ZoneInfo': ZoneInfo})
    k0 = extracted('kusho_test.py', ['Data', 'run'], {**base, 'PV': 20., 'TICK': .25, 'COST': 7.25, 'roll_minutes': roll})
    k = dict(k0)
    text = function_text('kusho_test.py', 'run')
    text = replace_once(text, 'flat_rth=False):', 'flat_rth=False, be_on=True):')
    text = replace_once(text, 'if swing and not be_done:', 'if swing and not be_done and be_on:')
    text = replace_once(text, 'swing=swing, fm=fm, xm=xm, net=',
              'swing=swing, R_initial=Rr, be_done=be_done, entry_bar_end=int(D.e[kf]), fm=fm, xm=xm, net=')
    text = replace_once(text, 't = pd.DataFrame(out)',
         'if pos != 0:\n'
         '        xm = int(np.flatnonzero(np.isfinite(c))[ -1 ])\n'
         '        exit_px = c[xm] - pos * TICK\n'
         '        jump = jump_points(D.g, D.rolls, fm, xm)\n'
         '        out.append(dict(date=pd.Timestamp(D.g.ts[fm//1440]), exit_date=pd.Timestamp(D.g.ts[xm//1440]),\n'
         '                        side=pos, entry=ent, exit=exit_px, kind="terminal", swing=swing,\n'
         '                        R_initial=Rr, be_done=be_done, entry_bar_end=int(D.e[kf]), fm=fm, xm=xm,\n'
         '                        net=((exit_px-ent)-jump)*pos*PV-COST))\n'
         '    t = pd.DataFrame(out)')
    k['jump_points'] = jump_points
    exec(compile(text, '<Kusho explicit BE guard and terminal metadata>', 'exec'), k)
    return roll, s0, s, s47, k0, k


def jump_points(g, rolls, first, last):
    c = g.c.ravel()
    total = 0.
    for j in rolls[(rolls > first) & (rolls <= last)]:
        p = int(j) - 1
        while p >= 0 and not np.isfinite(c[p]):
            p -= 1
        check(p >= 0, 'Unknown pre-roll price')
        total += c[j] - c[p]
    return total


def cumulative_jumps(g, rolls):
    z = np.zeros(g.D * 1440)
    for j in rolls:
        z[int(j)] = jump_points(g, np.array([j]), int(j) - 1, int(j))
    return z.cumsum()


def book_date(day):
    day = pd.Timestamp(day).normalize()
    return day + pd.Timedelta(days=(7 - day.dayofweek) if day.dayofweek >= 5 else 0)


def canonical(raw, family, variant, g, sessions, rolls, cum, calendar):
    t = raw.copy().reset_index(drop=True)
    check(len(t) > 0, 'Empty case: ' + family + '/' + variant)
    sym = 'ES' if family == 'S30_ES' else 'NQ'
    pv, comm = (50., 5.) if sym == 'ES' else (20., 7.25)
    source_net = t.net.to_numpy().copy()
    if family.startswith('S30'):
        t['fm'] = sessions.r.to_numpy()[t.i0.astype(int)] * 1440 + 901
        t['xm'] = sessions.r.to_numpy()[t.i1.astype(int)] * 1440 + 901
        t['entry'], t['exit'] = t.e_px, t.x_px
        t['raw_entry'], t['raw_exit'] = t.entry - t.side * .25, t.exit + t.side * .25
        t['market_legs'] = 2
        t = t.drop(columns=['jumps'])
    elif family == 'S47':
        t['fm'], t['xm'] = t.day * 1440 + t.j0, t.day * 1440 + t.j1
        t['raw_entry'], t['raw_exit'] = t.entry, t.exit
        t['market_legs'] = 2
    else:
        t['raw_entry'] = t.entry
        t['raw_exit'] = t.exit + t.side * .25 * t.kind.ne('target')
        t['market_legs'] = t.kind.ne('target').astype(int)
    t['fm'], t['xm'] = t.fm.astype(int), t.xm.astype(int)
    check((t.xm >= t.fm).all(), 'Invalid chronology')
    t['entry_date'] = pd.to_datetime(g.ts[t.fm // 1440])
    t['exit_date_actual'] = pd.to_datetime(g.ts[t.xm // 1440])
    t['date'] = t.exit_date_actual.map(book_date)
    t['jump_points'] = cum[t.xm.to_numpy()] - cum[t.fm.to_numpy()]
    t['gross'] = (t.raw_exit - t.raw_entry - t.jump_points) * t.side * pv
    t['commission'], t['slippage'] = comm, .25 * pv * t.market_legs
    t['net'] = t.gross - t.commission - t.slippage
    check(np.allclose(t.net, source_net, atol=1e-6), 'Source/net/roll/cost bridge differs')
    check(np.isfinite(t[['entry', 'exit', 'net', 'gross']]).all().all(), 'Nonfinite execution')
    t['micro_net'] = t.gross / 10 - 1.25 - t.slippage / 10
    t['extra_tick_cost_net'] = t.net - t.slippage
    t['family'], t['variant'], t['symbol'] = family, variant, sym
    t['terminal'] = t.kind.eq('terminal')
    t['Sunday_exit'] = t.exit_date_actual.dt.dayofweek.eq(6)
    t['target_bar_ambiguous'] = t.kind.eq('target')
    t['unprotected_entry_bar'] = family in ('S47', 'KUSHO')
    adverse, missing = [], []
    low, high = g.l.ravel(), g.h.ravel()
    for x in t.itertuples():
        end = x.xm if family.startswith('S30') or x.kind == 'stop' else x.xm + 1
        p = (low if x.side > 0 else high)[x.fm:end]
        adjusted = p - (cum[x.fm:end] - cum[x.fm])
        seen = adjusted[np.isfinite(adjusted)]
        seen = np.r_[x.raw_entry, seen, x.raw_exit - x.jump_points]
        worst = seen.min() if x.side > 0 else seen.max()
        adverse.append(min((worst - x.raw_entry) * x.side * pv - comm - x.slippage, x.net))
        missing.append(int((~np.isfinite(g.c.ravel()[x.fm:x.xm + 1])).sum()))
    t['source_adverse_mark'], t['missing_held_bars'] = adverse, missing
    daily, marking = mark_daily(t, g, cum, calendar, pv)
    t['last_close_fallback'] = False
    if family == 'S47':
        t['last_close_fallback'] = t.kind.eq('time') & ~np.isfinite(g.c[t.day.astype(int), 900])
    return t, daily, marking


def mark_daily(t, g, cum, calendar, pv):
    """Cash P&L from actual fills, past-only daily marks and explicit roll/fee allocation."""
    indices = pd.Index(pd.to_datetime(g.ts)).get_indexer(calendar)
    check((indices >= 0).all(), 'Accounting calendar outside grid')
    cuts = indices * 1440 + 1439
    observed = np.flatnonzero(np.isfinite(g.c.ravel()))
    last_pos = np.searchsorted(observed, cuts, side='right') - 1
    check((last_pos >= 0).all(), 'No historical mark before accounting cut')
    marks = observed[last_pos]
    d = pd.DataFrame(0., index=calendar, columns=['gross', 'commission', 'slippage', 'micro_commission'])
    marking = []
    for x in t.itertuples():
        first_book, last_book = book_date(g.ts[x.fm // 1440]), book_date(g.ts[x.xm // 1440])
        check(first_book in d.index and last_book in d.index, 'Trade escapes era calendar')
        # S47 charges both market ticks; S30 input prices contain both; Kusho entry is a limit.
        entry_slip = .25 * pv if x.family != 'KUSHO' else 0.
        exit_slip = x.slippage - entry_slip
        d.loc[first_book, ['commission', 'micro_commission', 'slippage']] += [x.commission / 2, .625, entry_slip]
        d.loc[last_book, ['commission', 'micro_commission', 'slippage']] += [x.commission / 2, .625, exit_slip]
        prev_px, prev_i = x.raw_entry, x.fm
        for k in np.flatnonzero((cuts >= x.fm) & (cuts < x.xm)):
            j = max(int(marks[k]), x.fm)
            px = x.raw_entry if j == x.fm and marks[k] < x.fm else g.c.ravel()[j]
            check(np.isfinite(px), 'Unknown active daily mark')
            d.iloc[k, 0] += (px - prev_px - (cum[j] - cum[prev_i])) * x.side * pv
            marking.append({'date': str(calendar[k].date()), 'entry_i': x.fm, 'mark_i': j,
                            'cut_i': int(cuts[k]), 'mark_age_minutes': int(cuts[k] - j)})
            prev_px, prev_i = px, j
        d.loc[last_book, 'gross'] += (x.raw_exit - prev_px - (cum[x.xm] - cum[prev_i])) * x.side * pv
    d['net'] = d.gross - d.commission - d.slippage
    d['micro_net'] = d.gross / 10 - d.micro_commission - d.slippage / 10
    d['extra_tick_cost_net'] = d.net - d.slippage
    for col in ['gross', 'commission', 'slippage', 'net', 'micro_net', 'extra_tick_cost_net']:
        check(abs(d[col].sum() - t[col].sum()) < .005, 'Daily/trade reconciliation: ' + col)
    return d, marking


def metrics(t, d):
    z = M.perf(d.net, t.net, capital=50000.)
    eq = 50000 + d.net.cumsum().to_numpy()
    peak = np.maximum.accumulate(np.maximum(eq, 50000.))
    z['max_dd'] = R.max_dd(d.net)
    z['calmar'] = z['annual'] / z['max_dd'] if z['max_dd'] else np.nan
    z['ulcer'] = float(np.sqrt(np.mean(((eq - peak) / peak * 100) ** 2)))
    z['ulcer_perf'] = z['annual'] / 50000 * 100 / z['ulcer'] if z['ulcer'] else np.nan
    z.update(net_total=d.net.sum(), trade_net_total=t.net.sum(), gross_total=d.gross.sum(),
             commission_total=d.commission.sum(), slippage_total=d.slippage.sum(), t_trade=B.tst(t.net),
             worst_trade=t.net.min(), micro_net_total=d.micro_net.sum(), micro_worst_trade=t.micro_net.min(),
             extra_tick_cost_total=d.extra_tick_cost_net.sum(), worst_source_adverse_mark=t.source_adverse_mark.min(),
             exit_booked_dd=R.max_dd(B.daily(t, d.index)), terminal_trades=int(t.terminal.sum()),
             missing_held_bars=int(t.missing_held_bars.sum()), last_close_fallbacks=int(t.last_close_fallback.sum()))
    return z


def fixtures():
    roll, s0, s, s47, k0, k = namespaces()
    class Tiny:
        def bars(self, n):
            raise RuntimeError('Not used')
    g = Tiny(); g.D = 10; g.ts = pd.date_range('2024-01-01', periods=10).to_numpy()
    for name in 'ohlc':
        setattr(g, name, np.full((10, 1440), 100.))
    S = pd.DataFrame({'r': range(8), 'date': pd.bdate_range('2024-01-01', periods=8),
                     'full': True, 'hi': 101., 'lo': 99., 'c15': 100., 'nxt': np.arange(8.) + 100.,
                     'ibs': [.1, .5, .9, .1, .9, .5, .5, .5]})
    a = s['run'](g, S, 20, .25, 7.25, np.array([], int))
    b = s0['run'](g, S, 20, .25, 7.25, np.array([], int))
    check(np.allclose(a.net, b.net), 'S30 unchanged source fixture')
    op = s['run'](g, S, 20, .25, 7.25, np.array([], int), variant='opposite_same_schedule')
    check(np.array_equal(a.i0, op.i0) and np.array_equal(a.i1, op.i1), 'Opposite changes schedule')
    check(np.allclose(a.net + op.net, -34.5), 'Opposite market fees')
    fixed = s['run'](g, S, 20, .25, 7.25, np.array([], int), variant='fixed_5_session_exit')
    check(fixed.i1.iloc[0] == 5, 'Five-session rule')
    strength = s['run'](g, S, 20, .25, 7.25, np.array([], int), variant='close_strength')
    check(strength.i0.iloc[0] == 2 and strength.i1.iloc[0] == 3, 'Strength timing')
    # A position from Friday through Sunday to Monday; one arbitrary roll jump must be removed once.
    g.D = 4; g.ts = pd.date_range('2024-01-05', periods=4).to_numpy()
    for name in 'ohlc':
        setattr(g, name, np.full((4, 1440), 100.))
    g.c[2:, :] = 110.; g.l[2:, :] = 109.; g.h[2:, :] = 111.; g.o[2:, :] = 110.
    rolls = np.array([2880]); cum = cumulative_jumps(g, rolls)
    raw = pd.DataFrame([{'fm': 901, 'xm': 4321, 'entry': 100., 'exit': 109.75,
                         'side': 1, 'kind': 'eod', 'net': -12.25}])
    cal = pd.to_datetime(['2024-01-05', '2024-01-08'])
    t, d, marks = canonical(raw, 'KUSHO', 'original', g, None, rolls, cum, cal)
    check(abs(t.net.sum() + 12.25) < 1e-8 and abs(d.net.sum() + 12.25) < 1e-8, 'Roll daily identity')
    check(abs(t.micro_net.iloc[0] + 1.75) < 1e-8, 'Native fee bridge')
    check(book_date('2024-01-07') == pd.Timestamp('2024-01-08'), 'Sunday booking')
    check(s47['eu_min'](pd.Timestamp('2024-03-18')) != s47['eu_min'](pd.Timestamp('2024-04-08')), 'London/US DST mismatch')
    # Exercise the actual guarded Kusho simulator: BE fires from the fill bar only when enabled.
    n = 70; end = np.arange(n) * 15 + 14; o = np.full(end[-1] + 1, 100.)
    lo, hi, close = o.copy(), o.copy(), o.copy()
    lo[end[61]-14:end[61]+1] = 99.5; hi[end[61]-14:end[61]+1] = 130.
    lo[end[62]-14:end[62]+1] = 100.; hi[end[62]-14:end[62]+1] = 102.
    dates = np.array([np.datetime64('2024-01-02')])
    D = SimpleNamespace(o=o, h=hi, l=lo, c=close, C=np.full(n, 101.), O=np.full(n, 100.),
        H=np.full(n, 130.), L=np.full(n, 99.), ema=np.full(n, 100.), atr=np.full(n, 10.),
        e=end, hhmm=np.full(n, 900), td=np.zeros(n, int), down=np.array([False]),
        early={}, rolls=np.array([], int), cum=np.zeros(n), g=SimpleNamespace(ts=dates, c=close.reshape(1,-1)))
    D.L[59], D.L[58], D.L[60] = 90., 95., 99.
    on, off = k['run'](D, mode='v9'), k['run'](D, mode='v9', be_on=False)
    check(on.be_done.any() and not off.be_done.any(), 'Explicit BE-off failed')
    check(on.kind.eq('stop').any() and off.kind.eq('terminal').any(), 'BE intervention not isolated')
    g.D = 21; g.ts = pd.date_range('2024-01-01', periods=21).to_numpy()
    for name in 'ohlc': setattr(g, name, np.full((21, 1440), 100.))
    T = pd.DataFrame({'r': range(21), 'date': pd.bdate_range('2024-01-01', periods=21),
                      'n': 800, 'first_ok': True, 'rng': 1., 'roll': False, 'hol': True})
    T.loc[20, 'hol'] = False
    eu = s47['eu_min'](T.date.iloc[-1])
    g.c[20, eu + 30], g.c[20, 570], g.l[20, 572] = 101., 101., 90.
    normal, no_stop = s47['run'](g, T), s47['run'](g, T, stop_atr=np.inf)
    check(normal.kind.eq('stop').all() and no_stop.kind.eq('time').all()
          and len(normal) == len(no_stop) == 1, 'Source S47 infinite-stop fixture')
    return {'groups_passed': 10, 'market_returns_computed': False}


def run(phase):
    dependencies = ['analysis/metrics.py', 'analysis/resampling.py',
                    'analysis/codex_ingredients_three_20261108.py', 'analysis/codex_ingredients_events_20261108.py']
    for path in [PLAN, CODE, EVIDENCE] + dependencies + [p.relative_to(ROOT).as_posix() for p in INPUT.iterdir()]:
        check(subprocess.check_output(['git', 'show', 'HEAD:' + path], cwd=ROOT) == (ROOT / path).read_bytes(),
              'Commit exact definitions before returns: ' + path)
    for item in json.loads((INPUT / 'sources.json').read_text())['files']:
        check(sha(INPUT / Path(item['path']).name) == item['sha256'], 'Pinned source hash differs')
    if phase == 'recent':
        receipt = json.loads((OUT / 'design/summary.json').read_text())
        check(receipt['implementation_gates_passed'] and receipt['script_sha256'] == sha(ROOT / CODE), 'Design gate/code changed')
    start, end = ('2018-01-01', '2022-12-30') if phase == 'design' else ('2023-01-01', '2026-10-09')
    fixture_receipt = fixtures()
    nq, es, inputs = B.grids(end)
    calendar = pd.bdate_range(start, end)
    roll, s0, s, s47, k0, k = namespaces()
    rolls = {'NQ': np.sort(roll(nq, 'NQ')), 'ES': np.sort(roll(es, 'ES'))}
    cum = {'NQ': cumulative_jumps(nq, rolls['NQ']), 'ES': cumulative_jumps(es, rolls['ES'])}
    S = {sym: s0['sessions'](g, sym) for sym, g in [('NQ', nq), ('ES', es)]}
    S = {sym: table[(table.date >= start) & (table.date <= end)].reset_index(drop=True) for sym, table in S.items()}
    T = s47['build'](nq)
    T.loc[(T.date < start) | (T.date > end), 'hol'] = True
    D = k0['Data'](nq, adjust=True)
    D.C = D.C.copy()
    D.C[pd.DatetimeIndex(nq.ts[D.e // 1440]) < start] = np.nan
    dest = OUT / phase; dest.mkdir(parents=True, exist_ok=False)
    for sym, table in S.items():
        table.to_csv(dest / ('S30_' + sym + '_features.csv'), index=False)
    T.to_csv(dest / 'S47_features.csv', index=False)
    good = np.isfinite(D.C) & (D.hhmm >= 900) & (D.hhmm <= 1345)
    pd.DataFrame({'bar_end_i': D.e[good], 'close': D.C[good], 'open': D.O[good], 'ema': D.ema[good],
                  'lower_wick': (D.O-D.L)[good], 'upper_wick': (D.H-D.O)[good],
                  'DOWN': D.down[np.minimum(D.td[good], len(D.down)-1)]}).to_csv(dest / 'KUSHO_features.csv', index=False)
    B.dump(dest / 'pre_return_admission.json', {'phase': phase, 'start': start, 'end': end,
          'fixture_receipt': fixture_receipt, 'raw_inputs': inputs,
          'source_ref': B.DATA_REF, 'source_roll_policy_is_retrospective': True,
          'rolls': {sym: [{'i': int(j), 'date': str(pd.Timestamp((es if sym=='ES' else nq).ts[j//1440]).date()),
                           'point_jump': float(cum[sym][j]-cum[sym][j-1])} for j in js] for sym, js in rolls.items()},
          'versions': {name: __import__(name).__version__ for name in ['numpy','pandas','numba','openpyxl','scipy','sklearn']}})
    results, dailies, statistics, parity, marking = {}, {}, [], {}, {}
    for family, names in FAMILIES.items():
        sym = 'ES' if family == 'S30_ES' else 'NQ'; g = es if sym == 'ES' else nq
        pv, commission = (50., 5.) if sym == 'ES' else (20., 7.25)
        for variant in names:
            if family.startswith('S30'):
                raw = s['run'](g, S[sym], pv, .25, commission, rolls[sym], variant=variant)
                if variant == 'original':
                    source = s0['run'](g, S[sym], pv, .25, commission, rolls[sym])
                    actual = raw[raw.kind.ne('terminal')]
                    check(len(source) == len(actual) and np.allclose(source.net, actual.net)
                          and np.array_equal(source.i0, actual.i0) and np.array_equal(source.i1, actual.i1), 'S30 source parity')
                    parity[family] = len(actual)
            elif family == 'S47':
                kw = {'no_NY_agreement': {'v2': False}, 'NY_only': {'ny_only': True},
                      'opposite_direction': {'side_override': lambda i, side: -side}, 'no_stop': {'stop_atr': np.inf}}.get(variant, {})
                raw = s47['run'](nq, T, **kw)
                if variant == 'original': parity[family] = {'trades': len(raw), 'check': 'unchanged source function'}
                if variant == 'no_stop': check(raw.kind.ne('stop').all(), 'Infinite stop unexpectedly executed')
            else:
                kw = {'no_wick': {'wick_on': False}, 'no_EMA': {'ema_on': False},
                      'no_break_even': {'be_on': False}, 'flat_1545': {'flat_rth': True}}.get(variant, {})
                raw = k['run'](D, mode='v9', **kw)
                if variant == 'no_break_even': check(not raw.be_done.any(), 'BE-off case still armed BE')
                if variant == 'original':
                    source = k0['run'](D, mode='v9'); actual = raw[raw.kind.ne('terminal')]
                    check(len(source) == len(actual) and np.allclose(source.net, actual.net)
                          and np.array_equal(source.fm, actual.fm) and np.array_equal(source.xm, actual.xm), 'Kusho source parity')
                    parity[family] = len(actual)
            t, d, marks = canonical(raw, family, variant, g, S.get(sym), rolls[sym], cum[sym], calendar)
            key, stem = family + '/' + variant, family + '__' + variant
            results[key], dailies[key], marking[key] = t, d, marks
            t.to_csv(dest / (stem + '_trades.csv'), index=False)
            d.to_csv(dest / (stem + '_daily.csv'), index_label='date')
            for side in ('all', 'long', 'short'):
                sub = t if side == 'all' else t[t.side.eq(1 if side == 'long' else -1)]
                sd, _ = mark_daily(sub, g, cum[sym], calendar, pv)
                statistics.append({'family': family, 'variant': variant, 'period': phase, 'side': side, **metrics(sub, sd)})
                sd.to_csv(dest / (stem + '_' + side + '_daily.csv'), index_label='date')
                for year in sorted(set(calendar.year)):
                    sy = sub[sub.date.dt.year.eq(year)]
                    statistics.append({'family': family, 'variant': variant, 'period': str(year), 'side': side,
                                       **metrics(sy, sd[sd.index.year == year])})
    effects = []
    for family, names in FAMILIES.items():
        base = dailies[family + '/original'].net
        R.bootstrap(base, n=1000, block=20, seed=SEED, chunk=250).loc[['annual','sharpe']].to_csv(dest / (family+'_original_bootstrap.csv'))
        for variant in names[1:]:
            delta = base - dailies[family + '/' + variant].net
            bounds = R.bootstrap(delta, n=1000, block=20, seed=SEED, chunk=250).loc['annual']
            effects.append({'family': family, 'intervention': variant, 'base_minus_intervention_net': delta.sum(),
                            'annual_effect_p5': bounds.p5, 'annual_effect_p50': bounds.p50, 'annual_effect_p95': bounds.p95})
    controls = {key: B.filter_control(results['S47/original'], results['S47/'+key], calendar)
                for key in ['no_NY_agreement', 'NY_only']}
    check(all(v['pure_nested_filter'] for v in controls.values()), 'S47 expected pure filter did not nest')
    pd.DataFrame(statistics).to_csv(dest / 'metrics.csv', index=False)
    pd.DataFrame(effects).to_csv(dest / 'paired_effects.csv', index=False)
    B.dump(dest / 'marking_receipts.json', marking)
    B.dump(dest / 'summary.json', {'phase': phase, 'start': start, 'end': end, 'rule_cases': 20,
          'implementation_gates_passed': True, 'script_sha256': sha(ROOT / CODE), 'plan_sha256': sha(ROOT / PLAN),
          'plan_commit': subprocess.check_output(['git','log','-1','--format=%H','--',PLAN],cwd=ROOT,text=True).strip(),
          'source_parity': parity, 'pure_filter_controls': controls, 'seed': SEED, 'resampling_draws': 1000,
          'dependency_sha256': {path: sha(ROOT/path) for path in dependencies},
          'terminal_counts': {key: int(t.terminal.sum()) for key,t in results.items()},
          'new_rule_selected': False, 'portfolio_tests_run': False})
    print(pd.DataFrame(statistics).query('period==@phase and side=="all"')
          [['family','variant','trades','net_total','max_dd','exit_booked_dd','terminal_trades']].round(2).to_string(index=False))
    print(json.dumps({'phase': phase, 'implementation_gates_passed': True, 'source_parity': parity}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['fixtures','design','recent'])
    args = parser.parse_args()
    if args.phase == 'fixtures': print(fixtures())
    else: run(args.phase)
