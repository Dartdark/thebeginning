# Checker report: letf_fade_gc

kind strategy, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t -0.44, PSR 0.331, DSR(N=374) 0.000 |
| G2 holdout | FAIL | 2018-22 $-46.1 (t -2.17), 2023-26 $14.8 (t 0.29) |
| G3 years | FAIL | 2/9 years positive: 2018 $-1,613, 2019 $-1,165, 2020 $-386, 2021 $-2,451, 2022 $-1,860, 2023 $-1,280, 2024 $694, 2025 $-883, 2026 $4,348 |
| G4 concentration | FAIL | without the best 5% of trades: $-30,355 total ($-89.5 a trade) vs $-4,595 |
| G5 placebo | FAIL | 200 placebo runs, mean $-30.0; share >= real $-12.9: 0.250 |
| G6 resampling | FAIL | 2023+ P(Sharpe <= 0) 0.394 |
| G7 MinTRL | FAIL | 357 trades vs MinTRL inf |
| G8 regime stability | FAIL | rho 0.28 (yearly Sharpe 2018 -2.2, 2019 -2.0, 2020 -0.2, 2021 -1.8, 2022 -1.0, 2023 -0.8, 2024 0.3, 2025 -0.2, 2026 0.6) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.289 vs Gaussian 95% 0.337 (ok; permutation p 0.613; 7 groups, n 307); P2 VIX regime (past-only median): SIS 0.293 vs Gaussian 95% 0.244 (DIFFERS; permutation p 0.022; 2 groups, n 307) |

**Gates: 0/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       357 44% $-13   $-509  -0.15   -0.21          0.92 $15,695  -0.03 12.40      -0.08
longs     176 39% $-75 $-1,463  -0.57   -0.72          0.63 $17,461  -0.08 13.14      -0.22
shorts    181 50%  $48    $954   0.41    0.74          1.38  $4,070   0.23  3.11       0.61
```
## 2023+ bootstrap
```
                       actual       p5       p50       p95
name   metric                                             
all    sharpe            0.15    -0.75      0.14      1.05
       sortino           0.22    -0.92      0.21      1.96
       pf_day            1.07     0.68      1.07      1.66
       calmar            0.08    -0.21      0.08      0.99
       ulcer             3.92     2.42      7.34     22.09
       max_dd        8,729.83 4,099.98  9,121.08 20,384.63
       P(Sharpe<=0)       NaN      NaN      0.39       NaN
longs  sharpe           -0.53    -1.43     -0.59      0.30
       sortino          -0.68    -1.57     -0.73      0.49
       pf_day            0.70     0.36      0.68      1.22
       calmar           -0.16    -0.25     -0.18      0.19
       ulcer            10.16     4.19     12.35     26.85
       max_dd       12,694.67 5,026.49 11,658.08 23,120.97
       P(Sharpe<=0)       NaN      NaN      0.86       NaN
shorts sharpe            0.84     0.04      0.88      1.67
       sortino           1.56     0.05      1.74      5.97
       pf_day            1.83     1.03      1.87      3.48
       calmar            0.67     0.02      0.76      3.62
       ulcer             1.21     0.69      1.98      6.20
       max_dd        4,070.00 1,225.00  3,805.00  7,470.25
       P(Sharpe<=0)       NaN      NaN      0.05       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all       $8,730      49%  $8,766 $13,540 $15,241        100%        100%        100%
longs    $12,695      74% $11,187 $14,768 $16,235        100%        100%        100%
shorts    $4,070      70%  $3,658  $5,251  $6,025        100%        100%         86%
```