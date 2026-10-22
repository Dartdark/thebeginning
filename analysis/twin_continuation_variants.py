"""Twin Continuation for prop accounts (2026-10-15): the breakout's swing-level stop risks ~$4,300 per NQ when hit (worst trade
-$11,700), too wide for a $2,000 trailing drawdown. Tests the code's own BO_MaxStopMult input (stop capped at k x 15-min ATR,
k = 1.0 / 2.0), then the funded bench (plan + Twin capped / MO only / replacing Overnight Bias ML) and the combine set.
  python3 analysis/twin_continuation_variants.py [SCRATCH_DIR]
"""
import sys, io, pickle, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import twin_continuation_test as tc
from twin_continuation_bench import grids
from portfolio import load_mc, paths, challenge
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    g = lab.g; B = tc.flatten(g); TT = {"orig": pd.read_pickle(SP + "twin_trades.pkl")}
    for k in (1.0, 2.0):
        T = tc.simulate(B, max_stop_mult=k); TT[f"cap{k:g}"] = T[T.date >= "2018-01-01"].reset_index(drop=True)
    print("\nBreakout leg by stop cap (per NQ, repo costs):")
    for nm, T in TT.items():
        X = T.set_index("date")
        for st in ("BO", "MO"):
            x = X[X.setup == st].net; print(tc.line(x, f"{nm} {st}") + f" | worst ${x.min():,.0f}")
        print(tc.line(X.net, f"{nm} ALL"))
    dates = pd.DatetimeIndex(g.ts[lab.tr])
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    for nm, T in TT.items():
        for part, m in (("", np.ones(len(T), bool)), ("_MO", (T.setup == "MO").to_numpy())):
            if part == "_MO" and nm != "orig": continue
            W, Rr = grids(g, B, T[m]); lab.W[nm + part] = W[lab.tr] / 10; lab.C[nm + part] = Rr[lab.tr][:, -1] / 10
    base = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2,
            "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    noonb = {k: v for k, v in base.items() if k != "ONB_ML2_MC"}
    sc = lambda p: (lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0))
    print("\nFunded bench (cushion $1,500):")
    for nm, p in (("plan", base), ("+ Twin cap1 1 MNQ", {**base, "cap1": 1}), ("+ Twin cap1 2 MNQ", {**base, "cap1": 2}),
                  ("+ Twin cap2 1 MNQ", {**base, "cap2": 1}), ("+ Twin cap2 2 MNQ", {**base, "cap2": 2}),
                  ("+ MO 1 MNQ", {**base, "orig_MO": 1}), ("ONB ML -> MO 2 MNQ", {**noonb, "orig_MO": 2}),
                  ("ONB ML -> Twin cap1 2 MNQ", {**noonb, "cap1": 2})):
        r = sc(p)
        print(f"   {nm:<28} ${r[0]['expected']:,.0f} / ${r[1]['expected']:,.0f}  blown {r[0]['blown']:.0%} / {r[1]['blown']:.0%}  paid {r[0]['any_payout']:.0%}"
              f" | 1y 2018-22 ${r[0]['s2018_22']:,.0f} 2023+ ${r[0]['s2023_on']:,.0f}")
    print("\nCombine (VB 8 + ONB ADX30 $1,100 + Bridge Monday 2 + EOS $500, Apex challenge rules, every start day):")
    atr = g.daily_atr(15); tr = g.trading; D = len(tr); yr = pd.DatetimeIndex(g.ts[tr]).year; P = {}
    def add(nm, t): w, r = paths(g, t); P[nm] = (w[tr] / 10, r[tr] / 10)
    add("VB", with_slippage(load_mc(g, REPORTS["VB"][0])))
    add("ONB30", with_slippage(load_mc(g, "mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx")))
    add("MON_BR", load_bridge_mc(g)); add("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))
    for nm in ("orig", "cap1", "cap2", "orig_MO"):
        P[nm] = (lab.W[nm] * 0 + 0, None)
        Tm = TT[nm.replace("_MO", "")]; Tm = Tm[Tm.setup == "MO"] if nm.endswith("_MO") else Tm
        W, Rr = grids(g, B, Tm); P[nm] = (W[tr] / 10, Rr[tr] / 10)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[tr], nan=1e12) * 2))[:, None]
    q_onb = risk(1100, 0.25); q_eos = risk(500, REPORTS["EOS"][1])
    def score(extra):
        W = P["VB"][0] * 8 + P["ONB30"][0] * q_onb + P["MON_BR"][0] * 2 + P["EOS"][0] * q_eos
        Rr = P["VB"][1] * 8 + P["ONB30"][1] * q_onb + P["MON_BR"][1] * 2 + P["EOS"][1] * q_eos
        for k, q in extra.items(): W = W + P[k][0] * q; Rr = Rr + P[k][1] * q
        res = [challenge(W, Rr, np.arange(s, min(s + 21, D))) for s in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018)
        o = np.array([np.nan if x is None else float(x[0] == "pass") for x in res])
        dd = np.array([np.nan if x is None or x[0] != "pass" else x[1] for x in res])
        return np.nanmean(o[ok]), np.nanmean(o[ok & (yr >= 2023)]), np.nanmedian(dd[ok])
    for nm, ex in (("combine now", {}), ("+ Twin cap1 2 MNQ", {"cap1": 2}), ("+ Twin cap1 4 MNQ", {"cap1": 4}),
                   ("+ Twin cap2 2 MNQ", {"cap2": 2}), ("+ MO 2 MNQ", {"orig_MO": 2}), ("+ MO 4 MNQ", {"orig_MO": 4}),
                   ("+ Twin orig 2 MNQ", {"orig": 2})):
        a, b, d = score(ex); print(f"   {nm:<22} pass {a:.1%} (2023-26 {b:.1%}), median days {d:.0f}")
