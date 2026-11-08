"""FINRA short-volume longs, Apex-shaped versions (user 2026-11-08: 'build the apex version'; the original stays on WATCHLIST #32).
PRE-REGISTERED (header committed before the first run; 2 variants, on top of the post hoc long-only rule, so the bar stays ~3.65).
Same signal (Nasdaq short-volume ratio Z >= 1 -> long NQ the next day at 08:31; early-close days skipped; $7.25 + 1 tick per fill):
  A  stop 0.25 x ATR15 (half), out at the 14:55 close        B  stop 0.25 x ATR15, out at the 10:30 close
Why: Apex fails an account on an intraday touch of the trailing floor, so a smaller, bounded loss per trade should fit it better.
Checks per version: $ a trade by period / year; random-day longs with the same exits (same count per year, 500 runs); checker
checks/candidates/finra_longs_a, finra_longs_b/ (pre_registered false); 150K evaluation (set + Twin 2 MNQ) + 2 / 4 MNQ; funded 150K
x 1.5 + Twin 2 + 2 / 4 MNQ; personal book + 1 MNQ (information).
  tools/run_stamped.sh analysis/finra_longs_apex_test.py > analysis/outputs/finra_longs_apex_test_output.txt
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import letf_flow_test as LF
from finra_short_test import SYMS
from new_sources_150k import daypaths
import bench150 as BB

V = {"finra_longs_a": dict(t0=830, t1=1455, stop=0.25), "finra_longs_b": dict(t0=830, t1=1030, stop=0.25)}

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
    ctx = BB.setup(); dts, D = ctx["dts"], ctx["D"]; dpos = pd.Series(np.arange(D), index=dts); paths = {}
    for nm, kw in V.items():
        T = LF.trades(g, sig, lambda d, z: 1, **kw); Ta = LF.trades(g, allday, lambda d, z: 1, **kw); an = Ta.set_index("date").net
        print(f"\n{nm} (stop {kw['stop']} ATR, out {kw['t1']}):"); print(LF.line(T.net, T.date, "signal longs")); print(LF.line(Ta.net, Ta.date, "every-day longs (control)"))
        print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()} | stops {int((T.net < -(kw['stop'] * 0)).sum())} of {len(T)} lost")
        cnt = T.groupby(T.date.dt.year).size(); rng = np.random.default_rng(23); pl = []
        for run in range(500):
            for y, n in cnt.items(): pl += [(run, x) for x in an.loc[rng.choice(an[an.index.year == y].index, n, replace=False)].values]
        pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean()
        print(f"   random-day longs: ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${T.net.mean():.0f}; p {np.mean(pm >= T.net.mean()):.3f}", flush=True)
        cd = f"checks/candidates/{nm}"; os.makedirs(cd, exist_ok=True)
        T.assign(date=T.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net", "risk"]].to_csv(f"{cd}/trades.csv", index=False)
        pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
        json.dump({"kind": "strategy", "pre_registered": False, "variants": 4}, open(f"{cd}/meta.json", "w"))
        open(f"{cd}/spec.md", "w").write(f"# FINRA short-volume longs, Apex version {nm[-1].upper()} (2026-11-08)\nNasdaq short-volume ratio Z >= 1 (QQQ + 10 mega-caps, vs past 60 days) -> long NQ next day 08:31, stop {kw['stop']} x ATR15, out {kw['t1']} CT. $7.25 + 1 tick per fill. Placebo = random-day longs.\n")
        paths[nm] = daypaths(D, [(int(dpos[d]) if d in dpos.index else None, a, n) for d, a, n in zip(T.date, T.adv, T.net)]); paths[nm + "_T"] = T
    print()
    BB.eval_bench(ctx, {f"+ {nm[-1].upper()} {n} MNQ": (n * paths[nm][0], n * paths[nm][1]) for nm in V for n in (2, 4)})
    print()
    BB.funded_bench(ctx, {f"+ {nm[-1].upper()} {n} MNQ": {**BB.BASE_FUNDED, nm: n} for nm in V for n in (2, 4)}, extra={nm: (paths[nm][0], paths[nm][1][:, -1]) for nm in V})
    print("\n   Personal book 1-year MC return / DD p95 (+ 1 MNQ, information):")
    BB.personal({nm[-1].upper(): (paths[nm + "_T"].net / 10 - 0.55).groupby(paths[nm + "_T"].date).sum() for nm in V})
