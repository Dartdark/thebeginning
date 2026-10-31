"""AlphaFlow ETH 30m short-only pullback (user's MultiCharts port of the TradingView 'Lorentzian Classification' indicator
+ fib pullback multi-slot engine, 2026-10-24; file Short-Only_Pullback_Strategy.txt; user's MC report ~10 months: 74 shorts,
PF 1.96, 32% win, +$87k on $100k at 2% risk).
Data: Binance ETHUSDT perpetual 30-minute klines 2020-01 -> 2026-10-23 (data/ETHUSDT_perp_30m.csv, UTC, open-stamped;
from data.binance.vision), 1-minute klines for the fill order (scratch only).
Signal = the port line by line: features RSI14 / WT 10-11 / CCI20 / ADX20 (all-time min-max for WT, CCI), label src[4] vs src,
Lorentzian ANN in C (analysis/c/lorentzian_ann.c: neighbours = the FIRST 5,000 bars of the chart, as the port's loop
runs lp = 0 .. 4999 from CurrentBar - 1 bars ago; 'rolling' = the last 5,000 bars instead), volatility (SMA ATR1 > ATR10),
regime (KLMF slope vs its 200 EMA >= -0.09), ADX14 > 21 filters, rational-quadratic kernel (h 6, r 3, x 25) falling.
Engine = the virtual slots (up to 8): on a new short signal, swing high = highest high of 30 bars, a0 = signal-bar low,
entry a0 + 0.41 R, stop a0 + 0.925 R, cancel a0 - 0.85 R, target entry - 4 x (stop - entry) (post's settings); from the
next bar: cancel first, then entry touch; same bar stop before target; risk $2,000 a trade (2% of $100k, no compounding).
Fill models: 'bar' = the code's 30-minute rules; '1m' = the same orders walked through 1-minute bars (cancel only before
the entry in time, stop before target in the same minute, no target in the fill minute).
Costs: Binance USDT-M VIP0 maker 0.02% (entry and target limits), taker 0.05% + 1 tick on stops; funding not charged.
  python3 analysis/alphaflow_eth_test.py [ETH_1M_ZIP_DIR] > analysis/outputs/alphaflow_eth_test_output.txt
"""
import sys, glob, ctypes, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, resampling as R

RISK, TICK, MAKER, TAKER = 2000.0, 0.01, 0.0002, 0.0005
NTRIAL = {"n": 0}
LIB = ctypes.CDLL("analysis/c/lorentzian_ann.so")


def xavg(x, n):
    a = 2.0 / (n + 1); out = np.empty(len(x)); out[0] = x[0]
    for i in range(1, len(x)): out[i] = out[i - 1] + a * (x[i] - out[i - 1])
    return out


def sma(x, n): return pd.Series(x).rolling(n, min_periods=1).mean().values


def runmm(x):
    lo, hi = np.minimum.accumulate(x), np.maximum.accumulate(x); rg = hi - lo
    return np.where(rg > 1e-9, (x - lo) / np.where(rg > 1e-9, rg, 1), 0.5)


def wilder_adx(h, l, c_ref, n):
    """The port's ADX: TR vs c_ref[1], Wilder sums, DX, then (prev*(n-1)+dx)/n (SMA for the first n bars)."""
    N = len(h); pc = np.r_[c_ref[0], c_ref[:-1]]; ph, pl = np.r_[h[0], h[:-1]], np.r_[l[0], l[:-1]]
    tr = np.maximum(np.maximum(h - l, np.abs(h - pc)), np.abs(l - pc)); tr[0] = h[0] - l[0]
    up, dn = h - ph, pl - l
    dmp = np.where(up > dn, np.maximum(up, 0), 0); dmn = np.where(dn > up, np.maximum(dn, 0), 0)
    s = np.empty((3, N)); s[:, 0] = tr[0], dmp[0], dmn[0]
    for i in range(1, N): s[:, i] = s[:, i - 1] - s[:, i - 1] / n + np.array([tr[i], dmp[i], dmn[i]])
    with np.errstate(all="ignore"):
        dip = np.where(s[0] != 0, s[1] / s[0] * 100, 0); din = np.where(s[0] != 0, s[2] / s[0] * 100, 0)
        dx = np.where(dip + din != 0, np.abs(dip - din) / (dip + din) * 100, 0)
    adx = np.empty(N); m = sma(dx, n)
    for i in range(N): adx[i] = m[i] if i < n else (adx[i - 1] * (n - 1) + dx[i]) / n
    return adx


def signals(d, rolling=False, maxbb=5000):
    o, h, l, c = (d[k].values for k in ("open", "high", "low", "close"))
    hlc3, ohlc4, src = (h + l + c) / 3, (o + h + l + c) / 4, (h + l + c + c) / 4
    # RSI (Wilder) as MultiCharts RSI
    ch = np.diff(c, prepend=c[0]); up, dn = np.maximum(ch, 0), np.maximum(-ch, 0)
    au, ad = pd.Series(up).ewm(alpha=1 / 14, adjust=False).mean().values, pd.Series(dn).ewm(alpha=1 / 14, adjust=False).mean().values
    rsi = np.where(ad > 0, 100 - 100 / (1 + au / np.where(ad > 0, ad, 1)), 100)
    f1 = rsi / 100
    e1 = xavg(hlc3, 10); e2 = xavg(np.abs(hlc3 - e1), 10); ci = np.where(e2 != 0, (hlc3 - e1) / (0.015 * np.where(e2 != 0, e2, 1)), 0)
    wt1 = xavg(ci, 11); f2 = runmm(wt1 - sma(wt1, 4))
    av = pd.Series(c).rolling(20).mean().values
    md = pd.Series(c).rolling(20).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True).values
    cci = np.where((md > 0) & ~np.isnan(md), (c - av) / (0.015 * np.where(md > 0, md, 1)), 0); f3 = runmm(np.nan_to_num(cci))
    f4 = wilder_adx(h, l, c, 20) / 100
    lab = np.zeros(len(c)); lab[4:] = np.where(src[:-4] < src[4:], -1, np.where(src[:-4] > src[4:], 1, 0))
    F = np.ascontiguousarray(np.c_[f1, f2, f3, f4], dtype=np.float64); pred = np.zeros(len(c))
    dp = ctypes.POINTER(ctypes.c_double)
    LIB.ann(F.ctypes.data_as(dp), np.ascontiguousarray(lab).ctypes.data_as(dp), len(c), 4, maxbb, 8, int(rolling), pred.ctypes.data_as(dp))
    # filters
    pc = np.r_[c[0], c[:-1]]; tr = np.maximum(np.maximum(h - l, np.abs(h - pc)), np.abs(l - pc))
    vol = sma(tr, 1) > sma(tr, 10)
    v1 = np.zeros(len(c)); v2 = np.zeros(len(c)); k = np.zeros(len(c)); k[0] = ohlc4[0]
    for i in range(1, len(c)):
        v1[i] = 0.2 * (ohlc4[i] - ohlc4[i - 1]) + 0.8 * v1[i - 1]; v2[i] = 0.1 * (h[i] - l[i]) + 0.8 * v2[i - 1]
        om = abs(v1[i] / v2[i]) if v2[i] else 0; al = (-om ** 2 + np.sqrt(om ** 4 + 16 * om ** 2)) / 8
        k[i] = al * ohlc4[i] + (1 - al) * k[i - 1]
    sl = np.abs(np.diff(k, prepend=k[0])); se = xavg(sl, 200); reg = np.where(se != 0, (sl - se) / np.where(se != 0, se, 1), 0) >= -0.09
    adxf = wilder_adx(h, l, src, 14) > 21
    filt = vol & reg & adxf
    sig = np.zeros(len(c))
    for i in range(len(c)):
        sig[i] = 1 if (pred[i] > 0 and filt[i]) else -1 if (pred[i] < 0 and filt[i]) else (sig[i - 1] if i else 0)
    diff = np.r_[False, sig[1:] != sig[:-1]]
    w = np.array([(1 + (i * i) / (36 * 2 * 3)) ** -3 for i in range(27)])
    yh = np.array([np.dot(src[max(0, i - 26):i + 1][::-1], w[:min(27, i + 1)]) / w[:min(27, i + 1)].sum() for i in range(len(c))])
    bear = np.r_[False, yh[:-1] > yh[1:]]; bull = np.r_[False, yh[:-1] < yh[1:]]
    return dict(short=(sig == -1) & diff & bear, long=(sig == 1) & diff & bull, pred=pred, filt=filt)


def setups(d, start, side=-1, rr=4.0, look=30, fe=0.41, fs=0.925, fc=-0.85):
    h, l = d.high.values, d.low.values; out = []
    hh = pd.Series(h).rolling(look, min_periods=1).max().values; ll = pd.Series(l).rolling(look, min_periods=1).min().values
    for i in np.where(start)[0]:
        if side < 0:
            a0, a1 = l[i], hh[i]; r = a1 - a0
            if r <= 0: continue
            e, s, cx = a0 + fe * r, a0 + fs * r, a0 + fc * r; t = e - rr * abs(s - e)
        else:
            a0, a1 = h[i], ll[i]; r = a1 - a0
            if r >= 0: continue
            e, s, cx = a0 + fe * r, a0 + fs * r, a0 + fc * r; t = e + rr * abs(e - s)
        rd = lambda x: np.floor(x / TICK + 0.5) * TICK
        out.append((i, rd(e), rd(s), rd(cx), rd(t)))
    return out


def simulate(d, sets, side=-1, slots=8, m1=None):
    """Virtual slots as the code. m1 = (minute index start per 30-min bar, 1-min o/h/l arrays) for the 1-minute walk."""
    h, l, o = d.high.values, d.low.values, d.open.values; N = len(h); act = []; trades = []; si = 0
    sets = sorted(sets); S = side
    for b in range(N):
        keep = []
        for z in act:
            st, i, e, s, cx, t, ef, eb = z
            res = None
            if m1 is None:
                if st == "p" and b > i:
                    if (l[b] <= cx) if S < 0 else (h[b] >= cx): continue
                    if (h[b] >= e) if S < 0 else (l[b] <= e):
                        ef = e; eb = b; st = "a"
                        if (h[b] >= s) if S < 0 else (l[b] <= s): res = (s, "stop")
                        elif (l[b] <= t) if S < 0 else (h[b] >= t): res = (t, "target")
                elif st == "a":
                    if (h[b] >= s) if S < 0 else (l[b] <= s): res = (s, "stop")
                    elif (l[b] <= t) if S < 0 else (h[b] >= t): res = (t, "target")
            else:
                a0, a1, mo, mh, ml = m1[0][b], m1[0][b + 1], m1[1], m1[2], m1[3]
                if st == "p" and b <= i: keep.append(z); continue
                for k in range(a0, a1):
                    if st == "p":
                        if (ml[k] <= cx) if S < 0 else (mh[k] >= cx): st = "x"; break
                        if (mh[k] >= e) if S < 0 else (ml[k] <= e):
                            ef = max(mo[k], e) if S < 0 else min(mo[k], e); eb = b; st = "a"
                            if (mh[k] >= s) if S < 0 else (ml[k] <= s): res = (s, "stop"); break
                            continue
                    elif st == "a":
                        if (mh[k] >= s) if S < 0 else (ml[k] <= s): res = (max(mo[k], s) if S < 0 else min(mo[k], s), "stop"); break
                        if (ml[k] <= t) if S < 0 else (mh[k] >= t): res = (t, "target"); break
                if st == "x": continue
            if res is not None:
                x, kind = res
                if kind == "stop": x = x + (TICK if S < 0 else -TICK)
                qty = RISK / abs(s - e)
                gross = (ef - x) * qty if S < 0 else (x - ef) * qty
                fee = qty * (ef * MAKER + x * (TAKER if kind == "stop" else MAKER))
                trades.append(dict(sig=i, eb=eb, xb=b, entry=ef, exit=x, kind=kind, gross=gross, net=gross - fee, R=(gross - fee) / RISK))
                continue
            keep.append((st, i, e, s, cx, t, ef, eb))
        act = keep
        while si < len(sets) and sets[si][0] == b:
            if len(act) < slots: act.append(("p",) + sets[si] + (None, None))
            si += 1
    t = pd.DataFrame(trades)
    if len(t):
        t["date"] = d.t.values[t.xb]; t["date"] = pd.to_datetime(t.date); t["entry_t"] = d.t.values[t.eb]
    return t


def load_1m(zdir, d):
    import zipfile, io
    parts = []
    for z in sorted(glob.glob(zdir + "/*.zip")):
        with zipfile.ZipFile(z) as f:
            x = pd.read_csv(io.BytesIO(f.read(f.namelist()[0])), header=None, usecols=range(5))
        if str(x.iloc[0, 0]).startswith("open"): x = x.iloc[1:]
        parts.append(x.astype(float))
    m = pd.concat(parts); m.columns = ["t", "o", "h", "l", "c"]; m["t"] = pd.to_datetime(m.t.astype("int64"), unit="ms")
    m = m.drop_duplicates("t").sort_values("t").reset_index(drop=True)
    idx = np.searchsorted(m.t.values, d.t.values); idx = np.r_[idx, len(m)]
    return idx, m.o.values, m.h.values, m.l.values


def tst(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pf(x): x = pd.Series(x); return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def line(t, nm, w=46):
    if len(t) < 5: return f"   {nm:<{w}} n={len(t)}"
    y = t.date.dt.year; by = t.groupby(y).R.sum()
    a, b = t.R[y < 2023], t.R[y >= 2023]
    return (f"   {nm:<{w}} n={len(t):4d} ({len(t) / 6.8:3.0f}/yr) {t.R.mean():+.3f} R  PF {pf(t.net):4.2f} t {tst(t.R):4.1f} win {np.mean(t.R > 0):.0%}"
            f" yrs+ {(by > 0).sum()}/{len(by)} | 20-22 {a.mean():+.3f} R t {tst(a):4.1f} | 23+ {b.mean():+.3f} R t {tst(b):4.1f} | ${t.net.sum():,.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    d = pd.read_csv("data/ETHUSDT_perp_30m.csv", parse_dates=["t"])
    S = signals(d); NTRIAL["n"] += 1
    print(f"bars {len(d)} ({d.t.iloc[0]} -> {d.t.iloc[-1]}); new short signals {S['short'].sum()}, long {S['long'].sum()}; "
          f"prediction < 0 on {np.mean(S['pred'] < 0):.0%} of bars, filters pass {S['filt'].mean():.0%}")
    st = setups(d, S["short"]); base = simulate(d, st); NTRIAL["n"] += 1
    base.to_csv("analysis/outputs/alphaflow_eth_trades.csv", index=False)
    w0 = d.t.iloc[-1] - pd.Timedelta(days=298)
    print("\n1. Short-only, the post's settings, $2,000 risk a trade, 30-minute rules (as the code):")
    print(line(base, "2020-01 -> 2026-10"))
    rec = base[base.entry_t >= w0]; print(line(rec, f"last ~10 months (from {w0.date()})"))
    print("   by year R:", base.groupby(base.date.dt.year).R.sum().round(1).to_dict(), "| trades:", base.groupby(base.date.dt.year).size().to_dict())
    print("   exits:", base.kind.value_counts().to_dict(), f"| setups {len(st)}, filled {len(base)}")
    eth = d.set_index("t").close.resample("YE").last(); print("   ETH year-end close:", eth.round(0).astype(int).to_dict())

    zdir = sys.argv[1] if len(sys.argv) > 1 else None
    if zdir:
        m1 = load_1m(zdir, d); have = d.t >= pd.Timestamp("2020-01-01")
        b1 = simulate(d, st, m1=m1); NTRIAL["n"] += 1
        print("\n2. Fill order on 1-minute bars (same orders):")
        print(line(b1, "1-minute walk")); print(line(b1[b1.entry_t >= w0], "1-minute walk, last ~10 months"))
        mg = base.merge(b1, on="sig", how="outer", suffixes=("_bar", "_1m"), indicator=True)
        print(f"   same setups filled: both {(mg._merge == 'both').sum()}, bar only {(mg._merge == 'left_only').sum()}, 1-min only {(mg._merge == 'right_only').sum()}; "
              f"bar target -> 1-min stop {((mg.kind_bar == 'target') & (mg.kind_1m == 'stop')).sum()}, bar stop -> 1-min target {((mg.kind_bar == 'stop') & (mg.kind_1m == 'target')).sum()}")
        base1 = b1
    else:
        base1 = None

    print("\n3. Variants and placebos (30-minute rules):")
    V = []
    roll = signals(d, rolling=True); NTRIAL["n"] += 1
    V.append(("ANN on the last 5,000 bars (rolling)", simulate(d, setups(d, roll["short"]))))
    dd = d[d.t >= d.t.iloc[-1] - pd.Timedelta(days=298 + 105)].reset_index(drop=True)      # chart loaded ~5,000 bars before the window
    s2 = signals(dd); t2 = simulate(dd, setups(dd, s2["short"])); t2 = t2[t2.entry_t >= w0]; NTRIAL["n"] += 1
    V.append(("chart starting 5,000 bars before the window", t2))
    V.append(("longs (mirror, AlphaFlow buy signals)", simulate(d, setups(d, S["long"], side=1), side=1)))
    V.append(("shorts on AlphaFlow BUY signals", simulate(d, setups(d, S["long"]))))
    for rr in (2.0, 3.0, 5.0): V.append((f"target {rr} R", simulate(d, setups(d, S["short"], rr=rr))))
    V.append(("file defaults (3 R)", simulate(d, setups(d, S["short"], rr=3.0))))
    V.append(("1 slot only", simulate(d, st, slots=1)))
    for nm, t in V:
        NTRIAL["n"] += 1; print(line(t, nm))
    rng = np.random.default_rng(1); n_sig = S["short"].sum(); pl = []
    for s in range(100):
        fake = np.zeros(len(d), bool); fake[rng.choice(np.arange(300, len(d)), n_sig, replace=False)] = True
        pl.append(simulate(d, setups(d, fake)))
    m = np.array([p.R.mean() for p in pl]); mr = np.array([p[p.entry_t >= w0].R.mean() for p in pl])
    print(f"   random short signals (same count, same fib engine), 100 seeds: {m.mean():+.3f} R (5-95% {np.percentile(m, 5):+.3f} .. "
          f"{np.percentile(m, 95):+.3f}); rule {base.R.mean():+.3f} R beats {np.mean(m < base.R.mean()):.0%}; last 10 months random "
          f"{np.nanmean(mr):+.3f} R (95% {np.nanpercentile(mr, 95):+.3f}) vs rule {rec.R.mean():+.3f}")

    print("\n4. Metrics ($2,000 risk a trade, daily, booked on the exit day):")
    days = pd.date_range(d.t.iloc[0].normalize(), d.t.iloc[-1].normalize(), freq="D")
    rows = {}
    for nm, t in (("bar rules", base),) + ((("1-min walk", base1),) if base1 is not None else ()):
        x = t.groupby(t.date.dt.normalize()).net.sum().reindex(days, fill_value=0.0)
        for per, s0 in (("2020-26", "2020-01-01"), ("2023+", "2023-01-01")):
            rows[f"{nm} {per}"] = (x[x.index >= s0], t[t.date >= s0].set_index("date").net)
    print(M.table(rows, capital=100_000.0)); print("   (calendar-day series scaled by sqrt(252): x 1.20 for 365-day Sharpe / Sortino)")
    x = base.groupby(base.date.dt.normalize()).net.sum().reindex(days, fill_value=0.0)
    b_, p_ = R.report({"bar rules 2023+": x[x.index >= "2023-01-01"]}, limits=(10000, 20000, 40000), capital=100_000.0); print(b_); print(p_)
    print(f"\n   trials {NTRIAL['n']}; t threshold {M.t_threshold(NTRIAL['n']):.2f}; deflated Sharpe {M.deflated_sharpe(x.values, NTRIAL['n']):.2f}")
