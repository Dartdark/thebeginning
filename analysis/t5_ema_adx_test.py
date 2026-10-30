"""'Trend-5' (T5) EMA-5 + ADX-14 bot (user's ib_insync script, 2026-10-30): on each 5-minute RTH bar, if flat and ADX(14) > 25,
buy when close > EMA(5), sell when close < EMA(5); 1 contract; the script has NO exit (it would hold forever; not Apex-legal).
Test fixed before looking (3 variants): exit 15:00 CT (Apex flat rule), entry at the next 5-min bar's open after the signal
bar closes; indicators (a) as the script computes them, on today's RTH bars only ('1 D' of history, so ADX first exists
after ~28 bars = ~10:50 CT), (b) on continuous RTH history (warm ADX from 08:35). Then (c) random-side control on the same
entry bars. One trade a day (the script never exits, so it never re-enters). Per contract after $7.25 NQ / $5 ES + 1 tick a side.
python3 analysis/t5_ema_adx_test.py
"""
import glob, numpy as np, pandas as pd


def ema(x, n): return x.ewm(span=n, adjust=False).mean()


def adx(h, l, c, n=14):
    up, dn = h.diff(), -l.diff()
    pdm = np.where((up > dn) & (up > 0), up, 0.0); mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / n, adjust=False).mean()
    pdi = 100 * pd.Series(pdm, index=h.index).ewm(alpha=1 / n, adjust=False).mean() / atr
    mdi = 100 * pd.Series(mdm, index=h.index).ewm(alpha=1 / n, adjust=False).mean() / atr
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi)
    return dx.ewm(alpha=1 / n, adjust=False).mean()


def five_min(sym):
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"data/{sym}_1min_20*.csv")) if "_ON_" not in f])
    d = d[(d.time > 830) & (d.time <= 1500)].copy()
    d["ts"] = pd.to_datetime(d.date.astype(str)) + pd.to_timedelta(d.time // 100, "h") + pd.to_timedelta(d.time % 100, "m")
    d = d.set_index("ts").sort_index()
    b = d.resample("5min", label="right", closed="right").agg(dict(open="first", high="max", low="min", close="last", date="last")).dropna()
    return b


for sym, pv, cost in (("ES", 50, 5.0 + 2 * 0.25 * 50), ("NQ", 20, 7.25 + 2 * 0.25 * 20)):
    b = five_min(sym); b = b[b.index >= "2017-11-01"]
    b["ema_c"], b["adx_c"] = ema(b.close, 5), adx(b.high, b.low, b.close)
    g = b.groupby("date")
    b["ema_d"] = g.close.transform(lambda s: ema(s, 5))
    b["adx_d"] = pd.concat([adx(x.high, x.low, x.close).where(np.arange(len(x)) >= 27) for _, x in g])  # script: ADX after warm-up
    res = {"a script (today only)": [], "b continuous": []}
    rng = np.random.default_rng(7)
    for day, x in g:
        if pd.Timestamp(str(int(day))) < pd.Timestamp("2018-01-01") or len(x) < 70: continue
        close15 = x.close.iloc[-1]
        for key, e, a in (("a script (today only)", "ema_d", "adx_d"), ("b continuous", "ema_c", "adx_c")):
            sig = x[(x[a] > 25) & (x.index.time < pd.Timestamp("14:55").time())]
            if not len(sig): continue
            t0 = sig.index[0]; side = 1 if sig.close.iloc[0] > sig[e].iloc[0] else -1
            nxt = x[x.index > t0]
            if not len(nxt): continue
            entry = nxt.open.iloc[0]
            res[key].append(dict(date=pd.Timestamp(str(int(day))), side=side, net=side * (close15 - entry) * pv - cost,
                                 rnd=rng.choice([-1, 1]) * (close15 - entry) * pv - cost, hour=t0.hour))
    print(f"\n{sym}")
    for key, rows in res.items():
        r = pd.DataFrame(rows).set_index("date")
        def st(s): return f"n {len(s):4d} ${s.mean():+5.0f} t {s.mean() / s.std() * np.sqrt(len(s)):+.1f}"
        print(f"  {key:22s} all {st(r.net)} | longs {st(r.net[r.side > 0])} | shorts {st(r.net[r.side < 0])} | random side {st(r.rnd)}")
        print(f"  {'':22s} 2018-22 {st(r.net[r.index < '2023'])} | 2023+ {st(r.net[r.index >= '2023'])} | "
              f"by year " + ", ".join(f"{k} {v / 1e3:+.0f}k" for k, v in r.net.groupby(r.index.year).sum().items()))
