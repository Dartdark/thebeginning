"""Leveraged-ETF rebalance trade (2026-10-12, from analysis/forced_flows3_test.py).
Mechanism: daily-reset leveraged/inverse ETFs (TQQQ, SQQQ, QLD, SSO, UPRO, SPXU...) must trade
L(L-1) x AUM x the day's return near the close, in the direction of the day's move, so big-move
days get one-way flow late in the session (Cheng & Madhavan 2009; Shum et al. 2016).
Trade: at 14:00 CT, if the 8:30 -> 14:00 move is at least K x the 15-day ATR, enter in its
direction at the 14:00 open... (the next 1-minute bar), stop S x ATR, exit at the 15:00 close.
Per NQ after $7.25 + 1 tick per market/stop fill."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, resampling as R
SP = "/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
g = pickle.load(open(SP + "g24.pkl", "rb")); es = pickle.load(open(SP + "ge.pkl", "rb"))
TICK = 0.25


def trades(G, k=0.4, stop=0.15, j_sig=840, j_exit=900, pv=20.0, cost=7.25, rand=None, pct=None):
    atr = G.daily_atr(15); ts = pd.DatetimeIndex(G.ts); rows = []
    rng = np.random.default_rng(rand) if rand is not None else None
    for d in G.trading:
        if ts[d].year < 2018 or np.isnan(atr[d]): continue
        o0, cs = G.o[d, 511], G.c[d, j_sig]
        if np.isnan(o0) or np.isnan(cs) or np.isnan(G.c[d, j_exit]): continue
        mv = cs - o0
        big = abs(mv) >= (pct / 100 * o0 if pct else k * atr[d])
        if not big: continue
        side = int(np.sign(mv)) if rng is None else int(rng.choice([-1, 1]))
        j0 = j_sig + 1; e = G.o[d, j0] + side * TICK; sl = e - side * stop * atr[d]
        px, j1 = None, j_exit
        for j in range(j0, j_exit + 1):
            if np.isnan(G.c[d, j]): continue
            if (G.l[d, j] <= sl) if side > 0 else (G.h[d, j] >= sl):
                px = (min(G.o[d, j], sl) if side > 0 else max(G.o[d, j], sl)) - side * TICK; j1 = j; break
        if px is None: px = G.c[d, j_exit] - side * TICK
        rows.append(dict(day=d, j0=j0, j1=j1, side=side, entry=e, exit=px, kind=0, pnl=(px - e) * side * pv,
                         net=(px - e) * side * pv - cost, date=ts[d], slips=0, stop_pts=stop * atr[d]))
    return pd.DataFrame(rows)


def line(t, name):
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); h = x[y >= 2023]; d_ = x[y <= 2022]
    pf = lambda s: s[s > 0].sum() / max(1e-9, -s[s < 0].sum())
    return (f"{name:<40} n={len(x):4d} win {np.mean(x>0):.0%} avg ${x.mean():4.0f} PF {pf(x):.2f} t={x.mean()/x.std()*np.sqrt(len(x)):4.1f}"
            f" yrs+ {(by>0).sum()}/{len(by)} | 18-22 ${d_.mean():4.0f} PF {pf(d_):.2f} | 23+ ${h.mean():4.0f} PF {pf(h):.2f}"
            f" | L ${x[t.side>0].mean():4.0f} S ${x[t.side<0].mean():4.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    print("\nThreshold (x ATR) x stop (x ATR), signal 14:00, exit 15:00, NQ:")
    for k in (0.3, 0.4, 0.5, 0.6):
        for st in (0.1, 0.15, 0.25, 0):
            print(line(trades(g, k, st if st else 50), f"move >= {k} ATR, stop {st if st else 'none'} ATR"))
    print("\nSignal time (move >= 0.4 ATR, stop 0.15 ATR):")
    for js, nm in ((780, "13:00"), (810, "13:30"), (840, "14:00"), (855, "14:15")):
        print(line(trades(g, 0.4, 0.15, j_sig=js), f"signal {nm}, exit 15:00"))
    print(line(trades(g, 0.4, 0.15, j_exit=870), "signal 14:00, exit 14:30"))
    print("\nES (point value $50, $5 costs):")
    print(line(trades(es, 0.4, 0.15, pv=50.0, cost=5.0), "ES move >= 0.4 ATR, stop 0.15 ATR"))
    print("\nPlacebo: same days and stop, random side (20 runs):")
    t = trades(g, 0.4, 0.15)
    pl = [trades(g, 0.4, 0.15, rand=r).net.mean() for r in range(20)]
    print(f"  real ${t.net.mean():.0f} vs random-side mean ${np.mean(pl):.0f} (range ${min(pl):.0f}..${max(pl):.0f})")
    t.to_pickle(SP + "letf_trades.pkl")
