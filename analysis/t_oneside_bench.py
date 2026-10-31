"""T_ONESIDE (user's upload 2026-10-24) in the Apex plans: add or replace.
Trades = analysis/t_oneside_test.py's rebuild WITH the note's stop (0.40 / 0.30 x ATRd; the file itself has none), raw prices,
our costs ($7.25 + 1 tick per market / stop fill via funded_lab), MNQ = NQ / 10. Book = T fade (heavy nights, 08:29 -> 08:44 CT)
+ OS long (other nights, 09:59 -> 10:59 CT), one trade a day.
  A. 50K funded, bootstrapped bench (funded_bootstrap, 1,000 paired 2-year histories, 20-day blocks): current plan
     + book 1 / 2 MNQ, + T only 1 / 2 MNQ; the book in place of ONB ML (the morning-bias piece it overlaps most).
  B. 50K evaluation: combine set (VB 8, ONB ADX30 $1,100, Bridge Monday 2, EOS $500) + book / T 1-4 MNQ; in place of EOS
     and of ONB ADX30.
  python3 analysis/t_oneside_bench.py SCRATCH_DIR [worker SEED N | merge | combine]
  (needs t_oneside_stop.csv from the test, plus what fc_2b_bench.py needs)
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


def load(sp):
    t = pd.read_csv(sp + "t_oneside_stop.csv", parse_dates=["date"])
    t = t[t.date >= "2018-01-01"].reset_index(drop=True)
    return t[["day", "j0", "j1", "side", "entry", "exit", "kind", "cell"]]


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); T0 = time.time(); t = load(SP); tT = t[t.cell == "T"].reset_index(drop=True)
    print(f"trades {len(t)} (T {len(tT)})")
    if MODE != "combine":
        lab = fast_plan_lab(SP); print(f"[plan lab {time.time() - T0:.0f}s]"); FB.add_moc_mes(lab, SP)
        rs = pd.read_csv(SP + "rs_trades.csv"); rs["kind"] = rs.kind.map(KIND)
        lab.add("RS_L", rs[rs.side > 0].reset_index(drop=True))
        lab.add("TOS", t); lab.add("TOS_T", tT)
        CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2, "RS_L": 1}
        drop = lambda *ks: {k: v for k, v in CUR.items() if k not in ks}
        plans = {"plan": CUR, "+ book 1 MNQ": {**CUR, "TOS": 1}, "+ book 2 MNQ": {**CUR, "TOS": 2},
                 "+ T only 1 MNQ": {**CUR, "TOS_T": 1}, "+ T only 2 MNQ": {**CUR, "TOS_T": 2},
                 "ONB ML -> book 2 MNQ": {**drop("ONB_ML2_MC"), "TOS": 2}}
        if MODE == "worker":
            seed, n = int(sys.argv[3]), int(sys.argv[4])
            res, y1, _ = FB.Boot(lab).run(plans, n=n, L=20, seed=seed)
            pickle.dump((res, y1), open(SP + f"tos_boot_{seed}.pkl", "wb")); print(f"[worker {seed} done {time.time() - T0:.0f}s]"); sys.exit()
        import glob
        parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + "tos_boot_*.pkl"))]
        res = {k: np.concatenate([p[0][k] for p in parts]) for k in plans}; y1 = {k: np.concatenate([p[1][k] for p in parts]) for k in plans}
        B = FB.Boot(lab); B.run = lambda *a, **k: (res, y1, 0)
        print(f"\nA. 50K funded, bootstrapped ({len(res['plan'])} paired histories from {len(parts)} workers, 20-day blocks, 2 years):")
        df, s_, _ = B.compare(plans); print(s_)
        print("\n   Daily correlation of the book with the plan pieces:")
        print(lab.corr(["TOS"] + list(CUR)).loc["TOS"].round(2).to_string())
        sys.exit()
    print("\nB. 50K evaluation (combine set + T_ONESIDE):")
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    yr = pd.DatetimeIndex(g.ts[trr]).year
    P = {}
    for nm, tt in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                   ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0]))),
                   ("TOS", with_slippage(t)), ("TOS_T", with_slippage(tT))):
        w, r = paths(g, tt); P[nm] = (w[trr] / 10, r[trr] / 10)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
    one = lambda p, c, n: 1.0
    cases = [(f"combine set + book {k} MNQ", {**q, "TOS": float(k)}) for k in (0, 1, 2, 3, 4)] + \
            [(f"combine set + T only {k} MNQ", {**q, "TOS_T": float(k)}) for k in (1, 2, 3, 4)] + \
            [(f"EOS -> book {k} MNQ", {**q, "EOS": 0.0, "TOS": float(k)}) for k in (2, 3)] + \
            [(f"ONB ADX30 -> book {k} MNQ", {**q, "ONB30": 0.0, "TOS": float(k)}) for k in (3, 4, 6)]
    for nm, qq in cases:
        Ws = sum(P[x][0] * qq[x] for x in qq); Rs = sum(P[x][1] * qq[x] for x in qq)
        res = [CL.challenge(Ws, Rs, np.arange(s0, min(s0 + CL.MAXD, D)), one) for s0 in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); ps = o == "pass"
        nd = np.array([x[1] if x else 0 for x in res])
        print(f"   {nm:<30} pass {ps[ok].mean():5.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, 23-26 {ps[ok & (yr >= 2023)].mean():5.1%}), "
              f"fail {(o == 'fail')[ok].mean():5.1%}, median days to pass {np.median(nd[ok & ps]):.0f}")
