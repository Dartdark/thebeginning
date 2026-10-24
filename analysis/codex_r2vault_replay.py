"""R2Vault frozen reconstruction (a973f077); no import-time market-data IO.

The PDF contains no source code. These five models implement the committed
interpretations, not verified author MultiCharts parity. Grid24.bars(5) is
reused through the reviewed observed-bar adapter. Entry and exit boundaries
follow a deterministic, causal one-minute OHLC path, not a whole-minute-low
shortcut after an intraminute stop entry.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from numba import njit

from codex_anson_replay import prepare_bars as prepare_observed_bars
from codex_anson_replay import _gap_records
from replica import is_early_close

R2_LENGTH = 576
R2_THRESHOLD = .030
NOISE = .20
STOP_POINTS, TARGET_POINTS, THROUGH = 75., 40., 1.
MODELS = {
    "et_raw": dict(start=510, end=870, apex=False, daily_reset=False),
    "et_apex": dict(start=510, end=870, apex=True, daily_reset=False),
    "ct_raw": dict(start=570, end=930, apex=False, daily_reset=False),
    "ct_apex": dict(start=570, end=930, apex=True, daily_reset=False),
    "et_daily_reset_raw": dict(start=510, end=870, apex=False, daily_reset=True),
}
FIRST_DATE = pd.Timestamp("2018-01-01")


@dataclass
class Prepared:
    bars: pd.DataFrame
    observed: np.ndarray
    known_closed: np.ndarray
    force_open: np.ndarray
    cutoff_row: int

    @property
    def observed_minutes(self):
        return self.observed


@dataclass
class ReplayResult:
    trades: pd.DataFrame
    audit: pd.DataFrame
    events: pd.DataFrame
    gaps: pd.DataFrame
    open_positions: pd.DataFrame
    state: dict
    spec: dict


def frozen_spec(model):
    if model not in MODELS:
        raise ValueError("Unknown frozen R2Vault model")
    return dict(model=model, **MODELS[model], bar_minutes=5, history="all observed24h bars",
                r2_length=576, threshold=.030, noise=.20, max_entries_per_CT_date=3,
                stop_points=75., target_points=40., break_even=False, r2_exit_disabled=True,
                path="OHLC if H-O<=O-L, else OLHC; opening orders before segments",
                target="one-point trade-through, fill at target; favorable qualifying gap at open",
                forced_exit_priority="queued market before resting protective opening gaps",
                costs="raw geometry; monetary commission and fill slips applied by caller",
                author_parity=False)


@njit(cache=True)
def rolling_regression(close, length=576):
    """Stable rolling centered OLS, periodically rebased; no future prices."""
    n = len(close)
    slope, r2 = np.full(n, np.nan), np.full(n, np.nan)
    cx = (length-1)/2.
    sxx = length*(length*length-1)/12.
    mean = m2 = cov = 0.
    for i in range(length-1, n):
        if i == length-1 or (i-length+1) % 1024 == 0:
            mean = 0.
            for k in range(length):
                mean += close[i-length+1+k]
            mean /= length
            m2 = cov = 0.
            for k in range(length):
                y = close[i-length+1+k]-mean
                m2 += y*y
                cov += (k-cx)*y
        else:
            old, new = close[i-length], close[i]
            cov += cx*(new-old)-length*(mean-old)
            newmean = mean+(new-old)/length
            m2 += (new-old)*(new-newmean+old-mean)
            mean = newmean
        if m2 <= 1e-12:
            slope[i], r2[i] = 0., 0.
        else:
            slope[i] = cov/sxx
            val = cov*cov/(sxx*m2)
            if val > 1.+1e-7:
                raise ValueError("Regression numerical error beyond roundoff")
            r2[i] = min(1., max(0., val))
    return slope, r2


def prepare(g, cutoff_date=None):
    base = prepare_observed_bars(g, cutoff_date)
    # CME eliminated the historical15:15..15:30 pause effective2021-06-28.
    # This labels missing observations only; existing price bars are retained.
    known_closed = base.known_closed.copy()
    old_pause = pd.DatetimeIndex(g.ts[:base.cutoff_row+1]) < pd.Timestamp("2021-06-28")
    known_closed[old_pause, 916:931] = True
    b = base.bars.copy()
    b["slope"], b["r2"] = rolling_regression(b.c.to_numpy(float))
    # Two per-minute opening-flatten clocks: ordinary / early, all arrays
    # indexed by the calendar minute's flat Grid24 address.
    force = np.zeros((2, (base.cutoff_row+1)*1440), dtype=np.bool_)
    openings = b.open_flat.to_numpy(np.int64)[1:]
    times = b.bar_j.to_numpy(np.int64)[:-1]
    force[0, openings] = times >= 955
    deadline = np.where(b.early_close_proxy.to_numpy(bool)[:-1], 690, 955)
    force[1, openings] = times >= deadline
    return Prepared(b, base.observed_minutes, known_closed, force, base.cutoff_row)


@njit(cache=True)
def minute_nodes(o, h, l, c):
    nodes = np.empty(4)
    nodes[0], nodes[3] = o, c
    if h-o <= o-l:
        nodes[1], nodes[2] = h, l
    else:
        nodes[1], nodes[2] = l, h
    return nodes


@njit(cache=True)
def _remaining_path(nodes, entry, side, cursor, next_segment):
    """Traverse a held position from a path cursor, returning causal extrema.

    Result: exited, price, kind, exit_segment, adverse_px. Target event price
    is target+/-1, while the executable limit fill is the target itself.
    """
    stop, target = entry-side*STOP_POINTS, entry+side*TARGET_POINTS
    adverse_signed = side*cursor
    for seg in range(next_segment, 4):
        dest = nodes[seg]
        if side > 0:
            if dest < cursor and dest <= stop <= cursor:
                adverse_signed = min(adverse_signed, stop)
                return True, stop, 0, seg, adverse_signed
            if dest > cursor and cursor <= target+THROUGH <= dest:
                adverse_signed = min(adverse_signed, cursor)
                return True, target, 1, seg, adverse_signed
        else:
            if dest > cursor and cursor <= stop <= dest:
                adverse_signed = min(adverse_signed, -stop)
                return True, stop, 0, seg, -adverse_signed
            if dest < cursor and dest <= target-THROUGH <= cursor:
                adverse_signed = min(adverse_signed, -cursor)
                return True, target, 1, seg, -adverse_signed
        adverse_signed = min(adverse_signed, side*dest)
        cursor = dest
    return False, np.nan, -1, -1, side*adverse_signed


@njit(cache=True)
def held_minute(o, h, l, c, entry, side):
    """A position held before this open: chronological gap orders first."""
    stop, target = entry-side*STOP_POINTS, entry+side*TARGET_POINTS
    if (o-stop)*side <= 0:
        return True, o, 0, 0, o
    if (o-target)*side >= THROUGH:
        return True, o, 1, 0, o
    return _remaining_path(minute_nodes(o, h, l, c), entry, side, o, 1)


@njit(cache=True)
def entering_minute(o, h, l, c, order):
    """One long buy-stop, then protection only after its actual crossing.

    Result: entered,entry,entry_segment,exited,exit,kind,exit_segment,adverse.
    Entry segment0 is an opening gap. Low/Open before an intraminute entry
    cannot become held risk or an executable stop fill.
    """
    nodes = minute_nodes(o, h, l, c)
    if o >= order:
        done, px, kind, seg, adverse = _remaining_path(nodes, o, 1, o, 1)
        return True, o, 0, done, px, kind, seg, adverse
    cursor = o
    for seg in range(1, 4):
        dest = nodes[seg]
        if dest > cursor and cursor <= order <= dest:
            done, px, kind, xseg, adverse = _remaining_path(nodes, order, 1, order, seg)
            return True, order, seg, done, px, kind, xseg, adverse
        cursor = dest
    return False, np.nan, -1, False, np.nan, -1, -1, np.nan


@njit(cache=True)
def fixed_entry_minute(o, h, l, c, entry, side, entry_segment):
    """Mirror a fixed actual entry at the same causal path cursor."""
    if entry_segment == 0:
        return _remaining_path(minute_nodes(o, h, l, c), entry, side, entry, 1)
    return _remaining_path(minute_nodes(o, h, l, c), entry, side, entry, entry_segment)


@njit(cache=True)
def _walk_fixed_arrays(o, h, l, c, observed, force_open, start, entry, side, entry_segment, apex):
    """Fast fixed-entry path used by null controls; no entry/open substitution."""
    for minute in range(start, len(o)):
        if not observed[minute]:
            continue
        if minute > start and apex and force_open[minute]:
            return minute, o[minute], 2, 0, o[minute]
        if minute == start:
            done, px, kind, segment, adverse = fixed_entry_minute(o[minute], h[minute], l[minute], c[minute], entry, side, entry_segment)
        else:
            done, px, kind, segment, adverse = held_minute(o[minute], h[minute], l[minute], c[minute], entry, side)
        if done:
            return minute, px, kind, segment, adverse
    return -1, np.nan, -1, -1, np.nan


def walk_fixed_entry(g, prepared, entry_row, entry_j, entry_price, side, model,
                     entry_phase="open", entry_segment=0):
    """Fixed-entry null geometry; preserves the actual intraminute cursor."""
    cfg = MODELS[model]
    start = int(entry_row)*1440+int(entry_j)
    seg = 0 if entry_phase == "open" else int(entry_segment)
    force = prepared.force_open[1]
    end = (prepared.cutoff_row+1)*1440
    result = _walk_fixed_arrays(*(getattr(g, x).ravel()[:end] for x in ("o", "h", "l", "c")),
                                prepared.observed.ravel(), force, start, float(entry_price), int(side), seg, cfg["apex"])
    minute, px, kind, xseg, adverse = result
    if minute < 0:
        return None
    return dict(entry_flat=start, exit_flat=int(minute), exit_row=int(minute)//1440,
                exit_j=int(minute)%1440, exit=float(px), kind=int(kind),
                exit_phase="open" if xseg == 0 else "intrabar", exit_segment=int(xseg),
                exit_minute_adverse_px=float(adverse), gross_points=(float(px)-float(entry_price))*int(side))


@njit(cache=True)
def walk_fixed_many(o, h, l, c, observed, force_open, starts, entries, sides, segments, apex):
    """Bulk primitive: columns exit_flat,exit,kind,segment,adverse,gross_points."""
    out = np.empty((len(starts), 6))
    for i in range(len(starts)):
        minute, px, kind, seg, adverse = _walk_fixed_arrays(o, h, l, c, observed, force_open,
                                                           starts[i], entries[i], sides[i], segments[i], apex)
        out[i, 0], out[i, 1], out[i, 2], out[i, 3], out[i, 4] = minute, px, kind, seg, adverse
        out[i, 5] = (px-entries[i])*sides[i]
    return out


TRADE_COLUMNS = [
    "model", "trade_id", "date", "day", "gridrow", "side", "entry_row", "entry_j", "entry_flat",
    "entry_date", "entry", "entry_phase", "entry_segment", "entry_path_order", "entry_bar_index",
    "entry_minute_adverse_px", "exit_row", "exit_j", "exit_flat", "exit_date", "exit", "exit_phase",
    "exit_segment", "exit_bar_index", "exit_minute_adverse_px", "j0", "j1", "kind", "exit_reason",
    "kind_label", "gross_points", "gross_nq", "stop_px", "target_px", "order_px",
    "signal_bar_index", "signal_row", "signal_j", "signal_r2", "signal_slope", "signal_close",
    "already_crossed_at_signal", "opening_gap_entry", "entry_gap_points",
    "vault_high", "vault_low", "vault_bar_index", "entry_number_today", "mae_points_observed",
    "path_start_flat", "path_end_flat_exclusive", "cross_date", "late_after_1559",
    "missing_held_minutes", "known_closure_missing_minutes", "unknown_held_minutes", "account_eligible",
]
GAP_COLUMNS = ["model", "trade_id", "trade_entry_flat", "trade_exit_flat", "first_flat", "last_flat", "minutes", "classification"]
EVENT_COLUMNS = ["model", "date", "gridrow", "minute", "bar_index", "event", "price", "phase"]


def _calendar(g, prepared, model):
    cfg, rows = MODELS[model], []
    trading = set(int(d) for d in g.trading)
    for d, date in enumerate(pd.DatetimeIndex(g.ts[:prepared.cutoff_row+1])):
        early = bool(is_early_close(date))
        end = min(cfg["end"], 690) if cfg["apex"] and early else cfg["end"]
        first = cfg["start"]-4
        apex_last = 691 if early else 956
        priced_or_closed = prepared.observed[d] | prepared.known_closed[d]
        control = priced_or_closed[first:end+1]
        account = priced_or_closed[first:apex_last+1]
        rows.append(dict(model=model, date=date, gridrow=d, is_trading_row=d in trading,
                         early_close_proxy=early, window_start=cfg["start"], window_end=end,
                         control_window_complete=bool(control.all()),
                         control_eligible=bool(d in trading and control.all()),
                         account_window_first_j=first, account_window_last_j=apex_last,
                         account_window_complete=bool(account.all()),
                         missing_account_window_minutes=int((~account).sum()),
                         known_closed_account_minutes=int((prepared.known_closed[d, first:apex_last+1]
                                                           & ~prepared.observed[d, first:apex_last+1]).sum()),
                         entries=0, exits=0, orders_issued=0, vault_updates=0,
                         orders_already_crossed_at_signal=0, opening_gap_entries=0,
                         affected_by_unknown_held_gap=False, affected_by_cross_date_trade=False,
                         affected_by_late_position=False, affected_by_unclosed_trade=False,
                         account_eligible=False))
    return pd.DataFrame(rows)


def _apply_trade_audit(audit, x, include_entry=True):
    er, xr = int(x["entry_row"]), int(x["exit_row"])
    if include_entry:
        audit.loc[er, "entries"] += 1
    audit.loc[xr, "exits"] += 1
    if include_entry and x["opening_gap_entry"]:
        audit.loc[er, "opening_gap_entries"] += 1
    if x["unknown_held_minutes"]:
        audit.loc[er:xr, "affected_by_unknown_held_gap"] = True
    if er != xr:
        audit.loc[er:xr, "affected_by_cross_date_trade"] = True
    if x["late_after_1559"]:
        audit.loc[er:xr, "affected_by_late_position"] = True


def _close(g, prepared, model, position, minute, px, kind, segment, adverse, bar_index,
           trades, gaps, audit):
    er, ej = divmod(int(position["entry_flat"]), 1440)
    xr, xj = divmod(int(minute), 1440)
    phase = "open" if segment == 0 else "intrabar"
    end = int(minute)+(phase != "open")
    group, known, unknown = _gap_records(prepared, int(position["entry_flat"]), end, len(trades), model)
    gaps.extend(group)
    points = float(px)-position["entry"]
    record = dict(position)
    record.update(model=model, trade_id=len(trades), date=pd.Timestamp(g.ts[er]), day=er, gridrow=er,
                  side=1, entry_row=er, entry_j=ej, entry_date=pd.Timestamp(g.ts[er]),
                  exit_row=xr, exit_j=xj, exit_flat=int(minute), exit_date=pd.Timestamp(g.ts[xr]),
                  exit=float(px), exit_phase=phase, exit_segment=int(segment), exit_bar_index=int(bar_index),
                  exit_minute_adverse_px=float(adverse), j0=ej, j1=xj, kind=int(kind),
                  exit_reason=("stop", "target", "apex_flat")[kind],
                  kind_label=("stop", "target", "apex_flat")[kind], gross_points=points, gross_nq=points*20.,
                  path_start_flat=int(position["entry_flat"]), path_end_flat_exclusive=end,
                  cross_date=er != xr,
                  late_after_1559=er != xr or xj > 960 or (xj == 960 and phase != "open"),
                  missing_held_minutes=known+unknown, known_closure_missing_minutes=known,
                  unknown_held_minutes=unknown,
                  mae_points_observed=max(position["mae_points_observed"], position["entry"]-float(adverse), -points, 0.))
    trades.append(record)
    if audit is not None:
        _apply_trade_audit(audit, record, include_entry=False)


def _open_snapshot(g, prepared, model, position):
    columns = TRADE_COLUMNS+["last_observed_row", "last_observed_j", "last_observed_flat", "last_observed_mark", "is_open", "status"]
    if position is None:
        return pd.DataFrame(columns=columns)
    x = dict(position)
    er, ej = divmod(int(x["entry_flat"]), 1440)
    x.update(model=model, side=1, date=pd.Timestamp(g.ts[er]), day=er, gridrow=er,
             entry_row=er, entry_j=ej, entry_date=pd.Timestamp(g.ts[er]),
             entry_phase=x["entry_phase"], is_open=True, status="unrealized_at_cutoff")
    last = int(x["last_observed_flat"])+1
    _, known, unknown = _gap_records(prepared, int(x["entry_flat"]), last, -1, model)
    x.update(missing_held_minutes=known+unknown, known_closure_missing_minutes=known, unknown_held_minutes=unknown)
    return pd.DataFrame([x]).reindex(columns=columns)


def _eligible(audit, start):
    audit["account_eligible"] = (audit.is_trading_row & audit.account_window_complete
        & ~audit.affected_by_unknown_held_gap & ~audit.affected_by_cross_date_trade
        & ~audit.affected_by_late_position & ~audit.affected_by_unclosed_trade & (audit.date >= start))
    audit["status"] = np.where(audit.account_eligible, "eligible", "excluded")


def replay(g, model="et_raw", cutoff_date=None, *, start_date=FIRST_DATE,
           prepared: Optional[Prepared] = None, initial_state=None):
    """Five-minute source calculations; one-minute causal fill traversal.

    State carries across the design/recent split. Before the first research
    date, vault/history warm up without entering positions. Coverage is an
    after-the-fact audit and never changes source features/orders.
    """
    import copy
    cfg, spec = MODELS[model], frozen_spec(model)
    p = prepare(g, cutoff_date) if prepared is None else prepared
    start = pd.Timestamp(start_date).normalize()
    audit = _calendar(g, p, model)
    state = copy.deepcopy(initial_state) if initial_state is not None else dict(
        vault_high=np.nan, vault_low=np.nan, vault_bar_index=-1, position=None, order=None,
        pending_flat=False, counter_day=-1, entries_today=0, last_bar_index=-1)
    trades, events, gaps = [], [], []
    for b in p.bars.itertuples(index=False):
        if int(b.bar_index) <= state["last_bar_index"]:
            continue
        # Source date and its entry counter are CT calendar based. Orders
        # never enter near midnight, so this also agrees with fill dates.
        if state["counter_day"] != int(b.gridrow):
            state["counter_day"], state["entries_today"] = int(b.gridrow), 0
            if cfg["daily_reset"]:
                state["vault_high"] = state["vault_low"] = np.nan
                state["vault_bar_index"] = -1
        active = b.date >= start
        order = state["order"]
        order_used = False
        first, last = int(b.open_flat), int(b.close_flat)
        minutes = np.flatnonzero(p.observed.ravel()[first:last+1])+first
        if active and state["pending_flat"] and state["position"] is not None:
            q = state["position"]
            _close(g, p, model, q, first, float(b.o), 2, 0, float(b.o), b.bar_index, trades, gaps, audit)
            events.append(dict(model=model, date=b.date, gridrow=int(b.gridrow), minute=first%1440,
                               bar_index=int(b.bar_index), event="exit", price=float(b.o), phase="open"))
            state["position"], state["pending_flat"] = None, False
        # Expiring buy stop is valid only during this next observed source bar.
        if active and (state["position"] is not None or order is not None):
            for minute in minutes:
                row, j = divmod(int(minute), 1440)
                oo, hh, ll, cc = (float(getattr(g, f)[row, j]) for f in ("o", "h", "l", "c"))
                held = state["position"] is not None
                entered = False
                if held:
                    done, px, kind, xseg, adverse = held_minute(oo, hh, ll, cc, state["position"]["entry"], 1)
                else:
                    early = cfg["apex"] and bool(is_early_close(pd.Timestamp(g.ts[row])))
                    window_end = min(cfg["end"], 690) if early else cfg["end"]
                    allowed = (order is not None and not order_used and state["entries_today"] < 3
                               and cfg["start"] < j <= window_end)
                    if not allowed:
                        continue
                    entered, entry, eseg, done, px, kind, xseg, adverse = entering_minute(oo, hh, ll, cc, order["order_px"])
                    if not entered:
                        continue
                    order_used = True
                    state["entries_today"] += 1
                    state["position"] = dict(order, entry_flat=int(minute), entry=float(entry),
                        entry_phase="open" if eseg == 0 else "intrabar", entry_segment=int(eseg),
                        entry_path_order="OHLC" if hh-oo <= oo-ll else "OLHC", entry_bar_index=int(b.bar_index),
                        stop_px=float(entry)-75., target_px=float(entry)+40.,
                        opening_gap_entry=bool(eseg == 0 and entry > order["order_px"]),
                        entry_gap_points=max(float(entry)-order["order_px"], 0.),
                        entry_minute_adverse_px=float(adverse), entry_number_today=state["entries_today"],
                        mae_points_observed=max(float(entry)-float(adverse), 0.))
                    audit.loc[row, "entries"] += 1
                    if eseg == 0 and entry > order["order_px"]:
                        audit.loc[row, "opening_gap_entries"] += 1
                    events.append(dict(model=model, date=pd.Timestamp(g.ts[row]), gridrow=row, minute=j,
                                       bar_index=int(b.bar_index), event="entry", price=float(entry),
                                       phase="open" if eseg == 0 else "intrabar"))
                q = state["position"]
                q["mae_points_observed"] = max(q["mae_points_observed"], q["entry"]-float(adverse), 0.)
                if done:
                    _close(g, p, model, q, minute, px, kind, xseg, adverse, b.bar_index, trades, gaps, audit)
                    events.append(dict(model=model, date=pd.Timestamp(g.ts[row]), gridrow=row, minute=j,
                                       bar_index=int(b.bar_index), event="exit", price=float(px),
                                       phase="open" if xseg == 0 else "intrabar"))
                    state["position"] = None
                else:
                    q.update(last_observed_row=row, last_observed_j=j, last_observed_flat=int(minute), last_observed_mark=cc)
        state["order"] = None
        # At the completed chart close, update vault before issuing orders.
        if np.isfinite(b.r2) and b.r2 <= R2_THRESHOLD:
            state["vault_high"], state["vault_low"] = float(b.h), float(b.l)
            state["vault_bar_index"] = int(b.bar_index)
            if active:
                audit.loc[int(b.gridrow), "vault_updates"] += 1
        early = cfg["apex"] and bool(b.early_close_proxy)
        end = min(cfg["end"], 690) if early else cfg["end"]
        if active and state["position"] is None and state["entries_today"] < 3 and cfg["start"] <= b.bar_j < end:
            vh, vl = state["vault_high"], state["vault_low"]
            if np.isfinite(vh) and vh > vl and np.isfinite(b.slope) and b.slope > 0:
                level = float(np.ceil((vh+.20*(vh-vl))/.25-1e-10)*.25)
                state["order"] = dict(order_px=level, signal_bar_index=int(b.bar_index),
                    signal_row=int(b.gridrow), signal_j=int(b.bar_j), signal_r2=float(b.r2), signal_slope=float(b.slope),
                    signal_close=float(b.c), already_crossed_at_signal=bool(b.c >= level),
                    vault_high=vh, vault_low=vl, vault_bar_index=state["vault_bar_index"])
                audit.loc[int(b.gridrow), "orders_issued"] += 1
                if b.c >= level:
                    audit.loc[int(b.gridrow), "orders_already_crossed_at_signal"] += 1
        deadline = 690 if early else 955
        if active and cfg["apex"] and state["position"] is not None and b.bar_j >= deadline:
            state["pending_flat"] = True
        state["last_bar_index"] = int(b.bar_index)
    if state["position"] is not None:
        er = int(state["position"]["entry_flat"])//1440
        audit.loc[er:, "affected_by_unclosed_trade"] = True
    _eligible(audit, start)
    t = pd.DataFrame(trades)
    if len(t):
        t["account_eligible"] = t.day.map(audit.set_index("gridrow").account_eligible).to_numpy(bool)
        t = t.reindex(columns=TRADE_COLUMNS)
    else:
        t = pd.DataFrame(columns=TRADE_COLUMNS)
    return ReplayResult(t, audit.loc[audit.date >= start].reset_index(drop=True),
        pd.DataFrame(events, columns=EVENT_COLUMNS), pd.DataFrame(gaps, columns=GAP_COLUMNS),
        _open_snapshot(g, p, model, state["position"]), state, spec)


def synthetic_checks():
    """All checks use invented prices; no actual source returns are read."""
    rng = np.random.default_rng(719)
    close = 1e8+np.cumsum(rng.normal(0., .3, 12000))
    slope, r2 = rolling_regression(close)
    x = np.arange(576)-575/2.
    sxx = np.dot(x, x)
    max_slope = max_r2 = 0.
    for i in range(575, len(close), 47):
        y = close[i-575:i+1]
        y = y-y.mean()
        cov = np.dot(x, y)
        direct_s, direct_r = cov/sxx, cov*cov/(sxx*np.dot(y, y))
        max_slope = max(max_slope, abs(direct_s-slope[i]))
        max_r2 = max(max_r2, abs(direct_r-r2[i]))
    assert max_slope <= 1e-6 and max_r2 <= 1e-6
    cs, cr = rolling_regression(np.full(900, 30000.))
    assert (cs[575:] == 0).all() and (cr[575:] == 0).all()
    # Entry after the low: no pre-entry Low10 can become a held stop.
    e = entering_minute(100., 200., 10., 180., 140.)
    assert e[0] and e[2] == 2 and e[3] and e[4] == 180. and e[5] == 1 and e[7] == 140.
    # High-first target occurs before a later low which would hit the stop.
    e = entering_minute(100., 160., 0., 80., 110.)
    assert e[2] == 1 and e[3] and e[4] == 150. and e[5] == 1 and e[7] == 110.
    # Same path, insufficient high: stop occurs only on the later down leg.
    e = entering_minute(100., 140., 0., 80., 110.)
    assert e[3] and e[4] == 35. and e[5] == 0 and e[7] == 35.
    xgap = held_minute(145., 200., 0., 100., 100., 1)
    assert xgap[:4] == (True, 145., 1, 0)
    xgap = held_minute(20., 200., 0., 100., 100., 1)
    assert xgap[:4] == (True, 20., 0, 0)
    assert not held_minute(100., 140.75, 90., 100., 100., 1)[0]
    assert held_minute(100., 141., 90., 100., 100., 1)[0]
    # Mirrored short begins at the long entry cursor, not before the low.
    short = fixed_entry_minute(100., 230., 10., 180., 140., -1, 2)
    assert short[0] and short[1] == 215. and short[2] == 0
    from grid24 import Grid24
    g = Grid24.__new__(Grid24)
    g.ts = pd.date_range("2018-01-01", periods=3).to_numpy()
    g.D, g.trading = 3, np.arange(3)
    g.dates = pd.DatetimeIndex(g.ts).strftime("%Y%m%d").to_numpy(int)
    shape = (3, 1440)
    g.o, g.c = np.full(shape, 1000.), np.full(shape, 1000.)
    g.h, g.l, g.v = np.full(shape, 1001.), np.full(shape, 999.), np.ones(shape)
    for d in range(3):
        g.h[d, 511:526] = 1100.
        g.l[d, 511:526] = 1000.
    p = prepare(g)
    # Synthetic feature values isolate order lifecycle without manufacturing
    # any real-market return or tuning a source threshold.
    p.bars["slope"] = 1.
    p.bars["r2"] = np.where(p.bars.bar_j <= 510, .01, .10)
    a = replay(g, "et_raw", prepared=p)
    assert len(a.trades) == 9
    assert (a.trades.groupby("entry_date").size() == 3).all()
    assert np.array_equal(a.trades.loc[a.trades.day == 0, "entry_j"], [511, 516, 521])
    assert (a.trades.entry_minute_adverse_px >= a.trades.entry).all()
    assert (a.trades.entry_minute_adverse_px == a.trades.exit_minute_adverse_px).all()
    # Pause is metadata only; its historical end date does not change bars.
    assert p.known_closed[0, 916:931].all()
    # Queued forced market exit wins over an otherwise profitable target gap.
    force = np.zeros(3, dtype=np.bool_)
    force[1] = True
    raw = _walk_fixed_arrays(np.array([100., 150., 150.]), np.array([101., 160., 160.]),
        np.array([99., 140., 140.]), np.array([100., 150., 150.]), np.ones(3, dtype=np.bool_),
        force, 0, 100., 1, 0, True)
    assert raw[0] == 1 and raw[1] == 150. and raw[2] == 2 and raw[3] == 0
    return dict(regression_direct_checks=len(range(575, len(close), 47)),
        regression_max_slope_error=max_slope, regression_max_r2_error=max_r2,
        regression_tolerance_at_1e8=1e-6, constant_window=True,
        low_before_entry_excluded=True, target_before_later_stop=True,
        stop_after_entry_only=True, opening_gap_priority=True, target_trade_through=True,
        mirrored_entry_cursor=True, max3_actual_entries_per_day=True,
        one_entry_per_issued_chart_order=True, same_minute_boundary_extrema=True,
        queued_market_priority=True, historical_pause_metadata_only=True,
        no_market_cache_loaded=True)


def _save_full_model(g, prepared, model, pieces, out):
    """Combine disjoint chronological stages without replaying a return."""
    t = pd.concat([x.trades for x in pieces], ignore_index=True)
    t["trade_id"] = np.arange(len(t))
    if t.entry_flat.duplicated().any():
        raise ValueError("Duplicate source entry address")
    gaps = pd.concat([x.gaps for x in pieces], ignore_index=True)
    if len(gaps):
        ids = pd.Series(t.trade_id.to_numpy(), index=t.entry_flat)
        gaps["trade_id"] = gaps.trade_entry_flat.map(ids).to_numpy(int)
    opened = pieces[-1].open_positions.copy()
    if len(opened):
        records, _, _ = _gap_records(prepared, int(opened.entry_flat.iloc[0]),
                                     int(opened.last_observed_flat.iloc[0])+1, -1, model)
        gaps = pd.concat([gaps, pd.DataFrame(records, columns=GAP_COLUMNS)], ignore_index=True)
    a = _calendar(g, prepared, model)
    for part in pieces:
        for x in part.audit.itertuples():
            for field in ("orders_issued", "vault_updates", "orders_already_crossed_at_signal"):
                a.loc[int(x.gridrow), field] = getattr(x, field)
    for x in t.to_dict("records"):
        _apply_trade_audit(a, x)
    if len(opened):
        x = opened.iloc[0]
        er = int(x.entry_row)
        a.loc[er, "entries"] += 1
        if bool(x.opening_gap_entry):
            a.loc[er, "opening_gap_entries"] += 1
        a.loc[er:, "affected_by_unclosed_trade"] = True
        if int(x.unknown_held_minutes):
            a.loc[er:, "affected_by_unknown_held_gap"] = True
    _eligible(a, FIRST_DATE)
    t["account_eligible"] = t.day.map(a.set_index("gridrow").account_eligible).to_numpy(bool)
    frames = dict(trades=t, audit=a.loc[a.date >= FIRST_DATE].reset_index(drop=True),
                  events=pd.concat([x.events for x in pieces], ignore_index=True),
                  gaps=gaps, open_positions=opened)
    for key, frame in frames.items():
        frame.to_csv(out/f"{model}_{key}.csv", index=False)
    print(f"FULL {model}: closed={len(t)}, open={len(opened)}, eligible_days={int(frames['audit'].account_eligible.sum())}", flush=True)
    return frames


def run_cached(cache_path="scratch_data/g24.pkl", output_dir="analysis/outputs/codex_r2vault/replay",
               feature_cache="agents/codex/runtime/r2vault_features.pkl"):
    """Explicit a973f077/dab01a8-gated execution; design before recent, five models."""
    import hashlib
    import json
    import pickle
    import subprocess
    from pathlib import Path
    for commit, path in (("a973f077", "agents/codex/plans/r2vault.md"),
                         ("dab01a8", "agents/codex/inputs/r2vault/calendar_metadata.md")):
        subprocess.run(["git", "cat-file", "-e", f"{commit}:{path}"], check=True)
    checks = synthetic_checks()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    with Path(cache_path).open("rb") as f:
        g = pickle.load(f)
    states, results = {}, {model: [] for model in MODELS}
    manifest = dict(preregistration_commit="a973f077", calendar_clarification_commit="dab01a8",
                    return_models=5, models=list(MODELS), checks=checks,
                    phase_order=["2018_22", "2023_plus"], no_selection=True,
                    feature_cache=str(feature_cache), model_files={})
    for period, start, cutoff in (("2018_22", "2018-01-01", "2022-12-31"),
                                  ("2023_plus", "2023-01-01", None)):
        p = prepare(g, cutoff)
        if cutoff is None:
            target = Path(feature_cache)
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("wb") as f:
                pickle.dump(p, f, protocol=4)
            np.save(out/"known_closed.npy", p.known_closed)
            p.bars.groupby(["date", "gridrow"], as_index=False).agg(
                chart_bars=("bar_index", "size"), low_r2_bars=("r2", lambda a: int((a <= .030).sum())),
                positive_slope_bars=("slope", lambda a: int((a > 0).sum()))).to_csv(out/"source_features_daily.csv", index=False)
        for model in MODELS:
            r = replay(g, model, cutoff, start_date=start, prepared=p, initial_state=states.get(model))
            states[model] = r.state
            results[model].append(r)
            for key in ("trades", "audit", "events", "gaps", "open_positions"):
                getattr(r, key).to_csv(out/f"{model}_{period}_{key}.csv", index=False)
            print(f"{period} {model}: closed={len(r.trades)}, open={len(r.open_positions)}", flush=True)
            if cutoff is None:
                frames = _save_full_model(g, p, model, results[model], out)
                manifest["model_files"][model] = {key: dict(rows=len(frame),
                    sha256=hashlib.sha256((out/f"{model}_{key}.csv").read_bytes()).hexdigest())
                    for key, frame in frames.items()}
    def file_sha(path):
        h = hashlib.sha256()
        with Path(path).open("rb") as f:
            for block in iter(lambda: f.read(1024*1024), b""):
                h.update(block)
        return h.hexdigest()
    manifest["source_inputs"] = {str(cache_path): file_sha(cache_path),
        "agents/codex/inputs/r2vault/source.pdf": file_sha("agents/codex/inputs/r2vault/source.pdf"),
        "agents/codex/inputs/r2vault/calendar_metadata.md": file_sha("agents/codex/inputs/r2vault/calendar_metadata.md")}
    manifest["scripts"] = {name: file_sha(Path(__file__).parent/name)
                           for name in (Path(__file__).name, "codex_anson_replay.py", "grid24.py", "replica.py")}
    manifest["known_closed_sha256"] = file_sha(out/"known_closed.npy")
    manifest["specs"] = {m: frozen_spec(m) for m in MODELS}
    (out/"replay_manifest.json").write_text(json.dumps(manifest, indent=2, default=str)+"\n", encoding="utf-8")
    return manifest
