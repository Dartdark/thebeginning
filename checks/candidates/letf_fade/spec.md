# Fade leveraged-ETF flow into the close, NQ (2026-11-08, post hoc in origin)

Z = yesterday's Nasdaq exposure flow of TQQQ / SQQQ / QLD / QID (L x fund dollar flow) / its past-60-day sd; |Z| >= 1.0 -> at 14:30 CT
trade AGAINST sign(Z) at the 14:31 open, stop 0.25 x ATR15, out at the 15:00 close; early-close days skipped; $7.25 + 1 tick per fill.

