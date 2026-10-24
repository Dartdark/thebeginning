"""Frozen source extension for 'overnight volume switch.txt'; no import-time IO.

Grid24/grid.execute cannot express this cross-date observed-bar state, exact
08:29 classification, next-bar-open VWAP exit, and entry-bar stop omission.
This module therefore extends execution while reusing Grid24's minute arrays.
Features always observe the entire cached chronology (including warm-up) up to
the requested cutoff. Coverage affects the account audit, never source signals
or feature history. No price data is loaded and no replay runs at import.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


MODES = ("literal_delay", "immediate_stop")
FIRST_RETURN_DATE = pd.Timestamp("2018-01-01")
DEFAULTS = dict(vol_mult=1.4, one_side_mult=2.0, min_night_bars=30,
                fade_stop_mult=.40, long_stop_mult=.30,
                night_start=960, night_end=509, rth_start=510, rth_end=900,
                exit_fade=524, cash_start=599, cash_end=659)
TRADE_COLUMNS = ["date", "gridrow", "day", "side", "cell", "leg", "signal_j", "entry_j",
                 "exit_j", "j0", "j1", "entry_row", "exit_row", "entry_date", "exit_date",
                 "entry_flat", "exit_flat", "entry", "exit", "kind", "kind_label",
                 "gross_points", "gross_nq", "stop_pts", "actual_stop_pts", "stop_px", "entry_phase", "exit_phase",
                 "path_start_flat", "path_end_flat_exclusive", "protection_start_flat",
                 "timing_mode", "missing_held_minutes", "cross_date", "late_after_1559",
                 "account_eligible"]


@dataclass
class SourceFeatures:
    daily: pd.DataFrame
    vwap: np.ndarray
    observed: np.ndarray
    cutoff_row: int


@dataclass
class ReplayResult:
    trades: pd.DataFrame
    audit: pd.DataFrame
    features: pd.DataFrame
    events: pd.DataFrame
    spec: dict


def frozen_spec(mode):
    if mode not in MODES:
        raise ValueError(f"Unknown frozen execution mode: {mode}")
    return dict(source="overnight volume switch.txt", timing_mode=mode,
                stop_activation="first observed bar after entry bar" if mode == "literal_delay"
                                else "entry bar; counterfactual diagnostic",
                primary_mode="literal_delay", bar_minutes=1, bar_stamp="close, Central",
                entry="next observed bar open after source signal",
                market_exit="next observed bar open; priority over stop at that open",
                stop="entry fill price +/- source distance; adverse gap open, otherwise stop level",
                targets=False, volume="Grid24.v as total Ticks under Build Volume On=Trade Volume",
                source_defaults=DEFAULTS, atr="mean prior 20 exact-15:00 completed RTH high-low ranges",
                source_history="all observed finite OHLC bars, across dates, without account eligibility filtering",
                source_vwap_zero="retain previous sessVWAP if current cumulative Ticks=0",
                current_night_os_guard="none: classified only validates prior history; short current nights can select OS",
                account_coverage="finite OHLC for each minute 08:29..11:00 inclusive; no missing held range or cross-date carry",
                costs="raw price geometry only; fees and fill slippage applied by account/diagnostics caller",
                account_failsafe="none invented: source carries and unclosed trades are audited/excluded",
                price_levels="adverse .25-point rounding: sell stop down, buy stop up; disclosed source benchmark adapter")


def stop_price(entry, side, stop_points):
    raw = float(entry)-int(side)*float(stop_points)
    return float((np.floor(raw/.25+1e-10) if side > 0 else np.ceil(raw/.25-1e-10))*.25)


def _cutoff_row(g, cutoff_date):
    if cutoff_date is None:
        return len(g.ts)-1
    return int(np.searchsorted(pd.DatetimeIndex(g.ts).values,
                               np.datetime64(pd.Timestamp(cutoff_date).normalize()), side="right")-1)


def build_features(g, cutoff_date=None):
    """Source feature state on every observed bar, before position guards.

    The exact 08:29 bar computes the prior-only median/range average, then
    inserts the current night. RTH initializes on the first observed bar whose
    time is strictly after 08:30, normally 08:31. No absent minute is fabricated.
    """
    last_row = _cutoff_row(g, cutoff_date)
    if last_row < 0:
        raise ValueError("Cutoff precedes the cached grid")
    shape = (last_row+1, g.o.shape[1])
    if shape[1] != 1440:
        raise ValueError("This source requires the Grid24 minute clock")
    observed = np.logical_and.reduce([np.isfinite(getattr(g, f)[:last_row+1]) for f in ("o", "h", "l", "c")])
    vw = np.full(shape, np.nan)
    rows = []
    night_hist, range_hist = [], []
    prev_night = prev_rth = False
    night_vol = night_bars = night_open = night_start_flat = 0
    heavy = classified = rth_on = False
    atr = day_hi = day_lo = m_open = m_hi = m_lo = 0.
    sum_pv = sum_v = sess_vwap = 0.
    median = night_move = 0.
    for d in range(last_row+1):
        rec = dict(date=pd.Timestamp(g.ts[d]), gridrow=d,
                   observed_ohlc_bars=int(observed[d].sum()), has_829=False,
                   classified=False, heavy=False, night_bars=0, night_volume=np.nan,
                   night_move=np.nan, night_open=np.nan, night_start_flat=-1,
                   median_volume=np.nan, atrD=np.nan, n_hist_before=len(night_hist),
                   n_range_before=len(range_hist), current_night_valid=False,
                   rth_start_j=-1, m_open=np.nan, m_hi=np.nan, m_lo=np.nan,
                   os_close=np.nan, os_vwap=np.nan, os_condition=False,
                   fade_side=0, range_recorded=False, day_range=np.nan,
                   missing_volume_bars=0)
        for j in np.flatnonzero(observed[d]):
            o, h, l, c = (float(getattr(g, f)[d, j]) for f in ("o", "h", "l", "c"))
            v = float(g.v[d, j])
            if not np.isfinite(v):
                rec["missing_volume_bars"] += 1
            is_night = j > DEFAULTS["night_start"] or j <= DEFAULTS["night_end"]
            is_rth = j > DEFAULTS["rth_start"] and j <= DEFAULTS["rth_end"]
            if is_night and not prev_night:
                night_vol, night_bars, night_open = 0., 0, o
                night_start_flat = d*1440+int(j)
                heavy = classified = rth_on = False
            if is_night:
                night_vol += v
                night_bars += 1
            if j == DEFAULTS["night_end"]:
                atr = float(np.mean(range_hist[-20:])) if len(range_hist) >= 20 else 0.
                median = float(np.median(night_hist[-20:])) if len(night_hist) >= 20 else 0.
                classified = len(night_hist) >= 20 and len(range_hist) >= 20
                heavy = classified and night_bars >= DEFAULTS["min_night_bars"] and night_vol > DEFAULTS["vol_mult"]*median
                move = night_move = c-night_open
                rec.update(has_829=True, classified=classified, heavy=bool(heavy), night_bars=night_bars,
                           night_volume=night_vol, night_move=move, night_open=night_open,
                           night_start_flat=night_start_flat, median_volume=median, atrD=atr,
                           n_hist_before=len(night_hist), n_range_before=len(range_hist),
                           current_night_valid=night_bars >= DEFAULTS["min_night_bars"],
                           fade_side=int(-np.sign(move)) if heavy and move != 0 and atr > 0 else 0)
                if night_bars >= DEFAULTS["min_night_bars"]:
                    night_hist.append(night_vol)
                    night_hist = night_hist[-20:]
            if is_rth:
                if not prev_rth:
                    rth_on = True
                    day_hi, day_lo = h, l
                    m_open, m_hi, m_lo = o, h, l
                    sum_pv = sum_v = 0.
                    rec["rth_start_j"] = int(j)
                day_hi, day_lo = max(day_hi, h), min(day_lo, l)
                if j <= DEFAULTS["cash_start"]:
                    m_hi, m_lo = max(m_hi, h), min(m_lo, l)
                sum_pv += (h+l+c)/3.*v
                sum_v += v
                if sum_v > 0:
                    sess_vwap = sum_pv/sum_v
            vw[d, j] = sess_vwap
            if j == DEFAULTS["rth_end"] and rth_on:
                rng = day_hi-day_lo
                range_hist.append(rng)
                range_hist = range_hist[-20:]
                rec.update(range_recorded=True, day_range=rng)
                rth_on = False
            if j == DEFAULTS["cash_start"]:
                condition = bool(classified and not heavy and rth_on and atr > 0
                                 and (m_hi-m_open) > DEFAULTS["one_side_mult"]*(m_open-m_lo)
                                 and c > sess_vwap)
                rec.update(m_open=m_open, m_hi=m_hi, m_lo=m_lo, os_close=c,
                           os_vwap=sess_vwap, os_condition=condition,
                           classified=classified, heavy=bool(heavy), atrD=atr,
                           night_bars=night_bars, night_volume=night_vol,
                           night_move=night_move, night_open=night_open,
                           night_start_flat=night_start_flat, median_volume=median,
                           current_night_valid=night_bars >= DEFAULTS["min_night_bars"])
            prev_night, prev_rth = bool(is_night), bool(is_rth)
        rows.append(rec)
    daily = pd.DataFrame(rows)
    daily["ratio"] = np.where(daily.median_volume > 0, daily.night_volume/daily.median_volume, np.nan)
    daily["os_without_829"] = daily.os_condition & ~daily.has_829
    return SourceFeatures(daily, vw, observed, last_row)


def _coverage(g, features):
    trading = set(int(r) for r in g.trading)
    rows = []
    for rec in features.daily.itertuples():
        d = int(rec.gridrow)
        obs = features.observed[d]
        missing = np.flatnonzero(~obs[509:661])+509
        rows.append(dict(date=rec.date, gridrow=d, is_trading_row=d in trading,
                         account_window_complete=not len(missing),
                         missing_account_window_minutes=len(missing),
                         missing_account_window_first=int(missing[0]) if len(missing) else -1,
                         missing_account_window_last=int(missing[-1]) if len(missing) else -1,
                         affected_by_unknown_held_gap=False, affected_by_cross_date_trade=False,
                         affected_by_unclosed_trade=False, account_eligible=False))
    return pd.DataFrame(rows)


def replay(g, mode="literal_delay", cutoff_date=None, *, start_date=FIRST_RETURN_DATE,
           features: Optional[SourceFeatures] = None):
    """Replay the observed source chronology, auditing rather than fixing gaps.

    Both entries and market exits fill at the next observed bar open. Stop
    checking starts on the following observed bar in the primary model, and
    on the entry bar only in the diagnostic. Market exits scheduled at the
    previous close take priority over a stop at their fill bar open.
    """
    spec = frozen_spec(mode)
    feat = build_features(g, cutoff_date) if features is None else features
    if feat.cutoff_row != _cutoff_row(g, cutoff_date):
        raise ValueError("Supplied features do not match the requested cutoff")
    audit = _coverage(g, feat)
    trading = set(int(r) for r in g.trading)
    signal_data = feat.daily.set_index("gridrow")
    events, trades = [], []
    position = pending_entry = pending_exit = None
    start = pd.Timestamp(start_date).normalize()
    # Warm-up bars before start still participate in feature construction, but
    # source entries begin only at the requested research interval.
    for d in range(feat.cutoff_row+1):
        date = pd.Timestamp(g.ts[d])
        if date < start:
            continue
        daily = signal_data.loc[d]
        for j in np.flatnonzero(feat.observed[d]):
            flat = d*1440+int(j)
            oo, hh, ll, cc = (float(getattr(g, f)[d, j]) for f in ("o", "h", "l", "c"))
            if pending_exit is not None and position is not None:
                _close_trade(position, flat, oo, pending_exit, "open", mode,
                             feat.observed, g, trades, audit)
                position = pending_exit = None
            if pending_entry is not None and position is None:
                position = dict(**pending_entry, entry_flat=flat, entry=oo,
                                stop_px=stop_price(oo, pending_entry["side"], pending_entry["stop_pts"]))
                position["protection_start_flat"] = flat + (mode == "literal_delay")
                pending_entry = None
                events.append(dict(date=date, gridrow=d, minute=int(j), event="fill_entry", cell=position["cell"], side=position["side"]))
            if position is not None and flat >= position["protection_start_flat"]:
                side, stop = position["side"], position["stop_px"]
                gap = oo <= stop if side > 0 else oo >= stop
                hit = ll <= stop if side > 0 else hh >= stop
                if gap or hit:
                    _close_trade(position, flat, oo if gap else stop, "stop", "open" if gap else "intrabar",
                                 mode, feat.observed, g, trades, audit)
                    position = None
            # These source triggers are calculated only at an observed close.
            # Position guards are evaluated after fills/stops within this bar.
            signal = None
            if j == DEFAULTS["night_end"] and int(daily.fade_side):
                signal = dict(side=int(daily.fade_side), cell="T", stop_pts=DEFAULTS["fade_stop_mult"]*float(daily.atrD))
            elif j == DEFAULTS["cash_start"] and bool(daily.os_condition):
                signal = dict(side=1, cell="OS", stop_pts=DEFAULTS["long_stop_mult"]*float(daily.atrD))
            if signal is not None:
                blocked = position is not None or pending_entry is not None
                events.append(dict(date=date, gridrow=d, minute=int(j), event="blocked_entry" if blocked else "signal_entry",
                                   cell=signal["cell"], side=signal["side"]))
                if not blocked:
                    pending_entry = dict(**signal, signal_flat=flat, signal_j=int(j), signal_date=date)
            if position is not None:
                if position["cell"] == "T" and DEFAULTS["exit_fade"] <= j < DEFAULTS["rth_end"]:
                    pending_exit = "fade_time"
                elif position["cell"] == "OS" and DEFAULTS["cash_start"] < j < DEFAULTS["rth_end"]:
                    if j >= DEFAULTS["cash_end"]:
                        pending_exit = "os_time"
                    elif cc < feat.vwap[d, j]:
                        pending_exit = "vwap"
    if position is not None:
        a = int(position["entry_flat"])//1440
        audit.loc[a:, "affected_by_unclosed_trade"] = True
        events.append(dict(date=pd.Timestamp(g.ts[feat.cutoff_row]), gridrow=feat.cutoff_row,
                           minute=-1, event="unclosed_position_at_cutoff", cell=position["cell"], side=position["side"]))
    if pending_entry is not None:
        events.append(dict(date=pending_entry["signal_date"], gridrow=pending_entry["signal_flat"]//1440,
                           minute=pending_entry["signal_j"], event="unfilled_entry_at_cutoff",
                           cell=pending_entry["cell"], side=pending_entry["side"]))
    audit["account_eligible"] = (audit.is_trading_row & audit.account_window_complete
                                 & ~audit.affected_by_unknown_held_gap & ~audit.affected_by_cross_date_trade
                                 & ~audit.affected_by_unclosed_trade & (audit.date >= start))
    audit["status"] = np.where(audit.account_eligible, "eligible", "excluded")
    result = pd.DataFrame(trades)
    if len(result):
        eligible = audit.set_index("gridrow").account_eligible
        result["account_eligible"] = result.day.map(eligible).fillna(False).to_numpy(bool)
        result = result.reindex(columns=TRADE_COLUMNS)
    else:
        result = pd.DataFrame(columns=TRADE_COLUMNS)
    # Return daily features/audit for the requested interval; history construction
    # above retains all prior observations, including weekends and partial nights.
    keep = (audit.date >= start)
    return ReplayResult(result, audit.loc[keep].reset_index(drop=True),
                        feat.daily.loc[feat.daily.date >= start].reset_index(drop=True),
                        pd.DataFrame(events), spec)


def _close_trade(p, flat, px, label, phase, mode, observed, g, trades, audit):
    entry_flat = int(p["entry_flat"])
    er, ej = divmod(entry_flat, 1440)
    xr, xj = divmod(int(flat), 1440)
    end = int(flat) + int(phase != "open")
    held_missing = int((~observed.ravel()[entry_flat:end]).sum())
    cross = er != xr
    late = cross or xj > 959  # 15:59 CT close stamp; do not invent a rescue fill.
    if held_missing and audit is not None:
        audit.loc[er:xr, "affected_by_unknown_held_gap"] = True
    if cross and audit is not None:
        audit.loc[er:xr, "affected_by_cross_date_trade"] = True
    side = int(p["side"])
    points = (float(px)-p["entry"])*side
    trades.append(dict(date=pd.Timestamp(g.ts[er]), gridrow=er, day=er, side=side, cell=p["cell"], leg=p["cell"],
                       signal_j=p["signal_j"], entry_j=ej, exit_j=xj, j0=ej, j1=xj,
                       entry_row=er, exit_row=xr, entry_date=pd.Timestamp(g.ts[er]), exit_date=pd.Timestamp(g.ts[xr]),
                       entry_flat=entry_flat, exit_flat=int(flat), entry=p["entry"], exit=float(px),
                       kind=0 if label == "stop" else 2, kind_label=label, gross_points=points, gross_nq=points*20.,
                       stop_pts=p["stop_pts"], actual_stop_pts=abs(p["entry"]-p["stop_px"]),
                       stop_px=p["stop_px"], entry_phase="open", exit_phase=phase,
                       path_start_flat=entry_flat, path_end_flat_exclusive=end,
                       protection_start_flat=p["protection_start_flat"], timing_mode=mode,
                       missing_held_minutes=held_missing, cross_date=cross, late_after_1559=late))


def walk_event(g, row, entry_j, side, leg, stop_points, timing="literal_delay", *, features=None,
               vwap=None, observed=None):
    """Fixed-event exit walker for predeclared nulls, without source selection.

    OS shorts mirror the VWAP crossing only for the random-side null; the
    source has no OS short. Pass prepared features (preferred), or explicit
    vwap/observed arrays, to avoid reconstructing feature history repeatedly.
    Returns the same raw geometry fields as one source ledger row. No prices
    are read beyond the supplied feature cutoff.
    """
    frozen_spec(timing)
    row, entry_j, side = int(row), int(entry_j), int(side)
    leg = str(leg).upper()
    if side not in (-1, 1) or leg not in ("T", "OS") or not np.isfinite(stop_points) or stop_points <= 0:
        raise ValueError("Fixed event requires side +/-1, T/OS leg and positive finite stop")
    if features is not None:
        observed, vwap = features.observed, features.vwap
    if observed is None:
        observed = np.logical_and.reduce([np.isfinite(getattr(g, f)) for f in ("o", "h", "l", "c")])
    if leg == "OS" and vwap is None:
        raise ValueError("OS event needs its source VWAP path")
    start = row*1440+entry_j
    if not observed[row, entry_j]:
        raise ValueError("Fixed event must open on an observed finite-OHLC bar")
    entry = float(g.o[row, entry_j])
    stop = stop_price(entry, side, stop_points)
    p = dict(side=side, cell=leg, stop_pts=float(stop_points), signal_j=entry_j-1,
             entry_flat=start, entry=entry, stop_px=stop,
             protection_start_flat=start+(timing == "literal_delay"))
    pending_market = None
    output = []
    for d in range(row, observed.shape[0]):
        first = entry_j if d == row else 0
        for j in np.flatnonzero(observed[d, first:])+first:
            flat = d*1440+int(j)
            oo, hh, ll, cc = (float(getattr(g, f)[d, j]) for f in ("o", "h", "l", "c"))
            if pending_market is not None:
                _close_trade(p, flat, oo, pending_market, "open", timing, observed, g, output, None)
                return output[0]
            if flat >= p["protection_start_flat"]:
                gap = oo <= stop if side > 0 else oo >= stop
                hit = ll <= stop if side > 0 else hh >= stop
                if gap or hit:
                    _close_trade(p, flat, oo if gap else stop, "stop", "open" if gap else "intrabar",
                                 timing, observed, g, output, None)
                    return output[0]
            if leg == "T" and DEFAULTS["exit_fade"] <= j < DEFAULTS["rth_end"]:
                pending_market = "fade_time"
            elif leg == "OS" and DEFAULTS["cash_start"] < j < DEFAULTS["rth_end"]:
                if j >= DEFAULTS["cash_end"]:
                    pending_market = "os_time"
                elif (cc-float(vwap[d, j]))*side < 0:
                    pending_market = "vwap"
    return None


def synthetic_checks():
    """Synthetic only; no cached market prices or strategy returns are loaded."""
    from types import SimpleNamespace
    n = 25
    dates = pd.date_range("2018-01-01", periods=n, freq="D")
    shape = (n, 1440)
    g = SimpleNamespace(ts=dates.to_numpy(), D=n, trading=np.arange(n),
                        o=np.full(shape, np.nan), h=np.full(shape, np.nan),
                        l=np.full(shape, np.nan), c=np.full(shape, np.nan), v=np.full(shape, np.nan))
    # First 24 days supply prior history; the 25th night is heavy. RTH is
    # complete through 15:00 so exact source warm-up, not manufactured counts.
    for d in range(n):
        js = np.r_[np.arange(0, 510), np.arange(510, 901), np.arange(1021, 1440)]
        g.o[d, js] = 100.
        g.h[d, js] = 110.
        g.l[d, js] = 90.
        g.c[d, js] = 100.
        g.v[d, js] = 1.
    g.v[-1, :510] = 10.
    g.c[-1, 509] = 105.
    # Short fade at bar 08:30 open=100, stop=108, first entry bar reaches
    # 110 but the following protected bar does not. Diagnostic stops there.
    g.h[-1, 511:525] = 101.
    g.l[-1, 511:525] = 99.
    f = build_features(g)
    a = replay(g, "literal_delay", features=f)
    b = replay(g, "immediate_stop", features=f)
    ta, tb = a.trades[a.trades.day == n-1].iloc[0], b.trades[b.trades.day == n-1].iloc[0]
    assert ta.entry_j == 510 and ta.exit_j == 525 and ta.kind_label == "fade_time"
    assert tb.entry_j == 510 and tb.exit_j == 510 and tb.kind_label == "stop"
    assert ta.entry == 100. and ta.stop_px == 108. and ta.stop_pts == 8.
    assert ta.protection_start_flat == ta.entry_flat+1 and tb.protection_start_flat == tb.entry_flat
    assert f.daily.iloc[-1].rth_start_j == 511
    # Prior-only median classification cannot include the current heavy night.
    assert f.daily.iloc[-1].night_volume > 1.4*f.daily.iloc[-1].median_volume
    assert a.audit.loc[a.audit.gridrow == n-1, "account_eligible"].iloc[0]
    assert stop_price(100., 1, 8.01) == 91.75 and stop_price(100., -1, 8.01) == 108.25
    for mode, expected in (("literal_delay", ta), ("immediate_stop", tb)):
        event = walk_event(g, n-1, 510, -1, "T", 8., mode, features=f)
        assert event["exit_j"] == expected.exit_j and event["exit"] == expected.exit
    # Quiet classification intentionally does not require >=30 current-night bars.
    q = SimpleNamespace(**{k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in vars(g).items()})
    for field in ("o", "h", "l", "c", "v"):
        getattr(q, field)[-2, 1021:] = np.nan
        getattr(q, field)[-1, :481] = np.nan
    q.h[-1, 511:660], q.l[-1, 511:660], q.c[-1, 511:660] = 110., 99., 105.
    qf = build_features(q)
    qr = qf.daily.iloc[-1]
    assert qr.night_bars == 29 and not qr.heavy and qr.classified and qr.os_condition
    # Market exits already queued at a prior close beat stops at the next open.
    q = SimpleNamespace(**{k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in vars(g).items()})
    q.o[-1, 525] = q.h[-1, 525] = q.c[-1, 525] = 120.
    q.l[-1, 525] = 119.
    event = walk_event(q, n-1, 510, -1, "T", 8., "literal_delay", features=f)
    assert event["kind_label"] == "fade_time" and event["exit"] == 120.
    q.o[-1, 511], q.h[-1, 511], q.l[-1, 511], q.c[-1, 511] = 115., 116., 114., 115.
    event = walk_event(q, n-1, 510, -1, "T", 8., "literal_delay", features=f)
    assert event["kind_label"] == "stop" and event["exit_phase"] == "open" and event["exit"] == 115.
    return dict(entry_bar_unprotected_primary=True, entry_bar_protected_diagnostic=True,
                next_bar_market_exit=True, fill_price_stop_anchor=True,
                rth_first_bar_831=True, prior_only_night_median=True,
                current_night_os_validity_omission_preserved=True,
                adverse_tick_rounding=True, pending_market_priority=True, adverse_stop_gap=True,
                no_market_cache_loaded=True)


def run_cached(cache_path="scratch_data/g24.pkl",
               output_dir="analysis/outputs/codex_night_volume_switch/replay",
               feature_cache="agents/codex/runtime/night_volume_switch_features.pkl"):
    """Explicit post-preregistration runner, design first and then recent once.

    Both execution modes remain frozen. Full ledgers concatenate the two
    disjoint periods; their combination does not replay or select a winner.
    The prepared feature cache contains source state/VWAP, never a new grid.
    """
    import hashlib
    import json
    import pickle
    import subprocess
    from pathlib import Path
    subprocess.run(["git", "cat-file", "-e", "affb482:agents/codex/plans/night_volume_switch.md"], check=True)
    checks = synthetic_checks()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    with Path(cache_path).open("rb") as f:
        g = pickle.load(f)
    by_mode = {mode: [] for mode in MODES}
    for period, start, cutoff in (("2018_22", "2018-01-01", "2022-12-31"),
                                  ("2023_plus", "2023-01-01", None)):
        features = build_features(g, cutoff)
        for mode in MODES:
            result = replay(g, mode, cutoff, start_date=start, features=features)
            for key in ("trades", "audit", "features", "events"):
                getattr(result, key).to_csv(out / f"{mode}_{period}_{key}.csv", index=False)
            if result.events.event.eq("unclosed_position_at_cutoff").any():
                raise ValueError("Unclosed position at the research split: audit state carry before combining periods")
            by_mode[mode].append(result)
            print(f"{period} {mode}: trades={len(result.trades)}, "
                  f"eligible_trades={int(result.trades.account_eligible.sum())}, "
                  f"eligible_days={int(result.audit.account_eligible.sum())}", flush=True)
        if cutoff is None:
            target = Path(feature_cache)
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("wb") as f:
                pickle.dump(features, f, protocol=4)
    manifest = dict(preregistration_commit="affb482", strategy_variants=2,
                    modes=list(MODES), synthetic_checks=checks,
                    period_order=["2018_22", "2023_plus"], no_parameter_selection=True,
                    feature_cache=str(feature_cache), account_failsafe_fills=0,
                    ledger_files={}, specs={})
    for mode, parts in by_mode.items():
        for key in ("trades", "audit", "features", "events"):
            frame = pd.concat([getattr(x, key) for x in parts], ignore_index=True)
            path = out / f"{mode}_{key}.csv"
            frame.to_csv(path, index=False)
            manifest["ledger_files"][path.name] = dict(rows=len(frame), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        manifest["specs"][mode] = frozen_spec(mode)
    def file_sha(path):
        h = hashlib.sha256()
        with Path(path).open("rb") as f:
            for block in iter(lambda: f.read(1024*1024), b""):
                h.update(block)
        return h.hexdigest()
    manifest["inputs"] = {str(cache_path): file_sha(cache_path),
                           "agents/codex/inputs/night_volume_switch/source.txt": file_sha("agents/codex/inputs/night_volume_switch/source.txt")}
    manifest["script_sha256"] = file_sha(__file__)
    (out / "replay_manifest.json").write_text(json.dumps(manifest, indent=2, default=str)+"\n", encoding="utf-8")
    return manifest
