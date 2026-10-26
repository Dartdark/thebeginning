"""I04 single pinned collector metadata intake; NO margin-value interpretation.

Import and fixtures never download/open the archive. Only timestamp/product/
contract-bucket/currency metadata fields are accessed after exact byte checks.
Maintenance and all other financial cells remain opaque, even on target rows.
Poll timestamps are not exchange announcement/effective/receipt timestamps.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import contextmanager
import csv
from datetime import date, datetime, timezone
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
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_hunt_v2_cme_margin_metadata"
SCRIPT = "analysis/codex_hunt_v2_cme_margin_metadata.py"
PLAN = "agents/codex/plans/hunt_v2_cme_margin_metadata_intake.md"
EVIDENCE = "agents/codex/evidence/hunt_v2_new_primary_nomination.md"
NOTE = "agents/codex/research/hunt_v2_new_primary_nomination.md"
IGNORE = "analysis/outputs/codex_hunt_v2_cme_margin_metadata/.gitignore"
SOURCE_REPOSITORY = "BrunoProgramming/cme_margin"
SOURCE_COMMIT = "93cc090bd7f680292436012b13c4e6fb44fc411f"
SOURCE_PATH = "data/cme_margin.csv"
SOURCE_URL = "https://raw.githubusercontent.com/BrunoProgramming/cme_margin/93cc090bd7f680292436012b13c4e6fb44fc411f/data/cme_margin.csv"
SOURCE_BYTES = 26989907
SOURCE_GIT_BLOB = "21c9202c0918bd2ea017fa80baeb1e467e10241c"
DOWNLOAD_TIMEOUT = 45
REQUIRED_HEADERS = ("Time", "Exchange", "Asset Class", "Product Name", "Product Code", "Start Period", "End Period", "Maintenance", "Currency", "Maint. Vol. Scan")
METADATA_FIELDS = ("Time", "Exchange", "Asset Class", "Product Name", "Product Code", "Start Period", "End Period", "Currency")
IDENTITY_FIELDS = ("Exchange", "Asset Class", "Product Name", "Product Code", "Currency")
BUCKET_FIELDS = ("Exchange", "Asset Class", "Product Code", "Start Period", "End Period", "Currency")
TARGETS = ("NQ", "MNQ", "ES", "MES")
ASCII_SPACE = " \t\r\n\v\f"
TIME_RE = re.compile(r"^(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})[ T](?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2})(?:\.(?P<fraction>[0-9]{1,9}))?(?:Z|\+00:00)$")
FINAL_STATUS = "DIAGNOSTIC_ONLY_NEEDS_PRIMARY_CLOCK_AND_HISTORY"


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""): digest.update(block)
    return digest.hexdigest()


def git_blob_sha(path):
    path = Path(path)
    digest = hashlib.sha1(b"blob " + str(path.stat().st_size).encode("ascii") + b"\0")
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""): digest.update(block)
    return digest.hexdigest()


def dump_once(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, allow_nan=False); handle.write("\n")


@contextmanager
def text_output(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.name.endswith(".gz"):
        with path.open("xb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
                with io.TextIOWrapper(compressed, encoding="utf-8", newline="") as handle: yield handle
    else:
        with path.open("x", encoding="utf-8", newline="") as handle: yield handle


def timestamp_metadata(raw):
    """Exact integer nanoseconds, no float/epoch guess or microsecond truncation."""
    if not isinstance(raw, str): raise ValueError("Time must remain a raw CSV string.")
    match = TIME_RE.fullmatch(raw)
    if match is None: raise ValueError("Time requires real ISO date/HH:MM:SS,0--9fractiondigits and explicit Z/+00:00.")
    g = match.groupdict()
    day = date(int(g["year"]), int(g["month"]), int(g["day"]))
    hour, minute, second = (int(g[name]) for name in ("hour", "minute", "second"))
    if not (0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60): raise ValueError("Impossible UTC clock.")
    fraction = g["fraction"] or ""
    ns = int(fraction.ljust(9, "0") or "0")
    clock = (day.toordinal(), hour * 3600 + minute * 60 + second, ns)
    return dict(raw=raw, UTC_date=day.isoformat(), UTC_year=day.year, fraction_raw=fraction,
        fractional_precision_digits=len(fraction), canonical_UTC_ns=f"{day.isoformat()}T{hour:02d}:{minute:02d}:{second:02d}.{ns:09d}Z",
        clock_key=clock, original_offset="Z" if raw.endswith("Z") else "+00:00")


def schema_positions(header):
    if not isinstance(header, list) or any(not isinstance(label, str) for label in header): raise ValueError("Header must be exact strings.")
    if len(header) != len(set(header)): raise ValueError("Duplicate/ambiguous full header labels.")
    if not set(REQUIRED_HEADERS).issubset(header): raise ValueError("Required exact collector headers absent; no aliases inferred.")
    # Only permitted metadata column indexes are constructed/accessed.
    return {name: header.index(name) for name in METADATA_FIELDS}


def selected_metadata(row, positions):
    return {name: row[index] for name, index in positions.items()}


def metadata_source_rows(path, header):
    positions = schema_positions(header)
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, strict=True)
        if next(reader) != header: raise ValueError("Header changed between bound read and CSV metadata stage.")
        for record_id, row in enumerate(reader, start=2):
            if len(row) != len(header): raise ValueError(f"CSVrecord{record_id} width differs from frozen header.")
            yield record_id, selected_metadata(row, positions)


def coverage_state():
    return dict(rows=0, valid_time_rows=0, invalid_time_rows=0, first=None, last=None,
        unique_times=set(), unique_dates=set(), by_year=Counter())


def update_coverage(state, timestamp):
    state["rows"] += 1
    if timestamp is None:
        state["invalid_time_rows"] += 1; return
    state["valid_time_rows"] += 1
    key = tuple(timestamp["clock_key"])
    state["unique_times"].add(key); state["unique_dates"].add(timestamp["UTC_date"])
    state["by_year"][timestamp["UTC_year"]] += 1
    if state["first"] is None or key < tuple(state["first"]["clock_key"]): state["first"] = timestamp
    if state["last"] is None or key > tuple(state["last"]["clock_key"]): state["last"] = timestamp


def finalized_coverage(state):
    return dict(source_rows=state["rows"], valid_time_rows=state["valid_time_rows"], invalid_time_rows=state["invalid_time_rows"],
        first_valid_poll_UTC=state["first"]["canonical_UTC_ns"] if state["first"] else None,
        last_valid_poll_UTC=state["last"]["canonical_UTC_ns"] if state["last"] else None,
        unique_UTC_poll_timestamps=len(state["unique_times"]), unique_UTC_poll_dates=len(state["unique_dates"]),
        source_rows_by_UTC_year={str(y): n for y, n in sorted(state["by_year"].items())},
        unique_UTC_poll_timestamps_by_year={str(y): sum(date.fromordinal(k[0]).year == y for k in state["unique_times"]) for y in sorted(state["by_year"])},
        unique_UTC_poll_dates_by_year={str(y): sum(day.startswith(f"{y:04d}-") for day in state["unique_dates"]) for y in sorted(state["by_year"])})


def inventory_metadata(numbered_rows, emit_target, emit_nonmonotone):
    """Only eight permitted metadata strings; never receive financial fields."""
    all_coverage = coverage_state(); identities = {}; target_coverage = {label: coverage_state() for label in TARGETS}
    raw_duplicates, canonical_duplicates = defaultdict(list), defaultdict(list)
    invalid_time, invalid_identity = [], []
    precision = Counter(); previous_global = None; previous_bucket = {}
    global_nonmonotone = bucket_nonmonotone = 0
    for record_id, metadata in numbered_rows:
        source_id = f"{SOURCE_REPOSITORY}@{SOURCE_COMMIT}:{SOURCE_PATH}:CSVrecord{record_id}"
        if set(metadata) != set(METADATA_FIELDS) or any(not isinstance(metadata[name], str) for name in METADATA_FIELDS):
            raise ValueError("Only the eight exact metadata CSV strings may enter inventory.")
        raw_identity = tuple(metadata[name] for name in IDENTITY_FIELDS)
        normalized = {name: metadata[name].strip(ASCII_SPACE) for name in METADATA_FIELDS if name != "Time"}
        empty = [name for name, value in normalized.items() if value == ""]
        if empty: invalid_identity.append(dict(source_id=source_id, empty_normalized_metadata_fields=empty, raw_metadata=metadata))
        item = identities.setdefault(raw_identity, coverage_state())
        try: timestamp = timestamp_metadata(metadata["Time"])
        except (ValueError, TypeError, OverflowError) as error:
            timestamp = None
            invalid_time.append(dict(source_id=source_id, raw_Time=metadata["Time"], issue=str(error)))
        update_coverage(item, timestamp); update_coverage(all_coverage, timestamp)
        bucket = tuple(metadata[name] for name in BUCKET_FIELDS)
        raw_duplicates[(metadata["Time"], *bucket)].append(source_id)
        if timestamp is not None:
            precision[timestamp["fractional_precision_digits"]] += 1
            key = tuple(timestamp["clock_key"])
            canonical_duplicates[(timestamp["canonical_UTC_ns"], *bucket)].append(source_id)
            current = dict(source_id=source_id, raw_Time=metadata["Time"], canonical_UTC_ns=timestamp["canonical_UTC_ns"], clock_key=key)
            if previous_global is not None and key < tuple(previous_global["clock_key"]):
                global_nonmonotone += 1
                emit_nonmonotone(dict(scope="global_original_sequence", source_id=source_id,
                    previous_source_id=previous_global["source_id"], raw_Time=metadata["Time"], previous_raw_Time=previous_global["raw_Time"]))
            previous = previous_bucket.get(bucket)
            if previous is not None and key < tuple(previous["clock_key"]):
                bucket_nonmonotone += 1
                emit_nonmonotone(dict(scope="same_raw_contract_bucket", source_id=source_id, bucket=list(bucket),
                    previous_source_id=previous["source_id"], raw_Time=metadata["Time"], previous_raw_Time=previous["raw_Time"]))
            previous_global = current; previous_bucket[bucket] = current
        target = normalized["Product Code"]
        if target in TARGETS:
            update_coverage(target_coverage[target], timestamp)
            emit_target(dict(source_row_id=record_id, source_id=source_id, target_label=target,
                raw_metadata=metadata, normalized_labels=normalized, timestamp=timestamp,
                timestamp_is_collector_poll_not_primary_release_or_effective=True))
    identity_records = []
    for labels, state in sorted(identities.items()):
        identity_records.append(dict(raw_identity=dict(zip(IDENTITY_FIELDS, labels)),
            normalized_identity={name: value.strip(ASCII_SPACE) for name, value in zip(IDENTITY_FIELDS, labels)},
            coverage=finalized_coverage(state)))
    targets = {}
    for target in TARGETS:
        raw_records = [record for record in identity_records if record["raw_identity"]["Product Code"].strip(ASCII_SPACE) == target]
        targets[target] = dict(observed=bool(target_coverage[target]["rows"]), coverage=finalized_coverage(target_coverage[target]),
            raw_identity_records=raw_records,
            missing_2018_26_UTC_years=[year for year in range(2018, 2027) if target_coverage[target]["by_year"][year] == 0])
    duplicate_raw = [dict(raw_Time=key[0], bucket=dict(zip(BUCKET_FIELDS, key[1:])), source_ids=ids,
        duplicated_metadata_only=True, maintenance_equivalence_or_conflict_unknown=True) for key, ids in sorted(raw_duplicates.items()) if len(ids) > 1]
    duplicate_canonical = [dict(canonical_UTC_ns=key[0], bucket=dict(zip(BUCKET_FIELDS, key[1:])), source_ids=ids,
        canonical_time_equivalence_only=True, maintenance_equivalence_or_conflict_unknown=True)
        for key, ids in sorted(canonical_duplicates.items()) if len(ids) > 1]
    return dict(status=FINAL_STATUS, all_products_coverage=finalized_coverage(all_coverage), identity_records=identity_records,
        targets=targets, raw_metadata_duplicate_groups=duplicate_raw, canonical_time_metadata_duplicate_groups=duplicate_canonical,
        invalid_timestamp_rows=invalid_time, invalid_identity_rows=invalid_identity,
        fractional_precision_source_rows={str(k): v for k, v in sorted(precision.items())},
        global_original_sequence_nonmonotone_rows=global_nonmonotone,
        same_raw_contract_bucket_nonmonotone_rows=bucket_nonmonotone,
        financial_fields_accessed_or_converted=False, margin_levels_or_changes_or_increases_counted=False,
        daily_margin_state_or_price_or_signal_or_return_calculated=False,
        collector_poll_is_not_primary_clock=True, original_CME_product_mapping_admitted=False)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(request.full_url, code, "Redirect forbidden for single pinned source", headers, fp)


def verify_download(path, expected_bytes=SOURCE_BYTES, expected_git_blob=SOURCE_GIT_BLOB):
    path = Path(path)
    audit = dict(path=str(path.relative_to(OUT)), bytes=path.stat().st_size, sha256=sha(path), git_blob_sha1=git_blob_sha(path),
        expected_bytes=expected_bytes, expected_git_blob_sha1=expected_git_blob,
        archive_is_opaque_before_this_binding=True)
    audit["passed"] = audit["bytes"] == expected_bytes and audit["git_blob_sha1"] == expected_git_blob
    return audit


def download_once(opener=None):
    cache = OUT / "cache"; cache.mkdir(parents=True, exist_ok=True)
    path = cache / "cme_margin.partial"
    # The partial name remains unchanged even after success. An interrupted
    # attempt is retained and can never silently resume or overwrite it.
    with path.open("xb") as handle:
        if opener is None: opener = urllib.request.build_opener(NoRedirect()).open
        request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "Codex-metadata-intake/1.0", "Accept-Encoding": "identity"})
        with opener(request, timeout=DOWNLOAD_TIMEOUT) as response:
            if response.geturl() != SOURCE_URL: raise ValueError("Response URL differs from the one pinned archive.")
            while True:
                block = response.read(1024 * 1024)
                if not block: break
                handle.write(block)
                if handle.tell() > SOURCE_BYTES: raise ValueError("Archive exceeds pinned byte count; retained partial, no retry.")
    return path


def git_bytes(ref, name):
    return subprocess.check_output(["git", "show", f"{ref}:{name}"], cwd=ROOT)


def verify_registration(prereg):
    if subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() != "codex/work":
        raise ValueError("I04 must remain on codex/work.")
    subprocess.check_call(["git", "merge-base", "--is-ancestor", prereg, "HEAD"], cwd=ROOT)
    for directory in (ROOT / "analysis/outputs").glob("codex_hunt_v2_cme_margin_metadata*"):
        if (directory / "intake_attempt.json").exists() or (directory / "intake_verified_execution.json").exists() or (directory / "cache/cme_margin.partial").exists():
            raise ValueError("Retained I04 complete/partial attempt exists; no unchanged retry or alternate directory.")
    hashes = {}
    for name in (SCRIPT, PLAN, EVIDENCE, NOTE, IGNORE, "agents/codex/RESEARCH_CONTROLS.md"):
        raw = (ROOT / name).read_bytes()
        if git_bytes("HEAD", name) != raw or git_bytes(prereg, name) != raw:
            raise ValueError("Commit exact I04 code/plan/evidence/source/dependencies before acquisition:" + name)
        hashes[name] = hashlib.sha256(raw).hexdigest()
    return dict(prereg=prereg, implementation_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        bound_files_sha256=hashes, versions=dict(python=sys.version.split()[0]), dependencies="Python standard library only",
        source=dict(repository=SOURCE_REPOSITORY, commit=SOURCE_COMMIT, path=SOURCE_PATH, URL=SOURCE_URL,
            expected_bytes=SOURCE_BYTES, expected_git_blob_sha1=SOURCE_GIT_BLOB),
        timeout_seconds=DOWNLOAD_TIMEOUT, retry_count=0, redirects_permitted=False,
        required_header_subset=list(REQUIRED_HEADERS), interpreted_metadata_fields=list(METADATA_FIELDS), fixed_targets=list(TARGETS),
        all_other_financial_fields_opaque=True, collector_MIT_software_license_is_not_CME_data_redistribution_permission=True)


@contextmanager
def intake_lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "intake.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB); yield


def intake(prereg):
    with intake_lock():
        binding = verify_registration(prereg); started = utcnow(); stage = "single_archive_download"
        dump_once(OUT / "intake_attempt.json", dict(started_utc=started, prereg=prereg,
            implementation_commit=binding["implementation_commit"], script_sha256=sha(ROOT / SCRIPT)))
        dump_once(OUT / "intake_pre_acquisition_binding.json", binding)
        archive = None; archive_audit = None
        try:
            archive = download_once()
            stage = "opaque_archive_byte_verification_before_header"
            archive_audit = verify_download(archive)
            dump_once(OUT / "intake_download_binding.json", archive_audit)
            if not archive_audit["passed"]: raise ValueError("Pinned archive size/Git-blob validation failed before header or CSV interpretation.")
            stage = "header_only_after_byte_verification"
            with archive.open("rb") as handle: raw_header = handle.readline()
            header = next(csv.reader(io.StringIO(raw_header.decode("utf-8-sig"), newline=""), strict=True))
            positions = schema_positions(header)
            dump_once(OUT / "intake_header_binding.json", dict(header=header, header_line_sha256=hashlib.sha256(raw_header).hexdigest(),
                header_hash_includes_line_ending=True, exact_metadata_positions=positions, financial_field_positions_not_accessed=True))
            stage = "timestamp_and_identity_metadata_only"
            with text_output(OUT / "intake_target_metadata_rows.jsonl.gz") as targets:
                with text_output(OUT / "intake_nonmonotone_metadata_rows.jsonl.gz") as nonmonotone:
                    result = inventory_metadata(metadata_source_rows(archive, header),
                        lambda value: targets.write(json.dumps(value, allow_nan=False) + "\n"),
                        lambda value: nonmonotone.write(json.dumps(value, allow_nan=False) + "\n"))
            for filename, value in (("intake_product_identity_inventory.json.gz", result["identity_records"]),
                ("intake_raw_metadata_duplicates.json.gz", result["raw_metadata_duplicate_groups"]),
                ("intake_canonical_metadata_duplicates.json.gz", result["canonical_time_metadata_duplicate_groups"]),
                ("intake_invalid_metadata_rows.json.gz", dict(timestamp_rows=result["invalid_timestamp_rows"], identity_rows=result["invalid_identity_rows"]))):
                with text_output(OUT / filename) as handle: json.dump(value, handle, allow_nan=False); handle.write("\n")
            summary = {key: value for key, value in result.items() if key not in ("identity_records", "raw_metadata_duplicate_groups", "canonical_time_metadata_duplicate_groups", "invalid_timestamp_rows", "invalid_identity_rows")}
            summary.update(product_identity_combinations=len(result["identity_records"]),
                raw_duplicate_metadata_groups=len(result["raw_metadata_duplicate_groups"]), canonical_duplicate_metadata_groups=len(result["canonical_time_metadata_duplicate_groups"]),
                invalid_timestamp_rows=len(result["invalid_timestamp_rows"]), invalid_identity_rows=len(result["invalid_identity_rows"]))
        except Exception as error:
            summary = dict(status="SOURCE_ACCESS_HASH_SCHEMA_OR_IMPLEMENTATION_BLOCKED", failed_stage=stage,
                exception_type=type(error).__name__, exception_message=str(error),
                HTTP_status=error.code if isinstance(error, urllib.error.HTTPError) else None,
                no_automatic_retry=True, source_or_implementation_block_is_not_alpha_rejection=True)
            dump_once(OUT / "intake_exception.json", dict(summary, traceback=traceback.format_exc()))
        for name, expected in binding["bound_files_sha256"].items():
            if sha(ROOT / name) != expected: raise ValueError("Bound I04 code/plan/source changed; completion unverified:" + name)
        cached = OUT / "cache/cme_margin.partial"
        cache_state = dict(exists=cached.exists(), bytes=cached.stat().st_size if cached.exists() else None,
            sha256=sha(cached) if cached.exists() else None, raw_cache_ignored_and_not_redistributed=True)
        if archive_audit is not None and cached.exists() and cache_state["sha256"] != archive_audit["sha256"]:
            raise ValueError("Archive changed after byte verification; no verified metadata result.")
        summary.update(hypotheses_added=0, gross_screens_added=0, economic_evaluations_added=0,
            primary_clock_or_effective_history_admitted=False, price_signal_return_or_account_calculated=False,
            margin_values_levels_changes_or_increases_read=False, raw_archive_cache=cache_state,
            running_budget=dict(counted_evaluations=3, max_evaluations=60, hypotheses=4, max_hypotheses=10, retained_gross_screens=2, archived_t6_evaluations=65),
            limitations="Collector poll Time is not CME announcement/effective/receipt time; bucket labels are not effective dates; MIT code license is not CME data redistribution permission; missing rows/years are not filled.")
        dump_once(OUT / "intake_summary.json", summary)
        names = sorted(path.name for path in OUT.iterdir() if path.is_file() and not path.name.startswith("synthetic_")
            and path.name not in (".gitignore", "intake.lock", "intake_verified_execution.json"))
        marker = dict(started_utc=started, completed_utc=utcnow(), phase="timestamp_identity_metadata_only",
            status=summary["status"], last_stage=stage, prereg=prereg, implementation_commit=binding["implementation_commit"],
            script_sha256=sha(ROOT / SCRIPT), artifacts_sha256={name: sha(OUT / name) for name in names}, archive_cache=cache_state,
            financial_experiment_run=False, hypotheses_added=0, gross_screens_added=0, economic_evaluations_added=0,
            maintenance_or_other_financial_cells_accessed=False, primary_clock_or_history_admitted=False, retry_authorized=False)
        dump_once(OUT / "intake_verified_execution.json", marker)
        return summary


def fixtures():
    global OUT
    checks = []
    one = timestamp_metadata("2020-01-02T03:04:05.1Z")
    nine = timestamp_metadata("2020-01-02 03:04:05.100000000+00:00")
    assert one["clock_key"] == nine["clock_key"] and one["fractional_precision_digits"] == 1 and nine["fractional_precision_digits"] == 9
    assert timestamp_metadata("2020-01-02T03:04:05.000000001Z")["clock_key"] < timestamp_metadata("2020-01-02T03:04:05.000000010Z")["clock_key"]
    assert timestamp_metadata("2019-12-31T23:59:59.999999999Z")["clock_key"] < timestamp_metadata("2020-01-01T00:00:00Z")["clock_key"]
    assert timestamp_metadata("0001-01-01T00:00:00Z")["UTC_date"] == "0001-01-01"
    checks.append("exactUTC0-9fractionprecision/normaldate;nanosecondordering/nofloatormicrosecondtruncation")
    for raw in ("2020-01-01T00:00:00", "2020-01-01T00:00:00+01:00", "2020-01-01T00:00:00-00:00", "2020-01-01T00:00:00z",
        "2020-01-01T00:00:00.Z", "2020-01-01T00:00:00.1234567890Z", "2019-02-29T00:00:00Z", "2020-02-30T00:00:00Z",
        "2020-01-01T24:00:00Z", "2020-01-01T00:60:00Z", "2020-01-01T00:00:60Z", "0000-01-01T00:00:00Z",
        " 2020-01-01T00:00:00Z", "2020-01-01T00:00:00Z ", "２０２０-01-01T00:00:00Z"):
        try: timestamp_metadata(raw)
        except (ValueError, TypeError): pass
        else: raise AssertionError("Invalid/naive/ambiguous timestamp admitted.")
    checks.append("naive/nonUTC/invaliddate/offset/precision/Unicode/outerwhitespaceclockrejected")
    header = list(REQUIRED_HEADERS)
    positions = schema_positions(header)
    for bad in (header[:-1], header + ["Time"], [name.replace("Maintenance", "maintenance") for name in header]):
        try: schema_positions(bad)
        except ValueError: pass
        else: raise AssertionError("Ambiguous/renamed schema admitted.")
    class PoisonFinancialRow:
        def __getitem__(self, index):
            if header[index] not in METADATA_FIELDS: raise AssertionError("Financial field accessed.")
            return "2020-01-01T00:00:00Z" if header[index] == "Time" else "00123" if header[index] == "Product Code" else "metadata"
    selected = selected_metadata(PoisonFinancialRow(), positions)
    assert selected["Product Code"] == "00123" and set(selected) == set(METADATA_FIELDS)
    checks.append("exactrequiredheaderwithopaqueMaintenance/financialpoisoncellsneveraccessed;leadingzerosretained")
    def row(clock, code="NQ", **changes):
        value = {name: "metadata" for name in METADATA_FIELDS}
        value.update(Time=clock, **{"Product Code": code, "Product Name": "same raw product name", "Start Period": "001", "End Period": "099", "Currency": "USD"})
        value.update(changes); return value
    artificial = [(2, row("2020-01-01T01:00:00.123456789Z")),
        (3, row("2020-01-01T01:00:00.123456788Z")),
        (4, row("2020-01-01T01:00:00.123456789Z")),
        (5, row("2020-01-01 01:00:00.123456789+00:00")),
        (6, row("2020-01-01T01:00:00Z", code="00123")),
        (7, row("INVALID", code="NQ"))]
    emitted, nonmonotone = [], []
    result = inventory_metadata(artificial, emitted.append, nonmonotone.append)
    assert result["status"] == FINAL_STATUS and result["targets"]["NQ"]["coverage"]["source_rows"] == 5
    assert not result["targets"]["MNQ"]["observed"] and result["targets"]["NQ"]["coverage"]["unique_UTC_poll_timestamps"] == 2
    assert result["invalid_timestamp_rows"] and result["global_original_sequence_nonmonotone_rows"] == 2
    assert len(result["raw_metadata_duplicate_groups"]) == 1 and len(result["canonical_time_metadata_duplicate_groups"]) == 1
    assert len(result["canonical_time_metadata_duplicate_groups"][0]["source_ids"]) == 3
    assert len(emitted) == 5 and any(item["raw_identity"]["Product Code"] == "00123" for item in result["identity_records"])
    checks.append("allidentity/yearcoverage;absentfixedtargets;raw+canonicalduplicateALLIDs;nanosecondnonmonotoneflags")
    assert all("Maintenance" not in json.dumps(item) for item in emitted)
    checks.append("targetledgercontainsmetadataonly;nolevels/increasecounts/effective-dateinterpretation")
    original_out = OUT; original_out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="synthetic_download_", dir=original_out) as temporary:
        OUT = Path(temporary)
        try:
            calls = []
            def denied(request, timeout):
                calls.append((request.full_url, timeout)); raise urllib.error.HTTPError(request.full_url, 403, "synthetic denied", {}, None)
            try: download_once(opener=denied)
            except urllib.error.HTTPError: pass
            else: raise AssertionError("Synthetic403 incorrectly passed.")
            assert len(calls) == 1 and calls[0] == (SOURCE_URL, DOWNLOAD_TIMEOUT)
            assert (OUT / "cache/cme_margin.partial").exists()
            try: download_once(opener=denied)
            except FileExistsError: pass
            else: raise AssertionError("Retained partial overwritten/retried.")
            assert len(calls) == 1
            opaque = OUT / "synthetic_opaque.bin"; opaque.write_bytes(b"artificial-only\n")
            proof = verify_download(opaque, expected_bytes=opaque.stat().st_size, expected_git_blob=git_blob_sha(opaque))
            assert proof["passed"] and not verify_download(opaque, expected_bytes=1, expected_git_blob="0" * 40)["passed"]
            for name in ("gzip1.gz", "gzip2.gz"):
                with text_output(OUT / name) as handle: handle.write("artificial\n")
            assert sha(OUT / "gzip1.gz") == sha(OUT / "gzip2.gz")
        finally: OUT = original_out
    checks.append("singleURL403noretry;partialretained/overwriteforbidden;size+GitblobSHA1+SHA256beforeCSV")
    checks.append("deterministicgzipmtime0allmetadataretained;rawarchivecacheexcludedfromGit")
    return dict(passed=True, checks=checks, actual_archive_downloaded_or_CSV_rows_read=False,
        financial_cells_accessed_or_converted=False, economic_evaluations_added=0, hypotheses_added=0, gross_screens_added=0,
        script_sha256=sha(ROOT / SCRIPT), versions=dict(python=sys.version.split()[0]))


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--phase", required=True, choices=("fixtures", "intake")); parser.add_argument("--prereg")
    args = parser.parse_args()
    if args.phase == "fixtures":
        result = fixtures(); dump_once(OUT / f"synthetic_checks_{result['script_sha256'][:12]}.json", result)
    else:
        if not args.prereg: parser.error("Intake requires committed --prereg.")
        result = intake(args.prereg)
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__": main()
