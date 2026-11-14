# Jesse CLMeanReversion on CME crude (pre-registered 2026-11-13, before any result)

Source: jesse.trade/strategies/clmeanreversion (free, @saleh; code read logged in, user 2026-11-13) and the premium page's
description. The author fitted it on CL-USDT perp May-Jul 2026 (prompt: "Sharpe >= 1.5 from May to July", optimised): BB(40, 3.45),
stop 3.43 x ATR(14) of the last COMPLETED 1h candle, 3% risk. So 2018-01 .. 2026-04 is out of the author's sample.

Rule (free, as coded): on each 30m close, flat: close < lower BB(40, 3.45) -> buy at the close; close > upper -> sell. Stop at
entry -/+ 3.43 x ATR(14, 1h completed). Take profit = the middle band at entry (resting limit). Also on every 30m close: long and
close >= current middle band -> out at the close (short mirror).
Fills (CME CL 1-min, Central time): market at the 30m close +-1 tick; stop at its price (or the open if gapped) -1 tick; target
limit on touch, no slippage; stop checked before target inside a minute. Costs $7.25 a CL a round trip + 1 tick ($10) a
market / stop fill. Rolls: back-adjusted by difference (largest reopen gap on days 10-26 of each month if > 4x the median).
30m and 1h bars on clock boundaries; CL's 16:00-17:00 CT break simply has no bars.

Variants (6, fixed):
- V0 as coded (both sides, 24h)
- V1 premium as described: V0 + fade only with the 1h EMA trend (long only if the last completed 1h close > EMA(50) of 1h
  closes, short only if below); EMA length is not given: 50 chosen here, 20 / 100 shown as sensitivity only
- V2 Apex-legal V0: every position out at the 15:30-15:45 CT bar close (well before 15:59), no entries 15:00-17:00 CT
- V3 Apex-legal V1
- V4 / V5 longs only / shorts only of V0 (slices)
Placebo: V0 entry moments with a random side (100 runs). Pass bar for 'promising': V0 or V1 t >= 2 after costs with both 2018-22
and 2023+ positive and beating the placebo p < 0.05; above C needs t >= metrics.t_threshold(N_items) or this pre-registration's
t >= 2 + clean placebo + checker.
