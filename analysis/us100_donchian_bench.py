"""US100 Donchian on NQ, stage 2 (after both arms passed the 2018-22 gate in us100_donchian_test.py). Controls and benches:
  placebo: same exits (1.5 ATR stop, 2 ATR trail, 60-bar channel, Apex flatten) entered at random 15-min bars, same count per year (100 runs)
  correlation with the plan pieces (daily); APEX arm as an add-on: 150K evaluation set + 2 MNQ, funded 150K plan x 1.5 + 2 MNQ (600 paired
  histories); SOURCE arm on the personal book at 1 micro (1-year MC return / DD, both periods).
  tools/run_stamped.sh analysis/us100_donchian_bench.py > analysis/outputs/us100_donchian_bench_output.txt
"""
import sys, io, runpy, contextlib, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC
from us100_donchian_test import bars15, run, PV, TICK, COMM
from new_sources_150k import daypaths
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from combine_levers_test import ONB30
from plan_150k_test import evaluation, R150
import funded_sim150 as F


def placebo(g, B, T, apex, runs=100, seed=3):
    """Random entries with the same exit machinery: re-run with entries forced at random bars."""
    o, h, l, c = (B[k].to_numpy() for k in "ohlc"); s = B.s.to_numpy(); hhmm = (s // 60) * 100 + s % 60; rows = B.row.to_numpy()
    tr = np.r_[h[0] - l[0], np.maximum(h[1:], c[:-1]) - np.minimum(l[1:], c[:-1])]; atr = pd.Series(tr).ewm(alpha=1 / 80, adjust=False).mean().to_numpy()
    lo60 = pd.Series(l).rolling(60).min().shift(1).to_numpy(); yrs = pd.DatetimeIndex(pd.to_datetime(g.ts[rows])).year
    ok = (yrs >= 2018) & ((hhmm < 1545) | (hhmm >= 1700) if apex else True)
    if EW: ok = ok & (hhmm >= EW[0]) & (hhmm < EW[1])
    cnt = T[T.edate >= "2018"].groupby(T.edate.dt.year).size(); rng = np.random.default_rng(seed); means = []; global PL_ROWS; PL_ROWS = []
    for _ in range(runs):
        nets = []
        for y, nn in cnt.items():
            cand = np.nonzero(ok & (yrs == y))[0]
            for i in rng.choice(cand, nn, replace=False):
                e = o[i] + TICK; st = e - 1.5 * atr[i - 1]; x = None
                for j in range(i, min(i + 2000, len(o))):
                    if apex and j > i and (hhmm[j] >= 1545 and hhmm[j] < 1700): x = o[j] - TICK; break
                    if o[j] <= st: x = o[j] - TICK; break
                    if l[j] <= st: x = st - TICK; break
                    if j > i and c[j] < lo60[j]: x = (o[j + 1] if j + 1 < len(o) else c[j]) - TICK; break
                    st = max(st, c[j] - 2 * atr[j])
                if x is None: x = c[min(i + 1999, len(o) - 1)] - TICK
                nets.append((x - e) * PV - COMM)
        means.append(np.mean(nets)); PL_ROWS += [(len(means) - 1, x_) for x_ in nets]
    return np.array(means)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); B = bars15(g); trr = list(g.trading); D = len(trr); dts = pd.DatetimeIndex(g.ts[trr]); yr = dts.year
    EW = (830, 1100) if len(sys.argv) > 1 and sys.argv[1] == "morning" else None
    if EW: print('   MORNING-ONLY entries 08:30-11:00 CT (post hoc, user 2026-11-08)')
    TS, TA = run(g, B, False, EW), run(g, B, True, EW)
    for T, apex, nm in ((TS, False, "SOURCE"), (TA, True, "APEX")):
        pl = placebo(g, B, T, apex); real = T[T.edate >= "2018"].net.mean()
        if EW and apex:
            import os, json
            cd = "checks/candidates/donchian_morning_apex"; os.makedirs(cd, exist_ok=True); Tt = T[T.edate >= "2018"]
            pd.DataFrame(dict(date=Tt.date.dt.strftime("%Y-%m-%d"), side=1, net=Tt.net)).to_csv(f"{cd}/trades.csv", index=False)
            pd.DataFrame(PL_ROWS, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
            json.dump({"kind": "strategy", "pre_registered": False, "variants": 4}, open(f"{cd}/meta.json", "w"))
            open(f"{cd}/spec.md", "w").write("# US100 Donchian, APEX arm, morning-only entries (post hoc, 2026-11-08)\nNQ 15-min 24h bars; long when the last close > prior 160-bar high; stop 1.5 x ATR80, trail 2 x ATR at each bar, exit on a close < prior 60-bar low; entries only on bars starting 08:30-10:45 CT; flat at the 15:45 bar (11:45 early close). $7.25 + 1 tick per fill per NQ. Chosen after an entry-time split of the all-hours version.\n")
        print(f"   placebo {nm}: real ${real:.0f} vs random entries mean ${pl.mean():.0f} (95th ${np.percentile(pl, 95):.0f}); p {np.mean(pl >= real):.2f}", flush=True)
    # APEX arm paths on the trading days (exit day), worst = trade adverse (from 15-min lows)
    rows = B.row.to_numpy(); L = B.l.to_numpy(); pos = {r: i for i, r in enumerate(trr)}; it = []
    for t in TA[TA.edate >= "2018"].itertuples():
        w = (L[t.i0:t.i1 + 1].min() - t.entry) * PV - COMM; r = rows[t.i1]
        while r not in pos and r > 0: r -= 1
        it.append((pos.get(r), w, t.net))
    Wa, Ra = daypaths(D, it)
    lab = pickle.load(open("scratch_data/lab.pkl", "rb")); C = pd.DataFrame({k: lab.C[k] for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC")}, index=dts)[yr >= 2018]
    c = C.corrwith(pd.Series(Ra[:, -1], index=dts)[yr >= 2018]); print("   APEX daily corr with plan:", c.round(2).to_dict())
    P = {}
    for k, t_ in {"VB": with_slippage(load_mc(g, REPORTS["VB"][0])), "ONB30": with_slippage(load_mc(g, ONB30)), "MON_BR": load_bridge_mc(g),
                  "EOS": with_slippage(load_mc(g, REPORTS["EOS"][0]))}.items():
        w, rr = paths(g, t_); P[k] = (w[trr] / 10, rr[trr] / 10)
    atr = g.daily_atr(15); risk = lambda d, m: np.floor(d / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    base = {"VB": 20.0, "ONB30": risk(2750, 0.25), "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1])}
    Wb = sum(P[k][0] * v for k, v in base.items()); Rb = sum(P[k][1] * v for k, v in base.items()); ok = yr >= 2018
    def ev(Wx, Rx):
        res = [evaluation(Wb + Wx, Rb + Rx, s, D, R150) for s in range(D)]
        return np.array([x[0] if x else "" for x in res]), ok & np.array([x is not None for x in res])
    o0, v0 = ev(0 * Wb, 0 * Rb)
    for q in (1, 2, 4):
        o, v = ev(q * Wa, q * Ra); ps = o == "pass"; d = (ps.astype(float) - (o0 == "pass").astype(float))[v & v0]
        rng = np.random.default_rng(1); nb = int(np.ceil(len(d) / 60)); st = rng.integers(0, len(d), (2000, nb)); mm = d[((st[:, :, None] + np.arange(60)) % len(d)).reshape(2000, -1)[:, :len(d)]].mean(axis=1)
        print(f"   150K eval + APEX Donchian {q} MNQ: pass {ps[v].mean():5.1%} vs {(o0 == 'pass')[v0].mean():5.1%} ({d.mean():+.1%}; {np.percentile(mm, 5):+.1%} / {np.percentile(mm, 95):+.1%})", flush=True)
    _argv = sys.argv; sys.argv = ["x", "scratch_data"]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    Sp = pd.read_pickle("scratch_data/single_print_sessions.pkl"); flag = Sp.flag.reindex(dts).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag; lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    lab.W["DON"] = Wa; lab.C["DON"] = Ra[:, -1]
    PLAN = {"VB_N": 2, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    sc = lambda p, k: {n: (("risk", v[1] * k) if isinstance(v, tuple) else v * k) for n, v in p.items()}
    V = {"plan x 1.5": sc(PLAN, 1.5), "+ Donchian 1 MNQ": {**sc(PLAN, 1.5), "DON": 1}, "+ Donchian 2 MNQ": {**sc(PLAN, 1.5), "DON": 2}}
    keys = sorted({k for p in V.values() for k in p}); Wall = np.stack([lab.W[k] for k in keys]); Call = np.stack([lab.C[k] for k in keys]); bases = {}
    for nm, p in V.items():
        names, b = lab._base(p); Bm = np.zeros((len(keys), lab.D))
        for i, k in enumerate(names): Bm[keys.index(k)] = b[i]
        bases[nm] = Bm
    chg = np.zeros(Wall.shape[2], bool); chg[-1] = True; chg[1:] |= (np.abs(np.diff(Wall, axis=2)) > 0).any(axis=(0, 1)); chg[0] |= (Wall[:, :, 0] != 0).any()
    Wc = np.ascontiguousarray(Wall[:, :, chg]); days = np.where(dts >= "2018-01-01")[0]; rng = np.random.default_rng(1); n, H, L_ = 600, 500, 20
    stb = rng.integers(0, len(days), (n, H // L_)); hist = days[((stb[:, :, None] + np.arange(L_)) % len(days)).reshape(n, -1)[:, :H]]; Rr = {nm: np.zeros((n, 3)) for nm in V}
    for hh in range(n):
        ix = hist[hh]; Wh = np.ascontiguousarray(Wc[:, ix]); Ch = np.ascontiguousarray(Call[:, ix])
        for nm, Bm in bases.items():
            r = F.simulate_sized(Wh, Ch, np.ascontiguousarray(Bm[:, ix]), horizon=H, starts=[0], fmin=0.5, fmax=1.0, ref=3000.0); Rr[nm][hh] = [r["paid"][0], r["blown"][0], r["payouts"][0] == 6]
    b0 = Rr["plan x 1.5"][:, 0]; print("\n   Funded 150K x 1.5, 600 paired histories, 2 years:")
    for nm, r in Rr.items(): print(f"      {nm:<20} 2y ${r[:, 0].mean():>7,.0f} blown {r[:, 1].mean():5.1%} all 6 {r[:, 2].mean():5.1%} diff ${(r[:, 0] - b0).mean():+6,.0f}")
    Pp = pd.read_pickle("scratch_data/personal_P.pkl"); Pp = Pp[[c_ for c_ in Pp.columns if c_ not in ("FC2B", "Kusho", "S47", "S30")]]
    ds = TS[TS.edate >= "2018"].groupby("date").net.sum() / 10 - 0.55; ds = ds.reindex(Pp.index, fill_value=0.0)
    mcf = lambda x: (lambda d_: (d_["pnl_p50"], d_["dd_p95"]))(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1))
    print("\n   Personal book + SOURCE Donchian 1 micro (return / DD p95):")
    for per, m in (("2018-26", np.ones(len(Pp), bool)), ("2018-22", Pp.index.year <= 2022), ("2023+", Pp.index.year >= 2023)):
        a50, add = mcf(Pp.sum(axis=1)[m]); b50, bdd = mcf((Pp.sum(axis=1) + ds)[m])
        print(f"      {per}: {a50 / add:.2f} -> {b50 / bdd:.2f} ({b50 / bdd - a50 / add:+.2f}); $ {a50:,.0f} -> {b50:,.0f}; corr {Pp.sum(axis=1)[m].corr(ds[m]):+.2f}")
