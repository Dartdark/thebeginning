"""I03: frozen native/OF key and same-key OHLC quality, never data repair.

Import/fixtures read no owned CSV rows. Stage A interprets metadata strings
only, saves common/probe sets before any numeric conversion. Stage B inspects
ALL frozen common keys, SAVES their outputs, then ONLY frozen OF-only probes.
No temporal price arithmetic, signal, return, grid, strategy or account exists.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import contextmanager
import csv
from datetime import date, datetime, timedelta, timezone
import fcntl
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import traceback

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "analysis/codex_hunt_v2_native_OF_gap_intake.py"
HELPER = "analysis/codex_hunt_v2_native_OF_gap_numeric.py"
PLAN = "agents/codex/plans/hunt_v2_native_OF_gap_intake.md"
SOURCE_NOTE = "agents/codex/research/hunt_v2_native_OF_gap_source.md"
SOURCE_MANIFEST = "agents/codex/inputs/hunt_v2_native_OF_gap_intake/source_manifest.json"
OLD_BINDING = "analysis/outputs/codex_hunt_v2_rs_classified_support/gross_input_binding.json"
OUT = ROOT / "analysis/outputs/codex_hunt_v2_native_OF_gap_intake"
YEARS = tuple(range(2018, 2023))
INPUT_NAMES = tuple([f"data/NQ_1min_{y}.csv" for y in YEARS] + [f"data/OF_1min_{y}_{part}.csv" for y in YEARS for part in range(1, 5)])
NATIVE_FIELDS = ("open", "high", "low", "close", "volume")
OF_FIELDS = (*NATIVE_FIELDS, "upvol", "downvol")
DATE_RE = re.compile(r"^[0-9]{8}$")
TIME_RE = re.compile(r"^[0-9]{1,4}$")
sys.path.insert(0, str(ROOT / "analysis"))
from codex_s03_calendar import calendar_status


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_bytes(ref, name):
    return subprocess.check_output(["git", "show", f"{ref}:{name}"], cwd=ROOT)


def dump_once(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, allow_nan=False); handle.write("\n")


@contextmanager
def text_output_once(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.name.endswith(".gz"):
        with path.open("xb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
                with io.TextIOWrapper(compressed, encoding="utf-8", newline="") as handle:
                    yield handle
    else:
        with path.open("x", encoding="utf-8", newline="") as handle:
            yield handle


@contextmanager
def csv_output(path, fields):
    with text_output_once(path) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); yield writer


def source_key(raw_date, raw_time, source_year, kind):
    """Only ASCII metadata; exact documented ET-minus60, including date rollover."""
    d, t = raw_date.strip(" \t\r\n"), raw_time.strip(" \t\r\n")
    if DATE_RE.fullmatch(d) is None or TIME_RE.fullmatch(t) is None:
        raise ValueError("Date requires8ASCII digits and time1--4ASCII HHMM digits.")
    day = date(int(d[:4]), int(d[4:6]), int(d[6:8]))
    if day.year != source_year: raise ValueError("Source date year contradicts frozen annual file.")
    number = int(t); hour, minute = divmod(number, 100)
    if not (0 <= hour < 24 and 0 <= minute < 60): raise ValueError("Impossible HHMM metadata.")
    stamp = datetime.combine(day, datetime.min.time()) + timedelta(hours=hour, minutes=minute)
    if kind == "OF": stamp -= timedelta(minutes=60)
    elif kind != "native": raise ValueError("Unregistered source kind.")
    return stamp.date().isoformat(), stamp.hour * 60 + stamp.minute


def kind_year(name):
    if name not in INPUT_NAMES: raise ValueError("Input outside explicit25-file allowlist.")
    if name.startswith("data/NQ_"): return "native", int(Path(name).stem[-4:])
    return "OF", int(Path(name).name.split("_")[2])


def source_id(name, record_id):
    return f"{name}:CSVrecord{record_id}"


def calendar_universe():
    calendar, expected = [], set()
    day = date(2018, 1, 1)
    while day <= date(2022, 12, 31):
        label = day.isoformat(); status = calendar_status(label)
        normal = status["kind"] == "normal" and day.weekday() < 5
        calendar.append(dict(date=label, year=day.year, weekday=day.weekday(), calendar_kind=status["kind"],
            cash_close_j=status["cash_close_j"], calendar_reason=status["reason"], expected_RTH_keys=390 if normal else 0))
        if normal: expected.update((label, j) for j in range(511, 901))
        day += timedelta(days=1)
    return calendar, frozenset(expected)


def metadata_rows(numbered_rows, name):
    """Rows contain only date/time strings. No numeric source field is accessed."""
    kind, year = kind_year(name)
    keys, issues, count = defaultdict(list), [], 0
    for record_id, raw_date, raw_time in numbered_rows:
        count += 1; ident = source_id(name, record_id)
        try: key = source_key(raw_date, raw_time, year, kind)
        except (ValueError, TypeError, OverflowError) as error:
            issues.append(dict(source_id=ident, raw_date=raw_date, raw_time=raw_time, issue=str(error))); continue
        keys[key].append(ident)
    return dict(keys=keys, issues=issues, source_rows=count, kind=kind, year=year, path=name)


def selected_csv_rows(name, requested_fields):
    """CSV remains strings; interpret selected metadata/fields only, never extras."""
    with (ROOT / name).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, strict=True)
        header = next(reader)
        if len(header) != len(set(header)): raise ValueError("Duplicate CSV header names:" + name)
        positions = {field: header.index(field) for field in requested_fields}
        for record_id, row in enumerate(reader, start=2):
            if len(row) != len(header): raise ValueError(f"CSVrecord{record_id} has wrong width:" + name)
            yield record_id, {field: row[index] for field, index in positions.items()}


def stage_a(binding):
    calendar, expected = calendar_universe()
    combined = {"native": defaultdict(list), "OF": defaultdict(list)}
    source_audits, issues, outside, duplicates = [], [], Counter(), []
    for name in INPUT_NAMES:
        raw = ((record_id, fields["date"], fields["time"]) for record_id, fields in selected_csv_rows(name, ("date", "time")))
        result = metadata_rows(raw, name)
        for key, ids in result["keys"].items():
            combined[result["kind"]][key].extend(ids)
            if key not in expected:
                mapped = date.fromisoformat(key[0]); status = calendar_status(key[0])
                outside[(name, mapped.year, status["kind"], "RTH" if 511 <= key[1] <= 900 else "outside_RTH")] += len(ids)
        issues.extend(result["issues"])
        source_audits.append(dict(path=name, kind=result["kind"], source_year=result["year"],
            source_rows=result["source_rows"], valid_metadata_rows=sum(map(len, result["keys"].values())),
            unique_mapped_keys=len(result["keys"]), invalid_metadata_rows=len(result["issues"])))
    for kind, mapping in combined.items():
        for key, ids in mapping.items():
            if len(ids) > 1:
                duplicates.append(dict(kind=kind, date=key[0], minute=key[1], source_ids=ids,
                    selected_numeric_fields_read=False, expected_normal_RTH_key=key in expected))
    common, probes = set(), set()
    states, daily = Counter(), defaultdict(Counter)
    presence_fields = ("date", "year", "calendar_kind", "minute", "presence", "native_source_ids", "OF_source_ids")
    with csv_output(OUT / "stage_a_presence.csv.gz", presence_fields) as writer:
        for key in sorted(expected):
            nids, oids = combined["native"].get(key, []), combined["OF"].get(key, [])
            state = "BOTH" if nids and oids else "NATIVE_ONLY" if nids else "OF_ONLY" if oids else "NEITHER"
            if state == "BOTH": common.add(key)
            if state == "OF_ONLY": probes.add(key)
            states[state] += 1; daily[key[0]][state] += 1
            writer.writerow(dict(date=key[0], year=int(key[0][:4]), calendar_kind="normal", minute=key[1], presence=state,
                native_source_ids=json.dumps(nids), OF_source_ids=json.dumps(oids)))
    key_fields = ("date", "year", "minute", "native_source_ids", "OF_source_ids")
    for filename, keys in (("stage_a_common_keys.csv.gz", common), ("stage_a_OF_only_probes.csv.gz", probes)):
        with csv_output(OUT / filename, key_fields) as writer:
            for key in sorted(keys):
                writer.writerow(dict(date=key[0], year=int(key[0][:4]), minute=key[1],
                    native_source_ids=json.dumps(combined["native"].get(key, [])), OF_source_ids=json.dumps(combined["OF"].get(key, []))))
    with csv_output(OUT / "stage_a_calendar_daily_counts.csv", ("date", "year", "weekday", "calendar_kind", "cash_close_j", "calendar_reason", "expected_RTH_keys", "BOTH", "NATIVE_ONLY", "OF_ONLY", "NEITHER")) as writer:
        for item in calendar: writer.writerow(dict(item, **{state: daily[item["date"]][state] for state in ("BOTH", "NATIVE_ONLY", "OF_ONLY", "NEITHER")}))
    dump_once(OUT / "stage_a_duplicate_ID_groups.json", dict(groups=duplicates, numeric_duplicate_equivalence_not_yet_interpreted=True))
    dump_once(OUT / "stage_a_metadata_audit.json", dict(source_audits=source_audits, invalid_metadata_rows=issues,
        outside_expected_metadata_counts=[dict(path=p, mapped_year=y, calendar_kind=k, clock_region=r, source_rows=n)
            for (p, y, k, r), n in sorted(outside.items())], presence_counts=dict(states), expected_keys=len(expected),
        metadata_pass=not issues, prices_or_quantities_converted=False))
    stage_names = ["stage_a_presence.csv.gz", "stage_a_common_keys.csv.gz", "stage_a_OF_only_probes.csv.gz",
        "stage_a_calendar_daily_counts.csv", "stage_a_duplicate_ID_groups.json", "stage_a_metadata_audit.json"]
    frozen = dict(stage="A_metadata_complete_before_numeric", metadata_pass=not issues,
        common_keys=len(common), OF_only_keys=len(probes), expected_keys=len(expected),
        status="NOT_TESTABLE_METADATA" if issues else "NO_ADDITIONAL_KEYS" if not probes else "FROZEN_FOR_PREAUTHORIZED_NUMERIC",
        artifacts_sha256={name: sha(OUT / name) for name in stage_names},
        fixed_key_set_sha256=sha_bytes(json.dumps([list(k) for k in sorted(expected)], separators=(",", ":")).encode()),
        numeric_values_converted=False, primary_source_provenance_admitted=False)
    dump_once(OUT / "stage_a_frozen_sets.json", frozen)
    return combined, frozenset(common), frozenset(probes), frozen


def numeric_selection(numbered, name, keys):
    """Membership BEFORE parsing: unselected OHLC/quantity strings stay opaque."""
    kind, year = kind_year(name); fields = NATIVE_FIELDS if kind == "native" else OF_FIELDS
    selected = defaultdict(list)
    for record_id, raw in numbered:
        key = source_key(raw["date"], raw["time"], year, kind)
        if key not in keys: continue
        selected[key].append(dict(source_id=source_id(name, record_id), **{field: raw[field] for field in fields}))
    return selected


def numeric_groups_for_year(year, keys, expected_ids):
    groups = {"native": defaultdict(list), "OF": defaultdict(list)}
    for name in INPUT_NAMES:
        kind, source_year = kind_year(name)
        if source_year != year: continue
        fields = ("date", "time", *(NATIVE_FIELDS if kind == "native" else OF_FIELDS))
        for key, rows in numeric_selection(selected_csv_rows(name, fields), name, keys).items():
            groups[kind][key].extend(rows)
    for kind, values in groups.items():
        for key, rows in values.items():
            if [row["source_id"] for row in rows] != expected_ids[kind].get(key, []):
                raise ValueError("Stage-A source IDs changed before numeric conversion.")
    return groups


def recheck_frozen_sets(frozen):
    for name, expected in frozen["artifacts_sha256"].items():
        if sha(OUT / name) != expected: raise ValueError("Frozen Stage-A key/probe artifact changed:" + name)


def common_stage(common, ids, frozen):
    from codex_hunt_v2_native_OF_gap_numeric import parse_selected_group, compare_groups
    recheck_frozen_sets(frozen)
    summary = Counter(); strata = defaultdict(Counter)
    fields = ("date", "year", "calendar_kind", "minute", "native_source_ids", "OF_source_ids", "native_status", "OF_status",
        "comparable", "OHLC_comparable", "quantity_comparable", "both_valid", "exact_OHLC_tuple", "within_one_tick_OHLC_tuple", "native_volume_equals_OF_aux_total", "OF_alias_pass",
        *[f"{name}_{suffix}" for name in ("open", "high", "low", "close") for suffix in ("exact", "abs_error_ticks", "within_one_tick")])
    with csv_output(OUT / "stage_b_common_concordance.csv.gz", fields) as writer:
        with text_output_once(OUT / "stage_b_common_mismatch_observations.jsonl.gz") as mismatch:
            for year in YEARS:
                keys = frozenset(key for key in common if int(key[0][:4]) == year)
                groups = numeric_groups_for_year(year, keys, ids)
                if set(groups["native"]) != set(keys) or set(groups["OF"]) != set(keys):
                    raise ValueError("A frozen common key disappeared before numeric stage.")
                for key in sorted(keys):
                    n = parse_selected_group(groups["native"][key], "native")
                    o = parse_selected_group(groups["OF"][key], "OF")
                    pair = compare_groups(n, o)
                    result = dict(date=key[0], year=year, calendar_kind="normal", minute=key[1],
                        native_source_ids=json.dumps(n["source_ids"]), OF_source_ids=json.dumps(o["source_ids"]),
                        native_status=n["status"], OF_status=o["status"])
                    for field in ("comparable", "OHLC_comparable", "quantity_comparable", "both_valid", "exact_OHLC_tuple", "within_one_tick_OHLC_tuple", "native_volume_equals_OF_aux_total", "OF_alias_pass"):
                        result[field] = pair[field]
                    for field in ("open", "high", "low", "close"):
                        for suffix in ("exact", "abs_error_ticks", "within_one_tick"):
                            result[f"{field}_{suffix}"] = pair["per_field"][field][suffix]
                    writer.writerow(result)
                    counts = {"keys": 1, "comparable": int(pair["comparable"]), "both_valid": int(pair["both_valid"]),
                        "OHLC_comparable": int(pair["OHLC_comparable"]), "quantity_comparable": int(pair["quantity_comparable"]),
                        "exact_OHLC_tuple": int(pair["exact_OHLC_tuple"] is True),
                        "within_one_tick_OHLC_tuple": int(pair["within_one_tick_OHLC_tuple"] is True),
                        "native_volume_equals_OF_aux_total": int(pair["native_volume_equals_OF_aux_total"] is True),
                        "OF_alias_pass": int(pair["OF_alias_pass"] is True)}
                    for field in ("open", "high", "low", "close"):
                        counts[field + "_exact"] = int(pair["per_field"][field]["exact"] is True)
                        counts[field + "_within_one_tick"] = int(pair["per_field"][field]["within_one_tick"] is True)
                    counts["native_unresolved"] = int(not n["resolved"]); counts["OF_unresolved"] = int(not o["resolved"])
                    counts["native_invalid"] = int(not n["valid"]); counts["OF_invalid"] = int(not o["valid"])
                    for label, group in (("native", n), ("OF", o)):
                        counts[label + "_format_variation_keys"] = int(group.get("format_variation", False))
                        counts[label + "_duplicate_excess_rows"] = group["duplicate_excess_rows"]
                        counts[label + "_any_zero_OHLC_keys"] = int(group.get("any_zero_OHLC", False))
                        counts[label + "_all_zero_OHLC_keys"] = int(group.get("all_zero_OHLC", False))
                        counts[label + "_any_zero_quantity_keys"] = int(bool(group.get("zero_quantity_fields", [])))
                        for issue in group["issues"]:
                            counts[label + "_issue_" + issue["issue"]] = counts.get(label + "_issue_" + issue["issue"], 0) + 1
                    summary.update(counts)
                    # Strata are frozen year/calendar/source paths; no concordance-driven subsets.
                    native_paths = sorted({row["source_id"].split(":CSVrecord")[0] for row in groups["native"][key]})
                    OF_paths = sorted({row["source_id"].split(":CSVrecord")[0] for row in groups["OF"][key]})
                    stratum = (year, "normal", "|".join(native_paths), "|".join(OF_paths))
                    strata[stratum].update(counts)
                    if (n["duplicate_excess_rows"] or o["duplicate_excess_rows"] or
                        not (pair["both_valid"] and pair["exact_OHLC_tuple"] and pair["native_volume_equals_OF_aux_total"] and pair["OF_alias_pass"])):
                        mismatch.write(json.dumps(dict(date=key[0], minute=key[1], native=n, OF=o, comparison=pair), allow_nan=False) + "\n")
    audit = dict(stage="B1_all_frozen_common_keys", status="DIAGNOSTIC_ONLY_NEEDS_PROVENANCE", counts=dict(summary),
        rates_over_ALL_common_keys={name: summary[name] / len(common) if common else None for name in
            ("comparable", "OHLC_comparable", "quantity_comparable", "both_valid", "exact_OHLC_tuple", "within_one_tick_OHLC_tuple",
                "native_volume_equals_OF_aux_total", "OF_alias_pass", *[f + suffix for f in ("open", "high", "low", "close") for suffix in ("_exact", "_within_one_tick")])},
        strata=[dict(year=y, calendar_kind=k, native_paths=n, OF_paths=o, counts=dict(counts)) for (y, k, n, o), counts in sorted(strata.items())],
        count_denominator="ALL fixed common keys; unresolved/invalid remain in denominator; no favorable deletion",
        one_tick_is_diagnostic_not_admission_threshold=True, temporal_returns_or_signals_calculated=False,
        primary_source_provenance_admitted=False)
    dump_once(OUT / "stage_b_common_summary.json", audit)
    names = ("stage_b_common_concordance.csv.gz", "stage_b_common_mismatch_observations.jsonl.gz", "stage_b_common_summary.json")
    checkpoint = dict(stage="B1_SAVED_BEFORE_ANY_OF_ONLY_NUMERIC_PROBE", artifacts_sha256={name: sha(OUT / name) for name in names},
        common_keys=len(common), OF_only_numeric_probes_converted=False)
    dump_once(OUT / "stage_b_common_saved_before_probes.json", checkpoint)
    return audit, checkpoint


def probe_stage(probes, ids, frozen, common_checkpoint):
    from codex_hunt_v2_native_OF_gap_numeric import parse_selected_group
    recheck_frozen_sets(frozen)
    for name, expected in common_checkpoint["artifacts_sha256"].items():
        if sha(OUT / name) != expected: raise ValueError("Common-key results changed before probe phase.")
    counts, by_year = Counter(), defaultdict(Counter)
    with text_output_once(OUT / "stage_b_OF_only_observations.jsonl.gz") as ledger:
        for year in YEARS:
            keys = frozenset(key for key in probes if int(key[0][:4]) == year)
            groups = numeric_groups_for_year(year, keys, ids)
            if groups["native"] or set(groups["OF"]) != set(keys):
                raise ValueError("Frozen OF-only probe identity changed.")
            for key in sorted(keys):
                result = parse_selected_group(groups["OF"][key], "OF")
                ledger.write(json.dumps(dict(date=key[0], year=year, calendar_kind="normal", minute=key[1],
                    native_observation_present=False, OF_standalone_observation=result,
                    native_bar_created=False, historical_receipt_or_gap_cause_verified=False), allow_nan=False) + "\n")
                item = dict(keys=1, resolved=int(result["resolved"]), valid=int(result["valid"]),
                    unresolved=int(not result["resolved"]), invalid=int(not result["valid"]),
                    any_zero_OHLC=int(result.get("any_zero_OHLC", False)), all_zero_OHLC=int(result.get("all_zero_OHLC", False)),
                    any_zero_quantity=int(bool(result.get("zero_quantity_fields", []))),
                    alias_pass=int(result.get("OF_volume_alias_pass") is True),
                    alias_fail=int(result.get("OF_volume_alias_pass") is False),
                    alias_unknown=int(result.get("OF_volume_alias_pass") is None),
                    format_variation_keys=int(result.get("format_variation", False)), duplicate_excess_rows=result["duplicate_excess_rows"])
                counts.update(item); by_year[year].update(item)
    audit = dict(stage="B2_exact_prebound_OF_only_probes", status="DIAGNOSTIC_ONLY_NEEDS_PROVENANCE", counts=dict(counts),
        by_year={str(y): dict(by_year[y]) for y in YEARS}, expected_prebound_probes=len(probes),
        primary_source_provenance_admitted=False, repaired_or_merged_native_grid_created=False,
        temporal_returns_or_signals_calculated=False, H03_H04_rerun_authorized=False)
    dump_once(OUT / "stage_b_OF_only_summary.json", audit)
    return audit


def after_stage_a(frozen, common_operation, probe_operation):
    """Injectable scope guard: no numeric operation on metadata/zero-key stop."""
    if not frozen["metadata_pass"]: return "NOT_TESTABLE_METADATA"
    if frozen["OF_only_keys"] == 0: return "NO_ADDITIONAL_KEYS"
    _, common_checkpoint = common_operation()
    probe_operation(common_checkpoint)
    return "DIAGNOSTIC_ONLY_NEEDS_PROVENANCE"


def verify_before_rows(prereg):
    if subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() != "codex/work":
        raise ValueError("I03 must remain on codex/work.")
    subprocess.check_call(["git", "merge-base", "--is-ancestor", prereg, "HEAD"], cwd=ROOT)
    for directory in (ROOT / "analysis/outputs").glob("codex_hunt_v2_native_OF_gap_intake*"):
        if (directory / "intake_verified_execution.json").exists() or (directory / "intake_attempt.json").exists():
            raise ValueError("Retained complete/partial I03 attempt exists; no automatic retry/alternate directory.")
    names = [SCRIPT, HELPER, PLAN, SOURCE_NOTE, SOURCE_MANIFEST, OLD_BINDING,
        "analysis/codex_s03_calendar.py", "analysis/replica.py", "agents/codex/RESEARCH_CONTROLS.md"]
    manifest = json.loads((ROOT / SOURCE_MANIFEST).read_text())
    if manifest.get("archival_source_only_never_executed") is not True:
        raise ValueError("Source archives must remain source-only.")
    for source in manifest["sources"]:
        name = source["path"]
        if not name.startswith("agents/codex/inputs/hunt_v2_native_OF_gap_intake/") or sha(ROOT / name) != source["sha256"]:
            raise ValueError("Exporter source archive differs from its registration.")
        names.append(name)
    for name in names:
        raw = (ROOT / name).read_bytes()
        if git_bytes(prereg, name) != raw or git_bytes("HEAD", name) != raw:
            raise ValueError("Freeze every I03 code/plan/source/dependency before rows:" + name)
    old = json.loads((ROOT / OLD_BINDING).read_text())
    by_name = {item["path"]: item for item in old["inventory"]}
    if len(by_name) != len(old["inventory"]): raise ValueError("Duplicate original inventory paths.")
    inventory, hashes = [], {name: sha(ROOT / name) for name in names}
    for name in INPUT_NAMES:
        registered = by_name.get(name)
        path = ROOT / name
        if registered is None or path.is_symlink(): raise ValueError("Missing/redirected original input:" + name)
        if path.stat().st_size != registered["bytes"] or sha(path) != registered["sha256"]:
            raise ValueError("Original H04 byte binding changed:" + name)
        with path.open("rb") as handle: header = handle.readline().decode("utf-8").rstrip("\r\n")
        if header != registered["header"]: raise ValueError("Original header binding changed:" + name)
        inventory.append(registered); hashes[name] = registered["sha256"]
    return dict(prereg=prereg, implementation_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        source_hashes=hashes, inventory=inventory, original_binding=OLD_BINDING,
        original_binding_implementation_commit=old["implementation_commit"], versions=dict(python=sys.version.split()[0], pandas=pd.__version__),
        source_clock="NativeCTclose;OFETclose-minus60withdaterollover;noalternateoffsets", no2017_ES_MC_2023plus_input=True,
        source_exports_executed=False, source_review_only_not_provenance_admission=True,
        fixed_scope=dict(years=list(YEARS), normal_weekday_minutes=[511, 900]))


@contextmanager
def execution_lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "intake.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB); yield


def intake(prereg):
    with execution_lock():
        binding = verify_before_rows(prereg); started = utcnow(); stage = "A_metadata"
        dump_once(OUT / "intake_attempt.json", dict(started_utc=started, prereg=prereg,
            implementation_commit=binding["implementation_commit"], script_sha256=sha(ROOT / SCRIPT)))
        dump_once(OUT / "intake_pre_rows_binding.json", binding)
        try:
            ids, common, probes, frozen = stage_a(binding)
            def run_common():
                nonlocal stage
                stage = "B1_ALL_common_key_numeric_concordance"
                return common_stage(common, ids, frozen)
            def run_probes(common_checkpoint):
                nonlocal stage
                stage = "B2_EXACT_prebound_OF_only_numeric_probes"
                return probe_stage(probes, ids, frozen, common_checkpoint)
            status = after_stage_a(frozen, run_common, run_probes)
        except Exception as error:
            status = "SOURCE_FORMAT_OR_IMPLEMENTATION_BLOCKED"
            dump_once(OUT / "intake_exception.json", dict(status=status, stage=stage,
                exception_type=type(error).__name__, exception_message=str(error), traceback=traceback.format_exc(),
                source_or_implementation_failure_not_alpha_rejection=True, automatic_retry_authorized=False))
        for name, expected in binding["source_hashes"].items():
            if sha(ROOT / name) != expected: raise ValueError("Bound I03 file changed; no verified completion:" + name)
        summary = dict(status=status, last_stage=stage, hypotheses_added=0, gross_screens_added=0, economic_evaluations_added=0,
            new_economic_signal_or_returns_calculated=False, primary_source_provenance_admitted=False,
            repaired_native_grid_or_gapfill_created=False, H03_H04_rescue_or_rerun_authorized=False,
            known_limits="Contract/roll/build/revision/receipt remain unverified; common concordance cannot authenticate missing native bar or halt cause.",
            running_budget=dict(counted_evaluations=3, max_evaluations=60, hypotheses=4, max_hypotheses=10, retained_gross_screens=2, archived_t6_evaluations=65))
        dump_once(OUT / "intake_summary.json", summary)
        names = sorted(path.name for path in OUT.iterdir() if path.is_file() and not path.name.startswith("synthetic_")
            and path.name not in (".gitignore", "intake.lock", "intake_verified_execution.json"))
        marker = dict(started_utc=started, completed_utc=utcnow(), phase="nonreturn_native_OF_quality_intake", status=status,
            last_stage=stage, prereg=prereg, implementation_commit=binding["implementation_commit"], script_sha256=sha(ROOT / SCRIPT),
            artifacts_sha256={name: sha(OUT / name) for name in names}, financial_experiment_run=False,
            hypotheses_added=0, gross_screens_added=0, economic_evaluations_added=0,
            primary_source_provenance_admitted=False, old_study_rerun_authorized=False, automatic_retry_authorized=False)
        dump_once(OUT / "intake_verified_execution.json", marker)
        return summary


def fixtures():
    global OUT, numeric_groups_for_year
    checks = []
    assert source_key("20180102", "0930", 2018, "OF") == ("2018-01-02", 510)
    assert source_key("20180101", "0030", 2018, "OF") == ("2017-12-31", 1410)
    assert source_key("20180102", "830", 2018, "native") == ("2018-01-02", 510)
    for raw_date, raw_time in (("20180230", "930"), ("20180102", "960"), ("20180102", "2400"), ("2018-01-02", "930"), ("20180102", "９３０"), ("20180102", "930.0")):
        try: source_key(raw_date, raw_time, 2018, "OF")
        except ValueError: pass
        else: raise AssertionError("Invalid metadata admitted.")
    checks.append("strictASCIIcalendar/HHMM;frozenET-60withdaterollover;invalidmappingfatal")
    cal, expected = calendar_universe()
    assert len(cal) == 1826 and ("2018-01-02", 511) in expected and ("2018-01-02", 900) in expected
    assert ("2018-01-02", 510) not in expected and ("2018-12-05", 600) not in expected
    assert not any(key[0] == "2018-11-23" for key in expected)
    checks.append("complete2018-22calendar;normalweekday511..900universeindependentofpresence")
    rows = [(2, "20180102", "831"), (3, "20180102", "831"), (4, "20180102", "832")]
    metadata = metadata_rows(rows, "data/NQ_1min_2018.csv")
    assert len(metadata["keys"][("2018-01-02", 511)]) == 2 and not metadata["issues"]
    checks.append("duplicatekeyalloriginalCSVrecordIDsretainedbeforenumericinterpretation")
    # Raw selected values deliberately poisonous outside the frozen key set.
    requested = frozenset({("2018-01-02", 511)})
    rows = [(2, dict(date="20180102", time="831", open="100", high="101", low="99", close="100", volume="10")),
        (3, dict(date="20180102", time="830", open="DO_NOT_CONVERT", high="DO_NOT_CONVERT", low="DO_NOT_CONVERT", close="DO_NOT_CONVERT", volume="DO_NOT_CONVERT"))]
    result = numeric_selection(rows, "data/NQ_1min_2018.csv", requested)
    assert set(result) == set(requested) and len(result[("2018-01-02", 511)]) == 1
    checks.append("fixedsetmembershipbeforeANYselectednumericconversion;outsideRTHpoisonuntouched")
    n, o = {1, 2}, {1, 3}
    presence = {key: "BOTH" if key in n and key in o else "NATIVE_ONLY" if key in n else "OF_ONLY" if key in o else "NEITHER" for key in (1, 2, 3, 4)}
    assert set(presence.values()) == {"BOTH", "NATIVE_ONLY", "OF_ONLY", "NEITHER"}
    assert tuple(INPUT_NAMES[:5]) == tuple(f"data/NQ_1min_{y}.csv" for y in YEARS) and len(INPUT_NAMES) == 25
    assert not any("2017" in name or "ES_" in name or "2023" in name for name in INPUT_NAMES)
    checks.append("allfourpresencestates;exact25originalNQ/OFinputs;no2017/ES/MC/2023")
    def forbidden(*args): raise AssertionError("Numeric operation reached after a Stage-A stop.")
    assert after_stage_a(dict(metadata_pass=True, OF_only_keys=0), forbidden, forbidden) == "NO_ADDITIONAL_KEYS"
    assert after_stage_a(dict(metadata_pass=False, OF_only_keys=3), forbidden, forbidden) == "NOT_TESTABLE_METADATA"
    order = []
    def artificial_common():
        order.append("common_saved"); return {}, {"synthetic_common_saved": True}
    def artificial_probes(checkpoint):
        assert checkpoint["synthetic_common_saved"] and order == ["common_saved"]
        order.append("probes")
    assert after_stage_a(dict(metadata_pass=True, OF_only_keys=1), artificial_common, artificial_probes) == "DIAGNOSTIC_ONLY_NEEDS_PROVENANCE"
    assert order == ["common_saved", "probes"]
    checks.append("Stage-Azero/invalidpreventsnumericcallbacks;commoncheckpointprecedesprobes;alwaysdiagnostic")
    original_out, original_builder = OUT, numeric_groups_for_year
    original_out.mkdir(parents=True, exist_ok=True)
    # Full common/probe integration uses artificial groups only. Never changes
    # the CLI's fixed actual output or allowlist, and never opens owned CSVs.
    with tempfile.TemporaryDirectory(prefix="synthetic_integration_", dir=original_out) as temporary:
        OUT = Path(temporary)
        key1, key2, probe = ("2018-01-02", 511), ("2018-01-02", 512), ("2018-01-02", 513)
        def raw(kind, ident, **changes):
            row = dict(source_id=ident, open="100", high="101", low="99", close="100.25", volume="10" if kind == "native" else "6")
            if kind == "OF": row.update(upvol="6", downvol="4")
            row.update(changes); return row
        def fake_builder(year, keys, unused_ids):
            if year != 2018: return {"native": {}, "OF": {}}
            if keys == frozenset({probe}):
                return {"native": {}, "OF": {probe: [raw("OF", "data/OF_1min_2018_1.csv:CSVrecord9", open="0", high="0", low="0", close="0")]}}
            native = {key1: [raw("native", "data/NQ_1min_2018.csv:CSVrecord2")],
                key2: [raw("native", "data/NQ_1min_2018.csv:CSVrecord3"), raw("native", "data/NQ_1min_2018.csv:CSVrecord4", high="101.25")]}
            of = {key: [raw("OF", f"data/OF_1min_2018_1.csv:CSVrecord{j}")] for j, key in enumerate((key1, key2), start=2)}
            return {"native": {k: v for k, v in native.items() if k in keys}, "OF": {k: v for k, v in of.items() if k in keys}}
        numeric_groups_for_year = fake_builder
        try:
            frozen = dict(artifacts_sha256={})
            common_result, checkpoint = common_stage(frozenset({key1, key2}), {}, frozen)
            assert common_result["counts"]["keys"] == 2 and common_result["counts"]["native_unresolved"] == 1
            with gzip.open(OUT / "stage_b_common_concordance.csv.gz", "rt", newline="") as handle:
                common_rows = list(csv.DictReader(handle))
            assert len(common_rows) == 2 and common_rows[1]["native_status"] == "DUPLICATE_CONFLICT"
            with gzip.open(OUT / "stage_b_common_mismatch_observations.jsonl.gz", "rt") as handle:
                mismatch_rows = [json.loads(line) for line in handle]
            assert len(mismatch_rows) == 1 and len(mismatch_rows[0]["native"]["source_ids"]) == 2
            probe_result = probe_stage(frozenset({probe}), {}, frozen, checkpoint)
            assert probe_result["counts"]["keys"] == 1 and probe_result["counts"]["invalid"] == 1
            with gzip.open(OUT / "stage_b_OF_only_observations.jsonl.gz", "rt") as handle:
                retained_probe = json.loads(next(handle))
            assert retained_probe["native_bar_created"] is False
            # Same logical bytes -> identical compressed bytes (fixed mtime/name).
            for name in ("deterministic1.txt.gz", "deterministic2.txt.gz"):
                with text_output_once(OUT / name) as handle: handle.write("artificial-only\n")
            assert sha(OUT / "deterministic1.txt.gz") == sha(OUT / "deterministic2.txt.gz")
            artifact = OUT / "synthetic_probe_set.json"
            artifact.write_text('{"probe":"initial"}')
            guard = dict(artifacts_sha256={artifact.name: sha(artifact)})
            artifact.write_text('{"probe":"changed"}')
            try: recheck_frozen_sets(guard)
            except ValueError: pass
            else: raise AssertionError("Mutated frozen probe set admitted.")
        finally:
            OUT, numeric_groups_for_year = original_out, original_builder
    checks.append("common-stageunresolvedduplicateintegrationretainsALLIDs/unknownperfields;noKeyError/nofavorablechoice")
    checks.append("commonoutputsSAVEDbeforefixedprobe;invalidzeroOFobservationretainedstandalone/nogrid")
    checks.append("deterministicgzipmtime0allrecordsretained;compressedhashbinding;mutatedprobesetrejected")
    return dict(passed=True, checks=checks, real_CSV_rows_or_numeric_values_read=False,
        temporal_returns_signals_prices_across_time_calculated=False, script_sha256=sha(ROOT / SCRIPT),
        hypotheses_added=0, gross_screens_added=0, economic_evaluations_added=0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=("fixtures", "intake")); parser.add_argument("--prereg")
    args = parser.parse_args()
    if args.phase == "fixtures":
        result = fixtures(); dump_once(OUT / f"synthetic_checks_{result['script_sha256'][:12]}.json", result)
    else:
        if not args.prereg: parser.error("Intake requires committed --prereg.")
        result = intake(args.prereg)
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__": main()
