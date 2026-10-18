"""Chan, Algorithmic Trading (2013), ch. 7 — the two Apex-fit ideas on Antigravity's short list
(antigravity/jesse tasks/out_book_chan_algotrading/ideas.md), pre-registered from the book's own rules, 2026-10-18.

A  Opening-gap momentum (Example 7.1, FSTX): if the open is above the previous session's high, buy at the open; below its
   low, short; out at the close. Here: regular session 8:30-15:00 CT, open = 8:30 bar open, close = 15:00 close.
   A1 as written (beyond the prior high / low); A2 Chan's code variant: beyond by 0.1 x the 90-day sd of daily returns.
   No stop in the book; also A3 = A1 with a 0.5 x ATR15 stop (an Apex account needs one).
   Mechanism (book): stops resting beyond yesterday's range fire at the open.
   Control: same-side open->close on all days (is the gap day any different from NQ's / ES's plain drift?).
B  Leveraged-ETF momentum (section 7.3): previous close (15:00 CT) -> 14:45 CT return > +2% buy, < -2% short, out 15:00.
   Also the same at 1% (NQ / ES rarely move 2%). Close relative of ES MOC Follow / Late-Day Flow.
Costs: $7.25 per NQ / $5 per ES round trip + 1 tick per market / stop fill. Per contract, 2018-2026.
  python3 analysis/chan_book_ideas_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import s_rank_es_round1_test as ER

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MK = {"NQ": ("g24.pkl", 20.0, 7.25), "ES": ("ge.pkl", 50.0, 5.0)}


def line(t, nm):
    if len(t) < 5: print(f"   {nm:<40} n={len(t)}"); return
    n = t.net; yrs = n.groupby(t.date.dt.year).sum(); gl = -n[n < 0].sum()
    tt = n.mean() / n.std() * np.sqrt(len(n)); a = n[t.date < "2023"]; h = n[t.date >= "2023"]
    print(f"   {nm:<40} n={len(n):4d} ${n.mean():6.0f} PF {n[n > 0].sum() / gl:4.2f} t {tt:4.1f} yrs+ {(yrs > 0).sum()}/{len(yrs)} "
          f"| 18-22 ${a.mean():5.0f} 23+ ${h.mean():5.0f} | L ${n[t.side > 0].mean():5.0f} ({(t.side > 0).sum()}) S ${n[t.side < 0].mean():5.0f} ({(t.side < 0).sum()})")


if __name__ == "__main__":
    for m, (f, pv, com) in MK.items():
        ER.PV, ER.COMM = pv, com
        g = pickle.load(open(SP + f, "rb"))
        tr = g.trading[pd.DatetimeIndex(g.ts[g.trading]) >= "2017-09-01"]
        cf = pd.Series(g.c.ravel()).ffill().to_numpy(); P = lambda rows, t: cf[rows * 1440 + jof(t)]
        J0, J1 = jof(831), jof(1500)                          # 8:30-8:31 bar (open = 8:30 print) .. 15:00
        o = g.o[tr, J0]; hi = np.nanmax(g.h[tr, J0:J1 + 1], 1); lo = np.nanmin(g.l[tr, J0:J1 + 1], 1); cl = P(tr, 1500)
        full = g.last_j[tr] >= J1
        ph, pl, pc = np.r_[np.nan, hi[:-1]], np.r_[np.nan, lo[:-1]], np.r_[np.nan, cl[:-1]]
        ret = pd.Series(cl / pc - 1); sd = ret.rolling(90).std().shift(1).to_numpy()
        atr = g.daily_atr(15)[tr]
        keep = (pd.DatetimeIndex(g.ts[tr]) >= "2018-01-01") & full & ~np.isnan(o) & ~np.isnan(ph)
        print(f"\n===== {m} (per contract) =====")
        print(" A. Opening-gap momentum, 8:30 open -> 15:00 close")
        side1 = np.where(o > ph, 1, np.where(o < pl, -1, 0))
        k = 0.1 * sd * pc
        side2 = np.where(o > ph + k, 1, np.where(o < pl - k, -1, 0))
        for nm, sd_, stop in (("A1 as written (no stop)", side1, np.inf), ("A2 0.1 sd threshold (no stop)", side2, np.inf),
                              ("A3 = A1 + 0.5 ATR stop", side1, 0.5)):
            m_ = keep & (sd_ != 0) & (~np.isnan(sd) if nm.startswith("A2") else True)
            t = ER.trades(g, tr[m_], sd_[m_], J0, J1, (stop * atr[m_]) if np.isfinite(stop) else np.inf)
            line(t, nm)
        allL = ER.trades(g, tr[keep], 1, J0, J1, np.inf); allS = ER.trades(g, tr[keep], -1, J0, J1, np.inf)
        line(allL, "control: long every day"); line(allS, "control: short every day")
        print(" B. Leveraged-ETF momentum: prev close -> 14:45, in 14:46, out 15:00")
        r1445 = P(tr, 1445) / pc - 1
        for thr in (0.02, 0.01):
            s = np.where(r1445 > thr, 1, np.where(r1445 < -thr, -1, 0)); m_ = keep & (s != 0)
            line(ER.trades(g, tr[m_], s[m_], jof(1446), J1, np.inf), f"B |return| > {thr:.0%}")
