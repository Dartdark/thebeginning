"""Extreme Money Flow (E Trades research paper + EMF.txt, user, 2026-10-18), rebuilt on our NQ 1-minute (CT):
session-anchored Chaikin Money Flow on regular-session 1-minute bars 8:30-14:59 CT (reset each session), length 20:
mult = ((C-L)-(H-C))/(H-L), CMF = sum(mult x volume, 20) / sum(volume, 20). After 20 bars: CMF crosses above +0.25 ->
long next bar at market; below -0.25 -> short. One trade a day; 80-pt stop and 80-pt target; flat 14:55 CT (next bar).
Paper: IS 2020-24 $109 a trade (PF 1.18, settings chosen in-sample), OOS 2025-26 $107; costs $3 + configured slippage.
Here: $14.50 + 2 ticks ($24.50) per NQ; 2018-2019 is data the paper never used (a fresh out-of-sample check).
Control: same days and times, random side (is the CMF direction worth anything?).
  python3 analysis/emf_cmf_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST, PTS = 20.0, 0.25, 24.5, 80.0


def run(g, d, side, j0, jx):
    e = g.o[d, j0] + side * TICK; tp, sp = e + side * PTS, e - side * PTS
    for j in range(j0, jx):
        h, l = g.h[d, j], g.l[d, j]
        if np.isnan(h): continue
        hit_s = (l <= sp) if side > 0 else (h >= sp); hit_t = (h >= tp) if side > 0 else (l <= tp)
        if hit_s: return (sp - side * TICK - e) * side * PV - COST                 # stop first if both (conservative)
        if hit_t and j > j0: return (tp - e) * side * PV - COST
    x = g.o[d, jx] if not np.isnan(g.o[d, jx]) else pd.Series(g.c[d, :jx]).ffill().iloc[-1]
    return (x - side * TICK - e) * side * PV - COST


def stats(t, nm):
    n = t.net; yrs = n.groupby(t.date.dt.year).sum(); gl = -n[n < 0].sum(); tt = n.mean() / n.std() * np.sqrt(len(n))
    per = lambda a, b: n[(t.date >= a) & (t.date < b)].mean()
    print(f"   {nm:<30} n={len(n):4d} ${n.mean():5.0f} PF {n[n > 0].sum() / gl:4.2f} t {tt:4.1f} yrs+ {(yrs > 0).sum()}/{len(yrs)} | "
          f"2018-19 ${per('2018', '2020'):.0f}  2020-24 ${per('2020', '2025'):.0f}  2025-26 ${per('2025', '2027'):.0f} | L ${n[t.side > 0].mean():.0f} S ${n[t.side < 0].mean():.0f}")
    print("     by year:", yrs.round(0).to_dict())


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); rng = np.random.default_rng(7); rows = []; ctrl = []
    J0, J1, JX = jof(831), jof(1459), jof(1456)
    for d in g.trading:
        dt = pd.Timestamp(g.ts[d])
        if dt < pd.Timestamp("2018-01-01") or g.last_j[d] < J1: continue
        H, L, C, V = g.h[d, J0:J1 + 1], g.l[d, J0:J1 + 1], g.c[d, J0:J1 + 1], np.nan_to_num(g.v[d, J0:J1 + 1])
        ok = ~np.isnan(C); H, L, C, V = H[ok], L[ok], C[ok], V[ok]; idx = np.flatnonzero(ok) + J0
        rngb = H - L; mult = np.where(rngb > 0, ((C - L) - (H - C)) / np.where(rngb > 0, rngb, 1), 0.0)
        mf = pd.Series(mult * V).rolling(20).sum(); vv = pd.Series(V).rolling(20).sum()
        cmf = (mf / vv.replace(0, np.nan)).fillna(0).to_numpy()
        for k in range(20, len(cmf)):
            side = 1 if (cmf[k] > 0.25 and cmf[k - 1] <= 0.25) else (-1 if (cmf[k] < -0.25 and cmf[k - 1] >= -0.25) else 0)
            if side and idx[k] + 1 < JX:
                j0 = idx[k] + 1
                rows.append(dict(date=dt, side=side, net=run(g, d, side, j0, JX)))
                rs = rng.choice([-1, 1]); ctrl.append(dict(date=dt, side=rs, net=run(g, d, rs, j0, JX)))
                break
    T, Cc = pd.DataFrame(rows), pd.DataFrame(ctrl)
    print("EMF (CMF 20, +/-0.25, 80 / 80 pts), per NQ after $24.50:")
    stats(T, "EMF as specified"); stats(Cc, "control: same entry, random side")
