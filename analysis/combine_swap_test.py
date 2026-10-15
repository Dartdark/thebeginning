"""Combine swaps (2026-10-15): the combine runs Overnight Bias ADX30 ($1,100 risk) while the funded plan runs the stronger
Overnight Bias ML v2 (deflated Sharpe 0.99). Does the ML version, or the whole funded plan scaled up, pass more often?
Every start day 2018-2026, Apex 50K combine rules (analysis/combine_levers_test.challenge, static sizing); CL fade left out
(NQ paths only).
  python3 analysis/combine_swap_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from combine_levers_test import challenge, MAXD, ONB30

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr); yr = pd.DatetimeIndex(g.ts[trr]).year
    P = {}
    srcs = {"VB": with_slippage(load_mc(g, REPORTS["VB"][0])), "ONB30": with_slippage(load_mc(g, ONB30)), "ONB_ML": with_slippage(load_mc(g, REPORTS["ONB_ML2_MC"][0])),
            "MON_BR": load_bridge_mc(g), "EOS": with_slippage(load_mc(g, REPORTS["EOS"][0])), "MON": with_slippage(load_mc(g, REPORTS["MON_MC"][0])),
            "LDF": with_slippage(load_mc(g, REPORTS["LDF_MC"][0])), "NFP": with_slippage(load_mc(g, REPORTS["NFP_MC"][0]))}
    for k, t in srcs.items():
        w, r = paths(g, t); P[k] = (w[trr] / 10, r[trr] / 10)
    risk = lambda d, m: np.floor(d / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    def run(q, nm):
        W = sum(P[k][0] * v for k, v in q.items()); R = sum(P[k][1] * v for k, v in q.items())
        res = [challenge(W, R, np.arange(s, min(s + MAXD, D)), lambda p, c, n: 1.0) for s in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x is not None else "" for x in res]); ps = o == "pass"
        dd = np.array([x[1] if x is not None else 0 for x in res])
        print(f"   {nm:<58} pass {ps[ok].mean():6.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, 23-26 {ps[ok & (yr >= 2023)].mean():5.1%}) "
              f"blown {(o[ok] == 'fail').mean():5.1%} time {(o[ok] == 'time').mean():5.1%} median days {np.median(dd[ok & ps]):.0f}", flush=True)
    base = {"VB": 8.0, "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
    run({**base, "ONB30": risk(1100, 0.25)}, "plan: VB 8 + ONB ADX30 $1,100 + Bridge Mon 2 + EOS $500")
    for d in (800, 1100, 1400):
        run({**base, "ONB_ML": risk(d, 0.30)}, f"ONB ML ${d:,} instead of ONB ADX30")
    run({**base, "ONB30": risk(1100, 0.25), "ONB_ML": risk(600, 0.30)}, "ONB ADX30 $1,100 + ONB ML $600")
    fp = lambda s: {"VB": 3.0 * s, "ONB_ML": risk(400 * s, 0.30), "MON": 1.0 * s, "EOS": risk(700 * s, REPORTS["EOS"][1]), "LDF": 2.0 * s,
                    "NFP": risk(500 * s, REPORTS["NFP_MC"][1]), "MON_BR": 1.0 * s}
    for s in (1.5, 2.0, 2.5, 3.0):
        run(fp(s), f"the funded plan (no CL) x {s}")
    # ONB ML $1,100 with the two state levers that were not negative in combine_levers_test (3 follow-ups, post-hoc)
    from combine_levers_test import challenge as ch
    q = {**base, "ONB_ML": risk(1100, 0.30)}
    W = sum(P[k][0] * v for k, v in q.items()); R = sum(P[k][1] * v for k, v in q.items())
    for nm, fn, ds in (("ONB ML $1,100 + behind x1.5 from day 11 if profit < $1,000", lambda p, c, n: 1.5 if (n >= 11 and p < 1000) else 1.0, 1000.0),
                       ("ONB ML $1,100 + finish x0.5 once profit >= $2,000", lambda p, c, n: 0.5 if p >= 2000 else 1.0, 1000.0),
                       ("ONB ML $1,100 + VB 10", None, 1000.0)):
        if fn is None:
            q2 = {**q, "VB": 10.0}; W2 = sum(P[k][0] * v for k, v in q2.items()); R2 = sum(P[k][1] * v for k, v in q2.items()); fn2 = lambda p, c, n: 1.0
        else: W2, R2, fn2 = W, R, fn
        res = [ch(W2, R2, np.arange(s, min(s + MAXD, D)), fn2, ds) for s in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x is not None else "" for x in res]); ps = o == "pass"
        print(f"   {nm:<58} pass {ps[ok].mean():6.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, 23-26 {ps[ok & (yr >= 2023)].mean():5.1%}) "
              f"blown {(o[ok] == 'fail').mean():5.1%} time {(o[ok] == 'time').mean():5.1%}", flush=True)
