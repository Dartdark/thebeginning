# Checker report: ot_anyday

kind strategy, pre-registered False, variants 6, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 4.84, PSR 1.000, DSR(N=374) 0.969 |
| G2 holdout | PASS | 2018-22 $152.6 (t 3.09), 2023-26 $337.0 (t 3.73) |
| G3 years | PASS | 8/9 years positive: 2018 $5,620, 2019 $11,678, 2020 $57,988, 2021 $-2,154, 2022 $35,078, 2023 $17,168, 2024 $48,044, 2025 $59,428, 2026 $28,344 |
| G4 concentration | PASS | without the best 5% of trades: $6,376 total ($5.8 a trade) vs $261,193 |
| G5 placebo | PASS | 500 placebo runs, mean $102.5; share >= real $224.6: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.000 |
| G7 MinTRL | PASS | 1163 trades vs MinTRL 136 |
| G8 regime stability | PASS | rho 0.70 (yearly Sharpe 2018 0.7, 2019 1.4, 2020 2.7, 2021 -0.1, 2022 1.8, 2023 1.5, 2024 2.6, 2025 2.3, 2026 1.6) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.201 vs Gaussian 95% 0.202 (ok; permutation p 0.195; 9 groups, n 1113); P2 VIX regime (past-only median): SIS 0.201 vs Gaussian 95% 0.127 (DIFFERS; permutation p 0.002; 2 groups, n 1113) |

**Gates: 8/8 pass -> PASS**

## Standard metrics
```
      trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all     1163 56% $225 $29,649   1.62    2.66          1.55 $20,850   1.42  4.35      13.63
longs   1163 56% $225 $29,649   1.62    2.66          1.55 $20,850   1.42  4.35      13.63
```
## 2023+ bootstrap
```
                      actual        p5       p50       p95
name  metric                                              
all   sharpe            1.94      1.10      2.00      2.88
      sortino           3.19      1.62      3.35      5.58
      pf_day            1.68      1.34      1.70      2.19
      calmar            2.18      0.79      2.22      4.83
      ulcer             4.48      2.25      4.83     12.63
      max_dd       19,329.25 11,252.24 19,140.50 34,887.17
      P(Sharpe<=0)       NaN       NaN      0.00       NaN
longs sharpe            1.94      1.10      2.00      2.88
      sortino           3.19      1.62      3.35      5.58
      pf_day            1.68      1.34      1.70      2.19
      calmar            2.18      0.79      2.22      4.83
      ulcer             4.48      2.25      4.83     12.63
      max_dd       19,329.25 11,252.24 19,140.50 34,887.17
      P(Sharpe<=0)       NaN       NaN      0.00       NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all     $19,329      56% $18,624 $29,493 $35,345        100%        100%        100%
longs   $19,329      56% $18,624 $29,493 $35,345        100%        100%        100%
```