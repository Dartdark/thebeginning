"""Conservative and aggressive versions of the personal stack (user, 2026-10-25), from analysis/personal_portfolio.py (1 micro
per piece, daily P&L, 2018-2026), measured like PORTFOLIO.md (Monte Carlo 20-day blocks, capital = DD p95 / 0.2).
  Conservative: only pieces proven in MultiCharts and live-ready - drops the forward-log pieces (S30, Kusho, S47, FC 2B,
  BB_MRM) and Dual Thrust (MultiCharts check pending); 1 micro each.
  Current: all pieces at 1 micro.
  Aggressive: all pieces; 2 micros on the five with Sharpe >= 1.4 (Twin, Overnight Tick, Kusho, Overnight Bias ML, Dual Thrust).
  python3 analysis/personal_variants.py > analysis/outputs/personal_variants_output.txt
"""
import sys, io, contextlib, runpy; sys.path.insert(0, "analysis")
import numpy as np, montecarlo as MC
with contextlib.redirect_stdout(io.StringIO()):
    P = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")["P"]
FWD = ["S30", "Kusho", "S47", "FC2B", "BB_MRM", "DualThrust"]
TOP = ["TwinContinuation", "OvernightTick", "Kusho", "OvernightBiasML", "DualThrust"]
W = {"conservative": {c: (0 if c in FWD else 1) for c in P}, "current": {c: 1 for c in P},
     "aggressive": {c: (2 if c in TOP else 1) for c in P}}
print(__doc__.split("\n")[0])
for nm, w in W.items():
    x = (P * [w[c] for c in P]).sum(axis=1); e = x.cumsum(); yrs = len(x) / 252
    d = MC.daily_mc(x.values, horizon=252, n=5000, block=20, trail=1e12)
    by = x.groupby(x.index.year).sum()
    print(f"\n{nm}: {sum(1 for v in w.values() if v)} pieces, {sum(w.values())} micros")
    print(f"   ${x.sum() / yrs:,.0f} a year, Sharpe {x.mean() / x.std() * np.sqrt(252):.2f}, max DD ${-(e - e.cummax()).min():,.0f}, worst day ${x.min():,.0f}, "
          f"worst month ${x.groupby([x.index.year, x.index.month]).sum().min():,.0f}")
    print(f"   Monte Carlo 1 year: p5 ${d['pnl_p5']:,.0f} / p50 ${d['pnl_p50']:,.0f} / p95 ${d['pnl_p95']:,.0f}, P(loss) {d['p_loss']:.1%}, DD p95 ${d['dd_p95']:,.0f}, "
          f"return/DD {d['ret_dd']:.1f}, capital ${d['dd_p95'] / 0.2:,.0f}")
    print("   by year:", {y: int(v) for y, v in by.round(0).items()})
    print("   sizes:", {k: v for k, v in w.items() if v})
