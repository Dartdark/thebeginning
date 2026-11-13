# Checker report: x2_rs_ym

kind strategy, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t -3.25, PSR 0.001, DSR(N=374) 0.000 |
| G2 holdout | FAIL | 2018-22 $-72.3 (t -1.89), 2023-26 $-127.3 (t -2.69) |
| G3 years | FAIL | 0/9 years positive: 2018 $-2,700, 2019 $-8,559, 2020 $-5,268, 2021 $-10,816, 2022 $-18,423, 2023 $-12,764, 2024 $-8,333, 2025 $-24,847, 2026 $-22,651 |
| G4 concentration | FAIL | without the best 5% of trades: $-245,612 total ($-220.7 a trade) vs $-114,360 |
| G5 placebo | FAIL | 100 placebo runs, mean $-18.8; share >= real $-97.6: 1.000 |
| G6 resampling | FAIL | 2023+ P(Sharpe <= 0) 0.995 |
| G7 MinTRL | FAIL | 1172 trades vs MinTRL inf |
| G8 regime stability | FAIL | rho 0.24 (yearly Sharpe 2018 -0.3, 2019 -1.4, 2020 -0.4, 2021 -1.1, 2022 -1.2, 2023 -1.2, 2024 -0.7, 2025 -1.5, 2026 -2.0) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.194 vs Gaussian 95% 0.200 (ok; permutation p 0.088; 9 groups, n 1122); P2 VIX regime (past-only median): SIS 0.244 vs Gaussian 95% 0.128 (DIFFERS; permutation p 0.000; 2 groups, n 1122) |

**Gates: 0/8 pass -> FAIL**

## Standard metrics
```
       trades win   avg   annual sharpe sortino profit_factor   max_dd calmar  ulcer ulcer_perf
all      1172 45%  $-98 $-12,590  -1.08   -1.49          0.79 $118,777  -0.11 102.72      -0.25
longs     574 50%  $-46  $-2,885  -0.35   -0.50          0.90  $34,796  -0.08  26.04      -0.22
shorts    598 40% $-147  $-9,705  -1.17   -1.58          0.69  $89,805  -0.11  85.27      -0.23
```
## 2023+ bootstrap
```
                       actual        p5       p50        p95
name   metric                                               
all    sharpe           -1.36     -2.35     -1.41      -0.50
       sortino          -1.85     -3.01     -1.91      -0.72
       pf_day            0.75      0.61      0.74       0.90
       calmar           -0.24     -0.25     -0.23      -0.14
       ulcer            67.61     35.77     83.17     142.69
       max_dd       74,054.80 40,451.58 79,104.68 122,460.63
       P(Sharpe<=0)       NaN       NaN      0.99        NaN
longs  sharpe           -0.43     -1.39     -0.49       0.36
       sortino          -0.61     -1.82     -0.69       0.55
       pf_day            0.88      0.66      0.87       1.11
       calmar           -0.15     -0.24     -0.16       0.21
       ulcer            22.12      9.56     28.12      61.99
       max_dd       27,248.00 13,453.85 29,496.35  55,858.58
       P(Sharpe<=0)       NaN       NaN      0.83        NaN
shorts sharpe           -1.51     -2.36     -1.50      -0.67
       sortino          -1.99     -2.90     -1.98      -0.96
       pf_day            0.64      0.49      0.64       0.82
       calmar           -0.25     -0.26     -0.24      -0.18
       ulcer            57.96     30.54     62.09     100.28
       max_dd       54,525.45 31,845.16 56,895.12  86,133.64
       P(Sharpe<=0)       NaN       NaN      1.00        NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $74,055      43% $74,973 $86,077 $91,981        100%        100%        100%
longs    $27,248      53% $26,870 $37,256 $41,485        100%        100%        100%
shorts   $54,525      25% $56,547 $63,859 $66,840        100%        100%        100%
```