"""H09 immutable SOURCE/support admission; no gross/stopped/account returns.

Imports and --fixtures read no owned input, schema or real calendar schedule.
Only --source binds and interprets the explicit 2017--22 ES minute inventory.
The source pass is a declared observed-chart/calendar port, never MC parity or
complete-feed certification. Future path presence can veto the whole phase;
it cannot choose which provisional parent/EXTRA tickets survive.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import contextmanager
import csv
from datetime import date, datetime, timedelta, timezone
import fcntl
from fractions import Fraction
import hashlib
import importlib.metadata
import json
from math import comb
from pathlib import Path
import re
import subprocess
import sys
import traceback
import warnings

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
import codex_hunt_v2_mes_parent as PARENT

OUT = ROOT / "analysis/outputs/codex_hunt_v2_mes_affordability"
SCRIPT = "analysis/codex_hunt_v2_mes_moc_admit.py"
PLAN = "agents/codex/plans/hunt_v2_mes_moc_affordability.md"
EVIDENCE = "agents/codex/research/hunt_v2_mes_moc_affordability_nomination.md"
CODE = (SCRIPT, "analysis/codex_hunt_v2_mes_parent.py", "analysis/grid24.py",
        "analysis/codex_s03_calendar.py", "analysis/replica.py")
SOURCE_PATH = "funded_strategies/ES_MOC_Follow.txt"
SOURCE_COMMIT = "d14dc9a153df128aafd3f48d4fea2aa78b88bb28"
SOURCE_BLOB = "33e4a6a1c57dc0867d6ee9b26c310879ebd08f18"
YEARS = tuple(range(2017, 2023))
DESIGN_YEARS = tuple(range(2018, 2023))
NATIVE = tuple(f"data/ES_1min_{year}.csv" for year in YEARS)
FIELDS = ("date", "time", "open", "high", "low", "close", "volume")
NUMERIC_RE = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")
TICK_TOLERANCE = 1e-7
FIRST = date(2017, 1, 1)
LAST = date(2022, 12, 31)


def now():
    return datetime.now(timezone.utc).isoformat()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def dump(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("x") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")


def csv_once(name, rows, fields):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("x", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(row[key], separators=(",", ":"))
                if isinstance(row.get(key), (dict, list)) else row.get(key) for key in fields})


def committed_proof(prereg):
    if git("branch", "--show-current").decode().strip() != "codex/work":
        raise ValueError("H09 stays on codex/work.")
    original = git("rev-parse", prereg).decode().strip()
    if re.fullmatch(r"[0-9a-f]{40}", original) is None:
        raise ValueError("A full immutable preregistration hash is required.")
    subprocess.check_call(["git", "merge-base", "--is-ancestor", original, "HEAD"], cwd=ROOT)
    for name in (PLAN, EVIDENCE):
        if git("show", original + ":" + name) != (ROOT / name).read_bytes():
            raise ValueError("Original H09 plan/evidence changed:" + name)
    code = {}
    for name in (*CODE, PLAN, EVIDENCE):
        current = sha(ROOT / name)
        if hashlib.sha256(git("show", "HEAD:" + name)).hexdigest() != current:
            raise ValueError("Commit exact source implementation/dependencies before data:" + name)
        code[name] = current
    blob = git("rev-parse", SOURCE_COMMIT + ":" + SOURCE_PATH).decode().strip()
    if blob != SOURCE_BLOB:
        raise ValueError("Pinned parent source blob changed.")
    return dict(prereg=original, implementation_commit=git("rev-parse", "HEAD").decode().strip(),
        code_sha256=code, parent_source=dict(commit=SOURCE_COMMIT, path=SOURCE_PATH, blob=blob,
            sha256=hashlib.sha256(git("show", SOURCE_COMMIT + ":" + SOURCE_PATH)).hexdigest()),
        runtime_versions=dict(python=sys.version.split()[0],
            **{name: importlib.metadata.version(name) for name in ("numpy", "pandas")}),
        calendar_protocol="codex_s03_calendar.calendar_status + literal pinned PL early-close predicate; conservative cash-auction port",
        observed_chart_history_not_complete_feed_or_MC_parity=True)


def bind_inputs(bound):
    """Every exact file is bound before even the first header is opened."""
    inventory = []
    for name in NATIVE:
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            raise ValueError("Explicit native regular file missing/unexpected symlink:" + name)
        inventory.append(dict(path=name, bytes=path.stat().st_size, sha256=sha(path)))
    bound["native_inventory"] = inventory
    dump("source_pre_value_binding.json", dict(bound, input_header_or_rows_interpreted=False,
        authorized_years=list(YEARS), performance_years=list(DESIGN_YEARS), warmup_only=[2017],
        raw_or_stopped_endpoint_returns_authorized=False, gross_screen_runs=0, economic_evaluations=0))


def native_key(raw_date, raw_time, source_year):
    if re.fullmatch(r"[0-9]{8}", raw_date) is None or re.fullmatch(r"[0-9]{1,4}", raw_time) is None:
        raise ValueError("Native date/time is not strict YYYYMMDD/HHMM.")
    day = date(int(raw_date[:4]), int(raw_date[4:6]), int(raw_date[6:]))
    if day.year != source_year or not FIRST <= day <= LAST:
        raise ValueError("Native date differs from its explicit source year/range.")
    hour, minute = divmod(int(raw_time), 100)
    if hour > 23 or minute > 59:
        raise ValueError("Native HHMM outside civil clock.")
    return (day - FIRST).days, hour * 60 + minute


def numeric_row(raw, positions):
    """Declared representation tolerance only; no discretionary quote repair."""
    import math
    parsed = []
    for field in FIELDS[2:]:
        text = raw[positions[field]].strip(" \t\r\n\v\f")
        if NUMERIC_RE.fullmatch(text) is None:
            raise ValueError("Non-numeric/nonfinite native " + field)
        value = float(text)
        if not math.isfinite(value):
            raise ValueError("Nonfinite native " + field)
        parsed.append(value)
    deviations = []
    for index in range(4):
        value = parsed[index]
        nearest = round(value * 4)
        deviation = abs(value * 4 - nearest)
        if value <= 0 or deviation > TICK_TOLERANCE:
            raise ValueError("Nonpositive/off-quarter-tick ES quote.")
        parsed[index] = nearest / 4
        deviations.append(deviation)
    op, high, low, close, volume = parsed
    if high < max(op, low, close) or low > min(op, high, close) or volume < 0:
        raise ValueError("Invalid OHLC ordering/negative volume.")
    return tuple(parsed), max(deviations)


def audit_native():
    """Global row/duplicate audit before Grid24's first-row duplicate collapse."""
    import numpy as np
    shape = ((LAST - FIRST).days + 1, 1440)
    values = np.full((5, *shape), np.nan, dtype=np.float64)
    source_record = np.zeros(shape, dtype=np.uint32)
    identical_duplicates = defaultdict(list)
    issues, files = [], []
    for name in NATIVE:
        year = int(Path(name).stem[-4:])
        count = identical = representation = 0
        maximum_tick_deviation = 0.
        with (ROOT / name).open(newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader)
            if header != list(FIELDS):
                raise ValueError("Explicit native seven-column schema differs:" + name + ":" + repr(header))
            positions = {field: header.index(field) for field in FIELDS}
            for record, raw in enumerate(reader, 2):
                count += 1
                try:
                    if len(raw) != len(FIELDS):
                        raise ValueError("Native CSV row width differs from header.")
                    row, minute = native_key(raw[positions["date"]], raw[positions["time"]], year)
                    parsed, deviation = numeric_row(raw, positions)
                    maximum_tick_deviation = max(maximum_tick_deviation, deviation)
                    representation += int(deviation > 0)
                    if source_record[row, minute]:
                        if tuple(values[:, row, minute]) != parsed:
                            raise ValueError("Conflicting duplicate native key; no first-row selection.")
                        key = (row, minute)
                        if not identical_duplicates[key]:
                            identical_duplicates[key].append(int(source_record[row, minute]))
                        identical_duplicates[key].append(record)
                        identical += 1
                    else:
                        values[:, row, minute] = parsed
                        source_record[row, minute] = record
                except (ValueError, OverflowError) as error:
                    issues.append(dict(source_path=name, source_csv_record=record, issue=str(error),
                        raw_date=raw[0] if raw else None, raw_time=raw[1] if len(raw) > 1 else None))
        files.append(dict(path=name, header=header, rows=count, identical_duplicate_rows=identical,
            nonzero_tolerance_canonicalizations=representation, max_tick_deviation=maximum_tick_deviation))
    duplicate_ledger = [dict(date=(FIRST + timedelta(days=day)).isoformat(), minute=minute,
        source_path=f"data/ES_1min_{(FIRST + timedelta(days=day)).year}.csv", source_csv_records=ids)
        for (day, minute), ids in sorted(identical_duplicates.items())]
    audit = dict(passed=not issues, files=files, total_rows=sum(item["rows"] for item in files),
        unique_native_keys=int((source_record > 0).sum()), identical_duplicate_groups=len(identical_duplicates),
        identical_duplicate_rows=sum(item["identical_duplicate_rows"] for item in files), issues=issues,
        identical_duplicate_ledger=duplicate_ledger,
        numeric_tick_tolerance=TICK_TOLERANCE, all_rows_globally_checked_before_Grid24=True,
        dates_timezone_assumption="native exporter close-labelled civil America/Chicago; no authenticated receipt/roll claim",
        price_or_volume_interpolated=False, negative_or_zero_ES_quotes_allowed=False)
    return values, source_record, dict(identical_duplicates), audit


def source_ids(day_index, minute, records, duplicates):
    day = FIRST + timedelta(days=int(day_index))
    selected = duplicates.get((int(day_index), int(minute)), [int(records[day_index, minute])])
    return [f"data/ES_1min_{day.year}.csv:csv:{record}" for record in selected if record]


def shared_grid_and_bars(values, records, duplicates):
    """Shared Grid24/bars5 with an explicit six-file cache inventory only."""
    import numpy as np
    from grid24 import Grid24
    cache = OUT / "cache/native_design"
    cache.mkdir(parents=True, exist_ok=True)
    expected_links = {f"day_{year}.csv": ROOT / name for year, name in zip(YEARS, NATIVE)}
    existing = {item.name for item in cache.iterdir()}
    if existing - set(expected_links):
        raise ValueError("Unexpected file in exact six-link Grid24 inventory.")
    for name, target in expected_links.items():
        link = cache / name
        if link.is_symlink():
            if link.resolve() != target.resolve():
                raise ValueError("Grid24 cache symlink points outside bound inventory.")
        elif link.exists():
            raise ValueError("Native Grid24 cache inventory must contain only symlinks.")
        else:
            link.symlink_to(target)
    grid = Grid24(str(cache / "day_*.csv"), night_pattern="")
    start = (date.fromisoformat(str(grid.ts[0])[:10]) - FIRST).days
    if start < 0 or start + grid.D > values.shape[1]:
        raise ValueError("Shared grid axis outside bound source range.")
    for index, attr in enumerate(("o", "h", "l", "c", "v")):
        actual = getattr(grid, attr)
        expected = values[index, start:start + grid.D]
        if not np.array_equal(np.isfinite(actual), np.isfinite(expected)):
            raise ValueError("Shared Grid24 presence differs from global native audit:" + attr)
        present = np.isfinite(expected)
        tolerance = TICK_TOLERANCE / 4 if index < 4 else 0.
        if np.any(np.abs(actual[present] - expected[present]) > tolerance):
            raise ValueError("Shared Grid24 values differ from global native audit:" + attr)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        shared = grid.bars(5)
    bars = []
    for day_index in range(grid.D):
        absolute_day = start + day_index
        day = FIRST + timedelta(days=absolute_day)
        for column, minute in enumerate(shared["j"]):
            if not np.isfinite(shared["c"][day_index, column]):
                continue
            minute = int(minute)
            absolute_end = absolute_day * 1440 + minute
            observed, missing, ids = [], [], []
            for absolute in range(absolute_end - 4, absolute_end + 1):
                previous_day, previous_minute = divmod(absolute, 1440)
                key = dict(date=(FIRST + timedelta(days=previous_day)).isoformat(), minute=previous_minute)
                if 0 <= previous_day < records.shape[0] and records[previous_day, previous_minute]:
                    observed.append(key)
                    ids.extend(source_ids(previous_day, previous_minute, records, duplicates))
                else:
                    missing.append(key)
            if not observed:
                raise ValueError("Shared nonempty chart bar has no audited native contributors.")
            canonical = {name: round(float(shared[attr][day_index, column]) * 4) / 4
                for name, attr in (("open", "o"), ("high", "h"), ("low", "l"), ("close", "c"))}
            bars.append(dict(date=day.isoformat(), minute=minute, **canonical,
                volume=float(shared["v"][day_index, column]), bar_id=day.isoformat() + ":C" + str(minute),
                source_ids=ids, observed_native_keys=observed, missing_native_keys=missing,
                native_count=len(observed), complete_five_minutes=not missing,
                exact_native_close_present=bool(records[absolute_day, minute]),
                first_observed_key=[observed[0]["date"], observed[0]["minute"]],
                last_observed_key=[observed[-1]["date"], observed[-1]["minute"]]))
    return grid, bars, dict(shared_engine="analysis/grid24.py::Grid24.bars(5)", grid_days=grid.D,
        observed_chart_bars=len(bars), partial_observed_chart_bars=sum(not row["complete_five_minutes"] for row in bars),
        Grid24_trading_or_last_j_used_for_membership=False, Grid24_daily_atr_used=False,
        shared_arrays_verified_against_global_native_audit=True,
        explicit_six_symlinks=[str((cache / name).relative_to(ROOT)) for name in sorted(expected_links)])


def classify_move(move, atr):
    # The pure parent persists its exact Fraction as numerator/denominator;
    # do not convert that denominator through a rounded float representation.
    if isinstance(atr, str) and re.fullmatch(r"[+-]?[0-9]+/[1-9][0-9]*", atr):
        exact_atr = Fraction(atr)
    else:
        exact_atr = PARENT.number(atr)
    ratio = abs(PARENT.number(move)) / exact_atr
    if ratio < Fraction(3, 10):
        raise ValueError("Provisional parent fails its frozen move threshold.")
    return "[.30,.50)" if ratio < Fraction(1, 2) else "[.50,.75)" if ratio < Fraction(3, 4) else "[.75,inf)"


def feature_rows(provisional):
    rows = []
    for event in provisional:
        if date.fromisoformat(event["date"]).year not in DESIGN_YEARS:
            continue
        row = dict(event)
        row.update(event_id=len(rows), year=date.fromisoformat(event["date"]).year,
            source_known=not bool(event["source_flags"]), qty_BASE_Q1=1, qty_CONST_Q2=2,
            source_or_count_gate_passed=False, terminal_return_or_stop_outcome_used=False)
        if not row["source_known"]:
            row.update(qty_extra=0, qty_policy=1)
        row["stratum"] = [row["year"], row["side"], classify_move(row["move_points"], row["atr_exact"])]
        rows.append(row)
    return rows


def combinatorial_support(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row["stratum"])].append(row)
    cells, product, variable = [], 1, 0
    for key, members in sorted(groups.items(), key=lambda item: str(item[0])):
        unknown = [row for row in members if not row["source_known"]]
        if any(row["qty_extra"] for row in unknown):
            raise ValueError("Unknown affordability must retain baseline one and fixed zero extra.")
        pool = [row for row in members if row["source_known"]]
        n, k = len(pool), sum(row["qty_extra"] for row in pool)
        choices = comb(n, k)
        product *= choices
        variable += int(0 < k < n)
        cells.append(dict(stratum=list(key), all_event_ids=[row["event_id"] for row in members],
            fixed_unknown_extra_zero_ids=[row["event_id"] for row in unknown],
            randomizable_event_ids=[row["event_id"] for row in pool], n=n, selected_extra_k=k,
            exact_choices=str(choices), variable_cell=0 < k < n))
    return dict(strata="design_year,side,absMove/ATRbins[.30,.50),[.50,.75),[.75,inf)",
        exact_distinct_mask_count=str(product), variable_cells=variable,
        minimum_distinct_masks=1000, passed=product >= 1000 and variable > 0, cells=cells,
        masks_or_return_paths_sampled=False, random_seed_for_later_masks=2026102709,
        unknown_extra_zero_fixed=True, exact_ATR_or_affordability_not_matched=True)


def expected_date_audit(parent, records, duplicates, calendar_callback):
    """No observed-day existence/full-session flag selects expected dates."""
    decisions = {row["date"]: row for row in parent["decision_audit"]}
    presence = {row["date"]: row for row in parent["observed_date_coverage"]}
    rows, contradictions = [], []
    day = date(2018, 1, 1)
    while day <= LAST:
        text = day.isoformat()
        cal = PARENT.calendar_audit(text, calendar_callback(text))
        candidate = decisions.get(text)
        seen = presence.get(text)
        required = cal["calendar_entry_allowed"]
        issues = []
        if required:
            if seen is None:
                issues.append("EXPECTED_NORMAL_CASH_DATE_HAS_NO_OBSERVED_CHART_DATE")
            for field in ("reference_state", "decision_state"):
                if seen is None or seen[field] != "COMPLETE_EXACT":
                    issues.append("EXPECTED_NORMAL_" + field.upper() + "_NOT_COMPLETE_EXACT")
            if candidate is None or candidate["atr"] is None or candidate["atr"] <= 0:
                issues.append("EXPECTED_NORMAL_PRIOR_15_CHART_TR_ATR_NOT_READY_POSITIVE")
            if candidate is not None:
                issues.extend(candidate["source_flags"])
        index = (day - FIRST).days
        if not required and cal["shared_cash_calendar"]["kind"] != "normal":
            close = cal["shared_cash_calendar"]["cash_close_j"]
            lower = int(close) + 1 if close is not None else 840
            # With no cash close (holiday/weekend), retain auction-window
            # observations, not ordinary Sunday evening reopen observations.
            upper = 1439 if close is not None else 900
            late = [minute for minute in range(lower, upper + 1) if records[index, minute]]
            if late:
                contradictions.append(dict(date=text, calendar=cal,
                    observed_after_cash_close_or_closed_auction_keys=late,
                    source_ids=[item for minute in late for item in source_ids(index, minute, records, duplicates)],
                    literal_parent_would_qualify=candidate["literal_parent_qualified"] if candidate else None,
                    disposition="Retained conservative cash-auction-calendar exclusion; not exact MC parity"))
        rows.append(dict(date=text, calendar=cal, expected_normal_source_gate_required=required,
            calendar_literal_disagreement=cal["literal"]["is_early_close"] != (cal["shared_cash_calendar"]["kind"] != "normal"),
            observed_chart_date=seen is not None, source_coverage=seen,
            parent_decision_available=candidate is not None, source_issues=sorted(set(issues)),
            passed=not issues, future_price_membership_used=False))
        day += timedelta(days=1)
    return rows, contradictions


def held_path_audit(rows, records, duplicates):
    output = []
    for row in rows:
        index = (date.fromisoformat(row["date"]) - FIRST).days
        missing = [minute for minute in range(891, 901) if not records[index, minute]]
        output.append(dict(event_id=row["event_id"], date=row["date"], side=row["side"],
            required_native_keys=list(range(891, 901)), missing_native_keys=missing,
            source_ids=[item for minute in range(891, 901) for item in source_ids(index, minute, records, duplicates)],
            entry_native_OPEN1451_known=bool(records[index, 891]),
            exact_terminal_native_C1500_known=bool(records[index, 900]), passed=not missing,
            terminal_return_or_stop_outcome_computed=False, unresolved_rows_never_removed_from_parent=True))
    return output


def counts(rows):
    output = []
    for model, quantity in (("BASE_Q1", "qty_BASE_Q1"), ("CONST_Q2", "qty_CONST_Q2"),
                            ("EXTRA", "qty_extra"), ("POLICY", "qty_policy")):
        for period in ("2018-22", *map(str, DESIGN_YEARS)):
            for side in ("both", "long", "short"):
                selected = [row for row in rows if (period == "2018-22" or row["year"] == int(period))
                    and (side == "both" or row["side"] == (1 if side == "long" else -1))]
                output.append(dict(model=model, period=period, side=side,
                    parent_tickets=len(selected), active_tickets=sum(row[quantity] > 0 for row in selected),
                    whole_contracts=sum(row[quantity] for row in selected),
                    known_affordability_tickets=sum(row["source_known"] for row in selected)))
    return output


def support_gate(rows, native, expected, held, null):
    known = sum(row["source_known"] for row in rows)
    fraction = known / len(rows) if rows else 0.
    extra = [row for row in rows if row["qty_extra"]]
    by_side = {str(side): sum(row["side"] == side for row in extra) for side in (-1, 1)}
    years = sorted({row["year"] for row in extra})
    coverage = all(row["passed"] for row in expected) and all(row["passed"] for row in held)
    checks = dict(native_global_valid=native["passed"], expected_and_held_source_paths_complete=coverage,
        min_100_design_parents=len(rows) >= 100, min_50_extra=len(extra) >= 50,
        min_10_extra_each_side=min(by_side.values()) >= 10,
        min_3_extra_years=len(years) >= 3, min_95percent_known=fraction >= .95,
        min_1000_distinct_matched_masks_and_variable_cell=null["passed"])
    return dict(phase="SOURCE_SUPPORT_only", passed=all(checks.values()), checks=checks,
        parent_events=len(rows), extra_events=len(extra), known_affordability_events=known,
        known_fraction=fraction, extra_by_side=by_side, extra_years=years,
        unresolved_expected_dates=[row["date"] for row in expected if not row["passed"]],
        unresolved_held_event_ids=[row["event_id"] for row in held if not row["passed"]],
        raw_stopped_or_account_returns_computed=False, gross_screen_runs=0, economic_evaluations=0,
        whole_source_veto_not_selective_future_path_deletion=True,
        observed_chart_and_conservative_calendar_port_only=True, source_MC_parity_certified=False,
        next_action="Separate committed raw screen permitted only after this artifact is independently reviewed and committed"
            if all(checks.values()) else "Close H09 before raw/economic returns; no count/calendar/threshold/null rescue")


def recheck(bound):
    for name, expected in bound["code_sha256"].items():
        if sha(ROOT / name) != expected:
            raise ValueError("Source code/prereg dependency changed during execution:" + name)
    for item in bound.get("native_inventory", []):
        if (ROOT / item["path"]).stat().st_size != item["bytes"] or sha(ROOT / item["path"]) != item["sha256"]:
            raise ValueError("Bound native source changed during execution:" + item["path"])


@contextmanager
def lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "source.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def source(prereg):
    with lock():
        if any((directory / "source_attempt.json").exists() for directory in
               (ROOT / "analysis/outputs").glob("codex_hunt_v2_mes_affordability*")):
            raise ValueError("Retained H09 source attempt exists; no unchanged rerun/alternate output directory.")
        bound = committed_proof(prereg)
        started = now()
        dump("source_attempt.json", dict(started_utc=started, **bound,
            new_gross_screen_or_economic_evaluation=False, retry_authorized=False))
        names = ["source_attempt.json"]
        stage = "bind_all_six_native_inputs_before_header_or_values"
        try:
            bind_inputs(bound)
            names.append("source_pre_value_binding.json")
            stage = "global_native_schema_clock_tick_OHLCV_duplicate_audit"
            values, records, duplicates, native = audit_native()
            dump("source_native_audit.json", native)
            names.append("source_native_audit.json")
            if not native["passed"]:
                raise ValueError("Native global audit failed; no Grid24 or parent feature evaluation.")
            stage = "bound_shared_cash_calendar_and_Grid24_bars5"
            from codex_s03_calendar import calendar_status
            grid, bars, grid_audit = shared_grid_and_bars(values, records, duplicates)
            parent = PARENT.reconstruct_parent(bars, calendar_auditor=calendar_status)
            del grid, values, bars
            rows = feature_rows(parent["candidates"])
            expected, contradictions = expected_date_audit(parent, records, duplicates, calendar_status)
            held = held_path_audit(rows, records, duplicates)
            null = combinatorial_support(rows)
            gate = support_gate(rows, native, expected, held, null)
            dump("source_grid_audit.json", grid_audit)
            dump("source_parent_features.json", rows)
            dump("source_decision_audit.json", [row for row in parent["decision_audit"]
                if date.fromisoformat(row["date"]).year in DESIGN_YEARS])
            dump("source_TR_audit.json", parent["stored_TR_audit"])
            dump("source_expected_dates.json", expected)
            dump("source_calendar_contradictions.json", contradictions)
            dump("source_held_path_audit.json", held)
            dump("source_null_support.json", null)
            csv_once("source_counts.csv", counts(rows), ("model", "period", "side", "parent_tickets",
                "active_tickets", "whole_contracts", "known_affordability_tickets"))
            csv_once("source_features.csv", rows, ("event_id", "date", "year", "side", "atr", "atr_exact",
                "move_points", "stop_points", "source_known", "qty_BASE_Q1", "qty_CONST_Q2", "qty_extra",
                "qty_policy", "stratum", "atr_reference_ids", "source_flags"))
            names += ["source_grid_audit.json", "source_parent_features.json", "source_decision_audit.json",
                "source_TR_audit.json", "source_expected_dates.json", "source_calendar_contradictions.json",
                "source_held_path_audit.json", "source_null_support.json", "source_counts.csv", "source_features.csv"]
        except Exception as error:
            gate = dict(phase="SOURCE_SUPPORT_only", passed=False, status="SOURCE_OR_IMPLEMENTATION_BLOCKED",
                stage=stage, exception_type=type(error).__name__, exception_message=str(error),
                raw_stopped_or_account_returns_computed=False, gross_screen_runs=0, economic_evaluations=0)
            dump("source_exception.json", dict(gate, traceback=traceback.format_exc()))
            names.append("source_exception.json")
        recheck(bound)
        dump("source_gate.json", gate)
        dump("source_input_binding.json", bound)
        names += ["source_gate.json", "source_input_binding.json"]
        marker = dict(started_utc=started, completed_utc=now(), phase="SOURCE_SUPPORT_only",
            passed=gate["passed"], prereg=bound["prereg"], implementation_commit=bound["implementation_commit"],
            code_sha256=bound["code_sha256"], artifacts_sha256={name: sha(OUT / name) for name in names},
            raw_stopped_or_account_returns_computed=False, gross_screen_runs=0, economic_evaluations=0,
            new_hypothesis_registered_by_this_script=False, next_outcome_phase_authorized=False,
            retry_authorized=False, source_MC_parity_or_complete_feed_certified=False)
        dump("source_verified_execution.json", marker)
        return gate


def fixtures():
    """Pure invented records only: no real calendar callback or owned file I/O."""
    checks = []
    assert native_key("20180102", "1450", 2018) == ((date(2018, 1, 2) - FIRST).days, 890)
    for raw in ("2460", "2400", "-1", "14:50"):
        try:
            native_key("20180102", raw, 2018)
        except ValueError:
            pass
        else:
            raise AssertionError("Bad native clock admitted.")
    pos = {name: index for index, name in enumerate(FIELDS)}
    values, _ = numeric_row(["20180102", "1450", "100", "101", "99", "100.25", "1"], pos)
    assert values == (100., 101., 99., 100.25, 1.)
    for bad in ("NaN", "0", "100.1", "-1"):
        try:
            numeric_row(["20180102", "1450", bad, "101", "99", "100.25", "1"], pos)
        except ValueError:
            pass
        else:
            raise AssertionError("Bad native quote admitted.")
    checks.append("native_exact_year_clock_positive_quartertick_finite_OHLCV")
    assert classify_move(".75", "5/2") == "[.30,.50)"
    assert classify_move("1.25", "5/2") == "[.50,.75)"
    assert classify_move("1.875", "5/2") == "[.75,inf)"
    checks.append("exact_rational_fixed_move_strata_boundaries")
    rows = [dict(event_id=i, date="2018-01-02", year=2018, side=1, source_known=True,
        qty_extra=int(i < 5), stratum=[2018, 1, "[.30,.50)"])
        for i in range(10)]
    null = combinatorial_support(rows)
    assert null["exact_distinct_mask_count"] == "252" and not null["passed"]
    rows += [dict(event_id=10 + i, date="2019-01-02", year=2019, side=-1, source_known=True,
        qty_extra=int(i < 5), stratum=[2019, -1, "[.30,.50)"])
        for i in range(10)]
    null = combinatorial_support(rows)
    assert null["exact_distinct_mask_count"] == "63504" and null["passed"]
    unknown = dict(rows[0], event_id=20, source_known=False, qty_extra=0)
    assert combinatorial_support(rows + [unknown])["exact_distinct_mask_count"] == "63504"
    checks.append("exact_combinatorial_support_no_duplicate_masks_unknown_zero_fixed")
    saturated = [dict(row, qty_extra=1) for row in rows]
    assert not combinatorial_support(saturated)["passed"]
    checks.append("constant_two_policy_no_variable_cell_fails_before_returns")
    import numpy as np
    records = np.zeros(((LAST - FIRST).days + 1, 1440), dtype=np.uint8)
    invented_day = "2018-01-02"
    index = (date.fromisoformat(invented_day) - FIRST).days
    # One invented normal date; every other day is explicitly an artificial
    # closed date. This does not generate/apply any real exchange schedule.
    calendar = lambda day: dict(kind="normal" if day == invented_day else "holiday",
        cash_close_j=900 if day == invented_day else None, reason="ARTIFICIAL_FIXTURE")
    empty = dict(decision_audit=[], observed_date_coverage=[])
    expected, _ = expected_date_audit(empty, records, {}, calendar)
    chosen = next(row for row in expected if row["date"] == invented_day)
    assert not chosen["passed"] and not chosen["observed_chart_date"]
    observed = dict(decision_audit=[dict(date=invented_day, atr=2., source_flags=[],
        literal_parent_qualified=False)], observed_date_coverage=[dict(date=invented_day,
        reference_state="COMPLETE_EXACT", decision_state="COMPLETE_EXACT")])
    expected, _ = expected_date_audit(observed, records, {}, calendar)
    assert next(row for row in expected if row["date"] == invented_day)["passed"]
    observed["observed_date_coverage"][0]["reference_state"] = "PARTIAL"
    expected, _ = expected_date_audit(observed, records, {}, calendar)
    assert not next(row for row in expected if row["date"] == invented_day)["passed"]
    checks.append("expected_normal_nonsignal_date_missing_or_partial_reference_global_veto_no_future_membership")
    event = dict(event_id=0, date=invented_day, side=1)
    records[index, 891:901] = 1
    assert held_path_audit([event], records, {})[0]["passed"]
    records[index, 900] = 0
    path = held_path_audit([event], records, {})
    assert len(path) == 1 and path[0]["missing_native_keys"] == [900] and not path[0]["passed"]
    assert path[0]["unresolved_rows_never_removed_from_parent"]
    checks.append("complete_entry_bar_through_exact_time_endpoint_presence_veto_retains_parent_ticket")
    return dict(passed=True, groups=len(checks), checks=checks,
        actual_input_header_schema_rows_or_schedule_accessed=False,
        raw_stopped_or_account_returns_computed=False, gross_screen_runs=0, economic_evaluations=0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fixtures", action="store_true")
    mode.add_argument("--source", action="store_true")
    parser.add_argument("--prereg")
    arguments = parser.parse_args()
    if arguments.fixtures:
        print(json.dumps(fixtures(), allow_nan=False))
    else:
        if not arguments.prereg:
            parser.error("--source requires original committed --prereg hash")
        print(json.dumps(source(arguments.prereg), allow_nan=False))
