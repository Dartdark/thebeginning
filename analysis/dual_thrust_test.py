"""NQ Dual Thrust v4, Central-time build (user's file, 2026-10-24; code in checks/candidates/dual_thrust/).
Python rebuild of the PowerLanguage signal on our NQ 1-minute day-session data (2017 = warm-up):
  prior RTH day (bars stamped 08:31-15:00 CT): H, L, C; RR = max(H - C, C - L) (NDays 1); ADR20 = mean of the last 20 RTH
  ranges; skip the day if RR / ADR20 > 1.2 (BandMax) or it is on the holiday list (the code's dates). Day open = open of
  the 08:31 bar. First bar (08:31-14:30) closing above open + 0.5 RR -> buy at the next bar's open (below open - 0.5 RR ->
  short). One trade a day. Entry bar: stop at the trigger bar's close -/+ 50 (v4 EntryBarStop), no target. From its close:
  stop entry -/+ 50, target entry +/- 100 (limit, fills when traded 1 tick through, no slippage); a bar touching both
  counts as the stop. A bar closing at 14:55 or later in a trade -> market exit at the next bar's open (14:56).
Costs: $7.25 per NQ round trip + 1 tick per market / stop fill (entry, stop, flatten). Per NQ (1 MNQ = 1/10).
  python3 analysis/dual_thrust_test.py
"""
import sys, glob, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, resampling as R, montecarlo as MC

PV, TICK, COST = 20.0, 0.25, 7.25


def load():
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/NQ_1min_20*.csv"))], ignore_index=True)
    d = d.drop_duplicates(["date", "time"]).sort_values(["date", "time"])
    d = d[(d.time >= 831) & (d.time <= 1500)]
    return {k: g.reset_index(drop=True) for k, g in d.groupby("date")}


def holiday(dt):
    mo, dy, dw = dt.month, dt.day, dt.isoweekday() % 7          # PowerLanguage DayOfWeek: 0 = Sunday, 1 = Monday
    return ((mo == 1 and dw == 1 and 15 <= dy <= 21) or (mo == 2 and dw == 1 and 15 <= dy <= 21) or (mo == 5 and dw == 1 and dy >= 25)
            or (mo == 6 and (dy == 19 or (dw == 1 and dy == 20) or (dw == 5 and dy == 18)))
            or (mo == 7 and (dy in (3, 4) or (dw == 1 and dy == 5))) or (mo == 9 and dw == 1 and dy <= 7)
            or (mo == 11 and ((dw == 4 and 22 <= dy <= 28) or (dw == 5 and 23 <= dy <= 29)))
            or (mo == 12 and (dy in (24, 25) or (dw == 1 and dy == 26))))


def setups(days, k=0.5, band=1.2, hol=True):
    """One row per day: the armed triggers and whether the day is allowed."""
    rows, prev = [], []
    for dk, g in days.items():
        dt = pd.Timestamp(str(dk))
        if len(prev) >= 20:
            H, L, C = prev[-1]; rr = max(H - C, C - L); adr = np.mean([h - l for h, l, _ in prev[-20:]])
            o = g.open.iloc[0]
            ok = rr > 0 and not (band > 0 and rr / adr > band) and not (hol and holiday(dt))
            rows.append(dict(date=dt, open=o, rr=rr, adr=adr, up=o + k * rr, dn=o - k * rr, ok=ok))
        if g.high.max() > g.low.min(): prev.append((g.high.max(), g.low.min(), g.close.iloc[-1]))
    return pd.DataFrame(rows)


def trade(g, up, dn, sl=50.0, tp=100.0, entry_bar_stop=True, last=1430, flat=1455, side_only=0, first=None):
    t, c = g.time.to_numpy(), g.close.to_numpy()
    o, h, l = g.open.to_numpy(), g.high.to_numpy(), g.low.to_numpy()
    for i in range(len(g) - 1):
        if t[i] > last: return None
        side = first if first is not None else (1 if c[i] > up else -1 if c[i] < dn else 0)
        if side == 0 or (side_only and side != side_only): continue
        e = o[i + 1]; trig = c[i]
        for j in range(i + 1, len(g)):
            if j > i + 1 and t[j - 1] >= flat:
                return dict(sig_time=t[i], exit_time=t[j], entry=e, exit=o[j], kind="flat", side=side, gross=(o[j] - e) * side * PV)
            if j == i + 1:
                stop = trig - side * sl if entry_bar_stop and sl > 0 else None; tgt = None
            else:
                stop = e - side * sl if sl > 0 else None; tgt = e + side * tp if tp > 0 else None
            if stop is not None and ((side > 0 and l[j] <= stop) or (side < 0 and h[j] >= stop)):
                px = min(o[j], stop) if side > 0 else max(o[j], stop)
                return dict(sig_time=t[i], exit_time=t[j], entry=e, exit=px, kind="stop", side=side, gross=(px - e) * side * PV)
            if tgt is not None and ((side > 0 and h[j] >= tgt + TICK) or (side < 0 and l[j] <= tgt - TICK)):
                px = max(o[j], tgt) if side > 0 else min(o[j], tgt)
                return dict(sig_time=t[i], exit_time=t[j], entry=e, exit=px, kind="target", side=side, gross=(px - e) * side * PV)
        return dict(sig_time=t[i], exit_time=t[-1], entry=e, exit=c[-1], kind="close", side=side, gross=(c[-1] - e) * side * PV)
    return None


def lab_trades(g, t):
    """Trades in the lab's format (grid24 rows / columns, raw exit; funded_lab.with_slippage adds the ticks)."""
    from grid24 import jof
    row = pd.Series(range(len(g.ts)), index=pd.DatetimeIndex(g.ts))
    nxt = lambda hm: jof(hm // 100 * 100 + hm % 100)
    return pd.DataFrame(dict(day=row.reindex(t.date).to_numpy(), j0=jof(t.sig_time.to_numpy()) + 1, j1=nxt(t.exit_time.to_numpy()),
                             side=t.side.to_numpy(), entry=t.entry.to_numpy(), exit=t.exit.to_numpy(),
                             kind=t.kind.map({"stop": 0, "target": 1, "flat": 2, "close": 2}).to_numpy()))


def run(days, S, start="2018-01-01", **kw):
    rows = []
    for s in S[S.ok].itertuples():
        g = days[int(s.date.strftime("%Y%m%d"))]
        r = trade(g, s.up, s.dn, **kw)
        if r: rows.append(dict(date=s.date, **r))
    t = pd.DataFrame(rows)
    t["net"] = t.gross - COST - TICK * PV * np.where(t.kind == "target", 1, 2)
    return t[t.date >= start].reset_index(drop=True)


def line(t, nm):
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); pf = x[x > 0].sum() / -x[x < 0].sum()
    a, b = x[y < 2023], x[y >= 2023]
    ta = lambda q: q.mean() / q.std() * np.sqrt(len(q))
    return (f"   {nm:<38} n={len(x):4d} win {np.mean(x > 0):.0%} ${x.mean():5.0f} PF {pf:.2f} t {ta(x):4.1f} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${a.mean():4.0f} (t {ta(a):.1f}) | 23+ ${b.mean():4.0f} (t {ta(b):.1f})")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    days = load(); S = setups(days); t = run(days, S)
    print(f"\n1. Rebuild (v4 as coded), per NQ after costs, {t.date.min().date()} -> {t.date.max().date()}:")
    print(line(t, "all")); print(line(t[t.side > 0], "longs")); print(line(t[t.side < 0], "shorts"))
    print("   by year ($ per NQ):", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("   exits:", t.kind.value_counts().to_dict(), f"| worst ${t.net.min():,.0f}, best ${t.net.max():,.0f}")
    print(f"   days allowed {S[S.date >= '2018'].ok.mean():.0%} (band skip {(S[S.date >= '2018'].rr / S[S.date >= '2018'].adr > 1.2).mean():.0%}), "
          f"trade on {len(t) / S[(S.date >= '2018') & S.ok].shape[0]:.0%} of allowed days; median signal time {int(t.sig_time.median())}")
    top = t.net.sort_values(ascending=False); k = int(round(0.05 * len(t)))
    print(f"   tail: top 5% ({k}) trades ${top.iloc[:k].sum():,.0f}, the rest ${top.iloc[k:].sum():,.0f}")
    print(line(run(days, S, entry_bar_stop=False), "v3 (no entry-bar stop)"))

    print("\n2. Controls (same exits):")
    rng = np.random.default_rng(1)
    rv = []
    for _ in range(20):
        rows = []
        for s in S[S.ok & (S.date >= "2018")].itertuples():
            g = days[int(s.date.strftime("%Y%m%d"))]; r0 = trade(g, s.up, s.dn)
            if r0 is None: continue
            # same signal bar, random side
            i = int(np.where(g.time.to_numpy() == r0["sig_time"])[0][0]); sd = rng.choice([-1, 1])
            sub = g.iloc[i:].reset_index(drop=True)
            r = trade(sub, np.inf, -np.inf, first=sd)
            if r: rows.append(dict(date=s.date, **r))
        x = pd.DataFrame(rows); x["net"] = x.gross - COST - TICK * PV * np.where(x.kind == "target", 1, 2); rv.append(x.net.mean())
    print(f"   same signal bar, random side (20 runs): ${np.mean(rv):.0f} (max ${max(rv):.0f}) vs ${t.net.mean():.0f}")
    rr_ = []
    for _ in range(20):
        rows = []
        al = S[S.ok & (S.date >= "2018")]
        for s in al.sample(len(t), random_state=int(rng.integers(1e9))).itertuples():
            g = days[int(s.date.strftime("%Y%m%d"))]; tm = g.time.to_numpy(); tm = tm[tm <= 1430]
            i = int(rng.integers(0, len(tm))); sub = g.iloc[i:].reset_index(drop=True)
            r = trade(sub, np.inf, -np.inf, first=int(rng.choice([-1, 1])))
            if r: rows.append(dict(date=s.date, **r))
        x = pd.DataFrame(rows); x["net"] = x.gross - COST - TICK * PV * np.where(x.kind == "target", 1, 2); rr_.append(x.net.mean())
    print(f"   random allowed day, random bar 08:31-14:30, random side, same count (20 runs): ${np.mean(rr_):.0f} (max ${max(rr_):.0f})")
    print("   sensitivity (not optimised; the user's settings stay):")
    for nm, S2, kw in (("K 0.4", setups(days, k=0.4), {}), ("K 0.6", setups(days, k=0.6), {}), ("K 0.7", setups(days, k=0.7), {}),
                       ("no band filter", setups(days, band=0), {}), ("band 1.9 (v2)", setups(days, band=1.9), {}),
                       ("no holiday filter", setups(days, hol=False), {}), ("stop 40 / target 80", S, dict(sl=40, tp=80)),
                       ("stop 60 / target 120", S, dict(sl=60, tp=120)), ("target 150", S, dict(tp=150)), ("no target", S, dict(tp=0))):
        print(line(run(days, S2, **kw), nm))

    alld = pd.bdate_range("2018-01-01", t.date.max())
    dl = lambda q: q.groupby(q.date).net.sum().reindex(alld, fill_value=0.0)
    print("\n3. Standard metrics per NQ:")
    rows = {"Dual Thrust": (dl(t), t.net), "longs": (dl(t[t.side > 0]), t.net[t.side > 0]), "shorts": (dl(t[t.side < 0]), t.net[t.side < 0])}
    print(M.table(rows))
    bt, pm = R.report({f"{k} 2023+": v[0][v[0].index >= "2023-01-01"] for k, v in rows.items()}, n=2000); print(bt); print(pm)
    print(MC.report(t.net, dl(t), size=0.1, label="1 MNQ"))
    print(MC.report(t.net, dl(t), size=0.3, label="3 MNQ"))

    print("\n4. Overlap with the plan (agents/tasks/plan_daily_pnl.csv, per micro):")
    p = pd.read_csv("agents/tasks/plan_daily_pnl.csv", parse_dates=["date"]).set_index("date")
    f = dl(t).reindex(p.index, fill_value=0.0) / 10
    for c in p.columns:
        both = ((p[c] != 0) & (f != 0)).sum()
        print(f"   {c:<24} corr {np.corrcoef(p[c], f)[0, 1]:+.2f}   days both trade {both}")
    print(f"   plan total (1 micro each)  corr {np.corrcoef(p.sum(axis=1), f)[0, 1]:+.2f}")
    t.to_csv("checks/candidates/dual_thrust/python_trades.csv", index=False)
