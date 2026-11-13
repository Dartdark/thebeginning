"""Evaluation-specific 150K set (user 2026-11-09: 'develop a strategy to bolster the eval phase'; diagnosis analysis/eval_failure_diag.py:
89% of failed evaluations die from one big VB / ONB stop, each about the $2,000 daily loss limit). PRE-REGISTERED (header committed before
the first run). Method (an optimisation, so the holdout is the test):
  candidates (MultiCharts-confirmed or rebuilt, Apex-legal, flat by the close), per MNQ unless noted:
    fixed units (1 micro): VB, Bridge Monday (MON_BR), Monday Long (MON), Twin cap1, Dual Thrust (DT), Relative Strength both (RS),
      Overnight Tick (OT), CL Sunday fade (per MCL), ES MOC (per MES)
    risk units ($250 at the stop): ONB ADX30 (stop 0.25 ATR), EOS, NFP, Late-Day Flow, ONB ML v2
  cap: a piece's size is limited so its 1st-percentile worst intraday day (2018-22) loses <= $1,500 (no single piece near the $2,000 limit);
  objective: 150K evaluation pass rate (plan_150k_test.evaluation, R150) over DESIGN starts 2018-01-02 -> 2022-11-30 (21-day windows end in
    2022); greedy coordinate search from the current set clipped to the caps: each step tries +1 / -1 unit on every piece and keeps the best
    move if it adds >= 0.2 points; stop when none does (max 60 steps);
  test once: HOLDOUT starts 2023-01-03 -> 2026-09-01 (never used by the search): pass / fail / time-out vs the current set, paired
    difference with a 60-day block bootstrap band; also 2018-22 and all starts; days to pass; worst-day exposure.
Adoption needs a holdout gain whose band excludes zero; the funded plan is separate (after the pass the account switches to it).
  tools/run_stamped.sh analysis/eval_set_builder.py > analysis/outputs/eval_set_builder_output.txt
"""
import sys, io, pickle, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import twin_continuation_test as tc
from twin_continuation_bench import grids
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from combine_levers_test import ONB30
from plan_150k_test import evaluation, R150
from new_sources_150k import daypaths
import funded_bootstrap as FB

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); trr = list(g.trading); D = len(trr); dts = pd.DatetimeIndex(g.ts[trr]); atr = g.daily_atr(15)[trr]
    U = {}; RISK = {}                                                     # name -> (W, R) per unit; RISK: stop points per day for $ units
    def add_trades(nm, t, stop_pts=None):
        w, r = paths(g, t); U[nm] = (w[trr] / 10, r[trr] / 10)
        if stop_pts is not None: RISK[nm] = np.nan_to_num(stop_pts, nan=1e12)
    add_trades("VB", with_slippage(load_mc(g, REPORTS["VB"][0])))
    add_trades("ONB30", with_slippage(load_mc(g, ONB30)), 0.25 * atr)
    add_trades("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])), REPORTS["EOS"][1] * atr)
    add_trades("NFP", with_slippage(load_mc(g, REPORTS["NFP_MC"][0])), REPORTS["NFP_MC"][1] * atr)
    add_trades("LDF", with_slippage(load_mc(g, REPORTS["LDF_MC"][0])), REPORTS["LDF_MC"][1] * atr)
    add_trades("ONB_ML", with_slippage(load_mc(g, REPORTS["ONB_ML2_MC"][0])), REPORTS["ONB_ML2_MC"][1] * atr)
    add_trades("MON", with_slippage(load_mc(g, REPORTS["MON_MC"][0])))
    add_trades("MON_BR", load_bridge_mc(g))
    B = tc.flatten(g); Tn = tc.simulate(B, max_stop_mult=1.0, v21=True); Tn = Tn[Tn.date >= "2018-01-01"]; w, r = grids(g, B, Tn); U["TWIN"] = (w[trr] / 10, r[trr] / 10)
    import dual_thrust_bench as DTB
    add_trades("DT", DTB.dt_trades(g))
    rs = pd.read_csv("scratch_data/rs_trades.csv"); rs = rs.assign(kind=rs.kind.map({"stop": 0, "target": 1, "flat": 2}))[["day", "j0", "j1", "side", "entry", "exit", "kind"]]
    add_trades("RS", with_slippage(rs))
    N = pd.read_csv("checks/candidates/overnight_tick/nights.csv", parse_dates=["date", "sess"]); N = N[N.down & ~N.half & N.rsv.notna() & N.hi25.notna()]
    N = N[((N.rsv < 0) & N.hi25.astype(bool)) | ((N.rsv >= 0) & ~N.hi25.astype(bool))]; dp = pd.Series(np.arange(D), index=dts)
    U["OT"] = daypaths(D, [(int(dp[d]) if d in dp.index else None, a, n) for d, a, n in zip(N.date, N.adv, N.net)])
    sys.argv = ["x", "scratch_data"]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
        lab = FB.add_moc_mes(lab)
    for k, nm in (("CLS", "CLS"), ("MOC_MES", "MOC")):
        Wk = lab.W[k]; Rk = np.zeros_like(Wk); Rk[:, -1] = lab.C[k]; U[nm] = (Wk, Rk)     # lab pieces: realized at the day's end
    names = list(U); yr = dts.year
    unit = lambda nm: (np.floor(250.0 / (RISK[nm] * 2.0))[:, None] if nm in RISK else 1.0)   # contracts per unit per day
    design = np.array([(d >= pd.Timestamp("2018-01-02")) and (d <= pd.Timestamp("2022-11-30")) for d in dts])
    hold = np.array([(d >= pd.Timestamp("2023-01-03")) and (d <= pd.Timestamp("2026-09-01")) for d in dts])
    cap = {}
    for nm in names:
        p1 = np.percentile((U[nm][0] * unit(nm)).min(axis=1)[design & ((U[nm][0] * unit(nm)).min(axis=1) < 0)], 1) if True else 0
        cap[nm] = max(0, int(np.floor(1500.0 / max(1.0, -p1))))
    print("   unit caps (1st-pct worst day <= $1,500):", cap)
    def tot(x):
        Wx = sum(U[nm][0] * unit(nm) * x[nm] for nm in names if x[nm]); Rx = sum(U[nm][1] * unit(nm) * x[nm] for nm in names if x[nm]); return Wx, Rx
    def run(x, mask):
        Wx, Rx = tot(x); res = [evaluation(Wx, Rx, s, D, R150) if mask[s] else None for s in range(D)]
        o = np.array([z[0] if z else "" for z in res]); n_ = np.array([z[1] if z else 0 for z in res]); v = mask & (o != ""); return o, n_, v
    rate = lambda x, m: (lambda o, n_, v: (o == "pass")[v].mean())(*run(x, m))
    CUR = {nm: 0 for nm in names}; CUR.update(VB=20, ONB30=11, MON_BR=5, EOS=5, TWIN=2)   # ONB $2,750 = 11 units; EOS $1,250 = 5 units
    start = {nm: min(CUR[nm], cap[nm]) for nm in names}
    print(f"   current set {CUR}\n   design pass: current {rate(CUR, design):.1%}, clipped to caps {rate(start, design):.1%}", flush=True)
    x = dict(start); best = rate(x, design)
    for step in range(60):
        cands = []
        for nm in names:
            for dlt in (+1, -1):
                y = dict(x); y[nm] += dlt
                if 0 <= y[nm] <= cap[nm]: cands.append((rate(y, design), nm, dlt, y))
        rr, nm, dlt, y = max(cands, key=lambda z: z[0])
        if rr < best + 0.002: break
        x, best = y, rr; print(f"   step {step + 1}: {nm} {dlt:+d} -> design pass {best:.1%}  {{{', '.join(f'{k}: {v}' for k, v in x.items() if v)}}}", flush=True)
    print(f"\n   FINAL eval set: {{{', '.join(f'{k}: {v}' for k, v in x.items() if v)}}}  (risk units = $250 at the stop)")
    allm = (yr >= 2018) & (dts <= pd.Timestamp("2026-09-01"))
    for nm_, m in (("design 2018-22", design), ("HOLDOUT 2023-26", hold), ("all 2018-26", allm)):
        out = {}
        for lab_, z in (("current", CUR), ("new", x)):
            o, n_, v = run(z, m); out[lab_] = (o, v); print(f"   {nm_:<16} {lab_:<8} pass {(o == 'pass')[v].mean():5.1%} fail {(o == 'fail')[v].mean():5.1%} time-out {(o == 'time')[v].mean():4.1%} | median days to pass {np.median(n_[v & (o == 'pass')]):.0f}")
        d_ = ((out["new"][0] == "pass").astype(float) - (out["current"][0] == "pass").astype(float))[out["new"][1] & out["current"][1]]
        rng = np.random.default_rng(1); nb = int(np.ceil(len(d_) / 60)); st = rng.integers(0, len(d_), (2000, nb)); mm = d_[((st[:, :, None] + np.arange(60)) % len(d_)).reshape(2000, -1)[:, :len(d_)]].mean(axis=1)
        print(f"      new - current {d_.mean():+.1%} (band {np.percentile(mm, 5):+.1%} / {np.percentile(mm, 95):+.1%})", flush=True)
    for lab_, z in (("current", CUR), ("new", x)):
        Wx, Rx = tot(z); dl = Rx[:, -1][allm]; wl = Wx.min(axis=1)[allm]
        print(f"   {lab_:<8} daily mean ${dl.mean():,.0f} sd ${dl.std():,.0f} | days with an intraday low < -$2,000: {np.mean(wl < -2000):.1%}, < -$3,000: {np.mean(wl < -3000):.1%}")
