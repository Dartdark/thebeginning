# Checker report: vb_nr7_sizing_replica_pyvb

kind filter, pre-registered True, variants 4, N (ranked items in TRIALS.csv) 239, t_threshold(N) 3.53

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | kept $185.0 (n 237) vs skipped $61.6 (n 1497), t 2.16 |
| G2 holdout | PASS | kept - skipped: 2018-22 $+150.8, 2023-26 $+96.0 |
| G3 years | PASS | kept beats skipped in 7/9 years: 2018 +171, 2019 -44, 2020 +281, 2021 +76, 2022 +127, 2023 +361, 2024 +174, 2025 +27, 2026 -358 |
| G5 placebo | PASS | labels shuffled within years (2,000): p 0.0370 |
| G6 resampling | PASS | kept trades 2023+ P(Sharpe <= 0) 0.050 |
| G7 MinTRL | PASS | 237 trades vs MinTRL 66 |
| G8 regime stability | FAIL | rho 0.55 (yearly Sharpe 2018 1.4, 2019 -0.1, 2020 2.5, 2021 1.3, 2022 0.9, 2023 2.6, 2024 0.6, 2025 1.2, 2026 -1.3) |

**Gates: 5/7 pass -> FAIL**

## Standard metrics
```
           trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all trades   1734 65%  $78 $14,997   1.14    1.73          1.22 $15,715   0.95  3.92       7.65
kept          237 70% $185  $4,833   1.04    1.74          1.71  $5,540   0.87  1.60       6.05
kept longs    237 70% $185  $4,833   1.04    1.74          1.71  $5,540   0.87  1.60       6.05
```
## 2023+ bootstrap
```
                           actual        p5       p50       p95
name       metric                                              
all trades sharpe            1.24      0.48      1.26      2.07
           sortino           1.89      0.69      1.93      3.38
           pf_day            1.34      1.12      1.35      1.65
           calmar            1.23      0.30      1.18      2.75
           ulcer             7.04      3.25      6.46     16.51
           max_dd       15,715.00 10,399.64 16,654.50 29,540.90
           P(Sharpe<=0)       NaN       NaN      0.00       NaN
kept       sharpe            0.87      0.02      0.87      1.70
           sortino           1.36      0.03      1.37      3.65
           pf_day            1.83      1.02      1.84      3.52
           calmar            0.91      0.01      0.72      2.53
           ulcer             2.60      1.54      3.95     11.50
           max_dd        5,540.50  3,100.84  6,617.12 13,610.26
           P(Sharpe<=0)       NaN       NaN      0.05       NaN
kept longs sharpe            0.87      0.02      0.87      1.70
           sortino           1.36      0.03      1.37      3.65
           pf_day            1.83      1.02      1.84      3.52
           calmar            0.91      0.01      0.72      2.53
           ulcer             2.60      1.54      3.95     11.50
           max_dd        5,540.50  3,100.84  6,617.12 13,610.26
           P(Sharpe<=0)       NaN       NaN      0.05       NaN
```
## 2023+ drawdown permutation
```
           actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all trades   $15,715      34% $17,351 $27,358 $33,927        100%        100%        100%
kept          $5,540      23%  $6,768 $10,834 $12,567        100%        100%        100%
kept longs    $5,540      23%  $6,768 $10,834 $12,567        100%        100%        100%
```