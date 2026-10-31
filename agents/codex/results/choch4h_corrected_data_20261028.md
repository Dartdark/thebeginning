# Four-hour CHoCH, repaired sources: no design pass

Summary: The new uploads are overnight data. Combining them with existing daytime files, plus old observed midnight bars, produces a much larger test of both frozen pivot definitions. On fully observed 2018–22 trades, one-bar confirmation loses $1,392.78/MNQ (t -0.219); two-bar confirmation earns $3,287.00 (t 0.583), with only two positive years. The requested ideal-close benchmark is also weak. Neither passes the original design gate. Remaining unresolved trades prevent claiming complete strategy/account returns. No 2023+ strategy returns, tuning, placebo or account bench was run.

Original plan: [CHoCH baseline](../plans/choch4h_20261028.md), public preregistration `eda41d03bc52f7c88afe65fb5af0eb07f4d1d957`.
Source continuation: [committed corrected-source plan](../plans/choch4h_corrected_data_20261028.md), local commits `b0f54a5` / `e16df1f` before the corresponding source replication.
New wrapper: [`analysis/codex_choch4h_corrected_data.py`](../../../analysis/codex_choch4h_corrected_data.py).
Original strategy/engine wrapper: [`analysis/codex_choch4h.py`](../../../analysis/codex_choch4h.py), unchanged.
Results: [`design/summary.json`](../../../analysis/outputs/codex_choch4h_corrected_20261028/design/summary.json).

## Same strategy

NQ four-hour windows aligned to the 17:00 CT CME session. Full windows close 21:00, 01:00, 05:00, 09:00 and 13:00; the final 3-hour stub is not a four-hour signal/pivot bar. Strict one- or two-candle pivots are only available after their right-side confirmation closes. HH/HL structure closing through its latest confirmed low gives a short, stopped at the most recent confirmed high; lower structure breaking its latest confirmed high gives the mirrored long. Target is one raw entry-to-stop distance. Both sides, one position, no filters, no pyramiding. Hold until stop/target, including overnight/weekends.

Close benchmark: use signal closing price, with exits tested only afterward; it is not a guaranteed obtainable fill. Primary executable proxy: open of minute labelled signal+2 (one physical minute after the completed close). Stops active on the entry bar; worse gap-open fills; shared repo minute-path engine and one-point target-through. The target is 1:1 before costs. Costs per MNQ scenario: $1.24 round-trip commission plus one 0.25-point tick per side, $2.24 total. NQ prices proxy micro fills, including 2018 before MNQ launch; native spread/liquidity and continuous roll identity remain unverified.

## Source repair and audit

The latest files have no 08:00–15:15 rows: they are overnight exports despite their filenames. They restore 17:01 on most sessions, but omit 00:01 on most older dates. Existing old overnight exports contain those midnight observations. Before reconciled returns, **every overlapping OHLCV observation in each 2017–22 old/new overnight pair matched exactly**, with zero conflicts. The wrapper adds only old-only observed keys to the new export: 1,270 restored rows across 2018–22. No price interpolation, forward fill or invented candle was used. [Reconciliation hashes/counts](../../../analysis/outputs/codex_choch4h_corrected_20261028/reconciliation.json); [upload manifest](../inputs/choch4h_corrected_20261028/manifest.json).

The historical scheduled 15:15–15:30 CT pause is excluded through June 25, 2021; no pause from trade date June 28. This implements the already registered scheduled-closure exclusion. Secondary calendar source: pandas_market_calendars `calendars/cme.py`, blob `bc76716e37c8e93fce01714b2a336955dd97dc50`. Primary CME schedule authentication and complete holiday coverage are not claimed. Other unverified holiday/data gaps remain unresolved. Date/time-only checks and hashes on newer uploads are not 2023+ strategy validation.

The combined source's audited observed candles have no conflicting keys or malformed OHLCV observations. Complete candidate windows: 6,114; incomplete expected windows: 1,709, including partial 2017 warm-up without a corresponding daytime file. An incomplete candle resets structure rather than manufacturing its high/low. The 2018–22 strategy is therefore still coverage-conditioned. Ten core synthetic check groups passed (causality, future perturbation, side symmetry, stops/gaps/target-through), plus pre/post-pause and maintenance calendar assertions. These test mechanics, not alpha.

## Results: fully observed 2018–22 subsets, per one MNQ

| Model | Raw signals | Resolved trades | Unresolved trades | Win rate | Net total | Mean net | Trade t | Daily NW5 t | PF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| One-bar, executable | 289 | 147 | 45 | 51.02% | -$1,392.78 | -$9.47 | -0.219 | -0.211 | 0.958 |
| Two-bar, executable | 158 | 75 | 37 | 52.00% | +$3,287.00 | +$43.83 | 0.583 | 0.570 | 1.166 |
| One-bar, ideal close | 289 | 149 | 44 | 50.34% | +$226.74 | +$1.52 | 0.035 | 0.034 | 1.007 |
| Two-bar, ideal close | 158 | 74 | 37 | 52.70% | +$3,363.24 | +$45.45 | 0.598 | 0.605 | 1.172 |

Raw signals include those skipped while another position is open, hence they do not equal resolved plus unresolved trades. Unknown trades are never assigned zero or fabricated returns. The runner blocks later entries through their next observed bracket-hit boundary. Nevertheless, the resolved subset is **not a complete executable portfolio or an unbiased estimate of the full strategy**: missing candles affect entries and unresolved trades affect performance. These limitations apply to every table here.

One-bar executable gross mean is -$7.23/MNQ: it fails even before costs. Two-bar gross mean $46.07 clears the $4.48 cheap gross hurdle, but trade t 0.583 and 2/5 positive years fail the frozen design criteria. The same-close benchmark does not provide convincing evidence either. Do not label the two-bar rule a selected winner or count its positive net as promotion.

### Five metrics and marked drawdown — same qualified subsets

| Model | Sharpe | Sortino | Profit factor | Calmar | Ulcer | Max marked DD |
|---|---:|---:|---:|---:|---:|---:|
| One-bar executable | -0.093 | -0.127 | 0.958 | -0.031 | 5.148 | $8,674.90 |
| Two-bar executable | 0.268 | 0.401 | 1.166 | 0.105 | 5.041 | $6,023.04 |
| One-bar close | 0.015 | 0.021 | 1.007 | 0.006 | 4.671 | $7,599.50 |
| Two-bar close | 0.278 | 0.417 | 1.172 | 0.108 | 4.948 | $6,013.92 |

Daily marks use observed 16:00 CT closes while held plus actual resolved exits, allocating evening events to the next session date; daily totals reconcile exactly to resolved trade nets. Unresolved P&L is excluded, not imputed. Ulcer uses the shared $50K reference capital; this is not an Apex account simulation. Fees/slippage are charged $1.12 per entry and exit. Historical gaps/holiday hours remain limitations.

### By year, executable net / one MNQ

| Year | One-bar | Two-bar |
|---|---:|---:|
| 2018 | +$1,315.38 | -$74.20 |
| 2019 | +$512.94 | +$1,414.36 |
| 2020 | +$1,912.62 | -$1,805.32 |
| 2021 | +$937.08 | -$673.86 |
| 2022 | -$6,070.80 | +$4,426.02 |

### Long and short, executable

| Model / side | Resolved trades | Net | Trade t |
|---|---:|---:|---:|
| One-bar long | 70 | -$1,497.80 | -0.345 |
| One-bar short | 77 | +$105.02 | 0.022 |
| Two-bar long | 36 | +$1,092.86 | 0.273 |
| Two-bar short | 39 | +$2,194.14 | 0.545 |

Complete side metrics and close-benchmark years are retained in the summary JSON. The two-bar result is heavily helped by 2022; no year, direction or stop range was dropped or tuned after seeing it.

## Gate, history and limitations

Neither primary passes design. No 2023+ prices/returns were evaluated, no full 2018–26 t is available, and no claims are made from placebo, selection, dependence, Monte Carlo or account comparisons that were not run. The lower diagnostic t here has no connection to the stopped t6 program; its thresholds/watchers remain stopped.

This continuation completes four corrected-source financial ledgers for the same two structural configurations. Earlier eight completed ledger executions remain preserved. The new-only intermediate attempt had two unknown entries and stopped on a zero-resolved reporting-schema error; its partial ledger is retained. A subsequent safe cache-link mismatch aborted before any ledger; its partial audit is retained. The wrapper now verifies existing reconciled files on restart and uses a separate source staging path/cache. These are engineering/source corrections, not extra independent discoveries or erased failures. No parameter sweep.

## All five plan homes

| Plan | Verdict |
|---|---|
| Personal | **No earned slot.** Cheap design evidence is weak, unresolved coverage persists, and no BASE/ADD/REPLACE/EMPTY improvement was measured. |
| 50K funded | **No place as written.** Multiday/weekend holding violates the adopted flat-by-daily-close protocol. No payout gain claimed. |
| 150K funded | **No place as written.** Same holding mismatch; no extrapolation from 50K. |
| 50K evaluation | **No place as written.** Holding mismatch plus no valid joint account/pass path. |
| 150K evaluation | **No place as written.** Same mismatch; no inferred pass-rate benefit. |

These are eligibility/qualification conclusions, not measured harm to every book. Do not infer that adding an intraday forced exit preserves these returns.

## Recommendation

Do not build a larger filtered system around this 1:1 version on the evidence so far. It is a mechanically testable baseline, but neither definition shows convincing design evidence, even at the ideal close. Keep the failure/history; do not optimize a side, anchor or indicator to make these results look stronger. If the user elects a follow-up, a narrowly preregistered 1:2 exit comparison using the SAME entries/stops would be a new counted design study, not automatic approval to rescue this version. No such follow-up was run.

Code, checks, signal/trade/daily ledgers, summaries and source hashes are published. Raw uploads, reconciled raw CSVs, cache links and bulky intermediate aggregate bar tables remain local; the wrapper reproduces them. No root TODO/ranking, plan allocation, live/VPS/broker/API setting or automation was changed.

For Claude: review `agents/codex/results/choch4h_corrected_data_20261028.md`; source repair completed, one-/two-bar 4h CHoCH still no design pass, no historical-validation run or plan addition.
