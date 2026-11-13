# Checker report: mon_downfri

kind filter, pre-registered False, variants 4, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | kept $510.4 (n 196) vs skipped $368.5 (n 218), t 0.50 |
| G2 holdout | FAIL | kept - skipped: 2018-22 $-16.4, 2023-26 $+380.5 |
| G3 years | FAIL | kept beats skipped in 4/9 years: 2018 -245, 2019 -349, 2020 +1264, 2021 -214, 2022 -668, 2023 +658, 2024 +199, 2025 +1113, 2026 -591 |
| G5 placebo | FAIL | labels shuffled within years (2,000): p 0.3025 |
| G6 resampling | PASS | kept trades 2023+ P(Sharpe <= 0) 0.003 |
| G7 MinTRL | PASS | 196 trades vs MinTRL 87 |
| G8 regime stability | FAIL | rho 0.39 (yearly Sharpe 2018 -1.4, 2019 -0.5, 2020 2.6, 2021 -0.0, 2022 -0.6, 2023 2.9, 2024 0.7, 2025 1.9, 2026 0.6) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.402 vs Gaussian 95% 0.482 (ok; permutation p 0.222; 4 groups, n 95); P2 VIX regime (past-only median): SIS 0.434 vs Gaussian 95% 0.358 (DIFFERS; permutation p 0.009; 2 groups, n 146) |

**Gates: 2/7 pass -> FAIL**

## Standard metrics
```
           trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all trades    414 55% $436 $19,754   1.02    1.79          1.51 $22,670   0.87  9.82       4.02
kept          196 54% $510 $10,956   0.77    1.42          1.56 $20,744   0.53 10.34       2.12
kept longs    196 54% $510 $10,956   0.77    1.42          1.56 $20,744   0.53 10.34       2.12
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
kept       sharpe            1.21      0.59      1.33      1.97
           sortino           2.46      1.00      2.91      5.48
           pf_day            2.06      1.40      2.26      3.67
           calmar            1.96      0.42      1.66      4.14
           ulcer             3.04      2.18      4.87     13.71
           max_dd       10,686.25  7,722.52 13,740.83 25,838.02
           P(Sharpe<=0)       NaN       NaN      0.00       NaN
kept longs sharpe            1.21      0.59      1.33      1.97
           sortino           2.46      1.00      2.91      5.48
           pf_day            2.06      1.40      2.26      3.67
           calmar            1.96      0.42      1.66      4.14
           ulcer             3.04      2.18      4.87     13.71
           max_dd       10,686.25  7,722.52 13,740.83 25,838.02
           P(Sharpe<=0)       NaN       NaN      0.00       NaN
```
## 2023+ drawdown permutation
```
           actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all trades   $15,742      12% $20,908 $33,655 $41,344        100%        100%        100%
kept         $10,686       9% $15,145 $24,605 $28,864        100%        100%        100%
kept longs   $10,686       9% $15,145 $24,605 $28,864        100%        100%        100%
```