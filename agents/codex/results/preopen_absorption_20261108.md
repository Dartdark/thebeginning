# Pre-open signed-flow absorption: REJECT

Summary: Five transported NQ files verified byte-for-byte;1,755,357 native bars support an exploratory design screen.
The absorption rule loses$6,386.50 per NQ on34trades,t−1.17,PF0.55; one-minute delay loses$7,006.50.
Both long and short sides lose, and every year with an absorption trade loses;2018 has no signals.
Heavy-total-volume comparator earns$37,658,t2.59, but repeats a known T-style mechanism and is not selectable.
No new strategy selected, later-period replay, funded/evaluation/personal bench, PowerLanguage or plan/live change.

Plan: `agents/codex/plans/preopen_absorption_20261108.md`, committed `e2d85b7` before returns.
Evidence: `agents/codex/evidence/preopen_absorption_20261108.md`.
Script: `analysis/codex_preopen_absorption_20261108.py`.
Reporter: `analysis/codex_preopen_absorption_report_20261108.py`.
Output: `analysis/outputs/codex_preopen_absorption_20261108/`.
No-return audit committed `ce84389` before design execution. Five registered definitions: four signal rules
(including three comparators) plus one mandatory delay stress. One eligible new candidate, Absorption.
Keep all prior T/flow searches,18ingredient cases and the failed five-case price-only handoff as selection history.
No implementation rerun, post-result parameter change or side/direction rescue in this study.

## Rule (as tested)

On NQ, use the overnight price move from the first observed bar OPEN after previous17:01 through current
08:28CTclose. Fade that direction. The price-only confirmation requires the last15-minute move08:14–08:28
to stall/reverse relative to the overnight direction. Absorption additionally requires last15-minute signed
aggressor volume to agree with the overnight direction, with absolute signed-volume share at least its own
previous60valid observations' median (minimum20). Today never enters its own median.

The comparator HeavyTotal requires native total night volume>1.4times the previous20valid nights' median.
It is an explicitly TOTAL-volume comparison, not a reconstruction of native PowerLanguage up-tick Volume.
PlainFade trades all admitted nonzero overnight moves. All four share entry/exits/costs/calendar.
Absorption is a pure subset of both PlainFade and PriceOnly on side, entry, exit and net cash.

Feature cutoff08:28close, with a full minute allowed for assumed receipt/processing; enter08:30-labelled
OPEN at08:29civil CT, before the cash bell. Delayed case enters08:31-labelled OPEN at08:30civil CT.
Exit08:45-labelled OPEN at08:44civil CT. The scheduled OPEN exit precedes that bar's intrabar stop.
Stop0.40times mean high-low range of previous20fully observed08:31–15:00RTHsessions, rounded adversely
onto the0.25tick, active on the entry bar. Gap stop fills at worse OPEN/stop. No TP, BE, trail or re-entry.
This uses inherited T timing/range risk, not the later09:00opening-handoff clock that already failed.

Historical receipt/corrections are unknown; the1-minute allowance is an exploratory assumption, not certified
point-in-time availability. Raw-price stop geometry and modeled slippage follow the preregistered source-style
cash bridge; native broker anchoring/tick fills are not independently established.

## Results

2018-01-01–2022-12-30 design, one fixed NQ contract,$20/point; commission$7.25round trip and one adverse
tick per entry/market-stop exit=$17.25total cost. Native1MNQ ledger uses$2/point,$1.25commission and$1slippage.
All values are total period dollars, not annual dollars, payouts, recommended leverage or a current-book result.
The whole source trading calendar has1,291dates (confirmed in the audit receipt); skipped/nontrading events
carry zero cash for ratios. Common eligible event universe1,022dates. Native2017warm-up wasn't supplied, so
the first21source calendar mornings lack required prior histories and are excluded openly.

### Five fixed cases
| case | trades | total | avg | t_trade | profit_factor | sharpe | max_dd | native_mnq_total | worst_trade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PlainFade | 1022 | -2,134.50 | -2.09 | -0.08 | 0.99 | -0.04 | 25,967.50 | -750.00 | -3,172.25 |
| PriceOnly | 459 | -24,437.75 | -53.24 | -1.37 | 0.84 | -0.60 | 28,117.00 | -2,684.75 | -3,172.25 |
| HeavyTotal | 203 | 37,658.25 | 185.51 | 2.59 | 1.63 | 1.13 | 7,212.50 | 3,659.25 | -2,652.25 |
| Absorption | 34 | -6,386.50 | -187.84 | -1.17 | 0.55 | -0.52 | 8,013.50 | -656.50 | -2,652.25 |
| Absorption_delay1m | 34 | -7,006.50 | -206.07 | -1.25 | 0.52 | -0.55 | 8,433.00 | -718.50 | -3,092.25 |

Absorption fails before any subtle comparison: gross−$5,800,net−$6,386.50,PF0.55,t−1.17. Its modeled native
1MNQ total is−$656.50. Delaying another minute and adding another tick per leg both remain negative.
The t statistic is descriptive and not selection-adjusted; a negative result does not need statistical
significance to fail the registered positive-edge screen. Both trade directions lose.

PlainFade's gross edge is too small for its costs. PriceOnly loses even before fees. HeavyTotal is positive,
consistent with a known activity-conditioned fade family, but it is a comparator frozen before outcomes.
Its positive result cannot replace the failed candidate or establish a new book contribution. It changes the
original native T volume field/cutoff, warm-up and admission, so old T verification/portfolio gains do not transfer.

### Cash and native-cost reconciliation
| case | trades | gross | commission | slippage | net | native_mnq_net | extra_tick_net |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Absorption | 34 | -5,800.00 | 246.50 | 340.00 | -6,386.50 | -656.50 | -6,726.50 |
| PlainFade | 1022 | 15,495.00 | 7,409.50 | 10,220.00 | -2,134.50 | -750.00 | -12,354.50 |
| HeavyTotal | 203 | 41,160.00 | 1,471.75 | 2,030.00 | 37,658.25 | 3,659.25 | 35,628.25 |
| Absorption_delay1m | 34 | -6,420.00 | 246.50 | 340.00 | -7,006.50 | -718.50 | -7,346.50 |
| PriceOnly | 459 | -16,520.00 | 3,327.75 | 4,590.00 | -24,437.75 | -2,684.75 | -29,027.75 |

Gross, fees, slippage, daily/trade net and native-micro totals reconcile to half a cent. Native MNQ net is
not NQ net divided by10, because the modeled native commission differs. Initial-zero-peak daily DD is used;
that DD excludes intraday open-loss marks and is not an Apex floor-risk estimate.

## Input admission, timing and gaps

Five gzip objects and all five decompressed CSVs match the exact transfer-manifest sizes/SHA256s; original
CSV bytes sum109,365,550. Native row count1,755,357. All inspected rows have valid quarter-tick OHLC,
finite nonnegative integer volumes, no duplicate CT timestamps and total=buy+sell. ET close labels convert
using America/New_York→America/Chicago, including DST, with no added minute. Year files concatenate before
night features. Only native prices/quantities are used; the older owned NQ CSVs provide calendar dates only.
No source, legacy export or cached grid is overwritten, backfilled or spliced.

Fields UpVol/DownVol are documented by the vendor as aggressor buy/sell volume. This is a source claim,
not independent reconstruction from raw trade/quote messages. It is not ordinary tick-direction volume.
The earlier OF export's misleading total-volume field is never used; native total is the verified sum.
Original contract/build/roll/adjustment map, exceptional-side classification and historical receipt remain
unverified. Thus even a profitable screen would remain conditional research, not native/live readiness.

Eligibility requires>=836of928nominal overnight closes and an observed08:28end, plus complete last15-minute
features. Missing bars stay missing. Known history only is used. The prior daily-range history takes20complete
native cash sessions; partial sessions do not silently supply underestimated ranges. No unknown held execution
minutes survive; the same execution-path admission applies to all normal/delay cases.

Exclusions:236declared quarterly roll-calendar dates,21warm-up,9night-coverage/decision-close dates and3zero
night directions. The calendar restriction is dates5–21ofMarch/June/September/December; it is deliberately
broader than exact rolls and is not a future-largest-gap splice. Residual roll risk persists. Coverage excludes
stress dates; do not generalize the retained sample to missing limit/halts or claim protection on those dates.
The nine overnight data/coverage exclusions are listed below. No extra post-result exclusions were added.
| date | reason |
| --- | --- |
| 2019-02-27 | night_coverage_or_decision_close |
| 2020-03-09 | night_coverage_or_decision_close |
| 2020-03-12 | night_coverage_or_decision_close |
| 2020-03-13 | night_coverage_or_decision_close |
| 2020-03-16 | night_coverage_or_decision_close |
| 2020-03-17 | night_coverage_or_decision_close |
| 2020-03-18 | night_coverage_or_decision_close |
| 2020-07-01 | night_coverage_or_decision_close |
| 2021-04-02 | night_coverage_or_decision_close |

Pre-return counts were PlainFade1,022;PriceOnly459;HeavyTotal203;Absorption34. Under the assumed$1,000NQ
trade SD,34events need about$343net/trade for t2, before dependence/selection corrections. Actual data only
barely meet the30-event cheap minimum; no threshold was loosened. Ten synthetic fixture groups cover modeled
long/short entry stops, gaps, adverse rounding, exit-OPEN priority, delay anchoring, missing-path rejection,
clock conversion and native fees. They are implementation checks, not native MC/broker verification.

## Placebos and account level

Both nested comparisons pass exact common-date trade identity. Removing PlainFade opportunities discards
+$4,252net,mean+$4.30,t0.17. Removing PriceOnly opportunities discards−$18,051,mean−$42.47,t−1.06;
that comparison reduces losses but does not turn Absorption profitable. Neither comparison beats matched-count
random subsets on profit or DD at the registered<=5%shares. Counts are matched within calendar year,1000runs,
seed20261108; descriptive null shares are not multiple-testing-adjusted p-values.
| parent | removed_n | removed_total | removed_mean | removed_t | random_profit_ge_actual | random_dd_le_actual |
| --- | --- | --- | --- | --- | --- | --- |
| PlainFade | 988 | 4,252.00 | 4.30 | 0.17 | 0.89 | 0.86 |
| PriceOnly | 425 | -18,051.25 | -42.47 | -1.06 | 0.84 | 0.80 |

Paired candidate-minus-parent daily cash deltas use1000moving20-session blocks. Total is period dollars;
percentile columns are annualized dollars on the full source trading-date calendar. Both intervals contain
zero, so neither meets the required positiveP5incremental gate.
| parent | total | annual_p5 | annual_p50 | annual_p95 |
| --- | --- | --- | --- | --- |
| PlainFade | -4,252.00 | -8,681.63 | -1,059.97 | 6,045.30 |
| PriceOnly | 18,051.25 | -2,004.20 | 2,821.21 | 8,239.32 |

The registered design gate fails. No2023+native file acquisition/replay, random-direction replay, MonteCarlo,
funded/evaluation/personal BASE/ADD/REPLACE/EMPTY, new forward promotion or PowerLanguage stage followed.
Neither improved payouts nor reduced account blow-up risk is established. Missing later/account results are
intentional stop-rule outcomes, not placeholders to be filled by reopening a failed strategy.

### Every registered gate
| gate | passed |
| --- | --- |
| trades_ge30 | True |
| gross_net_positive | False |
| t_ge2 | False |
| PF_ge1_2 | False |
| positive_years_ge3 | False |
| delay_positive | False |
| extra_tick_cost_positive | False |
| PlainFade_net_beaten | False |
| PlainFade_DD_not_worse | True |
| PlainFade_Sharpe_not_worse | False |
| PlainFade_pure_filter | True |
| PlainFade_removed_negative | False |
| PlainFade_random_profit | False |
| PlainFade_random_DD | False |
| PlainFade_paired_p5 | False |
| PriceOnly_net_beaten | True |
| PriceOnly_DD_not_worse | True |
| PriceOnly_Sharpe_not_worse | True |
| PriceOnly_pure_filter | True |
| PriceOnly_removed_negative | True |
| PriceOnly_random_profit | False |
| PriceOnly_random_DD | False |
| PriceOnly_paired_p5 | False |

## Scientific context: five source questions

1. About: persistent signed trading and adaptive liquidity in LSE stocks.
2. Finding: liquidity responses can offset predictable flow and bound price impact.
3. Profit: no net NQ strategy is demonstrated; stalled impact need not reverse.
4. Build on it: it motivates measuring flow versus response; the NQ/opening prediction is ours.
5. Code: this minute-volume screen is implementable; exact source replication needs trade/quote events.

Primary full source: Farmer/Gerig/Lillo/Mike2006, https://arxiv.org/html/physics/0602015 . It supplies conceptual
context and a warning, not numerical parameters or proof of our forecast. This is not a paper replication.

## What could make this wrong

Small sample, selected prior ideas, source classification, unresolved rolls/builds/receipt and missing stress
sessions limit inference. Minute OHLC cannot certify the sequence of trades, spread, queue, liquidity-provider
identity or actual latency. A stop does not establish safety on an Apex account. There is no quote-based
absorption measurement here: flow-price disagreement is an explicitly declared observable hypothesis.
No independent economic checker or native MC confirmation was performed for these new rules. Conditional
source audit/synthetic parity and two models agreeing would still not establish a profitable/live strategy.

## MultiCharts differences and outcome

No new PowerLanguage code, chart modification or plan change because design failed. Python uses native
aggressor categories; original T's up-tick classifier is a different input. One-minute receipt allowance and
08:28feature cutoff are explicit changes from the existing T source. No later side/weekday/threshold/follow
variant is authorized by this result. Original strategies retain their existing review/ranking status.

## Whole / long / short

`win` is a fraction; PF is per trade. Ratios use the full common calendar with zero cash on skipped dates,
and$50,000reporting capital. A zero-event year has no inferential t/PF; dashes indicate unavailable ratios.
| case | side | trades | win | total | avg | t_trade | sharpe | sortino | profit_factor | calmar | ulcer | max_dd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PlainFade | all | 1022 | 0.50 | -2,134.50 | -2.09 | -0.08 | -0.04 | -0.05 | 0.99 | -0.02 | 21.04 | 25,967.50 |
| PlainFade | long | 449 | 0.53 | 5,974.75 | 13.31 | 0.31 | 0.14 | 0.20 | 1.04 | 0.08 | 7.67 | 15,492.50 |
| PlainFade | short | 573 | 0.49 | -8,109.25 | -14.15 | -0.45 | -0.20 | -0.28 | 0.95 | -0.09 | 21.10 | 18,155.50 |
| PriceOnly | all | 459 | 0.49 | -24,437.75 | -53.24 | -1.37 | -0.60 | -0.80 | 0.84 | -0.17 | 29.72 | 28,117.00 |
| PriceOnly | long | 206 | 0.51 | -17,883.50 | -86.81 | -1.34 | -0.59 | -0.75 | 0.78 | -0.18 | 16.41 | 19,119.50 |
| PriceOnly | short | 253 | 0.47 | -6,554.25 | -25.91 | -0.56 | -0.25 | -0.34 | 0.91 | -0.09 | 15.97 | 14,843.50 |
| HeavyTotal | all | 203 | 0.62 | 37,658.25 | 185.51 | 2.59 | 1.13 | 1.89 | 1.63 | 1.02 | 2.38 | 7,212.50 |
| HeavyTotal | long | 120 | 0.64 | 27,580.00 | 229.83 | 2.32 | 1.01 | 1.74 | 1.76 | 1.06 | 2.08 | 5,061.00 |
| HeavyTotal | short | 83 | 0.59 | 10,078.25 | 121.42 | 1.20 | 0.53 | 0.83 | 1.42 | 0.51 | 2.88 | 3,880.25 |
| Absorption | all | 34 | 0.41 | -6,386.50 | -187.84 | -1.17 | -0.52 | -0.63 | 0.55 | -0.16 | 6.90 | 8,013.50 |
| Absorption | long | 16 | 0.38 | -5,131.00 | -320.69 | -1.31 | -0.56 | -0.62 | 0.36 | -0.15 | 6.07 | 6,684.25 |
| Absorption | short | 18 | 0.44 | -1,255.50 | -69.75 | -0.33 | -0.15 | -0.21 | 0.80 | -0.11 | 1.56 | 2,246.75 |
| Absorption_delay1m | all | 34 | 0.38 | -7,006.50 | -206.07 | -1.25 | -0.55 | -0.66 | 0.52 | -0.16 | 7.18 | 8,433.00 |
| Absorption_delay1m | long | 16 | 0.38 | -5,861.00 | -366.31 | -1.42 | -0.61 | -0.65 | 0.32 | -0.16 | 6.58 | 7,153.75 |
| Absorption_delay1m | short | 18 | 0.39 | -1,145.50 | -63.64 | -0.30 | -0.14 | -0.20 | 0.81 | -0.10 | 1.39 | 2,176.75 |

## By year, all sides

| case | period | trades | win | total | avg | t_trade | sharpe | sortino | profit_factor | calmar | ulcer | max_dd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PlainFade | 2018 | 184 | 0.51 | -3,699.00 | -20.10 | -0.52 | -0.52 | -0.75 | 0.90 | -0.35 | 8.59 | 10,339.75 |
| PlainFade | 2019 | 206 | 0.46 | -10,188.50 | -49.46 | -1.87 | -1.85 | -2.41 | 0.72 | -0.65 | 16.07 | 15,233.25 |
| PlainFade | 2020 | 211 | 0.53 | 10,610.25 | 50.29 | 0.91 | 0.90 | 1.38 | 1.18 | 1.30 | 5.75 | 7,990.00 |
| PlainFade | 2021 | 212 | 0.55 | 5,763.00 | 27.18 | 0.48 | 0.48 | 0.68 | 1.09 | 0.57 | 9.24 | 9,821.00 |
| PlainFade | 2022 | 209 | 0.48 | -4,620.25 | -22.11 | -0.25 | -0.25 | -0.35 | 0.96 | -0.17 | 21.95 | 25,967.50 |
| PriceOnly | 2018 | 74 | 0.47 | -4,116.50 | -55.63 | -0.91 | -0.90 | -1.17 | 0.77 | -0.51 | 7.13 | 7,913.75 |
| PriceOnly | 2019 | 88 | 0.41 | -6,088.00 | -69.18 | -1.69 | -1.66 | -2.14 | 0.63 | -0.68 | 9.25 | 8,779.50 |
| PriceOnly | 2020 | 102 | 0.48 | -7,304.50 | -71.61 | -1.03 | -1.02 | -1.31 | 0.77 | -0.81 | 8.77 | 8,763.75 |
| PriceOnly | 2021 | 106 | 0.58 | 5,986.50 | 56.48 | 0.63 | 0.63 | 0.91 | 1.17 | 0.62 | 8.69 | 9,331.00 |
| PriceOnly | 2022 | 89 | 0.48 | -12,915.25 | -145.12 | -1.07 | -1.06 | -1.34 | 0.76 | -0.81 | 17.29 | 15,578.00 |
| HeavyTotal | 2018 | 43 | 0.65 | 6,348.25 | 147.63 | 1.54 | 1.50 | 3.03 | 1.97 | 3.95 | 0.86 | 1,569.50 |
| HeavyTotal | 2019 | 40 | 0.60 | 2,965.00 | 74.12 | 0.97 | 0.96 | 1.56 | 1.45 | 0.97 | 2.24 | 2,977.50 |
| HeavyTotal | 2020 | 34 | 0.68 | 14,203.50 | 417.75 | 2.09 | 1.99 | 4.01 | 2.51 | 4.16 | 1.81 | 3,331.75 |
| HeavyTotal | 2021 | 49 | 0.59 | 8,114.75 | 165.61 | 1.04 | 1.03 | 1.69 | 1.45 | 1.09 | 6.04 | 7,212.50 |
| HeavyTotal | 2022 | 37 | 0.59 | 6,026.75 | 162.89 | 0.67 | 0.67 | 1.01 | 1.31 | 1.06 | 2.76 | 5,561.50 |
| Absorption | 2018 | 0 | — | 0.00 | — | — | — | — | — | — | 0.00 | -0.00 |
| Absorption | 2019 | 7 | 0.14 | -860.75 | -122.96 | -1.71 | -1.50 | -1.69 | 0.23 | -0.98 | 1.38 | 860.75 |
| Absorption | 2020 | 7 | 0.57 | -525.75 | -75.11 | -0.28 | -0.29 | -0.33 | 0.73 | -0.29 | 1.82 | 1,764.50 |
| Absorption | 2021 | 11 | 0.36 | -3,974.75 | -361.34 | -1.51 | -1.41 | -1.57 | 0.26 | -0.85 | 6.88 | 4,556.25 |
| Absorption | 2022 | 9 | 0.56 | -1,025.25 | -113.92 | -0.22 | -0.23 | -0.30 | 0.83 | -0.38 | 2.53 | 2,652.25 |
| Absorption_delay1m | 2018 | 0 | — | 0.00 | — | — | — | — | — | — | 0.00 | -0.00 |
| Absorption_delay1m | 2019 | 7 | 0.14 | -940.75 | -134.39 | -2.11 | -1.71 | -1.84 | 0.18 | -0.98 | 1.36 | 940.75 |
| Absorption_delay1m | 2020 | 7 | 0.57 | -225.75 | -32.25 | -0.14 | -0.14 | -0.17 | 0.85 | -0.15 | 1.37 | 1,479.50 |
| Absorption_delay1m | 2021 | 11 | 0.27 | -4,164.75 | -378.61 | -1.56 | -1.45 | -1.62 | 0.26 | -0.86 | 7.13 | 4,708.50 |
| Absorption_delay1m | 2022 | 9 | 0.56 | -1,675.25 | -186.14 | -0.35 | -0.36 | -0.44 | 0.74 | -0.53 | 3.03 | 3,101.75 |
