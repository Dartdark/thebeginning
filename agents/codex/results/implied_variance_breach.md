# NQ Implied Variance Budget Breach: REJECT; research continues

Summary: All three frozen candidates lost after costs in2018-22. Primary5min:223trades,
net$-24,896.75/NQ,trade t-1.365,dailyNW5 t-1.480; no candidate passed.
The variance-surprise gate removes profitable signals and fails conditional random timing. No2023+returns tested.
Program45counted evaluations/44unique rules retained; no t4.5/t5/t6 milestone. Continue a distinct mechanism.

Plan: agents/codex/plans/implied_variance_breach.md, prereg ea36af6.
Scripts: analysis/codex_implied_variance_breach.py and analysis/codex_implied_variance_breach_report.py.
Outputs: analysis/outputs/codex_implied_variance_breach/.
Five models:3candidates+2unselectable price controls. Prior40counted evaluations/39unique; plus unknown much
larger older repository/author searches. Overlapping-window returns and random paths below are additional
NON-SELECTABLE diagnostic return paths, not extra selected strategies or executable capitalized portfolios.

## Rule as tested

At completed5/15min closes09:00--13:30CT, compare cumulative squared one-minute log returns since08:31open
with a lagged option-implied variance budget. Prior cash-market day's EXACT VXNclose, converted to daily
variance by(VXN/100)^2/252, is multiplied by a prior60normal-date median realized/implied cash-variance
calibration and prior20normal-date median intraday variance share. At least60past dates,45valid scale and
15valid shape observations. Missing past dates keep their chronological window positions. Today's final
variance/completeness enters history only after today's decisions. No current/future VXN or full-day mask.

Long if cumulative move>=0.20prior15weekdayATR and close>runningcashVWAP; short mirrored. Require variance
ratio>=2(primary5min/15min)or3(one5minvariant). Price controls omit the ratio gate but retain its input/history
eligibility. Take FIRST qualifying window/date only, even if its scheduled open is missing; no later retry.
Entry at j+2nativeopen(oneextra whole minute), stop0.15ATR,target0.45ATR,ceilto0.25,activeentrybar,flat14:55.
One position/trade/day; noBE/trail/overnight/old trade list or return rescaling. Normalcash dates, noJuly3/Dec24.
NQ$7.25RT plus1tick($5)/market-stopfill; MNQ$1.24RT+$0.50/fill independently. Target needs1pointthrough;
worse-open stopgaps and fixed4tickfill stress. Sharedgrid._walk via first-signal adapter; no shared engine edits.

VXN's30-day expected-volatility interpretation is a source fact; a directional continuation edge is our unproven
hypothesis. Source:[Cboe methodology](https://cdn.cboe.com/api/global/us_indices/governance/Volatility_Index_Methodology_Selected_Broad_Based_Index_Equity_and_ETF_Volatility_Indices.pdf).
The252-day projection and causal cash-session calibration are model conventions, not a Cboe daily forecast.

## Design results

2018-22 only. Dollars/NQ except net_mnq rows in nativeMNQ. Cash-market-day zeros, initialzeroDD, all/side/year
standard shared metrics and NW5/NW20. Native gross/cost units are consistent. No2023+oraccountclaim.

| model | period | side | trades | win | avg | total | t_trade | t_nw5 | t_nw20 | sharpe | sortino | profit_factor | calmar | ulcer | max_dd | cost | missing_held_minutes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IVB5_2 | 2018-22 | all | 223 | 0.25112 | -111.64 | -24897 | -1.3652 | -1.4798 | -1.5243 | -0.60982 | -1.0634 | 0.79323 | -0.16686 | 32.06 | 29865 | 3641.8 | 0 |
| IVB5_2 | 2018 | all | 40 | 0.25 | -96.75 | -3870 | -0.89634 | -1.0887 | -1.2384 | -0.89999 | -1.5148 | 0.71028 | -0.84041 | 2.8656 | 4623.2 | 655 | 0 |
| IVB5_2 | 2019 | all | 38 | 0.18421 | -155.8 | -5920.5 | -2.0855 | -2.431 | -2.841 | -2.0113 | -2.8781 | 0.46924 | -1 | 6.6895 | 5920.5 | 630.5 | 0 |
| IVB5_2 | 2020 | all | 52 | 0.26923 | -74.462 | -3872 | -0.3602 | -0.43491 | -0.47094 | -0.36191 | -0.65248 | 0.88371 | -0.38565 | 9.7787 | 10000 | 837 | 0 |
| IVB5_2 | 2021 | all | 61 | 0.2623 | -143.07 | -8727.2 | -0.97103 | -1.0237 | -0.86333 | -0.97137 | -1.6253 | 0.74876 | -0.5422 | 23.448 | 16096 | 997.25 | 0 |
| IVB5_2 | 2022 | all | 32 | 0.28125 | -78.344 | -2507 | -0.23315 | -0.23734 | -0.28048 | -0.2367 | -0.42442 | 0.91002 | -0.27253 | 10.001 | 9235.5 | 522 | 0 |
| IVB5_2 | 2018-22 | long | 78 | 0.25641 | -125.9 | -9820.5 | -0.84412 | -0.86357 | -0.87583 | -0.37831 | -0.65786 | 0.78393 | -0.13314 | 14.125 | 14764 | 1285.5 | 0 |
| IVB5_2 | 2018 | long | 14 | 0.28571 | -52.964 | -741.5 | -0.23488 | -0.29158 | -0.30419 | -0.24326 | -0.44574 | 0.8528 | -0.25315 | 1.6027 | 2940.8 | 231.5 | 0 |
| IVB5_2 | 2019 | long | 13 | 0.15385 | -185.71 | -2414.2 | -1.3299 | -1.3462 | -1.4684 | -1.294 | -1.8231 | 0.43324 | -0.75281 | 2.9935 | 3207 | 214.25 | 0 |
| IVB5_2 | 2020 | long | 17 | 0.23529 | -78.721 | -1338.2 | -0.1991 | -0.21223 | -0.25784 | -0.20419 | -0.38172 | 0.88167 | -0.26479 | 4.5272 | 5034 | 283.25 | 0 |
| IVB5_2 | 2021 | long | 18 | 0.27778 | -295.58 | -5320.5 | -1.1789 | -1.2624 | -1.0767 | -1.1672 | -1.642 | 0.5264 | -0.77862 | 8.3644 | 6833.2 | 295.5 | 0 |
| IVB5_2 | 2022 | long | 16 | 0.3125 | -0.375 | -6 | -0.00075868 | -0.00076457 | -0.00074073 | -0.00078356 | -0.0014442 | 0.99956 | -0.00084236 | 7.4275 | 7151.2 | 261 | 0 |
| IVB5_2 | 2018-22 | short | 145 | 0.24828 | -103.97 | -15076 | -1.0693 | -1.2011 | -1.2378 | -0.47817 | -0.83584 | 0.79886 | -0.16194 | 20.524 | 18634 | 2356.2 | 0 |
| IVB5_2 | 2018 | short | 26 | 0.23077 | -120.33 | -3128.5 | -1.0295 | -1.2367 | -1.4313 | -1.0305 | -1.6135 | 0.62398 | -0.93419 | 3.0346 | 3362.2 | 423.5 | 0 |
| IVB5_2 | 2019 | short | 25 | 0.2 | -140.25 | -3506.2 | -1.5701 | -1.8519 | -1.9837 | -1.5301 | -2.2274 | 0.49148 | -0.84784 | 5.0965 | 4135.5 | 416.25 | 0 |
| IVB5_2 | 2020 | short | 35 | 0.28571 | -72.393 | -2533.8 | -0.29676 | -0.3608 | -0.38411 | -0.29957 | -0.52919 | 0.88476 | -0.30033 | 7.2898 | 8403.2 | 553.75 | 0 |
| IVB5_2 | 2021 | short | 43 | 0.25581 | -79.227 | -3406.8 | -0.43604 | -0.45201 | -0.38562 | -0.4395 | -0.79564 | 0.85504 | -0.29077 | 16.249 | 11716 | 701.75 | 0 |
| IVB5_2 | 2022 | short | 16 | 0.25 | -156.31 | -2501 | -0.33207 | -0.38896 | -0.54883 | -0.34178 | -0.59565 | 0.82452 | -0.44371 | 7.3974 | 5659 | 261 | 0 |
| IVB5_2 | 2018-22 | net_mnq | 223 | 0.25112 | -11.679 | -2604.5 | -1.4282 | -1.547 | -1.5906 | -0.63775 | -1.1062 | 0.78522 | -0.16848 | 3.3801 | 3094.2 | 479.02 | 0 |
| IVB5_2 | 2018-22 | stress_four_ticks | 223 | 0.25112 | -138.89 | -30972 | -1.6921 | -1.8264 | -1.8621 | -0.75444 | -1.2805 | 0.75305 | -0.17416 | 38.979 | 35595 | 9716.8 | 0 |
| IVB5_3 | 2018-22 | all | 88 | 0.19318 | -332.19 | -29233 | -2.9634 | -2.3851 | -2.1302 | -1.2744 | -1.7463 | 0.4809 | -0.17659 | 39.288 | 33134 | 1453 | 0 |
| IVB5_3 | 2018 | all | 10 | 0.1 | -398.75 | -3987.5 | -2.5938 | -1.7551 | -1.6519 | -2.0861 | -2.3798 | 0.19204 | -0.86973 | 3.0274 | 4603 | 167.5 | 0 |
| IVB5_3 | 2019 | all | 17 | 0.17647 | -115.78 | -1968.2 | -0.80293 | -0.88226 | -1.1928 | -0.81091 | -1.3922 | 0.6194 | -1 | 2.3501 | 1968.2 | 278.25 | 0 |
| IVB5_3 | 2020 | all | 27 | 0.14815 | -627.25 | -16936 | -3.49 | -2.0755 | -1.5791 | -2.9743 | -3.3214 | 0.23907 | -0.85783 | 27.492 | 19664 | 445.75 | 0 |
| IVB5_3 | 2021 | all | 23 | 0.26087 | -119.86 | -2756.8 | -0.47068 | -0.49512 | -0.69914 | -0.47812 | -0.80045 | 0.79897 | -0.401 | 7.6756 | 6874.8 | 381.75 | 0 |
| IVB5_3 | 2022 | all | 11 | 0.27273 | -325.89 | -3584.8 | -0.6379 | -0.57575 | -0.60041 | -0.65638 | -0.97713 | 0.64986 | -0.50753 | 9.2273 | 7091.2 | 179.75 | 0 |
| IVB5_3 | 2018-22 | long | 34 | 0.058824 | -678.87 | -23082 | -4.6476 | -3.2135 | -3.0306 | -1.649 | -1.9296 | 0.15798 | -0.19214 | 26.764 | 24045 | 581.5 | 0 |
| IVB5_3 | 2018 | long | 6 | 0 | -576.42 | -3458.5 | -12.952 | -2.2292 | -1.8494 | -2.4423 | -2.4186 | 0 | -1.004 | 2.1026 | 3458.5 | 103.5 | 0 |
| IVB5_3 | 2019 | long | 5 | 0 | -394.25 | -1971.2 | -8.5495 | -1.9538 | -1.9344 | -2.1937 | -2.1773 | 0 | -1 | 1.763 | 1971.2 | 86.25 | 0 |
| IVB5_3 | 2020 | long | 8 | 0 | -994.75 | -7958 | -6.3214 | -2.0753 | -1.7767 | -2.6345 | -2.604 | 0 | -0.99605 | 11.904 | 7958 | 138 | 0 |
| IVB5_3 | 2021 | long | 7 | 0 | -891.54 | -6240.8 | -9.1301 | -2.7827 | -2.6715 | -2.584 | -2.5554 | 0 | -1 | 6.5367 | 6240.8 | 120.75 | 0 |
| IVB5_3 | 2022 | long | 8 | 0.25 | -431.62 | -3453 | -0.72264 | -0.65408 | -0.67988 | -0.74606 | -1.0678 | 0.55637 | -0.74767 | 6.5444 | 4636.8 | 133 | 0 |
| IVB5_3 | 2018-22 | short | 54 | 0.27778 | -113.92 | -6151.5 | -0.75237 | -0.68065 | -0.63355 | -0.33791 | -0.52529 | 0.78717 | -0.084505 | 15.175 | 14570 | 871.5 | 0 |
| IVB5_3 | 2018 | short | 4 | 0.25 | -132.25 | -529 | -0.36286 | -0.35643 | -0.50983 | -0.41022 | -0.60571 | 0.64178 | -0.46405 | 1.0157 | 1144.5 | 64 | 0 |
| IVB5_3 | 2019 | short | 12 | 0.25 | 0.25 | 3 | 0.0012764 | 0.0014413 | 0.0014484 | 0.0013305 | 0.002763 | 1.0009 | 0.0017429 | 1.7525 | 1721.2 | 192 | 0 |
| IVB5_3 | 2020 | short | 19 | 0.21053 | -472.51 | -8977.8 | -1.9661 | -1.5987 | -1.278 | -1.8377 | -2.1996 | 0.37213 | -0.76387 | 16.247 | 11706 | 307.75 | 0 |
| IVB5_3 | 2021 | short | 16 | 0.375 | 217.75 | 3484 | 0.6563 | 0.6293 | 0.76082 | 0.66756 | 1.4347 | 1.4662 | 1.0571 | 3.2724 | 3295.8 | 261 | 0 |
| IVB5_3 | 2022 | short | 3 | 0.33333 | -43.917 | -131.75 | -0.037109 | -0.039874 | -0.039232 | -0.045433 | -0.076039 | 0.94632 | -0.053891 | 3.7885 | 2454.5 | 46.75 | 0 |
| IVB5_3 | 2018-22 | net_mnq | 88 | 0.19318 | -33.734 | -2968.6 | -3.0093 | -2.4168 | -2.1562 | -1.2924 | -1.7643 | 0.47625 | -0.17707 | 4.0249 | 3355.7 | 190.62 | 0 |
| IVB5_3 | 2018-22 | stress_four_ticks | 88 | 0.19318 | -359.98 | -31678 | -3.1983 | -2.5466 | -2.2626 | -1.3658 | -1.8369 | 0.45798 | -0.17889 | 42.153 | 35444 | 3898 | 0 |
| IVB15_2 | 2018-22 | all | 213 | 0.26291 | -79.644 | -16964 | -0.9483 | -1.0345 | -1.0715 | -0.42434 | -0.75326 | 0.84856 | -0.12894 | 28.756 | 26334 | 3459.2 | 0 |
| IVB15_2 | 2018 | all | 39 | 0.25641 | -46.096 | -1797.8 | -0.38082 | -0.38278 | -0.45032 | -0.38517 | -0.71932 | 0.86064 | -0.46378 | 2.253 | 3891.8 | 632.75 | 0 |
| IVB15_2 | 2019 | all | 36 | 0.19444 | -150.72 | -5426 | -1.9582 | -1.963 | -2.0361 | -1.8951 | -2.7034 | 0.48399 | -1 | 6.5309 | 5426 | 596 | 0 |
| IVB15_2 | 2020 | all | 49 | 0.2449 | -219.39 | -10750 | -1.1599 | -1.4479 | -1.3683 | -1.1543 | -1.8217 | 0.67098 | -0.65065 | 17.601 | 16457 | 795.25 | 0 |
| IVB15_2 | 2021 | all | 59 | 0.30508 | 5.3771 | 317.25 | 0.032834 | 0.036079 | 0.035849 | 0.03305 | 0.063848 | 1.0103 | 0.030352 | 13.622 | 10452 | 952.75 | 0 |
| IVB15_2 | 2022 | all | 30 | 0.3 | 23.083 | 692.5 | 0.064482 | 0.067728 | 0.076674 | 0.06558 | 0.12296 | 1.0275 | 0.07755 | 9.0432 | 8965.2 | 482.5 | 0 |
| IVB15_2 | 2018-22 | long | 73 | 0.21918 | -234.03 | -17084 | -1.7103 | -1.7174 | -1.5413 | -0.75583 | -1.1806 | 0.60629 | -0.1485 | 23.718 | 23027 | 1209.2 | 0 |
| IVB15_2 | 2018 | long | 13 | 0.23077 | -83.404 | -1084.2 | -0.3492 | -0.43095 | -0.44782 | -0.36171 | -0.65178 | 0.78476 | -0.34332 | 1.773 | 3170.8 | 214.25 | 0 |
| IVB15_2 | 2019 | long | 13 | 0.076923 | -295.33 | -3839.2 | -3.1322 | -2.6885 | -2.4771 | -2.4419 | -2.791 | 0.17115 | -0.82885 | 4.9548 | 4632 | 219.25 | 0 |
| IVB15_2 | 2020 | long | 16 | 0.1875 | -434.12 | -6946 | -1.6576 | -1.6464 | -1.5272 | -1.5754 | -1.9813 | 0.38581 | -0.75546 | 11.634 | 9158 | 271 | 0 |
| IVB15_2 | 2021 | long | 16 | 0.3125 | -228.81 | -3661 | -0.82491 | -0.87995 | -0.78713 | -0.83277 | -1.2255 | 0.61664 | -0.70761 | 5.919 | 5173.8 | 261 | 0 |
| IVB15_2 | 2022 | long | 15 | 0.26667 | -103.58 | -1553.8 | -0.20824 | -0.20972 | -0.18662 | -0.21523 | -0.3883 | 0.87922 | -0.21814 | 7.3876 | 7151.2 | 243.75 | 0 |
| IVB15_2 | 2018-22 | short | 140 | 0.28571 | 0.85714 | 120 | 0.0081085 | 0.0090304 | 0.0091043 | 0.0036392 | 0.0069537 | 1.0017 | 0.0015652 | 11.265 | 15346 | 2250 | 0 |
| IVB15_2 | 2018 | short | 26 | 0.26923 | -27.442 | -713.5 | -0.19565 | -0.18718 | -0.2209 | -0.19939 | -0.38253 | 0.90926 | -0.19997 | 2.6117 | 3582.2 | 418.5 | 0 |
| IVB15_2 | 2019 | short | 23 | 0.26087 | -68.989 | -1586.8 | -0.65275 | -0.66673 | -0.676 | -0.66031 | -1.0856 | 0.73029 | -0.58165 | 3.1181 | 2728 | 376.75 | 0 |
| IVB15_2 | 2020 | short | 33 | 0.27273 | -115.28 | -3804.2 | -0.45908 | -0.60728 | -0.66264 | -0.46303 | -0.80138 | 0.82193 | -0.4045 | 8.4742 | 9367.8 | 524.25 | 0 |
| IVB15_2 | 2021 | short | 43 | 0.30233 | 92.517 | 3978.2 | 0.46301 | 0.45791 | 0.40624 | 0.46657 | 1.0019 | 1.1874 | 0.48346 | 9.097 | 8228.8 | 691.75 | 0 |
| IVB15_2 | 2022 | short | 15 | 0.33333 | 149.75 | 2246.2 | 0.28241 | 0.35141 | 0.43643 | 0.29154 | 0.5668 | 1.1828 | 0.39852 | 6.7233 | 5659 | 238.75 | 0 |
| IVB15_2 | 2018-22 | net_mnq | 213 | 0.26291 | -8.4794 | -1806.1 | -1.0096 | -1.1011 | -1.1393 | -0.45168 | -0.79743 | 0.83992 | -0.13398 | 3.061 | 2698.2 | 455.62 | 0 |
| IVB15_2 | 2018-22 | stress_four_ticks | 213 | 0.25822 | -106.62 | -22709 | -1.2643 | -1.3762 | -1.4168 | -0.56499 | -0.97591 | 0.80549 | -0.15115 | 34.421 | 30072 | 9204.2 | 0 |
| BASE5 | 2018-22 | all | 1095 | 0.35434 | 99.567 | 1.0903e+05 | 2.6035 | 3.0576 | 3.0644 | 1.1644 | 2.3577 | 1.2255 | 1.7253 | 5.3471 | 12649 | 17774 | 0 |
| BASE5 | 2018 | all | 174 | 0.31034 | -8.4569 | -1471.5 | -0.16569 | -0.19988 | -0.20816 | -0.16616 | -0.31087 | 0.97002 | -0.22257 | 5.2351 | 6637.8 | 2831.5 | 0 |
| BASE5 | 2019 | all | 225 | 0.34222 | -2.5611 | -576.25 | -0.07221 | -0.074051 | -0.10133 | -0.072227 | -0.1318 | 0.9886 | -0.10359 | 5.0823 | 5562.8 | 3661.2 | 0 |
| BASE5 | 2020 | all | 226 | 0.36283 | 110.76 | 25032 | 1.2428 | 1.4716 | 1.5563 | 1.2402 | 2.4777 | 1.2245 | 2.3241 | 5.2029 | 10728 | 3663.5 | 0 |
| BASE5 | 2021 | all | 230 | 0.38261 | 158.42 | 36438 | 2.061 | 2.3614 | 2.2514 | 2.0597 | 4.2304 | 1.3744 | 3.5671 | 5.1342 | 10215 | 3722.5 | 0 |
| BASE5 | 2022 | all | 240 | 0.3625 | 206.69 | 49605 | 1.6619 | 2.0399 | 2.2174 | 1.6649 | 3.4255 | 1.2833 | 3.9374 | 5.8448 | 12649 | 3895 | 0 |
| BASE5 | 2018-22 | long | 577 | 0.36742 | 71.571 | 41297 | 1.4648 | 1.5913 | 1.6465 | 0.65499 | 1.266 | 1.1694 | 0.541 | 5.7558 | 15279 | 9488.2 | 0 |
| BASE5 | 2018 | long | 95 | 0.30526 | -38.671 | -3673.8 | -0.60933 | -0.67274 | -0.74032 | -0.6118 | -1.0773 | 0.85875 | -0.5236 | 5.2659 | 7044.2 | 1563.8 | 0 |
| BASE5 | 2019 | long | 122 | 0.36885 | 2.709 | 330.5 | 0.056438 | 0.058788 | 0.081144 | 0.056558 | 0.10391 | 1.0125 | 0.071305 | 3.9078 | 4635 | 1999.5 | 0 |
| BASE5 | 2020 | long | 124 | 0.40323 | 146.78 | 18201 | 1.2833 | 1.4302 | 1.6346 | 1.279 | 2.5504 | 1.3265 | 2.6973 | 3.7851 | 6721.2 | 2039 | 0 |
| BASE5 | 2021 | long | 119 | 0.42857 | 207.2 | 24657 | 1.9995 | 2.1336 | 2.1581 | 1.9862 | 4.1919 | 1.5362 | 3.2814 | 3.4083 | 7514.2 | 1947.8 | 0 |
| BASE5 | 2022 | long | 117 | 0.31624 | 15.229 | 1781.8 | 0.092467 | 0.10302 | 0.10319 | 0.092862 | 0.17352 | 1.0199 | 0.11708 | 9.3393 | 15279 | 1938.2 | 0 |
| BASE5 | 2018-22 | short | 518 | 0.33977 | 130.75 | 67730 | 2.1865 | 2.4359 | 2.4501 | 0.97611 | 2.0665 | 1.2826 | 0.68277 | 8.0803 | 19856 | 8285.5 | 0 |
| BASE5 | 2018 | short | 79 | 0.31646 | 27.877 | 2202.2 | 0.33661 | 0.35247 | 0.40022 | 0.33859 | 0.67084 | 1.0955 | 0.51001 | 3.7439 | 4335.2 | 1267.8 | 0 |
| BASE5 | 2019 | short | 103 | 0.31068 | -8.8034 | -906.75 | -0.16647 | -0.17966 | -0.26576 | -0.16694 | -0.30228 | 0.96237 | -0.30474 | 3.1811 | 2975.5 | 1661.8 | 0 |
| BASE5 | 2020 | short | 102 | 0.31373 | 66.966 | 6830.5 | 0.47591 | 0.53091 | 0.51387 | 0.47605 | 0.95522 | 1.1226 | 0.461 | 8.1771 | 14758 | 1624.5 | 0 |
| BASE5 | 2021 | short | 111 | 0.33333 | 106.13 | 11780 | 0.92761 | 1.0877 | 1.0558 | 0.92794 | 1.8723 | 1.2295 | 1.2182 | 6.0478 | 9670.5 | 1774.8 | 0 |
| BASE5 | 2022 | short | 123 | 0.4065 | 388.81 | 47823 | 2.1075 | 2.4156 | 2.7157 | 2.0967 | 4.6835 | 1.5597 | 4.6409 | 4.1589 | 10346 | 1956.8 | 0 |
| BASE5 | 2018-22 | net_mnq | 1095 | 0.35342 | 9.4417 | 10339 | 2.4688 | 2.9 | 2.9074 | 1.1042 | 2.2229 | 1.2122 | 1.6261 | 0.81757 | 1272.6 | 2341.3 | 0 |
| BASE5 | 2018-22 | stress_four_ticks | 1095 | 0.3516 | 72.622 | 79521 | 1.8923 | 2.2237 | 2.233 | 0.84649 | 1.6631 | 1.1575 | 0.99929 | 12.494 | 15928 | 47279 | 0 |
| BASE15 | 2018-22 | all | 1077 | 0.36119 | 116.04 | 1.2498e+05 | 3.0213 | 3.5246 | 3.7884 | 1.351 | 2.7585 | 1.2688 | 1.9777 | 4.9916 | 12649 | 17488 | 0 |
| BASE15 | 2018 | all | 173 | 0.32948 | 21.103 | 3650.8 | 0.39727 | 0.46415 | 0.50442 | 0.39837 | 0.77966 | 1.0764 | 0.48557 | 5.4882 | 7548.5 | 2804.2 | 0 |
| BASE15 | 2019 | all | 223 | 0.32287 | -8.7298 | -1946.8 | -0.24597 | -0.25333 | -0.33955 | -0.24603 | -0.44773 | 0.96154 | -0.29273 | 7.209 | 6650.2 | 3636.8 | 0 |
| BASE15 | 2020 | all | 222 | 0.37387 | 121.87 | 27056 | 1.3689 | 1.4717 | 1.5955 | 1.3659 | 2.7197 | 1.2519 | 2.8528 | 5.1323 | 9446.5 | 3589.5 | 0 |
| BASE15 | 2021 | all | 223 | 0.38565 | 171.7 | 38288 | 2.2028 | 2.4089 | 2.918 | 2.2006 | 4.5978 | 1.414 | 4.3968 | 4.0066 | 8708.2 | 3621.8 | 0 |
| BASE15 | 2022 | all | 236 | 0.38559 | 245.46 | 57929 | 1.9668 | 2.5882 | 3.0273 | 1.97 | 4.0839 | 1.3476 | 4.5981 | 4.7047 | 12649 | 3836 | 0 |
| BASE15 | 2018-22 | long | 560 | 0.38571 | 98.42 | 55115 | 2.0043 | 2.102 | 2.2289 | 0.89536 | 1.7559 | 1.2436 | 0.82149 | 6.9298 | 13429 | 9215 | 0 |
| BASE15 | 2018 | long | 98 | 0.30612 | -52.25 | -5120.5 | -0.84956 | -0.89779 | -0.97458 | -0.852 | -1.4621 | 0.81146 | -0.60545 | 6.8728 | 8491 | 1620.5 | 0 |
| BASE15 | 2019 | long | 118 | 0.36441 | 4.8263 | 569.5 | 0.099985 | 0.10726 | 0.14031 | 0.10021 | 0.18468 | 1.0227 | 0.12991 | 3.7881 | 4383.8 | 1935.5 | 0 |
| BASE15 | 2020 | long | 119 | 0.43697 | 192.41 | 22897 | 1.6662 | 1.7867 | 2.186 | 1.6564 | 3.3503 | 1.4544 | 3.3932 | 3.4919 | 6721.2 | 1952.8 | 0 |
| BASE15 | 2021 | long | 114 | 0.45614 | 247.84 | 28254 | 2.3554 | 2.4441 | 2.5563 | 2.33 | 5.0504 | 1.6765 | 3.76 | 2.9526 | 7514.2 | 1866.5 | 0 |
| BASE15 | 2022 | long | 111 | 0.35135 | 76.714 | 8515.2 | 0.45317 | 0.48609 | 0.5076 | 0.45498 | 0.86387 | 1.104 | 0.63662 | 8.2951 | 13429 | 1839.8 | 0 |
| BASE15 | 2018-22 | short | 517 | 0.33462 | 135.13 | 69862 | 2.2593 | 2.6346 | 2.9187 | 1.0084 | 2.1383 | 1.2928 | 1.1889 | 6.0271 | 11762 | 8273.2 | 0 |
| BASE15 | 2018 | short | 75 | 0.36 | 116.95 | 8771.2 | 1.2738 | 1.328 | 1.5125 | 1.2726 | 2.8221 | 1.4256 | 2.7094 | 2.5109 | 3250.2 | 1183.8 | 0 |
| BASE15 | 2019 | short | 105 | 0.27619 | -23.964 | -2516.2 | -0.45611 | -0.48658 | -0.6559 | -0.45712 | -0.82088 | 0.90129 | -0.43549 | 6.2597 | 5778 | 1701.2 | 0 |
| BASE15 | 2020 | short | 103 | 0.30097 | 40.371 | 4158.2 | 0.29236 | 0.32581 | 0.35568 | 0.29255 | 0.57524 | 1.0729 | 0.47878 | 6.238 | 8650.8 | 1636.8 | 0 |
| BASE15 | 2021 | short | 109 | 0.31193 | 92.062 | 10035 | 0.79771 | 0.89549 | 1.0435 | 0.79847 | 1.6267 | 1.1978 | 1.4373 | 5.111 | 6981.5 | 1755.2 | 0 |
| BASE15 | 2022 | short | 125 | 0.416 | 395.31 | 49414 | 2.1837 | 2.8077 | 3.5078 | 2.1716 | 4.8443 | 1.5829 | 6.5525 | 2.7871 | 7571.2 | 1996.2 | 0 |
| BASE15 | 2018-22 | net_mnq | 1077 | 0.36119 | 11.089 | 11943 | 2.8872 | 3.3688 | 3.6225 | 1.2911 | 2.6208 | 1.2549 | 1.8784 | 0.7154 | 1272.6 | 2303.5 | 0 |
| BASE15 | 2018-22 | stress_four_ticks | 1077 | 0.36026 | 89.078 | 95937 | 2.3113 | 2.6976 | 2.9069 | 1.0338 | 2.0477 | 1.1976 | 1.4677 | 9.3706 | 13084 | 46528 | 0 |

## Actual strategy vs price-only controls

The actual one/day ledgers are NOT nested: their first qualifying times differ. The following is an executable
whole-strategy comparison, not a falsely matched kept/removed trade ledger.

```json
{
  "IVB5_2": {
    "candidate_net": -24896.75,
    "base_net": 109026.25,
    "candidate_dd": 29865.25,
    "base_dd": 12648.75,
    "nested_actual_ledgers": false
  },
  "IVB5_3": {
    "candidate_net": -29233.0,
    "base_net": 109026.25,
    "candidate_dd": 33134.5,
    "base_dd": 12648.75,
    "nested_actual_ledgers": false
  },
  "IVB15_2": {
    "candidate_net": -16964.25,
    "base_net": 124976.75,
    "candidate_dd": 26333.5,
    "base_dd": 12648.75,
    "nested_actual_ledgers": false
  }
}
```

## Independent-window filter diagnostics

All potential price windows versus all budget-qualified windows, brackets/timeexit unchanged. These overlap
and are NON-EXECUTABLE diagnostics. Base/kept/removed totalnet, removedmean/t and1000matched-size random
subsets are shown. Their sums/DD cannot be presented as account or capped-strategy performance.

```json
{
  "IVB5_2": {
    "non_executable_overlapping_windows": true,
    "base_trades": 35172,
    "kept_trades": 5468,
    "removed_trades": 29704,
    "base_net": 3705563.0,
    "kept_net": 75567.0,
    "removed_net": 3629996.0,
    "removed_avg": 122.20562887153245,
    "removed_t": 19.17774601308564,
    "random_subsets": 1000,
    "random_net_mean": 578198.04,
    "p_random_net_ge_kept": 1.0,
    "p_kept_better_net_and_dd": 0.0
  },
  "IVB5_3": {
    "non_executable_overlapping_windows": true,
    "base_trades": 35172,
    "kept_trades": 2086,
    "removed_trades": 33086,
    "base_net": 3705563.0,
    "kept_net": -45528.5,
    "removed_net": 3751091.5,
    "removed_avg": 113.37397993108868,
    "removed_t": 18.49533002134431,
    "random_subsets": 1000,
    "random_net_mean": 219602.445,
    "p_random_net_ge_kept": 1.0,
    "p_kept_better_net_and_dd": 0.0
  },
  "IVB15_2": {
    "non_executable_overlapping_windows": true,
    "base_trades": 12122,
    "kept_trades": 1887,
    "removed_trades": 10235,
    "base_net": 1299930.5,
    "kept_net": 45804.25,
    "removed_net": 1254126.25,
    "removed_avg": 122.53309721543722,
    "removed_t": 11.280139168227294,
    "random_subsets": 1000,
    "random_net_mean": 200470.635,
    "p_random_net_ge_kept": 1.0,
    "p_kept_better_net_and_dd": 0.0
  }
}
```

## Conditional random timing

1000one-window-per-day paths on the actual candidate's EX-POST selected event dates. Windows come from
that date's eligible price-only set with original bracket/14:55exit and costs. This isolates timing conditional
on event days; it does not give an implementable advance calendar. All random totals/DD are retained in
 design_conditional_time_placebos.json; no placebo was selected for trading.

```json
{
  "IVB5_2": {
    "runs": 1000,
    "event_days": 223,
    "informative": true,
    "ex_post_event_date_conditioning": true,
    "actual_net": -24896.75,
    "actual_dd": 29865.25,
    "random_net_mean": -18346.555,
    "p_random_net_ge_kept": 0.685,
    "p_kept_better_net_and_dd": 0.308
  },
  "IVB5_3": {
    "runs": 1000,
    "event_days": 88,
    "informative": true,
    "ex_post_event_date_conditioning": true,
    "actual_net": -29233.0,
    "actual_dd": 33134.5,
    "random_net_mean": -10442.485,
    "p_random_net_ge_kept": 0.984,
    "p_kept_better_net_and_dd": 0.015
  },
  "IVB15_2": {
    "runs": 1000,
    "event_days": 213,
    "informative": true,
    "ex_post_event_date_conditioning": true,
    "actual_net": -16964.25,
    "actual_dd": 26333.5,
    "random_net_mean": -16563.845,
    "p_random_net_ge_kept": 0.511,
    "p_kept_better_net_and_dd": 0.456
  }
}
```

## Data, engineering and limits

NQintake 1,769,357rows,0exactduplicates,0conflictingkeys;
VXNintake 3,351rows,0exactduplicates,0conflictingdates.
Intake includes pre2018source metadata; actual design grids/calibration start2018 without2017warm-up.
Clock: native CT minute close labels; exact previous cash-date VXN. Daily closing-value receive/revision
vintages and live marketability during stress are unverified. Retained held-gap tickets:0 across all
actual candidate/control ledgers, listed in design_held_gap_tickets.csv. No incomplete ticket deleted.

Engineering passed exact prior-date/holiday checks, missing exact quote rejection,60/20date warm-up,
variance-vs-sigma units, later-price/completeness mutation invariance of earlier features, first-signal/no-retry
behavior, extra-minute delay, and shared entrybar/gap/through tests. Features, calibration history, window/
selection/missingentry counts and raw-input/source hashes are retained. These checks do not prove an edge.

No candidate cheap/complete gate passes. No2023+returns, expensive post-pass placebos/resampling/MC,
accountbench, independent promotion orPowerLanguage. Positive unfiltered controls remain unselectable;
do not nominate them after seeing this loss or retune a failed family. Option-implied variance may forecast
volatility without a directional underreaction that survives costs, consistent with this rejected test.

Actual raw-data research execution is recorded in design_verified_execution.json, completed
2026-10-26T02:30:44.365473+00:00. A GitHub read or automation schedule alone is not counted as research.
Next: preserve the failure, leave research continuation enabled, and preregister a DISTINCT mechanism.
Claude review path: agents/codex/results/implied_variance_breach.md.
