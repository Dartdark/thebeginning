"""MNQ ADX + Accelerator Oscillator, 1% risk (user's file, 2026-10-24; code in checks/candidates/adx_ac/).
Python rebuild of the PowerLanguage signal on our NQ 1-minute RTH bars (stamped 08:31-15:00 CT; indicators chained across
days on RTH bars only, as on a regular-session chart). The file gives no chart; main reading = a 1-minute Eastern RTH chart:
SessionStartTime 930 / LastEntryTime 1551 ET = 08:30 / 14:51 CT, SetExitOnClose = the 15:00 CT bar's close.
  ADX / DI+ (14, Wilder); AC = AO - SMA(AO, 8), AO = SMA(median, 8) - SMA(median, 39); ATR = SMA(true range, 14).
  Long setup: DI+ crosses above ADX (age 0, cancels a short setup); short setup: ADX crosses above DI+. Ages reset each day.
  Long: setup age <= 40 bars, DI+ > ADX, ADX >= 20 and rising, AC >= 0.1 ATR; short: age <= 40, ADX > DI+, ADX filter,
  AC <= -0.1 ATR. Flat and inside the window -> market entry at the next bar's open; the used setup is cleared.
  Exits (per contract, from the entry bar): stop 1 ATR, target 2 ATR (fills 1 tick through), break-even (stop to entry)
  once a bar's extreme reached +0.2 ATR (active from the next bar; a bar touching stop and target counts as the stop);
  else the session's last close. Re-entry allowed on later bars (a new cross is needed).
Costs: $7.25 per NQ round trip + 1 tick per market / stop fill (entry, stop, close). Per NQ (1 MNQ = 1/10).
  python3 analysis/adx_ac_test.py
"""
import sys, glob, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, resampling as R, montecarlo as MC

PV, TICK, COST = 20.0, 0.25, 7.25


def load(minutes=1, full=False, flat=1600):
    """full=True: the 24-hour CT chart (day + overnight files; session end = last bar at or before `flat`)."""
    fs = sorted(glob.glob("data/NQ_1min_20*.csv")) + (sorted(glob.glob("data/NQ_1min_ON_*.csv")) if full else [])
    d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    d = d.drop_duplicates(["date", "time"]).sort_values(["date", "time"])
    if not full: d = d[(d.time >= 831) & (d.time <= 1500)]
    d = d.reset_index(drop=True)
    if full:
        nt = np.r_[d.time.to_numpy()[1:], 9999]; nd = np.r_[d.date.to_numpy()[1:], 0]
        d["sess_end"] = (d.time <= flat) & ((nt > flat) | (nd != d.date))
        return d
    if minutes > 1:
        mm = (d.time // 100) * 60 + d.time % 100
        b = ((mm - 511) // minutes) * minutes + 510 + minutes             # bar stamped at its close (08:35, 08:40, ...)
        d["bar"] = (b // 60) * 100 + b % 60
        d = d.groupby(["date", "bar"]).agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                                          close=("close", "last")).reset_index().rename(columns={"bar": "time"})
    return d


def wilder(x, n):
    return pd.Series(x).ewm(alpha=1.0 / n, adjust=False).mean().to_numpy()


def indicators(d, adxn=14, fast=8, slow=39, atrn=14):
    h, l, c = d.high.to_numpy(), d.low.to_numpy(), d.close.to_numpy()
    ph, pl, pc = np.r_[np.nan, h[:-1]], np.r_[np.nan, l[:-1]], np.r_[np.nan, c[:-1]]
    up, dn = h - ph, pl - l
    pdm = np.where((up > dn) & (up > 0), up, 0.0); mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = np.fmax(h, pc) - np.fmin(l, pc); tr[0] = h[0] - l[0]
    str_ = wilder(tr, adxn); dip = 100 * wilder(pdm, adxn) / str_; dim = 100 * wilder(mdm, adxn) / str_
    dx = 100 * np.abs(dip - dim) / np.where(dip + dim > 0, dip + dim, np.nan)
    adx = wilder(np.nan_to_num(dx), adxn)
    med = pd.Series((h + l) / 2)
    ao = med.rolling(fast).mean() - med.rolling(slow).mean(); ac = (ao - ao.rolling(fast).mean()).to_numpy()
    atr = pd.Series(tr).rolling(atrn).mean().to_numpy()
    return adx, dip, ac, atr


def run(d, start_t=830, last_t=1451, minadx=20, conf=40, acm=0.1, sl=1.0, tp=2.0, be=0.2, side_only=0, rand=None, start="2018-01-01"):
    adx, dip, ac, atr = indicators(d)
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close"))
    t, dt = d.time.to_numpy(), d.date.to_numpy()
    N = len(d); la, sa = 999, 999; rows = []; i = 60
    newday = np.r_[True, dt[1:] != dt[:-1]]
    lastbar = d.sess_end.to_numpy() if "sess_end" in d else np.r_[dt[1:] != dt[:-1], True]
    while i < N - 1:
        if newday[i]: la, sa = 999, 999
        lc = dip[i] > adx[i] and dip[i - 1] <= adx[i - 1]; scx = adx[i] > dip[i] and adx[i - 1] <= dip[i - 1]
        if lc: la, sa = 0, 999
        elif la < 999: la += 1
        if scx: sa, la = 0, 999
        elif sa < 999: sa += 1
        filt = adx[i] >= minadx and adx[i] > adx[i - 1]; thr = acm * atr[i]
        L = la <= conf and dip[i] > adx[i] and filt and ac[i] >= thr
        S = sa <= conf and adx[i] > dip[i] and filt and ac[i] <= -thr
        if (L or S) and start_t <= t[i] <= last_t and not lastbar[i] and atr[i] > 0:
            side = 1 if L else -1
            if L: la = 999
            else: sa = 999
            if rand is not None: side = int(rand.choice([-1, 1]))
            if side_only and side != side_only: i += 1; continue
            j = i + 1; e = o[j]; A = atr[i]; stop = e - side * sl * A; tgt = e + side * tp * A; armed = False
            while True:
                st = e if armed else stop
                if (side > 0 and l[j] <= st) or (side < 0 and h[j] >= st):
                    px = min(o[j], st) if side > 0 else max(o[j], st); kind = "be" if armed else "stop"; break
                if (side > 0 and h[j] >= tgt + TICK) or (side < 0 and l[j] <= tgt - TICK):
                    px = max(o[j], tgt) if side > 0 else min(o[j], tgt); kind = "target"; break
                armed = armed or (side > 0 and h[j] >= e + be * A) or (side < 0 and l[j] <= e - be * A)
                if lastbar[j]: px = c[j]; kind = "close"; break
                j += 1
            rows.append(dict(date=pd.Timestamp(str(dt[i])), sig_time=t[i], exit_time=t[j], side=side, entry=e, exit=px, atr=A,
                             kind=kind, gross=(px - e) * side * PV))
            i = j                                   # flat again at bar j's close: may enter on it
            continue
        i += 1
    x = pd.DataFrame(rows)
    x["net"] = x.gross - COST - TICK * PV * np.where(x.kind == "target", 1, 2)
    return x[x.date >= start].reset_index(drop=True)


def line(t, nm):
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); pf = x[x > 0].sum() / -x[x < 0].sum()
    a, b = x[y < 2023], x[y >= 2023]
    ta = lambda q: q.mean() / q.std() * np.sqrt(len(q))
    return (f"   {nm:<34} n={len(x):5d} win {np.mean(x > 0):.0%} ${x.mean():6.1f} PF {pf:.2f} t {ta(x):5.1f} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${a.mean():5.1f} (t {ta(a):4.1f}) | 23+ ${b.mean():5.1f} (t {ta(b):4.1f})")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    d1 = load(1); t = run(d1)
    print(f"\n1. Rebuild, main reading (1-min Eastern RTH chart = entries 08:30-14:51 CT), per NQ after costs:")
    print(line(t, "all")); print(line(t[t.side > 0], "longs")); print(line(t[t.side < 0], "shorts"))
    print("   by year ($ per NQ):", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("   exits:", t.kind.value_counts().to_dict(), f"| trades a day {len(t) / t.date.nunique():.1f} on {t.date.nunique()} days, "
          f"median ATR {t.atr.median():.1f} pts, gross ${t.gross.mean():.1f} vs costs ${(t.gross - t.net).mean():.1f} a trade")
    print("\n2. The user's standard chart: 1-min, Exchange time (CT), CME 24-hour session; indicators on all bars,")
    print("   entries 09:30-15:51 CT, SetExitOnClose = the 16:00 CT session end (Apex needs flat by 15:59: also shown at 15:58):")
    dF = load(1, full=True); tF = run(dF, start_t=930, last_t=1551)
    print(line(tF, "24h CT chart, exit 16:00")); print(line(tF[tF.side > 0], "   longs")); print(line(tF[tF.side < 0], "   shorts"))
    print("   by year:", tF.groupby(tF.date.dt.year).net.sum().round(0).astype(int).to_dict(), "| exits", tF.kind.value_counts().to_dict())
    print(line(run(load(1, full=True, flat=1558), start_t=930, last_t=1551), "24h CT chart, flat 15:58"))
    print(line(run(d1, start_t=930, last_t=1451), "RTH bars, times as CT (09:30-14:51)"))
    d5 = load(5); t5 = run(d5, last_t=1450)
    print(line(t5, "5-min Eastern RTH")); print(line(t5[t5.side > 0], "   5-min longs")); print(line(t5[t5.side < 0], "   5-min shorts"))
    print("\n3. Controls (1-min main reading, same entries and exits):")
    rng = np.random.default_rng(1); rv = [run(d1, rand=rng).net.mean() for _ in range(5)]
    print(f"   same signal bars, random side (5 runs): ${np.mean(rv):.1f} (max ${max(rv):.1f}) vs ${t.net.mean():.1f}")
    print(line(run(d1, acm=0.0), "no AC threshold (AC sign only)"))
    print(line(run(d1, be=0), "no break-even"))
    alld = pd.bdate_range("2018-01-01", t.date.max())
    dl = lambda q: q.groupby(q.date).net.sum().reindex(alld, fill_value=0.0)
    print("\n4. Standard metrics per NQ (main reading):")
    rows = {"ADX AC": (dl(t), t.net), "longs": (dl(t[t.side > 0]), t.net[t.side > 0]), "shorts": (dl(t[t.side < 0]), t.net[t.side < 0])}
    print(M.table(rows))
    bt, pm = R.report({f"{k} 2023+": v[0][v[0].index >= "2023-01-01"] for k, v in rows.items()}, n=2000); print(bt); print(pm)
    print(MC.report(t.net, dl(t), size=0.1, label="1 MNQ"))
    t.to_csv("checks/candidates/adx_ac/python_trades.csv", index=False)
