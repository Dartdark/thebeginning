# Checker report: noise_volexit

kind strategy, pre-registered True, variants 2, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 3.38, PSR 0.999, DSR(N=374) 0.657 |
| G2 holdout | PASS | 2018-22 $37.5 (t 2.00), 2023-26 $85.5 (t 2.73) |
| G3 years | PASS | 8/9 years positive: 2018 $2,164, 2019 $2,550, 2020 $-7,026, 2021 $26,686, 2022 $20,968, 2023 $39,327, 2024 $9,055, 2025 $16,534, 2026 $18,056 |
| G4 concentration | FAIL | without the best 5% of trades: $-31,777 total ($-15.3 a trade) vs $128,314 |
| G5 placebo | FAIL | no placebo.csv supplied (required for a strategy) |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.002 |
| G7 MinTRL | PASS | 2180 trades vs MinTRL 551 |
| G8 regime stability | PASS | rho 0.66 (yearly Sharpe 2018 0.3, 2019 0.5, 2020 -0.6, 2021 2.3, 2022 1.4, 2023 2.9, 2024 0.7, 2025 1.0, 2026 1.0) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.165 vs Gaussian 95% 0.145 (DIFFERS; permutation p 0.001; 9 groups, n 2130); P2 VIX regime (past-only median): SIS 0.147 vs Gaussian 95% 0.094 (DIFFERS; permutation p 0.002; 2 groups, n 2130) |

**Gates: 6/8 pass -> FAIL**

## Standard metrics
```
      trades win avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all     2180 57% $59 $14,016   1.09    1.95          1.20 $22,876   0.61  6.17       4.54
longs   2180 57% $59 $14,016   1.09    1.95          1.20 $22,876   0.61  6.17       4.54
```
## 2023+ bootstrap
```
                      actual       p5       p50       p95
name  metric                                             
all   sharpe            1.34     0.63      1.44      2.22
      sortino           2.56     1.09      2.84      4.94
      pf_day            1.51     1.21      1.56      2.01
      calmar            0.91     0.42      1.41      3.32
      ulcer             6.66     2.60      5.39     13.77
      max_dd       22,875.81 9,449.72 15,540.98 27,140.46
      P(Sharpe<=0)       NaN      NaN      0.00       NaN
longs sharpe            1.34     0.63      1.44      2.22
      sortino           2.56     1.09      2.84      4.94
      pf_day            1.51     1.21      1.56      2.01
      calmar            0.91     0.42      1.41      3.32
      ulcer             6.66     2.60      5.39     13.77
      max_dd       22,875.81 9,449.72 15,540.98 27,140.46
      P(Sharpe<=0)       NaN      NaN      0.00       NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all     $22,876      94% $14,557 $23,179 $27,610        100%        100%        100%
longs   $22,876      94% $14,557 $23,179 $27,610        100%        100%        100%
```