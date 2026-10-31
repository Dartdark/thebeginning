# ML straddle/buffer strategy: REJECT as specified — execution uses future extrema

Summary: Equal long/short equity entries are followed by ML direction selection and next-day buffered exits.
Authors claim cumulative 14,051%/Sharpe 14.86 at 10% buffer and 583%/Sharpe 7.26 at 30%, on 484 test days.
Exit formulas require next-day final high/low, without a causal estimator or order-update specification.
Entry prices cancel in combined dollar P&L; high old-anchor classification accuracy is not proof of future edge.
Source algebra/clock audit completed; no market-return test, candidate allocation or new trial warranted.

Source: Jaime González-Maiz-Jiménez, Francisco López-Herrera and Adán Reyes-Santiago,
*Machine Learning Straddle Strategy with Buffer-Based Execution: A Patient Trader Approach to Equity Trading*,
SSRN 6401038. Indexed SSRN metadata lists posting 2026-03-13; uploaded PDF modified 2026-03-12.
The document says not peer reviewed. Main manuscript PDF 32–101 read, including references; initial 31 pages are
standalone figures repeated later. Embedded figure text was OCRed; representative mechanism image visually checked.
Native text extraction works for the main manuscript, while initial figures require image extraction/OCR.

[Owned PDF](../inputs/straddle_buffer_6401038_20261031/source.pdf) ·
[native text](../inputs/straddle_buffer_6401038_20261031/source.txt) ·
[figure OCR](../inputs/straddle_buffer_6401038_20261031/figure_ocr.txt) ·
[access/extraction receipt](../inputs/straddle_buffer_6401038_20261031/source_access.json).
[Executable audit](../../../analysis/codex_straddle_buffer_audit_20261031.py) ·
[claims](../../../analysis/outputs/codex_straddle_buffer_audit_20261031/claims.json) ·
[checks](../../../analysis/outputs/codex_straddle_buffer_audit_20261031/checks.json) ·
[hashes](../../../analysis/outputs/codex_straddle_buffer_audit_20261031/manifest.json).
Plan: none admitted. New economic return definitions/trials/account simulations 0; scout state unchanged.

## Five questions

1. **What is it about?** Simultaneously buy and short the same equity at day-t open. After day-t close,
   predict whether day-t+1 close exceeds the old day-t open. Cover the contrary leg near day-t+1's favorable
   extreme and close the retained leg at day-t+1 close. The name does not describe an options straddle.
2. **What does it find?** Authors report extraordinary equity results at 10%/20%/30% range buffers: cumulative
   returns 14,051%/2,688%/583%, annualized Sharpes 14.86/11.32/7.26 and win rates 85.5%/75.2%/65.6%. These
   are unverified author claims dependent on their exit model. We independently checked algebra and causality,
   not historical alpha, actual fills or income. No corrected performance estimate is available.
3. **Why does it make money, if it does?** Authors attribute profits to patient liquidity provision and ML.
   As specified, exits use realized future extrema; this can manufacture favorable selection of prices. No
   demonstrated executable liquidity premium is established. With equal quantities, the position is flat until
   one leg closes; profits then require a favorable directional position from that exit price to final close.
4. **Can we build on it?** Yes as a caution about target design, netting, causal orders and accounting. Reject
   it as a strategy now. Additional ordinary OHLC data cannot repair an order that needs future high/low.
   A separately justified strategy needs levels computed from information known before order placement, explicit
   missed-fill treatment and genuine forward-return baselines. Do not invent that adaptation to rescue this paper.
5. **Can a strategy code be made?** A literal hindsight simulator and a research audit can be coded; the audit
   is supplied here. A faithful **causal tradable strategy cannot yet be coded** from the stated rules because
   there is no pre-order forecast of the high/low, running-extreme policy, cancellation logic or no-fill fallback.
   Choosing any such rule changes the strategy and requires fresh evidence/preregistration. No trading code built.

## Published rule, sample and reported numbers

Sample:48 US-traded equities/ADRs/ETFs, Yahoo adjusted daily OHLCV, January 2,2018–November 28,2025.
Three tree classifiers, two feature-selection approaches and three buffers produce 864 configurations.
Chronological 75/25 train/test splits are applied separately within five overlapping periods. Full-sample
headlines concern the last 25%, approximately 484 test days in Table 13, not returns earned over all eight years.
Other sections give approximate 497 days. Overlapping periods are not independent forward experiments.

|Buffer|Cumulative return|Annualized Sharpe|Win rate|Table 13 max-DD statistic|
|---|---:|---:|---:|---:|
|10%|14,051%|14.86|85.5%|−1.6%|
|20%|2,688%|11.32|75.2%|−4.1%|
|30%|583%|7.26|65.6%|−10.6%|

All are aggregated author statistics across configurations; no single executable portfolio ledger or account
drawdown is established. Separate mean-drawdown tables mix periods and report different values. Do not quote
these figures as verified funded risk, forecast earnings or approved capital sizing.

## Decisive execution and information checks

**Future extrema:** Eq 2/PDF 42 covers a short at `L[t+1]+beta*(H[t+1]-L[t+1])`; Eq 3 sells a long at
`H[t+1]-beta*(H[t+1]-L[t+1])`. These are the final high/low of the execution day. The prose says expected
extremes and admits they are unknown, but supplies no estimator connecting expected to realized values.
PDF 60/97 assumes execution when a price touches the resulting level. That does not establish that the order
existed before the touch. Increasing beta from 10% to 30%, adding slippage or adjusting Sharpe for multiplicity
does not cure the unavailable information. Daily OHLC alone also cannot establish queue fills or trade order.

Our constructed counterexample has the identical observed prefix 100,99,101 followed either by 105,104 or 90,92.
At 30% buffer the final-day UP exit is 100.8 in one continuation and 93.3 in the other. A prefix-only order
cannot choose both with knowledge of the later path. This establishes the missing causal specification; it
does not prove the unavailable private author code used one particular faulty implementation.

**Offsetting entries:** with one share each, UP gross P&L is `(C-O)+(O-P)=C-P`; DOWN is
`(O-C)+(P-O)=P-C`. The initial entry cancels exactly. Tested entries 80/100/150 give the same dollar outcomes
for fixed exit and close. The normalization denominator, margin and fees remain separate. Equal static opposite
positions are not a volatility option; observing prices does not require paying for offsetting inventory.
Ordinary futures accounts net opposing same-contract orders; cross-account hedging is not a workaround here.

**Partly observed target:** at day-t close, day-t's move from O_t is already known. For independent equal-variance
zero-mean Gaussian returns X (known) and Y (future), predicting sign(X+Y) using sign(X) is analytically 75%
accurate while predicting sign(Y) stays 50%. This illustrative identity is not a market test or exact prediction
of authors' accuracy. It refutes treating approximately 71% old-anchor accuracy alone as evidence of profitable
future-return forecasting. A known-intraday-direction baseline and post-decision net P&L are required.

## Additional source consistency limits

- Cost tiers/PDF 45–46 imply 12–60bps per two-leg daily cycle. Table 15/PDF 64 instead deducts 8bps. Borrow costs
  are explicitly omitted. Execution/quantity/cashflow records are needed; do not replace all costs with a guessed fee.
- Table 3 labels 45 features, but its listed feature counts sum 47. Hyperparameter choices differ between Tables 4/5
  (for example XGBoost depth/learning rate and Random Forest estimator count). Exact code/settings are unavailable.
- PDF 67 claims 30% ML Sharpe exceeding 19, inconsistent with headline 7.26. Some figures and captions also differ.
- PSR/DSR/PSoR apply to the simulated outcome series; statistical significance cannot validate causal fills.
  Purged label maturity, fold-local scaling/selection and exact fit clocks also need audit before any ML replication.

## Disposition and account fit

Exact SSRN/title was not found in the checked local TIER_LIST/TODO/results search. Existing limit-entry,
missed-fill and cash/netting references are relevant; their old rejected trials remain preserved. A bounded
indexed title/GitHub-code search found no matching author implementation. It also surfaced a separate dual-buffer
follow-up; that source was not read and its existence does not certify this uploaded version.

This is an execution/evidence rejection, not an unchanged data-access blocker. Owned SPY daily and CME minute
prices cannot supply the future extrema at order time. No new acquisition loop, ML fit or market-return screen
was justified. The two-day rule is incompatible with ordinary weekday Apex intraday holdings as described;
no 50K/150K evaluation/funded strategy is admitted. Personal likewise fails execution eligibility. No BASE/ADD/
REPLACE/EMPTY, historical validation, native fills, Monte Carlo or independent economic verification occurred.

**No TODO candidate or allocation.** Deeper empirical investigation is unwarranted without a distinct causal
economic rule. Retain the audit in EXECUTION_REFERENCES E18 follow-up. No protective-order or live-system changes.
For Claude: `agents/codex/results/straddle_buffer_6401038_review_20261031.md`.
