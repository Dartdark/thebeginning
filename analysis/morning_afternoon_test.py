"""Morning momentum, afternoon reversal (Xu & Zhu 2022, "A Tale of One Day", SSRN 4192163), time-series port to NQ / ES / YM.

Paper: US stocks 1993-2019, cross-section: the past month's morning return (9:30-11:30 ET) predicts next month's return
positively, the afternoon return (14:00-16:00 ET) negatively; a daily afternoon-loser strategy has Sharpe 13 (1998-2010).
Port (CT clock): morning = 8:30 -> 10:30 close, afternoon = 13:00 -> 15:00; trade the next session 8:30 -> 15:00, 1 contract:
  1. daily: follow yesterday's morning; fade yesterday's afternoon; both (sum of the two signs, trade when they agree)
  2. 20-day sums of morning / afternoon returns as the signal (the paper's monthly formation), traded daily
Costs: $7.25 + 1 tick a fill (ES $5 + 1 tick).
  python3 analysis/morning_afternoon_test.py [SCRATCH_DIR]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import load, cost, SPEC, line
import metrics as M


def frame(sym):
    g = load(sym); pv = SPEC[sym][0]; r = g.trading
    cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    p = {h: cf[r * 1440 + jof(h)] for h in (830, 1030, 1300, 1500)}
    ok = ~np.isnan(g.c[r, jof(830):jof(1500) + 1]).all(1)
    d = pd.DataFrame({"am": np.log(p[1030] / p[830]), "pm": np.log(p[1500] / p[1300]), "day": (p[1500] - p[830]) * pv},
                     index=pd.DatetimeIndex(g.ts[r]))[ok]
    return d[d.index >= "2017-11-01"]


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    for s in ("NQ", "ES", "YM"):
        d = frame(s); c = cost(s); nxt = d.day.shift(-1)
        print(f"\n{s} ({len(d)} days), cost ${c:.2f}")
        X = pd.concat([d.am, d.pm, nxt / SPEC[s][0]], axis=1, keys=["am", "pm", "nxt"]).dropna()
        b = np.linalg.lstsq(np.c_[np.ones(len(X)), X.am, X.pm], X.nxt, rcond=None)[0]
        print(f"   corr(next session, morning) {X.am.corr(X.nxt):+.3f}, (next session, afternoon) {X.pm.corr(X.nxt):+.3f}")
        rows = {}
        for nm, sig in (("follow yesterday's morning", np.sign(d.am)), ("fade yesterday's afternoon", -np.sign(d.pm)),
                        ("both agree", np.where(np.sign(d.am) == -np.sign(d.pm), np.sign(d.am), 0)),
                        ("follow 20-day morning sum", np.sign(d.am.rolling(20).sum())),
                        ("fade 20-day afternoon sum", -np.sign(d.pm.rolling(20).sum()))):
            sig = pd.Series(sig, index=d.index); x = (sig * nxt)[sig != 0].dropna()
            print(line(x, f"{nm} gross")); print(line(x - c, f"{nm} NET")); rows[nm] = x - c
        print("   long every day (drift) NET:", line(nxt.dropna() - c, "")[4:])
