# Pre-registration: ZN Treasury benchmark clock

Summary: A bounded source-led intraday adaptation with a documented external benchmark-clock change.
No returns computed;2018–22design only,2017warm-up,175/180timestamp-eligible events.
One candidate+two controls reserve3definitions; all economic gates must pass.
A failed screen stops this definition; continue distinct source-supported families within global budgets.

Evidence:`agents/codex/evidence/scout_treasury_close_20261029.md`.
Code:`analysis/codex_scout_treasury_close_20261029.py`.
Run:`scout-treasury-close-20261029-design`. Owner:`codex-root-treasury-close`.
Family:`treasury_month_end_benchmark_clock_correction`; sourceSSRN3440417.

## Frozen rule and inputs

Exactly the rule/calendar/coverage/native costs in the evidence sheet. Long1ZN, final3bond business dates;
13:01open→14:00close before2021-01-14,14:01open→15:00close thereafter. Lagged ATR15stop rounded outward
to1/64point, no target/reentry. Shared Grid24 and grid.execute. Calendar/provisional/final inventories retained.
No target trade-through assumption affects this rule. No2023+inputs or current-portfolio outcomes in design.
Existing late-month Treasury failures count; the external2021clock correction motivates this additional look.

## Reserved definitions

1.ZN_INDEX_CLOCK_LONG: one candidate, fixed1ZN.
2.ZN_INDEX_CLOCK_CALENDAR_NULL:1000sameyear/month/weekday non-event samples, seed3440417,
  same stops/exits/costs; independent draws with replacement, no best-null selection.
3.ZN_INDEX_CLOCK_COST_STRESS: same fills,2ticks perfill, no new entry rule.

Pass all: at least150trades and90%of180eligible-calendar events; netmean>0; eventt>=2.5;
4/5positiveyears; fifth-percentile mean>0under2000year-cluster resamples seed3440418;
matchedcalendarp<=.05; stressedmean>0. Every definition is counted even if negative.
Report whole=longs, shorts not registered, byyear and all standardmetrics; daily/trade/cost identities must reconcile.
No post-result changes to clocks/dates/coverage/stops/costs. No multiday substitute after a failure.

If pass: freeze selection then register one unchanged2023+historical validation (already-seen repository history,
not fresh holdout). Continue surviving rule to current BASE/ADD/REPLACE/EMPTY integer-size comparisons for all
eligible homes, accounting for ZN's indivisible risk. Refresh current roster/data rules before accounts.
Require independent review, MC parity and frozen forward evidence before a trading decision.
No allocation, live/VPS/broker changes. User sends the completed reproducible package to Claude.
