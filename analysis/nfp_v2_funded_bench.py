"""NFP Fade v2 (two legs) as a REPLACEMENT of the NFP Fade in the funded plan (user 2026-11-13; prereg checks/candidates/nfp_fade/PREREG_v2.md).
Funded bench (bench150.funded_bench: 150K x 1.5 + Twin 2, 600 paired 2-year histories, cushion sizing). The plan's NFP Fade = NFP_MC
(MultiCharts trades) at risk $750 (= $500 x 1.5). Variants, same total risk:
  V2      NFP_MC at $375 + his leg (07:36 -> 08:30, no stop) sized like NFP_MC's contracts at $375 (half size each)
  his     his leg alone at $750 (same contracts as the plan's NFP)
  half    NFP_MC at $375 only (control: is any gain just less NFP?)
  none    NFP removed (control)
His-leg trades from analysis/nfp_5min_fade_check.py (same NFP days, our costs: $7.25 + 1 tick a side). No stop on his leg: sized by the
0.5 ATR stop distance of our leg only to match contract counts (its real worst trade is larger: reported).
  tools/run_stamped.sh analysis/nfp_v2_funded_bench.py > analysis/outputs/nfp_v2_funded_bench_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
src = open("analysis/nfp_5min_fade_check.py").read().split("def tt(x)")[0]; exec(compile(src, "nfp_head", "exec"))
import bench150 as BN
from build_lab import REPORTS
print(__doc__.split("\n")[0])
ctx = BN.setup(); lab = ctx["lab"]
rows = []
for r in days:
    t = trade(r, 735, 830)
    if t is None: continue
    s, e, px, why = t; rows.append((r, jof(735) + 1, jof(830), s, e, px, 2))
T = pd.DataFrame(rows, columns=["day", "j0", "j1", "side", "entry", "exit", "kind"])
lab.add("NFP_HIS", T, stop_pts=REPORTS["NFP_MC"][1] * g.daily_atr(15))
print(f"his leg: {len(T)} trades; worst per NQ ${((T.exit - T.entry) * T.side * 20).min() - 17.25:,.0f}; NFP_MC days {int((lab.C['NFP_MC'] != 0).sum())}")
d = lab.C["NFP_MC"]; h = lab.C["NFP_HIS"]; both = (d != 0) & (h != 0)
print(f"daily corr (days both trade, per MNQ unit): {np.corrcoef(d[both], h[both])[0, 1]:+.2f} on {both.sum()} days")
B = BN.BASE_FUNDED; print(f"funded base: {B}")
drop = {k: v for k, v in B.items() if k != "NFP_MC"}
V = {"V2: NFP $375 + his leg $375": {**drop, "NFP_MC": ("risk", 375.0), "NFP_HIS": ("risk", 375.0)},
     "his leg alone $750": {**drop, "NFP_HIS": ("risk", 750.0)},
     "half: NFP $375 only (control)": {**drop, "NFP_MC": ("risk", 375.0)},
     "no NFP (control)": drop}
BN.funded_bench(ctx, V)
