"""EOS size (user, 2026-10-16: 'would upping the size hurt the plan since it only trades 12 times a year?').
Combine (VB 8 + ONB ADX30 $1,100 + Bridge Monday 2 + EOS $X, Apex 50K rules, every start day 2018-26) and funded bench
(current plan with EOS ('risk', X), cushion $1,500, 1 / 2 years).
  python3 analysis/eos_size_check.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from combine_levers_test import challenge, MAXD, ONB30

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    g = lab.g; atr = g.daily_atr(15); tr = g.trading; D = len(tr); yr = pd.DatetimeIndex(g.ts[tr]).year
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))):
        w, r = paths(g, t); P[nm] = (w[tr] / 10, r[tr] / 10)
    rk = lambda d, m: np.floor(d / (np.nan_to_num(m * atr[tr], nan=1e12) * 2))[:, None]
    print("\nCombine:")
    for x in (0, 500, 750, 1000, 1500):
        q = {"VB": 8.0, "ONB30": rk(1100, 0.25), "MON_BR": 2.0, "EOS": rk(x, REPORTS["EOS"][1]) if x else 0.0}
        W = sum(P[k][0] * q[k] for k in P); R = sum(P[k][1] * q[k] for k in P)
        res = [challenge(W, R, np.arange(s, min(s + MAXD, D)), lambda p, c, n: 1.0) for s in range(D)]
        ok = np.array([z is not None for z in res]) & (yr >= 2018); o = np.array([z[0] if z else "" for z in res]); ps = o == "pass"
        print(f"   EOS ${x:>5}: pass {ps[ok].mean():.1%} (2018-22 {ps[ok & (yr < 2023)].mean():.1%}, 2023-26 {ps[ok & (yr >= 2023)].mean():.1%}) blown {(o[ok] == 'fail').mean():.1%}", flush=True)
    dates = pd.DatetimeIndex(g.ts[lab.tr])
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    base = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    print("\nFunded 50K (cushion $1,500):")
    for x in (0, 500, 700, 1000, 1400, 2000):
        p = {**base, "EOS": ("risk", x)} if x else base
        a, c = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0)
        print(f"   EOS ${x:>5}: 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%} paid {a['any_payout']:.0%}", flush=True)
