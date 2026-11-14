"""EMBIA_V3 (user's Jesse strategy, 2026-11-14; pre-registered checks/candidates/embia_v3/PREREG.md): rebuild on BTC spot and NQ, ingredient
breakdown, random-side placebo; NQ trades saved for the data sweep.
  tools/run_stamped.sh analysis/embia_v3_test.py > analysis/outputs/embia_v3_test_output.txt
"""
import sys, glob, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import jump_lib as L
print(__doc__.split("\n")[0])


def wilder(x, n):
    y = np.full(len(x), np.nan); s = np.nan
    for i in range(len(x)):
        if np.isnan(x[i]): continue
        s = x[i] if np.isnan(s) else s + (x[i] - s) / n; y[i] = s
    return y


def ind(b):
    """b: DataFrame o h l c v (bars). Adds vwma5/8/13/51, srsi k, adx, atr."""
    c, h, l, v = b.c.values, b.h.values, b.l.values, b.v.values
    pv = pd.Series(c * v); vv = pd.Series(v)
    for p in (5, 8, 13, 51): b[f"vw{p}"] = (pv.rolling(p).sum() / vv.rolling(p).sum()).values
    d = np.diff(c, prepend=np.nan); up = wilder(np.where(d > 0, d, 0.0), 14); dn = wilder(np.where(d < 0, -d, 0.0), 14)
    rsi = 100 - 100 / (1 + up / np.where(dn == 0, np.nan, dn)); r = pd.Series(rsi)
    st = (r - r.rolling(14).min()) / (r.rolling(14).max() - r.rolling(14).min()) * 100
    b["srsi"] = st.rolling(3).mean().values
    pc = np.r_[np.nan, c[:-1]]; tr = np.nanmax(np.c_[h - l, np.abs(h - pc), np.abs(l - pc)], axis=1)
    b["atr"] = wilder(tr, 14)
    um = h - np.r_[np.nan, h[:-1]]; dm = np.r_[np.nan, l[:-1]] - l
    pdm = np.where((um > dm) & (um > 0), um, 0.0); mdm = np.where((dm > um) & (dm > 0), dm, 0.0)
    a = wilder(tr, 14); pdi = 100 * wilder(pdm, 14) / a; mdi = 100 * wilder(mdm, 14) / a
    dx = 100 * np.abs(pdi - mdi) / np.where(pdi + mdi == 0, np.nan, pdi + mdi); b["adx"] = wilder(dx, 14)
    return b


def bars(m, tf):
    g = m.resample(tf, label="right", closed="right")
    b = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last(), "v": g.v.sum()}).dropna()
    return ind(b)


def signals(m, tf, drop=None):
    b = bars(m, tf); H = bars(m, "1h")
    Hs = H[["vw5", "vw8", "vw13", "vw51", "srsi"]].add_prefix("H_")
    b = pd.merge_asof(b, Hs, left_index=True, right_index=True, direction="backward")      # last COMPLETED 1h bar (stamped at its close)
    def on(k): return drop != k
    L_ = np.ones(len(b), bool); S_ = np.ones(len(b), bool)
    if on("ltf_stack"): L_ &= (b.vw5 > b.vw8) & (b.vw8 > b.vw13); S_ &= (b.vw5 < b.vw8) & (b.vw8 < b.vw13)
    if on("adx"): L_ &= b.adx > 28; S_ &= b.adx > 28
    if on("vwma_filter"): L_ &= b.c > b.H_vw51; S_ &= b.c < b.H_vw51
    if on("htf_srsi"): L_ &= b.H_srsi < 90; S_ &= b.H_srsi > 10
    if on("ltf_srsi"): L_ &= b.srsi < 20; S_ &= b.srsi > 80
    if on("htf_stack"): L_ &= (b.H_vw5 > b.H_vw8) & (b.H_vw8 > b.H_vw13); S_ &= (b.H_vw5 < b.H_vw8) & (b.H_vw8 < b.H_vw13)
    ok = b[["vw51", "H_vw51", "srsi", "H_srsi", "adx", "atr"]].notna().all(axis=1)
    side = np.where(L_ & ok, 1, np.where(S_ & ok, -1, 0))
    return b.index[side != 0], side[side != 0], b.atr.values[side != 0]


def simulate(m, ts_sig, side, atrv, cost_fn, flat=None, no_entry=None, rng=None):
    """walk the 1-min path; one position at a time. flat(i) -> True forces a market exit at that minute's close."""
    tsm = m.index.values; o, h, l, c = (m[k].values for k in ("o", "h", "l", "c"))
    pos = np.searchsorted(tsm, ts_sig.values, side="right"); out = []; busy = -1; n = len(o)
    for k in range(len(pos)):
        i = pos[k]
        if i >= n - 1 or i <= busy: continue
        if no_entry is not None and no_entry[i]: continue
        if tsm[i] - tsm[i - 1] > np.timedelta64(10, "m"): continue
        s = int(side[k]) if rng is None else int(rng.choice([-1, 1]))
        e = o[i]; sp = e - s * 2.85 * atrv[k]; tp = e + s * 3.4 * atrv[k]; ex = None
        for j in range(i, n):
            if (l[j] <= sp) if s > 0 else (h[j] >= sp): ex = (min(o[j], sp) if s > 0 else max(o[j], sp)) if j > i else sp; why = "stop"; break
            if (h[j] >= tp) if s > 0 else (l[j] <= tp): ex = tp; why = "tgt"; break
            if flat is not None and flat[j]: ex = c[j]; why = "flat"; break
        if ex is None: break
        out.append((pd.Timestamp(tsm[i]), s, e, ex, why, cost_fn(e, ex, s, why), j - i)); busy = j
    return pd.DataFrame(out, columns=["ts", "side", "entry", "exit", "why", "net", "mins"])


def tt(x): x = pd.Series(x); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan
def pf(x): return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
def line(T, nm):
    if len(T) < 5: return f"   {nm:<40} n {len(T)}"
    x = T.net; y = T.ts.dt.year
    return (f"   {nm:<40} n {len(x):5d} avg ${x.mean():7.1f} t {tt(x):5.2f} PF {pf(x):.2f} win {np.mean(x > 0):.0%} | 2018-22 ${x[y <= 2022].mean():7.1f} (t {tt(x[y <= 2022]):4.1f}) "
            f"2023+ ${x[y >= 2023].mean():7.1f} (t {tt(x[y >= 2023]):4.1f}) | L ${x[T.side > 0].mean():6.1f} S ${x[T.side < 0].mean():6.1f}")
def by_year(T): return "      " + " ".join(f"{k % 100:02d}:{v / 1000:+.1f}k" for k, v in T.net.groupby(T.ts.dt.year).sum().items())

# ---------------- markets
fs = sorted(glob.glob("data/BTCUSD_spot_1min_20*.csv")); d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
d.index = pd.to_datetime(d.date.astype(str), format="%Y%m%d") + pd.to_timedelta(d.time // 100 * 60 + d.time % 100, unit="m")
BTC = d.rename(columns={"open": "o", "high": "h", "low": "l", "close": "c", "volume": "v"})[["o", "h", "l", "c", "v"]].sort_index(); BTC = BTC[~BTC.index.duplicated()]
btc_cost = lambda e, x, s, why: ((x - e) * s - 0.0006 * (e + x))                       # $ per 1 BTC: 0.05% fee + 0.01% slip a side
nq = L.minute(); NQ = nq.set_index("ts").rename(columns={"open": "o", "high": "h", "low": "l", "close": "c", "volume": "v"})[["o", "h", "l", "c", "v"]]
nq_cost = lambda e, x, s, why: ((x - e) * s * 20 - 7.25 - 5.0 - (0 if why == "tgt" else 5.0))
hm = NQ.index.hour * 100 + NQ.index.minute
apex_flat = ((hm >= 1555) & (hm < 1700)); apex_noentry = ((hm >= 1500) & (hm < 1700)) | (NQ.index.dayofweek >= 5)

RES = {}
for mk, M, cost, extra in (("BTC spot", BTC, btc_cost, {}), ("NQ as coded (holds overnight)", NQ, nq_cost, {}),
                           ("NQ Apex (flat 15:55, no entries 15:00-17:00)", NQ, nq_cost, dict(flat=apex_flat, no_entry=apex_noentry))):
    print(f"\n################ {mk}")
    for tf in ("15min", "5min"):
        tsig, sd, av = signals(M, tf); T = simulate(M, tsig, sd, av, cost, **extra); T = T[T.ts >= "2018-01-01"]
        print(line(T, f"{tf} {'PRIMARY' if tf == '15min' else 'secondary'}")); print(by_year(T))
        print(f"      exits " + ", ".join(f"{k} {v}" for k, v in T.why.value_counts().items()) + f"; median hold {T.mins.median():.0f} min; {len(T) / 8.85:.0f} trades a year")
        RES[(mk, tf)] = T
    tsig, sd, av = signals(M, "15min"); rng = np.random.default_rng(1)
    pl = np.array([simulate(M, tsig, sd, av, cost, rng=rng, **extra).pipe(lambda P: P[P.ts >= "2018-01-01"].net.mean()) for _ in range(40)])
    base = RES[(mk, "15min")].net.mean()
    print(f"   random side, same entries (40 runs): mean ${pl.mean():.1f}, p95 ${np.percentile(pl, 95):.1f} -> real ${base:.1f}: p {np.mean(pl >= base):.3f}")
    print("   ingredient breakdown (15 min, one filter removed at a time):")
    for k in ("ltf_stack", "adx", "vwma_filter", "htf_srsi", "ltf_srsi", "htf_stack"):
        tsig, sd, av = signals(M, "15min", drop=k); T = simulate(M, tsig, sd, av, cost, **extra); print(line(T[T.ts >= "2018-01-01"], f"without {k}"))
T = RES[("NQ as coded (holds overnight)", "15min")]
T.assign(date=T.ts.dt.normalize(), entry_date=T.ts.dt.normalize())[["date", "entry_date", "net", "side"]].to_csv("checks/candidates/embia_v3/trades_nq.csv", index=False)
