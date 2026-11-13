"""S30 NQ entry-threshold sensitivity in the current personal book (2026-11-08; information only, run after bench_leads_book_test.py
flagged IBS < 0.10, to check that the lead sits on a plateau, not a spike). Reuses that script's daily-marked S30 builder.
  tools/run_stamped.sh analysis/s30_threshold_sensitivity.py > analysis/outputs/s30_threshold_sensitivity_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, montecarlo as MC
src = open("analysis/bench_leads_book_test.py").read()
head, main = src.split('if __name__ == "__main__":')
ns = {}; exec(head, ns); exec("def _m():\n" + main.split("    s20, n20")[0] + "\n    return locals()\n", ns); L = ns["_m"]()
base, idx = L["base"], L["idx"]
mcf = lambda x: (lambda d: d["pnl_p50"] / d["dd_p95"])(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1))
per = {"2018-26": np.ones(len(idx), bool), "2018-22": idx.year <= 2022, "2023+": idx.year >= 2023}
b = {p: mcf(base[m]) for p, m in per.items()}
print(__doc__.split("\n")[0]); print("   base " + " | ".join(f"{p} {v:.2f}" for p, v in b.items()))
for lo in (0.05, 0.075, 0.10, 0.125, 0.15, 0.20):
    s, n = L["s30_daily"](lo)
    print(f"   IBS < {lo:<5} trades {n:3d} | " + " | ".join(f"{p} {mcf((base + s)[m]):.2f} ({mcf((base + s)[m]) - b[p]:+.2f})" for p, m in per.items()), flush=True)
