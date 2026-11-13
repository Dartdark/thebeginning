"""Gate 2 of Boutgajouft (2026, SSRN 7525240, 'A Two-Gate Test for Structural Edge'): are a strategy's trade outcomes
distributed the same across partitions? Added to analysis/checker.py as G13 (user, 2026-11-08).
Per partition d with groups j = 1..K (each >= MIN_N trades):
  SIS_d = mean over group pairs of W1(F_j, F_k) / sd(all outcomes)        (paper eq. 7; W1 = Wasserstein-1, exact empirical)
  reference: the same statistic on N(0,1) draws with the observed group labels, B runs, 95th percentile (paper eq. 8)
  pass when SIS_d < reference for every evaluable partition (paper eq. 9).
Outcome = R-multiples (net / risk if trades.csv has 'risk', else net / trailing 50-trade sd, past-only).
Partitions here: P3 time = calendar years; P2 volatility = prior-day VIX above / below its expanding (past-only) median
(the paper used a full-sample VIX median, which is not known at the time); P1 instrument = the 'symbol' column if present.
Also printed (not gated): a label-permutation p-value, which does not assume normal outcomes (trade P&L is fat-tailed,
so the Gaussian reference can flag tail differences that are just noise; see the paper's own caveat).
"""
import numpy as np, pandas as pd

MIN_N, B = 20, 2000


def w1(a, b):
    """Exact Wasserstein-1 between two empirical distributions (integral of |F_a - F_b|)."""
    a = np.sort(a); b = np.sort(b); z = np.sort(np.concatenate([a, b]))
    if len(z) < 2: return 0.0
    Fa = np.searchsorted(a, z[:-1], side="right") / len(a); Fb = np.searchsorted(b, z[:-1], side="right") / len(b)
    return float(np.sum(np.abs(Fa - Fb) * np.diff(z)))


def sis(x, lab):
    g = [x[lab == u] for u in np.unique(lab)]; K = len(g); sd = x.std(ddof=1)
    if K < 2 or sd == 0: return np.nan
    d = [w1(g[i], g[j]) for i in range(K) for j in range(i + 1, K)]
    return float(np.mean(d) / sd)


def partition_test(x, lab, seed=1):
    x = np.asarray(x, float); lab = np.asarray(lab)
    keep = np.isin(lab, [u for u, c in zip(*np.unique(lab, return_counts=True)) if c >= MIN_N])
    x, lab = x[keep], lab[keep]
    if len(np.unique(lab)) < 2: return None
    s = sis(x, lab); rng = np.random.default_rng(seed)
    ref = np.array([sis(rng.standard_normal(len(x)), lab) for _ in range(B)])
    perm = np.array([sis(x, rng.permutation(lab)) for _ in range(B)])
    return dict(sis=s, tau=float(np.percentile(ref, 95)), p_perm=float(np.mean(perm >= s)), groups=len(np.unique(lab)), n=len(x))


def vix_regime(dates, path="data/VIX_daily.csv"):
    v = pd.read_csv(path); c = [k for k in v.columns if k.lower() in ("close", "vix", "adj close")][0]
    dc = [k for k in v.columns if "date" in k.lower()][0]
    s = pd.Series(v[c].to_numpy(float), index=pd.to_datetime(v[dc])).sort_index()
    prev = s.shift(1); med = s.expanding(250).median().shift(1)
    hi = (prev > med).reindex(pd.DatetimeIndex(dates), method="ffill")
    return np.where(hi.isna(), "na", np.where(hi.astype(bool), "high", "low"))


def r_multiples(T, w=50):
    """Outcomes in risk units, as the paper's R-multiples: net / risk when trades.csv has a 'risk' column ($ at the stop);
    otherwise net / the strategy's own trailing (past-only) standard deviation of the last w trades. Dollar P&L grows with
    the price level and volatility (NQ 2018 vs 2026), so raw dollars differ by year and VIX regime for every strategy."""
    if "risk" in T and (T.risk > 0).all(): return (T.net / T.risk).to_numpy(float), "net / risk"
    sd = T.net.shift(1).rolling(w, min_periods=w).std()
    return (T.net / sd).to_numpy(float), f"net / trailing {w}-trade sd"


def gate2(T):
    """T: DataFrame with date, net (optional risk, symbol). Returns (pass, text, rows)."""
    T = T.sort_values("date").reset_index(drop=True).copy(); T["date"] = pd.to_datetime(T.date)
    x, how = r_multiples(T); ok_ = np.isfinite(x); T = T[ok_].reset_index(drop=True); x = x[ok_]; rows = {}
    rows["P3 time (years)"] = partition_test(x, T.date.dt.year.to_numpy())
    try:
        lab = vix_regime(T.date); m = lab != "na"; rows["P2 VIX regime (past-only median)"] = partition_test(x[m], lab[m])
    except Exception as e:
        rows["P2 VIX regime (past-only median)"] = None
    if "symbol" in T and T.symbol.nunique() > 1: rows["P1 instrument"] = partition_test(x, T.symbol.to_numpy())
    ev = {k: v for k, v in rows.items() if v is not None}
    ok = bool(ev) and all(v["sis"] < v["tau"] for v in ev.values())
    txt = "; ".join(f"{k}: SIS {v['sis']:.3f} vs Gaussian 95% {v['tau']:.3f} ({'ok' if v['sis'] < v['tau'] else 'DIFFERS'}; "
                    f"permutation p {v['p_perm']:.3f}; {v['groups']} groups, n {v['n']})" for k, v in ev.items())
    skipped = [k for k, v in rows.items() if v is None]
    return ok, f"outcome = {how}; " + txt + (f"; not evaluable: {', '.join(skipped)}" if skipped else ""), rows
