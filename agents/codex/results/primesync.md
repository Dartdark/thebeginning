# PrimeSync: WATCH — research code built; full-target exit selected

Summary: Built the requested PowerLanguage prototype and tested two frozen exit protocols.
Milestones/full exit4.5R beat thirds in all four2018-22 contexts; equal-context difference90% interval favors full exits.
Chosen protocol stayed positive on2023+; PF1.06–1.28 and weak individual significance leave the entry unvalidated.
Default ExitMode0; parameters are explicit assumptions and MultiCharts compilation/parity remain unverified.
Queued for later review; no trading plan or live files changed.

Plan: agents/codex/plans/primesync.md, committed **ac08941890778a751039490a38a8fa5abd1def38** before returns.
Evidence: agents/codex/evidence/primesync.md.
Scripts: analysis/codex_primesync.py; analysis/codex_primesync_stats.py.
Outputs: analysis/outputs/codex_primesync/.
Trials: two exit protocols across four user-specified contexts = **eight design cells**, four frozen adverse-path diagnostics,
then four recent cells for the selected exit only. All are disclosed; no market/timeframe or side was selected.

## Code and rule as tested

[PowerLanguage code](../code/PrimeSync_v1.txt) · [Research setup](../code/PrimeSync_SETUP.md).
The user explicitly requested this code prototype before the usual code-after-validation gate,
and then asked to compare the exit styles and retain the better performer.

The source description leaves thresholds, MA type, VWAP anchor, chop definition,
ATR multiple, cooldown, sizing and session unspecified. These are our unoptimized
assumptions: SMA150; RTH chart-bar typical-price VWAP reset08:30 CT; volume>1.5x
prior20-bar mean; range>1.2x prior20-bar mean; ADX14>=20; stop1.5x simple ATR14;
4-bar cooldown; entries after08:30 and strictly before14:30; normal cash sessions
only; flat15:00. Indicators use Globex chart bars; total volume means Ticks.
Both directions remain enabled. No assertion of institutional order flow is established.

Both protocols use a $500 planned stop-risk budget, $5 per-unit sizing reserve,
max30 micros and quantities rounded down to multiples of3. The geometry/signal
history is NQ/ES; traded-dollar units are MNQ/MES equivalents. Actual next-minute
market entry slips one tick. R remains frozen from the signal ATR, anchored at
actual slipped entry. Stops/market exits slip one tick; targets require one point
trade-through; commission is assumed $1.04 per micro round trip. Every exited
unit is charged. No compounding or fractional tranche is used.

- **Milestones (ExitMode0):** TP1=1.5R touch raises stop to entry; TP2=2.5R
  touch raises it to the original TP1; all contracts target4.5R.
- **Thirds (ExitMode1):** one-third exits at each target; stop advances after
  the actual partial fills. A touched but unfilled limit does not count as a fill.

## Design exit comparison, 2018-22

Dollars below are actual micro-equivalent totals at the fixed research risk,
not per1 NQ/ES, yearly income or account payouts. Contexts overlap and must not
be summed as independent evidence or an approved executable portfolio.

| Context | Exit | Positions | Net | PF | Sharpe | Max DD |
|---|---|---|---|---|---|---|
| NQ_15 | Milestones | 373 | $15,633.36 | 1.20 | 0.59 | $6,385.02 |
| NQ_15 | Thirds | 373 | $6,938.36 | 1.09 | 0.31 | $7,540.64 |
| NQ_30 | Milestones | 181 | $13,360.62 | 1.42 | 0.81 | $3,234.78 |
| NQ_30 | Thirds | 181 | $10,480.12 | 1.33 | 0.74 | $3,087.78 |
| ES_15 | Milestones | 351 | $6,666.48 | 1.09 | 0.27 | $7,698.66 |
| ES_15 | Thirds | 350 | $3,627.10 | 1.05 | 0.17 | $7,795.09 |
| ES_30 | Milestones | 207 | $16,616.40 | 1.45 | 0.90 | $3,464.76 |
| ES_30 | Thirds | 207 | $13,248.90 | 1.36 | 0.84 | $3,097.26 |

The full-target style earned more in all four contexts. The equal-context
selection score is **$13,069** for full exits versus **$8,574** for thirds.
The paired20-day-block90% interval for **thirds minus full** is **−$6,980 to
−$2,144**, favoring full exits. This is an exit comparison conditional on this
reconstructed entry and sample, not proof of future profitability.
Some thirds configurations have smaller drawdowns; best net P&L is not necessarily
best funded-account survival. No account-level exit comparison has been made.

The selected style passed the registered cheap gate: daily t2.12 on the correlated
equal-context score, all four contexts net positive, sufficient events, no unresolved
held path, and positive excluding broad roll flags / under adverse-first execution.
It does not clear the repository's broader multiple-testing promotion standard by itself.

## Selected exit on recent history, 2023 through2026-10-09

| Context | Positions | Net | PF | Trade t | Sharpe | Max DD |
|---|---|---|---|---|---|---|
| NQ_15 | 223 | $10,344.54 | 1.23 | 1.17 | 0.59 | $6,210.18 |
| NQ_30 | 129 | $5,992.56 | 1.28 | 1.08 | 0.55 | $4,868.94 |
| ES_15 | 298 | $3,736.29 | 1.06 | 0.38 | 0.19 | $9,221.61 |
| ES_30 | 178 | $5,540.82 | 1.18 | 0.85 | 0.43 | $6,138.27 |

All four remain positive, but each recent trade t is below2. The1000-run,
20-day-block90% Sharpe intervals include zero for all four whole-context results:
NQ15 [−0.30,1.33], NQ30 [−0.32,1.21], ES15 [−0.65,0.94], ES30 [−0.42,1.12].
The equal-context score's recent Sharpe is0.63, interval [−0.17,1.28]. This is
modest historical evidence with substantial uncertainty. Long-only superiority
was not reproduced consistently; no side was dropped or re-optimized.
Recent history is already seen market history, not a fresh confirmatory holdout.

## Standard whole/long/short metrics for the selected exit

Avg$/position uses actual micro quantities. Avg$/mini normalizes each position's
net to one NQ for NQ contexts, or one ES for ES contexts; it is not an executable
fractional-contract result. Drawdown is the daily realized equity drawdown.

| Period | Context | Side | N | Win | Avg$/position | Avg$/mini | t | Sharpe | Sortino | PF | Calmar | Ulcer | MaxDD$ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2018-22 | NQ_15 | whole | 373 | 31.9% | 41.91 | 119.13 | 1.33 | 0.59 | 1.22 | 1.20 | 0.47 | 4.67 | 6,385.02 |
| 2018-22 | NQ_15 | long | 156 | 31.4% | 9.88 | 17.04 | 0.21 | 0.09 | 0.18 | 1.04 | 0.06 | 4.35 | 5,300.04 |
| 2018-22 | NQ_15 | short | 217 | 32.3% | 64.94 | 192.53 | 1.54 | 0.68 | 1.49 | 1.32 | 0.41 | 6.73 | 6,564.18 |
| 2018-22 | NQ_30 | whole | 181 | 39.8% | 73.82 | 192.78 | 1.83 | 0.81 | 1.74 | 1.42 | 0.80 | 1.57 | 3,234.78 |
| 2018-22 | NQ_30 | long | 78 | 44.9% | 96.12 | 146.72 | 1.56 | 0.68 | 1.52 | 1.59 | 0.50 | 2.11 | 2,915.16 |
| 2018-22 | NQ_30 | short | 103 | 35.9% | 56.93 | 227.66 | 1.07 | 0.47 | 1.00 | 1.31 | 0.32 | 2.83 | 3,511.68 |
| 2018-22 | ES_15 | whole | 351 | 32.5% | 18.99 | 69.91 | 0.62 | 0.27 | 0.53 | 1.09 | 0.17 | 6.19 | 7,698.66 |
| 2018-22 | ES_15 | long | 157 | 32.5% | 1.61 | 0.11 | 0.04 | 0.02 | 0.03 | 1.01 | 0.01 | 5.92 | 6,951.96 |
| 2018-22 | ES_15 | short | 194 | 32.5% | 33.06 | 126.39 | 0.76 | 0.33 | 0.68 | 1.16 | 0.15 | 6.92 | 8,540.16 |
| 2018-22 | ES_30 | whole | 207 | 40.1% | 80.27 | 145.76 | 2.05 | 0.90 | 1.94 | 1.45 | 0.93 | 2.68 | 3,464.76 |
| 2018-22 | ES_30 | long | 92 | 47.8% | 115.30 | 160.39 | 2.17 | 0.93 | 2.09 | 1.75 | 0.82 | 2.26 | 2,504.13 |
| 2018-22 | ES_30 | short | 115 | 33.9% | 52.25 | 134.06 | 0.93 | 0.41 | 0.90 | 1.26 | 0.18 | 4.34 | 6,407.82 |
| 2023+ | NQ_15 | whole | 223 | 31.4% | 46.39 | 138.21 | 1.17 | 0.59 | 1.24 | 1.23 | 0.43 | 4.79 | 6,210.18 |
| 2023+ | NQ_15 | long | 106 | 34.9% | 50.92 | 150.40 | 0.92 | 0.47 | 0.97 | 1.26 | 0.32 | 3.20 | 4,271.52 |
| 2023+ | NQ_15 | short | 117 | 28.2% | 42.28 | 127.16 | 0.75 | 0.38 | 0.84 | 1.21 | 0.27 | 3.40 | 4,732.62 |
| 2023+ | NQ_30 | whole | 129 | 42.6% | 46.45 | 149.37 | 1.08 | 0.55 | 1.06 | 1.28 | 0.31 | 2.77 | 4,868.94 |
| 2023+ | NQ_30 | long | 58 | 36.2% | -39.67 | -138.85 | -0.75 | -0.39 | -0.61 | 0.79 | -0.08 | 7.15 | 7,226.04 |
| 2023+ | NQ_30 | short | 71 | 47.9% | 116.81 | 384.81 | 1.83 | 0.91 | 2.07 | 1.80 | 1.04 | 1.93 | 2,037.66 |
| 2023+ | ES_15 | whole | 298 | 30.9% | 12.54 | -6.88 | 0.38 | 0.19 | 0.38 | 1.06 | 0.10 | 7.38 | 9,221.61 |
| 2023+ | ES_15 | long | 115 | 29.6% | -33.10 | -72.14 | -0.69 | -0.34 | -0.59 | 0.85 | -0.09 | 9.86 | 10,389.24 |
| 2023+ | ES_15 | short | 183 | 31.7% | 41.22 | 34.14 | 0.92 | 0.47 | 1.02 | 1.20 | 0.43 | 2.64 | 4,438.44 |
| 2023+ | ES_30 | whole | 178 | 38.8% | 31.13 | 35.81 | 0.85 | 0.43 | 0.84 | 1.18 | 0.23 | 3.78 | 6,138.27 |
| 2023+ | ES_30 | long | 72 | 40.3% | 2.96 | 27.97 | 0.06 | 0.03 | 0.05 | 1.02 | 0.01 | 3.18 | 3,764.76 |
| 2023+ | ES_30 | short | 106 | 37.7% | 50.26 | 41.13 | 0.99 | 0.51 | 1.08 | 1.30 | 0.32 | 2.89 | 4,223.88 |
| Full | NQ_15 | whole | 596 | 31.7% | 43.59 | 126.27 | 1.77 | 0.59 | 1.23 | 1.21 | 0.45 | 4.31 | 6,385.02 |
| Full | NQ_15 | long | 262 | 32.8% | 26.49 | 70.99 | 0.74 | 0.25 | 0.49 | 1.12 | 0.14 | 4.56 | 5,653.62 |
| Full | NQ_15 | short | 334 | 30.8% | 57.00 | 169.63 | 1.69 | 0.56 | 1.24 | 1.28 | 0.32 | 5.38 | 6,564.18 |
| Full | NQ_30 | whole | 310 | 41.0% | 62.43 | 174.71 | 2.12 | 0.70 | 1.45 | 1.37 | 0.44 | 1.88 | 4,868.94 |
| Full | NQ_30 | long | 136 | 41.2% | 38.21 | 24.93 | 0.90 | 0.30 | 0.60 | 1.22 | 0.07 | 5.08 | 7,988.04 |
| Full | NQ_30 | short | 174 | 40.8% | 81.36 | 291.78 | 1.99 | 0.66 | 1.43 | 1.48 | 0.44 | 2.43 | 3,511.68 |
| Full | ES_15 | whole | 649 | 31.7% | 16.03 | 34.65 | 0.71 | 0.24 | 0.46 | 1.07 | 0.12 | 6.40 | 9,221.61 |
| Full | ES_15 | long | 272 | 31.2% | -13.07 | -30.44 | -0.41 | -0.13 | -0.24 | 0.94 | -0.04 | 7.90 | 10,389.24 |
| Full | ES_15 | short | 377 | 32.1% | 37.02 | 81.61 | 1.19 | 0.40 | 0.83 | 1.18 | 0.18 | 5.46 | 8,540.16 |
| Full | ES_30 | whole | 385 | 39.5% | 57.55 | 94.92 | 2.13 | 0.71 | 1.46 | 1.33 | 0.40 | 2.80 | 6,138.27 |
| Full | ES_30 | long | 164 | 44.5% | 65.98 | 102.25 | 1.75 | 0.58 | 1.15 | 1.40 | 0.32 | 2.43 | 3,764.76 |
| Full | ES_30 | short | 221 | 35.7% | 51.30 | 89.49 | 1.35 | 0.45 | 0.98 | 1.28 | 0.19 | 3.71 | 6,407.82 |

Full by-year results are in selected_full_by_year.csv, with complete trade,
fill, signal, cost and bootstrap records beside it. Scale-outs count as one
flat-to-flat position. Metrics and ledgers are generated by the committed scripts.

## Execution/data checks, limitations and account scope

Six synthetic execution cases pass, including initial entry-bar stop, gap-through
stop, target touch versus fill, TP2 then stop atTP1, short symmetry, unknown paths
and integer quantities. All12 position/fill ledgers reconcile quantities and
costs; no held-path P&L is unresolved. PowerLanguage structural checks pass,
but they are not a compiler and cannot establish platform order behavior.

Reuse of existing Grid24 caches avoids rebuilding market grids. Incomplete
signal/VWAP histories and missing scheduled entries are inventoried, not silently
late-filled. Indicators require300 chart bars of warm-up. Continuous prices are
unadjusted: signals with a150-bar window overlapping the broad quarterly roll
window are flagged, and the cheap gate remains positive excluding them. That is
not verified individual-contract roll provenance.

The minute path follows the repository open-to-nearer-extreme-first convention.
The adverse-extreme-first diagnostic produced the same chosen totals here;
that does not establish tick-level sequence. Neither a stop nor the planned risk
budget guarantees the realized loss during gaps.

MC uses native symbol Ticks/BigPointValue and its own ADX initialization; the
screen uses mini-volume/price with micro sizing/costs. Match the research units
as documented before comparing reports. Native micro volume can change signals.
The code issues initial built-in protection, bar-close entries, IOG raised stops
and a next-event exit after the15:00 close; the Python time exit uses that
minute's close with slippage. This timing difference, seeds, missing data and
partial-order lifecycle require MC comparison. Live partial entry fills, broker
rejections and independent position synchronization were not validated.

| Destination | Current evidence |
|---|---|
| 50K evaluation | No placement established; no funded/evaluation gain inferred from standalone P&L |
| 150K evaluation | Same; native parity and independent strategy evidence pending |
| 50K funded | Same; $500 research budget is not an allocation recommendation |
| 150K funded | Same; no payout/blow-up comparison completed |
| Current personal portfolio | Potential research candidate, no measured marginal contribution yet |

The original protocol reserves matched random-side/time controls and global
selection-adjusted evidence for a later registered validation stage. They were
not run here; a superior exit cannot substitute for an entry placebo. Independent
review and native MC parity are prerequisites before a full account claim.
PrimeSync is therefore **WATCH**, with the selected research code preserved,
not a profitable live strategy or a new plan allocation.

## Reproduce and next step

```sh
/workspace/venvs/thebeginning/bin/python analysis/codex_primesync.py
/workspace/venvs/thebeginning/bin/python analysis/codex_primesync_stats.py
```

Compile the new Signal on a separate research chart and export Settings/List
of Trades plus matching minute/total-volume data. Follow PrimeSync_SETUP.md,
including the distinction between mini charts and micro risk units. The TODO
verification queue records the pending work. No live/VPS/broker changes.

For Claude: agents/codex/results/primesync.md.
