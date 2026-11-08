# Checker report: fade_ym

kind strategy, pre-registered False, variants 2, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 1.75, PSR 0.962, DSR(N=374) 0.109 |
| G2 holdout | PASS | 2018-22 $23.4 (t 0.60), 2023-26 $90.9 (t 1.83) |
| G3 years | PASS | 8/9 years positive: 2018 $3,941, 2019 $114, 2020 $5,876, 2021 $-3,926, 2022 $8,795, 2023 $6,985, 2024 $4,859, 2025 $9,267, 2026 $27,904 |
| G4 concentration | FAIL | without the best 5% of trades: $-83,940 total ($-75.4 a trade) vs $63,814 |
| G5 placebo | PASS | 100 placebo runs, mean $-18.8; share >= real $54.4: 0.020 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.036 |
| G7 MinTRL | PASS | 1172 trades vs MinTRL 1012 |
| G8 regime stability | PASS | rho 0.71 (yearly Sharpe 2018 0.4, 2019 0.0, 2020 0.5, 2021 -0.4, 2022 0.5, 2023 0.6, 2024 0.4, 2025 0.6, 2026 2.3) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.186 vs Gaussian 95% 0.200 (ok; permutation p 0.118; 9 groups, n 1122); P2 VIX regime (past-only median): SIS 0.243 vs Gaussian 95% 0.128 (DIFFERS; permutation p 0.000; 2 groups, n 1122) |

**Gates: 6/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      1172 48%  $54 $7,025   0.58    0.93          1.14 $20,752   0.34 11.61       1.21
longs     598 53% $102 $6,718   0.78    1.29          1.28  $8,722   0.77  4.82       2.79
shorts    574 44%   $5   $307   0.04    0.06          1.01 $24,767   0.01 20.02       0.03
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe            0.92      0.10      0.94      1.81
       sortino           1.51      0.15      1.54      3.18
       pf_day            1.21      1.02      1.22      1.46
       calmar            1.04      0.05      0.72      2.05
       ulcer             8.13      3.66      8.40     22.91
       max_dd       12,094.85 10,551.76 17,467.87 32,604.57
       P(Sharpe<=0)       NaN       NaN      0.04       NaN
longs  sharpe            1.10      0.23      1.09      1.91
       sortino           1.84      0.34      1.79      3.57
       pf_day            1.39      1.07      1.38      1.79
       calmar            1.23      0.12      0.94      2.59
       ulcer             4.26      2.52      5.31     13.77
       max_dd        8,609.55  6,369.75 10,927.90 19,763.04
       P(Sharpe<=0)       NaN       NaN      0.02       NaN
shorts sharpe            0.20     -0.58      0.23      1.09
       sortino           0.33     -0.87      0.38      1.94
       pf_day            1.06      0.84      1.07      1.39
       calmar            0.14     -0.19      0.13      1.05
       ulcer            11.92      4.68     12.42     34.13
       max_dd       13,484.20  9,270.38 17,260.88 33,681.27
       P(Sharpe<=0)       NaN       NaN      0.31       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $12,095       7% $16,928 $26,829 $32,065        100%        100%        100%
longs     $8,610      18% $10,713 $17,170 $21,547        100%        100%        100%
shorts   $13,484      17% $17,243 $26,735 $31,076        100%        100%        100%
```