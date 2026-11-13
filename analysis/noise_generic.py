"""Market-agnostic port of the Bridge noise-area engine (analysis/bridge_noise_15m_test.run), 2026-11-13, for
checks/candidates/noise_other_markets/PREREG.md. Same bar logic; the session (anchor bar, first decision, last entry, flat, prior close
bar), point value, tick, commission and the grid are inputs. Stop per day = stop_atr x the market's 15-day ATR (or a fixed sl).
run(g, mk, ...) -> trades DataFrame (per 1 contract, net after commission + 1 tick per market / stop fill).
"""
import sys; sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from replica import is_early_close


def hm(t): return t // 100 * 60 + t % 100


def series24(g):
    B = g.bars(15); out = []
    for r in range(g.D):
        for i in range(96):
            c = B["c"][r, i]
            if np.isnan(c) or (i == 0 and r == 0): continue
            out.append((r, (i * 15 // 60) * 100 + (i * 15) % 60, B["o"][r, i], B["h"][r, i], B["l"][r, i], c, i * 15))
    return pd.DataFrame(out, columns=["row", "t", "o", "h", "l", "c", "j"])


def ema(x, n):
    a = 2.0 / (n + 1); y = np.empty(len(x)); y[0] = x[0]
    for i in range(1, len(x)): y[i] = y[i - 1] + a * (x[i] - y[i - 1])
    return y


def run(g, S, mk, look=20, vm=1.0, emalen=20, rr=0.5, maxtr=10, maxstops=3, longs=True, shorts=True, sl=None, stop_atr=0.20,
        early_flat=True, rng=None, years=(2018, 2026)):
    """mk: dict(open_t (close stamp of the market's first session bar), close_t (close stamp of its last session bar, = prior close),
    first, last_entry, flat (HHMM), pv, tick, comm). rng: random side on every entry (placebo)."""
    PV, TICK, COMM = mk["pv"], mk["tick"], mk["comm"]
    atr = g.daily_atr(15)
    first_m, flat_t = hm(mk["first"]), mk["flat"]; nslot = (hm(flat_t) - first_m) // 15
    row, t, O, H, L, C, J = (S[k].to_numpy() for k in ("row", "t", "o", "h", "l", "c", "j"))
    E = ema(C, emalen); hist = [[] for _ in range(nslot + 2)]
    rows = []; pos = 0; e = 0.0; t_in = None; j_in = 0; pend = None
    today_open = prev_close = 0.0; trades = stops = 0; last_close = 0.0; ec = False; le = mk["last_entry"]; slv = sl or 0.0; tp = 0.0
    ts = pd.DatetimeIndex(g.ts); yr = ts.year

    def close_trade(px, kind, k, jx):
        nonlocal pos, stops
        if (px - e) * pos <= -slv: stops += 1
        rows.append((g.ts[row[k]], pos, e, px, kind, t_in, t[k], row[k], j_in, jx, slv)); pos = 0

    for k in range(len(S)):
        if k == 0 or row[k] != row[k - 1]:
            if pos != 0: close_trade(C[k - 1] - pos * TICK, "held past session", k - 1, J[k - 1])
            pend = None; today_open = 0.0; trades = stops = 0
            a = atr[row[k]]; slv = sl if sl else (round(stop_atr * a / TICK) * TICK if np.isfinite(a) else 0.0); tp = slv * rr
            ec = early_flat and is_early_close(ts[row[k]]); le = min(mk["last_entry"], 1100) if ec else mk["last_entry"]
        if t[k] == mk["open_t"]: today_open = O[k]; prev_close = last_close
        if t[k] == mk["close_t"]: last_close = C[k]
        if pend is not None:
            if pend[0] in ("out", "rev") and pos != 0: close_trade(O[k] - pos * TICK, pend[2], k, J[k] - 14)
            if pend[0] in ("in", "rev") and pend[1] != 0: pos = pend[1]; e = O[k] + pos * TICK; t_in = t[k]; j_in = J[k] - 14
            pend = None
        if pos != 0:
            r = row[k]; j1 = J[k]
            for m in range(max(0, j1 - 14), j1 + 1):
                if np.isnan(g.c[r, m]): continue
                stp, tgt = e - pos * slv, e + pos * tp
                if (g.l[r, m] <= stp) if pos > 0 else (g.h[r, m] >= stp):
                    close_trade((min(g.o[r, m], stp) if pos > 0 else max(g.o[r, m], stp)) - pos * TICK, "stop", k, m); break
                if (g.h[r, m] >= tgt) if pos > 0 else (g.l[r, m] <= tgt):
                    close_trade(tgt, "target", k, m); break
        tt = t[k]
        if hm(mk["first"]) <= hm(tt) <= hm(flat_t) and today_open > 0 and prev_close > 0 and slv > 0 and years[0] <= yr[row[k]] <= years[1]:
            slot = (hm(tt) - first_m) // 15 + 1
            if 1 <= slot <= nslot:
                mv = abs(C[k] / today_open - 1); hs = hist[slot]
                if len(hs) >= look:
                    avg = np.mean(hs[-look:]) * vm
                    ub = max(today_open, prev_close) * (1 + avg); lb = min(today_open, prev_close) * (1 - avg)
                    ltr, strl = max(ub, E[k]), min(lb, E[k]); can = trades < maxtr and stops < maxstops
                    lsig = C[k] > ub and C[k] > O[k]; ssig = C[k] < lb and C[k] < O[k]
                    if rng is not None and (lsig or ssig):
                        s_ = rng.choice([-1, 1]); lsig, ssig = s_ > 0, s_ < 0
                    lsig = lsig and longs; ssig = ssig and shorts
                    if tt != flat_t:
                        if pos == 0 and can and hm(tt) <= hm(le):
                            if lsig: pend = ("in", 1); trades += 1
                            elif ssig: pend = ("in", -1); trades += 1
                        elif pos == 1:
                            if hm(tt) <= hm(le) and ssig:
                                if can: pend = ("rev", -1, "reverse"); trades += 1
                                else: pend = ("out", 0, "reverse exit")
                            elif C[k] < ltr and rng is None: pend = ("out", 0, "band/EMA exit")
                        elif pos == -1:
                            if hm(tt) <= hm(le) and lsig:
                                if can: pend = ("rev", 1, "reverse"); trades += 1
                                else: pend = ("out", 0, "reverse exit")
                            elif C[k] > strl and rng is None: pend = ("out", 0, "band/EMA exit")
                hs.append(mv)
                if len(hs) > 100: hs.pop(0)
        if tt == flat_t and pos != 0: pend = ("out", 0, "flat")
        if ec and tt == 1130 and pos != 0: pend = ("out", 0, "flat early close")
    T = pd.DataFrame(rows, columns=["date", "side", "entry", "exit", "kind", "t0", "t1", "row", "j0", "j1", "sl"])
    T["date"] = pd.to_datetime(T.date); T["net"] = (T.exit - T.entry) * T.side * PV - COMM
    return T
