"""CL round 3 (2026-10-14): new forced-flow windows next to the CL Sunday up-gap fade, 2018-2026, 1 CL, $7.25 + 1 tick a fill.

Pre-specified (before looking):
  a  Friday pre-weekend: Friday 8:00 -> 13:29 long / short; 'fade the week' = against the sum of Mon-Thu day-session
     (8:00 -> 13:29) moves, Friday 8:00 -> 13:29 (placebo: fade week-to-date on Tue-Thu)
  b  Monday after the Sunday up-gap fade (gap >= 0.1 x 15-day ATR, as funded_strategies/CL_Sunday_Gap_Fade.txt): 9:00 -> 13:29
     continue short / go long; split by whether the fade worked (9:00 below the 17:05 Sunday entry); placebo: other Mondays
  c  overnight: long 16:00 -> 8:00 (roll jumps at 17:01 / 03:30-03:35 > 0.3% removed) vs day 8:00 -> 13:29; London open:
     follow the 1:00 -> 2:00 CT move, 2:00 -> 4:00
  python3 analysis/cl_round3_test.py [SCRATCH_DIR]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import load, line

PV, COST = 1000.0, 7.25 + 2 * 0.01 * 1000

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = load("CL"); cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    ts = pd.DatetimeIndex(g.ts); tr = g.trading; days = ts[tr]
    def at(rows, hh): return cf[np.asarray(rows) * 1440 + jof(hh)]
    D = pd.DataFrame({h: at(tr, h) for h in (100, 200, 400, 800, 900, 1329)}, index=days)
    ok = ~np.isnan(g.c[tr, jof(800):jof(1329) + 1]).all(1) & (g.last_j[tr] >= jof(1329)); D = D[ok]
    D = D[D.index >= "2017-12-01"]
    D["day"] = (D[1329] - D[800]) * PV
    # 15-day ATR of day ranges (00:00-23:59 calendar row), known before the date
    hi = pd.Series(np.nanmax(g.h[tr], 1), index=days); lo = pd.Series(np.nanmin(g.l[tr], 1), index=days)
    atr = (hi - lo).rolling(15).mean().shift(1).reindex(D.index)
    print("\na. Friday pre-weekend, 8:00 -> 13:29")
    fri = D.index.dayofweek == 4
    print(line(D.day[fri] - COST, "long Friday", 34)); print(line(-D.day[fri] - COST, "short Friday", 34))
    wk = D.index.to_period("W"); cum = D.day.groupby(wk).cumsum() - D.day          # week-to-date before today
    fade = -np.sign(cum) * D.day - COST
    print(line(fade[fri & (cum != 0)], "fade the week, Friday", 34))
    print(line(fade[D.index.dayofweek.isin([1, 2, 3]) & (cum != 0)], "fade week-to-date, Tue-Thu (placebo)", 34))
    print("\nb. Monday after the Sunday up-gap fade, 9:00 -> 13:29")
    mon = D.index[D.index.dayofweek == 0]; rows = []
    for d in mon:
        sun = d - pd.Timedelta(days=1); fr = d - pd.Timedelta(days=3)
        ks, kf = ts.searchsorted(sun), ts.searchsorted(fr)
        if ks >= len(ts) or ts[ks] != sun or ts[kf] != fr: continue
        fc = g.c[kf][~np.isnan(g.c[kf])]
        so = g.o[ks, jof(1701):jof(1705) + 1]; so = so[~np.isnan(so)]
        e = g.o[ks, jof(1705)]
        if len(fc) == 0 or len(so) == 0 or np.isnan(e) or np.isnan(atr.get(d, np.nan)): continue
        gap = (so[0] - fc[-1]) / atr[d]
        rows.append(dict(d=d, gap=gap, worked=D.loc[d, 900] < e, rest=(D.loc[d, 1329] - D.loc[d, 900]) * PV))
    M = pd.DataFrame(rows).set_index("d"); up = M.gap >= 0.1
    print(f"   Mondays {len(M)}, up-gap >= 0.1 ATR {int(up.sum())}")
    print(line(-M.rest[up] - COST, "up-gap Monday, continue short", 34)); print(line(M.rest[up] - COST, "up-gap Monday, long", 34))
    print(line(-M.rest[up & M.worked] - COST, "  fade worked, continue short", 34))
    print(line(M.rest[up & ~M.worked] - COST, "  fade failed, long", 34))
    print(line(-M.rest[~up] - COST, "other Mondays, short (placebo)", 34))
    print("\nc. overnight vs day, London open")
    lr = np.diff(np.log(cf), prepend=np.nan); lr[np.isnan(lr)] = 0; col = np.arange(len(lr)) % 1440
    lr[np.isin(col, [jof(1701)] + list(range(jof(330), jof(335) + 1))) & (np.abs(lr) > 0.003)] = 0; cum_ = np.cumsum(lr)
    r = np.array([tr[i] for i in range(len(tr)) if days[i] in D.index]); idx = ts[r]
    on = pd.Series(cum_[r[1:] * 1440 + jof(800)] - cum_[r[:-1] * 1440 + jof(1600)], index=idx[1:])
    onx = on * pd.Series(D[800].reindex(idx[1:]).values, index=idx[1:]) * PV - COST
    print(line(onx, "long overnight 16:00 -> 8:00", 34)); print(line(-onx - 2 * COST, "short overnight", 34))
    print(line(D.day - COST, "long day 8:00 -> 13:29", 34))
    lon = np.sign(D[200] - D[100]) * (D[400] - D[200]) * PV - COST
    print(line(lon, "London open: follow 1-2, trade 2-4", 34)); print(line(-lon - 2 * COST, "London open: fade", 34))
