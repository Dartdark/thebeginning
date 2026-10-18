"""Midday Range Breakout (user's MultiCharts file midday_breakout.pla, 2026-10-18), Python rebuild on our NQ 1-minute (CT):
lunch range = 11:00-12:30 CT high / low (12:00-13:30 ET); day move = 12:30 close vs 8:30 open, >= 0.2%; range 10-150 pts;
up day: buy stop at lunch high + 2 ticks, entries 12:30-14:00 CT, stop = lunch low - 2 ticks, out 14:55 CT (next bar
market); down day: mirror (the file's default allows shorts; the user's post says long only). One trade a day.
Costs: $14.50 + 2 ticks ($24.50) per NQ round trip (the user used $10).
Checks: longs (as posted), shorts, both; years; 2018-22 / 2023+; a plain control (buy the 12:31 open on qualifying up days,
same exit, no breakout); overlap with Late-Day Flow (MultiCharts trades) on the same days.
  python3 analysis/midday_breakout_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis"); sys.path.insert(0, "analysis/jesse")
import numpy as np, pandas as pd
from grid24 import jof
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
sys.argv = sys.argv[:1]
import compare as C
PV, TICK, COST = 20.0, 0.25, 24.5


def stats(t, nm):
    if len(t) < 5: print(f"   {nm:<36} n={len(t)}"); return
    n = t.net; yrs = n.groupby(t.date.dt.year).sum(); gl = -n[n < 0].sum(); tt = n.mean() / n.std() * np.sqrt(len(n))
    eq = n.cumsum(); dd = (eq - eq.cummax()).min(); a, h = n[t.date < "2023"], n[t.date >= "2023"]
    print(f"   {nm:<36} n={len(n):4d} ${n.mean():5.0f} PF {n[n > 0].sum() / gl:4.2f} t {tt:4.1f} win {np.mean(n > 0):.0%} yrs+ {(yrs > 0).sum()}/{len(yrs)} "
          f"net ${n.sum():,.0f} DD ${dd:,.0f} | 18-22 ${a.mean():.0f} 23+ ${h.mean():.0f}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); rows = []; ctrl = []
    for d in g.trading:
        dt = pd.Timestamp(g.ts[d])
        if dt < pd.Timestamp("2018-01-01") or g.last_j[d] < jof(1500): continue
        O = g.o[d, jof(831)]; H = g.h[d, jof(1101):jof(1230) + 1]; L = g.l[d, jof(1101):jof(1230) + 1]
        c1230 = pd.Series(g.c[d, :jof(1230) + 1]).ffill().iloc[-1]
        if np.isnan(O) or np.isnan(c1230) or np.all(np.isnan(H)): continue
        hi, lo = np.nanmax(H), np.nanmin(L); w = hi - lo; mv = (c1230 - O) / O * 100
        if not (10 <= w <= 150 and abs(mv) >= 0.2): continue
        side = 1 if mv > 0 else -1
        lvl = hi + 2 * TICK if side > 0 else lo - 2 * TICK; sp = lo - 2 * TICK if side > 0 else hi + 2 * TICK
        e = None
        for j in range(jof(1231), jof(1400)):
            if np.isnan(g.h[d, j]): continue
            if (side > 0 and g.h[d, j] >= lvl) or (side < 0 and g.l[d, j] <= lvl):
                e = (max(lvl, g.o[d, j]) if side > 0 else min(lvl, g.o[d, j])) + side * TICK; j0 = j; break
        exit_j = jof(1456)
        x0 = g.o[d, exit_j] if not np.isnan(g.o[d, exit_j]) else pd.Series(g.c[d, :exit_j]).ffill().iloc[-1]
        cx = g.o[d, jof(1231)] + side * TICK
        ctrl.append(dict(date=dt, side=side, net=((x0 - side * TICK) - cx) * side * PV - COST))
        if e is None: continue
        x = None
        for j in range(j0 + 1, exit_j):
            if np.isnan(g.h[d, j]): continue
            if (side > 0 and g.l[d, j] <= sp) or (side < 0 and g.h[d, j] >= sp):
                x = (min(sp, g.o[d, j]) if side > 0 else max(sp, g.o[d, j])) - side * TICK; break
        if x is None: x = x0 - side * TICK
        rows.append(dict(date=dt, side=side, net=(x - e) * side * PV - COST))
    T = pd.DataFrame(rows); Cc = pd.DataFrame(ctrl)
    stats(T[T.side > 0], "longs (as posted)"); stats(T[T.side < 0], "shorts (file default)"); stats(T, "both sides")
    print("   longs by year:", T[T.side > 0].groupby(T.date.dt.year).net.sum().round(0).to_dict())
    stats(Cc[Cc.side > 0], "control: buy 12:31 on the same up days")
    m = C.mc_trades(C.REPORTS["LateDayFlow"][0]); m["day"] = m.entry_time.dt.normalize()
    L = T[T.side > 0].set_index("date")
    both = L.index.intersection(m.day); same = m[m.day.isin(both)]
    print(f"\nOverlap with Late-Day Flow: {len(both)} of {len(L)} midday longs share the day with an LDF trade; "
          f"of those LDF went long on {(same.side > 0).mean():.0%}")
    dl = L.net.groupby(level=0).sum(); m["net"] = m.points * 20 - 24.5; dm = m.groupby("day").net.sum()
    j = pd.concat([dl, dm], axis=1).fillna(0); print(f"   daily P&L correlation with LDF: {j.corr().iloc[0, 1]:.2f}")
    pickle.dump(T, open(SP + "midday_breakout.pkl", "wb"))
