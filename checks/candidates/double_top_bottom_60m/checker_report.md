# Checker report: double_top_bottom_60m

kind strategy, pre-registered False, variants 33, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 2.77, PSR 1.000, DSR(N=374) 0.408 |
| G2 holdout | PASS | 2018-22 $212.6 (t 2.69), 2023-26 $234.4 (t 1.52) |
| G3 years | PASS | 8/9 years positive: 2018 $4,647, 2019 $1,928, 2020 $2,773, 2021 $35,002, 2022 $50,480, 2023 $-12,053, 2024 $32,422, 2025 $52,851, 2026 $6,007 |
| G4 concentration | FAIL | without the best 5% of trades: $-78,129 total ($-105.0 a trade) vs $174,056 |
| G5 placebo | PASS | 200 placebo runs, mean $-2.2; share >= real $222.0: 0.005 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.038 |
| G7 MinTRL | PASS | 784 trades vs MinTRL 194 |
| G8 regime stability | PASS | rho 0.65 (yearly Sharpe 2018 0.5, 2019 0.3, 2020 0.1, 2021 2.1, 2022 2.3, 2023 -0.8, 2024 1.5, 2025 1.4, 2026 0.3) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.271 vs Gaussian 95% 0.251 (DIFFERS; permutation p 0.029; 9 groups, n 734); P2 VIX regime (past-only median): SIS 0.285 vs Gaussian 95% 0.162 (DIFFERS; permutation p 0.001; 2 groups, n 734) |

**Gates: 6/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       784 50% $222 $19,062   0.93    1.89          1.37 $19,942   0.96  5.72       6.67
longs     384 54% $187  $7,853   0.51    1.10          1.32 $18,435   0.43 10.28       1.53
shorts    400 47% $256 $11,209   0.79    1.60          1.41 $28,490   0.39  5.72       3.92
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe            0.78      0.09      0.86      1.51
       sortino           1.76      0.16      1.93      4.18
       pf_day            1.36      1.03      1.39      1.86
       calmar            1.19      0.05      0.82      2.46
       ulcer            12.71      4.33     10.36     32.24
       max_dd       16,691.79 15,352.87 26,035.02 49,035.81
       P(Sharpe<=0)       NaN       NaN      0.04       NaN
longs  sharpe            0.77      0.14      0.81      1.32
       sortino           2.16      0.27      2.15      5.03
       pf_day            1.63      1.07      1.63      2.55
       calmar            1.82      0.09      1.00      3.20
       ulcer             6.21      2.96      7.05     19.81
       max_dd        8,642.96  8,652.84 15,173.29 27,994.97
       P(Sharpe<=0)       NaN       NaN      0.03       NaN
shorts sharpe            0.26     -0.54      0.32      1.09
       sortino           0.48     -0.86      0.62      2.41
       pf_day            1.11      0.81      1.14      1.58
       calmar            0.15     -0.17      0.21      1.20
       ulcer            16.46      5.94     16.08     47.94
       max_dd       28,490.11 14,105.27 25,944.43 51,903.64
       P(Sharpe<=0)       NaN       NaN      0.26       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $16,692       3% $26,612 $42,977 $51,893        100%        100%        100%
longs     $8,643       0% $16,074 $25,857 $31,540        100%        100%        100%
shorts   $28,490      55% $27,462 $43,475 $50,765        100%        100%        100%
```