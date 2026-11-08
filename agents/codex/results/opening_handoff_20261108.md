# FC/ONB/T opening handoff combinations: REJECT

Summary: Two frozen price-based combinations fail the 2018–22 design screen; no new strategy selected.
Continuation:60 trades,+$24,015 per NQ,t1.62; reversal:58,+$8,255,t0.61.
Both remove profitable trades and have lower Sharpe/Calmar than the common opening-drive parent.
Neither beats the registered matched random-subset profit/DD gates; delay and extra-cost stress remain positive.
Stop: no 2023+ combination returns, account bench, MultiCharts code or plan/live changes.

Plan: `agents/codex/plans/opening_handoff_20261108.md`, original `99d6209`, adapter amendment `9a34a7d`.
Evidence: `agents/codex/evidence/opening_handoff_20261108.md`.
Script: `analysis/codex_opening_handoff_20261108.py`.
Reporter: `analysis/codex_opening_handoff_report_20261108.py`.
Output: `analysis/outputs/codex_opening_handoff_20261108/`.
Trials: five fixed economic cases (parent, two candidates, their two delay stresses), plus registered random-drop
controls. Retain the aborted exact-anchor protocol's three partial price replays as prior execution history.
The prior18-case ingredient study and all earlier component searches remain selection history. Not independent discovery.

## Rule (as tested)

**Common entry/exits:** after the completed first30-minute opening drive, trade its direction at the09:01
close-labelled bar OPEN (09:00 civil CT). Use FCv2's100-point entry-bar stop,150-point next-bar trailing stop,
through-close market-exit fallback and no target. Break-even disabled using the source BER>0 guard.
Normal flatten at14:59-labelled OPEN, early-close flatten at11:31. One entry/day, no compounding.

**Continuation:** require the opening drive, overnight move and ONB overnight-location bias to agree;
15-minute ADX14>30; the09:00 close must break the first15-minute range in the drive direction.

**Reversal:** the opening drive must reverse the overnight move, with the cash-open price in the overnight
range's corresponding outer third (a down night starts in the lower third, an up night in the upper third).
Use the same ADX and first15-minute breakout confirmation. T supplies the overnight fade direction;
ONB supplies location/breakout/ADX confirmation; FC supplies opening drive and exit management.
This is a later confirmed reversal, not T's original pre-open entry or heavy-volume rule.

**Parent:** all eligible nonzero first30-minute drives with identical entry/exits. The two mandatory delay
cases enter09:02-labelled OPEN with the stop anchored to that fill; they cannot become selected variants.

Night direction uses first observed bar OPEN from previous17:01 through current08:29 versus08:29close.
ONB range covers previous23:01 through current08:30; cash-open is08:31-labelled OPEN. All candidate
features mature by09:00, before entry. No source MC trade-list outcomes, native up-tick Volume, total-volume
proxy, full-history-fitted ML score, calendar coefficient selection or other future return is used.
The proposed continuation/reversal pressure mechanism is unverified; prices do not identify forced actors.

## Results

Design2018-01-01–2022-12-30,2017 warm-up. All dollars below are total period profit at **1NQ** (20$/point),
$7.25 round-trip commission plus1tick on each market/stop fill ($17.25 total). No target fills.
Native1MNQ uses2$/point and$1.25 commission plus$1 round-trip slippage. A smaller commission bridge
means native MNQ net is not simply NQ net divided by10. Zero-P&L skipped and admitted sessions remain in final reporting ratios.
These are standalone fixed-size research results, not payout dollars, annual returns or recommended sizes.

### Five fixed cases
| case | trades | total | avg | t_trade | profit_factor | sharpe | max_dd | calmar | native_mnq_total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Continuation_delay1m | 60 | 23,085.00 | 384.75 | 1.53 | 1.76 | 0.67 | 12,762.50 | 0.35 | 2,277.00 |
| Continuation | 60 | 24,015.00 | 400.25 | 1.62 | 1.81 | 0.71 | 13,087.50 | 0.36 | 2,370.00 |
| Parent | 1042 | 142,455.50 | 136.71 | 2.44 | 1.22 | 1.08 | 27,225.50 | 1.02 | 13,698.50 |
| Reversal_delay1m | 58 | 4,519.50 | 77.92 | 0.34 | 1.12 | 0.15 | 14,191.25 | 0.06 | 421.50 |
| Reversal | 58 | 8,254.50 | 142.32 | 0.61 | 1.24 | 0.27 | 13,289.00 | 0.12 | 795.00 |

The final standard ratios are recalculated from the saved cash ledgers on all1,289 source trading dates,
including zeros on declared roll-calendar skips and data exclusions. Original design gates/intervals used
the1,042 admitted-date denominator and are retained unchanged in design/metrics.csv and results.json.
This reporting correction changes no trade, P&L, candidate, threshold or failed selection. All full-calendar
ratios are in full_calendar_metrics.csv; the adverse original paired intervals below retain their labeled
research-admitted denominator and are not account/calendar-year forecasts.

Continuation concentrates to60 trades and raises average trade to$400, but t1.62 fails even the cheap t2
hurdle. Its Sharpe and Calmar are below the parent. Reversal has t0.61. Both are positive
in aggregate but lack the registered evidence needed to advance. The parent itself has t2.44 and is only
a comparator, not a newly approved strategy. Continuation's larger mean/PF alone is not a pass.

### Data counts and execution checks

Common universe:1,042 sessions. Excluded241 declared quarterly-roll-calendar dates,4 sessions with unknown
execution paths and2 zero drives. The first30 minutes and execution paths are fully observed on admitted
sessions; no held minute is fabricated or forward-filled. Roll-calendar exclusions apply equally to all cases.
Candidate counts60/58 imply assumed t2 mean hurdles of$516/$525 using the predeclared$2,000 trade SD,
versus observed means$400/$142; that power assumption is not an economic validation.

Nine synthetic fixture groups pass: both entry-stop directions, adverse gap, next-bar trail, through-close
fallback, BE genuinely off, normal/early flatten, delayed entry and native fees. These verify modeled code,
not actual MultiCharts/broker fills. The independent source FCv2 exit port is reused; no native parity for
these new combinations is claimed. Gross-to-net and daily/trade/native-micro sums reconcile to half a cent.
| case | trades | gross | commission | slippage | net | native_mnq_net | missing_held_minutes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Continuation_delay1m | 60 | 24,120.00 | 435.00 | 600.00 | 23,085.00 | 2,277.00 | 0 |
| Continuation | 60 | 25,050.00 | 435.00 | 600.00 | 24,015.00 | 2,370.00 | 0 |
| Parent | 1042 | 160,430.00 | 7,554.50 | 10,420.00 | 142,455.50 | 13,698.50 | 0 |
| Reversal_delay1m | 58 | 5,520.00 | 420.50 | 580.00 | 4,519.50 | 421.50 | 0 |
| Reversal | 58 | 9,255.00 | 420.50 | 580.00 | 8,254.50 | 795.00 | 0 |

### Adapter failure retained

Original committed99d6209 erroneously required an exact17:01 source bar. Most exports lack that minute;
only35 parent events,3 continuation events and0 reversal events were admitted. The process replayed35 parent
and3+3 continuation/delay trades in memory, then failed normalizing the empty reversal dataframe. No
candidate economic summary from this attempt was printed or inspected, but those partial looks are retained.
The feature receipt, exclusions and traceback are in `aborted_exact_anchor/`; they are not erased or claimed
zero-return work. Source T actually uses the first observed reopening bar. The data-adapter/universe amendment
and empty numeric-dtype fix were committed9a34a7d before corrected returns. No clock or parameter was chosen
using P&L. The corrected protocol changes admission materially, as explicitly recorded in the plan.
Do not interpret the five nominal definitions as five untouched historical looks; these are source-informed
rules with prior component testing plus the retained partial adapter attempt.

## Placebos and account level

Both candidates are pure nested filters of the parent: retained date/side/entry/exit/net match exactly.
The excluded parent trades earn money: continuation removes982 trades averaging+$120.61,t2.10;
reversal removes984 averaging+$136.38,t2.37. Both fail the requirement that the filter remove losing trades.
Each was compared with1,000 within-year equal-count random subsets, seed20261108. Profit exceedance is
15.3% for continuation and45.7% for reversal, above the required<=5%; DD-no-worse shares68.9%/67.6%
also fail<=5%. These descriptive shares are not selection-adjusted p-values.
| case | removed_n | removed_total | removed_mean | removed_t | random_profit_ge_actual | random_dd_le_actual |
| --- | --- | --- | --- | --- | --- | --- |
| Continuation | 982 | 118,440.50 | 120.61 | 2.10 | 0.15 | 0.69 |
| Reversal | 984 | 134,201.00 | 136.38 | 2.37 | 0.46 | 0.68 |

Paired candidate-minus-parent daily cash differences use1,000 moving20-session blocks. The total delta
is period dollars; percentile intervals below are annualized dollars. Both intervals are entirely negative.
They measure this realized filtered-parent comparison, not the probability a strategy will fail in future.
| case | total | annual_p5 | annual_p50 | annual_p95 |
| --- | --- | --- | --- | --- |
| Continuation | -118,440.50 | -47,159.58 | -27,123.31 | -10,201.71 |
| Reversal | -134,201.00 | -50,731.32 | -30,884.84 | -12,005.28 |

Both candidates remain positive under the fixed one-minute delay and another1tick/leg fee stress. Those
checks do not compensate for failed significance/profit/filter gates. Because neither design candidate
passes, **no recent-return replay, random-side replay, Monte Carlo, current-book BASE/ADD/REPLACE/EMPTY,
funded/evaluation bench, forward promotion or MultiCharts code stage is run**. These are intentionally missing,
not invented. Prior component research on2023+ is already seen; this study did not compute new combination
returns there. No improvement to evaluation, funded or personal portfolios is established.

### Gate record
| check | Continuation | Reversal |
| --- | --- | --- |
| trades_min | True | True |
| gross_net_positive | True | True |
| t_ge2 | False | False |
| PF_ge1_2 | True | True |
| positive_years | True | True |
| net_beats_parent | False | False |
| DD_not_worse_parent | True | True |
| Sharpe_not_worse_parent | False | False |
| pure_nested_filter | True | True |
| removed_negative_t | False | False |
| random_profit | False | False |
| random_DD | False | False |
| paired_annual_p5 | False | False |
| delay_positive | True | True |
| extra_tick_cost_positive | True | True |

## What could make this wrong

- These are price-only combinations of selected existing ingredients. Missing native up-tick gates are omitted
  openly; a claim about a full FC+T volume hybrid would need those inputs and a separate registered protocol.
- Both source history and the preceding ingredient outputs informed the definitions. Recent history is already
  known and no fresh historical holdout exists; no independence or causal flow discovery is claimed.
- Sparse60/58 event sets make averages uncertain. A profitable net number can arise from a few large trades.
  Side/year tables below are diagnostics and do not authorize a post-hoc long-only, short-only or year filter.
- Daily realized drawdown omits open trade marks. A100-point MNQ stop models roughly$202.25 loss before gaps;
  account cushion, simultaneous strategies and floor touches require an earned chronological replay.
- Fixed100/150-point exits are inherited, not optimized for price level. One-minute OHLC misses tick order,
  queueing and actual bid/ask spread. Modeled slippage does not measure execution quality.
- Calendar dates5–21 of quarterly months are excluded before entry as a conservative roll precaution. This is
  broader than exact roll dates and cannot guarantee all seams are gone. No global largest-gap adjustment or
  future-aware roll signal was applied. The4 incomplete-path exclusions are research data admission; a live
  strategy cannot know future data quality. All candidates share the same admitted universe, and final reporting restores excluded dates as cash zeros.
- Reusing FC exit logic shifts the proposed T reversal into a later confirmation/longer holding interval.
  The original T signal's short pre-open edge does not establish a later continuation of that reversal.
- The maker has reconciled cash and synthetic execution; independent Claude/native verification is pending.
  No TIER, plan, live, broker, VPS, API-key, paid-data, scout-state or schedule change was made.

## Differences between MultiCharts code and the test

No new PowerLanguage code was written because the design gates failed. The Python source port uses FCv2
exit chronology with new price-derived admission, removes source volume selection and disables BE as declared.
It does not reproduce the native FC or T classifier, nor reuse the fitted ONB ML model. No deployment proposed.

## Whole / long / short results

`win` is a fraction; ratios use the full common trading calendar and$50,000 reporting capital. MaxDD uses initial
zero peak. This reporting capital does not establish required margin or safe account size.
| case | side | trades | win | total | avg | t_trade | sharpe | sortino | profit_factor | calmar | ulcer | max_dd | worst_trade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Continuation_delay1m | all | 60 | 0.57 | 23,085.00 | 384.75 | 1.53 | 0.67 | 1.50 | 1.76 | 0.35 | 4.06 | 12,762.50 | -2,017.25 |
| Continuation_delay1m | long | 26 | 0.58 | 2,741.50 | 105.44 | 0.35 | 0.16 | 0.25 | 1.20 | 0.11 | 4.41 | 4,946.75 | -2,017.25 |
| Continuation_delay1m | short | 34 | 0.56 | 20,343.50 | 598.34 | 1.58 | 0.68 | 1.86 | 2.24 | 0.51 | 2.56 | 7,815.75 | -2,017.25 |
| Continuation | all | 60 | 0.55 | 24,015.00 | 400.25 | 1.62 | 0.71 | 1.59 | 1.81 | 0.36 | 4.09 | 13,087.50 | -2,017.25 |
| Continuation | long | 26 | 0.58 | 2,046.50 | 78.71 | 0.26 | 0.12 | 0.18 | 1.14 | 0.08 | 4.76 | 5,156.75 | -2,017.25 |
| Continuation | short | 34 | 0.53 | 21,968.50 | 646.13 | 1.76 | 0.75 | 2.23 | 2.45 | 0.54 | 2.46 | 7,930.75 | -2,017.25 |
| Parent | all | 1042 | 0.48 | 142,455.50 | 136.71 | 2.44 | 1.08 | 1.94 | 1.22 | 1.02 | 5.06 | 27,225.50 | -2,017.25 |
| Parent | long | 548 | 0.51 | 70,787.00 | 129.17 | 1.74 | 0.77 | 1.32 | 1.21 | 0.41 | 8.87 | 34,077.75 | -2,017.25 |
| Parent | short | 494 | 0.45 | 71,668.50 | 145.08 | 1.71 | 0.76 | 1.43 | 1.23 | 0.70 | 8.10 | 19,897.00 | -2,017.25 |
| Reversal_delay1m | all | 58 | 0.47 | 4,519.50 | 77.92 | 0.34 | 0.15 | 0.25 | 1.12 | 0.06 | 10.64 | 14,191.25 | -2,017.25 |
| Reversal_delay1m | long | 23 | 0.43 | -2,091.75 | -90.95 | -0.20 | -0.09 | -0.15 | 0.90 | -0.03 | 10.26 | 12,042.50 | -2,017.25 |
| Reversal_delay1m | short | 35 | 0.49 | 6,611.25 | 188.89 | 0.80 | 0.35 | 0.59 | 1.40 | 0.26 | 3.67 | 4,884.00 | -2,017.25 |
| Reversal | all | 58 | 0.48 | 8,254.50 | 142.32 | 0.61 | 0.27 | 0.47 | 1.24 | 0.12 | 10.13 | 13,289.00 | -2,017.25 |
| Reversal | long | 23 | 0.43 | -1,936.75 | -84.21 | -0.18 | -0.08 | -0.14 | 0.91 | -0.03 | 10.16 | 11,932.50 | -2,017.25 |
| Reversal | short | 35 | 0.51 | 10,191.25 | 291.18 | 1.23 | 0.54 | 1.01 | 1.72 | 0.44 | 2.97 | 4,524.00 | -2,017.25 |

## By year, all sides

| case | period | trades | win | total | avg | t_trade | sharpe | sortino | profit_factor | calmar | ulcer | max_dd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Continuation_delay1m | 2018 | 12 | 0.67 | 5,113.00 | 426.08 | 0.95 | 0.94 | 2.23 | 2.43 | 1.71 | 2.72 | 2,926.75 |
| Continuation_delay1m | 2019 | 15 | 0.53 | 3,986.25 | 265.75 | 0.72 | 0.72 | 1.49 | 1.72 | 1.45 | 2.26 | 2,683.50 |
| Continuation_delay1m | 2020 | 8 | 0.62 | 3,287.00 | 410.88 | 0.70 | 0.71 | 1.55 | 1.98 | 0.95 | 3.47 | 3,366.75 |
| Continuation_delay1m | 2021 | 9 | 0.56 | 3,579.75 | 397.75 | 0.65 | 0.66 | 1.53 | 1.82 | 0.80 | 3.41 | 4,344.00 |
| Continuation_delay1m | 2022 | 16 | 0.50 | 7,119.00 | 444.94 | 0.62 | 0.63 | 1.42 | 1.53 | 0.83 | 5.56 | 8,418.50 |
| Continuation | 2018 | 12 | 0.67 | 5,283.00 | 440.25 | 1.00 | 0.99 | 2.29 | 2.48 | 1.81 | 2.54 | 2,856.75 |
| Continuation | 2019 | 15 | 0.53 | 4,446.25 | 296.42 | 0.81 | 0.81 | 1.64 | 1.81 | 1.66 | 2.37 | 2,623.50 |
| Continuation | 2020 | 8 | 0.62 | 3,202.00 | 400.25 | 0.71 | 0.72 | 1.51 | 1.98 | 0.95 | 3.27 | 3,276.75 |
| Continuation | 2021 | 9 | 0.56 | 3,874.75 | 430.53 | 0.72 | 0.73 | 1.73 | 1.92 | 0.90 | 3.29 | 4,224.00 |
| Continuation | 2022 | 16 | 0.44 | 7,209.00 | 450.56 | 0.64 | 0.65 | 1.49 | 1.55 | 0.79 | 6.05 | 8,863.50 |
| Parent | 2018 | 203 | 0.49 | 34,443.25 | 169.67 | 1.64 | 1.62 | 3.04 | 1.38 | 6.32 | 2.92 | 5,343.00 |
| Parent | 2019 | 208 | 0.52 | 4,097.00 | 19.70 | 0.29 | 0.29 | 0.43 | 1.06 | 0.44 | 7.58 | 9,009.00 |
| Parent | 2020 | 211 | 0.51 | 37,120.25 | 175.93 | 1.37 | 1.35 | 2.38 | 1.27 | 2.76 | 7.45 | 13,139.75 |
| Parent | 2021 | 211 | 0.48 | 24,170.25 | 114.55 | 0.96 | 0.95 | 1.52 | 1.17 | 1.08 | 10.89 | 21,782.50 |
| Parent | 2022 | 209 | 0.40 | 42,624.75 | 203.95 | 1.14 | 1.12 | 2.23 | 1.22 | 2.03 | 10.62 | 20,553.25 |
| Reversal_delay1m | 2018 | 11 | 0.36 | 515.25 | 46.84 | 0.14 | 0.15 | 0.23 | 1.14 | 0.25 | 2.01 | 2,017.25 |
| Reversal_delay1m | 2019 | 13 | 0.62 | 5,010.75 | 385.44 | 1.57 | 1.48 | 4.37 | 3.15 | 5.38 | 0.85 | 909.00 |
| Reversal_delay1m | 2020 | 9 | 0.33 | -3,285.25 | -365.03 | -0.56 | -0.58 | -0.79 | 0.65 | -0.64 | 5.04 | 5,036.75 |
| Reversal_delay1m | 2021 | 15 | 0.53 | -623.75 | -41.58 | -0.10 | -0.10 | -0.14 | 0.94 | -0.09 | 7.00 | 7,155.75 |
| Reversal_delay1m | 2022 | 10 | 0.40 | 2,902.50 | 290.25 | 0.31 | 0.32 | 0.64 | 1.28 | 0.33 | 11.51 | 8,530.75 |
| Reversal | 2018 | 11 | 0.36 | 615.25 | 55.93 | 0.17 | 0.18 | 0.28 | 1.17 | 0.30 | 2.03 | 2,017.25 |
| Reversal | 2019 | 13 | 0.62 | 5,225.75 | 401.98 | 1.53 | 1.45 | 4.32 | 3.33 | 6.25 | 0.90 | 817.25 |
| Reversal | 2020 | 9 | 0.33 | -2,265.25 | -251.69 | -0.38 | -0.39 | -0.57 | 0.75 | -0.49 | 4.61 | 4,501.75 |
| Reversal | 2021 | 15 | 0.53 | -1,658.75 | -110.58 | -0.26 | -0.26 | -0.36 | 0.86 | -0.22 | 7.40 | 7,335.75 |
| Reversal | 2022 | 10 | 0.50 | 6,337.50 | 633.75 | 0.67 | 0.68 | 1.53 | 1.72 | 0.87 | 9.83 | 7,128.50 |
