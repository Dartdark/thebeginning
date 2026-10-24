"""The user's limit-only Vault Break (analysis/vb_gv_limit_test.py, CT clock, touch fills) in the 50K evaluation (combine
set VB 8 MNQ / ONB ADX30 $1,100 / Bridge Monday 2 / EOS $500): in place of VB v1 (8 MNQ, and 4 + 4), and added at 2 / 4.
Trades booked on their own minute paths (worst point from the 1-minute lows); limit fills, no slippage.
  python3 analysis/vb_gv_limit_bench.py   (needs scratch_data/g24.pkl)
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import combine_levers_test as CL
import vb_gv_limit_test as VG

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    yr = pd.DatetimeIndex(g.ts[trr]).year
    t = VG.run(g); t["day"] = t.entry_i // 288; same = (t.exit_i // 288) == t.day
    print(f"[new VB trades {len(t)}, carried past the date {(~same).sum()} (left out)]")
    t = t[same].copy(); t["j0"] = (t.entry_i % 288) * 5 - 4; t["j1"] = (t.exit_i % 288) * 5; t["side"] = 1; t["kind"] = 1
    P = {}
    for nm, tt in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                   ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0]))), ("NEW", t)):
        w, r = paths(g, tt); P[nm] = (w[trr] / 10, r[trr] / 10)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
    one = lambda p, c, n: 1.0; wo = {a: b for a, b in q.items() if a != "VB"}
    cases = [("combine set (VB v1 8)", q), ("VB v1 -> new 8", {**wo, "NEW": 8.0}), ("VB v1 -> new 6", {**wo, "NEW": 6.0}),
             ("VB v1 4 + new 4", {**q, "VB": 4.0, "NEW": 4.0}), ("+ new 2", {**q, "NEW": 2.0}), ("+ new 4", {**q, "NEW": 4.0})]
    for nm, qq in cases:
        W = sum(P[x][0] * qq[x] for x in qq); Rr = sum(P[x][1] * qq[x] for x in qq)
        res = [CL.challenge(W, Rr, np.arange(s0, min(s0 + CL.MAXD, D)), one) for s0 in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); ps = o == "pass"
        n = np.array([x[1] if x else 0 for x in res])
        print(f"   {nm:<24} pass {ps[ok].mean():5.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, 23-26 {ps[ok & (yr >= 2023)].mean():5.1%}), "
              f"blown {(o[ok] == 'fail').mean():5.1%}, median days {np.median(n[ok & ps]):.0f}", flush=True)
