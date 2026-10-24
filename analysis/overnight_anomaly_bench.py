"""OvernightAnomaly v4.1 (Block B of the user's merged file, 2026-10-24) in the Apex plans: add or replace.
Trades = analysis/overnight_anomaly_test.py's rebuild (17:30 -> 02:30 CT, after a down RTH session), booked on the exit day
(the Apex trading day starting 17:00 CT); worst point = the hold's lowest low (applied from the start of that day). MNQ = NQ / 10.
  A. 50K funded, bootstrapped bench (funded_bootstrap, 1,000 paired 2-year histories, 20-day blocks): current plan
     + OA 1 / 2 MNQ; OA in place of the Monday Long (the plan's other overnight-into-the-day long).
  B. 50K evaluation: combine set (VB 8, ONB ADX30 $1,100, Bridge Monday 2, EOS $500) + OA 0-3 MNQ; OA in place of Bridge Monday.
  python3 analysis/overnight_anomaly_bench.py SCRATCH_DIR [worker SEED N | merge | combine]
  (needs overnight_anomaly_nights.csv from the test, plus what fc_2b_bench.py needs)
"""
import sys, time, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import funded_bootstrap as FB, combine_levers_test as CL
from fc_2b_bench import fast_plan_lab, KIND
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "merge"


def oa_trades(sp):
    N = pd.read_csv(sp + "overnight_anomaly_nights.csv", parse_dates=["date"])
    return N[N.down & ~N.half].set_index("date")


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); T0 = time.time(); t = oa_trades(SP)
    if MODE != "combine":
        lab = fast_plan_lab(SP); print(f"[plan lab {time.time() - T0:.0f}s]"); FB.add_moc_mes(lab, SP)
        rs = pd.read_csv(SP + "rs_trades.csv"); rs["kind"] = rs.kind.map(KIND)
        lab.add("RS_L", rs[rs.side > 0].reset_index(drop=True))
        dates = pd.DatetimeIndex(lab.g.ts[lab.tr]); pos = pd.Series(np.arange(len(dates)), index=dates)
        Wd = np.zeros(len(dates)); Cd = np.zeros(len(dates)); miss = 0
        for d, r in t.iterrows():
            if d in pos.index: i = pos[d]; Wd[i] = r.adv; Cd[i] = r.net
            else: miss += 1
        print(f"OA trades {len(t)}, not on a plan trading day {miss}")
        lab.W["OA"] = Wd[:, None] / 10 * np.ones((1, lab.W["VB"].shape[1])); lab.C["OA"] = Cd / 10
        CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2, "RS_L": 1}
        drop = lambda *ks: {k: v for k, v in CUR.items() if k not in ks}
        plans = {"plan": CUR, "+ OA 1 MNQ": {**CUR, "OA": 1}, "+ OA 2 MNQ": {**CUR, "OA": 2},
                 "Monday Long -> OA 1": {**drop("MON_MC"), "OA": 1}, "Monday Long -> OA 2": {**drop("MON_MC"), "OA": 2}}
        if MODE == "worker":
            seed, n = int(sys.argv[3]), int(sys.argv[4])
            res, y1, _ = FB.Boot(lab).run(plans, n=n, L=20, seed=seed)
            pickle.dump((res, y1), open(SP + f"oa_boot_{seed}.pkl", "wb")); print(f"[worker {seed} done {time.time() - T0:.0f}s]"); sys.exit()
        import glob
        parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + "oa_boot_*.pkl"))]
        res = {k: np.concatenate([p[0][k] for p in parts]) for k in plans}; y1 = {k: np.concatenate([p[1][k] for p in parts]) for k in plans}
        B = FB.Boot(lab); B.run = lambda *a, **k: (res, y1, 0)
        print(f"\nA. 50K funded, bootstrapped ({len(res['plan'])} paired histories from {len(parts)} workers, 20-day blocks, 2 years):")
        df, s_, _ = B.compare(plans); print(s_)
        print("\n   Daily correlation of OA with the plan pieces:")
        print(lab.corr(["OA"] + list(CUR)).loc["OA"].round(2).to_string())
        sys.exit()
    print("\nB. 50K evaluation (combine set + OA):")
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    yr = pd.DatetimeIndex(g.ts[trr]).year
    P = {}
    for nm, tt in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                   ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))):
        w, r = paths(g, tt); P[nm] = (w[trr] / 10, r[trr] / 10)
    pos = pd.Series(np.arange(D), index=pd.DatetimeIndex(g.ts[trr])); W = np.zeros((D, 1440)); Rr = np.zeros((D, 1440)); jx = jof(230)
    for d, r in t.iterrows():
        if d in pos.index:
            i = pos[d]; W[i, :jx + 1] = r.adv / 10; W[i, jx + 1:] = r.net / 10; Rr[i, jx:] = r.net / 10
    P["OA"] = (W, Rr)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
    one = lambda p, c, n: 1.0
    for nm, qq in [(f"combine set + OA {k} MNQ", {**q, "OA": float(k)}) for k in (0, 1, 2, 3)] + \
                  [(f"Bridge Monday -> OA {k} MNQ", {**q, "MON_BR": 0.0, "OA": float(k)}) for k in (1, 2)]:
        Ws = sum(P[x][0] * qq[x] for x in qq); Rs = sum(P[x][1] * qq[x] for x in qq)
        res = [CL.challenge(Ws, Rs, np.arange(s0, min(s0 + CL.MAXD, D)), one) for s0 in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); ps = o == "pass"
        nd = np.array([x[1] if x else 0 for x in res])
        print(f"   {nm:<28} pass {ps[ok].mean():5.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, 23-26 {ps[ok & (yr >= 2023)].mean():5.1%}), "
              f"fail {(o == 'fail')[ok].mean():5.1%}, median days to pass {np.median(nd[ok & ps]):.0f}")
