# Checker report: finra_short

kind strategy, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 3.00, PSR 1.000, DSR(N=374) 0.516 |
| G2 holdout | PASS | 2018-22 $180.9 (t 1.35), 2023-26 $670.0 (t 2.71) |
| G3 years | PASS | 8/9 years positive: 2018 $-223, 2019 $19,888, 2020 $23,018, 2021 $20,522, 2022 $10,600, 2023 $4,283, 2024 $27,338, 2025 $106,861, 2026 $83,959 |
| G4 concentration | FAIL | without the best 5% of trades: $-77,005 total ($-109.5 a trade) vs $296,247 |
| G5 placebo | PASS | 200 placebo runs, mean $121.6; share >= real $400.3: 0.010 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.000 |
| G7 MinTRL | PASS | 740 trades vs MinTRL 169 |
| G8 regime stability | PASS | rho 0.72 (yearly Sharpe 2018 -0.1, 2019 1.8, 2020 0.8, 2021 1.0, 2022 0.3, 2023 0.2, 2024 0.9, 2025 1.7, 2026 2.1) |
| G13 invariance | PASS | outcome = net / risk; P3 time (years): SIS 0.174 vs Gaussian 95% 0.266 (ok; permutation p 0.790; 9 groups, n 740); P2 VIX regime (past-only median): SIS 0.151 vs Gaussian 95% 0.158 (ok; permutation p 0.067; 2 groups, n 740) |

**Gates: 7/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       740 49% $400 $35,651   1.04    2.11          1.38 $37,995   0.94  9.51       7.50
longs     374 56% $661 $29,742   1.20    2.79          1.78 $23,896   1.24  4.10      14.49
shorts    366 42% $134  $5,910   0.25    0.45          1.11 $44,426   0.13 31.78       0.37
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe            1.35      0.75      1.39      2.00
       sortino           3.11      1.49      3.21      5.23
       pf_day            1.57      1.26      1.59      2.00
       calmar            1.47      0.65      1.92      4.09
       ulcer            21.39      3.55      7.28     19.14
       max_dd       37,995.50 18,990.38 29,244.29 50,103.94
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
longs  sharpe            1.39      0.81      1.40      2.02
       sortino           3.78      1.72      3.74      6.04
       pf_day            2.10      1.49      2.08      2.81
       calmar            3.02      0.90      2.54      5.50
       ulcer             4.03      2.54      5.10     11.66
       max_dd       14,214.00 10,622.81 16,436.00 27,358.32
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
shorts sharpe            0.47     -0.11      0.54      1.08
       sortino           0.93     -0.19      1.09      2.48
       pf_day            1.22      0.95      1.26      1.62
       calmar            0.37     -0.06      0.49      1.61
       ulcer            34.49      5.77     13.99     41.97
       max_dd       35,555.42 17,695.39 29,934.13 56,422.90
       P(Sharpe<=0)       NaN       NaN      0.09       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $37,995      65% $33,912 $52,110 $65,455        100%        100%        100%
longs    $14,214      12% $19,179 $31,266 $39,596        100%        100%        100%
shorts   $35,555      39% $38,598 $59,790 $73,189        100%        100%        100%
```