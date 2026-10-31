# Bitcoin spot/inverse-futures allocation: NEEDS DATA AND SPECIFICATION

Summary: SSRN3441913 derives executable-looking continuous controls, but does not establish a native net-cost strategy.
Source Sharpe4.86–5.07 versus spot4.40 comes from111 rally days, not our validation or account replay.
Main formula/payoff checks pass; AppendixB.2 has a confirmed sign discrepancy. Matching contracts/spot clocks and collateral are unverified.
Public BitMEX acquisition probes hit network proxy403. Do not replace inverse contracts with owned CME futures.
[Full review and five answers](../results/bitcoin_inverse_3441913_review.md); zero economic trials.

Source: Deng/Pan/Zhang/Zou, August23,2019 uploaded31-page PDF. Source/script hashes, actual owned schemas,
coefficients and probes: [audit](../../../analysis/outputs/codex_bitcoin_inverse_3441913_audit/audit.json).

## 1. Participant and reason for trading

A utility-maximizing investor allocates to estimated spot/futures risk premia. No dated forced institutional flow or
outside trader's obligation creates a demonstrated price concession. This is a portfolio-allocation hypothesis, not basis arbitrage.

## 2. Direction, size and timing before entry

The source calibrates December17,2018–March14,2019 before March15–July4 evaluation. Parameters include drifting prices and covariance.
Main calibrated controls are long spot and long futures; inverse describes BTC settlement, not direction.
Continuous controls have no discrete available_at/decision/fill clocks, confirmed native integer quantities or execution delays.
Rebalancing and parameter-refit protocol must be frozen; subsequent correlations cannot be used at an earlier decision.

## 3. Transmission and account relevance

BTC spot/BitMEX inverse, not NQ/ES or a CME contract payoff. Multiday continuous exposure cannot establish an Apex intraday slot.
Personal account only as conditional research; native collateral/mark/liquidation and regulated access/terms remain to be established.

## 4. Inputs and data feasibility

| Input | Verified status | Missing information |
|---|---|---|
| Source PDF and formulas | Full31-page upload; rendered main/appendix coefficients compared | Actual source strategy implementation and sign used in Table2 |
| Source paired contracts | Not confirmed; XBTM19/XBTU19 metadata probes blocked | Exact IDs, listing/expiry, price fields, daily timestamps and warm-up |
| Source spot/index | .BXBT candidate probe blocked | Exact series and separately executable spot venue/quotes |
| Owned CME BTC and Coinbase spot | Actual OHLCV headers inspected | These are not source inverse contract/index series |
| Collateral, native costs, marks and conversion | No matched ledger acquired | BTC fees/margin, liquidation timing, spot conversion/borrowing and rebalancing |

Four public probes returned tunnel403; receipts saved. No authentication, purchase or proxy instrument was used.
No full license/provenance/fill claim follows from an API URL.

## 5. Costs and account gaps

Source model omits transaction-cost/mark-margin constraints; its contract table listing margin percentages does not implement them.
Continuous rebalancing turnover is not free. Native inverse gains are in BTC and USD conversion has its own timing/fees.
No complete gross-to-net trade ledger, breakeven cost, intraday held-minute map or account overlap can be established yet.

## 6. Power before a return test

Source87 calibration/111 evaluation daily observations do not supply independent completed trades or a2018–22 census.
No observed strategy SD/net mean/t-power estimate available. Small rally sample and covariance estimation limit inference;
100 independent completed positions are not established by111 daily wealth marks.

## 7. Previous tests and falsifiers

No exact-source result found in ranked/watch/queue records on intake. Prior BTC reopen, seasonality, momentum and forced-flow
failures are distinct and not revived. Main coefficient matches matrix solution; printed AppendixB.2 coefficient does not.
A future reproduction must fail closed on unidentified contracts, impossible availability, nonpositive prices/singular covariance,
unreconciled BTC/USD cashflows or ignored liquidation. No parameter search is authorized to repair a failed reproduction.

## 8. Failure, liquidity and diversification

Drift/covariance instability, continuous-to-discrete error, funding for any separate perpetual adaptation, BTC collateral exposure,
margin liquidation, exchange/spot venue failure, fees and jumps can invalidate source optimality. Near-collinearity can amplify
allocation estimates. An inverse future is not a downside hedge merely because of its name; calibrated exposures are both long.
Source order types, stops, time exits and max concurrent exposure are unspecified. No pre-breach offset to existing plans established.
No Gaussian utility/control solution supplies actual account survival probabilities.

## Decision and next gate

**NEEDS MATCHING DATA AND SPECIFICATION.** Retain conditional personal research in TODO and currency/accounting lesson in E09.
With new matching inputs, reconcile one identified native contract interval and execution/availability clock without returns;
then complete coverage/cost/power gates and commit a bounded causal protocol before any economic trial.
No performance simulation, current allocation, BASE/ADD/REPLACE/EMPTY or Apex benchmark is earned now.


## User-requested code build completed

[Offline strategy implementation](../results/bitcoin_inverse_3441913_build.md) now implements both utility controls,
native lots, reciprocal position accounting and a hypothetical BTC/USD funding/cost bridge.20 behavioral tests pass.
User explicitly authorized this review build while the return-data gate remains. Pooled-wallet/discrete execution
assumptions are documented; no broker adapter or empirical trials. Status remains NEEDS DATA AND SPECIFICATION for returns.
