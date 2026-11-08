"""NY Fed reverse repo (RRP) liquidity -> NQ next day (user 2026-11-08: 'grab it and test'). PRE-REGISTERED (header committed before the
first run; 1 variant). Data: NY Fed markets API reverse repo results (data/nyfed/rrp_daily.csv, total accepted $bn per day, 2017-01 ->
2026-11-06; published the same afternoon).
Mechanism (popular macro claim, tested, not assumed): cash leaving the RRP facility moves into bills / markets (more liquidity -> risk
assets up); cash piling into RRP drains liquidity.
Rule: d5 = RRP today - RRP 5 operation days earlier ($bn); Z = d5 / sd of d5 over the previous 60 days; only days with RRP > $50bn
(otherwise there is no facility to drain); month-end windows excluded (last 2 and first 2 business days of each month: bank window
dressing, mechanical); Z <= -1 (cash leaving) -> long NQ the next trading day 08:31 -> 14:55, Z >= 1 -> short; stop 0.5 x ATR15;
early-close days skipped; $7.25 + 1 tick per fill.
POWER WARNING: RRP was near zero in 2018-20 and 2025-26, so signals exist almost only in 2021-24 (a period whose 'RRP drain = rally'
story is known); a pass here could not be split into design / holdout cleanly.
Checks: signal count by year; $ a trade, longs / shorts, by year; random side on the same days (200 runs); random-day longs (same count
per year) for the long side; checker checks/candidates/rrp_liquidity/; books (150K evaluation + 2 MNQ, funded 150K + 2 MNQ, personal + 1).
  tools/run_stamped.sh analysis/rrp_liquidity_test.py > analysis/outputs/rrp_liquidity_test_output.txt
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import letf_flow_test as LF
from new_sources_150k import daypaths
import bench150 as BB

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    r = pd.read_csv("data/nyfed/rrp_daily.csv", parse_dates=["operationDate"]).set_index("operationDate").rrp_bn.sort_index()
    d5 = r - r.shift(5); Z = d5 / d5.rolling(60).std().shift(1)
    bd = pd.Series(r.index, index=r.index); ym = r.index.to_period("M")
    rank_f = bd.groupby(ym).rank(); rank_b = bd.groupby(ym).rank(ascending=False)
    ok = (r > 50) & (rank_f > 2) & (rank_b > 2) & Z.notna()
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); days = pd.DatetimeIndex(g.ts[g.trading]); sig = {}
    for d, z in Z[ok].items():
        later = days[days > d]
        if len(later) and abs(z) >= 1.0: sig.setdefault(later[0], z)
    sig = pd.Series(sig).sort_index(); print("   signal days by year:", sig.groupby(sig.index.year).size().to_dict())
    kw = dict(t0=830, t1=1455, stop=0.5)
    T = LF.trades(g, sig, lambda d, z: -int(np.sign(z)), **kw)
    print(LF.line(T.net, T.date, "rule: RRP draining -> long, filling -> short")); print(LF.line(T[T.side > 0].net, T[T.side > 0].date, "   longs (cash leaving RRP)")); print(LF.line(T[T.side < 0].net, T[T.side < 0].date, "   shorts (cash entering)"))
    print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
    rng = np.random.default_rng(31); pl = []
    for run in range(200):
        sides = {d: int(rng.choice([-1, 1])) for d in sig.index}; Tp = LF.trades(g, sig, lambda d, z: sides[d], **kw); pl += [(run, x) for x in Tp.net]
    pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean()
    print(f"   random side (200 runs): ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${T.net.mean():.0f}; p {np.mean(pm >= T.net.mean()):.3f}")
    L = T[T.side > 0]; allday = pd.Series(1.0, index=days[(days >= "2021-01-01") & (days <= "2024-12-31")]); an = LF.trades(g, allday, lambda d, z: 1, **kw).set_index("date").net
    Ly = L[(L.date >= "2021") & (L.date < "2025")]; cnt = Ly.groupby(Ly.date.dt.year).size(); lr = []
    for run in range(500):
        lr.append(np.mean(np.concatenate([an[an.index.year == y].sample(n, random_state=run * 7 + y).values for y, n in cnt.items()])))
    print(f"   longs 2021-24 ${Ly.net.mean():.0f} vs random-day longs same years ${np.mean(lr):.0f} (95th ${np.percentile(lr, 95):.0f}); p {np.mean(np.array(lr) >= Ly.net.mean()):.3f}", flush=True)
    cd = "checks/candidates/rrp_liquidity"; os.makedirs(cd, exist_ok=True)
    T.assign(date=T.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net", "risk"]].to_csv(f"{cd}/trades.csv", index=False)
    pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": True, "variants": 1}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write("# RRP liquidity -> NQ next day (2026-11-08)\n" + __doc__.split("Rule:")[1].split("POWER WARNING")[0] + "\n")
    ctx = BB.setup(); dts, D = ctx["dts"], ctx["D"]; dpos = pd.Series(np.arange(D), index=dts)
    W1, R1 = daypaths(D, [(int(dpos[d]) if d in dpos.index else None, a, n) for d, a, n in zip(T.date, T.adv, T.net)])
    print()
    BB.eval_bench(ctx, {"+ RRP liquidity 2 MNQ": (2 * W1, 2 * R1)})
    BB.funded_bench(ctx, {"+ RRP liquidity 2 MNQ": {**BB.BASE_FUNDED, "RRP": 2}}, extra={"RRP": (W1, R1[:, -1])})
    print("\n   Personal book 1-year MC return / DD p95 (+ 1 MNQ):")
    BB.personal({"+ RRP 1 MNQ": (T.net / 10 - 0.55).groupby(T.date).sum()})
