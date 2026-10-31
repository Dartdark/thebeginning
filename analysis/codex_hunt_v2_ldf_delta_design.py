"""Hunt-v2 H01 counted design; frozen gross event/masks, 2018-22 only.

One shared BASE replay is masked into three counted configurations. Subset
paths are diagnostic resampling, not executable strategies. No validation or
account engine is called here; a passed design must go immediately to the bench.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_hunt_v2_ldf_delta"
os.environ["NUMBA_CACHE_DIR"] = str(OUT / "cache/numba")
sys.path.insert(0, str(ROOT / "analysis"))
import numpy as np
import pandas as pd
import metrics as M
import resampling as R
from grid import execute, _walk
import codex_hunt_v2_ldf_delta as G

SCRIPT = "analysis/codex_hunt_v2_ldf_delta_design.py"
MODELS = ("BASE", "LEGACY", "STRICT30")
SEED, RANDOM_SUBSETS = 20261026, 1000
BASES = {
    "MNQ": ("net_mnq", "gross_mnq", "cost_mnq"),
    "MNQ_4tick": ("net_mnq_4tick", "gross_mnq", "cost_mnq_4tick"),
    "NQ": ("net_nq", "gross_nq", "cost_nq"),
    "NQ_4tick": ("net_nq_4tick", "gross_nq", "cost_nq_4tick"),
}
DAILY_SCHEMA = dict(columns=["date", *MODELS], date_format="YYYY-MM-DD", net_unit="USD per 1 MNQ",
                    commission_rt=1.24, slippage_per_market_stop_fill=0.50, fill_count_per_trade=2)


def safe_json(value):
    if isinstance(value, dict):
        return {str(k): safe_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_json(v) for v in value]
    if isinstance(value, np.generic):
        return safe_json(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def dump(path: Path, value: dict) -> None:
    G.write_once(path, (json.dumps(safe_json(value), indent=2, allow_nan=False) + "\n").encode())


def nw_t(values, lag=5) -> float | None:
    x = np.asarray(values, float)
    if not len(x):
        return None
    e = x - x.mean()
    variance_sum = float(e @ e)
    for k in range(1, min(lag, len(x) - 1) + 1):
        variance_sum += 2 * (1 - k / (lag + 1)) * float(e[k:] @ e[:-k])
    return float(x.mean() * len(x) / np.sqrt(variance_sum)) if variance_sum > 0 else None


def costs(gross_points, fill_count=2) -> dict:
    gross_points = np.asarray(gross_points, float)
    result = dict(gross_points=gross_points, fill_count=fill_count,
                  gross_mnq=gross_points * 2, gross_nq=gross_points * 20,
                  commission_mnq=1.24, slippage_mnq=0.50 * fill_count,
                  commission_nq=7.25, slippage_nq=5.0 * fill_count)
    for name, pv, commission, slip in (("mnq", 2, 1.24, 0.50), ("nq", 20, 7.25, 5.0)):
        result[f"cost_{name}"] = commission + slip * fill_count
        result[f"cost_{name}_4tick"] = commission + 4 * slip * fill_count
        result[f"net_{name}"] = gross_points * pv - result[f"cost_{name}"]
        result[f"net_{name}_4tick"] = gross_points * pv - result[f"cost_{name}_4tick"]
    return result


def parse_bool(series: pd.Series) -> np.ndarray:
    labels = series.astype(str).str.lower()
    if not labels.isin(["true", "false"]).all():
        raise ValueError("Frozen event contains an ambiguous boolean state.")
    return labels.eq("true").to_numpy()


def fixtures() -> dict:
    # This compiles only synthetic paths; NUMBA_CACHE_DIR was set before grid import.
    o = np.array([100., 100., 100.])
    h = np.array([100., 101., 101.])
    l = np.array([100., 94., 99.])
    c = np.array([100., 100., 100.])
    assert _walk(o, h, l, c, 1, 2, 1, 95., np.inf, 1.)[:3] == (1, 95., 0)
    l = np.array([100., 99., 89.]); o[2] = 90.; h[2] = 91.; c[2] = 90.
    assert _walk(o, h, l, c, 1, 2, 1, 95., np.inf, 1.)[:3] == (2, 90., 0)
    o = np.array([100., 100., 100.]); h = np.array([100., 106., 101.]); l = np.array([100., 99., 99.]); c = np.array([100., 100., 100.])
    assert _walk(o, h, l, c, 1, 2, -1, 105., -np.inf, 1.)[:3] == (1, 105., 0)
    h = np.array([100., 101., 111.]); o[2] = 110.; l[2] = 109.; c[2] = 110.
    assert _walk(o, h, l, c, 1, 2, -1, 105., -np.inf, 1.)[:3] == (2, 110., 0)
    assert _walk(np.array([100., 100., 102.]), np.array([101., 101., 104.]),
                 np.array([99., 99., 101.]), np.array([100., 100., 103.]), 1, 2, 1, 90., np.inf, 1.)[:3] == (2, 103., 2)
    x = costs(np.array([10., -10.]))
    assert np.allclose(x["net_mnq"], [17.76, -22.24])
    assert np.allclose(x["net_mnq_4tick"], [14.76, -25.24])
    assert x["cost_nq"] == 17.25 and x["cost_nq_4tick"] == 47.25
    assert np.ceil((0.25 * 100.1) / 0.25) * 0.25 == 25.25
    assert R.max_dd([-10., 5.]) == 10.
    assert parse_bool(pd.Series([True, False])).tolist() == [True, False]
    assert len(MODELS) == 3 and MODELS[2] == "STRICT30"
    return dict(passed=True, checks=["entry-bar long/short stops", "worse long/short stop gaps", "no-target time exit",
        "native MNQ and NQ commissions/slippage", "fixed four-tick stress", "stop rounds up one native tick",
        "initial-zero drawdown", "unambiguous frozen booleans", "three configurations one primary"],
        raw_data_or_strategy_returns_read=False, script_sha256=G.sha(ROOT / SCRIPT),
        runtime_versions=G.runtime_versions(), numba_cache_dir=str(OUT / "cache/numba"))


def verify(prereg: str) -> tuple[dict, pd.DataFrame, pd.DataFrame, dict]:
    if subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() != "codex/work":
        raise ValueError("Counted design must remain on codex/work.")
    for path in (G.PLAN, G.EVIDENCE):
        if G.committed_bytes(prereg, path) != (ROOT / path).read_bytes():
            raise ValueError("Frozen evidence/plan differs: " + path)
    if G.committed_bytes("HEAD", SCRIPT) != (ROOT / SCRIPT).read_bytes():
        raise ValueError("Commit the design implementation before opening stopped returns.")
    for directory in (ROOT / "analysis/outputs").glob("codex_hunt_v2_ldf_delta*"):
        if (directory / "design_verified_execution.json").exists():
            raise ValueError("Completed H01 counted design already exists; no repeat or alternate directory.")
    marker_path = OUT / "gross_verified_execution.json"
    marker = json.loads(marker_path.read_text())
    if not (marker.get("passed") is True and marker.get("phase") == "gross" and marker.get("prereg") == prereg):
        raise ValueError("Successful matching frozen gross marker is required.")
    for name, expected in marker["artifacts_sha256"].items():
        if Path(name).name != name or G.sha(OUT / name) != expected:
            raise ValueError("Frozen gross artifact changed: " + name)
    gross_gate = json.loads((OUT / "gross_gate.json").read_text())
    if not gross_gate["passed"] or gross_gate["frozen_later_counted_models"] != list(MODELS):
        raise ValueError("Gross result does not authorize these three designs.")
    binding = json.loads((OUT / "gross_input_binding.json").read_text())
    if marker["script_sha256"] != G.sha(ROOT / G.SCRIPT):
        raise ValueError("Frozen gross maker changed.")
    for name, expected in binding["hashes"].items():
        if G.sha(ROOT / name) != expected:
            raise ValueError("Gross-bound raw/spec/helper source changed: " + name)
    events = pd.read_csv(OUT / "gross_events.csv")
    events["date"] = pd.to_datetime(events.date, format="%Y-%m-%d")
    events["event_id"] = np.arange(len(events), dtype=np.int32)
    if not (events.date.dt.year.between(2018, 2022).all() and events.date.is_unique and events.date.is_monotonic_increasing):
        raise ValueError("Frozen events are not the unique chronological design-only population.")
    if not events.side.isin([-1, 1]).all():
        raise ValueError("Frozen event has an invalid direction.")
    for model in MODELS[1:]:
        events[f"keep_{model}"] = parse_bool(events[f"keep_{model}"])
        if not events.loc[events.side < 0, f"keep_{model}"].all():
            raise ValueError("Frozen long-only filter removed a short.")
    if parse_bool(events.unresolved_held_path).any() or events.invalid_or_missing_held_minutes.ne(0).any():
        raise ValueError("Gross event contains an unresolved held path.")
    calendar = pd.read_csv(OUT / "gross_calendar_audit.csv")
    calendar["date"] = pd.to_datetime(calendar.date, format="%Y-%m-%d")
    calendar["pl_early_skip"] = parse_bool(calendar.pl_early_skip)
    if calendar.date.duplicated().any() or not calendar.date.dt.year.between(2018, 2022).all():
        raise ValueError("Frozen calendar is not unique and design-only.")
    dependencies = [SCRIPT, "analysis/grid.py", "analysis/metrics.py", "analysis/resampling.py"]
    hashes = dict(binding["hashes"])
    hashes.update({name: G.sha(ROOT / name) for name in dependencies})
    design_binding = dict(prereg=prereg,
        implementation_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        gross_marker_sha256=G.sha(marker_path), gross_artifacts_sha256=marker["artifacts_sha256"],
        source_hashes=hashes, runtime_versions=G.runtime_versions(), models=list(MODELS),
        candidate_features_regenerated=False, source_period="2018-22 only", numba_cache_dir=str(OUT / "cache/numba"))
    return binding, events, calendar, design_binding


def verify_runtime_binding(binding: dict) -> None:
    for name, expected in binding["source_hashes"].items():
        if G.sha(ROOT / name) != expected:
            raise ValueError("Bound design source changed before successful publication: " + name)
    if G.sha(OUT / "gross_verified_execution.json") != binding["gross_marker_sha256"]:
        raise ValueError("Frozen gross marker changed during design.")
    for name, expected in binding["gross_artifacts_sha256"].items():
        if G.sha(OUT / name) != expected:
            raise ValueError("Frozen gross artifact changed during design: " + name)


def replay_base(grid, events: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    lookup = {int(date): row for row, date in enumerate(grid.dates)}
    days = np.array([lookup[int(date.strftime("%Y%m%d"))] for date in events.date], dtype=int)
    stop_points = np.ceil((0.25 * events.atr.to_numpy(float)) / 0.25) * 0.25
    signals = pd.DataFrame(dict(day=days, dj=G.SIGNAL_J, side=events.side.to_numpy(int),
                                stop=stop_points, target=np.inf, exit_j=G.EXIT_J))
    trades = execute(grid, signals, max_trades=1, max_losses=1, name="H01_BASE")
    if len(trades) != len(events) or trades.day.duplicated().any():
        raise ValueError("Shared engine suppressed/duplicated a frozen BASE event.")
    trades = trades.merge(pd.DataFrame(dict(day=days, event_id=events.event_id, stop_points=stop_points)),
                           on="day", how="left", validate="one_to_one").sort_values("event_id").reset_index(drop=True)
    if not np.array_equal(trades.side.to_numpy(), events.side.to_numpy()):
        raise ValueError("Shared replay side differs from frozen event.")
    if not np.array_equal(trades.j0.to_numpy(), np.full(len(events), G.ENTRY_J)):
        raise ValueError("Shared replay changed the frozen entry clock.")
    if not np.allclose(trades.entry, events.entry_open, rtol=0, atol=1e-9):
        raise ValueError("Shared entry prices differ from immutable gross endpoints.")
    if not trades.kind.isin([0, 2]).all():
        raise ValueError("No-target design generated a target exit.")
    trades = trades.rename(columns={"j0": "entry_j", "j1": "exit_j", "pnl": "shared_engine_gross_nq",
                                    "net": "shared_engine_net_nq_before_fill_slippage", "mae": "raw_mae_nq"})
    trades["date"] = events.date.to_numpy()
    trades["year"] = events.year.to_numpy(int)
    trades["decision_j"] = G.SIGNAL_J
    trades["signal_hour"] = G.SIGNAL_J // 60
    trades["atr"] = events.atr.to_numpy(float)
    for model in MODELS[1:]:
        trades[f"keep_{model}"] = events[f"keep_{model}"].to_numpy(bool)
    for name, values in costs((trades.exit - trades.entry) * trades.side).items():
        trades[name] = values
    trades["entry_walltime_ct"] = trades.date.dt.strftime("%Y-%m-%d") + " 14:00"
    trades["entry_bar_label_ct"] = trades.date.dt.strftime("%Y-%m-%d") + " 14:01"
    trades["exit_hhmm_label"] = (trades.exit_j // 60) * 100 + trades.exit_j % 60
    valid = G.valid_ohlcv(grid.o, grid.h, grid.l, grid.c, grid.v)
    missing = [int((~valid[int(r.day), int(r.entry_j):int(r.exit_j) + 1]).sum()) for r in trades.itertuples()]
    trades["invalid_held_minutes"] = missing
    audit = dict(base_replays=1, frozen_base_events=len(events), executed_base_tickets=len(trades),
                 total_invalid_held_minutes=int(sum(missing)), exits_after_1430=int((trades.exit_j > G.EXIT_J).sum()),
                 exits_after_1559=int((trades.exit_j > 959).sum()), target_exits=0,
                 entry_bar_stops=int(((trades.exit_j == trades.entry_j) & (trades.kind == 0)).sum()),
                 no_queued_signal_or_counterfactual_reentry=True, source_eligibility_not_regenerated=True,
                 micro_fill_parity_verified=False, price_paths="NQ native bars with separately calculated MNQ fees")
    return trades, audit


def daily_calendar(grid, calendar: pd.DataFrame, events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DatetimeIndex]:
    result = calendar.copy()
    result["cash_day"] = result.cash_kind.isin(["normal", "early"])
    result["prior_atr_valid"] = np.isfinite(result.atr) & result.atr.gt(0)
    eligible = result.cash_day & result.prior_atr_valid
    if not eligible.any():
        raise ValueError("No finite-ATR cash-day design axis.")
    start = result.loc[eligible, "date"].min()
    result["included_in_design_daily"] = result.cash_day & result.date.ge(start)
    lookup = {int(date): row for row, date in enumerate(grid.dates)}
    valid = G.valid_ohlcv(grid.o, grid.h, grid.l, grid.c, grid.v)
    result["known_input_complete"] = [bool(valid[lookup[int(date.strftime("%Y%m%d"))], G.OPEN_J:G.SIGNAL_J + 1].all())
                                       for date in result.date]
    result["has_frozen_base_event"] = result.date.isin(events.date)
    axis = pd.DatetimeIndex(result.loc[result.included_in_design_daily, "date"])
    if not events.date.isin(axis).all():
        raise ValueError("Frozen event lies outside the common causal daily axis.")
    return result, axis


def daily_values(trades: pd.DataFrame, field: str, axis: pd.DatetimeIndex) -> pd.Series:
    return trades.groupby("date")[field].sum().reindex(axis, fill_value=0.0).rename(field)


def performance(daily: pd.Series, values: np.ndarray) -> dict:
    result = M.perf(daily, values)
    # Preserve the shared definitions while including the initial zero equity
    # peak, as the repo's resampling.max_dd does.
    dd = R.max_dd(daily.to_numpy())
    equity = 50_000 + daily.cumsum().to_numpy()
    peak = np.maximum.accumulate(np.maximum(equity, 50_000.))
    ulcer = float(np.sqrt(np.mean(((equity - peak) / peak * 100) ** 2)))
    result.update(max_dd=dd, calmar=result["annual"] / dd if dd > 0 else np.inf,
                  ulcer=ulcer, ulcer_perf=result["annual"] / 50_000 * 100 / ulcer if ulcer > 0 else np.inf,
                  total=float(np.sum(values)), t_trade=G.tstat(values), t_nw5=nw_t(daily), sessions=len(daily))
    return result


def all_metrics(tickets: dict, axis: pd.DatetimeIndex) -> pd.DataFrame:
    rows = []
    for model, trades in tickets.items():
        for period in ("2018-22", *map(str, G.YEARS)):
            a = axis if period == "2018-22" else axis[axis.year == int(period)]
            period_trades = trades if period == "2018-22" else trades[trades.year == int(period)]
            for side in ("all", "long", "short"):
                selected = period_trades if side == "all" else period_trades[period_trades.side == (1 if side == "long" else -1)]
                for basis, (field, gross, cost) in BASES.items():
                    daily = daily_values(selected, field, a)
                    values = selected[field].to_numpy(float)
                    rows.append(dict(model=model, period=period, side=side, basis=basis,
                                     gross=float(selected[gross].sum()), cost=float(selected[cost].sum()),
                                     **performance(daily, values)))
    return pd.DataFrame(rows)


def matched_subsets(base: pd.DataFrame, kept: pd.DataFrame, axis: pd.DatetimeIndex, model: str, seed: int) -> tuple[dict, pd.DataFrame, dict]:
    rng = np.random.default_rng(seed)
    groups = base.groupby(["year", "side", "signal_hour"], sort=True)
    keep_ids = set(kept.event_id.astype(int))
    pools = [(group.event_id.to_numpy(int), int(group.event_id.isin(keep_ids).sum())) for _, group in groups]
    day_index = axis.get_indexer(base.date)
    if (day_index < 0).any():
        raise ValueError("Subset event cannot be mapped to the fixed cash-day axis.")
    values = base.net_mnq.to_numpy(float)
    if not np.array_equal(base.event_id.to_numpy(int), np.arange(len(base))):
        raise ValueError("Matched subset IDs are not aligned to the immutable BASE row order.")
    actual_daily = daily_values(kept, "net_mnq", axis).to_numpy()
    actual_total, actual_dd = float(actual_daily.sum()), R.max_dd(actual_daily)
    selected_ids = np.zeros((RANDOM_SUBSETS, len(kept)), dtype=np.int32)
    paths = np.zeros((RANDOM_SUBSETS, len(axis)), dtype=float)
    totals, dds = [], []
    for run in range(RANDOM_SUBSETS):
        chosen = np.sort(np.concatenate([rng.choice(pool, size=nkeep, replace=False) for pool, nkeep in pools])).astype(np.int32)
        selected_ids[run] = chosen
        np.add.at(paths[run], day_index[chosen], values[chosen])
        totals.append(float(paths[run].sum())); dds.append(R.max_dd(paths[run]))
    totals, dds = np.asarray(totals), np.asarray(dds)
    joint = (actual_total > totals) & (actual_dd < dds)
    removed = base[~base.event_id.isin(keep_ids)]
    diagnostics = dict(model=model, seed=seed, samples=RANDOM_SUBSETS,
        strata="year x side x completed-signal hour", paths_are_nonexecutable_diagnostics=True,
        base_trades=len(base), kept_trades=len(kept), removed_trades=len(removed),
        base_net=float(base.net_mnq.sum()), kept_net=actual_total, removed_net=float(removed.net_mnq.sum()),
        removed_average=float(removed.net_mnq.mean()) if len(removed) else None,
        removed_t=G.tstat(removed.net_mnq), actual_kept_max_dd=actual_dd,
        jointly_beaten_fraction=float(joint.mean()), joint_comparison="strictly higher profit AND strictly lower max drawdown",
        random_profit_at_least_actual_p=float((1 + np.sum(totals >= actual_total)) / (RANDOM_SUBSETS + 1)),
        random_dd_at_most_actual_p=float((1 + np.sum(dds <= actual_dd)) / (RANDOM_SUBSETS + 1)))
    table = pd.DataFrame(dict(model=model, run=np.arange(RANDOM_SUBSETS), net_mnq=totals,
                              max_dd_mnq=dds, actual_jointly_beats=joint))
    arrays = {f"{model}_selected_event_ids": selected_ids, f"{model}_daily_mnq": paths}
    return diagnostics, table, arrays


@contextmanager
def lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "design.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def design(prereg: str) -> dict:
    with lock():
        gross_binding, events, calendar, binding = verify(prereg)
        started = G.utcnow()
        with (OUT / "design_attempts.jsonl").open("a") as handle:
            handle.write(json.dumps(dict(started_utc=started, script_sha256=G.sha(ROOT / SCRIPT), prereg=prereg, models=list(MODELS))) + "\n")
        grid, native_audit = G.native_grid(gross_binding)
        base, execution_audit = replay_base(grid, events)
        calendar_audit, axis = daily_calendar(grid, calendar, events)
        tickets = {"BASE": base, **{model: base[base[f"keep_{model}"]].copy() for model in MODELS[1:]}}
        for model, rows in tickets.items():
            if not rows.event_id.is_unique or not set(rows.event_id) <= set(base.event_id):
                raise ValueError("Filter is not an exact original-ticket subset.")
        metrics = all_metrics(tickets, axis)
        filter_rows, subset_tables, subset_arrays = {}, [], {}
        for i, model in enumerate(MODELS[1:]):
            diagnostics, table, arrays = matched_subsets(base, tickets[model], axis, model, SEED + i)
            filter_rows[model] = diagnostics; subset_tables.append(table); subset_arrays.update(arrays)
        subset_arrays.update(daily_dates=axis.strftime("%Y-%m-%d").to_numpy(dtype="U10"),
                             base_event_ids=base.event_id.to_numpy(np.int32))
        primary = metrics[(metrics.model == "STRICT30") & metrics.period.eq("2018-22") & metrics.side.eq("all") & metrics.basis.eq("MNQ")].iloc[0]
        stress = tickets["STRICT30"].net_mnq_4tick.sum()
        year_net = tickets["STRICT30"].groupby("year").net_mnq.sum().reindex(G.YEARS, fill_value=0)
        basic_gates = dict(at_least_100_trades=int(primary.trades) >= 100, positive_net=primary.total > 0,
            trade_t_at_least_2=primary.t_trade is not None and primary.t_trade >= 2,
            daily_nw5_at_least_1_5=primary.t_nw5 is not None and primary.t_nw5 >= 1.5,
            profit_factor_at_least_1_2=primary.profit_factor >= 1.2,
            at_least_4_positive_years=int((year_net > 0).sum()) >= 4, positive_four_tick_stress=stress > 0)
        f = filter_rows["STRICT30"]
        filter_gates = dict(kept_total_at_least_base=f["kept_net"] >= f["base_net"],
            removed_total_negative=f["removed_net"] < 0,
            removed_mean_negative=f["removed_average"] is not None and f["removed_average"] < 0,
            matched_joint_beat_at_least_90pct=f["jointly_beaten_fraction"] >= 0.90)
        quality_gates = dict(complete_held_paths=execution_audit["total_invalid_held_minutes"] == 0,
                             exits_before_1559=execution_audit["exits_after_1559"] == 0,
                             exact_base_ticket_subsets=True, unchanged_frozen_source=True)
        passed = bool(all(basic_gates.values()) and all(filter_gates.values()) and all(quality_gates.values()))
        metadata = dict(phase="design", period="2018-22 only", daily_schema=DAILY_SCHEMA,
            warmup_first_eligible_date=axis.min().date().isoformat(), design_last_date=axis.max().date().isoformat(),
            daily_calendar_basis="All normal and early cash days after first known prior-ATR warmup; excluded entry days remain zero.",
            native_audit=native_audit, execution_audit=execution_audit, v2_evaluations_before=0, v2_evaluations_after=3,
            v2_hypotheses=1, prior_t6_evaluations=65, cumulative_t6_plus_v2_evaluations=68,
            new_strict_formulas=1, repeated_reference_models=["BASE", "LEGACY"], nonexecutable_random_subset_paths=2000,
            initial_zero_drawdown_correction=True, validation_run=False, account_tests_run=False,
            next_action="Immediate current personal19 design bench if passed; otherwise close H01. No additional robustness/2023+ access here.")
        verify_runtime_binding(binding)
        for model, rows in tickets.items():
            G.csv_once(OUT / f"design_{model}_trades.csv", rows)
        G.csv_once(OUT / "design_metrics.csv", metrics)
        for suffix, field in (("", "net_mnq"), ("_nq", "net_nq"), ("_mnq_4tick", "net_mnq_4tick"), ("_nq_4tick", "net_nq_4tick")):
            daily = pd.DataFrame({model: daily_values(rows, field, axis) for model, rows in tickets.items()})
            daily.index.name = "date"
            G.csv_once(OUT / f"design_daily{suffix}.csv", daily.reset_index())
        G.csv_once(OUT / "design_calendar_audit.csv", calendar_audit)
        G.csv_once(OUT / "design_matched_subsets.csv", pd.concat(subset_tables, ignore_index=True))
        subset_buffer = io.BytesIO(); np.savez_compressed(subset_buffer, **subset_arrays)
        G.write_once(OUT / "design_matched_subset_paths.npz", subset_buffer.getvalue())
        dump(OUT / "design_filter_diagnostics.json", filter_rows)
        dump(OUT / "design_input_binding.json", binding)
        dump(OUT / "design_metadata.json", metadata)
        gate = dict(passed=passed, design_passed=passed, primary="STRICT30", selected="STRICT30" if passed else None,
            basic_gates=basic_gates, filter_gates=filter_gates, quality_gates=quality_gates,
            primary_metrics=primary.to_dict(), primary_four_tick_net=float(stress),
            filter_diagnostics=f, configurations_evaluated=list(MODELS), counted_evaluations=3,
            hypotheses=1, validation_authorized=False, next_stage="personal19_design_bench" if passed else "close_H01",
            downstream_requires_success_marker_and_all_artifact_hashes=True)
        # Publication of a gate alone is never sufficient: require the final
        # completed marker and every bound artifact before any downstream use.
        verify_runtime_binding(binding)
        dump(OUT / "design_gate.json", gate)
        # Explicit outputs avoid binding a still-open stdout log or unrelated
        # synthetic fixture that happens to share the design_ prefix.
        artifact_names = ([f"design_{model}_trades.csv" for model in MODELS]
            + ["design_metrics.csv", "design_daily.csv", "design_daily_nq.csv", "design_daily_mnq_4tick.csv", "design_daily_nq_4tick.csv",
               "design_calendar_audit.csv", "design_matched_subsets.csv", "design_matched_subset_paths.npz",
               "design_filter_diagnostics.json", "design_input_binding.json", "design_metadata.json", "design_gate.json"])
        verify_runtime_binding(binding)
        marker = dict(phase="design", passed=passed, design_passed=passed, selected=gate["selected"],
            started_utc=started, completed_utc=G.utcnow(), prereg=prereg,
            implementation_commit=binding["implementation_commit"], script_sha256=G.sha(ROOT / SCRIPT),
            gross_marker_sha256=binding["gross_marker_sha256"],
            artifacts_sha256={name: G.sha(OUT / name) for name in artifact_names}, daily_schema=DAILY_SCHEMA,
            warmup_first_eligible_date=metadata["warmup_first_eligible_date"], design_last_date=metadata["design_last_date"],
            counted_evaluations=3, base_execution_replays=1, hypotheses=1,
            validation_run=False, account_tests_run=False, runtime_versions=G.runtime_versions())
        dump(OUT / "design_verified_execution.json", marker)
        with (OUT / "design_attempts.jsonl").open("a") as handle:
            handle.write(json.dumps(dict(completed_utc=marker["completed_utc"], completed=True, phase="design", passed=passed, counted_evaluations=3)) + "\n")
        return gate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["fixtures", "design"], required=True)
    parser.add_argument("--prereg")
    args = parser.parse_args()
    if args.phase == "fixtures":
        result = fixtures()
        dump(OUT / f"design_synthetic_checks_{result['script_sha256'][:12]}.json", result)
    else:
        if not args.prereg:
            parser.error("Counted design requires the committed --prereg.")
        result = design(args.prereg)
    print(json.dumps(safe_json(result), allow_nan=False))


if __name__ == "__main__":
    main()
