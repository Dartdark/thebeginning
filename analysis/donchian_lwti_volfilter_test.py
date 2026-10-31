"""Donchian + LWTI, user's v2 paste (2026-10-23): adds a volatility filter, XAverageOrig(TrueRange, 288) > 20 points at the
signal bar (288 bars = 24 h on 5-min bars, the likely chart). Everything else as in analysis/donchian_lwti_test.py (D,
2026-10-13). The filter is applied by blocking entries on bars that fail it. Per NQ after $7.25 + 1 tick per market fill.
  python3 analysis/donchian_lwti_volfilter_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import donchian_lwti_test as D

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"

if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    print(__doc__.split("\n")[0])
    for k in (5, 15):
        s = D.series(g, k); up, dn, lw, av = D.indicators(s)
        H, L, C = (pd.Series(s[c]) for c in ("h", "l", "c"))
        tr = pd.concat([H - L, (H - C.shift()).abs(), (L - C.shift()).abs()], axis=1).max(axis=1)
        vol = tr.ewm(alpha=2 / 289, adjust=False).mean().to_numpy()
        yrs = pd.DatetimeIndex(g.ts)[s["row"]].year
        share = pd.Series(vol > 20).groupby(yrs).mean()
        print(f"\n{k}-min bars: share of bars passing the filter by year:", {y: f"{v:.0%}" for y, v in share.items() if y >= 2018})
        for thr in (None, 20):
            av2 = av if thr is None else np.where(vol > thr, av, np.inf)
            for apex in (False, True):
                t = D.run(g, s, (up, dn, lw, av2), apex=apex)
                nm = f"{'no vol filter' if thr is None else 'vol > 20'}, {'Apex (8:30-15:00, flat)' if apex else 'as coded'}"
                print(D.line(t, nm, 44))
                if thr and apex and len(t): print("   by year:", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
