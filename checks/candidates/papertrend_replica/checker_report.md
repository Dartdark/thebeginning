# Checker report: papertrend_replica

kind strategy, pre-registered False, variants 39, N (ranked items in TRIALS.csv) 291, t_threshold(N) 3.58

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 4.05, PSR 1.000, DSR(N=291) 0.865 |
| G2 holdout | PASS | 2018-22 $363.5 (t 3.55), 2023-26 $384.9 (t 2.30) |
| G3 years | PASS | 8/9 years positive: 2018 $14,868, 2019 $-5,001, 2020 $19,242, 2021 $39,292, 2022 $49,002, 2023 $7,412, 2024 $36,641, 2025 $1,028, 2026 $45,376 |
| G4 concentration | PASS | without the best 5% of trades: $56,818 total ($107.2 a trade) vs $207,860 |
| G5 placebo | PASS | 500 placebo runs, mean $-5.2; share >= real $372.5: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.003 |
| G7 MinTRL | PASS | 558 trades vs MinTRL 103 |
| G8 regime stability | PASS | rho 0.63 (yearly Sharpe 2018 1.8, 2019 -0.8, 2020 1.1, 2021 2.8, 2022 2.1, 2023 0.5, 2024 1.7, 2025 0.1, 2026 2.2) |

**Gates: 7/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       558 60% $373 $22,894   1.33    2.07          1.67 $27,768   0.82  5.35       8.56
longs     315 63% $329 $11,423   0.96    1.42          1.67 $23,508   0.49  6.96       3.28
shorts    243 56% $429 $11,470   0.92    1.52          1.66 $18,981   0.60  5.65       4.06
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe            1.16      0.39      1.17      1.93
       sortino           1.83      0.57      1.85      3.47
       pf_day            1.51      1.15      1.51      2.02
       calmar            1.45      0.25      1.17      2.84
       ulcer             7.47      3.29      7.31     18.83
       max_dd       16,007.50 12,127.40 19,702.75 35,188.66
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
longs  sharpe            0.83      0.09      0.84      1.60
       sortino           1.23      0.11      1.25      2.83
       pf_day            1.50      1.04      1.51      2.24
       calmar            0.53      0.05      0.77      2.25
       ulcer            17.32      3.00      7.46     21.99
       max_dd       23,507.75  9,144.50 16,127.38 31,563.02
       P(Sharpe<=0)       NaN       NaN      0.03       NaN
shorts sharpe            0.80     -0.07      0.79      1.60
       sortino           1.41     -0.10      1.40      3.51
       pf_day            1.51      0.97      1.50      2.36
       calmar            0.58     -0.03      0.64      2.19
       ulcer             8.34      3.43      8.46     25.87
       max_dd       18,552.50  8,818.34 16,432.12 32,657.90
       P(Sharpe<=0)       NaN       NaN      0.06       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $16,008      11% $21,818 $34,515 $42,196        100%        100%        100%
longs    $23,508      80% $18,419 $29,314 $36,132        100%        100%        100%
shorts   $18,552      74% $15,491 $24,856 $29,838        100%        100%        100%
```