# HMA / SMA crossover + RSI + LinReg, BTC 4H (user 2026-11-14: github.com/ZiadFrancis/CoinQuant_Vs_Python_HMA_Strategy, read-only clone).
Written before any result of OUR test. The author's own saved notebook (USE_SMA = True): 2019-02-20 -> 2026-05-10, 131 trades, 35% win,
+964% vs buy-and-hold +1,965%, Sharpe 0.64, max DD -55%, 2 bp commission a side, all-in sizing; the repo's purpose is CoinQuant-vs-Python
parity (it matches), not an edge claim.
Rule (utils.prepare_dataset defaults): 4H bars (UTC, bar-open labels), long only. ENTRY at the bar close when fast MA crosses above slow
MA (HMA 16 / 65 with floor rounding, or SMA 16 / 65) AND RSI14 (Wilder) > 52 AND close > LinReg(50) of the 4H close (the OLS fitted value
at the last bar). EXIT at the bar close when fast crosses below slow. No stop, no target.
Our data: Coinbase spot BTC-USD 1-min (Central, close-stamped -> UTC bar-open, as analysis/btc_adx_ensemble_test.py), 2018-12 -> 2026-10.
Report (both MA kinds): trades, win, avg % a trade, compounded return, CAGR, max DD, daily Sharpe; 2019-22 vs 2023+; buy-and-hold over the
same span; RANDOM-TIMING placebo = the same number of trades with the same holding lengths at random non-overlapping start bars (500 runs):
does the timing beat simply being long ~half the time? Ingredients: without the RSI filter, without the LinReg filter, crossover alone.
Trade match vs the author's CoinQuant log (backtest-trades-sma.csv). Costs: his 2 bp a side AND ours 6 bp a side (0.05% fee + 0.01% slip).
NQ port (multi-day holds: personal account only): the same rule on NQ 4H bars (24h, Central), per NQ, $7.25 + 1 tick a side; data sweep on it.
Pass (BTC, our costs): beats the random-timing placebo at p < 0.05 AND positive in both halves. Not Apex-legal in any form (multi-day).

## Result (2026-11-14, `analysis/outputs/hma_btc4h_test_output.txt`, `analysis/outputs/hma_btc4h_sweep_output.txt`)
Reproduction: SMA version (his saved run) 142 trades, +1,037% at his 2 bp (his +964% on Binance, 131 trades); 116 of his 132 entries
within one 4H bar of ours (exchange / time-stamp differences). Buy-and-hold over the span +1,983%.
SMA, our 6 bp: +915%, CAGR 35%, max DD -56%, Sharpe 0.93 vs buy-and-hold 0.95; random-timing placebo p 0.142 -> NO timing edge (it is
half of buy-and-hold at buy-and-hold's risk-adjusted return). FAIL.
HMA (the repo's name), our 6 bp: 246 trades, +647%, CAGR 30%, max DD -32%, Sharpe 1.06 vs 0.95, in the market 24% of the time; 2019-22
Sharpe 1.07 (B&H 0.88), 2023+ 1.09 (B&H 1.13); random-timing placebo p 0.004 -> PASSES the pre-registered gate (beats random timing,
positive in both halves). Its value is risk control (drawdown -32% vs ~-77% for holding), not more return. The RSI filter matters (without
it max DD -76%); the LinReg filter does nothing.
NQ port (personal, multi-day): SMA $2,113 a trade t 1.63, HMA $581 t 1.39; both below NQ long-only; data sweep p 0.68 (luck). FAIL.
Use: BTC only, multi-day, long only -> personal account (CME micro bitcoin futures would need its own test: rolls, CME hours). C+.
