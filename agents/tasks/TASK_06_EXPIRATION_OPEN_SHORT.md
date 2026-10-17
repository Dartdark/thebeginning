# Task 06: Expiration Open Short (NQ, 5-minute bars, shorts only)

Read `tasks/COMMON_NQ.md` first; it applies here. Save output in `tasks/out_06/`.

## Rule

1. **Expiration day** = the **third Friday** of the month (a Friday with day-of-month 15-21). There is one exception:
   if the stock market is closed that Friday, the expiration day is the **Thursday before** it. The closed third
   Fridays in the data are 2019-04-19, 2022-04-15, 2025-04-18 and 2026-06-19; trade none of these.
2. **Entry.** On an expiration day, at the close of the bar stamped **08:30**, if ATR exists, no position is open and no
   trade was taken yet today: sell short 1 contract next bar at market.
3. **Exits.**
   - Stop 0.30 × ATR above entry.
   - Otherwise buy back at the close of the first bar stamped at or after **10:00**.
