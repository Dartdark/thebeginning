"""Volatility-Volume-Gap day classifier on NQ 2018-2026 (paper: Mesfin 2026, arXiv 2605.11423; scout 2026-10-29). Paper (MNQ
5-min 2021-25, 40 classifier days): a day is VVG when |overnight gap|, |first-30-minute return| and first-bar volume (vs 20-day
mean) all exceed their expanding 66.7th percentiles; 77.6% reverse from the intraday peak, next-day return +25.6 bp vs other
days; every trade the author built failed (too few days). Our longer sample, fixed before looking: gap = 08:30 open vs prior
15:00 close; r1 = 08:30 -> 09:00; volume = first 5 minutes vs its 20-day mean; thresholds expanding from day 61. Outcomes per
NQ after $7.25 + 1 tick a side: (a) next-day long, 08:30 -> 15:00 and 15:00 -> next 15:00 (holds overnight: personal only);
(b) fade the 08:30 -> 14:30 move from 14:30 to 15:00 (the paper's peak-reversal idea); controls = the same on all other days.
python3 analysis/vvg_classifier_test.py
"""
import glob, numpy as np, pandas as pd
PV, COST = 20, 7.25 + 2 * 0.25 * 20
d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/NQ_1min_20*.csv")) if "_ON_" not in f])
g = d.groupby("date")
def at(t, col): return d[d.time == t].set_index("date")[col]
x = pd.DataFrame(dict(o=at(831, "open"), c900=at(900, "close"), c1430=at(1430, "close"), c=at(1500, "close"),
                      v5=d[(d.time > 830) & (d.time <= 835)].groupby("date").volume.sum())).dropna()
x.index = pd.to_datetime(x.index.astype(str))
x["gap"] = (np.log(x.o / x.c.shift(1))).abs(); x["r1"] = np.log(x.c900 / x.o).abs(); x["vdev"] = x.v5 / x.v5.rolling(20).mean().shift(1)
rw = x.index.month.isin([3, 6, 9, 12]) & (x.index.day >= 8) & (x.index.day <= 17)
x.loc[rw, "gap"] = np.nan                                                        # unadjusted roll jumps
th = {k: x[k].expanding(60).quantile(2 / 3).shift(1) for k in ("gap", "r1", "vdev")}
x["vvg"] = (x.gap > th["gap"]) & (x.r1 > th["r1"]) & (x.vdev > th["vdev"])
x["nd_rth"] = (x.c.shift(-1) - x.o.shift(-1)) * PV - COST; x["nd_cc"] = (x.c.shift(-1) - x.c) * PV - COST
x.loc[rw | np.roll(rw, -1), "nd_cc"] = np.nan
x["fade"] = -np.sign(x.c1430 - x.o) * (x.c - x.c1430) * PV - COST
x = x[x.index >= "2018-01-01"]
def show(nm, s):
    s = s.dropna(); print(f"   {nm:40s} n {len(s):4d}  ${s.mean():+6.0f}  t {s.mean() / s.std() * np.sqrt(len(s)):+.1f}  win {np.mean(s > 0):.0%}")
print(__doc__.split("\n")[0]); print(f"VVG days {x.vvg.sum()} of {len(x)} ({x.vvg.mean():.1%})")
for col, nm in (("nd_rth", "next-day long 08:30 -> 15:00"), ("nd_cc", "next-day long 15:00 -> 15:00"), ("fade", "fade 14:30 -> 15:00")):
    show(f"{nm}, VVG days", x[col][x.vvg]); show(f"{nm}, other days", x[col][~x.vvg])
for per, m in (("2018-22", x.index < "2023"), ("2023+", x.index >= "2023")):
    show(f"fade 14:30 -> 15:00, VVG {per}", x.fade[x.vvg & m]); show(f"next-day 08:30 -> 15:00, VVG {per}", x.nd_rth[x.vvg & m])
