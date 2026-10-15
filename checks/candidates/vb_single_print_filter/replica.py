"""Checker replica of vb_single_print_filter, built from spec.md + apex_strategies/NQ_Vault_Break.txt only.

1) Vault Break (longs, 30-min bars, midnight open + 0.30 x ATR15, midnight VWAP, entries 10:00..<14:30 next bar open,
   target 40 / stop 75 pts resolved on 1-minute bars, flat at the 14:30 bar close, max 3 a day, holiday half-day times).
   Costs (CLAUDE.md): $7.25 + 1 tick ($5) per market/stop fill (entry, stop, EOD); target = limit, no slippage.
2) Interior single-print flag on the previous regular session (13 x 30-min bars closing 9:00..15:00).
Writes replica_trades.csv (date, side, net, gross, kept) and replica_flags.csv.
"""
import sys, pickle
sys.path.insert(0, "analysis")
import numpy as np, pandas as pd

g = pickle.load(open("scratch_data/g24.pkl", "rb"))
B = g.bars(30)
O, H, L, C, V = B["o"], B["h"], B["l"], B["c"], B["v"]
J = B["j"]                        # bar i closes at minute J[i]
TIME = (J // 60) * 100 + J % 60    # hhmm of bar close (0 = 00:00)
ts = pd.DatetimeIndex(g.ts)
PT, TICK = 20.0, 0.25

# ---------- daily true range per calendar date (chart bars of that date), weekdays stored ----------
has = ~np.isnan(C).all(1)
dhi = np.nanmax(np.where(np.isnan(H), -np.inf, H), 1); dlo = np.nanmin(np.where(np.isnan(L), np.inf, L), 1)
dlast = np.array([r[~np.isnan(r)][-1] if ok else np.nan for r, ok in zip(C, has)])
atr = np.full(g.D, np.nan); hist = []; prevclose = np.nan
for d in range(g.D):
    if len(hist) >= 15: atr[d] = np.mean(hist[-15:])
    if has[d]:
        if ts[d].dayofweek < 5:
            tr = (max(dhi[d], prevclose) - min(dlo[d], prevclose)) if not np.isnan(prevclose) else dhi[d] - dlo[d]
            hist.append(tr)
        prevclose = dlast[d]


def early(dt):
    m, dd, dow, y = dt.month, dt.day, dt.dayofweek, dt.year   # pandas dow Mon=0
    wk = dow < 5
    return ((m == 1 and ((dd == 1 and wk) or (dd == 2 and dow == 0))) or (m == 1 and dow == 0 and 15 <= dd <= 21)
            or (m == 2 and dow == 0 and 15 <= dd <= 21) or (m == 5 and dow == 0 and dd >= 25)
            or (m == 6 and y >= 2022 and ((dd == 19 and wk) or (dd == 18 and dow == 4) or (dd == 20 and dow == 0)))
            or (m == 7 and (((dd in (3, 4)) and wk) or (dd == 5 and dow == 0))) or (m == 9 and dow == 0 and dd <= 7)
            or (m == 11 and dow == 3 and 22 <= dd <= 28) or (m == 11 and dow == 4 and 23 <= dd <= 29)
            or (m == 12 and (((dd in (24, 25)) and wk) or (dd == 26 and dow == 0))))


# ---------- Vault Break ----------
trades = []
for d in g.trading:
    if np.isnan(atr[d]) or not has[d]: continue
    dt = ts[d]
    if dt.year < 2018: continue
    le, fl = (1100, 1130) if early(dt) else (1430, 1430)
    valid = ~np.isnan(C[d])
    first = np.argmax(valid); sess_open = O[d, first]
    noise = sess_open + 0.30 * atr[d]
    tp = (H[d] + L[d] + C[d]) / 3; vv = np.nan_to_num(V[d])
    vwap = np.cumsum(np.nan_to_num(tp) * vv) / np.maximum(np.cumsum(vv), 1e-9)
    ntr = 0; pos_exit_j = -1   # minute column at which the open position ended (exit fill time)
    i = 0; nb = len(J)
    while i < nb - 1:
        if valid[i] and pos_exit_j < J[i] and TIME[i] >= 1000 and TIME[i] < le and ntr < 3 \
                and C[d, i] > noise and C[d, i] > vwap[i]:
            # buy next bar at market: open of the next 30-min bar = first 1-min open after J[i]
            j0 = J[i] + 1
            mins = np.where(~np.isnan(g.o[d, j0:]))[0]
            if len(mins) == 0: break
            je = j0 + mins[0]; entry = g.o[d, je]
            ntr += 1
            tgt, stp = entry + 40, entry - 75
            flat_j = g.jof(fl)
            # last available minute at or before flatten bar close
            ex = None
            for j in range(je, min(flat_j, 1439) + 1):
                if np.isnan(g.c[d, j]): continue
                if j > je and g.o[d, j] <= stp: ex = (g.o[d, j], "stop", j); break      # gap through stop
                if j > je and g.o[d, j] >= tgt: ex = (g.o[d, j], "tgt_gap", j); break
                hs, ht = g.l[d, j] <= stp, g.h[d, j] >= tgt
                if hs and ht:   # ambiguous minute: assume stop first (conservative)
                    ex = (stp, "stop", j); break
                if hs: ex = (stp, "stop", j); break
                if ht: ex = (tgt, "tgt", j); break
            if ex is None:
                jj = np.where(~np.isnan(g.c[d, :flat_j + 1]))[0][-1]
                ex = (g.c[d, jj], "eod", flat_j)
            px, kind, xj = ex
            gross = (px - entry) * PT
            fills_slip = 1 + (kind in ("stop", "eod"))
            net = gross - 7.25 - 5.0 * fills_slip
            trades.append(dict(date=dt.strftime("%Y-%m-%d"), side=1, net=net, gross=gross, entry=entry,
                               exit=px, kind=kind, ej=je, xj=xj))
            pos_exit_j = xj
            if kind == "eod": break
            # next decision: first bar close at/after exit minute (bar containing the exit)
            i = int(np.searchsorted(J, xj))
            continue
        i += 1
VB = pd.DataFrame(trades)

# ---------- interior single-print flag ----------
reg = (J >= g.jof(900)) & (J <= g.jof(1500))
assert reg.sum() == 13


def single_print(d, trim_tails=False, min_run=8):
    h, l = H[d, reg], L[d, reg]
    if np.isnan(h).any(): return None
    lo_t = np.round(l / TICK).astype(int); hi_t = np.round(h / TICK).astype(int)
    base = lo_t.min(); top = hi_t.max()
    cnt = np.zeros(top - base + 1, int)
    for a, b in zip(lo_t, hi_t): cnt[a - base:b - base + 1] += 1
    one = cnt == 1
    k = 0; best = 0
    while k < len(one):
        if one[k]:
            s = k
            while k < len(one) and one[k]: k += 1
            e = k - 1
            if trim_tails:
                # drop the tail parts: keep the run only if it is interior after removing extremes
                if s == 0 or e == len(one) - 1: s, e = s, e  # tail touches an extreme -> excluded below
            if s > 0 and e < len(one) - 1 and e - s + 1 >= min_run:
                return True
        else:
            k += 1
    return False


tr = list(g.trading)
flags = []
for n, d in enumerate(tr):
    if n == 0: continue
    p = tr[n - 1]
    sp = single_print(p)
    flags.append(dict(date=ts[d].strftime("%Y-%m-%d"), prev=ts[p].strftime("%Y-%m-%d"), sp_prev=sp,
                      flag=bool(sp) if sp is not None else False, prev_complete=sp is not None))
F = pd.DataFrame(flags)
F.to_csv("checks/candidates/vb_single_print_filter/replica_flags.csv", index=False)
VB = VB.merge(F[["date", "flag"]], on="date", how="left")
VB["kept"] = 1 - VB.flag.fillna(False).astype(bool).astype(int)
VB.to_csv("checks/candidates/vb_single_print_filter/replica_trades.csv", index=False)
print(len(VB), "replica trades;", VB.net.mean(), "avg net; flagged day share", F[F.date >= "2018"].flag.mean())
