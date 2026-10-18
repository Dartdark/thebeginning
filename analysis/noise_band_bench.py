"""Noise-band (Chuk 2026) on the bootstrapped funded bench: add 1 / 2 MNQ (longs+shorts, or shorts only, which are
uncorrelated with Vault Break) to the current plan. Per-MNQ minute paths from analysis/noise_band_chuk_test.py's trades,
our costs / 10 ($2.45 per MNQ round trip incl. 1 tick per fill).
  python3 analysis/noise_band_bench.py [SCRATCH_DIR]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import funded_bootstrap as FB
import noise_band_chuk_test as NB
from grid24 import jof

lab = FB.add_moc_mes(FB.plan_lab())
dates = pd.DatetimeIndex(lab.g.ts[lab.tr]); pos = pd.Series(np.arange(len(dates)), index=dates)
for key, sel in (("NB_MNQ", NB.T.side != 0), ("NBS_MNQ", NB.T.side < 0)):
    W = np.zeros((len(dates), 1440)); Cd = np.zeros(len(dates))
    for d, grp in NB.T[sel].groupby("date"):
        if d not in pos.index: continue
        i = pos[d]; acc = 0.0; day = np.zeros(1440)
        for r in grp.itertuples():
            a, b = NB.J0 + r.j0, NB.J0 + r.j1
            seg = NB.C[r.i, r.j0:r.j1 + 1]
            path = (seg - r.e) * r.side * 2 - 0.25 * 2 - 1.45
            day[a:b + 1] = acc + path
            acc += r.side * (r.x - r.e) * 2 - 2 * 0.25 * 2 - 1.45
            day[b + 1:] = acc
        W[i] = day; Cd[i] = acc
    lab.W[key] = W; lab.C[key] = Cd
CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2}
B = FB.Boot(lab)
plans = {"current plan": CUR, "+ noise-band 1 MNQ": {**CUR, "NB_MNQ": 1}, "+ noise-band 2 MNQ": {**CUR, "NB_MNQ": 2},
         "+ NB shorts only 1 MNQ": {**CUR, "NBS_MNQ": 1}, "+ NB shorts only 2 MNQ": {**CUR, "NBS_MNQ": 2}}
df, s, _ = B.compare(plans, base="current plan", n=1000, L=20); print(__doc__.split("\n")[0]); print(s)

# Replacement test (user rule 2026-10-18: a candidate may replace instead of add). Noise-band overlaps Vault Break most.
rep = {"current plan": CUR,
       "VB 0 / 0, NB 1 MNQ": {**CUR, "VB_N": 0, "VB_F": 0, "NB_MNQ": 1},
       "VB 0 / 0, NB 2 MNQ": {**CUR, "VB_N": 0, "VB_F": 0, "NB_MNQ": 2},
       "VB 0 / 0, NB 3 MNQ": {**CUR, "VB_N": 0, "VB_F": 0, "NB_MNQ": 3},
       "VB 1 / 1, NB 1 MNQ": {**CUR, "VB_N": 1, "VB_F": 1, "NB_MNQ": 1},
       "VB 2 / 1, NB longs-out: shorts 1": {**CUR, "NBS_MNQ": 1},
       "VB 1 / 1, NB shorts 1": {**CUR, "VB_N": 1, "VB_F": 1, "NBS_MNQ": 1}}
df, s, _ = B.compare(rep, base="current plan", n=1000, L=20)
print("\nReplacement (in place of / in part of Vault Break):"); print(s)

# Control: is the lower blow-up rate the noise band, or just less Vault Break?
ctl = {"current plan": CUR, "VB 0 / 0, nothing": {**CUR, "VB_N": 0, "VB_F": 0},
       "VB 1 / 1, nothing": {**CUR, "VB_N": 1, "VB_F": 1},
       "VB 1 / 1, NB shorts 1": {**CUR, "VB_N": 1, "VB_F": 1, "NBS_MNQ": 1},
       "VB 0 / 0, NB 1 MNQ": {**CUR, "VB_N": 0, "VB_F": 0, "NB_MNQ": 1}}
df, s, _ = B.compare(ctl, base="current plan", n=1000, L=20)
print("\nControl (VB cut with nothing in its place):"); print(s)
