"""Scan for ACTIVE strategies to add to the live #5 evaluation book (user 2026-11-12: 'scan the tier list for active strats';
book = bench150.LIVE_EVAL: ONB $3,500, MON_BR 5, Twin 2, DT 2, JF 1; VB retired, EOS dropped).
Candidates = every tiered strategy with a saved trade list (Apex-legal, flat by the close or inside one session): the eval-set
pieces (eval_set_builder: RS, LDF, NFP, MON, OT, CLS, MOC, ONB_ML) + Bridge noise longs (NBL), T fade (T_ONESIDE stop), S47 v2,
FVB, FINRA longs. Each added at 3 sizes (fixed: 1 / 2 / 3 micro; risk pieces: $500 / $1,000 / $1,500 at the stop).
Measures: trading days a year; fresh 150K pass 2018-22 and 2023-26, and from #5 now; paired diff vs the book, 60-day block bands.
'Helps' = the 2023-26 band AND the #5 band are above 0 and 2018-22 is not below. 13 x 3 = 39 trials: a 'helps' needs the bands, not
just a positive point. (RS trades: scratch_data/rs_trades.csv from analysis/relative_strength_test.py.)
  tools/run_stamped.sh analysis/active_scan_eval.py > analysis/outputs/active_scan_eval_output.txt
"""
import sys, io, runpy, contextlib; sys.path.insert(0, "analysis"); sys.argv = ["x"]
import numpy as np, pandas as pd
src = open("analysis/eval_size_combo.py").read().split("rows = []")[0].replace("cache=True", "cache=False")
ns = {}; exec(compile(src, "eval_size_combo_head", "exec"), ns)
book, fresh, now, P, dts, DES, HOL, NOWV, LIVE, g, trr, D = (ns[k] for k in ("book", "fresh", "now", "P", "dts", "DES", "HOL", "NOWV", "LIVE", "g", "trr", "D"))
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from new_sources_150k import daypaths
import funded_bootstrap as FB
def band(d):
    rng = np.random.default_rng(1); n = len(d); nb_ = int(np.ceil(n / 60)); st = rng.integers(0, n, (1000, nb_))
    mm = d[((st[:, :, None] + np.arange(60)) % n).reshape(1000, -1)[:, :n]].mean(1); return np.percentile(mm, 5), np.percentile(mm, 95)
atr = g.daily_atr(15)[trr]; U = {}; RISK = {}
t0 = pd.Timestamp(g.ts[0])
def norm(t, date_col="date"):
    t = t.copy()
    if "row" in t: t["day"] = t.row.astype(int)
    else: t["day"] = ((pd.to_datetime(t[date_col]) - t0).dt.days).astype(int)
    if not pd.api.types.is_numeric_dtype(t.kind): t["kind"] = t.kind.map({"stop": 0, "target": 1, "tgt": 1}).fillna(2).astype(int)
    t = t[pd.to_datetime(t[date_col]) >= "2018-01-01"]
    return t[["day", "j0", "j1", "side", "entry", "exit", "kind"]].astype({"day": int, "j0": int, "j1": int, "kind": int}).reset_index(drop=True)
def add(nm, t, stop=None):
    w, r = paths(g, t); U[nm] = (w[trr] / 10, r[trr] / 10)
    if stop is not None: RISK[nm] = np.nan_to_num(stop, nan=1e12)
add("LDF", with_slippage(load_mc(g, REPORTS["LDF_MC"][0])), REPORTS["LDF_MC"][1] * atr)
add("NFP", with_slippage(load_mc(g, REPORTS["NFP_MC"][0])), REPORTS["NFP_MC"][1] * atr)
add("ONB_ML", with_slippage(load_mc(g, REPORTS["ONB_ML2_MC"][0])), REPORTS["ONB_ML2_MC"][1] * atr)
add("MON", with_slippage(load_mc(g, REPORTS["MON_MC"][0])))
rs = pd.read_csv("scratch_data/rs_trades.csv"); rs = rs.assign(kind=rs.kind.map({"stop": 0, "target": 1, "flat": 2}))[["day", "j0", "j1", "side", "entry", "exit", "kind"]]
add("RS", with_slippage(rs))
N = pd.read_csv("checks/candidates/overnight_tick/nights.csv", parse_dates=["date", "sess"]); N = N[N.down & ~N.half & N.rsv.notna() & N.hi25.notna()]
N = N[((N.rsv < 0) & N.hi25.astype(bool)) | ((N.rsv >= 0) & ~N.hi25.astype(bool))]; dp = pd.Series(np.arange(D), index=dts)
U["OT"] = daypaths(D, [(int(dp[d]) if d in dp.index else None, a, n) for d, a, n in zip(N.date, N.adv, N.net)])
sys.argv = ["x", "scratch_data"]
with contextlib.redirect_stdout(io.StringIO()):
    lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]; lab = FB.add_moc_mes(lab)
for k, nm in (("CLS", "CLS"), ("MOC_MES", "MOC")):
    Wk = lab.W[k]; Rk = np.zeros_like(Wk); Rk[:, -1] = lab.C[k]; U[nm] = (Wk, Rk)
nbl = pd.read_csv("analysis/outputs/bridge_noise_15m_trades_rth_longs.csv", parse_dates=["date"]); add("NBL", norm(nbl))
add("T_FADE", with_slippage(norm(pd.read_csv("checks/candidates/t_oneside/python_trades_stop.csv"))))
add("S47v2", with_slippage(norm(pd.read_csv("checks/candidates/s47_v2/python_trades_v2.csv"))))
add("FVB", with_slippage(norm(pd.read_csv("checks/candidates/fvb/trades.csv"))))
add("FINRA_L", with_slippage(norm(pd.read_csv("checks/candidates/finra_longs/mc_trades.csv"))))
W0, R0 = book(LIVE); f0 = fresh(W0, R0); n0 = now(W0, R0); yr = dts.year
print(f"book {LIVE}: fresh 18-22 {f0[DES].mean():.1%} 23-26 {f0[HOL].mean():.1%} | #5 now {n0[NOWV].mean():.1%}")
helps = []
for nm, (Wu, Ru) in U.items():
    sizes = (500, 1000, 1500) if nm in RISK else (1, 2, 3)
    unit = (lambda m: np.floor(m / (RISK[nm] * 2.0))[:, None]) if nm in RISK else (lambda m: float(m))
    days = (Ru[:, -1] != 0) & (yr >= 2018); per_y = days.sum() / 8.85
    u1 = unit(sizes[0]); one = (Ru[:, -1] * (u1[:, 0] if np.ndim(u1) else u1))[days]
    print(f"\n== {nm}: {per_y:.0f} trading days a year, ${one.mean():,.0f} a trading day at size {sizes[0]} (win {np.mean(one > 0):.0%})")
    for s in sizes:
        m = unit(s); W = W0 + Wu * m; R = R0 + Ru * m; f = fresh(W, R); n = now(W, R)
        d1 = f[DES] - f0[DES]; d2 = f[HOL] - f0[HOL]; d3 = n[NOWV] - n0[NOWV]; b2 = band(d2); b3 = band(d3)
        ok = b2[0] > 0 and b3[0] > 0 and d1.mean() >= 0
        if ok: helps.append((nm, s, round(d2.mean(), 3), round(d3.mean(), 3)))
        print(f"   size {s:>5}: 18-22 {d1.mean():+.1%} | 23-26 {d2.mean():+.1%} ({b2[0]:+.1%}/{b2[1]:+.1%}) | #5 now {d3.mean():+.1%} ({b3[0]:+.1%}/{b3[1]:+.1%}){'   <- HELPS' if ok else ''}", flush=True)
print(f"\n== helps (both bands > 0, 2018-22 not below): {helps if helps else 'none'}")

print("\n== follow-up (added after the scan, disclosed): the leads together")
def sz(nm, s):
    u = (np.floor(s / (RISK[nm] * 2.0))[:, None]) if nm in RISK else float(s); return U[nm][0] * u, U[nm][1] * u
for combo in ({"NBL": 3}, {"NBL": 3, "LDF": 1000}, {"NBL": 3, "FINRA_L": 2}, {"NBL": 3, "LDF": 1000, "FINRA_L": 2}, {"LDF": 1000, "FINRA_L": 2}, {"NBL": 2, "LDF": 1000, "FINRA_L": 1}):
    W, R = W0.copy(), R0.copy()
    for nm, s in combo.items(): w, r = sz(nm, s); W += w; R += r
    f = fresh(W, R); n = now(W, R); d1 = f[DES] - f0[DES]; d2 = f[HOL] - f0[HOL]; d3 = n[NOWV] - n0[NOWV]; b2 = band(d2); b3 = band(d3)
    print(f"   {combo}: 18-22 {d1.mean():+.1%} | 23-26 {d2.mean():+.1%} ({b2[0]:+.1%}/{b2[1]:+.1%}) | #5 now {n[NOWV].mean():.1%} ({d3.mean():+.1%}, {b3[0]:+.1%}/{b3[1]:+.1%})", flush=True)
