"""Ingredient ablation, round 2 (user 2026-11-08: 'another set of strats to get ingredients from'): Vault Break v1, Dual Thrust v4 and
PAPERTREND v2. Information only (historical component evidence, no promotion): each strategy as is, then ONE part removed or isolated at a
time, per NQ after repo costs ($7.25 + 1 tick per market / stop fill), 2018-26 and both periods, with total $ and max drawdown (removing a
part can change later trades, so totals and risk are shown, not only $ a trade). Coupled changes are labelled as such (Codex 2026-11-08).
  Vault Break v1 (longs; 30-min close > session open + 0.30 x ATR15 and > VWAP, entries 10:00-14:30, target 40 / stop 75, max 3, out 14:30;
    engine vault_break_v8_test.run('v1'), matched to the MultiCharts list at corr 0.993): no noise level (mult 0) / no VWAP condition /
    neither (coupled) / no target / no stop (target kept) / 1 trade a day / entries from 08:30
  Dual Thrust v4 (open +- 0.5 x prior-day range RR, skip if RR > 1.2 x ADR20, stop 50 / target 100, entry-bar stop, flat 14:55;
    dual_thrust_test): no range threshold (k 0 = break of the open) / no band filter / no target / no stop (both stops off, target kept;
    coupled) / no entry-bar stop / no holiday list / longs only / shorts only
  PAPERTREND v2 (open +- 0.5 x ATR14 at 15-min marks, gap side only, skip after the widest of 7 ranges, 2 x ATR disaster stop, flat
    14:55; papertrend_test): no band (k 0) / no gap filter / no skip filter / no stop (as the report) / longs only / shorts only /
    random side (direction placebo, same days and times)
  tools/run_stamped.sh analysis/ingredient_ablation2.py > analysis/outputs/ingredient_ablation2_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd


def line(x, d, nm):
    x = pd.Series(np.asarray(x, float)); d = pd.DatetimeIndex(d); tt = lambda v: v.mean() / v.std(ddof=1) * np.sqrt(len(v)) if len(v) > 2 else np.nan
    a, b = x[(d < "2023").tolist()], x[(d >= "2023").tolist()]; pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    cum = pd.Series(x.values, index=d).groupby(level=0).sum().cumsum(); mdd = (cum.cummax() - cum).max()
    return (f"   {nm:<44} n {len(x):5d} ${x.mean():5.0f} t {tt(x):5.2f} PF {pf:4.2f} total ${x.sum() / 1000:5.0f}k maxDD ${mdd / 1000:4.1f}k | 2018-22 ${a.mean():4.0f} (t {tt(a):4.1f})"
            f" 2023+ ${b.mean():4.0f} (t {tt(b):4.1f}) | worst ${x.min():,.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    import vault_break_v8_test as VB
    g = pickle.load(open("scratch_data/g24.pkl", "rb"))
    print("\n1. Vault Break v1 (longs):")
    for nm, kw in (("as is", {}), ("no noise level (break of the open)", dict(mult=0.0)), ("no VWAP condition", dict(use_vwap=False)),
                   ("neither (close > open only; coupled)", dict(mult=0.0, use_vwap=False)), ("no target", dict(tp=1e6)),
                   ("no stop (target 40 kept)", dict(sl=1e6)), ("1 trade a day", dict(max_tr=1)), ("entries from 08:30", dict(first=830))):
        T = VB.run(g, "v1", **kw); T = T[T.date >= "2018-01-01"]; print(line(T.net, T.date, nm), flush=True)
    import dual_thrust_test as DT
    days = DT.load()
    print("\n2. Dual Thrust v4:")
    for nm, sk, kw in (("as is", {}, {}), ("no range threshold (k 0, break of the open)", dict(k=0.0), {}), ("no band filter", dict(band=0), {}),
                       ("no target", {}, dict(tp=0)), ("no stop (both stops off, target kept; coupled)", {}, dict(sl=0)),
                       ("no entry-bar stop", {}, dict(entry_bar_stop=False)), ("no holiday list", dict(hol=False), {}),
                       ("longs only", {}, dict(side_only=1)), ("shorts only", {}, dict(side_only=-1))):
        T = DT.run(days, DT.setups(days, **sk), **kw); print(line(T.net, T.date, nm), flush=True)
    import papertrend_test as PT
    NQ = PT.Days("NQ")
    print("\n3. PAPERTREND v2 (2 x ATR disaster stop as planned):")
    for nm, kw in (("as is", dict(stop_atr=2.0)), ("no band (k 0, break of the open)", dict(k=0.0, stop_atr=2.0)), ("no gap filter", dict(gap=False, stop_atr=2.0)),
                   ("no skip filter", dict(skip=False, stop_atr=2.0)), ("no stop (as the report)", dict(stop_atr=None))):
        T = PT.run(NQ, **kw); T = T[T.index >= "2018-01-01"]; print(line(T.net, T.index, nm), flush=True)
    T = PT.run(NQ, stop_atr=2.0); T = T[T.index >= "2018-01-01"]
    print(line(T[T.side > 0].net, T[T.side > 0].index, "longs only")); print(line(T[T.side < 0].net, T[T.side < 0].index, "shorts only"))
    R = [PT.run(NQ, stop_atr=2.0, side_mode="random", seed=s, count=False) for s in range(50)]
    rm = [r[r.index >= "2018-01-01"].net.mean() for r in R]
    print(f"   random side (50 runs, same days / times): ${np.mean(rm):.0f} a trade, 95th ${np.percentile(rm, 95):.0f}; real ${T.net.mean():.0f}")
