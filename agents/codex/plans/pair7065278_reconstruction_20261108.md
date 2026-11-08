# Corrected TQQQ/LQQ3 reconstruction: component gate before returns

Summary: User's new “do it” authorizes a corrected reconstruction after the original source rejection.
Do not relabel it a source replication or erase the original failure. No original-source parameter sweep.
Evidence status remains NEEDS DATA; economic testing is not admitted.

## Frozen components and scope

Implement a research-only quote validator, explicit currency conversion and causal signal state machine.
This is not a broker adapter, full cash ledger or executable strategy. No order submission, network access,
historical return calculation or account simulation is included in the component script.

One provisional corrected definition: one daily decision at 15:00 UTC on sessions for which **both**
venues' calendars establish continuous trading. This is 15:00/16:00 London and 10:00/11:00 New York
in ordinary winter/summer, with US/UK transition weeks handled by zoneinfo. Half days and holidays
require actual calendars, not weekdays. Use last available bid/ask per security and FX with timestamps
and receipt times no later than decision; all ages <=60 seconds. No forward fill across missing sessions.
Different clock and execution make this a new adaptation, not exact reproduction.

Explicit units only: TQQQ USD; LQQ3 GBX (divide100) or GBP; GBPUSD USD per GBP. No level heuristic.
Use midquote ratio TQQQ/(LQQ3_GBP*GBPUSD). Twenty-observation EMA, adjust=False, and rolling sample
standard deviation (ddof=1), minimum20. Flat opens+1 below−0.75 or−1 above+0.75. A long exits
when z>=−0.25; a short exits when z<=+0.25, including overshoot; no same-decision reversal.
Zero/nonfinite dispersion and missing observations produce a visible rejection, never an implicit trade.
Emit desired direction only; require actual later quotes and two-leg execution before a position exists.

## Checks committed before execution

Fixed synthetic component groups: (1) preserve same-unit499/501 prices and equivalent GBP conversion;
(2) reject unknown units, nonpositive/nonfinite prices, crossed quotes; (3) reject future events/receipts,
receipts before events and quotes older than60seconds; (4) verify past-only indicator prefix invariance and
20-observation warm-up; (5) long/short entry, overshoot exit and no instant reversal; (6) zero-dispersion rejection;
(7) decision/local-clock fixtures and closed-calendar rejection. No synthetic profit claim.
Admission passes only if every assertion passes. Failures stop use of the component until an explicitly
identified engineering correction, never a performance-based repair. Record code/plan SHA and commit.

## Data and economic stop

Free-data receipts are retained under inputs/pair7065278_reconstruction_20261108. Yahoo probes for required
design-period hourly data hit proxy403. The previous Stooq download gate remains unresolved; do not bypass.
Owned TQQQ NAV data does not establish native synchronized quotes, and author405row workbook lacks raw
LQQ3/FX and provenance. Web discovery found daily adjusted stock pages and subscription intraday products,
not an admitted free paired quote archive. No histories downloaded from these leads.

Before economic trials: require native dated quotes/receipts, issuer/unit/corporate actions, both calendars,
2018–22 coverage plus warm-up, later fills, borrow and financing/commission/FX/collateral ledger. Fix integer
share sizing, cash, gross exposure, forced liquidation and matched baseline before committing a separate
economic protocol. Do not choose these from the source's later curve. This document does not reserve or
authorize historical return trials on later-only data. Stop at NEEDS DATA if these inputs are absent.

Economic trials0; one provisional signal definition, no economic comparison. Any future performance test
counts this new adaptation and its original-source selection history. No paid acquisition, scout/schedule,
trading-plan, TIER, live/VPS/broker change. Personal research only; no Apex plan fit as written.
