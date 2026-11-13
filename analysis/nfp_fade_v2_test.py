"""NFP Fade v2 (pre-registered: checks/candidates/nfp_fade/PREREG_v2.md, user 2026-11-13): V1 AGREE filter, V2 two legs, vs our live rule.
  tools/run_stamped.sh analysis/nfp_fade_v2_test.py > analysis/outputs/nfp_fade_v2_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
src = open("analysis/nfp_5min_fade_check.py").read().split("def tt(x)")[0]
exec(compile(src, "nfp_head", "exec"))
print(__doc__.split("\n")[0])
def tt(x): return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan
def leg(r, react, t1, stop):
    t = trade(r, react, t1, stop)
    if t is None: return None
    s, e, px, why = t; return s, (px - e) * s * 20 - 7.25 - 10.0
rows = []
for r in days:
    a = leg(r, 735, 830, None); b = leg(r, 745, 900, 0.5)
    if b is None: continue
    rows.append((ts[r], b[1], a[0] if a else 0, b[0], a[1] if a else np.nan))
T = pd.DataFrame(rows, columns=["date", "base", "s35", "s45", "his"])
T["v1"] = np.where(T.s35 == T.s45, T.base, np.nan)
T["v2"] = 0.5 * T.base + 0.5 * T.his.fillna(0)
def line(x, nm):
    x = x.dropna(); yy = T.date[x.index].dt.year; a, b = x[yy <= 2022], x[yy >= 2023]
    eq = x.cumsum(); dd = (eq - eq.cummax()).min(); sh = x.mean() / x.std() * np.sqrt(9)
    return (f"   {nm:<40} n {len(x):2d} avg ${x.mean():5.0f} t {tt(x):4.2f} win {np.mean(x > 0):.0%} maxDD ${dd:,.0f} Sharpe/yr {sh:.2f} | "
            f"2018-22 ${a.mean():5.0f} (t {tt(a):4.1f}, n {len(a)}) | 2023-26 ${b.mean():5.0f} (t {tt(b):4.1f}, n {len(b)})")
print(line(T.base, "BASE our NFP Fade")); print(line(T.v1, "V1 AGREE (07:35 and 07:45 same sign)")); print(line(T.v2, "V2 two legs, half size each"))
print(line(T.his, "(his rule alone, reference)"))
dis = T[T.s35 != T.s45]; print(f"   days the two signals DISAGREE: {len(dis)}; our trade on them avg ${dis.base.mean():.0f} (t {tt(dis.base):.2f}); his leg on them avg ${dis.his.mean():.0f}")
