"""Test bench for funded strategies: any set of trade lists -> expected Apex 50K
Performance Account payouts (rules in funded_sim.py).

Every strategy is stored per 1 MNQ-equivalent (1/10 of the trade list's
per-NQ P&L), after $7.25 per NQ costs plus 1 tick (0.25 point) of slippage
on every market or stop fill (column `slips` = number of slipped fills; if
missing: entry + any non-target exit = 1 + (kind != 1)).

A plan maps strategy name -> size:
  number            fixed MNQ per trade
  ("risk", dollars) whole MNQ so a stop-out loses at most `dollars`; needs
                    the strategy's per-day stop in points (add(..., stop_pts=))

  lab = Lab(g); lab.add("VB", vb_trades); lab.add("OND", ond, stop_pts=0.3 * atr)
  lab.score({"VB": 3, "OND": ("risk", 500)})

Usage of the scores: compare a candidate against the benchmark (the interim
funded plan, BENCHMARK) on expected payouts within 1 and 2 years.
"""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "analysis")
from portfolio import paths
import funded_sim as F

SLIP = 0.25
BENCHMARK = {"VB": 3, "ONB": ("risk", 300), "OND": ("risk", 500)}


def with_slippage(t):
    t = t.copy()
    if "slips" not in t:
        t["slips"] = 1 + (t["kind"] != 1)
    t["exit"] = t["exit"] - t["side"] * t["slips"] * SLIP
    return t


class Lab:
    def __init__(self, g):
        self.g = g
        self.tr = g.trading
        self.D = len(self.tr)
        self.yr = pd.DatetimeIndex(g.ts[self.tr]).year
        self.W, self.C, self.stop = {}, {}, {}

    def add(self, name, trades, stop_pts=None, slippage=True):
        """stop_pts: per-calendar-row stop distance in points (for risk sizing)."""
        t = with_slippage(trades) if slippage else trades
        w, r = paths(self.g, t)
        self.W[name] = w[self.tr] / 10
        self.C[name] = r[self.tr][:, -1] / 10
        if stop_pts is not None:
            self.stop[name] = np.nan_to_num(np.asarray(stop_pts)[self.tr], nan=1e12)
        return self

    def daily(self, name):
        return self.C[name] * 10            # $ per NQ per trading day

    def corr(self, names=None):
        names = names or list(self.C)
        return pd.DataFrame({k: self.C[k] for k in names}).corr()

    def _base(self, plan):
        names = list(plan)
        b = np.zeros((len(names), self.D))
        for i, (k, v) in enumerate(plan.items()):
            if isinstance(v, tuple) and v[0] == "risk":
                b[i] = v[1] / (self.stop[k] * 2.0)        # $2 per point per MNQ
            else:
                b[i] = v
        return names, b

    def score(self, plan, horizon=250, **kw):
        names, b = self._base(plan)
        W = np.stack([self.W[k] for k in names]); C = np.stack([self.C[k] for k in names])
        st = np.arange(0, self.D - horizon)
        r = F.simulate_sized(W, C, b, horizon=horizon, starts=st, **kw)
        y = self.yr[st]; p = r["paid"]
        f = r["first"][r["first"] > 0]
        return dict(expected=p.mean(), s2018_22=p[y < 2023].mean(), s2023_on=p[y >= 2023].mean(),
                    worst_year=pd.Series(p).groupby(y).mean().min(), blown=r["blown"].mean(),
                    any_payout=(r["payouts"] > 0).mean(), all_6=(r["payouts"] == 6).mean(),
                    days_to_1st=np.median(f) if len(f) else np.nan)

    def table(self, plans, horizon=250):
        df = pd.DataFrame({k: self.score(p, horizon) for k, p in plans.items()}).T
        fm = {c: "${:,.0f}".format for c in ("expected", "s2018_22", "s2023_on", "worst_year")}
        fm.update({c: "{:.0%}".format for c in ("blown", "any_payout", "all_6")})
        fm["days_to_1st"] = "{:.0f}".format
        return df.to_string(formatters=fm)
