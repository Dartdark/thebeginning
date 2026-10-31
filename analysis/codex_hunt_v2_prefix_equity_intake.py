"""Owned JSON quality admission only; no returns/signals/trades are calculated.

Frozen schema: object['data'] contains rows of exactly eight fields ordered
Open,Low,High,Close,AbsChange,PctChange,GregorianDate,JalaliDate.  All JSON
numeric tokens remain strings.  Only OHLC on Gregorian dates2018--22 is
converted to Decimal for integrity checks.  Change/Jalali fields are ignored.
Importing this module reads no inputs.  Fixtures use artificial objects only.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import fcntl
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "analysis/codex_hunt_v2_prefix_equity_intake.py"
INPUT = ROOT / "agents/codex/inputs/hunt_v2_prefix_equity_intake"
OUT = ROOT / "analysis/outputs/codex_hunt_v2_prefix_equity_intake"
DESIGN_YEARS = tuple(range(2018, 2023))
FIELDS = ("Open", "Low", "High", "Close", "Abs_Change", "Pct_Change", "Gregorian_Date", "Jalali_Date")
MIN_UNIQUE_DESIGN_DATES = 240
DATE_RE = re.compile(r"^([0-9]{4})([-/])([0-9]{2})\2([0-9]{2})$")
PLAIN_PRICE_RE = re.compile(r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$")
COMMA_PRICE_RE = re.compile(r"^[0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]+)?$")
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
PROVENANCE_FIELDS = ("vendor", "index_identity", "close_clock_timezone", "adjustment_revision", "available_at_receipt")


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def file_sha(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_once(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")


def reject_constant(value: str):
    raise ValueError("Non-standard JSON numeric constant is not admitted.")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key is not admitted.")
        result[key] = value
    return result


def parse_json(raw: bytes):
    # Prevent the JSON decoder itself from converting pre/post-design prices.
    return json.loads(raw.decode("utf-8"), parse_int=str, parse_float=str,
                      parse_constant=reject_constant, object_pairs_hook=unique_object)


def gregorian(value) -> date:
    if not isinstance(value, str):
        raise ValueError("GregorianDate must be a string.")
    match = DATE_RE.fullmatch(value)
    if match is None:
        raise ValueError("GregorianDate must be exact YYYY-MM-DD or YYYY/MM/DD.")
    year, _, month, day = match.groups()
    return date(int(year), int(month), int(day))


def design_ohlc(row: list) -> tuple[tuple[Decimal, ...] | None, list[str], int]:
    """This function must be called only after2018--22 date admission."""
    converted = []
    normalized_fields = 0
    for value in row[:4]:
        # JSON booleans/null/objects must not masquerade as numeric prices.
        if not isinstance(value, str):
            return None, ["nonscalar_or_nonnumeric_OHLC"], normalized_fields
        if "," in value:
            if COMMA_PRICE_RE.fullmatch(value) is None:
                return None, ["invalid_English_thousands_grouping"], normalized_fields
            value = value.replace(",", "")
            normalized_fields += 1
        elif PLAIN_PRICE_RE.fullmatch(value) is None:
            return None, ["nonstandard_ASCII_numeric_OHLC"], normalized_fields
        try:
            number = Decimal(value)
        except (InvalidOperation, ValueError):
            return None, ["nonnumeric_OHLC"], normalized_fields
        if not number.is_finite() or number <= 0:
            return None, ["nonpositive_or_nonfinite_OHLC"], normalized_fields
        converted.append(number)
    op, low, high, close = converted
    issues = []
    if high < low:
        issues.append("high_below_low")
    if low > min(op, close):
        issues.append("low_above_open_or_close")
    if high < max(op, close):
        issues.append("high_below_open_or_close")
    return tuple(converted), issues, normalized_fields


def quality_audit(raw: bytes) -> dict:
    """Full-file date metadata plus design-only OHLC integrity, never returns."""
    result = dict(schema="data rows: " + ",".join(FIELDS), schema_pass=False,
        numerical_quality_pass=False, metadata_key_names=[], rows=0,
        coverage_by_year={}, design_coverage_by_year={str(y): 0 for y in DESIGN_YEARS},
        unique_design_dates_by_year={str(y): 0 for y in DESIGN_YEARS},
        first_date=None, last_date=None, invalid_schema_rows=[], invalid_date_rows=[],
        duplicate_date_rows=0, duplicate_date_ids=[], design_duplicate_conflict_date_ids=[],
        invalid_design_ohlc_rows=[], design_ohlc_converted_rows=0,
        design_English_thousands_normalized_fields=0,
        non_design_ohlc_converted_rows=0, changes_or_jalali_parsed=False,
        complete_trading_calendar_claimed=False, returns_signals_trades_metrics_calculated=False)
    try:
        wrapper = parse_json(raw)
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        result["schema_error"] = "invalid_UTF8_or_JSON_or_duplicate_object_key"
        return result
    if not isinstance(wrapper, dict) or not isinstance(wrapper.get("data"), list):
        result["schema_error"] = "expected_object_with_list_data"
        return result
    result["metadata_key_names"] = sorted(key for key in wrapper if key != "data")
    rows = wrapper["data"]
    result["rows"] = len(rows)
    dates = []
    date_counts = Counter()
    by_year = Counter()
    design_by_year = Counter()
    design_unique_by_year = {str(y): set() for y in DESIGN_YEARS}
    design_values = {}
    duplicate_conflicts = set()
    for row_id, row in enumerate(rows):
        if not isinstance(row, list) or len(row) != len(FIELDS):
            result["invalid_schema_rows"].append(row_id)
            continue
        try:
            day = gregorian(row[6])
        except (ValueError, TypeError, OverflowError):
            result["invalid_date_rows"].append(row_id)
            continue
        label = day.isoformat()
        dates.append(day)
        date_counts[label] += 1
        by_year[str(day.year)] += 1
        if day.year not in DESIGN_YEARS:
            continue  # No OHLC/change parsing, arithmetic or conflicts outside design.
        design_by_year[str(day.year)] += 1
        design_unique_by_year[str(day.year)].add(label)
        values, issues, normalized_fields = design_ohlc(row)
        result["design_English_thousands_normalized_fields"] += normalized_fields
        result["design_ohlc_converted_rows"] += 1
        if issues:
            result["invalid_design_ohlc_rows"].append(dict(row=row_id, date=label, violations=issues))
        if values is not None:
            if label in design_values and design_values[label] != values:
                duplicate_conflicts.add(label)
            else:
                design_values[label] = values
    result["coverage_by_year"] = dict(sorted(by_year.items()))
    result["design_coverage_by_year"] = {str(y): design_by_year[str(y)] for y in DESIGN_YEARS}
    result["unique_design_dates_by_year"] = {str(y): len(design_unique_by_year[str(y)]) for y in DESIGN_YEARS}
    result["first_date"] = min(dates).isoformat() if dates else None
    result["last_date"] = max(dates).isoformat() if dates else None
    result["duplicate_date_rows"] = sum(n - 1 for n in date_counts.values())
    result["duplicate_date_ids"] = sorted(day for day, n in date_counts.items() if n > 1)
    result["design_duplicate_conflict_date_ids"] = sorted(duplicate_conflicts)
    result["design_years_present"] = all(design_by_year[str(y)] > 0 for y in DESIGN_YEARS)
    result["coarse_unique_date_coverage_pass"] = all(len(design_unique_by_year[str(y)]) >= MIN_UNIQUE_DESIGN_DATES for y in DESIGN_YEARS)
    result["minimum_unique_design_dates_per_year"] = MIN_UNIQUE_DESIGN_DATES
    ascending = all(a <= b for a, b in zip(dates, dates[1:]))
    descending = all(a >= b for a, b in zip(dates, dates[1:]))
    result["date_ordering"] = "constant_or_single" if ascending and descending else "ascending" if ascending else "descending" if descending else "unsorted"
    result["schema_pass"] = bool(rows) and not result["invalid_schema_rows"] and not result["invalid_date_rows"]
    result["numerical_quality_pass"] = (result["schema_pass"] and result["coarse_unique_date_coverage_pass"]
        and not result["invalid_design_ohlc_rows"] and not duplicate_conflicts)
    result["duplicate_policy"] = "retain every source row; count all date duplicates; contradictory design OHLC blocks numerical quality; no dedup transformation"
    result["design_price_format_normalization"] = "strict ASCII plain decimal/exponent or unambiguous English groups of three thousands; remove commas only in2018-22 OHLC before Decimal"
    return result


def evidence_verified(entry) -> bool:
    return (isinstance(entry, dict) and entry.get("verified") is True
            and isinstance(entry.get("evidence"), str) and bool(entry["evidence"].strip()))


def provenance_audit(source: dict) -> dict:
    evidence = source.get("provenance", {})
    if not isinstance(evidence, dict):
        evidence = {}
    missing = [name for name in PROVENANCE_FIELDS if not evidence_verified(evidence.get(name))]
    return dict(required_field_names=list(PROVENANCE_FIELDS), verified_field_names=[name for name in PROVENANCE_FIELDS if name not in missing],
                unresolved_field_names=missing, provenance_pass=not missing,
                values_copied_into_audit=False, source_metadata_values_not_used_as_proof=True)


def owned_path(relative: str, root: Path) -> Path:
    if not isinstance(relative, str) or Path(relative).is_absolute():
        raise ValueError("Expected repository-relative owned path.")
    path = ROOT / relative
    if not path.resolve().is_relative_to(root.resolve()) or path.resolve() == root.resolve():
        raise ValueError("Path escapes owned intake directory.")
    return path


def committed_bytes(ref: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=ROOT)


def verify_manifest(prereg: str, manifest_name: str) -> tuple[dict, dict]:
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    if branch != "codex/work":
        raise ValueError("Input admission must run on codex/work.")
    for directory in (ROOT / "analysis/outputs").glob("codex_hunt_v2_prefix_equity_intake*"):
        if (directory / "intake_verified_execution.json").exists():
            raise ValueError("Completed intake already retained; do not repeat in a retry directory.")
    if committed_bytes("HEAD", SCRIPT) != (ROOT / SCRIPT).read_bytes():
        raise ValueError("Commit/freeze intake implementation in HEAD before reading inputs.")
    manifest_path = owned_path(manifest_name, INPUT)
    manifest_raw = manifest_path.read_bytes()
    if committed_bytes(prereg, manifest_name) != manifest_raw:
        raise ValueError("Manifest differs from its pre-data committed registration.")
    manifest = json.loads(manifest_raw, object_pairs_hook=unique_object)
    if not isinstance(manifest, dict) or not isinstance(manifest.get("inputs"), list) or len(manifest["inputs"]) != 2:
        raise ValueError("Frozen intake requires exactly two source entries.")
    if manifest.get("expected_schema") != dict(wrapper="data", row_width=8, columns=list(FIELDS)):
        raise ValueError("Manifest schema differs from frozen advertised eight-field schema.")
    if (manifest.get("design_price_conversion_years") != list(DESIGN_YEARS)
            or manifest.get("minimum_unique_design_dates_per_year") != MIN_UNIQUE_DESIGN_DATES
            or manifest.get("unverified_provenance_blocks_admission") is not True):
        raise ValueError("Manifest changes frozen year/coverage/provenance gates.")
    bindings = {SCRIPT: file_sha(ROOT / SCRIPT), manifest_name: sha256_bytes(manifest_raw)}
    prereg_paths = []
    for field in ("mechanism_path", "intake_plan_path"):
        name = manifest.get(field)
        path = owned_path(name, ROOT / "agents/codex")
        if committed_bytes(prereg, name) != path.read_bytes():
            raise ValueError("Mechanism/intake plan differs from pre-data committed registration.")
        bindings[name] = file_sha(path)
        prereg_paths.append(name)
    input_names = []
    for source in manifest["inputs"]:
        if not isinstance(source, dict) or not SHA1_RE.fullmatch(str(source.get("source_git_blob_sha", ""))):
            raise ValueError("Source requires explicit40-character lowercase Git blob SHA.")
        for field in ("name", "source_repository", "source_ref", "source_path"):
            if not isinstance(source.get(field), str) or not source[field].strip():
                raise ValueError("Missing source Git metadata field: " + field)
        if not isinstance(source.get("source_bytes"), int) or source["source_bytes"] <= 0:
            raise ValueError("Source metadata requires positive exact byte count.")
        path = owned_path(source.get("path"), INPUT)
        if path.name.lower().endswith(".json") is False or not path.is_file():
            raise ValueError("Expected bounded owned JSON input file.")
        input_names.append(source["path"])
    if len(set(input_names)) != 2 or manifest_name in input_names:
        raise ValueError("The two source files must be distinct from each other and manifest.")
    return manifest, dict(preregistration_commit=prereg,
        implementation_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        implementation_sha256=bindings[SCRIPT], manifest_path=manifest_name,
        mechanism_and_plan_paths=prereg_paths, source_bindings_sha256=bindings,
        runtime=dict(python=sys.version.split()[0], decimal="Python standard library", json="Python standard library"))


@contextmanager
def execution_lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "intake.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def audit(prereg: str, manifest_name: str) -> dict:
    with execution_lock():
        manifest, binding = verify_manifest(prereg, manifest_name)
        started = utcnow()
        with (OUT / "attempts.jsonl").open("a") as log:
            log.write(json.dumps(dict(started_utc=started, phase="owned_data_quality_intake",
                preregistration_commit=prereg, script_sha256=file_sha(ROOT / SCRIPT))) + "\n")
        sources = []
        for source_id, source in enumerate(manifest["inputs"]):
            path = owned_path(source["path"], INPUT)
            raw = path.read_bytes()
            observed_sha, observed_blob = sha256_bytes(raw), git_blob_sha(raw)
            provenance = provenance_audit(source)
            source_result = dict(source_id=source_id, name=source["name"], input_path=source["path"], byte_count=len(raw),
                file_sha256=observed_sha, expected_git_blob_sha=source["source_git_blob_sha"],
                observed_git_blob_sha=observed_blob, source_git_blob_matches=observed_blob == source["source_git_blob_sha"],
                expected_byte_count=source["source_bytes"], source_byte_count_matches=len(raw) == source["source_bytes"],
                source_git_repository=source["source_repository"], source_git_ref=source["source_ref"],
                source_git_path=source["source_path"], provenance=provenance)
            if source_result["source_git_blob_matches"] and source_result["source_byte_count_matches"]:
                source_result["quality"] = quality_audit(raw)
            else:
                source_result["quality"] = dict(numerical_quality_pass=False,
                    schema_pass=False, issue="Git blob/byte-count mismatch; no date/price audit performed")
            binding["source_bindings_sha256"][source["path"]] = observed_sha
            sources.append(source_result)
        numerical_pass = all(s["source_git_blob_matches"] and s["source_byte_count_matches"] and s["quality"]["numerical_quality_pass"] for s in sources)
        provenance_pass = all(s["provenance"]["provenance_pass"] for s in sources)
        result = dict(phase="owned_data_quality_intake", status="ADMITTED_FOR_PREREGISTERED_DESIGN_ONLY" if numerical_pass and provenance_pass else "NEEDS_DATA",
            numerical_quality_pass=numerical_pass, provenance_pass=provenance_pass,
            sources=sources, minimum_unique_design_dates_per_year=MIN_UNIQUE_DESIGN_DATES,
            design_years=list(DESIGN_YEARS), raw_JSON_numeric_tokens_converted_by_decoder=False,
            non_design_OHLC_converted=False, changes_or_Jalali_parsed=False,
            returns_signals_trades_metrics_correlations_calculated=False, economic_evaluations_added=0,
            hypotheses_added=0, no_remote_code_or_files_executed=True,
            limitation="Numerical quality is not source identity, correct event clock or point-in-time receipt proof; no complete calendar claim.")
        for name, expected in binding["source_bindings_sha256"].items():
            if file_sha(ROOT / name) != expected:
                raise ValueError("Bound code/plan/manifest/input changed during audit; no verified result.")
        write_once(OUT / "intake_source_binding.json", binding)
        write_once(OUT / "intake_quality_audit.json", result)
        marker = dict(started_utc=started, completed_utc=utcnow(), phase="owned_data_quality_intake",
            status=result["status"], preregistration_commit=prereg, implementation_commit=binding["implementation_commit"],
            script_sha256=file_sha(ROOT / SCRIPT),
            artifacts_sha256={name: file_sha(OUT / name) for name in ("intake_source_binding.json", "intake_quality_audit.json")},
            financial_experiment_run=False, economic_evaluations_added=0, hypotheses_added=0,
            downstream_requires_all_bound_hashes=True)
        write_once(OUT / "intake_verified_execution.json", marker)
        return dict(status=result["status"], numerical_quality_pass=numerical_pass,
            provenance_pass=provenance_pass, returns_calculated=False, economic_evaluations_added=0)


def synthetic_checks() -> dict:
    rows = [["100", "90", "110", "101", "IGNORE_ABS", "IGNORE_PCT", (date(year, 1, 1) + timedelta(days=i)).isoformat(), "IGNORE_JALALI"]
            for year in DESIGN_YEARS for i in range(MIN_UNIQUE_DESIGN_DATES)]
    # Unknown pre/post-design prices are deliberately poisonous and unconverted.
    rows += [["POISON_DO_NOT_CONVERT"] * 6 + ["2017/12/29", "IGNORE_JALALI"],
             ["POISON_DO_NOT_CONVERT"] * 6 + ["2023-01-03", "IGNORE_JALALI"]]
    raw = json.dumps(dict(name="DO_NOT_LOG_METADATA_VALUE", data=rows)).encode()
    result = quality_audit(raw)
    assert result["numerical_quality_pass"] and result["design_ohlc_converted_rows"] == 5 * MIN_UNIQUE_DESIGN_DATES
    assert result["non_design_ohlc_converted_rows"] == 0 and result["metadata_key_names"] == ["name"]
    assert "DO_NOT_LOG_METADATA_VALUE" not in json.dumps(result)
    assert len(result["coverage_by_year"]) == 7 and result["duplicate_date_rows"] == 0
    # Decoder retains numeric JSON literals as strings in every era.
    assert parse_json(b'{"data":[[1,0.5,2,1.5,"x","x","2024-01-02","x"]]}')["data"][0][:4] == ["1", "0.5", "2", "1.5"]
    for invalid in ("2018-02-30", "2019/02/29", "2018-02/01", "2018-2-01", "2018-02-01T00:00:00", "2018-02-01 ", "２０１８-02-01"):
        altered = [row.copy() for row in rows]
        altered[0][6] = invalid
        assert not quality_audit(json.dumps({"data": altered}).encode())["schema_pass"]
    assert gregorian("2020/02/29") == date(2020, 2, 29)
    assert not quality_audit(b'{"data":[],"data":[]}')["schema_pass"]
    assert not quality_audit(json.dumps({"data": [rows[0][:7]]}).encode())["schema_pass"]
    duplicated = [row.copy() for row in rows] + [rows[0].copy()]
    duplicate_result = quality_audit(json.dumps({"data": duplicated}).encode())
    assert duplicate_result["duplicate_date_rows"] == 1 and duplicate_result["numerical_quality_pass"]
    duplicated[-1][0] = "102"
    assert not quality_audit(json.dumps({"data": duplicated}).encode())["numerical_quality_pass"]
    for column, value in ((0, True), (0, None), (0, "NaN"), (0, "0"), (1, "105"), (2, "99")):
        altered = [row.copy() for row in rows]
        altered[0][column] = value
        assert not quality_audit(json.dumps({"data": altered}).encode())["numerical_quality_pass"]
    comma = [row.copy() for row in rows]
    comma[0][:4] = ["2,695.81", "2,600.00", "2,800.00", "2,700.00"]
    comma_result = quality_audit(json.dumps({"data": comma}).encode())
    assert comma_result["numerical_quality_pass"] and comma_result["design_English_thousands_normalized_fields"] == 4
    for malformed in ("12,34", "1,00,000", "2,695,81", " 2695.81", "2_695.81", "２６９５.81"):
        comma[0][0] = malformed
        assert not quality_audit(json.dumps({"data": comma}).encode())["numerical_quality_pass"]
    assert not quality_audit(json.dumps({"data": rows[1:]}).encode())["numerical_quality_pass"]
    assert not provenance_audit({})["provenance_pass"]
    verified = {name: dict(verified=True, evidence="synthetic evidence only") for name in PROVENANCE_FIELDS}
    assert provenance_audit({"provenance": verified})["provenance_pass"]
    verified["available_at_receipt"]["evidence"] = ""
    assert not provenance_audit({"provenance": verified})["provenance_pass"]
    assert git_blob_sha(b"test\n") == "9daeafb9864cf43055ae93beb0afd6c7d144bfa4"
    try:
        owned_path("agents/codex/inputs/hunt_v2_prefix_equity_intake/../../../../data/escape.json", INPUT)
    except ValueError:
        pass
    else:
        raise AssertionError("Owned path escape admitted.")
    return dict(passed=True, real_source_inputs_read=False, returns_signals_trades_metrics_calculated=False,
        checks=["strict data wrapper/eight fields", "metadata names only", "actual calendar/date format",
            "240 unique dates in each of five design years required", "design-only OHLC conversion; poison pre/post-design untouched",
            "JSON numeric tokens retained as strings", "OHLC integrity/nonfinite/bool/null rejection",
            "strict ASCII dates/numbers and advertised English thousands normalization; malformed groups rejected",
            "duplicate date counts and design OHLC conflicts retained", "provenance independent of numerical quality",
            "Git blob SHA separate from SHA256", "owned-path escape rejection"],
        runtime=dict(python=sys.version.split()[0]), script_sha256=file_sha(ROOT / SCRIPT))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=("fixtures", "audit"))
    parser.add_argument("--prereg")
    parser.add_argument("--manifest")
    args = parser.parse_args()
    if args.phase == "fixtures":
        result = synthetic_checks()
        write_once(OUT / f"synthetic_checks_{result['script_sha256'][:12]}.json", result)
    else:
        if not args.prereg or not args.manifest:
            parser.error("Audit requires committed --prereg and repository-relative --manifest.")
        result = audit(args.prereg, args.manifest)
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__":
    main()
