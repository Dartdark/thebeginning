"""Standard performance metrics for every strategy test (adopted 2026-10-12).

perf(daily_pnl, trades=None, capital=50_000) -> dict
  daily_pnl  $ P&L per trading day (pandas Series indexed by date, 0 on days without a trade)
  trades     optional $ P&L per trade (for profit factor and win rate per trade)
  capital    account size the drawdown percentages are measured against (Apex 50K)

Definitions (daily data, 252 trading days a year, risk-free rate 0 since these are futures):
  Sharpe        mean(daily) / sd(daily) x sqrt(252)
  Sortino       mean(daily) / downside deviation x sqrt(252),
                downside deviation = sqrt(mean(min(daily, 0)^2)) over all days
  Profit factor gross profit / gross loss, per trade if trades are given, else per day
  Calmar        average annual $ P&L / max drawdown $ (equity peak to trough)
  Ulcer index   sqrt(mean(drawdown_pct^2)), drawdown_pct = (equity - running peak) / running peak
                x 100, equity = capital + cumulative P&L. Lower is better.
  Ulcer perf.   (annual return % on capital) / Ulcer index (Martin ratio)
"""
import numpy as np
import pandas as pd


def perf(daily, trades=None, capital=50_000.0):
    d = pd.Series(daily, dtype=float).fillna(0.0)
    n = len(d)
    years = n / 252.0
    mu, sd = d.mean(), d.std()
    downside = np.sqrt(np.mean(np.minimum(d.to_numpy(), 0.0) ** 2))
    eq = capital + d.cumsum()
    peak = eq.cummax()
    dd = eq - peak
    dd_pct = dd / peak * 100.0
    maxdd = -dd.min()
    ulcer = float(np.sqrt(np.mean(dd_pct.to_numpy() ** 2)))
    annual = d.sum() / years if years else np.nan
    x = pd.Series(trades, dtype=float) if trades is not None else d[d != 0]
    gp, gl = x[x > 0].sum(), -x[x < 0].sum()
    return dict(
        trades=int(len(x)),
        win=float((x > 0).mean()) if len(x) else np.nan,
        avg=float(x.mean()) if len(x) else np.nan,
        annual=float(annual),
        sharpe=float(mu / sd * np.sqrt(252)) if sd > 0 else np.nan,
        sortino=float(mu / downside * np.sqrt(252)) if downside > 0 else np.nan,
        profit_factor=float(gp / gl) if gl > 0 else np.inf,
        max_dd=float(maxdd),
        calmar=float(annual / maxdd) if maxdd > 0 else np.inf,
        ulcer=ulcer,
        ulcer_perf=float((annual / capital * 100.0) / ulcer) if ulcer > 0 else np.inf,
    )


def table(rows, capital=50_000.0):
    """rows: {name: (daily, trades_or_None)} -> formatted DataFrame."""
    df = pd.DataFrame({k: perf(v[0], v[1], capital) for k, v in rows.items()}).T
    fmt = {"trades": "{:.0f}".format, "win": "{:.0%}".format, "avg": "${:,.0f}".format,
           "annual": "${:,.0f}".format, "sharpe": "{:.2f}".format, "sortino": "{:.2f}".format,
           "profit_factor": "{:.2f}".format, "max_dd": "${:,.0f}".format, "calmar": "{:.2f}".format,
           "ulcer": "{:.2f}".format, "ulcer_perf": "{:.2f}".format}
    return df.to_string(formatters=fmt)


# ---------------------------------------------------------------------------------------------------------------------
# Multiple testing (added 2026-10-15). Every idea ever tested is a trial (TRIALS.csv, built from TIER_LIST.md by
# analysis/trials.py). The more trials, the higher the bar for calling the best one real.
#
# psr(x, sr0)            Probabilistic Sharpe ratio (Bailey & Lopez de Prado 2012): P(true per-period Sharpe > sr0), using
#                        the sample's length, skew and kurtosis.
# expected_max_sr(n, T)  Sharpe (per period) the best of n trials of PURE NOISE reaches on T observations
#                        (Bailey, Borwein, Lopez de Prado & Zhu 2014): sqrt(V) x [(1 - g) z(1 - 1/n) + g z(1 - 1/(n e))],
#                        g = 0.5772 (Euler), V = 1 / (T - 1) the variance of a zero-edge Sharpe estimate.
# deflated_sharpe(x, n)  DSR = psr(x, expected_max_sr(n, len(x))): probability the strategy beats the best of n noise trials.
#                        >= 0.95 passes. Conservative when n counts trials of unrelated ideas.
# t_threshold(n)         |t| a single result needs when it is the best of n tests (Bonferroni, one-sided 5%): for filters and
#                        splits, where a return series is not the thing tested.
# ---------------------------------------------------------------------------------------------------------------------
from statistics import NormalDist

_N = NormalDist()
EULER = 0.5772156649


def psr(x, sr0=0.0):
    x = pd.Series(x, dtype=float).dropna(); T = len(x)
    if T < 10 or x.std() == 0: return np.nan
    sr = x.mean() / x.std(); g3 = float(((x - x.mean()) ** 3).mean() / x.std() ** 3)
    g4 = float(((x - x.mean()) ** 4).mean() / x.std() ** 4)
    den = np.sqrt(max(1e-12, 1 - g3 * sr + (g4 - 1) / 4 * sr ** 2))
    return _N.cdf((sr - sr0) * np.sqrt(T - 1) / den)


def expected_max_sr(n, T):
    if n <= 1: return 0.0
    v = 1.0 / (T - 1)
    return np.sqrt(v) * ((1 - EULER) * _N.inv_cdf(1 - 1 / n) + EULER * _N.inv_cdf(1 - 1 / (n * np.e)))


def deflated_sharpe(x, n):
    x = pd.Series(x, dtype=float).dropna()
    return psr(x, expected_max_sr(n, len(x)))


def t_threshold(n, alpha=0.05):
    return _N.inv_cdf(1 - alpha / max(1, n))
