"""New-mechanism search (user 2026-11-08, after ingredient rounds 1-3): two untested uses of the cross-index engine. PRE-REGISTERED (header
committed before the first run; 2 ranked items, 1 variant each). Engine = Relative Strength's Z (relative_strength_test.signals: EWMA beta
and residual variance of 1-min RTH log returns, 20-day half-life; Z = (A's move since 8:30 - beta x B's) / sqrt(residual var x minutes)).
  X1 Late relative flow (Relative Strength's engine in Late-Day Flow's window; mechanism: Nasdaq-100 leveraged ETFs rebalance more than the
     S&P ones on days NQ outruns ES, in the last hour): at 14:00 CT, |Z of NQ vs ES since 8:30| >= 1.25 -> follow NQ at the 14:01 open,
     stop 0.25 x the 20-day average RTH range (Late-Day Flow's stop), no target, out at the 14:30 close. NQ, $7.25 + 1 tick per fill.
  X2 Relative Strength on YM vs ES (same rule as the live Relative Strength, the Dow instead of the Nasdaq): at 9:00 CT, |Z of YM vs ES|
     >= 1.25 -> follow YM at the 9:01 open, stop 0.6 / target 1.0 x the 20-day average RTH range, flat 15:00. YM $5 a point, tick 1,
     $5 + 1 tick per fill (MYM = 1/10).
Checks per item: $ a trade by period / year, longs / shorts; random side on the same days (100 runs); daily corr with Late-Day Flow and
Relative Strength (NQ); checker checks/candidates/x1_late_relflow, x2_rs_ym; 150K evaluation (set + Twin 2 MNQ) + 2 micros; funded 150K
x 1.5 + Twin 2 + 2 micros; personal book + 1 micro.
  tools/run_stamped.sh analysis/cross_index_flow_test.py > analysis/outputs/cross_index_flow_test_output.txt
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
sys.argv = [sys.argv[0], "scratch_data"]
import relative_strength_test as RS
from new_sources_150k import daypaths
import bench150 as BB


def load_pair(fa, fb):
    """RS.load with any pair: A traded, B the reference (both Grid24 pickles)."""
    g = pickle.load(open(fa, "rb")); e = pickle.load(open(fb, "rb")); hol = RS.holidays(); rows = []
    ei = {int(d): k for k, d in enumerate(e.dates)}; a, b, b2 = jof(830), jof(1500), jof(1555)
    for d in g.trading:
        dt = int(g.dates[d])
        if dt < 20170901 or dt not in ei: continue
        k = ei[dt]
        if np.isnan(g.c[d, a + 1:b + 1]).all() or np.isnan(e.c[k, a + 1:b + 1]).all(): continue
        rows.append((d, k, dt, dt not in hol and g.last_j[d] >= b and e.last_j[k] >= b))
    days = pd.DataFrame(rows, columns=["d", "k", "date", "ok"])
    f = lambda x: pd.DataFrame(x).ffill(axis=1).to_numpy()
    N = {c: f(getattr(g, c)[days.d.to_numpy(), a:b2 + 1]) for c in ("o", "h", "l", "c")}; E = f(e.c[days.k.to_numpy(), a:b2 + 1])
    N["o"] = np.where(np.isnan(N["o"]), N["c"], N["o"])
    return days, N, E, g


def line(x, d, nm):
    x = pd.Series(np.asarray(x, float)); d = pd.DatetimeIndex(d); tt = lambda v: v.mean() / v.std(ddof=1) * np.sqrt(len(v)) if len(v) > 2 else np.nan
    a, b = x[(d < "2023").tolist()], x[(d >= "2023").tolist()]; pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    cum = pd.Series(x.values, index=d).groupby(level=0).sum().cumsum(); mdd = (cum.cummax() - cum).max()
    return (f"   {nm:<14} n {len(x):5d} ${x.mean():5.0f} t {tt(x):5.2f} PF {pf:4.2f} total ${x.sum() / 1000:5.0f}k maxDD ${mdd / 1000:4.1f}k | 2018-22 ${a.mean():4.0f} (t {tt(a):4.1f})"
            f" 2023+ ${b.mean():4.0f} (t {tt(b):4.1f}) | worst ${x.min():,.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    ctx = BB.setup(); dts = ctx["dts"]; D = ctx["D"]; dpos = pd.Series(np.arange(D), index=dts)
    Pp = pd.read_pickle("scratch_data/personal_P.pkl")
    ITEMS = {"x1_late_relflow": dict(fa="scratch_data/g24.pkl", decide=1400, kw=dict(stop_f=0.25, tgt_f=None, flat=1430), cost=(20.0, 0.25, 7.25), mk="MNQ"),
             "x2_rs_ym": dict(fa="scratch_data/gy.pkl", decide=900, kw=dict(), cost=(5.0, 1.0, 5.0), mk="MYM")}
    for name, it in ITEMS.items():
        RS.PV, RS.TICK, RS.COMM = it["cost"]
        days, N, E, g = load_pair(it["fa"], "scratch_data/ge.pkl")
        Z = RS.signals(days, N, E, decide=it["decide"]); T = RS.trades(days, N, Z, decide=it["decide"], **it["kw"]); T = T[T.date >= "2018-01-01"].reset_index(drop=True)
        print(f"\n{name}:"); print(line(T.pnl, T.date, "all")); print(line(T[T.side > 0].pnl, T[T.side > 0].date, "longs")); print(line(T[T.side < 0].pnl, T[T.side < 0].date, "shorts"))
        print(f"      by year $: {T.groupby(T.date.dt.year).pnl.sum().round(0).astype(int).to_dict()} | exits {T.kind.value_counts().to_dict()}")
        pl = []
        for s in range(100):
            rng = np.random.default_rng(s); Zp = np.where(np.isfinite(Z), np.abs(Z) * rng.choice([-1, 1], len(Z)), np.nan)
            Tp = RS.trades(days, N, Zp, decide=it["decide"], **it["kw"]); pl += [(s, x) for x in Tp[Tp.date >= "2018-01-01"].pnl]
        pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean()
        print(f"   random side ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${T.pnl.mean():.0f}; p {np.mean(pm >= T.pnl.mean()):.2f}", flush=True)
        cd = f"checks/candidates/{name}"; os.makedirs(cd, exist_ok=True)
        T.assign(date=T.date.dt.strftime("%Y-%m-%d"), net=T.pnl)[["date", "side", "net"]].to_csv(f"{cd}/trades.csv", index=False)
        pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
        json.dump({"kind": "strategy", "pre_registered": True, "variants": 1}, open(f"{cd}/meta.json", "w"))
        open(f"{cd}/spec.md", "w").write(f"# {name} (2026-11-08)\n" + __doc__.split("PRE-REGISTERED")[1].split("Checks per item")[0] + "\n")
        # worst-path approximation per day: min(adverse, net) via daypaths (per full contract -> per micro)
        pv, tick, comm = it["cost"]
        adv = []
        for t in T.itertuples():                                    # worst open P&L during the trade (1-min lows / highs), after costs
            lo = np.nanmin(g.l[t.day, t.j0:t.j1 + 1]) if t.side > 0 else np.nanmax(g.h[t.day, t.j0:t.j1 + 1])
            adv.append((lo - t.entry) * t.side * pv - (t.gross - t.pnl))
        W1, R1 = daypaths(D, [(int(dpos[d]) if d in dpos.index else None, a, n) for d, a, n in zip(T.date, adv, T.pnl)])
        dd = pd.Series(R1[:, -1], index=dts); lab = ctx["lab"]
        rs_nq = Pp.RelativeStrength.reindex(dts, fill_value=0.0); ldf_ = pd.Series(lab.C["LDF_MC"], index=dts)
        print("   daily corr:", {"Late-Day Flow": round(dd.corr(ldf_), 2), "Relative Strength NQ": round(dd.corr(rs_nq), 2), "Twin": round(dd.corr(pd.Series(lab.C['TWIN'], index=dts)), 2)})
        print()
        BB.eval_bench(ctx, {f"+ {name} 2 {it['mk']}": (2 * W1, 2 * R1)})
        BB.funded_bench(ctx, {f"+ {name} 2 {it['mk']}": {**BB.BASE_FUNDED, name: 2}}, extra={name: (W1, R1[:, -1])})
        print(f"   Personal book 1-year MC return / DD p95 (+ 1 {it['mk']}):")
        BB.personal({f"+ 1 {it['mk']}": (T.pnl / 10 - 0.55).groupby(T.date).sum()})
