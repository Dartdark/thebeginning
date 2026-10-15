"""VWAP Pullback after an opening-range break (user's MultiCharts file VWAP_Pullback_NQ_Margin_Vol_1min_TF,
2026-10-13), replicated on 1-minute NQ.

Rules (CT): opening range = 1-minute bars 8:31-9:00; a later close above (below) it latches a long (short)
bias; VWAP of (H+L+C)/3 x volume from 8:31; RetestMode 1: low touches VWAP, then a close back above it ->
buy the next bar at market (shorts mirrored); stop = the last confirmed 20-bar swing low (StopMode 1) or
the pullback low (StopMode 2); target = the last confirmed 5-bar swing high, must be above the close;
entries 9:01-17:00; one trade a day; day reset 23:00. Exits: bracket only (the original, may hold
overnight) or the Apex version (entries until 15:00, flat at 15:55).
Per NQ after $7.25 + 1 tick per market / stop fill (target = limit, no slippage).
  python3 analysis/vwap_orb_pullback_test.py [SCRATCH_DIR]
"""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25


def series(g):
    flat = {c: getattr(g, c).ravel() for c in ("o", "h", "l", "c", "v")}
    idx = np.where(~np.isnan(flat["c"]))[0]
    s = {c: flat[c][idx] for c in flat}
    s["t"] = idx; s["row"] = idx // 1440; s["col"] = idx % 1440
    return s


def pivots(h, l, n):
    """Value of the last confirmed n-strength pivot high / low known at each bar (strict, as in the file)."""
    H, L = pd.Series(h), pd.Series(l)
    lmax = H.shift(1).rolling(n).max(); rmax = H[::-1].shift(1).rolling(n).max()[::-1]
    lmin = L.shift(1).rolling(n).min(); rmin = L[::-1].shift(1).rolling(n).min()[::-1]
    ph = (H > lmax) & (H > rmax); pl = (L < lmin) & (L < rmin)
    vh = pd.Series(np.where(ph, H, np.nan)).shift(n).ffill().to_numpy()      # confirmed n bars later
    vl = pd.Series(np.where(pl, L, np.nan)).shift(n).ffill().to_numpy()
    return vh, vl


def run(g, s, sh, sl, th, tl, apex=True, retest=1, stopmode=1, minrr=0.0, longs=True, shorts=True, rand=None, bias=None, exit_t=None,
        gate=None, end_entry=None, fsl=None, ftp=None):
    """gate: optional boolean per bar of the series (e.g. an ADX condition on the signal bar; it delays, the latches stay)."""
    O, H, L, C, V, row, col = s["o"], s["h"], s["l"], s["c"], s["v"], s["row"], s["col"]
    N = len(C); hhmm = (col // 60) * 100 + col % 60
    ts = pd.DatetimeIndex(g.ts); rng = np.random.default_rng(rand) if rand is not None else None
    end_entry = (1500 if apex else 1700) if end_entry is None else end_entry
    out = []; i = 0
    # walk day by day: a "day" starts at the 23:00 reset
    starts = np.where((hhmm > 2300) & (np.r_[True, hhmm[:-1] <= 2300]))[0]
    for a, b in zip(starts[:-1], starts[1:]):
        seg = np.arange(a, b)
        rs = seg[(hhmm[seg] > 830) & (hhmm[seg] <= 900)]
        if len(rs) < 10: continue
        d = row[rs[0]]
        if ts[d].year < 2018: continue
        orh, orl = H[rs].max(), L[rs].min()
        vw_idx = seg[(hhmm[seg] > 830) & (hhmm[seg] <= 1700)]
        tp = (H[vw_idx] + L[vw_idx] + C[vw_idx]) / 3; vv = np.maximum(V[vw_idx], 1)
        vwap = np.cumsum(tp * vv) / np.cumsum(vv)
        vmap = dict(zip(vw_idx, vwap))
        lb = sb = ltouch = stouch = lthru = sthru = False; pbl = pbh = None
        if bias is not None:                     # direction from another signal instead of the opening-range break
            bd = bias.get(int(d), 0)
            if bd == 0: continue
        entry = None
        for k in seg[seg > rs[-1]]:
            if hhmm[k] > 1700: break
            if bias is None:
                if C[k] > orh: lb = True
                if C[k] < orl: sb = True
            else:
                lb, sb = bd > 0, bd < 0
            if k not in vmap or not (900 < hhmm[k] <= end_entry): continue
            vw = vmap[k]
            lsig = ssig = False
            if lb:
                if retest == 1:
                    if L[k] <= vw: ltouch = True
                    lsig = ltouch and C[k] > vw
                else:
                    if C[k] < vw: lthru = True
                    lsig = lthru and C[k] > vw
            if sb:
                if retest == 1:
                    if H[k] >= vw: stouch = True
                    ssig = stouch and C[k] < vw
                else:
                    if C[k] > vw: sthru = True
                    ssig = sthru and C[k] < vw
            if ltouch or lthru: pbl = L[k] if pbl is None else min(pbl, L[k])
            if stouch or sthru: pbh = H[k] if pbh is None else max(pbh, H[k])
            if gate is not None and not gate[k]: lsig = ssig = False
            for side, sig in ((1, lsig and longs), (-1, ssig and shorts)):
                if not sig: continue
                stop = (sl[k] if stopmode == 1 else pbl) if side > 0 else (sh[k] if stopmode == 1 else pbh)
                tgt = th[k] if side > 0 else tl[k]
                if stop is None or np.isnan(stop) or np.isnan(tgt): continue
                if not ((stop < C[k] < tgt) if side > 0 else (tgt < C[k] < stop)): continue
                if minrr and abs(tgt - C[k]) / abs(C[k] - stop) < minrr: continue
                entry = (k, side, stop, tgt); break
            if entry: break
        if entry is None: continue
        k, side, stop, tgt = entry
        if rng is not None:                      # placebo: same entry bar, random side, mirrored distances
            ns = int(rng.choice([-1, 1]))
            if ns != side:
                ds, dt_ = abs(C[k] - stop), abs(tgt - C[k]); side = ns
                stop, tgt = C[k] - side * ds, C[k] + side * dt_
        j = k + 1
        if j >= N: continue
        e = O[j] + side * TICK; px = None; kind = 0
        if fsl is not None:                      # fixed exits (points, or per-day arrays) anchored to the entry price
            sl_ = fsl[row[k]] if hasattr(fsl, '__len__') else fsl; tp_ = ftp[row[k]] if hasattr(ftp, '__len__') else ftp
            stop, tgt = O[j] - side * sl_, O[j] + side * tp_
        while j < N:
            if (L[j] <= stop) if side > 0 else (H[j] >= stop):
                px = ((min(O[j], stop) if side > 0 else max(O[j], stop)) if j > k + 1 else stop) - side * TICK; break
            if (H[j] >= tgt) if side > 0 else (L[j] <= tgt):
                px = (max(O[j], tgt) if side > 0 else min(O[j], tgt)); kind = 1; break
            if (apex and 1555 <= hhmm[j] < 1700) or (exit_t is not None and hhmm[j] >= exit_t and hhmm[j] < 1700):
                px = C[j] - side * TICK; break
            j += 1
        if px is None: continue
        out.append(dict(day=row[k + 1], date=ts[row[k + 1]], side=side, entry=e, exit=px, kind=kind,
                        net=(px - e) * side * PV - COST, j0=col[k + 1], j1=col[j], t0=s["t"][k + 1], t1=s["t"][j],
                        overnight=row[j] != row[k + 1], slips=0))
    return pd.DataFrame(out)


def line(t, nm, w=48):
    if len(t) < 3: return f"{nm:<{w}} n={len(t)}"
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum()
    pf = lambda q: q[q > 0].sum() / max(1e-9, -q[q < 0].sum())
    a = x[y >= 2021]; h = x[y >= 2023]
    return (f"{nm:<{w}} n={len(x):4d} win {np.mean(x > 0):.0%} avg ${x.mean():5.0f} PF {pf(x):.2f}"
            f" t={x.mean() / x.std() * np.sqrt(len(x)):4.1f} yrs+ {(by > 0).sum()}/{len(by)} | 2021+ ${a.mean():5.0f} PF {pf(a):.2f}"
            f" win {np.mean(a > 0):.0%} | 23+ ${h.mean():5.0f} | L ${x[t.side > 0].mean():4.0f} S ${x[t.side < 0].mean():4.0f}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    s = series(g)
    sh, sl = pivots(s["h"], s["l"], 20); th, tl = pivots(s["h"], s["l"], 5)
    print(__doc__.split("\n")[0])
    orig = run(g, s, sh, sl, th, tl, apex=False)
    apx = run(g, s, sh, sl, th, tl, apex=True)
    print("\n1. As written (bracket only, entries to 17:00) and the Apex version (entries to 15:00, flat 15:55):")
    print(line(orig, "original"))
    print(f"   original: {orig.overnight.mean():.0%} of trades held past the day; target hit {np.mean(orig.kind == 1):.0%}")
    print(line(apx, "Apex version"))
    for nm, t in (("original", orig), ("Apex", apx)):
        print(f"   {nm} by year:", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print(line(apx[apx.side > 0], "  Apex longs")); print(line(apx[apx.side < 0], "  Apex shorts"))
    pl = [run(g, s, sh, sl, th, tl, apex=True, rand=r).net.mean() for r in range(10)]
    print(f"   placebo (same entry bars, random side, 10 runs): ${np.mean(pl):.0f} ({min(pl):.0f}..{max(pl):.0f}) vs ${apx.net.mean():.0f}")
    print("\n2. Variants (Apex version):")
    for nm, kw in (("RetestMode 2 (close through, reclaim)", dict(retest=2)), ("StopMode 2 (pullback extreme)", dict(stopmode=2)),
                   ("MinRR 1", dict(minrr=1.0)), ("MinRR 1.5", dict(minrr=1.5)), ("longs only", dict(shorts=False))):
        print(line(run(g, s, sh, sl, th, tl, apex=True, **kw), nm))
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dl = lambda t: t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    print("\n3. Standard metrics per NQ:")
    print(M.table({"original": (dl(orig), orig.net), "Apex version": (dl(apx), apx.net),
                   "Apex longs": (dl(apx[apx.side > 0]), apx.net[apx.side > 0]), "Apex shorts": (dl(apx[apx.side < 0]), apx.net[apx.side < 0])}))
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    a2 = apx[apx.j1 >= apx.j0].copy()
    lab.add("VWP", a2, slippage=False)
    dts2 = pd.DatetimeIndex(g.ts[lab.tr]); mk = dts2.year >= 2018
    P = {k: pd.Series(lab.daily(k), index=dts2)[mk] for k in ("VB", "ONB_ML2_MC", "LDF_MC", "VWP")}
    print("   correlation with the plan:", pd.DataFrame(P).corr().round(2).loc["VWP"].to_dict())
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "VCS_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    for nm, p in (("current plan", plan), ("+ VWAP pullback 1 MNQ", {**plan, "VWP": 1})):
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<24} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
