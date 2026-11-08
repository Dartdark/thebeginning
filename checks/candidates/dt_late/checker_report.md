# Checker report: dt_late

kind strategy, pre-registered True, variants 3, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 3.20, PSR 0.999, DSR(N=374) 0.595 |
| G2 holdout | PASS | 2018-22 $95.2 (t 2.55), 2023-26 $99.7 (t 2.01) |
| G3 years | PASS | 8/9 years positive: 2018 $24,672, 2019 $-9,109, 2020 $18,246, 2021 $30,860, 2022 $17,772, 2023 $27,096, 2024 $21,357, 2025 $12,049, 2026 $10,500 |
| G4 concentration | FAIL | without the best 5% of trades: $-3,588 total ($-2.4 a trade) vs $153,444 |
| G5 placebo | PASS | 100 placebo runs, mean $-14.6; share >= real $97.2: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.018 |
| G7 MinTRL | PASS | 1578 trades vs MinTRL 400 |
| G8 regime stability | PASS | rho 0.66 (yearly Sharpe 2018 2.0, 2019 -1.0, 2020 1.1, 2021 2.0, 2022 0.9, 2023 1.6, 2024 1.2, 2025 0.6, 2026 0.6) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.256 vs Gaussian 95% 0.169 (DIFFERS; permutation p 0.000; 9 groups, n 1528); P2 VIX regime (past-only median): SIS 0.130 vs Gaussian 95% 0.110 (DIFFERS; permutation p 0.013; 2 groups, n 1528) |

**Gates: 7/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      1578 45%  $97 $16,761   1.06    1.86          1.20 $27,730   0.60  6.29       5.33
longs     826 49% $133 $11,956   1.08    1.92          1.30 $18,830   0.63  5.83       4.10
shorts    752 41%  $58  $4,805   0.42    0.74          1.11 $30,119   0.16 10.53       0.91
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe            1.00      0.16      0.98      1.78
       sortino           1.79      0.28      1.76      3.30
       pf_day            1.18      1.03      1.18      1.34
       calmar            0.92      0.08      0.80      2.21
       ulcer             6.88      4.11      8.97     25.68
       max_dd       19,331.50 13,091.55 21,677.25 39,050.09
       P(Sharpe<=0)       NaN       NaN      0.02       NaN
longs  sharpe            1.23      0.43      1.23      1.95
       sortino           2.27      0.75      2.27      3.80
       pf_day            1.33      1.11      1.33      1.57
       calmar            0.83      0.25      1.17      2.72
       ulcer             4.50      2.78      5.55     13.65
       max_dd       18,830.25  8,325.58 13,292.62 24,062.15
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
shorts sharpe            0.18     -0.67      0.16      0.96
       sortino           0.31     -1.09      0.28      1.76
       pf_day            1.04      0.86      1.04      1.26
       calmar            0.12     -0.20      0.08      0.86
       ulcer            16.51      6.28     16.83     46.82
       max_dd       18,386.25 12,982.95 24,637.50 49,113.12
       P(Sharpe<=0)       NaN       NaN      0.38       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $19,332      32% $21,843 $34,751 $42,502        100%        100%        100%
longs    $18,830      88% $13,404 $21,336 $25,587        100%        100%        100%
shorts   $18,386      20% $23,215 $35,847 $42,747        100%        100%        100%
```