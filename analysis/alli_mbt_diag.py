"""Why does the AlligatorV2 rebuild lose on MBT when it wins on spot? (user 2026-11-13: 'use spot data but execute on futures').
It already IS spot signals -> MBT fills (analysis/jesse_rebuilds_personal_bench.py). Variants of the execution only, per MBT a year:
 A as benched (resting MBT stop, every spot trade) | B no resting MBT stop (all exits copied at the spot exit time)
 C only entries while CME is open (skip signals during the daily break / weekend) | D = B + C | spot itself in $ per 0.1 BTC for reference
  tools/run_stamped.sh analysis/alli_mbt_diag.py > analysis/outputs/alli_mbt_diag_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
src = open("analysis/jesse_rebuilds_personal_bench.py", encoding="utf-8").read().split("S0 = PB.run(PB.setup())")[0]
g = {"__name__": "diag", "__doc__": __doc__}; exec(compile(src, "bench", "exec"), g)
np, pd, FT, AL, mark, days = (g[k] for k in ("np", "pd", "FT", "AL", "mark", "days"))
t = AL[(AL.t >= FT[0]) & (AL.tx <= FT[-1])].reset_index(drop=True)
ie = np.searchsorted(FT, t.t.values + np.timedelta64(30, "m"))
gap = (FT[np.minimum(ie, len(FT) - 1)] - (t.t.values + np.timedelta64(30, "m"))) / np.timedelta64(1, "m")
open_ = gap <= 15
yrs = (days[-1] - pd.Timestamp("2018-12-17")).days / 365.25
spot = (t.ret * t.e * 0.1)
print(f"spot trades in the MBT window: {len(t)}, spot $ per 0.1 BTC a year {spot.sum() / yrs:,.0f} (costs 0.07% a side already in); CME open at the signal: {open_.mean():.0%}")
print(f"   spot $ a year: entries while CME open {spot[open_].sum() / yrs:,.0f} | while shut {spot[~open_].sum() / yrs:,.0f}")
for nm, tt, big in (("A as benched", t, False), ("B no resting MBT stop", t, True), ("C CME-open entries only", t[open_], False), ("D B + C", t[open_], True)):
    x = tt.assign(R=10.0) if big else tt
    s, n = mark(x); e = s.cumsum()
    print(f"{nm:<26} {n} trades, ${s.sum() / yrs:,.0f} a year per MBT, max DD ${(e - e.cummax()).min():,.0f}, by year " + " ".join(f"{y} {v:+,.0f}" for y, v in s.groupby(s.index.year).sum().items() if y >= 2019))
