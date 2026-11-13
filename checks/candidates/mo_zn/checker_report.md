# Checker report: mo_zn

kind strategy, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t -1.33, PSR 0.100, DSR(N=374) 0.000 |
| G2 holdout | FAIL | 2018-22 $-38.0 (t -1.42), 2023-26 $-8.4 (t -0.44) |
| G3 years | FAIL | 3/9 years positive: 2018 $75, 2019 $-240, 2020 $182, 2021 $-968, 2022 $-2,389, 2023 $-1,732, 2024 $-1,030, 2025 $2,062, 2026 $-287 |
| G4 concentration | FAIL | without the best 5% of trades: $-9,726 total ($-49.9 a trade) vs $-4,328 |
| G5 placebo | FAIL | no placebo.csv supplied (required for a strategy) |
| G6 resampling | FAIL | 2023+ P(Sharpe <= 0) 0.617 |
| G7 MinTRL | FAIL | 206 trades vs MinTRL inf |
| G8 regime stability | FAIL | rho 0.33 (yearly Sharpe 2018 0.2, 2019 -0.2, 2020 0.3, 2021 -1.7, 2022 -1.3, 2023 -1.2, 2024 -1.1, 2025 1.9, 2026 -0.4) |
| G13 invariance | CONCERN | outcome = net / risk; P3 time (years): SIS 0.429 vs Gaussian 95% 0.414 (DIFFERS; permutation p 0.023; 4 groups, n 134); P2 VIX regime (past-only median): SIS 0.167 vs Gaussian 95% 0.299 (ok; permutation p 0.440; 2 groups, n 206) |

**Gates: 0/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg annual sharpe sortino profit_factor max_dd calmar ulcer ulcer_perf
all       206 40% $-21  $-477  -0.44   -0.64          0.80 $6,707  -0.07  7.05      -0.14
longs      89 36% $-34  $-338  -0.45   -0.65          0.70 $4,317  -0.08  4.81      -0.14
shorts    117 43% $-11  $-140  -0.18   -0.26          0.89 $3,147  -0.04  3.27      -0.09
```
## 2023+ bootstrap
```
                      actual       p5      p50      p95
name   metric                                          
all    sharpe          -0.22    -0.95    -0.14     0.63
       sortino         -0.33    -1.28    -0.21     1.03
       pf_day           0.91     0.66     0.94     1.31
       calmar          -0.08    -0.23    -0.06     0.50
       ulcer            3.59     0.95     2.43     5.76
       max_dd       3,215.63 1,212.75 2,509.84 4,954.13
       P(Sharpe<=0)      NaN      NaN     0.62      NaN
longs  sharpe          -0.12    -0.92    -0.11     0.65
       sortino         -0.17    -1.18    -0.17     1.15
       pf_day           0.93     0.54     0.93     1.54
       calmar          -0.06    -0.24    -0.06     0.58
       ulcer            1.64     0.59     1.48     3.61
       max_dd       1,580.00   780.59 1,576.41 3,166.22
       P(Sharpe<=0)      NaN      NaN     0.61      NaN
shorts sharpe          -0.20    -0.90    -0.10     0.62
       sortino         -0.29    -1.16    -0.15     1.05
       pf_day           0.89     0.60     0.95     1.43
       calmar          -0.09    -0.23    -0.05     0.56
       ulcer            2.24     0.62     1.63     3.95
       max_dd       1,773.75   788.69 1,645.63 3,360.37
       P(Sharpe<=0)      NaN      NaN     0.58      NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank   dd50   dd95   dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all       $3,216      78% $2,682 $3,952 $4,508        100%         89%         32%
longs     $1,580      46% $1,618 $2,416 $2,766         97%         21%          0%
shorts    $1,774      40% $1,895 $2,751 $3,101        100%         41%          2%
```