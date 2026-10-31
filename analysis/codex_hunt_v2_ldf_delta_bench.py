"""Hunt v2 H01: frozen, DESIGN-ONLY personal19 comparison.

No financial file is opened at import or by --fixtures. Financial execution
requires an explicit root authorization, committed implementation, and a passed
design gate whose complete artifact inventory is bound by its success marker.
This is an uncapped daily personal-book comparison, never an Apex path result.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date, datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "analysis"))
CACHE = ROOT / "analysis/outputs/codex_hunt_v2_ldf_delta/cache/numba"
os.environ["NUMBA_CACHE_DIR"] = str(CACHE)

import numpy as np
import pandas as pd
import codex_anson_personal as SHARED
import metrics as METRICS
import resampling as RESAMPLING

PLAN = "agents/codex/plans/hunt_v2_ldf_delta_confirmation.md"
PREREG = "aa726e2"
SOURCE_PINS = ("afde088b8b64cf939ff1b325a27eea041cf62c70", "92b1d4cde768bcfce019cf9a95944158dd0ebba3")
BASELINE_COMMIT = "63f557da51f8348b1779f0dd44259aff8c2d01df"
BASELINE = "analysis/outputs/codex_rebound/personal19/UNIFORM/fee_1.24/baseline_daily19.csv"
BASELINE_COPY = "analysis/outputs/codex_rebound/personal19/SUNDAY2/fee_1.24/baseline_daily19.csv"
SNAPSHOT = "agents/codex/inputs/rebound/plan_update_afde088"
CONTEXT = ("analysis/personal_portfolio.py", "analysis/personal_variants.py",
           "personal_strategies/PORTFOLIO.md", "funded_strategies/FUNDED_PLAN.md")
DEPENDENCIES = ("analysis/codex_anson_personal.py", "analysis/metrics.py", "analysis/resampling.py", "analysis/montecarlo.py")
COLUMNS = ("VaultBreak", "OvernightBiasML", "MondayLong", "ExpirationOpenShort", "LateDayFlow", "NFPFade",
           "BridgeMondayLong", "CLSundayFade_perMCL", "ESMOCFollow_perMES", "RelativeStrength", "FC2B",
           "TwinContinuation", "OvernightTick", "DualThrust", "Kusho", "S47", "S30", "SwingTarget", "PaperTrend")
MODELS = ("BASE", "LEGACY", "STRICT30")
ROWS = ("BASE", "ADD", "EMPTY", "REPLACE")
MC_N, MC_HORIZON, MC_BLOCK, MC_SEED = 5000, 252, 20, 20261026
FEE, SLIP, TOL = 1.24, 0.50, 1e-6
END = date(2022, 12, 31)
DEFAULT_OUT = ROOT / "analysis/outputs/codex_hunt_v2_ldf_delta/bench_design"
LIMITS = [
    "Personal baseline preserves published daily marks, not intraday margin/liquidation or an Apex account path.",
    "Core baseline commissions are per nonzero P&L day; some reentry fees are undercounted. MOC/S30 inherit fee approximations.",
    "Twin is the marked v1 checker ledger, not an exact v2.1 ledger; Kusho is booked on exit. These mark uncertainties are not quantified here.",
    "Candidate native commission/slippage is checked independently. NQ price observations still do not establish native MNQ listing, fills, spread or receipt.",
    "The retained OT baseline ends2026-07-07. This design-only comparison ends2022; it manufactures no later complete-book history.",
    "A positive point utility condition is UNRESOLVED without source parity and quantified baseline fee/mark uncertainty; it is not trading approval.",
]


class Unresolved(ValueError):
    """A benchmark cannot be qualified from incomplete or inconsistent inputs."""


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def sha(path: Path | str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def blob(body: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_output(path: Path | str) -> Path:
    path = Path(path).resolve()
    if not path.is_relative_to((ROOT / "analysis/outputs").resolve()) or not path.relative_to(ROOT / "analysis/outputs").parts[0].startswith("codex_"):
        raise ValueError("Output must stay in analysis/outputs/codex_*")
    return path


def write_once(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(content)


def json_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, allow_nan=False, default=str) + "\n").encode()


def finite_json(value):
    if isinstance(value, dict):
        return {k: finite_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [finite_json(v) for v in value]
    if isinstance(value, (np.floating, float)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def read_design_rows(stream, required, *, stop_at_future=False):
    """Validate date before converting any financial field; never evaluate2023+."""
    reader = csv.DictReader(stream)
    if reader.fieldnames is None or not set(required) <= set(reader.fieldnames):
        raise Unresolved("Missing required source columns: " + ",".join(required))
    rows = []
    for row in reader:
        stamp = date.fromisoformat(row["date"])
        if stamp > END:
            if stop_at_future:
                break
            raise Unresolved("Future candidate/calendar row is forbidden in design bench")
        if stamp < date(2018, 1, 1):
            continue
        rows.append((pd.Timestamp(stamp), row))
    return rows


def bool_value(value: str) -> bool:
    if str(value).lower() in ("true", "1"):
        return True
    if str(value).lower() in ("false", "0"):
        return False
    raise Unresolved("Nonliteral calendar boolean")


def metadata_bindings() -> dict:
    """Hashes/header/source objects only; no financial CSV values are parsed."""
    body = (ROOT / BASELINE).read_bytes()
    if body != (ROOT / BASELINE_COPY).read_bytes():
        raise Unresolved("Retained current19 baseline copies differ")
    if blob(body) != git("rev-parse", BASELINE_COMMIT + ":" + BASELINE).decode().strip():
        raise Unresolved("Baseline differs from its committed artifact")
    with (ROOT / BASELINE).open(newline="") as stream:
        if tuple(next(csv.reader(stream))) != ("date", *COLUMNS):
            raise Unresolved("Current19 baseline header changed")
    manifest_path = ROOT / SNAPSHOT / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if manifest["reference"] != SOURCE_PINS[0]:
        raise Unresolved("Wrong current19 source pin")
    bindings = {BASELINE: hashlib.sha256(body).hexdigest(), BASELINE_COPY: sha(ROOT / BASELINE_COPY),
                str(manifest_path.relative_to(ROOT)): sha(manifest_path)}
    for rel in CONTEXT:
        earlier, current = (git("show", pin + ":" + rel) for pin in SOURCE_PINS)
        if earlier != current:
            raise Unresolved("Adopted source changed since afde088: " + rel)
        saved = ROOT / SNAPSHOT / rel
        if saved.read_bytes() != earlier or sha(saved) != manifest["files"][rel]["sha256"]:
            raise Unresolved("Retained source context changed: " + rel)
        bindings[str(saved.relative_to(ROOT))] = sha(saved)
    return bindings


def authorize(args) -> tuple[dict, dict, dict]:
    if not args.authorize_design_pass:
        raise PermissionError("Explicit root design-pass authorization is required before financial reads")
    if git("branch", "--show-current").decode().strip() != "codex/work":
        raise PermissionError("Work only on codex/work")
    prereg = git("rev-parse", args.prereg).decode().strip()
    if prereg != git("rev-parse", PREREG).decode().strip() or git("show", prereg + ":" + PLAN) != (ROOT / PLAN).read_bytes():
        raise PermissionError("Frozen preregistration changed")
    if not args.implementation_commit:
        raise PermissionError("Root must freeze/commit this bench before execution")
    for rel in (str(Path(__file__).relative_to(ROOT)), *DEPENDENCIES):
        if git("show", args.implementation_commit + ":" + rel) != (ROOT / rel).read_bytes():
            raise PermissionError("Uncommitted implementation/dependency: " + rel)
    gate_path, marker_path = Path(args.design_gate).resolve(), Path(args.design_marker).resolve()
    if gate_path.parent != marker_path.parent:
        raise PermissionError("Gate and marker must share the frozen design directory")
    gate, marker = json.loads(gate_path.read_text()), json.loads(marker_path.read_text())
    if marker.get("phase") != "design" or not marker.get("design_passed", marker.get("passed", False)) or not gate.get("design_passed", gate.get("passed", False)):
        raise PermissionError("A completed passed design gate is required")
    artifacts = marker.get("artifacts_sha256")
    if not isinstance(artifacts, dict) or artifacts.get(gate_path.name) != sha(gate_path):
        raise PermissionError("Design gate is not bound by the success marker")
    for name, expected in artifacts.items():
        path = (marker_path.parent / name).resolve()
        if not path.is_relative_to(marker_path.parent) or sha(path) != expected:
            raise PermissionError("Design artifact hash mismatch: " + name)
    for name, raw_path in (("design_daily.csv", args.candidate_daily), ("design_calendar_audit.csv", args.calendar),
                           ("design_BASE_trades.csv", args.base_trades), ("design_STRICT30_trades.csv", args.strict_trades)):
        path = Path(raw_path).resolve()
        if path != marker_path.parent / name or artifacts.get(name) != sha(path):
            raise PermissionError("Bench input is not the exact marker-bound " + name)
    schema = marker.get("daily_schema", {})
    if schema.get("net_unit") != "USD per 1 MNQ" or schema.get("commission_rt") != FEE or schema.get("slippage_per_market_stop_fill") != SLIP:
        raise PermissionError("Design daily unit/cost metadata is missing or different")
    start, end = date.fromisoformat(marker["warmup_first_eligible_date"]), date.fromisoformat(marker["design_last_date"])
    if not date(2018, 1, 1) <= start <= end <= END:
        raise PermissionError("Invalid frozen design/warmup clock")
    bindings = metadata_bindings()
    for rel in (PLAN, str(Path(__file__).relative_to(ROOT)), *DEPENDENCIES):
        bindings[rel] = sha(ROOT / rel)
    for path in (gate_path, marker_path, Path(args.candidate_daily), Path(args.calendar), Path(args.base_trades), Path(args.strict_trades)):
        bindings[str(path.relative_to(ROOT))] = sha(path)
    return gate, marker, bindings


def load_inputs(args, marker) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    start, end = pd.Timestamp(marker["warmup_first_eligible_date"]), pd.Timestamp(marker["design_last_date"])
    with (ROOT / BASELINE).open(newline="") as stream:
        rows = read_design_rows(stream, ("date", *COLUMNS), stop_at_future=True)
    baseline = pd.DataFrame([{k: float(r[k]) for k in COLUMNS} for d, r in rows if start <= d <= end],
                            index=pd.DatetimeIndex([d for d, _ in rows if start <= d <= end], name="date"))
    with Path(args.candidate_daily).open(newline="") as stream:
        rows = read_design_rows(stream, ("date", *MODELS))
    replay = pd.DataFrame([{k: float(r[k]) for k in MODELS} for _, r in rows],
                          index=pd.DatetimeIndex([d for d, _ in rows], name="date"))
    for frame in (baseline, replay):
        if frame.empty or frame.index.has_duplicates or not frame.index.is_monotonic_increasing or not np.isfinite(frame.to_numpy()).all():
            raise Unresolved("Unordered, duplicated, empty or nonfinite daily input")
    if replay.index.min() < start or replay.index.max() > end:
        raise Unresolved("Daily file differs from declared warmup/design window")
    with Path(args.calendar).open(newline="") as stream:
        rows = read_design_rows(stream, ("date", "cash_day", "included_in_design_daily"))
    calendar = {}
    for d, row in rows:
        if d in calendar:
            raise Unresolved("Duplicate processed calendar date")
        calendar[d] = {k: bool_value(row[k]) for k in ("cash_day", "included_in_design_daily")}
    expected_rows = {d for d, flags in calendar.items() if flags["included_in_design_daily"]}
    if expected_rows != set(replay.index):
        raise Unresolved("Daily file does not match its processed calendar inclusion proof")
    extra = replay.index.difference(baseline.index)
    if (np.abs(replay.loc[extra, list(MODELS)].to_numpy()) > TOL).any():
        raise Unresolved("Nonzero candidate day has no published book date")
    proven_zero = []
    for d in baseline.index.difference(replay.index):
        if d not in calendar or calendar[d]["cash_day"]:
            raise Unresolved("Missing maker observation for a book day; no silent zero fill: " + str(d.date()))
        proven_zero.append(d)
    if proven_zero:
        replay = pd.concat([replay, pd.DataFrame(0.0, index=proven_zero, columns=MODELS)]).sort_index()
    replay = replay.reindex(baseline.index)
    if replay.isna().any().any():
        raise Unresolved("Alignment created an unproven zero")
    return baseline, replay, dict(days=len(baseline), first=str(baseline.index.min().date()),
                                 last=str(baseline.index.max().date()), explicit_closed_cash_zero_dates=[str(d.date()) for d in proven_zero],
                                 zero_only_maker_dates_outside_book=[str(d.date()) for d in extra],
                                 coverage_basis="All published book dates after declared warmup; noneligible candidate dates remain proven zeros")


def load_checked_trades(path: Path | str) -> pd.DataFrame:
    required = ("date", "event_id", "side", "entry", "exit", "gross_points", "fill_count", "net_mnq")
    with Path(path).open(newline="") as stream:
        rows = read_design_rows(stream, required)
    out = []
    for d, row in rows:
        numeric = {k: float(row[k]) for k in required if k not in ("date", "event_id")}
        if not all(np.isfinite(v) for v in numeric.values()):
            raise Unresolved("Nonfinite candidate ledger")
        if numeric["side"] not in (-1, 1) or numeric["fill_count"] != 2:
            raise Unresolved("Frozen one-micro/two-market-fill execution differs")
        gross = (numeric["exit"] - numeric["entry"]) * numeric["side"]
        if abs(gross - numeric["gross_points"]) > TOL or abs(gross * 2 - FEE - SLIP * numeric["fill_count"] - numeric["net_mnq"]) > TOL:
            raise Unresolved("Candidate native commission/slippage does not reconcile")
        out.append(dict(date=d, event_id=str(row["event_id"]), **numeric))
    frame = pd.DataFrame(out, columns=required)
    if frame.event_id.duplicated().any() or frame.date.duplicated().any():
        raise Unresolved("Frozen one-trade/day ledger has duplicate IDs/dates")
    return frame


def check_candidate_money(base: pd.DataFrame, strict: pd.DataFrame, replay: pd.DataFrame) -> dict:
    if not set(strict.event_id) <= set(base.event_id):
        raise Unresolved("STRICT30 is not a subset of canonical BASE tickets")
    lookup = base.set_index("event_id")
    for row in strict.itertuples(index=False):
        source = lookup.loc[row.event_id]
        if source.date != row.date or any(abs(float(source[k]) - getattr(row, k)) > TOL for k in ("side", "entry", "exit", "gross_points", "fill_count", "net_mnq")):
            raise Unresolved("Shared filter ticket changed its execution/fees")
    for key, trades in (("BASE", base), ("STRICT30", strict)):
        daily = trades.groupby("date").net_mnq.sum().reindex(replay.index, fill_value=0.0)
        if len(trades[~trades.date.isin(replay.index)]) or not np.allclose(daily, replay[key], rtol=0, atol=TOL):
            raise Unresolved("Ledger-to-daily reconciliation failed: " + key)
    return dict(base_trades=len(base), strict_trades=len(strict), strict_exact_execution_subset=True,
                commission_rt=FEE, slippage_per_market_stop_fill=SLIP, contract_quantity=1,
                base_net=float(base.net_mnq.sum()), strict_net=float(strict.net_mnq.sum()))


def build_portfolios(frame: pd.DataFrame, replay: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    total = frame.sum(axis=1)
    published = frame["LateDayFlow"]
    strict = replay["STRICT30"]
    plans = dict(BASE=total, ADD=total + strict, EMPTY=total - published, REPLACE=total - published + strict)
    parity = pd.DataFrame(dict(published_ldf=published, replay_base=replay["BASE"], strict=strict,
                               implementation_delta=replay["BASE"] - published,
                               filter_delta=strict - replay["BASE"], replacement_delta=strict - published))
    np.testing.assert_allclose(parity.replacement_delta, parity.implementation_delta + parity.filter_delta, atol=TOL, rtol=0)
    np.testing.assert_allclose(plans["REPLACE"] - plans["BASE"], parity.replacement_delta, atol=TOL, rtol=0)
    return plans, parity


def ratio(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator > 0 else float("nan")


def historical(values) -> dict:
    x = np.asarray(values, float)
    result = METRICS.perf(x)
    dd = RESAMPLING.max_dd(x)
    # Shared max_dd includes initial zero; preserve that basis for utility gates.
    result.update(total=float(x.sum()), days=len(x), annual=float(x.mean() * 252),
                  initial_zero_max_dd=dd, historical_return_dd=ratio(x.mean() * 252, dd),
                  initial_zero_calmar=ratio(x.mean() * 252, dd))
    return result


def point_utility(summary: dict) -> dict:
    result = {}
    for name in ("ADD", "REPLACE"):
        comparisons = {}
        for reference in ("BASE", "EMPTY"):
            margins = {key: summary[name][key] - summary[reference][key]
                       for key in ("historical_return_dd", "median_mc_return_dd")}
            comparisons[reference] = dict(margins=margins, passed=all(np.isfinite(v) and v > 0 for v in margins.values()))
        result[name] = dict(comparisons=comparisons, passed=all(v["passed"] for v in comparisons.values()))
    return result


def benchmark(plans: dict, parity: pd.DataFrame) -> tuple[dict, pd.DataFrame, dict, dict, np.ndarray]:
    days = next(iter(plans.values())).index
    idx = SHARED.histories(len(days), n=MC_N, horizon=MC_HORIZON, block=MC_BLOCK, seed=MC_SEED)
    simulations, summary = {}, {}
    for name, series in plans.items():
        profit, dd = SHARED.simulate_daily(series.to_numpy(), idx)
        simulations[name] = (profit, dd)
        summary[name] = dict(**historical(series), mc_profit_p5=float(np.quantile(profit, .05)),
                             mc_profit_p50=float(np.median(profit)), mc_profit_p95=float(np.quantile(profit, .95)),
                             mc_dd_p50=float(np.median(dd)), mc_dd_p95=float(np.quantile(dd, .95)),
                             median_mc_return_dd=ratio(np.median(profit), np.median(dd)),
                             p_losing_year=float(np.mean(profit <= 0)))
    paired = []
    for name in ("ADD", "REPLACE"):
        for reference in ("BASE", "EMPTY"):
            p, dd = simulations[name]
            bp, bdd = simulations[reference]
            lo, hi = SHARED.paired_mean_interval(p - bp, seed=MC_SEED, n=MC_N)
            dlo, dhi = SHARED.paired_mean_interval(dd - bdd, seed=MC_SEED, n=MC_N)
            alo, ahi = SHARED.historical_annual_effect_interval((plans[name] - plans[reference]).to_numpy(),
                                                               seed=MC_SEED, n=MC_N, block=MC_BLOCK)
            paired.append(dict(config=name, reference=reference, mean_annual_profit_delta=float((p - bp).mean()),
                               paired_mc_mean_delta_95_lo=float(lo), paired_mc_mean_delta_95_hi=float(hi),
                               mean_dd_delta=float((dd - bdd).mean()), paired_mc_dd_delta_95_lo=float(dlo),
                               paired_mc_dd_delta_95_hi=float(dhi), historical_annual_delta_95_lo=float(alo),
                               historical_annual_delta_95_hi=float(ahi),
                               historical_return_dd_margin=summary[name]["historical_return_dd"] - summary[reference]["historical_return_dd"],
                               median_mc_return_dd_margin=summary[name]["median_mc_return_dd"] - summary[reference]["median_mc_return_dd"]))
    # A nonselectable reference diagnostic separates book implementation changes
    # from the STRICT-minus-replayed-BASE filter delta. It cannot nominate a rule.
    diagnostic = plans["BASE"] + parity.implementation_delta
    p, dd = SHARED.simulate_daily(diagnostic.to_numpy(), idx)
    ref_effect = dict(nonselectable=True, historical=historical(diagnostic),
                      median_mc_return_dd=ratio(np.median(p), np.median(dd)),
                      total_implementation_delta=float(parity.implementation_delta.sum()),
                      total_filter_delta=float(parity.filter_delta.sum()),
                      total_replacement_delta=float(parity.replacement_delta.sum()),
                      daily_parity_mismatches=int((parity.implementation_delta.abs() > TOL).sum()),
                      max_abs_daily_implementation_delta=float(parity.implementation_delta.abs().max()))
    return summary, pd.DataFrame(paired), simulations, ref_effect, idx


def disposition(point, parity_established: bool) -> dict:
    passed = any(row["passed"] for row in point.values())
    if not passed:
        return dict(status="FAIL", point_utility_passed=False, continue_to_validation=False,
                    reason="Neither frozen ADD nor REPLACE beats both BASE and EMPTY on historical and median-MC return/DD.")
    return dict(status="UNRESOLVED", point_utility_passed=True, continue_to_validation=False,
                reason=("Canonical BASE does not reproduce the published LDF slot; implementation/parity gain is not filter alpha. "
                        if not parity_established else "") +
                       "Published baseline fee/reentry/mark uncertainty is not quantitatively bounded by this bench; positive point utility alone cannot clear it.")


def run(args) -> dict:
    out = safe_output(args.out)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError("Preserve retained bench outputs; choose no overwrite/retry after success")
    for directory in (ROOT / "analysis/outputs").glob("codex_hunt_v2_ldf_delta*"):
        if any(directory.rglob("bench_design_verified_execution.json")):
            raise PermissionError("A completed H01 design bench already exists; do not rerun selection")
    gate, marker, bindings = authorize(args)
    started = utcnow()
    frame, replay, calendar = load_inputs(args, marker)
    base, strict = load_checked_trades(args.base_trades), load_checked_trades(args.strict_trades)
    money = check_candidate_money(base, strict, replay)
    plans, parity = build_portfolios(frame, replay)
    summary, pairs, sims, ref_effect, idx = benchmark(plans, parity)
    point = point_utility(summary)
    parity_ok = ref_effect["daily_parity_mismatches"] == 0
    decision = disposition(point, parity_ok)
    result = dict(**decision, point_tests=point, canonical_published_ldf_parity_established=parity_ok,
                  baseline_uncertainty_quantified=False, native_candidate_money=money, common_calendar=calendar,
                  mc=dict(draws=MC_N, horizon=MC_HORIZON, block=MC_BLOCK, seed=MC_SEED,
                          convention="codex_anson_personal.histories/simulate_daily; repo noncircular20-day blocks",
                          ratio="median annual profit / median maximum drawdown; historical annual profit / initial-zero DD"),
                  phase="design_only", selected_candidate="STRICT30", benchmark_rows=list(ROWS),
                  new_economic_configurations=0, validation_or_apex_claim=False, limitations=LIMITS)
    if any(sha(ROOT / name) != expected for name, expected in bindings.items()):
        raise RuntimeError("Bound input/implementation changed during financial execution; no success marker written")
    out.mkdir(parents=True, exist_ok=False)
    buffers = {"portfolio_daily.csv": pd.DataFrame(plans).to_csv(index_label="date").encode(),
               "replay_slot_parity.csv": parity.to_csv(index_label="date").encode(),
               "bench_summary.csv": pd.DataFrame(summary).T.to_csv(index_label="config").encode(),
               "paired_effects.csv": pairs.to_csv(index=False).encode(),
               "reference_replay_diagnostic.json": json_bytes(finite_json(ref_effect)),
               "bench_gate.json": json_bytes(finite_json(result))}
    for name, body in buffers.items():
        write_once(out / name, body)
    np.save(out / "paired_histories.npy", idx)
    np.savez_compressed(out / "paired_portfolio_paths.npz", **{name + "__" + field: values[i]
        for name, values in sims.items() for i, field in enumerate(("profit", "drawdown"))})
    artifacts = {p.name: sha(p) for p in out.iterdir() if p.is_file()}
    success = dict(started_utc=started, completed_utc=utcnow(), phase="design_personal_bench", status=decision["status"],
                   prereg=args.prereg, implementation_commit=args.implementation_commit,
                   root_design_pass_authorized=True, candidate_design_marker_sha256=sha(args.design_marker),
                   input_bindings=bindings, artifacts_sha256=artifacts, no_2023_candidate_values_evaluated=True,
                   baseline_source_pins=list(SOURCE_PINS), baseline_artifact_commit=BASELINE_COMMIT,
                   financial_benchmark_completed=True, no_promotion_or_apex_claim=True)
    write_once(out / "bench_design_verified_execution.json", json_bytes(success))
    return result


def fixtures() -> dict:
    checks = []
    columns = ("date", "BASE", "LEGACY", "STRICT30")
    future = io.StringIO("date,BASE,LEGACY,STRICT30\n2022-12-30,1,1,1\n2023-01-03,not-a-number,not-a-number,not-a-number\n")
    try:
        read_design_rows(future, columns)
    except Unresolved as exc:
        assert "Future" in str(exc)
        checks.append("future_candidate_rejected_before_float_conversion")
    else:
        raise AssertionError("Future candidate admitted")
    rows = read_design_rows(io.StringIO("date,X\n2022-12-30,1\n2023-01-03,not-a-number\n"), ("date", "X"), stop_at_future=True)
    assert len(rows) == 1 and float(rows[0][1]["X"]) == 1
    checks.append("baseline_stream_stops_before_future_financial_conversion")
    days = pd.date_range("2020-01-01", periods=260)
    frame = pd.DataFrame(0.0, index=days, columns=COLUMNS)
    frame["VaultBreak"] = np.where(np.arange(260) % 4 == 0, -3.0, 4.0)
    frame["LateDayFlow"] = np.where(np.arange(260) % 3 == 0, -2.0, 1.0)
    replay = pd.DataFrame({key: frame.LateDayFlow.copy() for key in MODELS})
    replay["STRICT30"] = np.where(frame.LateDayFlow < 0, 0.0, frame.LateDayFlow)
    portfolios, audit = build_portfolios(frame, replay)
    assert np.allclose(portfolios["EMPTY"], frame.VaultBreak)
    assert np.allclose(portfolios["REPLACE"] - portfolios["BASE"], audit.filter_delta)
    checks.append("whole_micro_add_replace_empty_decomposition")
    replay["BASE"] += 2
    _, changed = build_portfolios(frame, replay)
    assert np.allclose(changed.replacement_delta, changed.filter_delta + changed.implementation_delta)
    assert (changed.implementation_delta.abs() > TOL).all()
    checks.append("implementation_difference_not_mislabelled_filter_profit")
    idx = SHARED.histories(260, n=31, horizon=40, block=5, seed=MC_SEED)
    profit, dd = SHARED.simulate_daily(frame.VaultBreak.to_numpy(), idx)
    import montecarlo as MC
    reference = MC.daily_mc(frame.VaultBreak.to_numpy(), horizon=40, n=31, block=5, seed=MC_SEED)
    assert np.isclose(np.median(profit), reference["pnl_p50"])
    assert np.isclose(np.median(dd), reference["dd_p50"])
    checks.append("shared_history_engine_matches_repo_montecarlo")
    assert np.array_equal(idx, SHARED.histories(260, n=31, horizon=40, block=5, seed=MC_SEED))
    checks.append("identical_paired_history_indices")
    assert np.isclose(RESAMPLING.max_dd([-5, 3]), 5)
    assert not np.isfinite(ratio(1, 0))
    checks.append("initial_zero_drawdown_and_no_infinite_utility_pass")
    sample = {name: dict(historical_return_dd=1.0, median_mc_return_dd=1.0) for name in ROWS}
    sample["ADD"] = dict(historical_return_dd=1.1, median_mc_return_dd=1.1)
    point = point_utility(sample)
    assert point["ADD"]["passed"]
    assert disposition(point, False)["status"] == "UNRESOLVED"
    assert disposition(point, True)["status"] == "UNRESOLVED"
    sample["ADD"]["median_mc_return_dd"] = .9
    assert disposition(point_utility(sample), True)["status"] == "FAIL"
    checks.append("strict_both_references_both_ratios_and_uncertainty_veto")
    class Args:
        authorize_design_pass = False
    try:
        authorize(Args())
    except PermissionError:
        checks.append("root_gate_blocks_before_financial_reads")
    else:
        raise AssertionError("Unauthorised read path")
    return dict(passed=True, checks=checks, private_financial_inputs_opened=False,
                script_sha256=sha(Path(__file__)), command="--fixtures", new_return_trials=0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", action="store_true")
    parser.add_argument("--authorize-design-pass", action="store_true")
    parser.add_argument("--prereg", default=PREREG)
    parser.add_argument("--implementation-commit")
    parser.add_argument("--candidate-daily", type=Path)
    parser.add_argument("--calendar", type=Path)
    parser.add_argument("--design-gate", type=Path)
    parser.add_argument("--design-marker", type=Path)
    parser.add_argument("--base-trades", type=Path)
    parser.add_argument("--strict-trades", type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    if args.fixtures:
        result = fixtures()
        path = ROOT / "analysis/outputs/codex_hunt_v2_ldf_delta" / ("bench_synthetic_checks_" + result["script_sha256"][:12] + ".json")
        body = json_bytes(result)
        if path.exists():
            if path.read_bytes() != body:
                raise ValueError("Different retained synthetic artifact")
        else:
            write_once(path, body)
        print(json.dumps(result))
        return
    required = ("candidate_daily", "calendar", "design_gate", "design_marker", "base_trades", "strict_trades")
    if any(getattr(args, name) is None for name in required):
        parser.error("Financial execution needs all bound design inputs and explicit authorization")
    print(json.dumps(finite_json(run(args))))


if __name__ == "__main__":
    main()
