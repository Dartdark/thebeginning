"""Five funded accounts on the same 7-strategy plan, started together or staggered (2026-10-13).
Funded bench (cushion sizing, full size from $1,500), real day order, MultiCharts trade lists. Account k
starts k x GAP trading days after the first; totals are measured from the first start.
  python3 analysis/stagger_funded_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import funded_sim as F

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PLAN = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2,
        "NFP_MC": ("risk", 500), "VCS_MC": 1}
N = 5

if __name__ == "__main__":
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    names, b = lab._base(PLAN)
    W = np.stack([lab.W[k] for k in names]); C = np.stack([lab.C[k] for k in names])
    D = lab.D; yr = lab.yr
    cache = {}

    def sim(h):
        if h not in cache:
            st = np.arange(0, D - 1)
            r = F.simulate_sized(W, C, b, horizon=max(h, 1), starts=st, fmin=0.5, fmax=1.0, ref=1500.0)
            cache[h] = (np.where(h > 0, r["paid"], 0.0), r["blown"], r["days"])
        return cache[h]

    print(__doc__.split("\n")[0])
    print(f"\nTotal payouts of {N} accounts, measured from the first start (starts 2018 to the last date with a full window):")
    for gap in (0, 5, 10, 21, 63):
        out = {}
        for T in (125, 250, 500):
            last = D - T - 1
            tot = np.zeros(last); blown = np.zeros(last)
            for k in range(N):
                h = T - k * gap
                if h <= 0: continue
                p, bl, dd = sim(h)
                tot += p[k * gap:k * gap + last]; blown += bl[k * gap:k * gap + last] * (dd[k * gap:k * gap + last] <= h)
            m = yr[:last] >= 2018
            out[T] = (tot[m], blown[m])
        t1, b1 = out[250]; t2, b2 = out[500]
        print(f"  starts {gap:>2} days apart: 6m ${out[125][0].mean():,.0f} | 1y ${t1.mean():,.0f} (5% ${np.percentile(t1, 5):,.0f}, 95% ${np.percentile(t1, 95):,.0f})"
              f" | 2y ${t2.mean():,.0f} (5% ${np.percentile(t2, 5):,.0f}) | $13k in total within 1y {np.mean(t1 >= 13000):.0%}"
              f" | 3+ of 5 blown within 2y {np.mean(b2 >= 3):.1%}, all 5 {np.mean(b2 >= 5):.1%}")
    p, bl, dd = sim(500); last = D - 501; m = yr[:last] >= 2018
    print(f"\n  one account alone, 2y (full windows): ${p[:last][m].mean():,.0f}, blown {bl[:last][m].mean():.0%}")
