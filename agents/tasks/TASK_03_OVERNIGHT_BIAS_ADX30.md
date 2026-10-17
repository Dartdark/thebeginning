# Task 03: Overnight Bias, ADX 30 version (NQ, 15-minute bars, longs and shorts)

Read `tasks/COMMON_NQ.md` first; it applies here. Save output in `tasks/out_03/`.

## Rule

1. **ADX.** ADX(14) with Wilder's smoothing on the 15-minute bars (all bars of the 24-hour session). Initialise each
   smoothed sum with the plain sum / average of its first 14 values. Report exactly how you computed it.
2. **Overnight range.**
   - It starts at the first bar stamped **after 23:00**, i.e. the 23:15 bar.
   - It includes every bar up to and including the bar stamped **08:30** next morning.
   - Overnight high / low = the highest high and lowest low of those bars.
3. **Bias.** On the first bar stamped after 08:30 and at or before 08:45 (the 08:45 bar), take open = that bar's
   **open**. pos = (open − overnight low) / (overnight high − overnight low).
   - pos ≥ 0.6667 → bias **long**.
   - pos ≤ 0.3333 → bias **short**.
   - otherwise no trade today.
4. **Opening range** = the high and low of the bars stamped after 08:30 up to 08:45, which is the 08:45 bar. It is
   complete at the close of the 08:45 bar.
5. **Entry window.** On the close of each bar from the 08:45 bar up to but not including the **last-entry time**
   (14:00; on EARLY days 11:00), if all hold:
   - bias ≠ 0, the opening range is complete, ATR exists;
   - no position is open, and no trade was taken yet today (one trade a day, including a trade that opened and closed
     inside one bar);
   - ADX > 30.

   Then place, for the next bar only (re-place it each bar while the conditions still hold):
   - **Long bias:**
     - if the bar's close ≥ opening-range high − 2 ticks, buy at market next bar;
     - otherwise a buy-stop at the opening-range high.
   - **Short bias:**
     - if the close ≤ opening-range low + 2 ticks, sell at market next bar;
     - otherwise a sell-stop at the opening-range low.
6. **Exits.**
   - Stop = 0.25 × ATR from entry.
   - Target = 3 × that distance.
   - Otherwise close at the close of the first bar stamped at or after the **exit time** (14:30; on EARLY days 11:30).
7. The overnight range, bias and opening range reset at each new date.
