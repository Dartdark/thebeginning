"""What the WATCHLIST #38 versions would add together IF the 2009-2017 test validated them (user 2026-11-10). POST HOC, information.
Personal: current plan = personal_P + Overnight Tick at 2 MNQ + CL fade 2 MCL on high-OVX weekends (adopted 2026-11-10); new = the
same with OT 'skip stretched S&P + 3 MNQ on any fear', Swing Target '2x on Nasdaq-fear spikes', PaperTrend '2x below the S&P median'.
Funded 150K: only Overnight Tick is in that plan (2 MNQ, FUNDED_PLAN): OT 2 flat vs the OT version.
  tools/run_stamped.sh analysis/sweep_combined_value.py > analysis/outputs/sweep_combined_value_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC, bench150 as BB
from new_data_screen import RULES, prior
from data_sweep import series
from new_sources_150k import daypaths

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    P = pd.read_pickle("scratch_data/personal_P.pkl"); idx = P.index; S = series()
    def masks(dates):
        reg = lambda nm, rule: pd.Series(prior(S[nm], dates, RULES[rule]) == 1, index=dates)
        fa = reg("VIX9D/VIX", "above_median") | reg("VXN", "above_median") | reg("GVZ", "above_median") | reg("VIX9D", "above_median")
        return reg("SPX", "z_high"), fa, reg("VXN-VIX", "z_high"), reg("SPX", "above_median"), reg("OVX", "above_median")
    sz, fa, spk, med, ovx = masks(idx)
    otm = np.where(sz, 0.0, np.where(fa, 3.0, 2.0)); stm = np.where(spk, 2.0, 1.0); ptm = np.where(med, 1.0, 2.0)
    cl = P.CLSundayFade_perMCL; clm = np.where(ovx, 2.0, 1.0)
    f = lambda x: (lambda r: (r["pnl_p50"], r["pnl_p5"], r["dd_p95"], r["pnl_p50"] / r["dd_p95"]))(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1))
    yrs = len(idx) / 252
    for lab, cols in (("FULL book", list(P.columns)), ("CORE book", [c for c in P.columns if c not in ("FC2B", "Kusho", "S47", "S30")])):
        cur = P[cols].sum(axis=1) + P.OvernightTick - cl + cl * clm
        new = cur - 2 * P.OvernightTick + P.OvernightTick * otm - P.SwingTarget + P.SwingTarget * stm - P.PaperTrend + P.PaperTrend * ptm
        print(f"\n   {lab}: backtest $ a year current ${cur.sum() / yrs:,.0f} -> new ${new.sum() / yrs:,.0f} ({(new - cur).sum() / yrs:+,.0f})")
        for per, m in (("2018-26", np.ones(len(idx), bool)), ("2018-22", idx.year <= 2022), ("2023+", idx.year >= 2023)):
            a, b = f(cur[m]), f(new[m])
            print(f"      {per}: median year ${a[0]:,.0f} -> ${b[0]:,.0f} ({b[0] - a[0]:+,.0f}) | bad year (p5) ${a[1]:,.0f} -> ${b[1]:,.0f} | DD p95 ${a[2]:,.0f} -> ${b[2]:,.0f} | return/DD {a[3]:.2f} -> {b[3]:.2f}")
        eq = lambda x: (x.cumsum().cummax() - x.cumsum()).max()
        print(f"      historical max DD ${eq(cur):,.0f} -> ${eq(new):,.0f}")
    print("\n   Funded 150K (Overnight Tick is the only one of the three in it):")
    ctx = BB.setup(); D, dts = ctx["D"], ctx["dts"]; dp = pd.Series(np.arange(D), index=dts)
    N = pd.read_csv("checks/candidates/overnight_tick/nights.csv", parse_dates=["date", "sess"]); N = N[N.down & ~N.half & N.rsv.notna() & N.hi25.notna()]
    N = N[((N.rsv < 0) & N.hi25.astype(bool)) | ((N.rsv >= 0) & ~N.hi25.astype(bool))]
    W, R = daypaths(D, [(int(dp[d]) if d in dp.index else None, a, n) for d, a, n in zip(N.date, N.adv, N.net)])
    sz2, fa2, _, _, _ = masks(dts); m = np.where(sz2, 0.0, np.where(fa2, 3.0, 2.0))
    BB.funded_bench(ctx, {"+ OT 2 flat (plan)": {**BB.BASE_FUNDED, "OT": 2}, "+ OT skip stretched / 3 on fear": {**BB.BASE_FUNDED, "OT_V": 1}},
                    extra={"OT": (W, R[:, -1]), "OT_V": (W * m[:, None], R[:, -1] * m)})
