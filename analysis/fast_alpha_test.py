"""Fast alphas as an execution overlay (Zarattini & Pagani, Concretum QuanTips #2, Feb 2026; user's upload 2026-10-14).

Paper (SPY 5-min, 2007-26): after a streak of N same-direction 5-minute bars the next bar reverts (0.1-0.4 bp); traded
alone it loses after commissions. Used as an overlay on an ATR breakout (open +- 0.5 ATR(14), checked at 15-minute closes,
stop back at the open, flat at the close) - enter only after a 5-minute bar against the breakout, exit a stop only after a
5-minute bar in the trade's favour - CAGR +2 pp, Sharpe 0.86 -> 0.99.
Here, NQ 2018-2026, regular session 8:30-15:00 CT, $7.25 + 1 tick per market fill, 1 NQ:
  1. The fast alpha on NQ: next 5-min bar after streaks of N >= 1..5 (points, t, 2018-22 / 2023-26); standalone N = 1.
  2. The paper's baseline breakout and the overlay (entries, exits, both); control = the same delays at random (each
     trade gets another trade's overlay delay), so "waiting" is separated from "waiting for a counter bar".
  3. The overlay on the plan's MultiCharts trades (VB, ONB ML v2, ONB ADX30, Monday, EOS, LDF, NFP): delay each entry to
     the close of the first 5-min bar against the trade (max wait 15 / 30 / 60 min, then enter anyway or skip), same
     exit price and time (brackets fixed in price; a trade whose exit comes first is missed); plus the random-delay control.
  python3 analysis/fast_alpha_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from alpha101_test import daily_bars
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 20.0, 0.25, 7.25
SPLIT = pd.Timestamp("2023-01-01")


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def fast_alpha(g):
    rows = g.trading; J = np.arange(jof(835), jof(1500) + 1, 5)
    C = pd.DataFrame(g.c[rows][:, np.r_[jof(830), J]]).ffill(axis=1).to_numpy()
    r = np.diff(C, axis=1)                      # 5-min bar point changes 8:35 .. 15:00
    lr = np.diff(np.log(C), axis=1) * 1e4
    yrs = pd.DatetimeIndex(g.ts[rows]).year.to_numpy()
    out = []
    sg = np.sign(r)
    for N in range(1, 6):
        for d, nm in ((-1, "down"), (1, "up")):
            m = np.ones_like(r[:, N - 1:-1], dtype=bool)
            for k in range(N):
                m &= sg[:, N - 1 - k:r.shape[1] - 1 - k] == d
            nxt = r[:, N:]; nb = lr[:, N:]
            Y = np.repeat(yrs[:, None], nxt.shape[1], 1)
            v, b, y = nxt[m], nb[m], Y[m]
            out.append(dict(N=N, streak=nm, per_day=m.sum() / len(rows), next_pts=v.mean(), next_bp=b.mean(), t=tstat(v),
                            pts_18_22=v[y < 2023].mean(), pts_23_26=v[y >= 2023].mean()))
    # standalone N = 1 always-in reversal: position -sign(r_t) over bar t+1, cost per change of position
    pos = -sg[:, :-1]; pnl = pos * r[:, 1:] * PV
    flips = np.abs(np.diff(np.c_[np.zeros(len(rows)), pos, np.zeros(len(rows))], axis=1)).sum(1)  # contracts traded
    gross = pnl.sum(1); cost = flips / 2 * (COMM + 2 * TICK * PV)
    return pd.DataFrame(out), pd.DataFrame(dict(gross=gross, net=gross - cost, trades=flips / 2), index=pd.DatetimeIndex(g.ts[rows]))


def counter_bar(cf, t0, side, want, tmax):
    """First 5-min bar ending at an absolute minute t >= t0 (on the 5-min grid) whose close-to-close change has the sign
    `want * side` (want = -1: against the trade, +1: with it). Returns t or None if none by tmax."""
    t = int(np.ceil(t0 / 5.0) * 5)
    while t <= tmax:
        ch = cf[t] - cf[t - 5]
        if np.isfinite(ch) and np.sign(ch) == want * side: return t
        t += 5
    return None


def breakout(g, atr, cf, entry_overlay=False, exit_overlay=False, delays=None, rng=None):
    """Paper baseline on NQ. delays: None, or an array to draw random entry delays (minutes) from (control)."""
    out = []; chk = [jof(845) + 15 * i for i in range(25)]            # 8:45 .. 14:45 checkpoints
    eod = jof(1500)
    for d in g.trading:
        O = g.o[d, jof(831)]; a = atr[d]
        if not (np.isfinite(O) and np.isfinite(a)): continue
        U, L = O + 0.5 * a, O - 0.5 * a; base = d * 1440
        pos = 0; ent = None; tbusy = -1
        for t in chk:
            if t <= tbusy: continue
            c = cf[base + t]
            if pos == 0:
                s = 1 if c > U else (-1 if c < L else 0)
                if s == 0: continue
                te = t
                if entry_overlay:
                    te = counter_bar(cf, base + t + 5, s, -1, base + eod - 5)
                    if te is None: continue
                    te -= base
                elif delays is not None:
                    te = t + int(rng.choice(delays))
                    if te >= eod: continue
                # cancel if the stop level was crossed while waiting (checked at the entry time)
                px = cf[base + te]
                if s * (px - O) <= 0: tbusy = te; continue
                pos, ent, j0 = s, px + s * TICK, te; tbusy = te
            else:
                if pos * (c - O) <= 0:
                    tx = t
                    if exit_overlay:
                        tx = counter_bar(cf, base + t + 5, pos, +1, base + eod)
                        tx = eod if tx is None else tx - base
                    px = cf[base + tx]
                    out.append(dict(date=pd.Timestamp(g.ts[d]), side=pos, j0=j0, j1=tx, entry=ent, exit=px - pos * TICK, kind=0))
                    pos = 0; tbusy = tx
        if pos != 0:
            px = cf[base + eod]
            out.append(dict(date=pd.Timestamp(g.ts[d]), side=pos, j0=j0, j1=eod, entry=ent, exit=px - pos * TICK, kind=2))
    t = pd.DataFrame(out); t["net"] = (t.exit - t.entry) * t.side * PV - COMM
    return t


def stats(t, col="net"):
    x = t[col]; y = t.date.dt.year; by = x.groupby(y).sum()
    return dict(n=len(x), avg=x.mean(), pf=x[x > 0].sum() / max(1e-9, -x[x < 0].sum()), t=tstat(x), yrs=f"{(by > 0).sum()}/{len(by)}",
                d=x[y < 2023].mean(), h=x[y >= 2023].mean(), L=x[t.side > 0].mean(), S=x[t.side < 0].mean())


def overlay_plan(t, cf, wait, mode, rand_delays=None, rng=None):
    """Delay each entry to the close of the first 5-min bar against the trade. mode 'enter' = enter anyway after `wait`
    minutes, 'skip' = skip the trade. Exit price / time unchanged; trades exiting before the new entry are missed."""
    rows = []
    for r in t.itertuples():
        e0 = int(r.day) * 1440 + int(r.j0) - 1          # minute whose close ~ the original fill
        x1 = int(r.day) * 1440 + int(r.j1)
        if rand_delays is not None:
            dl = int(rng.choice(rand_delays)); te = e0 + dl if dl > 0 else None
        else:
            te = counter_bar(cf, e0 + 1, int(r.side), -1, e0 + wait)
            dl = None
        if rand_delays is None and te is None:
            if mode == "skip": rows.append(dict(date=r.date, side=r.side, net=0.0, old=r.net, delay=np.nan, missed=1)); continue
            te = e0 + wait
        if te is None or te - e0 <= 0:
            rows.append(dict(date=r.date, side=r.side, net=r.net, old=r.net, delay=0, missed=0)); continue
        if te >= x1:
            rows.append(dict(date=r.date, side=r.side, net=0.0, old=r.net, delay=te - e0, missed=1)); continue
        ne = cf[te] + r.side * TICK
        net = (r.exit - ne) * r.side * PV - COMM
        rows.append(dict(date=r.date, side=r.side, net=net, old=r.net, delay=te - e0, missed=0, gain_pts=r.side * (r.entry - ne)))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    print(__doc__.split("\n")[0])

    print("\n1. The fast alpha on NQ (regular session 5-min bars): next bar after a streak of >= N bars")
    F, S1 = fast_alpha(g)
    print(F.to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
    print(f"   standalone N = 1 reversal, always in: gross ${S1.gross.mean():,.0f} a day, {S1.trades.mean():.0f} round trips a day,"
          f" net ${S1.net.mean():,.0f} a day (cost per round trip ${COMM + 2 * TICK * PV:.2f} vs gross ${S1.gross.sum() / S1.trades.sum():.2f})")

    print("\n2. The paper's breakout (open +- 0.5 x RTH ATR(14), 15-min checks, stop at the open, flat 15:00 CT), 1 NQ")
    B = daily_bars(g)
    tr = np.maximum(B.high - B.low, np.maximum(abs(B.high - B.close.shift()), abs(B.low - B.close.shift())))
    atr = np.full(g.D, np.nan); atr[B.row.values] = tr.rolling(14).mean().shift(1).values
    V = {"baseline": breakout(g, atr, cf), "entry overlay": breakout(g, atr, cf, entry_overlay=True),
         "exit overlay": breakout(g, atr, cf, exit_overlay=True), "both (paper)": breakout(g, atr, cf, True, True)}
    # entry delays of the overlay vs the baseline signal time: rebuild by matching day / side order
    base_first = V["baseline"].groupby("date").j0.first(); ov_first = V["entry overlay"].groupby("date").j0.first()
    dd = (ov_first - base_first.reindex(ov_first.index)).dropna(); dd = dd[(dd > 0) & (dd < 300)].astype(int).values
    rng = np.random.default_rng(3)
    V["random delay (control)"] = breakout(g, atr, cf, delays=dd, rng=rng)
    rows = {k: stats(v) for k, v in V.items()}
    print(pd.DataFrame(rows).T.to_string(float_format=lambda v: f"{v:,.1f}"))
    print(f"   overlay entry delay: median {np.median(dd):.0f} min (mean {dd.mean():.0f})")
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days >= pd.Timestamp("2018-01-01")]
    dl = lambda t: t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    tab = {}
    for k in ("baseline", "both (paper)"):
        t = V[k]; tab[k] = (dl(t), t.net); tab[k + " longs"] = (dl(t[t.side > 0]), t[t.side > 0].net); tab[k + " shorts"] = (dl(t[t.side < 0]), t[t.side < 0].net)
    print(M.table(tab))
    b_, p_ = R.report({k: dl(V[k])[days >= SPLIT] for k in ("baseline", "both (paper)")}, n=3000); print(b_); print(p_)

    print("\n3. The overlay on the plan's MultiCharts trades (entry delayed to the first 5-min bar against the trade)")
    from time_clusters_test import trades
    T = trades(g)
    out = []
    for k in ("VB", "ONB_ML2_MC", "ONB_ADX30", "MON_MC", "EOS", "LDF_MC", "NFP_MC"):
        t = T[k]
        for wait in (15, 30, 60):
            for mode in ("enter", "skip"):
                o = overlay_plan(t, cf, wait, mode)
                ctrl = []
                dly_ = o.delay.dropna().astype(int).values
                for s in range(5):
                    c = overlay_plan(t, cf, wait, mode, rand_delays=dly_, rng=np.random.default_rng(s)); ctrl.append(c.net.mean())
                y = o.date.dt.year
                out.append(dict(strategy=k, wait=wait, mode=mode, n=len(o), old=o.old.mean(), new=o.net.mean(), diff=(o.net - o.old).mean(),
                                t_diff=tstat(o.net - o.old), d18_22=(o.net - o.old)[y < 2023].mean(), d23_26=(o.net - o.old)[y >= 2023].mean(),
                                missed=o.missed.mean(), med_delay=o.delay.median(), random_delay=np.mean(ctrl)))
    P = pd.DataFrame(out)
    print(P.to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
    pickle.dump(dict(F=F, V=V, P=P), open(SP + "fast_alpha.pkl", "wb"))
