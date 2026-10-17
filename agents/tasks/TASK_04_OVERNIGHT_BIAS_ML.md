# Task 04: Overnight Bias with an ML day filter (NQ, 15-minute bars, longs and shorts)

Read `tasks/COMMON_NQ.md` and `tasks/TASK_03_OVERNIGHT_BIAS_ADX30.md` first. This is Task 03's rule with different
settings plus a "skip today" score. Save output in `tasks/out_04/`.

## Changes from Task 03

- ADX threshold **20** (instead of 30).
- Stop = **0.30** × ATR (instead of 0.25); target still 3 × the stop distance.
- Longs only on days with score ≥ **0.03**; shorts only on days with score ≥ **0**.
- **No trades at all** on days where the score can't be computed yet (fewer than 59 stored trading days).

## Stored history (updated when a new date starts)

During each date, track:
- `open830` = the open of the first bar stamped after 08:30 and at or before 08:45;
- `close1500` = the close of the last bar stamped at or before 15:00;
- whether the date had a bar stamped from 11:00 to 15:15.

When a new date starts, store the date that just ended as a **trading day** if all of these hold:
- it was Monday-Friday;
- it had a bar stamped 11:00-15:15;
- `close1500` and `open830` both exist.

For each stored day keep, most recent first:
- `C[k]` = close1500;
- `O[k]` = open830;
- `A[k]` = the 15-day ATR as it stood on the **last bar of that date**, before the new date's true range is added.

## Today's score (computed on the first bar of each date, once at least 59 days are stored)

Inputs, with ATR = today's ATR (the new date's value, after the previous date's TR was added) and ln = natural log:
- ret1 = ln(C[0] / C[1]); ret5 = ln(C[0] / C[5]); ret20 = ln(C[0] / C[20])
- rth1 = ln(C[0] / O[0])
- atr_ratio = ATR / ((ATR + A[0] + ... + A[58]) / 60)
- dist50 = ln(C[0] / average(C[0..49]))
- r_k = ln(C[k] / C[k+1]) for k = 0..19; rv = sample st.dev.(r_0..r_4) / sample st.dev.(r_0..r_19), with
  denominators 4 and 19 (rv = 1 if the second is 0)
- dow = today's weekday (Mon = 1 ... Fri = 5)
- tdm3 = 1 if today is among the first 3 trading days of its month, counting stored trading days (today = 1 if the
  last stored day was in another month, else the number of stored days so far this month + 1)
- opex = 1 if today is Monday-Friday and the Friday of today's week has day-of-month 15-21

```
score = 0.05535517974
      + 2.550842376  * ret1   + 0.05697325462 * ret5   - 0.08269967616 * ret20
      + 1.729498386  * rth1   - 0.03608247696 * atr_ratio - 0.3355796551 * dist50
      - 0.03976333906 * rv
      + 0.07809504609 * [dow=1] - 0.008560935801 * [dow=2] - 0.02267574106 * [dow=3]
      - 0.03459885088 * [dow=4] - 0.005544247888 * [dow=5]
      + 0.1654566373 * tdm3   - 0.003794081905 * opex
```

Add a `score` column to trades.csv, and report the score on every trading day in `tasks/out_04/scores.csv`
(`date,score`).
