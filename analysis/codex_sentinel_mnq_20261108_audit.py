"""Maker audit from raw minutes and saved ledgers; no new economic definition.

Separate scalar execution replay and pandas EMA reconstruction. This is not a
blind independent checker, broker-fill validation, or new historical trial.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_sentinel_mnq_20261108'
REPORT = ROOT / 'agents/codex/results/sentinel_mnq_20261108.md'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def indicators(r):
    a = r[['open', 'high', 'low', 'close']].to_numpy().reshape(-1, 5, 4)
    b = pd.DataFrame(dict(o=a[:, 0, 0], h=a[:, :, 1].max(axis=1),
                          l=a[:, :, 2].min(axis=1), c=a[:, -1, 3]))
    for n, name in [(9, 'fast'), (21, 'slow')]:
        b[name] = np.nan
        if len(b) >= n:
            s = pd.concat([pd.Series([b.c.iloc[:n].mean()], index=[n - 1]), b.c.iloc[n:]])
            b.loc[s.index, name] = s.ewm(span=n, adjust=False).mean()
    pc = b.c.shift(1)
    b['atr'] = pd.concat([b.h - b.l, (b.h - pc).abs(), (b.l - pc).abs()], axis=1).max(axis=1).rolling(14).mean()
    b['slope'] = b.slow.diff()
    b['j'] = np.arange(35, 35 + 5 * len(b), 5)
    return b


def rebuild(r, b, baseline):
    # Entry reconstructed without calling any registered signal/helper function.
    entry = None
    for k in b.index[(b.j >= 135) & (b.j <= 360)]:
        for side in [1, -1]:
            now = b.loc[k]
            aligned = side * (now.c - now.slow) > 0 and side * now.slope > 0
            candles = b.loc[[k - 1, k]]
            confirm = ((side * (candles.c - candles.o) > 0) &
                       (side * (candles.c - candles.fast) > 0)).all()
            if aligned and (baseline or confirm):
                entry = k, side
                break
        if entry is not None:
            break
    if entry is None:
        return None
    k, side = entry
    dj, j0 = int(b.loc[k, 'j']), int(b.loc[k, 'j']) + 1
    stop_dist = np.ceil(2 * b.loc[k, 'atr'] * 4) / 4
    ep = r.loc[j0, 'open']
    stop_px = ep - side * stop_dist
    exit_dj, dynamic = 415, False
    for q in range(k + 1, len(b)):
        now, prior = b.loc[q], b.loc[q - 1]
        if now.j >= 415:
            break
        wrong = side * (now.c - now.fast) < 0
        prior_wrong = side * (prior.c - prior.fast) < 0
        aligned = side * (now.c - now.slow) > 0 and side * now.slope > 0
        if wrong and (not aligned or prior_wrong):
            exit_dj, dynamic = int(now.j), True
            break
    limit = exit_dj + 1 if dynamic else 415
    for j in range(j0, limit + 1):
        bar = r.loc[j]
        if dynamic and j == limit:
            px, reason = bar.open, ('stop_gap_at_exit_open' if side * (bar.open - stop_px) <= 0 else 'indicator_next_open')
            break
        if j > j0 and side * (bar.open - stop_px) <= 0:
            px, reason = bar.open, 'stop_gap'
            break
        if (side == 1 and bar.low <= stop_px) or (side == -1 and bar.high >= stop_px):
            px, reason = stop_px, 'stop'
            break
        if j == limit:
            px, reason = bar.close, 'scheduled_flat'
            break
    return dict(decision_j=dj, j0=j0, j1=j, side=side, entry=ep, exit=px,
                stop_points=stop_dist, reason=reason, exit_decision_j=exit_dj)


def main():
    result = json.loads((OUT / 'design_result.json').read_text())
    assert not result['passed'] and not result['placebos_run'] and not result['accounts_tested']
    raw = pd.concat([pd.read_csv(ROOT / f'data/NQ_1min_{y}.csv') for y in range(2018, 2023)])
    raw = raw.drop_duplicates(['date', 'time'])
    raw['j'] = raw.time // 100 * 60 + raw.time % 100 - 480
    raw = raw[(raw.j >= 31) & (raw.j <= 415)]
    data = {d: r.set_index('j').sort_index() for d, r in raw.groupby('date')}
    cov = pd.read_csv(OUT / 'design_coverage.csv', parse_dates=['date'])
    eligible = set(cov.loc[cov.eligible, 'date'])
    cache = {}
    for d in eligible:
        r = data[int(d.strftime('%Y%m%d'))]
        assert len(r) == 385
        cache[d] = r, indicators(r)
    checked = {}
    suffix_checks = 0
    for name, baseline in [('design_trades.csv', False), ('design_baseline_trades.csv', True)]:
        t = pd.read_csv(OUT / name, parse_dates=['date', 'entry_at', 'exit_at', 'exit_interval_start', 'exit_interval_end'])
        assert t.date.is_unique and set(t.date) == eligible
        for row in t.itertuples():
            r, b = cache[row.date]
            z = rebuild(r, b, baseline)
            for field, expected in z.items():
                actual = getattr(row, field)
                assert actual == expected if isinstance(expected, str) else np.isclose(actual, expected), (row.date, field)
            gross = (row.exit - row.entry) * row.side * 2
            assert np.isclose(row.gross_mnq, gross)
            assert np.isclose(row.net_mnq, gross - 2.24)
            assert np.isclose(row.stress_mnq, gross - 4.48)
            eb = r.loc[row.j1]
            assert eb.low <= row.exit <= eb.high
            assert row.entry_at == row.date + pd.Timedelta(minutes=480 + row.j0 - 1)
            if row.reason == 'stop':
                assert pd.isna(row.exit_at)
            else:
                m = 480 + row.j1 - (row.reason != 'scheduled_flat')
                assert row.exit_at == row.date + pd.Timedelta(minutes=m)
            # Recompute features on a truncated prefix: no suffix needed at entry.
            if not baseline:
                prefix = indicators(r.loc[:row.decision_j])
                q = int((row.decision_j - 35) / 5)
                for col in ['fast', 'slow', 'atr', 'slope']:
                    assert np.isclose(prefix.loc[q, col], b.loc[q, col])
                suffix_checks += 1
        old = pd.read_csv(OUT / 'attempt1' / name)
        # Timestamp/reason metadata are the only changed fields after amendment.
        stable = ['day', 'j0', 'j1', 'side', 'entry', 'exit', 'kind', 'pnl', 'mae', 'qty', 'net',
                  'decision_j', 'exit_decision_j', 'stop_points', 'gross_mnq', 'commission_mnq',
                  'slippage_mnq', 'net_mnq', 'stress_mnq', 'net_nq']
        pd.testing.assert_frame_equal(old[stable], t[stable], check_dtype=False)
        checked[name] = len(t)
    for name in ['design_daily.csv', 'design_metrics.csv', 'design_signals.csv']:
        assert (OUT / name).read_bytes() == (OUT / 'attempt1' / name).read_bytes(), name
    old_result = json.loads((OUT / 'attempt1/design_result.json').read_text())
    for key in ['primary', 'baseline', 'stress', 'gates', 'years']:
        assert old_result[key] == result[key]
    t = pd.read_csv(OUT / 'design_trades.csv', parse_dates=['date'])
    daily = pd.read_csv(OUT / 'design_daily.csv', parse_dates=['date'])
    assert np.isclose(daily.net_mnq.sum(), t.net_mnq.sum())
    assert np.isclose(t.net_mnq.sum(), result['primary']['total'])
    assert np.allclose(daily.net_mnq, daily.gross_mnq - daily.commission_mnq - daily.slippage_mnq)
    audit = dict(passed=True, review='Maker raw-minute implementation/accounting audit, not independent economic verification',
                 scalar_reconstructed_trades=checked, entry_prefix_checks=suffix_checks,
                 clock_amendment_economic_columns_identical=True, daily_and_trade_totals_reconcile=True,
                 native_cost_bridge=True, no_recent_or_dependent_stages=True,
                 exit_reasons=t.reason.value_counts().to_dict(),
                 audit_code_sha256=sha(__file__), runner_sha256=sha(ROOT / 'analysis/codex_sentinel_mnq_20261108.py'),
                 result_sha256=sha(OUT / 'design_result.json'),
                 limits=['Same author/maker; no blind checker', 'No native MNQ quotes or broker fills',
                         'Intraminute stop time/order unresolved by OHLC', 'No fresh/2023+ return validation earned'])
    (OUT / 'maker_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    homes = ['Personal', '50K funded', '150K funded', '50K evaluation', '150K evaluation']
    pd.DataFrame([dict(home=h, verdict='No place earned: failed standalone design gate',
                       base_add_replace_empty_run=False) for h in homes]).to_csv(OUT / 'book_disposition.csv', index=False)
    report(result, audit)
    print(json.dumps(audit, indent=2))


def money(x):
    return f'{"−" if x < 0 else ""}${abs(x):,.2f}'


def report(r, audit):
    p, b, s = r['primary'], r['baseline'], r['stress']
    m = pd.read_csv(OUT / 'design_metrics.csv').fillna('')
    text = f'''# Sentinel-inspired MNQ intraday: REJECT at the design gate

Summary: Built the user's own intraday adaptation; it is not the withheld KSE Sentinel/PSX strategy.
Design 2018–22: {p['trades']:,} trades, gross {money(p['gross'])}, net {money(p['total'])} at 1 MNQ, PF {p['profit_factor']:.2f}, t {p['daily_t']:.2f}.
The simpler trend baseline loses less ({money(b['total'])}); higher costs worsen the candidate to {money(s['total'])}.
Only 1 of 5 years is positive; no 2023+ return validation, placebo, account stage or PowerLanguage is earned.
No place earned in personal, 50K/150K funded or 50K/150K evaluation; these are gate dispositions, not account simulations.

Plan: [frozen rules](../plans/sentinel_mnq_20261108.md), committed before returns at `{r['prereg_commit']}`.
[Evidence](../evidence/sentinel_mnq_20261108.md), [runner](../../../analysis/codex_sentinel_mnq_20261108.py),
[maker audit](../../../analysis/codex_sentinel_mnq_20261108_audit.py),
[saved results](../../../analysis/outputs/codex_sentinel_mnq_20261108/design_result.json).
Trials: **one candidate + one baseline = two economic definitions**, no parameter search or side rescue.
One implementation rerun corrected clock metadata only; original output retained in `attempt1/`.

## Rule and source boundary

Five-minute RTH candles, session-reset SMA-seeded EMA9/EMA21. First qualifying two-candle trend entry 10:20–14:00 CT;
one MNQ, one trade/day, next-minute-open entry. Fixed 2 × ATR14 stop, rounded up to0.25point, active from entry minute;
no target. With an aligned master trend, require two wrong-side EMA9 closes to exit; otherwise one. Exit next
minute open, or flatten 14:55 CT. Exact inequalities, seeding and true-range rules are in the committed plan.

Baseline uses first EMA21 position/slope alignment in the same allowed window, without entry candle/EMA9
confirmation; identical stop/exit/cost policy. Entry times can differ, so the delta is a whole-rule comparison,
not proof the candle filter alone caused losses. Both rules get the same 1,238 eligible dates.

Native economics are **one hypothetical MNQ, $2/point** on NQ-price bars, fee $1.24 round trip plus $0.50 per
market/stop fill. Total $2.24/trade. Stress $2.48 plus $1/fill = $4.48. These are assumed costs, not measured fills;
MNQ did not exist before May 2019. NQ prices do not certify MNQ spread, latency or execution parity.

## Design results, 2018-01-01 through 2022-12-30

|Rule/costs|Trades|Gross MNQ|Fees|Slippage|Net MNQ|PF|Daily t|Sharpe|Max daily DD|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
'''
    for label, z in [('Custom, main', p), ('Custom, stress', s), ('Simple trend baseline, main', b)]:
        text += f"|{label}|{z['trades']:,}|{money(z['gross'])}|{money(z['commission'])}|{money(z['slippage'])}|{money(z['total'])}|{z['profit_factor']:.2f}|{z['daily_t']:.2f}|{z['sharpe']:.2f}|{money(z['max_dd'])}|\n"
    text += f'''
Candidate − baseline net = {money(p['total']-b['total'])}, paired daily t = {r['paired_daily_t_vs_baseline']:.2f}.
That weak delta does not establish a significant difference; both standalone rules fail the gate.
Candidate average net {money(p['avg'])}/trade; even before modeled costs average gross is{money(p['gross']/p['trades'])}.
No nonnegative extra round-trip cost fits the observed mean: reducing costs alone to zero still leaves a loss.
Daily metrics include all eligible sessions; unknown data days are excluded visibly, not imputed.

|Side, main costs|Trades|Win|Net MNQ|Avg/trade|Trade t|Sharpe|Sortino|PF|Calmar|Ulcer %|Max daily DD|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
'''
    for side in ['whole', 'long', 'short']:
        z = m[(m.side == side) & (m.year.astype(str) == 'all')].iloc[0]
        text += f"|{side}|{z.trades:,.0f}|{z.win:.1%}|{money(z.total)}|{money(z.avg)}|{z.trade_t:.2f}|{z.sharpe:.2f}|{z.sortino:.2f}|{z.profit_factor:.2f}|{z.calmar:.2f}|{z.ulcer:.2f}|{money(z.max_dd)}|\n"
    text += '''
|Year|Trades|Long net MNQ|Short net MNQ|Whole net MNQ|Baseline net MNQ|
|---|---:|---:|---:|---:|---:|
'''
    for y in range(2018, 2023):
        z = m[m.year.astype(str) == str(y)].set_index('side')
        text += f"|{y}|{z.loc['whole','trades']:,.0f}|{money(z.loc['long','total'])}|{money(z.loc['short','total'])}|{money(z.loc['whole','total'])}|{money(z.loc['baseline','total'])}|\n"
    text += '''
Full side-by-year metrics are in `design_metrics.csv`; no long-only or short-only variant was selected.

## Gates, account homes and stopping

Only the ≥300 trade count passes. Positive net, t≥2, PF≥1.10, ≥4 positive years, positive stress and
better total than baseline all fail. Stop here under the frozen protocol. No placebo, 2023+ returns,
bootstrap/permutation/Monte Carlo, funded/evaluation/personal account comparison or trading implementation.
No BASE/ADD/REPLACE/EMPTY gains, payouts, blow-up probabilities or timing benefits are claimed.
All five homes have **no place earned**, because the standalone gate failed; account harm was not measured.

## Data, clocks and maker audit

1,249 scheduled normal cash sessions; 1,238 complete (99.12%). Eleven incomplete/invalid normal days remain
in `design_coverage.csv`. Ten known early closes skipped by rule. Complete-path inclusion is retrospective
research data selection, not a live skip oracle. Features reset each RTH session, so overnight 03:32/17:01 roll
jumps and cross-session warm-up are absent. Contract IDs/native quotes and undocumented intraday rolls remain limits.

13 synthetic checks cover seeding/causality, exit strictness, entry-minute protection, stop gaps, next-open exit,
short P&L, scheduled flatten and cost bridge. The maker audit separately reconstructs all 2,476 candidate/baseline
entries and exits from raw minutes with pandas EMA seeds and scalar stop walking, checks 1,238 entry prefixes,
fills within the bar, costs and trade-to-day totals. This is the same maker's implementation audit, **not a blind
independent economic checker** or broker-fill verification. No profitable-candidate promotion is requested.

[Clock amendment](../plans/sentinel_mnq_20261108_clock_amendment.md), commit `b4b2ede0`: intraminute stops now
have an explicit containing-minute interval and missing exact `exit_at`; gap/open and scheduled close events retain
their modeled timestamps. The first output is preserved. Audit asserts every economic column, daily P&L,
signal, metric and gate is unchanged. Two definitions remain two definitions; this was no new strategy look.
A one-minute stop interval cannot establish the actual tick time or broker latency.

## Five source questions, updated by the requested build

1. **About:** the paper describes daily PSX trend continuation; our requested experiment adapts the disclosed concept
   to a different market/timeframe with explicit new settings.
2. **Findings:** the author's PF 2.51/Sharpe 2.08 remain unreplicated source claims. Our frozen MNQ proxy loses money
   in 2018–22 before and after costs; it earns no further validation.
3. **Why money, if any:** persistence is the proposed mechanism, without a verified forced flow. This construction
   demonstrates no design-period profit; do not explain it with an invented market story.
4. **Build on it:** this specific user-requested adaptation is now tested and rejected. No rescue search is justified.
   Exact PSX reproduction remains a separate source/data gate, not refuted by this MNQ result.
5. **Strategy code:** **yes**, reproducible Python research code and ledgers were made. No MultiCharts code is earned
   under the project rule requiring a passing strategy first; no profitability or live suitability follows from coding.

## Reproduce

From repository root, with the frozen plan and code committed:

```sh
python analysis/codex_sentinel_mnq_20261108.py inventory --period design
python analysis/codex_sentinel_mnq_20261108.py synthetic
python analysis/codex_sentinel_mnq_20261108.py run --period design
python analysis/codex_sentinel_mnq_20261108_audit.py
```

`design_result.json` records input hashes, code SHA, dependencies and gates;`maker_audit.json` records reconciliation.
For Claude: `agents/codex/results/sentinel_mnq_20261108.md` — reject custom MNQ version; exact PSX source still gated.
No tier, portfolio, live strategy, account/broker/VPS setting or orders changed.
'''
    REPORT.write_text(text)


if __name__ == '__main__':
    main()
