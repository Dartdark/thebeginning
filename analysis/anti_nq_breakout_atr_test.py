"""Antigravity's NQBreakoutATR (antigravity/jesse strategies/NQBreakoutATR, report NQ_breakout_atr_building_blocks_report.md,
2026-10-20): independent rebuild on our data, 2018-2026, with our costs (pre-registered 2026-10-20, before any result).

Rule as coded (Jesse, 15-minute NQ candles, 24 h): long when the close > highest high of the previous 10 bars, short when
the close < lowest low of the previous 10, only if the candle OPENS 08:30-14:30 CT and ADX(14) > 30 (filter 9128);
market fill at that close. Stop = entry -/+ 2 x ATR(14) (resting, intrabar on 1-minute data). At each 15-min close:
exit 4 = give back >= 40 points from the best close; exit 5 (the 'production' mode) = once the best close is >= 50 points
in profit, exit if the open gain < 50% of it. One position at a time; NO time exit (positions run overnight).
Antigravity's report: 2021-22 in-sample (filter and exit picked there), 2023-24 'OOS', 2019-24 1,218 trades +$43,398 at
5 MNQ (~$71 per NQ a trade); its own bootstrap median Sharpe 0.83 vs 2.02 original.

Variants (4, fixed in advance): A as coded (exit 5, holds overnight); B exit 4 only (its baseline); C no filter (naked,
exit 5); D Apex version = A + flat at 15:55 CT and no entry after 14:45. Prices roll-adjusted (overnight holds cross the
17:00 / 03:30 roll jumps). Costs $7.25 + 1 tick on entry and exit = $17.25 per NQ. Random-entry placebo for A and D: the
same number of entries on random 15-min bars of the same window with a random side, same exits, 200 runs.
  python3 analysis/anti_nq_breakout_atr_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from roll_adjust import roll_jumps
import metrics as M, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, COST = 20.0, 17.25


def wilder(x, n):
    out = np.full(len(x), np.nan); x = np.asarray(x, float); s = np.nan
    for i in range(len(x)):
        if np.isnan(x[i]): out[i] = s; continue
        s = x[i] if np.isnan(s) else s + (x[i] - s) / n; out[i] = s
    return out


def build(g):
    n = g.D * 1440; adj = np.zeros(n + 1)
    for j, jump in roll_jumps(g, "NQ").items(): adj[:j] += jump
    adj = adj[:n]; f = lambda a: a.ravel() + adj
    o, h, l, c = f(g.o), f(g.h), f(g.l), f(g.c)
    m = dict(o=o, h=h, l=l, c=c)
    k = 15; nb = n // k
    H = np.nanmax(h[:nb * k].reshape(nb, k), 1); L = np.nanmin(l[:nb * k].reshape(nb, k), 1)
    cc = c[:nb * k].reshape(nb, k); C = pd.DataFrame(cc).ffill(axis=1).to_numpy()[:, -1]
    ok = ~np.isnan(C)
    bars = pd.DataFrame(dict(H=H[ok], L=L[ok], C=C[ok], end=(np.arange(nb)[ok] + 1) * k - 1))   # end = last minute index
    tm = (bars.end % 1440); bars["t_close"] = (tm + 1) // 60 * 100 + (tm + 1) % 60          # bar close time HHMM
    bars["date"] = pd.to_datetime(g.ts[bars.end // 1440]); bars["dow"] = bars.date.dt.dayofweek
    pc = bars.C.shift(1)
    tr = np.maximum(bars.H - bars.L, np.maximum((bars.H - pc).abs(), (bars.L - pc).abs()))
    bars["atr"] = wilder(tr.to_numpy(), 14)
    up = bars.H.diff(); dn = -bars.L.diff()
    pdm = np.where((up > dn) & (up > 0), up, 0.0); ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
    atr_ = wilder(tr.to_numpy(), 14); pdi = 100 * wilder(pdm, 14) / atr_; ndi = 100 * wilder(ndm, 14) / atr_
    dx = 100 * np.abs(pdi - ndi) / (pdi + ndi); bars["adx"] = wilder(dx, 14)
    bars["hh"] = bars.H.shift(1).rolling(10).max(); bars["ll"] = bars.L.shift(1).rolling(10).min()
    return bars, m


def run(bars, m, filt=True, mode=5, flat=False, forced=None, rng=None):
    """forced: array of (bar index, side) entries for the placebo instead of the rule."""
    B = bars; n = len(B); C, H, L, E = B.C.to_numpy(), B.H.to_numpy(), B.L.to_numpy(), B.end.to_numpy()
    tc = B.t_close.to_numpy(); atr = B.atr.to_numpy(); adx = B.adx.to_numpy(); hh, ll = B.hh.to_numpy(), B.ll.to_numpy()
    start = int(np.searchsorted(B.date.to_numpy(), np.datetime64("2018-01-01")))
    win = (tc >= 845) & (tc <= 1445)
    sig = np.zeros(n, int)
    if forced is None:
        ok = win & ((adx > 30) if filt else True)
        sig[ok & (C > hh)] = 1; sig[ok & (C < ll) & (sig == 0)] = -1
    else:
        for i, s in forced: sig[i] = s
    out = []; i = start
    while i < n - 1:
        s = sig[i]
        if s == 0 or np.isnan(atr[i]): i += 1; continue
        e = C[i]; stop = e - s * 2 * atr[i]; best = e; x = None; j = i + 1
        while j < n:
            lo, hi = E[j - 1] + 1, E[j] + 1                        # minutes of bar j
            mins_l, mins_h, mins_o = m["l"][lo:hi], m["h"][lo:hi], m["o"][lo:hi]
            hit = np.flatnonzero((mins_l <= stop) if s > 0 else (mins_h >= stop))
            if flat:                                               # 15:55 flat inside the bar
                day_min = (np.arange(lo, hi) % 1440)
                fl = np.flatnonzero(day_min == jof(1555))
                if len(fl) and (not len(hit) or fl[0] < hit[0]):
                    x = pd.Series(m["c"][lo:lo + fl[0] + 1]).ffill().iloc[-1]; break
            if len(hit):
                q = hit[0]; op = mins_o[q]; x = (min(op, stop) if s > 0 else max(op, stop)) if not np.isnan(op) else stop; break
            px = C[j]; best = max(best, px) if s > 0 else min(best, px)
            gain, mx = (px - e) * s, (best - e) * s
            if mode == 5 and mx >= 50 and gain / mx < 0.5: x = px; break
            if (best - px) * s >= 40: x = px; break
            j += 1
        if x is None: break
        j = min(j, n - 1)
        out.append((B.date.iloc[i], s, tc[i], e, x, (x - e) * s * PV - COST, j - i, E[i], E[j]))
        i = j                                                      # next signal from the exit bar's close on
    return pd.DataFrame(out, columns=["date", "side", "t", "entry", "exit", "pnl", "bars", "m0", "m1"])


def line(nm, t):
    x = t.pnl; yr = t.groupby(t.date.dt.year).pnl.sum(); gp, gl = x[x > 0].sum(), -x[x < 0].sum()
    a, b = t[t.date < "2023"].pnl, t[t.date >= "2023"].pnl
    ts = lambda v: v.mean() / v.std() * np.sqrt(len(v))
    print(f"   {nm:<34} n {len(t):5d} ${x.mean():6.0f} PF {gp / gl:4.2f} t {ts(x):4.1f} win {(x > 0).mean():.0%} yrs+ {(yr > 0).sum()}/{len(yr)}"
          f" | 18-22 ${a.mean():.0f} (t {ts(a):.1f}) 23+ ${b.mean():.0f} (t {ts(b):.1f}) | long ${t[t.side > 0].pnl.mean():.0f} short ${t[t.side < 0].pnl.mean():.0f}"
          f" | hold {t.bars.median():.0f} bars")
    return yr


def placebo(bars, m, real, nm, flat, runs=200, seed=5):
    rng = np.random.default_rng(seed); tc = bars.t_close.to_numpy()
    start = int(np.searchsorted(bars.date.to_numpy(), np.datetime64("2018-01-01")))
    pool = np.flatnonzero((tc >= 845) & (tc <= 1445) & (np.arange(len(bars)) >= start) & ~np.isnan(bars.atr.to_numpy()))
    means = []
    for _ in range(runs):
        idx = np.sort(rng.choice(pool, len(real), replace=False)); sd = rng.choice([-1, 1], len(idx))
        p = run(bars, m, mode=5, flat=flat, forced=zip(idx, sd)); means.append(p.pnl.mean())
    means = np.array(means)
    print(f"   placebo {nm}: real ${real.pnl.mean():.0f} vs random ${means.mean():.0f} (p95 ${np.percentile(means, 95):.0f}), p = {(np.sum(means >= real.pnl.mean()) + 1) / (runs + 1):.3f}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); bars, m = build(g); del g
    print(f"15-min bars {len(bars)}, {bars.date.iloc[0].date()} .. {bars.date.iloc[-1].date()}")
    R = {}
    for nm, kw in (("A as coded (exit 5, overnight)", dict()), ("B exit 4 only", dict(mode=0)),
                   ("C no filter", dict(filt=False)), ("D Apex: A + flat 15:55", dict(flat=True))):
        R[nm] = run(bars, m, **kw); yr = line(nm, R[nm])
        if nm.startswith("A"): print("      by year:", yr.round(0).to_dict())
        if nm.startswith("A"): print("      2019-24 only (its window):", round(R[nm][(R[nm].date >= "2019") & (R[nm].date < "2025")].pnl.mean()), "$ a trade per NQ")
    A = R["A as coded (exit 5, overnight)"]; D = R["D Apex: A + flat 15:55"]
    over = (A.m1 // 1440 > A.m0 // 1440) | (A.m1 % 1440 > jof(1559))
    print(f"   A: share of trades still open after 15:59 CT: {over.mean():.0%}; their average ${A[over].pnl.mean():.0f} vs same-day ${A[~over].pnl.mean():.0f}")
    placebo(bars, m, A, "A", flat=False); placebo(bars, m, D, "D", flat=True)
    for nm, t in (("A", A), ("D", D)):
        idx = pd.bdate_range("2018-01-01", "2026-10-09"); d = pd.Series(0.0, index=idx); gg = t.groupby("date").pnl.sum()
        d.loc[d.index.intersection(gg.index)] = gg.reindex(d.index.intersection(gg.index)).values
        print(f"\n   {nm}: ", M.perf(d, t.pnl)); print(MC.report(t.pnl.to_numpy(), d.to_numpy(), size=0.1, label=nm + " 1 MNQ"))
