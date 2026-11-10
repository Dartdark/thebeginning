"""Macro follow-ups (user 2026-11-10: 'do both'). PRE-REGISTERED (header committed before the first run).
1 Robust-surprise rerun of analysis/macro_tests.py part B: z = (actual - consensus) / (1.4826 x median absolute deviation of that series'
  surprises, 2018-26), so the 2020 outliers no longer shrink every other surprise; BIG = |z| >= 1; same 10 items (5 groups x follow /
  fade the 07:30 -> 07:45 reaction, 07:46 -> 09:00, stop 0.5 ATR), bar t_threshold(10).
2 Inflation-day fade (post hoc in origin: following lost on inflation days in macro_tests.py): on every CPI / PPI / PCE release day
  (07:30 CT), fade the 07:29 -> 07:45 NQ reaction at the 07:46 open, stop 0.5 x daily ATR15, out at the 09:00 close; per NQ after $7.25
  + 1 tick per fill. Random-side placebo (500 runs); overlap with NFP Fade (jobs days) reported; benches: personal book + 1 MNQ,
  150K evaluation + 2 MNQ, funded 150K + 2 MNQ (intraday worst = the trade's worst excursion).
  tools/run_stamped.sh analysis/macro_followups.py > analysis/outputs/macro_followups_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from metrics import t_threshold, perf
from ingredient_ablation3 import line
from new_sources_150k import daypaths
from macro_tests import GROUPS
import bench150 as BB

PV, TICK, COMM = 20.0, 0.25, 7.25


def events(robust=True):
    M = pd.read_csv("data/codex_20261109/macro_events_2018plus.csv", parse_dates=["time"]).dropna(subset=["actual"])
    M["ct"] = M.time.dt.tz_convert("America/Chicago"); M["day"] = pd.DatetimeIndex(M.ct.dt.date); M["hm"] = M.ct.dt.hour * 100 + M.ct.dt.minute
    M["s"] = M.actual - M.forecast
    sc = (lambda x: 1.4826 * (x - x.median()).abs().median()) if robust else (lambda x: x.std())
    M["z"] = M.groupby("series").s.transform(lambda x: x / sc(x.dropna()) if sc(x.dropna()) > 0 else np.nan)
    gm = {s: k for k, v in GROUPS.items() for s in v}; M["group"] = M.series.map(gm); rows = []
    for (grp, day), x in M.dropna(subset=["group"]).groupby(["group", "day"]):
        zz = x.z.dropna(); rows.append(dict(group=grp, day=day, hm=int(x.hm.min()), z=zz.loc[zz.abs().idxmax()] if len(zz) else np.nan))
    return pd.DataFrame(rows)


def trade(g, cf, atr, r, side):
    """07:46 open -> 09:00 close, stop 0.5 ATR; returns (net, worst $) per NQ."""
    j0, j1 = jof(746), jof(900); e = g.o[r, j0]
    if not np.isfinite(e): return None
    e += side * TICK; sp = e - side * 0.5 * atr[r]; worst = 0.0
    for j in range(j0, j1 + 1):
        if not np.isfinite(g.c[r, j]): continue
        lo = g.l[r, j] if side > 0 else g.h[r, j]; worst = min(worst, (lo - e) * side)
        if (side > 0 and g.l[r, j] <= sp) or (side < 0 and g.h[r, j] >= sp):
            px = (min(g.o[r, j], sp) if side > 0 else max(g.o[r, j], sp)) - side * TICK; return (px - e) * side * PV - COMM, worst * PV - COMM
    cc = g.c[r, j0:j1 + 1]; px = cc[np.isfinite(cc)][-1] - side * TICK
    return (px - e) * side * PV - COMM, min(worst * PV, (px - e) * side * PV) - COMM


def run(g, cf, atr, pos, days, fade, rng=None):
    rows = []
    for d in days:
        if d not in pos.index: continue
        r = int(pos[d]); c0, c1 = cf[r * 1440 + jof(729)], cf[r * 1440 + jof(745)]
        if not (np.isfinite(c0) and np.isfinite(c1)) or c1 == c0 or np.isnan(atr[r]): continue
        s = int(np.sign(c1 - c0)) * (-1 if fade else 1)
        if rng is not None: s = int(rng.choice([-1, 1]))
        x = trade(g, cf, atr, r, s)
        if x is not None: rows.append((d, s, x[0], x[1]))
    return pd.DataFrame(rows, columns=["date", "side", "net", "adv"])


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); pos = pd.Series(np.arange(len(g.ts)), index=pd.DatetimeIndex(g.ts))
    cf = pd.Series(g.c.ravel()).ffill().to_numpy(); E = events(True)
    print(f"\n1. Robust-surprise rerun (items 10, bar t >= {t_threshold(10):.2f}):")
    for grp in ("INFLATION", "JOBS", "CLAIMS", "RETAIL", "GDP"):
        x = E[(E.group == grp) & (E.hm == 730)]; big = x[x.z.abs() >= 1]; print(f"   {grp}: release days {len(x)}, big surprises (robust) {len(big)}")
        for fade, nm in ((False, "ITEM follow, big surprise"), (True, "ITEM fade, big surprise")):
            T = run(g, cf, atr, pos, list(big.day), fade); print(line(T.net, T.date, "   " + nm))
    print("\n2. Inflation-day fade (every CPI / PPI / PCE day, 07:46 -> 09:00):")
    infl = sorted(set(E[(E.group == "INFLATION") & (E.hm == 730)].day)); T = run(g, cf, atr, pos, infl, True)
    print(line(T.net, T.date, "inflation-day fade")); print(line(T[T.side > 0].net, T[T.side > 0].date, "   longs")); print(line(T[T.side < 0].net, T[T.side < 0].date, "   shorts"))
    print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
    rng = np.random.default_rng(29); pm = np.array([run(g, cf, atr, pos, infl, True, rng).net.mean() for _ in range(500)])
    print(f"   random side (500 runs): mean ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${T.net.mean():.0f}; p {np.mean(pm >= T.net.mean()):.3f}")
    jobs = set(E[E.group == "JOBS"].day); print(f"   overlap with jobs-report days (NFP Fade's days): {T.date.isin(jobs).sum()} of {len(T)}")
    d = T.set_index("date").net.groupby(level=0).sum(); P = perf(d.reindex(pd.bdate_range("2018-01-01", "2026-10-31"), fill_value=0))
    print(f"   daily: Sharpe {P['sharpe']:.2f} Sortino {P['sortino']:.2f} PF {P['profit_factor']:.2f} Calmar {P['calmar']:.2f} max DD ${P['max_dd']:,.0f} per NQ")
    ctx = BB.setup(); D, dts = ctx["D"], ctx["dts"]; dp = pd.Series(np.arange(D), index=dts)
    W1, R1 = daypaths(D, [(int(dp[x]) if x in dp.index else None, a, n) for x, a, n in zip(T.date, T.adv, T.net)])
    print(); BB.eval_bench(ctx, {"+ inflation-day fade 2 MNQ": (2 * W1, 2 * R1)})
    print(); BB.funded_bench(ctx, {"+ inflation-day fade 2 MNQ": {**BB.BASE_FUNDED, "IDF": 2}}, extra={"IDF": (W1, R1[:, -1])})
    print("\n   Personal book 1-year MC return / DD (+ 1 MNQ):"); BB.personal({"+ inflation-day fade 1 MNQ": (T.net / 10 - 0.55).groupby(T.date).sum()})
