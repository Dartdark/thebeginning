# Anson momentum/range: frozen placement test across all current plans

Summary: Backtest the supplied intended rule to determine placement in50K/150Kevaluation,funded or personal plans.
Primary settings4.5/20come from the user; file3.0/6defaults are a standalone diagnostic,not a selectable winner.
No optimization; preserve source timing and separately identify Apex holiday adaptation.
If no setting earns a useful place under the declared gates, report it and move on.

Evidence: `agents/codex/evidence/anson_momentum.md` (TEST).
Source/user input: `agents/codex/inputs/anson_momentum/{source.txt,user_spec.md}`.
Plan pin: Claude `e34d71cd3537a9f019d2521e280fc92f3ffdb4c6`.
This document must be committed before any new Anson return series.

## Frozen source and variants

NQ5-minute bars,Central,IOGoff,Default-session proxy=Grid24 continuous observed bars across dates with the
repository exchange gaps. Use Grid24.bars(5),not a new cache. Treat each finite aggregated chart bar as observed;
do not require every overnight minute. Need prior20chartbars and the source CurrentBar history check,absorbed
by2017-12warmup. Do not claim an exact original2016-24 reproduction from data beginning2017-12.

At a close, momentum=close−close12observed chart bars ago. Denominator=mean20preceding bar high-low ranges,
excluding current. If flat,08:30<=Time<=14:30,denominator>0 andabs(momentum)/denominator>=threshold,
queue next observed chart-bar-open market entry in momentum direction. No volume,stop,target or volatility sizing.
Entry bar counts as held1 at its close; after HoldBars completed position bars,queue market exit at next
observed chart-bar open. A bar whose open exits a trade remains flat until its close; it can then signal an
entry at the following bar open. Preserve that flat chart bar between fills. ExitTime14:55 queues the next
chart-open fill,wall-clock14:55,normally the1-minute bar closing14:56. Market entries hold their opening minute;
market exits do not hold their fill minute's later range. Queue exits before subsequent signals at a close.

Exactly three return models:
1. `intended_raw`:threshold4.5,hold20;literal supplied time rules;personal primary.
2. `intended_apex`:same4.5/20,early-close adapter on repo calendar:entry signals strictly before11:30;
   queue final exit at11:30close for nextchart open,wall11:30,normally1-minute close11:31. Apex primary.
3. `defaults_raw`:file3.0/6unchanged;standalone diagnostic only,never chosen for account placement after results.

Raw early-close positions may carry into reopen because14:55 is absent. Preserve actual observed next-bar
execution and report all cross-date/late/gap spans; invent no stop,rescue exit or fill on a missing bar.
Source features and history always use all observed bars before account coverage filtering.
For Apex shared-day comparisons require finite minute OHLC08:26..14:56,or08:26..11:31on repo early-close
dates,and no unknown held spans/cross-date positions. Exclude unknown days for all allocations; don't delete
their observations from signal history. Show excluded dates,especially stress days,and altered block adjacency.

Personal uses intended_raw and marks open positions at each trading date's last observed close at/before16:00,
without looking beyond the mark. Fills after16:00 book to the next plan session; closure-spanning source positions
are allowed. Save/audit every held gap because bar exports alone may not distinguish closure from feed loss.
Do not silently erase those trades,forward-fill an execution,or claim complete tick-level risk coverage.
Candidate entry slip$.50/MNQ is charged in entry session; fee1.275+$.50exit slip in exit session. Preserve
published baselineTwin marking and its known cost timing rather than silently rebuilding that plan.

## Periods, prior results and statistics

Run fixed design2018-22 first;no model selection. Then2023+ once,report2025+ separately as the user's author-OOS
boundary,plus2018-24 partial author-IS and all years. All periods have already been seen by researchers or the
user; this is historical replication,not a fresh sealed holdout. The quoted2023IS trades/$86 and352OOS/$160
cannot be verified without the original ledger,full data/session/chart properties and variant registry.

Standard whole/long/short metrics: trades,win,netmean,total,t,Sharpe,Sortino,PF,Calmar,Ulcer,maxDD by period/year;
bootstrap90%intervals using5000daily10-day-block samples; trade/dailyMC at1/2MNQ. Report source raw and common
account universe explicitly. CostprimaryApex$1.04/micro RT +.25point per entry and exit=total$2.04/MNQ;
sensitivity fee$1.24. Personal follows publishedfee1.275(+two slips),not an invented broker quote. Author-cost
arithmetic at$7.25/NQtotal is a diagnostic on the same ledger,not exact author parity or an adoption convention.

Placebos for intended_apex:1000random-side runs on same actual entry events,identical timed exits(no stops),
so change sign of gross and keep costs;1000random-time schedules on same trading days preserving per-day event
count,side order,hold20and finalflatten,using eligible source entry times08:30..14:30(early before11:30).
Reexecute one-position/flat-bar constraints; overlapping shifted events skip rather than use future exits to
force a count. Seeds848/849. All diagnostic/trial counts saved; no parameter-neighbour search authorized.

## Baselines and account tests

Reuse prepared50Klab and exact prior RS replay after verifying current-plan dependency hashes. Latest150K
funded includes DualThrust2MNQ: reuse its pinned committed timed trades_replica.csv and strictly reconcile every
date/side/kind/entry/exit/net against the committed primary ledger before path construction with the unchanged
DT.lab_trades adapter. Map dates to the existing grid,never infer timestamps by price. The localcache lacks2017
RTHwarmup,so do not silently rebuild DT signals from incomplete history. Restore RS BOTHsides from the prior
reconciled ledger. This is baseline ledger reuse,not a new DT strategy search. No price-cache rebuild.

50K funded roster remains VB2/1,ONBMLrisk400,MON1,EOSrisk700,LDF2,NPFrisk500,Bridge1,CLS2MCL,MOC2MES,RS_L1.
150Kfunded=current non-RS roster scaled1.5 (VB3/1.5),RSboth1,DT2,ref$3000.50Kref$1500.
Use integerfloor(base*cushionf+1e-9),fclip[.5,1],existing50K/150Kfunded_sim rules and payout ladders.
Frozen50Kallocations:BASE,EMPTY_VB,ADD1,ADD2,REPLACE_VB2.150K:BASE,EMPTY_VB,ADD1,ADD2,ADD4,REPLACE_VB2.
VB is the preselected overlapping momentum slot; no slot chosen after correlations. Removing fullVB retains
flag conditioning in the empty control. Default3/6andrawclosurecarry are not Apex candidates.

1000paired500-day circular20-day-block histories,seeds1..4each250;measure250/500horizons,2018+and2025+
cohorts. Same eligible days and histories across allocations. Existing exact quantity-state minima may be reused
and generalized with declared50K/150Kparameters. Every configuration checks allfive original simulator outputs
on five fixed histories at both horizons. Synthetic fixtures cover payouts,DLL,trail,integer rounding and
ref1500/3000; do not assume a50Khardcodedlookup is valid for150K. Save payoutmeans,p5/p95,blown,all6,days6
including noncompletion and paired95%effect intervals from5000paired-history resamples. BothApexfee regimes.

Evaluation50K:currentVB8,ONB30risk1100,Bridge2,EOSrisk500;150Kscale2.5 meansVB20,Bridge5,risk2750/1250.
Compute integer risk quantities AFTER scaling dollar budgets,not2.5times already-floored50Kquantities.
Use existing challenge/evaluation rules50Ktarget3000,trail2000,DLL1000;150Ktarget9000,trail4000,DLL2000;
21trading-day horizons. Same allocation families and candidateMNQs as funded by account size. Full real-day
chronological windows,exclude any window touching unknown candidate day rather than compress time. Report
2018-22,2018-24,2023+,2025+ andfull2018+,paired pass/fail/time changes,median days,20-start-block intervals.
Preserve existing account-specific same-minute tie handling and disclose50Kpass-first versus150Kbreach-first.

Personal current14pieces and starterA/B/C/D from latest personal_portfolio.py,withTwin16:00daily marks,
OvernightAnomaly andDT. Preserve publishedlegacyfees(.55extra) and document per-nonzeroday VB undercount and
other fee differences. Candidate fee1.275 for matched convention. A/B:BASE,ADD1,ADD2. C/D/FULL:BASE,ADD1,
ADD2,EMPTY_VB,REPLACE_VB1 =21configurations. No selection of a new best ladder or size. MC5000paired252-day
histories,20-dayblocks,seed1 matching repositorydaily_mc,2018+and2025+;save profitp5/median/p95,lossfrequency,
DDp95,capitalrequiredat20%DD andreturn/DD. Report actualchronological metrics and effect uncertainty; an added
positive-return leg does not earn a place if risk/capital burden absorbs its contribution. Source raw gap/MTM
and baseline approximate cost/path limitations remain explicit. Do not claim a personal intraday-risk certificate
from EOD-onlyMC. All candidate sizes are research probes,not new live allocations.

## Mechanism, power, trial burden and decision

Price continuation is hypothesized; no forced-flow exemption. ReportedEV makes a cheap cost/power screen
plausible. Multiple rejected TP/SL/sizing/side/WFO settings count even though final code is simple; exactauthor
search size is unknown. At minimum use latestTRIALSrankeditems + priorCodexOR2 + night-switch2 + current3,
recordfouraccountcontexts and21personalconfigs separately. No adapting after2025+ observations.

No plan change unless currentpromotiongates pass: MCconfirmation,multiple-testtANDDSR>=.95,positive design/
validation with2023+t>=2,clean placebos,independentcleanPASS and a material paired portfolio gain overBASE and
empty slot without unacceptable risk/capital. The user's2025+ interval spanningzero alone neither proves
overfitting nor justifies trading: evaluate dependence and tail losses at actualaccountsize.
If no plan gains,move on. No live,VPS,broker,key,PR#2,infrastructureorotheragentbranchchanges.
