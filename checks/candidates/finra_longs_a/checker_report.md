# Checker report: finra_longs_a

kind strategy, pre-registered False, variants 4, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 2.95, PSR 1.000, DSR(N=374) 0.492 |
| G2 holdout | PASS | 2018-22 $267.5 (t 1.82), 2023-26 $850.9 (t 2.38) |
| G3 years | PASS | 9/9 years positive: 2018 $1,658, 2019 $18,272, 2020 $11,930, 2021 $20,657, 2022 $4,203, 2023 $30,125, 2024 $3,336, 2025 $59,708, 2026 $44,670 |
| G4 concentration | PASS | without the best 5% of trades: $10,867 total ($30.6 a trade) vs $194,560 |
| G5 placebo | PASS | 500 placebo runs, mean $119.7; share >= real $520.2: 0.002 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.002 |
| G7 MinTRL | PASS | 374 trades vs MinTRL 61 |
| G8 regime stability | PASS | rho 0.79 (yearly Sharpe 2018 0.7, 2019 2.4, 2020 0.8, 2021 1.5, 2022 0.2, 2023 2.0, 2024 0.2, 2025 1.3, 2026 1.8) |
| G13 invariance | PASS | outcome = net / risk; P3 time (years): SIS 0.249 vs Gaussian 95% 0.326 (ok; permutation p 0.316; 8 groups, n 357); P2 VIX regime (past-only median): SIS 0.180 vs Gaussian 95% 0.221 (ok; permutation p 0.128; 2 groups, n 374) |

**Gates: 7/8 pass -> FAIL**

## Standard metrics
```
      trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      374 45% $520 $23,720   1.02    2.90          1.66 $16,040   1.48  3.86      12.27
longs    374 45% $520 $23,720   1.02    2.90          1.66 $16,040   1.48  3.86      12.27
```
## 2023+ bootstrap
```
                      actual       p5       p50       p95
name  metric                                             
all   sharpe            1.19     0.66      1.24      1.79
      sortino           3.97     1.60      3.96      6.92
      pf_day            1.92     1.38      1.93      2.66
      calmar            3.39     0.67      2.27      5.50
      ulcer             4.01     2.65      5.53     13.81
      max_dd       10,469.08 9,541.78 14,999.58 25,963.33
      P(Sharpe<=0)       NaN      NaN      0.00       NaN
longs sharpe            1.19     0.66      1.24      1.79
      sortino           3.97     1.60      3.96      6.92
      pf_day            1.92     1.38      1.93      2.66
      calmar            3.39     0.67      2.27      5.50
      ulcer             4.01     2.65      5.53     13.81
      max_dd       10,469.08 9,541.78 14,999.58 25,963.33
      P(Sharpe<=0)       NaN      NaN      0.00       NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all     $10,469       1% $18,108 $28,576 $34,504        100%        100%        100%
longs   $10,469       1% $18,108 $28,576 $34,504        100%        100%        100%
```