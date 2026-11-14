"""TrendSwingTrader V2 rebuild by matching V2's published daily equity curve (pre-registered checks/candidates/tst_v2_rebuild/PREREG.md).
  tools/run_stamped.sh analysis/tst_v2_rebuild.py > analysis/outputs/tst_v2_rebuild_output.txt
"""
import sys, json, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
print(__doc__.split("\n")[0])
src = open("analysis/jesse_lib_btc_test.py", encoding="utf-8").read().split("adx_ref = P.run(P.setup())")[0]
E = {"__name__": "lib", "__doc__": "x\n"}; exec(compile(src, "jesse_lib_engine", "exec"), E)
atr, dmi, ema = E["atr"], E["dmi"], E["ema"]
h4 = E["bars"]("4h"); q15 = E["bars"]("15min")


def site_days(name, period):
    j = json.load(open(f"scratch_data/jesse_site/{name}__{period.replace(' ', '_')}.json"))
    d = j["equity_curve"][0]["data"]; t = pd.to_datetime([x["time"] for x in d], unit="s"); v = np.array([x["value"] for x in d])
    ch = np.r_[np.abs(np.diff(v)) > 1e-6, False]                     # change from day i to day i+1 -> activity during day i (shift tested)
    return pd.Series(ch, index=t)


C = h4.close.to_numpy(); A = atr(h4); _, _, ADX = dmi(h4); T4 = h4.index.values
Q = q15.index.values; QH, QL = q15.high.to_numpy(), q15.low.to_numpy()
qpos = np.searchsorted(Q, (h4.index + pd.Timedelta(hours=4)).values)      # first 15m bar after each 4h close
EM = {n: ema(C, n) for n in (9, 13, 21, 30, 34, 50, 70, 100, 150, 200)}


def run(f, mi, sl, adx_t, S, T, R, lo=None, hi=None):
    e1, e2, e3 = EM[f], EM[mi], EM[sl]
    sig = np.where((e3 < e2) & (e2 < e1) & (e1 < C) & (ADX > adx_t), 1, np.where((e3 > e2) & (e2 > e1) & (e1 > C) & (ADX > adx_t), -1, 0))
    i0 = 0 if lo is None else np.searchsorted(T4, np.datetime64(lo)); i1 = len(C) - 1 if hi is None else np.searchsorted(T4, np.datetime64(hi))
    out = []; i = max(i0, 200)
    while i < i1:
        s = sig[i]
        if not s: i += 1; continue
        e = C[i]; a = A[i]; stop = e - s * S * a; tgt = e + s * T * a; half = False; j = i; px = None; parts = 0.0
        while j < len(C) - 1:
            for k in range(qpos[j], min(qpos[j + 1], len(Q))):
                if (s == 1 and QL[k] <= stop) or (s == -1 and QH[k] >= stop): px = stop; break
                if not half and ((s == 1 and QH[k] >= tgt) or (s == -1 and QL[k] <= tgt)):
                    half = True; parts = 0.5 * s * (tgt - e) / e; stop = e
            if px is not None: break
            j += 1
            if half: stop = max(C[j] - R * A[j], e) if s == 1 else min(C[j] + R * A[j], e)
        if px is None: break
        q = 0.5 if half else 1.0
        out.append((T4[i], T4[j] + np.timedelta64(4, "h"), s, parts + q * s * (px - e) / e - 0.0014))
        i = j + 1
    return pd.DataFrame(out, columns=["t", "tx", "side", "ret"])


def active_days(t, days):
    a = np.zeros(len(days), bool); dv = days.values
    for r in t.itertuples():
        d0 = np.datetime64(pd.Timestamp(r.t).normalize()); d1 = np.datetime64((pd.Timestamp(r.tx) - pd.Timedelta(seconds=1)).normalize())
        a[(dv >= d0) & (dv <= d1)] = True
    return pd.Series(a, index=days)


def f1(a, b):
    a = a.astype(bool); b = b.astype(bool); tp = (a & b).sum(); return 2 * tp / (a.sum() + b.sum()) if (a.sum() + b.sum()) else 0.0


V2 = pd.concat([site_days("trendswingtrader-v2", p) for p in ("2022 - 2023", "2023 - 2024")])
V1 = pd.concat([site_days("trendswingtrader-v1", p) for p in ("2022 - 2023", "2023 - 2024")])
V2h = site_days("trendswingtrader-v2", "2025 - 2026")
days = V2.index; wide = pd.date_range("2021-12-20", "2024-01-10"); wide_h = pd.date_range("2024-12-20", "2026-01-10")
al = lambda act, sh, idx: act.shift(sh).reindex(idx).fillna(False).astype(bool)
# 1. alignment on V1's own code (21 / 50 / 100, ADX 25, stop 2, half at 3, trail 2)
act = active_days(run(21, 50, 100, 25, 2.0, 3.0, 2.0, "2021-12-01", "2024-01-01"), wide)
for sh in (-1, 0, 1):
    print(f"V1 code vs V1 site curve, shift {sh:+d} day: F1 {f1(al(act, sh, days), V1):.3f} (site active days {V1.sum()}, ours {al(act, sh, days).sum()})")
best_sh = max((-1, 0, 1), key=lambda sh: f1(al(act, sh, days), V1))
print(f"V1 code vs V2 site curve (how far V2 is from V1): F1 {f1(al(act, best_sh, days), V2):.3f}; alignment shift {best_sh:+d}")
# 2. grid on 2022-23
rows = []
for f, mi, sl, a_, S, T, R in itertools.product((9, 13, 21, 30), (34, 50, 70), (100, 150, 200), (20, 25, 30, 35), (1.5, 2, 2.5, 3), (2, 3, 4), (1.5, 2, 3)):
    t = run(f, mi, sl, a_, S, T, R, "2021-12-01", "2024-01-01")
    tt = t[(t.t >= np.datetime64("2022-01-01")) & (t.t < np.datetime64("2024-01-01"))]
    rows.append((f, mi, sl, a_, S, T, R, f1(al(active_days(t, wide), best_sh, days), V2), len(tt), int((tt.side == 1).sum()), tt.ret.sum()))
G = pd.DataFrame(rows, columns=["fast", "mid", "slow", "adx", "stop", "half", "trail", "f1", "n", "longs", "ret"]).sort_values("f1", ascending=False)
print(f"\nV2 site 2022-23: 58 trades (31 long), active days {V2.sum()}; grid of {len(G)} candidates, F1: median {G.f1.median():.3f}, 95th {G.f1.quantile(.95):.3f}, best {G.f1.max():.3f}")
print(G.head(15).to_string(index=False))
G.to_csv("checks/candidates/tst_v2_rebuild/grid.csv", index=False)
# 3. check on 2025 (never used to pick)
v1h = al(active_days(run(21, 50, 100, 25, 2.0, 3.0, 2.0, "2024-12-01", "2026-01-01"), wide_h), best_sh, V2h.index)
print(f"\nCHECK 2025 (not used to pick); V2 active days {V2h.sum()}; V1 code vs V2 2025 F1 {f1(v1h, V2h):.3f}")
for sel in range(0, 5):
    c = G.iloc[sel]; tc = run(int(c.fast), int(c.mid), int(c.slow), c.adx, c.stop, c.half, c.trail, "2024-12-01", "2026-01-01")
    print(f"   rank {sel + 1}: {dict(c[['fast', 'mid', 'slow', 'adx', 'stop', 'half', 'trail']])} 2022-23 F1 {c.f1:.3f} -> 2025 F1 {f1(al(active_days(tc, wide_h), best_sh, V2h.index), V2h):.3f}")
