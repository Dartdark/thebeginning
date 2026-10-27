# Frozen independent six-leg euro package, v1

User-authorized reconstruction,2026-10-27. Mechanism/evidence sheet precedes data.
No author implementation or return parity claimed. No t6/hunt resumption,
optimization, live actions or source-payload re-export. One package configuration
and one own-EUR-momentum baseline; eight inspected economic series(total plus
six component series plus control), not eight independent discoveries. Author
trial count UNKNOWN, retain all reported failures/sweeps; don't invent a total.

## Data, clocks, calendars and missingness

Use Grid24 on native6E/ZN/CL/ES/GC minute files,2017warmup and2018–22design only.
Dates useAmerica/Chicago;15:00CT=16:00NewYork, same US DST schedule. Eligible
decision dates are preknown NORMAL cash-calendar dates fromcodex_s03_calendar.
No holiday/early-close decision; positions may persist over them/weekends.
This is our explicit custom decision calendar, not the author's chart session.

Exact close-labelled CLOSE15:00for all predictors; exactOPEN15:02for6Efill,
physically15:01CT. All closes are at/before decision, entry after decision.
Cross-asset daily changes are differences of successive scheduled cut closes,
not default exchange settlements. EUR reaction=CLOSE08:30−CLOSE07:29CT.
Daily EUR high/low uses observed native bars after prior eligible15:00cut
through today's15:00, and last completed Mon–Fri calendar week's range.

No forward-fill of required source endpoints, prices, complete rolling windows
or state across unknown decisions. Known calendar gaps are explicit; missing
normal cuts invalidate affected features. Expected-session rolling windows
retain missing rows, never compress them into fictitious complete history.
Gross/net diagnostics on observed coherent input blocks are labelled conditional;
unknown carry/exit paths cannot become zeros or a clean portfolio PASS. Require
allfive closes and EUR reaction endpoints plus nextfill for common analysis.
If an interval lacks an endpoint, close the coherent block at its last available
fill as an offline boundary liquidation; restart flat only after full rolling
warmup. This is a data-segment diagnostic, not an executable data-outage exit.
Record EVERY such boundary and deny clean execution/account promotion.

Continuous exports have no authenticated contract IDs or point-in-time roll map.
Do not fix their jumps by fitting returns. Mark raw-stitch roll ambiguity and
coarse6E-to-M6Eprices as source limits. No native-M6E liquidity/spread assertion.

## Fully fixed feature definitions

Trend asset score=mean(sign(C_t−C_t−h),h=10,21,63). Macro score=
(trendZN−trendCL−trendES)/3. Zero is flat. Raw macro DIRECTION=sign(score),
even when integer macro quantity rounds to zero. No learned/refit weights.

EUR annual volatility=std(last60scheduled close-to-close arithmetic percentage
returns,ddof1)*sqrt252, including the current completed return. Require all60;
zero/invalidvol is unknown. Multiplier=min(1.5,.05/vol). The5%target refers to
the return volatility of the base EUR notional, NOT5%of personal-account equity.
Base macro allocation2M6E; desired signed quantity=truncate_toward_zero(
2*score*multiplier), absolute cap3contracts. Other published allocations are
fixed RSI1,Weekly1,MacroShock2,StockShock1,GoldShock2. No fractional positions,
minimum-one override, changing capital reference or favorable rounding variants.

RSI2 uses Wilder exponential smoothing alpha1/2 of daily up/down changes,
seeded with the first2valid changes; missing resets state. BuyRSI<10withmacro>0,
shortRSI>90withmacro<0. Exit at a completed close>=SMA5(long),<=SMA5(short),
or after10eligible held intervals. Direction is tested at ENTRY only. No
same-decision exit/reentry. No intraday inferred touch of an unknown daily SMA.

Weekly entry: today's cut close strictly beyond last COMPLETED calendar week's
observed high(long)/low(short), matching raw macro direction. Exit at close
through the opposite current completed-week range boundary or after10eligible
held intervals. Missing/incomplete week is unknown. No rolling-five-day substitute.

Shock z=(today's close CHANGE−prior60changesmean)/prior60changesSD(ddof1).
The baseline EXCLUDES today's change. Differences work through nonpositive CL
prices; no log-of-negative or conventional CLpercentage return is used.
- MacroShock:abs(ZN z)>2 OR abs(EUR reaction z)>2. Follow source sign. Same-sign
  coincidence is ONE2M6Eposition; opposite-sign coincidence is flat, not a
  hindsight-selected branch. EUR reaction baseline uses its own prior60values.
- StockShock:abs(ES z)>2.5, followsign,1M6E.
- GoldShock:abs(GC z)>2.25, followsign,2M6E.
Shock desired exposure is held to next eligible rebalance. Consecutive same-sign
events keep the position without fake close/reopen fees; no pyramiding.

Control: same macro allocation/vol sizing but replace macro score by EUR's own
10/21/63trend score. All other clocks/costs are identical; control not selectable.

## Broker positions, execution and accounting

Maintain six signed integer virtual positions and one net broker position=sum.
Mark at raw6EOPEN15:02proxy and rebalance at that arrival point. For every buy,
price=ceil(raw/.0001)*.0001+.0001; for sell=floor(raw/.0001)*.0001−.0001.
Charge1.20USD*abs(quantity change). Grid projection is separate from the adverse
one-tick allowance; no additional quoted spread is double counted. Fees are
2.40RTplus2.50RTtickcost, before adverse grid projection. Treat one-way order
quantity, reversals, rebalance and explicit terminal/segment flatten correctly.

Daily gross=previous quantity*(arrival_t−arrival_t−1)*12500. Daily net adds
cashflow effects of current signed order vs arrival mark, minus unit fees.
TrackFIFOunit tickets for realized roundtripPnL and reconcile all realized net
to marked daily net when flat. Portfolio costs use NET broker turnover; component
standalone costs are diagnostic, with the netting-cost saving shown separately.
No claim these6E-derived execution projections are observed M6Efills.

No stop was specified: use only registered indicator/time exits; disclose
unbounded gap/margin risk. End-of-sample and missing-block liquidation at the
last observed arrival is explicitly diagnostic, never a hindsight executable
risk-management rule. No drawdown cap or optimized size is added.

## Design gates, trial accounting and later work

Commit this plan and exact code before new returns; bind sources/hash/version.
Run2018–22first. Report gross total/mean/t/year/side and turnover per equivalent
roundtrip before net. Raw gross per completed-equivalent unit must exceed
2xnominalRT4.90=9.80USD per leg for a gross PASS; extra grid cost only increases
the actual hurdle. Retain fails. Since net is simple exact turnover arithmetic
of those SAME fixed exposures(no stop rescue/search), report allsix native-cost
design curves as part of the cheap reconstruction, including gross fails.

FULL-package continuation gate: allsix standalone components positive after
costs, package positive; package dailyNW5t>=2, at least4/5positive designyears,
and at least30closed unit tickets in EACH component. Retain sparse/zero-exposure
legs as failures, not denominator removals. Gross failure also denies promotion.
No dropping legs or changing weights/rounding/costs to rescue the package.
Show trade t, dailyNW5,DSR_N326andN1000scenario, standardfive metrics,
long/short/year and all source limits. Package may be low-turnover; daily
statistics are primary dependence basis, not a count of overlapping ticket bets.

Only if the design gate passes, run immediate personal19 BASE/ADD/REPLACE/EMPTY
bench before extra robustness, with identical mark clocks/coverage and current
whole-contract sizes. Prespecified replacement is the whole CL Sunday personal
slot, EMPTY removes it. Require paired return/DD and median-profit gains versus
both BASE and EMPTY, no worseDD95 over5000paired252day20blockhistories,
seed2026102706. Candidate must be reconstructed at the actual book's mark clock
for that comparison; a15:01series cannot silently stand for16:00marks. Missing
joint source/roll/mark paths remain limits; no invented book contribution.

Freeze selected unchangedpackage and commit before2023+once, never freshholdout.
No2023+run if design fails. Fullpromotion needs t>=currentmetrics.t_threshold(N)
orDSR>=.95, bothperiodspositive, random-date and random-side same-exit placebo
p<=.05each, dependence/selection/roll/cost audits, and fresh independent raw-spec
checker. Account contribution required; annual correlation alone doesn't qualify.
Nulls if unlocked:1000nonwrapping calendar-matched dates and1000side flips with
same position durations/size/cost conventions; seed2026102707/08. Do not infer
significance from source-selected parameter plateaus or failed ML controls.

Personal is the only possible home for this multi-day specification. Explicitly
report50Kfunded,150Kfunded,50Kevaluation,150Kevaluation as incompatible with
their intraday/noovernight restriction as written; no intraday conversion here.
PowerLanguage only after passing relevant gates and source review, then Claude's
MultiCharts check. No live deployment. Preserve all counts/results; stop this
bounded build after a failed gate, not the user's future separate research.
