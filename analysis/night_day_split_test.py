"""Overnight vs intraday return split (paper: Knuteson 2020, 'Strikingly Suspicious Overnight and Intraday Returns',
SSRN 3705017; user upload 2026-10-29). Paper: 21 world indices 1990-2020 earn everything close -> open and lose open ->
close; for the S&P 500 / NASDAQ the split stopped in 2008 (its own footnote 17). Check on NQ / ES 2018-2026: overnight =
15:00 -> 08:30 CT (next day), intraday = 08:30 -> 15:00; roll weeks (days 8-17 of Mar / Jun / Sep / Dec, unadjusted contract switch) and |overnight| > 6 sd dropped. Per contract per
day, gross and after $7.25 NQ / $5 ES + 1 tick a side; 'short intraday' tests the paper's negative leg.
python3 analysis/night_day_split_test.py
"""
import glob, numpy as np, pandas as pd
for sym, pv, cost in (("NQ", 20, 7.25 + 2 * 0.25 * 20), ("ES", 50, 5.0 + 2 * 0.25 * 50)):
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"data/{sym}_1min_20*.csv")) if "_ON_" not in f])
    o = d[d.time == 831].set_index("date").open; c = d[d.time == 1500].set_index("date").close
    x = pd.DataFrame(dict(o=o, c=c)).dropna(); x.index = pd.to_datetime(x.index.astype(str)); x = x[x.index >= "2018-01-01"]
    x["on"] = (x.o - x.c.shift(1)) * pv; x["id"] = (x.c - x.o) * pv; x = x.dropna()
    r = np.log(x.o / x.c.shift(1)).reindex(x.index); rw = x.index.month.isin([3, 6, 9, 12]) & (x.index.day >= 8) & (x.index.day <= 17)
    x = x[((r - r.mean()).abs() < 6 * r.std()) & ~rw]
    print(f"\n{sym}: {len(x)} days")
    for per, y in (("2018-22", x[:"2022"]), ("2023+", x["2023":]), ("all", x)):
        for nm, s in (("overnight long", y.on), ("intraday long", y.id), ("intraday short", -y.id)):
            g, n = s.mean(), s - cost
            print(f"   {per:8s} {nm:15s} gross ${g:+5.0f}/day (sum ${s.sum() / 1e3:+6.0f}k), net ${n.mean():+5.0f}, t {n.mean() / n.std() * np.sqrt(len(n)):+.1f}")
    yrs = x.groupby(x.index.year)[["on", "id"]].sum() / 1e3
    print("   by year ($k gross, overnight / intraday): " + ", ".join(f"{k} {a:+.0f}/{b:+.0f}" for k, (a, b) in yrs.iterrows()))
