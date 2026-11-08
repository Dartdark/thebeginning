# Checker report: mo_cl

kind strategy, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 0.80, PSR 0.801, DSR(N=374) 0.010 |
| G2 holdout | FAIL | 2018-22 $133.6 (t 1.17), 2023-26 $-52.3 (t -0.59) |
| G3 years | FAIL | 5/9 years positive: 2018 $-654, 2019 $1,443, 2020 $3,470, 2021 $3,334, 2022 $7,500, 2023 $-1,415, 2024 $-1,246, 2025 $200, 2026 $-1,204 |
| G4 concentration | FAIL | without the best 5% of trades: $-18,920 total ($-109.4 a trade) vs $11,430 |
| G5 placebo | FAIL | no placebo.csv supplied (required for a strategy) |
| G6 resampling | FAIL | 2023+ P(Sharpe <= 0) 0.721 |
| G7 MinTRL | FAIL | 183 trades vs MinTRL 689 |
| G8 regime stability | FAIL | rho 0.55 (yearly Sharpe 2018 -0.2, 2019 0.3, 2020 0.7, 2021 0.8, 2022 0.7, 2023 -0.3, 2024 -0.4, 2025 0.1, 2026 -0.9) |
| G13 invariance | PASS | outcome = net / risk; P3 time (years): SIS 0.226 vs Gaussian 95% 0.447 (ok; permutation p 0.983; 7 groups, n 159); P2 VIX regime (past-only median): SIS 0.172 vs Gaussian 95% 0.314 (ok; permutation p 0.366; 2 groups, n 183) |

**Gates: 0/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       183 42%  $62 $1,297   0.27    0.54          1.19  $8,446   0.15  6.13       0.42
longs      79 42% $-51  $-461  -0.22   -0.31          0.83 $10,400  -0.04  8.43      -0.11
shorts    104 42% $149 $1,758   0.40    0.94          1.42  $5,186   0.34  3.66       0.96
```
## 2023+ bootstrap
```
                      actual       p5      p50       p95
name   metric                                           
all    sharpe          -0.30    -1.32    -0.34      0.55
       sortino         -0.49    -1.77    -0.55      1.07
       pf_day           0.84     0.47     0.82      1.39
       calmar          -0.14    -0.26    -0.13      0.41
       ulcer            7.49     3.06     8.47     19.31
       max_dd       6,851.60 3,968.13 8,556.40 16,325.47
       P(Sharpe<=0)      NaN      NaN     0.72       NaN
longs  sharpe          -1.53    -2.27    -1.56     -0.81
       sortino         -1.68    -2.32    -1.69     -0.98
       pf_day           0.23     0.07     0.22      0.50
       calmar          -0.27    -0.27    -0.26     -0.21
       ulcer           12.44     5.36    11.19     18.12
       max_dd       9,269.00 5,088.68 9,711.40 15,111.19
       P(Sharpe<=0)      NaN      NaN     1.00       NaN
shorts sharpe           0.54    -0.36     0.54      1.26
       sortino          1.12    -0.57     1.13      3.62
       pf_day           1.51     0.77     1.52      2.96
       calmar           0.61    -0.14     0.42      1.92
       ulcer            1.53     1.09     2.61      7.37
       max_dd       2,478.00 1,731.65 3,447.00  7,127.74
       P(Sharpe<=0)      NaN      NaN     0.15       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank   dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all       $6,852      30% $7,747 $11,158 $12,991        100%        100%        100%
longs     $9,269       7% $9,454 $10,492 $10,964        100%        100%        100%
shorts    $2,478      19% $3,196  $5,359  $6,352        100%         96%         59%
```