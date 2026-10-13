"""Bollinger Band reversal strategies on NQ (2026-10-13, user idea).

Bands: SMA(20) +/- K x stdev(20) of bar closes on a continuous 24-hour bar series (as on a
MultiCharts chart). Two entry styles:
  touch    a bar closes outside a band -> fade it at the next minute's open
  reentry  a bar closes back inside after the previous bar closed outside (the classic "reversal")
Exit: target = the middle band at the signal bar (limit, no slippage), stop = S x 15-day ATR
(market, 1 tick), time exit after H minutes or at the session cutoff. One position at a time.
Sessions: RTH (signals 8:45-14:00, out by 14:55) and overnight (signals 18:00-23:30 and 0:00-6:00,
out by 23:59 / 7:25). Filters: none; quiet = ADX(14) on the same bars < 20; narrow = band width
below its median of the last 100 bars.
Daily version: daily close below the lower band (20, 2) -> buy the next 8:30 open, sell 15:00
(Apex-legal day trade), with and without a rising 200-day EMA.
Per NQ after $7.25 + 1 tick per market/stop fill, 2018-2026.
  python3 analysis/bollinger_reversal_test.py [SCRATCH_DIR]
"""
import sys, warnings, pickle, itertools; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from news_meanrev_test import row, summ

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"


def bar_series(g, k):
    b = g.bars(k)
    D, P = b["c"].shape
    flat = {c: b[c].ravel() for c in ("o", "h", "l", "c")}
    ok = ~np.isnan(flat["c"])
    idx = np.where(ok)[0]
    s = pd.DataFrame({c: flat[c][idx] for c in flat})
    s["row"] = idx // P; s["col"] = (idx % P) * k
    return s


def add_bands(s, n=20, K=2.0):
    m = s.c.rolling(n).mean(); sd = s.c.rolling(n).std(ddof=0)
    s["mid"] = m; s["up"] = m + K * sd; s["lo"] = m - K * sd
    s["width"] = (s.up - s.lo) / m
    s["narrow"] = s.width < s.width.rolling(100).median()
    # ADX(14), Wilder
    h, l, c = s.h.to_numpy(), s.l.to_numpy(), s.c.to_numpy()
    up = np.r_[0, np.diff(h)]; dn = np.r_[0, -np.diff(l)]
    pdm = np.where((up > dn) & (up > 0), up, 0.0); ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = np.fmax(h - l, np.fmax(np.abs(h - np.r_[c[0], c[:-1]]), np.abs(l - np.r_[c[0], c[:-1]])))
    a = 1 / 14
    atr = pd.Series(tr).ewm(alpha=a, adjust=False).mean()
    pdi = 100 * pd.Series(pdm).ewm(alpha=a, adjust=False).mean() / atr
    ndi = 100 * pd.Series(ndm).ewm(alpha=a, adjust=False).mean() / atr
    dx = 100 * (pdi - ndi).abs() / (pdi + ndi)
    s["adx"] = dx.ewm(alpha=a, adjust=False).mean().to_numpy()
    return s


def in_window(col, session):
    hh = (col // 60) * 100 + col % 60
    if session == "RTH":
        return (hh >= 845) & (hh <= 1400)
    return ((hh >= 1800) & (hh <= 2330)) | (hh <= 600)


def cutoff(col, session):
    if session == "RTH": return jof(1455)
    return 1439 if col >= jof(1800) else jof(725)


def trades(g, s, atr, style="touch", session="RTH", filt="none", stop=0.15, hold=60):
    c, lo, up, mid = s.c.to_numpy(), s.lo.to_numpy(), s.up.to_numpy(), s.mid.to_numpy()
    prev_c, prev_lo, prev_up = np.r_[np.nan, c[:-1]], np.r_[np.nan, lo[:-1]], np.r_[np.nan, up[:-1]]
    if style == "touch":
        sig_l, sig_s = c < lo, c > up
    else:
        sig_l = (prev_c < prev_lo) & (c > lo)
        sig_s = (prev_c > prev_up) & (c < up)
    side = np.where(sig_l, 1, np.where(sig_s, -1, 0))
    ok = in_window(s.col.to_numpy(), session) & (side != 0) & ~np.isnan(mid)
    if filt == "quiet": ok &= s.adx.to_numpy() < 20
    if filt == "narrow": ok &= s.narrow.to_numpy()
    ts = pd.DatetimeIndex(g.ts); rows = []; busy = (-1, -1)
    rr, cc = s.row.to_numpy(), s.col.to_numpy()
    for i in np.where(ok)[0]:
        d, j = int(rr[i]), int(cc[i])
        if ts[d].year < 2018 or ts[d].dayofweek == 5 or np.isnan(atr[d]): continue
        if d == busy[0] and j <= busy[1]: continue
        j0 = j + 1; cut = cutoff(j, session)
        if j0 >= cut: continue
        e = g.o[d, j0]
        if np.isnan(e): continue
        sd = int(side[i]); tgt = mid[i]
        if (tgt - e) * sd <= 0: continue                     # already past the middle band
        r = row(g, d, j0, sd, min(j0 + hold, cut), e - sd * stop * atr[d], tgt)
        if r: rows.append(r); busy = (d, r["j1"])
    return pd.DataFrame(rows)


def line(t, nm, w=60):
    return summ(t, nm, w)


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15)
    print(__doc__.split("\n")[0])
    res = []
    for k in (5, 15):
        for K in (2.0, 2.5, 3.0):
            s = add_bands(bar_series(g, k), 20, K)
            for style, session, filt in itertools.product(("touch", "reentry"), ("RTH", "night"), ("none", "quiet", "narrow")):
                t = trades(g, s, atr, style, session, filt)
                x = t.net if len(t) else pd.Series(dtype=float)
                res.append(dict(bars=k, K=K, style=style, session=session, filt=filt, n=len(t),
                                avg=x.mean(), pf=x[x > 0].sum() / max(1e-9, -x[x < 0].sum()) if len(t) else np.nan,
                                t=x.mean() / x.std() * np.sqrt(len(x)) if len(t) > 1 else np.nan,
                                h23=x[t.date.dt.year >= 2023].mean() if len(t) else np.nan,
                                yrs=int((x.groupby(t.date.dt.year).sum() > 0).sum()) if len(t) else 0))
    R = pd.DataFrame(res)
    print(f"\n1. Intraday grid: {len(R)} versions (stop 0.15 ATR, target middle band, out after 60 min)")
    print(R.to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
    print(f"\n   versions with avg > 0: {np.mean(R.avg > 0):.0%}; with t >= 2: {np.mean(R.t >= 2):.0%}; with t <= -2: {np.mean(R.t <= -2):.0%}")

    best = R.sort_values("t", ascending=False).head(3)
    print("\n2. Best three by t, with other stops / holds (sensitivity) and the mirror 'follow' trade:")
    for _, b in best.iterrows():
        s = add_bands(bar_series(g, int(b.bars)), 20, b.K)
        for st, hd in ((0.1, 60), (0.15, 30), (0.15, 120), (0.25, 60), (0.4, 60)):
            print("  " + line(trades(g, s, atr, b.style, b.session, b.filt, st, hd),
                              f"{b.bars}m K{b.K} {b.style} {b.session} {b.filt} stop {st} hold {hd}"))

    print("\n3. Daily Bollinger reversal: close below the lower band (20, 2) -> buy next day 8:30, sell 15:00")
    tr = g.trading; dts = pd.DatetimeIndex(g.ts[tr])
    C = pd.Series(g.c[tr, 900]).ffill()
    m, sd = C.rolling(20).mean(), C.rolling(20).std(ddof=0)
    ema = C.ewm(span=200, adjust=False).mean(); rising = ema > ema.shift(5)
    nxt = pd.Series((g.c[tr, 900] - g.o[tr, 511]) * 20).shift(-1)       # next day's RTH, per NQ
    for nm, cond in (("close < lower band", C < m - 2 * sd), ("close < lower band, EMA200 rising", (C < m - 2 * sd) & rising),
                     ("close > upper band: short next day", C > m + 2 * sd)):
        sgn = -1 if "short" in nm else 1
        x = (sgn * nxt - 17.25)[cond & (dts.year >= 2018)].dropna()
        y = pd.Series(x.values, index=dts[x.index]).groupby(level=0).sum()
        by = y.groupby(y.index.year).sum()
        print(f"  {nm:<40} n={len(x):3d} avg ${x.mean():5.0f} PF {x[x>0].sum()/-x[x<0].sum():.2f} t={x.mean()/x.std()*np.sqrt(len(x)):4.1f}"
              f" yrs+ {(by>0).sum()}/{len(by)}")
