"""Twin's Morning Momentum setup on ES (user 2026-11-08: proven ingredient, different market). PRE-REGISTERED (header committed
before the run). Rules unchanged from Twin v2.1 MO (twin_continuation_test.simulate, use_bo=False, v21 holiday rules): 10-min
oscillator (close - EMA21) / (3 x ATR14) smoothed EMA3 crossing +-100 on a full bucket ending 08:40-09:30 CT, market entry, no
target, out 14:50; stop 20 ES points (~ Twin's 75 NQ points in % of price). ES: $50 a point, tick 0.25, $5 + 1 tick per fill.
Checks: per trade by period; random-side placebo (100 runs); daily corr with Twin's NQ momentum and the plan; checker folder
checks/candidates/mo_es/; 150K evaluation + 2 MES and funded 150K x 1.5 (with Twin cap1 2 MNQ, the adopted plan) + 2 MES.
  tools/run_stamped.sh analysis/mo_es_test.py > analysis/outputs/mo_es_test_output.txt
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
    ge = pickle.load(open("scratch_data/ge.pkl", "rb")); Be = tc.flatten(ge)
    T = tc.simulate(Be, use_bo=False, v21=True, mo_stop=20.0, pv=50.0, tick=0.25, comm=5.0); T = T[T.date >= "2018-01-01"].reset_index(drop=True)
    tt = lambda x: x.mean() / x.std(ddof=1) * np.sqrt(len(x)); a, b = T[T.date < "2023"].net, T[T.date >= "2023"].net
    print(f"   MO on ES: n {len(T)} ${T.net.mean():.0f} t {tt(T.net):.2f} PF {T.net[T.net > 0].sum() / -T.net[T.net < 0].sum():.2f} | 2018-22 ${a.mean():.0f} (t {tt(a):.1f}) 2023+ ${b.mean():.0f} (t {tt(b):.1f}) | longs ${T[T.side > 0].net.mean():.0f} shorts ${T[T.side < 0].net.mean():.0f} | worst ${T.net.min():,.0f}")
    print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
    rng = np.random.default_rng(6); pl = []
    for run in range(100):
        Tp = tc.simulate(Be, use_bo=False, v21=True, mo_stop=20.0, pv=50.0, tick=0.25, comm=5.0, placebo_rng=rng); Tp = Tp[Tp.date >= "2018-01-01"]; pl += [(run, x) for x in Tp.net]
    pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean(); print(f"   random-side placebo ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; p {np.mean(pm >= T.net.mean()):.2f}")
    cd = "checks/candidates/mo_es"; os.makedirs(cd, exist_ok=True)
    T.assign(date=T.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net"]].to_csv(f"{cd}/trades.csv", index=False)
    pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": True, "variants": 1}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write("# Morning Momentum on ES (Twin v2.1 MO rules, 2026-11-08)\nES 1-minute, 24h. 10-minute buckets; oscillator = (close - EMA21 of bucket closes) / (3 x Wilder ATR14 of buckets) x 100, EMA3-smoothed; long when it crosses above +100 (short below -100) on a full bucket ending 08:40-09:30 CT, one attempt a day, no early-close days; market entry next bar; stop 20 points; no target; exit at 14:50 CT. $5 + 1 tick per fill per ES.\n")
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); trr = list(g.trading); D = len(trr); dts = pd.DatetimeIndex(g.ts[trr]); yr = dts.year
    We, Re = grids(ge, Be, T, pv=50.0); edts = pd.DatetimeIndex(ge.ts); epos = pd.Series(np.arange(len(edts)), index=edts)
    idx = np.array([epos.get(d, -1) for d in dts]); W = np.zeros((D, 1440)); R = np.zeros((D, 1440)); m = idx >= 0
    W[m] = We[idx[m]] / 10; R[m] = Re[idx[m]] / 10                      # per MES
    B = tc.flatten(g); Tn = tc.simulate(B, max_stop_mult=1.0, v21=True); Tn = Tn[Tn.date >= "2018-01-01"]; Wt, Rt = grids(g, B, Tn); Wt, Rt = Wt[trr] / 10, Rt[trr] / 10
    mo_nq = Tn[Tn.setup == "MO"].groupby("date").net.sum().reindex(dts, fill_value=0.0); es_d = pd.Series(R[:, -1], index=dts)
    lab = pickle.load(open("scratch_data/lab.pkl", "rb")); C = pd.DataFrame({k: lab.C[k] for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC")}, index=dts); C["Twin NQ momentum"] = mo_nq
    print("   daily corr:", C[yr >= 2018].corrwith(es_d[yr >= 2018]).round(2).to_dict())
    P = {}
    for k, t_ in {"VB": with_slippage(load_mc(g, REPORTS["VB"][0])), "ONB30": with_slippage(load_mc(g, ONB30)), "MON_BR": load_bridge_mc(g),
                  "EOS": with_slippage(load_mc(g, REPORTS["EOS"][0]))}.items():
        w, rr = paths(g, t_); P[k] = (w[trr] / 10, rr[trr] / 10)
    atr = g.daily_atr(15); risk = lambda d, m_: np.floor(d / (np.nan_to_num(m_ * atr[trr], nan=1e12) * 2))[:, None]
    base = {"VB": 20.0, "ONB30": risk(2750, 0.25), "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1])}
    Wb = sum(P[k][0] * v for k, v in base.items()) + 2 * Wt; Rb = sum(P[k][1] * v for k, v in base.items()) + 2 * Rt; ok = (yr >= 2018) & (dts <= "2026-09-01")
    def ev(Wx, Rx):
        res = [evaluation(Wb + Wx, Rb + Rx, s, D, R150) for s in range(D)]; return np.array([x[0] if x else "" for x in res]), ok & np.array([x is not None for x in res])
    o0, v0 = ev(0 * W, 0 * R); print(f"\n   150K evaluation (set + Twin 2 MNQ) alone: pass {(o0 == 'pass')[v0].mean():.1%}")
    for q in (2, 4):
        o, v = ev(q * W, q * R); d = ((o == "pass").astype(float) - (o0 == "pass").astype(float))[v & v0]
        rng = np.random.default_rng(1); nb = int(np.ceil(len(d) / 60)); st = rng.integers(0, len(d), (2000, nb)); mm = d[((st[:, :, None] + np.arange(60)) % len(d)).reshape(2000, -1)[:, :len(d)]].mean(axis=1)
        print(f"   + ES momentum {q} MES: pass {(o == 'pass')[v].mean():5.1%} ({d.mean():+.1%}; band {np.percentile(mm, 5):+.1%} / {np.percentile(mm, 95):+.1%})", flush=True)
    sys.argv = ["x", "scratch_data"]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    Sp = pd.read_pickle("scratch_data/single_print_sessions.pkl"); flag = Sp.flag.reindex(dts).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag; lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    lab.W["TWIN"] = Wt; lab.C["TWIN"] = Rt[:, -1]; lab.W["MOES"] = W; lab.C["MOES"] = R[:, -1]
    PLAN = {"VB_N": 2, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    sc = lambda p, k: {n: (("risk", v[1] * k) if isinstance(v, tuple) else v * k) for n, v in p.items()}
    VV = {"plan x 1.5 + Twin 2": {**sc(PLAN, 1.5), "TWIN": 2}, "+ ES momentum 2 MES": {**sc(PLAN, 1.5), "TWIN": 2, "MOES": 2}, "+ ES momentum 4 MES": {**sc(PLAN, 1.5), "TWIN": 2, "MOES": 4}}
    keys = sorted({k for p in VV.values() for k in p}); Wall = np.stack([lab.W[k] for k in keys]); Call = np.stack([lab.C[k] for k in keys]); bases = {}
    for nm, p in VV.items():
        names, b = lab._base(p); Bm = np.zeros((len(keys), lab.D))
        for i, k in enumerate(names): Bm[keys.index(k)] = b[i]
        bases[nm] = Bm
    chg = np.zeros(Wall.shape[2], bool); chg[-1] = True; chg[1:] |= (np.abs(np.diff(Wall, axis=2)) > 0).any(axis=(0, 1)); chg[0] |= (Wall[:, :, 0] != 0).any()
    Wc = np.ascontiguousarray(Wall[:, :, chg]); days = np.where((dts >= "2018-01-01") & (dts <= "2026-10-09"))[0]; rng = np.random.default_rng(1); n, H, L_ = 600, 500, 20
    stb = rng.integers(0, len(days), (n, H // L_)); hist = days[((stb[:, :, None] + np.arange(L_)) % len(days)).reshape(n, -1)[:, :H]]; Rr = {nm: np.zeros((n, 3)) for nm in VV}
    for hh in range(n):
        ix = hist[hh]; Wh = np.ascontiguousarray(Wc[:, ix]); Ch = np.ascontiguousarray(Call[:, ix])
        for nm, Bm in bases.items():
            r = F.simulate_sized(Wh, Ch, np.ascontiguousarray(Bm[:, ix]), horizon=H, starts=[0], fmin=0.5, fmax=1.0, ref=3000.0); Rr[nm][hh] = [r["paid"][0], r["blown"][0], r["payouts"][0] == 6]
    b0 = Rr["plan x 1.5 + Twin 2"][:, 0]; print("\n   Funded 150K x 1.5 + Twin 2 MNQ, 600 paired histories, 2 years:")
    for nm, r in Rr.items(): print(f"      {nm:<22} 2y ${r[:, 0].mean():>7,.0f} blown {r[:, 1].mean():5.1%} all 6 {r[:, 2].mean():5.1%} diff ${(r[:, 0] - b0).mean():+5,.0f} beats {np.mean(r[:, 0] > b0) + 0.5 * np.mean(r[:, 0] == b0):5.1%}")
