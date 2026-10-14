"""BTC short-only 'fade the retail euphoria' (user's idea, 2026-10-14), CME bitcoin futures 2019-2026, US hours, per 1 BTC
(= 10 MBT), $25 commission + 1 tick (5 points) per fill = $35 a round trip; flat by 15:00 CT.
Pre-specified (before looking); every rule is short-only and compared with a random short (BTC drifts up):
  A  fade multi-day euphoria: 1 / 3 / 5-day close-to-close (15:00 CT) return z >= 1.5 vs its 60-day history -> short next
     session 8:30 -> 15:00
  B  fade the overnight pump: 15:00 -> 8:30 return z >= 1.5 -> short 8:30 -> 15:00
  C  fade the intraday spike: up >= 1 x 15-day ATR from the 8:30 price by 10:30 -> short 10:30 -> 15:00, stop at the day's
     high so far + 0.25 ATR
  D  fade an up day on heavy volume: 8:30-15:00 up and session volume z >= 2 vs 60 days -> short next session 8:30 -> 15:00
  E  round numbers: first touch of a $5,000 multiple from below 8:30-14:00 -> short at the touch +1 tick, out 60 min later
Placebo / baseline: short every session 8:30 -> 15:00 (and 10:30 -> 15:00 for C).
  python3 analysis/btc_retail_fade_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import line
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
TICK, COMM = 5.0, 25.0; COST = COMM + 2 * TICK

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "btc.pkl", "rb")); ts = pd.DatetimeIndex(g.ts)
    cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    tr = g.trading; days = ts[tr]
    full = ~np.isnan(g.c[tr, jof(830):jof(1500) + 1]).all(1) & (g.last_j[tr] >= jof(1500))
    tr, days = tr[full], days[full]
    at = lambda hh: cf[tr * 1440 + jof(hh)]
    D = pd.DataFrame({h: at(h) for h in (830, 1030, 1500)}, index=days)
    D["vol"] = np.nansum(g.v[tr, jof(831):jof(1500) + 1], 1)
    D = D[D.index >= "2018-06-01"]; tr = tr[-len(D):]
    D["s830"] = (D[830] - D[1500]) - COST          # short 8:30 -> 15:00 ($ per BTC, $1 a point)
    D["s1030"] = (D[1030] - D[1500]) - COST
    lc = np.log(D[1500]); z = lambda x: (x - x.rolling(60).mean().shift(1)) / x.rolling(60).std().shift(1)
    nxt = lambda m: m.shift(1).fillna(False).astype(bool)       # signal on day t -> trade on t+1
    hi = pd.Series(np.nanmax(g.h[tr], 1), index=D.index); lo = pd.Series(np.nanmin(g.l[tr], 1), index=D.index)
    atr = (hi - lo).rolling(15).mean().shift(1)
    S = D.index >= "2019-01-01"
    print("\nbaseline (random short): ")
    print(line(D.s830[S], "short every session 8:30-15:00", 40)); print(line(D.s1030[S], "short every session 10:30-15:00", 40))
    print("\nA. fade multi-day euphoria (signal day t, short t+1 8:30-15:00)")
    for k in (1, 3, 5):
        m = nxt(z(lc.diff(k)) >= 1.5); print(line(D.s830[m & S], f"{k}-day return z >= 1.5", 40))
    print("\nB. fade the overnight pump")
    on = np.log(D[830] / D[1500].shift(1)); m = z(on) >= 1.5
    print(line(D.s830[m & S], "overnight z >= 1.5, short 8:30-15:00", 40))
    print("\nC. fade the intraday spike (stop = high so far + 0.25 ATR)")
    out = []
    for i, d in enumerate(D.index):
        if d < pd.Timestamp("2019-01-01") or np.isnan(atr.iloc[i]): continue
        r = tr[i]; p0 = D[830].iloc[i]
        if D[1030].iloc[i] - p0 < atr.iloc[i]: continue
        e = D[1030].iloc[i] - TICK; stop = np.nanmax(g.h[r, jof(830):jof(1030) + 1]) + 0.25 * atr.iloc[i]
        px = cf[r * 1440 + jof(1500)] + TICK
        for j in range(jof(1031), jof(1500) + 1):
            if g.h[r, j] >= stop: px = max(g.o[r, j], stop) + TICK; break
        out.append((d, e - px - COMM))
    c = pd.Series([v for _, v in out], index=pd.DatetimeIndex([d for d, _ in out])); print(line(c, "up >= 1 ATR by 10:30, short to 15:00", 40))
    print("\nD. fade an up day on heavy volume")
    m = nxt(((D[1500] - D[830]) > 0) & (z(np.log(D.vol.replace(0, np.nan))) >= 2))
    print(line(D.s830[m & S], "up day + volume z >= 2, short next day", 40))
    print("\nE. first touch of a $5,000 multiple from below, 8:30-14:00, out 60 min")
    out = []
    for i, d in enumerate(D.index):
        if d < pd.Timestamp("2019-01-01"): continue
        r = tr[i]; p = g.c[r]; h = g.h[r]; prev = cf[r * 1440 + jof(829)]
        lvl = (np.floor(prev / 5000) + 1) * 5000
        hit = np.flatnonzero(h[jof(831):jof(1400) + 1] >= lvl)
        if len(hit):
            j = jof(831) + hit[0]; e = lvl - TICK; x = cf[r * 1440 + min(j + 60, jof(1500))] + TICK
            out.append((d, e - x - COMM))
    rn = pd.Series([v for _, v in out], index=pd.DatetimeIndex([d for d, _ in out])); print(line(rn, "round-number short, 60 min", 40))
