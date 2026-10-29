# Pre-registration: ES pre-payroll reopen premium

Summary: Test one long ES/MES rule before payrolls using only a known public schedule and lagged ATR.
No market return has been computed for this proposal. Design2018–22only; recent history remains closed.
One candidate and two controls reserve3economic definitions; no tuning or source/event substitution.
A failed gate rejects this protocol. Passing design must continue through validation and actual portfolio comparisons.

Hypothesis: non-FOMC pre-announcement impact uncertainty can pay a positive premium before the news.
Source/evidence: agents/codex/evidence/scout_pre_nfp_20261029.md.
Script: analysis/codex_scout_pre_nfp_20261029.py.
Source: ssrn:3290649, related3387172 merged; November1 2021primary author version.
Family:non_FOMC_preannouncement_reopen.
Run:scout-pre-nfp-20261029-design. Lease owner:codex-root-pre-nfp.

## Frozen executable rule
All55calendar/data-eligible NFP dates2018–22, no price/direction/occupancy selection.
Long ES at the open of17:06-labelled minute the preceding date (17:05CT wall clock);
stop1.0ATR15 measured with the prior calendar date's known lagged daily ATR; no target/reentry;
time exit the07:25-labelled minute close, five minutes before payrolls. Use shared grid.execute on a
shifted same-CME-session view. The original source instead starts at16:00ET and has no imposed stop;
this is an adaptation, not exact replication. Time-exit close fills are bar approximations; MC parity pending.
Reject missing entry/exit, <99%minute presence, any >5consecutive missing minutes, and quarterly roll-window
days8–17ofMarch/June/September/December. The pre-return inventory freezes exclusions.
Event date/clock must match the preceding month's BLS scheduled notice; no first-Friday guessing.
2017warm-up; no2023+inputs or outcomes in the design command.

## Definitions reserved before returns
1. PRE_NFP_ES_REOPEN: primary rule at1MES, plus1ES unit-cost bridge (same fills, not independent trial).
2. PRE_NFP_ES_CALENDAR_NULL:1000matched-month/weekday non-NFP calendar samples with identical rule/exits,
   seed3387172. One frozen null generator; no best placebo or alternate matching selected.
3. PRE_NFP_ES_COST_STRESS: identical fills with2ticks per market/stop fill.

Fixed base costs: ES$5RT+2x$12.50ticks; MES$1.24RT+2x$1.25ticks.
Stress MES$1.24+4x$1.25=$6.24. No sizing optimization. No shorts.
Information clock: previous-month public notice+one full day is available weeks before entry; all ATR inputs
precede the entry date. No future announcement content, VIX change or volume-based contract choice.

## Pass/fail and reporting
Data gate:>=40eligibleevents and>=90%of60officialevents; endpoint and coverage exclusions frozen.
Source55events and power limitations are disclosed; this is a cheap screen for a large effect, not a powered
confirmation of a small historical mean. Preserve all source/repository multiple-testing history.
All economic gates required: native1MES netmean>0, event t>=2,4of5positiveyears,5th-percentile mean>0under
2000year-cluster bootstraps (seed3387173), matched-calendar p<=.05 and stress mean>0.
Report ESgross/net and nativeMES, costs, whole/long results, shorts notrun, byyear, standard metrics,
coverage exclusions, bootstrap and placebo. Daily totals must reconcile to trades.
Any failure: commit REJECT, stop recent/account work and move to another evidenced family within global budgets.
No side flip, clock/stop/event optimization, rescue filter or unregistered GDP/ISM extension.

If design passes: commit selection, then one unchanged2023+historical-validation protocol with contemporary
prospective calendar evidence and hashed inputs. Current book sources must be refreshed read-only for actual
BASE/ADD/REPLACE/EMPTY at integer sizes for every eligible evaluation/funded/personal home.
Closest predicted overlap is the overnight equity-long sleeve; later NFP Fade is a different temporal exposure.
Independent checker, MC compiled/trade parity and forward evidence remain open until done.
No changes to allocations, live files, VPS or broker settings. User sends completed package to Claude.

