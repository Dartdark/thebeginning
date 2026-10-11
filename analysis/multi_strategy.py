"""Multi-strategy plan for Apex 50K: one strategy per account, accounts started
together. Reproduces the tables in multi_strategy/README.md.

Strategies (trade lists):
  V3     NQ VWAP Momentum v3, from its MultiCharts report
  VB     Vault Break (apex_strategies/NQ_Vault_Break.txt)
  DRIVE  Opening Drive (multi_strategy/NQ_Opening_Drive.txt)
  GAP    Gap Fill, experimental (multi_strategy/NQ_Gap_Fill.txt)
VB, DRIVE and GAP come from the Python versions in candidates.py unless a
MultiCharts report is given, e.g.
  python3 analysis/multi_strategy.py --VB "Vault Break report.xlsx" --DRIVE "Drive report.xlsx"
Every challenge is started on a real day and run on the real days that
followed (portfolio.py), at the account sizes in ACCOUNTS.

Extra strategies that only exist as MultiCharts reports can be added with
  --VPA report.xlsx   (VWAP Pullback ADX, multi_strategy/NQ_VWAP_Pullback_ADX.txt)
  --ONB report.xlsx   (Overnight Bias, apex_strategies/NQ_Overnight_Bias.txt)
each as its own 10 MNQ account.

Usage (from the repo root): python3 analysis/multi_strategy.py [--NAME report.xlsx ...]
Takes about a minute.
"""
import sys
import argparse
import numpy as np
import pandas as pd
sys.path.insert(0, "analysis")
from grid import Grid, execute
from portfolio import Book, load_mc, challenge
from candidates import vault_break, opening_drive, gap_fade

V3_REPORT = "Backtesting Strategy Performance Report v2 filtered up test.xlsx"
GREEN = 1.50                   # filter line threshold (10-day average range %)

# account name -> {strategy: MNQ}; GAP is sized by $ risk in the strategy, so
# "GAP: 10" means one unit of RiskPerTrade
ACCOUNTS = {
    "A  V3 10 MNQ": {"V3": 10},
    "B  Vault Break 12 MNQ": {"VB": 12},
    "C  Opening Drive 10 MNQ": {"DRIVE": 10},
    "D  Gap Fill $1,000 risk": {"GAP": 10},
}
PLANS = [["A  V3 10 MNQ"],
         ["A  V3 10 MNQ", "B  Vault Break 12 MNQ"],
         ["A  V3 10 MNQ", "B  Vault Break 12 MNQ", "C  Opening Drive 10 MNQ"],
         ["A  V3 10 MNQ", "B  Vault Break 12 MNQ", "C  Opening Drive 10 MNQ", "D  Gap Fill $1,000 risk"]]


def python_trades(g):
    return {
        "VB": execute(g, *_unpack(vault_break(g))),
        "DRIVE": execute(g, *_unpack(opening_drive(g, mode="follow", min_pct=0.2, flat=1100))),
        "GAP": execute(g, *_unpack(gap_fade(g, min_gap=0.2, max_gap=1.0, flat=1000, risk_usd=1000))),
    }


def _unpack(x):
    sig, kw = x
    return (sig,) if not kw else (sig, kw.get("max_trades", 99), kw.get("max_losses", 99))


def zero_edge(t):
    """Same trades with the average P&L removed (what the rules alone give)."""
    t = t.copy()
    q = t["qty"] if "qty" in t else 1.0
    t["exit"] = t["exit"] - t["side"] * t["net"].mean() / 20.0 / q
    return t


def outcomes(book, mnq, D, days=21):
    w, r = book.combine(mnq)
    res = [challenge(w, r, np.arange(s, min(s + days, D))) for s in range(D)]
    return np.array([np.nan if x is None else float(x[0] == "pass") for x in res])


def summary(t):
    y = t["date"].dt.year
    w, l = t.net[t.net > 0].sum(), -t.net[t.net < 0].sum()
    return dict(trades=len(t), win=f"{(t.net > 0).mean():.0%}", avg=round(t.net.mean()),
                pf=round(w / l, 2), avg_2018_22=round(t.net[y < 2023].mean()),
                avg_2023_26=round(t.net[y >= 2023].mean()))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for k in ("VB", "DRIVE", "GAP"):
        ap.add_argument(f"--{k}", help=f"MultiCharts report for {k} (default: Python version)")
    ap.add_argument("--VPA", help="MultiCharts report for VWAP Pullback ADX")
    ap.add_argument("--ONB", help="MultiCharts report for Overnight Bias")
    args = ap.parse_args()

    g = Grid("NQ_1min_*.csv")
    T = {"V3": load_mc(g, V3_REPORT), **python_trades(g)}
    for k in ("VB", "DRIVE", "GAP"):
        if getattr(args, k):
            T[k] = load_mc(g, getattr(args, k))
            print(f"{k}: MultiCharts report {getattr(args, k)}")
    for k, label in (("VPA", "E  VWAP Pullback ADX 10 MNQ"), ("ONB", "F  Overnight Bias 10 MNQ")):
        if getattr(args, k):
            T[k] = load_mc(g, getattr(args, k))
            ACCOUNTS[label] = {k: 10}
            PLANS.append(PLANS[2] + [label])
            print(f"{k}: MultiCharts report {getattr(args, k)}")

    print("\nPer strategy, per NQ (GAP per trade at its $ risk), after costs")
    print(pd.DataFrame({k: summary(t) for k, t in T.items()}).T.to_string())

    daily = pd.DataFrame({k: t.groupby("day").net.sum().reindex(range(g.D), fill_value=0)
                          for k, t in T.items()})
    print("\nCorrelation of daily P&L")
    print(daily.corr().round(2).to_string())

    book, book0 = Book(g), Book(g)
    for k, t in T.items():
        book.add(k, t)
        book0.add(k, zero_edge(t))
    yr = pd.DatetimeIndex(g.ts).year
    on = np.nan_to_num(g.avg10) >= GREEN
    on3 = on & np.r_[False, on[:-1]] & np.r_[False, False, on[:-2]]

    O = pd.DataFrame({a: outcomes(book, m, g.D) for a, m in ACCOUNTS.items()})
    Z = pd.DataFrame({a: outcomes(book0, m, g.D) for a, m in ACCOUNTS.items()})
    print("\nPass rate per account (challenge started on every day 2018-2026)")
    rows = {a: {"any day": O[a].mean(), "no edge": Z[a].mean(), "line green": O[a][on].mean(),
                "green 3 days": O[a][on3].mean(), "starts 2023-26": O[a][yr >= 2023].mean(),
                "worst year": O[a].groupby(yr).mean().min()} for a in ACCOUNTS}
    print(pd.DataFrame(rows).T.map("{:.0%}".format).to_string())
    print("\nPass rate by start year")
    print(O.groupby(yr).mean().map("{:.0%}".format).to_string())
    print("\nCorrelation of pass/fail between accounts started the same day")
    print(O.corr().round(2).to_string())

    print("\nAccounts started together: chance that at least one passes")
    for plan in PLANS:
        x = O[plan]
        anyp = x.max(axis=1, skipna=False)
        print(f"  {len(plan)} account(s) {' + '.join(p.split()[1] for p in plan):<28}"
              f" any day {anyp.mean():.0%}  line green {anyp[on].mean():.0%}"
              f"  starts 2023-26 {anyp[yr >= 2023].mean():.0%}  worst year {anyp.groupby(yr).mean().min():.0%}"
              f"  expected passes {x.sum(axis=1).mean():.2f}")
