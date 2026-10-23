"""FC 2B, Flow-Confirmed Opening Drive (user's file, 2026-10-23; code + overview in checks/candidates/fc_2b/).
Python rebuild of the PowerLanguage signal on our NQ 1-minute day-session data (2017-05 onward; 2017 = z-score warm-up):
  opening range = bars stamped 08:31-09:00 CT; dir = sign(close of 09:00 bar - open of 08:31 bar);
  ratio = sum(V x (C - O) / max(H - L, 0.25)) / sum(V) over the range; z vs the previous ZLookback (60) days' ratios
  (population sd; at least 20 days); enter at the 09:01 bar's open when dir and z agree beyond 1.0.
  Exits as coded: from the bar AFTER the entry bar a stop = max(entry - 100, best high since the signal close - 150,
  entry + 1 once a high reached entry + 66) (shorts mirrored), recomputed at each bar close; a stop fills at the stop or
  at the open if the bar gaps through it; at 14:58 or later -> market exit at the next bar's open (14:59 bar); on early
  closes the last bar's close (SetExitOnClose). The entry bar has no working stop (as in the code).
Costs: $7.25 per NQ round trip + 1 tick per market / stop fill (entry, stop, EOD). Per NQ (1 MNQ = 1/10).
  python3 analysis/fc_2b_test.py [ZMIN]
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


def signals(days, zlook=60, warm=20, zmin=1.0):
    buf, out = [], []
    for dt, g in days.items():
        orr = g[g.time <= 900]
        if len(orr) == 0: continue
        bd = orr.volume * (orr.close - orr.open) / np.maximum(orr.high - orr.low, TICK)
        ratio = bd.sum() / max(orr.volume.sum(), 1)
        n = min(len(buf), zlook); z = 0.0
        if n >= 2:
            h = np.array(buf[-n:]); vr = (h ** 2).mean() - h.mean() ** 2
            if vr > 0: z = (ratio - h.mean()) / np.sqrt(vr)
        warm_ok = len(buf) >= warm; buf.append(ratio)
        oc, oo = orr.close.iloc[-1], orr.open.iloc[0]; dr = 1 if oc > oo else -1 if oc < oo else 0
        side = dr if (warm_ok and dr and dr * z >= zmin) else 0
        out.append(dict(date=pd.Timestamp(str(dt)), side=side, z=z, dir=dr, sig_close=oc, has_900=(orr.time.iloc[-1] == 900)))
    return pd.DataFrame(out)


def trade(g, side, sig_close, sl=100.0, trail=150.0, be=0.66):
    a = g[g.time >= 901].reset_index(drop=True)
    if len(a) == 0: return None
    e = a.open.iloc[0]; best = sig_close; armed = False; stop = None
    for i in range(len(a)):
        o, h, l, c, t = a.open[i], a.high[i], a.low[i], a.close[i], a.time[i]
        if i > 0:
            if stop is not None and ((side > 0 and l <= stop) or (side < 0 and h >= stop)):
                px = min(o, stop) if side > 0 else max(o, stop)
                return dict(entry=e, exit=px, kind="stop", minutes=i, gross=(px - e) * side * PV)
            if a.time[i - 1] >= 1458:
                return dict(entry=e, exit=o, kind="eod", minutes=i, gross=(o - e) * side * PV)
        # bar close: update and set the stop for the next bar
        if side > 0:
            best = max(best, h); armed = armed or (be > 0 and h >= e + be * sl)
            stop = max(e - sl, best - trail if trail else -1e18, e + 4 * TICK if armed else -1e18)
        else:
            best = min(best, l); armed = armed or (be > 0 and l <= e - be * sl)
            stop = min(e + sl, best + trail if trail else 1e18, e - 4 * TICK if armed else 1e18)
    c = a.close.iloc[-1]
    return dict(entry=e, exit=c, kind="close", minutes=len(a), gross=(c - e) * side * PV)


def run(days, sig, **kw):
    rows = []
    for _, s in sig[sig.side != 0].iterrows():
        g = days[int(s.date.strftime("%Y%m%d"))]
        r = trade(g, s.side, s.sig_close, **kw)
        if r: rows.append(dict(date=s.date, side=s.side, **r))
    t = pd.DataFrame(rows)
    t["net"] = t.gross - COST - 2 * TICK * PV          # entry market fill + stop / EOD market fill
    return t[t.date >= "2018-01-01"].reset_index(drop=True)


def line(t, nm):
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); pf = x[x > 0].sum() / -x[x < 0].sum()
    a, b = x[y < 2023], x[y >= 2023]
    ta = lambda q: q.mean() / q.std() * np.sqrt(len(q))
    return (f"   {nm:<34} n={len(x):4d} win {np.mean(x > 0):.0%} ${x.mean():5.0f} PF {pf:.2f} t {ta(x):4.1f} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${a.mean():4.0f} (t {ta(a):.1f}) | 23+ ${b.mean():4.0f} (t {ta(b):.1f})")


if __name__ == "__main__":
    zmin = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    print(__doc__.split("\n")[0])
    days = load(); sig = signals(days, zmin=zmin); t = run(days, sig)
    print(f"\n1. Rebuild, per NQ after costs (z >= {zmin}):")
    print(line(t, "all")); print(line(t[t.side > 0], "longs")); print(line(t[t.side < 0], "shorts"))
    print("   by year ($ per NQ):", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("   exits:", t.kind.value_counts().to_dict(), f"| worst ${t.net.min():,.0f}, best ${t.net.max():,.0f}")
    top = t.net.sort_values(ascending=False); k = int(round(0.09 * len(t)))
    print(f"   tail: top 9% ({k}) trades ${top.iloc[:k].sum():,.0f}, the rest ${top.iloc[k:].sum():,.0f}")

    print("\n2. Controls (same exits):")
    rng = np.random.default_rng(1); base = sig.copy()
    elig = base[base.dir != 0]
    print(line(run(days, base.assign(side=base.dir.where(base.index >= 20, 0))), "no flow filter (every drive day)"))
    rs = []
    for r in range(20):
        s2 = base.copy(); s2["side"] = 0; pick = rng.choice(elig.index[elig.index >= 20], (base.side != 0).sum(), replace=False)
        s2.loc[pick, "side"] = rng.choice([-1, 1], len(pick)); rs.append(run(days, s2).net.mean())
    print(f"   random days + random side, same count (20 runs): ${np.mean(rs):.0f} (max ${max(rs):.0f}) vs ${t.net.mean():.0f}")
    rv = [run(days, base.assign(side=base.side * rng.choice([-1, 1], len(base)))).net.mean() for _ in range(20)]
    print(f"   same days, random side (20 runs): ${np.mean(rv):.0f} (max ${max(rv):.0f})")
    print(line(run(days, base.assign(side=-base.side)), "opposite side"))
    for z2 in (0.5, 0.75, 1.25, 1.5):
        print(line(run(days, signals(days, zmin=z2)), f"z >= {z2}"))
    for nm, kw in (("stop 100, no trail, no BE", dict(trail=0, be=0)), ("trail 100", dict(trail=100)), ("trail 200", dict(trail=200)),
                   ("stop 75", dict(sl=75)), ("stop 150", dict(sl=150))):
        print(line(run(days, sig, **kw), nm))

    alld = pd.bdate_range("2018-01-01", t.date.max())
    dl = lambda q: q.groupby(q.date).net.sum().reindex(alld, fill_value=0.0)
    print("\n3. Standard metrics per NQ:")
    rows = {"FC 2B": (dl(t), t.net), "longs": (dl(t[t.side > 0]), t.net[t.side > 0]), "shorts": (dl(t[t.side < 0]), t.net[t.side < 0])}
    print(M.table(rows))
    bt, pm = R.report({f"{k} 2023+": v[0][v[0].index >= "2023-01-01"] for k, v in rows.items()}, n=2000); print(bt); print(pm)
    print(MC.report(t.net, dl(t), size=0.1, label="1 MNQ"))
    print(MC.report(t.net, dl(t), size=0.2, label="2 MNQ"))

    print("\n4. Overlap with the plan (agents/tasks/plan_daily_pnl.csv, per micro):")
    p = pd.read_csv("agents/tasks/plan_daily_pnl.csv", parse_dates=["date"]).set_index("date")
    f = dl(t).reindex(p.index, fill_value=0.0) / 10
    for c in p.columns:
        both = ((p[c] != 0) & (f != 0)).sum()
        print(f"   {c:<24} corr {np.corrcoef(p[c], f)[0, 1]:+.2f}   days both trade {both}")
    print(f"   plan total (1 micro each)  corr {np.corrcoef(p.sum(axis=1), f)[0, 1]:+.2f}")
    t.to_csv("checks/candidates/fc_2b/python_trades.csv", index=False)
