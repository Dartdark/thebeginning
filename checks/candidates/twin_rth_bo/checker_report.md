# Checker report: twin_rth_bo

kind strategy, pre-registered False, variants 7, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 5.27, PSR 1.000, DSR(N=374) 0.996 |
| G2 holdout | PASS | 2018-22 $297.1 (t 4.35), 2023-26 $324.2 (t 3.19) |
| G3 years | PASS | 8/9 years positive: 2018 $10,993, 2019 $-3,988, 2020 $26,569, 2021 $27,885, 2022 $71,940, 2023 $25,589, 2024 $23,772, 2025 $12,327, 2026 $51,142 |
| G4 concentration | PASS | without the best 5% of trades: $42,971 total ($56.8 a trade) vs $246,228 |
| G5 placebo | PASS | 100 placebo runs, mean $24.1; share >= real $308.9: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.001 |
| G7 MinTRL | PASS | 797 trades vs MinTRL 58 |
| G8 regime stability | PASS | rho 0.65 (yearly Sharpe 2018 1.2, 2019 -0.6, 2020 2.2, 2021 2.0, 2022 3.2, 2023 1.6, 2024 1.6, 2025 0.7, 2026 2.5) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.245 vs Gaussian 95% 0.240 (DIFFERS; permutation p 0.045; 9 groups, n 747); P2 VIX regime (past-only median): SIS 0.166 vs Gaussian 95% 0.151 (DIFFERS; permutation p 0.037; 2 groups, n 747) |

**Gates: 8/8 pass -> PASS**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       797 47% $309 $26,896   1.73    3.96          1.69 $13,019   2.07  3.92      13.73
longs     424 50% $283 $13,096   1.33    2.92          1.73 $10,567   1.24  3.88       6.75
shorts    373 45% $339 $13,800   1.14    2.76          1.65 $14,874   0.93  3.97       6.95
```
## 2023+ bootstrap
```
                       actual       p5       p50       p95
name   metric                                             
all    sharpe            1.60     0.84      1.64      2.39
       sortino           3.55     1.65      3.67      6.05
       pf_day            1.61     1.28      1.63      2.10
       calmar            2.18     0.65      2.04      4.43
       ulcer             3.84     2.40      4.69     12.05
       max_dd       13,018.70 9,242.08 14,207.17 25,626.97
       P(Sharpe<=0)       NaN      NaN      0.00       NaN
longs  sharpe            1.50     0.80      1.54      2.20
       sortino           3.60     1.59      3.73      6.35
       pf_day            1.89     1.38      1.93      2.66
       calmar            2.38     0.64      2.10      4.84
       ulcer             3.81     1.75      3.48      8.22
       max_dd        7,693.10 5,459.36  8,755.23 15,850.25
       P(Sharpe<=0)       NaN      NaN      0.00       NaN
shorts sharpe            0.78     0.02      0.81      1.51
       sortino           1.68     0.03      1.72      3.82
       pf_day            1.39     1.01      1.40      1.94
       calmar            0.68     0.01      0.71      2.23
       ulcer             5.51     3.39      7.36     21.12
       max_dd       14,873.52 8,627.23 14,383.32 27,776.52
       P(Sharpe<=0)       NaN      NaN      0.04       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $13,019      32% $14,566 $22,800 $26,951        100%        100%        100%
longs     $7,693      24%  $9,265 $14,713 $17,668        100%        100%        100%
shorts   $14,874      50% $14,913 $23,889 $28,978        100%        100%        100%
```