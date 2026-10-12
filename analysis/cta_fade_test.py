"""Follow-up to cta_volcontrol_test.py (2026-10-12): the day after a CTA signal flip reverses.
Checks: (1) flip direction, by year, trade with a stop; (2) is it just big-move reversal? matched
non-flip days with the same move size; (3) placebo: 200 random lookback sets (4 lookbacks in
15-300 days, none within 3 days of 21/63/126/252); (4) fade the trigger touch intraday;
(5) vol-control V2 by flow sign. Per NQ after $7.25 + 1 tick per market/stop fill.
  python3 analysis/cta_fade_test.py [SCRATCH_DIR]
"""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from news_meanrev_test import row, summ
from cta_volcontrol_test import rep, vc_exposure, CTA_N, PV

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"


def signals(cl, Ns):
    S = np.full((len(Ns), len(cl)), np.nan)
    for i, n in enumerate(Ns): S[i, n:] = np.sign(cl[n:] - cl[:-n])
    return S


def flip_dir(S):
    return np.r_[0, np.nansum(S[:, 1:] - S[:, :-1], 0)] / 2       # + = signals flipped up today


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); es = pickle.load(open(SP + "ge.pkl", "rb"))
    atr = g.daily_atr(15); tr = g.trading; dts = pd.DatetimeIndex(g.ts[tr])
    o830, c900 = g.o[tr, 511], g.c[tr, 900]
    cl = pd.Series(c900).ffill().to_numpy()
    day = (c900 - o830) * PV
    nxt = np.r_[day[1:], np.nan]
    cc = np.r_[np.nan, np.diff(cl)]                                # today's close-to-close move (pts)
    a_tr = atr[tr]
    print(__doc__.split("\n")[0])

    S = signals(cl, CTA_N); fd = flip_dir(S)
    print("\n1. CTA flips (21/63/126/252): fade the next day 8:30 -> 15:00, $ per NQ before stops")
    for m in (1, 2):
        rep(f">= {m} flips: fade next day", -np.sign(fd) * nxt, dts, np.abs(fd) >= m)
        rep(f">= {m} flips UP (bullish flip): short next day", -nxt, dts, fd >= m)
        rep(f">= {m} flips DOWN (bearish flip): long next day", nxt, dts, fd <= -m)
    for n_ in CTA_N:
        fi = flip_dir(signals(cl, (n_,)))
        rep(f"single lookback {n_}: fade next day", -np.sign(fi) * nxt, dts, np.abs(fi) >= 1)
    x = pd.Series(-np.sign(fd) * nxt - 17.25, index=dts)[(np.abs(fd) >= 1) & (dts.year >= 2018)]
    print("   >= 1 flip, fade, by year:", x.groupby(x.index.year).sum().round(0).astype(int).to_dict())

    print("\n2. Big-move control: flip days vs non-flip days with the same |close-to-close| / ATR")
    z = np.abs(cc) / a_tr
    flip = np.abs(fd) >= 1
    bins = np.nanpercentile(z[flip & (dts.year >= 2018)], [0, 25, 50, 75, 100])
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (z >= lo) & (z <= hi) & (dts.year >= 2018)
        a = rep(f"  |move| {lo:.2f}-{hi:.2f} ATR, flip days: fade the move next day", -np.sign(cc) * nxt, dts, m & flip)
        b = rep(f"  |move| {lo:.2f}-{hi:.2f} ATR, no flip: fade the move next day", -np.sign(cc) * nxt, dts, m & ~flip)
    print("   (fade the move = fade the flip: a flip up needs an up close)")

    print("\n3. Placebo: 200 random lookback sets (4 lookbacks, 15-300 days, away from 21/63/126/252)")
    rng = np.random.default_rng(7); allowed = [n for n in range(15, 301) if min(abs(n - c) for c in CTA_N) > 3]
    real = (-np.sign(fd) * nxt - 17.25)[(np.abs(fd) >= 1) & (dts.year >= 2018) & ~np.isnan(nxt)].mean()
    pl = []
    for _ in range(200):
        Ns = tuple(sorted(rng.choice(allowed, 4, replace=False)))
        f_ = flip_dir(signals(cl, Ns)); m = (np.abs(f_) >= 1) & (dts.year >= 2018) & ~np.isnan(nxt)
        pl.append((-np.sign(f_) * nxt - 17.25)[m].mean())
    pl = np.array(pl)
    print(f"   real fade ${real:.0f} a day vs random sets: mean ${pl.mean():.0f}, 5% ${np.percentile(pl, 5):.0f},"
          f" 95% ${np.percentile(pl, 95):.0f}; real beats {np.mean(real > pl):.0%} of them")

    print("\n4. As a trade: fade the next day from 8:31, stop 0.3 / 0.5 ATR / none, out 15:00")
    for sk in (0.3, 0.5, None):
        rows = []
        for k in range(253, len(tr) - 1):
            if abs(fd[k]) < 1 or dts[k + 1].year < 2018: continue
            d = tr[k + 1]; side = -int(np.sign(fd[k])); e = g.o[d, 511]
            if np.isnan(e) or np.isnan(atr[d]): continue
            r_ = row(g, d, 511, side, jof(1500), (e + side * 0.25) - side * sk * atr[d] if sk else None, None)
            if r_: rows.append(r_)
        t = pd.DataFrame(rows)
        print("  " + summ(t, f"fade CTA flip next day, stop {sk or 'none'}", 50))
        if sk == 0.3: t.to_pickle(SP + "cta_fade_trades.pkl")

    print("\n5. Fade the trigger touch intraday (limit at the nearest trigger 8:45-14:00, stop 0.3 ATR, out 15:00)")
    rows = []
    for k in range(260, len(tr)):
        d = tr[k]
        if dts[k].year < 2018 or np.isnan(atr[d]): continue
        p0 = g.c[d, jof(845)]
        if np.isnan(p0): continue
        lv = []
        for i, n in enumerate(CTA_N):
            ref = cl[k - n]; s_prev = S[i, k - 1]
            if s_prev < 0 and ref > p0: lv.append((ref - p0, -1, ref))      # touch from below -> short
            if s_prev > 0 and ref < p0: lv.append((p0 - ref, 1, ref))       # touch from above -> long
        lv = [x for x in lv if x[0] <= 1.0 * atr[d]]
        if not lv: continue
        _, side, L = min(lv)
        for j in range(jof(846), jof(1400) + 1):
            if np.isnan(g.h[d, j]): continue
            if (side < 0 and g.h[d, j] >= L) or (side > 0 and g.l[d, j] <= L):
                # limit fill at L (no slippage), stop 0.3 ATR, out 15:00
                stop = L - side * 0.3 * atr[d]; px = None; j1 = jof(1500)
                for jj in range(j + 1, jof(1500) + 1):
                    if np.isnan(g.h[d, jj]): continue
                    if (side > 0 and g.l[d, jj] <= stop) or (side < 0 and g.h[d, jj] >= stop):
                        px = (min(g.o[d, jj], stop) if side > 0 else max(g.o[d, jj], stop)) - side * 0.25; j1 = jj; break
                if px is None:
                    cc_ = g.c[d, jof(1500)]
                    if np.isnan(cc_): break
                    px = cc_ - side * 0.25
                rows.append(dict(day=d, j0=j, j1=j1, side=side, entry=L, exit=px, kind=0, slips=0,
                                 net=(px - L) * side * PV - 7.25, date=pd.Timestamp(g.ts[d])))
                break
    print("  " + summ(pd.DataFrame(rows), "fade trigger touch", 50))

    print("\n6. Vol-control flow known at the open (lag 1), last hour 14:01 -> 15:00, by sign")
    ei = pd.Series(np.arange(len(es.dates)), index=es.dates).reindex(g.dates[tr]).to_numpy()
    okk = ~np.isnan(ei); ei = np.where(okk, ei, 0).astype(int)
    e900 = pd.Series(np.where(okk, es.c[ei, 900], np.nan)).ffill().to_numpy()
    r_es = np.r_[np.nan, e900[1:] / e900[:-1] - 1]
    E = vc_exposure(r_es); f = np.r_[np.nan, E[:-1]] - np.r_[np.nan, np.nan, E[:-2]]
    lh = (c900 - g.o[tr, 841]) * PV
    for q in (0.04, 0.06, 0.08):
        rep(f"sell flow > {q}: short 14:01-15:00", -lh, dts, f < -q)
        rep(f"buy flow > {q}: long 14:01-15:00", lh, dts, f > q)
        rep(f"sell flow > {q}: short 8:30-15:00", -day, dts, f < -q)
    xs = pd.Series(-lh - 17.25, index=dts)[(f < -0.06) & (dts.year >= 2018)]
    print("   sell flow > 0.06, last hour short, by year:", xs.groupby(xs.index.year).sum().round(0).astype(int).to_dict())

    print("\n7. Vol-control sell-flow last hour as a trade (short 14:01, stop k ATR, out 15:00) and in the funded bench")
    import metrics as M, resampling as R
    days_ = dts[dts.year >= 2018]
    res = {}
    for q in (0.04, 0.06, 0.08):
        for sk in (0.15, 0.25, None):
            rows = []
            for k in np.where(f < -q)[0]:
                d = tr[k]
                if dts[k].year < 2018 or np.isnan(atr[d]): continue
                e = g.o[d, 841]
                if np.isnan(e): continue
                r_ = row(g, d, 841, -1, jof(1500), (e - 0.25) + sk * atr[d] if sk else None, None)
                if r_: rows.append(r_)
            t = pd.DataFrame(rows); res[(q, sk)] = t
            print("  " + summ(t, f"sell flow > {q}, stop {sk or 'none'}", 40))
    t = res[(0.06, 0.25)]
    dly = t.groupby(t.date).net.sum().reindex(days_, fill_value=0.0)
    h = t[t.date.dt.year >= 2023]; D2 = days_[days_.year >= 2023]
    print(M.table({"VC sell 0.06 / 0.25 ATR, 2018-26": (dly, t.net),
                   "  2023-26": (h.groupby(h.date).net.sum().reindex(D2, fill_value=0.0), h.net)}))
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    lab.add("VCS", t, stop_pts=0.25 * atr, slippage=False)
    dts2 = pd.DatetimeIndex(g.ts[lab.tr]); mk = dts2.year >= 2018
    P = {k: pd.Series(lab.daily(k), index=dts2)[mk] for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "VCS")}
    print("  correlation with the plan:", pd.DataFrame(P).corr().round(2).loc["VCS"].to_dict())
    both = (pd.Series(lab.daily("LDF_MC"), index=dts2) != 0) & (pd.Series(lab.daily("VCS"), index=dts2) != 0)
    print(f"  days traded by both VCS and Late-Day Flow: {both.sum()} of {(pd.Series(lab.daily('VCS'), index=dts2) != 0).sum()}")
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2}
    CS = dict(fmin=0.5, fmax=1.0, ref=2000.0)
    for nm, p in (("current plan", plan), ("+ VCS 1 MNQ", {**plan, "VCS": 1}), ("+ VCS 2 MNQ", {**plan, "VCS": 2}),
                  ("+ VCS $300 risk", {**plan, "VCS": ("risk", 300)})):
        a = lab.score(p, 250, **CS); b = lab.score(p, 500, **CS)
        print(f"  {nm:<18} 1y ${a['expected']:,.0f} (2023+ ${a['s2023_on']:,.0f}) 2y ${b['expected']:,.0f} blown {a['blown']:.0%} / {b['blown']:.0%}")
    B, Pm = R.report({"VCS 2023-26": dly[dly.index.year >= 2023], "VCS 2018-26": dly}, n=5000)
    print(B); print(Pm)
