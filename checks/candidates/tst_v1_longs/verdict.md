PASS WITH CONCERNS - more than BTC drift (random-entry p < 0.005), but G1 deflated significance FAILS (t 3.38 < 3.71, DSR 0.64), so not above C; 2025-26 indistinguishable from random.

**Replication** (`replica.py`, spec only; 1-min Coinbase CT bar-close stamps -> UTC bar-open, 4h UTC candles, talib-style EMA / Wilder ATR, ADX).
Replica 168 trades +1.57% a trade, t 3.28 vs maker 165, +1.62%, t 3.38. Entry-time match 163/165 maker trades (98.8%), 163/168 replica
(97.0%); on the 163 matched, net corr 1.0000, max |diff| < 0.2 pp. Mismatches: 2018-07-17 (warm-up, one candle apart), 2021-06-15 20:00
(EMA50-EMA100 gap $5.9: knife-edge), 2022-12-14 x2 and 2023-01-07 vs maker's 2023-01-12 (ADX 26-37, stack true in my data: maker probably
computes indicators on a finite candle window, as jesse does; spec ambiguity, not an error). Maker's `tx` is consistently one candle
before the candle where the stop fills (labelling only; nets identical).

**Drift benchmarks (replica, 2018-06 -> 2026-10)**
- (a) random long entries, same exits, same frequency (p 0.0134 per flat bar, 175 trades, 200 runs): +0.43% a trade (5-95% -0.14..+1.11).
  Strategy excess +1.13% a trade, 0/200 runs >= strategy (p < 0.005, z 2.9). 2018-22: +1.81 vs +0.37 (p < 0.005); 2023+: +1.28 vs +0.47
  (p 0.040); 2025-26: +0.24 vs -0.10 (p 0.225). Saved as `placebo.csv` (G5).
- (b) buy-and-hold over each trade's exact window (entry close -> exit minute, 0.14% round trip): +2.04% a trade, i.e. MORE than the
  strategy (excess -0.48%, t -1.89). The half-off at 3 ATR costs return; the edge is all in the entry timing. (Exposure-matched B&H,
  +1.54%, is near-tautological: same exit times.) Unconditional drift over the average 33-bar hold is only +0.71%.
- (c) filter removed, same exits: no filter +0.19% a trade (excess +1.38, Welch p 0.006); ADX only +0.45% (p 0.023); EMA stack only
  +0.90% (p 0.14 - the ADX adds little that is significant; the EMA stack does the work).
- Daily mark-to-market vs BTC: CAGR 31% / vol 26% / Sharpe 1.19 / max DD -43% vs B&H 35% / 63% / 0.80 / -76%; B&H scaled to the same
  vol 19% CAGR, DD -41%. Regression on daily BTC: beta 0.20, alpha +20%/yr (t 2.65); 2023+ alpha +13.5%/yr (t 1.58).

**Gates** (`run_gates.py` = analysis/checker.py with leak_checks patched TICK 0.01 / PV 1 for BTCUSD_spot; plain checker.py raises KeyError).
Maker trades: G1 FAIL (t 3.38, DSR(N=487) 0.638; t_threshold 3.71) | G2 PASS (2018-22 t 2.58, 2023-26 t 2.26) | G3 PASS 8/9 years
(2018 neg.) | G4 PASS (without best 5%: +0.79% a trade, t 1.91; top 5 trades = 35% of total) | G5 PASS (random placebo 0.000) | G6 PASS
(P(Sharpe<=0) 0.016) | G7 PASS (165 vs 35) | G8 PASS (rho 0.67) | G9 skipped (no variant lists) | G10 PASS (100% fills in bar) | G11 PASS
(next-minute entry keeps 100%) | G12 skipped (nothing fitted) | G13 CONCERN (VIX-regime split differs, p 0.009). Replica: same, G1 t 3.28 /
DSR 0.60. Units: the "$" columns in checker_report.md are fractions (print as $0.0). Tool defect: checker's daily() reindexes to
business days and silently drops 34/165 weekend-dated trades from G6/G8; on calendar days G6 0.009, G8 rho 0.72 (same verdict).

**Leaks / traps checked.** Entry = close of the signal candle; indicators use that candle (fine for 24/7 spot); entry at the next 1-min
open: identical (+1.57%); one full 4h candle later: +1.35%, t 2.87. Costs x2: +1.43%, t 3.00. Stop / target walked from the next minute,
stop first; no trade exits inside its entry candle. DST: fall-back hour has one copy in the data (1440 rows), negligible. Neighbours all
positive, t 2.3-3.6 (ADX 20 +0.92 / 30 +1.42; stop 1.5 +1.00 / 2.5 +1.45; half 2.5 +1.36 / 3.5 +1.70; trail 1.5 +1.36 / 2.5 +1.69;
EMA 10/30/60 +1.13, 20/50/200 +1.52, 9/21/55 +1.11, 30/60/120 +1.41; ratcheting trail +1.38 t 3.55). By year: 2018 -0.88, 2019 +1.34,
2020 +3.40, 2021 +2.44, 2022 +0.19, 2023 +2.21, 2024 +1.77, 2025 +0.14, 2026 +0.36 (% a trade). Longs-only is post hoc (shorts lost).

**Not verified:** the +0.93 return/DD in the personal book and the CME Micro Bitcoin execution: 35/168 entries fall on weekends when
CME is shut, and futures basis/roll differ from spot.

**What would change my mind:** (1) 2025-26 staying flat (p 0.23 vs random) - the edge may be decaying; (2) CME MBT replay with weekend
entries moved to the Sunday open - if the excess over random drops below ~0.5% a trade it is drift; (3) a pre-registered forward run
reaching t >= 3.71 (or the 2023+ alpha t 1.58 rising above 2).
