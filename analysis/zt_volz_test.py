"""Vol-normalised Z (user's MultiCharts paste 2026-11-09: 'ZT' indicator + strategy). PRE-REGISTERED (header committed before the
first run). ZT = (Close - XAverage(Close, 32)) / (Close x StandardDev(Close / Close[1] - 1, 32, population) x sqrt(32)).
Strategy as coded: flat and ZT >= +2 -> long next bar at market (SignalMode 1 = continuation, the default; mirror short at <= -2);
SignalMode 0 = fade (long at <= -2, short at >= +2). Exit next bar at market when |ZT| <= 0.25, or ZT past -/+4 against the
position, or BarsSinceEntry >= 8; TrendMode 0 (none), no time filter = trades 24 h (not Apex-legal). Bar size not given: 5 / 15 /
30 / 60 minutes, NQ continuous 24 h series (gaps included, as on a chart), signals from 2018. Per NQ after $7.25 + 1 tick per fill.
ITEMS (8): {continuation, fade} x {5, 15, 30, 60 min}, Apex version = the paste's own time filter UseTimeFilter, StartTime 0835,
EndTime 1445 (entries on bars closing 08:35-14:45 CT; a bar closing after 14:45 -> out at the next open, <= 15:00). Bar t >=
metrics.t_threshold(8). Context (not items): the same 8 as coded (24 h); TrendMode 1 / 2 on the best Apex item.
Per item: trades, $ a trade, t, PF, years positive, 2018-22 vs 2023-26, longs / shorts separately; daily Sharpe / Sortino /
Calmar / Ulcer and 2023+ bootstrap Sharpe band. Best Apex item by t (selection noted): random-side placebo (200 runs); if its t >= 2
and 2023+ > 0: 150K evaluation + 2 MNQ, funded 150K x 1.5 + Twin 2 + 2 MNQ, personal + 1 MNQ (add, and replace Dual Thrust as the
overlapping intraday momentum piece). Stop rule: if no Apex item has t >= 2, the benches are skipped.
  tools/run_stamped.sh analysis/zt_volz_test.py > analysis/outputs/zt_volz_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from donchian_lwti_test import series
from metrics import perf, t_threshold
from resampling import bootstrap

PV, TICK, COST = 20.0, 0.25, 7.25


def zt(C, mean_len=32, vol_len=32, trend_len=64):
    s = pd.Series(C); ema = s.ewm(alpha=2 / (mean_len + 1), adjust=False).mean()
    rv = (s / s.shift(1) - 1).rolling(vol_len).std(ddof=0); pvol = s * rv * np.sqrt(mean_len)
    z = ((s - ema) / pvol).where(pvol > 0, 0.0)
    tr = s.ewm(alpha=2 / (trend_len + 1), adjust=False).mean()
    return z.to_numpy(), (s > tr).to_numpy(), (s < tr).to_numpy()


def run(g, s, z, up, dn, mode=1, entry=2.0, exit_=0.25, stop=4.0, hold=8, trend=0, window=None, rng=None):
    O, H, L, C, row, hm = s["o"], s["h"], s["l"], s["c"], s["row"], s["hhmm"]
    ts = pd.DatetimeIndex(g.ts); y0 = np.searchsorted(row, np.flatnonzero(ts >= "2018-01-01")[0])
    n = len(C); out = []; pos = 0; pend = 0; xp = False; e = 0.0; i0 = 0; adv = 0.0
    inwin = np.ones(n, bool) if window is None else (hm >= window[0]) & (hm <= window[1])
    for i in range(max(y0, 70), n):
        if pend:                                                        # entry fill at this bar's open
            pos = pend; e = O[i] + pos * TICK; i0 = i; adv = 0.0; pend = 0
        elif xp:                                                        # exit fill at this bar's open
            px = O[i] - pos * TICK; out.append((ts[row[i0]], row[i0], row[i], pos, (px - e) * pos * PV - COST, min(adv, (px - e) * pos) * PV - COST)); pos = 0; xp = False
        if pos:
            adv = min(adv, ((L[i] if pos > 0 else H[i]) - e) * pos)
            bse = i - i0
            if abs(z[i]) <= exit_ or z[i] * pos <= -stop or bse >= hold or (window is not None and not inwin[i]): xp = True
            continue
        if not inwin[i]: continue
        al = trend == 0 or (trend == 1 and up[i]) or (trend == 2 and not up[i])
        as_ = trend == 0 or (trend == 1 and dn[i]) or (trend == 2 and not dn[i])
        sig = 0
        if mode == 0:
            if z[i] <= -entry and al: sig = 1
            elif z[i] >= entry and as_: sig = -1
        else:
            if z[i] >= entry and al: sig = 1
            elif z[i] <= -entry and as_: sig = -1
        if sig: pend = sig if rng is None else int(rng.choice([-1, 1]))
    return pd.DataFrame(out, columns=["date", "row0", "row1", "side", "net", "adv"])


def line(T, nm):
    if len(T) < 5: return f"   {nm:<34} n={len(T)}"
    x = T.net; t = x.mean() / x.std() * np.sqrt(len(x)); gl = -x[x < 0].sum(); by = x.groupby(T.date.dt.year).sum()
    a, b = x[T.date < "2023"], x[T.date >= "2023"]; L_, S_ = x[T.side > 0], x[T.side < 0]
    tl = lambda v: v.mean() / v.std() * np.sqrt(len(v)) if len(v) > 2 else np.nan
    return (f"   {nm:<34} n {len(x):5d} ${x.mean():6.1f} t {t:5.2f} PF {x[x > 0].sum() / gl:4.2f} yrs+ {(by > 0).sum()}/{len(by)} | 18-22 ${a.mean():.0f} 23+ ${b.mean():.0f}"
            f" | L ${L_.mean():.0f} (t {tl(L_):.1f}) S ${S_.mean():.0f} (t {tl(S_):.1f}) | overnight {np.mean(T.row0 != T.row1):.0%}"), t


def daily(T, g):
    d = T.groupby(T.date).net.sum(); days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days >= "2018-01-01"]
    return d.reindex(days, fill_value=0.0)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); APEX = (835, 1445); res = {}
    print(f"   bar t for 8 items: {t_threshold(8):.2f}")
    for k in (5, 15, 30, 60):
        s = series(g, k); z, up, dn = zt(s["c"]); S = (s, z, up, dn)
        print(f"\n {k}-min bars: |ZT| >= 2 on {np.mean(np.abs(z[70:]) >= 2):.1%} of bars")
        for mode, mn in ((1, "continuation"), (0, "fade")):
            T = run(g, *S, mode=mode); print(line(T, f"{mn}, as coded 24 h")[0])
            Ta = run(g, *S, mode=mode, window=APEX); ln, t = line(Ta, f"ITEM {mn}, Apex 08:35-14:45"); print(ln, flush=True)
            res[(k, mn)] = (t, Ta, S, mode)
    (kb, mb), (tb, Tb, Sb, modeb) = max(res.items(), key=lambda kv: kv[1][0])
    print(f"\n Best Apex item by t: {kb}-min {mb} (t {tb:.2f}; picked after seeing all 8)")
    d = daily(Tb, g); P, H = perf(d), perf(d[d.index >= "2023"]); b = bootstrap(d[d.index >= "2023"].values, n=2000, block=10).loc["sharpe"]
    print(f"   daily Sharpe {P['sharpe']:.2f} Sortino {P['sortino']:.2f} PF {P['profit_factor']:.2f} Calmar {P['calmar']:.2f} Ulcer {P['ulcer']:.1f} DD ${P['max_dd']:,.0f} | 2023+ Sharpe {H['sharpe']:.2f} (band {b.p5:.2f} / {b.p95:.2f})")
    print(f"   by year $: {Tb.groupby(Tb.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
    for tm, nm in ((1, "TrendMode 1 (with the 64-EMA)"), (2, "TrendMode 2 (against it)")):
        print(line(run(g, *Sb, mode=modeb, window=APEX, trend=tm), f"context: {nm}")[0])
    rng = np.random.default_rng(23); pm = np.array([run(g, *Sb, mode=modeb, window=APEX, rng=rng).net.mean() for _ in range(200)])
    print(f"   random side (200 runs): ${pm.mean():.1f}, 95th ${np.percentile(pm, 95):.1f}; real ${Tb.net.mean():.1f}; p {np.mean(pm >= Tb.net.mean()):.3f}", flush=True)
    if not (tb >= 2 and Tb[Tb.date >= "2023"].net.mean() > 0):
        print("\n   Stop rule: best Apex item t < 2 or 2023+ <= 0 -> benches skipped."); sys.exit()
    import bench150 as BB
    from new_sources_150k import daypaths
    ctx = BB.setup(); dts, D = ctx["dts"], ctx["D"]; dpos = pd.Series(np.arange(D), index=dts)
    W1, R1 = daypaths(D, [(int(dpos[x]) if x in dpos.index else None, a, n_) for x, a, n_ in zip(Tb.date, Tb.adv, Tb.net)])
    BB.eval_bench(ctx, {"+ ZT 2 MNQ": (2 * W1, 2 * R1)}); print()
    BB.funded_bench(ctx, {"+ ZT 2 MNQ": {**BB.BASE_FUNDED, "ZT": 2}}, extra={"ZT": (W1, R1[:, -1])}); print()
    pm1 = (Tb.net / 10 - 0.55).groupby(Tb.date).sum()
    BB.personal({"+ ZT 1 MNQ": pm1}); print("   replacing Dual Thrust:"); BB.personal({"ZT 1 for DT": pm1}, drop=("DualThrust",))
