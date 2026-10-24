"""Frozen ORPullback replay extension for Grid24; no file loading or CLI.

The rule is the supplied ORPullback.txt with PriceScaled=False. Both immutable
timing modes use an account adapter: flatten at 11:30 CT on replica.is_early_close
dates, prohibit entries at/after that early flatten, and otherwise flatten 14:55.
The adapter changes the source's holiday behavior; it is not a live source fix.

Reuse Grid24.bars(5), grid24.jof, grid.FILL_THROUGH, and the repository calendar.
grid.execute cannot express close entries, consumed-before-guards state, or the
two protection delays; grid._walk also uses a different same-minute tie rule.
This module therefore extends execution without replacing grid or building data.

All prices and gross_points are raw geometry. Fees/slippage/money sizing belong
to the caller. In particular, the entry minute's OHLC predates its close entry:
the first held minute is entry_j + 1, not entry_j.
"""
from dataclasses import dataclass
from typing import Iterable, Optional
import warnings

import numpy as np
import pandas as pd

from grid import FILL_THROUGH, POINT_VALUE
from grid24 import Grid24, jof
from replica import is_early_close


TIMING_MODES = ("reported_rule", "literal_mc_delay")
PROTECTION_DELAYS = {"reported_rule": 1, "literal_mc_delay": 6}
STOP_POINTS = 50.0
TARGET_POINTS = 100.0
MAX_TRADES = 2
MAX_LOSSES = 2
RTH_FIRST_J = int(jof(831))
OR_END_J = int(jof(845))
REGULAR_LAST_ENTRY_J = int(jof(1430))
REGULAR_FLAT_J = int(jof(1455))
EARLY_FLAT_J = int(jof(1130))

LEDGER_COLUMNS = [
    "date", "gridrow", "day", "side", "entry_j", "exit_j", "j0", "j1",
    "entry", "exit", "kind", "kind_label", "gross_points", "gross_nq",
    "stop_px", "target_px", "entry_phase", "exit_phase", "path_start_j",
    "protection_start_j", "timing_mode", "early_close_adapter", "flat_j",
    "mae_points_conservative",
]
EVENT_COLUMNS = ["date", "gridrow", "signal_j", "side", "outcome"]


@dataclass
class ReplayResult:
    trades: pd.DataFrame
    audit: pd.DataFrame
    spec: dict
    events: pd.DataFrame


def frozen_spec(timing):
    """Metadata for one predeclared timing mode; no parameter selection."""
    if timing not in TIMING_MODES:
        raise ValueError("timing must be one of %r" % (TIMING_MODES,))
    return dict(
        rule="ORPullback supplied source, PriceScaled=False",
        timing_mode=timing,
        protection_delay_minutes=PROTECTION_DELAYS[timing],
        entry_phase="close", stop_points=STOP_POINTS,
        target_points=TARGET_POINTS, max_trades=MAX_TRADES,
        max_losses=MAX_LOSSES, loss_counter="gross_points < 0",
        target_fill_through_points=float(FILL_THROUGH),
        target_fill_price="target level or better favorable minute open",
        stop_gap_price="adverse minute open, including first protected minute",
        same_minute_stop_target="stop first",
        regular_last_entry_j=REGULAR_LAST_ENTRY_J,
        regular_flat_j=REGULAR_FLAT_J, early_flat_j=EARLY_FLAT_J,
        early_entry_cutoff="strictly before early_flat_j",
        early_calendar="replica.is_early_close",
        account_adapter="early 11:30 CT flatten in both timing modes",
        missing_policy="exclude session before signals unless all OHLC minutes "
                       "08:31..scheduled_flat are finite; no backdated fills",
        costs="not applied; raw close-entry geometry only",
        price_scaled=False,
        path_note="entry-minute OHLC is excluded; first held minute entry_j+1",
    )


def _selected_rows(g, rows):
    selected = np.asarray(list(g.trading if rows is None else rows), dtype=int)
    if selected.ndim != 1 or len(np.unique(selected)) != len(selected):
        raise ValueError("rows must be distinct Grid24 row indices")
    if np.any(selected < 0) or np.any(selected >= g.D):
        raise ValueError("row outside Grid24")
    return np.sort(selected)


def minute_exit(open_, high, low, side, stop_px, target_px):
    """Frozen protected-minute exit; None or (price, kind, phase, both, gap).

    This small geometry helper is also available to frozen-event diagnostics.
    The preregistered conservative stop-first tie overrides a target/stop
    collision within a minute; target gaps otherwise improve the limit fill.
    """
    stop_hit = low <= stop_px if side > 0 else high >= stop_px
    target_hit = (high >= target_px + FILL_THROUGH if side > 0
                  else low <= target_px - FILL_THROUGH)
    both = bool(stop_hit and target_hit)
    gap = open_ <= stop_px if side > 0 else open_ >= stop_px
    if gap:
        return float(open_), 0, "open", both, True
    if stop_hit:
        return float(stop_px), 0, "intrabar", both, False
    if target_hit:
        price = max(open_, target_px) if side > 0 else min(open_, target_px)
        phase = "open" if price != target_px else "intrabar"
        return float(price), 1, phase, False, False
    return None


def walk_event(g, row, entry_j, side, timing="reported_rule"):
    """Raw fixed-event exit for diagnostics, bypassing trigger-selection gates.

    Caller enforces one-position collisions and the predeclared placebo schedule.
    The row must already pass replay's full-session completeness audit. No source
    parameters, price scaling, fees or account selection are changed here.
    """
    spec = frozen_spec(timing)
    row, entry_j, side = int(row), int(entry_j), int(side)
    if side not in (-1, 1) or entry_j % 5:
        raise ValueError("event requires side +/-1 and a five-minute close")
    date = pd.Timestamp(g.ts[row])
    early = bool(is_early_close(date))
    flat_j = EARLY_FLAT_J if early else REGULAR_FLAT_J
    if entry_j <= OR_END_J or entry_j >= flat_j:
        raise ValueError("event must follow the OR and precede account flatten")
    entry = float(g.c[row, entry_j])
    stop, target = entry-side*STOP_POINTS, entry+side*TARGET_POINTS
    protected_from = entry_j + spec["protection_delay_minutes"]
    mae = 0.0
    outcome = None
    for minute in range(entry_j + 1, flat_j + 1):
        oo, hh, ll = (float(getattr(g, f)[row, minute]) for f in ("o", "h", "l"))
        if not np.isfinite([oo, hh, ll, g.c[row, minute]]).all():
            raise ValueError("walk_event requires a pre-audited complete session")
        if minute >= protected_from:
            outcome = minute_exit(oo, hh, ll, side, stop, target)
        if outcome is not None:
            price, kind, phase, _, _ = outcome
            adverse_price = price if kind == 0 or phase == "open" else (ll if side > 0 else hh)
            mae = max(mae, (entry-adverse_price)*side)
            break
        mae = max(mae, (entry-(ll if side > 0 else hh))*side)
    else:
        minute, price, kind, phase = flat_j, float(g.c[row, flat_j]), 2, "close"
    points = (price-entry)*side
    return dict(
        date=date, gridrow=row, day=row, side=side, entry_j=entry_j,
        exit_j=minute, j0=entry_j, j1=minute, entry=entry, exit=price,
        kind=kind, kind_label=("stop", "target", "time")[kind],
        gross_points=points, gross_nq=points*POINT_VALUE,
        stop_px=stop, target_px=target, entry_phase="close", exit_phase=phase,
        path_start_j=entry_j+1, protection_start_j=protected_from,
        timing_mode=timing, early_close_adapter=early, flat_j=flat_j,
        mae_points_conservative=mae,
    )


def replay(g, timing="reported_rule", rows: Optional[Iterable[int]] = None):
    """Replay selected existing Grid24 rows, returning ledgers and data audits.

    This function does not instantiate Grid24 or rebuild caches. Incomplete
    sessions are explicitly excluded rather than interpreted as zero-signal
    days. The caller must preserve that distinction in reports/account inputs.
    Trading comparisons must not select a timing mode after inspecting returns.
    """
    spec = frozen_spec(timing)
    selected = _selected_rows(g, rows)
    for field in ("o", "h", "l", "c"):
        if np.shape(getattr(g, field)) != (g.D, 1440):
            raise ValueError("Grid24 OHLC arrays must have shape (D, 1440)")
    # Grid24.bars intentionally has empty overnight/weekend slices. Suppress
    # only its expected nan-reduction warning, not data-integrity errors.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="All-NaN slice encountered")
        bars = g.bars(5)
    if not np.array_equal(bars["j"], np.arange(0, 1440, 5)):
        raise ValueError("five-minute bars must be midnight-aligned close stamps")

    trades, audits, events = [], [], []
    for row in selected:
        row = int(row)
        date = pd.Timestamp(g.ts[row])
        early = bool(is_early_close(date))
        flat_j = EARLY_FLAT_J if early else REGULAR_FLAT_J
        required = slice(RTH_FIRST_J, flat_j + 1)
        complete = np.ones(flat_j - RTH_FIRST_J + 1, dtype=bool)
        missing_by_field = {}
        for field in ("o", "h", "l", "c"):
            good = np.isfinite(getattr(g, field)[row, required])
            missing_by_field["missing_" + field] = int((~good).sum())
            complete &= good
        diag = dict(
            date=date, gridrow=row, timing_mode=timing,
            early_close_adapter=early, scheduled_flat_j=flat_j,
            required_minutes=len(complete), missing_minutes=int((~complete).sum()),
            missing_or_minutes=int((~complete[:OR_END_J-RTH_FIRST_J+1]).sum()),
            status="eligible" if complete.all() else "excluded_incomplete_session",
            triggers=0, entries=0, blocked_position=0, blocked_time=0,
            blocked_trade_cap=0, blocked_loss_cap=0,
            stop_exits=0, target_exits=0, time_exits=0,
            same_minute_double_hits=0, gap_stop_exits=0,
            unprotected_minutes=0, unprotected_stop_crosses=0,
            unprotected_target_crosses=0, losses=0, **missing_by_field,
        )
        if not complete.all():
            audits.append(diag)
            continue
        day_trades, day_events = _replay_day(g, bars, row, date, flat_j, early,
                                             timing, diag)
        trades.extend(day_trades)
        events.extend(day_events)
        audits.append(diag)
    return ReplayResult(
        trades=pd.DataFrame(trades, columns=LEDGER_COLUMNS),
        audit=pd.DataFrame(audits), spec=spec,
        events=pd.DataFrame(events, columns=EVENT_COLUMNS),
    )


def _replay_day(g, bars, row, date, flat_j, early, timing, diag):
    """Chronological raw-price replay of one pre-audited complete session."""
    or_high = float(np.max(g.h[row, RTH_FIRST_J:OR_END_J + 1]))
    or_low = float(np.min(g.l[row, RTH_FIRST_J:OR_END_J + 1]))
    armed_l = armed_s = done_l = done_s = False
    entries = losses = 0
    pos = None
    out, events = [], []

    def finish(minute, price, kind, phase):
        nonlocal pos, losses
        points = (price - pos["entry"]) * pos["side"]
        out.append(dict(
            date=date, gridrow=row, day=row, side=pos["side"],
            entry_j=pos["entry_j"], exit_j=int(minute),
            j0=pos["entry_j"], j1=int(minute), entry=pos["entry"],
            exit=float(price), kind=int(kind),
            kind_label=("stop", "target", "time")[kind],
            gross_points=float(points), gross_nq=float(points * POINT_VALUE),
            stop_px=pos["stop"], target_px=pos["target"],
            entry_phase="close", exit_phase=phase,
            path_start_j=pos["entry_j"] + 1,
            protection_start_j=pos["protection_start_j"],
            timing_mode=timing, early_close_adapter=early, flat_j=flat_j,
            mae_points_conservative=float(pos["mae"]),
        ))
        losses += int(points < 0)
        diag[("stop_exits", "target_exits", "time_exits")[kind]] += 1
        pos = None

    for minute in range(OR_END_J + 1, flat_j + 1):
        oo = float(g.o[row, minute])
        hh = float(g.h[row, minute])
        ll = float(g.l[row, minute])
        cc = float(g.c[row, minute])
        if pos is not None:
            side = pos["side"]
            stop_hit = ll <= pos["stop"] if side > 0 else hh >= pos["stop"]
            target_hit = (hh >= pos["target"] + FILL_THROUGH if side > 0
                          else ll <= pos["target"] - FILL_THROUGH)
            protected = minute >= pos["protection_start_j"]
            if protected:
                outcome = minute_exit(oo, hh, ll, side, pos["stop"], pos["target"])
                if outcome is not None:
                    price, kind, phase, both, gap_stop = outcome
                    diag["same_minute_double_hits"] += int(both)
                    diag["gap_stop_exits"] += int(gap_stop)
                    adverse_price = price if kind == 0 or phase == "open" else (ll if side > 0 else hh)
                    adverse = (pos["entry"] - adverse_price) * side
                    pos["mae"] = max(pos["mae"], adverse)
                    finish(minute, price, kind, phase)
            else:
                diag["unprotected_minutes"] += 1
                diag["unprotected_stop_crosses"] += int(stop_hit)
                diag["unprotected_target_crosses"] += int(target_hit)
            if pos is not None:
                adverse = (pos["entry"] - (ll if side > 0 else hh)) * side
                pos["mae"] = max(pos["mae"], adverse)
                if minute == flat_j:
                    finish(minute, cc, 2, "close")

        if minute % 5:
            continue
        idx = minute // 5
        close = float(bars["c"][row, idx])
        open_ = float(bars["o"][row, idx])
        side = 0
        # Consume the first qualifying trigger before position/time/day guards.
        if armed_l and not done_l and close < open_ and close > or_high:
            side, done_l = 1, True
        elif armed_s and not done_s and close > open_ and close < or_low:
            side, done_s = -1, True
        # Arming occurs after triggering, and does not reset on a range recross.
        if close > or_high:
            armed_l = True
        if close < or_low:
            armed_s = True
        if not side:
            continue
        diag["triggers"] += 1
        time_ok = (minute < flat_j if early
                   else minute <= REGULAR_LAST_ENTRY_J)
        reason = ("blocked_position" if pos is not None else
                  "blocked_time" if not time_ok else
                  "blocked_trade_cap" if entries >= MAX_TRADES else
                  "blocked_loss_cap" if losses >= MAX_LOSSES else "entered")
        events.append(dict(date=date, gridrow=row, signal_j=minute,
                           side=side, outcome=reason))
        if reason != "entered":
            diag[reason] += 1
            continue
        entries += 1
        diag["entries"] += 1
        pos = dict(side=side, entry=close, entry_j=minute,
                   stop=close-side*STOP_POINTS,
                   target=close+side*TARGET_POINTS,
                   protection_start_j=minute+PROTECTION_DELAYS[timing], mae=0.0)
    if pos is not None:
        raise AssertionError("complete session ended without account-adapter flat")
    diag["losses"] = losses
    return out, events


def synthetic_checks():
    """Temporal/guard checks on invented prices only; never loads market data."""
    class ToyGrid:
        bars = Grid24.bars

        def __init__(self, date="2026-10-20"):
            self.D = 1
            self.ts = np.array([np.datetime64(date)])
            self.trading = np.array([0])
            self.o = np.full((1, 1440), 100.0)
            self.h = np.full((1, 1440), 101.0)
            self.l = np.full((1, 1440), 99.0)
            self.c = np.full((1, 1440), 100.0)
            self.v = np.ones((1, 1440))

        def bar(self, close_j, open_, close, high, low):
            sl = slice(close_j - 4, close_j + 1)
            self.o[0, sl] = open_
            self.c[0, sl] = close
            self.h[0, sl] = high
            self.l[0, sl] = low

    def first_long(date="2026-10-20"):
        toy = ToyGrid(date)
        toy.bar(int(jof(850)), 100.0, 103.0, 104.0, 100.0)
        toy.bar(int(jof(855)), 103.0, 102.0, 104.0, 101.5)
        return toy

    toy = first_long()
    toy.l[0, int(jof(856))] = 40.0
    toy.o[0, int(jof(901))] = 40.0
    toy.l[0, int(jof(901))] = 40.0
    reported = replay(toy, "reported_rule")
    literal = replay(toy, "literal_mc_delay")
    assert len(reported.trades) == len(literal.trades) == 1
    assert reported.trades.iloc[0].entry_j == int(jof(855))
    assert reported.trades.iloc[0].exit_j == int(jof(856))
    assert reported.trades.iloc[0]["exit"] == 52.0
    assert literal.trades.iloc[0].protection_start_j == int(jof(901))
    assert literal.trades.iloc[0]["exit"] == 40.0
    assert literal.trades.iloc[0].exit_phase == "open"
    assert literal.audit.iloc[0].unprotected_minutes == 5

    toy = first_long()
    toy.h[0, int(jof(856))] = 203.0
    toy.l[0, int(jof(856))] = 52.0
    both = replay(toy)
    assert both.trades.iloc[0].kind == 0
    assert both.audit.iloc[0].same_minute_double_hits == 1

    toy = first_long()
    toy.o[0, int(jof(856))] = 205.0
    toy.h[0, int(jof(856))] = 206.0
    toy.l[0, int(jof(856))] = 204.0
    toy.c[0, int(jof(856))] = 205.0
    gap_target = replay(toy)
    assert gap_target.trades.iloc[0]["exit"] == 205.0
    assert gap_target.trades.iloc[0].kind == 1
    walked = walk_event(toy, 0, int(jof(855)), 1)
    assert walked["exit"] == 205.0 and walked["kind"] == 1

    toy = first_long()
    toy.bar(int(jof(905)), 100.0, 97.0, 101.0, 96.0)
    toy.bar(int(jof(910)), 97.0, 98.0, 98.5, 96.0)
    toy.h[0, int(jof(911))] = 203.0
    toy.bar(int(jof(915)), 97.0, 98.0, 98.5, 96.0)
    consumed = replay(toy)
    assert len(consumed.trades) == 1
    assert ((consumed.events.side == -1)
            & (consumed.events.outcome == "blocked_position")).sum() == 1

    early = replay(first_long("2026-11-27"))
    assert early.trades.iloc[0].exit_j == EARLY_FLAT_J
    assert early.trades.iloc[0].kind == 2
    assert early.trades.iloc[0].early_close_adapter

    toy = first_long()
    toy.c[0, int(jof(1101))] = np.nan
    missing = replay(toy)
    assert missing.trades.empty and missing.events.empty
    assert missing.audit.iloc[0].status == "excluded_incomplete_session"
    assert missing.audit.iloc[0].missing_minutes == 1
    return dict(
        invented_prices_only=True, market_data_loaded=False,
        protection_timing_and_gap_stop="pass", stop_first_tie="pass",
        favorable_target_gap_and_event_walker="pass",
        blocked_trigger_consumes_side="pass", early_flat_adapter="pass",
        missing_day_exclusion="pass",
    )


def run_cached(cache_path="scratch_data/g24.pkl",
               output_dir="analysis/outputs/codex_or_pullback_portfolio/replay"):
    """Explicit frozen run: design first, then 2023+ once, without a new cache.

    Call only after the research preregistration is committed. There is no CLI
    or import-time price loading. Full ledgers below are concatenations of the
    two period runs, not another strategy-return execution.
    """
    import hashlib
    import json
    import pickle
    from pathlib import Path

    checks = synthetic_checks()
    with open(cache_path, "rb") as handle:
        g = pickle.load(handle)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    years = pd.DatetimeIndex(g.ts).year.to_numpy()
    all_rows = np.asarray(g.trading, dtype=int)
    periods = (
        ("design", all_rows[(years[all_rows] >= 2018) & (years[all_rows] <= 2022)]),
        ("recent", all_rows[years[all_rows] >= 2023]),
    )
    pieces = {mode: [] for mode in TIMING_MODES}
    manifest = dict(
        preregistration_commit="1ad4306", cache_path=str(cache_path),
        replay_module_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        cache_first_date=str(pd.Timestamp(g.ts[0]).date()),
        cache_last_date=str(pd.Timestamp(g.ts[-1]).date()),
        calendar_rows=int(g.D), trading_rows=int(len(g.trading)),
        execution_order=[], synthetic_checks=checks, timing_specs={},
        new_candidate_variants=2,
    )
    for period, rows in periods:
        for mode in TIMING_MODES:
            result = replay(g, timing=mode, rows=rows)
            for label, frame in (("trades", result.trades), ("audit", result.audit),
                                 ("events", result.events)):
                frame.to_csv(output / (mode + "_" + period + "_" + label + ".csv"), index=False)
            pieces[mode].append(result)
            record = dict(
                period=period, timing_mode=mode, requested_days=int(len(rows)),
                eligible_days=int((result.audit.status == "eligible").sum()),
                incomplete_days=int((result.audit.status != "eligible").sum()),
                trades=int(len(result.trades)),
            )
            manifest["execution_order"].append(record)
            manifest["timing_specs"][mode] = result.spec
            print(json.dumps(record), flush=True)
    for mode in TIMING_MODES:
        for label in ("trades", "audit", "events"):
            combined = pd.concat([getattr(piece, label) for piece in pieces[mode]],
                                 ignore_index=True)
            combined.to_csv(output / (mode + "_" + label + ".csv"), index=False)
    (output / "replay_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
