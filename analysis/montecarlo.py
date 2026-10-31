"""Monte Carlo analysis for any strategy (added 2026-10-16, user: 'start integrating Monte Carlo analysis').

Two views, both from the strategy's own results (no model assumptions):
  trade_mc(pnl)   reshuffle the trade sequence (with replacement = bootstrap, or without = permutation): distribution of
                  the total, the max drawdown, the longest losing streak and the chance of a drawdown of a given size.
                  Answers 'how bad could the path have been with the same trades?'
  daily_mc(daily) block bootstrap of daily P&L over a horizon (keeps volatility clustering): distribution of the
                  horizon's P&L, its max drawdown, P(loss), and the chance an Apex-style end-of-day trailing drawdown is
                  hit (trailing from the highest end-of-day balance, locking at start + lock once reached).
                  return/DD = median P&L / median max DD (Davey's score; descriptive only). END-OF-DAY only: it misses
                  intraday dips through the limit, so Apex account decisions use funded_sim / prop_sim (intraday lows).
  report(...)     prints both as one compact block; used by every new test from 2026-10-16 (CLAUDE.md testing standard).
Usage:  import montecarlo as MC;  print(MC.report(pnl_series, daily_series, size=1))
"""
import numpy as np, pandas as pd


def _maxdd(cum):
    return (np.maximum.accumulate(np.concatenate([np.zeros((cum.shape[0], 1)), cum], 1), axis=1)[:, 1:] - cum).max(1)


def _streak(x):
    best = cur = 0
    for v in x:
        cur = cur + 1 if v <= 0 else 0; best = max(best, cur)
    return best


def trade_mc(pnl, n=10000, replace=True, seed=1, dd_levels=(1000, 2000, 5000)):
    x = np.asarray(pd.Series(pnl).dropna(), float); rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), (n, len(x))) if replace else np.argsort(rng.random((n, len(x))), 1)
    sims = x[idx]; cum = sims.cumsum(1); dd = _maxdd(cum)
    streaks = np.array([_streak(s) for s in sims[: min(n, 2000)]])
    e = np.r_[0, x.cumsum()]; actual_dd = (np.maximum.accumulate(e) - e).max()
    return dict(n_trades=len(x), total_p5=np.percentile(cum[:, -1], 5), total_p50=np.median(cum[:, -1]), total_p95=np.percentile(cum[:, -1], 95),
                p_loss=np.mean(cum[:, -1] <= 0), dd_actual=actual_dd, dd_p50=np.median(dd), dd_p95=np.percentile(dd, 95), dd_p99=np.percentile(dd, 99),
                dd_rank=np.mean(dd <= actual_dd), streak_actual=_streak(x), streak_p95=np.percentile(streaks, 95),
                **{f"p_dd_{k}": np.mean(dd >= k) for k in dd_levels})


def daily_mc(daily, horizon=252, n=5000, block=10, seed=1, trail=2000.0, lock=100.0):
    d = np.asarray(pd.Series(daily).fillna(0.0), float); rng = np.random.default_rng(seed)
    nb = int(np.ceil(horizon / block)); starts = rng.integers(0, len(d) - block, (n, nb))
    sims = (starts[:, :, None] + np.arange(block)).reshape(n, -1)[:, :horizon]; x = d[sims]; cum = x.cumsum(1)
    dd = _maxdd(cum)
    # Apex-style EOD trailing: floor = max(prev floor, min(peak EOD - trail, lock)); breach if cum <= floor (EOD check)
    peak = np.maximum.accumulate(np.concatenate([np.zeros((n, 1)), cum], 1), axis=1)[:, :-1]
    floor = np.minimum(peak - trail, lock); floor = np.maximum.accumulate(floor, axis=1)
    hit = (cum <= floor).any(1)
    return dict(horizon=horizon, pnl_p5=np.percentile(cum[:, -1], 5), pnl_p50=np.median(cum[:, -1]), pnl_p95=np.percentile(cum[:, -1], 95),
                p_loss=np.mean(cum[:, -1] <= 0), dd_p50=np.median(dd), dd_p95=np.percentile(dd, 95), p_trail_hit=np.mean(hit),
                ret_dd=np.median(cum[:, -1]) / max(np.median(dd), 1e-9))   # Davey's 'Monte Carlo return / drawdown' (median / median)


def report(pnl, daily=None, size=1.0, label="", trail=2000.0, horizon=252):
    """size multiplies P&L (e.g. 0.1 for one micro of a full-contract backtest)."""
    t = trade_mc(np.asarray(pnl) * size)
    s = (f"   Monte Carlo {label} (x{size:g}): trades {t['n_trades']} | total p5 ${t['total_p5']:,.0f} / p50 ${t['total_p50']:,.0f} / p95 ${t['total_p95']:,.0f}, "
         f"P(total <= 0) {t['p_loss']:.1%}\n"
         f"      max DD actual ${t['dd_actual']:,.0f} (rank {t['dd_rank']:.0%}), shuffled p50 ${t['dd_p50']:,.0f} / p95 ${t['dd_p95']:,.0f} / p99 ${t['dd_p99']:,.0f}; "
         f"losing streak actual {t['streak_actual']}, p95 {t['streak_p95']:.0f}")
    if daily is not None:
        dm = daily_mc(np.asarray(daily) * size, horizon=horizon, trail=trail)
        s += (f"\n      {horizon}-day block bootstrap: P&L p5 ${dm['pnl_p5']:,.0f} / p50 ${dm['pnl_p50']:,.0f} / p95 ${dm['pnl_p95']:,.0f}, "
              f"P(loss) {dm['p_loss']:.1%}, max DD p50 ${dm['dd_p50']:,.0f} / p95 ${dm['dd_p95']:,.0f}, return/DD {dm['ret_dd']:.2f}, P(hit ${trail:,.0f} trailing, EOD check only) {dm['p_trail_hit']:.1%}")
    return s


if __name__ == "__main__":
    rng = np.random.default_rng(0); x = rng.normal(50, 400, 500)
    print(report(x, pd.Series(np.where(rng.random(1000) < 0.5, rng.normal(50, 400, 1000), 0.0)), label="self-test"))
