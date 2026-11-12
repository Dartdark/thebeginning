"""Shared 150K benches for add-on / replacement candidates (2026-11-08; factored out of analysis/mo_es_test.py, same numbers).

  ctx = setup()                       NQ grid, eval base = the LIVE #5 evaluation set (LIVE_EVAL below, kept equal to
                                      live/expected_setup.json; printed on every run), funded lab with VB_F / VB_N / TWIN
  setup(base="legacy")                the pre-2026-11-12 eval base (VB 20, ONB30, MON_BR 5, EOS, Twin 2; no DT, no JF) to reproduce old outputs
  RULE (user 2026-11-12: 'dont test upcoming shit on past shit'): when a live chart / size changes, update LIVE_EVAL in the same
  commit as expected_setup.json. Funded base: BASE_FUNDED (no funded account live; VB still in the funded plan).
  to_nq_days(ctx, gx, W, R)           per-row minute paths of another market's grid -> NQ trading-day rows
  eval_bench(ctx, {name: (W, R)})     W, R already sized ($, NQ trading-day rows x 1440), added to the base; paired pass-rate diff + block band
  funded_bench(ctx, {name: plan}, extra={key: (W, C)})   600 paired 2-year histories, 150K x 1.5 + Twin 2 as the base plan
  personal(ctx, {name: daily $ Series}, drop=())         personal book 1-year MC return / DD (p50 / p95), by period
"""
import sys, io, runpy, contextlib, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
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
import montecarlo as MC

LIVE_EVAL = {"ONB30": ("risk", 2750), "EOS": ("risk", 1250), "MON_BR": 5, "TWIN": 2, "DT": 2, "JF": 2}   # #5 as of 2026-11-12 (VB out 11/11, JF in 11/12)
LEGACY_EVAL = {"VB": 20, "ONB30": ("risk", 2750), "MON_BR": 5, "EOS": ("risk", 1250), "TWIN": 2}
PLAN = {"VB_N": 2, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
sc = lambda p, k: {n: (("risk", v[1] * k) if isinstance(v, tuple) else v * k) for n, v in p.items()}
BASE_FUNDED = {**sc(PLAN, 1.5), "TWIN": 2}


def setup(twin_trades=None, base="live"):
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); trr = list(g.trading); D = len(trr); dts = pd.DatetimeIndex(g.ts[trr]); yr = dts.year
    B = tc.flatten(g)
    Tn = tc.simulate(B, max_stop_mult=1.0, v21=True) if twin_trades is None else twin_trades
    Tn = Tn[Tn.date >= "2018-01-01"]; Wt, Rt = grids(g, B, Tn); Wt, Rt = Wt[trr] / 10, Rt[trr] / 10
    P = {}
    for k, t_ in {"VB": with_slippage(load_mc(g, REPORTS["VB"][0])), "ONB30": with_slippage(load_mc(g, ONB30)), "MON_BR": load_bridge_mc(g),
                  "EOS": with_slippage(load_mc(g, REPORTS["EOS"][0]))}.items():
        w, rr = paths(g, t_); P[k] = (w[trr] / 10, rr[trr] / 10)
    atr = g.daily_atr(15); risk = lambda d, m_: np.floor(d / (np.nan_to_num(m_ * atr[trr], nan=1e12) * 2))[:, None]
    spec = LIVE_EVAL if base == "live" else LEGACY_EVAL
    if "DT" in spec:
        import dual_thrust_bench as DTB
        w, rr = paths(g, DTB.dt_trades(g)); P["DT"] = (w[trr] / 10, rr[trr] / 10)
    if "JF" in spec:
        from jump_fade_paths import jf_paths
        P["JF"] = jf_paths(dts, D)
    P["TWIN"] = (Wt, Rt)
    rm = {"ONB30": 0.25, "EOS": REPORTS["EOS"][1]}
    mult = {k: (risk(v[1], rm[k]) if isinstance(v, tuple) else float(v)) for k, v in spec.items()}
    Wb = sum(P[k][0] * m for k, m in mult.items()); Rb = sum(P[k][1] * m for k, m in mult.items())
    print(f"[bench150] eval base ({base}): " + ", ".join(f"{k} {'$' + str(v[1]) + ' risk' if isinstance(v, tuple) else v}" for k, v in spec.items()), flush=True)
    sys.argv = ["x", "scratch_data"]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    Sp = pd.read_pickle("scratch_data/single_print_sessions.pkl"); flag = Sp.flag.reindex(dts).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag; lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    lab.W["TWIN"] = Wt; lab.C["TWIN"] = Rt[:, -1]
    return dict(g=g, B=B, trr=trr, D=D, dts=dts, yr=yr, Wb=Wb, Rb=Rb, Wt=Wt, Rt=Rt, Tn=Tn, lab=lab, P=P, mult=mult, base=base)


def to_nq_days(ctx, gx, W, R):
    edts = pd.DatetimeIndex(gx.ts); epos = pd.Series(np.arange(len(edts)), index=edts)
    idx = np.array([epos.get(d, -1) for d in ctx["dts"]]); Wo = np.zeros((ctx["D"], 1440)); Ro = np.zeros((ctx["D"], 1440)); m = idx >= 0
    Wo[m] = W[idx[m]]; Ro[m] = R[idx[m]]
    return Wo, Ro


def eval_bench(ctx, cands, end="2026-09-01", label="150K evaluation (set + Twin 2 MNQ)"):
    D, dts, yr, Wb, Rb = (ctx[k] for k in ("D", "dts", "yr", "Wb", "Rb")); ok = (yr >= 2018) & (dts <= end)
    def ev(Wx, Rx):
        res = [evaluation(Wb + Wx, Rb + Rx, s, D, R150) for s in range(D)]; return np.array([x[0] if x else "" for x in res]), ok & np.array([x is not None for x in res])
    o0, v0 = ev(0.0, 0.0); print(f"   {label} alone: pass {(o0 == 'pass')[v0].mean():.1%} (starts to {end})")
    out = {}
    for nm, (W, R) in cands.items():
        o, v = ev(W, R); d = ((o == "pass").astype(float) - (o0 == "pass").astype(float))[v & v0]
        rng = np.random.default_rng(1); nb = int(np.ceil(len(d) / 60)); st = rng.integers(0, len(d), (2000, nb)); mm = d[((st[:, :, None] + np.arange(60)) % len(d)).reshape(2000, -1)[:, :len(d)]].mean(axis=1)
        print(f"   {nm:<34} pass {(o == 'pass')[v].mean():5.1%} ({d.mean():+.1%}; band {np.percentile(mm, 5):+.1%} / {np.percentile(mm, 95):+.1%})", flush=True)
        out[nm] = d.mean()
    return out


def funded_bench(ctx, variants, extra=None, end="2026-10-09", label="Funded 150K x 1.5 + Twin 2 MNQ"):
    lab, dts = ctx["lab"], ctx["dts"]
    for k, (W, C) in (extra or {}).items(): lab.W[k] = W; lab.C[k] = C
    V = {"base: plan x 1.5 + Twin 2": BASE_FUNDED, **variants}
    keys = sorted({k for p in V.values() for k in p}); Wall = np.stack([lab.W[k] for k in keys]); Call = np.stack([lab.C[k] for k in keys]); bases = {}
    for nm, p in V.items():
        names, b = lab._base(p); Bm = np.zeros((len(keys), lab.D))
        for i, k in enumerate(names): Bm[keys.index(k)] = b[i]
        bases[nm] = Bm
    chg = np.zeros(Wall.shape[2], bool); chg[-1] = True; chg[1:] |= (np.abs(np.diff(Wall, axis=2)) > 0).any(axis=(0, 1)); chg[0] |= (Wall[:, :, 0] != 0).any()
    Wc = np.ascontiguousarray(Wall[:, :, chg]); days = np.where((dts >= "2018-01-01") & (dts <= end))[0]; rng = np.random.default_rng(1); n, H, L_ = 600, 500, 20
    stb = rng.integers(0, len(days), (n, H // L_)); hist = days[((stb[:, :, None] + np.arange(L_)) % len(days)).reshape(n, -1)[:, :H]]; Rr = {nm: np.zeros((n, 3)) for nm in V}
    for hh in range(n):
        ix = hist[hh]; Wh = np.ascontiguousarray(Wc[:, ix]); Ch = np.ascontiguousarray(Call[:, ix])
        for nm, Bm in bases.items():
            r = F.simulate_sized(Wh, Ch, np.ascontiguousarray(Bm[:, ix]), horizon=H, starts=[0], fmin=0.5, fmax=1.0, ref=3000.0); Rr[nm][hh] = [r["paid"][0], r["blown"][0], r["payouts"][0] == 6]
    b0 = Rr[list(V)[0]][:, 0]; print(f"   {label}, 600 paired histories (to {end}), 2 years:")
    for nm, r in Rr.items(): print(f"      {nm:<34} 2y ${r[:, 0].mean():>7,.0f} blown {r[:, 1].mean():5.1%} all 6 {r[:, 2].mean():5.1%} diff ${(r[:, 0] - b0).mean():+5,.0f} beats {np.mean(r[:, 0] > b0) + 0.5 * np.mean(r[:, 0] == b0):5.1%}")
    return Rr


def personal(cands, drop=(), end=None):
    """cands: {name: daily $ Series (already sized, costs in)} added to the personal book (minus `drop` columns)."""
    Pp = pd.read_pickle("scratch_data/personal_P.pkl"); Pp = Pp[[c for c in Pp.columns if c not in ("FC2B", "Kusho", "S47", "S30")]]
    if end is not None: Pp = Pp[Pp.index <= end]
    base = Pp.drop(columns=[c for c in drop if c in Pp]).sum(axis=1)
    mcf = lambda x: (lambda d_: d_["pnl_p50"] / d_["dd_p95"])(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1))
    full = Pp.sum(axis=1)
    for per, m in (("2018-26", np.ones(len(Pp), bool)), ("2018-22", Pp.index.year <= 2022), ("2023+", Pp.index.year >= 2023)):
        r0 = mcf(full[m]); parts = [f"book {r0:.2f}"]
        for nm, s in cands.items():
            r = mcf((base + s.reindex(Pp.index, fill_value=0.0))[m]); parts.append(f"{nm} {r:.2f} ({r - r0:+.2f})")
        print(f"      {per}: " + " | ".join(parts))
