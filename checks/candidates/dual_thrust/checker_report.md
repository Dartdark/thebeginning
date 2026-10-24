# Checker report: dual_thrust

kind strategy, pre-registered False, variants 44, N (ranked items in TRIALS.csv) 287, t_threshold(N) 3.58

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 4.39, PSR 1.000, DSR(N=287) 0.939 |
| G2 holdout | PASS | 2018-22 $125.1 (t 3.14), 2023-26 $159.3 (t 3.07) |
| G3 years | PASS | 9/9 years positive: 2018 $26,902, 2019 $16,425, 2020 $9,843, 2021 $19,862, 2022 $38,085, 2023 $6,760, 2024 $59,523, 2025 $29,414, 2026 $19,441 |
| G4 concentration | PASS | without the best 5% of trades: $65,248 total ($42.6 a trade) vs $226,255 |
| G5 placebo | PASS | 20 placebo runs, mean $18.8; share >= real $140.4: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.000 |
| G7 MinTRL | PASS | 1611 trades vs MinTRL 215 |
| G8 regime stability | PASS | rho 0.80 (yearly Sharpe 2018 2.0, 2019 1.4, 2020 0.6, 2021 1.2, 2022 1.9, 2023 0.4, 2024 3.0, 2025 1.5, 2026 1.2) |

**Gates: 7/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      1611 45% $140 $24,920   1.46    2.64          1.28 $19,621   1.27  3.55      14.03
longs     821 47% $126 $11,422   0.97    1.72          1.26 $16,016   0.71  3.46       6.60
shorts    790 44% $155 $13,497   1.08    2.01          1.30 $24,140   0.56  9.91       2.72
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe            1.55      0.88      1.57      2.30
       sortino           2.85      1.56      2.88      4.39
       pf_day            1.28      1.15      1.28      1.44
       calmar            1.50      0.68      1.81      3.73
       ulcer             7.87      2.80      5.23     11.58
       max_dd       19,620.75 10,803.66 16,148.12 26,999.19
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
longs  sharpe            0.69     -0.11      0.67      1.47
       sortino           1.21     -0.18      1.19      2.75
       pf_day            1.16      0.98      1.16      1.39
       calmar            0.56     -0.04      0.50      1.68
       ulcer             7.02      4.26      9.78     26.99
       max_dd       16,015.75 10,711.77 18,095.50 34,256.53
       P(Sharpe<=0)       NaN       NaN      0.07       NaN
shorts sharpe            1.49      0.82      1.52      2.19
       sortino           2.86      1.50      2.92      4.46
       pf_day            1.40      1.21      1.41      1.66
       calmar            1.35      0.67      1.85      3.74
       ulcer             9.43      2.27      4.11      9.36
       max_dd       15,148.00  7,214.25 11,139.38 19,045.70
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $19,621      57% $18,751 $28,510 $34,030        100%        100%        100%
longs    $16,016      33% $18,009 $28,611 $34,316        100%        100%        100%
shorts   $15,148      69% $13,244 $20,810 $25,275        100%        100%        100%
```