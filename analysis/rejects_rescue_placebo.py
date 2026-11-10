"""Placebo for the 'rescue' subsets of analysis/rejects_sweep.py (user 2026-11-10: 'I'm seeing 9 leads then?'). For each listed
strategy: the best subset t over 63 RANDOM day splits (same on-shares as its 63 real regimes, positive in both periods, >= 40 trades),
200 runs -> how often luck matches the real best-regime subset t (p). Information.
  tools/run_stamped.sh analysis/rejects_rescue_placebo.py > analysis/outputs/rejects_rescue_placebo_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from rejects_sweep import load

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    R = pd.read_csv("analysis/outputs/rejects_sweep_table.csv")
    picks = {"twin_rth_bo": 5.76, "ricochet_1144": 4.22, "donchian_morning_apex": 4.00, "finra_short": 3.99, "gc_combo": 3.90, "fade_ym": 3.29,
             "turn_of_month": 3.31, "ot_anyday": 5.56, "ot_es": 5.26}
    rng = np.random.default_rng(1)
    for n, real in picks.items():
        x = load(n); x = x[x.index >= "2018-01-01"]; shares = R[R.strategy == n].n_sub.values / len(x); e = x.index.year <= 2022; best = []
        for run in range(200):
            bt = -9
            for sh in shares:
                m = rng.random(len(x)) < sh; sub = x[m]
                if len(sub) >= 40 and sub[e[m]].mean() > 0 and sub[~e[m]].mean() > 0: bt = max(bt, sub.mean() / sub.std() * np.sqrt(len(sub)))
            best.append(bt)
        best = np.array(best)
        print(f"   {n:<22} all t {x.mean() / x.std() * np.sqrt(len(x)):.2f} | real best-regime subset t {real:.2f} | random best-of-63: median {np.median(best):.2f}, 95th {np.percentile(best, 95):.2f} | p {np.mean(best >= real):.3f}", flush=True)
