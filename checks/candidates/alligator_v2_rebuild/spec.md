# AlligatorV2 rebuild (BTC, 30m) - spec for the checker

Data: `data/BTCUSD_spot_1min_*.csv` (Coinbase spot, US Central time stamped at the bar CLOSE): convert to UTC bar-open times and
build 30m and 4h candles on UTC boundaries (as Jesse). 2018-06 -> 2026-10.

Indicators on 30m (closed candles): ADX(14) and ATR(14) Wilder; CMO(14) on close; Stochastic RSI k: RSI(14, Wilder) -> stochastic
over 14 -> 3-period SMA (Jesse srsi defaults); Alligator on close: SMMA(13) shifted 8 (jaw), SMMA(8) shifted 5 (teeth), SMMA(5)
shifted 3 (lips). On 4h: the same Alligator from COMPLETED 4h candles; EMA(50) of 4h closes INCLUDING the forming 4h candle
(the last completed EMA stepped once with the current 30m close, as Jesse's get_candles('4h') includes the forming candle).

Long at a 30m close when: close > lips > teeth > jaw (30m) AND the same order on the 4h Alligator AND ADX > 40 AND close > 4h EMA50
AND CMO > 20 AND StochRSI k < 20. Short: the mirror (all reversed, CMO < -20, k > 80). Flat only (one position at a time).
Entry at that 30m close (market). Stop = entry -/+ 3 x ATR(14, 30m) at entry; target = entry +/- 2 x ATR. Both rest; walked on
1-min bars from the next minute, stop before target inside a minute, stop fills at its price (or the open if gapped through).
Costs: 0.05% fee + 0.02% slippage per side on market / stop fills; target fills fee only. Unit: return per trade (fraction).

Maker's claim (to break): 352 trades, win 70%, +0.39% a trade, PF 1.56, t 3.32; 2018-21 t 2.55, 2022-23 t 1.80, 2024-26 t 1.21;
longs t 2.33, shorts t 2.42; random-side placebo p 0.00.
How it was found: the settings (ADX 40, CMO 20, StochRSI 20, stop 3, target 2, 4h EMA 50) were picked out of 2,160 by matching
the PREMIUM strategy's published daily in-trade days in 2022-23 (not by return). 2018-21 was never used.
Check especially: look-ahead in the 4h forming-candle EMA and the 4h Alligator; ADX / SMMA / StochRSI definitions; fill rules;
how much rests on the 2:3 target:stop geometry (high win rate, small target); concentration by year; neighbours (ADX 35 / 45,
stop 2.5 / 3.5, target 1.5 / 2.5, CMO 10 / 30, StochRSI 10 / 30).
