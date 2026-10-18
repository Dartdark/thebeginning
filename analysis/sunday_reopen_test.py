"""NQ Sunday reopen first-minute push (user's 'NQ_WKND_v2' write-up, 2026-10-18), rebuilt on our 1-minute data (CT):
gap = first price at the 17:00 CT reopen (open of the bar stamped 17:01) vs Friday's last price; trade in the gap's
direction at that first price (+ k ticks worse), out at the close of that first minute (17:01:00). Skip roll weekends
(4th-20th of Mar / Jun / Sep / Dec). Reopens after a weekday holiday closure (> 1.6 days) count, as in the write-up.
Fill realism (the write-up's open question): entry k = 0 / 1 / 2 / 4 ticks worse than the first print; and 'one minute
late' = enter at the 17:01 close, out at the 17:02 close. Costs $14.50 + 2 ticks per NQ round trip (write-up: $3.50 + 2 ticks).
Same rule on ES and YM. Per contract.
  python3 analysis/sunday_reopen_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MK = {"NQ": ("g24", 20.0, 0.25, 14.5), "ES": ("ge", 50.0, 0.25, 10.0), "YM": ("gy", 5.0, 1.0, 10.0)}


def reopens(g):
    c = g.c.ravel(); ok = np.flatnonzero(~np.isnan(c)); gap = np.diff(ok); k = np.flatnonzero(gap >= int(1.6 * 1440))
    out = []
    for i in k:
        j_prev, j = ok[i], ok[i + 1]
        if j % 1440 != jof(1701): continue                                # the reopen bar must be the 17:00 CT minute
        ts = pd.Timestamp(g.ts[j // 1440])
        if ts.month in (3, 6, 9, 12) and 4 <= ts.day <= 20: continue
        out.append((ts, j_prev, j))
    return out


def line(x, dates, nm):
    x = pd.Series(np.asarray(x, float), index=pd.DatetimeIndex(dates)); t = x.mean() / x.std() * np.sqrt(len(x))
    yrs = x.groupby(x.index.year).sum(); a, b, c = x[x.index < "2022"], x[(x.index >= "2022") & (x.index < "2024")], x[x.index >= "2024"]
    print(f"   {nm:<38} n={len(x):3d} ${x.mean():5.0f} t {t:4.1f} win {np.mean(x > 0):.0%} yrs+ {(yrs > 0).sum()}/{len(yrs)} | "
          f"-2021 ${a.mean():.0f}  22-23 ${b.mean():.0f}  24+ ${c.mean():.0f} | worst ${x.min():,.0f}")


if __name__ == "__main__":
    for sym, (f, pv, tick, com) in MK.items():
        g = pickle.load(open(SP + f + ".pkl", "rb")); c = g.c.ravel(); o = g.o.ravel()
        R = [(ts, jp, j) for ts, jp, j in reopens(g) if ts >= pd.Timestamp("2017-01-01")]
        dates = [r[0] for r in R]; side = np.array([np.sign(o[j] - c[jp]) for _, jp, j in R])
        first, m1 = np.array([o[j] for _, _, j in R]), np.array([c[j] for _, _, j in R])
        m2 = np.array([c[j + 1] if not np.isnan(c[j + 1]) else c[j] for _, _, j in R])
        cost = com + 2 * tick * pv
        print(f"\n{sym}: {len(R)} reopens (roll weekends skipped); gap = 0 on {np.sum(side == 0)}")
        m = side != 0
        print(f"   gross push 17:00 first print -> 17:01: {np.mean(((m1 - first) * side)[m] / first[m]) * 1e4:.1f} bp")
        for k in (0, 1, 2, 4):
            pnl = ((m1 - (first + side * k * tick)) * side - tick) * pv - com      # exit 1 tick worse at 17:01
            line(pnl[m], np.array(dates)[m], f"enter first print + {k} ticks, out 17:01")
        late = ((m2 - m1) * side) * pv - cost
        line(late[m], np.array(dates)[m], "one minute late: 17:01 -> 17:02")
