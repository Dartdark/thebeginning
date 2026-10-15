# Checker report: twin_continuation_replica

kind strategy, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 193, t_threshold(N) 3.47

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 5.46, PSR 1.000, DSR(N=193) 0.995 |
| G2 holdout | PASS | 2018-22 $185.5 (t 2.63), 2023-26 $469.6 (t 5.05) |
| G3 years | PASS | 8/9 years positive: 2018 $4,217, 2019 $-4,694, 2020 $32,627, 2021 $40,087, 2022 $38,712, 2023 $41,894, 2024 $43,960, 2025 $45,934, 2026 $92,227 |
| G4 concentration | PASS | without the best 5% of trades: $85,198 total ($83.4 a trade) vs $334,963 |
| G5 placebo | PASS | 10 placebo runs, mean $55.6; share >= real $311.6: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.000 |

**Gates: 6/6 pass -> PASS**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      1075 68% $312 $36,220   1.75    2.71          1.61 $16,141   2.24  6.78      10.69
longs     592 71% $282 $17,833   1.31    1.89          1.65 $19,251   0.93  4.60       7.76
shorts    483 64% $348 $18,386   1.19    1.92          1.59 $17,337   1.06  9.83       3.74
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe            2.48      1.67      2.47      3.28
       sortino           4.15      2.53      4.13      6.18
       pf_day            1.93      1.55      1.93      2.43
       calmar            4.67      1.79      3.75      6.66
       ulcer             2.99      1.83      3.32      7.34
       max_dd       12,149.26 10,098.04 14,922.42 24,319.95
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
longs  sharpe            2.00      1.17      1.99      2.79
       sortino           3.30      1.71      3.32      5.44
       pf_day            2.08      1.52      2.08      2.89
       calmar            2.77      1.03      2.58      5.29
       ulcer             3.78      1.65      3.38      8.30
       max_dd       11,352.71  7,361.18 11,930.05 20,671.89
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
shorts sharpe            1.53      0.73      1.54      2.35
       sortino           2.56      1.06      2.59      4.67
       pf_day            1.78      1.31      1.78      2.49
       calmar            1.70      0.47      1.65      3.78
       ulcer             4.11      2.43      5.17     13.41
       max_dd       14,884.00  9,254.54 15,334.96 27,389.63
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $12,149       5% $17,155 $26,421 $32,582        100%        100%        100%
longs    $11,353      29% $12,973 $20,306 $24,788        100%        100%        100%
shorts   $14,884      43% $15,556 $24,656 $30,640        100%        100%        100%
```