"""Filters on WATCHLIST #28 (long NQ after a green RTH day; user ask 2026-11-08 'add a volatility filter or something').
EXPLORATORY, not pre-registered (Codex weekly review 2026-11-06 #4: the header was written before running but never committed
before the run, and every filter's 2023+ result is printed). Family (6 filters, each splits the green days in two; mechanism in brackets):
  F1 volatility: 20-day ATR (RTH ranges) above its 1-year median [continuation is stronger in volatile regimes]
  F2 trend: 15:00 close above its 200-day average [drift supports the overnight long]
  F3 strength: green body >= 0.5 x 20-day ATR [a strong day continues more than a doji]
  F4 close location: 15:00 close in the top 25% of the RTH range [buyers in control into the close]
  F5 no weekend: skip Friday signals [weekend gap risk]
  F6 calm: 20-day ATR BELOW its 1-year median (mirror of F1)
Selection on 2018-22 ONLY (best design t that also keeps >= 40% of the trades); 2023+ read once for the chosen one.
Every filter counts as a trial (+6 on top of #28's).
  tools/run_stamped.sh analysis/long_after_green_filters.py > analysis/outputs/long_after_green_filters_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M
from long_after_green_test import run, candles, ts, J0, J1

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); T = g.trading
    op, cl, ks, keep = candles(g)
    hi = np.nanmax(g.h[T][:, J0:J1 + 1], axis=1); lo = np.nanmin(g.l[T][:, J0:J1 + 1], axis=1)
    atr = pd.Series(hi - lo).rolling(20, min_periods=15).mean()
    atr_med = atr.rolling(252, min_periods=200).median().to_numpy(); atr = atr.to_numpy()
    sma = pd.Series(cl).ffill().rolling(200).mean().to_numpy()
    dow = pd.DatetimeIndex(g.ts[T]).dayofweek.to_numpy()
    loc = (cl - lo) / np.where(hi > lo, hi - lo, np.nan)
    green = keep & (cl > op) & ~np.isnan(atr_med)
    F = {"F1 volatile (ATR > 1y median)": atr > atr_med, "F2 above SMA200": cl > sma,
         "F3 strong body >= 0.5 ATR": (cl - op) >= 0.5 * atr, "F4 close in top 25% of range": loc >= 0.75,
         "F5 skip Friday": dow != 4, "F6 calm (ATR < 1y median)": atr < atr_med}
    base = run(g, 20.0, 7.25, ks[green])
    def row(t, nm, full=False):
        a = t[t.date < "2023"].net; b = t[t.date >= "2023"].net
        s = f"   {nm:<32} n={len(t):5d} | design 18-22 n={len(a):4d} ${a.mean():5.0f} t {ts(a):4.1f}"
        return s + (f" | 23+ ${b.mean():5.0f} t {ts(b):4.1f} | all ${t.net.mean():5.0f} t {ts(t.net):4.2f}" if full else "")
    print("\nDesign 2018-22 only (2023+ hidden):"); print(row(base, "no filter"))
    res = {}
    for nm, m in F.items():
        tin, tout = run(g, 20.0, 7.25, ks[green & m]), run(g, 20.0, 7.25, ks[green & ~m])
        res[nm] = (tin, tout); print(row(tin, nm + " IN")); print(row(tout, "      ... OUT"))
    nb = (base.date < "2023").sum()
    ok = {nm: ts(v[0][v[0].date < "2023"].net) for nm, v in res.items() if (v[0].date < "2023").sum() >= 0.4 * nb}
    pick = max(ok, key=ok.get)
    print(f"\nChosen on design t (>= 40% of trades kept): {pick}")
    print("\nOne look at 2023+ (chosen, its complement, no filter):")
    print(row(res[pick][0], pick + " IN", True)); print(row(res[pick][1], "      ... OUT", True)); print(row(base, "no filter", True))
    print("\nAll filters, full sample (information only, AFTER the pick):")
    for nm, v in res.items(): print(row(v[0], nm + " IN", True))
    nt = len([1 for l_ in open("TIER_LIST.md") if l_.startswith("| ") and "---" not in l_]) + 6
    print(f"\n   t needed (N = {nt}): {M.t_threshold(nt):.2f}")
