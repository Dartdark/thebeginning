"""Twin-like strategies, round 1 (user's request, 2026-10-15: 'a great edge that trades a lot', but Apex-shaped).
A  Transfer test: Twin Continuation with its exact default settings on ES, YM, GC, CL (and NQ as the reference), no tuning.
   The only translation: Morning Momentum's 75-point NQ stop becomes k x 15-day daily ATR, k = 75 / NQ's median daily ATR
   2018-26 (same fraction of a normal day in every market; NQ rerun with it too). Session 17:00-16:00 CT, MO window
   8:40-9:30 CT and every other input unchanged. Costs: ES $5 + 1 tick, others $7.25 + 1 tick per market / stop fill.
   Per market: whole / BO / MO, longs / shorts, 2018-22 vs 2023-26, % of price; random-side placebo (10 runs) where t >= 2.
B  Correlation of the markets' daily P&L (in % of price) -- a second stream only helps if it is not NQ again.
  python3 analysis/twin_family_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import twin_continuation_test as tc
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MK = {"NQ": ("g24.pkl", 20.0, 0.25, 7.25), "ES": ("ge.pkl", 50.0, 0.25, 5.0), "YM": ("gy.pkl", 5.0, 1.0, 7.25),
      "GC": ("gc.pkl", 100.0, 0.10, 7.25), "CL": ("cl.pkl", 1000.0, 0.01, 7.25)}


def load(sym):
    g = pickle.load(open(SP + MK[sym][0], "rb")); B = tc.flatten(g); B["atr"] = g.daily_atr(15)[B["row"]]; return g, B


def stats(x, nm, w=22):
    x = x.dropna(); y = x.index.year; by = x.groupby(y).sum(); t = x.mean() / x.std() * np.sqrt(len(x))
    pf = x[x > 0].sum() / max(1e-12, -x[x < 0].sum())
    return (f"   {nm:<{w}} n {len(x):5d} avg {x.mean():+.3f}% PF {pf:4.2f} t {t:5.2f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 2018-22 {x[y < 2023].mean():+.3f}% 2023-26 {x[y >= 2023].mean():+.3f}%"), t


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g, B = load("NQ"); a = pd.Series(g.daily_atr(15)[g.trading], index=pd.DatetimeIndex(g.ts[g.trading]))
    k = 75.0 / a["2018":].median(); print(f"\nNQ median 15-day ATR 2018-26 {a['2018':].median():.0f} pts -> MO stop k = {k:.3f} x ATR")
    daily = {}
    for sym, (_, pv, tick, comm) in MK.items():
        if sym != "NQ": g, B = load(sym)
        T = tc.simulate(B, pv=pv, tick=tick, comm=comm, mo_stop_atr=k); T = T[T.date >= "2018-01-01"].reset_index(drop=True)
        T.to_pickle(SP + f"twin_family_{sym}.pkl"); X = T.set_index("date")
        print(f"\n{sym}: {len(T)} trades, $ per contract avg ${X.net.mean():.0f} (repo costs), ${X.net.groupby(X.index.year).sum().mean():,.0f} a year")
        s, t_all = stats(X.pct, "ALL (% of price)"); print(s)
        for st in ("BO", "MO"):
            for sd, sn in ((0, ""), (1, " longs"), (-1, " shorts")):
                x = X[(X.setup == st) & ((X.side == sd) if sd else True)].pct
                if len(x) > 10: print(stats(x, f"{st}{sn}")[0])
        days = pd.bdate_range("2018-01-01", X.index.max())
        dd = X.net.groupby(level=0).sum().reindex(days, fill_value=0.0)
        print("   " + M.table({sym: (dd, X.net)}).split("\n")[1])
        daily[sym] = X.pct.groupby(level=0).sum().reindex(days, fill_value=0.0)
        if t_all >= 2:
            pl = []
            for s_ in range(10):
                P = tc.simulate(B, pv=pv, tick=tick, comm=comm, mo_stop_atr=k, placebo_rng=np.random.default_rng(200 + s_))
                pl.append(P[P.date >= "2018-01-01"].pct.mean())
            print(f"   placebo (random side, 10 runs): mean {np.mean(pl):+.3f}%, max {np.max(pl):+.3f}% vs real {X.pct.mean():+.3f}%; share >= real {np.mean(np.array(pl) >= X.pct.mean()):.1f}")
    print("\nB. Daily P&L correlation (% of price):")
    print(pd.DataFrame(daily).corr().round(2).to_string())
