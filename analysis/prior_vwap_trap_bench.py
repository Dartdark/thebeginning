"""Prior VWAP Trap (user's upload 2026-10-29) on the plan benches: add and replace (CLAUDE.md 'Add or replace').
  evals : 50K evaluation (combine set VB 8 / ONB ADX30 $1,100 / Bridge 2 / EOS $500) and 150K (x 2.5): + PVT 1-3 MNQ,
          VB -> PVT, VB 4 + PVT (combine_levers_test.challenge, every start day 2018-2026).
  worker50 / worker150 SEED N, merge : 50K / 150K funded, bootstrapped (funded_bootstrap, paired 2-year histories, 20-day
          blocks) on the CURRENT plans: 50K = t_oneside_bench2 'RS longs -> T 1'; 150K = swing_target_bench 'DT 2 -> ST 2'.
          + PVT 1 / 2; VB -> PVT; Swing Target -> PVT (the other intraday momentum piece).
  personal : personal portfolio (1 micro each) + PVT, PVT in place of Dual Thrust / Swing Target.
  python3 analysis/prior_vwap_trap_bench.py SCRATCH_DIR [evals | worker50 SEED N | worker150 SEED N | merge | personal]
"""
import sys, pickle, warnings, runpy, io, contextlib; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import combine_levers_test as CL

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "evals"


def pvt_trades(g):
    """Lab-format PVT trades (raw entry / exit; with_slippage adds the 2 ticks)."""
    t = pd.read_csv("checks/candidates/prior_vwap_trap/trades_python.csv")
    t = t[t.date >= 20180101].reset_index(drop=True)
    day = np.searchsorted(g.dates, t.date.to_numpy())
    j1 = np.where(t.kind == "time", jof(t.t1.to_numpy()) - 1, jof(t.t1.to_numpy()))
    x = pd.DataFrame(dict(day=day, j0=jof(t.t0.to_numpy()), j1=j1, side=t.side, entry=t.entry, exit=t.exit,
                          kind=np.where(t.kind == "stop", 0, 2)))
    return with_slippage(x)


def plans50():
    import t_oneside_bench2 as TB2
    CUR = TB2.plans50()["RS longs -> T 1"]
    drop = lambda *ks: {k: v for k, v in CUR.items() if k not in ks}
    return {"50K plan (now)": CUR, "+ PVT 1": {**CUR, "PVT": 1}, "+ PVT 2": {**CUR, "PVT": 2},
            "VB -> PVT 1": {**drop("VB_N", "VB_F"), "PVT": 1}, "VB -> PVT 2": {**drop("VB_N", "VB_F"), "PVT": 2},
            "ST -> PVT 1": {**drop("ST"), "PVT": 1}}


def plans150():
    import swing_target_bench as STB
    CUR = STB.plans150()["DT 2 -> ST 2"]
    drop = lambda *ks: {k: v for k, v in CUR.items() if k not in ks}
    return {"150K plan (now)": CUR, "+ PVT 1": {**CUR, "PVT": 1}, "+ PVT 2": {**CUR, "PVT": 2}, "+ PVT 3": {**CUR, "PVT": 3},
            "VB -> PVT 3": {**drop("VB_N", "VB_F"), "PVT": 3}, "ST 2 -> PVT 2": {**drop("ST"), "PVT": 2}}


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    if MODE in ("worker50", "worker150", "merge"):
        import time, glob
        import funded_bootstrap as FB, funded_sim150 as F150, funded_sim as F50
        import overnight_tick_bench as OTB, swing_target_bench as STB, t_oneside_bench2 as TB2
        if MODE != "merge":
            which = 50 if MODE == "worker50" else 150; seed, n = int(sys.argv[3]), int(sys.argv[4]); T0 = time.time()
            lab = OTB.lab_for(which); lab.add("ST", STB.pt_trades(lab.g)); lab.add("PVT", pvt_trades(lab.g), slippage=False)
            if which == 50: lab.add("T", TB2.tos_t())
            FB.F = F50 if which == 50 else F150
            pl = plans50() if which == 50 else plans150(); kw = {} if which == 50 else dict(ref=3000.0)
            res, y1, _ = FB.Boot(lab).run(pl, n=n, L=20, seed=seed, **kw)
            pickle.dump((res, y1), open(SP + f"pvt{which}_boot_{seed}.pkl", "wb")); print(f"[{MODE} {seed} done {time.time() - T0:.0f}s]")
            if seed == 1:
                ks = [k for k in pl[next(iter(pl))]] + ["PVT"]; print(lab.corr(ks).loc["PVT"].round(2).to_string())
            sys.exit()
        for which, pl in ((50, plans50()), (150, plans150())):
            parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + f"pvt{which}_boot_*.pkl"))]
            if not parts: continue
            res = {k: np.concatenate([p[0][k] for p in parts]) for k in pl}; y1 = {k: np.concatenate([p[1][k] for p in parts]) for k in pl}
            B = FB.Boot.__new__(FB.Boot); B.run = lambda *a, **k: (res, y1, 0)
            print(f"\n{which}K funded, bootstrapped ({len(res[next(iter(pl))])} paired 2-year histories):")
            df, s_, _ = B.compare(pl); print(s_)
        sys.exit()
    if MODE == "personal":
        import montecarlo as MC
        with contextlib.redirect_stdout(io.StringIO()):
            gg = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")
        P, days, ft = gg["P"], gg["days"], gg["from_trades"]
        t = pd.read_csv("checks/candidates/prior_vwap_trap/trades_python.csv")
        t = pd.DataFrame(dict(date=pd.to_datetime(t.date.astype(str)), net=t.pnl))
        o, _ = ft(None, "PVT", t); tot = P.sum(axis=1); yrs = len(days) / 252
        print(f"\nPersonal portfolio ({P.shape[1]} pieces at 1 micro; PVT alone ${o.sum() / yrs:,.0f} a year, corr with the rest {np.corrcoef(o, tot)[0, 1]:+.2f}):")
        cases = [("now", tot), ("+ PVT", tot + o), ("+ PVT x 2", tot + 2 * o)]
        for k in [c for c in P.columns if c in ("DualThrust", "SwingTarget", "ST")]:
            cases.append((f"{k} -> PVT", tot - P[k] + o))
        for nm, x in cases:
            d = MC.daily_mc(x.values, horizon=252, n=5000, block=20, trail=1e12); e = x.cumsum()
            print(f"   {nm:<22} ${x.sum() / yrs:>7,.0f} a year, Sharpe {x.mean() / x.std() * np.sqrt(252):.2f}, max DD ${-(e - e.cummax()).min():>6,.0f}, "
                  f"DD p95 ${d['dd_p95']:>6,.0f}, return/DD {d['ret_dd']:.1f}, capital ${d['dd_p95'] / 0.2:>7,.0f}")
        sys.exit()
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    yr = pd.DatetimeIndex(g.ts[trr]).year; P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0]))), ("PVT", pvt_trades(g))):
        w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    print(f"[PVT in the lab: {int((P['PVT'][1][:, -1] != 0).sum())} trade days, ${P['PVT'][1][:, -1].sum() * 10 / max(1, (P['PVT'][1][:, -1] != 0).sum()):.0f} per NQ per trade day]")
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    one = lambda p, c, n: 1.0
    import plan_150k_test as P150
    for size, mult, rules in (("50K", 1.0, None), ("150K", 2.5, "150")):
        q = {"VB": 8.0 * mult, "ONB30": risk(1100 * mult, 0.25), "MON_BR": 2.0 * mult, "EOS": risk(500 * mult, REPORTS["EOS"][1])}
        wo = lambda k: {a: b for a, b in q.items() if a != k}
        cases = [("set", q)] + [(f"+ PVT {k}", {**q, "PVT": float(k * mult)}) for k in (1, 2, 3)]
        cases += [(f"VB -> PVT {k}", {**wo("VB"), "PVT": float(k * mult)}) for k in (4, 6, 8)]
        cases += [(f"VB 4 + PVT {k}", {**q, "VB": 4.0 * mult, "PVT": float(k * mult)}) for k in (2, 4)]
        print(f"\n{size} evaluation (PVT sizes x {mult}):")
        if rules:   # whole contracts at 150K size from their own dollar risk (as swing_target_bench)
            q = {"VB": 20.0, "ONB30": risk(2750, 0.25), "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1])}
            cases = [("set", q)] + [(f"+ PVT {k}", {**q, "PVT": float(k)}) for k in (2, 5, 8)] + \
                    [(f"VB 20 -> PVT {k}", {**{a: b for a, b in q.items() if a != "VB"}, "PVT": float(k)}) for k in (10, 20)]
        for nm, qq in cases:
            W = sum(P[x][0] * qq[x] for x in qq); Rr = sum(P[x][1] * qq[x] for x in qq)
            if rules: res = [P150.evaluation(W, Rr, s0, D, P150.R150) for s0 in range(D)]
            else: res = [CL.challenge(W, Rr, np.arange(s0, min(s0 + CL.MAXD, D)), one) for s0 in range(D)]
            ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); ps = o == "pass"
            print(f"   {nm:<16} pass {ps[ok].mean():5.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, 23-26 {ps[ok & (yr >= 2023)].mean():5.1%}), fail {(o == 'fail')[ok].mean():5.1%}", flush=True)
