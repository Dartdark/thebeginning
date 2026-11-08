"""Bridge noise-area NQ 15-min (port analysis/bridge_noise_15m_test.py, RTH chart; trades analysis/outputs/
bridge_noise_15m_trades_rth[_longs].csv) in every Apex plan: add or replace. Minute paths from the trades (portfolio.paths:
worst = adverse 1-min extremes, our costs, slippage already in the prices). MNQ = NQ / 10.
  NBL = longs only (the promoted variant), NB = both sides as posted. Overlap: Vault Break (daily corr 0.28) and the day
  breakouts (Dual Thrust on 150K): replacements and their empty slots.
  A. 50K evaluation: combine set + NBL 0-3 / NB 1-2; VB 8 -> NBL 2 / 4 / 6 (and VB empty).
  B. 150K evaluation: x 2.5 (whole contracts) + NBL 0 / 2 / 5; VB 20 -> NBL 5 / 10.
  C. 50K funded, bootstrapped (plan as rollzone_bench): + NBL 1 / 2, + NB 1; VB 2/1 -> 1/1 + NBL 1 (and empty); VB -> NBL 2.
  D. 150K funded, bootstrapped: plan x 1.5 + RS 1 + DT 2 + OT 2, + NBL 1 / 2 / 3; DT 2 -> NBL 2; VB -> NBL 3.
  python3 analysis/bridge_noise_15m_bench.py SCRATCH_DIR [evals | worker50 SEED N | worker150 SEED N | merge]
"""
import sys, glob, time, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "merge"
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import funded_bootstrap as FB, funded_sim150 as F150, funded_sim as F50, combine_levers_test as CL, plan_150k_test as P150
import overnight_tick_bench as OTB, rollzone_bench as RZB

KIND = {"stop": 0, "target": 1}


def nb(longs_only):
    f = "analysis/outputs/bridge_noise_15m_trades_rth" + ("_longs" if longs_only else "") + ".csv"
    t = pd.read_csv(f, parse_dates=["date"]); t = t[t.date >= "2018-01-01"].copy()
    t["day"] = t.row.astype(int); t["kind"] = t.kind.map(KIND).fillna(2).astype(int)
    return t[["day", "j0", "j1", "side", "entry", "exit", "kind"]].reset_index(drop=True)


def add_nb(lab):
    lab.add("NBL", nb(True), slippage=False); lab.add("NB", nb(False), slippage=False)


def plans50():
    p = RZB.plans50(); CUR = p["50K plan"]; drop = lambda *ks: {k: v for k, v in CUR.items() if k not in ks}
    return {"50K plan": CUR, "+ NBL 1 MNQ": {**CUR, "NBL": 1}, "+ NBL 2 MNQ": {**CUR, "NBL": 2}, "+ NB (both) 1 MNQ": {**CUR, "NB": 1},
            "VB 2/1 -> 1/1 + NBL 1": {**CUR, "VB_N": 1, "NBL": 1}, "VB 2/1 -> 1/1 (empty)": {**CUR, "VB_N": 1},
            "VB -> NBL 2": {**drop("VB_N", "VB_F"), "NBL": 2}, "VB empty": drop("VB_N", "VB_F")}


def plans150():
    p = RZB.plans150(); base = p["150K plan"]; drop = lambda *ks: {k: v for k, v in base.items() if k not in ks}
    return {"150K plan": base, "+ NBL 1 MNQ": {**base, "NBL": 1}, "+ NBL 2 MNQ": {**base, "NBL": 2}, "+ NBL 3 MNQ": {**base, "NBL": 3},
            "DT 2 -> NBL 2": {**drop("DT"), "NBL": 2}, "DT empty": drop("DT"),
            "VB -> NBL 3": {**drop("VB_N", "VB_F"), "NBL": 3}, "VB empty": drop("VB_N", "VB_F")}


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); T0 = time.time()
    if MODE == "evals":
        g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
        yr = pd.DatetimeIndex(g.ts[trr]).year; P = {}
        for nm, tt in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                       ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0]))),
                       ("NBL", nb(True)), ("NB", nb(False))):
            w, r = paths(g, tt); P[nm] = (w[trr] / 10, r[trr] / 10)
        risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
        q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
        one = lambda p, c, n: 1.0

        def rep(nm, res):
            ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); ps = o == "pass"
            print(f"   {nm:<30} pass {ps[ok].mean():5.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, 23-26 {ps[ok & (yr >= 2023)].mean():5.1%}), "
                  f"fail {(o == 'fail')[ok].mean():5.1%}", flush=True)
        print("\nA. 50K evaluation (every start day, 2018+):")
        for nm, extra in (("combine set", {}), ("+ NBL 1", {"NBL": 1.0}), ("+ NBL 2", {"NBL": 2.0}), ("+ NBL 3", {"NBL": 3.0}),
                          ("+ NB (both) 1", {"NB": 1.0}), ("+ NB (both) 2", {"NB": 2.0}), ("VB 8 -> NBL 2", {"VB": 0.0, "NBL": 2.0}),
                          ("VB 8 -> NBL 4", {"VB": 0.0, "NBL": 4.0}), ("VB 8 -> NBL 6", {"VB": 0.0, "NBL": 6.0}), ("VB empty", {"VB": 0.0})):
            qq = {**q, **extra}
            Ws = sum(P[x][0] * qq[x] for x in qq); Rs = sum(P[x][1] * qq[x] for x in qq)
            rep(nm, [CL.challenge(Ws, Rs, np.arange(s0, min(s0 + CL.MAXD, D)), one) for s0 in range(D)])
        print("\nB. 150K evaluation (combine set x 2.5, whole contracts):")
        q150 = {"VB": 20.0, "ONB30": risk(2750, 0.25), "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1])}
        for nm, extra in (("x 2.5", {}), ("+ NBL 2", {"NBL": 2.0}), ("+ NBL 5", {"NBL": 5.0}), ("VB 20 -> NBL 5", {"VB": 0.0, "NBL": 5.0}),
                          ("VB 20 -> NBL 10", {"VB": 0.0, "NBL": 10.0}), ("VB empty", {"VB": 0.0})):
            qq = {**q150, **extra}
            Ws = sum(P[x][0] * qq[x] for x in qq); Rs = sum(P[x][1] * qq[x] for x in qq)
            rep(nm, [P150.evaluation(Ws, Rs, s0, D, P150.R150) for s0 in range(D)])
        print(f"[evals done {time.time() - T0:.0f}s]"); sys.exit()
    if MODE == "personal":
        import io, runpy, contextlib, montecarlo as MC, bridge_noise_15m_mc_check as K
        with contextlib.redirect_stdout(io.StringIO()):
            gg = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")
        P, days, ft = gg["P"], gg["days"], gg["from_trades"]; tot = P.sum(axis=1); yrs = len(days) / 252
        A = K.load("RTH Anchor")                                    # MC-confirmed trades (RTH-anchored code), our costs, per NQ
        print(f"\nE. Personal portfolio ({P.shape[1]} pieces at 1 micro), + the MC-confirmed noise 15-min (1 MNQ):")
        print("   corr of the current pieces with NBL:", end=" ")
        o, _ = ft(None, "NBL", A[A.side > 0][["date", "net"]]); ob, _ = ft(None, "NB", A[["date", "net"]])
        print(", ".join(f"{c} {np.corrcoef(o, P[c])[0, 1]:+.2f}" for c in P if abs(np.corrcoef(o, P[c])[0, 1]) >= 0.1))
        rows = [("current", tot), ("+ NBL 1", tot + o), ("+ NBL 2", tot + 2 * o), ("+ NB (both) 1", tot + ob)]
        for c in ("VaultBreak", "DualThrust", "SwingTarget"):
            if c in P: rows.append((f"{c} -> NBL 1", tot - P[c] + o))
        for nm, x in rows:
            d = MC.daily_mc(x.values, horizon=252, n=5000, block=20, trail=1e12); e = x.cumsum()
            print(f"   {nm:<24} ${x.sum() / yrs:>7,.0f} a year, Sharpe {x.mean() / x.std() * np.sqrt(252):.2f}, max DD ${-(e - e.cummax()).min():>6,.0f}, "
                  f"MC p50 ${d['pnl_p50']:>7,.0f}, DD p95 ${d['dd_p95']:>6,.0f}, return/DD {d['ret_dd']:.1f}, capital ${d['dd_p95'] / 0.2:>7,.0f}")
        sys.exit()
    if MODE in ("worker50", "worker150"):
        which = 50 if MODE == "worker50" else 150; seed, n = int(sys.argv[3]), int(sys.argv[4])
        lab = OTB.lab_for(which); RZB.add_rz(lab); add_nb(lab)
        FB.F = F50 if which == 50 else F150
        pl = plans50() if which == 50 else plans150(); kw = {} if which == 50 else dict(ref=3000.0)
        res, y1, _ = FB.Boot(lab).run(pl, n=n, L=20, seed=seed, **kw)
        pickle.dump((res, y1), open(SP + f"nb15_{which}_boot_{seed}.pkl", "wb")); print(f"[{MODE} {seed} done {time.time() - T0:.0f}s]"); sys.exit()
    for which, pl in ((50, plans50()), (150, plans150())):
        parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + f"nb15_{which}_boot_*.pkl"))]
        if not parts: continue
        res = {k: np.concatenate([p[0][k] for p in parts]) for k in pl}; y1 = {k: np.concatenate([p[1][k] for p in parts]) for k in pl}
        B = FB.Boot.__new__(FB.Boot); B.run = lambda *a, **k: (res, y1, 0)
        print(f"\n{'C' if which == 50 else 'D'}. {which}K funded, bootstrapped ({len(res[next(iter(pl))])} paired 2-year histories):")
        df, s_, _ = B.compare(pl); print(s_)
