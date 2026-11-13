"""Edge hunt for the evaluation book: 7 pre-registered mechanisms (checks/candidates/edge_hunt_1113/PREREG.md, user 2026-11-13).
Gate discipline: design 2018-22 first; the 2023-26 holdout line of a rule is printed ONLY if it passes G1 (avg > 0, t >= 2.0).
Trades saved to checks/candidates/edge_hunt_1113/trades_<H>.csv (all years; the holdout rows are not summarised unless G1 passes).
  tools/run_stamped.sh analysis/edge_hunt_1113.py > analysis/outputs/edge_hunt_1113_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from replica import is_early_close
from candidates24 import _continuous_adx
print(__doc__.split("\n")[0])
g = pickle.load(open("scratch_data/g24.pkl", "rb")); ts = pd.DatetimeIndex(g.ts); atr = g.daily_atr(15)
O, Hh, Ll, C, Vv = (x.ravel() for x in (g.o, g.h, g.l, g.c, g.v)); N = len(O)
PV, TICK, COMM = 20.0, 0.25, 7.25
TR = [d for d in g.trading if ts[d].year >= 2017 and d >= 1 and np.isfinite(atr[d]) and not is_early_close(ts[d])]
rt = lambda x: round(x / TICK) * TICK
F = lambda d, hhmm: d * 1440 + jof(hhmm)                       # flat index of the minute bar CLOSING at hhmm on calendar row d


def first_ok(i0, i1):
    for i in range(i0, i1 + 1):
        if np.isfinite(O[i]): return i
    return None


def sim(i0, side, stop, tgt, i_end):
    """enter at the open of flat minute i0 (+1 tick), stop / target in points from the fill (tgt None = none), out at the close of i_end."""
    i0 = first_ok(i0, min(i0 + 5, i_end))
    if i0 is None or stop <= 0: return None
    e = O[i0] + side * TICK; ef = O[i0]; sp = ef - side * stop; tp = None if tgt is None else ef + side * tgt; last = ef
    for i in range(i0, i_end + 1):
        if not np.isfinite(Hh[i]): continue
        last = C[i]
        if (Ll[i] <= sp) if side > 0 else (Hh[i] >= sp):
            px = (min(O[i], sp) if side > 0 else max(O[i], sp)) if i > i0 else sp
            return (px - side * TICK - e) * side * PV - COMM, i, "stop"
        if tp is not None and ((Hh[i] >= tp) if side > 0 else (Ll[i] <= tp)):
            return (tp - e) * side * PV - COMM, i, "tgt"
    return (last - side * TICK - e) * side * PV - COMM, i_end, "time"


def run(setups, rng=None):
    rows = []
    for d, i0, side, stop, tgt, i_end in setups:
        s = side if rng is None else int(rng.choice([-1, 1]))
        r = sim(i0, s, stop, tgt, i_end)
        if r is not None: rows.append((ts[d], d, i0, r[1], s, r[0], r[2], stop))
    return pd.DataFrame(rows, columns=["date", "day", "i0", "i1", "side", "net", "why", "stop"])


def tt(x): x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan
def pf(x): return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
def stat(x, nm):
    return f"{nm} n {len(x):4d} avg ${x.mean():6.1f} t {tt(x):5.2f} PF {pf(x):.2f} win {np.mean(x > 0):.0%}" if len(x) > 4 else f"{nm} n {len(x)}"


# ---------------- setups
def slot_setups(slots, lookback=20, thr=2.0, stop_atr=0.15):
    """slots: list of functions d -> (flat start idx of the first minute, flat end idx) for trading day d."""
    out = []; hist = {k: [] for k in range(len(slots))}
    for d in TR:
        for k, fn in enumerate(slots):
            a, b_ = fn(d)
            if a < 0 or not (np.isfinite(O[a]) and np.isfinite(C[b_])): continue
            h = hist[k]
            if len(h) >= lookback:
                x = np.array(h[-lookback:]); sd = x.std(ddof=1)
                if sd > 0 and abs(x.mean() / sd * np.sqrt(lookback)) >= thr:
                    out.append((d, a, int(np.sign(x.mean())), rt(stop_atr * atr[d]), None, b_))
            h.append((C[b_] - O[a]) / atr[d])
    return out

RTH = [(lambda d, k=k: (F(d, 830) + 1 + 30 * k, F(d, 830) + 30 * (k + 1))) for k in range(13)]
ON = [(lambda d, k=k: (F(d - 1, 1700) + 1 + 60 * k, F(d - 1, 1700) + 60 * (k + 1))) for k in range(15)]   # 17:00 (previous calendar day) .. 08:00


def h2():
    out = []
    for d in TR:
        a, b_ = F(d - 1, 1700) + 1, F(d, 830)
        if not np.isfinite(Hh[a:b_ + 1]).any(): continue
        onh, onl = np.nanmax(Hh[a:b_ + 1]), np.nanmin(Ll[a:b_ + 1]); A = atr[d]; buf = 0.02 * A
        hi = -np.inf; lo = np.inf; tb = {1: None, -1: None}; done = False; i_end = F(d, 1430)
        for i in range(F(d, 831), F(d, 1300) + 1):
            if not np.isfinite(Hh[i]): continue
            hi = max(hi, Hh[i]); lo = min(lo, Ll[i])
            if tb[-1] is None and Hh[i] >= onh + buf: tb[-1] = i            # breach above -> short setup pending
            if tb[1] is None and Ll[i] <= onl - buf: tb[1] = i
            m = i % 1440
            if m % 5 == 0:                                                    # a 5-minute bar closes here
                for side, lvl in ((-1, onh), (1, onl)):
                    t0 = tb[side]
                    if t0 is None or t0 == "used" or i - t0 > 30: continue
                    if (C[i] < lvl) if side < 0 else (C[i] > lvl):
                        ext = hi if side < 0 else lo
                        stop = max(abs(ext - C[i]) + TICK, 0.05 * A)
                        out.append((d, i + 1, side, rt(stop), rt(2 * stop), i_end)); done = True; break
                if done: break
    return out


def h3(adx_lo=None, adx_hi=20.0):
    b = g.bars(15); A15 = _continuous_adx(b, 14); out = []
    for d in TR:
        ax = A15[d, 35]                                                       # the 15-min bar closing 08:45
        if not np.isfinite(ax) or (adx_hi is not None and not ax < adx_hi) or (adx_lo is not None and not ax > adx_lo): continue
        orh, orl = b["h"][d, 35], b["l"][d, 35]
        if not np.isfinite(orh) or orh <= orl: continue
        mid = (orh + orl) / 2
        for i in range(36, 45):                                               # 15-min closes 09:00 .. 11:00
            c = b["c"][d, i]
            if not np.isfinite(c): continue
            if c > orh or c < orl:
                side = -1 if c > orh else 1; tg = abs(c - mid)
                if tg >= 4 * TICK: out.append((d, d * 1440 + i * 15 + 1, side, rt(0.25 * atr[d]), rt(tg), F(d, 1430)))
                break
    return out


def h4(lo=1.5, hi=None):
    out = []; hist = []
    for d in TR:
        a, b_ = F(d, 830) + 1, F(d, 845); v = np.nansum(Vv[a:b_ + 1])
        if not (np.isfinite(O[a]) and np.isfinite(C[b_])) or v <= 0: continue
        if len(hist) >= 20:
            rv = v / np.mean(hist[-20:]); mv = C[b_] - O[a]
            if mv != 0 and (lo is None or rv >= lo) and (hi is None or rv < hi):
                out.append((d, b_ + 1, int(np.sign(mv)), rt(0.25 * atr[d]), None, F(d, 1430)))
        hist.append(v)
    return out


def h5():
    out = []
    for d in TR:
        a, b_ = F(d - 1, 1700) + 1, F(d, 100)
        if not np.isfinite(Hh[a:b_ + 1]).any(): continue
        ah, al = np.nanmax(Hh[a:b_ + 1]), np.nanmin(Ll[a:b_ + 1]); mid = (ah + al) / 2; A = atr[d]
        for i in range(F(d, 215), F(d, 700) + 1, 15):
            if not np.isfinite(C[i]): continue
            if C[i] > ah or C[i] < al:
                side = 1 if C[i] > ah else -1; stop = min(max(abs(C[i] - mid), 0.05 * A), 0.25 * A)
                out.append((d, i + 1, side, rt(stop), None, F(d, 825))); break
    return out


def h6():
    out = []; wk_open = {}
    for d in TR:
        key = (ts[d].isocalendar().year, ts[d].isocalendar().week)
        if key not in wk_open and np.isfinite(O[F(d, 830) + 1]): wk_open[key] = O[F(d, 830) + 1]
        if ts[d].dayofweek == 4 and key in wk_open and np.isfinite(C[F(d, 1300)]):
            w = C[F(d, 1300)] - wk_open[key]
            if abs(w) >= atr[d]: out.append((d, F(d, 1300) + 1, int(-np.sign(w)), rt(0.3 * atr[d]), None, F(d, 1455)))
    return out


HYP = [("H1a periodicity RTH", lambda: slot_setups(RTH)), ("H1b periodicity overnight", lambda: slot_setups(ON)), ("H2 overnight-extreme sweep", h2),
       ("H3 range-regime OR fade", h3), ("H4 opening relative volume", h4), ("H5 London break of Asia range", h5), ("H6 Friday de-risk fade", h6)]
passed = []
for nm, fn in HYP:
    S = fn(); T = run(S); T = T[T.date >= "2018-01-01"].reset_index(drop=True); tag = nm.split()[0]
    T.to_csv(f"checks/candidates/edge_hunt_1113/trades_{tag}.csv", index=False)
    de = T[T.date.dt.year <= 2022]; x = de.net
    by = " ".join(f"{k % 100:02d}:{v / 1000:+.1f}k" for k, v in x.groupby(de.date.dt.year).sum().items())
    print(f"\n== {nm}: {len(T)} trades 2018-26 ({len(T) / 8.85:.0f} a year), avg stop ${T.stop.mean() * PV:,.0f}")
    print(f"   DESIGN 2018-22: {stat(x, 'both')} | {stat(x[de.side > 0], 'longs')} | {stat(x[de.side < 0], 'shorts')}\n      {by}")
    g1 = len(x) > 30 and x.mean() > 0 and tt(x) >= 2.0
    print(f"   G1 (avg > 0, t >= 2.0): {'PASS' if g1 else 'FAIL -> holdout not opened'}")
    if g1:
        ho = T[T.date.dt.year >= 2023]; y = ho.net
        by = " ".join(f"{k % 100:02d}:{v / 1000:+.1f}k" for k, v in y.groupby(ho.date.dt.year).sum().items())
        print(f"   HOLDOUT 2023-26: {stat(y, 'both')} | {stat(y[ho.side > 0], 'longs')} | {stat(y[ho.side < 0], 'shorts')}\n      {by}")
        print(f"   whole sample: {stat(T.net, 'both')}; exits " + ", ".join(f"{k} {v}" for k, v in T.why.value_counts().items()))
        rng = np.random.default_rng(1); pl = np.array([(lambda P: P[P.date >= "2018-01-01"].net.mean())(run(S, rng)) for _ in range(200)])
        p = np.mean(pl >= T.net.mean()); g2 = y.mean() > 0 and tt(y) >= 1.5 and tt(T.net) >= 2.45
        print(f"   G2 (holdout avg > 0, t >= 1.5; whole t >= 2.45): {'PASS' if g2 else 'FAIL'} | G3 placebo: mean ${pl.mean():.1f}, p95 ${np.percentile(pl, 95):.1f}, p {p:.3f}: {'PASS' if p < 0.05 else 'FAIL'}")
        if g2 and p < 0.05: passed.append(nm)
print("\n== info (controls, design years only): H3 on ADX > 30 days:", stat((lambda T: T[(T.date >= '2018-01-01') & (T.date.dt.year <= 2022)].net)(run(h3(adx_lo=30.0, adx_hi=None))), ""),
      "| H4 with relative volume < 1:", stat((lambda T: T[(T.date >= '2018-01-01') & (T.date.dt.year <= 2022)].net)(run(h4(lo=None, hi=1.0))), ""))
print(f"\n== reached G4 (evaluation bench): {passed if passed else 'none'}")
