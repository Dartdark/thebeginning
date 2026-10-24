"""Checker replica of T_ONESIDE (+ research-note stop), built from spec.md only, on the raw 1-minute CSVs.

python3 checks/candidates/t_oneside/replica.py   (run from the repo root)
Writes in this folder: replica_trades.csv (stop at stop price, as the spec), replica_trades_gap.csv (stop fills at the
bar's open when the bar opens beyond the stop), replica_nights.csv (per-day night stats / flags).
"""
import glob, os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
COST = 17.25; PV = 20.0


def load():
    fs = sorted(glob.glob("data/NQ_1min_20*.csv")) + sorted(glob.glob("data/NQ_1min_ON_20*.csv"))
    d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True).drop_duplicates(["date", "time"])
    d = d.sort_values(["date", "time"]).reset_index(drop=True)
    d = d[d.date >= 20171201].reset_index(drop=True)   # ON data starts 2017-12-01: night volume needs it
    return d


def build(d, gap_fill=False, stop_on=True, mult=1.4, t_in=830, t_out=845, T_on='heavy', OS_on='light', kT=0.40, kOS=0.30, os_cond='full'):
    date = d.date.to_numpy(); tm = d.time.to_numpy()
    o, h, l, c, v = (d[k].to_numpy(float) for k in ("open", "high", "low", "close", "volume"))
    isday = (tm >= 830) & (tm <= 1659)
    n = len(d)
    # ---- ATRd: per date with a 15:00 bar, range of bars 08:31-15:00 ----
    rth = d[(d.time >= 831) & (d.time <= 1500)]
    g = rth.groupby("date")
    full = g.time.max().eq(1500) & g.time.min().eq(831)
    rng = (g.high.max() - g.low.min())[full]
    rng_dates = rng.index.to_numpy(); rng_vals = rng.to_numpy()

    def atrd(D):
        k = np.searchsorted(rng_dates, D)          # sessions strictly before D
        return rng_vals[k - 20:k].mean() if k >= 20 else np.nan

    # ---- nights: runs of night bars ending right before a day bar ----
    starts = np.flatnonzero(isday & ~np.r_[False, isday[:-1]])    # first day bar of each day block
    # day blocks: index ranges of consecutive day bars
    ends = np.flatnonzero(isday & ~np.r_[isday[1:], False])
    rows = []; trades = []
    bank = []                                       # volumes of valid nights (in order)
    prev_end = -1
    for s, e in zip(starts, ends):
        D = date[s]
        ns, ne = prev_end + 1, s                    # night bars [ns, ne)
        prev_end = e
        if ne - ns <= 0:
            continue
        nb = ne - ns
        nvol = v[ns:ne].sum()
        last = ne - 1                               # last night bar (should be 08:29 of D)
        ret = c[last] - o[ns]
        valid = nb >= 30
        med = np.median(bank[-20:]) if len(bank) >= 20 else np.nan
        heavy = bool(valid and len(bank) >= 20 and nvol > mult * med)
        rows.append(dict(date=D, nbars=nb, nvol=nvol, med=med, ret=ret, valid=valid, heavy=heavy,
                         first_night=f"{date[ns]}-{tm[ns]}", last_night=f"{date[last]}-{tm[last]}",
                         day_first=tm[s], day_last=tm[e]))
        if valid:
            bank.append(nvol)
        if D < 20180101 or not valid or np.isnan(med):
            continue
        A = atrd(D)
        day = slice(s, e + 1)
        dt = tm[day]; do, dh, dl, dc, dv = o[day], h[day], l[day], c[day], v[day]

        def run(side, i_in, i_out_default, dist, exit_rule=None):
            """i_in: index (within day) of entry bar; fills at its open. Returns trade dict."""
            px = do[i_in]; stop = px - side * dist if (stop_on and np.isfinite(dist)) else None
            i = i_in
            while True:
                # exit at open of bar i if scheduled
                if i == i_out_default[0]:
                    return px, do[i], "flat", i
                if stop is not None:
                    hit = (dl[i] <= stop) if side > 0 else (dh[i] >= stop)
                    if hit:
                        fill = stop
                        if gap_fill:
                            fill = min(do[i], stop) if side > 0 else max(do[i], stop)
                        return px, fill, "stop", i
                if exit_rule is not None and exit_rule(i):
                    i_out_default[0] = i + 1
                i += 1
                if i >= len(dt):
                    return px, dc[-1], "eod", i - 1

        doT = {'heavy': heavy, 'light': not heavy, 'all': True}[T_on]
        doOS = {'heavy': heavy, 'light': not heavy, 'all': True}[OS_on]
        if doT and ret != 0:
            side = -1 if ret > 0 else 1
            i_in = np.searchsorted(dt, t_in)
            if i_in < len(dt) and dt[i_in] == t_in:
                i_out = np.searchsorted(dt, t_out)
                px, ex, kind, ix = run(side, i_in, [i_out], kT * A)
                trades.append(dict(date=D, leg="T", side=side, entry=px, exit=ex, kind=kind,
                                   net=side * (ex - px) * PV - COST, atrd=A, ratio=nvol / med))
        if doOS:
            i0 = np.searchsorted(dt, 830); i959 = np.searchsorted(dt, 959)
            if i0 >= len(dt) or dt[i0] != 830 or i959 >= len(dt) or dt[i959] != 959:
                continue
            p0 = do[i0]
            bh = dh[i0:i959 + 1].max(); bl = dl[i0:i959 + 1].min()
            tp = (dh + dl + dc) / 3
            cum = np.cumsum(tp[i0:] * dv[i0:]) / np.cumsum(dv[i0:])
            vw = np.r_[np.full(i0, np.nan), cum]
            cb = (bh - p0) > 2 * (p0 - bl); cv = dc[i959] > vw[i959]
            if {'full': cb and cv, 'box': cb, 'vwap': cv, 'none': True}[os_cond]:
                i_in = i959 + 1
                if dt[i_in] != 1000:
                    continue  # never happens on the sample
                i_out = np.searchsorted(dt, 1100)
                rule = lambda i: dc[i] < vw[i]
                px, ex, kind, ix = run(1, i_in, [i_out], kOS * A, rule)
                trades.append(dict(date=D, leg="OS", side=1, entry=px, exit=ex, kind=kind,
                                   net=(ex - px) * PV - COST, atrd=A, ratio=nvol / med))
    return pd.DataFrame(rows), pd.DataFrame(trades)


if __name__ == "__main__":
    d = load()
    nights, T = build(d)
    _, Tg = build(d, gap_fill=True)
    _, Tn = build(d, stop_on=False)
    for df in (nights, T, Tg, Tn):
        df["date"] = pd.to_datetime(df.date.astype(str))
    nights.to_csv(os.path.join(HERE, "replica_nights.csv"), index=False)
    T.to_csv(os.path.join(HERE, "replica_trades.csv"), index=False)
    Tg.to_csv(os.path.join(HERE, "replica_trades_gap.csv"), index=False)
    Tn.to_csv(os.path.join(HERE, "replica_trades_nostop.csv"), index=False)
    for nm, x in (("stop@price", T), ("stop gap-aware", Tg), ("no stop", Tn)):
        print(nm, x.groupby("leg").net.agg(["count", "mean", "sum"]).round(1).to_dict("index"))
