# Checker report: twin_continuation

kind strategy, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 201, t_threshold(N) 3.48

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 5.46, PSR 1.000, DSR(N=201) 0.995 |
| G2 holdout | PASS | 2018-22 $188.0 (t 2.66), 2023-26 $468.8 (t 5.03) |
| G3 years | PASS | 8/9 years positive: 2018 $5,660, 2019 $-4,694, 2020 $32,627, 2021 $40,129, 2022 $38,712, 2023 $41,894, 2024 $43,109, 2025 $45,915, 2026 $92,227 |
| G4 concentration | PASS | without the best 5% of trades: $85,813 total ($84.1 a trade) vs $335,578 |
| G5 placebo | PASS | 10 placebo runs, mean $35.3; share >= real $312.5: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.000 |
| G7 MinTRL | PASS | 1074 trades vs MinTRL 110 |
| G8 regime stability | PASS | rho 0.63 (yearly Sharpe 2018 0.4, 2019 -0.6, 2020 1.9, 2021 2.3, 2022 1.2, 2023 2.3, 2024 2.1, 2025 1.9, 2026 3.8) |
| G9 PBO | PASS | CSCV over 17 variants, 16 blocks: PBO 0.26 |

**Gates: 9/9 pass -> PASS**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      1074 68% $312 $36,287   1.76    2.71          1.62 $16,141   2.25  6.10      11.90
longs     590 71% $283 $17,807   1.31    1.89          1.65 $19,251   0.92  4.59       7.75
shorts    484 64% $349 $18,481   1.19    1.93          1.59 $17,337   1.07  8.89       4.16
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe            2.47      1.66      2.46      3.27
       sortino           4.13      2.50      4.12      6.14
       pf_day            1.93      1.55      1.92      2.41
       calmar            4.65      1.77      3.73      6.63
       ulcer             3.00      1.83      3.33      7.34
       max_dd       12,149.26 10,098.04 14,922.42 24,320.91
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
longs  sharpe            1.99      1.17      1.99      2.79
       sortino           3.29      1.70      3.31      5.43
       pf_day            2.08      1.52      2.07      2.89
       calmar            2.76      1.02      2.57      5.28
       ulcer             3.78      1.66      3.38      8.30
       max_dd       11,352.71  7,361.18 11,930.05 20,671.89
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
shorts sharpe            1.52      0.72      1.53      2.34
       sortino           2.54      1.04      2.56      4.61
       pf_day            1.78      1.30      1.78      2.47
       calmar            1.69      0.47      1.63      3.76
       ulcer             4.12      2.43      5.20     13.50
       max_dd       14,884.00  9,254.64 15,344.62 27,425.96
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $12,149       5% $17,220 $26,446 $32,582        100%        100%        100%
longs    $11,353      30% $12,850 $20,227 $24,357        100%        100%        100%
shorts   $14,884      42% $15,631 $24,682 $30,640        100%        100%        100%
```