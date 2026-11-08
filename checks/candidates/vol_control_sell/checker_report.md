# Checker report: vol_control_sell

kind strategy, pre-registered False, variants 3, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 2.14, PSR 0.993, DSR(N=374) 0.163 |
| G2 holdout | PASS | 2018-22 $207.8 (t 0.89), 2023-26 $694.0 (t 2.06) |
| G3 years | PASS | 8/9 years positive: 2018 $713, 2019 $374, 2020 $-4,091, 2021 $10,008, 2022 $1,099, 2023 $259, 2024 $9,938, 2025 $5,354, 2026 $6,657 |
| G4 concentration | PASS | without the best 5% of trades: $9,599 total ($143.3 a trade) vs $30,310 |
| G5 placebo | PASS | 200 placebo runs, mean $25.2; share >= real $426.9: 0.005 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.019 |
| G7 MinTRL | PASS | 71 trades vs MinTRL 32 |
| G8 regime stability | PASS | rho 0.61 (yearly Sharpe 2018 0.2, 2019 0.4, 2020 -1.7, 2021 1.4, 2022 0.3, 2023 0.2, 2024 1.2, 2025 0.9, 2026 2.2) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; ; not evaluable: P3 time (years), P2 VIX regime (past-only median) |

**Gates: 7/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg annual sharpe sortino profit_factor max_dd calmar ulcer ulcer_perf
all        71 55% $427 $3,491   0.71    1.75          2.12 $5,578   0.63  4.56       1.53
shorts     71 55% $427 $3,491   0.71    1.75          2.12 $5,578   0.63  4.56       1.53
```
## 2023+ bootstrap
```
                      actual       p5      p50      p95
name   metric                                          
all    sharpe           1.04     0.23     1.00     1.53
       sortino          2.98     0.44     2.84     7.76
       pf_day           3.12     1.26     2.97     8.27
       calmar           1.97     0.15     1.40     4.78
       ulcer            1.63     0.75     2.28     6.59
       max_dd       3,166.75 1,672.25 4,004.00 8,553.04
       P(Sharpe<=0)      NaN      NaN     0.02      NaN
shorts sharpe           1.04     0.23     1.00     1.53
       sortino          2.98     0.44     2.84     7.76
       pf_day           3.12     1.26     2.97     8.27
       calmar           1.97     0.15     1.40     4.78
       ulcer            1.63     0.75     2.28     6.59
       max_dd       3,166.75 1,672.25 4,004.00 8,553.04
       P(Sharpe<=0)      NaN      NaN     0.02      NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank   dd50   dd95   dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all       $3,167      32% $3,781 $5,895 $7,040        100%        100%         76%
shorts    $3,167      32% $3,781 $5,895 $7,040        100%        100%         76%
```