"""Overnight TickRSV / VIX (rebuild analysis/overnight_tick_test.py, rule with VIX SMA 25; trades end 2026-07-07 with the
order-flow data) in every plan: add or replace. 17:05 -> 03:00 CT = inside one Apex trading day (it starts 17:00 CT), so
Apex-legal; booked on the exit day, worst point = the hold's lowest low applied from the start of that day. MNQ = NQ / 10.
  A. 50K evaluation: combine set + OT 0-3 MNQ; OT in place of Bridge Monday.   B. 150K evaluation: combine x 2.5 + OT 2-8.
  C. 50K funded, bootstrapped (paired 2-year histories): plan + OT 1 / 2; OT in place of the Monday Long.
  D. 150K funded, bootstrapped: plan x 1.5 + RS 1 + DT 2, + OT 1 / 2 / 3.
  E. Personal portfolio (17 pieces at 1 micro): + OT, OT in place of Overnight Anomaly (same idea, unfiltered).
  python3 analysis/overnight_tick_bench.py SCRATCH_DIR [evals | personal | worker50 SEED N | worker150 SEED N | merge]
"""
import sys, io, glob, time, pickle, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import funded_bootstrap as FB, funded_sim150 as F150, funded_sim as F50, combine_levers_test as CL, plan_150k_test as P150
import montecarlo as MC, dual_thrust_bench as DB
from fc_2b_bench import fast_plan_lab, KIND
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "merge"
JX = jof(300)


def ot():
    return pd.read_csv("checks/candidates/overnight_tick/python_trades.csv", parse_dates=["date"]).set_index("date")


def add_ot(lab, t):
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr]); pos = pd.Series(np.arange(len(dates)), index=dates)
    Wd = np.zeros(len(dates)); Cd = np.zeros(len(dates))
    for d, r in t.iterrows():
        if d in pos.index: i = pos[d]; Wd[i] = r.adv; Cd[i] = r.net
    lab.W["OT"] = Wd[:, None] / 10 * np.ones((1, lab.W["VB"].shape[1])); lab.C["OT"] = Cd / 10


def plans50():
    CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2, "RS_L": 1}
    return {"50K plan": CUR, "+ OT 1 MNQ": {**CUR, "OT": 1}, "+ OT 2 MNQ": {**CUR, "OT": 2},
            "Monday Long -> OT 1": {**{k: v for k, v in CUR.items() if k != "MON_MC"}, "OT": 1}}


def plans150():
    CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2}
    base = {**{n: (("risk", v[1] * 1.5) if isinstance(v, tuple) else v * 1.5) for n, v in CUR.items()}, "RS": 1, "DT": 2}
    return {"150K plan": base, "+ OT 1 MNQ": {**base, "OT": 1}, "+ OT 2 MNQ": {**base, "OT": 2}, "+ OT 3 MNQ": {**base, "OT": 3}}


def lab_for(which):
    lab = fast_plan_lab(SP); FB.add_moc_mes(lab, SP)
    rs = pd.read_csv(SP + "rs_trades.csv"); rs["kind"] = rs.kind.map(KIND)
    lab.add("RS_L", rs[rs.side > 0].reset_index(drop=True))
    if which == 150: lab.add("RS", rs); lab.add("DT", DB.dt_trades(lab.g), slippage=False)
    add_ot(lab, ot()); return lab


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); T0 = time.time(); t = ot()
    if MODE == "evals":
        g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
        yr = pd.DatetimeIndex(g.ts[trr]).year; P = {}
        for nm, tt in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                       ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))):
            w, r = paths(g, tt); P[nm] = (w[trr] / 10, r[trr] / 10)
        pos = pd.Series(np.arange(D), index=pd.DatetimeIndex(g.ts[trr])); W = np.zeros((D, 1440)); Rr = np.zeros((D, 1440))
        for d, r in t.iterrows():
            if d in pos.index: i = pos[d]; W[i, :JX + 1] = r.adv / 10; W[i, JX + 1:] = r.net / 10; Rr[i, JX:] = r.net / 10
        P["OT"] = (W, Rr)
        risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
        q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
        one = lambda p, c, n: 1.0
        def rep(nm, res):
            ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); ps = o == "pass"
            print(f"   {nm:<30} pass {ps[ok].mean():5.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, 23-26 {ps[ok & (yr >= 2023)].mean():5.1%}), "
                  f"fail {(o == 'fail')[ok].mean():5.1%}", flush=True)
        print("\nA. 50K evaluation (every start day; OT trades stop 2026-07-07):")
        for nm, qq in [(f"combine set + OT {k} MNQ", {**q, "OT": float(k)}) for k in (0, 1, 2, 3)] + \
                      [(f"Bridge Monday -> OT {k} MNQ", {**q, "MON_BR": 0.0, "OT": float(k)}) for k in (1, 2, 3)]:
            Ws = sum(P[x][0] * qq[x] for x in qq); Rs = sum(P[x][1] * qq[x] for x in qq)
            rep(nm, [CL.challenge(Ws, Rs, np.arange(s0, min(s0 + CL.MAXD, D)), one) for s0 in range(D)])
        print("\nB. 150K evaluation (combine set x 2.5):")
        for k in (0, 2, 3, 5, 8):
            qq = {**{a: b * 2.5 for a, b in q.items()}, "OT": float(k)}
            Ws = sum(P[x][0] * qq[x] for x in qq); Rs = sum(P[x][1] * qq[x] for x in qq)
            rep(f"x 2.5 + OT {k} MNQ", [P150.evaluation(Ws, Rs, s0, D, P150.R150) for s0 in range(D)])
        sys.exit()
    if MODE == "personal":
        with contextlib.redirect_stdout(io.StringIO()):
            g = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")
        P, days, ft = g["P"], g["days"], g["from_trades"]
        o, _ = ft(None, "OT", t.reset_index()[["date", "net"]]); tot = P.sum(axis=1); yrs = len(days) / 252; s30 = P["S30"]
        print(f"\nE. Personal portfolio (1 micro each; OT alone ${o.sum() / yrs:,.0f} a year to 2026-07, corr with the rest "
              f"{np.corrcoef(o, tot)[0, 1]:+.2f}, with Overnight Anomaly {np.corrcoef(o, P['OvernightAnomaly'])[0, 1]:+.2f}):")
        for nm, x in (("17 pieces (now)", tot), ("+ OT", tot + o), ("Overnight Anomaly -> OT", tot - P["OvernightAnomaly"] + o),
                      ("core 16 (no S30)", tot - s30), ("core 16, OA -> OT", tot - s30 - P["OvernightAnomaly"] + o)):
            d = MC.daily_mc(x.values, horizon=252, n=5000, block=20, trail=1e12); e = x.cumsum()
            print(f"   {nm:<26} ${x.sum() / yrs:>7,.0f} a year, Sharpe {x.mean() / x.std() * np.sqrt(252):.2f}, max DD ${-(e - e.cummax()).min():>6,.0f}, "
                  f"MC p50 ${d['pnl_p50']:>7,.0f}, DD p95 ${d['dd_p95']:>6,.0f}, return/DD {d['ret_dd']:.1f}, capital ${d['dd_p95'] / 0.2:>7,.0f}")
        sys.exit()
    if MODE in ("worker50", "worker150"):
        which = 50 if MODE == "worker50" else 150; seed, n = int(sys.argv[3]), int(sys.argv[4])
        lab = lab_for(which); FB.F = F50 if which == 50 else F150
        pl = plans50() if which == 50 else plans150(); kw = {} if which == 50 else dict(ref=3000.0)
        res, y1, _ = FB.Boot(lab).run(pl, n=n, L=20, seed=seed, **kw)
        pickle.dump((res, y1), open(SP + f"ot{which}_boot_{seed}.pkl", "wb")); print(f"[{MODE} {seed} done {time.time() - T0:.0f}s]"); sys.exit()
    for which, pl in ((50, plans50()), (150, plans150())):
        parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + f"ot{which}_boot_*.pkl"))]
        if not parts: continue
        res = {k: np.concatenate([p[0][k] for p in parts]) for k in pl}; y1 = {k: np.concatenate([p[1][k] for p in parts]) for k in pl}
        B = FB.Boot.__new__(FB.Boot); B.run = lambda *a, **k: (res, y1, 0)
        print(f"\n{'C' if which == 50 else 'D'}. {which}K funded, bootstrapped ({len(res[next(iter(pl))])} paired 2-year histories):")
        df, s_, _ = B.compare(pl); print(s_)
