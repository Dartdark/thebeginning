"""VB longs bigger after a 60-min double top (user 2026-11-08, flipped bench_pairings_test #3: VB longs within 4 h after a
60-min double top $191 vs $86 otherwise, t 1.2, 100 trades; POST HOC). Everything else unchanged.
  evaluation (corrected engine): those VB longs x 1.5 / x 2 (contracts, floored), 50K (VB 8) and 150K (VB 20) sets
  funded 150K: plan x 1.5 (VB_N 2 / VB_F 1 x 1.5), those VB longs x 1.5 / x 2; 600 paired bootstrap histories
  tools/run_stamped.sh analysis/vb_double_top_sizing.py > analysis/outputs/vb_double_top_sizing_output.txt
"""
import sys, io, runpy, contextlib, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from combine_levers_test import ONB30, challenge, MAXD
from plan_150k_test import evaluation, R150
from candlestick_patterns_test import rth_bars
from chart_patterns_test import pivots_signals
import funded_sim150 as F

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr); yr = pd.DatetimeIndex(g.ts[trr]).year
    B = rth_bars(g, 60); S = pivots_signals(B); dt_ = B[S["DTOP"][0]][["row", "j"]]
    vb = with_slippage(load_mc(g, REPORTS["VB"][0])).reset_index(drop=True)
    after = np.array([s > 0 and ((dt_.row == r) & (dt_.j < j) & (dt_.j >= j - 240)).any() for r, j, s in zip(vb.day, vb.j0, vb.side)])
    print(f"   VB trades {len(vb)}, longs after a 60-min double top {after.sum()}")
    P = {}
    for k, t in {"VB_DT": vb[after], "VB_REST": vb[~after], "ONB30": with_slippage(load_mc(g, ONB30)), "MON_BR": load_bridge_mc(g),
                 "EOS": with_slippage(load_mc(g, REPORTS["EOS"][0]))}.items():
        w, rr = paths(g, t); P[k] = (w[trr] / 10, rr[trr] / 10)
    risk = lambda d, m: np.floor(d / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    ok = yr >= 2018
    for acct, vbq, base in ((50, 8, {"ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}),
                            (150, 20, {"ONB30": risk(2750, 0.25), "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1])})):
        print(f"\n{acct}K evaluation (corrected engine), every start day 2018+:")
        o0 = None
        for f in (1.0, 1.5, 2.0):
            q = {**base, "VB_REST": float(vbq), "VB_DT": float(np.floor(vbq * f))}
            W = sum(P[k][0] * v for k, v in q.items()); R = sum(P[k][1] * v for k, v in q.items())
            res = [challenge(W, R, np.arange(s, min(s + MAXD, D)), lambda p, c, n: 1.0) for s in range(D)] if acct == 50 else [evaluation(W, R, s, D, R150) for s in range(D)]
            o = np.array([x[0] if x else "" for x in res]); v = ok & np.array([x is not None for x in res]); ps = o == "pass"
            if o0 is None: o0, v0 = o, v
            d = (ps.astype(float) - (o0 == "pass").astype(float))[v & v0]; rng = np.random.default_rng(1); nb = int(np.ceil(len(d) / 60))
            st = rng.integers(0, len(d), (2000, nb)); mm = d[((st[:, :, None] + np.arange(60)) % len(d)).reshape(2000, -1)[:, :len(d)]].mean(axis=1)
            print(f"   VB longs after a double top x {f:<3}: pass {ps[v].mean():5.1%} (18-22 {ps[v & (yr < 2023)].mean():5.1%}, 23+ {ps[v & (yr >= 2023)].mean():5.1%}) fail {(o[v] == 'fail').mean():5.1%}"
                  f" | vs plan {d.mean():+.1%} ({np.percentile(mm, 5):+.1%} / {np.percentile(mm, 95):+.1%})", flush=True)
    sys.argv = ["x", "scratch_data"]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr]); Sp = pd.read_pickle("scratch_data/single_print_sessions.pkl"); flag = Sp.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    wd, rd = paths(lab.g, vb[after]); wr, rr_ = paths(lab.g, vb[~after])
    for nm, w, r in (("DT", wd, rd), ("REST", wr, rr_)):
        W1, C1 = w[lab.tr] / 10, r[lab.tr][:, -1] / 10
        lab.W[f"VBN_{nm}"] = W1 * ~flag[:, None]; lab.C[f"VBN_{nm}"] = C1 * ~flag; lab.W[f"VBF_{nm}"] = W1 * flag[:, None]; lab.C[f"VBF_{nm}"] = C1 * flag
    PLAN = {"ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    sc = lambda p, k: {n: (("risk", v[1] * k) if isinstance(v, tuple) else v * k) for n, v in p.items()}
    V = {f"VB longs after a double top x {f}": {**sc(PLAN, 1.5), "VBN_REST": 3, "VBF_REST": 1.5, "VBN_DT": 3 * f, "VBF_DT": 1.5 * f} for f in (1.0, 1.5, 2.0)}
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
        ix = hist[h]; Wh = np.ascontiguousarray(Wc[:, ix]); Ch = np.ascontiguousarray(Call[:, ix])
        for nm, Bm in bases.items():
            r = F.simulate_sized(Wh, Ch, np.ascontiguousarray(Bm[:, ix]), horizon=H, starts=[0], fmin=0.5, fmax=1.0, ref=3000.0)
            R[nm][h] = [r["paid"][0], r["blown"][0], r["payouts"][0] == 6]
    print("\nFunded 150K plan x 1.5, 600 paired bootstrap histories, 2 years:")
    b0 = R[list(V)[0]][:, 0]
    for nm, r in R.items():
        print(f"   {nm:<34} 2y ${r[:, 0].mean():>7,.0f}  blown {r[:, 1].mean():5.1%}  all 6 {r[:, 2].mean():5.1%}  beats base {np.mean(r[:, 0] > b0) + 0.5 * np.mean(r[:, 0] == b0):5.1%}  diff ${(r[:, 0] - b0).mean():+6,.0f}")
