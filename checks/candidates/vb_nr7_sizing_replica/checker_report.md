# Checker report: vb_nr7_sizing_replica

kind filter, pre-registered True, variants 4, N (ranked items in TRIALS.csv) 239, t_threshold(N) 3.53

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | kept $217.2 (n 240) vs skipped $60.3 (n 1503), t 2.81 |
| G2 holdout | PASS | kept - skipped: 2018-22 $+174.2, 2023-26 $+139.9 |
| G3 years | PASS | kept beats skipped in 6/9 years: 2018 +201, 2019 -102, 2020 +378, 2021 -6, 2022 +175, 2023 +306, 2024 +144, 2025 +109, 2026 -153 |
| G5 placebo | PASS | labels shuffled within years (2,000): p 0.0045 |
| G6 resampling | PASS | kept trades 2023+ P(Sharpe <= 0) 0.020 |
| G7 MinTRL | PASS | 240 trades vs MinTRL 50 |
| G8 regime stability | FAIL | rho 0.55 (yearly Sharpe 2018 1.4, 2019 -1.0, 2020 3.0, 2021 0.8, 2022 1.4, 2023 2.4, 2024 0.6, 2025 1.4, 2026 -0.6) |

**Gates: 5/7 pass -> FAIL**

## Standard metrics
```
           trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all trades   1743 66%  $82 $15,848   1.21    1.83          1.23 $14,356   1.10  3.59       8.83
kept          240 73% $217  $5,791   1.24    2.31          1.88  $5,180   1.12  1.45       7.99
kept longs    240 73% $217  $5,791   1.24    2.31          1.88  $5,180   1.12  1.45       7.99
```
## 2023+ bootstrap
```
                           actual        p5       p50       p95
name       metric                                              
all trades sharpe            1.31      0.57      1.34      2.12
           sortino           1.99      0.81      2.04      3.44
           pf_day            1.37      1.15      1.38      1.68
           calmar            1.42      0.38      1.30      2.90
           ulcer             5.63      3.19      6.02     14.76
           max_dd       14,355.50 10,134.05 15,895.75 27,871.77
           P(Sharpe<=0)       NaN       NaN      0.00       NaN
kept       sharpe            1.10      0.27      1.09      1.88
           sortino           1.88      0.39      1.85      4.38
           pf_day            2.18      1.21      2.16      4.30
           calmar            1.18      0.16      1.03      2.98
           ulcer             2.34      1.27      3.18      8.57
           max_dd        5,180.50  3,049.00  5,808.75 10,952.57
           P(Sharpe<=0)       NaN       NaN      0.01       NaN
kept longs sharpe            1.10      0.27      1.09      1.88
           sortino           1.88      0.39      1.85      4.38
           pf_day            2.18      1.21      2.16      4.30
           calmar            1.18      0.16      1.03      2.98
           ulcer             2.34      1.27      3.18      8.57
           max_dd        5,180.50  3,049.00  5,808.75 10,952.57
           P(Sharpe<=0)       NaN       NaN      0.01       NaN
```
## 2023+ drawdown permutation
```
           actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all trades   $14,356      25% $16,886 $26,345 $32,326        100%        100%        100%
kept          $5,180      40%  $5,591  $9,224 $11,310        100%        100%        100%
kept longs    $5,180      40%  $5,591  $9,224 $11,310        100%        100%        100%
```