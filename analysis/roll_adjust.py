"""Roll jumps in our continuous (not back-adjusted) 1-minute futures data, for multi-day / overnight tests (2026-10-18).
A roll shows up as one price jump at a session break (the export switches contract at a reopen). For each market's roll
window (calendar, below) the largest break gap is taken as the roll if it is > 4x the market's median break gap.
roll_jumps(g, sym) -> Series {minute index of the first new-contract bar: jump in points}.
"""
import numpy as np, pandas as pd

WINDOWS = {  # (months, first day, last day) where the data's front contract changes
    "ES": ((3, 6, 9, 12), 5, 16), "NQ": ((3, 6, 9, 12), 5, 16), "YM": ((3, 6, 9, 12), 5, 16), "6E": ((3, 6, 9, 12), 5, 16),
    "ZN": ((2, 5, 8, 11), 18, 31), "CL": (tuple(range(1, 13)), 10, 26), "GC": ((1, 3, 5, 7, 9, 11), 18, 31),
}


def break_gaps(g):
    c = g.c.ravel(); ok = np.flatnonzero(~np.isnan(c))
    step = np.diff(ok); brk = ok[1:][step >= 30]                 # first bar after a >= 30-minute pause
    prev = ok[:-1][step >= 30]
    return pd.DataFrame(dict(j=brk, gap=c[brk] - c[prev], gap_open=g.o.ravel()[brk] - c[prev],
                             ts=pd.to_datetime(g.ts[brk // 1440]) + pd.to_timedelta(brk % 1440, "m")))


def roll_jumps(g, sym, mult=4.0):
    b = break_gaps(g); months, d0, d1 = WINDOWS[sym]
    med = b.gap_open.abs().median(); out = {}
    for (y, m), grp in b.groupby([b.ts.dt.year, b.ts.dt.month]):
        if m not in months: continue
        w = grp[(grp.ts.dt.day >= d0) & (grp.ts.dt.day <= d1)]
        if not len(w): continue
        k = w.gap_open.abs().idxmax()
        if abs(w.at[k, "gap_open"]) > mult * med: out[int(w.at[k, "j"])] = float(w.at[k, "gap_open"])
    return pd.Series(out, dtype=float)


def adjusted_close(g, sym, minutes):
    """Close at the given flat minute indices, back-adjusted by subtracting later roll jumps (difference adjustment)."""
    cf = pd.Series(g.c.ravel()).ffill().to_numpy(); px = cf[minutes]
    J = roll_jumps(g, sym)
    adj = np.zeros(len(minutes))
    for j, jump in J.items():
        adj[minutes < j] += jump                                  # earlier prices shifted onto the newest contract
    return px + adj, J
