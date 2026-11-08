# FC 2B, ONB and T_ONESIDE ingredients: WATCH — diagnostics only

Summary: Tested 18 frozen cases; both ONBs share a breakout core, with different settings and an added ML filter.
T_ONESIDE's fade direction and pre-open timing contributed in both periods; its stop mainly limits tails.
FC's flow selection concentrates return and lowers drawdown; its break-even rule reduced net profit in both periods.
ONB ML's calendar block is the clearest fitted-score contributor; this is in-sample attribution, not validation.
No rule, size, plan or live change; independent review pending.

Plan: `agents/codex/plans/ingredients_fc_onb_t_20261108.md`, commit `b0e5112`.
Script: `analysis/codex_ingredients_fc_onb_t_20261108.py`.
Reporter: `analysis/codex_ingredients_fc_onb_t_report_20261108.py`.
Output: `analysis/outputs/codex_ingredients_fc_onb_t_20261108/`.
Trials run: 18 distinct fixed diagnostic definitions plus the registered controls; no optimum selected.
Design receipt committed as `0c11d55` before recent execution. No implementation reruns or rescue variants.

## Rule (as tested)

- **FC 2B v2:** opening-drive direction and historical flow-selected MC entry dates; exact v2 exit replica,
  including entry-bar backstop, 100-point stop, 150-point trail, 66-point BE trigger and next-open flatten.
  Four cases: original, all opening drives without the flow date gate, BE disabled only, trail disabled only.
- **ONB ADX30:** overnight location sets direction, 08:30–08:45 CT opening-range breakout,
  ADX >30, stop 0.25 daily ATR and 3R target. Four cases: original, no ADX, two-sided first breakout
  without the overnight direction restriction, no target while preserving the stop.
- **ONB ML v2:** the same core with ADX >20 and stop 0.30 ATR, plus the frozen score.
  Five cases: original; no score at these same parent settings; remove calendar, price or volatility
  terms separately. Remaining coefficients, intercept and thresholds stay fixed. No refit/recentering.
  The no-ML parent is deliberately **not** the differently configured ADX30 strategy.
- **T_ONESIDE:** active fade-only v2, not the OS leg. Fade the overnight move on MC-selected heavy-night
  dates, 0.40 ATR stop active from entry, exit at the 08:45-labelled bar open.
  Five cases: original, all valid nights without the volume hurdle, follow the same selected nights,
  enter one minute later at the cash bell, remove only the stop. Regular entry is the 08:30-labelled
  bar's open (08:29 civil CT); delayed entry is 08:31-labelled open (08:30 civil CT).

**Information/data scope:** design 2018-01-01–2022-12-30, unchanged historical replication
2023-01-01–2026-10-09. Earlier data supply warm-up only. T's all-night universe starts 2018-01-30,
the first retained MC fade event. Both recent history and MC ledgers were already known.
FC and T use up-tick `Volume` in MultiCharts; exported total ticks cannot reconstruct that field.
Their original admission is therefore taken from retained MC dates/sides. Removing that gate is a
conditional comparison with an all-drive/all-night universe, not a deployable reconstructed volume signal.

**Mechanism versus evidence:** FC proposes opening-flow continuation; ONB proposes overnight location
followed by opening participation; T proposes reversal of an unusually active overnight move near the
cash open. These tests identify return/risk dependencies in the rules. They do not identify participants,
measure forced orders, establish a causal explanation, or prove these mechanisms remain profitable live.

## Results

All amounts are **one NQ contract**, fixed size, net of $7.25 round-trip commission and one 0.25-point
adverse tick per market/stop fill; target exit has no modeled slippage. These are total period profits,
not annual dollars or account payouts. Native MNQ ledgers use $1.25 commission plus native tick costs,
not NQ net divided by ten. DD below is daily realized equity drawdown with the initial zero peak,
not intraday account drawdown or a funded-account safety estimate.

### Original baselines
| family | period | trades | total | avg | t_trade | sharpe | profit_factor | max_dd | worst_trade | native_mnq_total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FC2B | design | 443 | 129,353.25 | 291.99 | 3.68 | 1.61 | 1.62 | 8,884.75 | -2,017.25 | 12,702.75 |
| ONB30 | design | 364 | 123,767.67 | 340.02 | 4.05 | 1.76 | 1.77 | 7,580.67 | -2,595.92 | 12,185.67 |
| ONBML | design | 186 | 117,294.60 | 630.62 | 4.51 | 1.91 | 2.58 | 7,874.35 | -3,305.65 | 11,631.81 |
| Tfade | design | 228 | 47,642.00 | 208.96 | 3.17 | 1.38 | 1.74 | 7,212.50 | -2,652.25 | 4,644.50 |
| FC2B | recent | 327 | 87,259.25 | 266.85 | 2.21 | 1.12 | 1.43 | 15,251.00 | -2,017.25 | 8,554.25 |
| ONB30 | recent | 312 | 127,568.75 | 408.87 | 3.06 | 1.55 | 1.58 | 13,571.08 | -5,088.08 | 12,593.08 |
| ONBML | recent | 152 | 108,115.70 | 711.29 | 3.13 | 1.56 | 1.93 | 15,626.45 | -6,102.25 | 10,731.77 |
| Tfade | recent | 130 | 37,272.50 | 286.71 | 1.96 | 0.99 | 1.55 | 11,289.25 | -3,267.25 | 3,659.00 |

### What drives each strategy

**FC 2B: flow selection concentrates opportunity; exits have different roles.** Removing the flow gate
raises total net from $129,353 to $151,204 early and $87,259 to $114,708 recently, but DD rises from
$8,885 to $32,598 and $15,251 to $33,646. The removed trades are positive in aggregate, so this is
not a strict profitable-versus-losing-trades filter success. It retains much of the return at far fewer trades
and lower historical DD. Removing BE adds $3,380 / $8,190 net; the recent paired annual interval
includes zero. Removing the trail is almost neutral early (original minus no-trail −$20), but loses
$22,600 recently and raises DD to $19,136; recent paired annual contribution is $2,366–$10,008
(5th–95th percentile). The trail is period-dependent; BE is not an established alpha source.
None of this justifies changing the frozen production/forward rule.

**ONB ADX30: overnight direction and ADX mainly concentrate exposure and control realized DD.**
Two-sided first breakout produces almost the same early net ($124,237 vs $123,768) but much worse
DD ($33,990 vs $7,581). Recently it earns $107,693 vs $127,569 with DD $32,103 vs $13,571.
This direction intervention can change which entry occurs first, so it is not a pure removed-trade filter.
Removing ADX costs $8,661 early but adds $25,997 recently; DD worsens in both periods. The 3R target
is close to neutral early; removing it adds $10,885 recently, with unchanged recent maximum DD.
The paired recent target contribution interval includes zero. ADX/target are not uniformly profit-producing
ingredients, and the no-target case has not earned any book change.

**ONB ML: same breakout mechanism, with calendar-conditioned admission.** Dropping calendar terms
reduces early net from $117,295 to $49,958 and recent net from $108,116 to $51,694.
The original-minus-no-calendar annual intervals are positive in both periods ($7,746–$17,801 early;
$5,868–$25,219 recent). Price terms contribute $44,333 early but −$4,040 recently; volatility terms
reduce net by $39,537 early / $12,670 recently while restricting exposure. These are fixed-threshold
sensitivity tests: deleting a block changes admission and the score's level. They are not additive causal
attribution, optimized replacement scores or evidence that coefficients should be removed.
Without ML, the identically configured parent earns more total net in both periods but at larger DD.
The frozen weights were fitted on 2018–26, so **both splits are fitted-sample description**; no OOS ML claim.

**T_ONESIDE: the fade direction and the minute before the bell are the clearest repeat contributors.**
Following the same nights instead of fading turns +$47,642 / +$37,273 into −$53,638 / −$35,093.
Entering at the bell loses $8,695 / $9,905; paired annual timing contribution intervals stay positive
($263–$3,586 early, $558–$4,855 recent). These are OHLC replay differences, not measured live fill savings.
Removing the stop reduces profit by $5,565 / $3,770 and raises DD from $7,213 / $11,289 to
$11,488 / $14,904. The recent stop contribution interval includes zero; the tail-control role is clearer.
All-night fading is much weaker ($28,998 / $28,286 net, DD $24,711 / $27,411).
However, the early all-night reconstruction changes four common-date directions, so its comparison is
not a pure volume filter; do not credit its entire difference to heavy-night selection.

### Full fixed-case comparison

#### design

| family | variant | trades | total | avg | t_trade | sharpe | profit_factor | max_dd | worst_trade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FC2B | original | 443 | 129,353.25 | 291.99 | 3.68 | 1.61 | 1.62 | 8,884.75 | -2,017.25 |
| FC2B | no_flow_gate | 1287 | 151,204.25 | 117.49 | 2.48 | 1.10 | 1.21 | 32,597.50 | -2,017.25 |
| FC2B | no_BE | 443 | 132,733.25 | 299.62 | 3.59 | 1.57 | 1.56 | 8,419.75 | -2,017.25 |
| FC2B | no_trail | 443 | 129,373.25 | 292.04 | 3.65 | 1.60 | 1.62 | 9,529.25 | -2,017.25 |
| ONB30 | original | 364 | 123,767.67 | 340.02 | 4.05 | 1.76 | 1.77 | 7,580.67 | -2,595.92 |
| ONB30 | no_ADX | 634 | 115,106.75 | 181.56 | 2.72 | 1.20 | 1.33 | 12,914.33 | -2,917.92 |
| ONB30 | no_overnight_bias | 797 | 124,237.42 | 155.88 | 2.92 | 1.29 | 1.32 | 33,990.08 | -2,766.25 |
| ONB30 | no_target | 364 | 123,274.08 | 338.67 | 3.77 | 1.65 | 1.75 | 9,582.25 | -2,595.92 |
| ONBML | original | 186 | 117,294.60 | 630.62 | 4.51 | 1.91 | 2.58 | 7,874.35 | -3,305.65 |
| ONBML | no_ML | 551 | 128,308.15 | 232.86 | 3.13 | 1.38 | 1.43 | 11,839.70 | -3,305.65 |
| ONBML | no_calendar | 108 | 49,957.90 | 462.57 | 2.20 | 0.96 | 1.80 | 9,749.50 | -2,855.35 |
| ONBML | no_price | 165 | 72,961.45 | 442.19 | 3.24 | 1.40 | 2.01 | 9,538.90 | -3,305.65 |
| ONBML | no_vol | 380 | 156,831.80 | 412.72 | 4.47 | 1.94 | 1.87 | 9,789.90 | -3,305.65 |
| Tfade | original | 228 | 47,642.00 | 208.96 | 3.17 | 1.38 | 1.74 | 7,212.50 | -2,652.25 |
| Tfade | no_heavy_gate | 1261 | 28,997.75 | 23.00 | 1.01 | 0.44 | 1.08 | 24,710.50 | -3,172.25 |
| Tfade | follow_night | 228 | -53,638.00 | -235.25 | -3.39 | -1.47 | 0.56 | 54,100.75 | -3,072.25 |
| Tfade | at_bell | 228 | 38,947.00 | 170.82 | 2.60 | 1.14 | 1.57 | 7,352.50 | -3,092.25 |
| Tfade | no_stop | 228 | 42,077.00 | 184.55 | 2.60 | 1.14 | 1.59 | 11,487.50 | -3,482.25 |

#### recent

| family | variant | trades | total | avg | t_trade | sharpe | profit_factor | max_dd | worst_trade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FC2B | original | 327 | 87,259.25 | 266.85 | 2.21 | 1.12 | 1.43 | 15,251.00 | -2,017.25 |
| FC2B | no_flow_gate | 972 | 114,708.00 | 118.01 | 1.77 | 0.90 | 1.17 | 33,645.75 | -2,017.25 |
| FC2B | no_BE | 327 | 95,449.25 | 291.89 | 2.25 | 1.14 | 1.37 | 15,380.00 | -2,017.25 |
| FC2B | no_trail | 327 | 64,659.25 | 197.73 | 1.65 | 0.84 | 1.31 | 19,136.00 | -2,017.25 |
| ONB30 | original | 312 | 127,568.75 | 408.87 | 3.06 | 1.55 | 1.58 | 13,571.08 | -5,088.08 |
| ONB30 | no_ADX | 486 | 153,565.83 | 315.98 | 2.75 | 1.39 | 1.37 | 24,871.42 | -5,088.08 |
| ONB30 | no_overnight_bias | 621 | 107,693.33 | 173.42 | 1.91 | 0.97 | 1.22 | 32,102.75 | -5,088.08 |
| ONB30 | no_target | 312 | 138,454.00 | 443.76 | 3.07 | 1.55 | 1.62 | 13,571.08 | -5,088.08 |
| ONBML | original | 152 | 108,115.70 | 711.29 | 3.13 | 1.56 | 1.93 | 15,626.45 | -6,102.25 |
| ONBML | no_ML | 450 | 140,297.80 | 311.77 | 2.51 | 1.27 | 1.35 | 26,524.60 | -6,102.25 |
| ONBML | no_calendar | 93 | 51,693.65 | 555.85 | 1.72 | 0.86 | 1.58 | 23,369.45 | -6,102.25 |
| ONBML | no_price | 143 | 112,155.45 | 784.30 | 3.37 | 1.66 | 2.10 | 10,796.35 | -4,420.05 |
| ONBML | no_vol | 328 | 120,785.90 | 368.25 | 2.47 | 1.25 | 1.42 | 19,967.90 | -6,102.25 |
| Tfade | original | 130 | 37,272.50 | 286.71 | 1.96 | 0.99 | 1.55 | 11,289.25 | -3,267.25 |
| Tfade | no_heavy_gate | 973 | 28,285.75 | 29.07 | 0.71 | 0.36 | 1.06 | 27,411.00 | -3,877.25 |
| Tfade | follow_night | 130 | -35,092.50 | -269.94 | -1.85 | -0.94 | 0.67 | 38,805.75 | -4,047.25 |
| Tfade | at_bell | 130 | 27,367.50 | 210.52 | 1.42 | 0.72 | 1.37 | 11,869.25 | -3,267.25 |
| Tfade | no_stop | 130 | 33,502.50 | 257.71 | 1.70 | 0.86 | 1.47 | 14,904.25 | -4,007.25 |

## Placebos and account level

The registered T direction control actually replays reversed positions with the same stop distance and
scheduled exit; costs are charged again. It is not a sign flip of net P&L. For nested date filters,
common-date side/entry/exit/net must match before treating the difference as removed trades.
1,000 within-year equal-count random subsets provide descriptive selection controls.
Their tail shares are **not** multiple-testing-adjusted p-values and do not establish economic adoption.
| family | period | pure_nested_filter | removed_n | removed_total | removed_mean | removed_t | random_profit_ge_actual | random_dd_le_actual |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FC2B | design | True | 844.00 | 21,851.00 | 25.89 | 0.44 | 0.00 | 0.00 |
| ONBML | design | True | 365.00 | 11,013.55 | 30.17 | 0.35 | 0.00 | 0.07 |
| Tfade | design | False | — | — | — | — | — | — |
| FC2B | recent | True | 645.00 | 27,448.75 | 42.56 | 0.54 | 0.07 | 0.03 |
| ONBML | recent | True | 298.00 | 32,182.10 | 107.99 | 0.74 | 0.01 | 0.22 |
| Tfade | recent | True | 843.00 | -8,986.75 | -10.66 | -0.26 | 0.01 | 0.29 |

A small `random_profit_ge_actual` means the actual selection beats most matched-count random subsets
on total profit; `random_dd_le_actual` is the fraction with DD no worse than actual. FC's removed trades
are +$25.89 / +$42.56 per trade (t 0.44 / 0.54). ONB ML's are +$30.17 / +$107.99 (t 0.35 / 0.74).
Neither meets the strict requirement that removed trades lose. T's recent removed nights average −$10.66
(t −0.26); its removal edge is weak despite beating most random selections on total net. Early T has four
common-date direction mismatches (2018-02-07, 2018-05-25, 2018-09-06, 2022-01-21), listed in
`Tfade_allnight_common_date_mismatches.csv`; attribution to volume alone is withheld. The fixed MC
parent sides remain unchanged. No correction/search was made after seeing these differences.

Paired intervals below use original-minus-intervention **daily** cash differences, 1,000 moving
20-session blocks, seed 20261108. Dollar intervals are **annualized** while the delta column is total
period net. Positive delta favors the original. Eighteen definitions plus controls are retained; these
unadjusted diagnostic intervals must not select/promote a strategy. Original strategy standalone recent
bootstrap distributions, including annual P&L, are in `recent_bootstrap.csv` (all 18 cases).
Bootstrap DD/Calmar/Ulcer retain the repository sampler's convention; the displayed realized DD uses
its zero-start-aware `max_dd`. No claim that a bootstrap distribution is an account liquidation model.
| family | period | component_removed | original_minus_variant | annual_effect_p5 | annual_effect_p50 | annual_effect_p95 |
| --- | --- | --- | --- | --- | --- | --- |
| FC2B | design | no_flow_gate | -21,851.00 | -18,245.42 | -3,414.98 | 10,578.63 |
| FC2B | design | no_BE | -3,380.00 | -3,752.39 | -651.51 | 2,326.50 |
| FC2B | design | no_trail | -20.00 | -2,335.64 | -151.02 | 2,211.65 |
| ONB30 | design | no_ADX | 8,660.92 | -6,213.87 | 2,054.80 | 9,440.27 |
| ONB30 | design | no_overnight_bias | -469.75 | -11,285.24 | -476.22 | 10,103.62 |
| ONB30 | design | no_target | 493.58 | -4,503.48 | -401.85 | 4,022.41 |
| ONBML | design | no_ML | -11,013.55 | -11,123.84 | -1,831.52 | 7,217.70 |
| ONBML | design | no_calendar | 67,336.70 | 7,745.77 | 13,054.10 | 17,801.45 |
| ONBML | design | no_price | 44,333.15 | 942.54 | 8,388.31 | 18,482.05 |
| ONBML | design | no_vol | -39,537.20 | -15,237.66 | -7,847.59 | -937.68 |
| Tfade | design | no_heavy_gate | 18,644.25 | -4,171.32 | 3,451.97 | 10,834.59 |
| Tfade | design | follow_night | 101,280.00 | 10,138.75 | 19,938.11 | 29,491.09 |
| Tfade | design | at_bell | 8,695.00 | 263.14 | 1,638.78 | 3,586.45 |
| Tfade | design | no_stop | 5,565.00 | 30.16 | 1,039.57 | 2,265.26 |
| FC2B | recent | no_flow_gate | -27,448.75 | -26,937.97 | -5,907.69 | 14,863.65 |
| FC2B | recent | no_BE | -8,190.00 | -8,548.64 | -2,065.47 | 3,852.58 |
| FC2B | recent | no_trail | 22,600.00 | 2,366.48 | 5,836.40 | 10,007.61 |
| ONB30 | recent | no_ADX | -25,997.08 | -19,906.54 | -6,888.10 | 6,526.73 |
| ONB30 | recent | no_overnight_bias | 19,875.42 | -13,620.24 | 3,953.45 | 23,197.49 |
| ONB30 | recent | no_target | -10,885.25 | -9,763.77 | -2,636.94 | 3,823.50 |
| ONBML | recent | no_ML | -32,182.10 | -26,027.63 | -8,585.64 | 7,520.74 |
| ONBML | recent | no_calendar | 56,422.05 | 5,868.48 | 15,214.78 | 25,218.72 |
| ONBML | recent | no_price | -4,039.75 | -11,071.94 | -759.43 | 9,436.58 |
| ONBML | recent | no_vol | -12,670.20 | -15,070.50 | -3,953.08 | 7,276.83 |
| Tfade | recent | no_heavy_gate | 8,986.75 | -11,821.67 | 3,245.60 | 18,211.49 |
| Tfade | recent | follow_night | 72,365.00 | 3,480.28 | 17,619.28 | 32,540.83 |
| Tfade | recent | at_bell | 9,905.00 | 557.68 | 2,582.16 | 4,855.40 |
| Tfade | recent | no_stop | 3,770.00 | -333.45 | 957.63 | 2,712.11 |

**Account level:** not run. This task dissects existing ingredients; it neither selects a replacement nor
measures payout contribution. No BASE/ADD/REPLACE/EMPTY, leverage choice, evaluation pass probability,
funded blow-up rate or improvement to the current stack is established by these results. Any proposed
new combination requires a separate bounded preregistration and the actual current-book comparisons.

## What could make this wrong

- Exact MC baseline entry/gross parity: FC 443/443 early and 327/327 recent; T 228/228 early and
  130/130 recent. All common entries and gross P&L match, with no missing parent events, side differences
  or cross-date trades. This verifies conditional replay, not the missing up-tick classifier.
- ONB ADX30's custom core exactly matches the pinned original engine on the same inputs/settings.
  This is internal implementation identity, not a new independent MultiCharts comparison. ML adds a
  source port of the fixed score; its deleted-block cases have no MC parity claim.
- A small number of unobserved nominal held closes remain: FC original recent 3; FC all-drive early 7 /
  recent 4; FC no-BE/no-trail recent 3 each; ONB no-ADX early 1; ONB no-bias recent 4; T all-night early 3.
  All other cases have zero. Existing engine missing-bar policies remain; no future fill or invented prices.
  Even with matching realized MC P&L, intrabar risk around missing bars is uncertain.
- ONB source execution retains 1-point target trade-through and OHLC ordering. Two-sided counterfactual
  simultaneous touches use a declared nearer-extreme rule; real order of touches needs tick data.
- FC no-BE correctly uses BER=0 with the v2 `BER > 0` guard; it does not accidentally arm BE immediately.
  Every stop/target intervention preserves the other exit inputs. T stop rounding is fixed before execution.
- Both ONBs share a directional breakout core; their nominal profits cannot be added as independent edges.
  Calendar-block dominance does not isolate individual weekdays versus turn-of-month contributions.
- One-way component deletion measures dependencies conditional on the remaining system. It does not
  show interactions, statistical independence, optimal rules, forced institutional trading or live causality.
- No new learned model, honest ML holdout, forward log observation or independent economic verification.
  Both time periods were already seen historically; recent is replication, not an untouched holdout.
- The immutable input manifest and raw Git-blob checks pin data to the retained source snapshot;
  the reporter checks gross, commission, slippage, native micro fees and daily/trade sums to half a cent.

## Differences between MultiCharts and this test

No MultiCharts code was written or changed. FC/T selected source dates and sides come from MC ledgers
because native up-tick volume is absent. Exit replays use minute OHLC, not ticks or broker fills.
ONB is a source-style repository engine, not a newly verified native chart export. T's all-night control uses
observed overnight direction, which differs from four early MC-selected directions. These limits remain
visible even though original FC/T baseline realized results match exactly.

## Practical ingredient conclusion

For later, separately registered idea design: FC contributes **opening-flow selection and continuation**;
ONB contributes **overnight location plus opening-range participation**, with the ML version adding
**calendar-based selection rather than a separate core signal**; T contributes **pre-open overnight reversal**.
T's fade is directionally different from FC/ONB continuation, so combining all three as simultaneous
confirmations may reject the opportunity each was intended to capture. First identify whether a proposed
new rule uses a continuation regime or a pre-open reversal regime. No hybrid was tested in this task.

## Detailed long/short and annual results

`all_metrics.csv` includes every whole/long/short result and every year, plus costs, worst trade and native
MNQ totals. The following tables retain the required standard metrics. `win` is a fraction; profit factor
is per trade. Annualized ratios use the shared calendar including zero-P&L sessions and $50,000 capital.

### design: whole / long / short

| family | variant | side | trades | win | total | avg | t_trade | sharpe | sortino | profit_factor | calmar | ulcer | max_dd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FC2B | original | all | 443 | 0.60 | 129,353.25 | 291.99 | 3.68 | 1.61 | 3.07 | 1.62 | 2.85 | 2.68 | 8,884.75 |
| FC2B | original | long | 217 | 0.63 | 59,171.75 | 272.68 | 2.58 | 1.13 | 2.00 | 1.59 | 1.14 | 4.36 | 10,120.25 |
| FC2B | original | short | 226 | 0.56 | 70,181.50 | 310.54 | 2.63 | 1.15 | 2.33 | 1.64 | 1.69 | 4.16 | 8,135.25 |
| FC2B | no_flow_gate | all | 1287 | 0.57 | 151,204.25 | 117.49 | 2.48 | 1.10 | 1.91 | 1.21 | 0.91 | 6.03 | 32,597.50 |
| FC2B | no_flow_gate | long | 688 | 0.57 | 37,702.00 | 54.80 | 0.90 | 0.40 | 0.63 | 1.10 | 0.21 | 12.58 | 34,464.25 |
| FC2B | no_flow_gate | short | 599 | 0.56 | 113,502.25 | 189.49 | 2.57 | 1.13 | 2.18 | 1.36 | 1.04 | 6.58 | 21,432.75 |
| FC2B | no_BE | all | 443 | 0.52 | 132,733.25 | 299.62 | 3.59 | 1.57 | 3.03 | 1.56 | 3.08 | 3.10 | 8,419.75 |
| FC2B | no_BE | long | 217 | 0.56 | 54,586.75 | 251.55 | 2.32 | 1.02 | 1.79 | 1.49 | 0.98 | 4.85 | 10,877.25 |
| FC2B | no_BE | short | 226 | 0.47 | 78,146.50 | 345.78 | 2.73 | 1.19 | 2.48 | 1.62 | 1.43 | 4.76 | 10,685.25 |
| FC2B | no_trail | all | 443 | 0.60 | 129,373.25 | 292.04 | 3.65 | 1.60 | 3.06 | 1.62 | 2.65 | 3.07 | 9,529.25 |
| FC2B | no_trail | long | 217 | 0.64 | 60,336.75 | 278.05 | 2.64 | 1.15 | 2.04 | 1.61 | 1.17 | 4.37 | 10,120.25 |
| FC2B | no_trail | short | 226 | 0.56 | 69,036.50 | 305.47 | 2.55 | 1.12 | 2.28 | 1.63 | 1.53 | 4.24 | 8,817.00 |
| ONB30 | original | all | 364 | 0.51 | 123,767.67 | 340.02 | 4.05 | 1.76 | 3.85 | 1.77 | 3.19 | 3.56 | 7,580.67 |
| ONB30 | original | long | 185 | 0.56 | 53,669.08 | 290.10 | 3.05 | 1.32 | 2.68 | 1.81 | 1.24 | 3.25 | 8,465.92 |
| ONB30 | original | short | 179 | 0.46 | 70,098.58 | 391.61 | 2.81 | 1.22 | 2.79 | 1.74 | 1.65 | 4.99 | 8,294.92 |
| ONB30 | no_ADX | all | 634 | 0.44 | 115,106.75 | 181.56 | 2.72 | 1.20 | 2.32 | 1.33 | 1.74 | 10.12 | 12,914.33 |
| ONB30 | no_ADX | long | 353 | 0.47 | 54,924.92 | 155.59 | 1.96 | 0.86 | 1.59 | 1.31 | 0.79 | 8.30 | 13,639.75 |
| ONB30 | no_ADX | short | 281 | 0.40 | 60,181.83 | 214.17 | 1.91 | 0.84 | 1.69 | 1.35 | 0.67 | 13.63 | 17,526.92 |
| ONB30 | no_overnight_bias | all | 797 | 0.47 | 124,237.42 | 155.88 | 2.92 | 1.29 | 2.39 | 1.32 | 0.71 | 13.76 | 33,990.08 |
| ONB30 | no_overnight_bias | long | 393 | 0.52 | 52,108.83 | 132.59 | 1.92 | 0.85 | 1.48 | 1.29 | 0.65 | 6.76 | 15,660.58 |
| ONB30 | no_overnight_bias | short | 404 | 0.42 | 72,128.58 | 178.54 | 2.20 | 0.97 | 1.89 | 1.34 | 0.48 | 14.87 | 29,264.08 |
| ONB30 | no_target | all | 364 | 0.50 | 123,274.08 | 338.67 | 3.77 | 1.65 | 3.79 | 1.75 | 2.52 | 3.97 | 9,582.25 |
| ONB30 | no_target | long | 185 | 0.56 | 53,464.83 | 289.00 | 3.03 | 1.32 | 2.67 | 1.81 | 1.23 | 3.28 | 8,465.92 |
| ONB30 | no_target | short | 179 | 0.45 | 69,809.25 | 390.00 | 2.53 | 1.11 | 2.72 | 1.72 | 1.55 | 4.85 | 8,817.42 |
| ONBML | original | all | 186 | 0.58 | 117,294.60 | 630.62 | 4.51 | 1.91 | 4.81 | 2.58 | 2.91 | 1.96 | 7,874.35 |
| ONBML | original | long | 80 | 0.62 | 39,249.60 | 490.62 | 3.15 | 1.32 | 3.01 | 2.65 | 1.44 | 2.06 | 5,330.20 |
| ONBML | original | short | 106 | 0.55 | 78,045.00 | 736.27 | 3.42 | 1.45 | 3.79 | 2.55 | 2.14 | 3.07 | 7,123.40 |
| ONBML | no_ML | all | 551 | 0.49 | 128,308.15 | 232.86 | 3.13 | 1.38 | 2.61 | 1.43 | 2.12 | 6.01 | 11,839.70 |
| ONBML | no_ML | long | 300 | 0.53 | 44,672.70 | 148.91 | 1.72 | 0.76 | 1.27 | 1.29 | 0.57 | 6.87 | 15,222.35 |
| ONBML | no_ML | short | 251 | 0.45 | 83,635.45 | 333.21 | 2.64 | 1.15 | 2.44 | 1.56 | 1.52 | 5.83 | 10,765.25 |
| ONBML | no_calendar | all | 108 | 0.49 | 49,957.90 | 462.57 | 2.20 | 0.96 | 2.15 | 1.80 | 1.00 | 5.06 | 9,749.50 |
| ONBML | no_calendar | long | 32 | 0.47 | 5,808.80 | 181.53 | 0.61 | 0.27 | 0.44 | 1.30 | 0.12 | 7.15 | 9,757.65 |
| ONBML | no_calendar | short | 76 | 0.50 | 44,149.10 | 580.91 | 2.14 | 0.93 | 2.31 | 2.03 | 1.35 | 3.21 | 6,370.50 |
| ONBML | no_price | all | 165 | 0.56 | 72,961.45 | 442.19 | 3.24 | 1.40 | 3.04 | 2.01 | 1.50 | 2.93 | 9,538.90 |
| ONBML | no_price | long | 79 | 0.61 | 23,053.95 | 291.82 | 1.81 | 0.79 | 1.44 | 1.76 | 0.37 | 5.06 | 12,115.55 |
| ONBML | no_price | short | 86 | 0.51 | 49,907.50 | 580.32 | 2.69 | 1.15 | 2.78 | 2.19 | 1.44 | 3.93 | 6,795.25 |
| ONBML | no_vol | all | 380 | 0.53 | 156,831.80 | 412.72 | 4.47 | 1.94 | 4.19 | 1.87 | 3.13 | 3.42 | 9,789.90 |
| ONBML | no_vol | long | 183 | 0.55 | 41,219.25 | 225.24 | 2.07 | 0.91 | 1.60 | 1.49 | 0.77 | 6.05 | 10,409.40 |
| ONBML | no_vol | short | 197 | 0.51 | 115,612.55 | 586.87 | 4.02 | 1.72 | 4.25 | 2.21 | 3.77 | 2.79 | 5,996.80 |
| Tfade | original | all | 228 | 0.63 | 47,642.00 | 208.96 | 3.17 | 1.38 | 2.36 | 1.74 | 1.29 | 1.84 | 7,212.50 |
| Tfade | original | long | 132 | 0.64 | 32,918.00 | 249.38 | 2.74 | 1.18 | 2.09 | 1.87 | 1.42 | 1.56 | 4,530.75 |
| Tfade | original | short | 96 | 0.60 | 14,724.00 | 153.38 | 1.64 | 0.72 | 1.17 | 1.56 | 0.73 | 2.99 | 3,956.25 |
| Tfade | no_heavy_gate | all | 1261 | 0.52 | 28,997.75 | 23.00 | 1.01 | 0.44 | 0.65 | 1.08 | 0.23 | 17.44 | 24,710.50 |
| Tfade | no_heavy_gate | long | 572 | 0.54 | 23,688.00 | 41.41 | 1.14 | 0.51 | 0.74 | 1.14 | 0.45 | 5.27 | 10,233.75 |
| Tfade | no_heavy_gate | short | 689 | 0.50 | 5,309.75 | 7.71 | 0.26 | 0.12 | 0.17 | 1.03 | 0.05 | 20.21 | 21,321.50 |
| Tfade | follow_night | all | 228 | 0.35 | -53,638.00 | -235.25 | -3.39 | -1.47 | -1.90 | 0.56 | -0.19 | 61.27 | 54,100.75 |
| Tfade | follow_night | long | 96 | 0.39 | -17,706.00 | -184.44 | -1.83 | -0.80 | -1.04 | 0.61 | -0.17 | 19.48 | 20,208.00 |
| Tfade | follow_night | short | 132 | 0.33 | -35,932.00 | -272.21 | -2.86 | -1.24 | -1.60 | 0.52 | -0.19 | 45.56 | 37,958.00 |
| Tfade | at_bell | all | 228 | 0.61 | 38,947.00 | 170.82 | 2.60 | 1.14 | 1.84 | 1.57 | 1.04 | 2.42 | 7,352.50 |
| Tfade | at_bell | long | 132 | 0.62 | 24,498.00 | 185.59 | 2.04 | 0.89 | 1.44 | 1.59 | 0.90 | 2.22 | 5,299.75 |
| Tfade | at_bell | short | 96 | 0.59 | 14,449.00 | 150.51 | 1.61 | 0.71 | 1.14 | 1.54 | 0.73 | 2.96 | 3,849.00 |
| Tfade | no_stop | all | 228 | 0.63 | 42,077.00 | 184.55 | 2.60 | 1.14 | 1.75 | 1.59 | 0.72 | 2.81 | 11,487.50 |
| Tfade | no_stop | long | 132 | 0.65 | 29,978.00 | 227.11 | 2.30 | 1.00 | 1.57 | 1.72 | 0.69 | 2.45 | 8,487.00 |
| Tfade | no_stop | short | 96 | 0.60 | 12,099.00 | 126.03 | 1.26 | 0.56 | 0.83 | 1.42 | 0.55 | 3.60 | 4,266.75 |

### recent: whole / long / short

| family | variant | side | trades | win | total | avg | t_trade | sharpe | sortino | profit_factor | calmar | ulcer | max_dd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FC2B | original | all | 327 | 0.64 | 87,259.25 | 266.85 | 2.21 | 1.12 | 2.25 | 1.43 | 1.48 | 8.17 | 15,251.00 |
| FC2B | original | long | 158 | 0.65 | 57,659.50 | 364.93 | 2.18 | 1.10 | 2.23 | 1.62 | 1.21 | 5.49 | 12,363.50 |
| FC2B | original | short | 169 | 0.63 | 29,599.75 | 175.15 | 1.01 | 0.51 | 1.03 | 1.26 | 0.36 | 19.46 | 21,154.50 |
| FC2B | no_flow_gate | all | 972 | 0.61 | 114,708.00 | 118.01 | 1.77 | 0.90 | 1.63 | 1.17 | 0.88 | 12.22 | 33,645.75 |
| FC2B | no_flow_gate | long | 517 | 0.63 | 86,581.75 | 167.47 | 1.89 | 0.96 | 1.72 | 1.25 | 1.07 | 6.48 | 20,909.00 |
| FC2B | no_flow_gate | short | 455 | 0.59 | 28,126.25 | 61.82 | 0.61 | 0.31 | 0.58 | 1.09 | 0.15 | 32.88 | 49,647.50 |
| FC2B | no_BE | all | 327 | 0.46 | 95,449.25 | 291.89 | 2.25 | 1.14 | 2.28 | 1.37 | 1.61 | 7.68 | 15,380.00 |
| FC2B | no_BE | long | 158 | 0.51 | 67,869.50 | 429.55 | 2.38 | 1.20 | 2.44 | 1.60 | 1.32 | 5.41 | 13,267.50 |
| FC2B | no_BE | short | 169 | 0.41 | 27,579.75 | 163.19 | 0.88 | 0.45 | 0.88 | 1.19 | 0.38 | 13.78 | 18,679.75 |
| FC2B | no_trail | all | 327 | 0.64 | 64,659.25 | 197.73 | 1.65 | 0.84 | 1.65 | 1.31 | 0.88 | 8.76 | 19,136.00 |
| FC2B | no_trail | long | 158 | 0.65 | 52,699.50 | 333.54 | 1.97 | 0.99 | 2.01 | 1.56 | 1.08 | 5.81 | 12,683.50 |
| FC2B | no_trail | short | 169 | 0.63 | 11,959.75 | 70.77 | 0.42 | 0.21 | 0.41 | 1.11 | 0.14 | 20.32 | 21,364.50 |
| ONB30 | original | all | 312 | 0.51 | 127,568.75 | 408.87 | 3.06 | 1.55 | 3.10 | 1.58 | 2.43 | 3.25 | 13,571.08 |
| ONB30 | original | long | 174 | 0.54 | 67,840.83 | 389.89 | 2.32 | 1.17 | 2.30 | 1.60 | 1.28 | 3.84 | 13,694.75 |
| ONB30 | original | short | 138 | 0.48 | 59,727.92 | 432.81 | 2.01 | 1.01 | 2.08 | 1.55 | 1.30 | 4.84 | 11,887.00 |
| ONB30 | no_ADX | all | 486 | 0.47 | 153,565.83 | 315.98 | 2.75 | 1.39 | 2.67 | 1.37 | 1.60 | 4.51 | 24,871.42 |
| ONB30 | no_ADX | long | 278 | 0.50 | 89,255.58 | 321.06 | 2.29 | 1.16 | 2.10 | 1.40 | 1.42 | 5.24 | 16,281.67 |
| ONB30 | no_ADX | short | 208 | 0.42 | 64,310.25 | 309.18 | 1.60 | 0.81 | 1.65 | 1.34 | 0.75 | 6.64 | 22,142.42 |
| ONB30 | no_overnight_bias | all | 621 | 0.45 | 107,693.33 | 173.42 | 1.91 | 0.97 | 1.78 | 1.22 | 0.87 | 7.63 | 32,102.75 |
| ONB30 | no_overnight_bias | long | 315 | 0.52 | 106,977.25 | 339.61 | 2.72 | 1.38 | 2.65 | 1.49 | 1.32 | 3.73 | 20,930.83 |
| ONB30 | no_overnight_bias | short | 306 | 0.39 | 716.08 | 2.34 | 0.02 | 0.01 | 0.02 | 1.00 | 0.00 | 19.54 | 41,817.42 |
| ONB30 | no_target | all | 312 | 0.51 | 138,454.00 | 443.76 | 3.07 | 1.55 | 3.35 | 1.62 | 2.64 | 3.21 | 13,571.08 |
| ONB30 | no_target | long | 174 | 0.53 | 70,352.08 | 404.32 | 2.25 | 1.14 | 2.37 | 1.61 | 1.33 | 4.10 | 13,694.75 |
| ONB30 | no_target | short | 138 | 0.48 | 68,101.92 | 493.49 | 2.08 | 1.05 | 2.37 | 1.63 | 1.48 | 4.71 | 11,887.00 |
| ONBML | original | all | 152 | 0.58 | 108,115.70 | 711.29 | 3.13 | 1.56 | 3.09 | 1.93 | 1.79 | 3.72 | 15,626.45 |
| ONBML | original | long | 77 | 0.69 | 67,656.45 | 878.66 | 2.97 | 1.45 | 2.76 | 2.32 | 1.58 | 2.77 | 11,084.00 |
| ONBML | original | short | 75 | 0.47 | 40,459.25 | 539.46 | 1.56 | 0.79 | 1.62 | 1.62 | 0.52 | 6.81 | 20,235.95 |
| ONBML | no_ML | all | 450 | 0.49 | 140,297.80 | 311.77 | 2.51 | 1.27 | 2.33 | 1.35 | 1.37 | 5.04 | 26,524.60 |
| ONBML | no_ML | long | 253 | 0.53 | 95,106.75 | 375.92 | 2.42 | 1.22 | 2.19 | 1.46 | 1.27 | 5.17 | 19,468.05 |
| ONBML | no_ML | short | 197 | 0.44 | 45,191.05 | 229.40 | 1.14 | 0.58 | 1.08 | 1.23 | 0.48 | 8.62 | 24,529.90 |
| ONBML | no_calendar | all | 93 | 0.47 | 51,693.65 | 555.85 | 1.72 | 0.86 | 1.65 | 1.58 | 0.57 | 8.70 | 23,369.45 |
| ONBML | no_calendar | long | 27 | 0.56 | 16,181.55 | 599.32 | 0.93 | 0.47 | 0.81 | 1.56 | 0.42 | 5.21 | 9,985.30 |
| ONBML | no_calendar | short | 66 | 0.44 | 35,512.10 | 538.06 | 1.43 | 0.72 | 1.46 | 1.59 | 0.42 | 8.66 | 21,697.40 |
| ONBML | no_price | all | 143 | 0.57 | 112,155.45 | 784.30 | 3.37 | 1.66 | 3.71 | 2.10 | 2.69 | 2.78 | 10,796.35 |
| ONBML | no_price | long | 85 | 0.64 | 71,191.95 | 837.55 | 3.05 | 1.49 | 3.13 | 2.33 | 2.27 | 2.52 | 8,108.20 |
| ONBML | no_price | short | 58 | 0.48 | 40,963.50 | 706.27 | 1.71 | 0.86 | 2.05 | 1.85 | 1.22 | 3.60 | 8,714.15 |
| ONBML | no_vol | all | 328 | 0.49 | 120,785.90 | 368.25 | 2.47 | 1.25 | 2.33 | 1.42 | 1.57 | 7.18 | 19,967.90 |
| ONBML | no_vol | long | 167 | 0.55 | 74,037.15 | 443.34 | 2.30 | 1.16 | 2.06 | 1.56 | 0.98 | 6.38 | 19,494.60 |
| ONBML | no_vol | short | 161 | 0.43 | 46,748.75 | 290.36 | 1.27 | 0.64 | 1.25 | 1.30 | 0.48 | 9.80 | 25,348.85 |
| Tfade | original | all | 130 | 0.55 | 37,272.50 | 286.71 | 1.96 | 0.99 | 1.73 | 1.55 | 0.86 | 5.11 | 11,289.25 |
| Tfade | original | long | 69 | 0.55 | 15,834.75 | 229.49 | 1.07 | 0.54 | 0.90 | 1.37 | 0.36 | 4.51 | 11,284.25 |
| Tfade | original | short | 61 | 0.56 | 21,437.75 | 351.44 | 1.80 | 0.90 | 1.71 | 1.83 | 0.76 | 3.90 | 7,266.25 |
| Tfade | no_heavy_gate | all | 973 | 0.49 | 28,285.75 | 29.07 | 0.71 | 0.36 | 0.55 | 1.06 | 0.27 | 17.92 | 27,411.00 |
| Tfade | no_heavy_gate | long | 428 | 0.52 | 11,302.00 | 26.41 | 0.42 | 0.21 | 0.31 | 1.06 | 0.12 | 15.47 | 23,587.75 |
| Tfade | no_heavy_gate | short | 545 | 0.46 | 16,983.75 | 31.16 | 0.58 | 0.30 | 0.47 | 1.07 | 0.20 | 16.72 | 21,765.50 |
| Tfade | follow_night | all | 130 | 0.44 | -35,092.50 | -269.94 | -1.85 | -0.94 | -1.19 | 0.67 | -0.23 | 41.51 | 38,805.75 |
| Tfade | follow_night | long | 61 | 0.44 | -20,097.25 | -329.46 | -1.75 | -0.88 | -1.07 | 0.56 | -0.21 | 28.87 | 25,005.25 |
| Tfade | follow_night | short | 69 | 0.43 | -14,995.25 | -217.32 | -0.99 | -0.50 | -0.66 | 0.74 | -0.20 | 17.45 | 19,838.25 |
| Tfade | at_bell | all | 130 | 0.55 | 27,367.50 | 210.52 | 1.42 | 0.72 | 1.20 | 1.37 | 0.60 | 6.30 | 11,869.25 |
| Tfade | at_bell | long | 69 | 0.54 | 8,349.75 | 121.01 | 0.54 | 0.28 | 0.44 | 1.18 | 0.16 | 6.28 | 13,635.00 |
| Tfade | at_bell | short | 61 | 0.56 | 19,017.75 | 311.77 | 1.61 | 0.81 | 1.51 | 1.72 | 0.58 | 4.74 | 8,434.25 |
| Tfade | no_stop | all | 130 | 0.55 | 33,502.50 | 257.71 | 1.70 | 0.86 | 1.41 | 1.47 | 0.58 | 5.61 | 14,904.25 |
| Tfade | no_stop | long | 69 | 0.55 | 13,284.75 | 192.53 | 0.86 | 0.44 | 0.68 | 1.30 | 0.23 | 5.83 | 15,019.25 |
| Tfade | no_stop | short | 61 | 0.56 | 20,217.75 | 331.44 | 1.65 | 0.83 | 1.49 | 1.75 | 0.62 | 4.31 | 8,464.25 |

### By year, all sides

| family | variant | period | trades | win | total | avg | t_trade | sharpe | sortino | profit_factor | calmar | ulcer | max_dd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FC2B | original | 2018 | 83 | 0.53 | 19,928.25 | 240.10 | 1.70 | 1.67 | 3.11 | 1.65 | 4.13 | 2.81 | 4,733.00 |
| FC2B | original | 2019 | 97 | 0.54 | 9,361.75 | 96.51 | 1.06 | 1.05 | 1.70 | 1.33 | 1.97 | 3.31 | 4,650.75 |
| FC2B | original | 2020 | 83 | 0.60 | 13,993.25 | 168.59 | 0.85 | 0.84 | 1.45 | 1.28 | 1.54 | 6.05 | 8,884.75 |
| FC2B | original | 2021 | 85 | 0.65 | 34,108.75 | 401.28 | 2.20 | 2.14 | 3.94 | 1.81 | 6.08 | 2.58 | 5,479.25 |
| FC2B | original | 2022 | 95 | 0.66 | 51,961.25 | 546.96 | 2.31 | 2.25 | 4.82 | 1.90 | 8.76 | 2.74 | 5,791.75 |
| FC2B | no_flow_gate | 2018 | 257 | 0.53 | 45,131.75 | 175.61 | 1.99 | 1.97 | 3.62 | 1.42 | 5.78 | 2.76 | 7,662.50 |
| FC2B | no_flow_gate | 2019 | 258 | 0.55 | 6,954.50 | 26.96 | 0.48 | 0.48 | 0.70 | 1.09 | 0.76 | 6.31 | 8,889.50 |
| FC2B | no_flow_gate | 2020 | 257 | 0.61 | 36,781.75 | 143.12 | 1.26 | 1.25 | 2.15 | 1.24 | 1.49 | 14.35 | 24,089.50 |
| FC2B | no_flow_gate | 2021 | 257 | 0.55 | 11,336.75 | 44.11 | 0.43 | 0.42 | 0.64 | 1.07 | 0.42 | 11.59 | 26,336.75 |
| FC2B | no_flow_gate | 2022 | 258 | 0.60 | 50,999.50 | 197.67 | 1.35 | 1.33 | 2.57 | 1.26 | 2.46 | 10.36 | 20,271.50 |
| FC2B | no_BE | 2018 | 83 | 0.52 | 18,823.25 | 226.79 | 1.60 | 1.57 | 2.89 | 1.59 | 3.89 | 3.27 | 4,740.25 |
| FC2B | no_BE | 2019 | 97 | 0.51 | 7,471.75 | 77.03 | 0.84 | 0.83 | 1.32 | 1.24 | 1.25 | 4.41 | 5,859.75 |
| FC2B | no_BE | 2020 | 83 | 0.49 | 9,238.25 | 111.30 | 0.55 | 0.54 | 0.92 | 1.16 | 1.07 | 6.28 | 8,419.75 |
| FC2B | no_BE | 2021 | 85 | 0.58 | 43,588.75 | 512.81 | 2.50 | 2.42 | 4.82 | 1.92 | 8.45 | 2.50 | 5,039.00 |
| FC2B | no_BE | 2022 | 95 | 0.49 | 53,611.25 | 564.33 | 2.27 | 2.22 | 4.76 | 1.78 | 7.85 | 3.25 | 6,674.00 |
| FC2B | no_trail | 2018 | 83 | 0.53 | 19,928.25 | 240.10 | 1.70 | 1.67 | 3.11 | 1.65 | 4.13 | 2.81 | 4,733.00 |
| FC2B | no_trail | 2019 | 97 | 0.54 | 9,361.75 | 96.51 | 1.06 | 1.05 | 1.70 | 1.33 | 1.97 | 3.31 | 4,650.75 |
| FC2B | no_trail | 2020 | 83 | 0.60 | 10,503.25 | 126.55 | 0.65 | 0.65 | 1.08 | 1.21 | 1.08 | 7.31 | 9,529.25 |
| FC2B | no_trail | 2021 | 85 | 0.65 | 31,108.75 | 365.99 | 2.02 | 1.97 | 3.54 | 1.73 | 5.55 | 2.67 | 5,479.25 |
| FC2B | no_trail | 2022 | 95 | 0.67 | 58,471.25 | 615.49 | 2.51 | 2.44 | 5.46 | 2.03 | 9.44 | 2.64 | 6,051.75 |
| ONB30 | original | 2018 | 72 | 0.46 | 7,475.75 | 103.83 | 0.95 | 0.94 | 1.89 | 1.34 | 2.06 | 2.93 | 3,561.50 |
| ONB30 | original | 2019 | 71 | 0.42 | 3,680.67 | 51.84 | 0.54 | 0.53 | 1.04 | 1.18 | 0.65 | 5.15 | 5,567.92 |
| ONB30 | original | 2020 | 64 | 0.52 | 14,769.00 | 230.77 | 1.23 | 1.21 | 2.28 | 1.46 | 2.37 | 3.68 | 6,083.75 |
| ONB30 | original | 2021 | 77 | 0.53 | 36,915.00 | 479.42 | 2.52 | 2.43 | 5.73 | 2.05 | 5.63 | 3.57 | 6,400.92 |
| ONB30 | original | 2022 | 80 | 0.60 | 60,927.25 | 761.59 | 2.88 | 2.76 | 6.24 | 2.20 | 10.72 | 3.00 | 5,553.33 |
| ONB30 | no_ADX | 2018 | 131 | 0.34 | -8,690.42 | -66.34 | -0.85 | -0.84 | -1.41 | 0.83 | -0.66 | 16.19 | 12,914.33 |
| ONB30 | no_ADX | 2019 | 110 | 0.40 | 3,576.50 | 32.51 | 0.43 | 0.42 | 0.82 | 1.11 | 0.48 | 6.71 | 7,336.83 |
| ONB30 | no_ADX | 2020 | 119 | 0.53 | 31,572.75 | 265.32 | 1.78 | 1.75 | 3.20 | 1.50 | 4.62 | 3.51 | 6,677.67 |
| ONB30 | no_ADX | 2021 | 132 | 0.42 | 19,068.67 | 144.46 | 1.01 | 0.99 | 1.88 | 1.23 | 1.61 | 8.88 | 11,551.58 |
| ONB30 | no_ADX | 2022 | 142 | 0.50 | 69,579.25 | 489.99 | 2.29 | 2.25 | 4.53 | 1.58 | 5.60 | 5.70 | 12,137.42 |
| ONB30 | no_overnight_bias | 2018 | 156 | 0.46 | 12,202.17 | 78.22 | 1.15 | 1.14 | 2.16 | 1.26 | 2.03 | 2.78 | 5,907.25 |
| ONB30 | no_overnight_bias | 2019 | 169 | 0.45 | 8,860.83 | 52.43 | 0.92 | 0.91 | 1.76 | 1.20 | 1.71 | 3.81 | 5,066.42 |
| ONB30 | no_overnight_bias | 2020 | 153 | 0.42 | -19,570.50 | -127.91 | -1.09 | -1.08 | -1.59 | 0.81 | -0.56 | 35.18 | 33,990.08 |
| ONB30 | no_overnight_bias | 2021 | 162 | 0.51 | 52,261.17 | 322.60 | 2.71 | 2.66 | 5.70 | 1.70 | 6.53 | 3.15 | 7,811.75 |
| ONB30 | no_overnight_bias | 2022 | 157 | 0.53 | 70,483.75 | 448.94 | 2.36 | 2.32 | 4.50 | 1.57 | 5.55 | 6.75 | 12,404.17 |
| ONB30 | no_target | 2018 | 72 | 0.46 | 7,685.00 | 106.74 | 0.97 | 0.96 | 1.95 | 1.35 | 2.12 | 2.81 | 3,561.50 |
| ONB30 | no_target | 2019 | 71 | 0.42 | 2,958.67 | 41.67 | 0.45 | 0.45 | 0.84 | 1.14 | 0.52 | 5.22 | 5,567.92 |
| ONB30 | no_target | 2020 | 64 | 0.52 | 24,364.00 | 380.69 | 1.54 | 1.51 | 3.77 | 1.77 | 3.91 | 3.64 | 6,083.75 |
| ONB30 | no_target | 2021 | 77 | 0.52 | 37,220.67 | 483.39 | 2.34 | 2.27 | 5.73 | 2.04 | 3.79 | 4.96 | 9,582.25 |
| ONB30 | no_target | 2022 | 80 | 0.59 | 51,045.75 | 638.07 | 2.40 | 2.33 | 5.11 | 1.96 | 5.58 | 5.22 | 8,941.58 |
| ONBML | original | 2018 | 30 | 0.43 | 3,217.90 | 107.26 | 0.55 | 0.55 | 1.11 | 1.30 | 1.50 | 2.44 | 2,098.00 |
| ONBML | original | 2019 | 34 | 0.56 | 12,286.70 | 361.37 | 2.48 | 2.31 | 7.69 | 3.24 | 5.83 | 1.22 | 2,057.75 |
| ONBML | original | 2020 | 33 | 0.64 | 18,137.45 | 549.62 | 1.96 | 1.87 | 3.93 | 2.62 | 5.36 | 1.94 | 3,305.65 |
| ONBML | original | 2021 | 40 | 0.60 | 30,064.30 | 751.61 | 2.38 | 2.24 | 5.49 | 2.62 | 3.73 | 3.99 | 7,874.35 |
| ONBML | original | 2022 | 49 | 0.63 | 53,588.25 | 1,093.64 | 2.81 | 2.63 | 7.12 | 2.91 | 9.80 | 2.69 | 5,340.50 |
| ONBML | no_ML | 2018 | 114 | 0.40 | 1,164.00 | 10.21 | 0.11 | 0.11 | 0.19 | 1.03 | 0.11 | 10.40 | 10,091.20 |
| ONBML | no_ML | 2019 | 97 | 0.44 | 6,475.75 | 66.76 | 0.79 | 0.78 | 1.49 | 1.23 | 1.10 | 5.18 | 5,747.90 |
| ONBML | no_ML | 2020 | 99 | 0.57 | 24,757.25 | 250.07 | 1.54 | 1.52 | 2.62 | 1.47 | 3.18 | 4.50 | 7,605.35 |
| ONBML | no_ML | 2021 | 115 | 0.50 | 29,113.05 | 253.16 | 1.52 | 1.50 | 2.81 | 1.41 | 3.63 | 4.42 | 7,831.55 |
| ONBML | no_ML | 2022 | 126 | 0.54 | 66,798.10 | 530.14 | 2.27 | 2.22 | 4.39 | 1.63 | 5.51 | 5.94 | 11,839.70 |
| ONBML | no_calendar | 2018 | 20 | 0.40 | 1,526.50 | 76.32 | 0.32 | 0.32 | 0.68 | 1.22 | 0.63 | 2.96 | 2,371.15 |
| ONBML | no_calendar | 2019 | 8 | 0.25 | 1,040.30 | 130.04 | 0.38 | 0.39 | 0.94 | 1.45 | 0.46 | 1.75 | 2,232.25 |
| ONBML | no_calendar | 2020 | 16 | 0.56 | -936.40 | -58.52 | -0.16 | -0.16 | -0.22 | 0.91 | -0.15 | 6.48 | 6,254.65 |
| ONBML | no_calendar | 2021 | 20 | 0.40 | 7,902.90 | 395.14 | 0.76 | 0.76 | 1.68 | 1.58 | 1.53 | 4.19 | 5,031.40 |
| ONBML | no_calendar | 2022 | 44 | 0.59 | 40,424.60 | 918.74 | 2.20 | 2.10 | 5.14 | 2.38 | 8.99 | 2.77 | 4,394.35 |
| ONBML | no_price | 2018 | 34 | 0.41 | 584.00 | 17.18 | 0.09 | 0.09 | 0.16 | 1.04 | 0.14 | 4.03 | 4,184.80 |
| ONBML | no_price | 2019 | 31 | 0.61 | 9,740.65 | 314.21 | 2.14 | 2.01 | 5.69 | 2.88 | 6.75 | 1.15 | 1,410.25 |
| ONBML | no_price | 2020 | 28 | 0.57 | 9,967.10 | 355.97 | 1.11 | 1.09 | 2.00 | 1.80 | 2.29 | 2.87 | 4,243.25 |
| ONBML | no_price | 2021 | 34 | 0.65 | 29,803.80 | 876.58 | 3.09 | 2.76 | 8.20 | 3.64 | 10.95 | 1.55 | 2,657.30 |
| ONBML | no_price | 2022 | 38 | 0.55 | 22,865.90 | 601.73 | 1.39 | 1.36 | 2.91 | 1.79 | 2.34 | 5.39 | 9,538.90 |
| ONBML | no_vol | 2018 | 88 | 0.39 | 2,101.60 | 23.88 | 0.22 | 0.21 | 0.40 | 1.06 | 0.33 | 5.38 | 6,241.95 |
| ONBML | no_vol | 2019 | 69 | 0.48 | 8,115.55 | 117.62 | 1.20 | 1.18 | 2.30 | 1.45 | 1.71 | 3.08 | 4,624.85 |
| ONBML | no_vol | 2020 | 62 | 0.60 | 24,138.60 | 389.33 | 1.83 | 1.78 | 3.26 | 1.80 | 4.73 | 3.18 | 4,983.00 |
| ONBML | no_vol | 2021 | 73 | 0.59 | 42,731.25 | 585.36 | 2.65 | 2.55 | 5.56 | 2.14 | 4.26 | 3.79 | 9,789.90 |
| ONBML | no_vol | 2022 | 88 | 0.60 | 79,744.80 | 906.19 | 3.19 | 3.05 | 7.09 | 2.32 | 13.47 | 2.21 | 5,782.65 |
| Tfade | original | 2018 | 50 | 0.64 | 7,597.50 | 151.95 | 1.73 | 1.69 | 3.37 | 1.96 | 4.40 | 1.13 | 1,693.50 |
| Tfade | original | 2019 | 40 | 0.57 | 1,895.00 | 47.38 | 0.64 | 0.63 | 0.99 | 1.28 | 0.62 | 2.42 | 2,977.50 |
| Tfade | original | 2020 | 43 | 0.72 | 19,653.25 | 457.05 | 2.95 | 2.72 | 6.10 | 3.15 | 8.30 | 0.74 | 2,311.75 |
| Tfade | original | 2021 | 56 | 0.62 | 14,019.00 | 250.34 | 1.67 | 1.63 | 2.81 | 1.73 | 1.90 | 4.39 | 7,212.50 |
| Tfade | original | 2022 | 39 | 0.56 | 4,477.25 | 114.80 | 0.49 | 0.49 | 0.73 | 1.21 | 0.79 | 2.95 | 5,561.50 |
| Tfade | no_heavy_gate | 2018 | 237 | 0.49 | -5,013.25 | -21.15 | -0.65 | -0.64 | -0.92 | 0.89 | -0.42 | 9.69 | 11,695.50 |
| Tfade | no_heavy_gate | 2019 | 257 | 0.51 | -9,763.25 | -37.99 | -1.59 | -1.57 | -2.04 | 0.78 | -0.58 | 16.32 | 16,459.00 |
| Tfade | no_heavy_gate | 2020 | 252 | 0.56 | 22,733.00 | 90.21 | 1.76 | 1.74 | 2.71 | 1.34 | 2.84 | 5.50 | 7,812.25 |
| Tfade | no_heavy_gate | 2021 | 258 | 0.54 | 17,814.50 | 69.05 | 1.33 | 1.32 | 2.02 | 1.24 | 2.14 | 6.18 | 8,125.00 |
| Tfade | no_heavy_gate | 2022 | 257 | 0.50 | 3,226.75 | 12.56 | 0.16 | 0.16 | 0.23 | 1.03 | 0.13 | 18.40 | 24,710.50 |
| Tfade | follow_night | 2018 | 50 | 0.32 | -8,332.50 | -166.65 | -2.19 | -2.10 | -2.47 | 0.47 | -0.98 | 9.46 | 8,332.50 |
| Tfade | follow_night | 2019 | 40 | 0.42 | -4,660.00 | -116.50 | -1.52 | -1.49 | -1.80 | 0.56 | -0.90 | 7.26 | 5,033.25 |
| Tfade | follow_night | 2020 | 43 | 0.21 | -22,061.75 | -513.06 | -3.31 | -2.99 | -3.52 | 0.30 | -0.98 | 26.15 | 22,061.75 |
| Tfade | follow_night | 2021 | 56 | 0.38 | -11,456.00 | -204.57 | -1.20 | -1.18 | -1.64 | 0.67 | -0.56 | 19.12 | 19,991.75 |
| Tfade | follow_night | 2022 | 39 | 0.44 | -7,127.75 | -182.76 | -0.74 | -0.74 | -0.98 | 0.75 | -0.72 | 11.32 | 9,699.50 |
| Tfade | at_bell | 2018 | 50 | 0.60 | 3,352.50 | 67.05 | 0.93 | 0.92 | 1.49 | 1.39 | 1.85 | 1.29 | 1,778.50 |
| Tfade | at_bell | 2019 | 40 | 0.55 | 1,835.00 | 45.88 | 0.64 | 0.63 | 1.00 | 1.28 | 0.63 | 2.16 | 2,857.50 |
| Tfade | at_bell | 2020 | 43 | 0.74 | 19,073.25 | 443.56 | 2.98 | 2.75 | 6.09 | 3.18 | 9.55 | 0.66 | 1,951.75 |
| Tfade | at_bell | 2021 | 56 | 0.59 | 10,509.00 | 187.66 | 1.20 | 1.18 | 1.88 | 1.47 | 1.40 | 6.52 | 7,352.50 |
| Tfade | at_bell | 2022 | 39 | 0.56 | 4,177.25 | 107.11 | 0.45 | 0.45 | 0.66 | 1.19 | 0.71 | 2.88 | 5,736.50 |
| Tfade | no_stop | 2018 | 50 | 0.64 | 7,457.50 | 149.15 | 1.70 | 1.66 | 3.30 | 1.93 | 4.70 | 1.29 | 1,554.50 |
| Tfade | no_stop | 2019 | 40 | 0.57 | 2,295.00 | 57.38 | 0.78 | 0.77 | 1.21 | 1.36 | 0.79 | 2.22 | 2,853.00 |
| Tfade | no_stop | 2020 | 43 | 0.74 | 19,253.25 | 447.75 | 2.62 | 2.46 | 4.52 | 2.81 | 7.05 | 0.87 | 2,666.75 |
| Tfade | no_stop | 2021 | 56 | 0.62 | 9,049.00 | 161.59 | 0.93 | 0.92 | 1.32 | 1.37 | 0.77 | 8.40 | 11,487.50 |
| Tfade | no_stop | 2022 | 39 | 0.56 | 4,022.25 | 103.13 | 0.43 | 0.43 | 0.62 | 1.19 | 0.71 | 3.43 | 5,561.50 |
| FC2B | original | 2023 | 82 | 0.56 | 4,335.50 | 52.87 | 0.24 | 0.24 | 0.43 | 1.08 | 0.30 | 11.15 | 14,236.00 |
| FC2B | original | 2024 | 91 | 0.68 | 27,775.25 | 305.22 | 1.49 | 1.46 | 2.80 | 1.55 | 2.08 | 10.33 | 13,012.75 |
| FC2B | original | 2025 | 89 | 0.70 | 37,384.75 | 420.05 | 1.82 | 1.79 | 3.95 | 1.81 | 4.78 | 5.70 | 7,663.00 |
| FC2B | original | 2026 | 65 | 0.58 | 17,763.75 | 273.29 | 0.81 | 0.91 | 1.94 | 1.33 | 1.47 | 9.98 | 15,251.00 |
| FC2B | no_flow_gate | 2023 | 257 | 0.59 | 15,106.75 | 58.78 | 0.50 | 0.49 | 0.84 | 1.09 | 0.49 | 16.82 | 30,509.25 |
| FC2B | no_flow_gate | 2024 | 258 | 0.63 | 78,709.50 | 305.08 | 2.23 | 2.20 | 4.39 | 1.48 | 4.53 | 7.37 | 16,923.25 |
| FC2B | no_flow_gate | 2025 | 257 | 0.61 | 9,306.75 | 36.21 | 0.29 | 0.29 | 0.50 | 1.05 | 0.30 | 31.72 | 30,217.25 |
| FC2B | no_flow_gate | 2026 | 200 | 0.61 | 11,585.00 | 57.92 | 0.37 | 0.41 | 0.75 | 1.08 | 0.54 | 18.54 | 27,146.75 |
| FC2B | no_BE | 2023 | 82 | 0.45 | 14,825.50 | 180.80 | 0.77 | 0.76 | 1.40 | 1.23 | 1.00 | 9.36 | 14,556.00 |
| FC2B | no_BE | 2024 | 91 | 0.47 | 15,745.25 | 173.02 | 0.82 | 0.81 | 1.48 | 1.24 | 1.00 | 13.15 | 15,380.00 |
| FC2B | no_BE | 2025 | 89 | 0.47 | 44,959.75 | 505.17 | 1.96 | 1.92 | 4.27 | 1.70 | 4.49 | 4.75 | 9,818.50 |
| FC2B | no_BE | 2026 | 65 | 0.43 | 19,918.75 | 306.44 | 0.85 | 0.96 | 2.02 | 1.30 | 1.74 | 9.63 | 14,458.50 |
| FC2B | no_trail | 2023 | 82 | 0.56 | 4,135.50 | 50.43 | 0.23 | 0.23 | 0.41 | 1.07 | 0.28 | 11.20 | 14,236.00 |
| FC2B | no_trail | 2024 | 91 | 0.68 | 24,830.25 | 272.86 | 1.32 | 1.30 | 2.48 | 1.49 | 1.84 | 9.79 | 13,112.75 |
| FC2B | no_trail | 2025 | 89 | 0.70 | 28,454.75 | 319.72 | 1.38 | 1.37 | 2.97 | 1.61 | 3.46 | 6.70 | 8,058.00 |
| FC2B | no_trail | 2026 | 65 | 0.58 | 7,238.75 | 111.37 | 0.34 | 0.39 | 0.78 | 1.13 | 0.48 | 13.97 | 19,136.00 |
| ONB30 | original | 2023 | 86 | 0.49 | 12,927.67 | 150.32 | 1.00 | 0.99 | 1.78 | 1.29 | 2.17 | 3.97 | 5,850.17 |
| ONB30 | original | 2024 | 80 | 0.60 | 68,958.25 | 861.98 | 3.62 | 3.40 | 8.53 | 2.68 | 12.46 | 3.43 | 5,386.42 |
| ONB30 | original | 2025 | 77 | 0.48 | 19,628.42 | 254.91 | 0.80 | 0.79 | 1.47 | 1.27 | 1.93 | 5.67 | 9,988.08 |
| ONB30 | original | 2026 | 69 | 0.48 | 26,054.42 | 377.60 | 1.08 | 1.21 | 2.40 | 1.41 | 2.42 | 5.95 | 13,571.08 |
| ONB30 | no_ADX | 2023 | 126 | 0.44 | 28,346.25 | 224.97 | 1.51 | 1.49 | 2.95 | 1.37 | 3.68 | 4.98 | 7,543.42 |
| ONB30 | no_ADX | 2024 | 138 | 0.46 | 61,793.83 | 447.78 | 2.33 | 2.28 | 4.87 | 1.63 | 7.40 | 5.48 | 8,123.75 |
| ONB30 | no_ADX | 2025 | 122 | 0.50 | 20,192.33 | 165.51 | 0.62 | 0.61 | 1.09 | 1.16 | 0.84 | 8.77 | 23,439.75 |
| ONB30 | no_ADX | 2026 | 100 | 0.46 | 43,233.42 | 432.33 | 1.35 | 1.51 | 2.93 | 1.39 | 2.96 | 6.76 | 18,407.08 |
| ONB30 | no_overnight_bias | 2023 | 161 | 0.43 | 7,615.50 | 47.30 | 0.40 | 0.40 | 0.71 | 1.08 | 0.54 | 10.73 | 13,898.25 |
| ONB30 | no_overnight_bias | 2024 | 155 | 0.50 | 71,489.33 | 461.22 | 2.77 | 2.71 | 5.90 | 1.74 | 7.70 | 4.67 | 9,032.67 |
| ONB30 | no_overnight_bias | 2025 | 169 | 0.47 | 39,287.00 | 232.47 | 1.18 | 1.16 | 2.14 | 1.26 | 2.39 | 10.61 | 16,150.67 |
| ONB30 | no_overnight_bias | 2026 | 136 | 0.41 | -10,698.50 | -78.67 | -0.33 | -0.38 | -0.63 | 0.93 | -0.42 | 20.33 | 32,102.75 |
| ONB30 | no_target | 2023 | 86 | 0.49 | 13,269.17 | 154.29 | 1.01 | 1.00 | 1.83 | 1.30 | 2.22 | 3.93 | 5,850.17 |
| ONB30 | no_target | 2024 | 80 | 0.60 | 78,064.50 | 975.81 | 3.60 | 3.38 | 9.66 | 2.90 | 14.23 | 3.38 | 5,337.92 |
| ONB30 | no_target | 2025 | 77 | 0.48 | 20,396.92 | 264.90 | 0.81 | 0.80 | 1.53 | 1.28 | 2.00 | 5.33 | 9,988.08 |
| ONB30 | no_target | 2026 | 69 | 0.46 | 26,723.42 | 387.30 | 0.98 | 1.10 | 2.44 | 1.41 | 2.48 | 6.41 | 13,571.08 |
| ONBML | original | 2023 | 35 | 0.49 | 14,277.75 | 407.94 | 1.25 | 1.23 | 2.63 | 1.68 | 2.96 | 4.77 | 4,730.95 |
| ONBML | original | 2024 | 38 | 0.66 | 39,603.40 | 1,042.19 | 2.71 | 2.50 | 6.88 | 3.33 | 6.53 | 1.81 | 5,899.15 |
| ONBML | original | 2025 | 47 | 0.62 | 18,637.85 | 396.55 | 0.91 | 0.90 | 1.42 | 1.40 | 1.17 | 7.20 | 15,626.45 |
| ONBML | original | 2026 | 32 | 0.53 | 35,596.70 | 1,112.40 | 1.72 | 1.88 | 4.28 | 2.14 | 3.71 | 4.41 | 12,100.75 |
| ONBML | no_ML | 2023 | 115 | 0.46 | 22,783.05 | 198.11 | 1.21 | 1.20 | 2.21 | 1.31 | 2.65 | 5.97 | 8,430.50 |
| ONBML | no_ML | 2024 | 128 | 0.51 | 71,734.00 | 560.42 | 2.63 | 2.56 | 5.43 | 1.79 | 8.57 | 5.40 | 8,141.00 |
| ONBML | no_ML | 2025 | 113 | 0.50 | 4,422.75 | 39.14 | 0.15 | 0.15 | 0.23 | 1.04 | 0.17 | 10.45 | 25,002.20 |
| ONBML | no_ML | 2026 | 94 | 0.47 | 41,358.00 | 439.98 | 1.25 | 1.40 | 2.64 | 1.38 | 3.27 | 7.19 | 15,927.10 |
| ONBML | no_calendar | 2023 | 31 | 0.35 | 4,737.15 | 152.81 | 0.43 | 0.43 | 0.83 | 1.21 | 0.62 | 8.11 | 7,482.40 |
| ONBML | no_calendar | 2024 | 21 | 0.52 | 15,487.95 | 737.52 | 1.27 | 1.23 | 2.87 | 2.09 | 2.55 | 2.43 | 5,899.15 |
| ONBML | no_calendar | 2025 | 25 | 0.56 | 5,680.95 | 227.24 | 0.30 | 0.30 | 0.46 | 1.16 | 0.24 | 16.44 | 23,369.45 |
| ONBML | no_calendar | 2026 | 16 | 0.50 | 25,787.60 | 1,611.72 | 1.55 | 1.67 | 4.25 | 2.66 | 3.10 | 5.31 | 10,466.80 |
| ONBML | no_price | 2023 | 30 | 0.53 | 14,401.90 | 480.06 | 1.45 | 1.41 | 3.08 | 1.92 | 3.20 | 4.04 | 4,410.95 |
| ONBML | no_price | 2024 | 39 | 0.62 | 39,170.25 | 1,004.37 | 2.55 | 2.38 | 6.99 | 3.06 | 9.29 | 2.62 | 4,103.80 |
| ONBML | no_price | 2025 | 43 | 0.60 | 26,405.45 | 614.08 | 1.50 | 1.47 | 2.89 | 1.82 | 3.43 | 3.16 | 7,539.55 |
| ONBML | no_price | 2026 | 31 | 0.52 | 32,177.85 | 1,038.00 | 1.47 | 1.62 | 3.56 | 1.92 | 3.76 | 4.91 | 10,796.35 |
| ONBML | no_vol | 2023 | 81 | 0.42 | 6,878.05 | 84.91 | 0.44 | 0.44 | 0.77 | 1.12 | 0.47 | 11.94 | 14,433.10 |
| ONBML | no_vol | 2024 | 90 | 0.52 | 52,585.40 | 584.28 | 2.28 | 2.22 | 4.73 | 1.84 | 5.33 | 3.85 | 9,599.65 |
| ONBML | no_vol | 2025 | 86 | 0.55 | 25,508.80 | 296.61 | 0.91 | 0.91 | 1.55 | 1.29 | 1.25 | 8.18 | 19,967.90 |
| ONBML | no_vol | 2026 | 71 | 0.48 | 35,813.65 | 504.42 | 1.23 | 1.37 | 2.65 | 1.44 | 2.88 | 6.02 | 15,693.60 |
| Tfade | original | 2023 | 24 | 0.50 | 5,581.00 | 232.54 | 1.03 | 1.02 | 2.01 | 1.73 | 1.48 | 3.54 | 3,709.75 |
| Tfade | original | 2024 | 33 | 0.58 | 11,950.75 | 362.14 | 1.44 | 1.40 | 2.68 | 1.92 | 2.33 | 3.60 | 4,993.25 |
| Tfade | original | 2025 | 45 | 0.51 | 7,023.75 | 156.08 | 0.53 | 0.53 | 0.86 | 1.22 | 0.61 | 6.27 | 11,289.25 |
| Tfade | original | 2026 | 28 | 0.64 | 12,717.00 | 454.18 | 1.31 | 1.45 | 2.68 | 1.84 | 4.09 | 3.15 | 3,914.50 |
| Tfade | no_heavy_gate | 2023 | 257 | 0.49 | 2,841.75 | 11.06 | 0.22 | 0.22 | 0.32 | 1.04 | 0.19 | 8.85 | 14,636.00 |
| Tfade | no_heavy_gate | 2024 | 259 | 0.47 | -5,462.75 | -21.09 | -0.34 | -0.34 | -0.48 | 0.95 | -0.24 | 11.35 | 21,918.50 |
| Tfade | no_heavy_gate | 2025 | 257 | 0.49 | 11,211.75 | 43.63 | 0.49 | 0.49 | 0.73 | 1.08 | 0.40 | 12.85 | 27,411.00 |
| Tfade | no_heavy_gate | 2026 | 200 | 0.49 | 19,695.00 | 98.47 | 0.78 | 0.88 | 1.39 | 1.15 | 1.40 | 12.16 | 17,683.00 |
| Tfade | follow_night | 2023 | 24 | 0.46 | -5,754.00 | -239.75 | -1.20 | -1.18 | -1.35 | 0.54 | -0.62 | 13.70 | 9,057.50 |
| Tfade | follow_night | 2024 | 33 | 0.42 | -13,484.25 | -408.61 | -1.74 | -1.67 | -1.95 | 0.47 | -0.77 | 15.32 | 17,011.00 |
| Tfade | follow_night | 2025 | 45 | 0.49 | -3,166.25 | -70.36 | -0.24 | -0.24 | -0.33 | 0.92 | -0.21 | 15.89 | 14,457.75 |
| Tfade | follow_night | 2026 | 28 | 0.36 | -12,688.00 | -453.14 | -1.27 | -1.42 | -1.72 | 0.55 | -1.03 | 21.36 | 15,538.50 |
| Tfade | at_bell | 2023 | 24 | 0.50 | 4,276.00 | 178.17 | 0.74 | 0.74 | 1.36 | 1.48 | 0.82 | 4.75 | 5,114.75 |
| Tfade | at_bell | 2024 | 33 | 0.61 | 13,005.75 | 394.11 | 1.51 | 1.47 | 2.92 | 2.04 | 2.76 | 3.41 | 4,583.25 |
| Tfade | at_bell | 2025 | 45 | 0.49 | 3,573.75 | 79.42 | 0.27 | 0.27 | 0.43 | 1.10 | 0.30 | 6.83 | 11,869.25 |
| Tfade | at_bell | 2026 | 28 | 0.61 | 6,512.00 | 232.57 | 0.65 | 0.73 | 1.18 | 1.36 | 1.34 | 4.32 | 6,139.50 |
| Tfade | no_stop | 2023 | 24 | 0.50 | 6,231.00 | 259.62 | 1.19 | 1.17 | 2.52 | 1.88 | 2.00 | 2.86 | 3,059.75 |
| Tfade | no_stop | 2024 | 33 | 0.58 | 12,540.75 | 380.02 | 1.54 | 1.49 | 2.93 | 2.02 | 2.97 | 3.46 | 4,103.25 |
| Tfade | no_stop | 2025 | 45 | 0.51 | 2,938.75 | 65.31 | 0.21 | 0.21 | 0.31 | 1.08 | 0.19 | 9.17 | 14,904.25 |
| Tfade | no_stop | 2026 | 28 | 0.64 | 11,792.00 | 421.14 | 1.17 | 1.31 | 2.26 | 1.73 | 3.26 | 3.44 | 4,559.00 |
