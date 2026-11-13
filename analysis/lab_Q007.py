"""Lab Q007: NG EIA storage report (Thu 09:30 CT) first-5-minute fade / follow. Pre-registration:
checks/candidates/lab_Q007/PREREG.md. Stages 1-2 on 2018-22 only; stage 3 (2023-onward) only with --holdout.
  python3 analysis/lab_Q007.py [--holdout]
"""
import sys, os, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import Grid24, jof
import metrics as M

PV, TICK, COMM = 10_000.0, 0.001, 5.0
COST = COMM + 2 * TICK * PV          # $25 round trip (1 tick per fill)
PK = "scratch_data/ng.pkl"
HOLD = "--holdout" in sys.argv


def load():
    if os.path.exists(PK): return pickle.load(open(PK, "rb"))
    g = Grid24("data/NG_1min_20*.csv", night_pattern=""); pickle.dump(g, open(PK, "wb"), protocol=4); return g


def vol_ratio(g, rows):
    base = np.nanmedian(g.v[rows][:, jof(916):jof(930) + 1], axis=1)
    return g.v[rows, jof(931)] / base


def release_rows(g):
    rows = g.trading
    idx = pd.DatetimeIndex(g.ts[rows]); ratio = vol_ratio(g, rows)
    df = pd.DataFrame(dict(row=rows, dow=idx.dayofweek, ratio=ratio), index=idx)
    df["wk"] = idx.to_period("W")
    out = []
    for _, w in df.groupby("wk"):
        th = w[(w.dow == 3) & (w.ratio >= 3)]
        if len(th): out.append(th.row.iloc[0]); continue
        alt = w[w.dow.isin([2, 4]) & (w.ratio >= 3)]
        if len(alt): out.append(alt.sort_values("ratio").row.iloc[-1])
    return np.array(sorted(out))


def trades(g, rows, atr, variant):
    """$ P&L per NG for each row where the rule trades (pd.Series indexed by date)."""
    c930, c935 = g.c[rows, jof(930)], g.c[rows, jof(935)]
    mv = c935 - c930; a = atr[rows]
    ok = np.isfinite(mv) & np.isfinite(a) & (np.abs(mv) >= 0.15 * a)
    side = -np.sign(mv) if variant in (1, 3) else np.sign(mv)
    if variant == 3:
        mo = pd.DatetimeIndex(g.ts[rows]).month
        ok &= np.isin(mo, [11, 12, 1, 2, 3])
    res = {}
    j0, j1 = jof(937), jof(1030)
    for k in np.where(ok)[0]:
        r, s = rows[k], side[k]
        o, h, l, cl = g.o[r, j0:j1 + 1], g.h[r, j0:j1 + 1], g.l[r, j0:j1 + 1], g.c[r, j0:j1 + 1]
        if not np.isfinite(o[0]): continue
        ent = o[0]; stop = ent - s * 0.3 * a[k]; px = None
        for i in range(len(o)):
            if not np.isfinite(h[i]): continue
            if s > 0 and l[i] <= stop: px = min(stop, o[i]) - TICK; break
            if s < 0 and h[i] >= stop: px = max(stop, o[i]) + TICK; break
        if px is None:
            last = cl[np.isfinite(cl)]; px = last[-1] - s * TICK
            pnl = s * (px - ent) * PV - COMM - TICK * PV     # entry tick + exit tick
        else:
            pnl = s * (px - ent) * PV - COMM - TICK * PV     # entry tick; stop tick already in px
        res[pd.Timestamp(g.ts[r])] = pnl
    return pd.Series(res, dtype=float).sort_index()


def tstat(x): return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def pf(x): return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def show(x, nm):
    by = x.groupby(x.index.year).sum()
    print(f"  {nm:<34} n={len(x):4d} avg ${x.mean():6.1f} PF {pf(x):4.2f} t {tstat(x):5.2f} win {np.mean(x > 0):.0%} "
          f"yrs+ {(by > 0).sum()}/{len(by)}  " + " ".join(f"{y}:{v:+.0f}" for y, v in by.items()))


if __name__ == "__main__":
    g = load(); atr = g.daily_atr(14)
    rel = release_rows(g)
    yr = pd.DatetimeIndex(g.ts[rel]).year
    dsg = rel[(yr >= 2018) & (yr <= 2022)]; hold = rel[yr >= 2023]
    idx = pd.DatetimeIndex(g.ts[rel])
    print(f"release days found: {len(rel)} (Thu {np.mean(idx.dayofweek == 3):.0%}); design {len(dsg)}, holdout {len(hold)}")
    print(f"median 09:31 volume ratio: release {np.nanmedian(vol_ratio(g, rel)):.1f}; "
          f"other days {np.nanmedian(vol_ratio(g, np.setdiff1d(g.trading, rel))):.1f}")
    print(f"cost per round trip ${COST:.0f}\n\nStage 1 (2018-22)")
    T = {v: trades(g, dsg, atr, v) for v in (1, 2, 3)}
    for v, nm in ((1, "V1 fade"), (2, "V2 follow"), (3, "V3 fade, Nov-Mar")): show(T[v], nm)
    best = max(T, key=lambda v: tstat(T[v])); x = T[best]
    s1 = tstat(x) >= 2.0 and pf(x) >= 1.15 and len(x) >= 40
    print(f"  best V{best}: stage 1 {'PASS' if s1 else 'FAIL'}")
    # gross reference (no costs), for the lesson
    for v in (1, 2): print(f"  V{v} gross avg ${(T[v] + COST).mean():.1f}")
    # stage 2 placebo regardless (cheap), design years only
    other = np.setdiff1d(g.trading, rel); oy = pd.DatetimeIndex(g.ts[other]).year
    other = other[(oy >= 2018) & (oy <= 2022)]
    P = trades(g, other, atr, best)
    rng = np.random.default_rng(7); pm = []
    pidx = pd.DatetimeIndex(g.ts[other]); Pv = P.reindex(pidx)          # NaN = no trade that day
    for _ in range(500):
        smp = Pv.iloc[rng.choice(len(Pv), len(dsg), replace=False)].dropna(); pm.append(smp.mean())
    p = np.mean(np.array(pm) >= x.mean())
    print(f"\nStage 2 placebo (V{best} on random non-release days): placebo avg ${np.nanmean(pm):.1f}, p = {p:.3f}; "
          f"all non-release days n={len(P)} avg ${P.mean():.1f}")
    by = x.groupby(x.index.year).sum(); s2 = p < 0.05 and (by > 0).sum() >= 4
    print(f"  stage 2 {'PASS' if s2 else 'FAIL'}")
    for side, nm in ((1, "longs"), (-1, "shorts")): pass
    daily = x.reindex(pd.date_range("2018-01-01", "2022-12-31", freq="B"), fill_value=0.0)
    m = M.perf(daily, x)
    print("  metrics V%d 2018-22: Sharpe %.2f Sortino %.2f PF %.2f Calmar %.2f Ulcer %.2f" %
          (best, m["sharpe"], m["sortino"], m["profit_factor"], m["calmar"], m["ulcer"]))
    if HOLD and s1 and s2:
        h = trades(g, hold, atr, best); print("\nStage 3 holdout (one look)"); show(h, f"V{best} 2023-onward")
        a = pd.concat([x, h]); show(a, f"V{best} full 2018-onward")
