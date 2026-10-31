"""H05 frozen protected design: ATR source admission BEFORE new stopped returns.

--phase admit computes only past ATR/source metadata and an immutable cache.
--phase design requires the exact PASS admission marker SHA. Imports/fixtures
never read actual inputs. Shared execution adapter uses native MNQ fee maths;
neither old outcome maker,2023+ nor account/bench engine is called here.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import warnings

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_hunt_v2_highwin_confirmation"
os.environ["NUMBA_CACHE_DIR"] = str(OUT / "cache/numba")
sys.path.insert(0, str(ROOT / "analysis"))
import numpy as np
import pandas as pd
import metrics as M
import resampling as R
from grid24 import Grid24
from codex_s03_calendar import calendar_status
from codex_hunt_v2_ldf_delta import audit_atr_references, csv_once, runtime_versions, sha, tstat, utcnow, valid_ohlcv

SCRIPT = "analysis/codex_hunt_v2_highwin_design.py"
EXECUTION = "analysis/codex_hunt_v2_highwin_execution.py"
PLAN = "agents/codex/plans/hunt_v2_highwin_confirmation.md"
ADJUDICATION = "agents/codex/research/hunt_v2_highwin_atr_adjudication.md"
GROSS_MARKER = OUT / "gross_verified_execution.json"
GROSS_BINDING = OUT / "gross_input_binding.json"
ENTRIES = OUT / "parent_entries.csv"
RAW_EVENTS = OUT / "gross_events.csv"
GROSS_PREREG = "16635fcc3890252886cd82f60aac143161685814"
ADMIT_MARKER = OUT / "design_atr_admission_verified.json"
CACHE = OUT / "cache/design_native_grid.npz"
MODELS = ("PROTECTED_HW", "TIME_CONTROL")
YEARS = tuple(range(2018, 2023))
STATE_START, EXIT_J = 20170901, 891


def safe(value):
    if isinstance(value, dict): return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [safe(v) for v in value]
    if isinstance(value, np.generic): return safe(value.item())
    if isinstance(value, float) and not np.isfinite(value): return None
    return value


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle: json.dump(safe(value), handle, indent=2, allow_nan=False); handle.write("\n")


def committed(ref, name):
    return subprocess.check_output(["git", "show", f"{ref}:{name}"], cwd=ROOT)


def nw5_t(values):
    # Exact established H01 design NW5 estimator; same252-day daily axis.
    x = np.asarray(values, float)
    if not len(x): return None
    centered = x - x.mean(); covariance_sum = float(centered @ centered)
    for lag in range(1, min(5, len(x) - 1) + 1):
        covariance_sum += 2 * (1 - lag / 6) * float(centered[lag:] @ centered[:-lag])
    return float(x.mean() * len(x) / np.sqrt(covariance_sum)) if covariance_sum > 0 else None


def verify(prereg, phase):
    if subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() != "codex/work": raise ValueError("H05 stays on codex/work.")
    subprocess.check_call(["git", "merge-base", "--is-ancestor", prereg, "HEAD"], cwd=ROOT)
    marker = json.loads(GROSS_MARKER.read_text()); binding = json.loads(GROSS_BINDING.read_text())
    if not (marker["phase"] == "raw_gross" and marker["passed"] is True and marker["implementation_commit"] == GROSS_PREREG):
        raise ValueError("The exact committed successful H05 gross proof is required.")
    for name, expected in marker["artifacts_sha256"].items():
        if Path(name).name != name or sha(OUT / name) != expected: raise ValueError("Gross artifact changed:" + name)
    for name, expected in binding["hashes"].items():
        if sha(ROOT / name) != expected: raise ValueError("Gross-bound code/source/input changed:" + name)
    dependencies = [SCRIPT, EXECUTION, PLAN, ADJUDICATION, "analysis/grid.py", "analysis/grid24.py", "analysis/metrics.py",
        "analysis/resampling.py", "analysis/codex_hunt_v2_ldf_delta.py", "analysis/codex_s03_calendar.py",
        "analysis/replica.py", "agents/codex/RESEARCH_CONTROLS.md"]
    hashes = dict(binding["hashes"])
    for name in dependencies:
        raw = (ROOT / name).read_bytes()
        if committed("HEAD", name) != raw or committed(prereg, name) != raw: raise ValueError("Commit exact design/adjudication/helper before new values:" + name)
        hashes[name] = hashlib.sha256(raw).hexdigest()
    for directory in (ROOT / "analysis/outputs").glob("codex_hunt_v2_highwin_confirmation*"):
        names = ("design_atr_admission_attempt.json", "design_atr_admission_verified.json") if phase == "admit" else ("design_attempt.json", "design_verified_execution.json")
        if any((directory / name).exists() for name in names): raise ValueError("Design phase attempt/completion retained; no automatic retry or alternate directory.")
    hashes[str(GROSS_MARKER.relative_to(ROOT))] = sha(GROSS_MARKER)
    hashes[str(GROSS_BINDING.relative_to(ROOT))] = sha(GROSS_BINDING)
    hashes[str(ENTRIES.relative_to(ROOT))] = sha(ENTRIES)
    hashes[str(RAW_EVENTS.relative_to(ROOT))] = sha(RAW_EVENTS)
    return dict(prereg=prereg, implementation_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        gross_prereg=GROSS_PREREG, gross_marker_sha256=sha(GROSS_MARKER), hashes=hashes,
        native_paths=binding["native_paths"], versions=runtime_versions(), source_adjudication=ADJUDICATION,
        ordinary_price_receipt_not_invented_fatal_gate=True)


def recheck(binding):
    for name, expected in binding["hashes"].items():
        if sha(ROOT / name) != expected: raise ValueError("Frozen design-bound file changed:" + name)


def load_bound_grid(binding):
    cache = OUT / "cache"; cache.mkdir(parents=True, exist_ok=True)
    names = set()
    for name in binding["native_paths"]:
        source = Path(name); prefix = "night" if "_ON_" in source.name else "day"
        link = cache / f"{prefix}_{source.stem[-4:]}.csv"; names.add(link.name)
        if link.is_symlink():
            if link.resolve() != source.resolve(): raise ValueError("Bound native cache symlink changed.")
        elif link.exists(): raise ValueError("Unbound nonlink native cache input.")
        else: link.symlink_to(source)
    if {path.name for path in cache.glob("*.csv")} != names: raise ValueError("Unbound year/source in native cache.")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return Grid24(str(cache / "day_*.csv"), str(cache / "night_*.csv"))


def entries_from_frozen(grid):
    frame = pd.read_csv(ENTRIES)
    if len(frame) != 216 or frame.event_id.duplicated().any() or frame.date.duplicated().any():
        raise ValueError("Exact216unique frozen parent entries required; no entry selection.")
    if not pd.to_datetime(frame.date).dt.year.isin(YEARS).all(): raise ValueError("Frozen entry outside2018--22.")
    actual = grid.o[frame.row.to_numpy(int), frame.entry_j.to_numpy(int)]
    if not np.array_equal(actual, frame.entry.to_numpy(float)): raise ValueError("Native entry changed from original gross proof.")
    return frame


def atr_source_audit(grid, entries):
    """Defined observed-date ranges with EVERY gap/source limitation retained."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        atr = grid.daily_atr(15)
        memberships = audit_atr_references(grid, atr)
        hi, low = np.nanmax(grid.h, axis=1), np.nanmin(grid.l, axis=1)
    observed = np.isfinite(grid.c); valid = valid_ohlcv(grid.o, grid.h, grid.l, grid.c, grid.v)
    has = observed.any(axis=1)
    last_j = np.where(has, 1439 - np.argmax(observed[:, ::-1], axis=1), -1)
    previous_close_row = np.full(grid.D, -1, int); previous = -1
    daily_rows = []
    for row, timestamp in enumerate(pd.DatetimeIndex(grid.ts)):
        previous_close_row[row] = previous
        if has[row]: previous = row
        kind = calendar_status(timestamp)["kind"]
        rth_count = int(observed[row, 511:916].sum()); normal_gap = kind == "normal" and rth_count < 405
        daily_rows.append(dict(row=row, date=timestamp.date().isoformat(), date_id=int(grid.dates[row]),
            calendar_kind=kind, observed_bars=int(observed[row].sum()), invalid_observed_bars=int((observed[row] & ~valid[row]).sum()),
            observed_RTH_0831_1515=rth_count, missing_normal_RTH_minutes=405 - rth_count if kind == "normal" else None,
            normal_RTH_source_limit=normal_gap, has_any_observed_close=bool(has[row]),
            stored_weekday=bool(has[row] and timestamp.dayofweek < 5), observed_high=hi[row], observed_low=low[row],
            last_observed_j=int(last_j[row]), previous_close_source_row=int(previous_close_row[row]),
            previous_close_source_date_id=int(grid.dates[previous_close_row[row]]) if previous_close_row[row] >= 0 else None))
    daily = pd.DataFrame(daily_rows)
    row_lookup = {int(day): row for row, day in enumerate(grid.dates)}
    records, affected = [], []
    augmented = entries.copy(); augmented["atr15"] = atr[entries.row.to_numpy(int)]
    fatal = []
    for index, event in augmented.iterrows():
        row = int(event.row); membership = memberships[row]; dates = json.loads(membership["atr_reference_date_ids"])
        ids = [row_lookup[day] for day in dates]
        known = bool(len(ids) == 15 and all(k < row for k in ids) and all(day >= STATE_START for day in dates)
            and np.isfinite(event.atr15) and event.atr15 > 0)
        source_limits = [int(grid.dates[k]) for k in ids if bool(daily.loc[k, "normal_RTH_source_limit"])]
        previous_ids = [int(grid.dates[previous_close_row[k]]) if previous_close_row[k] >= 0 else None for k in ids]
        if any(int(daily.loc[k, "invalid_observed_bars"]) > 0 for k in ids): known = False
        # Coverage omissions between the earliest stored member and decision
        # remain visible, whether absent or an overnight-only stored date.
        interval = daily.iloc[min(ids):row] if ids else daily.iloc[0:0]
        absent_normal = interval[(interval.calendar_kind == "normal") & ~interval.has_any_observed_close]
        record = dict(event_id=event.event_id, date=event.date, row=row, atr15=event.atr15,
            **membership, TR_previous_close_source_date_ids=json.dumps(previous_ids),
            source_limit_reference_date_ids=json.dumps(source_limits),
            missing_whole_normal_dates_in_reference_span=json.dumps(absent_normal.date_id.astype(int).tolist()),
            source_limit=bool(source_limits or len(absent_normal)), observed_definition_admitted=known,
            external_full_range_or_PL_parity_verified=False)
        records.append(record)
        augmented.loc[index, "ATR_source_limit"] = record["source_limit"]
        if record["source_limit"]: affected.append(record)
        if not known: fatal.append(record)
    audit = dict(passed=not fatal and len(augmented) == 216, event_count=len(augmented),
        fatal_membership_past_only_finite_positive_or_observed_integrity_events=fatal,
        affected_source_limit_events=len(affected), statistical_gate_separate_from_source_limits=True,
        source_status="OBSERVED_DEFINITION_WITH_SOURCE_LIMITS" if affected else "OBSERVED_DEFINITION_ONLY_EXTERNAL_PARITY_UNVERIFIED",
        definition="ExactGrid24.daily_atr15+sharedaudit;15storedweekdayavailable-barTR;past-only;noRTH/ideal1440substitute",
        source_limit_policy="RETAINALLaffectedreferences/events;NOdeletions/substitution/denominatorchange;fullfeed/PLpromotionclaimsremainunverified",
        new_stopped_or_time_control_outcomes_calculated=False)
    return augmented, pd.DataFrame(records), daily, pd.DataFrame(affected), audit


@contextmanager
def design_lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "design.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB); yield


def admit(prereg):
    with design_lock():
        binding = verify(prereg, "admit"); started = utcnow()
        dump(OUT / "design_atr_admission_attempt.json", dict(started_utc=started, prereg=prereg, script_sha256=sha(ROOT / SCRIPT)))
        grid = load_bound_grid(binding); entries = entries_from_frozen(grid)
        augmented, refs, daily, affected, audit = atr_source_audit(grid, entries)
        recheck(binding)
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        with CACHE.open("xb") as handle:
            np.savez_compressed(handle, **{name: getattr(grid, name) for name in ("o", "h", "l", "c", "v", "dates", "ts", "last_j")}, D=np.array(grid.D))
        names = []
        for name, frame in (("design_atr_entries.csv", augmented), ("design_atr_reference_ids.csv", refs),
            ("design_atr_daily_source_audit.csv", daily), ("design_atr_source_limit_events.csv", affected)):
            csv_once(OUT / name, frame); names.append(name)
        dump(OUT / "design_atr_admission_gate.json", audit); dump(OUT / "design_atr_input_binding.json", binding)
        names += ["design_atr_admission_attempt.json", "design_atr_admission_gate.json", "design_atr_input_binding.json"]
        marker = dict(started_utc=started, completed_utc=utcnow(), phase="ATR_source_admission_before_stopped_returns", passed=audit["passed"],
            prereg=prereg, implementation_commit=binding["implementation_commit"], script_sha256=sha(ROOT / SCRIPT),
            artifacts_sha256={name: sha(OUT / name) for name in names}, cache_path=str(CACHE.relative_to(ROOT)), cache_sha256=sha(CACHE),
            source_status=audit["source_status"], affected_source_limit_events=audit["affected_source_limit_events"],
            stopped_outcomes_calculated=False, economic_evaluations_added=0, original_parent_entries_preserved=True)
        dump(ADMIT_MARKER, marker)
        return dict(passed=marker["passed"], source_status=marker["source_status"], source_limit_events=marker["affected_source_limit_events"], admission_marker_sha256=sha(ADMIT_MARKER), stopped_outcomes_calculated=False)


def metrics_rows(models, axis):
    rows = []; daily_all = pd.DataFrame(index=axis)
    for model, trades in models.items():
        trade_dates = pd.to_datetime(trades.date).dt.normalize()
        daily = pd.Series(trades.net_mnq.to_numpy(float), index=trade_dates).groupby(level=0).sum().reindex(axis, fill_value=0.)
        daily_all[model] = daily
        for period in ("2018-22", *map(str, YEARS)):
            date_mask = np.ones(len(trades), bool) if period == "2018-22" else trade_dates.dt.year.to_numpy() == int(period)
            period_axis = axis if period == "2018-22" else axis[axis.year == int(period)]
            for side in ("both", "long", "short"):
                mask = date_mask & (np.ones(len(trades), bool) if side == "both" else trades.side.to_numpy() == (1 if side == "long" else -1))
                subset = trades.loc[mask]; dates = trade_dates[mask]
                values = subset.net_mnq.to_numpy(float)
                d = pd.Series(values, index=dates).groupby(level=0).sum().reindex(period_axis, fill_value=0.)
                standard = M.perf(d, values)
                rows.append(dict(model=model, period=period, side=side, net_total=float(values.sum()),
                    trade_t=tstat(values), daily_NW5_t=nw5_t(d), **standard))
    return pd.DataFrame(rows), daily_all


def design_gate(models, metrics, source_status):
    primary = models["PROTECTED_HW"]
    totals = primary.groupby(pd.to_datetime(primary.date).dt.year).net_mnq.sum().reindex(YEARS, fill_value=0.)
    row = metrics[(metrics.model == "PROTECTED_HW") & (metrics.period == "2018-22") & (metrics.side == "both")].iloc[0]
    total = float(primary.net_mnq.sum()); excluded = {str(year): total - float(value) for year, value in totals.items()}
    passed = bool(len(primary) >= 100 and total > 0 and pd.notna(row.trade_t) and row.trade_t >= 2
        and pd.notna(row.daily_NW5_t) and row.daily_NW5_t >= 2 and (totals > 0).sum() >= 4 and min(excluded.values()) > 0)
    return dict(statistical_design_pass=passed, trades=len(primary), net_total=total, trade_t=row.trade_t,
        daily_NW5_t=row.daily_NW5_t, positive_years=int((totals > 0).sum()), annual_totals=totals.to_dict(),
        total_excluding_each_year=excluded, source_status=source_status, source_limits_resolved=False,
        promotion_or_trading_approved=False, next_stage="IMMEDIATE_FROZEN_PERSONAL19_BOOK_BENCH_WITH_LIMITATIONS" if passed else "CLOSE_H05_BEFORE_BENCH_VALIDATION_OR_MORE_ROBUSTNESS")


def design(prereg, admission_sha):
    with design_lock():
        binding = verify(prereg, "design")
        if sha(ADMIT_MARKER) != admission_sha: raise ValueError("Exact explicit ATR-admission marker SHA required.")
        admission = json.loads(ADMIT_MARKER.read_text())
        if not (admission["passed"] and admission["prereg"] == prereg and admission["script_sha256"] == sha(ROOT / SCRIPT)):
            raise ValueError("Matching pre-outcome ATR admission PASS required.")
        for name, expected in admission["artifacts_sha256"].items():
            if sha(OUT / name) != expected: raise ValueError("ATR admission artifact changed:" + name)
        if sha(CACHE) != admission["cache_sha256"]: raise ValueError("Bound private native cache changed.")
        started = utcnow(); dump(OUT / "design_attempt.json", dict(started_utc=started, prereg=prereg,
            admission_marker_sha256=admission_sha, implementation_commit=binding["implementation_commit"], script_sha256=sha(ROOT / SCRIPT)))
        with np.load(CACHE, allow_pickle=False) as saved:
            grid = SimpleNamespace(**{name: saved[name] for name in saved.files})
        grid.D = int(grid.D)
        entries = pd.read_csv(OUT / "design_atr_entries.csv")
        from codex_hunt_v2_highwin_execution import execute_native_models
        # This boundary is the FIRST new stopped/time-control outcome call.
        models = execute_native_models(grid, entries)
        axis = pd.bdate_range("2018-01-01", "2022-12-31")
        metrics, daily = metrics_rows(models, axis)
        gate = design_gate(models, metrics, admission["source_status"])
        raw = pd.read_csv(RAW_EVENTS, usecols=["event_id", "gross_MNQ"])
        control = models["TIME_CONTROL"].merge(raw, on="event_id", validate="one_to_one")
        if len(control) != len(entries) or not np.allclose(control.gross_mnq, control.gross_MNQ, atol=1e-9):
            raise ValueError("TIME control differs from bound raw gross endpoints; actual outcome attempt retained.")
        recheck(binding)
        names = []
        for model, frame in models.items():
            name = f"design_{model}_trades.csv"; csv_once(OUT / name, frame); names.append(name)
        csv_once(OUT / "design_metrics_side_year.csv", metrics); csv_once(OUT / "design_daily.csv", daily.rename_axis("date").reset_index())
        names += ["design_metrics_side_year.csv", "design_daily.csv"]
        bridge = {}
        for model, trades in models.items():
            bridge[model] = dict(events=len(trades), gross_total_MNQ=float(trades.gross_mnq.sum()),
                net_total_MNQ=float(trades.net_mnq.sum()), commission_total=float(trades.commission_mnq.sum()),
                slippage_total=float((trades.entry_slippage_mnq + trades.exit_slippage_mnq).sum()),
                break_even_total_cost_per_event=float(trades.gross_mnq.mean()),
                break_even_commission_per_event=float((trades.gross_mnq - trades.entry_slippage_mnq - trades.exit_slippage_mnq).mean()),
                native_point_value=2., commission_RT=1.24, adverse_market_stop_per_fill=.5,
                shared_engine_NQ_net_ignored=True, extra_cost_latency_stress_not_run=True)
        dump(OUT / "design_cost_bridge.json", bridge); dump(OUT / "design_gate.json", gate); dump(OUT / "design_input_binding.json", binding)
        names += ["design_cost_bridge.json", "design_gate.json", "design_input_binding.json", "design_attempt.json"]
        marker = dict(started_utc=started, completed_utc=utcnow(), phase="frozen_two_model_native_cost_design", prereg=prereg,
            implementation_commit=binding["implementation_commit"], script_sha256=sha(ROOT / SCRIPT),
            admission_marker_sha256=admission_sha, artifacts_sha256={name: sha(OUT / name) for name in names},
            statistical_design_pass=gate["statistical_design_pass"], source_status=admission["source_status"],
            source_limits_resolved=False, economic_evaluations_added=2, models=list(MODELS),
            validation_or_account_or_robustness_run=False, immediate_book_bench_required_if_pass=True)
        dump(OUT / "design_verified_execution.json", marker)
        return gate


def fixtures():
    # Only artificial returns/source membership; no owned values/ledgers read.
    assert nw5_t([0., 0., 0.]) is None and nw5_t([1., 2., 3.]) is not None
    values = np.r_[np.zeros(10), np.ones(10)]
    assert nw5_t(values) < tstat(values)
    assert safe(dict(a=np.inf, b=np.float64(1), c=np.nan)) == dict(a=None, b=1., c=None)
    checks = ["exactH01NW5semantics/zeros/dependence", "JSONnonfiniteexplicitunknown"]
    dates = pd.date_range("2017-12-01", periods=46)
    arrays = {name: np.full((len(dates), 1440), np.nan) for name in ("o", "h", "l", "c", "v")}
    partial_row, absent_row = 26, 33
    for row in range(len(dates)):
        if row == absent_row: continue
        js = [1200] if row == partial_row else [10, 540, 900, 1430]
        price = 100 + row
        for name, value in (("o", price), ("h", price + 1), ("l", price - 1), ("c", price + .25), ("v", 10.)):
            arrays[name][row, js] = value
    synthetic = SimpleNamespace(**arrays, ts=dates.to_numpy(), dates=dates.strftime("%Y%m%d").astype(int).to_numpy(), D=len(dates))
    synthetic.daily_atr = lambda n: Grid24.daily_atr(synthetic, n)
    event_row = 42
    artificial_entries = pd.DataFrame([dict(row=event_row, date=dates[event_row].date().isoformat(),
        event_id=f"ARTIFICIAL_SOURCE_{i}") for i in range(216)])
    augmented, refs, daily, affected, admission = atr_source_audit(synthetic, artificial_entries)
    assert admission["passed"] and len(affected) == 216 and augmented.ATR_source_limit.all()
    reference_ids = json.loads(refs.iloc[0].atr_reference_date_ids)
    assert len(reference_ids) == 15 and max(reference_ids) < int(synthetic.dates[event_row])
    assert int(synthetic.dates[partial_row]) in reference_ids and daily.loc[partial_row, "stored_weekday"]
    assert daily.loc[partial_row, "observed_RTH_0831_1515"] == 0 and daily.loc[partial_row, "normal_RTH_source_limit"]
    assert int(synthetic.dates[absent_row]) not in reference_ids
    assert int(synthetic.dates[absent_row]) in json.loads(refs.iloc[0].missing_whole_normal_dates_in_reference_span)
    assert len(json.loads(refs.iloc[0].TR_previous_close_source_date_ids)) == 15
    checks.append("exactsharedATR15pastmembership+previous-closeIDs;ON-onlynormaldatestoredpartialTR;wholemissingdateflaggednotfilled")
    early_entries = artificial_entries.assign(row=5, date=dates[5].date().isoformat())
    _, _, _, _, immature = atr_source_audit(synthetic, early_entries)
    assert not immature["passed"] and len(immature["fatal_membership_past_only_finite_positive_or_observed_integrity_events"]) == 216
    checks.append("ATRwarmup/finitepositive/count/past-onlygateBEFOREoutcomes;retainsALLsource-limitevents")
    def fake_model(totals):
        return pd.DataFrame([dict(date=f"{year}-01-02", net_mnq=total / 20) for year, total in totals.items() for _ in range(20)])
    models = {"PROTECTED_HW": fake_model({y: 10. for y in YEARS})}
    metric = pd.DataFrame([dict(model="PROTECTED_HW", period="2018-22", side="both", trade_t=2.1, daily_NW5_t=2.1)])
    passed = design_gate(models, metric, "ARTIFICIAL_SOURCE_LIMITS")
    assert passed["statistical_design_pass"] and not passed["promotion_or_trading_approved"] and not passed["source_limits_resolved"]
    models["PROTECTED_HW"] = fake_model({2018: 100., 2019: -10., 2020: 2., 2021: 2., 2022: 2.})
    assert not design_gate(models, metric, "ARTIFICIAL_SOURCE_LIMITS")["statistical_design_pass"]
    metric.loc[0, "daily_NW5_t"] = 1.99
    assert not design_gate({"PROTECTED_HW": fake_model({y: 10. for y in YEARS})}, metric, "ARTIFICIAL_SOURCE_LIMITS")["statistical_design_pass"]
    checks.append("frozenstatisticaldesigngate/year-exclusion/NW5boundaries;statPASSneverresolvessourcelimits/promotion")
    return dict(passed=True, checks=checks,
        real_native_ATR_entries_or_outcomes_read=False, script_sha256=sha(ROOT / SCRIPT), versions=runtime_versions())


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--phase", required=True, choices=("fixtures", "admit", "design"))
    parser.add_argument("--prereg"); parser.add_argument("--admission-sha")
    args = parser.parse_args()
    if args.phase == "fixtures":
        result = fixtures(); dump(OUT / f"design_synthetic_checks_{result['script_sha256'][:12]}.json", result)
    else:
        if not args.prereg: parser.error("Actual phase requires committed --prereg.")
        if args.phase == "admit": result = admit(args.prereg)
        else:
            if not args.admission_sha: parser.error("Design requires exact --admission-sha from pre-outcome admission.")
            result = design(args.prereg, args.admission_sha)
    print(json.dumps(safe(result), allow_nan=False))


if __name__ == "__main__": main()
