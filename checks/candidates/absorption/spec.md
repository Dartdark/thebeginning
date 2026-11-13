# Order-flow absorption, NQ (2026-11-08)
 (header committed before the
first run; 1 variant; new mechanism, not in TIER_LIST).
Mechanism: price normally moves with net aggressive flow (Kyle 1985; Cont, Kukanov & Stoikov 2014: price change ~ order-flow imbalance).
When the first two RTH hours' price move is much WEAKER than its aggressor delta implies, large passive orders are absorbing the
aggression (a seller working limit orders under buying, or the mirror); that inventory is still being worked, so the rest of the day
should follow the price, not the flow. Prediction: trade in the direction of the price-vs-flow residual.
Rule (The Bridge's NQ aggressor volume, data/OF_1min_*, RTH 9:30-16:15 ET = 8:30-15:15 CT, ends 2026-07-07):
  per day: P = NQ close of the 10:29 CT bar - open of the 8:30 bar (points); F = sum of (up - down aggressor volume) over 8:30-10:29 CT.
  past-only fit over the previous 60 trading days: P = a + b x F (OLS); residual sd s. Z = (P - a - b x F) / s.
  |Z| >= 1.0 -> enter at the 10:31 CT bar's open in the direction of sign(Z); stop 0.3 x ATR15 (daily, known that morning); no target;
  out at the 14:55 CT close. CME early-close days skipped. Costs $7.25 + 1 tick per NQ market / stop fill.

