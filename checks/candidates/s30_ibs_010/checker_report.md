FAIL (as submitted: the IBS < 0.10 threshold). The IBS mechanism itself replicates exactly and passes every other gate; the 0.10 pick does not survive G9 (PBO 0.71).

**Replication.** `replica.py` was written from spec.md alone: g24 grid, 15-min bars, 26 bars 08:45-15:00, IBS at the 15:00 close, fill at the 15:15 bar open, $7.25 per round trip + 1 tick a fill = $17.25 (the repo convention in grid.py/portfolio.py). Result: **171/171 trades, same entry dates, net identical to the cent (max diff $0.00, corr 1.00)**. My first pass charged $7.25 per side and was off by exactly $7.25 a trade; that was my reading, not a maker error. Spec text says "matched 169 / 169" but trades.csv has 171 rows, so the spec text is stale. One position opened 2026-11-02 is still open at data end and is not in the list.

**Gates** (`analysis/checker.py`, with fills.csv and the 5 sibling thresholds in variants/): G1 PASS (t 5.11 vs t_threshold(374) 3.65; DSR 0.977) · G2 PASS (2018-22 $2,089 t 4.07; 2023-26 $3,003 t 3.21) · G3 PASS (9/9 years; 2026 weakest, Sharpe 0.7) · G4 PASS (without the top 5%: $1,672 a trade) · G5 PASS (maker placebo p 0.000) · G6 PASS (2023+ P(Sharpe<=0) 0.003) · G7 PASS (171 vs MinTRL 21) · G8 PASS (rho 0.81) · **G9 FAIL (CSCV PBO 0.71 over the 6 thresholds 0.05-0.20)** · G10 PASS (100% of fills inside their bar) · G11 PASS (one-bar delay keeps 96% of Sharpe) · G12 n/a (no fitted parts besides the threshold) · G13 PASS (soft). Result 10/11 -> FAIL. Roll-adjusted replica (`../s30_ibs_010_replica/`): G1 t 4.90 / DSR 0.963, G2 2023+ t 2.95, all others the same (G5 there only lacks a placebo file).

**Leak and trap checks.**
- Look-ahead: none. IBS uses only bars up to 15:00, the fill is the next bar's open, and the 15:15 open is inside its bar on 100% of fills. Entering one full session later still gives $1,647 a trade (t 4.06).
- Selection (post hoc, 6 variants, not pre-registered): every threshold makes money (t 3.4-5.1, 0.05-0.30), so the effect is broad. But 0.10 is the in-sample t peak, and PBO 0.71 says the in-sample best threshold usually ranks below median out of sample. The source rule IBS < 0.20 gives $1,492 a trade (t 3.83, still above 3.65; 2023+ t 2.27). Expect that, not $2,436.
- Long-only beta in a bull market: the placebos are my own, 300 runs each. Random entry days per year with the same IBS>0.8 exit: mean $930 (p 0.000). Random entry with hold lengths matched: $490 (p 0.000). Unconditional long drift over the 509 held sessions (23% of sessions) is about $102k, against $420k gross. So the edge is not just drift.
- Contract rolls on raw prices: rolls detected as one-minute jumps of +0.35% (2018-19) and +1% (2022Q3+, 120-308 pts). 4 trades span one (2018-12, 2023-03, 2024-03, 2026-03) and book $12.1k of roll gap. Removing it gives a mean of $2,365 (t 4.90). Small effect, but live rolls need handling.
- Known risk, confirmed: exit-booked max DD is $25.6k. Marked at each 15:15 it is **$45.3k** (matches the spec). Marked on every 1-min close it is **$60.9k**. The worst open excursion was -$42.9k (2025-04-03 entry, closed +$11.7k). That is a marked Calmar of about 1.0 (or 0.76 intraday) on $46.5k a year per NQ. There is no stop, and positions are held through weekends and holidays: personal account only, MNQ sizing.

**What would change my mind.** (1) A pre-registered threshold (the source 0.20) re-submitted: it would likely pass (t 3.83, 2023+ t 2.27); or a PBO <= 0.50 over a wider pre-declared grid. (2) Out-of-sample 2026-11+ trades keeping the mean above about $1,500 a trade at 0.10. (3) A marked-to-market sizing check (the funded/personal bench on the $60.9k intraday DD) showing the account survives the 2025-04 type excursion.

---

# Checker report: s30_ibs_010

kind strategy, pre-registered False, variants 6, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 5.11, PSR 1.000, DSR(N=374) 0.977 |
| G2 holdout | PASS | 2018-22 $2088.9 (t 4.07), 2023-26 $3003.1 (t 3.21) |
| G3 years | PASS | 9/9 years positive: 2018 $6,264, 2019 $23,247, 2020 $93,934, 2021 $38,685, 2022 $59,292, 2023 $61,046, 2024 $40,707, 2025 $72,476, 2026 $20,975 |
| G4 concentration | PASS | without the best 5% of trades: $270,826 total ($1671.8 a trade) vs $416,625 |
| G5 placebo | PASS | 200 placebo runs, mean $952.6; share >= real $2436.4: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.003 |
| G7 MinTRL | PASS | 171 trades vs MinTRL 21 |
| G8 regime stability | PASS | rho 0.81 (yearly Sharpe 2018 0.5, 2019 1.7, 2020 2.9, 2021 1.9, 2022 1.5, 2023 2.4, 2024 1.6, 2025 1.6, 2026 0.7) |
| G9 PBO | FAIL | CSCV over 6 variants, 16 blocks: PBO 0.71 |
| G10 fill sanity | PASS | 100.0% of fills inside their 15-min bar (+/- 2 ticks), clock +0 min |
| G11 one-bar delay | PASS | net $2436 (t 5.1) -> $2372 (t 4.9), Sharpe kept 96% |
| G13 invariance | PASS | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.425 vs Gaussian 95% 0.517 (ok; permutation p 0.208; 3 groups, n 72); P2 VIX regime (past-only median): SIS 0.263 vs Gaussian 95% 0.382 (ok; permutation p 0.334; 2 groups, n 121) |

**Gates: 10/11 pass -> FAIL**

## Standard metrics
```
      trades win    avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      171 74% $2,436 $46,476   1.60    3.18          2.88 $25,571   1.82  2.75      33.80
longs    171 74% $2,436 $46,476   1.60    3.18          2.88 $25,571   1.82  2.75      33.80
```
## 2023+ bootstrap
```
                      actual        p5       p50       p95
name  metric                                              
all   sharpe            1.53      0.69      1.49      2.23
      sortino           2.93      1.06      2.80      5.93
      pf_day            2.82      1.57      2.73      5.42
      calmar            2.03      0.51      1.78      4.64
      ulcer             4.24      2.50      6.86     20.89
      max_dd       24,776.25 14,539.50 26,678.12 50,212.51
      P(Sharpe<=0)       NaN       NaN      0.00       NaN
longs sharpe            1.53      0.69      1.49      2.23
      sortino           2.93      1.06      2.80      5.93
      pf_day            2.82      1.57      2.73      5.42
      calmar            2.03      0.51      1.78      4.64
      ulcer             4.24      2.50      6.86     20.89
      max_dd       24,776.25 14,539.50 26,678.12 50,212.51
      P(Sharpe<=0)       NaN       NaN      0.00       NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all     $24,776      40% $26,670 $42,084 $52,923        100%        100%        100%
longs   $24,776      40% $26,670 $42,084 $52,923        100%        100%        100%
```