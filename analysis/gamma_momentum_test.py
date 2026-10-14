"""Dealer gamma x intraday momentum (user's idea, 2026-10-14): do GEX levels turn the end-of-day momentum into a forced flow?

Mechanism (Baltussen, Da, Lammers & Martens 2021; Barbon, Beckmeyer, Buraschi & Moerke 2021): dealers short gamma must
buy as the market rises and sell as it falls, mostly near the close, so the day's move continues into the close when
gamma is negative and reverts when it is positive. Gao et al. (2018) found the momentum on SPY 1993-2013; on NQ it is gone
on average since 2018 (analysis/gao_intraday_momentum_test.py, analysis/intraday_momentum_test.py).
Gamma data:
  - The Bridge's 0DTE NDX gamma flip (GEX_1min_*.csv, cumulative weighting, steepness > 0.02), known intraday,
    2023-03-28 .. 2026-07-07 (backtest-legal part). Regime = NQ above / below the flip at the decision minute.
  - SqueezeMetrics S&P GEX (data/DIX.csv), previous day's value: negative, or its 252-day rank, 2018-2026.
Trades (1 NQ, $7.25 + 1 tick a fill, entry at the decision minute's close, out at 15:00 CT):
  1. Last half-hour 14:30 -> 15:00 following the day's move so far (previous 15:00 close -> 14:30 = "ROD", and the
     regular-session move 8:30 -> 14:30), by the regime at 14:30; fading it above the flip; distance-to-flip buckets.
  2. Last hour 14:00 -> 15:00 and the Late-Day Flow window 14:00 -> 14:30 (8:30 -> 14:00 move), by the regime at 14:00;
     the Late-Day Flow MultiCharts trades by regime.
  3. SqueezeMetrics GEX (2018-26) for the same last-half-hour trade, alone and with the Bridge regime.
  Placebo: the regime labels shuffled across days (1,000 runs) for the below-minus-above difference.
Design 2023-03-28 .. 2024-12-31, holdout 2025-01-01 .. 2026-07-07 (as in analysis/gamma_regime_test.py).
  python3 analysis/gamma_momentum_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from gamma_regime_test import load_gex, Regime, START, END, SPLIT
import gex_flows as GX
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 20.0, 0.25, 7.25
COST = COMM + 2 * TICK * PV


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def line(x, nm, idx=None, w=58):
    x = pd.Series(x).dropna()
    if len(x) < 5: return f"   {nm:<{w}} n={len(x)}"
    d = x[x.index < SPLIT] if isinstance(x.index, pd.DatetimeIndex) else x
    h = x[x.index >= SPLIT] if isinstance(x.index, pd.DatetimeIndex) else x
    pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():5.0f} PF {pf:4.2f} t {tstat(x):4.1f} win {np.mean(x > 0):.0%}"
            f" | design ${d.mean():5.0f} (n {len(d)}) holdout ${h.mean():5.0f} (n {len(h)})")


def build(g, Rg):
    cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    F = GX.features_for(g)
    rows = []; prev = None
    for d in g.trading:
        b = d * 1440
        if g.last_j[d] < jof(1500):
            continue
        p = {k: cf[b + jof(k)] for k in (900, 1400, 1430, 1500)}
        o = g.o[d, jof(831)]
        if prev is not None and np.isfinite(o):
            dt = pd.Timestamp(g.ts[d])
            ok = START <= dt <= END and Rg.A["present"][d, jof(1300):jof(1431)].any()     # that day's own gamma data
            reg30, dist30 = Rg.at(d, jof(1430)) if ok else ("n/a", np.nan)
            reg00, dist00 = Rg.at(d, jof(1400)) if ok else ("n/a", np.nan)
            rows.append(dict(date=dt, day=d, rod=p[1430] / prev - 1, rm=p[1430] / o - 1, rm14=p[1400] / o - 1,
                             rod14=p[1400] / prev - 1, l30=p[1500] - p[1430], l60=p[1500] - p[1400], ldf=p[1430] - p[1400],
                             reg30=reg30, dist30=dist30, reg00=reg00, dist00=dist00,
                             gneg=F.gex_neg.get(d, np.nan), grank=F.gex_rank.get(d, np.nan)))
        prev = cf[b + jof(1500)]
    return pd.DataFrame(rows).set_index("date")


def follow(T, sig, move):
    s = np.sign(T[sig]); return s * T[move] * PV - COST


def shuffle_diff(x, lab, a="below", b="above", n=1000, seed=5):
    rng = np.random.default_rng(seed); real = x[lab == a].mean() - x[lab == b].mean(); out = []
    L = lab.to_numpy()
    for _ in range(n):
        p = rng.permutation(L); out.append(x[p == a].mean() - x[p == b].mean())
    out = np.array(out); return real, np.mean(out >= real)


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    A = load_gex(g); Rg = Regime(g, A)
    T = build(g, Rg); T = T[T.index >= pd.Timestamp("2018-01-01")]
    G = T[(T.index >= START) & (T.index <= END) & (T.reg30 != "n/a")]
    print(f"sessions 2018-26: {len(T)}; with Bridge gamma: {len(G)} ({G.index[0].date()} .. {G.index[-1].date()});"
          f" regime at 14:30: {G.reg30.value_counts(normalize=True).round(2).to_dict()}")

    print("\n1. Last half-hour 14:30 -> 15:00, follow the day's move, by the 0DTE gamma regime at 14:30")
    for sig, nm in (("rod", "ROD (prev 15:00 close -> 14:30)"), ("rm", "session move (8:30 -> 14:30)")):
        x = follow(G, sig, "l30")
        print(line(x, f"follow {nm}, all"))
        for r in ("below", "above", "weak/none"):
            print(line(x[G.reg30 == r], f"   {r} the flip"))
        real, p = shuffle_diff(x, G.reg30)
        print(f"      below minus above ${real:.0f} a trade; shuffled-label placebo p = {p:.3f}")
        big = G[sig].abs() >= G[sig].abs().expanding(40).median().shift(1)
        print(line(x[(G.reg30 == "below") & big], "   below the flip and |move| above its running median"))
        print(line(x[(G.reg30 == "above") & big], "   above the flip and |move| above its running median"))
        print(line(-(x + COST) - COST, "   fade, all"))
        print(line((-(x + COST) - COST)[G.reg30 == "above"], "   fade above the flip (Barbon reversal)"))
    x = follow(G, "rod", "l30")
    print("   distance to the flip at 14:30 (price - flip) / price, follow ROD:")
    for lo, hi in ((-1, -0.01), (-0.01, -0.003), (-0.003, 0), (0, 0.003), (0.003, 0.01), (0.01, 1)):
        m = (G.dist30 >= lo) & (G.dist30 < hi)
        print(line(x[m], f"      {lo * 100:+.1f}% .. {hi * 100:+.1f}%"))
    # directional asymmetry: below the flip + falling day (dealers sell into the close) vs rising
    print(line(x[(G.reg30 == "below") & (G.rod < 0)], "   below the flip, day down (follow = short)"))
    print(line(x[(G.reg30 == "below") & (G.rod > 0)], "   below the flip, day up (follow = long)"))
    print(line(x[(G.reg30 == "above") & (G.rod < 0)], "   above the flip, day down (follow = short)"))
    print(line(x[(G.reg30 == "above") & (G.rod > 0)], "   above the flip, day up (follow = long)"))

    print("\n2. From 14:00: last hour (to 15:00) and the Late-Day Flow window (to 14:30), follow the 8:30 -> 14:00 move, regime at 14:00")
    for mv, nm in (("l60", "last hour 14:00 -> 15:00"), ("ldf", "14:00 -> 14:30 (LDF window, every day)")):
        x = follow(G, "rm14", mv)
        print(line(x, f"{nm}, all"))
        for r in ("below", "above", "weak/none"):
            print(line(x[G.reg00 == r], f"   {r} the flip"))
        real, p = shuffle_diff(x, G.reg00); print(f"      below minus above ${real:.0f}; placebo p = {p:.3f}")
    from time_clusters_test import trades as plan_trades
    P = plan_trades(g); ldf = P["LDF_MC"]; ldf = ldf[(ldf.date >= START) & (ldf.date <= END)].copy()
    reg = G.reg00.reindex(ldf.date.dt.normalize()).to_numpy(); ldf["reg"] = reg
    print("   Late-Day Flow MultiCharts trades by the regime at 14:00 (the same as analysis/gamma_regime_test.py, section 2):")
    for r in ("below", "above", "weak/none"):
        q = ldf[ldf.reg == r]; print(line(q.set_index("date").net, f"      LDF {r}"))
    # Late-Day Flow held to 15:00 when below the flip
    ext = ldf[(ldf.reg == "below")]
    add = []
    for rr in ext.itertuples():
        row = G.loc[rr.date.normalize()] if rr.date.normalize() in G.index else None
        if row is not None and rr.kind == 2: add.append(rr.side * row.l30 * PV)
    print(f"      holding LDF on to 15:00 when below the flip (time exits only): +${np.mean(add):.0f} gross a trade on {len(add)} trades (t {tstat(add):.1f})")

    print("\n3. SqueezeMetrics GEX (previous day), last half-hour follow ROD, 2018-2026")
    x = follow(T, "rod", "l30")
    for nm, m in (("all", T.grank.notna()), ("GEX < 0", T.gneg == True), ("GEX rank < 20%", T.grank < 0.2),
                  ("GEX rank 20-80%", (T.grank >= 0.2) & (T.grank < 0.8)), ("GEX rank >= 80%", T.grank >= 0.8)):
        q = x[m]; y = q.index.year; by = q.groupby(y).sum()
        print(line(q, f"   {nm}") + f" | years + {(by > 0).sum()}/{len(by)}")
    q = x[(T.grank >= 0.8)]; print(line(-(q + COST) - COST, "   fade after GEX rank >= 80% (reversal)"))
    fd = -(x + COST) - COST
    print("   fade ROD 14:30 -> 15:00 by year (all days): " + " | ".join(f"{y} ${v:.0f}" for y, v in fd.groupby(fd.index.year).mean().items()))
    both = (G.reg30 == "below") & (T.grank.reindex(G.index) < 0.2)
    print(line(follow(G, "rod", "l30")[both], "   Bridge below the flip AND SqueezeMetrics rank < 20%"))

    # metrics for the gamma-conditioned version, if any
    x = follow(G, "rod", "l30"); sel = x[G.reg30 == "below"]
    days = G.index
    dl = sel.reindex(days, fill_value=0.0)
    s_ = np.sign(G.rod)[G.reg30 == "below"]
    rows = {"follow ROD below the flip (2023-26)": (dl, sel), "  longs": (sel.where(s_ > 0, 0).reindex(days, fill_value=0.0), sel[s_ > 0]),
            "  shorts": (sel.where(s_ < 0, 0).reindex(days, fill_value=0.0), sel[s_ < 0])}
    print("\n" + M.table(rows))
    b_, p_ = R.report({"below the flip, holdout 2025-26": dl[dl.index >= SPLIT]}, n=3000); print(b_); print(p_)
    pickle.dump(dict(T=T, G=G), open(SP + "gamma_momentum.pkl", "wb"))
