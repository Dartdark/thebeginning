"""Late-Day Flow stop: none / wider (user 2026-11-08, lead from ingredient_ablation3.py: 'no stop' $94 t 3.5, max DD $15.0k -> $11.9k).
PRE-REGISTERED (header committed before the first run; 2 variants; post hoc in origin). Rule otherwise unchanged (NQ_Late_Day_Flow.txt:
at 14:00 CT, move from the 08:30 open >= 0.4 x ATR15 -> follow at the next bar's open, out at the 14:30 close, early-close days skipped):
  base  stop 0.25 x ATR15 (as live)      A  no stop      B  stop 0.5 x ATR15
Costs $7.25 + 1 tick per NQ market / stop fill. Per variant: $ a trade, t, total, max DD, worst trade, by period / year, longs / shorts;
random side (100 runs); checker checks/candidates/ldf_nostop, ldf_stop50. Books, each REPLACING the plan's Late-Day Flow (MultiCharts list)
with the Python rebuild (as is vs A vs B), same size: 50K funded (funded_bootstrap, plan LDF 2 MNQ, 600 paired 2-year histories),
150K funded x 1.5 + Twin 2 (bench150, LDF 3 MNQ), personal book (LateDayFlow column, 1 MNQ).
  tools/run_stamped.sh analysis/ldf_stop_test.py > analysis/outputs/ldf_stop_test_output.txt
"""
import sys, os, io, json, pickle, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from replica import is_early_close
from funded_lab import with_slippage
import bench150 as BB

PV, TICK, COMM = 20.0, 0.25, 7.25


def ldf(g, stop=0.25, k=0.4, rng=None):
    """Trades with raw prices (lab format) and net after costs; stop None = no stop."""
    atr = g.daily_atr(15); ts = pd.DatetimeIndex(g.ts); rows = []; js, jx, j0o = jof(1400), jof(1430), jof(831)
    for d in g.trading:
        if ts[d].year < 2018 or np.isnan(atr[d]) or is_early_close(ts[d]): continue
        o0, cs = g.o[d, j0o], g.c[d, js]
        if np.isnan(o0) or np.isnan(cs) or np.isnan(g.c[d, jx]): continue
        mv = cs - o0
        if abs(mv) < k * atr[d] or mv == 0: continue
        side = int(np.sign(mv)) if rng is None else int(rng.choice([-1, 1]))
        j0 = js + 1; e = g.o[d, j0]; px = None; kind = 2; j1 = jx
        if stop is not None:
            sl = e - side * stop * atr[d]
            for j in range(j0, jx + 1):
                if np.isnan(g.c[d, j]): continue
                if (g.l[d, j] <= sl) if side > 0 else (g.h[d, j] >= sl):
                    px = min(g.o[d, j], sl) if side > 0 else max(g.o[d, j], sl); kind = 0; j1 = j; break
        if px is None: px = g.c[d, jx]
        rows.append(dict(day=d, j0=j0, j1=j1, side=side, entry=e, exit=px, kind=kind, date=ts[d],
                         net=(px - e) * side * PV - COMM - 2 * TICK * PV))
    return pd.DataFrame(rows)


def line(x, d, nm):
    x = pd.Series(np.asarray(x, float)); d = pd.DatetimeIndex(d); tt = lambda v: v.mean() / v.std(ddof=1) * np.sqrt(len(v)) if len(v) > 2 else np.nan
    a, b = x[(d < "2023").tolist()], x[(d >= "2023").tolist()]; pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    cum = pd.Series(x.values, index=d).groupby(level=0).sum().cumsum(); mdd = (cum.cummax() - cum).max()
    return (f"   {nm:<26} n {len(x):5d} ${x.mean():5.0f} t {tt(x):5.2f} PF {pf:4.2f} total ${x.sum() / 1000:5.0f}k maxDD ${mdd / 1000:4.1f}k | 2018-22 ${a.mean():4.0f} (t {tt(a):4.1f})"
            f" 2023+ ${b.mean():4.0f} (t {tt(b):4.1f}) | worst ${x.min():,.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb"))
    V = {"base (stop 0.25 ATR)": 0.25, "A no stop": None, "B stop 0.5 ATR": 0.5}; T = {nm: ldf(g, s) for nm, s in V.items()}
    for nm, t in T.items():
        print(line(t.net, t.date, nm)); print(line(t[t.side > 0].net, t[t.side > 0].date, "   longs")); print(line(t[t.side < 0].net, t[t.side < 0].date, "   shorts"))
        print(f"      by year $: {t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict()} | stops {int((t.kind == 0).sum())}")
    for nm, cd_, s in (("A no stop", "ldf_nostop", None), ("B stop 0.5 ATR", "ldf_stop50", 0.5)):
        pl = []
        for r in range(100): pl += [(r, x) for x in ldf(g, s, rng=np.random.default_rng(r)).net]
        pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean(); t = T[nm]
        print(f"   {nm}: random side ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${t.net.mean():.0f}; p {np.mean(pm >= t.net.mean()):.2f}", flush=True)
        cd = f"checks/candidates/{cd_}"; os.makedirs(cd, exist_ok=True)
        t.assign(date=t.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net"]].to_csv(f"{cd}/trades.csv", index=False)
        pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
        json.dump({"kind": "strategy", "pre_registered": True, "variants": 2}, open(f"{cd}/meta.json", "w"))
        open(f"{cd}/spec.md", "w").write(f"# Late-Day Flow, {nm} (2026-11-08)\nNQ: at 14:00 CT, move from the 08:30 open >= 0.4 x ATR15 -> follow at the next bar's open, out at the 14:30 close, early-close days skipped; stop: {'none' if s is None else f'{s} x ATR15'}. $7.25 + 1 tick per fill.\n")
    lt = {nm: with_slippage(t[["day", "j0", "j1", "side", "entry", "exit", "kind"]].reset_index(drop=True)) for nm, t in T.items()}
    keys = {"base (stop 0.25 ATR)": "LDF_PY", "A no stop": "LDF_A", "B stop 0.5 ATR": "LDF_B"}
    # personal
    dmn = lambda t: (t.net / 10 - 0.55).groupby(t.date).sum()
    print("\n   Personal book 1-year MC return / DD p95 (LateDayFlow column replaced, 1 MNQ):")
    BB.personal({nm: dmn(t) for nm, t in T.items()}, drop=("LateDayFlow",))
    # 50K funded
    import funded_bootstrap as FB
    with contextlib.redirect_stdout(io.StringIO()):
        lab = FB.plan_lab()
    for nm, k in keys.items(): lab.add(k, lt[nm], slippage=False)
    P0 = {k: v for k, v in FB.PLAN.items() if k != "LDF_MC"}; n_ldf = FB.PLAN["LDF_MC"]
    plans = {f"{nm} {n_ldf} MNQ": {**P0, k: n_ldf} for nm, k in keys.items()}
    df, s, _ = FB.Boot(lab).compare(plans, n=600, L=20); print(f"\n   50K funded (plan, LDF {n_ldf} MNQ replaced), 600 paired 2-year histories:\n{s}", flush=True)
    # 150K funded
    ctx = BB.setup(); lab = ctx["lab"]
    for nm, k in keys.items(): lab.add(k, lt[nm], slippage=False)
    base = {k: v for k, v in BB.BASE_FUNDED.items() if k != "LDF_MC"}; n3 = BB.BASE_FUNDED["LDF_MC"]
    BB.BASE_FUNDED = {**base, "LDF_PY": n3}
    BB.funded_bench(ctx, {f"A no stop {n3} MNQ": {**base, "LDF_A": n3}, f"B stop 0.5 ATR {n3} MNQ": {**base, "LDF_B": n3}},
                    label=f"Funded 150K x 1.5 + Twin 2 (LDF {n3} MNQ: Python rebuild as the base)")
