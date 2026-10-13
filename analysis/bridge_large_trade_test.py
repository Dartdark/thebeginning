"""The Bridge's OFB_LargeTradePredictability_Signal, horizon-matched (user's paste), 2026-10-13.

At each bar close: Dir = +1 / -1 from the bar's colour (TestMode 1), its largest print if >= MinSize contracts
(2; signed: + bought, - sold), or both agreeing (3). Dir <> 0 -> be in that direction from the next bar's open
(an opposite signal flips; the same signal keeps the position); no signal -> out at the open after HoldBars.
Data: the Bridge's big_trade per minute (OF_1min_*.csv, 2018-2026 RTH) on the 1-minute grid, bars 8:31-15:00 CT
(positions are closed at the 15:00 open). Also on 5-minute bars (largest print of the 5 minutes).
Gross = before costs; net = $7.25 per round trip + 1 tick per market fill, per NQ.
  python3 analysis/bridge_large_trade_test.py [SCRATCH_DIR]
"""
import sys, glob, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25
HALF = COST / 2 + TICK * PV                     # one side: half the commission + 1 tick


def big_trades(g):
    d = pd.concat([pd.read_csv(f, usecols=["date", "time", "big_trade"]) for f in sorted(glob.glob("OF_1min_*.csv"))], ignore_index=True)
    row = np.minimum(np.searchsorted(g.dates, d.date.values), g.D - 1); ok = g.dates[row] == d.date.values
    B = np.full((g.D, 1440), np.nan); B[row[ok], jof(d.time.values[ok] - 100)] = d.big_trade.values[ok]
    return B


def run(g, B, mode=1, min_size=100, hold=1, k=1):
    """Per-day bar-by-bar position path on k-minute bars. Returns (trades, per-bar gross points, bars in market)."""
    ts = pd.DatetimeIndex(g.ts); a, z = jof(831), jof(1500)
    trades, gross_pts, nbars = [], 0.0, 0
    for d in g.trading:
        if ts[d].year < 2018 or np.isnan(B[d, a:z]).all(): continue
        cols = np.arange(a + k - 1, z + 1, k)                # bar closes
        o = np.array([g.o[d, j - k + 1] for j in cols]); c = g.c[d, cols]
        if k == 1: big = B[d, cols]
        else:
            seg = B[d, a:z + 1][: len(cols) * k].reshape(len(cols), k)
            idx = np.nanargmax(np.abs(np.nan_to_num(seg)), axis=1); big = seg[np.arange(len(cols)), idx]
        color = np.sign(c - o); prt = np.where(np.abs(np.nan_to_num(big)) >= min_size, np.sign(np.nan_to_num(big)), 0)
        if mode == 1: dirn = color
        elif mode == 2: dirn = prt
        else: dirn = np.where((color != 0) & (color == prt), color, 0)
        dirn = np.nan_to_num(dirn)
        pos = 0; since = 0; cur = None; n = len(cols)
        for i in range(n - 1):
            # decision at the close of bar i -> position during bar i+1 (enter/exit at its open)
            want = pos
            if dirn[i] != 0: want = int(dirn[i])
            elif pos != 0 and since >= hold - 1: want = 0
            px = o[i + 1]
            if np.isnan(px): continue
            if want != pos:
                if pos != 0:
                    cur["exit"] = px - pos * TICK; cur["j1"] = cols[i + 1] - k + 1
                    cur["net"] = (cur["exit"] - cur["entry"]) * pos * PV - COST; trades.append(cur); cur = None
                if want != 0:
                    cur = dict(day=d, date=ts[d], side=want, j0=cols[i + 1] - k + 1, entry=px + want * TICK, kind=2, slips=0, gross=0.0)
                    since = 0
                pos = want
            elif pos != 0:
                since = 0 if dirn[i] == pos else since + 1
            if pos != 0 and i + 2 < n and not np.isnan(o[i + 2]):
                gp = (o[i + 2] - o[i + 1]) * pos; gross_pts += gp; nbars += 1; cur["gross"] += gp * PV
        if pos != 0 and cur is not None:                     # out at the 15:00 bar's open
            px = o[-1] - pos * TICK; cur["exit"] = px; cur["j1"] = cols[-1] - k + 1
            cur["net"] = (px - cur["entry"]) * pos * PV - COST; trades.append(cur)
    return pd.DataFrame(trades), gross_pts, nbars


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); B = big_trades(g)
    print(__doc__.split("\n")[0])
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dl = lambda t: t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    res = {}
    for k in (1, 5):
        print(f"\n{k}-minute bars:")
        for mode, nm in ((1, "candle colour"), (2, "whale print >= 100"), (3, "both agree")):
            for ms in ((100,) if mode == 1 else (100, 200)):
                t, gp, nb = run(g, B, mode, ms, 1, k)
                if mode == 1 and ms != 100: continue
                x = t.net; y = t.date.dt.year
                gpb = gp / max(nb, 1)
                print(f"   {nm:<20} size>={ms:<4} trades {len(t):7d}  gross {gpb:+.3f} pts a bar in market ({nb} bars),"
                      f" gross per trade ${t.gross.mean():6.1f} | net per trade ${x.mean():6.1f} PF {x[x > 0].sum() / -x[x < 0].sum():.2f}"
                      f" t={x.mean() / x.std() * np.sqrt(len(x)):6.1f} | net 18-22 ${x[y < 2023].mean():6.1f} 23-26 ${x[y >= 2023].mean():6.1f}"
                      f" | L ${x[t.side > 0].mean():6.1f} S ${x[t.side < 0].mean():6.1f}")
                res[(k, mode, ms)] = t
    print("\n   (cost per round trip $17.25 = 0.86 points; a 1-minute NQ bar moves ~4-8 points)")
    print("\nStandard metrics per NQ (net):")
    rows = {f"{k}-min {['', 'candle', 'whale', 'both'][m]} {ms}": (dl(t), t.net) for (k, m, ms), t in res.items()}
    print(M.table(rows))
