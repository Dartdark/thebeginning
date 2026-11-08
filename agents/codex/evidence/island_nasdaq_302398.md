# Island/Nasdaq competition: DON'T TEST as a standalone NQ/ES strategy

Summary: Historical fine-grid undercutting illustrates market-design-dependent rents, not a current futures signal.
Source: [full review](../results/island_nasdaq_302398_review.md), Biais/Bisière/Spatt, November26,2003, SSRN302398.
Financial-return trials: zero. Source arithmetic/synthetic measurement checks only.

## Participant, obligation and transmission

Stock liquidity suppliers may improve a coarse external quote using a finer venue grid. No compulsory NQ/ES order or proven present-day retail access/priority advantage is identified. A market-design change compressed the historical opportunity rather than establishing its persistence today.

## Direction, size and clocks

No full entry/exit/inventory/size protocol. Source's thirty-minute midpoint is a postfill evaluation label, not pretrade information or an actual exit. Venue quotes, available-at/order clocks and matching rules must be synchronized.

## Data and implementation

Needs relevant native event books, unrounded competing quotes, order identities/queues, cancellation/partial/nonfill evidence and costs. Owned minute bars cannot reconstruct these. The upload supplies no original panel/replication code. No suitable new directional strategy merits broad data acquisition.

## Costs, power and previous evidence

Conditional marginal-order markouts differ from a whole-policy net ledger. Handling cost and rent are jointly identified; risk-neutral modelling omits inventory-risk costs. Short selected samples and model restrictions do not establish a modern edge. Existing failed passive-entry substitutions and flow studies remain closed.

## Risk and portfolio fit

Adverse selection, latency, stale quotes, queue loss and regime/rule changes can remove apparent spread capture. No measured loss offset, current-book diversification, executable risk or account-survival benefit established. No position or order type nominated for our accounts.

## Decision

Retain quote-precision and cost/markout lessons in E01/E56; no strategy/data queue entry, return preregistration, MultiCharts strategy or allocation. Later use only within a separately justified offline execution question with actual native records.
