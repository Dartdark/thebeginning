"""Breakout regime: follow when hot, fade when cold (pre-registered: checks/candidates/breakout_regime/PREREG.md, user 2026-11-12).
  tools/run_stamped.sh analysis/breakout_regime_test.py > analysis/outputs/breakout_regime_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import Grid24
import vault_break_v8_test as V
from scipy.stats import spearmanr
print(__doc__.split("\n")[0])
g = Grid24(); B = V.boundary(g, "tr"); ts = pd.DatetimeIndex(g.ts); FL = g.jof(1430); TICK, PV, COST = V.TICK, V.PV, V.COST
print(f"data to {ts[g.trading[-1]].date()}")


def trade(d, j0, side, tp, sl, end=FL):
    """enter at the open of minute j0 (1 tick slippage), bracket tp / sl points (None = none), out at the close of minute end."""
    if np.isnan(g.o[d, j0]): return np.nan
    e = g.o[d, j0] + side * TICK; ef = e - side * TICK
    for m in range(j0, end + 1):
        if np.isnan(g.h[d, m]): continue
        hi, lo = g.h[d, m], g.l[d, m]
        if sl is not None and ((side > 0 and lo <= ef - sl) or (side < 0 and hi >= ef + sl)):
            stp = ef - side * sl; px = (min(g.o[d, m], stp) if side > 0 else max(g.o[d, m], stp)) if m > j0 else stp
            return (px - side * TICK - e) * side * PV - COST
        if tp is not None and ((side > 0 and hi >= ef + tp) or (side < 0 and lo <= ef - tp)):
            return tp * PV - side * 0 - COST - TICK * PV * 0 - (e - ef) * side * PV
    c = g.c[d, end]
    if np.isnan(c): c = g.c[d, :end + 1][~np.isnan(g.c[d, :end + 1])][-1]
    return (c - side * TICK - e) * side * PV - COST


def tt(x): x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan
def line(x, dts, nm):
    x = pd.Series(np.asarray(x, float), index=pd.DatetimeIndex(dts)).dropna(); y = x.index.year
    pf = x[x > 0].sum() / -x[x < 0].sum() if (x < 0).any() else np.inf
    by = " ".join(f"{yy % 100:02d}:{x[y == yy].sum() / 1000:+5.1f}k" for yy in sorted(set(y)))
    return (f"   {nm:<34} n {len(x):4d} avg ${x.mean():5.0f} t {tt(x):4.1f} PF {pf:4.2f} win {np.mean(x > 0):4.0%} | 18-22 ${x[y <= 2022].mean():5.0f} (t {tt(x[y <= 2022]):4.1f}) "
            f"23-26 ${x[y >= 2023].mean():5.0f} (t {tt(x[y >= 2023]):4.1f})\n      by year: {by}")


T = V.run(g, "v1"); T["atr"] = B[T.day.values]
T["drift"] = [(g.c[r.day, FL] - r.entry) / r.atr if not np.isnan(g.c[r.day, FL]) else np.nan for r in T.itertuples()]
# state S: mean drift of the previous 60 signals on earlier dates
dr = T.drift.values; days = T.day.values; S = np.full(len(T), np.nan)
for i in range(len(T)):
    prev = np.flatnonzero(days[:i] < days[i])
    if len(prev) >= 60: S[i] = np.nanmean(dr[prev[-60:]])
T["S"] = S; W = T[~np.isnan(T.S)].copy(); W["yr"] = W.date.dt.year

print("\n== D0: path after VB entries (ATR units, mean): +30 / +60 / +120 min / 14:30; share trading back to the noise level / VWAP")
def pathstats(x):
    out = []
    for r in x.itertuples():
        d, j0 = r.day, r.j0; e = r.entry; a = r.atr
        def at(k): m = min(j0 + k, FL); return (g.c[d, m] - e) / a if not np.isnan(g.c[d, m]) else np.nan
        sess = g.o[d, ~np.isnan(g.o[d])][0]; noise = sess + 0.30 * a
        v = g.v[d, :j0]; tp_ = (g.h[d, :j0] + g.l[d, :j0] + g.c[d, :j0]) / 3; ok = ~np.isnan(tp_) & (v > 0); vw = (tp_[ok] * v[ok]).sum() / v[ok].sum()
        lo = np.nanmin(g.l[d, j0:FL + 1])
        out.append((at(30), at(60), at(120), r.drift, lo <= noise, lo <= vw))
    o = np.array(out, float); return np.nanmean(o, 0)
for lab, m in (("2018-24", T.date.dt.year <= 2024), ("2025", T.date.dt.year == 2025), ("2026 Jan-Jul", (T.date >= "2026-01-01") & (T.date < "2026-08-01")), ("2026 Aug-", T.date >= "2026-08-01")):
    p = pathstats(T[m]); print(f"   {lab:<13} n {m.sum():4d} | +30m {p[0]:+.3f} +60m {p[1]:+.3f} +120m {p[2]:+.3f} 14:30 {p[3]:+.3f} | back to noise level {p[4]:.0%}, to VWAP {p[5]:.0%}")

print("\n== H1: does the state S (mean drift of the previous 60 signals) predict the next signal's drift?")
for lab, m in (("2018-26", W.yr > 0), ("2018-22", W.yr <= 2022), ("2023-26", W.yr >= 2023)):
    x = W[m]; rho, p = spearmanr(x.S, x.drift, nan_policy="omit")
    print(f"   {lab}: n {len(x)} Spearman {rho:+.3f} (p {p:.3f}) | drift when S < 0 {x.drift[x.S < 0].mean():+.4f} (n {np.sum(x.S < 0)}) vs S >= 0 {x.drift[x.S >= 0].mean():+.4f} (n {np.sum(x.S >= 0)})")
print("   share of signals with S < 0 by year: " + " ".join(f"{y % 100:02d}:{np.mean(x.S < 0):.0%}" for y, x in W.groupby("yr")))

print("\n== Variants (per NQ, costs in)")
cold = W[W.S < 0]; hot = W[W.S >= 0]
A = np.array([trade(r.day, r.j0, -1, 40.0, 75.0) for r in cold.itertuples()])
print(line(W.net, W.date, "VB always (after warm-up)"))
print(line(hot.net, hot.date, "B  VB when hot (S >= 0)"))
print(line(A, cold.date, "A  fade when cold (short, 40/75)"))
print(line(cold.net, cold.date, "   (VB's own trades when cold)"))
C = pd.concat([pd.Series(hot.net.values, index=hot.date), pd.Series(A, index=cold.date)]).sort_index()
print(line(C.values, C.index, "C  switch (B + A)"))
for nm, x, dd in (("VB always", W.net, W), ("B", hot.net, hot)):
    pass
rB = lambda x: (x / (75 * 20))
print(f"   avg R: VB always 18-22 {rB(W.net[W.yr <= 2022]).mean():+.3f} 23-26 {rB(W.net[W.yr >= 2023]).mean():+.3f} | B 18-22 {rB(hot.net[hot.yr <= 2022]).mean():+.3f} 23-26 {rB(hot.net[hot.yr >= 2023]).mean():+.3f}")
rng = np.random.default_rng(1); pl = []
for _ in range(200):
    sd = rng.choice([-1, 1], len(cold)); pl.append(np.nanmean([trade(r.day, r.j0, s, 40.0, 75.0) for r, s in zip(cold.itertuples(), sd)]))
pl = np.array(pl); print(f"   A random-side placebo (same entries, 200 runs): mean ${pl.mean():.0f}, A ${np.nanmean(A):.0f}, p {np.mean(pl >= np.nanmean(A)):.3f}")

print("\n== D: market-wide morning move (|m| >= 0.3 ATR at 10:00), follow / fade by the trailing 60-day morning -> afternoon corr")
rows = []
for d in g.trading:
    o, a, b_ = g.o[d, g.jof(831)], g.c[d, g.jof(1000)], g.c[d, FL]
    if np.isnan(o) or np.isnan(a) or np.isnan(b_) or np.isnan(B[d]): continue
    rows.append((d, ts[d], (a - o) / B[d], (b_ - a) / B[d]))
Dd = pd.DataFrame(rows, columns=["d", "date", "am", "pm"]); Dd["rho"] = Dd.am.rolling(60).corr(Dd.pm).shift(1)
Dd = Dd[(Dd.date >= "2018-01-01") & Dd.rho.notna() & (Dd.am.abs() >= 0.3)]
side = np.sign(Dd.am) * np.where(Dd.rho >= 0, 1, -1)
Dn = np.array([trade(int(d), g.jof(1001), int(s), None, round(0.3 * B[int(d)] * 4) / 4) for d, s in zip(Dd.d, side)])
print(line(Dn, Dd.date, "D  regime follow / fade"))
fol = np.array([trade(int(d), g.jof(1001), int(s), None, round(0.3 * B[int(d)] * 4) / 4) for d, s in zip(Dd.d, np.sign(Dd.am))])
print(line(fol, Dd.date, "   (always follow, control)"))
print(line(-fol - 2 * COST, Dd.date, "   (always fade, approx control)"))
pl = []
for _ in range(200):
    sd = rng.choice([-1, 1], len(Dd)); pl.append(np.nanmean([trade(int(d), g.jof(1001), int(s), None, round(0.3 * B[int(d)] * 4) / 4) for d, s in zip(Dd.d, sd)]))
pl = np.array(pl); print(f"   D random-side placebo: mean ${pl.mean():.0f}, D ${np.nanmean(Dn):.0f}, p {np.mean(pl >= np.nanmean(Dn)):.3f}")
W.to_csv("checks/candidates/breakout_regime/vb_signals_state.csv", index=False)
