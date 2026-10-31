"""I02: bounded CL Legacy sign-state source support, never an economic test.

Import and --phase fixtures read no owned source rows.  Real execution requires
the committed plan/code/evidence.  Every pinned ZIP/member is byte-verified,
then ALL-year identity metadata is admitted, BEFORE any selected2018--22
position count is converted.  As-of metadata is never a publication timestamp.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import contextmanager
import csv
from datetime import date, datetime, timedelta, timezone
import fcntl
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "analysis/codex_hunt_v2_cl_cot_state_intake.py"
PLAN = "agents/codex/plans/hunt_v2_cl_cot_state_intake.md"
EVIDENCE = "agents/codex/evidence/hunt_v2_owned_flow_nomination.md"
NOTE = "agents/codex/research/hunt_v2_owned_flow_nomination.md"
OUT = ROOT / "analysis/outputs/codex_hunt_v2_cl_cot_state_intake"
TARGET_CODE = "067651"
TARGET_NAME = "CRUDE OIL, LIGHT SWEET - NEW YORK MERCANTILE EXCHANGE"
HEADER_SHA256 = "e4605b0ce9a5dbe7e13b592cc07e53e83df25193a074256e9ac4c1e79d59e6ba"
WIDTH = 129
MIN_NEGATIVE_WEEKS = 20
YEARS = tuple(range(2017, 2023))
DESIGN_YEARS = tuple(range(2018, 2023))
SELECTED_HEADERS = {0: "Market and Exchange Names", 2: "As of Date in Form YYYY-MM-DD",
    3: "CFTC Contract Market Code", 7: "Open Interest (All)",
    8: "Noncommercial Positions-Long (All)", 9: "Noncommercial Positions-Short (All)"}
# Immutable compressed bytes were inspected before this intake, never positions.
SOURCES = (
    (2017, 1711091, "5e910b93b5af5e1c8f4006eaeee10109754ee5dd2c7f9d04520bd9770c8ece2b", 14109048, "dd333f32"),
    (2018, 1900546, "adaecbfadf54f117308cc8a135cd9ba827deac3eb1489a5febc642c403728527", 15365481, "00e5b4e8"),
    (2019, 1904592, "3f2707b5fcab1491329684c82cc03759ab66899839f533e09ff0a5dcf517b0c5", 15419216, "57125e9d"),
    (2020, 1838852, "8c83c820e5f6fd193a0923aa02cfe520d20dbe74bba571a576c92baf7a186317", 15038669, "de73f504"),
    (2021, 1882568, "423d20412ec3fb629500fcbfbaa7b6973c5868965000d13963e9b63700c90952", 15251600, "de161a75"),
    (2022, 1983765, "206364f467eb0013b0a5f8e9526426cc6fcfc5bad4e4f91b25e00311a0184cfa", 16277791, "bffae737"),
)
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
CODE_RE = re.compile(r"^[0-9]{6}$")
COUNT_RE = re.compile(r"^[0-9]+$")


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def file_sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json_once(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, allow_nan=False); handle.write("\n")


def write_csv_once(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def git_bytes(ref, name):
    return subprocess.check_output(["git", "show", f"{ref}:{name}"], cwd=ROOT)


def metadata_day(value):
    if not isinstance(value, str) or DATE_RE.fullmatch(value) is None:
        raise ValueError("As-of date must be exact ASCII YYYY-MM-DD.")
    return date.fromisoformat(value)


def count_value(value):
    # No alternate locale, punctuation repair, rounding, floats or missing-to-zero.
    if not isinstance(value, str):
        raise ValueError("A source count must remain a CSV string.")
    trimmed = value.strip(" \t\r\n")
    if COUNT_RE.fullmatch(trimmed) is None:
        raise ValueError("A position count must be nonnegative ASCII integer digits.")
    return int(trimmed)


def validate_header(header):
    if len(header) != WIDTH or any(header[k] != value for k, value in SELECTED_HEADERS.items()):
        raise ValueError("Header schema or selected exact fields differ from frozen registration.")


def source_path(year):
    if year not in YEARS:
        raise ValueError("No source outside the six pinned years is permitted.")
    path = ROOT / f"data/cot/deacot{year}.zip"
    if path.is_symlink() or not path.resolve().is_relative_to((ROOT / "data/cot").resolve()):
        raise ValueError("Source path escapes the frozen owned COT allowlist.")
    return path


def verify_source_bytes(source):
    year, zip_size, zip_sha, member_size, member_crc = source
    path = source_path(year)
    observed = dict(year=year, path=str(path.relative_to(ROOT)), ZIP_bytes=path.stat().st_size,
        ZIP_sha256=file_sha(path), expected_ZIP_bytes=zip_size, expected_ZIP_sha256=zip_sha,
        member="annual.txt", expected_member_bytes=member_size, expected_member_CRC32=member_crc)
    if observed["ZIP_bytes"] != zip_size or observed["ZIP_sha256"] != zip_sha:
        raise ValueError(f"Pinned ZIP bytes differ for{year}; no CSV interpretation.")
    with zipfile.ZipFile(path) as archive:
        if archive.namelist() != ["annual.txt"]:
            raise ValueError(f"Unexpected ZIP member scope for{year}.")
        info = archive.getinfo("annual.txt")
        if info.file_size != member_size or f"{info.CRC:08x}" != member_crc or info.flag_bits & 1:
            raise ValueError(f"Pinned member metadata differs for{year}.")
        digest, crc, total = hashlib.sha256(), 0, 0
        with archive.open("annual.txt") as handle:
            header_raw = handle.readline()
            digest.update(header_raw); crc = zlib.crc32(header_raw, crc); total += len(header_raw)
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block); crc = zlib.crc32(block, crc); total += len(block)
        observed.update(member_bytes=total, member_sha256=digest.hexdigest(), member_CRC32=f"{crc & 0xffffffff:08x}",
            header_line_sha256=sha_bytes(header_raw), header_hash_includes_line_ending=True,
            encoding="Latin-1 byte preserving; selected metadata/count grammar ASCII")
        if total != member_size or observed["member_CRC32"] != member_crc or sha_bytes(header_raw) != HEADER_SHA256:
            raise ValueError(f"Member hash/CRC/header validation failed for{year}.")
        header = next(csv.reader(io.StringIO(header_raw.decode("latin-1"), newline=""), strict=True))
        validate_header(header)
    return observed


@contextmanager
def source_rows(year):
    with zipfile.ZipFile(source_path(year)) as archive:
        with archive.open("annual.txt") as raw:
            with io.TextIOWrapper(raw, encoding="latin-1", newline="") as text:
                reader = csv.reader(text, strict=True)
                validate_header(next(reader))
                yield enumerate(reader, start=2)  # One-based CSV record ID including header.


def identity_rows(year, numbered_rows):
    """Metadata only: return selected source IDs, never parse a count field."""
    audit = dict(year=year, total_source_rows=0, target_rows=0, valid_target_metadata_rows=0,
        target_raw_name_code_pairs=[], first_target_asof=None, last_target_asof=None,
        out_of_file_year_target_rows=[], non_Tuesday_target_rows=[], issues=[],
        target_metadata=[], position_count_fields_converted=0)
    pairs, days = Counter(), []
    for row_id, row in numbered_rows:
        audit["total_source_rows"] += 1
        if len(row) != WIDTH:
            audit["issues"].append(dict(source_row_id=row_id, issue="row_width_not129")); continue
        raw_code, raw_name = row[3], row[0]
        code, name = raw_code.strip(" \t\r\n"), raw_name.strip()
        if code != TARGET_CODE and name != TARGET_NAME:
            continue  # No other-market date/count conversion or inspection.
        audit["target_rows"] += 1
        pairs[(raw_code, raw_name)] += 1
        if CODE_RE.fullmatch(code) is None or code != TARGET_CODE or name != TARGET_NAME:
            audit["issues"].append(dict(source_row_id=row_id, issue="declared_code_exact_name_mismatch",
                raw_code=raw_code, raw_name=raw_name)); continue
        try:
            asof = metadata_day(row[2])
        except (ValueError, TypeError):
            audit["issues"].append(dict(source_row_id=row_id, issue="invalid_target_asof", raw_asof=row[2])); continue
        item = dict(source_row_id=row_id, source_year=year, asof=asof.isoformat(), contract_code=code)
        if asof.year not in YEARS:
            audit["issues"].append(dict(**item, issue="asof_outside2017_22")); continue
        if asof.year != year:
            audit["out_of_file_year_target_rows"].append(item)
        if asof.weekday() != 1:
            audit["non_Tuesday_target_rows"].append(item)
        audit["valid_target_metadata_rows"] += 1
        audit["target_metadata"].append(item); days.append(asof)
    if audit["target_rows"] == 0:
        audit["issues"].append(dict(issue="declared_target_absent"))
    audit["target_raw_name_code_pairs"] = [dict(raw_code=code, raw_name=name, rows=n) for (code, name), n in sorted(pairs.items())]
    audit["first_target_asof"] = min(days).isoformat() if days else None
    audit["last_target_asof"] = max(days).isoformat() if days else None
    audit["passed"] = not audit["issues"] and audit["target_rows"] == audit["valid_target_metadata_rows"]
    return audit


def selected_counts(year, numbered_rows, identity):
    """Called only after ALL six identity audits pass;2017 is never called."""
    if year not in DESIGN_YEARS or identity["year"] != year or not identity["passed"]:
        raise ValueError("Numeric conversion requires admitted design-year metadata.")
    admitted = {item["source_row_id"]: item for item in identity["target_metadata"]}
    rows, faults = [], []
    for row_id, row in numbered_rows:
        if row_id not in admitted:
            continue
        item = admitted[row_id]
        if len(row) != WIDTH or row[3].strip(" \t\r\n") != TARGET_CODE or row[0].strip() != TARGET_NAME or row[2] != item["asof"]:
            raise ValueError("Metadata changed between admission and numeric pass.")
        # Cross-file dates are retained. No2017 or outside2018--22 count conversion.
        if int(item["asof"][:4]) not in DESIGN_YEARS:
            faults.append(dict(**item, issue="design_ZIP_contains_non_design_asof_count_not_converted")); continue
        try:
            oi, long, short = (count_value(row[k]) for k in (7, 8, 9))
            if oi <= 0 or long > oi or short > oi:
                raise ValueError("Selected positions must be bounded by positive OI.")
        except (ValueError, TypeError):
            faults.append(dict(**item, issue="invalid_selected_nonnegative_integer_count_or_OI_bound")); continue
        net = long - short
        rows.append(dict(**item, source_id=f"deacot{year}.zip:annual.txt:CSVrecord{row_id}",
            OI=oi, noncommercial_long=long, noncommercial_short=short,
            sign="negative" if net < 0 else "positive" if net > 0 else "zero"))
    if len(rows) + len(faults) != len(admitted):
        raise ValueError("A metadata-admitted source ID vanished before numeric parsing.")
    return rows, faults


def summarize_counts(rows, numeric_faults):
    by_key, duplicate_groups, conflicts = defaultdict(list), [], []
    for item in rows:
        by_key[(item["contract_code"], item["asof"])].append(item)
    unique = []
    for key, copies in sorted(by_key.items()):
        values = {(r["OI"], r["noncommercial_long"], r["noncommercial_short"]) for r in copies}
        if len(copies) > 1:
            duplicate_groups.append(dict(contract_code=key[0], asof=key[1], source_ids=[r["source_id"] for r in copies],
                selected_counts_identical=len(values) == 1, excess_rows=len(copies) - 1))
        if len(values) != 1:
            conflicts.append(dict(contract_code=key[0], asof=key[1], source_ids=[r["source_id"] for r in copies])); continue
        item = copies[0].copy(); item["source_ids"] = [r["source_id"] for r in copies]
        unique.append(item)
    week_signs = defaultdict(set)
    week_dates = defaultdict(list)
    for item in unique:
        day = metadata_day(item["asof"]); iso = day.isocalendar()
        key = (iso.year, iso.week)
        week_signs[key].add(item["sign"]); week_dates[key].append(item["asof"])
    multi = [dict(ISO_year=y, ISO_week=w, asof_dates=week_dates[(y, w)], signs=sorted(week_signs[(y, w)]))
        for y, w in sorted(week_dates) if len(week_dates[(y, w)]) > 1]
    conflicting_weeks = [item for item in multi if len(item["signs"]) > 1]
    negative_weeks = sorted(key for key, signs in week_signs.items() if signs == {"negative"})
    years = {}
    for year in DESIGN_YEARS:
        subset = [r for r in unique if metadata_day(r["asof"]).year == year]
        count = Counter(r["sign"] for r in subset)
        negative = {metadata_day(r["asof"]).isocalendar()[:2] for r in subset if r["sign"] == "negative"}
        years[str(year)] = dict(unique_reports=len(subset), negative=count["negative"], zero=count["zero"],
            positive=count["positive"], distinct_negative_ISO_weeks=len(negative))
    source_ok = not numeric_faults and not conflicts and not conflicting_weeks and all(years[str(y)]["unique_reports"] for y in DESIGN_YEARS)
    status = "NOT_TESTABLE_DATA" if not source_ok else "NEEDS_PUBLICATION_DATA" if len(negative_weeks) >= MIN_NEGATIVE_WEEKS else "STOP_NO_SUPPORT"
    result = dict(status=status, selected_numeric_stage_rows_attempted=len(rows) + len(numeric_faults),
        valid_selected_rows=len(rows), unresolved_numeric_rows=numeric_faults, unique_design_reports=len(unique),
        duplicate_selected_groups=duplicate_groups, conflicting_selected_keys=conflicts,
        multiple_reports_per_ISO_week=multi, conflicting_sign_ISO_weeks=conflicting_weeks,
        distinct_negative_asof_dates=sum(r["sign"] == "negative" for r in unique),
        distinct_negative_ISO_weeks=len(negative_weeks), negative_ISO_week_keys=[dict(ISO_year=y, ISO_week=w) for y, w in negative_weeks],
        minimum_distinct_negative_ISO_weeks=MIN_NEGATIVE_WEEKS, by_asof_year=years,
        first_design_asof=min((r["asof"] for r in unique), default=None), last_design_asof=max((r["asof"] for r in unique), default=None),
        source_count_integrity_pass=bool(source_ok), source_support_pass=bool(source_ok and len(negative_weeks) >= MIN_NEGATIVE_WEEKS),
        support_is_not_power_or_trade_count=True, publication_mapping_verified=False,
        asof_is_not_publication=True, trading_TEST_or_H04_authorized=False)
    return result, unique


def verify_registration(authorization_commit):
    if subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() != "codex/work":
        raise ValueError("Source intake must remain on codex/work.")
    subprocess.check_call(["git", "merge-base", "--is-ancestor", authorization_commit, "HEAD"], cwd=ROOT)
    for directory in (ROOT / "analysis/outputs").glob("codex_hunt_v2_cl_cot_state_intake*"):
        if (directory / "intake_verified_execution.json").exists() or (directory / "intake_attempt.json").exists():
            raise ValueError("Retained intake attempt/completion already exists; no repeat in another directory.")
    hashes = {}
    for name in (SCRIPT, PLAN, EVIDENCE, NOTE):
        raw = (ROOT / name).read_bytes()
        if git_bytes("HEAD", name) != raw or git_bytes(authorization_commit, name) != raw:
            raise ValueError("Commit and freeze code/plan/evidence/source note before any source rows:" + name)
        hashes[name] = sha_bytes(raw)
    return dict(authorization_commit=authorization_commit,
        implementation_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        bound_files_sha256=hashes, runtime=dict(python=sys.version.split()[0], implementation=sys.implementation.name,
            parser="Python standard-library csv strict, Latin-1 byte preserving", ZIP="Python standard-library zipfile/zlib"),
        source_allowlist=[dict(year=y, path=f"data/cot/deacot{y}.zip", ZIP_bytes=n, ZIP_sha256=s, member="annual.txt",
            member_bytes=m, member_CRC32=c) for y, n, s, m, c in SOURCES],
        selected_header_indices={str(k): v for k, v in SELECTED_HEADERS.items()}, exact_target_code=TARGET_CODE,
        exact_target_name=TARGET_NAME, header_line_sha256=HEADER_SHA256, minimum_negative_ISO_weeks=MIN_NEGATIVE_WEEKS,
        dependencies="Standard library only; no price/grid/metrics/account module imported.")


@contextmanager
def intake_lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "intake.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB); yield


def intake(authorization_commit):
    with intake_lock():
        binding = verify_registration(authorization_commit)
        started = utcnow()
        write_json_once(OUT / "intake_attempt.json", dict(started_utc=started, authorization_commit=authorization_commit,
            implementation_commit=binding["implementation_commit"], script_sha256=binding["bound_files_sha256"][SCRIPT],
            phase="nonreturn_CL_position_support_intake", rule="No repeat of retained complete or incomplete attempt."))
        # Byte stage for ALL sources before any CSV interpretation.
        sources = [verify_source_bytes(source) for source in SOURCES]
        for source in sources:
            binding["bound_files_sha256"][source["path"]] = source["ZIP_sha256"]
        write_json_once(OUT / "intake_pre_rows_binding.json", dict(**binding, source_byte_audits=sources,
            recorded_utc=utcnow(), numeric_fields_converted=False))
        # Identity metadata stage for ALL six years before numeric conversion.
        identities = []
        for year in YEARS:
            with source_rows(year) as rows:
                identities.append(identity_rows(year, rows))
        write_json_once(OUT / "intake_identity_audit.json", dict(sources=identities,
            all_year_identity_pass=all(item["passed"] for item in identities), position_count_fields_converted=0))
        selected, faults, unique = [], [], []
        if all(item["passed"] for item in identities):
            for identity in identities:
                year = identity["year"]
                if year == 2017:
                    continue
                with source_rows(year) as numbered:
                    rows, bad = selected_counts(year, numbered, identity)
                selected.extend(rows); faults.extend(bad)
            result, unique = summarize_counts(selected, faults)
        else:
            result = dict(status="NOT_TESTABLE_IDENTITY", source_count_integrity_pass=False,
                source_support_pass=False, selected_numeric_stage_rows_attempted=0,
                trading_TEST_or_H04_authorized=False, publication_mapping_verified=False)
        result.update(phase="nonreturn_CL_position_support_intake", fixed_predicate="Legacy_Noncommercial_Long_All_minus_Short_All<0",
            all_year_identity_pass=all(item["passed"] for item in identities), source_byte_audits=sources,
            numeric_conversion_years=list(DESIGN_YEARS), pre2018_or_2023plus_positions_converted=False,
            other_market_numeric_fields_converted=False, NQ_chart_TFF_release_mapping_inspected=False,
            prices_trades_returns_signals_metrics_accounts_calculated=False, point_in_time_admission=False,
            hypotheses_added=0, economic_evaluations_added=0, gross_screens_added=0,
            limitation="As-of support cannot establish original release/vintage/receipt, Sunday opportunities, economic edge or book improvement.")
        for name, digest in binding["bound_files_sha256"].items():
            if file_sha(ROOT / name) != digest:
                raise ValueError("Code/plan/evidence/source bytes changed during intake:" + name)
        fields = ("source_year", "source_row_id", "source_id", "asof", "contract_code", "OI", "noncommercial_long", "noncommercial_short", "sign")
        write_csv_once(OUT / "intake_selected_source_rows.csv", selected, fields)
        write_json_once(OUT / "intake_unique_selected_states.json", dict(rows=unique, duplicate_policy="One canonical selected key; retain ALL source IDs and identical counts; conflicts block support."))
        write_json_once(OUT / "intake_support_audit.json", result)
        artifact_names = ("intake_attempt.json", "intake_pre_rows_binding.json", "intake_identity_audit.json",
            "intake_selected_source_rows.csv", "intake_unique_selected_states.json", "intake_support_audit.json")
        marker = dict(started_utc=started, completed_utc=utcnow(), phase=result["phase"], status=result["status"],
            authorization_commit=authorization_commit, implementation_commit=binding["implementation_commit"],
            script_sha256=binding["bound_files_sha256"][SCRIPT],
            artifacts_sha256={name: file_sha(OUT / name) for name in artifact_names},
            financial_experiment_run=False, gross_screens_added=0, economic_evaluations_added=0, hypotheses_added=0,
            publication_mapping_verified=False, point_in_time_admission=False, authorizes_TEST_or_H04=False,
            downstream_requires_all_bound_hashes=True)
        write_json_once(OUT / "intake_verified_execution.json", marker)
        return dict(status=result["status"], all_year_identity_pass=result["all_year_identity_pass"],
            negative_ISO_weeks=result.get("distinct_negative_ISO_weeks"), source_support_pass=result["source_support_pass"],
            returns_calculated=False, gross_screens_added=0, economic_evaluations_added=0, hypotheses_added=0)


def synthetic_row(day, long="10", short="20", oi="100", code=TARGET_CODE, name=TARGET_NAME):
    row = ["POISON_UNUSED_FIELD"] * WIDTH
    row[0], row[2], row[3], row[7], row[8], row[9] = name, day, code, oi, long, short
    return row


def fixtures():
    checks = []
    header = ["IGNORED"] * WIDTH
    for k, value in SELECTED_HEADERS.items(): header[k] = value
    validate_header(header)
    for k in SELECTED_HEADERS:
        bad = header.copy(); bad[k] = "WRONG"
        try: validate_header(bad)
        except ValueError: pass
        else: raise AssertionError("Wrong selected header admitted.")
    checks.append("129-field exact selected header schema")
    for value in ("NaN", "1.0", "-1", "+1", "1,000", "", "１２", "1_000", "Infinity", None, True):
        try: count_value(value)
        except ValueError: pass
        else: raise AssertionError("Invalid count admitted.")
    assert count_value(" \t0012 ") == 12
    checks.append("strict nonnegative ASCII integer grammar; no float/commas/rounding/missing repair")
    for value in ("2018-02-30", "2018-1-02", "2018/01/02", "２０１８-01-02", "2018-01-02 "):
        try: metadata_day(value)
        except ValueError: pass
        else: raise AssertionError("Ambiguous/impossible metadata date admitted.")
    checks.append("strict real ASCII as-of dates, never release timestamps")
    poison17 = identity_rows(2017, [(2, synthetic_row("2017-01-03", long="POISON", short="POISON", oi="POISON"))])
    assert poison17["passed"] and poison17["position_count_fields_converted"] == 0
    try: selected_counts(2017, [], poison17)
    except ValueError: pass
    else: raise AssertionError("2017 numeric stage admitted.")
    checks.append("2017 metadata-only poison positions never converted")
    other = synthetic_row("POISON_DATE", long="POISON", short="POISON", oi="POISON", code="123456", name="OTHER")
    rows = [(2, other), (3, synthetic_row("2018-01-02"))]
    identity = identity_rows(2018, rows); converted, faults = selected_counts(2018, rows, identity)
    assert identity["passed"] and len(converted) == 1 and not faults and converted[0]["source_row_id"] == 3
    checks.append("other-market poisonous dates/counts never converted")
    for row in (synthetic_row("2018-01-02", code="067650"), synthetic_row("2018-01-02", name="OTHER"), synthetic_row("2023-01-03")):
        assert not identity_rows(2018, [(2, row)])["passed"]
    assert not identity_rows(2018, [(2, other)])["passed"]
    checks.append("declared code AND exact name required; absent/otheryear identity blocked before numeric stage")
    for oi, long, short in (("0", "0", "0"), ("100", "101", "1"), ("100", "1", "101"), ("100", "1.0", "2")):
        rows = [(2, synthetic_row("2018-01-02", oi=oi, long=long, short=short))]
        identity = identity_rows(2018, rows); converted, faults = selected_counts(2018, rows, identity)
        assert not converted and len(faults) == 1
    checks.append("positive OI and long/short bounds; unresolved integers block support")
    synthetic = []
    for year in DESIGN_YEARS:
        row = synthetic_row(f"{year}-01-02", long="20", short="10")
        identity = identity_rows(year, [(2, row)]); converted, faults = selected_counts(year, [(2, row)], identity)
        assert identity["passed"] and not faults
        synthetic.extend(converted)
    # Exactly19/20 distinct negative weeks plus an independent positive report/year.
    for i in range(20):
        day = date(2018, 2, 6) + timedelta(weeks=i)
        rows = [(100 + i, synthetic_row(day.isoformat()))]
        identity = identity_rows(2018, rows); converted, faults = selected_counts(2018, rows, identity)
        assert not faults
        synthetic.extend(converted)
    result19, _ = summarize_counts(synthetic[:-1], [])
    result20, _ = summarize_counts(synthetic, [])
    assert result19["status"] == "STOP_NO_SUPPORT" and result19["distinct_negative_ISO_weeks"] == 19
    assert result20["status"] == "NEEDS_PUBLICATION_DATA" and result20["distinct_negative_ISO_weeks"] == 20
    assert not result20["trading_TEST_or_H04_authorized"] and not result20["publication_mapping_verified"]
    checks.append("fixed19vs20 week boundary; support never grants publication/TEST/H04")
    copied = synthetic[-1].copy(); copied["source_id"] = "duplicate-source-id"; copied["source_row_id"] = 999
    duplicate, unique = summarize_counts(synthetic + [copied], [])
    assert duplicate["source_support_pass"] and len(unique) == len(synthetic) and len(duplicate["duplicate_selected_groups"]) == 1
    copied["noncommercial_long"] = 11
    conflict, _ = summarize_counts(synthetic + [copied], [])
    assert conflict["status"] == "NOT_TESTABLE_DATA" and conflict["conflicting_selected_keys"]
    checks.append("exact selected duplicates collapse once with all IDs; contradictory counts fatal")
    opposite = synthetic[-1].copy(); opposite["asof"] = (metadata_day(opposite["asof"]) + timedelta(days=1)).isoformat()
    opposite["sign"] = "positive"; opposite["source_id"] = "opposite-sign-source"
    conflictweek, _ = summarize_counts(synthetic + [opposite], [])
    assert conflictweek["status"] == "NOT_TESTABLE_DATA" and conflictweek["conflicting_sign_ISO_weeks"]
    checks.append("multiple as-of dates in a week retained; conflicting weekly signs block support")
    holiday = identity_rows(2018, [(2, synthetic_row("2018-12-24"))])
    assert holiday["passed"] and holiday["non_Tuesday_target_rows"]
    outyear = identity_rows(2018, [(2, synthetic_row("2017-12-26"))])
    assert outyear["passed"] and outyear["out_of_file_year_target_rows"]
    assert selected_counts(2018, [(2, synthetic_row("2017-12-26"))], outyear)[1]
    checks.append("holiday weekdays and in-range cross-file dates retained; nondesign positions never converted")
    assert [s[0] for s in SOURCES] == list(YEARS) and len({s[2] for s in SOURCES}) == 6
    for year in (2016, 2023, 2026):
        try: source_path(year)
        except ValueError: pass
        else: raise AssertionError("Source year outside allowlist admitted.")
    checks.append("exact six ZIP constants; no future source wildcard")
    return dict(passed=True, checks=checks, real_source_rows_read=False,
        prices_trades_returns_signals_metrics_accounts_calculated=False, economic_evaluations_added=0,
        hypotheses_added=0, gross_screens_added=0, script_sha256=file_sha(ROOT / SCRIPT),
        runtime=dict(python=sys.version.split()[0]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=("fixtures", "intake"))
    parser.add_argument("--authorization-commit")
    args = parser.parse_args()
    if args.phase == "fixtures":
        result = fixtures()
        write_json_once(OUT / f"synthetic_checks_{result['script_sha256'][:12]}.json", result)
    else:
        if not args.authorization_commit:
            parser.error("Intake requires committed --authorization-commit.")
        result = intake(args.authorization_commit)
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__":
    main()
