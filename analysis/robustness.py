"""Robustness checks for parameter grids (2026-10-12), used with param_clusters.py.

fold_table(P, DL, days, folds) : re-optimize on overlapping time folds; for each fold the best
    combination and the percentile rank of chosen settings -> is the optimum stable over time?
sensitivity(P, DL, days, center, params) : one parameter at a time around `center`, others fixed
    -> smooth / flat curves = robust, sharp drops between neighbours = overfit.
Score = Calmar on daily $ P&L (annual $ / max drawdown $), plus Sharpe.
"""
import numpy as np
import pandas as pd


def calmar_rows(DL, mask):
    X = DL[:, mask].astype(float)
    eq = np.cumsum(X, 1)
    dd = (np.maximum.accumulate(np.maximum(eq, 0), 1) - eq).max(1)
    annual = X.sum(1) / (mask.sum() / 252.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(dd > 0, annual / dd, np.nan)


def sharpe_rows(DL, mask):
    X = DL[:, mask].astype(float)
    sd = X.std(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(sd > 0, X.mean(1) / sd * np.sqrt(252), np.nan)


def find(P, center):
    m = np.ones(len(P), bool)
    for k, v in center.items():
        m &= np.isclose(P[k].to_numpy(float), v)
    return np.nonzero(m)[0][0]


def fold_table(P, DL, days, folds, params, chosen):
    rows = []
    for lo, hi in folds:
        mask = (days.year >= lo) & (days.year <= hi)
        c = calmar_rows(DL, mask)
        b = int(np.nanargmax(c))
        r = {"fold": f"{lo}-{hi}", **{f"best {p}": P.iloc[b][p] for p in params}, "best calmar": c[b]}
        for name, ctr in chosen.items():
            i = find(P, ctr)
            r[f"{name} calmar"] = c[i]
            r[f"{name} pct"] = np.nanmean(c < c[i])
        rows.append(r)
    return pd.DataFrame(rows)


def sensitivity(P, DL, days, center, params, years=(2018, 2026)):
    mask = (days.year >= years[0]) & (days.year <= years[1])
    c = calmar_rows(DL, mask); s = sharpe_rows(DL, mask)
    out = {}
    for p in params:
        m = np.ones(len(P), bool)
        for q in params:
            if q != p:
                m &= np.isclose(P[q].to_numpy(float), center[q])
        idx = np.nonzero(m)[0]
        idx = idx[np.argsort(P.iloc[idx][p].to_numpy(float))]
        out[p] = pd.DataFrame({p: P.iloc[idx][p].to_numpy(), "calmar": c[idx], "sharpe": s[idx]})
    return out
