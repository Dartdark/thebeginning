# Checker report: finra_longs_e

kind strategy, pre-registered False, variants 7, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 2.43, PSR 1.000, DSR(N=374) 0.158 |
| G2 holdout | PASS | 2018-22 $167.9 (t 1.23), 2023-26 $1022.2 (t 2.14) |
| G3 years | PASS | 9/9 years positive: 2018 $1,830, 2019 $2,402, 2020 $4,253, 2021 $3,190, 2022 $9,318, 2023 $4,435, 2024 $7,531, 2025 $52,706, 2026 $25,284 |
| G4 concentration | PASS | without the best 5% of trades: $27,798 total ($137.6 a trade) vs $110,949 |
| G5 placebo | PASS | 500 placebo runs, mean $190.3; share >= real $520.9: 0.006 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.003 |
| G7 MinTRL | PASS | 213 trades vs MinTRL 30 |
| G8 regime stability | PASS | rho 0.80 (yearly Sharpe 2018 2.7, 2019 0.9, 2020 0.4, 2021 0.5, 2022 0.7, 2023 0.6, 2024 1.0, 2025 1.3, 2026 2.3) |
| G13 invariance | PASS | outcome = net / risk; P3 time (years): SIS 0.278 vs Gaussian 95% 0.419 (ok; permutation p 0.601; 7 groups, n 189); P2 VIX regime (past-only median): SIS 0.191 vs Gaussian 95% 0.293 (ok; permutation p 0.400; 2 groups, n 213) |

**Gates: 7/8 pass -> FAIL**

## Standard metrics
```
      trades win  avg  annual sharpe sortino profit_factor max_dd calmar ulcer ulcer_perf
all      213 55% $521 $13,586   0.84    2.96          2.05 $7,296   1.86  4.14       6.56
longs    213 55% $521 $13,586   0.84    2.96          2.05 $7,296   1.86  4.14       6.56
```
## 2023+ bootstrap
```
                     actual       p5      p50       p95
name  metric                                           
all   sharpe           1.07     0.65     1.13      1.88
      sortino          5.55     1.49     5.15     10.31
      pf_day           3.03     1.53     2.91      5.01
      calmar           3.20     0.57     2.73      6.99
      ulcer            5.60     1.60     3.36      8.52
      max_dd       7,296.17 4,635.58 7,788.17 14,089.09
      P(Sharpe<=0)      NaN      NaN     0.00       NaN
longs sharpe           1.07     0.65     1.13      1.88
      sortino          5.55     1.49     5.15     10.31
      pf_day           3.03     1.53     2.91      5.01
      calmar           3.20     0.57     2.73      6.99
      ulcer            5.60     1.60     3.36      8.52
      max_dd       7,296.17 4,635.58 7,788.17 14,089.09
      P(Sharpe<=0)      NaN      NaN     0.00       NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank   dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $7,296      50% $7,309 $11,804 $14,398        100%        100%        100%
longs    $7,296      50% $7,309 $11,804 $14,398        100%        100%        100%
```