"""H05 E1 selected high-win Morning Momentum: independent gross-first rebuild.

Imports never read actual market/MC/cache rows. Signal is the frozen observed-
bucket Python E1 definition, not a PL/MC parity claim. Entry/source/held audit
precedes ANY entry->OPEN14:51 raw return. No stop/target/BO/account engine runs.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import traceback
from types import SimpleNamespace
import warnings

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_hunt_v2_highwin_confirmation"
SCRIPT = "analysis/codex_hunt_v2_highwin_gross.py"
HELPER = "analysis/codex_hunt_v2_highwin_signal.py"
PLAN = "agents/codex/plans/hunt_v2_highwin_confirmation.md"
EVIDENCE = "agents/codex/research/hunt_v2_next_executable_nomination.md"
NOTE = EVIDENCE
SOURCE_MANIFEST = "agents/codex/inputs/hunt_v2_highwin_confirmation/source_manifest.json"
SOURCE_REF = "d14dc9a"
SOURCE_PATHS = ("analysis/high_winrate_test.py", "analysis/twin_continuation_test.py", "analysis/high_winrate_bench.py")
WARMUP = "agents/codex/inputs/ob_v2_bench/NQ_1min_2017.csv"
YEARS = tuple(range(2018, 2023))
ALL_YEARS = (2017, *YEARS)
STATE_START = 20170901
EXIT_J, MIN_EVENTS, RT_COST, HURDLE = 891, 100, 2.24, 4.48
FIELDS = ("open", "high", "low", "close", "volume")
sys.path.insert(0, str(ROOT / "analysis"))
from grid24 import Grid24, jof
from codex_s03_calendar import calendar_status
from replica import is_early_close
from codex_hunt_v2_ldf_delta import csv_once, dump_once, runtime_versions, sha, tstat, utcnow, valid_ohlcv, validate_metadata_keys


def native_paths():
    return [str(ROOT / WARMUP), *[str(ROOT / f"data/NQ_1min_{y}.csv") for y in YEARS],
        *[str(ROOT / f"data/NQ_1min_ON_{y}.csv") for y in ALL_YEARS]]


def allowed_day(day):
    d = pd.Timestamp(day)
    return calendar_status(d)["kind"] == "normal" and d.dayofweek < 5 and not is_early_close(d)


def committed(ref, name):
    return subprocess.check_output(["git", "show", f"{ref}:{name}"], cwd=ROOT)


def csv_gzip_once(path, frame):
    with path.open("xb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8", newline="") as handle:
                frame.to_csv(handle, index=False, float_format="%.12g")


def audited_native(paths):
    parts = []
    for name in paths:
        frame = pd.read_csv(name, usecols=["date", "time", *FIELDS])
        frame["source_path"] = str(Path(name).relative_to(ROOT)); frame["source_row_id"] = np.arange(len(frame)) + 2
        parts.append(frame)
    frame = pd.concat(parts, ignore_index=True)
    duplicated = frame.duplicated(["date", "time"], keep=False)
    duplicates = frame.loc[duplicated].copy()
    groups = duplicates.groupby(["date", "time"])[list(FIELDS)].nunique(dropna=False)
    conflicts = groups.gt(1).any(axis=1); conflict_keys = set(conflicts[conflicts].index.tolist())
    duplicates["conflicting_key"] = [(d, t) in conflict_keys for d, t in zip(duplicates.date, duplicates.time)]
    unique = frame.drop_duplicates(["date", "time"], keep="first").sort_values(["date", "time"])
    valid = valid_ohlcv(*(unique[field].to_numpy(float) for field in FIELDS))
    active = unique.date.to_numpy() >= STATE_START
    invalid = unique.loc[~valid].copy()
    audit = dict(source_rows=len(frame), unique_rows=len(unique), all_duplicate_source_IDs_retained=True,
        identical_duplicate_excess_rows=int(frame.duplicated(["date", "time"]).sum()) if not conflict_keys else None,
        conflicting_duplicate_keys=int(conflicts.sum()), invalid_observed_OHLCV_rows=int((~valid).sum()),
        invalid_observed_rows_after_state_start=int((~valid & active).sum()), state_start=STATE_START,
        missing_ideal_minutes_not_imputed=True, observed_bucket_definition_not_unbounded_ideal_lineage=True)
    return unique, audit, duplicates, invalid


def build_grid(binding):
    paths = binding["native_paths"]
    frame, audit, duplicates, invalid = audited_native(paths)
    cache = OUT / "cache"; cache.mkdir(parents=True, exist_ok=True)
    for name in paths:
        source = Path(name); prefix = "night" if "_ON_" in source.name else "day"
        link = cache / f"{prefix}_{source.stem[-4:]}.csv"
        if link.is_symlink():
            if link.resolve() != source.resolve(): raise ValueError("Unexpected isolated grid symlink.")
        elif link.exists(): raise ValueError("Unexpected nonlink cache input.")
        else: link.symlink_to(source)
    if {path.name for path in cache.glob("*.csv")} != {f"{prefix}_{y}.csv" for prefix in ("day", "night") for y in ALL_YEARS}:
        raise ValueError("Unbound input/year in isolated grid cache.")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        grid = Grid24(str(cache / "day_*.csv"), str(cache / "night_*.csv"))
    if pd.DatetimeIndex(grid.ts).year.min() != 2017 or pd.DatetimeIndex(grid.ts).year.max() != 2022:
        raise ValueError("Native grid crossed explicit2017warmup/2018--22 scope.")
    rows, cols = np.searchsorted(grid.dates, frame.date.to_numpy()), jof(frame.time.to_numpy())
    presence = np.zeros((grid.D, 1440), bool); presence[rows, cols] = True
    for field, attr in zip(FIELDS, ("o", "h", "l", "c", "v")):
        if not np.allclose(getattr(grid, attr)[rows, cols], frame[field].to_numpy(float), equal_nan=True):
            raise ValueError("Shared grid differs from source-audited first values:" + field)
    return grid, presence, audit, duplicates, invalid


def observed_records(grid, presence):
    # The selected Python definition observes finite-close Data1 bars. An
    # invalid selected observed field is an admission failure, never repaired.
    mask = presence & np.isfinite(grid.c) & (grid.dates >= STATE_START)[:, None]
    flat = np.flatnonzero(mask)
    row, minute = flat // 1440, flat % 1440
    return dict(o=grid.o.ravel()[flat], h=grid.h.ravel()[flat], l=grid.l.ravel()[flat], c=grid.c.ravel()[flat],
        row=row, j=minute, date=grid.dates[row], global_index=flat)


def indicator_entries(grid, presence):
    from codex_hunt_v2_highwin_signal import reconstruct_mo
    signals, buckets = reconstruct_mo(observed_records(grid, presence))
    signals = pd.DataFrame(signals)
    buckets = pd.DataFrame(buckets)
    valid = valid_ohlcv(grid.o, grid.h, grid.l, grid.c, grid.v)
    calendar = []
    for row, timestamp in enumerate(pd.DatetimeIndex(grid.ts)):
        if timestamp.year not in YEARS: continue
        observed_RTH = int(presence[row, 511:916].sum())
        calendar.append(dict(date=timestamp.date().isoformat(), year=timestamp.year, row=row,
            allowed_calendar=allowed_day(timestamp), calendar_kind=calendar_status(timestamp)["kind"],
            observed_RTH_0831_1515=observed_RTH, missing_RTH_0831_1515=405 - observed_RTH,
            whole_expected_normal_RTH_missing=bool(allowed_day(timestamp) and observed_RTH == 0),
            observed_full_date_bars=int(presence[row].sum()),
            source_missing_minutes_reported_not_ideal_history_repair=True))
    entries, unresolved = [], []
    for signal in signals.to_dict("records") if len(signals) else []:
        row, minute = int(signal["row"]), int(signal["j"])
        timestamp = pd.Timestamp(grid.ts[row])
        if timestamp.year not in YEARS or not allowed_day(timestamp): continue
        entry_j = minute + 1
        entry_ok = bool(entry_j < 1440 and presence[row, entry_j] and valid[row, entry_j])
        held_bad = int((~valid[row, entry_j:EXIT_J]).sum())
        endpoint_ok = bool(presence[row, EXIT_J] and np.isfinite(grid.o[row, EXIT_J]) and grid.o[row, EXIT_J] > 0)
        day = timestamp.normalize()
        at = lambda j: (day + pd.Timedelta(minutes=j)).tz_localize("America/Chicago").isoformat()
        event = dict(signal)
        event.update(date=timestamp.date().isoformat(), year=timestamp.year,
            event_id=f"HW_E1_{int(grid.dates[row])}_01", entry_j=entry_j,
            entry=float(grid.o[row, entry_j]) if entry_ok else None, entry_valid=entry_ok,
            raw_exit_j=EXIT_J, endpoint_open_valid=endpoint_ok, invalid_held_minutes=held_bad,
            unresolved_held_path=held_bad > 0,
            feature_event_time=at(minute), assumed_available_at=at(minute), decision_time=at(minute),
            first_fill_interval_start=at(minute), first_fill_interval_end=at(entry_j),
            receipt_verified=False, ordinary_observed_price_receipt_not_fatal_extra_gate=True,
            raw_endpoint_arithmetic_calculated=False)
        entries.append(event)
        if not (entry_ok and endpoint_ok and held_bad == 0):
            unresolved.append(dict(event_id=event["event_id"], date=event["date"], entry_valid=entry_ok,
                endpoint_open_valid=endpoint_ok, invalid_held_minutes=held_bad))
    columns = ("date", "year", "event_id", "row", "j", "side", "entry_j", "entry", "entry_valid", "endpoint_open_valid", "invalid_held_minutes", "unresolved_held_path")
    events = pd.DataFrame(entries) if entries else pd.DataFrame(columns=columns)
    return events, pd.DataFrame(calendar), buckets, pd.DataFrame(unresolved), signals


def admission_gate(entries, calendar, native_audit, unresolved):
    whole_days = int(calendar.whole_expected_normal_RTH_missing.astype(bool).sum())
    passed = (native_audit["conflicting_duplicate_keys"] == 0 and native_audit["invalid_observed_OHLCV_rows"] == 0
        and len(unresolved) == 0 and len(entries) >= MIN_EVENTS)
    return dict(phase="pre_gross", passed=bool(passed), events=len(entries),
        conflicting_duplicate_keys=native_audit["conflicting_duplicate_keys"], invalid_observed_OHLCV_rows=native_audit["invalid_observed_OHLCV_rows"],
        missing_whole_expected_normal_sessions=whole_days, unresolved_entry_endpoint_or_held_events=len(unresolved),
        whole_missing_session_is_reported_NO_OBSERVATIONS_not_raw_signal_repair_or_fatal_veto=True,
        minimum_events_before_raw_endpoint_attachment=MIN_EVENTS, minimum_count_pass=len(entries) >= MIN_EVENTS,
        raw_returns_calculated=False, gross_screen_runs=0, economic_evaluations=0,
        source_definition="Fixed selected Python E1 observed10minbuckets; not TwinPL/MCparity",
        partial_observed_bucket_state_is_literal_not_repaired=True,
        reason="Source/entry/held admission PASS" if passed else "Source/entry/held admission failed before raw endpoint arithmetic; no profitability verdict")


def attach_raw(grid, entries):
    result = entries.copy()
    exits = grid.o[result.row.to_numpy(int), EXIT_J]
    if not (np.isfinite(exits).all() and (exits > 0).all()): raise ValueError("Admitted OPEN14:51 endpoint absent.")
    result["raw_exit_open"] = exits
    result["gross_points"] = (exits - result.entry.to_numpy(float)) * result.side.to_numpy(int)
    result["gross_MNQ"] = result.gross_points * 2.0
    result["raw_endpoint_arithmetic_calculated"] = True
    return result


def summaries(events):
    records = []
    for period in ("2018-22", *map(str, YEARS)):
        subset = events if period == "2018-22" else events[events.year == int(period)]
        for side, number in (("both", None), ("long", 1), ("short", -1)):
            part = subset if number is None else subset[subset.side == number]
            values = part.gross_MNQ.to_numpy(float)
            sd = float(values.std(ddof=1)) if len(values) > 1 else None
            records.append(dict(period=period, side=side, events=len(values), total_MNQ=float(values.sum()),
                mean_MNQ=float(values.mean()) if len(values) else None, SD=sd,
                SE=sd / np.sqrt(len(values)) if sd is not None else None, t=tstat(values)))
    return pd.DataFrame(records)


def after_admission(grid, entries, admission, attach=attach_raw):
    if not admission["passed"]: return entries.copy(), admission, None
    events = attach(grid, entries)
    mean = float(events.gross_MNQ.mean()) if len(events) else None
    passed = len(events) >= MIN_EVENTS and mean is not None and mean >= HURDLE
    gate = dict(admission, phase="raw_gross", passed=bool(passed), raw_returns_calculated=True, gross_screen_runs=1,
        primary="E1_selected_T.10_S.20_ATR15_definition_raw_NO_STOP", minimum_events=MIN_EVENTS,
        gross_mean_MNQ=mean, gross_t=tstat(events.gross_MNQ), native_roundtrip_cost_MNQ=RT_COST, gross_hurdle_MNQ=HURDLE,
        costs_subtracted=False, stop_target_or_design_returns_calculated=False,
        reason="Gross PASS only; frozen protected design remains separate" if passed else "Frozen gross gate failed; stop H05 before protected design/bench/2023+")
    return events, gate, summaries(events)


def verify_before_data(prereg):
    if subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() != "codex/work": raise ValueError("H05 must run on codex/work.")
    subprocess.check_call(["git", "merge-base", "--is-ancestor", prereg, "HEAD"], cwd=ROOT)
    for directory in (ROOT / "analysis/outputs").glob("codex_hunt_v2_highwin_confirmation*"):
        if any((directory / name).exists() for name in ("gross_attempt.json", "pre_gross_verified_execution.json", "gross_verified_execution.json")):
            raise ValueError("Retained H05 attempt/completion exists; no automatic retry/alternate directory.")
    manifest = json.loads((ROOT / SOURCE_MANIFEST).read_text())
    sources = manifest["sources"]
    if {source["source_path"] for source in sources} != set(SOURCE_PATHS) or len(sources) != 3:
        raise ValueError("Source archives must be exactly the3frozen selected-rule definitions.")
    source_names = []
    for source in sources:
        name = source["path"]
        if not name.startswith("agents/codex/inputs/hunt_v2_highwin_confirmation/"):
            raise ValueError("Archive outside candidate inputs.")
        raw = (ROOT / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != source["sha256"] or raw != committed(SOURCE_REF, source["source_path"]):
            raise ValueError("Archive differs from immutable selected source:" + name)
        source_names.append(name)
    dependencies = [SCRIPT, HELPER, "analysis/grid24.py", "analysis/codex_s03_calendar.py", "analysis/replica.py",
        "analysis/codex_hunt_v2_ldf_delta.py", "agents/codex/RESEARCH_CONTROLS.md"]
    required = [PLAN, EVIDENCE, NOTE, SOURCE_MANIFEST, *source_names, *dependencies]
    hashes = {}
    for name in required:
        raw = (ROOT / name).read_bytes()
        if committed(prereg, name) != raw or committed("HEAD", name) != raw: raise ValueError("Commit/freeze exact H05 scope/code/source before data:" + name)
        hashes[name] = hashlib.sha256(raw).hexdigest()
    paths = native_paths()
    inventory = []
    for name in paths:
        path = Path(name); relative = str(path.relative_to(ROOT))
        if not path.is_file() or path.is_symlink(): raise ValueError("Frozen source missing/redirected:" + name)
        hashes[relative] = sha(path)
        with path.open("rb") as handle: header = handle.readline().decode("utf-8").rstrip("\r\n")
        inventory.append(dict(path=relative, bytes=path.stat().st_size, sha256=hashes[relative], header=header))
    return dict(prereg=prereg, implementation_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        source_ref=SOURCE_REF, hashes=hashes, inventory=inventory, native_paths=paths,
        versions=runtime_versions(), all_source_definitions_archival_only_not_imported=True, no2023plus_OR_MC_input=True)


def metadata_audit(binding):
    result = []
    for name in binding["native_paths"]:
        path = Path(name); frame = pd.read_csv(path, usecols=["date", "time"])
        validate_metadata_keys(frame, int(path.stem[-4:]), path.name)
        result.append(dict(path=str(path.relative_to(ROOT)), rows=len(frame), first_date=int(frame.date.min()),
            last_date=int(frame.date.max()), duplicate_keys=int(frame.duplicated(["date", "time"]).sum())))
    return result


@contextmanager
def execution_lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "gross.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB); yield


def gross(prereg):
    with execution_lock():
        binding = verify_before_data(prereg); started = utcnow(); stage = "metadata"
        dump_once(OUT / "gross_attempt.json", dict(started_utc=started, prereg=prereg,
            implementation_commit=binding["implementation_commit"], script_sha256=sha(ROOT / SCRIPT)))
        dump_once(OUT / "gross_pre_rows_binding.json", binding)
        saved = ["gross_attempt.json", "gross_pre_rows_binding.json"]
        try:
            binding["metadata"] = metadata_audit(binding)
            stage = "native_source_grid"
            grid, presence, native_audit, duplicates, invalid = build_grid(binding)
            stage = "independent_observed_MO_signal_ENTRY_and_held_audit"
            entries, calendar, buckets, unresolved, source_signals = indicator_entries(grid, presence)
            admission = admission_gate(entries, calendar, native_audit, unresolved)
            for name, frame in (("parent_entries.csv", entries), ("gross_calendar_audit.csv", calendar),
                ("gross_observed_bucket_audit.csv.gz", buckets), ("gross_unresolved_events.csv", unresolved),
                ("gross_source_signals_feature_only.csv", source_signals), ("gross_duplicate_source_rows.csv", duplicates),
                ("gross_invalid_source_rows.csv", invalid)):
                if name.endswith(".gz"): csv_gzip_once(OUT / name, frame)
                else: csv_once(OUT / name, frame)
                saved.append(name)
        except Exception as error:
            admission = dict(phase="pre_gross", passed=False, status="SOURCE_FORMAT_OR_IMPLEMENTATION_BLOCKED", stage=stage,
                exception_type=type(error).__name__, exception_message=str(error), raw_returns_calculated=False,
                gross_screen_runs=0, economic_evaluations=0, no_automatic_retry=True,
                reason="Exception BEFORE raw attachment; not a strategy profitability verdict")
            dump_once(OUT / "pre_gross_exception.json", dict(admission, traceback=traceback.format_exc())); saved.append("pre_gross_exception.json")
            grid = None; entries = pd.DataFrame(); native_audit = {}
        # The catcher ends here. Any later error must not falsely claim0returns.
        events, decision, summary = after_admission(grid, entries, admission)
        if binding["hashes"] != {name: sha(ROOT / name) for name in binding["hashes"]}:
            raise ValueError("Bound H05 code/source/input changed during execution.")
        if decision["raw_returns_calculated"]:
            csv_once(OUT / "gross_events.csv", events); csv_once(OUT / "gross_summary.csv", summary)
            saved += ["gross_events.csv", "gross_summary.csv"]
        else:
            dump_once(OUT / "gross_summary_status.json", dict(status="N/A: source/entry/held admission failed; no endpoint arithmetic", raw_returns_calculated=False)); saved.append("gross_summary_status.json")
        gate_name = "gross_gate.json" if decision["raw_returns_calculated"] else "pre_gross_gate.json"
        audit = dict(native=native_audit, source_bucket="LITERALrow*1000+((j-1)%1440)//10inclmidnightpartials;observedstateallhours",
            fixed_state_start=STATE_START, no2017_performance=True, invalid_conflicts_fatal=True,
            missing_ideal_minutes_not_forward_filled_or_unbounded_lineage_veto=True, held_events_must_be_complete=True,
            ATR15_not_calculated_or_used_by_raw_phase=True,
            uniform_entry_calendar="sharednormalweekday/fullholiday/earlycloseguard;indicatorhistoryunchanged",
            raw_window="nativeOPENsignal_j+1throughOPEN891;noSL/TP/net",
            target_stop_future_frozen=(.10, .20), source_parent75ptstop_not_simulated_to_choose_first_signal=True,
            no_BO_no_MC_profit_no2023plus=True, exact_PL_or_MC_parity_claimed=False,
            continuous_contract_roll_and_MNQ_fill_receipt_uncertainty="Disclosed; no retrospective jump exclusion or invented causal-roll fatal requirement",
            raw_returns_calculated=decision["raw_returns_calculated"])
        for name, value in ((gate_name, decision), ("gross_input_binding.json", binding), ("gross_data_audit.json", audit)):
            dump_once(OUT / name, value); saved.append(name)
        marker = dict(started_utc=started, completed_utc=utcnow(), phase=decision["phase"], passed=decision["passed"],
            prereg=prereg, implementation_commit=binding["implementation_commit"], script_sha256=sha(ROOT / SCRIPT),
            artifacts_sha256={name: sha(OUT / name) for name in saved}, raw_returns_calculated=decision["raw_returns_calculated"],
            gross_screen_runs=decision["gross_screen_runs"], economic_evaluations=0, new_hypotheses=1,
            stopped_design_or_accounts_or_validation_run=False, MC_outcomes_read=False, retry_authorized=False)
        marker_name = "gross_verified_execution.json" if decision["raw_returns_calculated"] else "pre_gross_verified_execution.json"
        dump_once(OUT / marker_name, marker)
        return decision


def fixtures():
    checks = []
    assert len(native_paths()) == 12 and not any("2023" in path for path in native_paths())
    assert EXIT_J == jof(1451) and STATE_START == 20170901
    assert allowed_day("2018-01-02") and not allowed_day("2018-12-05") and not allowed_day("2018-11-23")
    checks.append("explicit2017warmup/2018-22DAYON;sharedcalendarentryonly;fixedOPEN1451")
    blank = pd.DataFrame()
    bad = dict(phase="pre_gross", passed=False, raw_returns_calculated=False, gross_screen_runs=0)
    def forbidden(*args): raise AssertionError("Raw endpoint attached after source gate failure.")
    _, unchanged, summary = after_admission(None, blank, bad, attach=forbidden)
    assert unchanged["gross_screen_runs"] == 0 and summary is None
    checks.append("source/ENTRY/heldgatebeforeANYrawreturn;failure0screens/0economicevals")
    events = pd.DataFrame([dict(year=2018, side=1, gross_MNQ=10.), dict(year=2018, side=-1, gross_MNQ=-5.)])
    s = summaries(events)
    assert s[(s.period == "2018-22") & (s.side == "both")].iloc[0].total_MNQ == 5
    assert s[(s.period == "2022") & (s.side == "both")].iloc[0].events == 0
    checks.append("grossmeanSDSEt/totalbybothsidesyear;emptyandsingleeventgroupsretained")
    calendar = pd.DataFrame([dict(whole_expected_normal_RTH_missing=False)])
    audit = dict(conflicting_duplicate_keys=0, invalid_observed_OHLCV_rows=0)
    enough = pd.DataFrame([dict()] * MIN_EVENTS)
    assert admission_gate(enough, calendar, audit, pd.DataFrame())["passed"]
    assert not admission_gate(enough.iloc[:-1], calendar, audit, pd.DataFrame())["passed"]
    assert not admission_gate(enough, calendar, audit, pd.DataFrame([dict(invalid_held_minutes=1)]))["passed"]
    audit["conflicting_duplicate_keys"] = 1
    assert not admission_gate(enough, calendar, audit, pd.DataFrame())["passed"]
    checks.append("invalid/conflictingactualinputsandheldgapsveto;noinfiniteidealminuteveto")
    # End-to-end independent signal -> exact native entry/held/end audit,
    # artificial bars only. No endpoint PnL/old maker/ATR function is called.
    dates = pd.DatetimeIndex(["2017-09-01", "2018-01-02"])
    shape = (2, 1440)
    arrays = {name: np.full(shape, np.nan) for name in ("o", "h", "l", "c", "v")}
    presence = np.zeros(shape, bool)
    for row, js, price in ((0, np.arange(591, 1181), 100.), (1, np.arange(511, EXIT_J + 1), 1000.)):
        for name, value in (("o", price), ("h", price + .25), ("l", price - .25), ("c", price), ("v", 10.)):
            arrays[name][row, js] = value
        presence[row, js] = True
    grid = SimpleNamespace(**arrays, ts=dates.to_numpy(), dates=dates.strftime("%Y%m%d").astype(int).to_numpy(), D=2)
    entries, synthetic_calendar, buckets, missing, source_signals = indicator_entries(grid, presence)
    assert len(entries) == 1 and entries.iloc[0].j == 520 and entries.iloc[0].entry_j == 521 and entries.iloc[0].side == 1
    assert entries.iloc[0].date == "2018-01-02" and entries.iloc[0].entry == 1000 and missing.empty
    assert "ATR15" not in entries.columns and not entries.raw_endpoint_arithmetic_calculated.any()
    assert entries.iloc[0].first_fill_interval_start.startswith("2018-01-02T08:40")
    assert entries.iloc[0].first_fill_interval_end.startswith("2018-01-02T08:41")
    presence[1, 700] = False
    for name in arrays: getattr(grid, name)[1, 700] = np.nan
    retained, _, _, gaps, _ = indicator_entries(grid, presence)
    assert len(retained) == 1 and retained.iloc[0].invalid_held_minutes == 1 and len(gaps) == 1
    grid.o[1, EXIT_J] = np.nan
    retained, _, _, gaps, _ = indicator_entries(grid, presence)
    assert not retained.iloc[0].endpoint_open_valid and len(gaps) == 1
    checks.append("fullsignalhelperintegrationnextnativeOPEN/CTfillclock;heldgap+missingexitretained/nofallback;noATRorPnL")
    return dict(passed=True, checks=checks, actual_native_data_MC_or_cache_rows_read=False,
        gross_stopped_or_account_returns_calculated=False, script_sha256=sha(ROOT / SCRIPT), versions=runtime_versions())


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--phase", required=True, choices=("fixtures", "gross")); parser.add_argument("--prereg")
    args = parser.parse_args()
    if args.phase == "fixtures":
        result = fixtures(); dump_once(OUT / f"synthetic_checks_{result['script_sha256'][:12]}.json", result)
    else:
        if not args.prereg: parser.error("Gross requires committed --prereg.")
        result = gross(args.prereg)
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__": main()
