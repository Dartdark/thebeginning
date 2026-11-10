"""Plateau check of the 150K 'finish' lever (information only, after analysis/eval_levers150.py: x0.5 once profit >= $6,000 gave
+1.7 points, band +0.8 / +2.8): thresholds $4,500-$7,500 x size 0.33 / 0.5 / 0.67 on the same base and engine.
  tools/run_stamped.sh analysis/eval_finish150_plateau.py > analysis/outputs/eval_finish150_plateau_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
import dual_thrust_bench as DTB
import bench150 as BB
from eval_levers150 import challenge, band

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    ctx = BB.setup(); g, trr, D, dts = ctx["g"], ctx["trr"], ctx["D"], ctx["dts"]; P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("DT", DTB.dt_trades(g))): w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    Wb = ctx["Wb"] - 5 * P["VB"][0] + 2 * P["DT"][0]; Rb = ctx["Rb"] - 5 * P["VB"][1] + 2 * P["DT"][1]
    S = [s for s in range(D) if pd.Timestamp("2018-01-02") <= dts[s] <= pd.Timestamp("2026-09-01")]; early = dts[S] < "2023-01-01"
    p0 = np.array([challenge(Wb, Rb, s, D) == "pass" for s in S], float); print(f"   base pass {p0.mean():.1%}")
    for k in (0.33, 0.5, 0.67):
        row = []
        for th in (4500, 5000, 6000, 7000, 7500):
            p = np.array([challenge(Wb, Rb, s, D, scale_fn=lambda pr, c, n, th=th, k=k: k if pr >= th else 1.0) == "pass" for s in S], float); lo, hi = band(p - p0)
            row.append(f"${th:,}: {p.mean() - p0.mean():+.1%} ({lo:+.1%}/{hi:+.1%}; 18-22 {p[early].mean() - p0[early].mean():+.1%}, 23+ {p[~early].mean() - p0[~early].mean():+.1%})")
        print(f"   size x{k}: " + " | ".join(row), flush=True)
