"""Hunt-v2 H01: frozen raw-window gross screen for LDF delta confirmation.

This module does not load prices when imported.  Gross returns are opened only
after committed plan/evidence/source verification.  Gross is a fixed 14:00
decision -> next-native-minute open -> 14:30 close move, with NO stop or fees.
It is not the later executable LDF design (which retains the 0.25 ATR stop).
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import warnings

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_hunt_v2_ldf_delta"
PLAN = "agents/codex/plans/hunt_v2_ldf_delta_confirmation.md"
EVIDENCE = "agents/codex/evidence/hunt_v2_ldf_delta_confirmation.md"
SCRIPT = "analysis/codex_hunt_v2_ldf_delta.py"
sys.path.insert(0, str(ROOT / "analysis"))
from grid24 import Grid24, jof
from codex_s03_calendar import calendar_status
from replica import is_early_close

YEARS = tuple(range(2018, 2023))
OPEN_J, SIGNAL_J, ENTRY_J, EXIT_J = 511, 840, 841, 870
FLOW_FIRST_J = 811
ATR_DAYS, MIN_MOVE_ATR = 15, 0.40
MNQ_POINT_VALUE, RT_COMMISSION, FILL_SLIPPAGE = 2.0, 1.24, 0.50
RT_COST = RT_COMMISSION + 2 * FILL_SLIPPAGE
GROSS_HURDLE = 2 * RT_COST
MIN_KEPT = 100
MODELS = ("BASE", "LEGACY", "STRICT30")
NATIVE_FIELDS = ("open", "high", "low", "close", "volume")
OF_FIELDS = ("open", "high", "low", "close", "volume", "upvol", "downvol")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_once(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError("Retained artifact must not be overwritten: " + str(path))
    with path.open("xb") as handle:
        handle.write(data)


def dump_once(path: Path, value: dict) -> None:
    write_once(path, (json.dumps(value, indent=2, allow_nan=False) + "\n").encode())


def csv_once(path: Path, frame: pd.DataFrame) -> None:
    write_once(path, frame.to_csv(index=False, float_format="%.12g").encode())


def tstat(values) -> float | None:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) < 2 or values.std(ddof=1) <= 0:
        return None
    return float(values.mean() / values.std(ddof=1) * np.sqrt(len(values)))


def valid_ohlcv(o, h, l, c, v) -> np.ndarray:
    arrays = [np.asarray(x, dtype=float) for x in (o, h, l, c, v)]
    o, h, l, c, v = arrays
    finite = np.logical_and.reduce([np.isfinite(x) for x in arrays])
    return (finite & (o > 0) & (h > 0) & (l > 0) & (c > 0) & (v >= 0)
            & (l <= np.minimum(o, c)) & (h >= np.maximum(o, c)) & (h >= l))


def filter_states(native, source) -> dict:
    """One causal 30-minute input window; no future rows or return targets."""
    native_ok = valid_ohlcv(*(native[name] for name in NATIVE_FIELDS))
    source_ok = valid_ohlcv(*(source[name] for name in NATIVE_FIELDS))
    buy, sell = np.asarray(source["upvol"], float), np.asarray(source["downvol"], float)
    total = buy + sell
    quantities = np.isfinite(buy) & np.isfinite(sell) & (buy >= 0) & (sell >= 0) & (total > 0)
    close_match = np.abs(np.asarray(source["close"]) - native["close"]) <= 0.25
    volume_match = np.asarray(native["volume"]) == total
    valid = native_ok & source_ok & quantities & close_match & volume_match
    strict_known = len(valid) == 30 and bool(valid.all())
    strict_delta = float((buy - sell).sum()) if strict_known else None
    legacy_diff = np.asarray(source["volume"], float) - sell
    legacy_sum = float(np.nansum(legacy_diff))
    legacy_known = bool(np.isfinite(legacy_sum) and legacy_sum != 0)
    aliases = np.isfinite(source["volume"]) & np.isfinite(buy)
    return dict(
        strict_known=strict_known, strict_delta=strict_delta,
        strict_remove_long=bool(strict_known and strict_delta < 0),
        legacy_known=legacy_known, legacy_delta=legacy_sum if legacy_known else None,
        legacy_remove_long=bool(legacy_known and legacy_sum < 0),
        valid_source_minutes=int(valid.sum()),
        source_rows_present=int(np.isfinite(source["volume"]).sum()),
        volume_upvol_mismatch_minutes=int((aliases & (source["volume"] != buy)).sum()),
        close_mismatch_minutes=int((np.isfinite(source["close"]) & np.isfinite(native["close"]) & ~close_match).sum()),
        total_volume_mismatch_minutes=int((quantities & np.isfinite(native["volume"]) & ~volume_match).sum()),
    )


def synthetic_checks() -> dict:
    native = {name: np.ones(30) * value for name, value in
              (("open", 100), ("high", 101), ("low", 99), ("close", 100), ("volume", 10))}
    source = {name: values.copy() for name, values in native.items()}
    source.update(upvol=np.ones(30) * 4, downvol=np.ones(30) * 6, volume=np.ones(30) * 4)
    state = filter_states(native, source)
    assert state["strict_known"] and state["strict_remove_long"] and state["legacy_remove_long"]
    partial = {name: values.copy() for name, values in source.items()}
    for name in partial:
        partial[name][0] = np.nan
    state = filter_states(native, partial)
    assert not state["strict_known"] and not state["strict_remove_long"] and state["legacy_remove_long"]
    zero = {name: values.copy() for name, values in source.items()}
    zero.update(upvol=np.ones(30) * 5, downvol=np.ones(30) * 5, volume=np.ones(30) * 5)
    state = filter_states(native, zero)
    assert state["strict_known"] and state["strict_delta"] == 0 and not state["strict_remove_long"]
    absent = {name: np.full(30, np.nan) for name in source}
    state = filter_states(native, absent)
    assert not state["strict_known"] and not state["legacy_known"] and not state["legacy_remove_long"]
    mismatched = {name: values.copy() for name, values in source.items()}
    mismatched["close"][0] += 0.50
    assert not filter_states(native, mismatched)["strict_known"]
    wrong_volume = {name: values.copy() for name, values in native.items()}
    wrong_volume["volume"][0] += 1
    assert not filter_states(wrong_volume, source)["strict_known"]
    assert valid_ohlcv([100], [101], [99], [100], [0])[0]
    assert not valid_ohlcv([100], [99], [98], [100], [1])[0]
    assert jof(1401) == ENTRY_J and jof(1430) == EXIT_J and SIGNAL_J - FLOW_FIRST_J + 1 == 30
    assert calendar_status("2023-07-03")["kind"] != "normal" or is_early_close(pd.Timestamp("2023-07-03"))
    assert RT_COST == 2.24 and abs(GROSS_HURDLE - 4.48) < 1e-12
    return dict(passed=True, checks=["negative complete flow removes only eligible longs",
        "partial legacy removes while strict retains", "zero/unknown retained", "close/quantity mismatch invalidates strict",
        "OHLCV integrity", "exact close-label clock", "holiday skip", "independent native micro cost arithmetic"],
        prices_or_strategy_returns_read=False)


def committed_bytes(ref: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=ROOT)


def verify_before_prices(prereg: str) -> dict:
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    if branch != "codex/work":
        raise ValueError("Wrong execution branch: " + branch)
    for name in (PLAN, EVIDENCE):
        if committed_bytes(prereg, name) != (ROOT / name).read_bytes():
            raise ValueError("Preregistration/evidence differs from its committed version: " + name)
    if committed_bytes("HEAD", SCRIPT) != (ROOT / SCRIPT).read_bytes():
        raise ValueError("Freeze current implementation in HEAD before opening returns.")
    for directory in (ROOT / "analysis/outputs").glob("codex_hunt_v2_ldf_delta*"):
        if (directory / "gross_verified_execution.json").exists():
            raise ValueError("A successful H01 gross execution already exists; do not repeat in a retry directory.")
    paths = []
    for year in YEARS:
        paths.extend([ROOT / f"data/NQ_1min_{year}.csv", ROOT / f"data/NQ_1min_ON_{year}.csv"])
    of_paths = [p for year in YEARS for p in sorted((ROOT / "data").glob(f"OF_1min_{year}_*.csv"))]
    if not of_paths or any(not p.exists() for p in paths):
        raise FileNotFoundError("Frozen 2018-22 native/OF inputs unavailable.")
    for year in YEARS:
        if not any(p.name.startswith(f"OF_1min_{year}_") for p in of_paths):
            raise FileNotFoundError("Missing frozen OF year: " + str(year))
    dependencies = [PLAN, EVIDENCE, SCRIPT, "analysis/grid24.py", "analysis/codex_s03_calendar.py", "analysis/replica.py"]
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in paths + of_paths}
    hashes.update({name: sha(ROOT / name) for name in dependencies})
    # Metadata-only year/clock check precedes reading each file's price fields.
    metadata = []
    for path in paths + of_paths:
        key = pd.read_csv(path, usecols=["date", "time"])
        year = int(path.name.split("_")[-2] if path.name.startswith("OF_") else path.stem[-4:])
        if key.empty or not key["date"].between(year * 10000 + 101, year * 10000 + 1231).all():
            raise ValueError("Mislabeled source year; do not open price fields: " + path.name)
        hhmm = key["time"].to_numpy()
        if not ((hhmm >= 0) & (hhmm <= 2359) & (hhmm % 100 < 60) & (hhmm == np.floor(hhmm))).all():
            raise ValueError("Malformed native clock: " + path.name)
        metadata.append(dict(path=str(path.relative_to(ROOT)), rows=len(key),
                             min_date=int(key.date.min()), max_date=int(key.date.max()),
                             duplicate_metadata_keys=int(key.duplicated(["date", "time"]).sum())))
    return dict(prereg=prereg, implementation_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                hashes=hashes, metadata=metadata, native_paths=[str(p) for p in paths], of_paths=[str(p) for p in of_paths])


def audited_frame(paths: list[str], columns: tuple[str, ...], source: str) -> tuple[pd.DataFrame, dict]:
    parts = [pd.read_csv(path, usecols=["date", "time", *columns]) for path in paths]
    frame = pd.concat(parts, ignore_index=True)
    duplicate = frame.duplicated(["date", "time"], keep=False)
    grouped = frame.loc[duplicate].groupby(["date", "time"])[list(columns)].nunique(dropna=False)
    conflicts = grouped.gt(1).any(axis=1)
    if conflicts.any():
        raise ValueError(f"Conflicting {source} duplicates: {int(conflicts.sum())}; no overwrite permitted.")
    repeated = int(frame.duplicated(["date", "time"]).sum())
    frame = frame.drop_duplicates(["date", "time"]).sort_values(["date", "time"])
    return frame, dict(source=source, identical_duplicate_rows=repeated, conflicting_duplicate_keys=0, unique_rows=len(frame))


def native_grid(binding: dict) -> tuple[Grid24, dict]:
    native, duplicates = audited_frame(binding["native_paths"], NATIVE_FIELDS, "native")
    # Grid24 is the shared grid implementation. Isolated symlink inputs ensure
    # its constructor cannot glob 2017 warmup or 2023+ source files.
    cache = OUT / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    ignore = OUT / ".gitignore"
    if not ignore.exists():
        ignore.write_text("cache/\n*.lock\n")
    for source in map(Path, binding["native_paths"]):
        prefix = "night" if "_ON_" in source.name else "day"
        link = cache / f"{prefix}_{source.stem[-4:]}.csv"
        if link.is_symlink():
            if link.resolve() != source.resolve():
                raise ValueError("Cache link points to a different source.")
        elif link.exists():
            raise ValueError("Unexpected cache input exists.")
        else:
            link.symlink_to(source)
    expected = {f"{prefix}_{year}.csv" for prefix in ("day", "night") for year in YEARS}
    observed = {p.name for prefix in ("day", "night") for p in cache.glob(f"{prefix}_*.csv")}
    if observed != expected:
        raise ValueError("Isolated grid cache contains an unbound year/source; refuse price loading.")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        grid = Grid24(str(cache / "day_*.csv"), str(cache / "night_*.csv"))
    if pd.DatetimeIndex(grid.ts).year.max() > 2022 or pd.DatetimeIndex(grid.ts).year.min() < 2018:
        raise ValueError("Shared grid crossed the registered design period.")
    # Keep this frame only to prove the shared constructor agrees with audited
    # duplicate values, rather than silently dropping conflicting input keys.
    rows = np.searchsorted(grid.dates, native.date.to_numpy())
    cols = jof(native.time.to_numpy())
    if not np.allclose(grid.c[rows, cols], native.close.to_numpy(), equal_nan=True):
        raise ValueError("Shared grid does not match duplicate-audited native closes.")
    return grid, duplicates


def flow_grid(binding: dict, grid: Grid24) -> tuple[dict, dict]:
    frame, audit = audited_frame(binding["of_paths"], OF_FIELDS, "OF")
    source_dates = pd.to_datetime(frame.date.astype(str), format="%Y%m%d")
    source_minutes = jof(frame.time.to_numpy())
    source_wall = source_dates + pd.to_timedelta(source_minutes, unit="m")
    # Both US zones share DST dates; the per-bar source export is ET and the
    # native grid is CT. This is label conversion, not a measured receipt lag.
    native_wall = source_wall - pd.Timedelta(hours=1)
    ct_dates = native_wall.dt.strftime("%Y%m%d").astype(int).to_numpy()
    rows = np.searchsorted(grid.dates, ct_dates)
    inside = (rows < grid.D) & (grid.dates[np.minimum(rows, grid.D - 1)] == ct_dates)
    cols = (native_wall.dt.hour * 60 + native_wall.dt.minute).to_numpy()
    result = {}
    for name in OF_FIELDS:
        array = np.full((grid.D, 1440), np.nan)
        array[rows[inside], cols[inside]] = frame[name].to_numpy(float)[inside]
        result[name] = array
    audit.update(source_timezone="Eastern bar-close labels", native_timezone="Central bar-close labels",
                 conversion="source ET wall label minus60minutes; common US DST transition dates",
                 rows_outside_design_grid_after_conversion=int((~inside).sum()))
    return result, audit


def summarize_events(events: pd.DataFrame) -> pd.DataFrame:
    output = []
    for model in MODELS:
        kept = np.ones(len(events), dtype=bool) if model == "BASE" else events[f"keep_{model}"].to_numpy(bool)
        for population, population_mask in (("base", np.ones(len(events), bool)), ("kept", kept), ("removed", ~kept)):
            for period in ("2018-22", *map(str, YEARS)):
                period_mask = np.ones(len(events), bool) if period == "2018-22" else events.year.eq(int(period)).to_numpy()
                for side, side_mask in (("all", np.ones(len(events), bool)), ("long", events.side.eq(1).to_numpy()), ("short", events.side.eq(-1).to_numpy())):
                    rows = events[population_mask & period_mask & side_mask]
                    values = rows.gross_mnq.to_numpy(float)
                    finite = values[np.isfinite(values)]
                    output.append(dict(model=model, population=population, period=period, side=side,
                        events=len(rows), observed_endpoint_returns=len(finite),
                        unresolved_held_events=int(rows.unresolved_held_path.sum()),
                        gross_total_mnq=float(finite.sum()) if len(finite) else 0.0,
                        gross_mean_mnq=float(finite.mean()) if len(finite) else None,
                        gross_t=tstat(finite), gross_total_nq=float(finite.sum() * 10) if len(finite) else 0.0,
                        cost_hurdle_mnq=GROSS_HURDLE))
    return pd.DataFrame(output)


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
        grid, native_audit = native_grid(binding)
        flow, flow_audit = flow_grid(binding, grid)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            atr = grid.daily_atr(ATR_DAYS)
        valid = valid_ohlcv(grid.o, grid.h, grid.l, grid.c, grid.v)
        records, calendar_rows = [], []
        reasons = {}
        for day, ts in enumerate(pd.DatetimeIndex(grid.ts)):
            status = calendar_status(ts)
            skip_pl = is_early_close(ts)
            calendar_rows.append(dict(date=ts.date().isoformat(), cash_kind=status["kind"],
                                      cash_close_j=status["cash_close_j"], pl_early_skip=bool(skip_pl)))
            reason = None
            if status["kind"] != "normal" or skip_pl:
                reason = "known_calendar_skip"
            elif not np.isfinite(atr[day]) or atr[day] <= 0:
                reason = "prior15_stored_weekday_atr_warmup_or_unavailable"
            elif not valid[day, OPEN_J:SIGNAL_J + 1].all():
                reason = "incomplete_or_invalid_known_feature_window"
            else:
                move = grid.c[day, SIGNAL_J] - grid.o[day, OPEN_J]
                if move == 0 or abs(move) < MIN_MOVE_ATR * atr[day]:
                    reason = "below_frozen_ldf_move_threshold"
            if reason is not None:
                reasons[reason] = reasons.get(reason, 0) + 1
                continue
            side = 1 if move > 0 else -1
            segment = slice(FLOW_FIRST_J, SIGNAL_J + 1)
            native = {name: getattr(grid, name[0] if name != "volume" else "v")[day, segment] for name in NATIVE_FIELDS}
            source = {name: array[day, segment] for name, array in flow.items()}
            states = filter_states(native, source)
            asof_has_flow = bool(np.isfinite(flow["volume"][day, :SIGNAL_J + 1]).any())
            # If any finite delta contribution exists in the causal window, a
            # finite buy-volume already exists by the decision. Later-day OF
            # availability cannot create a valid negative earlier sum.
            if not asof_has_flow:
                states.update(legacy_known=False, legacy_delta=None, legacy_remove_long=False)
            held_valid = valid[day, ENTRY_J:EXIT_J + 1]
            entry, exit_price = grid.o[day, ENTRY_J], grid.c[day, EXIT_J]
            points = (exit_price - entry) * side if np.isfinite(entry) and np.isfinite(exit_price) else np.nan
            records.append(dict(date=ts.date().isoformat(), year=ts.year, side=side, decision_j=SIGNAL_J,
                entry_label_j=ENTRY_J, exit_label_j=EXIT_J, atr=float(atr[day]), day_move=float(move),
                entry_open=float(entry), exit_close=float(exit_price), gross_points=float(points),
                gross_mnq=float(points * MNQ_POINT_VALUE), gross_nq=float(points * 20),
                invalid_or_missing_held_minutes=int((~held_valid).sum()),
                unresolved_held_path=not bool(held_valid.all()),
                asof_has_any_of=asof_has_flow, keep_LEGACY=not (side > 0 and states["legacy_remove_long"]),
                keep_STRICT30=not (side > 0 and states["strict_remove_long"]), **states))
        events = pd.DataFrame(records)
        if events.empty:
            raise ValueError("No registered gross events; retain attempt and investigate inputs, no economic result.")
        summary = summarize_events(events)
        primary = events[events.keep_STRICT30]
        observed = primary.gross_mnq[np.isfinite(primary.gross_mnq)]
        complete_endpoint = len(observed) == len(primary)
        complete_held = not bool(events.unresolved_held_path.any())
        mean = float(observed.mean()) if len(observed) else None
        economic_pass = bool(mean is not None and mean >= GROSS_HURDLE and len(primary) >= MIN_KEPT)
        passed = economic_pass and complete_endpoint and complete_held
        source_hashes = binding["hashes"]
        if source_hashes != {name: sha(ROOT / name) for name in source_hashes}:
            raise ValueError("Bound source changed; refuse successful gross artifact.")
        csv_once(OUT / "gross_events.csv", events)
        csv_once(OUT / "gross_summary.csv", summary)
        csv_once(OUT / "gross_calendar_audit.csv", pd.DataFrame(calendar_rows))
        dump_once(OUT / "gross_input_binding.json", binding)
        gate = dict(primary_model="STRICT30", gross_kind="RAW_NO_STOP", gross_hurdle_mnq=GROSS_HURDLE,
            native_roundtrip_cost_mnq=RT_COST, min_kept=MIN_KEPT, kept_events=len(primary), base_events=len(events),
            removed_events=int((~events.keep_STRICT30).sum()), observed_primary_endpoint_returns=len(observed),
            primary_gross_mean_mnq=mean, primary_gross_t=tstat(observed), economic_pass=economic_pass,
            all_primary_endpoints_observed=complete_endpoint, all_base_held_paths_complete=complete_held,
            unresolved_base_held_events=int(events.unresolved_held_path.sum()), passed=passed,
            counted_evaluations_this_gross_screen=0, gross_hypotheses_this_screen=1,
            frozen_later_counted_models=list(MODELS), validation_run=False, account_tests_run=False,
            decisions="Proceed only if passed; otherwise stop H01 before all counted designs/validation/benches.")
        dump_once(OUT / "gross_gate.json", gate)
        audit = dict(native=native_audit, flow=flow_audit, calendar_reasons=reasons,
            no_2017_warmup=True, no_2023_or_later_files=True, no_g_trading_eligibility=True,
            atr_basis="shifted prior15 STORED weekday true ranges from shared Grid24; missing dates dropped; source starts2018",
            completed_flow_labels_ct="13:31 through14:00 inclusive", raw_entry_label_ct="14:01 native minute open (14:00 wall)",
            raw_exit_label_ct="14:30 native minute close", stops_or_targets_simulated=False,
            native_micro_prices_verified=False, fees_are_repository_native_MNQ_assumptions=True,
            actual_receipt_spread_and_roll_fidelity_verified=False,
            invalid_held_paths_retained_and_block_pass=True, strict_unknown_retains_original_trade=True,
            strict_flow_known_events=int(events.strict_known.sum()),
            volume_upvol_mismatch_minutes_on_event_windows=int(events.volume_upvol_mismatch_minutes.sum()))
        dump_once(OUT / "gross_data_audit.json", audit)
        artifacts = ["gross_events.csv", "gross_summary.csv", "gross_calendar_audit.csv", "gross_input_binding.json", "gross_gate.json", "gross_data_audit.json"]
        marker = dict(started_utc=started, completed_utc=utcnow(), phase="gross", passed=passed,
            prereg=prereg, implementation_commit=binding["implementation_commit"], script_sha256=sha(ROOT / SCRIPT),
            artifacts_sha256={name: sha(OUT / name) for name in artifacts}, strategy_execution_run=False,
            raw_window_source_returns_calculated=True, counted_evaluations=0, new_hypotheses=1,
            validation_run=False, account_tests_run=False)
        dump_once(OUT / "gross_verified_execution.json", marker)
        with (OUT / "attempts.jsonl").open("a") as log:
            log.write(json.dumps(dict(completed_utc=marker["completed_utc"], phase="gross", completed=True, passed=passed)) + "\n")
        return gate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("fixtures", "gross"), required=True)
    parser.add_argument("--prereg")
    args = parser.parse_args()
    if args.phase == "fixtures":
        result = synthetic_checks()
        result["script_sha256"] = sha(ROOT / SCRIPT)
        path = OUT / f"synthetic_checks_{result['script_sha256'][:12]}.json"
        dump_once(path, result)
    else:
        if not args.prereg:
            parser.error("Gross phase requires a committed --prereg.")
        result = gross(args.prereg)
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__":
    main()
