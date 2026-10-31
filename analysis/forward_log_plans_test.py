"""Forward-log strategies in the plans they could join (user, 2026-10-24: 'what would the plan look like with them').
FC 2B v2, S47 v2, Kusho v9 (roll-adjusted; 21:00 with weekend holds = personal only, flat 15:45 = Apex-legal), S30 IBS
(holds days = personal only).
  A. Personal portfolio (analysis/personal_portfolio.py, 14 pieces at 1 micro, FC 2B already one of them): each candidate
     added at 1 micro (FC 2B: removed), then all together; Monte Carlo 1 year, capital at the 20% rule. Kusho / S47 booked
     on their exit day (not marked daily), $0.55 extra micro fee as in the ladder.
  B. 150K funded (plan x 1.5 + RS 1 + Dual Thrust 2, full size from $3,000): + FC 2B / S47 v2 / Kusho v9 15:45 at 1 and
     2 MNQ, and all three at 1; single history (start days from 2018) and bootstrapped 2-year histories (paired).
  python3 analysis/forward_log_plans_test.py SCRATCH_DIR [personal | single | worker SEED N | merge]
"""
import sys, io, glob, pickle, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC, funded_bootstrap as FB, funded_sim150 as F150, dual_thrust_bench as DB

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "personal"


def personal():
    with contextlib.redirect_stdout(io.StringIO()):
        g = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")
    P, days, ft = g["P"].copy(), g["days"], g["from_trades"]
    k21 = pd.read_csv("checks/candidates/kusho/python_trades_v9_rolladj.csv", parse_dates=["date", "exit_date"])
    k15 = pd.read_csv("checks/candidates/kusho/python_trades_v9_RTH_rolladj.csv", parse_dates=["date", "exit_date"])
    s47 = pd.read_csv("checks/candidates/s47_v2/python_trades_v2.csv", parse_dates=["date"])
    s30 = pd.read_csv("checks/candidates/s30_ibs/daily_nq_es_per_micro.csv", index_col=0, parse_dates=True).iloc[:, 0].reindex(days, fill_value=0.0)
    C = {"S47 v2": ft(None, "S47", s47)[0], "Kusho v9 21:00": ft(None, "K21", k21.assign(date=k21.exit_date))[0],
         "Kusho v9 15:45": ft(None, "K15", k15.assign(date=k15.exit_date))[0], "S30 IBS": s30.rename("S30")}
    tot = P.sum(axis=1); yrs = len(days) / 252
    rows = {"full 14 (now)": tot, "  without FC 2B": tot - P["FC2B"]}
    for k, x in C.items(): rows[f"  + {k}"] = tot + x
    rows["+ S47 + Kusho 21:00 + S30"] = tot + C["S47 v2"] + C["Kusho v9 21:00"] + C["S30 IBS"]
    rows["+ S47 + Kusho 15:45 + S30"] = tot + C["S47 v2"] + C["Kusho v9 15:45"] + C["S30 IBS"]
    rows["+ S47 + Kusho 21:00 (no S30)"] = tot + C["S47 v2"] + C["Kusho v9 21:00"]
    print("\nA. Personal portfolio, every piece at 1 micro (2018-01 -> 2026-10):")
    for k, x in C.items():
        print(f"   {k:<16} alone ${x.sum() / yrs:,.0f} a year, corr with the 14 {np.corrcoef(x, tot)[0, 1]:+.2f}")
    for nm, x in rows.items():
        d = MC.daily_mc(x.values, horizon=252, n=5000, block=20, trail=1e12); e = x.cumsum()
        print(f"   {nm:<30} ${x.sum() / yrs:>7,.0f} a year, Sharpe {x.mean() / x.std() * np.sqrt(252):.2f}, max DD ${-(e - e.cummax()).min():>6,.0f}, "
              f"MC p50 ${d['pnl_p50']:>7,.0f} / p5 ${d['pnl_p5']:>7,.0f}, DD p95 ${d['dd_p95']:>6,.0f}, return/DD {d['ret_dd']:.1f}, capital ${d['dd_p95'] / 0.2:>7,.0f}")


def lab150():
    rw = runpy.run_path("analysis/replace_weak_bench.py", run_name="lib")
    lab = runpy.run_path("analysis/fc_2b_bench.py", run_name="lib")["fast_plan_lab"](SP); FB.add_moc_mes(lab, SP)
    rs = pd.read_csv(SP + "rs_trades.csv"); rs["kind"] = rs.kind.map({"stop": 0, "target": 1, "flat": 2}); lab.add("RS", rs)
    lab.add("DT", DB.dt_trades(lab.g), slippage=False)
    c = rw["candidates"](lab.g)
    k15 = runpy.run_path("analysis/kusho_bench.py", run_name="lib")["trades"]("v9_RTH_rolladj", lab.g)
    for k, t in (("FC", c["FC"]), ("S47", c["S47"]), ("K15", k15)): lab.add(k, t, slippage=False)
    CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2}
    base = {**{n: (("risk", v[1] * 1.5) if isinstance(v, tuple) else v * 1.5) for n, v in CUR.items()}, "RS": 1, "DT": 2}
    plans = {"150K plan (now, with DT 2)": base}
    for k, nm in (("FC", "FC 2B"), ("S47", "S47 v2"), ("K15", "Kusho v9 15:45")):
        for n in (1, 2): plans[f"+ {nm} {n} MNQ"] = {**base, k: n}
    plans["+ all three at 1 MNQ"] = {**base, "FC": 1, "S47": 1, "K15": 1}
    return lab, plans


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    if MODE == "personal": personal(); sys.exit()
    lab, plans = lab150()
    if MODE == "single":
        print("\nB1. 150K funded, single history (start days from 2018, full size from a $3,000 cushion):")
        s18 = int(np.searchsorted(pd.DatetimeIndex(lab.g.ts[lab.tr]), pd.Timestamp("2018-01-01")))
        for nm, plan in plans.items():
            names, b = lab._base(plan); W = np.stack([lab.W[k] for k in names]); C = np.stack([lab.C[k] for k in names]); out = []
            for h in (250, 500):
                r = F150.simulate_sized(W, C, b, horizon=h, starts=np.arange(s18, lab.D - h), fmin=0.5, fmax=1.0, ref=3000.0)
                d6 = np.where(r["payouts"] == 6, r["days"], np.inf); out.append((r["paid"].mean(), r["blown"].mean(), np.median(d6)))
            print(f"   {nm:<28} 1y ${out[0][0]:>7,.0f} | 2y ${out[1][0]:>7,.0f} blown {out[1][1]:>4.1%} | 6th payout day {out[1][2]:.0f}", flush=True)
        sys.exit()
    FB.F = F150
    if MODE == "worker":
        seed, n = int(sys.argv[3]), int(sys.argv[4])
        res, y1, _ = FB.Boot(lab).run(plans, n=n, L=20, seed=seed, ref=3000.0)
        pickle.dump((res, y1), open(SP + f"fl150_boot_{seed}.pkl", "wb")); sys.exit()
    parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + "fl150_boot_*.pkl"))]
    res = {k: np.concatenate([p[0][k] for p in parts]) for k in plans}; y1 = {k: np.concatenate([p[1][k] for p in parts]) for k in plans}
    B = FB.Boot(lab); B.run = lambda *a, **k: (res, y1, 0)
    print(f"\nB2. 150K funded, bootstrapped ({len(res[next(iter(plans))])} paired 2-year histories, 20-day blocks, full size from $3,000):")
    df, s_, _ = B.compare(plans); print(s_)
    print("   (the 150K ladder pays at most $20,500 per account)")
