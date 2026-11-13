# Checker report: ldf_nostop

kind strategy, pre-registered True, variants 2, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 3.46, PSR 1.000, DSR(N=374) 0.701 |
| G2 holdout | PASS | 2018-22 $84.4 (t 3.03), 2023-26 $104.6 (t 2.13) |
| G3 years | PASS | 8/9 years positive: 2018 $8,283, 2019 $-6,710, 2020 $3,350, 2021 $11,185, 2022 $25,426, 2023 $20,031, 2024 $929, 2025 $5,029, 2026 $17,228 |
| G4 concentration | FAIL | without the best 5% of trades: $-15,443 total ($-18.0 a trade) vs $84,749 |
| G5 placebo | PASS | 100 placebo runs, mean $-15.4; share >= real $93.6: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.014 |
| G7 MinTRL | PASS | 905 trades vs MinTRL 179 |
| G8 regime stability | FAIL | rho 0.49 (yearly Sharpe 2018 1.9, 2019 -2.8, 2020 0.6, 2021 1.5, 2022 2.8, 2023 3.0, 2024 0.1, 2025 0.4, 2026 1.6) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.294 vs Gaussian 95% 0.227 (DIFFERS; permutation p 0.000; 9 groups, n 855); P2 VIX regime (past-only median): SIS 0.236 vs Gaussian 95% 0.151 (DIFFERS; permutation p 0.001; 2 groups, n 855) |

**Gates: 6/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       905 55%  $94 $9,265   1.14    1.97          1.43 $11,949   0.78  5.71       3.25
longs     490 57%  $77 $4,145   0.74    1.30          1.41 $12,920   0.32  4.02       2.06
shorts    415 54% $113 $5,120   0.87    1.49          1.45  $7,312   0.70  4.22       2.43
```
## 2023+ bootstrap
```
                       actual       p5       p50       p95
name   metric                                             
all    sharpe            1.06     0.28      1.10      1.85
       sortino           1.85     0.43      1.94      3.60
       pf_day            1.38     1.08      1.40      1.77
       calmar            0.91     0.15      0.99      2.62
       ulcer             5.22     2.46      5.28     13.70
       max_dd       11,949.00 6,568.57 11,139.25 20,297.16
       P(Sharpe<=0)       NaN      NaN      0.01       NaN
longs  sharpe            0.56    -0.24      0.59      1.24
       sortino           0.98    -0.34      1.04      2.68
       pf_day            1.29     0.91      1.30      1.81
       calmar            0.32    -0.10      0.46      1.65
       ulcer             6.00     2.49      5.80     17.88
       max_dd       12,919.75 5,176.30  9,269.38 19,266.62
       P(Sharpe<=0)       NaN      NaN      0.12       NaN
shorts sharpe            0.95     0.19      1.01      1.70
       sortino           1.64     0.30      1.74      3.42
       pf_day            1.47     1.08      1.50      2.05
       calmar            0.92     0.12      0.93      2.44
       ulcer             4.10     1.94      4.09     11.27
       max_dd        7,311.50 4,416.46  7,576.62 14,509.64
       P(Sharpe<=0)       NaN      NaN      0.02       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $11,949      64% $10,925 $17,950 $21,232        100%        100%        100%
longs    $12,920      86%  $9,528 $15,346 $18,146        100%        100%        100%
shorts    $7,312      39%  $7,874 $12,658 $15,046        100%        100%        100%
```