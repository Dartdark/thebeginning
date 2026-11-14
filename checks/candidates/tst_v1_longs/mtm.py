"""Checker: mark-to-market daily equity of the replica vs BTC buy-and-hold (time-in-market and risk matched)."""
import sys, os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import replica as R
m = R.load_1m(); b = R.bars4h(m); S = R.Sim(m, b); sig, atr = S.signal(); T = S.run(sig, atr)
n = len(m); w = np.zeros(n)
for r in T.itertuples():
    e = S.i1[r.j]                       # first minute after entry close
    h = int(r.ih) + 1 if r.half else r.xi
    w[e:h] += 1.0
    if r.half: w[h:r.xi] += 0.5         # exit minute itself handled approx
c = m.close.values; ret = np.r_[0, c[1:] / c[:-1] - 1]
rr = w * ret
for r in T.itertuples():               # exit minute: from the previous close to the fill price; half minute: to the target
    rr[r.xi] = (0.5 if r.half else 1.0) * (r.exit / c[r.xi - 1] - 1)
    # half-off minute stays on the minute-close approximation (target level not stored)
gross = pd.Series(rr, index=m.index)
d = gross.resample("1D").sum()
# costs: subtract trade-level cost on exit day (approx: model net - gross trade return)
d = d.loc["2018-06-01":]
bh = pd.Series(ret, index=m.index).resample("1D").sum().loc["2018-06-01":]
def st(x, lab):
    eq = (1 + x).cumprod(); dd = (eq / eq.cummax() - 1).min(); yrs = len(x) / 365.25
    cagr = eq.iloc[-1] ** (1 / yrs) - 1; sh = x.mean() / x.std() * np.sqrt(365)
    print(f"{lab:34s} CAGR {cagr:+.1%} vol {x.std()*np.sqrt(365):.0%} Sharpe {sh:.2f} maxDD {dd:.0%} CAGR/DD {cagr/-dd:.2f}")
    return sh
cost_per_trade = 2 * (R.FEE + R.SLIP)
cd = pd.Series(cost_per_trade, index=T.tx.dt.normalize()).groupby(level=0).sum().reindex(d.index, fill_value=0)
st(d - cd, "strategy MTM (approx costs)")
st(bh, "BTC buy & hold")
k = (d - cd).std() / bh.std(); st(bh * k, f"BTC B&H scaled to strategy vol ({k:.2f}x)")
for y in range(2018, 2027):
    a, bb = (d - cd).loc[str(y)], bh.loc[str(y)]
    print(f"  {y}: strategy {((1+a).prod()-1):+.0%}  B&H {((1+bb).prod()-1):+.0%}  B&H x{k:.2f} {((1+bb*k).prod()-1):+.0%}")
# alpha / beta of daily strategy on daily BTC
import numpy.linalg as L
X = np.c_[np.ones(len(bh)), bh.values]; y = (d - cd).values; beta = L.lstsq(X, y, rcond=None)[0]
res = y - X @ beta; se = np.sqrt(res.var(ddof=2) / len(y) / 1)
print(f"daily regression on BTC: alpha {beta[0]*365:+.1%}/yr (t {beta[0]/se:.2f}), beta {beta[1]:.2f}")
for st_ in ("2023-01-01",):
    yy, xx = y[bh.index >= st_], bh.values[bh.index >= st_]; X2 = np.c_[np.ones(len(xx)), xx]; bt = L.lstsq(X2, yy, rcond=None)[0]; rr = yy - X2 @ bt
    print(f"  {st_}+: alpha {bt[0]*365:+.1%}/yr (t {bt[0]/np.sqrt(rr.var(ddof=2)/len(yy)):.2f}), beta {bt[1]:.2f}")
