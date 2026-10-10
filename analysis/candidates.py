"""Candidate NQ strategies for the multi-strategy Apex plan, as signal generators
for grid.execute(). Each function returns (signals DataFrame, execute kwargs).
Used in the plan (multi_strategy/README.md): vault_break, opening_drive
(mode="follow"), gap_fade (experimental). The others were tested and dropped.

All decisions use only information available at the decision bar's close;
entries fill at the next bar's open. Data: 1-minute bars 08:00-15:15 CT.

  vault_break   the user's Vault Break: long when a 30-minute close is above
                both the noise level (session open + 30% of the 15-day ATR)
                and VWAP, 10:00-14:30 CT. The original anchors the session
                open and VWAP at midnight; the exports start at 08:00 CT, so
                here they are anchored at 08:00 (approximation, see README).
  orb           opening-range breakout: a 5-minute close outside the
                08:30-09:00 range, entries 09:00-11:00 (the window the VWAP
                strategy never trades)
  vwap_fade     counter-trend: fade a stretched move far from VWAP back
                toward it
  late_mom      intraday momentum: the day's direction since the open,
                traded in the last part of the session
  gap_fade      fade the overnight gap at the 08:30 open toward the previous close
  opening_drive the first 30 minutes' direction, faded or followed
  lunch_revert  midday RSI(2) mean reversion
  prior_level   previous day's high/low breakout or failed breakout
"""
import numpy as np
import pandas as pd
from grid import j_of, NMIN


def daily_atr(g, n=15):
    """ATR of the previous n days from the 08:00-15:15 bars (true range with the
    previous day's last close). Known before today's session."""
    hi = np.nanmax(g.h, axis=1); lo = np.nanmin(g.l, axis=1)
    last = np.array([r[~np.isnan(r)][-1] for r in g.c])
    pc = np.r_[np.nan, last[:-1]]
    tr = np.nanmax(np.c_[hi - lo, np.abs(hi - pc), np.abs(lo - pc)], axis=1)
    return pd.Series(tr).rolling(n).mean().shift(1).to_numpy()


def _sig(g, mask, bars, side, stop, target, exit_hhmm, early_exit=None):
    """Signals from a (D, K) boolean mask on k-minute bars."""
    d, k = np.nonzero(mask)
    xj = np.full(len(d), j_of(exit_hhmm))
    return pd.DataFrame(dict(day=d, dj=bars["j"][k], side=side if np.ndim(side) == 0 else side[d, k],
                             stop=stop if np.ndim(stop) == 0 else stop[d, k],
                             target=target if np.ndim(target) == 0 else target[d, k],
                             exit_j=xj))


def vault_break(g, atr_n=15, mult=0.30, anchor=800, first=1000, last=1430,
                tp_usd=800, sl_usd=1500, max_trades=3, bar_mins=30, flat=1430):
    b = g.bars(bar_mins)
    atr = daily_atr(g, atr_n)
    sess_open = g.o[:, j_of(anchor) + 1]
    noise = sess_open + mult * atr
    vw = g.vwap_from(anchor)[:, b["j"]]
    t = b["j"] + 480; t = (t // 60) * 100 + t % 60           # bar close HHMM
    win = (t >= first) & (t < last)
    m = (b["c"] > noise[:, None]) & (b["c"] > vw) & win[None, :]
    s = _sig(g, m, b, 1, sl_usd / 20.0, tp_usd / 20.0, flat)
    return s, dict(max_trades=max_trades)


def orb(g, or_start=830, or_end=900, last=1100, flat=1455, stop_frac=1.0,
        tgt_frac=1.0, min_or=0, max_or=1e9, max_trades=1, side_filter=0):
    """Close outside the opening range; stop/target as fractions of its height."""
    b = g.bars(5)
    a, e = j_of(or_start) + 1, j_of(or_end)
    with np.errstate(all="ignore"):
        hi = np.nanmax(g.h[:, a:e + 1], axis=1); lo = np.nanmin(g.l[:, a:e + 1], axis=1)
    rng = hi - lo
    t = b["j"] + 480; t = (t // 60) * 100 + t % 60
    win = (t >= or_end) & (t < last)
    okr = (rng >= min_or) & (rng <= max_or)
    up = (b["c"] > hi[:, None]) & win & okr[:, None]
    dn = (b["c"] < lo[:, None]) & win & okr[:, None]
    if side_filter > 0: dn[:] = False
    if side_filter < 0: up[:] = False
    # first breakout only: the first bar where either is true
    m = up | dn
    first = m & (np.cumsum(m, axis=1) == 1)
    side = np.where(up, 1, -1)
    R = np.repeat(rng[:, None], m.shape[1], axis=1)
    s = _sig(g, first, b, side, R * stop_frac, R * tgt_frac, flat)
    return s, dict(max_trades=max_trades)


def vwap_fade(g, dist_pct=0.6, first=1000, last=1400, flat=1455, stop_pts=60.0,
              tgt="vwap", tgt_pts=40.0, max_trades=2, anchor=830, mom_bars=0):
    """Fade a 5-minute close at least dist_pct beyond VWAP (from the 08:30 open),
    on a reversal candle (red after green above, green after red below)."""
    b = g.bars(5)
    vw = g.vwap_from(anchor)[:, b["j"]]
    t = b["j"] + 480; t = (t // 60) * 100 + t % 60
    win = (t >= first) & (t < last)
    dist = (b["c"] - vw) / vw * 100
    red = b["c"] < b["o"]; green = b["c"] > b["o"]
    prev_green = np.c_[np.zeros((g.D, 1), bool), green[:, :-1]]
    prev_red = np.c_[np.zeros((g.D, 1), bool), red[:, :-1]]
    sh = (dist >= dist_pct) & red & prev_green & win
    lg = (dist <= -dist_pct) & green & prev_red & win
    m = sh | lg
    side = np.where(sh, -1, 1)
    if tgt == "vwap":
        tp = np.abs(b["c"] - vw)
    else:
        tp = np.full(m.shape, tgt_pts)
    s = _sig(g, m, b, side, stop_pts, tp, flat)
    return s, dict(max_trades=max_trades, max_losses=1)


def late_mom(g, ref=830, decide=1400, flat=1510, min_pct=0.25, stop_pts=60.0,
             tgt_pts=np.inf, vw_confirm=True):
    """At `decide`, trade in the direction of the move since `ref` if it is at
    least min_pct; hold to `flat`."""
    j = j_of(decide)
    p0 = g.o[:, j_of(ref) + 1]
    c = g.c[:, j]
    ret = (c / p0 - 1) * 100
    vw = g.vwap_from(ref)[:, j]
    up = ret >= min_pct; dn = ret <= -min_pct
    if vw_confirm:
        up &= c > vw; dn &= c < vw
    d = np.nonzero(up | dn)[0]
    s = pd.DataFrame(dict(day=d, dj=j, side=np.where(up[d], 1, -1), stop=stop_pts,
                          target=tgt_pts, exit_j=j_of(flat)))
    return s, dict(max_trades=1)


def gap_fade(g, min_gap=0.15, max_gap=1.0, open_hhmm=830, last=900, flat=1000,
             stop_mult=1.0, max_trades=1, risk_usd=None):
    """Fade the overnight gap at the 08:30 open toward the previous session's
    15:15 close. Gap = open vs previous close in %. Target = the gap fill,
    stop = stop_mult x gap size beyond the entry."""
    j0 = j_of(open_hhmm)                      # decide at the close of the 08:30 bar
    op = g.c[:, j0]                           # last price before the open (known at decision)
    pc = np.array([np.nan] + [r[~np.isnan(r)][-1] for r in g.c[:-1]])
    gap = (op / pc - 1) * 100
    ok = (np.abs(gap) >= min_gap) & (np.abs(gap) <= max_gap)
    d = np.nonzero(ok)[0]
    side = np.where(gap[d] > 0, -1, 1)
    size = np.abs(op[d] - pc[d])
    s = pd.DataFrame(dict(day=d, dj=j0, side=side, stop=size * stop_mult, target=size,
                          exit_j=j_of(flat)))
    if risk_usd:
        s["qty"] = np.floor(risk_usd / (s["stop"] * 2.0)) / 10.0
    return s, dict(max_trades=max_trades)


def opening_drive(g, start=830, decide=900, flat=1000, min_pct=0.3, mode="fade",
                  stop_pts=50.0, tgt_pts=np.inf):
    """Direction of the first 30 minutes, at `decide`: fade it or follow it."""
    j = j_of(decide)
    p0 = g.o[:, j_of(start) + 1]
    ret = (g.c[:, j] / p0 - 1) * 100
    ok = np.abs(ret) >= min_pct
    d = np.nonzero(ok)[0]
    side = np.sign(ret[d]).astype(int) * (-1 if mode == "fade" else 1)
    s = pd.DataFrame(dict(day=d, dj=j, side=side, stop=stop_pts, target=tgt_pts,
                          exit_j=j_of(flat)))
    return s, dict(max_trades=1)


def rsi(x, n):
    d = np.diff(x, axis=1, prepend=np.nan)
    up = np.where(d > 0, d, 0.0); dn = np.where(d < 0, -d, 0.0)
    out = np.full(x.shape, np.nan)
    au = pd.DataFrame(up.T).ewm(alpha=1 / n, adjust=False).mean().T.to_numpy()
    ad = pd.DataFrame(dn.T).ewm(alpha=1 / n, adjust=False).mean().T.to_numpy()
    with np.errstate(all="ignore"):
        out = 100 - 100 / (1 + au / ad)
    return out


def lunch_revert(g, n=2, lo=10, hi=90, first=1030, last=1300, flat=1330,
                 stop_pts=40.0, tgt_pts=20.0, bar_mins=5, max_trades=2):
    """Midday mean reversion: RSI(n) of 5-minute closes (within the day)
    below lo -> long, above hi -> short; quick target, time exit."""
    b = g.bars(bar_mins)
    r = rsi(b["c"], n)
    t = b["j"] + 480; t = (t // 60) * 100 + t % 60
    win = (t >= first) & (t < last)
    lg = (r <= lo) & win; sh = (r >= hi) & win
    m = lg | sh
    s = _sig(g, m, b, np.where(lg, 1, -1), stop_pts, tgt_pts, flat)
    return s, dict(max_trades=max_trades, max_losses=1)


def prior_level(g, mode="break", first=900, last=1300, flat=1455, stop_pts=40.0,
                tgt_pts=80.0, max_trades=1, buffer_pts=0.0):
    """Prior day's regular-session high/low. break: 5-minute close beyond it ->
    follow. fail: price pokes beyond it then closes back inside -> fade."""
    b = g.bars(5)
    ph, pl = g.prev_high[:, None], g.prev_low[:, None]
    t = b["j"] + 480; t = (t // 60) * 100 + t % 60
    win = (t >= first) & (t < last)
    if mode == "break":
        lg = (b["c"] > ph + buffer_pts) & win; sh = (b["c"] < pl - buffer_pts) & win
    else:
        lg = (b["l"] < pl) & (b["c"] > pl) & win; sh = (b["h"] > ph) & (b["c"] < ph) & win
    m = lg | sh
    first_ = m & (np.cumsum(m, axis=1) == 1)
    s = _sig(g, first_, b, np.where(lg, 1, -1), stop_pts, tgt_pts, flat)
    return s, dict(max_trades=max_trades)
