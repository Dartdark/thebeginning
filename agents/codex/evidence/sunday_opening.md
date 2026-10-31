# Sunday Opening: TEST — bounded source replication, no promotion claim

Summary: Uploaded NQ/MNQ 1-minute Central-time strategy buys Sunday evening after a nonpositive session-based week.
All default entry/exit/stop/target inputs are specified; the execution settings and parameter-search history are not.
Test the frozen defaults as a cheap design screen, separating historical close fills from next-open execution.
No measured forced demand is supplied; this is a calendar/weekly-reversal hypothesis, not established scheduled-flow alpha.
Return trials before this sheet: 0 for this upload; related Sunday/overnight families already tested.

Sources: supplied Sunday_Opening.txt (archived unchanged below); Claude source pin 92b1d4cde768bcfce019cf9a95944158dd0ebba3;
codex/work standing instruction agents/codex/USER_CODE_WORKFLOW.md read at aa726e23957224c1d3814b5328483abae5919838.
This evidence sheet precedes the return-test preregistration.

## 1. Participants and proposed mechanism
Sunday's 17:00 CT reopening resumes NQ price discovery after the weekend. Buying following a down week might capture recovery in thinner evening liquidity.
The code observes no auction order, hedge obligation or unexecuted demand; who must buy at 17:17 is unknown.
Its exact 17:17/19:12 clocks have no supplied economic derivation or development provenance. They are frozen, not searched.
TEST authorizes only falsification/replication of user-supplied rules, not presenting this as a newly verified forced-flow mechanism.

## 2. Direction, size and clock before entry
Long only, one contract in the upload. Compare the newest completed 17:00-anchored session close SC[0] with SC[5], allowing equality.
That is five observed-session intervals, normally Friday-to-Friday; holidays/missing sessions can change the calendar anchor.
At the first available Sunday bar close in 17:17–17:22 inclusive, buy if eligible; exit first available close at/after 19:12.
1-minute bars are close-stamped and dates assumed calendar dates in America/Chicago (DST aware).
Source close fills are a diagnostic. Primary executable proxy sends after the decision and enters next existing minute's open; time exit uses the next open after its threshold close.
Unconditional built-in stop/target exist: 80/50 NQ points, per contract. MNQ nominal stop $160, target $100 before costs/gaps; NQ $1,600/$1,000.
No claimed underlying dollar flow or hedge fraction is available; one MNQ size is a research unit, not a proposed live allocation.

## 3. Contract transmission
Trades NQ/MNQ directly. It is not the previously tested first-minute gap-direction push and does not require the missing first reopening print.
Nor is it the oil-specific Sunday up-gap fade.
Direct trading in the contract does not establish a directional cause.

## 4. Data and distinct information
Existing scratch_data/g24.pkl joins daytime/overnight NQ minute exports. Reuse without rebuilding.
Only completed-session prices and calendar/clock are inputs; no later-day return may determine eligibility.
Independent no-return inventory checks session resets, source SC comparisons, entry windows, exits and missing bars.
No tick/quote history or MC report is supplied, so exact fills, spreads and platform parity remain unresolved.
Freeze one-point target trade-through for screening; real platform settings must be confirmed before promotion.
Retain upload/hash and identify raw-grid/cache date coverage and observed-session dependencies.
No explicit rollover correction is in the code; report this as a limitation of the literal source. Any exposure spanning a known roll must be flagged, not silently retained.

## 5. Costs and gaps
Legacy full-NQ diagnostic: $7.25 RT + 1 tick per market/stop fill; targets no exit slippage.
Primary per-MNQ proxy: $1.04 RT + $0.50 per market/stop fill, with all outcomes also expressed per-NQ equivalent. Native fee is the latest recorded account convention, not derived by dividing NQ commission.
A $100 target and $160 stop need approximately 62.2% target wins if every other trade hits the stop under these costs; actual time exits/gaps change that arithmetic.
The window can overlap Overnight Tick/VIX and, from 19:00, Bridge Monday Long; do not call it an empty gap. The saved earlier occupancy map is not a current event-conditioned overlap audit.
All eligible events are screened regardless of whether the existing plan has a position.

## 6. Power
Five design years have roughly 260 Sundays; assuming half are down gives about 130 opportunities before missing data/warm-up.
With assumed per-NQ-equivalent SD $1,000, t≈2 requires net mean 2×1000/√130≈$175; a promotion-level t≈3.6 needs about $316.
These are planning assumptions, not observed counts or estimated returns. Session inventory establishes actual opportunities without candidate P&L.
The power is limited but not logically impossible with a $1,000 gross target. No timing or stop/target scan is authorized.
The no-return inventory subsequently found 112 down-week design opportunities and eight with incomplete entry-to-exit minute coverage, including March 2020 stress dates. These stay visible; do not delete them to improve results.

## 7. Prior work and falsifiers
Related: analysis/sunday_reopen_test.py, WATCHLIST #22; Bridge Monday Long; Overnight Tick/VIX; Overnight Rebound C; broad overnight/drift studies in TIER_LIST.
Novelty is the frozen down-week selection and short Sunday-evening holding/bracket, not a new independent flow family.
Reject the submitted configuration if its primary design net edge fails the preregistered gate, a delayed executable fill erases it, or the down-week filter fails its incremental test.
Failure does not authorize optimizing clocks, switching sides or promoting the unfiltered control.

## 8. Risk and diversification
Marketable entry/stop/time exits consume liquidity; target is passive and requires trade-through. No guaranteed closing fills or hard dollar stop bound across gaps.
Continuation of a weak week, weekend news, thin book and data gaps can cluster losses. Other NQ long strategies can lose simultaneously.
An offset later Monday cannot protect a Sunday breach; account chronology must be respected.
Start with one MNQ risk unit only in research. No live deployment. Data-stale or missing-window cases are explicitly counted; no historical backfilled entry after the six-minute source window.
If design passes, review actual 50K/150K evaluation/funded plus personal addition/replacement/empty-slot placement at integer sizes. If design fails, document the stopping condition separately for each destination.

## Decision
TEST for a committed bounded design screen, not live trading. Preserve source semantics and disclose next-open execution as a proxy.
No rank or plan change until independent review, platform confirmation and useful account contribution. No source settings are optimized.

