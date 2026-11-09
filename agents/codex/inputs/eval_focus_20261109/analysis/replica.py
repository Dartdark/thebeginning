"""Python replica of NQ_VWAP_Momentum.txt, run on 1-minute bars exported by
NQ_Bar_Exporter.txt (CT exchange time, bar-close timestamps, 08:00-15:15).

Mirrors the MultiCharts setup used for the v2.1 backtest:
  - 5-minute signal bars built from the 1-minute bars
  - 15-minute VWAP anchored at 08:30 CT, built from bar (H+L+C)/3 x volume
  - entries at the next 5-minute bar's open
  - stop / target checked on 1-minute bars (Bar Magnifier), intrabar path
    O-H-L-C when the open is nearer the high, else O-L-H-C
  - profit target fills only when price trades through it by FILL_THROUGH
    points ("Fill limit price exceeded by 1 points"), stop fills at the stop
    or at the bar open if it gapped through
  - flatten on the close of the 5-minute bar at the day's flatten time
Prices and P&L are per 1 NQ ($20/point), before costs.

Calibration against the MultiCharts v2.1 trade list (5,234 trades): every
MultiCharts entry is at 09:50 or later although NoTradeUntil is 900, so the
replica starts entries at the 09:45 decision (no_trade_until=945). With that,
88% of MultiCharts trades are reproduced exactly (same bar, side, entry
price; P&L identical on 99%), daily first entries agree on 84% of days, and
win rate / average trade / Apex pass rates agree closely. Remaining
differences are marginal VWAP-slope signals. Treat results as exploratory
and confirm any change with a MultiCharts backtest.
"""
import glob
import numpy as np
import pandas as pd

POINT_VALUE = 20.0
FILL_THROUGH = 1.0

DEFAULTS = dict(
    anchor=830, vwap_mins=15, momentum_mins=60, min_change_pct=0.1,
    stop_pts=80.0, long_target_pts=40.0, short_target_pts=50.0,
    use_pct_exits=False, stop_pct=0.30, long_target_pct=0.15, short_target_pct=0.19,
    no_trade_until=945, last_entry=1430, flatten=1455,
    use_holiday_times=True, early_last_entry=1100, early_flatten=1145,
    trade_longs=True, trade_shorts=True,
    max_trades=4, max_losses=2,
    entry_filter=None,          # optional callable(day_info: dict, side: int) -> bool
    momentum_rth_only=False,    # momentum lookback counts only bars after the anchor (RTH session chart)
)


def load_bars(pattern):
    files = sorted(glob.glob(pattern))
    d = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    d = d.drop_duplicates(["date", "time"]).sort_values(["date", "time"])
    return d.reset_index(drop=True)


def to_mins(hhmm):
    return (hhmm // 100) * 60 + hhmm % 100


def is_early_close(ts):
    mo, dom, yr = ts.month, ts.day, ts.year
    dow = (ts.weekday() + 1) % 7          # 0 = Sunday, like PowerLanguage
    wk = 1 <= dow <= 5
    return ((mo == 1 and ((dom == 1 and wk) or (dom == 2 and dow == 1)))
            or (mo == 1 and dow == 1 and 15 <= dom <= 21)
            or (mo == 2 and dow == 1 and 15 <= dom <= 21)
            or (mo == 5 and dow == 1 and dom >= 25)
            or (mo == 6 and yr >= 2022 and ((dom == 19 and wk) or (dom == 18 and dow == 5)
                                            or (dom == 20 and dow == 1)))
            or (mo == 7 and (((dom == 3 or dom == 4) and wk) or (dom == 5 and dow == 1)))
            or (mo == 9 and dow == 1 and dom <= 7)
            or (mo == 11 and dow == 4 and 22 <= dom <= 28)
            or (mo == 11 and dow == 5 and 23 <= dom <= 29)
            or (mo == 12 and (((dom == 24 or dom == 25) and wk) or (dom == 26 and dow == 1))))


def _five_minute(day):
    """Group one day's 1-minute bars into 5-minute bars stamped at their close."""
    m = to_mins(day["time"].to_numpy())
    key = ((m + 4) // 5) * 5                       # 08:01..08:05 -> 08:05
    day = day.assign(key=key)
    g = day.groupby("key", sort=True)
    five = pd.DataFrame({
        "open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(),
        "close": g["close"].last(), "volume": g["volume"].sum(),
        "first": g.apply(lambda x: x.index[0], include_groups=False),
        "last": g.apply(lambda x: x.index[-1], include_groups=False),
    })
    five["time"] = (five.index // 60) * 100 + five.index % 60
    return five.reset_index(drop=True)


def _walk_exit(m1, i0, i1, side, entry, stop_px, tgt_px):
    """Scan 1-minute bars i0..i1 for the stop or target. Returns (idx, price, kind) or None."""
    for i in range(i0, i1 + 1):
        o, h, l = m1["open"][i], m1["high"][i], m1["low"][i]
        if side > 0:
            if o <= stop_px:
                return i, o, "Stop Loss"
            hit_t = h >= tgt_px + FILL_THROUGH
            hit_s = l <= stop_px
            if hit_t and hit_s:
                return (i, tgt_px, "Profit Target") if (h - o) <= (o - l) else (i, stop_px, "Stop Loss")
        else:
            if o >= stop_px:
                return i, o, "Stop Loss"
            hit_t = l <= tgt_px - FILL_THROUGH
            hit_s = h >= stop_px
            if hit_t and hit_s:
                return (i, tgt_px, "Profit Target") if (o - l) <= (h - o) else (i, stop_px, "Stop Loss")
        if hit_s:
            return i, stop_px, "Stop Loss"
        if hit_t:
            return i, tgt_px, "Profit Target"
    return None


def daily_features(bars, anchor=830, close_time=1515):
    """One row per day of features that are known before the session opens."""
    rth = bars[bars["time"] > anchor]
    g = rth.groupby("date")
    d = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(),
                      "low": g["low"].min(), "close": g["close"].last()})
    d["range_pct"] = (d["high"] - d["low"]) / d["close"] * 100
    f = pd.DataFrame(index=d.index)
    f["prev_close"] = d["close"].shift(1)
    f["prev_range_pct"] = d["range_pct"].shift(1)
    f["avg10_range_pct"] = d["range_pct"].rolling(10).mean().shift(1)
    f["gap_pct"] = (d["open"] / d["close"].shift(1) - 1) * 100
    f["prev_ret_pct"] = (d["close"] / d["close"].shift(1) - 1).shift(1) * 100
    f["trend20_pct"] = (d["close"].shift(1) / d["close"].rolling(20).mean().shift(1) - 1) * 100
    f["rth_open"] = d["open"]
    return f


def run(bars, **kw):
    p = {**DEFAULTS, **kw}
    feats = daily_features(bars, p["anchor"])
    m1 = {c: bars[c].to_numpy() for c in ("open", "high", "low", "close")}
    trades = []
    mom_bars = max(1, round(p["momentum_mins"] / 5))
    anchor_m = to_mins(p["anchor"])
    rth_closes = []                                    # 5-minute closes after the anchor, all days
    for date, day in bars.groupby("date", sort=True):
        ts = pd.Timestamp(str(date))
        five = _five_minute(day)
        early = p["use_holiday_times"] and is_early_close(ts)
        last_entry = p["early_last_entry"] if early else p["last_entry"]
        flatten = p["early_flatten"] if early else p["flatten"]

        cum_pv = cum_v = 0.0
        vwap_now = vwap_prev = 0.0
        vcount = 0
        bkt = None
        pos = 0; entry = stop_px = tgt_px = 0.0; entry_t = None
        pending = None                                 # (side, stop_pts, tgt_pts)
        pending_info = None
        n_trades = n_losses = 0
        info = {"date": ts, **(feats.loc[date].to_dict() if date in feats.index else {})}
        day_hi = -np.inf; day_lo = np.inf; or_hi = -np.inf; or_lo = np.inf
        trade_info = None; worst = 0.0

        for k in range(len(five)):
            b = five.iloc[k]
            t = int(b["time"]); mins = to_mins(t)
            i0, i1 = int(b["first"]), int(b["last"])

            # fill a pending entry at this bar's open
            if pending is not None and pos == 0:
                side, sp, tp = pending
                pos, entry = side, b["open"]
                stop_px = entry - side * sp
                tgt_px = entry + side * tp
                entry_t = t
                trade_info, pending_info = pending_info, None
                worst = entry
                pending = None
            # stop / target inside this bar
            if pos != 0:
                hit = _walk_exit(m1, i0, i1, pos, entry, stop_px, tgt_px)
                j = hit[0] if hit else i1
                seg = slice(i0, j + 1)
                worst = (min(worst, m1["low"][seg].min()) if pos > 0
                         else max(worst, m1["high"][seg].max()))
                if hit:
                    _, px, kind = hit
                    if kind == "Stop Loss":
                        worst = (min(worst, px) if pos > 0 else max(worst, px))
                    pnl = (px - entry) * pos * POINT_VALUE
                    mae = abs(worst - entry) * POINT_VALUE
                    trades.append((ts, entry_t, t, pos, entry, px, kind, pnl, mae, trade_info))
                    n_losses += pnl < 0
                    pos = 0

            # VWAP (15-minute buckets from 08:30)
            mfa = mins - anchor_m
            if mfa > 0:
                if bkt is None:
                    bkt = [b["high"], b["low"], b["close"], 0.0]
                bkt[0] = max(bkt[0], b["high"]); bkt[1] = min(bkt[1], b["low"])
                bkt[2] = b["close"]; bkt[3] += b["volume"]
                if mfa % p["vwap_mins"] == 0:
                    cum_pv += (bkt[0] + bkt[1] + bkt[2]) / 3 * bkt[3]
                    cum_v += bkt[3]
                    if cum_v > 0:
                        vwap_prev, vwap_now = vwap_now, cum_pv / cum_v
                        vcount += 1
                    bkt = None

            c = b["close"]
            if mfa > 0:
                day_hi = max(day_hi, b["high"]); day_lo = min(day_lo, b["low"])
                if mfa <= 60:
                    or_hi = max(or_hi, b["high"]); or_lo = min(or_lo, b["low"])
            if p["momentum_rth_only"]:
                if mfa > 0:
                    rth_closes.append(c)
                pct = ((c / rth_closes[-1 - mom_bars] - 1) * 100
                       if mfa > 0 and len(rth_closes) > mom_bars else 0.0)
            else:
                pct = (c / five["close"].iloc[k - mom_bars] - 1) * 100 if k >= mom_bars else 0.0
            long_setup = mfa > 0 and vcount >= 2 and c > vwap_now and vwap_now > vwap_prev and pct >= p["min_change_pct"]
            short_setup = mfa > 0 and vcount >= 2 and c < vwap_now and vwap_now < vwap_prev and pct <= -p["min_change_pct"]
            prev_red = k >= 1 and five["close"].iloc[k - 1] < five["open"].iloc[k - 1]
            prev_green = k >= 1 and five["close"].iloc[k - 1] > five["open"].iloc[k - 1]
            long_trig = long_setup and c < b["open"] and not prev_red
            short_trig = short_setup and c > b["open"] and not prev_green

            trades_today = n_trades + (1 if pos else 0)
            can_enter = (p["no_trade_until"] <= t < last_entry and pos == 0
                         and trades_today < p["max_trades"] and n_losses < p["max_losses"])
            if can_enter:
                if p["use_pct_exits"]:
                    sp = c * p["stop_pct"] / 100
                    lt, st = c * p["long_target_pct"] / 100, c * p["short_target_pct"] / 100
                else:
                    sp, lt, st = p["stop_pts"], p["long_target_pts"], p["short_target_pts"]
                info.update(time=t, close=c, vwap=vwap_now, vwap_prev=vwap_prev, pct=pct,
                            day_hi=day_hi, day_lo=day_lo, or_hi=or_hi, or_lo=or_lo)
                f = p["entry_filter"]
                if long_trig and p["trade_longs"] and (f is None or f(info, 1)):
                    pending = (1, sp, lt); n_trades += 1; pending_info = dict(info)
                elif short_trig and p["trade_shorts"] and (f is None or f(info, -1)):
                    pending = (-1, sp, st); n_trades += 1; pending_info = dict(info)

            # flatten at the close of the flatten bar
            if pos != 0 and t >= flatten:
                pnl = (c - entry) * pos * POINT_VALUE
                trades.append((ts, entry_t, t, pos, entry, c, "EOD", pnl,
                               abs(worst - entry) * POINT_VALUE, trade_info))
                n_losses += pnl < 0
                pos = 0
        if pos != 0:                                   # data ended before flatten bar
            c = five["close"].iloc[-1]
            pnl = (c - entry) * pos * POINT_VALUE
            trades.append((ts, entry_t, int(five["time"].iloc[-1]), pos, entry, c, "EOD", pnl,
                           abs(worst - entry) * POINT_VALUE, trade_info))
    out = pd.DataFrame(trades, columns=["date", "entry_time", "exit_time", "side", "entry",
                                        "exit", "kind", "pnl", "mae", "info"])
    feats_cols = pd.DataFrame([i or {} for i in out["info"]]).drop(columns=["date"], errors="ignore")
    return pd.concat([out.drop(columns=["info"]), feats_cols], axis=1)
