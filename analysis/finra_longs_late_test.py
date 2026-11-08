"""FINRA short-volume longs entered after 10:30 (user 2026-11-08: 'the edge builds through the day ... trade only after 10:30, when the market
has chosen its direction; maybe remove the stop'). PRE-REGISTERED (header committed before the first run; 3 variants on top of the post hoc
long-only rule; bar ~3.65). Same signal (Nasdaq short-volume ratio Z >= 1 -> long NQ the next trading day); early-close days skipped;
$7.25 + 1 tick per fill. The original has no target, so 'no TP' is already the case.
  C  enter 10:31, stop 0.25 x ATR15, out 14:55
  D  enter 10:31, no stop, out 14:55
  E  enter 10:31 only if NQ's 10:30 close > its 08:30 open ('direction chosen' up), stop 0.25 x ATR15, out 14:55
Checks per version: $ a trade by period / year; random-day longs with the same entry / exit / condition (same count per year, 500 runs);
checker checks/candidates/finra_longs_c, _d, _e (pre_registered false); 150K evaluation (set + Twin 2 MNQ) + 2 / 4 MNQ; funded 150K x 1.5
+ Twin 2 + 2 / 4 MNQ; personal book + 1 MNQ.
  tools/run_stamped.sh analysis/finra_longs_late_test.py > analysis/outputs/finra_longs_late_test_output.txt
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import letf_flow_test as LF
from finra_short_test import SYMS
from new_sources_150k import daypaths
import bench150 as BB

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    F = pd.read_csv("data/finra/short_volume.csv", sep="|", parse_dates=["Date"]); F = F[F.Symbol.isin(SYMS) & (F.TotalVolume > 0)]
    F["r"] = F.ShortVolume / F.TotalVolume; R = F.pivot_table(index="Date", columns="Symbol", values="r").mean(axis=1)
    Z = (R - R.rolling(60).mean().shift(1)) / R.rolling(60).std().shift(1)
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); days = pd.DatetimeIndex(g.ts[g.trading]); sig = {}
    for d, z in Z.dropna().items():
        later = days[days > d]
        if len(later) and z >= 1.0: sig.setdefault(later[0], z)
    sig = pd.Series(sig).sort_index(); allday = pd.Series(1.0, index=days[days >= Z.dropna().index.min()])
    pos = pd.Series(np.arange(len(g.ts)), index=pd.DatetimeIndex(g.ts))
    up = lambda d: 1 if (d in pos.index and g.c[int(pos[d]), jof(1030)] > g.o[int(pos[d]), jof(831)]) else 0
    V = {"finra_longs_c": (dict(t0=1030, t1=1455, stop=0.25), lambda d, z: 1), "finra_longs_d": (dict(t0=1030, t1=1455, stop=100.0), lambda d, z: 1),
         "finra_longs_e": (dict(t0=1030, t1=1455, stop=0.25), lambda d, z: up(d))}
    ctx = BB.setup(); dts, D = ctx["dts"], ctx["D"]; dpos = pd.Series(np.arange(D), index=dts); paths = {}
    for nm, (kw, fn) in V.items():
        T = LF.trades(g, sig, fn, **kw); Ta = LF.trades(g, allday, fn, **kw); an = Ta.set_index("date").net
        print(f"\n{nm[-1].upper()} ({kw}):"); print(LF.line(T.net, T.date, "signal longs")); print(LF.line(Ta.net, Ta.date, "every-day longs, same rule (control)"))
        print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
        cnt = T.groupby(T.date.dt.year).size(); rng = np.random.default_rng(29); pl = []
        for run in range(500):
            for y, n in cnt.items():
                pool_ = an[an.index.year == y]
                if len(pool_) >= n: pl += [(run, x) for x in pool_.loc[rng.choice(pool_.index, n, replace=False)].values]
        pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean()
        print(f"   random-day longs: ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${T.net.mean():.0f}; p {np.mean(pm >= T.net.mean()):.3f}", flush=True)
        cd = f"checks/candidates/{nm}"; os.makedirs(cd, exist_ok=True)
        T.assign(date=T.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net", "risk"]].to_csv(f"{cd}/trades.csv", index=False)
        pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
        json.dump({"kind": "strategy", "pre_registered": False, "variants": 7}, open(f"{cd}/meta.json", "w"))
        open(f"{cd}/spec.md", "w").write(f"# FINRA short-volume longs, version {nm[-1].upper()} (2026-11-08)\nNasdaq short-volume ratio Z >= 1 -> long NQ the next day; " + __doc__.split(f"  {nm[-1].upper()}  ")[1].split("\n")[0] + ". $7.25 + 1 tick per fill. Placebo = random-day longs, same rule.\n")
        paths[nm] = daypaths(D, [(int(dpos[d]) if d in dpos.index else None, a, n) for d, a, n in zip(T.date, T.adv, T.net)]); paths[nm + "_T"] = T
    print()
    BB.eval_bench(ctx, {f"+ {nm[-1].upper()} {n} MNQ": (n * paths[nm][0], n * paths[nm][1]) for nm in V for n in (2, 4)})
    print()
    BB.funded_bench(ctx, {f"+ {nm[-1].upper()} {n} MNQ": {**BB.BASE_FUNDED, nm: n} for nm in V for n in (2, 4)}, extra={nm: (paths[nm][0], paths[nm][1][:, -1]) for nm in V})
    print("\n   Personal book 1-year MC return / DD p95 (+ 1 MNQ):")
    BB.personal({nm[-1].upper(): (paths[nm + "_T"].net / 10 - 0.55).groupby(paths[nm + "_T"].date).sum() for nm in V})
