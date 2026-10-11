"""Volatility-scaled position sizing for every strategy.

References:
  Moreira & Muir, "Volatility-Managed Portfolios" (Journal of Finance, 2017):
    weight = c / sigma^2 (previous month's realized variance)
  Harvey, Hoyle, Korgaonkar, Rattray, Sargaison & Van Hemert, "The Impact of
    Volatility Targeting" (Journal of Portfolio Management, 2018):
    weight = target vol / sigma (inverse volatility)

Volatility is NQ's own, in points (a contract's P&L is in points), known before
each day starts:
  RV21   square root of the average daily realized variance of 5-minute price
         changes (8:30-15:15 CT) over the previous 21 trading days
  ATR15  the 15-day average daily range the strategies already use
Weights are scaled to average 1 over the sample (so average size is the same
as fixed sizing; this constant does not change Sharpe ratios) and capped at
0.25x-3x, as leverage limits in both papers.

For each strategy (MultiCharts trade lists, per NQ, after costs):
  - risk-adjusted results of daily P&L with each sizing
  - Apex 50K pass rate at whole-MNQ sizes, base size chosen on 2018-2022 starts
And the Vault Break + Overnight Bias account with each sizing on Vault Break.

Usage (from the repo root): python3 analysis/vol_scaling.py   (about 3 minutes)
"""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "analysis")
from grid24 import Grid24, jof
from portfolio import load_mc, paths, challenge
from multi_strategy import V3_REPORT
from multi_strategy24 import VB_REPORT, OD_REPORT, ONB_REPORT

CAP = (0.25, 3.0)


def vol_estimates(g):
    """Per calendar row: RV21 and ATR15 in points, known before that day."""
    a, b = jof(830), jof(1515)
    c5 = g.c[:, a + 5:b + 1:5]                         # 5-minute closes 8:35..15:15
    rv = np.nansum(np.diff(c5, axis=1) ** 2, axis=1)   # daily realized variance, points^2
    tr = g.trading
    s = pd.Series(np.nan, index=range(g.D))
    s.iloc[tr] = rv[tr]
    rv21 = np.sqrt(s.iloc[tr].rolling(21).mean().shift(1))
    out = pd.Series(np.nan, index=range(g.D)); out.iloc[tr] = rv21.values
    return dict(RV21=out.ffill().to_numpy(), ATR15=g.daily_atr(15))


def weights(sig, kind):
    if kind == "fixed":
        return np.ones_like(sig)
    w = 1 / sig if kind == "inv_vol" else 1 / sig ** 2
    w = w / np.nanmean(w)
    return np.clip(w, *CAP)


def daily_stats(g, t, w):
    """Risk-adjusted results of daily P&L with per-day weights w (per NQ)."""
    tr = g.trading
    q = w[t["day"].to_numpy()]
    d = pd.Series(t["net"].to_numpy() * q).groupby(t["day"].to_numpy()).sum()
    d = d.reindex(tr, fill_value=0.0)
    yr = pd.DatetimeIndex(g.ts[tr]).year
    sh = lambda x: x.mean() / x.std() * np.sqrt(252)
    eq = d.cumsum(); dd = (eq.cummax() - eq).max()
    down = d[d < 0]
    return dict(sharpe=sh(d), sharpe_18_22=sh(d[yr < 2023]), sharpe_23_26=sh(d[yr >= 2023]),
                sortino=d.mean() / np.sqrt((down ** 2).sum() / len(d)) * np.sqrt(252),
                calmar=d.mean() * 252 / dd, worst_year=d.groupby(yr).sum().min(),
                losing_years=int((d.groupby(yr).sum() < 0).sum()))


def mnq_trades(t, w, base):
    """Whole-MNQ size per trade = round(base x weight); size-0 trades skipped."""
    t = t.copy()
    m = np.round(base * w[t["day"].to_numpy()])
    t["qty"] = m / 10.0
    return t[t["qty"] > 0].reset_index(drop=True)


def pass_rates(g, t, yr):
    w, r = paths(g, t)
    w, r = w[g.trading], r[g.trading]
    D = len(w)
    o = np.array([np.nan if x is None else float(x[0] == "pass")
                  for x in (challenge(w, r, np.arange(s, min(s + 21, D))) for s in range(D))])
    return np.nanmean(o), np.nanmean(o[yr < 2023]), np.nanmean(o[yr >= 2023]), \
        pd.Series(o).groupby(yr).mean().min()


if __name__ == "__main__":
    g = Grid24()
    V = vol_estimates(g)
    yr = pd.DatetimeIndex(g.ts[g.trading]).year
    T = {"V3": load_mc(g, V3_REPORT), "Vault Break": load_mc(g, VB_REPORT),
         "Opening Drive": load_mc(g, OD_REPORT), "Overnight Bias": load_mc(g, ONB_REPORT)}
    schemes = [("fixed", None)] + [(k, v) for k in ("inv_vol", "inv_var") for v in ("RV21", "ATR15")]
    W = {(k, v): weights(V[v] if v else np.ones(g.D), k) for k, v in schemes}
    label = lambda k, v: "fixed size" if k == "fixed" else \
        f"{'1/vol (Harvey et al.)' if k == 'inv_vol' else '1/variance (Moreira-Muir)'}, {v}"

    print("Risk-adjusted results of daily P&L (per NQ on average; weights average 1)")
    rows = []
    for name, t in T.items():
        for k, v in schemes:
            s = daily_stats(g, t, W[(k, v)])
            rows.append(dict(strategy=name, sizing=label(k, v), **s))
    df = pd.DataFrame(rows)
    pd.set_option("display.width", 250)
    print(df.to_string(index=False, formatters={
        "sharpe": "{:.2f}".format, "sharpe_18_22": "{:.2f}".format, "sharpe_23_26": "{:.2f}".format,
        "sortino": "{:.2f}".format, "calmar": "{:.2f}".format, "worst_year": "${:,.0f}".format}))

    print("\nApex 50K pass rate, whole MNQ, base size chosen on 2018-22 starts")
    BASES = {"V3": (6, 8, 10, 12), "Vault Break": (8, 10, 12, 15), "Opening Drive": (6, 8, 10, 12),
             "Overnight Bias": (4, 6, 8, 10)}
    best = {}
    for name, t in T.items():
        for k, v in schemes:
            res = [(b,) + pass_rates(g, mnq_trades(t, W[(k, v)], b), yr) for b in BASES[name]]
            b, p, pi, po, wy = max(res, key=lambda x: x[2])
            best[(name, k, v)] = b
            print(f"  {name:<15} {label(k, v):<36} base {b:>2} MNQ  pass {p:.0%}  2018-22 {pi:.0%}"
                  f"  2023-26 {po:.0%}  worst year {wy:.0%}")

    # Overnight Bias as traded: sized by its own stop ($1,100 risk); for reference
    from multi_strategy24 import risk_sized
    t = risk_sized(g, T["Overnight Bias"], 1100)
    p = pass_rates(g, t, yr)
    print(f"  {'Overnight Bias':<15} {'as traded: $1,100 risk (stop = 30% ATR)':<36}          pass {p[0]:.0%}"
          f"  2018-22 {p[1]:.0%}  2023-26 {p[2]:.0%}  worst year {p[3]:.0%}")
    s = pd.Series(t["net"].to_numpy()).groupby(t["day"].to_numpy()).sum().reindex(g.trading, fill_value=0)
    print(f"  (its daily Sharpe as traded: {s.mean() / s.std() * np.sqrt(252):.2f})")

    print("\nOne account: Vault Break (sizing as shown, base 8 MNQ) + Overnight Bias ($1,100 risk)")
    onb_w, onb_r = paths(g, t)
    for k, v in schemes:
        vb = mnq_trades(T["Vault Break"], W[(k, v)], 8)
        w1, r1 = paths(g, vb)
        w, r = (w1 + onb_w)[g.trading], (r1 + onb_r)[g.trading]
        D = len(w)
        o = np.array([np.nan if x is None else float(x[0] == "pass")
                      for x in (challenge(w, r, np.arange(s, min(s + 21, D))) for s in range(D))])
        print(f"  Vault Break {label(k, v):<36} pass {np.nanmean(o):.0%}  2018-22 {np.nanmean(o[yr < 2023]):.0%}"
              f"  2023-26 {np.nanmean(o[yr >= 2023]):.0%}  worst year {pd.Series(o).groupby(yr).mean().min():.0%}")
