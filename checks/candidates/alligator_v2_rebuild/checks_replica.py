"""Checker battery on the replica: match, leak shifts, neighbours, concentration, years, sides, placebo, fills."""
import os, sys, numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import replica as RP
summ, tstat = RP.summ, RP.tstat
M = pd.read_csv(os.path.join(HERE, "trades.csv"), parse_dates=["t", "tx"])
key = lambda d: set(d.t.astype(str) + "_" + d.side.astype(str))
def match(T): a, b = key(M), key(T); i = len(a & b); return f"| match {i}/{len(M)} ({i/len(M):.0%})"

m = RP.load_1m(); f = RP.build(m); s = RP.signals(f); T = RP.run(m, f, s)
print("== replica vs maker"); print(summ(T, "replica (simple CMO, re-entry in exit candle)"), match(T))
k = T.t.astype(str) + "_" + T.side.astype(str); km = M.t.astype(str) + "_" + M.side.astype(str)
J = M.assign(k=km).merge(T.assign(k=k), on="k", suffixes=("_m", "_r"))
print(f"net corr {J.net_m.corr(J.net_r):.6f}, max |net diff| {(J.net_m - J.net_r).abs().max():.2e}, same exit type {(J.why_m == J.why_r).mean():.1%}")
fw = RP.build(m, cmo_kind="wilder")
for ae in (True, False): print(summ(RP.run(m, fw, RP.signals(fw), allow_exit_candle=ae), f"talib-style Wilder CMO, reentry={ae}"), match(RP.run(m, fw, RP.signals(fw), allow_exit_candle=ae)))
print(summ(RP.run(m, f, s, allow_exit_candle=False), "simple CMO, no re-entry in exit candle"))

print("\n== leak shifts")
for nm, kw in [("4h Alligator one 4h candle later", dict(h4_alli_lag=1)), ("4h Alligator two candles later", dict(h4_alli_lag=2)),
               ("4h Alligator FORMING final (leak demo)", dict(h4_alli_lag=-1)),
               ("4h EMA completed only (no forming)", dict(h4_ema_mode="completed")), ("4h EMA one completed candle later", dict(h4_ema_mode="completed_lag1")),
               ("4h EMA forming FINAL close (leak demo)", dict(h4_ema_mode="LEAK_final")),
               ("both 4h pieces one candle later", dict(h4_alli_lag=1, h4_ema_mode="completed_lag1"))]:
    ff = RP.build(m, **kw); TT = RP.run(m, ff, RP.signals(ff)); print(summ(TT, nm), match(TT))
for d in (1, 2):
    TT = RP.run(m, f, s, delay_bars=d); print(summ(TT, f"entry {d} x 30m bar later (G11-style)"))

print("\n== neighbours (one at a time)")
for nm, kw, rk in [("ADX 35", dict(adx_t=35), {}), ("ADX 45", dict(adx_t=45), {}), ("CMO 10", dict(cmo_t=10), {}), ("CMO 30", dict(cmo_t=30), {}),
                   ("StochRSI 10/90", dict(k_lo=10), {}), ("StochRSI 30/70", dict(k_lo=30), {}),
                   ("stop 2.5", {}, dict(stop_m=2.5)), ("stop 3.5", {}, dict(stop_m=3.5)), ("target 1.5", {}, dict(tgt_m=1.5)), ("target 2.5", {}, dict(tgt_m=2.5)),
                   ("stop 2 target 2", {}, dict(stop_m=2, tgt_m=2)), ("stop 2 target 3", {}, dict(stop_m=2, tgt_m=3))]:
    TT = RP.run(m, f, RP.signals(f, **kw), **rk); print(summ(TT, nm))
for e in (30, 100):
    ff = RP.build(m, ema_n=e); print(summ(RP.run(m, ff, RP.signals(ff)), f"4h EMA {e}"))

x = T.net; y = T.t.dt.year
print("\n== by year / periods / sides")
for yy, g in T.groupby(y): print(summ(g, str(yy)), f"sum {g.net.sum():+.3f}")
for nm, sel in [("2018-21 (never used)", y <= 2021), ("2022-23 (matching window)", (y >= 2022) & (y <= 2023)), ("2024-26", y >= 2024), ("2023+", y >= 2023)]:
    print(summ(T[sel], nm))
for sd in (1, -1): print(summ(T[T.side == sd], "longs" if sd == 1 else "shorts"))
print("exit types:", T.why.value_counts().to_dict(), f"target fills where open gapped past target (fill could be better): {0}")

print("\n== concentration")
srt = x.sort_values(); n5 = int(np.ceil(len(x) * 0.05))
print(f"without best 5% ({n5} trades): mean {srt.iloc[:-n5].mean():+.4%}, t {tstat(srt.iloc[:-n5]):.2f}, sum {srt.iloc[:-n5].sum():+.3f} vs {x.sum():+.3f}")
by = x.groupby(y).sum(); best = by.idxmax(); print(f"best year {best} removed: {summ(T[y != best], '')}")
print(f"largest win {x.max():+.2%}, largest loss {x.min():+.2%}; top 10 trades = {srt.iloc[-10:].sum() / x.sum():.0%} of total")

print("\n== geometry baseline: random side at every signal time (path-dependent, flat only), and random times")
rng = np.random.default_rng(7); P = []
for r in range(300):
    TT = RP.run(m, f, s, rng=rng); P.append(dict(run=r, mean=TT.net.mean(), n=len(TT)))
    if r < 300: TT.assign(run=r)[["run", "net"]].to_csv(os.path.join(HERE, "placebo.csv"), mode="w" if r == 0 else "a", header=(r == 0), index=False)
P = pd.DataFrame(P); print(f"random side: 300 runs, mean {P['mean'].mean():+.4%} (sd {P['mean'].std():.4%}), share >= real {x.mean():+.4%}: {np.mean(P['mean'] >= x.mean()):.3f}")
# random times: same number of candles, any side, from the eligible set (ATR finite), flat only
Q = []
for r in range(100):
    s2 = np.zeros(len(s), int); idx = rng.choice(np.arange(200, len(s)), size=int((s != 0).sum()), replace=False); s2[idx] = rng.choice([-1, 1], len(idx))
    TT = RP.run(m, f, s2); Q.append(TT.net.mean())
print(f"random times + random side (same signal count): 100 runs, mean {np.mean(Q):+.4%}, share >= real: {np.mean(np.array(Q) >= x.mean()):.3f}")

print("\n== fills (own L1 / data issues)")
mi = m.index
def inside(ts, px):
    w = m.loc[ts - pd.Timedelta(minutes=1): ts - pd.Timedelta(minutes=1)]
    return len(w) and (w.low.iloc[0] - 0.01 <= px <= w.high.iloc[0] + 0.01)
ok_e = np.mean([inside(r.entry_time, r.e) for r in T.itertuples()]); ok_x = np.mean([inside(r.exit_time, r.x) for r in T.itertuples()])
print(f"entry price inside its last 1m bar {ok_e:.1%}; exit price inside its 1m bar {ok_x:.1%}")
gp = []
for r in T.itertuples():
    seg = mi[(mi >= r.entry_time) & (mi < r.exit_time)]
    if len(seg) > 1: gp.append(np.diff(seg.values).max() / np.timedelta64(1, "m"))
    else: gp.append(0)
T["maxgap"] = gp; print(f"trades with a data gap > 30 min while open: {(T.maxgap > 30).sum()} (net of those {T.net[T.maxgap > 30].sum():+.3f})")
print(f"same-minute exits (entry minute = exit minute): {(T.exit_time - T.entry_time <= pd.Timedelta(minutes=1)).sum()}; median hold {(T.exit_time - T.entry_time).median()}")
T["entry_time_ct_end"] = T.entry_time
T.drop(columns=["entry_time_ct_end"]).assign(entry=T.e, exit=T.x)[["entry_time", "exit_time", "side", "entry", "exit"]].to_csv(os.path.join(HERE, "fills_utc.csv"), index=False)
T[["date", "side", "net", "t", "tx", "why", "e", "R"]].to_csv(os.path.join(HERE, "replica_trades.csv"), index=False)
