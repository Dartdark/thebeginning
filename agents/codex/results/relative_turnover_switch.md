# NQ Relative Turnover Switch: REJECT; continue distinct research

Summary: None of the three candidates passed2018-22 design. Primary5min:192trades,
net$-2,047.00/NQ,trade t-0.365,dailyNW5 t-0.371. Other candidates had25/20trades.
The switch fails uniform and own-volume/time-stratified random-drop checks. No2023+returns tested.
Program50counted evaluations/49unique rules retained; no t4.5/t5/t6 event. Continue a DISTINCT mechanism.

Plan: agents/codex/plans/relative_turnover_switch.md, prereg9d82548.
Scripts: analysis/codex_relative_turnover_switch.py and analysis/codex_relative_turnover_switch_report.py.
Outputs: analysis/outputs/codex_relative_turnover_switch/.
Five models:3candidates+2unselectable own-volume/price controls. Prior45evaluations/44unique; plus unknown
larger repository/author searches. Overlapping windows and random subsets are additional NON-SELECTABLE
return diagnostics, not capitalized portfolios or fresh independent trials. All controls remain unselectable.

## Trade as tested

At5/15min closes09:00--14:00CT, R=Vnq*20*Cnq/(Ves*50*Ces). Normalize each clock bar by the median R on
exact prior20normal research dates,min15valid joint observations,excluding today. Previous bar must have
its own normalized ratio<=1; current>=1.5(primary5min/15min)or2(one5minvariant). OwnNQrelativevolume>=1,
ES>=0.5, same-clock prior medians. Current NQ body>=50%range and close in top25%(long)orbottom25%(short).

OnlyNQtraded; ES quantity is a reference. No price residual, old strategy ticket, VXNforecast or OPPpathfilter.
Entryj+2nativeopen(oneextra minute),stop0.10prior15weekdayATR,target0.20,ceilto0.25,activeentrybar;
exitmin(j+45,14:55),max4/day,oneposition,no stale/sameclose signals/BE/trail/overnight/resizing.
NQ$7.25RT+1tick($5)/market-stopfill; nativeMNQ$1.24RT+$0.50/fill independently. Target1pointthrough,
worse-open stop gaps and fixed4tickfill stress. Calendar-normal dates,noJuly3/Dec24,standardquarterlyrollguard.
Complete bothmarkets/current+previous bars; no current-day future-completeness mask or forwardfill.

Controls retain current-candle price/own-volume conditions and all data/history eligibility but omit both
peer-switch tests. A shift in relative turnover is a quantity proxy, not net buying or observed institutional
rotation. The proposed continuation mechanism was unproven and fails this screen.

## Design results

2018-22 only; dollars/NQ except net_mnq rows in nativeMNQ. Standard shared metrics, cashdayzeros,initialzeroDD,
all/long/short/year,NW5/NW20,cost/native/stress. Signal features and execution counts preserved.

| model | period | side | trades | win | avg | total | t_trade | t_nw5 | t_nw20 | sharpe | sortino | profit_factor | calmar | ulcer | max_dd | cost | missing_held_minutes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CTS5_15 | 2018-22 | all | 192 | 0.42708 | -10.661 | -2047 | -0.36455 | -0.37054 | -0.38617 | -0.16658 | -0.26011 | 0.93609 | -0.057757 | 7.3057 | 7094 | 3207 | 0 |
| CTS5_15 | 2018 | all | 52 | 0.32692 | -80.038 | -4162 | -2.418 | -2.5929 | -2.6148 | -2.2527 | -2.67 | 0.47208 | -0.97779 | 4.1752 | 4273.5 | 877 | 0 |
| CTS5_15 | 2019 | all | 41 | 0.46341 | -16.03 | -657.25 | -0.47401 | -0.48775 | -0.51397 | -0.46489 | -0.67021 | 0.83401 | -0.33308 | 2.386 | 1973.2 | 687.25 | 0 |
| CTS5_15 | 2020 | all | 46 | 0.52174 | 73.946 | 3401.5 | 0.92119 | 0.94381 | 1.1199 | 0.92791 | 1.7002 | 1.3807 | 1.3703 | 1.3881 | 2472.5 | 768.5 | 0 |
| CTS5_15 | 2021 | all | 42 | 0.45238 | 77.512 | 3255.5 | 1.0697 | 1.171 | 1.288 | 1.1535 | 2.3585 | 1.5007 | 1.9263 | 1.1955 | 1690 | 684.5 | 0 |
| CTS5_15 | 2022 | all | 11 | 0.27273 | -353.16 | -3884.8 | -2.6156 | -2.036 | -2.2833 | -2.1329 | -2.2095 | 0.18181 | -0.9065 | 5.3076 | 4302.5 | 189.75 | 0 |
| CTS5_15 | 2018-22 | long | 120 | 0.475 | 19.792 | 2375 | 0.63356 | 0.65886 | 0.68077 | 0.29692 | 0.48336 | 1.1554 | 0.19746 | 2.5238 | 2407.5 | 2030 | 0 |
| CTS5_15 | 2018 | long | 32 | 0.375 | -37.875 | -1212 | -0.85689 | -0.91405 | -0.94474 | -0.86042 | -1.141 | 0.70618 | -1.004 | 1.147 | 1212 | 542 | 0 |
| CTS5_15 | 2019 | long | 27 | 0.48148 | -4.4722 | -120.75 | -0.11701 | -0.12816 | -0.14454 | -0.11893 | -0.17847 | 0.94601 | -0.14231 | 0.64327 | 848.5 | 455.75 | 0 |
| CTS5_15 | 2020 | long | 30 | 0.63333 | 134.42 | 4032.5 | 1.5677 | 1.5532 | 1.7043 | 1.5266 | 3.0054 | 1.9776 | 2.9021 | 0.80855 | 1384 | 507.5 | 0 |
| CTS5_15 | 2021 | long | 29 | 0.41379 | -10.526 | -305.25 | -0.15134 | -0.17338 | -0.18584 | -0.18566 | -0.25869 | 0.93311 | -0.14883 | 2.3372 | 2051 | 490.25 | 0 |
| CTS5_15 | 2022 | long | 2 | 0.5 | -9.75 | -19.5 | -0.042857 | -0.060556 | -0.060563 | -0.060554 | -0.082355 | 0.91781 | -0.082519 | 0.34261 | 237.25 | 34.5 | 0 |
| CTS5_15 | 2018-22 | short | 72 | 0.34722 | -61.417 | -4422 | -1.0609 | -1.0493 | -1.1052 | -0.46806 | -0.71508 | 0.73585 | -0.15959 | 6.712 | 5546.2 | 1177 | 0 |
| CTS5_15 | 2018 | short | 20 | 0.25 | -147.5 | -2950 | -3.1757 | -2.7327 | -3.2608 | -2.6132 | -2.8374 | 0.21516 | -0.91476 | 3.4332 | 3237.8 | 335 | 0 |
| CTS5_15 | 2019 | short | 14 | 0.42857 | -38.321 | -536.5 | -0.56419 | -0.54474 | -0.52321 | -0.57768 | -0.75576 | 0.68862 | -0.34118 | 2.0911 | 1572.5 | 231.5 | 0 |
| CTS5_15 | 2020 | short | 16 | 0.3125 | -39.438 | -631 | -0.23733 | -0.25115 | -0.34064 | -0.23657 | -0.4089 | 0.86881 | -0.31723 | 1.7545 | 1981.2 | 261 | 0 |
| CTS5_15 | 2021 | short | 13 | 0.53846 | 273.9 | 3560.8 | 1.6331 | 1.6603 | 1.7026 | 1.5417 | 4.4302 | 2.8369 | 5.0187 | 0.46094 | 709.5 | 194.25 | 0 |
| CTS5_15 | 2022 | short | 9 | 0.22222 | -429.47 | -3865.2 | -2.8688 | -2.0826 | -2.3459 | -2.156 | -2.2186 | 0.1431 | -0.90606 | 5.4044 | 4283 | 155.25 | 0 |
| CTS5_15 | 2018-22 | net_mnq | 192 | 0.42188 | -1.5811 | -303.58 | -0.54065 | -0.55043 | -0.57436 | -0.24711 | -0.3808 | 0.90687 | -0.079643 | 0.7957 | 762.96 | 419.58 | 0 |
| CTS5_15 | 2018-22 | stress_four_ticks | 192 | 0.41146 | -39.021 | -7492 | -1.3249 | -1.3556 | -1.4202 | -0.60525 | -0.88412 | 0.78836 | -0.14756 | 11.564 | 10162 | 8652 | 0 |
| CTS5_20 | 2018-22 | all | 25 | 0.56 | 93.75 | 2343.8 | 0.95787 | 0.85932 | 0.75706 | 0.42902 | 0.85492 | 1.6276 | 0.21266 | 1.1901 | 2206 | 411.25 | 0 |
| CTS5_20 | 2018 | all | 9 | 0.33333 | -65.028 | -585.25 | -0.76026 | -0.90925 | -1.04 | -0.77549 | -1.0487 | 0.54929 | -0.54343 | 1.2183 | 1081.2 | 145.25 | 0 |
| CTS5_20 | 2019 | all | 3 | 1 | 101.08 | 303.25 | 4.2994 | 1.7015 | 1.8773 | 1.6509 | nan | inf | nan | 0 | 0 | 51.75 | 0 |
| CTS5_20 | 2020 | all | 11 | 0.54545 | 162.75 | 1790.2 | 0.79395 | 0.70343 | 0.61158 | 0.80548 | 1.6367 | 1.7348 | 0.92681 | 1.7617 | 1924 | 184.75 | 0 |
| CTS5_20 | 2021 | all | 2 | 1 | 417.75 | 835.5 | 1.8163 | 1.2623 | 1.3248 | 1.2402 | nan | inf | nan | 0 | 0 | 29.5 | 0 |
| CTS5_20 | 2022 | all | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| CTS5_20 | 2018-22 | long | 16 | 0.75 | 182.44 | 2919 | 2.1367 | 2.0147 | 1.8923 | 0.86426 | 2.2354 | 3.7564 | 1.2372 | 0.19807 | 472.25 | 261 | 0 |
| CTS5_20 | 2018 | long | 6 | 0.5 | 21.083 | 126.5 | 0.19043 | 0.26507 | 0.3089 | 0.20618 | 0.36856 | 1.2156 | 0.34372 | 0.24821 | 369.5 | 93.5 | 0 |
| CTS5_20 | 2019 | long | 3 | 1 | 101.08 | 303.25 | 4.2994 | 1.7015 | 1.8773 | 1.6509 | nan | inf | nan | 0 | 0 | 51.75 | 0 |
| CTS5_20 | 2020 | long | 5 | 0.8 | 330.75 | 1653.8 | 1.5804 | 1.4194 | 1.2947 | 1.3862 | 3.4949 | 4.5019 | 3.488 | 0.36936 | 472.25 | 86.25 | 0 |
| CTS5_20 | 2021 | long | 2 | 1 | 417.75 | 835.5 | 1.8163 | 1.2623 | 1.3248 | 1.2402 | nan | inf | nan | 0 | 0 | 29.5 | 0 |
| CTS5_20 | 2022 | long | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| CTS5_20 | 2018-22 | short | 9 | 0.22222 | -63.917 | -575.25 | -0.28394 | -0.26533 | -0.24237 | -0.13402 | -0.23864 | 0.78501 | -0.043031 | 1.7068 | 2675.8 | 150.25 | 0 |
| CTS5_20 | 2018 | short | 3 | 0 | -237.25 | -711.75 | -3.6357 | -1.6674 | -1.8325 | -1.6227 | -1.6174 | 0 | -1.004 | 1.146 | 711.75 | 51.75 | 0 |
| CTS5_20 | 2019 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| CTS5_20 | 2020 | short | 6 | 0.33333 | 22.75 | 136.5 | 0.066723 | 0.064297 | 0.05851 | 0.072771 | 0.13842 | 1.0695 | 0.069226 | 1.8429 | 1964 | 98.5 | 0 |
| CTS5_20 | 2021 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| CTS5_20 | 2022 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| CTS5_20 | 2018-22 | net_mnq | 25 | 0.56 | 8.86 | 221.5 | 0.90525 | 0.81501 | 0.71794 | 0.40638 | 0.79774 | 1.5842 | 0.19374 | 0.12638 | 228.84 | 54 | 0 |
| CTS5_20 | 2018-22 | stress_four_ticks | 25 | 0.52 | 66.15 | 1653.8 | 0.67159 | 0.61434 | 0.54129 | 0.30418 | 0.56116 | 1.4046 | 0.12463 | 1.5997 | 2656 | 1101.2 | 0 |
| CTS15_15 | 2018-22 | all | 20 | 0.6 | 72 | 1440 | 0.83063 | 0.82058 | 1.0273 | 0.37449 | 0.64021 | 1.5674 | 0.33642 | 0.47756 | 856.75 | 335 | 0 |
| CTS15_15 | 2018 | all | 7 | 0.57143 | 137.75 | 964.25 | 0.99741 | 1.01 | 1.1237 | 0.99975 | 3.0554 | 2.7636 | 4.9079 | 0.16917 | 197.25 | 110.75 | 0 |
| CTS15_15 | 2019 | all | 3 | 0.66667 | -52.25 | -156.75 | -0.67129 | -0.74783 | -0.76208 | -0.74207 | -0.75633 | 0.24367 | -0.75633 | 0.34456 | 207.25 | 51.75 | 0 |
| CTS15_15 | 2020 | all | 5 | 0.6 | -11.25 | -56.25 | -0.049321 | -0.059711 | -0.066064 | -0.054908 | -0.069887 | 0.94953 | -0.065396 | 0.70262 | 856.75 | 86.25 | 0 |
| CTS15_15 | 2021 | all | 5 | 0.6 | 137.75 | 688.75 | 0.67044 | 0.62559 | 1.1275 | 0.71 | 1.4539 | 2.0288 | 1.0288 | 0.19104 | 669.5 | 86.25 | 0 |
| CTS15_15 | 2022 | all | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| CTS15_15 | 2018-22 | long | 9 | 0.66667 | 58.861 | 529.75 | 0.58886 | 0.54764 | 0.75802 | 0.2735 | 0.47017 | 1.6293 | 0.15838 | 0.52396 | 669.5 | 155.25 | 0 |
| CTS15_15 | 2018 | long | 2 | 0.5 | 82.75 | 165.5 | 0.32451 | 0.43752 | 0.44014 | 0.43668 | 0.96272 | 1.9608 | 0.96464 | 0.22909 | 172.25 | 34.5 | 0 |
| CTS15_15 | 2019 | long | 2 | 1 | 25.25 | 50.5 | 2.02 | 1.2904 | 1.3445 | 1.2689 | nan | inf | nan | 0 | 0 | 34.5 | 0 |
| CTS15_15 | 2020 | long | 1 | 1 | 257.75 | 257.75 | nan | 1.0122 | 1.0456 | 0.99802 | nan | inf | nan | 0 | 0 | 17.25 | 0 |
| CTS15_15 | 2021 | long | 4 | 0.5 | 14 | 56 | 0.066118 | 0.065758 | 0.10563 | 0.07614 | 0.11821 | 1.0836 | 0.083645 | 0.7029 | 669.5 | 69 | 0 |
| CTS15_15 | 2022 | long | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| CTS15_15 | 2018-22 | short | 11 | 0.54545 | 82.75 | 910.25 | 0.59426 | 0.61309 | 0.64606 | 0.27398 | 0.46759 | 1.5366 | 0.16348 | 0.69908 | 1114.5 | 179.75 | 0 |
| CTS15_15 | 2018 | short | 5 | 0.6 | 159.75 | 798.75 | 0.87768 | 0.90743 | 0.93793 | 0.9 | 3.018 | 3.1328 | 2.8463 | 0.20223 | 281.75 | 76.25 | 0 |
| CTS15_15 | 2019 | short | 1 | 0 | -207.25 | -207.25 | nan | -1.0122 | -1.0458 | -1 | -1 | 0 | -1 | 0.35802 | 207.25 | 17.25 | 0 |
| CTS15_15 | 2020 | short | 4 | 0.5 | -78.5 | -314 | -0.27898 | -0.31842 | -0.35851 | -0.31684 | -0.39013 | 0.71826 | -0.28063 | 0.97773 | 1114.5 | 69 | 0 |
| CTS15_15 | 2021 | short | 1 | 1 | 632.75 | 632.75 | nan | 1.0122 | 1.0458 | 1 | nan | inf | nan | 0 | 0 | 17.25 | 0 |
| CTS15_15 | 2022 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| CTS15_15 | 2018-22 | net_mnq | 20 | 0.6 | 6.685 | 133.7 | 0.77122 | 0.76337 | 0.95947 | 0.34853 | 0.58683 | 1.5184 | 0.30682 | 0.050562 | 87.22 | 43.8 | 0 |
| CTS15_15 | 2018-22 | stress_four_ticks | 20 | 0.55 | 43.5 | 870 | 0.49935 | 0.49755 | 0.63455 | 0.22765 | 0.35947 | 1.3112 | 0.18393 | 0.59481 | 946.75 | 905 | 0 |
| OWN5 | 2018-22 | all | 4122 | 0.39277 | -18.759 | -77324 | -2.0487 | -2.1141 | -2.1745 | -0.95369 | -1.3436 | 0.92321 | -0.17838 | 81.867 | 86767 | 67230 | 4 |
| OWN5 | 2018 | all | 784 | 0.375 | -15.522 | -12169 | -1.2671 | -1.3875 | -1.2755 | -1.3024 | -1.8235 | 0.89996 | -0.58646 | 21.428 | 20832 | 12704 | 4 |
| OWN5 | 2019 | all | 797 | 0.42158 | -4.9413 | -3938.2 | -0.5121 | -0.49033 | -0.48696 | -0.51713 | -0.77566 | 0.95799 | -0.40738 | 11.372 | 9667.2 | 13023 | 0 |
| OWN5 | 2020 | all | 808 | 0.41089 | -6.7983 | -5493 | -0.3259 | -0.39446 | -0.39199 | -0.35239 | -0.51214 | 0.97333 | -0.45352 | 11.003 | 12064 | 13203 | 0 |
| OWN5 | 2021 | all | 849 | 0.35689 | -54.311 | -46110 | -2.9304 | -2.7454 | -2.4992 | -3.0283 | -3.8942 | 0.79533 | -0.81724 | 59.148 | 56422 | 13850 | 0 |
| OWN5 | 2022 | all | 884 | 0.40045 | -10.876 | -9614 | -0.35309 | -0.36536 | -0.46005 | -0.36523 | -0.52421 | 0.97332 | -0.42733 | 24.394 | 22588 | 14449 | 0 |
| OWN5 | 2018-22 | long | 2108 | 0.41176 | -24.923 | -52538 | -2.0365 | -1.9679 | -2.0069 | -0.94164 | -1.3575 | 0.89394 | -0.19043 | 42.793 | 55222 | 34798 | 4 |
| OWN5 | 2018 | long | 402 | 0.37313 | -33.407 | -13430 | -2.0697 | -2.371 | -2.2473 | -2.0673 | -2.6257 | 0.7857 | -0.83863 | 15.013 | 16078 | 6604.5 | 4 |
| OWN5 | 2019 | long | 416 | 0.46635 | 0.86298 | 359 | 0.067977 | 0.07265 | 0.07002 | 0.075273 | 0.11653 | 1.008 | 0.06552 | 6.2795 | 5479.2 | 6881 | 0 |
| OWN5 | 2020 | long | 414 | 0.45894 | 9.779 | 4048.5 | 0.35862 | 0.3637 | 0.3678 | 0.38984 | 0.59257 | 1.043 | 0.42637 | 7.7711 | 9457.8 | 6881.5 | 0 |
| OWN5 | 2021 | long | 433 | 0.37644 | -39.409 | -17064 | -1.5507 | -1.5229 | -1.4549 | -1.5139 | -2.2467 | 0.84127 | -0.55694 | 27.472 | 30640 | 7124.2 | 0 |
| OWN5 | 2022 | long | 443 | 0.386 | -59.71 | -26452 | -1.4204 | -1.3391 | -1.5355 | -1.4748 | -2.0964 | 0.85794 | -0.89713 | 31.376 | 29602 | 7306.8 | 0 |
| OWN5 | 2018-22 | short | 2014 | 0.37289 | -12.307 | -24786 | -0.89962 | -0.95922 | -0.8956 | -0.40976 | -0.64659 | 0.95155 | -0.094857 | 46.827 | 52302 | 32432 | 0 |
| OWN5 | 2018 | short | 382 | 0.37696 | 3.2997 | 1260.5 | 0.17829 | 0.16128 | 0.1543 | 0.17736 | 0.29196 | 1.0214 | 0.10701 | 12.219 | 11826 | 6099.5 | 0 |
| OWN5 | 2019 | short | 381 | 0.3727 | -11.279 | -4297.2 | -0.76815 | -0.77004 | -0.69745 | -0.74292 | -1.1435 | 0.91214 | -0.51769 | 10.267 | 8300.8 | 6142.2 | 0 |
| OWN5 | 2020 | short | 394 | 0.36041 | -24.217 | -9541.5 | -0.76206 | -0.838 | -0.83276 | -0.74322 | -1.2118 | 0.91463 | -0.72004 | 11.89 | 13199 | 6321.5 | 0 |
| OWN5 | 2021 | short | 416 | 0.33654 | -69.822 | -29046 | -2.5815 | -2.0763 | -1.8326 | -2.4494 | -3.4322 | 0.7534 | -0.82696 | 43.547 | 35124 | 6726 | 0 |
| OWN5 | 2022 | short | 441 | 0.41497 | 38.181 | 16838 | 0.84906 | 1.1155 | 1.1807 | 0.91319 | 1.4917 | 1.0967 | 1.3723 | 7.9022 | 12319 | 7142.2 | 0 |
| OWN5 | 2018-22 | net_mnq | 4122 | 0.39083 | -2.3909 | -9855.3 | -2.6112 | -2.693 | -2.767 | -1.2154 | -1.6884 | 0.90337 | -0.1864 | 10.894 | 10583 | 8845.8 | 4 |
| OWN5 | 2018-22 | stress_four_ticks | 4122 | 0.37724 | -45.939 | -1.8936e+05 | -4.9822 | -5.1218 | -5.2427 | -2.3164 | -3.0383 | 0.82516 | -0.197 | 207.03 | 1.9239e+05 | 1.7926e+05 | 4 |
| OWN15 | 2018-22 | all | 2964 | 0.41127 | 1.9976 | 5921 | 0.1845 | 0.1959 | 0.19155 | 0.083266 | 0.12214 | 1.0085 | 0.046691 | 19.705 | 25382 | 48139 | 2 |
| OWN15 | 2018 | all | 573 | 0.41187 | 8.2387 | 4720.8 | 0.55464 | 0.60408 | 0.78176 | 0.58851 | 0.88873 | 1.055 | 0.88227 | 3.4914 | 5372 | 9224.2 | 0 |
| OWN15 | 2019 | all | 530 | 0.39434 | -20.599 | -10918 | -1.7399 | -1.8393 | -1.5936 | -1.9898 | -2.562 | 0.84007 | -0.88376 | 14.028 | 12354 | 8647.5 | 0 |
| OWN15 | 2020 | all | 586 | 0.43174 | 16.615 | 9736.5 | 0.68615 | 0.66379 | 0.57704 | 0.65764 | 0.99043 | 1.0684 | 0.62126 | 16.856 | 15610 | 9513.5 | 0 |
| OWN15 | 2021 | all | 618 | 0.38835 | -20.964 | -12956 | -0.94562 | -0.9911 | -1.1382 | -1.0054 | -1.3329 | 0.91695 | -0.57446 | 24.304 | 22552 | 10030 | 0 |
| OWN15 | 2022 | all | 657 | 0.4277 | 23.344 | 15337 | 0.66662 | 0.75159 | 0.75713 | 0.66517 | 1.0064 | 1.062 | 0.77122 | 12.798 | 19966 | 10723 | 2 |
| OWN15 | 2018-22 | long | 1507 | 0.42535 | -23.328 | -35156 | -1.6399 | -1.7346 | -1.7603 | -0.71285 | -1.0187 | 0.89913 | -0.17283 | 31.07 | 40716 | 24841 | 2 |
| OWN15 | 2018 | long | 287 | 0.4216 | -3.9399 | -1130.8 | -0.20071 | -0.21587 | -0.21342 | -0.20348 | -0.31121 | 0.97283 | -0.22274 | 5.6128 | 5096.8 | 4715.8 | 0 |
| OWN15 | 2019 | long | 285 | 0.45614 | 4.0132 | 1143.8 | 0.25366 | 0.30073 | 0.2973 | 0.28722 | 0.42196 | 1.0359 | 0.26698 | 3.9422 | 4284 | 4666.2 | 0 |
| OWN15 | 2020 | long | 305 | 0.45246 | -13.299 | -4056.2 | -0.44204 | -0.42528 | -0.39854 | -0.40758 | -0.58286 | 0.94268 | -0.22724 | 17.89 | 17780 | 5046.2 | 0 |
| OWN15 | 2021 | long | 314 | 0.40764 | -42.537 | -13356 | -1.4597 | -1.3794 | -1.6748 | -1.3328 | -1.828 | 0.8258 | -0.66761 | 21.931 | 20006 | 5201.5 | 0 |
| OWN15 | 2022 | long | 316 | 0.39241 | -56.19 | -17756 | -1.1463 | -1.3252 | -1.3838 | -1.1452 | -1.6509 | 0.86088 | -0.90383 | 23.745 | 19724 | 5211 | 2 |
| OWN15 | 2018-22 | short | 1457 | 0.39671 | 28.193 | 41077 | 1.7224 | 1.7169 | 1.595 | 0.77462 | 1.3793 | 1.117 | 0.4643 | 12.544 | 17708 | 23298 | 0 |
| OWN15 | 2018 | short | 286 | 0.4021 | 20.46 | 5851.5 | 0.91669 | 0.87901 | 1.0615 | 0.89968 | 1.617 | 1.1326 | 1.263 | 4.2766 | 4651.5 | 4508.5 | 0 |
| OWN15 | 2019 | short | 245 | 0.32245 | -49.23 | -12061 | -2.786 | -2.9766 | -2.7379 | -2.9938 | -3.7682 | 0.66891 | -1 | 15.846 | 12061 | 3981.2 | 0 |
| OWN15 | 2020 | short | 281 | 0.40925 | 49.085 | 13793 | 1.2755 | 1.2454 | 1.0593 | 1.2382 | 2.2537 | 1.1926 | 1.8494 | 5.7139 | 7428.5 | 4467.2 | 0 |
| OWN15 | 2021 | short | 304 | 0.36842 | 1.3191 | 401 | 0.039323 | 0.038639 | 0.040554 | 0.04299 | 0.066029 | 1.0051 | 0.035105 | 10.767 | 11423 | 4829 | 0 |
| OWN15 | 2022 | short | 341 | 0.46041 | 97.046 | 33093 | 1.9557 | 2.0728 | 1.9899 | 1.9444 | 3.7087 | 1.2764 | 3.5723 | 4.6334 | 9300.5 | 5512.2 | 0 |
| OWN15 | 2018-22 | net_mnq | 2964 | 0.40789 | -0.31524 | -934.36 | -0.29115 | -0.30938 | -0.30248 | -0.13139 | -0.1903 | 0.98682 | -0.062016 | 2.8213 | 3015.7 | 6340.4 | 2 |
| OWN15 | 2018-22 | stress_four_ticks | 2964 | 0.39575 | -24.976 | -74029 | -2.2902 | -2.4355 | -2.3798 | -1.0324 | -1.4205 | 0.90166 | -0.18682 | 92.811 | 79317 | 1.2809e+05 | 2 |

## Actual capped controls

Actual capped ledgers are not nested; these totals/DD compare whole strategies. No fabricated actual removed
trade list is inferred by joining different execution paths.

```json
{
  "CTS5_15": {
    "candidate_net": -2047.0,
    "base_net": -77324.5,
    "nested_actual_ledgers": false,
    "candidate_dd": 7094.0,
    "base_dd": 86767.25
  },
  "CTS5_20": {
    "candidate_net": 2343.75,
    "base_net": -77324.5,
    "nested_actual_ledgers": false,
    "candidate_dd": 2206.0,
    "base_dd": 86767.25
  },
  "CTS15_15": {
    "candidate_net": 1440.0,
    "base_net": 5921.0,
    "nested_actual_ledgers": false,
    "candidate_dd": 856.75,
    "base_dd": 25382.5
  }
}
```

## Independent-window diagnostics: uniform dropping

All qualified windows retain original brackets/timeexits/costs but overlap. These are explicitly NON-EXECUTABLE
sums and DD. Base/kept/removed totals, removedmean/t, and1000matched-size random subsets follow:

```json
{
  "CTS5_15": {
    "non_executable_signal_only": true,
    "base_trades": 14182,
    "kept_trades": 201,
    "removed_trades": 13981,
    "base_net": -279994.5,
    "kept_net": -1902.25,
    "removed_net": -278092.25,
    "removed_avg": -19.890726700522137,
    "removed_t": -4.090161935205764,
    "random_subsets": 1000,
    "random_net_mean": -3842.23,
    "p_random_net_ge_kept": 0.396,
    "p_kept_better_net_and_dd": 0.588
  },
  "CTS5_20": {
    "non_executable_signal_only": true,
    "base_trades": 14182,
    "kept_trades": 25,
    "removed_trades": 14157,
    "base_net": -279994.5,
    "kept_net": 2343.75,
    "removed_net": -282338.25,
    "removed_avg": -19.943367238821786,
    "removed_t": -4.14081275467387,
    "random_subsets": 1000,
    "random_net_mean": -586.825,
    "p_random_net_ge_kept": 0.139,
    "p_kept_better_net_and_dd": 0.686
  },
  "CTS15_15": {
    "non_executable_signal_only": true,
    "base_trades": 4696,
    "kept_trades": 20,
    "removed_trades": 4676,
    "base_net": -61896.0,
    "kept_net": 1440.0,
    "removed_net": -63336.0,
    "removed_avg": -13.544910179640718,
    "removed_t": -1.6090625623551322,
    "random_subsets": 1000,
    "random_net_mean": -337.885,
    "p_random_net_ge_kept": 0.254,
    "p_kept_better_net_and_dd": 0.745
  }
}
```

## Own-volume and time-matched dropping

1000random subsets keep the candidate's count in each signalhour x NQrelativevolume bin([1,1.5),[1.5,2),[2,inf)).
This controls some own-volume/time concentration; it neither proves causality nor makes overlapping windows
an executable portfolio. Full1000totals/DD arrays are in design_stratified_drops.json. No placebo/cell selected.

```json
{
  "CTS5_15": {
    "non_executable_signal_only": true,
    "runs": 1000,
    "kept_windows": 201,
    "informative": true,
    "strata": [
      {
        "signal_hour": 9,
        "own_volume_bin": 0,
        "base": 1949,
        "kept": 22
      },
      {
        "signal_hour": 9,
        "own_volume_bin": 1,
        "base": 645,
        "kept": 9
      },
      {
        "signal_hour": 9,
        "own_volume_bin": 2,
        "base": 275,
        "kept": 3
      },
      {
        "signal_hour": 10,
        "own_volume_bin": 0,
        "base": 1774,
        "kept": 13
      },
      {
        "signal_hour": 10,
        "own_volume_bin": 1,
        "base": 666,
        "kept": 10
      },
      {
        "signal_hour": 10,
        "own_volume_bin": 2,
        "base": 429,
        "kept": 5
      },
      {
        "signal_hour": 11,
        "own_volume_bin": 0,
        "base": 1533,
        "kept": 22
      },
      {
        "signal_hour": 11,
        "own_volume_bin": 1,
        "base": 656,
        "kept": 12
      },
      {
        "signal_hour": 11,
        "own_volume_bin": 2,
        "base": 590,
        "kept": 9
      },
      {
        "signal_hour": 12,
        "own_volume_bin": 0,
        "base": 1418,
        "kept": 28
      },
      {
        "signal_hour": 12,
        "own_volume_bin": 1,
        "base": 639,
        "kept": 8
      },
      {
        "signal_hour": 12,
        "own_volume_bin": 2,
        "base": 647,
        "kept": 8
      },
      {
        "signal_hour": 13,
        "own_volume_bin": 0,
        "base": 1423,
        "kept": 25
      },
      {
        "signal_hour": 13,
        "own_volume_bin": 1,
        "base": 611,
        "kept": 10
      },
      {
        "signal_hour": 13,
        "own_volume_bin": 2,
        "base": 700,
        "kept": 15
      },
      {
        "signal_hour": 14,
        "own_volume_bin": 0,
        "base": 121,
        "kept": 1
      },
      {
        "signal_hour": 14,
        "own_volume_bin": 1,
        "base": 57,
        "kept": 1
      }
    ],
    "kept_net": -1902.25,
    "kept_dd": 7375.25,
    "random_net_mean": -4517.665,
    "p_random_net_ge_kept": 0.37,
    "p_kept_better_net_and_dd": 0.609
  },
  "CTS5_20": {
    "non_executable_signal_only": true,
    "runs": 1000,
    "kept_windows": 25,
    "informative": true,
    "strata": [
      {
        "signal_hour": 9,
        "own_volume_bin": 0,
        "base": 1949,
        "kept": 1
      },
      {
        "signal_hour": 9,
        "own_volume_bin": 2,
        "base": 275,
        "kept": 1
      },
      {
        "signal_hour": 10,
        "own_volume_bin": 0,
        "base": 1774,
        "kept": 1
      },
      {
        "signal_hour": 10,
        "own_volume_bin": 1,
        "base": 666,
        "kept": 1
      },
      {
        "signal_hour": 10,
        "own_volume_bin": 2,
        "base": 429,
        "kept": 2
      },
      {
        "signal_hour": 11,
        "own_volume_bin": 0,
        "base": 1533,
        "kept": 2
      },
      {
        "signal_hour": 11,
        "own_volume_bin": 1,
        "base": 656,
        "kept": 1
      },
      {
        "signal_hour": 11,
        "own_volume_bin": 2,
        "base": 590,
        "kept": 2
      },
      {
        "signal_hour": 12,
        "own_volume_bin": 0,
        "base": 1418,
        "kept": 5
      },
      {
        "signal_hour": 12,
        "own_volume_bin": 1,
        "base": 639,
        "kept": 1
      },
      {
        "signal_hour": 13,
        "own_volume_bin": 0,
        "base": 1423,
        "kept": 2
      },
      {
        "signal_hour": 13,
        "own_volume_bin": 1,
        "base": 611,
        "kept": 3
      },
      {
        "signal_hour": 13,
        "own_volume_bin": 2,
        "base": 700,
        "kept": 3
      }
    ],
    "kept_net": 2343.75,
    "kept_dd": 2206.0,
    "random_net_mean": -589.185,
    "p_random_net_ge_kept": 0.149,
    "p_kept_better_net_and_dd": 0.654
  },
  "CTS15_15": {
    "non_executable_signal_only": true,
    "runs": 1000,
    "kept_windows": 20,
    "informative": true,
    "strata": [
      {
        "signal_hour": 9,
        "own_volume_bin": 0,
        "base": 710,
        "kept": 1
      },
      {
        "signal_hour": 10,
        "own_volume_bin": 0,
        "base": 601,
        "kept": 1
      },
      {
        "signal_hour": 10,
        "own_volume_bin": 1,
        "base": 203,
        "kept": 1
      },
      {
        "signal_hour": 10,
        "own_volume_bin": 2,
        "base": 105,
        "kept": 1
      },
      {
        "signal_hour": 11,
        "own_volume_bin": 0,
        "base": 560,
        "kept": 2
      },
      {
        "signal_hour": 11,
        "own_volume_bin": 2,
        "base": 145,
        "kept": 1
      },
      {
        "signal_hour": 12,
        "own_volume_bin": 0,
        "base": 504,
        "kept": 4
      },
      {
        "signal_hour": 12,
        "own_volume_bin": 1,
        "base": 218,
        "kept": 2
      },
      {
        "signal_hour": 12,
        "own_volume_bin": 2,
        "base": 146,
        "kept": 1
      },
      {
        "signal_hour": 13,
        "own_volume_bin": 0,
        "base": 478,
        "kept": 3
      },
      {
        "signal_hour": 13,
        "own_volume_bin": 1,
        "base": 193,
        "kept": 1
      },
      {
        "signal_hour": 14,
        "own_volume_bin": 0,
        "base": 123,
        "kept": 1
      },
      {
        "signal_hour": 14,
        "own_volume_bin": 1,
        "base": 44,
        "kept": 1
      }
    ],
    "kept_net": 1440.0,
    "kept_dd": 856.75,
    "random_net_mean": -354.935,
    "p_random_net_ge_kept": 0.235,
    "p_kept_better_net_and_dd": 0.763
  }
}
```

## Data, clocks and remaining limits

```json
{
  "intake": {
    "NQ": {
      "symbol": "NQ",
      "rows": 1769357,
      "exact_duplicates": 0,
      "conflicting_keys": 0,
      "first": 20171201,
      "last": 20221230,
      "clock": "native CT minute close labels"
    },
    "ES": {
      "symbol": "ES",
      "rows": 2096132,
      "exact_duplicates": 0,
      "conflicting_keys": 0,
      "first": 20170102,
      "last": 20221230,
      "clock": "native CT minute close labels"
    }
  },
  "date_mapping": {
    "5": {
      "nq_dates": 1825,
      "exact_ES_dates": 1825,
      "missing_ES_dates": 0,
      "normal_reference_dates": 1249,
      "calendar_roll_dates": 80,
      "frame_minutes": 5
    },
    "15": {
      "nq_dates": 1825,
      "exact_ES_dates": 1825,
      "missing_ES_dates": 0,
      "normal_reference_dates": 1249,
      "calendar_roll_dates": 80,
      "frame_minutes": 15
    }
  }
}
```

Current generic exporter emits Ticks. Intake-only2018OFcorroboration has25,188matched minute
rows; nativeNQquantity equals aggressive-buy+sell sum on98.3762%,
versus0.0040%matching buys alone. This supports total-quantity interpretation
in that sample, NOT all-year/ES/export-vintage/contract parity. OF fields do not enter the strategy. Exporter/
audit source hashes are retained. Native source roll-switch timing is not independently verified.

Synthetic checks passed notional units, long/short price symmetry, current/previous switch and own-volume
guards, prior-only medians invariant to current/future mutation, exact missing-data windows without stretching,
and shared calendar/entrybar/gap/through/delay checks. Source hashes, all eligible signal features, rolls/date
mapping and suppression/missing-entry counts are preserved. Held-gap tickets acrossactual ledgers:2,
retained in design_held_gap_tickets.csv, never deleted. All rawdata/reference checks have their stated limits.

No basic/complete candidate pass. No2023+validation, expensive post-pass placebos/resampling/MC, accountbench,
independent promotion orPowerLanguage. Positive small-count variants are not t4.5/t5/t6; do not lower thresholds,
flip direction, tune exits or nominate controls after seeing this failure. Continue a distinct mechanism.
Actual raw-data execution completed2026-10-26T03:37:04.180423+00:00; see design_verified_execution.json.
Claude review path: agents/codex/results/relative_turnover_switch.md.
