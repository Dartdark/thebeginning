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
