PASS WITH CONCERNS: the rebuild is faithful and I found no leak, but G1 (DSR) fails, the edge decays after 2023, and it is sensitive to costs.

**Replication.** `replica.py` was written from spec.md only (Coinbase 1m, converted CT bar close -> UTC bar open; 30m/4h UTC candles). It matches **352/352 trades** (entry time + side, 100%). Net returns correlate at 1.000000 (max diff 1e-5, from ATR warm-up), exit types match 100%, result n 352, win 70%, +0.389%/trade, PF 1.56, t 3.32. Two points the spec does not pin down: (a) CMO. A 100% match needs **textbook CMO (simple 14-bar sums)**. The talib-style Wilder CMO (what Jesse's `cmo` calls) matches 88% and does *better* (n 396, t 4.03), so this choice does not flatter the result. (b) Re-entry is allowed at the close of the 30m candle in which the exit happened. Disallowing it gives n 350, t 3.39. The maker's `tx` is my exit candle +30 min (a labelling convention only).

**Gates** (`checker.py`, with my 300-run random-side placebo.csv): G1 **FAIL**: t 3.32 < t_threshold(487) 3.71, DSR 0.591. The pre-registration exemption needs <= 3 variants and this search had 2,160. G2 PASS (2018-22 t 2.76, 2023-26 t 1.88). G3 PASS (8/9 years, 2021 -1.9%). G4 PASS (without best 5%: +0.18%/trade, t 1.64). G5 PASS (placebo p 0.000). G6 PASS (2023+ P(Sharpe<=0) 0.044). G7 PASS (352 vs MinTRL 118). G8 PASS (rho 0.77). G13 ok. The "$" amounts in the report are fractions rounded to $0, so ignore the dollar formatting. **Skipped:** G9 (no variant lists), G10/G11 via leak_checks (it has no BTCUSD tick or point value; I ran both by hand, below), G12 (nothing was fitted on returns: the settings were fitted to the premium's in-trade days).

**Leak checks.**
- 4h EMA50 (forming-candle step): the filter **never binds**. Forming, completed-only, one candle later and even a deliberate leak using the final close give the identical 352 trades. It can neither leak nor help.
- 4h Alligator one completed candle later: n 332, t 3.23. Two later: t 2.64. The "forming final" leak version matches only 96%, so the maker used completed candles.
- 30m entry one bar later: t 3.82. Two bars later: t 3.31. Hand-run G11: the Sharpe holds.
- Fills: 100% of entries and exits fall inside their 1m bar. No same-minute exits, median hold 7.4 h. 2 trades span data gaps over 30 min (net -1.0%). Stops gapped through fill at the open: the worst loss is -15.8% on the 2021-05-19 crash (3 ATR was about 15%).
- Random times plus random side with the same 2:3 geometry: mean -0.11%/trade. Random side at the real signal times: -0.06%. The geometry alone loses money, so the edge comes from the signal.

**Neighbours** (t): ADX 35/45 2.92/2.95; CMO 10/30 3.59/3.48; StochRSI 10/30 3.06/2.43; stop 2.5/3.5 3.06/3.79; target 1.5/2.5 2.78/3.20; stop 2/target 3 1.93; EMA 30/100 3.32/3.36. Every neighbour is positive, so the result is a plateau, not a spike.

**By period.**
- Years (mean/trade): 2018 +0.81%, 2019 +0.53%, 2020 +0.70%, 2021 -0.05%, 2022 +0.50%, 2023 +0.34%, 2024 +0.23%, 2025 +0.18%, 2026 +0.14%.
- Splits: unseen 2018-21 t 2.55; matching window 2022-23 t 1.80; 2024-26 t 1.21.
- Sides: longs t 2.33 (+0.29%), shorts t 2.42 (+0.51%).
- Concentration: best year (2020) removed gives t 2.70. Top 10 trades are 35% of the total. Winsorised 1/99 gives t 3.79.

**What would most change my mind.**
1. **Costs.** At 2x (0.14% a side) the full sample is t 2.23 but 2023+ is t 0.86. At 3x 2023+ is t -0.16. Retail Coinbase taker fees are far above 0.05%, so the venue and fee tier decide whether this is real.
2. **Decay and venue.** The mean per trade falls every year since 2022 (2026 t 0.58). 87 entries happen while CME is closed and 57 trades are held over a Saturday. On a CME-feasible subset I get n 258, t 2.46, so the edge survives if traded on CME, but more thinly.
3. **Significance.** This passes only if the premium-matching selection is accepted as non-return selection. The premium itself is a survivor that jesse.trade chose to publish, so its selection bias is inherited. The clean evidence is 2018-21 (t 2.55, never used), not the full-sample t 3.32.
