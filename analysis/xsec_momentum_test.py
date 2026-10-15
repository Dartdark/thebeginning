"""Cross-sectional momentum, Apex-legal version (user's PDF: 'The Distribution of Cross-Sectional Momentum Returns', SSRN
3018366 -- theory: CSM returns are a mixture of normals; positive mean can come with negative skew). The paper's strategy
holds for a month; Apex must be flat daily, so the testable form is: rank our 7 futures (NQ, ES, YM, GC, CL, ZN, 6E) by their
past return and trade the NEXT day session 8:30 -> 15:00 CT, long the top 2, short the bottom 2, each leg risk-scaled to
$300 per 1 sd of its day-session move (fractional contracts, research only), costs $7.25 + 1 tick a fill (ES $5).
Pre-registered ranking windows: 1, 5, 20 days of close-to-close (15:00 CT) log returns, each z-scored by the market's own
60-day sd; plus the reverse (short winners) as the mirror and an equities-only (NQ/ES/YM) version of the 5-day rule.
Reported: mean, t, by half, skewness of daily P&L (the paper's point), standard metrics for the best by t.
  python3 analysis/xsec_momentum_test.py [SCRATCH_DIR]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import load, cost, SPEC, line
import metrics as M, resampling as R

SYMS = ["NQ", "ES", "YM", "GC", "CL", "ZN", "6E"]


def frame(sym):
    g = load(sym); pv = SPEC[sym][0]; r = g.trading
    cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    p830 = cf[r * 1440 + jof(830)]; p1500 = cf[r * 1440 + jof(1500)]
    ok = ~np.isnan(g.c[r, jof(1430):jof(1500) + 1]).all(1) & ~np.isnan(g.c[r, jof(800):jof(830) + 1]).all(1)
    d = pd.DataFrame({"p1500": p1500, "day": (p1500 - p830) * pv}, index=pd.DatetimeIndex(g.ts[r]))[ok]
    lr = np.log(d.p1500).diff(); lr[lr.abs() > 0.08] = np.nan                    # drop roll jumps
    d["lr"] = lr; d["sd60"] = lr.rolling(60).std().shift(0)
    d["sdday"] = d.day.rolling(60).std().shift(1)
    return d[d.index >= "2017-10-01"]


def book(D, syms, k, sign=1, n_side=2):
    Z = pd.concat({s: D[s].lr.rolling(k).sum() / (D[s].sd60 * np.sqrt(k)) for s in syms}, axis=1).shift(1).dropna()
    NX = pd.concat({s: D[s].day for s in syms}, axis=1).reindex(Z.index); SD = pd.concat({s: D[s].sdday for s in syms}, axis=1).reindex(Z.index)
    rk = Z.rank(axis=1)
    W = sign * ((rk > len(syms) - n_side).astype(float) - (rk <= n_side).astype(float))
    Q = W * 300.0 / SD
    pnl = (Q * NX).sum(1) - (Q.abs() * pd.Series({s: cost(s) for s in syms})).sum(1)
    return pnl[pnl.index >= "2018-01-01"].dropna()


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    D = {s: frame(s) for s in SYMS}
    res = {}
    for k in (1, 5, 20):
        for sg, nm in ((1, "momentum"), (-1, "reversal")):
            x = book(D, SYMS, k, sg); res[f"{nm} {k}d"] = x
            print(line(x, f"{nm} {k}d (7 mkts, top/bottom 2)") + f" | skew {x.skew():+.2f}")
    x = book(D, ["NQ", "ES", "YM"], 5, 1, 1); res["momentum 5d equities"] = x
    print(line(x, "momentum 5d, NQ/ES/YM, top/bottom 1") + f" | skew {x.skew():+.2f}")
    best = max(res, key=lambda k: res[k].mean() / res[k].std() * np.sqrt(len(res[k])))
    x = res[best]; days = pd.bdate_range("2018-01-01", x.index.max()); dd = x.reindex(days, fill_value=0.0)
    print(f"\nBest by t: {best}; N items {len(pd.read_csv('TRIALS.csv'))} -> bar t {M.t_threshold(len(pd.read_csv('TRIALS.csv'))):.2f}")
    print(M.table({best: (dd, x)}))
    b_, p_ = R.report({best: dd[dd.index >= "2023"]}, n=2000); print("2023+ bootstrap:\n" + b_)
