# NQ Auction Demand Confirmation: REJECT; continue distinct research

Summary: All three candidates failed 2018–22 design. Primary 15-minute rule: 199 trades,
net $-3,677.75/NQ, trade t -0.378, daily Newey-West(5) t -0.344.
Both 5-minute and stricter demand variants also lost money; all failed matched random-drop gates.
No 2023+ returns tested. Program: 55 counted evaluations / 54 unique rules; no t4.5/t5/t6 milestone.

Plan: agents/codex/plans/auction_demand_confirmation.md, preregistration 3db3857 (amends d03cdcb before returns).
Scripts: analysis/codex_auction_demand_confirmation.py and analysis/codex_auction_demand_confirmation_report.py.
Outputs: analysis/outputs/codex_auction_demand_confirmation/.
Five models: three candidates and two unselectable same-clock ZN price-confirmation controls.
Prior program: 50 evaluations / 49 unique rules, plus unknown larger repository and author searches.
Uniform and stratified random subsets are nonselectable diagnostics, not extra economic configurations.

## Trade as tested

Use nominal, non-FRN Treasury Note/Bond auctions closing at 13:00 ET (12:00 CT). Map terms to the nearest
2/3/5/7/10/20/30-year tenor within half a year; reject equal-distance ties. Separate reopening and original
issues. The reference is the median of the exact six strictly prior results in that group, requiring at least
four positive finite observations. Missing results retain their history slots. Prior December 2017 auction
metadata can seed references, but all price execution starts in 2018. Multiple simultaneous eligible events
would skip that date. No such design-period date occurred.

D = published bid-to-cover / prior reference − 1. This is a historical deviation, not a consensus surprise,
when-issued yield tail, observed dealer inventory or forced next-day hedge. The proposed mechanism was that
an auction-demand result and same-direction bond repricing might leave further equity adjustment after entry.
The design result does not support that mechanism.

At 12:15 CT (ADC15 primary) or 12:05 (ADC5), measure ZN's close change from the exact 11:59 close.
Buy NQ if both D and the ZN change are positive; sell if both are negative. ADC15_D05 additionally requires
|D| >= 0.05. A zero D or ZN change produces no candidate. ZN15/ZN5 controls omit the demand sign/size gate
and keep identical reference, date and data eligibility. Only NQ is traded; ZN is an input.

On shared-calendar normal cash dates, require exact NQ/ZN mapping and complete positive, valid OHLC and
nonnegative volume from 11:59 through the decision close. No forward fill or future-day completeness mask.
Decision j enters at native open j+2: 12:17/12:07 close-labelled minute, one additional whole minute after
the decision. One contract and at most one trade per event date. Stop 0.15 of prior 15-weekday calendar ATR,
target 0.30, rounded up to 0.25 point; entry-bar protection active; exit at 12:55 CT. No overnight holding,
retrigger, break-even, trailing stop or return rescaling.

Shared grid._walk/F.replay execution charges NQ $7.25 round trip plus one tick ($5) per market/stop fill.
Native MNQ is priced independently at $1.24 round trip plus $0.50 per such fill. Target needs one NQ point
through; stop gaps fill at the worse native open. Fixed four-tick slippage is a nonselectable stress test.

## Design results

2018–22 only. Daily grid: 2018-01-02 through 2022-12-30, 1259 cash sessions
including zero-return days. Dollars are per NQ except native net_mnq rows. Shared metrics include all trades,
both sides, every year, NW5/NW20, initial-zero drawdown, costs, native micro costs and fill stress.

| model | period | side | trades | win | avg | total | t_trade | t_nw5 | t_nw20 | sharpe | sortino | profit_factor | calmar | ulcer | max_dd | cost | missing_held_minutes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ADC15 | 2018-22 | all | 199 | 0.44724 | -18.481 | -3677.8 | -0.37757 | -0.34422 | -0.31394 | -0.16923 | -0.26447 | 0.92666 | -0.072232 | 7.1152 | 10191 | 3387.8 | 0 |
| ADC15 | 2018 | all | 23 | 0.47826 | 69.707 | 1603.2 | 0.79165 | 0.76457 | 0.74862 | 0.79916 | 1.4736 | 1.6057 | 1.6255 | 0.62072 | 990.25 | 386.75 | 0 |
| ADC15 | 2019 | all | 38 | 0.55263 | -40.539 | -1540.5 | -0.99604 | -1.1418 | -0.98194 | -0.99613 | -1.2228 | 0.66643 | -0.5793 | 2.6695 | 2659.2 | 650.5 | 0 |
| ADC15 | 2020 | all | 32 | 0.5 | 27.438 | 878 | 0.25821 | 0.25963 | 0.22161 | 0.26106 | 0.43123 | 1.1217 | 0.1974 | 5.0986 | 4430.2 | 547 | 0 |
| ADC15 | 2021 | all | 52 | 0.38462 | -37.058 | -1927 | -0.4581 | -0.48376 | -0.55213 | -0.4609 | -0.69991 | 0.84959 | -0.42345 | 4.4496 | 4550.8 | 887 | 0 |
| ADC15 | 2022 | all | 54 | 0.38889 | -49.843 | -2691.5 | -0.34639 | -0.30033 | -0.26772 | -0.34933 | -0.54797 | 0.88223 | -0.36264 | 8.8124 | 7451.5 | 916.5 | 0 |
| ADC15 | 2018-22 | long | 102 | 0.46078 | -101.86 | -10390 | -1.4311 | -1.3146 | -1.2281 | -0.63728 | -0.86287 | 0.66683 | -0.15884 | 9.7224 | 13092 | 1744.5 | 0 |
| ADC15 | 2018 | long | 8 | 0.625 | 67.125 | 537 | 0.4559 | 0.48164 | 0.48697 | 0.48052 | 1.0138 | 1.6782 | 0.85408 | 0.51474 | 631.25 | 133 | 0 |
| ADC15 | 2019 | long | 18 | 0.72222 | 31.361 | 564.5 | 0.8792 | 0.95656 | 1.077 | 0.88441 | 1.2866 | 1.6479 | 1.1853 | 0.34852 | 476.25 | 310.5 | 0 |
| ADC15 | 2020 | long | 16 | 0.4375 | -86.625 | -1386 | -0.6239 | -0.55276 | -0.51994 | -0.63415 | -0.853 | 0.6875 | -0.42108 | 4.1932 | 3278.5 | 276 | 0 |
| ADC15 | 2021 | long | 27 | 0.44444 | -72.435 | -1955.8 | -0.74741 | -0.81074 | -0.99024 | -0.75294 | -0.97495 | 0.68652 | -0.54008 | 4.5198 | 3621.2 | 465.75 | 0 |
| ADC15 | 2022 | long | 33 | 0.30303 | -246.95 | -8149.2 | -1.3002 | -1.1814 | -1.0943 | -1.2911 | -1.7452 | 0.5676 | -0.96007 | 11.707 | 8522 | 559.25 | 0 |
| ADC15 | 2018-22 | short | 97 | 0.43299 | 69.193 | 6711.8 | 1.0458 | 1.0499 | 1.1127 | 0.46769 | 0.96475 | 1.3539 | 0.48586 | 2.3541 | 2765 | 1643.2 | 0 |
| ADC15 | 2018 | short | 15 | 0.4 | 71.083 | 1066.2 | 0.62585 | 0.61754 | 0.76566 | 0.63946 | 1.122 | 1.5747 | 1.1517 | 0.62454 | 929.5 | 253.75 | 0 |
| ADC15 | 2019 | short | 20 | 0.4 | -105.25 | -2105 | -1.5452 | -1.6872 | -1.5345 | -1.4979 | -1.7825 | 0.43822 | -0.88048 | 2.6486 | 2390.8 | 340 | 0 |
| ADC15 | 2020 | short | 16 | 0.5625 | 141.5 | 2264 | 0.88339 | 0.96253 | 0.96905 | 0.88738 | 1.8453 | 1.8142 | 1.539 | 1.2447 | 1465.2 | 271 | 0 |
| ADC15 | 2021 | short | 25 | 0.32 | 1.15 | 28.75 | 0.0086154 | 0.0090645 | 0.0094186 | 0.0087755 | 0.015246 | 1.0044 | 0.012789 | 1.9622 | 2248 | 421.25 | 0 |
| ADC15 | 2022 | short | 21 | 0.52381 | 259.89 | 5457.8 | 1.26 | 1.221 | 1.4133 | 1.2465 | 3.582 | 2.3619 | 3.4763 | 1.2676 | 1576.2 | 357.25 | 0 |
| ADC15 | 2018-22 | net_mnq | 199 | 0.43216 | -2.3631 | -470.26 | -0.48279 | -0.4401 | -0.40131 | -0.21635 | -0.33592 | 0.90729 | -0.088556 | 0.80856 | 1062.9 | 441.26 | 0 |
| ADC15 | 2018-22 | stress_four_ticks | 199 | 0.41709 | -47.803 | -9512.8 | -0.97446 | -0.88762 | -0.80877 | -0.43601 | -0.65814 | 0.82244 | -0.14997 | 10.168 | 12696 | 9222.8 | 0 |
| ADC5 | 2018-22 | all | 204 | 0.44608 | -32.324 | -6594 | -0.61937 | -0.63928 | -0.65279 | -0.27745 | -0.42289 | 0.88839 | -0.13472 | 9.5149 | 9796.8 | 3459 | 0 |
| ADC5 | 2018 | all | 25 | 0.6 | 87.55 | 2188.8 | 1.0292 | 1.0181 | 1.0976 | 1.0302 | 1.9241 | 1.7606 | 2.0263 | 0.6505 | 1084.5 | 416.25 | 0 |
| ADC5 | 2019 | all | 38 | 0.44737 | -56.855 | -2160.5 | -1.2775 | -1.2238 | -1.1199 | -1.2686 | -1.5504 | 0.59482 | -0.68932 | 2.9988 | 3134.2 | 650.5 | 0 |
| ADC5 | 2020 | all | 31 | 0.48387 | -79.831 | -2474.8 | -0.57097 | -0.69468 | -0.76495 | -0.57538 | -0.79075 | 0.76377 | -0.42683 | 7.0185 | 5775 | 529.75 | 0 |
| ADC5 | 2021 | all | 52 | 0.42308 | -12.827 | -667 | -0.15076 | -0.14872 | -0.1768 | -0.1519 | -0.22364 | 0.95093 | -0.13323 | 6.8671 | 5006.5 | 882 | 0 |
| ADC5 | 2022 | all | 58 | 0.37931 | -60.009 | -3480.5 | -0.41914 | -0.43034 | -0.42471 | -0.4223 | -0.674 | 0.87014 | -0.37835 | 8.0522 | 9235.8 | 980.5 | 0 |
| ADC5 | 2018-22 | long | 104 | 0.45192 | -58.067 | -6039 | -0.72915 | -0.84799 | -0.83462 | -0.32689 | -0.47399 | 0.82266 | -0.12373 | 7.1264 | 9769.2 | 1769 | 0 |
| ADC5 | 2018 | long | 8 | 0.75 | 225.25 | 1802 | 1.4844 | 1.4192 | 1.5182 | 1.3893 | 6.6044 | 6.3078 | 6.8987 | 0.15403 | 262.25 | 128 | 0 |
| ADC5 | 2019 | long | 19 | 0.52632 | -8.5658 | -162.75 | -0.19116 | -0.16165 | -0.15227 | -0.19583 | -0.26224 | 0.89766 | -0.11455 | 1.1554 | 1420.8 | 327.75 | 0 |
| ADC5 | 2020 | long | 15 | 0.46667 | -118.58 | -1778.8 | -0.58905 | -0.94797 | -0.90026 | -0.60036 | -0.76785 | 0.6744 | -0.37315 | 6.6672 | 4748 | 258.75 | 0 |
| ADC5 | 2021 | long | 28 | 0.46429 | -32.071 | -898 | -0.31978 | -0.35349 | -0.37605 | -0.32445 | -0.43681 | 0.86042 | -0.27854 | 3.6873 | 3224 | 483 | 0 |
| ADC5 | 2022 | long | 34 | 0.32353 | -147.1 | -5001.5 | -0.70526 | -0.8162 | -0.81792 | -0.71124 | -1.0574 | 0.75273 | -0.6474 | 8.3937 | 7756.2 | 571.5 | 0 |
| ADC5 | 2018-22 | short | 100 | 0.44 | -5.55 | -555 | -0.082586 | -0.084052 | -0.095216 | -0.037118 | -0.061742 | 0.97782 | -0.016358 | 6.2861 | 6791.2 | 1690 | 0 |
| ADC5 | 2018 | short | 17 | 0.52941 | 22.75 | 386.75 | 0.22307 | 0.21939 | 0.27197 | 0.2296 | 0.35021 | 1.1524 | 0.35804 | 0.7628 | 1084.5 | 288.25 | 0 |
| ADC5 | 2019 | short | 19 | 0.36842 | -105.14 | -1997.8 | -1.3717 | -1.6053 | -1.6606 | -1.3431 | -1.6011 | 0.46613 | -1 | 2.4113 | 1997.8 | 322.75 | 0 |
| ADC5 | 2020 | short | 16 | 0.5 | -43.5 | -696 | -0.21721 | -0.23554 | -0.27045 | -0.22312 | -0.33075 | 0.86116 | -0.24503 | 2.9434 | 2829.2 | 271 | 0 |
| ADC5 | 2021 | short | 24 | 0.375 | 9.625 | 231 | 0.066477 | 0.063122 | 0.075439 | 0.067766 | 0.10691 | 1.0323 | 0.06647 | 4.7973 | 3475.2 | 399 | 0 |
| ADC5 | 2022 | short | 24 | 0.45833 | 63.375 | 1521 | 0.34778 | 0.37283 | 0.41221 | 0.35441 | 0.73388 | 1.2314 | 0.62354 | 1.3177 | 2449 | 409 | 0 |
| ADC5 | 2018-22 | net_mnq | 204 | 0.44118 | -3.7474 | -764.46 | -0.71805 | -0.74114 | -0.75643 | -0.32157 | -0.48722 | 0.87187 | -0.1481 | 1.0665 | 1033.2 | 450.96 | 0 |
| ADC5 | 2018-22 | stress_four_ticks | 204 | 0.42647 | -61.441 | -12534 | -1.1743 | -1.2113 | -1.2331 | -0.52498 | -0.77531 | 0.79958 | -0.17102 | 13.873 | 14670 | 9399 | 0 |
| ADC15_D05 | 2018-22 | all | 82 | 0.47561 | -27.677 | -2269.5 | -0.37693 | -0.35206 | -0.33296 | -0.16947 | -0.24058 | 0.89457 | -0.043044 | 8.2471 | 10554 | 1404.5 | 0 |
| ADC15_D05 | 2018 | all | 7 | 0.42857 | -24.393 | -170.75 | -0.1249 | -0.13475 | -0.13629 | -0.13474 | -0.18182 | 0.89388 | -0.14153 | 0.75163 | 1211.2 | 120.75 | 0 |
| ADC15_D05 | 2019 | all | 13 | 0.53846 | -59.558 | -774.25 | -0.76877 | -0.81021 | -0.82995 | -0.78055 | -0.98089 | 0.5622 | -0.75042 | 1.2744 | 1031.8 | 219.25 | 0 |
| ADC15_D05 | 2020 | all | 22 | 0.45455 | -41.114 | -904.5 | -0.32261 | -0.32511 | -0.27281 | -0.32816 | -0.50278 | 0.83868 | -0.21756 | 4.4566 | 4141 | 379.5 | 0 |
| ADC15_D05 | 2021 | all | 18 | 0.44444 | -55.583 | -1000.5 | -0.42979 | -0.41158 | -0.43045 | -0.43917 | -0.61908 | 0.77066 | -0.4541 | 2.4585 | 2203.2 | 305.5 | 0 |
| ADC15_D05 | 2022 | all | 22 | 0.5 | 26.386 | 580.5 | 0.1251 | 0.11531 | 0.11135 | 0.128 | 0.17978 | 1.071 | 0.10769 | 5.5651 | 5412 | 379.5 | 0 |
| ADC15_D05 | 2018-22 | long | 43 | 0.46512 | -102.6 | -4411.8 | -0.92599 | -0.87376 | -0.84814 | -0.41495 | -0.53139 | 0.67719 | -0.11056 | 5.8683 | 7987 | 741.75 | 0 |
| ADC15_D05 | 2018 | long | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| ADC15_D05 | 2019 | long | 3 | 0.66667 | 31.083 | 93.25 | 0.32387 | 0.39055 | 0.39531 | 0.386 | 0.76278 | 1.7628 | 0.76278 | 0.055295 | 122.25 | 51.75 | 0 |
| ADC15_D05 | 2020 | long | 11 | 0.45455 | -125.89 | -1384.8 | -0.87359 | -0.80144 | -0.78493 | -0.88102 | -1.0513 | 0.5206 | -0.5651 | 2.9635 | 2440.8 | 189.75 | 0 |
| ADC15_D05 | 2021 | long | 13 | 0.53846 | -10.327 | -134.25 | -0.069479 | -0.072043 | -0.072503 | -0.072159 | -0.1057 | 0.94922 | -0.090434 | 0.95337 | 1484.5 | 224.25 | 0 |
| ADC15_D05 | 2022 | long | 16 | 0.375 | -186.62 | -2986 | -0.7205 | -0.68848 | -0.66948 | -0.73235 | -0.92598 | 0.62733 | -0.55394 | 6.9709 | 5412 | 276 | 0 |
| ADC15_D05 | 2018-22 | short | 39 | 0.48718 | 54.929 | 2142.2 | 0.58356 | 0.5788 | 0.55896 | 0.26325 | 0.47827 | 1.2726 | 0.14129 | 3.3969 | 3034.8 | 662.75 | 0 |
| ADC15_D05 | 2018 | short | 7 | 0.42857 | -24.393 | -170.75 | -0.1249 | -0.13475 | -0.13629 | -0.13474 | -0.18182 | 0.89388 | -0.14153 | 0.75163 | 1211.2 | 120.75 | 0 |
| ADC15_D05 | 2019 | short | 10 | 0.5 | -86.75 | -867.5 | -0.89319 | -0.93963 | -0.95975 | -0.90203 | -1.1124 | 0.47304 | -0.8408 | 1.4109 | 1031.8 | 167.5 | 0 |
| ADC15_D05 | 2020 | short | 11 | 0.45455 | 43.659 | 480.25 | 0.20354 | 0.22602 | 0.20572 | 0.21221 | 0.39193 | 1.1767 | 0.28134 | 1.7015 | 1700.2 | 189.75 | 0 |
| ADC15_D05 | 2021 | short | 5 | 0.2 | -173.25 | -866.25 | -0.61723 | -0.55349 | -0.54521 | -0.65866 | -0.86685 | 0.49607 | -0.64912 | 1.8611 | 1334.5 | 81.25 | 0 |
| ADC15_D05 | 2022 | short | 6 | 0.83333 | 594.42 | 3566.5 | 2.4331 | 1.7944 | 2.092 | 1.8153 | 21.367 | 22.324 | 21.409 | 0.10209 | 167.25 | 103.5 | 0 |
| ADC15_D05 | 2018-22 | net_mnq | 82 | 0.46341 | -3.2827 | -269.18 | -0.44707 | -0.41749 | -0.39475 | -0.20094 | -0.28358 | 0.87624 | -0.049932 | 0.88195 | 1079 | 182.68 | 0 |
| ADC15_D05 | 2018-22 | stress_four_ticks | 82 | 0.45122 | -57.311 | -4699.5 | -0.78005 | -0.72733 | -0.68703 | -0.34977 | -0.48054 | 0.79448 | -0.078923 | 9.7179 | 11918 | 3834.5 | 0 |
| ZN15 | 2018-22 | all | 290 | 0.48621 | -17.25 | -5002.5 | -0.44714 | -0.40298 | -0.36757 | -0.20026 | -0.29794 | 0.92928 | -0.085821 | 8.5727 | 11667 | 4952.5 | 0 |
| ZN15 | 2018 | all | 34 | 0.52941 | 30.103 | 1023.5 | 0.46215 | 0.39664 | 0.40168 | 0.46778 | 0.76573 | 1.2587 | 0.70745 | 0.95603 | 1452.5 | 576.5 | 0 |
| ZN15 | 2019 | all | 55 | 0.56364 | -10.341 | -568.75 | -0.29495 | -0.33865 | -0.31023 | -0.29689 | -0.4141 | 0.90391 | -0.22741 | 2.4202 | 2501 | 938.75 | 0 |
| ZN15 | 2020 | all | 59 | 0.50847 | -12.589 | -742.75 | -0.16072 | -0.18156 | -0.15239 | -0.16144 | -0.22927 | 0.94876 | -0.10375 | 7.6897 | 7131 | 1012.8 | 0 |
| ZN15 | 2021 | all | 70 | 0.42857 | -8.3929 | -587.5 | -0.1223 | -0.12245 | -0.15007 | -0.12293 | -0.18904 | 0.9637 | -0.1551 | 3.4386 | 3788 | 1197.5 | 0 |
| ZN15 | 2022 | all | 72 | 0.44444 | -57.319 | -4127 | -0.48171 | -0.40366 | -0.35638 | -0.48453 | -0.72384 | 0.86328 | -0.35513 | 13.449 | 11667 | 1227 | 0 |
| ZN15 | 2018-22 | long | 161 | 0.50311 | -84.983 | -13682 | -1.6284 | -1.581 | -1.485 | -0.72527 | -0.95625 | 0.69893 | -0.16537 | 11.854 | 16560 | 2757.2 | 0 |
| ZN15 | 2018 | long | 15 | 0.6 | -17.583 | -263.75 | -0.18383 | -0.1615 | -0.16228 | -0.19006 | -0.28459 | 0.86429 | -0.24007 | 0.84917 | 1103 | 253.75 | 0 |
| ZN15 | 2019 | long | 32 | 0.6875 | 54.156 | 1733 | 1.3807 | 1.4342 | 1.5162 | 1.3639 | 2.5882 | 1.9206 | 2.1944 | 0.65021 | 789.75 | 547 | 0 |
| ZN15 | 2020 | long | 34 | 0.52941 | -81.662 | -2776.5 | -0.78065 | -0.83278 | -0.80617 | -0.78303 | -0.97968 | 0.71957 | -0.45698 | 7.1476 | 6051.8 | 586.5 | 0 |
| ZN15 | 2021 | long | 40 | 0.475 | -34.875 | -1395 | -0.4354 | -0.46427 | -0.54882 | -0.43918 | -0.59384 | 0.84061 | -0.31604 | 5.5495 | 4414 | 690 | 0 |
| ZN15 | 2022 | long | 40 | 0.325 | -274.5 | -10980 | -1.6689 | -1.5793 | -1.4841 | -1.6416 | -2.1515 | 0.5219 | -0.93181 | 15.48 | 11830 | 680 | 0 |
| ZN15 | 2018-22 | short | 129 | 0.46512 | 67.285 | 8679.8 | 1.1887 | 1.148 | 1.1642 | 0.53103 | 0.9879 | 1.3431 | 0.46996 | 2.8974 | 3696.8 | 2195.2 | 0 |
| ZN15 | 2018 | short | 19 | 0.47368 | 67.75 | 1287.2 | 0.75171 | 0.73864 | 0.91665 | 0.76133 | 1.3365 | 1.6396 | 1.3904 | 0.62308 | 929.5 | 322.75 | 0 |
| ZN15 | 2019 | short | 23 | 0.3913 | -100.08 | -2301.8 | -1.675 | -1.8267 | -1.6464 | -1.6181 | -1.9194 | 0.42977 | -0.91776 | 2.7131 | 2508 | 391.75 | 0 |
| ZN15 | 2020 | short | 25 | 0.48 | 81.35 | 2033.8 | 0.69026 | 0.71092 | 0.67072 | 0.69552 | 1.2959 | 1.4427 | 0.66712 | 2.7269 | 3036.5 | 426.25 | 0 |
| ZN15 | 2021 | short | 30 | 0.36667 | 26.917 | 807.5 | 0.22303 | 0.23252 | 0.24229 | 0.22622 | 0.39687 | 1.1086 | 0.35921 | 1.6816 | 2248 | 507.5 | 0 |
| ZN15 | 2022 | short | 32 | 0.59375 | 214.16 | 6853 | 1.3246 | 1.2261 | 1.3068 | 1.3137 | 2.6957 | 1.9493 | 1.9542 | 3.0185 | 3520.8 | 547 | 0 |
| ZN15 | 2018-22 | net_mnq | 290 | 0.47586 | -2.24 | -649.6 | -0.58064 | -0.52332 | -0.47714 | -0.26 | -0.3844 | 0.90917 | -0.10419 | 0.98955 | 1247.9 | 644.6 | 0 |
| ZN15 | 2018-22 | stress_four_ticks | 290 | 0.44828 | -46.733 | -13552 | -1.2093 | -1.0899 | -0.99184 | -0.54068 | -0.77752 | 0.82028 | -0.15987 | 14.129 | 16968 | 13502 | 0 |
| ZN5 | 2018-22 | all | 288 | 0.48264 | -12.302 | -3543 | -0.28288 | -0.28592 | -0.28882 | -0.12671 | -0.19267 | 0.95614 | -0.05821 | 7.8982 | 12183 | 4883 | 0 |
| ZN5 | 2018 | all | 33 | 0.60606 | 69.265 | 2285.8 | 0.92537 | 0.76127 | 0.82953 | 0.92898 | 1.5677 | 1.5262 | 1.3727 | 1.0166 | 1671.8 | 549.25 | 0 |
| ZN5 | 2019 | all | 51 | 0.5098 | -12.838 | -654.75 | -0.32477 | -0.33748 | -0.31418 | -0.32707 | -0.45233 | 0.89108 | -0.24417 | 2.462 | 2681.5 | 874.75 | 0 |
| ZN5 | 2020 | all | 58 | 0.51724 | 1.8017 | 104.5 | 0.017245 | 0.0195 | 0.019839 | 0.017327 | 0.026365 | 1.0059 | 0.013653 | 7.1291 | 7623.8 | 975.5 | 0 |
| ZN5 | 2021 | all | 72 | 0.47222 | -3.2222 | -232 | -0.047037 | -0.047285 | -0.050425 | -0.047273 | -0.069066 | 0.98679 | -0.034685 | 8.9611 | 6688.8 | 1227 | 0 |
| ZN5 | 2022 | all | 74 | 0.39189 | -68.196 | -5046.5 | -0.54085 | -0.53997 | -0.55258 | -0.54377 | -0.83671 | 0.85688 | -0.41588 | 10.937 | 12183 | 1256.5 | 0 |
| ZN5 | 2018-22 | long | 155 | 0.50968 | -30.056 | -4658.8 | -0.49565 | -0.5517 | -0.57449 | -0.22223 | -0.32151 | 0.89797 | -0.10223 | 6.0788 | 9121.8 | 2633.8 | 0 |
| ZN5 | 2018 | long | 14 | 0.71429 | 144.54 | 2023.5 | 1.1467 | 0.95492 | 1.0675 | 1.1369 | 2.1802 | 2.2694 | 3.0447 | 0.39474 | 667.25 | 226.5 | 0 |
| ZN5 | 2019 | long | 31 | 0.58065 | 40.331 | 1250.2 | 0.93925 | 0.86437 | 0.79236 | 0.94083 | 1.7037 | 1.551 | 0.90795 | 1.1551 | 1377 | 534.75 | 0 |
| ZN5 | 2020 | long | 28 | 0.57143 | -47.786 | -1338 | -0.32524 | -0.4012 | -0.37288 | -0.32932 | -0.43281 | 0.85882 | -0.26756 | 6.1866 | 4981 | 473 | 0 |
| ZN5 | 2021 | long | 42 | 0.52381 | -15.345 | -644.5 | -0.19639 | -0.22106 | -0.22159 | -0.1983 | -0.27015 | 0.92758 | -0.17018 | 4.8228 | 3787.2 | 724.5 | 0 |
| ZN5 | 2022 | long | 40 | 0.325 | -148.75 | -5950 | -0.79096 | -0.89498 | -1.0241 | -0.79568 | -1.1827 | 0.74595 | -0.69719 | 9.0711 | 8568.2 | 675 | 0 |
| ZN5 | 2018-22 | short | 133 | 0.45113 | 8.3891 | 1115.8 | 0.13435 | 0.14347 | 0.15801 | 0.060308 | 0.098547 | 1.0318 | 0.045668 | 4.2855 | 4890.2 | 2249.2 | 0 |
| ZN5 | 2018 | short | 19 | 0.52632 | 13.803 | 262.25 | 0.15023 | 0.14785 | 0.18145 | 0.15425 | 0.23322 | 1.0954 | 0.24278 | 0.83364 | 1084.5 | 322.75 | 0 |
| ZN5 | 2019 | short | 20 | 0.4 | -95.25 | -1905 | -1.2979 | -1.5223 | -1.564 | -1.2778 | -1.5268 | 0.49091 | -0.95357 | 2.3825 | 1997.8 | 340 | 0 |
| ZN5 | 2020 | short | 30 | 0.46667 | 48.083 | 1442.5 | 0.32009 | 0.3841 | 0.42043 | 0.32377 | 0.58151 | 1.1775 | 0.38618 | 3.0089 | 3720.5 | 502.5 | 0 |
| ZN5 | 2021 | short | 30 | 0.4 | 13.75 | 412.5 | 0.11054 | 0.10496 | 0.13316 | 0.11219 | 0.17444 | 1.0476 | 0.10706 | 5.1986 | 3853 | 502.5 | 0 |
| ZN5 | 2022 | short | 34 | 0.47059 | 26.574 | 903.5 | 0.16212 | 0.177 | 0.18486 | 0.1645 | 0.2716 | 1.0763 | 0.20698 | 4.0236 | 4382.5 | 581.5 | 0 |
| ZN5 | 2018-22 | net_mnq | 288 | 0.47917 | -1.7452 | -502.62 | -0.4013 | -0.40559 | -0.40949 | -0.17974 | -0.27166 | 0.93837 | -0.080569 | 0.91598 | 1248.7 | 636.62 | 0 |
| ZN5 | 2018-22 | stress_four_ticks | 288 | 0.45833 | -41.417 | -11928 | -0.95005 | -0.95924 | -0.96602 | -0.4251 | -0.62602 | 0.86028 | -0.16316 | 11.625 | 14633 | 13268 | 0 |

## Filter falsifiers and selection gate

Because there is at most one event per date, candidate ledgers are actual executable subsets of the matching
same-clock controls: identical entry, side, brackets, exits and costs. There is no overlapping virtual-book
profit being called executable. The table below preserves base/kept/removed total profits, removed mean/t,
and 1,000 uniformly sampled matched-size subsets. design_uniform_draws.json archives the shared helper's
same seeded draws; all three summary values reconcile exactly within numerical tolerance.

```json
{
  "ADC15": {
    "non_executable_signal_only": false,
    "base_trades": 290,
    "kept_trades": 199,
    "removed_trades": 91,
    "base_net": -5002.5,
    "kept_net": -3677.75,
    "removed_net": -1324.75,
    "removed_avg": -14.557692307692308,
    "removed_t": -0.23921741987089867,
    "random_subsets": 1000,
    "random_net_mean": -3411.335,
    "p_random_net_ge_kept": 0.535,
    "p_kept_better_net_and_dd": 0.406
  },
  "ADC5": {
    "non_executable_signal_only": false,
    "base_trades": 288,
    "kept_trades": 204,
    "removed_trades": 84,
    "base_net": -3543.0,
    "kept_net": -6594.0,
    "removed_net": 3051.0,
    "removed_avg": 36.32142857142857,
    "removed_t": 0.46109928117057947,
    "random_subsets": 1000,
    "random_net_mean": -2308.11,
    "p_random_net_ge_kept": 0.766,
    "p_kept_better_net_and_dd": 0.228
  },
  "ADC15_D05": {
    "non_executable_signal_only": false,
    "base_trades": 290,
    "kept_trades": 82,
    "removed_trades": 208,
    "base_net": -5002.5,
    "kept_net": -2269.5,
    "removed_net": -2733.0,
    "removed_avg": -13.139423076923077,
    "removed_t": -0.28914584204010796,
    "random_subsets": 1000,
    "random_net_mean": -1631.34,
    "p_random_net_ge_kept": 0.545,
    "p_kept_better_net_and_dd": 0.123
  }
}
```

Another 1,000 subsets preserve kept count within each (year, tenor, reopening) cell, without replacement.
Cells and summary follow; all random totals/DD are saved in design_stratified_drops.json. No cell, direction,
threshold or subset was chosen after returns.

```json
{
  "ADC15": {
    "runs": 1000,
    "informative": true,
    "actual_executable_ledger_subsets": true,
    "cells": [
      {
        "year": 2018,
        "tenor": 2,
        "reopening": "No",
        "base": 4,
        "kept": 2
      },
      {
        "year": 2018,
        "tenor": 3,
        "reopening": "No",
        "base": 5,
        "kept": 5
      },
      {
        "year": 2018,
        "tenor": 5,
        "reopening": "No",
        "base": 8,
        "kept": 5
      },
      {
        "year": 2018,
        "tenor": 7,
        "reopening": "No",
        "base": 7,
        "kept": 5
      },
      {
        "year": 2018,
        "tenor": 10,
        "reopening": "Yes",
        "base": 5,
        "kept": 3
      },
      {
        "year": 2018,
        "tenor": 30,
        "reopening": "Yes",
        "base": 5,
        "kept": 3
      },
      {
        "year": 2019,
        "tenor": 2,
        "reopening": "No",
        "base": 5,
        "kept": 5
      },
      {
        "year": 2019,
        "tenor": 3,
        "reopening": "No",
        "base": 8,
        "kept": 4
      },
      {
        "year": 2019,
        "tenor": 5,
        "reopening": "No",
        "base": 9,
        "kept": 5
      },
      {
        "year": 2019,
        "tenor": 7,
        "reopening": "No",
        "base": 11,
        "kept": 10
      },
      {
        "year": 2019,
        "tenor": 10,
        "reopening": "No",
        "base": 4,
        "kept": 4
      },
      {
        "year": 2019,
        "tenor": 10,
        "reopening": "Yes",
        "base": 7,
        "kept": 3
      },
      {
        "year": 2019,
        "tenor": 30,
        "reopening": "No",
        "base": 4,
        "kept": 1
      },
      {
        "year": 2019,
        "tenor": 30,
        "reopening": "Yes",
        "base": 7,
        "kept": 6
      },
      {
        "year": 2020,
        "tenor": 2,
        "reopening": "No",
        "base": 4,
        "kept": 2
      },
      {
        "year": 2020,
        "tenor": 3,
        "reopening": "No",
        "base": 10,
        "kept": 5
      },
      {
        "year": 2020,
        "tenor": 5,
        "reopening": "No",
        "base": 10,
        "kept": 7
      },
      {
        "year": 2020,
        "tenor": 7,
        "reopening": "No",
        "base": 12,
        "kept": 4
      },
      {
        "year": 2020,
        "tenor": 10,
        "reopening": "No",
        "base": 4,
        "kept": 3
      },
      {
        "year": 2020,
        "tenor": 10,
        "reopening": "Yes",
        "base": 8,
        "kept": 4
      },
      {
        "year": 2020,
        "tenor": 30,
        "reopening": "No",
        "base": 4,
        "kept": 4
      },
      {
        "year": 2020,
        "tenor": 30,
        "reopening": "Yes",
        "base": 6,
        "kept": 3
      },
      {
        "year": 2021,
        "tenor": 2,
        "reopening": "No",
        "base": 8,
        "kept": 6
      },
      {
        "year": 2021,
        "tenor": 3,
        "reopening": "No",
        "base": 6,
        "kept": 4
      },
      {
        "year": 2021,
        "tenor": 5,
        "reopening": "No",
        "base": 11,
        "kept": 7
      },
      {
        "year": 2021,
        "tenor": 7,
        "reopening": "No",
        "base": 12,
        "kept": 11
      },
      {
        "year": 2021,
        "tenor": 10,
        "reopening": "No",
        "base": 3,
        "kept": 2
      },
      {
        "year": 2021,
        "tenor": 10,
        "reopening": "Yes",
        "base": 8,
        "kept": 5
      },
      {
        "year": 2021,
        "tenor": 20,
        "reopening": "No",
        "base": 3,
        "kept": 2
      },
      {
        "year": 2021,
        "tenor": 20,
        "reopening": "Yes",
        "base": 8,
        "kept": 7
      },
      {
        "year": 2021,
        "tenor": 30,
        "reopening": "No",
        "base": 3,
        "kept": 3
      },
      {
        "year": 2021,
        "tenor": 30,
        "reopening": "Yes",
        "base": 8,
        "kept": 5
      },
      {
        "year": 2022,
        "tenor": 2,
        "reopening": "No",
        "base": 8,
        "kept": 6
      },
      {
        "year": 2022,
        "tenor": 3,
        "reopening": "No",
        "base": 7,
        "kept": 4
      },
      {
        "year": 2022,
        "tenor": 5,
        "reopening": "No",
        "base": 10,
        "kept": 9
      },
      {
        "year": 2022,
        "tenor": 7,
        "reopening": "No",
        "base": 12,
        "kept": 7
      },
      {
        "year": 2022,
        "tenor": 10,
        "reopening": "No",
        "base": 4,
        "kept": 4
      },
      {
        "year": 2022,
        "tenor": 10,
        "reopening": "Yes",
        "base": 8,
        "kept": 7
      },
      {
        "year": 2022,
        "tenor": 20,
        "reopening": "No",
        "base": 4,
        "kept": 3
      },
      {
        "year": 2022,
        "tenor": 20,
        "reopening": "Yes",
        "base": 7,
        "kept": 6
      },
      {
        "year": 2022,
        "tenor": 30,
        "reopening": "No",
        "base": 4,
        "kept": 3
      },
      {
        "year": 2022,
        "tenor": 30,
        "reopening": "Yes",
        "base": 8,
        "kept": 5
      }
    ],
    "kept_net": -3677.75,
    "kept_dd": 10191.25,
    "random_net_mean": -4855.97,
    "p_random_net_ge_kept": 0.412,
    "p_kept_better_net_and_dd": 0.535
  },
  "ADC5": {
    "runs": 1000,
    "informative": true,
    "actual_executable_ledger_subsets": true,
    "cells": [
      {
        "year": 2018,
        "tenor": 2,
        "reopening": "No",
        "base": 6,
        "kept": 3
      },
      {
        "year": 2018,
        "tenor": 3,
        "reopening": "No",
        "base": 5,
        "kept": 5
      },
      {
        "year": 2018,
        "tenor": 5,
        "reopening": "No",
        "base": 6,
        "kept": 4
      },
      {
        "year": 2018,
        "tenor": 7,
        "reopening": "No",
        "base": 8,
        "kept": 7
      },
      {
        "year": 2018,
        "tenor": 10,
        "reopening": "Yes",
        "base": 4,
        "kept": 3
      },
      {
        "year": 2018,
        "tenor": 30,
        "reopening": "Yes",
        "base": 4,
        "kept": 3
      },
      {
        "year": 2019,
        "tenor": 2,
        "reopening": "No",
        "base": 5,
        "kept": 4
      },
      {
        "year": 2019,
        "tenor": 3,
        "reopening": "No",
        "base": 7,
        "kept": 3
      },
      {
        "year": 2019,
        "tenor": 5,
        "reopening": "No",
        "base": 9,
        "kept": 6
      },
      {
        "year": 2019,
        "tenor": 7,
        "reopening": "No",
        "base": 11,
        "kept": 10
      },
      {
        "year": 2019,
        "tenor": 10,
        "reopening": "No",
        "base": 4,
        "kept": 4
      },
      {
        "year": 2019,
        "tenor": 10,
        "reopening": "Yes",
        "base": 6,
        "kept": 4
      },
      {
        "year": 2019,
        "tenor": 30,
        "reopening": "Yes",
        "base": 7,
        "kept": 7
      },
      {
        "year": 2020,
        "tenor": 2,
        "reopening": "No",
        "base": 5,
        "kept": 2
      },
      {
        "year": 2020,
        "tenor": 3,
        "reopening": "No",
        "base": 8,
        "kept": 5
      },
      {
        "year": 2020,
        "tenor": 5,
        "reopening": "No",
        "base": 12,
        "kept": 8
      },
      {
        "year": 2020,
        "tenor": 7,
        "reopening": "No",
        "base": 10,
        "kept": 2
      },
      {
        "year": 2020,
        "tenor": 10,
        "reopening": "No",
        "base": 4,
        "kept": 3
      },
      {
        "year": 2020,
        "tenor": 10,
        "reopening": "Yes",
        "base": 7,
        "kept": 3
      },
      {
        "year": 2020,
        "tenor": 30,
        "reopening": "No",
        "base": 4,
        "kept": 3
      },
      {
        "year": 2020,
        "tenor": 30,
        "reopening": "Yes",
        "base": 7,
        "kept": 5
      },
      {
        "year": 2021,
        "tenor": 2,
        "reopening": "No",
        "base": 7,
        "kept": 4
      },
      {
        "year": 2021,
        "tenor": 3,
        "reopening": "No",
        "base": 9,
        "kept": 5
      },
      {
        "year": 2021,
        "tenor": 5,
        "reopening": "No",
        "base": 9,
        "kept": 7
      },
      {
        "year": 2021,
        "tenor": 7,
        "reopening": "No",
        "base": 12,
        "kept": 11
      },
      {
        "year": 2021,
        "tenor": 10,
        "reopening": "No",
        "base": 4,
        "kept": 2
      },
      {
        "year": 2021,
        "tenor": 10,
        "reopening": "Yes",
        "base": 7,
        "kept": 5
      },
      {
        "year": 2021,
        "tenor": 20,
        "reopening": "No",
        "base": 3,
        "kept": 2
      },
      {
        "year": 2021,
        "tenor": 20,
        "reopening": "Yes",
        "base": 9,
        "kept": 7
      },
      {
        "year": 2021,
        "tenor": 30,
        "reopening": "No",
        "base": 4,
        "kept": 3
      },
      {
        "year": 2021,
        "tenor": 30,
        "reopening": "Yes",
        "base": 8,
        "kept": 6
      },
      {
        "year": 2022,
        "tenor": 2,
        "reopening": "No",
        "base": 8,
        "kept": 7
      },
      {
        "year": 2022,
        "tenor": 3,
        "reopening": "No",
        "base": 9,
        "kept": 6
      },
      {
        "year": 2022,
        "tenor": 5,
        "reopening": "No",
        "base": 11,
        "kept": 9
      },
      {
        "year": 2022,
        "tenor": 7,
        "reopening": "No",
        "base": 12,
        "kept": 8
      },
      {
        "year": 2022,
        "tenor": 10,
        "reopening": "No",
        "base": 4,
        "kept": 3
      },
      {
        "year": 2022,
        "tenor": 10,
        "reopening": "Yes",
        "base": 8,
        "kept": 7
      },
      {
        "year": 2022,
        "tenor": 20,
        "reopening": "No",
        "base": 3,
        "kept": 3
      },
      {
        "year": 2022,
        "tenor": 20,
        "reopening": "Yes",
        "base": 8,
        "kept": 6
      },
      {
        "year": 2022,
        "tenor": 30,
        "reopening": "No",
        "base": 3,
        "kept": 3
      },
      {
        "year": 2022,
        "tenor": 30,
        "reopening": "Yes",
        "base": 8,
        "kept": 6
      }
    ],
    "kept_net": -6594.0,
    "kept_dd": 9796.75,
    "random_net_mean": -4426.995,
    "p_random_net_ge_kept": 0.661,
    "p_kept_better_net_and_dd": 0.337
  },
  "ADC15_D05": {
    "runs": 1000,
    "informative": true,
    "actual_executable_ledger_subsets": true,
    "cells": [
      {
        "year": 2018,
        "tenor": 2,
        "reopening": "No",
        "base": 4,
        "kept": 1
      },
      {
        "year": 2018,
        "tenor": 3,
        "reopening": "No",
        "base": 5,
        "kept": 3
      },
      {
        "year": 2018,
        "tenor": 5,
        "reopening": "No",
        "base": 8,
        "kept": 1
      },
      {
        "year": 2018,
        "tenor": 7,
        "reopening": "No",
        "base": 7,
        "kept": 1
      },
      {
        "year": 2018,
        "tenor": 10,
        "reopening": "Yes",
        "base": 5,
        "kept": 1
      },
      {
        "year": 2019,
        "tenor": 2,
        "reopening": "No",
        "base": 5,
        "kept": 1
      },
      {
        "year": 2019,
        "tenor": 3,
        "reopening": "No",
        "base": 8,
        "kept": 2
      },
      {
        "year": 2019,
        "tenor": 5,
        "reopening": "No",
        "base": 9,
        "kept": 1
      },
      {
        "year": 2019,
        "tenor": 7,
        "reopening": "No",
        "base": 11,
        "kept": 4
      },
      {
        "year": 2019,
        "tenor": 10,
        "reopening": "No",
        "base": 4,
        "kept": 3
      },
      {
        "year": 2019,
        "tenor": 30,
        "reopening": "Yes",
        "base": 7,
        "kept": 2
      },
      {
        "year": 2020,
        "tenor": 2,
        "reopening": "No",
        "base": 4,
        "kept": 2
      },
      {
        "year": 2020,
        "tenor": 3,
        "reopening": "No",
        "base": 10,
        "kept": 3
      },
      {
        "year": 2020,
        "tenor": 5,
        "reopening": "No",
        "base": 10,
        "kept": 4
      },
      {
        "year": 2020,
        "tenor": 7,
        "reopening": "No",
        "base": 12,
        "kept": 2
      },
      {
        "year": 2020,
        "tenor": 10,
        "reopening": "No",
        "base": 4,
        "kept": 3
      },
      {
        "year": 2020,
        "tenor": 10,
        "reopening": "Yes",
        "base": 8,
        "kept": 3
      },
      {
        "year": 2020,
        "tenor": 30,
        "reopening": "No",
        "base": 4,
        "kept": 2
      },
      {
        "year": 2020,
        "tenor": 30,
        "reopening": "Yes",
        "base": 6,
        "kept": 3
      },
      {
        "year": 2021,
        "tenor": 2,
        "reopening": "No",
        "base": 8,
        "kept": 3
      },
      {
        "year": 2021,
        "tenor": 3,
        "reopening": "No",
        "base": 6,
        "kept": 2
      },
      {
        "year": 2021,
        "tenor": 5,
        "reopening": "No",
        "base": 11,
        "kept": 2
      },
      {
        "year": 2021,
        "tenor": 7,
        "reopening": "No",
        "base": 12,
        "kept": 2
      },
      {
        "year": 2021,
        "tenor": 10,
        "reopening": "No",
        "base": 3,
        "kept": 1
      },
      {
        "year": 2021,
        "tenor": 10,
        "reopening": "Yes",
        "base": 8,
        "kept": 3
      },
      {
        "year": 2021,
        "tenor": 20,
        "reopening": "Yes",
        "base": 8,
        "kept": 3
      },
      {
        "year": 2021,
        "tenor": 30,
        "reopening": "Yes",
        "base": 8,
        "kept": 2
      },
      {
        "year": 2022,
        "tenor": 2,
        "reopening": "No",
        "base": 8,
        "kept": 2
      },
      {
        "year": 2022,
        "tenor": 5,
        "reopening": "No",
        "base": 10,
        "kept": 6
      },
      {
        "year": 2022,
        "tenor": 7,
        "reopening": "No",
        "base": 12,
        "kept": 5
      },
      {
        "year": 2022,
        "tenor": 10,
        "reopening": "No",
        "base": 4,
        "kept": 2
      },
      {
        "year": 2022,
        "tenor": 20,
        "reopening": "No",
        "base": 4,
        "kept": 2
      },
      {
        "year": 2022,
        "tenor": 20,
        "reopening": "Yes",
        "base": 7,
        "kept": 2
      },
      {
        "year": 2022,
        "tenor": 30,
        "reopening": "No",
        "base": 4,
        "kept": 2
      },
      {
        "year": 2022,
        "tenor": 30,
        "reopening": "Yes",
        "base": 8,
        "kept": 1
      }
    ],
    "kept_net": -2269.5,
    "kept_dd": 10553.5,
    "random_net_mean": -3789.02,
    "p_random_net_ge_kept": 0.373,
    "p_kept_better_net_and_dd": 0.319
  }
}
```

The frozen basic gate required >=100 trades, positive net, trade t>=2, daily NW5>=1.5, PF>=1.20, at least four
positive years, positive native-MNQ net and positive four-tick stress net. Filter gates additionally required
removed mean<0, kept total>=base total, p(random net>=kept)<=0.10, and better profit/DD than at least 90% of
both uniform and stratified subsets. No candidate passed the basic or complete gate. The primary's positive
short-side total is not a whole-strategy pass and is not nominated as a new rule.

```json
{
  "prereg": "3db3857",
  "gates": {
    "ADC15": {
      "count": true,
      "net": false,
      "t": false,
      "nw5": false,
      "pf": false,
      "years": false,
      "micro": false,
      "stress": false,
      "removed_loses": true,
      "kept_total_ge_base": true,
      "uniform_net": false,
      "uniform_joint": false,
      "stratified_net": false,
      "stratified_joint": false
    },
    "ADC5": {
      "count": true,
      "net": false,
      "t": false,
      "nw5": false,
      "pf": false,
      "years": false,
      "micro": false,
      "stress": false,
      "removed_loses": false,
      "kept_total_ge_base": false,
      "uniform_net": false,
      "uniform_joint": false,
      "stratified_net": false,
      "stratified_joint": false
    },
    "ADC15_D05": {
      "count": false,
      "net": false,
      "t": false,
      "nw5": false,
      "pf": false,
      "years": false,
      "micro": false,
      "stress": false,
      "removed_loses": true,
      "kept_total_ge_base": true,
      "uniform_net": false,
      "uniform_joint": false,
      "stratified_net": false,
      "stratified_joint": false
    }
  },
  "passing": [],
  "selected": null,
  "counted_program_evaluations": 55,
  "unique_program_models": 54,
  "exact_actual_subset_controls": true,
  "program_continues": true
}
```

## Data, clocks and limits

```json
{
  "auction_source": {
    "rows": 525,
    "exact_duplicates": 0,
    "conflicting_keys": 0,
    "source_fields": [
      "auction_date",
      "cusip",
      "security_type",
      "security_term",
      "closing_time_comp",
      "reopening",
      "inflation_index_security",
      "floating_rate",
      "bid_to_cover_ratio"
    ],
    "high_yield_used": false,
    "clock": "13:00ET deadline=12:00CT; actual result receipt/vintage unverified",
    "structural_exclusions": 152,
    "unsupported_tenor_rows": 0,
    "invalid_BTC_history_slots": 0,
    "eligible_events": 373,
    "eligible_dates": 373,
    "multiple_event_dates": 0,
    "first": "2017-12-11",
    "last": "2022-12-29",
    "by_tenor": {
      "2": 46,
      "3": 52,
      "5": 60,
      "7": 60,
      "10": 61,
      "20": 33,
      "30": 61
    }
  },
  "price_sources": {
    "NQ": {
      "symbol": "NQ",
      "rows": 1769357,
      "exact_duplicates": 0,
      "conflicting_keys": 0,
      "first": 20171201,
      "last": 20221230,
      "clock": "native CT minute close labels"
    },
    "ZN": {
      "symbol": "ZN",
      "rows": 1681117,
      "exact_duplicates": 0,
      "conflicting_keys": 0,
      "first": 20171201,
      "last": 20221230,
      "clock": "native CT minute close labels"
    }
  },
  "event_and_execution_counts": {
    "ADC15": {
      "input": {
        "signal": 199,
        "demand_confirmation_or_size_gate": 91,
        "invalid_result_or_prior_reference": 42,
        "zero_ZN_reaction": 30,
        "incomplete_known_price_window": 6
      },
      "execution": {
        "suppressed_invested_or_same_close": 0,
        "suppressed_daily_cap": 0,
        "missing_scheduled_entry": 0
      },
      "signals": 199,
      "executed": 199
    },
    "ADC5": {
      "input": {
        "signal": 204,
        "demand_confirmation_or_size_gate": 84,
        "invalid_result_or_prior_reference": 42,
        "zero_ZN_reaction": 35,
        "incomplete_known_price_window": 3
      },
      "execution": {
        "suppressed_invested_or_same_close": 0,
        "suppressed_daily_cap": 0,
        "missing_scheduled_entry": 0
      },
      "signals": 204,
      "executed": 204
    },
    "ADC15_D05": {
      "input": {
        "demand_confirmation_or_size_gate": 208,
        "signal": 82,
        "invalid_result_or_prior_reference": 42,
        "zero_ZN_reaction": 30,
        "incomplete_known_price_window": 6
      },
      "execution": {
        "suppressed_invested_or_same_close": 0,
        "suppressed_daily_cap": 0,
        "missing_scheduled_entry": 0
      },
      "signals": 82,
      "executed": 82
    },
    "ZN15": {
      "input": {
        "signal": 290,
        "invalid_result_or_prior_reference": 42,
        "zero_ZN_reaction": 30,
        "incomplete_known_price_window": 6
      },
      "execution": {
        "suppressed_invested_or_same_close": 0,
        "suppressed_daily_cap": 0,
        "missing_scheduled_entry": 0
      },
      "signals": 290,
      "executed": 290
    },
    "ZN5": {
      "input": {
        "signal": 288,
        "invalid_result_or_prior_reference": 42,
        "zero_ZN_reaction": 35,
        "incomplete_known_price_window": 3
      },
      "execution": {
        "suppressed_invested_or_same_close": 0,
        "suppressed_daily_cap": 0,
        "missing_scheduled_entry": 0
      },
      "signals": 288,
      "executed": 288
    }
  }
}
```

Auction intake includes five December 2017 reference-only events: 373 eligible source events in total,
368 in design, 326 with valid prior references before price checks. Reference-ready counts for 2018–22
are 40/62/68/78/78. No conflicting or exact duplicate source keys occurred. Six primary/three 5-minute
events failed the known-price window; no scheduled entries were missing. No held-minute gaps occurred
in any saved ledger (0 held-gap tickets). Input hashes, eligible features, event exclusions,
synthetic checks, and every failed candidate/control ledger are retained.
The completion review found that initial intake stored only aggregate structural exclusions. The report
script now archives all 152 excluded source rows with their frozen-rule reasons in
design_auction_source_exclusions.csv, checking the source hash and original exclusion count. Signals,
returns, selection and the original input binding were not changed.

Synthetic checks cover tenor/reopening references, current/future result invariance, missing history slots,
duplicate conflicts, summer/winter ET-to-CT conversion, matching candidate/control directions, extra delay,
shared calendar, entry-bar stops, worse stop gaps and target-through. Pre-return reviewers inspected intake
and code only; that is not a fresh raw-spec independent performance check.

Treasury's public policy says results become available after auction conclusion and its results page updates
in real time as results are available. It does not verify this CSV's historical publication, receipt or revision
timestamps. Availability by 12:15/12:05 CT remains an assumption. Source continuity/roll-switch timing and
original-contract parity are not independently established. Bid-to-cover is confounded by offering size,
tenor, reopening and bidding behavior. No favorable inference removes those limits.

No 2023+ validation, post-pass random-side/time placebos, expensive resampling/Monte Carlo, independent
promotion, account comparisons or PowerLanguage followed the failed gate. There is no account pass/payout
claim. Do not flip directions, promote the short side or controls, or tune this family after rejection.
Continue a distinct mechanism. This failure creates no milestone alert and does not pause research.
Actual raw-data execution: 2026-10-26T04:31:48.751202+00:00 to 2026-10-26T04:32:03.576830+00:00.
Claude review path: agents/codex/results/auction_demand_confirmation.md.
