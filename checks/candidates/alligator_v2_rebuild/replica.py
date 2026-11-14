"""Checker replica of the AlligatorV2 rebuild, written from spec.md only (BTC spot, 30m, return units)."""
import sys, glob, os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CACHE = os.path.join(os.environ.get("SCRATCH", HERE), "btc_1m.pkl")


def load_1m():
    if os.path.exists(CACHE): return pd.read_pickle(CACHE)
    fs = sorted(glob.glob(os.path.join(ROOT, "data", "BTCUSD_spot_1min_20*.csv")))
    d = pd.concat([pd.read_csv(f) for f in fs]).drop_duplicates(["date", "time"])
    ct = pd.to_datetime(d.date.astype(str)) + pd.to_timedelta(d.time // 100, "h") + pd.to_timedelta(d.time % 100, "m")
    ct = pd.DatetimeIndex(ct).tz_localize("America/Chicago", ambiguous=True, nonexistent="NaT")
    d.index = ct.tz_convert("UTC").tz_localize(None) - pd.Timedelta(minutes=1)      # UTC bar OPEN time
    d = d[d.index.notna()]; d = d[~d.index.duplicated()].sort_index()[["open", "high", "low", "close"]]
    d.to_pickle(CACHE); return d


def resample(m, rule):
    return m.resample(rule, label="left", closed="left").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()


def wilder(x, n): return pd.Series(np.asarray(x, float)).ewm(alpha=1 / n, adjust=False).mean().values


def rsi(c, n=14):
    d = c.diff().fillna(0); up = wilder(d.clip(lower=0), n); dn = wilder((-d).clip(lower=0), n)
    return pd.Series(100 * up / (up + dn), index=c.index)


def atr(b, n=14):
    pc = b.close.shift(); tr = pd.concat([b.high - b.low, (b.high - pc).abs(), (b.low - pc).abs()], axis=1).max(axis=1)
    return pd.Series(wilder(tr, n), index=b.index)


def adx(b, n=14):
    up = b.high.diff().fillna(0).values; dn = (-b.low.diff()).fillna(0).values
    pdm = np.where((up > dn) & (up > 0), up, 0.0); ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
    a = atr(b, n).values
    pdi = 100 * wilder(pdm, n) / a; ndi = 100 * wilder(ndm, n) / a
    dx = np.nan_to_num(100 * np.abs(pdi - ndi) / (pdi + ndi))
    return pd.Series(wilder(dx, n), index=b.index)


def cmo(c, n=14, kind="wilder"):
    if kind == "wilder": return 2 * rsi(c, n) - 100            # talib CMO (Wilder-smoothed gains / losses)
    d = c.diff(); su = d.clip(lower=0).rolling(n).sum(); sd = (-d).clip(lower=0).rolling(n).sum()
    return 100 * (su - sd) / (su + sd)                          # textbook Chande (simple sums)


def srsi_k(c, n=14, ns=14, k=3):
    r = rsi(c, n); lo = r.rolling(ns).min(); hi = r.rolling(ns).max()
    return (100 * (r - lo) / (hi - lo)).rolling(k).mean()


def smma(c, n): return pd.Series(wilder(c.values, n), index=c.index)


def alligator(c):
    return smma(c, 13).shift(8), smma(c, 8).shift(5), smma(c, 5).shift(3)   # jaw, teeth, lips


def build(m, ema_n=50, cmo_kind="simple", h4_alli_lag=0, h4_ema_mode="forming"):
    b = resample(m, "30min"); h = resample(m, "4h")
    f = pd.DataFrame(index=b.index); f["close"] = b.close
    f["adx"] = adx(b); f["atr"] = atr(b); f["cmo"] = cmo(b.close, 14, cmo_kind); f["k"] = srsi_k(b.close)
    f["jaw"], f["teeth"], f["lips"] = alligator(b.close)
    hj, ht, hl = alligator(h.close); he = h.close.ewm(span=ema_n, adjust=False).mean()
    H = pd.DataFrame({"hj": hj, "ht": ht, "hl": hl, "he": he})
    bucket = f.index.floor("4h"); closes_4h = (f.index + pd.Timedelta(minutes=30)) == bucket + pd.Timedelta(hours=4)
    hpos = H.index.get_indexer(bucket)
    last_done = np.where(closes_4h, hpos, hpos - 1)   # last COMPLETED 4h candle at this 30m close
    ia = last_done - h4_alli_lag
    for c_ in ("hj", "ht", "hl"): f[c_] = np.where(ia >= 0, H[c_].values[np.clip(ia, 0, len(H) - 1)], np.nan)
    prev = hpos - 1                                   # 4h candle before the forming one
    pe = np.where(prev >= 0, H.he.values[np.clip(prev, 0, None)], np.nan); a = 2 / (ema_n + 1)
    if h4_ema_mode == "forming": f["he"] = pe * (1 - a) + a * f.close.values
    elif h4_ema_mode == "completed": f["he"] = np.where(last_done >= 0, H.he.values[np.clip(last_done, 0, None)], np.nan)
    elif h4_ema_mode == "completed_lag1": f["he"] = np.where(last_done >= 1, H.he.values[np.clip(last_done - 1, 0, None)], np.nan)
    elif h4_ema_mode == "LEAK_final":                 # deliberate leak: the forming 4h candle FINAL close
        f["he"] = H.he.values[hpos]
    return f


def signals(f, adx_t=40, cmo_t=20, k_lo=20):
    c = f.close
    L = (c > f.lips) & (f.lips > f.teeth) & (f.teeth > f.jaw) & (f.hl > f.ht) & (f.ht > f.hj) & (f.adx > adx_t) & (c > f.he) & (f.cmo > cmo_t) & (f.k < k_lo)
    S = (c < f.lips) & (f.lips < f.teeth) & (f.teeth < f.jaw) & (f.hl < f.ht) & (f.ht < f.hj) & (f.adx > adx_t) & (c < f.he) & (f.cmo < -cmo_t) & (f.k > 100 - k_lo)
    return np.where(L, 1, np.where(S, -1, 0))


FEE, SLIP = 0.0005, 0.0002


def walk(O, Hh, Ll, i0, side, stop, tgt):
    """first exit from minute index i0 on: stop before target inside a minute; stop at its price or the open if gapped."""
    n = len(O); j = i0; step = 4000
    while j < n:
        o, hh, ll = O[j:j + step], Hh[j:j + step], Ll[j:j + step]
        if side == 1: hs = ll <= stop; ht = hh >= tgt
        else: hs = hh >= stop; ht = ll <= tgt
        any_ = hs | ht
        if any_.any():
            q = int(np.argmax(any_)); jj = j + q
            if hs[q]:
                px = min(o[q], stop) if side == 1 else max(o[q], stop); return jj, px, "stop"
            return jj, tgt, "target"
        j += step
    return None


def run(m, f, sig, stop_m=3.0, tgt_m=2.0, allow_exit_candle=True, rng=None, start="2018-06-01", delay_bars=0):
    O, Hh, Ll = m.open.values, m.high.values, m.low.values; mt = m.index.values
    ft = f.index.values; close = f.close.values; A = f.atr.values; out = []; free_from = np.datetime64(start)
    for i in np.where(sig != 0)[0]:
        if ft[i] < free_from: continue
        side = int(sig[i]) if rng is None else int(rng.choice([-1, 1]))
        k = i + delay_bars
        if k >= len(ft): break
        e = close[k]; a = A[i]
        if not np.isfinite(a) or a <= 0: continue
        stop = e - side * stop_m * a; tgt = e + side * tgt_m * a
        ent_close = ft[k] + np.timedelta64(30, "m")
        i0 = np.searchsorted(mt, ent_close)            # first minute starting at / after the 30m close
        r = walk(O, Hh, Ll, i0, side, stop, tgt)
        if r is None: break
        jj, px, why = r
        net = side * (px - e) / e - (FEE + SLIP) - ((FEE + SLIP) if why == "stop" else FEE)
        tx = pd.Timestamp(mt[jj]).floor("30min")
        out.append(dict(date=pd.Timestamp(ft[i]).strftime("%Y-%m-%d"), side=side, net=net, t=pd.Timestamp(ft[i]), tx=tx, why=why,
                        e=e, x=px, R=stop_m * a / e, entry_time=pd.Timestamp(ent_close), exit_time=pd.Timestamp(mt[jj]) + pd.Timedelta(minutes=1)))
        free_from = (tx + pd.Timedelta(minutes=0 if allow_exit_candle else 30)).to_datetime64()
    return pd.DataFrame(out)


def tstat(x): x = pd.Series(x); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def summ(T, name=""):
    if len(T) < 3: return f"{name:40s} n {len(T)}"
    x = T.net; pf = x[x > 0].sum() / -x[x < 0].sum()
    return f"{name:40s} n {len(T):4d} win {np.mean(x > 0):.0%} mean {x.mean():+.4%} PF {pf:.2f} t {tstat(x):+.2f}"


if __name__ == "__main__":
    m = load_1m(); f = build(m); sig = signals(f); T = run(m, f, sig)
    T.drop(columns=["entry_time", "exit_time", "x"]).to_csv(os.path.join(HERE, "trades_replica_out.csv.txt"), index=False)
    T.to_pickle(os.path.join(os.environ.get("SCRATCH", HERE), "replica_T.pkl"))
    print(summ(T, "replica"))
