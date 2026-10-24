"""Checker's robustness / leak probes for PAPERTREND v2 (built on the replica's logic).
  python3 checks/candidates/papertrend/robustness.py
"""
import sys, os, pickle, warnings; warnings.filterwarnings("ignore")
ROOT = "/home/user/thebeginning"; sys.path.insert(0, ROOT + "/analysis"); os.chdir(ROOT)
import numpy as np, pandas as pd
from grid24 import jof
import s_rank_gap_round2_test as SR

PV, COST = 20.0, 17.25
g = pickle.load(open("scratch_data/g24.pkl", "rb"))
O, H, L, C = g.o, g.h, g.l, g.c
ts = pd.DatetimeIndex(g.ts); j831, j1455, j1500 = jof(831), jof(1455), jof(1500)
rows = [r for r in range(g.D) if ts[r].dayofweek < 5 and not np.isnan(C[r, j1455]) and not np.isnan(C[r, j1500])]
S = pd.DataFrame(dict(row=rows, date=ts[rows], O=O[rows, j831],
                      rng=np.nanmax(H[rows, j831:j1500 + 1], 1) - np.nanmin(L[rows, j831:j1500 + 1], 1), C=C[rows, j1500]))
S["gap"] = S.O - S.C.shift(1); S["prow"] = S.row.shift(1)
SY = SR.Sym("NQ", g); rb = np.array(sorted(SR.rolls_index(SY)[0]))
S["roll"] = [bool(((rb >= int(p) * 1440 + j1500 + 1) & (rb <= r * 1440 + j831)).any()) if p == p else False
             for p, r in zip(S.prow, S.row)]
M15 = [jof(h * 100 + m) for h in range(8, 15) for m in (0, 15, 30, 45) if 845 <= h * 100 + m <= 1400]


def run(k=0.5, n_atr=14, skip7=7, gapmode="with", marks=M15, delay=1, exit_j=j1455, drop_roll=True, at_close=False,
        side_mode=None, seed=None):
    atr = S.rng.rolling(n_atr).mean().shift(1)
    skip = (S.rng.shift(1) >= S.rng.rolling(skip7).max().shift(1)) if skip7 else pd.Series(False, index=S.index)
    rng = np.random.default_rng(seed) if seed is not None else None
    out = []
    for i in range(len(S)):
        s = S.iloc[i]
        if s.date < pd.Timestamp("2018-01-01") or np.isnan(atr[i]) or skip[i] or (drop_roll and s.roll): continue
        if gapmode != "none" and (np.isnan(s.gap) or s.gap == 0): continue
        r = int(s.row); up, dn = s.O + k * atr[i], s.O - k * atr[i]
        gs = np.sign(s.gap) * (-1 if gapmode == "against" else 1)
        side = None
        for m in marks:
            c = C[r, m]
            if np.isnan(c): continue
            if c > up and (gapmode == "none" or gs > 0): side = 1; break
            if c < dn and (gapmode == "none" or gs < 0): side = -1; break
        if side is None: continue
        if side_mode == "long": side = 1
        if side_mode == "random": side = rng.choice([-1, 1])
        if at_close: entry = C[r, m]
        else:
            kk = np.where(~np.isnan(O[r, m + delay:exit_j + 1]))[0]
            if not len(kk): continue
            entry = O[r, m + delay + kk[0]]
        ex = C[r, exit_j]
        if np.isnan(ex): continue
        out.append(dict(date=s.date, side=side, net=side * (ex - entry) * PV - COST, atrpts=side * (ex - entry) / atr[i]))
    return pd.DataFrame(out)


def summ(nm, t):
    x = t.net; y = t.date.dt.year; a, b = x[y < 2023], x[y >= 2023]
    tt = lambda v: v.mean() / v.std() * np.sqrt(len(v)) if len(v) > 2 else np.nan
    pf = x[x > 0].sum() / -x[x < 0].sum(); by = x.groupby(y).sum()
    Lg, Sh = x[t.side > 0], x[t.side < 0]
    print(f"{nm:<42} n {len(x):4d} avg ${x.mean():6.0f} t {tt(x):4.1f} PF {pf:4.2f} yrs+ {(by > 0).sum()}/{len(by)} | "
          f"18-22 ${a.mean():5.0f} t {tt(a):4.1f} | 23+ ${b.mean():5.0f} t {tt(b):4.1f} | L {len(Lg)} ${Lg.mean():5.0f} "
          f"S {len(Sh)} ${Sh.mean():5.0f} | ATR-units t {tt(t.atrpts):4.1f}")
    return t


base = summ("BASE (spec)", run())
summ("roll days kept", run(drop_roll=False))
for k in (0.25, 0.4, 0.6, 0.75, 1.0): summ(f"band k={k}", run(k=k))
for n in (10, 20): summ(f"ATR {n}", run(n_atr=n))
summ("no skip filter", run(skip7=0))
summ("skip filter = widest of 5", run(skip7=5))
summ("no gap filter (either side)", run(gapmode="none"))
summ("gap filter reversed (against gap)", run(gapmode="against"))
summ("marks every 5 min 08:35-14:00", run(marks=[jof(h * 100 + m) for h in range(8, 15) for m in range(0, 60, 5)
                                               if 835 <= h * 100 + m <= 1400]))
summ("marks every 1 min 08:32-14:00", run(marks=[j for j in range(jof(832), jof(1400) + 1)]))
summ("marks 15-min to 12:00 only", run(marks=[m for m in M15 if m <= jof(1200)]))
summ("entry at the mark close (no delay)", run(at_close=True))
summ("entry 5 min late", run(delay=5))
summ("exit 15:00 close", run(exit_j=j1500))
summ("exit 13:00 close", run(exit_j=jof(1300)))
summ("same days, always long", run(side_mode="long"))
r = [run(side_mode="random", seed=s).net.mean() for s in range(30)]
print(f"random side on the base days (30 runs, with re-scan): mean ${np.mean(r):.0f}, max ${np.max(r):.0f}")

# by-year and long/short of the base, and concentration
y = base.date.dt.year
print(base.groupby([y, "side"]).net.agg(["count", "sum"]).unstack().round(0))
x = base.net.sort_values(ascending=False)
print(f"top 10 trades ${x.head(10).sum():,.0f} of ${x.sum():,.0f}; top 28 (5%) ${x.head(28).sum():,.0f}")
