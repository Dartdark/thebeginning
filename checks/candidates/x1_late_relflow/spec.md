# x1_late_relflow (2026-11-08)
 (header
committed before the first run; 2 ranked items, 1 variant each). Engine = Relative Strength's Z (relative_strength_test.signals: EWMA beta
and residual variance of 1-min RTH log returns, 20-day half-life; Z = (A's move since 8:30 - beta x B's) / sqrt(residual var x minutes)).
  X1 Late relative flow (Relative Strength's engine in Late-Day Flow's window; mechanism: Nasdaq-100 leveraged ETFs rebalance more than the
     S&P ones on days NQ outruns ES, in the last hour): at 14:00 CT, |Z of NQ vs ES since 8:30| >= 1.25 -> follow NQ at the 14:01 open,
     stop 0.25 x the 20-day average RTH range (Late-Day Flow's stop), no target, out at the 14:30 close. NQ, $7.25 + 1 tick per fill.
  X2 Relative Strength on YM vs ES (same rule as the live Relative Strength, the Dow instead of the Nasdaq): at 9:00 CT, |Z of YM vs ES|
     >= 1.25 -> follow YM at the 9:01 open, stop 0.6 / target 1.0 x the 20-day average RTH range, flat 15:00. YM $5 a point, tick 1,
     $5 + 1 tick per fill (MYM = 1/10).

