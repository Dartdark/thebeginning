# Checker report: overnight_tick

kind strategy, pre-registered False, variants 30, N (ranked items in TRIALS.csv) 291, t_threshold(N) 3.58

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 5.21, PSR 1.000, DSR(N=291) 0.991 |
| G2 holdout | PASS | 2018-22 $278.8 (t 3.78), 2023-26 $517.5 (t 3.67) |
| G3 years | PASS | 9/9 years positive: 2018 $3,331, 2019 $9,290, 2020 $33,224, 2021 $14,148, 2022 $29,792, 2023 $14,129, 2024 $22,829, 2025 $32,172, 2026 $41,618 |
| G4 concentration | PASS | without the best 5% of trades: $67,970 total ($133.5 a trade) vs $200,534 |
| G5 placebo | PASS | 20 placebo runs, mean $165.4; share >= real $374.1: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.000 |
| G7 MinTRL | PASS | 536 trades vs MinTRL 52 |
| G8 regime stability | PASS | rho 0.81 (yearly Sharpe 2018 0.6, 2019 1.3, 2020 2.1, 2021 1.3, 2022 2.4, 2023 1.7, 2024 1.7, 2025 1.6, 2026 3.3) |

**Gates: 8/8 pass -> PASS**

## Standard metrics
```
      trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      536 60% $374 $22,835   1.73    3.26          1.98 $12,801   1.78  2.91      15.71
longs    536 60% $374 $22,835   1.73    3.26          1.98 $12,801   1.78  2.91      15.71
```
## 2023+ bootstrap
```
                      actual       p5       p50       p95
name  metric                                             
all   sharpe            1.88     1.05      1.84      2.57
      sortino           3.56     1.61      3.44      6.35
      pf_day            2.11     1.50      2.06      2.91
      calmar            2.38     1.00      2.50      5.56
      ulcer             2.56     1.56      3.31      7.69
      max_dd       12,801.25 6,893.19 11,268.00 19,105.59
      P(Sharpe<=0)       NaN      NaN      0.00       NaN
longs sharpe            1.88     1.05      1.84      2.57
      sortino           3.56     1.61      3.44      6.35
      pf_day            2.11     1.50      2.06      2.91
      calmar            2.38     1.00      2.50      5.56
      ulcer             2.56     1.56      3.31      7.69
      max_dd       12,801.25 6,893.19 11,268.00 19,105.59
      P(Sharpe<=0)       NaN      NaN      0.00       NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all     $12,801      48% $12,910 $19,817 $23,338        100%        100%        100%
longs   $12,801      48% $12,910 $19,817 $23,338        100%        100%        100%
```