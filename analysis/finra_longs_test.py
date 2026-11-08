"""FINRA short volume, LONGS ONLY (user 2026-11-08). POST HOC (the long / short split was seen in finra_short_test.py: longs $661 t 3.5);
header committed before this run; 2nd variant, so the bar is t >= the multiple-testing threshold (~3.65) or DSR >= 0.95.
Rule: as finra_short_test with only the long side: Nasdaq short-volume ratio Z (QQQ + 10 mega-caps, vs past 60 days) >= 1 -> long NQ the
next trading day at 08:31, stop 0.5 x ATR15, out 14:55; early-close days skipped; $7.25 + 1 tick per fill.
Key control (a long-only rule in a rising market earns the drift): random-day longs, the same number per year, same exits (500 runs);
also long every day. Plus: by period / year, Z >= 2 subset (information), checker checks/candidates/finra_longs/ (pre_registered false),
150K evaluation + 2 MNQ, funded 150K x 1.5 + Twin 2 + 2 MNQ, personal + 1 MNQ.
  tools/run_stamped.sh analysis/finra_longs_test.py > analysis/outputs/finra_longs_test_output.txt
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import letf_flow_test as LF
from finra_short_test import SYMS
from new_sources_150k import daypaths
import bench150 as BB

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    F = pd.read_csv("data/finra/short_volume.csv", sep="|", parse_dates=["Date"]); F = F[F.Symbol.isin(SYMS) & (F.TotalVolume > 0)]
    F["r"] = F.ShortVolume / F.TotalVolume; R = F.pivot_table(index="Date", columns="Symbol", values="r").mean(axis=1)
    Z = (R - R.rolling(60).mean().shift(1)) / R.rolling(60).std().shift(1)
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); days = pd.DatetimeIndex(g.ts[g.trading]); kw = dict(t0=830, t1=1455, stop=0.5)
    sig = {}
    for d, z in Z.dropna().items():
        later = days[days > d]
        if len(later) and z >= 1.0: sig.setdefault(later[0], z)
    sig = pd.Series(sig).sort_index()
    T = LF.trades(g, sig, lambda d, z: 1, **kw)
    print(LF.line(T.net, T.date, "longs after a high short ratio")); print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
    big = T[T.z >= 2]; print(LF.line(big.net, big.date, "   Z >= 2 only (info)"))
    allday = pd.Series(1.0, index=days[(days >= Z.dropna().index.min())]); Ta = LF.trades(g, allday, lambda d, z: 1, **kw)
    print(LF.line(Ta.net, Ta.date, "control: long every day (same exits)"))
    pool = {y: [d for d in allday.index if d.year == y] for y in sorted(set(allday.index.year))}; cnt = T.groupby(T.date.dt.year).size()
    an = Ta.set_index("date").net; rng = np.random.default_rng(19); pl = []
    for run in range(500):
        for y, n in cnt.items():
            pk = rng.choice(an[an.index.year == y].index, n, replace=False); pl += [(run, x) for x in an.loc[pk].values]
    pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean()
    print(f"   random-day longs (same count per year, 500 runs): ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${T.net.mean():.0f}; p {np.mean(pm >= T.net.mean()):.3f}", flush=True)
    for per, lo, hi in (("2018-22", "2018", "2023"), ("2023+", "2023", "2100")):
        a_ = T[(T.date >= lo) & (T.date < hi)].net.mean(); b_ = an[(an.index >= lo) & (an.index < hi)].mean(); print(f"   {per}: signal longs ${a_:.0f} vs every-day longs ${b_:.0f} (edge ${a_ - b_:+.0f})")
    cd = "checks/candidates/finra_longs"; os.makedirs(cd, exist_ok=True)
    T.assign(date=T.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net", "risk"]].to_csv(f"{cd}/trades.csv", index=False)
    pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": False, "variants": 2}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write("# FINRA short volume, longs only (2026-11-08, post hoc)\n" + __doc__.split("Rule:")[1].split("Key control")[0] + "\nPlacebo = random-day longs, same count per year.\n")
    ctx = BB.setup(); dts, D = ctx["dts"], ctx["D"]; dpos = pd.Series(np.arange(D), index=dts)
    W1, R1 = daypaths(D, [(int(dpos[d]) if d in dpos.index else None, a, n) for d, a, n in zip(T.date, T.adv, T.net)])
    lab = ctx["lab"]; dd = pd.Series(R1[:, -1], index=dts); span = dts >= "2018-08-01"
    C = pd.DataFrame({k: lab.C[k] for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "TWIN")}, index=dts)
    print("   daily corr:", C[span].corrwith(dd[span]).round(2).to_dict(), "\n")
    BB.eval_bench(ctx, {"+ FINRA longs 2 MNQ": (2 * W1, 2 * R1)})
    print()
    BB.funded_bench(ctx, {"+ FINRA longs 2 MNQ": {**BB.BASE_FUNDED, "FSL": 2}}, extra={"FSL": (W1, R1[:, -1])})
    print("\n   Personal book 1-year MC return / DD p95 (+ 1 MNQ):")
    BB.personal({"+ FINRA longs 1 MNQ": (T.net / 10 - 0.55).groupby(T.date).sum()})
