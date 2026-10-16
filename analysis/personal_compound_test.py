"""Personal account at full size and compounding (user, 2026-10-16). The plan without Apex rules: all 8 strategies, daily
P&L per 1 NQ (CL fade 1 CL) 2018-2026 (analysis/personal_account_test.py: $101k a year, max DD $24k). Sizing rule: one
'unit' = the whole plan at 1/10 NQ (MNQ) per $10,000 of equity (= 1 NQ per $100k, max DD ~24% of the account), re-set each
day from the account balance; whole units only. Paths: 20-trading-day block bootstrap of the 2018-26 days (5,000 paths),
5 years. Scenarios: start $10k or $100k; backtest edge or 75% of it (each day's P&L minus 25% of the average day); with or
without Apex payouts added ($5k a month from month 4, a conservative slice of the projected 20-account income).
Costs as in the backtest ($7.25 + 1 tick a fill per NQ); no taxes; no capacity limit (see the note in the output).
  python3 analysis/personal_compound_test.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    names = ["VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC", "MON_BR_MC", "CLS"]
    d = pd.Series(sum(lab.C[k] for k in names) * 10, index=dates); d = d[d.index >= "2018-01-01"].to_numpy()   # $ per 1 NQ set
    unit = d / 10.0                                                                                             # $ per 1/10 set
    rng = np.random.default_rng(7); N, Y, B = 5000, 5, 20; T = 252 * Y
    nb = len(unit) // B
    idx = np.concatenate([np.arange(b * B, b * B + B) for b in range(nb)]).reshape(nb, B)
    paths = idx[rng.integers(0, nb, (N, T // B + 1))].reshape(N, -1)[:, :T]
    for edge in (1.0, 0.75):
        u = unit - (1 - edge) * unit.mean()
        print(f"\n=== {'backtest edge' if edge == 1 else '75% of the edge'} (one 1/10-NQ unit earns ${u.mean() * 252:,.0f} a year on average)")
        for start, monthly in ((10_000, 0), (10_000, 5_000), (100_000, 0)):
            eq = np.full(N, float(start)); peak = eq.copy(); mdd = np.zeros(N); snap = {}
            for t in range(T):
                if monthly and t >= 63 and t % 21 == 0: eq += monthly
                units = np.maximum(np.floor(eq / 10_000), 1)
                eq = eq + units * u[paths[:, t]]
                peak = np.maximum(peak, eq); mdd = np.maximum(mdd, 1 - eq / peak)
                if (t + 1) % 252 == 0: snap[(t + 1) // 252] = eq.copy()
            lbl = f"start ${start:,}" + (f" + ${monthly:,}/month from Apex" if monthly else "")
            print(f"  {lbl}")
            for yv in (1, 2, 3, 5):
                e = snap[yv]
                print(f"     year {yv}: median ${np.median(e):>13,.0f}   10th pct ${np.percentile(e, 10):>13,.0f}   90th pct ${np.percentile(e, 90):>13,.0f}"
                      f"   size then ~{np.median(np.floor(e / 10_000)) / 10:,.1f} NQ per strategy")
            print(f"     worst peak-to-trough drawdown over 5 years: median {np.median(mdd):.0%}, 90th pct {np.percentile(mdd, 90):.0%}; "
                  f"accounts below start at year 1: {np.mean(snap[1] < start):.0%}")
