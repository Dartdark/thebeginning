"""One frozen, user-requested candle/EMA MNQ adaptation; not KSE replication.

Inventory and synthetic modes do not compute historical strategy returns.
Design/recent require the exact plan and implementation committed first.
Shared grid.execute handles protective stops; the adapter implements causal
indicator exits at the next minute open, rather than the decision-bar close.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse
import hashlib
import json
import platform
import subprocess
import warnings

import numpy as np
import pandas as pd
import scipy
from grid import Grid, execute, j_of
import metrics as M
import resampling as R
from codex_s03_calendar import calendar_status

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_sentinel_mnq_20261108'
PLAN = 'agents/codex/plans/sentinel_mnq_20261108.md'
EVIDENCE = 'agents/codex/evidence/sentinel_mnq_20261108.md'
SCRIPT = Path(__file__).relative_to(ROOT).as_posix()
FEE, SLIP, STRESS_FEE, STRESS_SLIP = 1.24, .50, 2.48, 1.00
FIRST, LAST, FLAT = j_of(1015), j_of(1400), j_of(1455)
SEED = 7102818


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def dump(p, obj):
    def conv(v):
        if isinstance(v, (np.integer, np.floating, np.bool_)):
            return v.item()
        if isinstance(v, Path):
            return str(v)
        raise TypeError(type(v).__name__)
    Path(p).write_text(json.dumps(obj, indent=2, default=conv) + '\n')


def years(period):
    return range(2018, 2023) if period == 'design' else range(2023, 2027)


def files(period):
    return [ROOT / f'data/NQ_1min_{y}.csv' for y in years(period)]


def inventory(period):
    OUT.mkdir(parents=True, exist_ok=True)
    paths = files(period)
    raw = pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
    cols = ['open', 'high', 'low', 'close']
    conflicts = raw.groupby(['date', 'time'])[cols].nunique().max(axis=1).gt(1)
    if conflicts.any():
        raise RuntimeError('Conflicting duplicate prices: resolve before testing')
    raw = raw.drop_duplicates(['date', 'time']).copy()
    raw['j'] = j_of(raw.time)
    raw['valid'] = (raw[cols].notna().all(axis=1) & (raw.low > 0)
                    & (raw.low <= raw[cols].min(axis=1))
                    & (raw.high >= raw[cols].max(axis=1)))
    grouped = {d: r for d, r in raw.groupby('date')}
    first = f'{min(years(period))}-01-01'
    last = '2022-12-31' if period == 'design' else str(pd.to_datetime(raw.date.max(), format='%Y%m%d').date())
    records = []
    required = set(range(j_of(831), FLAT + 1))
    for d in pd.bdate_range(first, last):
        cal = calendar_status(d)
        if cal['kind'] == 'holiday':
            continue
        x = grouped.get(int(d.strftime('%Y%m%d')), pd.DataFrame(columns=['j', 'valid']))
        have = set(x.loc[x.valid.astype(bool), 'j'])
        complete = required.issubset(have)
        records.append(dict(date=str(d.date()), calendar=cal['kind'],
                            expected_minutes=len(required), valid_minutes=len(required & have),
                            eligible=cal['kind'] == 'normal' and complete,
                            reason='known early close' if cal['kind'] != 'normal' else
                            ('complete' if complete else 'missing/invalid minute path')))
    cov = pd.DataFrame(records)
    cov.to_csv(OUT / f'{period}_coverage.csv', index=False)
    normal = cov.calendar.eq('normal')
    result = dict(period=period, returns_computed=False, scheduled_sessions=len(cov),
                  normal_sessions=int(normal.sum()), eligible=int(cov.eligible.sum()),
                  path_coverage=float(cov.loc[normal, 'eligible'].mean()),
                  early_closes_skipped=int((~normal).sum()),
                  unresolved_normal_sessions=int((normal & ~cov.eligible).sum()),
                  inputs=[dict(path=str(p.relative_to(ROOT)), sha256=sha(p)) for p in paths],
                  coverage_sha256=sha(OUT / f'{period}_coverage.csv'),
                  sd_assumption_mnq=100.,
                  illustrative_net_daily_mean_for_t2=200 / np.sqrt(cov.eligible.sum()),
                  power_limit='Assumed $100 daily SD, one opportunity/day at most; dependence and multiplicity raise hurdle')
    dump(OUT / f'{period}_inventory.json', result)
    print(json.dumps(result, indent=2))


def committed():
    for p in [PLAN, EVIDENCE, SCRIPT]:
        subprocess.run(['git', 'cat-file', '-e', 'HEAD:' + p], cwd=ROOT, check=True)
        subprocess.run(['git', 'diff', '--exit-code', 'HEAD', '--', p], cwd=ROOT, check=True)
    return subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', PLAN], cwd=ROOT, text=True).strip()


def seeded_ema(x, n):
    """Session-local SMA seed, followed by standard recursive EMA."""
    x = np.asarray(x, float)
    out = np.full_like(x, np.nan)
    if len(x) >= n:
        out[n - 1] = np.mean(x[:n])
        for i in range(n, len(x)):
            out[i] = out[i - 1] + 2 / (n + 1) * (x[i] - out[i - 1])
    return out


def features(g, day):
    # Only complete cash-session bars; no 08:00 premarket or prior-day seed.
    js = np.arange(j_of(835), FLAT + 1, 5)
    op = np.array([g.o[day, j - 4] for j in js])
    hi = np.array([np.max(g.h[day, j - 4:j + 1]) for j in js])
    lo = np.array([np.min(g.l[day, j - 4:j + 1]) for j in js])
    cl = g.c[day, js]
    prior = np.r_[cl[0], cl[:-1]]
    tr = np.maximum(hi - lo, np.maximum(np.abs(hi - prior), np.abs(lo - prior)))
    return dict(j=js, o=op, c=cl, fast=seeded_ema(cl, 9), slow=seeded_ema(cl, 21),
                atr=pd.Series(tr).rolling(14).mean().to_numpy())


def master(f, k, side):
    return (np.isfinite(f['slow'][k - 1]) and
            side * (f['c'][k] - f['slow'][k]) > 0 and
            side * (f['slow'][k] - f['slow'][k - 1]) > 0)


def entry_side(f, k, baseline=False):
    for side in [1, -1]:
        if not master(f, k, side):
            continue
        if baseline or all(side * (f['c'][q] - f['o'][q]) > 0 and
                           side * (f['c'][q] - f['fast'][q]) > 0 for q in [k - 1, k]):
            return side
    return 0


def exit_decision(f, k, side):
    for q in range(k + 1, len(f['j'])):
        j = f['j'][q]
        if j >= FLAT:
            break
        against = side * (f['c'][q] - f['fast'][q]) < 0
        prior_against = side * (f['c'][q - 1] - f['fast'][q - 1]) < 0
        if against and (not master(f, q, side) or prior_against):
            return int(j), True
    return FLAT, False


def signals(g, days, baseline=False, placebo=None, seed=SEED):
    rng = np.random.default_rng(seed)
    out = []
    for day in days:
        f = features(g, day)
        chosen = None
        for k, j in enumerate(f['j']):
            if not FIRST <= j <= LAST:
                continue
            side = entry_side(f, k, baseline)
            if side:
                chosen = (k, side)
                break
        if chosen is None:
            continue
        k, side = chosen
        original_j = int(f['j'][k])
        if placebo == 'side':
            side = int(rng.choice([-1, 1]))
        elif placebo == 'time':
            # Conditional null: original day/side, random registered time.
            k = int(rng.choice(np.flatnonzero((f['j'] >= FIRST) & (f['j'] <= LAST))))
        exit_j, dynamic = exit_decision(f, k, side)
        out.append(dict(day=day, dj=int(f['j'][k]), side=side,
                        stop=float(np.ceil(2 * f['atr'][k] * 4) / 4), target=np.inf,
                        exit_j=exit_j, dynamic=dynamic, original_dj=original_j))
    return pd.DataFrame(out, columns=['day', 'dj', 'side', 'stop', 'target', 'exit_j', 'dynamic', 'original_dj'])


def replay(g, sig):
    t = execute(g, sig, max_trades=1, name='Sentinel_MNQ_custom')
    spec = sig.set_index('day')
    for i, r in t.iterrows():
        s = spec.loc[r.day]
        reason = 'stop' if r.kind == 0 else 'scheduled_flat'
        if r.kind == 0 and r.j1 > r.j0:
            stop_px = r.entry - r.side * s.stop
            if r.side * (g.o[int(r.day), int(r.j1)] - stop_px) <= 0:
                reason = 'stop_gap'
        if r.kind == 2 and bool(s.dynamic):
            # Stops through the decision close have already been walked. At the
            # next open both a market exit and a gap-through stop fill at the open.
            nxt = int(s.exit_j) + 1
            px = g.o[int(r.day), nxt]
            stop_px = r.entry - r.side * s.stop
            gap_stop = r.side * (px - stop_px) <= 0
            t.loc[i, ['j1', 'exit', 'kind']] = [nxt, px, 0 if gap_stop else 2]
            t.loc[i, 'pnl'] = (px - r.entry) * r.side * 20
            t.loc[i, 'mae'] = max(r.mae, max(0., (r.entry - px) * r.side * 20))
            reason = 'stop_gap_at_exit_open' if gap_stop else 'indicator_next_open'
        t.loc[i, 'reason'] = reason
        t.loc[i, 'decision_j'] = int(s.dj)
        t.loc[i, 'exit_decision_j'] = int(s.exit_j)
        t.loc[i, 'stop_points'] = s.stop
    t['gross_mnq'] = t.pnl / 10
    t['commission_mnq'] = FEE
    t['slippage_mnq'] = 2 * SLIP
    t['net_mnq'] = t.gross_mnq - t.commission_mnq - t.slippage_mnq
    t['stress_mnq'] = t.gross_mnq - STRESS_FEE - 2 * STRESS_SLIP
    t['net_nq'] = t.pnl - 7.25 - 10.
    # Replace shared pre-slippage net after the market-exit adapter.
    t['net'] = t.pnl - 7.25
    for col, jscol in [('entry_bar_close', 'j0'), ('exit_bar_close', 'j1')]:
        t[col] = pd.to_datetime(t.date) + pd.to_timedelta(480 + t[jscol].astype(int), unit='min')
    t['entry_at'] = t.entry_bar_close - pd.Timedelta(minutes=1)
    t['exit_interval_start'] = t.exit_bar_close - pd.Timedelta(minutes=1)
    t['exit_interval_end'] = t.exit_bar_close
    t['exit_at'] = t.exit_bar_close.where(t.reason.eq('scheduled_flat'), t.exit_interval_start)
    # OHLC locates an intraminute stop only within an interval. Do not label
    # that interval's opening boundary as a known execution timestamp.
    t.loc[t.reason.eq('stop'), 'exit_at'] = pd.NaT
    return t


def daily(t, dates, col='net_mnq'):
    return t.groupby('date')[col].sum().reindex(dates, fill_value=0.)


def tstat(x):
    return float(x.mean() / x.std() * np.sqrt(len(x))) if len(x) > 1 and x.std() > 0 else None


def measure(t, dates, col='net_mnq'):
    d = daily(t, dates, col)
    r = M.perf(d, t[col])
    r.update(total=float(d.sum()), trade_t=tstat(t[col]), daily_t=tstat(d), days=len(d),
             max_dd=R.max_dd(d), gross=float(t.gross_mnq.sum()),
             commission=float((STRESS_FEE if col == 'stress_mnq' else FEE) * len(t)),
             slippage=float((2 * STRESS_SLIP if col == 'stress_mnq' else 2 * SLIP) * len(t)))
    return r


def run(period):
    prereg = committed()
    if period == 'recent' and not json.loads((OUT / 'design_result.json').read_text())['passed']:
        raise RuntimeError('Failed design gate: historical validation prohibited')
    inv = json.loads((OUT / f'{period}_inventory.json').read_text())
    assert inv['path_coverage'] >= .95
    assert sha(OUT / f'{period}_coverage.csv') == inv['coverage_sha256']
    for p in inv['inputs']:
        assert sha(ROOT / p['path']) == p['sha256']
    # Isolated symlinks ensure no accidental later-price access in design.
    work = ROOT / f'scratch_data/codex_sentinel_mnq_{period}'
    work.mkdir(parents=True, exist_ok=True)
    for p in files(period):
        (work / p.name).symlink_to(p) if not (work / p.name).exists() else None
    assert {p.name for p in work.glob('*.csv')} == {p.name for p in files(period)}
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        g = Grid(str(work / '*.csv'))
    assert set(pd.DatetimeIndex(g.ts).year).issubset(set(years(period)))
    cov = pd.read_csv(OUT / f'{period}_coverage.csv', parse_dates=['date'])
    dates = pd.DatetimeIndex(cov.loc[cov.eligible, 'date'])
    daymap = {pd.Timestamp(d): i for i, d in enumerate(g.ts)}
    days = [daymap[d] for d in dates]
    sig, base_sig = signals(g, days), signals(g, days, baseline=True)
    t, base = replay(g, sig), replay(g, base_sig)
    sig.to_csv(OUT / f'{period}_signals.csv', index=False)
    t.to_csv(OUT / f'{period}_trades.csv', index=False)
    base.to_csv(OUT / f'{period}_baseline_trades.csv', index=False)
    d = pd.DataFrame({c: daily(t, dates, c) for c in ['gross_mnq', 'commission_mnq', 'slippage_mnq', 'net_mnq', 'stress_mnq', 'net_nq']})
    d['baseline_mnq'] = daily(base, dates)
    d.to_csv(OUT / f'{period}_daily.csv', index_label='date')
    assert np.isclose(d.net_mnq.sum(), t.net_mnq.sum())
    assert np.allclose(d.net_mnq, d.gross_mnq - d.commission_mnq - d.slippage_mnq)
    rows = []
    for label, tr in [('whole', t), ('long', t[t.side > 0]), ('short', t[t.side < 0]), ('baseline', base)]:
        for y in ['all'] + list(years(period)):
            tt = tr if y == 'all' else tr[tr.date.dt.year == y]
            dd = dates if y == 'all' else dates[dates.year == y]
            if len(dd):
                rows.append(dict(side=label, year=y, **measure(tt, dd)))
    pd.DataFrame(rows).to_csv(OUT / f'{period}_metrics.csv', index=False)
    primary, stress, baseline = measure(t, dates), measure(t, dates, 'stress_mnq'), measure(base, dates)
    ys = d.net_mnq.groupby(d.index.year).sum()
    gates = dict(at_least300_trades=len(t) >= 300, positive_native_net=primary['total'] > 0,
                 daily_t_at_least2=primary['daily_t'] is not None and primary['daily_t'] >= 2,
                 profit_factor_at_least1_1=primary['profit_factor'] >= 1.1,
                 four_of_five_years_positive=int((ys > 0).sum()) >= (4 if period == 'design' else 3),
                 stress_positive=stress['total'] > 0,
                 beats_price_only_baseline=primary['total'] > baseline['total'])
    cheap_pass = all(gates.values())
    placebo_p = {}
    if cheap_pass:
        null = []
        for family in ['side', 'time']:
            for i in range(1000):
                tt = replay(g, signals(g, days, placebo=family, seed=SEED + i))
                null.append(dict(family=family, draw=i, total=float(tt.net_mnq.sum())))
            print('completed', family, flush=True)
        nd = pd.DataFrame(null)
        nd.to_csv(OUT / f'{period}_placebos.csv', index=False)
        for f in ['side', 'time']:
            placebo_p[f] = float((1 + (nd.loc[nd.family == f, 'total'] >= primary['total']).sum()) / 1001)
            gates[f + '_placebo_p_le05'] = placebo_p[f] <= .05
    result = dict(period=period, primary=primary, stress=stress, baseline=baseline,
                  paired_daily_t_vs_baseline=tstat(d.net_mnq - d.baseline_mnq),
                  years=ys.to_dict(), gates=gates, cheap_pass=cheap_pass, passed=all(gates.values()),
                  placebos_run=cheap_pass, placebo_p=placebo_p,
                  strategy_definitions_run=2, selected_variant='single frozen custom version',
                  accounts_tested=False, independent_verification=False,
                  prereg_commit=prereg, script_sha256=sha(__file__), inventory=inv,
                  dependencies=dict(python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__, scipy=scipy.__version__),
                  assumption='NQ OHLC proxy, $2/point, $1.24 RT fee plus $0.50 per market/stop fill; pre-2019 MNQ synthetic',
                  stress_assumption='$2.48 RT fee plus $1 per market/stop fill; unchanged fixed one-trade sizing/state',
                  breakeven_extra_roundtrip_cost=float(t.net_mnq.mean()),
                  next_gate='historical validation then independent checker' if all(gates.values()) else 'STOP; no rescue search or dependent tests')
    dump(OUT / f'{period}_result.json', result)
    print(json.dumps(result, indent=2))


def synthetic():
    checks = []
    def check(name, ok):
        assert ok, name
        checks.append(name)
    x = np.arange(1., 31.)
    e = seeded_ema(x, 9)
    check('SMA seed and recursive EMA', np.isnan(e[:8]).all() and e[8] == 5 and np.isclose(e[9], 6))
    check('EMA prefix causality', np.allclose(e[:20], seeded_ema(x[:20], 9), equal_nan=True))
    f = dict(j=np.array([0, 5, 10, 15, FLAT]), o=np.array([100., 102., 102., 102., 102.]),
             c=np.array([101., 103., 101., 100., 100.]), fast=np.array([100., 101., 102., 102., 102.]),
             slow=np.array([98., 99., 100., 101., 102.]))
    check('two candles above fast EMA enter long', entry_side(f, 1) == 1)
    check('master intact waits for second adverse fast close', exit_decision(f, 1, 1) == (15, True))
    f['slow'][2] = 102.
    check('weakened master exits after first adverse fast close', exit_decision(f, 1, 1) == (10, True))
    a = np.full((1, 10), 100.)
    g = SimpleNamespace(o=a.copy(), h=a.copy() + .25, l=a.copy() - .25, c=a.copy(),
                        last_j=np.array([9]), ts=np.array(['2020-01-02'], dtype='datetime64[ns]'))
    sig = pd.DataFrame([dict(day=0, dj=1, side=1, stop=2., target=np.inf, exit_j=5, dynamic=True, original_dj=1)])
    g.o[0, 6] = 101.; g.h[0, 6] = 101.; g.c[0, 6] = 101.
    t = replay(g, sig).iloc[0]
    check('indicator exit uses next open not signal close', t.exit == 101 and t.j1 == 6)
    check('native cost bridge', np.isclose(t.net_mnq, 2 - 1.24 - 1) and np.isclose(t.stress_mnq, 2 - 2.48 - 2))
    check('decision-to-fill clock', t.entry_at == pd.Timestamp('2020-01-02 08:01') and t.exit_at == pd.Timestamp('2020-01-02 08:05'))
    g.l[0, 2] = 97.
    t = replay(g, sig).iloc[0]
    check('stop active on entry minute', t.exit == 98 and t.kind == 0 and t.j1 == 2)
    g.l[0, 2] = 99.75; g.o[0, 3] = 96.; g.l[0, 3] = 95.75; g.h[0, 3] = 96.25
    t = replay(g, sig).iloc[0]
    check('protective stop gap fills adverse open', t.exit == 96 and t.j1 == 3)
    g.o[0, 3] = 100.; g.l[0, 3] = 99.75; g.h[0, 3] = 100.25
    g.o[0, 6] = 96.; g.l[0, 6] = 95.75; g.h[0, 6] = 96.25
    t = replay(g, sig).iloc[0]
    check('gap at dynamic exit open', t.exit == 96 and t.reason == 'stop_gap_at_exit_open')
    sig['side'] = -1; g.o[0, 6] = 99.
    t = replay(g, sig).iloc[0]
    check('short P&L mirror', t.exit == 99 and np.isclose(t.gross_mnq, 2))
    sig['dynamic'] = False
    t = replay(g, sig).iloc[0]
    check('scheduled flatten uses registered close', t.exit == 100 and t.j1 == 5 and t.reason == 'scheduled_flat')
    OUT.mkdir(parents=True, exist_ok=True)
    dump(OUT / 'synthetic_checks.json', dict(passed=True, checks=checks, historical_returns_computed=False, script_sha256=sha(__file__)))
    print(f'{len(checks)} synthetic checks passed')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['inventory', 'synthetic', 'run'])
    ap.add_argument('--period', choices=['design', 'recent'], default='design')
    a = ap.parse_args()
    if a.mode == 'inventory':
        inventory(a.period)
    elif a.mode == 'synthetic':
        synthetic()
    else:
        run(a.period)
