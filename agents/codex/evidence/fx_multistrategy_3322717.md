# FX multi-strategy, SSRN 3322717: NEEDS DATA / SOURCE CLARIFICATION

Summary: The author reports improved portfolio Sharpe from FX carry/trend diversification.
The uploaded source has inconsistent optimizer attribution and insufficiently specified pruning/execution rules.
Only one of the eight FX futures is owned. No source-faithful return test is currently defined.
Personal research only; daily flattening would change the source strategy. Return trials: zero.

Source: January 25, 2019 uploaded PDF, retained under `agents/codex/inputs/fx_multistrategy_3322717/`.
Detailed source/page references, audit and search receipts: [review](../results/fx_multistrategy_3322717.md).

## 1. Who trades and why?

The proposed mechanisms are carry risk compensation, price persistence/reversal and macro linkages.
No forced participant, deadline or order obligation is estimated. No identified intraday flow edge.

## 2. Ex-ante direction, size and timing

Expanding percentile ranks determine signed risk budgets; daily inputs and monthly allocation rebalance.
Publication/availability and executable fill clocks are unspecified; cross-country closes are asynchronous.
The source does not estimate predictable dollar demand relative to futures volume. Missing clocks block replication.

## 3. Transmission

The source trades eight FX futures directly; no demonstrated signal transmission to NQ/ES or micros.
A macro correlation does not justify moving the source rule onto an index future.

## 4. Independent information and data

Yield gaps are the incremental non-price input. Need dated domestic/US one- and ten-year yields, eight FX futures
with contract IDs/rolls, linked local equity histories and the exact commodity series/definitions.
Only 6E is in the owned FX panel; inspected US-rate and NDX/GLD files do not complete the source universe.
No complete point-in-time panel or author code was verified in bounded GitHub searches. Costs/licensing unknown.
Selection/pruning dates, indicator signs, negative-yield handling and solver constraints also require clarification.

## 5. Costs and intraday gaps

No executable gross-to-net bridge, native contract/roll fees or turnover decomposition. No source intraday exit.
Existing NQ plan occupancy is not relevant to a persistent FX sleeve; no event selection based on book flatness.
Cannot compare a source intraday expected move to costs because the source supplies no such trade.

## 6. Power

No executable opportunity inventory or per-trade SD is defined. Daily observations of overlapping slow positions
are not independent trades. Do not manufacture a t-stat or power estimate from the author's aggregate Sharpe.
After source/data clarification, count independent design-period holding/rebalance blocks before preregistration.

## 7. Already tested and falsifiers

Exact SSRN/title/author searches found no prior exact review in the local tier/watchlist/queue/reference files.
Carry/trend diversification is a broader existing research family; this is not a newly established market effect.
A later test must keep pruning training-only, benchmark simple risk/equal weights, include native costs and USD
exposure controls, and stop if a frozen design fails. This sheet does not register such a return test.

## 8. Failure and diversification

Carry unwinds, USD concentration, trend reversals, illiquidity and rolling costs can create shared losses.
Liquidity role cannot be specified without source execution rules. Cross-market diversification and protective
effect relative to the personal book are unmeasured. Annual volatility targeting does not cap intraday losses;
an offset arriving later would not undo an Apex floor breach. No stop/holding protocol is invented here.

## Next gate

**NEEDS DATA / SOURCE CLARIFICATION**: resolve author method/pruning/clock ambiguities and reconcile one
dated formation/rebalance/roll month before any bounded return preregistration. No Apex placement as written.
