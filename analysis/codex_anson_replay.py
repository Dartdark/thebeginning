"""Frozen Anson intraday-momentum replay extension; no import-time IO.

The user pins NQ, five-minute Default/Globex observed bars, CT and IOG off.
User-intended inputs 4.5/20 supersede the uploaded defaults 3/6. The latter is
a standalone diagnostic, never selected into an account after seeing returns.

Reuse Grid24.bars(5). grid.execute cannot express the source's observed-bar
holding counter, next-chart-bar-open exits, full chronological chart history,
and raw cross-date holds. This extension does not replace or rebuild a grid.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from replica import is_early_close


BAR_MINUTES = 5
LOOKBACK = 12
RANGE_LOOKBACK = 20
MAX_BARS_BACK = 20
START_J, LAST_ENTRY_J, FLAT_SIGNAL_J = 510, 870, 895
EARLY_FLAT_J = 690
FIRST_RETURN_DATE = pd.Timestamp("2018-01-01")
MODELS = {
    "intended_raw": dict(threshold=4.5, hold_bars=20, early_adapter=False),
    "intended_apex": dict(threshold=4.5, hold_bars=20, early_adapter=True),
    "defaults_raw": dict(threshold=3.0, hold_bars=6, early_adapter=False),
}
TRADE_COLUMNS = [
    "model", "trade_id", "date", "gridrow", "day", "side", "signal_date", "signal_row", "signal_j",
    "signal_bar_index", "entry_bar_index", "exit_signal_bar_index", "exit_bar_index",
    "entry_date", "exit_date", "entry_row", "exit_row", "entry_j", "exit_j", "j0", "j1",
    "entry_flat", "exit_flat", "entry_phase", "exit_phase", "path_start_flat", "path_end_flat_exclusive",
    "entry", "exit", "kind", "kind_label", "gross_points", "gross_nq", "qty",
    "bars_held", "threshold", "momentum", "average_range", "strength",
    "entry_fill_lag_minutes", "exit_fill_lag_minutes", "cross_date", "late_after_1559",
    "missing_held_minutes", "known_closure_missing_minutes", "unknown_held_minutes",
    "mae_points_observed", "early_adapter_exit", "account_eligible",
]


@dataclass
class PreparedBars:
    bars: pd.DataFrame
    observed_minutes: np.ndarray
    known_closed: np.ndarray
    cutoff_row: int


@dataclass
class ReplayResult:
    trades: pd.DataFrame
    audit: pd.DataFrame
    features: pd.DataFrame
    events: pd.DataFrame
    gaps: pd.DataFrame
    spec: dict


def frozen_spec(model):
    if model not in MODELS:
        raise ValueError(f"Unknown preregistered return model: {model}")
    return dict(
        model=model, **MODELS[model], instrument="NQ raw geometry / MNQ monetary scaling by caller",
        timezone="Central", bar_minutes=BAR_MINUTES, session="Default/Globex proxy from observed Grid24 bars",
        iog=False, lookback_bars=LOOKBACK, range_lookback_bars=RANGE_LOOKBACK,
        denominator="mean High-Low of preceding 20 observed chart bars, excluding current",
        momentum="current chart close minus chart close 12 observed bars ago",
        current_bar_guard="observed index + 1 - assumed MaxBarsBack20 > 20; all pre-start history retained",
        entry="signal close 08:30..14:30 inclusive, next observed chart-bar open",
        hold="entry chart bar counts as completed held bar1; queue exit when held count reaches HoldBars",
        ordinary_flat="queue market exit on chart close>=14:55; next observed chart open, wall14:55 when contiguous",
        early_policy="repository early-close dates: no entry signals at/after11:30; queue exit at11:30"
                     if MODELS[model]["early_adapter"] else "raw source; no early-close intervention",
        stop=False, target=False, costs="raw geometry only; caller charges two market fill slips and round-trip fee",
        quantity="one raw NQ unit; account quantities applied externally",
        source_state="whole observed chart chronology before eligibility filtering; no date reset",
        coverage="Apex requires finite OHLC08:26..14:56 regular /08:26..11:31 early, plus known timely fills",
        gap_policy="retain raw known exits; audit missing held spans; never invent an exit or fill an absent bar",
        known_closure_proxy="daily16:01..17:00; weekendFri16:01..Sun17:00; repo early dates12:01..17:00",
        closure_caveat="early NQ closing clock is an explicit proxy, not independently verified calendar parity",
    )


def _cutoff_row(g, cutoff_date):
    if cutoff_date is None:
        return len(g.ts)-1
    return int(np.searchsorted(pd.DatetimeIndex(g.ts).values,
                               np.datetime64(pd.Timestamp(cutoff_date).normalize()), side="right")-1)


def _closed_proxy(g, last_row):
    """Known-closure proxy for audit labels only; never removes a source bar."""
    result = np.zeros((last_row+1, 1440), dtype=bool)
    for d, stamp in enumerate(pd.DatetimeIndex(g.ts[:last_row+1])):
        result[d, 961:1021] = True
        if stamp.weekday() == 4:
            result[d, 961:] = True
        elif stamp.weekday() == 5:
            result[d] = True
        elif stamp.weekday() == 6:
            result[d, :1021] = True
        if is_early_close(stamp):
            result[d, 721:1021] = True
    return result


def prepare_bars(g, cutoff_date=None):
    """Build observed five-minute bars and prior-only features without returns.

    Midnight bars include their preceding four minutes through Grid24.bars.
    Completely absent chart bars are skipped, preserving source bar indexing.
    Partial chart bars remain observed and their coverage is audited separately.
    """
    last_row = _cutoff_row(g, cutoff_date)
    if last_row < 0:
        raise ValueError("Cutoff precedes the cached grid")
    if g.o.shape[1] != 1440:
        raise ValueError("Replay requires Grid24")
    observed = np.logical_and.reduce([np.isfinite(getattr(g, f)[:last_row+1]) for f in ("o", "h", "l", "c")])
    b = g.bars(BAR_MINUTES)
    valid = np.logical_and.reduce([np.isfinite(b[f][:last_row+1]) for f in ("o", "h", "l", "c")])
    ds, ks = np.nonzero(valid)
    stamps = ds*1440+b["j"][ks]
    obs_flat = observed.ravel()
    first = np.empty(len(stamps), dtype=np.int64)
    count = np.empty(len(stamps), dtype=np.int64)
    for i, close in enumerate(stamps):
        lo = max(0, int(close)-BAR_MINUTES+1)
        seen = np.flatnonzero(obs_flat[lo:int(close)+1])+lo
        if not len(seen):
            raise ValueError("Aggregated chart bar has no complete observed OHLC minute")
        first[i], count[i] = int(seen[0]), len(seen)
    np.testing.assert_allclose(b["o"][ds, ks], g.o.ravel()[first], rtol=0, atol=1e-10,
                               err_msg="A chart open must be an observed complete minute open")
    frame = pd.DataFrame(dict(bar_index=np.arange(len(stamps)), gridrow=ds,
                              date=pd.DatetimeIndex(g.ts[ds]), bar_j=b["j"][ks],
                              close_flat=stamps.astype(np.int64), open_flat=first,
                              observed_minute_count=count,
                              **{f: b[f][ds, ks] for f in ("o", "h", "l", "c")}))
    close = frame.c.to_numpy(float)
    ranges = (frame.h-frame.l).to_numpy(float)
    momentum, avg = np.full(len(frame), np.nan), np.full(len(frame), np.nan)
    momentum[LOOKBACK:] = close[LOOKBACK:]-close[:-LOOKBACK]
    sums = np.r_[0., np.cumsum(ranges)]
    avg[RANGE_LOOKBACK:] = (sums[RANGE_LOOKBACK:-1]-sums[:-RANGE_LOOKBACK-1])/RANGE_LOOKBACK
    strength = np.divide(np.abs(momentum), avg, out=np.zeros(len(frame)), where=avg > 0)
    frame["momentum"], frame["average_range"], frame["strength"] = momentum, avg, strength
    frame["history_ready"] = (frame.bar_index+1-MAX_BARS_BACK) > max(LOOKBACK, RANGE_LOOKBACK)
    frame["early_close_proxy"] = [is_early_close(x) for x in frame.date]
    return PreparedBars(frame, observed, _closed_proxy(g, last_row), last_row)


def _calendar(g, prepared):
    trading = set(int(d) for d in g.trading)
    rows = []
    for d, date in enumerate(pd.DatetimeIndex(g.ts[:prepared.cutoff_row+1])):
        early = bool(is_early_close(date))
        stop = 692 if early else 897  # inclusive11:31/14:56, Python upper exclusive
        core = prepared.observed_minutes[d, 506:stop]
        regular = prepared.observed_minutes[d, 506:897]
        rows.append(dict(date=date, gridrow=d, is_trading_row=d in trading,
                         early_close_proxy=early, apex_window_first_j=506, apex_window_last_j=stop-1,
                         apex_window_complete=bool(core.all()), missing_apex_window_minutes=int((~core).sum()),
                         regular_window_complete=bool(regular.all()),
                         source_trades_entered=0, source_trades_exited=0,
                         affected_by_unknown_held_gap=False, affected_by_cross_date_trade=False,
                         affected_by_delayed_entry=False, affected_by_delayed_exit=False,
                         affected_by_unclosed_trade=False, affected_by_late_position=False,
                         account_eligible=False))
    return pd.DataFrame(rows)


def _gap_records(prepared, first, end, trade_id, model):
    missing = np.flatnonzero(~prepared.observed_minutes.ravel()[first:end])+first
    if not len(missing):
        return [], 0, 0
    labels = prepared.known_closed.ravel()[missing]
    split = np.r_[True, (np.diff(missing) > 1) | (np.diff(labels.astype(int)) != 0)]
    starts = np.flatnonzero(split)
    ends = np.r_[starts[1:], len(missing)]
    records = [dict(model=model, trade_id=trade_id, first_flat=int(missing[a]),
                    last_flat=int(missing[b-1]), minutes=int(b-a),
                    trade_entry_flat=int(first), trade_exit_flat=int(end),
                    classification="known_closure_proxy" if labels[a] else "unknown_observation_gap")
               for a, b in zip(starts, ends)]
    return records, int(labels.sum()), int((~labels).sum())


def _finish(g, prepared, position, exit_bar, label, bars_held, model, audit, trades, gaps):
    enter = position["entry_bar"]
    entry_flat, exit_flat = int(enter.open_flat), int(exit_bar.open_flat)
    er, ej = divmod(entry_flat, 1440)
    xr, xj = divmod(exit_flat, 1440)
    sign, signal = position["side"], position["signal_bar"]
    entry_lag = entry_flat-int(signal.close_flat)-1
    exit_lag = exit_flat-int(position["exit_signal_bar"].close_flat)-1
    if exit_flat <= entry_flat:
        raise ValueError("Source exit must follow its entry")
    recs, closed_missing, unknown_missing = _gap_records(prepared, entry_flat, exit_flat, len(trades), model)
    gaps.extend(recs)
    if audit is not None:
        audit.loc[er, "source_trades_entered"] += 1
        audit.loc[xr, "source_trades_exited"] += 1
        if unknown_missing:
            audit.loc[er:xr, "affected_by_unknown_held_gap"] = True
        if er != xr:
            audit.loc[er:xr, "affected_by_cross_date_trade"] = True
        if entry_lag:
            audit.loc[int(signal.gridrow):er, "affected_by_delayed_entry"] = True
        if exit_lag:
            audit.loc[int(position["exit_signal_bar"].gridrow):xr, "affected_by_delayed_exit"] = True
        if er != xr or xj > 960:  # open of16:00 close-stamped minute iswall15:59
            audit.loc[er:xr, "affected_by_late_position"] = True
    adverse = (g.l if sign > 0 else g.h).ravel()[entry_flat:exit_flat]
    finite = adverse[np.isfinite(adverse)]
    mae = max(0., float(np.max((float(enter.o)-finite)*sign))) if len(finite) else np.nan
    mae = max(mae, (float(enter.o)-float(exit_bar.o))*sign)
    points = (float(exit_bar.o)-float(enter.o))*sign
    spec = MODELS[model]
    trades.append(dict(model=model, trade_id=len(trades), date=pd.Timestamp(g.ts[er]), gridrow=er, day=er, side=sign,
                       signal_date=signal.date, signal_row=int(signal.gridrow), signal_j=int(signal.bar_j),
                       signal_bar_index=int(signal.bar_index), entry_bar_index=int(enter.bar_index),
                       exit_signal_bar_index=int(position["exit_signal_bar"].bar_index), exit_bar_index=int(exit_bar.bar_index),
                       entry_date=pd.Timestamp(g.ts[er]), exit_date=pd.Timestamp(g.ts[xr]),
                       entry_row=er, exit_row=xr, entry_j=ej, exit_j=xj, j0=ej, j1=xj,
                       entry_flat=entry_flat, exit_flat=exit_flat, entry_phase="open", exit_phase="open",
                       path_start_flat=entry_flat, path_end_flat_exclusive=exit_flat,
                       entry=float(enter.o), exit=float(exit_bar.o), kind=2, kind_label=label,
                       gross_points=points, gross_nq=points*20., qty=1., bars_held=bars_held,
                       threshold=spec["threshold"], momentum=float(signal.momentum),
                       average_range=float(signal.average_range), strength=float(signal.strength),
                       entry_fill_lag_minutes=entry_lag, exit_fill_lag_minutes=exit_lag,
                       cross_date=er != xr, late_after_1559=(er != xr or xj > 960),
                       missing_held_minutes=closed_missing+unknown_missing,
                       known_closure_missing_minutes=closed_missing, unknown_held_minutes=unknown_missing,
                       mae_points_observed=mae, early_adapter_exit="early" in label))


def replay(g, model="intended_raw", cutoff_date=None, *, start_date=FIRST_RETURN_DATE,
           prepared: Optional[PreparedBars] = None):
    """Source state first; calendar coverage is attached after all source trades."""
    spec = frozen_spec(model)
    cfg = MODELS[model]
    prepared = prepare_bars(g, cutoff_date) if prepared is None else prepared
    if prepared.cutoff_row != _cutoff_row(g, cutoff_date):
        raise ValueError("Prepared bars differ from requested cutoff")
    audit = _calendar(g, prepared)
    start = pd.Timestamp(start_date).normalize()
    position = pending_entry = pending_exit = None
    bars_held = 0
    events, trades, gaps = [], [], []
    for b in prepared.bars.itertuples(index=False):
        if b.date < start:
            continue
        if pending_exit is not None and position is not None:
            _finish(g, prepared, position, b, pending_exit, bars_held, model, audit, trades, gaps)
            position = pending_exit = None
            bars_held = 0
        if pending_entry is not None and position is None:
            position = dict(**pending_entry, entry_bar=b)
            pending_entry = None
            bars_held = 0
        if position is not None:
            bars_held += 1
        else:
            bars_held = 0
        early = cfg["early_adapter"] and bool(b.early_close_proxy)
        in_time = START_J <= b.bar_j <= LAST_ENTRY_J and (not early or b.bar_j < EARLY_FLAT_J)
        if position is None and b.history_ready and in_time and b.average_range > 0 and b.strength >= cfg["threshold"]:
            side = int(np.sign(b.momentum))
            if side:
                pending_entry = dict(side=side, signal_bar=b)
                events.append(dict(model=model, date=b.date, gridrow=int(b.gridrow), minute=int(b.bar_j),
                                   bar_index=int(b.bar_index), side=side, event="signal_entry"))
        if position is not None:
            held_exit = bars_held >= cfg["hold_bars"]
            early_exit = early and b.bar_j >= EARLY_FLAT_J
            normal_exit = b.bar_j >= FLAT_SIGNAL_J
            if held_exit or early_exit or normal_exit:
                # Holding exits occur first in the source when two identical
                # market exits are generated on one close. Preserve that label.
                pending_exit = "hold" if held_exit else "early_flat" if early_exit else "time_flat"
                if held_exit and (early_exit or normal_exit):
                    pending_exit += "+early_flat" if early_exit else "+time_flat"
                position["exit_signal_bar"] = b
    if position is not None:
        er = int(position["entry_bar"].open_flat)//1440
        audit.loc[er:, "affected_by_unclosed_trade"] = True
        events.append(dict(model=model, date=pd.Timestamp(g.ts[prepared.cutoff_row]),
                           gridrow=prepared.cutoff_row, minute=-1, bar_index=-1,
                           side=position["side"], event="unclosed_position_at_cutoff"))
    if pending_entry is not None:
        b = pending_entry["signal_bar"]
        events.append(dict(model=model, date=b.date, gridrow=int(b.gridrow), minute=int(b.bar_j),
                           bar_index=int(b.bar_index), side=pending_entry["side"], event="unfilled_entry_at_cutoff"))
    audit["model"] = model
    # This is Apex suitability, not a decision to discard raw personal returns.
    audit["account_eligible"] = (audit.is_trading_row & audit.apex_window_complete
                                 & ~audit.affected_by_unknown_held_gap & ~audit.affected_by_cross_date_trade
                                 & ~audit.affected_by_delayed_entry & ~audit.affected_by_delayed_exit
                                 & ~audit.affected_by_unclosed_trade & ~audit.affected_by_late_position
                                 & (audit.date >= start))
    audit["status"] = np.where(audit.account_eligible, "eligible", "excluded")
    t = pd.DataFrame(trades)
    if len(t):
        t["account_eligible"] = t.day.map(audit.set_index("gridrow").account_eligible).to_numpy(bool)
        t = t.reindex(columns=TRADE_COLUMNS)
    else:
        t = pd.DataFrame(columns=TRADE_COLUMNS)
    features = prepared.bars.loc[prepared.bars.date >= start].copy()
    features["model"] = model
    features["source_threshold_met"] = features.history_ready & (features.average_range > 0) & (features.strength >= cfg["threshold"])
    return ReplayResult(t, audit.loc[audit.date >= start].reset_index(drop=True), features,
                        pd.DataFrame(events, columns=["model", "date", "gridrow", "minute", "bar_index", "side", "event"]),
                        pd.DataFrame(gaps, columns=["model", "trade_id", "trade_entry_flat", "trade_exit_flat",
                                                   "first_flat", "last_flat", "minutes", "classification"]), spec)


def walk_event(g, prepared, entry_bar_index, side, model="intended_raw"):
    """Fixed-event exit geometry for predeclared diagnostics; no source signals.

    Caller supplies a source-information-safe observed entry bar. With no price
    stop/target the holding/time exit schedule is independent of side, but this
    helper still replays the exact bar clock and account adapter.
    """
    frozen_spec(model)
    cfg = MODELS[model]
    side, entry_bar_index = int(side), int(entry_bar_index)
    if side not in (-1, 1) or entry_bar_index < 1:
        raise ValueError("Fixed event requires side +/-1 and a preceding observed signal bar")
    bars = prepared.bars
    entry, signal = bars.iloc[entry_bar_index], bars.iloc[entry_bar_index-1]
    position = dict(side=side, entry_bar=entry, signal_bar=signal)
    held = 0
    pending = None
    out, gaps = [], []
    for b in bars.iloc[entry_bar_index:].itertuples(index=False):
        if pending is not None:
            _finish(g, prepared, position, b, pending, held, model, None, out, gaps)
            return out[0]
        held += 1
        early = cfg["early_adapter"] and b.early_close_proxy and b.bar_j >= EARLY_FLAT_J
        late = b.bar_j >= FLAT_SIGNAL_J
        if held >= cfg["hold_bars"] or early or late:
            pending = "hold" if held >= cfg["hold_bars"] else "early_flat" if early else "time_flat"
            if held >= cfg["hold_bars"] and (early or late):
                pending += "+early_flat" if early else "+time_flat"
            position["exit_signal_bar"] = b
    return None


def synthetic_checks():
    """Synthetic only: no cached prices, market files or strategy returns."""
    from grid24 import Grid24
    g = Grid24.__new__(Grid24)
    g.ts = pd.date_range("2018-01-01", periods=3, freq="D").to_numpy()
    g.D, g.trading = 3, np.arange(3)
    g.dates = pd.DatetimeIndex(g.ts).strftime("%Y%m%d").to_numpy(int)
    shape = (3, 1440)
    for f in ("o", "h", "l", "c", "v"):
        setattr(g, f, np.ones(shape)*100.)
    g.h += 1.
    g.l -= 1.
    # A monotone half-point-per-minute path gives 30 points/12 bars,
    # versus ~4-point prior average range: both fixed thresholds fire.
    prices = 100.+np.arange(3*1440).reshape(shape)*.5
    g.o, g.c = prices.copy(), prices+.25
    g.h, g.l = prices+1., prices-1.
    prepared = prepare_bars(g)
    a = replay(g, "intended_raw", prepared=prepared)
    b = replay(g, "defaults_raw", prepared=prepared)
    t = a.trades.iloc[0]
    assert t.entry_j == 511 and t.exit_j == 611 and t.bars_held == 20
    assert t.exit_signal_bar_index-t.entry_bar_index == 19
    assert b.trades.iloc[0].exit_j-b.trades.iloc[0].entry_j == 30
    assert b.trades.iloc[0].bars_held == 6
    # At least one whole chart bar remains flat after an open market exit.
    day = a.trades[a.trades.day == t.day]
    assert (day.entry_bar_index.to_numpy()[1:] > day.exit_bar_index.to_numpy()[:-1]).all()
    i = int(t.signal_bar_index)
    history = prepared.bars
    np.testing.assert_allclose(t.momentum, history.c.iloc[i]-history.c.iloc[i-12])
    np.testing.assert_allclose(t.average_range, (history.h-history.l).iloc[i-20:i].mean())
    for model, source in (("intended_raw", a), ("defaults_raw", b)):
        x = source.trades.iloc[0]
        fixed = walk_event(g, prepared, x.entry_bar_index, x.side, model)
        assert fixed["exit_flat"] == x.exit_flat and fixed["gross_points"] == x.gross_points
    # The ordinary14:55 close exit fills the 14:56 stamped minute open,
    # not the 15:00 chart close. The Jan1 calendar is an early-close proxy.
    assert ((a.trades.exit_j == 896) & a.trades.kind_label.str.contains("flat")).any()
    e = replay(g, "intended_apex", prepared=prepared)
    assert (e.trades[e.trades.day == 0].exit_j <= 691).all()
    assert (e.trades[e.trades.day == 0].signal_j < 690).all()
    # A missing early-close afternoon is not silently filled. Raw next-bar
    # orders can wait until the reopen, whereas the explicit adapter is flat.
    early = Grid24.__new__(Grid24)
    for name, value in vars(g).items():
        setattr(early, name, value.copy() if isinstance(value, np.ndarray) else value)
    for name in ("o", "h", "l", "c", "v"):
        getattr(early, name)[0, 721:1021] = np.nan
    ef = prepare_bars(early)
    raw = replay(early, "intended_raw", prepared=ef)
    adapted = replay(early, "intended_apex", prepared=ef)
    assert (raw.trades.entry_fill_lag_minutes > 0).any()
    assert raw.trades.late_after_1559.any()
    assert not adapted.trades.late_after_1559.any()
    assert (raw.trades.gross_points == (raw.trades.exit-raw.trades.entry)*raw.trades.side).all()
    return dict(user_intended_4_5_20=True, defaults_3_6_diagnostic=True,
                prior_only_range_denominator=True, six_completed_held_bars_not_seven=True,
                twenty_completed_held_bars=True, observed_next_chart_open=True,
                no_instant_reentry_after_exit=True, ordinary_flat_wall1455=True,
                explicit_early_adapter=True, fixed_event_walker_parity=True,
                raw_late_reopen_order_preserved=True,
                no_market_cache_loaded=True)


def run_cached(cache_path="scratch_data/g24.pkl", output_dir="analysis/outputs/codex_anson/replay",
               feature_cache="agents/codex/runtime/anson_bars.pkl"):
    """Explicit post-928c0ea runner: design first, recent once, no selection.

    Full observed chart features are kept in an ignored task cache. Committed
    daily feature summaries and signals are compact; no repeated per-bar CSV
    or market cache is created. Raw source trades are never filtered out here.
    """
    import hashlib
    import json
    import pickle
    import subprocess
    from pathlib import Path
    subprocess.run(["git", "cat-file", "-e", "928c0ea:agents/codex/plans/anson_momentum.md"], check=True)
    checks = synthetic_checks()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    with Path(cache_path).open("rb") as f:
        g = pickle.load(f)
    by_model = {model: [] for model in MODELS}
    feature_summary = []
    for period, start, cutoff in (("2018_22", "2018-01-01", "2022-12-31"),
                                  ("2023_plus", "2023-01-01", None)):
        prepared = prepare_bars(g, cutoff)
        for model in MODELS:
            result = replay(g, model, cutoff, start_date=start, prepared=prepared)
            for key in ("trades", "audit", "events", "gaps"):
                getattr(result, key).to_csv(out / f"{model}_{period}_{key}.csv", index=False)
            if result.events.event.eq("unclosed_position_at_cutoff").any():
                raise ValueError("Unclosed split/end position: retain state and audit before interpreting closed-trade results")
            daily = result.features.groupby(["date", "gridrow"], as_index=False).agg(
                observed_chart_bars=("bar_index", "size"),
                partial_chart_bars=("observed_minute_count", lambda a: int((a < BAR_MINUTES).sum())),
                history_ready_bars=("history_ready", "sum"),
                threshold_met_bars=("source_threshold_met", "sum"))
            daily["model"], daily["period"] = model, period
            feature_summary.append(daily)
            by_model[model].append(result)
            print(f"{period} {model}: closed_trades={len(result.trades)} "
                  f"apex_eligible_trades={int(result.trades.account_eligible.sum())} "
                  f"apex_eligible_days={int(result.audit.account_eligible.sum())} "
                  f"late_trades={int(result.trades.late_after_1559.sum())}", flush=True)
        if cutoff is None:
            target = Path(feature_cache)
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("wb") as f:
                pickle.dump(prepared, f, protocol=4)
    manifest = dict(preregistration_commit="928c0ea", return_models=3,
                    models=list(MODELS), synthetic_checks=checks,
                    period_order=["2018_22", "2023_plus"], no_parameter_selection=True,
                    feature_cache=str(feature_cache), no_rescue_fills=True,
                    ledger_files={}, specs={})
    for model, parts in by_model.items():
        for key in ("trades", "audit", "events", "gaps"):
            if key == "gaps":
                frames, offset = [], 0
                for part in parts:
                    fragment = part.gaps.copy()
                    fragment["trade_id"] += offset
                    frames.append(fragment)
                    offset += len(part.trades)
                frame = pd.concat(frames, ignore_index=True)
            else:
                frame = pd.concat([getattr(x, key) for x in parts], ignore_index=True)
            if key == "trades":
                frame["trade_id"] = np.arange(len(frame))
            path = out / f"{model}_{key}.csv"
            frame.to_csv(path, index=False)
            manifest["ledger_files"][path.name] = dict(rows=len(frame), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        manifest["specs"][model] = frozen_spec(model)
    pd.concat(feature_summary, ignore_index=True).to_csv(out / "source_features_daily.csv", index=False)
    def file_sha(path):
        h = hashlib.sha256()
        with Path(path).open("rb") as f:
            for block in iter(lambda: f.read(1024*1024), b""):
                h.update(block)
        return h.hexdigest()
    manifest["inputs"] = {str(cache_path): file_sha(cache_path),
                           **{f"agents/codex/inputs/anson_momentum/{name}": file_sha(f"agents/codex/inputs/anson_momentum/{name}")
                              for name in ("source.txt", "user_spec.md")}}
    manifest["script_sha256"] = file_sha(__file__)
    (out / "replay_manifest.json").write_text(json.dumps(manifest, indent=2, default=str)+"\n", encoding="utf-8")
    return manifest


def refresh_saved_gap_references(output_dir="analysis/outputs/codex_anson/replay"):
    """Metadata-only repair of split-local IDs; never reads prices or returns.

    This is retained for reproducing the initial output-reference correction.
    New run_cached outputs already have these keys directly. Prices, sides,
    dates, entry/exit addresses and gross results are asserted unchanged.
    """
    import hashlib
    import json
    from pathlib import Path
    out = Path(output_dir)
    for model in MODELS:
        fragments, gap_fragments, offset = [], [], 0
        for period in ("2018_22", "2023_plus"):
            tp, gp = out/f"{model}_{period}_trades.csv", out/f"{model}_{period}_gaps.csv"
            t, gaps = pd.read_csv(tp), pd.read_csv(gp)
            t["trade_id"] = np.arange(len(t))
            t = t.reindex(columns=TRADE_COLUMNS)
            if len(gaps):
                ix = gaps.trade_id.to_numpy(int)
                gaps["trade_entry_flat"] = t.entry_flat.iloc[ix].to_numpy(int)
                gaps["trade_exit_flat"] = t.exit_flat.iloc[ix].to_numpy(int)
            else:
                gaps["trade_entry_flat"] = pd.Series(dtype=int)
                gaps["trade_exit_flat"] = pd.Series(dtype=int)
            gaps = gaps.reindex(columns=["model", "trade_id", "trade_entry_flat", "trade_exit_flat",
                                        "first_flat", "last_flat", "minutes", "classification"])
            t.to_csv(tp, index=False)
            gaps.to_csv(gp, index=False)
            fragments.append(t)
            gaps = gaps.copy()
            gaps["trade_id"] += offset
            gap_fragments.append(gaps)
            offset += len(t)
        before = pd.read_csv(out/f"{model}_trades.csv")
        combined = pd.concat(fragments, ignore_index=True)
        combined["trade_id"] = np.arange(len(combined))
        invariant = [c for c in before.columns if c != "trade_id"]
        pd.testing.assert_frame_equal(before[invariant], combined[invariant], check_dtype=False)
        combined.to_csv(out/f"{model}_trades.csv", index=False)
        pd.concat(gap_fragments, ignore_index=True).to_csv(out/f"{model}_gaps.csv", index=False)
    path = out/"replay_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    for name, info in manifest["ledger_files"].items():
        target = out/name
        info["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    manifest["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    manifest["gap_reference_metadata_correction"] = "Split-local gap IDs offset in combined ledger; raw return fields unchanged"
    path.write_text(json.dumps(manifest, indent=2, default=str)+"\n", encoding="utf-8")
