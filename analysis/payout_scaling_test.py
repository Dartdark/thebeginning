"""Scaling up size as a funded account grows (user, 2026-10-15). Two ways, on the current plan, 50K and 150K (Apex's real
ladders, analysis/funded_sim.py / funded_sim150.py):
  cushion   size f = cushion / ref (cushion = balance - drawdown threshold), now capped at 1 (full size); let it go above:
            fmax 1.25 / 1.5 / 2 (more size the further the account is above its threshold)
  stage     multiply all sizes after each payout: 'mild' 1 / 1 / 1.25 / 1.25 / 1.5 / 1.5, 'ladder' = the payout caps relative
            to the first (50K 1 / 1 / 1.33 / 1.67 / 1.67 / 2; 150K 1 / 1.2 / 1.2 / 1.2 / 1.6 / 2), 'bold' 1 / 1.5 / 2 / 2 / 2 / 2
After a payout the balance sits at least at the safety net, i.e. $2,000 above the locked threshold on the 50K ($4,000 on
the 150K), so the account's own buffer grows as payouts are taken. Reported: expected payouts 1 / 2 years, blown, all 6
within 2 years, median trading days to the 6th payout (accounts that finish). Every start day.
  python3 analysis/payout_scaling_test.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import funded_sim as F50, funded_sim150 as F150

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    g = lab.g; dates = pd.DatetimeIndex(g.ts[lab.tr])
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    PLAN = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    sc = lambda plan, k: {n: (("risk", v[1] * k) if isinstance(v, tuple) else v * k) for n, v in plan.items()}
    def bench(F, plan, ref, fmax, stage, nm):
        names, b = lab._base(plan)
        W = np.stack([lab.W[k] for k in names]); C = np.stack([lab.C[k] for k in names]); out = []
        for h in (250, 500):
            r = F.simulate_sized(W, C, b, horizon=h, starts=np.arange(0, lab.D - h), fmin=0.5, fmax=fmax, ref=ref, stage=np.asarray(stage, float))
            fin = r["days"][r["payouts"] == 6]
            out.append((r["paid"].mean(), r["blown"].mean(), np.mean(r["payouts"] == 6), np.median(fin) if len(fin) else np.nan))
        print(f"   {nm:<44} 1y ${out[0][0]:>7,.0f} blown {out[0][1]:>4.0%} | 2y ${out[1][0]:>7,.0f} blown {out[1][1]:>4.0%} all 6 {out[1][2]:>4.0%} "
              f"median days to 6th {out[1][3]:>4.0f}", flush=True)
    ONE = [1] * 6
    for size, F, plan, ref, ladder in (("50K", F50, PLAN, 1500.0, [1, 1, 1.33, 1.67, 1.67, 2]),
                                       ("150K", F150, sc(PLAN, 1.5), 3000.0, [1, 1.2, 1.2, 1.2, 1.6, 2])):
        print(f"\n== {size} (current: full size from ${ref:,.0f} cushion, capped at 1)")
        bench(F, plan, ref, 1.0, ONE, "current")
        for fm in (1.25, 1.5, 2.0): bench(F, plan, ref, fm, ONE, f"cushion: fmax {fm}")
        for nm, st in (("mild", [1, 1, 1.25, 1.25, 1.5, 1.5]), ("ladder", ladder), ("bold", [1, 1.5, 2, 2, 2, 2])):
            bench(F, plan, ref, 1.0, st, f"stage: {nm} {st}")
        bench(F, plan, ref, 1.5, [1, 1, 1.25, 1.25, 1.5, 1.5], "cushion fmax 1.5 + stage mild")
