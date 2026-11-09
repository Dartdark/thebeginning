"""Volatile-regime gap-up fade, NQ (user 2026-11-09: 'find a new strategy that gains on VB and ONB stop days'; from analysis/stopday_screen.py:
VB stop days gap up more often (65% vs 55%), have bigger gaps and prior ranges, and come with VIX above its 25-day SMA 57% vs 39%).
PRE-REGISTERED (header committed before the first run; 1 variant). Mechanism: in a volatile market an overnight gap up is fragile; cash
sellers fade it, which is the day a long breakout (VB) fails.
Rule: yesterday's VIX close > its 25-day SMA AND today's 08:31 open >= the prior 15:00 close + 0.25 x ATR15 -> short NQ at the 08:31 open,
stop 0.5 x ATR15, out at the 14:55 close (covers VB's 10:00-14:30 window); CME early-close days skipped; $7.25 + 1 tick per fill.
Checks: $ a trade by period / year; $ per micro on VB / ONB stop days vs other days; random side on the same days (200 runs); the mirror
(gap-DOWN long on high-VIX days, information); calm-VIX gap-ups (information); daily corr with VB / ONB; checker checks/candidates/vol_gap_fade/;
150K evaluation (set + Twin 2) + 2 / 4 MNQ with the stop-day pass detail; funded 150K + 2 MNQ.
  tools/run_stamped.sh analysis/vol_gap_fade_test.py > analysis/outputs/vol_gap_fade_test_output.txt
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc
from build_lab import REPORTS
from combine_levers_test import ONB30
import letf_flow_test as LF
from new_sources_150k import daypaths
import bench150 as BB

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); ts = pd.DatetimeIndex(g.ts); trr = g.trading; days = pd.DatetimeIndex(ts[trr]); atr = g.daily_atr(15)
    vix = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE.sort_index(); hi_s = (vix > vix.rolling(25).mean())
    hi = lambda d: bool(hi_s[hi_s.index < d].iloc[-1]) if (hi_s.index < d).any() else False
    gap = {}
    for i in range(1, len(trr)):
        r, p = trr[i], trr[i - 1]; o, c = g.o[r, jof(831)], g.c[p, jof(1500)]
        if np.isfinite(o) and np.isfinite(c) and np.isfinite(atr[r]): gap[ts[r]] = (o - c) / atr[r]
    gp = pd.Series(gap); gp = gp[gp.index >= "2018-01-01"]; H = pd.Series({d: hi(d) for d in gp.index})
    sets = {"rule: high VIX, gap up >= 0.25 ATR, short": (gp[(gp >= 0.25) & H], -1), "mirror: high VIX, gap down, long (info)": (gp[(gp <= -0.25) & H], 1),
            "calm VIX gap up >= 0.25, short (info)": (gp[(gp >= 0.25) & ~H], -1)}
    kw = dict(t0=830, t1=1455, stop=0.5); out = {}
    stop = {}
    for nm, f in (("VB", REPORTS["VB"][0]), ("ONB", ONB30)):
        t = load_mc(g, f); t["date"] = ts[t.day.values]; stop[nm] = set(t[t.kind == 0].date)
    for nm, (sig, side) in sets.items():
        T = LF.trades(g, sig, lambda d, z, s=side: s, **kw); out[nm] = T
        print(LF.line(T.net, T.date, nm)); print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
        for k in ("VB", "ONB"):
            m = T.date.isin(list(stop[k])); print(f"      on {k} stop days: n {m.sum()} ${T.net[m].mean():.0f} vs other ${T.net[~m].mean():.0f}")
    T = out["rule: high VIX, gap up >= 0.25 ATR, short"]; sig = sets["rule: high VIX, gap up >= 0.25 ATR, short"][0]
    rng = np.random.default_rng(59); pl = []
    for run in range(200):
        sides = {d: int(rng.choice([-1, 1])) for d in sig.index}; Tp = LF.trades(g, sig, lambda d, z: sides[d], **kw); pl += [(run, x) for x in Tp.net]
    pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean()
    print(f"   random side (200 runs): ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${T.net.mean():.0f}; p {np.mean(pm >= T.net.mean()):.3f}", flush=True)
    cd = "checks/candidates/vol_gap_fade"; os.makedirs(cd, exist_ok=True)
    T.assign(date=T.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net", "risk"]].to_csv(f"{cd}/trades.csv", index=False)
    pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": True, "variants": 1}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write("# Volatile-regime gap-up fade, NQ (2026-11-09)\n" + __doc__.split("Rule:")[1].split("Checks:")[0] + "\n")
    ctx = BB.setup(); dts, D = ctx["dts"], ctx["D"]; dp = pd.Series(np.arange(D), index=dts)
    W1, R1 = daypaths(D, [(int(dp[d]) if d in dp.index else None, a, n) for d, a, n in zip(T.date, T.adv, T.net)])
    lab = ctx["lab"]; dd = pd.Series(R1[:, -1], index=dts); span = dts >= "2018-01-01"
    print("   daily corr:", {k: round(dd[span].corr(pd.Series(lab.C[k], index=dts)[span]), 2) for k in ("VB", "ONB_ML2_MC", "TWIN", "EOS", "LDF_MC")}, "\n")
    BB.eval_bench(ctx, {f"+ vol gap fade {n} MNQ": (n * W1, n * R1) for n in (2, 4)})
    print(); BB.funded_bench(ctx, {"+ vol gap fade 2 MNQ": {**BB.BASE_FUNDED, "VGF": 2}}, extra={"VGF": (W1, R1[:, -1])})
