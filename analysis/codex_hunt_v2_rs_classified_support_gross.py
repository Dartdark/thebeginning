"""H04: literal RS parent ENTRY/source admission, then conditional raw gross only.

Imports never load prices, OF, caches or MC rows.  No protective/stopped/account
engine or original ffilled RS research module is called.  Raw OPEN541->CLOSE900
arithmetic is reachable only after ALL source/reference/prefix/held and MC ENTRY
admission gates pass.  Failed admission preserves0returns/0grossscreens.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import fcntl
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import traceback
from types import SimpleNamespace
import warnings

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "analysis/codex_hunt_v2_rs_classified_support_gross.py"
PLAN = "agents/codex/plans/hunt_v2_rs_classified_support.md"
EVIDENCE = "agents/codex/evidence/hunt_v2_next_new_input.md"
NOTE = "agents/codex/research/hunt_v2_next_new_input.md"
OUT = ROOT / "analysis/outputs/codex_hunt_v2_rs_classified_support"
SOURCE_REF = "7f0800ffc04d56bd878750369a4abc2316ee01d8"
ARCHIVE_DIR = "agents/codex/inputs/hunt_v2_rs_classified_support"
PARENT_ARCHIVE = ARCHIVE_DIR + "/NQ_Relative_Strength.source.txt"
ORIGINAL_ARCHIVE = ARCHIVE_DIR + "/RelStrength_v3.source.txt"
SOURCE_MANIFEST = ARCHIVE_DIR + "/source_manifest.json"
PARENT_SHA = "20882cb3486ccbd60801572fa72f984161d408b89bc1621142e131de86292ffc"
ORIGINAL_SHA = "d819039cd0aedb33aa730f4b3b723adcc3169d10f4e9fa57c351e4652dc79b61"
WARMUP = "agents/codex/inputs/ob_v2_bench/NQ_1min_2017.csv"
MC = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute Relative Strength.xlsx"
YEARS = tuple(range(2018, 2023))
ALL_YEARS = (2017, *YEARS)
NATIVE_FIELDS = ("open", "high", "low", "close", "volume")
OF_FIELDS = (*NATIVE_FIELDS, "upvol", "downvol")
ALPHA, WARMUP_UPDATES, ZMIN = 2 / (20 * 390 + 1), 1950, 1.25
DECISION_J, ENTRY_J, EXIT_J = 540, 541, 900
FLOW_FIRST_J, FLOW_LAST_J = 525, 539
RT_COST, HURDLE, MIN_KEPT, KNOWN_MIN, PARITY_MIN = 2.24, 4.48, 100, .90, .90
sys.path.insert(0, str(ROOT / "analysis"))
from codex_hunt_v2_ldf_delta import (csv_once, dump_once, runtime_versions, sha,
    tstat, utcnow, valid_ohlcv, validate_metadata_keys)
from codex_hunt_v2_swing_opening_gross import opening_state
from grid24 import Grid24, jof
from codex_s03_calendar import calendar_status
from replica import is_early_close


def committed(ref, name):
    return subprocess.check_output(["git", "show", f"{ref}:{name}"], cwd=ROOT)


def source_holidays(text):
    return {int(v) + 19000000 for v in re.findall(r"Hol(?:Full|Early)\[[0-9]+\]\s*=\s*([0-9]{7})", text)}


def allowed_entry(date, holidays):
    day = pd.Timestamp(date)
    return (int(day.strftime("%Y%m%d")) not in holidays and calendar_status(day)["kind"] == "normal"
        and day.dayofweek < 5 and not is_early_close(day))


def read_audited(paths, fields, source):
    """Retain original IDs for every duplicate; no conflict is admitted to gross."""
    parts = []
    for name in paths:
        part = pd.read_csv(name, usecols=["date", "time", *fields])
        part["source_path"] = str(Path(name).relative_to(ROOT))
        part["source_row_id"] = np.arange(len(part)) + 2
        parts.append(part)
    frame = pd.concat(parts, ignore_index=True)
    duplicated = frame.duplicated(["date", "time"], keep=False)
    duplicate_rows = frame.loc[duplicated].copy()
    groups = duplicate_rows.groupby(["date", "time"])[list(fields)].nunique(dropna=False)
    conflicts = groups.gt(1).any(axis=1)
    conflict_keys = set(conflicts[conflicts].index.tolist())
    duplicate_counts = duplicate_rows.groupby(["date", "time"]).size()
    identical_excess = sum(int(count) - 1 for key, count in duplicate_counts.items() if key not in conflict_keys)
    conflicting_excess = sum(int(count) - 1 for key, count in duplicate_counts.items() if key in conflict_keys)
    duplicate_rows["conflicting_key"] = [(d, t) in conflict_keys for d, t in zip(duplicate_rows.date, duplicate_rows.time)]
    unique = frame.drop_duplicates(["date", "time"], keep="first").sort_values(["date", "time"])
    values = unique[list(fields)].to_numpy(float)
    validity = valid_ohlcv(*(unique[c].to_numpy(float) for c in NATIVE_FIELDS))
    audit = dict(source=source, total_source_rows=len(frame), unique_rows=len(unique),
        duplicate_excess_rows=int(duplicated.sum() - len(groups)),
        identical_duplicate_excess_rows=identical_excess, conflicting_duplicate_excess_rows=conflicting_excess,
        conflicting_duplicate_keys=int(conflicts.sum()), invalid_unique_OHLCV_rows=int((~validity).sum()),
        source_IDs_retained_for_all_duplicate_rows=True, no_duplicate_conflict_used_for_gross=not bool(conflicts.any()),
        finite_selected_numeric_cells=int(np.isfinite(values).sum()))
    return unique, audit, duplicate_rows


@dataclass(frozen=True)
class NativeAdapter:
    instrument: str

    @property
    def paths(self):
        if self.instrument == "NQ":
            return [str(ROOT / WARMUP), *[str(ROOT / f"data/NQ_1min_{y}.csv") for y in YEARS]]
        if self.instrument == "ES":
            return [str(ROOT / f"data/ES_1min_{y}.csv") for y in ALL_YEARS]
        raise ValueError("Only fixed NQ/ES source allowlists are permitted.")

    def build(self):
        frame, audit, duplicates = read_audited(self.paths, NATIVE_FIELDS, self.instrument)
        cache = OUT / "cache" / self.instrument
        cache.mkdir(parents=True, exist_ok=True)
        for name in self.paths:
            path = Path(name); link = cache / f"day_{path.stem[-4:]}.csv"
            if link.is_symlink():
                if link.resolve() != path.resolve(): raise ValueError("Unexpected grid symlink source.")
            elif link.exists(): raise ValueError("Unexpected nonlink cache source.")
            else: link.symlink_to(path)
        if {p.name for p in cache.glob("*.csv")} != {f"day_{y}.csv" for y in ALL_YEARS}:
            raise ValueError("Unbound source/year exists in isolated grid cache.")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            grid = Grid24(str(cache / "day_*.csv"), night_pattern="")
        if pd.DatetimeIndex(grid.ts).year.min() != 2017 or pd.DatetimeIndex(grid.ts).year.max() != 2022:
            raise ValueError("Grid crossed explicit2017--22 input scope.")
        rows, cols = np.searchsorted(grid.dates, frame.date.to_numpy()), jof(frame.time.to_numpy())
        observed = np.zeros((grid.D, 1440), bool); observed[rows, cols] = True
        for field, attr in zip(NATIVE_FIELDS, ("o", "h", "l", "c", "v")):
            if not np.allclose(getattr(grid, attr)[rows, cols], frame[field].to_numpy(float), equal_nan=True):
                raise ValueError("Shared Grid24 differs from audited first-source values:" + self.instrument + field)
        return grid, observed, audit, duplicates


def align_es(native, es, observed):
    arrays = {name: np.full((native.D, 1440), np.nan) for name in ("o", "h", "l", "c", "v")}
    result_observed = np.zeros((native.D, 1440), bool)
    source_rows = {int(day): row for row, day in enumerate(es.dates)}
    for row, day in enumerate(native.dates):
        k = source_rows.get(int(day))
        if k is None: continue
        for name in arrays: arrays[name][row] = getattr(es, name)[k]
        result_observed[row] = observed[k]
    return SimpleNamespace(**arrays), result_observed


def flow_grid(paths, grid):
    frame, audit, duplicates = read_audited(paths, OF_FIELDS, "OF_ET")
    source_date = pd.to_datetime(frame.date.astype(str), format="%Y%m%d")
    native_clock = source_date + pd.to_timedelta(jof(frame.time.to_numpy()), unit="m") - pd.Timedelta(hours=1)
    dates = native_clock.dt.strftime("%Y%m%d").astype(int).to_numpy()
    rows = np.searchsorted(grid.dates, dates)
    inside = (rows < grid.D) & (grid.dates[np.minimum(rows, grid.D - 1)] == dates)
    cols = (native_clock.dt.hour * 60 + native_clock.dt.minute).to_numpy()
    result = {}
    for field in OF_FIELDS:
        values = np.full((grid.D, 1440), np.nan)
        values[rows[inside], cols[inside]] = frame[field].to_numpy(float)[inside]
        result[field] = values
    audit.update(source_clock="ET close labels minus60minutes; both US zones share DST change dates",
        historical_receipt_verified=False, rows_outside_native_calendar=int((~inside).sum()))
    return result, audit, duplicates


def feature_state(side, native, flow):
    same_window = opening_state(native, flow)
    delta, known = same_window["opening_delta"], same_window["flow_known"]
    p, p_known = same_window["opening_price_move"], same_window["opening_price_move"] is not None
    return dict(flow_known=known, flow_delta=delta, flow_known_neutral=bool(known and delta == 0),
        flow_unknown_reason=same_window["flow_unknown_reason"], keep_FLOW15=not (known and side * delta < 0),
        price_known=p_known, price_move=p, keep_PRICE15=not (p_known and side * p < 0),
        valid_source_minutes=same_window["valid_source_minutes"],
        source_alias_mismatch_minutes=same_window["source_alias_mismatch_minutes"],
        native_total_mismatch_minutes=same_window["native_total_mismatch_minutes"],
        source_close_mismatch_minutes=same_window["source_close_mismatch_minutes"])


def information_clock(day):
    day = pd.Timestamp(day).normalize()
    at = lambda j: (day + pd.Timedelta(minutes=j)).tz_localize("America/Chicago").isoformat()
    return dict(event_time=at(FLOW_LAST_J), available_at=at(DECISION_J), decision_time=at(DECISION_J),
        first_fill_interval_start=at(DECISION_J), first_fill_interval_end=at(ENTRY_J),
        availability_allowance_minutes=1, actual_receipt_verified=False,
        source_clock="CT nativeclose/ET OFclose-minus60; zero alternative offsets; nextbarOPEN541")


def finalize_store(session, number):
    js = session["js"]
    complete = (js == list(range(511, 901)) and all(session["valid"]) and np.isfinite(session["hi"])
        and np.isfinite(session["lo"]) and session["hi"] >= session["lo"])
    return dict(store_id=number, date=session["date"], source_DayOK=session["dayok"],
        range_value=float(session["hi"] - session["lo"]), observed_RTH_bars=len(js),
        missing_RTH_minutes=390 - len(set(js)), invalid_RTH_bars=int(len(js) - sum(session["valid"])),
        first_observed_RTH_j=min(js) if js else None, last_observed_RTH_j=max(js) if js else None,
        reference_complete=bool(complete), stored_from_literal_NewRTH=True)


def parent_entries(grid, observed, es, es_observed, flow, holidays):
    """Literal observed Data1 state; invalid/missing references flagged, never repaired."""
    valid_n = valid_ohlcv(grid.o, grid.h, grid.l, grid.c, grid.v)
    valid_e = valid_ohlcv(es.o, es.h, es.l, es.c, es.v)
    history, stores, events, days = [], [], [], []
    cov = v1 = v2 = beta = residual = 0.0; nest = 0
    prev = None; session = None; nba = 0; anchor_n = anchor_e = np.nan
    ewma_fault_days = []
    for row, timestamp in enumerate(pd.DatetimeIndex(grid.ts)):
        date = timestamp.date().isoformat(); date_id = int(grid.dates[row])
        if date_id < 20170901: continue
        literal_ok = date_id not in holidays
        shared_ok = allowed_entry(timestamp, holidays)
        expected_session = bool(literal_ok and timestamp.dayofweek < 5)
        day_faults_before = ewma_fault_days.copy()
        actual_js = np.flatnonzero(observed[row])
        decision = None; first_rth = None; anchor_expected = False
        for j in actual_js:
            j = int(j); rth = 510 < j <= 900
            new_rth = bool(rth and (prev is None or prev[0] != row or prev[1] <= 510 or prev[1] > 900))
            if rth:
                if new_rth:
                    if session is not None and session["dayok"]:
                        store = finalize_store(session, len(stores)); stores.append(store); history.append(store)
                    avg = float(np.mean([item["range_value"] for item in history[-20:]])) if history else np.nan
                    session = dict(date=date, dayok=literal_ok, hi=grid.h[row, j], lo=grid.l[row, j],
                        js=[j], valid=[bool(valid_n[row, j])])
                    anchor_n = grid.c[prev] if prev is not None else np.nan
                    anchor_e = es.c[prev] if prev is not None else np.nan
                    anchor_expected = bool(prev is not None and prev == (row, 510) and valid_n[prev] and valid_e[prev] and es_observed[prev])
                    nba = 0; first_rth = j
                else:
                    session["hi"] = np.maximum(session["hi"], grid.h[row, j])
                    session["lo"] = np.minimum(session["lo"], grid.l[row, j])
                    session["js"].append(j); session["valid"].append(bool(valid_n[row, j]))
                if np.isfinite(anchor_n) and anchor_n > 0: nba += 1
                previous_n = grid.c[prev] if prev is not None else np.nan
                previous_e = es.c[prev] if prev is not None else np.nan
                current_n, current_e = grid.c[row, j], es.c[row, j]
                pair_positive = all(np.isfinite(x) and x > 0 for x in (previous_n, previous_e, current_n, current_e))
                if literal_ok and pair_positive:
                    x, y = 10000 * np.log(current_n / previous_n), 10000 * np.log(current_e / previous_e)
                    if nest == 0: cov, v1, v2 = x * y, x * x, y * y
                    else:
                        cov += ALPHA * (x * y - cov); v1 += ALPHA * (x * x - v1); v2 += ALPHA * (y * y - v2)
                    nest += 1
                    if v1 > 0 and v2 > 0:
                        beta = cov / v2; residual = v1 - 2 * beta * cov + beta * beta * v2
                if j == DECISION_J:
                    reference = history[-20:]
                    prefix_bad_n = int((~valid_n[row, 510:DECISION_J + 1]).sum())
                    prefix_bad_e = int((~valid_e[row, 510:DECISION_J + 1]).sum())
                    current_ewma_fault = bool(expected_session and (prefix_bad_n or prefix_bad_e or first_rth != 511))
                    range_bad = [item["store_id"] for item in reference if not item["reference_complete"]]
                    ref_bad = bool(day_faults_before or current_ewma_fault or range_bad or not anchor_expected)
                    z = None
                    if literal_ok and nba >= 1 and nest >= WARMUP_UPDATES and residual > 0 and all(np.isfinite(x) and x > 0 for x in (anchor_n, anchor_e, current_e, current_n)):
                        rel = 10000 * np.log(current_n / anchor_n) - beta * 10000 * np.log(current_e / anchor_e)
                        z = float(rel / np.sqrt(residual * nba))
                    side = 1 if z is not None and z >= ZMIN else -1 if z is not None and z <= -ZMIN else 0
                    decision = dict(z=z, side=side, NEst=nest, NBA=nba, beta=float(beta), residual=float(residual),
                        anchor_n=float(anchor_n), anchor_e=float(anchor_e), anchor_expected=anchor_expected,
                        first_observed_RTH_j=first_rth, prefix_invalid_native=prefix_bad_n, prefix_invalid_ES=prefix_bad_e,
                        ewma_lineage_unresolved=bool(day_faults_before or current_ewma_fault),
                        ewma_prior_fault_dates=json.dumps(day_faults_before), reference_unresolved=ref_bad,
                        stored_reference_ids=json.dumps([x["store_id"] for x in reference]),
                        stored_reference_dates=json.dumps([x["date"] for x in reference]),
                        unresolved_stored_reference_ids=json.dumps(range_bad), average_range20=avg,
                        stored_reference_count=len(reference))
            prev = (row, j)
        # Full-day gaps contaminate all later EWMA references indefinitely. No20day reset.
        full_native_bad = int((~valid_n[row, 511:901]).sum())
        full_ES_bad = int((~valid_e[row, 511:901]).sum())
        if expected_session and (full_native_bad or full_ES_bad or first_rth != 511 or not anchor_expected):
            ewma_fault_days.append(date)
        ready = bool((decision is not None and decision["NEst"] >= WARMUP_UPDATES) or (decision is None and nest >= WARMUP_UPDATES))
        eligible = bool(timestamp.year in YEARS and shared_ok and ready)
        prefix_unresolved = bool(eligible and (decision is None or not decision["anchor_expected"]
            or decision["prefix_invalid_native"] or decision["prefix_invalid_ES"] or decision["NBA"] != 30))
        day = dict(date=date, year=timestamp.year, source_DayOK=literal_ok, shared_calendar_kind=calendar_status(timestamp)["kind"],
            allowed_calendar=shared_ok, comparison_eligible=eligible, warmup_ready=ready, first_observed_RTH_j=first_rth,
            observed_native_RTH_bars=int(observed[row, 511:901].sum()), full_native_invalid_RTH=full_native_bad,
            full_ES_invalid_RTH=full_ES_bad, decision_present=decision is not None,
            prefix_unresolved=prefix_unresolved, entry_unresolved=False, held_unresolved=False,
            reference_unresolved=bool(eligible and decision is not None and decision["reference_unresolved"]),
            disposition="outside_design_or_calendar_or_warmup")
        if decision is not None:
            for key in ("z", "side", "NEst", "NBA", "beta", "residual", "anchor_n", "anchor_e", "anchor_expected",
                "prefix_invalid_native", "prefix_invalid_ES", "ewma_lineage_unresolved", "ewma_prior_fault_dates",
                "stored_reference_ids", "stored_reference_dates", "unresolved_stored_reference_ids", "average_range20", "stored_reference_count"):
                day["decision_" + key] = decision[key]
        if eligible:
            day["disposition"] = "missing_decision" if decision is None else "no_RS_threshold" if decision["side"] == 0 else "parent_signal"
        if eligible and decision is not None and decision["side"]:
            entry_ok = bool(observed[row, ENTRY_J] and valid_n[row, ENTRY_J])
            day["entry_unresolved"] = not entry_ok
            held_bad = int((~valid_n[row, ENTRY_J:EXIT_J + 1]).sum())
            day["held_unresolved"] = held_bad > 0
            if entry_ok:
                native = {name: getattr(grid, attr)[row, FLOW_FIRST_J:FLOW_LAST_J + 1]
                    for name, attr in zip(NATIVE_FIELDS, ("o", "h", "l", "c", "v"))}
                source = {name: values[row, FLOW_FIRST_J:FLOW_LAST_J + 1] for name, values in flow.items()}
                state = feature_state(decision["side"], native, source)
                own_known = bool(valid_n[row, 510] and valid_n[row, DECISION_J])
                own = float(grid.c[row, DECISION_J] - grid.c[row, 510]) if own_known else None
                events.append(dict(date=date, year=timestamp.year, event_id=f"RS_RAW_{date_id}_01", entry_j=ENTRY_J,
                    entry=float(grid.o[row, ENTRY_J]), **decision, **state, own_opening_known=own_known,
                    own_opening_move=own, own_opening_sign=int(np.sign(own)) if own_known else None,
                    unresolved_held_path=held_bad > 0, invalid_held_minutes=held_bad, **information_clock(timestamp)))
        days.append(day)
    event_columns = ("date", "year", "event_id", "entry_j", "entry", "side", "reference_unresolved",
        "flow_known", "keep_FLOW15", "keep_PRICE15", "unresolved_held_path", "invalid_held_minutes")
    events_frame = pd.DataFrame(events) if events else pd.DataFrame(columns=event_columns)
    return events_frame, pd.DataFrame(days), pd.DataFrame(stores)


def entry_parity(events, calendar, mc, metadata):
    selected = events.copy(); hits, matches, used = [], 0, set()
    for p in selected.itertuples():
        possible = mc[(mc.date == p.date) & (mc.side == p.side)]
        hit = None
        for k, row in possible.iterrows():
            clock_ok = pd.isna(row.entry_j) or row.entry_j == ENTRY_J
            if k not in used and abs(row.entry - p.entry) <= .25 + 1e-9 and clock_ok:
                hit = k; break
        if hit is not None: matches += 1; used.add(hit)
        hits.append(dict(parent_event_id=p.event_id, date=p.date, side=p.side, parent_entry=p.entry,
            matched_MC=hit is not None, MC_source_row_id=int(mc.loc[hit, "source_row_id"]) if hit is not None else None))
    mc = mc.copy(); mc["matched_parent"] = [k in used for k in mc.index]
    precision, recall = matches / len(events) if len(events) else None, matches / len(mc) if len(mc) else None
    meta_pass = bool(metadata["passed"])
    audit = dict(parent_entries=len(events), MC_entries=len(mc), matches=matches,
        parent_to_MC_fraction=precision, MC_to_parent_fraction=recall, threshold=PARITY_MIN,
        passed=bool(meta_pass and precision is not None and recall is not None and min(precision, recall) >= PARITY_MIN),
        entry_price_tolerance=.25, present_MC_clock_must_equal=ENTRY_J, timestamp_offsets_tested=[0],
        missing_MC_clock_is_unverified_not_invented=True, MC_metadata=metadata,
        MC_exit_price_gross_net_fees_interpreted=False)
    return audit, pd.DataFrame(hits), mc


def admission_gate(entries, calendar, parity, source_audits):
    conflicts = sum(a["conflicting_duplicate_keys"] for a in source_audits)
    refs = int(entries.reference_unresolved.astype(bool).sum()) if len(entries) else 0
    ref_days = int(calendar.reference_unresolved.astype(bool).sum()) if len(calendar) else 0
    prefix = int(calendar.prefix_unresolved.astype(bool).sum()) if len(calendar) else 0
    entry = int(calendar.entry_unresolved.astype(bool).sum()) if len(calendar) else 0
    held = int(calendar.held_unresolved.astype(bool).sum()) if len(calendar) else 0
    passed = bool(parity["passed"] and conflicts == 0 and ref_days == 0 and refs == 0 and prefix == 0 and entry == 0 and held == 0)
    return dict(phase="pre_gross", passed=passed, MC_entry_parity_pass=parity["passed"],
        conflicting_source_keys=conflicts, unresolved_reference_events=refs,
        unresolved_reference_decision_days=ref_days, unresolved_prefix_days=prefix,
        unresolved_entry_days=entry, unresolved_held_event_days=held, parent_entries=len(entries),
        raw_returns_calculated=False, gross_screen_runs=0, counted_evaluations=0,
        stopped_returns_calculated=False, validation_run=False, book_bench_run=False,
        reason="ALL source and ENTRY gates passed" if passed else "Frozen source/ENTRY admission failed; no raw endpoints or economic verdict")


def attach_raw(grid, entries):
    rows = {pd.Timestamp(day).date().isoformat(): k for k, day in enumerate(grid.ts)}
    result = entries.copy()
    closes = np.array([grid.c[rows[day], EXIT_J] for day in entries.date], dtype=float)
    if not np.isfinite(closes).all() or (closes <= 0).any(): raise ValueError("Admitted raw CLOSE900 endpoint missing.")
    result["raw_exit_j"] = EXIT_J; result["raw_exit_close"] = closes
    result["gross_points"] = (closes - result.entry.to_numpy(float)) * result.side.to_numpy(int)
    result["gross_MNQ"] = result.gross_points * 2.0
    return result


def summaries(events):
    rows = []
    for model, keep in (("BASE", np.ones(len(events), bool)), ("FLOW15", events.keep_FLOW15.astype(bool).to_numpy()),
        ("PRICE15", events.keep_PRICE15.astype(bool).to_numpy())):
        for group, mask in (("kept", keep), ("removed", ~keep)):
            frame = events.loc[mask]
            for period in ("2018-22", *map(str, YEARS)):
                period_frame = frame if period == "2018-22" else frame[frame.year == int(period)]
                for side in ("both", "long", "short"):
                    part = period_frame if side == "both" else period_frame[period_frame.side == (1 if side == "long" else -1)]
                    values = part.gross_MNQ.to_numpy(float)
                    sd = float(values.std(ddof=1)) if len(values) > 1 else None
                    rows.append(dict(model=model, subset=group, period=period, side=side, events=len(values),
                        total=float(values.sum()), mean=float(values.mean()) if len(values) else None,
                        SD=sd, SE=sd / np.sqrt(len(values)) if sd is not None else None, t=tstat(values)))
    return pd.DataFrame(rows)


def raw_after_admission(grid, entries, admission, attach=attach_raw):
    if not admission["passed"]: return entries.copy(), admission, None
    events = attach(grid, entries)
    kept = events[events.keep_FLOW15.astype(bool)]
    known_fraction = float(events.flow_known.astype(bool).mean()) if len(events) else None
    mean = float(kept.gross_MNQ.mean()) if len(kept) else None
    passed = bool(len(kept) >= MIN_KEPT and known_fraction is not None and known_fraction >= KNOWN_MIN
        and mean is not None and mean >= HURDLE)
    gate = dict(admission, phase="raw_gross", passed=passed, source_entry_admission_pass=True,
        raw_returns_calculated=True, gross_screen_runs=1, primary="FLOW15", kept_events=len(kept),
        base_events=len(events), known_flow_fraction=known_fraction, minimum_known_fraction=KNOWN_MIN,
        minimum_kept_events=MIN_KEPT, primary_gross_mean_MNQ=mean, primary_gross_t=tstat(kept.gross_MNQ),
        native_roundtrip_cost_MNQ=RT_COST, gross_hurdle_MNQ=HURDLE,
        costs_subtracted=False, stops_targets_simulated=False,
        reason="Gross PASS only; stopped design remains separately gated" if passed else "Frozen gross gate failed; close H04 before stopped/validation/book tests")
    return events, gate, summaries(events)


def verify_before_data(prereg):
    if subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() != "codex/work":
        raise ValueError("H04 must run on codex/work.")
    subprocess.check_call(["git", "merge-base", "--is-ancestor", prereg, "HEAD"], cwd=ROOT)
    dependencies = [SCRIPT, "analysis/codex_hunt_v2_rs_mc_entry_xml.py", "analysis/codex_hunt_v2_swing_opening_gross.py",
        "analysis/codex_hunt_v2_ldf_delta.py", "analysis/grid24.py", "analysis/codex_s03_calendar.py", "analysis/replica.py",
        "agents/codex/RESEARCH_CONTROLS.md"]
    required = [PLAN, EVIDENCE, NOTE, PARENT_ARCHIVE, ORIGINAL_ARCHIVE, SOURCE_MANIFEST, *dependencies]
    for name in required:
        raw = (ROOT / name).read_bytes()
        if committed("HEAD", name) != raw or committed(prereg, name) != raw:
            raise ValueError("Freeze all code/plan/source dependencies before data:" + name)
    if sha(ROOT / PARENT_ARCHIVE) != PARENT_SHA or sha(ROOT / ORIGINAL_ARCHIVE) != ORIGINAL_SHA:
        raise ValueError("Pinned parent/original source archive differs.")
    for directory in (ROOT / "analysis/outputs").glob("codex_hunt_v2_rs_classified_support*"):
        if any((directory / name).exists() for name in ("gross_verified_execution.json", "pre_gross_verified_execution.json", "gross_attempt.json")):
            raise ValueError("H04 attempt/completion already retained; no alternate-directory rerun.")
    native, es = NativeAdapter("NQ").paths, NativeAdapter("ES").paths
    of = [str(path) for year in YEARS for path in sorted((ROOT / "data").glob(f"OF_1min_{year}_*.csv"))]
    if not all(any(f"OF_1min_{year}_" in path for path in of) for year in YEARS): raise FileNotFoundError("Missing admitted OF year.")
    input_paths = [*native, *es, *of, str(ROOT / MC)]
    if not all(Path(name).is_file() for name in input_paths): raise FileNotFoundError("Frozen H04 input missing.")
    hashes = {name: sha(ROOT / name) for name in required}
    inventory = []
    for name in input_paths:
        path = Path(name); relative = str(path.relative_to(ROOT))
        hashes[relative] = sha(path)
        item = dict(path=relative, bytes=path.stat().st_size, sha256=hashes[relative])
        if path.suffix == ".csv":
            item["header"] = path.open("rb").readline().decode("utf-8").rstrip("\r\n")
        inventory.append(item)
    return dict(prereg=prereg, implementation_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        hashes=hashes, inventory=inventory, native_paths=native, ES_paths=es, OF_paths=of,
        source_ref=SOURCE_REF, versions=runtime_versions(), metadata_only_before_this_binding=True)


def metadata_audit(binding):
    result = []
    for name in [*binding["native_paths"], *binding["ES_paths"], *binding["OF_paths"]]:
        path = Path(name)
        frame = pd.read_csv(path, usecols=["date", "time"])
        year = int(path.name.split("_")[-2] if path.name.startswith("OF_") else path.stem[-4:])
        validate_metadata_keys(frame, year, path.name)
        result.append(dict(path=str(path.relative_to(ROOT)), rows=len(frame), min_date=int(frame.date.min()),
            max_date=int(frame.date.max()), duplicate_metadata_keys=int(frame.duplicated(["date", "time"]).sum())))
    return result


@contextmanager
def execution_lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "gross.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB); yield


def source_and_entry_phase(binding, stage):
    """All possible caught format/implementation failures precede raw attachment."""
    stage["name"] = "source_metadata_audit"
    binding["metadata"] = metadata_audit(binding)
    stage["name"] = "native_NQ_audit_and_grid"
    native, observed, n_audit, n_duplicates = NativeAdapter("NQ").build()
    stage["name"] = "ES_audit_grid_and_alignment"
    es_grid, es_present, e_audit, e_duplicates = NativeAdapter("ES").build()
    es, e_observed = align_es(native, es_grid, es_present)
    stage["name"] = "classified_OF_source_audit"
    flow, f_audit, f_duplicates = flow_grid(binding["OF_paths"], native)
    stage["name"] = "literal_parent_signal_and_ENTRY_metadata"
    holidays = source_holidays((ROOT / PARENT_ARCHIVE).read_text())
    entries, calendar, stores = parent_entries(native, observed, es, e_observed, flow, holidays)
    stage["name"] = "raw_XML_selected_MC_ENTRY_metadata"
    from codex_hunt_v2_rs_mc_entry_xml import read_entry_metadata
    dates = set(calendar.loc[calendar.comparison_eligible.astype(bool), "date"])
    mc, mc_meta = read_entry_metadata(ROOT / MC, dates)
    stage["name"] = "MC_ENTRY_parity"
    parity, matches, parsed_mc = entry_parity(entries, calendar, mc, mc_meta)
    stage["name"] = "all_source_and_ENTRY_admission"
    source_audits = [n_audit, e_audit, f_audit]
    admission = admission_gate(entries, calendar, parity, source_audits)
    return (native, entries, calendar, stores, parity, matches, parsed_mc, admission,
        n_audit, e_audit, f_audit, n_duplicates, e_duplicates, f_duplicates)


def failure_decision(stage, error):
    return dict(phase="pre_gross", passed=False, status="SOURCE_FORMAT_OR_IMPLEMENTATION_BLOCKED",
        stage=stage, exception_type=type(error).__name__, exception_message=str(error),
        raw_returns_calculated=False, gross_screen_runs=0, counted_evaluations=0,
        stopped_returns_calculated=False, validation_run=False, account_tests_run=False,
        reason="Exception BEFORE raw attachment; source/format/implementation block, not strategy profitability or alpha rejection",
        retry_authorized=False, prior_attempt_preserved=True)


def preserve_pre_raw_exception(binding, started, stage, error, trace):
    decision = failure_decision(stage, error)
    hashes_now = {name: sha(ROOT / name) for name in binding["hashes"]}
    bindings_unchanged = hashes_now == binding["hashes"]
    dump_once(OUT / "pre_gross_failure_trace.json", dict(**decision, traceback=trace,
        bound_files_unchanged=bindings_unchanged, observed_bound_sha256=hashes_now))
    dump_once(OUT / "gross_input_binding.json", binding)
    dump_once(OUT / "pre_gross_gate.json", decision)
    dump_once(OUT / "gross_summary_status.json", dict(status=decision["status"], raw_returns_calculated=False,
        interpretation="N/A; caught exception is not an economic rejection; no automatic retry"))
    if not bindings_unchanged:
        raise ValueError("Bound source changed during blocked pre-raw phase; retained failure is unverified.") from error
    names = ("gross_attempt.json", "gross_pre_rows_binding.json", "pre_gross_failure_trace.json",
        "gross_input_binding.json", "pre_gross_gate.json", "gross_summary_status.json")
    marker = dict(started_utc=started, completed_utc=utcnow(), phase="pre_gross", passed=False,
        status=decision["status"], stage=stage, prereg=binding["prereg"],
        implementation_commit=binding["implementation_commit"], script_sha256=sha(ROOT / SCRIPT),
        artifacts_sha256={name: sha(OUT / name) for name in names}, raw_returns_calculated=False,
        gross_screen_runs=0, counted_evaluations=0, new_hypotheses=1,
        stopped_returns_calculated=False, MC_exit_or_profit_converted=False, validation_run=False,
        account_tests_run=False, exception_before_raw_attachment_verified=True, auto_retry_authorized=False)
    dump_once(OUT / "pre_gross_verified_execution.json", marker)
    return decision


def gross(prereg):
    with execution_lock():
        binding = verify_before_data(prereg); started = utcnow()
        dump_once(OUT / "gross_attempt.json", dict(started_utc=started, prereg=prereg,
            implementation_commit=binding["implementation_commit"], script_sha256=sha(ROOT / SCRIPT)))
        dump_once(OUT / "gross_pre_rows_binding.json", binding)
        stage = dict(name="source_and_ENTRY_phase_not_started")
        try:
            (native, entries, calendar, stores, parity, matches, parsed_mc, admission,
                n_audit, e_audit, f_audit, n_duplicates, e_duplicates, f_duplicates) = source_and_entry_phase(binding, stage)
        except Exception as error:
            return preserve_pre_raw_exception(binding, started, stage["name"], error, traceback.format_exc())
        # No exception catcher below this boundary can falsely claim0rawreturns.
        events, decision, summary = raw_after_admission(native, entries, admission)
        if binding["hashes"] != {name: sha(ROOT / name) for name in binding["hashes"]}:
            raise ValueError("Bound code/plan/input changed during H04.")
        names = ["gross_attempt.json", "gross_pre_rows_binding.json"]
        for name, frame in (("parent_entries.csv", entries), ("gross_calendar_audit.csv", calendar),
            ("gross_stored_reference_audit.csv", stores), ("gross_mc_entry_matches.csv", matches),
            ("gross_mc_entries_design_only.csv", parsed_mc), ("gross_native_duplicate_rows.csv", n_duplicates),
            ("gross_ES_duplicate_rows.csv", e_duplicates), ("gross_OF_duplicate_rows.csv", f_duplicates)):
            csv_once(OUT / name, frame); names.append(name)
        if decision["raw_returns_calculated"]:
            csv_once(OUT / "gross_events.csv", events); csv_once(OUT / "gross_summary.csv", summary)
            names += ["gross_events.csv", "gross_summary.csv"]
        else:
            dump_once(OUT / "gross_summary_status.json", dict(status="N/A: source/ENTRY admission failed before raw endpoint arithmetic", raw_returns_calculated=False))
            names.append("gross_summary_status.json")
        data_audit = dict(native=n_audit, ES=e_audit, OF=f_audit, no2017_performance=True, no2023plus_inputs=True,
            no_forward_fill=True, no_shared_pickles=True, literal_source_DayOK_controls_state=True,
            shared_calendar_controls_entries_only=True, EWMA_lineage_faults_expire=False,
            stored_range_faults_expire_only_when_leaving_literal20buffer=True,
            parent_entries=len(entries), known_flow_entries=int(entries.flow_known.astype(bool).sum()) if len(entries) else 0,
            source_history="ObservedRTHNBA/EWMA firstpairinit alpha2/(20*390+1),1950updates; observedpriorcloseanchors;20storedRTHmeanranges",
            raw_returns_calculated=decision["raw_returns_calculated"], MNQ_quote_receipt_or_execution_verified=False,
            no_MC_exit_or_profit_conversion=True, input_schema_eras="nativeCTclose;OFETclose-minus60; retrospectivefeedreceiptunverified")
        manifest = dict(candidate_id="hunt_v2_H04_RS_CLASSIFIED_SUPPORT", prereg=prereg,
            implementation_commit=binding["implementation_commit"], script_sha256=sha(ROOT / SCRIPT), versions=runtime_versions(),
            information_clock="OFclose539+1assumedminuteavailable540;decision540;nativeOPEN541wall540;actualreceiptunverified",
            models=["REPLAY_BASE", "FLOW15", "PRICE15_unselectable", "DELAY_BASE_conditional", "DELAY_FLOW15_conditional"],
            raw_window="OPEN541->CLOSE900;nostop/notarget;onlyafterALLsourceandENTRYadmission",
            economic_evaluations=0, raw_returns_calculated=decision["raw_returns_calculated"],
            native_MNQ_cost_assumption=dict(commission_RT=1.24, adverse_market_stop_per_fill=.50, raw_RT=RT_COST, gross_hurdle=HURDLE),
            raw_costs_subtracted=False, stopped_or_delay_or_cost_stress_run=False,
            historical_validation_or_book_bench_or_placebos_or_MC_run=False, phase=decision["phase"])
        gate_name = "gross_gate.json" if decision["raw_returns_calculated"] else "pre_gross_gate.json"
        for name, value in (("gross_input_binding.json", binding), ("gross_entry_parity.json", parity),
            (gate_name, decision), ("gross_data_audit.json", data_audit), ("gross_run_manifest.json", manifest)):
            dump_once(OUT / name, value); names.append(name)
        marker = dict(started_utc=started, completed_utc=utcnow(), phase=decision["phase"], passed=decision["passed"],
            prereg=prereg, implementation_commit=binding["implementation_commit"], script_sha256=sha(ROOT / SCRIPT),
            artifacts_sha256={name: sha(OUT / name) for name in names}, raw_returns_calculated=decision["raw_returns_calculated"],
            gross_screen_runs=decision["gross_screen_runs"], counted_evaluations=0, new_hypotheses=1,
            stopped_returns_calculated=False, MC_exit_or_profit_converted=False, validation_run=False, account_tests_run=False)
        marker_name = "gross_verified_execution.json" if decision["raw_returns_calculated"] else "pre_gross_verified_execution.json"
        dump_once(OUT / marker_name, marker)
        return decision


def artificial_grid(dates):
    days = pd.DatetimeIndex(dates)
    shape = (len(days), 1440)
    arrays = {key: np.full(shape, np.nan) for key in ("o", "h", "l", "c", "v")}
    observed = np.zeros(shape, bool)
    for row in range(len(days)):
        js = np.arange(480, 916)
        close = 100 + row * .2 + .005 * (js - 480) + .01 * np.sin(js * .2 + row)
        arrays["o"][row, js] = close - .003; arrays["h"][row, js] = close + .03
        arrays["l"][row, js] = close - .03; arrays["c"][row, js] = close; arrays["v"][row, js] = 10
        observed[row, js] = True
    return SimpleNamespace(**arrays, ts=days.to_numpy(), dates=days.strftime("%Y%m%d").astype(int).to_numpy(), D=len(days)), observed


def synthetic_checks():
    checks = []
    assert ALPHA == 2 / 7801 and WARMUP_UPDATES == 1950 and ENTRY_J == 541 and EXIT_J == 900
    text = "HolFull[0] = 1180101; HolEarly[1] = 1181123;"
    assert source_holidays(text) == {20180101, 20181123}
    assert not allowed_entry("2018-11-23", source_holidays(text)) and not allowed_entry("2018-01-06", set())
    checks.append("literalHOLparsing;sharedentrycalendar;fixedEWMA1950andnativeclocks")
    native = {name: np.full(15, value) for name, value in zip(NATIVE_FIELDS, (100., 101., 99., 100., 10.))}
    flow = dict(native, volume=np.full(15, 7.), upvol=np.full(15, 7.), downvol=np.full(15, 3.))
    for side in (-1, 1):
        state = feature_state(side, native, flow)
        assert state["flow_known"] and state["keep_FLOW15"] == (side == 1) and state["keep_PRICE15"]
    flow["upvol"][0] = 6
    assert not feature_state(-1, native, flow)["flow_known"] and feature_state(-1, native, flow)["keep_FLOW15"]
    flow["upvol"][:] = 5; flow["volume"][:] = 5; flow["downvol"][:] = 5
    assert feature_state(-1, native, flow)["flow_known_neutral"] and feature_state(-1, native, flow)["keep_FLOW15"]
    checks.append("independentRSside*Dgate;neutralKEEP;invalidaliasUNKNOWNKEEP;fixedsamewindowpricecontrol")
    clock = information_clock("2018-01-02")
    assert clock["event_time"].startswith("2018-01-02T08:59") and clock["available_at"].startswith("2018-01-02T09:00")
    assert clock["first_fill_interval_end"].startswith("2018-01-02T09:01")
    assert information_clock("2018-07-02")["decision_time"].endswith("-05:00") and clock["decision_time"].endswith("-06:00")
    checks.append("featureevent/assumedavailability/decision/nextbarfillclockandDST")
    dates = pd.bdate_range("2017-09-01", periods=12)
    g, observed = artificial_grid(dates); e, ep = artificial_grid(dates)
    e.c = e.c * 2; e.o = e.o * 2; e.h = e.h * 2; e.l = e.l * 2
    flow_grid_values = {field: np.full((g.D, 1440), np.nan) for field in OF_FIELDS}
    entries, cal, stores = parent_entries(g, observed, e, ep, flow_grid_values, set())
    assert entries.empty and len(stores) == 11 and stores.reference_complete.all()
    assert cal.iloc[-1].warmup_ready and not cal.comparison_eligible.any()
    checks.append("literalobservedRTHstate;2017featureonly;storedrangeatnextNewRTH;1950warmup")
    # An eligible historical missing minute is never ffilled and lineage never expires.
    observed[2, 600] = False
    for field in ("o", "h", "l", "c", "v"): getattr(g, field)[2, 600] = np.nan
    _, _, faultstores = parent_entries(g, observed, e, ep, flow_grid_values, set())
    assert not faultstores.loc[faultstores.date == dates[2].date().isoformat(), "reference_complete"].iloc[0]
    checks.append("missingnativebarretainedinliteralstoredreference;noOHLCforwardfill")
    # Exact observed NBA and unbounded EWMA lineage on design dates, independent
    # of whether the synthetic residual happens to cross the trading threshold.
    dates = pd.bdate_range("2017-12-18", periods=35)
    g, observed = artificial_grid(dates); e, ep = artificial_grid(dates)
    for row in range(e.D):
        js = np.flatnonzero(ep[row])
        adjustment = .05 * np.sin(js * .37 + row * .6)
        e.c[row, js] += adjustment; e.o[row, js] += adjustment
        e.h[row, js] += adjustment; e.l[row, js] += adjustment
    flow_values = {field: np.full((g.D, 1440), np.nan) for field in OF_FIELDS}
    _, good_days, _ = parent_entries(g, observed, e, ep, flow_values, set())
    assert good_days.loc[good_days.decision_present, "decision_NBA"].eq(30).all()
    assert good_days.iloc[6].decision_NEst == 6 * 390 + 30
    missing_row = 3
    ep[missing_row, 600] = False
    for field in ("o", "h", "l", "c", "v"): getattr(e, field)[missing_row, 600] = np.nan
    _, bad_days, _ = parent_entries(g, observed, e, ep, flow_values, set())
    late = bad_days.iloc[-1]
    assert late.decision_ewma_lineage_unresolved and dates[missing_row].date().isoformat() in late.decision_ewma_prior_fault_dates
    assert late.decision_unresolved_stored_reference_ids == "[]"
    checks.append("exactobservedNBA30/NEstcounts;oneESgapretainsEWMAlineageafter20rangebufferreplacements")
    g, observed = artificial_grid(dates)
    clean_es, clean_ep = artificial_grid(dates)
    observed[missing_row, 510] = False
    for field in ("o", "h", "l", "c", "v"): getattr(g, field)[missing_row, 510] = np.nan
    _, anchor_days, _ = parent_entries(g, observed, clean_es, clean_ep, flow_values, set())
    assert anchor_days.iloc[missing_row].full_native_invalid_RTH == 0 and anchor_days.iloc[missing_row].full_ES_invalid_RTH == 0
    assert anchor_days.iloc[-1].decision_ewma_lineage_unresolved
    assert dates[missing_row].date().isoformat() in anchor_days.iloc[-1].decision_ewma_prior_fault_dates
    assert anchor_days.iloc[-1].decision_unresolved_stored_reference_ids == "[]"
    checks.append("missing830anchorwithcompleteRTHcontaminatesunboundedEWMAafter20rangereplacements")
    # Source admission must stop before ANY endpoint function is reached.
    empty = pd.DataFrame(columns=["reference_unresolved", "flow_known", "keep_FLOW15", "keep_PRICE15"])
    cal = pd.DataFrame([dict(reference_unresolved=False, prefix_unresolved=True, entry_unresolved=False, held_unresolved=False)])
    admission = admission_gate(empty, cal, dict(passed=False), [dict(conflicting_duplicate_keys=0)])
    def forbidden(*args): raise AssertionError("Endpoint arithmetic reached after source failure.")
    _, stopped, summary = raw_after_admission(None, empty, admission, attach=forbidden)
    assert not stopped["raw_returns_calculated"] and stopped["gross_screen_runs"] == 0 and summary is None
    checks.append("ALLsource/ENTRY/heldgatesbeforeanyrawendpoint;failure0returns0screens")
    cal = pd.DataFrame([dict(reference_unresolved=True, prefix_unresolved=False, entry_unresolved=False, held_unresolved=False)])
    noevent_ref = admission_gate(empty, cal, dict(passed=True), [dict(conflicting_duplicate_keys=0)])
    assert not noevent_ref["passed"] and noevent_ref["unresolved_reference_decision_days"] == 1
    checks.append("unresolvedreferenceonallotherwiseeligibledecisionsvetoesevensidezero/noentry")
    blocked = failure_decision("raw_XML_selected_MC_ENTRY_metadata", ValueError("synthetic invalid header"))
    assert blocked["status"] == "SOURCE_FORMAT_OR_IMPLEMENTATION_BLOCKED" and not blocked["raw_returns_calculated"]
    assert blocked["gross_screen_runs"] == 0 and not blocked["retry_authorized"]
    checks.append("pre-rawexceptionclassifiedsource/format/implementationblockwithtrace;noalphaverdict/noautoretry")
    parent = pd.DataFrame([dict(date="2018-01-02", event_id="x", side=1, entry=100.)])
    mc = pd.DataFrame([dict(date="2018-01-02", side=1, entry=100.25, entry_j=None, source_row_id=5)])
    p, _, _ = entry_parity(parent, pd.DataFrame(), mc, dict(passed=True))
    assert p["passed"] and p["missing_MC_clock_is_unverified_not_invented"]
    mc.loc[0, "entry_j"] = 542
    assert not entry_parity(parent, pd.DataFrame(), mc, dict(passed=True))[0]["passed"]
    checks.append("fixedtickparity;optionalclockunverified;presentclockmustbe541;zerooffsetsearch")
    values = pd.DataFrame([dict(year=2018, side=1, keep_FLOW15=True, keep_PRICE15=False, gross_MNQ=10.),
        dict(year=2018, side=-1, keep_FLOW15=False, keep_PRICE15=True, gross_MNQ=-20.)])
    summary = summaries(values)
    selected = summary[(summary.model == "FLOW15") & (summary.subset == "kept") & (summary.period == "2018-22") & (summary.side == "both")].iloc[0]
    assert selected.events == 1 and selected.total == 10
    checks.append("grossBASEFLOWPRICEkeptremovedbyyearside;zeroandsingleeventSDSEt")
    return dict(passed=True, checks=checks, real_price_OF_MC_cache_rows_read=False,
        raw_or_stopped_or_account_returns_calculated=False, script_sha256=sha(ROOT / SCRIPT), versions=runtime_versions())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=("fixtures", "gross"))
    parser.add_argument("--prereg")
    args = parser.parse_args()
    if args.phase == "fixtures":
        result = synthetic_checks(); dump_once(OUT / f"synthetic_checks_{result['script_sha256'][:12]}.json", result)
    else:
        if not args.prereg: parser.error("Gross requires committed --prereg.")
        result = gross(args.prereg)
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__":
    main()
