# ORB30 EMA: implementation review — corrected synthetic checks pass

Summary: Independent source inspection and synthetic fixtures support the frozen minute-OHLC reconstruction.
Found an entry-phase error in the original side-null control and missing flatten-open excursion updates; both are corrected.
Fourteen execution fixtures and 100 arithmetic path checks pass without accessing real market returns.
This is not independent raw-data replication, MT5/MC compilation, native-tick parity, or a strategy-promotion verdict.

Scope: `agents/codex/plans/orb30_ema.md`, `analysis/codex_orb30_ema.py`.
Reproducible independent fixtures: `analysis/codex_orb30_review.py`.
Output: `analysis/outputs/codex_orb30_ema/independent_synthetic_review.json`.

## Findings and correction checks

1. **Original side null entered too early.** It used a market fill at the open of the actual breakout's minute, rather than the actual breakout price and phase. On an intrabar breakout, this admitted pre-trigger price movement. The corrected mode2 replays the upward trigger for both sides, retains actual gap-adjusted entry/risk, and mirrors the short bracket. New fixtures explicitly exclude the pre-entry low before an upward trigger and stop a mirrored short only after that trigger.
2. **Original MAE/MFE omitted the flatten open.** If the flatten open created a new adverse/favorable excursion, the ticket stored the previous extreme. The corrected flatten branch incorporates the exit open. Main P&L had already used the proper exit price; the correction does not itself change the trading protocol.

The engine's candidate order is not active during the opening range. OR labels511..540 imply first execution at541 open (09:00 CT wall time). Completed M30 closes feed a causal EMA; the 09:00 value is saved before later bars are processed. CASH retains history across dates and only admits cash M30 closes; FULL admits complete M30 bars throughout the available session. Missing minutes prevent a bar entering this explicitly defined EMA proxy. These are declared reconstruction choices, not verified author-feed conventions.

Other execution fixtures check entry-bar protection, worse-open stop gaps, entry-gap risk/target recalculation, one trade/day, exact one-point target-through, flatten-before-entry cancellation, no-target hold, and explicit unclosed status when the flatten bar is missing. Synthetic observations never substitute for an empirical held-gap audit. Integer MNQ sizing has no margin constraint; it must not be described as a broker-executable account simulation.

## Statistical interpretation

- A randomized trade sequence conditions on the existing tickets; it cannot establish the breakout trigger's incremental value. The fixed/random-time controls in this reconstruction move stop geometry relative to their market entry and therefore test more than timing alone. The report must retain that qualification.
- Conditional side controls preserve actual trigger timing, but use the already selected breakout dates; they are not a prospective short-entry strategy.
- For identical ordered R returns, fixed-fractional equity is a product of `(1 + fraction*R)`. Uniformly scaling initial equity preserves relative drawdown. A correctly normalized contiguous subperiod cannot have greater relative maximum drawdown than its encompassing curve. One hundred independently generated synthetic paths verify this arithmetic here.
- The original post explicitly says R uses balance-at-entry; that formula is correct. Its doubled average R alone does not prove the second reply's proposed denominator mistake. Raw ledgers and exact definitions are needed to diagnose the incompatible 16.07% subset/10.16% full-history claims.
- Profit factor from balance-weighted dollars can change when the same R returns are re-compounded or reordered. Do not call it universally scale-free across those transformations. Exceeding a10% drawdown limit is also not synonymous with ruin.

## Remaining evidence boundary

No original EA, complete inputs, MT5 ledger or broker tick data were supplied. The authorized flatten/EMA proxy cannot prove original CFD-to-NQ translation. The synthetic tests do not validate cache provenance/completeness, holidays for every exchange era, live receipt latency, limit queues, true within-minute order, contract-roll treatment, or plan-account chronology. A separately reviewed raw-data rebuild and native platform parity remain prerequisites to promotion.

## Additional PowerLanguage prototype static review

Scope additionally includes generator `analysis/codex_orb30_code.py` and generated `agents/codex/code/ORB30_EMA_Research.txt`. No MultiCharts compiler, chart, broker or trading connection was used.

Initial static review found two material issues and sent them to the builder before completion:

1. Resetting M30Count whenever the calendar date changed excluded every midnight-ending M30 bar, whereas Python includes the complete previous23:31..00:00 bar. Continuity must preserve count across consecutive23:59→00:00 dates and still reject true gaps.
2. If the flatten minute is absent and a position crosses dates, the original date-reset code cleared ORLow and DecisionClock before management. That could enlarge the stop and remove the overdue-flat condition. A carried position needs preserved anchors and an explicit emergency-flat/no-entry fault state; do not claim guaranteed timer flatten from this completed-minute approximation.

The review found the intended tick-up target rounding, one completed-minute OR update, and persistent DayQty reasonable by static inspection. The integer diagnostic and MC MaxContracts cap must be compared explicitly. Provide sufficient pre-period M30 warm-up. Same-bar built-in protection, order cancellation, gap-fill stop reanchoring and next-tick time exits still require actual compilation and platform replay; the code is a research prototype, not a tested EA or deployment candidate. Correction verification is recorded below when the generated source is updated.

**Static correction verification:** The regenerated source now preserves M30 continuity across a consecutive midnight boundary; independent counter fixtures admit that complete bar and reject a deliberately gapped bar. The new CarryPosition state preserves old OR anchors, blocks new-day entries and OR accumulation, and repeatedly requests an emergency market exit while the carried position remains open. Both static findings are addressed in the generator and generated text. This fault behavior deliberately differs from the Python unclosed-ticket flag; it is not an independently tested live-exit guarantee. Compiler acceptance, broker cancellation/acknowledgment and native tick parity remain unverified.
