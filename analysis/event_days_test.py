"""Tests of event_days.py ideas (2026-10-11). Expects pickled NQ/ES grids from a scratch run;
kept as the record of the test. The release-fade grid is the commented block at the end."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
from grid24 import jof
import event_days as E
for name, f, pv, cost in (("NQ", "g24.pkl", 20, 7.25 + 2*5), ("ES", "ge.pkl", 50, 5 + 2*12.5)):
    g = pickle.load(open(f"/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/{f}","rb"))
    chk = E.check_fomc(g)
    print(f"\n{name}: FOMC dates found {len(chk)}, 13:00-13:10 range vs normal: median {chk.median():.1f}x, min {chk.min():.1f}x on {pd.Timestamp(chk.idxmin()).date()}")
    tr = g.trading
    C = pd.DataFrame(g.c).ffill(axis=1).to_numpy()
    yr = pd.Series(pd.DatetimeIndex(g.ts).year, index=range(len(g.ts)))
    fom = E.rows_of(g, E.FOMC_DATES)
    prev = {d: tr[np.searchsorted(tr, d) - 1] for d in fom}
    rel = E.release_days(g)
    rel = rel[pd.DatetimeIndex(g.ts[rel]).year >= 2018]
    normal = np.setdiff1d(tr[pd.DatetimeIndex(g.ts[tr]).year >= 2018], np.r_[fom, rel])
    def w(rows, a, b):
        x = (C[rows, jof(b)] - C[rows, jof(a)]) * pv
        return x[~np.isnan(x)]
    def rep(lab, x):
        by = pd.Series(x).groupby(yr.reindex(rows_used).to_numpy()[:len(x)]).mean() if False else None
        print(f"  {lab:<52} n={len(x):4d} gross ${x.mean():7.0f} net ${x.mean()-cost:7.0f} win {(x-cost>0).mean():.0%} t={x.mean()/x.std()*np.sqrt(len(x)):4.1f}")
    print(f" Pre-FOMC drift (long)")
    rep("FOMC day 8:30 -> 12:55 CT", w(fom, 830, 1255))
    rep("FOMC day 0:00 -> 12:55 CT", w(fom, 0, 1255))
    rep("day before FOMC 13:00 -> 15:00 CT", w(np.array(list(prev.values())), 1300, 1500))
    rep("normal days 8:30 -> 12:55 CT (comparison)", w(normal, 830, 1255))
    rep("FOMC day 13:00 -> 15:00 CT (after statement)", w(fom, 1300, 1500))
    print(f" Macro release days (7:30 CT spike), {len(rel)} days")
    rep("release day long 8:30 -> 15:00", w(rel, 830, 1500))
    rep("normal day long 8:30 -> 15:00 (comparison)", w(normal, 830, 1500))
    # follow the 7:30 reaction: direction of 7:29 -> 8:00 move, hold 8:30 -> 15:00
    d = np.sign(C[rel, jof(800)] - C[rel, jof(729)])
    x = d * (C[rel, jof(1500)] - C[rel, jof(830)]) * pv; x = x[~np.isnan(x)]
    rep("release day: follow the 7:30-8:00 reaction, 8:30 -> 15:00", x)
    x = d * (C[rel, jof(830)] - C[rel, jof(800)]) * pv; x = x[~np.isnan(x)]
    rep("release day: follow the 7:30-8:00 reaction, 8:00 -> 8:30", x)
    # pre-FOMC by year
    x = w(fom, 830, 1255); y = pd.DatetimeIndex(g.ts[fom]).year
    print("  pre-FOMC 8:30->12:55 by year:", pd.Series(x, index=y[:len(x)]).groupby(level=0).mean().round().to_dict())
# import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
# import numpy as np, pandas as pd
# from grid24 import jof
# import event_days as E
# for name, f, pv, cost in (("NQ", "g24.pkl", 20, 7.25 + 2*5), ("ES", "ge.pkl", 50, 5 + 2*12.5)):
#     g = pickle.load(open(f"/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/{f}","rb"))
#     C = pd.DataFrame(g.c).ffill(axis=1).to_numpy()
#     for mult in (2.0, 3.0, 4.0):
#         rel = E.release_days(g, mult=mult); rel = rel[pd.DatetimeIndex(g.ts[rel]).year >= 2018]
#         y = pd.DatetimeIndex(g.ts[rel]).year
#         for react_end, a, b in ((745, 745, 830), (800, 800, 830), (800, 800, 900), (800, 800, 1500)):
#             d = -np.sign(C[rel, jof(react_end)] - C[rel, jof(729)])     # fade
#             x = d * (C[rel, jof(b)] - C[rel, jof(a)]) * pv
#             ok = ~np.isnan(x); x2, yy = x[ok], y[ok]
#             by = pd.Series(x2 - cost).groupby(yy).mean()
#             print(f"{name} spike>{mult}x fade reaction 7:29->{react_end}, hold {a}->{b}: n={len(x2)} net ${x2.mean()-cost:5.0f} t={x2.mean()/x2.std()*np.sqrt(len(x2)):4.1f} yrs+ {(by>0).sum()}/{len(by)}")
