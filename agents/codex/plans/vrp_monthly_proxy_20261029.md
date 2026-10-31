# Monthly VRP proxy: bounded personal-only feasibility test

Summary: User explicitly authorized an adapted test on 2026-10-29 after source-only review.
Two frozen monthly equity-exposure rules; three unselectable controls; no parameter search.
Use causal VIX-minus-ES-realized-variance proxy, not exact SPX or author-data replication.
Run 2018–22 design first; failed gates stop all 2023+ returns and account benches.

## Authority and source boundary

The uploaded Zhou (2018), SSRN 1783624, motivates a positive equity premium at one-to-three-month horizons.
No compulsory order flow is identified. This is uncertainty-risk compensation, not a forced-flow hypothesis.
The user explicitly requested testing now, including an adaptation if source parity is unavailable.
The author's homepage links VRPtable.txt through December 2024; the Drive host is network-policy denied.
The official Fed table ends December 2008, before our design period. Neither is substituted with invented data.
Existing data/SPY_daily.csv has index/futures-scale values and is NOT used as SPY.

## Frozen proxy and information clock

Use data/VIX_daily.csv end-of-month exact-date CLOSE, variance IV=(VIX/100)^2/12.
RV is the completed previous calendar month's sum of squared five-minute ES cash-session log returns
(08:30 open to closes 08:35,08:40,...15:00 CT, shortened to12:00 on known early closes), plus each cash
day's prior cash close to current08:30 open return. Every required endpoint must exist; no interpolation.
Continuous ES replaces SPX: a material source deviation. The prior cash close comes from the last calendar
cash session, not a silently stretched older session. Closed holidays contribute no cash observation.
Feature-only quarterly roll corrections use shared roll_adjust.roll_jumps on a grid PREFIX ending at that
month's last cash session. Its median-break heuristic is evaluated using only that prefix. Difference-adjust
cash endpoints by detected jumps between endpoints, with levels on the latest known prefix contract scale.
Unverified vendor roll provenance remains a limitation; this is a research proxy, not certified source parity.
RV must have all cash-session five-minute endpoints and overnight anchors for the calendar month, or that
month's feature is unknown. An unknown feature cannot silently become zero or a no-trade observation.

Month-end VIX and completed RV available conservatively at17:00 CT on the final cash session.
Decision at08:30 CT of next month's first cash session; first fill at exact08:31 bar OPEN, representing
08:30 boundary under the exporter close-label convention. This provides an overnight delay after the feature.
No trade at the feature's closing price. CT=America/Chicago with DST. Rebalance/exit at the same next-month
first-cash-session08:31 OPEN; charge a new round trip for every independent monthly allocation.

## Tradable window / instrument adaptation

Target months January, February, April, May, July, August, October, November ONLY. March/June/September/
December are omitted by calendar BEFORE observing returns to avoid holding an unverified continuous-contract
switch. Their first cash-session open may close the prior month's position before the roll window.
This restriction is our adaptation, not a source result. It limits generalization and statistical power.
One fixed MES-equivalent long per selected month: $5/point, integer one; before MES listing this is an ES-price
counterfactual, explicitly labelled. No shorts, target, stop, leverage escalation or intraday flatten.
Hold overnight: personal-account research only; incompatible with all four Apex evaluation/funded homes.
Missing held minutes do not alter scheduled no-stop P&L endpoints, but are audited and prevent implementation
certification; missing entry/exit or daily cash marks veto the entire data gate, never delete losing events.
Monthly mark ledger uses cash-session closes including early closes; overnight/weekend moves accrue to next
cash session. Daily mark totals MUST equal monthly ledger net. Margin/intraminute liquidation not modelled.

## Five frozen economic definitions; no tuning

Candidate P: buy one MES-equivalent next target month iff previous month's proxy VRP=IV-RV >0.
Candidate H: buy iff proxy VRP exceeds median of the previous12 calendar-month VRP values EXCLUDING current;
all12 must be known. The 2017 warm-up may be insufficient; retain unknowns and counts.
Control B: constant one-MES-equivalent long in the SAME candidate-known target months.
Control I: IV above its previous12-calendar-month median (exclude current).
Control R: RV below its previous12-calendar-month median (exclude current).
For paired comparisons use the common known12-month history universe for all five; additionally retain P's
standalone coverage count, without evaluating another return ledger on the larger universe.
These are two candidate rules plus three nonselectable controls, five economic definitions total.
No sign inversion, third threshold, NQ port, optimized horizon or post-gate rescue.

## Costs and gross-to-net bridge

Native assumed MES commission $1.24/round trip plus one adverse0.25-point tick EACH side ($2.50 total):
RT=$3.74. This includes spread allowance; do not add spread again. Stress four ticks EACH side: RT=$11.24.
Compute gross at raw ES opens then subtract costs; no fictitious micro quote precision.
No interest on idle cash, dividends or futures cash financing adjustment is added. These are ES-price P&Ls,
not SPY total returns and not fully collateralized investment-account returns. Capital$50,000 only for Ulcer.

## Sequential gates (fixed now, before outcomes)

Stage1: design2018–2022;2017 feature warm-up, no2023+ ES price files. VIX filtered to<=2022 immediately.
Data gate requires at least30 common-known target months; all scheduled entry/exit/daily marks known.
If feature incompleteness prevents30, retain diagnostics and STOP; do not repair after observing targets.
Evaluate both candidates once on the common-known universe; no selecting a new threshold.
Economic gate for EACH: >=15 selected months, gross mean >2*$3.74=$7.48, net total>0,
monthly trade t>=2, and net total>B's net total. This is screening, not promotion.
Filter controls: removed B trades must have negative mean and t<=-1; exactly-count-matched random month
drops1000 draws must be beaten on BOTH profit and max daily DD in>=90% of draws. No removal means no
new filter merit. Retain the unfiltered base and all failed definitions. Monthly observations, not daily
marks, determine the trade t; also report monthly net-difference NW t with3lags. Seed1783624.
Failure stops2023+, MC/full portfolio and PL. A failed early gate is a completed negative feasibility test.

Stage2 ONLY if>=one passes: commit design disposition before one unchanged2023+ historical validation;
complete target months through latest source-available exit, no partial current month. Load2022 warm-up
plus2023+ only; do not call this a fresh holdout. Show candidate net positive/recent t>=2, same filter
controls and actual cost stress. Bootstrap three-month blocks1000draws on paired monthly books, retaining
daily paths within sampled months. No candidate selected on validation. A failure stops account placement.

Stage3 only for a passing candidate: refresh latest personal roster, compare BASE/ADD/REPLACE/EMPTY at1MES
with the highest absolute2018–22 daily correlation existing long-equity component as the replacement slot,
selected without2023+ results. >=5% gain in mean-profit/p95-DD, positive paired annual gain lower90% bound,
and no larger capital need at20%DD budget; native/intraminute/margin/MC parity unresolved means WATCH only.
Four Apex homes are structurally ineligible for this overnight rule: no payout/pass simulation implied.
Do not infer personal book contribution from standalone statistics. Shared resampling/MC tools are used if reached.

## Reporting, integrity and limits

Commit this plan and TEST evidence BEFORE return code is run. Commit the exact implementation before outcomes.
Record prereg/code SHAs, input hashes, versions, eligibility, unknowns, source attempts, all five definitions,
2018–22/year/long/all metrics with explicit zero-short rows, raw/cost/net, stress and daily-month reconciliation.
Reuse Grid24, roll_adjust, metrics, existing t/NW functions; extend in analysis/codex_vrp_monthly_proxy.py.
Use synthetic checks for fill timing, causal feature history, roll-crossing correction and book reconciliation.
No shared engine edits or strategy/plan/live/VPS/broker/key changes. Prior trials/Hunt/t6 stay preserved.
Independent review, native implementation parity and forward evidence remain required for any allocation.
