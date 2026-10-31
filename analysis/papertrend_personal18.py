"""PAPERTREND v2 (MultiCharts List of Trades of Claude's code, checks/candidates/papertrend/mc_trades_claude.csv, per NQ after
$17.25) added to the current 18-piece personal plan at 1 MNQ, and in place of Dual Thrust (2026-10-25, user).
  python3 analysis/papertrend_personal18.py > analysis/outputs/papertrend_personal18_output.txt"""
import io, runpy, contextlib, sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np
import montecarlo as MC
with contextlib.redirect_stdout(io.StringIO()):
    gg = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")
P, ft = gg["P"], gg["from_trades"]; yrs = len(P) / 252
o, n = ft("checks/candidates/papertrend/mc_trades_claude.csv", "PT"); tot = P.sum(axis=1)
print(__doc__.split("\n")[0]); print(f"PT alone ${o.sum() / yrs:,.0f} a year ({n} trades), corr with the book {np.corrcoef(o, tot)[0, 1]:+.2f}, "
      f"Dual Thrust {np.corrcoef(o, P['DualThrust'])[0, 1]:+.2f}, Swing Target {np.corrcoef(o, P['SwingTarget'])[0, 1]:+.2f}")
for nm, x in (("18 pieces (now)", tot), ("+ PT 1 MNQ", tot + o), ("Dual Thrust -> PT", tot - P["DualThrust"] + o), ("Swing Target -> PT", tot - P["SwingTarget"] + o)):
    d = MC.daily_mc(x.values, horizon=252, n=5000, block=20, trail=1e12); e = x.cumsum()
    print(f"   {nm:<22} ${x.sum() / yrs:>7,.0f} a year, Sharpe {x.mean() / x.std() * np.sqrt(252):.2f}, max DD ${-(e - e.cummax()).min():>6,.0f}, "
          f"DD p95 ${d['dd_p95']:>6,.0f}, return/DD {d['ret_dd']:.2f}, capital ${d['dd_p95'] / 0.2:>7,.0f}")
