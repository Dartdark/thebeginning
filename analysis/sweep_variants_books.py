"""Versions built from the data-sweep hits (WATCHLIST #38), alone and combined, vs each piece's current form and in the books (user
2026-11-10). POST HOC (the hits came from a 1,190-comparison screen): information only; the 2009-2017 NQ export is the real test.
Regimes as analysis/data_sweep.py (last close before the day). Personal book sizes: Overnight Tick 2 MNQ, others 1 micro.
Per version: the piece alone ($ a year, max DD, daily Sharpe, active days) and the personal book's 1-year bootstrap median /
p95 DD / return-to-DD in 2018-26, 2018-22, 2023+ (full book and core book).
  tools/run_stamped.sh analysis/sweep_variants_books.py > analysis/outputs/sweep_variants_books_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC
from new_data_screen import RULES, prior
from data_sweep import series

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    P = pd.read_pickle("scratch_data/personal_P.pkl"); idx = P.index; S = series()
    reg = lambda nm, rule: pd.Series(prior(S[nm], idx, RULES[rule]) == 1, index=idx)
    spx_z, spx_up, spx_med = reg("SPX", "z_high"), reg("SPX", "rising"), reg("SPX", "above_median")
    fear = reg("VIX9D/VIX", "above_median"); fear_any = reg("VIX9D/VIX", "above_median") | reg("VXN", "above_median") | reg("GVZ", "above_median") | reg("VIX9D", "above_median")
    gex = reg("GEX (SqueezeMetrics)", "above_median"); vxnspk = reg("VXN-VIX", "z_high"); vxnhi = reg("VXN-VIX", "above_median")
    one = pd.Series(1.0, index=idx); W = lambda m, a, b=1.0: m.map({True: a, False: b}).astype(float)
    V = {"OvernightTick": (2.0, {"skip S&P stretched (#1)": W(spx_z, 0), "3 on fear days (VIX9D/VIX, #4)": W(fear, 1.5),
                                  "skip stretched + 3 on fear": W(spx_z, 0) * W(fear & ~spx_z, 1.5),
                                  "skip stretched + 3 on any fear (#3,4,7,10)": W(spx_z, 0) * W(fear_any & ~spx_z, 1.5)}),
         "SwingTarget": (1.0, {"skip S&P stretched (#2)": W(spx_z, 0), "skip S&P rising (#6)": W(spx_up, 0), "skip high GEX (#8)": W(gex, 0),
                                "2 on Nasdaq-fear spikes (#5)": W(vxnspk, 2), "skip stretched or high GEX + 2 on spikes": W(spx_z | gex, 0) * W(vxnspk & ~(spx_z | gex), 2)}),
         "PaperTrend": (1.0, {"only below the S&P median (#9)": W(spx_med, 0), "2 below the S&P median": W(spx_med, 1, 2)}),
         "ESMOCFollow_perMES": (1.0, {"skip Nasdaq fear > S&P fear (#11)": W(vxnhi, 0)})}
    f = lambda x: (lambda r: (r["pnl_p50"], r["dd_p95"], r["pnl_p50"] / r["dd_p95"]))(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1))
    yrs = len(idx) / 252
    def alone(x):
        eq = x.cumsum(); dd = (eq.cummax() - eq).max(); sh = x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else np.nan
        return f"${x.sum() / yrs:6,.0f}/yr  DD ${dd:6,.0f}  Sharpe {sh:4.2f}  active {(x != 0).mean():4.0%}"
    pers = (("2018-26", np.ones(len(idx), bool)), ("2018-22", idx.year <= 2022), ("2023+", idx.year >= 2023))
    for col, (size, vs) in V.items():
        base_piece = P[col] * size
        print(f"\n=== {col} (book size {size:g}) ===")
        print(f"   {'current':<44} {alone(base_piece)}")
        for nm, m in vs.items(): print(f"   {nm:<44} {alone(P[col] * size * m)}")
        for lab, cols in (("full", list(P.columns)), ("core", [c for c in P.columns if c not in ("FC2B", "Kusho", "S47", "S30")])):
            if col not in cols: continue
            base = P[cols].sum(axis=1) - P[col] + base_piece; b0 = {p: f(base[m]) for p, m in pers}
            print(f"   {lab} book: current " + " | ".join(f"{p} {b0[p][2]:.2f}" for p, _ in pers))
            for nm, m in vs.items():
                alt = base - base_piece + P[col] * size * m
                print(f"      {nm:<41} " + " | ".join(f"{p} {(lambda y: f'{y[2]:.2f} ({y[2] - b0[p][2]:+.2f}; ${y[0] - b0[p][0]:+,.0f})')(f(alt[mm]))}" for p, mm in pers), flush=True)
