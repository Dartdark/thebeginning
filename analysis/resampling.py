"""Bootstrap and permutation tests on daily P&L (adopted 2026-10-12).

bootstrap(daily, n=5000, block=10, seed=1, capital=50_000) -> DataFrame
  Moving-block bootstrap: rebuild the period from random blocks of `block` consecutive
  trading days (blocks keep short streaks and volatility clusters together), n times.
  Returns the 5% / 50% / 95% values of Sharpe, Sortino, profit factor (per day), Calmar,
  Ulcer index, max drawdown $ and annual $, plus the actual value. Answers "how sure are we
  of this number?" -- a 90% interval whose low end is still good means the edge is not luck
  of a few days.

permutation(daily, n=5000, seed=1, limits=(1000, 2000, 3000)) -> dict
  Shuffle the order of the same days n times (total P&L unchanged) and record the max
  drawdown of each order. Returns the actual max DD, its percentile among the shuffles
  (low = the real history was kinder than most orders), the 50% / 95% / 99% shuffled DD,
  and P(max DD >= each limit) -- with limits in $ such as the Apex $2,000 trailing drawdown.
  Answers "how bad could the drawdown have been with the very same days?".

window_risk(daily, window=60, limit=2000, n=500, seed=1) -> dict
  Apex version of the permutation test. For every start day, the max drawdown inside the
  next `window` trading days; returns the share of windows that reach `limit` in the real
  day order and on average over n shuffles. Real > shuffled means losing days cluster
  (streaks), so the i.i.d. challenge simulator (portfolio.random_days) understates the risk;
  real < shuffled means the history was kinder than a random order.

Same definitions as metrics.perf (252 days a year, drawdown % against $50,000).
Use on the 2023-2026 holdout (out of sample) and on the full 2018-2026 period.
"""
import numpy as np
import pandas as pd


def _stats(X, capital):
    """Metrics for each row of X (samples x days)."""
    T = X.shape[1]
    mu, sd = X.mean(1), X.std(1, ddof=1)
    down = np.sqrt((np.minimum(X, 0.0) ** 2).mean(1))
    eq = capital + X.cumsum(1)
    peak = np.maximum.accumulate(eq, 1)
    dd = eq - peak
    maxdd = -dd.min(1)
    ulcer = np.sqrt(((dd / peak * 100.0) ** 2).mean(1))
    annual = X.sum(1) / (T / 252.0)
    gp, gl = np.where(X > 0, X, 0).sum(1), -np.where(X < 0, X, 0).sum(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return dict(sharpe=mu / sd * np.sqrt(252), sortino=mu / down * np.sqrt(252),
                    pf_day=gp / gl, calmar=annual / maxdd, ulcer=ulcer, max_dd=maxdd, annual=annual)


def max_dd(daily):
    eq = np.cumsum(np.asarray(daily, float))
    return float(-(eq - np.maximum.accumulate(np.maximum(eq, 0.0))).min())


def bootstrap(daily, n=5000, block=10, seed=1, capital=50_000.0, chunk=1000):
    x = pd.Series(daily, dtype=float).fillna(0.0).to_numpy()
    T = len(x); rng = np.random.default_rng(seed)
    nb = int(np.ceil(T / block)); out = {}
    for s in range(0, n, chunk):
        m = min(chunk, n - s)
        starts = rng.integers(0, T - block + 1, (m, nb))
        idx = (starts[:, :, None] + np.arange(block)).reshape(m, -1)[:, :T]
        for k, v in _stats(x[idx], capital).items():
            out.setdefault(k, []).append(v)
    out = {k: np.concatenate(v) for k, v in out.items()}
    actual = {k: v[0] for k, v in _stats(x[None, :], capital).items()}
    rows = {k: dict(actual=actual[k], p5=np.nanpercentile(v, 5), p50=np.nanpercentile(v, 50),
                    p95=np.nanpercentile(v, 95)) for k, v in out.items()}
    df = pd.DataFrame(rows).T
    df.attrs["p_sharpe_le_0"] = float(np.mean(out["sharpe"] <= 0))
    return df


def permutation(daily, n=5000, seed=1, limits=(1000, 2000, 3000), chunk=1000):
    x = pd.Series(daily, dtype=float).fillna(0.0).to_numpy()
    x = x[x != 0]                      # only days with P&L matter for the order
    rng = np.random.default_rng(seed); dds = []
    for s in range(0, n, chunk):
        m = min(chunk, n - s)
        X = x[np.argsort(rng.random((m, len(x))), 1)]
        eq = X.cumsum(1)
        dds.append(-(eq - np.maximum.accumulate(np.maximum(eq, 0.0), 1)).min(1))
    dds = np.concatenate(dds); a = max_dd(x)
    res = dict(actual_dd=a, pct_rank=float(np.mean(dds < a)), dd50=float(np.percentile(dds, 50)),
               dd95=float(np.percentile(dds, 95)), dd99=float(np.percentile(dds, 99)))
    for L in limits:
        res[f"P(dd>={L})"] = float(np.mean(dds >= L))
    return res


def _window_hit(x, window, limit):
    """Share of start days whose max drawdown within the next `window` days reaches `limit`.
    x: (samples x days)."""
    eq = np.concatenate([np.zeros((x.shape[0], 1)), x.cumsum(1)], 1)
    W = np.lib.stride_tricks.sliding_window_view(eq, window + 1, axis=1)   # samples x starts x w+1
    dd = (W - np.maximum.accumulate(W, 2)).min(2)
    return (-dd >= limit).mean(1)


def window_risk(daily, window=60, limit=2000, n=500, seed=1, chunk=50):
    x = pd.Series(daily, dtype=float).fillna(0.0).to_numpy()
    rng = np.random.default_rng(seed); sh = []
    for s in range(0, n, chunk):
        m = min(chunk, n - s)
        sh.append(_window_hit(x[np.argsort(rng.random((m, len(x))), 1)], window, limit))
    sh = np.concatenate(sh)
    return dict(real=float(_window_hit(x[None, :], window, limit)[0]), shuffled=float(sh.mean()),
                shuffled_p5=float(np.percentile(sh, 5)), shuffled_p95=float(np.percentile(sh, 95)))


def report(rows, n=5000, block=10, limits=(1000, 2000, 3000), capital=50_000.0):
    """rows: {name: daily} -> (bootstrap table, permutation table) as strings."""
    b, p = [], {}
    for name, d in rows.items():
        t = bootstrap(d, n, block, capital=capital)
        for k in ("sharpe", "sortino", "pf_day", "calmar", "ulcer", "max_dd"):
            r = t.loc[k]
            b.append(dict(name=name, metric=k, actual=r.actual, p5=r.p5, p50=r.p50, p95=r.p95))
        b.append(dict(name=name, metric="P(Sharpe<=0)", actual=np.nan, p5=np.nan,
                      p50=t.attrs["p_sharpe_le_0"], p95=np.nan))
        p[name] = permutation(d, n, limits=limits)
    B = pd.DataFrame(b).set_index(["name", "metric"])
    P = pd.DataFrame(p).T
    fmtP = {c: ("${:,.0f}".format if c.startswith("dd") or c == "actual_dd" else "{:.0%}".format) for c in P}
    return B.to_string(float_format=lambda v: f"{v:,.2f}"), P.to_string(formatters=fmtP)


def fan_paths(daily, kind="bootstrap", n=2000, block=10, seed=1):
    """Equity paths for the fan charts: 'bootstrap' (block resample, ends spread out) or
    'permutation' (shuffled order, every path ends at the same total). Returns (n x days)."""
    x = pd.Series(daily, dtype=float).fillna(0.0).to_numpy(); T = len(x)
    rng = np.random.default_rng(seed)
    if kind == "permutation":
        X = x[np.argsort(rng.random((n, T)), 1)]
    else:
        nb = int(np.ceil(T / block)); starts = rng.integers(0, T - block + 1, (n, nb))
        X = x[(starts[:, :, None] + np.arange(block)).reshape(n, -1)[:, :T]]
    return X.cumsum(1)


def fan_chart(daily, title, path, n=2000, block=10, limit=None):
    """Two panels like the slides: bootstrap and permutation equity fans
    (1-99%, 5-95% and 25-75% bands, median), with the real equity in red."""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    d = pd.Series(daily, dtype=float).fillna(0.0); real = d.cumsum().to_numpy(); t = d.index
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor="#111")
    for ax, kind in zip(axes, ("bootstrap", "permutation")):
        E = fan_paths(d, kind, n, block)
        q = np.percentile(E, [1, 5, 25, 50, 75, 95, 99], 0)
        ax.set_facecolor("#1a1d2b")
        ax.fill_between(t, q[0], q[6], color="#6a3fb5", alpha=.35, label="1-99%")
        ax.fill_between(t, q[1], q[5], color="#4b4fc9", alpha=.45, label="5-95%")
        ax.fill_between(t, q[2], q[4], color="#3a6fd8", alpha=.45, label="25-75%")
        ax.plot(t, q[3], color="#8fb3ff", lw=1, label="median")
        ax.plot(t, real, color="#ff3b5c", lw=1.6, label="real")
        ax.axhline(0, color="#888", lw=.6)
        if kind == "permutation":
            dd = -(E - np.maximum.accumulate(np.maximum(E, 0), 1)).min(1)
            rdd = float(-(real - np.maximum.accumulate(np.maximum(real, 0))).min())
            sub = (f"max DD real ${rdd:,.0f} | shuffled median ${np.median(dd):,.0f}, "
                   f"95% ${np.percentile(dd, 95):,.0f}")
            if limit: sub += f"\nreal DD smaller than {np.mean(dd > rdd):.0%} of shuffles"
        else:
            sub = (f"final P&L 5-95%: ${q[1][-1]:,.0f} to ${q[5][-1]:,.0f} "
                   f"(real ${real[-1]:,.0f}); P(loss) {np.mean(E[:, -1] <= 0):.0%}")
        ax.set_title(f"{kind.title()}\n{sub}".replace("$", r"\$"), color="w", fontsize=10)
        ax.tick_params(colors="#ccc"); ax.yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda v, _: f"${v/1000:,.0f}k"))
        for s in ax.spines.values(): s.set_color("#444")
        ax.legend(loc="upper left", fontsize=8, facecolor="#222", labelcolor="w", framealpha=.8)
    fig.suptitle(title.replace("$", r"\$"), color="w", fontsize=13); fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)
