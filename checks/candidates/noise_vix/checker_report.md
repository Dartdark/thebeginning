# Checker report: noise_vix

kind filter, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | kept $40.8 (n 1394) vs skipped $87.9 (n 1189), t -2.09 |
| G2 holdout | FAIL | kept - skipped: 2018-22 $-30.8, 2023-26 $-63.2 |
| G3 years | FAIL | kept beats skipped in 3/9 years: 2018 -3, 2019 +11, 2020 -32, 2021 +13, 2022 -120, 2023 +29, 2024 -14, 2025 -36, 2026 -216 |
| G5 placebo | FAIL | labels shuffled within years (2,000): p 0.9795 |
| G6 resampling | PASS | kept trades 2023+ P(Sharpe <= 0) 0.029 |
| G7 MinTRL | PASS | 1394 trades vs MinTRL 637 |
| G8 regime stability | PASS | rho 0.64 (yearly Sharpe 2018 0.5, 2019 0.5, 2020 0.1, 2021 1.9, 2022 0.2, 2023 2.2, 2024 0.9, 2025 1.7, 2026 -1.1) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.268 vs Gaussian 95% 0.190 (DIFFERS; permutation p 0.000; 9 groups, n 1344); P2 VIX regime (past-only median): SIS 0.137 vs Gaussian 95% 0.141 (ok; permutation p 0.049; 2 groups, n 1344) |

**Gates: 3/7 pass -> FAIL**

## Standard metrics
```
           trades win avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all trades   2583 63% $62 $17,620   1.64    3.26          1.27 $12,204   1.44  2.73      12.91
kept         1394 63% $41  $6,209   0.77    1.39          1.16 $16,670   0.37  3.46       3.59
kept longs   1394 63% $41  $6,209   0.77    1.39          1.16 $16,670   0.37  3.46       3.59
```
## 2023+ bootstrap
```
                           actual       p5       p50       p95
name       metric                                             
all trades sharpe            1.95     1.24      1.99      2.76
           sortino           4.03     2.29      4.13      6.51
           pf_day            1.80     1.44      1.82      2.33
           calmar            2.01     1.03      2.50      5.06
           ulcer             2.38     1.63      3.09      6.77
           max_dd       12,203.50 6,286.62  9,754.00 15,980.32
           P(Sharpe<=0)       NaN      NaN      0.00       NaN
kept       sharpe            0.88     0.17      0.96      1.71
           sortino           1.59     0.27      1.73      3.64
           pf_day            1.44     1.07      1.48      2.09
           calmar            0.49     0.08      0.80      2.24
           ulcer             4.47     2.42      5.52     14.83
           max_dd       16,669.50 6,112.82 10,663.12 20,333.02
           P(Sharpe<=0)       NaN      NaN      0.03       NaN
kept longs sharpe            0.88     0.17      0.96      1.71
           sortino           1.59     0.27      1.73      3.64
           pf_day            1.44     1.07      1.48      2.09
           calmar            0.49     0.08      0.80      2.24
           ulcer             4.47     2.42      5.52     14.83
           max_dd       16,669.50 6,112.82 10,663.12 20,333.02
           P(Sharpe<=0)       NaN      NaN      0.03       NaN
```
## 2023+ drawdown permutation
```
           actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all trades   $12,204      82%  $9,537 $14,756 $17,774        100%        100%        100%
kept         $16,670      94% $10,584 $17,072 $21,409        100%        100%        100%
kept longs   $16,670      94% $10,584 $17,072 $21,409        100%        100%        100%
```