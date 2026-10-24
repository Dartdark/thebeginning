"""PAPERTREND v2 (rebuild analysis/papertrend_test.py, with a 2 x ATR disaster stop: same P&L as no stop, bounded risk) in
every plan: add or replace. Intraday 08:46 -> 14:55 CT, so Apex-legal. MNQ = NQ / 10.
  A. 50K evaluation: combine set + PT 0-3 MNQ; PT in place of Bridge Monday.   B. 150K evaluation: combine x 2.5 + PT 0-5.
  C. 50K funded, bootstrapped (paired 2-year histories): plan (with OT in place of the Monday Long) + PT 1; PT in place of
     RS longs / EOS / one VB contract.
  D. 150K funded, bootstrapped: plan x 1.5 + RS 1 + DT 2 + OT 2, + PT 1 / 2; PT in place of Dual Thrust (the closest rule).
  E. Personal portfolio (17 pieces at 1 micro): + PT, PT in place of Dual Thrust.
  python3 analysis/papertrend_bench.py SCRATCH_DIR [evals | personal | worker50 SEED N | worker150 SEED N | merge]
"""
import sys, io, glob, time, pickle, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "merge"
ARGS = list(sys.argv)
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import funded_bootstrap as FB, funded_sim150 as F150, funded_sim as F50, combine_levers_test as CL, plan_150k_test as P150
import montecarlo as MC
import overnight_tick_bench as OTB
sys.argv = [ARGS[0], SP]
import papertrend_test as PTT
sys.argv = ARGS


def pt_trades(g):
    """Lab-format trades on grid g (rows placed by date), raw entry / exit (with_slippage adds the 2 ticks)."""
    t = PTT.run(PTT.Days("NQ"), stop_atr=2.0, count=False)
    row = pd.Series(np.arange(len(g.ts)), index=pd.DatetimeIndex(g.ts))
    x = pd.DataFrame(dict(day=row.reindex(t.index).to_numpy(), j0=t.sig.to_numpy() + 1, j1=t.j1.to_numpy(), side=t.side.to_numpy(),
                          entry=t.entry.to_numpy(), exit=t.exit.to_numpy(), kind=t.kind.to_numpy(), date=t.index, net=t.net.to_numpy()))
    x = x[x.day.notna()].reset_index(drop=True); x["day"] = x.day.astype(int)
    return x[x.date >= "2018-01-01"].reset_index(drop=True)


def plans50():
    CUR = {**{k: v for k, v in FB.PLAN.items() if k != "MON_MC"}, "VB_N": 2, "MOC_MES": 2, "RS_L": 1, "OT": 1}
    drop = lambda *ks: {k: v for k, v in CUR.items() if k not in ks}
    return {"50K plan": CUR, "+ PT 1 MNQ": {**CUR, "PT": 1}, "RS longs -> PT 1": {**drop("RS_L"), "PT": 1},
            "EOS -> PT 1": {**drop("EOS"), "PT": 1}, "VB 2/1 -> 1/1 + PT 1": {**CUR, "VB_N": 1, "PT": 1}}


def plans150():
    CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2}
    base = {**{n: (("risk", v[1] * 1.5) if isinstance(v, tuple) else v * 1.5) for n, v in CUR.items()}, "RS": 1, "DT": 2, "OT": 2}
    nodt = {k: v for k, v in base.items() if k != "DT"}
    return {"150K plan": base, "+ PT 1 MNQ": {**base, "PT": 1}, "+ PT 2 MNQ": {**base, "PT": 2},
            "DT 2 -> PT 2": {**nodt, "PT": 2}, "DT 2 -> DT 1 + PT 1": {**base, "DT": 1, "PT": 1}}


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); T0 = time.time()
    if MODE == "evals":
        g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
        yr = pd.DatetimeIndex(g.ts[trr]).year; P = {}
        for nm, tt in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                       ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0]))),
                       ("PT", with_slippage(pt_trades(g)))):
            w, r = paths(g, tt); P[nm] = (w[trr] / 10, r[trr] / 10)
        risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
        q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
        one = lambda p, c, n: 1.0
        def rep(nm, res):
            ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); ps = o == "pass"
            print(f"   {nm:<30} pass {ps[ok].mean():5.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, 23-26 {ps[ok & (yr >= 2023)].mean():5.1%}), "
                  f"fail {(o == 'fail')[ok].mean():5.1%}", flush=True)
        print("\nA. 50K evaluation (every start day):")
        for nm, qq in [(f"combine set + PT {k} MNQ", {**q, "PT": float(k)}) for k in (0, 1, 2, 3)] + \
                      [(f"Bridge Monday -> PT {k} MNQ", {**q, "MON_BR": 0.0, "PT": float(k)}) for k in (1, 2)] + \
                      [(f"VB 8 -> 6 + PT {k} MNQ", {**q, "VB": 6.0, "PT": float(k)}) for k in (1, 2)]:
            Ws = sum(P[x][0] * qq[x] for x in qq); Rs = sum(P[x][1] * qq[x] for x in qq)
            rep(nm, [CL.challenge(Ws, Rs, np.arange(s0, min(s0 + CL.MAXD, D)), one) for s0 in range(D)])
        print("\nB. 150K evaluation (combine set x 2.5):")
        for k in (0, 1, 2, 3, 5):
            qq = {**{a: b * 2.5 for a, b in q.items()}, "PT": float(k)}
            Ws = sum(P[x][0] * qq[x] for x in qq); Rs = sum(P[x][1] * qq[x] for x in qq)
            rep(f"x 2.5 + PT {k} MNQ", [P150.evaluation(Ws, Rs, s0, D, P150.R150) for s0 in range(D)])
        sys.exit()
    if MODE == "personal":
        with contextlib.redirect_stdout(io.StringIO()):
            gg = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")
        P, days, ft = gg["P"], gg["days"], gg["from_trades"]
        g = pickle.load(open(SP + "g24.pkl", "rb")); t = pt_trades(g)
        o, _ = ft(None, "PT", t[["date", "net"]]); tot = P.sum(axis=1); yrs = len(days) / 252; dt = P["DualThrust"]
        print(f"\nE. Personal portfolio (1 micro each; PT alone ${o.sum() / yrs:,.0f} a year, corr with the rest {np.corrcoef(o, tot)[0, 1]:+.2f}, "
              f"with Dual Thrust {np.corrcoef(o, dt)[0, 1]:+.2f}):")
        for nm, x in (("17 pieces (now)", tot), ("+ PT", tot + o), ("Dual Thrust -> PT", tot - dt + o), ("+ PT x 2", tot + 2 * o)):
            d = MC.daily_mc(x.values, horizon=252, n=5000, block=20, trail=1e12); e = x.cumsum()
            print(f"   {nm:<26} ${x.sum() / yrs:>7,.0f} a year, Sharpe {x.mean() / x.std() * np.sqrt(252):.2f}, max DD ${-(e - e.cummax()).min():>6,.0f}, "
                  f"MC p50 ${d['pnl_p50']:>7,.0f}, DD p95 ${d['dd_p95']:>6,.0f}, return/DD {d['ret_dd']:.1f}, capital ${d['dd_p95'] / 0.2:>7,.0f}")
        sys.exit()
    if MODE in ("worker50", "worker150"):
        which = 50 if MODE == "worker50" else 150; seed, n = int(sys.argv[3]), int(sys.argv[4])
        lab = OTB.lab_for(which); lab.add("PT", pt_trades(lab.g))
        FB.F = F50 if which == 50 else F150
        pl = plans50() if which == 50 else plans150(); kw = {} if which == 50 else dict(ref=3000.0)
        res, y1, _ = FB.Boot(lab).run(pl, n=n, L=20, seed=seed, **kw)
        pickle.dump((res, y1), open(SP + f"pt{which}_boot_{seed}.pkl", "wb")); print(f"[{MODE} {seed} done {time.time() - T0:.0f}s]"); sys.exit()
    for which, pl in ((50, plans50()), (150, plans150())):
        parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + f"pt{which}_boot_*.pkl"))]
        if not parts: continue
        res = {k: np.concatenate([p[0][k] for p in parts]) for k in pl}; y1 = {k: np.concatenate([p[1][k] for p in parts]) for k in pl}
        B = FB.Boot.__new__(FB.Boot); B.run = lambda *a, **k: (res, y1, 0)
        print(f"\n{'C' if which == 50 else 'D'}. {which}K funded, bootstrapped ({len(res[next(iter(pl))])} paired 2-year histories):")
        df, s_, _ = B.compare(pl); print(s_)
