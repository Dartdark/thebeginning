"""Frozen120-minute pre-event activity extension; no real outcomes on import.

Self-checks use planted arrays. Actual inputs/cache/fits/replays require a frozen
protocol. The finite profile is an adaptation, not a fitted Hawkes classifier.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import argparse
import gzip
import hashlib
import io
import json
import subprocess
import sys
import warnings

sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
import sklearn

import codex_pressure_learning_20261110 as L
import codex_pressure_build_20261110_inputs as I
import codex_pressure_build_20261110_replay as E
import codex_cash_open_repair as C

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_pressure_memory_20261110"
PLAN = "agents/codex/plans/pressure_memory_20261110.md"
EVIDENCE = "agents/codex/evidence/pressure_memory_20261110.md"
CACHE_COMMIT = "0d61f59e30304a5a9850ef1a20b33a2d1f04cc2d"
CACHE_PATH = "analysis/outputs/codex_pressure_learning_20261110/features_and_labels.csv.gz"
NATIVE_MANIFEST = "agents/codex/inputs/bridge_native_2018_22_20261108/transfer_manifest.json"
CODE = ["analysis/codex_pressure_memory_20261110.py", "analysis/codex_pressure_learning_20261110.py",
        "analysis/codex_pressure_build_20261110_inputs.py", "analysis/codex_pressure_build_20261110_replay.py",
        "analysis/grid.py", "analysis/grid24.py", "analysis/metrics.py",
        "analysis/codex_cash_open_repair.py", "analysis/codex_s03_calendar.py"]
KAPPA, PROFILE, FAST = .12, 120, 15
MODELS = ("HGB_MEMORY", "RIDGE_MEMORY", "HGB_LOCAL", "RIDGE_LOCAL")
SELECTABLE = ("HGB_MEMORY", "RIDGE_MEMORY")
CONTROL_FOR = {"HGB_MEMORY": "HGB_LOCAL", "RIDGE_MEMORY": "RIDGE_LOCAL"}
LOCAL_FEATURES = list(L.FEATURES)
MEMORY_FEATURES = ["activity120", "activity_accel15_105", "ema_abs_u", "ema_u", "ema_sign_u",
                   "pressure120", "pressure_accel", "alignment120", "peak_fraction120"]
DIRECTIONAL = ("ema_u", "ema_sign_u", "pressure120", "pressure_accel")
FEATURES = LOCAL_FEATURES + MEMORY_FEATURES + ["side_x_" + k for k in DIRECTIONAL]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _dump(path, value):
    C.write(path, json.dumps(value, indent=2, default=str, allow_nan=True) + "\n")


def _csv(path, frame):
    payload = frame.to_csv(index=False).encode()
    C.write(path, gzip.compress(payload, mtime=0) if str(path).endswith(".gz") else payload)


def load_cached_samples(root=ROOT):
    """Reuse exact Git-bound batch2 features/labels, never regenerate payoffs."""
    payload = (Path(root) / CACHE_PATH).read_bytes()
    expected = subprocess.check_output(["git", "show", f"{CACHE_COMMIT}:{CACHE_PATH}"], cwd=ROOT)
    if payload != expected:
        raise ValueError("Cache differs from frozen batch2 Git bytes")
    data = pd.read_csv(io.BytesIO(payload), compression="gzip")
    required = set(LOCAL_FEATURES + L.SIGNAL_FIELDS + ["label_net_R", "label_valid", "label_kind", "label_known_at"])
    if not required.issubset(data): raise ValueError(f"Missing cached columns: {required - set(data)}")
    for name in ("date", "input_last_time", "label_known_at"):
        data[name] = pd.to_datetime(data[name], errors="raise")
        if data[name].isna().any(): raise ValueError(f"Missing cached timestamp: {name}")
    data["date"] = data.date.dt.normalize()
    if len(data) and (data.date.min() < pd.Timestamp("2018-01-01") or data.date.max() >= pd.Timestamp("2023-01-01")):
        raise ValueError("Cached dates outside design")
    for name in ("label_valid", "label_full_horizon_valid"):
        if name not in data: continue
        if not pd.api.types.is_bool_dtype(data[name]):
            mapped = data[name].map({"True": True, "False": False, True: True, False: False})
            if mapped.isna().any(): raise ValueError(f"Unknown boolean in {name}")
            data[name] = mapped.astype(bool)
    if data.duplicated(["day", "signal_j", "side"]).any() or not data.side.isin((-1, 1)).all():
        raise ValueError("Invalid cached decision/side keys")
    key = data.date + pd.to_timedelta(data.signal_j, unit="min")
    if not data.input_last_time.eq(key).all(): raise ValueError("Cached feature clock mismatch")
    if not np.isfinite(data[LOCAL_FEATURES]).all(axis=None): raise ValueError("Invalid cached base feature")
    return data, dict(source_commit=CACHE_COMMIT, source_path=CACHE_PATH,
                      compressed_sha256=hashlib.sha256(payload).hexdigest(), rows=len(data),
                      labels_regenerated=False, label_values_changed=False)


def minute_seasons(raw_returns, grid_dates, calendar):
    """Before-day minute factors over exact20 normal-cash slots, min15 finite.

    Valid zero observations remain in medians. An admitted median must be
    strictly positive. Its cross-clock center includes all admitted00:00--23:59
    medians. Roll-date history is retained, as in the original ML volume baseline.
    """
    frame = pd.DataFrame(np.abs(raw_returns), index=pd.DatetimeIndex(grid_dates), columns=np.arange(1440))
    wide = frame.reindex(pd.DatetimeIndex(calendar))
    medians = wide.shift(1).rolling(20, min_periods=15).median()
    medians.iloc[:20] = np.nan  # Do not turn min15 into a shorter calendar window.
    medians = medians.where(np.isfinite(medians) & medians.gt(0))
    center = medians.median(axis=1)
    factors = medians.div(center.where(center > 0), axis=0)
    return factors


def summarize_profile(u, buy, sell, volume=None):
    """Fixed120 exact one-minute observations, oldest first; no thresholds fit."""
    u, buy, sell = (np.asarray(x, dtype=float) for x in (u, buy, sell))
    if u.shape != (PROFILE,) or buy.shape != u.shape or sell.shape != u.shape:
        raise ValueError("Exactly120 minute values required")
    volume = buy + sell if volume is None else np.asarray(volume, dtype=float)
    if volume.shape != u.shape or not all(np.isfinite(x).all() for x in (u, buy, sell, volume)):
        return None, "PROFILE_NONFINITE"
    if (buy < 0).any() or (sell < 0).any() or (volume < 0).any() or not np.array_equal(volume, buy + sell):
        return None, "FLOW_UNKNOWN"
    absolute = np.abs(u)
    early_activity, late_activity = absolute[:-FAST].mean(), absolute[-FAST:].mean()
    early_volume, late_volume = volume[:-FAST].sum(), volume[-FAST:].sum()
    total_activity, total_volume = absolute.sum(), volume.sum()
    if min(early_activity, late_activity, total_activity) <= 0:
        return None, "ZERO_ACTIVITY_DENOMINATOR"
    if min(early_volume, late_volume, total_volume) <= 0:
        return None, "ZERO_VOLUME_DENOMINATOR"
    # Exact source-style kappa per minute; finite initialization at zero.
    weights = KAPPA * (1 - KAPPA) ** np.arange(PROFILE - 1, -1, -1)
    delta = buy - sell
    result = dict(activity120=float(absolute.mean()),
                  activity_accel15_105=float(np.log(late_activity / early_activity)),
                  ema_abs_u=float(weights @ absolute), ema_u=float(weights @ u),
                  ema_sign_u=float(weights @ np.sign(u)),
                  pressure120=float(delta.sum() / total_volume),
                  pressure_accel=float(delta[-FAST:].sum() / late_volume - delta[:-FAST].sum() / early_volume),
                  alignment120=float((u * np.sign(delta)).sum() / total_activity),
                  peak_fraction120=float(absolute.max() / total_activity))
    if not np.isfinite(list(result.values())).all(): return None, "PROFILE_NONFINITE"
    return result, "KNOWN"


def make_memory_features(native_minutes, calendar, endpoint_times, *, grid=None):
    """Profile returns T−124..T−5 from closes T−125..T−5, no current bar.

    Current five-minute features from the immutable cache remain available.
    A known profile needs all121 closes and120 return/flow/seasonal observations.
    Nothing is filled, shortened, centered or conditioned on a subsequent jump.
    """
    if grid is None: grid = I.make_grid(native_minutes)
    dates = pd.DatetimeIndex(grid.ts)
    calendar = pd.DatetimeIndex(calendar).normalize()
    times = pd.DatetimeIndex(endpoint_times).unique().sort_values()
    if times.tz is not None or calendar.tz is not None: raise ValueError("Naive CT clocks required")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        atr = grid.daily_atr(15)
    lag = np.roll(grid.c, 1, axis=1)
    lag[:, 0] = np.r_[np.nan, grid.c[:-1, -1]]
    with np.errstate(divide="ignore", invalid="ignore"):
        raw = (grid.c - lag) / atr[:, None]
    factors = minute_seasons(raw, dates, calendar)
    days = {pd.Timestamp(date): k for k, date in enumerate(dates)}
    rows = []
    for date, group in pd.Series(times, index=times).groupby(times.normalize()):
        d = days.get(pd.Timestamp(date))
        factor_row = factors.loc[date].to_numpy(float) if date in factors.index else np.full(1440, np.nan)
        if d is not None:
            with np.errstate(divide="ignore", invalid="ignore"):
                u_day = raw[d] / factor_row
        for stamp in group:
            j = int(stamp.hour * 60 + stamp.minute)
            record = {name: np.nan for name in MEMORY_FEATURES}
            status = "PROFILE_CLOCK_UNKNOWN"
            if d is not None and stamp.second == 0 and stamp.microsecond == 0 and j % 5 == 0 and 125 <= j <= 1439:
                anchors = np.arange(j - 125, j - 4)
                window = np.arange(j - 124, j - 4)
                if not np.isfinite(grid.c[d, anchors]).all():
                    status = "PROFILE_PRICE_UNKNOWN"
                elif not np.isfinite(u_day[window]).all():
                    status = "SEASONAL_OR_RETURN_UNKNOWN"
                else:
                    values, status = summarize_profile(u_day[window], grid.buy[d, window], grid.sell[d, window], grid.v[d, window])
                    if values is not None: record.update(values)
            record.update(time=stamp, profile_known=status == "KNOWN", profile_status=status,
                          profile_start=stamp - pd.Timedelta(minutes=125),
                          profile_last_input_time=stamp - pd.Timedelta(minutes=5))
            rows.append(record)
    columns = MEMORY_FEATURES + ["time", "profile_known", "profile_status", "profile_start", "profile_last_input_time"]
    frame = pd.DataFrame(rows, columns=columns).set_index("time")
    audit = dict(requested_endpoints=len(times), known_endpoints=int(frame.profile_known.sum()),
                 status_counts=frame.profile_status.value_counts().to_dict(), features=MEMORY_FEATURES,
                 interval="120returns at T-124..T-5,121closes T-125..T-5; excludes current five-minute bar",
                 normalizer="(minute close difference)/prior-day sharedATR15 / own minute factor; exact previous20normal-cash slots, min15finite, positive median; valid zeros retained",
                 clock_center="Cross-median of all admittedpositive finite00:00--23:59 clock medians; roll-date history retained",
                 source_adaptation="kappa=.12 perminute from2021pp5-6; u is not paper J; no4.36 classification or jump exclusion;120min finite profile is not a fitted long-memory/Hawkes kernel",
                 early_hours="09:00 decisions include observed CME preopen history, unlike the source's stock cash-session setting",
                 no_future_jump_class=True, no_fill=True)
    return frame, audit


def add_memory_features(samples, profiles):
    data = samples.copy().reset_index(drop=True)
    if set(FEATURES[len(LOCAL_FEATURES):]) & set(data): raise ValueError("Memory features already attached")
    if profiles.index.has_duplicates: raise ValueError("Duplicate profile endpoint")
    key = pd.DatetimeIndex(data.date + pd.to_timedelta(data.signal_j, unit="min"))
    context = profiles.reindex(key).reset_index(drop=True)
    for name in MEMORY_FEATURES: data[name] = context[name].to_numpy()
    for name in DIRECTIONAL: data["side_x_" + name] = data.side * data[name]
    declared_known = context.profile_known.eq(True)
    known = declared_known & np.isfinite(data[FEATURES]).all(axis=1)
    last_time = pd.to_datetime(context.profile_last_input_time)
    if (declared_known & ~last_time.eq(pd.Series(key) - pd.Timedelta(minutes=5))).any():
        raise ValueError("Known profile must have an exact nonmissing T-5 endpoint")
    data["profile_known"] = known
    data["profile_status"] = context.profile_status.fillna("ENDPOINT_UNKNOWN").to_numpy()
    data["profile_last_input_time"] = last_time
    receipt = dict(base_paired_rows=len(data), retained_paired_rows=int(known.sum()),
                   retained_decisions=int(data.loc[known, ["day", "signal_j"]].drop_duplicates().shape[0]),
                   unknown_paired_rows=int((~known).sum()), status_counts=data.profile_status.value_counts().to_dict(),
                   inference_filter="Only observed historical profile/normalizer availability; never label_valid or future payoff",
                   features=FEATURES, local_control_features=LOCAL_FEATURES)
    return data.loc[known].copy().reset_index(drop=True), receipt


def estimator(name):
    if name not in MODELS: raise ValueError(name)
    return L._estimator("RIDGE" if name.startswith("RIDGE") else "HGB")


def fit_predict(data, calendar):
    """Four models, exact inherited monthly admission/scaling/hurdle semantics.

    Each candidate has a same-estimator local control. This wrapper changes no
    original module globals or files and performs no duplicate alias fits.
    """
    missing = set(FEATURES + ["label_net_R", "label_valid", "label_known_at"]) - set(data)
    if missing: raise ValueError(f"Missing columns: {missing}")
    columns_out = L.SIGNAL_FIELDS + ["score_R", "model", "fit_time"]
    if data.empty:
        return ({name: pd.DataFrame(columns=columns_out) for name in MODELS},
                pd.DataFrame(columns=columns_out), pd.DataFrame())
    forecasts, fits = [], []
    months = pd.period_range(data.date.min(), data.date.max(), freq="M")
    for month in months:
        print("memory monthly fit", str(month), flush=True)
        fit_time = month.start_time
        test = data[(data.date >= fit_time) & (data.date < (month + 1).start_time)]
        if test.empty: continue
        train, admission = L.training_rows(data, calendar, fit_time)
        for name in MODELS:
            columns = LOCAL_FEATURES if name.endswith("_LOCAL") else FEATURES
            info = dict(admission, model=name, feature_columns=columns)
            if admission["skipped_reasons"]:
                info["status"] = "SKIP"; fits.append(info); continue
            scaler = L.StandardScaler()
            x = scaler.fit_transform(train[columns].to_numpy(float))
            y = train.label_net_R.to_numpy(float)
            model = estimator(name); model.fit(x, y)
            score = model.predict(scaler.transform(test[columns].to_numpy(float)))
            if not np.isfinite(score).all(): raise ValueError("Nonfinite memory forecast")
            p = test[L.SIGNAL_FIELDS].copy()
            p["score_R"] = score; p["model"] = name; p["fit_time"] = fit_time
            forecasts.append(p)
            info.update(status="FIT", prediction_rows=len(test), scaler_mean=scaler.mean_.tolist(),
                        scaler_scale=scaler.scale_.tolist(), train_target_mean=float(y.mean()),
                        train_target_min=float(y.min()), train_target_max=float(y.max()))
            if name.startswith("RIDGE"):
                info.update(coef=model.coef_.tolist(), intercept=float(model.intercept_))
            fits.append(info)
    prediction = pd.concat(forecasts, ignore_index=True) if forecasts else pd.DataFrame(columns=columns_out)
    signals = {name: L._signals(prediction[prediction.model == name].copy()) for name in MODELS}
    return signals, prediction, pd.DataFrame(fits)


def run(prereg, *, out=OUT, root=ROOT):
    out, root = Path(out), Path(root)
    if root.resolve() != ROOT.resolve(): raise ValueError("Actual run requires canonical Git-bound input root")
    paths = [PLAN, EVIDENCE] + CODE + [NATIVE_MANIFEST]
    for path in paths:
        if subprocess.check_output(["git", "show", f"{prereg}:{path}"], cwd=ROOT) != (ROOT / path).read_bytes():
            raise ValueError(f"Protocol/code not frozen: {path}")
    if (out / "results.json").exists(): raise ValueError("Existing results cannot be overwritten")
    out.mkdir(parents=True, exist_ok=True)
    _dump(out / "binding.json", dict(prereg=prereg, files={p: sha(ROOT / p) for p in paths},
                                     cache_commit=CACHE_COMMIT, cache_path=CACHE_PATH,
                                     models=list(MODELS), selectable_order=list(SELECTABLE),
                                     prior_study_definitions=15, new_economic_definitions=4,
                                     cumulative_new_study_definitions=19, older_book_searches=39,
                                     validation_outcomes_read=False, labels_regenerated=False,
                                     sklearn_version=sklearn.__version__))
    cached, cache_audit = load_cached_samples(root)
    native = I.load_design_native(root=root); grid = I.make_grid(native)
    calendar = pd.DatetimeIndex([d for d in pd.to_datetime(grid.ts) if C.normal_cash(d)])
    daymap = {pd.Timestamp(d): k for k, d in enumerate(grid.ts)}
    if not cached.date.map(daymap).eq(cached.day).all(): raise ValueError("Cached grid-day map changed")
    endpoints = cached.date + pd.to_timedelta(cached.signal_j, unit="min")
    profiles, profile_audit = make_memory_features(native, calendar, endpoints, grid=grid)
    _csv(out / "profile_features.csv.gz", profiles.rename_axis("time").reset_index())
    data, attachment = add_memory_features(cached, profiles)
    _dump(out / "input_and_profile_audit.json", dict(cache=cache_audit, native=native.attrs.get("input_audit", {}),
                                                    profile=profile_audit, attachment=attachment))
    _csv(out / "eligible_features_and_fixed_labels.csv.gz", data)
    signals, predictions, fits = fit_predict(data, calendar)
    _csv(out / "predictions.csv.gz", predictions); _csv(out / "monthly_fits.csv", fits)
    summaries, tables, gates = {}, [], {}
    for name in MODELS:
        _csv(out / f"{name}_signals.csv.gz", signals[name])
        trades, execution = E.replay(signals[name], grid=grid, max_trades=4)
        _csv(out / f"{name}_trades.csv.gz", trades)
        known = not bool(execution["unknown_held_path_trades"])
        table = E.metrics_table(trades, calendar, allow_unknown=not known); table["model"] = name; tables.append(table)
        daily = trades.groupby("date").net.sum().reindex(calendar, fill_value=0)
        _csv(out / f"{name}_daily.csv", daily.rename("net").rename_axis("date").reset_index())
        summary = dict(summary=E.metrics_summary(trades, calendar, allow_unknown=not known),
                       micro=E.metrics_summary(trades, calendar, "net_mnq", allow_unknown=not known),
                       stress=E.metrics_summary(trades, calendar, "stress_four_ticks", allow_unknown=not known),
                       stop_first=E.metrics_summary(trades, calendar, "stop_first_net", allow_unknown=not known),
                       execution=execution, positive_years=int((daily.groupby(daily.index.year).sum() > 0).sum()),
                       long_trades=int((trades.side == 1).sum()), short_trades=int((trades.side == -1).sum()))
        summaries[name] = summary
        if name in SELECTABLE:
            s = summary["summary"]
            gates[name] = dict(trades=s["trades"] >= 250, dates=trades.date.nunique() >= 100,
                               long_count=summary["long_trades"] >= 25, short_count=summary["short_trades"] >= 25,
                               net=s["total"] > 0, micro_net=summary["micro"]["total"] > 0,
                               trade_t=s["t_trade"] >= 2, daily_nw5=s["t_nw5"] >= 1.5,
                               profit_factor=s["profit_factor"] >= 1.2, years=summary["positive_years"] >= 4,
                               stress_net=summary["stress"]["total"] > 0, stop_first_net=summary["stop_first"]["total"] > 0,
                               held_paths=execution["unknown_held_path_trades"] == 0)
    _csv(out / "metrics.csv", pd.concat(tables, ignore_index=True))
    result = dict(prereg=prereg, stats=summaries, basic_gates=gates,
                  basic_pass_candidates=[name for name in SELECTABLE if all(gates[name].values())],
                  selected=None, design_gate_complete=False, validation_allowed=False,
                  new_economic_definitions=4, prior_study_definitions=15, cumulative_new_study_definitions=19,
                  control_for=CONTROL_FOR,
                  selection_policy="HGB_MEMORY then RIDGE_MEMORY after all frozen gates; HGB_LOCAL/RIDGE_LOCAL unselectable",
                  limitations="Conditional finite historical activity profile, not a fitted power-law/Hawkes process, causal jump forecast proof, full book or guaranteed net trade edge")
    _dump(out / "results.json", result)
    print(pd.DataFrame({name: value["summary"] for name, value in summaries.items()}).T.to_string(), flush=True)
    return result


def self_check():
    """Planted arrays only; no real cache/inputs/fits/replay outcomes."""
    u = np.linspace(-1, 2, PROFILE); buy = np.full(PROFILE, 6.); sell = np.full(PROFILE, 4.)
    feature, status = summarize_profile(u, buy, sell)
    assert status == "KNOWN"
    states = np.zeros(3)
    for value in u: states = KAPPA * np.array([abs(value), value, np.sign(value)]) + (1 - KAPPA) * states
    np.testing.assert_allclose([feature[k] for k in ("ema_abs_u", "ema_u", "ema_sign_u")], states)
    np.testing.assert_allclose(feature["pressure120"], .2)
    assert summarize_profile(np.zeros(PROFILE), buy, sell)[0] is None
    zero = u.copy(); zero[10] = 0.
    assert summarize_profile(zero, buy, sell)[0] is not None
    dates = pd.date_range("2020-01-01", periods=50, freq="D"); calendar = dates[dates.dayofweek < 5]
    raw = np.ones((len(dates), 1440)); raw[:, 540] = 2.
    factors = minute_seasons(raw, dates, calendar)
    day = calendar[21]
    np.testing.assert_allclose(factors.loc[day, 540], 2.)
    changed = raw.copy(); changed[dates.get_loc(day):] = 10000.
    np.testing.assert_allclose(minute_seasons(changed, dates, calendar).loc[day], factors.loc[day])
    assert factors.iloc[:20].isna().all(axis=None)
    changed = raw.copy(); previous = calendar[1:21]
    for stamp in previous[:6]: changed[dates.get_loc(stamp), 540] = np.nan
    assert pd.isna(minute_seasons(changed, dates, calendar).loc[day, 540])
    c = np.tile(100. + .25 * np.arange(1440), (len(dates), 1))
    grid = SimpleNamespace(ts=dates.to_numpy(), c=c.copy(), buy=np.full(c.shape, 6.), sell=np.full(c.shape, 4.),
                           v=np.full(c.shape, 10.), daily_atr=lambda n: np.ones(len(dates)))
    endpoint = day + pd.Timedelta(hours=9)
    profile, _ = make_memory_features(None, calendar, [endpoint], grid=grid)
    assert profile.profile_known.iloc[0]
    grid.c[dates.get_loc(day), 536:541] = 100000.  # Only the excluded current5min bar changes.
    after, _ = make_memory_features(None, calendar, [endpoint], grid=grid)
    np.testing.assert_allclose(profile[MEMORY_FEATURES], after[MEMORY_FEATURES])
    saved = grid.c[dates.get_loc(day), 500]
    grid.c[dates.get_loc(day), 500] = np.nan
    missing, _ = make_memory_features(None, calendar, [endpoint], grid=grid)
    assert not missing.profile_known.iloc[0]
    grid.c[dates.get_loc(day), 500] = saved
    grid.buy[dates.get_loc(day), 510] = np.nan
    missing, _ = make_memory_features(None, calendar, [endpoint], grid=grid)
    assert not missing.profile_known.iloc[0]
    grid.buy[dates.get_loc(day), 510] = 6.
    base = pd.DataFrame([{**{name: 0. for name in LOCAL_FEATURES}, "date": day, "day": dates.get_loc(day),
                          "signal_j": 540, "side": side, "label_valid": False} for side in (1, -1)])
    attached, _ = add_memory_features(base, profile)
    assert len(attached) == 2 and not attached.label_valid.any()
    np.testing.assert_allclose(attached.side_x_pressure120, [.2, -.2])
    for bad_time in (pd.NaT, endpoint - pd.Timedelta(minutes=6)):
        invalid = profile.copy(); invalid["profile_last_input_time"] = bad_time
        try: add_memory_features(base, invalid)
        except ValueError: pass
        else: raise AssertionError("Known profile accepted a missing/stale endpoint")
    original = list(L.FEATURES)
    assert len(FEATURES) == 34 and LOCAL_FEATURES == original
    assert estimator("HGB_MEMORY").get_params() == estimator("HGB_LOCAL").get_params()
    assert estimator("RIDGE_MEMORY").get_params() == estimator("RIDGE_LOCAL").get_params()
    assert estimator("HGB_MEMORY").max_iter == 120 and estimator("RIDGE_MEMORY").alpha == 100.
    assert L.FEATURES == original
    return dict(passed=True, actual_cache_inputs_fits_or_outcomes_read=False, feature_count=len(FEATURES),
                checks=["source_kappa_recurrence", "valid_zeros_and_invalid_denominators",
                        "prior20_min15_sameclock_and_current_future_exclusion", "exact120_pre_event_profile",
                        "current5min_bar_excluded", "missing_profile_minute_not_stretched",
                        "exact_nonmissing_Tminus5_contract", "label_independent_shared_eligibility",
                        "side_interactions_and_algorithm_matched_fixed_learners"], selectable_order=list(SELECTABLE),
                control_for=CONTROL_FOR)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--phase", choices=["self-check", "design"], required=True)
    parser.add_argument("--prereg"); parser.add_argument("--out", type=Path, default=OUT); parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    if args.phase == "self-check": print(json.dumps(self_check(), indent=2))
    elif not args.prereg: parser.error("--prereg required before actual cache/input/fits/outcome reads")
    else: run(args.prereg, out=args.out, root=args.root)
