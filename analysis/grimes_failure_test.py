"""Grimes, *The Art and Science of Technical Analysis* — Antigravity's #1 (2026-10-18): the Failure Test (spring / upthrust):
price probes beyond a key level, then closes back inside; trade the snap-back, stop 1 tick beyond the probe extreme.
Pre-registered mechanical version (4 trials): key level = the previous regular session's high / low (8:30-15:00 CT).
5-minute bars 8:35-14:00 CT: a bar trades above the prior high, and within the next 3 bars (incl. itself) a bar CLOSES back
below it -> short at the next bar's open, stop 1 tick above the highest high since the probe; mirror below the prior low.
One trade a day (first signal). Exit: (a) 15:00 close, (b) Grimes' time stop: 4 bars (20 min) after entry.
Per contract after $7.25 + 1 tick a side (NQ) / $5 + 1 tick a side (ES).
  python3 analysis/grimes_failure_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import s_rank_es_round1_test as ER

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"


def line(t, nm):
    if len(t) < 5: print(f"   {nm:<30} n={len(t)}"); return
    n = t.net; yrs = n.groupby(t.date.dt.year).sum(); gl = -n[n < 0].sum(); tt = n.mean() / n.std() * np.sqrt(len(n))
    a, h = n[t.date < "2023"], n[t.date >= "2023"]
    print(f"   {nm:<30} n={len(n):4d} ${n.mean():6.0f} PF {n[n > 0].sum() / gl:4.2f} t {tt:4.1f} yrs+ {(yrs > 0).sum()}/{len(yrs)} | 18-22 ${a.mean():.0f} 23+ ${h.mean():.0f} | L ${n[t.side > 0].mean():.0f} S ${n[t.side < 0].mean():.0f}")


if __name__ == "__main__":
    for nm, f, pv, com in (("NQ", "g24.pkl", 20.0, 7.25 * 2), ("ES", "ge.pkl", 50.0, 10.0)):
        ER.PV, ER.COMM, ER.TICK = pv, com, 0.25
        g = pickle.load(open(SP + f, "rb")); tr = g.trading
        J0, J1 = jof(831), jof(1500)
        hi = np.nanmax(g.h[tr, J0:J1 + 1], 1); lo = np.nanmin(g.l[tr, J0:J1 + 1], 1)
        rows, sides, j0s, stops = [], [], [], []
        for i in range(1, len(tr)):
            d = tr[i]
            if pd.Timestamp(g.ts[d]) < pd.Timestamp("2018-01-01") or g.last_j[d] < J1: continue
            ph, pl = hi[i - 1], lo[i - 1]
            ends = np.arange(jof(835), jof(1400) + 1, 5)                       # 5-min bar closes 8:35..14:00
            H = np.array([np.nanmax(g.h[d, e - 4:e + 1]) for e in ends]); L = np.array([np.nanmin(g.l[d, e - 4:e + 1]) for e in ends])
            C = np.array([g.c[d, e] for e in ends])
            done = False
            for k in range(len(ends)):
                for side, probe in ((-1, H[k] > ph), (1, L[k] < pl)):
                    if done or not probe: continue
                    for m in range(k, min(k + 3, len(ends))):
                        back = C[m] < ph if side < 0 else C[m] > pl
                        if back and ends[m] + 1 <= jof(1400):
                            ext = (H[k:m + 1].max() + 0.25) if side < 0 else (L[k:m + 1].min() - 0.25)
                            entry_j = ends[m] + 1
                            dist = (ext - g.o[d, entry_j]) * (-side) if side < 0 else (g.o[d, entry_j] - ext)
                            if not np.isfinite(dist) or dist <= 0: break
                            rows.append(d); sides.append(side); j0s.append(entry_j); stops.append(abs(g.o[d, entry_j] - ext)); done = True
                            break
                if done: break
        rows, sides, j0s, stops = map(np.array, (rows, sides, j0s, stops))
        print(f"\n{nm}: {len(rows)} failure tests (prior-session high / low)")
        res = []
        for j0, s, d, st in zip(j0s, sides, rows, stops):
            pass
        t_close = pd.concat([ER.trades(g, rows[[i]], sides[i], j0s[i], J1, stops[i]) for i in range(len(rows))])
        t_time = pd.concat([ER.trades(g, rows[[i]], sides[i], j0s[i], min(j0s[i] + 19, J1), stops[i]) for i in range(len(rows))])
        line(t_close, "exit 15:00 (or stop)"); line(t_time, "exit after 4 bars (or stop)")
