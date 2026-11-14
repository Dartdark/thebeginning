"""BTC ADX ensemble (user's Jesse strategy 'BTCAdxEnsembleFree', pasted 2026-11-13): Python port on Coinbase spot BTC-USD 1-min
(data/BTCUSD_spot_1min_*, Central time stamped at the close -> converted to UTC bar-open times, as Jesse's candles).
Rule as coded: on each closed 1h candle, side = +1 if close > 4h EMA(200) (last completed 4h candle) AND close > SuperTrend(10, 3)
(mirror for -1), Bollinger(20, 2) width < 15%, daily (4h candle opening 16:00 UTC) 20-day / 120-day return-vol ratio < 1.5.
Two books (ADX(14) > 40, > 50) open at the 1h close when empty and not against the net side; each book: stop 2.5 ATR(14),
half off at 1.5 ATR, rest at 8 ATR, out after 240 h or at an hour end with close on the other side of the 4h EMA. Book exits are
checked on every 15m candle (high / low) and filled at that 15m close (the code changes the wanted size; Jesse trades it at the
close); a real guard stop 1% beyond the farthest book stop fills at its price and empties every book. Risk 3% of the account per
book at the stop. Costs: 0.05% fee + 0.02% slippage per side on every fill (the code's own fee_rate is exchange-set; not included
by us beyond this).
Not modelled: the 2% rebalance tolerance, leverage / liquidation, compounding interaction of the two books (each book trade is
scored in R; account % = 3% x R).
  tools/run_stamped.sh analysis/btc_adx_ensemble_test.py > analysis/outputs/btc_adx_ensemble_test_output.txt
"""
import sys, glob, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from metrics import t_threshold

COST = 0.0007
print(__doc__.split("\n")[0])


def load():
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/BTCUSD_spot_1min_*.csv"))])
    ts = pd.to_datetime(d.date.astype(str) + d.time.astype(str).str.zfill(4), format="%Y%m%d%H%M")
    ts = ts.dt.tz_localize("America/Chicago", ambiguous="NaT", nonexistent="NaT")
    d = d.assign(ts=ts - pd.Timedelta(minutes=1)).dropna(subset=["ts"])
    d["ts"] = d.ts.dt.tz_convert("UTC").dt.tz_localize(None)
    return d.drop_duplicates("ts").set_index("ts").sort_index()[["open", "high", "low", "close"]]


def rs(m, rule):
    return m.resample(rule, label="left", closed="left").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()


def rma(x, n):
    out = np.full(len(x), np.nan); s = np.nan
    for i, v in enumerate(x):
        if np.isnan(v): continue
        s = v if np.isnan(s) else s + (v - s) / n
        out[i] = s
    return out


def wilder_sum_init(x, n):
    """TA-Lib style Wilder smoothing (seeded with the mean of the first n)"""
    out = np.full(len(x), np.nan)
    if len(x) <= n: return out
    s = np.nanmean(x[1:n + 1]); out[n] = s
    for i in range(n + 1, len(x)):
        s = s + (x[i] - s) / n; out[i] = s
    return out


def indicators(h1):
    H, L, C = h1.high.to_numpy(), h1.low.to_numpy(), h1.close.to_numpy()
    pc = np.r_[np.nan, C[:-1]]
    tr = np.nanmax(np.c_[H - L, np.abs(H - pc), np.abs(L - pc)], axis=1); tr[0] = H[0] - L[0]
    atr14 = wilder_sum_init(tr, 14)
    up = H - np.r_[np.nan, H[:-1]]; dn = np.r_[np.nan, L[:-1]] - L
    pdm = np.where((up > dn) & (up > 0), up, 0.0); ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
    a = wilder_sum_init(tr, 14); p = wilder_sum_init(pdm, 14); q = wilder_sum_init(ndm, 14)
    pdi = 100 * p / a; ndi = 100 * q / a
    dx = 100 * np.abs(pdi - ndi) / (pdi + ndi)
    adx = np.full(len(C), np.nan)
    # ADX = Wilder average of DX, seeded with the mean of the first 14 DX values
    first = 14; s = np.nan
    for i in range(first, len(C)):
        if i < first + 13: continue
        if np.isnan(s): s = np.nanmean(dx[first:first + 14]); adx[i] = s; continue
        s = s + (dx[i] - s) / 14; adx[i] = s
    # SuperTrend(10, 3) on hl2 with ATR(10)
    atr10 = wilder_sum_init(tr, 10); hl2 = (H + L) / 2
    ub = hl2 + 3 * atr10; lb = hl2 - 3 * atr10; st = np.full(len(C), np.nan); fu = ub.copy(); fl = lb.copy(); trend_up = True
    for i in range(1, len(C)):
        if np.isnan(atr10[i]): continue
        if not np.isnan(fu[i - 1]):
            fu[i] = ub[i] if (ub[i] < fu[i - 1] or C[i - 1] > fu[i - 1]) else fu[i - 1]
            fl[i] = lb[i] if (lb[i] > fl[i - 1] or C[i - 1] < fl[i - 1]) else fl[i - 1]
        if trend_up and C[i] < fl[i]: trend_up = False
        elif not trend_up and C[i] > fu[i]: trend_up = True
        st[i] = fl[i] if trend_up else fu[i]
    sma = pd.Series(C).rolling(20).mean().to_numpy(); sd = pd.Series(C).rolling(20).std(ddof=0).to_numpy()
    bbw = 100 * 4 * sd / sma
    return adx, atr14, st, bbw


def setup():
    m = load(); m15 = rs(m, "15min"); h1 = rs(m, "1h"); h4 = rs(m, "4h")
    adx, atr, st, bbw = indicators(h1)
    ema = h4.close.ewm(span=200, adjust=False).mean().to_numpy().copy(); ema[:199] = np.nan
    t4 = h4.index.to_numpy()
    d4 = h4[h4.index.hour == 16].close
    lr = np.log(d4).diff()
    vr = (lr.rolling(20).std() / lr.rolling(120).std()).to_numpy()   # last 120 returns of 121 closes
    td = d4.index.to_numpy()
    H1 = pd.DataFrame({"adx": adx, "atr": atr, "st": st, "bbw": bbw, "close": h1.close.to_numpy()}, index=h1.index)
    return m15, H1, ema, t4, vr, td


def run(ctx, gates=("adx", "bbw", "vol", "st"), books=(40, 50), side_override=None, seed=None):
    m15, H1, ema, t4, vr, td = ctx
    rng = np.random.default_rng(seed) if seed is not None else None
    T = m15.index.to_numpy(); Hh, Ll, Cc = (m15[k].to_numpy() for k in ("high", "low", "close"))
    h1i = {t: i for i, t in enumerate(H1.index.to_numpy())}
    A = H1.to_numpy(); hour = np.timedelta64(1, "h")
    b = [None] * len(books); out = []
    def close_book(i, px, t, why):
        k = b[i]; s = k["s"]; r = s * (px - k["e"]) / k["e"]
        pnl = k["q"] * r + (0.5 * k["pr"] if k["half"] else 0.0) - COST * (1 + k["q"]) - (COST * 0.5 if k["half"] else 0.0)
        out.append((k["t"], t, s, books[i], pnl, k["R"], why)); b[i] = None
    for j in range(len(T)):
        t, h, l, c = T[j], Hh[j], Ll[j], Cc[j]
        he = (pd.Timestamp(t).minute == 45)
        i4 = np.searchsorted(t4, t + np.timedelta64(15, "m") - np.timedelta64(4, "h"), side="right") - 1
        e4 = ema[i4] if i4 >= 0 else np.nan
        lt = (1 if c > e4 else -1) if (he and not np.isnan(e4)) else 0
        # guard stop: 1% beyond the farthest open book stop
        open_ = [k for k in b if k]
        if open_:
            s = open_[0]["s"]; g = min(k["stop"] for k in open_) * 0.99 if s == 1 else max(k["stop"] for k in open_) * 1.01
            if (s == 1 and l <= g) or (s == -1 and h >= g):
                for i in range(len(b)):
                    if b[i]: close_book(i, g, t, "guard")
                continue
        for i, k in enumerate(b):
            if k is None: continue
            s = k["s"]
            if (s == 1 and l <= k["stop"]) or (s == -1 and h >= k["stop"]): close_book(i, c, t, "stop"); continue
            if (s == 1 and h >= k["tp"]) or (s == -1 and l <= k["tp"]): close_book(i, c, t, "tp"); continue
            if not k["half"] and ((s == 1 and h >= k["pt"]) or (s == -1 and l <= k["pt"])):
                k["half"] = True; k["pr"] = s * (c - k["e"]) / k["e"]; k["q"] = 0.5
            if (t - k["t"]) >= 240 * hour or (he and lt == -s): close_book(i, c, t, "time" if lt != -s else "ema")
        if not he: continue
        ih = h1i.get(t - np.timedelta64(45, "m"))
        if ih is None or ih < 60 or np.isnan(e4): continue
        adx, atr, st, bbw, cl = A[ih]
        if np.isnan(adx) or np.isnan(atr) or np.isnan(st): continue
        side = lt
        if "st" in gates and (1 if c > st else -1) != lt: side = 0
        if "bbw" in gates and bbw >= 15.0: side = 0
        if side and "vol" in gates:
            iv = np.searchsorted(td, t + np.timedelta64(15, "m") - np.timedelta64(4, "h"), side="right") - 1
            if iv >= 0 and not np.isnan(vr[iv]) and vr[iv] >= 1.5: side = 0
        if not side: continue
        if rng is not None: side = int(rng.choice([-1, 1]))
        net = sum(k["s"] for k in b if k)
        if net * side < 0: continue
        for i, lvl in enumerate(books):
            if b[i] is None and ("adx" not in gates or adx > lvl):
                R = 2.5 * atr / c
                b[i] = {"s": side, "e": c, "stop": c - side * 2.5 * atr, "pt": c + side * 1.5 * atr, "tp": c + side * 8 * atr,
                        "half": False, "q": 1.0, "pr": 0.0, "t": t, "R": R}
    d = pd.DataFrame(out, columns=["t", "tx", "side", "book", "ret", "R", "why"])
    d["r"] = d.ret / d.R; d["yr"] = pd.DatetimeIndex(d.t).year
    return d


def stats(d, nm):
    x = d.r
    if len(x) < 2: print(f"{nm:<34} n {len(x)}"); return
    pf = x[x > 0].sum() / -x[x < 0].sum(); t = x.mean() / x.std(ddof=1) * np.sqrt(len(x))
    a = d.r[d.yr <= 2022]; z = d.r[d.yr >= 2023]
    ta_ = a.mean() / a.std(ddof=1) * np.sqrt(len(a)) if len(a) > 2 else np.nan
    tz = z.mean() / z.std(ddof=1) * np.sqrt(len(z)) if len(z) > 2 else np.nan
    print(f"{nm:<34} n {len(x):4d} win {np.mean(x > 0):5.1%} mean {x.mean():+.3f}R PF {pf:4.2f} t {t:5.2f} | 2018-22 {a.mean():+.3f}R t {ta_:5.2f} "
          f"| 2023+ {z.mean():+.3f}R t {tz:5.2f} | acct %/yr {3 * x.sum() / ((d.t.max() - d.t.min()).days / 365.25):+.1f}")


if __name__ == "__main__":
    ctx = setup(); m15 = ctx[0]
    print(f"data {m15.index[0]} -> {m15.index[-1]} UTC, 15m candles {len(m15)}")
    d = run(ctx); stats(d, "AS CODED (2 books ADX 40/50)")
    print("by year (R per book trade, sum R):")
    for y, g in d.groupby("yr"): print(f"  {y}: n {len(g):3d} mean {g.r.mean():+.3f}R sum {g.r.sum():+6.2f}R win {np.mean(g.r > 0):.0%}")
    for s, nm in ((1, "longs"), (-1, "shorts")): stats(d[d.side == s], f"  {nm}")
    for bk in (40, 50): stats(d[d.book == bk], f"  book ADX>{bk}")
    print("exits:", d.why.value_counts().to_dict())
    print("\ningredient breakdown (one gate removed at a time; books 40/50 unless noted):")
    for g, nm in ((("bbw", "vol", "st"), "no ADX gate (both books always)"), (("adx", "vol", "st"), "no Bollinger width"),
                  (("adx", "bbw", "st"), "no vol-ratio filter"), (("adx", "bbw", "vol"), "no SuperTrend agreement"),
                  ((), "EMA side only")):
        stats(run(ctx, gates=g), nm)
    for bk in ((25,), (30,), (40,), (50,), (60,)): stats(run(ctx, books=bk), f"single book ADX>{bk[0]}")
    print("\nplacebo: same entry moments, random side, same exits (40 runs):")
    pm = np.array([run(ctx, seed=s).r.mean() for s in range(40)])
    print(f"  mean {pm.mean():+.3f}R, p95 {np.percentile(pm, 95):+.3f}R, real {d.r.mean():+.3f}R, p = {np.mean(pm >= d.r.mean()):.3f}")
    print(f"multiple-testing bar t_threshold(N=400) = {t_threshold(400):.2f}")
    d.assign(date=pd.DatetimeIndex(d.t).normalize().date, net=d.r).to_csv("scratch_data/btc_adx_ensemble_trades.csv", index=False)
