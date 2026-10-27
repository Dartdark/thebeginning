# PrimeSync reconstruction and frozen exit comparison

Summary: Build the requested research PowerLanguage code and compare two exit styles.
The user authorized this code prototype before profitability is established.
No original code/settings were supplied; this is our explicit reconstruction.
Commit this plan before new signals/returns. No live files or allocations change.

## Fixed entry specification — assumptions, not the author's verified settings

- ES and NQ; 15- and 30-minute bars, CT, Globex history, one position per context.
  Four user-requested study contexts, not a choice of the best context.
- SMA150: completed close crosses from <= previous SMA to > current SMA for
  longs; reverse for shorts. Both sides remain enabled without optimization.
- Chart-bar VWAP, typical price x total volume, reset at 08:30 CT each date;
  only bars ending after 08:30 and at/before 15:00 enter its running sums.
- Current total volume >1.5 x mean of the previous 20 bars (exclude current).
- Current high-low >1.2 x mean high-low of previous 20 bars (exclude current).
- Chop proxy ADX(14)>=20; ATR = simple mean of 14 chart-bar true ranges.
  Signal-bar ATR x1.5, rounded up to the 0.25-point tick, frozen as initial R.
- Signals after 08:30 and strictly before 14:30 CT. Enter at the immediate
  next minute open; a missing scheduled entry does not permit a later fill.
- Skip known cash holidays/early-close sessions using codex_s03_calendar.
  Close remaining positions at the close of the minute stamped 15:00 CT.
- Four completed parent bars of cooldown after a full exit, counting actual
  nonempty chart bars across sessions. No pyramiding, reversals or compounding.
- Exclude the initial 300 available chart bars for warm-up. Require the full
  scheduled signal bucket and native next entry minute; inventory missing data.

## Exactly two exit variants

0. MILESTONES: full quantity to target 4.5R. A touch of 1.5R raises stop to
   entry; touch of 2.5R raises stop to the original 1.5R price.
1. THIRDS: one-third at 1.5R, one-third at 2.5R, rest at 4.5R. Stops advance
   after the corresponding partial limit fills, not merely a target touch.

No additional runner, slope, session, direction or filter variants are authorized.
This is two exit protocols across four fixed contexts: **eight evaluated cells**
and no market/timeframe selection. Count all eight in the results/trial disclosure.
The entry family already has the author's undisclosed prior looks.

## Sizing, costs, execution and uncertainty

Same $500 planned risk per position in both variants. Traded units are MNQ/MES
equivalents using NQ/ES signal/price history: point values $2/$5. Quantity is
3 x floor(min(30, floor(500/(R x point_value +5)))/3). Skip quantity<3.
The $5 reserve is for sizing only, not an additional P&L fee.
Native assumed commission $1.04 per micro round trip. Entry and stop/time exits
each slip 1 tick adverse. Passive target fills require 1 point trade-through,
matching the existing research convention. Each exited unit pays its own costs.
Targets round away from entry to native ticks. Frozen R is anchored at actual
slipped entry. Planned risk is not a bound on gap loss.

Reuse Grid24.bars and existing ADX/metrics/calendar tools. Extend the execution
walker only for progressive stops and integer partials. Intraminute path follows
the repository open-to-nearer-extreme-first convention, then the other extreme,
then close. Do not use a minute's high to tighten a stop before its path reaches
that high. Record an ambiguity flag; winner advancement additionally requires
positive net under adverse-extreme-first execution, registered as a diagnostic.
Missing held prices make a path unresolved: retain it, never silently zero-fill
or score its unknown P&L. No validated advancement with unresolved held paths.

Continuous contracts are unadjusted. Flag a signal whose preceding 150 chart
bars overlap the standard quarterly roll window (expiry third Friday minus
8 calendar days through the following Friday). This is a broad diagnostic,
not a claim that the precise vendor roll timestamp is known. Advancement must
remain positive excluding those flagged trades; exact roll provenance remains
necessary for a later implementation/account claim.

## Design selection and hard gate

Design 2018-01-01 to 2022-12-31 only; no 2023+ returns until the gate passes.
For each exit style, average its four context daily P&L series on common dates
for the selection statistic. This correlated equal-weight research score is not
an executable quarter-contract portfolio or four independent samples.
Choose the higher total design score; a 90% paired 20-day block-bootstrap interval
on the score difference that includes zero means no established winner, and
the simpler MILESTONES stays the provisional code default.
For a conclusive winner the interval must exclude zero in its favor.

Advancement requires: net positive, daily t>=2, at least 3/4 contexts net positive,
at least 100 total context-events and 30/context, no unresolved held path, positive
after excluding roll flags and positive adverse-first execution. If any fail,
stop: publish the code as unvalidated, the relative design comparison and why
there is no qualified strategy winner. Do not open 2023+ or run funded benches.
The cheap t=2 gate is not promotion; global trials-adjusted significance and
matched random-side/time controls are required later under a separate plan.

If it passes, evaluate only the chosen universal exit style on 2023+ unchanged,
whole/long/short/yearly metrics and 1,000 whole-day-block bootstrap intervals.
Recent data already seen in other research are historical validation, not fresh
holdout. Full account tests require independent implementation checks and native
MC parity; absent that, mark every placement blocked rather than infer benefit.

## Reporting and code

One flat-to-flat position is one observation; scale-outs are not independent
trades. Retain trade/fill/signal/audit ledgers and by-year metrics: gross, fees,
slippage, net, trades/win/mean/t, Sharpe/Sortino/PF/Calmar/Ulcer/maxDD.
Save code/input hashes, dependencies, dates, exclusions, seeds and plan commit.
MC prototype uses bar-close signals, intrabar order generation for stop updates,
initial built-in protection, actual entry anchors, same integer tranche rule
and no look-ahead. Its native symbol volume and platform ADX seed can differ
from the mini-price/micro-cost Python screen; do not claim compiled/parity status.
If no meaningful positive evidence survives, do not add it to the promising queue.

Files: analysis/codex_primesync.py; agents/codex/code/PrimeSync_v1.txt;
agents/codex/results/primesync.md; analysis/outputs/codex_primesync/.
