# Checker report: btc_adx_ensemble

kind strategy, pre-registered False, variants 12, N (ranked items in TRIALS.csv) 487, t_threshold(N) 3.71

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 5.61, PSR 1.000, DSR(N=487) 0.997 |
| G2 holdout | PASS | 2018-22 $0.3 (t 4.90), 2023-26 $0.2 (t 2.93) |
| G3 years | PASS | 9/9 years positive: 2018 $7, 2019 $57, 2020 $39, 2021 $18, 2022 $7, 2023 $29, 2024 $15, 2025 $13, 2026 $10 |
| G4 concentration | PASS | without the best 5% of trades: $86 total ($0.1 a trade) vs $195 |
| G5 placebo | PASS | 40 placebo runs, mean $0.0; share >= real $0.3: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.021 |
| G7 MinTRL | PASS | 773 trades vs MinTRL 59 |
| G8 regime stability | PASS | rho 0.81 (yearly Sharpe 2018 1.6, 2019 2.6, 2020 1.7, 2021 1.3, 2022 0.3, 2023 1.1, 2024 1.3, 2025 0.9, 2026 1.1) |
| G13 invariance | PASS | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.200 vs Gaussian 95% 0.235 (ok; permutation p 0.188; 8 groups, n 723); P2 VIX regime (past-only median): SIS 0.151 vs Gaussian 95% 0.155 (ok; permutation p 0.058; 2 groups, n 723) |

**Gates: 8/8 pass -> PASS**

## Standard metrics
```
       trades win avg annual sharpe sortino profit_factor max_dd calmar ulcer ulcer_perf
all       773 39%  $0    $19   1.34    3.49          1.67    $10   1.89  0.01       5.81
longs     385 42%  $0    $14   1.21    3.49          1.88    $10   1.30  0.01       3.97
shorts    388 35%  $0     $6   0.63    1.52          1.46    $13   0.45  0.01       1.30
```
## 2023+ bootstrap
```
                     actual    p5   p50   p95
name   metric                                
all    sharpe          1.04  0.24  1.08  1.74
       sortino         2.74  0.50  2.81  5.53
       pf_day          1.59  1.11  1.62  2.27
       calmar          1.73  0.13  1.02  2.89
       ulcer           0.01  0.01  0.01  0.03
       max_dd          9.13  9.07 15.53 28.65
       P(Sharpe<=0)     NaN   NaN  0.02   NaN
longs  sharpe          1.12  0.34  1.16  1.81
       sortino         3.23  0.72  3.32  6.51
       pf_day          1.98  1.21  2.02  3.16
       calmar          1.90  0.20  1.32  3.62
       ulcer           0.01  0.00  0.01  0.02
       max_dd          7.22  6.04 10.31 19.14
       P(Sharpe<=0)     NaN   NaN  0.01   NaN
shorts sharpe          0.23 -0.79  0.22  0.95
       sortino         0.56 -1.32  0.51  2.95
       pf_day          1.16  0.64  1.15  1.88
       calmar          0.19 -0.21  0.13  1.10
       ulcer           0.01  0.01  0.01  0.03
       max_dd         11.13  7.78 14.71 28.96
       P(Sharpe<=0)     NaN   NaN  0.33   NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank dd50 dd95 dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all           $9       5%  $14  $22  $26          0%          0%          0%
longs         $7      17%   $9  $15  $17          0%          0%          0%
shorts       $11      24%  $14  $21  $24          0%          0%          0%
```