"""Lab Q009: NG drift 08:00 -> 09:29 CT before the EIA storage report. Pre-registration:
checks/candidates/lab_Q009/PREREG.md. Stages 1-2 on 2018-22; stage 3 (2023-onward) only with --holdout.
  python3 analysis/lab_Q009.py [--holdout]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M
from lab_Q007 import load, release_rows, PV, TICK, COMM, COST, tstat, pf, show

HOLD = "--holdout" in sys.argv


def trades(g, rows, atr, v):
    res = {}; j0, j1 = jof(801), jof(929)
    for r in rows:
        o, h, l, c = g.o[r, j0:j1 + 1], g.h[r, j0:j1 + 1], g.l[r, j0:j1 + 1], g.c[r, j0:j1 + 1]
        a = atr[r]
        if not (np.isfinite(o[0]) and np.isfinite(a)): continue
        if v == 1: s = 1
        elif v == 2: s = -1
        else:
            s = np.sign(g.c[r, jof(759)] - g.o[r - 1, jof(1701)])
            if not np.isfinite(s) or s == 0: continue
        ent = o[0]; stop = ent - s * 0.3 * a; px = None
        for i in range(len(o)):
            if not np.isfinite(h[i]): continue
            if s > 0 and l[i] <= stop: px = min(stop, o[i]) - TICK; break
            if s < 0 and h[i] >= stop: px = max(stop, o[i]) + TICK; break
        if px is None:
            last = c[np.isfinite(c)]; px = last[-1] - s * TICK
        res[pd.Timestamp(g.ts[r])] = s * (px - ent) * PV - COMM - TICK * PV
    return pd.Series(res, dtype=float).sort_index()


if __name__ == "__main__":
    g = load(); atr = g.daily_atr(14); rel = release_rows(g)
    yr = pd.DatetimeIndex(g.ts[rel]).year; dsg = rel[(yr >= 2018) & (yr <= 2022)]; hold = rel[yr >= 2023]
    print(f"release days: design {len(dsg)}, holdout {len(hold)}; cost ${COST:.0f}\n\nStage 1 (2018-22)")
    T = {v: trades(g, dsg, atr, v) for v in (1, 2, 3)}
    for v, nm in ((1, "V1 long 08:00->09:29"), (2, "V2 short"), (3, "V3 follow the overnight")): show(T[v], nm)
    best = max(T, key=lambda v: tstat(T[v])); x = T[best]
    s1 = tstat(x) >= 2.0 and pf(x) >= 1.15 and len(x) >= 40
    print(f"  best V{best}: stage 1 {'PASS' if s1 else 'FAIL'}; gross avg ${x.mean() + COST:.1f}")
    other = np.setdiff1d(g.trading, rel); oy = pd.DatetimeIndex(g.ts[other]).year; other = other[(oy >= 2018) & (oy <= 2022)]
    P = trades(g, other, atr, best).reindex(pd.DatetimeIndex(g.ts[other]))
    rng = np.random.default_rng(7)
    pm = np.array([P.iloc[rng.choice(len(P), len(dsg), replace=False)].mean() for _ in range(500)])
    p = np.mean(pm >= x.mean()); by = x.groupby(x.index.year).sum(); s2 = p < 0.05 and (by > 0).sum() >= 4
    print(f"\nStage 2 placebo V{best}: non-release days avg ${P.mean():.1f}, placebo p = {p:.3f}; stage 2 {'PASS' if s2 else 'FAIL'}")
    daily = x.reindex(pd.date_range("2018-01-01", "2022-12-31", freq="B"), fill_value=0.0); m = M.perf(daily, x)
    print("  metrics V%d 2018-22: Sharpe %.2f Sortino %.2f PF %.2f Calmar %.2f Ulcer %.2f" %
          (best, m["sharpe"], m["sortino"], m["profit_factor"], m["calmar"], m["ulcer"]))
    if HOLD and s1 and s2:
        h = trades(g, hold, atr, best); print("\nStage 3 holdout (one look)"); show(h, f"V{best} 2023-onward")
        show(pd.concat([x, h]), f"V{best} full 2018-onward")
