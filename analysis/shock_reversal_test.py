"""Shock Reversal (L. Franceschetti, 'ORB + Shock Reversal' research note 22.09.2026, uploaded 2026-10-24;
checks/candidates/shock_reversal/). The note withholds every threshold, so this is a pre-registered PROXY of the
described module, fixed before the first run (3 variants, no filters fitted):
  - 15-min NQ bars, RTH. Shock = the 30-min move into a signal bar closing 12:45, 13:00, 13:15, 13:30 or 13:45 CT
    (entries 13:00-14:00 CT = the note's 14:00-15:00 NY window), divided by the std of the same slot's 30-min move over
    the 60 prior full sessions. Variants: |z| >= 2.0 / 2.5 / 3.0.
  - Down shock and the bar closes above the RTH VWAP (08:30 onward) -> long; up shock and below VWAP -> short. First
    signal of the day only (one Shock trade a day). Entry at the next bar's open (market).
  - Exit: 8 bars, bounded by the RTH close; at these entry times that is always the 15:00 CT close (as the note says).
    No stop / target (theirs are not disclosed); the ADX / ATR filters are not disclosed and are left out.
Costs $7.25 + 1 tick per fill per NQ. Half days skipped. Controls: the opposite side on the same signals (follow), random
side (500 runs), the same entries without the VWAP condition.
  python3 analysis/shock_reversal_test.py SCRATCH_DIR
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import line
import metrics as M, resampling as R, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 20.0, 0.25, 7.25
SLOTS = (1245, 1300, 1315, 1330, 1345)


def last(a):
    f = np.flatnonzero(np.isfinite(a)); return a[f[-1]] if len(f) else np.nan


def sessions(g):
    rows = []
    for r in g.trading:
        if not np.isfinite(g.c[r, jof(1455):jof(1500) + 1]).any(): continue          # half day / no full session
        jj = np.arange(jof(831), jof(1500) + 1)
        c = g.c[r, jj]; h, l, v = g.h[r, jj], g.l[r, jj], np.nan_to_num(g.v[r, jj])
        tp = np.nan_to_num((h + l + c) / 3); cv = np.cumsum(v); vw = np.where(cv > 0, np.cumsum(tp * v) / np.maximum(cv, 1), np.nan)
        d = dict(r=r, date=pd.Timestamp(g.ts[r]), x=last(g.c[r, jof(1446):jof(1500) + 1]))
        for s in SLOTS:
            k = jof(s) - jof(831)
            d[f"c{s}"] = last(c[max(0, k - 14):k + 1]); d[f"p{s}"] = last(c[max(0, k - 44):k - 29])
            d[f"vw{s}"] = vw[k]; d[f"o{s}"] = g.o[r, jof(s) + 1]
        rows.append(d)
    S = pd.DataFrame(rows)
    for s in SLOTS:
        m = S[f"c{s}"] - S[f"p{s}"]; S[f"m{s}"] = m
        S[f"z{s}"] = m / m.rolling(60, min_periods=60).std().shift(1)
    return S


def trades(S, k, vwap=True, side_mult=1):
    out = []
    for x in S.itertuples():
        for s in SLOTS:
            z, c, vw, o = getattr(x, f"z{s}"), getattr(x, f"c{s}"), getattr(x, f"vw{s}"), getattr(x, f"o{s}")
            if not np.isfinite(z) or not np.isfinite(o) or not np.isfinite(x.x): continue
            side = 1 if (z <= -k and (not vwap or c > vw)) else -1 if (z >= k and (not vwap or c < vw)) else 0
            if side:
                side *= side_mult; e = o + side * TICK; px = x.x - side * TICK
                out.append(dict(date=x.date, slot=s, side=side, z=z, net=(px - e) * side * PV - COMM)); break
    return pd.DataFrame(out)


def stats(x, nm, days):
    p = M.perf(x.groupby(x.index).sum().reindex(days, fill_value=0.0), x.values)
    return (f"   {nm:<26} Sharpe {p['sharpe']:5.2f} Sortino {p['sortino']:5.2f} PF {p['profit_factor']:4.2f} "
            f"Calmar {p['calmar']:5.2f} Ulcer {p['ulcer']:5.2f} maxDD ${p['max_dd']:,.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    S = sessions(g); S = S[S.date >= "2018-01-01"].reset_index(drop=True); days = pd.DatetimeIndex(S.date)
    s_ = lambda t, m=None: (t.net if m is None else t.net[m]).set_axis(pd.DatetimeIndex(t.date if m is None else t.date[m]))
    print(f"sessions {len(S)}\n\nper NQ, 2018-2026, held to 15:00 CT:")
    T = {}
    for k in (2.0, 2.5, 3.0):
        t = trades(S, k); T[k] = t
        print(line(s_(t), f"z {k}: reversal (the module)", 40))
        print(line(s_(t, t.side > 0), f"   longs (down shock, above VWAP)", 40))
        print(line(s_(t, t.side < 0), f"   shorts (up shock, below VWAP)", 40))
        f = trades(S, k, side_mult=-1); print(line(s_(f), f"   control: follow the shock", 40))
        nv = trades(S, k, vwap=False); print(line(s_(nv), f"   control: reversal without VWAP", 40))
    rng = np.random.default_rng(20261024)
    print("\nrandom side on the same entries (500 runs):")
    for k, t in T.items():
        raw = (t.net + COMM) / t.side       # long-side gross per trade
        r = np.array([((raw * rng.choice([-1, 1], len(t))) - COMM).mean() for _ in range(500)])
        print(f"   z {k}: module ${t.net.mean():.1f} vs random p50 ${np.median(r):.1f}, beaten by {np.mean(r >= t.net.mean()):.1%}")
    print("\nby year (sum per NQ):")
    print(pd.DataFrame({f"z {k}": s_(t).groupby(lambda d: d.year).sum() for k, t in T.items()}).round(0).to_string())
    print("\nmetrics (daily, per NQ; whole / longs / shorts):")
    for k, t in T.items():
        for nm, m in (("all", None), ("longs", t.side > 0), ("shorts", t.side < 0)):
            print(stats(s_(t, m), f"z {k} {nm}", days))
    d23 = days[days >= "2023-01-01"]
    best = T[2.5]; x = s_(best, best.date >= "2023-01-01")
    print("\nresampling, z 2.5 (middle variant, fixed in advance) 2023+:"); print("\n".join(R.report({"z 2.5": x.groupby(x.index).sum().reindex(d23, fill_value=0.0)})))
    y = s_(best); print(MC.report(y.values, y.groupby(y.index).sum().reindex(days, fill_value=0.0), size=0.1, label="z 2.5, 1 MNQ"))
    for k, t in T.items():
        y = s_(t); print(f"   z {k}: DSR at 288 items {M.deflated_sharpe(y.groupby(y.index).sum().reindex(days, fill_value=0.0), 288):.2f}")
    for k, t in T.items(): t.to_csv(SP + f"shock_reversal_z{k}.csv", index=False)

    # controls added after the first run (2026-10-24): is it the shock or just the VWAP side? and their trade frequency
    print("\npost-hoc controls:")
    vw = pd.DataFrame([dict(date=x.date, side=(1 if x.c1245 > x.vw1245 else -1), o=x.o1245, x=x.x) for x in S.itertuples()
                       if np.isfinite(x.o1245) and np.isfinite(x.x) and np.isfinite(x.vw1245)])
    vw["net"] = (vw.x - vw.side * TICK - (vw.o + vw.side * TICK)) * vw.side * PV - COMM
    print(line(s_(vw), "every day: VWAP side at 12:45 -> 15:00", 40))
    print(line(s_(vw, vw.side > 0), "   above VWAP -> long", 40)); print(line(s_(vw, vw.side < 0), "   below VWAP -> short", 40))
    for k in (1.5, 1.75):
        t = trades(S, k); print(line(s_(t), f"z {k} reversal ({len(t) / 8.8:.0f} a year; theirs ~36-47)", 40))
