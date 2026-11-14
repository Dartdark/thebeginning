# Checker report: mc_es_dip_buy

kind strategy, pre-registered False, variants 4, N (ranked items in TRIALS.csv) 487, t_threshold(N) 3.71

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 2.86, PSR 1.000, DSR(N=487) 0.413 |
| G2 holdout | PASS | 2018-22 $34.4 (t 2.08), 2023-26 $50.3 (t 1.98) |
| G3 years | PASS | 9/9 years positive: 2018 $157, 2019 $1,295, 2020 $1,937, 2021 $2,567, 2022 $1,129, 2023 $2,526, 2024 $2,395, 2025 $1,975, 2026 $705 |
| G4 concentration | FAIL | without the best 5% of trades: $-1,807 total ($-5.3 a trade) vs $14,687 |
| G5 placebo | FAIL | no placebo.csv supplied (required for a strategy) |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.024 |
| G7 MinTRL | PASS | 357 trades vs MinTRL 84 |
| G8 regime stability | PASS | rho 0.73 (yearly Sharpe 2018 0.3, 2019 1.6, 2020 1.4, 2021 1.4, 2022 0.6, 2023 1.5, 2024 1.0, 2025 1.1, 2026 -0.4) |
| G10 fill sanity | PASS | 100.0% of fills inside their 60-min bar (+/- 2 ticks), clock +0 min |
| G11 one-bar delay | PASS | net $481 (t 3.2) -> $447 (t 3.0), Sharpe kept 94% |
| G13 invariance | PASS | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.254 vs Gaussian 95% 0.351 (ok; permutation p 0.628; 8 groups, n 307); P2 VIX regime (past-only median): SIS 0.184 vs Gaussian 95% 0.241 (ok; permutation p 0.168; 2 groups, n 307) |

**Gates: 7/10 pass -> FAIL**

## Standard metrics
```
       trades win avg annual sharpe sortino profit_factor max_dd calmar ulcer ulcer_perf
all       357 35% $41 $1,501   0.92    2.30          1.60 $1,499   1.00  0.83       3.60
longs     226 41% $64 $1,448   0.95    2.51          1.87 $1,723   0.84  0.76       3.81
shorts    131 26%  $1    $53   0.09    0.18          1.02 $1,602   0.03  1.59       0.07
```
## 2023+ bootstrap
```
                      actual     p5      p50      p95
name   metric                                        
all    sharpe           0.86   0.16     0.89     1.49
       sortino          2.06   0.31     2.16     4.45
       pf_day           1.52   1.08     1.54     2.15
       calmar           1.01   0.08     0.95     2.67
       ulcer            0.86   0.56     1.12     2.77
       max_dd       1,498.66 960.03 1,659.96 3,255.12
       P(Sharpe<=0)      NaN    NaN     0.02      NaN
longs  sharpe           0.84   0.09     0.87     1.48
       sortino          2.07   0.17     2.14     4.82
       pf_day           1.64   1.05     1.66     2.56
       calmar           0.81   0.05     0.88     2.71
       ulcer            0.92   0.56     1.14     2.90
       max_dd       1,723.46 889.47 1,597.62 3,190.04
       P(Sharpe<=0)      NaN    NaN     0.04      NaN
shorts sharpe           0.21  -0.58     0.21     0.84
       sortino          0.42  -0.93     0.42     2.10
       pf_day           1.16   0.65     1.16     1.84
       calmar           0.20  -0.20     0.15     1.17
       ulcer            0.55   0.34     0.75     1.91
       max_dd         607.03 444.45   838.45 1,712.83
       P(Sharpe<=0)      NaN    NaN     0.31      NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank   dd50   dd95   dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all       $1,499      24% $1,809 $2,917 $3,510         99%         36%          4%
longs     $1,723      57% $1,646 $2,679 $3,104         98%         25%          2%
shorts      $607       7%   $912 $1,446 $1,713         38%          0%          0%
```