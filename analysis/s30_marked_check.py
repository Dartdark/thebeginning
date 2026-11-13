"""S30 NQ lead after Codex's 2026-11-08 ingredient study (agents/codex/results/ingredients_s30_s47_kusho_20261108.md: marked DD $59.5k vs
$37.7k booked at exits; 'entry advantage changes by era' - unrestricted entry did as well as IBS < 0.20 recently). Information only.
Per NQ, marked to market daily at the 15:00 close (roll jumps removed; same builder as bench_leads_book_test): total by period and marked
max DD for entry IBS < 0.10 / < 0.20 / any session (unrestricted, Codex's control), same exit (IBS > 0.80).
  tools/run_stamped.sh analysis/s30_marked_check.py > analysis/outputs/s30_marked_check_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np
src = open("analysis/bench_leads_book_test.py").read(); head, main = src.split('if __name__ == "__main__":')
ns = {}; exec(head, ns); exec("def _m():\n" + main.split("    s20, n20")[0] + "\n    return locals()\n", ns); L = ns["_m"]()
idx = L["idx"]; print(__doc__.split("\n")[0])
for lo, nm in ((0.10, "IBS < 0.10 (lead)"), (0.20, "IBS < 0.20 (bench)"), (1.01, "any session (unrestricted)")):
    s, n = L["s30_daily"](lo); x = s * 10                                  # per NQ
    out = [f"   {nm:<28} trades {n:3d}"]
    for p, m in (("2018-22", idx.year <= 2022), ("2023+", idx.year >= 2023), ("2018-26", idx.year >= 2018)):
        c = x[m].cumsum(); out.append(f"{p} ${x[m].sum() / 1000:5.0f}k maxDD ${(c.cummax() - c).max() / 1000:4.1f}k Sharpe {x[m].mean() / x[m].std() * np.sqrt(252):.2f}")
    print(" | ".join(out), flush=True)
