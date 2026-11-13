# Pre-registration: NQ push-reversal engine + order-flow-entropy gate (2026-11-11)

Source: Vlasiuk & Smirnov, arXiv 2511.06177 (SPY: no effect at short lags; at long lags large pushes are followed by
non-zero responses, and large DOWN pushes are followed by stronger UP responses than the mirror). Ingredient: Singha,
arXiv 2512.15720 (low order-flow entropy -> larger next moves, no direction).
Written and committed BEFORE any result was computed. Script: `analysis/push_reversal_test.py`.

## Primary rule (frozen)
- NQ 1-min RTH bars (`data/NQ_1min_*.csv`, Central time, close-stamped), 08:31-15:00.
- Push at bar i = close[i] - close[i-60] (60-min lag). z = push / sd, sd = std of all 60-min RTH changes over the
  previous 20 sessions (no look-ahead).
- **Long** at the next bar's open on the first bar of the day closing 09:31-14:30 with z <= -2. One trade a day.
- Exit: close of the 60th bar after entry, or 15:55, or stop at entry - 1.0 x sd (filled 1 tick worse).
- Costs: $7.25 + 1 tick per market / stop fill, i.e. $17.25 per NQ round trip.
- Control (not traded): the mirror short on z >= +2. The paper predicts it is weaker.

## Gates (stop at the first that fails)
1. Design 2018-2022: mean net > 0 with t >= 2.0, and random-time placebo (same days, random entry time in the window,
   same exits, 1,000 draws) p < 0.05.
2. One look at the 2023+ holdout: mean net > 0, t >= 1.5.
3. Then the full CLAUDE.md suite, trials.py, checker, benches.

## Ingredient (looked at on the design period only, then frozen)
- Entropy proxy: over the 30 bars before the signal, symbols up / down / flat 1-min closes; Shannon entropy of the
  9 consecutive-pair states. Gate = entropy below the design-period 30th percentile of signal entropies.
- Prediction (from the paper): gated trades show larger |60-min move|; the P&L effect is whatever it is.
- Kept only if gated trades have a higher mean net on design AND the gate keeps >= 30% of trades.

## Information only (design period, never chosen from)
Lag 30 / 120, z 1.5 / 2.5 neighbours printed to show stability, not to pick a version.
