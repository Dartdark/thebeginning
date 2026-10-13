"""Overnight-range breakout with both-side stop entries ("Gold Breakout 15M Strategy", TradingView),
ported to NQ (2026-10-13).

Gold version: range = 00:00-07:00 broker time (GMT+3), buy stop at the range high and sell stop at the
range low (one cancels the other), 1 trade a day, stop 1% of entry (or the other side of the range), no
target, out at 20:00 broker time; risk 1% of equity. In Chicago time (summer) that is: range 17:00-23:00
CT (the Asia session), entries from 23:00, out at 12:00 CT, which fits inside one Apex day (17:00-15:59).

Versions (all CT; the range is built from the 17:00 CT reopen of the evening before):
  range end 23:00 (gold literal) / 2:00 (all of Asia) / 8:30 (whole overnight session)
  stop 1% / 0.5% of entry / the other side of the range / 0.3 x 15-day ATR
  exit 12:00 (gold literal) or 15:00
Entry: the first minute that trades through a boundary fills the stop order at the level (or the
open, if it gaps through) + 1 tick; if one minute touches both, the side nearer the minute's open.
Per NQ after $7.25 + 1 tick per market/stop fill, 2018-2026.
  python3 analysis/range_breakout_gold_test.py [SCRATCH_DIR]
"""
import sys, warnings, pickle, itertools; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25


def off(hhmm):
    """Minutes after 17:00 CT of the previous evening."""
    m = jof(hhmm)
    return m - jof(1700) if m >= jof(1700) else m + (1440 - jof(1700))


def run(g, r_end=2300, exit_t=1200, stop="pct1", rand=None):
    O, H, L, C = (getattr(g, a).ravel() for a in "ohlc")
    atr = g.daily_atr(15); ts = pd.DatetimeIndex(g.ts)
    rng = np.random.default_rng(rand) if rand is not None else None
    o_r1, o_x = off(r_end), off(exit_t)
    rows = []
    for d in g.trading:
        if ts[d].year < 2018 or d == 0 or np.isnan(atr[d]): continue
        s = (d - 1) * 1440 + jof(1700)
        seg_h, seg_l = H[s:s + o_r1], L[s:s + o_r1]
        if np.isnan(seg_h).all(): continue
        rh, rl = np.nanmax(seg_h), np.nanmin(seg_l)
        if not rh > rl: continue
        side = 0; t0 = None
        for t in range(s + o_r1, s + o_x):
            if np.isnan(H[t]): continue
            up, dn = H[t] >= rh, L[t] <= rl
            if up or dn:
                if up and dn: side = 1 if abs(O[t] - rh) < abs(O[t] - rl) else -1
                else: side = 1 if up else -1
                t0 = t; break
        if t0 is None: continue
        lvl = rh if side > 0 else rl
        e = (max(O[t0], lvl) if side > 0 else min(O[t0], lvl)) + side * TICK
        if rng is not None: side = int(rng.choice([-1, 1]))       # placebo: same time, random side
        if stop == "pct1": sp = e - side * 0.01 * e
        elif stop == "pct05": sp = e - side * 0.005 * e
        elif stop == "range": sp = rl if side > 0 else rh
        else: sp = e - side * 0.3 * atr[d]
        if (e - sp) * side <= 0: sp = e - side * 0.25 * atr[d]       # placebo flipped side: keep a stop
        px = None; t1 = s + o_x - 1
        for t in range(t0, s + o_x):
            if np.isnan(H[t]): continue
            if (L[t] <= sp) if side > 0 else (H[t] >= sp):
                px = ((min(O[t], sp) if side > 0 else max(O[t], sp)) if t > t0 else sp) - side * TICK; t1 = t; break
        if px is None:
            cc = C[t0:s + o_x]; ok = np.where(~np.isnan(cc))[0]
            t1 = t0 + ok[-1]; px = cc[ok[-1]] - side * TICK
        rows.append(dict(day=d, t0=t0, t1=t1, side=side, entry=e, exit=px, stop_pts=abs(e - sp),
                         net=(px - e) * side * PV - COST, date=ts[d]))
    return pd.DataFrame(rows)


def line(t, nm, w=40):
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); h = x[y >= 2023]
    pf = lambda q: q[q > 0].sum() / max(1e-9, -q[q < 0].sum())
    L_, S_ = x[t.side > 0], x[t.side < 0]
    return (f"{nm:<{w}} n={len(x):4d} win {np.mean(x > 0):.0%} avg ${x.mean():5.0f} PF {pf(x):.2f}"
            f" t={x.mean() / x.std() * np.sqrt(len(x)):4.1f} yrs+ {(by > 0).sum()}/{len(by)} | 23+ ${h.mean():5.0f} PF {pf(h):.2f}"
            f" | L ${L_.mean():4.0f} PF {pf(L_):.2f} S ${S_.mean():4.0f} PF {pf(S_):.2f}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    print(__doc__.split("\n")[0])
    print("\n1. Grid (range end x stop x exit), per NQ:")
    res, par = {}, {}
    for r_end, stop, ex in itertools.product((2300, 200, 830), ("pct1", "pct05", "range", "atr03"), (1200, 1500)):
        nm = f"range to {r_end:>4}, stop {stop:<5}, out {ex}"
        res[nm] = run(g, r_end, ex, stop); par[nm] = (r_end, ex, stop); print(line(res[nm], nm))
    lit = res["range to 2300, stop pct1 , out 1200"]
    print("\n2. Gold-literal version (range 17:00-23:00, stop 1%, out 12:00):")
    print("   by year:", lit.groupby(lit.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print(f"   entries by hour (CT): {(pd.Series(lit.t0 % 1440 // 60)).value_counts().sort_index().to_dict()}")
    pl = [run(g, 2300, 1200, "pct1", rand=r).net.mean() for r in range(20)]
    print(f"   placebo (same entry time, random side, 20 runs): ${np.mean(pl):.0f} ({min(pl):.0f}..{max(pl):.0f}) vs real ${lit.net.mean():.0f}")
    tt = {k: v.net.mean() / v.net.std() * np.sqrt(len(v)) for k, v in res.items()}
    best = max(tt, key=tt.get); b = res[best]
    print(f"\n3. Best of {len(res)} by t: {best}")
    print("   by year:", b.groupby(b.date.dt.year).net.sum().round(0).astype(int).to_dict())
    plb = [run(g, *par[best], rand=r).net.mean() for r in range(20)]
    print(f"   placebo: ${np.mean(plb):.0f} ({min(plb):.0f}..{max(plb):.0f}) vs real ${b.net.mean():.0f}")
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dl = lambda t: t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    print(M.table({"gold literal": (dl(lit), lit.net), f"best": (dl(b), b.net), "  best longs": (dl(b[b.side > 0]), b.net[b.side > 0]),
                   "  best shorts": (dl(b[b.side < 0]), b.net[b.side < 0])}))
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    dts2 = pd.DatetimeIndex(g.ts[lab.tr]); mk = dts2.year >= 2018
    for nm, t in (("gold literal", lit), ("best", b)):
        x = dl(t).reindex(dts2[mk], fill_value=0.0)
        cor = {k: round(float(np.corrcoef(x, pd.Series(lab.daily(k), index=dts2)[mk])[0, 1]), 2)
               for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC")}
        print(f"   correlation of '{nm}' with the plan: {cor}")
    # funded bench for the best (all its trades sit inside the day's calendar row)
    bb = b.copy(); bb["j0"] = bb.t0 - bb.day * 1440; bb["j1"] = bb.t1 - bb.day * 1440; bb["kind"] = 0; bb["slips"] = 0
    lab.add("RB", bb, slippage=False)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "VCS_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    for nm, p in (("current plan", plan), ("+ best breakout 1 MNQ", {**plan, "RB": 1}), ("+ best breakout 2 MNQ", {**plan, "RB": 2})):
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<24} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
