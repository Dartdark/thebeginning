# Checker report: letf_fade_cl

kind strategy, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t -0.21, PSR 0.416, DSR(N=374) 0.001 |
| G2 holdout | FAIL | 2018-22 $7.8 (t 0.29), 2023-26 $-24.1 (t -0.66) |
| G3 years | FAIL | 4/9 years positive: 2018 $663, 2019 $-2,126, 2020 $3,837, 2021 $-2,396, 2022 $2,457, 2023 $2,814, 2024 $-1,312, 2025 $-624, 2026 $-5,659 |
| G4 concentration | FAIL | without the best 5% of trades: $-35,116 total ($-72.3 a trade) vs $-2,346 |
| G5 placebo | FAIL | 200 placebo runs, mean $-21.0; share >= real $-4.6: 0.190 |
| G6 resampling | FAIL | 2023+ P(Sharpe <= 0) 0.696 |
| G7 MinTRL | FAIL | 512 trades vs MinTRL inf |
| G8 regime stability | FAIL | rho 0.44 (yearly Sharpe 2018 0.3, 2019 -1.1, 2020 0.8, 2021 -1.1, 2022 0.4, 2023 0.9, 2024 -0.7, 2025 -0.5, 2026 -1.0) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.280 vs Gaussian 95% 0.291 (ok; permutation p 0.195; 8 groups, n 451); P2 VIX regime (past-only median): SIS 0.225 vs Gaussian 95% 0.207 (DIFFERS; permutation p 0.036; 2 groups, n 462) |

**Gates: 0/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       512 46%  $-5   $-260  -0.07   -0.11          0.97 $10,332  -0.03  5.45      -0.10
longs     282 41% $-43 $-1,333  -0.48   -0.71          0.75 $15,483  -0.09 14.57      -0.18
shorts    230 52%  $42  $1,073   0.45    0.75          1.30  $5,370   0.20  2.24       0.96
```
## 2023+ bootstrap
```
                       actual       p5      p50       p95
name   metric                                            
all    sharpe           -0.34    -1.20    -0.26      0.62
       sortino          -0.49    -1.50    -0.39      1.05
       pf_day            0.86     0.59     0.89      1.30
       calmar           -0.12    -0.24    -0.10      0.51
       ulcer             6.26     2.38     8.65     25.27
       max_dd       10,332.17 3,350.54 9,127.33 21,134.07
       P(Sharpe<=0)       NaN      NaN     0.70       NaN
longs  sharpe           -0.38    -1.22    -0.30      0.45
       sortino          -0.58    -1.47    -0.45      0.88
       pf_day            0.79     0.49     0.84      1.31
       calmar           -0.15    -0.25    -0.12      0.43
       ulcer             5.55     1.87     7.12     19.87
       max_dd        7,984.33 2,526.27 7,378.00 16,540.97
       P(Sharpe<=0)       NaN      NaN     0.73       NaN
shorts sharpe           -0.02    -0.81    -0.04      0.87
       sortino          -0.03    -0.95    -0.06      1.43
       pf_day            0.99     0.57     0.97      1.71
       calmar           -0.01    -0.23    -0.02      0.74
       ulcer             3.37     1.23     3.55      9.59
       max_dd        5,370.00 1,709.68 3,855.08  8,334.33
       P(Sharpe<=0)       NaN      NaN     0.53       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank   dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $10,332      64% $9,507 $13,338 $15,254        100%        100%        100%
longs     $7,984      45% $8,193 $11,389 $12,411        100%        100%        100%
shorts    $5,370      90% $3,894  $5,868  $6,726        100%        100%         84%
```