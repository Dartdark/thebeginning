"""RollZone 24h NQ Long (rebuild analysis/rollzone_24h_test.py; trades in checks/candidates/rollzone_24h/) in every Apex plan:
add or replace. Entries 17:00 -> 15:30 CT, out by 08:25 (night) / 15:55 (day): inside one Apex trading day (17:00 -> 16:00),
so Apex-legal; booked on that trading day, worst point = the worst open P&L of the day's trades (closed earlier ones
included) applied from the start of the day (as overnight_tick_bench.py). MNQ = NQ / 10.
  RZ  = NQCAP, the note's tested version: session loss budget 75 NQ points = $150 per MNQ (scales with size).
  RZA = ATR version, the plain 0.8 x DailyATR stop (median ~$690 per MNQ); 1 MNQ only (the default $1,500 cap binds above).
Overlap: night longs ~ Overnight Tick (OT), day breakouts ~ Vault Break / Dual Thrust: replacements and their empty slots.
  A. 50K evaluation: combine set + RZ 0-3 MNQ.   B. 150K evaluation: x 2.5 (whole contracts) + RZ 0-5.
  C. 50K funded, bootstrapped: plan (as swing_target_bench) + RZ 1 / 2, + RZA 1; OT -> RZ 1 (and OT empty); VB 2/1 -> 1/1 + RZ 1.
  D. 150K funded, bootstrapped: plan x 1.5 + RS 1 + DT 2 + OT 2, + RZ 1 / 2 / 3; OT 2 -> RZ 2 (and OT empty); DT 2 -> RZ 2.
  E. Personal portfolio (17 pieces at 1 micro): + RZ / RZA, in place of Overnight Tick, in place of Dual Thrust.
  python3 analysis/rollzone_bench.py SCRATCH_DIR [evals | personal | worker50 SEED N | worker150 SEED N | merge]
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
import overnight_tick_bench as OTB, montecarlo as MC


def rz(name):
    t = pd.read_csv(f"checks/candidates/rollzone_24h/python_trades_{name}.csv", parse_dates=["date"])
    t = t[(t.date >= "2018-01-01") & ~t.roll]
    rows = []
    for d, x in t.groupby("date"):
        cum, worst = 0.0, 0.0
        for r in x.sort_values("e").itertuples():
            worst = min(worst, cum + r.adv); cum += r.net
        rows.append((d, worst, cum))
    return pd.DataFrame(rows, columns=["date", "adv", "net"]).set_index("date")


def day_paths(dates, t):
    """(D,) worst and close per trading date, per NQ."""
    pos = pd.Series(np.arange(len(dates)), index=dates); W = np.zeros(len(dates)); C = np.zeros(len(dates))
    for d, r in t.iterrows():
        if d in pos.index: W[pos[d]] = r.adv; C[pos[d]] = r.net
    return W, C


def add_rz(lab):
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    for key, name in (("RZ", "NQCAP"), ("RZA", "ATR")):
        W, C = day_paths(dates, rz(name))
        lab.W[key] = W[:, None] / 10 * np.ones((1, lab.W["VB"].shape[1])); lab.C[key] = C / 10


def plans50():
    CUR = {**{k: v for k, v in FB.PLAN.items() if k != "MON_MC"}, "VB_N": 2, "MOC_MES": 2, "RS_L": 1, "OT": 1}
    drop = lambda *ks: {k: v for k, v in CUR.items() if k not in ks}
    return {"50K plan": CUR, "+ RZ 1 MNQ": {**CUR, "RZ": 1}, "+ RZ 2 MNQ": {**CUR, "RZ": 2}, "+ RZA 1 MNQ": {**CUR, "RZA": 1},
            "OT -> RZ 1": {**drop("OT"), "RZ": 1}, "OT empty": drop("OT"), "VB 2/1 -> 1/1 + RZ 1": {**CUR, "VB_N": 1, "RZ": 1},
            "VB 2/1 -> 1/1 (empty)": {**CUR, "VB_N": 1}}


def plans150():
    CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2}
    base = {**{n: (("risk", v[1] * 1.5) if isinstance(v, tuple) else v * 1.5) for n, v in CUR.items()}, "RS": 1, "DT": 2, "OT": 2}
    drop = lambda *ks: {k: v for k, v in base.items() if k not in ks}
    return {"150K plan": base, "+ RZ 1 MNQ": {**base, "RZ": 1}, "+ RZ 2 MNQ": {**base, "RZ": 2}, "+ RZ 3 MNQ": {**base, "RZ": 3},
            "OT 2 -> RZ 2": {**drop("OT"), "RZ": 2}, "OT empty": drop("OT"), "DT 2 -> RZ 2": {**drop("DT"), "RZ": 2}}


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); T0 = time.time()
    if MODE == "evals":
        g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
        yr = pd.DatetimeIndex(g.ts[trr]).year; P = {}
        for nm, tt in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                       ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))):
            w, r = paths(g, tt); P[nm] = (w[trr] / 10, r[trr] / 10)
        dates = pd.DatetimeIndex(g.ts[trr]); Wd, Cd = day_paths(dates, rz("NQCAP"))
        P["RZ"] = (np.repeat(Wd[:, None] / 10, 1440, 1), np.repeat(Cd[:, None] / 10, 1440, 1))
        risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
        q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
        one = lambda p, c, n: 1.0
        def rep(nm, res):
            ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res]); ps = o == "pass"
            print(f"   {nm:<30} pass {ps[ok].mean():5.1%} (18-22 {ps[ok & (yr < 2023)].mean():5.1%}, 23-26 {ps[ok & (yr >= 2023)].mean():5.1%}), "
                  f"fail {(o == 'fail')[ok].mean():5.1%}", flush=True)
        print("\nA. 50K evaluation (every start day; RZ worst point placed at the day's start):")
        for k in (0, 1, 2, 3):
            qq = {**q, "RZ": float(k)}
            Ws = sum(P[x][0] * qq[x] for x in qq); Rs = sum(P[x][1] * qq[x] for x in qq)
            rep(f"combine set + RZ {k} MNQ", [CL.challenge(Ws, Rs, np.arange(s0, min(s0 + CL.MAXD, D)), one) for s0 in range(D)])
        print("\nB. 150K evaluation (combine set x 2.5, whole contracts):")
        for k in (0, 2, 5):
            qq = {"VB": 20.0, "ONB30": risk(2750, 0.25), "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1]), "RZ": float(k)}
            Ws = sum(P[x][0] * qq[x] for x in qq); Rs = sum(P[x][1] * qq[x] for x in qq)
            rep(f"x 2.5 + RZ {k} MNQ", [P150.evaluation(Ws, Rs, s0, D, P150.R150) for s0 in range(D)])
        sys.exit()
    if MODE == "personal":
        with contextlib.redirect_stdout(io.StringIO()):
            gg = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")
        P, days, ft = gg["P"], gg["days"], gg["from_trades"]; tot = P.sum(axis=1); yrs = len(days) / 252
        print("\nE. Personal portfolio (1 micro each):")
        for key, name in (("RZ", "NQCAP"), ("RZA", "ATR")):
            t = rz(name).reset_index()[["date", "net"]]; o, _ = ft(None, key, t)
            print(f"   {key} alone ${o.sum() / yrs:,.0f} a year, corr with the rest {np.corrcoef(o, tot)[0, 1]:+.2f}, with OT "
                  f"{np.corrcoef(o, P['OvernightTick'])[0, 1]:+.2f}, with Dual Thrust {np.corrcoef(o, P['DualThrust'])[0, 1]:+.2f}")
            for nm, x in (("17 pieces (now)", tot), (f"+ {key}", tot + o), (f"Overnight Tick -> {key}", tot - P["OvernightTick"] + o),
                          (f"Dual Thrust -> {key}", tot - P["DualThrust"] + o)):
                d = MC.daily_mc(x.values, horizon=252, n=5000, block=20, trail=1e12); e = x.cumsum()
                print(f"   {nm:<26} ${x.sum() / yrs:>7,.0f} a year, Sharpe {x.mean() / x.std() * np.sqrt(252):.2f}, max DD ${-(e - e.cummax()).min():>6,.0f}, "
                      f"MC p50 ${d['pnl_p50']:>7,.0f}, DD p95 ${d['dd_p95']:>6,.0f}, return/DD {d['ret_dd']:.1f}, capital ${d['dd_p95'] / 0.2:>7,.0f}")
        sys.exit()
    if MODE in ("worker50", "worker150"):
        which = 50 if MODE == "worker50" else 150; seed, n = int(sys.argv[3]), int(sys.argv[4])
        lab = OTB.lab_for(which); add_rz(lab)
        FB.F = F50 if which == 50 else F150
        pl = plans50() if which == 50 else plans150(); kw = {} if which == 50 else dict(ref=3000.0)
        res, y1, _ = FB.Boot(lab).run(pl, n=n, L=20, seed=seed, **kw)
        pickle.dump((res, y1), open(SP + f"rz{which}_boot_{seed}.pkl", "wb")); print(f"[{MODE} {seed} done {time.time() - T0:.0f}s]"); sys.exit()
    for which, pl in ((50, plans50()), (150, plans150())):
        parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + f"rz{which}_boot_*.pkl"))]
        if not parts: continue
        res = {k: np.concatenate([p[0][k] for p in parts]) for k in pl}; y1 = {k: np.concatenate([p[1][k] for p in parts]) for k in pl}
        B = FB.Boot.__new__(FB.Boot); B.run = lambda *a, **k: (res, y1, 0)
        print(f"\n{'C' if which == 50 else 'D'}. {which}K funded, bootstrapped ({len(res[next(iter(pl))])} paired 2-year histories):")
        df, s_, _ = B.compare(pl); print(s_)
