# Checker report: mo_gc

kind strategy, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 0.20, PSR 0.581, DSR(N=374) 0.003 |
| G2 holdout | FAIL | 2018-22 $-24.9 (t -0.35), 2023-26 $87.1 (t 0.37) |
| G3 years | FAIL | 5/9 years positive: 2018 $2,764, 2019 $2,224, 2020 $7,479, 2021 $-5,400, 2022 $-10,107, 2023 $3,915, 2024 $-1,572, 2025 $18,341, 2026 $-13,192 |
| G4 concentration | FAIL | without the best 5% of trades: $-41,723 total ($-211.8 a trade) vs $4,452 |
| G5 placebo | FAIL | no placebo.csv supplied (required for a strategy) |
| G6 resampling | FAIL | 2023+ P(Sharpe <= 0) 0.349 |
| G7 MinTRL | FAIL | 208 trades vs MinTRL 13454 |
| G8 regime stability | FAIL | rho 0.37 (yearly Sharpe 2018 1.2, 2019 0.6, 2020 1.5, 2021 -1.4, 2022 -2.5, 2023 0.7, 2024 -0.3, 2025 1.8, 2026 -0.9) |
| G13 invariance | PASS | outcome = net / risk; P3 time (years): SIS 0.371 vs Gaussian 95% 0.426 (ok; permutation p 0.108; 6 groups, n 156); P2 VIX regime (past-only median): SIS 0.252 vs Gaussian 95% 0.293 (ok; permutation p 0.086; 2 groups, n 208) |

**Gates: 0/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       208 44%  $21   $496   0.07    0.11          1.04 $20,839   0.02 16.41       0.06
longs     103 45% $129 $1,475   0.29    0.57          1.30 $10,591   0.14  9.32       0.32
shorts    105 44% $-84  $-980  -0.18   -0.28          0.85 $17,861  -0.05 10.89      -0.18
```
## 2023+ bootstrap
```
                       actual       p5       p50       p95
name   metric                                             
all    sharpe            0.19    -0.69      0.21      1.08
       sortino           0.32    -0.95      0.35      2.31
       pf_day            1.12     0.68      1.13      1.97
       calmar            0.12    -0.20      0.11      1.15
       ulcer             7.81     4.50     13.15     39.35
       max_dd       15,543.20 8,451.40 18,103.70 38,038.17
       P(Sharpe<=0)       NaN      NaN      0.35       NaN
longs  sharpe            0.50    -0.43      0.48      1.24
       sortino           0.98    -0.61      0.93      3.39
       pf_day            1.49     0.73      1.45      2.86
       calmar            0.38    -0.15      0.33      1.73
       ulcer             5.94     2.20      6.42     20.34
       max_dd        9,240.40 4,351.60  9,439.70 20,021.28
       P(Sharpe<=0)       NaN      NaN      0.18       NaN
shorts sharpe           -0.22    -1.10     -0.15      0.68
       sortino          -0.32    -1.30     -0.23      1.47
       pf_day            0.83     0.37      0.87      1.93
       calmar           -0.10    -0.25     -0.07      0.71
       ulcer             6.62     4.32     14.10     38.10
       max_dd       16,575.20 6,601.71 15,566.10 33,258.09
       P(Sharpe<=0)       NaN      NaN      0.60       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $15,543      39% $16,862 $26,846 $31,462        100%        100%        100%
longs     $9,240      61%  $8,424 $13,581 $16,115        100%        100%        100%
shorts   $16,575      55% $16,085 $23,264 $26,762        100%        100%        100%
```