"""Dual Thrust v4 (user's file, 2026-10-24; rebuild analysis/dual_thrust_test.py) in the Apex plans: add or replace.
  A. 50K funded, bootstrapped bench (funded_bootstrap, 1,000 paired 2-year histories, 20-day blocks, seeds 1-4 x 250 = the
     FC 2B / replace-weak benches' histories): current plan + DT 1 MNQ (both sides / longs / shorts); DT in place of the
     piece it overlaps most (RS longs, corr +0.21; VB, +0.16: VB_N 2 -> 1) and of the weak slots EOS / LDF.
  B. 50K evaluation: combine set (VB 8, ONB ADX30 $1,100, Bridge Monday 2, EOS $500) + DT 1-3 MNQ; DT in place of EOS /
     Bridge (1-3 MNQ) and of VB (4 / 6 / 8 MNQ) (combine_levers_test.challenge).
  python3 analysis/dual_thrust_bench.py SCRATCH_DIR worker SEED N | merge | combine
"""
import sys, time, pickle, glob, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import funded_bootstrap as FB, combine_levers_test as CL
import dual_thrust_test as DT

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "merge"


def dt_trades(g):
    days = DT.load(); t = DT.run(days, DT.setups(days)); x = DT.lab_trades(g, t)
    assert x.day.notna().all(); x["day"] = x.day.astype(int)
    return with_slippage(x)


def plans():
    CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2, "RS_L": 1}
    drop = lambda *ks: {k: v for k, v in CUR.items() if k not in ks}
    return {"plan": CUR, "+ DT 1 MNQ": {**CUR, "DT": 1}, "+ DT longs 1": {**CUR, "DT_L": 1}, "+ DT shorts 1": {**CUR, "DT_S": 1},
            "RS longs -> DT 1": {**drop("RS_L"), "DT": 1}, "VB 2/1 -> 1/1 + DT 1": {**CUR, "VB_N": 1, "DT": 1},
            "EOS -> DT 1": {**drop("EOS"), "DT": 1}, "LDF -> DT 1": {**drop("LDF_MC"), "DT": 1}}


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); T0 = time.time()
    if MODE in ("worker", "merge"):
        lab = runpy.run_path("analysis/fc_2b_bench.py", run_name="lib")["fast_plan_lab"](SP); FB.add_moc_mes(lab, SP)
        rs = pd.read_csv(SP + "rs_trades.csv"); rs["kind"] = rs.kind.map({"stop": 0, "target": 1, "flat": 2})
        lab.add("RS_L", rs[rs.side > 0].reset_index(drop=True))
        t = dt_trades(lab.g)
        lab.add("DT", t, slippage=False); lab.add("DT_L", t[t.side > 0].reset_index(drop=True), slippage=False)
        lab.add("DT_S", t[t.side < 0].reset_index(drop=True), slippage=False)
        print(f"[DT trades {len(t)}, ${lab.C['DT'].sum() * 10 / len(t):.0f} per NQ in the lab]")
    if MODE == "worker":
        seed, n = int(sys.argv[3]), int(sys.argv[4])
        res, y1, _ = FB.Boot(lab).run(plans(), n=n, L=20, seed=seed)
        pickle.dump((res, y1), open(SP + f"dt_boot_{seed}.pkl", "wb")); print(f"[worker {seed} done {time.time() - T0:.0f}s]"); sys.exit()
    if MODE == "merge":
        parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + "dt_boot_*.pkl"))]
        res = {k: np.concatenate([p[0][k] for p in parts]) for k in plans()}; y1 = {k: np.concatenate([p[1][k] for p in parts]) for k in plans()}
        B = FB.Boot(lab); B.run = lambda *a, **k: (res, y1, 0)
        print(f"\nA. 50K funded, bootstrapped ({len(res['plan'])} paired histories from {len(parts)} workers, 20-day blocks, 2 years):")
        df, s_, _ = B.compare(plans()); print(s_)
        print("\n   Daily correlation of DT with the plan pieces:")
        print(lab.corr(["DT"] + list(plans()["plan"])).loc["DT"].round(2).to_string())
        sys.exit()
    print("\nB. 50K evaluation:")
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    yr = pd.DatetimeIndex(g.ts[trr]).year
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0]))), ("DT", dt_trades(g))):
        w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
    one = lambda p, c, n: 1.0
    wo = lambda k: {a: b for a, b in q.items() if a != k}
    cases = [("combine set", q)] + [(f"+ DT {k}", {**q, "DT": float(k)}) for k in (1, 2, 3)]
    cases += [(f"EOS -> DT {k}", {**wo("EOS"), "DT": float(k)}) for k in (1, 2, 3)]
    cases += [(f"Bridge -> DT {k}", {**wo("MON_BR"), "DT": float(k)}) for k in (1, 2, 3)]
    cases += [(f"VB -> DT {k}", {**wo("VB"), "DT": float(k)}) for k in (4, 6, 8)]
    cases += [(f"VB 4 + DT {k}", {**q, "VB": 4.0, "DT": float(k)}) for k in (2, 4)]
    for nm, qq in cases:
        W = sum(P[x][0] * qq[x] for x in qq); Rr = sum(P[x][1] * qq[x] for x in qq)
        res = [CL.challenge(W, Rr, np.arange(s0, min(s0 + CL.MAXD, D)), one) for s0 in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); ps = o == "pass"
        n = np.array([x[1] if x else 0 for x in res])
        print(f"   {nm:<22} pass {ps[ok].mean():5.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, 23-26 {ps[ok & (yr >= 2023)].mean():5.1%}), "
              f"blown {(o[ok] == 'fail').mean():5.1%}, median days {np.median(n[ok & ps]):.0f}", flush=True)
