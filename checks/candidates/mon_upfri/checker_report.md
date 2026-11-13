# Checker report: mon_upfri

kind filter, pre-registered False, variants 4, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | kept $368.5 (n 218) vs skipped $510.4 (n 196), t -0.50 |
| G2 holdout | FAIL | kept - skipped: 2018-22 $+16.4, 2023-26 $-380.5 |
| G3 years | FAIL | kept beats skipped in 5/9 years: 2018 +245, 2019 +349, 2020 -1264, 2021 +214, 2022 +668, 2023 -658, 2024 -199, 2025 -1113, 2026 +591 |
| G5 placebo | FAIL | labels shuffled within years (2,000): p 0.6975 |
| G6 resampling | PASS | kept trades 2023+ P(Sharpe <= 0) 0.035 |
| G7 MinTRL | PASS | 218 trades vs MinTRL 139 |
| G8 regime stability | PASS | rho 0.73 (yearly Sharpe 2018 -0.3, 2019 1.5, 2020 0.3, 2021 0.5, 2022 0.4, 2023 1.8, 2024 0.4, 2025 0.6, 2026 1.2) |
| G13 invariance | PASS | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.364 vs Gaussian 95% 0.446 (ok; permutation p 0.358; 5 groups, n 130); P2 VIX regime (past-only median): SIS 0.290 vs Gaussian 95% 0.330 (ok; permutation p 0.110; 2 groups, n 168) |

**Gates: 3/7 pass -> FAIL**

## Standard metrics
```
           trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all trades    414 55% $436 $19,754   1.02    1.79          1.51 $22,670   0.87  9.82       4.02
kept          218 56% $369  $8,798   0.67    1.11          1.45 $19,975   0.44  6.39       2.76
kept longs    218 56% $369  $8,798   0.67    1.11          1.45 $19,975   0.44  6.39       2.76
```
## 2023+ bootstrap
```
                           actual        p5       p50       p95
name       metric                                              
all trades sharpe            1.51      0.83      1.58      2.28
           sortino           2.79      1.37      3.01      5.03
           pf_day            1.83      1.38      1.89      2.59
           calmar            2.29      0.62      1.87      4.06
           ulcer             3.71      2.67      5.58     13.88
           max_dd       15,741.92 12,179.04 19,925.08 34,785.27
           P(Sharpe<=0)       NaN       NaN      0.00       NaN
kept       sharpe            0.91      0.13      0.89      1.65
           sortino           1.56      0.19      1.52      3.40
           pf_day            1.63      1.07      1.61      2.50
           calmar            0.76      0.08      0.82      2.39
           ulcer             7.66      3.23      7.87     24.02
           max_dd       19,974.83 10,039.16 17,631.96 35,057.11
           P(Sharpe<=0)       NaN       NaN      0.03       NaN
kept longs sharpe            0.91      0.13      0.89      1.65
           sortino           1.56      0.19      1.52      3.40
           pf_day            1.63      1.07      1.61      2.50
           calmar            0.76      0.08      0.82      2.39
           ulcer             7.66      3.23      7.87     24.02
           max_dd       19,974.83 10,039.16 17,631.96 35,057.11
           P(Sharpe<=0)       NaN       NaN      0.03       NaN
```
## 2023+ drawdown permutation
```
           actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all trades   $15,742      12% $20,908 $33,655 $41,344        100%        100%        100%
kept         $19,975      62% $18,446 $29,402 $35,991        100%        100%        100%
kept longs   $19,975      62% $18,446 $29,402 $35,991        100%        100%        100%
```