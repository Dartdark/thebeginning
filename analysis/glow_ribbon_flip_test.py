"""Glow Ribbon Flip (TradingView, 2026-10-13): EMA basis + ratcheting ATR band, stop-and-reverse flips
and pullback re-entries, ported to NQ.

Rules: basis EMA(21); band = EMA -/+ ATR(10) x 2.0 (Wilder ATR). In an uptrend the lower band only rises,
in a downtrend the upper band only falls; a close beyond the band flips the trend and resets the band.
Entries at the next bar's open: on a flip (into the new direction), or, when flat inside an established
trend, on a close back across the EMA in the trend's direction (pullback). Stop = the band, re-armed each
bar (intrabar, 1-minute resolution); optional target 2R (R = entry to band at entry), limit order.
Apex: flat at 15:55 CT, no entries 15:45-17:00 CT; the trend state runs on continuously.
Variants: 5 / 15 / 30 / 60-minute bars, target 2R or none, band 2.0 or 3.0 ATR, 24h or day session only.
Per NQ after $7.25 + 1 tick per market/stop fill (the target is a limit, no slippage), 2018-2026.
  python3 analysis/glow_ribbon_flip_test.py [SCRATCH_DIR]
"""
import sys, warnings, pickle, itertools; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from bollinger_reversal_test import bar_series
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25


def run(g, k=15, ema_n=21, atr_n=10, mult=2.0, rr=2.0, rth=False, pullbacks=True, rand=None):
    s = bar_series(g, k)
    O, H, L, C = (getattr(g, a).ravel() for a in "ohlc")
    ts = pd.DatetimeIndex(g.ts)
    T = (s.row * 1440 + s.col).to_numpy()                       # flat minute index of each bar's close
    c, h, l = s.c.to_numpy(), s.h.to_numpy(), s.l.to_numpy()
    ema = pd.Series(c).ewm(span=ema_n, adjust=False).mean().to_numpy()
    pc = np.r_[c[0], c[:-1]]
    tr = np.fmax(h - l, np.fmax(np.abs(h - pc), np.abs(l - pc)))
    atr = pd.Series(tr).ewm(alpha=1 / atr_n, adjust=False).mean().to_numpy()
    rng = np.random.default_rng(rand) if rand is not None else None
    trend, band = 1, ema[0] - mult * atr[0]
    pos = 0; e = stop = tgt = 0.0; t_in = 0; rows = []
    started = 2 * ema_n

    def close_pos(t, px, kind):
        nonlocal pos
        rows.append(dict(t0=t_in, t1=t, side=pos, entry=e, exit=px, kind=kind,
                         net=(px - e) * pos * PV - COST, date=ts[t_in // 1440]))
        pos = 0

    for i in range(1, len(c)):
        # 1) manage an open position minute by minute through this bar
        if pos != 0:
            for t in range(T[i - 1] + 1, T[i] + 1):
                if np.isnan(H[t]): continue
                col = t % 1440
                if (L[t] <= stop) if pos > 0 else (H[t] >= stop):
                    close_pos(t, (min(O[t], stop) if pos > 0 else max(O[t], stop)) - pos * TICK, 0); break
                if rr and ((H[t] >= tgt) if pos > 0 else (L[t] <= tgt)):
                    close_pos(t, max(O[t], tgt) if pos > 0 else min(O[t], tgt), 1); break
                if 955 <= col < 1020:
                    close_pos(t, C[t] - pos * TICK, 0); break
        # 2) update the trend and the band at this bar's close
        lo_b, up_b = ema[i] - mult * atr[i], ema[i] + mult * atr[i]
        flip = 0
        if trend > 0:
            band = max(band, lo_b)
            if c[i] < band: trend, band, flip = -1, up_b, -1
        else:
            band = min(band, up_b)
            if c[i] > band: trend, band, flip = 1, lo_b, 1
        if pos != 0 and pos == trend:                   # re-arm the stop on the ratcheted band
            stop = max(stop, band) if pos > 0 else min(stop, band)
        if i < started: continue
        # 3) signals -> entry at the next minute's open
        new = 0
        if flip != 0:
            new = flip
        elif pullbacks and pos == 0:
            if trend > 0 and c[i] > ema[i] and pc[i] <= ema[i - 1]: new = 1
            if trend < 0 and c[i] < ema[i] and pc[i] >= ema[i - 1]: new = -1
        if new == 0: continue
        if pos == new: continue
        t0 = T[i] + 1
        if t0 >= len(O) or np.isnan(O[t0]): continue
        col = t0 % 1440; hh = (col // 60) * 100 + col % 60
        if 1545 <= hh < 1700: continue
        if rth and not (830 <= hh <= 1430): continue
        if ts[t0 // 1440].year < 2018: continue
        if pos != 0:                                   # reverse: exit at the same open
            close_pos(t0, O[t0] - pos * TICK, 0)
        side = new if rng is None else int(rng.choice([-1, 1]))
        e = O[t0] + side * TICK
        stop = band if side == trend else (e - side * mult * atr[i])
        R_ = (e - stop) * side
        if R_ <= 0: continue
        tgt = e + side * rr * R_ if rr else 0.0
        pos, t_in = side, t0
    return pd.DataFrame(rows)


def line(t, nm, w=44):
    if len(t) < 2: return f"{nm:<{w}} n={len(t)}"
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); h = x[y >= 2023]
    pf = lambda q: q[q > 0].sum() / max(1e-9, -q[q < 0].sum())
    L_, S_ = x[t.side > 0], x[t.side < 0]
    return (f"{nm:<{w}} n={len(x):5d} win {np.mean(x > 0):.0%} avg ${x.mean():5.0f} PF {pf(x):.2f}"
            f" t={x.mean() / x.std() * np.sqrt(len(x)):5.1f} yrs+ {(by > 0).sum()}/{len(by)} | 23+ ${h.mean():5.0f} PF {pf(h):.2f}"
            f" | L ${L_.mean():4.0f} PF {pf(L_):.2f} S ${S_.mean():4.0f} PF {pf(S_):.2f}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    print(__doc__.split("\n")[0])
    print("\n1. Variants, per NQ:")
    res = {}
    for k, rr, mult in itertools.product((5, 15, 30, 60), (2.0, 0), (2.0, 3.0)):
        nm = f"{k:>2}-min, target {'2R' if rr else 'none'}, band {mult} ATR"
        res[nm] = run(g, k, mult=mult, rr=rr); print(line(res[nm], nm))
    for k in (15, 30):
        nm = f"{k:>2}-min, 2R, 2.0 ATR, day session only"
        res[nm] = run(g, k, rth=True); print(line(res[nm], nm))
        nm = f"{k:>2}-min, 2R, 2.0 ATR, no pullbacks (flips only)"
        res[nm] = run(g, k, pullbacks=False); print(line(res[nm], nm))
    tt = {k: v.net.mean() / v.net.std() * np.sqrt(len(v)) for k, v in res.items() if len(v) > 1}
    best = max(tt, key=tt.get); b = res[best]
    print(f"\n2. Best of {len(res)} by t: {best}")
    print("   by year:", b.groupby(b.date.dt.year).net.sum().round(0).astype(int).to_dict())
    kb = int(best.split("-")[0]); rrb = 2.0 if "2R" in best else 0; mb = 3.0 if "3.0" in best else 2.0
    pl = [run(g, kb, mult=mb, rr=rrb, rand=r).net.mean() for r in range(10)]
    print(f"   placebo (same entry times, random side, 10 runs): ${np.mean(pl):.0f} ({min(pl):.0f}..{max(pl):.0f}) vs real ${b.net.mean():.0f}")
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dl = lambda t: t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    d15 = res["15-min, target 2R, band 2.0 ATR"]
    print(M.table({"defaults (15-min)": (dl(d15), d15.net), "best": (dl(b), b.net),
                   "  best longs": (dl(b[b.side > 0]), b.net[b.side > 0]), "  best shorts": (dl(b[b.side < 0]), b.net[b.side < 0])}))
