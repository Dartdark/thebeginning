"""Donchian breakout + Larry Williams Large Trade Index + volume filter (user's paste), 2026-10-13.

Rules as coded (bar size not given; 15-minute bars assumed: 96 bars = 24 hours; 5 / 30 also run), on the 24-hour
NQ series: long when the bar's high >= the 96-bar highest high (current bar included), LWTI > 50 and volume >
its 30-bar average; short mirrored (low <= 96-bar lowest low, LWTI < 50); one entry per calendar date, one position;
market entry at the next bar's open. EntryPrice = the signal bar's close. Exits as coded: at a bar close, if the
bar's high >= EntryPrice + 100 (long) -> sell at the next bar's open, else if its low <= EntryPrice - 50 -> sell
at the next open (shorts mirrored, 100 / 50). No time exit (holds overnight / for days).
LWTI (function not in the paste; common definition): 50 + 50 x SMA(close - close[25], 20) / ATR(25). Only its
side of 50 matters, i.e. the sign of the smoothed 25-bar momentum, so the scaling doesn't change the trades.
Apex version: signal bars 8:30-15:00 CT only, flat at the first bar after 15:00 CT.
Per NQ after $7.25 + 1 tick per market fill.
  python3 analysis/donchian_lwti_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25


def series(g, k):
    b = g.bars(k); D, n = b["c"].shape
    flat = {c: b[c].ravel() for c in ("o", "h", "l", "c", "v")}
    idx = np.flatnonzero(~np.isnan(flat["c"]))
    s = {c: flat[c][idx] for c in flat}
    s["row"] = idx // n; s["j"] = (idx % n) * k; s["hhmm"] = (s["j"] // 60) * 100 + s["j"] % 60
    return s


def indicators(s, don=96, lw_len=25, lw_sm=20, vol_len=30):
    H, L, C, V = (pd.Series(s[c]) for c in ("h", "l", "c", "v"))
    up, dn = H.rolling(don).max(), L.rolling(don).min()
    tr = pd.concat([H - L, (H - C.shift()).abs(), (L - C.shift()).abs()], axis=1).max(axis=1)
    lw = 50 + 50 * (C - C.shift(lw_len)).rolling(lw_sm).mean() / tr.rolling(lw_len).mean()
    av = V.rolling(vol_len).mean()
    return up.to_numpy(), dn.to_numpy(), lw.to_numpy(), av.to_numpy()


def run(g, s, ind, tp_l=100, sl_l=50, tp_s=100, sl_s=50, apex=False, use_lw=True, use_vol=True, longs=True, shorts=True,
        rand=None, start=830, end=1500):
    up, dn, lw, av = ind
    O, H, L, C, V, row, hm = s["o"], s["h"], s["l"], s["c"], s["v"], s["row"], s["hhmm"]
    ts = pd.DatetimeIndex(g.ts); rng = np.random.default_rng(rand) if rand is not None else None
    n = len(C); out = []; pos = None; pend = 0; xpend = False; traded_date = -1; tset = set(g.trading)
    for i in range(1, n):
        # fills at this bar's open
        if pend:
            e = O[i] + pend * TICK; pos = dict(side=pend, e=e, ep=pend_ep, i0=i, row0=row[i]); pend = 0
        elif pos is not None and xpend:
            px = O[i] - pos["side"] * TICK
            out.append(dict(day=pos["row0"], date=ts[pos["row0"]], side=pos["side"], entry=pos["e"], exit=px, kind=2, slips=0,
                            j0=0, j1=0, i0=pos["i0"], i1=i, overnight=row[i] != pos["row0"],
                            net=(px - pos["e"]) * pos["side"] * PV - COST)); pos = None; xpend = False
        # bar close
        if pos is not None:
            s_ = pos["side"]
            if s_ > 0:
                if H[i] >= pos["ep"] + tp_l or L[i] <= pos["ep"] - sl_l: xpend = True
            else:
                if L[i] <= pos["ep"] - tp_s or H[i] >= pos["ep"] + sl_s: xpend = True
            if apex and (hm[i] >= end or (i + 1 < n and row[i + 1] != row[i])): xpend = True
            continue
        if row[i] == traded_date or np.isnan(lw[i]) or np.isnan(av[i]) or ts[row[i]].year < 2018: continue
        if apex and not (start < hm[i] <= end and row[i] in tset): continue
        vol_ok = (V[i] > av[i]) if use_vol else True
        side = 0
        if longs and H[i] >= up[i] and (lw[i] > 50 or not use_lw) and vol_ok: side = 1
        elif shorts and L[i] <= dn[i] and (lw[i] < 50 or not use_lw) and vol_ok: side = -1
        if side:
            if apex and hm[i] >= end: continue
            if rng is not None: side = int(rng.choice([-1, 1]))
            pend = side; pend_ep = C[i]; traded_date = row[i]
    return pd.DataFrame(out)


def line(t, nm, w=40):
    if len(t) < 3: return f"{nm:<{w}} n={len(t)}"
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum()
    pf = lambda q: q[q > 0].sum() / max(1e-9, -q[q < 0].sum())
    a, b = x[y < 2023], x[y >= 2023]
    return (f"{nm:<{w}} n={len(x):5d} win {np.mean(x > 0):.0%} avg ${x.mean():5.0f} PF {pf(x):.2f} t={x.mean() / x.std() * np.sqrt(len(x)):4.1f}"
            f" yrs+ {(by > 0).sum()}/{len(by)} | 18-22 ${a.mean():4.0f} | 23-26 ${b.mean():4.0f} | L ${x[t.side > 0].mean():4.0f} S ${x[t.side < 0].mean():4.0f}"
            f" | overnight {t.overnight.mean():.0%}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    print(__doc__.split("\n")[0])
    S = {k: series(g, k) for k in (5, 15, 30)}; I = {k: indicators(S[k]) for k in S}
    print("\n1. As coded (24 h, no time exit, one entry a day):")
    asis = {k: run(g, S[k], I[k]) for k in S}
    for k, t in asis.items(): print(line(t, f"{k}-min bars"))
    t15 = asis[15]
    print("   15-min by year:", t15.groupby(t15.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print(f"   15-min: worst trade ${t15.net.min():,.0f}; exit fill beyond the 50-pt stop level: "
          f"{np.mean(t15.net < -(50 * PV + COST + 2 * TICK * PV)):.0%} of trades")

    print("\n2. Apex version (signals 8:30-15:00 CT, flat after 15:00):")
    apx = {k: run(g, S[k], I[k], apex=True) for k in S}
    for k, t in apx.items(): print(line(t, f"{k}-min bars"))
    a15 = apx[15]
    print("   15-min by year:", a15.groupby(a15.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print(line(a15[a15.side > 0], "  15-min longs")); print(line(a15[a15.side < 0], "  15-min shorts"))
    pl = [run(g, S[15], I[15], apex=True, rand=r).net.mean() for r in range(10)]
    print(f"   placebo (same entry bars, random side, 10 runs): ${np.mean(pl):.0f} ({min(pl):.0f}..{max(pl):.0f}) vs ${a15.net.mean():.0f}")
    for nm, kw in (("no LWTI filter", dict(use_lw=False)), ("no volume filter", dict(use_vol=False)), ("neither filter", dict(use_lw=False, use_vol=False)),
                   ("TP 50 / SL 50", dict(tp_l=50, tp_s=50)), ("TP 150 / SL 75", dict(tp_l=150, sl_l=75, tp_s=150, sl_s=75))):
        print(line(run(g, S[15], I[15], apex=True, **kw), f"15-min Apex, {nm}"))

    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dl = lambda t: t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    print("\n3. Standard metrics per NQ (15-min):")
    rows = {"as coded": (dl(t15), t15.net), "Apex": (dl(a15), a15.net), "Apex longs": (dl(a15[a15.side > 0]), a15.net[a15.side > 0]),
            "Apex shorts": (dl(a15[a15.side < 0]), a15.net[a15.side < 0])}
    print(M.table(rows))
    bt, pm = R.report({f"{k} 2023+": v[0][v[0].index >= "2023-01-01"] for k, v in rows.items()}, n=2000); print(bt); print(pm)
