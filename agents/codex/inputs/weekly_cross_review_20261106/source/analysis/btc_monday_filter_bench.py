"""Monday Long sized by Bitcoin's weekend move (WATCHLIST #27; user 2026-11-05 'test it anyway'). POST HOC: the split was found on
the full sample incl. 2023+, so no holdout is left; read any gain with that discount.
BTC weekend = Coinbase spot Fri 16:00 -> Sun 17:00 CT (analysis/outputs/btc_weekend_beta_NQ.csv); Monday Long = the plan's MC trades.
  C. 150K funded, bootstrapped (plan as rollzone_bench.plans150): Monday Long 1.5 (plan) vs only on BTC-down weekends, vs 2x down / 1x up.
  E. Personal book (1 micro each): Monday Long vs BTC-down only vs 2 down / 1 up.
  python3 analysis/btc_monday_filter_bench.py SCRATCH_DIR [worker SEED N | merge | personal]
"""
import sys, glob, time, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "merge"
import funded_bootstrap as FB, funded_sim150 as F150
import overnight_tick_bench as OTB, rollzone_bench as RZB


def btc_monday():
    d = pd.read_csv("analysis/outputs/btc_weekend_beta_NQ.csv", parse_dates=["date"])
    return pd.Series(d.btc.values, index=d.date + pd.Timedelta(days=3))         # Friday -> Monday


def add_split(lab):
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr]); b = btc_monday().reindex(dates)
    dn = (b < 0).to_numpy(); up = (b >= 0).to_numpy()                               # no BTC data -> neither (pre-2018-12)
    for key, m in (("MON_DN", dn), ("MON_UP", up)):
        lab.W[key] = lab.W["MON_MC"] * m[:, None]; lab.C[key] = lab.C["MON_MC"] * m
    return dn.sum(), up.sum()


def plans():
    base = RZB.plans150()["150K plan"]; q = base["MON_MC"]; drop = {k: v for k, v in base.items() if k != "MON_MC"}
    return {"150K plan": base, "Monday Long only after BTC-down": {**drop, "MON_DN": q},
            "Monday 2x after BTC-down, 1x after up": {**drop, "MON_DN": 2 * q, "MON_UP": q},
            "Monday 1.5x down, 0.5x up": {**drop, "MON_DN": 1.5 * q, "MON_UP": 0.5 * q}}


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); T0 = time.time()
    if MODE == "worker":
        seed, n = int(sys.argv[3]), int(sys.argv[4])
        lab = OTB.lab_for(150); nd, nu = add_split(lab); FB.F = F150
        res, y1, _ = FB.Boot(lab).run(plans(), n=n, L=20, seed=seed, ref=3000.0)
        pickle.dump((res, y1), open(SP + f"btcmon_boot_{seed}.pkl", "wb")); print(f"[worker {seed} done {time.time() - T0:.0f}s; Mondays down {nd} up {nu}]"); sys.exit()
    if MODE == "personal":
        import io, runpy, contextlib, montecarlo as MC
        with contextlib.redirect_stdout(io.StringIO()):
            gg = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")
        P, days = gg["P"], gg["days"]; tot = P.sum(axis=1); yrs = len(days) / 252; mon = P["MondayLong"]
        b = btc_monday().reindex(days); dn = (b < 0).astype(float); up = (b >= 0).astype(float)
        print("\nE. Personal book (1 micro each), Monday Long sizing by the BTC weekend:")
        for nm, x in (("current (Monday 1)", tot), ("Monday only after BTC-down", tot - mon + mon * dn),
                      ("Monday 2 down / 1 up", tot - mon + mon * (2 * dn + up))):
            d = MC.daily_mc(x.values, horizon=252, n=5000, block=20, trail=1e12); e = x.cumsum()
            print(f"   {nm:<30} ${x.sum() / yrs:>7,.0f} a year, Sharpe {x.mean() / x.std() * np.sqrt(252):.2f}, max DD ${-(e - e.cummax()).min():>6,.0f}, "
                  f"MC p50 ${d['pnl_p50']:>7,.0f}, DD p95 ${d['dd_p95']:>6,.0f}, return/DD {d['ret_dd']:.1f}")
        sys.exit()
    pl = plans(); parts = [pickle.load(open(f, "rb")) for f in sorted(glob.glob(SP + "btcmon_boot_*.pkl"))]
    res = {k: np.concatenate([p[0][k] for p in parts]) for k in pl}; y1 = {k: np.concatenate([p[1][k] for p in parts]) for k in pl}
    B = FB.Boot.__new__(FB.Boot); B.run = lambda *a, **k: (res, y1, 0)
    print(f"\nC. 150K funded, bootstrapped ({len(res[next(iter(pl))])} paired 2-year histories):")
    df, s_, _ = B.compare(pl); print(s_)
