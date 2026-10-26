"""MAGNET18 in the 50K evaluation: combine set (VB 8, ONB ADX30 $1,100, Bridge Monday 2, EOS $500) + MAGNET18 1-3 MNQ
(early-close days left out: the file would hold through the 12:00 CT halt, not allowed on Apex).
  python3 analysis/magnet18_bench.py SCRATCH_DIR   (needs magnet18_days.csv from analysis/magnet18_test.py)
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import combine_levers_test as CL
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    T = pd.read_csv(SP + "magnet18_days.csv", parse_dates=["date"]); T = T[T.gate & ~T.early]
    t = pd.DataFrame(dict(day=T.r, j0=jof(1031), j1=jof(1429), side=1, entry=T.e, exit=T.x, kind=2)).reset_index(drop=True)
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    yr = pd.DatetimeIndex(g.ts[trr]).year; P = {}
    for nm, tt in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                   ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0]))), ("M18", with_slippage(t))):
        w, r = paths(g, tt); P[nm] = (w[trr] / 10, r[trr] / 10)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
    one = lambda p, c, n: 1.0
    for nm, qq in [(f"combine set + MAGNET18 {k} MNQ", {**q, "M18": float(k)}) for k in (0, 1, 2, 3)] + \
                  [(f"EOS -> MAGNET18 {k} MNQ", {**q, "EOS": 0.0, "M18": float(k)}) for k in (1, 2)]:
        Ws = sum(P[x][0] * qq[x] for x in qq); Rs = sum(P[x][1] * qq[x] for x in qq)
        res = [CL.challenge(Ws, Rs, np.arange(s0, min(s0 + CL.MAXD, D)), one) for s0 in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); ps = o == "pass"
        nd = np.array([x[1] if x else 0 for x in res])
        print(f"   {nm:<32} pass {ps[ok].mean():5.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, 23-26 {ps[ok & (yr >= 2023)].mean():5.1%}), "
              f"fail {(o == 'fail')[ok].mean():5.1%}, median days to pass {np.median(nd[ok & ps]):.0f}")
