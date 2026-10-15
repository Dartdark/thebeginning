# Checker report: vb_single_print_filter

kind filter, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 193, t_threshold(N) 3.47

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | kept $132.4 (n 1238) vs skipped $17.8 (n 518), t 2.38 |
| G2 holdout | PASS | kept - skipped: 2018-22 $+73.3, 2023-26 $+156.4 |
| G3 years | PASS | kept beats skipped in 7/9 years: 2018 -15, 2019 +5, 2020 +230, 2021 +96, 2022 +33, 2023 +197, 2024 +209, 2025 -63, 2026 +246 |
| G5 placebo | PASS | labels shuffled within years (2,000): p 0.0075 |
| G4 concentration | PASS | n/a for filters |
| G6 resampling | PASS | kept trades 2023+ P(Sharpe <= 0) 0.000 |

**Gates: 6/6 pass -> PASS**

## Standard metrics
```
           trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all trades   1756 66%  $99 $19,085   1.44    2.22          1.29 $12,402   1.54  3.07      12.43
kept         1238 68% $132 $18,068   1.60    2.56          1.41 $11,727   1.54  2.58      14.00
kept longs   1238 68% $132 $18,068   1.60    2.56          1.41 $11,727   1.54  2.58      14.00
```
## 2023+ bootstrap
```
                           actual       p5       p50       p95
name       metric                                             
all trades sharpe            1.58     0.83      1.61      2.39
           sortino           2.44     1.21      2.48      3.93
           pf_day            1.46     1.22      1.47      1.79
           calmar            2.02     0.60      1.76      3.58
           ulcer             4.51     2.70      4.93     11.48
           max_dd       12,401.50 9,448.27 14,584.12 24,758.81
           P(Sharpe<=0)       NaN      NaN      0.00       NaN
kept       sharpe            1.82     1.06      1.86      2.65
           sortino           2.92     1.59      2.98      4.64
           pf_day            1.67     1.35      1.69      2.14
           calmar            2.15     0.82      2.12      4.34
           ulcer             3.53     2.04      3.90      9.07
           max_dd       11,727.00 7,588.70 11,939.00 20,607.85
           P(Sharpe<=0)       NaN      NaN      0.00       NaN
kept longs sharpe            1.82     1.06      1.86      2.65
           sortino           2.92     1.59      2.98      4.64
           pf_day            1.67     1.35      1.69      2.14
           calmar            2.15     0.82      2.12      4.34
           ulcer             3.53     2.04      3.90      9.07
           max_dd       11,727.00 7,588.70 11,939.00 20,607.85
           P(Sharpe<=0)       NaN      NaN      0.00       NaN
```
## 2023+ drawdown permutation
```
           actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all trades   $12,402      16% $15,447 $24,480 $29,729        100%        100%        100%
kept         $11,727      41% $12,307 $19,131 $24,229        100%        100%        100%
kept longs   $11,727      41% $12,307 $19,131 $24,229        100%        100%        100%
```