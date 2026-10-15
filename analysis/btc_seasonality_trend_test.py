"""Bitcoin seasonality, trend-following and mean reversion (Padysak & Vojtko, Quantpedia, SSRN 4081000; Gemini spot hourly
2015-11 .. 2022-02): long 21:00 -> 23:00 UTC ~33% a year (max DD -22% vs -84% buy & hold); long the next day when the
close is a 10-day high (trend) or a 10-day low (bounce), 10 better than 50 days; both combined ~98% a year, max DD -38%.

Here: CME bitcoin futures 1-min (scratch_data/btc.pkl, 2018-12 .. 2026-10, CT; CME halts 16:00-17:00 CT). Paper period
overlap = 2018-12 .. 2022-02; OUT OF SAMPLE = 2022-03 .. 2026-10. P&L per 1 BTC (10 MBT), $25 + 1 tick (5 pts) a fill =
$35 a round trip.
  A  return by UTC hour (all hours with data), in-sample overlap vs out-of-sample; the paper's 21:00 -> 23:00 UTC hold
     (= 15:00/16:00 -> 17:00/18:00 CT depending on DST, ACROSS the CME halt, i.e. NOT Apex-legal) as research
  B  daily signals on the session close (last bar before the 16:00 CT halt): close = max (min) of the last N session closes
     (N 10 / 50) -> long the next session, 17:00 open -> 15:59 close (Apex-legal: flat by 15:59); combined = either;
     vs long every session; in-sample overlap / out-of-sample; standard metrics on the combined 10-day rule
  python3 analysis/btc_seasonality_trend_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
COST = 25.0 + 2 * 5.0
OOS = pd.Timestamp("2022-03-01")


def minute_series(g):
    c = g.c.ravel(); o = g.o.ravel(); ok = ~np.isnan(c); idx = np.where(ok)[0]
    t = pd.DatetimeIndex(np.repeat(g.ts, 1440)[idx]) + pd.to_timedelta(idx % 1440, unit="m")   # bar close time, CT (naive)
    return pd.DataFrame({"o": o[idx], "c": c[idx]}, index=t)


def line(x, nm, w=34):
    x = x.dropna(); t = x.mean() / x.std() * np.sqrt(len(x)); pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    a, b = x[x.index < OOS], x[x.index >= OOS]
    ta = a.mean() / a.std() * np.sqrt(len(a)) if len(a) > 2 else np.nan; tb = b.mean() / b.std() * np.sqrt(len(b)) if len(b) > 2 else np.nan
    return (f"   {nm:<{w}} n {len(x):5d} avg ${x.mean():7.1f} PF {pf:4.2f} t {t:5.2f} win {np.mean(x > 0):.0%}"
            f" | 2018-12..22-02 ${a.mean():7.1f} (t {ta:4.1f}) | OOS 22-03..26 ${b.mean():7.1f} (t {tb:4.1f})")


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "btc.pkl", "rb")); S = minute_series(g)
    utc = S.index.tz_localize("America/Chicago", ambiguous="NaT", nonexistent="NaT").tz_convert("UTC")
    S = S[~utc.isna()]; S["utc"] = utc[~utc.isna()]
    # A: hourly returns in UTC (close-to-close of the last bar in each UTC hour), % per hour, by period
    H = S.set_index("utc").c.resample("1h").last().dropna()
    r = np.log(H).diff().dropna(); r = r[(r.index.to_series().diff() <= pd.Timedelta("1h")).values]
    r = r[r.abs() < 0.2]
    tab = pd.DataFrame({"2018-22 (paper overlap) bp": r[r.index < OOS.tz_localize("UTC")].groupby(r[r.index < OOS.tz_localize("UTC")].index.hour).mean() * 1e4,
                        "OOS 2022-26 bp": r[r.index >= OOS.tz_localize("UTC")].groupby(r[r.index >= OOS.tz_localize("UTC")].index.hour).mean() * 1e4,
                        "n OOS": r[r.index >= OOS.tz_localize("UTC")].groupby(r[r.index >= OOS.tz_localize("UTC")].index.hour).size()})
    print("\nA. Mean log return by UTC hour ending (CME futures; hours inside the CME halt have no data):")
    print(tab.round(1).to_string())
    # 21:00 -> 23:00 UTC hold, per 1 BTC
    out = []
    for d, grp in S.groupby(S.utc.dt.date):
        a = grp[grp.utc.dt.hour < 21]; b = grp[grp.utc.dt.hour < 23]
        if len(a) and len(b) and b.index[-1] > a.index[-1] and (b.utc.iloc[-1] - a.utc.iloc[-1]) >= pd.Timedelta("90min"):
            out.append(dict(date=pd.Timestamp(d), net=b.c.iloc[-1] - a.c.iloc[-1] - COST))
    X = pd.DataFrame(out).set_index("date").net
    print("\n" + line(X, "long ~21:00 -> 23:00 UTC (across halt)"))
    # B: daily session closes (last bar before 16:00 CT), next session 17:00 open -> 15:59 close
    S["sess"] = (S.index - pd.Timedelta("17h")).normalize()           # session = date of its 17:00 CT start + 1 day ... keyed by start
    sess = S.groupby("sess").agg(o=("o", "first"), c=("c", "last"), n=("c", "size"))
    sess = sess[sess.n >= 200]
    nxt = (sess.c - sess.o).shift(-1) - COST                          # next session's open -> close, per 1 BTC
    rows = {}
    for N in (10, 50):
        hi = sess.c >= sess.c.rolling(N).max(); lo = sess.c <= sess.c.rolling(N).min()
        rows[f"{N}-day high -> long next"] = nxt[hi]; rows[f"{N}-day low -> long next"] = nxt[lo]; rows[f"{N}-day high or low"] = nxt[hi | lo]
        rows[f"{N}-day neither (risky zone)"] = nxt[~(hi | lo)]
    rows["long every session"] = nxt
    print("\nB. Daily signals (per 1 BTC, next session 17:00 -> 15:59 CT):")
    for nm, x in rows.items():
        x = x.dropna(); x.index = pd.DatetimeIndex(x.index); print(line(x, nm))
    x = rows["10-day high or low"].dropna(); x.index = pd.DatetimeIndex(x.index)
    days = pd.DatetimeIndex(sess.index); dd = x.reindex(days, fill_value=0.0)
    lab = {"10-day high or low": (dd, x)}
    for nm in ("10-day high -> long next", "10-day low -> long next"):
        y = rows[nm].dropna(); y.index = pd.DatetimeIndex(y.index); lab[nm] = (y.reindex(days, fill_value=0.0), y)
    print("\nStandard metrics (per 1 BTC; this is long-only, so 'longs' = all):"); print(M.table(lab, capital=50_000))
    b_, p_ = R.report({k: v[0][v[0].index >= OOS] for k, v in lab.items()}, n=2000); print("OOS 2022-26 bootstrap:\n" + b_ + "\nOOS drawdown permutation:\n" + p_)
