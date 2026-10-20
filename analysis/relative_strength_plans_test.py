"""Relative Strength NQ / ES in every Apex plan (user: 'include it in all relevant plans', 2026-10-20).
RS trades = the Python rebuild (analysis/relative_strength_test.py -> SCRATCH/rs_trades.csv), user's settings, in MNQ.
  A. 50K evaluation: current combine set (VB 8, ONB ADX30 $1,100, Bridge Monday 2, EOS $500) + RS 1-4 MNQ, both sides or
     longs only (combine_levers_test.challenge: +$3,000, $2,000 EOD trail, $1,000 daily limit, 21 trading days).
  B. 150K evaluation (account #3): combine set x 2.5 (the 150K setting) + RS 2-8 MNQ (plan_150k_test.evaluation).
  C. 150K funded: current funded plan x 1.5, full size from a $3,000 cushion (the 150K setting) + RS 1-4 MNQ
     (funded_sim150, single history; no bootstrapped 150K bench exists).
  (50K funded: analysis/relative_strength_bench.py, bootstrapped: RS longs 1 MNQ chosen.)
  python3 analysis/relative_strength_plans_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import combine_levers_test as CL, plan_150k_test as P150, funded_bootstrap as FB, funded_sim150 as F150

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
KIND = {"stop": 0, "target": 1, "flat": 2}

if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    yr = pd.DatetimeIndex(g.ts[trr]).year
    rs = pd.read_csv(SP + "rs_trades.csv"); rs["kind"] = rs.kind.map(KIND)
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0]))),
                  ("RS", with_slippage(rs)), ("RS_L", with_slippage(rs[rs.side > 0].reset_index(drop=True)))):
        w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
    Wc = sum(P[k][0] * q[k] for k in q); Rc = sum(P[k][1] * q[k] for k in q)
    one = lambda p, c, n: 1.0

    def ev50(W, R, nm, base=None):
        res = [CL.challenge(W, R, np.arange(s, min(s + CL.MAXD, D)), one) for s in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); ps = o == "pass"
        dd = np.array([x[1] if x else 0 for x in res])
        print(f"   {nm:<34} pass {ps[ok].mean():5.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, 23-26 {ps[ok & (yr >= 2023)].mean():5.1%})"
              f" blown {(o[ok] == 'fail').mean():5.1%} time {(o[ok] == 'time').mean():4.1%} median days {np.median(dd[ok & ps]):.0f}", flush=True)

    def ev150(W, R, nm):
        res = [P150.evaluation(W, R, s, D, P150.R150) for s in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); ps = o == "pass"
        dd = np.array([x[1] if x else 0 for x in res])
        print(f"   {nm:<34} pass {ps[ok].mean():5.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, 23-26 {ps[ok & (yr >= 2023)].mean():5.1%})"
              f" blown {(o[ok] == 'fail').mean():5.1%} time {(o[ok] == 'time').mean():4.1%} median days {np.median(dd[ok & ps]):.0f}", flush=True)

    print("A. 50K evaluation (every start day 2018-26)")
    ev50(Wc, Rc, "combine set (now)")
    for k in ("RS", "RS_L"):
        for n in (1, 2, 3, 4): ev50(Wc + P[k][0] * n, Rc + P[k][1] * n, f"+ {k} {n} MNQ")
    print("\nB. 150K evaluation (combine set x 2.5)")
    ev150(Wc * 2.5, Rc * 2.5, "combine set x 2.5 (now)")
    for k in ("RS", "RS_L"):
        for n in (2, 3, 5, 8): ev150(Wc * 2.5 + P[k][0] * n, Rc * 2.5 + P[k][1] * n, f"+ {k} {n} MNQ")

    print("\nC. 150K funded (current plan x 1.5, full size from a $3,000 cushion; single history)")
    lab = FB.plan_lab(SP); FB.add_moc_mes(lab, SP); lab.add("RS", rs); lab.add("RS_L", rs[rs.side > 0].reset_index(drop=True))
    CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2}
    sc = lambda plan, k: {n: (("risk", v[1] * k) if isinstance(v, tuple) else v * k) for n, v in plan.items()}

    def bench(plan, nm, ref=3000.0):
        names, b = lab._base(plan); W = np.stack([lab.W[k] for k in names]); C = np.stack([lab.C[k] for k in names]); out = []
        for h in (250, 500):
            r = F150.simulate_sized(W, C, b, horizon=h, starts=np.arange(0, lab.D - h), fmin=0.5, fmax=1.0, ref=ref)
            out.append((r["paid"].mean(), r["blown"].mean(), np.mean(r["payouts"] == 6)))
        print(f"   {nm:<34} 1y ${out[0][0]:>7,.0f} blown {out[0][1]:>4.0%} | 2y ${out[1][0]:>7,.0f} blown {out[1][1]:>4.0%} all 6 {out[1][2]:>4.0%}", flush=True)
    base = sc(CUR, 1.5); bench(base, "plan x 1.5 (now)")
    for k in ("RS", "RS_L"):
        for n in (1, 2, 3, 4): bench({**base, k: n}, f"+ {k} {n} MNQ")
