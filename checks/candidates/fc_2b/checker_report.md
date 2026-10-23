# Checker report: fc_2b

kind strategy, pre-registered False, variants 40, N (ranked items in TRIALS.csv) 282, t_threshold(N) 3.57

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 4.02, PSR 1.000, DSR(N=282) 0.890 |
| G2 holdout | PASS | 2018-22 $292.0 (t 3.68), 2023-26 $252.3 (t 2.10) |
| G3 years | PASS | 9/9 years positive: 2018 $19,928, 2019 $9,362, 2020 $13,993, 2021 $34,109, 2022 $51,961, 2023 $4,336, 2024 $27,775, 2025 $37,385, 2026 $13,752 |
| G4 concentration | PASS | without the best 5% of trades: $1,558 total ($2.1 a trade) vs $212,601 |
| G5 placebo | PASS | 300 placebo runs, mean $89.6; share >= real $275.0: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.009 |
| G7 MinTRL | PASS | 773 trades vs MinTRL 112 |
| G8 regime stability | PASS | rho 0.81 (yearly Sharpe 2018 1.7, 2019 1.0, 2020 0.8, 2021 2.1, 2022 2.2, 2023 0.2, 2024 1.5, 2025 1.8, 2026 0.7) |

**Gates: 7/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       773 61% $275 $23,355   1.32    2.58          1.51 $15,251   1.53  2.68      17.45
longs     376 64% $305 $12,613   1.07    2.04          1.59 $12,364   1.02  3.96       6.37
shorts    397 59% $246 $10,742   0.81    1.63          1.44 $21,154   0.51  6.32       3.40
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe            1.06      0.36      1.10      1.77
       sortino           2.11      0.64      2.21      3.96
       pf_day            1.40      1.11      1.42      1.78
       calmar            1.39      0.23      1.10      2.68
       ulcer             8.14      3.64      7.59     20.66
       max_dd       15,251.00 12,204.27 20,190.62 35,462.65
       P(Sharpe<=0)       NaN       NaN      0.01       NaN
longs  sharpe            1.05      0.34      1.08      1.74
       sortino           2.11      0.60      2.20      4.11
       pf_day            1.59      1.16      1.61      2.21
       calmar            1.15      0.24      1.19      2.92
       ulcer             5.49      2.73      5.57     14.79
       max_dd       12,363.50  7,497.61 12,275.12 23,188.53
       P(Sharpe<=0)       NaN       NaN      0.01       NaN
shorts sharpe            0.47     -0.33      0.50      1.20
       sortino           0.94     -0.55      1.01      2.82
       pf_day            1.24      0.87      1.26      1.79
       calmar            0.33     -0.14      0.35      1.51
       ulcer            19.38      4.89     12.24     35.41
       max_dd       21,154.50 11,362.17 20,839.38 40,171.71
       P(Sharpe<=0)       NaN       NaN      0.16       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $15,251       7% $21,396 $34,211 $41,491        100%        100%        100%
longs    $12,364      35% $13,724 $21,522 $25,747        100%        100%        100%
shorts   $21,154      53% $20,719 $32,754 $38,420        100%        100%        100%
```