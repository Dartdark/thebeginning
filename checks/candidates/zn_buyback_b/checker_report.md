# Checker report: zn_buyback_b

kind strategy, pre-registered True, variants 2, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t -4.11, PSR 0.000, DSR(N=374) 0.000 |
| G2 holdout | FAIL | 2018-22 $nan (t nan), 2023-26 $-31.2 (t -4.11) |
| G3 years | FAIL | 0/3 years positive: 2024 $-217, 2025 $-278, 2026 $-939 |
| G4 concentration | FAIL | without the best 5% of trades: $-1,606 total ($-37.3 a trade) vs $-1,433 |
| G5 placebo | FAIL | 50 placebo runs, mean $-34.8; share >= real $-31.2: 0.300 |
| G6 resampling | FAIL | 2023+ P(Sharpe <= 0) 1.000 |
| G7 MinTRL | FAIL | 46 trades vs MinTRL inf |
| G8 regime stability | FAIL | rho 0.18 (yearly Sharpe 2024 -1.9, 2025 -1.6, 2026 -3.2) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; ; not evaluable: P3 time (years), P2 VIX regime (past-only median) |

**Gates: 0/8 pass -> FAIL**

## Standard metrics
```
      trades win  avg annual sharpe sortino profit_factor max_dd calmar ulcer ulcer_perf
all       46 17% $-31  $-606  -2.33   -2.40          0.16 $1,397  -0.43  1.12      -1.08
longs     46 17% $-31  $-606  -2.33   -2.40          0.16 $1,397  -0.43  1.12      -1.08
```
## 2023+ bootstrap
```
                     actual     p5      p50      p95
name  metric                                        
all   sharpe          -2.33  -3.01    -2.36    -1.53
      sortino         -2.40  -3.01    -2.46    -1.72
      pf_day           0.16   0.07     0.18     0.36
      calmar          -0.43  -0.42    -0.42    -0.38
      ulcer            1.12   0.82     1.42     2.06
      max_dd       1,396.88 751.22 1,241.56 1,761.50
      P(Sharpe<=0)      NaN    NaN     1.00      NaN
longs sharpe          -2.33  -3.01    -2.36    -1.53
      sortino         -2.40  -3.01    -2.46    -1.72
      pf_day           0.16   0.07     0.18     0.36
      calmar          -0.43  -0.42    -0.42    -0.38
      ulcer            1.12   0.82     1.42     2.06
      max_dd       1,396.88 751.22 1,241.56 1,761.50
      P(Sharpe<=0)      NaN    NaN     1.00      NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank   dd50   dd95   dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $1,433       0% $1,439 $1,523 $1,564        100%          0%          0%
longs    $1,433       0% $1,439 $1,523 $1,564        100%          0%          0%
```