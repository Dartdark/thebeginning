"""ORB -> VWAP Fade v1.1 (user's PDF with PowerLanguage, 2026-10-25; Kusho ORB / AMT family; checks/candidates/orb_vwap_fade/).
Rebuild on our ES 1-minute bars (Central time, close-stamped, 24-hour grid):
  Session bars = time > SessStart and <= SessEnd (1545). OR = the first 7 session bars; width = OR range / close of bar 7.
  Trade only if width >= 0.15%. From bar 8, while flat and no entry yet today (entries until 15:00): buy limit at the OR low if
  the OR low < VWAP, sell limit at the OR high if the OR high > VWAP (VWAP = typical price x volume from the first session
  bar, as of the previous bar). After a fill, from the next bar: target = limit at the VWAP (as of the previous bar), stop =
  the OR extreme -/+ 1.25 x OR range (a bar touching both = the stop). Flat at the bar after 15:45 (next bar at market).
  A limit fills when touched (MultiCharts' default) or, as a check, only when traded 1 tick through; a bar opening beyond
  the limit fills at the open.
The question: SessStart 930 on a Central-time chart is 10:30 ET, one hour after the cash open; 830 is the real open. Both are
run. Costs per ES: theirs ($1.50 a side + 1 tick on the stop and the EOD exit only, limits free) and ours ($5 round trip +
1 tick per market / stop fill). 2018-2026; the author's IS 2020-22 / OOS 2023-26.
  python3 analysis/orb_vwap_fade_test.py [SCRATCH_DIR] > analysis/outputs/orb_vwap_fade_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
g = pickle.load(open(SP + "ge.pkl", "rb"))
PV, TICK = 50.0, 0.25
TR = g.trading
NT = {"n": 0}


def run(sess=930, orbars=7, stop_mult=1.25, min_pct=0.15, through=0, comm_rt=3.0, slip_all=False, start="2018-01-01",
        sess_end=1545, cutoff=1500, count=True):
    if count: NT["n"] += 1
    j0 = jof(sess) + 1; je = jof(sess_end); jc = jof(cutoff)
    rows = []
    for r in TR:
        d = pd.Timestamp(g.ts[r])
        if d < pd.Timestamp(start): continue
        o, h, l, c, v = g.o[r], g.h[r], g.l[r], g.c[r], np.nan_to_num(g.v[r])
        if np.isnan(c[j0:j0 + orbars]).any() or np.isnan(c[je]): continue
        orh, orl = np.nanmax(h[j0:j0 + orbars]), np.nanmin(l[j0:j0 + orbars]); rng = orh - orl
        cl = c[j0 + orbars - 1]
        if rng <= 0 or rng / cl * 100 < min_pct: continue
        tp = (h + l + c) / 3
        cum = np.nancumsum(np.where(np.arange(1440) >= j0, np.nan_to_num(tp) * v, 0)); cv = np.cumsum(np.where(np.arange(1440) >= j0, v, 0))
        vw = np.where(cv > 0, cum / np.maximum(cv, 1), np.nan)
        lstp, sstp = orl - stop_mult * rng, orh + stop_mult * rng
        pos = 0; e = np.nan; x = np.nan; kind = ""; ej = -1
        for j in range(j0 + orbars, je + 2):
            if np.isnan(o[j]): continue
            if pos == 0:
                if j - 1 > jc: break
                vprev = vw[j - 1]
                lt, st = orl - through * TICK, orh + through * TICK
                if orl < vprev and l[j] <= lt: pos, e, ej = 1, min(o[j], orl), j
                elif orh > vprev and h[j] >= st: pos, e, ej = -1, max(o[j], orh), j
                continue
            if j - 1 >= je:                                           # 15:45 bar closed -> exit at this bar's open
                x, kind = o[j], "eod"; break
            tgt = vw[j - 1]
            if pos == 1:
                if l[j] <= lstp: x, kind = min(o[j], lstp), "stop"; break
                if h[j] >= tgt + through * TICK: x, kind = max(o[j], tgt), "tp"; break
            else:
                if h[j] >= sstp: x, kind = max(o[j], sstp), "stop"; break
                if l[j] <= tgt - through * TICK: x, kind = min(o[j], tgt), "tp"; break
        if pos == 0: continue
        if kind == "": x, kind = c[je + 1], "eod"
        gross = (x - e) * pos * PV
        slips = (1 if kind in ("stop", "eod") else 0) + (1 if slip_all else 0)
        rows.append(dict(date=d, side=pos, e=e, x=x, kind=kind, width=rng / cl * 100, gross=gross, net=gross - comm_rt - slips * TICK * PV))
    return pd.DataFrame(rows).set_index("date")


def tst(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pf(x): x = pd.Series(x); return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def line(T, nm, w=50):
    if len(T) < 5: return f"   {nm:<{w}} n={len(T)}"
    x = T.net; y = x.index.year; e = x.cumsum()
    a, b, p = x[(y >= 2020) & (y <= 2022)], x[y >= 2023], x[y < 2020]
    return (f"   {nm:<{w}} n={len(x):4d} ${x.mean():6.1f} PF {pf(x):4.2f} t {tst(x):4.1f} win {np.mean(x > 0):.0%} maxDD ${-(e - e.cummax()).min():>6,.0f} | "
            f"pre 18-19 ${p.mean() if len(p) else 0:6.1f} t {tst(p):4.1f} | IS 20-22 ${a.mean():6.1f} win {np.mean(a > 0):.0%} | OOS 23-26 ${b.mean():6.1f} win {np.mean(b > 0):.0%} t {tst(b):4.1f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    print("\n1. Which session start matches the author (2020-2026, their costs, touch fills; author: net ~$29.5k, PF ~1.30, win ~76%, "
          "IS $23.1 / OOS $49.9 a trade):")
    for s, nm in ((930, "SessStart 930 CT = 10:30 ET"), (830, "SessStart 830 CT = the 09:30 ET open")):
        T = run(sess=s, start="2020-01-01")
        print(f"   {nm:<30} net ${T.net.sum():>8,.0f}  PF {pf(T.net):.2f}  win {np.mean(T.net > 0):.1%}  trades {len(T)}  "
              f"IS ${T.net[T.index.year <= 2022].mean():.1f}  OOS ${T.net[T.index.year >= 2023].mean():.1f}")
    print("\n2. 2018-2026 (2018-19 = before the author's data):")
    T = run(); print(line(T, "930 CT, their costs, touch fills"))
    print(line(run(through=1), "930 CT, fills only 1 tick through"))
    print(line(run(comm_rt=5.0, slip_all=True), "930 CT, our costs ($5 + 1 tick a fill)"))
    print(line(run(comm_rt=5.0, slip_all=True, through=1), "930 CT, our costs + 1 tick through"))
    print(line(run(sess=830), "830 CT (true open), their costs"))
    print(line(run(min_pct=0), "930 CT, no width filter"))
    for mp in (0.10, 0.20, 0.25): print(line(run(min_pct=mp), f"930 CT, width >= {mp}%"))
    for ob in (5, 10, 15): print(line(run(orbars=ob), f"930 CT, OR {ob} bars"))
    for sm in (0.75, 2.0): print(line(run(stop_mult=sm), f"930 CT, stop {sm} x range"))
    for s in (900, 1000, 1030): print(line(run(sess=s), f"start {s} CT"))
    print("   by year (930, their costs):", T.net.groupby(T.index.year).sum().round(0).astype(int).to_dict())
    print("   exits:", T.kind.value_counts().to_dict(), "| longs", f"${T.net[T.side > 0].mean():.1f} ({(T.side > 0).sum()})",
          "shorts", f"${T.net[T.side < 0].mean():.1f} ({(T.side < 0).sum()})")
    print("   by width bucket ($ a trade / win):", {f"{a}-{b}%": (round(T.net[(T.width >= a) & (T.width < b)].mean(), 1), round((T.net[(T.width >= a) & (T.width < b)] > 0).mean(), 2), int(((T.width >= a) & (T.width < b)).sum()))
                                              for a, b in ((0.15, 0.2), (0.2, 0.3), (0.3, 0.5), (0.5, 9))})
    print("\n3. Metrics (930 CT, our costs + 1 tick through, per ES) and Monte Carlo at 1 MES:")
    Tq = run(comm_rt=5.0, slip_all=True, through=1)
    days = pd.DatetimeIndex(np.asarray(g.ts)[TR]); days = days[days >= "2018-01-01"]
    dd = Tq.net.groupby(Tq.index).sum().reindex(days, fill_value=0.0)
    print(M.table({"2018-26": (dd, Tq.net), "2023+": (dd[dd.index >= "2023-01-01"], Tq.net[Tq.index >= "2023-01-01"])}))
    print(MC.report(Tq.net.values, daily=dd.values, size=0.1, label="ORB VWAP fade 1 MES"))
    print(f"\n   variants run here: {NT['n']}; t threshold {M.t_threshold(NT['n']):.2f}")
