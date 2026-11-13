# Checker report: letf_fade

kind strategy, pre-registered False, variants 2, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 3.12, PSR 1.000, DSR(N=374) 0.564 |
| G2 holdout | PASS | 2018-22 $42.4 (t 0.88), 2023-26 $229.6 (t 3.41) |
| G3 years | PASS | 7/9 years positive: 2018 $3,780, 2019 $-2,885, 2020 $2,129, 2021 $2,663, 2022 $8,593, 2023 $8,596, 2024 $-22, 2025 $26,629, 2026 $26,330 |
| G4 concentration | FAIL | without the best 5% of trades: $-8,268 total ($-14.4 a trade) vs $75,812 |
| G5 placebo | PASS | 200 placebo runs, mean $-5.3; share >= real $125.3: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.000 |
| G7 MinTRL | PASS | 605 trades vs MinTRL 149 |
| G8 regime stability | FAIL | rho 0.56 (yearly Sharpe 2018 1.3, 2019 -1.1, 2020 0.2, 2021 0.4, 2022 1.1, 2023 1.4, 2024 -0.0, 2025 2.4, 2026 2.6) |
| G13 invariance | CONCERN | outcome = net / risk; P3 time (years): SIS 0.289 vs Gaussian 95% 0.260 (DIFFERS; permutation p 0.006; 9 groups, n 605); P2 VIX regime (past-only median): SIS 0.266 vs Gaussian 95% 0.172 (DIFFERS; permutation p 0.001; 2 groups, n 605) |

**Gates: 5/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg annual sharpe sortino profit_factor max_dd calmar ulcer ulcer_perf
all       605 56% $125 $8,325   1.03    1.82          1.47 $9,204   0.90  4.49       3.71
longs     328 58% $105 $3,765   0.82    1.32          1.48 $8,333   0.45  5.63       1.34
shorts    277 53% $150 $4,560   0.68    1.28          1.46 $7,791   0.59  3.82       2.38
```
## 2023+ bootstrap
```
                      actual       p5      p50       p95
name   metric                                           
all    sharpe           1.69     0.98     1.65      2.28
       sortino          3.33     1.70     3.22      5.13
       pf_day           1.86     1.43     1.83      2.36
       calmar           2.11     0.99     2.36      4.47
       ulcer            3.11     1.43     2.49      5.15
       max_dd       7,414.08 4,237.27 6,350.38 10,379.02
       P(Sharpe<=0)      NaN      NaN     0.00       NaN
longs  sharpe           1.64     0.82     1.62      2.40
       sortino          3.20     1.35     3.18      5.92
       pf_day           2.07     1.43     2.05      3.00
       calmar           2.59     0.63     1.98      4.56
       ulcer            2.39     1.07     2.05      4.80
       max_dd       3,593.08 2,743.50 4,608.42  8,262.91
       P(Sharpe<=0)      NaN      NaN     0.00       NaN
shorts sharpe           0.86    -0.04     0.81      1.52
       sortino          1.72    -0.06     1.60      4.07
       pf_day           1.67     0.98     1.62      2.67
       calmar           0.92    -0.02     0.72      2.58
       ulcer            3.41     1.99     4.86     13.46
       max_dd       6,848.58 3,977.22 8,026.29 15,473.30
       P(Sharpe<=0)      NaN      NaN     0.06       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank   dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all       $7,414      53% $7,232 $11,518 $13,701        100%        100%        100%
longs     $3,593      14% $4,645  $7,182  $8,336        100%        100%        100%
shorts    $6,849      38% $7,445 $11,881 $14,064        100%        100%        100%
```