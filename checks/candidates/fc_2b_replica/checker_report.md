# Checker report: fc_2b_replica

kind strategy, pre-registered False, variants 40, N (ranked items in TRIALS.csv) 282, t_threshold(N) 3.57

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 3.82, PSR 1.000, DSR(N=282) 0.845 |
| G2 holdout | PASS | 2018-22 $290.2 (t 3.65), 2023-26 $220.3 (t 1.84) |
| G3 years | PASS | 9/9 years positive: 2018 $16,162, 2019 $8,699, 2020 $15,678, 2021 $31,945, 2022 $55,792, 2023 $3,363, 2024 $28,705, 2025 $25,765, 2026 $13,093 |
| G4 concentration | FAIL | without the best 5% of trades: $-4,761 total ($-6.6 a trade) vs $199,201 |
| G5 placebo | PASS | 300 placebo runs, mean $89.6; share >= real $260.7: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.030 |
| G7 MinTRL | PASS | 764 trades vs MinTRL 124 |
| G8 regime stability | PASS | rho 0.81 (yearly Sharpe 2018 1.3, 2019 1.0, 2020 0.9, 2021 2.1, 2022 2.4, 2023 0.2, 2024 1.5, 2025 1.3, 2026 0.7) |
| G9 PBO | PASS | CSCV over 16 variants, 16 blocks: PBO 0.45 |

**Gates: 7/9 pass -> FAIL**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       764 60% $261 $21,930   1.26    2.42          1.48 $17,430   1.26  3.24      13.55
longs     377 62% $292 $12,100   1.02    1.91          1.54 $14,838   0.82  4.57       5.29
shorts    387 59% $231  $9,831   0.77    1.52          1.42 $21,697   0.45  6.62       2.97
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe            0.93      0.15      0.92      1.64
       sortino           1.80      0.26      1.78      3.57
       pf_day            1.34      1.05      1.34      1.71
       calmar            1.04      0.08      0.81      2.31
       ulcer             9.67      4.13      9.22     27.05
       max_dd       17,429.50 13,249.59 21,837.62 40,257.50
       P(Sharpe<=0)       NaN       NaN      0.03       NaN
longs  sharpe            1.00      0.17      0.99      1.67
       sortino           1.99      0.30      1.96      3.79
       pf_day            1.55      1.08      1.54      2.13
       calmar            0.91      0.10      0.95      2.63
       ulcer             6.22      3.12      6.53     18.70
       max_dd       14,838.50  8,063.50 13,802.12 26,222.65
       P(Sharpe<=0)       NaN       NaN      0.02       NaN
shorts sharpe            0.33     -0.57      0.34      1.12
       sortino           0.63     -0.91      0.64      2.58
       pf_day            1.16      0.77      1.17      1.72
       calmar            0.21     -0.18      0.21      1.26
       ulcer            21.00      5.59     14.87     45.64
       max_dd       21,697.25 12,209.05 22,867.75 46,315.99
       P(Sharpe<=0)       NaN       NaN      0.26       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $17,430      17% $22,149 $35,136 $43,887        100%        100%        100%
longs    $14,838      58% $13,962 $22,439 $26,890        100%        100%        100%
shorts   $21,697      50% $21,647 $34,125 $40,030        100%        100%        100%
```