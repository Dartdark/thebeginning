"""Ingredient ablation, round 3 (user 2026-11-08: 'take apart relative strength, late day flow, and dual thrust'). Information only
(historical component evidence, no promotion). Dual Thrust was taken apart in round 2 (analysis/ingredient_ablation2.py, same day):
its rows are not rerun here. Each strategy as is, then ONE part removed or isolated at a time, per NQ after repo costs ($7.25 + 1 tick
per market / stop fill), 2018-26 and both periods, with total $ and max drawdown. Coupled changes labelled.
  Relative Strength (relative_strength_test: at 9:00 Z of NQ's 8:30-9:00 move beyond beta x ES's, |Z| >= 1.25, follow at 9:01, stop 0.6 /
    target 1.0 x the 20-day average RTH range, flat 15:00): own momentum only (beta 0) / market part only (beta x ES) / no volatility
    scaling (raw residual move in bp, threshold set so the trade count matches: a full-sample quantile, labelled) / no target / no stop
    (target kept) / decide at 9:15 / longs only / shorts only / random side (50 runs)
  Late-Day Flow (rule of NQ_Late_Day_Flow.txt, MultiCharts-confirmed: at 14:00 CT, if the move from the 08:30 open >= 0.4 x ATR15, follow
    at the next bar's open, stop 0.25 x ATR, out at the 14:30 close; CME early-close days skipped; rebuilt here on the 1-min grid):
    no move threshold (follow every day) / no volatility scaling (threshold as a % of price, count matched; full-sample quantile) /
    no stop / exit 15:00 instead of 14:30 / signal at 14:10 / longs only / shorts only / random side (50 runs)
  tools/run_stamped.sh analysis/ingredient_ablation3.py > analysis/outputs/ingredient_ablation3_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from replica import is_early_close

PV, TICK, COMM = 20.0, 0.25, 7.25


def line(x, d, nm):
    x = pd.Series(np.asarray(x, float)); d = pd.DatetimeIndex(d); tt = lambda v: v.mean() / v.std(ddof=1) * np.sqrt(len(v)) if len(v) > 2 else np.nan
    a, b = x[(d < "2023").tolist()], x[(d >= "2023").tolist()]; pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    cum = pd.Series(x.values, index=d).groupby(level=0).sum().cumsum(); mdd = (cum.cummax() - cum).max()
    return (f"   {nm:<46} n {len(x):5d} ${x.mean():5.0f} t {tt(x):5.2f} PF {pf:4.2f} total ${x.sum() / 1000:5.0f}k maxDD ${mdd / 1000:4.1f}k | 2018-22 ${a.mean():4.0f} (t {tt(a):4.1f})"
            f" 2023+ ${b.mean():4.0f} (t {tt(b):4.1f}) | worst ${x.min():,.0f}")


def ldf(g, k=0.4, stop=0.25, sig=1400, ex=1430, pct=None, rng=None, use_stop=True):
    atr = g.daily_atr(15); ts = pd.DatetimeIndex(g.ts); rows = []; js, jx, j0o = jof(sig), jof(ex), jof(831)
    for d in g.trading:
        if ts[d].year < 2018 or np.isnan(atr[d]) or is_early_close(ts[d]): continue
        o0, cs = g.o[d, j0o], g.c[d, js]
        if np.isnan(o0) or np.isnan(cs) or np.isnan(g.c[d, jx]): continue
        mv = cs - o0; thr = (pct / 100 * o0) if pct is not None else k * atr[d]
        if abs(mv) < thr or mv == 0: continue
        side = int(np.sign(mv)) if rng is None else int(rng.choice([-1, 1]))
        j0 = js + 1; e = g.o[d, j0] + side * TICK; sl = e - side * stop * atr[d]; px = None
        if use_stop:
            for j in range(j0, jx + 1):
                if np.isnan(g.c[d, j]): continue
                if (g.l[d, j] <= sl) if side > 0 else (g.h[d, j] >= sl):
                    px = (min(g.o[d, j], sl) if side > 0 else max(g.o[d, j], sl)) - side * TICK; break
        if px is None: px = g.c[d, jx] - side * TICK
        rows.append(dict(date=ts[d], side=side, net=(px - e) * side * PV - COMM, mv_pct=abs(mv) / o0 * 100))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = [sys.argv[0], "scratch_data"]
    import relative_strength_test as RS
    days, N, E = RS.load(); Z = RS.signals(days, N, E)
    T0 = RS.trades(days, N, Z); T0 = T0[T0.date >= "2018-01-01"]
    print("\n1. Relative Strength:")
    print(line(T0.pnl, T0.date, "as is"))
    Zo = RS.signals(days, N, E, beta_mode="own"); T = RS.trades(days, N, Zo); T = T[T.date >= "2018-01-01"]; print(line(T.pnl, T.date, "own momentum only (beta 0)"))
    Zm = RS.signals(days, N, E, beta_mode="mkt"); T = RS.trades(days, N, Zm); T = T[T.date >= "2018-01-01"]; print(line(T.pnl, T.date, "market part only (beta x ES)"))
    Zr = RS.signals(days, N, E, beta_mode="raw"); ok = np.isfinite(Z) & np.isfinite(Zr); share = np.mean(np.abs(Z[ok]) >= 1.25)
    thr = np.quantile(np.abs(Zr[ok]), 1 - share); T = RS.trades(days, N, Zr, zmin=thr); T = T[T.date >= "2018-01-01"]
    print(line(T.pnl, T.date, f"no vol scaling (raw residual >= {thr:.0f} bp; count-matched)"))
    for nm, kw in (("no target", dict(tgt_f=None)), ("no stop (target kept)", dict(stop_f=1e6))):
        T = RS.trades(days, N, Z, **kw); T = T[T.date >= "2018-01-01"]; print(line(T.pnl, T.date, nm))
    Z15 = RS.signals(days, N, E, decide=915); T = RS.trades(days, N, Z15, decide=915); T = T[T.date >= "2018-01-01"]; print(line(T.pnl, T.date, "decide at 9:15"))
    print(line(T0[T0.side > 0].pnl, T0[T0.side > 0].date, "longs only")); print(line(T0[T0.side < 0].pnl, T0[T0.side < 0].date, "shorts only"))
    # random side: flip the side, mirror the bracket (same days, same entry)
    rm = []
    for s in range(50):
        rng = np.random.default_rng(s); Zp = np.where(np.isfinite(Z), np.abs(Z) * rng.choice([-1, 1], len(Z)), np.nan)
        Tp = RS.trades(days, N, Zp); rm.append(Tp[Tp.date >= "2018-01-01"].pnl.mean())
    print(f"   random side (50 runs, same days): ${np.mean(rm):.0f} a trade, 95th ${np.percentile(rm, 95):.0f}; real ${T0.pnl.mean():.0f}", flush=True)
    g = pickle.load(open("scratch_data/g24.pkl", "rb"))
    print("\n2. Late-Day Flow (check vs MultiCharts: 895 trades, $95 a trade, PF 1.44, t 3.5):")
    L0 = ldf(g); print(line(L0.net, L0.date, "as is"))
    T = ldf(g, k=0.0); print(line(T.net, T.date, "no move threshold (follow every day)"))
    q = np.quantile(ldf(g, k=0.0).mv_pct, 1 - len(L0) / len(T)); T = ldf(g, pct=q); print(line(T.net, T.date, f"no vol scaling (move >= {q:.2f}% of price; count-matched)"))
    for nm, kw in (("no stop", dict(use_stop=False)), ("exit 15:00 instead of 14:30", dict(ex=1500)), ("signal at 14:10", dict(sig=1410, ex=1440))):
        T = ldf(g, **kw); print(line(T.net, T.date, nm))
    print(line(L0[L0.side > 0].net, L0[L0.side > 0].date, "longs only")); print(line(L0[L0.side < 0].net, L0[L0.side < 0].date, "shorts only"))
    rm = [ldf(g, rng=np.random.default_rng(s)).net.mean() for s in range(50)]
    print(f"   random side (50 runs, same days): ${np.mean(rm):.0f} a trade, 95th ${np.percentile(rm, 95):.0f}; real ${L0.net.mean():.0f}")
    print("\n3. Dual Thrust: see analysis/outputs/ingredient_ablation2_output.txt (round 2, same day).")
