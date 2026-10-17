# Task 08: NFP Fade (NQ, 5-minute bars, longs and shorts)

Read `tasks/COMMON_NQ.md` first; it applies here. Save output in `tasks/out_08/`.

## Rule

1. **Reference price** = the close of the bar stamped **07:30**. Reset each date.
2. **Release spike.**
   - On every Monday-Friday date, take the range (high − low) of the bar stamped **07:35**.
   - Compare it with the **median of the previous 20 such ranges**, not counting today's; with an even count, the
     median is the average of the middle two.
   - It is a spike if range > 3.0 × that median. No spike can be flagged until 20 earlier ranges exist.
   - Then add today's range to the history.
   - The spike flag resets each date.
3. **Entry.** At the close of the bar stamped **07:45**, if all of these hold:
   - today is a **Friday** with day-of-month ≤ 10;
   - today's 07:35 bar was a spike;
   - the reference price and ATR exist;
   - no position is open and no trade was taken yet today.

   Then reaction = that bar's close − reference price:
   - reaction > 0 → sell short 1 contract next bar at market;
   - reaction < 0 → buy 1 contract next bar at market;
   - reaction = 0 → no trade.
4. **Exits.**
   - Stop 0.50 × ATR from entry.
   - Otherwise close at the close of the first bar stamped at or after **09:00**.
