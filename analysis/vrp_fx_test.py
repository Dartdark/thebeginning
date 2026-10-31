"""US stock variance risk premium -> next-month EUR/USD (paper: Londono & Zhou 2012, 'Variance Risk Premiums and the Forward
Premium Puzzle', Fed IFDP 1068, SSRN 2209753; user upload 2026-10-29). Paper 2000-2011: a higher US VP predicts the dollar
weakening against the euro over the next month (1% significance), and VP predicts stock returns best at 3 months
(Bollerslev, Tauchen & Zhou 2009). Our data starts 2017, so 2018-2026 is fully out of the paper's sample.
Rule fixed before looking: month-end VP = VIX^2/12 - realised S&P variance of the past 21 sessions (monthly %^2);
regress the next calendar month's 6E (USD per EUR) log return on VP; trade: long 6E for the next month when VP is above
its expanding median (from 2018 on, history from 2011), short otherwise; per 6E contract after $7.25 + 1 tick a side
(round trip $19.75); drift control = always long. 6E is unadjusted (roll jumps ~0.1-0.3% a quarter add noise).
Same check for ES (SPX next 1 and 3 months).   python3 analysis/vrp_fx_test.py
"""
import glob, numpy as np, pandas as pd
e = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/6E_1min_20*.csv"))])
e = e[e.time <= 1600]; ec = e.groupby("date").close.last(); ec.index = pd.to_datetime(ec.index.astype(str))
s = pd.read_csv("data/SPX_daily.csv", parse_dates=["date"]).set_index("date").close
v = pd.read_csv("data/VIX_daily.csv"); v["date"] = pd.to_datetime(v.DATE); v = v.set_index("date").CLOSE.reindex(s.index).ffill()
rs = np.log(s).diff()
vp = (v ** 2 / 12 - (rs ** 2).rolling(21).sum() * 1e4).dropna()        # monthly %^2
me = vp.groupby(vp.index.to_period("M")).tail(1)                          # month-end values
med = me.expanding(24).median()
def nxt(px, k=1):
    m = np.log(px.groupby(px.index.to_period("M")).last()); return (m.shift(-k) - m)
fx = nxt(ec); sp1 = nxt(s); sp3 = nxt(s, 3)
df = pd.DataFrame(dict(vp=me.values, med=med.values), index=me.index.to_period("M"))
df["fx"] = fx; df["sp1"] = sp1; df["sp3"] = sp3; df["eur"] = ec.groupby(ec.index.to_period("M")).last()
df = df[df.index >= "2018-01"].dropna(subset=["fx"])
def ols(y, x):
    X = np.c_[np.ones(len(x)), x]; b = np.linalg.lstsq(X, y, rcond=None)[0]; u = y - X @ b
    se = np.sqrt(np.diag(np.linalg.inv(X.T @ X)) * (u @ u) / (len(y) - 2)); return b[1], b[1] / se[1], 1 - u.var() / y.var()
print(__doc__.split("\n")[0]); print(f"months {len(df)} ({df.index[0]} -> {df.index[-1]}), VP mean {df.vp.mean():.1f} %^2/month, > 0 in {np.mean(df.vp > 0):.0%}")
z = (df.vp - df.vp.mean()) / df.vp.std()
for col, nm, sgn in (("fx", "6E next month", "+ (paper: dollar weakens vs EUR)"), ("sp1", "SPX next month", "+"), ("sp3", "SPX next 3 months (overlapping)", "+")):
    x = df.dropna(subset=[col]); zz = z[x.index]; b, t, r2 = ols(x[col].values * 100, zz.values)
    print(f"  {nm:32s} slope {b:+.2f}% per 1 sd VP, t {t:+.1f}, R2 {r2:.3f}   expected sign {sgn}")
for per, x in (("2018-22", df[df.index < "2023-01"]), ("2023+", df[df.index >= "2023-01"]), ("all", df)):
    sig = np.where(x.vp > x.med, 1, -1); usd = x.fx * x.eur * 125000
    pnl = sig * usd - 19.75; lng = usd - 19.75
    print(f"  {per:8s} 6E long/short by VP vs median: {len(x)} months, ${pnl.mean():+.0f}/month, t {pnl.mean() / pnl.std() * np.sqrt(len(x)):+.1f}, "
          f"longs {np.sum(sig > 0)} ${pnl[sig > 0].mean():+.0f}, shorts {np.sum(sig < 0)} ${pnl[sig < 0].mean():+.0f};  always long ${lng.mean():+.0f}")
