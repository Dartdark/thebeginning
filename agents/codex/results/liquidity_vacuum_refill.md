# NQ Liquidity Vacuum Refill: REJECT; research continues

Summary: All three frozen candidates failed2018-22. Primary5min:15trades,net$2,451.25/NQ,t0.866,NW5 1.035.
The stricter5min version had6trades and15min2trades. No meaningful power; volume removes profitable signals.
No2023+validation/accounts. Continue a distinct mechanism rather than loosen this one after seeingreturns.

Plan: agents/codex/plans/liquidity_vacuum_refill.md,846c9bc.
Script: analysis/codex_liquidity_vacuum_refill.py. Outputs: analysis/outputs/codex_liquidity_vacuum_refill/.
Trials5; program30counted evaluations/29unique economic rules,plus unknown earlier repo/author searches.
Independent per-signal controls below add non-executable return paths, not selectable strategy candidates.

## Trade as tested

A completed5/15min directional jump>=2or3times prior20same-clock range median, volume<=prior20same-clock
median, body>=70%, close near extreme. Nextbar retraces>=halfjump without extending beyond its extreme
by>0.25point. Fade atnextnativeopen01:00--06:30CT. No static level sweep or existing strategy signal.
Complete preceding30minutes+A+B,normalcash days,noJuly3/Dec24. Stop0.08priorATR,target0.12,time30min,
flat07:25,max4/day,no stale/sameclose entry. NQ$7.25RT+1tick/market-stop,MNQ$1.24RT+$0.50/fill.
Target1pointthrough,entrybarprotection,worsestopgaps;4tickstress. Nightspread/realreceipt assumptions remain.

## Design results

Dollars/NQ except net_mnq rows nativeMNQ; standardcashdayzeros/initialzeroDD,all/side/year metrics.

| model | period | side | trades | win | avg | total | t_trade | t_nw5 | t_nw20 | sharpe | sortino | profit_factor | calmar | ulcer | max_dd | cost | missing_held_minutes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LV5_R2 | 2018-22 | all | 15 | 0.53333 | 163.42 | 2451.2 | 0.86557 | 1.0352 | 1.0182 | 0.39822 | 0.72798 | 1.746 | 0.33733 | 0.63941 | 1454.5 | 233.75 | 0 |
| LV5_R2 | 2018 | all | 4 | 0.25 | -103.5 | -414 | -1.1397 | -0.90308 | -0.95741 | -1.102 | -1.1652 | 0.22869 | -0.77438 | 1.0048 | 536.75 | 69 | 0 |
| LV5_R2 | 2019 | all | 1 | 1 | 162.75 | 162.75 | nan | 1.0122 | 1.0458 | 1 | nan | inf | nan | 0 | 0 | 17.25 | 0 |
| LV5_R2 | 2020 | all | 8 | 0.625 | 358.38 | 2867 | 1.0624 | 1.2608 | 1.2899 | 1.053 | 1.9672 | 2.2593 | 1.9633 | 0.25383 | 1454.5 | 113 | 0 |
| LV5_R2 | 2021 | all | 2 | 0.5 | -82.25 | -164.5 | -0.2109 | -1.0122 | -1.0456 | -1 | -1 | 0.65167 | -1 | 0.092685 | 164.5 | 34.5 | 0 |
| LV5_R2 | 2022 | all | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV5_R2 | 2018-22 | long | 9 | 0.55556 | 55.528 | 499.75 | 0.24108 | 0.47051 | 0.58316 | 0.10404 | 0.14938 | 1.2232 | 0.068772 | 0.59851 | 1454.5 | 145.25 | 0 |
| LV5_R2 | 2018 | long | 2 | 0.5 | -94.75 | -189.5 | -0.43563 | -0.56699 | -0.73945 | -0.56516 | -0.60809 | 0.39311 | -0.6093 | 0.58588 | 312.25 | 34.5 | 0 |
| LV5_R2 | 2019 | long | 1 | 1 | 162.75 | 162.75 | nan | 1.0122 | 1.0458 | 1 | nan | inf | nan | 0 | 0 | 17.25 | 0 |
| LV5_R2 | 2020 | long | 4 | 0.5 | 172.75 | 691 | 0.33087 | 0.70827 | 0.91084 | 0.3264 | 0.47414 | 1.4751 | 0.4732 | 0.51691 | 1454.5 | 59 | 0 |
| LV5_R2 | 2021 | long | 2 | 0.5 | -82.25 | -164.5 | -0.2109 | -1.0122 | -1.0456 | -1 | -1 | 0.65167 | -1 | 0.092685 | 164.5 | 34.5 | 0 |
| LV5_R2 | 2022 | long | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV5_R2 | 2018-22 | short | 6 | 0.5 | 325.25 | 1951.5 | 0.96562 | 1.1904 | 1.1492 | 0.60723 | 5.105 | 2.8643 | 1.7399 | 0.28951 | 224.5 | 88.5 | 0 |
| LV5_R2 | 2018 | short | 2 | 0 | -112.25 | -224.5 | -2.4944 | -1.3408 | -1.1366 | -1.3172 | -1.3153 | 0 | -1.004 | 0.42077 | 224.5 | 34.5 | 0 |
| LV5_R2 | 2019 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV5_R2 | 2020 | short | 4 | 0.75 | 544 | 2176 | 1.1211 | 1.3591 | 1.3761 | 1.5247 | nan | 3.6464 | nan | 0 | 0 | 54 | 0 |
| LV5_R2 | 2021 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV5_R2 | 2022 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV5_R2 | 2018-22 | net_mnq | 15 | 0.53333 | 15.827 | 237.4 | 0.8383 | 1.0114 | 0.99752 | 0.3867 | 0.69903 | 1.7147 | 0.3244 | 0.06657 | 146.48 | 31.1 | 0 |
| LV5_R2 | 2018-22 | stress_four_ticks | 15 | 0.53333 | 138.42 | 2076.2 | 0.72685 | 0.90418 | 0.90021 | 0.3383 | 0.58681 | 1.5939 | 0.2744 | 0.77532 | 1514.5 | 608.75 | 0 |
| LV5_R3 | 2018-22 | all | 6 | 0.66667 | 511.08 | 3066.5 | 1.2488 | 1.1804 | 1.0518 | 0.58398 | 1.8865 | 2.979 | 0.84398 | 0.056893 | 727.25 | 83.5 | 0 |
| LV5_R3 | 2018 | all | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV5_R3 | 2019 | all | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV5_R3 | 2020 | all | 6 | 0.66667 | 511.08 | 3066.5 | 1.2488 | 1.1964 | 1.0941 | 1.3042 | 4.2082 | 2.979 | 4.1999 | 0.12692 | 727.25 | 83.5 | 0 |
| LV5_R3 | 2021 | all | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV5_R3 | 2022 | all | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV5_R3 | 2018-22 | long | 3 | 0.66667 | 472.75 | 1418.2 | 0.78228 | 1.0951 | 1.033 | 0.37504 | 0.87248 | 2.9502 | 0.39034 | 0.056893 | 727.25 | 41.75 | 0 |
| LV5_R3 | 2018 | long | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV5_R3 | 2019 | long | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV5_R3 | 2020 | long | 3 | 0.66667 | 472.75 | 1418.2 | 0.78228 | 1.1079 | 1.073 | 0.83622 | 1.9463 | 2.9502 | 1.9424 | 0.12692 | 727.25 | 41.75 | 0 |
| LV5_R3 | 2021 | long | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV5_R3 | 2022 | long | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV5_R3 | 2018-22 | short | 3 | 0.66667 | 549.42 | 1648.2 | 0.80069 | 1.0672 | 1.0261 | 0.55582 | nan | 3.0046 | nan | 0 | 0 | 41.75 | 0 |
| LV5_R3 | 2018 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV5_R3 | 2019 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV5_R3 | 2020 | short | 3 | 0.66667 | 549.42 | 1648.2 | 0.80069 | 1.0791 | 1.0653 | 1.241 | nan | 3.0046 | nan | 0 | 0 | 41.75 | 0 |
| LV5_R3 | 2021 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV5_R3 | 2022 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV5_R3 | 2018-22 | net_mnq | 6 | 0.66667 | 50.593 | 303.56 | 1.2362 | 1.1795 | 1.0516 | 0.58145 | 1.8543 | 2.9461 | 0.8296 | 0.0058272 | 73.24 | 11.44 | 0 |
| LV5_R3 | 2018-22 | stress_four_ticks | 6 | 0.66667 | 491.08 | 2946.5 | 1.1908 | 1.1763 | 1.051 | 0.57192 | 1.7408 | 2.8307 | 0.77883 | 0.059258 | 757.25 | 203.5 | 0 |
| LV15_R2 | 2018-22 | all | 2 | 0 | -884.75 | -1769.5 | -14.156 | -1.4174 | -1.1225 | -0.63138 | -0.63113 | 0 | -0.20016 | 2.6365 | 1769.5 | 34.5 | 0 |
| LV15_R2 | 2018 | all | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV15_R2 | 2019 | all | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV15_R2 | 2020 | all | 2 | 0 | -884.75 | -1769.5 | -14.156 | -1.4455 | -1.1743 | -1.4107 | -1.4079 | 0 | -0.99605 | 3.1128 | 1769.5 | 34.5 | 0 |
| LV15_R2 | 2021 | all | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV15_R2 | 2022 | all | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV15_R2 | 2018-22 | long | 2 | 0 | -884.75 | -1769.5 | -14.156 | -1.4174 | -1.1225 | -0.63138 | -0.63113 | 0 | -0.20016 | 2.6365 | 1769.5 | 34.5 | 0 |
| LV15_R2 | 2018 | long | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV15_R2 | 2019 | long | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV15_R2 | 2020 | long | 2 | 0 | -884.75 | -1769.5 | -14.156 | -1.4455 | -1.1743 | -1.4107 | -1.4079 | 0 | -0.99605 | 3.1128 | 1769.5 | 34.5 | 0 |
| LV15_R2 | 2021 | long | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV15_R2 | 2022 | long | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV15_R2 | 2018-22 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV15_R2 | 2018 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV15_R2 | 2019 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV15_R2 | 2020 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV15_R2 | 2021 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV15_R2 | 2022 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| LV15_R2 | 2018-22 | net_mnq | 2 | 0 | -88.99 | -177.98 | -14.238 | -1.4175 | -1.1225 | -0.6314 | -0.63115 | 0 | -0.20016 | 0.26518 | 177.98 | 4.48 | 0 |
| LV15_R2 | 2018-22 | stress_four_ticks | 2 | 0 | -914.75 | -1829.5 | -14.636 | -1.4177 | -1.1225 | -0.63148 | -0.63123 | 0 | -0.20016 | 2.7259 | 1829.5 | 94.5 | 0 |
| PRICE5 | 2018-22 | all | 281 | 0.55516 | 29.013 | 8152.8 | 1.2044 | 1.4033 | 1.3953 | 0.5794 | 0.87559 | 1.2041 | 0.57283 | 2.6296 | 2848.8 | 4517.2 | 0 |
| PRICE5 | 2018 | all | 71 | 0.47887 | -11.968 | -849.75 | -0.48793 | -0.42569 | -0.45982 | -0.46562 | -0.61788 | 0.87209 | -0.3804 | 3.1917 | 2242.8 | 1149.8 | 0 |
| PRICE5 | 2019 | all | 46 | 0.71739 | 71.337 | 3281.5 | 2.8153 | 3.3551 | 3.0298 | 2.8464 | 6.607 | 3.0845 | 10.993 | 0.16354 | 298.5 | 753.5 | 0 |
| PRICE5 | 2020 | all | 66 | 0.54545 | 74.644 | 4926.5 | 1.2284 | 1.4137 | 1.2496 | 1.2855 | 2.1948 | 1.4588 | 2.4786 | 1.3949 | 1979.8 | 1028.5 | 0 |
| PRICE5 | 2021 | all | 50 | 0.5 | -14.45 | -722.5 | -0.25323 | -0.30213 | -0.36894 | -0.29203 | -0.39038 | 0.92182 | -0.30205 | 2.945 | 2392 | 797.5 | 0 |
| PRICE5 | 2022 | all | 48 | 0.58333 | 31.604 | 1517 | 0.36318 | 0.47151 | 0.5273 | 0.4029 | 0.58446 | 1.1291 | 0.5439 | 3.3566 | 2800.2 | 788 | 0 |
| PRICE5 | 2018-22 | long | 143 | 0.54545 | 11.596 | 1658.2 | 0.32511 | 0.36355 | 0.38305 | 0.15523 | 0.22269 | 1.0713 | 0.10777 | 2.8174 | 3079.8 | 2311.8 | 0 |
| PRICE5 | 2018 | long | 33 | 0.54545 | -26.189 | -864.25 | -0.75337 | -0.58068 | -0.63194 | -0.67987 | -0.79716 | 0.74115 | -0.58509 | 1.8646 | 1483 | 534.25 | 0 |
| PRICE5 | 2019 | long | 19 | 0.63158 | 27.75 | 527.25 | 0.64753 | 0.88842 | 1.3573 | 0.76328 | 1.2496 | 1.5018 | 1.9366 | 0.27214 | 272.25 | 312.75 | 0 |
| PRICE5 | 2020 | long | 37 | 0.54054 | 52.48 | 1941.8 | 0.67555 | 0.79498 | 0.76209 | 0.6609 | 0.99159 | 1.3169 | 1.1251 | 1.6621 | 1719 | 588.25 | 0 |
| PRICE5 | 2021 | long | 27 | 0.48148 | -5.5833 | -150.75 | -0.069368 | -0.087902 | -0.10687 | -0.082449 | -0.11499 | 0.96905 | -0.10669 | 1.6026 | 1413 | 430.75 | 0 |
| PRICE5 | 2022 | long | 27 | 0.55556 | 7.5648 | 204.25 | 0.059833 | 0.067231 | 0.072018 | 0.068765 | 0.099836 | 1.026 | 0.066585 | 4.1606 | 3079.8 | 445.75 | 0 |
| PRICE5 | 2018-22 | short | 138 | 0.56522 | 47.062 | 6494.5 | 1.4567 | 1.6622 | 1.6736 | 0.69856 | 1.1949 | 1.389 | 0.50453 | 1.6735 | 2576.5 | 2205.5 | 0 |
| PRICE5 | 2018 | short | 38 | 0.42105 | 0.38158 | 14.5 | 0.010968 | 0.01273 | 0.012457 | 0.011895 | 0.018276 | 1.0044 | 0.012076 | 1.5498 | 1205.5 | 615.5 | 0 |
| PRICE5 | 2019 | short | 27 | 0.77778 | 102.01 | 2754.2 | 3.3799 | 3.2631 | 2.7728 | 2.999 | 9.6116 | 6.2612 | 10.306 | 0.07873 | 267.25 | 440.75 | 0 |
| PRICE5 | 2020 | short | 29 | 0.55172 | 102.92 | 2984.8 | 1.0527 | 1.4087 | 1.4047 | 1.2457 | 2.6135 | 1.6476 | 3.5319 | 0.59181 | 841.75 | 440.25 | 0 |
| PRICE5 | 2021 | short | 23 | 0.52174 | -24.859 | -571.75 | -0.30215 | -0.31117 | -0.41453 | -0.313 | -0.43706 | 0.86916 | -0.35512 | 1.9429 | 1610 | 366.75 | 0 |
| PRICE5 | 2022 | short | 21 | 0.61905 | 62.512 | 1312.8 | 0.53075 | 0.57826 | 0.56857 | 0.54038 | 0.88919 | 1.3376 | 0.85946 | 1.35 | 1533.5 | 342.25 | 0 |
| PRICE5 | 2018-22 | net_mnq | 281 | 0.54448 | 2.3863 | 670.56 | 0.99064 | 1.1557 | 1.1526 | 0.4769 | 0.71083 | 1.1652 | 0.40209 | 0.33603 | 333.8 | 596.44 | 0 |
| PRICE5 | 2018-22 | stress_four_ticks | 281 | 0.48754 | 2.5365 | 712.75 | 0.1042 | 0.12129 | 0.12191 | 0.050158 | 0.071018 | 1.0162 | 0.026323 | 5.4727 | 5419.8 | 11957 | 0 |
| PRICE15 | 2018-22 | all | 82 | 0.5122 | 44.335 | 3635.5 | 0.9318 | 1.0195 | 1.0052 | 0.40517 | 0.63148 | 1.3123 | 0.19734 | 2.7341 | 3687.5 | 1324.5 | 0 |
| PRICE15 | 2018 | all | 17 | 0.52941 | 20.397 | 346.75 | 0.4951 | 0.4569 | 0.4005 | 0.52394 | 0.83612 | 1.3293 | 0.52867 | 0.76992 | 658.5 | 293.25 | 0 |
| PRICE15 | 2019 | all | 13 | 0.46154 | -6.0962 | -79.25 | -0.13558 | -0.17532 | -0.23754 | -0.14151 | -0.19612 | 0.91439 | -0.21347 | 0.45494 | 371.25 | 219.25 | 0 |
| PRICE15 | 2020 | all | 20 | 0.35 | -109.75 | -2195 | -1.0145 | -1.1957 | -1.1944 | -0.95932 | -1.1619 | 0.58025 | -0.5929 | 5.1976 | 3687.5 | 315 | 0 |
| PRICE15 | 2021 | all | 17 | 0.82353 | 254.51 | 4326.8 | 3.4401 | 2.8306 | 3.6137 | 2.7225 | 10.062 | 7.7421 | 13.427 | 0.082177 | 322.25 | 258.25 | 0 |
| PRICE15 | 2022 | all | 15 | 0.4 | 82.417 | 1236.2 | 0.45035 | 0.5174 | 0.52373 | 0.44984 | 0.77445 | 1.3262 | 0.57891 | 1.9299 | 2144 | 238.75 | 0 |
| PRICE15 | 2018-22 | long | 50 | 0.42 | -5.65 | -282.5 | -0.082319 | -0.096507 | -0.092974 | -0.037186 | -0.057767 | 0.96959 | -0.014899 | 3.2969 | 3795.2 | 812.5 | 0 |
| PRICE15 | 2018 | long | 12 | 0.33333 | -41.417 | -497 | -0.94585 | -0.76855 | -0.67193 | -0.95174 | -1.1354 | 0.52802 | -0.54954 | 1.3625 | 908 | 207 | 0 |
| PRICE15 | 2019 | long | 4 | 0.25 | -48.5 | -194 | -0.55612 | -0.92948 | -1.3334 | -0.61065 | -0.70467 | 0.44847 | -0.58877 | 0.38237 | 329.5 | 69 | 0 |
| PRICE15 | 2020 | long | 13 | 0.23077 | -238.79 | -3104.2 | -1.7357 | -1.9604 | -2.1742 | -1.6171 | -1.866 | 0.3211 | -0.83347 | 4.9766 | 3709.8 | 209.25 | 0 |
| PRICE15 | 2021 | long | 10 | 0.8 | 203.75 | 2037.5 | 1.7712 | 1.8468 | 1.9861 | 1.6128 | 4.7563 | 4.3706 | 6.3227 | 0.11559 | 322.25 | 152.5 | 0 |
| PRICE15 | 2022 | long | 11 | 0.45455 | 134.11 | 1475.2 | 0.59067 | 0.73727 | 0.71756 | 0.60941 | 1.1764 | 1.5447 | 0.98299 | 1.4416 | 1506.8 | 174.75 | 0 |
| PRICE15 | 2018-22 | short | 32 | 0.65625 | 122.44 | 3918 | 2.1642 | 2.0105 | 2.0536 | 0.91806 | 1.8284 | 2.6674 | 0.72496 | 0.63611 | 1081.8 | 512 | 0 |
| PRICE15 | 2018 | short | 5 | 1 | 168.75 | 843.75 | 3.2883 | 1.9694 | 2.0954 | 1.9245 | nan | inf | nan | 0 | 0 | 86.25 | 0 |
| PRICE15 | 2019 | short | 9 | 0.55556 | 12.75 | 114.75 | 0.234 | 0.31245 | 0.36286 | 0.24689 | 0.38685 | 1.1999 | 0.3288 | 0.30291 | 349 | 150.25 | 0 |
| PRICE15 | 2020 | short | 7 | 0.57143 | 129.89 | 909.25 | 0.89931 | 0.92077 | 0.97511 | 0.90975 | 1.7347 | 2.3845 | 1.768 | 0.73703 | 512.25 | 105.75 | 0 |
| PRICE15 | 2021 | short | 7 | 0.85714 | 327.04 | 2289.2 | 4.3691 | 2.1353 | 2.3685 | 2.3279 | 61.456 | 62.456 | 61.456 | 0.034021 | 37.25 | 105.75 | 0 |
| PRICE15 | 2022 | short | 4 | 0.25 | -59.75 | -239 | -0.18498 | -0.2125 | -0.21273 | -0.2124 | -0.32114 | 0.77906 | -0.22182 | 1.2867 | 1081.8 | 64 | 0 |
| PRICE15 | 2018-22 | net_mnq | 82 | 0.5122 | 3.9185 | 321.32 | 0.82356 | 0.90145 | 0.88816 | 0.35824 | 0.5523 | 1.2712 | 0.17201 | 0.28771 | 373.9 | 174.68 | 0 |
| PRICE15 | 2018-22 | stress_four_ticks | 82 | 0.5 | 17.628 | 1445.5 | 0.36685 | 0.40146 | 0.39495 | 0.15962 | 0.23632 | 1.1126 | 0.072833 | 3.2195 | 3972.5 | 3514.5 | 0 |

## Matched filter diagnostics

Actual capped candidates/control ledgers need not nest. Below are explicitly NON-EXECUTABLE overlapping
independent entries that isolate the volume gate. They cannot establish a causal executable portfolio benefit.

```json
{
  "LV5_R2": {
    "non_executable_signal_only": true,
    "base_trades": 293,
    "kept_trades": 15,
    "removed_trades": 278,
    "base_net": 7750.75,
    "kept_net": 2451.25,
    "removed_net": 5299.5,
    "removed_avg": 19.06294964028777,
    "removed_t": 0.8346511647707563,
    "random_subsets": 1000,
    "random_net_mean": 414.71,
    "p_random_net_ge_kept": 0.092,
    "p_kept_better_net_and_dd": 0.332
  },
  "LV5_R3": {
    "non_executable_signal_only": true,
    "base_trades": 293,
    "kept_trades": 6,
    "removed_trades": 287,
    "base_net": 7750.75,
    "kept_net": 3066.5,
    "removed_net": 4684.25,
    "removed_avg": 16.321428571428573,
    "removed_t": 0.7259792557670108,
    "random_subsets": 1000,
    "random_net_mean": 163.675,
    "p_random_net_ge_kept": 0.0,
    "p_kept_better_net_and_dd": 0.412
  },
  "LV15_R2": {
    "non_executable_signal_only": true,
    "base_trades": 82,
    "kept_trades": 2,
    "removed_trades": 80,
    "base_net": 3635.5,
    "kept_net": -1769.5,
    "removed_net": 5405.0,
    "removed_avg": 67.5625,
    "removed_t": 1.4750365089861999,
    "random_subsets": 1000,
    "random_net_mean": 98.865,
    "p_random_net_ge_kept": 1.0,
    "p_kept_better_net_and_dd": 0.0
  }
}
```

No candidatepasses basiccounts/t or fullfiltercriteria; no carried2023+returntest,MC/bootstrap,accountbench,
independentpromotion orPowerLanguage. Sourceaudit/engineeringchecks/inputbinding/completegate retained.
Unknown priors, unobserved actor, thinliquidity/news and execution costs further weaken inference.
Next: distinct cash-closing-auction curvature mechanism, separately preregistered before returns.
Claudehandoff: agents/codex/results/liquidity_vacuum_refill.md.
