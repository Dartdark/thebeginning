# Leveraged-ETF flow -> closing hedge demand, NQ (2026-11-08)
 (header committed
before the first run; 1 variant; new mechanism and new use of data/letf).
Mechanism: creations / redemptions in the Nasdaq-100 leveraged and inverse ETFs force ProShares to add / cut Nasdaq exposure at the cash
close of the day they are processed. Retail flows into these funds come in waves (dip buying, hedging runs), so a big net flow yesterday
predicts more flow, and more closing hedge trades in the same direction, today.
Data: ProShares daily NAV / AUM (data/letf/: TQQQ +3, SQQQ -3, QLD +2, QID -2; to 2026-10-21). Fund dollar flow on day D (split-proof):
flow_D = AUM_D - AUM_{D-1} x NAV_D / NAV_{D-1}; Nasdaq exposure flow X_D = sum over funds of L x flow_D. Point in time: the row for D is
published the evening of D, so a trade on D uses X_{D-1}.
Rule: Z = X_{D-1} / sd of X over the previous 60 trading days (past only); |Z| >= 1.0 -> at 14:30 CT follow sign(Z) (net bullish exposure
created -> long) at the 14:31 open, stop 0.25 x ATR15, out at the 15:00 close (the cash close, where creations are hedged). CME early-
close days skipped. NQ, $7.25 + 1 tick per market / stop fill.

