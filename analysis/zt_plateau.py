"""ZT continuation threshold plateau (2026-11-09, after the ablation: EntryZ 1.0 t 3.03, 1.25 t 3.50, 1.5 t 0.66 on 15-min). Information
only: EntryZ 0.9 -> 1.6 in 0.05 steps, 15-min and 30-min, everything else as the ablation base; longs / shorts t.
  tools/run_stamped.sh analysis/zt_plateau.py > analysis/outputs/zt_plateau_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from donchian_lwti_test import series
import zt_ablation as A

if __name__ == "__main__":
    print(__doc__.split("\n")[0]); g = pickle.load(open("scratch_data/g24.pkl", "rb"))
    tt = lambda x: x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan
    for k in (15, 30):
        s = series(g, k); z = A.zser(s); print(f"\n {k}-min:")
        for ez in np.round(np.arange(0.9, 1.61, 0.05), 2):
            T = A.run(g, s, z, entry=ez); a, b = T[T.date < "2023"].net, T[T.date >= "2023"].net
            print(f"   EntryZ {ez:4.2f} n {len(T):5d} ${T.net.mean():5.0f} t {tt(T.net):5.2f} | 18-22 ${a.mean():4.0f} 23+ ${b.mean():4.0f} | L t {tt(T[T.side > 0].net):4.1f} S t {tt(T[T.side < 0].net):4.1f} | worst day ${T.groupby(T.date).net.sum().min():,.0f}", flush=True)
