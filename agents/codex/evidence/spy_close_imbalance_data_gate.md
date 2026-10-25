# SPY closing-imbalance data acceptance: no-return checklist

Date: 2026-10-25. Parent: `spy_close_imbalance.md` (NEEDS DATA).
This is an intake specification, not a return-test plan. No message sample has been obtained or parsed.

## Obtain / verify before accepting files

- Product must be NYSE **Arca** SPY closing-auction messages, not NYSE stocks, Nasdaq NOII, consolidated trades or a final imbalance.
- Ask for SPY-only/time-filtered research quote, sample, history start/end, ongoing licence and access. Confirm sample cost before accepting any paid service.
- Separate historical replay rights from real-time/non-display permissions and any exchange/vendor fees.
- Request original message schema versions, documentation of publication schedules, corrections, freeze/cancellation rules and historical changes.
- Ask whether files preserve each disseminated update or regenerate end-of-day summaries; request source timestamps and sequence fields, plus any capture/receipt timestamps.
- Verify auction-result prints and SPY/ES synchronized quotes can be sourced. A delivery file created next day is not automatically disqualifying if it preserves the original live dissemination sequence.

## File checks without future returns

1. Save originals read-only under a research input location with source/version/download timestamp and SHA256; do not archive credentials.
2. Parse dates, exchange zone/DST, sequence, symbol, message type, auction identifier, side enum, quantity units, reference price, indicative price and paired quantity. Retain distinct fields; never guess signed-field semantics.
3. Inventory sessions by year and schedule era. Report missing days, early closes, delayed/cancelled auctions, duplicate sequences, corrections, stale updates, missing fields and time reversals. Expected calendar must distinguish exchange closure from missing file.
4. Verify cancellations/revisions are applied when disseminated, never backfilled into earlier states. Keep final totals out of signal construction.
5. Reconstruct only messages available by each candidate observation; audit several sessions against vendor/exchange examples. Without receipt timestamps, label source-time reconstruction and specify a conservative simulated lag.
6. Count informative messages/events in design years, report zeros/sign changes and prior-volume warm-up coverage. No ES forward-return columns, plots, correlations or parameter ranking.
7. Audit quote freshness and matching clocks. One-minute futures bars cannot establish an executable intraminute quote.
8. Estimate a feasible observation window from documentation/coverage, not returns. Choose one signal definition and denominator based on field semantics; make all provisional choices visible.
9. Record missing- versus zero-imbalance handling and no-trade conditions. Do not silently carry an old day's imbalance.
10. Revisit budget, effective opportunity count and roster overlap. Do not label an event census a performance pass.

## Stop conditions

Keep NEEDS DATA if original messages, historical schedules, quotes or plausible latency cannot be verified.
Stop acquisition if only an unaffordable full-market package is offered; do not purchase automatically.
Nasdaq/QQQ data can motivate another evidence sheet for NQ after venue/schema/history/cost verification; it cannot silently fill missing SPY data.

## Transition to a future preregistration

Only after intake: freeze decision → receipt/latency → entry → stop → time exit; one primary direction; fixed cost and price-control model; design/validation periods; at most five variants including mandatory execution stresses; gross/net/statistical/placebo gates and hard stop.
No requirement is waived because the mechanism is scheduled.

