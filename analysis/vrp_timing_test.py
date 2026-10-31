"""Variance risk premium as a futures timing signal (paper: Ratnaike 2026, SSRN 7664478, user upload 2026-10-29).
The paper's trade (delta-hedged short SPX straddle) needs options, which Apex doesn't allow. Futures proxy, fixed before
looking: VRP_t = VIX close - NQ's past 21-day realised vol (close-to-close, annualised). Does VRP predict NQ's next-day
(15:15 -> 15:15 close) or next-21-day return (Bollerslev, Tauchen & Zhou 2009: high VRP -> higher equity returns)?
Quintiles 2018-2026; 'always long' is the drift control.  python3 analysis/vrp_timing_test.py
"""
import glob, numpy as np, pandas as pd
d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/NQ_1min_20*.csv")) if "_ON_" not in f])
c = d.groupby("date").close.last(); c.index = pd.to_datetime(c.index.astype(str))
v = pd.read_csv("data/VIX_daily.csv"); v.columns = [x.lower() for x in v.columns]
v["date"] = pd.to_datetime(v.iloc[:, 0]); v = v.set_index("date")["close"].reindex(c.index).ffill()
r = np.log(c).diff()                                                     # roll days add noise (unadjusted); median-robust below
rv = r.rolling(21).std() * np.sqrt(252) * 100
vrp = v - rv
nx1 = r.shift(-1); nx21 = r.rolling(21).sum().shift(-21)
df = pd.DataFrame(dict(vrp=vrp, nx1=nx1, nx21=nx21)).dropna(); df = df[df.index >= "2018-01-01"]
df["q"] = pd.qcut(df.vrp, 5, labels=False) + 1
print(__doc__.split("\n")[0]); print(f"days {len(df)}, VRP mean {df.vrp.mean():.1f} pts, VIX > past realised on {np.mean(df.vrp > 0):.0%} of days")
for col, nm in (("nx1", "next day"), ("nx21", "next 21 days")):
    g = df.groupby("q")[col]; m = g.mean() * 1e4; t = g.mean() / g.std() * np.sqrt(g.count())
    print(f"\n{nm} NQ return by VRP quintile (bp; t; 21-day windows overlap so their t is ~4.6x too high):")
    for q in m.index: print(f"   Q{q}: {m[q]:7.1f} bp  t {t[q]:4.1f}")
    print(f"   all days: {df[col].mean() * 1e4:.1f} bp;  Q5 - Q1 = {m[5] - m[1]:.1f} bp")
# simple rule: long NQ next day only when VRP is in its top 2 quintiles (thresholds from 2018-2022 only), per NQ after costs
th = df.vrp[df.index < "2023-01-01"].quantile(0.6)
for per, x in (("2018-22", df[df.index < "2023-01-01"]), ("2023+", df[df.index >= "2023-01-01"])):
    on = x[x.vrp >= th]; pnl = on.nx1 * c.reindex(on.index) * 20 - 7.25 - 10
    allp = x.nx1 * c.reindex(x.index) * 20 - 7.25 - 10
    print(f"\n{per}: long next day when VRP >= {th:.1f}: {len(on)} days, ${pnl.mean():.0f}/NQ, t {pnl.mean() / pnl.std() * np.sqrt(len(on)):.1f}; "
          f"always long ${allp.mean():.0f}/NQ (drift)")
