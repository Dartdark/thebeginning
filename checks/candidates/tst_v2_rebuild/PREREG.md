# TrendSwingTrader V2 rebuild by matching (pre-registered 2026-11-13, before any search result)

User: "U can't create the codes urself from ur findings" -> rebuild the premium V2 (no code) from the free V1 code + V2's own
backtest record on jesse.trade (daily equity curves per year from the site's metrics endpoint, user-approved; saved in
scratch_data/jesse_site/).

Family (V2 = "an optimized version", 3 moving averages, BTC 4h): V1's rules with different settings.
 long when EMA_slow < EMA_mid < EMA_fast < close and ADX(14) > A; stop S x ATR(14); half off at T x ATR; then the stop goes to
 entry and trails max(close - R x ATR, entry) on each 4h close (mirror short).
Grid (5,184): fast {9, 13, 21, 30} x mid {34, 50, 70} x slow {100, 150, 200} x A {20, 25, 30, 35} x S {1.5, 2, 2.5, 3} x
 T {2, 3, 4} x R {1.5, 2, 3}. Search fills on 15m bars (stop before target inside a bar) for speed.
Target: V2's in-trade days = days whose equity changed (site daily curve, UTC). Score = F1 between a candidate's in-position
days and V2's, on 2022 + 2023 (2024 excluded: V2's 2024 numbers are byte-identical to V1's). Day alignment (shift -1 / 0 / +1)
fixed first on V1's own code against V1's site curve.
Check (never used to pick): the best candidate's F1 on V2's 2025 curve.
Accept the rebuild if its 2025 F1 is within 0.10 of its 2022-23 F1 and >= 0.6; otherwise report that V2 is not V1 with new
settings. If accepted: test it like any strategy on our data (Coinbase spot 2018-06 -> 2026-10, 1-min fills, costs, by year,
2018-21 = never seen by the author or the match, placebo). Counts as one item with 5,184 variants in trials.py.
