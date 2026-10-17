# Task 09: ES MOC Follow (ES, 5-minute bars, longs and shorts)

Read `tasks/ANTIGRAVITY_BRIEF.md` and `tasks/COMMON_NQ.md` first. COMMON_NQ's conventions apply (Central time, bars
stamped at their close, ATR, EARLY days, fills, output) with the changes below. Save output in `tasks/out_09/`.

## Data (differs from NQ)

- `ES_1min_<year>.csv` (E-mini S&P 500, continuous, not back-adjusted).
- Each file covers the full 24-hour session; there is no separate overnight file.
- Same columns and Central-time stamping as NQ.
- Use the repo copies (`research_scripts/data/` once pulled) or identical `C:\NQData` copies; check and report which.
- 1 contract = $50 per point, tick 0.25.

## Rule

1. **Reference price** = the close of the bar stamped **14:00**. Reset each date.
2. **Signal.** At the close of the bar stamped **14:50**, if all of these hold:
   - today is not an EARLY day;
   - the reference price and ATR exist;
   - no position is open and no trade was taken yet today.

   Then move = that bar's close − reference price. If |move| ≥ 0.30 × ATR, trade 1 contract in the **direction of the
   move**, next bar at market.
3. **Exits.**
   - Stop 0.25 × ATR from entry.
   - Otherwise close at the close of the first bar stamped at or after **15:00**.
