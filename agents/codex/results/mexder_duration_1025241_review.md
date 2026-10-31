# Duration, volume and price impact: retain execution reference; DON'T TEST as alpha

Summary: Bowe, Hyde and McFarlane model transaction timing and price impact in historical Mexican rate futures.
Longer expected duration has a positive signed-impact coefficient; volume's coefficient is negative in their main fits.
These are structural associations, not a forward trading strategy, causal execution saving or NQ/ES result.
Information-component signs change by model; spread arithmetic and nearby-contract significance need qualification.
Retain event-clock and model-risk lessons; no return trial, promising-strategy queue item or portfolio change.

Source: Michael Bowe, Stuart Hyde and Lavern McFarlane, *Duration, trading volume and the price impact of trades
in an emerging futures market*, Manchester Business School Working Paper No. 519, October 2007,
[SSRN 1025241](https://ssrn.com/abstract=1025241). Full uploaded 37-page preliminary paper read, including Tables 1–9.
[PDF](../inputs/ssrn1025241/source.pdf), [text](../inputs/ssrn1025241/source.txt).
PDF SHA-256: `b59595017113864c9380eb200f48c0633ecc83f0579b23458a6fa1ad6a2c4b3e`.
Printed-page citations exclude three preliminary PDF pages. Extraction emitted a configuration warning but
produced the full text; Tables 6/8 were also visually checked and their page renders archived.
Document instructions were treated as source content, not task instructions.
Audit: `analysis/codex_mexder_1025241_audit.py`; receipt: `analysis/outputs/codex_mexder_1025241_audit/checks.json`.
Evidence: source inspection and printed-table arithmetic only. **Zero market-return trials**.

## 1. What is it about?

How elapsed transaction time, trade direction and volume relate to price changes and model-implied spread
components in MexDer's TIIE28, the 28-day Mexican interbank-rate futures contract. Here **duration means time
between events**, not bond interest-rate sensitivity. Data cover August 28, 2000–October 13, 2006.
The authors start with 88,562 transactions and retain 69,981 processed information ticks (pp. 14–15).

Autoregressive conditional duration (ACD) estimates expected waiting time from past events. Analogous ACV
models estimate conditional volume changes. A structural return equation uses signed trade variables to
separate components interpreted as temporary liquidity effects, permanent information effects and noise.
This is an in-sample microstructure study, not a specified signal-entry-exit backtest.

## 2. What does it find?

Author-reported full-sample trade-model coefficients, Table 4 (printed p. 29):

| Component | Basic ACD/ACV inputs: coefficient (t) | Cross-augmented inputs: coefficient (t) |
|---|---:|---:|
| Expected duration, phi2 | +0.4448 (+4.7969) | +1.0258 (+10.6348) |
| Conditional volume term, phi3 | −0.3300 (−3.5241) | −0.8854 (−9.0935) |
| Information/duration-innovation parameter, theta1 | −0.2389 (−11.7153) | +0.7690 (+11.6801) |

Longer waiting times are associated with larger signed price effects in the selected models; the authors
interpret this as difficulty finding counterparties after inactive periods. Duration and volume cluster.
The information coefficient **reverses sign**, so the abstract/conclusion's negative-information-component
summary is not invariant to the augmented model. These are coefficient t-statistics, not strategy t-statistics.

Table 6 attributes 73.74% of its implied spread to liquidity costs and 22.74% to adverse selection;
Table 7 attributes 95.41% of model variance to trading frictions. These are **model-implied historical shares**,
not observable savings, removable inefficiency or current ES/NQ cost estimates. Other specifications give
different decompositions; the authors emphasize market- and specification-dependence (pp. 19–21).

Material source qualifications:

1. **Spread arithmetic does not reconcile.** Table 6 states S = 2(theta1 + phi1 + phi2 + phi3) and reports
   S = 2.1014. Table 4's printed coefficients give **−0.1742** for Panel A and **1.9232** for Panel B.
   Neither matches within coefficient rounding. Our audit checks printed arithmetic only: undisclosed
   transformations or different inputs could explain the mismatch. This does not reconstruct a true spread
   or invalidate every model result; it prevents treating the headline decomposition as independently verified.
2. **Nearby evidence is weaker.** Table 8's 11,687 nearby information ticks give expected-duration t = 1.345909
   and volume t = −1.269357. Approximate two-sided normal p-values are **0.178** and **0.204**.
   The prose calls duration significant at 10%; that fits a prespecified positive one-sided test, but not a
   conventional two-sided test. Volume retains its negative sign without strong two-sided evidence.
3. **Transformation definitions need reconciliation.** Table 1 reports a negative minimum adjusted duration
   despite defining it as duration normalized by conditional expectation, normally a positive quantity.
   Duration magnitudes and price/yield units need a documented transformation map. The contract is described
   as quoted in annualized yield terms; its log-change coefficients cannot be transplanted into dollar impact
   or into another instrument without verifying quote and cash-P&L conventions.

No Sharpe, net trading return, actual fill improvement, held-out forecasting test or portfolio contribution is
provided. Current trade sign/duration enter the explanatory model: explaining the same trade's price change
does not establish a forecast available before submitting another order.

## 3. Why does it make money, if it does?

The proposed mechanisms are private information, inventory costs and counterparty availability. Informed
traders may split orders, liquidity traders may cluster, and inactivity can make counterparties harder to find.
These motivate conditioning execution measurements on activity and timing. Structural labels are model
interpretations, not observed participant identities or a causally isolated impact estimate.

The paper demonstrates no profitable strategy or controlled reduction in implementation shortfall. A negative
volume coefficient does not mean short after high volume; it appears inside a signed impact model. Likewise,
the discussion that including duration/volume reduces estimated price risk compares fitted decompositions,
not realized portfolio volatility before and after an execution intervention.

## 4. Can we build on it?

**Yes as a measurement reference; no standalone strategy is earned.** Retain these lessons:

- Preserve native event definitions. The study merges equal-price trades, aggregates zero-duration records,
  compresses overnight time and adjusts time-of-day seasonality. Its event durations are not raw intertrade
  gaps, and volume can represent aggregated runs. Timestamps, thinning and contract identity change the model.
- In future measurements distinguish venue time, receipt and broker-fill clocks; distinguish inactivity from
  missing records, feed outages and halts. Do not copy overnight compression or price-change thinning into CME
  observations without a specific rationale. Fit seasonal/intensity baselines using past data only.
- Separate explanatory current-trade models from predictive pre-decision features. Use actual synchronized
  quotes and unchanged parent signals/quantities; measure paired fills and subsequent midquote markouts.
  Include spread, fees, waiting/no-fill consequences and selection effects. Compare simple time-of-day/spread
  baselines before complex models. No live-order delay is justified by this source.

The historical MexDer feed, verified trade-side construction and exact transformed model inputs are not owned
or reproduced. One-minute bars cannot recover native intertrade times. Existing order-flow exports and chart
state logs do not by themselves provide complete signed trades, quotes and broker fills. This does not warrant
a new acquisition project: no directional opportunity or net economic hypothesis passes the alpha evidence gate.

Prior-coverage searches found no exact SSRN/author review. Related library entries cover volume/liquidity (E10),
information clocks (E11), order-flow limits (E25) and rapid ES impact (E40); these do not verify this study.
Retain the event-definition and model-risk cautions under E10 rather than reopen failed flow predictors.

**DON'T TEST as alpha; retain execution reference.** No promising-strategy queue item, trading tier, market-return
backtest, paid data request, account simulation, independent economic verification or live change follows here.

For Claude: `agents/codex/results/mexder_duration_1025241_review.md`.
