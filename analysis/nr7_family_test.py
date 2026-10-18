"""NR7 family test (user, 2026-10-18). Hypothesis (Crabel; Kaufman ch. 16): a volatility-breakout earns more on the session
after an NR7 day (the previous regular session's range is the narrowest of the last 7).
Already SEEN (not a clean test): Vault Break NQ $217 vs $60 (t 2.8), ES stretch breakout $163 vs $25 on all days (t 1.7),
Overnight Bias ADX30 worse after NR7 (t -1.6).
PRE-REGISTERED out-of-sample part (written before running): the user's NR7 stretch breakout, unchanged (OCO stops at
open +/- 2 x 10-session stretch, stop at the opposite level, one trade a day), on markets not yet looked at:
  NQ, YM 8:30-15:00 CT (last entry 12:00, out 14:58); CL 8:00-13:30 (11:30, 13:28); GC 7:20-12:30 (10:20, 12:28).
Test per market: NR7 days vs ALL other days with the same breakout ($ difference, Welch t). Pass = the pooled
out-of-sample difference has t >= 2 and at least 3 of 4 markets point the right way.
Pooled over all 7 (seen + new): Stouffer z of the difference t's (seen ones counted at their own t).
Costs per contract: commission + 2 ticks (NQ $14.50 + $10, YM $10 + $10, CL $14.50 + $20, GC $14.50 + $20).
  python3 analysis/nr7_family_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MK = {  # file, point value, tick, commission RT, session open, session close, last entry, exit
    "NQ": ("g24", 20.0, 0.25, 14.5, 830, 1500, 1200, 1458), "YM": ("gy", 5.0, 1.0, 10.0, 830, 1500, 1200, 1458),
    "CL": ("cl", 1000.0, 0.01, 14.5, 800, 1330, 1130, 1328), "GC": ("gc", 100.0, 0.10, 14.5, 720, 1230, 1020, 1228)}


def trade(g, d, up, dn, j_start, last, out):
    H, L, O, C = g.h[d], g.l[d], g.o[d], g.c[d]; side = 0
    for j in range(j_start, last + 1):
        if np.isnan(H[j]): continue
        hu, hd = H[j] >= up, L[j] <= dn
        if hu and hd: return 1, up, dn
        if hu: side, e, sp, j0 = 1, max(up, O[j]), dn, j; break
        if hd: side, e, sp, j0 = -1, min(dn, O[j]), up, j; break
    if not side: return None
    for j in range(j0 + 1, out + 1):
        if np.isnan(H[j]): continue
        if (side > 0 and L[j] <= sp) or (side < 0 and H[j] >= sp):
            return side, e, (min(sp, O[j]) if side > 0 else max(sp, O[j]))
    cc = C[j0:out + 1]; ok = np.flatnonzero(~np.isnan(cc))
    return side, e, cc[ok[-1]]


def market(sym):
    f, pv, tick, com, so, sc, le, ex = MK[sym]; g = pickle.load(open(SP + f + ".pkl", "rb")); tr = g.trading
    J0, J1 = jof(so) + 1, jof(sc)
    O = g.o[tr, J0]; H = np.nanmax(g.h[tr, J0:J1 + 1], 1); L = np.nanmin(g.l[tr, J0:J1 + 1], 1)
    D = pd.DataFrame(dict(row=tr, O=O, H=H, L=L), index=pd.DatetimeIndex(g.ts[tr]).normalize())
    D["R"] = D.H - D.L; D["stretch"] = np.minimum(D.H - D.O, D.O - D.L).rolling(10).mean().shift(1)
    D["nr7"] = (D.R <= D.R.rolling(7).min()).shift(1).fillna(False).astype(bool)
    rows = []
    for dt, r in D[(D.index >= "2018-01-01") & D.stretch.notna() & D.O.notna()].iterrows():
        if g.last_j[r.row] < jof(ex): continue
        x = trade(g, int(r.row), r.O + 2 * r.stretch, r.O - 2 * r.stretch, J0, jof(le), jof(ex))
        if x: rows.append(dict(date=dt, nr7=r.nr7, side=x[0], net=(x[2] - x[1]) * x[0] * pv - com - 2 * tick * pv))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    ts = {}; diffs = []
    print("Out-of-sample markets (pre-registered): NR7 days vs other days, same breakout")
    for sym in MK:
        t = market(sym); a, b = t[t.nr7], t[~t.nr7]
        dm = a.net.mean() - b.net.mean(); se = np.sqrt(a.net.var() / len(a) + b.net.var() / len(b)); ts[sym] = dm / se
        per = lambda y: f"18-22 ${y[y.date < '2023'].net.mean():.0f} / 23+ ${y[y.date >= '2023'].net.mean():.0f}"
        ta = a.net.mean() / a.net.std() * np.sqrt(len(a))
        print(f"  {sym}: NR7 n={len(a):3d} ${a.net.mean():6.0f} (t {ta:4.1f}; {per(a)}) | other n={len(b):4d} ${b.net.mean():6.0f} | diff ${dm:.0f}, t {dm / se:.1f}")
        diffs.append(dict(sym=sym, dm=dm, se=se))
    z_oos = sum(ts.values()) / np.sqrt(len(ts)); right = sum(v > 0 for v in ts.values())
    print(f"\nOut-of-sample pooled (Stouffer) z = {z_oos:.2f}; right direction in {right}/4 -> {'PASS' if z_oos >= 2 and right >= 3 else 'FAIL'}")
    seen = {"VB (NQ)": 2.8, "ES stretch": 1.7, "ONB ADX30": -1.6}
    allt = list(ts.values()) + list(seen.values()); z_all = sum(allt) / np.sqrt(len(allt))
    print(f"All 7 (incl. the 3 already seen, ES stretch counted vs all days): z = {z_all:.2f}")
