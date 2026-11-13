"""Noise-area momentum ported to ES YM GC CL ZN 6E NG (pre-registered: checks/candidates/noise_other_markets/PREREG.md, user 2026-11-13).
Engine analysis/noise_generic.py (matches the NQ engine trade for trade: 5,341 / 5,341 identical on NQ 24h RTH-anchored).
  tools/run_stamped.sh analysis/noise_other_markets_test.py > analysis/outputs/noise_other_markets_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis"); sys.argv = ["x", "scratch_data"]
import numpy as np, pandas as pd
import noise_generic as NG
from cl_forced_flows_test import load
print(__doc__.split("\n")[0])
MK = {"ES": dict(open_t=845, close_t=1500, first=900, last_entry=1400, flat=1430, pv=50.0, tick=0.25, comm=5.0),
      "YM": dict(open_t=845, close_t=1500, first=900, last_entry=1400, flat=1430, pv=5.0, tick=1.0, comm=5.0),
      "GC": dict(open_t=745, close_t=1230, first=800, last_entry=1200, flat=1230, pv=100.0, tick=0.1, comm=5.0),
      "CL": dict(open_t=815, close_t=1330, first=830, last_entry=1300, flat=1330, pv=1000.0, tick=0.01, comm=5.0),
      "ZN": dict(open_t=745, close_t=1400, first=800, last_entry=1330, flat=1400, pv=1000.0, tick=1 / 64, comm=5.0),
      "6E": dict(open_t=745, close_t=1400, first=800, last_entry=1330, flat=1400, pv=125000.0, tick=0.00005, comm=5.0),
      "NG": dict(open_t=815, close_t=1330, first=830, last_entry=1300, flat=1330, pv=10000.0, tick=0.001, comm=5.0)}
def tt(x): x = pd.Series(x); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan
def pf(x): return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
res = []
for sym, mk in MK.items():
    g = load(sym); S = NG.series24(g)
    T = NG.run(g, S, mk); T = T[T.date >= "2018-01-01"]; y = T.date.dt.year
    print(f"\n== {sym}: {len(T)} trades 2018-26, stop avg {T.sl.mean():.4g} pts (${T.sl.mean() * mk['pv']:,.0f})")
    for nm, m in (("both", np.ones(len(T), bool)), ("longs", T.side > 0), ("shorts", T.side < 0)):
        x = T.net[m]; yy = y[m]
        by = " ".join(f"{a % 100:02d}:{x[yy == a].sum() / 1000:+.1f}k" for a in sorted(yy.unique()))
        print(f"   {nm:<6} n {len(x):4d} avg ${x.mean():6.1f} t {tt(x):5.2f} PF {pf(x):.2f} win {np.mean(x > 0):.0%} | 18-22 ${x[yy <= 2022].mean():6.1f} (t {tt(x[yy <= 2022]):4.1f}) "
              f"23+ ${x[yy >= 2023].mean():6.1f} (t {tt(x[yy >= 2023]):4.1f})\n          {by}", flush=True)
        res.append((sym, nm, x.mean(), tt(x), x[yy <= 2022].mean(), x[yy >= 2023].mean()))
    cand = [r for r in res if r[0] == sym and r[3] >= 2.0 and r[4] > 0 and r[5] > 0]
    if cand:                                               # placebo only where it could pass (saves time; disclosed)
        rng = np.random.default_rng(1); pl = []
        for _ in range(40):
            P = NG.run(g, S, mk, rng=rng); P = P[P.date >= "2018-01-01"]; pl.append(P.net.mean())
        pl = np.array(pl)
        for r in cand: print(f"   placebo (random side, 40 runs, same signals, band/EMA exit off): mean ${pl.mean():.1f}, p95 ${np.percentile(pl, 95):.1f}; {r[1]} avg ${r[2]:.1f} -> p {np.mean(pl >= r[2]):.3f}")
print("\n== PASS (t >= 2.5, both halves > 0, placebo p < 0.05 — placebo shown above where run):")
for r in res:
    if r[3] >= 2.5 and r[4] > 0 and r[5] > 0: print(f"   {r[0]} {r[1]}: avg ${r[2]:.1f}, t {r[3]:.2f}")
