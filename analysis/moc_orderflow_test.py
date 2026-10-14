"""MOC auction follow x order flow (The Bridge MBO, NQ), 2026-10-14 (user: "don't I have order-flow data").

The MOC follow (watchlist #10; analysis/moc_london_close_test.py): after a >= 0.3 ATR 14:00 -> 14:50 CT move, follow it
14:51 -> 15:00, stop 0.25 ATR: $263 a trade, t 3.1, placebo clean, but only $54 a trade in 2023-26. If closing-auction
imbalances (published from 14:50 CT) drive the last ten minutes, aggressive flow before / at 14:50 should say which
days carry the move. Order flow from OF_1min_*.csv (RTH 8:30-15:15 CT, 2018-01 .. 2026-07; loader from
analysis/orderflow_test.py). Pre-registered, decided at the 14:50 close:
  1. Mechanism check (not tradeable): is the 14:51-15:00 move accompanied by aggressive flow in its direction?
  2. Every day: do the 14:30-14:50 delta, the 14:50-bar delta and the 14:50 book imbalance predict 14:51 -> 15:00
     (correlations, design 2018-22 vs holdout 2023-26), beyond the price move?
  3. The MOC trades split by whether the 14:00-14:50 delta and the 14:40-14:50 delta agree with the trade side.
     Costs $7.25 + 1 tick per fill, per NQ.
  python3 analysis/moc_orderflow_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from orderflow_test import load_of
from s_rank_cl_round1_test import tstat

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPLIT = pd.Timestamp("2023-01-01")


def line(x, nm, w=62):
    x = pd.Series(x).dropna(); y = x.index.year
    if len(x) < 8: return f"   {nm:<{w}} n={len(x)}"
    pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():6.0f} PF {pf:4.2f} t {tstat(x):4.1f} win {np.mean(x > 0):.0%}"
            f" | 18-22 ${x[y < 2023].mean():6.0f} (t {tstat(x[y < 2023]):4.1f}) 23-26 ${x[y >= 2023].mean():6.0f} (t {tstat(x[y >= 2023]):4.1f})")


if __name__ == "__main__":
    pd.set_option("display.width", 230)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); A = load_of(g)
    tr = g.trading[pd.DatetimeIndex(g.ts[g.trading]) >= "2018-01-01"]
    has = A["has"][tr, jof(1450)] & A["has"][tr, jof(1500)]
    tr = tr[has]; idx = pd.DatetimeIndex(g.ts[tr]); atr = g.daily_atr(15)[tr]
    cf = pd.Series(g.c.ravel()).ffill().to_numpy(); P = lambda t: cf[tr * 1440 + jof(t)]
    dsum = lambda a, b: np.nansum(A["delta"][tr, jof(a):jof(b) + 1], 1)
    vsum = lambda a, b: np.nansum(A["tot"][tr, jof(a):jof(b) + 1], 1)
    print(f"days with order flow at 14:50-15:00: {len(tr)} ({idx[0].date()} .. {idx[-1].date()})")
    nxt = (P(1500) - P(1450)) / atr
    S = pd.DataFrame({"mv_1400": (P(1450) - P(1400)) / atr, "nxt": nxt,
                      "d_1400": dsum(1401, 1450) / np.maximum(vsum(1401, 1450), 1), "d_1430": dsum(1431, 1450) / np.maximum(vsum(1431, 1450), 1),
                      "d_1450bar": dsum(1450, 1450) / np.maximum(vsum(1450, 1450), 1), "imb_1450": A["simb"][tr, jof(1450)],
                      "d_after": dsum(1451, 1500) / np.maximum(vsum(1451, 1500), 1)}, index=idx)
    y = S.index.year
    print("\n1. Mechanism: 14:51-15:00 delta (share of volume) vs the 14:51-15:00 move")
    print(f"   corr {S.d_after.corr(S.nxt):.2f} (18-22 {S[y < 2023].d_after.corr(S[y < 2023].nxt):.2f}, 23-26 {S[y >= 2023].d_after.corr(S[y >= 2023].nxt):.2f}); "
          f"on MOC days (|14:00-14:50| >= 0.3 ATR) the after-delta agrees with the trade side {np.mean(np.sign(S.d_after) == np.sign(S.mv_1400))[()] if False else np.mean((np.sign(S.d_after) == np.sign(S.mv_1400))[S.mv_1400.abs() >= 0.3]):.0%}")
    print("\n2. Every day: predictors of the 14:51-15:00 move (correlation; partial = after the 14:00-14:50 price move)")
    for f in ("mv_1400", "d_1400", "d_1430", "d_1450bar", "imb_1450"):
        rows = []
        for nm, m in (("all", np.ones(len(S), bool)), ("18-22", y < 2023), ("23-26", y >= 2023)):
            s = S[m].dropna(subset=[f, "nxt", "mv_1400"])
            c = s[f].corr(s.nxt)
            if f != "mv_1400":
                X = np.c_[np.ones(len(s)), s.mv_1400, s[f]]; b, *_ = np.linalg.lstsq(X, s.nxt, rcond=None)
                r = s.nxt - X @ b; se = np.sqrt(np.diag(np.linalg.inv(X.T @ X)) * r.var()); pt = b[2] / se[2]
            else: pt = np.nan
            rows.append(f"{nm} corr {c:+.3f} (partial t {pt:+.1f})")
        print(f"   {f:<10} " + " | ".join(rows))

    print("\n3. MOC trades (>= 0.3 ATR, stop 0.25) split by order flow agreement")
    t = pickle.load(open(SP + "moc_london.pkl", "rb"))["moc"]
    t = t[t.date.isin(idx)].copy(); t.index = pd.DatetimeIndex(t.date)
    F = S.reindex(t.index)
    print(line(t.net, "MOC trades with order-flow data"))
    for f in ("d_1400", "d_1430", "d_1450bar", "imb_1450"):
        agree = np.sign(F[f]).to_numpy() == t.side.to_numpy()
        print(line(t.net[agree], f"{f} agrees with the trade"))
        print(line(t.net[~agree], f"{f} disagrees"))
