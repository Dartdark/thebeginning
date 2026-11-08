"""Parameter-cluster robustness (2026-10-12): instead of the single best combination, group the
good combinations into clusters and use the tested combination nearest each cluster centre (medoid).

grid_scores(rows) -> DataFrame of parameters + design (2018-22) and holdout (2023-26) metrics
cluster_top(df, params, score, top=0.2, k=5) -> clusters of the top fraction by `score`
  (parameters scaled to 0-1 over the grid), each with size, spread and its medoid.
"""
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, "analysis")
import metrics as M

TICK_USD = 5.0          # 1 tick of NQ


def trade_net(t):
    slips = 1 + (t["kind"] != 1).astype(int)
    return t["net"] - slips * TICK_USD


def period_metrics(t, all_days, lo, hi):
    d = pd.DatetimeIndex(t["date"])
    m = (d >= lo) & (d < hi)
    x = trade_net(t)[m]
    daily = x.groupby(d[m]).sum().reindex(all_days[(all_days >= lo) & (all_days < hi)], fill_value=0.0)
    r = M.perf(daily, trades=x)
    r["t"] = x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 1 else np.nan
    return r


def kmeans(X, k, n_init=20, iters=100, seed=0):
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(n_init):
        C = X[rng.choice(len(X), k, replace=False)]
        for _ in range(iters):
            lab = np.argmin(((X[:, None, :] - C[None]) ** 2).sum(2), 1)
            newC = np.array([X[lab == i].mean(0) if (lab == i).any() else C[i] for i in range(k)])
            if np.allclose(newC, C):
                break
            C = newC
        inertia = ((X - C[lab]) ** 2).sum()
        if best is None or inertia < best[0]:
            best = (inertia, lab, C)
    return best[1], best[2]


def cluster_top(df, params, score, top=0.2, k=5, min_trades=None, trades_col=None):
    d = df.copy()
    if min_trades and trades_col:
        d = d[d[trades_col] >= min_trades]
    d = d.replace([np.inf, -np.inf], np.nan).dropna(subset=[score])
    sel = d[d[score] >= d[score].quantile(1 - top)].copy()
    lo, hi = df[params].min(), df[params].max()
    X = ((sel[params] - lo) / (hi - lo).replace(0, 1)).to_numpy(float)
    k = min(k, len(sel))
    lab, C = kmeans(X, k)
    sel["cluster"] = lab
    out = []
    for i in range(k):
        mem = sel[sel.cluster == i]
        Xi = X[lab == i]
        med = mem.iloc[np.argmin(((Xi - C[i]) ** 2).sum(1))]
        out.append(dict(cluster=i, size=len(mem), score_mean=mem[score].mean(), score_sd=mem[score].std(),
                        **{f"{p}_range": f"{mem[p].min():g}-{mem[p].max():g}" for p in params},
                        **{f"medoid_{p}": med[p] for p in params}, medoid_index=med.name))
    return pd.DataFrame(out).sort_values("size", ascending=False), sel
