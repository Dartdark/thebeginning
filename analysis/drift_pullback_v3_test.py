"""DriftPullBack (user's simplified file 2026-10-24; checks/candidates/drift_pullback_v3/): the v2.1 rebuild
(analysis/drift_pullback_test.py) with this file's differences: no arm expiry (window 99), entries 10:00-15:30 ET =
9:00-14:30 CT, flat 15:55 ET = 14:55 CT, 1 tick stop slippage. Standalone per NQ, then the personal portfolio
(17 pieces, 1 micro each): + DP, + DP longs, + DP shorts.
  python3 analysis/drift_pullback_v3_test.py SCRATCH_DIR
"""
import sys, io, pickle, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd, montecarlo as MC
import drift_pullback_test as DP
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); P = DP.prep(g)
    t = DP.run(g, P, window=99, start=900, end=1430, flat=1455, slip_ticks=1)
    print(DP.line(t, "v3 all")); print(DP.line(t[t.side > 0], "  longs")); print(DP.line(t[t.side < 0], "  shorts"))
    print("   by year:", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
    with contextlib.redirect_stdout(io.StringIO()):
        G = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")
    Pp, ft = G["P"], G["from_trades"]; tot = Pp.sum(axis=1); yrs = len(Pp) / 252
    print("\nPersonal portfolio (1 micro each):")
    for nm, q in (("17 pieces (now)", None), ("+ DP", t), ("+ DP longs", t[t.side > 0]), ("+ DP shorts", t[t.side < 0])):
        x = tot if q is None else tot + ft(None, "DP", q[["date", "net"]])[0]
        d = MC.daily_mc(x.values, horizon=252, n=5000, block=20, trail=1e12); e = x.cumsum()
        print(f"   {nm:<18} ${x.sum() / yrs:>7,.0f} a year, Sharpe {x.mean() / x.std() * np.sqrt(252):.2f}, max DD ${-(e - e.cummax()).min():>6,.0f}, "
              f"DD p95 ${d['dd_p95']:>6,.0f}, return/DD {d['ret_dd']:.1f}, capital ${d['dd_p95'] / 0.2:>7,.0f}")
