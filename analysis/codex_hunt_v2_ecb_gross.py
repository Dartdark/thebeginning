"""H06 calendar-first ECB preconference FOLLOW5 gross screen.

Import/fixtures never download/read owned prices. Calendar byte/date/clock
quality precedes a separately committed ROOT source-admission review, whose
exact marker SHA is required BEFORE any6E price bytes. No later bracket,
stopped,2023+, account or remote study maker is imported or called.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import date, datetime, time, timedelta
import fcntl
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import traceback
from urllib.parse import urlparse
import urllib.error
import urllib.request
import warnings
from zoneinfo import ZoneInfo, TZPATH

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_hunt_v2_ecb_preconference"
SCRIPT = "analysis/codex_hunt_v2_ecb_gross.py"
PLAN = "agents/codex/plans/hunt_v2_ecb_preconference.md"
SOURCE_NOTE = "agents/codex/research/hunt_v2_ecb_release_source.md"
ROOT_REVIEW = "agents/codex/research/hunt_v2_ecb_calendar_admission.json"
CALENDAR_URL = "https://raw.githubusercontent.com/chris-cheshire/project-midas-mk7/f9e756cbbca3a0576178412a48e1e374c9c76cfe/midas/data/calendar/ecb.txt"
CALENDAR_BYTES = 3650
CALENDAR_BLOB = "68cba6e08e80c47c7476277f07caeec320ef9995"
CALENDAR_CACHE = OUT / "cache/ecb_calendar.partial"
CALENDAR_MARKER = OUT / "calendar_verified_execution.json"
SOURCE_COMMIT = "f9e756cbbca3a0576178412a48e1e374c9c76cfe"
YEARS = tuple(range(2018, 2023))
FIELDS = ("open", "high", "low", "close", "volume")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CALENDAR_REQUIRED_ARTIFACTS = ("calendar_attempt.json", "calendar_pre_acquisition_binding.json", "calendar_byte_binding.json", "calendar_quality.json", "calendar_design_clocks.csv")
PRICE_TICK, NATIVE_POINT_VALUE, RT_UPPER_COST, GROSS_HURDLE = .00005, 12500., 4.99, 9.98
MIN_EVENTS, MIN_SIDE = 35, 5
sys.path.insert(0, str(ROOT / "analysis"))
from grid24 import Grid24, jof
from codex_s03_calendar import calendar_status
from replica import is_early_close
from codex_hunt_v2_ldf_delta import csv_once, dump_once, runtime_versions, sha, tstat, utcnow, valid_ohlcv, validate_metadata_keys


def committed(ref, name):
    return subprocess.check_output(["git", "show", f"{ref}:{name}"], cwd=ROOT)


def git_blob(path):
    path = Path(path)
    digest = hashlib.sha1(b"blob " + str(path.stat().st_size).encode("ascii") + b"\0")
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""): digest.update(block)
    return digest.hexdigest()


def event_clocks(day):
    if DATE_RE.fullmatch(day) is None: raise ValueError("Calendar date must be exact ISOdate.")
    d = date.fromisoformat(day)
    new_era = d >= date(2022, 7, 21)
    release = datetime.combine(d, time(14, 15) if new_era else time(13, 45), ZoneInfo("Europe/Berlin"))
    presser = datetime.combine(d, time(14, 45) if new_era else time(14, 30), ZoneInfo("Europe/Berlin"))
    r, p = release.astimezone(ZoneInfo("America/Chicago")), presser.astimezone(ZoneInfo("America/Chicago"))
    if r.date() != d or p.date() != d: raise ValueError("Unexpected native-date rollover; no clock repair.")
    R, P = r.hour * 60 + r.minute, p.hour * 60 + p.minute
    if not (R + 11 < P < 959): raise ValueError("Frozen preconference/native-flat interval impossible.")
    stamp = lambda j: datetime.combine(d, time(j // 60, j % 60), ZoneInfo("America/Chicago")).isoformat()
    return dict(date=day, year=d.year, era="NEW_20220721" if new_era else "OLD_1345_1430",
        release_Berlin=release.isoformat(), conference_Berlin=presser.isoformat(), release_CT=r.isoformat(), conference_CT=p.isoformat(),
        release_UTC=release.astimezone(ZoneInfo("UTC")).isoformat(), conference_UTC=presser.astimezone(ZoneInfo("UTC")).isoformat(),
        R=R, P=P, reaction_first_j=R + 1, reaction_last_j=R + 5,
        feature_event_time=stamp(R + 5), assumed_available_at=stamp(R + 10), decision_time=stamp(R + 10),
        entry_j=R + 11, first_fill_interval_start=stamp(R + 10), first_fill_interval_end=stamp(R + 11),
        exit_j=P, flat_open_wall_time=stamp(P - 1), publication_processing_assumption_minutes=5,
        historical_receipt_verified=False, offset_search_performed=False)


def timezone_provenance():
    files = {}
    for zone in ("Europe/Berlin", "America/Chicago", "UTC"):
        for directory in TZPATH:
            path = Path(directory) / zone
            if path.is_file():
                files[str(path)] = sha(path); break
    return dict(zoneinfo="Python standard library", system_zone_files_sha256=files,
        clock_table_is_bound_before_prices=True, actual_historical_receipt_not_established_by_timezone_rules=True)


def entry_calendar_disposition(day):
    status = calendar_status(day)
    if status["kind"] != "normal": return False, "SKIP_" + status["kind"].upper(), status["reason"]
    if pd.Timestamp(day).dayofweek >= 5: return False, "SKIP_WEEKEND", "weekend"
    if is_early_close(pd.Timestamp(day)): return False, "SKIP_EARLY", "shared early-close guard"
    return True, "ELIGIBLE_NORMAL_SESSION", "shared full normal session"


def calendar_parse(raw):
    text = raw.decode("utf-8-sig")
    comments, records, faults = [], [], []
    urls = set()
    for row_id, original in enumerate(text.splitlines(), start=1):
        line = original.strip(" \t\r\n")
        if not line: continue
        if line.startswith("#"):
            comments.append(dict(source_line_id=row_id, raw=original))
            for value in re.findall(r"https?://[^\s<>]+", line):
                cleaned = value.rstrip('.,;:)\'\"')
                if (urlparse(cleaned).hostname or "").lower() in ("ecb.europa.eu", "www.ecb.europa.eu"): urls.add(cleaned)
            continue
        try:
            if DATE_RE.fullmatch(line) is None: raise ValueError("Not one exact ISOdate per noncomment line.")
            parsed = date.fromisoformat(line)
        except ValueError as error:
            faults.append(dict(source_line_id=row_id, raw=original, issue=str(error))); continue
        records.append(dict(date=line, source_line_id=row_id, raw=original, year=parsed.year, weekday=parsed.weekday()))
    counts = Counter(record["date"] for record in records)
    duplicate_dates = [dict(date=day, source_line_ids=[r["source_line_id"] for r in records if r["date"] == day]) for day, n in sorted(counts.items()) if n > 1]
    nonmonotone = [dict(previous_date=a["date"], previous_source_line_id=a["source_line_id"],
        date=b["date"], source_line_id=b["source_line_id"]) for a, b in zip(records, records[1:]) if b["date"] <= a["date"]]
    design = [record for record in records if record["year"] in YEARS]
    by_year = {str(year): len({r["date"] for r in design if r["year"] == year}) for year in YEARS}
    weekdays = all(record["weekday"] < 5 for record in design)
    passed = not faults and not duplicate_dates and not nonmonotone and weekdays and all(n == 8 for n in by_year.values()) and bool(urls)
    clocks = []
    for record in design:
        eligible, disposition, reason = entry_calendar_disposition(record["date"])
        clocks.append(dict(**event_clocks(record["date"]), calendar_source_line_id=record["source_line_id"],
            eligible_calendar=eligible, calendar_disposition=disposition, calendar_disposition_reason=reason))
    return dict(passed=passed, source_comments=comments, official_ECB_URL_claims=sorted(urls),
        all_date_rows=records, invalid_lines=faults, duplicate_dates=duplicate_dates, nonmonotone_date_pairs=nonmonotone,
        design_dates=len(design), unique_design_dates=len({r["date"] for r in design}), design_unique_by_year=by_year,
        all_design_weekdays=weekdays, clocks=clocks, parser="ISOdate/line;blankand#commentignored;noaddition/offsetsearch",
        primary_2018_22_date_independent_corroboration=False, calendar_is_public_scheduled_date_claim=True,
        primary_historical_receipt_or_availability_admitted=False, prices_read=False)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(request.full_url, code, "Pinned-calendar redirects forbidden", headers, fp)


def acquire_calendar(opener=None):
    CALENDAR_CACHE.parent.mkdir(parents=True, exist_ok=True)
    with CALENDAR_CACHE.open("xb") as handle:
        if opener is None: opener = urllib.request.build_opener(NoRedirect()).open
        request = urllib.request.Request(CALENDAR_URL, headers={"User-Agent": "Codex-calendar-intake/1.0", "Accept-Encoding": "identity"})
        with opener(request, timeout=45) as response:
            if response.geturl() != CALENDAR_URL: raise ValueError("Single pinned source URL changed.")
            while True:
                block = response.read(4096)
                if not block: break
                handle.write(block)
                if handle.tell() > CALENDAR_BYTES: raise ValueError("Calendar exceeds pinned byte size; retain partial/no retry.")
    proof = dict(bytes=CALENDAR_CACHE.stat().st_size, expected_bytes=CALENDAR_BYTES, git_blob_sha1=git_blob(CALENDAR_CACHE),
        expected_git_blob_sha1=CALENDAR_BLOB, sha256=sha(CALENDAR_CACHE), source_URL=CALENDAR_URL, source_commit=SOURCE_COMMIT)
    proof["passed"] = proof["bytes"] == CALENDAR_BYTES and proof["git_blob_sha1"] == CALENDAR_BLOB
    return proof


def verify_base(prereg):
    if not isinstance(prereg, str) or re.fullmatch(r"[0-9a-f]{40}", prereg) is None:
        raise ValueError("Use the immutable full40-character lowercase prereg commit, never HEAD/branch/short alias.")
    resolved = subprocess.check_output(["git", "rev-parse", "--verify", prereg + "^{commit}"], cwd=ROOT, text=True).strip()
    if resolved != prereg: raise ValueError("Prereg must resolve exactly to the supplied immutable commit.")
    if subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() != "codex/work": raise ValueError("H06 stays on codex/work.")
    subprocess.check_call(["git", "merge-base", "--is-ancestor", prereg, "HEAD"], cwd=ROOT)
    dependencies = (SCRIPT, PLAN, SOURCE_NOTE, "analysis/grid24.py", "analysis/codex_hunt_v2_ldf_delta.py",
        "analysis/codex_s03_calendar.py", "analysis/replica.py", "agents/codex/RESEARCH_CONTROLS.md")
    hashes = {}
    for name in dependencies:
        raw = (ROOT / name).read_bytes()
        if committed(prereg, name) != raw or committed("HEAD", name) != raw: raise ValueError("Freeze exact H06 code/plan/source/dependencies before input:" + name)
        hashes[name] = hashlib.sha256(raw).hexdigest()
    return dict(prereg=prereg, implementation_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        hashes=hashes, versions=runtime_versions(), source_commit=SOURCE_COMMIT, source_URL=CALENDAR_URL,
        timezone_provenance=timezone_provenance(),
        timezone_interpretation="Europe/Berlin civilrelease/conference->America/Chicago viazoneinfo;nooffsetsearch")


def recheck(binding):
    for name, expected in binding["hashes"].items():
        if sha(ROOT / name) != expected: raise ValueError("H06 bound file changed:" + name)
    for name, expected in binding.get("timezone_provenance", {}).get("system_zone_files_sha256", {}).items():
        if sha(Path(name)) != expected: raise ValueError("Time-zone rule source changed during phase:" + name)


@contextmanager
def execution_lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "research.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB); yield


def calendar_phase(prereg):
    with execution_lock():
        binding = verify_base(prereg)
        for directory in (ROOT / "analysis/outputs").glob("codex_hunt_v2_ecb_preconference*"):
            if any((directory / name).exists() for name in ("calendar_attempt.json", "calendar_verified_execution.json", "cache/ecb_calendar.partial")):
                raise ValueError("Retained calendar attempt/completion exists; no retry/alternate source/directory.")
        started = utcnow(); dump_once(OUT / "calendar_attempt.json", dict(started_utc=started, prereg=prereg, script_sha256=sha(ROOT / SCRIPT)))
        dump_once(OUT / "calendar_pre_acquisition_binding.json", binding)
        stage = "single_pinned_download"; names = ["calendar_attempt.json", "calendar_pre_acquisition_binding.json"]
        try:
            proof = acquire_calendar(); dump_once(OUT / "calendar_byte_binding.json", proof); names.append("calendar_byte_binding.json")
            if not proof["passed"]: raise ValueError("Calendar byte/blob proof failed BEFORE parser.")
            stage = "ISOdates_header_claims_and_fixed_era_clock_quality"
            result = calendar_parse(CALENDAR_CACHE.read_bytes())
            dump_once(OUT / "calendar_quality.json", result); csv_once(OUT / "calendar_design_clocks.csv", pd.DataFrame(result["clocks"]))
            names += ["calendar_quality.json", "calendar_design_clocks.csv"]
            passed = result["passed"]
            status = "CALENDAR_QUALITY_PASS_REQUIRES_COMMITTED_ROOT_SOURCE_REVIEW" if passed else "CALENDAR_QUALITY_FAILED_NO_PRICES"
        except Exception as error:
            passed = False; status = "CALENDAR_ACCESS_HASH_FORMAT_OR_IMPLEMENTATION_BLOCKED"
            dump_once(OUT / "calendar_exception.json", dict(stage=stage, type=type(error).__name__, message=str(error), traceback=traceback.format_exc(),
                HTTP_status=error.code if isinstance(error, urllib.error.HTTPError) else None, retry_authorized=False)); names.append("calendar_exception.json")
        recheck(binding)
        marker = dict(started_utc=started, completed_utc=utcnow(), phase="calendar_only_no_prices", passed=passed, status=status,
            prereg=prereg, implementation_commit=binding["implementation_commit"], script_sha256=sha(ROOT / SCRIPT),
            artifacts_sha256={name: sha(OUT / name) for name in names}, cache_sha256=sha(CALENDAR_CACHE) if CALENDAR_CACHE.exists() else None,
            timezone_provenance=binding["timezone_provenance"],
            primary_date_corroboration_claimed=False, source_admission_before_prices_required=True, prices_or_returns_read=False,
            economic_evaluations=0, gross_screens=0)
        dump_once(CALENDAR_MARKER, marker)
        return dict(status=status, passed=passed, calendar_marker_sha256=sha(CALENDAR_MARKER), prices_read=False)


def validate_calendar_marker_contract(marker):
    if not (marker.get("phase") == "calendar_only_no_prices" and marker.get("passed") is True):
        raise ValueError("Strict calendar-only phase and boolean PASS required before prices.")
    artifacts = marker.get("artifacts_sha256")
    if not isinstance(artifacts, dict) or not set(CALENDAR_REQUIRED_ARTIFACTS).issubset(artifacts):
        raise ValueError("Calendar PASS marker is missing required clock/quality/byte/attempt/binding proof.")
    for name, expected in artifacts.items():
        if not isinstance(name, str) or Path(name).name != name or name in (".", "..") or "/" in name or "\\" in name:
            raise ValueError("Calendar artifact keys must be basenames only.")
        if not isinstance(expected, str) or SHA256_RE.fullmatch(expected) is None:
            raise ValueError("Calendar artifact hash must be a64-character lowercaseSHA256.")
    if not isinstance(marker.get("cache_sha256"), str) or SHA256_RE.fullmatch(marker["cache_sha256"]) is None:
        raise ValueError("Calendar cache SHA256 must be explicit and valid.")


def accepted_calendar_before_prices(prereg, calendar_sha):
    binding = verify_base(prereg)
    if sha(CALENDAR_MARKER) != calendar_sha: raise ValueError("Exact calendar PASS-marker SHA required before prices.")
    marker = json.loads(CALENDAR_MARKER.read_text())
    validate_calendar_marker_contract(marker)
    if not (marker["prereg"] == prereg and marker["script_sha256"] == sha(ROOT / SCRIPT)):
        raise ValueError("Frozen calendar/code/prereg quality PASS required.")
    for name, expected in marker["artifacts_sha256"].items():
        if sha(OUT / name) != expected: raise ValueError("Calendar artifact changed:" + name)
        binding["hashes"][str((OUT / name).relative_to(ROOT))] = expected
    if sha(CALENDAR_CACHE) != marker["cache_sha256"]: raise ValueError("Pinned calendar cache changed.")
    binding["hashes"][str(CALENDAR_CACHE.relative_to(ROOT))] = marker["cache_sha256"]
    binding["hashes"][str(CALENDAR_MARKER.relative_to(ROOT))] = calendar_sha
    raw = (ROOT / ROOT_REVIEW).read_bytes()
    if committed("HEAD", ROOT_REVIEW) != raw: raise ValueError("Commit ROOT source admission AFTER calendar and BEFORE prices.")
    review = json.loads(raw)
    if not (review.get("accepted_for_frozen_research") is True and review.get("calendar_marker_sha256") == calendar_sha):
        raise ValueError("ROOT has not admitted this exact calendar/source for the frozen research.")
    if any(not review.get(name) for name in ("availability_finding", "evidence", "limitations")):
        raise ValueError("ROOT source review must bind documented availability/evidence/limitations, not waive unknown clocks.")
    binding["hashes"][ROOT_REVIEW] = hashlib.sha256(raw).hexdigest()
    binding["root_source_review"] = review; binding["calendar_marker_sha256"] = calendar_sha
    binding["calendar_original_implementation_commit"] = marker["implementation_commit"]
    return binding


def build_native(binding):
    paths = [ROOT / f"data/6E_1min_{year}.csv" for year in YEARS]
    inventory = []; parts = []
    for path in paths:
        relative = str(path.relative_to(ROOT)); binding["hashes"][relative] = sha(path)
        with path.open("rb") as handle: header = handle.readline().decode("utf-8").rstrip("\r\n")
        inventory.append(dict(path=relative, bytes=path.stat().st_size, sha256=binding["hashes"][relative], header=header))
    # All5source hashes/headers bind before native numeric interpretation.
    dump_once(OUT / "gross_pre_price_binding.json", dict(binding, native_inventory=inventory))
    metadata_audits = []
    for path, year in zip(paths, YEARS):
        metadata = pd.read_csv(path, usecols=["date", "time"]); validate_metadata_keys(metadata, year, path.name)
        metadata_audits.append(dict(path=str(path.relative_to(ROOT)), year=year, source_rows=len(metadata),
            first_date=int(metadata.date.min()), last_date=int(metadata.date.max()), duplicate_metadata_keys=int(metadata.duplicated(["date", "time"]).sum())))
    # ALL5date/clock/year audits pass BEFORE any native OHLCV conversion.
    binding["native_metadata_audits"] = metadata_audits
    dump_once(OUT / "gross_native_metadata_audit.json", dict(all5_metadata_passed_before_any_native_values=True, sources=metadata_audits))
    for path in paths:
        frame = pd.read_csv(path, usecols=["date", "time", *FIELDS])
        frame["source_path"] = str(path.relative_to(ROOT)); frame["source_row_id"] = np.arange(len(frame)) + 2; parts.append(frame)
    frame = pd.concat(parts, ignore_index=True)
    duplicated = frame.duplicated(["date", "time"], keep=False); duplicates = frame.loc[duplicated].copy()
    group = duplicates.groupby(["date", "time"])[list(FIELDS)].nunique(dropna=False)
    conflicts = group.gt(1).any(axis=1); badkeys = set(conflicts[conflicts].index.tolist())
    duplicates["conflicting_key"] = [(d, t) in badkeys for d, t in zip(duplicates.date, duplicates.time)]
    unique = frame.drop_duplicates(["date", "time"], keep="first").sort_values(["date", "time"])
    valid = valid_ohlcv(*(unique[name].to_numpy(float) for name in FIELDS))
    prices = unique[list(FIELDS[:4])].to_numpy(float)
    ticks = np.isfinite(prices).all(axis=1) & np.isclose(prices / PRICE_TICK, np.rint(prices / PRICE_TICK), atol=1e-7, rtol=0).all(axis=1)
    invalid = unique.loc[~valid | ~ticks].copy()
    cache = OUT / "cache"; cache.mkdir(parents=True, exist_ok=True)
    for path, year in zip(paths, YEARS):
        link = cache / f"day_{year}.csv"
        if link.is_symlink():
            if link.resolve() != path.resolve(): raise ValueError("Native source link changed.")
        elif link.exists(): raise ValueError("Unbound native cache input.")
        else: link.symlink_to(path)
    if {path.name for path in cache.glob("*.csv")} != {f"day_{year}.csv" for year in YEARS}: raise ValueError("Unbound native input/year.")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        grid = Grid24(str(cache / "day_*.csv"), night_pattern="")
    rows, cols = np.searchsorted(grid.dates, unique.date.to_numpy()), jof(unique.time.to_numpy())
    presence = np.zeros((grid.D, 1440), bool); presence[rows, cols] = True
    for name, attr in zip(FIELDS, ("o", "h", "l", "c", "v")):
        if not np.allclose(getattr(grid, attr)[rows, cols], unique[name].to_numpy(float), equal_nan=True): raise ValueError("Shared grid differs from source-audited duplicate policy.")
    audit = dict(source_rows=len(frame), unique_rows=len(unique), duplicate_excess_rows=int(frame.duplicated(["date", "time"]).sum()),
        conflicting_duplicate_keys=int(conflicts.sum()), invalid_OHLCV_or_price_tick_rows=len(invalid),
        standard_6E_price_tick=PRICE_TICK, floating_tick_check_tolerance_ticks=1e-7,
        future_or_old_strategy_inputs_read=False, native_M6E_quote_or_execution_verified=False)
    return grid, presence, audit, duplicates, invalid


def extract_events(grid, presence, clocks):
    valid = valid_ohlcv(grid.o, grid.h, grid.l, grid.c, grid.v)
    by_date = {int(day): row for row, day in enumerate(grid.dates)}
    entries, audit = [], []
    for clock in clocks.to_dict("records"):
        day = clock["date"]; row = by_date.get(int(day.replace("-", "")))
        eligible, disposition, reason = entry_calendar_disposition(day)
        if not eligible:
            audit.append(dict(clock, event_id="ECB_" + day.replace("-", ""), row=row,
                eligible_calendar=False, calendar_disposition=disposition, calendar_disposition_reason=reason,
                source_window_complete=None, missing_or_invalid_window_minutes="[]", endpoint_open_valid=None,
                reaction_points=None, reaction_side=None, flat_reaction=False, entry=None,
                event_price_window_inspected=False, raw_endpoint_returns_calculated=False))
            continue
        start, feature, entry, end = (int(clock[name]) for name in ("reaction_first_j", "reaction_last_j", "entry_j", "exit_j"))
        missing = list(range(start, end)) if row is None else [j for j in range(start, end) if not (presence[row, j] and valid[row, j])]
        endpoint = bool(row is not None and presence[row, end] and np.isfinite(grid.o[row, end]) and grid.o[row, end] > 0)
        complete = row is not None and not missing and endpoint
        reaction = float(grid.c[row, feature] - grid.o[row, start]) if row is not None and valid[row, start] and valid[row, feature] else None
        side = 1 if reaction is not None and reaction > 0 else -1 if reaction is not None and reaction < 0 else 0
        event = dict(clock, event_id="ECB_" + day.replace("-", ""), row=row,
            eligible_calendar=True, calendar_disposition=disposition, calendar_disposition_reason=reason,
            source_window_complete=complete, missing_or_invalid_window_minutes=json.dumps(missing), endpoint_open_valid=endpoint,
            reaction_points=reaction, reaction_side=side, flat_reaction=side == 0 and reaction is not None,
            entry=float(grid.o[row, entry]) if row is not None and valid[row, entry] else None,
            event_price_window_inspected=True, raw_endpoint_returns_calculated=False)
        audit.append(event)
        if side != 0: entries.append(dict(event, side=side))
    return pd.DataFrame(entries), pd.DataFrame(audit)


def admission_gate(entries, events, source):
    sides = entries.reaction_side.value_counts().to_dict() if len(entries) else {}
    eligible = events[events.eligible_calendar.astype(bool)] if len(events) else events
    complete = len(events) == 40 and bool(eligible.source_window_complete.fillna(False).astype(bool).all())
    passed = bool(complete and source["conflicting_duplicate_keys"] == 0 and source["invalid_OHLCV_or_price_tick_rows"] == 0
        and len(entries) >= MIN_EVENTS and sides.get(1, 0) >= MIN_SIDE and sides.get(-1, 0) >= MIN_SIDE)
    return dict(phase="pre_gross", passed=passed, scheduled_events=len(events), nonflat_events=len(entries),
        primary_longs=int(sides.get(1, 0)), primary_shorts=int(sides.get(-1, 0)), minimum_events=MIN_EVENTS, minimum_each_side=MIN_SIDE,
        eligible_calendar_events=len(eligible), skipped_calendar_events=len(events) - len(eligible),
        all_eligible_reaction_wait_held_endpoint_windows_complete=complete,
        incomplete_event_IDs=eligible.loc[~eligible.source_window_complete.fillna(False).astype(bool), "event_id"].tolist() if len(eligible) else [],
        source=source, raw_returns_calculated=False, gross_screen_runs=0, economic_evaluations=0,
        reason="Source/countPASS only; raw endpoints still gated" if passed else "Source/countfailedBEFOREendpointreturns;closeH06latergates")


def raw_after_admission(grid, entries, gate, attach=None):
    if not gate["passed"]: return entries.copy(), gate, None
    if attach is None:
        exit_prices = grid.o[entries.row.to_numpy(int), entries.exit_j.to_numpy(int)]
        gross_points = exit_prices - entries.entry.to_numpy(float)
    else: exit_prices, gross_points = attach(grid, entries)
    frames = []
    for model in ("FOLLOW5", "LONG_CALENDAR"):
        frame = entries.copy(); frame["model"] = model
        frame["side"] = entries.reaction_side.to_numpy(int) if model == "FOLLOW5" else 1
        frame["raw_exit_open"] = exit_prices; frame["gross_M6E"] = gross_points * frame.side.to_numpy(int) * NATIVE_POINT_VALUE
        frame["raw_endpoint_returns_calculated"] = True; frames.append(frame)
    result = pd.concat(frames, ignore_index=True); summaries = []
    for model in ("FOLLOW5", "LONG_CALENDAR"):
        for period in ("2018-22", *map(str, YEARS)):
            for side, sign in (("both", None), ("long", 1), ("short", -1)):
                part = result[result.model == model]
                if period != "2018-22": part = part[part.year == int(period)]
                if sign is not None: part = part[part.side == sign]
                values = part.gross_M6E.to_numpy(float); sd = float(values.std(ddof=1)) if len(values) > 1 else None
                summaries.append(dict(model=model, period=period, side=side, events=len(values), total=float(values.sum()),
                    mean=float(values.mean()) if len(values) else None, SD=sd, SE=sd / np.sqrt(len(values)) if sd is not None else None, t=tstat(values)))
    primary = result[result.model == "FOLLOW5"].gross_M6E
    passed = bool(primary.mean() >= GROSS_HURDLE)
    decision = dict(gate, phase="raw_gross", passed=passed, raw_returns_calculated=True, gross_screen_runs=1,
        primary_gross_mean_M6E=float(primary.mean()), primary_gross_t=tstat(primary), gross_hurdle_M6E=GROSS_HURDLE,
        conservative_native_RT_upper_cost_M6E=RT_UPPER_COST, costs_subtracted=False, stopped_or_bracket_outcomes_calculated=False)
    return result, decision, pd.DataFrame(summaries)


def gross_phase(prereg, calendar_sha):
    with execution_lock():
        binding = accepted_calendar_before_prices(prereg, calendar_sha)
        for directory in (ROOT / "analysis/outputs").glob("codex_hunt_v2_ecb_preconference*"):
            if any((directory / name).exists() for name in ("gross_attempt.json", "gross_verified_execution.json", "pre_gross_verified_execution.json")):
                raise ValueError("Retained H06price/gross attempt exists; no automatic retry/alternate directory.")
        started = utcnow(); dump_once(OUT / "gross_attempt.json", dict(started_utc=started, prereg=prereg, calendar_marker_sha256=calendar_sha))
        names = ["gross_attempt.json"]; stage = "source_inventory_and_native_admission"
        try:
            grid, presence, source, duplicates, invalid = build_native(binding)
            stage = "frozen_clock_reaction_wait_and_held_event_admission"
            clocks = pd.read_csv(OUT / "calendar_design_clocks.csv")
            entries, events = extract_events(grid, presence, clocks)
            gate = admission_gate(entries, events, source)
            for name, frame in (("gross_parent_entries.csv", entries), ("gross_all_calendar_event_audit.csv", events),
                ("gross_duplicate_source_rows.csv", duplicates), ("gross_invalid_source_rows.csv", invalid)):
                csv_once(OUT / name, frame); names.append(name)
        except Exception as error:
            grid = None; entries = pd.DataFrame()
            gate = dict(phase="pre_gross", passed=False, raw_returns_calculated=False, gross_screen_runs=0, economic_evaluations=0,
                status="SOURCE_FORMAT_OR_IMPLEMENTATION_BLOCKED", stage=stage, exception_type=type(error).__name__, exception_message=str(error))
            dump_once(OUT / "gross_source_exception.json", dict(gate, traceback=traceback.format_exc())); names.append("gross_source_exception.json")
        result, decision, summary = raw_after_admission(grid, entries, gate)
        recheck(binding)
        if decision["raw_returns_calculated"]:
            csv_once(OUT / "gross_events.csv", result); csv_once(OUT / "gross_summary.csv", summary); names += ["gross_events.csv", "gross_summary.csv"]
        gate_name = "gross_gate.json" if decision["raw_returns_calculated"] else "pre_gross_gate.json"
        dump_once(OUT / gate_name, decision); dump_once(OUT / "gross_input_binding.json", binding)
        dump_once(OUT / "gross_cost_bridge.json", dict(M6E_point_value=NATIVE_POINT_VALUE, M6E_tick=.0001, M6E_tick_value=1.25,
            standard_6E_tick=PRICE_TICK, commission_RT=1.24, adverse_native_market_tick_per_fill=1.25,
            maximum_native_quantization_per_fill=.625, RT_cost_upper=4.99, RAW_gross_hurdle=9.98,
            no_raw_fee_or_quantization_subtraction=True, actual_M6E_fills_not_verified=True, no_later_fixed_stop_or_net_models_run=True))
        names += [gate_name, "gross_input_binding.json", "gross_cost_bridge.json"]
        if (OUT / "gross_pre_price_binding.json").exists(): names.append("gross_pre_price_binding.json")
        if (OUT / "gross_native_metadata_audit.json").exists(): names.append("gross_native_metadata_audit.json")
        marker = dict(started_utc=started, completed_utc=utcnow(), phase=decision["phase"], passed=decision["passed"],
            prereg=prereg, implementation_commit=binding["implementation_commit"], script_sha256=sha(ROOT / SCRIPT),
            calendar_marker_sha256=calendar_sha, artifacts_sha256={name: sha(OUT / name) for name in names},
            raw_returns_calculated=decision["raw_returns_calculated"], gross_screen_runs=decision["gross_screen_runs"], economic_evaluations=0,
            primary_date_corroboration_claimed=False, stopped_validation_or_account_outcomes_run=False)
        dump_once(OUT / ("gross_verified_execution.json" if decision["raw_returns_calculated"] else "pre_gross_verified_execution.json"), marker)
        return decision


def fixtures():
    checks = []
    assert event_clocks("2018-01-25")["R"] == 405 and event_clocks("2018-07-26")["R"] == 405
    assert event_clocks("2018-03-15")["R"] == 465 and event_clocks("2018-11-01")["R"] == 465
    newer = event_clocks("2022-07-21")
    assert newer["R"] == 435 and newer["P"] == 465 and newer["entry_j"] == 446
    assert event_clocks("2022-06-09")["P"] == 450
    checks.append("BerlinCTwinter/summer/US-EUDSTmismatch;fixed20220721era;nooffsetsearch")
    raw = "# scheduled calendar, https://www.ecb.europa.eu/press/pressconf/\n"
    for year in YEARS:
        first = date(year, 1, 1)
        first += timedelta(days=(3 - first.weekday()) % 7)
        raw += "".join((first + timedelta(weeks=4 * n)).isoformat() + "\n" for n in range(8))
    quality = calendar_parse(raw.encode())
    assert quality["passed"] and quality["design_dates"] == 40 and not quality["primary_2018_22_date_independent_corroboration"]
    assert not calendar_parse((raw + "2018-01-04\n").encode())["passed"]
    assert not calendar_parse(raw.replace("https://www.ecb.europa.eu/press/pressconf/", "NO_PRIMARY_URL").encode())["passed"]
    checks.append("40fixedcalendarrows/8uniqueweekdayperyear/commentsURLs;duplicates/schemafail;qualitynotprimaryauth")
    no = dict(passed=False, phase="pre_gross", raw_returns_calculated=False, gross_screen_runs=0)
    def forbidden(*args): raise AssertionError("Endpoint arithmetic called after source/count failure.")
    _, stopped, summary = raw_after_admission(None, pd.DataFrame(), no, attach=forbidden)
    assert not stopped["raw_returns_calculated"] and summary is None
    checks.append("source/countgatebeforeANYgrossendpoint;0screens/0econonfailure")
    clock = event_clocks("2018-01-25"); shape = (1, 1440)
    arrays = {name: np.full(shape, np.nan) for name in ("o", "h", "l", "c", "v")}
    presence = np.zeros(shape, bool)
    for j in range(clock["reaction_first_j"], clock["P"] + 1):
        for name, value in (("o", 1.2), ("h", 1.2001), ("l", 1.1999), ("c", 1.2), ("v", 10.)): arrays[name][0, j] = value
        presence[0, j] = True
    arrays["c"][0, clock["reaction_last_j"]] = 1.20005
    grid = type("Artificial", (), dict(**arrays, dates=np.array([20180125])))()
    entries, events = extract_events(grid, presence, pd.DataFrame([clock]))
    assert len(entries) == 1 and entries.iloc[0].side == 1 and entries.iloc[0].entry_j == clock["R"] + 11
    presence[0, clock["R"] + 7] = False
    _, missing = extract_events(grid, presence, pd.DataFrame([clock]))
    assert not missing.iloc[0].source_window_complete and clock["R"] + 7 in json.loads(missing.iloc[0].missing_or_invalid_window_minutes)
    checks.append("first5reaction+5processingwait+heldsourcecompleteness;waitgapretainednotdeleted")
    source = dict(conflicting_duplicate_keys=0, invalid_OHLCV_or_price_tick_rows=0)
    complete40 = pd.DataFrame([dict(eligible_calendar=True, source_window_complete=True, event_id=f"ARTIFICIAL_{i}") for i in range(40)])
    enough = pd.DataFrame(dict(reaction_side=[1] * 30 + [-1] * 5))
    assert admission_gate(enough, complete40, source)["passed"]
    assert not admission_gate(enough.iloc[:-1], complete40, source)["passed"]
    one_side = pd.DataFrame(dict(reaction_side=[1] * 31 + [-1] * 4))
    assert not admission_gate(one_side, complete40, source)["passed"]
    complete40.loc[0, "source_window_complete"] = False
    assert not admission_gate(enough, complete40, source)["passed"]
    checks.append("35event/min5eachsideBEFOREreturns;all40sourcewindowsmustbecomplete/retainfailures")
    reverse = raw.splitlines()[0] + "\n" + "\n".join(reversed(raw.splitlines()[1:])) + "\n"
    unordered = calendar_parse(reverse.encode())
    assert not unordered["passed"] and unordered["nonmonotone_date_pairs"] and not unordered["duplicate_dates"]
    checks.append("calendarstrictmonotonicISOsequence;nooutcomebasedsort/repair")
    proof = dict(phase="calendar_only_no_prices", passed=True, cache_sha256="1" * 64,
        artifacts_sha256={name: "0" * 64 for name in CALENDAR_REQUIRED_ARTIFACTS})
    validate_calendar_marker_contract(proof)
    variants = []
    variants.append(dict(proof, phase="raw_gross")); variants.append(dict(proof, passed="True"))
    variants.append(dict(proof, artifacts_sha256={name: value for name, value in proof["artifacts_sha256"].items() if name != "calendar_design_clocks.csv"}))
    variants.append(dict(proof, artifacts_sha256=dict(proof["artifacts_sha256"], **{"../escape": "0" * 64})))
    variants.append(dict(proof, artifacts_sha256=dict(proof["artifacts_sha256"], **{"bad.json": "not_a_hash"})))
    for bad in variants:
        try: validate_calendar_marker_contract(bad)
        except ValueError: pass
        else: raise AssertionError("Malformed/missing/unsafe calendar proof admitted.")
    for alias in ("HEAD", "codex/work", "f9e756c", "A" * 40):
        try: verify_base(alias)
        except ValueError: pass
        else: raise AssertionError("Mutable/ambiguous prereg alias admitted.")
    checks.append("strictcalendarPASSphase/bool/requiredproofhashes/basenames;immutablepreregnoHEADaliases")
    class NoSkippedWindow(np.ndarray):
        def __getitem__(self, key):
            if isinstance(key, tuple): raise AssertionError("Skipped holiday event price window accessed.")
            return super().__getitem__(key)
    excluded_arrays = {name: np.full((1, 1440), np.nan).view(NoSkippedWindow) for name in ("o", "h", "l", "c", "v")}
    holiday_grid = type("ArtificialHoliday", (), dict(**excluded_arrays, dates=np.array([20190704])))()
    excluded_entries, excluded_events = extract_events(holiday_grid, np.zeros((1, 1440), bool), pd.DataFrame([event_clocks("2019-07-04")]))
    assert excluded_entries.empty and len(excluded_events) == 1 and not excluded_events.iloc[0].eligible_calendar
    assert excluded_events.iloc[0].calendar_disposition == "SKIP_HOLIDAY" and not excluded_events.iloc[0].event_price_window_inspected
    assert excluded_events.iloc[0].reaction_points is None
    checks.append("sharedholiday/earlyentrydispositionbeforeeventpricewindows;all40rosterIDsretainedwithoutskippedoutcomes")
    global CALENDAR_CACHE
    original_cache = CALENDAR_CACHE
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="synthetic_transport_", dir=OUT) as temporary:
        CALENDAR_CACHE = Path(temporary) / "calendar.partial"
        calls = []
        def denied(request, timeout):
            calls.append((request.full_url, timeout))
            raise urllib.error.HTTPError(request.full_url, 403, "artificial denied", {}, None)
        try:
            try: acquire_calendar(opener=denied)
            except urllib.error.HTTPError: pass
            else: raise AssertionError("Synthetic403didnotstop.")
            assert len(calls) == 1 and calls[0] == (CALENDAR_URL, 45) and CALENDAR_CACHE.exists()
            try: acquire_calendar(opener=denied)
            except FileExistsError: pass
            else: raise AssertionError("Retainedpartialwasoverwritten/retried.")
            assert len(calls) == 1
        finally: CALENDAR_CACHE = original_cache
    checks.append("singlepinnedGET/no403retry;partialwriteonce;noactualnetworkinthefixture")
    return dict(passed=True, checks=checks, actual_calendar_downloaded_or_6E_prices_read=False,
        actual_raw_or_stopped_returns_calculated=False, script_sha256=sha(ROOT / SCRIPT), versions=runtime_versions())


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--phase", required=True, choices=("fixtures", "calendar", "gross"))
    parser.add_argument("--prereg"); parser.add_argument("--calendar-sha")
    args = parser.parse_args()
    if args.phase == "fixtures":
        result = fixtures(); dump_once(OUT / f"synthetic_checks_{result['script_sha256'][:12]}.json", result)
    else:
        if not args.prereg: parser.error("Actual phase requires committed --prereg.")
        if args.phase == "calendar": result = calendar_phase(args.prereg)
        else:
            if not args.calendar_sha: parser.error("Gross requires exact --calendar-sha plus committed ROOT review before prices.")
            result = gross_phase(args.prereg, args.calendar_sha)
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__": main()
