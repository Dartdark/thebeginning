# Checker report: x1_late_relflow

kind strategy, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 3.05, PSR 0.999, DSR(N=374) 0.533 |
| G2 holdout | FAIL | 2018-22 $163.2 (t 3.69), 2023-26 $38.6 (t 0.67) |
| G3 years | PASS | 7/9 years positive: 2018 $8,265, 2019 $-1,508, 2020 $6,240, 2021 $11,190, 2022 $15,636, 2023 $7,769, 2024 $863, 2025 $4,533, 2026 $-5,756 |
| G4 concentration | PASS | without the best 5% of trades: $2,168 total ($5.2 a trade) vs $47,233 |
| G5 placebo | PASS | 100 placebo runs, mean $-16.7; share >= real $108.3: 0.000 |
| G6 resampling | FAIL | 2023+ P(Sharpe <= 0) 0.243 |
| G7 MinTRL | PASS | 436 trades vs MinTRL 117 |
| G8 regime stability | FAIL | rho 0.53 (yearly Sharpe 2018 2.4, 2019 -1.1, 2020 1.1, 2021 2.6, 2022 2.0, 2023 2.0, 2024 0.2, 2025 0.7, 2026 -1.0) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.365 vs Gaussian 95% 0.313 (DIFFERS; permutation p 0.004; 8 groups, n 383); P2 VIX regime (past-only median): SIS 0.353 vs Gaussian 95% 0.218 (DIFFERS; permutation p 0.000; 2 groups, n 386) |

**Gates: 5/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg annual sharpe sortino profit_factor max_dd calmar ulcer ulcer_perf
all       436 58% $108 $5,200   1.00    1.75          1.54 $7,580   0.69  2.28       4.57
longs     217 61% $106 $2,529   0.71    1.21          1.56 $5,449   0.46  1.96       2.59
shorts    219 55% $111 $2,671   0.70    1.27          1.53 $9,027   0.30  3.04       1.76
```
## 2023+ bootstrap
```
                      actual       p5      p50       p95
name   metric                                           
all    sharpe           0.34    -0.50     0.32      1.17
       sortino          0.50    -0.65     0.47      1.93
       pf_day           1.14     0.83     1.13      1.58
       calmar           0.25    -0.16     0.18      1.11
       ulcer            4.50     2.74     7.00     19.48
       max_dd       7,579.75 5,042.00 9,702.47 19,752.35
       P(Sharpe<=0)      NaN      NaN     0.24       NaN
longs  sharpe           0.41    -0.43     0.38      1.24
       sortino          0.58    -0.54     0.54      2.10
       pf_day           1.26     0.78     1.24      2.05
       calmar           0.28    -0.16     0.24      1.33
       ulcer            2.87     1.75     4.35     11.67
       max_dd       5,449.44 2,975.66 5,841.88 11,909.14
       P(Sharpe<=0)      NaN      NaN     0.22       NaN
shorts sharpe           0.09    -0.69     0.09      0.88
       sortino          0.13    -0.92     0.14      1.55
       pf_day           1.05     0.70     1.05      1.60
       calmar           0.04    -0.21     0.05      0.82
       ulcer            6.13     2.40     6.54     17.84
       max_dd       9,027.50 3,798.49 7,767.78 16,216.20
       P(Sharpe<=0)      NaN      NaN     0.42       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank   dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all       $7,580      25% $9,042 $14,363 $17,021        100%        100%        100%
longs     $5,449      47% $5,587  $8,919 $10,703        100%        100%         99%
shorts    $9,027      72% $7,576 $11,784 $13,711        100%        100%        100%
```