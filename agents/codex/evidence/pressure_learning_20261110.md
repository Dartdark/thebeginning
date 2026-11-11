# Causal pressure-state net-payoff forecasting: TEST, related-family extension

Summary: The first impact-residual/rejection model failed; do not tune or invert it.
Next question: can closed-bar pressure/fragility state forecast net small-target payoff for either direction?
Use monthly chronological fitting with mature historical labels, not ex-post jump labels or a forced fade.
Native design inputs and shared replay are available; quote/receipt/contract/microfill limitations remain.
Three additional frozen definitions; all3 first-batch failures and earlier pressure searches remain counted.

## Mechanism and distinction

The papers describe self-exciting activity, persistent flow and variable price response. Hypothesis: joint closed-bar
price/pressure/volatility state identifies asymmetric subsequent barrier payoffs after costs. No forced order, known
size or permanent premium is observed. This is a supervised conditional-response test, not an exact Hawkes/propagator
replication, and remains related to extensive failed flow/pattern research. Raw price/body forecasts are a mandatory control.

## Information and contract

Native NQ minute OHLC,total,buy,sell2018–22; complete5min bars, CTclose labels, nativehashes verified. Each observation's
ATR/volume normalization uses preceding data. Fit scalers on the training fold only. Train both directional counterfactual
net-R outcomes; each label matures only after the full30min horizon, including earlytargethits. No shuffled folds.
Models know no event's future endogenous/exogenous class, future day extrema, outcome or index membership at entry.

## Costs, risk and power

Shared delayedopen convention, entrybarstops, gaps,1pointtargetthrough, nativeMNQpriceproxyfees1.24RT+.50/marketstopfill.
Stop=.10priorATR tick-ceiled, target=.3stop tick-ceiled; oneposition,max4/day,30min,flat14:55. Hardstops can slip.
Training examples overlap; thousands of rows are not thousands of independent observations. Need>=100sessions and
10,000 mature valid side-label rows plus>=50 fullstop labels per side across>=30sessions. Actual designtrade gate>=250
over>=100sessions; desired significance must survive dailydependence/coststress. The screenshot's82% win rate is no guarantee.

## Failure and diversification

Any drift, permanent information, spread/impact or conditional-fit instability can destroy the edge. Crossing orders
consume liquidity. A learner can merely rediscover ordinary momentum/reversal and share VB/ONB losses. Evaluate eligible
events without incumbent-flat filtering. False positive forecasts are the principal falsifier; a high training score
does not count. Unknown execution paths remain unknown. Only after passing standalone validation: joint150Kcommonprice
BASE/ADD/REPLACE/EMPTY at frozen integer exposure with30calendar expiry, actualDLLliquidationcost and failuretiming.

Decision: **TEST** only under the separately committed protocol. Do not promote the pricecontrol, tune a failed hurdle,
reverse predictions, inspect recent returns early or claim a new independent factor. No live changes.
