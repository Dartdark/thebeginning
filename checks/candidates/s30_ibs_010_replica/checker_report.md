# Checker report: s30_ibs_010_replica

kind strategy, pre-registered False, variants 6, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 4.90, PSR 1.000, DSR(N=374) 0.963 |
| G2 holdout | PASS | 2018-22 $2084.2 (t 4.05), 2023-26 $2824.0 (t 2.95) |
| G3 years | PASS | 9/9 years positive: 2018 $5,769, 2019 $23,247, 2020 $93,934, 2021 $38,685, 2022 $59,292, 2023 $58,616, 2024 $35,797, 2025 $72,476, 2026 $16,670 |
| G4 concentration | PASS | without the best 5% of trades: $258,686 total ($1596.8 a trade) vs $404,485 |
| G5 placebo | FAIL | no placebo.csv supplied (required for a strategy) |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.003 |
| G7 MinTRL | PASS | 171 trades vs MinTRL 23 |
| G8 regime stability | PASS | rho 0.80 (yearly Sharpe 2018 0.4, 2019 1.7, 2020 2.9, 2021 1.9, 2022 1.5, 2023 2.3, 2024 1.4, 2025 1.6, 2026 0.6) |
| G13 invariance | PASS | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.435 vs Gaussian 95% 0.517 (ok; permutation p 0.189; 3 groups, n 72); P2 VIX regime (past-only median): SIS 0.259 vs Gaussian 95% 0.382 (ok; permutation p 0.344; 2 groups, n 121) |

**Gates: 7/8 pass -> FAIL**

## Standard metrics
```
      trades win    avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      171 73% $2,365 $45,122   1.54    2.98          2.78 $29,081   1.55  2.89      31.18
longs    171 73% $2,365 $45,122   1.54    2.98          2.78 $29,081   1.55  2.89      31.18
```
## 2023+ bootstrap
```
                      actual        p5       p50       p95
name  metric                                              
all   sharpe            1.42      0.57      1.38      2.16
      sortino           2.61      0.85      2.50      5.59
      pf_day            2.64      1.45      2.57      5.11
      calmar            1.63      0.39      1.54      4.20
      ulcer             4.85      2.74      7.83     24.40
      max_dd       29,081.25 15,252.25 28,661.00 54,074.14
      P(Sharpe<=0)       NaN       NaN      0.00       NaN
longs sharpe            1.42      0.57      1.38      2.16
      sortino           2.61      0.85      2.50      5.59
      pf_day            2.64      1.45      2.57      5.11
      calmar            1.63      0.39      1.54      4.20
      ulcer             4.85      2.74      7.83     24.40
      max_dd       29,081.25 15,252.25 28,661.00 54,074.14
      P(Sharpe<=0)       NaN       NaN      0.00       NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all     $29,081      52% $28,735 $46,130 $56,258        100%        100%        100%
longs   $29,081      52% $28,735 $46,130 $56,258        100%        100%        100%
```