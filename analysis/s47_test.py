"""S47 / S47 v2, Europe-Open Impulse (user's files, 2026-10-23; code + overview in checks/candidates/s47_v2/).
Python rebuild on our 24-hour NQ grid (analysis/grid24, Dec 2017 onward), per the code's header:
  trading date = bars from 17:01 CT belong to the next date; overnight = 17:01-08:30; ATR_ON = mean overnight
  high - low of the previous 20 trading dates (>= 15 usable: >= 700 bars and a first bar by 17:10; roll sessions are
  not usable here because our continuous series is not back-adjusted, while the code rebuilds them; small difference);
  EU = 08:00 London in CT (zoneinfo); s = (last close <= EU+30 min - last close <= EU-15 min) / ATR_ON;
  trade if |s| > 0.0625; v2 also needs the 09:30 close - last close <= 08:30 to have the same sign.
  Entry 09:31 bar open; stop 0.5 x ATR_ON (tick-rounded away) from the bar after the entry bar, fill at the stop or the
  open if gapped; exit the 15:00 bar close. Skipped: quarterly roll sessions (Friday 8-14 through 2022-03, then Monday
  11-17), the code's holiday / early-close list.
Costs: $7.25 per NQ round trip + 1 tick per market / stop fill (entry, stop / exit). Per NQ; 1 MNQ = 1/10.
  python3 analysis/s47_test.py SCRATCH_DIR
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo
from datetime import datetime
from grid24 import jof
import metrics as M, resampling as R, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25


def eu_min(d):
    t = datetime(d.year, d.month, d.day, 8, 0, tzinfo=ZoneInfo("Europe/London")).astimezone(ZoneInfo("America/Chicago"))
    return t.hour * 60 + t.minute


def skip_day(d):
    m, dd, dow = d.month, d.day, d.dayofweek          # Monday = 0
    roll = False
    if m % 3 == 0:
        roll = (dow == 4 and 8 <= dd <= 14) if d.year * 100 + m <= 202203 else (dow == 0 and 11 <= dd <= 17)
    hol = ((m == 1 and dow == 0 and 15 <= dd <= 21) or (m == 2 and dow == 0 and 15 <= dd <= 21) or (m == 5 and dow == 0 and dd >= 25)
           or (d.year >= 2022 and m == 6 and ((dd == 19 and dow <= 4) or (dd == 18 and dow == 4) or (dd == 20 and dow == 0)))
           or (m == 7 and ((dd == 4 and dow <= 4) or (dd == 3 and dow == 4) or (dd == 5 and dow == 0)))
           or (m == 7 and dd == 3 and dow <= 3) or (m == 9 and dow == 0 and dd <= 7)
           or (m == 11 and dow == 3 and 22 <= dd <= 28) or (m == 11 and dow == 4 and 23 <= dd <= 29)
           or (m == 12 and dd == 24 and dow <= 3))
    return roll, hol


def build(g):
    """One row per trading date (weekday grid rows): overnight path = previous calendar row from 17:01 + this row to 08:30."""
    rows = []; c = g.c; h = g.h; l = g.l; o = g.o
    for r in range(1, g.D):
        d = pd.Timestamp(g.ts[r])
        if d.dayofweek >= 5: continue
        prev = r - 1
        while prev > 0 and pd.Timestamp(g.ts[prev]).dayofweek == 5: prev -= 1       # Monday: Sunday evening row is r-1
        eve_c = c[r - 1, jof(1701):]; eve_h = h[r - 1, jof(1701):]; eve_l = l[r - 1, jof(1701):]
        mor_c = c[r, :jof(830) + 1]; mor_h = h[r, :jof(830) + 1]; mor_l = l[r, :jof(830) + 1]
        onc = np.r_[eve_c, mor_c]; ok_bars = np.isfinite(onc)
        n = ok_bars.sum(); first_ok = ok_bars[:10].any()
        rng = (np.nanmax(np.r_[eve_h, mor_h]) - np.nanmin(np.r_[eve_l, mor_l])) if n else np.nan
        roll, hol = skip_day(d)
        rows.append(dict(r=r, date=d, n=n, first_ok=first_ok, rng=rng, roll=roll, hol=hol))
    return pd.DataFrame(rows)


def last_close(g, r, minute):
    """Last close at or before 'minute' of the trading date (minute < 0 = previous evening)."""
    if minute >= 0:
        seg = g.c[r, :minute + 1]; seg = seg[np.isfinite(seg)]
        if len(seg): return seg[-1]
        minute = -1
    seg = g.c[r - 1, :1440 + minute + 1]; seg = seg[np.isfinite(seg)]
    return seg[-1] if len(seg) else np.nan


def run(g, T, v2=True, stop_atr=0.5, thr=0.0625, side_override=None):
    usable = (T.n >= 700) & T.first_ok & ~T.roll
    onr = T.rng.where(usable)
    atr = onr.shift(1).rolling(20, min_periods=1).mean(); cnt = onr.shift(1).rolling(20, min_periods=1).count()
    out = []
    for i, x in T.iterrows():
        if x.roll or x.hol or not (x.n >= 700 and x.first_ok) or cnt[i] < 15 or not np.isfinite(atr[i]): continue
        r = int(x.r); A = atr[i]; eu = eu_min(x.date)
        p0, p1 = last_close(g, r, eu - 15), last_close(g, r, eu + 30)
        ny0, c930 = last_close(g, r, jof(830)), g.c[r, jof(930)]
        if not np.all(np.isfinite([p0, p1, ny0, c930])): continue
        s = (p1 - p0) / A
        if abs(s) <= thr: continue
        side = 1 if s > 0 else -1
        if v2 and not ((side > 0 and c930 > ny0) or (side < 0 and c930 < ny0)): continue
        if side_override is not None: side = side_override(i, side)
        e = g.o[r, jof(931)]
        if not np.isfinite(e): continue
        sp = np.floor((e - stop_atr * A) / TICK) * TICK if side > 0 else np.ceil((e + stop_atr * A) / TICK) * TICK
        px, kind, j1 = np.nan, "time", jof(1500)
        for j in range(jof(932), jof(1500) + 1):
            hh, ll, oo = g.h[r, j], g.l[r, j], g.o[r, j]
            if not np.isfinite(hh): continue
            if (side > 0 and ll <= sp) or (side < 0 and hh >= sp):
                px = (min(oo, sp) if side > 0 else max(oo, sp)); kind = "stop"; j1 = j; break
        if kind == "time":
            seg = g.c[r, :jof(1500) + 1]; seg = seg[np.isfinite(seg)]; px = seg[-1]
        gross = (px - e) * side * PV
        out.append(dict(date=x.date, day=r, j0=jof(931), j1=j1, side=side, entry=e, exit=px, kind=kind, s=s, atr=A,
                        net=gross - COST - 2 * TICK * PV))
    return pd.DataFrame(out)


def line(t, nm):
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); pf = x[x > 0].sum() / -x[x < 0].sum()
    a, b = x[y < 2023], x[y >= 2023]; ta = lambda q: q.mean() / q.std() * np.sqrt(len(q))
    return (f"   {nm:<30} n={len(x):4d} win {np.mean(x > 0):.0%} ${x.mean():5.0f} PF {pf:.2f} t {ta(x):4.1f} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${a.mean():4.0f} (t {ta(a):.1f}) | 23+ ${b.mean():4.0f} (t {ta(b):.1f})")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); T = build(g)
    v2 = run(g, T, v2=True); v1 = run(g, T, v2=False)
    print("\n1. Rebuild, per NQ after our costs:")
    for nm, t in (("S47 v2", v2), ("  v2 longs", v2[v2.side > 0]), ("  v2 shorts", v2[v2.side < 0]),
                  ("S47 (no NY agreement)", v1), ("  disagreement days only", v1[~v1.date.isin(v2.date)])):
        print(line(t, nm))
    print("   v2 by year ($ per NQ):", v2.groupby(v2.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("   S47 by year ($ per NQ):", v1.groupby(v1.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("   v2 exits:", v2.kind.value_counts().to_dict())

    print("\n2. Controls on v2 (same days, same stop / exit):")
    rng = np.random.default_rng(1)
    rs = [run(g, T, v2=True, side_override=lambda i, s: int(rng.choice([-1, 1]))).net.mean() for _ in range(10)]
    print(f"   random side (10 runs): ${np.mean(rs):.0f} (max ${max(rs):.0f}) vs ${v2.net.mean():.0f}")
    print(line(run(g, T, v2=True, side_override=lambda i, s: -s), "opposite side"))
    ny_only = []
    for st in (0.4, 0.6):
        print(line(run(g, T, v2=True, stop_atr=st), f"stop {st} x ATR_ON"))
    for th in (0.03, 0.125):
        print(line(run(g, T, v2=True, thr=th), f"threshold {th}"))

    alld = pd.bdate_range("2018-01-01", v2.date.max())
    dl = lambda q: q.groupby(q.date).net.sum().reindex(alld, fill_value=0.0)
    print("\n3. Standard metrics per NQ (v2):")
    rows = {"S47 v2": (dl(v2), v2.net), "longs": (dl(v2[v2.side > 0]), v2.net[v2.side > 0]), "shorts": (dl(v2[v2.side < 0]), v2.net[v2.side < 0])}
    print(M.table(rows))
    bt, pm = R.report({f"{k} 2023+": v[0][v[0].index >= "2023-01-01"] for k, v in rows.items()}, n=2000); print(bt); print(pm)
    print(MC.report(v2.net, dl(v2), size=0.1, label="1 MNQ"))

    print("\n4. Overlap (daily P&L correlation; days both trade):")
    p = pd.read_csv("agents/tasks/plan_daily_pnl.csv", parse_dates=["date"]).set_index("date")
    f = dl(v2).reindex(p.index, fill_value=0.0) / 10
    fc = pd.read_csv("checks/candidates/fc_2b/trades.csv", parse_dates=["date"]); fcd = fc.groupby("date").net.sum().reindex(p.index, fill_value=0.0) / 10
    for c in list(p.columns) + ["FC2B"]:
        x = fcd if c == "FC2B" else p[c]
        print(f"   {c:<24} corr {np.corrcoef(x, f)[0, 1]:+.2f}   days both trade {int(((x != 0) & (f != 0)).sum())}")
    print(f"   plan total               corr {np.corrcoef(p.sum(axis=1), f)[0, 1]:+.2f}")
    v2.to_csv("checks/candidates/s47_v2/python_trades_v2.csv", index=False); v1.to_csv("checks/candidates/s47_v2/python_trades_s47.csv", index=False)
