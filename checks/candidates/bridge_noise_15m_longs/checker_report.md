# Checker report: bridge_noise_15m_longs

kind strategy, pre-registered False, variants 14, N (ranked items in TRIALS.csv) 367, t_threshold(N) 3.64

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 5.54, PSR 1.000, DSR(N=367) 0.993 |
| G2 holdout | PASS | 2018-22 $49.7 (t 3.33), 2023-26 $76.0 (t 4.45) |
| G3 years | PASS | 9/9 years positive: 2018 $5,216, 2019 $3,805, 2020 $6,233, 2021 $26,287, 2022 $22,336, 2023 $39,352, 2024 $16,694, 2025 $24,804, 2026 $17,531 |
| G4 concentration | PASS | without the best 5% of trades: $98,692 total ($40.3 a trade) vs $162,257 |
| G5 placebo | PASS | 200 placebo runs, mean $-11.4; share >= real $62.9: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.000 |
| G7 MinTRL | PASS | 2579 trades vs MinTRL 252 |
| G8 regime stability | PASS | rho 0.80 (yearly Sharpe 2018 0.8, 2019 0.7, 2020 0.7, 2021 2.5, 2022 1.7, 2023 3.1, 2024 1.3, 2025 2.3, 2026 1.3) |
| G9 PBO | FAIL | CSCV over 11 variants, 16 blocks: PBO 0.71 |
| G10 fill sanity | PASS | 100.0% of fills inside their 15-min bar (+/- 2 ticks), clock +0 min |
| G11 one-bar delay | FAIL | net $-23 (t -1.7) -> $54 (t 4.6), Sharpe kept nan% |

**Gates: 9/11 pass -> FAIL**

## Standard metrics
```
      trades win avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all     2579 63% $63 $17,739   1.65    3.29          1.28 $12,204   1.45  2.70      13.16
longs   2579 63% $63 $17,739   1.65    3.29          1.28 $12,204   1.45  2.70      13.16
```
## 2023+ bootstrap
```
                      actual       p5      p50       p95
name  metric                                            
all   sharpe            1.97     1.20     1.98      2.76
      sortino           4.09     2.21     4.13      6.44
      pf_day            1.81     1.43     1.82      2.33
      calmar            2.03     0.98     2.54      5.09
      ulcer             2.42     1.64     3.07      6.68
      max_dd       12,203.50 6,399.68 9,743.00 16,456.17
      P(Sharpe<=0)       NaN      NaN     0.00       NaN
longs sharpe            1.97     1.20     1.98      2.76
      sortino           4.09     2.21     4.13      6.44
      pf_day            1.81     1.43     1.82      2.33
      calmar            2.03     0.98     2.54      5.09
      ulcer             2.42     1.64     3.07      6.68
      max_dd       12,203.50 6,399.68 9,743.00 16,456.17
      P(Sharpe<=0)       NaN      NaN     0.00       NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank   dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all     $12,204      83% $9,456 $14,863 $18,159        100%        100%        100%
longs   $12,204      83% $9,456 $14,863 $18,159        100%        100%        100%
```