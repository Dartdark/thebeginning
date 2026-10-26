"""Does adding S47 v2 or FC 2B change the DAYS to pass the 50K evaluation? (user, 2026-10-23)
Combine set (VB 8, ONB ADX30 $1,100, Bridge Monday 2, EOS $500) + S47 v2 / FC 2B at 0-3 MNQ; combine_levers_test.challenge
(+$3,000 target, $2,000 EOD trail, $1,000 daily limit, 21-trading-day window); every start day 2018-2026.
Reports pass rate, median / mean trading days to pass (passes only) and the share passing within 5 / 10 days.
  python3 analysis/combine_days_test.py SCRATCH_DIR
"""
import sys, pickle, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import combine_levers_test as CL

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
FCREP = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute FC 2B v2.xlsx"

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr); yr = pd.DatetimeIndex(g.ts[trr]).year
    s47 = runpy.run_path("analysis/s47_bench.py", run_name="lib")["s47_trades"](g)
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0]))),
                  ("S47", s47), ("FC", with_slippage(load_mc(g, FCREP)))):
        w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
    one = lambda p, c, n: 1.0
    for add, ks in (("none", (0,)), ("S47", (1, 2, 3)), ("FC", (1, 2, 3))):
        for k in ks:
            qq = {**q, add: float(k)} if add != "none" else q
            W = sum(P[x][0] * qq[x] for x in qq); Rr = sum(P[x][1] * qq[x] for x in qq)
            res = [CL.challenge(W, Rr, np.arange(s0, min(s0 + CL.MAXD, D)), one) for s0 in range(D)]
            ok = np.array([x is not None for x in res]) & (yr >= 2018)
            o = np.array([x[0] if x else "" for x in res]); n = np.array([x[1] if x else 0 for x in res])
            ps = ok & (o == "pass"); fl = ok & (o == "fail")
            nm = "combine set" if add == "none" else f"+ {'S47 v2' if add == 'S47' else 'FC 2B'} {k} MNQ"
            print(f"   {nm:<18} pass {ps.sum() / ok.sum():5.1%} | days to pass median {np.median(n[ps]):4.1f}, mean {n[ps].mean():4.1f} | "
                  f"passed within 5 days {np.mean((n <= 5)[ok] & ps[ok]):5.1%}, within 10 {np.mean((n <= 10)[ok] & ps[ok]):5.1%} | "
                  f"fail {fl.sum() / ok.sum():5.1%} (median day {np.median(n[fl]):.0f})")
