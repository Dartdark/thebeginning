"""High-win-rate search, round 3 (user's request, 2026-10-15): Apex needs frequent trades with a HIGH win rate and a small fixed
loss (round 2 showed low-win trend-day capture loses to losing streaks under the $2,000 trail). Pre-registered, 9 variants:
  entries (known directional edges)
    E1  Twin's Morning Momentum signal (breakout leg off), market entry next bar (378 signals 2018-26)
    E2  same signal, limit at the session VWAP until 11:00 CT (round 2 'V1' fills)
    E3  Twin's swing-breakout entries (stop entries at open 6h swing levels), only those filled 8:30-14:30 CT
  exits, in fractions of the 15-day daily ATR (known before the day): target / stop = 0.05 / 0.10, 0.10 / 0.20, 0.15 / 0.30;
      otherwise out at the 14:51 open (E1, E2) or the 15:45 close (E3); stop checked before target on the same bar;
      exits start the bar after the entry. Costs $7.25 + 1 tick per market / stop fill, limit target no slip.
Pass: t >= t_threshold(N items) (or DSR >= 0.95), random-side placebo p < 0.05, both halves positive. Also: the win rate the
exit shape alone gives (random-side placebo win rate) vs the real one.
  python3 analysis/high_winrate_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import twin_continuation_test as tc
from mo_pullback_test import run
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 20.0, 0.25, 7.25
EXITS = ((0.05, 0.10), (0.10, 0.20), (0.15, 0.30))


def exits(g, E, tgt, stp, sides=None):
    atr = g.daily_atr(15); out = []
    for k, e in enumerate(E.itertuples()):
        a = atr[e.row]; side = e.side if sides is None else sides[k]
        if not np.isfinite(a): continue
        T, S = e.entry + side * tgt * a, e.entry - side * stp * a; h, l, o, c = g.h[e.row], g.l[e.row], g.o[e.row], g.c[e.row]
        px = None
        for j in range(e.ej + 1, e.jx + 1):
            if np.isnan(c[j]): continue
            if j == e.jx and e.xmode == "open": px, kind = o[j], 2; break
            if (side > 0 and l[j] <= S) or (side < 0 and h[j] >= S): px, kind = (min(o[j], S) if side > 0 else max(o[j], S)), 0; break
            if (side > 0 and h[j] >= T) or (side < 0 and l[j] <= T): px, kind = (max(o[j], T) if side > 0 else min(o[j], T)), 1; break
            if j == e.jx: px, kind = c[j], 2; break
        if px is None:
            last = np.where(~np.isnan(c[:e.jx + 1]))[0]; px, kind = c[last[-1]], 2
        slips = e.slip_in + (0 if kind == 1 else 1)
        out.append(dict(date=pd.Timestamp(g.ts[e.row]), side=side, net=(px - e.entry) * side * PV - COMM - slips * TICK * PV, kind=kind,
                        row=e.row, ej=e.ej, xj=j if px is not None else e.jx, entry=e.entry, exit=px))
    return pd.DataFrame(out).set_index("date")


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); B = tc.flatten(g)
    T = tc.simulate(B, use_bo=False); T = T[T.setup == "MO"]
    sig = pd.DataFrame({"row": B["row"][T.sig_i.to_numpy()], "j": B["j"][T.sig_i.to_numpy()], "side": T.side.to_numpy(), "piv": T.piv.to_numpy()})
    sig = sig[pd.DatetimeIndex(g.ts[sig.row]) >= "2018-01-01"].reset_index(drop=True)
    E = {}
    e1 = sig.assign(ej=sig.j + 1); e1["entry"] = g.o[e1.row, e1.ej]; e1 = e1.dropna(subset=["entry"])
    E["E1"] = e1.assign(jx=jof(1451), xmode="open", slip_in=1)
    v1 = run(g, sig, "V1"); E["E2"] = v1.reset_index(drop=True).assign(jx=jof(1451), xmode="open", slip_in=0)[["row", "ej", "entry", "side", "jx", "xmode", "slip_in"]]
    TB = pd.read_pickle(SP + "twin_trades.pkl"); TB = TB[TB.setup == "BO"]
    rows, js = B["row"][TB.i0.to_numpy()], B["j"][TB.i0.to_numpy()]
    e3 = pd.DataFrame({"row": rows, "ej": js, "entry": TB.entry.to_numpy(), "side": TB.side.to_numpy()})
    e3 = e3[(e3.ej >= jof(830)) & (e3.ej <= jof(1430))]
    E["E3"] = e3.assign(jx=jof(1545), xmode="close", slip_in=1)
    N = len(pd.read_csv("TRIALS.csv")) + 1; thr = M.t_threshold(N); res = {}
    print(f"\nN items {N} -> t threshold {thr:.2f}\n")
    for en, Ed in E.items():
        Ed = Ed.reset_index(drop=True)
        for tg, st in EXITS:
            X = exits(g, Ed, tg, st); x = X.net; y = x.index.year
            t = x.mean() / x.std() * np.sqrt(len(x)); pf = x[x > 0].sum() / -x[x < 0].sum()
            rng = np.random.default_rng(11); pl, pw = [], []
            for _ in range(100):
                P = exits(g, Ed, tg, st, sides=rng.choice([-1, 1], len(Ed))); pl.append(P.net.mean()); pw.append((P.net > 0).mean())
            p = np.mean(np.array(pl) >= x.mean())
            ok = t >= thr and p < 0.05 and x[y < 2023].mean() > 0 and x[y >= 2023].mean() > 0
            res[(en, tg, st)] = X
            print(f"   {en} T {tg:.2f} / S {st:.2f}: n {len(x):4d} avg ${x.mean():6.1f} PF {pf:4.2f} t {t:5.2f} win {np.mean(x > 0):.0%} (shape-only {np.mean(pw):.0%})"
                  f" yrs+ {(x.groupby(y).sum() > 0).sum()}/{len(set(y))} | 2018-22 ${x[y < 2023].mean():6.1f} 2023-26 ${x[y >= 2023].mean():6.1f}"
                  f" | placebo ${np.mean(pl):6.1f} p {p:.2f} | {'PASS' if ok else '-'}", flush=True)
    best = max(res, key=lambda k: res[k].net.mean() / res[k].net.std() * np.sqrt(len(res[k])))
    X = res[best]; days = pd.bdate_range("2018-01-01", X.index.max()); rows_ = {}
    for nm, x in ((f"{best}", X.net), ("longs", X[X.side == 1].net), ("shorts", X[X.side == -1].net)):
        rows_[str(nm)] = (x.groupby(level=0).sum().reindex(days, fill_value=0.0), x)
    print(f"\nStandard metrics, best by t {best} (per NQ):"); print(M.table(rows_))
    b_, p_ = R.report({k: v[0][v[0].index >= "2023"] for k, v in rows_.items()}, n=2000); print("2023+ bootstrap:\n" + b_ + "\n2023+ drawdown permutation:\n" + p_)
    pickle.dump(res, open(SP + "high_winrate_res.pkl", "wb"))
