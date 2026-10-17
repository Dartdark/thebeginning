"""Month-end Treasury index extension on ZN (2026-10-17, literature scan): bond index funds must buy duration at the
month-end index rebalance (the 3pm ET = 14:00 CT close on the last business day), more in refunding months
(Feb / May / Aug / Nov). Dealers publish the expected extension in advance.
PRE-REGISTERED: long 1 ZN, $1,000 / point, $7.25 + 1 tick (1/64 = $15.625) per fill.
  A  last business day of the month, 7:21 open -> 13:59 close CT (main)
  B  the business day before it, same window
  C  last business day, 12:00 -> 13:59 (afternoon)
  split: refunding months vs others; placebos: the same window on all other days, on the first business day
  python3 analysis/zn_month_end_test.py
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from cl_forced_flows_test import load
import metrics as M, montecarlo as MC, resampling as R

PV, TICK, COMM = 1000.0, 1 / 64, 7.25


def tstat(x): x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def line(x, nm):
    x = pd.Series(x).dropna(); y = x.index.year; a, b = x[y < 2023], x[y >= 2023]; by = x.groupby(y).sum()
    pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return (f"   {nm:<46} n {len(x):4d} avg ${x.mean():6.1f} PF {pf:4.2f} win {np.mean(x > 0):3.0%} t {tstat(x):+4.1f} yrs+ {(by > 0).sum()}/{len(by)} | "
            f"18-22 ${a.mean():6.1f} (t {tstat(a):+4.1f}) | 23+ ${b.mean():6.1f} (t {tstat(b):+4.1f})")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = load("ZN"); ts = pd.DatetimeIndex(g.ts)
    tr = g.trading[(ts[g.trading] >= "2018-01-01") & (g.last_j[g.trading] >= jof(1359))]
    d = pd.DatetimeIndex(ts[tr]); C = pd.DataFrame(g.c[tr]).ffill(axis=1).to_numpy()
    def leg(a, b):
        o = g.o[tr, jof(a)]; c = C[:, jof(b)]
        return pd.Series(((c - o) - 2 * TICK) * PV - 2 * COMM, index=d)
    day = leg(721, 1359); aft = leg(1200, 1359)
    per = d.to_period("M"); last = pd.Series(d, index=d).groupby(per).transform("max") == d
    first = pd.Series(d, index=d).groupby(per).transform("min") == d
    pos = pd.Series(np.arange(len(d)), index=d); prev = pd.Series(False, index=d)
    prev.iloc[(pos[last].to_numpy() - 1)[pos[last].to_numpy() > 0]] = True
    refund = d.month.isin([2, 5, 8, 11])
    lastm, prevm, firstm = last.to_numpy(), prev.to_numpy(), first.to_numpy()
    print(f"\n{len(d)} ZN days 2018-26; month-ends {lastm.sum()}")
    print(line(day[lastm], "A last business day 7:21 -> 13:59 (long)"))
    print(line(day[prevm], "B day before 7:21 -> 13:59"))
    print(line(aft[lastm], "C last business day 12:00 -> 13:59"))
    print(line(day[lastm & refund], "A, refunding months (Feb/May/Aug/Nov)"))
    print(line(day[lastm & ~refund], "A, other months"))
    print(line(day[~lastm & ~prevm], "placebo: all other days 7:21 -> 13:59"))
    print(line(day[firstm], "placebo: first business day 7:21 -> 13:59"))
    print(f"   gross (before costs) A: ${(day[lastm] + 2 * TICK * PV + 2 * COMM).mean():.1f} a trade; other days ${(day[~lastm & ~prevm] + 2 * TICK * PV + 2 * COMM).mean():.1f}")
    t = day[lastm]; days = pd.bdate_range(d[0], d[-1]); dl = t.groupby(t.index.normalize()).sum().reindex(days, fill_value=0)
    print("\n" + M.table({"ZN month-end long (A), per ZN": (dl, t)}))
    b_, p_ = R.report({"ZN month-end A, 2023+": dl[dl.index >= "2023-01-01"]}, n=2000); print(b_); print(p_)
    print(MC.report(t.to_numpy(), dl.to_numpy(), size=1, label="per ZN"))
