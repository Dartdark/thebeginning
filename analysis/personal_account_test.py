"""Personal (own-money) account vs Apex (user, 2026-10-15: 'is a live personal account the optimal path for growth?').
The plan's raw edge without Apex's rules: every funded-plan NQ strategy at 1 NQ (MultiCharts trade lists, $7.25 + 1 tick),
CL fade at 1 CL, daily P&L 2018-2026: annual profit, max drawdown, worst month, and the capital needed for a given risk
tolerance (max drawdown = 20% / 30% of capital), so return on capital can be compared with Apex's cost-only risk.
  python3 analysis/personal_account_test.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    names = ["VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC", "MON_BR_MC", "CLS"]
    # lab.C is $ per MNQ (per MCL for CLS); 1 NQ = 10 MNQ, 1 CL = 10 MCL
    d = pd.Series(sum(lab.C[k] for k in names) * 10, index=dates); d = d[d.index >= "2018-01-01"]
    eq = d.cumsum(); dd = (eq - eq.cummax()).min(); yrs = len(d) / 252
    m = d.resample("ME").sum()
    print(f"\nAll 8 strategies at 1 NQ (1 CL): ${d.sum() / yrs:,.0f} a year, max drawdown ${-dd:,.0f}, worst month ${m.min():,.0f}, "
          f"losing months {np.mean(m < 0):.0%}, Sharpe {d.mean() / d.std() * np.sqrt(252):.2f}")
    for per, x in (("2018-22", d[d.index.year < 2023]), ("2023-26", d[d.index.year >= 2023])):
        e = x.cumsum(); print(f"   {per}: ${x.sum() / (len(x) / 252):,.0f} a year, max DD ${-(e - e.cummax()).min():,.0f}")
    print("   by year:", d.groupby(d.index.year).sum().round(0).astype(int).to_dict())
    for tol in (0.2, 0.3):
        cap = -dd / tol
        print(f"   capital for a {tol:.0%} max drawdown: ${cap:,.0f} -> {d.sum() / yrs / cap:.0%} a year on capital (backtest)")
