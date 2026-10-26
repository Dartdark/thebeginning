"""Hunt v2 H02: DESIGN-ONLY current personal19 FVB-short bench.

Import and --fixtures never open market data or private financial CSVs.
Financial execution requires root's explicit design-pass authorization, a
committed H02 preregistration and implementation, and verified design artifacts.
The four fixed whole-micro rows are conditional daily personal-book comparisons;
they are not intraday funded-account paths or permission to evaluate 2023+.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date, datetime, timezone
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "analysis/codex_hunt_v2_fvb_short_bench.py"
OUTPUT_ROOT = ROOT / "analysis/outputs/codex_hunt_v2_fvb_short"
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "analysis"))
os.environ["NUMBA_CACHE_DIR"] = str(OUTPUT_ROOT / "bench_engineering/cache/numba")

import numpy as np
import pandas as pd
import codex_anson_personal as SHARED
import metrics as METRICS
import resampling as RESAMPLING

PLAN = "agents/codex/plans/hunt_v2_fvb_short_execution.md"
EVIDENCE = "agents/codex/evidence/hunt_v2_fvb_short_execution.md"
CONTROLS = "agents/codex/RESEARCH_CONTROLS.md"
CANDIDATE_ID = "hunt_v2_H02_FVB_SHORT_EXEC"
SOURCE_PINS = ("afde088b8b64cf939ff1b325a27eea041cf62c70", "92b1d4cde768bcfce019cf9a95944158dd0ebba3")
BASELINE_COMMIT = "63f557da51f8348b1779f0dd44259aff8c2d01df"
BASELINE = "analysis/outputs/codex_rebound/personal19/UNIFORM/fee_1.24/baseline_daily19.csv"
BASELINE_COPY = "analysis/outputs/codex_rebound/personal19/SUNDAY2/fee_1.24/baseline_daily19.csv"
SNAPSHOT = "agents/codex/inputs/rebound/plan_update_afde088"
CONTEXT = ("analysis/personal_portfolio.py", "analysis/personal_variants.py",
           "personal_strategies/PORTFOLIO.md", "funded_strategies/FUNDED_PLAN.md")
DEPENDENCIES = ("analysis/codex_anson_personal.py", "analysis/metrics.py", "analysis/resampling.py", "analysis/montecarlo.py", CONTROLS)
COLUMNS = ("VaultBreak", "OvernightBiasML", "MondayLong", "ExpirationOpenShort", "LateDayFlow", "NFPFade",
           "BridgeMondayLong", "CLSundayFade_perMCL", "ESMOCFollow_perMES", "RelativeStrength", "FC2B",
           "TwinContinuation", "OvernightTick", "DualThrust", "Kusho", "S47", "S30", "SwingTarget", "PaperTrend")
MODELS = ("SHORT_EXEC", "BOTH_CAUSAL")
ROWS = ("BASE", "ADD", "EMPTY", "REPLACE")
SLOT = "DualThrust"
FIRST, LAST = date(2018, 1, 1), date(2022, 12, 31)
MC_N, MC_HORIZON, MC_BLOCK, MC_SEED = 5000, 252, 20, 20261026
FEE, SLIP, POINT_VALUE, TOL = 1.24, 0.50, 2.0, 1e-6
LIMITS = [
    "Published current19 daily personal marks are preserved unchanged; they are not joint intraday margin/liquidation or funded/evaluation account paths.",
    "Core published commissions use nonzero-P&L days and can undercount reentries; MOC/S30 retain inherited fee approximations. A common $1.24 label does not prove exact per-ticket fee parity.",
    "Twin uses the marked v1 checker ledger rather than exact v2.1; Kusho uses exit-date booking. The fee, reentry and mark uncertainty is not quantitatively bounded here.",
    "The candidate is charged exact native one-MNQ assumed fees, but NQ bars do not establish native MNQ listing, fills, spread, receipt or zero processing delay.",
    "The preknown quarterly guard is not verified vendor-switch provenance. Shared design source/clock/calendar and unresolved-path gates remain required.",
    "SHORT_EXEC is a separately executable rule; BOTH_CAUSAL is an unselectable reference, not a source ledger whose shorts can be masked into candidate returns.",
    "This compares the candidate with an unchanged published DualThrust slot. It does not call a candidate-versus-DT execution-method difference a filter increment or establish old-source FVB/MC-list parity.",
    "Retained OT book coverage ends2026-07-07. This design-only bench uses2018-22 and constructs no complete postcutoff book history.",
    "Positive point/paired utility remains conditional while baseline uncertainty is unresolved; no promotion, trading approval, funded payout claim or2023+ authorization follows.",
]


class Unresolved(ValueError):
    """Incomplete evidence must not become a passing benchmark."""


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
    if not path.is_relative_to(OUTPUT_ROOT.resolve()) or path == OUTPUT_ROOT.resolve():
        raise ValueError("Output must be a child of the H02 Codex output directory")
    return path


def write_once(path: Path, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(body)


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
    """Check dates before financial conversion; never evaluate2023+ values."""
    reader = csv.DictReader(stream)
    if reader.fieldnames is None or not set(required) <= set(reader.fieldnames):
        raise Unresolved("Missing source columns: " + ",".join(required))
    rows, previous = [], None
    for row in reader:
        stamp = date.fromisoformat(row["date"])
        if previous is not None and stamp < previous:
            raise Unresolved("Unordered source date; future-stop boundary is unsafe")
        previous = stamp
        if stamp > LAST:
            if stop_at_future:
                break
            raise Unresolved("Future candidate/calendar row is forbidden")
        if stamp >= FIRST:
            rows.append((pd.Timestamp(stamp), row))
    return rows


def bool_value(value) -> bool:
    if str(value).lower() in ("true", "1"):
        return True
    if str(value).lower() in ("false", "0"):
        return False
    raise Unresolved("Calendar boolean must be literal")


def metadata_bindings() -> dict:
    """Executed only after root gate; hashes/header/source provenance, no prices."""
    body = (ROOT / BASELINE).read_bytes()
    if body != (ROOT / BASELINE_COPY).read_bytes():
        raise Unresolved("Published current19 baseline copies differ")
    if blob(body) != git("rev-parse", BASELINE_COMMIT + ":" + BASELINE).decode().strip():
        raise Unresolved("Published baseline differs from committed artifact")
    with (ROOT / BASELINE).open(newline="") as stream:
        if tuple(next(csv.reader(stream))) != ("date", *COLUMNS):
            raise Unresolved("Adopted current19 header changed")
    path = ROOT / SNAPSHOT / "manifest.json"
    manifest = json.loads(path.read_text())
    if manifest["reference"] != SOURCE_PINS[0]:
        raise Unresolved("Incorrect current19 source pin")
    bindings = {BASELINE: hashlib.sha256(body).hexdigest(), BASELINE_COPY: sha(ROOT / BASELINE_COPY),
                str(path.relative_to(ROOT)): sha(path)}
    for rel in CONTEXT:
        earlier, current = (git("show", pin + ":" + rel) for pin in SOURCE_PINS)
        saved = ROOT / SNAPSHOT / rel
        if earlier != current or saved.read_bytes() != earlier or sha(saved) != manifest["files"][rel]["sha256"]:
            raise Unresolved("Current19 retained source definition changed: " + rel)
        bindings[str(saved.relative_to(ROOT))] = sha(saved)
    return bindings


def artifact_inventory(marker_path: Path, marker: dict) -> dict:
    artifacts = marker.get("artifacts_sha256")
    if not isinstance(artifacts, dict) or not artifacts:
        raise PermissionError("Design marker has no immutable artifact inventory")
    for name, expected in artifacts.items():
        path = (marker_path.parent / name).resolve()
        if path.parent != marker_path.parent or not isinstance(expected, str) or sha(path) != expected:
            raise PermissionError("Design artifact hash/path mismatch: " + name)
    return artifacts


def authorize(args) -> tuple[dict, dict, dict]:
    # This guard precedes marker/hash/baseline reads, including engineering retries.
    if not args.authorize_design_pass:
        raise PermissionError("Explicit root design-pass GO is required before financial input reads")
    if git("branch", "--show-current").decode().strip() != "codex/work":
        raise PermissionError("Work only on codex/work")
    if not args.prereg or not args.implementation_commit:
        raise PermissionError("Committed H02 preregistration and implementation are required")
    prereg = git("rev-parse", args.prereg).decode().strip()
    implementation = git("rev-parse", args.implementation_commit).decode().strip()
    git("merge-base", "--is-ancestor", prereg, implementation)
    git("merge-base", "--is-ancestor", implementation, "HEAD")
    for rel in (PLAN, EVIDENCE):
        if git("show", prereg + ":" + rel) != (ROOT / rel).read_bytes() or git("show", implementation + ":" + rel) != (ROOT / rel).read_bytes():
            raise PermissionError("H02 preregistration/evidence changed after commit: " + rel)
    for rel in (SCRIPT, *DEPENDENCIES):
        if git("show", implementation + ":" + rel) != (ROOT / rel).read_bytes():
            raise PermissionError("Implementation/dependency is not frozen: " + rel)
    marker_path, gate_path = Path(args.design_marker).resolve(), Path(args.design_gate).resolve()
    if marker_path != OUTPUT_ROOT / "design_verified_execution.json" or gate_path != OUTPUT_ROOT / "design_gate.json":
        raise PermissionError("Only canonical H02 design artifacts may authorize the bench")
    marker, gate = json.loads(marker_path.read_text()), json.loads(gate_path.read_text())
    if marker.get("candidate_id") != CANDIDATE_ID or marker.get("phase") != "design" or marker.get("primary_model") != "SHORT_EXEC" or marker.get("selected") is not None:
        raise PermissionError("Wrong H02 family/phase/primary, or premature prebench selection")
    if not marker.get("design_passed", marker.get("passed", False)) or not gate.get("design_passed", gate.get("passed", False)):
        raise PermissionError("A completed passed H02 design gate is mandatory")
    if git("rev-parse", marker.get("prereg", "INVALID")).decode().strip() != prereg or git("rev-parse", marker.get("implementation_commit", "INVALID")).decode().strip() != implementation:
        raise PermissionError("Design marker is not bound to the committed H02 plan/implementation")
    schema = marker.get("daily_schema", {})
    if schema.get("columns") != ["date", *MODELS] or schema.get("net_unit") != "USD per 1 MNQ" or schema.get("commission_rt") != FEE or schema.get("slippage_per_market_stop_fill") != SLIP:
        raise PermissionError("H02 daily model/native-unit/cost schema differs")
    inventory = artifact_inventory(marker_path, marker)
    inputs = (("design_gate.json", gate_path), ("design_daily.csv", args.candidate_daily),
              ("design_calendar_audit.csv", args.calendar), ("design_SHORT_EXEC_trades.csv", args.short_trades),
              ("design_BOTH_CAUSAL_trades.csv", args.both_trades))
    bindings = {}
    for name, raw_path in inputs:
        path = Path(raw_path).resolve()
        if path != marker_path.parent / name or inventory.get(name) != sha(path):
            raise PermissionError("Input is not the exact hash-bound H02 " + name)
        bindings[str(path.relative_to(ROOT))] = sha(path)
    # Require the independently verified H02 gross predecessor, not a bare gate.
    gross_path = OUTPUT_ROOT / "gross_verified_execution.json"
    gross_marker = json.loads(gross_path.read_text())
    if gross_marker.get("phase") != "gross" or not gross_marker.get("passed") or git("rev-parse", gross_marker.get("prereg", "INVALID")).decode().strip() != prereg:
        raise PermissionError("Verified passed H02 gross predecessor is missing")
    artifact_inventory(gross_path, gross_marker)
    if marker.get("gross_marker_sha256") != sha(gross_path):
        raise PermissionError("Stopped design is not bound to its gross predecessor")
    bindings.update(metadata_bindings())
    for rel in (SCRIPT, PLAN, EVIDENCE, *DEPENDENCIES):
        bindings[rel] = sha(ROOT / rel)
    for path in (marker_path, gross_path):
        bindings[str(path.relative_to(ROOT))] = sha(path)
    return gate, marker, bindings


def load_inputs(args) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    with (ROOT / BASELINE).open(newline="") as stream:
        rows = read_design_rows(stream, ("date", *COLUMNS), stop_at_future=True)
    frame = pd.DataFrame([{k: float(r[k]) for k in COLUMNS} for _, r in rows],
                         index=pd.DatetimeIndex([d for d, _ in rows], name="date"))
    with Path(args.candidate_daily).open(newline="") as stream:
        rows = read_design_rows(stream, ("date", *MODELS))
    daily = pd.DataFrame([{k: float(r[k]) for k in MODELS} for _, r in rows],
                         index=pd.DatetimeIndex([d for d, _ in rows], name="date"))
    for value in (frame, daily):
        if value.empty or value.index.has_duplicates or not value.index.is_monotonic_increasing or not np.isfinite(value.to_numpy()).all():
            raise Unresolved("Unordered, duplicated, empty or nonfinite daily source")
    if set(frame.index.year) != set(range(2018, 2023)):
        raise Unresolved("Published book is missing a design year")
    with Path(args.calendar).open(newline="") as stream:
        rows = read_design_rows(stream, ("date", "cash_day", "included_in_design_daily"))
    calendar = {}
    for d, row in rows:
        if d in calendar:
            raise Unresolved("Duplicate processed calendar date")
        calendar[d] = {k: bool_value(row[k]) for k in ("cash_day", "included_in_design_daily")}
    if any(flags["cash_day"] and not flags["included_in_design_daily"] for flags in calendar.values()):
        raise Unresolved("Design drops a cash day; retain warmup/skipped days as explicit zeros")
    if {d for d, flags in calendar.items() if flags["included_in_design_daily"]} != set(daily.index):
        raise Unresolved("Design daily rows differ from their calendar inclusion proof")
    extra = daily.index.difference(frame.index)
    if (np.abs(daily.loc[extra, list(MODELS)].to_numpy()) > TOL).any():
        raise Unresolved("Nonzero candidate date has no published book date")
    missing = frame.index.difference(daily.index)
    for d in missing:
        if d not in calendar or calendar[d]["cash_day"]:
            raise Unresolved("Missing observed candidate book day; no silent zero: " + str(d.date()))
    if len(missing):
        daily = pd.concat([daily, pd.DataFrame(0.0, index=missing, columns=MODELS)]).sort_index()
    daily = daily.reindex(frame.index)
    if daily.isna().any().any():
        raise Unresolved("Unproven zero introduced by alignment")
    audit = dict(days=len(frame), first=str(frame.index.min().date()), last=str(frame.index.max().date()),
                 all_design_years=True, warmup_cash_zeros_required=True,
                 explicit_closed_cash_zero_dates=[str(d.date()) for d in missing],
                 zero_only_maker_dates_outside_book=[str(d.date()) for d in extra],
                 coverage_basis="Every published2018-22 book day; all maker cash days including warmup are explicit")
    return frame, daily, audit


def load_checked_trades(path: Path | str, model: str) -> pd.DataFrame:
    required = ("date", "event_id", "side", "entry_j", "exit_j", "entry", "exit", "gross_points", "fill_count", "net_mnq")
    with Path(path).open(newline="") as stream:
        rows = read_design_rows(stream, required)
    out = []
    for d, row in rows:
        numeric = {k: float(row[k]) for k in required if k not in ("date", "event_id")}
        if not all(np.isfinite(v) for v in numeric.values()):
            raise Unresolved("Nonfinite candidate trade")
        if numeric["side"] not in (-1, 1) or (model == "SHORT_EXEC" and numeric["side"] != -1) or numeric["fill_count"] != 2:
            raise Unresolved("Frozen native one-micro/two-fill or side policy differs")
        ej, xj = numeric["entry_j"], numeric["exit_j"]
        if ej != int(ej) or xj != int(xj) or not 512 <= ej <= 631 or not ej <= xj <= 911:
            raise Unresolved("Entry/exit clock differs; no half-day or after15:59 fallback")
        gross = (numeric["exit"] - numeric["entry"]) * numeric["side"]
        if abs(gross - numeric["gross_points"]) > TOL or abs(gross * POINT_VALUE - FEE - SLIP * numeric["fill_count"] - numeric["net_mnq"]) > TOL:
            raise Unresolved("Gross/native commission/slippage/net bridge does not reconcile")
        out.append(dict(date=d, event_id=str(row["event_id"]), **numeric))
    frame = pd.DataFrame(out, columns=required)
    if frame.empty or frame.event_id.eq("").any() or frame.event_id.duplicated().any() or frame.groupby("date").size().max() > 2:
        raise Unresolved("Empty ledger, duplicate IDs or more than two daily tickets")
    for _, group in frame.groupby("date", sort=False):
        if not group.entry_j.is_monotonic_increasing or (group.entry_j.to_numpy()[1:] < group.exit_j.to_numpy()[:-1] + 2).any():
            raise Unresolved("Overlapping tickets or reentry before the later signal boundary")
    return frame


def check_candidate_money(ledgers: dict, daily: pd.DataFrame) -> dict:
    result = {}
    for model in MODELS:
        trades = ledgers[model]
        reconstructed = trades.groupby("date").net_mnq.sum().reindex(daily.index, fill_value=0.0)
        if len(trades[~trades.date.isin(daily.index)]) or not np.allclose(reconstructed, daily[model], atol=TOL, rtol=0):
            raise Unresolved("Ticket-to-daily reconciliation failed: " + model)
        result[model] = dict(tickets=len(trades), long_tickets=int((trades.side == 1).sum()), short_tickets=int((trades.side == -1).sum()),
                             max_tickets_per_day=int(trades.groupby("date").size().max()), gross=float(trades.gross_points.sum() * POINT_VALUE),
                             commission=float(len(trades) * FEE), slippage=float(trades.fill_count.sum() * SLIP),
                             net=float(trades.net_mnq.sum()), contract_quantity=1,
                             commission_rt=FEE, slippage_per_market_stop_fill=SLIP,
                             latest_exit_close_label_j=int(trades.exit_j.max()))
    return dict(models=result, reference_selectable=False, short_is_not_a_both_ledger_mask=True,
                candidate_versus_DT_parity_asserted=False, cost_basis="USD per1MNQ; raw entry/exit prices plus separate adverse fills")


def build_portfolios(frame: pd.DataFrame, daily: pd.DataFrame) -> dict:
    total, old, candidate = frame.sum(axis=1), frame[SLOT], daily["SHORT_EXEC"]
    plans = dict(BASE=total, ADD=total + candidate, EMPTY=total - old, REPLACE=total - old + candidate)
    np.testing.assert_allclose(plans["ADD"] - plans["BASE"], candidate, atol=TOL, rtol=0)
    np.testing.assert_allclose(plans["REPLACE"] - plans["EMPTY"], candidate, atol=TOL, rtol=0)
    np.testing.assert_allclose(plans["BASE"] - plans["EMPTY"], old, atol=TOL, rtol=0)
    return plans


def ratio(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator > 0 else float("nan")


def path_ratios(profit, drawdown):
    out = np.full(len(profit), np.nan)
    np.divide(profit, drawdown, out=out, where=np.asarray(drawdown) > 0)
    return out


def historical(values) -> dict:
    x = np.asarray(values, float)
    result, dd = METRICS.perf(x), RESAMPLING.max_dd(x)
    result.update(total=float(x.sum()), days=len(x), annual=float(x.mean() * 252), initial_zero_max_dd=dd,
                  historical_return_dd=ratio(x.mean() * 252, dd))
    return result


def utility_tests(summary: dict, paired: pd.DataFrame) -> dict:
    result = {}
    for name in ("ADD", "REPLACE"):
        comparisons = {}
        for reference in ("BASE", "EMPTY"):
            row = paired[(paired.config == name) & (paired.reference == reference)].iloc[0]
            margins = {key: summary[name][key] - summary[reference][key] for key in ("historical_return_dd", "median_mc_return_dd")}
            q5 = float(row.paired_return_dd_delta_p5)
            point = all(np.isfinite(v) and v > 0 for v in margins.values())
            paired_ok = int(row.paired_return_dd_finite_paths) == MC_N and np.isfinite(q5) and q5 > 0
            comparisons[reference] = dict(margins=margins, point_passed=point, paired_return_dd_delta_p5=q5,
                                          paired_passed=bool(paired_ok), passed=bool(point and paired_ok))
        result[name] = dict(comparisons=comparisons, passed=all(x["passed"] for x in comparisons.values()))
    return result


def benchmark(plans: dict, *, n=MC_N, horizon=MC_HORIZON, block=MC_BLOCK):
    days = next(iter(plans.values())).index
    idx = SHARED.histories(len(days), n=n, horizon=horizon, block=block, seed=MC_SEED)
    summary, simulations = {}, {}
    for name, series in plans.items():
        profit, dd = SHARED.simulate_daily(series.to_numpy(), idx)
        simulations[name] = (profit, dd)
        summary[name] = dict(**historical(series), mc_profit_p5=float(np.quantile(profit, .05)), mc_profit_p50=float(np.median(profit)),
                             mc_profit_p95=float(np.quantile(profit, .95)), mc_dd_p50=float(np.median(dd)), mc_dd_p95=float(np.quantile(dd, .95)),
                             median_mc_return_dd=ratio(np.median(profit), np.median(dd)), p_losing_year=float(np.mean(profit <= 0)))
    pairs = []
    for name in ("ADD", "REPLACE"):
        for reference in ("BASE", "EMPTY"):
            p, dd = simulations[name]
            bp, bdd = simulations[reference]
            delta = path_ratios(p, dd) - path_ratios(bp, bdd)
            finite = delta[np.isfinite(delta)]
            q = np.quantile(finite, [.05, .5, .95]) if len(finite) else [float("nan")] * 3
            lo, hi = SHARED.paired_mean_interval(p - bp, seed=MC_SEED, n=n)
            dlo, dhi = SHARED.paired_mean_interval(dd - bdd, seed=MC_SEED, n=n)
            alo, ahi = SHARED.historical_annual_effect_interval((plans[name] - plans[reference]).to_numpy(), seed=MC_SEED, n=n, block=block)
            pairs.append(dict(config=name, reference=reference, mean_annual_profit_delta=float((p-bp).mean()),
                              paired_mc_mean_delta_95_lo=float(lo), paired_mc_mean_delta_95_hi=float(hi),
                              mean_dd_delta=float((dd-bdd).mean()), paired_mc_dd_delta_95_lo=float(dlo), paired_mc_dd_delta_95_hi=float(dhi),
                              historical_annual_delta_95_lo=float(alo), historical_annual_delta_95_hi=float(ahi),
                              historical_return_dd_margin=summary[name]["historical_return_dd"]-summary[reference]["historical_return_dd"],
                              median_mc_return_dd_margin=summary[name]["median_mc_return_dd"]-summary[reference]["median_mc_return_dd"],
                              paired_return_dd_finite_paths=len(finite), paired_return_dd_delta_p5=float(q[0]),
                              paired_return_dd_delta_p50=float(q[1]), paired_return_dd_delta_p95=float(q[2]),
                              paired_losing_year_probability_delta=float(np.mean(p <= 0)-np.mean(bp <= 0))))
    return summary, pd.DataFrame(pairs), simulations, idx


def disposition(tests: dict) -> dict:
    if not any(row["passed"] for row in tests.values()):
        return dict(status="FAIL", conditional_utility_passed=False, continue_to_validation=False,
                    reason="No frozen ADD/REPLACE beats BASE and EMPTY in both return/DD ratios with paired return/DD delta5%quantile>0 against both.")
    return dict(status="UNRESOLVED", conditional_utility_passed=True, continue_to_validation=False,
                reason="Conditional published-book utility passes, but baseline fee/reentry/mark uncertainty is unbounded; no qualifying book-improvement claim or2023+ permission.")


def run(args) -> dict:
    # authorize() is intentionally before reading even source financial hashes.
    gate, marker, bindings = authorize(args)
    out = safe_output(args.out)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError("Preserve retained H02 bench outputs")
    if any(OUTPUT_ROOT.rglob("bench_design_verified_execution.json")):
        raise PermissionError("H02 design bench already completed; no alternate-directory financial rerun")
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    with (OUTPUT_ROOT / "bench.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        if any(OUTPUT_ROOT.rglob("bench_design_verified_execution.json")):
            raise PermissionError("Concurrent H02 benchmark completed")
        started = utcnow()
        frame, daily, calendar = load_inputs(args)
        ledgers = {"SHORT_EXEC": load_checked_trades(args.short_trades, "SHORT_EXEC"),
                   "BOTH_CAUSAL": load_checked_trades(args.both_trades, "BOTH_CAUSAL")}
        money = check_candidate_money(ledgers, daily)
        plans = build_portfolios(frame, daily)
        summary, paired, simulations, idx = benchmark(plans)
        tests = utility_tests(summary, paired)
        decision = disposition(tests)
        result = dict(**decision, comparisons=tests, phase="design_only", candidate_id=CANDIDATE_ID,
                      primary_model="SHORT_EXEC", selected=None, unselectable_reference="BOTH_CAUSAL", replacement_slot=SLOT,
                      benchmark_rows=list(ROWS), native_candidate_money=money, common_calendar=calendar,
                      baseline_definition_unchanged=True, baseline_uncertainty_quantified=False,
                      alpha_identity="ADD minus BASE and REPLACE minus EMPTY equal independently executable SHORT_EXEC; REPLACE minus BASE also removes published DT.",
                      mc=dict(draws=MC_N, horizon=MC_HORIZON, block=MC_BLOCK, seed=MC_SEED,
                              convention="codex_anson_personal.histories/simulate_daily; repo noncircular20-day blocks",
                              point_ratio="median annual profit / median DD; historical annual profit / initial-zero DD",
                              paired_ratio="per-identical-history profit/DD difference;5%quantile must be positive against both controls"),
                      counted_evaluations_this_bench=0, new_selectable_strategy_configurations=0,
                      validation_or_funded_claim=False, half_day_check="All retained candidate exits<=15:11CT by ticket audit; no half-day holds permitted by design gate.",
                      limitations=LIMITS)
        if any(sha(ROOT / rel) != expected for rel, expected in bindings.items()):
            raise RuntimeError("Bound implementation/input changed during bench; no success marker")
        out.mkdir(parents=True, exist_ok=True)
        buffers = {"portfolio_daily.csv": pd.DataFrame(plans).to_csv(index_label="date").encode(),
                   "candidate_slot_audit.csv": pd.DataFrame(dict(published_dual_thrust=frame[SLOT], short_exec=daily.SHORT_EXEC,
                       both_causal_reference=daily.BOTH_CAUSAL, replacement_delta=daily.SHORT_EXEC-frame[SLOT])).to_csv(index_label="date").encode(),
                   "bench_summary.csv": pd.DataFrame(summary).T.to_csv(index_label="config").encode(),
                   "paired_effects.csv": paired.to_csv(index=False).encode(), "bench_gate.json": json_bytes(finite_json(result))}
        for name, body in buffers.items():
            write_once(out / name, body)
        np.save(out / "paired_histories.npy", idx)
        np.savez_compressed(out / "paired_portfolio_paths.npz", **{name+"__"+field: values[i]
            for name, values in simulations.items() for i, field in enumerate(("profit", "drawdown"))})
        artifacts = {p.name: sha(p) for p in out.iterdir() if p.is_file()}
        success = dict(started_utc=started, completed_utc=utcnow(), phase="design_personal_bench", status=decision["status"],
                       candidate_id=CANDIDATE_ID, prereg=args.prereg, implementation_commit=args.implementation_commit,
                       root_design_pass_authorized=True, candidate_design_marker_sha256=sha(args.design_marker),
                       input_bindings=bindings, artifacts_sha256=artifacts, no_2023_candidate_values_evaluated=True,
                       baseline_source_pins=list(SOURCE_PINS), baseline_artifact_commit=BASELINE_COMMIT,
                       financial_benchmark_completed=True, no_promotion_or_funded_claim=True)
        write_once(out / "bench_design_verified_execution.json", json_bytes(success))
        return result


def fixtures() -> dict:
    checks = []
    try:
        read_design_rows(io.StringIO("date,X\n2022-12-30,1\n2023-01-03,not-a-number\n"), ("date", "X"))
    except Unresolved as exc:
        assert "Future" in str(exc)
        checks.append("future_candidate_rejected_before_financial_conversion")
    else:
        raise AssertionError("Future candidate admitted")
    rows = read_design_rows(io.StringIO("date,X\n2022-12-30,1\n2023-01-03,not-a-number\n"), ("date", "X"), stop_at_future=True)
    assert len(rows) == 1 and float(rows[0][1]["X"]) == 1
    checks.append("baseline_stops_before_future_financial_conversion")
    days = pd.date_range("2020-01-01", periods=260)
    frame = pd.DataFrame(0.0, index=days, columns=COLUMNS)
    frame["VaultBreak"] = np.where(np.arange(260) % 4 == 0, -3.0, 4.0)
    frame[SLOT] = np.where(np.arange(260) % 3 == 0, -2.0, 1.0)
    daily = pd.DataFrame(dict(SHORT_EXEC=np.where(np.arange(260) % 4 == 0, 2.0, -0.2), BOTH_CAUSAL=0.0), index=days)
    plans = build_portfolios(frame, daily)
    assert np.allclose(plans["EMPTY"], frame.VaultBreak)
    assert np.allclose(plans["REPLACE"]-plans["EMPTY"], daily.SHORT_EXEC)
    assert not np.allclose(plans["REPLACE"]-plans["BASE"], daily.SHORT_EXEC)
    checks.append("whole_micro_add_empty_replace_and_alpha_identity")
    idx = SHARED.histories(260, n=31, horizon=40, block=5, seed=MC_SEED)
    profit, dd = SHARED.simulate_daily(frame.VaultBreak.to_numpy(), idx)
    import montecarlo as MC
    reference = MC.daily_mc(frame.VaultBreak.to_numpy(), horizon=40, n=31, block=5, seed=MC_SEED)
    assert np.isclose(np.median(profit), reference["pnl_p50"]) and np.isclose(np.median(dd), reference["dd_p50"])
    assert np.array_equal(idx, SHARED.histories(260, n=31, horizon=40, block=5, seed=MC_SEED))
    checks.append("shared_montecarlo_parity_and_paired_histories")
    summary, pairs, simulations, paired_idx = benchmark(plans, n=31, horizon=40, block=5)
    assert np.array_equal(idx, paired_idx)
    for row in pairs.itertuples(index=False):
        p, d = simulations[row.config]
        rp, rd = simulations[row.reference]
        actual = np.quantile(path_ratios(p, d)-path_ratios(rp, rd), .05)
        assert np.isclose(row.paired_return_dd_delta_p5, actual)
    checks.append("paired_ratio_quantile_uses_identical_annual_paths")
    assert RESAMPLING.max_dd([-5, 3]) == 5 and not np.isfinite(ratio(1, 0))
    assert np.isnan(path_ratios(np.array([1.0]), np.array([0.0]))[0])
    checks.append("initial_zero_drawdown_and_undefined_ratio_veto")
    sample = {key: dict(historical_return_dd=1.0, median_mc_return_dd=1.0) for key in ROWS}
    sample["ADD"] = dict(historical_return_dd=1.1, median_mc_return_dd=1.1)
    fake = pd.DataFrame([dict(config=name, reference=ref, paired_return_dd_delta_p5=.01, paired_return_dd_finite_paths=MC_N)
                         for name in ("ADD", "REPLACE") for ref in ("BASE", "EMPTY")])
    tests = utility_tests(sample, fake)
    assert tests["ADD"]["passed"] and disposition(tests)["status"] == "UNRESOLVED"
    fake.loc[(fake.config == "ADD") & (fake.reference == "EMPTY"), "paired_return_dd_delta_p5"] = 0
    assert disposition(utility_tests(sample, fake))["status"] == "FAIL"
    checks.append("strict_both_controls_paired_p5_and_unbounded_uncertainty_veto")
    class Args:
        authorize_design_pass = False
    try:
        authorize(Args())
    except PermissionError:
        checks.append("root_go_blocks_before_any_financial_hash_or_body_read")
    else:
        raise AssertionError("Unauthorised input path")
    return dict(passed=True, checks=checks, private_financial_inputs_opened=False, new_return_trials=0,
                script_sha256=sha(ROOT / SCRIPT), command="--fixtures")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", action="store_true")
    parser.add_argument("--authorize-design-pass", action="store_true")
    parser.add_argument("--prereg")
    parser.add_argument("--implementation-commit")
    for name in ("candidate-daily", "calendar", "design-gate", "design-marker", "short-trades", "both-trades"):
        parser.add_argument("--" + name, type=Path)
    parser.add_argument("--out", type=Path, default=OUTPUT_ROOT / "bench_design")
    args = parser.parse_args()
    if args.fixtures:
        result = fixtures()
        path = OUTPUT_ROOT / "bench_engineering" / ("synthetic_checks_" + result["script_sha256"][:12] + ".json")
        body = json_bytes(result)
        if path.exists():
            if path.read_bytes() != body:
                raise ValueError("Different retained synthetic fixture artifact")
        else:
            write_once(path, body)
        print(json.dumps(result))
        return
    if any(getattr(args, name) is None for name in ("candidate_daily", "calendar", "design_gate", "design_marker", "short_trades", "both_trades")):
        parser.error("Financial execution requires every marker-bound H02 input and explicit root GO")
    print(json.dumps(finite_json(run(args))))


if __name__ == "__main__":
    main()
