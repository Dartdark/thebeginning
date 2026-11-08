# Frozen ingredient round: S30, S47 v2, Kusho v9

Summary: Dissect the three families named by the user, without choosing a changed strategy.
Commit this plan, evidence, exact harness and source manifest before market returns.
Five definitions per family, S30 on both NQ/ES = **20 market/rule combinations**.

## Frozen definitions

**S30, NQ and ES**, cash-session IBS = (15:00 close − low)/(high − low), source 08:31–15:00 minute bars.
At least 380 observed closes and the 15:00 close; require next 15:01-labelled OPEN and positive range.
`original`: long IBS<0.20, exit IBS>0.80, no stop/target, one position, next-bar market fills.
`no_low_IBS_entry`: enter on every valid decision while flat; original upper-IBS exit.
`fixed_5_session_exit`: original entry, exit at the first valid decision at least five source weekday rows later,
instead of the upper-IBS exit. Five is fixed, not selected from tested horizons; missing decisions may extend it.
`opposite_same_schedule`: original low-entry/high-exit event schedule, short instead; mirrored market costs.
`close_strength`: long IBS>0.80, exit IBS<0.20; changes reversal to strength-following, not a short mirror.
No unbounded buy-and-hold or extra horizon/threshold is priced.

**S47 v2, NQ:** exact source timezone-aware London 07:45→08:30 impulse, |s|>0.0625 relative to past20
overnight ranges (at least15 usable), plus matching Chicago08:30→09:30 move; enter09:31-labelled OPEN,
source 0.50×overnight-range tick-rounded stop active **after** the entry bar; exit15:00 CLOSE.
Source roll/holiday and coverage guards retained.
`original`; `no_NY_agreement` (v1); `NY_only` (follow Chicago first hour, remove London threshold/agreement);
`opposite_direction` on original selected days with mirrored stop; `no_stop` (infinite stop distance).
The first two removals must pass exact retained-trade identity as pure nested comparisons.

**Kusho v9, NQ:** use retained Data(adjust=True), v9, conv='ours'; not FAR or C03.
15-minute bars09:00–13:45, bullish above EMA50, lower wick≤70ticks, limit at signal open for one bar;
mirrored shorts in the source DOWN regime. Source swing/fallback bracket, break-even and21:00 scheduling,
one position, entry-bar protection delay and holiday behavior retained.
`original`; `no_wick`; `no_EMA`; `no_break_even`; `flat_1545` using existing flat_rth=True.
Only disable BE with an explicit Boolean guard; zero trigger is not 'off'. Native source entry needs1tick
trade-through, target1point; no touch-fill alternative or additional entry-bar repair is priced.
Filter removals can change later occupancy; do not pretend they are nested trade deletions.

## Data, boundaries and source parity

Raw Git snapshot `fe35af99aa90d7f31b91f8693859251bb44dd9ab`, retained Grid24 and exact source hashes.
Configured Python environment, shared metrics/resampling/ingredient helpers. No persistent research cache.
2017 features warm-up only. Design2018-01-01–2022-12-30, then unchanged recent2023-01-01–2026-10-09 after
implementation admission. Already-seen recent history is replication, not a fresh holdout. No economic selection
is made between the cases. Source calendar guards and marker/fallback conventions are exposed.

Each era starts flat. S30 uses only that era's decision rows, retaining computed cash-session features. For
Kusho, indicators/regime/swings retain all past warm-up; pre-era signal closes are masked so positions start flat.
Open positions at the era end are forced closed for **boundary accounting**, flagged separately, never described
as an original rule exit. S30 uses its final valid decision's15:01 OPEN; Kusho its final observed close after entry.
Terminal exits pay market friction. Reconcile all positions, including terminal ones; don't silently omit unrealized
losses or let validation returns enter design. Unfilled final pending orders are not fills.

Closed original S30 trades must match the unmodified source run on the same era decision table; original Kusho
nonterminal trades must match unmodified source run on the same warm-feature/flat-start view. S47 original
source prices/costs preserved. Source parity is not new MC certification; mark any lack of independent native check.
Instrument only the frozen alternatives and terminal/time/state metadata. No top-level source research/live code.

Retain source roll_minutes price-jump identification/removal and Kusho's adjusted indicators, and save the
identified jumps. This monthly maximum and full-sample threshold are retrospective continuous-series repair,
not verified actual roll dates, live-known features or free executable rolling. Can remove real economic gaps;
attribution remains conditional on that existing approximation. No new native/point-in-time alpha claim.

## Daily accounting, prices and costs

Use **marked-to-market** daily P&L for S30 and Kusho, not exit-only booking. Source-calendar weekday cuts at
23:59CT; weekend price changes/exits accrue on the next weekday. Last observed close at/before a cut only,
with stale/missing marks flagged. Include entry/exit fill prices, subtract each crossed roll jump once, and allocate
half commission to entry/exit. Individual-leg daily totals and long/short/year totals must reconcile to trade net
to the cent. Record exit-booked DD separately to expose hidden holding risk. These cuts are research accounting,
not a prop firm's EOD/trailing clock. Keep actual entry/exit minute indices and full observed adverse paths.

NQ$20/point, tick0.25, commission$7.25RT; ES$50/point,tick0.25,$5RT. S30/S47 market fills pay1tick each leg.
Kusho entry/target are limits (no extra tick charged); market/stop exit pays1adverse tick. Target-through policy
remains unchanged. Micros scale price/slippage dollars by1/10, with **assumed$1.25RT native micro commission**;
never scale standard commission by1/10 and call it native. Save gross, commission, slippage, roll removal and net.
Extra-cost stress subtracts1additional tick per actual market/stop leg on fixed orders, not a new fill-path replay.
Roll execution cost/contract identifiers/quotes remain absent. No compounding or risk/size search.

Retain missing held bars, target-minute ambiguity, unprotected fill bars, nonpositive swing risks, last-close
fallback and terminal counts. Observed adverse marks are not native-tape extrema or account breach probabilities.
Daily stale marks and absent bars remain uncertainty; don't invent quotes or a protective stop on an unprotected bar.

## Gates, analysis and report

Before real returns: fixtures for low/high IBS rules, five-session exit, opposite schedule, explicit BE-off,
S47 no-stop and DST clocks, standard/micro costs, Sunday bookkeeping, roll subtraction and daily reconciliation.
After design: require original-source equality, finite execution/net, gross/net/daily reconciliation, independent
price-path fixtures and preservation of each case. Abort on implementation failure; no profit-driven repair.
Commit design receipt before opening recent; identical code/settings/data conventions throughout.

Whole/era/year and all/long/short metrics: count, wins, gross/cost/net/average, t, Sharpe/Sortino/PF, initial-peak
DD/Calmar/Ulcer, exit-booked DD, worst trade/adverse mark, micro and cost stress. Save features/admission,
trade/daily ledgers and run identity/dependency versions. Original annual/Sharpe and base-minus-each-case
annual effect:1000moving20weekday block draws, seed80314. Multiday paths can exceed a block; limitations explicit.

S47 pure gates: removed count/total/mean/t plus1000within-year random drops matching original counts, total
profit and DD. S30 entry/exit and Kusho filter removals change the position state; paired whole-rule comparisons
only, no false removed-trade/random-subset claim. Side/exit changes are nonnested policy comparisons. No sixth
economic definition or post-result rescue.

Persistent contribution requires original-minus-case profit>0 in both eras; stronger additionally requires both
paired lower bounds>0. Mixed effects/wide bounds remain conditional; protection judged with tail risk too.
All prior author/research/ingredient looks remain multiplicity. No best-case adoption or standalone ranking.
No new candidate, combined rule, MC code, portfolio/account runs, plan/TIER edits, live/VPS/broker/key access,
external messages, paid data, scout-history changes or duplicate automation. Independent review follows completion.
