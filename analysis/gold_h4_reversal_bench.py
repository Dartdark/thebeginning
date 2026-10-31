"""Gold H4 reversal (analysis/gold_h4_reversal_test.py, as coded = multi-day holds, personal only) in the personal plan at 1 MGC:
add, and replace the most-correlated piece / S30 / CL fade (compared with simply dropping that piece). $0.55 extra micro fee a trade.
  python3 analysis/gold_h4_reversal_bench.py   (needs scratch_data/g24.pkl from analysis/build_lab.py)
"""
import sys, io, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd, montecarlo as MC
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")
P, days = g["P"].copy(), g["days"]; print(list(P.columns))
gd = pd.read_csv("analysis/outputs/gold_h4_reversal_daily_per_gc.csv", index_col=0, parse_dates=True).iloc[:, 0]
gold = (gd / 10 - 0).reindex(days, fill_value=0.0)
tr = pd.read_csv("analysis/outputs/gold_h4_reversal_trades.csv", parse_dates=["date"]); fee = tr.groupby("date").size().reindex(days, fill_value=0) * 0.55
gold = gold - fee
tot = P.sum(axis=1); yrs = len(days) / 252
print(f"gold alone ${gold.sum()/yrs:,.0f}/yr, corr with plan {np.corrcoef(gold, tot)[0,1]:+.2f}; corr with each:")
print(P.corrwith(gold).round(2).to_string())
rows = {"plan now": tot, "+ Gold H4 1 MGC": tot + gold}
top = P.corrwith(gold).idxmax(); rows[f"{top} -> Gold H4"] = tot - P[top] + gold
for nm, x in rows.items():
    d = MC.daily_mc(x.values, horizon=252, n=5000, block=20, trail=1e12); e = x.cumsum()
    print(f"{nm:<28} ${x.sum()/yrs:>7,.0f}/yr Sharpe {x.mean()/x.std()*np.sqrt(252):.2f} maxDD ${-(e-e.cummax()).min():,.0f} MC p50 ${d['pnl_p50']:,.0f} DD p95 ${d['dd_p95']:,.0f} return/DD {d['ret_dd']:.2f} capital ${d['dd_p95']/0.2:,.0f}")
for nm, x in {"plan without S30": tot - P["S30"], "without CL fade": tot - P["CLSundayFade_perMCL"], "CL fade -> Gold H4": tot - P["CLSundayFade_perMCL"] + gold}.items():
    d = MC.daily_mc(x.values, horizon=252, n=5000, block=20, trail=1e12)
    print(f"{nm:<28} ${x.sum()/yrs:>7,.0f}/yr DD p95 ${d['dd_p95']:,.0f} return/DD {d['ret_dd']:.2f}")
