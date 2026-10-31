# Checker report: fvb

kind strategy, pre-registered False, variants 27, N (ranked items in TRIALS.csv) 291, t_threshold(N) 3.58

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 3.82, PSR 1.000, DSR(N=291) 0.854 |
| G2 holdout | PASS | 2018-22 $126.5 (t 2.86), 2023-26 $216.3 (t 2.66) |
| G3 years | PASS | 9/9 years positive: 2018 $34,032, 2019 $14,759, 2020 $18,388, 2021 $30,442, 2022 $55,151, 2023 $20,498, 2024 $72,686, 2025 $81,829, 2026 $28,786 |
| G4 concentration | FAIL | without the best 5% of trades: $-335,604 total ($-164.4 a trade) vs $356,572 |
| G5 placebo | PASS | 500 placebo runs, mean $59.2; share >= real $165.8: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.000 |
| G7 MinTRL | PASS | 2150 trades vs MinTRL 313 |
| G8 regime stability | PASS | rho 0.85 (yearly Sharpe 2018 2.0, 2019 1.2, 2020 0.8, 2021 1.3, 2022 1.5, 2023 0.8, 2024 2.1, 2025 1.9, 2026 0.7) |

**Gates: 6/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      2150 29% $166 $39,324   1.28    2.83          1.29 $28,174   1.40  3.46      22.74
longs    1335 30%  $75 $11,064   0.53    1.10          1.13 $31,359   0.35  5.25       4.21
shorts    815 29% $314 $28,261   1.23    3.64          1.55 $21,202   1.33  6.85       8.25
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe            1.36      0.67      1.38      2.07
       sortino           3.08      1.38      3.14      5.18
       pf_day            1.33      1.15      1.34      1.57
       calmar            1.85      0.47      1.51      3.32
       ulcer             6.66      4.15      8.51     23.01
       max_dd       28,174.50 22,176.35 34,981.75 60,072.70
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
longs  sharpe            0.43     -0.37      0.43      1.14
       sortino           0.90     -0.70      0.88      2.59
       pf_day            1.11      0.92      1.10      1.31
       calmar            0.35     -0.14      0.29      1.28
       ulcer            10.07      7.38     18.61     60.29
       max_dd       31,359.25 20,836.50 37,538.62 72,951.14
       P(Sharpe<=0)       NaN       NaN      0.18       NaN
shorts sharpe            1.41      0.70      1.43      2.07
       sortino           4.43      1.89      4.54      7.55
       pf_day            1.68      1.28      1.69      2.18
       calmar            1.95      0.53      1.83      4.18
       ulcer            12.02      3.05      6.66     17.35
       max_dd       21,202.25 14,198.36 22,859.88 39,157.49
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $28,174      14% $36,267 $57,834 $69,175        100%        100%        100%
longs    $31,359      19% $39,219 $61,580 $72,730        100%        100%        100%
shorts   $21,202      44% $21,901 $34,442 $41,720        100%        100%        100%
```