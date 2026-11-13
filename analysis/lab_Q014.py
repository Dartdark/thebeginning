"""Lab Q014: GC while the Shanghai Gold Exchange is closed (Spring Festival, National Day). Pre-registration:
checks/candidates/lab_Q014/PREREG.md; calendar data/sge_holidays.csv. Stages 1-2 on 2018-22; stage 3 only with --holdout.
  python3 analysis/lab_Q014.py [--holdout]
"""
import sys, os, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import Grid24, jof
import metrics as M

PV, TICK, COMM = 100.0, 0.1, 5.0
COST = COMM + 2 * TICK * PV
HOLD = "--holdout" in sys.argv
PK = "scratch_data/gc.pkl"


def load():
    if os.path.exists(PK): return pickle.load(open(PK, "rb"))
    g = Grid24("data/GC_1min_20*.csv", night_pattern=""); pickle.dump(g, open(PK, "wb"), protocol=4); return g


def trade(g, r, s, atr):
    a = atr[r]; j0, j1 = jof(721), jof(1225)
    o, h, l, c = g.o[r, j0:j1 + 1], g.h[r, j0:j1 + 1], g.l[r, j0:j1 + 1], g.c[r, j0:j1 + 1]
    if not (np.isfinite(a) and np.isfinite(o[0])): return None
    ent = o[0]; stop = ent - s * 0.3 * a; px = None
    for i in range(len(o)):
        if not np.isfinite(h[i]): continue
        if s > 0 and l[i] <= stop: px = min(stop, o[i]) - TICK; break
        if s < 0 and h[i] >= stop: px = max(stop, o[i]) + TICK; break
    if px is None:
        last = c[np.isfinite(c)]; px = last[-1] - s * TICK
    return s * (px - ent) * PV - COMM - TICK * PV


def run(g, rows, s, atr):
    out = {}
    for r in rows:
        p = trade(g, r, s, atr)
        if p is not None: out[pd.Timestamp(g.ts[r])] = p
    return pd.Series(out, dtype=float).sort_index()


def tstat(x): return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan
def pf(x): return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def show(x, nm):
    by = x.groupby(x.index.year).sum()
    print(f"  {nm:<30} n={len(x):4d} avg ${x.mean():6.1f} (gross ${x.mean() + COST:6.1f}) PF {pf(x):4.2f} t {tstat(x):5.2f} "
          f"win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}  " + " ".join(f"{y}:{v:+.0f}" for y, v in by.items()))


if __name__ == "__main__":
    g = load(); atr = g.daily_atr(14); rows = g.trading; idx = pd.DatetimeIndex(g.ts[rows])
    cal = pd.read_csv("data/sge_holidays.csv", comment="#", parse_dates=["date"])
    hol = set(cal.date); pos = {d: i for d, i in zip(idx, rows)}
    clos = [pos[d] for d in sorted(hol) if d in pos]
    # holidays = runs of closure dates within 12 days; first 3 and the 2 sessions after each
    grp = (cal.date.diff().dt.days.fillna(99) > 12).cumsum(); first3, reopen = [], []
    for _, gdf in cal.groupby(grp):
        ds = [d for d in gdf.date if d in pos]; first3 += [pos[d] for d in ds[:3]]
        after = idx[idx > gdf.date.max()][:2]; reopen += [pos[d] for d in after]
    yr = lambda L: np.array([pd.Timestamp(g.ts[r]).year for r in L])
    sel = lambda L, lo, hi: [r for r, y in zip(L, yr(L)) if lo <= y <= hi]
    print(f"closure weekdays with GC data: {len(clos)} (missing {len(hol) - len(clos)}); cost ${COST:.0f}\n\nStage 1 (2018-22)")
    T = {1: run(g, sel(clos, 2018, 2022), -1, atr), 2: run(g, sel(reopen, 2018, 2022), 1, atr), 3: run(g, sel(first3, 2018, 2022), -1, atr)}
    for v, nm in ((1, "V1 short, closure days"), (2, "V2 long, 2 reopen sessions"), (3, "V3 short, first 3 closure days")): show(T[v], nm)
    best = max(T, key=lambda v: tstat(T[v])); x = T[best]
    s1 = tstat(x) >= 2.0 and pf(x) >= 1.15 and len(x) >= 40
    print(f"  best V{best}: stage 1 {'PASS' if s1 else 'FAIL'}")
    excl = set(clos) | set(reopen)
    other = [r for r, d in zip(rows, idx) if 2018 <= d.year <= 2022 and r not in excl]
    side = 1 if best == 2 else -1
    P = run(g, other, side, atr).reindex(pd.DatetimeIndex(g.ts[other])); rng = np.random.default_rng(7)
    pm = np.array([P.iloc[rng.choice(len(P), len(x), replace=False)].mean() for _ in range(500)])
    p = np.mean(pm >= x.mean()); by = x.groupby(x.index.year).sum(); s2 = p < 0.05 and (by > 0).sum() >= 4
    print(f"\nStage 2 placebo V{best}: other weekdays avg ${P.mean():.1f}, p = {p:.3f}; stage 2 {'PASS' if s2 else 'FAIL'}")
    daily = x.reindex(pd.date_range("2018-01-01", "2022-12-31", freq="B"), fill_value=0.0); m = M.perf(daily, x)
    print("  metrics V%d 2018-22: Sharpe %.2f Sortino %.2f PF %.2f Calmar %.2f Ulcer %.2f" %
          (best, m["sharpe"], m["sortino"], m["profit_factor"], m["calmar"], m["ulcer"]))
    if HOLD and s1 and s2:
        L = {1: clos, 2: reopen, 3: first3}[best]; h = run(g, sel(L, 2023, 2026), side, atr)
        print("\nStage 3 holdout (one look)"); show(h, f"V{best} 2023-onward"); show(pd.concat([x, h]), f"V{best} full")
