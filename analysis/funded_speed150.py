"""150K funded book at ONE year (user 2026-11-13: improve the funded book's big pieces). The 2-year bench is cap-bound (base pays $20,245,
98.7% reach all 6 payouts: analysis/outputs/funded_resize150_output.txt), so sizes / leads can only change SPEED and blown risk. This runs
the informative variants from the resize and leads benches at 250 trading days (same 600 paired histories, cushion sizing).
  tools/run_stamped.sh analysis/funded_speed150.py > analysis/outputs/funded_speed150_output.txt
"""
import sys, io, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import bench150 as BN
print(__doc__.split("\n")[0])
ctx = BN.setup(); lab = ctx["lab"]; dts = ctx["dts"]; B = BN.LIVE_FUNDED
with contextlib.redirect_stdout(io.StringIO()):
    ou = runpy.run_path("analysis/ou_regime_test.py"); Dou = ou["build"]("NQ")[4]
mr = Dou.mr.reindex(dts).fillna(False).to_numpy().astype(bool)
for suf, mm in (("F", mr), ("N", ~mr)): lab.W["LDF_MC_MR" + suf] = lab.W["LDF_MC"] * mm[:, None]; lab.C["LDF_MC_MR" + suf] = lab.C["LDF_MC"] * mm
d = lambda k: {a: b for a, b in B.items() if a != k}
V = {"TWIN -> 0": d("TWIN"), "TWIN x0.5": {**B, "TWIN": 1}, "ONB_ML x0.5 ($300)": {**B, "ONB_ML2_MC": ("risk", 300.0)},
     "ONB_ML x1.5 ($900)": {**B, "ONB_ML2_MC": ("risk", 900.0)}, "EOS x0.5 ($500)": {**B, "EOS": ("risk", 500.0)},
     "LDF x1.5 (4.5)": {**B, "LDF_MC": 4.5}, "#16 LDF MR 4.5 / other 3": {**d("LDF_MC"), "LDF_MC_MRF": 4.5, "LDF_MC_MRN": 3.0},
     "DT -> 0": d("DT"), "CLS -> 0": d("CLS"), "OT -> 0": d("OT"), "OT x1.5 (3)": {**B, "OT": 3}}
BN.funded_bench(ctx, V, H=250, label="Funded 150K (LIVE_FUNDED), 1 YEAR")
