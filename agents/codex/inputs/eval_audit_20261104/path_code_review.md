# Independent path-builder review — 2026-11-04

Summary: Code-only review before the evaluation experiment preregistration; no historical market path or account outcome was computed.
The builder's synthetic selftest and a separate builder-to-engine same-phase roundtrip fixture passed.
Shared-price netting, Sunday exposure, missing-price propagation and segment indexing were reviewed.
The reported clock, uncertainty, source-bar risk and input-registration defects were corrected before sizing outcomes.
This is an engineering review, not independent verification of strategy profitability or broker execution.

Reviewer: independent child agent `eval_path_builder/path_code_review`.
Scope: `analysis/codex_eval_paths_20261104.py`, its interface to
`analysis/codex_eval_engine_20261104.py`, and a bounded read-only review of
`analysis/codex_eval_extra_ledgers_20261104.py`.

## Findings and resolution status

1. **Fractional cross-asset source events previously created phantom backtracks. Fixed and inspected.**
   The earlier implementation reset another asset to its preceding integer OHLC endpoint at each
   fractional source-fill insertion. The current implementation retains each asset's most recent point
   within that minute and advances all assets at integer phases. This fixes an unintended zigzag.
   The builder's added two-asset fixture passed: a later asset-A exit leaves asset B at its earlier106
   insertion, rather than resetting it to110. No quote is carried into a missing raw minute.

2. **An entry and its own same-phase exit could previously leave a phantom holding. Fixed and inspected.**
   The builder now places that exit on a duplicate, identical-price/time node after the entry.
   The engine preparer also explicitly orders already-active exits before new entries, and an entry
   before its own same-row exit. A separate synthetic integration opened and closed one MNQ at101
   on Sunday19:00, with $0.62/side commission and0.25-point market slippage. It charged both fills,
   ended flat, and produced the arithmetic check balance $49,997.76 from $50,000. This is a fabricated
   engineering fixture, not a strategy result.

3. **Incompatible within-minute exit order must become an unknown price. Fixed and inspected.**
   In the reviewed `assemble()` branch, an otherwise matched open-time exit earlier than its own
   entry was flagged `hard_unknown`, but the event's `matched` boolean remained true while its phase
   was moved later. This could inject an impossible fill at an arbitrary later point. The implementation
   owner now sets `xgood=False` for every branch that declares incompatible ordering.
   A quality-table warning alone must not grant a fill to the account engine. In the final code,
   an unmatched source order carries a NaN raw fill rather than overwriting a valid shared quote.

4. **Known open/close clocks must not be moved to an arbitrary matching touch. Fixed and inspected.**
   The bounded extra-ledger review found `_infer()` falling back to the first matching minute in a
   chart candle after a known market-open/close price mismatch. A pure synthetic example with a10:00
   close order, source price100, native10:00close101 and earlier09:57high/low101/99 returned09:57.
   A10:00decision cannot be executed three minutes early. The adapter owner was asked to preserve
   the declared open/close timestamp and phase with a failed-match flag; the corrected implementation
   does so and its new synthetic regression passes. Only genuine resting stop/limit orders may search
   for an intrabar touch. No historical source was run in this check.
   A subsequent edge fix also keeps the original bar-open clock when a resting-order search lower
   bound is later than that open. The lower bound no longer moves a known market-open timestamp.

5. **Partial source timestamps cannot certify full account-day no-signal coverage. Fixed and inspected.**
   `_sampling_bounds()` now requires explicit certified full account dates as `YYYY-MM-DD`, rejecting
   a datetime such as `2026-07-07 04:45`. The declared dates must still be justified against exact
   source settings. A date-only string is an assertion to verify, not evidence by itself. Last trade
   date is never an adequate source sampling end. OT must not be zero-extended beyond its coverage.

6. **Metadata/empty-file and price-validation issues. Fixed and inspected.**
   Empty `quality.csv` has explicit columns. Malformed OHLC becomes all-NaN for that asset/minute.
   Crossing phases are clamped within their declared range after numeric tolerance checks. Entry
   fill-kind values are validated and passed to the engine. Stop metadata reflects configured
   overrides, and no-source-stop infinity is serialized separately from an unresolved nonfinite risk.

7. **Source chart compression affects calendar-date ATR and integer risk sizing. Fixed and inspected.**
   ONB30/ONBML source reports use15-minute charts; LDF/MON/NFP use5-minute charts. The chart candle
   closing at00:00 includes prior-date minutes, so the source's calendar-date ATR cannot in general be
   replaced by civil one-minute-date ATR with an assertion of exact parity. The bounded VCS adapter
   already reconstructs its5-minute calendar ATR for this reason. The builder now requires per-key
   frozen source compression for ATR sizing and computes `source_calendar_atr()` with source-chart
   date banking, Sunday previous-close updates and prior weekday history. A synthetic23:59extreme
   shifts to the next source-date00:00candle, and future-input mutation leaves prior risk unchanged.
   The expanded selftest passed. This is a source-formula correction, not an observed PnL difference.

8. **Every consumed input must belong to the preregistered hash set. Fixed and inspected.**
   The earlier guard validated listed hashes without requiring every glob-discovered raw file or
   static ledger to be listed. It now requires membership for actual raw inputs and existing ledgers.
   Generated ledgers require a frozen adapter; their permitted source/code/receipt chain must remain
   checked. This prevents a concurrently added raw CSV from silently changing the intended input set.

9. **Broker net-flat target eligibility must use current equity. Referred to the core owner and fixed.**
   Opposing virtual sleeve tickets can leave the broker net flat with locked realized account profit.
   Requiring every virtual ticket to close could defer a valid target pass. The core owner changed
   target eligibility to broker net-flat equity, clearing virtual bookkeeping without a fictitious
   gross liquidation cost. A subsequent review caught stale pre-liquidation equity in that check:
   fees/slippage after a cutoff or guard flatten could leave cash below the target. The owner now
   recomputes equity before both net-flat checks and reports35synthetic checks plus100raw/fast parity
   tapes passing, including $53,000.50mark equity→$52,999.38cash cases that must not pass. These are
   owner-reported fixture results; the reviewed core hash is owned by its separate engineering audit.

10. **CL source calendar and incomplete risk histories. Final correction inspected and synthetic tests pass.**
    The CL gap-fade source uses an Eastern exchange-time chart. Its calendar-bank boundary is23:00CT.
    The final helper accepts a60-minute source-clock offset, caches by both compression and offset,
    and looks up the source entry date after applying that offset. A synthetic23:00extreme enters the
    following Eastern bank. Fixed offsets apply to relevant open-market observations; the Sunday DST
    transition is closed and cannot supply an invented quote.
    Previously, wholly absent source candles inside an observed day span escaped the missing count.
    A synthetic five-minute midday gap reproduced this. The final helper counts incomplete and wholly
    absent candles within that span, with frozen documented closures handled separately. An observed
    quote contradicting a frozen closure remains an uncertainty. Risk input gaps now make usable
    `stop_points_at_entry` NaN; the conditional owned-feed estimate is retained separately. VCS reuses
    this helper, and RTH range risk checks also preserve missing-bar counts. Boundary/full-day absence
    and exact original-feed parity still require source/calendar evidence, not a zero diagnostic count.

11. **Required target trade-through must follow the modeled target crossing. Fixed and inspected.**
    The final build requires per-market trade-through distances. A whole-minute high could previously
    qualify a long target even if that high occurred before the same-minute entry. The final check uses
    the remaining common path after the target crossing and honors explicit source qualifier failures.
    A pre-entry extreme alone cannot clear this gate. Failure remains an unknown source exit; it is
    not silently converted into a different stop/time exit or a profitable fill.

12. **An unallocated invalid sleeve must not poison another sleeve's observed quote. Fixed and inspected.**
    Failed source matching is encoded in the order's NaN raw fill, while valid common OHLC remains
    available to other allocated sleeves. The engine rejects an allocated invalid fill as UNKNOWN.
    Actual missing market OHLC still remains NaN, including while another sleeve is exposed.

## Source and accounting checks

- Account-session mapping retains Sunday evening Bridge entries: close-labelled17:01 begins the
  following account date, while17:00 closes the preceding date. A daily00:00 truncation is not used.
- Each asset has one shared modeled price. Opposing sleeves do not contribute independently
  adverse extrema. The engine's aggregate basis preserves locked PnL when net exposure is zero.
- Segment bounds cover `node[i]+1` through `node[i+1]` inclusive, before orders at the next node.
  Missing masks prevent a skip from treating an unobserved held quote as a flat return.
- Source entry/exit event rows, session boundaries and flat-deadline nodes are included in the
  segment index. A source fill with no matching quote reaches the core as an unknown raw fill;
  this does not erase an independently observed shared quote used by another sleeve.
- Confirmed source initial risk includes VB75fixed points, ONB30.25ATR15, ONBML/EOS.30ATR15,
  DT50fixed points, RS.60RTH20 and TOS.40RTH20. Bridge and default OT have no finite source stop.
  Initial risk must never be inferred from a future realized exit.
- Confirmed adapter exit classifications against source code: PaperTrend normal exits this bar at
  close; its holiday exits next bar at market. SwingTarget normal/holiday exits next bar at market.
  FC2B `.stp` exits are stops and `.mkt`/`.eod` are next-bar market orders. VCS normal exit is this
  bar at close. Native MNQ value is $2/point; normalization is not ten full NQ contracts.

## Limits that remain even after engineering fixes

The O→nearest-extreme→other→C chronology and synchronization of different assets are explicit
conditional models. OHLC observations do not identify the actual intraminute order or simultaneous
cross-asset quotes. Report fills and inferred source timestamps do not certify broker fills, rejected
orders, missing-bar extremes, exact source-feed parity or target trade-through. Material sensitivity
must remain visible in the final report rather than being described as native execution verification.

Risk histories use past observations but still need input-completeness and source-formula checks.
Finite ATR/range values do not by themselves certify a complete original source lookback.
Hard unknowns, unsupported source boundaries and material source mismatches must not become
zero-PnL observations or silent no-signal periods.

The final builder preallocates numeric tape arrays instead of retaining millions of Python row
objects and then copying them. The reviewed capacity bound is4×active minutes+4×source trades+3×dates.
For roughly3,100days and3assets, the raw OHLC array alone is about429MB. Source grids, tape arrays and
temporaries can still require several GB. These are allocation estimates, not a measured historical
run. Actual runtime/peak memory should be recorded after preregistration.

## Checks run

- `/workspace/venvs/thebeginning/bin/python analysis/codex_eval_paths_20261104.py selftest`: PASS.
- Separate in-memory synthetic builder/engine same-phase roundtrip: PASS, both fills, no open position.
- Pure in-memory adapter clock-mismatch fixture: reproduced finding4 above before correction.
- `/workspace/venvs/thebeginning/bin/python analysis/codex_eval_extra_ledgers_20261104.py selftest`:
  PASS after the known-clock correction; only synthetic clocks/kinds were loaded.
- Read-only source inspection; no actual historical normalization, path build, sizing screen, account
  simulation or return selection was performed by this reviewer.

The final builder synthetic selftest passed after numeric preallocation and source-chart ATR changes.
Final expanded builder/adapter selftests passed after the clock, strict risk, target and source-fill changes.
Reviewed builder SHA256: `767694333f4eb69039ea5c6ed3568883a80abe5e0502f1baf4a188226b4d10b1`.
Reviewed adapter SHA256: `8d9b54b839fe227f7d7774032cc92d8140ea2d616e14abd606039501aaba9ae5`.
The root must commit the final artifacts/config and pass their exact preregistration checks before
market calculations. The engine owner separately controls the latest core/fixture hash.
