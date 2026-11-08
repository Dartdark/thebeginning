"""Twin's Morning Momentum engine on CL, GC and ZN, anchored to each market's own open (user 2026-11-08, batch of 5, test 1).
PRE-REGISTERED (header committed before the first run; one variant per market, 3 ranked items). Rules = Twin v2.1 MO
(twin_continuation_test.simulate, use_bo=False, v21 holiday rules): 10-min oscillator (close - EMA21) / (3 x ATR14) smoothed EMA3
crossing +-100 on a full 10-min bucket ending in the window, first signal a day, market entry, no target. Window and exit move with
the market's regular-hours open / close as Twin's do with NQ's (open + 10 .. open + 60 min; flat 10 min before the close):
  CL  window 08:10-09:00 CT, flat 13:20   $1,000 a point, tick 0.01,     $5 + 1 tick per fill (MCL = 1/10)
  GC  window 07:30-08:20 CT, flat 12:20   $100 a point,   tick 0.10,     $5 + 1 tick per fill (MGC = 1/10)
  ZN  window 07:30-08:20 CT, flat 13:50   $1,000 a point, tick 1/64,     $5 + 1 tick per fill (no micro: whole contracts)
Stop 0.3 x the daily ATR(15) known that morning (Twin's 75 NQ points = 0.29 x NQ's median daily ATR 2018-26).
Checks: per trade by period, longs / shorts, by year; random-side placebo (100 runs); daily corr with Twin NQ momentum and the plan;
checker folder checks/candidates/mo_<mkt>/; 150K evaluation (set + Twin 2 MNQ) + the market at Twin's risk ($300 per stop, from the
2023+ median stop) and half of it; funded 150K x 1.5 + Twin 2 + the same sizes; personal book + the market at the risk-matched size.
  tools/run_stamped.sh analysis/mo_markets_test.py CL > analysis/outputs/mo_markets_test_CL_output.txt   (GC, ZN alike)
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import twin_continuation_test as tc
from twin_continuation_bench import grids
import bench150 as BB

SPEC = {"CL": dict(win=(810, 900), ex=1320, pv=1000.0, tick=0.01, micro=True), "GC": dict(win=(730, 820), ex=1220, pv=100.0, tick=0.10, micro=True),
        "ZN": dict(win=(730, 820), ex=1350, pv=1000.0, tick=1 / 64, micro=False)}
COMM = 5.0

if __name__ == "__main__":
    mk = sys.argv[1]; S = SPEC[mk]; print(__doc__.split("\n")[0]); print(f"   market {mk}")
    f = f"scratch_data/{mk.lower()}.pkl"
    if not os.path.exists(f):
        from grid24 import Grid24
        pickle.dump(Grid24(f"data/{mk}_1min_20*.csv", night_pattern=""), open(f, "wb"), protocol=4)
    gx = pickle.load(open(f, "rb")); Bx = tc.flatten(gx); Bx["atr"] = gx.daily_atr(15)[Bx["row"]]
    kw = dict(use_bo=False, v21=True, mo_stop_atr=0.3, mo_window=S["win"], mo_exit=S["ex"], pv=S["pv"], tick=S["tick"], comm=COMM)
    T = tc.simulate(Bx, **kw); T = T[T.date >= "2018-01-01"].reset_index(drop=True)
    stop_d = 0.3 * Bx["atr"][T.i0] * S["pv"]; T["risk"] = stop_d
    tt = lambda x: x.mean() / x.std(ddof=1) * np.sqrt(len(x)); a, b = T[T.date < "2023"].net, T[T.date >= "2023"].net
    print(f"   MO on {mk}: n {len(T)} ${T.net.mean():.0f} t {tt(T.net):.2f} PF {T.net[T.net > 0].sum() / -T.net[T.net < 0].sum():.2f} | 2018-22 ${a.mean():.0f} (t {tt(a):.1f}) 2023+ ${b.mean():.0f} (t {tt(b):.1f}) | longs ${T[T.side > 0].net.mean():.0f} (t {tt(T[T.side > 0].net):.1f}) shorts ${T[T.side < 0].net.mean():.0f} (t {tt(T[T.side < 0].net):.1f}) | worst ${T.net.min():,.0f}")
    print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
    print(f"      exits: {T.kind.map({0: 'stop', 2: 'time'}).value_counts().to_dict()} | median stop ${np.median(stop_d):,.0f} per contract (2023+ ${np.median(stop_d[T.date >= '2023']):,.0f})")
    cd = f"checks/candidates/mo_{mk.lower()}"; os.makedirs(cd, exist_ok=True)
    if tt(T.net) < 2.0:      # stop rule added after the first run (2026-11-08, lab rule: stop at the first failed gate); rules unchanged
        T.assign(date=T.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net", "risk"]].to_csv(f"{cd}/trades.csv", index=False)
        json.dump({"kind": "strategy", "pre_registered": True, "variants": 1}, open(f"{cd}/meta.json", "w"))
        open(f"{cd}/spec.md", "w").write(f"# Morning Momentum on {mk} (Twin v2.1 MO rules, own-open window, 2026-11-08)\nWindow {S['win']} CT, flat {S['ex']}, stop 0.3 x daily ATR(15), no target; ${COMM:.0f} + 1 tick per fill. Stopped at the first failed gate (t < 2): no placebo or benches.\n")
        print("   STOPPED at the first failed gate (t < 2.0): no placebo, no benches"); sys.exit(0)
    rng = np.random.default_rng(6); pl = []
    for run in range(100):
        Tp = tc.simulate(Bx, placebo_rng=rng, **kw); Tp = Tp[Tp.date >= "2018-01-01"]; pl += [(run, x) for x in Tp.net]
    pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean(); print(f"   random-side placebo ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; p {np.mean(pm >= T.net.mean()):.2f}", flush=True)
    cd = f"checks/candidates/mo_{mk.lower()}"; os.makedirs(cd, exist_ok=True)
    T.assign(date=T.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net", "risk"]].to_csv(f"{cd}/trades.csv", index=False)
    pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": True, "variants": 1}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write(f"# Morning Momentum on {mk} (Twin v2.1 MO rules, own-open window, 2026-11-08)\n{mk} 1-minute, 24h, CT. 10-minute clock buckets; oscillator = (close - EMA21 of bucket closes) / (3 x Wilder ATR14 of buckets) x 100, EMA3-smoothed; long when it crosses above +100 (short below -100) on a full bucket ending {S['win'][0]}-{S['win'][1]} CT, one attempt a day, no CME early-close days; market entry next bar; stop 0.3 x daily ATR(15); no target; exit at {S['ex']} CT. ${COMM:.0f} + 1 tick per fill per contract.\n")
    # ---- benches
    ctx = BB.setup(); We, Re = grids(gx, Bx, T, pv=S["pv"])
    W1, R1 = BB.to_nq_days(ctx, gx, We / 10, Re / 10)                      # per micro (1/10 contract)
    dts, yr = ctx["dts"], ctx["yr"]
    lab = ctx["lab"]; mo_nq = ctx["Tn"][ctx["Tn"].setup == "MO"].groupby("date").net.sum().reindex(dts, fill_value=0.0); dd = pd.Series(R1[:, -1], index=dts)
    C = pd.DataFrame({k: lab.C[k] for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "CLS")}, index=dts); C["Twin NQ momentum"] = mo_nq
    print("   daily corr:", C[yr >= 2018].corrwith(dd[yr >= 2018]).round(2).to_dict())
    m23 = np.median(stop_d[T.date >= "2023"]) / 10                          # $ per micro at the stop
    q = max(1, int(round(300 / m23)))
    if not S["micro"]: q = max(10, int(round(q / 10)) * 10)
    sizes = sorted({q, max(1 if S["micro"] else 10, (q // 2) if S["micro"] else int(round(q / 20)) * 10)})
    unit = (lambda n: f"{n} M{mk}") if S["micro"] else (lambda n: f"{n // 10} {mk}")
    print(f"   risk-matched size: {unit(q)} (${q * m23:,.0f} per stop vs Twin 2 MNQ $300); sizes tested {[unit(n) for n in sizes]}\n")
    BB.eval_bench(ctx, {f"+ {mk} momentum {unit(n)}": (n * W1, n * R1) for n in sizes})
    print()
    BB.funded_bench(ctx, {f"+ {mk} momentum {unit(n)}": {**BB.BASE_FUNDED, "MOX": n} for n in sizes}, extra={"MOX": (W1, R1[:, -1])})
    print("\n   Personal book 1-year MC return / DD p95 (+ the market at the risk-matched size):")
    BB.personal({f"+ {unit(q)}": pd.Series(q * R1[:, -1], index=dts)})
