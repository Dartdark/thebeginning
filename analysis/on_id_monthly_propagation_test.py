"""Monthly overnight / intraday momentum and cross-reversal, NQ / ES (paper: Chen, Stivers & Sun, 'Heterogeneity in Overnight-
versus-Intraday Stock-Return Behavior with Asymmetric Information and 52-week Price Anchoring', SSRN 7443340; user upload
2026-10-29). Paper (stock cross-section): last month's overnight return predicts this month's overnight (+) and intraday (-),
last month's intraday predicts intraday (+) and overnight (-); price near the 52-week high (PTA) weakens intraday momentum.
Time-series version fixed before looking: monthly sums of daily overnight (15:00 -> 08:30 CT) and intraday (08:30 -> 15:00)
log returns, roll weeks out; slopes of next month on this month (t), and intraday momentum split by month-end price / 252-day
high above vs below 0.95.   python3 analysis/on_id_monthly_propagation_test.py
"""
import glob, numpy as np, pandas as pd
def ols(y, x):
    X = np.c_[np.ones(len(x)), x]; b = np.linalg.lstsq(X, y, rcond=None)[0]; u = y - X @ b
    return b[1], b[1] / np.sqrt(np.linalg.inv(X.T @ X)[1, 1] * (u @ u) / (len(y) - 2))
for sym in ("NQ", "ES"):
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"data/{sym}_1min_20*.csv")) if "_ON_" not in f])
    o = d[d.time == 831].set_index("date").open; c = d[d.time == 1500].set_index("date").close
    x = pd.DataFrame(dict(o=o, c=c)).dropna(); x.index = pd.to_datetime(x.index.astype(str))
    x["on"] = np.log(x.o / x.c.shift(1)); x["id"] = np.log(x.c / x.o); x["hi"] = x.c.rolling(252).max(); x = x.dropna()
    rw = x.index.month.isin([3, 6, 9, 12]) & (x.index.day >= 8) & (x.index.day <= 17); x = x[~rw & (x.index >= "2018-01-01")]
    m = x.groupby(x.index.to_period("M")).agg(on=("on", "sum"), id=("id", "sum"), pta=("c", "last"), hi=("hi", "last"))
    m["pta"] = m.pta / m.hi; n = m.shift(-1); m = m.iloc[:-1]; n = n.iloc[:-1]
    print(f"\n{sym}: {len(m)} months")
    for a, b, nm in (("on", "on", "overnight -> overnight (paper +)"), ("on", "id", "overnight -> intraday (paper -)"),
                     ("id", "id", "intraday -> intraday (paper +)"), ("id", "on", "intraday -> overnight (paper -)")):
        s, t = ols(n[b].values * 100, m[a].values * 100); print(f"   {nm:34s} slope {s:+.2f}, t {t:+.1f}")
    for nm, k in (("near 52w high (>= 0.95)", m.pta >= 0.95), ("below", m.pta < 0.95)):
        s, t = ols(n.id[k].values * 100, m.id[k].values * 100); print(f"   intraday momentum, {nm:24s} {k.sum():3d} months slope {s:+.2f}, t {t:+.1f}")
