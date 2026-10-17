# Task 05: Monday Long (NQ, 5-minute bars, longs only)

Read `tasks/COMMON_NQ.md` first; it applies here. Save output in `tasks/out_05/`.

## Rule

1. **Early-close Mondays are skipped** (this task's own list; it is NOT the EARLY list). A Monday counts as early-close
   if it is:
   - Jan 1 or Jan 2;
   - Jan 15-21;
   - Feb 15-21;
   - May 25 or later;
   - from 2022, Jun 19 or Jun 20;
   - Jul 4 or Jul 5;
   - Sep 1-7;
   - Dec 25 or Dec 26.
2. **Entry.** On each other Monday, at the close of the bar stamped **08:30**, if ATR exists, no position is open and no
   trade was taken yet today: buy 1 contract next bar at market.
3. **Exits.**
   - Stop 0.50 × ATR below entry.
   - Otherwise sell at the close of the first bar stamped at or after **15:00**.
