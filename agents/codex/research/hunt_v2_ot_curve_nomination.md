# OT conditioned on lagged volatility shape: eligible conditional question

Decision: **TEST for a finite source-and-gross preregistration**, not data admission or a promotion.
The exact current OT-specific VIX>VIX3M gate was not found in the inspected definitions. This is a
conditional book-filter question in a heavily selected fear/overnight family, not a new standalone
forced flow. Its fixed sign must not be reversed if backwardation is rare or unsuccessful.

Source-only,2026-10-26. Read instructions/task/progress and current ranking/source definitions.
Latest read-only source is073e27ca7f0338aba2f771aeccb20c6eba0b1a41; root reports its changes from7f0800f
are operational files only, not inspected here. All relevant research/ranking/book/data definitions
remain byte-identical to7f0800f. Work stays codex/work; no operational body was opened or changed.
Program checkpoint3/60economic evaluations,4/10hypotheses,2gross screens; archivedt6=65. This review
adds0/0/0. No actual data/price/OF/trade/workbook/cache rows or new return was read/calculated. Only
source/docs, file presence/size, Git metadata and the VIX3M header were inspected. A helper checked
the narrow prior-definition question independently, also without data or execution.

## Exact adopted parent

|Pinned source at073e/7f|Git blob|SHA256|
|---|---|---|
|funded_strategies/NQ_Overnight_Tick_VIX.txt|00f4702cdc73a6cf11fc89aa3bc0d20c953731f6|f74269c71706bb79cbaaa3fb8d18d408e515db15f76f9739ecb3bb0c2da9866a|
|checks/candidates/overnight_tick/NQ_Overnight_Tick_VIX.txt|e727ba9d91d6e4a56c1df739c51b68af5a9703c4|60e1cb009fc25c27a6f579ea63009570977757cea2830945983a8e8ece885a4e|
|analysis/overnight_tick_test.py|2999a1bd70c2d22252d4bcc9c20a703a57315259|d9e9fc050cd721f3b86a4aebc87b7482aea5b3d1331e5bc1c3d187038d12cecc|

The funded copy differs from the checked candidate by a6-line adoption/header block; strategy body
is unchanged. Current personal19 uses1MNQ,50K funded1MNQ replaces Monday Long,150K funded2MNQ adds
alongside Monday Long; evaluations do not adopt OT. Future aggressive personal weights are not current.

Parent chart is5-minute CT close-labelled NQ/MNQ, IOGoff, VIXdaily Data2. RTH is Time>08:30and<=15:00;
the first observed RTH bar supplies Open, the last supplies Close/RTHLast. A session must be down and
not early, where the literal early condition is RTHLast<14:00. This is not a NYSE holiday-list gate.
`TickRSV=(UpSum-DnSum)/(UpSum+DnSum)` over Time>14:15and<=15:15. On a1-minute source reconstruction
the exact60bar labels are14:16..15:15(j856..915), or15:16..16:15ET. Header prose saying'14:15–15:15'
must not accidentally include a61st source minute. True total is upvol+downvol; OFvolume is up-classified
quantity, not total. A price-direction volume proxy is a known different, weaker prior model.

When the RSV window ends, the source freezes StateDown/StateEarly/StateHasRSV/StateRSV and an unused
session state. At the first evening bar Time>=17:05 it consumes StateUsed **even if Pass=false**.
Pass requires down, not early, positive aggregate RSV quantity and either negativeRSV with VIX(D)>
its25daily-closeSMA, or nonnegativeRSV with VIX(D)<=SMA25. D is the triggering RTH date. No alternate
SMA length, cell or source-proxy nomination is allowed. No inherited20-night range warmup is needed
for the optional disaster stop because **UseDisasterStop=false**: the adopted parent has no stop/target.

Normal5-minute decision17:05 issues next-bar market, whose labelled17:10open is wall17:05; the
1-minute reference is OPENj1026(label17:06). Exit decision03:00 issues next-bar market, wall03:00,
native OPENj181(label03:01). Long1wholeMNQ initially, at most one decision/trade per RTH session.
Friday normally carries to Sunday; rare holiday carries can be longer under the source's'next evening'
state rule. The saved checker documents Christmas/Good-Friday cases. Reconstruct the observed source
state rather than forcing every D into D's evening or simply looking back four calendar days.
The curve gate must consume the same decision even when dropping a ticket; it cannot free a later entry.

Native gaps/endpoints, the first RTH open/last close, RSV completeness, daily VIX25-close warmup,
Data2date, pending state and next evening/exit clocks all need frozen audits before returns. The old
maker's partial sums/first-finite endpoints/last-bar inference are not certified complete source paths.
Do not impose H04's infinite EWMA uncertainty on this different parent or rerun H04. Conversely, do
not hide real OT gaps. The published roll detector selects large jumps retrospectively; the saved
checker reports zero detected switches inside its OT holds, which is source context, not an authority
to delete newly inconvenient nights. Freeze a causal contract/roll calendar or retain unresolved
contract paths as source-gate failures; a price jump must not become a convenient roll exclusion.

## Prior definitions and required controls

|Source|Already examined definition|Consequence|
|---|---|---|
|analysis/vix_regime.py|eVRP×curve on VB/ONB/OD/OND; optional trueVIX3M input, otherwise VIX>1.10*SMA20 proxy|OT is absent, but do not falsely call all prior curve work proxy-only; source conditionally uses the real file|
|analysis/vix_sleeve_test.py|TrueVIX/VIX3M×VRP multi-day VIXY long/short/cash sleeve and personal addition|Same data family, different instrument/exposure/clock; failed book case remains prior evidence|
|analysis/overnight_tick_test.py; replica/verdict|Current OT interaction, fiveVIXlengths, alternate barRSV, shuffled regimes, lagged parentVIX sensitivity|No true term-shape gate found; author≈30unknown variants and selected cell/length remain material|
|analysis/ond_sentiment_filter_test.py; overnight_sentiment_vote_test.py|OND/other overnight models with VIX/price MAs; later inverse'fear' cuts|Known result-informed fear-night ancestry, not a fresh discovery or validation|
|analysis/overnight_anomaly_test.py; overnight_round.py; existing rebound study|Different entry/exit/stop/down-day/roll definitions|Do not port or tune those windows, borrow their outcomes or relabel a filtered copy as independent alpha|

The new predictor is the **same-date difference between30-day and3-month SPX implied-volatility
indices**, not a front-VX futures curve, calendar-spread return, observed insurance order or measured
dealer position. Its incremental value must survive the existing parent RSV/VIXcell, lagged spot-VIX
level/regime and own down-RTH move controls. Price/level-matched subsets are essential; a selected
backwardation mean is insufficient. No economic output file was opened for this source comparison.

## Single prospective curve date/sign, before values

For parent RTH dateD, letF1andF2be the latest and second-latest **expected** Cboe/USindex daily sessions
strictly beforeD, from a prebound historical calendar. Require both to be full ordinary sessions for
this conservative clock policy; an early/unknown expected session makes the curve state UNKNOWN.
Do not walk farther back to replace it, choose the second available row, forward-fill or align either
series to a different date. For a normal FridayD/Sunday entry, F2isWednesday, not a date selected from
Sunday's calendar or from the latest data seen at Sunday entry.

At fixedF2use matching positive finite CLOSEs only. KEEP_KNOWN iffVIX(F2)>VIX3M(F2). Equality and
contango DROP_KNOWN. Missing/invalid/mismatched dates, unclear calendar or source provenance remain
UNKNOWN KEEP; they are not observed backwardation. Unknown parent OT state is a different problem:
it remains unresolved/admission-failing, rather than becoming a newly invented parent ticket.

The F2daily feature is deliberately at least one complete intervening full session older than D.
An allowed research clock would assign availability only afterF1's completed close, then decide at
D's original evening time. This is a **conservative publication/processing assumption**, not authenticated
historical receipt or original as-published vintages. It changes the question to persistent prior
stress, not a real-time measurement of the latest close's urgent insurance orders. If the later source
audit contradicts this order/identity or a known revision creates leakage, stop. Do not tryF1/currentD,
flip to contango or relax availability after seeing counts/returns.

Use one fixed unselectable level control, same F2: KEEP iffVIX(F2)>its25daily-closeSMA throughF2,
UNKNOWNKEEP. Match subsets on year, source-knownness, parentRSV/VIXcell and prespecified spot-level/
cash-RTH-move strata. Root must freeze their exact bins/calendar/unknown rules before data, not select
them from profits. A five-model ceiling can fit BASE/CURVE/LAGGED_LEVEL plus a conditional matched
activation-delay BASE/CURVE pair; PUBLISHED stays source/entry reference only, not a sixth standalone
financial model. Published-book versus replay accounting remains an explicit later bench control.

## Inputs: actual presence, provenance claims and limits

|Input|What was verified without values|What is not verified|
|---|---|---|
|Native NQDAY/ON,OF|Owned2018..22filenames present, including ON2017 and OFparts; only names/sizes inspected here|Actual held gaps, source clocks/rolls, selected windows/aliases/receipt, MC-entry parity|
|LocalVIX_daily.csv|Present321,423bytes|Different from latest fetched version; do not assume its dates/values are interchangeable|
|Latest-sourceVIX_daily.csv|Gitblobd4101774924ca7d55dd67d014de2e43aaaac3b5e,325,278bytes|Original fetch/receipt/vintage binding and actual required daily coverage|
|Latest-sourceVIX3M_daily.csv|Gitblob0deb965a89bf3ef27ff6e54893e1f97a8c87b20e,148,859bytes; headerDATE,OPEN,HIGH,LOW,CLOSE; absent localroot|Actual required dates/values, historical identity/schema eras, original fetch/receipt/revisions|
|Cboe provenance|Owned vix_sleeve source explicitly calls both daily files Cboe; VIX producer-source points to official history endpoint|This is not a retained authenticated VIX3Mdownload/response or exact historical publication log|

Archive **both** daily series from the same pinned source into allowed Codex inputs before loading
values. Do not overwrite the local file, mix the older local VIX with a newer VIX3M, or cherry-pick a
version by performance. Header/date/range/duplicate/conflict checks and all2018–22pluswarmup source
bindings must precede features. Data2VIX(D) and its25-closeSMA still belong to the unchanged parent;
the new lagged curve does not magically authenticate the parent's current-day feed.

Source-only independent VIX provenance cross-check: `datasets/finance-vix/README.md`, fetched as text,
blob9325d3a51a9118d399652bf8747e13675a491448, cites Cboe's historical page and official daily URL
`https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv`. No CSV was fetched from it.
The README also explicitly lacks a clear publisher-license statement; its PDDL attribution is the
secondary maintainer's judgment, not a Cboe redistribution grant. It does not verify VIX3M or publication
time. VIX3M's official historical-source/methodology binding remains a specific admission item, not
an invitation to fetch blocked hosts, buy data, create an account or pretend exact receipt is known.

## Power and smallest next step

Backwardation can be uncommon. OT already selects down days and its two RSV/VIXcells, so a broad-market
backwardation frequency cannot estimate this conditional count. No selected count was measured. Freeze
a minimum kept count before data;100is the preferred cheap gate, and this nomination explicitly accepts
failure there without inspecting endpoints or expanding windows. For assumed per-event SD100USD/MNQ,
n100needs net mean≈20USD for t≈2, n50≈28.28USD, plus2.24cost. These are planning assumptions, not observed
SD/power/promotion. Dependence and the inherited selection history make effective information smaller.

Root may now write/commit a finite plan plus source-only/synthetic-reviewed entry reconstruction,
fixed calendar/curve/parent state, native costs and the actual count/source gates before new rows.
Admission must precede raw endpoints; gross mean>=4.48USD/MNQ before full timed-leg evaluations.
Because adopted OT has no stop, the timed design is not an excuse to invent one or optimize brackets.
Filters still require totalBASE/kept/removed profits, negative removed profit and1000matched subsets;
per-trade improvement alone cannot pass. Immediately after design PASS use current personal19BASE,
ADD, OTslotREPLACE and EMPTY at whole contracts/paired1yearMC, with native fee/reentry/mark/coverage
uncertainties predeclared. Existing OTconstant-adverse account paths are not valid joint chronology;
no funded/evaluation improvement may be invented from them. Commit selection before selected rule/
matched control2023+once, then all standard promotion/placebo/dependence/independent-checker gates.

Nothing here resumes a closed study, changes a watcher/automation, claims a result/phone delivery or
registers H05. TEST is the ability to freeze this conditional question, not a prediction that it passes.
