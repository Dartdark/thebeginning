# NQ Flow Absorption: REJECT; continue the t6 program

Summary: Five frozen models failed the 2018-22 design screen. The primary absorption rule had only4 trades,
net -$454 per NQ, trade t -2.30 and daily NW5 t -1.61. The other two absorption candidates had no trades.
No2023+ or account tests were run. This rejects this mechanism, not the user's continuing research mandate.

Plan: `agents/codex/plans/flow_absorption.md`, prereg d8ac116.
Script: `analysis/codex_flow_absorption.py`. Outputs: `analysis/outputs/codex_flow_absorption/`.
Trials:3candidates+2price controls; cumulative10economic configurations in the corrected standalone program.
Independent-per-signal diagnostics below are additional non-executable return paths, not selectable strategies.
Unknown older repository/author searches remain relevant; this is not a fresh ten-trial universe.

## Rule as tested

Buy a completed5/15-minute up bar closing in its upper quartile despite aggressive net selling of at least20%
(or35% in one5-minute variant); mirror shorts. Signal closes09:00-14:00CT. OF timestamps ET minus60minutes.
All input minutes complete; OF/native close must match within0.25point. Wait one whole extra minute then
next native open (signal j+2). Stop0.10 and target0.15 prior15-weekday ATR;30minute limit, max4/day,
flat14:55; normal cash days, no July3/December24. The shared `_walk` adapter enforces signal-time flatness,
no stale signals, protected entry-bar stops, worse stop gaps and1point target-through. This is the documented
extension of grid.execute needed for the additional receipt delay and per-signal eligibility.
NQ fees$7.25RT plus1tick per market/stop fill; nativeMNQ$1.24RT plus$0.50/fill. Four-tick stress also failed.

## Design results

All results below2018-22 only. Dollar metrics per1NQ. Zero calendar cash sessions retained for daily metrics.
2023+ not accessed for returns; validation and all plan decisions remain closed.

| Model | Side / period | Trades | Net/NQ | Win | PF | Trade t | Daily NW5 t | Max DD | Sharpe | Sortino | Calmar | Ulcer |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A5_D20 | all / 2018-22 | 4 | $-454.00 | 25.0% | 0.067 | -2.302 | -1.608 | $486.75 | -0.715 | -0.720 | -0.187 | 0.855 |
| A5_D20 | all / 2018 | 3 | $-296.75 | 33.3% | 0.099 | -1.485 | -1.279 | $329.50 | -1.258 | -1.269 | -0.904 | 0.617 |
| A5_D20 | all / 2019 | 1 | $-157.25 | 0.0% | 0.000 | nan | -1.002 | $157.25 | -1.000 | -1.000 | -1.000 | 0.020 |
| A5_D20 | all / 2020 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D20 | all / 2021 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D20 | all / 2022 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D20 | long / 2018-22 | 1 | $-147.25 | 0.0% | 0.000 | nan | -1.002 | $147.25 | -0.447 | -0.447 | -0.200 | 0.293 |
| A5_D20 | long / 2018 | 1 | $-147.25 | 0.0% | 0.000 | nan | -1.012 | $147.25 | -1.002 | -1.002 | -1.004 | 0.288 |
| A5_D20 | long / 2019 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D20 | long / 2020 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D20 | long / 2021 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D20 | long / 2022 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D20 | short / 2018-22 | 3 | $-306.75 | 33.3% | 0.096 | -1.506 | -1.268 | $339.50 | -0.565 | -0.570 | -0.181 | 0.571 |
| A5_D20 | short / 2018 | 2 | $-149.50 | 50.0% | 0.180 | -0.695 | -0.814 | $182.25 | -0.808 | -0.822 | -0.824 | 0.337 |
| A5_D20 | short / 2019 | 1 | $-157.25 | 0.0% | 0.000 | nan | -1.002 | $157.25 | -1.000 | -1.000 | -1.000 | 0.020 |
| A5_D20 | short / 2020 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D20 | short / 2021 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D20 | short / 2022 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D35 | all / 2018-22 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D35 | all / 2018 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D35 | all / 2019 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D35 | all / 2020 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D35 | all / 2021 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D35 | all / 2022 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D35 | long / 2018-22 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D35 | long / 2018 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D35 | long / 2019 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D35 | long / 2020 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D35 | long / 2021 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D35 | long / 2022 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D35 | short / 2018-22 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D35 | short / 2018 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D35 | short / 2019 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D35 | short / 2020 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D35 | short / 2021 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A5_D35 | short / 2022 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A15_D20 | all / 2018-22 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A15_D20 | all / 2018 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A15_D20 | all / 2019 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A15_D20 | all / 2020 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A15_D20 | all / 2021 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A15_D20 | all / 2022 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A15_D20 | long / 2018-22 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A15_D20 | long / 2018 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A15_D20 | long / 2019 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A15_D20 | long / 2020 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A15_D20 | long / 2021 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A15_D20 | long / 2022 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A15_D20 | short / 2018-22 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A15_D20 | short / 2018 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A15_D20 | short / 2019 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A15_D20 | short / 2020 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A15_D20 | short / 2021 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| A15_D20 | short / 2022 | 0 | $0.00 | nan% | nan | nan | nan | $0.00 | nan | nan | nan | 0.000 |
| PRICE5 | all / 2018-22 | 4822 | $-40,409.50 | 44.3% | 0.961 | -1.122 | -1.089 | $60,714.50 | -0.504 | -0.733 | -0.133 | 52.239 |
| PRICE5 | all / 2018 | 976 | $-15,906.00 | 42.8% | 0.879 | -1.756 | -1.761 | $21,297.00 | -1.790 | -2.382 | -0.750 | 15.683 |
| PRICE5 | all / 2019 | 972 | $-1,787.00 | 45.7% | 0.983 | -0.235 | -0.284 | $7,009.00 | -0.254 | -0.355 | -0.255 | 5.074 |
| PRICE5 | all / 2020 | 950 | $1,557.50 | 45.7% | 1.007 | 0.094 | 0.095 | $12,055.00 | 0.087 | 0.134 | 0.129 | 8.174 |
| PRICE5 | all / 2021 | 964 | $-26,384.00 | 42.3% | 0.885 | -1.689 | -1.650 | $41,243.00 | -1.845 | -2.407 | -0.640 | 41.097 |
| PRICE5 | all / 2022 | 960 | $2,110.00 | 44.9% | 1.006 | 0.084 | 0.079 | $29,750.00 | 0.084 | 0.126 | 0.071 | 18.914 |
| PRICE5 | long / 2018-22 | 2538 | $-16,190.50 | 45.5% | 0.969 | -0.635 | -0.651 | $34,118.00 | -0.296 | -0.436 | -0.095 | 29.658 |
| PRICE5 | long / 2018 | 528 | $-15,433.00 | 42.2% | 0.784 | -2.441 | -2.410 | $17,255.00 | -2.442 | -3.020 | -0.898 | 9.594 |
| PRICE5 | long / 2019 | 496 | $3,299.00 | 48.0% | 1.064 | 0.606 | 0.712 | $4,896.00 | 0.679 | 1.085 | 0.674 | 3.984 |
| PRICE5 | long / 2020 | 514 | $3,933.50 | 49.2% | 1.035 | 0.330 | 0.392 | $6,784.75 | 0.371 | 0.562 | 0.577 | 4.833 |
| PRICE5 | long / 2021 | 518 | $-13,355.50 | 43.2% | 0.884 | -1.225 | -1.187 | $23,224.50 | -1.247 | -1.735 | -0.575 | 23.200 |
| PRICE5 | long / 2022 | 482 | $5,365.50 | 45.0% | 1.031 | 0.300 | 0.300 | $15,532.50 | 0.306 | 0.468 | 0.347 | 12.062 |
| PRICE5 | short / 2018-22 | 2284 | $-24,219.00 | 42.9% | 0.952 | -0.953 | -0.922 | $37,721.75 | -0.416 | -0.628 | -0.129 | 28.724 |
| PRICE5 | short / 2018 | 448 | $-473.00 | 43.5% | 0.992 | -0.073 | -0.072 | $10,747.50 | -0.073 | -0.112 | -0.044 | 10.755 |
| PRICE5 | short / 2019 | 476 | $-5,086.00 | 43.3% | 0.906 | -0.959 | -1.040 | $6,561.25 | -1.004 | -1.453 | -0.775 | 6.434 |
| PRICE5 | short / 2020 | 436 | $-2,376.00 | 41.5% | 0.977 | -0.205 | -0.215 | $8,898.25 | -0.189 | -0.297 | -0.266 | 7.691 |
| PRICE5 | short / 2021 | 446 | $-13,028.50 | 41.3% | 0.885 | -1.163 | -1.143 | $21,602.00 | -1.229 | -1.725 | -0.603 | 21.008 |
| PRICE5 | short / 2022 | 478 | $-3,255.50 | 44.8% | 0.982 | -0.183 | -0.169 | $25,569.50 | -0.176 | -0.269 | -0.128 | 16.827 |
| PRICE15 | all / 2018-22 | 4814 | $-34,911.50 | 45.2% | 0.963 | -1.029 | -1.158 | $56,496.75 | -0.492 | -0.716 | -0.124 | 48.911 |
| PRICE15 | all / 2018 | 975 | $-723.75 | 45.1% | 0.994 | -0.081 | -0.092 | $7,973.75 | -0.090 | -0.130 | -0.091 | 7.572 |
| PRICE15 | all / 2019 | 971 | $-13,544.75 | 44.0% | 0.865 | -1.933 | -2.290 | $14,519.75 | -2.189 | -2.839 | -0.933 | 16.201 |
| PRICE15 | all / 2020 | 945 | $-5,831.25 | 46.1% | 0.972 | -0.367 | -0.425 | $18,672.00 | -0.376 | -0.538 | -0.311 | 16.637 |
| PRICE15 | all / 2021 | 963 | $-28,161.75 | 43.3% | 0.867 | -1.927 | -2.077 | $34,488.75 | -2.042 | -2.698 | -0.817 | 36.357 |
| PRICE15 | all / 2022 | 960 | $13,350.00 | 47.5% | 1.042 | 0.566 | 0.653 | $15,151.00 | 0.614 | 0.955 | 0.885 | 9.436 |
| PRICE15 | long / 2018-22 | 2648 | $-31,158.00 | 46.2% | 0.937 | -1.305 | -1.517 | $36,650.75 | -0.619 | -0.867 | -0.170 | 37.394 |
| PRICE15 | long / 2018 | 523 | $-6,476.75 | 44.9% | 0.897 | -1.051 | -1.329 | $9,628.00 | -1.105 | -1.539 | -0.675 | 10.944 |
| PRICE15 | long / 2019 | 533 | $-6,959.25 | 45.6% | 0.868 | -1.390 | -1.493 | $8,298.75 | -1.515 | -2.058 | -0.839 | 7.892 |
| PRICE15 | long / 2020 | 550 | $-5,067.50 | 49.1% | 0.954 | -0.454 | -0.493 | $15,129.00 | -0.450 | -0.628 | -0.334 | 11.003 |
| PRICE15 | long / 2021 | 545 | $-9,331.25 | 45.5% | 0.914 | -0.892 | -0.986 | $15,727.25 | -0.995 | -1.440 | -0.593 | 15.103 |
| PRICE15 | long / 2022 | 497 | $-3,323.25 | 45.7% | 0.980 | -0.201 | -0.246 | $12,133.25 | -0.215 | -0.301 | -0.275 | 11.482 |
| PRICE15 | short / 2018-22 | 2166 | $-3,753.50 | 44.0% | 0.992 | -0.156 | -0.163 | $29,938.00 | -0.071 | -0.111 | -0.025 | 20.361 |
| PRICE15 | short / 2018 | 452 | $5,753.00 | 45.4% | 1.099 | 0.880 | 0.835 | $3,914.50 | 0.948 | 1.567 | 1.476 | 3.135 |
| PRICE15 | short / 2019 | 438 | $-6,585.50 | 42.0% | 0.862 | -1.342 | -1.518 | $7,707.00 | -1.490 | -2.090 | -0.854 | 10.016 |
| PRICE15 | short / 2020 | 395 | $-763.75 | 42.0% | 0.992 | -0.068 | -0.078 | $14,714.75 | -0.070 | -0.111 | -0.052 | 14.449 |
| PRICE15 | short / 2021 | 418 | $-18,830.50 | 40.4% | 0.818 | -1.845 | -1.917 | $22,547.75 | -1.918 | -2.608 | -0.835 | 24.512 |
| PRICE15 | short / 2022 | 463 | $16,673.25 | 49.5% | 1.109 | 0.991 | 1.043 | $14,634.75 | 0.982 | 1.611 | 1.144 | 9.322 |

## Data and controls

515,156 selected OF rows; no exact or conflicting duplicates.497,780 valid source/native close matches;
16,958 finite source/native mismatches excluded. No forward fill. Historical receive timestamps unverified.
All4primary executions had observed held minutes. Signals/execution suppressions are in design_counts.json.

Actual capped price controls: PRICE5 4,822trades, net-$40,409.50; PRICE15 4,814, net-$34,911.50.
Caps make actual base ledgers non-nested. Separate independent-per-signal diagnostics deliberately allow
overlapping events and cannot be executed as a portfolio:5min base38,884tickets, net-$733,674;
primary keeps4net-$454, removes38,880net-$733,220 (avg-$18.86,t-7.92).
Of1,000matched-size random subsets,64.1% made at least the primary's net. Only35.9% were jointly worse
on profit and DD. Thus the primary fails even this weak filter check; empty candidates are uninformative.
15min independent base13,448events, net-$226,498; neither15min candidate event qualified.
See design_filter_diagnostics.json. Do not present these overlapping diagnostics as executable returns.

## Limits and next action

Engineering retries fixed empty-ledger dtypes/CSV representation only; thresholds and execution were unchanged.
No random-entry/bootstraps/MC/account bench/PowerLanguage or promotion on a failed cheap gate.
The presumed absorption mechanism is rare under the frozen raw-data agreement gate. Do not silently relax it.
Continue with a distinct, separately committed evidence sheet and preregistration. Claude review handoff:
`agents/codex/results/flow_absorption.md`. No shared ranks/plans/live files changed.
