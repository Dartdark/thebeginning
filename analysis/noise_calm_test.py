"""Noise-area longs: size up on calm days / volatility-scaled exits (user 2026-11-08, follow-up of noise_vix_test.py's post hoc lead).
PRE-REGISTERED (header committed before the first run; 2 variants). Base: the personal plan's noise-area 15-min longs (Bridge code, RTH,
longs only, stop 50 / target 25, flat 14:45, early-close flat 11:30), 1 MNQ, $7.25 + 1 tick per NQ fill (/10 per MNQ, + $0.55 a trade).
  A  calm-day sizing: 2 MNQ when yesterday's VIX close <= its 25-day SMA, else 1 MNQ (every trade kept).
  B  volatility-scaled exits: stop = k x the daily ATR(15) known that morning, target = stop / 2; k = 50 / median ATR(15) of 2018-22
     (the design period), so B equals the base at that period's median volatility. 1 MNQ.
Checks: per trade by period and year (B), calm / volatile split (A and B); checker for B (strategy) checks/candidates/noise_volexit/;
personal book 1-year MC return / DD p95 by period (noise-area added as is / A / B; the book file has no noise column);
Monte Carlo at trading size (montecarlo.report). Also (user question, same day): Overnight Tick at 2 MNQ vs 1 MNQ at trading size.
  tools/run_stamped.sh analysis/noise_calm_test.py > analysis/outputs/noise_calm_test_output.txt
"""
import sys, os, json, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import bridge_noise_15m_test as BN
import montecarlo as MC
import bench150 as BB

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = BN.g; atr = g.daily_atr(15); dts = pd.DatetimeIndex(g.ts)
    m22 = np.isin(np.arange(g.D), g.trading) & (dts.year >= 2018) & (dts.year <= 2022) & np.isfinite(atr)
    k = 50.0 / np.median(atr[m22]); print(f"   k = 50 / median ATR15 2018-22 ({np.median(atr[m22]):.0f} pts) = {k:.3f}")
    S = BN.series("rth")
    T0 = BN.run(S, shorts=False, early_flat=True)
    T1 = BN.run(S, shorts=False, early_flat=True, sl_row={int(r): k * atr[r] for r in g.trading if np.isfinite(atr[r])})
    vix = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE.sort_index()
    calm_s = (vix <= vix.rolling(25).mean()).where(vix.rolling(25).count() == 25)
    calm = lambda d: calm_s[calm_s.index < d].iloc[-1] if (calm_s.index < d).any() else np.nan
    tt = lambda x: x.mean() / x.std(ddof=1) * np.sqrt(len(x)) if len(x) > 2 else np.nan
    out = {}
    for nm, T in (("base (stop 50 / target 25)", T0), ("B vol-scaled exits", T1)):
        T = T[T.date >= "2018-01-01"].reset_index(drop=True); T["calm"] = T.date.map(calm); T = T[T.calm.notna()].reset_index(drop=True); T["calm"] = T.calm.astype(bool); out[nm] = T
        a, b = T[T.date < "2023"].net, T[T.date >= "2023"].net
        print(f"   {nm:<28} n {len(T):4d} ${T.net.mean():4.0f} t {tt(T.net):5.2f} | 2018-22 ${a.mean():.0f} (t {tt(a):.1f}) 2023+ ${b.mean():.0f} (t {tt(b):.1f}) | calm ${T[T.calm].net.mean():.0f} volatile ${T[~T.calm].net.mean():.0f} | total ${T.net.sum():,.0f} worst ${T.net.min():,.0f}")
        print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
    T0, T1 = out["base (stop 50 / target 25)"], out["B vol-scaled exits"]
    cd = "checks/candidates/noise_volexit"; os.makedirs(cd, exist_ok=True)
    T1.assign(date=T1.date.dt.strftime("%Y-%m-%d"), risk=None)[["date", "side", "net"]].to_csv(f"{cd}/trades.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": True, "variants": 2}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write(f"# Noise-area longs, volatility-scaled exits (2026-11-08)\nBridge noise-area 15-min longs on the NQ RTH chart (band from the 08:30 open / prior close, flat 14:45, early-close flat 11:30); stop = {k:.3f} x daily ATR(15), target = stop / 2. $7.25 + 1 tick per fill.\n")
    dmn = lambda T, w=1.0: (T.net / 10 - 0.55).mul(w).groupby(T.date).sum()
    wA = np.where(T0.calm, 2.0, 1.0)
    D = {"as is": dmn(T0), "A calm 2 / else 1": dmn(T0, wA), "B vol exits": dmn(T1)}
    print("\n   Personal book 1-year MC return / DD p95 (noise-area added):")
    BB.personal({f"+ {k_}": v for k_, v in D.items()})
    print("\n   Monte Carlo at trading size (noise-area alone, MNQ):")
    days = pd.bdate_range("2018-01-02", T0.date.max())
    for nm, T, w in (("as is 1 MNQ", T0, np.ones(len(T0))), ("A calm 2 / else 1", T0, wA), ("B vol exits 1 MNQ", T1, np.ones(len(T1)))):
        x = (T.net / 10 - 0.55) * w; print(MC.report(x.values * 10, (x.groupby(T.date).sum()).reindex(days, fill_value=0.0).values * 10, size=0.1, label=nm))
    print("\n   Overnight Tick at trading size (user question): 1 MNQ vs 2 MNQ, per-night trades to 2026-07-07")
    N = pd.read_csv("checks/candidates/overnight_tick/nights.csv", parse_dates=["date", "sess"])
    sig = N.down & ~N.half & N.rsv.notna() & N.hi25.notna() & (((N.rsv < 0) & N.hi25.astype(bool)) | ((N.rsv >= 0) & ~N.hi25.astype(bool)))
    t = N[sig]; dd = t.groupby("date").net.sum().reindex(pd.bdate_range(t.date.min(), t.date.max()), fill_value=0.0)
    for sz in (0.1, 0.2): print(MC.report(t.net.values, dd.values, size=sz, label=f"OT {int(sz * 10)} MNQ"))
    print(f"   OT worst night per MNQ ${t.net.min() / 10:,.0f}, worst intranight ${t.adv.min() / 10:,.0f}")
