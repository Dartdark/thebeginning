"""Codex weekly review 2026-11-06 #2: long_after_green_test.one() skips missing minutes in the held path. Count, per trade, the
missing 1-minute bars inside the held window OUTSIDE normal closures (CME daily break 16:00-17:00 CT, i.e. bars closing
16:01-17:00; whole dates with no data = weekend / holiday), and rerun the frozen rule without the affected trades.
  tools/run_stamped.sh analysis/long_after_green_gaps.py > analysis/outputs/long_after_green_gaps_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from long_after_green_test import run, candles, ts, J0, J1
from grid24 import jof

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); T = g.trading
    op, cl, ks, keep = candles(g); green = ks[keep & (cl > op)]
    brk = (np.arange(1440) >= jof(1601)) & (np.arange(1440) <= jof(1700))
    has_row = ~np.isnan(g.c).all(axis=1)
    miss = []
    for k in green:
        if k + 1 >= len(T): continue
        r, rn = T[k], T[k + 1]; m = 0
        for rr in range(r, rn + 1):
            if not has_row[rr]: continue
            a = J1 + 1 if rr == r else 0; b = (J1 if rr == rn else 1439) + 1
            seg = np.isnan(g.c[rr, a:b]) & ~brk[a:b]
            if rr == rn: pass
            m += int(seg.sum())
        miss.append((pd.Timestamp(g.ts[rn]), m))
    M = pd.DataFrame(miss, columns=["date", "missing"])
    base = run(g, 20.0, 7.25, green)
    print(f"\n   trades {len(M)}; with any missing held minute {np.mean(M.missing > 0):.1%}; > 5 missing {np.mean(M.missing > 5):.1%}; "
          f"> 60 missing {np.mean(M.missing > 60):.1%}; median missing {M.missing.median():.0f}, max {M.missing.max()}")
    print("   missing minutes by year (trades with any):", M[M.missing > 0].groupby(M.date.dt.year).size().to_dict())
    j = base.merge(M, on="date", how="left")
    for lim in (0, 5, 60):
        x = j[j.missing <= lim]
        print(f"   only trades with <= {lim:>2} missing minutes: n {len(x)}, ${x.net.mean():.0f} a trade, t {ts(x.net):.2f}"
              f" (2018-22 ${x[x.date < '2023'].net.mean():.0f}, 2023+ ${x[x.date >= '2023'].net.mean():.0f})")
    print(f"   all trades: n {len(j)}, ${j.net.mean():.0f}, t {ts(j.net):.2f}")
