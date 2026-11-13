# Checker report: dt_notarget

kind strategy, pre-registered True, variants 3, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 4.37, PSR 1.000, DSR(N=374) 0.946 |
| G2 holdout | PASS | 2018-22 $181.3 (t 3.47), 2023-26 $225.6 (t 2.83) |
| G3 years | PASS | 9/9 years positive: 2018 $39,028, 2019 $17,080, 2020 $19,023, 2021 $22,582, 2022 $63,290, 2023 $23,820, 2024 $86,758, 2025 $33,709, 2026 $21,554 |
| G4 concentration | FAIL | without the best 5% of trades: $-154,872 total ($-100.5 a trade) vs $326,843 |
| G5 placebo | PASS | 100 placebo runs, mean $49.9; share >= real $201.4: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.000 |
| G7 MinTRL | PASS | 1623 trades vs MinTRL 177 |
| G8 regime stability | PASS | rho 0.83 (yearly Sharpe 2018 2.4, 2019 1.5, 2020 0.9, 2021 1.1, 2022 2.0, 2023 1.0, 2024 2.8, 2025 1.0, 2026 0.8) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.232 vs Gaussian 95% 0.167 (DIFFERS; permutation p 0.000; 9 groups, n 1573); P2 VIX regime (past-only median): SIS 0.120 vs Gaussian 95% 0.109 (DIFFERS; permutation p 0.023; 2 groups, n 1573) |

**Gates: 7/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      1623 40% $201 $35,702   1.44    3.61          1.36 $27,353   1.31  2.70      26.45
longs     826 43% $178 $16,040   1.04    2.33          1.34 $21,693   0.74  3.34       9.61
shorts    797 37% $226 $19,662   1.01    2.77          1.39 $23,186   0.85  7.47       5.27
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe            1.42      0.77      1.44      2.04
       sortino           3.79      1.88      3.83      5.85
       pf_day            1.35      1.17      1.35      1.55
       calmar            1.52      0.64      1.80      3.56
       ulcer             5.48      3.48      6.63     15.40
       max_dd       27,353.00 15,478.74 23,461.75 39,990.10
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
longs  sharpe            0.84      0.06      0.83      1.50
       sortino           1.91      0.13      1.91      3.71
       pf_day            1.25      1.02      1.25      1.50
       calmar            0.69      0.04      0.76      2.06
       ulcer             7.04      4.21      8.99     25.06
       max_dd       21,693.00 12,204.23 19,688.00 37,008.28
       P(Sharpe<=0)       NaN       NaN      0.04       NaN
shorts sharpe            1.14      0.44      1.15      1.82
       sortino           3.45      1.16      3.45      6.29
       pf_day            1.45      1.15      1.45      1.84
       calmar            1.33      0.30      1.28      3.13
       ulcer             8.01      3.63      7.54     19.24
       max_dd       20,195.00 13,217.44 20,693.12 37,040.82
       P(Sharpe<=0)       NaN       NaN      0.01       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $27,353      55% $26,512 $41,405 $49,095        100%        100%        100%
longs    $21,693      51% $21,453 $34,861 $39,831        100%        100%        100%
shorts   $20,195      39% $21,577 $34,445 $41,664        100%        100%        100%
```