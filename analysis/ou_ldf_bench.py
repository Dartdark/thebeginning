"""Funded bench: Late-Day Flow sized by the NQ OU regime (analysis/ou_regime_test.py, part C: LDF $191 a trade when the prior-20-
session theta is above its 120-day average vs $19 otherwise, t 3.1, design +$128 / holdout +$218; 1 of 8 strategies tested).
Plan = funded plan with the single-print VB (3 / flagged 1) + CL fade 2 MCL, cushion $1,500. Placebo: random-day split.
  python3 analysis/ou_ldf_bench.py [SCRATCH_DIR]   (run ou_regime_test.py and single_print_test.py first)
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
        ou = runpy.run_path("analysis/ou_regime_test.py")
        D = ou["build"]("NQ")[4]
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    mr = D.mr.reindex(dates).fillna(False).to_numpy().astype(bool)
    print(f"bench days {len(dates)}, MR regime {mr.mean():.0%}; LDF $/NQ a day MR {lab.daily('LDF_MC')[mr].mean():.1f}, other {lab.daily('LDF_MC')[~mr].mean():.1f}")

    def split(name, m, tag):
        lab.W[name + tag + "F"] = lab.W[name] * m[:, None]; lab.C[name + tag + "F"] = lab.C[name] * m
        lab.W[name + tag + "N"] = lab.W[name] * ~m[:, None]; lab.C[name + tag + "N"] = lab.C[name] * ~m
    split("VB", flag, "_"); split("LDF_MC", mr, "_")
    base = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    sc = lambda p: (lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0))
    res = {}
    for nm, p in (("plan (LDF 2)", {**base, "LDF_MC": 2}), ("LDF MR 3 / trend 1", {**base, "LDF_MC_F": 3, "LDF_MC_N": 1}),
                  ("LDF MR 2 / trend 1", {**base, "LDF_MC_F": 2, "LDF_MC_N": 1}), ("LDF MR 3 / trend 2", {**base, "LDF_MC_F": 3, "LDF_MC_N": 2})):
        r = res[nm] = sc(p)
        print(f"   {nm:<24} ${r[0]['expected']:,.0f} / ${r[1]['expected']:,.0f}  blown {r[0]['blown']:.0%} / {r[1]['blown']:.0%}"
              f" | 1y 2018-22 ${r[0]['s2018_22']:,.0f} 2023+ ${r[0]['s2023_on']:,.0f}")
    rng = np.random.default_rng(9); pe = []
    for i in range(15):
        m = rng.random(len(dates)) < mr.mean(); split("LDF_MC", m, f"_r{i}")
        pe.append(sc({**base, f"LDF_MC_r{i}F": 3, f"LDF_MC_r{i}N": 1})[0]["expected"])
    pe = np.array(pe); real = res["LDF MR 3 / trend 1"][0]["expected"]
    print(f"   placebo LDF 3 / 1 on random days (15): mean ${pe.mean():,.0f}, max ${pe.max():,.0f}; share >= real {np.mean(pe >= real):.2f}")
