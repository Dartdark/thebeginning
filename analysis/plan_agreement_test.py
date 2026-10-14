"""Combine the plan's edges (2026-10-14): do the plan strategies' same-day signals, or the plan's recent P&L, predict each
strategy's next trades? MultiCharts trade lists (per contract, $7.25 + 1 tick a market / stop fill via funded_lab.with_slippage).
Pre-specified:
  A  agreement: for each NQ trade, the plan's NQ trades that ENTERED EARLIER the same date (known at entry): same side vs
     opposite side vs none; per-trade P&L in units of the strategy's own sd (z), pooled, plus per strategy
  B  Overnight Bias ML's side that morning as the filter for later strategies (VB, LDF, EOS, VCS, NFP)
  C  sizing by recent results: plan daily P&L (each strategy in its own sd units) on days after a positive vs negative
     trailing 5-day / 20-day plan P&L
  python3 analysis/plan_agreement_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc
from funded_lab import with_slippage
from co_oc_reversal_test import load

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
F = {"VB": "Backtesting Strategy Performance Report VB v1.xlsx",
     "ONB_ML": "Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx",
     "MON": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes NQ Monday Longs.xlsx",
     "EOS": "Backtesting Strategy Performance Report EOS v1.xlsx",
     "LDF": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes Late Day Flow.xlsx",
     "NFP": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes NFP Fade.xlsx",
     "BRIDGE": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes Bridge Monday Longs.xlsx",
     "VCS": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes Vol-Control Sell Flow.xlsx"}


def tline(x, nm):
    x = pd.Series(x).dropna()
    if len(x) < 5: return f"   {nm:<44} n={len(x)}"
    return f"   {nm:<44} n={len(x):5d} mean z {x.mean():+.3f}  t {x.mean() / x.std() * np.sqrt(len(x)):+.2f}"


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    T = []
    for k, f in F.items():
        t = with_slippage(load_mc(g, f)); t["net"] = (t.exit - t.entry) * t.side * 20 - 7.25
        t["date"] = pd.DatetimeIndex(g.ts[t.day.values]); t["strat"] = k
        T.append(t[["date", "day", "j0", "side", "net", "strat"]])
    T = pd.concat(T); T = T[T.date >= "2018-01-01"].reset_index(drop=True)
    sd = T.groupby("strat").net.transform("std"); T["z"] = T.net / sd
    print(T.groupby("strat").agg(n=("net", "size"), avg=("net", "mean"), longs=("side", lambda s: (s > 0).mean())).round(2).to_string())
    # A
    same = np.zeros(len(T), int); opp = np.zeros(len(T), int)
    for d, grp in T.groupby("day"):
        for i in grp.index:
            prior = grp[(grp.j0 < T.at[i, "j0"]) & (grp.strat != T.at[i, "strat"])]
            same[i] = (prior.side == T.at[i, "side"]).sum(); opp[i] = (prior.side != T.at[i, "side"]).sum()
    T["same"], T["opp"] = same, opp
    print("\nA. agreement with earlier plan trades the same day (pooled, z units)")
    print(tline(T.z[(T.same > 0) & (T.opp == 0)], "earlier trade(s) same side only"))
    print(tline(T.z[(T.opp > 0) & (T.same == 0)], "earlier trade(s) opposite side only"))
    print(tline(T.z[(T.same == 0) & (T.opp == 0)], "no earlier plan trade"))
    for s in ("VB", "LDF", "EOS", "VCS"):
        q = T[T.strat == s]
        print(f"   {s}: same ${q.net[(q.same > 0) & (q.opp == 0)].mean():.0f} (n {((q.same > 0) & (q.opp == 0)).sum()}), "
              f"opposite ${q.net[(q.opp > 0) & (q.same == 0)].mean():.0f} (n {((q.opp > 0) & (q.same == 0)).sum()}), "
              f"none ${q.net[(q.same == 0) & (q.opp == 0)].mean():.0f} (n {((q.same == 0) & (q.opp == 0)).sum()})")
    print("\nB. Overnight Bias ML's side that morning as a filter (trades entering after the ONB entry)")
    onb = T[T.strat == "ONB_ML"].set_index("day")[["side", "j0"]]
    for s in ("VB", "LDF", "EOS", "VCS", "NFP"):
        q = T[T.strat == s].copy(); m = q.day.map(onb.side); after = q.j0 > q.day.map(onb.j0)
        q = q[m.notna() & after]; agree = q.side == q.day.map(onb.side)
        print(f"   {s:<6} with ONB agreeing ${q.net[agree].mean():6.0f} (n {agree.sum():3d}, z t {q.z[agree].mean() / q.z[agree].std() * np.sqrt(agree.sum()):+.2f}) | "
              f"disagreeing ${q.net[~agree].mean():6.0f} (n {(~agree).sum():3d}) | no ONB trade ${T[(T.strat == s) & ~T.day.isin(onb.index)].net.mean():6.0f}")
    print("\nC. plan daily P&L (sd units) after positive vs negative trailing plan P&L")
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days >= "2018-01-01"]
    P = T.groupby("date").z.sum().reindex(days).fillna(0)
    for w in (5, 20):
        tr_ = P.rolling(w).sum().shift(1)
        print(tline(P[tr_ > 0], f"after trailing {w}-day plan P&L > 0")); print(tline(P[tr_ <= 0], f"after trailing {w}-day plan P&L <= 0"))
