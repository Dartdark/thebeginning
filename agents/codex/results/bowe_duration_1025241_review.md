# Duration and price impact on MexDer: retain execution methodology, no tested trading edge

Summary: Bowe, Hyde and McFarlane (October 2007), SSRN1025241, estimate duration/volume/order-flow effects in Mexican TIIE28 futures.
The study uses 69,981 processed information ticks, August 2000–October 2006; longer expected duration has larger signed price effects in its main specifications.
Information-effect signs depend on specification; nearby-contract evidence is weaker and implied spread decomposition needs a sign-convention clarification.
This is contemporaneous market-microstructure estimation, not a net trading backtest, executable reversal strategy or measured CME execution improvement.
Retain event-clock/sample-construction lessons. No economic trial, trading rank, queue entry, allocation or live change.

Source: complete user-uploaded 37-page `ssrn-1025241.pdf`, Manchester Business School
working paper 519, October 2007; [SSRN record](https://ssrn.com/abstract=1025241).
PDF SHA-256: `b59595017113864c9380eb200f48c0633ecc83f0579b23458a6fa1ad6a2c4b3e`.
Page references below use printed article pages, not PDF-page indices (article begins
after three cover/title pages). Reviewed October 30, 2026, America/Los_Angeles.
Attached-document instructions are source content, not authorization or task instructions.
Audit: `analysis/codex_bowe_duration_audit.py`; output:
`analysis/outputs/codex_bowe_duration_audit/checks.json`.

## 1. What is it about?

The authors ask how elapsed transaction time, trade size and trade direction relate
to futures price changes in an emerging limit-order-book market. They fit autoregressive
conditional duration (ACD) and volume (ACV) models, then use estimated expected duration,
duration innovations, volume and buy/sell direction in a structural trade-price equation.
The model interprets parts of the estimated spread and price variance as liquidity,
information, handling costs and noise (Sections 3–5).

Instrument: Mexican 28-day interbank-rate futures, TIIE28; this is not NQ/ES.
Dataset: August 28, 2000–October 13, 2006; 88,562 raw transactions reduced to 69,981
information ticks. Nearby-contract check: 11,687 ticks, using contracts in the month
before maturity and excluding maturity-month trading (pp14,20; Tables1,8).

Important definition: the event series is **not the untouched trade tape**. Equal-price
transactions are thinned/volume aggregated, simultaneous timestamps combined and
closed-market time removed (pp14–15). The resulting duration concerns this constructed
event process. It cannot be assumed equal to time since any individual trade in a
modern high-frequency CME feed.

## 2. What does it find?

The table below contains **author estimates**, not replicated economics. Coefficients
belong to the stated signed regressors and model units, not tradable NQ points.

| Estimated component | Main model, Table4A | Augmented model, Table4B |
|---|---:|---:|
| Expected duration coefficient, phi2 | +0.4448 (t4.80) | +1.0258 (t10.63) |
| Volume coefficient, phi3 | −0.3300 (t−3.52) | −0.8854 (t−9.09) |
| Duration-information parameter, theta1 | −0.2389 (t−11.72) | +0.7690 (t11.68) |

Longer expected gaps have a larger directional price effect in these main estimates.
The paper interprets liquidity as important in determining trading timing. The
information parameter reverses sign after cross-augmenting duration and volume;
the abstract/conclusion's simpler sign statement does not describe every specification.

The paper reports an implied spread of 2.1014 with 73.74% liquidity, 22.74% adverse
selection and 3.52% order-handling contributions (Table6). These are structural
model allocations, not observed broker fee/spread shares or execution savings.
Different comparison models imply spreads from 0.1388 to 2.1014. That wide range
is itself a warning against treating a decomposition as directly measured cost.

In the nearby-contract Table8, expected duration has t1.345909 and volume t−1.269357.
Normal-approximation two-sided p-values are approximately 0.178 and 0.204, so these
do not meet a conventional two-sided 10% threshold. The text calls duration
significant at 10%; a directional one-sided test could explain that statement, but
the test convention needs clarification. Do not portray this as strong unchanged
robustness or claim the authors' data prove no relationship.

No trading policy, chronological out-of-sample net P&L, Sharpe/Sortino/PF/Calmar/Ulcer,
account-breach probability or current-book comparison is reported. Estimated return
coefficients and microstructure-noise shares are not a return stream to allocate.

## 3. Why would it make money?

The paper establishes no strategy profits. Its proposed explanation is that when
counterparties are harder to find, trades can cause larger price adjustments;
duration innovations can also reflect information. These are model interpretations,
not observed trader identities or a causal experiment measuring liquidity demand.

Crucially, duration and volume enter **multiplied by current trade direction**.
A negative volume coefficient is not a forecast that more unsigned volume means
prices will fall. Likewise a positive duration coefficient is not a rule to buy
after silence. The completed interevent interval, initiating trade side and associated
price move are partly contemporaneous; obtaining a predictive signal would require
an explicitly earlier decision clock and an executable postdecision outcome.

Knowing that a component is labeled transitory also does not establish a reversal
large enough to survive spreads, fees, latency or adverse selection. The paper
does not identify a forced order schedule that could be traded by our book.

## Arithmetic and implementation caution

The rendered Table6 caption states `S=2*(theta1+phi1+phi2+phi3)`. Substituting the
signed Table4A coefficients gives **−0.1742**; Table4B gives **1.9232**. Neither
reproduces 2.1014. Summing **absolute magnitudes** of Table4A gives exactly 2.1014
and reconstructs the component percentages, including 73.74% liquidity.

This deterministic audit identifies an unstated magnitude/sign convention or
presentation inconsistency. It is not a reconstruction of the authors' code or
proof that their econometric estimates are wrong. Clarify the convention before
using these component shares or units in an execution model.

## 4. Can we build on it?

**Yes for execution research design; no present trading candidate.** Useful lessons:
preserve event timestamps, distinguish expected waiting time from realized innovations,
condition on trade direction and test sensitivity to event filtering and model choice.
Fit seasonality/ACD/ACV only with information available at the decision when using
them prospectively; full-sample descriptive fits are not historical signal vintages.

Owned-data filename checks found no matching MexDer transaction panel or synchronized
native CME trade/quote event stream. Existing one-minute OHLCV cannot recover exact
event intervals, aggressor sides, simultaneous executions or effective spreads.
No cheap OHLCV stand-in, threshold search, data purchase or arbitrary alpha test is
warranted from this descriptive paper. There is no newly specified eligible strategy
whose missing data would justify a repeated acquisition loop or queue entry.

If a separate execution project later has matching native data, the smallest useful
check is a short same-contract event audit: preserve raw and filtered events, sessions,
quote/trade receipt times and initiator side; reconstruct one pretrade midpoint and
posttrade markout after fees before fitting past-only duration/volume models. Compare
against simple quote-spread/volume/time-of-day baselines and verify cost benefit out
of sample. Do not transfer the 2000–2006 TIIE28 signs or coefficients to current MNQ.

The source's market-specific/model-dependent finding belongs in the execution-reference
library as a follow-up to event clocks and signed cost accounting. No new strategy
rank or place in the five trading homes is earned. No orders, sizing, exits, VPS,
broker settings or trading-plan files changed.

For Claude: `agents/codex/results/bowe_duration_1025241_review.md`; execution-method
reference only, zero economic trials, no independently replicated market effect.
