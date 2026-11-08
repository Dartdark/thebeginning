"""Lab Q013: 6E after US payrolls: follow / fade the 07:30 -> 07:45 move from 07:46 to 09:55 CT.
Pre-registration: checks/candidates/lab_Q013/PREREG.md. Stages 1-2 on 2018-22; stage 3 only with --holdout.
  python3 analysis/lab_Q013.py [--holdout]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M
from lab_Q003 import load, PV, TICK, COMM, COST, tstat, pf, show

HOLD = "--holdout" in sys.argv


def vr(g, r, stamp):
    j = jof(stamp); base = np.nanmedian(g.v[r, j - 15:j]); return g.v[r, j] / base if base > 0 else np.nan


def trade(g, r, v, atr):
    a = atr[r]; mv = g.c[r, jof(745)] - g.c[r, jof(730)]
    if not (np.isfinite(a) and np.isfinite(mv)) or mv == 0: return None
    if v == 3 and abs(mv) < 0.3 * a: return None
    s = np.sign(mv) * (-1 if v == 2 else 1); j0, j1 = jof(747), jof(955)
    o, h, l, c = g.o[r, j0:j1 + 1], g.h[r, j0:j1 + 1], g.l[r, j0:j1 + 1], g.c[r, j0:j1 + 1]
    if not np.isfinite(o[0]): return None
    ent = o[0]; stop = ent - s * 0.3 * a; px = None
    for i in range(len(o)):
        if not np.isfinite(h[i]): continue
        if s > 0 and l[i] <= stop: px = min(stop, o[i]) - TICK; break
        if s < 0 and h[i] >= stop: px = max(stop, o[i]) + TICK; break
    if px is None:
        last = c[np.isfinite(c)]; px = last[-1] - s * TICK
    return s * (px - ent) * PV - COMM - TICK * PV


def run(g, rows, v, atr):
    out = {}
    for r in rows:
        p = trade(g, r, v, atr)
        if p is not None: out[pd.Timestamp(g.ts[r])] = p
    return pd.Series(out, dtype=float).sort_index()


if __name__ == "__main__":
    g = load(); atr = g.daily_atr(14); rows = g.trading; idx = pd.DatetimeIndex(g.ts[rows])
    fri = rows[idx.dayofweek == 4]; fidx = pd.DatetimeIndex(g.ts[fri])
    isn = np.array([d.day <= 10 and vr(g, r, 731) >= 5 for r, d in zip(fri, fidx)])
    nfp, oth = fri[isn], fri[~isn]
    ny = pd.DatetimeIndex(g.ts[nfp]).year; oy = pd.DatetimeIndex(g.ts[oth]).year
    print("NFP days by year: " + " ".join(f"{y}:{n}" for y, n in pd.Series(ny).value_counts().sort_index().items()))
    D, H, O = nfp[(ny >= 2018) & (ny <= 2022)], nfp[ny >= 2023], oth[(oy >= 2018) & (oy <= 2022)]
    print(f"design {len(D)}, holdout {len(H)}; cost ${COST:.2f}\n\nStage 1 (2018-22)")
    T = {v: run(g, D, v, atr) for v in (1, 2, 3)}
    for v, nm in ((1, "V1 follow 07:46->09:55"), (2, "V2 fade"), (3, "V3 follow, |move| >= 0.3 ATR")): show(T[v], nm)
    best = max(T, key=lambda v: tstat(T[v])); x = T[best]
    s1 = tstat(x) >= 2.0 and pf(x) >= 1.15 and len(x) >= 40
    print(f"  best V{best}: stage 1 {'PASS' if s1 else 'FAIL'}")
    P = run(g, O, best, atr).reindex(pd.DatetimeIndex(g.ts[O])); rng = np.random.default_rng(7)
    pm = np.array([P.iloc[rng.choice(len(P), len(D), replace=False)].mean() for _ in range(500)])
    p = np.mean(pm >= x.mean()); by = x.groupby(x.index.year).sum(); s2 = p < 0.05 and (by > 0).sum() >= 4
    print(f"\nStage 2 placebo V{best}: other Fridays avg ${P.mean():.1f}, p = {p:.3f}; stage 2 {'PASS' if s2 else 'FAIL'}")
    daily = x.reindex(pd.date_range("2018-01-01", "2022-12-31", freq="B"), fill_value=0.0); m = M.perf(daily, x)
    print("  metrics V%d 2018-22: Sharpe %.2f Sortino %.2f PF %.2f Calmar %.2f Ulcer %.2f" %
          (best, m["sharpe"], m["sortino"], m["profit_factor"], m["calmar"], m["ulcer"]))
    if HOLD and s1 and s2:
        h = run(g, H, best, atr); print("\nStage 3 holdout (one look)"); show(h, f"V{best} 2023-onward")
        show(pd.concat([x, h]), f"V{best} full 2018-onward")
