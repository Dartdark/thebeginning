"""Score candidate direction signals (analysis/direction_search.py) inside a fixed trade, with
Overnight Bias's own bias as the benchmark (2026-10-12).

For every trading day the outcome of a long and of a short is precomputed per NQ, after $7.25 +
1 tick per market/stop fill, for two engines:
  'open'  enter at the 8:45 open; stop 30% of the 15-day ATR; target 3R; flat 14:30 CT
  'orb'   ONB mechanics without ADX: stop order at the 8:30-8:45 range high (low) until 14:00,
          same stop / target / exit
A direction signal picks which outcome is taken (0 = no trade). Same bar: stop first.
"""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
SP = "/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
g = pickle.load(open(SP + "g24.pkl", "rb"))
PV, COST, TICK = 20.0, 7.25, 0.25
atr = g.daily_atr(15)


def trade(d, side, j_in, px_in, stop_pts, j_exit=870):
    o, h, l, c = g.o[d], g.h[d], g.l[d], g.c[d]
    e = px_in + side * TICK; sl = e - side * stop_pts; tp = e + side * 3 * stop_pts
    for j in range(j_in, j_exit + 1):
        if np.isnan(c[j]): continue
        if (l[j] <= sl) if side > 0 else (h[j] >= sl):
            px = (min(o[j], sl) if side > 0 else max(o[j], sl)) - side * TICK; return (px - e) * side * PV - COST, j
        if (h[j] >= tp) if side > 0 else (l[j] <= tp):
            return (tp - e) * side * PV - COST, j
    jj = j_exit
    while np.isnan(c[jj]) and jj > j_in: jj -= 1
    return (c[jj] - side * TICK - e) * side * PV - COST, jj


def outcomes():
    out = {}
    for d in g.trading:
        if np.isnan(g.o[d, 526]) or np.isnan(atr[d]) or np.isnan(g.c[d, 870]): continue
        sp = 0.30 * atr[d]; r = {}
        for s in (1, -1):
            r[("open", s)] = trade(d, s, 526, g.o[d, 526], sp)[0]
            orh, orl = np.nanmax(g.h[d, 511:526]), np.nanmin(g.l[d, 511:526])
            lvl = orh if s > 0 else orl; res = 0.0
            for j in range(526, 841):
                if np.isnan(g.c[d, j]): continue
                if (g.h[d, j] >= lvl) if s > 0 else (g.l[d, j] <= lvl):
                    px = max(g.o[d, j], lvl) if s > 0 else min(g.o[d, j], lvl)
                    # stop/target checked from the entry bar's close onward (entry bar: stop only on close beyond)
                    res = trade(d, s, j + 1, px, sp)[0]
                    break
            r[("orb", s)] = res
        out[pd.Timestamp(g.ts[d])] = r
    return pd.DataFrame(out).T


if __name__ == "__main__":
    O = outcomes(); O.to_pickle(SP + "dir_outcomes.pkl"); print(O.describe().T)
