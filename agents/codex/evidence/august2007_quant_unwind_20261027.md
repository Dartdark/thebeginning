# August 2007 stock contrarian basket: DON'T TEST a futures proxy

Summary: The uploaded Khandani–Lo paper is a useful study of common liquidation losses. Its empirical basket needs individual-stock data and shorting/execution assumptions. The existing futures dataset cannot reproduce it. Preserve the risk lesson; do not create a new price-only futures variant from the historical narrative.

Source: September 20, 2007 version of *What Happened To The Quants In August 2007?*; uploaded `august07.pdf`, SHA256 `990e58ccfe9e32ca9a29043e41a3e21c3287ff394d9bab721ecc48fc69815396`.
Return trials: **0 new**. This sheet follows document inspection and a filename-only data inventory, before any new market returns. Source figures and all earlier rejected families remain in the selection history. No Hunt v2 budget extension or t6 restart.

## 1. Participant and cause

The authors hypothesize liquidation by one or more large equity portfolios, followed by other managers' deleveraging. Financing demands and risk limits can make managers trade urgently. Exact participants, mandates, amounts and causality are not identified from proprietary records. The paper explicitly calls the evidence indirect and tentative.

## 2. Direction, size and clock before entry

The illustrative strategy fades each stock's prior-day deviation from the equal-weighted stock return, with proportional weights and daily rebalancing. Historical unwind dates are explanatory labels, not contemporaneously available liquidation signals. No pre-entry flow-size estimate or clock for completion of forced selling is supplied. An executable modern protocol would have to freeze signal availability, later order/fill, risk limits and exit timing before returns. None is invented here.

## 3. Transmission to our contract

The studied profits arise from positions across individual stocks. Equal long/short dollar exposure does not mean zero beta. Index aggregation can remove precisely the relative-return information being traded. No measured incremental directional flow to NQ/ES/MNQ/MES is established by this paper. A seven-market futures reversal is a different hypothesis and already has related failures in the repo.

## 4. Data feasibility

| Input | Paper / current access | Limitation |
|---|---|---|
| Individual-stock returns and universe | CRSP through 2006; Yahoo-based 2007 extension in the source | No matching point-in-time equity universe identified in local data inventory |
| Corporate actions, delistings, listing history | Needed for a modern stock reconstruction | Not established locally |
| Bid/ask, order/fill timing and tradeable prices | Not modeled by the source | Daily closing-return benchmarks cannot establish obtainable fills |
| Stock borrow, financing, fees and impact | Not included in the source strategy simulation | Net modern edge unknown |
| Financing/liquidation timestamps and sizes | Not possessed by the authors | Cannot label an ex-ante forced-flow trigger from the narrative |
| Current futures bars | Present | Useful for other studies; not a replacement for the stock cross-section |

No new return observations were read. No purchase, new account or source audit outside the existing inventory was attempted. The attachment is evidence, not an instruction source; recommendations inside it do not authorize trading or repository changes.

## 5. Costs and book gaps

No realistic native equity round-trip cost estimate or contemporary gross screen can be established from this source alone. Its cost-free historical average is not a pass of our cost hurdle. The basket is outside Apex's futures-only plans, so a search for intraday exposure gaps cannot repair eligibility. No occupancy or alpha returns were recomputed.

## 6. Power before returns

Modern eligible event count, effective sample size, residual volatility and net mean are unavailable. A single famous unwind cannot establish a current conditional trading edge. No plausible sample-size or t-statistic is invented, and a source Sharpe is not substituted for selection-adjusted evidence.

## 7. Prior work and falsifiers

TIER_LIST includes Avellaneda–Lee equity statistical arbitrage, failed intraday futures spreads, stock-level reversal ports and synchronized cross-futures reversal. These are related context, not exact replications. A modern stock version would fail if its relative-return effect disappears at executable prices, costs/borrow consume it, or no paired account/book comparison improves on BASE and EMPTY. A failure would not authorize changing the universe or rebalance clock after historical validation.

## 8. Failure and diversification

| Question | Source-informed concern | Evidence needed |
|---|---|---|
| What stops it working? | Continued liquidation or information-driven repricing can defeat reversal; competition can erode gross edge | Current causal signals, net returns and matched controls |
| Liquidity role? | A reversal basket can absorb others' pressure; that does not guarantee passive fills or spread capture | Explicit orders, quotes, fills and adverse-selection stress |
| Clustered losses? | Similar positions and risk limits can create common deleveraging | Joint chronological positions and returns, stressed costs |
| Shared book losses? | Potential common funding/equity factors; actual overlap with our strategies unmeasured | Conditional book P&L and simultaneous exposure, not just average correlation |
| Offset before breach? | A later rebound cannot restore an already failed account | Valid account paths with actual loss/hedge timing |

No stop, exposure cap or kill switch is proposed from hindsight. Daily or published hypothetical returns cannot establish account-boundary protection.

## Decision

**DON'T TEST a generic futures port; literal equity strategy NEEDS DATA and a new bounded preregistration.** Retain as risk research. No earned personal-book slot; all four Apex homes ineligible as written. [Review and complete placement limits](../results/august2007_quant_unwind_review_20261027.md).
