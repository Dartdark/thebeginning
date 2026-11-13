"""Progress across the books, before (as of 2026-11-07) vs now (2026-11-09 decisions), same engines, same data (user 2026-11-09:
'calculate the overall earnings in all books compared to last time'). Information only.
  150K evaluation (pass rate, 21-day windows, corrected trailing engine, starts 2018 -> 2026-09):
    before = VB 20, ONB ADX30 $2,750, Bridge Monday 5, EOS $1,250; + Twin 2 MNQ (11/08); now = + VB 15 / Dual Thrust 2 MNQ (11/09).
  Funded 150K (600 paired 2-year histories, cushion sizing): before = plan x 1.5; now = plan x 1.5 + Twin 2 MNQ. The 11/08 per-stop
    cushion cap was benched on the 50K plan only (blown 8.1 -> 2.3%, payouts same; cushion_cap_funded_vb2_output.txt): quoted, not rerun.
  Personal (1-year block bootstrap of the daily book, median year / p95 drawdown, from personal_P.pkl, data to 2026-10-09): before =
    the book with Overnight Tick at 1 MNQ; now = OT at 2 MNQ + ZT continuation 1 MNQ + FINRA longs 1 MNQ. Shown for the core book
    (without the forward-log pieces FC2B / Kusho / S47 / S30) and the full book (every piece at 1 micro).
  tools/run_stamped.sh analysis/progress_books.py > analysis/outputs/progress_books_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from plan_150k_test import evaluation, R150
from donchian_lwti_test import series
import dual_thrust_bench as DTB
import montecarlo as MC
import zt_ablation as A
import bench150 as BB

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    ctx = BB.setup(base="legacy"); g, trr, D, dts, yr = ctx["g"], ctx["trr"], ctx["D"], ctx["dts"], ctx["yr"]
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("DT", DTB.dt_trades(g))): w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    ok = (yr >= 2018) & (dts <= pd.Timestamp("2026-09-01"))
    V = {"before 11/08 (no Twin)": (ctx["Wb"] - 2 * ctx["Wt"], ctx["Rb"] - 2 * ctx["Rt"]), "+ Twin 2 (11/08)": (ctx["Wb"], ctx["Rb"]),
         "now: + VB 15 / DT 2 (11/09)": (ctx["Wb"] - 5 * P["VB"][0] + 2 * P["DT"][0], ctx["Rb"] - 5 * P["VB"][1] + 2 * P["DT"][1])}
    print("\n1. 150K evaluation (pass / fail / time-out, all starts 2018 -> 2026-09; recent = starts 2025+):")
    out = {}
    for nm, (W, R) in V.items():
        res = [evaluation(W, R, s, D, R150) if ok[s] else None for s in range(D)]; o = np.array([x[0] if x else "" for x in res]); v = o != ""
        rec = v & (dts >= "2025-01-01"); out[nm] = (o, v)
        print(f"   {nm:<30} pass {(o == 'pass')[v].mean():5.1%} fail {(o == 'fail')[v].mean():5.1%} time-out {(o == 'time')[v].mean():4.1%} | recent pass {(o == 'pass')[rec].mean():5.1%}"
              f" | fee per passed account ${249 / max(1e-9, (o == 'pass')[v].mean()):,.0f}", flush=True)
    print("\n2. Funded 150K (2-year payouts per account):")
    BB.funded_bench(ctx, {"before: plan x 1.5 (no Twin)": {k: v for k, v in BB.BASE_FUNDED.items() if k != "TWIN"}})
    print("   (50K per-stop cushion cap, 11/08, quoted: 2-year payouts $11,778 -> $11,747, blown 8.1% -> 2.3%)")
    print("\n3. Personal account (1-year bootstrap, 2,000 paths, blocks of 20 days):")
    Pp = pd.read_pickle("scratch_data/personal_P.pkl"); idx = Pp.index
    s = series(g, 15); T = A.run(g, s, A.zser(s), entry=1.25); zt = (T.net / 10 - 0.55).groupby(T.date).sum().reindex(idx, fill_value=0.0)
    F = pd.read_csv("checks/candidates/finra_longs/mc_trades.csv", parse_dates=["date"]); fin = (F.net_rc / 10 - 0.55).groupby(F.date).sum().reindex(idx, fill_value=0.0)
    mc = lambda x: MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1)
    for lab, cols in (("core book (no forward-log pieces)", [c for c in Pp.columns if c not in ("FC2B", "Kusho", "S47", "S30")]), ("full book (every piece)", list(Pp.columns))):
        b0 = Pp[cols].sum(axis=1); steps = [("before (OT 1 MNQ)", b0), ("+ OT 2nd MNQ (11/08)", b0 + Pp.OvernightTick), ("+ ZT 1 MNQ (11/09)", b0 + Pp.OvernightTick + zt),
                                           ("now: + FINRA 1 MNQ (11/09)", b0 + Pp.OvernightTick + zt + fin)]
        print(f"   {lab}:")
        for nm, x in steps:
            r = mc(x); print(f"      {nm:<28} backtest ${x.sum() / (len(x) / 252):>7,.0f} a year | MC median year ${r['pnl_p50']:>7,.0f} p5 ${r['pnl_p5']:>7,.0f} | DD p95 ${r['dd_p95']:>6,.0f} | return/DD {r['pnl_p50'] / r['dd_p95']:.2f}", flush=True)
    print(f"   ZT and FINRA alone per MNQ: ${zt.sum() / (len(idx) / 252):,.0f} / ${fin.sum() / (len(idx) / 252):,.0f} a year; personal data end {idx.max().date()}")
