"""Jesse CLMeanReversion (free + premium as described) on CME CL futures, pre-registered checks/candidates/jesse_cl_meanrev/PREREG.md
(user 2026-11-13: jesse.trade library, shortlist #1). Per 1 CL after $7.25 + 1 tick a market / stop fill; per MCL = / 10 - $0.55.
  tools/run_stamped.sh analysis/jesse_cl_meanrev_test.py > analysis/outputs/jesse_cl_meanrev_test_output.txt
"""
import sys, glob, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
print(__doc__.split("\n")[0])
PV, TICK, COMM = 1000.0, 0.01, 7.25
BBP, BBD, ATRM = 40, 3.45, 3.43

d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/CL_1min_20*.csv"))])
d["ts"] = pd.to_datetime(d.date.astype(str) + d.time.astype(str).str.zfill(4), format="%Y%m%d%H%M") - pd.Timedelta(minutes=1)  # bar open, CT
d = d.drop_duplicates("ts").sort_values("ts").reset_index(drop=True)
d = d[d.ts >= "2017-06-01"].reset_index(drop=True)
# rolls: first bar after a >= 30-min pause, days 10-26, largest |gap| of the month if > 4x the median reopen gap -> difference adjust
brk = np.flatnonzero(d.ts.diff().dt.total_seconds().to_numpy() >= 1800)
gap = d.open.to_numpy()[brk] - d.close.to_numpy()[brk - 1]
B = pd.DataFrame(dict(j=brk, gap=gap, ts=d.ts.to_numpy()[brk])); med = B.gap.abs().median(); adj = np.zeros(len(d)); nroll = 0
for _, g in B[(B.ts.dt.day >= 10) & (B.ts.dt.day <= 26)].groupby([B.ts.dt.year, B.ts.dt.month]):
    k = g.gap.abs().idxmax()
    if abs(g.at[k, "gap"]) > 4 * med: adj[:int(g.at[k, "j"])] += g.at[k, "gap"]; nroll += 1
for c in ("open", "high", "low", "close"): d[c] = d[c] + adj
print(f"CL 1-min {d.ts.iloc[0]} -> {d.ts.iloc[-1]} CT, {len(d):,} bars, rolls removed {nroll} (median reopen gap {med:.3f})")
m = d.set_index("ts")[["open", "high", "low", "close"]]
agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
b30 = m.resample("30min", label="left", closed="left").agg(agg).dropna()
h1 = m.resample("1h", label="left", closed="left").agg(agg).dropna()
C = b30.close
mid = C.rolling(BBP).mean(); sd = C.rolling(BBP).std(ddof=0); up = mid + BBD * sd; lo = mid - BBD * sd
pc = h1.close.shift(); tr = pd.concat([h1.high - h1.low, (h1.high - pc).abs(), (h1.low - pc).abs()], axis=1).max(axis=1)
atr1 = tr.ewm(alpha=1 / 14, adjust=False).mean()                       # Wilder ATR(14) on 1h
ema1 = {n: h1.close.ewm(span=n, adjust=False).mean() for n in (20, 50, 100)}
t_close = b30.index + pd.Timedelta(minutes=30)


def last_done(s):
    """value of the last COMPLETED 1h candle at each 30m close"""
    idx = s.index + pd.Timedelta(hours=1)
    pos = np.searchsorted(idx.values, t_close.values, side="right") - 1
    v = np.full(len(t_close), np.nan); ok = pos >= 0; v[ok] = s.to_numpy()[pos[ok]]; return v


A1 = last_done(atr1); H1C = last_done(h1.close); E1 = {n: last_done(e) for n, e in ema1.items()}
MT = m.index.values; MO, MH, ML, MC = (m[k].to_numpy() for k in ("open", "high", "low", "close"))
mpos = np.searchsorted(MT, t_close.values)                            # first minute after each 30m close
hm = t_close.hour * 100 + t_close.minute
flat_bar = np.asarray(hm == 1545); noent = np.asarray((hm >= 1500) & (hm < 1700))
CV, MID, UP, LO = C.to_numpy(), mid.to_numpy(), up.to_numpy(), lo.to_numpy()


def run(trend=None, apex=False, seed=None):
    rng = np.random.default_rng(seed) if seed is not None else None
    out = []; i = BBP; n = len(CV)
    while i < n - 1:
        if np.isnan(LO[i]) or np.isnan(A1[i]) or (apex and noent[i]): i += 1; continue
        s = 1 if CV[i] < LO[i] else (-1 if CV[i] > UP[i] else 0)
        if s and trend is not None:
            if not ((s == 1 and H1C[i] > E1[trend][i]) or (s == -1 and H1C[i] < E1[trend][i])): s = 0
        if not s: i += 1; continue
        if rng is not None: s = int(rng.choice([-1, 1]))
        e = CV[i] + s * TICK; stop = CV[i] - s * ATRM * A1[i]; tp = MID[i]
        if (tp - e) * s <= 0: i += 1; continue
        j = i + 1; px = None; why = None
        while j < n:
            for k in range(mpos[j - 1], min(mpos[j], len(MT))):            # minutes inside 30m bar j
                if (s == 1 and ML[k] <= stop) or (s == -1 and MH[k] >= stop):
                    px = (min(stop, MO[k]) if s == 1 else max(stop, MO[k])) - s * TICK; why = "stop"; break
                if (s == 1 and MH[k] >= tp) or (s == -1 and ML[k] <= tp):
                    px = tp; why = "target"; break
            if px is not None: break
            if (s == 1 and CV[j] >= MID[j]) or (s == -1 and CV[j] <= MID[j]): px = CV[j] - s * TICK; why = "mean"; break
            if apex and flat_bar[j]: px = CV[j] - s * TICK; why = "flat"; break
            j += 1
        if px is None: break
        out.append((b30.index[i], b30.index[j], s, (px - e) * s * PV - COMM, why, ATRM * A1[i] * PV))
        i = j + 1
    t = pd.DataFrame(out, columns=["t", "tx", "side", "net", "why", "risk"]); t["yr"] = t.t.dt.year
    return t


def tt(x): return x.mean() / x.std(ddof=1) * np.sqrt(len(x)) if len(x) > 2 else np.nan


def show(t, nm):
    x = t.net; a = t[t.yr <= 2022]; z = t[t.yr >= 2023]; oos = t[~((t.t >= "2026-05-01") & (t.t < "2026-08-01"))]
    pf = x[x > 0].sum() / -x[x < 0].sum() if (x < 0).any() else np.inf
    yrs = (t.t.max() - t.t.min()).days / 365.25
    dd = t.groupby(t.tx.dt.normalize()).net.sum(); e = dd.cumsum()
    print(f"\n{nm}\n  {len(t)} trades ({len(t) / yrs:.0f} a year), win {np.mean(x > 0):.1%}, ${x.mean():.1f} per CL, PF {pf:.2f}, t {tt(x):.2f} | "
          f"2018-22 ${a.net.mean():.1f} (t {tt(a.net):.2f}) | 2023+ ${z.net.mean():.1f} (t {tt(z.net):.2f}) | without the author's fit window t {tt(oos.net):.2f}")
    print(f"  max DD ${(e - e.cummax()).min():,.0f} per CL, worst trade ${x.min():,.0f}, median stop ${t.risk.median():,.0f}; per MCL ${x.mean() / 10 - 0.55:.2f} a trade, ${(x / 10 - 0.55).sum() / yrs:,.0f} a year")
    print(f"  longs ${t.net[t.side == 1].mean():.1f} (t {tt(t.net[t.side == 1]):.2f}, n {(t.side == 1).sum()}) | shorts ${t.net[t.side == -1].mean():.1f} (t {tt(t.net[t.side == -1]):.2f}, n {(t.side == -1).sum()}) | exits {t.why.value_counts().to_dict()}")
    print("  by year $: " + "  ".join(f"{y} {g.net.sum():+,.0f} ({len(g)})" for y, g in t.groupby("yr")))
    return t


V0 = show(run(), "V0 as coded (free; both sides, 24h)")
V1 = show(run(trend=50), "V1 premium as described: fade only with the 1h EMA(50) trend")
for n in (20, 100): show(run(trend=n), f"   sensitivity: 1h EMA({n})")
show(run(apex=True), "V2 Apex-legal V0 (out 15:45 CT, no entries 15:00-17:00)")
show(run(trend=50, apex=True), "V3 Apex-legal V1")
show(V0[V0.side == 1], "V4 V0 longs (slice)"); show(V0[V0.side == -1], "V5 V0 shorts (slice)")
pm = np.array([run(seed=s).net.mean() for s in range(100)])
print(f"\nplacebo, V0 entry moments with a random side (100 runs): mean ${pm.mean():.1f}, p95 ${np.percentile(pm, 95):.1f}; real ${V0.net.mean():.1f}, p = {np.mean(pm >= V0.net.mean()):.2f}")
V0.assign(date=V0.tx.dt.normalize().dt.date).to_csv("checks/candidates/jesse_cl_meanrev/trades_V0.csv", index=False)
V1.assign(date=V1.tx.dt.normalize().dt.date).to_csv("checks/candidates/jesse_cl_meanrev/trades_V1.csv", index=False)
