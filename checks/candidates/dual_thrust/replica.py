"""Checker replica of Dual Thrust v4 (CT) built from spec.md only. Raw data: data/NQ_1min_20*.csv (bar-close stamps, CT).
Writes trades_replica.csv (date, side, net, entry, exit, kind, sig_time, rr, adr, band, entry_time, exit_time)."""
import glob, os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
K, SL, TP, BAND, TICK = 0.5, 50.0, 100.0, 1.2, 0.25
VARIANT = dict(a.split("=") for a in sys.argv[1:])          # e.g. touch=1 (target at touch), noentrystop=1
TOUCH = VARIANT.get("touch") == "1"


def holiday(d):
    mo, dy, dw = d.month, d.day, d.weekday() + 1          # MC DayOfWeek: Mon = 1
    return ((mo == 1 and dw == 1 and 15 <= dy <= 21) or (mo == 2 and dw == 1 and 15 <= dy <= 21)
            or (mo == 5 and dw == 1 and dy >= 25)
            or (mo == 6 and (dy == 19 or (dw == 1 and dy == 20) or (dw == 5 and dy == 18)))
            or (mo == 7 and (dy in (3, 4) or (dw == 1 and dy == 5)))
            or (mo == 9 and dw == 1 and dy <= 7)
            or (mo == 11 and ((dw == 4 and 22 <= dy <= 28) or (dw == 5 and 23 <= dy <= 29)))
            or (mo == 12 and (dy in (24, 25) or (dw == 1 and dy == 26))))


def load():
    fs = sorted(glob.glob(os.path.join(ROOT, "data", "NQ_1min_20*.csv")))
    out = []
    for f in fs:
        d = pd.read_csv(f, dtype={"date": str})
        out.append(d[["date", "time", "open", "high", "low", "close"]])
    return pd.concat(out, ignore_index=True)


def sim_day(g, O, rr, side_force=None):
    t, o, h, l, c = (g[k].values for k in ("time", "open", "high", "low", "close"))
    up, dn = O + K * rr, O - K * rr
    scan = np.where((t >= 831) & (t <= 1430))[0]
    sig = None
    for i in scan:
        if c[i] > up: sig, side = i, 1; break
        if c[i] < dn: sig, side = i, -1; break
    if sig is None or sig + 1 >= len(t): return None
    if side_force is not None: side = side_force
    e = sig + 1; ent = o[e]
    st0 = c[sig] - side * SL
    st, tg = ent - side * SL, ent + side * TP
    ex = kind = None; xi = None
    for j in range(e, len(t)):
        if j == e:                                       # entry bar: only the trigger-close stop
            if VARIANT.get("noentrystop") != "1" and ((side == 1 and l[j] <= st0) or (side == -1 and h[j] >= st0)):
                ex = min(o[j], st0) if side == 1 else max(o[j], st0); kind = "stop"; xi = j; break
        else:
            hit_s = (l[j] <= st) if side == 1 else (h[j] >= st)
            thr = 0 if TOUCH else TICK
            hit_t = (h[j] >= tg + thr) if side == 1 else (l[j] <= tg - thr)
            if hit_s:
                ex = min(o[j], st) if side == 1 else max(o[j], st); kind = "stop"; xi = j; break
            if hit_t:
                ex = max(o[j], tg) if side == 1 else min(o[j], tg); kind = "target"; xi = j; break
        if t[j] >= 1455:
            if j + 1 < len(t): ex = o[j + 1]; kind = "flat"; xi = j + 1
            else: ex = c[j]; kind = "close"; xi = j
            break
    if ex is None: ex = c[-1]; kind = "close"; xi = len(t) - 1
    gross = side * (ex - ent) * 20.0
    cost = 7.25 + 5.0 + (0.0 if kind == "target" else 5.0)
    return dict(side=side, net=gross - cost, entry=ent, exit=ex, kind=kind, sig_time=int(t[sig]),
                entry_time=int(t[e]), exit_time=int(t[xi]))


def run(df, side_rng=None):
    rows = []; hist = []                                 # banked (H, L, C, range)
    for ds, g in df.groupby("date", sort=True):
        d = pd.Timestamp(ds)
        g = g.sort_values("time")
        r = g[(g.time >= 831) & (g.time <= 1500)]
        if len(r) and len(hist) >= 20 and d >= pd.Timestamp("2018-01-01") and (r.time.iloc[0] == 831 or True):
            pH, pL, pC, _ = hist[-1]
            rr = max(pH - pC, pC - pL); adr = np.mean([x[3] for x in hist[-20:]])
            if rr > 0 and not (rr / adr > BAND) and not holiday(d):
                O = r.open.iloc[0]
                sf = None if side_rng is None else int(side_rng.choice([-1, 1]))
                res = sim_day(g.reset_index(drop=True), O, rr, sf)
                if res:
                    res.update(date=d.strftime("%Y-%m-%d"), rr=rr, adr=adr, band=rr / adr,
                               first_rth=int(r.time.iloc[0]), last_bar=int(g.time.iloc[-1]))
                    rows.append(res)
        if len(r):
            H, L, C = r.high.max(), r.low.min(), r.close.iloc[-1]
            if H > L: hist.append((H, L, C, H - L))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = load()
    T = run(df)
    cols = ["date", "side", "net", "entry", "exit", "kind", "sig_time", "entry_time", "exit_time", "rr", "adr", "band",
            "first_rth", "last_bar"]
    name = "trades_replica" + "".join(f"_{k}{v}" for k, v in VARIANT.items()) + ".csv"
    T[cols].to_csv(os.path.join(HERE, name), index=False)
    print(len(T), T.net.sum(), T.net.mean())
