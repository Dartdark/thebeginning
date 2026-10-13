"""20/50 EMA zone pullback (user spec, 2026-10-13), NQ 10-minute bars.

Long: EMA20 > EMA50, the bar's low touches or overlaps the zone (low <= upper boundary = EMA20) and the
bar closes above the upper boundary; optional confirmation: the bar is bullish (close > open), or the
NEXT bar is bullish. Short: the mirror image. No position open -> enter at the next bar's open.
Stop 30 points, target 65 points from the entry, filled intrabar (stop first if both in one minute).
Apex: flat by 15:55 CT.
Modes: RTH   entries 8:40-14:30 CT, flat 15:00
       24h   entries any time except 15:45-17:00 CT, flat 15:55 CT (positions held overnight
             inside one Apex day, 17:00 -> 15:55)
Stops: fixed 30 / 65 points (as specified) or scaled to price (30 / 65 at NQ 25,000, i.e. 0.12% / 0.26%).
Per NQ after $7.25 + 1 tick per market/stop fill (target is a limit, no slippage), 2018-2026.
  python3 analysis/ema_zone_pullback_test.py [SCRATCH_DIR]
"""
import sys, warnings, pickle, itertools; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from bollinger_reversal_test import bar_series
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25


def signals(s, confirm="same"):
    e20 = s.c.ewm(span=20, adjust=False).mean(); e50 = s.c.ewm(span=50, adjust=False).mean()
    up_, lo_ = np.maximum(e20, e50), np.minimum(e20, e50)
    bull, bear = s.c > s.o, s.c < s.o
    L = (e20 > e50) & (s.l <= up_) & (s.c > up_)
    S = (e20 < e50) & (s.h >= lo_) & (s.c < lo_)
    if confirm == "same":
        L &= bull; S &= bear
    side = np.where(L, 1, np.where(S, -1, 0))
    if confirm == "next":                       # the following bar must close in the trade's direction
        nb, ns = bull.shift(-1, fill_value=False).to_numpy(), bear.shift(-1, fill_value=False).to_numpy()
        side = np.where((side == 1) & nb, 1, np.where((side == -1) & ns, -1, 0))
        side = np.r_[0, side[:-1]]              # signal is known at the close of the next bar
    trend = np.where(e20 > e50, 1, -1)
    return side, trend


class Flat:
    def __init__(self, g):
        self.O, self.H, self.L, self.C = (getattr(g, a).ravel() for a in "ohlc")
        self.N = len(self.C); self.ts = pd.DatetimeIndex(g.ts)


def sim(F, t0, side, sl, tp, mode):
    """Enter at the open of flat minute t0; returns (t1, entry, exit, kind) or None."""
    e = F.O[t0]
    if np.isnan(e): return None
    e += side * TICK
    stop, tgt = e - side * sl, e + side * tp
    flat_col = 900 if mode == "RTH" else 955
    t = t0
    while t < F.N:
        col = t % 1440
        if not np.isnan(F.H[t]):
            if (F.L[t] <= stop) if side > 0 else (F.H[t] >= stop):
                px = (min(F.O[t], stop) if side > 0 else max(F.O[t], stop)) if t > t0 else stop
                return t, e, px - side * TICK, 0
            if (F.H[t] >= tgt) if side > 0 else (F.L[t] <= tgt):
                return t, e, (max(F.O[t], tgt) if side > 0 else min(F.O[t], tgt)) if t > t0 else tgt, 1
            if col >= flat_col and col < 1020:
                return t, e, F.C[t] - side * TICK, 0
        t += 1
    return None


def run(g, F, s, side, mode="24h", scale=False, rand=None, trend=None):
    rng = np.random.default_rng(rand) if rand is not None else None
    rows_, cols = s.row.to_numpy(), s.col.to_numpy()
    price = s.c.to_numpy()
    out = []; busy = -1
    idx = np.where(side != 0)[0]
    if rng is not None:                          # placebo: same number of entries at random eligible bars
        elig = np.where(np.isin(cols, cols[idx]))[0]
        idx = np.sort(rng.choice(elig, len(idx), replace=False))
    for i in idx:
        d, j = int(rows_[i]), int(cols[i])
        if F.ts[d].year < 2018: continue
        hh = (j // 60) * 100 + j % 60
        if mode == "RTH" and not (840 <= hh <= 1430): continue
        if mode == "24h" and 1545 <= hh < 1700: continue
        t0 = d * 1440 + j + 1
        if t0 <= busy: continue
        sd = int(side[i]) if rng is None else (int(trend[i]) if trend is not None else int(rng.choice([-1, 1])))
        k = price[i] / 25000.0 if scale else 1.0
        r = sim(F, t0, sd, 30 * k, 65 * k, mode)
        if r is None: continue
        t1, e, px, kind = r
        out.append(dict(t0=t0, t1=t1, side=sd, entry=e, exit=px, kind=kind, net=(px - e) * sd * PV - COST,
                        date=F.ts[t0 // 1440], exit_date=F.ts[t1 // 1440]))
        busy = t1
    return pd.DataFrame(out)


def line(t, nm, w=46):
    if len(t) == 0: return f"{nm:<{w}} n=0"
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); h = x[y >= 2023]
    pf = lambda q: q[q > 0].sum() / max(1e-9, -q[q < 0].sum())
    L, S = x[t.side > 0], x[t.side < 0]
    return (f"{nm:<{w}} n={len(x):5d} win {np.mean(x > 0):.0%} avg ${x.mean():5.0f} PF {pf(x):.2f}"
            f" t={x.mean() / x.std() * np.sqrt(len(x)):5.1f} yrs+ {(by > 0).sum()}/{len(by)} | 23+ ${h.mean():5.0f} PF {pf(h):.2f}"
            f" | L ${L.mean():4.0f} PF {pf(L):.2f} S ${S.mean():4.0f} PF {pf(S):.2f}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); F = Flat(g)
    s = bar_series(g, 10)
    print(__doc__.split("\n")[0])
    print("\n1. As specified and variants (per NQ):")
    res = {}
    for confirm, mode, scale in itertools.product(("same", "next", "off"), ("24h", "RTH"), (False, True)):
        side, trend = signals(s, confirm)
        t = run(g, F, s, side, mode, scale)
        nm = f"confirm {confirm:<4} {mode:<3} {'scaled' if scale else '30/65 pts'}"
        res[nm] = t; print(line(t, nm))
    base = res["confirm same 24h 30/65 pts"]
    print("\n2. As specified (confirm same bar, 24h, 30/65 points), by year:")
    print("   ", base.groupby(base.date.dt.year).net.agg(["count", "sum", "mean"]).round(0).astype(int).T.to_string())
    print(f"   exits: target {np.mean(base.kind == 1):.0%}, stop / time {np.mean(base.kind == 0):.0%};"
          f" trades held past midnight {np.mean(base.date != base.exit_date):.0%}")
    side, trend = signals(s, "same")
    pl_t = [run(g, F, s, side, "24h", False, rand=r, trend=trend).net.mean() for r in range(10)]
    pl_r = [run(g, F, s, side, "24h", False, rand=100 + r).net.mean() for r in range(10)]
    print(f"   placebo, same number of entries at random 10-min closes (10 runs each):")
    print(f"     side = EMA trend: ${np.mean(pl_t):.0f} ({min(pl_t):.0f}..{max(pl_t):.0f}); random side: ${np.mean(pl_r):.0f}"
          f" ({min(pl_r):.0f}..{max(pl_r):.0f}); real ${base.net.mean():.0f}")
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dl = lambda t: t.groupby(t.exit_date).net.sum().reindex(days, fill_value=0.0)
    rows = {"as specified": (dl(base), base.net), "  longs": (dl(base[base.side > 0]), base.net[base.side > 0]),
            "  shorts": (dl(base[base.side < 0]), base.net[base.side < 0])}
    best_nm = max(res, key=lambda k: res[k].net.mean() / res[k].net.std() * np.sqrt(len(res[k])) if len(res[k]) > 1 else -9)
    rows[f"best: {best_nm}"] = (dl(res[best_nm]), res[best_nm].net)
    print("\n3. Standard metrics per NQ, 2018-26:"); print(M.table(rows))
    b = res[best_nm]; b23 = b[b.date.dt.year >= 2023]
    Bt, Pm = R.report({f"best 2023-26": dl(b23)[lambda x: x.index.year >= 2023], "as specified 2023-26":
                       dl(base[base.date.dt.year >= 2023])[lambda x: x.index.year >= 2023]}, n=2000)
    print(Bt)
