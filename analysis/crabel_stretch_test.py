"""Crabel Stretch Breakout (user's MultiCharts file Crabel_Stretch_Breakout_NQ_v3, 2026-10-13), replicated on NQ.

Rules (CT; the file uses ET): open = 8:30 open; stretch = 10-day average of min(high - open, open - low) of
the 8:30-15:00 session; buy stop at open + 1.4 x stretch, sell stop at open - 1.4 x stretch, from the
8:31 bar until 9:30 (10:30 ET); first side hit = the trade; stop 0.7 x stretch from the fill; out at the
14:56 open (15:55 ET + 1 bar); one entry a day. Setup modes: every day / NR7 / inside day / both;
trend filter: 20-day SMA of cash closes. The author optimized on 2018-2023 and holds out 2024-2026.
Per NQ after $7.25 + 1 tick per market/stop fill.
  python3 analysis/crabel_stretch_test.py [SCRATCH_DIR]
"""
import sys, warnings, pickle, itertools; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25


def day_stats(g):
    tr = g.trading; a, b = 511, jof(1500)
    O = g.o[tr, a]
    with np.errstate(all="ignore"):
        H = np.nanmax(g.h[tr, a:b + 1], 1); L = np.nanmin(g.l[tr, a:b + 1], 1)
    C = pd.Series(g.c[tr, b]).ffill().to_numpy()
    full = ~np.isnan(g.c[tr, b])                      # days that reach 15:00 (early closes are not stored)
    return tr, O, H, L, C, full


def run(g, mult=1.4, stop=0.7, n=10, end=930, setup=0, trend=0, longs=True, shorts=True, rand=None):
    tr, O, H, L, C, full = day_stats(g)
    ts = pd.DatetimeIndex(g.ts); rng = np.random.default_rng(rand) if rand is not None else None
    st = np.minimum(H - O, O - L)
    ok = full & ~np.isnan(st)
    idx = np.where(ok)[0]
    rows = []
    hist_s, hist_r, hist_c, prev_hl = [], [], [], None
    stored = {}                                       # for each trading day: (avg stretch, NR, inside, up, dn) known before it
    for k in range(len(tr)):
        if len(hist_s) >= n:
            avg = np.mean(hist_s[-n:]); nr = len(hist_r) >= 7 and hist_r[-1] < min(hist_r[-7:-1])
            ins = prev_hl is not None and prev_hl[2]
            sma = np.mean(hist_c[-20:]) if len(hist_c) >= 20 else np.nan
            stored[k] = (avg, nr, ins, hist_c[-1] > sma if not np.isnan(sma) else False,
                         hist_c[-1] < sma if not np.isnan(sma) else False)
        if ok[k]:
            hist_s.append(st[k]); hist_r.append(H[k] - L[k]); hist_c.append(C[k])
            inside = prev_hl is not None and H[k] <= prev_hl[0] and L[k] >= prev_hl[1]
            prev_hl = (H[k], L[k], inside)
    for k, (avg, nr, ins, up, dn) in stored.items():
        d = tr[k]
        if ts[d].year < 2018 or np.isnan(O[k]) or avg <= 0: continue
        if setup == 1 and not nr: continue
        if setup == 2 and not ins: continue
        if setup == 3 and not (nr and ins): continue
        lo_ok, sh_ok = longs, shorts
        if trend == 1: lo_ok &= up; sh_ok &= dn
        if trend == 2: lo_ok &= up
        up_l, dn_l = O[k] + mult * avg, O[k] - mult * avg
        side = 0; j0 = None
        for j in range(512, jof(end) + 1):
            h, l, o = g.h[d, j], g.l[d, j], g.o[d, j]
            if np.isnan(h): continue
            hu, hd = lo_ok and h >= up_l, sh_ok and l <= dn_l
            if hu or hd:
                side = (1 if abs(o - up_l) <= abs(o - dn_l) else -1) if (hu and hd) else (1 if hu else -1)
                j0 = j; break
        if j0 is None: continue
        lvl = up_l if side > 0 else dn_l
        e = (max(g.o[d, j0], lvl) if side > 0 else min(g.o[d, j0], lvl)) + side * TICK
        if rng is not None: side = int(rng.choice([-1, 1]))
        sp = e - side * stop * avg
        px = None; j1 = jof(1456)
        for j in range(j0, jof(1456)):
            h, l, o = g.h[d, j], g.l[d, j], g.o[d, j]
            if np.isnan(h): continue
            if (l <= sp) if side > 0 else (h >= sp):
                px = ((min(o, sp) if side > 0 else max(o, sp)) if j > j0 else sp) - side * TICK; j1 = j; break
        if px is None:
            ox = g.o[d, jof(1456)]
            if np.isnan(ox):
                cc = g.c[d, j0:jof(1456)]; okc = np.where(~np.isnan(cc))[0]; ox = cc[okc[-1]]; j1 = j0 + okc[-1]
            px = ox - side * TICK
        rows.append(dict(day=d, j0=j0, j1=j1, side=side, entry=e, exit=px, kind=0, slips=0,
                         net=(px - e) * side * PV - COST, date=ts[d]))
    return pd.DataFrame(rows)


def line(t, nm, w=46):
    if len(t) < 2: return f"{nm:<{w}} n={len(t)}"
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum()
    pf = lambda q: q[q > 0].sum() / max(1e-9, -q[q < 0].sum())
    a, b = x[y <= 2023], x[y >= 2024]
    L_, S_ = x[t.side > 0], x[t.side < 0]
    return (f"{nm:<{w}} n={len(x):4d} win {np.mean(x > 0):.0%} avg ${x.mean():5.0f} PF {pf(x):.2f}"
            f" t={x.mean() / x.std() * np.sqrt(len(x)):4.1f} yrs+ {(by > 0).sum()}/{len(by)} | 18-23 ${a.mean():5.0f} PF {pf(a):.2f}"
            f" | 24-26 ${b.mean():5.0f} PF {pf(b):.2f} | L ${L_.mean():4.0f} S ${S_.mean():4.0f}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    print(__doc__.split("\n")[0])
    base = run(g)
    print("\n1. Defaults (every day, 1.4x entry, 0.7x stop, entries to 9:30 CT, no trend filter):")
    print(line(base, "defaults"))
    print("   by year:", base.groupby(base.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print(line(base[base.side > 0], "  longs")); print(line(base[base.side < 0], "  shorts"))
    pl = [run(g, rand=r).net.mean() for r in range(20)]
    print(f"   placebo (same entry time, random side, 20 runs): ${np.mean(pl):.0f} ({min(pl):.0f}..{max(pl):.0f}) vs ${base.net.mean():.0f}")
    print("\n2. Neighbours (design 2018-23 vs holdout 2024-26):")
    res = {}
    for mult, stop, end in itertools.product((1.0, 1.2, 1.4, 1.6, 1.8), (0.5, 0.7, 1.0), (930, 1030)):
        res[(mult, stop, end)] = run(g, mult, stop, end=end)
        print(line(res[(mult, stop, end)], f"entry {mult}x stop {stop}x until {end}"))
    print("\n3. Setup and trend modes (defaults otherwise):")
    for s_, nm in ((1, "NR7"), (2, "inside day"), (3, "NR7 + inside")):
        print(line(run(g, setup=s_), nm))
    for tm, nm in ((1, "trend filter both sides"), (2, "trend filter longs only")):
        print(line(run(g, trend=tm), nm))
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dl = lambda t: t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    print("\n4. Standard metrics per NQ, defaults:")
    h = base[base.date.dt.year >= 2024]; D2 = days[days.year >= 2024]
    print(M.table({"2018-26": (dl(base), base.net), "longs": (dl(base[base.side > 0]), base.net[base.side > 0]),
                   "shorts": (dl(base[base.side < 0]), base.net[base.side < 0]),
                   "holdout 2024-26": (dl(h).reindex(D2, fill_value=0.0), h.net)}))
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    lab.add("CRB", base, slippage=False)
    dts2 = pd.DatetimeIndex(g.ts[lab.tr]); mk = dts2.year >= 2018
    P = {k: pd.Series(lab.daily(k), index=dts2)[mk] for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC", "VCS_MC", "CRB")}
    print("   correlation with the plan:", pd.DataFrame(P).corr().round(2).loc["CRB"].to_dict())
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "VCS_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    for nm, p in (("current plan", plan), ("+ Crabel 1 MNQ", {**plan, "CRB": 1}), ("+ Crabel 2 MNQ", {**plan, "CRB": 2})):
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<18} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")

    print("\n5. Combine (VB 8 MNQ + ONB ADX30 $1,100 [+ Crabel], 21 days, every start day, with slippage):")
    from portfolio import load_mc, paths, challenge
    from funded_lab import with_slippage
    tr = g.trading; D = len(tr); yr = pd.DatetimeIndex(g.ts[tr]).year; atr = g.daily_atr(15)
    vb = load_mc(g, "Backtesting Strategy Performance Report VB v1.xlsx"); w, r = paths(g, with_slippage(vb)); VBw, VBc = w[tr] / 10, r[tr] / 10
    on = load_mc(g, "Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx")
    w, r = paths(g, with_slippage(on)); Ow, Oc = w[tr] / 10, r[tr] / 10
    q = np.floor(1100 / (0.25 * np.nan_to_num(atr[tr], nan=1e12) * 2))[:, None]
    w, r = paths(g, base); Cw, Cc = w[tr] / 10, r[tr] / 10
    for nm, k in (("VB 8 + ONB", 0), ("+ Crabel 2 MNQ", 2), ("+ Crabel 4 MNQ", 4), ("Crabel 8 MNQ instead of VB", -8)):
        if k >= 0: W, Rr = VBw * 8 + Ow * q + Cw * k, VBc * 8 + Oc * q + Cc * k
        else: W, Rr = Ow * q + Cw * 8, Oc * q + Cc * 8
        res = [challenge(W, Rr, np.arange(s, min(s + 21, D))) for s in range(D)]
        o = np.array([np.nan if x is None else float(x[0] == "pass") for x in res])
        print(f"   {nm:<28} pass {np.nanmean(o[yr >= 2018]):.1%} | 2023-26 {np.nanmean(o[yr >= 2023]):.1%}")
