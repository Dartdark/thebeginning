"""S47 v2 (user's Europe-Open Impulse, 2026-10-23) in the Apex plans: add or replace, same benches as FC 2B
(analysis/fc_2b_bench.py: bootstrapped 50K funded bench with the current plan; 50K combine set).
Trades = the Python rebuild (analysis/s47_test.py -> checks/candidates/s47_v2/python_trades_v2.csv, which matches the author's
MultiCharts years), our costs, sized in MNQ.
  python3 analysis/s47_bench.py SCRATCH_DIR [worker SEED N | merge | combine]
"""
import sys, time, pickle, glob, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import funded_bootstrap as FB, combine_levers_test as CL

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "merge"
KIND = {"stop": 0, "target": 1, "flat": 2}
FCREP = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute FC 2B v2.xlsx"


def s47_trades():
    t = pd.read_csv("checks/candidates/s47_v2/python_trades_v2.csv", parse_dates=["date"])
    t["kind"] = np.where(t.kind == "stop", 0, 2)
    t["exit"] = t.exit - t.side * 0.5            # paths() charges $7.25; the 2 ticks of slippage go into the exit price
    return t


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); T0 = time.time()
    fast_plan_lab = runpy.run_path("analysis/fc_2b_bench.py", run_name="lib")["fast_plan_lab"]
    lab = fast_plan_lab(SP); FB.add_moc_mes(lab, SP)
    rs = pd.read_csv(SP + "rs_trades.csv"); rs["kind"] = rs.kind.map(KIND); lab.add("RS_L", rs[rs.side > 0].reset_index(drop=True))
    s = s47_trades(); lab.add("S47", s, slippage=False)
    fc = load_mc(lab.g, FCREP); fc = fc[pd.DatetimeIndex(lab.g.ts[fc.day]) >= "2018-01-01"].reset_index(drop=True); lab.add("FC", fc)
    print(f"S47 v2 trades {len(s)}; per NQ from the lab ${lab.C['S47'].sum() * 10 / len(s):.0f} a trade (rebuild ${s.net.mean():.0f})")
    CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2, "RS_L": 1}
    drop = lambda *ks: {k: v for k, v in CUR.items() if k not in ks}
    plans = {"plan": CUR, "+ S47 v2 1 MNQ": {**CUR, "S47": 1}, "+ S47 v2 2 MNQ": {**CUR, "S47": 2},
             "+ S47 v2 1 + FC 2B 1": {**CUR, "S47": 1, "FC": 1}, "RS longs -> S47 v2 1": {**drop("RS_L"), "S47": 1},
             "  RS longs slot empty": drop("RS_L")}
    if MODE == "worker":
        seed, n = int(sys.argv[3]), int(sys.argv[4])
        res, y1, _ = FB.Boot(lab).run(plans, n=n, L=20, seed=seed)
        pickle.dump((res, y1), open(SP + f"s47_boot_{seed}.pkl", "wb")); print(f"[worker {seed} done {time.time() - T0:.0f}s]"); sys.exit()
    if MODE == "merge":
        parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + "s47_boot_*.pkl"))]
        res = {k: np.concatenate([p[0][k] for p in parts]) for k in plans}; y1 = {k: np.concatenate([p[1][k] for p in parts]) for k in plans}
        B = FB.Boot(lab); B.run = lambda *a, **k: (res, y1, 0)
        print(f"\nA. 50K funded, bootstrapped ({len(res['plan'])} paired histories, 20-day blocks, 2 years):")
        df, s_, _ = B.compare(plans); print(s_)
        print("\n   Daily correlation of S47 v2 with the plan pieces:"); print(lab.corr(["S47", "FC"] + list(CUR)).loc["S47"].round(2).to_string())
        sys.exit()
    print("\nB. 50K evaluation (combine set + S47 v2):")
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr); yr = pd.DatetimeIndex(g.ts[trr]).year
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0]))),
                  ("S47", s)):
        w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
    one = lambda p, c, n: 1.0
    for k in (0, 1, 2, 3):
        qq = {**q, "S47": float(k)}
        W = sum(P[x][0] * qq[x] for x in qq); Rr = sum(P[x][1] * qq[x] for x in qq)
        res = [CL.challenge(W, Rr, np.arange(s0, min(s0 + CL.MAXD, D)), one) for s0 in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); ps = o == "pass"
        print(f"   combine set + S47 v2 {k} MNQ: pass {ps[ok].mean():5.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, 23-26 {ps[ok & (yr >= 2023)].mean():5.1%})")
