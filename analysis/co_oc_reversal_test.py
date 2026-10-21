"""Overnight-intraday reversal (Liu, Liu, Wang, Zhou & Zhu 2025, "Overnight-Intraday Reversal Everywhere", SSRN 2730304).

Paper: across futures (2004-18, daily open / close from TickData), buy the assets with the lowest close-to-open return
and sell the highest, hold open-to-close: Sharpe 5.5 equity indices, 1.9 rates, 3.5 commodities, 1.6 currencies.
Here, synchronised clock on our 7 markets (NQ, ES, YM, GC, CL, ZN, 6E), 2018-2026:
  signal  overnight log return, previous day's 15:00 CT close -> today's 8:30 CT close, with the 17:01 / 03:32 CT
          one-minute moves above 0.3% removed (contract-roll jumps in the unadjusted continuous series)
  trade   8:30 CT close -> 15:00 CT close, z = overnight / its 60-day sd (known before the trade)
  A  cross-section, all 7: w = -(z - mean z), each leg risk-scaled to $300 per 1 sd of its day-session move (fractional
     contracts, research only); B  equities only (NQ / ES / YM); C  the 4 others (GC / CL / ZN / 6E)
  D  time series on each market alone: fade the overnight move when |z| >= 1 (1 contract)
Costs a round trip: $7.25 + 1 tick a fill (ES $5 + 1 tick, as in CLAUDE.md).
  python3 analysis/co_oc_reversal_test.py [SCRATCH_DIR]
"""
import sys, os, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import Grid24, jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPEC = {"NQ": (20.0, 0.25, 7.25), "ES": (50.0, 0.25, 5.0), "YM": (5.0, 1.0, 7.25), "GC": (100.0, 0.10, 7.25),
        "CL": (1000.0, 0.01, 7.25), "ZN": (1000.0, 1 / 64, 7.25), "6E": (125000.0, 0.00005, 7.25)}
EQ, OTH = ["NQ", "ES", "YM"], ["GC", "CL", "ZN", "6E"]


def cost(s):
    pv, tick, comm = SPEC[s]; return comm + 2 * tick * pv


def load(sym):
    os.makedirs(SP, exist_ok=True)
    pk = SP + f"{sym.lower()}.pkl"
    if os.path.exists(pk): return pickle.load(open(pk, "rb"))
    g = (Grid24("data/NQ_1min_20*.csv", "data/NQ_1min_ON_*.csv") if sym == "NQ" else Grid24(f"data/{sym}_1min_20*.csv", night_pattern=""))
    pickle.dump(g, open(pk, "wb"), protocol=4); return g


def series(sym):
    g = load(sym); pv = SPEC[sym][0]
    cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    lr = np.diff(np.log(cf), prepend=np.nan); lr[np.isnan(lr)] = 0.0
    col = np.arange(len(lr)) % 1440
    jump = np.isin(col, [jof(1701), jof(332)]) & (np.abs(lr) > 0.003)
    lr[jump] = 0.0
    cum = np.cumsum(lr)
    r = g.trading
    # drop NQ's day-only dates without an overnight file etc.: need both 15:00 yesterday and 8:30 today
    idx = pd.DatetimeIndex(g.ts[r])
    on = cum[r[1:] * 1440 + jof(830)] - cum[r[:-1] * 1440 + jof(1500)]
    p830 = cf[r[1:] * 1440 + jof(830)]; p1500 = cf[r[1:] * 1440 + jof(1500)]
    day = (p1500 - p830) * pv
    has = ~np.isnan(g.c[r[1:], jof(800):jof(830) + 1]).all(1) & ~np.isnan(g.c[r[1:], jof(1430):jof(1500) + 1]).all(1)
    df = pd.DataFrame({"on": on, "day": day}, index=idx[1:])[has]
    df = df[df.index >= "2017-10-01"]
    df["z"] = df.on / df.on.rolling(60).std().shift(1)
    df["sd"] = df.day.rolling(60).std().shift(1)
    return df


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def line(x, nm, w=44):
    x = pd.Series(x).dropna(); x = x[x.index >= "2018-01-01"]
    if len(x) < 5: return f"   {nm:<{w}} n={len(x)}"
    y = x.index.year; by = x.groupby(y).sum(); pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    sr = x.mean() / x.std() * np.sqrt(252)
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():6.1f} PF {pf:4.2f} t {tstat(x):4.1f} SR {sr:4.1f} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${x[y < 2023].mean():6.1f} 23-26 ${x[y >= 2023].mean():6.1f}")


def xsec(D, syms, risk=300.0):
    Z = pd.concat({s: D[s].z for s in syms}, axis=1).dropna()
    W = -(Z.sub(Z.mean(1), axis=0))
    W = W.div(W.abs().sum(1), axis=0) * len(syms)          # gross exposure = len(syms) risk units
    N = pd.concat({s: W[s] * risk / D[s].sd.reindex(W.index) for s in syms}, axis=1)
    gross = sum(N[s] * D[s].day.reindex(N.index) for s in syms)
    c = sum(N[s].abs() * cost(s) for s in syms)
    return gross.dropna(), (gross - c).dropna()


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    D = {s: series(s) for s in EQ + OTH}
    for s in D: print(f"   {s}: {len(D[s])} days {D[s].index[0].date()} .. {D[s].index[-1].date()}, cost ${cost(s):.2f}")
    print("\nCorrelation of overnight z across markets (2018+):")
    print(pd.concat({s: D[s].z for s in D}, axis=1).loc["2018":].corr().round(2).to_string())

    print("\nA-C. Cross-sectional CO-OC, $ a day ($300 risk per unit; gross, then net)")
    res = {}
    for nm, syms in (("A all 7", EQ + OTH), ("B equities", EQ), ("C GC/CL/ZN/6E", OTH)):
        g, n = xsec(D, syms); res[nm] = n
        print(line(g, f"{nm} gross")); print(line(n, f"{nm} NET"))
    g, _ = xsec(D, EQ + OTH); g = g[g.index >= "2018"]
    print(line(xsec(D, EQ + OTH)[0].shift(0)[lambda x: x.index.dayofweek == 0], "A all 7 gross, Mondays only"))

    print("\nD. Time series: fade the overnight move when |z| >= 1, 1 contract (gross, NET; then follow for reference)")
    for s in EQ + OTH:
        d = D[s].dropna(); m = d.z.abs() >= 1
        x = -np.sign(d.z[m]) * d.day[m]
        print(line(x, f"{s} fade gross")); print(line(x - cost(s), f"{s} fade NET"))

    nm = "A all 7"; x = res[nm]; x = x[x.index >= "2018"]
    print(f"\n{nm} NET standard metrics:")
    print(M.table({nm: (x, None)}))
    b, p = R.report({nm: x[x.index >= "2023"]}, n=2000)
    print("2023+ bootstrap:\n" + b)
