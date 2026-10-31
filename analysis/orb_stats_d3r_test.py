"""ORB Statistics [Dots3Red] (TradingView indicator, user upload 2026-10-29) on NQ: 30-min opening range from the 08:30 CT
open, first 1-min close beyond it (to 15:00), target 1x range beyond the side, stop opposite side (or midpoint), else flat
15:15. Indicator's hit rates + the trade's net P&L per NQ ($7.25 + 1 tick on entry and on stop / time exits).
  python3 analysis/orb_stats_d3r_test.py
"""
import glob, numpy as np, pandas as pd
d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/NQ_1min_20[12]*.csv")) if "_ON_" not in f])
d = d[(d.date >= 20180101)]
res = []
for stop_mode in ("opposite", "mid"):
    for day, g in d.groupby("date"):
        g = g[(g.time > 830) & (g.time <= 1515)]
        orb = g[g.time <= 900]
        if len(orb) < 25: continue
        hi, lo = orb.high.max(), orb.low.min(); rng = hi - lo
        if rng <= 0: continue
        rest = g[(g.time > 900) & (g.time <= 1500)]
        br = rest[(rest.close > hi) | (rest.close < lo)]
        if br.empty: res.append(dict(stop=stop_mode, day=day, side=0)); continue
        e = br.iloc[0]; side = 1 if e.close > hi else -1; px = e.close
        tgt = (hi + rng) if side > 0 else (lo - rng)
        stp = (lo if side > 0 else hi) if stop_mode == "opposite" else (hi + lo) / 2
        after = g[g.time > e.time]; out, ex = "time", after.close.iloc[-1] if len(after) else px
        for r in after.itertuples():
            hs = r.low <= stp if side > 0 else r.high >= stp
            ht = r.high >= tgt if side > 0 else r.low <= tgt
            if hs: out, ex = "stop", stp; break
            if ht: out, ex = "target", tgt; break
        slip = 0.25 * (1 + (out != "target"))
        pnl = ((ex - px) * side - slip) * 20 - 7.25
        res.append(dict(stop=stop_mode, day=day, side=side, out=out, pnl=pnl, rng=rng))
r = pd.DataFrame(res); r["yr"] = r.day // 10000
for sm, g in r.groupby("stop"):
    t = g[g.side != 0]
    print(f"\n== stop {sm}: days {len(g)}, no-breakout {np.mean(g.side == 0):.0%}, trades {len(t)}")
    for s, h in t.groupby("side"):
        print(f"  {'long' if s > 0 else 'short'}: n {len(h)}, target {np.mean(h.out == 'target'):.0%}, stop {np.mean(h.out == 'stop'):.0%}, "
              f"time {np.mean(h.out == 'time'):.0%}, net ${h.pnl.mean():.0f}/NQ, t {h.pnl.mean() / h.pnl.std() * np.sqrt(len(h)):.1f}")
    print(f"  all: net ${t.pnl.mean():.0f}/NQ, t {t.pnl.mean() / t.pnl.std() * np.sqrt(len(t)):.1f}; 2023+ ${t[t.yr >= 2023].pnl.mean():.0f}")
    print("  by year:", {y: round(h.pnl.sum() / 1000, 1) for y, h in t.groupby('yr')}, "$k/NQ")
