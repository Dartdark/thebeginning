"""London Session Signal B proxy (Mesfin 2026, "Structural Limits of OHLCV-Based Intraday Momentum Signals in MNQ", SSRN 6709401).

Paper: GMM regimes on 15-min London bars (03:00-08:30 ET = 02:00-07:30 CT); long at the next bar open after a clean switch from
'bearish chop' to 'bullish drift', out 60 min or 08:30 ET, 20-pt stop; walk-forward t 4.3, +4.09 pts per MNQ, but a 15-min delay
flips it to t -2.8 (a sign of entering inside the trigger bar). The regime mapping is not fully specified, so a rule proxy:
  chop bar   : 15-min return <= 0 and range below its 20-bar median
  drift bar  : return >= +k x 20-bar sd of 15-min returns and close in the top 30% of its range; no bar in the prior 2 with range
               above 2 x the 20-bar median ('no extreme volatility')
  signal     : chop bar followed by a drift bar, drift bar closing 02:15-07:15 CT
  entries    : (a) next bar open (tradeable); (b) 15 min later (the paper's delay test); (c) the drift bar's OWN open (look-ahead,
               what a bar-timestamp slip does); exit 60 min after entry or 07:30 CT, stop 20 pts. 1 NQ, $7.25 + 1 tick a fill.
  python3 analysis/london_signal_b_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import line

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 20.0, 0.25, 7.25


def trade(g, d, j_in, j_out, stop=20.0):
    """Long from the open of minute j_in to the close of j_out, stop below entry. Returns $ net or nan."""
    o = g.o[d, j_in]
    if np.isnan(o): return np.nan
    e = o + TICK; s = e - stop
    for m in range(j_in, j_out + 1):
        if np.isnan(g.l[d, m]): continue
        if g.l[d, m] <= s:
            px = min(g.o[d, m], s) - TICK if m > j_in else s - TICK
            return (px - e) * PV - COMM
    c = g.c[d, :j_out + 1]; mm = np.flatnonzero(~np.isnan(c))
    return (c[mm[-1]] - TICK - e) * PV - COMM


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); b = g.bars(15)
    rows = [d for d in g.trading if pd.Timestamp(g.ts[d]).year >= 2018]
    R = {}
    for k in (0.5, 1.0, 1.5):
        res = {"next": [], "delay": [], "own": []}; dates = []
        for d in rows:
            o, h, l, c = b["o"][d], b["h"][d], b["l"][d], b["c"][d]
            ret = c - o; rng = h - l
            for i in range(jof(215) // 15, jof(715) // 15 + 1):
                if i < 22 or np.isnan(c[i]) or np.isnan(c[i - 1]): continue
                sd = np.nanstd(ret[i - 21:i - 1]); med = np.nanmedian(rng[i - 21:i - 1])
                if not (sd > 0 and med > 0): continue
                chop = ret[i - 1] <= 0 and rng[i - 1] < med
                drift = ret[i] >= k * sd and rng[i] > 0 and (c[i] - l[i]) / rng[i] >= 0.7
                calm = np.nanmax(rng[i - 2:i]) <= 2 * med
                if not (chop and drift and calm): continue
                jc = i * 15                                        # drift bar closes at minute jc
                end = jof(730)
                res["next"].append(trade(g, d, jc + 1, min(jc + 60, end)))
                res["delay"].append(trade(g, d, jc + 16, min(jc + 75, end)) if jc + 16 < end else np.nan)
                res["own"].append(trade(g, d, jc - 14, min(jc - 14 + 59, end)))
                dates.append(pd.Timestamp(g.ts[d])); break           # one signal a day (first)
        idx = pd.DatetimeIndex(dates)
        print(f"\nk = {k} (drift bar >= {k} sd)")
        for nm, lab in (("next", "next bar open (tradeable)"), ("delay", "15 min later"), ("own", "drift bar's own open (LOOK-AHEAD)")):
            x = pd.Series(res[nm], index=idx).dropna(); print(line(x, lab, 40))
            R[(k, nm)] = x
    x = R[(1.0, "next")]
    print("\nk 1.0 tradeable, gross (before costs): avg $%.1f" % (x + COMM + 2 * TICK * PV).mean())
