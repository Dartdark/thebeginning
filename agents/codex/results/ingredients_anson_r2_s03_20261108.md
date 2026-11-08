# Anson, R2Vault and S03 v2: WATCH — ingredient grids completed

Summary:
Completed15 frozen definitions, first design history and then unchanged recent replication.
Anson's direction/strength gate matter; R2's R² vault rule helps; S03's entry band matters more than entry VWAP.
S03's stop is protection: recent daily DD is$21,951 versus$41,219 without it, despite a lower average trade.
No changed strategy, side selection, new combination, account admission or trading-plan change is earned.

Plan: [`ingredients_anson_r2_s03_20261108.md`](../plans/ingredients_anson_r2_s03_20261108.md), **7320764**, before returns.
Implementation-only amendment: [`syntax/fixture record`](../plans/ingredients_anson_r2_s03_20261108_implementation.md), **65de599**.
Design checkpoint **70e5d0a** precedes recent replay. Evidence: [`ingredient sheet`](../evidence/ingredients_anson_r2_s03_20261108.md).
Script:`analysis/codex_ingredients_anson_r2_s03_20261108.py`; aggregation:`analysis/codex_ingredients_anson_r2_s03_report_20261108.py`.
Output:`analysis/outputs/codex_ingredients_anson_r2_s03_20261108/`. Trials: **15 definitions**, five per family;
eight partial-design cases were repeated for implementation verification, not new economic definitions.

## Rule (as tested)

The user requested a Change / $ a trade / t / Read grid. We use Anson's intended4.5/20 with the existing early
adapter, R2Vault's **CT intraday-adapted** model, and S03v2's0.4-sigma stop with its intraday guard. These choices
were registered before this round. R2's stronger published raw overnight model is a different baseline and is not
silently substituted. Earlier failed placement decisions remain intact; this is component attribution, not a rescue.

| Family | Original rule |
|---|---|
| Anson | NQ5-minute observed bars; close−close12bars ago, divided by mean range of prior20bars; strength≥4.5; follow direction, flat only,08:30–14:30CT; next chart-open entry,20completed-bar/14:55 queued exit, early11:30 adapter; no stop/target |
| R2Vault | NQ5-minute576-close OLS; R²≤.030 refreshes persistent vault; positive slope, buy stop above vault high+.20range; ≤3filled entries/date;75point stop/40point target, one-point target-through; CT09:30–15:30 entries,15:55/early11:30 flatten; no BE |
| S03v2 | NQ1-minute; gap-adjusted band from14 prior accepted same-minute sessions and current total-volume VWAP; check09:00–14:30CT every30minutes; follow beyond band/VWAP; next-open band/VWAP exits/reversals;0.4raw-sigma stop, source15:00 exit plus guard |

All times are Chicago, on close-stamped bars. A labelled minute OPEN is one minute earlier in civil time. Anson's
14:55-close queued exit normally fills the14:56-labelled OPEN at14:55 civil CT. S03's09:00 decision fills the
09:01-labelled OPEN at09:00 civil CT. These source models assume immediate processing, not measured latency.
R2 traverses a deterministic causal minute OHLC path, including only post-entry/pre-exit segments. Targets require
one-point trade-through; stops gap at the opening price. S03's stop is active in the entry minute, rounded away to
a valid tick. S03 source ring-buffer acceptance/zero-history defects and volume proxy remain unchanged.

Design2018-01-01–2022-12-30; recent2023-01-01–2026-10-09.2017 supplies feature warm-up only. All recent history
and prior source diagnostics were already seen. These are historical replications, not fresh holdouts. Each era
starts flat, with historical features/vaults retained; no case is left open at either endpoint.

Raw data/Grid24/early calendar are pinned to`fe35af99aa90d7f31b91f8693859251bb44dd9ab`; retained research engines
and supplied source/spec to codex/work`4d88f53` (full hashes in`sources.json`). No persistent research cache was built.

**Costs/units:** net per fixed **one NQ**, $20/point,0.25tick,$7.25RTcommission plus one adverse tick on each
market/stop fill. Anson/S03 normal cost$17.25; R2 target trades$12.25 because the exit is a limit. Slippage is
charged monetarily on the source raw fill geometry, without a new bracket re-anchoring/latency replay. MNQ
sensitivity uses one-tenth price/slippage dollars and **assumed$1.25RTcommission**, not a broker quote. Additional
cost stress adds one extra tick per market/stop fill on unchanged orders. No compounding or sizing search.

Earlier reports used$1.04/MNQ-equivalent commission, i.e.$10.40 per NQ before slippage, and some account tables
used a filtered common-date universe. These grids use$7.25 standard-NQ commission, all source events, the owned
2017daytime warm-up and the explicitly named intraday baselines. Do not splice their means/counts with old tables
or call a changed unit/universe an economic improvement. Native MC/author parity is not established here.

## Results — requested grids

**Each pair below is design2018–22 / recent2023–2026-10-09.** Dollar cells are average net per trade, not annual
profit. Trade t is descriptive; paired20-day-block uncertainty and total profit/DD inform the Read column.
Baseline side rows are actual contributions within the both-side stream, **not side-only strategy reruns**.

### Anson

| Change | $ a trade | t | Read |
|---|---:|---:|---|
| As is: strength4.5, hold20, early adapter | $50 / $166 |1.24 /1.99|Base; positive but weak standalone evidence |
| Fade momentum instead | −$85 / −$201 |−2.09 /−2.40|Following is better in both eras; both paired directional intervals exclude zero |
| Remove strength/range-magnitude gate | −$30 / −$34 |−1.70 /−1.06|Key policy ingredient: ungated versions lose in both eras |
| Hold6 bars instead of20 | $16 / $81 |0.75 /1.78|Longer hold adds net in both eras, but timing-effect intervals remain wide |
| Remove early-close adapter | $50 / $165 |1.24 /1.97|Tiny/conditional profit effect; raw version produces6/5 late fills versus0/0 |
| Baseline long trades | $90 / $212 |1.62 /1.88|Stronger contribution than shorts; still uncertain, post hoc |
| Baseline short trades | $16 / $125 |0.28 /1.02|Weak evidence; this is not a short-only deployment test |

The strength gate's whole-policy net advantage is **$215,453 design/$271,452 recent**; both annual paired lower
bounds are positive. This is not an exact deletion of losing trades: removing it changes occupancy and later
signals. It also removes most magnitude/range normalization from selection, while keeping valid-history/range guards.

Hold20 adds$34,842/$46,940 versus hold6, but recent daily DD is$39,256 rather than$31,533. Both timing-effect
intervals include zero. A different horizon changes subsequent entries; the difference is not a separately
tradable return from minutes30–100. Momentum12/range20 and the ordinary window are held fixed, not proved optimal.

The early guard gives up$146 design and adds$1,437 recently. Its raw alternative has one recent cross-date trade,
11 late fills across eras and much more uncertain held coverage. Near-equal average profit does not make an
operational guard decoration. The original has no stop: recent worst trade is−$11,057 and its worst observed
source adverse mark−$16,122. Range-normalized entry strength does not create constant dollar risk per contract.

### R2Vault

| Change | $ a trade | t | Read |
|---|---:|---:|---|
| As is: CT vault/slope,75stop/40target, intraday guard | $24 / $46 |1.02 /1.72|Base, long only; neither era establishes a strong standalone edge |
| Fade the upward trigger, mirrored bracket | −$70 / −$59 |−2.82 /−2.14|Up-break direction helps; both paired directional intervals are positive |
| Refresh vault every bar: no R² gate | −$15 / $27 |−0.63 /1.06|R²-based vault selection helps both eras; recent advantage remains uncertain |
| Remove positive-slope gate | $24 / $19 |1.18 /0.82|Conditional: original gate gives up design net and adds recent net |
| No stop; target and flatten retained | −$14 / $24 |−0.36 /0.47|Protection matters: recent DD$23.6k→$76.7k; worst trade−$24.1k without stop |

The fade shorts **at the original upward trigger crossing**, not at a downside-break signal. A pre-entry low is
not its target or held risk. Both variants then regenerate entries/exits under their actual mirrored brackets and
daily limits. This is a conditional causal-cursor comparison, not a literal sell-stop order above the market or
verified instantaneous live reversal execution.

The R² vault-update rule adds$57,009 design/$23,517 recent relative to refreshing on every bar. Only the design
paired lower bound is positive. Low R² measures absence of a linear fit, not automatically low volatility or
observed institutional accumulation. This experiment does not identify such a causal actor.

The positive-slope gate gives up$14,163 design and adds$28,603 recent; both intervals span zero. It lowers DD
relative to the broader rule in both eras, but is not a persistent source of additional total dollars. A near-equal
design average hides the lost total profit when fewer trades are taken.

The stop adds$51,949/$37,425 in net and reduces DD in both eras. Its recent profit interval is still wide, but the
tail result is material: worst realized loss−$1,517→−$24,147, worst observed adverse mark−$1,517→−$26,952 without it.
Buffer.20,target40,lookback576 and cap3/day were not isolated or optimized. Original has no short leg; its only
short experiment here is the deliberately registered fade. Earlier no-placement/rejection results remain intact.
Its source R² exit threshold2.00 cannot trigger on bounded0–1 R², and BE is already off; neither is a separately
priced return contributor in this round.

### S03 v2

| Change | $ a trade | t | Read |
|---|---:|---:|---|
| As is: band+VWAP entry,0.4sigma stop | $112 / $132 |3.82 /2.12|Base; clearer design evidence than Anson/R2, weaker recently |
| Fade direction; preserve virtual-source exit decisions | −$75 / −$78 |−4.85 /−2.62|Continuation direction matters; both paired intervals exclude zero |
| Remove entry VWAP confirmation | $105 / $117 |3.70 /1.96|Small positive contribution, uncertain; VWAP still controls exits |
| Remove entry band crossing; follow VWAP | $10 / −$8 |1.25 /−0.52|Key entry component: recent DD$22.0k→$107.6k without the band gate |
| Remove sigma stop | $123 / $174 |2.99 /1.96|Higher mean hides similar recent total and much worse DD$22.0k→$41.2k |
| Baseline long trades | $107 / $230 |2.98 /2.38|Most recent profit is long; post hoc contribution, not a selected long-only rule |
| Baseline short trades | $117 / $39 |2.53 /0.50|Short contribution weakens recently; no automatic side removal |

S03's fade tracks a virtual follow-direction position for signal/band decisions, while actual position/stop are
mirrored. Naively using the long-follow exit rules on a high-band short would mechanically alter the meaning of
the experiment. Price-dependent stopouts still change later occupancy, so schedules/counts need not match.

The entry band adds **$74,562 design/$179,116 recent** in whole-policy net. The recent annual-effect interval is
positive; the design lower bound is about−$615/year. Removing entry VWAP gives up$3,760/$9,155; both intervals
include zero. That makes entry VWAP a smaller, uncertain contributor rather than proof of no effect. VWAP and
bands remain in the exits of both entry-gate interventions; this does not test removing either indicator entirely.

The stop adds$19,557 design but gives up only$1,118 recent total net: **$132,191 with stop versus$133,309 without**.
The no-stop recent average rises partly because its trade count falls1,004→765. Recent DD rises$21,951→$41,219,
and worst realized loss−$2,027→−$6,477. This is risk shaping with reentries, not a fixed-trade average improvement.
History14, gap anchor and30-minute decision schedule were held fixed; no best lookback/window was selected.

## Baseline statistics and yearly record

Whole2018–2026-10-09, fixed one NQ, all source events, after the costs stated above:

| Baseline | Trades | Win | Net | Avg | t | Sharpe | Sortino | PF | Daily DD | Calmar | Ulcer |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Anson |2,056|53%|$202,134|$98|2.34|0.77|1.17|1.17|$39,256|0.57|11.39|
| R2Vault |2,857|63%|$100,532|$35|1.97|0.64|0.89|1.09|$23,569|0.47|8.78|
| S03v2 |2,382|30%|$286,506|$120|3.86|1.35|3.07|1.35|$21,951|1.44|2.19|

| Baseline / era | Trades | Net | Avg | t | Sharpe | Sortino | PF | Daily DD | Calmar | Ulcer |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Anson design |1,207|$60,814|$50|1.24|0.53|0.74|1.11|$34,758|0.34|13.60|
| Anson recent |849|$141,320|$166|1.99|1.01|1.60|1.23|$39,256|0.92|11.82|
| R2 design |1,402|$34,286|$24|1.02|0.42|0.58|1.07|$15,250|0.43|9.41|
| R2 recent |1,455|$66,246|$46|1.72|0.87|1.23|1.10|$23,569|0.72|10.98|
| S03 design |1,378|$154,315|$112|3.82|1.74|3.65|1.41|$12,255|2.43|2.20|
| S03 recent |1,004|$132,191|$132|2.12|1.13|2.69|1.30|$21,951|1.54|4.47|

Baseline whole-history side contributions: Anson longs960/$135,830/average$141/t2.46/PF1.30, shorts1,096/$66,304/
$60/t1.00/PF1.09. R2 is long only. S03 longs1,173/$185,021/$158/t3.49/PF1.52, shorts1,209/$101,485/$84/t1.96/PF1.22.
Full long/short Sharpe, Sortino, Calmar, Ulcer, wins and DD for all15cases/eras/years are saved in the phase metrics,
`whole_metrics.csv` and`year_side_metrics.csv`. No side-only simulation or side nomination is hidden in these rows.
Ulcer's$50K reference is a reporting convention, not sufficient capital. DD includes the initial zero-P&L peak.

| Year, marked net | Anson | R2Vault | S03v2 |
|---|---:|---:|---:|
|2018|$24,561|−$4,824|$41,785|
|2019|$11,342|$4,906|$1,101|
|2020|−$15,155|$5,513|$30,280|
|2021|$22,475|$18,268|$23,085|
|2022|$17,591|$10,423|$58,064|
|2023|$17,712|$22,629|$51,983|
|2024|$64,893|$5,720|$18,950|
|2025|$9,552|−$4,569|$42,559|
|2026 through10/09|$49,164|$42,466|$18,700|

Recent original Sharpe5/95% block bounds: Anson **0.25–1.72**, R2 **0.02–1.60**, S03 **0.57–1.58**. Native one-MNQ
whole-history fee sensitivities net$19,134/$8,553/$27,400 respectively. Every original remains positive in both
eras under the fixed extra-tick stress. These are conditional historical estimates, not new portfolio payouts or
proof of survival through an unseen regime. Current account comparisons were deliberately not rerun.

## Placebos, paired evidence and account level

Every entry-gate comparison fails exact nested-trade identity in both eras. Matching uses unique entry-minute
events, not calendar dates with multiple trades. Occupancy, levels, daily caps, stopouts or later opportunities
change; therefore removed-trade means and random deletion of original trades would answer a different question.
No such favorable filter statistic is invented. Saved`filter_controls` mark all five comparisons nonnested.

Original minus intervention annual-dollar5/95% intervals,1,000 moving20-weekday block draws, seed80315:

| Comparison | Design annual interval | Recent annual interval |
|---|---:|---:|
| Anson fade |[$1,112,$61,763]|[$25,314,$133,708]|
| Anson no strength |[$20,189,$67,020]|[$24,169,$117,706]|
| Anson hold6 |[−$2,842,$17,902]|[−$9,768,$31,980]|
| Anson no early adapter |[−$297,$214]|[$25,$644]|
| R2 fade |[$6,186,$44,109]|[$6,317,$63,535]|
| R2 no R² gate |[$4,179,$19,485]|[−$8,400,$24,303]|
| R2 no slope |[−$9,475,$4,931]|[−$3,267,$18,930]|
| R2 no stop |[$261,$18,303]|[−$8,422,$30,976]|
| S03 fade |[$43,809,$84,496]|[$31,568,$103,223]|
| S03 no entry VWAP |[−$418,$1,857]|[−$940,$5,579]|
| S03 no entry band |[−$615,$31,235]|[$20,801,$70,689]|
| S03 no sigma stop |[−$1,323,$8,268]|[−$10,786,$9,620]|

Under the frozen label, all three directional comparisons and Anson's strength gate have stronger historical
contribution support. Anson hold20, R2's R² update/stop and S03's two entry gates add net in both eras but have
uncertain separation. R2 slope, Anson early-adapter profit and S03 stop profit are conditional; risk/operational
usefulness can remain. 'Wide interval' is not proof of decoration. No standalone t or block bound undoes selection.

No additional random-time/side return definitions, optimized neighbors, new account/portfolio or replacement/
empty-slot runs were added. Earlier source placebos/placement results remain in the linked Anson/R2/S03 reports,
with their original costs/universes. These current controls are bounded component comparisons, not a complete
admission suite for any changed rule. A new candidate needs a separate protocol, native checks and current-book
tests before an allocation claim. Prior negative placement decisions are not reopened by relative improvements.

## What could make this wrong

- Source/platform parity remains unverified. Exact wrapper agreement is not an independent source reconstruction,
  native tick/queue replay or MultiCharts certification. R2's timezone is ambiguous in its PDF; this grid freezes
  CT and intraday flatten before prices rather than choosing the best clock. Its raw model is a different rule.
- Missing observations and proxy calendars remain explicit. Original Anson has13/0 unknown held minutes by era,
  R2 has9/0, S03 has0/3. The raw Anson adapter-off case has19/1,140. A proxy label cannot prove a feed outage or
  an exchange closure. No absent opening fill or rescue stop is invented. All source events remain in these grids.
- S03 retains111/52 trades affected by incomplete accepted history in design/recent. Missing ring-buffer cells
  can be zero; cumulative VWAP uses total exported volume, not verified PowerLanguage up-tick/Ticks settings.
  Removing entry VWAP does not remove exit VWAP. These are causal but conditional source-policy replays.
- The source raw continuous prices lack authenticated dated-contract roll/quote metadata. Original intraday
  models have no cross-date trades here; Anson adapter-off has one recently. Actual gap/slippage/roll costs can
  differ, especially for delayed fills or a no-stop variant. Research23:59 weekday marks are not a prop floor clock.
- Every author optimization, source test and prior ingredient round remains selection history. Already-seen2023+
  is not a new untouched test. The grids do not establish parameters as optimal or distinguish all index beta,
  news and state-selection effects from a causal behavioral mechanism.

## Implementation and reproduction

Before prices, retained source synthetic checks and ten intervention groups exercised actual Anson timing,
R2 crossing-cursor fades/infinite stop/slope removal, S03 virtual direction and independent entry-gate removals,
stop activation, calendars and prior-only history. Baseline source parity passes1,207/849 Anson,1,402/1,455 R2,
1,378/1,004 S03 trades. All gross/cost/net, marked daily, side and yearly totals reconcile. Exact source/raw input
hashes, dependencies/versions, feature digests, day audits, event ledgers and marking receipts are retained.

One design attempt stopped before R2 slope-removal pricing because an exact syntax-edit hook lacked AST-printer
parentheses. Amendment65de599 corrected that hook and expanded fixtures, with **no economic-rule change**. Its
eight priced cases remain in`design_attempt_7320764_hook/` and match the completed rerun on entry/exit/side/gross/net.
The original/corrected code and receipts remain committed; the partial run is not erased or called unseen data.

Configured Python:`analysis/codex_ingredients_anson_r2_s03_20261108.py fixtures`, then`design`, then`recent`.
Phases require committed exact inputs and refuse to overwrite outputs; use a scratch checkout with saved results
moved aside intact. The report script regenerates grid CSV/Markdown and aggregate audits from saved ledgers only.

## Differences between MultiCharts code and this test

No new PowerLanguage was written or deployed, and no fresh MC trade list was paired. The source assumptions
above—raw fill geometry, trade-through, immediate processing, total-volume proxy, early adapters and deterministic
intraminute path—are not verified native equivalence. Useful execution lessons are retained in
[`EXECUTION_REFERENCES.md`](../EXECUTION_REFERENCES.md). Independent Claude review remains pending.

No TIER_LIST/trading-plan/live/VPS/broker/key/scout-history/schedule changes. No changed version selected.
