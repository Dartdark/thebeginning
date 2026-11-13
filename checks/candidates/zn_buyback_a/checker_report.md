# Checker report: zn_buyback_a

kind strategy, pre-registered True, variants 2, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 0.91, PSR 0.811, DSR(N=374) 0.022 |
| G2 holdout | FAIL | 2018-22 $nan (t nan), 2023-26 $23.2 (t 0.91) |
| G3 years | PASS | 2/3 years positive: 2024 $18, 2025 $1,332, 2026 $-282 |
| G4 concentration | PASS | without the best 5% of trades: $19 total ($0.5 a trade) vs $1,067 |
| G5 placebo | PASS | 50 placebo runs, mean $-39.4; share >= real $23.2: 0.000 |
| G6 resampling | FAIL | 2023+ P(Sharpe <= 0) 0.292 |
| G7 MinTRL | FAIL | 46 trades vs MinTRL 158 |
| G8 regime stability | FAIL | rho 0.53 (yearly Sharpe 2024 0.0, 2025 1.9, 2026 -0.4) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; ; not evaluable: P3 time (years), P2 VIX regime (past-only median) |

**Gates: 3/8 pass -> FAIL**

## Standard metrics
```
      trades win avg annual sharpe sortino profit_factor max_dd calmar ulcer ulcer_perf
all       46 52% $23   $451   0.59    0.91          1.41 $1,216   0.37  0.98       0.92
longs     46 52% $23   $451   0.59    0.91          1.41 $1,216   0.37  0.98       0.92
```
## 2023+ bootstrap
```
                     actual     p5    p50      p95
name  metric                                      
all   sharpe           0.59  -0.76   0.39     1.52
      sortino          0.91  -0.93   0.59     3.15
      pf_day           1.41   0.63   1.26     2.57
      calmar           0.37  -0.33   0.32     2.27
      ulcer            0.98   0.28   0.78     2.17
      max_dd       1,216.25 430.59 912.81 1,961.97
      P(Sharpe<=0)      NaN    NaN   0.29      NaN
longs sharpe           0.59  -0.76   0.39     1.52
      sortino          0.91  -0.93   0.59     3.15
      pf_day           1.41   0.63   1.26     2.57
      calmar           0.37  -0.33   0.32     2.27
      ulcer            0.98   0.28   0.78     2.17
      max_dd       1,216.25 430.59 912.81 1,961.97
      P(Sharpe<=0)      NaN    NaN   0.29      NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank dd50   dd95   dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $1,216      91% $817 $1,320 $1,549         24%          0%          0%
longs    $1,216      91% $817 $1,320 $1,549         24%          0%          0%
```