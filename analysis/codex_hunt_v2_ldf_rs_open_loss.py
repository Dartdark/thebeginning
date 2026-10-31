"""H07 frozen source-only admission; import never opens financial inputs.

SOURCE reads selected owned MC position metadata only.  There is deliberately
no feature, raw-return, stopped-design or account execution in this version.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import csv
from datetime import date, datetime, time, timezone
import fcntl
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_hunt_v2_ldf_rs_open_loss"
sys.dont_write_bytecode = True
os.environ["NUMBA_CACHE_DIR"] = str(OUT / "cache/numba")
sys.path.insert(0, str(ROOT / "analysis"))
import codex_hunt_v2_ldf_rs_metadata as META

SCRIPT = "analysis/codex_hunt_v2_ldf_rs_open_loss.py"
HELPER = "analysis/codex_hunt_v2_ldf_rs_metadata.py"
PLAN = "agents/codex/plans/hunt_v2_ldf_rs_open_loss.md"
EVIDENCE = "agents/codex/evidence/hunt_v2_ldf_rs_open_loss.md"
ADDENDUM = "agents/codex/research/hunt_v2_ldf_rs_predata_adjudication.md"
PREREG = "4c36121"
MC = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute Relative Strength.xlsx"
PARENT = ROOT / "analysis/outputs/codex_hunt_v2_ldf_delta"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def encoded(value):
    return (json.dumps(value, indent=2, allow_nan=False) + "\n").encode()


def once(name, value):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(encoded(value))


def committed_hash(path):
    """Validate opaque current bytes without parsing any financial values."""
    current = sha(ROOT / path)
    expected = hashlib.sha256(git("show", "HEAD:" + path)).hexdigest()
    if current != expected:
        raise ValueError("Uncommitted source/artifact differs:" + path)
    return current


def parent_binding():
    records, hashes = {}, {}
    for filename in ("gross_verified_execution.json", "design_verified_execution.json"):
        path = PARENT / filename
        relative = str(path.relative_to(ROOT))
        hashes[relative] = committed_hash(relative)
        marker = json.loads(path.read_text())
        if marker.get("phase") != ("gross" if filename.startswith("gross") else "design"):
            raise ValueError("Parent marker phase differs.")
        for name, expected in marker["artifacts_sha256"].items():
            if Path(name).name != name:
                raise ValueError("Parent marker contains unsafe artifact path.")
            rel = str((PARENT / name).relative_to(ROOT))
            actual = committed_hash(rel)
            if actual != expected:
                raise ValueError("Immutable parent artifact hash differs:" + rel)
            hashes[rel] = actual
        records[filename] = dict(sha256=hashes[relative], implementation_commit=marker["implementation_commit"],
            script_sha256=marker["script_sha256"], original_prereg=marker["prereg"])
    if not records:
        raise ValueError("No immutable parent binding.")
    return dict(markers=records, hashes=hashes, parent_maker_executed=False,
        parent_outcome_values_interpreted=False, parent_failed_filter_reopened=False)


def binding(prereg):
    if git("branch", "--show-current").decode().strip() != "codex/work":
        raise ValueError("H07 source admission must stay on codex/work.")
    actual_prereg = git("rev-parse", prereg).decode().strip()
    if actual_prereg != git("rev-parse", PREREG).decode().strip():
        raise ValueError("Use original H07 preregistration4c36121.")
    for path in (PLAN, EVIDENCE):
        if git("show", actual_prereg + ":" + path) != (ROOT / path).read_bytes():
            raise ValueError("Frozen H07 plan/evidence changed:" + path)
    code = {path: committed_hash(path) for path in (SCRIPT, HELPER, ADDENDUM)}
    for directory in (ROOT / "analysis/outputs").glob("codex_hunt_v2_ldf_rs_open_loss*"):
        if (directory / "source_attempt.json").exists() or (directory / "source_verified_execution.json").exists():
            raise ValueError("Existing H07 source attempt; no automatic/alternate-directory rerun.")
    if sha(ROOT / MC) != META.WORKBOOK_SHA256:
        raise ValueError("Owned RS workbook differs from source-only frozen inventory.")
    return dict(prereg=actual_prereg, implementation_commit=git("rev-parse", "HEAD").decode().strip(),
        code_sha256=code, plan_sha256=sha(ROOT / PLAN), evidence_sha256=sha(ROOT / EVIDENCE),
        workbook=dict(path=MC, bytes=(ROOT / MC).stat().st_size, sha256=META.WORKBOOK_SHA256),
        parent=parent_binding(), python=sys.version.split()[0],
        package_versions={name: importlib.metadata.version(name) for name in ("numpy", "pandas", "openpyxl")},
        runtime_cache=str(OUT / "cache"), phase="SOURCE_only", original_H01_H04_studies_unchanged=True)


def parent_decision_dates():
    """Only dates are interpreted; other parent fields never converted/used."""
    dates = []
    with (PARENT / "gross_events.csv").open(newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or "date" not in reader.fieldnames:
            raise ValueError("Immutable LDF parent lacks date header.")
        for row_number, row in enumerate(reader, start=2):
            day = date.fromisoformat(row["date"])
            if day.year not in META.DESIGN_YEARS:
                raise ValueError("Parent date is outside frozen design.")
            dates.append(dict(source_csv_record=row_number, date=day.isoformat(),
                decision_time_ct=datetime.combine(day, time(14, 0)).isoformat()))
    if not dates or len({item["date"] for item in dates}) != len(dates):
        raise ValueError("Parent dates are empty or not unique.")
    if [item["date"] for item in dates] != sorted(item["date"] for item in dates):
        raise ValueError("Immutable parent chronology differs.")
    return dates


def coverage_audit(settings, dates):
    if not settings or not settings.get("passed"):
        return dict(passed=False, reason="Settings source protocol failed; no coverage inference", checked=0)
    bad = [item for item in dates if not META.timestamp_within_coverage(settings, item["date"], 840)]
    return dict(passed=not bad, checked=len(dates), coverage_start_ct=settings["supported_start"],
        coverage_end_ct=settings["supported_end"], exact_rational_bounds=True, unsupported_parent_decisions=bad,
        absence_FLAT_only_under_declared_report_completeness_assumption=True,
        complete_external_history_or_live_position_parity_verified=False)


@contextmanager
def lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "source.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def source(prereg):
    with lock():
        bound = binding(prereg)
        started = now()
        once("source_attempt.json", dict(started_utc=started, **bound))
        audit = META.read_owned_rs(ROOT / MC)
        dates = parent_decision_dates()
        coverage = coverage_audit(audit.get("settings"), dates)
        passed = audit.get("global_pass") is True and coverage["passed"] is True
        gate = dict(phase="SOURCE_only", passed=passed,
            selected_event_metadata=len(audit.get("events", [])), structural_issues=len(audit.get("issues", [])),
            source_protocol_supported=audit.get("protocol_supported") is True,
            parent_decision_coverage=coverage, owned_stream=audit,
            feature_support_gate_run=False, native_marks_or_new_feature_masks_calculated=False,
            raw_or_stopped_returns_calculated=False, gross_screen_runs=0, economic_evaluations=0,
            next_action="Commit SOURCE PASS before only fixed feature/support phase; no outcomes authorized" if passed else
                "Close H07 at whole-source gate before features/outcomes; no alternate list/clock/parent rescue")
        once("source_parent_dates_only.json", dates)
        once("source_gate.json", gate)
        once("source_input_binding.json", bound)
        for path, expected in bound["code_sha256"].items():
            if sha(ROOT / path) != expected:
                raise ValueError("Bound implementation changed during SOURCE:" + path)
        if sha(ROOT / MC) != META.WORKBOOK_SHA256:
            raise ValueError("Bound workbook changed during SOURCE.")
        for path, expected in bound["parent"]["hashes"].items():
            if sha(ROOT / path) != expected:
                raise ValueError("Bound parent artifact changed during SOURCE:" + path)
        names = ("source_attempt.json", "source_parent_dates_only.json", "source_gate.json", "source_input_binding.json")
        marker = dict(started_utc=started, completed_utc=now(), phase="SOURCE_only", passed=passed,
            prereg=bound["prereg"], implementation_commit=bound["implementation_commit"],
            code_sha256=bound["code_sha256"], artifacts_sha256={name: sha(OUT / name) for name in names},
            actual_RS_selected_metadata_values_read=True,
            new_native_marks_or_features_or_returns_calculated=False,
            future_year_RS_Time_Price_Qty_or_exit_Price_PNL_interpreted=False,
            gross_screen_runs=0, economic_evaluations=0,
            source_PASS_is_not_feature_or_economic_admission=True)
        once("source_verified_execution.json", marker)
        return dict(marker=marker, selected_metadata_events=gate["selected_event_metadata"],
            source_issues=audit.get("issues", []), coverage=coverage)


def fixtures():
    checks = META.fixtures()
    dates = [dict(date="2020-01-02", decision_time_ct="2020-01-02T14:00:00")]
    def artificial_settings(start, end):
        a, b = META._setting_bound(start, False), META._setting_bound(end, False)
        return dict(passed=True, supported_start=a["timestamp"], supported_end=b["timestamp"],
            supported_start_exact=a, supported_end_exact=b)
    full = artificial_settings("2020-01-01T00:00:00", "2020-01-02T23:59:59.999999")
    assert coverage_audit(full, dates)["passed"]
    short = artificial_settings("2020-01-01T00:00:00", "2020-01-02T13:59:59")
    assert not coverage_audit(short, dates)["passed"]
    assert not coverage_audit(dict(passed=False), dates)["passed"]
    checks.update(source_wrapper_sha256=sha(ROOT / SCRIPT), coverage_bounds_tests=3,
        actual_RS_values_or_native_marks_or_returns_read=False)
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("fixtures", "source"), required=True)
    parser.add_argument("--prereg", default=PREREG)
    args = parser.parse_args()
    if args.phase == "fixtures":
        result = fixtures()
        OUT.mkdir(parents=True, exist_ok=True)
        filename = "source_synthetic_checks_" + sha(ROOT / SCRIPT)[:12] + "_" + sha(ROOT / HELPER)[:12] + ".json"
        if not (OUT / filename).exists():
            once(filename, result)
    else:
        result = source(args.prereg)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
