"""Standing screen (user 2026-11-10: 'consider all strategies in new data to see if they could improve them'): split EVERY piece of
the personal book (scratch_data/personal_P.pkl, daily P&L per micro, on each piece's active days) by a regime built from a daily
data series, and flag pieces whose gap clears the multiple-testing bar with the same sign in 2018-22 and 2023+.
Regimes (value = the series' last close BEFORE each day, no look-ahead):
  above_median   value > median of its past 252 closes
  z_high         z of the value vs its past 60 closes >= 1
  rising         value > its value 20 closes earlier
Usage:
  python3 analysis/new_data_screen.py CSV DATE_COL VALUE_COL REGIME [NAME]
  e.g. python3 analysis/new_data_screen.py data/codex_20261108/OVX.csv date close_index_points above_median OVX
A flagged piece is a LEAD (screen result): next steps are its book bench (post hoc, information) and an out-of-sample check
(older data or the forward log) before any plan change (DEVELOPMENT_PROCESS 'New data: screen every piece').
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from metrics import t_threshold
from new_data_filters_test import prior

RULES = {"above_median": lambda s: float(s.iloc[-1] > s.iloc[-252:].median()) if len(s) >= 120 else np.nan,
         "z_high": lambda s: float((s.iloc[-1] - s.iloc[-61:-1].mean()) / s.iloc[-61:-1].std() >= 1.0) if len(s) >= 61 else np.nan,
         "rising": lambda s: float(s.iloc[-1] > s.iloc[-21]) if len(s) >= 21 else np.nan}


def screen(series, rule, name="series", P=None):
    P = pd.read_pickle("scratch_data/personal_P.pkl") if P is None else P
    on = pd.Series(prior(series, P.index, RULES[rule]) == 1, index=P.index); bar = t_threshold(len(P.columns))
    print(f"   {name} / {rule}: regime ON {on.mean():.0%} of days; bar |t| >= {bar:.2f} for {len(P.columns)} pieces")
    print(f"   {'piece':<22}{'n on/off':>10}{'$ on':>8}{'$ off':>8}{'diff t':>8}  {'18-22 on/off':>14}  {'23+ on/off':>14}")
    rows = []
    for c in P.columns:
        x = P[c][P[c] != 0]; h = on.reindex(x.index).values; a, b = x[h], x[~h]
        if len(a) < 10 or len(b) < 10: continue
        t = (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b)); e = x.index.year <= 2022
        g1, g2 = x[e & h].mean() - x[e & ~h].mean(), x[~e & h].mean() - x[~e & ~h].mean()
        flag = abs(t) >= bar and np.sign(g1) == np.sign(g2)
        print(f"   {c:<22}{len(a):>5}/{len(b):<4}{a.mean():8.0f}{b.mean():8.0f}{t:8.2f}  {x[e & h].mean():6.0f}/{x[e & ~h].mean():<6.0f}  {x[~e & h].mean():6.0f}/{x[~e & ~h].mean():<6.0f}{' <- LEAD' if flag else ''}")
        rows.append(dict(piece=c, t=t, same_sign=np.sign(g1) == np.sign(g2), lead=flag))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    f, dc, vc, rule = sys.argv[1:5]; nm = sys.argv[5] if len(sys.argv) > 5 else vc
    s = pd.read_csv(f, parse_dates=[dc]).set_index(dc)[vc].astype(float).dropna().sort_index()
    print(__doc__.split("\n")[0]); screen(s, rule, nm)
