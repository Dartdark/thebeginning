"""Strategy building blocks (2026-10-20): entries and exits as reusable pieces, Apex-legal (intraday, flat by 15:55 CT).

From Antigravity's catalog (antigravity/jesse tasks/STRATEGY_BUILDING_BLOCKS.md), rebuilt for our data and rules:
  - RTH 15-minute bars (8:30-15:00 CT; bar i closes at 8:45 + 15 i, i = 0..25), lookbacks run across days on that RTH
    series, prices back-adjusted for roll jumps (roll_adjust.roll_jumps) so lookbacks don't see the roll gap.
  - A signal at the close of bar i (i = 0..21, i.e. 8:45..14:00) enters at the next bar's open (market) or, for stop
    entries, during bar i + 1 at the stop level (or the minute's open if it gaps through).
  - Costs per contract round trip: commission + 1 tick on each market / stop fill (NQ $7.25 + $10 = $17.25, ES $5 + $25).
  - One position at a time; days that close early (no 15:00 bar) are skipped.

  rth = RTH(g, "NQ")                     # bars + 1-minute data for one market
  sig = ENTRIES["E2"](rth)               # (days, 26) array of +1 / -1 / 0 signals at bar closes (stop entries: dict)
  trades = run(rth, sig, exit_bars=4)    # DataFrame: date, i, side, entry, exit, pnl ($ per contract after costs)
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from roll_adjust import roll_jumps

SPEC = {"NQ": (20.0, 0.25, 7.25), "ES": (50.0, 0.25, 5.0)}      # $ per point, tick, commission
NB, LAST_SIG = 26, 21                                           # RTH bars a day; last signal bar (14:00)
J0 = jof(830)                                                   # first RTH minute column is J0 + 1 (8:31 bar)


class RTH:
    def __init__(self, g, sym):
        self.sym = sym; self.pv, self.tick, comm = SPEC[sym]; self.cost = comm + 2 * self.tick * self.pv
        days = [d for d in g.trading if g.last_j[d] >= jof(1555) and not np.isnan(g.c[d, J0 + 1:jof(1500) + 1]).all()
                and pd.Timestamp(g.ts[d]) >= pd.Timestamp("2018-01-01")]
        self.days = np.array(days); self.dates = pd.DatetimeIndex(g.ts[self.days])
        J = roll_jumps(g, sym); adj = np.zeros(len(self.days))
        for j, jump in J.items(): adj[self.days * 1440 + jof(1500) < j] += jump
        self.adj = adj
        m = {c: getattr(g, c)[self.days, J0 + 1:jof(1500) + 1] for c in ("o", "h", "l", "c", "v")}   # (n, 390) minutes
        for c in ("o", "h", "l", "c"): m[c] = pd.DataFrame(m[c] + adj[:, None]).ffill(axis=1).bfill(axis=1).to_numpy()
        m["v"] = np.nan_to_num(m["v"]); self.m = m
        r = lambda a: a.reshape(len(self.days), NB, 15)
        self.O = r(m["o"])[:, :, 0]; self.C = r(m["c"])[:, :, -1]
        self.H = r(m["h"]).max(2); self.L = r(m["l"]).min(2); self.V = r(m["v"]).sum(2)
        c1 = pd.DataFrame(g.c[self.days, :jof(1555) + 1]).ffill(axis=1).to_numpy()[:, -1]
        self.C1555 = c1 + adj
        n = len(self.days)
        self.flat = lambda a: a.reshape(-1)                     # day-major flat RTH series
        self.unflat = lambda a: np.asarray(a).reshape(n, NB)
        self.dow = self.dates.dayofweek.to_numpy()
        ym = self.dates.year * 12 + self.dates.month; self.first_of_month = np.r_[True, ym[1:] != ym[:-1]]


# ---------------------------------------------------------------------------------------------------------------------
# Entries: signal at the close of bar i (+1 long, -1 short). Only i <= LAST_SIG are used.
# ---------------------------------------------------------------------------------------------------------------------
def _s(x): return pd.Series(x)


def e1_three_bars(r):            # three bars in a row closing above (below) their open
    up = r.flat(r.C > r.O); dn = r.flat(r.C < r.O)
    u = _s(up).rolling(3).sum().to_numpy() == 3; d = _s(dn).rolling(3).sum().to_numpy() == 3
    return r.unflat(np.where(u, 1, np.where(d, -1, 0)))


def _hilo_close(r, n=10):
    c = _s(r.flat(r.C)); hi = c.rolling(n).max().to_numpy(); lo = c.rolling(n).min().to_numpy(); c = c.to_numpy()
    return c >= hi, c <= lo


def e2_close_breakout(r):        # close = highest (lowest) close of 10 bars -> follow
    hi, lo = _hilo_close(r); return r.unflat(np.where(hi & ~lo, 1, np.where(lo & ~hi, -1, 0)))


def e3_close_fade(r):            # the same extremes, faded
    return -e2_close_breakout(r)


def e4_lowvol_fade(r):           # extreme close on below-average volume (10 bars) -> fade
    hi, lo = _hilo_close(r); v = _s(r.flat(r.V)); low = (v < v.rolling(10).mean()).to_numpy()
    return r.unflat(np.where(low & lo & ~hi, 1, np.where(low & hi & ~lo, -1, 0)))


def e5_dueling(r):               # up over 15 bars but down over 50 -> long; the reverse -> short
    c = _s(r.flat(r.C)); a = (c > c.shift(15)) & (c < c.shift(50)); b = (c < c.shift(15)) & (c > c.shift(50))
    return r.unflat(np.where(a, 1, np.where(b, -1, 0)))


def e6_first_day(r):             # calendar: first trading day of the month, long at 8:45
    s = np.zeros((len(r.days), NB), int); s[r.first_of_month, 0] = 1; return s


def e7_tuesday(r):               # day of week: Tuesday ('Turnaround Tuesday', the catalog's example), long at 8:45
    s = np.zeros((len(r.days), NB), int); s[r.dow == 1, 0] = 1; return s


def e9_ma_cross(r):              # SMA 10 crosses SMA 50
    c = _s(r.flat(r.C)); f = c.rolling(10).mean(); s = c.rolling(50).mean(); x = np.sign(f - s)
    return r.unflat(np.where((x > 0) & (x.shift(1) <= 0), 1, np.where((x < 0) & (x.shift(1) >= 0), -1, 0)))


def e10_stop_breakout(r):        # resting stops at the 10-bar high / low (Donchian / Turtle), placed after each bar close
    h = _s(r.flat(r.H)).rolling(10).max().to_numpy(); l = _s(r.flat(r.L)).rolling(10).min().to_numpy()
    return {"stop": True, "buy": r.unflat(h), "sell": r.unflat(l)}


ENTRIES = {"E1 three bars": e1_three_bars, "E2 close breakout": e2_close_breakout, "E3 close fade": e3_close_fade,
           "E4 low-vol fade": e4_lowvol_fade, "E5 dueling momentum": e5_dueling, "E6 first day of month": e6_first_day,
           "E7 Tuesday": e7_tuesday, "E9 MA 10/50 cross": e9_ma_cross, "E10 stop breakout": e10_stop_breakout}


# ---------------------------------------------------------------------------------------------------------------------
# Running an entry with a neutral exit (Step 1): exit_bars = hold N bars (exit at that bar's close), or None = 15:55.
# ---------------------------------------------------------------------------------------------------------------------
def _stop_fill(r, d, i, buy, sell):
    """First touch of the buy / sell stop during bar i + 1 (1-minute bars); returns (side, price, bar) or None."""
    k = i + 1; sl = slice(k * 15, k * 15 + 15)
    o, h, l = r.m["o"][d, sl], r.m["h"][d, sl], r.m["l"][d, sl]
    for q in range(15):
        ub, dn = h[q] >= buy, l[q] <= sell
        if ub and dn: return None                                   # both in one minute: ambiguous, skip
        if ub: return 1, max(buy, o[q]), k
        if dn: return -1, min(sell, o[q]), k
    return None


def run(r, sig, exit_bars=4):
    rows = []
    stop = isinstance(sig, dict) and sig.get("stop")
    for d in range(len(r.days)):
        i = 0
        while i <= LAST_SIG:
            if stop:
                b, s_ = sig["buy"][d, i], sig["sell"][d, i]
                f = None if np.isnan(b) else _stop_fill(r, d, i, b, s_)
                if f is None: i += 1; continue
                side, e, k = f
            else:
                side = int(sig[d, i])
                if side == 0: i += 1; continue
                e, k = r.O[d, i + 1], i + 1
            if exit_bars is None: x, xb = r.C1555[d], NB
            else: xb = min(k + exit_bars - 1, NB - 1); x = r.C[d, xb]
            rows.append((r.dates[d], i, side, e, x, (x - e) * side * r.pv - r.cost))
            if exit_bars is None: break
            i = xb                                                  # next signal from the exit bar's close
    return pd.DataFrame(rows, columns=["date", "i", "side", "entry", "exit", "pnl"])


def market_pnl(r, exit_bars=4):
    """$ P&L per contract after costs of a market entry at every (day, signal bar), long; for placebos."""
    e = r.O[:, 1:LAST_SIG + 2]
    if exit_bars is None: x = np.repeat(r.C1555[:, None], LAST_SIG + 1, 1)
    else: x = r.C[:, np.minimum(np.arange(1, LAST_SIG + 2) + exit_bars - 1, NB - 1)]
    return (x - e) * r.pv                                            # (days, 22) gross long points x $; cost added later
