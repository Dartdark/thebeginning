"""Twin cap1 with breakout entries only in regular hours (08:30-15:00 CT) vs the current Twin cap1 (user 2026-11-08; lead from
ingredient_ablation.py: $309 vs $248 a trade). PRE-REGISTERED (header committed before this run; post hoc in origin). Replacement test:
per trade by period; 150K evaluation set + Twin 2 MNQ; funded 150K x 1.5 + Twin 2 MNQ (600 paired histories); checker folder
checks/candidates/twin_rth_bo/ (placebo = Twin's random-side placebo of the same rule, 100 runs).
  tools/run_stamped.sh analysis/twin_rth_bo_test.py > analysis/outputs/twin_rth_bo_test_output.txt
"""
import sys, io, os, json, runpy, contextlib, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import twin_continuation_test as tc
from twin_continuation_bench import grids
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from combine_levers_test import ONB30
from plan_150k_test import evaluation, R150
import funded_sim150 as F

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); trr = list(g.trading); D = len(trr); dts = pd.DatetimeIndex(g.ts[trr]); yr = dts.year
    B = tc.flatten(g); tt = lambda x: x.mean() / x.std(ddof=1) * np.sqrt(len(x))
    V = {"current Twin cap1": dict(max_stop_mult=1.0, v21=True), "breakouts RTH only": dict(max_stop_mult=1.0, v21=True, bo_rth_only=True)}
    TT, PT = {}, {}
    for nm, kw in V.items():
        T = tc.simulate(B, **kw); T = T[T.date >= "2018-01-01"].reset_index(drop=True); TT[nm] = T
        a, b = T[T.date < "2023"].net, T[T.date >= "2023"].net; bo, mo = T[T.setup == "BO"].net, T[T.setup == "MO"].net
        print(f"   {nm:<20} n {len(T):5d} ${T.net.mean():4.0f} t {tt(T.net):5.2f} total ${T.net.sum() / 1000:.0f}k | 2018-22 ${a.mean():.0f} (t {tt(a):.1f}) 2023+ ${b.mean():.0f} (t {tt(b):.1f})"
              f" | BO n {len(bo)} ${bo.mean():.0f} / MO n {len(mo)} ${mo.mean():.0f} | worst ${T.net.min():,.0f}")
        print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
        W, R = grids(g, B, T); PT[nm] = (W[trr] / 10, R[trr] / 10)
    T = TT["breakouts RTH only"]; rng = np.random.default_rng(4); pl = []
    for run in range(100):
        Tp = tc.simulate(B, max_stop_mult=1.0, v21=True, bo_rth_only=True, placebo_rng=rng); Tp = Tp[Tp.date >= "2018-01-01"]
        pl += [(run, x) for x in Tp.net]
    pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean(); print(f"   random-side placebo: ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; rule ${T.net.mean():.0f}; p {np.mean(pm >= T.net.mean()):.2f}")
    cd = "checks/candidates/twin_rth_bo"; os.makedirs(cd, exist_ok=True)
    T.assign(date=T.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net"]].to_csv(f"{cd}/trades.csv", index=False)
    pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": False, "variants": 7}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write("# Twin Continuation cap1, breakout entries only 08:30-15:00 CT (2026-11-08)\nTwin v2.1 rules (personal_strategies/Twin_Continuation.txt, BO_MaxStopMult 1) with the swing-breakout entry orders armed only on 15-minute boundaries inside 08:30-15:00 CT; Morning Momentum unchanged. $7.25 + 1 tick per fill per NQ.\n")
    P = {}
    for k, t_ in {"VB": with_slippage(load_mc(g, REPORTS["VB"][0])), "ONB30": with_slippage(load_mc(g, ONB30)), "MON_BR": load_bridge_mc(g),
                  "EOS": with_slippage(load_mc(g, REPORTS["EOS"][0]))}.items():
        w, rr = paths(g, t_); P[k] = (w[trr] / 10, rr[trr] / 10)
    atr = g.daily_atr(15); risk = lambda d, m: np.floor(d / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    base = {"VB": 20.0, "ONB30": risk(2750, 0.25), "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1])}
    Wb = sum(P[k][0] * v for k, v in base.items()); Rb = sum(P[k][1] * v for k, v in base.items()); ok = yr >= 2018; O = {}
    print("\n   150K evaluation + Twin 2 MNQ:")
    for nm, (W, R) in PT.items():
        res = [evaluation(Wb + 2 * W, Rb + 2 * R, s, D, R150) for s in range(D)]; o = np.array([x[0] if x else "" for x in res]); v = ok & np.array([x is not None for x in res]); O[nm] = (o, v)
        print(f"      {nm:<20} pass {(o == 'pass')[v].mean():5.1%} (18-22 {(o == 'pass')[v & (yr < 2023)].mean():5.1%}, 23+ {(o == 'pass')[v & (yr >= 2023)].mean():5.1%})", flush=True)
    (o0, v0), (o1, v1) = O["current Twin cap1"], O["breakouts RTH only"]; d = ((o1 == "pass").astype(float) - (o0 == "pass").astype(float))[v0 & v1]
    rng = np.random.default_rng(1); nb = int(np.ceil(len(d) / 60)); st = rng.integers(0, len(d), (2000, nb)); mm = d[((st[:, :, None] + np.arange(60)) % len(d)).reshape(2000, -1)[:, :len(d)]].mean(axis=1)
    print(f"      paired difference {d.mean():+.1%} (90% band {np.percentile(mm, 5):+.1%} / {np.percentile(mm, 95):+.1%})")
    sys.argv = ["x", "scratch_data"]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    Sp = pd.read_pickle("scratch_data/single_print_sessions.pkl"); flag = Sp.flag.reindex(dts).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag; lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    for nm, (W, R) in PT.items(): lab.W["TW_" + nm] = W; lab.C["TW_" + nm] = R[:, -1]
    PLAN = {"VB_N": 2, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    sc = lambda p, k: {n: (("risk", v[1] * k) if isinstance(v, tuple) else v * k) for n, v in p.items()}
    VV = {nm: {**sc(PLAN, 1.5), "TW_" + nm: 2} for nm in PT}
    keys = sorted({k for p in VV.values() for k in p}); Wall = np.stack([lab.W[k] for k in keys]); Call = np.stack([lab.C[k] for k in keys]); bases = {}
    for nm, p in VV.items():
        names, b = lab._base(p); Bm = np.zeros((len(keys), lab.D))
        for i, k in enumerate(names): Bm[keys.index(k)] = b[i]
        bases[nm] = Bm
    chg = np.zeros(Wall.shape[2], bool); chg[-1] = True; chg[1:] |= (np.abs(np.diff(Wall, axis=2)) > 0).any(axis=(0, 1)); chg[0] |= (Wall[:, :, 0] != 0).any()
    Wc = np.ascontiguousarray(Wall[:, :, chg]); days = np.where(dts >= "2018-01-01")[0]; rng = np.random.default_rng(1); n, H, L_ = 600, 500, 20
    stb = rng.integers(0, len(days), (n, H // L_)); hist = days[((stb[:, :, None] + np.arange(L_)) % len(days)).reshape(n, -1)[:, :H]]; Rr = {nm: np.zeros((n, 3)) for nm in VV}
    for hh in range(n):
        ix = hist[hh]; Wh = np.ascontiguousarray(Wc[:, ix]); Ch = np.ascontiguousarray(Call[:, ix])
        for nm, Bm in bases.items():
            r = F.simulate_sized(Wh, Ch, np.ascontiguousarray(Bm[:, ix]), horizon=H, starts=[0], fmin=0.5, fmax=1.0, ref=3000.0); Rr[nm][hh] = [r["paid"][0], r["blown"][0], r["payouts"][0] == 6]
    b0 = Rr["current Twin cap1"][:, 0]; print("\n   Funded 150K x 1.5 + Twin 2 MNQ, 600 paired histories, 2 years:")
    for nm, r in Rr.items(): print(f"      {nm:<20} 2y ${r[:, 0].mean():>7,.0f} blown {r[:, 1].mean():5.1%} all 6 {r[:, 2].mean():5.1%} diff ${(r[:, 0] - b0).mean():+5,.0f} beats {np.mean(r[:, 0] > b0) + 0.5 * np.mean(r[:, 0] == b0):5.1%}")
