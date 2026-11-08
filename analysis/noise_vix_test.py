"""Noise-area longs filtered by the VIX regime (user 2026-11-08, batch of 5, test 4). PRE-REGISTERED (header committed before the
first run; 1 variant, filter). Base: the personal plan's noise-area 15-min longs (The Bridge's code, RTH-anchored, longs only, stop 50 /
target 25, flat 14:45, early-close flat 11:30; analysis/bridge_noise_15m_test.run(shorts=False, early_flat=True)), $7.25 + 1 tick per
NQ market / stop fill. Filter (second mechanism: intraday momentum is stronger when volatility is high): trade the day only when the
previous trading day's VIX close > the 25-day SMA of VIX closes (known before the open; the same VIX regime as Overnight Tick).
Checks: kept vs skipped per trade by period and by year; checker (kind filter, label shuffle within years) checks/candidates/noise_vix/;
personal book (noise-area 1 MNQ as is vs filtered; the book file has no noise column, so both are added to it).
  tools/run_stamped.sh analysis/noise_vix_test.py > analysis/outputs/noise_vix_test_output.txt
"""
import sys, os, json, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import bridge_noise_15m_test as BN
import bench150 as BB

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    T = BN.run(BN.series("rth"), shorts=False, early_flat=True); T = T[T.date >= "2018-01-01"].reset_index(drop=True)
    vix = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE.sort_index()
    hi = (vix > vix.rolling(25).mean()).where(vix.rolling(25).count() == 25)   # regime at each VIX close
    T["kept"] = T.date.map(lambda d: hi[hi.index < d].iloc[-1] if (hi.index < d).any() else np.nan)
    T = T[T.kept.notna()].reset_index(drop=True); T["kept"] = T.kept.astype(bool).astype(int)
    # 'index < d': the last VIX close strictly before the trade date (yesterday's close), known before the open
    tt = lambda x: x.mean() / x.std(ddof=1) * np.sqrt(len(x)) if len(x) > 2 else np.nan
    for nm, m in (("all (as planned)", np.ones(len(T), bool)), ("kept: VIX > SMA25", T.kept == 1), ("skipped: VIX <= SMA25", T.kept == 0)):
        x = T[m]; a, b = x[x.date < "2023"].net, x[x.date >= "2023"].net
        print(f"   {nm:<24} n {len(x):4d} ${x.net.mean():5.0f} t {tt(x.net):5.2f} | 2018-22 ${a.mean():.0f} (t {tt(a):.1f}) 2023+ ${b.mean():.0f} (t {tt(b):.1f}) | total ${x.net.sum():,.0f}")
    by = T.groupby([T.date.dt.year, "kept"]).net.mean().unstack().round(0); print("   $ a trade by year (0 skipped / 1 kept):", by.to_dict(orient="index"))
    cd = "checks/candidates/noise_vix"; os.makedirs(cd, exist_ok=True)
    T.assign(date=T.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net", "kept"]].to_csv(f"{cd}/trades.csv", index=False)
    json.dump({"kind": "filter", "pre_registered": True, "variants": 1}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write("# Noise-area longs, VIX regime filter (2026-11-08)\nBase: Bridge noise-area 15-min longs on the NQ RTH chart (band from the 08:30 open / prior close, stop 50 / target 25, flat 14:45, early-close flat 11:30), $7.25 + 1 tick per fill. Filter: trade only when the previous VIX close > its 25-day SMA.\n")
    print("\n   Personal book 1-year MC return / DD p95 (noise-area 1 MNQ added both ways):")
    d0 = (T.groupby("date").net.sum() / 10 - 0.55 * T.groupby("date").size()); d1 = (T[T.kept == 1].groupby("date").net.sum() / 10 - 0.55 * T[T.kept == 1].groupby("date").size())
    BB.personal({"+ noise-area as is": d0, "+ noise-area VIX-filtered": d1})
