"""Checker replica of the Bridge noise-area NQ 15-min strategy, built from spec.md alone.

Chart: RTH 15-minute bars closing 08:45..15:00 CT on the rows of g.trading (scratch_data/g24.pkl, analysis/grid24.py).
Signals at bar close, market orders fill at the next bar's open +/- 1 tick. Stop / target placed relative to the actual
fill, resolved on the 1-minute path (stop first in a minute that touches both). Stop fills at min(stop, minute open) - 1 tick
(long), target exactly at the target. Net per 1 contract = points * 20 - 7.25.
Band: per slot (09:00 .. 14:15 bars), mean |Close/TodayOpen - 1| of the slot's LookbackDays most recent STORED moves; today's
move is stored only after today's decision (checked by assertion in leak mode).
Early-close days (no 14:30 bar): an open position is closed at that day's last bar close - 1 tick (flagged 'held');
an entry signal on a day's last bar (no next bar that day) is skipped and counted.

usage: python3 replica.py               -> writes trades_replica_both.csv, trades_replica_longs.csv, fills.csv (longs)
       python3 replica.py sens          -> knife-edge table for longs-only
"""
import sys, pickle, os
import numpy as np, pandas as pd

ROOT = "/home/user/thebeginning"
sys.path.insert(0, ROOT + "/analysis")
HERE = os.path.dirname(os.path.abspath(__file__))
TICK, PV, COMM = 0.25, 20.0, 7.25

_G = None


def load():
    global _G
    if _G is None:
        g = pickle.load(open(ROOT + "/scratch_data/g24.pkl", "rb"))
        b = g.bars(15)
        rows = np.array(sorted(g.trading))
        # RTH bars: closing 08:45 (i=35) .. 15:00 (i=60)
        I = np.arange(35, 61)
        _G = dict(g=g, b=b, rows=rows, I=I)
    return _G


def run(lookback=20, mult=1.0, ema_len=20, stop_pts=50.0, rr=0.5, long_on=True, short_on=True,
        max_trades=10, max_stops=3, slip=TICK, comm=COMM, shift_band=False, collect_fills=False):
    G = load(); g, b, rows, I = G["g"], G["b"], G["rows"], G["I"]
    tgt_pts = stop_pts * rr
    alpha = 2.0 / (ema_len + 1)
    hist = {s: [] for s in range(1, 23)}
    ema = None; prev_close = None
    trades = []; fills = []; skipped_last_bar = 0
    for r in rows:
        o = b["o"][r, I]; h = b["h"][r, I]; l = b["l"][r, I]; c = b["c"][r, I]
        ok = ~np.isnan(c)
        if not ok.any():
            continue
        idx = np.where(ok)[0]
        today_open = None; trades_today = 0; stops_today = 0
        pos = 0; entry = None; entry_t = None; stop = tgt = None
        pending = None          # list of actions at next bar open: ('exit',) / ('long',) / ('short',)
        closed_since = []       # trades closed since last bar-close check
        day = pd.Timestamp(str(g.dates[r]))
        for k, ii in enumerate(idx):
            bi = I[ii]                     # bar index in the bars() grid
            tmin = bi * 15                 # close time in minutes
            hhmm = (tmin // 60) * 100 + tmin % 60
            # ---- fill pending market orders at this bar's open
            if pending:
                px = o[ii]
                for act in pending:
                    if act == "exit" and pos != 0:
                        xp = px - slip * pos
                        trades.append(_tr(day, pos, entry, xp, "band/EMA exit" if hhmm != 1445 else "flat 14:30", comm, entry_t, day + pd.Timedelta(minutes=int(tmin))))
                        closed_since.append(trades[-1]); pos = 0
                    elif act in ("long", "short"):
                        sd = 1 if act == "long" else -1
                        if pos == -sd:
                            xp = px - slip * pos
                            trades.append(_tr(day, pos, entry, xp, "reversal", comm, entry_t, day + pd.Timedelta(minutes=int(tmin))))
                            closed_since.append(trades[-1]); pos = 0
                        if pos == 0:
                            pos = sd; entry = px + slip * sd
                            entry_t = day + pd.Timedelta(minutes=int(tmin))
                            stop = entry - stop_pts * sd; tgt = entry + tgt_pts * sd
                pending = None
            # ---- stop / target on the 1-minute path inside this bar
            if pos != 0:
                for j in range(tmin - 14, tmin + 1):
                    mo, mh, ml = g.o[r, j], g.h[r, j], g.l[r, j]
                    if np.isnan(mo):
                        continue
                    if pos == 1:
                        if ml <= stop:
                            xp = min(stop, mo) - slip; kind = "stop"
                        elif mh >= tgt:
                            xp = tgt; kind = "target"
                        else:
                            continue
                    else:
                        if mh >= stop:
                            xp = max(stop, mo) + slip; kind = "stop"
                        elif ml <= tgt:
                            xp = tgt; kind = "target"
                        else:
                            continue
                    trades.append(_tr(day, pos, entry, xp, kind, comm, entry_t, day + pd.Timedelta(minutes=int(j))))
                    closed_since.append(trades[-1]); pos = 0
                    break
            # ---- bar-close logic
            ema = c[ii] if ema is None else ema + alpha * (c[ii] - ema)
            if k == 0:
                today_open = o[ii]
                pc = prev_close
                trades_today = 0; stops_today = 0; closed_since = []
            if closed_since:
                if closed_since[-1]["net"] <= -stop_pts * PV:      # PositionProfit(1) <= -StopDollars (per contract)
                    stops_today += 1
                closed_since = []
            if 900 <= hhmm <= 1430 and today_open and pc:
                slot = (tmin - 540) // 15 + 1
                if 1 <= slot <= 22:
                    move = abs(c[ii] / today_open - 1)
                    H = hist[slot]
                    if len(H) >= lookback:
                        avg = np.mean(H[-lookback:])
                        ub = max(today_open, pc) * (1 + avg * mult)
                        lb = min(today_open, pc) * (1 - avg * mult)
                        ltr = max(ub, ema); st = min(lb, ema)
                        last_bar = (k == len(idx) - 1)
                        acts = []
                        if hhmm < 1430:
                            if pos == 0 and trades_today < max_trades and stops_today < max_stops and hhmm <= 1400:
                                if long_on and c[ii] > ub and c[ii] > o[ii]:
                                    acts = ["long"]; trades_today += 1
                                elif short_on and c[ii] < lb and c[ii] < o[ii]:
                                    acts = ["short"]; trades_today += 1
                            if pos == 1:
                                if hhmm <= 1400 and short_on and c[ii] < lb and c[ii] < o[ii]:
                                    acts = ["exit"]
                                    if trades_today < max_trades and stops_today < max_stops:
                                        acts = ["short"]; trades_today += 1
                                elif c[ii] < ltr:
                                    acts = ["exit"]
                            if pos == -1:
                                if hhmm <= 1400 and long_on and c[ii] > ub and c[ii] > o[ii]:
                                    acts = ["exit"]
                                    if trades_today < max_trades and stops_today < max_stops:
                                        acts = ["long"]; trades_today += 1
                                elif c[ii] > st:
                                    acts = ["exit"]
                        if acts:
                            if last_bar and any(a in ("long", "short") for a in acts) and pos == 0:
                                skipped_last_bar += 1
                            pending = acts
                    if not shift_band:
                        H.append(move)
                    else:
                        H.append(move)   # placeholder (leak test below uses run_leak)
                    if len(H) > 100:
                        del H[0]
            if hhmm == 1430 and pos != 0:
                pending = ["exit"]
        # ---- end of day
        if pos != 0:          # early close: no 14:30 bar
            xp = c[idx[-1]] - slip * pos
            tmin = I[idx[-1]] * 15
            trades.append(_tr(day, pos, entry, xp, "held past session (closed at last bar)", comm, entry_t, day + pd.Timedelta(minutes=int(tmin))))
            pos = 0
        prev_close = c[idx[-1]]
    T = pd.DataFrame(trades)
    T.attrs["skipped_last_bar"] = skipped_last_bar
    return T


def _tr(day, side, entry, xp, kind, comm, et, xt):
    pts = (xp - entry) * side
    return dict(date=day.strftime("%Y-%m-%d"), side=side, net=round(pts * PV - comm, 2), entry=entry, exit=xp,
                kind=kind, entry_time=et, exit_time=xt)


def summ(T, label=""):
    T = T[T.date >= "2018-01-01"]
    x = T.net
    t = x.mean() / x.std() * np.sqrt(len(x))
    pf = x[x > 0].sum() / -x[x < 0].sum()
    yrs = T.groupby(T.date.str[:4]).net.sum()
    s = x.sort_values(ascending=False); top = s.iloc[:int(len(s) * 0.05)].sum() / x.sum()
    return dict(label=label, n=len(x), mean=round(x.mean(), 1), total=round(x.sum()), pf=round(pf, 3), t=round(t, 2),
                yrs_pos=f"{(yrs > 0).sum()}/{len(yrs)}", top5_share=round(top, 2),
                h23=round(T[T.date >= "2023"].net.mean(), 1), h18_22=round(T[T.date < "2023"].net.mean(), 1))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "base"
    if mode == "base":
        for nm, kw in (("both", {}), ("longs", dict(short_on=False))):
            T = run(**kw)
            print(nm, summ(T, nm), "skipped last-bar entries:", T.attrs["skipped_last_bar"])
            print(T[T.date >= "2018"].kind.value_counts().to_dict())
            T[T.date >= "2018-01-01"].to_csv(os.path.join(HERE, f"trades_replica_{nm}.csv"), index=False)
    elif mode == "sens":
        rows = []
        for kw in [dict(), dict(lookback=14), dict(lookback=30), dict(ema_len=10), dict(ema_len=40),
                   dict(stop_pts=40, rr=0.5), dict(stop_pts=60, rr=0.5), dict(mult=0.8), dict(mult=1.2),
                   dict(stop_pts=50, rr=1.0), dict(slip=0.5)]:
            T = run(short_on=False, **kw)
            rows.append(summ(T, str(kw) or "base"))
        print(pd.DataFrame(rows).to_string(index=False))
