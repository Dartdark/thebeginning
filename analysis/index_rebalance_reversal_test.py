"""Franz (2019), 'The Index Effect Minute by Minute' (SSRN 3459744; user, 2026-10-18): index adds / deletes are pushed in
the last 30 minutes of the rebalancing date and reverse in the early hours of the next day (price pressure). That is a
stock-level effect (adds vs deletes net out in the index), so the futures version tested here is the index-level analog.
Pre-registered before looking:
  Events = rebalancing dates: S&P / NDX quarterly (3rd Friday of Mar / Jun / Sep / Dec, incl. NDX's annual December),
           MSCI quarterly (last business day of Feb / May / Aug / Nov), Russell reconstitution (late June Fridays).
  Signal = the 14:30 -> 15:00 CT move on the event day (the paper's last 30 minutes).
  Trade  = fade it, (A) from the 17:00 CT reopen (first bar 17:01-17:10) to the 10:30 CT close of the next trading day
           (the paper's 'early trading hours'; Apex-legal, one Apex day), (B) 8:30 open -> 10:30 of the next day.
           Also only when |move| >= 0.15 ATR15 (a real push).
  Placebo = the same rule on every other day.  Nights that contain a contract switch are left out.
  Costs per contract round trip: NQ $24.50, ES $35.
  python3 analysis/index_rebalance_reversal_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import overnight_round as OR

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
OR.SP = SP
MK = {"NQ": ("g24", 20.0, 24.5), "ES": ("ge", 50.0, 35.0)}
RUSSELL = pd.to_datetime(["2018-06-22", "2019-06-28", "2020-06-26", "2021-06-25", "2022-06-24", "2023-06-23",
                          "2024-06-28", "2025-06-27", "2026-06-26"])


def events(dts):
    s = pd.Series(dts, index=dts); ev = {}
    for (y, m), g in s.groupby([s.index.year, s.index.month]):
        if m in (3, 6, 9, 12):
            fr = g[g.index.dayofweek == 4]
            if len(fr) >= 3 and 15 <= fr.index[2].day <= 21: ev[fr.index[2]] = "S&P/NDX"
        if m in (2, 5, 8, 11): ev[g.index[-1]] = "MSCI"
    for d in RUSSELL:
        if d in s.index: ev[d] = "Russell"
    return ev


def stats(x, dates, nm):
    x = pd.Series(np.asarray(x, float), index=pd.DatetimeIndex(dates)).dropna()
    if len(x) < 5: print(f"   {nm:<44} n={len(x)}"); return
    t = x.mean() / x.std() * np.sqrt(len(x)); yrs = x.groupby(x.index.year).sum(); gl = -x[x < 0].sum()
    a, h = x[x.index < "2023"], x[x.index >= "2023"]
    print(f"   {nm:<44} n={len(x):4d} ${x.mean():6.1f} PF {x[x > 0].sum() / gl if gl else np.inf:4.2f} t {t:4.1f} "
          f"yrs+ {(yrs > 0).sum()}/{len(yrs)} | 18-22 ${a.mean():.0f} 23+ ${h.mean():.0f}")


def table(sym):
    g = OR.load(sym); _, pv, cost = MK[sym]; tr = g.trading; dts = pd.DatetimeIndex(g.ts[tr])
    atr = g.daily_atr(15); cf = pd.Series(g.c.ravel()).ffill().to_numpy(); R = OR.roll_minutes(g, sym)
    ev = events(dts[dts >= "2018-01-01"]); rows = []
    for i in range(len(tr) - 1):
        r, nx = tr[i], tr[i + 1]; d = dts[i]
        if d < pd.Timestamp("2018-01-01") or not atr[r] > 0: continue
        mv = cf[r * 1440 + jof(1500)] - cf[r * 1440 + jof(1430)]
        seg = g.o[nx - 1, jof(1701):jof(1710) + 1]; ok = np.flatnonzero(~np.isnan(seg))
        if not len(ok) or np.isnan(mv): continue
        e0 = (nx - 1) * 1440 + jof(1701) + ok[0]; x = cf[nx * 1440 + jof(1030)]
        if ((R >= e0) & (R <= nx * 1440 + jof(1030))).any(): continue      # contract switch inside the hold
        side = -np.sign(mv)
        rows.append(dict(date=d, ev=ev.get(d, ""), move=mv / atr[r], side=side,
                         A=(side * (x - seg[ok[0]])) * pv - cost, B=(side * (x - g.o[nx, jof(831)])) * pv - cost))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    for sym in ("NQ", "ES"):
        df = table(sym); e = df[df.ev != ""]; o = df[df.ev == ""]
        print(f"\n{sym}: {len(e)} rebalancing dates ({e.ev.value_counts().to_dict()}), {len(o)} other days")
        for leg, nm in (("A", "(A) 17:00 reopen -> 10:30"), ("B", "(B) 8:30 -> 10:30")):
            stats(e[leg], e.date, f"{nm}, rebalancing dates")
            big = e.move.abs() >= 0.15; stats(e[leg][big], e.date[big], "   only |move| >= 0.15 ATR")
            stats(e[leg][e.side > 0], e.date[e.side > 0], "   longs (after a down last 30 min)")
            stats(e[leg][e.side < 0], e.date[e.side < 0], "   shorts")
            for k in ("S&P/NDX", "MSCI", "Russell"):
                s = e[e.ev == k]; stats(s[leg], s.date, f"   {k} only")
            stats(o[leg], o.date, "   placebo: every other day")
        if sym == "NQ":
            print("   NQ event list:"); print(e[["date", "ev", "move", "A", "B"]].round(2).to_string(index=False))
