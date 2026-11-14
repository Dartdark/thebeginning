"""Checker replica of the BTC ADX ensemble, written from spec.md alone (no maker code read).
python3 checks/candidates/btc_adx_ensemble/replica.py   -> trades_replica.csv (base) ; import run() for variants."""
import os, sys, glob, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CACHE = os.path.join(os.environ.get("BTC_CACHE", HERE), "_btc15.pkl")


def load_1m():
    fs = sorted(glob.glob(os.path.join(ROOT, "data", "BTCUSD_spot_1min_20*.csv")))
    d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    d = d.drop_duplicates(["date", "time"], keep="first").reset_index(drop=True)
    ct = pd.to_datetime(d.date.astype(str)) + pd.to_timedelta(d.time // 100, "h") + pd.to_timedelta(d.time % 100, "m")
    # CT bar-CLOSE stamps -> UTC. Fall-back hour appears once only after de-dup (CSV has one row per stamp); treat as CDT.
    loc = ct.dt.tz_localize("America/Chicago", ambiguous=np.ones(len(ct), bool), nonexistent="shift_forward")
    utc = loc.dt.tz_convert("UTC").dt.tz_localize(None) - pd.Timedelta(minutes=1)   # bar OPEN time
    d.index = utc
    d = d[~d.index.duplicated()].sort_index()
    return d[["open", "high", "low", "close"]]


def candles(m, rule):
    c = m.resample(rule, label="left", closed="left").agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    return c.dropna()


def get_data():
    if os.path.exists(CACHE): return pd.read_pickle(CACHE)
    m = load_1m(); D = {k: candles(m, r) for k, r in (("m15", "15min"), ("h1", "1h"), ("h4", "4h"))}
    D["m1"] = m
    pd.to_pickle(D, CACHE); return D


# ---------------- indicators (TA-Lib style Wilder seeding) ----------------
def tr_arr(h, l, c):
    tr = np.full(len(c), np.nan)
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1])))
    return tr


def atr_talib(h, l, c, n):
    tr = tr_arr(h, l, c); out = np.full(len(c), np.nan)
    if len(c) <= n: return out
    out[n] = tr[1:n + 1].mean()
    for i in range(n + 1, len(c)): out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def adx_talib(h, l, c, n):
    N = len(c); out = np.full(N, np.nan); tr = tr_arr(h, l, c)
    pdm = np.zeros(N); mdm = np.zeros(N)
    up = h[1:] - h[:-1]; dn = l[:-1] - l[1:]
    pdm[1:] = np.where((up > 0) & (up > dn), up, 0.0); mdm[1:] = np.where((dn > 0) & (dn > up), dn, 0.0)
    sp, sm, st = pdm[1:n].sum(), mdm[1:n].sum(), tr[1:n].sum()       # n-1 values (TA-Lib)
    dxs = []; adx = np.nan
    for i in range(n, N):
        sp = sp - sp / n + pdm[i]; sm = sm - sm / n + mdm[i]; st = st - st / n + tr[i]
        pdi = 100 * sp / st if st else 0.0; mdi = 100 * sm / st if st else 0.0
        dx = 100 * abs(pdi - mdi) / (pdi + mdi) if (pdi + mdi) else 0.0
        if len(dxs) < n:
            dxs.append(dx)
            if len(dxs) == n: adx = np.mean(dxs); out[i] = adx
        else:
            adx = (adx * (n - 1) + dx) / n; out[i] = adx
    return out


def adx_ewm(h, l, c, n):
    """independent alternative: pandas ewm(alpha=1/n, adjust=False), no SMA seeding"""
    tr = pd.Series(tr_arr(h, l, c)); up = np.r_[np.nan, h[1:] - h[:-1]]; dn = np.r_[np.nan, l[:-1] - l[1:]]
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0)); mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0))
    a = 1 / n
    s = lambda x: x.iloc[1:].ewm(alpha=a, adjust=False).mean().reindex(x.index)
    atr = s(tr); pdi = 100 * s(pdm) / atr; mdi = 100 * s(mdm) / atr
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi)
    return dx.ewm(alpha=a, adjust=False).mean().to_numpy()


def adx_sma(h, l, c, n):
    """non-Wilder variant (simple rolling means) to show sensitivity to the ADX definition"""
    tr = pd.Series(tr_arr(h, l, c)); up = np.r_[np.nan, h[1:] - h[:-1]]; dn = np.r_[np.nan, l[:-1] - l[1:]]
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0)); mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0))
    s = lambda x: x.rolling(n).mean()
    pdi = 100 * s(pdm) / s(tr); mdi = 100 * s(mdm) / s(tr)
    return (100 * (pdi - mdi).abs() / (pdi + mdi)).rolling(n).mean().to_numpy()


def ema_talib(x, n):
    out = np.full(len(x), np.nan); k = 2 / (n + 1)
    if len(x) < n: return out
    out[n - 1] = x[:n].mean()
    for i in range(n, len(x)): out[i] = out[i - 1] + k * (x[i] - out[i - 1])
    return out


def supertrend(h, l, c, n=10, f=3.0):
    atr = atr_talib(h, l, c, n); hl2 = (h + l) / 2; ub = hl2 + f * atr; lb = hl2 - f * atr
    N = len(c); U = ub.copy(); L = lb.copy(); st = np.full(N, np.nan); dirn = np.zeros(N)
    for i in range(n + 1, N):
        U[i] = ub[i] if (ub[i] < U[i - 1] or c[i - 1] > U[i - 1]) else U[i - 1]
        L[i] = lb[i] if (lb[i] > L[i - 1] or c[i - 1] < L[i - 1]) else L[i - 1]
        if dirn[i - 1] in (0, -1): dirn[i] = 1 if c[i] > U[i] else -1
        else: dirn[i] = -1 if c[i] < L[i] else 1
        st[i] = L[i] if dirn[i] == 1 else U[i]
    return st


def bbw(c, n=20, k=2.0):
    s = pd.Series(c); m = s.rolling(n).mean(); sd = s.rolling(n).std(ddof=0)
    return (100 * (2 * k * sd) / m).to_numpy()


_IND = {}


def h1_ind(h1, adx_fn):
    if adx_fn not in _IND:
        H, L, C = (h1[k].to_numpy() for k in ("high", "low", "close"))
        f = {"talib": adx_talib, "ewm": adx_ewm, "sma": adx_sma}[adx_fn]
        _IND[adx_fn] = pd.DataFrame({"adx": f(H, L, C, 14), "atr": atr_talib(H, L, C, 14), "st": supertrend(H, L, C),
                                     "bbw": bbw(C)}, index=h1.index)
    return _IND[adx_fn]


# ---------------- backtest ----------------
def run(D, levels=(40, 50), stop_atr=2.5, tp_atr=8.0, half_atr=1.5, max_h=240, ema_shift=0, vol_shift=0, h1_shift=0,
        fill="close", entry_delay=0, adx_fn="talib", no_adx=False, cost=0.0007, guard=True, start="2018-01-01",
        adverse=0.0005, adx_roll=0):
    m15, h1, h4 = D["m15"], D["h1"], D["h4"]
    ind = h1_ind(h1, adx_fn).shift(h1_shift)
    if adx_roll:  # placebo: ADX series rotated in time (keeps its distribution and persistence, breaks the alignment)
        ind = ind.copy(); ind['adx'] = np.roll(ind.adx.to_numpy(), adx_roll)   # +1: one candle older ; -1: the NEXT, unclosed candle (a planted leak)
    e4 = pd.Series(ema_talib(h4.close.to_numpy(), 200), index=h4.index + pd.Timedelta(hours=4))   # keyed by CLOSE time
    e4 = e4.shift(ema_shift)    # +1 one more 4h candle of lag ; -1 the 4h candle still forming (its final value: leak)
    d16 = h4[h4.index.hour == 16].close; d16.index = d16.index + pd.Timedelta(hours=4)              # known at 20:00 UTC
    lr = np.log(d16).diff().to_numpy(); vrv = np.full(len(d16), np.nan)
    for i in range(len(d16)):
        if i + 1 < 62: continue
        r = lr[max(1, i - 119):i + 1]; r20 = lr[i - 19:i + 1]
        vrv[i] = np.std(r20, ddof=1) / np.std(r, ddof=1)
    vr = pd.Series(vrv, index=d16.index).shift(vol_shift)
    t15 = m15.index; close_t = t15 + pd.Timedelta(minutes=15)
    o, hi, lo, cl = (m15[k].to_numpy() for k in ("open", "high", "low", "close"))
    ffill_at = lambda s: s.reindex(s.index.union(close_t)).ffill().reindex(close_t).to_numpy()
    ema_at = ffill_at(e4); vr_at = ffill_at(vr)
    A = ind.reindex(t15 - pd.Timedelta(minutes=45)).to_numpy()
    is_hr = (t15.minute == 45)
    ct_ns = ((close_t - close_t[0]) / pd.Timedelta(hours=1)).to_numpy(); maxns = max_h
    books = {lv: None for lv in levels}; out = []; pend = []

    def close_book(lv, i, px, why):
        b = books[lv]
        b["ret"] += b["rem"] * (b["side"] * (px - b["e"]) / b["e"] - cost)
        out.append(dict(t=t15[b["i"]], tx=t15[i], side=b["side"], book=lv, why=why, R=b["R"], entry=b["e"], exit=px,
                        net=b["ret"] / b["R"], half=b["half"]))
        books[lv] = None

    def open_book(lv, i, s, atr):
        e = cl[i]
        books[lv] = dict(i=i, side=s, e=e, atr=atr, stop=e - s * stop_atr * atr, R=stop_atr * atr / e, ret=-cost, rem=1.0,
                         half=False)
    i0 = np.searchsorted(t15, pd.Timestamp(start))
    for i in range(i0, len(t15)):
        op = [lv for lv in levels if books[lv] is not None and books[lv]["i"] < i]
        if guard and op:
            s = books[op[0]]["side"]
            g = (min(books[lv]["stop"] for lv in op) * 0.99) if s == 1 else (max(books[lv]["stop"] for lv in op) * 1.01)
            if (s == 1 and lo[i] <= g) or (s == -1 and hi[i] >= g):
                px = g if fill == "close" else ((min(o[i], g) if s == 1 else max(o[i], g)) * (1 - s * adverse))
                for lv in op: close_book(lv, i, px, "guard")
                op = []
        for lv in op:
            b = books[lv]; s = b["side"]; a = b["atr"]
            stp = b["stop"]; tp = b["e"] + s * tp_atr * a; hf = b["e"] + s * half_atr * a
            if (s == 1 and lo[i] <= stp) or (s == -1 and hi[i] >= stp):
                px = cl[i] if fill == "close" else (min(o[i], stp) if s == 1 else max(o[i], stp)) * (1 - s * adverse)
                close_book(lv, i, px, "stop"); continue
            if (s == 1 and hi[i] >= tp) or (s == -1 and lo[i] <= tp):
                close_book(lv, i, cl[i] if fill == "close" else tp, "tp"); continue
            if not b["half"] and ((s == 1 and hi[i] >= hf) or (s == -1 and lo[i] <= hf)):
                px = cl[i] if fill == "close" else hf
                b["ret"] += 0.5 * (s * (px - b["e"]) / b["e"] - cost); b["rem"] = 0.5; b["half"] = True
            if ct_ns[i] - ct_ns[b["i"]] >= maxns:
                close_book(lv, i, cl[i], "time"); continue
            if is_hr[i] and not np.isnan(ema_at[i]) and (cl[i] - ema_at[i]) * s < 0:
                close_book(lv, i, cl[i], "ema"); continue
        if pend:
            for (lv, s, atr, k) in [p for p in pend if p[3] == i]:
                oth = [books[o_]["side"] for o_ in levels if o_ != lv and books[o_] is not None]
                if books[lv] is None and not (oth and oth[0] != s): open_book(lv, i, s, atr)
            pend = [p for p in pend if p[3] > i]
        if not is_hr[i]: continue
        adx, atr, st, bw = A[i]; ema = ema_at[i]
        if np.isnan(atr) or np.isnan(ema) or np.isnan(st) or np.isnan(bw) or np.isnan(adx): continue
        c = cl[i]; s = 1 if c > ema else -1
        if not ((c - st) * s > 0 and bw < 15 and (np.isnan(vr_at[i]) or vr_at[i] < 1.5)): continue
        for lv in levels:
            if books[lv] is not None or any(p[0] == lv for p in pend): continue
            if not no_adx and not adx > lv: continue
            oth = [books[o_]["side"] for o_ in levels if o_ != lv and books[o_] is not None]
            if oth and oth[0] != s: continue
            if entry_delay: pend.append((lv, s, atr, i + entry_delay)); continue
            open_book(lv, i, s, atr)
    T = pd.DataFrame(out)
    if len(T): T.insert(0, "date", T.t.dt.normalize()); T = T.sort_values(["t", "book"]).reset_index(drop=True)
    return T


if __name__ == "__main__":
    D = get_data(); T = run(D)
    T[["date", "side", "net", "t", "tx", "book", "why", "R"]].to_csv(os.path.join(HERE, "trades_replica.csv"), index=False)
    print(len(T), round(T.net.mean(), 3), round((T.net > 0).mean(), 3))
