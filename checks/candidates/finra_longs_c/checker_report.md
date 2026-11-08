# Checker report: finra_longs_c

kind strategy, pre-registered False, variants 7, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 2.40, PSR 1.000, DSR(N=374) 0.189 |
| G2 holdout | PASS | 2018-22 $84.6 (t 0.82), 2023-26 $641.2 (t 2.28) |
| G3 years | PASS | 7/9 years positive: 2018 $2,334, 2019 $2,154, 2020 $12,461, 2021 $3,049, 2022 $-2,068, 2023 $-1,588, 2024 $10,039, 2025 $52,678, 2026 $42,741 |
| G4 concentration | PASS | without the best 5% of trades: $1,208 total ($3.4 a trade) vs $121,800 |
| G5 placebo | PASS | 500 placebo runs, mean $70.4; share >= real $325.7: 0.002 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.004 |
| G7 MinTRL | PASS | 374 trades vs MinTRL 74 |
| G8 regime stability | PASS | rho 0.65 (yearly Sharpe 2018 1.1, 2019 0.6, 2020 1.0, 2021 0.3, 2022 -0.1, 2023 -0.2, 2024 0.9, 2025 1.3, 2026 2.8) |
| G13 invariance | PASS | outcome = net / risk; P3 time (years): SIS 0.290 vs Gaussian 95% 0.326 (ok; permutation p 0.088; 8 groups, n 357); P2 VIX regime (past-only median): SIS 0.186 vs Gaussian 95% 0.221 (ok; permutation p 0.128; 2 groups, n 374) |

**Gates: 7/8 pass -> FAIL**

## Standard metrics
```
      trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      374 52% $326 $14,849   0.83    2.31          1.58 $17,004   0.87  7.90       3.76
longs    374 52% $326 $14,849   0.83    2.31          1.58 $17,004   0.87  7.90       3.76
```
## 2023+ bootstrap
```
                      actual       p5       p50       p95
name  metric                                             
all   sharpe            1.14     0.59      1.22      1.95
      sortino           4.25     1.33      4.18      7.86
      pf_day            2.10     1.34      2.09      3.13
      calmar            1.68     0.49      2.07      5.07
      ulcer            11.10     2.37      5.10     12.42
      max_dd       15,906.83 7,752.74 12,556.71 22,015.17
      P(Sharpe<=0)       NaN      NaN      0.00       NaN
longs sharpe            1.14     0.59      1.22      1.95
      sortino           4.25     1.33      4.18      7.86
      pf_day            2.10     1.34      2.09      3.13
      calmar            1.68     0.49      2.07      5.07
      ulcer            11.10     2.37      5.10     12.42
      max_dd       15,906.83 7,752.74 12,556.71 22,015.17
      P(Sharpe<=0)       NaN      NaN      0.00       NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all     $15,907      88% $11,366 $18,234 $23,216        100%        100%        100%
longs   $15,907      88% $11,366 $18,234 $23,216        100%        100%        100%
```