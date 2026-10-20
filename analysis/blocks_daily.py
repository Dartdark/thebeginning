"""Strategy building blocks on DAILY bars, multi-day holds (2026-10-20): for a personal account (not Apex: holds overnight).

The catalog's entry blocks (analysis/blocks.py ENTRIES) were written for daily / swing charts, so Step 1b runs them as
designed: one bar per trading day, the bar closing at 15:00 CT (window: previous 15:00 -> 15:00), prices back-adjusted
for roll jumps at minute level (roll_adjust.roll_jumps). A signal at the 15:00 close enters at the 15:01 price (market) or,
for stop entries, at the stop level during the next day's bar; exit at 15:01 N trading days after the signal.
Costs per contract round trip = commission + 1 tick a fill; a hold that crosses a roll pays one more round trip.

  d = Daily(g, "GC"); tr = run(d, ENTRIES["E2 close breakout"](d), hold=20)
  tr: date, side, entry, exit, pnl ($ per contract after costs), R (pnl / 20-day ATR in $ at the signal)
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from roll_adjust import roll_jumps
from blocks import ENTRIES   # noqa: F401  (same entry functions; Daily mimics RTH with one bar a day)

SPEC = {"NQ": (20.0, 0.25, 7.25), "ES": (50.0, 0.25, 5.0), "YM": (5.0, 1.0, 5.0), "GC": (100.0, 0.1, 14.5),
        "CL": (1000.0, 0.01, 14.5), "ZN": (1000.0, 1 / 64, 14.5), "6E": (125000.0, 0.00005, 14.5)}


class Daily:
    def __init__(self, g, sym, start="2017-01-01"):
        self.sym = sym; self.pv, self.tick, comm = SPEC[sym]; self.cost = comm + 2 * self.tick * self.pv
        T = np.array([d for d in g.trading if pd.Timestamp(g.ts[d]) >= pd.Timestamp(start)])
        n = g.D * 1440; J = roll_jumps(g, sym); self.jumps = np.array(sorted(J.index), int)
        adj = np.zeros(n + 1)
        for j, jump in J.items(): adj[:j] += jump                       # earlier prices shifted onto the newest contract
        adj = adj[:n]
        o, h, l, c, v = (getattr(g, k).ravel() for k in ("o", "h", "l", "c", "v"))
        self.cf = pd.Series(c).ffill().to_numpy() + adj
        self.of = pd.Series(np.where(np.isnan(o), c, o)).ffill().to_numpy() + adj
        self.hf = np.where(np.isnan(h), -np.inf, h + adj); self.lf = np.where(np.isnan(l), np.inf, l + adj)
        ci = T * 1440 + jof(1500)
        self.ci = ci; self.days = T; self.dates = pd.DatetimeIndex(g.ts[T])
        a = np.r_[0, ci[:-1] + 1]
        self.C = self.cf[ci][:, None]; self.O = self.of[a][:, None]
        self.H = np.array([self.hf[s:e + 1].max() for s, e in zip(a, ci)])[:, None]
        self.L = np.array([self.lf[s:e + 1].min() for s, e in zip(a, ci)])[:, None]
        self.V = np.array([np.nansum(v[s:e + 1]) for s, e in zip(a, ci)])[:, None]
        self.H[0] = self.L[0] = self.C[0]
        pc = np.r_[self.C[0, 0], self.C[:-1, 0]]
        tr_ = np.maximum(self.H[:, 0] - self.L[:, 0], np.maximum(abs(self.H[:, 0] - pc), abs(self.L[:, 0] - pc)))
        self.atr = pd.Series(tr_).rolling(20).mean().to_numpy() * self.pv
        self.flat = lambda x: np.asarray(x).reshape(-1); self.unflat = lambda x: np.asarray(x).reshape(-1, 1)
        self.dow = self.dates.dayofweek.to_numpy()
        ym = self.dates.year * 12 + self.dates.month; self.first_of_month = np.r_[True, ym[1:] != ym[:-1]]


def _rolled(d, a, b): return np.any((d.jumps > a) & (d.jumps <= b))


def run(d, sig, hold=20, start="2018-01-01"):
    rows = []; stop = isinstance(sig, dict) and sig.get("stop"); n = len(d.days)
    k0 = int(np.searchsorted(d.dates, pd.Timestamp(start)))
    k = max(k0, 60)
    while k < n - hold:
        if stop:
            b, s = sig["buy"][k, 0], sig["sell"][k, 0]
            if np.isnan(b) or np.isnan(s): k += 1; continue
            lo, hi_ = d.ci[k] + 1, d.ci[k + 1] + 1; side = 0
            for m in range(lo, hi_):
                ub, dn = d.hf[m] >= b, d.lf[m] <= s
                if ub and dn: break
                if ub: side, e, em = 1, max(b, d.of[m]), m; break
                if dn: side, e, em = -1, min(s, d.of[m]), m; break
            if side == 0: k += 1; continue
        else:
            side = int(sig[k, 0])
            if side == 0: k += 1; continue
            em = d.ci[k] + 1; e = d.cf[em]
        xm = d.ci[k + hold] + 1; x = d.cf[xm]
        pnl = (x - e) * side * d.pv - d.cost * (2 if _rolled(d, em, xm) else 1)
        rows.append((d.dates[k], side, e, x, pnl, pnl / d.atr[k] if d.atr[k] > 0 else np.nan, k))
        k += hold                                                         # next signal from the exit day's close
    return pd.DataFrame(rows, columns=["date", "side", "entry", "exit", "pnl", "R", "k"])


def placebo_R(d, tr, hold, rng):
    """Same sides and hold, market entries at the 15:01 price on random signal days."""
    n = len(d.days); k0 = max(int(np.searchsorted(d.dates, pd.Timestamp("2018-01-01"))), 60)
    k = rng.integers(k0, n - hold, len(tr)); em = d.ci[k] + 1; xm = d.ci[k + hold] + 1
    pnl = (d.cf[xm] - d.cf[em]) * tr.side.to_numpy() * d.pv - d.cost
    return pnl / d.atr[k]
