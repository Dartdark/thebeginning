"""Late-Day Flow in the 150K funded plan as whole contracts (user 2026-11-13: 'yea do that' -> LDF 3 -> 4.5 from funded_speed150; a chart
needs an integer). Plan (LIVE_FUNDED, LDF 3) vs LDF 4 and 5, 1 year and 2 years, 600 paired histories, cushion sizing.
  tools/run_stamped.sh analysis/funded_ldf_int150.py > analysis/outputs/funded_ldf_int150_output.txt
"""
import sys; sys.path.insert(0, "analysis")
import bench150 as BN
print(__doc__.split("\n")[0])
ctx = BN.setup(); B = dict(BN.LIVE_FUNDED); B["LDF_MC"] = 3.0
V = {"LDF 4": {**B, "LDF_MC": 4.0}, "LDF 5": {**B, "LDF_MC": 5.0}}
BN.funded_bench(ctx, V, H=250, label="Funded 150K, 1 YEAR"); BN.funded_bench(ctx, V, H=500, label="Funded 150K, 2 YEARS")
