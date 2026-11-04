"""How often a 12-trading-day stretch as bad as 2026-10-20 -> 11-04 shows up in the backtest (user, 2026-11-04).
Daily closed P&L of the 50K combine set (VB 8 MNQ, ONB ADX30 risk $1,100, Bridge 2, EOS $500; MultiCharts trade lists + 1 tick,
2018 -> 2026-10), rolling 12-trading-day sums; the stretch = the Python ports on the extended data (-$3,348 for VB + ONB at plan size;
VB alone -$410 per MNQ gross = live -$401).
  python3 analysis/bad_stretch_freq.py > analysis/outputs/bad_stretch_freq_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import combine_levers_test as CL

g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); tr = g.trading
dts = pd.DatetimeIndex(g.ts[tr]); m = dts >= "2018-01-01"
risk = lambda dollars, mm: np.floor(dollars / (np.nan_to_num(mm * atr[tr], nan=1e12) * 2))
day = {}
for nm, t, q in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0])), 8.0), ("ONB", with_slippage(load_mc(g, CL.ONB30)), risk(1100, 0.25)),
                 ("MON_BR", load_bridge_mc(g), 2.0), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])), risk(500, REPORTS["EOS"][1]))):
    w, r = paths(g, t); day[nm] = pd.Series(r[tr][:, -1] / 10 * q, index=dts)[m]
S = pd.DataFrame(day); tot = S.sum(axis=1); vbmnq = S.VB / 8
print(__doc__.split("\n")[0])
print(f"\nBacktest {S.index[0].date()} -> {S.index[-1].date()}, {len(S)} trading days; 50K set average 12-day P&L ${tot.rolling(12).sum().mean():+,.0f}")
for nm, x, cut in (("50K set (VB 8 + ONB $1,100 + Bridge + EOS)", tot, -3348.0), ("VB per MNQ, gross-ish", vbmnq, -410.0)):
    r12 = x.rolling(12).sum().dropna()
    p = (r12 <= cut).mean()
    # separate episodes: first day of each run of windows at or below the cut
    hit = (r12 <= cut).astype(int); starts = r12.index[(hit.diff() == 1) | ((hit == 1) & (np.arange(len(hit)) == 0))]
    print(f"\n{nm}: this stretch ${cut:+,.0f}")
    print(f"   share of 12-day windows this bad or worse: {p:.1%}  (percentile {p * 100:.1f})")
    print(f"   separate episodes 2018-26: {len(starts)} (~{len(starts) / (len(x) / 252):.1f} a year); by year: "
          f"{pd.Series(1, index=starts).groupby(starts.year).sum().to_dict()}")
    print(f"   worst 12-day window ${r12.min():+,.0f} (ending {r12.idxmin().date()}); 5th pct ${r12.quantile(0.05):+,.0f}, 10th ${r12.quantile(0.10):+,.0f}")
