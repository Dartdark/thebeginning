# Checker report: pt_late

kind strategy, pre-registered True, variants 3, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 3.64, PSR 1.000, DSR(N=374) 0.737 |
| G2 holdout | PASS | 2018-22 $311.3 (t 3.22), 2023-26 $308.7 (t 2.03) |
| G3 years | PASS | 8/9 years positive: 2018 $11,653, 2019 $-8,335, 2020 $17,163, 2021 $32,572, 2022 $42,506, 2023 $8,636, 2024 $29,290, 2025 $5,334, 2026 $27,733 |
| G4 concentration | PASS | without the best 5% of trades: $36,857 total ($72.3 a trade) vs $166,551 |
| G5 placebo | PASS | 100 placebo runs, mean $-2.8; share >= real $310.2: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.011 |
| G7 MinTRL | PASS | 537 trades vs MinTRL 123 |
| G8 regime stability | PASS | rho 0.61 (yearly Sharpe 2018 1.5, 2019 -1.3, 2020 1.2, 2021 3.1, 2022 1.9, 2023 0.8, 2024 1.6, 2025 0.3, 2026 1.2) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.300 vs Gaussian 95% 0.281 (DIFFERS; permutation p 0.052; 8 groups, n 476); P2 VIX regime (past-only median): SIS 0.242 vs Gaussian 95% 0.198 (DIFFERS; permutation p 0.013; 2 groups, n 487) |

**Gates: 8/8 pass -> PASS**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       537 60% $310 $18,193   1.19    1.83          1.60 $19,888   0.91  6.25       5.82
longs     305 64% $368 $12,258   1.22    1.96          1.95 $15,991   0.77  4.94       4.97
shorts    232 54% $234  $5,935   0.51    0.76          1.34 $26,536   0.22  9.07       1.31
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe            1.01      0.28      1.05      1.81
       sortino           1.56      0.38      1.64      3.21
       pf_day            1.45      1.10      1.46      1.98
       calmar            1.07      0.17      1.01      2.52
       ulcer             6.33      3.36      7.27     19.89
       max_dd       16,704.25 11,046.09 18,183.88 34,163.20
       P(Sharpe<=0)       NaN       NaN      0.01       NaN
longs  sharpe            1.19      0.53      1.25      2.05
       sortino           1.85      0.73      1.97      4.06
       pf_day            1.83      1.30      1.91      3.01
       calmar            0.91      0.35      1.36      3.41
       ulcer             8.04      1.85      4.37     11.69
       max_dd       15,991.25  6,383.52 11,108.00 20,582.40
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
shorts sharpe            0.26     -0.66      0.24      1.11
       sortino           0.40     -0.86      0.37      2.12
       pf_day            1.15      0.70      1.13      1.81
       calmar            0.13     -0.20      0.13      1.12
       ulcer            16.40      5.62     15.59     47.64
       max_dd       26,536.25 11,453.24 22,931.62 47,830.45
       P(Sharpe<=0)       NaN       NaN      0.33       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $16,704      22% $20,472 $32,617 $40,157        100%        100%        100%
longs    $15,991      79% $12,816 $20,296 $25,045        100%        100%        100%
shorts   $26,536      79% $20,891 $32,005 $36,459        100%        100%        100%
```