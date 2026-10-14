"""Youngblood (2026) zero-edge placebo through OUR Apex funded bench (2026-10-14): random long / short at 10:00 ET (9:00 CT open),
fixed 8 MNQ, symmetric 100-tick (25-point) target and stop, else flat at 15:00 CT; NQ 2018-2026. $0.725 commission + 1 tick
($0.50) per MNQ per stop / market fill. Ten random seeds; compared with the plan (current funded plan + CL fade, cushion $1,500).
The question: how much of the bench's value would a strategy with NO edge collect from the account structure alone?
  python3 analysis/random_strategy_bench.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
if __name__ == "__main__":
    print(__doc__.split("\n")[0]); sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        ns = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")
    lab = ns["lab"]; g = lab.g; O, H, L, C = g.o, g.h, g.l, g.c
    rows = lab.tr; ncol = lab.W["VB"].shape[1]
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    a, c = lab.score(plan, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(plan, 500, fmin=0.5, fmax=1.0, ref=1500.0)
    print(f"plan                                 ${a['expected']:,.0f} / ${c['expected']:,.0f}  paid {a['any_payout']:.0%}  blown {a['blown']:.0%} / {c['blown']:.0%}")
    res = []
    for seed in range(10):
        rng = np.random.default_rng(seed); Cd = np.zeros(len(rows)); Wd = np.zeros(len(rows)); gross = []
        for i, d in enumerate(rows):
            e = O[d, 541]
            if np.isnan(e) or pd.Timestamp(g.ts[d]).year < 2018: continue
            s = rng.choice([-1, 1]); tp, sl = e + s * 25, e - s * 25; px = None; worst = 0.0
            for m in range(541, 900):
                if np.isnan(H[d, m]): continue
                adv = (L[d, m] - e) if s > 0 else (e - H[d, m]); worst = min(worst, max(adv, -25))
                if (s > 0 and L[d, m] <= sl) or (s < 0 and H[d, m] >= sl): px = sl - s * 0.25; kind = 0; break
                if (s > 0 and H[d, m] >= tp) or (s < 0 and L[d, m] <= tp): px = tp; kind = 1; break
            if px is None:
                k = 900
                while np.isnan(C[d, k]): k -= 1
                px = C[d, k] - s * 0.25; kind = 2
            pts = (px - (e + s * 0.25)) * s
            net = pts * 2 - 0.725; Cd[i] = net; Wd[i] = min(net, worst * 2 - 0.725); gross.append(pts * 2)
        lab.C["RND"] = Cd; lab.W["RND"] = Wd[:, None] * np.ones((1, ncol))
        r1 = lab.score({"RND": 8}, 250, fmin=1.0, fmax=1.0, ref=1500.0); r2 = lab.score({"RND": 8}, 500, fmin=1.0, fmax=1.0, ref=1500.0)
        res.append((np.mean(gross) * 8, r1["expected"], r2["expected"], r1["any_payout"], r1["blown"], r2["blown"]))
    R = pd.DataFrame(res, columns=["gross_per_day_8mnq", "1y", "2y", "paid", "blown1", "blown2"])
    print(f"random 8 MNQ, 10 seeds (mean / min / max):")
    for c_ in R.columns: print(f"   {c_:<20} {R[c_].mean():>10,.2f} {R[c_].min():>10,.2f} {R[c_].max():>10,.2f}")
