# Task 02: Vault Break (NQ, 30-minute bars, longs only)

Read `tasks/COMMON_NQ.md` first; it applies here. Save output in `tasks/out_02/`.

## Rule

1. **Session open.** The open of the **first bar of each date**. That is the bar stamped 00:00, which covers 23:30 to
   00:00, if it has trades.
2. **VWAP from midnight.** From the first bar of each date, cumulative sum of (high + low + close) / 3 × volume of each
   30-minute bar, divided by cumulative volume. Reset at each new date.
3. **Noise level** = session open + 0.30 × ATR (15-day ATR as in COMMON_NQ).
4. **Entry.** On the close of any bar stamped from **10:00** up to but not including the **last-entry time** (14:30; on
   EARLY days 11:00), buy 1 contract **next bar at market**, if all of these hold:
   - no position is open;
   - trades taken today < 3 (closed trades this date plus one if a position is open);
   - bar close > noise level;
   - bar close > VWAP.
5. **Exits.**
   - Stop 75 points below entry.
   - Target 40 points above entry.
   - Otherwise sell at the close of the first bar stamped at or after the **flatten time** (14:30; on EARLY days 11:30).
6. After an exit the rule may enter again the same date (up to 3 trades) under the same conditions.
