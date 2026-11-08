# Sentinel-inspired MNQ intraday: REJECT at the design gate

Summary: Built the user's own intraday adaptation; it is not the withheld KSE Sentinel/PSX strategy.
Design 2018–22: 1,238 trades, gross −$240.50, net −$3,013.62 at 1 MNQ, PF 0.90, t -1.23.
The simpler trend baseline loses less (−$1,999.62); higher costs worsen the candidate to −$5,786.74.
Only 1 of 5 years is positive; no 2023+ return validation, placebo, account stage or PowerLanguage is earned.
No place earned in personal, 50K/150K funded or 50K/150K evaluation; these are gate dispositions, not account simulations.

Plan: [frozen rules](../plans/sentinel_mnq_20261108.md), committed before returns at `5e066bb56aa587f33c11248eb6bad59e696b1ac4`.
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
|Custom, main|1,238|−$240.50|$1,535.12|$1,238.00|−$3,013.62|0.90|-1.23|-0.55|$3,519.72|
|Custom, stress|1,238|−$240.50|$3,070.24|$2,476.00|−$5,786.74|0.82|-2.36|-1.06|$6,067.58|
|Simple trend baseline, main|1,238|$773.50|$1,535.12|$1,238.00|−$1,999.62|0.93|-0.83|-0.37|$2,918.30|

Candidate − baseline net = −$1,014.00, paired daily t = -0.55.
That weak delta does not establish a significant difference; both standalone rules fail the gate.
Candidate average net −$2.43/trade; even before modeled costs average gross is−$0.19.
No nonnegative extra round-trip cost fits the observed mean: reducing costs alone to zero still leaves a loss.
Daily metrics include all eligible sessions; unknown data days are excluded visibly, not imputed.

|Side, main costs|Trades|Win|Net MNQ|Avg/trade|Trade t|Sharpe|Sortino|PF|Calmar|Ulcer %|Max daily DD|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|whole|1,238|36.1%|−$3,013.62|−$2.43|-1.23|-0.55|-0.95|0.90|-0.17|2.91|$3,519.72|
|long|690|37.7%|−$1,931.10|−$2.80|-1.19|-0.54|-0.86|0.87|-0.14|2.02|$2,794.56|
|short|548|34.1%|−$1,082.52|−$1.98|-0.59|-0.26|-0.48|0.93|-0.08|2.32|$2,936.34|

|Year|Trades|Long net MNQ|Short net MNQ|Whole net MNQ|Baseline net MNQ|
|---|---:|---:|---:|---:|---:|
|2018|245|−$414.80|−$14.00|−$428.80|$174.70|
|2019|248|−$350.14|−$173.38|−$523.52|−$239.52|
|2020|246|$674.92|−$325.46|$349.46|−$717.04|
|2021|250|$790.34|−$1,796.84|−$1,006.50|−$128.50|
|2022|249|−$2,631.42|$1,227.16|−$1,404.26|−$1,089.26|

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
