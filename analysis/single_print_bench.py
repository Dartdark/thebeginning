"""Funded bench for the single-print day flag (analysis/single_print_test.py, Red Ledger RL-FS-2026-01): size the breakout
strategies (Vault Break, Overnight Bias ML) down on sessions after an interior single print.
Plan = current funded plan + CL fade 2 MCL, cushion $1,500 (1 year / 2 years, blown). Placebo: VB cut on a random 30% of days.
  python3 analysis/single_print_bench.py [SCRATCH_DIR]   (run single_print_test.py first)
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    S = pd.read_pickle(SP + "single_print_sessions.pkl")
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    print(f"bench days {len(dates)}, flagged {flag.mean():.0%}")

    def split(name, m, tag):
        lab.W[name + tag + "F"] = lab.W[name] * m[:, None]; lab.C[name + tag + "F"] = lab.C[name] * m
        lab.W[name + tag + "N"] = lab.W[name] * ~m[:, None]; lab.C[name + tag + "N"] = lab.C[name] * ~m
        if name in lab.stop: lab.stop[name + tag + "F"] = lab.stop[name + tag + "N"] = lab.stop[name]
    split("VB", flag, "_"); split("ONB_ML2_MC", flag, "_")
    for k in ("VB", "ONB_ML2_MC"):
        print(f"   {k}: $/NQ a day flagged {lab.daily(k)[flag].mean():.1f}, other {lab.daily(k)[~flag].mean():.1f}")
    base = {"MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    onb = {"ONB_ML2_MC": ("risk", 400)}
    sc = lambda p: (lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0))
    show = lambda nm, r: print(f"   {nm:<40} ${r[0]['expected']:,.0f} / ${r[1]['expected']:,.0f}  blown {r[0]['blown']:.0%} / {r[1]['blown']:.0%}"
                               f" | 1y 2018-22 ${r[0]['s2018_22']:,.0f} 2023+ ${r[0]['s2023_on']:,.0f}")
    res = {}
    for nm, p in (("plan (VB 3)", {**base, **onb, "VB": 3}),
                  ("VB 3 / flagged 2", {**base, **onb, "VB_N": 3, "VB_F": 2}),
                  ("VB 3 / flagged 1", {**base, **onb, "VB_N": 3, "VB_F": 1}),
                  ("VB 3 / flagged 0", {**base, **onb, "VB_N": 3, "VB_F": 0}),
                  ("VB 4 / flagged 1", {**base, **onb, "VB_N": 4, "VB_F": 1}),
                  ("VB 3 / flagged 1 + ONB $400 / flagged $200", {**base, "ONB_ML2_MC_N": ("risk", 400), "ONB_ML2_MC_F": ("risk", 200), "VB_N": 3, "VB_F": 1}),
                  ("ONB $400 / flagged $200 only", {**base, "ONB_ML2_MC_N": ("risk", 400), "ONB_ML2_MC_F": ("risk", 200), "VB": 3})):
        res[nm] = sc(p); show(nm, res[nm])
    print("\n   placebo: VB 3 / 1 on a random 30% of days (20 draws)")
    rng = np.random.default_rng(5); pe = []
    for i in range(20):
        m = rng.random(len(dates)) < flag.mean(); split("VB", m, f"_r{i}")
        pe.append(sc({**base, **onb, f"VB_r{i}N": 3, f"VB_r{i}F": 1})[0]["expected"])
    pe = np.array(pe); real = res["VB 3 / flagged 1"][0]["expected"]
    print(f"   real ${real:,.0f}; placebo mean ${pe.mean():,.0f}, max ${pe.max():,.0f}; share >= real {np.mean(pe >= real):.2f}")
