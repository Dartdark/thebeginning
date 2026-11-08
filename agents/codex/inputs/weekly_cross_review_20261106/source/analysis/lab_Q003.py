"""Lab Q003: 6E into / out of the 4 pm London fix (month-end and every day). Pre-registration:
checks/candidates/lab_Q003/PREREG.md. Stages 1-2 on 2018-22; stage 3 (2023-onward) only with --holdout.
  python3 analysis/lab_Q003.py [--holdout]
"""
import sys, os, pickle, warnings, datetime as dt; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo
from grid24 import Grid24, jof
import metrics as M

PV, TICK, COMM = 125_000.0, 0.00005, 5.0
COST = COMM + 2 * TICK * PV                       # $17.50
PK = "scratch_data/e6.pkl"
HOLD = "--holdout" in sys.argv
LON, CT = ZoneInfo("Europe/London"), ZoneInfo("America/Chicago")


def load():
    if os.path.exists(PK): return pickle.load(open(PK, "rb"))
    g = Grid24("data/6E_1min_20*.csv", night_pattern=""); pickle.dump(g, open(PK, "wb"), protocol=4); return g


def fix_col(ts):
    d = pd.Timestamp(ts).date()
    t = dt.datetime(d.year, d.month, d.day, 16, 0, tzinfo=LON).astimezone(CT)
    return t.hour * 60 + t.minute


def trade(g, r, F, v):
    """$ P&L of variant v on row r with fix column F (None if not traded)."""
    c, o = g.c[r], g.o[r]
    if v in (1, 3):
        a, b, e, x = c[F - 30], c[F - 5], o[F - 4], c[F]
        mv = b - a; s = np.sign(mv)
    else:
        a, b, e, x = c[F - 30], c[F], o[F + 2], c[F + 30]
        mv = b - a; s = -np.sign(mv)
    if not np.all(np.isfinite([a, b, e, x])) or s == 0: return None
    return s * (x - e) * PV - COST


def run(g, rows, cols, v):
    out = {}
    for r, F in zip(rows, cols):
        p = trade(g, r, F, v)
        if p is not None: out[pd.Timestamp(g.ts[r])] = p
    return pd.Series(out, dtype=float).sort_index()


def tstat(x): return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan
def pf(x): return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def show(x, nm):
    by = x.groupby(x.index.year).sum()
    print(f"  {nm:<30} n={len(x):4d} avg ${x.mean():6.1f} (gross ${x.mean() + COST:5.1f}) PF {pf(x):4.2f} t {tstat(x):5.2f} "
          f"win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}  " + " ".join(f"{y}:{v:+.0f}" for y, v in by.items()))


if __name__ == "__main__":
    g = load(); rows = g.trading
    idx = pd.DatetimeIndex(g.ts[rows])
    me = pd.Series(idx, index=idx).groupby(idx.to_period("M")).transform("max").to_numpy() == idx.to_numpy()
    F = np.array([fix_col(t) for t in g.ts[rows]])
    print(f"sessions {len(rows)}; month-ends {me.sum()}; fix at 11:00 CT on {np.mean(F == 660):.1%} of days")
    yr = idx.year; D = (yr >= 2018) & (yr <= 2022); H = yr >= 2023
    print(f"cost ${COST:.2f} a round trip\n\nStage 1 (2018-22)")
    T = {1: run(g, rows[D & me], F[D & me], 1), 2: run(g, rows[D & me], F[D & me], 2), 3: run(g, rows[D], F[D], 3)}
    for v, nm in ((1, "V1 month-end follow into fix"), (2, "V2 month-end fade after fix"), (3, "V3 follow into fix, all days")):
        show(T[v], nm)
    best = max(T, key=lambda v: tstat(T[v])); x = T[best]
    s1 = tstat(x) >= 2.0 and pf(x) >= 1.15 and len(x) >= (80 if best == 3 else 40)
    print(f"  best V{best}: stage 1 {'PASS' if s1 else 'FAIL'}")
    rng = np.random.default_rng(7)
    if best in (1, 2):
        pool = np.where(D & ~me)[0]; P = run(g, rows[pool], F[pool], best).reindex(pd.DatetimeIndex(g.ts[rows[pool]]))
        pm = [P.iloc[rng.choice(len(P), int((D & me).sum()), replace=False)].mean() for _ in range(500)]
    else:
        hours = [h * 60 for h in range(3, 15) if h not in (10, 11)]; pm = []
        for _ in range(500):
            cols = rng.choice(hours, D.sum()); pm.append(run(g, rows[D], cols, 3).mean())
    pm = np.array(pm); p = np.mean(pm >= x.mean())
    by = x.groupby(x.index.year).sum(); s2 = p < 0.05 and (by > 0).sum() >= 4
    print(f"\nStage 2 placebo V{best}: placebo avg ${np.nanmean(pm):.1f}, p = {p:.3f}; stage 2 {'PASS' if s2 else 'FAIL'}")
    daily = x.reindex(pd.date_range("2018-01-01", "2022-12-31", freq="B"), fill_value=0.0); m = M.perf(daily, x)
    print("  metrics V%d 2018-22: Sharpe %.2f Sortino %.2f PF %.2f Calmar %.2f Ulcer %.2f" %
          (best, m["sharpe"], m["sortino"], m["profit_factor"], m["calmar"], m["ulcer"]))
    for nm, xs in (("longs", x[x.index.isin(x.index)]),): pass
    if HOLD and s1 and s2:
        sel = H & (me if best in (1, 2) else True)
        h = run(g, rows[sel], F[sel], best); print("\nStage 3 holdout (one look)"); show(h, f"V{best} 2023-onward")
        show(pd.concat([x, h]), f"V{best} full 2018-onward")
