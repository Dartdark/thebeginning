# H02 FVB independent short execution: CLOSED at gross data gate

Summary: the frozen first-short raw window exceeded its cost hurdle, but one retained holding path and two otherwise-eligible scan prefixes were incomplete. The preregistered data veto therefore failed. No stopped rule, 2023+ validation or book bench ran. This is not a rejection based on measured stopped alpha, and the favorable gross mean does not qualify the strategy.

Plan: `agents/codex/plans/hunt_v2_fvb_short_execution.md`, original2421d7e; effective pre-data clarification/implementation **b4ed0f6**. Script: `analysis/codex_hunt_v2_fvb_short_gross.py`, SHA `221efb8959d12b7522009325a9bb22e846a4dc4ebc55853494304676d1f4fb38`. Outputs: `analysis/outputs/codex_hunt_v2_fvb_short/`.

**Running budget:3/60 counted evaluations,2/10 hypotheses,2 gross screens. H02 adds0 counted economic evaluations.** Prior t6 archived65 and prior FVB roughly27 author evaluations remain in selection history. No budget reset or new promotion claim.

## Mechanism and frozen rule

The user explicitly requested unfinished B-item confirmations. FVB shorts were a result-informed lead; the old reported short series masked a BOTH replay, where long trades could consume time and caps. A truly executable short-only strategy must ignore long signals before entry/state decisions. Proposed contingent sell-stop liquidation at prior lows is unmeasured; no known compulsory investor or dollar-flow size is asserted.

Signal timeframe1minute, NQ native prices, prospective1MNQ. Previous14 exact normal calendar slots provide mean RTH range; prior RTH08:31–15:15 must have all405minutes; current PM03:01–08:30 all330. Prior range≤1.5ATR, PMrange≤ATR, priorbody/range<.6. Ordered known lows are prior-RTH low then PMlow when distinct, except nonoverlapping prior/PM ranges use PMlow alone. First signal close strictly below an active low during08:31–10:30 enters exact next-minute open, exits exact15:11close. The cheap screen has NO stop, target, reentry or fee subtraction. Full stopped .18ATR/max2 stop-only-reentry rule was registered but NEVER evaluated.

The calendar skips known holidays/early closes and a frozen conservative quarterly second-Thursday+0/1/4/5 guard on today/prior reference. It is not verified vendor-roll provenance. Missing known prior/PM inputs skip that day before trading, with no older-session stretching. Otherwise-eligible missing scan prefixes and held paths remain visible and veto the screen.

Clock: prior reference available after its15:15close; PM available08:30; signal event/availability/decision at completed close; next-native-open fill shares that boundary under an idealized zero-receipt/processing-delay convention. No verified real receipt or latency evidence. CT uses America/Chicago/DST.

## Raw gross screen2018–22

Source files2018-01-01–2022-12-31 only, no2017 warmup, no2023 files. Run `2026-10-26T15:37:49.916148+00:00` to `2026-10-26T15:37:54.579010+00:00`. Native audit:1,751,608unique rows,0duplicate conflicts,0identical duplicates. All nine marker-bound artifact hashes were independently checked after completion; no financial rerun.


- 352first-short opportunities,352finite endpoints; all/short identical, long0events (metrics undefined).
- Gross total **$7,532.00/MNQ**, mean **$21.3977**, SD$258.6767, standard error$13.7875, unadjusted gross trade **t1.552**.
- Native assumed RT cost$1.24commission+$0.50entry+$0.50exit=$2.24. Gross hurdle$4.48, min100events: the economic mean/count condition passed.
- **Final gross gate FAILED**:1incomplete held event containing2invalid/missing minutes;2unresolved eligible scan days. Favorable observed endpoints do not overrule these gates.

|Year|Events|Gross mean/MNQ|Gross t|Gross total/MNQ|
|---|---:|---:|---:|---:|
|2018|58|$54.78|2.180|$3177.50|
|2019|83|$9.34|0.871|$775.00|
|2020|60|$-16.06|-0.494|$-963.50|
|2021|62|$19.85|0.714|$1230.50|
|2022|89|$37.22|0.888|$3312.50|

2018-07-26 signal08:47(j527), next open labelled08:48(j528), exit15:11(j911) has2invalid/missing held minutes. Its observed raw endpoint return is **-$27.50/MNQ** and remains included; no complete-case deletion. Scan-prefix gaps:2019-12-05 at08:43(j523),2021-09-17 at08:32(j512). They remain unresolved, not assumed no-trade or skipped into later signals.

Calendar dispositions:576known calendar skips,100known roll guards,109prior-reference warmup/incomplete skips,7incomplete known PM skips,140prior-range exclusions,30PM-range exclusions,300prior-body exclusions,209resolved no-signal days,352retained events and2unresolved scan days. Normal eligibility is preknown, never current whole-day membership. All retained raw exit endpoints are15:11CT; known early/holiday days skipped before entry. No executable stopped-trade half-day certification follows from raw endpoints alone.

## Costs, metrics and controls not reached

The raw-window cost arithmetic leaves$19.1577/event above assumed$2.24RT, but this is NOT stopped-strategy net performance or measured execution capacity. Spread allowance is within per-fill adverse slippage, not charged twice. Prespecified later stress was4ticks/fill,RT$5.24; no stopped stress return was calculated. NQ prices do not verify historical MNQ quotes/listing/fills or vendor contract switches.

|Required later result|Status|
|---|---|
|Stopped design, long/short/year, five metrics, daily NW5|NOT RUN: raw data gate failed|
|BOTH_CAUSAL reference and executable short cap/reentry comparison|NOT RUN|
|2023+ previously seen historical validation/full2018–26 net significance or DSR|NOT RUN|
|Identical-exit random-time/random-side placebos|NOT RUN|
|Filter totals/1000matched subsets|No executable subset filter evaluated; independent short state is not a masked BOTH portfolio|
|Current19 BASE/ADD/REPLACE/EMPTY,1MNQ,DT replacement; paired one-year MC|NOT RUN|
|Funded50K/150K/evaluation joint paths or pass/payout improvement|NOT RUN; existing joint-path limits remain|
|Fresh independent raw-spec promotion checker/MC-list confirmation/PowerLanguage|NOT RUN|

The unused bench adapter and synthetic fixtures are engineering only: `analysis/codex_hunt_v2_fvb_short_bench.py` and `bench_engineering/`. No baseline financial CSV body or account simulation was opened/run for H02. No stopped implementation was written after the failed gate. Preexecution source PASS was a source/synthetic review, not promotion or raw-strategy confirmation.

## Verdict and continuation

**CLOSE H02 at the frozen gross data gate; no stopped/validation/bench/MC/PL tests, no window/threshold/coverage rescue. Continue the bounded hunt with a distinct evidenced mechanism.** Existing reference-only uploads remain unexecuted. No t6 research/threshold/watcher restart and no trading approval.
