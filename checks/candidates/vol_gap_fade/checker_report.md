# Checker report: vol_gap_fade

kind strategy, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 1.60, PSR 0.957, DSR(N=374) 0.070 |
| G2 holdout | PASS | 2018-22 $122.0 (t 0.57), 2023-26 $624.5 (t 1.54) |
| G3 years | PASS | 7/9 years positive: 2018 $1,253, 2019 $-12,885, 2020 $2,659, 2021 $3,751, 2022 $26,447, 2023 $4,080, 2024 $-4,459, 2025 $53,353, 2026 $31,330 |
| G4 concentration | FAIL | without the best 5% of trades: $-72,505 total ($-247.5 a trade) vs $105,529 |
| G5 placebo | FAIL | 200 placebo runs, mean $220.7; share >= real $341.5: 0.215 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.048 |
| G7 MinTRL | PASS | 309 trades vs MinTRL 284 |
| G8 regime stability | FAIL | rho 0.53 (yearly Sharpe 2018 0.1, 2019 -2.6, 2020 0.1, 2021 0.2, 2022 1.1, 2023 0.3, 2024 -0.2, 2025 1.4, 2026 1.1) |
| G13 invariance | PASS | outcome = net / risk; P3 time (years): SIS 0.309 vs Gaussian 95% 0.370 (ok; permutation p 0.186; 9 groups, n 309); P2 VIX regime (past-only median): SIS 0.167 vs Gaussian 95% 0.259 (ok; permutation p 0.255; 2 groups, n 309) |

**Gates: 4/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       309 44% $342 $11,537   0.53    1.05          1.30 $20,518   0.56 14.70       1.57
shorts    309 44% $342 $11,537   0.53    1.05          1.30 $20,518   0.56 14.70       1.57
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe            0.77      0.01      0.69      1.29
       sortino           1.63      0.02      1.44      3.14
       pf_day            1.46      1.01      1.41      1.94
       calmar            1.10      0.01      0.70      2.15
       ulcer            13.58      5.64     12.13     33.99
       max_dd       19,365.33 15,961.04 26,373.63 48,177.38
       P(Sharpe<=0)       NaN       NaN      0.05       NaN
shorts sharpe            0.77      0.01      0.69      1.29
       sortino           1.63      0.02      1.44      3.14
       pf_day            1.46      1.01      1.41      1.94
       calmar            1.10      0.01      0.70      2.15
       ulcer            13.58      5.64     12.13     33.99
       max_dd       19,365.33 15,961.04 26,373.63 48,177.38
       P(Sharpe<=0)       NaN       NaN      0.05       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $19,365       3% $30,605 $49,439 $58,536        100%        100%        100%
shorts   $19,365       3% $30,605 $49,439 $58,536        100%        100%        100%
```