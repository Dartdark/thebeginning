# Checker report: mc_btc_adx_longs

kind strategy, pre-registered False, variants 10, N (ranked items in TRIALS.csv) 487, t_threshold(N) 3.71

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 2.87, PSR 1.000, DSR(N=487) 0.417 |
| G2 holdout | PASS | 2018-22 $12.4 (t 1.13), 2023-26 $54.2 (t 2.65) |
| G3 years | PASS | 7/8 years positive: 2019 $728, 2020 $1,278, 2021 $873, 2022 $-1,092, 2023 $1,874, 2024 $5,195, 2025 $190, 2026 $1,408 |
| G4 concentration | PASS | without the best 5% of trades: $152 total ($0.5 a trade) vs $10,454 |
| G5 placebo | FAIL | no placebo.csv supplied (required for a strategy) |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.034 |
| G7 MinTRL | PASS | 304 trades vs MinTRL 76 |
| G8 regime stability | PASS | rho 0.64 (yearly Sharpe 2019 1.2, 2020 1.1, 2021 0.0, 2022 -1.4, 2023 1.2, 2024 1.3, 2025 0.0, 2026 1.1) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.491 vs Gaussian 95% 0.380 (DIFFERS; permutation p 0.001; 7 groups, n 254); P2 VIX regime (past-only median): SIS 0.162 vs Gaussian 95% 0.266 (ok; permutation p 0.397; 2 groups, n 254) |

**Gates: 6/8 pass -> FAIL**

## Standard metrics
```
      trades win avg annual sharpe sortino profit_factor max_dd calmar ulcer ulcer_perf
all      304 38% $34   $770   0.54    1.34          1.66 $1,860   0.41  1.57       0.98
longs    304 38% $34   $770   0.54    1.34          1.66 $1,860   0.41  1.57       0.98
```
## 2023+ bootstrap
```
                     actual       p5      p50      p95
name  metric                                          
all   sharpe           0.85     0.13     0.89     1.60
      sortino          2.29     0.29     2.48     5.42
      pf_day           1.63     1.08     1.69     2.61
      calmar           0.84     0.07     0.91     2.84
      ulcer            1.42     0.68     1.31     3.10
      max_dd       1,860.43 1,027.79 1,772.30 3,433.91
      P(Sharpe<=0)      NaN      NaN     0.03      NaN
longs sharpe           0.85     0.13     0.89     1.60
      sortino          2.29     0.29     2.48     5.42
      pf_day           1.63     1.08     1.69     2.61
      calmar           0.84     0.07     0.91     2.84
      ulcer            1.42     0.68     1.31     3.10
      max_dd       1,860.43 1,027.79 1,772.30 3,433.91
      P(Sharpe<=0)      NaN      NaN     0.03      NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank   dd50   dd95   dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $1,860      55% $1,803 $2,876 $3,463         99%         35%          4%
longs    $1,860      55% $1,803 $2,876 $3,463         99%         35%          4%
```