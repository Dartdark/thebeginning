"""TrendSwingTrader V2 REBUILD tested like any strategy (pre-registered checks/candidates/tst_v2_rebuild/PREREG.md; the match passed
its check: 2022-23 F1 0.658 -> 2025 F1 0.719, V1's own code 0.607 -> 0.463; ceiling = V1 code vs V1's site curve 0.793).
Primary = rank 1 of the match (EMA 21 / 50 / 200, ADX > 35, stop 1.5 ATR, half off at 4 ATR, trail 2 ATR); ranks 2-5 shown as the
family. Coinbase spot BTC 1-min 2018-06 -> 2026-10, Jesse order semantics (analysis/jesse_lib_btc_test.py engine), 0.05% fee +
0.02% slippage a side. 2018-2021 was never seen by the author's V2 page nor by the match; 2022-23 was used to match; 2024 is V1's
copy on the site; 2025-26 checked only by active-day overlap, never by return.
  tools/run_stamped.sh analysis/tst_v2_rebuild_test.py > analysis/outputs/tst_v2_rebuild_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
src = open("analysis/jesse_lib_btc_test.py", encoding="utf-8").read().split("adx_ref = P.run(P.setup())")[0]
E = {"__name__": "lib", "__doc__": "x\n"}; exec(compile(src, "jesse_lib_engine", "exec"), E)
np, pd, P = E["np"], E["pd"], E["P"]
print(__doc__.split("\n")[0])
atr, dmi, ema, simulate, tt = E["atr"], E["dmi"], E["ema"], E["simulate"], E["tt"]
b = E["bars"]("4h"); C = b.close.to_numpy(); A = atr(b); _, _, ADX = dmi(b)
ref = P.run(P.setup()); AD = ref.groupby(pd.DatetimeIndex(ref.tx).normalize()).ret.sum()


def build(f, mi, sl, a_, S, T, R):
    e1, e2, e3 = ema(C, f), ema(C, mi), ema(C, sl)
    sig = np.where((e3 < e2) & (e2 < e1) & (e1 < C) & (ADX > a_), 1, np.where((e3 > e2) & (e2 > e1) & (e1 > C) & (ADX > a_), -1, 0)); sig[:200] = 0
    def plan(i, s, e): return e - s * S * A[i], e + s * T * A[i]
    def mg(j, pos, event=None):
        if event == "half": pos["stop"] = pos["e"]; return None
        if pos["half"]: pos["stop"] = max(C[j] - R * A[j], pos["e"]) if pos["s"] == 1 else min(C[j] + R * A[j], pos["e"])
    return lambda seed=None: simulate(b, sig, plan, manage=mg, seed=seed, half=True)


def show(nm, t, full=True):
    x = t.ret; p = lambda m: x[m]
    per = {"2018-21 (unseen)": t.yr <= 2021, "2022-23 (matched)": (t.yr >= 2022) & (t.yr <= 2023), "2024": t.yr == 2024, "2025-26": t.yr >= 2025}
    pf = x[x > 0].sum() / -x[x < 0].sum()
    print(f"\n{nm}: {len(t)} trades ({len(t) / 8.3:.0f} a year), win {np.mean(x > 0):.0%}, {100 * x.mean():+.3f}% a trade ({t.r.mean():+.3f}R), PF {pf:.2f}, t {tt(x):.2f}; "
          f"2018-22 t {tt(x[t.yr <= 2022]):.2f}, 2023+ t {tt(x[t.yr >= 2023]):.2f}")
    print("   " + " | ".join(f"{k}: {100 * p(m).mean():+.3f}% t {tt(p(m)):.2f} n {m.sum()}" for k, m in per.items()))
    if full:
        print(f"   longs {100 * x[t.side == 1].mean():+.3f}% (t {tt(x[t.side == 1]):.2f}, n {(t.side == 1).sum()}) | shorts {100 * x[t.side == -1].mean():+.3f}% (t {tt(x[t.side == -1]):.2f}, n {(t.side == -1).sum()})")
        print("   by year % (sum of trade returns): " + "  ".join(f"{y} {100 * g.ret.sum():+.0f}" for y, g in t.groupby("yr")))
        dd = t.groupby(t.tx.dt.normalize()).ret.sum(); idx = pd.date_range("2018-06-01", AD.index.max())
        print(f"   daily corr with the BTC ADX ensemble: {np.corrcoef(dd.reindex(idx, fill_value=0), AD.reindex(idx, fill_value=0))[0, 1]:+.2f}")


G = pd.read_csv("checks/candidates/tst_v2_rebuild/grid.csv").head(5)
run1 = build(*[G.iloc[0][k] for k in ("fast", "mid", "slow", "adx", "stop", "half", "trail")])
T1 = run1(); show("REBUILD rank 1 (21 / 50 / 200, ADX 35, stop 1.5, half 4, trail 2)", T1)
pm = np.array([run1(seed=s).ret.mean() for s in range(40)])
print(f"   placebo (random side, 40 runs): mean {100 * pm.mean():+.3f}%, p95 {100 * np.percentile(pm, 95):+.3f}%, real {100 * T1.ret.mean():+.3f}%, p = {np.mean(pm >= T1.ret.mean()):.2f}")
show("   same, longs only (slice)", T1[T1.side == 1], full=False)
V1 = build(21, 50, 100, 25, 2.0, 3.0, 2.0)(); show("free V1 for comparison (same engine)", V1, full=False)
for k in range(1, 5):
    c = G.iloc[k]; show(f"family rank {k + 1} ({int(c.fast)} / {int(c.mid)} / {int(c.slow)}, ADX {c.adx:g}, stop {c.stop:g}, half {c.half:g}, trail {c.trail:g})",
                        build(*[c[x] for x in ("fast", "mid", "slow", "adx", "stop", "half", "trail")])(), full=False)
T1.to_csv("checks/candidates/tst_v2_rebuild/trades_rank1.csv", index=False)
