# BTC ADX ensemble (user's Jesse strategy 'BTCAdxEnsembleFree', pasted 2026-11-13)

Candidate: trend following on BTC with two sub-books sharing one position. NOT an NQ strategy: units are R, not dollars.

## Data
`data/BTCUSD_spot_1min_*.csv` (Coinbase spot; date, time in US Central time, stamped at the bar CLOSE). Convert to UTC and to
bar-open times, then build 15m, 1h and 4h candles on UTC boundaries (as an exchange / Jesse does).

## Indicators (closed candles only)
- 1h: ADX(14) and ATR(14) (Wilder, TA-Lib seeding), SuperTrend(period 10, factor 3), Bollinger(20, 2) width in % of the
  middle band = 100 x (upper - lower) / middle.
- 4h: EMA(200) of the close; use the last COMPLETED 4h candle.
- Vol ratio: closes of the 4h candles that OPEN at 16:00 UTC (one per day); log returns; std of the last 20 / std of the
  last 120 (ddof 1); needs >= 62 such closes, else the filter is skipped.

## Signal, at each 1h close (the 15m candle that opens at :45)
side = +1 if close > 4h EMA, else -1. No signal unless: close is on the same side of SuperTrend; Bollinger width < 15;
vol ratio < 1.5 (when available).
Books: levels 40 and 50. A book opens when it is empty, ADX > its level, and the signal side is not against the net side
of the other open book. Entry at that close.

## Book exits, checked on EVERY 15m candle after entry, in this order, filled at that 15m candle's CLOSE
1. stop: low <= entry - 2.5 ATR (long; mirror for short) -> whole book out
2. target: high >= entry + 8 ATR -> whole book out
3. half: high >= entry + 1.5 ATR, once -> half the book out
4. time: 240 hours since entry, or (at an hour end) close on the other side of the 4h EMA -> out
ATR = the 1h ATR(14) at entry. Guard: a real stop 1% beyond the farthest open book stop, filled AT its price, closes every book.

## Costs and units
0.07% of notional per side on every fill (0.05% fee + 0.02% slippage). Result per book trade in R, R = 2.5 x ATR / entry.

## Maker's claim (to break)
773 book trades 2018-06..2026-10, win 39%, +0.25R, PF 1.67, every year positive; book 40 alone t 3.9, book 50 alone t 4.2;
longs +0.33R, shorts +0.17R (2023+ shorts ~0). The ADX level is the edge (PF 1.04 without it; monotonic 25 -> 60).

## Things the maker did NOT check
Jesse's own backtest; perp funding; drawdown at 3% risk per book; whether filling exits at the 15m close (not at the stop /
target price) flatters or hurts; ADX / SuperTrend against a reference implementation; rows are correlated (two books).
`analysis/checker.py` is built for NQ dollars: use the gates that make sense for R units and say which you skipped.
