"""Antigravity's per-symbol 'proven structural edges' (2026-10-18): the untested ones, pre-registered (4 trials).
Already tested elsewhere: CL Sunday fade (plan), CL EIA fade (F, -$65), ZN 7:30 releases (F today), ZN auctions (F),
gold vs ZN lead (F), ES MOC (plan), YM vs NQ divergence (fading loses, F).
 1 CL pit-open breakout: range 17:00 (prev) -> 8:00 CT; from 8:00 to 10:30 a stop entry at range high / low (first
   touch), stop at the range midpoint, out 10:30.
 2 ZN pit-open breakout: same with range to 7:20, entries 7:20-10:00, out 10:00.
 3 GC morning continuation: direction of 7:20 -> 8:30, enter 8:30, out 10:30.
 4 GC London PM fix flow: direction of 8:45 -> 9:00 CT, enter 9:00, out 10:30.
Per contract after commission $14.50 + 2 ticks (CL $34.50, GC $34.50, ZN $45.75).
  python3 analysis/anti_symbol_edges_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPEC = {"CL": ("cl", 1000.0, 0.01), "ZN": ("zn", 1000.0, 1 / 64), "GC": ("gc", 100.0, 0.1)}


def line(x, d, nm):
    x = pd.Series(np.asarray(x, float), index=pd.DatetimeIndex(d)).dropna(); t = x.mean() / x.std() * np.sqrt(len(x))
    yrs = x.groupby(x.index.year).sum()
    print(f"   {nm:<40} n={len(x):4d} ${x.mean():6.0f} t {t:4.1f} yrs+ {(yrs > 0).sum()}/{len(yrs)} | 18-22 ${x[x.index < '2023'].mean():.0f} 23+ ${x[x.index >= '2023'].mean():.0f}")


def orb(sym, t_open, t_end):
    f, pv, tick = SPEC[sym]; g = pickle.load(open(SP + f + ".pkl", "rb")); cost = 14.5 + 2 * tick * pv
    tr = g.trading; out, ds = [], []
    for i in range(1, len(tr)):
        d, dp = tr[i], tr[i - 1]; dt = pd.Timestamp(g.ts[d])
        if dt < pd.Timestamp("2018-01-01") or g.last_j[d] < jof(t_end): continue
        H = np.r_[g.h[dp, jof(1701):], g.h[d, :jof(t_open) + 1]]; L = np.r_[g.l[dp, jof(1701):], g.l[d, :jof(t_open) + 1]]
        if np.all(np.isnan(H)): continue
        hi, lo = np.nanmax(H), np.nanmin(L); mid = (hi + lo) / 2; side = 0
        for j in range(jof(t_open) + 1, jof(t_end)):
            if np.isnan(g.h[d, j]): continue
            if g.h[d, j] >= hi: side, e, j0 = 1, max(hi, g.o[d, j]), j; break
            if g.l[d, j] <= lo: side, e, j0 = -1, min(lo, g.o[d, j]), j; break
        if not side: continue
        x = None
        for j in range(j0 + 1, jof(t_end) + 1):
            if np.isnan(g.h[d, j]): continue
            if (side > 0 and g.l[d, j] <= mid) or (side < 0 and g.h[d, j] >= mid): x = mid; break
        if x is None: x = pd.Series(g.c[d, :jof(t_end) + 1]).ffill().iloc[-1]
        out.append((x - e) * side * pv - cost); ds.append(dt)
    return out, ds


def follow(sym, a, b, ex):
    f, pv, tick = SPEC[sym]; g = pickle.load(open(SP + f + ".pkl", "rb")); cost = 14.5 + 2 * tick * pv
    cf = pd.Series(g.c.ravel()).ffill().to_numpy(); out, ds = [], []
    for d in g.trading:
        dt = pd.Timestamp(g.ts[d])
        if dt < pd.Timestamp("2018-01-01") or g.last_j[d] < jof(ex): continue
        P = lambda t: cf[d * 1440 + jof(t)]; s = np.sign(P(b) - P(a))
        if s: out.append((P(ex) - P(b)) * s * pv - cost); ds.append(dt)
    return out, ds


if __name__ == "__main__":
    line(*orb("CL", 800, 1030), "1 CL pit-open breakout 8:00-10:30")
    line(*orb("ZN", 720, 1000), "2 ZN pit-open breakout 7:20-10:00")
    line(*follow("GC", 720, 830, 1030), "3 GC follow 7:20->8:30, hold to 10:30")
    line(*follow("GC", 845, 900, 1030), "4 GC follow 8:45->9:00 (PM fix), to 10:30")
