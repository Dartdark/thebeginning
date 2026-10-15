# Checker report: vb_single_print_filter_replica

kind filter, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 193, t_threshold(N) 3.47

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | kept $128.4 (n 1227) vs skipped $11.1 (n 529), t 2.43 |
| G2 holdout | PASS | kept - skipped: 2018-22 $+83.7, 2023-26 $+151.2 |
| G3 years | PASS | kept beats skipped in 7/9 years: 2018 -30, 2019 +5, 2020 +247, 2021 +97, 2022 +62, 2023 +214, 2024 +227, 2025 -14, 2026 +169 |
| G5 placebo | PASS | labels shuffled within years (2,000): p 0.0075 |
| G6 resampling | PASS | kept trades 2023+ P(Sharpe <= 0) 0.000 |

**Gates: 5/5 pass -> PASS**

## Standard metrics
```
           trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all trades   1756 66%  $93 $18,017   1.38    2.12          1.27 $11,748   1.53  2.95      12.20
kept         1227 68% $128 $17,369   1.56    2.48          1.40 $11,672   1.49  2.61      13.33
kept longs   1227 68% $128 $17,369   1.56    2.48          1.40 $11,672   1.49  2.61      13.33
```
## 2023+ bootstrap
```
                           actual       p5       p50       p95
name       metric                                             
all trades sharpe            1.46     0.74      1.49      2.27
           sortino           2.25     1.07      2.30      3.69
           pf_day            1.42     1.19      1.44      1.75
           calmar            1.93     0.53      1.54      3.28
           ulcer             4.32     2.84      5.31     12.28
           max_dd       11,747.75 9,565.65 14,757.88 25,001.39
           P(Sharpe<=0)       NaN      NaN      0.00       NaN
kept       sharpe            1.72     0.95      1.74      2.54
           sortino           2.74     1.41      2.78      4.43
           pf_day            1.63     1.31      1.64      2.08
           calmar            1.99     0.73      1.94      3.99
           ulcer             3.44     2.14      4.06      9.47
           max_dd       11,672.00 7,587.50 12,039.12 20,732.59
           P(Sharpe<=0)       NaN      NaN      0.00       NaN
kept longs sharpe            1.72     0.95      1.74      2.54
           sortino           2.74     1.41      2.78      4.43
           pf_day            1.63     1.31      1.64      2.08
           calmar            1.99     0.73      1.94      3.99
           ulcer             3.44     2.14      4.06      9.47
           max_dd       11,672.00 7,587.50 12,039.12 20,732.59
           P(Sharpe<=0)       NaN      NaN      0.00       NaN
```
## 2023+ drawdown permutation
```
           actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all trades   $11,748       8% $15,830 $24,930 $30,649        100%        100%        100%
kept         $11,672      37% $12,612 $19,375 $24,877        100%        100%        100%
kept longs   $11,672      37% $12,612 $19,375 $24,877        100%        100%        100%
```