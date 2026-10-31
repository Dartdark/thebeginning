# Checker report: t_oneside

kind strategy, pre-registered False, variants 5, N (ranked items in TRIALS.csv) 291, t_threshold(N) 3.58

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 4.28, PSR 1.000, DSR(N=291) 0.926 |
| G2 holdout | PASS | 2018-22 $135.2 (t 3.66), 2023-26 $172.3 (t 2.56) |
| G3 years | PASS | 9/9 years positive: 2018 $6,740, 2019 $6,589, 2020 $22,674, 2021 $20,511, 2022 $13,544, 2023 $13,097, 2024 $19,426, 2025 $5,213, 2026 $23,602 |
| G4 concentration | PASS | without the best 5% of trades: $7,316 total ($8.8 a trade) vs $131,397 |
| G5 placebo | PASS | 20 placebo runs, mean $-28.9; share >= real $150.3: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.003 |
| G7 MinTRL | PASS | 874 trades vs MinTRL 120 |
| G8 regime stability | PASS | rho 0.82 (yearly Sharpe 2018 1.4, 2019 1.7, 2020 2.7, 2021 2.1, 2022 1.0, 2023 1.6, 2024 1.8, 2025 0.3, 2026 1.9) |

**Gates: 7/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       874 53% $150 $14,625   1.42    2.47          1.51 $12,335   1.19  2.78      10.52
longs     725 52% $128 $10,347   1.15    1.97          1.44 $14,565   0.71  3.13       6.60
shorts    149 59% $258  $4,278   0.85    1.55          1.78  $7,261   0.59  3.27       2.62
```
## 2023+ bootstrap
```
                       actual       p5       p50       p95
name   metric                                             
all    sharpe            1.29     0.51      1.28      2.06
       sortino           2.23     0.82      2.22      3.93
       pf_day            1.44     1.15      1.43      1.80
       calmar            1.28     0.34      1.26      2.92
       ulcer             6.79     2.55      5.19     12.77
       max_dd       12,335.15 7,836.02 12,307.53 21,559.59
       P(Sharpe<=0)       NaN      NaN      0.00       NaN
longs  sharpe            0.91     0.15      0.91      1.65
       sortino           1.52     0.22      1.53      3.09
       pf_day            1.32     1.04      1.32      1.66
       calmar            0.66     0.07      0.76      2.18
       ulcer             7.01     2.93      6.47     17.24
       max_dd       14,564.95 7,472.48 12,657.21 23,948.74
       P(Sharpe<=0)       NaN      NaN      0.02       NaN
shorts sharpe            1.01     0.20      1.01      1.74
       sortino           1.99     0.30      2.01      4.76
       pf_day            2.05     1.15      2.07      3.97
       calmar            0.84     0.10      0.98      3.46
       ulcer             3.77     1.29      3.36      9.95
       max_dd        7,261.45 2,765.19  5,974.20 12,485.62
       P(Sharpe<=0)       NaN      NaN      0.02       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $12,335      46% $12,654 $19,539 $23,407        100%        100%        100%
longs    $14,565      69% $12,749 $20,354 $24,348        100%        100%        100%
shorts    $7,261      79%  $5,749  $9,362 $11,364        100%        100%        100%
```