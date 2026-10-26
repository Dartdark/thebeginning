"""Standalone saved-entry clock-codec diagnostic; never a return experiment.

The original failed H03 maker/marker are immutable.  This diagnostic only adds
the canonical repository HHMM codec to a NEW entry-metadata comparison.  It
does not call the original maker, rebuild a grid, inspect MC exits/net, open
raw-window endpoints, or authorize further research on H03's fatal input gaps.

Source contract: grid24.jof maps integer HHMM to (HHMM//100)*60+HHMM%100;
portfolio.load_mc constructs that HHMM as entry.hour*100+entry.minute.  The
pinned parent PL source performs the same Time arithmetic.  A dedicated
mc_trades_v3.csv producer has not been located; that provenance limit remains.
The codec is fixed here, not chosen by comparing offsets or match rates.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "analysis/codex_hunt_v2_swing_mc_codec_diagnostic.py"
PLAN = "agents/codex/plans/hunt_v2_swing_mc_codec_diagnostic.md"
SOURCE_REF = "7f0800ffc04d56bd878750369a4abc2316ee01d8"
PRODUCER_SOURCE = "checks/candidates/fc_2b/mc_to_trades.py"
ORIGINAL_SCRIPT = "analysis/codex_hunt_v2_swing_opening_gross.py"
BASE = ROOT / "analysis/outputs/codex_hunt_v2_swing_opening"
OUT = BASE / "codec_diagnostic"
ORIGINAL_MARKER = BASE / "pre_gross_verified_execution.json"
PARENT = BASE / "parent_entries.csv"
CALENDAR = BASE / "gross_calendar_audit.csv"
ORIGINAL_BINDING = BASE / "gross_input_binding.json"
MC = ROOT / "agents/codex/inputs/rebound/plan_update_afde088/checks/candidates/swing_target/mc_trades_v3.csv"
YEARS = tuple(range(2018, 2023))
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
HHMM_RE = re.compile(r"^[0-9]{3,4}$")
SIDE_RE = re.compile(r"^-?1(?:\.0+)?$")
PRICE_TOLERANCE, MINUTE_TOLERANCE, PARITY_THRESHOLD = .25, 1., .90
sys.path.insert(0, str(ROOT / "analysis"))
from grid24 import jof  # Pure codec only; Grid24 constructor is never called.


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utcnow():
    return pd.Timestamp.now(tz="UTC").isoformat()


def write_json_once(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        json.dump(value, handle, indent=2, allow_nan=False); handle.write("\n")


def write_csv_once(path, frame):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle: frame.to_csv(handle, index=False, float_format="%.12g")


def committed(ref, path):
    return subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=ROOT)


def date_id(value):
    if not isinstance(value, str) or DATE_RE.fullmatch(value) is None:
        raise ValueError("Date must be exact ISO YYYY-MM-DD.")
    return pd.Timestamp(value).date().isoformat()


def hhmm_to_minute(value):
    if not isinstance(value, str) or HHMM_RE.fullmatch(value) is None:
        raise ValueError("Clock must be exactly3or4 ASCII integer HHMM digits.")
    number = int(value)
    hour, minute = number // 100, number % 100
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("Impossible HHMM hour/minute.")
    return int(jof(number))


def side_value(value):
    if not isinstance(value, str) or SIDE_RE.fullmatch(value) is None:
        raise ValueError("Side must be an integer-valued±1 encoding.")
    return int(value.split(".")[0])


def bool_value(value):
    if value not in ("True", "False", "true", "false"):
        raise ValueError("Ambiguous saved boolean metadata.")
    return value.lower() == "true"


def parent_from_strings(frame, comparison_dates):
    rows, faults = [], []
    for idx, record in frame.iterrows():
        try:
            day = date_id(record["date"])
            if int(day[:4]) not in YEARS:
                raise ValueError("Saved parent entry is outside original design years.")
            side = side_value(record["side"])
            entry = float(record["entry"])
            minute_raw = float(record["entry_j"])
            if not (np.isfinite(entry) and entry > 0 and np.isfinite(minute_raw) and minute_raw.is_integer() and 0 <= minute_raw < 1440):
                raise ValueError("Invalid saved parent entry metadata.")
        except (ValueError, TypeError, OverflowError):
            faults.append(dict(source_row_id=int(idx), issue="invalid_saved_parent_metadata")); continue
        if day not in comparison_dates:
            faults.append(dict(source_row_id=int(idx), date=day, issue="saved_parent_outside_original_comparison_universe"))
        rows.append(dict(source_row_id=int(idx), event_id=f"saved_parent_row_{idx}", date=day, side=side,
            entry=entry, entry_j=int(minute_raw)))
    parent = pd.DataFrame(rows, columns=("source_row_id", "event_id", "date", "side", "entry", "entry_j"))
    duplicates = parent.loc[parent.date.duplicated(keep=False), ["source_row_id", "event_id", "date"]].to_dict("records")
    return parent, dict(passed=not faults and not duplicates, invalid_rows=faults, duplicate_date_rows=duplicates)


def mc_from_strings(frame, comparison_dates):
    dates, invalid_dates = [], []
    for idx, value in frame.date.items():
        try: dates.append(date_id(value))
        except (ValueError, TypeError): dates.append(""); invalid_dates.append(int(idx))
    frame = frame.copy(); frame["date"] = dates
    design = frame.date.str[:4].isin(list(map(str, YEARS)))
    excluded = [dict(source_row_id=int(idx), date=day, reason="outside_original_preknown_calendar_or_parent_warmup")
        for idx, day in frame.loc[design & ~frame.date.isin(comparison_dates), "date"].items()]
    frame = frame[design & frame.date.isin(comparison_dates)].copy()
    duplicates = frame[frame.date.duplicated(keep=False)]
    rows, invalid = [], []
    for idx, record in frame.iterrows():
        try:
            side = side_value(record["side"])
            entry = float(record["entry"])
            if not np.isfinite(entry) or entry <= 0: raise ValueError("Invalid MCentry price.")
            minute = hhmm_to_minute(record["t_in"])
        except (ValueError, TypeError, OverflowError):
            invalid.append(dict(source_row_id=int(idx), date=record["date"], issue="invalid_entry_side_or_strict_HHMM")); continue
        rows.append(dict(source_row_id=int(idx), date=record["date"], side=side, entry=entry,
            original_t_in=record["t_in"], entry_j=minute))
    mc = pd.DataFrame(rows, columns=("source_row_id", "date", "side", "entry", "original_t_in", "entry_j"))
    audit = dict(passed=not invalid_dates and not invalid and duplicates.empty,
        fullfile_invalid_date_row_ids=invalid_dates, invalid_design_entry_rows=invalid,
        duplicate_design_entry_dates=sorted(duplicates.date.unique().tolist()),
        duplicate_design_entry_source_row_ids=[int(idx) for idx in duplicates.index],
        excluded_design_entry_date_rows=excluded, eligible_design_entry_rows_before_parse=len(frame))
    return mc, audit


def compare_entries(parent, mc, parent_audit, mc_audit):
    matched, used, count = [], set(), 0
    for p in parent.itertuples():
        possible = mc[(mc.date == p.date) & (mc.side == p.side)]
        hit = None
        for idx, m in possible.iterrows():
            if idx not in used and abs(m.entry - p.entry) <= PRICE_TOLERANCE + 1e-9 and abs(m.entry_j - p.entry_j) <= MINUTE_TOLERANCE + 1e-9:
                hit = idx; break
        if hit is not None: used.add(hit); count += 1
        matched.append(dict(parent_source_row_id=p.source_row_id, parent_event_id=p.event_id,
            date=p.date, side=p.side, parent_entry=p.entry, parent_entry_j=p.entry_j,
            matched_mc=hit is not None, mc_source_row_id=int(mc.loc[hit, "source_row_id"]) if hit is not None else None))
    mc = mc.copy(); mc["matched_parent"] = [idx in used for idx in mc.index]
    precision = count / len(parent) if len(parent) else None
    recall = count / len(mc) if len(mc) else None
    result = dict(parent_entries=len(parent), mc_entries=len(mc), matches=count,
        parent_to_mc_fraction=precision, mc_to_parent_fraction=recall, matching_threshold=PARITY_THRESHOLD,
        metadata_pass=parent_audit["passed"] and mc_audit["passed"],
        codec_entry_parity_pass=bool(parent_audit["passed"] and mc_audit["passed"] and precision is not None and recall is not None
            and precision >= PARITY_THRESHOLD and recall >= PARITY_THRESHOLD),
        price_tolerance=PRICE_TOLERANCE, minute_tolerance=MINUTE_TOLERANCE,
        clock_codec="strict3/4ASCIIHHMM;sharedgrid24.jof;zerooffset;noalternativeformatsearch",
        offsets_tested=[0], matching_rule_changed=False, parent_metadata_audit=parent_audit, mc_metadata_audit=mc_audit,
        original_run_reinterpreted_or_overwritten=False, raw_returns_calculated=False, gross_screen_runs=0,
        economic_evaluations=0, stopped_returns_calculated=False, mc_exit_or_net_interpreted=False,
        original_fatal_input_issues_resolved=False, authorizes_gross_or_stopped_or_book_bench=False,
        status="ENTRY_METADATA_DIAGNOSTIC_ONLY; H03 remains blocked by original reference/prefix issues")
    return result, pd.DataFrame(matched), mc


def verify(authorization_commit):
    if subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() != "codex/work":
        raise ValueError("Diagnostic must remain on codex/work.")
    if committed("HEAD", SCRIPT) != (ROOT / SCRIPT).read_bytes() or committed(authorization_commit, SCRIPT) != (ROOT / SCRIPT).read_bytes():
        raise ValueError("Commit the diagnostic code before interpreting saved metadata.")
    if committed(authorization_commit, PLAN) != (ROOT / PLAN).read_bytes():
        raise ValueError("Freeze the separate diagnostic scope before interpreting saved metadata.")
    if (OUT / "codec_verified_execution.json").exists(): raise ValueError("Saved codec diagnostic already completed; no repeats.")
    marker = json.loads(ORIGINAL_MARKER.read_text())
    if not (marker.get("phase") == "pre_gross" and marker.get("passed") is False and marker.get("raw_returns_calculated") is False and marker.get("gross_screen_runs") == 0):
        raise ValueError("Expected original immutable pre-gross failure without returns.")
    if marker["script_sha256"] != sha(ROOT / ORIGINAL_SCRIPT): raise ValueError("Original maker changed after failure.")
    for path in (PARENT, CALENDAR, ORIGINAL_BINDING):
        if marker["artifacts_sha256"].get(path.name) != sha(path): raise ValueError("Original selected artifact changed:" + path.name)
    source_binding = json.loads(ORIGINAL_BINDING.read_text())
    mc_name = str(MC.relative_to(ROOT))
    if source_binding["hashes"].get(mc_name) != sha(MC): raise ValueError("Original MC source changed.")
    dependencies = [SCRIPT, PLAN, ORIGINAL_SCRIPT, "analysis/grid24.py", "analysis/portfolio.py"]
    hashes = {name: sha(ROOT / name) for name in dependencies}
    for name in ("analysis/grid24.py",):
        if source_binding["hashes"].get(name) != hashes[name]: raise ValueError("Original shared codec dependency changed.")
    for path in (ORIGINAL_MARKER, PARENT, CALENDAR, ORIGINAL_BINDING, MC): hashes[str(path.relative_to(ROOT))] = sha(path)
    return dict(authorization_commit=authorization_commit, original_preregistration_commit=marker["prereg"],
        original_implementation_commit=marker["implementation_commit"], implementation_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        source_hashes=hashes, original_marker_sha256=sha(ORIGINAL_MARKER), original_artifacts_sha256=marker["artifacts_sha256"],
        versions=dict(python=sys.version.split()[0], numpy=np.__version__, pandas=pd.__version__),
        source_contract=[dict(path="analysis/grid24.py", function="jof", statement="(hhmm//100)*60+hhmm%100"),
            dict(path="analysis/portfolio.py", function="load_mc", statement="entry datetime hour*100+minute passed to sharedjof"),
            dict(git_ref=SOURCE_REF, path=PRODUCER_SOURCE, line=10, statement="genericMCproducer:t_in=entryDate.strftime('%H%M').astype(int)",
                 sha256=hashlib.sha256(committed(SOURCE_REF, PRODUCER_SOURCE)).hexdigest())],
        dedicated_mc_v3_CSV_producer_located=False, chart_timezone_receipt_verified=False,
        no_native_data_read=True, original_source_or_marker_mutated=False)


@contextmanager
def diagnostic_lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "codec.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB); yield


def diagnostic(authorization_commit):
    with diagnostic_lock():
        binding = verify(authorization_commit); started = utcnow()
        # Calendar metadata preserves the original reciprocal-match denominator.
        calendar = pd.read_csv(CALENDAR, usecols=["date", "comparison_eligible"], dtype=str, keep_default_na=False)
        calendar["date"] = calendar.date.map(date_id)
        allowed = calendar.comparison_eligible.map(bool_value)
        dates = set(calendar.loc[allowed, "date"])
        parent_raw = pd.read_csv(PARENT, usecols=["date", "side", "entry_j", "entry"], dtype=str, keep_default_na=False)
        parent, pa = parent_from_strings(parent_raw, dates)
        mc_raw = pd.read_csv(MC, usecols=["date", "side", "entry", "t_in"], dtype=str, keep_default_na=False)
        mc, ma = mc_from_strings(mc_raw, dates)
        result, matches, parsed_mc = compare_entries(parent, mc, pa, ma)
        for name, expected in binding["source_hashes"].items():
            if sha(ROOT / name) != expected: raise ValueError("Diagnostic-bound source changed:" + name)
        for name, frame in (("codec_parent_entries.csv", parent), ("codec_mc_entries_design_only.csv", parsed_mc), ("codec_matches.csv", matches)):
            write_csv_once(OUT / name, frame)
        write_json_once(OUT / "codec_binding.json", binding); write_json_once(OUT / "codec_audit.json", result)
        names = ["codec_parent_entries.csv", "codec_mc_entries_design_only.csv", "codec_matches.csv", "codec_binding.json", "codec_audit.json"]
        marker = dict(started_utc=started, completed_utc=utcnow(), phase="saved_entry_HHMM_codec_diagnostic",
            authorization_commit=authorization_commit, implementation_commit=binding["implementation_commit"],
            script_sha256=sha(ROOT / SCRIPT), original_marker_sha256=binding["original_marker_sha256"],
            artifacts_sha256={name: sha(OUT / name) for name in names}, raw_returns_calculated=False,
            gross_screen_runs=0, economic_evaluations=0, original_fatal_issues_resolved=False, authorizes_continuation=False)
        write_json_once(OUT / "codec_verified_execution.json", marker)
        return dict(status=result["status"], codec_entry_parity_pass=result["codec_entry_parity_pass"],
            parent_to_mc_fraction=result["parent_to_mc_fraction"], mc_to_parent_fraction=result["mc_to_parent_fraction"],
            raw_returns_calculated=False, original_fatal_issues_resolved=False)


def fixtures():
    assert hhmm_to_minute("848") == 8 * 60 + 48
    assert hhmm_to_minute("1145") == 11 * 60 + 45
    assert hhmm_to_minute("900") == 9 * 60
    assert hhmm_to_minute("0000") == 0 and hhmm_to_minute("2359") == 1439
    for bad in ("1260", "2400", "900.0", "09:00", " 900", "9", "90", "９００", "-900"):
        try: hhmm_to_minute(bad)
        except ValueError: pass
        else: raise AssertionError("Invalid HHMM clock admitted.")
    parent_raw = pd.DataFrame([dict(date="2018-01-02", side="1.0", entry_j="528", entry="100")])
    parent, pa = parent_from_strings(parent_raw, {"2018-01-02"})
    raw = pd.DataFrame([dict(date="2018-01-02", side="1", entry="100.25", t_in="848"),
        dict(date="2023-01-02", side="POISON", entry="POISON", t_in="POISON"),
        dict(date="2018-01-03", side="UNREAD", entry="UNREAD", t_in="UNREAD")])
    mc, ma = mc_from_strings(raw, {"2018-01-02"})
    result, matches, _ = compare_entries(parent, mc, pa, ma)
    assert result["codec_entry_parity_pass"] and not result["authorizes_gross_or_stopped_or_book_bench"]
    assert len(mc) == 1 and ma["excluded_design_entry_date_rows"][0]["source_row_id"] == 2
    duplicate = pd.concat([raw, raw.iloc[:1]], ignore_index=True)
    mc, ma = mc_from_strings(duplicate, {"2018-01-02"})
    assert not compare_entries(parent, mc, pa, ma)[0]["codec_entry_parity_pass"]
    raw.loc[0, "t_in"] = "850"  # Two minutes fails unchanged one-minute tolerance.
    mc, ma = mc_from_strings(raw, {"2018-01-02"})
    assert not compare_entries(parent, mc, pa, ma)[0]["codec_entry_parity_pass"]
    return dict(passed=True, real_saved_entries_or_MC_read=False, raw_returns_calculated=False,
        checks=["canonicalrepoHHMMthree/fourASCIIdigits", "actualhour/minutevalidation;nooffsetsearch",
            "savedparentmetadataonly", "datefilterbeforeMCnumericconversion/futurepoison",
            "unchangedprice/time/reciprocalparitythresholds", "duplicateMCentryfatal", "excludeddateIDsretained",
            "parityrepairdoesnotclearoriginalinputfaults"], script_sha256=sha(ROOT / SCRIPT))


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--phase", required=True, choices=("fixtures", "diagnostic")); parser.add_argument("--authorization-commit")
    args = parser.parse_args()
    if args.phase == "fixtures":
        result = fixtures(); write_json_once(OUT / f"synthetic_checks_{result['script_sha256'][:12]}.json", result)
    else:
        if not args.authorization_commit: parser.error("Diagnostic requires committed --authorization-commit.")
        result = diagnostic(args.authorization_commit)
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__": main()
