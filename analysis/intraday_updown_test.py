"""Intraday market-wide ups / downs (Zhang, Lin & Zhang 2016, SSRN 3131369; user's PDF 2026-10-15). Paper: at time m, if the
market is up vs yesterday's close (Index Signal) or more stocks are up than down (UpDown breadth signal), buy the index and
hold to today's close; short if down. China 2000-15: 10-15 bp a day; US 2013-15 (15-min grid, value-weighted market): 4-6 bp
a day for most m, best 8.2 bp at 9:45 ET, t > 2 except 10:15 / 10:30 ET; explained as retail intraday sentiment.
Here, the Index Signal on NQ and ES futures, 2018-2026 (we have no stock-breadth data): at m = 8:45 .. 14:45 CT every 15 min,
side = sign(price at m - yesterday's 15:00 CT close), enter at m's close + 1 tick, exit 15:00 CT close - 1 tick, 1 contract,
$7.25 (ES $5) a round trip. Gross bp too (the paper's unit). Placebo: same days, random side.
  python3 analysis/intraday_updown_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MK = {"NQ": ("g24.pkl", 20.0, 0.25, 7.25), "ES": ("ge.pkl", 50.0, 0.25, 5.0)}
MS = [845, 900, 915, 930, 945, 1000, 1015, 1030, 1045, 1100, 1115, 1130, 1145, 1200, 1215, 1230, 1245, 1300, 1315, 1330, 1345, 1400, 1415, 1430, 1445]

if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    best = {}
    for s, (f, pv, tick, comm) in MK.items():
        g = pickle.load(open(SP + f, "rb")); tr = g.trading
        C = pd.DataFrame(g.c[tr, :jof(1500) + 1]).ffill(axis=1).to_numpy()
        ts = pd.DatetimeIndex(g.ts[tr]); keep = ts.year >= 2018
        close = C[:, jof(1500)]; prev = np.r_[np.nan, close[:-1]]
        print(f"\n{s}: m (CT) | n | gross bp/day (18-22 / 23-26) | net $/trade t | yrs+ | placebo $ | longs $ / shorts $")
        rng = np.random.default_rng(1)
        for m in MS:
            pm = C[:, jof(m)]; side = np.sign(pm - prev)
            ok = keep & ~np.isnan(side) & (side != 0) & ~np.isnan(close)
            bp = side * np.log(close / pm) * 1e4
            net = ((close - pm) * side - 2 * tick) * pv - comm
            x = pd.Series(net[ok], index=ts[ok]); b = pd.Series(bp[ok], index=ts[ok]); sd = side[ok]
            y = x.index.year; t = x.mean() / x.std() * np.sqrt(len(x))
            pl = np.mean([((((close - pm) * rng.choice([-1, 1], len(close)) - 2 * tick) * pv - comm)[ok]).mean() for _ in range(20)])
            by = x.groupby(y).sum()
            print(f"   {m:4d}  n {len(x):4d}  {b.mean():+5.2f} ({b[y < 2023].mean():+5.2f} / {b[y >= 2023].mean():+5.2f})  ${x.mean():+6.1f} t {t:+4.1f}"
                  f"  {(by > 0).sum()}/{len(by)}  pl ${pl:+6.1f}  L ${x[sd > 0].mean():+6.1f} S ${x[sd < 0].mean():+6.1f}")
            if m == 845: best[s] = (x, sd)
    print("\nStandard metrics at the paper's best US time (9:45 ET = 8:45 CT), per contract:")
    for s, (x, sd) in best.items():
        print(f"  {s}:"); print(M.table({"all": (x, x), "longs": (x[sd > 0], x[sd > 0]), "shorts": (x[sd < 0], x[sd < 0])}))
