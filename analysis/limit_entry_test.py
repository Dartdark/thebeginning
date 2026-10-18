"""Limit instead of market entries for the plan's market-order strategies (user, 2026-10-18).
For each MultiCharts trade (VB, LDF, ES MOC, Monday Long, EOS, NFP Fade): decision = the bar close before the entry bar;
the market order fills at the next minute's open (+1 tick slippage in our standard). Alternative: a LIMIT at the decision
close k ticks better (k = 0 / 1 / 2), working for W minutes; it fills only if price trades THROUGH it by 1 tick
(conservative queue assumption). Filled: same exit, entry at the limit, no entry slippage. Not filled: the trade is missed
(its P&L lost). This measures both the tick saved and the adverse selection (limits fill more often on the losers).
Per contract; costs as compare.py (commission per side + 1 tick per market / stop fill).
  python3 analysis/limit_entry_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis"); sys.path.insert(0, "analysis/jesse")
import numpy as np, pandas as pd
from grid24 import jof
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
sys.argv = sys.argv[:1]
import compare as C

RUN = {"VaultBreak": ("g24", 30), "LateDayFlow": ("g24", 5), "ESMOCFollow": ("ge", 5), "MondayLong": ("g24", 5),
       "ExpOpenShort": ("g24", 5), "NFPFade": ("g24", 5)}

if __name__ == "__main__":
    grids = {}; rows = []
    for nm, (f, blen) in RUN.items():
        g = grids.setdefault(f, pickle.load(open(SP + f + ".pkl", "rb"))); pos = pd.Series(np.arange(g.D), index=pd.DatetimeIndex(g.ts).normalize())
        path, pv, tick, cost = C.REPORTS[nm]; m = C.mc_trades(path); m = m[m.entry_time >= "2018-01-01"]
        base = m.points * pv - 2 * cost - 2 * tick * pv
        rec = []
        for t, s, e, x in zip(m.entry_time, m.side, m.entry, m.exit):
            d = pos.get(t.normalize()); dec = t - pd.Timedelta(minutes=blen); jd = jof(dec.hour * 100 + dec.minute)
            if d is None: rec.append(None); continue
            pdec = pd.Series(g.c[d, :jd + 1]).ffill().iloc[-1]
            rec.append((d, jd, pdec, s, e, x))
        chk = np.array([abs(r[4] - g.o[r[0], r[1] + 1]) <= tick for r in rec if r is not None and not np.isnan(g.o[r[0], r[1] + 1])])
        print(f"\n{nm}: {len(m)} trades; MC entry = first minute's open within 1 tick on {chk.mean():.0%}; market-entry net ${base.mean():.0f} a trade (t {base.mean() / base.std() * np.sqrt(len(base)):.1f})")
        for W in ((1, 2, 5) if nm != "ESMOCFollow" else (1, 2)):
            for k in (0, 1, 2):
                net = []; fills = 0; miss_net = []
                for r, b in zip(rec, base):
                    if r is None: net.append(b); continue
                    d, jd, pdec, s, e, x = r; lim = pdec - s * k * tick
                    seg_l, seg_h = g.l[d, jd + 1:jd + 1 + W], g.h[d, jd + 1:jd + 1 + W]
                    hit = (np.nanmin(seg_l) <= lim - tick) if s > 0 else (np.nanmax(seg_h) >= lim + tick)
                    if hit: fills += 1; net.append((x - lim) * s * pv - 2 * cost - tick * pv)
                    else: net.append(0.0); miss_net.append(b)
                net = np.array(net)
                print(f"   limit {k} tick(s) better, {W} min: filled {fills / len(net):.0%}, net ${net.mean():6.1f} a signal "
                      f"(vs ${base.mean():.1f} market; diff {net.mean() - base.mean():+.1f}); missed trades averaged ${np.mean(miss_net) if miss_net else 0:.0f}")
