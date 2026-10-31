"""Hunt-v2 H03: Swing Target v3 ENTRY-ONLY opening-agreement gross screen.

Imports never load market data.  No stopped/target/break-even engine is imported
or called.  The fixed raw window is the first parent stop entry to OPEN j900
(14:59 wall CT).  MC reads select date/side/entry/t_in strings only, then remove
non-design dates before converting any entry field.  MC exits/net stay unread.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import fcntl
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
from types import SimpleNamespace
import warnings

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_hunt_v2_swing_opening"
SCRIPT = "analysis/codex_hunt_v2_swing_opening_gross.py"
PLAN = "agents/codex/plans/hunt_v2_swing_opening_agreement.md"
EVIDENCE = "agents/codex/evidence/hunt_v2_book_filter_nomination.md"
SOURCE_REF = "7f0800ffc04d56bd878750369a4abc2316ee01d8"
SOURCE = "funded_strategies/NQ_Swing_Target_v3.txt"
SOURCE_SHA256 = "88689848107edfc2cd4f704b0b5f9030b7695a92dcade38ec112f3b2f8509377"
SOURCE_ARCHIVE = "agents/codex/inputs/hunt_v2_swing_opening_agreement/NQ_Swing_Target_v3.source.txt"
SOURCE_MANIFEST = "agents/codex/inputs/hunt_v2_swing_opening_agreement/source_manifest.json"
WARMUP = "agents/codex/inputs/ob_v2_bench/NQ_1min_2017.csv"
MC = "agents/codex/inputs/rebound/plan_update_afde088/checks/candidates/swing_target/mc_trades_v3.csv"
sys.path.insert(0, str(ROOT / "analysis"))
from codex_hunt_v2_ldf_delta import (audited_frame, csv_once, dump_once,
    runtime_versions, sha, tstat, utcnow, valid_ohlcv, validate_metadata_keys)
from grid24 import Grid24, jof
from codex_s03_calendar import calendar_status
from replica import is_early_close

YEARS = tuple(range(2018, 2023))
NATIVE_FIELDS = ("open", "high", "low", "close", "volume")
OF_FIELDS = (*NATIVE_FIELDS, "upvol", "downvol")
RTH_FIRST_J, STORE_J = 511, 900
FEATURE_LAST_J, FIRST_ENTRY_J, LAST_ENTRY_J, RAW_EXIT_J = 525, 526, 870, 900
RT_COST, GROSS_HURDLE, MIN_KEPT = 2.24, 4.48, 100
KNOWN_FRACTION_MIN, PARITY_MIN = 0.90, 0.90
LATER_CONFIGURATIONS = ("MC_PUBLISHED", "REPLAY_BASE", "OPEN_AGREE", "REPLAY_BASE_DELAY1", "OPEN_AGREE_DELAY1")
EVENT_COLUMNS = ("date", "event_id", "year", "side", "entry_j", "entry", "entry_phase", "entry_gap",
    "both_levels_touched", "raw_exit_j", "raw_exit_open", "gross_points", "gross_mnq", "gross_nq",
    "unresolved_held_path", "invalid_held_minutes", "exit_open_valid", "reference_unresolved",
    "reference_store_ids", "reference_dates", "lineage_fault_dates", "reference_geometry_unresolved", "hi_ref", "lo_ref", "avg_range20", "opening_price_move",
    "opening_delta", "flow_known", "flow_known_neutral", "flow_unknown_reason", "keep_OPEN_AGREE", "valid_source_minutes",
    "source_alias_mismatch_minutes", "native_total_mismatch_minutes", "source_close_mismatch_minutes",
    "event_time", "available_at", "decision_time", "first_fill_interval_start", "first_fill_interval_end",
    "receipt_latency_verified", "source_clock", "scan_prefix_valid_bars")


def committed_bytes(ref, path):
    return subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=ROOT)


def literal_holiday(date):
    d = pd.Timestamp(date); m, day, y = d.month, d.day, d.year
    dow = (d.dayofweek + 1) % 7  # Source PowerLanguage Sunday=0.
    return bool((m == 1 and dow == 1 and 15 <= day <= 21)
        or (m == 2 and dow == 1 and 15 <= day <= 21)
        or (m == 5 and dow == 1 and day >= 25)
        or (y >= 2022 and m == 6 and (day == 19 or (day == 20 and dow == 1) or (day == 18 and dow == 5)))
        or (m == 7 and (day in (3, 4) or (day == 5 and dow == 1)))
        or (m == 9 and dow == 1 and day <= 7)
        or (m == 11 and dow == 4 and 22 <= day <= 28)
        or (m == 11 and dow == 5 and 23 <= day <= 29)
        or (m == 12 and (day in (24, 25, 31) or (day == 26 and dow == 1) or (day == 23 and dow == 5)))
        or (m == 1 and (day == 1 or (day == 2 and dow == 1))))


def allow_calendar(date):
    return calendar_status(date)["kind"] == "normal" and not is_early_close(pd.Timestamp(date)) and not literal_holiday(date)


@dataclass(frozen=True)
class NativeAdapter:
    output: Path = OUT

    @property
    def paths(self):
        return (ROOT / WARMUP, *(ROOT / f"data/NQ_1min_{year}.csv" for year in YEARS))

    def build(self, names):
        if tuple(map(Path, names)) != self.paths:
            raise ValueError("Wrong native/warm-up source set.")
        frame, audit = audited_frame(list(map(str, self.paths)), NATIVE_FIELDS, "native_day_only")
        cache = self.output / "cache"; cache.mkdir(parents=True, exist_ok=True)
        ignore = self.output / ".gitignore"
        if not ignore.exists(): ignore.write_text("cache/\n*.lock\n")
        for source in self.paths:
            link = cache / f"day_{source.stem[-4:]}.csv"
            if link.is_symlink():
                if link.resolve() != source.resolve(): raise ValueError("Wrong cache source link.")
            elif link.exists(): raise ValueError("Unexpected non-symlink cache source.")
            else: link.symlink_to(source)
        if {p.name for p in cache.glob("*.csv")} != {f"day_{y}.csv" for y in (2017, *YEARS)}:
            raise ValueError("Unbound input in isolated native cache.")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            grid = Grid24(str(cache / "day_*.csv"), night_pattern="")
        if pd.DatetimeIndex(grid.ts).year.min() != 2017 or pd.DatetimeIndex(grid.ts).year.max() != 2022:
            raise ValueError("Shared grid crossed admitted source years.")
        rows, cols = np.searchsorted(grid.dates, frame.date.to_numpy()), jof(frame.time.to_numpy())
        for name, attr in (("open", "o"), ("high", "h"), ("low", "l"), ("close", "c"), ("volume", "v")):
            if not np.allclose(getattr(grid, attr)[rows, cols], frame[name].to_numpy(float), equal_nan=True):
                raise ValueError("Shared grid differs from duplicate-audited native " + name)
        return grid, audit


def store_coverage(session):
    """Audit literal stored ranges without replacing or stretching history."""
    dates = list(dict.fromkeys(session["bar_dates"]))
    js = session["bar_js"]
    mixed = len(dates) != 1
    first, last = (min(js), max(js)) if js else (None, None)
    contiguous = bool(js) and len(js) == len(set(js)) and sorted(js) == list(range(RTH_FIRST_J, last + 1))
    kind = calendar_status(dates[0])["kind"] if dates else "unknown"
    known_short = bool(dates) and kind in ("early", "holiday")
    complete = not mixed and contiguous and kind != "weekend" and (known_short or last == STORE_J)
    return dict(reference_complete=bool(complete), mixed_date_reference=mixed, known_short_reference=known_short,
        first_valid_j=first, last_valid_j=last, valid_rth_bars=len(js), expected_normal_rth_bars=390,
        stored_bar_date_ids=json.dumps(dates), missing_or_invalid_reference_minutes=(390 - len(set(js))) if not known_short else (last - RTH_FIRST_J + 1 - len(set(js)) if js else 0))


def parent_history(grid, valid):
    """Literal v3 observed-bar storage only; no entry or protective exit P&L."""
    history, stores, features, days, lineage_faults = [], [], {}, [], []
    active = None
    previous_observed_date = None
    for row, ts in enumerate(pd.DatetimeIndex(grid.ts)):
        label = ts.date().isoformat()
        js = np.flatnonzero(valid[row])
        day = dict(date=label, year=ts.year, literal_holiday=literal_holiday(ts), cash_kind=calendar_status(ts)["kind"],
            allowed_calendar=allow_calendar(ts), n_stored_before_first_bar=len(history), first_native_j=int(js[0]) if len(js) else None,
            missing_0831=not bool(valid[row, RTH_FIRST_J]), discarded_unclosed_reference=False, stale_mixed_state=False)
        day["n_stored_at_first_bar_after_backstop"] = len(history)
        for position, j in enumerate(js):
            if position == 0 and previous_observed_date != label and active is not None and j < RTH_FIRST_J:
                coverage = store_coverage(active)
                stored = dict(store_id=len(stores), session_date=active["session_date"], high=active["high"], low=active["low"],
                    range=active["high"] - active["low"], stored_at_date=label, stored_at_j=int(j), store_reason="new_date_backstop", **coverage)
                stores.append(stored); history.insert(0, stored); active = None
            elif position == 0 and previous_observed_date != label and active is not None and j > RTH_FIRST_J:
                day["stale_mixed_state"] = True
            if position == 0:
                day["n_stored_at_first_bar_after_backstop"] = len(history)
            if j == RTH_FIRST_J:
                if active is not None:
                    day["discarded_unclosed_reference"] = True
                    if not store_coverage(active)["reference_complete"]:
                        lineage_faults.append(dict(date=active["session_date"], stored_count_at_fault=len(stores)))
                fault_dates = [fault["date"] for fault in lineage_faults if len(stores) - fault["stored_count_at_fault"] < 20]
                feature = dict(n_stored=len(history), reference_store_ids=json.dumps([s["store_id"] for s in history[:20]]),
                    reference_dates=json.dumps([s["session_date"] for s in history[:20]]), lineage_fault_dates=json.dumps(fault_dates),
                    reference_geometry_unresolved=False,
                    reference_unresolved=bool(fault_dates) or any(not s["reference_complete"] for s in history[:20]))
                if len(history) >= 20:
                    feature.update(hi_ref=max(s["high"] for s in history[:2]), lo_ref=min(s["low"] for s in history[:2]),
                        avg_range20=float(np.mean([s["range"] for s in history[:20]])))
                    feature["reference_geometry_unresolved"] = not (np.isfinite(feature["avg_range20"]) and feature["avg_range20"] > 0
                        and np.isfinite(feature["hi_ref"]) and np.isfinite(feature["lo_ref"]) and feature["hi_ref"] > feature["lo_ref"])
                    feature["reference_unresolved"] |= feature["reference_geometry_unresolved"]
                features[row] = feature
                active = dict(session_date=label, high=float(grid.h[row, j]), low=float(grid.l[row, j]), bar_js=[int(j)], bar_dates=[label])
            elif active is not None and RTH_FIRST_J < j <= STORE_J:
                active["high"] = max(active["high"], float(grid.h[row, j]))
                active["low"] = min(active["low"], float(grid.l[row, j]))
                active["bar_js"].append(int(j)); active["bar_dates"].append(label)
            if active is not None and j == STORE_J:
                coverage = store_coverage(active)
                stored = dict(store_id=len(stores), session_date=active["session_date"], high=active["high"], low=active["low"],
                    range=active["high"] - active["low"], stored_at_date=label, stored_at_j=int(j), store_reason="literal_1500", **coverage)
                stores.append(stored); history.insert(0, stored); active = None
            previous_observed_date = label
        day["n_stored_after_day"] = len(history)
        day["history_ready"] = features.get(row, {}).get("n_stored", day["n_stored_at_first_bar_after_backstop"]) >= 20
        day["lineage_fault_dates"] = features.get(row, {}).get("lineage_fault_dates", "[]")
        day["reference_geometry_unresolved"] = features.get(row, {}).get("reference_geometry_unresolved", False)
        day["comparison_eligible"] = ts.year in YEARS and day["allowed_calendar"] and day["history_ready"]
        days.append(day)
    return features, pd.DataFrame(stores), pd.DataFrame(days)


def stop_entry(o, h, l, hi, lo):
    both = bool(h >= hi and l <= lo)
    if o >= hi: return dict(side=1, entry=float(o), entry_phase="open", entry_gap=bool(o > hi), both_levels_touched=both)
    if o <= lo: return dict(side=-1, entry=float(o), entry_phase="open", entry_gap=bool(o < lo), both_levels_touched=both)
    high_first = h - o <= o - l  # Shared convention: ties high first.
    if both: side = 1 if high_first else -1
    elif h >= hi: side = 1
    elif l <= lo: side = -1
    else: return None
    return dict(side=side, entry=float(hi if side > 0 else lo), entry_phase="intrabar", entry_gap=False, both_levels_touched=both)


def parent_entry(grid, row, valid, feature):
    if feature is None or feature.get("n_stored", 0) < 20:
        return None, dict(disposition="warmup_or_missing_session_start", unresolved_scan=feature is None)
    hi, lo = feature["hi_ref"], feature["lo_ref"]
    if not valid[row, RTH_FIRST_J]: return None, dict(disposition="missing_session_start", unresolved_scan=True)
    if not (lo <= grid.o[row, RTH_FIRST_J] <= hi and grid.h[row, RTH_FIRST_J] <= hi and grid.l[row, RTH_FIRST_J] >= lo):
        return None, dict(disposition="initial_open_or_range_outside_parent_levels", unresolved_scan=False)
    for j in range(RTH_FIRST_J, FEATURE_LAST_J + 1):
        if not valid[row, j]: return None, dict(disposition="missing_or_invalid_early_prefix", unresolved_scan=True, invalid_prefix_j=j)
        if grid.h[row, j] > hi or grid.l[row, j] < lo:
            return None, dict(disposition="strict_pre845_level_breach", unresolved_scan=False)
    for j in range(FIRST_ENTRY_J, LAST_ENTRY_J + 1):
        if not valid[row, j]: return None, dict(disposition="missing_or_invalid_live_order_prefix", unresolved_scan=True, invalid_prefix_j=j)
        entry = stop_entry(grid.o[row, j], grid.h[row, j], grid.l[row, j], hi, lo)
        if entry is not None:
            return dict(entry_j=j, scan_prefix_valid_bars=j - RTH_FIRST_J + 1, **entry), dict(disposition="first_parent_entry", unresolved_scan=False)
    return None, dict(disposition="no_parent_entry", unresolved_scan=False)


def flow_grid(binding, grid):
    frame, audit = audited_frame(binding["of_paths"], OF_FIELDS, "OF")
    source_date = pd.to_datetime(frame.date.astype(str), format="%Y%m%d")
    native_wall = source_date + pd.to_timedelta(jof(frame.time.to_numpy()), unit="m") - pd.Timedelta(hours=1)
    date_ids = native_wall.dt.strftime("%Y%m%d").astype(int).to_numpy()
    rows = np.searchsorted(grid.dates, date_ids)
    inside = (rows < grid.D) & (grid.dates[np.minimum(rows, grid.D - 1)] == date_ids)
    cols = (native_wall.dt.hour * 60 + native_wall.dt.minute).to_numpy()
    result = {}
    for name in OF_FIELDS:
        arr = np.full((grid.D, 1440), np.nan)
        arr[rows[inside], cols[inside]] = frame[name].to_numpy(float)[inside]
        result[name] = arr
    audit.update(source_clock="ET close labels minus60minutes toCT; US DST dates shared", rows_outside_native_grid=int((~inside).sum()))
    return result, audit


def opening_state(native, source):
    native_ok = valid_ohlcv(*(native[k] for k in NATIVE_FIELDS))
    source_ok = valid_ohlcv(*(source[k] for k in NATIVE_FIELDS))
    buy, sell, alias = np.asarray(source["upvol"], float), np.asarray(source["downvol"], float), np.asarray(source["volume"], float)
    quantities = np.isfinite(buy) & np.isfinite(sell) & (buy >= 0) & (sell >= 0)
    aliases = np.isfinite(alias) & np.isfinite(buy) & (alias == buy)
    totals = quantities & np.isfinite(native["volume"]) & (buy + sell == native["volume"])
    closes = np.isfinite(source["close"]) & np.isfinite(native["close"]) & (np.abs(source["close"] - native["close"]) <= .25)
    valid = native_ok & source_ok & quantities & aliases & totals & closes
    complete = len(valid) == 15 and bool(valid.all())
    aggregate_positive = complete and bool((buy + sell).sum() > 0)
    p = float(native["close"][-1] - native["open"][0]) if bool(native_ok.all()) and len(native_ok) == 15 else None
    delta = float((alias - sell).sum()) if complete else None
    known = bool(complete and aggregate_positive and p is not None)
    reason = "" if known else "incomplete_or_invalid_unmatched_flow" if not complete else "zero_aggregate_tape_volume"
    return dict(opening_price_move=p, opening_delta=delta, flow_known=known,
        flow_known_neutral=bool(known and (p == 0 or delta == 0)), flow_unknown_reason=reason,
        keep_OPEN_AGREE=not (known and p * delta < 0), valid_source_minutes=int(valid.sum()),
        source_alias_mismatch_minutes=int((np.isfinite(alias) & np.isfinite(buy) & ~aliases).sum()),
        native_total_mismatch_minutes=int((quantities & np.isfinite(native["volume"]) & ~totals).sum()),
        source_close_mismatch_minutes=int((np.isfinite(source["close"]) & np.isfinite(native["close"]) & ~closes).sum()))


def information_clock(date, entry_j):
    day = pd.Timestamp(date).normalize()
    event = (day + pd.Timedelta(minutes=FEATURE_LAST_J)).tz_localize("America/Chicago")
    start = (day + pd.Timedelta(minutes=entry_j - 1)).tz_localize("America/Chicago")
    end = (day + pd.Timedelta(minutes=entry_j)).tz_localize("America/Chicago")
    assert event <= start
    return dict(event_time=event.isoformat(), available_at=event.isoformat(), decision_time=event.isoformat(),
        first_fill_interval_start=start.isoformat(), first_fill_interval_end=end.isoformat(), receipt_latency_verified=False,
        source_clock="nativeCTclose; OF_ETminus60; zero receipt delay assumption; intrabar fill time unknown")


def extract_entries(grid, flow):
    """Parent entries/features only; no event exit endpoint or raw P&L."""
    valid = valid_ohlcv(grid.o, grid.h, grid.l, grid.c, grid.v)
    features, stores, calendar = parent_history(grid, valid)
    records = []
    for row, ts in enumerate(pd.DatetimeIndex(grid.ts)):
        calendar.loc[row, "unresolved_scan"] = False
        calendar.loc[row, "reference_unresolved"] = False
        calendar.loc[row, "disposition"] = "outside_design_or_known_calendar_skip"
        if ts.year not in YEARS or not calendar.loc[row, "allowed_calendar"]: continue
        feature = features.get(row)
        if feature is None and not calendar.loc[row, "history_ready"]: continue
        entry, audit = parent_entry(grid, row, valid, feature)
        for key, value in audit.items(): calendar.loc[row, key] = value
        if entry is None: continue
        j = entry["entry_j"]
        window = slice(RTH_FIRST_J, FEATURE_LAST_J + 1)
        native = {name: getattr(grid, name[0] if name != "volume" else "v")[row, window] for name in NATIVE_FIELDS}
        source = {name: array[row, window] for name, array in flow.items()}
        state = opening_state(native, source)
        calendar.loc[row, "reference_unresolved"] = bool(feature["reference_unresolved"])
        records.append(dict(date=ts.date().isoformat(), event_id=f"ST_RAW_{ts.strftime('%Y%m%d')}_01", year=ts.year,
            **entry, **{k: feature[k] for k in ("reference_unresolved", "reference_store_ids", "reference_dates", "lineage_fault_dates", "reference_geometry_unresolved", "hi_ref", "lo_ref", "avg_range20")},
            **state, **information_clock(ts, j)))
    calendar["unresolved_scan"] = calendar.unresolved_scan.astype(bool)
    calendar["reference_unresolved"] = calendar.reference_unresolved.astype(bool)
    return pd.DataFrame(records, columns=EVENT_COLUMNS), calendar, stores


def attach_raw_windows(grid, entries):
    """Called only AFTER entry-parity PASS.  Never simulates protection/BE."""
    events = entries.copy()
    events["unresolved_held_path"] = False
    events["exit_open_valid"] = False
    lookup = {pd.Timestamp(ts).date().isoformat(): row for row, ts in enumerate(grid.ts)}
    valid = valid_ohlcv(grid.o, grid.h, grid.l, grid.c, grid.v)
    for idx, event in events.iterrows():
        row, j = lookup[event.date], int(event.entry_j)
        exit_open = grid.o[row, RAW_EXIT_J]
        exit_ok = bool(np.isfinite(exit_open) and exit_open > 0)
        held = valid[row, j:RAW_EXIT_J]
        points = (exit_open - event.entry) * event.side if exit_ok else np.nan
        values = dict(raw_exit_j=RAW_EXIT_J, raw_exit_open=float(exit_open), gross_points=float(points),
            gross_mnq=float(points * 2), gross_nq=float(points * 20),
            unresolved_held_path=not bool(held.all()) or not exit_ok,
            invalid_held_minutes=int((~held).sum()), exit_open_valid=exit_ok)
        for key, value in values.items(): events.loc[idx, key] = value
    for name in ("unresolved_held_path", "exit_open_valid"):
        events[name] = events[name].astype(bool)
    return events


DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
TIME_RE = re.compile(r"^(?:(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})[ T])?(?P<h>[0-9]{2}):(?P<m>[0-9]{2})(?::(?P<s>[0-9]{2}))?$")
SIDE_RE = re.compile(r"^-?1(?:\.0+)?$")


def mc_date(value):
    if not isinstance(value, str) or DATE_RE.fullmatch(value) is None: raise ValueError("MCdate must be ISOdate only.")
    return pd.Timestamp(value).date().isoformat()


def mc_minute(value, row_date):
    match = TIME_RE.fullmatch(value)
    if match is None: raise ValueError("MCt_in is neither strict CTtime nor ISOdate+CTtime.")
    day = match.group("date")
    if day is not None and mc_date(day) != row_date: raise ValueError("MCt_in date differs from rowdate.")
    h, m, s = int(match.group("h")), int(match.group("m")), int(match.group("s") or 0)
    if h > 23 or m > 59 or s > 59: raise ValueError("Impossible MCclock.")
    return h * 60 + m + s / 60


def mc_entries_from_strings(frame, comparison_dates):
    frame = frame.copy()
    invalid_dates = []
    dates = []
    for idx, value in frame.date.items():
        try: dates.append(mc_date(value))
        except (ValueError, TypeError): dates.append(""); invalid_dates.append(int(idx))
    frame["date"] = dates
    # Filter dates BEFORE entry/side/time conversion. No future entry fields.
    design = frame.date.str[:4].isin(list(map(str, YEARS)))
    excluded = [dict(source_row_id=int(idx), date=day, reason="outside_preknown_calendar_or_parent_warmup")
                for idx, day in frame.loc[design & ~frame.date.isin(comparison_dates), "date"].items()]
    frame = frame[design & frame.date.isin(comparison_dates)].copy()
    duplicate_dates = sorted(frame.loc[frame.date.duplicated(keep=False), "date"].unique().tolist())
    duplicate_ids = [int(idx) for idx in frame.index[frame.date.duplicated(keep=False)]]
    rows, invalid_entries = [], []
    for r in frame.itertuples():
        try:
            if SIDE_RE.fullmatch(r.side) is None: raise ValueError("MCside must be integer-valued±1encoding.")
            entry = float(r.entry)
            if not np.isfinite(entry) or entry <= 0: raise ValueError("Invalid MCentry price.")
            minute = mc_minute(r.t_in, r.date)
        except (ValueError, TypeError, OverflowError):
            invalid_entries.append(dict(source_row_id=int(r.Index), date=r.date, issue="invalid_or_ambiguous_side_entry_or_CTclock"))
            continue
        rows.append(dict(source_row_id=int(r.Index), date=r.date, side=int(r.side.split(".")[0]), entry=entry, entry_j=minute))
    metadata = dict(passed=not invalid_dates and not invalid_entries and not duplicate_dates,
        fullfile_invalid_date_row_ids=invalid_dates, invalid_design_entry_rows=invalid_entries,
        duplicate_design_entry_dates=duplicate_dates, duplicate_design_entry_source_row_ids=duplicate_ids,
        excluded_design_entry_date_rows=excluded,
        eligible_design_entry_rows_before_parse=len(frame), interpretation="oneMCentry/date;duplicateorunparseablemetadatafatalevenifmatchingfractionsfavorable")
    return pd.DataFrame(rows, columns=("source_row_id", "date", "side", "entry", "entry_j")), metadata


def entry_parity(events, calendar, path=None, frame=None):
    dates = set(calendar.loc[calendar.comparison_eligible, "date"])
    if frame is None:
        # usecols prevents loading ANY exit/kind/gross/net fields from MC.
        frame = pd.read_csv(path, usecols=["date", "side", "entry", "t_in"], dtype=str, keep_default_na=False)
    mc, metadata = mc_entries_from_strings(frame, dates)
    parent = events[events.date.isin(dates)]
    matches, details, used = 0, [], set()
    for p in parent.itertuples():
        possible = mc[(mc.date == p.date) & (mc.side == p.side)]
        hit = None
        for idx, r in possible.iterrows():
            if idx not in used and abs(r.entry - p.entry) <= .25 + 1e-9 and abs(r.entry_j - p.entry_j) <= 1 + 1e-9:
                hit = idx; break
        if hit is not None: used.add(hit); matches += 1
        details.append(dict(date=p.date, side=p.side, parent_entry=p.entry, parent_entry_j=p.entry_j,
            matched_mc_entry=hit is not None, mc_row=int(hit) if hit is not None else None))
    precision = matches / len(parent) if len(parent) else None
    recall = matches / len(mc) if len(mc) else None
    result = dict(parent_entries=len(parent), mc_entries=len(mc), matches=matches,
        parent_to_mc_fraction=precision, mc_to_parent_fraction=recall,
        passed=bool(metadata["passed"] and precision is not None and recall is not None and precision >= PARITY_MIN and recall >= PARITY_MIN),
        comparison="unique one-to-one date/side,entry±.25,entryclose-label±1minute on common preknown normalcalendar after parent warmup",
        mc_metadata_audit=metadata, mc_exit_price_kind_gross_net_read=False, no_full_stopped_parity_claim=True)
    mc["matched_parent"] = [idx in used for idx in mc.index]
    return result, pd.DataFrame(details), mc


def summaries(events):
    rows = []
    for population, mask in (("BASE", np.ones(len(events), bool)), ("KEPT", events.keep_OPEN_AGREE.astype(bool).to_numpy()), ("REMOVED", ~events.keep_OPEN_AGREE.astype(bool).to_numpy())):
        for period in ("2018-22", *map(str, YEARS)):
            per = np.ones(len(events), bool) if period == "2018-22" else events.year.eq(int(period)).to_numpy()
            for side, sm in (("all", np.ones(len(events), bool)), ("long", events.side.eq(1).to_numpy()), ("short", events.side.eq(-1).to_numpy())):
                selected = events[mask & per & sm]
                x = selected.gross_mnq.to_numpy(float); x = x[np.isfinite(x)]
                rows.append(dict(population=population, period=period, side=side, events=len(selected), observed_returns=len(x),
                    gross_total_mnq=float(x.sum()), gross_mean_mnq=float(x.mean()) if len(x) else None, gross_t=tstat(x),
                    gross_sd_mnq=float(x.std(ddof=1)) if len(x) > 1 else None,
                    gross_standard_error_mnq=float(x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 1 else None,
                    unresolved_held_events=int(selected.unresolved_held_path.sum()), known_flow_events=int(selected.flow_known.sum()),
                    unresolved_reference_events=int(selected.reference_unresolved.sum()), hurdle_mnq=GROSS_HURDLE))
    return pd.DataFrame(rows)


def gate(events, calendar, parity):
    kept = events[events.keep_OPEN_AGREE.astype(bool)]
    x = kept.gross_mnq.to_numpy(float); observed = x[np.isfinite(x)]
    mean = float(observed.mean()) if len(observed) else None
    known = float(events.flow_known.astype(bool).mean()) if len(events) else None
    held = not bool(events.unresolved_held_path.any())
    prefixes = not bool(calendar.unresolved_scan.any())
    references = not bool(events.reference_unresolved.any())
    economic = bool(len(kept) >= MIN_KEPT and mean is not None and mean >= GROSS_HURDLE)
    complete = len(observed) == len(kept) and held and prefixes and references
    flow_pass = known is not None and known > KNOWN_FRACTION_MIN
    return dict(primary_model="OPEN_AGREE", kind="ENTRY_ONLY_PARENT_RAW_NO_STOP", base_events=len(events), kept_events=len(kept), removed_events=int((~events.keep_OPEN_AGREE.astype(bool)).sum()),
        primary_gross_mean_mnq=mean, primary_gross_t=tstat(observed), min_kept=MIN_KEPT, gross_hurdle_mnq=GROSS_HURDLE,
        economic_pass=economic, known_flow_fraction_on_base_events=known, known_flow_strictly_above90percent=flow_pass,
        all_base_held_paths_complete=held, all_eligible_prefixes_resolved=prefixes, all_base_references_resolved=references,
        unresolved_base_held_events=int(events.unresolved_held_path.sum()), unresolved_scan_days=int(calendar.unresolved_scan.sum()),
        unresolved_base_reference_events=int(events.reference_unresolved.sum()), entry_parity_pass=parity["passed"],
        all_kept_endpoints_observed=len(observed) == len(kept), passed=bool(economic and complete and flow_pass and parity["passed"]),
        stopped_returns_calculated=False, mc_exit_or_net_read=False, counted_evaluations=0, validation_run=False, account_tests_run=False)


def raw_after_entry_parity(grid, entries, calendar, parity, attach=attach_raw_windows):
    """A failed pre-gross audit cannot open the registered raw return window."""
    if not parity["passed"]:
        return entries.copy(), dict(phase="pre_gross", passed=False, primary_model="OPEN_AGREE",
            reason="MC entry metadata/parity admission failed before raw endpoints",
            parent_entry_events=len(entries), entry_parity_pass=False,
            raw_returns_calculated=False, gross_screen_runs=0, counted_evaluations=0,
            stopped_returns_calculated=False, mc_exit_or_net_read=False, validation_run=False, account_tests_run=False), None
    events = attach(grid, entries)
    decision = gate(events, calendar, parity)
    decision.update(phase="gross", raw_returns_calculated=True, gross_screen_runs=1)
    return events, decision, summaries(events)


def verify_before_prices(prereg):
    if subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() != "codex/work": raise ValueError("Wrongbranch.")
    for p in (PLAN, EVIDENCE):
        if committed_bytes(prereg, p) != (ROOT / p).read_bytes(): raise ValueError("Prereg/evidencechanged:" + p)
    dependencies = [SCRIPT, "analysis/codex_hunt_v2_ldf_delta.py", "analysis/grid24.py", "analysis/codex_s03_calendar.py", "analysis/replica.py", "agents/codex/RESEARCH_CONTROLS.md"]
    for p in dependencies:
        if committed_bytes("HEAD", p) != (ROOT / p).read_bytes(): raise ValueError("FreezeHEADsource:" + p)
    for p in (ROOT / "analysis/outputs").glob("codex_hunt_v2_swing_opening*"):
        if any((p / name).exists() for name in ("gross_verified_execution.json", "pre_gross_verified_execution.json")):
            raise ValueError("H03pre-gross/grosscompleted;noalternate-directoryrerun.")
    source = committed_bytes(SOURCE_REF, SOURCE)
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA256: raise ValueError("Frozenv3sourceSHAchanged.")
    for name in (SOURCE_ARCHIVE, SOURCE_MANIFEST):
        if committed_bytes(prereg, name) != (ROOT / name).read_bytes(): raise ValueError("Frozenparentarchivechanged:" + name)
    if sha(ROOT / SOURCE_ARCHIVE) != SOURCE_SHA256: raise ValueError("Parentarchivedoesnotmatchpinnedv3bytes.")
    native = list(map(str, NativeAdapter().paths))
    of = [str(p) for y in YEARS for p in sorted((ROOT / "data").glob(f"OF_1min_{y}_*.csv"))]
    if any(not Path(p).exists() for p in [*native, str(ROOT / MC)]) or any(not any(f"OF_1min_{y}_" in p for p in of) for y in YEARS): raise FileNotFoundError("Frozeninputmissing.")
    paths = [*map(Path, native), *map(Path, of), ROOT / MC]
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    hashes.update({p: sha(ROOT / p) for p in [PLAN, EVIDENCE, SOURCE_ARCHIVE, SOURCE_MANIFEST, *dependencies]})
    metadata = []
    for p in [*map(Path, native), *map(Path, of)]:
        frame = pd.read_csv(p, usecols=["date", "time"])
        y = int(p.name.split("_")[-2] if p.name.startswith("OF_") else p.stem[-4:])
        validate_metadata_keys(frame, y, p.name)
        metadata.append(dict(path=str(p.relative_to(ROOT)), rows=len(frame), min_date=int(frame.date.min()), max_date=int(frame.date.max()), duplicate_keys=int(frame.duplicated(["date", "time"]).sum())))
    return dict(prereg=prereg, implementation_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        hashes=hashes, metadata=metadata, native_paths=native, of_paths=of, source_ref=SOURCE_REF,
        source_path=SOURCE, source_sha256=SOURCE_SHA256, runtime_versions=runtime_versions())


@contextmanager
def execution_lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "gross.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB); yield


def gross(prereg):
    with execution_lock():
        binding = verify_before_prices(prereg); started = utcnow()
        with (OUT / "attempts.jsonl").open("a") as log: log.write(json.dumps(dict(started_utc=started, prereg=prereg, phase="raw_gross", script_sha256=sha(ROOT / SCRIPT))) + "\n")
        grid, native_audit = NativeAdapter().build(binding["native_paths"])
        flow, flow_audit = flow_grid(binding, grid)
        entries, calendar, stores = extract_entries(grid, flow)
        parity, matches, mc_entries = entry_parity(entries, calendar, path=ROOT / MC)
        events, decision, summary = raw_after_entry_parity(grid, entries, calendar, parity)
        raw_calculated = decision["raw_returns_calculated"]
        if binding["hashes"] != {p: sha(ROOT / p) for p in binding["hashes"]}: raise ValueError("Boundsourceschanged.")
        names = []
        for name, frame in (("parent_entries.csv", entries), ("gross_calendar_audit.csv", calendar),
            ("gross_stored_reference_audit.csv", stores), ("gross_mc_entry_matches.csv", matches), ("gross_mc_entries_design_only.csv", mc_entries)):
            csv_once(OUT / name, frame); names.append(name)
        if raw_calculated:
            csv_once(OUT / "gross_events.csv", events); csv_once(OUT / "gross_summary.csv", summary)
            names.extend(["gross_events.csv", "gross_summary.csv"])
        else:
            dump_once(OUT / "gross_summary_status.json", dict(status="N/A: failed MCENTRY pre-gross audit", raw_returns_calculated=False))
            names.append("gross_summary_status.json")
        gate_name = "gross_gate.json" if raw_calculated else "pre_gross_gate.json"
        dump_once(OUT / "gross_input_binding.json", binding); dump_once(OUT / gate_name, decision); dump_once(OUT / "gross_entry_parity.json", parity)
        names.extend(["gross_input_binding.json", gate_name, "gross_entry_parity.json"])
        audit = dict(native=native_audit, flow=flow_audit, source_history="literalv3:20storedRTH08:31..15:00ranges;2storedextrema;new-datepre831backstop",
            source_entry_only=True, protective_stop_target_BE_evaluated=False, no_mc_exits_or_net_read=True,
            raw_exit="nativeOPENj900=14:59wallCT;noSL/TP/BE/net", parent_first_entry_cap=1,
            ambiguity_path="nearerextremefirst,tiesHIGHfirst;pairedOCOassumptionnotverifiedintrabar",
            calendar="literalv3HOL UNIONsharedholiday/early/mourning/GF;historynotcalendarfiltered",
            no_g_trading_or_last_j_eligibility=True, no2017_trades=True, no_ON_or2023_inputs=True,
            source_classification="OFvolume=upvol,buy+sell=nativeV,closeswithin.25;all15required,nonnegativeperminute,positiveaggregatetape;neutralP/DKEEP_KNOWN;invalidUNKNOWN_KEEP",
            input_schema_eras="annualnativeCTclose andOFETclose exports;historicalreceiptunverified",
            flow_known_events=int(events.flow_known.sum()), base_entry_events=len(events),
            both_level_entry_minutes=int(events.both_levels_touched.sum()), worse_open_gap_entries=int(events.entry_gap.sum()),
            unexplained_base_reference_events=int(events.reference_unresolved.sum()), unresolved_parent_prefix_days=int(calendar.unresolved_scan.sum()),
            unresolved_base_held_events=int(events.unresolved_held_path.sum()) if raw_calculated else None,
            raw_returns_calculated=raw_calculated, native_MNQ_spread_fills_verified=False)
        dump_once(OUT / "gross_data_audit.json", audit)
        kept_mean = decision.get("primary_gross_mean_mnq")
        bridge = dict(raw_fees_subtracted=0, later_MNQ_commission_RT=1.24, later_market_stop_slippage_per_fill=.50,
            assumed_roundtrip=RT_COST, primary_raw_breakeven_extra_cost_per_event=kept_mean - RT_COST if kept_mean is not None else None,
            frozen_later_cost_only_stress="4ticksadversepermarket/stopfill;5.24RT;notselectable", stopped_stress_returns_calculated=False,
            frozen_later_latency_stress="1minuteactivationdelay:firstentry527;onlyafterdesignpass+immediatebookbench;no delayedrawreturns",
            latency="zero-receiptdelayresearchassumption;actualavailabilityandMNQexecutionunverified", no_double_spread_charge=True)
        dump_once(OUT / "gross_cost_bridge.json", bridge)
        manifest = dict(candidate_id="hunt_v2_H03_SWING_OPENING_AGREEMENT", family_id="adoptedSTv3_whole_day_filter",
            preregistration_commit=prereg, implementation_commit=binding["implementation_commit"], code_sha256=sha(ROOT / SCRIPT),
            source_hashes=binding["hashes"], versions=runtime_versions(), years=list(YEARS), warmup="owned2017featureonly;storedcoverageaudited",
            random_seed=None, learned_model=False, event_count=len(events), known_flow_fraction=float(entries.flow_known.astype(bool).mean()) if len(entries) else None,
            information_clock="featureclose/available/decision08:45zero-delay;firstparentfillnativej>=526;exactintraminutetimingunknown",
            baseline_ladder="entry-onlyBASE vswhole-dayOPEN_AGREE kept/removed raw;stoppedcontrolsconditionalongrossPASS",
            unknown_policy="KEEP/UNKNOWN,neverfavorabledeletion", counted_evaluations=0, stopped_returns_calculated=False,
            raw_returns_calculated=raw_calculated, phase=decision["phase"])
        manifest["frozen_later_configurations"] = list(LATER_CONFIGURATIONS)
        manifest["delayed_raw_returns_calculated"] = False
        manifest["price_confounding_diagnostic"] = "1000matchedsubsetsstrata(year,side,openingPsign,entry_j<=660vs>660,flowknown);conditionalongrossPASS"
        dump_once(OUT / "gross_run_manifest.json", manifest)
        names.extend(["gross_data_audit.json", "gross_cost_bridge.json", "gross_run_manifest.json"])
        marker = dict(started_utc=started, completed_utc=utcnow(), phase=decision["phase"], passed=decision["passed"], prereg=prereg,
            implementation_commit=binding["implementation_commit"], script_sha256=sha(ROOT / SCRIPT),
            artifacts_sha256={p: sha(OUT / p) for p in names}, counted_evaluations=0, new_hypotheses=1,
            raw_returns_calculated=raw_calculated, gross_screen_runs=decision["gross_screen_runs"],
            stopped_returns_calculated=False, mc_exit_or_net_read=False, validation_run=False, account_tests_run=False)
        marker_name = "gross_verified_execution.json" if raw_calculated else "pre_gross_verified_execution.json"
        dump_once(OUT / marker_name, marker)
        return decision


def synthetic_checks():
    assert literal_holiday("2021-12-31") and not allow_calendar("2023-04-07") and not allow_calendar("2018-12-05")
    assert stop_entry(100, 111, 89, 110, 90)["side"] == 1  # Equidistant tie highfirst.
    assert stop_entry(100, 112, 89, 110, 90)["side"] == -1
    gap = stop_entry(112, 113, 111, 110, 90)
    assert gap["entry"] == 112 and gap["entry_gap"]
    dates = pd.date_range("2017-11-01", "2018-01-10", freq="D")
    shape = (len(dates), 1440)
    fake = SimpleNamespace(ts=dates.to_numpy(), dates=dates.strftime("%Y%m%d").astype(int).to_numpy(), D=len(dates))
    for attr in ("o", "h", "l", "c", "v"): setattr(fake, attr, np.full(shape, np.nan))
    for row, day in enumerate(dates):
        if day.dayofweek >= 5: continue
        for attr, value in (("o", 100.), ("h", 110.), ("l", 90.), ("c", 100.), ("v", 10.)):
            getattr(fake, attr)[row, 480:916] = value
    row = len(dates) - 1
    fake.o[row, 511], fake.h[row, 511:526], fake.l[row, 511:526] = 99., 105., 95.
    fake.h[row, 526], fake.l[row, 526] = 111., 99.
    valid = valid_ohlcv(fake.o, fake.h, fake.l, fake.c, fake.v)
    features, stores, calendar = parent_history(fake, valid)
    assert features[row]["n_stored"] >= 20 and features[row]["avg_range20"] == 20
    entry, audit = parent_entry(fake, row, valid, features[row])
    assert entry["entry_j"] == 526 and entry["entry"] == 110 and entry["side"] == 1
    assert not audit["unresolved_scan"]
    fake.h[row, 525] = 110.25
    assert parent_entry(fake, row, valid_ohlcv(fake.o, fake.h, fake.l, fake.c, fake.v), features[row])[0] is None
    fake.h[row, 525] = 110.  # Touchalone does not disarm.
    assert parent_entry(fake, row, valid_ohlcv(fake.o, fake.h, fake.l, fake.c, fake.v), features[row])[0]["entry_j"] == 526
    fake.c[row, 520] = np.nan
    e, a = parent_entry(fake, row, valid_ohlcv(fake.o, fake.h, fake.l, fake.c, fake.v), features[row])
    assert e is None and a["unresolved_scan"]
    fake.c[row, 520] = 100.
    # Last14:29 close issuance remains live for native14:30, never14:31.
    saved_h, saved_l = fake.h[row].copy(), fake.l[row].copy()
    fake.h[row, 526:872], fake.l[row, 526:872] = 105., 95.
    fake.h[row, 870] = 111.
    last, _ = parent_entry(fake, row, valid_ohlcv(fake.o, fake.h, fake.l, fake.c, fake.v), features[row])
    assert last["entry_j"] == 870
    fake.h[row, 870], fake.h[row, 871] = 105., 111.
    assert parent_entry(fake, row, valid_ohlcv(fake.o, fake.h, fake.l, fake.c, fake.v), features[row])[0] is None
    fake.h[row], fake.l[row] = saved_h, saved_l
    native = {k: np.full(15, v) for k, v in (("open", 100.), ("high", 105.), ("low", 95.), ("close", 101.), ("volume", 10.))}
    source = {k: v.copy() for k, v in native.items()}; source.update(volume=np.full(15, 6.), upvol=np.full(15, 6.), downvol=np.full(15, 4.))
    state = opening_state(native, source)
    assert state["flow_known"] and state["keep_OPEN_AGREE"] and state["opening_delta"] == 30
    source.update(volume=np.full(15, 4.), upvol=np.full(15, 4.), downvol=np.full(15, 6.))
    assert not opening_state(native, source)["keep_OPEN_AGREE"]
    source.update(volume=np.full(15, 5.), upvol=np.full(15, 5.), downvol=np.full(15, 5.))
    assert opening_state(native, source)["flow_known"] and opening_state(native, source)["flow_known_neutral"] and opening_state(native, source)["keep_OPEN_AGREE"]
    source["upvol"][0] = 6.
    assert not opening_state(native, source)["flow_known"]
    # Valid zero-quantity minutes remain observed; only aggregate0 is unknown.
    source.update(volume=np.full(15, 5.), upvol=np.full(15, 5.), downvol=np.full(15, 5.))
    native["volume"][0] = 0.
    for key in ("volume", "upvol", "downvol"): source[key][0] = 0.
    assert opening_state(native, source)["flow_known"]
    native["close"][-1] = native["open"][0]
    source["close"][-1] = native["close"][-1]
    assert opening_state(native, source)["flow_known_neutral"]
    native["volume"][:] = 0.
    for key in ("volume", "upvol", "downvol"): source[key][:] = 0.
    assert not opening_state(native, source)["flow_known"] and opening_state(native, source)["keep_OPEN_AGREE"]
    # Restore one invalid-alias source window for UNKNOWN_KEEP entry fixtures.
    source.update(volume=np.full(15, 5.), upvol=np.full(15, 5.), downvol=np.full(15, 5.))
    source["upvol"][0] = 6.
    flow = {name: np.full(shape, np.nan) for name in OF_FIELDS}
    for name, values in source.items(): flow[name][row, 511:526] = values
    entries, cal, stored = extract_entries(fake, flow)
    assert entries.raw_exit_open.isna().all() and entries.gross_points.isna().all()
    def forbidden_raw(*args): raise AssertionError("Raw attachment called after failed entry parity.")
    _, pre_gate, pre_summary = raw_after_entry_parity(fake, entries, cal, {"passed": False}, attach=forbidden_raw)
    assert not pre_gate["raw_returns_calculated"] and pre_gate["gross_screen_runs"] == 0 and pre_summary is None
    events = attach_raw_windows(fake, entries)
    final = events[events.date.eq("2018-01-10")]
    assert len(final) == 1 and final.iloc[0].raw_exit_j == 900 and final.iloc[0].raw_exit_open == 100
    assert final.iloc[0].keep_OPEN_AGREE and not final.iloc[0].flow_known
    fake.c[row, 700] = np.nan
    entries, cal, _ = extract_entries(fake, flow)
    events = attach_raw_windows(fake, entries)
    assert events[events.date.eq("2018-01-10")].iloc[0].unresolved_held_path
    fake.c[row, 700] = 100.
    fake.c[row, 900] = np.nan  # After liquidation: no held-path veto.
    entries, _, _ = extract_entries(fake, flow)
    events = attach_raw_windows(fake, entries)
    assert not events[events.date.eq("2018-01-10")].iloc[0].unresolved_held_path
    fake.c[row, 900] = 100.
    for day, expected in (("2021-12-31", False), ("2022-12-23", False), ("2021-11-25", True), ("2021-11-27", False)):
        short = dict(bar_dates=[day] * 210, bar_js=list(range(511, 721)))
        assert store_coverage(short)["reference_complete"] == expected
    # Nineteen stores + prior missing900 becomes twenty through pre831backstop;
    # missing today's511 remains an eligible unknown prefix, not lost warmup.
    small_dates = pd.bdate_range("2017-12-11", periods=21)
    small = SimpleNamespace(ts=small_dates.to_numpy(), dates=small_dates.strftime("%Y%m%d").astype(int).to_numpy(), D=len(small_dates))
    for attr, value in (("o", 100.), ("h", 110.), ("l", 90.), ("c", 100.), ("v", 10.)):
        arr = np.full((small.D, 1440), np.nan); arr[:, 480:916] = value
        arr[-2, 900:] = np.nan; arr[-1, 511] = np.nan
        setattr(small, attr, arr)
    small_valid = valid_ohlcv(small.o, small.h, small.l, small.c, small.v)
    _, _, small_calendar = parent_history(small, small_valid)
    assert small_calendar.iloc[-1].n_stored_before_first_bar == 19
    assert small_calendar.iloc[-1].n_stored_at_first_bar_after_backstop == 20 and small_calendar.iloc[-1].history_ready
    small_flow = {key: np.full((small.D, 1440), np.nan) for key in OF_FIELDS}
    _, small_calendar, _ = extract_entries(small, small_flow)
    assert small_calendar.iloc[-1].unresolved_scan
    # A literal overwritten missing-normal-end is retained as a lineage fault,
    # never inserted into DH/DL and never silently stretched into a clean ref.
    for attr in ("o", "h", "l", "c", "v"):
        arr = getattr(small, attr); arr[-1, :511] = np.nan
        arr[-1, 511] = {"o": 100., "h": 110., "l": 90., "c": 100., "v": 10.}[attr]
    small_valid = valid_ohlcv(small.o, small.h, small.l, small.c, small.v)
    small_features, _, small_calendar = parent_history(small, small_valid)
    assert small_calendar.iloc[-1].discarded_unclosed_reference
    assert small_features[small.D - 1]["reference_unresolved"]
    assert json.loads(small_features[small.D - 1]["lineage_fault_dates"]) == [small_dates[-2].date().isoformat()]
    sample = pd.DataFrame([dict(date="2018-01-10", side="1", entry="110", t_in="2018-01-10 08:46:00"),
                           dict(date="2023-01-03", side="FUTURE_POISON", entry="FUTURE_POISON", t_in="FUTURE_POISON")])
    mc, meta = mc_entries_from_strings(sample, {"2018-01-10", "2023-01-03"})
    assert len(mc) == 1 and mc.iloc[0].entry_j == 526
    assert meta["passed"]
    encoded = sample.iloc[:1].copy(); encoded.loc[0, "side"] = "1.0"
    parsed, meta = mc_entries_from_strings(encoded, {"2018-01-10"})
    assert meta["passed"] and parsed.iloc[0].side == 1
    encoded.loc[0, "side"] = "1.1"
    _, meta = mc_entries_from_strings(encoded, {"2018-01-10"})
    assert not meta["passed"]
    duplicate = pd.concat([sample, sample.iloc[:1]], ignore_index=True)
    _, meta = mc_entries_from_strings(duplicate, {"2018-01-10"})
    assert not meta["passed"] and meta["duplicate_design_entry_source_row_ids"] == [0, 2]
    excluded = pd.DataFrame([dict(date="2018-01-11", side="UNREAD", entry="UNREAD", t_in="UNREAD")])
    _, meta = mc_entries_from_strings(excluded, {"2018-01-10"})
    assert meta["passed"] and meta["excluded_design_entry_date_rows"][0]["source_row_id"] == 0
    assert mc_minute("08:46", "2018-01-10") == 526
    try: mc_minute("2018-01-11 08:46:00", "2018-01-10")
    except ValueError: pass
    else: raise AssertionError("MCdateidentityfailureaccepted")
    empty = pd.DataFrame(columns=EVENT_COLUMNS)
    assert len(summaries(empty)) == 54
    assert not gate(empty, pd.DataFrame({"unresolved_scan": [False]}), {"passed": True})["passed"]
    assert information_clock("2018-01-10", 526)["available_at"] == information_clock("2018-01-10", 526)["first_fill_interval_start"]
    return dict(passed=True, real_prices_or_MC_or_returns_read=False, stopped_engine_called=False,
        checks=["literalHOLplussharedcalendar", "pairedstopnearerextreme/tie/worsegap", "20STORED390minuteRTHranges",
            "earliest526andstrictpre845disarm/touch", "missingcausalprefixveto", "15minuteactualflowaliases/totals/closes",
            "whole-daystrictdisagreementdrop;neutralKNOWN/invalidUNKNOWN_KEEP", "fixedrawOPENj900andheldgapretention",
            "MCentry-onlystrings/datebeforeconversion/futurepoison", "MCclock/dateidentity/integer-sideencoding/duplicateIDs/exclusions", "zeroeventsummary/gate",
            "idealizedinformationclock", "lastentry870not871", "aggregateflow/zerominute/knownneutral",
            "normal-literalholiday/weekendreferenceveto", "19to20backstopthenmissing511veto",
            "discardednormalreference20storelineageflag", "failedentryparitynevercallsrawattachment",
            "exit900postopenHLCnotheldcoverage"], script_sha256=sha(ROOT / SCRIPT), runtime_versions=runtime_versions())


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--phase", required=True, choices=("fixtures", "gross")); parser.add_argument("--prereg")
    args = parser.parse_args()
    if args.phase == "fixtures":
        result = synthetic_checks(); dump_once(OUT / f"synthetic_checks_{result['script_sha256'][:12]}.json", result)
    else:
        if not args.prereg: parser.error("Grossrequirescommitted--prereg")
        result = gross(args.prereg)
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__": main()
