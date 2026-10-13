"""The Bridge's OFB_LiquidityPredictability_SIG: does resting-book imbalance predict the next bar? (user's paste), 2026-10-13.

Imbalance % = (bid depth - ask depth) / (bid + ask) x 100 over the top N levels (the Bridge's s48-s53 from
OF_1min_*.csv: 10 / 20 / 50 levels). At each bar close: Dir from the candle (TestMode 1), the book (2: >= +Threshold
long, <= -Threshold short) or both agreeing (3); enter next bar at market, exit after exactly HoldBars = 1 bar (every
signal bar is its own round trip). 1- and 5-minute bars, 8:31-15:00 CT, 2018-2026.
Gross = points per trade before costs; net = $7.25 + 1 tick per market fill (2 fills), per NQ.
  python3 analysis/bridge_liquidity_test.py [SCRATCH_DIR]
"""
import sys, glob, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25
LV = {10: ("s48", "s49"), 20: ("s50", "s51"), 50: ("s52", "s53")}

if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    d = pd.concat([pd.read_csv(f, usecols=["date", "time", "s48", "s49", "s50", "s51", "s52", "s53"]) for f in sorted(glob.glob("OF_1min_*.csv"))],
                  ignore_index=True)
    row = np.minimum(np.searchsorted(g.dates, d.date.values), g.D - 1); ok = g.dates[row] == d.date.values
    d, row = d[ok], row[ok]; col = jof(d.time.values - 100)
    IMB = {}
    for n, (b, a) in LV.items():
        x = np.full((g.D, 1440), np.nan); bb, aa = d[b].to_numpy(float), d[a].to_numpy(float)
        with np.errstate(all="ignore"): x[row, col] = np.where(bb + aa > 0, (bb - aa) / (bb + aa) * 100, np.nan)
        IMB[n] = x
    ts = pd.DatetimeIndex(g.ts); rows = [r for r in g.trading if ts[r].year >= 2018 and not np.isnan(IMB[50][r, jof(831):jof(1500)]).all()]
    R_ = np.array(rows)
    print(__doc__.split("\n")[0]); print(f"sessions: {len(rows)}")
    print("   imbalance (50 levels) share of minutes >= +20: {:.0%}, <= -20: {:.0%}".format(
        np.nanmean(IMB[50][R_, jof(831):jof(1500)] >= 20), np.nanmean(IMB[50][R_, jof(831):jof(1500)] <= -20)))
    for k in (1, 5):
        cols = np.arange(jof(831) + k - 1, jof(1500) - 2 * k + 1, k)      # signal bar closes with two bars after
        o_next = g.o[R_][:, cols + 1]; o_next2 = g.o[R_][:, cols + k + 1]
        c, o = g.c[R_][:, cols], g.o[R_][:, cols - k + 1]
        color = np.nan_to_num(np.sign(c - o)); fwd = o_next2 - o_next
        yrs = ts[R_].year.to_numpy()[:, None] * np.ones_like(fwd)
        print(f"\n{k}-minute bars:")
        def rep(nm, dirn):
            m = (dirn != 0) & ~np.isnan(fwd)
            gp = (dirn * fwd)[m]; net = gp * PV - COST - 2 * TICK * PV; y = yrs[m]
            pf = net[net > 0].sum() / -net[net < 0].sum()
            print(f"   {nm:<34} trades {m.sum():7d} gross {gp.mean():+.3f} pts (t {gp.mean() / gp.std() * np.sqrt(len(gp)):5.1f})"
                  f" | net ${net.mean():6.1f} PF {pf:.2f} | net 18-22 ${net[y < 2023].mean():6.1f} 23-26 ${net[y >= 2023].mean():6.1f}"
                  f" | gross L {gp[(dirn[m] > 0)].mean():+.3f} S {gp[(dirn[m] < 0)].mean():+.3f}")
        rep("1 candle colour", color)
        for n in (10, 20, 50):
            imb = IMB[n][R_][:, cols]
            for th in (20, 40):
                book = np.where(imb >= th, 1, np.where(imb <= -th, -1, 0))
                rep(f"2 book {n} levels, +/-{th}%", book)
                if th == 20: rep(f"3 both agree ({n} levels, 20%)", np.where((color != 0) & (color == book), color, 0))
        imb = IMB[50][R_][:, cols]; book = np.where(imb >= 20, 1, np.where(imb <= -20, -1, 0))
        rep("2 book 50 levels 20%, FADED", -book)
    print("\n   (a round trip costs $17.25 = 0.86 points)")
