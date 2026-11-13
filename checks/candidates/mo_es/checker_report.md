# Checker report: mo_es

kind strategy, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 2.62, PSR 0.998, DSR(N=374) 0.349 |
| G2 holdout | PASS | 2018-22 $192.9 (t 1.83), 2023-26 $239.6 (t 1.87) |
| G3 years | FAIL | 5/9 years positive: 2018 $3,820, 2019 $-732, 2020 $-2,175, 2021 $-2,452, 2022 $29,515, 2023 $-4,248, 2024 $7,450, 2025 $7,782, 2026 $17,288 |
| G4 concentration | PASS | without the best 5% of trades: $968 total ($3.9 a trade) vs $56,248 |
| G5 placebo | PASS | 100 placebo runs, mean $27.2; share >= real $213.9: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.020 |
| G7 MinTRL | PASS | 263 trades vs MinTRL 83 |
| G8 regime stability | FAIL | rho 0.47 (yearly Sharpe 2018 0.9, 2019 -0.2, 2020 -0.4, 2021 -0.4, 2022 2.5, 2023 -0.7, 2024 1.1, 2025 0.9, 2026 2.1) |
| G13 invariance | PASS | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.390 vs Gaussian 95% 0.400 (ok; permutation p 0.046; 6 groups, n 193); P2 VIX regime (past-only median): SIS 0.221 vs Gaussian 95% 0.290 (ok; permutation p 0.203; 2 groups, n 213) |

**Gates: 6/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       263 48% $214 $6,203   0.86    1.92          1.55 $10,645   0.58  5.84       2.12
longs     140 51% $196 $3,025   0.69    1.40          1.58 $12,682   0.24  8.14       0.74
shorts    123 45% $234 $3,179   0.56    1.32          1.53  $9,410   0.34  4.65       1.37
```
## 2023+ bootstrap
```
                      actual       p5      p50       p95
name   metric                                           
all    sharpe           0.94     0.22     0.95      1.62
       sortino          2.04     0.41     2.07      4.14
       pf_day           1.55     1.11     1.56      2.23
       calmar           1.05     0.13     0.98      2.57
       ulcer            6.44     2.10     4.21     10.08
       max_dd       6,932.50 4,447.12 7,470.00 13,608.87
       P(Sharpe<=0)      NaN      NaN     0.02       NaN
longs  sharpe           1.11     0.37     1.13      1.77
       sortino          2.67     0.68     2.73      5.68
       pf_day           2.13     1.26     2.17      3.79
       calmar           1.81     0.25     1.35      3.70
       ulcer            2.71     1.18     2.46      6.07
       max_dd       3,270.00 2,357.25 4,321.25  8,235.00
       P(Sharpe<=0)      NaN      NaN     0.01       NaN
shorts sharpe           0.24    -0.53     0.25      0.91
       sortino          0.48    -0.86     0.50      2.29
       pf_day           1.17     0.71     1.18      1.93
       calmar           0.14    -0.19     0.17      1.17
       ulcer            9.27     2.70     6.54     17.14
       max_dd       9,410.00 4,120.00 8,030.00 16,125.25
       P(Sharpe<=0)      NaN      NaN     0.29       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank   dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all       $6,932      35% $7,712 $12,724 $15,225        100%        100%        100%
longs     $3,270      16% $4,330  $7,233  $8,735        100%        100%         93%
shorts    $9,410      63% $8,642 $13,496 $15,559        100%        100%        100%
```
