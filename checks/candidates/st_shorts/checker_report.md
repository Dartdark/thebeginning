# Checker report: st_shorts

kind filter, pre-registered False, variants 4, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | kept $485.5 (n 281) vs skipped $167.6 (n 321), t 2.31 |
| G2 holdout | PASS | kept - skipped: 2018-22 $+211.6, 2023-26 $+462.5 |
| G3 years | PASS | kept beats skipped in 8/9 years: 2018 +468, 2019 +13, 2020 +121, 2021 +86, 2022 +306, 2023 +216, 2024 +12, 2025 -338, 2026 +2165 |
| G5 placebo | PASS | labels shuffled within years (2,000): p 0.0115 |
| G6 resampling | PASS | kept trades 2023+ P(Sharpe <= 0) 0.000 |
| G7 MinTRL | PASS | 281 trades vs MinTRL 48 |
| G8 regime stability | PASS | rho 0.75 (yearly Sharpe 2018 3.2, 2019 1.0, 2020 0.9, 2021 1.2, 2022 1.5, 2023 1.4, 2024 1.0, 2025 0.6, 2026 4.2) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.360 vs Gaussian 95% 0.391 (ok; permutation p 0.103; 7 groups, n 223); P2 VIX regime (past-only median): SIS 0.292 vs Gaussian 95% 0.280 (DIFFERS; permutation p 0.042; 2 groups, n 231) |

**Gates: 6/7 pass -> FAIL**

## Standard metrics
```
            trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all trades     602 63% $316 $20,779   1.50    2.12          1.62 $15,636   1.33  2.33      17.82
kept           281 67% $486 $14,903   1.50    2.26          1.97 $13,989   1.07  3.17       9.41
kept shorts    281 67% $486 $14,903   1.50    2.26          1.97 $13,989   1.07  3.17       9.41
```
## 2023+ bootstrap
```
                            actual        p5       p50       p95
name        metric                                              
all trades  sharpe            1.60      0.76      1.68      2.62
            sortino           2.25      1.01      2.41      4.12
            pf_day            1.63      1.26      1.67      2.27
            calmar            1.67      0.46      1.53      3.46
            ulcer             4.44      2.65      5.85     14.88
            max_dd       15,636.40 10,742.90 17,443.59 31,591.37
            P(Sharpe<=0)       NaN       NaN      0.00       NaN
kept        sharpe            1.72      0.89      1.70      2.53
            sortino           2.71      1.25      2.66      4.72
            pf_day            2.14      1.48      2.10      3.18
            calmar            1.39      0.70      1.90      4.19
            ulcer             5.54      1.73      3.62      8.29
            max_dd       13,989.31  6,369.53  9,896.87 17,137.10
            P(Sharpe<=0)       NaN       NaN      0.00       NaN
kept shorts sharpe            1.72      0.89      1.70      2.53
            sortino           2.71      1.25      2.66      4.72
            pf_day            2.14      1.48      2.10      3.18
            calmar            1.39      0.70      1.90      4.19
            ulcer             5.54      1.73      3.62      8.29
            max_dd       13,989.31  6,369.53  9,896.87 17,137.10
            P(Sharpe<=0)       NaN       NaN      0.00       NaN
```
## 2023+ drawdown permutation
```
            actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all trades    $15,636      41% $16,707 $26,977 $32,541        100%        100%        100%
kept          $13,989      84% $10,550 $16,988 $21,086        100%        100%        100%
kept shorts   $13,989      84% $10,550 $16,988 $21,086        100%        100%        100%
```