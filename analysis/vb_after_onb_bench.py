"""Funded bench for watchlist #15 (2026-10-14): extra Vault Break MNQ only on VB trades that enter after Overnight Bias ML has
gone long the same day (VB after an ONB ML long: $214 a trade vs $64 otherwise, t 2.55; analysis/plan_agreement_test.py).
Plan = the current funded plan (VB 3, ONB ML $400, Monday 1, EOS $700, LDF 2, NFP $500, Bridge Monday 1, CL fade 2 MCL), as in
analysis/cl_sunday_fade_bench.py; 'VBX' = the boosted VB trades as a separate stream, + 1 / 2 / 3 MNQ. Cushion sizing
f = clip(cushion / ref, 0.5, 1) with ref $1,500 (bench) and $1,000 (live recommendation).
Needs scratch lab.pkl (analysis/build_lab.py) and s_rank_gap2.pkl (analysis/s_rank_gap_round2_test.py).
  python3 analysis/vb_after_onb_bench.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc
from speed_to_13k import run as speed, fmt

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    # the CL-fade bench builds the lab with CLS (the CL fade) added; reuse its namespace
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        ns = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")
    lab, g = ns["lab"], ns["lab"].g
    vb = load_mc(g, "mc_reports/Backtesting Strategy Performance Report VB v1.xlsx")
    onb = load_mc(g, "mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx")
    ol = onb[onb.side == 1].groupby("day").j0.min()
    m = vb.day.map(ol); vbx = vb[m.notna() & (vb.j0 > m)].reset_index(drop=True)
    print(f"VB trades {len(vb)}, boosted subset {len(vbx)}")
    atr = g.daily_atr(15); lab.add("VBX", vbx, stop_pts=0.30 * atr)
    print("daily correlation VBX with:", {k: round(float(np.corrcoef(lab.C["VBX"], lab.C[k])[0, 1]), 2) for k in ("VB", "ONB_ML2_MC", "LDF_MC", "CLS")})
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500),
            "MON_BR_MC": 1, "CLS": 2}
    out = {}
    for ref in (1500.0, 1000.0):
        for q in (0, 1, 2, 3):
            p = {**plan, "VBX": q} if q else plan
            a, c = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=ref), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=ref)
            nm = f"cushion ${ref:,.0f}: plan" + (f" + VBX {q} MNQ" if q else "")
            print(f"   {nm:<36} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}"
                  f" | 1y 2018-22 ${a['s2018_22']:,.0f} 2023+ ${a['s2023_on']:,.0f}")
            out[nm] = speed(lab, p, fmin=0.5, fmax=1.0, ref=ref)
    print(fmt(pd.DataFrame(out).T))
