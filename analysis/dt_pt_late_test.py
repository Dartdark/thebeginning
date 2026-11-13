"""Dual Thrust without its target / Dual Thrust and PAPERTREND from 10:00 (user 2026-11-08, leads from ingredient_ablation2.py).
PRE-REGISTERED (header committed before the first run; 3 variants; post hoc in origin: the ablation already showed DT 'no target'
and VB's late start, so promotion needs t >= the multiple-testing bar or a clean placebo). Rules otherwise unchanged:
  A  Dual Thrust v4, no target (stop 50 + entry-bar stop kept, flat 14:55)            (dual_thrust_test.run, tp=0)
  B  Dual Thrust v4, signal bars from 10:00 CT (triggers unchanged: open +- 0.5 x prior-day range; last signal 14:30)   (t_start=1000)
  C  PAPERTREND v2 (2 x ATR disaster stop), 15-min marks from 10:00 CT instead of 08:45 (last 14:00)   (papertrend_test.run, first=jof(1000))
Costs $7.25 + 1 tick per NQ market / stop fill (target = limit, 1 tick through). Per variant: $ a trade, t, total, max DD, by period and
year, longs / shorts; random side at the same signal bars (100 runs DT, 100 PT); checker checks/candidates/dt_notarget, dt_late, pt_late.
Books, each as a REPLACEMENT of the piece it changes: personal book (the MultiCharts DualThrust / PaperTrend column replaced by the
Python rebuild as is vs the variant, 1 MNQ each, + $0.55 a trade); funded 150K x 1.5 + Twin 2 + Dual Thrust 2 MNQ (the plan's DT
input) with DT 2 -> A 2 / B 2 (the bench has no Relative Strength or Overnight Tick: their trade files are not in this session).
  tools/run_stamped.sh analysis/dt_pt_late_test.py > analysis/outputs/dt_pt_late_test_output.txt
"""
import sys, os, json, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from funded_lab import with_slippage
import dual_thrust_test as DT
import papertrend_test as PT
import bench150 as BB


def line(x, d, nm):
    x = pd.Series(np.asarray(x, float)); d = pd.DatetimeIndex(d); tt = lambda v: v.mean() / v.std(ddof=1) * np.sqrt(len(v)) if len(v) > 2 else np.nan
    a, b = x[(d < "2023").tolist()], x[(d >= "2023").tolist()]; pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    cum = pd.Series(x.values, index=d).groupby(level=0).sum().cumsum(); mdd = (cum.cummax() - cum).max()
    return (f"   {nm:<34} n {len(x):5d} ${x.mean():5.0f} t {tt(x):5.2f} PF {pf:4.2f} total ${x.sum() / 1000:5.0f}k maxDD ${mdd / 1000:4.1f}k | 2018-22 ${a.mean():4.0f} (t {tt(a):4.1f})"
            f" 2023+ ${b.mean():4.0f} (t {tt(b):4.1f}) | worst ${x.min():,.0f}")


def save(name, T, dates, pl, variants=3):
    cd = f"checks/candidates/{name}"; os.makedirs(cd, exist_ok=True)
    pd.DataFrame(dict(date=pd.DatetimeIndex(dates).strftime("%Y-%m-%d"), side=T.side.values, net=T.net.values)).to_csv(f"{cd}/trades.csv", index=False)
    pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": True, "variants": variants}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write(f"# {name} (2026-11-08)\n" + __doc__.split("Rules otherwise unchanged:")[1].split("Costs")[0] + "\n$7.25 + 1 tick per fill per NQ.\n")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    days = DT.load(); S = DT.setups(days)
    D0 = DT.run(days, S); DA = DT.run(days, S, tp=0); DB_ = DT.run(days, S, t_start=1000)
    print("\n1. Dual Thrust v4 (per NQ):")
    for nm, T in (("as is", D0), ("A no target", DA), ("B signals from 10:00", DB_)):
        print(line(T.net, T.date, nm)); print(line(T[T.side > 0].net, T[T.side > 0].date, "   longs")); print(line(T[T.side < 0].net, T[T.side < 0].date, "   shorts"))
        print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
    for nm, kw, T in (("dt_notarget", dict(tp=0), DA), ("dt_late", dict(t_start=1000), DB_)):
        rng = np.random.default_rng(3); pl = []
        for run in range(100):
            Tp = DT.run(days, S, flip_rng=rng, **kw); pl += [(run, x) for x in Tp.net]
        pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean()
        print(f"   {nm}: random side at the same signal bars ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${T.net.mean():.0f}; p {np.mean(pm >= T.net.mean()):.2f}", flush=True)
        save(nm, T, T.date, pl)
    NQ = PT.Days("NQ")
    P0 = PT.run(NQ, stop_atr=2.0); PC = PT.run(NQ, stop_atr=2.0, first=jof(1000))
    P0, PC = P0[P0.index >= "2018-01-01"], PC[PC.index >= "2018-01-01"]
    print("\n2. PAPERTREND v2 (per NQ):")
    for nm, T in (("as is (marks from 08:45)", P0), ("C marks from 10:00", PC)):
        print(line(T.net, T.index, nm)); print(line(T[T.side > 0].net, T[T.side > 0].index, "   longs")); print(line(T[T.side < 0].net, T[T.side < 0].index, "   shorts"))
        print(f"      by year $: {T.groupby(T.index.year).net.sum().round(0).astype(int).to_dict()}")
    pl = []
    for s in range(100):
        Tp = PT.run(NQ, stop_atr=2.0, first=jof(1000), side_mode="random", seed=100 + s, count=False); Tp = Tp[Tp.index >= "2018-01-01"]; pl += [(s, x) for x in Tp.net]
    pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean()
    print(f"   pt_late: random side ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${PC.net.mean():.0f}; p {np.mean(pm >= PC.net.mean()):.2f}", flush=True)
    save("pt_late", PC, PC.index, pl)
    # personal book
    dmn = lambda x, d: (pd.Series(np.asarray(x, float) / 10 - 0.55, index=pd.DatetimeIndex(d))).groupby(level=0).sum()
    print("\n3. Personal book 1-year MC return / DD p95 (piece replaced by the Python rebuild as is vs the variant, 1 MNQ):")
    print("   Dual Thrust:"); BB.personal({"DT rebuild as is": dmn(D0.net, D0.date), "A no target": dmn(DA.net, DA.date), "B from 10:00": dmn(DB_.net, DB_.date)}, drop=("DualThrust",))
    print("   PAPERTREND:"); BB.personal({"PT rebuild as is": dmn(P0.net, P0.index), "C from 10:00": dmn(PC.net, PC.index)}, drop=("PaperTrend",))
    # funded 150K
    ctx = BB.setup(); g, lab = ctx["g"], ctx["lab"]
    for k, T in (("DT0", D0), ("DTA", DA), ("DTB", DB_)):
        x = DT.lab_trades(g, T); x = x[x.day.notna()].reset_index(drop=True); x["day"] = x.day.astype(int); lab.add(k, with_slippage(x), slippage=False)
    print()
    base = {**BB.BASE_FUNDED, "DT0": 2}
    import bench150 as _b; _b.BASE_FUNDED = base
    BB.funded_bench(ctx, {"DT 2 -> A no target 2": {**{k: v for k, v in base.items() if k != "DT0"}, "DTA": 2},
                          "DT 2 -> B from 10:00 2": {**{k: v for k, v in base.items() if k != "DT0"}, "DTB": 2}},
                    label="Funded 150K x 1.5 + Twin 2 + Dual Thrust 2 MNQ")
