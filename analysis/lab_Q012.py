"""Lab Q012: 6E after the ECB decision / press conference. Pre-registration: checks/candidates/lab_Q012/PREREG.md.
Stages 1-2 on 2018-22; stage 3 (2023-onward) only with --holdout.   python3 analysis/lab_Q012.py [--holdout]
"""
import sys, warnings, datetime as dt; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo
from grid24 import jof
import metrics as M
from lab_Q003 import load, PV, TICK, COMM, COST, tstat, pf, show

HOLD = "--holdout" in sys.argv
BER, CT = ZoneInfo("Europe/Berlin"), ZoneInfo("America/Chicago")


def ct_col(ts, hh, mm):
    d = pd.Timestamp(ts).date(); t = dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=BER).astimezone(CT)
    return t.hour * 60 + t.minute


def ratio(g, r, T0):
    base = np.nanmedian(g.v[r, T0 - 15 + 1:T0 + 1])          # bars ending T0-14 .. T0
    return g.v[r, T0 + 1] / base if base > 0 else np.nan


def ecb_days(g):
    rows = g.trading[pd.DatetimeIndex(g.ts[g.trading]).dayofweek == 3]
    out, other = {}, []
    for r in rows:
        # amendment 1: decision time by date (13:45 Berlin before 2022-07-01, 14:15 after)
        T0 = ct_col(g.ts[r], 13, 45) if pd.Timestamp(g.ts[r]) < pd.Timestamp("2022-07-01") else ct_col(g.ts[r], 14, 15)
        q = ratio(g, r, T0)
        if np.isfinite(q) and q >= 5: out[r] = T0
        else: other.append(r)
    return out, np.array(other)


def trade(g, r, T0, v, atr):
    c = g.c[r]; a = atr[r]
    m = c[T0 + 90] - c[T0] if v in (1, 2) else c[T0 + 90] - c[T0 + 30]
    s = np.sign(m) * (-1 if v == 2 else 1)
    j0, j1 = T0 + 92, jof(1030)
    if not np.isfinite(s) or s == 0 or not np.isfinite(a) or j0 >= j1: return None
    o, h, l, cl = g.o[r, j0:j1 + 1], g.h[r, j0:j1 + 1], g.l[r, j0:j1 + 1], g.c[r, j0:j1 + 1]
    if not np.isfinite(o[0]): return None
    ent = o[0]; stop = ent - s * 0.3 * a; px = None
    for i in range(len(o)):
        if not np.isfinite(h[i]): continue
        if s > 0 and l[i] <= stop: px = min(stop, o[i]) - TICK; break
        if s < 0 and h[i] >= stop: px = max(stop, o[i]) + TICK; break
    if px is None:
        last = cl[np.isfinite(cl)]; px = last[-1] - s * TICK
    return s * (px - ent) * PV - COMM - TICK * PV


def run(g, items, v, atr):
    out = {}
    for r, T0 in items:
        p = trade(g, r, T0, v, atr)
        if p is not None: out[pd.Timestamp(g.ts[r])] = p
    return pd.Series(out, dtype=float).sort_index()


if __name__ == "__main__":
    g = load(); atr = g.daily_atr(14); E, other = ecb_days(g)
    yr = lambda r: pd.Timestamp(g.ts[r]).year
    by_y = pd.Series([yr(r) for r in E]).value_counts().sort_index()
    print("ECB days found by year: " + " ".join(f"{y}:{n}" for y, n in by_y.items()))
    print("first few:", [str(pd.Timestamp(g.ts[r]).date()) + f"@{T // 60:02d}:{T % 60:02d}" for r, T in list(E.items())[:6]])
    D = [(r, T) for r, T in E.items() if 2018 <= yr(r) <= 2022]; H = [(r, T) for r, T in E.items() if yr(r) >= 2023]
    print(f"design {len(D)}, holdout {len(H)}; cost ${COST:.2f}\n\nStage 1 (2018-22)")
    T = {v: run(g, D, v, atr) for v in (1, 2, 3)}
    for v, nm in ((1, "V1 follow decision->+90"), (2, "V2 fade it"), (3, "V3 follow +30->+90")): show(T[v], nm)
    best = max(T, key=lambda v: tstat(T[v])); x = T[best]
    s1 = tstat(x) >= 2.0 and pf(x) >= 1.15 and len(x) >= 40
    print(f"  best V{best}: stage 1 {'PASS' if s1 else 'FAIL'}")
    od = other[[2018 <= yr(r) <= 2022 for r in other]]
    Tmode = pd.Series([T0 for _, T0 in D]).mode()[0]          # placebo uses each draw's matched ECB clock
    rng = np.random.default_rng(7); clocks = np.array([T0 for _, T0 in D]); pm = []
    P = {T0: run(g, [(r, T0) for r in od], best, atr).reindex(pd.DatetimeIndex(g.ts[od])) for T0 in np.unique(clocks)}
    for _ in range(500):
        pick = rng.choice(len(od), len(D), replace=False)
        vals = [P[c].iloc[i] for i, c in zip(pick, clocks)]; pm.append(np.nanmean(vals))
    p = np.mean(np.array(pm) >= x.mean()); by = x.groupby(x.index.year).sum(); s2 = p < 0.05 and (by > 0).sum() >= 4
    print(f"\nStage 2 placebo V{best}: other Thursdays avg ${np.nanmean(pm):.1f}, p = {p:.3f}; stage 2 {'PASS' if s2 else 'FAIL'}")
    daily = x.reindex(pd.date_range("2018-01-01", "2022-12-31", freq="B"), fill_value=0.0); m = M.perf(daily, x)
    print("  metrics V%d 2018-22: Sharpe %.2f Sortino %.2f PF %.2f Calmar %.2f Ulcer %.2f" %
          (best, m["sharpe"], m["sortino"], m["profit_factor"], m["calmar"], m["ulcer"]))
    if HOLD and s1 and s2:
        h = run(g, H, best, atr); print("\nStage 3 holdout (one look)"); show(h, f"V{best} 2023-onward")
        show(pd.concat([x, h]), f"V{best} full 2018-onward")
