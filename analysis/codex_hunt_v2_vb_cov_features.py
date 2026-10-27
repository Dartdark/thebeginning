"""H10 lagged published-book covariance FEATURE/support gate only.

Import and --fixtures read no owned data, headers, calendars or market returns.
Only --features may bind/read the explicitly frozen published personal19 CSV,
after an unchanged committed preregistration and implementation are verified.
No raw prices, VB execution, candidate P&L, gross screen or account paths run.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from contextlib import contextmanager
import csv
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import fcntl
from fractions import Fraction
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_hunt_v2_vb_covariance"
SCRIPT = "analysis/codex_hunt_v2_vb_cov_features.py"
PLAN = "agents/codex/plans/hunt_v2_vb_covariance.md"
EVIDENCE = "agents/codex/research/hunt_v2_independent_book_constraint_gate.md"
SOURCE_PIN = "d14dc9a153df128aafd3f48d4fea2aa78b88bb28"
BASELINE = "analysis/outputs/codex_rebound/personal19/UNIFORM/fee_1.24/baseline_daily19.csv"
BASELINE_COPY = "analysis/outputs/codex_rebound/personal19/SUNDAY2/fee_1.24/baseline_daily19.csv"
BASELINE_SHA256 = "d724c7d02b6db71e63ba705079dbea7fefaa42c6b4f436308a28993ca1908803"
LEG_COLUMNS = ("VaultBreak", "OvernightBiasML", "MondayLong", "ExpirationOpenShort", "LateDayFlow", "NFPFade",
    "BridgeMondayLong", "CLSundayFade_perMCL", "ESMOCFollow_perMES", "RelativeStrength", "FC2B", "TwinContinuation",
    "OvernightTick", "DualThrust", "Kusho", "S47", "S30", "SwingTarget", "PaperTrend")
SOURCE_CODE = (SCRIPT, "analysis/codex_hunt_v2_highwin_bench.py", "analysis/codex_rebound_personal_update.py",
    "agents/codex/RESEARCH_CONTROLS.md", "agents/codex/research/hunt_v2_bench_source_map.md",
    "analysis/codex_s03_calendar.py", "analysis/replica.py", "analysis/grid.py")
DESIGN_START, DESIGN_END = date(2018, 1, 1), date(2023, 1, 1)
DESIGN_YEARS = tuple(range(2018, 2023))
WINDOW = 252
MIN_KNOWN_FEATURE_DAYS = 100
MIN_EXTRA_DAYS = 50
MIN_EXTRA_YEARS = 3
NUMBER = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")
DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")
LIMITATIONS = [
    "Feature is a fixed selected published personal19 shadow-book daily proxy, not actual native account equity or receipt.",
    "Prior dated rows are assumed completed before the next VB10:00 decision under the frozen exit/next-book-day/Twin16:00 booking contract.",
    "Core fees use nonzero-day activity and can undercount reentries; marks, source/version and OT coverage are not certified by fee repricing.",
    "BASE19 includes its existing one-MNQ VB; X is that same saved VB column. Actual protected replay may differ and needs implementation controls.",
    "The current roster and parent were selected on this historical data. 2023+ can only be previously seen historical validation.",
    "Negative historical sample delta variance is a forecast/proxy condition, not realized variance reduction, alpha, promotion or account approval.",
    "FEATURE counts are an upper bound on selected qualifying first-signal dates; no parent execution/trade membership or profit is established.",
]


def now():
    return datetime.now(timezone.utc).isoformat()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def exact(value):
    return str(value.numerator) + "/" + str(value.denominator)


def decimal_fraction(text):
    """Exact stored decimal representation, never binary-float classification."""
    text = text.strip()
    if not text or NUMBER.fullmatch(text) is None:
        raise ValueError("Missing/non-numeric/nonfinite published financial cell.")
    try:
        number = Decimal(text)
    except InvalidOperation as error:
        raise ValueError("Invalid published decimal financial cell.") from error
    if not number.is_finite():
        raise ValueError("Nonfinite published financial cell.")
    return Fraction(number)


def parse_date(text):
    if DATE.fullmatch(text) is None:
        raise ValueError("Published date must be exact unzoned ISO YYYY-MM-DD.")
    return date.fromisoformat(text)


def read_design_rows(handle):
    """Date is inspected BEFORE any P&L conversion; future financial cells skip.

    CSV tokenization and full-file hashing do not constitute numeric evaluation.
    Financially invalid design rows remain explicit unknown rows in their original
    positions, veto SOURCE, and contaminate later rolling windows without dropping
    or compressing them. Bad/duplicate/unordered date metadata fails globally.
    """
    reader = csv.reader(handle)
    header = next(reader)
    if header != ["date", *LEG_COLUMNS]:
        raise ValueError("Exact date-first current19 roster/order required.")
    rows, issues = [], []
    excluded = Counter()
    previous = None
    all_rows = 0
    for record, raw in enumerate(reader, 2):
        all_rows += 1
        if not raw:
            raise ValueError("Empty published CSV record; cannot assign a completed book date.")
        day = parse_date(raw[0])
        if previous is not None and day <= previous:
            raise ValueError("Published date metadata must be globally unique and strictly increasing.")
        previous = day
        if not DESIGN_START <= day < DESIGN_END:
            excluded[str(day.year)] += 1
            # Do not check/convert/interrogate any out-of-design P&L field.
            continue
        row = dict(date=day, source_csv_record=record, source_id=BASELINE + ":csv:" + str(record),
            known=False, book=None, parent=None, issues=[])
        if len(raw) != 1 + len(LEG_COLUMNS):
            row["issues"].append("DESIGN_ROW_WIDTH_DIFFERS_FROM_CURRENT19_SCHEMA")
        else:
            values = []
            for field, text in zip(LEG_COLUMNS, raw[1:]):
                try:
                    values.append(decimal_fraction(text))
                except ValueError:
                    row["issues"].append("UNKNOWN_OR_NONFINITE_DESIGN_CELL:" + field)
            if not row["issues"]:
                row.update(known=True, book=sum(values, Fraction(0)), parent=values[0])
        issues += [dict(date=day.isoformat(), source_csv_record=record, issue=issue) for issue in row["issues"]]
        rows.append(row)
    gaps = [dict(previous_stored_date=a["date"].isoformat(), next_stored_date=b["date"].isoformat(),
        unrepresented_civil_dates=[(a["date"] + timedelta(days=i)).isoformat()
            for i in range(1, (b["date"] - a["date"]).days)],
        disposition="Observed stored-date gap only; no assumed closure/no-trade or inserted zero")
        for a, b in zip(rows, rows[1:]) if (b["date"] - a["date"]).days > 1]
    audit = dict(passed=not issues and bool(rows) and {row["date"].year for row in rows} == set(DESIGN_YEARS),
        input_header=list(header), exact_current19_roster_order=True, all_csv_date_records=all_rows,
        design_rows=len(rows), known_design_rows=sum(row["known"] for row in rows),
        unknown_design_rows=sum(not row["known"] for row in rows),
        first_design_date=rows[0]["date"].isoformat() if rows else None,
        last_design_date=rows[-1]["date"].isoformat() if rows else None,
        design_years=sorted({row["date"].year for row in rows}), issues=issues,
        excluded_date_metadata_rows_by_year=dict(excluded), excluded_financial_cells_numerically_converted=0,
        stored_date_gaps=gaps,
        observed_dated_book_rows_only=True, complete_exchange_calendar_verified=False,
        dropped_unknown_rows=0, forward_filled_rows=0, invented_2017_or_zero_warmup_rows=0,
        raw_prices_or_strategy_execution_read=False)
    return rows, audit


def calendar_audit(rows, calendar_callback):
    """Minimum FULL design cash-date coverage, with an injected source callback.

    This function itself imports no real schedule. Artificial fixtures supply
    artificial status callbacks; actual run_features supplies the committed
    codex_s03_calendar callback only after all code/input bindings are checked.
    Every observed book row is retained, including observed holiday rows.
    """
    present = {row["date"] for row in rows}
    if len(present) != len(rows) or any(not DESIGN_START <= day < DESIGN_END for day in present):
        raise ValueError("Calendar audit needs unique design-only stored book dates.")
    records, missing, extra = [], [], []
    day = DESIGN_START
    while day < DESIGN_END:
        status = dict(calendar_callback(day.isoformat()))
        if status.get("kind") not in {"normal", "early", "holiday", "weekend"}:
            raise ValueError("Bound calendar returned an unrecognized date classification.")
        expected = status["kind"] in {"normal", "early"}
        exists = day in present
        if expected and not exists:
            missing.append(day.isoformat())
        if exists and not expected:
            extra.append(day.isoformat())
        records.append(dict(date=day.isoformat(), calendar=status, stored_book_row_present=exists,
            normal_or_early_row_required=expected, passed=not expected or exists,
            observed_extra_holiday_row_retained=exists and not expected))
        day += timedelta(days=1)
    return dict(passed=not missing, performed=True,
        scope="Minimum stored-book coverage on all bound normal/early cash dates; not complete native-futures certification",
        full_start=DESIGN_START.isoformat(), full_end=(DESIGN_END - timedelta(days=1)).isoformat(),
        dates_checked=len(records), expected_normal_or_early_dates=sum(row["normal_or_early_row_required"] for row in records),
        stored_design_rows=len(rows), missing_expected_normal_or_early_dates=missing,
        extra_observed_non_normal_or_early_dates=extra, extra_actual_rows_retained_in_252_history=True,
        schedule_selects_or_drops_observed_history_rows=False, inserted_or_forward_filled_zero_rows=0,
        records=records, raw_prices_candidate_returns_or_execution_used=False)


def risk_from_window(window):
    """Exact sign of sample delta variance; caller supplies PREVIOUS rows only."""
    if len(window) != WINDOW or any(not row["known"] for row in window):
        return dict(known=False, reason="WARMUP" if len(window) < WINDOW else "UNKNOWN_PRIOR_ROW",
            qty_extra=0, qty_policy=1)
    n = len(window)
    sb = sum((row["book"] for row in window), Fraction(0))
    sx = sum((row["parent"] for row in window), Fraction(0))
    sbx = sum((row["book"] * row["parent"] for row in window), Fraction(0))
    sxx = sum((row["parent"] ** 2 for row in window), Fraction(0))
    centered_bx, centered_xx = n * sbx - sb * sx, n * sxx - sx * sx
    numerator = 2 * centered_bx + centered_xx
    denominator = n * (n - 1)
    if centered_xx < 0:
        raise AssertionError("Exact parent centered square sum cannot be negative.")
    extra = int(centered_xx > 0 and numerator < 0)
    return dict(known=True, reason="EXACT_NEGATIVE_DELTA_VARIANCE" if extra else
        "ZERO_PARENT_VARIANCE" if centered_xx == 0 else "NONNEGATIVE_DELTA_VARIANCE",
        n=n, centered_cross_numerator_exact=exact(centered_bx),
        centered_parent_square_numerator_exact=exact(centered_xx),
        delta_variance_sign_numerator_exact=exact(numerator),
        common_sample_denominator=denominator,
        sample_covariance_book_parent_exact=exact(centered_bx / denominator),
        sample_parent_variance_exact=exact(centered_xx / denominator),
        sample_delta_variance_exact=exact(numerator / denominator),
        units="published_proxy_USD_squared_per_daily_row", qty_extra=extra, qty_policy=1 + extra,
        baseline_already_includes_parent=True, shadow_baseline_not_policy_feedback=True,
        population_and_sample_sign_equivalent=True)


def compute_features(rows):
    """Current financial row is appended AFTER recording its pre-entry feature."""
    history = deque(maxlen=WINDOW)
    features = []
    for row in rows:
        risk = risk_from_window(history)
        previous = list(history)
        if previous and not previous[-1]["date"] < row["date"]:
            raise ValueError("Every feature observation must precede its decision date.")
        features.append(dict(feature_id=len(features), date=row["date"].isoformat(), year=row["date"].year,
            decision_time_civil_CT=row["date"].isoformat() + "T10:00:00[America/Chicago]",
            feature_known=risk["known"], **{key: value for key, value in risk.items() if key != "known"},
            previous_observed_rows=len(previous),
            window_start_date=previous[0]["date"].isoformat() if previous else None,
            window_end_date=previous[-1]["date"].isoformat() if previous else None,
            prior_source_ids=[item["source_id"] for item in previous],
            prior_unknown_source_ids=[item["source_id"] for item in previous if not item["known"]],
            current_or_future_financial_row_used=False, current_date_pnl_saved=False,
            qty_BASE_Q1=1, qty_CONST_Q2=2,
            parent_qualifying_signal_or_protected_ticket_established=False,
            actual_candidate_return_or_execution_computed=False))
        history.append(row)
    return features


def summarize_features(features):
    counts = []
    for year in ("2018-22", *map(str, DESIGN_YEARS)):
        selected = [row for row in features if year == "2018-22" or row["year"] == int(year)]
        counts.append(dict(period=year, observed_book_dates=len(selected),
            known_postwarmup_feature_days=sum(row["feature_known"] for row in selected),
            warmup_or_unknown_feature_days=sum(not row["feature_known"] for row in selected),
            EXTRA_potential_days=sum(row["qty_extra"] for row in selected),
            qty_policy_one_days=sum(row["qty_policy"] == 1 for row in selected),
            qty_policy_two_days=sum(row["qty_policy"] == 2 for row in selected),
            source_is_published_book_proxy=True, actual_parent_tickets_or_returns_counted=False))
    return counts


def feature_gate(features, source_audit):
    postwarmup = [row for row in features if row.get("previous_observed_rows", WINDOW) == WINDOW]
    known = [row for row in features if row["feature_known"]]
    active = [row for row in known if row["qty_extra"]]
    years = sorted({row["year"] for row in active})
    checks = dict(published_design_source_valid=source_audit["passed"],
        minimum_100_postwarmup_known_feature_days=len(known) >= MIN_KNOWN_FEATURE_DAYS,
        minimum_50_active_potential_feature_days=len(active) >= MIN_EXTRA_DAYS,
        minimum_3_active_design_years=len(years) >= MIN_EXTRA_YEARS,
        minimum_95percent_known_postwarmup=bool(postwarmup) and len(known) * 100 >= 95 * len(postwarmup),
        nonconstant_known_mask=0 < len(active) < len(known))
    passed = all(checks.values())
    return dict(phase="FEATURE_SUPPORT_upper_bound_only", passed=passed, checks=checks,
        known_postwarmup_feature_days=len(known), active_potential_feature_days=len(active), active_years=years,
        postwarmup_feature_days=len(postwarmup),
        known_postwarmup_fraction_exact=exact(Fraction(len(known), len(postwarmup))) if postwarmup else "0/1",
        source_rows=len(features), minimum_window_rows=WINDOW,
        raw_price_source_qualification_not_run=True, gross_screen_runs=0, economic_evaluations=0,
        new_candidate_profit_t_or_account_returns_computed=False,
        negative_covariance_identity_not_realized_risk_guarantee=True,
        scope="conditional published-shadow-book proxy; active days are an upper bound on first-signal dates",
        next_action="Independent actual FEATURE review and separate committed raw-price SOURCE admission required; no gross authorization yet"
            if passed else "Close H10 before raw prices/gross/economic tests; no parent/window/boundary/roster/source rescue")


def committed_binding(prereg):
    if git("branch", "--show-current").decode().strip() != "codex/work":
        raise ValueError("H10 stays on codex/work.")
    original = git("rev-parse", prereg).decode().strip()
    if re.fullmatch(r"[0-9a-f]{40}", original) is None:
        raise ValueError("Immutable full preregistration hash required.")
    subprocess.check_call(["git", "merge-base", "--is-ancestor", original, "HEAD"], cwd=ROOT)
    code = {}
    for name in (PLAN, EVIDENCE):
        if git("show", original + ":" + name) != (ROOT / name).read_bytes():
            raise ValueError("Frozen preregistration/evidence changed:" + name)
    for name in (*SOURCE_CODE, PLAN, EVIDENCE):
        current = sha(ROOT / name)
        if hashlib.sha256(git("show", "HEAD:" + name)).hexdigest() != current:
            raise ValueError("Commit exact code/source/prereg before actual features:" + name)
        code[name] = current
    return dict(prereg=original, implementation_commit=git("rev-parse", "HEAD").decode().strip(),
        code_sha256=code, adopted_source_pin=SOURCE_PIN,
        runtime=dict(python=sys.version, pandas=importlib.metadata.version("pandas"),
            numpy=importlib.metadata.version("numpy"), numba=importlib.metadata.version("numba"),
            financial_numeric_core="stdlib Decimal/Fraction; exact stored decimals"),
        source_identity=dict(primary_path=BASELINE, same_case_copy_path=BASELINE_COPY,
            expected_sha256_each=BASELINE_SHA256, fee_view="published native research1.24RT"),
        row_completion_contract="Prior completed dated published-book rows before nextVB10:00; conditional source assumption, not account receipt certification",
        limitations=LIMITATIONS)


def dump_once(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("x") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")


def csv_once(name, rows):
    with (OUT / name).open("x", newline="") as handle:
        if not rows:
            raise ValueError("Cannot save an unspecified empty CSV schema.")
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, separators=(",", ":")) if isinstance(value, (dict, list)) else value
                for key, value in row.items()})


def recheck(binding):
    for name, expected in binding["code_sha256"].items():
        if sha(ROOT / name) != expected:
            raise ValueError("Bound code/source changed during FEATURE execution:" + name)
    for inventory in binding.get("input_inventory", []):
        if (sha(ROOT / inventory["path"]) != inventory["sha256"]
                or (ROOT / inventory["path"]).stat().st_size != inventory["bytes"]):
            raise ValueError("Bound published baseline/copy changed during FEATURE execution.")


@contextmanager
def lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "feature.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def run_features(prereg):
    with lock():
        if any((directory / "feature_attempt.json").exists() for directory in
                (ROOT / "analysis/outputs").glob("codex_hunt_v2_vb_covariance*")):
            raise ValueError("Retained H10 FEATURE attempt exists; no unchanged rerun or alternate output directory.")
        binding = committed_binding(prereg)
        started = now()
        dump_once("feature_attempt.json", dict(started_utc=started, **binding,
            new_hypothesis_registered_by_script=False, gross_screen_runs=0, economic_evaluations=0,
            retry_authorized=False))
        names = ["feature_attempt.json"]
        source_audit = calendar = None
        mask_computed = counts_computed = False
        stage = "bind_primary_published_baseline_before_header_or_values"
        try:
            inventory = []
            for name in (BASELINE, BASELINE_COPY):
                path = ROOT / name
                if not path.is_file() or path.is_symlink():
                    raise ValueError("Frozen published baseline/copy missing/unexpected symlink.")
                inventory.append(dict(path=name, bytes=path.stat().st_size, sha256=sha(path)))
            binding["input_inventory"] = inventory
            dump_once("feature_pre_value_binding.json", dict(binding,
                input_header_or_financial_rows_interpreted=False, design_financial_years=list(DESIGN_YEARS),
                future_financial_values_authorized=False, raw_prices_or_execution_authorized=False))
            names.append("feature_pre_value_binding.json")
            if any(item["sha256"] != BASELINE_SHA256 for item in inventory):
                raise ValueError("Primary/copy published baseline SHA differs; no favorable file choice.")
            stage = "date_first_design_published_proxy_source_audit"
            with (ROOT / BASELINE).open(newline="") as handle:
                rows, source_audit = read_design_rows(handle)
            dump_once("feature_source_audit.json", source_audit)
            names.append("feature_source_audit.json")
            stage = "bound_full_design_normal_and_early_cash_date_coverage"
            cache = OUT / "cache/numba"
            cache.mkdir(parents=True, exist_ok=True)
            os.environ["NUMBA_CACHE_DIR"] = str(cache)
            # The real calendar transitively imports replica/grid/Numba. No
            # bytecode/cache can escape the declared Codex runtime subtree.
            sys.dont_write_bytecode = True
            if str(ROOT / "analysis") not in sys.path:
                sys.path.insert(0, str(ROOT / "analysis"))
            from codex_s03_calendar import calendar_status
            calendar = calendar_audit(rows, calendar_status)
            dump_once("feature_calendar_audit.json", calendar)
            names.append("feature_calendar_audit.json")
            if not source_audit["passed"] or not calendar["passed"]:
                gate = dict(phase="FEATURE_SUPPORT_upper_bound_only", passed=False,
                    status="SOURCE_REJECTED_BEFORE_FEATURES", stage=stage,
                    published_design_source_valid=source_audit["passed"],
                    minimum_cash_date_coverage_passed=calendar["passed"],
                    missing_expected_normal_or_early_dates=calendar["missing_expected_normal_or_early_dates"],
                    feature_mask_computed=False, feature_counts_computed=False,
                    new_candidate_profit_t_or_account_returns_computed=False,
                    raw_price_source_qualification_not_run=True, gross_screen_runs=0, economic_evaluations=0,
                    next_action="Close H10 at source rejection without feature masks or raw prices; no date deletion/zero insertion/rescue")
            else:
                stage = "exact_lagged_published_book_risk_features_and_upper_bound_counts"
                features = compute_features(rows)
                mask_computed = True
                counts = summarize_features(features)
                counts_computed = True
                gate = feature_gate(features, source_audit)
                gate.update(minimum_cash_date_coverage_passed=True, feature_mask_computed=True,
                    feature_counts_computed=True)
                dump_once("feature_rows.json", features)
                csv_once("feature_counts.csv", counts)
                names += ["feature_rows.json", "feature_counts.csv"]
        except Exception as error:
            if "feature_source_audit.json" not in names:
                source_audit = dict(passed=False, completed=False, stage=stage,
                    status="SOURCE_AUDIT_NOT_COMPLETED", numeric_or_date_source_exception=True,
                    feature_mask_computed=False, future_financial_values_converted=0)
                dump_once("feature_source_audit.json", source_audit)
                names.append("feature_source_audit.json")
            if "feature_calendar_audit.json" not in names:
                calendar = dict(passed=False, performed=False, stage=stage,
                    status="CALENDAR_AUDIT_NOT_COMPLETED", feature_mask_computed=False,
                    raw_prices_candidate_returns_or_execution_used=False)
                dump_once("feature_calendar_audit.json", calendar)
                names.append("feature_calendar_audit.json")
            gate = dict(phase="FEATURE_SUPPORT_upper_bound_only", passed=False,
                status="SOURCE_OR_IMPLEMENTATION_BLOCKED", stage=stage,
                exception_type=type(error).__name__, exception_message=str(error),
                published_design_source_valid=source_audit["passed"],
                minimum_cash_date_coverage_passed=calendar["passed"],
                feature_mask_computed=mask_computed, feature_counts_computed=counts_computed,
                new_candidate_profit_t_or_account_returns_computed=False, raw_price_source_qualification_not_run=True,
                gross_screen_runs=0, economic_evaluations=0, retry_authorized=False)
            dump_once("feature_exception.json", dict(gate, traceback=traceback.format_exc()))
            names.append("feature_exception.json")
        recheck(binding)
        dump_once("feature_gate.json", gate)
        dump_once("feature_input_binding.json", binding)
        names += ["feature_gate.json", "feature_input_binding.json"]
        marker = dict(started_utc=started, completed_utc=now(), phase="FEATURE_SUPPORT_upper_bound_only",
            passed=gate["passed"], prereg=binding["prereg"], implementation_commit=binding["implementation_commit"],
            code_sha256=binding["code_sha256"], artifacts_sha256={name: sha(OUT / name) for name in names},
            new_candidate_profit_t_or_account_returns_computed=False, gross_screen_runs=0, economic_evaluations=0,
            raw_prices_or_execution_read=False, raw_outcome_phase_authorized=False, retry_authorized=False,
            scope="conditional dated published-book risk proxy, not certified actual-account/native-equity risk",
            limitations=LIMITATIONS)
        dump_once("feature_verified_execution.json", marker)
        return gate


def invented_row(day, parent, book, record=0, known=True):
    return dict(date=day, known=known, parent=Fraction(parent) if known else None,
        book=Fraction(book) if known else None, source_csv_record=record, source_id="ARTIFICIAL:" + str(record), issues=[])


def fixtures():
    """Pure invented dates/observations only; no file/market/calendar access."""
    checks = []
    days = [date(2000, 1, 1) + timedelta(days=i) for i in range(WINDOW + 3)]
    x = [Fraction(i % 17 - 8, 10) for i in range(WINDOW)]
    negative = [invented_row(day, value, -value, i) for i, (day, value) in enumerate(zip(days, x))]
    r = risk_from_window(negative)
    assert r["known"] and r["qty_extra"] == 1
    assert Fraction(r["sample_delta_variance_exact"]) == -Fraction(r["sample_parent_variance_exact"])
    positive = [dict(row, book=row["parent"]) for row in negative]
    assert risk_from_window(positive)["qty_extra"] == 0
    checks.append("exact_covariance_identity_negative_and_positive_including_parent_in_baseline")
    boundary = [dict(row, book=-row["parent"] / 2) for row in negative]
    assert risk_from_window(boundary)["delta_variance_sign_numerator_exact"] == "0/1"
    assert risk_from_window(boundary)["qty_extra"] == 0
    flat_parent = [dict(row, parent=Fraction(0)) for row in negative]
    assert risk_from_window(flat_parent)["qty_extra"] == 0
    assert decimal_fraction("0.1") == Fraction(1, 10)
    assert risk_from_window(negative[:-1])["reason"] == "WARMUP"
    checks.append("strict_zero_boundary_zero_variance_no_epsilon_exact_decimals_and_252_warmup")
    complete = negative + [invented_row(days[WINDOW], 1, 1, WINDOW), invented_row(days[WINDOW + 1], 2, -2, WINDOW + 1)]
    original = compute_features(complete)
    poisoned = compute_features(negative + [invented_row(days[WINDOW], 10**12, 10**15, WINDOW),
        invented_row(days[WINDOW + 1], -10**14, 10**18, WINDOW + 1)])
    assert original[:WINDOW + 1] == poisoned[:WINDOW + 1]
    assert original[WINDOW]["window_end_date"] == days[WINDOW - 1].isoformat()
    assert original[WINDOW + 1]["window_start_date"] == days[1].isoformat()
    assert all(row["qty_extra"] == 0 for row in original[:WINDOW])
    checks.append("current_and_future_poison_excluded_previous_rows_only_and_one_row_window_shift")
    invalid = negative.copy()
    invalid[100] = invented_row(days[100], 0, 0, 100, known=False)
    a = compute_features(invalid + [invented_row(days[WINDOW], 1, 1, WINDOW)])
    assert not a[-1]["feature_known"] and a[-1]["qty_extra"] == 0
    assert a[-1]["prior_unknown_source_ids"] == ["ARTIFICIAL:100"]
    all_zero_days_kept = negative.copy()
    all_zero_days_kept[100] = invented_row(days[100], 0, 0, 100)
    z = compute_features(all_zero_days_kept + [invented_row(days[WINDOW], 1, 1, WINDOW)])
    assert z[-1]["feature_known"] and len(z[-1]["prior_source_ids"]) == WINDOW
    checks.append("unknown_rows_not_dropped_or_compressed_and_known_zero_no_trade_days_retained")
    text = io.StringIO()
    writer = csv.writer(text)
    writer.writerow(["date", *LEG_COLUMNS])
    writer.writerow(["2018-01-02", *(["0.1"] * len(LEG_COLUMNS))])
    writer.writerow(["2018-01-03", "NaN", *(["0"] * (len(LEG_COLUMNS) - 1))])
    writer.writerow(["2023-01-02", *(["FUTURE_PNL_MUST_NOT_CONVERT"] * len(LEG_COLUMNS))])
    rows, audit = read_design_rows(io.StringIO(text.getvalue()))
    assert len(rows) == 2 and rows[0]["book"] == Fraction(19, 10) and not rows[1]["known"]
    assert audit["excluded_financial_cells_numerically_converted"] == 0 and not audit["passed"]
    assert audit["excluded_date_metadata_rows_by_year"] == {"2023": 1}
    checks.append("exact_schema_date_first_future_numeric_poison_skip_and_invalid_design_global_veto")
    artificial = [dict(feature_known=True, qty_extra=int(i < 50), year=2018 + i % 3) for i in range(100)]
    assert feature_gate(artificial, {"passed": True})["passed"]
    assert not feature_gate([dict(row, qty_extra=0) for row in artificial], {"passed": True})["passed"]
    assert not feature_gate([dict(row, qty_extra=1) for row in artificial], {"passed": True})["passed"]
    assert not feature_gate(artificial, {"passed": False})["passed"]
    checks.append("frozen_upper_bound_50_active_3_years_100_known_nonconstant_and_source_veto")
    fake_rows = [invented_row(date(2018, 1, i), 1, -1, i) for i in (2, 3, 4)]
    fake_calendar = lambda day: dict(kind="normal" if day == "2018-01-02" else
        "early" if day == "2018-01-03" else "holiday", cash_close_j=900 if day == "2018-01-02" else
        720 if day == "2018-01-03" else None, reason="ARTIFICIAL_FIXTURE_ONLY")
    covered = calendar_audit(fake_rows, fake_calendar)
    assert covered["passed"] and covered["expected_normal_or_early_dates"] == 2
    assert covered["extra_observed_non_normal_or_early_dates"] == ["2018-01-04"]
    assert len(fake_rows) == 3 and covered["extra_actual_rows_retained_in_252_history"]
    missing_normal = calendar_audit(fake_rows[1:], fake_calendar)
    missing_early = calendar_audit([fake_rows[0], fake_rows[2]], fake_calendar)
    assert missing_normal["missing_expected_normal_or_early_dates"] == ["2018-01-02"]
    assert missing_early["missing_expected_normal_or_early_dates"] == ["2018-01-03"]
    assert not missing_normal["passed"] and not missing_early["passed"]
    assert covered["dates_checked"] == (DESIGN_END - DESIGN_START).days
    checks.append("injected_artificial_full_date_calendar_normal_early_missing_veto_extra_holiday_rows_retained")
    return dict(passed=True, groups=len(checks), checks=checks, actual_owned_input_or_calendar_accessed=False,
        new_candidate_profit_t_or_account_returns_computed=False, gross_screen_runs=0, economic_evaluations=0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fixtures", action="store_true")
    mode.add_argument("--features", action="store_true")
    parser.add_argument("--prereg")
    arguments = parser.parse_args()
    if arguments.fixtures:
        print(json.dumps(fixtures(), allow_nan=False))
    else:
        if not arguments.prereg:
            parser.error("--features requires original committed --prereg hash")
        print(json.dumps(run_features(arguments.prereg), allow_nan=False))
