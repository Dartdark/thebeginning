"""Supply disruptions and trend-following in crude oil (user's original study, July 2026, PDF with the full rule spec):
oil trend-following has no unconditional edge, but a 20-bar breakout (S3) inside SUPPLY-disruption windows (physical flow
impaired) has been profitable 5 of 5 times since 2007 at 8-10x peacetime expectancy, while THREAT windows (headlines, no
lost barrels) lose. The author's suggested check: score your own CL breakout inside / outside the dated windows.
S3 (appendix): hourly bars; long if close > highest high of the prior 20 bars and close > SMA(200) (short symmetric);
enter at the signal bar's close; hard stop 1.5 x ATR(14, Wilder); once +2R, trail at 0.25 x the initial stop distance
from the best price; stop fills gap-aware (bar opens beyond the stop -> fill at the open). Scored in R.
Windows inside our data (CL 1-min 2017-12 .. 2026-10, CT): supply COVID 2020-02-01..05-31, Russia 2022-02-24..06-30, Iran war
2026-02-28..04-17, renewed US-Iran 2026-06-28..07-31 (open-ended in the paper; July is when its table stops); threat Abqaiq
2019-09, Soleimani 2020-01, Iran-Israel 2024-04 and 2024-10, Twelve-Day War 2025-06-13..06-27. The paper's windows were set
with hindsight; this checks whether the split rhymes on our data, not whether it can be traded live.
Series: our CL continuous series with the roll jumps removed (back-adjusted: one-minute moves > 0.3% at the 17:01 / 3:32 CT
roll bars set to 0; the paper shows the roll policy alone can flip a result). Costs $7.25 + 1 tick a fill, 1 CL ($1,000/pt).
  A  S3 as specified (multi-day holds; NOT Apex-legal), by window class, longs / shorts
  B  Apex-legal S3: same signals, entries 8:00-14:00 CT, flat at 15:55 CT
  C  our own CL trades by window: Twin Continuation on CL (BO / MO day trades) and the CL Sunday fade
  python3 analysis/oil_supply_windows_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import load

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 1000.0, 0.01, 7.25
SUPPLY = [("COVID", "2020-02-01", "2020-05-31"), ("Russia", "2022-02-24", "2022-06-30"), ("Iran war", "2026-02-28", "2026-04-17"),
          ("US-Iran renewed", "2026-06-28", "2026-07-31")]
THREAT = [("Abqaiq", "2019-09-01", "2019-09-30"), ("Soleimani", "2020-01-01", "2020-01-31"), ("Iran-Israel Apr", "2024-04-01", "2024-04-30"),
          ("Iran-Israel Oct", "2024-10-01", "2024-10-31"), ("Twelve-Day War", "2025-06-13", "2025-06-27")]


def window(d):
    for nm, a, b in SUPPLY:
        if pd.Timestamp(a) <= d <= pd.Timestamp(b) + pd.Timedelta(hours=23, minutes=59): return "supply", nm
    for nm, a, b in THREAT:
        if pd.Timestamp(a) <= d <= pd.Timestamp(b) + pd.Timedelta(hours=23, minutes=59): return "threat", nm
    return "outside", ""


def hourly(g):
    """Back-adjusted hourly OHLC (24h) from 1-min, with the minute timestamps."""
    o, h, l, c = (x.ravel() for x in (g.o, g.h, g.l, g.c))
    cf = pd.Series(c).ffill().to_numpy()
    lr = np.diff(np.log(cf), prepend=np.nan); lr[np.isnan(lr)] = 0.0
    col = np.arange(len(lr)) % 1440
    lr[np.isin(col, [jof(1701), jof(332)]) & (np.abs(lr) > 0.003)] = 0.0
    adj = np.exp(np.cumsum(lr)) / cf                                     # multiply raw prices by this
    T = np.arange(len(c)); ok = ~np.isnan(c)
    day = T // 1440; ts = pd.DatetimeIndex(g.ts)[day] + pd.to_timedelta(col, "min")
    df = pd.DataFrame({"o": o * adj, "h": h * adj, "l": l * adj, "c": c * adj, "raw": c, "t": ts})[ok]
    df["k"] = (T[ok] - 1) // 60
    b = df.groupby("k").agg(o=("o", "first"), h=("h", "max"), l=("l", "min"), c=("c", "last"), raw=("raw", "last"), t=("t", "last"))
    return b.reset_index(drop=True)


def s3(b, apex=False):
    o, h, l, c, raw = (b[k].to_numpy() for k in ("o", "h", "l", "c", "raw")); t = pd.DatetimeIndex(b.t)
    hhmm = t.hour * 100 + t.minute
    tr = np.maximum(h - l, np.maximum(np.abs(h - np.r_[np.nan, c[:-1]]), np.abs(l - np.r_[np.nan, c[:-1]])))
    atr = pd.Series(tr).ewm(alpha=1 / 14, adjust=False).mean().to_numpy()
    sma = pd.Series(c).rolling(200).mean().to_numpy()
    hh = pd.Series(h).rolling(20).max().shift(1).to_numpy(); ll = pd.Series(l).rolling(20).min().shift(1).to_numpy()
    scale = raw / c                                                      # back to the traded contract's price for $
    out = []; i = 201; N = len(c)
    while i < N - 1:
        side = 1 if (c[i] > hh[i] and c[i] > sma[i]) else (-1 if (c[i] < ll[i] and c[i] < sma[i]) else 0)
        if side == 0 or (apex and not (800 <= hhmm[i] <= 1400)): i += 1; continue
        e = c[i]; R = 1.5 * atr[i]; stop = e - side * R; best = e; x = None; j = i + 1
        while j < N:
            if apex and (hhmm[j] >= 1555 or t[j].date() != t[i].date()):
                x = c[j - 1] if t[j].date() != t[i].date() else c[j]; break
            if side * (stop - o[j]) >= 0: x = o[j]; break                # gapped through the stop
            if side * (stop - (l[j] if side > 0 else h[j])) >= 0: x = stop; break
            best = max(best, h[j]) if side > 0 else min(best, l[j])
            if side * (best - e) >= 2 * R:
                ns = best - side * 0.25 * R; stop = max(stop, ns) if side > 0 else min(stop, ns)
            if apex and hhmm[j] >= 1555: x = c[j]; break
            j += 1
        if x is None: break
        sc = scale[i]
        net = ((x - e) * side * sc - 2 * TICK) * PV - COMM; risk = R * sc * PV
        cls, nm = window(t[i])
        out.append(dict(t=t[i], side=side, net=net, R=net / risk, cls=cls, win=nm))
        i = j + 1
    return pd.DataFrame(out)


def report(T, label):
    T = T[T.t >= "2018-01-01"]
    print(f"\n{label}: {len(T)} trades, total {T.R.sum():+.1f}R, {T.R.mean():+.3f}R / trade, ${T.net.mean():+.0f} / trade")
    for cls in ("supply", "threat", "outside"):
        x = T[T.cls == cls]
        if len(x) == 0: print(f"   {cls:<8} none"); continue
        tt = x.R.mean() / x.R.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan
        print(f"   {cls:<8} n {len(x):4d}  {x.R.sum():+7.1f}R  {x.R.mean():+.3f}R/trade (t {tt:+.1f})  ${x.net.mean():+6.0f}/trade"
              f" | longs {x[x.side > 0].R.sum():+.1f}R (n {np.sum(x.side > 0)}), shorts {x[x.side < 0].R.sum():+.1f}R (n {np.sum(x.side < 0)})")
    w = T[T.cls != "outside"].groupby(["cls", "win"]).agg(n=("R", "size"), R=("R", "sum"), usd=("net", "sum"))
    print("   by window:", "; ".join(f"{k[1]} ({k[0][0]}) {v.R:+.1f}R n{int(v.n)}" for k, v in w.iterrows()))
    o = T[T.cls == "outside"]
    print("   outside by year (R):", o.groupby(o.t.dt.year).R.sum().round(1).to_dict())


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = load("CL"); b = hourly(g)
    report(s3(b), "A. S3 as specified, hourly, multi-day holds (not Apex-legal)")
    report(s3(b, apex=True), "B. Apex-legal S3: entries 8:00-14:00 CT, flat 15:55 CT")
    print("\nC. Our own CL trades by window ($ per CL):")
    tw = pd.read_pickle(SP + "twin_family_CL.pkl"); tw["t"] = pd.to_datetime(tw.date)
    tw["cls"] = [window(d)[0] for d in tw.t]
    for setup in ("BO", "MO"):
        x = tw[tw.setup == setup]
        print(f"   Twin Continuation on CL, {setup}: " + " | ".join(
            f"{c} n {np.sum(x.cls == c)} ${x[x.cls == c].net.mean():+.0f}" for c in ("supply", "threat", "outside")))
    # CL Sunday up-gap fade (funded plan, 2 MCL): same trade loop as analysis/cl_sunday_fade_bench.py
    fr = pickle.load(open(SP + "s_rank_gap2.pkl", "rb"))["frames"]["CL"]
    O, H, Cc = g.o.ravel(), g.h.ravel(), pd.Series(g.c.ravel()).ffill().to_numpy(); rows = []
    for r in fr.itertuples():
        if not r.ok or not (r.gA >= 0.1): continue
        e_i = int(r.sun) * 1440 + jof(1706); x_i = int(r.mon) * 1440 + jof(900)
        if np.isnan(O[e_i]): continue
        e = O[e_i] - TICK; px = Cc[x_i] + TICK; sp = e + 0.75 * r.atr
        hit = np.where(H[e_i:x_i + 1] >= sp)[0]
        if len(hit): jx = e_i + hit[0]; px = (sp if jx == e_i or np.isnan(O[jx]) else max(O[jx], sp)) + TICK
        rows.append(dict(t=pd.Timestamp(g.ts[int(r.mon)]), net=(e - px) * PV - COMM))
    cs = pd.DataFrame(rows); cs = cs[cs.t >= "2018-01-01"]; cs["cls"] = [window(d)[0] for d in cs.t]; cs["win"] = [window(d)[1] for d in cs.t]
    print("   CL Sunday fade (shorts): " + " | ".join(f"{c} n {np.sum(cs.cls == c)} ${cs[cs.cls == c].net.mean():+.0f}" for c in ("supply", "threat", "outside")))
    print("      in-window trades:", "; ".join(f"{r.t.date()} {r.win} ${r.net:+,.0f}" for r in cs[cs.cls != "outside"].itertuples()))
    A = s3(b); A = A[A.t >= "2018-01-01"]
    neg = A[(A.t >= "2020-04-14") & (A.t <= "2020-04-28")]
    print(f"\nCheck: S3 trades 2020-04-14..28 (CL's negative-price roll): n {len(neg)}, {neg.R.sum():+.1f}R; COVID window without them "
          f"{A[(A.win == 'COVID')].R.sum() - neg.R.sum():+.1f}R")
    o = cs[cs.cls == "outside"].net; a = cs.net
    print(f"\nCL Sunday fade: all {len(a)} trades ${a.sum():,.0f} (t {a.mean() / a.std() * np.sqrt(len(a)):.1f}); outside the windows {len(o)} trades "
          f"${o.sum():,.0f}, ${o.mean():+.0f}/trade, t {o.mean() / o.std() * np.sqrt(len(o)):.1f}, win {np.mean(o > 0):.0%}; "
          f"share of P&L from windows {1 - o.sum() / a.sum():.0%}")
    print("   outside by year:", o.groupby(cs[cs.cls == 'outside'].t.dt.year).sum().round(0).astype(int).to_dict())
