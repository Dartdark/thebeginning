"""Fade YM vs ES (user 2026-11-08, after cross_index_flow_test X2: following YM's residual vs ES lost in all 9 years, t -3.25).
PRE-REGISTERED (header committed before the first run; 1 variant; POST HOC in origin: the reverse was seen first, so promotion needs
t >= the multiple-testing bar, not 2.0). Rule = X2 with the side flipped: at 9:00 CT, Z of YM's 8:30-9:00 move beyond beta x ES's
(Relative Strength's EWMA engine); |Z| >= 1.25 -> trade YM AGAINST Z at the 9:01 open, stop 0.6 / target 1.0 x the 20-day average RTH
range, flat 15:00. YM $5 a point, tick 1, $5 + 1 tick per fill (MYM = 1/10).
Mechanism (to be checked, not assumed): Dow / Nasdaq rotation; a Dow morning lead over the S&P tends to reverse.
Checks: $ a trade by period / year, longs / shorts; random side (100 runs); daily corr with the NQ Relative Strength (MultiCharts list)
and with the plan; overlap: same-day trades with NQ Relative Strength and whether the fade's NQ-equivalent side agrees; checker
checks/candidates/fade_ym/; 150K evaluation (set + Twin 2 MNQ) + 2 / 4 MYM; funded 150K x 1.5 + Twin 2 + 2 / 4 MYM; personal book
+ 1 MYM and in place of Relative Strength (1 MNQ -> 1 / 2 MYM).
  tools/run_stamped.sh analysis/fade_ym_test.py > analysis/outputs/fade_ym_test_output.txt
"""
import sys, os, json, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import cross_index_flow_test as X
RS = X.RS
from new_sources_150k import daypaths
import bench150 as BB

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    RS.PV, RS.TICK, RS.COMM = 5.0, 1.0, 5.0
    days, N, E, g = X.load_pair("scratch_data/gy.pkl", "scratch_data/ge.pkl")
    Z = RS.signals(days, N, E, decide=900); T = RS.trades(days, N, -Z, decide=900); T = T[T.date >= "2018-01-01"].reset_index(drop=True)
    print(X.line(T.pnl, T.date, "fade YM vs ES")); print(X.line(T[T.side > 0].pnl, T[T.side > 0].date, "longs")); print(X.line(T[T.side < 0].pnl, T[T.side < 0].date, "shorts"))
    print(f"      by year $: {T.groupby(T.date.dt.year).pnl.sum().round(0).astype(int).to_dict()} | exits {T.kind.value_counts().to_dict()}")
    pl = []
    for s in range(100):
        rng = np.random.default_rng(s); Zp = np.where(np.isfinite(Z), np.abs(Z) * rng.choice([-1, 1], len(Z)), np.nan)
        Tp = RS.trades(days, N, Zp, decide=900); pl += [(s, x) for x in Tp[Tp.date >= "2018-01-01"].pnl]
    pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean()
    print(f"   random side ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${T.pnl.mean():.0f}; p {np.mean(pm >= T.pnl.mean()):.3f}", flush=True)
    cd = "checks/candidates/fade_ym"; os.makedirs(cd, exist_ok=True)
    T.assign(date=T.date.dt.strftime("%Y-%m-%d"), net=T.pnl)[["date", "side", "net"]].to_csv(f"{cd}/trades.csv", index=False)
    pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": False, "variants": 2}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write("# Fade YM vs ES (2026-11-08, post hoc in origin)\n" + __doc__.split("Rule = X2 with the side flipped:")[1].split("Mechanism")[0] + "\n")
    # overlap with NQ Relative Strength (MultiCharts per-MNQ daily column)
    Pp = pd.read_pickle("scratch_data/personal_P.pkl"); rsd = Pp.RelativeStrength
    fd = (T.pnl / 10 - 0.55).groupby(T.date).sum()
    both = fd.index.intersection(rsd[rsd != 0].index)
    print(f"   overlap: fade days {len(fd)}, NQ RS trade days {int((rsd != 0).sum())}, both {len(both)}; daily corr (all days) {fd.reindex(Pp.index, fill_value=0).corr(rsd):.2f}")
    ctx = BB.setup(); dts, D = ctx["dts"], ctx["D"]; dpos = pd.Series(np.arange(D), index=dts)
    adv = []
    for t in T.itertuples():
        lo = np.nanmin(g.l[t.day, t.j0:t.j1 + 1]) if t.side > 0 else np.nanmax(g.h[t.day, t.j0:t.j1 + 1])
        adv.append((lo - t.entry) * t.side * 5.0 - (t.gross - t.pnl))
    W1, R1 = daypaths(D, [(int(dpos[d]) if d in dpos.index else None, a, n) for d, a, n in zip(T.date, adv, T.pnl)])
    lab = ctx["lab"]; dd = pd.Series(R1[:, -1], index=dts)
    C = pd.DataFrame({k: lab.C[k] for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "TWIN")}, index=dts)
    print("   daily corr with the plan:", C[dts >= "2018"].corrwith(dd[dts >= "2018"]).round(2).to_dict(), "\n")
    BB.eval_bench(ctx, {f"+ fade YM {n} MYM": (n * W1, n * R1) for n in (2, 4)})
    print()
    BB.funded_bench(ctx, {f"+ fade YM {n} MYM": {**BB.BASE_FUNDED, "FYM": n} for n in (2, 4)}, extra={"FYM": (W1, R1[:, -1])})
    print("\n   Personal book 1-year MC return / DD p95:")
    BB.personal({"+ 1 MYM": fd, "+ 2 MYM": 2 * fd})
    BB.personal({"RS 1 MNQ -> 1 MYM": fd, "RS 1 MNQ -> 2 MYM": 2 * fd}, drop=("RelativeStrength",))
