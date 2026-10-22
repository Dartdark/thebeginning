"""BTC Momentum ("September Winner", user's MultiCharts file, 2026-10-13) and Bitcoin forced flows, on CME
Bitcoin futures 1-minute data (BTC_1min_<year>.csv, Dec 2018 - Oct 2026, CT).

Strategy: if the 8:00 -> 8:30 CT move is down, short at the end of the window and hold to the 15:00 close;
shorts only, no stop (defaults). As coded on a 5-minute chart the window is really 7:55 -> 8:25 (the bar
stamped 8:00 opens at 7:55). Both versions are tested, plus longs, stops, by year and by month.
Forced flows: (a) spot Bitcoin ETFs (since 11 Jan 2024) create / redeem against a ~15:00 CT benchmark:
follow the day's move in the last hour (Late-Day Flow logic) before vs after the ETFs; (b) CME Bitcoin
futures settle on the CF Bitcoin Reference Rate at 16:00 London on the last Friday of the month (10:00 CT
in winter, 10:00 CT in summer too since London and Chicago shift together): the 9:00 -> 10:00 window on
expiry Fridays vs other Fridays.
Costs per MBT (0.1 BTC, $0.10 a point, tick 5 points = $0.50): $2.50 a round trip + 1 tick per market / stop fill.
Results are shown per 10 MBT (= 1 BTC, $1 a point) to keep the numbers readable.
  python3 analysis/btc_momentum_test.py [SCRATCH_DIR]
"""
import sys, warnings, pickle, os; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import Grid24, jof
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV = 1.0                       # $ per point for 1 BTC = 10 MBT
TICK = 5.0
COST = 25.0                    # 10 MBT x $2.50
SLIP = TICK * PV               # 1 tick on 10 MBT = 10 x $0.50


_CF = {}


def last_px(G, d, j):
    """Last traded price at or before the close of column j on row d (bars are missing when nothing trades)."""
    if id(G) not in _CF: _CF[id(G)] = pd.DataFrame(G.c).ffill(axis=1).to_numpy()
    return _CF[id(G)][d, j]


def trade(G, d, j_in, side, j_out, stop_pct=None):
    o, h, l, c = G.o[d], G.h[d], G.l[d], G.c[d]
    while j_in <= j_out and np.isnan(o[j_in]): j_in += 1      # first trade after the signal
    if j_in > j_out: return None
    e = o[j_in]
    sp = e * (1 - side * stop_pct) if stop_pct else None
    for j in range(j_in, j_out + 1):
        if np.isnan(h[j]): continue
        if sp is not None and ((l[j] <= sp) if side > 0 else (h[j] >= sp)):
            px = (min(o[j], sp) if side > 0 else max(o[j], sp)) if j > j_in else sp
            return (px - e) * side * PV - COST - 2 * SLIP
    cc = c[j_in:j_out + 1]; ok = np.where(~np.isnan(cc))[0]
    if not len(ok): return None
    return (cc[ok[-1]] - e) * side * PV - COST - 2 * SLIP


def momentum(G, t0=800, t1=830, exit_t=1500, longs=False, shorts=True, stop_pct=None, rand=None, coded=False):
    ts = pd.DatetimeIndex(G.ts); rng = np.random.default_rng(rand) if rand is not None else None
    rows = []
    for d in G.trading:
        if ts[d].year < 2019: continue
        if coded:   # as coded on 5-min bars: open of the bar stamped 8:00 (7:55), close of the 8:25 bar, enter at that close
            a, b = jof(755), jof(825)
        else:
            a, b = jof(800), jof(830)
        op, cl = last_px(G, d, a), last_px(G, d, b)                 # price at 7:55 / 8:00 and at 8:25 / 8:30
        if np.isnan(op) or np.isnan(cl) or cl == op: continue
        side = 1 if cl > op else -1
        if side > 0 and not longs: continue
        if side < 0 and not shorts: continue
        if rng is not None: side = int(rng.choice([-1, 1]))
        x = trade(G, d, b + 1, side, jof(exit_t), stop_pct)
        if x is not None: rows.append(dict(date=ts[d], side=side, net=x))
    return pd.DataFrame(rows)


def line(t, nm, w=52):
    if len(t) < 3: return f"{nm:<{w}} n={len(t)}"
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); h = x[y >= 2023]
    pf = lambda q: q[q > 0].sum() / max(1e-9, -q[q < 0].sum())
    return (f"{nm:<{w}} n={len(x):4d} win {np.mean(x > 0):.0%} avg ${x.mean():6.0f} PF {pf(x):.2f}"
            f" t={x.mean() / x.std() * np.sqrt(len(x)):4.1f} yrs+ {(by > 0).sum()}/{len(by)} | 23+ ${h.mean():6.0f} PF {pf(h):.2f}")


if __name__ == "__main__":
    pk = SP + "gbtc.pkl"
    if os.path.exists(pk): G = pickle.load(open(pk, "rb"))
    else:
        G = Grid24("data/BTC_1min_20*.csv", night_pattern=""); pickle.dump(G, open(pk, "wb"), protocol=4)
    print(__doc__.split("\n")[0])
    ts = pd.DatetimeIndex(G.ts[G.trading])
    print(f"trading days {len(G.trading)}, {ts[0].date()} .. {ts[-1].date()}; per 1 BTC (= 10 MBT) after costs")
    have = np.mean(~np.isnan(G.c[G.trading][:, jof(800):jof(1500)]))
    print(f"share of 8:00-15:00 minutes with a trade: {have:.0%} (missing minutes = no trades; prices carried forward)")

    print("\n1. The strategy (shorts only, hold to 15:00, no stop):")
    coded = momentum(G, coded=True); doc = momentum(G)
    print(line(coded, "as coded (7:55 -> 8:25 window)")); print(line(doc, "as documented (8:00 -> 8:30)"))
    for nm, t in (("as coded", coded), ("as documented", doc)):
        print(f"   {nm} by year:", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
        print(f"   {nm} by month (avg):", t.groupby(t.date.dt.month).net.mean().round(0).astype(int).to_dict())
    print(line(momentum(G, longs=True, shorts=False), "longs only (morning up -> long)"))
    print(line(momentum(G, longs=True, shorts=True), "both sides"))
    for sp in (0.01, 0.02, 0.03):
        print(line(momentum(G, stop_pct=sp), f"shorts, stop {sp:.0%}"))
    for ex in (1000, 1200, 1400):
        print(line(momentum(G, exit_t=ex), f"shorts, exit {ex}"))
    pl = [momentum(G, rand=r).net.mean() for r in range(20)]
    print(f"   placebo (same days, random side, 20 runs): ${np.mean(pl):.0f} ({min(pl):.0f}..{max(pl):.0f}) vs ${doc.net.mean():.0f}")
    allday = momentum(G, longs=True, shorts=True)
    sh_every = []
    for d in G.trading:
        if pd.Timestamp(G.ts[d]).year < 2019: continue
        x = trade(G, d, jof(831), -1, jof(1500))
        if x is not None: sh_every.append(dict(date=pd.Timestamp(G.ts[d]), side=-1, net=x))
    print(line(pd.DataFrame(sh_every), "control: short EVERY day 8:31 -> 15:00"))

    print("\n2. Forced flow (a): last hour, follow the day's move (|0:00 -> 14:00| >= 1%), 14:01 -> 15:00:")
    rows = []
    for d in G.trading:
        o0, c14 = last_px(G, d, 0), last_px(G, d, jof(1400))
        if np.isnan(o0) or np.isnan(c14) or pd.Timestamp(G.ts[d]).year < 2019: continue
        mv = c14 / o0 - 1
        if abs(mv) < 0.01: continue
        x = trade(G, d, jof(1401), int(np.sign(mv)), jof(1500))
        if x is not None: rows.append(dict(date=pd.Timestamp(G.ts[d]), side=int(np.sign(mv)), net=x))
    lh = pd.DataFrame(rows)
    print(line(lh[lh.date < "2024-01-11"], "before spot ETFs (2019 - 10 Jan 2024)"))
    print(line(lh[lh.date >= "2024-01-11"], "with spot ETFs (11 Jan 2024 on)"))

    print("\n3. Forced flow (b): CME monthly settlement (last Friday, BRR at 16:00 London ~ 10:00 CT):")
    fr = ts[ts.dayofweek == 4]
    last_fri = pd.Series(fr).groupby([fr.year, fr.month]).max().to_numpy()
    for nm, days in (("expiry Fridays", last_fri), ("other Fridays", np.setdiff1d(fr.to_numpy(), last_fri))):
        mv = []
        for dd in days:
            d = np.searchsorted(G.dates, int(pd.Timestamp(dd).strftime("%Y%m%d")))
            a, b, c_ = last_px(G, d, jof(900)), last_px(G, d, jof(1000)), last_px(G, d, jof(1100))
            if np.isnan(a) or np.isnan(b) or np.isnan(c_): continue
            mv.append((b / a - 1, c_ / b - 1))
        mv = np.array(mv)
        print(f"   {nm:<15} n={len(mv):3d}: 9:00->10:00 mean {mv[:, 0].mean():+.3%} |abs| {np.abs(mv[:, 0]).mean():.3%};"
              f" 10:00->11:00 mean {mv[:, 1].mean():+.3%}; reversal corr {np.corrcoef(mv[:, 0], mv[:, 1])[0, 1]:+.2f}")
