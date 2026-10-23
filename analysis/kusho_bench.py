"""Kusho in the Apex plans (2026-10-23): the Apex-shaped versions only (Kusho v9 flat at 15:45 = 'v9_RTH', and C03).
Trades = the Python rebuild (analysis/kusho_test.py -> checks/candidates/kusho/python_trades_{v9_RTH,C03}.csv; exit prices
already include the 1-tick stop / market slippage, paths() adds $7.25), sized in MNQ.
  A. 50K funded, bootstrapped (as analysis/fc_2b_bench.py): + v9_RTH 1 / 2, + C03 1, VB -> v9_RTH (and the VB slot empty),
     RS longs -> v9_RTH.   B. 50K evaluation: combine set + v9_RTH / C03 1-3 MNQ, and VB 8 -> v9_RTH 4 / 8.
  python3 analysis/kusho_bench.py SCRATCH_DIR [worker SEED N | merge | combine]
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
KIND = {"stop": 0, "target": 1, "flat": 2, "eod": 2}


def trades(name):
    t = pd.read_csv(f"checks/candidates/kusho/python_trades_{name}.csv", parse_dates=["date"])
    t["day"] = t.fm // 1440; t["j0"] = t.fm % 1440; t["j1"] = t.xm % 1440; t["kind"] = t.kind.map(KIND)
    assert (t.xm // 1440 == t.day).all()
    return t


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); T0 = time.time()
    fast_plan_lab = runpy.run_path("analysis/fc_2b_bench.py", run_name="lib")["fast_plan_lab"]
    lab = fast_plan_lab(SP); FB.add_moc_mes(lab, SP)
    rs = pd.read_csv(SP + "rs_trades.csv"); rs["kind"] = rs.kind.map({"stop": 0, "target": 1, "flat": 2})
    lab.add("RS_L", rs[rs.side > 0].reset_index(drop=True))
    for nm in ("v9_RTH", "C03"): lab.add(nm, trades(nm), slippage=False)
    print("per NQ from the lab: " + ", ".join(f"{nm} ${lab.C[nm].sum() * 10 / len(trades(nm)):.0f}" for nm in ("v9_RTH", "C03")))
    CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2, "RS_L": 1}
    drop = lambda *ks: {k: v for k, v in CUR.items() if k not in ks}
    plans = {"plan": CUR, "+ Kusho v9 15:45 1 MNQ": {**CUR, "v9_RTH": 1}, "+ Kusho v9 15:45 2 MNQ": {**CUR, "v9_RTH": 2},
             "+ C03 1 MNQ": {**CUR, "C03": 1}, "VB -> Kusho v9 15:45 1": {**drop("VB_N", "VB_F"), "v9_RTH": 1},
             "  VB slot empty": drop("VB_N", "VB_F"), "RS longs -> Kusho v9 15:45 1": {**drop("RS_L"), "v9_RTH": 1},
             "  RS longs slot empty": drop("RS_L")}
    if MODE == "worker":
        seed, n = int(sys.argv[3]), int(sys.argv[4])
        res, y1, _ = FB.Boot(lab).run(plans, n=n, L=20, seed=seed)
        pickle.dump((res, y1), open(SP + f"kusho_boot_{seed}.pkl", "wb")); print(f"[worker {seed} done {time.time() - T0:.0f}s]"); sys.exit()
    if MODE == "merge":
        parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + "kusho_boot_*.pkl"))]
        res = {k: np.concatenate([p[0][k] for p in parts]) for k in plans}; y1 = {k: np.concatenate([p[1][k] for p in parts]) for k in plans}
        B = FB.Boot(lab); B.run = lambda *a, **k: (res, y1, 0)
        print(f"\nA. 50K funded, bootstrapped ({len(res['plan'])} paired histories, 20-day blocks, 2 years):")
        df, s_, _ = B.compare(plans); print(s_)
        print("\n   Daily correlation with the plan pieces:"); print(lab.corr(["v9_RTH", "C03"] + list(CUR)).loc[["v9_RTH", "C03"]].round(2).T.to_string())
        sys.exit()
    print("\nB. 50K evaluation:")
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr); yr = pd.DatetimeIndex(g.ts[trr]).year
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0]))),
                  ("K9", trades("v9_RTH")), ("C03", trades("C03"))):
        w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
    one = lambda p, c, n: 1.0
    cases = [("combine set", q)] + [(f"+ Kusho v9 15:45 {k} MNQ", {**q, "K9": float(k)}) for k in (1, 2, 3)] + \
            [(f"+ C03 {k} MNQ", {**q, "C03": float(k)}) for k in (1, 2, 3)] + \
            [(f"VB 8 -> Kusho v9 15:45 {k}", {**{a: b for a, b in q.items() if a != "VB"}, "K9": float(k)}) for k in (4, 8)]
    for nm, qq in cases:
        W = sum(P[x][0] * qq[x] for x in qq); Rr = sum(P[x][1] * qq[x] for x in qq)
        res = [CL.challenge(W, Rr, np.arange(s0, min(s0 + CL.MAXD, D)), one) for s0 in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); n = np.array([x[1] if x else 0 for x in res])
        ps = ok & (o == "pass")
        print(f"   {nm:<28} pass {ps.sum() / ok.sum():5.1%} (18-22 {ps[ok & (yr < 2023)].sum() / (ok & (yr < 2023)).sum():5.1%}, "
              f"23-26 {ps[ok & (yr >= 2023)].sum() / (ok & (yr >= 2023)).sum():5.1%}) | median days to pass {np.median(n[ps]):.0f}")
