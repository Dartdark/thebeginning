"""Overnight Tick 'any day' (user 2026-11-08; lead from ingredient_ablation.py: the order-flow x VIX cell alone, t 4.8). PRE-REGISTERED
(header committed before this run; post hoc in origin). Rule: long 17:05 -> 03:00 CT when (closing order flow 14:15-15:15 CT < 0 and VIX >
its 25-day SMA) or (order flow >= 0 and VIX <= SMA), on ANY day (the down-day condition dropped); early-close days excluded; no stop.
Compared with the current rule (down days only) as a REPLACEMENT: per trade by period; random-night placebo (same count per year, 500
runs); checker folder checks/candidates/ot_anyday/; personal book (OT column swapped, return / DD); 150K funded plan x 1.5 + OT 2 MNQ;
150K evaluation set + OT 2 MNQ. Order flow = The Bridge aggressor volume (ends 2026-07-07); agreement with the bar-direction proxy shown.
  tools/run_stamped.sh analysis/ot_anyday_test.py > analysis/outputs/ot_anyday_test_output.txt
"""
import sys, io, os, json, runpy, contextlib, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC
from new_sources_150k import daypaths
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from combine_levers_test import ONB30
from plan_150k_test import evaluation, R150
import funded_sim150 as F

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    N = pd.read_csv("checks/candidates/overnight_tick/nights.csv", parse_dates=["date", "sess"]); N = N[N.rsv.notna() & N.hi25.notna() & ~N.half].reset_index(drop=True)
    hi = N.hi25.astype(bool); cell = ((N.rsv < 0) & hi) | ((N.rsv >= 0) & ~hi)
    R = {"current (down days)": N[N.down & cell], "any day": N[cell]}
    tt = lambda x: x.mean() / x.std(ddof=1) * np.sqrt(len(x))
    print(f"   order-flow sign agreement with the bar-direction proxy: {np.mean(np.sign(N.rsv) == np.sign(N.rsv_bar)):.0%}")
    for nm, T in R.items():
        a, b = T[T.date < "2023"].net, T[T.date >= "2023"].net
        print(f"   {nm:<20} n {len(T):4d} ${T.net.mean():5.0f} t {tt(T.net):5.2f} PF {T.net[T.net > 0].sum() / -T.net[T.net < 0].sum():.2f} | 2018-22 ${a.mean():.0f} (t {tt(a):.1f}) 2023+ ${b.mean():.0f} (t {tt(b):.1f}) | worst ${T.net.min():,.0f}")
        print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
    T = R["any day"]; rng = np.random.default_rng(9); pool = {y: N[N.date.dt.year == y].net.values for y in N.date.dt.year.unique()}
    cnt = T.groupby(T.date.dt.year).size(); pl = []
    for run in range(500):
        for y, n in cnt.items(): pl += [(run, x) for x in rng.choice(pool[y], n, replace=False)]
    pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean()
    print(f"   placebo (random nights, same count per year): ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; any-day ${T.net.mean():.0f}; p {np.mean(pm >= T.net.mean()):.3f}")
    cd = "checks/candidates/ot_anyday"; os.makedirs(cd, exist_ok=True)
    T.assign(date=T.date.dt.strftime("%Y-%m-%d"), side=1)[["date", "side", "net"]].to_csv(f"{cd}/trades.csv", index=False)
    pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": False, "variants": 6}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write("# Overnight Tick, any day (2026-11-08)\nLong NQ 17:05 -> 03:00 CT, no stop, when (closing order flow 14:15-15:15 CT < 0 and VIX > SMA25) or (>= 0 and VIX <= SMA25); any day except early closes; nights with a contract switch dropped. $7.25 + 1 tick per fill. Order flow = The Bridge aggressor volume.\n")
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); trr = list(g.trading); D = len(trr); dts = pd.DatetimeIndex(g.ts[trr]); yr = dts.year
    dpos = pd.Series(np.arange(D), index=dts); PT = {}
    for nm, TT in R.items():
        it = [(int(dpos[d]) if d in dpos.index else None, a, n) for d, a, n in zip(TT.date, TT.adv, TT.net)]; PT[nm] = daypaths(D, it)
    # personal book: swap the OvernightTick column (per micro, + $0.55)
    Pp = pd.read_pickle("scratch_data/personal_P.pkl"); Pp = Pp[[c for c in Pp.columns if c not in ("FC2B", "Kusho", "S47", "S30")]]
    mcf = lambda x: (lambda d_: d_["pnl_p50"] / d_["dd_p95"])(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1))
    print("\n   Personal book return / DD (OT column replaced; order-flow span only, to 2026-07-07):")
    span = Pp.index <= "2026-07-07"; Q = Pp[span]
    for per, m in (("2018-26", np.ones(len(Q), bool)), ("2018-22", Q.index.year <= 2022), ("2023+", Q.index.year >= 2023)):
        out = []
        for nm, TT in R.items():
            s = (TT.groupby("date").net.sum() / 10 - 0.55).reindex(Q.index, fill_value=0.0); out.append(mcf((Q.drop(columns="OvernightTick").sum(axis=1) + s)[m]))
        print(f"      {per}: current {out[0]:.2f} -> any day {out[1]:.2f} ({out[1] - out[0]:+.2f})")
    # 150K evaluation set + OT 2 MNQ
    P = {}
    for k, t_ in {"VB": with_slippage(load_mc(g, REPORTS["VB"][0])), "ONB30": with_slippage(load_mc(g, ONB30)), "MON_BR": load_bridge_mc(g),
                  "EOS": with_slippage(load_mc(g, REPORTS["EOS"][0]))}.items():
        w, rr = paths(g, t_); P[k] = (w[trr] / 10, rr[trr] / 10)
    atr = g.daily_atr(15); risk = lambda d, m: np.floor(d / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    base = {"VB": 20.0, "ONB30": risk(2750, 0.25), "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1])}
    Wb = sum(P[k][0] * v for k, v in base.items()); Rb = sum(P[k][1] * v for k, v in base.items()); ok = (yr >= 2018) & (dts <= "2026-06-01")
    print("\n   150K evaluation (starts to 2026-06):")
    for nm, (W, Rr) in [("set alone", (0 * Wb, 0 * Rb))] + [(f"+ OT {k} 2 MNQ", (2 * PT[k][0], 2 * PT[k][1])) for k in R]:
        res = [evaluation(Wb + W, Rb + Rr, s, D, R150) for s in range(D)]; o = np.array([x[0] if x else "" for x in res]); v = ok & np.array([x is not None for x in res])
        print(f"      {nm:<30} pass {(o == 'pass')[v].mean():5.1%}", flush=True)
    # funded 150K x 1.5 + OT 2 MNQ
    sys.argv = ["x", "scratch_data"]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    Sp = pd.read_pickle("scratch_data/single_print_sessions.pkl"); flag = Sp.flag.reindex(dts).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag; lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    for k in R: lab.W["OT_" + k] = PT[k][0]; lab.C["OT_" + k] = PT[k][1][:, -1]
    PLAN = {"VB_N": 2, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    sc = lambda p, k: {n: (("risk", v[1] * k) if isinstance(v, tuple) else v * k) for n, v in p.items()}
    V = {f"+ OT {k} 2 MNQ": {**sc(PLAN, 1.5), "OT_" + k: 2} for k in R}
    keys = sorted({k for p in V.values() for k in p}); Wall = np.stack([lab.W[k] for k in keys]); Call = np.stack([lab.C[k] for k in keys]); bases = {}
    for nm, p in V.items():
        names, b = lab._base(p); Bm = np.zeros((len(keys), lab.D))
        for i, k in enumerate(names): Bm[keys.index(k)] = b[i]
        bases[nm] = Bm
    chg = np.zeros(Wall.shape[2], bool); chg[-1] = True; chg[1:] |= (np.abs(np.diff(Wall, axis=2)) > 0).any(axis=(0, 1)); chg[0] |= (Wall[:, :, 0] != 0).any()
    Wc = np.ascontiguousarray(Wall[:, :, chg]); days = np.where((dts >= "2018-01-01") & (dts <= "2026-07-07"))[0]; rng = np.random.default_rng(1); n, H, L_ = 600, 500, 20
    stb = rng.integers(0, len(days), (n, H // L_)); hist = days[((stb[:, :, None] + np.arange(L_)) % len(days)).reshape(n, -1)[:, :H]]; Rr = {nm: np.zeros((n, 3)) for nm in V}
    for hh in range(n):
        ix = hist[hh]; Wh = np.ascontiguousarray(Wc[:, ix]); Ch = np.ascontiguousarray(Call[:, ix])
        for nm, Bm in bases.items():
            r = F.simulate_sized(Wh, Ch, np.ascontiguousarray(Bm[:, ix]), horizon=H, starts=[0], fmin=0.5, fmax=1.0, ref=3000.0); Rr[nm][hh] = [r["paid"][0], r["blown"][0], r["payouts"][0] == 6]
    b0 = Rr[list(V)[0]][:, 0]; print("\n   Funded 150K x 1.5 + OT 2 MNQ, 600 paired histories (to 2026-07), 2 years:")
    for nm, r in Rr.items(): print(f"      {nm:<30} 2y ${r[:, 0].mean():>7,.0f} blown {r[:, 1].mean():5.1%} all 6 {r[:, 2].mean():5.1%} diff vs current ${(r[:, 0] - b0).mean():+6,.0f}")
