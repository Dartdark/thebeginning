"""Placebo for the funded 'ALL skips together' result of analysis/apex_sweep.py (blown 2.2% -> 0.2%, +$280). FAIR version (selection
mimicked): for each piece, 63 random day splits with the on-shares of its 63 real regimes; pick the one with the largest same-sign gap |t|
(as the real sweep did) and skip its unfavourable days; all pieces together; 10 runs on the same funded 150K bench. Information.
  tools/run_stamped.sh analysis/apex_sweep_placebo.py > analysis/outputs/apex_sweep_placebo_output.txt
"""
import sys, io, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import bench150 as BB
from new_data_screen import RULES, prior
from data_sweep import series
from apex_sweep import screen

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    ctx = BB.setup(); lab = ctx["lab"]; ld = pd.DatetimeIndex(lab.g.ts[lab.tr]).normalize(); S = series()
    fk = {"VB": "VB", "ONB ML": "ONB_ML2_MC", "Monday Long": "MON_MC", "EOS": "EOS", "LDF": "LDF_MC", "NFP": "NFP_MC", "Bridge Monday": "MON_BR_MC", "CL fade": "CLS", "Twin": "TWIN"}
    R0 = screen({p: np.asarray(lab.C[k], float) for p, k in fk.items()}, ld, S); R = R0[R0.same]
    share = {}
    for p in fk:
        r = R[R.piece == p].reindex(R[R.piece == p].t.abs().sort_values(ascending=False).index).iloc[0]
        on = prior(S[r.series], ld, RULES[r.rule]) == 1; keep = on if r.t > 0 else ~on; share[p] = 1 - keep.mean()
    print("   skipped share of days per piece:", {p: f"{v:.0%}" for p, v in share.items()})
    rng = np.random.default_rng(21); ext, var = {}, {}
    for run in range(10):
        plan = dict(BB.BASE_FUNDED)
        for p, k in fk.items():
            x = np.asarray(lab.C[k], float); act = x != 0; v = x[act]; e = ld[act].year <= 2022; best = (-1, None)
            for sh in R0[R0.piece == p].share.values:
                h_all = rng.random(len(ld)) < sh; h = h_all[act]
                if h.sum() < 15 or (~h).sum() < 15: continue
                a_, b_ = v[h], v[~h]; t = (a_.mean() - b_.mean()) / np.sqrt(a_.var() / len(a_) + b_.var() / len(b_))
                same = np.sign(v[e & h].mean() - v[e & ~h].mean()) == np.sign(v[~e & h].mean() - v[~e & ~h].mean())
                if same and abs(t) > best[0]: best = (abs(t), h_all if t > 0 else ~h_all)
            m = best[1].astype(float)
            for kk in (["VB_N", "VB_F"] if k == "VB" else [k]):
                if kk not in plan: continue
                nk = f"{kk}_R{run}"; ext[nk] = (lab.W[kk] * m[:, None], lab.C[kk] * m); plan[nk] = plan.pop(kk)
                if kk in lab.stop: lab.stop[nk] = lab.stop[kk]
        var[f"random skips run {run}"] = plan
    BB.funded_bench(ctx, var, extra=ext)
