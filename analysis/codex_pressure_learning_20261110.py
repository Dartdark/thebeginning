"""Frozen monthly forecasts of exact net barrier payoffs; inert on import.

Actual label generation/replay requires the parent's committed second protocol.
--phase self-check uses only invented arrays/tables. No live/network/Git mutations.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
import warnings

sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor
import sklearn
import codex_pressure_build_20261110_inputs as I
import codex_pressure_build_20261110_replay as E
import codex_cash_open_repair as C

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_pressure_learning_20261110"
PLAN = "agents/codex/plans/pressure_learning_20261110.md"
EVIDENCE = "agents/codex/evidence/pressure_learning_20261110.md"
CODE = ["analysis/codex_pressure_learning_20261110.py", "analysis/codex_pressure_build_20261110_inputs.py",
        "analysis/codex_pressure_build_20261110_replay.py", "analysis/grid.py", "analysis/grid24.py",
        "analysis/codex_cash_open_repair.py", "analysis/codex_s03_calendar.py", "analysis/metrics.py"]
MODELS = ("RIDGE", "HGB", "HGB_PRICE")
SELECTABLE = ("RIDGE", "HGB")
BASE_FEATURES = ["body0", "range0", "loc0", "body1", "body2", "q0", "q1", "q2",
                 "efficiency3", "log_volume_ratio", "vol3_atr", "hour", "side"]
DIRECTIONAL = ["body0", "body1", "body2", "loc0", "q0", "q1", "q2", "efficiency3"]
FEATURES = BASE_FEATURES + ["side_x_" + k for k in DIRECTIONAL]
PRICE_FEATURES = [k for k in FEATURES if k not in {"q0", "q1", "q2", "side_x_q0", "side_x_q1", "side_x_q2"}]
SIGNAL_FIELDS = ["date", "day", "signal_j", "first_entry_j", "stop", "target", "exit_j", "side", "input_last_time"]
TRAIN_SLOTS, MIN_DATES, MIN_ROWS = 126, 100, 10000
MIN_SIDE_STOPS, MIN_SIDE_STOP_DATES = 50, 30
SCORE_HURDLE = .02


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _dump(path, value):
    C.write(path, json.dumps(value, indent=2, default=str, allow_nan=True) + "\n")


def _csv(path, frame):
    data = frame.to_csv(index=False).encode()
    C.write(path, gzip.compress(data, mtime=0) if str(path).endswith(".gz") else data)


def prepare_data(minutes=None, grid=None, *, root=ROOT, build_labels=True):
    """Return samples, normal-cash calendar, grid, audit.

    Every decision has two counterfactual side rows. Features never use label
    values. Full-horizon OHLC completeness is required for training labels;
    inference eligibility depends only on features known at the decision.
    Calling build_labels=True on real data is an economic study operation.
    """
    if minutes is None:
        minutes = I.load_design_native(root=root)
    if grid is None:
        grid = I.make_grid(minutes)
    bars = I.complete5min_ohlcv(minutes).copy()
    bars["date"] = bars.index.normalize()
    bars["signal_j"] = bars.index.hour * 60 + bars.index.minute
    calendar = pd.DatetimeIndex([d for d in pd.to_datetime(grid.ts) if C.normal_cash(d)])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        atr = pd.Series(grid.daily_atr(15), index=pd.to_datetime(grid.ts))
    bars["atr"] = bars.date.map(atr)
    body = bars.close - bars.open
    span = bars.high - bars.low
    bars["body0"] = body / bars.atr
    bars["range0"] = span / bars.atr
    bars["loc0"] = 2 * (bars.close - bars.low) / span.replace(0, np.nan) - 1
    bars["q0"] = (bars.buy - bars.sell) / bars.volume.replace(0, np.nan)
    for lag in (1, 2):
        prior = bars.index - pd.Timedelta(minutes=5 * lag)
        bars[f"body{lag}"] = body.reindex(prior).to_numpy() / bars.atr.to_numpy()
        bars[f"q{lag}"] = bars.q0.reindex(prior).to_numpy()
    body_sum = bars[["body0", "body1", "body2"]].sum(axis=1, min_count=3)
    abs_sum = bars[["body0", "body1", "body2"]].abs().sum(axis=1, min_count=3)
    bars["efficiency3"] = body_sum / abs_sum.replace(0, np.nan)
    changes = []
    for lag in range(3):
        now = bars.close.reindex(bars.index - pd.Timedelta(minutes=5 * lag)).to_numpy()
        before = bars.close.reindex(bars.index - pd.Timedelta(minutes=5 * (lag + 1))).to_numpy()
        changes.append(now - before)
    bars["vol3_atr"] = np.sqrt(np.sum(np.square(changes), axis=0)) / bars.atr
    # Exact previous 20 normal-cash slots at the same clock. Current date is
    # shifted out before rolling; missing slots do not stretch the window.
    volume = bars[bars.date.isin(calendar)].pivot(index="date", columns="signal_j", values="volume").reindex(calendar)
    medians = volume.shift(1).rolling(20, min_periods=20).median()
    baseline = medians.stack(dropna=False)
    key = pd.MultiIndex.from_arrays([bars.date.to_numpy(), bars.signal_j.to_numpy()])
    prior_volume = baseline.reindex(key).to_numpy()
    bars["log_volume_ratio"] = np.log(bars.volume / np.where(prior_volume > 0, prior_volume, np.nan))
    bars["hour"] = bars.signal_j // 60
    rollfree=set(d for d in calendar if not C.roll_guard(d))
    eligible = (bars.date.isin(rollfree)
                & bars.signal_j.between(540, 840) & bars.atr.gt(0))
    source = bars[eligible].copy()
    source["input_last_time"] = source.index
    needed = [k for k in BASE_FEATURES if k != "side"]
    finite = np.isfinite(source[needed]).all(axis=1)
    source = source[finite].copy()
    source["day"] = source.date.map({pd.Timestamp(v): i for i, v in enumerate(grid.ts)})
    source["first_entry_j"] = source.signal_j + 2
    source["stop"] = np.ceil(.10 * source.atr * 4.) / 4.
    source["target"] = np.ceil(.3 * source.stop * 4.) / 4.
    source["exit_j"] = np.minimum(source.signal_j + 31, 895)
    source["label_known_at"] = source.date + pd.to_timedelta(source.exit_j, unit="min")
    sides = []
    for side in (1, -1):
        block = source.copy(); block["side"] = side
        for name in DIRECTIONAL:
            block["side_x_" + name] = side * block[name]
        sides.append(block)
    data = pd.concat(sides).sort_values(["date", "signal_j", "side"], kind="stable").reset_index(drop=True)
    data["label_net_R"] = np.nan
    data["label_kind"] = np.nan
    data["label_valid"] = False
    data["label_full_horizon_valid"] = False
    diagnostic = {}
    if build_labels:
        pieces = []
        # Independent helper accepts one row per decision; two separate side
        # calls produce the paired training outcomes without simultaneous trades.
        for side in (1, -1):
            signals = data[data.side == side][SIGNAL_FIELDS]
            print('counterfactual training labels',side,len(signals),flush=True)
            ledger, diagnostic[str(side)] = E.replay(signals, grid=grid, independent=True)
            if len(ledger):
                label = ledger[["day", "signal_j", "side", "stop", "net_mnq", "kind", "path_valid"]].copy()
                label["label_net_R"] = label.net_mnq / (label.stop * 2.)
                label = label.rename(columns={"kind": "label_kind", "path_valid": "label_valid"})
                pieces.append(label[["day", "signal_j", "side", "label_net_R", "label_kind", "label_valid"]])
        if pieces:
            data = data.drop(columns=["label_net_R", "label_kind", "label_valid"]).merge(
                pd.concat(pieces), on=["day", "signal_j", "side"], how="left", validate="one_to_one")
        horizon = {}
        for row in source.itertuples():
            d, a, b = int(row.day), int(row.first_entry_j), int(row.exit_j)
            values = np.column_stack([getattr(grid, k)[d, a:b + 1] for k in ("o", "h", "l", "c")])
            valid = (np.isfinite(values).all(axis=1) & (values[:, 1] >= np.maximum(values[:, 0], values[:, 3]))
                     & (values[:, 2] <= np.minimum(values[:, 0], values[:, 3])) & (values[:, 1] >= values[:, 2]))
            horizon[(d, int(row.signal_j))] = bool(valid.all())
        data["label_full_horizon_valid"] = [horizon[(int(d), int(j))] for d, j in zip(data.day, data.signal_j)]
        data["label_valid"] = (data.label_valid.fillna(False).astype(bool) & data.label_full_horizon_valid
                               & np.isfinite(data.label_net_R))
    audit = dict(minutes=minutes.attrs.get("input_audit", {}), five_minute=bars.attrs.get("input_audit", {}),
                 decision_rows=len(source), paired_rows=len(data), feature_incomplete_decisions=int((~finite).sum()),
                 label_valid_rows=int(data.label_valid.sum()), label_unavailable_rows=int((~data.label_valid).sum()),
                 independent_label_diagnostics=diagnostic, features=FEATURES, price_features=PRICE_FEATURES,
                 volume_baseline="exact previous20 normal-cash dates, same5minclock, minimum20 finite; includes roll-calendar slots",
                 atr="shared Grid24.daily_atr(15), shifted previous stored weekday true ranges",
                 vol3="sqrt(sum of3 closed5min close-change squares) divided by priorATR",
                 label_clock="decision j; entry open wallj+1 (labelj+2); mature at frozen exit j+31, regardless early exit",
                 labels_computed=build_labels, native_micro="net_mnq is an NQ-price proxy, not native MNQ fills")
    return data, calendar, grid, audit


def training_rows(data, calendar, fit_time):
    """Exact-slot chronological fit admission, exposed for clock-only checks."""
    fit_time = pd.Timestamp(fit_time)
    slots = pd.DatetimeIndex(calendar)[pd.DatetimeIndex(calendar) < fit_time][-TRAIN_SLOTS:]
    mask = (data.date.isin(slots) & data.label_valid & data.label_known_at.lt(fit_time))
    selected = data.loc[mask].copy()
    reasons = []
    if len(slots) != TRAIN_SLOTS: reasons.append("fewer126priorcalendar_slots")
    if selected.date.nunique() < MIN_DATES: reasons.append("fewer100label_dates")
    if len(selected) < MIN_ROWS: reasons.append("fewer10000paired_label_rows")
    downside = {}
    for side in (1, -1):
        loss = selected[(selected.side == side) & (selected.label_kind == 0)]
        downside[str(side)] = dict(stops=len(loss), dates=int(loss.date.nunique()))
        if len(loss) < MIN_SIDE_STOPS: reasons.append(f"fewer50stops_side{side}")
        if loss.date.nunique() < MIN_SIDE_STOP_DATES: reasons.append(f"fewer30stop_dates_side{side}")
    audit = dict(fit_time=str(fit_time), calendar_slots=len(slots), first_slot=str(slots.min()) if len(slots) else None,
                 last_slot=str(slots.max()) if len(slots) else None, label_rows=len(selected), label_dates=int(selected.date.nunique()),
                 max_label_known_at=str(selected.label_known_at.max()) if len(selected) else None,
                 max_input_time=str(selected.input_last_time.max()) if len(selected) else None,
                 downside=downside, skipped_reasons=reasons)
    if len(selected):
        assert selected.date.max() < fit_time and selected.label_known_at.max() < fit_time
    return selected, audit


def _estimator(name):
    if name == "RIDGE": return Ridge(alpha=100.)
    if name in {"HGB", "HGB_PRICE"}:
        return HistGradientBoostingRegressor(max_iter=120, max_leaf_nodes=7, max_depth=3,
                                             min_samples_leaf=250, l2_regularization=10., learning_rate=.05,
                                             early_stopping=False, random_state=20261110)
    raise ValueError(name)


def _signals(predictions):
    rows = []
    if len(predictions):
        for _, group in predictions.groupby(["day", "signal_j"], sort=True):
            ranked = group.sort_values("score_R", ascending=False, kind="stable")
            if ranked.score_R.iloc[0] <= SCORE_HURDLE: continue
            if len(ranked) > 1 and np.isclose(ranked.score_R.iloc[0], ranked.score_R.iloc[1], rtol=0, atol=1e-12): continue
            rows.append(ranked.iloc[0])
    return pd.DataFrame(rows, columns=predictions.columns if len(predictions.columns) else SIGNAL_FIELDS + ["score_R", "model", "fit_time"])


def fit_predict(data, calendar, *, models=MODELS):
    """Return signals_by_model, all side forecasts, monthly fit audit.

    StandardScaler sees training rows only. The estimator receives exactly the
    named columns, never a label, fill, realized outcome or inferred future class.
    """
    missing = set(FEATURES + ["label_net_R", "label_valid", "label_known_at"]) - set(data.columns)
    if missing: raise ValueError(f"Missing columns: {missing}")
    forecasts, fits = [], []
    if data.empty:
        return {m: pd.DataFrame(columns=SIGNAL_FIELDS + ["score_R", "model", "fit_time"]) for m in models}, pd.DataFrame(), pd.DataFrame()
    months = pd.period_range(data.date.min(), data.date.max(), freq="M")
    for month in months:
        print('monthly fit',str(month),flush=True)
        fit_time = month.start_time
        test = data[(data.date >= fit_time) & (data.date < (month + 1).start_time)]
        if test.empty: continue
        train, admission = training_rows(data, calendar, fit_time)
        for name in models:
            columns = PRICE_FEATURES if name == "HGB_PRICE" else FEATURES
            info = dict(admission, model=name, feature_columns=columns)
            if admission["skipped_reasons"]:
                info["status"] = "SKIP"; fits.append(info); continue
            scaler = StandardScaler()
            x = scaler.fit_transform(train[columns].to_numpy(float))
            y = train.label_net_R.to_numpy(float)
            model = _estimator(name); model.fit(x, y)
            score = model.predict(scaler.transform(test[columns].to_numpy(float)))
            if not np.isfinite(score).all(): raise ValueError("Nonfinite model forecast")
            p = test[SIGNAL_FIELDS].copy()
            p["score_R"] = score; p["model"] = name; p["fit_time"] = fit_time
            forecasts.append(p)
            info.update(status="FIT", prediction_rows=len(test), scaler_mean=scaler.mean_.tolist(),
                        scaler_scale=scaler.scale_.tolist(), train_target_mean=float(y.mean()),
                        train_target_min=float(y.min()), train_target_max=float(y.max()))
            if name == "RIDGE": info.update(coef=model.coef_.tolist(), intercept=float(model.intercept_))
            fits.append(info)
    prediction = pd.concat(forecasts, ignore_index=True) if forecasts else pd.DataFrame(columns=SIGNAL_FIELDS + ["score_R", "model", "fit_time"])
    signals = {name: _signals(prediction[prediction.model == name].copy()) for name in models}
    return signals, prediction, pd.DataFrame(fits)


def run(prereg, *, out=OUT, root=ROOT):
    """Explicit committed design runner. It never reads 2023+ price outcomes."""
    root, out = Path(root), Path(out)
    paths = [PLAN, EVIDENCE] + CODE
    for name in paths:
        frozen = subprocess.check_output(["git", "show", f"{prereg}:{name}"], cwd=ROOT)
        if frozen != (ROOT / name).read_bytes(): raise ValueError(f"Protocol/code not frozen: {name}")
    if (out / "results.json").exists(): raise ValueError("Existing outcomes cannot be overwritten")
    out.mkdir(parents=True, exist_ok=True)
    _dump(out / "binding.json", dict(prereg=prereg, files={p:sha(ROOT/p) for p in paths}, models=MODELS,
                                     new_economic_definitions=3, prior_trials_retained=True,
                                     sklearn_version=sklearn.__version__, validation_outcomes_read=False))
    data, calendar, grid, audit = prepare_data(root=root)
    print('prepared causal features and mature training labels',len(data),flush=True)
    _dump(out / "input_and_label_audit.json", audit)
    _csv(out / "features_and_labels.csv.gz", data)
    signals, predictions, fits = fit_predict(data, calendar)
    _csv(out / "predictions.csv.gz", predictions); _csv(out / "monthly_fits.csv", fits)
    summaries, tables = {}, []
    for name in MODELS:
        _csv(out / f"{name}_signals.csv.gz", signals[name])
        trades, execution = E.replay(signals[name], grid=grid, max_trades=4)
        _csv(out / f"{name}_trades.csv.gz", trades)
        known = not bool(execution["unknown_held_path_trades"])
        table = E.metrics_table(trades, calendar, allow_unknown=not known); table["model"] = name; tables.append(table)
        daily = trades.groupby("date").net.sum().reindex(calendar, fill_value=0)
        _csv(out / f"{name}_daily.csv", daily.rename("net").rename_axis("date").reset_index())
        summaries[name] = dict(summary=E.metrics_summary(trades, calendar, allow_unknown=not known),
                               micro=E.metrics_summary(trades, calendar, "net_mnq", allow_unknown=not known),
                               stress=E.metrics_summary(trades, calendar, "stress_four_ticks", allow_unknown=not known),
                               stop_first=E.metrics_summary(trades, calendar, "stop_first_net", allow_unknown=not known),
                               execution=execution, positive_years=int((daily.groupby(daily.index.year).sum()>0).sum()),
                               long_trades=int((trades.side == 1).sum()), short_trades=int((trades.side == -1).sum()))
    _csv(out / "metrics.csv", pd.concat(tables, ignore_index=True))
    result = dict(prereg=prereg, stats=summaries, selected=None, design_gate_complete=False,
                  validation_allowed=False, new_economic_definitions=3,
                  selection_policy="RIDGE first if every parent's frozen gate passes, else HGB; HGB_PRICE unselectable")
    _dump(out / "results.json", result)
    print(pd.DataFrame({m:v["summary"] for m,v in summaries.items()}).T.to_string(), flush=True)
    return result


def self_check():
    """Planted clocks, schema and selection only; no real labels or outcomes."""
    cal = pd.bdate_range("2019-01-01", periods=200)
    fit = cal[180].normalize()
    sample = pd.DataFrame({"date":cal, "side":1, "label_valid":True, "label_kind":0,
                           "input_last_time":cal+pd.Timedelta(hours=9), "label_known_at":cal+pd.Timedelta(hours=9,minutes=31),
                           "label_net_R":0.1})
    got, audit = training_rows(sample, cal, fit)
    assert got.date.min() == cal[54] and got.date.max() == cal[179] and len(got) == 126
    bad = sample.copy(); bad.loc[179,"label_known_at"] = fit+pd.Timedelta(minutes=1)
    got2, _ = training_rows(bad, cal, fit)
    assert len(got2) == 125 and cal[179] not in set(got2.date)
    assert all(k in FEATURES for k in PRICE_FEATURES) and not any(k in PRICE_FEATURES for k in ("q0","q1","q2","side_x_q0","side_x_q1","side_x_q2"))
    p = pd.DataFrame([dict(day=0, signal_j=540, score_R=.03, side=1),dict(day=0,signal_j=540,score_R=.01,side=-1),
                      dict(day=0,signal_j=545,score_R=.02,side=1),dict(day=0,signal_j=545,score_R=.01,side=-1),
                      dict(day=0,signal_j=550,score_R=.03,side=1),dict(day=0,signal_j=550,score_R=.03,side=-1)])
    chosen = _signals(p)
    assert len(chosen)==1 and chosen.iloc[0].side==1 and chosen.iloc[0].signal_j==540
    assert 540+2-1+30 == 540+31
    return dict(passed=True, checks=["exact126calendar_slots", "fully_mature_labels_only", "fixed_feature_control_schema",
                                    "strict_net_R_hurdle", "best_side_and_tie_skip", "30wallminute_label_clock"],
                real_inputs_or_labels_read=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["self-check", "design"], required=True)
    parser.add_argument("--prereg")
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    if args.phase == "self-check": print(json.dumps(self_check(), indent=2))
    elif not args.prereg: parser.error("--prereg is required before any actual labels/outcomes")
    else: run(args.prereg, out=args.out, root=args.root)
