"""Combine (Apex 50K challenge) with the gold Asian breakout added (user's request 2026-10-14).

Challenge simulator: analysis/portfolio.py (RULES: $3,000 target, $2,000 trailing MLL, $1,000 daily loss limit,
21 trading days), every start day 2018-2026 (and 2023+), real day order, intraday minute paths.
Combine set (HANDOFF): VB 8 MNQ + ONB ADX30 $1,100 risk + Bridge Monday Long 2 MNQ + EOS $500 risk (MultiCharts lists).
Gold (MGC = GC / 10): filter B version (fills before 02:00 CT), stop 1.0 x range; exits 12:00 (best R) and
breakeven + 3R target out 12:00 (fewest losses); fixed 1-5 MGC or risk-sized ($ risk / range $ per MGC).
Gold's own minute path (adverse excursion from gold's highs / lows) is placed on the NQ calendar row of the trade date
(entries 00:00-01:59, exits by 12:00 CT, so it shares the same Apex day).
  python3 analysis/combine_gold_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import asian_breakout_test as AB
import gold_asian_breakout_gc_test as GT
from gold_breakout_exit_test import manage
from portfolio import paths, challenge
from time_clusters_test import trades as plan_trades

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, COMM = 100.0, 7.25


def gold_paths(g, gc, t, qty):
    """(worst, real) $ arrays on the NQ grid for gold trades, qty MGC per trade (array or scalar)."""
    W = np.zeros(g.o.shape); Rr = np.zeros(g.o.shape)
    H, L = gc.h.ravel(), gc.l.ravel()
    row = pd.Series(np.arange(g.D), index=g.dates)
    q = np.broadcast_to(np.asarray(qty, float), (len(t),))
    for (r, qq) in zip(t.itertuples(), q):
        if qq <= 0: continue
        d = row.get(int(pd.Timestamp(r.date).strftime("%Y%m%d")))
        if d is None: continue
        j0, j1 = r.t0 - r.day * 1440, r.t1 - r.day * 1440
        seg = slice(r.t0, r.t1 + 1)
        adv = (L[seg] if r.side > 0 else H[seg])
        a = ((np.nan_to_num(adv, nan=r.entry) - r.entry) * r.side * PV - COMM) / 10 * qq
        a[-1] = min(a[-1], r.net / 10 * qq)
        W[d, j0:j1 + 1] += a; W[d, j1 + 1:] += r.net / 10 * qq; Rr[d, j1:] += r.net / 10 * qq
    return W, Rr


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); gc = GT.load_gc()
    T = plan_trades(g); atr = g.daily_atr(15); tr = g.trading; D = len(tr); yr = pd.DatetimeIndex(g.ts[tr]).year
    P = {}
    for nm in ("VB", "ONB_ADX30", "MON_BR", "EOS"):
        w, r = paths(g, T[nm]); P[nm] = (w[tr] / 10, r[tr] / 10)
    rk = lambda dl_, m: np.floor(dl_ / (np.nan_to_num(m * atr[tr], nan=1e12) * 2))[:, None]
    base_parts = [(P["VB"], 8), (P["ONB_ADX30"], rk(1100, 0.25)), (P["MON_BR"], 2), (P["EOS"], rk(500, 0.30))]
    W0 = sum(p[0] * q for p, q in base_parts); R0 = sum(p[1] * q for p, q in base_parts)

    base = AB.run(gc, "GC", exit_t=1200); base = base[(base.date >= pd.Timestamp("2018-01-01")) & ((base.t0 % 1440) // 60 < 2)].reset_index(drop=True)
    G = {"out 12:00": manage(gc, base, 1200, False, None), "BE + 3R, out 12:00": manage(gc, base, 1200, True, 3.0)}

    def run(W, Rr, label):
        res = [challenge(W, Rr, np.arange(s, min(s + 21, D))) for s in range(D)]
        o = np.array([np.nan if x is None else float(x[0] == "pass") for x in res])
        mll = np.array([np.nan if x is None else float(x[0] == "fail_mll") for x in res])
        nd = np.array([np.nan if x is None or x[0] != "pass" else x[1] for x in res])
        m18, m23 = yr >= 2018, yr >= 2023
        print(f"   {label:<44} pass {np.nanmean(o[m18]):.1%} | 2023-26 {np.nanmean(o[m23]):.1%} | MLL fail {np.nanmean(mll[m18]):.1%}"
              f" | median days to pass {np.nanmedian(nd[m18]):.0f}")
        return np.nanmean(o[m18]), np.nanmean(o[m23])

    print("\n1. Combine pass rates (every start day)")
    run(W0, R0, "current combine (VB 8 + ONB30 + BrMon 2 + EOS)")
    out = {}
    for gnm, t in G.items():
        for q in (1, 2, 3, 5):
            gw, gr = gold_paths(g, gc, t, q)
            out[(gnm, f"{q} MGC")] = run(W0 + gw[tr], R0 + gr[tr], f"+ gold {gnm}, {q} MGC")
        for risk in (100, 200, 300):
            q = np.floor(risk / (t.width.values * PV / 10))
            gw, gr = gold_paths(g, gc, t, q)
            out[(gnm, f"risk ${risk}")] = run(W0 + gw[tr], R0 + gr[tr], f"+ gold {gnm}, risk ${risk} (median {np.median(q):.0f} MGC)")
    print("\n2. Gold alone as a combine strategy (no NQ), risk-sized")
    for gnm, t in G.items():
        for risk in (200, 300, 500):
            q = np.floor(risk / (t.width.values * PV / 10)); gw, gr = gold_paths(g, gc, t, q)
            run(gw[tr], gr[tr], f"gold only {gnm}, risk ${risk}")
    print("\n3. Same-day overlap: gold trades also on NQ trade days (combine risk stacking)")
    gd = set(pd.to_datetime(G["out 12:00"].date).dt.normalize())
    for nm in ("VB", "ONB_ADX30", "MON_BR", "EOS"):
        d = set(T[nm].date.dt.normalize()); print(f"   {nm}: {len(d & gd) / max(1, len(d)):.0%} of its days also have a gold trade")
