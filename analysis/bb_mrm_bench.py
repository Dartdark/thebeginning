"""BB_MRM (analysis/bb_mrm_test.py, exchange clock 08:05-09:20 CT) in the Apex plans.
  A. 50K evaluation: combine set (VB 8 / ONB ADX30 $1,100 / Bridge Monday 2 / EOS $500) + BB_MRM 1-4 MNQ; in place of EOS / Bridge.
  B. 50K funded, bootstrapped (funded_bootstrap, 1,000 paired 2-year histories): plan + 1 / 2 MNQ, longs / shorts; in place of the
     weak slots (EOS, LDF).
  python3 analysis/bb_mrm_bench.py SCRATCH_DIR combine | worker SEED N | merge
"""
import sys, time, pickle, glob, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import funded_bootstrap as FB, combine_levers_test as CL
import bb_mrm_test as T

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "combine"


def bb_trades(g):
    t = T.run(T.load(), count=False)
    ts = t.t.values; row = np.searchsorted(g.ts, t.t.dt.normalize().values); j0 = (t.t.dt.hour * 60 + t.t.dt.minute).values
    t = t.assign(day=row, j0=j0 - 1, j1=np.minimum(j0 + t.bars.values, 1439), kind=np.where(t.kind == "target", 1, 2))
    # net already holds the slippage: give paths() an exit that reproduces it
    t["exit"] = t.entry + t.side * (t.net + T.COMM) / T.PV
    return t


def plans():
    CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2, "RS_L": 1}
    drop = lambda *ks: {k: v for k, v in CUR.items() if k not in ks}
    return {"plan": CUR, "+ BB 1 MNQ": {**CUR, "BB": 1}, "+ BB 2 MNQ": {**CUR, "BB": 2}, "+ BB shorts 1": {**CUR, "BB_S": 1},
            "EOS -> BB 1": {**drop("EOS"), "BB": 1}, "LDF -> BB 1": {**drop("LDF_MC"), "BB": 1}}


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); T0 = time.time()
    if MODE == "combine":
        g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
        yr = pd.DatetimeIndex(g.ts[trr]).year; P = {}
        for nm, tt in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                       ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0]))), ("BB", bb_trades(g))):
            w, r = paths(g, tt); P[nm] = (w[trr] / 10, r[trr] / 10)
        risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
        q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
        one = lambda p, c, n: 1.0; wo = lambda k: {a: b for a, b in q.items() if a != k}
        cases = [("combine set", q)] + [(f"+ BB {k}", {**q, "BB": float(k)}) for k in (1, 2, 3, 4)]
        cases += [(f"EOS -> BB {k}", {**wo("EOS"), "BB": float(k)}) for k in (1, 2, 3)] + [(f"Bridge -> BB {k}", {**wo("MON_BR"), "BB": float(k)}) for k in (1, 2, 3)]
        for nm, qq in cases:
            W = sum(P[x][0] * qq[x] for x in qq); Rr = sum(P[x][1] * qq[x] for x in qq)
            res = [CL.challenge(W, Rr, np.arange(s0, min(s0 + CL.MAXD, D)), one) for s0 in range(D)]
            ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); ps = o == "pass"
            n = np.array([x[1] if x else 0 for x in res])
            print(f"   {nm:<16} pass {ps[ok].mean():5.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, 23-26 {ps[ok & (yr >= 2023)].mean():5.1%}), "
                  f"blown {(o[ok] == 'fail').mean():5.1%}, median days {np.median(n[ok & ps]):.0f}", flush=True)
        sys.exit()
    lab = runpy.run_path("analysis/fc_2b_bench.py", run_name="lib")["fast_plan_lab"](SP); FB.add_moc_mes(lab, SP)
    rs = pd.read_csv(SP + "rs_trades.csv"); rs["kind"] = rs.kind.map({"stop": 0, "target": 1, "flat": 2}); lab.add("RS_L", rs[rs.side > 0].reset_index(drop=True))
    t = bb_trades(lab.g); lab.add("BB", t, slippage=False); lab.add("BB_S", t[t.side < 0].reset_index(drop=True), slippage=False)
    if MODE == "worker":
        seed, n = int(sys.argv[3]), int(sys.argv[4])
        res, y1, _ = FB.Boot(lab).run(plans(), n=n, L=20, seed=seed)
        pickle.dump((res, y1), open(SP + f"bb_boot_{seed}.pkl", "wb")); print(f"[worker {seed} done {time.time() - T0:.0f}s]"); sys.exit()
    parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + "bb_boot_*.pkl"))]
    res = {k: np.concatenate([p[0][k] for p in parts]) for k in plans()}; y1 = {k: np.concatenate([p[1][k] for p in parts]) for k in plans()}
    B = FB.Boot(lab); B.run = lambda *a, **k: (res, y1, 0)
    print(f"\nB. 50K funded, bootstrapped ({len(res['plan'])} paired histories, 20-day blocks, 2 years):")
    df, s_, _ = B.compare(plans()); print(s_)
    print("\n   Daily correlation of BB with the plan pieces:"); print(lab.corr(["BB"] + list(plans()["plan"])).loc["BB"].round(2).to_string())
