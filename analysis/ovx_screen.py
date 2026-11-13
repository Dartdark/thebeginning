"""OVX regime screen of every personal-book piece (user 2026-11-10: 'can we use OVX on something else?'). Information / screen:
each piece's daily P&L (per micro, scratch_data/personal_P.pkl) on its active days, split by oil-volatility regime (the previous
OVX close above the median of its past 252 closes); difference t, both periods. ~20 items: a piece goes to a pre-registered test
only if |t| >= metrics.t_threshold(20) (~2.8) AND the gap has the same sign in 2018-22 and 2023+.
  tools/run_stamped.sh analysis/ovx_screen.py > analysis/outputs/ovx_screen_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from metrics import t_threshold
from new_data_filters_test import prior

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    P = pd.read_pickle("scratch_data/personal_P.pkl"); ovx = pd.read_csv("data/codex_20261108/OVX.csv", parse_dates=["date"]).set_index("date").close_index_points.astype(float)
    hi = pd.Series(prior(ovx, P.index, lambda s: float(s.iloc[-1] > s.iloc[-252:].median()) if len(s) >= 120 else np.nan) == 1, index=P.index)
    print(f"   high-OVX days {hi.mean():.0%}; bar |t| >= {t_threshold(len(P.columns)):.2f} for {len(P.columns)} pieces\n")
    print(f"   {'piece':<22}{'n hi/lo':>10}{'$ hi':>8}{'$ lo':>8}{'diff t':>8}  {'18-22 hi/lo':>14}  {'23+ hi/lo':>14}")
    for c in P.columns:
        x = P[c][P[c] != 0]; h = hi.reindex(x.index); a, b = x[h], x[~h]
        if len(a) < 10 or len(b) < 10: continue
        t = (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))
        e = x.index.year <= 2022
        f = lambda m: f"{x[m & h.values].mean():6.0f}/{x[m & ~h.values].mean():<6.0f}"
        flag = " <-" if abs(t) >= t_threshold(len(P.columns)) and np.sign(x[e & h.values].mean() - x[e & ~h.values].mean()) == np.sign(x[~e & h.values].mean() - x[~e & ~h.values].mean()) else ""
        print(f"   {c:<22}{len(a):>5}/{len(b):<4}{a.mean():8.0f}{b.mean():8.0f}{t:8.2f}  {f(e):>14}  {f(~e):>14}{flag}")
