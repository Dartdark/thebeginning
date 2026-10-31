"""ICT 'Accumulation-Manipulation-Distribution' (Power of 3) on NQ 2018-2026 (paper: Taylor 2026, arXiv 2610.35887; scout
2026-10-29). Paper's rules (NQ 15-min 2022-26): Asia range 18:00-23:00 CT (prior evening), London 01:00-04:00 CT sweeps one side
by >= 10 pts before 03:00 CT and closes back inside before 04:00 CT; bilateral sweeps and Asia ranges above the 75th percentile
skipped; bullish (low swept) -> long, bearish -> short. Paper: no direction beyond the daily trend regime (right 62-71% with the
trend, 25-30% against). Our check, fixed before looking, 1-min bars: (a) signal direction from 08:40 CT open to 09:30 close and
to 15:00; (b) the paper's trade adapted to Apex: enter 08:40 open, stop London extreme -/+ 4 pts, target the opposite Asia
boundary, out 15:00; days whose target or stop traded before 08:40 skipped (paper: target; stop added after a first run let
the stop fill above a long entry), stop fills at the bar open on a gap; (c) split by trend (prior close vs 20-day SMA) and a
trend-only control on the same days. Per NQ after $7.25 + 1 tick a side; FOMC / NFP not removed (noted).
python3 analysis/ict_amd_test.py
"""
import glob, numpy as np, pandas as pd
PV, COST = 20, 7.25 + 2 * 0.25 * 20
on = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/NQ_1min_ON_20*.csv"))])
rth = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/NQ_1min_20*.csv")) if "_ON_" not in f])
on_g = {k: g for k, g in on.groupby("date")}; rth_g = {k: g for k, g in rth.groupby("date")}
days = sorted(rth_g); closes = pd.Series({d: rth_g[d][rth_g[d].time <= 1500].close.iloc[-1] for d in days})
sma = closes.rolling(20).mean()
rows = []
for i, d in enumerate(days[1:], 1):
    dt = pd.Timestamp(str(d)); prev = int((dt - pd.Timedelta(days=1)).strftime("%Y%m%d"))
    if dt.weekday() == 0: prev = int((dt - pd.Timedelta(days=1)).strftime("%Y%m%d"))     # Sunday evening
    a = on_g.get(prev); l = on_g.get(d); r = rth_g[d]
    if a is None or l is None: continue
    a = a[(a.time > 1800) & (a.time <= 2300)]; l = l[(l.time > 100) & (l.time <= 400)]
    if len(a) < 200 or len(l) < 150: continue
    ah, al = a.high.max(), a.low.min()
    lo_hit = l[l.low <= al - 10]; hi_hit = l[l.high >= ah + 10]
    if len(lo_hit) and len(hi_hit): continue
    side = 0
    for hit, sgn in ((lo_hit, 1), (hi_hit, -1)):
        if len(hit) and hit.time.iloc[0] <= 300:
            after = l[l.time > hit.time.iloc[0]]
            if len(after[(after.close < ah) & (after.close > al)]): side = sgn
    if side == 0: continue
    ext = l.low.min() if side > 0 else l.high.max()
    pre = pd.concat([on_g[d][on_g[d].time > 400], r[r.time <= 840]])
    hit_before = (pre.high.max() >= ah) if side > 0 else (pre.low.min() <= al)
    stop_before = (pre.low.min() <= ext - 4) if side > 0 else (pre.high.max() >= ext + 4)   # setup void before entry
    e = r[r.time >= 841]
    if len(e) < 300: continue
    entry = e.open.iloc[0]; stop = ext - 4 if side > 0 else ext + 4; tgt = ah if side > 0 else al
    p930 = side * (e[e.time <= 930].close.iloc[-1] - entry); p1500 = side * (e[e.time <= 1500].close.iloc[-1] - entry)
    ex = None
    for _, b in e[e.time <= 1500].iterrows():
        if side > 0 and b.low <= stop: ex = min(b.open, stop); break            # gap through the stop fills at the open
        if side < 0 and b.high >= stop: ex = max(b.open, stop); break
        if (side > 0 and b.high >= tgt) or (side < 0 and b.low <= tgt): ex = tgt; break
    if ex is None: ex = e[e.time <= 1500].close.iloc[-1]
    trend = 1 if closes[days[i - 1]] > sma[days[i - 1]] else -1
    rows.append(dict(date=dt, side=side, rng=ah - al, p930=p930, p1500=p1500, trade=side * (ex - entry), hit_before=hit_before,
                     trend=trend, risk=abs(entry - stop), stop_before=stop_before))
x = pd.DataFrame(rows).set_index("date"); x = x[x.index >= "2018-01-01"]
x = x[x.rng <= x.rng.expanding(60).quantile(0.75).shift(1).fillna(np.inf)]
print(__doc__.split("\n")[0]); print(f"signal days {len(x)} ({x.side.gt(0).sum()} long / {x.side.lt(0).sum()} short)")
def show(nm, s):
    s = s.dropna(); print(f"   {nm:44s} n {len(s):4d}  ${s.mean():+6.0f}  t {s.mean() / s.std() * np.sqrt(len(s)):+.1f}  win {np.mean(s > 0):.0%}")
show("direction 08:40 -> 09:30 (net)", x.p930 * PV - COST)
show("direction 08:40 -> 15:00 (net)", x.p1500 * PV - COST)
t = x[~x.hit_before & ~x.stop_before]
show("paper trade (target not yet hit), net", t.trade * PV - COST)
for per, m in (("2018-22", t.index < "2023"), ("2023+", t.index >= "2023")): show(f"   {per}", t.trade[m] * PV - COST)
for nm, m in (("   longs", t.side > 0), ("   shorts", t.side < 0), ("   with trend", t.side == t.trend), ("   against trend", t.side != t.trend)):
    show(nm, t.trade[m] * PV - COST)
show("trend-only control, same days 08:40 -> 15:00", (x.trend * x.p1500 * x.side) * PV - COST)
