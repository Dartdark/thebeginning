"""GC_COMBO v2 (user's upload 2026-10-24) in the Apex plans, at MGC (= GC / 10; 1 MGC at |score| 2 and the stretch, 2 at >= 3).
Trades = analysis/gc_combo_test.py's rebuild (vote B by the minute tick-rule proxy). Each GC trade is intraday (07:20-15:00 CT),
booked on its NQ trading day with its own minute path (worst point from the GC lows / highs).
  A. 50K funded, bootstrapped bench (1,000 paired 2-year histories): plan + COMBO 1 / 2 x; in place of CL Sunday (the other
     non-NQ piece).
  B. 50K evaluation: combine set + COMBO 1 / 2 / 3 x.
  [GCC_SRC=gc_combo_trades_mc.csv] python3 analysis/gc_combo_bench.py SCRATCH_DIR [worker SEED N | merge | combine]
  (needs gc_combo_trades.csv from the rebuild, or gc_combo_trades_mc.csv from analysis/gc_combo_mc_eval.py; gc.pkl)
"""
import sys, time, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import funded_bootstrap as FB, combine_levers_test as CL
from fc_2b_bench import fast_plan_lab, KIND

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "merge"
import os
SRC = os.environ.get("GCC_SRC", "gc_combo_trades.csv")      # gc_combo_trades_mc.csv = the user's MultiCharts trades (2026-10-24)
PV, TICK, COMM = 100.0, 0.10, 7.25


def gc_paths(sp, dates):
    """(worst, real) per NQ trading day x minute, $ per MGC unit (contracts as traded / 10)."""
    gc = pickle.load(open(sp + "gc.pkl", "rb")); T = pd.read_csv(sp + SRC, parse_dates=["date"])
    if "same_day" in T: T = T[T.same_day]     # MC trades held over a holiday halt (13 of 1,188) are not Apex-legal: left out
    pos = pd.Series(np.arange(len(dates)), index=dates); W = np.zeros((len(dates), 1440)); Rr = np.zeros((len(dates), 1440)); miss = 0
    for t in T.itertuples():
        if t.date not in pos.index: miss += 1; continue
        i = pos[t.date]; seg = slice(t.j0, t.j1 + 1)
        adv = (gc.l[t.day, seg] if t.side > 0 else gc.h[t.day, seg])
        a = ((np.nan_to_num(adv, nan=t.e) - t.e) * t.side * PV - COMM) * t.qty / 10
        a[-1] = min(a[-1], t.net / 10)
        W[i, seg] += a; W[i, t.j1 + 1:] += t.net / 10; Rr[i, t.j1:] += t.net / 10
    print(f"[GC trades {len(T)}, not on an NQ trading day {miss}]")
    return W, Rr


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); T0 = time.time()
    if MODE != "combine":
        lab = fast_plan_lab(SP); FB.add_moc_mes(lab, SP)
        rs = pd.read_csv(SP + "rs_trades.csv"); rs["kind"] = rs.kind.map(KIND); lab.add("RS_L", rs[rs.side > 0].reset_index(drop=True))
        W, Rr = gc_paths(SP, pd.DatetimeIndex(lab.g.ts[lab.tr]))
        k = lab.W["VB"].shape[1]
        lab.W["GCC"] = W.min(axis=1)[:, None] * np.ones((1, k)); lab.C["GCC"] = Rr[:, -1]      # daily worst point, as CLS
        CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2, "RS_L": 1}
        drop = lambda *ks: {kk: v for kk, v in CUR.items() if kk not in ks}
        plans = {"plan": CUR, "+ GC_COMBO 1x MGC": {**CUR, "GCC": 1}, "+ GC_COMBO 2x MGC": {**CUR, "GCC": 2},
                 "CL Sunday -> GC_COMBO 1x": {**drop("CLS"), "GCC": 1}}
        if MODE == "worker":
            seed, n = int(sys.argv[3]), int(sys.argv[4])
            res, y1, _ = FB.Boot(lab).run(plans, n=n, L=20, seed=seed)
            pickle.dump((res, y1), open(SP + f"gcc_boot_{SRC[:-4]}_{seed}.pkl", "wb")); print(f"[worker {seed} done {time.time() - T0:.0f}s]"); sys.exit()
        import glob
        parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + f"gcc_boot_{SRC[:-4]}_*.pkl"))]
        res = {kk: np.concatenate([p[0][kk] for p in parts]) for kk in plans}; y1 = {kk: np.concatenate([p[1][kk] for p in parts]) for kk in plans}
        B = FB.Boot(lab); B.run = lambda *a, **k_: (res, y1, 0)
        print(f"\nA. 50K funded, bootstrapped ({len(res['plan'])} paired histories, 20-day blocks, 2 years):")
        df, s_, _ = B.compare(plans); print(s_)
        print("\n   Daily correlation of GC_COMBO with the plan pieces:"); print(lab.corr(["GCC"] + list(CUR)).loc["GCC"].round(2).to_string())
        sys.exit()
    print("\nB. 50K evaluation (combine set + GC_COMBO at MGC):")
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    yr = pd.DatetimeIndex(g.ts[trr]).year; P = {}
    for nm, tt in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                   ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))):
        w, r = paths(g, tt); P[nm] = (w[trr] / 10, r[trr] / 10)
    P["GCC"] = gc_paths(SP, pd.DatetimeIndex(g.ts[trr]))
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
    one = lambda p, c, n: 1.0
    for nm, qq in [(f"combine set + GC_COMBO {k}x MGC", {**q, "GCC": float(k)}) for k in (0, 1, 2, 3)]:
        Ws = sum(P[x][0] * qq[x] for x in qq); Rs = sum(P[x][1] * qq[x] for x in qq)
        res = [CL.challenge(Ws, Rs, np.arange(s0, min(s0 + CL.MAXD, D)), one) for s0 in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); ps = o == "pass"
        nd = np.array([x[1] if x else 0 for x in res])
        print(f"   {nm:<32} pass {ps[ok].mean():5.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, 23-26 {ps[ok & (yr >= 2023)].mean():5.1%}), "
              f"fail {(o == 'fail')[ok].mean():5.1%}, median days to pass {np.median(nd[ok & ps]):.0f}")
