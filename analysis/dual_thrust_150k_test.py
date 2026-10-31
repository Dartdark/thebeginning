"""Dual Thrust v4 on the Apex 150K accounts (user, 2026-10-24: 'how would it improve 150k account').
DT trades = analysis/dual_thrust_test.py rebuild (v4 as coded, $7.25 + 1 tick per market / stop fill), in MNQ.
  A. 150K evaluation (account #3, combine set x 2.5; plan_150k_test.evaluation: +$9,000, $4,000 EOD trail, $2,000 daily
     pause, 30 days) + DT 2-8 MNQ (both / longs / shorts); DT in place of part of VB.
  B. 150K funded, single history (funded_sim150, every start day; the setting used for the 150K plan): plan x 1.5 + RS both
     sides 1 MNQ, full size from a $3,000 cushion; + DT 1-4 MNQ (both / longs / shorts), DT in place of RS, VB 3/1.5 -> 2/1.5.
  C. 150K funded, bootstrapped (funded_bootstrap.Boot with the 150K simulator, 2-year histories, 20-day blocks, paired).
  python3 analysis/dual_thrust_150k_test.py SCRATCH_DIR [N_BOOT]
"""
import sys, pickle, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import combine_levers_test as CL, plan_150k_test as P150, funded_bootstrap as FB, funded_sim150 as F150
import dual_thrust_bench as DB

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
NB = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 500
KIND = {"stop": 0, "target": 1, "flat": 2}

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    yr = pd.DatetimeIndex(g.ts[trr]).year
    dt = DB.dt_trades(g)
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0]))),
                  ("DT", dt), ("DT_L", dt[dt.side > 0].reset_index(drop=True)), ("DT_S", dt[dt.side < 0].reset_index(drop=True))):
        w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}

    def ev150(qq, nm):
        W = sum(P[k][0] * v for k, v in qq.items()); R = sum(P[k][1] * v for k, v in qq.items())
        res = [P150.evaluation(W, R, s, D, P150.R150) for s in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); ps = o == "pass"
        dd = np.array([x[1] if x else 0 for x in res])
        print(f"   {nm:<30} pass {ps[ok].mean():5.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, 23-26 {ps[ok & (yr >= 2023)].mean():5.1%})"
              f" blown {(o[ok] == 'fail').mean():5.1%} time {(o[ok] == 'time').mean():4.1%} median days {np.median(dd[ok & ps]):.0f}", flush=True)

    print("\nA. 150K evaluation (combine set x 2.5, every start day 2018-26)")
    q25 = {k: v * 2.5 for k, v in q.items()}
    ev150(q25, "combine set x 2.5 (now)")
    for k in ("DT", "DT_L", "DT_S"):
        for n in (2, 3, 5, 8): ev150({**q25, k: float(n)}, f"+ {k} {n} MNQ")
    for vb, n in ((15, 5), (10, 10), (10, 5)): ev150({**q25, "VB": float(vb), "DT": float(n)}, f"VB {vb} + DT {n} MNQ")

    print("\nB. 150K funded (plan x 1.5 + RS 1 MNQ, full size from a $3,000 cushion; single history, every start day)")
    lab = runpy.run_path("analysis/fc_2b_bench.py", run_name="lib")["fast_plan_lab"](SP); FB.add_moc_mes(lab, SP)
    rs = pd.read_csv(SP + "rs_trades.csv"); rs["kind"] = rs.kind.map(KIND); lab.add("RS", rs)
    lab.add("DT", dt, slippage=False); lab.add("DT_L", dt[dt.side > 0].reset_index(drop=True), slippage=False)
    lab.add("DT_S", dt[dt.side < 0].reset_index(drop=True), slippage=False)
    CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2}
    sc = lambda plan, k: {n: (("risk", v[1] * k) if isinstance(v, tuple) else v * k) for n, v in plan.items()}
    base = {**sc(CUR, 1.5), "RS": 1}
    plans = {"150K plan (now)": base}
    for k in ("DT", "DT_L", "DT_S"):
        for n in (1, 2, 3, 4): plans[f"+ {k} {n} MNQ"] = {**base, k: n}
    plans["RS -> DT 1"] = {**{a: b for a, b in base.items() if a != "RS"}, "DT": 1}
    plans["RS -> DT 2"] = {**{a: b for a, b in base.items() if a != "RS"}, "DT": 2}
    plans["VB_N 3 -> 2 + DT 1"] = {**base, "VB_N": 2.0, "DT": 1}
    plans["VB_N 3 -> 2 + DT 2"] = {**base, "VB_N": 2.0, "DT": 2}
    s18 = int(np.searchsorted(pd.DatetimeIndex(lab.g.ts[lab.tr]), pd.Timestamp("2018-01-01")))
    for nm, plan in plans.items():
        names, b = lab._base(plan); W = np.stack([lab.W[k] for k in names]); C = np.stack([lab.C[k] for k in names]); out = []
        for h in (250, 500):
            st = np.arange(s18, lab.D - h)      # start days from 2018 (2017 rows have almost no trades; the plan doc's setting)
            r = F150.simulate_sized(W, C, b, horizon=h, starts=st, fmin=0.5, fmax=1.0, ref=3000.0)
            f = r["first"][r["first"] > 0]; d6 = np.where(r["payouts"] == 6, r["days"], np.inf)
            out.append((r["paid"].mean(), r["blown"].mean(), np.mean(r["payouts"] == 6), np.median(f) if len(f) else np.nan, np.median(d6)))
        print(f"   {nm:<24} 1y ${out[0][0]:>7,.0f} blown {out[0][1]:>4.1%} | 2y ${out[1][0]:>7,.0f} blown {out[1][1]:>4.1%} "
              f"all 6 {out[1][2]:>4.0%} | days to 1st payout {out[1][3]:.0f}, to 6th {out[1][4]:.0f}", flush=True)

    if "--no-boot" in sys.argv: sys.exit()
    print(f"\nC. 150K funded, bootstrapped ({NB} paired 2-year histories, 20-day blocks, full size from $3,000):")
    FB.F = F150                                                    # Boot.run calls F.simulate_sized
    pick = ["150K plan (now)", "+ DT 1 MNQ", "+ DT 2 MNQ", "+ DT_S 1 MNQ", "RS -> DT 1", "VB_N 3 -> 2 + DT 1"]
    df, s_, _ = FB.Boot(lab).compare({k: plans[k] for k in pick}, n=NB, L=20, seed=1, ref=3000.0); print(s_)
    print("   (the 150K ladder pays at most $20,500 per account)")
