"""Funded phase (Apex 50K EOD Performance Account): sizes and strategies that
maximize the money taken out, on the full 24-hour data.

Prints:
  1. Overnight Drift (new, NQ_Overnight_Drift.txt): results, neighbouring
     settings, correlation with the other strategies
  2. Performance Accounts started on every real day: expected payouts
     within 1 year (250 trading days) and 2 years (500) for the challenge
     sizes and the funded candidates, with and without Overnight Drift
  3. the same with no edge (each strategy's average trade removed)
  4. payout timing: buffer kept above the safety net; the consistency rule
  5. challenge + funded together: expected payouts per challenge bought

Rules and assumptions: analysis/funded_sim.py.
Usage (from the repo root): python3 analysis/funded24.py   (about 4 minutes)
"""
import os
import sys
import warnings
import numpy as np
import pandas as pd
sys.path.insert(0, "analysis")
warnings.filterwarnings("ignore")
from grid import execute
from grid24 import Grid24
from portfolio import load_mc, paths
from candidates24 import overnight_drift24
from multi_strategy import zero_edge
from multi_strategy24 import VB_REPORT, OD_REPORT, ONB_REPORT, summary
import funded_sim as F

NAMES = ["VB", "ONB", "OD", "OND"]
# sizes: VB and OD in MNQ; ONB and OND as RiskPerTrade in $ (whole MNQ, stop 30% ATR)
PLANS = {
    "Challenge plan (VB 8, ONB $1,100)": dict(VB=8, ONB=1100),
    "Fast: VB 4, ONB $500, OND $500": dict(VB=4, ONB=500, OND=500),
    "Balanced: VB 3, ONB $300, OND $500": dict(VB=3, ONB=300, OND=500),
    "Balanced, no OND: VB 3, ONB $300": dict(VB=3, ONB=300),
    "Slow: VB 2, ONB $300, OND $500": dict(VB=2, ONB=300, OND=500),
    "Slow, no OND: VB 2, ONB $300": dict(VB=2, ONB=300),
    "Slowest: VB 1, ONB $300, OND $300": dict(VB=1, ONB=300, OND=300),
}
PASS_RATE, FEE = 0.44, 50          # challenge plan (multi_strategy24.py)
OND_REPORT = "Backtesting Strategy Performance Report OND v1.xlsx"   # used when present


class Book:
    def __init__(self, g, trades):
        tr = g.trading
        self.W = np.stack([paths(g, trades[k])[0][tr] / 10 for k in NAMES])     # per MNQ
        self.C = np.stack([paths(g, trades[k])[1][tr][:, -1] / 10 for k in NAMES])
        self.stop_mnq = 0.30 * np.nan_to_num(g.daily_atr(15)[tr], nan=1e12) * 2.0
        self.D = len(tr)
        self.yr = pd.DatetimeIndex(g.ts[tr]).year

    def base(self, plan):
        b = np.zeros((len(NAMES), self.D))
        for k, v in plan.items():
            i = NAMES.index(k)
            b[i] = v / self.stop_mnq if k in ("ONB", "OND") else v
        return b

    def run(self, plan, horizon, **kw):
        st = np.arange(0, self.D - horizon)
        r = F.simulate_sized(self.W, self.C, self.base(plan), horizon=horizon, starts=st, **kw)
        r["yr"] = self.yr[st]
        return r


def row(r):
    p, y = r["paid"], r["yr"]
    f = r["first"][r["first"] > 0]
    return dict(expected=p.mean(), starts_2018_22=p[y < 2023].mean(), starts_2023_on=p[y >= 2023].mean(),
                worst_year=pd.Series(p).groupby(y).mean().min(), all_6=(r["payouts"] == 6).mean(),
                blown=r["blown"].mean(), any_payout=(r["payouts"] > 0).mean(),
                days_to_1st=np.median(f) if len(f) else np.nan, days_used=r["days"].mean())


def show(df):
    money = {c: "${:,.0f}".format for c in ("expected", "starts_2018_22", "starts_2023_on", "worst_year")}
    pct = {c: "{:.0%}".format for c in ("all_6", "blown", "any_payout")}
    days = {c: "{:.0f}".format for c in ("days_to_1st", "days_used")}
    print(df.to_string(formatters={**money, **pct, **days}))


if __name__ == "__main__":
    g = Grid24()
    s, kw = overnight_drift24(g)
    T = {"VB": load_mc(g, VB_REPORT), "ONB": load_mc(g, ONB_REPORT), "OD": load_mc(g, OD_REPORT),
         "OND": load_mc(g, OND_REPORT) if os.path.exists(OND_REPORT) else execute(g, s, **kw)}
    print("Overnight Drift:", OND_REPORT if os.path.exists(OND_REPORT) else "Python version")

    print("1. Overnight Drift (Python), per NQ after $7.25 costs")
    var = {"as specified (stop 30% ATR, out 3:00)": {},
           "stop 20% ATR": dict(stop_atr=0.20), "stop 50% ATR": dict(stop_atr=0.50),
           "no stop": dict(stop_atr=1e3), "out 2:00": dict(exit=200), "out 2:30": dict(exit=230),
           "out 4:00": dict(exit=400), "every night (not only after down days)": dict(down_only=False)}
    rows = {}
    for name, v in var.items():
        s, kw = overnight_drift24(g, **v)
        t = execute(g, s, **kw)
        rows[name] = summary(t)
        rows[name]["years_positive"] = int((t.groupby(pd.DatetimeIndex(t["date"]).year).net.mean() > 0).sum())
    print(pd.DataFrame(rows).T.to_string())
    t = T["OND"]
    print("By year:", t.groupby(pd.DatetimeIndex(t["date"]).year).net.mean().round().to_dict())
    tr = g.trading
    daily = pd.DataFrame({k: paths(g, T[k])[1][tr][:, -1] for k in NAMES})
    print("Correlation of daily P&L"); print(daily.corr().round(2).to_string())

    B = Book(g, T)
    for H in (250, 500):
        print(f"\n2. Performance Accounts, payouts within {H} trading days ({'1 year' if H == 250 else '2 years'});"
              " starts on every day with that many days after it")
        show(pd.DataFrame({k: row(B.run(p, H)) for k, p in PLANS.items()}).T)

    print("\n3. No edge (each strategy's average trade removed), 1 year")
    Z = Book(g, {k: zero_edge(v) for k, v in T.items()})
    show(pd.DataFrame({k: row(Z.run(PLANS[k], 250)) for k in
                       ("Challenge plan (VB 8, ONB $1,100)", "Balanced: VB 3, ONB $300, OND $500")}).T)

    print("\n4. Payout timing, Balanced plan, 1 year")
    bal = PLANS["Balanced: VB 3, ONB $300, OND $500"]
    show(pd.DataFrame({f"keep ${k:,} above the cap": row(B.run(bal, 250, keep=k)) for k in (0, 500, 1000, 2000)}).T)
    show(pd.DataFrame({"no consistency rule (for comparison)": row(B.run(bal, 250, consistency=False))}).T)

    print(f"\n5. Per challenge bought (pass rate {PASS_RATE:.0%}, ${FEE} fee), funded payouts within 1 year")
    for k in ("Challenge plan (VB 8, ONB $1,100)", "Balanced: VB 3, ONB $300, OND $500"):
        e = B.run(PLANS[k], 250)["paid"].mean()
        print(f"  {k:<40} ${PASS_RATE * e - FEE:,.0f} per challenge, ${e - FEE / PASS_RATE:,.0f} per funded account")
