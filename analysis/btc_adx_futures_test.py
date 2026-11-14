"""BTC ADX ensemble on CME BITCOIN FUTURES (user 2026-11-13: 'cant it be traded on btc futures?'). Same rule as
analysis/btc_adx_ensemble_test.py, on data/BTC_1min_* (CME front month, Central time stamped at the close; from 2018-12-17),
roll jumps removed by ratio (largest reopen gap on days 15-31 of each month if > 4x the median reopen gap), candles on UTC
boundaries from the bars that exist (CME is closed 16:00-17:00 CT and weekends: indicators simply skip the gaps).
Dollars per MBT (0.1 BTC): $2.50 round trip + 1 tick (5 points = $0.50) on every fill = 17.5 points a fill.
 A  as coded: holds up to 240 h, over nights and weekends -> NOT Apex-legal (personal account only)
 B  Apex version: every book out at the last 15m close before 15:59 CT (the 15:30-15:45 candle), no entries 15:00-17:00 CT,
    books may re-enter after the reopen on a fresh signal
 C  B, longs only
Sizing shown: 1 MBT per book. Stop distance in $ per MBT printed (Apex 150K EOD trail $4,000).
  tools/run_stamped.sh analysis/btc_adx_futures_test.py > analysis/outputs/btc_adx_futures_test_output.txt
"""
import sys, glob, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import btc_adx_ensemble_test as P
print(__doc__.split("\n")[0])
MULT, CPTS = 0.1, 17.5


def load_fut():
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/BTC_1min_*.csv"))])
    ts = pd.to_datetime(d.date.astype(str) + d.time.astype(str).str.zfill(4), format="%Y%m%d%H%M")
    d = d.assign(ct=ts).drop_duplicates("ct").sort_values("ct").reset_index(drop=True)
    # roll jumps: first bar after a >= 30-minute pause, days 15-31, largest |gap| of the month if > 4x the median reopen gap
    brk = np.flatnonzero(d.ct.diff().dt.total_seconds().to_numpy() >= 1800)
    gap = d.open.to_numpy()[brk] / d.close.to_numpy()[brk - 1] - 1
    B = pd.DataFrame(dict(j=brk, gap=gap, ts=d.ct.to_numpy()[brk])); med = B.gap.abs().median(); f = np.ones(len(d)); n = 0
    for _, g in B[(B.ts.dt.day >= 15)].groupby([B.ts.dt.year, B.ts.dt.month]):
        k = g.gap.abs().idxmax()
        if abs(g.at[k, "gap"]) > 4 * med: f[:int(g.at[k, "j"])] *= 1 + g.at[k, "gap"]; n += 1
    print(f"futures bars {len(d)}, {d.ct.iloc[0]} -> {d.ct.iloc[-1]} CT, rolls removed {n} (median reopen gap {med:.3%})")
    for c in ("open", "high", "low", "close"): d[c] = d[c] * f
    d["f"] = f
    u = d.ct.dt.tz_localize("America/Chicago", ambiguous="NaT", nonexistent="NaT") - pd.Timedelta(minutes=1)
    d = d.assign(ts=u.dt.tz_convert("UTC").dt.tz_localize(None)).dropna(subset=["ts"]).set_index("ts")
    return d


m = load_fut()
m15 = P.rs(m, "15min"); h1 = P.rs(m, "1h"); h4 = P.rs(m, "4h")
fac = m.f.resample("15min", label="left", closed="left").last().reindex(m15.index).to_numpy()
adx, atr, st, bbw = P.indicators(h1)
ema = h4.close.ewm(span=200, adjust=False).mean().to_numpy().copy(); ema[:199] = np.nan
d4 = h4[h4.index.hour == 16].close
if len(d4) < 200: d4 = h4.groupby(h4.index.normalize()).close.last()      # 16:00 UTC is inside the CME break part of the year
lr = np.log(d4).diff(); vr = (lr.rolling(20).std() / lr.rolling(120).std()).to_numpy()
H1 = pd.DataFrame({"adx": adx, "atr": atr, "st": st, "bbw": bbw, "close": h1.close.to_numpy()}, index=h1.index)
ctx = (m15, H1, ema, h4.index.to_numpy(), vr, d4.index.to_numpy())
ct = m15.index.tz_localize("UTC").tz_convert("America/Chicago"); hm = ct.hour * 100 + ct.minute
flat = np.asarray(hm == 1530); noent = np.asarray((hm >= 1445) & (hm < 1700))
facs = pd.Series(fac, index=m15.index)


def report(d, nm):
    if not len(d): print(nm, "no trades"); return
    px = d.e.to_numpy() / facs.reindex(pd.DatetimeIndex(d.t)).to_numpy()            # real (unadjusted) entry price
    d = d.assign(usd=d.ret * px * MULT, stop_usd=d.R * px * MULT, day=pd.DatetimeIndex(d.tx).normalize())
    x = d.usd; pf = x[x > 0].sum() / -x[x < 0].sum(); t = x.mean() / x.std(ddof=1) * np.sqrt(len(x))
    dd = d.groupby("day").usd.sum(); td = dd.mean() / dd.std(ddof=1) * np.sqrt(len(dd)); eq = dd.cumsum(); mdd = (eq - eq.cummax()).min()
    yrs = (d.t.max() - d.t.min()).days / 365.25
    print(f"\n{nm}\n  {len(d)} book trades, win {np.mean(x > 0):.1%}, ${x.mean():.1f} per MBT a trade, PF {pf:.2f}, t {t:.2f} (daily t {td:.2f}), "
          f"${x.sum() / yrs:,.0f} a year, max DD ${mdd:,.0f}, worst trade ${x.min():,.0f}, worst day ${dd.min():,.0f}; stop $ per MBT median {d.stop_usd.median():.0f} (2025+ {d.stop_usd[d.yr >= 2025].median():.0f})")
    print("  R: mean %+.3f, 2019-22 %+.3f, 2023+ %+.3f | longs $%.1f (n %d)  shorts $%.1f (n %d)" % (
        d.r.mean(), d.r[d.yr <= 2022].mean(), d.r[d.yr >= 2023].mean(), x[d.side == 1].mean(), (d.side == 1).sum(), x[d.side == -1].mean(), (d.side == -1).sum()))
    print("  by year $: " + "  ".join(f"{y} {g.usd.sum():+,.0f} ({len(g)})" for y, g in d.groupby("yr")))
    print("  exits:", d.why.value_counts().to_dict())
    return d


A = report(P.run(ctx, cost_pts=CPTS), "A  as coded on CME futures (multi-day holds; not Apex-legal)")
B = report(P.run(ctx, cost_pts=CPTS, flat=flat, noent=noent), "B  Apex version: flat by 15:45 CT, no entries 14:45-17:00 CT")
C = report(P.run(ctx, cost_pts=CPTS, flat=flat, noent=noent, longs_only=True), "C  B, longs only")
for nm, d in (("A", A), ("B", B)):
    if d is not None: d.assign(date=pd.DatetimeIndex(d.tx).normalize().date, net=d.usd).to_csv(f"scratch_data/btc_adx_fut_{nm}.csv", index=False)
