# Checker report: turn_of_month

kind strategy, pre-registered False, variants 3, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 2.53, PSR 0.996, DSR(N=374) 0.327 |
| G2 holdout | PASS | 2018-22 $187.9 (t 1.21), 2023-26 $609.3 (t 2.26) |
| G3 years | PASS | 7/9 years positive: 2018 $8,086, 2019 $-4,843, 2020 $27,648, 2021 $-7,251, 2022 $21,467, 2023 $24,242, 2024 $6,573, 2025 $34,220, 2026 $48,909 |
| G4 concentration | FAIL | without the best 5% of trades: $-13,399 total ($-33.1 a trade) vs $159,052 |
| G5 placebo | PASS | 200 placebo runs, mean $122.2; share >= real $372.5: 0.015 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.004 |
| G7 MinTRL | PASS | 427 trades vs MinTRL 169 |
| G8 regime stability | PASS | rho 0.63 (yearly Sharpe 2018 0.8, 2019 -0.6, 2020 1.9, 2021 -0.5, 2022 0.8, 2023 1.5, 2024 0.3, 2025 1.3, 2026 1.5) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.331 vs Gaussian 95% 0.313 (DIFFERS; permutation p 0.013; 8 groups, n 377); P2 VIX regime (past-only median): SIS 0.298 vs Gaussian 95% 0.223 (DIFFERS; permutation p 0.005; 2 groups, n 377) |

**Gates: 6/8 pass -> FAIL**

## Standard metrics
```
      trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      427 53% $372 $17,374   0.83    1.45          1.37 $22,275   0.78  7.27       4.78
longs    427 53% $372 $17,374   0.83    1.45          1.37 $22,275   0.78  7.27       4.78
```
## 2023+ bootstrap
```
                      actual        p5       p50       p95
name  metric                                              
all   sharpe            1.12      0.47      1.27      1.94
      sortino           1.98      0.78      2.27      3.92
      pf_day            1.50      1.18      1.58      2.08
      calmar            1.62      0.34      1.34      3.00
      ulcer             5.78      3.73      7.64     20.54
      max_dd       17,668.25 15,112.71 23,561.75 40,648.31
      P(Sharpe<=0)       NaN       NaN      0.00       NaN
longs sharpe            1.12      0.47      1.27      1.94
      sortino           1.98      0.78      2.27      3.92
      pf_day            1.50      1.18      1.58      2.08
      calmar            1.62      0.34      1.34      3.00
      ulcer             5.78      3.73      7.64     20.54
      max_dd       17,668.25 15,112.71 23,561.75 40,648.31
      P(Sharpe<=0)       NaN       NaN      0.00       NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all     $17,668       4% $26,976 $43,688 $55,016        100%        100%        100%
longs   $17,668       4% $26,976 $43,688 $55,016        100%        100%        100%
```