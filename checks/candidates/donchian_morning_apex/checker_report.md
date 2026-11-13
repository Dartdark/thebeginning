# Checker report: donchian_morning_apex

kind strategy, pre-registered False, variants 4, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 2.84, PSR 0.999, DSR(N=374) 0.442 |
| G2 holdout | PASS | 2018-22 $164.1 (t 3.05), 2023-26 $125.3 (t 1.36) |
| G3 years | PASS | 8/9 years positive: 2018 $4,982, 2019 $7,929, 2020 $10,400, 2021 $24,709, 2022 $10,060, 2023 $28,878, 2024 $3,945, 2025 $-4,379, 2026 $10,151 |
| G4 concentration | FAIL | without the best 5% of trades: $-46,744 total ($-74.4 a trade) vs $96,675 |
| G5 placebo | PASS | 100 placebo runs, mean $38.2; share >= real $146.0: 0.010 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.070 |
| G7 MinTRL | PASS | 662 trades vs MinTRL 175 |
| G8 regime stability | PASS | rho 0.69 (yearly Sharpe 2018 0.9, 2019 1.6, 2020 1.0, 2021 2.7, 2022 0.9, 2023 2.1, 2024 0.3, 2025 -0.4, 2026 0.6) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.252 vs Gaussian 95% 0.275 (ok; permutation p 0.161; 9 groups, n 612); P2 VIX regime (past-only median): SIS 0.291 vs Gaussian 95% 0.173 (DIFFERS; permutation p 0.001; 2 groups, n 612) |

**Gates: 6/8 pass -> FAIL**

## Standard metrics
```
      trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      662 38% $146 $10,560   0.93    2.09          1.40 $15,872   0.67  3.96       5.34
longs    662 38% $146 $10,560   0.93    2.09          1.40 $15,872   0.67  3.96       5.34
```
## 2023+ bootstrap
```
                      actual       p5       p50       p95
name  metric                                             
all   sharpe            0.68    -0.08      0.67      1.34
      sortino           1.51    -0.15      1.48      3.37
      pf_day            1.28     0.97      1.27      1.62
      calmar            0.61    -0.04      0.56      1.83
      ulcer             8.66     3.87      8.89     24.53
      max_dd       15,872.43 9,890.28 16,898.19 32,273.12
      P(Sharpe<=0)       NaN      NaN      0.07       NaN
longs sharpe            0.68    -0.08      0.67      1.34
      sortino           1.51    -0.15      1.48      3.37
      pf_day            1.28     0.97      1.27      1.62
      calmar            0.61    -0.04      0.56      1.83
      ulcer             8.66     3.87      8.89     24.53
      max_dd       15,872.43 9,890.28 16,898.19 32,273.12
      P(Sharpe<=0)       NaN      NaN      0.07       NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all     $15,872      32% $17,835 $28,360 $34,287        100%        100%        100%
longs   $15,872      32% $17,835 $28,360 $34,287        100%        100%        100%
```