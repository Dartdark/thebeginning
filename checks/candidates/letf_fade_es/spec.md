# LETF-flow fade on ES (frozen NQ rule, 2026-11-08)
 (header committed before the first run; rules frozen
from analysis/letf_fade_test.py, nothing re-tuned; data downloaded 2026-11-08 from ProShares, never looked at for returns before).
  ES: S&P 500 funds UPRO +3, SPXU -3, SSO +2, SDS -2; ES $50 a point, tick 0.25, $5 + 1 tick per fill (MES = 1/10)
  YM: Dow 30 funds UDOW +3, SDOW -3, DDM +2, DXD -2; YM $5 a point, tick 1, $5 + 1 tick per fill (MYM = 1/10)
Rule (same as NQ): exposure flow X_D = sum of L x (AUM_D - AUM_{D-1} x NAV_D / NAV_{D-1}); Z = X_{D-1} / past-60-day sd; |Z| >= 1 ->
trade AGAINST sign(Z) at the 14:31 CT open, stop 0.25 x ATR15, out at the 15:00 close; CME early-close days skipped; 2018-26.

