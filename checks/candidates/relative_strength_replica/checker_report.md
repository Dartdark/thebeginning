# Checker report: relative_strength_replica

kind strategy, pre-registered False, variants 12, N (ranked items in TRIALS.csv) 266, t_threshold(N) 3.56

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 3.85, PSR 1.000, DSR(N=266) 0.844 |
| G2 holdout | PASS | 2018-22 $251.6 (t 2.81), 2023-26 $343.9 (t 2.69) |
| G3 years | PASS | 9/9 years positive: 2018 $25,295, 2019 $7,282, 2020 $19,931, 2021 $41,686, 2022 $58,016, 2023 $12,147, 2024 $58,872, 2025 $63,044, 2026 $58,203 |
| G4 concentration | FAIL | without the best 5% of trades: $-43,276 total ($-39.2 a trade) vs $344,477 |
| G5 placebo | PASS | 100 placebo runs, mean $2.1; share >= real $295.9: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.002 |
| G7 MinTRL | PASS | 1164 trades vs MinTRL 204 |
| G8 regime stability | PASS | rho 0.85 (yearly Sharpe 2018 1.8, 2019 0.7, 2020 0.9, 2021 1.8, 2022 1.4, 2023 0.4, 2024 1.8, 2025 1.5, 2026 1.6) |

**Gates: 6/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      1164 53% $296 $38,007   1.27    2.14          1.34 $28,539   1.33  4.77      15.93
longs     600 57% $353 $23,367   1.13    1.88          1.44 $23,445   1.00  4.32      10.83
shorts    564 48% $235 $14,640   0.68    1.15          1.25 $37,705   0.39 10.38       2.82
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe            1.36      0.60      1.32      2.01
       sortino           2.29      0.95      2.23      3.58
       pf_day            1.33      1.13      1.32      1.53
       calmar            1.72      0.40      1.39      3.02
       ulcer             9.88      4.50      8.87     25.02
       max_dd       28,539.10 22,187.09 34,219.75 58,663.04
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
longs  sharpe            1.41      0.73      1.41      2.10
       sortino           2.43      1.16      2.43      3.92
       pf_day            1.52      1.24      1.52      1.89
       calmar            1.86      0.57      1.69      3.63
       ulcer             5.57      3.13      6.06     14.67
       max_dd       18,945.90 13,040.22 20,649.05 34,300.44
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
shorts sharpe            0.53     -0.32      0.49      1.27
       sortino           0.88     -0.48      0.81      2.31
       pf_day            1.17      0.91      1.15      1.45
       calmar            0.51     -0.11      0.32      1.29
       ulcer            20.12      7.38     19.08     59.60
       max_dd       27,306.05 23,188.25 39,655.90 76,881.51
       P(Sharpe<=0)       NaN       NaN      0.16       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $28,539      10% $37,554 $59,791 $75,486        100%        100%        100%
longs    $18,946      15% $24,164 $39,183 $48,541        100%        100%        100%
shorts   $27,306       9% $38,417 $60,670 $72,758        100%        100%        100%
```