"""ONB longs bigger after a red RTH day (user 2026-11-08, 'enhance, not replace'). POST HOC: the split came from bench_pairings_test
#2 (ONB ADX30 longs after red $418 vs after green $258, t 0.8; ONB ML longs $715 vs $591, t 0.4). Everything else unchanged.
  evaluation (corrected engine): ONB ADX30 longs after a red day x 1.5 / x 2 (risk budget), 50K ($1,100) and 150K ($2,750) sets
  funded 150K: plan x 1.5 (VB_N 2, full from $3,000), ONB ML longs after a red day x 1.5 / x 2; 600 paired bootstrap histories
  tools/run_stamped.sh analysis/onb_red_day_sizing.py > analysis/outputs/onb_red_day_sizing_output.txt
"""
import sys, io, runpy, contextlib, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from combine_levers_test import ONB30, challenge, MAXD
from plan_150k_test import evaluation, R150
from grid24 import jof
import funded_sim150 as F

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr); yr = pd.DatetimeIndex(g.ts[trr]).year
    op, cl = g.o[trr, jof(831)], g.c[trr, jof(1500)]; red_prev_tr = np.r_[False, (cl < op)[:-1]]          # per trading row
    rowpos = {r: i for i, r in enumerate(trr)}
    onb = with_slippage(load_mc(g, ONB30)); isred = np.array([red_prev_tr[rowpos[r]] if r in rowpos else False for r in onb.day])
    P = {}
    for k, t in {"VB": with_slippage(load_mc(g, REPORTS["VB"][0])), "ONB_LR": onb[(onb.side > 0) & isred], "ONB_REST": onb[~((onb.side > 0) & isred)],
                 "MON_BR": load_bridge_mc(g), "EOS": with_slippage(load_mc(g, REPORTS["EOS"][0]))}.items():
        w, rr = paths(g, t); P[k] = (w[trr] / 10, rr[trr] / 10)
    risk = lambda d, m: np.floor(d / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    ok = yr >= 2018
    for acct, onb_d, base in ((50, 1100, {"VB": 8.0, "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}),
                              (150, 2750, {"VB": 20.0, "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1])})):
        print(f"\n{acct}K evaluation (corrected engine), every start day 2018+:")
        o0 = None
        for f in (1.0, 1.5, 2.0):
            q = {**base, "ONB_REST": risk(onb_d, 0.25), "ONB_LR": risk(onb_d * f, 0.25)}
            W = sum(P[k][0] * v for k, v in q.items()); R = sum(P[k][1] * v for k, v in q.items())
            res = [challenge(W, R, np.arange(s, min(s + MAXD, D)), lambda p, c, n: 1.0) for s in range(D)] if acct == 50 else [evaluation(W, R, s, D, R150) for s in range(D)]
            o = np.array([x[0] if x else "" for x in res]); v = ok & np.array([x is not None for x in res]); ps = o == "pass"
            if o0 is None: o0, v0 = o, v
            d = ((ps).astype(float) - (o0 == "pass").astype(float))[v & v0]; rng = np.random.default_rng(1); nb = int(np.ceil(len(d) / 60))
            st = rng.integers(0, len(d), (2000, nb)); mm = d[((st[:, :, None] + np.arange(60)) % len(d)).reshape(2000, -1)[:, :len(d)]].mean(axis=1)
            print(f"   ONB longs after red x {f:<3}: pass {ps[v].mean():5.1%} (18-22 {ps[v & (yr < 2023)].mean():5.1%}, 23+ {ps[v & (yr >= 2023)].mean():5.1%}) fail {(o[v] == 'fail').mean():5.1%}"
                  f" | vs plan {d.mean():+.1%} ({np.percentile(mm, 5):+.1%} / {np.percentile(mm, 95):+.1%})", flush=True)
    sys.argv = ["x", "scratch_data"]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr]); S = pd.read_pickle("scratch_data/single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag; lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    lop, lcl = lab.g.o[lab.tr, jof(831)], lab.g.c[lab.tr, jof(1500)]; rp = np.r_[False, (lcl < lop)[:-1]]
    lab.W["ML_LR"] = lab.W["ONB_ML2_L"] * rp[:, None]; lab.C["ML_LR"] = lab.C["ONB_ML2_L"] * rp
    lab.W["ML_REST"] = lab.W["ONB_ML2_S"] + lab.W["ONB_ML2_L"] * ~rp[:, None]; lab.C["ML_REST"] = lab.C["ONB_ML2_S"] + lab.C["ONB_ML2_L"] * ~rp
    lab.stop["ML_LR"] = lab.stop["ML_REST"] = lab.stop["ONB_ML2_MC"]
    PLAN = {"VB_N": 2, "VB_F": 1, "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    sc = lambda p, k: {n: (("risk", v[1] * k) if isinstance(v, tuple) else v * k) for n, v in p.items()}
    V = {f"ONB ML longs after red x {f}": {**sc(PLAN, 1.5), "ML_REST": ("risk", 600), "ML_LR": ("risk", 600 * f)} for f in (1.0, 1.5, 2.0)}
    keys = sorted({k for p in V.values() for k in p}); Wall = np.stack([lab.W[k] for k in keys]); Call = np.stack([lab.C[k] for k in keys])
    bases = {}
    for nm, p in V.items():
        names, b = lab._base(p); Bm = np.zeros((len(keys), lab.D))
        for i, k in enumerate(names): Bm[keys.index(k)] = b[i]
        bases[nm] = Bm
    chg = np.zeros(Wall.shape[2], bool); chg[-1] = True; chg[1:] |= (np.abs(np.diff(Wall, axis=2)) > 0).any(axis=(0, 1)); chg[0] |= (Wall[:, :, 0] != 0).any()
    Wc = np.ascontiguousarray(Wall[:, :, chg]); days = np.where(dates >= "2018-01-01")[0]; rng = np.random.default_rng(1); n, H, L = 600, 500, 20
    stb = rng.integers(0, len(days), (n, H // L)); hist = days[((stb[:, :, None] + np.arange(L)) % len(days)).reshape(n, -1)[:, :H]]
    R = {nm: np.zeros((n, 3)) for nm in V}
    for h in range(n):
        ix = hist[h]; W = np.ascontiguousarray(Wc[:, ix]); C = np.ascontiguousarray(Call[:, ix])
        for nm, Bm in bases.items():
            r = F.simulate_sized(W, C, np.ascontiguousarray(Bm[:, ix]), horizon=H, starts=[0], fmin=0.5, fmax=1.0, ref=3000.0)
            R[nm][h] = [r["paid"][0], r["blown"][0], r["payouts"][0] == 6]
    print("\nFunded 150K plan x 1.5, 600 paired bootstrap histories, 2 years:")
    b0 = R[list(V)[0]][:, 0]
    for nm, r in R.items():
        print(f"   {nm:<30} 2y ${r[:, 0].mean():>7,.0f}  blown {r[:, 1].mean():5.1%}  all 6 {r[:, 2].mean():5.1%}  beats base {np.mean(r[:, 0] > b0) + 0.5 * np.mean(r[:, 0] == b0):5.1%}  diff ${(r[:, 0] - b0).mean():+6,.0f}")
