# 6J fixing-flow mechanics: manual, synthetic-only follow-up

The user's reply on 2026-10-27 says existing native 6J access is available but cannot
be exported now: “Test the mechanics first to see if it's even worth it.” This
authorizes this limited follow-up, not an eleventh Hunt v2 hypothesis or a new
economic test. Hunt v2 stays completed at 10 hypotheses / 5 economic models /
4 gross screens; continuation and the t6 watcher stay paused. No empirical data,
historical event schedule, returns, proxy backtest or account replay will run.

## Question and mechanism, before running checks

The inherited claim is Japanese importers buying USD before a 09:55 Asia/Tokyo
bank fixing, especially on settlement dates called gotobi. Commercial payment
objectives can create demand, but neither a date indicator nor an individual
invoice proves aggregate net demand, its magnitude or residual demand after
exporter netting, dealer prehedging and other orders. No admitted primary source
here certifies the fix's historical rule/era, bank calendar or actual order flow.

The directional implication, conditional on net USD buying moving USD/JPY up,
is **short USD-per-JPY 6J**. A post-fix long needs a separate temporary-impact
assumption; permanent repricing supplies no reversal. The question is whether
this chain is coherent, not whether it has positive expected returns.

The mechanism, gotobi dates and clock have adverse selection history. The pinned
Tokyo idea card and prior script already examined an NQ proxy and recent hourly
USD/JPY, with failure/opposite-sign summaries. Those summaries are not a complete
native 6J test, and changing instruments does not create a new independent family.
Do not rerun them, reverse the sign to rescue them or import their returns.

## Fixed mechanical checks

Use only invented values, explicit fictional holiday closures and Python named
timezones. The harness has no market-input or network interface.

1. USD/JPY up/down/unchanged maps to the opposite/zero reciprocal change. This
   is a bookkeeping illustration, not an executable spot-to-futures substitute.
2. Importer/exporter offsetting and already-prehedged scenarios need not leave
   residual USD demand. Quantity scenarios are arbitrary, not measured flows.
3. A lasting impact and an assumed reversing impact imply different post-fix
   outcomes. A fix alone does not choose between them.
4. Convert the inherited 09:55 JST clock in winter, summer, both US transition
   weeks, Monday-to-Sunday and year rollover; retain previous Chicago civil date.
5. Incomplete calendar knowledge returns UNKNOWN. A deliberately fictional
   closure fixture checks backwards shifting and deduplication, not Japan's
   actual convention. Invalid dates are rejected rather than moved to month-end.
6. An observed-bar decision can use only a subsequent open after its explicit
   receipt time. A missing exact open is unavailable, not forward filled. A
   calendar-only order need not wait for a price signal; no entry rule is selected.
7. Show two-sided execution friction and the 2x round-trip gross hurdle as
   conditional arithmetic. Illustrative contract multiplier/tick and fees are
   assumptions, NOT admitted current native specifications, fee quotes or fills.
   Do not infer micro execution from scaling standard 6J.

No complete strategy, stop distance, executable order schedule, empirical trial,
gross-effect mean/t, placebo, book improvement or trading approval is selected
by these checks. A later empirical study would first need an admitted mechanism,
actual contract/calendar/cost provenance, new bounded authorization and its own
committed preregistration. Synthetic success cannot clear those gates.

## Decision rule

Implementation consistency PASS permits a **small later source-admission and
gross-screen proposal**, conditional on the unresolved mechanism/calendar/cost
facts. It does not justify a costly full export or backtest by itself. A claimed
native edge, tick-level fills, low correlation or account benefit without native
data is forbidden. Keep the disposition NEEDS DATA / SOURCE CONFIRMATION.

## Bound source context

- Prior gate: `agents/codex/research/hunt_v2_tokyo_fix_source_gate.md` (historical
  9/10 snapshot; the actual current budget is completed 10/10).
- Connected GitHub source head read 2026-10-27:
  `6416de2dd39782eb4a43bd665c866409da4deb70`, parent `d14dc9a`.
  Its unchanged Tokyo card blob is `3240398d45bd5f55f4144717dcfdef3399d54e90`;
  unchanged ranking blob `2b37b76fe74189ef87b044e8f1aa51cdd755bd0d`.
- Prior Tokyo script blob `e1d7e1c7421fe40b946141ace7e80fec62941186` was read
  as source only. No import, execution, Yahoo request or reanalysis.
- Final Hunt v2 summary and pause remain authoritative for that completed task.

Write only the authorized Codex paths. Preserve existing untracked work. Commit
this test contract and code before executing synthetic checks; retain results
and independent review separately from the completed economic ledger.

## Retained implementation review and revision

The first synthetic run at code/plan commit `d143a80` passed its 19 bundled checks.
An independent reviewer found the exact-open fixture insufficient: the helper
could accept a later observed open when the intended next-minute open was absent.
That output is retained as `synthetic_checks.json`, not a valid full mechanics
clearance. Before the revised synthetic run, require an explicit scheduled open
and add the missing-scheduled-open/later-open-present adversarial case. Save the
revised output separately as `synthetic_checks_v2.json`. This is a disclosed
synthetic implementation correction, not a new economic variant or trial.
