"""Declared one-minute OHLC reconstruction of the S03 Noise Area bulletin.

Import is inert: no files, price grids, historical signals or returns are read.
The primary close-stamped cash anchor is 08:31 CT; 08:30 is a declared clock
sensitivity. Sigma uses fourteen *previous complete cash sessions*, never the
current session. Calendar exclusions are known in advance; a current day's
later missing bar cannot remove an earlier decision. VWAP uses observed minute
(H+L+C)/3 times total exported volume, resetting at the anchor. Zero cumulative
volume leaves VWAP unavailable.

Both sides share one chronological position. Checks are 09:00--14:30 CT every
30 minutes. Band/VWAP exits and reversals are next-minute-open market orders;
the normal 15:00 close schedules a 15:01 open flatten. Stops are frozen at the
entry decision, anchored to the clean fill, rounded toward entry and live on
the fill minute. grid._walk supplies the repository's OHLC stop convention.
Missing minutes are never filled synthetically; pending orders wait for the
next observed minute within the date and every delayed order is audited.
A missing flatten bar schedules the market exit at the first later observed
close; its next observed open must be at/before 15:59 CT or the position is
censored. No final observed price is silently used as a market exit.

Prices in entry/exit include slippage; raw_entry/raw_exit do not. Net already
includes $7.25/NQ round turn and the specified ticks per market/stop fill.
The slips=0 marker prevents funded_lab from charging slippage twice. Quantity
is one NQ research contract (divide its dollar geometry by ten for one MNQ).
2023+ requires explicit allow_post2022; default feature construction ends
before 2023. The caller enforces the committed preregistration gate before
running any historical replay.
"""

from collections import deque
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

try:
    from grid import _walk
    from grid24 import Grid24
    from codex_s03_calendar import calendar_status
except ImportError:
    from analysis.grid import _walk
    from analysis.grid24 import Grid24
    from analysis.codex_s03_calendar import calendar_status

POINT_VALUE = 20.0
TICK = 0.25
COMMISSION = 7.25
CHECKS = tuple(range(9 * 60, 14 * 60 + 31, 30))
FLATTEN = 15 * 60
DAY_CUTOFF = 15 * 60 + 59
TRADE_COLUMNS = [
    "day", "j0", "j1", "exit_day", "date", "entry_date", "exit_date",
    "side", "qty", "entry", "exit", "raw_entry", "raw_exit", "kind",
    "slips", "slip_fills", "slippage_usd", "pnl", "net", "mae", "why",
    "decision_index", "decision_day", "decision_j", "decision_date",
    "global_decision", "global_entry", "global_exit", "entry_phase",
    "exit_phase", "carry", "entry_order_id", "exit_order_id",
    "exit_bar_index", "exit_bar_date", "exit_bar_close", "stop",
    "stop_distance", "signal_sigma", "signal_close", "unknown_held_minutes",
    "execution_complete", "exit_decision_index", "exit_decision_j",
    "entry_minute_adverse_px", "exit_minute_adverse_px", "cross_date",
]
FEATURE_COLUMNS = [
    "bar_index", "day", "j", "time", "date", "global_close", "close",
    "session_open", "prior_close", "prior_close_date", "prior_close_kind",
    "sigma", "win_count", "history_start", "history_end", "upper", "lower",
    "vwap", "observed_minutes", "expected_minutes", "prefix_gap",
    "calendar_kind", "calendar_reason", "calendar_eligible", "decision_observed",
    "feature_ready", "timing_ok", "signal_side", "long_exit", "short_exit",
]


def _minute(hhmm):
    h, m = divmod(int(hhmm), 100)
    if not 0 <= h <= 23 or not 0 <= m <= 59:
        raise ValueError("invalid HHMM time")
    return 60 * h + m


def _period(years, allow_post2022):
    lo, hi = map(int, years)
    if lo > hi:
        raise ValueError("years must be inclusive (first_year, last_year)")
    if hi >= 2023 and not allow_post2022:
        raise ValueError("2023+ replay requires the preregistered root gate")
    return pd.Timestamp(lo, 1, 1), pd.Timestamp(hi + 1, 1, 1)


def select_period(frame, years=(2018, 2022), *, allow_post2022=False,
                  date_column="date"):
    lo, end = _period(years, allow_post2022)
    d = pd.DatetimeIndex(frame[date_column])
    return frame.loc[(d >= lo) & (d < end)].copy()


def _calendar(value, calendar):
    calendar = calendar or calendar_status
    info = calendar(pd.Timestamp(value))
    if not isinstance(info, dict) or info.get("kind") not in {
            "normal", "early", "holiday", "weekend"}:
        raise ValueError("calendar must return kind normal/early/holiday/weekend")
    return dict(info, reason=info.get("reason", info["kind"]))


def prepare_features(g, *, lookback=14, anchor=831, end="2023-01-01",
                     allow_post2022=False, calendar=None):
    """Build forward-only scheduled decision rows without computing returns.

    ``end`` is exclusive. Prior-close state is the immediately preceding cash
    session, including excluded early sessions: normal days require their
    exact 15:00 close; early days require their calendar 12:00 close. A missing
    expected cash endpoint makes PC
    unavailable on the next cash session instead of silently reaching back.
    Every OHLCV minute anchor..15:00 is required for a prior full-history day.
    """
    if lookback < 1 or anchor not in (830, 831):
        raise ValueError("lookback must be positive and anchor must be 830 or 831")
    if end is None:
        if not allow_post2022:
            raise ValueError("unbounded features require allow_post2022")
        end = pd.Timestamp.max
    end = pd.Timestamp(end)
    if end > pd.Timestamp("2023-01-01") and not allow_post2022:
        raise ValueError("2023+ features require the preregistered root gate")
    a = _minute(anchor)
    history = deque(maxlen=int(lookback))
    rows, sessions = [], []
    previous = dict(close=np.nan, date=pd.NaT, kind="unavailable")
    for d, value in enumerate(g.ts):
        dt = pd.Timestamp(value).normalize()
        if dt >= end:
            break
        cal = _calendar(dt, calendar)
        if cal["kind"] == "weekend":
            continue
        # Only the selected historical prefix is touched; no future-day array
        # participates in either history inclusion or today's eligibility.
        oo, hh, ll, cc, vv = (np.asarray(getattr(g, k)[d]) for k in "ohlcv")
        op = float(oo[a])
        valid = np.isfinite(oo[a:FLATTEN + 1]) & np.isfinite(hh[a:FLATTEN + 1])
        valid &= np.isfinite(ll[a:FLATTEN + 1]) & np.isfinite(cc[a:FLATTEN + 1])
        vol_ok = np.isfinite(vv[a:FLATTEN + 1]) & (vv[a:FLATTEN + 1] >= 0)
        valid &= vol_ok
        use = valid & (vv[a:FLATTEN + 1] > 0)
        typical = (hh[a:FLATTEN + 1] + ll[a:FLATTEN + 1] + cc[a:FLATTEN + 1]) / 3
        cpv = np.cumsum(np.where(use, typical * vv[a:FLATTEN + 1], 0.0))
        cv = np.cumsum(np.where(use, vv[a:FLATTEN + 1], 0.0))
        observed = np.cumsum(valid)
        vwap = np.divide(cpv, cv, out=np.full_like(cpv, np.nan), where=cv > 0)
        sigma = np.mean([x[1] for x in history], axis=0) if len(history) == lookback else None
        for j in CHECKS + (FLATTEN,):
            k = j - a
            price = float(cc[j])
            raw_sigma = float(sigma[k]) if sigma is not None else np.nan
            upper = max(op, previous["close"]) * (1 + raw_sigma) if np.isfinite(op) and np.isfinite(previous["close"]) else np.nan
            lower = min(op, previous["close"]) * (1 - raw_sigma) if np.isfinite(op) and np.isfinite(previous["close"]) else np.nan
            w = float(vwap[k])
            native = bool(valid[k])
            ready = (cal["kind"] == "normal" and native and op > 0 and
                     np.isfinite(previous["close"]) and np.isfinite(raw_sigma) and
                     np.isfinite(w))
            side = int(1 if price > upper and price > w else
                       (-1 if price < lower and price < w else 0)) if ready and j in CHECKS else 0
            rows.append(dict(
                bar_index=len(rows), day=d, j=j, time=(j // 60) * 100 + j % 60,
                date=dt, global_close=d * 1440 + j, close=price,
                session_open=op, prior_close=previous["close"],
                prior_close_date=previous["date"], prior_close_kind=previous["kind"],
                sigma=raw_sigma, win_count=len(history),
                history_start=history[0][0] if history else pd.NaT,
                history_end=history[-1][0] if history else pd.NaT,
                upper=upper, lower=lower, vwap=w, observed_minutes=int(observed[k]),
                expected_minutes=k + 1, prefix_gap=bool(observed[k] < k + 1),
                calendar_kind=cal["kind"], calendar_reason=cal["reason"],
                calendar_eligible=cal["kind"] == "normal", decision_observed=native,
                feature_ready=ready, timing_ok=j in CHECKS, signal_side=side,
                long_exit=bool(ready and price < max(upper, w)),
                short_exit=bool(ready and price > min(lower, w)),
            ))
        full = bool(cal["kind"] == "normal" and op > 0 and valid.all())
        sessions.append(dict(day=d, date=dt, calendar_kind=cal["kind"],
                             calendar_reason=cal["reason"], full_history_eligible=full,
                             observed_minutes=int(valid.sum()), expected_minutes=len(valid)))
        # End-of-day facts enter state only after all of today's decision rows.
        if full:
            history.append((dt, np.abs(cc[a:FLATTEN + 1] / op - 1)))
        if cal["kind"] in ("normal", "early"):
            end_j = int(cal.get("cash_close_j", FLATTEN))
            pc = float(cc[end_j])
            previous = dict(close=pc, date=dt, kind=cal["kind"])
    out = pd.DataFrame(rows, columns=FEATURE_COLUMNS)
    out.attrs.update(lookback=int(lookback), anchor=anchor, end=end,
                     sessions=pd.DataFrame(sessions),
                     volume_proxy="observed 1m typical price times total exported volume",
                     prior_close_policy="immediately preceding cash session; exact normal/early calendar endpoint",
                     current_gap_policy="observed-only VWAP; causal prefix audit; no future completeness filter")
    return out


@dataclass
class _Position:
    raw_entry: float
    entry_minute: int
    side: int
    stop: float
    distance: float
    decision: dict
    entry_order: dict
    stop_order: object
    worst: float
    unknown: list = field(default_factory=list)


def run(g, years=(2018, 2022), *, stop_sigma=0.4, anchor=831, slip_ticks=1.0,
        allow_post2022=False, commission=COMMISSION, lookback=14, features=None,
        calendar=None, signal_override=None, record_orders=True):
    """Replay one frozen profile and return (trades, scheduled features).

    ``signal_override`` is an optional vector/callable on feature rows with
    values -1/0/+1 for declared matched-exit nulls. It replaces check signals,
    retaining the original band/VWAP exits, timing and feature-readiness gates.
    A stop at a pending reversal's opening bar closes the old position first;
    its redundant market-exit leg is cancelled and the opposite entry remains.
    Missing-minute uncertainty is retained on trades and in audit attrs; a
    caller must block account conclusions for an incomplete path.
    """
    lo, end = _period(years, allow_post2022)
    if stop_sigma < 0 or slip_ticks < 0 or commission < 0:
        raise ValueError("stop multiplier and execution costs cannot be negative")
    if anchor not in (830, 831):
        raise ValueError("anchor must be 830 or 831")
    if features is None:
        f = prepare_features(g, lookback=lookback, anchor=anchor, end=end,
                             allow_post2022=allow_post2022, calendar=calendar)
    else:
        if features.attrs.get("anchor", anchor) != anchor or features.attrs.get("lookback", lookback) != lookback:
            raise ValueError("feature anchor/lookback does not match replay")
        f = features.loc[pd.DatetimeIndex(features.date) < end].copy()
    f = f.reset_index(drop=True)
    f["in_period"] = (pd.DatetimeIndex(f.date) >= lo) & (pd.DatetimeIndex(f.date) < end)
    f["entry_eligible"] = f.in_period & f.feature_ready & f.timing_ok
    if signal_override is not None:
        override = np.asarray(signal_override(f) if callable(signal_override) else signal_override)
        if override.shape != (len(f),) or not np.isin(override, [-1, 0, 1]).all():
            raise ValueError("signal_override needs one -1/0/+1 value per feature row")
        f["source_signal_side"] = f.signal_side
        f["signal_side"] = np.where(f.entry_eligible, override, 0).astype(int)
    orders, trades, censored, gaps, delays, unmatched = [], [], [], [], [], []
    order_count = 0
    position = None
    pending_exit = pending_entry = None
    day_audit = []

    def order(row, name, action, **extra):
        nonlocal order_count
        order_count += 1
        item = dict(order_id=order_count, name=name, action=action,
                    decision_index=int(row["bar_index"]), decision_day=int(row["day"]),
                    decision_j=int(row["j"]), decision_date=row["date"],
                    global_decision=int(row["global_close"]), status="pending",
                    order_type="market", activation_minute=int(row["global_close"]) + 1,
                    fill_minute=np.nan, raw_fill=np.nan, raw_trigger=np.nan,
                    fill_bar_index=np.nan, native_fill_close=np.nan, delay_minutes=0)
        item.update(extra)
        if record_orders:
            orders.append(item)
        return item

    def finish(minute, raw, kind, why, phase, item):
        nonlocal position
        p = position
        day, j = divmod(int(minute), 1440)
        entry_day, j0 = divmod(p.entry_minute, 1440)
        entry_px = p.raw_entry + p.side * TICK * slip_ticks
        exit_px = float(raw) - p.side * TICK * slip_ticks
        dec = p.decision
        entry_adverse = float(g.l[entry_day, j0] if p.side > 0 else g.h[entry_day, j0])
        if minute == p.entry_minute and kind == 0:
            entry_adverse = float(raw)
        exit_adverse = float(raw) if phase == "open" or kind == 0 else float(
            g.l[day, j] if p.side > 0 else g.h[day, j])
        trades.append(dict(
            day=entry_day, j0=j0, j1=j, exit_day=day,
            date=pd.Timestamp(g.ts[entry_day]), entry_date=pd.Timestamp(g.ts[entry_day]),
            exit_date=pd.Timestamp(g.ts[day]), side=p.side, qty=1.0,
            entry=entry_px, exit=exit_px, raw_entry=p.raw_entry, raw_exit=float(raw),
            kind=int(kind), slips=0, slip_fills=2,
            slippage_usd=2 * TICK * slip_ticks * POINT_VALUE,
            pnl=(float(raw) - p.raw_entry) * p.side * POINT_VALUE,
            net=(exit_px - entry_px) * p.side * POINT_VALUE - commission,
            mae=abs(p.worst - p.raw_entry) * POINT_VALUE, why=why,
            decision_index=int(dec["bar_index"]), decision_day=int(dec["day"]),
            decision_j=int(dec["j"]), decision_date=dec["date"],
            global_decision=int(dec["global_close"]), global_entry=p.entry_minute,
            global_exit=int(minute), entry_phase="open", exit_phase=phase,
            carry=day != entry_day, entry_order_id=p.entry_order["order_id"],
            exit_order_id=item["order_id"], exit_bar_index=int(minute),
            exit_bar_date=pd.Timestamp(g.ts[day]), exit_bar_close=int(minute),
            stop=p.stop, stop_distance=p.distance, signal_sigma=dec["sigma"],
            signal_close=dec["close"], unknown_held_minutes=len(p.unknown),
            execution_complete=not p.unknown, exit_decision_index=item["decision_index"],
            exit_decision_j=item["decision_j"],
            entry_minute_adverse_px=entry_adverse,
            exit_minute_adverse_px=exit_adverse, cross_date=day != entry_day,
        ))
        item.update(status="filled", fill_minute=int(minute), raw_fill=float(raw),
                    fill_bar_index=int(minute), native_fill_close=int(minute))
        if p.stop_order is not None and p.stop_order is not item:
            p.stop_order["status"] = "cancelled_position_closed"
        position = None

    for day, day_features in f.loc[f.in_period].groupby("day", sort=True):
        day = int(day)
        lookup = {int(r["j"]): r for r in day_features.to_dict("records")}
        # Calendar exclusions are predetermined; today's future coverage is
        # deliberately absent from this eligibility decision.
        audit = dict(day=day, date=pd.Timestamp(g.ts[day]),
                     calendar_kind=str(day_features.calendar_kind.iloc[0]),
                     account_eligible=True, unknown_held_minutes=0,
                     delayed_orders=0, censored_positions=0,
                     unmatched_orders=0,
                     flatten_catchup=False,
                     observed_cash_minutes=int(day_features.observed_minutes.iloc[-1]),
                     expected_cash_minutes=int(day_features.expected_minutes.iloc[-1]))
        audit["missing_cash_minutes"] = audit["expected_cash_minutes"] - audit["observed_cash_minutes"]
        audit["no_cash_data"] = audit["observed_cash_minutes"] == 0
        day_audit.append(audit)
        if not bool(day_features.calendar_eligible.any()):
            continue
        gap_start, delay_start, censor_start = len(gaps), len(delays), len(censored)
        unmatched_start = len(unmatched)
        flatten_seen = False
        oo, hh, ll, cc = (np.asarray(getattr(g, k)[day]) for k in "ohlc")
        native_minutes = np.isfinite(oo) & np.isfinite(hh) & np.isfinite(ll) & np.isfinite(cc)
        for j in range(_minute(anchor), DAY_CUTOFF + 1):
            minute = day * 1440 + j
            row = lookup.get(j)
            if not native_minutes[j]:
                if position is not None:
                    position.unknown.append(minute)
                    gaps.append(dict(day=day, date=pd.Timestamp(g.ts[day]), j=j,
                                     global_minute=minute, side=position.side,
                                     entry_order_id=position.entry_order["order_id"],
                                     reason="missing_native_OHLC_while_held"))
                continue
            if position is None and pending_entry is None and pending_exit is None and row is None:
                continue
            # Existing protective stop sees an adverse opening gap before
            # pending market exits. Both fill at the same raw opening price.
            if position is not None and position.stop_order is not None:
                gap = ((position.side > 0 and oo[j] <= position.stop) or
                       (position.side < 0 and oo[j] >= position.stop))
                if gap and minute > position.entry_minute:
                    position.worst = min(position.worst, oo[j]) if position.side > 0 else max(position.worst, oo[j])
                    finish(minute, oo[j], 0, "S03.Stop", "open", position.stop_order)
            if pending_exit is not None:
                if position is not None:
                    position.worst = min(position.worst, oo[j]) if position.side > 0 else max(position.worst, oo[j])
                    pending_exit["delay_minutes"] = minute - pending_exit["activation_minute"]
                    if pending_exit["delay_minutes"]:
                        delays.append(dict(order_id=pending_exit["order_id"], delay_minutes=pending_exit["delay_minutes"], fill_minute=minute))
                    finish(minute, oo[j], 2, pending_exit["name"], "open", pending_exit)
                else:
                    pending_exit["status"] = "cancelled_flat_after_stop"
                pending_exit = None
            if pending_entry is not None:
                decision, item, side = pending_entry
                if position is not None:
                    raise AssertionError("S03 cannot pyramid")
                raw = float(oo[j])
                distance = float(stop_sigma * decision["sigma"] * decision["close"])
                raw_stop = raw - side * distance
                stop = (np.ceil(raw_stop / TICK) if side > 0 else np.floor(raw_stop / TICK)) * TICK if stop_sigma > 0 else (np.nan)
                st = order(decision, "S03.Stop", "sell" if side > 0 else "buy_to_cover",
                           order_type="stop", activation_minute=minute,
                           raw_trigger=stop, status="working") if stop_sigma > 0 else None
                position = _Position(raw, minute, side, float(stop), distance,
                                     decision, item, st, raw)
                delay = minute - item["activation_minute"]
                item.update(status="filled", fill_minute=minute, raw_fill=raw,
                            fill_bar_index=minute, native_fill_close=minute, delay_minutes=delay)
                if delay:
                    delays.append(dict(order_id=item["order_id"], delay_minutes=delay, fill_minute=minute))
                pending_entry = None
            if position is not None:
                # Calling _walk on a single observed minute preserves entry-
                # minute stop activation. Its synthetic time result is ignored.
                if position.stop_order is None:
                    worst = ll[j] if position.side > 0 else hh[j]
                    kind = 2
                else:
                    target = np.inf if position.side > 0 else -np.inf
                    _, px, kind, worst = _walk(oo, hh, ll, cc, j, j,
                                               position.side, position.stop, target, 1.0)
                position.worst = min(position.worst, worst) if position.side > 0 else max(position.worst, worst)
                if kind == 0:
                    finish(minute, px, 0, "S03.Stop", "intrabar", position.stop_order)
            if j >= FLATTEN and not flatten_seen:
                flatten_seen = True
                if position is not None:
                    if row is None:
                        # This is a real later one-minute CLOSE, not an
                        # inferred close of the absent 15:00 bar.
                        row = dict(lookup[FLATTEN], j=j,
                                   time=(j // 60) * 100 + j % 60,
                                   close=float(cc[j]), global_close=minute)
                    audit["flatten_catchup"] = j != FLATTEN
                    pending_exit = order(row, "S03.TimeX" if j == FLATTEN else "S03.CatchupTimeX",
                                         "sell" if position.side > 0 else "buy_to_cover")
                continue
            if row is None:
                continue
            if j == FLATTEN:
                continue
            if not bool(row["entry_eligible"]):
                continue
            desired = int(row["signal_side"])
            side = position.side if position is not None else 0
            close_existing = side != 0 and (desired == -side or
                (side > 0 and row["long_exit"]) or (side < 0 and row["short_exit"]))
            if close_existing:
                pending_exit = order(row, "S03.ReverseX" if desired == -side else "S03.BandVwapX",
                                     "sell" if side > 0 else "buy_to_cover")
            if desired and desired != side and (side == 0 or close_existing):
                pending_entry = (row, order(row, "S03.Long" if desired > 0 else "S03.Short",
                                            "buy" if desired > 0 else "sell_short"), desired)
        if position is not None:
            if pending_exit is not None and pending_exit["name"] == "S03.CatchupTimeX":
                reason = "unfilled_catchup_flatten_endpoint"
            elif not bool(lookup.get(FLATTEN, {}).get("decision_observed", False)):
                reason = "missing_flatten_decision_no_later_native_close"
            else:
                reason = "unfilled_flatten_endpoint"
            censored.append(dict(day=day, date=pd.Timestamp(g.ts[day]),
                                 raw_entry=position.raw_entry, global_entry=position.entry_minute,
                                 side=position.side, stop=position.stop, reason=reason,
                                 decision_index=int(position.decision["bar_index"]),
                                 unknown_held_minutes=len(position.unknown)))
            if position.stop_order is not None:
                position.stop_order["status"] = "working_censored"
            position = None
        if pending_exit is not None:
            pending_exit["status"] = "unfilled_endpoint"
            unmatched.append(dict(pending_exit))
            pending_exit = None
        if pending_entry is not None:
            pending_entry[1]["status"] = "unfilled_endpoint"
            unmatched.append(dict(pending_entry[1]))
            pending_entry = None
        audit.update(unknown_held_minutes=len(gaps) - gap_start,
                     delayed_orders=len(delays) - delay_start,
                     censored_positions=len(censored) - censor_start,
                     unmatched_orders=len(unmatched) - unmatched_start,
                     account_eligible=not (len(gaps) - gap_start or
                         len(delays) - delay_start or len(censored) - censor_start or
                         len(unmatched) - unmatched_start))
    t = pd.DataFrame(trades, columns=TRADE_COLUMNS)
    t.attrs.update(orders=pd.DataFrame(orders), censored=censored,
                   unknown_held_minutes=pd.DataFrame(gaps), delayed_orders=pd.DataFrame(delays),
                   unmatched_orders=pd.DataFrame(unmatched),
                   execution_complete=not censored and not gaps and not delays and not unmatched,
                   day_audit=pd.DataFrame(day_audit),
                   net_includes_slippage=True, slip_ticks=slip_ticks, commission=commission,
                   stop_sigma=stop_sigma, anchor=anchor, years=tuple(years), lookback=lookback,
                   stop_anchor="raw fill", stop_rounding="toward entry", quantity_geometry="1 NQ; /10 for 1 MNQ",
                   flatten_decision=1500, first_check=900, last_check=1430,
                   missing_flatten_policy="first later observed close sends next-open exit by15:59; otherwise censor",
                   pending_market_policy="next observed native minute within date; audit delay",
                   priority="old-position gap stop, pending market exit, pending entry, intrabar stop, close decision")
    return t, f


def _fixture_grid(first="2020-01-02", last=None):
    """Empty in-memory Grid24 for synthetic checks; no data files are opened."""
    cal = pd.date_range(first, last or first, freq="D")
    g = Grid24.__new__(Grid24)
    g.ts = cal.to_numpy()
    g.dates = cal.strftime("%Y%m%d").astype(int).to_numpy()
    g.D = len(cal)
    for key in "ohlcv":
        setattr(g, key, np.full((g.D, 1440), np.nan))
    g.trading = np.flatnonzero(cal.dayofweek < 5)
    return g


def _fixture_session(g, day, price=100.0, stop=901):
    for key in "ohlc":
        getattr(g, key)[day, _minute(831):stop + 1] = price
    g.v[day, _minute(831):stop + 1] = 1.0


def _fixture_features(g, signals, sigma=0.01):
    """Explicit decision state for focused execution fixtures."""
    rows = []
    for d in g.trading:
        for j in CHECKS + (FLATTEN,):
            rows.append(dict(bar_index=len(rows), day=int(d), j=j,
                time=(j // 60) * 100 + j % 60, date=pd.Timestamp(g.ts[d]),
                global_close=int(d) * 1440 + j, close=float(g.c[d, j]),
                session_open=100., prior_close=100., sigma=sigma, win_count=14,
                upper=100.5, lower=99.5, vwap=100., feature_ready=True,
                calendar_kind="normal", calendar_eligible=True,
                decision_observed=bool(np.isfinite(g.c[d, j])),
                timing_ok=j in CHECKS, signal_side=signals.get(j, 0),
                long_exit=False, short_exit=False,
                observed_minutes=j - _minute(831) + 1,
                expected_minutes=j - _minute(831) + 1))
    out = pd.DataFrame(rows)
    out.attrs.update(anchor=831, lookback=14)
    return out


def synthetic_checks():
    """Focused source/execution fixtures, with no historical data or selection."""
    passed = []
    g = _fixture_grid("2020-01-02", "2020-02-28")
    full_days = [d for d in range(g.D) if _calendar(g.ts[d], None)["kind"] == "normal"][:18]
    for i, d in enumerate(full_days):
        _fixture_session(g, d)
        g.c[d, _minute(900)] = 100. + i
        g.h[d, _minute(900)] = 100. + i
    omitted = full_days[3]
    g.c[omitted, _minute(1200)] = np.nan
    today = full_days[-1]
    g.c[today, _minute(900)] = 999.
    past = [i for i, d in enumerate(full_days[:-1]) if d != omitted][-14:]
    r = prepare_features(g).query("day == @today and j == 540").iloc[0]
    assert r.win_count == 14 and np.isclose(r.sigma, np.mean(past) / 100.)
    assert r.history_end == pd.Timestamp(g.ts[full_days[-2]])
    passed.append("exact_previous14_full_cash_sessions_excludes_gaps_holidays_and_today")

    # A complete prior session supplies sigma; current-day information can
    # change future history inclusion but cannot change an earlier row.
    g = _fixture_grid("2020-01-02", "2020-01-03")
    _fixture_session(g, 0)
    g.c[0, _minute(900)] = 102.
    _fixture_session(g, 1)
    g.c[1, _minute(900)] = 104.
    f1 = prepare_features(g, lookback=1)
    r = f1[(f1.day == 1) & (f1.j == _minute(900))].iloc[0]
    assert np.isclose(r.sigma, .02) and r.history_end == pd.Timestamp("2020-01-02")
    assert r.signal_side == 1
    g.c[1, _minute(1400)] = np.nan
    f2 = prepare_features(g, lookback=1)
    pd.testing.assert_series_equal(r, f2[(f2.day == 1) & (f2.j == _minute(900))].iloc[0])
    passed.append("prior_complete_session_only_and_current_future_gap_causality")

    # Do not replace a missing normal endpoint with the last observed price.
    g.c[0, FLATTEN] = np.nan
    f = prepare_features(g, lookback=1)
    r = f[(f.day == 1) & (f.j == _minute(900))].iloc[0]
    assert np.isnan(r.prior_close) and r.win_count == 0 and not r.feature_ready
    passed.append("missing_normal_prior_endpoint_is_unavailable_and_not_full_history")

    # An excluded legitimate early session remains the immediate cash PC.
    g = _fixture_grid("2019-11-27", "2019-12-02")
    _fixture_session(g, 0)
    _fixture_session(g, 2, price=107., stop=12 * 60)
    _fixture_session(g, 5)
    f = prepare_features(g, lookback=1)
    r = f[(f.day == 5) & (f.j == _minute(900))].iloc[0]
    assert r.prior_close == 107 and r.prior_close_kind == "early"
    assert r.history_end == pd.Timestamp("2019-11-27")
    passed.append("holiday_excluded_early_cash_close_included_in_prior_close")
    g.c[2, 12 * 60] = np.nan
    r = prepare_features(g, lookback=1).query("day == 5 and j == 540").iloc[0]
    assert np.isnan(r.prior_close) and not r.feature_ready
    passed.append("missing_early_calendar_endpoint_is_unavailable")

    # Band clearance without VWAP confirmation does not enter. An anchor
    # change is visible and volume zero is unavailable, rather than price VWAP.
    g = _fixture_grid("2020-01-02", "2020-01-03")
    _fixture_session(g, 0)
    _fixture_session(g, 1, price=103.)
    g.o[1, _minute(831)] = 100.
    g.c[1, _minute(900)] = 101.
    g.l[1, _minute(900)] = 101.
    f = prepare_features(g, lookback=1)
    r = f[(f.day == 1) & (f.j == _minute(900))].iloc[0]
    assert r.close > r.upper and r.close < r.vwap and r.signal_side == 0
    g.v[1] = 0.
    r = prepare_features(g, lookback=1).query("day == 1 and j == 540").iloc[0]
    assert np.isnan(r.vwap) and not r.feature_ready
    passed.append("strict_band_and_vwap_confirmation_zero_volume_unavailable")

    g = _fixture_grid("2020-01-02", "2020-01-03")
    _fixture_session(g, 0)
    _fixture_session(g, 1, price=98.)
    g.o[1, _minute(831)] = 100.
    g.c[1, _minute(900)] = 99.
    g.h[1, _minute(900)] = 99.
    r = prepare_features(g, lookback=1).query("day == 1 and j == 540").iloc[0]
    assert r.close < r.lower and r.close > r.vwap and r.signal_side == 0
    _fixture_session(g, 1)
    r = prepare_features(g, lookback=1).query("day == 1 and j == 540").iloc[0]
    assert r.close == r.upper == r.lower == r.vwap
    assert not r.signal_side and not r.long_exit and not r.short_exit
    passed.append("short_vwap_confirmation_and_strict_equality_no_action")

    # Entry-minute stops, tick rounding toward entry and symmetric costs.
    for side in (1, -1):
        g = _fixture_grid()
        _fixture_session(g, 0)
        if side > 0:
            g.l[0, _minute(901)] = 99.5
        else:
            g.h[0, _minute(901)] = 100.5
        f = _fixture_features(g, {_minute(900): side})
        t, _ = run(g, years=(2020, 2020), features=f)
        assert len(t) == 1 and t.iloc[0].j0 == t.iloc[0].j1 == _minute(901)
        r = t.iloc[0]
        assert r.exit_phase == "intrabar" and r.kind == 0
        assert r.raw_exit == 100. - side * .25 and r.net == -22.25
        assert r.slips == 0 and r.stop_distance == .4
        assert r.entry_minute_adverse_px == r.raw_exit
    passed.append("both_sides_entry_minute_stop_rounding_and_no_double_cost")

    g = _fixture_grid()
    _fixture_session(g, 0)
    f = _fixture_features(g, {_minute(900): 1, _minute(930): 1, _minute(1000): 1})
    t, _ = run(g, years=(2020, 2020), stop_sigma=0, features=f)
    assert len(t) == 1 and t.iloc[0].j1 == _minute(1501)
    assert t.iloc[0].why == "S03.TimeX" and t.iloc[0].exit_phase == "open"
    assert t.iloc[0].net == -17.25 and t.attrs["execution_complete"]
    passed.append("same_direction_no_pyramid_and_1500_decision_1501_open")

    for side in (1, -1):
        g = _fixture_grid()
        _fixture_session(g, 0)
        for key in "ohlc":
            getattr(g, key)[0, _minute(931):] = 100. + side
        f = _fixture_features(g, {_minute(900): side})
        f.loc[f.j == _minute(930), "long_exit" if side > 0 else "short_exit"] = True
        t, _ = run(g, years=(2020, 2020), stop_sigma=0, features=f)
        assert len(t) == 1 and t.iloc[0].why == "S03.BandVwapX"
        assert t.iloc[0].j1 == _minute(931) and t.iloc[0].net == 2.75
    passed.append("both_sides_check_exit_waits_next_open")

    g = _fixture_grid()
    _fixture_session(g, 0)
    for key in "ohlc":
        getattr(g, key)[0, _minute(931):] = 98.
    f = _fixture_features(g, {_minute(900): 1, _minute(930): -1})
    t, _ = run(g, years=(2020, 2020), stop_sigma=0, features=f)
    assert list(t.side) == [1, -1] and t.iloc[0].j1 == t.iloc[1].j0 == _minute(931)
    assert np.isclose(t.net.sum(), -40. - 2 * 17.25)
    passed.append("opposite_check_reversal_separate_round_turn_costs")

    # A gap through the old stop and a pending reversal exit share the raw
    # open. Only the stop closes the old position; exactly one short opens.
    g = _fixture_grid()
    _fixture_session(g, 0)
    for key in "ohlc":
        getattr(g, key)[0, _minute(931):] = 99.
    f = _fixture_features(g, {_minute(900): 1, _minute(930): -1})
    t, _ = run(g, years=(2020, 2020), features=f)
    assert list(t.side) == [1, -1] and t.iloc[0].raw_exit == 99.
    assert t.iloc[0].kind == 0 and t.iloc[0].exit_phase == "open"
    orders = t.attrs["orders"]
    assert len(orders[orders.status == "cancelled_flat_after_stop"]) == 1
    passed.append("gap_stop_pending_reversal_priority_single_position")

    # Missing entry open waits a real next minute, with delay disclosed.
    g = _fixture_grid()
    _fixture_session(g, 0)
    for key in "ohlc":
        getattr(g, key)[0, _minute(901)] = np.nan
    f = _fixture_features(g, {_minute(900): 1})
    t, _ = run(g, years=(2020, 2020), stop_sigma=0, features=f)
    assert t.iloc[0].j0 == _minute(902) and len(t.attrs["delayed_orders"]) == 1
    assert not t.attrs["execution_complete"]
    passed.append("missing_fill_minute_waits_observed_open_and_blocks_complete_path")

    # A missing flatten decision uses a real later close and then next open.
    g = _fixture_grid()
    _fixture_session(g, 0, stop=_minute(1503))
    for key in "ohlc":
        getattr(g, key)[0, _minute(1500)] = np.nan
    f = _fixture_features(g, {_minute(900): 1})
    t, _ = run(g, years=(2020, 2020), stop_sigma=0, features=f)
    assert len(t) == 1 and t.iloc[0].j1 == _minute(1502)
    assert t.iloc[0].why == "S03.CatchupTimeX" and t.iloc[0].exit_decision_j == _minute(1501)
    assert t.iloc[0].unknown_held_minutes == 1
    passed.append("missing_flatten_catchup_real_close_then_real_open_unknown_path")

    g = _fixture_grid()
    _fixture_session(g, 0, stop=_minute(1459))
    f = _fixture_features(g, {_minute(900): 1})
    t, _ = run(g, years=(2020, 2020), stop_sigma=0, features=f)
    assert t.empty and len(t.attrs["censored"]) == 1
    assert not t.attrs["execution_complete"]
    passed.append("missing_end_no_fabricated_last_close_trade")

    g = _fixture_grid()
    _fixture_session(g, 0, stop=_minute(1430))
    f = _fixture_features(g, {_minute(1430): 1})
    t, _ = run(g, years=(2020, 2020), stop_sigma=0, features=f)
    assert t.empty and len(t.attrs["unmatched_orders"]) == 1
    assert not t.attrs["execution_complete"]
    assert not t.attrs["day_audit"].iloc[0].account_eligible
    passed.append("unfilled_entry_endpoint_is_unmatched_and_blocks_account_path")
    try:
        run(g, years=(2023, 2023))
    except ValueError:
        pass
    else:
        raise AssertionError("recent-period gate failed")
    passed.append("2023_gate_before_feature_or_return_computation")
    return passed
