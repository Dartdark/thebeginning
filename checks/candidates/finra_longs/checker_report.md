# Checker report: finra_longs

kind strategy, pre-registered False, variants 2, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 3.51, PSR 1.000, DSR(N=374) 0.757 |
| G2 holdout | PASS | 2018-22 $360.9 (t 2.16), 2023-26 $1053.3 (t 2.81) |
| G3 years | PASS | 8/9 years positive: 2018 $-1,171, 2019 $17,764, 2020 $34,397, 2021 $19,883, 2022 $5,636, 2023 $29,840, 2024 $14,579, 2025 $61,411, 2026 $64,799 |
| G4 concentration | PASS | without the best 5% of trades: $58,561 total ($165.0 a trade) vs $247,138 |
| G5 placebo | PASS | 500 placebo runs, mean $137.5; share >= real $660.8: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.000 |
| G7 MinTRL | PASS | 374 trades vs MinTRL 50 |
| G8 regime stability | PASS | rho 0.68 (yearly Sharpe 2018 -0.4, 2019 2.2, 2020 2.1, 2021 1.3, 2022 0.2, 2023 1.8, 2024 0.8, 2025 1.3, 2026 2.3) |
| G13 invariance | PASS | outcome = net / risk; P3 time (years): SIS 0.244 vs Gaussian 95% 0.326 (ok; permutation p 0.530; 8 groups, n 357); P2 VIX regime (past-only median): SIS 0.183 vs Gaussian 95% 0.221 (ok; permutation p 0.127; 2 groups, n 374) |

**Gates: 7/8 pass -> FAIL**

## Standard metrics
```
      trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      374 56% $661 $30,130   1.21    2.81          1.78 $23,896   1.26  4.13      14.61
longs    374 56% $661 $30,130   1.21    2.81          1.78 $23,896   1.26  4.13      14.61
```
## 2023+ bootstrap
```
                      actual        p5       p50       p95
name  metric                                              
all   sharpe            1.40      0.87      1.45      2.09
      sortino           3.82      1.85      3.83      6.42
      pf_day            2.10      1.53      2.11      2.92
      calmar            3.09      0.95      2.80      5.90
      ulcer             4.06      2.36      4.95     12.01
      max_dd       14,214.00 10,268.63 15,642.13 26,029.29
      P(Sharpe<=0)       NaN       NaN      0.00       NaN
longs sharpe            1.40      0.87      1.45      2.09
      sortino           3.82      1.85      3.83      6.42
      pf_day            2.10      1.53      2.11      2.92
      calmar            3.09      0.95      2.80      5.90
      ulcer             4.06      2.36      4.95     12.01
      max_dd       14,214.00 10,268.63 15,642.13 26,029.29
      P(Sharpe<=0)       NaN       NaN      0.00       NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all     $14,214      12% $19,179 $31,266 $39,596        100%        100%        100%
longs   $14,214      12% $19,179 $31,266 $39,596        100%        100%        100%
```