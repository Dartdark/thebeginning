# Monthly FOMC coefficient decomposition: DON'T TEST as a strategy

Summary: Source-only paper review; useful attribution and predictor-overlap diagnostics.
The paper reports stock-return covariance with later policy surprises, not executable ES/NQ strategy returns.
The proposed leap from predicting a surprise to earning a stock return remains untested.
Do not open a return screen until a separate, timestamp-safe trading hypothesis earns an evidence pass.

Source: Ahluwalia, SSRN 7674953, user-uploaded version; [review and provenance](../results/fomc_monthly_coefficients_review_20261029.md).
Return trials: **0**. No new strategy selected. Source results are not independent replications.

## 1. Who trades, and what forces or causes the trade?

Stocks and rate futures reprice policy and macro news. The paper does not identify a mandated participant,
net futures flow or delay that a small trader can systematically capture. Its causal interpretation remains conditional.

## 2. Direction, size and timing known before entry

No trade direction or flow size is supplied. Meeting and release dates can be known beforehand; the realized
surprise is available only after its measurement window. Completed release-day returns may forecast a later
surprise in-sample, but neither the forecast fit nor a profitable trade mapping is validated out of sample.
Any future design must state ET/CT with DST, receipt delay, decision time and first executable fill separately.

## 3. Does the flow reach the contract or its direct hedge?

The S&P 500 connects economically to ES/MES; the paper's nonfinancial-stock universe is not NQ.
Discount-rate and growth news transmit to both, but this does not establish net directional flow, incomplete
pricing after entry or a transferable per-contract profit. Dividend-sorted stock spreads are not index-futures trades.

## 4. New information and data feasibility

| Input | Source | Availability / current verification |
|---|---|---|
| Surprise labels / underlying rate changes | Paper's SF Fed workbook and event-study database references | Paper sample mainly 1988–2023; current files, vintages, Eurodollar/SOFR definitions and publication latency unverified here |
| Event/release calendar | Scheduled FOMC dates; paper uses ALFRED release vintages | Calendar knowledge differs from availability of numeric surprises; survey consensus is a separate input |
| Predictors / outcome prices | Completed stock returns and six orthogonalization predictors | Need fold-local fitting and exact measurement windows; original monthly predictors overlap some outcome returns |
| Stock-portfolio replication | CRSP, plus IBES for growth characterization | Not established as owned; licences/costs unchecked; futures OHLC is insufficient |

No dataset was newly acquired. Reference links are leads, not a completed availability audit.

## 5. Costs and actual intraday gaps

There is no executable gross-return estimate to compare with fees, spread, announcement slippage and latency.
FOMC and release minutes can have concentrated execution risk. No event-matched current occupancy calculation
was run, so no empty portfolio window or diversification improvement is claimed. Candidate events must not be
selected from zero-P&L dates or current plan flatness if a future screen becomes justified.

## 6. Power before a return test

The source's 256 monthly observations are not 256 independent 2018–22 trading opportunities.
About eight scheduled meetings annually implies roughly forty design-period events before exclusions; this is
a schedule-based planning approximation, not an audited event count. At effective count n, a t≈2 screen needs
net mean about 2 times event-return SD / sqrt(n), with costs added to obtain the gross hurdle. No event-return SD,
fixed horizon or plausible net mean is established here; power is **unresolved**, not passed.
More bars per meeting cannot fix the event count. A separate exact calendar/count and feasibility gate would be required.

## 7. Already tested and falsifiers

Pinned codex/work context: c8b35a5928f5026283759bc7ff74679f4106f0a0. TIER_LIST includes rejected
pre-FOMC drift, statement follow/fade and other FOMC branches; WATCHLIST #23 is the distinct liquidity-conditioned
short. This paper neither confirms nor overturns them. A future incremental hypothesis would fail if past-only
features cannot forecast the target beyond price/calendar baselines, or forecast improvements do not survive
execution costs in a fixed stock-return protocol. Do not use a future surprise to classify earlier trades.

## 8. Failure and diversification

| Question | Prediction / unresolved evidence |
|---|---|
| What stops the mechanism? | Full prior pricing, changing policy reaction functions, or news that moves growth and discount rates together; no forced-flow mechanism is established |
| Our liquidity role? | Unspecified; marketable event orders would face adverse selection and wider spreads, while passive orders face missed fills |
| How can losses cluster? | Macro regime shifts, false forecasts, announcement reversals, data delays and statement/press-conference disagreement |
| Which existing strategies share losses? | Potential common equity/macro exposure with VB, ONB, RS and NFP; not measured |
| Can an offset arrive before breach? | Unknown; annual correlation or a future meeting cannot protect an earlier account loss |

No stop, time exit or concurrent size is proposed because the candidate has not earned a TEST verdict.
No account-level protection, small-account suitability or personal-account profitability is inferred.

## Decision and next gate

**DON'T TEST as a ready strategy.** Keep the source review as a methodological reference.
If separately prioritized later, first audit the cited event labels and past-only predictors without returns,
then articulate a distinct, executable hypothesis and complete its power/cost gate. Only a new TEST evidence
sheet permits preregistration and a cheap 2018–22 screen. No automatic backtest or queue promotion follows.
