"""Replacement sweep, stage 2b: the stage-1 screen (one history) overstated swaps at 2 MNQ (the bootstrapped bench blew
17-22%), so every plan slot's top-2 candidates by 'vs empty slot' at the SMALL size (1 MNQ or $400 risk) go on the
bootstrapped bench with their empty-slot controls.
  python3 analysis/replacement_sweep_stage2b.py [SCRATCH_DIR]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
sys.argv = sys.argv[:1] + ["scratch_data"] if len(sys.argv) < 2 else sys.argv
import replacement_sweep as RS
import funded_bootstrap as FB

R = pd.read_pickle(RS.SP + "replacement_stage1.pkl")
ctl = R[R.cand == "(nothing)"].set_index(["piece", "how"])
R["vs_empty"] = R.y2 - [ctl.loc[(p, h), "y2"] for p, h in zip(R.piece, R.how)]
small = R[(R.cand != "(nothing)") & R["size"].isin(["1", "('risk', 400)"])]
plans = {"current plan": RS.CUR}
for (piece, how), grp in small.groupby(["piece", "how"], sort=False):
    p0 = RS.drop(piece) if how == "whole" else {**RS.CUR, **RS.PART[piece]}
    plans[f"{piece} {how} -> empty"] = p0
    for r in grp.sort_values("vs_empty", ascending=False).head(2).itertuples():
        sz = ("risk", 400) if r.size.startswith("(") else 1
        plans[f"{piece} {how} -> {r.cand} {r.size}"] = {**p0, r.cand: sz}
B = FB.Boot(RS.lab); df, s, _ = B.compare(plans, base="current plan", n=1000, L=20)
print(__doc__.split("\n")[0]); print(s); df.to_pickle(RS.SP + "replacement_stage2b.pkl")
