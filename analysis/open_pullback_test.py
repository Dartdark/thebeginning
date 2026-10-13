"""Open-breakout pullback (user's idea, 2026-10-13): after a breakout from the 8:30 CT open, price pulls back to the
open and continues. Exits / sizing designed here. NQ, 5-minute signal bars, fills on 1-minute bars.

  Breakout   price trades >= open x (1 + X%) (long) or <= open x (1 - X%) (short) before 10:30 CT; the first side
             to break sets the day's direction. X = 0.15 / 0.25 / 0.35 / 0.50 / 0.75%.
  Entry A    (the user's): a 5-min bar after the breakout that touches the open (low <= open for longs) and closes
             back on the breakout side -> market at the next bar's open; stop 1 tick past that bar's low / high.
  Entry B    a limit order at the open once the breakout has happened (fills at the open or better); stop =
             0.20 x the 15-day ATR from the open.
             Entries until 12:00 CT; one trade a day.
  Target     1 / 1.5 / 2 / 3 R, the breakout extreme (highest high / lowest low before entry), or none; all trades
             out at the close of the 14:55 CT bar.
Design 2018-2022, holdout 2023-2026. Per NQ after $7.25 + 1 tick per market / stop fill (limits: none).
  python3 analysis/open_pullback_test.py [SCRATCH_DIR]
"""
import sys, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25
SPLIT = pd.Timestamp("2023-01-01")
XS = (0.15, 0.25, 0.35, 0.50, 0.75)
TGTS = (1.0, 1.5, 2.0, 3.0, "ext", None)


def day_trade(g, d, atr_d, x, entry, tgt, sides):
    O, H, L, C = g.o[d], g.h[d], g.l[d], g.c[d]
    op = O[jof(831)]
    if np.isnan(op) or np.isnan(atr_d): return None
    up, dn = op * (1 + x / 100), op * (1 - x / 100)
    side = 0; jb = None
    for j in range(jof(831), jof(1030) + 1):
        if np.isnan(H[j]): continue
        hu, hd = H[j] >= up, L[j] <= dn
        if hu or hd:
            side = 1 if (hu and not hd) else (-1 if (hd and not hu) else (1 if abs(O[j] - up) < abs(O[j] - dn) else -1))
            jb = j; break
    if side == 0 or side not in sides: return None
    # entry search
    ext = np.nanmax(H[jof(831):jb + 1]) if side > 0 else np.nanmin(L[jof(831):jb + 1])
    j0 = e = stop = None
    if entry == "A":
        first5 = ((jb // 5) + 1) * 5                 # first 5-min bar closing after the breakout minute's bar
        for jc in range(first5, jof(1200) + 1, 5):
            seg = slice(jc - 4, jc + 1)
            if np.isnan(C[seg]).all(): continue
            hi, lo = np.nanmax(H[seg]), np.nanmin(L[seg]); cl = C[seg][~np.isnan(C[seg])][-1]
            if side > 0 and lo <= op and cl > op:
                e = O[jc + 1] + TICK if not np.isnan(O[jc + 1]) else None; stop = lo - TICK; j0 = jc + 1
            elif side < 0 and hi >= op and cl < op:
                e = O[jc + 1] - TICK if not np.isnan(O[jc + 1]) else None; stop = hi + TICK; j0 = jc + 1
            if e is None and j0 is not None: return None
            if e is not None: break
            ext = max(ext, hi) if side > 0 else min(ext, lo)
        if e is None or (side > 0 and stop >= e) or (side < 0 and stop <= e): return None
    else:
        for j in range(jb + 1, jof(1200) + 1):
            if np.isnan(L[j]): continue
            if (side > 0 and L[j] <= op) or (side < 0 and H[j] >= op):
                e = min(O[j], op) if side > 0 else max(O[j], op); j0 = j; stop = op - side * 0.20 * atr_d; break
            ext = max(ext, H[j]) if side > 0 else min(ext, L[j])
        if e is None: return None
    risk = abs(e - stop)
    if tgt == "ext": tp = ext if (ext - e) * side > 0 else None
    elif tgt is None: tp = None
    else: tp = e + side * tgt * risk
    if tgt == "ext" and tp is None: return None
    jx = jof(1455); px = None; kind = 2
    for j in range(j0, jx + 1):
        if np.isnan(H[j]): continue
        if (L[j] <= stop) if side > 0 else (H[j] >= stop):
            px = ((min(O[j], stop) if side > 0 else max(O[j], stop)) if j > j0 else stop) - side * TICK; kind = 0; break
        if tp is not None and ((H[j] >= tp) if side > 0 else (L[j] <= tp)):
            px = (max(O[j], tp) if side > 0 else min(O[j], tp)) if j > j0 else tp; kind = 1; break
    if px is None:
        cc = C[j0:jx + 1]; ok = np.flatnonzero(~np.isnan(cc)); px = cc[ok[-1]] - side * TICK; j = j0 + ok[-1]
    return dict(day=d, side=side, j0=j0, j1=j, entry=e, exit=px, kind=kind, slips=0, risk=risk,
                net=(px - e) * side * PV - COST)


def run(g, x, entry, tgt, sides=(1, -1)):
    ts = pd.DatetimeIndex(g.ts); atr = g.daily_atr(15); out = []
    for d in g.trading:
        if ts[d].year < 2018: continue
        r = day_trade(g, d, atr[d], x, entry, tgt, sides)
        if r is None: continue
        r["date"] = ts[d]; out.append(r)
    return pd.DataFrame(out)


def stats(t):
    if len(t) < 10: return dict(n=len(t), avg=np.nan, pf=np.nan, t=np.nan, d=np.nan, h=np.nan, yrs=np.nan)
    x = t.net; y = t.date.dt.year
    pf = lambda q: q[q > 0].sum() / max(1e-9, -q[q < 0].sum())
    by = x.groupby(y).sum()
    return dict(n=len(x), avg=x.mean(), pf=pf(x), t=x.mean() / x.std() * np.sqrt(len(x)), d=x[y < 2023].mean(),
                h=x[y >= 2023].mean(), pfd=pf(x[y < 2023]), pfh=pf(x[y >= 2023]), yrs=f"{(by > 0).sum()}/{len(by)}",
                win=np.mean(x > 0))


def line(t, nm, w=50):
    s = stats(t)
    if s["n"] < 10: return f"{nm:<{w}} n={s['n']}"
    return (f"{nm:<{w}} n={s['n']:4d} win {s['win']:.0%} avg ${s['avg']:5.0f} PF {s['pf']:.2f} t={s['t']:4.1f} yrs+ {s['yrs']}"
            f" | 18-22 ${s['d']:4.0f} PF {s['pfd']:.2f} | 23-26 ${s['h']:4.0f} PF {s['pfh']:.2f}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    print(__doc__.split("\n")[0])
    rows = []; T = {}
    for side, x, entry, tgt in itertools.product((1, -1), XS, ("A", "B"), TGTS):
        t = run(g, x, entry, tgt, sides=(side,)); T[(side, x, entry, tgt)] = t
        s = stats(t); rows.append(dict(side="long" if side > 0 else "short", x=x, entry=entry, tgt=str(tgt), **{k: s[k] for k in ("n", "avg", "pf", "t", "d", "h", "yrs")}))
    G = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    for sd in ("long", "short"):
        q = G[G.side == sd].copy()
        print(f"\n1. {sd.upper()}S: all {len(q)} combinations (design 2018-22 avg 'd', holdout 2023-26 avg 'h'), sorted by design avg:")
        print(q.sort_values("d", ascending=False).to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
        print(f"   {sd}s: combinations with design avg > 0: {np.mean(q.d > 0):.0%}; of those, holdout avg > 0: {np.mean(q[q.d > 0].h > 0):.0%}")
    pickle.dump(dict(G=G, T=T), open(SP + "open_pullback.pkl", "wb"))

    print("\n2. The best region (longs, 0.50% breakout, limit at the open = entry B) vs controls:")
    from bridge_monday_confirm import load_bridge_mc
    atr = g.daily_atr(15); ts = pd.DatetimeIndex(g.ts)
    for tgt in (1.5, 2.0, 3.0, "ext"):
        print(line(T[(1, 0.50, "B", tgt)], f"long 0.50% B target {tgt}"))
    best = T[(1, 0.50, "B", 2.0)]
    print(line(T[(1, 0.15, "B", 2.0)], "control: the same rule after only a 0.15% breakout"))
    # mirrored placebo: short at the same fills, same stop / target distances
    pl = []
    for r in best.itertuples():
        d = int(r.day); e = r.entry; risk = r.risk; stop, tp = e + risk, e - 2 * risk
        O, H, L, C = g.o[d], g.h[d], g.l[d], g.c[d]; px = None
        for j in range(int(r.j0), jof(1455) + 1):
            if np.isnan(H[j]): continue
            if H[j] >= stop: px = (max(O[j], stop) if j > r.j0 else stop) + TICK; break
            if L[j] <= tp: px = min(O[j], tp) if j > r.j0 else tp; break
        if px is None:
            cc = C[int(r.j0):jof(1455) + 1]; px = cc[~np.isnan(cc)][-1] + TICK
        pl.append(dict(date=r.date, side=-1, net=(e - px) * PV - COST))
    print(line(pd.DataFrame(pl), "placebo: SHORT at the same fills, mirrored 2R"))
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    long_all = []
    for d in g.trading:
        if ts[d].year < 2018: continue
        o, c = g.o[d, jof(831)], g.c[d, jof(1455)]
        if not (np.isnan(o) or np.isnan(c)): long_all.append(dict(date=ts[d], side=1, net=(c - o - 2 * TICK) * PV - COST))
    print(line(pd.DataFrame(long_all), "control: long every day 8:30 open -> 14:55"))
    dl = lambda t: t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    print("\n3. Standard metrics per NQ (long 0.50% B 2R):")
    print(M.table({"long 0.50 B 2R": (dl(best), best.net)}))
    bt, pm = R.report({"2023+": dl(best)[dl(best).index >= "2023-01-01"]}, n=3000); print(bt); print(pm)
    print("\n4. Funded bench (8-strategy plan; + this at RiskPerTrade, stop = 0.20 ATR):")
    lab = pickle.load(open(SP + "lab.pkl", "rb")); lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    lab.add("OPB", best, stop_pts=0.20 * atr, slippage=False)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500),
            "VCS_MC": 1, "MON_BR_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    for nm, p in (("current plan", plan), ("+ open pullback $200", {**plan, "OPB": ("risk", 200)}), ("+ open pullback $400", {**plan, "OPB": ("risk", 400)})):
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<26} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
