"""Antigravity's 'where real alpha comes from' list (2026-10-18): the two untested parts, pre-registered.
#1 European close and #4 month-end / quarter-end pension rebalancing are already in TIER_LIST (10:30 follow t 2.3, C;
ESEuroCloseTrend F; pension rebalancing t 1.2 / quarter-end t -0.2).
A  NQ after 10-year / 30-year Treasury auctions (12:00 CT result, data/treasury_auctions.csv, 13:00 ET closes, original
   issues and reopenings): 'algos reprice tech' -> follow NQ's 12:00 -> 12:05 move from 12:05 to 13:00 and to 15:00.
   Placebo: the same trade on all other days.
B  Trapped overnight inventory: if >= 90% of overnight volume (17:00 -> 8:29 CT) traded above the prior 15:00 settle
   (or below), and the cash open fails (the 8:30-8:45 range closes back below the 8:30 open for 'above' days, above it
   for 'below' days), trade against the overnight side from 8:45 to 9:00 and to 9:15.
Per NQ after $14.50 + 2 ticks ($24.50).
  python3 analysis/anti_forced_flow_ideas_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, COST = 20.0, 24.5


def line(x, d, nm):
    x = pd.Series(np.asarray(x, float), index=pd.DatetimeIndex(d)).dropna()
    if len(x) < 5: print(f"   {nm:<44} n={len(x)}"); return
    t = x.mean() / x.std() * np.sqrt(len(x)); yrs = x.groupby(x.index.year).sum()
    print(f"   {nm:<44} n={len(x):4d} ${x.mean():6.0f} t {t:4.1f} yrs+ {(yrs > 0).sum()}/{len(yrs)} | 18-22 ${x[x.index < '2023'].mean():.0f} 23+ ${x[x.index >= '2023'].mean():.0f}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    P = lambda d, t: cf[d * 1440 + jof(t)]
    tr = g.trading[pd.DatetimeIndex(g.ts[g.trading]) >= "2018-01-01"]; dts = pd.DatetimeIndex(g.ts[tr]).normalize()
    A = pd.read_csv("data/treasury_auctions.csv"); A = A[A.security_term.str.contains("9-Year|10-Year|29-Year|30-Year") & (A.closing_time_comp == "01:00 PM")]
    adays = set(pd.to_datetime(A.auction_date))
    print("A. NQ after 10y / 30y auctions (follow 12:00 -> 12:05)")
    for ex in (1300, 1500):
        res = {True: ([], []), False: ([], [])}
        for d, dt in zip(tr, dts):
            if g.last_j[d] < jof(1500): continue
            mv = P(d, 1205) - P(d, 1200); s = np.sign(mv)
            if s == 0: continue
            r = ((P(d, ex) - P(d, 1205)) * s - 0.5) * PV - COST
            k = dt in adays; res[k][0].append(r); res[k][1].append(dt)
        line(*res[True], f"auction days, out {ex}"); line(*res[False], f"placebo: other days, out {ex}")
    print("B. Trapped overnight inventory (>= 90% of ON volume one side of the settle, open fails)")
    rows = {900: ([], []), 915: ([], [])}; nsetup = 0
    for i in range(1, len(tr)):
        d, dp = tr[i], tr[i - 1]
        if g.last_j[d] < jof(1500): continue
        settle = P(dp, 1500)
        c = np.r_[g.c[dp, jof(1701):], g.c[d, :jof(829) + 1]]; v = np.r_[g.v[dp, jof(1701):], g.v[d, :jof(829) + 1]]
        ok = ~np.isnan(c) & ~np.isnan(v); 
        if v[ok].sum() <= 0: continue
        up = v[ok][c[ok] > settle].sum() / v[ok].sum()
        side = -1 if up >= 0.9 else (1 if up <= 0.1 else 0)
        if not side: continue
        o = g.o[d, jof(831)]; c845 = P(d, 845)
        if not ((side < 0 and c845 < o) or (side > 0 and c845 > o)): continue
        nsetup += 1
        for ex in (900, 915):
            rows[ex][0].append(((P(d, ex) - c845) * side - 0.5) * PV - COST); rows[ex][1].append(dts[i])
    for ex, (x, dd) in rows.items(): line(x, dd, f"against the overnight side 8:45 -> {ex}")
