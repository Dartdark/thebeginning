"""VIX regime filter (Zarattini, Mele & Aziz 2025, "The Volatility Edge") tested
on the NQ strategies, mainly Vault Break.

The paper times short-volatility positions with two daily signals:
  eVRP  = VIX - expected realized volatility (10-day realized vol of SPY)
  BoC   = backwardation or contango: VIX above or below VIX3M
and splits days into four regimes:
  short vol   eVRP > 0 and contango      (calm, insurance overpriced)
  half short  eVRP <= 0 and contango
  long vol    eVRP <= 0 and backwardation (stress building)
  cash        eVRP > 0 and backwardation
Here each NQ trade day gets the regime known at the PREVIOUS day's close.

Data: daily VIX closes from data/VIX_daily.csv (CBOE history via the public
datasets/finance-vix repository). VIX3M and SPY were not downloadable from
here, so two stand-ins are used (replace them when the real series are in
data/, see load_features):
  - realized vol: NQ's 10-day close-to-close vol (15:00 CT closes) x 0.8,
    because NQ is about 1.25x as volatile as the S&P 500
  - backwardation: VIX more than 10% above its own 20-day average
    (28% of days, more often than true VIX > VIX3M, which is about 10-15%)

Prints, per strategy: results by regime and by VIX quartile, Vault Break's
regime split by year, and the effect on the challenge (combined account) and
the funded phase of trading Vault Break smaller or not at all in the weak
regimes.

Usage (from the repo root): python3 analysis/vix_regime.py   (about 2 minutes)
"""
import os
import sys
import warnings
import numpy as np
import pandas as pd
sys.path.insert(0, "analysis")
warnings.filterwarnings("ignore")
from grid import execute
from grid24 import Grid24, jof
from portfolio import load_mc, paths, challenge
from candidates24 import overnight_drift24
from multi_strategy24 import VB_REPORT, ONB_REPORT, OD_REPORT, risk_sized
import funded_sim as F

VIX_FILE = "data/VIX_daily.csv"
VIX3M_FILE = "data/VIX3M_daily.csv"       # optional: DATE,CLOSE (replaces the stand-in)
SPY_FILE = "data/SPY_daily.csv"           # optional: DATE,CLOSE (replaces the stand-in)
RV_SCALE = 0.8
REGIMES = ["short vol", "half short", "long vol", "cash"]


def load_features(g):
    """Regime inputs known at the close of the previous trading day."""
    tr = g.trading
    dates = pd.DatetimeIndex(g.ts[tr])
    C = pd.DataFrame(g.c).ffill(axis=1).to_numpy()
    nq = pd.Series(C[tr, jof(1500)], index=dates)
    vix = pd.read_csv(VIX_FILE, parse_dates=["DATE"]).set_index("DATE")["CLOSE"].reindex(dates, method="ffill")
    if os.path.exists(SPY_FILE):
        spy = pd.read_csv(SPY_FILE, parse_dates=["DATE"]).set_index("DATE")["CLOSE"].reindex(dates, method="ffill")
        rv = np.log(spy).diff().rolling(10).std() * np.sqrt(252) * 100
    else:
        rv = np.log(nq).diff().rolling(10).std() * np.sqrt(252) * 100 * RV_SCALE
    if os.path.exists(VIX3M_FILE):
        v3 = pd.read_csv(VIX3M_FILE, parse_dates=["DATE"]).set_index("DATE")["CLOSE"].reindex(dates, method="ffill")
        back = vix > v3
    else:
        back = vix > 1.10 * vix.rolling(20).mean()
    f = pd.DataFrame({"vix": vix, "evrp": vix - rv, "back": back}).shift(1)
    f["back"] = f["back"].astype(bool)
    pos = f.evrp > 0
    f["regime"] = np.select([pos & ~f.back, ~pos & ~f.back, ~pos & f.back], REGIMES[:3], REGIMES[3])
    f.loc[f.evrp.isna(), "regime"] = "n/a"
    return f


def stats(x):
    w, l = x[x > 0].sum(), -x[x < 0].sum()
    return dict(trades=len(x), avg=round(x.mean()) if len(x) else np.nan,
                pf=round(w / l, 2) if l > 0 else np.nan, win=f"{(x > 0).mean():.0%}" if len(x) else "")


if __name__ == "__main__":
    g = Grid24()
    f = load_features(g)
    print("Stand-ins:", "SPY file" if os.path.exists(SPY_FILE) else f"NQ 10-day vol x {RV_SCALE}", "|",
          "VIX3M file" if os.path.exists(VIX3M_FILE) else "VIX > 1.1 x its 20-day average")
    print("Share of days per regime:", f.regime.value_counts(normalize=True).round(2).to_dict())
    s, kw = overnight_drift24(g)
    T = {"VB": load_mc(g, VB_REPORT), "ONB": load_mc(g, ONB_REPORT), "OD": load_mc(g, OD_REPORT),
         "OND": execute(g, s, **kw)}
    for k, t in T.items():
        r = f.reindex(pd.DatetimeIndex(t["date"])).reset_index(drop=True)
        net = t["net"].reset_index(drop=True)
        rows = {"all": stats(net)}
        for reg in REGIMES:
            rows[reg] = stats(net[r.regime == reg])
        q = pd.qcut(r.vix, 4)
        for i, c in enumerate(q.cat.categories):
            rows[f"VIX {c.left:.0f}-{c.right:.0f}"] = stats(net[q == c])
        print(f"\n{k}, per NQ after costs, by the previous close's regime")
        print(pd.DataFrame(rows).T.to_string())

    t = T["VB"]
    r = f.reindex(pd.DatetimeIndex(t["date"]))
    y = pd.DatetimeIndex(t["date"]).year
    tab = pd.DataFrame({"short vol": t.net.values[r.regime.values == "short vol"],
                        }).T
    by = pd.DataFrame({"year": y, "reg": r.regime.values, "net": t.net.values})
    print("\nVault Break average trade by year: short-vol regime vs the rest")
    piv = by.assign(g=np.where(by.reg == "short vol", "short vol", "other")).pivot_table(
        index="year", columns="g", values="net", aggfunc=["mean", "count"]).round(0)
    print(piv.to_string())

    # ---- account tests: Vault Break size by regime ----
    tr = g.trading
    reg_day = f.regime.values
    D = len(tr)
    P = {k: paths(g, v) for k, v in (("VB", T["VB"]), ("ONB", risk_sized(g, T["ONB"], 1100)))}
    W = {k: (P[k][0][tr], P[k][1][tr]) for k in P}

    def vb_mult(rule):
        m = np.ones(D)
        if rule == "skip cash":
            m[reg_day == "cash"] = 0
        elif rule == "half cash + half short":
            m[(reg_day == "cash") | (reg_day == "half short")] = 0.5
        elif rule == "skip cash + half short":
            m[(reg_day == "cash") | (reg_day == "half short")] = 0
        return m

    RULES = ["none", "skip cash", "half cash + half short", "skip cash + half short"]
    yr = pd.DatetimeIndex(g.ts[tr]).year
    print("\nChallenge, one account: Vault Break 8 MNQ (sized by regime) + Overnight Bias $1,100")
    for rule in RULES:
        m = np.floor(8 * vb_mult(rule)) / 10
        w = W["VB"][0] * m[:, None] + W["ONB"][0]
        rr = W["VB"][1] * m[:, None] + W["ONB"][1]
        res = [challenge(w, rr, np.arange(s0, min(s0 + 21, D))) for s0 in range(D)]
        o = np.array([np.nan if x is None else float(x[0] == "pass") for x in res])
        print(f"  {rule:<26} pass {np.nanmean(o):.1%}  2018-22 {np.nanmean(o[yr < 2023]):.1%}"
              f"  2023-26 {np.nanmean(o[yr >= 2023]):.1%}")

    print("\nFunded (Balanced plan: VB 3, ONB $300, OND $500), payouts within 1 year")
    from funded24 import Book, PLANS
    B = Book(g, T)
    bal = PLANS["Balanced: VB 3, ONB $300, OND $500"]
    for rule in RULES:
        b = B.base(bal)
        b[0] = 3 * vb_mult(rule)
        st = np.arange(0, B.D - 250)
        res = F.simulate_sized(B.W, B.C, b, horizon=250, starts=st)
        p = res["paid"]; ys = B.yr[st]
        print(f"  {rule:<26} expected ${p.mean():,.0f}  starts 2018-22 ${p[ys < 2023].mean():,.0f}"
              f"  2023+ ${p[ys >= 2023].mean():,.0f}  blown {res['blown'].mean():.0%}")
