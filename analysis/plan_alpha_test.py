"""Alpha vs beta for the plan (after 'What Is Alpha', The Institutional Protocol Quant Foundations N-01, user's PDF 2026-10-15:
alpha = the intercept of excess returns regressed on benchmark factor returns; beta can be bought, only the intercept is
skill; claims need t >= 3). Our strategies are mostly NQ longs, so the benchmark that matters is NQ itself.
Here, per strategy, daily net P&L of 1 NQ (MultiCharts trade lists, $7.25 + 1 tick, 2018-2026, every trading day, 0 when
flat) regressed on the daily P&L of holding 1 NQ (15:00 CT close to 15:00 CT close; for Bridge Monday the Friday 15:00 ->
Monday 15:00 move is booked on Monday). Newey-West t (5 lags). Reported: beta, alpha $ a day / a year, alpha t, and the share
of the strategy's total P&L that beta x NQ's drift explains. Second model adds the day-session move (8:30 -> 15:00) and the
overnight move separately (a strategy can carry exposure to only one part of the day).
  python3 analysis/plan_alpha_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, COMM = 20.0, 7.25


def nw_ols(y, X, lags=5):
    X = np.column_stack([np.ones(len(y)), X]); b = np.linalg.lstsq(X, y, rcond=None)[0]; e = y - X @ b
    XtXi = np.linalg.inv(X.T @ X); S = (X * e[:, None]).T @ (X * e[:, None])
    for L in range(1, lags + 1):
        w = 1 - L / (lags + 1); G = (X[L:] * e[L:, None]).T @ (X[:-L] * e[:-L, None]); S += w * (G + G.T)
    se = np.sqrt(np.diag(XtXi @ S @ XtXi)); return b, b / se


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); tr = g.trading; ts = pd.DatetimeIndex(g.ts[tr])
    C = pd.DataFrame(g.c[tr]).ffill(axis=1).to_numpy()
    c15, o830 = C[:, jof(1500)], C[:, jof(830)]
    mk = pd.DataFrame({"bh": np.r_[np.nan, np.diff(c15)] * PV, "day": (c15 - o830) * PV}, index=ts)
    mk["night"] = mk.bh - mk.day
    mk = mk[(ts.year >= 2018)].dropna()
    T = {k: with_slippage(load_mc(g, REPORTS[k][0])) for k in ("VB", "ONB_ML2_MC", "EOS", "MON_MC", "LDF_MC", "NFP_MC")}
    T["MON_BR"] = load_bridge_mc(g)
    print(f"\nNQ buy-and-hold: ${mk.bh.mean():.0f} a day (${mk.bh.mean() * 252:,.0f} a year per NQ); day session ${mk.day.mean():.0f}, overnight ${mk.night.mean():.0f}")
    print("\nModel 1: strategy daily P&L = alpha + beta x NQ daily P&L")
    print(f"   {'strategy':<11} {'P&L/yr':>9} {'beta':>6} {'alpha/yr':>9} {'alpha t':>8} {'raw t':>6} {'beta share':>10} | model 2: beta_day beta_night alpha/yr t")
    rows = []
    for nm, t in T.items():
        net = (t.exit - t.entry).to_numpy() * t.side.to_numpy() * PV - COMM
        s = pd.Series(net, index=pd.DatetimeIndex(g.ts[t.day.to_numpy()])).groupby(level=0).sum().reindex(mk.index, fill_value=0.0)
        y = s.to_numpy()
        b, tt = nw_ols(y, mk.bh.to_numpy()); b2, t2 = nw_ols(y, mk[["day", "night"]].to_numpy())
        _, traw = nw_ols(y, np.zeros((len(y), 0)))
        share = b[1] * mk.bh.mean() / y.mean()
        print(f"   {nm:<11} ${y.mean() * 252:>8,.0f} {b[1]:>6.3f} ${b[0] * 252:>8,.0f} {tt[0]:>8.2f} {traw[0]:>6.2f} {share:>10.0%} |"
              f" {b2[1]:+.3f} {b2[2]:+.3f} ${b2[0] * 252:>8,.0f} {t2[0]:+.2f}")
        rows.append(s.rename(nm))
    P = pd.concat(rows, axis=1)
    y = P.sum(1).to_numpy(); b, tt = nw_ols(y, mk.bh.to_numpy())
    print(f"   {'all 7 (1 NQ each)':<11} ${y.mean() * 252:>8,.0f} {b[1]:>6.3f} ${b[0] * 252:>8,.0f} {tt[0]:>8.2f}   beta share {b[1] * mk.bh.mean() / y.mean():.0%}")
    for per, m in (("2018-22", mk.index.year < 2023), ("2023-26", mk.index.year >= 2023)):
        b, tt = nw_ols(y[m], mk.bh.to_numpy()[m])
        print(f"      {per}: beta {b[1]:.3f}, alpha ${b[0] * 252:,.0f}/yr, t {tt[0]:.2f}")
