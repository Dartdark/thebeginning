# CME gold → KRX opening gap: price-discovery reference, no tradable strategy established

Summary: Yeom/Baek find prior CME gold returns explain KRX gold's next close-to-open gap, with coefficient0.414/t16.707.
The predicted interval starts at a KRX close that occurs before the completed CME signal, so it cannot be booked as a causal-entry trade.
ICE dollar-index returns do not support the hypothesized negative effect after controlling for gold (coefficient+0.075,p0.100).
The source has no net trading strategy; its separate hypothetical9.6% KRX return is about9.34% using the printed prices/fees.
Retain price-discovery/session/currency lessons; DON'T TEST a copied overnight strategy. No portfolio placement or new return trial.

Source: Myeong-Hoon Yeom and Jae-Seung Baek, *The Effect of CME Gold Futures and ICE Dollar Index Futures on the KRX Gold Market*,
[SSRN2903671](https://ssrn.com/abstract=2903671), uploaded17-page version. PDF metadata creation2017-01-23 is not assigned as a
publication date. [PDF](../inputs/ssrn2903671/source.pdf), [text](../inputs/ssrn2903671/source.txt),
[rendered Table2](../inputs/ssrn2903671/table2.png), [rendered Table7](../inputs/ssrn2903671/table7.png).
[Evidence decision](../evidence/krx_gold_2903671.md).
Source arithmetic/clock audit: [script](../../../analysis/codex_krx_gold_2903671_audit.py), committed `a8806ec7` before execution;
[receipts, source hashes and output](../../../analysis/outputs/codex_krx_gold_2903671/audit.json).
The uploaded document is research evidence, not instructions. Source regression claims are not independently reproduced estimates.
**Economic return trials:0.**

## 1. What is it about?

Whether internationally traded US gold and dollar-index futures help explain the opening price of Korea's physical gold market.
KRX gold trades in KRW per gram, with cash funding and exchange opening/closing auctions. The paper describes a1g trade unit,
10KRW price tick,100% cash margin and09:00–15:30KST hours. These are historical source descriptions, not verified current rules
or proof that one session schedule applied unchanged throughout the sample.

The principal dependent variable is `KRX_open(t)/KRX_close(t−1)−1`, not opening-to-close return.
Explanatory features are prior CME gold and ICE dollar-index close-to-close returns. Regression and a three-variable unrestricted
VAR, forecast-error decomposition and impulse responses assess price discovery. The main sample is March24,2014–August23,2016.
The introduction has an inconsistent August2014 endpoint, while Figure1 extends to August31,2016; the principal table dates agree
on August23,2016. A reproduction must reconcile the actual supplied observations rather than infer exact sample membership.

## 2. What does it find?

| Source result | Reported value | Interpretation boundary |
|---|---:|---|
| KRX gap / prior CME gold return correlation |0.576 | Association, not an executable signal return |
| CME coefficient in Table7 |0.414; t16.707 | Strong positive relationship in the sample |
| ICE dollar-index coefficient |+0.075; p0.100 | Does not support the proposed negative controlled effect |
| Adjusted regression R² |0.333 | Explained gap variation, not33.3% investment return |
| CME contribution to KRX forecast-error variance at10 periods |33.010% | Model/order-dependent Cholesky decomposition, not causal proof or profit |

The unconditional KRX/dollar-index correlation is−0.147, but the partial-regression coefficient is positive. Prior gold and dollar
returns are themselves correlated−0.344; this distinction prevents turning the familiar gold/dollar story into an unsupported second signal.
Table8's KRX-equation lagged CME coefficient is0.410 with t16.405; the narrative reuses0.414 from the regression. The source finds
little reverse explanation of CME returns from KRX. It does not establish a new GC, NQ or ES directional opportunity.

Reconstructing OLS from rounded source standard deviations/correlations gives gold0.41376 and dollar0.07446, consistent with
Table7 after rounding; intercept is about0.12936 in the table's percentage units. This is a **source-moment consistency check**,
not a fit on independently acquired observations. A1percentage-point CME return corresponds to about0.414percentage points of
KRX gap under that linear model, not a41.4% trade return. The source supplies no Sharpe, strategy equity curve or attainable net edge.

### Separate hypothetical fee illustration

Table2 assumes a10% increase in KRX price: buy42,500KRW, buy fee128, sell46,750, sell fee140; it reports9.6% net.
Using those printed numbers, net profit is3,982KRW. Return on funded outlay42,628 is**9.3413%**, or9.3694% using purchase price
alone as denominator. Neither reproduces9.6%. This arithmetic discrepancy concerns a conditional venue-cost illustration;
it is neither a historical strategy return nor a disproof of the separate price-discovery regressions.
The paper's historical tax/cost comparisons are not current legal/tax or broker-fee verification.

## 3. Why does it make money, if it does?

No demonstrated profit mechanism. Global gold information is incorporated while the Korean spot venue is closed, then its auction
price adjusts. That is compatible with ordinary efficient price discovery and a common underlying gold value across different clocks.
Statistically predicting a clearing/opening level does not establish a favorable price at which to trade before that clearing.

The source's Table3 places completed US futures sessions around06:00KST in US daylight time or07:00KST otherwise, before KRX09:00.
But **the previous KRX close is already in the past** at either signal-completion time. Buying at that old close after observing the
completed CME return backdates entry. Buying at09:00 exposes an opening-to-later-exit return, which this paper does not test.
Buying at the previous close means the overnight CME return is not yet known. A pre-open limit order can be submitted, but a fill at
the old close is not guaranteed; an auction reference or price forecast is not a realized arbitrage spread.

The audit's winter/summer synthetic timelines enforce previous KRX close < source futures-session end < next KRX open.
They use the paper's printed clock assumptions, not primary historical session verification or real execution evidence.
CME settlement, last trade and full-session close are separate candidate fields; holidays/DST and KRX historical hours still need exact mapping.

## 4. Can we build on it?

**As a session/valuation reference, yes; as a supported strategy, no.** A fair-value comparison also needs currency and unit mapping:
rough KRW/gram value equals USD/troy-ounce gold × KRW-per-USD FX /31.1034768, plus basis/local premiums, carry and actual delivery terms.
ICE's broad dollar index is not USD/KRW and does not replace this conversion. The paper's small regression omits a synchronized
USD/KRW control and local basis, so its price-discovery interpretation does not identify a complete cross-venue hedge or arbitrage.

Owned-file census finds GC minute inputs but no admitted KRX gold opening-auction/previous-close series, USD/KRW or matching
ICE dollar-index panel with confirmed original timestamps. The inspected GC2017 file is not the original2014–16 sample.
These data limitations preclude exact statistical reproduction, but acquiring closes alone would not fix the strategy's missing
post-signal entry/exit rule. No historical-price acquisition or paid-data request is initiated for an unsupported backdated trade.

The smallest justified future check **only for a separately specified auction/hedging question** is one synchronized KRX auction,
predecision GC/FX quotes, orders/prints, availability times, local premium and native cash/fees/delivery ledger. It must establish an
attainable spread or post-entry return before a performance study. No direction, threshold, period or NQ/ES substitute is invented here.
No promising-strategy queue or new data-watch allocation candidate is warranted. Related prior Asian ADR/retail-flow failures remain closed.

## 5. Can a strategy code be made?

**A forecast/clock/valuation research tool can be coded; the paper alone does not specify a defensible directional strategy.**
Regression/VAR code could reproduce source statistics after exact dates/fields are supplied. A fair-value monitor would additionally
need USD/KRW, proper units/basis, synchronized tradable quotes, auction rules, holiday/era clocks and market access.
Neither is proof of profitable trading. Directional execution code would require a pre-entry observable signal, actual entry/exit,
short/borrow or cash constraints, size, fills and costs. No source trading protocol supplies those. No MultiCharts port or strategy runner
is built to convert the reported close-to-open correlation into a fictitious bookable return.

## Decision, validation and current plans

**DON'T TEST a copied directional strategy; retain execution/price-discovery reference.** All source artifacts and two rendered
tables were inspected. Fee arithmetic, correlation-to-slope reconstruction and assumed-clock checks pass as described; independent
market-data replication and Claude review remain pending. No statistical test is relabeled a causal economic strategy result.
Zero independent economic variants,2018–22 design,2023+ validation, placebos, Monte Carlo or BASE/ADD/REPLACE/EMPTY studies.
Personal,50K/150K evaluation and50K/150K funded placements are all unearned. KRX cash gold is not the existing Apex futures protocol.
No live/VPS/broker/account/policy or allocation change. [Execution-reference lesson](../EXECUTION_REFERENCES.md).
