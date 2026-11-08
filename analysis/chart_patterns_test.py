"""Chart patterns on NQ (user 2026-11-08, hft.md/cp sheet, part 2). PRE-REGISTERED (header committed before the first run; 36 trials).
Pattern definitions follow Lo, Mamaysky & Wang (2000, 'Foundations of Technical Analysis') on causal zigzag pivots:
  pivot = swing high / low confirmed once price moves 1.5 x ATR14 (of that timeframe) back from it; signal at the confirmation bar,
  on the last 5 pivots E1..E5 (E5 = just confirmed). Tolerance tol = 0.75 x ATR ('equal' levels), rectangles 0.4 x ATR.
  HS (short): E1 max, E3 > E1, E3 > E5, |E1-E5| <= tol, |E2-E4| <= tol          IHS (long): mirror
  BTOP (short): E1 max, E1 < E3 < E5, E2 > E4                                     BBOT (long): E1 min, E1 > E3 > E5, E2 < E4
  TTOP (short): E1 max, E1 > E3 > E5, E2 < E4                                     TBOT (long): E1 min, E1 < E3 < E5, E2 > E4
  RTOP (short): E1 max, E1/E3/E5 within 0.4 ATR of their mean, E2/E4 too, min top > max bottom      RBOT (long): mirror
  DTOP (short): last 3 pivots max-min-max, |E3-E5| <= tol                         DBOT (long): mirror
  bull flag (long): last leg E4(min) -> E5... uses E3(min) -> E4(max) impulse >= 4.5 ATR, E5 (min) retraces <= 50% of it
  bear flag (short): mirror
Trades as candlestick_patterns_test.py: enter next bar open, stop 1 x ATR, exit after 4 bars (intraday) / the next session open ->
14:59 (daily), flat by 14:59, no intraday entries after 14:30; $7.25 + 1 tick per fill; control = every bar, same side; placebo
1,000 same-size random sets. Timeframes: RTH 15-min, 60-min, daily, 2018-26.
  tools/run_stamped.sh analysis/chart_patterns_test.py > analysis/outputs/chart_patterns_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M
from candlestick_patterns_test import rth_bars, PV, TICK, COMM, J830, J1459, J1430


def pivots_signals(B, k_atr=1.5):
    h, l = B.h.to_numpy(), B.l.to_numpy(); atr = (B.h - B.l).rolling(14, min_periods=10).mean().to_numpy()
    n = len(B); sig = {nm: np.zeros(n, bool) for nm in ("HS", "IHS", "BTOP", "BBOT", "TTOP", "TBOT", "RTOP", "RBOT", "DTOP", "DBOT", "bull flag", "bear flag")}
    piv = []                       # (price, +1 max / -1 min)
    trend, ext, exti = 0, None, None
    for i in range(n):
        a = atr[i]
        if np.isnan(a): continue
        if trend == 0: trend, ext, exti = 1, h[i], i; continue
        conf = False
        if trend == 1:
            if h[i] > ext: ext, exti = h[i], i
            elif ext - l[i] >= k_atr * a: piv.append((ext, 1)); trend, ext, exti, conf = -1, l[i], i, True
        else:
            if l[i] < ext: ext, exti = l[i], i
            elif h[i] - ext >= k_atr * a: piv.append((ext, -1)); trend, ext, exti, conf = 1, h[i], i, True
        if not conf or len(piv) < 5: continue
        E = [p for p, _ in piv[-5:]]; t1 = piv[-5][1]; tol = 0.75 * a; tr = 0.4 * a
        E1, E2, E3, E4, E5 = E
        if t1 == 1:
            sig["HS"][i] = E3 > E1 and E3 > E5 and abs(E1 - E5) <= tol and abs(E2 - E4) <= tol
            sig["BTOP"][i] = E1 < E3 < E5 and E2 > E4
            sig["TTOP"][i] = E1 > E3 > E5 and E2 < E4
            tops, bots = [E1, E3, E5], [E2, E4]
            sig["RTOP"][i] = max(abs(x - np.mean(tops)) for x in tops) <= tr and max(abs(x - np.mean(bots)) for x in bots) <= tr and min(tops) > max(bots)
        else:
            sig["IHS"][i] = E3 < E1 and E3 < E5 and abs(E1 - E5) <= tol and abs(E2 - E4) <= tol
            sig["BBOT"][i] = E1 > E3 > E5 and E2 < E4
            sig["TBOT"][i] = E1 < E3 < E5 and E2 > E4
            bots, tops = [E1, E3, E5], [E2, E4]
            sig["RBOT"][i] = max(abs(x - np.mean(bots)) for x in bots) <= tr and max(abs(x - np.mean(tops)) for x in tops) <= tr and max(bots) < min(tops)
        t5 = piv[-1][1]
        if t5 == 1: sig["DTOP"][i] = abs(E3 - E5) <= tol            # max-min-max
        else: sig["DBOT"][i] = abs(E3 - E5) <= tol                   # min-max-min
        if t5 == -1 and E4 - E3 >= 3 * k_atr * a and (E4 - E5) <= 0.5 * (E4 - E3): sig["bull flag"][i] = True
        if t5 == 1 and E3 - E4 >= 3 * k_atr * a and (E5 - E4) <= 0.5 * (E3 - E4): sig["bear flag"][i] = True
    side = {"HS": -1, "IHS": 1, "BTOP": -1, "BBOT": 1, "TTOP": -1, "TBOT": 1, "RTOP": -1, "RBOT": 1, "DTOP": -1, "DBOT": 1, "bull flag": 1, "bear flag": -1}
    return {k: (v, side[k]) for k, v in sig.items()}


def trades(g, B, k, side, hold=4):
    T = list(g.trading); pos = {r: i for i, r in enumerate(T)}
    atr = (B.h - B.l).rolling(14, min_periods=10).mean().to_numpy()
    net = np.full(len(B), np.nan); rows = B.row.to_numpy(); js = B.j.to_numpy()
    for i in range(len(B)):
        if np.isnan(atr[i]): continue
        if k == 0:
            p = pos[rows[i]]
            if p + 1 >= len(T): continue
            r = T[p + 1]; j0, j1 = J830 + 1, J1459
        else:
            r = rows[i]; j0 = js[i] + 1; j1 = min(js[i] + hold * k, J1459)
            if js[i] >= J1430: continue
        o = g.o[r, j0:j1 + 1]; h = g.h[r, j0:j1 + 1]; l = g.l[r, j0:j1 + 1]; c = g.c[r, j0:j1 + 1]; ok = ~np.isnan(c)
        if ok.sum() < 1: continue
        o, h, l, c = o[ok], h[ok], l[ok], c[ok]; e = o[0]; stp = e - side * atr[i]
        hit = np.nonzero(l <= stp)[0] if side > 0 else np.nonzero(h >= stp)[0]
        x = ((min(o[hit[0]], stp) if side > 0 else max(o[hit[0]], stp)) if len(hit) else c[-1]) - side * TICK
        net[i] = ((x - (e + side * TICK)) * side) * PV - COMM
    return net


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); rng = np.random.default_rng(7); out = []
    for k, tf in ((15, "15-min"), (60, "60-min"), (0, "daily")):
        B = rth_bars(g, k); d = pd.DatetimeIndex(g.ts[B.row.to_numpy()]); keep = d >= "2018-01-01"
        S = pivots_signals(B); ALL = {s: trades(g, B, k, s) for s in (1, -1)}
        print(f"\n{tf} bars 2018-26 (n {keep.sum()}); control = every bar: long ${np.nanmean(ALL[1][keep]):.1f}, short ${np.nanmean(ALL[-1][keep]):.1f}")
        for nm, (m, s) in S.items():
            x = ALL[s]; sel = m & keep & ~np.isnan(x); v = x[sel]
            if len(v) < 10: print(f"   {nm:<10} n {len(v)} (too few)"); continue
            pool = x[keep & ~np.isnan(x)]
            pl = np.array([pool[rng.choice(len(pool), len(v), replace=False)].mean() for _ in range(1000)])
            a, b = v[d[sel] < "2023"], v[d[sel] >= "2023"]; tt = v.mean() / v.std(ddof=1) * np.sqrt(len(v)); pf = v[v > 0].sum() / max(1e-9, -v[v < 0].sum())
            print(f"   {nm:<10} {'L' if s > 0 else 'S'} n {len(v):5d} ${v.mean():7.1f} t {tt:5.2f} PF {pf:4.2f} win {np.mean(v > 0):4.0%} | control ${pool.mean():6.1f}"
                  f" placebo p {np.mean(pl >= v.mean()):.3f} | 18-22 ${a.mean() if len(a) else np.nan:7.1f} 23+ ${b.mean() if len(b) else np.nan:7.1f}", flush=True)
            out.append((tf, nm, len(v), v.mean(), tt, np.mean(pl >= v.mean()), a.mean() if len(a) else np.nan, b.mean() if len(b) else np.nan))
    R = pd.DataFrame(out, columns=["tf", "p_", "n", "mean", "t", "p", "a", "b"])
    nt = len([1 for l_ in open("TIER_LIST.md") if l_.startswith("| ") and "---" not in l_]) + 36
    print(f"\nt needed (N = {nt}): {M.t_threshold(nt):.2f}; t >= 2: {(R.t >= 2).sum()} of {len(R)}; placebo p < 0.05: {(R.p < 0.05).sum()};"
          f" positive both halves AND p < 0.05: {((R.a > 0) & (R.b > 0) & (R.p < 0.05)).sum()}")
