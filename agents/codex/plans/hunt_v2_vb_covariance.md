# H10 preregistration: one extra VB micro only at negative estimated book variance contribution

Mechanism BEFORE data: `research/hunt_v2_independent_book_constraint_gate.md`. Adopted source is
`d14dc9a153df128aafd3f48d4fea2aa78b88bb28`. Root chose the accepted plain Vault Break parent before
any new feature/header/count/return inspection. Commit this plan/evidence before inputs; commit reviewed
implementation before each actual phase. H01–H09 remain closed. This is a new own-book cross-covariance
constraint, not scalar volatility targeting, an open-position loss gate, an ATR250 sizing rescue,
an outside forced-order claim or a fresh directional alpha. All prior parent/book/t6 selection remains.

## Fixed shadow book, exact quantity and completion clock

Let X be the saved daily published-proxy return of1MNQ VaultBreak. Let B be the sum of all19 adopted
one-micro daily proxy columns, INCLUDING that X. B is always the fixed SHADOW BASE19; do not feed past
POLICY/EXTRA results back into it. On date d use exactly the252 preceding stored book-date rows, all
jointly known/completed before d's first C1000 VB decision, INCLUDING zero/no-VB days. No current-date
value, partial window, dropping unknown rows, reindexing missing days as zero,2017 padding or future
filling. Freeze today's quantity for all its parent proposals/tickets.

Define sample delta=2Cov(B,X)+Var(X). **EXTRA=1 iff delta<0 and Var(X)>0; otherwise0. POLICY=1+EXTRA.**
Equality/unknown keep the existingq1. Exact decimal/rational arithmetic from stored CSV strings fixes
the sign; no epsilon, correlation percentile or dollar rounding. For n=252, sign numerator is
`2*(n*sum(BX)-sum(B)*sum(X)) + n*sum(X²)-sum(X)²`. Sample/population denominators have the same sign.
Because B already contains X, equivalently Cov(X,B-X)<-1.5Var(X); mere low correlation is insufficient.
The identity is a historical proxy-variance forecast, not proof that the actual next trade lowers risk.

Root's predata clock adjudication is the conditional published-shadow-book contract in the evidence
sheet: core legs are intraday (Sunday-to-Monday belongs to the Monday exit day); added legs use actual
exit/next-plan-day booking or Twin16:00marks. A previous book row is completed before the following
VB10:00 under that contract. This is not an authenticated account receipt or proof of native marked
equity. Audit date/coverage/booking assumptions; contrary future-date evidence vetoes. No fictional
delay repairs it. Mark/version/fee uncertainty stays explicit and prevents a certified improvement
unless bounded/rebuilt. The2026 roster was historically selected: counterfactual shadow returns do
not imply a2018 trader knew it.2023+ can only be previously seen historical validation.

## Five frozen economic definitions

1. BASE_Q1: causal protected plain VB1MNQ.
2. CONST_Q2: identical parent2MNQ on every ticket, unselectable exposure control.
3. COV_EXTRA: sole candidate piece, additional1MNQ on active dates only.
4. COV_POLICY: executable1/2MNQ, algebraically BASE_Q1+COV_EXTRA. Its t cannot qualify EXTRA.
5. STRESS_PARENT: unselectable parent with four adverse native ticks per market/stop fill, same fee.
   Summarize EXTRA/POLICY with their frozen PRIMARY mask; never select a new stress mask.

One parent ticket atq2 is not two independent observations. No baselineq0, new long/short direction,
parent/window/zero-boundary/buffer/roster/fee-view/size sweep, fractional risk scaling or leverage beyond2.
SP/NR7 were selected funded sizing studies; current personal plain1MNQ does not borrow their quantities.
Prior full-history VB1,743trades is selected source context, not a new design/EXTRA power measurement.

## FEATURE: first support gate before raw prices or candidate returns

Bind the canonical primary input and its same-case comparison copy BEFORE even headers:

- `analysis/outputs/codex_rebound/personal19/UNIFORM/fee_1.24/baseline_daily19.csv`
- `analysis/outputs/codex_rebound/personal19/SUNDAY2/fee_1.24/baseline_daily19.csv`

Both must match the pre-existing source-bound SHA256
`d724c7d02b6db71e63ba705079dbea7fefaa42c6b4f436308a28993ca1908803`; copy mismatch is not permission
to choose a favorable baseline. Bind provenance/builder/code/source hashes. Exact header is date then
the19 LEG_COLUMNS specified in committed `codex_hunt_v2_highwin_bench.py`; no alternate column/roster.
No financial maker import. Full-file hashing is metadata, not validation. Read each date BEFORE
numeric conversion; interpret ONLY2018–22 financial cells, never2023+ cells. Record skipped date
metadata count/future-financial-conversions0. All date keys unique/ordered, finite numeric19cells;
malformed/missing rows remain unknown and cause the global source gate to fail, never compress history.
Report actual stored-date calendar/gaps. Before feature evaluation, apply the bound shared
`codex_s03_calendar.calendar_status` source to FULL2018-01-01..2022-12-31. Every normal/early cash
date must have a stored book row; any absent expected row globally vetoes, never drop/compress or
zero-reindex it. Retain extra actual holiday/book rows in the252-row history. This is a minimum
calendar-completeness check, not proof of full native-futures coverage; preserve all gaps/source
limits. Generate/apply the schedule only after this commit; invented fixtures inject artificial
callbacks. First252 actual2018-start rows are unscored warmup; no fictitious earlier zeros.

Feature outputs: source row/window IDs, prior start/end/date<d, n, exact numerator/variance/covariance,
known flag, qEXTRA/qPOLICY, year counts and clock/coverage limitations. No selected-return profit/t,
Sharpe, stopped paths or account tests. Existing2018–22 book P&L is necessarily interpreted to form
this feature; this is not a new protected strategy evaluation or a look at2023+.

FEATURE upper-bound support needs >=100 post-warmup known dates,>=50 active feature DAYS spanning
>=3 design years,>=95% known post-warmup fraction, nonconstant known mask, all source/clock checks.
These are potential dates, NOT VB tickets or proof any active date has a signal. If support fails,
close H10 with0gross/0economic; do not open raw prices or finish economic adapters. The50-day minimum
reflects independent-date power, not contract-duplication. Planning example only: assumed100USD SD
with50independent tickets requires≈28.3USD net mean for t2; actual count/SD/mean are unknown.

## SOURCE, literal parent and gross-before-stopped order

Only after committed FEATURE PASS and its independent review: explicit NQ day+overnight2017..2022
files,2017 warmup only,2018–22 design. Bind all12files, hashes, clocks/schema, finite quarter-tick OHLC
ordering/volume>=0 and duplicate/conflict audits before source features; no all-year pickle, proxy/OF
splice, future `g.trading`, missing-entry skip or last-observed-close time fallback. Review/commit
calendar/source/native implementation before any raw price values. Partial past observations retained
as SOURCE_LIMITED; unknown potentially eligible parent dates/decision/held paths globally veto, not
selective removal. Source does not compute stops to identify future reentry membership.

Literal source `apex_strategies/NQ_Vault_Break.txt`, Gitblob a2bfedd0605ad2026ff859aad2245e38dc5fc812:
CT30-minute chart bars; first OBSERVED bar of each new chart date supplies SessOpen. Midnight C0000
contains prior29native minutes. Prior15 stored weekday chart-date true ranges under the literal
DayClose/PrevDayClose guards supply ATR. Noise=SessOpen+.30ATR. Chart-bar(H+L+C)/3×BarVol VWAP
accumulates since that date; preserve the source's intradayTicks/Volume assumption. Do not replace
this with a1-minute midnight open/ATR/VWAP or choose a favorable history convention.

Normal decision closes1000..1400 every30minutes (strictly before1430); early1000/1030 (before1100).
Long only when Close>Noise and Close>VWAP, next exact native OPEN. One position, max3 tickets/date.
Active75point stop,40point target; normal exactC1430 flat, earlyC1130. Freeze literal source holiday
predicate plus the existing normal/early/closed source-calendar adjudication before prices; report
differences, do not infer holidays from missing bars. All Apex exits<15:59CT; no overnight parent.

SOURCE counts the FIRST qualifying proposal/date independently of stop/target results. Require
>=100 base first-proposal dates,>=50 active selected dates across>=3years,>=95% feature-known on
base dates, all critical proposals/exactentry/fixedendpoint/held paths resolved,>=1000 matched masks
and a variable cell. Matched cells=design year ×first-proposal decision bucket[1000,1100),[1100,1200),
[1200,1430), early flag. Unknown fixedEXTRA0. Count combinations before returns; no pooling/threshold
rescue. Later draw1000 UNIQUE within-cell selected-date masks,seed2026102710,max100000attempts,
preserving active date counts. Keep actualIDs/daily paths; diagnostic allocations are not funded paths.

Raw cheap screen: FIRST proposal/date only, rawnextOPEN→exacttime-flatCLOSE, signedlong×2USD/point,
no stop/target/fees. Save all/active/omitted counts,total,mean,SD,SE,t byyear andlong;short0/N/A.
**COV_EXTRA first/day gross mean>=4.48USD**, twice worst regular MNQmarket RT2.24. Failure closes
H10 with1gross/0economic. All later qualifying raw windows, if saved, are overlapping DIAGNOSTICS,
not executable trades or independent evidence. FIRST/day is a cheap gross reference, not the later
max3 protected strategy; never run stopped transit in SOURCE and call it outcome-free.

## Native protected design, matched allocations and immediate book gate

After gross PASS only: shared grid/bars/execute/_walk with reviewed native adapter, recompute actual
position/stop/target/cap3 reentries. Each frozen day mask applies to every admitted parent ticket.
Executed entry=rawOPEN+.25primary; stop/target anchor to executed entry. Entry-bar and later gaps use
worse RAW observed OPEN, never a favorable nominal stop after adverse entry. Target needs1NQpoint
trade-through, no target adverse market tick. Exact native fill USD at2/point,1.24commission per
contract/ticket; primary .50entryslip and .50market/stop exits. Target-cost RT1.74; market/stop2.24.
Do not double-charge entry slip from an already executed-entry anchored stop. Four-tick stress uses
1point adverse entry/market/stop exit and its own anchored levels,5.24marketRT/3.24targetRT. No rescale
of an NQnet result, spread/latency guarantee or whole-contract liquidity assumption hidden as a pass.

COV_EXTRA design:>=50active dates,positive total,trade t>=2,dailyNW5>=1.5,PF>=1.2,>=3positive years,
positive excluding each individual year,positive EXTRA stress; POLICYpositive. Long-only inherited;
report long/shortN/A,byyear,winrate,Sharpe,Sortino,PF,Calmar,Ulcer,maxDD,t,NW5,active-date counts,
raw/stopped/cost bridge and breakevenextra cost. AllBASEq1tickets stay inPOLICY. Save all/kept/omitted
EXTRA-opportunity profits and omitted t even when positive; this is allocation, not a claim that removed
existing trades lose money. Require EXTRA to strictly beat both totalprofit andmaxDD on>=951/1000
fixed matched-date allocations: (1+#nullprofit>=actual OR nullDD<=actual)/1001<=.05, ties fail.

Immediately after design PASS, BEFORE more robustness, use CURRENTpersonal19 on identical design
dates/nativefee1.24 and fixedpublished1.04diagnostic, whole contracts. Shared5000paired252-day/20-day
block MC,seed2026102710. BASEpublished, EMPTY=BASE−wholeVBslot, ADD=BASE+causalEXTRA,
REPLACE=EMPTY+causalPOLICY. Controls: EMPTY+causalBASE_Q1,EMPTY+causalCONST_Q2,BASE+causalBASE_Q1.
Separate proxy-versus-causal-parent execution differences from allocation alpha. An eligible ADD/
REPLACE must beat BASE,EMPTY and corresponding constant-size implementation/exposure controls in
historical annualprofit/maxDD,medianMCannualprofit/medianmaxDD,medianannualprofit/DD95; positive paired
medianprofit differences. Show absoluteDD95 and intervals; no seed/leg/fee selection.

Published-book fees/reentries/mark/version/coverage uncertainty remains. Known VBmax3 fee-undercharge
arithmetic alone does not bound Twin/mark/coverage uncertainty. Unsupported envelopes mean LIMITED,
not a certified candidate, even for nominal improvement. Funded50K/150K and evaluation claims require
valid current-definition joint intraday paths; daily proxies cannot establish pass/payout benefits.

## Only selected historical validation, placebos and promotion

If design/book survive, COMMITCOV_EXTRA/POLICY plus matchedBASE_Q1 selection before only selected
rule/control runs2023+once, explicitly previously seen historical validation. Do not read baseline
future P&L during design. OTcoverage ends2026-07-07; full jointly known dates stop there unless a
new independently admitted source extends it. Later zeros are not verified no-trades. State exact
2018–26 tested endpoints and any inability to support the requested full window.

Same-exit random-side and random-time each requirep<=.05,1000retainedpaths,seed2026102720. Randomside
uses original causal price-proposal stream on active feature dates, independent uniform signs, same
75stop/40target/flat/cap3/protection and nativecost; reexecute membership to prevent overlaps. Randomtime
uses ALL known active feature dates, not future-VB-signal membership: draw3 distinct eligible30minute
decision clocks/day uniformly, sort, use long direction, same caps/exit/native engine; no signal filter.
Earlydates have2eligibleclocks and drawboth. Compare totalnet on the common fixed feature-date universe,
report differing executed counts, gross and fees. Require BOTH total-net p and per-executed-ticket
net-mean p<=.05 for EACH family, using(1+#null>=actual)/1001. A zero-ticket/undefined-mean null blocks
interpretation; no count/outcome-based redraw. Thus extra null fees from more trades cannot alone
qualify the candidate. Missing possible paths block the test, never redraw on returns. These are diagnostic null positions, not adopted book legs. Their exact
reviewed implementation is committed before validation values; no favorable recipe after results.

Pre-MNQlisting NQ-price/MNQ-cost history is counterfactual research, not historical MNQfills; the
shared quote grid does not certify micro spread/liquidity. Full incremental EXTRA itself must clear
trade t>=metrics.t_threshold(currentN_items326≈3.609533)
OR DSR>=.95, positive2018–22 and2023+, dependence/selection/family controls and a FRESH independent
raw-spec rebuild before promotion. POLICY/oldparent/selectedunadjustedt cannot substitute. Reconcile
native ledger/daily totals, side/year/source/calendar/entry-bar/target/gap/holiday audits and book
uncertainty. Only a fully passing piece gets a Codex PowerLanguage draft for Claude, no deployment.

## Budget and reproducibility boundary

Before registration5/60economic evaluations,9/10hypotheses,4gross screens plus65archivedt6. This
committed plan registersH10as the FINAL allowed hypothesis. Finish this frozen final question as its
gates permit, start no11th. FEATURE/SOURCE rejection adds0gross/0economic; raw1gross/0economic;
all five actually run stopped definitions add5economic; validation selected/control each adds1 if
newly evaluated. Never erase controls/failures, prior selections or partial attempts. At completion of
this final hypothesis (or60economic first), save complete bounded summary and PAUSE continuation
`6adea9fee9c88191a45399d233743746`. Do not resume t6 or its paused watcher.

Codeonly `analysis/codex_hunt_v2_vb_cov*.py`; outputs/cache
`analysis/outputs/codex_hunt_v2_vb_covariance/`; final report
`agents/codex/results/hunt_v2_vb_covariance.md`. Exclusive lock, write-once attempts/markers, exact
prereg/source/code/dependency/input hashes, date-before-value split, runtime versions and run clocks.
No data on import/invented fixtures. Write onlyallowedCodexpaths, preserve others/untracked work,
fetch/pull safely beforepush. No shared rankings/plans/rootTODO/otherbranch,PR2,live/VPS/broker/API/
Rithmic/Apex/settings,purchases/paiddata/accounts/trials/externalmessages,stoppedweb/403retry or
submitted-template execution. Routine rejected/support results keep notification_eventnull; budget
completion summary/pause is separately recorded, without a fabricated candidate or phone-delivery claim.
