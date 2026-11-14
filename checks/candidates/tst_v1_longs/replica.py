"""Checker replica of TrendSwingTrader V1 longs (BTC 4h), written from spec.md only.
python3 checks/candidates/tst_v1_longs/replica.py  (run from repo root)"""
import os, glob, sys, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.environ.get("BTC_CACHE", os.path.join(os.environ.get("TEMP", "/tmp"), "btc_spot_1m_utc.pkl"))
FEE, SLIP = 0.0005, 0.0002


def load_1m():
    if os.path.exists(CACHE): return pd.read_pickle(CACHE)
    fs = sorted(glob.glob("data/BTCUSD_spot_1min_20*.csv"))
    d = pd.concat([pd.read_csv(f) for f in fs]).drop_duplicates(["date", "time"])
    loc = pd.to_datetime(d.date.astype(str)) + pd.to_timedelta(d.time // 100, "h") + pd.to_timedelta(d.time % 100, "m")
    ct = pd.DatetimeIndex(loc).tz_localize("America/Chicago", ambiguous=np.ones(len(d), bool), nonexistent="shift_forward")
    d.index = (ct.tz_convert("UTC").tz_localize(None) - pd.Timedelta(minutes=1))     # UTC bar-open
    d.index.name = "t"; d["ct_end"] = loc.values
    d = d[~d.index.duplicated()].sort_index()[["open", "high", "low", "close", "ct_end"]]
    d.to_pickle(CACHE); return d


def bars4h(m):
    b = m[["open", "high", "low", "close"]].resample("4h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    return b


def ema(x, n):   # talib style: SMA seed
    x = np.asarray(x, float); out = np.full(len(x), np.nan); a = 2 / (n + 1)
    out[n - 1] = x[:n].mean()
    for i in range(n, len(x)): out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def wilder(x, n, seed_sum=False):
    x = np.asarray(x, float); out = np.full(len(x), np.nan)
    st = np.argmax(~np.isnan(x)); out[st + n - 1] = np.nanmean(x[st:st + n])
    for i in range(st + n, len(x)): out[i] = (out[i - 1] * (n - 1) + x[i]) / n
    return out


def atr_adx(b, n=14):
    h, l, c = b.high.values, b.low.values, b.close.values; pc = np.r_[np.nan, c[:-1]]
    tr = np.nanmax(np.c_[h - l, np.abs(h - pc), np.abs(l - pc)], axis=1); tr[0] = h[0] - l[0]
    atr = wilder(tr, n)
    up = h - np.r_[np.nan, h[:-1]]; dn = np.r_[np.nan, l[:-1]] - l
    pdm = np.where((up > dn) & (up > 0), up, 0.0); mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    pdm[0] = mdm[0] = np.nan; tr1 = tr.copy(); tr1[0] = np.nan
    s_tr, s_p, s_m = wilder(tr1, n), wilder(pdm, n), wilder(mdm, n)
    pdi, mdi = 100 * s_p / s_tr, 100 * s_m / s_tr
    dx = 100 * np.abs(pdi - mdi) / (pdi + mdi)
    return atr, wilder(dx, n)


class Sim:
    def __init__(self, m, b):
        self.m, self.b = m, b
        self.mt = m.index.values; self.mo, self.mh, self.ml, self.mc = (m[k].values for k in ("open", "high", "low", "close"))
        bt = b.index.values
        self.i0 = np.searchsorted(self.mt, bt); self.i1 = np.searchsorted(self.mt, bt + np.timedelta64(240, "m"))
        self.bc = b.close.values; self.cache = {}

    def ind(self, n14=14, emas=(21, 50, 100)):
        k = (n14, emas)
        if k not in self.cache:
            atr, adx = atr_adx(self.b, n14); self.cache[k] = (atr, adx, [ema(self.b.close.values, e) for e in emas])
        return self.cache[k]

    def signal(self, adx_min=25, emas=(21, 50, 100), use_ema=True, use_adx=True):
        atr, adx, (ef, em, es) = self.ind(14, emas); c = self.bc
        s = np.ones(len(c), bool)
        if use_ema: s &= (es < em) & (em < ef) & (ef < c)
        if use_adx: s &= adx > adx_min
        s &= ~np.isnan(atr) & ~np.isnan(es)
        return s, atr

    def trade(self, j, atr, k_stop=2.0, k_half=3.0, k_trail=2.0, ratchet=False, entry_px=None, start_min=None):
        """long entered at close of 4h bar j. returns dict or None if still open at data end."""
        mo, mh, ml = self.mo, self.mh, self.ml
        E = self.bc[j] if entry_px is None else entry_px; a = atr[j]
        stop, tgt, half = E - k_stop * a, E + k_half * a, False; legs = []; t_half = None
        bj = j
        first = self.i1[j] if start_min is None else start_min
        while True:
            bj += 1
            if bj >= len(self.bc): return None
            lo_i, hi_i = max(self.i0[bj], first), self.i1[bj]
            if hi_i > lo_i:
                L, H = ml[lo_i:hi_i], mh[lo_i:hi_i]
                if not half:
                    sh = np.flatnonzero(L <= stop); th = np.flatnonzero(H >= tgt)
                    s0 = sh[0] if len(sh) else 10**9; t0 = th[0] if len(th) else 10**9
                    if s0 <= t0 and s0 < 10**9:
                        px = min(stop, mo[lo_i + s0]); legs = [(1.0, px, True)]; xi = lo_i + s0; break
                    if t0 < 10**9:
                        half = True; legs.append((0.5, tgt, False)); t_half = lo_i + t0; stop = E
                        L2 = L[t0 + 1:]; sh = np.flatnonzero(L2 <= stop)
                        if len(sh):
                            xi = lo_i + t0 + 1 + sh[0]; legs.append((0.5, min(stop, mo[xi]), True)); break
                else:
                    sh = np.flatnonzero(L <= stop)
                    if len(sh):
                        xi = lo_i + sh[0]; legs.append((0.5, min(stop, mo[xi]), True)); break
            if half:
                ns = max(self.bc[bj] - k_trail * atr[bj], E)
                stop = max(stop, ns) if ratchet else ns
        Ee = E * (1 + SLIP); net = 0.0
        for w, px, mkt in legs:
            xe = px * (1 - SLIP) if mkt else px
            net += w * ((xe - Ee) / E - FEE * Ee / E - FEE * xe / E)
        return dict(j=j, bx=bj, xi=xi, net=net, half=half, entry=E, exit=legs[-1][1], ih=t_half)

    def run(self, sig, atr, start="2018-06-01", reentry_same_bar=True, **kw):
        out = []; j = int(np.searchsorted(self.b.index.values, np.datetime64(start))); n = len(self.bc)
        while j < n:
            if sig[j]:
                r = self.trade(j, atr, **kw)
                if r is None: break
                out.append(r); j = r["bx"] if reentry_same_bar else r["bx"] + 1
                continue
            j += 1
        return self.frame(out)

    def frame(self, out):
        T = pd.DataFrame(out)
        if not len(T): return T
        T["t"] = self.b.index[T.j]; T["tx"] = self.b.index[T.bx]; T["date"] = T.t.dt.normalize(); T["side"] = 1
        return T


def main():
    m = load_1m(); b = bars4h(m); S = Sim(m, b)
    sig, atr = S.signal(); T = S.run(sig, atr)
    T[["date", "side", "net", "t", "tx", "entry", "exit", "half"]].to_csv(os.path.join(HERE, "trades_replica_base.csv"), index=False)
    print(len(T), T.net.mean(), T.net.mean() / T.net.std() * np.sqrt(len(T)))
    return S, T


if __name__ == "__main__":
    main()
