# Selected MAE price-offset comparison — TEST as a bounded execution diagnostic

Summary: User explicitly requests a selected-book test after the source review; its earlier DON'T TEST history stays intact.
Select Vault Break, FC 2B and S47 by mechanism; one fixed 0.25% pullback, no threshold search.
Owned minute prices and existing parent adapters permit a conditional fixed-parent execution comparison.
Strict source/fill/path gates still control advancement; incomplete VB paths cannot certify a full strategy.
Reserve 15 definitions including baseline, main/stress candidate and two nulls per parent; no paused program restart.

## 1. Who trades / mechanism

The source's conviction hypothesis is unproved. This test asks a narrower mechanical question at the user's
explicit request: can a material price concession exceed missed opportunity and native fees on an existing
slow intraday directional exposure? FC 2B follows the opening drive; S47 follows Europe/NY agreement; Vault Break
is an intraday breakout with meaningful remaining holding time. MOC/NFP/LDF timing flows are excluded beforehand
because delay risks missing their short scheduled windows. No winner is selected from new returns.

## 2. Direction, size and timing

Reference is the recorded original virtual-parent entry event and raw price, known at that event. Child order
activates at the first following minute, excluding the original event bar. Tick-round a 0.25% adverse price offset
(buy down / short up). Rest until original virtual exit; exclude its entire exit minute because fill/cancel
priority is unidentified. Nonfills remain zero contributions on all original opportunities. Native one-micro unit
only; actual book sizes are a later stage. Target/stop/time intents stay original, not re-anchored to child fill.
All clocks are Central. This is the paper's fixed-parent architecture, not a regenerated native strategy.

## 3. Market mapping / input clock

Owned NQ one-minute OHLC (day + overnight) 2017–2022, Grid24, exact file hashes in config. Design April 2, 2018
through December 30, 2022. No 2023+ raw prices loaded in design; source ledgers contain previously seen later rows,
filtered before new return arithmetic. Existing FC2B/S47/unit-ledger adapters are reused and hashed. Parent/roster
source pinned to Claude commit in config. Missing bars/ambiguous source/target fills stay UNKNOWN; no imputation.
One-tick trade-through qualifies a child limit. Same minute order uses the existing common OHLC path convention,
not claimed tick chronology. Changed roll intervals are UNKNOWN; source adjusted cash is preserved otherwise.

## 4. Novelty / prior history

This is an expressly requested direct-user experiment after SSRN7063478 review, not independent evidence of a
new source alpha. Preserve E05 small-tick limits, all E06/24-stream results, author threshold/side selection,
the 10,000 earlier-definition floor and paused scout/evaluation/lab histories. Fixed offset differs from earlier
opposite-return timing; earlier negatives neither prove it fails nor justify changing it after this test.
Scout counters remain 4 hypotheses / 10 definitions. Dedicated direct-user reservation follows the already
committed N15/current-book precedents; no automatic scout lease or schedule is resumed.

## 5. Costs, liquidity and overlap

Primary MNQ point value $2, tick 0.25. $1.24 round-trip commission; one adverse tick per market/stop fill.
Passive child entries pay no entry slippage but require one tick through. A marketable gap uses observed OPEN,
with one-tick adverse cost capped at the limit. Stress: $2.48 and two market/stop ticks, also capped for gap entries.
Source targets keep their existing 1-point qualification; no future fill/price selection. Original source baseline
and stressed baseline use the same resolved population. No current-book-flat event selection is allowed.
Parent liquidity, concurrent book overlap and actual integer/cushion settings remain later account questions.

## 6. Power before returns

Prior known design opportunity counts are approximately VB 829, FC2B 425 and S47 367; no new P&L used to choose
them. Assuming an incremental SD of $100 per micro per event purely for planning, t=2 needs about $7/$10/$10
mean improvement respectively, with effective sample size lower under dependence. A roughly 4.5 multiple-trial
bar needs about $16/$22/$23. A 0.25% price concession can be economically material relative to this hurdle,
but cancellations and lost winners may dominate. This is feasibility arithmetic, not power certification.
At least 30 actual fills and complete paths are mandatory; paired daily inference and DSR gate selection.

## 7. Failure predictions and diversification

- Trend days may never pull back; missed winners can exceed price savings. Falsifier: nonpositive total net
  improvement or stress increment. Higher per-fill averages alone do not pass.
- Resting orders may fill during deterioration; common losses can coincide with VB/FC2B/S47 long exposure.
  No hedge or crisis protection is assumed. Full path/native risk checks precede any account inference.
- Existing VB source/target coverage is incomplete under prior strict admission; its result is conditional unless
  every path qualifies. No majority/subset exception is introduced. Missing source information stops dependent stages.
- Changed brackets/parent state, fill gaps, fees and order priority could invalidate implementation. Independent
  raw-spec/native reconstruction remains a separate required gate even if this execution diagnostic passes.

## Decision

**TEST this explicitly requested bounded diagnostic**, with the protocol and exact code committed/published before
returns. A failed design stops controls/2023+/accounts for that parent without another offset or selected side.
Only a passing frozen profile earns matched controls, once-only historical validation and native current-book
BASE/ADD/REPLACE/EMPTY at actual size. No allocation, live system, VPS, broker or API-key authorization.
