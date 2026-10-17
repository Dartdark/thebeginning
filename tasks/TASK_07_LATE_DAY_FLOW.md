# Task 07: Late-Day Flow (NQ, 5-minute bars, longs and shorts)

Read `tasks/COMMON_NQ.md` first; it applies here. Save output in `tasks/out_07/`.

## Rule

1. **Session open** = the open of the bar stamped **08:35** (the 08:30-08:35 bar). Reset each date.
2. **Signal.** At the close of the bar stamped **14:00**, if all of these hold:
   - today is not an EARLY day;
   - the session open exists and ATR exists;
   - no position is open and no trade was taken yet today.

   Then move = that bar's close − session open. If |move| ≥ 0.40 × ATR, trade 1 contract in the **direction of the
   move** (buy if up, sell short if down) next bar at market.
3. **Exits.**
   - Stop 0.25 × ATR from entry.
   - Otherwise close at the close of the first bar stamped at or after **14:30**.
