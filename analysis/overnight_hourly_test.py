"""Overnight drift by hour, NQ / ES (papers: Boyarchenko, Larsen & Whelan, 'The Overnight Drift', NY Fed SR 917 / RFS 2023 and their
2026 Liberty Street follow-up 'The Disappearing Overnight Drift'; Bondarenko & Muravyev, 'Market Return Around the Clock', JFQA
2023; scout 2026-10-30). Claims (ES 1998-2020): the 02:00-03:00 ET (01:00-02:00 CT) European-open hour earns ~3.7% a year and
most of the market return; it is pay to liquidity providers who absorb closing sell imbalances, so larger after down closes;
the 2026 post says the hour averages ~0 in 2021-25. Our check, fixed before looking, 1-min Globex bars (roll weeks out):
(a) mean return per CT hour from 17:00 to 08:00, 2018-20 vs 2021-26; (b) long 01:00 -> 02:00 CT and the 4-hour window
23:00 -> 03:00 CT, all nights and after a down RTH day (08:30 -> 15:00 return < 0); per contract after $7.25 NQ / $5 ES +
1 tick a side.   python3 analysis/overnight_hourly_test.py
"""
import glob, numpy as np, pandas as pd
for sym, pv, cost in (("NQ", 20, 7.25 + 2 * 0.25 * 20), ("ES", 50, 5.0 + 2 * 0.25 * 50)):
    rth = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"data/{sym}_1min_20*.csv")) if "_ON_" not in f])
    onf = sorted(glob.glob(f"data/{sym}_1min_ON_20*.csv"))                 # NQ: separate night files; ES files are 24 h
    on = pd.concat([pd.read_csv(f) for f in onf]) if onf else rth[(rth.time > 1515) | (rth.time <= 830)].copy()
    on["ts"] = pd.to_datetime(on.date.astype(str)) + pd.to_timedelta(on.time // 100, "h") + pd.to_timedelta(on.time % 100, "m")
    on = on.set_index("ts").sort_index()
    # session date: bars after 17:00 belong to the next trading day
    on["sess"] = (on.index + pd.Timedelta(hours=7)).normalize()
    px = on.close; hr = on.index.hour
    o = rth[rth.time == 831].set_index("date").open; c = rth[rth.time == 1500].set_index("date").close
    day = pd.DataFrame(dict(o=o, c=c)).dropna(); day.index = pd.to_datetime(day.index.astype(str)); day["ret"] = day.c / day.o - 1
    last = on.groupby([on.sess, hr]).close.last().unstack()               # close at the end of each CT hour per session
    first = on.groupby(on.sess).close.first()
    rows = {}
    order = [17, 18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7]
    prev = first
    for h in order:
        if h not in last: continue
        cur = last[h]; rows[h] = (cur - prev) * pv; prev = cur.fillna(prev)
    H = pd.DataFrame(rows); H = H[H.index >= "2018-01-02"]
    rw = H.index.month.isin([3, 6, 9, 12]) & (H.index.day >= 7) & (H.index.day <= 18); H = H[~rw]
    H = H[(H.abs() < H.abs().quantile(0.999) * 3).all(axis=1)]
    prevday = day.ret.shift(1).reindex(H.index, method="ffill")            # last completed RTH day before this night
    print(f"\n{sym}: {len(H)} nights; mean $ per CT hour (hour h = bar ending in that hour), 2018-20 | 2021-26")
    a, b = H[H.index < "2021"], H[H.index >= "2021"]
    print("   " + "  ".join(f"{h:02d}:{a[h].mean():+4.0f}|{b[h].mean():+4.0f}" for h in H.columns))
    for nm, cols in (("01:00 -> 02:00 CT (European open)", [1]), ("23:00 -> 03:00 CT (4 h)", [23, 0, 1, 2])):
        s = H[cols].sum(axis=1) - cost
        for per, m in (("2018-20", H.index < "2021"), ("2021-26", H.index >= "2021")):
            for cnd, k in (("all nights", m), ("after down day", m & (prevday < 0)), ("after up day", m & (prevday > 0))):
                x = s[k]; print(f"   {nm:34s} {per} {cnd:15s} n {len(x):4d} ${x.mean():+5.0f} t {x.mean() / x.std() * np.sqrt(len(x)):+.1f}")
