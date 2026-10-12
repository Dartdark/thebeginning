"""Mean reversion, scheduled news and headline shocks on NQ (2026-10-12, user request).

Not repeated here (already in TIER_LIST.md): fading big 30/60-minute RTH moves (F), round
numbers (F), VWAP fade / lunchtime RSI(2) / IBS (F), quiet-day midday fade (D), gap fill (D),
post-settlement reversal (D), 7:30 release fade (D), pre-FOMC drift (F), announcement-day
premium (F), asymmetric next-day reversal (C).

New here:
  A. Mean reversion
     A1  Asia session VWAP fade (17:00-23:59 CT, VWAP from 17:00): price stretched k x ATR from
         VWAP -> fade, target VWAP (limit), stop, out 23:59
     A2  London / pre-market VWAP fade (00:00-07:25 CT, VWAP from midnight), out 07:25
     A3  Multi-day pullback: after N down (up) sessions in a row (15:00 -> 15:00), buy (sell)
         the next 8:30 open, out 15:00, stop 0.3 ATR (Connors-style daily reversion, day-traded)
  B. Scheduled news
     B1  FOMC statement (13:00 CT): follow / fade the 13:00 -> 13:05/13:10/13:15 reaction,
         hold to 13:29 (before the press conference), 14:00 or 15:00
     B2  Press conference: follow / fade the 13:00 -> 13:30 statement move from 13:30 to 15:00
     B3  9:00 CT releases (ISM, JOLTS, confidence, home sales; detected from the 9:00-9:05
         range spike): follow / fade the 9:00 -> 9:05/9:10 reaction, hold 30/60 min
     B4  7:30 releases split NFP-like (first Friday, day <= 10) vs other (CPI, PPI, retail...):
         follow / fade the 7:30 -> 7:45 reaction into 8:00/8:30
  C. Headline shocks (no headline feed for NQ here: unscheduled price jumps as the proxy)
     5-minute move > k x its normal size for that time of day (20-day mean |move| in the same
     slot), outside scheduled minutes (7:30, 8:30 open, 9:00, 13:00-13:45 FOMC days, 15:00-15:15).
     Follow / fade from the next minute, hold 15 / 30 / 60 minutes, stop = the jump's size.
     Day session (8:40-14:15 CT) and overnight (17:30-7:15) separately. Jeon, McCurdy & Zhao
     (2022, JFE "News as sources of jumps"): news jumps continue, no-news jumps reverse.

Costs: $7.25 per NQ + 1 tick on every market/stop fill (limit targets fill without slippage).
  python3 analysis/news_meanrev_test.py [SCRATCH_DIR]
"""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import event_days as E

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
TICK, PV, COST = 0.25, 20.0, 7.25


def sim(G, d, j0, side, stop_px, tgt_px, j_exit):
    """Enter at the open of column j0 (+1 tick), stop (market, +1 tick), target (limit), else
    out at the close of j_exit (-1 tick). Returns (j1, entry, exit, kind 1 = target)."""
    e = G.o[d, j0]
    if np.isnan(e): return None
    e += side * TICK
    for j in range(j0, j_exit + 1):
        h, l, o = G.h[d, j], G.l[d, j], G.o[d, j]
        if np.isnan(h): continue
        if stop_px is not None and ((l <= stop_px) if side > 0 else (h >= stop_px)):
            px = (min(o, stop_px) if side > 0 else max(o, stop_px)) if j > j0 else stop_px
            return j, e, px - side * TICK, 0
        if tgt_px is not None and ((h >= tgt_px) if side > 0 else (l <= tgt_px)):
            return j, e, (max(o, tgt_px) if side > 0 else min(o, tgt_px)) if j > j0 else tgt_px, 1
    c = G.c[d, j_exit]
    if np.isnan(c):
        cc = G.c[d, j0:j_exit + 1]; ok = np.where(~np.isnan(cc))[0]
        if not len(ok): return None
        j_exit = j0 + ok[-1]; c = cc[ok[-1]]
    return j_exit, e, c - side * TICK, 0


def row(G, d, j0, side, j1e, stop, tgt):
    r = sim(G, d, j0, side, stop, tgt, j1e)
    if r is None: return None
    j1, e, px, kind = r
    pnl = (px - e) * side * PV
    return dict(day=d, j0=j0, j1=j1, side=side, entry=e, exit=px, kind=kind, slips=0,
                net=pnl - COST, date=pd.Timestamp(G.ts[d]))


def summ(t, name, w=46):
    if t is None or len(t) == 0: return f"{name:<{w}} n=   0"
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); h = x[y >= 2023]
    pf = lambda s: s[s > 0].sum() / max(1e-9, -s[s < 0].sum())
    ts_ = x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 1 else np.nan
    L, S = x[t.side > 0], x[t.side < 0]
    return (f"{name:<{w}} n={len(x):5d} win {np.mean(x > 0):.0%} avg ${x.mean():5.0f} PF {pf(x):.2f} t={ts_:4.1f}"
            f" yrs+ {(by > 0).sum()}/{len(by)} | 23+ ${h.mean() if len(h) else np.nan:5.0f} PF {pf(h):.2f}"
            f" | L ${L.mean() if len(L) else np.nan:4.0f} S ${S.mean() if len(S) else np.nan:4.0f}")


# ------------------------------------------------------------------ A1 / A2 VWAP fades
def vwap_fade(G, atr, vw, start, end, k=0.15, stop_k=0.15, first=None, last=None, step=5):
    """One trade per row: first `step`-minute close in [first, last] with |close - VWAP| > k ATR
    -> fade at the next minute, target VWAP at entry time, stop stop_k ATR beyond entry."""
    rows = []; ts = pd.DatetimeIndex(G.ts)
    first = first or start + 30; last = last or end - 60
    J = np.arange(jof(first), jof(last) + 1, step)
    for d in range(G.D):
        if ts[d].year < 2018 or ts[d].dayofweek == 5 or np.isnan(atr[d]): continue
        c = G.c[d, J]; v = vw[d, J]
        dev = c - v
        hit = np.where(np.abs(dev) > k * atr[d])[0]
        if not len(hit): continue
        i = hit[0]; j0 = J[i] + 1; side = -int(np.sign(dev[i]))
        if j0 >= jof(end): continue
        e = G.o[d, j0]
        if np.isnan(e): continue
        r = row(G, d, j0, side, jof(end), e - side * stop_k * atr[d], v[i])
        if r: rows.append(r)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ A3 multi-day pullback
def pullback(G, atr, n=2, stop_k=0.3, side_mode="both"):
    tr = G.trading; ts = pd.DatetimeIndex(G.ts); rows = []
    c15 = G.c[:, jof(1500)]
    cl = pd.Series(c15[tr]).ffill().to_numpy()
    ret = np.r_[np.nan, np.diff(cl)]
    for i in range(n + 1, len(tr)):
        d = tr[i]
        if ts[d].year < 2018 or np.isnan(atr[d]): continue
        last = ret[i - n:i]                                       # the n sessions before day i
        if np.all(last < 0): side = 1
        elif np.all(last > 0): side = -1
        else: continue
        if side_mode == "long" and side < 0: continue
        if side_mode == "short" and side > 0: continue
        j0 = jof(830) + 1; e = G.o[d, j0]
        if np.isnan(e): continue
        r = row(G, d, j0, side, jof(1500), e - side * stop_k * atr[d] if stop_k else None, None)
        if r: rows.append(r)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ B scheduled news
def reaction_trades(G, days, t_react0, t_react1, t_exit, mode, stop_k=None, atr=None, min_move=0.0):
    rows = []; ts = pd.DatetimeIndex(G.ts)
    for d in days:
        if ts[d].year < 2018: continue
        a, b = G.c[d, jof(t_react0)], G.c[d, jof(t_react1)]
        if np.isnan(a) or np.isnan(b) or abs(b - a) <= min_move: continue
        s = int(np.sign(b - a)) * (1 if mode == "follow" else -1)
        if s == 0: continue
        j0 = jof(t_react1) + 1; e = G.o[d, j0]
        if np.isnan(e): continue
        stop = None
        if stop_k == "react": stop = e - s * abs(b - a)
        elif stop_k: stop = e - s * stop_k * atr[d]
        r = row(G, d, j0, s, jof(t_exit), stop, None)
        if r: rows.append(r)
    return pd.DataFrame(rows)


def spike_days(G, t0, t1, mult=3.0, lookback=20):
    tr = G.trading
    r = pd.Series(E.bar_range(G, tr, t0, t1))
    base = r.rolling(lookback).median().shift(1)
    return tr[(r > mult * base).to_numpy()]


# ------------------------------------------------------------------ C headline-shock jumps
def jumps(G, fomc, k=5.0, window=(840, 1415), lookback=20, step=5):
    """Unscheduled 5-minute jumps: (row, column of the jump's last bar, signed move)."""
    C = pd.DataFrame(G.c).ffill(axis=1).to_numpy()
    J = np.arange(jof(window[0]), jof(window[1]) + 1, step) if window[0] < window[1] else \
        np.r_[np.arange(jof(window[0]), 1440, step), np.arange(step, jof(window[1]) + 1, step)]
    mv = C[:, J] - C[:, J - step]
    has = ~np.isnan(G.c[:, J]) & ~np.isnan(G.c[:, J - step])
    mv[~has] = np.nan
    # normal size per slot: mean |move| over the previous `lookback` calendar rows that traded
    norm = pd.DataFrame(np.abs(mv)).rolling(lookback, min_periods=8).mean().shift(1).ffill().to_numpy()
    sched = np.zeros(len(J), bool)
    hhmm = (J // 60) * 100 + J % 60
    for a, b in ((730, 740), (830, 840), (900, 910), (1500, 1520), (1000, 1005)):
        sched |= (hhmm > a) & (hhmm <= b)
    fom = set(E.rows_of(G, E.FOMC_DATES).tolist())
    out = []
    z = np.abs(mv) / norm
    for d, i in zip(*np.where(z > k)):
        if sched[i]: continue
        if d in fom and 1300 < hhmm[i] <= 1545: continue
        out.append((d, J[i], mv[d, i]))
    return out


def jump_trades(G, js, mode, hold=30, stop="jump", end_cap=None):
    rows = []; ts = pd.DatetimeIndex(G.ts); last_d = -1; last_j = -1
    for d, j, m in js:
        if ts[d].year < 2018: continue
        if d == last_d and j <= last_j: continue          # one trade at a time
        s = int(np.sign(m)) * (1 if mode == "follow" else -1)
        j0 = j + 1; j1 = min(j0 + hold, 1439 if end_cap is None else end_cap)
        if j0 >= 1440: continue
        e = G.o[d, j0]
        if np.isnan(e): continue
        sp = e - s * abs(m) if stop == "jump" else None
        r = row(G, d, j0, s, j1, sp, None)
        if r: rows.append(r); last_d, last_j = d, r["j1"]
    return pd.DataFrame(rows)


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    atr = g.daily_atr(15)
    print(__doc__.split("\n")[0])

    print("\n=== A1. Asia session VWAP fade (VWAP from 17:00, entries 17:30-23:00, out 23:59) ===")
    vw17 = g.vwap_rows(start_j=jof(1700))
    for k in (0.1, 0.15, 0.25):
        for sk in (0.1, 0.2):
            print(summ(vwap_fade(g, atr, vw17, 1700, 2359, k, sk, 1730, 2300), f"stretch {k} ATR, stop {sk} ATR"))
    print("\n=== A2. London / pre-market VWAP fade (VWAP from 0:00, entries 0:30-6:30, out 7:25) ===")
    vw0 = g.vwap_rows(start_j=0)
    for k in (0.1, 0.15, 0.25):
        for sk in (0.1, 0.2):
            print(summ(vwap_fade(g, atr, vw0, 0, 725, k, sk, 30, 630), f"stretch {k} ATR, stop {sk} ATR"))

    print("\n=== A3. Multi-day pullback, trade the next session 8:30-15:00 ===")
    for n in (2, 3, 4):
        for sk in (0.3, 0):
            print(summ(pullback(g, atr, n, sk), f"after {n} sessions same way, stop {sk or 'none'} ATR"))

    print("\n=== B1/B2. FOMC statement 13:00 CT and press conference 13:30 ===")
    fom = E.rows_of(g, E.FOMC_DATES)
    for mode in ("follow", "fade"):
        for r1 in (1305, 1310, 1315):
            for ex in (1329, 1400, 1500):
                print(summ(reaction_trades(g, fom, 1300, r1, ex, mode), f"{mode} 13:00->{r1}, out {ex}"))
    for mode in ("follow", "fade"):
        print(summ(reaction_trades(g, fom, 1300, 1330, 1500, mode), f"{mode} 13:00->13:30 move, 13:30->15:00"))
        print(summ(reaction_trades(g, fom, 1330, 1345, 1500, mode), f"{mode} presser 13:30->13:45, ->15:00"))

    print("\n=== B3. 9:00 CT releases (9:00-9:05 range > 3x normal) ===")
    s9 = spike_days(g, 900, 905, 3.0)
    print(f"  {len(s9)} days")
    for mode in ("follow", "fade"):
        for r1 in (905, 910):
            for hold in (30, 60):
                ex = (r1 // 100) * 100 + (r1 % 100 + hold) if r1 % 100 + hold < 60 else (r1 // 100 + 1) * 100 + (r1 % 100 + hold - 60)
                print(summ(reaction_trades(g, s9, 900, r1, ex, mode), f"{mode} 9:00->{r1}, out {ex}"))

    print("\n=== B4. 7:30 releases: NFP-like (Friday, day <= 10) vs other ===")
    rel = E.release_days(g)
    tsr = pd.DatetimeIndex(g.ts[rel])
    nfp = rel[(tsr.dayofweek == 4) & (tsr.day <= 10)]; oth = np.setdiff1d(rel, nfp)
    print(f"  NFP-like {len(nfp)}, other {len(oth)}")
    for nm, days in (("NFP", nfp), ("other", oth)):
        for mode in ("follow", "fade"):
            for ex in (800, 830, 900):
                print(summ(reaction_trades(g, days, 729, 745, ex, mode), f"{nm}: {mode} 7:29->7:45, out {ex}"))

    print("\n=== C. Headline-shock proxy: unscheduled 5-minute jumps ===")
    for win, nm, cap in (((840, 1415), "day 8:40-14:15", jof(1455)), ((1730, 715), "overnight 17:30-7:15", None)):
        for k in (4.0, 6.0, 8.0):
            js = jumps(g, fom, k, win)
            for mode in ("follow", "fade"):
                for hold in (15, 30, 60):
                    print(summ(jump_trades(g, js, mode, hold, end_cap=cap), f"{nm} >{k:.0f}x {mode} {hold}m"))
