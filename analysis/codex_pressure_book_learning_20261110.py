"""Frozen archival-book input test using the batch-2 label cache.

No actual cache, market inputs, fits or return outcomes are read on import or by
--phase self-check. Real study operations require an exact committed protocol.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import subprocess
import sys

sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
import sklearn

import codex_pressure_learning_20261110 as L
import codex_pressure_build_20261110_inputs as I
import codex_pressure_build_20261110_replay as E
import codex_pressure_book_20261110_inputs as B
import codex_cash_open_repair as C

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_pressure_book_learning_20261110"
PLAN = "agents/codex/plans/pressure_book_learning_20261110.md"
EVIDENCE = "agents/codex/evidence/pressure_book_learning_20261110.md"
CACHE_COMMIT = "0d61f59e30304a5a9850ef1a20b33a2d1f04cc2d"
CACHE_PATH = "analysis/outputs/codex_pressure_learning_20261110/features_and_labels.csv.gz"
NATIVE_MANIFEST = "agents/codex/inputs/bridge_native_2018_22_20261108/transfer_manifest.json"
CODE = ["analysis/codex_pressure_book_learning_20261110.py",
        "analysis/codex_pressure_book_20261110_inputs.py",
        "analysis/codex_pressure_learning_20261110.py",
        "analysis/codex_pressure_build_20261110_inputs.py",
        "analysis/codex_pressure_build_20261110_replay.py",
        "analysis/grid.py", "analysis/grid24.py", "analysis/metrics.py",
        "analysis/codex_cash_open_repair.py", "analysis/codex_s03_calendar.py"]
MODELS = ("HGB_BOOK", "RIDGE_BOOK", "HGB_NOBOOK")
SELECTABLE = ("HGB_BOOK", "RIDGE_BOOK")
RENAME_MODELS = {"HGB": "HGB_BOOK", "RIDGE": "RIDGE_BOOK", "HGB_PRICE": "HGB_NOBOOK"}
NOBOOK_FEATURES = list(L.FEATURES)  # Includes all original aggressor q features.
BOOK_FEATURES = ["spread", "topimb", "depth10imb", "depth50imb", "near_fraction", "log_depth10_ratio",
                 "log_depth10_growth5min", "spread_change5min", "imbalance_change5min"]
BOOK_DIRECTIONAL = ("topimb", "depth10imb", "depth50imb", "imbalance_change5min")
ADDED_FEATURES = BOOK_FEATURES + ["capacity_buy", "capacity_sell"] + ["side_x_" + k for k in BOOK_DIRECTIONAL] + ["side_x_capacity_difference"]
FEATURES = NOBOOK_FEATURES + ADDED_FEATURES


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _dump(path, value):
    C.write(path, json.dumps(value, indent=2, default=str, allow_nan=True) + "\n")


def _csv(path, frame):
    payload = frame.to_csv(index=False).encode()
    C.write(path, gzip.compress(payload, mtime=0) if str(path).endswith(".gz") else payload)


def _boolean(values, name, *, missing_false=False):
    if pd.api.types.is_bool_dtype(values):
        return values.fillna(False).astype(bool)
    translated = values.map({True: True, False: False, "True": True, "False": False,
                             "true": True, "false": False, 1: True, 0: False})
    if missing_false:
        translated = translated.where(values.notna(), False)
    if translated.isna().any():
        raise ValueError(f"Unknown boolean value in {name}")
    return translated.astype(bool)


def load_cached_samples(root=ROOT):
    """Read exact archived cache bytes only after the caller's protocol binding.

    No label is recomputed or clipped. Unknown label outcomes are retained for
    inference; the inherited monthly trainer handles their historical admission.
    """
    payload = (Path(root) / CACHE_PATH).read_bytes()
    archived = subprocess.check_output(["git", "show", f"{CACHE_COMMIT}:{CACHE_PATH}"], cwd=ROOT)
    if payload != archived:
        raise ValueError("Cached features/labels differ from the frozen batch-2 Git object")
    data = pd.read_csv(io.BytesIO(payload), compression="gzip")
    required = set(NOBOOK_FEATURES + L.SIGNAL_FIELDS + ["label_net_R", "label_valid", "label_kind", "label_known_at"])
    if not required.issubset(data.columns):
        raise ValueError(f"Cached schema changed: {required - set(data.columns)}")
    for column in ("date", "input_last_time", "label_known_at"):
        data[column] = pd.to_datetime(data[column], errors="raise")
        if data[column].isna().any(): raise ValueError(f"Missing cached timestamp: {column}")
    data["date"] = data.date.dt.normalize()
    if len(data) and (data.date.min() < pd.Timestamp("2018-01-01") or data.date.max() >= pd.Timestamp("2023-01-01")):
        raise ValueError("Cache contains dates outside the frozen design period")
    data["label_valid"] = _boolean(data.label_valid, "label_valid")
    if "label_full_horizon_valid" in data:
        data["label_full_horizon_valid"] = _boolean(data.label_full_horizon_valid, "label_full_horizon_valid")
    if data.duplicated(["day", "signal_j", "side"]).any():
        raise ValueError("Duplicate cached side/decision")
    if not data.side.isin((-1, 1)).all():
        raise ValueError("Unexpected cached side")
    expected_time = data.date + pd.to_timedelta(data.signal_j, unit="min")
    if not data.input_last_time.eq(expected_time).all():
        raise ValueError("Cached feature clock is inconsistent")
    if not np.isfinite(data[NOBOOK_FEATURES]).all(axis=None):
        raise ValueError("Nonfinite original feature in the frozen cache")
    receipt = dict(source_commit=CACHE_COMMIT, source_path=CACHE_PATH,
                   source_git_blob=subprocess.check_output(["git", "rev-parse", f"{CACHE_COMMIT}:{CACHE_PATH}"], cwd=ROOT, text=True).strip(),
                   compressed_sha256=hashlib.sha256(payload).hexdigest(), rows=len(data),
                   labels_regenerated=False, label_values_changed=False,
                   rule="Exact batch-2 fixed-bracket net payoffs; no future-label filter on forecast eligibility")
    return data, receipt


def add_book_features(samples, endpoints, native_bars):
    """Attach exact known decision-endpoint context to both cached side rows.

    `label_valid`, label values, label horizon and future prices do not determine
    admission. Unknown current/lag/baseline book state remains explicit in audit.
    """
    if list(B.FEATURES) != BOOK_FEATURES:
        raise ValueError("Book adapter feature definitions changed")
    if endpoints.index.has_duplicates or native_bars.index.has_duplicates:
        raise ValueError("Endpoint and native-bar keys must be unique")
    if set(ADDED_FEATURES) & set(samples.columns):
        raise ValueError("Book features already present in the base cache")
    data = samples.copy().reset_index(drop=True)
    key = pd.DatetimeIndex(data.date + pd.to_timedelta(data.signal_j, unit="min"))
    context = endpoints.reindex(key).reset_index(drop=True)
    flow = native_bars.reindex(key)[["buy", "sell"]].reset_index(drop=True)
    required = BOOK_FEATURES + ["bid_depth10", "ask_depth10", "book_features_known"]
    if not set(required).issubset(context):
        raise ValueError(f"Missing book endpoint context: {set(required) - set(context)}")
    current_known = _boolean(context.book_features_known, "book_features_known", missing_false=True)
    quantities_known = np.isfinite(flow).all(axis=1) & flow.ge(0).all(axis=1)
    depth_known = np.isfinite(context[["bid_depth10", "ask_depth10"]]).all(axis=1) & context[["bid_depth10", "ask_depth10"]].gt(0).all(axis=1)
    for name in BOOK_FEATURES:
        data[name] = context[name].to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        data["capacity_buy"] = np.log1p(flow.buy.to_numpy() / context.ask_depth10.where(context.ask_depth10 > 0).to_numpy())
        data["capacity_sell"] = np.log1p(flow.sell.to_numpy() / context.bid_depth10.where(context.bid_depth10 > 0).to_numpy())
    for name in BOOK_DIRECTIONAL:
        data["side_x_" + name] = data.side * data[name]
    data["side_x_capacity_difference"] = data.side * (data.capacity_buy - data.capacity_sell)
    finite = np.isfinite(data[FEATURES]).all(axis=1)
    known = current_known & quantities_known & depth_known & finite
    # Include each availability component in the saved receipt, without making
    # the model consume these flags as outcome-selected features.
    data["book_features_known"] = known
    data["book_input_time"] = key
    data["book_status"] = context.book_status.fillna("ENDPOINT_UNKNOWN").to_numpy() if "book_status" in context else np.where(known, "KNOWN", "UNKNOWN")
    audit = dict(base_paired_rows=len(data), retained_paired_rows=int(known.sum()),
                 retained_decisions=int(data.loc[known, ["day", "signal_j"]].drop_duplicates().shape[0]),
                 unknown_paired_rows=int((~known).sum()), endpoint_status_counts=data.book_status.value_counts().to_dict(),
                 book_context_known_rows=int(current_known.sum()), capacities_require_positive_depth=True,
                 inference_filter="Only known finite current/lag/baseline book context and native bar capacity inputs; never label_valid",
                 features=FEATURES, no_book_control_features=NOBOOK_FEATURES,
                 capacity="log1p(native completed five-minute buy/ask_depth10), log1p(sell/bid_depth10)",
                 capacity_limit="Five-minute historical trades divided by endpoint archival depth; no observed queue depletion or full LOB gaps",
                 conditional_archive=True)
    return data.loc[known].copy().reset_index(drop=True), audit


def configured_learner():
    """Fresh source-module namespace; original module/globals/files stay intact."""
    spec = importlib.util.spec_from_file_location("_pressure_book_isolated_monthly_learner", Path(L.__file__))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.FEATURES = list(FEATURES)
    module.PRICE_FEATURES = list(NOBOOK_FEATURES)
    module.MODELS = ("HGB", "RIDGE", "HGB_PRICE")
    module.SELECTABLE = ("HGB", "RIDGE")
    return module


def fit_predict(data, calendar):
    learner = configured_learner()
    signal, predictions, fits = learner.fit_predict(data, calendar, models=("HGB", "RIDGE", "HGB_PRICE"))
    renamed = {}
    for internal, external in RENAME_MODELS.items():
        frame = signal[internal].copy()
        if "model" in frame: frame["model"] = external
        renamed[external] = frame
    for frame in (predictions, fits):
        if "model" in frame: frame["model"] = frame.model.map(RENAME_MODELS)
    return renamed, predictions, fits


def _basic_gates(value, trades):
    s = value["summary"]
    return dict(trades=s["trades"] >= 250, dates=trades.date.nunique() >= 100,
                long_count=value["long_trades"] >= 25, short_count=value["short_trades"] >= 25,
                net=s["total"] > 0, micro_net=value["micro"]["total"] > 0,
                trade_t=s["t_trade"] >= 2, daily_nw5=s["t_nw5"] >= 1.5,
                profit_factor=s["profit_factor"] >= 1.2, years=value["positive_years"] >= 4,
                stress_net=value["stress"]["total"] > 0, stop_first_net=value["stop_first"]["total"] > 0,
                held_paths=value["execution"]["unknown_held_path_trades"] == 0)


def run(prereg, *, out=OUT, root=ROOT):
    """Actual-design runner; all original labels remain fixed and Git-bound."""
    out, root = Path(out), Path(root)
    if root.resolve() != ROOT.resolve():
        raise ValueError("This protocol binds the current research worktree inputs only")
    paths = [PLAN, EVIDENCE] + CODE + [NATIVE_MANIFEST]
    for name in paths:
        frozen = subprocess.check_output(["git", "show", f"{prereg}:{name}"], cwd=ROOT)
        if frozen != (ROOT / name).read_bytes():
            raise ValueError(f"Protocol/code not frozen: {name}")
    if (out / "results.json").exists():
        raise ValueError("Existing outcomes cannot be overwritten")
    out.mkdir(parents=True, exist_ok=True)
    _dump(out / "binding.json", dict(prereg=prereg, files={p: sha(ROOT / p) for p in paths},
                                     label_cache_commit=CACHE_COMMIT, label_cache_path=CACHE_PATH,
                                     models=list(MODELS), selectable_order=list(SELECTABLE),
                                     new_economic_definitions=3, labels_regenerated=False,
                                     prior_study_definitions=12, cumulative_new_study_definitions=15,
                                     older_book_searches=39, older_book_searches_retained=True,
                                     sklearn_version=sklearn.__version__, validation_outcomes_read=False))
    cached, cache_audit = load_cached_samples(root)
    native = I.load_design_native(root=root)
    grid = I.make_grid(native)
    calendar = pd.DatetimeIndex([d for d in pd.to_datetime(grid.ts) if C.normal_cash(d)])
    mapping = {pd.Timestamp(d): i for i, d in enumerate(grid.ts)}
    if not cached.date.map(mapping).eq(cached.day).all():
        raise ValueError("Cached grid-day mapping differs from admitted native input")
    book, book_audit = B.load_book_minutes(root=root, native_minutes=native)
    endpoints = B.make_book_features(book, calendar)
    bars = I.complete5min_ohlcv(native)
    data, feature_audit = add_book_features(cached, endpoints, bars)
    _dump(out / "input_and_cache_audit.json", dict(cache=cache_audit, native=native.attrs.get("input_audit", {}),
                                                  book=book_audit, endpoints=endpoints.attrs.get("input_audit", {}),
                                                  attachment=feature_audit))
    _csv(out / "eligible_features_and_fixed_labels.csv.gz", data)
    signals, predictions, fits = fit_predict(data, calendar)
    _csv(out / "predictions.csv.gz", predictions); _csv(out / "monthly_fits.csv", fits)
    summaries, tables, ledgers = {}, [], {}
    for name in MODELS:
        _csv(out / f"{name}_signals.csv.gz", signals[name])
        trades, execution = E.replay(signals[name], grid=grid, max_trades=4)
        ledgers[name] = trades
        _csv(out / f"{name}_trades.csv.gz", trades)
        known = not bool(execution["unknown_held_path_trades"])
        table = E.metrics_table(trades, calendar, allow_unknown=not known)
        table["model"] = name; tables.append(table)
        daily = trades.groupby("date").net.sum().reindex(calendar, fill_value=0)
        _csv(out / f"{name}_daily.csv", daily.rename("net").rename_axis("date").reset_index())
        summaries[name] = dict(summary=E.metrics_summary(trades, calendar, allow_unknown=not known),
                               micro=E.metrics_summary(trades, calendar, "net_mnq", allow_unknown=not known),
                               stress=E.metrics_summary(trades, calendar, "stress_four_ticks", allow_unknown=not known),
                               stop_first=E.metrics_summary(trades, calendar, "stop_first_net", allow_unknown=not known),
                               execution=execution, positive_years=int((daily.groupby(daily.index.year).sum() > 0).sum()),
                               long_trades=int((trades.side == 1).sum()), short_trades=int((trades.side == -1).sum()))
    _csv(out / "metrics.csv", pd.concat(tables, ignore_index=True))
    gates = {name: _basic_gates(summaries[name], ledgers[name]) for name in SELECTABLE}
    result = dict(prereg=prereg, stats=summaries, basic_gates=gates,
                  basic_pass_candidates=[name for name in SELECTABLE if all(gates[name].values())],
                  selected=None, design_gate_complete=False, validation_allowed=False,
                  new_economic_definitions=3, prior_study_definitions=12,
                  cumulative_new_study_definitions=15, older_book_searches=39,
                  selection_policy="HGB_BOOK then RIDGE_BOOK only after all frozen gates; HGB_NOBOOK unselectable",
                  control_limit="HGB_BOOK versus HGB_NOBOOK isolates added inputs within the same estimator; RIDGE_BOOK versus HGB_NOBOOK is whole-policy only",
                  source_gate_complete=False, original_receipt_build_revision_vintages_verified=False,
                  interpretation="Conditional archival bar-state fragility, not native book gaps or verified receipt/queue information")
    _dump(out / "results.json", result)
    print(pd.DataFrame({name: item["summary"] for name, item in summaries.items()}).T.to_string(), flush=True)
    print(json.dumps({"basic_gates": gates, "basic_pass_candidates": result["basic_pass_candidates"]}, indent=2), flush=True)
    return result


def self_check():
    """Planted joins/configuration only; no cache/input/model-fit/outcome reads."""
    stamp = pd.Timestamp("2020-02-03 09:05")
    base = pd.DataFrame([{**{name: 0. for name in NOBOOK_FEATURES},
                          "date": stamp.normalize(), "day": 0, "signal_j": 545,
                          "side": side, "label_valid": False, "label_net_R": np.nan}
                         for side in (1, -1)])
    endpoint = pd.DataFrame({name: [0.] for name in BOOK_FEATURES}, index=[stamp])
    endpoint["spread"] = 1.; endpoint["topimb"] = .2
    endpoint["bid_depth10"] = 100.; endpoint["ask_depth10"] = 100.
    endpoint["book_features_known"] = True; endpoint["book_status"] = "KNOWN"
    flow = pd.DataFrame({"buy": [60.], "sell": [40.]}, index=[stamp])
    joined, _ = add_book_features(base, endpoint, flow)
    assert len(joined) == 2 and not joined.label_valid.any()
    np.testing.assert_allclose(joined.capacity_buy, np.log1p(.6))
    np.testing.assert_allclose(joined.capacity_sell, np.log1p(.4))
    np.testing.assert_allclose(joined.side_x_topimb, [.2, -.2])
    np.testing.assert_allclose(joined.side_x_capacity_difference,
                               np.array([1., -1.]) * (np.log1p(.6) - np.log1p(.4)))
    changed = base.copy(); changed["label_valid"] = True; changed["label_net_R"] = [999., -999.]
    replayed, _ = add_book_features(changed, endpoint, flow)
    np.testing.assert_allclose(joined[FEATURES], replayed[FEATURES])
    assert len(joined) == len(replayed)
    unknown = endpoint.copy(); unknown["book_features_known"] = False
    dropped, _ = add_book_features(base, unknown, flow)
    assert dropped.empty
    zero = endpoint.copy(); zero["ask_depth10"] = 0.
    dropped, _ = add_book_features(base, zero, flow)
    assert dropped.empty
    zero_flow = flow.copy(); zero_flow["buy"] = 0.
    retained, _ = add_book_features(base, endpoint, zero_flow)
    assert len(retained) == 2 and retained.capacity_buy.eq(0).all()
    original = list(L.FEATURES); original_price = list(L.PRICE_FEATURES)
    learner = configured_learner()
    assert L.FEATURES == original and L.PRICE_FEATURES == original_price
    assert learner.FEATURES == FEATURES and learner.PRICE_FEATURES == NOBOOK_FEATURES
    assert "q0" in learner.PRICE_FEATURES and len(FEATURES) == 37
    assert learner._estimator("RIDGE").alpha == 100.
    assert learner._estimator("HGB").max_iter == 120
    assert not _boolean(pd.Series(["False", "True"]), "planted").iloc[0]
    return dict(passed=True, actual_cache_inputs_fits_or_outcomes_read=False,
                feature_count=len(FEATURES), no_book_feature_count=len(NOBOOK_FEATURES),
                checks=["exact_endpoint_capacities_and_side_interactions", "label_independent_inference_eligibility",
                        "unknown_book_and_zero_depth_excluded", "valid_derived_zero_retained",
                        "isolated_learner_configuration_and_fixed_hyperparameters", "strict_boolean_parsing"],
                selectable_order=list(SELECTABLE), control="HGB_NOBOOK")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["self-check", "design"], required=True)
    parser.add_argument("--prereg")
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    if args.phase == "self-check": print(json.dumps(self_check(), indent=2))
    elif not args.prereg: parser.error("--prereg required before actual cache/book/model/outcome reads")
    else: run(args.prereg, out=args.out, root=args.root)
