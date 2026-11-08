"""Checker folders for turn of the month and Vol-Control Sell (user 2026-11-08). Per NQ, repo costs, 2018+.
  tom: long NQ 08:30 open -> 15:00 close on the last trading day of each month and the first 3 of the next; stop 0.5 x daily ATR15
       (prior day); placebo = the same trade on random trading days, same count per year (200 runs)
  vcs: Vol-Control Sell Flow MC trades (REPORTS VCS_MC, with_slippage); placebo = short 14:00 -> 15:00 (same window, 0.25 x ATR
       stop as in the code) on random trading days, same count per year (200 runs)
  python3 analysis/checker_candidates_1108.py   (then: python3 analysis/checker.py checks/candidates/<name>)
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc
from funded_lab import with_slippage
from build_lab import REPORTS
from new_sources_150k import path_exit

TICK, COMM, PV = 0.25, 7.25, 20.0


def day_trade(g, r, atr, side, ja, jb, stopm):
    a = atr[r - 1] if r > 0 else np.nan
    oo = g.o[r, ja:jb + 1]; ok = ~np.isnan(oo)
    if not ok.any() or not np.isfinite(a): return None
    e = oo[ok][0] + side * TICK; x, _ = path_exit(g, [(r, ja, jb)], side, e, stopm * a)
    return ((x - side * TICK) - e) * side * PV - COMM


def write(name, T, pl, spec):
    cd = f"checks/candidates/{name}"; os.makedirs(cd, exist_ok=True)
    T.assign(date=pd.DatetimeIndex(T.date).strftime("%Y-%m-%d"))[["date", "side", "net"]].to_csv(f"{cd}/trades.csv", index=False)
    pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": False, "variants": 3}, open(f"{cd}/meta.json", "w")); open(f"{cd}/spec.md", "w").write(spec)
    print(f"   {name}: {len(T)} trades ${T.net.mean():.0f}, placebo mean ${np.mean([n for _, n in pl]):.0f}")


if __name__ == "__main__":
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); trr = list(g.trading); dts = pd.DatetimeIndex(g.ts[trr])
    J0, J1 = jof(831), jof(1500); ok18 = dts >= "2018-01-01"; rng = np.random.default_rng(5)
    mon = dts.month.to_numpy(); last = np.r_[mon[1:] != mon[:-1], False]; first = np.r_[False, mon[1:] != mon[:-1]]; tom = np.zeros(len(trr), bool)
    for k in range(len(trr)):
        if last[k]: tom[k] = True
        if first[k]: tom[k:k + 3] = True
    rows = [(dts[k], 1, day_trade(g, trr[k], atr, 1, J0, J1, 0.5)) for k in np.nonzero(tom & ok18)[0]]
    T = pd.DataFrame([r for r in rows if r[2] is not None], columns=["date", "side", "net"])
    allv = {k: day_trade(g, trr[k], atr, 1, J0, J1, 0.5) for k in np.nonzero(ok18)[0]}
    byy = {}
    for k, v in allv.items():
        if v is not None: byy.setdefault(dts[k].year, []).append(v)
    cnt = T.groupby(T.date.dt.year).size(); pl = []
    for run in range(200):
        for y, n in cnt.items(): pl += [(run, x) for x in rng.choice(byy[y], n, replace=False)]
    write("turn_of_month", T, pl, """# Turn of the month, NQ intraday (personal-book candidate 2026-11-08)
Long NQ at the 08:30 CT open (first 1-minute bar's open) and out at the 15:00 CT close, on the last trading day of each month and the
first 3 trading days of the next month (RTH trading days). Stop 0.5 x the 15-day daily ATR (prior day's value) below entry, checked on
1-minute bars. Costs $7.25 per round trip + 1 tick per market / stop fill per NQ. 2018-2026. Looked at before (TIER_LIST 'Turn of the
month', overnight_round.py); this intraday version picked 2026-11-08 for Apex legality; not pre-registered.
""")
    vcs = with_slippage(load_mc(g, REPORTS["VCS_MC"][0])); vcs = vcs[pd.DatetimeIndex(g.ts[vcs.day.to_numpy()]) >= "2018-01-01"]
    T2 = pd.DataFrame(dict(date=pd.DatetimeIndex(g.ts[vcs.day.to_numpy()]), side=vcs.side.to_numpy(), net=((vcs.exit - vcs.entry) * vcs.side * PV - COMM).to_numpy()))
    allv = {k: day_trade(g, trr[k], atr, -1, jof(1401), J1, 0.25) for k in np.nonzero(ok18)[0]}
    byy = {}
    for k, v in allv.items():
        if v is not None: byy.setdefault(dts[k].year, []).append(v)
    cnt = T2.groupby(T2.date.dt.year).size(); pl = []
    for run in range(200):
        for y, n in cnt.items(): pl += [(run, x) for x in rng.choice(byy[y], n, replace=False)]
    write("vol_control_sell", T2, pl, """# Vol-Control Sell Flow (personal-book candidate 2026-11-08; funded plan until October 2026)
`funded_strategies/NQ_Vol_Control_Sell.txt` as run in MultiCharts (REPORTS VCS_MC): short NQ 14:00 -> 15:00 CT when a lagged S&P
volatility-control model must sell more than 6% of fund size; stop 0.25 x ATR. Trades = the MultiCharts list, repo costs.
""")
