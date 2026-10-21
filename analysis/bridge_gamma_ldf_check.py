"""Follow-ups to analysis/bridge_filter_scan2.py (2026-10-14):
 1. gamma features (fixed with the basis) on their own split: data from 2023-03-28 only, design 2023-03-28 .. 2024-12-31,
    holdout 2025-01-01 .. 2026; same keep-the-better-half rule and PASS bar (design |t| >= 2, holdout t >= 1.5)
 2. funded bench for the one round-2 pass: Late-Day Flow taken / sized by the Heatmap wall imbalance (keep the 'low' half:
    the larger resting wall on the side the trade moves toward), cut at the 2018-22 median
  python3 analysis/bridge_gamma_ldf_check.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    F = pd.read_pickle(SP + "bridge_features2.pkl")
    print("\n1. gamma features, design 2023-03..2024, holdout 2025-26")
    for s in ("VB", "ONB_ML", "LDF"):
        q = F[(F.strat == s) & (F.date >= "2023-03-28")]
        for c in ("gamma", "groom", "gcen"):
            x = q[c]; ok = x.notna(); d = ok & (q.date.dt.year <= 2024); h = ok & (q.date.dt.year >= 2025)
            if d.sum() < 20 or h.sum() < 10: print(f"   {s:<6} {c:<5} n design {int(d.sum())}, holdout {int(h.sum())}: too few"); continue
            med = x[d].median(); hi = x >= med
            if c == "gamma": hi = x > 0.5
            a, b = q.net[d & hi], q.net[d & ~hi]
            if len(a) < 5 or len(b) < 5: print(f"   {s:<6} {c:<5} one-sided split"); continue
            td = (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b)); keep = hi if td > 0 else ~hi
            k, sk = q.net[h & keep], q.net[h & ~keep]
            th = (k.mean() - sk.mean()) / np.sqrt(k.var() / max(len(k), 1) + sk.var() / max(len(sk), 1)) if len(k) > 2 and len(sk) > 2 else np.nan
            print(f"   {s:<6} {c:<5} n {int(ok.sum()):4d} design t {td:+.2f} | holdout kept ${k.mean():6.0f} (n {len(k)}) skipped ${sk.mean():6.0f} (n {len(sk)}) t {th:+.2f}"
                  + ("  PASS" if abs(td) >= 2 and th >= 1.5 else ""))
    print("\n2. funded bench: Late-Day Flow by wall imbalance")
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        ns = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")
    lab = ns["lab"]; g = lab.g
    q = F[F.strat == "LDF"]; med = q.wallimb[q.date.dt.year < 2023].median()
    low = {(int(r.day), int(r.j0)): (r.wallimb < med) for r in q.itertuples() if not np.isnan(r.wallimb)}
    t = load_mc(g, "mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Late Day Flow.xlsx")
    a = np.array([low.get((int(d), int(j)), None) for d, j in zip(t.day, t.j0)], dtype=object)
    print(f"   LDF trades {len(t)}: kept (wall toward the trade) {int((a == True).sum())}, other {int((a != True).sum())}")
    atr = g.daily_atr(15)
    lab.add("LDF_K", t[a == True].reset_index(drop=True), stop_pts=0.25 * atr)
    lab.add("LDF_O", t[a != True].reset_index(drop=True), stop_pts=0.25 * atr)
    base = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    for nm, p in (("plan (LDF 2 MNQ)", {**base, "LDF_MC": 2}), ("kept 2 only", {**base, "LDF_K": 2}),
                  ("kept 3 / other 1", {**base, "LDF_K": 3, "LDF_O": 1}), ("kept 3 / other 2", {**base, "LDF_K": 3, "LDF_O": 2}),
                  ("kept 4 / other 1", {**base, "LDF_K": 4, "LDF_O": 1})):
        r1, r2 = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0)
        print(f"   {nm:<20} ${r1['expected']:,.0f} / ${r2['expected']:,.0f}  blown {r1['blown']:.0%} / {r2['blown']:.0%}"
              f" | 1y 2018-22 ${r1['s2018_22']:,.0f} 2023+ ${r1['s2023_on']:,.0f}")
