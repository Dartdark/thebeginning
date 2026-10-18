"""ZN momentum after the 7:30 CT macro releases (CPI, payrolls, PPI, retail sales ...): the one new Apex-fit idea in
Antigravity's readings of Pedersen, *Efficiently Inefficient* (ch. 11 / 14) and Chan, *Machine Trading* (2026-10-18).
Mechanism (Antigravity's inference, not the books' rule): duration hedgers (dealers, pensions, mortgage hedgers) must
re-hedge after a data surprise, so the first move keeps going.
Pre-registered (4 variants): release day = ZN's 7:30-7:35 range > 3x its 20-day median (event_days.release_days on ZN);
follow the 7:30 -> 7:35 ZN move, enter 7:36 open; exit 9:00 or 14:00; no stop or an 8-tick stop.
Placebo: same rule on non-release days. Costs $7.25 + 1 tick ($15.625) per market / stop fill = $38.50 a round trip.
  python3 analysis/zn_release_momentum_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import event_days as EV
import s_rank_es_round1_test as ER

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
ER.PV, ER.TICK, ER.COMM = 1000.0, 1 / 64, 7.25


def line(t, nm):
    if len(t) < 5: print(f"   {nm:<34} n={len(t)}"); return
    n = t.net; yrs = n.groupby(t.date.dt.year).sum(); gl = -n[n < 0].sum()
    tt = n.mean() / n.std() * np.sqrt(len(n)); a = n[t.date < "2023"]; h = n[t.date >= "2023"]
    print(f"   {nm:<34} n={len(n):4d} ${n.mean():6.0f} PF {n[n > 0].sum() / gl:4.2f} t {tt:4.1f} yrs+ {(yrs > 0).sum()}/{len(yrs)} | 18-22 ${a.mean():5.0f} 23+ ${h.mean():5.0f}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "zn.pkl", "rb"))
    print("tick", ER.TICK, "check a ZN price:", np.nanmedian(g.c[g.trading[-50:], jof(800)]))
    rel = EV.release_days(g); rel = rel[pd.DatetimeIndex(g.ts[rel]) >= "2018-01-01"]
    other = np.setdiff1d(g.trading[pd.DatetimeIndex(g.ts[g.trading]) >= "2018-01-01"], rel)
    cf = pd.Series(g.c.ravel()).ffill().to_numpy(); P = lambda rows, t: cf[rows * 1440 + jof(t)]
    print(f"release days {len(rel)}, other days {len(other)}")
    for nm, rows in (("RELEASE days", rel), ("placebo: other days", other)):
        print(nm)
        mv = P(rows, 735) - P(rows, 730); s = np.sign(mv).astype(int); m = s != 0
        for ex in (900, 1400):
            for st in (np.inf, 8):
                t = ER.trades(g, rows[m], s[m], jof(736), jof(ex), st * ER.TICK if np.isfinite(st) else np.inf)
                line(t, f"exit {ex}, stop {'none' if not np.isfinite(st) else '8 ticks'}")
