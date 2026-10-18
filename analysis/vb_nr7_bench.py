"""Vault Break sized up the session after an NR7 day (yesterday's 8:30-15:00 range the narrowest of the last 7; Crabel via
Kaufman, `analysis/kaufman_day_filters_test.py`: VB $217 vs $60 a trade, t 2.8, 2018-22 $222 / 2023+ $212) on the
bootstrapped funded bench, current plan (VB 2 / single-print 1, ES MOC 2 MES). NR7 days that are also single-print days stay at 1.
  python3 analysis/vb_nr7_bench.py [SCRATCH_DIR]
"""
import sys; sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import funded_bootstrap as FB

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2}

if __name__ == "__main__":
    print(__doc__.split("\n")[0], flush=True)
    lab = FB.add_moc_mes(FB.plan_lab(SP), SP); g = lab.g; tr = lab.tr
    hi = np.nanmax(g.h[tr, jof(831):jof(1500) + 1], 1); lo = np.nanmin(g.l[tr, jof(831):jof(1500) + 1], 1)
    rng = pd.Series(hi - lo)
    nr7 = (rng <= rng.rolling(7).min()).shift(1).fillna(False).to_numpy().astype(bool)
    vbn = lab.C["VB_N"] != 0
    print(f"VB non-flagged days {vbn.sum()}, of which after NR7: {(vbn & nr7).sum()}; avg per lab unit NR7 "
          f"{lab.C['VB_N'][vbn & nr7].mean():.1f} vs other {lab.C['VB_N'][vbn & ~nr7].mean():.1f}", flush=True)
    lab.W["VB_NR"] = lab.W["VB_N"] * nr7[:, None]; lab.C["VB_NR"] = lab.C["VB_N"] * nr7
    lab.W["VB_NO"] = lab.W["VB_N"] * ~nr7[:, None]; lab.C["VB_NO"] = lab.C["VB_N"] * ~nr7
    base = {k: v for k, v in CUR.items() if k != "VB_N"}
    plans = {"current (VB 2 / 1)": CUR, "VB 2, NR7 days 3": {**base, "VB_NO": 2, "VB_NR": 3},
             "VB 2, NR7 days 4": {**base, "VB_NO": 2, "VB_NR": 4}, "VB 1, NR7 days 3": {**base, "VB_NO": 1, "VB_NR": 3}}
    B = FB.Boot(lab)
    for seed in (1, 2):
        df, s, _ = B.compare(plans, n=1000, L=20, seed=seed); print(f"\nseed {seed}, 1,000 paired histories, L 20:\n{s}", flush=True)
