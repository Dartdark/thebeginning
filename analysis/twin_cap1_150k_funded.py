"""Twin cap1 on the 150K FUNDED plan at its current size (user 2026-11-08): funded plan x 1.5 (VB_N 2 as in FUNDED_PLAN), full size
from a $3,000 cushion, with and without Twin cap1 1 / 2 / 3 MNQ. funded_sim150 (150K PA rules, PA lock correct for funded).
(1) every start day, one history, 1 and 2 years; (2) 600 paired block-bootstrap histories (20-day blocks, 2 years).
  tools/run_stamped.sh analysis/twin_cap1_150k_funded.py > analysis/outputs/twin_cap1_150k_funded_output.txt
"""
import sys, io, runpy, contextlib, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import twin_continuation_test as tc, funded_sim150 as F
from twin_continuation_bench import grids

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", "scratch_data"]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    g = lab.g; dates = pd.DatetimeIndex(g.ts[lab.tr])
    S = pd.read_pickle("scratch_data/single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    B = tc.flatten(g); T = tc.simulate(B, max_stop_mult=1.0, v21=True); T = T[T.date >= "2018-01-01"].reset_index(drop=True)
    Wt, Rt = grids(g, B, T); lab.W["TWIN"] = Wt[lab.tr] / 10; lab.C["TWIN"] = (Rt[lab.tr] / 10)[:, -1]
    PLAN = {"VB_N": 2, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    sc = lambda p, k: {n: (("risk", v[1] * k) if isinstance(v, tuple) else v * k) for n, v in p.items()}
    V = {"plan x 1.5": sc(PLAN, 1.5)}
    for q in (1, 2, 3): V[f"plan x 1.5 + Twin cap1 {q} MNQ"] = {**sc(PLAN, 1.5), "TWIN": q}
    keys = sorted({k for p in V.values() for k in p}); Wall = np.stack([lab.W[k] for k in keys]); Call = np.stack([lab.C[k] for k in keys])
    bases = {}
    for nm, p in V.items():
        names, b = lab._base(p); Bm = np.zeros((len(keys), lab.D))
        for i, k in enumerate(names): Bm[keys.index(k)] = b[i]
        bases[nm] = Bm
    print("\n1. Every start day (one history), full size from a $3,000 cushion:")
    for nm, Bm in bases.items():
        out = []
        for h in (250, 500):
            r = F.simulate_sized(Wall, Call, Bm, horizon=h, starts=np.arange(0, lab.D - h), fmin=0.5, fmax=1.0, ref=3000.0)
            out.append((r["paid"].mean(), r["blown"].mean(), np.mean(r["payouts"] == 6)))
        print(f"   {nm:<30} 1y ${out[0][0]:>7,.0f} blown {out[0][1]:>4.0%} | 2y ${out[1][0]:>7,.0f} blown {out[1][1]:>4.0%} all 6 {out[1][2]:>4.0%}", flush=True)
    chg = np.zeros(Wall.shape[2], bool); chg[-1] = True; chg[1:] |= (np.abs(np.diff(Wall, axis=2)) > 0).any(axis=(0, 1)); chg[0] |= (Wall[:, :, 0] != 0).any()
    Wc = np.ascontiguousarray(Wall[:, :, chg]); days = np.where(dates >= "2018-01-01")[0]; rng = np.random.default_rng(1); n, H, L = 600, 500, 20
    stb = rng.integers(0, len(days), (n, H // L)); hist = days[((stb[:, :, None] + np.arange(L)) % len(days)).reshape(n, -1)[:, :H]]
    R = {nm: np.zeros((n, 3)) for nm in V}
    for h in range(n):
        ix = hist[h]; W = np.ascontiguousarray(Wc[:, ix]); C = np.ascontiguousarray(Call[:, ix])
        for nm, Bm in bases.items():
            r = F.simulate_sized(W, C, np.ascontiguousarray(Bm[:, ix]), horizon=H, starts=[0], fmin=0.5, fmax=1.0, ref=3000.0)
            R[nm][h] = [r["paid"][0], r["blown"][0], r["payouts"][0] == 6]
    b0 = R["plan x 1.5"][:, 0]; print("\n2. 600 paired bootstrap histories, 2 years:")
    for nm, r in R.items():
        print(f"   {nm:<30} 2y ${r[:, 0].mean():>7,.0f} (p5 ${np.percentile(r[:, 0], 5):>6,.0f})  blown {r[:, 1].mean():5.1%}  all 6 {r[:, 2].mean():5.1%}"
              f"  beats plan {np.mean(r[:, 0] > b0) + 0.5 * np.mean(r[:, 0] == b0):5.1%}  diff ${(r[:, 0] - b0).mean():+6,.0f}")
