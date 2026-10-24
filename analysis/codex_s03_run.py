"""Reproduce the four fixed S03 profiles behind the committed stage gates.

PYTHONPATH=analysis /workspace/venvs/thebeginning/bin/python \
  analysis/codex_s03_run.py --design --prereg-commit d9ef177df4f2a788dc4e9d108c4cdc1fbc4880ad

Recent history additionally requires the root's saved passing design gate.
This module is inert on import and never calculates recent features in design.
"""

import argparse
import hashlib
import json
from pathlib import Path
import pickle
import platform
import time

import numpy as np
import pandas as pd

from codex_s03_replay import prepare_features, run, synthetic_checks

PREREG_COMMIT = "d9ef177df4f2a788dc4e9d108c4cdc1fbc4880ad"
PLAN_SHA256 = "ec135137d244afc7d24ca53f62bc77936e07d5e64259757d85dcc20ce3d2d879"
SOURCE_SHA256 = "05a176b0c4f6804d48d427ad484175076d125a61b62122736c34c6797c0d2b52"
PROFILES = {
    "V2": dict(stop_sigma=.4, anchor=831, slip_ticks=1.),
    "V1": dict(stop_sigma=0., anchor=831, slip_ticks=1.),
    "C2": dict(stop_sigma=.4, anchor=830, slip_ticks=1.),
    "E2": dict(stop_sigma=.4, anchor=831, slip_ticks=3.),
}
AUDIT_TABLE_COLUMNS = {
    "orders": ["order_id", "name", "status", "global_decision", "fill_minute"],
    "day_audit": ["day", "date", "account_eligible", "unknown_held_minutes", "unmatched_orders"],
    "unknown_held_minutes": ["day", "date", "j", "global_minute", "side", "entry_order_id", "reason"],
    "delayed_orders": ["order_id", "delay_minutes", "fill_minute"],
    "unmatched_orders": ["order_id", "name", "status", "global_decision", "fill_minute"],
}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _plain(value):
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(x) for x in value]
    if isinstance(value, np.generic):
        return _plain(value.item())
    if isinstance(value, (pd.Timestamp, np.datetime64)):
        return None if pd.isna(value) else pd.Timestamp(value).isoformat()
    if value is pd.NaT or value is pd.NA:
        return None
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, Path):
        return str(value)
    return value


def _json(path, value):
    Path(path).write_text(json.dumps(_plain(value), indent=2, allow_nan=False) + "\n")


def _summary(trades, years):
    x = trades.net.to_numpy(float)
    sd = x.std(ddof=1) if len(x) > 1 else np.nan
    annual = trades.groupby(pd.DatetimeIndex(trades.date).year).net.sum()
    annual = annual.reindex(range(years[0], years[1] + 1), fill_value=0.)
    return dict(trades=len(trades), total_net=float(x.sum()),
                mean_net=float(x.mean()) if len(x) else None,
                win_rate=float((x > 0).mean()) if len(x) else None,
                trade_t=float(x.mean() / sd * np.sqrt(len(x))) if sd > 0 else None,
                positive_years=int((annual > 0).sum()),
                annual_net={str(y): float(net) for y, net in annual.items()})


def _save_attrs(output, prefix, attrs):
    """CSV for tabular attrs; JSON only contains plain metadata/references."""
    metadata, tables = {}, {}
    for key, value in attrs.items():
        if isinstance(value, pd.DataFrame):
            table = value.copy()
            if len(table.columns) == 0:
                table = pd.DataFrame(columns=AUDIT_TABLE_COLUMNS.get(key, ["empty"]))
            path = output / f"{prefix}_{key}.csv"
            table.to_csv(path, index=False)
            tables[key] = dict(path=str(path), sha256=sha256(path), rows=len(table))
        elif key == "censored":
            path = output / f"{prefix}_censored.json"
            _json(path, value)
            tables[key] = dict(path=str(path), sha256=sha256(path), rows=len(value))
        else:
            metadata[key] = value
    metadata["audit_tables"] = tables
    return metadata


def run_profiles(*, stage, prereg_commit, gate_file=None,
                 cache_path="scratch_data/g24.pkl",
                 output_dir="analysis/outputs/codex_s03_noisearea"):
    if prereg_commit != PREREG_COMMIT:
        raise ValueError("preregistration commit does not match the frozen S03 test")
    if stage not in {"design", "recent"}:
        raise ValueError("stage must be design or recent")
    gate = None
    if stage == "recent":
        if gate_file is None:
            raise ValueError("recent replay requires the root's saved passing design gate")
        gate = json.loads(Path(gate_file).read_text())
        gate_commit = gate.get("prereg_commit", gate.get("prereg_sha"))
        if gate.get("passed") is not True or gate_commit != PREREG_COMMIT:
            raise ValueError("recent gate must explicitly pass and match the preregistration commit")
        if gate.get("plan_sha256", PLAN_SHA256) != PLAN_SHA256:
            raise ValueError("recent gate plan hash does not match the frozen plan")
    plan = Path("agents/codex/plans/s03_noisearea.md")
    source = Path("agents/codex/inputs/s03_noisearea/source.html")
    if sha256(plan) != PLAN_SHA256:
        raise ValueError("local S03 plan differs from the published preregistration")
    if sha256(source) != SOURCE_SHA256:
        raise ValueError("uploaded HTML differs from the frozen source hash")
    started = time.perf_counter()
    checks = synthetic_checks()
    cache_path = Path(cache_path)
    cache_hash = sha256(cache_path)
    with cache_path.open("rb") as stream:
        g = pickle.load(stream)
    years = (2018, 2022) if stage == "design" else (2023, pd.Timestamp(g.ts[-1]).year)
    end = pd.Timestamp(years[1] + 1, 1, 1)
    allow_recent = stage == "recent"
    feature_started = time.perf_counter()
    features_by_anchor = {anchor: prepare_features(g, anchor=anchor, end=end,
        allow_post2022=allow_recent) for anchor in (831, 830)}
    feature_seconds = time.perf_counter() - feature_started
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for anchor, features in features_by_anchor.items():
        if len(features) and pd.Timestamp(features.date.max()) >= end:
            raise AssertionError("feature period includes prices beyond the stage boundary")
        history = features.loc[features.history_end.notna()]
        if len(history) and not (history.history_end < history.date).all():
            raise AssertionError("sigma includes a current or later cash session")
        name = f"{stage}_features" if anchor == 831 else f"{stage}_C2_features"
        features.to_pickle(output / f"{name}.pkl")
        features.attrs["sessions"].to_csv(output / f"{name}_sessions.csv", index=False)
    summaries = {}
    for profile, parameters in PROFILES.items():
        profile_started = time.perf_counter()
        trades, selected_features = run(g, years=years, allow_post2022=allow_recent,
            features=features_by_anchor[parameters["anchor"]], **parameters)
        if profile in {"V2", "C2"}:
            feature_name = f"{stage}_features.pkl" if profile == "V2" else f"{stage}_C2_features.pkl"
            selected_features.to_pickle(output / feature_name)
        elapsed = time.perf_counter() - profile_started
        prefix = f"{stage}_{profile}"
        ledger = output / f"{prefix}.csv"
        trades.to_csv(ledger, index=False)
        attr_metadata = _save_attrs(output, prefix, trades.attrs)
        expected = ((trades.raw_exit - trades.raw_entry) * trades.side * 20.
                    - 7.25 - trades.slippage_usd)
        error = float(np.max(np.abs(expected - trades.net))) if len(trades) else 0.
        slipped = (trades.exit - trades.entry) * trades.side * 20. - 7.25
        slipped_error = float(np.max(np.abs(slipped - trades.net))) if len(trades) else 0.
        if not np.isfinite(error) or error > 1e-7 or slipped_error > 1e-7:
            raise AssertionError(f"{profile} ledger cost reconciliation failed")
        orders = trades.attrs["orders"]
        summary = _summary(trades, years)
        audit = dict(stage=stage, profile=profile, prereg_commit=PREREG_COMMIT,
            plan_sha256=PLAN_SHA256, source_sha256=SOURCE_SHA256,
            cache_path=str(cache_path), cache_sha256=cache_hash,
            parameters=parameters, years=list(years), elapsed_seconds=elapsed,
            raw_net_reconciliation_max_abs=error,
            slipped_net_reconciliation_max_abs=slipped_error,
            commission_per_NQ=7.25, commission_total=7.25 * len(trades),
            slippage_total=float(trades.slippage_usd.sum()),
            first_entry=str(trades.date.min()) if len(trades) else None,
            last_exit=str(trades.exit_date.max()) if len(trades) else None,
            cross_date_trades=int(trades.carry.sum()),
            unknown_held_minutes_count=len(trades.attrs["unknown_held_minutes"]),
            delayed_order_count=len(trades.attrs["delayed_orders"]),
            unmatched_order_count=len(trades.attrs["unmatched_orders"]),
            censored_position_count=len(trades.attrs["censored"]),
            order_status_counts=orders.status.value_counts().to_dict() if len(orders) else {},
            feature_rows=len(selected_features), feature_last_date=str(selected_features.date.max()),
            no_current_or_future_session_in_sigma=True,
            prices_exclusive_end=end, ledger_path=str(ledger), ledger_sha256=sha256(ledger),
            replay_attrs=attr_metadata, **summary)
        _json(output / f"{prefix}_audit.json", audit)
        summaries[profile] = audit
        print(f"{stage} {profile}: n={summary['trades']} net={summary['total_net']:.2f} "
              f"mean={summary['mean_net']} t={summary['trade_t']} positive_years={summary['positive_years']} "
              f"unknown_held_minutes={audit['unknown_held_minutes_count']} "
              f"censored={audit['censored_position_count']} unmatched={audit['unmatched_order_count']} "
              f"seconds={elapsed:.2f}", flush=True)
    manifest = dict(stage=stage, prereg_commit=PREREG_COMMIT, plan_sha256=PLAN_SHA256,
        source_sha256=SOURCE_SHA256, cache_path=str(cache_path), cache_sha256=cache_hash,
        cache_first_date=pd.Timestamp(g.ts[0]), cache_last_date=pd.Timestamp(g.ts[-1]),
        years=list(years), prices_exclusive_end=end,
        python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__,
        synthetic_checks=checks, feature_seconds=feature_seconds,
        feature_rows_by_anchor={str(anchor): len(f) for anchor, f in features_by_anchor.items()},
        elapsed_seconds=time.perf_counter() - started,
        gate_path=str(gate_file) if gate_file is not None else None,
        gate_sha256=sha256(gate_file) if gate_file is not None else None,
        script_sha256=sha256(__file__), replay_sha256=sha256("analysis/codex_s03_replay.py"),
        calendar_sha256=sha256("analysis/codex_s03_calendar.py"),
        profiles={name: {key: audit[key] for key in (
            "trades", "total_net", "mean_net", "trade_t", "positive_years", "annual_net",
            "unknown_held_minutes_count", "censored_position_count", "unmatched_order_count")}
            for name, audit in summaries.items()})
    _json(output / f"{stage}_manifest.json", manifest)
    return summaries


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    stage = parser.add_mutually_exclusive_group(required=True)
    stage.add_argument("--design", action="store_true")
    stage.add_argument("--recent", action="store_true")
    parser.add_argument("--prereg-commit", required=True)
    parser.add_argument("--gate-file")
    parser.add_argument("--cache", default="scratch_data/g24.pkl")
    parser.add_argument("--output", default="analysis/outputs/codex_s03_noisearea")
    args = parser.parse_args()
    run_profiles(stage="design" if args.design else "recent", prereg_commit=args.prereg_commit,
                 gate_file=args.gate_file, cache_path=args.cache, output_dir=args.output)
