"""Moving Hurst regime strategy (Dudia, Kumar & Bhattacharyya, SSRN 3543079; user upload 2026-10-29), the paper's
'Concluded Plan' with its own parameters on NQ daily closes (15:15 CT, unadjusted), 2018-2026, $7.25 + 1 tick a fill.
  Hurst (R/S, 100 daily returns): H > 0.5 -> momentum: MACD(12,26,9) line crosses its signal: long / short.
  H <= 0.5 -> mean reversion: close crosses above SMA80 with RSI(2) < 20 -> long; below with RSI(2) > 80 -> short;
  exit when the close crosses back through SMA4. Positions held overnight (personal account only; Apex is flat by 15:59).
  python3 analysis/hurst_regime_test.py
"""
import glob, numpy as np, pandas as pd
d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/NQ_1min_20*.csv")) if "_ON_" not in f])
c = d.groupby("date").close.last(); c.index = pd.to_datetime(c.index.astype(str))
r = np.log(c).diff()


def rs_hurst(x):
    x = np.asarray(x); n = len(x); out = []; ns = []
    for k in (8, 12, 16, 25, 33, 50, 100):
        if k > n: break
        m = n // k; rs = []
        for i in range(m):
            s = x[i * k:(i + 1) * k]; z = np.cumsum(s - s.mean()); sd = s.std()
            if sd > 0: rs.append((z.max() - z.min()) / sd)
        if rs: out.append(np.log(np.mean(rs))); ns.append(np.log(k))
    return np.polyfit(ns, out, 1)[0] if len(ns) > 2 else np.nan


H = r.rolling(100).apply(rs_hurst, raw=True)
ema = lambda s, n: s.ewm(span=n, adjust=False).mean()
macd = ema(c, 12) - ema(c, 26); sig = ema(macd, 9)
sma80, sma4 = c.rolling(80).mean(), c.rolling(4).mean()
dlt = c.diff(); up = dlt.clip(lower=0).ewm(alpha=1 / 2, adjust=False).mean(); dn = (-dlt.clip(upper=0)).ewm(alpha=1 / 2, adjust=False).mean()
rsi = 100 - 100 / (1 + up / dn)
pos = np.zeros(len(c)); p = 0; tr = 0
for i in range(1, len(c)):
    if np.isnan(H.iloc[i]) or np.isnan(sma80.iloc[i]): continue
    new = p
    if H.iloc[i] > 0.5:
        if macd.iloc[i - 1] <= sig.iloc[i - 1] and macd.iloc[i] > sig.iloc[i]: new = 1
        elif macd.iloc[i - 1] >= sig.iloc[i - 1] and macd.iloc[i] < sig.iloc[i]: new = -1
    else:
        if c.iloc[i - 1] <= sma80.iloc[i - 1] < c.iloc[i] and rsi.iloc[i] < 20: new = 1
        elif c.iloc[i - 1] >= sma80.iloc[i - 1] > c.iloc[i] and rsi.iloc[i] > 80: new = -1
        elif p > 0 and c.iloc[i] < sma4.iloc[i]: new = 0
        elif p < 0 and c.iloc[i] > sma4.iloc[i]: new = 0
    if new != p: tr += abs(new - p)
    pos[i] = new; p = new
P = pd.Series(pos, index=c.index)
pnl = (P.shift(1) * c.diff() * 20).fillna(0)
cost = P.diff().abs().fillna(0) * (7.25 / 2 + 0.25 * 20)              # per side: half commission + 1 tick
net = (pnl - cost)[c.index >= "2018-01-01"]
yr = net.groupby(net.index.year).sum() / 1000
sh = net.mean() / net.std() * np.sqrt(252)
bh = (c.diff() * 20)[c.index >= "2018-01-01"]
print(__doc__.split("\n")[0])
print(f"NQ 1 contract 2018-2026: net ${net.sum() / 1000:.0f}k, Sharpe {sh:.2f}, days long {np.mean(P[c.index >= '2018'] > 0):.0%} / short {np.mean(P[c.index >= '2018'] < 0):.0%}, position changes {int(tr)}")
print("by year $k:", {int(k): round(v, 1) for k, v in yr.items()})
print(f"buy and hold 1 NQ: ${bh.sum() / 1000:.0f}k, Sharpe {bh.mean() / bh.std() * np.sqrt(252):.2f}; share of days H > 0.5: {np.mean(H[c.index >= '2018'] > 0.5):.0%}")
# momentum leg alone vs MACD always-on (does the Hurst switch add anything?)
mpos = np.sign(macd - sig); mp = (mpos.shift(1) * c.diff() * 20 - mpos.diff().abs() * (7.25 / 2 + 5)).fillna(0)[c.index >= "2018"]
print(f"MACD cross always on (no Hurst filter): ${mp.sum() / 1000:.0f}k, Sharpe {mp.mean() / mp.std() * np.sqrt(252):.2f}")
