# Lab Q010: 6E month-end hedge rebalancing, direction from the month's US equity move (pre-registered 2026-11-01,
before any return; parent Q003)

**Mechanism.** Melvin & Prins (2015): foreign investors hedge the dollar value of their US equity holdings and reset the
hedges at month-end, mostly through the 4 pm London fix. If US stocks rose over the month, the hedge is too small, so they
sell more USD forward (buy EUR) at month-end -> 6E up into the fix; if stocks fell, 6E down. The side is known before the
day starts, unlike Q003 (which followed the pre-fix price move).

**Signal.** ES month-to-date = ES close of the 08:30 CT bar on the trade day / ES close of the 15:00 CT bar on the last ES
session of the previous month - 1 (ge.pkl). Side = +1 (long 6E) if > 0, -1 if < 0, skip if 0 or missing.
**Days.** Month-end = the last 6E weekday session of the month (as Q003). Fix F = 16:00 London in CT (Q003 `fix_col`).

**Rule (1 6E, $125,000 a point, tick 0.00005 = $6.25; no stop).**
- V1: month-end day, entry at the open of bar 0831 (08:30 CT), exit at the close of bar F.
- V2: month-end day, entry at the open of bar F-29, exit at the close of bar F.
- V3: V1 on each of the last 2 sessions of the month (signal recomputed each day at 08:30).

**Costs.** $5 + 1 tick per fill = $17.50 a round trip.

**Gates.** Stage 1 (2018-22): best t >= 2.0, PF >= 1.15, >= 40 trades. Stage 2: (a) random-day placebo: the same variant
on random non-month-end sessions (same count, signal = ES change since the previous month-end, 500 draws), p < 0.05;
(b) >= 4 of 5 years positive. Mid-month control (first session on or after the 15th) reported alongside. Stage 3 one look on
2023-onward: same sign, t >= 1.5, PF >= 1.1. t bar `lab_tools.bar()` 3.64; pre-registered mechanism with 3 variants ->
full-sample t >= 2.0 + clean placebo. Apex: yes (6E / M6E).
