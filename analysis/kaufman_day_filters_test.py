"""Kaufman, Trading Systems and Methods (5th ed.) ch. 16 via Antigravity's book reading (antigravity/jesse
tasks/out_book_kaufman_systems): its shortlist is opening-range breakouts (Crabel, Fisher ACD, Rudd, Bookstaber) — that
family is already tested (TIER_LIST: Crabel stretch, Zarattini ORBs, Fabio ORB, Mesfin; ONB and Vault Break are the
breakouts that work). The untested part is Crabel's day types: trade the breakout after an INSIDE day (yesterday's
range inside the day before) or an NR7 day (yesterday's range the narrowest of 7). Pre-registered here as day filters on
the plan's breakouts, MultiCharts trade lists (Vault Break 30-min, Overnight Bias ADX30 15-min), 2018-2026, 4 trials.
Ranges = regular session 8:30-15:00 CT. Per NQ after $7.25 + 1 tick per side (2 ticks a trade).
  python3 analysis/kaufman_day_filters_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis"); sys.path.insert(0, "analysis/jesse")
import numpy as np, pandas as pd
from grid24 import jof
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
sys.argv = sys.argv[:1]
import compare as C

if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); tr = g.trading
    hi = np.nanmax(g.h[tr, jof(831):jof(1500) + 1], 1); lo = np.nanmin(g.l[tr, jof(831):jof(1500) + 1], 1)
    d = pd.DataFrame(dict(hi=hi, lo=lo), index=pd.DatetimeIndex(g.ts[tr]).normalize()).dropna()
    d["rng"] = d.hi - d.lo
    inside = (d.hi < d.hi.shift(1)) & (d.lo > d.lo.shift(1))
    nr7 = d.rng <= d.rng.rolling(7).min()
    flag = pd.DataFrame(dict(inside=inside.shift(1), nr7=nr7.shift(1)), index=d.index).fillna(False).astype(bool)   # known before day d
    for nm in ("VaultBreak", "ONBiasADX30"):
        path, pv, tick, cost = C.REPORTS[nm]
        m = C.mc_trades(path); m["net"] = m.points * pv - 2 * cost - 2 * tick * pv
        m["day"] = m.entry_time.dt.normalize(); m = m[m.day >= "2018-01-01"].join(flag, on="day").dropna(subset=["inside"])
        print(f"\n{nm}: {len(m)} trades, all ${m.net.mean():.0f}")
        for f in ("inside", "nr7"):
            k = m[f].astype(bool).to_numpy(); a, b = m[k], m[~k]
            dm = a.net.mean() - b.net.mean(); se = np.sqrt(a.net.var() / len(a) + b.net.var() / len(b))
            per = {p: (x[x.day < "2023"].net.mean(), x[x.day >= "2023"].net.mean()) for p, x in (("on", a), ("off", b))}
            print(f"   after {f:<6} day: n={len(a):4d} ${a.net.mean():5.0f} vs other ${b.net.mean():5.0f}  diff t {dm / se:4.1f} "
                  f"| on: 18-22 ${per['on'][0]:.0f} 23+ ${per['on'][1]:.0f}; off: 18-22 ${per['off'][0]:.0f} 23+ ${per['off'][1]:.0f}")


def placebo(n_sims=5000, seed=1):
    """Random-day placebo for the VB NR7 result: draw as many VB trading days as NR7 has, compare the $ a trade."""
    g = pickle.load(open(SP + "g24.pkl", "rb")); tr = g.trading
    hi = np.nanmax(g.h[tr, jof(831):jof(1500) + 1], 1); lo = np.nanmin(g.l[tr, jof(831):jof(1500) + 1], 1)
    d = pd.DataFrame(dict(rng=hi - lo), index=pd.DatetimeIndex(g.ts[tr]).normalize()).dropna()
    nr7 = (d.rng <= d.rng.rolling(7).min()).shift(1).fillna(False).astype(bool)
    path, pv, tick, cost = C.REPORTS["VaultBreak"]; m = C.mc_trades(path); m["net"] = m.points * pv - 2 * cost - 2 * tick * pv
    m["day"] = m.entry_time.dt.normalize(); m = m[m.day >= "2018-01-01"]
    days = m.day.unique(); k = int(nr7.reindex(days).fillna(False).sum()); real = m.net[nr7.reindex(m.day).fillna(False).to_numpy()].mean()
    rng_ = np.random.default_rng(seed); by = m.groupby("day").net.agg(["sum", "count"])
    sims = np.array([(lambda s: s["sum"].sum() / s["count"].sum())(by.loc[rng_.choice(days, k, replace=False)]) for _ in range(n_sims)])
    print(f"\nVB NR7 random-day placebo: real ${real:.0f} a trade over {k} days; random days mean ${sims.mean():.0f}, "
          f"95th ${np.percentile(sims, 95):.0f}, 99th ${np.percentile(sims, 99):.0f}, p = {np.mean(sims >= real):.4f}")


if __name__ == "__main__":
    placebo()
