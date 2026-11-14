# Checker report: replica_gates

kind strategy, pre-registered False, variants 2, N (ranked items in TRIALS.csv) 487, t_threshold(N) 3.71

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 3.28, PSR 1.000, DSR(N=487) 0.597 |
| G2 holdout | PASS | 2018-22 $0.0 (t 2.42), 2023-26 $0.0 (t 2.29) |
| G3 years | PASS | 8/9 years positive: 2018 $-0, 2019 $0, 2020 $1, 2021 $0, 2022 $0, 2023 $0, 2024 $0, 2025 $0, 2026 $0 |
| G4 concentration | PASS | without the best 5% of trades: $1 total ($0.0 a trade) vs $3 |
| G5 placebo | PASS | 200 placebo runs, mean $0.0; share >= real $0.0: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.032 |
| G7 MinTRL | PASS | 168 trades vs MinTRL 37 |
| G8 regime stability | PASS | rho 0.62 (yearly Sharpe 2018 0.3, 2019 -0.8, 2020 2.2, 2021 0.8, 2022 -0.0, 2023 1.1, 2024 1.7, 2025 0.3, 2026 0.1) |
| G10 fill sanity | PASS | 100.0% of fills inside their 240-min bar (+/- 2 ticks), clock +0 min |
| G11 one-bar delay | PASS | net $548 (t 2.4) -> $547 (t 2.4), Sharpe kept 100% |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.237 vs Gaussian 95% 0.598 (ok; permutation p 0.724; 2 groups, n 47); P2 VIX regime (past-only median): SIS 0.479 vs Gaussian 95% 0.383 (DIFFERS; permutation p 0.009; 2 groups, n 118) |

**Gates: 9/10 pass -> FAIL**

## Standard metrics
```
      trades win avg annual sharpe sortino profit_factor max_dd calmar ulcer ulcer_perf
all      168 54%  $0     $0   0.80    1.59          1.91     $0   0.40  0.00       1.35
longs    168 54%  $0     $0   0.80    1.59          1.91     $0   0.40  0.00       1.35
```
## 2023+ bootstrap
```
                    actual   p5  p50  p95
name  metric                             
all   sharpe          0.98 0.13 0.94 1.60
      sortino         2.26 0.23 2.17 4.75
      pf_day          1.85 1.08 1.82 2.94
      calmar          1.69 0.07 0.99 2.97
      ulcer           0.00 0.00 0.00 0.00
      max_dd          0.12 0.11 0.19 0.38
      P(Sharpe<=0)     NaN  NaN 0.03  NaN
longs sharpe          0.98 0.13 0.94 1.60
      sortino         2.26 0.23 2.17 4.75
      pf_day          1.85 1.08 1.82 2.94
      calmar          1.69 0.07 0.99 2.97
      ulcer           0.00 0.00 0.00 0.00
      max_dd          0.12 0.11 0.19 0.38
      P(Sharpe<=0)     NaN  NaN 0.03  NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank dd50 dd95 dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all          $0       3%   $0   $0   $0          0%          0%          0%
longs        $0       3%   $0   $0   $0          0%          0%          0%
```