"""Candlestick patterns on NQ (user 2026-11-08, hft.md/cp chart-pattern sheet). PRE-REGISTERED (this header committed with the
first run; 36 trials): 12 patterns x 3 timeframes, RTH bars 2018-26, per 1 NQ, $7.25 + 1 tick per market / stop fill.
Patterns (b = body |C-O|, r = range H-L, uw / lw = upper / lower wick; 'down' = close 1 bar ago < close 4 bars ago):
  bull engulfing: prev red, now green, O <= C1 and C >= O1, down     bear engulfing: mirror, up
  hammer: lw >= 2b, uw <= 0.25 r, b > 0, down -> long              shooting star: uw >= 2b, lw <= 0.25 r, up -> short
  morning star: bar1 red b1 >= 0.6 r1, bar2 b2 <= 0.3 b1, bar3 green C3 > mid of bar1 body   evening star: mirror
  three white soldiers: 3 green, rising closes, each O inside prior body, each b >= 0.5 r -> long   three black crows: mirror
  piercing: prev red b >= 0.6 r, O <= C1, mid(body1) < C < O1, down    dark cloud: mirror, up
  bull harami: prev red b >= 0.6 r, now green with body inside prev body, down     bear harami: mirror, up
Trades: enter at the next bar's open; stop 1 x the 14-bar average range of that timeframe; exit after 3 bars (intraday) or at
14:59 CT (daily: the next session, 08:30 open -> 14:59); everything flat by 14:59 (Apex-legal). No entries after 14:30 intraday.
Control: the same trade on EVERY bar, same side; placebo p = share of 1,000 random same-size sets of those trades with a mean >= the
pattern's. 2023+ shown separately.
  tools/run_stamped.sh analysis/candlestick_patterns_test.py > analysis/outputs/candlestick_patterns_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M

PV, TICK, COMM = 20.0, 0.25, 7.25
J830, J1459, J1430 = jof(830), jof(1459), jof(1430)


def rth_bars(g, k):
    """RTH bars of k minutes (k = 5 / 15) or daily (k = 0): DataFrame row, j_end (last minute column), o h l c."""
    T = g.trading; out = []
    for r in T:
        if pd.Timestamp(g.ts[r]) < pd.Timestamp("2017-10-01"): continue
        if k == 0:
            seg = slice(J830 + 1, jof(1500) + 1); c = g.c[r, seg]
            if np.isnan(c).all(): continue
            ok = ~np.isnan(c); o = g.o[r, seg][ok][0]
            out.append((r, jof(1500), o, np.nanmax(g.h[r, seg]), np.nanmin(g.l[r, seg]), c[ok][-1])); continue
        for s in range(J830 + 1, jof(1500) + 1, k):
            seg = slice(s, s + k); c = g.c[r, seg]
            if np.isnan(c).all(): continue
            ok = ~np.isnan(c)
            out.append((r, s + k - 1, g.o[r, seg][ok][0], np.nanmax(g.h[r, seg]), np.nanmin(g.l[r, seg]), c[ok][-1]))
    return pd.DataFrame(out, columns=["row", "j", "o", "h", "l", "c"])


def patterns(B):
    o, h, l, c = (B[x].to_numpy() for x in "ohlc"); b = np.abs(c - o); r = h - l
    uw = h - np.maximum(o, c); lw = np.minimum(o, c) - l
    sh = lambda x, n: np.concatenate([np.full(n, np.nan), x[:-n]])
    o1, c1, b1, r1 = sh(o, 1), sh(c, 1), sh(b, 1), sh(r, 1); o2, c2, b2, r2 = sh(o, 2), sh(c, 2), sh(b, 2), sh(r, 2)
    down = c1 < sh(c, 4); up = c1 > sh(c, 4)
    green, red = c > o, c < o; g1, r1d = c1 > o1, c1 < o1; g2, r2d = c2 > o2, c2 < o2
    with np.errstate(invalid="ignore"):
        P = {
            "bull engulfing": (r1d & green & (o <= c1) & (c >= o1) & down, 1),
            "bear engulfing": (g1 & red & (o >= c1) & (c <= o1) & up, -1),
            "hammer": ((lw >= 2 * b) & (uw <= 0.25 * r) & (b > 0) & down, 1),
            "shooting star": ((uw >= 2 * b) & (lw <= 0.25 * r) & (b > 0) & up, -1),
            "morning star": (r2d & (b2 >= 0.6 * r2) & (b1 <= 0.3 * b2) & green & (c > (o2 + c2) / 2), 1),
            "evening star": (g2 & (b2 >= 0.6 * r2) & (b1 <= 0.3 * b2) & red & (c < (o2 + c2) / 2), -1),
            "three white soldiers": (green & g1 & g2 & (c > c1) & (c1 > c2) & (o >= o1) & (o <= c1) & (o1 >= o2) & (o1 <= c2)
                                     & (b >= 0.5 * r) & (b1 >= 0.5 * r1) & (b2 >= 0.5 * r2), 1),
            "three black crows": (red & r1d & r2d & (c < c1) & (c1 < c2) & (o <= o1) & (o >= c1) & (o1 <= o2) & (o1 >= c2)
                                  & (b >= 0.5 * r) & (b1 >= 0.5 * r1) & (b2 >= 0.5 * r2), -1),
            "piercing": (r1d & (b1 >= 0.6 * r1) & (o <= c1) & (c > (o1 + c1) / 2) & (c < o1) & down, 1),
            "dark cloud": (g1 & (b1 >= 0.6 * r1) & (o >= c1) & (c < (o1 + c1) / 2) & (c > o1) & up, -1),
            "bull harami": (r1d & (b1 >= 0.6 * r1) & green & (o >= c1) & (c <= o1) & down, 1),
            "bear harami": (g1 & (b1 >= 0.6 * r1) & red & (o <= c1) & (c >= o1) & up, -1),
        }
    return {k: (np.nan_to_num(v, nan=0).astype(bool), s) for k, (v, s) in P.items()}


def trades(g, B, k, side):
    """Net $ of the trade signalled at each bar (NaN when no valid trade), for one side."""
    T = list(g.trading); pos = {r: i for i, r in enumerate(T)}
    atr = (B.h - B.l).rolling(14, min_periods=10).mean().shift(0).to_numpy()
    net = np.full(len(B), np.nan); rows = B.row.to_numpy(); js = B.j.to_numpy()
    for i in range(len(B)):
        if np.isnan(atr[i]): continue
        if k == 0:
            p = pos[rows[i]]
            if p + 1 >= len(T): continue
            r = T[p + 1]; j0, j1 = J830 + 1, J1459
        else:
            r = rows[i]; j0 = js[i] + 1; j1 = min(js[i] + 3 * k, J1459)
            if js[i] >= J1430: continue
        o = g.o[r, j0:j1 + 1]; h = g.h[r, j0:j1 + 1]; l = g.l[r, j0:j1 + 1]; c = g.c[r, j0:j1 + 1]
        ok = ~np.isnan(c)
        if ok.sum() < 1: continue
        o, h, l, c = o[ok], h[ok], l[ok], c[ok]; e = o[0]; stp = e - side * atr[i]; x = None
        hit = np.nonzero(l <= stp)[0] if side > 0 else np.nonzero(h >= stp)[0]
        if len(hit): m = hit[0]; x = (min(o[m], stp) if side > 0 else max(o[m], stp)) - side * TICK
        else: x = c[-1] - side * TICK
        net[i] = ((x - (e + side * TICK)) * side) * PV - COMM
    return net


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); rng = np.random.default_rng(7); rows_out = []
    for k, tf in ((0, "daily"), (15, "15-min"), (5, "5-min")):
        B = rth_bars(g, k); d = pd.DatetimeIndex(g.ts[B.row.to_numpy()]); keep = d >= "2018-01-01"
        P = patterns(B); ALL = {s: trades(g, B, k, s) for s in (1, -1)}
        print(f"\n{tf} bars 2018-26 (n {keep.sum()}); control = every bar: long ${np.nanmean(ALL[1][keep]):.1f}, short ${np.nanmean(ALL[-1][keep]):.1f} a trade")
        for nm, (m, s) in P.items():
            x = ALL[s]; sel = m & keep & ~np.isnan(x); v = x[sel]
            if len(v) < 10: print(f"   {nm:<22} n {len(v)} (too few)"); continue
            pool = x[keep & ~np.isnan(x)]
            pl = np.array([pool[rng.choice(len(pool), len(v), replace=False)].mean() for _ in range(1000)])
            a = v[d[sel] < "2023"]; b = v[d[sel] >= "2023"]; tt = v.mean() / v.std(ddof=1) * np.sqrt(len(v))
            pf = v[v > 0].sum() / max(1e-9, -v[v < 0].sum())
            print(f"   {nm:<22} {'L' if s > 0 else 'S'} n {len(v):5d} ${v.mean():6.1f} t {tt:5.2f} PF {pf:4.2f} win {np.mean(v > 0):4.0%} | control ${pool.mean():6.1f}"
                  f" placebo p {np.mean(pl >= v.mean()):.3f} | 18-22 ${a.mean():6.1f} 23+ ${b.mean():6.1f}", flush=True)
            rows_out.append((tf, nm, len(v), v.mean(), tt, np.mean(pl >= v.mean()), a.mean(), b.mean()))
    R = pd.DataFrame(rows_out, columns=["tf", "pattern", "n", "mean", "t", "p", "m1822", "m23"])
    nt = len([1 for l_ in open("TIER_LIST.md") if l_.startswith("| ") and "---" not in l_]) + 36
    print(f"\nt needed (N = {nt}): {M.t_threshold(nt):.2f}; patterns with t >= 2: {(R.t >= 2).sum()} of {len(R)}; placebo p < 0.05: {(R.p < 0.05).sum()};"
          f" positive in both halves AND p < 0.05: {((R.m1822 > 0) & (R.m23 > 0) & (R.p < 0.05)).sum()}")
