# TrendSwingTrader V1, longs only (BTC, 4h) - spec for the checker

Data: `data/BTCUSD_spot_1min_*.csv` (Coinbase spot, US Central time stamped at the bar CLOSE): convert to UTC bar-open times and
build 4h candles on UTC boundaries. 2018-06 -> 2026-10.

Long at a 4h close when EMA(100) < EMA(50) < EMA(21) < close AND ADX(14, Wilder) > 25, flat only. Entry at that close.
Stop = entry - 2 x ATR(14) at entry. Half the position exits at entry + 3 x ATR (resting limit). After the half, the stop moves to
entry, and at each later 4h close it is set to max(close - 2 x ATR(14), entry). Stops / targets walked on 1-min bars from the next
minute, stop before target inside a minute, stop fills at its price (or the open if gapped). Costs 0.05% fee + 0.02% slippage per
side on market / stop fills; the half-off limit pays fee only. Unit: return per trade (fraction of entry), weighted by the halves.
Shorts exist in the original code (mirror) and LOST money (-0.17% a trade, t -0.34): longs-only is a post-hoc choice.

Maker's claim (to break): longs 165 trades, +1.62% a trade, t 3.38; in the personal book (longs on CME Micro Bitcoin) it raised
return / drawdown by +0.93 (2019-26). The longs ride BTC's upward drift: test against a fair benchmark (random long entries at the
same frequency with the same exits, or buy-and-hold over the same holding periods) - that is the main question.
Also: neighbours (ADX 20 / 30, stop 1.5 / 2.5, half 2.5 / 3.5, trail 1.5 / 2.5, EMA sets), by year, concentration.
