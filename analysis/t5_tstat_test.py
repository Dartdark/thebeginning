"""'T5 NQ' v2 (user's ib_insync script, 2026-10-30): 5-min RTH bars; base signal = +1 if close > EMA(5) else -1; strategy
return = log return x previous signal; rolling 60-bar t-stat of those returns. Flat and |t| >= 5 -> enter in the base
signal's direction (1 NQ); exit when |t| < 3. The script reads only today's bars ('1 D', >= 65 needed -> first decision
~14:00 CT) and never flattens at the close. Test fixed before looking (3 variants): (a) as written (today's bars, |t|),
(b) t >= +5 only (the script also enters when the trend-following return is strongly NEGATIVE, t <= -5, still following
the signal), (c) indicators on continuous RTH history so it can trade all day; all: decide on the closed bar, act at the
next bar's open, forced exit 15:00 CT (Apex); per NQ after $7.25 + 1 tick a side. Result: |t| >= 5 never happens, so
(d, e) add one disclosed extra look at a reachable threshold (2.5 / exit 1.5).   python3 analysis/t5_tstat_test.py
"""
import glob, numpy as np, pandas as pd
import sys; sys.path.insert(0, "analysis")
from t5_ema_adx_test import five_min, ema

PV, COST = 20, 7.25 + 2 * 0.25 * 20
b = five_min("NQ"); b = b[b.index >= "2017-11-01"].copy()


def tstat_cols(x):
    e = ema(x.close, 5); sig = np.where(x.close > e, 1, -1)
    sr = np.log(x.close / x.close.shift(1)) * pd.Series(sig, index=x.index).shift(1)
    t = sr.rolling(60).mean() / sr.rolling(60).std() * np.sqrt(60)
    return pd.DataFrame(dict(sig=sig, t=t), index=x.index)


cont = tstat_cols(b)
daily = pd.concat([tstat_cols(x) for _, x in b.groupby("date")])
res = {}
ENTER, EXIT = 5.0, 3.0
t_all = cont.t[cont.index >= "2018-01-01"].dropna()
print(f"rolling t over {len(t_all):,} bars 2018+: max |t| {t_all.abs().max():.2f}; |t| >= 3 on {(t_all.abs() >= 3).mean():.2%} of bars; "
      f">= 5 on {(t_all.abs() >= 5).sum()} bars (median t {t_all.median():+.2f}: following the EMA-5 loses on 5-min NQ)")
for key, src, pos_only, ENTER, EXIT in (("a as written", daily, False, 5.0, 3.0), ("b t >= +5 only", daily, True, 5.0, 3.0),
                                        ("c continuous history", cont, False, 5.0, 3.0),
                                        ("d extra look: |t|>=2.5, exit<1.5, continuous", cont, False, 2.5, 1.5),
                                        ("e extra look: t>=+2.5, exit<1.5, continuous", cont, True, 2.5, 1.5)):
    S = b.join(src); trades = []
    for day, x in S.groupby("date"):
        if pd.Timestamp(str(int(day))) < pd.Timestamp("2018-01-01"): continue
        pos, entry = 0, 0.0; rows = list(x.itertuples())
        for i in range(len(rows) - 1):
            r, nx = rows[i], rows[i + 1]
            if np.isnan(r.t): continue
            if pos == 0 and ((r.t >= ENTER) if pos_only else (abs(r.t) >= ENTER)) and nx.Index.time() < pd.Timestamp("15:00").time():
                pos, entry = int(r.sig), nx.open
            elif pos != 0 and abs(r.t) < EXIT:
                trades.append(dict(date=pd.Timestamp(str(int(day))), side=pos, net=pos * (nx.open - entry) * PV - COST)); pos = 0
        if pos != 0:
            trades.append(dict(date=pd.Timestamp(str(int(day))), side=pos, net=pos * (rows[-1].close - entry) * PV - COST))
    res[key] = pd.DataFrame(trades).set_index("date") if trades else pd.DataFrame(columns=["side", "net"], index=pd.DatetimeIndex([], name="date"))


def st(s): return f"n {len(s):4d} ${s.mean():+5.0f} t {s.mean() / s.std() * np.sqrt(len(s)):+.1f}" if len(s) > 2 else f"n {len(s)}"


print(__doc__.split("\n")[0])
for key, r in res.items():
    print(f"  {key:44s} all {st(r.net)} | longs {st(r.net[r.side > 0])} | shorts {st(r.net[r.side < 0])} | "
          f"2018-22 {st(r.net[r.index < '2023'])} | 2023+ {st(r.net[r.index >= '2023'])}")
