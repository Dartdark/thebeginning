# Checker report: finra_longs_d

kind strategy, pre-registered False, variants 7, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 1.73, PSR 0.984, DSR(N=374) 0.061 |
| G2 holdout | PASS | 2018-22 $24.2 (t 0.19), 2023-26 $567.1 (t 1.87) |
| G3 years | PASS | 6/9 years positive: 2018 $4,292, 2019 $2,264, 2020 $12,102, 2021 $-3,434, 2022 $-10,096, 2023 $5,309, 2024 $-8,568, 2025 $53,420, 2026 $41,709 |
| G4 concentration | FAIL | without the best 5% of trades: $-25,159 total ($-70.9 a trade) vs $96,998 |
| G5 placebo | PASS | 500 placebo runs, mean $12.9; share >= real $259.4: 0.016 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.026 |
| G7 MinTRL | PASS | 374 trades vs MinTRL 219 |
| G8 regime stability | FAIL | rho 0.55 (yearly Sharpe 2018 1.7, 2019 0.5, 2020 0.9, 2021 -0.3, 2022 -0.5, 2023 0.5, 2024 -0.4, 2025 1.3, 2026 2.7) |
| G13 invariance | PASS | outcome = net / risk; P3 time (years): SIS 0.317 vs Gaussian 95% 0.326 (ok; permutation p 0.188; 8 groups, n 357); P2 VIX regime (past-only median): SIS 0.194 vs Gaussian 95% 0.221 (ok; permutation p 0.202; 2 groups, n 374) |

**Gates: 5/8 pass -> FAIL**

## Standard metrics
```
      trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      374 58% $259 $11,826   0.60    1.16          1.38 $25,971   0.46 12.74       1.86
longs    374 58% $259 $11,826   0.60    1.16          1.38 $25,971   0.46 12.74       1.86
```
## 2023+ bootstrap
```
                      actual       p5       p50       p95
name  metric                                             
all   sharpe            0.94     0.18      1.00      1.70
      sortino           2.25     0.26      2.31      5.59
      pf_day            1.80     1.09      1.79      2.89
      calmar            1.07     0.09      1.06      3.68
      ulcer            12.07     3.00      8.31     27.89
      max_dd       22,101.50 9,573.65 21,767.25 42,540.54
      P(Sharpe<=0)       NaN      NaN      0.03       NaN
longs sharpe            0.94     0.18      1.00      1.70
      sortino           2.25     0.26      2.31      5.59
      pf_day            1.80     1.09      1.79      2.89
      calmar            1.07     0.09      1.06      3.68
      ulcer            12.07     3.00      8.31     27.89
      max_dd       22,101.50 9,573.65 21,767.25 42,540.54
      P(Sharpe<=0)       NaN      NaN      0.03       NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all     $22,102      70% $19,191 $30,140 $35,878        100%        100%        100%
longs   $22,102      70% $19,191 $30,140 $35,878        100%        100%        100%
```