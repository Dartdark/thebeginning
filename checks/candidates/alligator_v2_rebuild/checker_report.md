# Checker report: alligator_v2_rebuild

kind strategy, pre-registered True, variants 2160, N (ranked items in TRIALS.csv) 487, t_threshold(N) 3.71

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 3.32, PSR 0.998, DSR(N=487) 0.591 |
| G2 holdout | PASS | 2018-22 $0.0 (t 2.76), 2023-26 $0.0 (t 1.88) |
| G3 years | PASS | 8/9 years positive: 2018 $0, 2019 $0, 2020 $0, 2021 $-0, 2022 $0, 2023 $0, 2024 $0, 2025 $0, 2026 $0 |
| G4 concentration | PASS | without the best 5% of trades: $1 total ($0.0 a trade) vs $1 |
| G5 placebo | PASS | 300 placebo runs, mean $-0.0; share >= real $0.0: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.044 |
| G7 MinTRL | PASS | 352 trades vs MinTRL 118 |
| G8 regime stability | PASS | rho 0.77 (yearly Sharpe 2018 3.1, 2019 1.5, 2020 1.7, 2021 0.2, 2022 1.0, 2023 2.0, 2024 0.6, 2025 0.4, 2026 0.7) |
| G13 invariance | PASS | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.280 vs Gaussian 95% 0.352 (ok; permutation p 0.621; 8 groups, n 302); P2 VIX regime (past-only median): SIS 0.183 vs Gaussian 95% 0.244 (ok; permutation p 0.286; 2 groups, n 302) |

**Gates: 7/8 pass -> FAIL**

## Standard metrics
```
       trades win avg annual sharpe sortino profit_factor max_dd calmar ulcer ulcer_perf
all       352 70%  $0     $0   1.13    1.84          1.56     $0   1.13  0.00       3.96
longs     191 69%  $0     $0   0.75    1.18          1.46     $0   0.44  0.00       1.51
shorts    161 71%  $0     $0   0.85    1.41          1.64     $0   0.70  0.00       2.77
```
## 2023+ bootstrap
```
                     actual    p5  p50  p95
name   metric                              
all    sharpe          0.92  0.04 0.94 1.85
       sortino         1.40  0.05 1.43 3.28
       pf_day          1.49  1.02 1.50 2.28
       calmar          1.44  0.02 0.73 2.24
       ulcer           0.00  0.00 0.00 0.00
       max_dd          0.06  0.07 0.12 0.23
       P(Sharpe<=0)     NaN   NaN 0.04  NaN
longs  sharpe          0.36 -0.49 0.38 1.31
       sortino         0.52 -0.61 0.55 2.31
       pf_day          1.23  0.75 1.24 2.14
       calmar          0.30 -0.17 0.24 1.48
       ulcer           0.00  0.00 0.00 0.00
       max_dd          0.08  0.05 0.11 0.22
       P(Sharpe<=0)     NaN   NaN 0.23  NaN
shorts sharpe          0.94  0.09 0.96 1.75
       sortino         1.54  0.13 1.56 3.73
       pf_day          1.88  1.06 1.90 3.57
       calmar          1.44  0.05 0.89 2.78
       ulcer           0.00  0.00 0.00 0.00
       max_dd          0.04  0.04 0.07 0.14
       P(Sharpe<=0)     NaN   NaN 0.04  NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank dd50 dd95 dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all           $0       0%   $0   $0   $0          0%          0%          0%
longs         $0      19%   $0   $0   $0          0%          0%          0%
shorts        $0       2%   $0   $0   $0          0%          0%          0%
```