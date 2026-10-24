"""Literal DriftBreak v2 replay, with the declared research data proxy.

This module never loads price data or runs a historical test on import. ``run``
defaults to 2018--2022 and refuses later periods without ``allow_post2022``.
Features use midnight-aligned, close-stamped 30-minute Grid24 bars, total
exported volume as an explicit proxy for PowerLanguage's chart Volume, and
IOG off. Every Date containing a positive range counts, including Sunday.

Execution uses grid._walk's one-minute path, gap-stop and limit conventions.
Brackets are armed on the entry minute. Next-bar market orders wait for the
next valid chart bar, including across a holiday halt. SetExitOnClose is
applied only at the declared chart-session endpoint (default 24:00, following
MULTICHARTS_PITFALLS.md); missing session-end bars are never inferred from the
last RTH observation. A partial native endpoint bar uses its last observed
minute's close; native and actual fill timestamps are recorded separately.
A surviving position also receives the source's Carry
order at the first new-Date bar CLOSE, for the following bar's open.

The returned ledger has raw and slipped prices. Its ``net`` already includes
$7.25/NQ and one tick on each market/stop fill; ``slips=0`` prevents funded_lab's
price helper from charging slippage twice. Use ``net`` directly, never apply
param_clusters.trade_net to this already adjusted ledger. ``pnl`` is gross
raw-price dollars.
Unclosed positions at the selected period/data endpoint are censored, never
marked to the last observed close. Orders and censored positions are in attrs.
"""

from collections import deque
from dataclasses import dataclass
import warnings

import numpy as np
import pandas as pd

try:
    from grid import _walk
    from grid24 import Grid24
except ImportError:
    from analysis.grid import _walk
    from analysis.grid24 import Grid24


POINT_VALUE = 20.0
TICK = 0.25
COMMISSION = 7.25
TRADE_COLUMNS = [
    "day", "j0", "j1", "exit_day", "date", "entry_date", "exit_date",
    "side", "qty", "entry", "exit", "raw_entry", "raw_exit", "kind",
    "slips", "slip_fills", "slippage_usd", "pnl", "net", "mae", "why",
    "decision_index", "decision_day", "decision_j", "decision_date",
    "global_decision", "global_entry", "global_exit", "entry_phase",
    "exit_phase", "carry", "entry_order_id", "exit_order_id",
    "exit_bar_index", "exit_bar_date", "exit_bar_close",
]


def _minute(hhmm):
    if hhmm == 2400:
        return 0
    h, m = divmod(int(hhmm), 100)
    if h < 0 or h > 23 or m < 0 or m > 59:
        raise ValueError("invalid HHMM time")
    return h * 60 + m


def _period(years, allow_post2022):
    lo, hi = map(int, years)
    if lo > hi:
        raise ValueError("years must be (first_year, last_year), inclusive")
    if hi >= 2023 and not allow_post2022:
        raise ValueError("2023+ replay requires the preregistered root gate")
    return pd.Timestamp(lo, 1, 1), pd.Timestamp(hi + 1, 1, 1)


def select_period(frame, years=(2018, 2022), *, allow_post2022=False,
                  date_column="date"):
    """Select an already computed ledger, enforcing the same period gate."""
    lo, end = _period(years, allow_post2022)
    d = pd.DatetimeIndex(frame[date_column])
    return frame.loc[(d >= lo) & (d < end)].copy()


def prepare_features(g, *, boundary_len=15, drift_len=4, end=None):
    """Source state at each valid 30m close, with no trade/return computation.

    ``end`` is exclusive. Range history is formed from these 30m bars, rather
    than g.h/g.l calendar rows: the 00:00 bar belongs to its native new Date
    even though its first 29 minutes fall on the previous calendar date.
    Close[4] advances through valid chart bars and never resets on Date/gaps.
    """
    if not 1 <= boundary_len <= 250 or drift_len < 1:
        raise ValueError("invalid range/drift lookback")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        b = g.bars(30)
    valid = np.isfinite(b["c"])
    if end is not None:
        valid &= (pd.DatetimeIndex(g.ts) < pd.Timestamp(end))[:, None]
    days, slots = np.nonzero(valid)
    minute_open = g.o.ravel()
    minute_close = g.c.ravel()
    hist = deque(maxlen=boundary_len)
    closes = deque(maxlen=drift_len)
    previous_day = -1
    sess_high = sess_low = sess_open = np.nan
    cpv = cv = vwap = 0.0
    below = 0
    rows = []
    for bar_index, (day, slot) in enumerate(zip(days, slots)):
        j = int(slot) * 30
        stop = int(day) * 1440 + j
        start = max(0, stop - 29)
        opens = np.flatnonzero(np.isfinite(minute_open[start:stop + 1]))
        last = np.flatnonzero(np.isfinite(minute_close[start:stop + 1]))
        if not len(opens) or not len(last):
            raise ValueError("valid chart close lacks executable minute OHLC")
        first_minute = start + int(opens[0])
        last_minute = start + int(last[-1])
        o, h, l, c, v = (float(b[k][day, slot]) for k in ("o", "h", "l", "c", "v"))
        new_date = int(day) != previous_day
        if new_date:
            if previous_day >= 0 and sess_high - sess_low > 0:
                hist.append(sess_high - sess_low)
            sess_open, sess_high, sess_low = o, h, l
            cpv = cv = 0.0
            vwap_prev = 0.0
            below = 0
        else:
            sess_high, sess_low = max(sess_high, h), min(sess_low, l)
            vwap_prev = vwap
        boundary = float(np.mean(hist)) if len(hist) == boundary_len else np.nan
        if v > 0:
            cpv += ((h + l + c) / 3.0) * v
            cv += v
        vwap = cpv / cv if cv > 0 else c
        ref = closes[0] if len(closes) == drift_len else np.nan
        drift = (c - ref) / ref * 100.0 if np.isfinite(ref) and ref != 0 else 0.0
        below = below + 1 if c < vwap else 0
        rows.append(dict(
            bar_index=bar_index, day=int(day), slot=int(slot), j=j,
            date=pd.Timestamp(g.ts[day]), time=(j // 60) * 100 + j % 60,
            global_close=stop, first_minute=first_minute, last_minute=last_minute,
            open=o, high=h, low=l, close=c, volume=v, new_date=new_date,
            session_open=sess_open, session_high=sess_high, session_low=sess_low,
            boundary=boundary, win_count=len(hist), vwap=vwap, vwap_prev=vwap_prev,
            bars_below_vwap=below, drift_ref=ref, drift_pct=drift,
        ))
        closes.append(c)
        previous_day = int(day)
    out = pd.DataFrame(rows)
    out.attrs.update(boundary_len=boundary_len, drift_len=drift_len,
                     volume_proxy="total exported volume; MC Volume may be up-volume",
                     bar_minutes=30, alignment="midnight", iog=False)
    return out


@dataclass
class _Position:
    raw_entry: float
    entry_minute: int
    side: int
    stop: float
    target: float
    decision: dict
    order_id: int
    worst: float
    stop_order: dict
    target_order: dict
    eoc_order: object


def run(g, years=(2018, 2022), *, veto_mode=1, target_through=1.0,
        slip_ticks=1.0, commission=COMMISSION, session_end=2400,
        allow_post2022=False, features=None, boundary_len=15, drift_len=4,
        noise_mult=0.30, drift_threshold=0.10, first=1000, last=1400,
        flatten_time=1530, max_trades=2, vwap_exit_bars=7,
        target_points=40.0, stop_points=75.0, exit_on_bar_close=False,
        apex_safe=False,
        decision_mask=None, random_side_seed=None, random_time_seed=None,
        entry_schedule=None, record_orders=True):
    """Replay one frozen rule; return ``(trades, features)``.

    Veto modes 0 and 1 are the only supported strategy variants. Sensitivities
    ``target_through=0`` and ``slip_ticks`` change execution, not raw brackets.
    ``decision_mask`` is a bool vector/callable on feature rows. A supplied
    ``entry_schedule`` is a collection of bar_index values (or bar_index->side
    mapping) replacing the price/veto entry gates while retaining timing,
    flat-position and two-submission caps. ``random_time_seed`` chooses two
    valid decision bars per Date in the same entry window, bypassing price and
    veto gates; ``random_side_seed`` independently randomizes submitted sides.
    These controls implement nulls, not additional production strategies.
    ``apex_safe`` applies only the existing VB early-close calendar: entries
    strictly before 11:00 and a market exit at an observed chart close at or
    after 11:30. It never fabricates a missing 11:30 close or changes ordinary
    dates' 15:30 next-bar exit.
    """
    lo, end = _period(years, allow_post2022)
    if veto_mode not in (0, 1):
        raise ValueError("only preregistered veto_mode 0 or 1 is supported")
    if target_through < 0 or slip_ticks < 0 or commission < 0:
        raise ValueError("execution costs/fill-through cannot be negative")
    if target_points <= 0 or stop_points <= 0 or max_trades < 1:
        raise ValueError("invalid bracket/submission cap")
    first_min, last_min, flat_min = map(_minute, (first, last, flatten_time))
    end_min = _minute(session_end) if session_end is not None else None
    if features is None:
        f = prepare_features(g, boundary_len=boundary_len, drift_len=drift_len, end=end)
    else:
        if features.attrs.get("boundary_len", boundary_len) != boundary_len:
            raise ValueError("feature boundary lookback does not match run")
        if features.attrs.get("drift_len", drift_len) != drift_len:
            raise ValueError("feature drift lookback does not match run")
        f = features.loc[pd.DatetimeIndex(features.date) < end].copy()
    if f.empty:
        t = pd.DataFrame(columns=TRADE_COLUMNS)
        t.attrs.update(orders=pd.DataFrame(), censored=[], net_includes_slippage=True)
        return t, f
    f = f.reset_index(drop=True)
    f["noise_up"] = f.session_open + noise_mult * f.boundary
    f["in_period"] = (f.date >= lo) & (f.date < end)
    if apex_safe:
        from candidates24 import _early
        early_dates = _early(g)
        f["early_date"] = early_dates[f.day.to_numpy(int)]
    else:
        f["early_date"] = False
    f["timing_ok"] = (f.j >= first_min) & (f.j <= last_min) & (f.j < flat_min)
    if apex_safe:
        f["timing_ok"] &= ~f.early_date | (f.j < _minute(1100))
    f["price_ok"] = (f.close > f.noise_up) & (f.close > f.vwap)
    f["context_ok"] = True if veto_mode == 0 else f.drift_pct > -drift_threshold
    f["entry_eligible"] = (f.in_period & f.timing_ok & f.price_ok & f.context_ok
                             & (f.win_count >= boundary_len) & (f.boundary > 0))
    if decision_mask is None:
        mask = np.ones(len(f), dtype=bool)
    else:
        mask = np.asarray(decision_mask(f) if callable(decision_mask) else decision_mask, dtype=bool)
        if mask.shape != (len(f),):
            raise ValueError("decision_mask must have one boolean per feature row")
    if entry_schedule is not None and random_time_seed is not None:
        raise ValueError("choose entry_schedule or random_time_seed")
    schedule = None
    if entry_schedule is not None:
        schedule = dict(entry_schedule) if hasattr(entry_schedule, "items") else {int(i): 1 for i in entry_schedule}
        if any(v not in (-1, 1) for v in schedule.values()):
            raise ValueError("scheduled side must be +1 or -1")
    if random_time_seed is not None:
        rng_time = np.random.default_rng(random_time_seed)
        schedule = {}
        eligible = f[f.in_period & f.timing_ok & (f.win_count >= boundary_len) & (f.boundary > 0)]
        for _, rows in eligible.groupby("day", sort=True):
            chosen = rng_time.choice(rows.bar_index.to_numpy(), min(max_trades, len(rows)), replace=False)
            schedule.update({int(i): 1 for i in chosen})
    rng_side = np.random.default_rng(random_side_seed) if random_side_seed is not None else None
    o, h, l, c = (getattr(g, k).ravel() for k in ("o", "h", "l", "c"))
    orders, trades = [], []
    position = None
    pending_entry = None
    pending_exits = []
    attempts = 0
    previous_day = -1
    order_counter = 0

    def order(row, name, action):
        nonlocal order_counter
        order_counter += 1
        item = dict(order_id=order_counter, name=name, action=action,
                    decision_index=int(row["bar_index"]), decision_day=int(row["day"]),
                    decision_j=int(row["j"]), decision_date=row["date"],
                    global_decision=int(row["global_close"]), status="pending",
                    fill_minute=np.nan, raw_fill=np.nan,
                    order_type="market", activation_minute=np.nan,
                    raw_trigger=np.nan, fill_bar_index=np.nan,
                    native_fill_close=np.nan)
        if record_orders:
            orders.append(item)
        return item

    def finish(minute, raw_price, kind, why, phase, exit_order=None):
        nonlocal position
        if exit_order is None and kind in (0, 1):
            exit_order = position.stop_order if kind == 0 else position.target_order
        for bracket_order in (position.stop_order, position.target_order, position.eoc_order):
            if bracket_order is not None and bracket_order is not exit_order:
                bracket_order["status"] = "cancelled_oco" if kind in (0, 1) else "cancelled_position_closed"
        side = position.side
        entry_day, j0 = divmod(position.entry_minute, 1440)
        exit_day, j1 = divmod(int(minute), 1440)
        slipped_entry = position.raw_entry + side * TICK * slip_ticks
        slipped_exit = raw_price - side * TICK * slip_ticks * (kind != 1)
        gross = (raw_price - position.raw_entry) * side * POINT_VALUE
        slip_fills = 1 + int(kind != 1)
        decision = position.decision
        trades.append(dict(
            day=entry_day, j0=j0, j1=j1, exit_day=exit_day,
            date=pd.Timestamp(g.ts[entry_day]), entry_date=pd.Timestamp(g.ts[entry_day]),
            exit_date=pd.Timestamp(g.ts[exit_day]), side=side, qty=1.0,
            entry=slipped_entry, exit=slipped_exit,
            raw_entry=position.raw_entry, raw_exit=float(raw_price), kind=int(kind),
            slips=0, slip_fills=slip_fills,
            slippage_usd=slip_fills * TICK * slip_ticks * POINT_VALUE,
            pnl=gross, net=(slipped_exit - slipped_entry) * side * POINT_VALUE - commission,
            mae=abs(position.worst - position.raw_entry) * POINT_VALUE, why=why,
            decision_index=int(decision["bar_index"]), decision_day=int(decision["day"]),
            decision_j=int(decision["j"]), decision_date=decision["date"],
            global_decision=int(decision["global_close"]), global_entry=position.entry_minute,
            global_exit=int(minute), entry_phase="open", exit_phase=phase,
            carry=exit_day != entry_day, entry_order_id=position.order_id,
            exit_order_id=exit_order["order_id"] if exit_order else np.nan,
            exit_bar_index=int(row["bar_index"]), exit_bar_date=row["date"],
            exit_bar_close=int(row["global_close"]),
        ))
        if exit_order:
            exit_order.update(status="filled", fill_minute=int(minute), raw_fill=float(raw_price),
                              fill_bar_index=int(row["bar_index"]), native_fill_close=int(row["global_close"]))
        position = None

    for row_no, row in enumerate(f.to_dict("records")):
        a, z = int(row["first_minute"]), int(row["last_minute"])
        if pending_entry is not None:
            decision, entry_order, side = pending_entry
            raw = float(o[a])
            exit_action = "sell" if side > 0 else "buy_to_cover"
            stop_order = order(decision, "DB2.Stop", exit_action)
            target_order = order(decision, "DB2.Target", exit_action)
            stop_order.update(status="working", order_type="stop", activation_minute=a,
                              raw_trigger=raw - side * stop_points)
            target_order.update(status="working", order_type="limit", activation_minute=a,
                                raw_trigger=raw + side * target_points)
            eoc_order = order(decision, "DB2.ExitOnClose", exit_action) if end_min is not None else None
            if eoc_order is not None:
                eoc_order.update(status="working", order_type="session_close", activation_minute=a)
            position = _Position(raw, a, side, raw - side * stop_points,
                                 raw + side * target_points, decision,
                                 entry_order["order_id"], raw, stop_order, target_order, eoc_order)
            entry_order.update(status="filled", fill_minute=a, raw_fill=raw,
                               activation_minute=a, fill_bar_index=int(row["bar_index"]),
                               native_fill_close=int(row["global_close"]))
            pending_entry = None
        if pending_exits:
            if position is not None:
                # All are market orders for this same opening price. Keep the
                # last source label (TimeX after VwapX after Carry), and audit
                # every simultaneously generated order rather than double-sell.
                winner = pending_exits[-1]
                position.worst = min(position.worst, o[a]) if position.side > 0 else max(position.worst, o[a])
                finish(a, float(o[a]), 2, winner["name"], "open", winner)
                for item in pending_exits[:-1]:
                    item["status"] = "superseded_same_open"
            else:
                for item in pending_exits:
                    item["status"] = "cancelled_flat"
            pending_exits = []
        if position is not None:
            # _walk regards its first minute as the entry minute. Preserve its
            # gap-stop rule when walking a later chart-bar segment separately.
            gap_stop = a > position.entry_minute and (
                (position.side > 0 and o[a] <= position.stop) or
                (position.side < 0 and o[a] >= position.stop))
            if gap_stop:
                position.worst = min(position.worst, o[a]) if position.side > 0 else max(position.worst, o[a])
                finish(a, float(o[a]), 0, "DB2.Stop", "open")
            else:
                minute, px, kind, worst = _walk(o, h, l, c, a, z, position.side,
                                               position.stop, position.target, target_through)
                position.worst = min(position.worst, worst) if position.side > 0 else max(position.worst, worst)
                if kind != 2:
                    gap_fill = kind == 0 and minute > position.entry_minute and (
                        (position.side > 0 and o[minute] <= position.stop) or
                        (position.side < 0 and o[minute] >= position.stop))
                    finish(int(minute), float(px), int(kind),
                           "DB2.Target" if kind == 1 else "DB2.Stop",
                           "open" if gap_fill else "intrabar")
        # SetExitOnClose is a built-in exit active on the entry bar. Do not
        # move it to an inferred holiday/RTH endpoint absent chart metadata.
        if position is not None and end_min is not None and row["j"] == end_min:
            close_order = position.eoc_order
            finish(z, float(c[z]), 2, "DB2.ExitOnClose", "close", close_order)
        new_date = row["day"] != previous_day
        if new_date:
            attempts = 0
            if position is not None:
                pending_exits.append(order(row, "DB2.Carry", "sell" if position.side > 0 else "buy_to_cover"))
        desired = bool(row["entry_eligible"])
        scheduled_side = 1
        if schedule is not None:
            desired = (row["bar_index"] in schedule and row["in_period"]
                       and row["timing_ok"] and row["win_count"] >= boundary_len
                       and row["boundary"] > 0)
            scheduled_side = int(schedule.get(row["bar_index"], 1))
        if desired and mask[row_no] and position is None and attempts < max_trades:
            side = int(rng_side.choice((-1, 1))) if rng_side is not None else scheduled_side
            pending_entry = (row, order(row, "DB2.Long" if side > 0 else "NULL.Short",
                                        "buy" if side > 0 else "sell_short"), side)
            attempts += 1
        if position is not None:
            if vwap_exit_bars > 0 and row["bars_below_vwap"] >= vwap_exit_bars:
                pending_exits.append(order(row, "DB2.VwapX", "sell" if position.side > 0 else "buy_to_cover"))
            early_flat = apex_safe and row["early_date"] and row["j"] >= _minute(1130)
            if early_flat or row["j"] >= flat_min:
                if early_flat or exit_on_bar_close:
                    name = "APEX.EarlyTimeX" if early_flat else "DB2.TimeX"
                    close_order = order(row, name, "sell" if position.side > 0 else "buy_to_cover")
                    finish(z, float(c[z]), 2, name, "close", close_order)
                    for item in pending_exits:
                        item["status"] = "cancelled_flat"
                    pending_exits = []
                else:
                    pending_exits.append(order(row, "DB2.TimeX", "sell" if position.side > 0 else "buy_to_cover"))
        previous_day = int(row["day"])
    censored = []
    if position is not None:
        censored.append(dict(raw_entry=position.raw_entry, global_entry=position.entry_minute,
                             side=position.side, reason="period_or_data_endpoint",
                             decision_index=int(position.decision["bar_index"])))
        position.stop_order["status"] = "working_censored"
        position.target_order["status"] = "working_censored"
        if position.eoc_order is not None:
            position.eoc_order["status"] = "working_censored"
    if pending_entry is not None:
        pending_entry[1]["status"] = "unfilled_endpoint"
    for item in pending_exits:
        item["status"] = "unfilled_endpoint"
    t = pd.DataFrame(trades, columns=TRADE_COLUMNS)
    t.attrs.update(orders=pd.DataFrame(orders), censored=censored,
                   net_includes_slippage=True, target_through=target_through,
                   slip_ticks=slip_ticks, commission=commission,
                   session_end=session_end, veto_mode=veto_mode,
                   apex_safe=apex_safe,
                   volume_proxy=f.attrs.get("volume_proxy"), years=tuple(years))
    return t, f


def _fixture_grid(dates, bars):
    """Tiny in-memory Grid24; bars are (date, HHMM, O,H,L,C,V)."""
    g = Grid24.__new__(Grid24)
    cal = pd.date_range(min(dates), max(dates), freq="D")
    g.ts = cal.to_numpy()
    g.dates = cal.strftime("%Y%m%d").astype(int).to_numpy()
    g.D = len(cal)
    for k in ("o", "h", "l", "c", "v"):
        setattr(g, k, np.full((g.D, 1440), np.nan))
    for date, time, *values in bars:
        day = int(cal.get_loc(pd.Timestamp(date)))
        j = _minute(time)
        for k, value in zip(("o", "h", "l", "c", "v"), values):
            getattr(g, k)[day, j] = value
    g.trading = np.flatnonzero(cal.dayofweek < 5)
    return g


def synthetic_checks():
    """Meaningful fixtures only; no files, historical data, or result selection."""
    passed = []
    # Prior 15 completed positive Date ranges include a Sunday; a cross-date
    # 23:45 spike belongs to the next Date's 00:00 native bar.
    dates = pd.date_range("2020-01-01", periods=17)
    bars = [(str(d.date()), 1200, 100, 110 + i, 100, 105, 1)
            for i, d in enumerate(dates)]
    bars.append(("2020-01-15", 2345, 100, 1000, 100, 101, 1))
    g = _fixture_grid(dates, bars)
    f = prepare_features(g)
    current = f[f.date == "2020-01-16"].iloc[0]
    assert current.j == 0 and current.high == 1000
    assert current.boundary == np.mean(np.arange(10.0, 25.0))
    assert f[f.date == "2020-01-17"].iloc[0].boundary == np.mean(list(np.arange(11.0, 25.0)) + [900.0])
    passed.append("prior15_positive_Date_ranges_Sunday_midnight")
    g = _fixture_grid(["2020-01-01", "2020-01-04"], [
        ("2020-01-01", 1200, 100, 110, 100, 105, 1),
        ("2020-01-02", 1200, 100, 100, 100, 100, 1),
        ("2020-01-03", 1200, 100, 120, 100, 110, 1),
        ("2020-01-04", 1200, 100, 130, 100, 115, 1),
    ])
    assert prepare_features(g, boundary_len=2).iloc[-1].boundary == 15
    passed.append("zero_range_Date_not_counted")
    g = _fixture_grid(["2020-01-01", "2020-01-02"], [
        ("2020-01-01", 1000, 110, 140, 80, 110, 10),
        ("2020-01-01", 1030, 120, 130, 100, 120, 30),
        ("2020-01-01", 1100, 150, 160, 140, 150, 0),
        ("2020-01-02", 1000, 99, 100, 98, 99, 0),
    ])
    f = prepare_features(g)
    np.testing.assert_allclose(f.vwap, [110, 115, 115, 99])
    passed.append("30m_TP_volume_VWAP_zero_volume_reset")
    g = _fixture_grid(["2020-01-02", "2020-01-06"], [
        ("2020-01-02", 1200, 10000, 10010, 9990, 10000, 1),
        ("2020-01-03", 1200, 10000, 10010, 9990, 10000, 1),
        ("2020-01-05", 1800, 10000, 10010, 9990, 10000, 1),
        ("2020-01-06", 930, 10000, 10010, 9990, 10000, 1),
        ("2020-01-06", 1000, 9990, 10000, 9980, 9990, 1),
    ])
    f = prepare_features(g, boundary_len=1)
    assert f.iloc[-1].drift_ref == 10000 and f.iloc[-1].drift_pct == -0.10
    _, gated = run(g, years=(2020, 2020), boundary_len=1, features=f)
    _, ungated = run(g, years=(2020, 2020), boundary_len=1, features=f, veto_mode=0)
    assert not gated.iloc[-1].context_ok and ungated.iloc[-1].context_ok
    passed.append("Close4_across_weekend_exact_veto_threshold")
    # Source caps submitted attempts, and accepts 10:00 and 14:00 inclusive.
    bars = [("2020-01-01", 1200, 100, 110, 90, 100, 1)]
    bars += [("2020-01-02", 1000, 100, 120, 90, 120, 1),
             ("2020-01-02", 1001, 120, 161, 119, 160, 1),
             ("2020-01-02", 1030, 150, 160, 140, 160, 1),
             ("2020-01-02", 1031, 160, 201, 159, 200, 1),
             ("2020-01-02", 1100, 190, 200, 180, 200, 1),
             ("2020-01-02", 1400, 190, 200, 180, 200, 1),
             ("2020-01-02", 1401, 200, 241, 199, 240, 1)]
    g = _fixture_grid(["2020-01-01", "2020-01-02"], bars)
    t, f = run(g, years=(2020, 2020), boundary_len=1, veto_mode=0)
    submitted = t.attrs["orders"].query("action == 'buy'")
    assert len(submitted) == 2 and list(submitted.decision_j) == [600, 630]
    assert f[f.time == 1400].iloc[-1].timing_ok
    assert (t.kind == 1).all() and np.allclose(t.net, 800 - 7.25 - 5)
    passed.append("inclusive_entry_window_two_submissions_costs")
    # Entry-minute bracket/path and fill-through are delegated to shared walk.
    for high, expected in [(141, 1), (200, 0)]:
        aa = np.array([100.0])
        _, _, kind, _ = _walk(aa, np.array([float(high)]), np.array([24.0]), aa,
                              0, 0, 1, 25.0, 140.0, 1.0)
        assert kind == expected
    aa = np.array([100.0])
    assert _walk(aa, np.array([140.0]), np.array([99.0]), aa, 0, 0, 1, 25., 140., 1.)[2] == 2
    assert _walk(aa, np.array([140.0]), np.array([99.0]), aa, 0, 0, 1, 25., 140., 0.)[2] == 1
    passed.append("prearmed_entry_brackets_shared_path_target_touch")
    # A time exit waits across a half-day halt; no inferred RTH close.
    bars = [("2020-01-01", 1200, 100, 110, 90, 100, 1),
            ("2020-01-02", 1000, 100, 120, 90, 120, 1),
            ("2020-01-02", 1001, 120, 121, 119, 120, 1),
            ("2020-01-02", 1200, 120, 121, 119, 120, 1),
            ("2020-01-02", 1701, 130, 131, 129, 130, 1)]
    g = _fixture_grid(["2020-01-01", "2020-01-02"], bars)
    t, _ = run(g, years=(2020, 2020), boundary_len=1, veto_mode=0, flatten_time=1200)
    assert len(t) == 1 and t.iloc[0].j1 == 1021 and t.iloc[0].raw_exit == 130
    assert t.iloc[0].why == "DB2.TimeX" and t.iloc[0].exit_phase == "open"
    passed.append("next_bar_market_across_halfday_halt")
    # Midnight Carry is submitted after the 00:00 bar, not at its open.
    bars = [("2020-01-01", 1200, 100, 110, 90, 100, 1),
            ("2020-01-02", 1000, 100, 120, 90, 120, 1),
            ("2020-01-02", 1001, 120, 121, 119, 120, 1),
            ("2020-01-02", 2345, 122, 123, 121, 122, 1),
            ("2020-01-03", 1, 125, 126, 124, 125, 1)]
    g = _fixture_grid(["2020-01-01", "2020-01-03"], bars)
    kw = dict(years=(2020, 2020), boundary_len=1, veto_mode=0,
              flatten_time=2359, vwap_exit_bars=0)
    t, _ = run(g, session_end=None, **kw)
    assert len(t) == 1 and t.iloc[0].why == "DB2.Carry" and t.iloc[0].j1 == 1
    assert t.iloc[0].exit_day == 2 and t.iloc[0].carry
    t, _ = run(g, session_end=2400, **kw)
    assert len(t) == 1 and t.iloc[0].why == "DB2.ExitOnClose"
    assert t.iloc[0].exit_day == 1 and t.iloc[0].j1 == 1425
    t, _ = run(g, session_end=1600, **kw)
    assert t.iloc[0].why == "DB2.Carry"
    passed.append("midnight_carry_vs_declared_session_end_no_inferred_close")
    # The Apex profile is a separate declared rule, using the existing VB
    # early-close calendar. Missing holiday closes remain unresolved.
    bars = [("2020-07-02", 1200, 100, 110, 90, 100, 1),
            ("2020-07-03", 1000, 100, 120, 90, 120, 1),
            ("2020-07-03", 1001, 120, 121, 119, 120, 1),
            ("2020-07-03", 1100, 120, 121, 119, 120, 1),
            ("2020-07-03", 1130, 123, 124, 122, 123, 1),
            ("2020-07-03", 1530, 125, 126, 124, 125, 1),
            ("2020-07-03", 1531, 126, 127, 125, 126, 1)]
    g = _fixture_grid(["2020-07-02", "2020-07-03"], bars)
    t, f = run(g, years=(2020, 2020), boundary_len=1, veto_mode=0, apex_safe=True)
    assert len(t) == 1 and t.iloc[0].j1 == 690 and t.iloc[0].why == "APEX.EarlyTimeX"
    assert t.iloc[0].exit_phase == "close" and not f[f.time == 1100].iloc[-1].timing_ok
    t, _ = run(g, years=(2020, 2020), boundary_len=1, veto_mode=0)
    assert len(t) == 1 and t.iloc[0].j1 == 931 and t.iloc[0].why == "DB2.TimeX"
    g = _fixture_grid(["2020-07-02", "2020-07-03"], bars[:4])
    t, _ = run(g, years=(2020, 2020), boundary_len=1, veto_mode=0, apex_safe=True)
    assert t.empty and len(t.attrs["censored"]) == 1
    passed.append("Apex_early_calendar_1130_observed_close_no_fabricated_price")
    # A stop on the entry minute pays both market-entry and stop slippage.
    g = _fixture_grid(["2020-01-01", "2020-01-02"], [
        ("2020-01-01", 1200, 100, 110, 90, 100, 1),
        ("2020-01-02", 1000, 100, 120, 90, 120, 1),
        ("2020-01-02", 1001, 120, 300, 44, 100, 1),
    ])
    t, _ = run(g, years=(2020, 2020), boundary_len=1, veto_mode=0)
    assert len(t) == 1 and t.iloc[0].kind == 0 and t.iloc[0].raw_exit == 45
    assert t.iloc[0].net == -1500 - 7.25 - 10
    assert t.iloc[0].exit_order_id in t.attrs["orders"].query("status == 'filled'").order_id.values
    passed.append("entry_minute_stop_and_two_fill_slippage")
    # Period gating is tested without accessing any historical observations.
    try:
        run(g, years=(2023, 2023))
    except ValueError as error:
        assert "2023+" in str(error)
    else:
        raise AssertionError("post-2022 period gate did not hold")
    passed.append("post2022_gate")
    return passed


if __name__ == "__main__":
    print("Synthetic checks:", ", ".join(synthetic_checks()))
