# Noise band on GC (2026-11-08)
 (header committed before the first run; one variant per market, 2 ranked items). The Bridge's NQ RTH code, with its
clock moved to each market's regular hours and its point exits turned into % of price (NQ 50 / 25 pts ~ 0.35% / 0.175% at 2018-26 prices):
  15-min bars anchored to the open (CL 08:00-13:30 CT, GC 07:20-12:30 CT); TodayOpen = first RTH open, PrevClose = last RTH close of the
  previous trading day; slot = bar closing open + 30 .. close - 45; move = |close / TodayOpen - 1|; band = mean of that slot's previous
  20 moves; UB = max(open, prev close) x (1 + band), LB = min(...) x (1 - band); EMA20 of the RTH 15-min closes (continuous).
  On a slot bar, flat and bar close <= close - 60: close > UB and close > bar open -> buy next bar open; close < LB and < bar open -> short.
  Long: short signal (<= close - 60) -> reverse (if the day caps allow, else exit); else close < max(UB, EMA) -> exit next open. Mirror.
  Stop 0.35% / target 0.175% of the entry price (1-minute path, stop first), max 10 entries and 3 stops a day; flat at the open of the
  bar after close - 30 (CL 13:00 -> out 13:00, GC 12:00 -> out 12:00); CME early-close days skipped. Both sides (longs / shorts reported).
  CL $1,000 a point, tick 0.01; GC $100 a point, tick 0.10; $5 + 1 tick per market / stop fill (target = limit, no slip). Micros = 1/10.

Stopped at the first failed gate (t < 2): no placebo or benches.
