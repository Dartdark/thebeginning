"""Hunt-v2 H02 FVB SHORT_EXEC: fixed first-signal RAW_NO_STOP gross screen.

Importing this module never reads market data.  The fixtures phase uses synthetic
arrays only.  The gross phase requires an immutable committed preregistration
and implementation, and binds only native 2018--22 day/overnight NQ inputs.

The short-only state is independent of the old BOTH ledger: long signals never
consume time or the later short-only attempt allowance.  This cheap screen has
one first short event/day, no stop, no target, no fees and no re-entry.  It is not
the later stopped strategy and cannot establish net significance/book benefit.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import fcntl
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import warnings

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_hunt_v2_fvb_short"
SCRIPT = "analysis/codex_hunt_v2_fvb_short_gross.py"
PLAN = "agents/codex/plans/hunt_v2_fvb_short_execution.md"
EVIDENCE = "agents/codex/evidence/hunt_v2_fvb_short_execution.md"
SOURCE_REF = "92b1d4c"
SOURCE_PATHS = ("checks/candidates/fvb/spec.md", "analysis/fvb_test.py")
sys.path.insert(0, str(ROOT / "analysis"))

# H01 pure infrastructure only: no H01 paths, guards, strategy or financial run.
from codex_hunt_v2_ldf_delta import (audited_frame, csv_once, dump_once,
    runtime_versions, sha, tstat, utcnow, valid_ohlcv, validate_metadata_keys)
from grid24 import Grid24, jof
from codex_s03_calendar import calendar_status
from replica import is_early_close

YEARS = tuple(range(2018, 2023))
NATIVE_FIELDS = ("open", "high", "low", "close", "volume")
RTH_FIRST_J, RTH_LAST_J = 511, 915
PM_FIRST_J, PM_LAST_J = 181, 510
SIGNAL_FIRST_J, SIGNAL_LAST_J, EXIT_J = 511, 630, 911
ATR_DAYS = 14
MNQ_POINT_VALUE, RT_COMMISSION, FILL_SLIPPAGE = 2.0, 1.24, 0.50
RT_COST = RT_COMMISSION + 2 * FILL_SLIPPAGE
GROSS_HURDLE, MIN_EVENTS = 2 * RT_COST, 100
STRESS_SLIPPAGE_PER_FILL, STRESS_RT_COST = 2.0, 5.24  # Four MNQ ticks/fill; cost-only later diagnostic.
MODEL = "SHORT_EXEC"
EVENT_COLUMNS = (
    "date", "event_id", "year", "model", "side", "signal_j", "entry_label_j", "exit_label_j",
    "level_name", "level_price", "signal_close", "entry_open", "exit_close", "gross_points",
    "gross_mnq", "gross_nq", "invalid_or_missing_held_minutes", "unresolved_held_path",
    "pmh", "pml", "short_levels", "scan_prefix_valid_bars", "scan_prefix_required_bars",
    "event_time", "available_at", "decision_time", "first_executable_fill",
    "premarket_available_at", "prior_rth_available_at", "first_fill_close_label_j",
    "information_clock_assumption", "receipt_or_execution_latency_verified",
    "atr_reference_date_ids", "atr_reference_count", "atr_reference_complete",
    "atr_missing_reference_date_ids", "atr_reference_max_date_id", "prior_rth_date_id",
    "prior_rth_complete", "atr", "pdh", "pdl", "prior_range", "prior_body_ratio")


@dataclass(frozen=True)
class SourceAdapter:
    """Immutable, hypothesis-local inputs for the shared Grid24 builder."""
    output: Path = OUT
    years: tuple[int, ...] = YEARS

    @property
    def paths(self) -> tuple[Path, ...]:
        return tuple(ROOT / f"data/NQ_1min_{suffix}{year}.csv"
                     for year in self.years for suffix in ("", "ON_"))

    def build(self, paths: list[str]) -> tuple[Grid24, dict]:
        if tuple(map(Path, paths)) != self.paths:
            raise ValueError("Native file order/set differs from frozen2018-22 source adapter.")
        native, audit = audited_frame(paths, NATIVE_FIELDS, "native")
        cache = self.output / "cache"
        cache.mkdir(parents=True, exist_ok=True)
        ignore = self.output / ".gitignore"
        if not ignore.exists():
            ignore.write_text("cache/\n*.lock\n")
        for source in self.paths:
            prefix = "night" if "_ON_" in source.name else "day"
            link = cache / f"{prefix}_{source.stem[-4:]}.csv"
            if link.is_symlink():
                if link.resolve() != source.resolve():
                    raise ValueError("Cache link points outside bound source set.")
            elif link.exists():
                raise ValueError("Unexpected non-symlink cache input.")
            else:
                link.symlink_to(source)
        expected = {f"{prefix}_{year}.csv" for prefix in ("day", "night") for year in self.years}
        observed = {p.name for p in cache.glob("*.csv")}
        if observed != expected:
            raise ValueError("Unbound year/source in isolated cache; refuse shared-grid loading.")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            grid = Grid24(str(cache / "day_*.csv"), str(cache / "night_*.csv"))
        grid_years = pd.DatetimeIndex(grid.ts).year
        if grid_years.min() < min(self.years) or grid_years.max() > max(self.years):
            raise ValueError("Shared grid crossed the frozen design years.")
        rows = np.searchsorted(grid.dates, native.date.to_numpy())
        cols = jof(native.time.to_numpy())
        for field, attr in (("open", "o"), ("high", "h"), ("low", "l"), ("close", "c"), ("volume", "v")):
            if not np.allclose(getattr(grid, attr)[rows, cols], native[field].to_numpy(), equal_nan=True):
                raise ValueError("Shared grid differs from duplicate-audited native " + field)
        return grid, audit


def committed_bytes(ref: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=ROOT)


def normal_session(date) -> bool:
    """Known calendar eligibility, independent of current or future prices."""
    d = pd.Timestamp(date)
    return calendar_status(d)["kind"] == "normal" and not is_early_close(d)


def quarterly_roll_date(date) -> pd.Timestamp:
    """Calendar second Thursday; this is not a measured vendor-switch date."""
    d = pd.Timestamp(date)
    first = pd.Timestamp(year=d.year, month=d.month, day=1)
    return first + pd.Timedelta(days=(3 - first.weekday()) % 7 + 7)


def roll_guard(date) -> bool:
    """Conservative calendar assumption, not official vendor-roll evidence."""
    d = pd.Timestamp(date).normalize()
    return d.month in (3, 6, 9, 12) and d in {
        quarterly_roll_date(d) + pd.Timedelta(days=n) for n in (0, 1, 4, 5)}


def short_levels(pdh: float, pdl: float, pmh: float, pml: float) -> list[tuple[str, float]]:
    if pdh < pml or pdl > pmh:
        return [("pm_low", pml)]
    name = "structural_pdl" if pml < pdl < pmh else "pdl_break"
    result = [(name, pdl)]
    if pml != pdl:
        result.append(("pm_low", pml))
    return result


def first_short_signal(close: np.ndarray, valid: np.ndarray,
                       levels: list[tuple[str, float]]) -> dict:
    """Only the already completed scan prefix is inspected for eligibility.

    An invalid scan minute ends this day's search.  It cannot be skipped to
    discover a later favorable signal; the unavailable search remains audited.
    After a valid trigger, later missing scan minutes belong to its held path.
    """
    for j in range(SIGNAL_FIRST_J, SIGNAL_LAST_J + 1):
        if not valid[j]:
            return dict(found=False, incomplete_scan_prefix=True, invalid_scan_j=j,
                        scan_prefix_last_inspected_j=j,
                        scan_prefix_valid_bars=j - SIGNAL_FIRST_J,
                        scan_prefix_required_bars=SIGNAL_LAST_J - SIGNAL_FIRST_J + 1)
        for name, level in levels:
            if close[j] < level:
                return dict(found=True, incomplete_scan_prefix=False, signal_j=j,
                            level_name=name, level_price=float(level), signal_close=float(close[j]),
                            scan_prefix_last_inspected_j=j, scan_prefix_valid_bars=j - SIGNAL_FIRST_J + 1,
                            scan_prefix_required_bars=j - SIGNAL_FIRST_J + 1)
    return dict(found=False, incomplete_scan_prefix=False, scan_prefix_last_inspected_j=SIGNAL_LAST_J,
                scan_prefix_valid_bars=SIGNAL_LAST_J - SIGNAL_FIRST_J + 1,
                scan_prefix_required_bars=SIGNAL_LAST_J - SIGNAL_FIRST_J + 1)


def clock_state(date, signal_j: int, prior_date_id: int) -> dict:
    """The exact close/open boundary is idealized, never a verified receipt."""
    decision = (pd.Timestamp(date).normalize() + pd.Timedelta(minutes=signal_j)).tz_localize("America/Chicago")
    pm_available = (pd.Timestamp(date).normalize() + pd.Timedelta(minutes=PM_LAST_J)).tz_localize("America/Chicago")
    prior_available = (pd.Timestamp(str(prior_date_id)) + pd.Timedelta(minutes=RTH_LAST_J)).tz_localize("America/Chicago")
    if not (prior_available < pm_available <= decision):
        raise ValueError("Noncausal feature information clock.")
    return dict(event_time=decision.isoformat(), available_at=decision.isoformat(),
        decision_time=decision.isoformat(), first_executable_fill=decision.isoformat(),
        premarket_available_at=pm_available.isoformat(), prior_rth_available_at=prior_available.isoformat(),
        first_fill_close_label_j=signal_j + 1,
        information_clock_assumption="zero receipt/processing delay; next-native-bar open shares signal-close wall boundary",
        receipt_or_execution_latency_verified=False)


def prior_references(grid, valid: np.ndarray) -> tuple[list[dict], list[dict]]:
    """Exact prior14 normal calendar slots; incomplete slots are not replaced.

    Feature values for today use only dates strictly before today.  No current
    RTH completeness or g.trading/last_j state may determine eligibility.
    """
    dates = pd.DatetimeIndex(grid.ts)
    reference_calendar = pd.date_range(f"{min(YEARS)}-01-01", dates[-1], freq="D")
    expected = [d for d in reference_calendar if normal_session(d)]
    by_date = {pd.Timestamp(d).normalize(): i for i, d in enumerate(dates)}
    completed, session_audit = {}, []
    for date in expected:
        row = by_date.get(date)
        complete = row is not None and bool(valid[row, RTH_FIRST_J:RTH_LAST_J + 1].all())
        if complete:
            h = float(grid.h[row, RTH_FIRST_J:RTH_LAST_J + 1].max())
            l = float(grid.l[row, RTH_FIRST_J:RTH_LAST_J + 1].min())
            o, c = float(grid.o[row, RTH_FIRST_J]), float(grid.c[row, RTH_LAST_J])
            rng = h - l
            completed[date] = dict(high=h, low=l, open=o, close=c, range=rng,
                                   body_ratio=abs(c - o) / rng if rng > 0 else np.nan)
        session_audit.append(dict(date=date.date().isoformat(), date_id=int(date.strftime("%Y%m%d")),
            complete_rth=complete, expected_rth_bars=RTH_LAST_J - RTH_FIRST_J + 1,
            valid_rth_bars=int(valid[row, RTH_FIRST_J:RTH_LAST_J + 1].sum()) if row is not None else 0,
            grid_row_present=row is not None, **completed.get(date, {})))
    reference_rows = []
    for date in dates:
        previous = [d for d in expected if d < date]
        references = previous[-ATR_DAYS:]
        complete = len(references) == ATR_DAYS and all(d in completed for d in references)
        prior = completed.get(previous[-1], {}) if previous else {}
        ranges = [completed[d]["range"] for d in references] if complete else []
        value = float(np.mean(ranges)) if ranges else np.nan
        reference_rows.append(dict(
            atr_reference_date_ids=json.dumps([int(d.strftime("%Y%m%d")) for d in references], separators=(",", ":")),
            atr_reference_count=len(references), atr_reference_complete=bool(complete),
            atr_missing_reference_date_ids=json.dumps([int(d.strftime("%Y%m%d")) for d in references if d not in completed], separators=(",", ":")),
            atr_reference_max_date_id=int(references[-1].strftime("%Y%m%d")) if references else None,
            prior_rth_date_id=int(previous[-1].strftime("%Y%m%d")) if previous else None,
            prior_rth_complete=bool(prior), atr=value,
            pdh=prior.get("high", np.nan), pdl=prior.get("low", np.nan),
            prior_range=prior.get("range", np.nan), prior_body_ratio=prior.get("body_ratio", np.nan)))
        if references and not references[-1] < date:
            raise AssertionError("Nonpast prior reference.")
    return reference_rows, session_audit


def collect_events(grid) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    valid = valid_ohlcv(grid.o, grid.h, grid.l, grid.c, grid.v)
    refs, sessions = prior_references(grid, valid)
    records, calendars, reasons = [], [], {}
    for row, ts in enumerate(pd.DatetimeIndex(grid.ts)):
        state = refs[row]
        status = calendar_status(ts)
        audit = dict(date=ts.date().isoformat(), year=ts.year, calendar_kind=status["kind"],
            calendar_reason=status["reason"], cash_close_j=status["cash_close_j"],
            known_early_skip=bool(is_early_close(ts)), known_roll_skip=roll_guard(ts),
            pm_expected_bars=PM_LAST_J - PM_FIRST_J + 1,
            pm_valid_bars=int(valid[row, PM_FIRST_J:PM_LAST_J + 1].sum()), **state)
        prior_roll_skip = bool(state["prior_rth_date_id"] is not None
                               and roll_guard(pd.Timestamp(str(state["prior_rth_date_id"]))))
        audit["prior_reference_roll_skip"] = prior_roll_skip
        audit["unresolved_causal_scan"] = False
        reason = None
        if not normal_session(ts):
            reason = "known_calendar_skip"
        elif roll_guard(ts) or prior_roll_skip:
            reason = "known_calendar_roll_guard"
        elif not state["atr_reference_complete"]:
            reason = "prior14_normal_calendar_slots_warmup_or_incomplete"
        elif not np.isfinite(state["atr"]) or state["atr"] <= 0:
            reason = "nonpositive_or_invalid_prior14_rth_mean_range"
        elif not valid[row, PM_FIRST_J:PM_LAST_J + 1].all():
            reason = "incomplete_or_invalid_known_premarket_window"
        else:
            pmh = float(grid.h[row, PM_FIRST_J:PM_LAST_J + 1].max())
            pml = float(grid.l[row, PM_FIRST_J:PM_LAST_J + 1].min())
            audit.update(pmh=pmh, pml=pml, pm_range=pmh - pml)
            if not pmh > pml:
                reason = "premarket_high_not_above_low"
            elif state["prior_range"] > 1.5 * state["atr"]:
                reason = "prior_range_above_1p5_atr"
            elif pmh - pml > state["atr"]:
                reason = "premarket_range_above_1p0_atr"
            elif not np.isfinite(state["prior_body_ratio"]) or state["prior_body_ratio"] >= 0.6:
                reason = "prior_body_ratio_at_least_0p6_or_unavailable"
            else:
                levels = short_levels(state["pdh"], state["pdl"], pmh, pml)
                audit["short_levels"] = json.dumps(levels, separators=(",", ":"))
                signal = first_short_signal(grid.c[row], valid[row], levels)
                audit.update(signal)
                if signal["incomplete_scan_prefix"]:
                    reason = "incomplete_or_invalid_causal_scan_prefix"
                    audit["unresolved_causal_scan"] = True
                elif not signal["found"]:
                    reason = "no_short_signal_in_frozen_window"
                else:
                    signal_j = signal["signal_j"]
                    entry_j = signal_j + 1
                    entry, exit_price = grid.o[row, entry_j], grid.c[row, EXIT_J]
                    # RAW native open/close: do not stop, tick-round or subtract costs.
                    points = entry - exit_price if np.isfinite(entry) and np.isfinite(exit_price) else np.nan
                    held_valid = valid[row, entry_j:EXIT_J + 1]
                    records.append(dict(date=ts.date().isoformat(), event_id=f"FVB_SHORT_GROSS_{ts.strftime('%Y%m%d')}_01",
                        year=ts.year, model=MODEL,
                        side=-1, signal_j=signal_j, entry_label_j=entry_j, exit_label_j=EXIT_J,
                        level_name=signal["level_name"], level_price=signal["level_price"],
                        signal_close=signal["signal_close"], entry_open=float(entry), exit_close=float(exit_price),
                        gross_points=float(points), gross_mnq=float(points * MNQ_POINT_VALUE),
                        gross_nq=float(points * 20), invalid_or_missing_held_minutes=int((~held_valid).sum()),
                        unresolved_held_path=not bool(held_valid.all()), pmh=pmh, pml=pml,
                        short_levels=json.dumps(levels, separators=(",", ":")),
                        scan_prefix_valid_bars=signal["scan_prefix_valid_bars"],
                        scan_prefix_required_bars=signal["scan_prefix_required_bars"],
                        **clock_state(ts, signal_j, state["prior_rth_date_id"]), **state))
                    reason = "first_short_event_retained"
        audit["disposition"] = reason
        reasons[reason] = reasons.get(reason, 0) + 1
        calendars.append(audit)
    return pd.DataFrame(records, columns=EVENT_COLUMNS), pd.DataFrame(calendars), pd.DataFrame(sessions), reasons


def summarize_events(events: pd.DataFrame) -> pd.DataFrame:
    result = []
    for period in ("2018-22", *map(str, YEARS)):
        period_mask = np.ones(len(events), bool) if period == "2018-22" else events.year.eq(int(period)).to_numpy()
        for side, side_mask in (("all", np.ones(len(events), bool)), ("long", events.side.eq(1).to_numpy()), ("short", events.side.eq(-1).to_numpy())):
            rows = events[period_mask & side_mask]
            finite = rows.gross_mnq.to_numpy(float)
            finite = finite[np.isfinite(finite)]
            result.append(dict(model=MODEL, period=period, side=side, events=len(rows),
                observed_endpoint_returns=len(finite), unresolved_held_events=int(rows.unresolved_held_path.sum()),
                gross_observed_total_mnq=float(finite.sum()), gross_mean_mnq=float(finite.mean()) if len(finite) else None,
                gross_t=tstat(finite),
                gross_sd_mnq=float(finite.std(ddof=1)) if len(finite) > 1 else None,
                gross_stderr_mnq=float(finite.std(ddof=1) / np.sqrt(len(finite))) if len(finite) > 1 else None,
                gross_observed_total_nq=float(finite.sum() * 10),
                cost_hurdle_mnq=GROSS_HURDLE, costs_subtracted=False, stops_simulated=False))
    return pd.DataFrame(result)


def gross_decision(events: pd.DataFrame, calendar: pd.DataFrame) -> dict:
    """The frozen cheap-screen conjunction, including zero-event retention."""
    observed = events.gross_mnq.to_numpy(dtype=float)
    observed = observed[np.isfinite(observed)]
    mean = float(observed.mean()) if len(observed) else None
    complete_endpoint = len(observed) == len(events)
    complete_held = not bool(events.unresolved_held_path.any())
    complete_scan = not bool(calendar.unresolved_causal_scan.any())
    economic_pass = bool(mean is not None and mean >= GROSS_HURDLE and len(events) >= MIN_EVENTS)
    return dict(primary_model=MODEL, gross_kind="FIRST_SHORT_RAW_NO_STOP", gross_hurdle_mnq=GROSS_HURDLE,
        native_roundtrip_cost_mnq=RT_COST, min_events=MIN_EVENTS, events=len(events),
        observed_endpoint_returns=len(observed), primary_gross_mean_mnq=mean, primary_gross_t=tstat(observed),
        economic_pass=economic_pass, all_endpoints_observed=complete_endpoint,
        all_held_paths_complete=complete_held, unresolved_held_events=int(events.unresolved_held_path.sum()),
        all_eligible_causal_scans_resolved=complete_scan,
        unresolved_causal_scan_days=int(calendar.unresolved_causal_scan.sum()),
        passed=economic_pass and complete_endpoint and complete_held and complete_scan,
        counted_evaluations_this_screen=0, gross_hypotheses_this_screen=1,
        validation_run=False, account_tests_run=False, costs_subtracted=False, stops_simulated=False,
        unresolved_events_retained_and_veto_pass=True, downstream_requires_marker_and_all_hashes=True,
        decisions="Proceed only if passed; otherwise close H02 before stopped design/validation/book benches.")


def verify_before_prices(prereg: str) -> dict:
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    if branch != "codex/work":
        raise ValueError("Wrong execution branch: " + branch)
    for name in (PLAN, EVIDENCE):
        if committed_bytes(prereg, name) != (ROOT / name).read_bytes():
            raise ValueError("Preregistration/evidence differs from committed source: " + name)
    implementation_dependencies = [SCRIPT, "analysis/codex_hunt_v2_ldf_delta.py", "analysis/grid24.py",
                    "analysis/codex_s03_calendar.py", "analysis/replica.py", "agents/codex/RESEARCH_CONTROLS.md"]
    dependencies = implementation_dependencies + [PLAN, EVIDENCE]
    for name in implementation_dependencies:
        if committed_bytes("HEAD", name) != (ROOT / name).read_bytes():
            raise ValueError("Freeze implementation/dependencies in HEAD before opening returns: " + name)
    for directory in (ROOT / "analysis/outputs").glob("codex_hunt_v2_fvb_short*"):
        if (directory / "gross_verified_execution.json").exists():
            raise ValueError("H02 gross already completed; no financial rerun in alternate retry directories.")
    adapter = SourceAdapter()
    if any(not p.exists() for p in adapter.paths):
        raise FileNotFoundError("Registered native2018-22 NQ day/overnight source missing.")
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in adapter.paths}
    hashes.update({name: sha(ROOT / name) for name in dependencies})
    import hashlib
    source_spec_hashes = {name: hashlib.sha256(committed_bytes(SOURCE_REF, name)).hexdigest() for name in SOURCE_PATHS}
    metadata = []
    for path in adapter.paths:
        keys = pd.read_csv(path, usecols=["date", "time"])
        validate_metadata_keys(keys, int(path.stem[-4:]), path.name)
        metadata.append(dict(path=str(path.relative_to(ROOT)), rows=len(keys),
            min_date=int(keys.date.min()), max_date=int(keys.date.max()),
            duplicate_metadata_keys=int(keys.duplicated(["date", "time"]).sum())))
    return dict(prereg=prereg, implementation_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        hashes=hashes, metadata=metadata, native_paths=list(map(str, adapter.paths)), source_ref=SOURCE_REF,
        source_spec_hashes=source_spec_hashes, runtime_versions=runtime_versions())


@contextmanager
def execution_lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "gross.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def gross(prereg: str) -> dict:
    with execution_lock():
        binding = verify_before_prices(prereg)
        started = utcnow()
        with (OUT / "attempts.jsonl").open("a") as log:
            log.write(json.dumps(dict(started_utc=started, phase="gross", prereg=prereg, script_sha256=sha(ROOT / SCRIPT))) + "\n")
        grid, native_audit = SourceAdapter().build(binding["native_paths"])
        events, calendar, sessions, reasons = collect_events(grid)
        summary = summarize_events(events)
        observed = events.gross_mnq.to_numpy(dtype=float)
        observed = observed[np.isfinite(observed)]
        mean = float(observed.mean()) if len(observed) else None
        gate = gross_decision(events, calendar)
        passed = gate["passed"]
        if binding["hashes"] != {name: sha(ROOT / name) for name in binding["hashes"]}:
            raise ValueError("Bound source changed during run; no successful artifact can be issued.")
        csv_once(OUT / "gross_events.csv", events)
        csv_once(OUT / "gross_summary.csv", summary)
        csv_once(OUT / "gross_calendar_audit.csv", calendar)
        csv_once(OUT / "gross_prior_session_audit.csv", sessions)
        dump_once(OUT / "gross_input_binding.json", binding)
        manifest = dict(candidate_id="hunt_v2_H02_FVB_SHORT_EXEC", family_id="existing_posthoc_FVB_short_confirmation",
            phase="2018-22 cheap raw gross screen; no stopped economic evaluation", preregistration_commit=prereg,
            code_sha256=sha(ROOT / SCRIPT), implementation_commit=binding["implementation_commit"],
            source_hashes=binding["hashes"], source_definition_ref=binding["source_ref"],
            source_definition_hashes=binding["source_spec_hashes"], input_schema_eras="native continuous NQ date/time CT close-stamped CSV; no era harmonization",
            data_start="2018-01-01", data_end="2022-12-31", no2017_warmup=True, no2023_returns=True,
            first_short_events=len(events), observed_endpoints=len(observed), calendar_dispositions=reasons,
            unresolved_held_events=int(events.unresolved_held_path.sum()), unresolved_causal_scans=int(calendar.unresolved_causal_scan.sum()),
            random_seed=None, randomization_used=False, versions=runtime_versions(),
            native_contract="MNQ assumed costs; signals and raw prices from native NQ exports",
            point_value_mnq=MNQ_POINT_VALUE, commission_per_roundtrip_mnq=RT_COMMISSION,
            slippage_per_fill_mnq=FILL_SLIPPAGE, gross_hurdle_mnq=GROSS_HURDLE,
            later_cost_only_stress_slippage_per_fill_mnq=STRESS_SLIPPAGE_PER_FILL,
            later_cost_only_stress_roundtrip_mnq=STRESS_RT_COST,
            information_clock=dict(event_time="signal native close", available_at="signal close under zero receipt delay assumption",
                decision_time="same signal close", first_executable_fill="next native bar open at same wall boundary; idealized zero processing latency",
                feature_available_before_decision=True, live_receipt_latency_verified=False),
            label_maturity="not applicable: unchanged fixed rule, no learned model or fitted preprocessing",
            baseline_ladder="raw first-short window first; later frozen stopped SHORT_EXEC vs independently causal BOTH reference; no ML",
            report_paths=[str((OUT / name).relative_to(ROOT)) for name in ("gross_events.csv", "gross_summary.csv", "gross_calendar_audit.csv", "gross_prior_session_audit.csv")])
        dump_once(OUT / "gross_run_manifest.json", manifest)
        cost_bridge = dict(gross_mean_per_event_mnq=mean, fees_subtracted_in_screen=0.0,
            assumed_later_commission_per_roundtrip_mnq=RT_COMMISSION,
            assumed_later_entry_slippage_mnq=FILL_SLIPPAGE, assumed_later_exit_slippage_mnq=FILL_SLIPPAGE,
            assumed_later_native_roundtrip_cost_mnq=RT_COST,
            raw_window_breakeven_extra_cost_per_event_mnq=mean - RT_COST if mean is not None else None,
            bridge_is_cost_arithmetic_not_stopped_strategy_net_performance=True,
            latency="idealized zero receipt/processing delay; actual next-open executability unverified",
            spread="repository one-tick slippage per market/stop fill includes spread allowance; no second spread charge",
            frozen_later_execution_stress="four ticks per fill,5.24RT MNQ; same stopped rule cost-only monotonic diagnostic, not selectable",
            stress_slippage_per_fill_mnq=STRESS_SLIPPAGE_PER_FILL, stress_roundtrip_cost_mnq=STRESS_RT_COST,
            stress_returns_calculated=False)
        dump_once(OUT / "gross_cost_bridge.json", cost_bridge)
        dump_once(OUT / "gross_gate.json", gate)
        audit = dict(native=native_audit, calendar_reasons=reasons, no2017_warmup=True, no2023_or_later_files=True,
            no_g_trading_or_last_j_eligibility=True, prior_reference_policy="exact prior14 normal calendar slots; incomplete slot veto",
            prior_rth_labels_ct="08:31..15:15 inclusive405minutes", premarket_labels_ct="03:01..08:30 inclusive330minutes",
            atr_basis="mean of previous14 complete expected RTH RANGES, never true range",
            signal_labels_ct="08:31..10:30 inclusive; first close strictly below ordered short level",
            raw_entry="exact signal_j+1 native open, no rounding", raw_exit="15:11 native close, no fallback",
            stops_or_targets_simulated=False, current_full_session_coverage_never_controls_entry=True,
            incomplete_scan_prefix_stops_search=True, invalid_held_paths_retained_and_veto_pass=True,
            native_micro_prices_verified=False, costs_are_repository_MNQ_assumptions=True,
            old_both_ledger_short_subset_reused=False, actual_spread_receipt_and_vendor_roll_fidelity_verified=False,
            roll_guard="conservative secondThursday quarter-month offsets0,1,4,5 on today OR immediate prior-reference date; not official vendor-roll proof",
            atr_may_include_roll_guard_slot_intraday_ranges=True,
            incomplete_eligible_causal_scans_veto_pass=True)
        dump_once(OUT / "gross_data_audit.json", audit)
        artifact_names = ["gross_events.csv", "gross_summary.csv", "gross_calendar_audit.csv",
            "gross_prior_session_audit.csv", "gross_input_binding.json", "gross_run_manifest.json",
            "gross_cost_bridge.json", "gross_gate.json", "gross_data_audit.json"]
        marker = dict(started_utc=started, completed_utc=utcnow(), phase="gross", passed=passed, prereg=prereg,
            implementation_commit=binding["implementation_commit"], script_sha256=sha(ROOT / SCRIPT),
            artifacts_sha256={name: sha(OUT / name) for name in artifact_names}, counted_evaluations=0,
            new_hypotheses=1, strategy_execution_run=False, raw_window_returns_calculated=True,
            runtime_versions=runtime_versions(), validation_run=False, account_tests_run=False,
            downstream_requirement="Require this verified marker AND every artifact hash; gross_gate alone is insufficient.")
        dump_once(OUT / "gross_verified_execution.json", marker)
        with (OUT / "attempts.jsonl").open("a") as log:
            log.write(json.dumps(dict(completed_utc=marker["completed_utc"], phase="gross", completed=True, passed=passed)) + "\n")
        return gate


def synthetic_checks() -> dict:
    assert (RTH_LAST_J - RTH_FIRST_J + 1, PM_LAST_J - PM_FIRST_J + 1, SIGNAL_LAST_J - SIGNAL_FIRST_J + 1) == (405, 330, 120)
    assert (int(jof(831)), int(jof(1030)), int(jof(1511))) == (511, 630, 911)
    assert RT_COST == 2.24 and abs(GROSS_HURDLE - 4.48) < 1e-12
    assert RT_COMMISSION + 2 * STRESS_SLIPPAGE_PER_FILL == STRESS_RT_COST
    assert short_levels(110, 100, 115, 95) == [("structural_pdl", 100), ("pm_low", 95)]
    assert short_levels(110, 100, 108, 100) == [("pdl_break", 100)]
    assert short_levels(110, 100, 120, 115) == [("pm_low", 115)]
    assert short_levels(110, 100, 95, 90) == [("pm_low", 90)]
    c, valid = np.full(1440, 110.), np.ones(1440, bool)
    c[511], c[512] = 105., 94.
    signal = first_short_signal(c, valid, short_levels(110, 100, 115, 95))
    assert signal["signal_j"] == 512 and signal["level_name"] == "structural_pdl"
    # No long-signal consumption and no crossing-from-above requirement.
    c[511] = 99.
    assert first_short_signal(c, valid, [("pdl", 100.)])["signal_j"] == 511
    c[511] = 100.
    assert first_short_signal(c, valid, [("pdl", 100.)])["signal_j"] == 512
    valid[511] = False
    assert first_short_signal(c, valid, [("pdl", 100.)])["incomplete_scan_prefix"]
    valid[511] = True
    c[:] = 110.
    c[630] = 99.
    assert first_short_signal(c, valid, [("pdl", 100.)])["signal_j"] == 630
    c[630], c[631] = 110., 99.
    assert not first_short_signal(c, valid, [("pdl", 100.)])["found"]
    # Exact expected calendar slots and strictly prior RTH range mean.
    dates = pd.date_range("2018-01-01", "2018-02-15", freq="D")
    shape = (len(dates), 1440)
    fake = SimpleNamespace(ts=dates.to_numpy(), dates=dates.strftime("%Y%m%d").astype(int).to_numpy(), D=len(dates))
    for attr, value in (("o", 100.), ("h", 105.), ("l", 95.), ("c", 100.), ("v", 10.)):
        setattr(fake, attr, np.full(shape, value))
    good = valid_ohlcv(fake.o, fake.h, fake.l, fake.c, fake.v)
    refs, _ = prior_references(fake, good)
    assert refs[-1]["atr_reference_complete"] and refs[-1]["atr"] == 10.
    ids = json.loads(refs[-1]["atr_reference_date_ids"])
    assert len(ids) == 14 and ids[-1] < int(fake.dates[-1])
    # A missing exact prior calendar session is vetoed, never replaced by older.
    missed = np.where(fake.dates == ids[-2])[0][0]
    good[missed, 700] = False
    changed, _ = prior_references(fake, good)
    assert changed[-1]["atr_reference_date_ids"] == refs[-1]["atr_reference_date_ids"]
    assert not changed[-1]["atr_reference_complete"] and str(ids[-2]) in changed[-1]["atr_missing_reference_date_ids"]
    # Future/current changes cannot alter today's references.
    fake.h[-1, :] = 100000.
    future_changed, _ = prior_references(fake, good)
    assert changed[-1]["atr_reference_date_ids"] == future_changed[-1]["atr_reference_date_ids"]
    assert changed[-1]["atr_missing_reference_date_ids"] == future_changed[-1]["atr_missing_reference_date_ids"]
    assert not future_changed[-1]["atr_reference_complete"]
    # A late current RTH gap cannot suppress an earlier valid trigger.  The
    # fixed exit/path audit, rather than full-session membership, decides gaps.
    fake.h[-1, :] = 105.
    fake.c[-1, SIGNAL_FIRST_J] = 94.
    fake.l[-1, SIGNAL_FIRST_J] = 94.
    fake.c[-1, RTH_LAST_J] = np.nan  # After911, outside the held raw window.
    events, audit, _, _ = collect_events(fake)
    final = events[events.date.eq(dates[-1].date().isoformat())]
    assert len(final) == 1 and not bool(final.iloc[0].unresolved_held_path)
    assert final.iloc[0].entry_label_j == SIGNAL_FIRST_J + 1
    assert final.iloc[0].event_time == final.iloc[0].available_at == final.iloc[0].decision_time == final.iloc[0].first_executable_fill
    assert pd.Timestamp(final.iloc[0].premarket_available_at) <= pd.Timestamp(final.iloc[0].decision_time)
    fake.c[-1, 900] = np.nan
    events, _, _, _ = collect_events(fake)
    final = events[events.date.eq(dates[-1].date().isoformat())]
    assert len(final) == 1 and bool(final.iloc[0].unresolved_held_path)
    assert final.iloc[0].invalid_or_missing_held_minutes == 1
    fake.c[-1, EXIT_J] = np.nan
    events, _, _, _ = collect_events(fake)
    final = events[events.date.eq(dates[-1].date().isoformat())]
    assert len(final) == 1 and np.isnan(final.iloc[0].gross_mnq)
    # A missing prefix before a hypothetical later trigger remains unresolved;
    # it is never silently skipped into the observed later signal.
    fake.c[-1, SIGNAL_FIRST_J] = np.nan
    events, audit, _, _ = collect_events(fake)
    assert not events.date.eq(dates[-1].date().isoformat()).any()
    assert bool(audit.iloc[-1].unresolved_causal_scan)
    assert audit.iloc[-1].disposition == "incomplete_or_invalid_causal_scan_prefix"
    empty_gate = gross_decision(events, audit)
    assert empty_gate["events"] == 0 and not empty_gate["passed"]
    assert len(summarize_events(events)) == 18
    # Native entry absence is retained; incomplete PM cannot produce a signal.
    fake.c[-1, SIGNAL_FIRST_J] = 94.
    fake.o[-1, SIGNAL_FIRST_J + 1] = np.nan
    events, _, _, _ = collect_events(fake)
    assert len(events) == 1 and bool(events.iloc[0].unresolved_held_path) and np.isnan(events.iloc[0].gross_mnq)
    fake.c[-1, PM_FIRST_J] = np.nan
    events, audit, _, _ = collect_events(fake)
    assert events.empty and audit.iloc[-1].disposition == "incomplete_or_invalid_known_premarket_window"
    # Primary mean/minimum sample alone cannot overrule any unresolved source.
    toy = pd.DataFrame({"gross_mnq": np.full(100, 5.), "unresolved_held_path": np.zeros(100, bool)})
    resolved = pd.DataFrame({"unresolved_causal_scan": [False]})
    assert gross_decision(toy, resolved)["passed"]
    assert not gross_decision(toy.iloc[:99], resolved)["passed"]
    assert not gross_decision(toy, pd.DataFrame({"unresolved_causal_scan": [True]}))["passed"]
    toy.loc[0, "unresolved_held_path"] = True
    assert not gross_decision(toy, resolved)["passed"]
    toy.loc[0, "unresolved_held_path"], toy.loc[0, "gross_mnq"] = False, np.nan
    assert not gross_decision(toy, resolved)["passed"]
    assert not normal_session("2018-12-05") and not normal_session("2023-07-03")
    assert roll_guard("2022-03-10") and roll_guard("2022-03-15") and not roll_guard("2022-03-16")
    validate_metadata_keys(pd.DataFrame({"date": [20200229], "time": [1511]}), 2020, "leap synthetic")
    for date, clock in ((20180230, 1511), (20180102, 1260), (20180102.5, 1511)):
        try:
            validate_metadata_keys(pd.DataFrame({"date": [date], "time": [clock]}), 2018, "invalid synthetic")
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid synthetic metadata was accepted.")
    return dict(passed=True, prices_or_strategy_returns_read=False, runtime_versions=runtime_versions(),
        checks=["close-label clocks405/330/120", "native MNQ gross hurdle", "gap/ordered/deduplicated short levels",
                "strict below not crossing; ignores long signals", "inclusive final scan; no next-observed gaps",
                "causal scan-prefix failure", "exact prior14 complete calendar slots and missing-slot veto",
                "current/future RTH cannot alter prior references", "calendar skip and calendar roll guard",
                "real date/integer/clock metadata integrity", "later RTH gap never suppresses earlier trigger",
                "held/end-point gaps retained; no next-observed/fallback", "idealized clock field causality",
                "missing eligible prefix retained unresolved", "frozen four-tick per fill later cost-only stress",
                "zero-event schema/audits/failed gate", "missing native entry retained and PM completeness",
                "gross min-sample/endpoint/held/scan conjunction"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=("fixtures", "gross"))
    parser.add_argument("--prereg")
    args = parser.parse_args()
    if args.phase == "fixtures":
        result = synthetic_checks()
        result["script_sha256"] = sha(ROOT / SCRIPT)
        target = OUT / f"synthetic_checks_{result['script_sha256'][:12]}.json"
        dump_once(target, result)
    else:
        if not args.prereg:
            parser.error("Gross requires committed --prereg.")
        result = gross(args.prereg)
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__":
    main()
