# Checker report: ot_es

kind strategy, pre-registered True, variants 2, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 4.36, PSR 1.000, DSR(N=374) 0.924 |
| G2 holdout | PASS | 2018-22 $159.5 (t 3.19), 2023-26 $209.6 (t 2.97) |
| G3 years | PASS | 9/9 years positive: 2018 $1,205, 2019 $9,795, 2020 $22,692, 2021 $502, 2022 $17,012, 2023 $8,025, 2024 $7,702, 2025 $14,218, 2026 $14,690 |
| G4 concentration | PASS | without the best 5% of trades: $24,190 total ($47.7 a trade) vs $95,842 |
| G5 placebo | PASS | 500 placebo runs, mean $20.2; share >= real $179.5: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.000 |
| G7 MinTRL | PASS | 534 trades vs MinTRL 73 |
| G8 regime stability | PASS | rho 0.77 (yearly Sharpe 2018 0.3, 2019 2.1, 2020 2.0, 2021 0.1, 2022 2.2, 2023 1.5, 2024 1.2, 2025 1.4, 2026 2.7) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.240 vs Gaussian 95% 0.289 (ok; permutation p 0.720; 8 groups, n 470); P2 VIX regime (past-only median): SIS 0.320 vs Gaussian 95% 0.196 (DIFFERS; permutation p 0.001; 2 groups, n 484) |

**Gates: 8/8 pass -> PASS**

## Standard metrics
```
      trades win  avg  annual sharpe sortino profit_factor max_dd calmar ulcer ulcer_perf
all      534 60% $179 $10,914   1.45    2.57          1.74 $7,408   1.47  2.39       9.13
longs    534 60% $179 $10,914   1.45    2.57          1.74 $7,408   1.47  2.39       9.13
```
## 2023+ bootstrap
```
                     actual       p5      p50       p95
name  metric                                           
all   sharpe           1.54     0.73     1.52      2.28
      sortino          2.65     1.08     2.64      4.86
      pf_day           1.82     1.32     1.81      2.51
      calmar           1.66     0.59     1.87      4.31
      ulcer            2.29     1.33     2.69      6.10
      max_dd       7,407.50 3,872.12 6,415.00 11,220.62
      P(Sharpe<=0)      NaN      NaN     0.00       NaN
longs sharpe           1.54     0.73     1.52      2.28
      sortino          2.65     1.08     2.64      4.86
      pf_day           1.82     1.32     1.81      2.51
      calmar           1.66     0.59     1.87      4.31
      ulcer            2.29     1.33     2.69      6.10
      max_dd       7,407.50 3,872.12 6,415.00 11,220.62
      P(Sharpe<=0)      NaN      NaN     0.00       NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank   dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $7,408      55% $7,175 $11,308 $13,398        100%        100%        100%
longs    $7,408      55% $7,175 $11,308 $13,398        100%        100%        100%
```