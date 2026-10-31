"""H07 fixed no-return feature/support admission AFTER immutable SOURCE PASS.

Imports and fixtures never read owned rows. Actual native value conversion is
restricted to parent-date C840/O541 keys. As-of state consumes only event<840,
boundary840 is unknown, and later events/whole-day diagnostics never select a
mask. No raw/stopped endpoints, OF masks, profits or account engine is loaded.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import contextmanager
import csv
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import fcntl
import hashlib
import json
from math import comb
from pathlib import Path
import re
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
OUT = ROOT / "analysis/outputs/codex_hunt_v2_ldf_rs_open_loss"
SCRIPT = "analysis/codex_hunt_v2_ldf_rs_features.py"
SOURCE_SCRIPT = "analysis/codex_hunt_v2_ldf_rs_open_loss.py"
HELPER = "analysis/codex_hunt_v2_ldf_rs_metadata.py"
PLAN = "agents/codex/plans/hunt_v2_ldf_rs_open_loss.md"
EVIDENCE = "agents/codex/evidence/hunt_v2_ldf_rs_open_loss.md"
ADDENDUM = "agents/codex/research/hunt_v2_ldf_rs_predata_adjudication.md"
PREREG = "4c36121"
PARENT = ROOT / "analysis/outputs/codex_hunt_v2_ldf_delta"
MC = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute Relative Strength.xlsx"
SOURCE_REQUIRED = ("source_attempt.json", "source_parent_dates_only.json", "source_gate.json", "source_input_binding.json")
PARENT_FIELDS = ("date", "year", "side", "decision_j", "entry_label_j", "exit_label_j", "atr", "day_move", "entry_open")
YEARS = tuple(range(2018, 2023))
NATIVE_NAMES = tuple(name for y in YEARS for name in (f"data/NQ_1min_{y}.csv", f"data/NQ_1min_ON_{y}.csv"))
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
NUMBER_RE = re.compile(r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$")
ASCII_SPACE = " \t\r\n\v\f"
MODELS = ("BASE", "RS_OPEN_LOSS", "SAME_SIDE_OPEN", "PRICE_0901")
FEATURE_CSV_FIELDS = ("event_id", "date", "year", "side", "keep_BASE", "keep_RS_OPEN_LOSS",
    "keep_SAME_SIDE_OPEN", "keep_PRICE_0901", "source_known", "same_side_open", "price_sign",
    "stratum_A", "stratum_B", "state", "unknown_reason", "C840", "O541", "rs_side",
    "rs_trade_id", "rs_entry", "current_position_mark_points", "native_required_keys_known",
    "parent_source_csv_record", "decision_j", "entry_label_j", "exit_label_j")
sys.path.insert(0, str(ROOT / "analysis"))
import codex_hunt_v2_ldf_rs_metadata as META


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""): digest.update(block)
    return digest.hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def dump(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("x") as handle:
        json.dump(value, handle, indent=2, allow_nan=False); handle.write("\n")


def csv_once(name, rows, fields):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("x", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(row[key], separators=(",", ":")) if isinstance(row[key], (dict, list)) else row[key] for key in fields})


def exact_decimal(raw):
    text = raw.strip(ASCII_SPACE) if isinstance(raw, str) else str(raw)
    if NUMBER_RE.fullmatch(text) is None: raise ValueError("Selected price/metadata is not a strict ASCII decimal.")
    number = Decimal(text)
    if not number.is_finite(): raise ValueError("Selected price/metadata must be finite.")
    return number


def quarter_price(raw):
    number = exact_decimal(raw)
    if number <= 0 or number % Decimal(".25") != 0: raise ValueError("Selected native/RS price must be positive exact quarter tick.")
    return number


def integer(raw):
    number = exact_decimal(raw)
    if number != number.to_integral_value(): raise ValueError("Source integer metadata is fractional.")
    return int(number)


def source_proof(prereg, source_sha):
    if git("branch", "--show-current").decode().strip() != "codex/work": raise ValueError("H07 FEATURES stays on codex/work.")
    original = git("rev-parse", PREREG).decode().strip()
    if git("rev-parse", prereg).decode().strip() != original: raise ValueError("Use original economic H07 preregistration4c36121.")
    for name in (PLAN, EVIDENCE):
        if git("show", original + ":" + name) != (ROOT / name).read_bytes(): raise ValueError("Economic plan/evidence changed." + name)
    if SHA_RE.fullmatch(source_sha or "") is None: raise ValueError("Exact SOURCE marker SHA256 required.")
    marker_path = OUT / "source_verified_execution.json"
    if sha(marker_path) != source_sha: raise ValueError("SOURCE marker differs from explicit proof SHA.")
    marker = json.loads(marker_path.read_text())
    if not (marker.get("phase") == "SOURCE_only" and marker.get("passed") is True and marker.get("prereg") == original):
        raise ValueError("Matching strict SOURCE-only PASS is required before any native marks.")
    for commit in (original, marker.get("implementation_commit", "")):
        if re.fullmatch(r"[0-9a-f]{40}", commit) is None: raise ValueError("SOURCE/original commit must be an immutable full hash.")
        subprocess.check_call(["git", "merge-base", "--is-ancestor", commit, "HEAD"], cwd=ROOT)
    artifacts = marker.get("artifacts_sha256", {})
    if not isinstance(artifacts, dict) or not set(SOURCE_REQUIRED).issubset(artifacts): raise ValueError("SOURCE proof incomplete.")
    hashes = {str(marker_path.relative_to(ROOT)): source_sha}
    for name, expected in artifacts.items():
        if not isinstance(name, str) or Path(name).name != name or "/" in name or "\\" in name:
            raise ValueError("SOURCE artifact names must be safe basenames.")
        if not isinstance(expected, str) or SHA_RE.fullmatch(expected) is None or sha(OUT / name) != expected:
            raise ValueError("SOURCE artifact bytes/hash changed:" + name)
        if hashlib.sha256(git("show", "HEAD:" + str((OUT / name).relative_to(ROOT)))).hexdigest() != expected:
            raise ValueError("Commit completed SOURCE artifacts before FEATURES:" + name)
        hashes[str((OUT / name).relative_to(ROOT))] = expected
    bound = json.loads((OUT / "source_input_binding.json").read_text())
    for name, expected in bound["code_sha256"].items():
        if sha(ROOT / name) != expected or hashlib.sha256(git("show", "HEAD:" + name)).hexdigest() != expected:
            raise ValueError("SOURCE producer/addendum changed after admitted data:" + name)
        hashes[name] = expected
    if marker.get("code_sha256") != bound["code_sha256"]: raise ValueError("SOURCE code chain differs.")
    for name, expected in bound["parent"]["hashes"].items():
        if sha(ROOT / name) != expected: raise ValueError("Immutable H01 artifact changed:" + name)
        hashes[name] = expected
    for name in (SCRIPT, HELPER, SOURCE_SCRIPT, PLAN, EVIDENCE, ADDENDUM):
        current = sha(ROOT / name)
        if hashlib.sha256(git("show", "HEAD:" + name)).hexdigest() != current: raise ValueError("Commit exact FEATURES/code/dependencies before new values:" + name)
        hashes[name] = current
    if sha(ROOT / MC) != bound["workbook"]["sha256"] or bound["workbook"]["sha256"] != META.WORKBOOK_SHA256:
        raise ValueError("Authoritative owned RS workbook changed.")
    hashes[MC] = META.WORKBOOK_SHA256
    gate = json.loads((OUT / "source_gate.json").read_text())
    if not (gate.get("phase") == "SOURCE_only" and gate.get("passed") is True and gate.get("source_protocol_supported") is True
        and gate.get("parent_decision_coverage", {}).get("passed") is True and gate.get("owned_stream", {}).get("global_pass") is True):
        raise ValueError("Actual global stream/Settings/coverage support required; no selective future-fault UNKNOWN.")
    for directory in (ROOT / "analysis/outputs").glob("codex_hunt_v2_ldf_rs_open_loss*"):
        if any((directory / name).exists() for name in ("features_attempt.json", "features_verified_execution.json")):
            raise ValueError("Retained FEATURES attempt/completion exists; no alternate-directory/unchanged rerun.")
    return dict(prereg=original, implementation_commit=git("rev-parse", "HEAD").decode().strip(),
        source_marker_sha256=source_sha, source_implementation_commit=marker["implementation_commit"], hashes=hashes,
        source_metadata_artifacts_only_not_new_RS_workbook_decode=True), gate["owned_stream"]


def parent_metadata():
    rows = []
    with (PARENT / "gross_events.csv").open(newline="") as handle:
        reader = csv.reader(handle); header = next(reader)
        positions = {name: header.index(name) for name in PARENT_FIELDS}
        for event_id, raw in enumerate(reader):
            selected = {name: raw[position] for name, position in positions.items()}
            day = date.fromisoformat(selected["date"]); side = integer(selected["side"])
            if day.year not in YEARS or integer(selected["year"]) != day.year or side not in (-1, 1): raise ValueError("Immutable parent date/year/side metadata differs.")
            if (integer(selected["decision_j"]), integer(selected["entry_label_j"]), integer(selected["exit_label_j"])) != (840, 841, 870): raise ValueError("Immutable parent clocks differ.")
            if exact_decimal(selected["atr"]) <= 0: raise ValueError("Immutable parent prior ATR invalid.")
            rows.append(dict(event_id=event_id, parent_source_csv_record=event_id + 2, date=day.isoformat(), year=day.year,
                side=side, decision_j=840, entry_label_j=841, exit_label_j=870,
                parent_atr_raw=selected["atr"], parent_day_move_raw=selected["day_move"], parent_entry_open_raw=selected["entry_open"]))
    if not rows or len({row["date"] for row in rows}) != len(rows) or [row["date"] for row in rows] != sorted(row["date"] for row in rows):
        raise ValueError("Immutable parent events must remain unique and chronological.")
    return rows


def native_key(raw_date, raw_time, source_year):
    if re.fullmatch(r"[0-9]{8}", raw_date) is None or re.fullmatch(r"[0-9]{1,4}", raw_time) is None: raise ValueError("Native date/time codec differs from bound source.")
    day = date(int(raw_date[:4]), int(raw_date[4:6]), int(raw_date[6:8]))
    if day.year != source_year: raise ValueError("Native file/source year mismatch.")
    hour, minute = divmod(int(raw_time), 100)
    if hour > 23 or minute > 59: raise ValueError("Impossible native HHMM.")
    return day.isoformat(), hour * 60 + minute


def select_mark_rows(numbered_rows, positions, source_name, parent_dates):
    """Native date/key membership BEFORE any open/close numeric conversion."""
    output = defaultdict(list); year = int(Path(source_name).stem[-4:])
    for record_id, raw in numbered_rows:
        key = native_key(raw[positions["date"]], raw[positions["time"]], year)
        if key[0] not in parent_dates or key[1] not in (541, 840): continue
        field = "open" if key[1] == 541 else "close"
        raw_value = raw[positions[field]]
        item = dict(source_path=source_name, source_csv_record=record_id, source_field=field, raw=raw_value)
        try: item.update(valid=True, value=str(quarter_price(raw_value)), issue=None)
        except (ValueError, InvalidOperation) as error: item.update(valid=False, value=None, issue=str(error))
        output[key].append(item)
    return output


def collect_native_marks(parent, bound):
    original = json.loads((PARENT / "gross_input_binding.json").read_text())
    paths = [str(Path(name).relative_to(ROOT)) if Path(name).is_absolute() else name for name in original["native_paths"]]
    if len(paths) != len(set(paths)) or set(paths) != set(NATIVE_NAMES): raise ValueError("H01 native inventory is not the exact10design-only DAY/ON files.")
    inventory = []
    for name in paths:
        expected = original["hashes"].get(name)
        if expected is None or sha(ROOT / name) != expected: raise ValueError("H01-bound native input changed:" + name)
        bound["hashes"][name] = expected
        inventory.append(dict(path=name, bytes=(ROOT / name).stat().st_size, sha256=expected))
    dump("features_pre_mark_binding.json", dict(bound, native_inventory=inventory,
        numeric_keys_authorized="Parent-dateC840close/O541openONLY; no rawlate-windowendpoint/volume/OF/wholegrid"))
    dates = {row["date"] for row in parent}; grouped = defaultdict(list)
    for name in paths:
        with (ROOT / name).open(newline="") as handle:
            reader = csv.reader(handle); header = next(reader)
            positions = {field: header.index(field) for field in ("date", "time", "open", "close")}
            for key, rows in select_mark_rows(enumerate(reader, start=2), positions, name, dates).items(): grouped[key].extend(rows)
    ledger, marks = [], {}
    for day in sorted(dates):
        for minute in (541, 840):
            rows = grouped.get((day, minute), [])
            values = {Decimal(row["value"]) for row in rows if row["valid"]}
            known = bool(rows and all(row["valid"] for row in rows) and len(values) == 1)
            item = dict(date=day, minute=minute, source_field="open" if minute == 541 else "close", known=known,
                value=str(next(iter(values))) if known else None, source_rows=rows,
                issue=None if known else "missing_invalid_or_contradictory_selected_native_key")
            ledger.append(item); marks[(day, minute)] = item
    return marks, ledger


def asof_state(stream, day, ldf_side, mark, scheduled_open):
    if stream.get("global_pass") is not True: raise ValueError("Global source must PASS before any feature; never selectively UNKNOWN future malformed data.")
    prefix = []
    def prefix_audit():
        return dict(asof_prefix_source_ids=[event.get("source_id") for event in prefix],
            asof_prefix_source_row_ids=[event.get("source_row_id") for event in prefix])
    unknown = lambda reason: dict(known_state=False, state="UNKNOWN", reason=reason, same_side_open=None,
        rs_side=None, rs_trade_id=None, rs_entry=None, current_position_mark_points=None, current_position_adverse=None,
        rs_entry_source_id=None, rs_entry_source_row_id=None, **prefix_audit())
    if not META.timestamp_within_coverage(stream["settings"], day, 840): return unknown("outside_declared_Settings_coverage")
    if not mark["known"] or not scheduled_open["known"]: return unknown("required_native_C840_or_O541_unknown")
    close, native_open = quarter_price(mark["value"]), quarter_price(scheduled_open["value"])
    # Only the timestamp and date are accessed to discard future events.
    # In particular, full-day noncanonical-entry diagnostics are NEVER used.
    prefix = [event for event in stream["events"] if event["date"] == day and int(event["minute"]) <= 840]
    if any(int(event["minute"]) == 840 for event in prefix): return unknown("exact_decision_boundary_event840")
    active = None
    for event in prefix:
        if event["type"] == "ENTRY":
            if active is not None: raise ValueError("Admitted source prefix contradicts global position integrity.")
            if int(event["minute"]) != 541: return unknown("observed_prefix_entry_noncanonical_clock")
            try: entry = quarter_price(event["entry"])
            except (ValueError, InvalidOperation): return unknown("observed_prefix_entry_price_invalid")
            if abs(entry - native_open) > Decimal(".00000001"): return unknown("observed_prefix_entry_native_O541_basis_mismatch")
            active = (event, entry)
        elif event["type"] == "EXIT":
            if active is None or active[0]["trade_id"] != event["trade_id"]: raise ValueError("Admitted source prefix has unmatched exit.")
            active = None
        else: raise ValueError("Admitted source event type is invalid.")
    if active is None:
        return dict(known_state=True, state="FLAT", reason="declared_report_coverage_and_asof_prefix_flat",
            same_side_open=False, rs_side=None, rs_trade_id=None, rs_entry=None, current_position_mark_points=None, current_position_adverse=False,
            rs_entry_source_id=None, rs_entry_source_row_id=None, **prefix_audit())
    event, entry = active; value = (close - entry) * int(event["side"])
    return dict(known_state=True, state="OPEN", reason="asof_prefix_own_position", same_side_open=int(event["side"]) == ldf_side,
        rs_side=int(event["side"]), rs_trade_id=event["trade_id"], rs_entry=str(entry), current_position_mark_points=str(value), current_position_adverse=value < 0,
        rs_entry_source_id=event.get("source_id"), rs_entry_source_row_id=event.get("source_row_id"), **prefix_audit())


def feature_rows(parent, marks, stream):
    rows = []
    for event in parent:
        mark, reference = marks[(event["date"], 840)], marks[(event["date"], 541)]
        native_known = mark["known"] and reference["known"]
        move = (Decimal(mark["value"]) - Decimal(reference["value"])) * event["side"] if native_known else None
        sign = "NEGATIVE" if move is not None and move < 0 else "POSITIVE" if move is not None and move > 0 else "ZERO" if move == 0 else "UNKNOWN"
        state = asof_state(stream, event["date"], event["side"], mark, reference)
        primary_drop = bool(state["known_state"] and state["same_side_open"] and state["current_position_adverse"])
        overlap_drop = bool(state["known_state"] and state["same_side_open"])
        if state["known_state"] and state["same_side_open"]:
            if primary_drop != (sign == "NEGATIVE"): raise ValueError("Exact-basis interaction identity failed; no alternate mark rule.")
        rows.append(dict(event, **state, C840=mark["value"], O541=reference["value"], native_required_keys_known=native_known,
            native_C840_source_rows=mark["source_rows"], native_O541_source_rows=reference["source_rows"],
            PRICE_0901_sign=sign, fixed_price_signed_points=str(move) if move is not None else None,
            keep_BASE=True, keep_RS_OPEN_LOSS=not primary_drop, keep_SAME_SIDE_OPEN=not overlap_drop,
            keep_PRICE_0901=not (move is not None and move < 0), parent_decision_remains_consumed=True,
            no_freed_cap_or_reentry=True, raw_or_stopped_endpoint_return_used=False,
            feature_event_time_ct=event["date"] + "T14:00:00", assumed_available_at_ct=event["date"] + "T14:00:00"))
        rows[-1].update(source_known=state["known_state"], price_sign=sign,
            unknown_reason=state["reason"] if not state["known_state"] else None,
            stratum_A=[event["year"], event["side"], sign],
            stratum_B=[event["year"], event["side"], state["known_state"], state["same_side_open"]])
    return rows


def feature_csv_rows(rows):
    """Stable no-outcome mask contract; explicit0/1 avoids CSV truthiness."""
    flags = {"keep_BASE", "keep_RS_OPEN_LOSS", "keep_SAME_SIDE_OPEN", "keep_PRICE_0901", "source_known", "same_side_open", "native_required_keys_known"}
    return [{key: (int(row[key]) if row[key] is not None else "") if key in flags else row[key]
        for key in FEATURE_CSV_FIELDS} for row in rows]


def combinatorial_support(rows, scheme):
    groups = defaultdict(list)
    for row in rows:
        if not row["known_state"] and not row["keep_RS_OPEN_LOSS"]: raise ValueError("Unknown source row must stay fixed-kept.")
        key = (row["year"], row["side"], row["PRICE_0901_sign"]) if scheme == "A" else (row["year"], row["side"], row["known_state"], row["same_side_open"])
        groups[key].append(row)
    cells = []; product = 1; variable = 0
    for key, members in sorted(groups.items(), key=lambda item: str(item[0])):
        fixed = [row for row in members if not row["known_state"]]
        pool = [row for row in members if row["known_state"]]
        n, k = len(pool), sum(row["keep_RS_OPEN_LOSS"] for row in pool)
        choices = comb(n, k); product *= choices; variable += int(0 < k < n)
        cells.append(dict(stratum=list(key), all_event_ids=[row["event_id"] for row in members],
            fixed_unknown_kept_event_ids=[row["event_id"] for row in fixed], randomizable_event_ids=[row["event_id"] for row in pool],
            all_rows=len(members), primary_kept_total=sum(row["keep_RS_OPEN_LOSS"] for row in members),
            randomizable_n=n, randomizable_kept_k=k, exact_choices=str(choices), variable_cell=0 < k < n))
    return dict(scheme=scheme, strata="year,side,PRICE0901sign" if scheme == "A" else "year,side,known-state,same-side-open",
        exact_distinct_mask_count=str(product), variable_cells=variable, minimum_distinct_masks=1000,
        passed=product >= 1000 and variable >= 1, cells=cells, source_unknown_kept_fixed_in_every_mask=True,
        masks_or_return_paths_sampled=False, no_joint_open_and_adverse_sign_matching=True)


def support_gate(rows, null_a, null_b):
    kept = [row for row in rows if row["keep_RS_OPEN_LOSS"]]; removed = [row for row in rows if not row["keep_RS_OPEN_LOSS"]]
    known = sum(row["known_state"] for row in rows); fraction = known / len(rows) if rows else 0.
    side_kept = {str(side): sum(row["side"] == side for row in kept) for side in (-1, 1)}
    removed_years = sorted({row["year"] for row in removed}); native_complete = bool(rows) and all(row["native_required_keys_known"] for row in rows)
    passed = bool(native_complete and fraction >= .90 and len(kept) >= 100 and len(removed) >= 20
        and len(removed_years) >= 3 and min(side_kept.values()) >= 10 and null_a["passed"] and null_b["passed"])
    return dict(phase="FEATURES_SUPPORT_only", passed=passed, parent_events=len(rows), known_state_events=known,
        known_fraction=fraction, minimum_known_fraction=.90, primary_kept=len(kept), primary_removed=len(removed),
        primary_removed_years=removed_years, primary_kept_by_side=side_kept, required_native_mark_reference_complete=native_complete,
        null_A_pass=null_a["passed"], null_B_pass=null_b["passed"], gross_screen_runs=0, economic_evaluations=0,
        raw_or_stopped_returns_calculated=False, future_event_fields_or_global_noncanonical_date_summary_used_for_masks=False,
        primary_is_price_sign_times_same_side_open_interaction=True,
        known_flat_uses_declared_report_coverage_assumption=True, independently_verified_live_or_MC_completeness=False,
        H01_H04_rawspec_source_limitations_cleared=False,
        next_action="Feature/supportPASS only; separately committed gross remains required" if passed else "CloseH07beforegross/economicoutcomes; no threshold/clock/null rescue")


def counts(rows):
    output = []
    for model in MODELS:
        for subset in ("kept", "removed"):
            selected = [row for row in rows if row["keep_" + model] == (subset == "kept")]
            for year in ("2018-22", *map(str, YEARS)):
                period = selected if year == "2018-22" else [row for row in selected if row["year"] == int(year)]
                for side in ("both", "long", "short"):
                    group = period if side == "both" else [row for row in period if row["side"] == (1 if side == "long" else -1)]
                    output.append(dict(model=model, subset=subset, period=year, side=side, events=len(group), known_state_events=sum(row["known_state"] for row in group)))
    return output


def recheck(bound):
    for name, expected in bound["hashes"].items():
        if sha(ROOT / name) != expected: raise ValueError("H07 FEATURES bound file changed:" + name)


@contextmanager
def lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "features.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB); yield


def features(prereg, source_sha):
    with lock():
        bound, stream = source_proof(prereg, source_sha); started = now()
        dump("features_attempt.json", dict(started_utc=started, prereg=bound["prereg"], implementation_commit=bound["implementation_commit"], source_marker_sha256=source_sha, script_sha256=sha(ROOT / SCRIPT)))
        names = ["features_attempt.json"]; stage = "immutable_parent_selected_metadata"
        try:
            parent = parent_metadata()
            stage = "only_exact_native_C840_and_O541_marks"
            marks, ledger = collect_native_marks(parent, bound)
            stage = "strict_asof_prefix_and_fixed_masks"
            rows = feature_rows(parent, marks, stream)
            a, b = combinatorial_support(rows, "A"), combinatorial_support(rows, "B")
            gate = support_gate(rows, a, b)
            dump("features_native_marks.json", ledger); dump("features_rows.json", rows)
            csv_once("features.csv", feature_csv_rows(rows), FEATURE_CSV_FIELDS)
            dump("features_null_support_A.json", a); dump("features_null_support_B.json", b)
            csv_once("features_counts.csv", counts(rows), ("model", "subset", "period", "side", "events", "known_state_events"))
            names += ["features_native_marks.json", "features_rows.json", "features.csv", "features_null_support_A.json", "features_null_support_B.json", "features_counts.csv"]
        except Exception as error:
            gate = dict(phase="FEATURES_SUPPORT_only", passed=False, status="SOURCE_FEATURE_OR_IMPLEMENTATION_BLOCKED", stage=stage,
                exception_type=type(error).__name__, exception_message=str(error), gross_screen_runs=0, economic_evaluations=0, raw_or_stopped_returns_calculated=False)
            dump("features_exception.json", dict(gate, traceback=traceback.format_exc())); names.append("features_exception.json")
        recheck(bound)
        dump("features_gate.json", gate); dump("features_input_binding.json", bound)
        names += ["features_gate.json", "features_input_binding.json"]
        if (OUT / "features_pre_mark_binding.json").exists(): names.append("features_pre_mark_binding.json")
        marker = dict(started_utc=started, completed_utc=now(), phase="FEATURES_SUPPORT_only", passed=gate["passed"],
            prereg=bound["prereg"], implementation_commit=bound["implementation_commit"], source_marker_sha256=source_sha,
            script_sha256=sha(ROOT / SCRIPT), artifacts_sha256={name: sha(OUT / name) for name in names},
            gross_screen_runs=0, economic_evaluations=0, raw_or_stopped_returns_calculated=False,
            parent_source_or_RS_path_reexecuted=False, actual_new_feature_masks_only=True,
            next_outcome_phase_authorized=False, retry_authorized=False)
        dump("features_verified_execution.json", marker)
        return gate


def fixtures():
    def coverage():
        a, b = META._setting_bound("2017-01-01", False), META._setting_bound("2023-01-01", False)
        return dict(passed=True, supported_start_exact=a, supported_end_exact=b)
    def source(events): return dict(global_pass=True, settings=coverage(), events=events, noncanonical_entry_dates=["2020-01-02"])
    def mark(value): return dict(known=True, value=str(value), source_rows=[])
    entry = dict(date="2020-01-02", minute=541, type="ENTRY", side=1, entry=100., trade_id=1)
    later = dict(date="2020-01-02", minute=900, type="EXIT", side=1, trade_id=1)
    state = asof_state(source([entry, later]), "2020-01-02", 1, mark(99), mark(100))
    assert state["known_state"] and state["same_side_open"] and state["current_position_adverse"]
    for minute in (841, 850, 899):
        changed = dict(later, minute=minute, entry="POISON_UNUSED_EXIT_PRICE", quantity="POISON_UNUSED_FUTURE_QTY")
        assert asof_state(source([entry, changed]), "2020-01-02", 1, mark(99), mark(100)) == state
    assert asof_state(source([entry, dict(later, minute=840)]), "2020-01-02", 1, mark(99), mark(100))["state"] == "UNKNOWN"
    assert asof_state(source([entry, dict(later, minute=839)]), "2020-01-02", 1, mark(99), mark(100))["state"] == "FLAT"
    assert asof_state(source([dict(entry, minute=542), later]), "2020-01-02", 1, mark(99), mark(100))["state"] == "UNKNOWN"
    assert asof_state(source([dict(entry, entry=100.25), later]), "2020-01-02", 1, mark(99), mark(100))["state"] == "UNKNOWN"
    flat = asof_state(source([]), "2020-01-02", 1, mark(99), mark(100))
    future_entry = dict(entry, minute=850, entry="POISON_FUTURE_ENTRY_PRICE", canonical_entry_clock=False)
    assert asof_state(source([future_entry]), "2020-01-02", 1, mark(99), mark(100)) == flat
    try: asof_state(dict(source([]), global_pass=False), "2020-01-02", 1, mark(99), mark(100))
    except ValueError: pass
    else: raise AssertionError("Global source fault selectively converted into a feature mask.")
    checks = ["asofprefixstrict/boundary840UNKNOWN/closedbefore840", "futureexit+entry+noncanonicalsummarypoisoninvariance", "basis/noncanonicalprefixUNKNOWNKEEP;globalfaultblocksfeatures"]
    parent = [dict(event_id=0, date="2020-01-02", year=2020, side=1,
        parent_source_csv_record=2, decision_j=840, entry_label_j=841, exit_label_j=870)]
    marks = {("2020-01-02", 840): mark(99), ("2020-01-02", 541): mark(100)}
    row = feature_rows(parent, marks, source([entry, later]))[0]
    assert not row["keep_RS_OPEN_LOSS"] and not row["keep_SAME_SIDE_OPEN"] and not row["keep_PRICE_0901"]
    no_rs = feature_rows(parent, marks, source([]))[0]
    assert no_rs["keep_RS_OPEN_LOSS"] and no_rs["keep_SAME_SIDE_OPEN"] and not no_rs["keep_PRICE_0901"]
    assert feature_rows(parent, {**marks, ("2020-01-02", 840): mark(100)}, source([entry, later]))[0]["keep_RS_OPEN_LOSS"]
    checks.append("primaryexactprice-times-overlapinteraction;pricecontrolindependentRS;zeroKEEP")
    contract = feature_csv_rows([row])[0]
    assert set(contract) == set(FEATURE_CSV_FIELDS) and contract["source_known"] == 1 and contract["keep_RS_OPEN_LOSS"] == 0
    assert contract["stratum_A"] == [2020, 1, "NEGATIVE"] and contract["stratum_B"] == [2020, 1, True, True]
    unknown_row = feature_rows(parent, marks, source([dict(entry, minute=542), later]))[0]
    unknown_contract = feature_csv_rows([unknown_row])[0]
    assert unknown_contract["source_known"] == 0 and unknown_contract["same_side_open"] == "" and unknown_contract["keep_RS_OPEN_LOSS"] == 1
    assert unknown_contract["keep_PRICE_0901"] == 0  # Independent price control even when own state unknown.
    checks.append("stableCSVmaskcontract/explicit0and1/JSONboolnullstrata/unknownPRICEindependence")
    positions = dict(date=0, time=1, open=2, close=3)
    raw = [(2, ["20200102", "901", "100", "POISON_UNSELECTED_CLOSE"]), (3, ["20200102", "1400", "POISON_UNSELECTED_OPEN", "99"]),
        (4, ["20200102", "1430", "POISON_EXIT_OPEN", "POISON_EXIT_CLOSE"]), (5, ["20230102", "1400", "POISON_FUTURE", "POISON_FUTURE"])]
    # Future-source rows are not an allowed annual file; test unrelated design
    # date poison instead, preserving the strict file-year metadata guard.
    raw[-1] = (5, ["20200103", "1400", "POISON_OTHER_DATE", "POISON_OTHER_DATE"])
    selected = select_mark_rows(raw, positions, "data/NQ_1min_2020.csv", {"2020-01-02"})
    assert set(selected) == {("2020-01-02", 541), ("2020-01-02", 840)} and all(r["valid"] for group in selected.values() for r in group)
    checks.append("nativekey+fieldselectionBEFOREnumbers;noC870/O841/unselectedcolumnorotherdateconversion")
    synthetic = []
    for year in YEARS:
        for side in (-1, 1):
            for index in range(20):
                synthetic.append(dict(event_id=len(synthetic), year=year, side=side, PRICE_0901_sign="NEGATIVE", known_state=True,
                    same_side_open=True, keep_RS_OPEN_LOSS=index >= 5, native_required_keys_known=True))
    synthetic.append(dict(event_id=999, year=2020, side=1, PRICE_0901_sign="NEGATIVE", known_state=False, same_side_open=None, keep_RS_OPEN_LOSS=True, native_required_keys_known=True))
    a, b = combinatorial_support(synthetic, "A"), combinatorial_support(synthetic, "B")
    assert a["passed"] and b["passed"] and any(999 in cell["fixed_unknown_kept_event_ids"] for cell in a["cells"])
    assert support_gate(synthetic, a, b)["passed"]
    saturated = [dict(item, keep_RS_OPEN_LOSS=True) for item in synthetic]
    assert not combinatorial_support(saturated, "A")["passed"]
    assert not support_gate(saturated, combinatorial_support(saturated, "A"), combinatorial_support(saturated, "B"))["passed"]
    checks.append("bothdistinctnullcombinatorialcounts/variablecells/unknownfixedKEEP;supportthresholds/saturationfail")
    return dict(passed=True, checks=checks, actual_RS_native_parent_outcome_or_source_artifacts_read=False,
        raw_or_stopped_returns_calculated=False, script_sha256=sha(ROOT / SCRIPT), gross_screen_runs=0, economic_evaluations=0)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--phase", choices=("fixtures", "features"), required=True)
    parser.add_argument("--prereg", default=PREREG); parser.add_argument("--source-sha")
    args = parser.parse_args()
    if args.phase == "fixtures":
        result = fixtures(); dump("features_synthetic_checks_" + result["script_sha256"][:12] + ".json", result)
    else:
        if not args.source_sha: parser.error("FEATURES requires exact SOURCE PASS --source-sha; no outcome phase exists here.")
        result = features(args.prereg, args.source_sha)
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__": main()
