# Frozen pre-open absorption screen

Summary: One new signed-flow/price candidate, three comparator definitions and a fixed delayed replay; five cases.
2018–22design only until all registered gates pass. No fitted ML, parameter scan, source repair or optimization.
Record source-data uncertainty and prior selection, not a claim that academic microstructure implies NQ profits.

## Scope, files and clocks

Evidence: agents/codex/evidence/preopen_absorption_20261108.md. Inputs: the five transferred native2018–22files
and their hash manifest at f8cd198. Check both compressed/original hashes, header, rows, quarter tick, OHLC,
nonnegative integer quantities, total=buy+sell, chronological/unique timestamps. No return statistics before
source admission. Use ET close stamps -> timezone-aware CT; no extra minute. Never splice another price feed.
Owned fe35af99 NQ daytime files supply calendar dates only; hash those inputs. No full-grid/cache persistence.

Event date=CT morning date. Night starts previous calendar date17:01; observed first OPEN through current08:28.
Exact nominal cutoff is928slots: previous17:01 through08:28inclusive. Require at least
ceil(.9*928)=836observed closes and observed ending08:28. Missing bars are not volume zero. First observed
night minute may differ from17:01; record its timestamp, do not invent a fixed opener. Current last15bars
08:14–08:28must all have finite OHLC/buy/sell/total and positive aggregate volume. Nightmove = C08:28−firstO;
nonzero direction n=sign(nightmove). At decision, calculate delta15=sum(buy−sell)/sum(total). pressure=abs(delta15).
Past pressure median uses previous60valid observations (minimum20), updated AFTER today's feature assessment.
Night-volume median uses previous20valid nights (minimum20), also excludes today's observation. Prior histories
update from all valid decision windows, including nontrading roll-calendar dates; no return-selected history.

ADR20=mean(H−L) of previous20complete native RTH sessions08:31–15:00CT: require all390observedOHLC bars
and valid first/last anchors. This is the inherited T daily-range estimator, not true-range ATR. Today is appended
only after calculating today's known ADR. No2017native warm-up: first valid events start openly later in2018.

Admission: nonzero nightmove, finite known histories, weekday/source trading-calendar date. Skip dates5–21
in March/June/September/December as a causal conservative roll precaution. No largest-future-gap adjustment.
Require finite OHLC on08:30–08:45inclusive for common normal/delay execution; unknown path is an explicit
research admission exclusion, not future-data knowledge usable live. Record all excluded calendar dates and
retain their zero cash in daily ratios; report coverage, warm-up and stress-period exclusions. No data repair.

## Five fixed definitions

1. PlainFade: fade n on every admitted morning.
2. PriceOnly: PlainFade when n*(C08:28−O08:14)<=0 (recent price stalls/reverses relative to overnight direction).
3. HeavyTotal: PlainFade when native night total >1.4*median(previous20native night totals).
   This is a comparator using verified TOTAL volume, not exact native T_ONESIDE UpTick classification.
4. Absorption: PriceOnly plus n*delta15>0 AND abs(delta15)>=median(previous60pressure observations,min20).
   Thus aggressive trades persist in the overnight direction while last15-minute price progress does not.
5. Absorption_delay1m: unchanged Absorption decisions/sides; entry delayed1minute, not selectable.

No combined alternative between HeavyTotal and Absorption, no post-hoc weekday/side/threshold variant.
Only Absorption is eligible for selection; other rules expose what price and plain activity already explain.

## Orders, costs and path

Feature cutoff08:28close, one completed minute for assumed receipt/processing. First executable fill
08:30-labelled OPEN=08:29civil CT. Mandatory delay08:31OPEN=08:30civilCT. Fixed exit08:45OPEN=08:44civilCT,
queued market exit wins at its OPEN over that bar's intrabar stop. Stop distance=.40*ADR20 from raw entry;
round sellstop down/buystop up to.25; active on entry bar. Adverse gaps fill at worse of stop/open. No targets,
BE, trail or re-entry; side fixed, one position. Source-style risk levels unshifted; costs separate cash bridge.
NQgross=(rawexit−rawentry)*side*20, net=gross−7.25−10. NativeMNQgross/10−1.25−1. Extra1tick per leg fee
stress subtracts another$10NQ/$1MNQ from the same trades; it does not silently reanchor stop geometry.

Before market replay, synthetic fixtures verify long/short, entry stop, gap stop, stop rounding, scheduled
OPEN priority, delayed-entry anchoring, one-minute clock and native costs. Common-date side/entry/exit/net
must exactly match for nested filters. Daily/gross/net/fees/native sums reconcile to half a cent.
Save features/exclusions/counts/power receipt BEFORE pricing. Run metadata audit before --phase design.

## Cheap design gates and stop

Absorption must satisfy ALL:
- >=30trades, positivegross/net, trade-meant>=2, PF>=1.2, >=3positive calendar years;
- net >PriceOnly AND net >PlainFade; DD<=each, Sharpe>=each on common full calendar;
- pure nested filter versus both parents; removed trades negative total and t<=−1 in each comparison;
- 1000within-year matched-count random subsets: profitexceedance<=5% AND DD-no-worse share<=5% for each;
- candidate-minus-each-parent annual moving20-session bootstrap(1000,seed20261108) P5>0;
- delayednet>0 and extra1tick/legcostnet>0.
Report HeavyTotal for source context, never select it from this study. The signed-flow incremental gate against
PriceOnly is primary; ratios or average trade alone do not waive the total-profit/removed-trades gate.
No promotion from this cheap screen. If any gate fails, stop recent/placebo/accounts/PowerLanguage; preserve all
five cases and prior failures. No rescue with different clocks, warm-up, missingness, side, direction or costs.

## Earned later stages

If design passes, freeze selected Absorption before acquiring/pricing matching2023–2026-07-07native data;
those bytes have not been supplied here. Same recent gates with>=20trades and>=halfyearspositive; full-t clears
metrics.t_threshold(max(500,TIERitems+5)) AND DSR>=.95; already-seen history is replication, not a fresh holdout.
A real replayed random-direction control must be beaten at95thpercentile;5000-run10daybootstrap/permutation and
native-size MonteCarlo follow. No manual upside/downside carveout. A failed stage stops all dependent stages.
After independent/native-data review: then-current eval/funded50K/150K/personal BASE/ADD/REPLACE/EMPTY at actual
integer1MNQ first, Tfade replacement (overlap), actual native fees, chronological joint marks and payout/risk/timing.
No inferred safe size from closed-trade DD; no book benefits until bench. Native ticks/receipt/roll metadata needed
before live readiness; success on uncertain continuous bars would remain conditional research.

Outputunder analysis/outputs/codex_preopen_absorption_20261108; code/plan/input/dependency/package hashes and
all cases retained. Do not alter plan/TIER, native exports, live/VPS/broker/APIkeys, other branches, scout/schedules,
existing failed programs or paid-data entitlements. Push codex/work only. Show direct results in chat.
