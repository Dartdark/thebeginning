"""Lab Q016: ES / ZN drift before 09:00 CT releases (ISM manufacturing, Conference Board) -> follow after the release.
Pre-registration: checks/candidates/lab_Q016/PREREG.md. Stages 1-2 on 2018-22; stage 3 only with --holdout.
  python3 analysis/lab_Q016.py [--holdout]
"""
import sys, os, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay
from grid24 import Grid24, jof
import metrics as M

HOLD = "--holdout" in sys.argv
SPEC = {"ES": dict(pv=50.0, tick=0.25, comm=5.0), "ZN": dict(pv=1000.0, tick=1 / 64, comm=5.0)}


def load(sym):
    pk = "scratch_data/ge.pkl" if sym == "ES" else "scratch_data/zn.pkl"
    if os.path.exists(pk): return pickle.load(open(pk, "rb"))
    g = Grid24(f"data/{sym}_1min_20*.csv", night_pattern=""); pickle.dump(g, open(pk, "wb"), protocol=4); return g


def vr(g, r, stamp):
    j = jof(stamp); base = np.nanmedian(g.v[r, j - 15:j]); return g.v[r, j] / base if base > 0 else np.nan


def release_days(es):
    bd = CustomBusinessDay(calendar=USFederalHolidayCalendar())
    cand = set()
    for y in range(2017, 2027):
        for m in range(1, 13):
            first = pd.Timestamp(y, m, 1); cand.add(first if first == (first - bd + bd) and first.dayofweek < 5 and
                                                    first not in USFederalHolidayCalendar().holidays(first, first) else first + bd)
            last = pd.Timestamp(y, m, 1) + pd.offsets.MonthEnd(0)
            cand.add(last - pd.Timedelta(days=(last.dayofweek - 1) % 7))           # last Tuesday
    pos = {d: i for i, d in enumerate(es.dates)}; keep = []
    for d in sorted(cand):
        r = pos.get(int(d.strftime("%Y%m%d")))
        if r is None or r not in set(es.trading): continue
        # amendment 1: calendar dates alone (no 0901 confirmation); still drop a 07:30 release the same morning
        if not (vr(es, r, 731) >= 3): keep.append(pd.Timestamp(d))
    return keep


def trades(g, sym, days, v, atr):
    sp = SPEC[sym]; pos = {d: i for i, d in enumerate(g.dates)}; out = {}
    xj = jof(930 if v == 2 else 910)
    for d in days:
        r = pos.get(int(d.strftime("%Y%m%d")))
        if r is None: continue
        a = atr[r]; mv = g.c[r, jof(858)] - g.c[r, jof(835)]
        if not (np.isfinite(a) and np.isfinite(mv)) or abs(mv) < 0.05 * a: continue
        s = np.sign(mv); j0 = jof(900)
        o, h, l, c = g.o[r, j0:xj + 1], g.h[r, j0:xj + 1], g.l[r, j0:xj + 1], g.c[r, j0:xj + 1]
        if not np.isfinite(o[0]): continue
        ent = o[0]; stop = ent - s * 0.3 * a; px = None
        for i in range(len(o)):
            if not np.isfinite(h[i]): continue
            if s > 0 and l[i] <= stop: px = min(stop, o[i]) - sp["tick"]; break
            if s < 0 and h[i] >= stop: px = max(stop, o[i]) + sp["tick"]; break
        if px is None:
            last = c[np.isfinite(c)]; px = last[-1] - s * sp["tick"]
        out[d] = s * (px - ent) * sp["pv"] - sp["comm"] - sp["tick"] * sp["pv"]
    return pd.Series(out, dtype=float).sort_index()


def tstat(x): return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan
def pf(x): return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def show(x, nm, cost):
    by = x.groupby(x.index.year).sum()
    print(f"  {nm:<26} n={len(x):4d} avg ${x.mean():6.1f} (gross ${x.mean() + cost:6.1f}) PF {pf(x):4.2f} t {tstat(x):5.2f} "
          f"win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}  " + " ".join(f"{y}:{v:+.0f}" for y, v in by.items()))


if __name__ == "__main__":
    G = {"ES": load("ES"), "ZN": load("ZN")}; A = {k: g.daily_atr(14) for k, g in G.items()}
    days = release_days(G["ES"]); dsg = [d for d in days if 2018 <= d.year <= 2022]; hold = [d for d in days if d.year >= 2023]
    print(f"release days kept: {len(days)} (design {len(dsg)}, holdout {len(hold)})")
    cost = {k: SPEC[k]["comm"] + 2 * SPEC[k]["tick"] * SPEC[k]["pv"] for k in SPEC}
    cfg = {1: ("ES", 1), 2: ("ES", 2), 3: ("ZN", 1)}
    print("\nStage 1 (2018-22)")
    T = {v: trades(G[s], s, dsg, w, A[s]) for v, (s, w) in cfg.items()}
    for v, nm in ((1, "V1 ES follow to 09:10"), (2, "V2 ES follow to 09:30"), (3, "V3 ZN follow to 09:10")): show(T[v], nm, cost[cfg[v][0]])
    best = max(T, key=lambda v: tstat(T[v])); x = T[best]; sym, w = cfg[best]
    s1 = tstat(x) >= 2.0 and pf(x) >= 1.15 and len(x) >= 40
    print(f"  best V{best}: stage 1 {'PASS' if s1 else 'FAIL'}")
    g = G[sym]; rows = g.trading; idx = pd.DatetimeIndex(g.ts[rows])
    other = [d for d in idx if 2018 <= d.year <= 2022 and d not in set(days)]
    P = trades(g, sym, other, w, A[sym]).reindex(other)
    rng = np.random.default_rng(7)
    pm = np.array([P.iloc[rng.choice(len(P), len(dsg), replace=False)].mean() for _ in range(500)])
    p = np.mean(pm >= x.mean()); by = x.groupby(x.index.year).sum(); s2 = p < 0.05 and (by > 0).sum() >= 4
    print(f"\nStage 2 placebo V{best}: non-release days avg ${P.mean():.1f}, p = {p:.3f}; stage 2 {'PASS' if s2 else 'FAIL'}")
    daily = x.reindex(pd.date_range("2018-01-01", "2022-12-31", freq="B"), fill_value=0.0); m = M.perf(daily, x)
    print("  metrics V%d 2018-22: Sharpe %.2f Sortino %.2f PF %.2f Calmar %.2f Ulcer %.2f" %
          (best, m["sharpe"], m["sortino"], m["profit_factor"], m["calmar"], m["ulcer"]))
    if HOLD and s1 and s2:
        h = trades(g, sym, hold, w, A[sym]); print("\nStage 3 holdout (one look)"); show(h, f"V{best} 2023-onward", cost[sym])
        show(pd.concat([x, h]), f"V{best} full 2018-onward", cost[sym])
