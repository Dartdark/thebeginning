"""Overnight Tick on ES: the current OT signal, traded on ES (user 2026-11-08, batch of 5, test 3). PRE-REGISTERED (header committed
before the first run; 1 ranked item, plus 1 information line = 2 variants). Primary: the live OT rule exactly as on NQ (NQ RTH down day,
NQ closing order flow 14:15-15:15 CT from The Bridge's aggressor volume, VIX close vs its 25-day SMA: long when (flow < 0 and VIX > SMA)
or (flow >= 0 and VIX <= SMA); early closes and contract-switch nights out), but long ES 17:05 -> 03:00 CT, no stop. $50 a point,
$5 + 1 tick per fill (MES = 1/10). Information only: ES's own day (ES down day, ES bar-direction signed volume as the flow).
Checks: per trade by period, by year; random-night placebo (same count per year, 500 runs); daily corr with OT on NQ and the plan;
checker folder checks/candidates/ot_es/; 150K evaluation (set + Twin 2 MNQ) + 2 / 4 MES; funded 150K x 1.5 + Twin 2 + 2 / 4 MES;
personal book + 1 MES and + 1 MES replacing 1 MNQ of OT. Order flow ends 2026-07-07: benches run to then.
  tools/run_stamped.sh analysis/ot_es_test.py > analysis/outputs/ot_es_test_output.txt
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import overnight_tick_test as OT
from new_sources_150k import daypaths
import bench150 as BB

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    OT.PV, OT.TICK, OT.COMM = 50.0, 0.25, 5.0
    ge = pickle.load(open("scratch_data/ge.pkl", "rb")); E = OT.nights(ge)
    N = pd.read_csv("checks/candidates/overnight_tick/nights.csv", parse_dates=["date", "sess"])
    M_ = E.merge(N[["sess", "down", "half", "rsv", "hi25", "net"]].rename(columns={"down": "nq_down", "half": "nq_half", "net": "nq_net"}), on="sess", how="left")
    hi = M_.hi25.astype(bool)
    cellq = lambda q: ((q < 0) & hi) | ((q >= 0) & ~hi)
    prim = M_[M_.nq_down.fillna(False).astype(bool) & ~M_.nq_half.fillna(True).astype(bool) & M_.rsv.notna() & M_.hi25.notna() & cellq(M_.rsv)].reset_index(drop=True)
    own = M_[M_.down & ~M_.half & M_.rsv_bar.notna() & M_.hi25.notna() & cellq(M_.rsv_bar)].reset_index(drop=True)
    tt = lambda x: x.mean() / x.std(ddof=1) * np.sqrt(len(x))
    for nm, T in (("OT signal on ES (primary)", prim), ("ES's own day + bar-direction flow (info)", own)):
        a, b = T[T.date < "2023"].net, T[T.date >= "2023"].net
        print(f"   {nm:<42} n {len(T):4d} ${T.net.mean():5.0f} t {tt(T.net):5.2f} PF {T.net[T.net > 0].sum() / -T.net[T.net < 0].sum():.2f} | 2018-22 ${a.mean():.0f} (t {tt(a):.1f}) 2023+ ${b.mean():.0f} (t {tt(b):.1f}) | worst ${T.net.min():,.0f}")
        print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
    T = prim; every = M_[~M_.half & M_.rsv.notna() & M_.hi25.notna()]
    print(f"   every ES night in the same span: n {len(every)} ${every.net.mean():.0f} (t {tt(every.net):.2f})")
    rng = np.random.default_rng(9); pool = {y: every[every.date.dt.year == y].net.values for y in every.date.dt.year.unique()}
    cnt = T.groupby(T.date.dt.year).size(); pl = []
    for run in range(500):
        for y, n in cnt.items(): pl += [(run, x) for x in rng.choice(pool[y], n, replace=False)]
    pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean()
    print(f"   placebo (random ES nights, same count per year): ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; p {np.mean(pm >= T.net.mean()):.3f}", flush=True)
    cd = "checks/candidates/ot_es"; os.makedirs(cd, exist_ok=True)
    T.assign(date=T.date.dt.strftime("%Y-%m-%d"), side=1)[["date", "side", "net"]].to_csv(f"{cd}/trades.csv", index=False)
    pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": True, "variants": 2}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write("# Overnight Tick signal on ES (2026-11-08)\nLong ES 17:05 -> 03:00 CT, no stop, on NQ RTH down days when (NQ closing order flow 14:15-15:15 CT < 0 and VIX > SMA25) or (>= 0 and VIX <= SMA25); early closes and contract-switch nights excluded. $5 + 1 tick per fill per ES. Order flow = The Bridge aggressor volume on NQ.\n")
    ctx = BB.setup(); dts, D = ctx["dts"], ctx["D"]; dpos = pd.Series(np.arange(D), index=dts)
    W1, R1 = daypaths(D, [(int(dpos[d]) if d in dpos.index else None, a, n) for d, a, n in zip(T.date, T.adv, T.net)])     # per MES
    nq = N[N.down & ~N.half & N.rsv.notna() & N.hi25.notna()]; nq = nq[((nq.rsv < 0) & nq.hi25.astype(bool)) | ((nq.rsv >= 0) & ~nq.hi25.astype(bool))]
    otq = nq.groupby("date").net.sum().reindex(dts, fill_value=0.0); dd = pd.Series(R1[:, -1], index=dts); span = (dts >= "2018-01-01") & (dts <= "2026-07-07")
    lab = ctx["lab"]; C = pd.DataFrame({k: lab.C[k] for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "TWIN")}, index=dts); C["OT on NQ"] = otq
    print("   daily corr:", C[span].corrwith(dd[span]).round(2).to_dict(), "\n")
    BB.eval_bench(ctx, {f"+ OT on ES {n} MES": (n * W1, n * R1) for n in (2, 4)}, end="2026-06-01")
    print()
    BB.funded_bench(ctx, {f"+ OT on ES {n} MES": {**BB.BASE_FUNDED, "OTES": n} for n in (2, 4)}, extra={"OTES": (W1, R1[:, -1])}, end="2026-07-07")
    print("\n   Personal book 1-year MC return / DD p95 (to 2026-07-07):")
    es1 = pd.Series(R1[:, -1], index=dts) - 0.0
    BB.personal({"+ 1 MES": es1}, end="2026-07-07")
    BB.personal({"OT 1 MNQ -> 1 MES": es1}, drop=("OvernightTick",), end="2026-07-07")
