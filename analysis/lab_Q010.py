"""Lab Q010: 6E month-end hedge rebalancing, side from ES month-to-date. Pre-registration:
checks/candidates/lab_Q010/PREREG.md. Stages 1-2 on 2018-22; stage 3 (2023-onward) only with --holdout.
  python3 analysis/lab_Q010.py [--holdout]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M
from lab_Q003 import load, fix_col, PV, COST, tstat, pf, show

HOLD = "--holdout" in sys.argv


def es_marks(es):
    r = es.trading; idx = pd.DatetimeIndex(es.ts[r])
    c830 = pd.Series(es.c[r, jof(830)], index=idx); c1500 = pd.Series(es.c[r, jof(1500)], index=idx)
    last = c1500.groupby(idx.to_period("M")).apply(lambda s: s.dropna().iloc[-1] if s.notna().any() else np.nan)
    return c830, last


def signal(day, c830, last):
    pm = (day.to_period("M") - 1)
    if day not in c830.index or pm not in last.index: return 0
    x = c830.loc[day] / last.loc[pm] - 1
    return 0 if not np.isfinite(x) or x == 0 else np.sign(x)


def run(g, rows, v, c830, last):
    out = {}
    for r in rows:
        d = pd.Timestamp(g.ts[r]); s = signal(d, c830, last)
        if s == 0: continue
        F = fix_col(g.ts[r]); e = g.o[r, jof(831)] if v in (1, 3) else g.o[r, F - 29]; x = g.c[r, F]
        if not (np.isfinite(e) and np.isfinite(x)): continue
        out[d] = s * (x - e) * PV - COST
    return pd.Series(out, dtype=float).sort_index()


if __name__ == "__main__":
    g = load(); es = pickle.load(open("scratch_data/ge.pkl", "rb")); c830, last = es_marks(es)
    rows = g.trading; idx = pd.DatetimeIndex(g.ts[rows]); per = idx.to_period("M")
    rank = pd.Series(idx, index=idx).groupby(per).rank(ascending=False).to_numpy()   # 1 = last session
    me1, me2 = rank == 1, rank <= 2
    mid = pd.Series(idx >= idx.normalize().map(lambda d: d.replace(day=15)), index=idx)
    midday = (mid & ~mid.groupby(per).shift(1, fill_value=False)).to_numpy()
    yr = idx.year; D = (yr >= 2018) & (yr <= 2022); H = yr >= 2023
    print(f"cost ${COST:.2f}\n\nStage 1 (2018-22)")
    T = {1: run(g, rows[D & me1], 1, c830, last), 2: run(g, rows[D & me1], 2, c830, last), 3: run(g, rows[D & me2], 3, c830, last)}
    for v, nm in ((1, "V1 08:30 -> fix, month-end"), (2, "V2 fix-30 -> fix, month-end"), (3, "V3 V1 on last 2 sessions")): show(T[v], nm)
    best = max(T, key=lambda v: tstat(T[v])); x = T[best]
    s1 = tstat(x) >= 2.0 and pf(x) >= 1.15 and len(x) >= 40
    print(f"  best V{best}: stage 1 {'PASS' if s1 else 'FAIL'}")
    show(run(g, rows[D & midday], best, c830, last), f"mid-month control V{best}")
    pool = rows[D & ~me2]; P = run(g, pool, best, c830, last).reindex(pd.DatetimeIndex(g.ts[pool]))
    rng = np.random.default_rng(7); n = int((D & (me2 if best == 3 else me1)).sum())
    pm = np.array([P.iloc[rng.choice(len(P), n, replace=False)].mean() for _ in range(500)])
    p = np.mean(pm >= x.mean()); by = x.groupby(x.index.year).sum(); s2 = p < 0.05 and (by > 0).sum() >= 4
    print(f"\nStage 2 placebo V{best}: random days avg ${np.nanmean(pm):.1f}, p = {p:.3f}; stage 2 {'PASS' if s2 else 'FAIL'}")
    daily = x.reindex(pd.date_range("2018-01-01", "2022-12-31", freq="B"), fill_value=0.0); m = M.perf(daily, x)
    print("  metrics V%d 2018-22: Sharpe %.2f Sortino %.2f PF %.2f Calmar %.2f Ulcer %.2f" %
          (best, m["sharpe"], m["sortino"], m["profit_factor"], m["calmar"], m["ulcer"]))
    for sd, nm in ((1, "longs"), (-1, "shorts")):
        sig = pd.Series({d: signal(d, c830, last) for d in x.index}); show(x[sig == sd], f"  V{best} {nm}")
    if HOLD and s1 and s2:
        sel = H & (me2 if best == 3 else me1)
        h = run(g, rows[sel], best, c830, last); print("\nStage 3 holdout (one look)"); show(h, f"V{best} 2023-onward")
        show(pd.concat([x, h]), f"V{best} full 2018-onward")
