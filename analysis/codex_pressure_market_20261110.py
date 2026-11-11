"""Frozen common-market/flow price-impact extension; no outcomes on import.

Only --phase design with committed protocol may read actual inputs or returns.
The --phase self-check path uses invented matrices and normalization tables.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import gzip
import hashlib
import json
import subprocess
import warnings

import numpy as np
import pandas as pd

import codex_pressure_build_20261110_inputs as I
import codex_pressure_build_20261110_replay as E
import codex_pressure_market_20261110_inputs as J
import codex_cash_open_repair as C

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_pressure_market_20261110"
PLAN = "agents/codex/plans/pressure_market_20261110.md"
EVIDENCE = "agents/codex/evidence/pressure_market_20261110.md"
CODE = ["analysis/codex_pressure_market_20261110.py",
        "analysis/codex_pressure_market_20261110_inputs.py",
        "analysis/codex_pressure_build_20261110_inputs.py",
        "analysis/codex_pressure_build_20261110_replay.py",
        "analysis/grid.py", "analysis/grid24.py", "analysis/metrics.py",
        "analysis/codex_cash_open_repair.py", "analysis/codex_s03_calendar.py"]
NATIVE_MANIFEST = "agents/codex/inputs/bridge_native_2018_22_20261108/transfer_manifest.json"
MODELS = ("FULL", "COMMON_ONLY", "FLOW_ONLY")
FEATURES = {"FULL": ("q0", "q1", "q2", "e0", "e1", "e2"),
            "COMMON_ONLY": ("e0", "e1", "e2"),
            "FLOW_ONLY": ("q0", "q1", "q2")}
SIGNAL_COLUMNS = ["date", "day", "signal_j", "event_j", "side", "stop_price", "max_stop",
                  "target_R", "exit_j", "z", "model", "fit_last_date", "input_last_time"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _dump(path, value):
    C.write(path, json.dumps(value, indent=2, default=str, allow_nan=True) + "\n")


def _csv(path, frame):
    payload = frame.to_csv(index=False).encode()
    C.write(path, gzip.compress(payload, mtime=0) if str(path).endswith(".gz") else payload)


def _season(history):
    """Historical own-clock medians; caller has already selected past dates."""
    median = history.groupby("j").raw_y.agg(lambda x: np.median(np.abs(x)))
    counts = history.groupby("j").date.nunique()
    median = median[counts >= 15]
    center = median.median()
    if not np.isfinite(center) or center <= 1e-12:
        return pd.Series(dtype=float)
    return median / center


def _normalize(frame, nq_season, es_season):
    """All ES lags use their corresponding ES clock, not the event's clock."""
    result = frame.copy()
    result["fN"] = result.j.map(nq_season)
    result["y"] = result.raw_y / result.fN
    valid = np.isfinite(result.y) & result.fN.gt(1e-12)
    for lag in range(3):
        scale = (result.j - 5 * lag).map(es_season)
        result[f"e{lag}"] = result[f"eraw{lag}"] / scale
        valid &= np.isfinite(result[f"e{lag}"]) & scale.gt(1e-12)
    for name in ("q0", "q1", "q2"):
        valid &= np.isfinite(result[name])
    return result.loc[valid].copy()


def _fits(history):
    """Fit every model on the identical row matrix, then apply a common gate."""
    target = history.y.to_numpy(float)
    fits = {}
    for name in MODELS:
        matrix = np.column_stack([np.ones(len(history)), history[list(FEATURES[name])].to_numpy(float)])
        beta, _, rank, _ = np.linalg.lstsq(matrix, target, rcond=None)
        residual = target - matrix @ beta
        rms = float(np.sqrt(np.mean(residual ** 2)))
        fits[name] = dict(beta=beta, rank=int(rank), rms=rms,
                          finite=bool(np.isfinite(beta).all() and np.isfinite(rms)),
                          full_rank=bool(rank == matrix.shape[1]))
    common = (all(v["finite"] and v["full_rank"] and v["rms"] > 1e-9 for v in fits.values())
              and fits["FULL"]["beta"][1] > 0
              and fits["FLOW_ONLY"]["beta"][1] > 0
              and fits["FULL"]["beta"][4] > 0
              and fits["COMMON_ONLY"]["beta"][1] > 0)
    return fits, bool(common)


def model_signals(minutes, grid, es_minutes, es_grid=None):
    """Return (signals_by_model, daily_fits, calendar, input/feature_audit).

    Real-data calls are study operations. All normalizers and fits use exact
    previous twenty normal-cash slots, with roll dates excluded, not replaced.
    Confirmation uses NQ only; ES at the later confirmation is not required.
    """
    if es_grid is None:
        es_grid = I.make_grid(es_minutes)
    b = I.complete5min_ohlcv(minutes).copy()
    es, es_bar_audit = I.aggregate_complete(es_minutes, minutes=5, require_flow=False)
    es = es.copy()
    b["date"] = b.index.normalize(); b["j"] = b.index.hour * 60 + b.index.minute
    es["date"] = es.index.normalize(); es["j"] = es.index.hour * 60 + es.index.minute
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        atr_nq = pd.Series(grid.daily_atr(15), index=pd.to_datetime(grid.ts))
        atr_es = pd.Series(es_grid.daily_atr(15), index=pd.to_datetime(es_grid.ts))
    b["atr"] = b.date.map(atr_nq)
    b["es_atr"] = b.date.map(atr_es)
    es["atr"] = es.date.map(atr_es)
    b["raw_y"] = (b.close - b.open) / b.atr
    es["raw_y"] = (es.close - es.open) / es.atr
    b["q0"] = (b.buy - b.sell) / b.volume.replace(0, np.nan)
    for lag in (1, 2):
        b[f"q{lag}"] = b.q0.reindex(b.index - pd.Timedelta(minutes=5 * lag)).to_numpy()
    es_body = es.close - es.open
    for lag in range(3):
        # Same-session slots used below make this exactly today's ES ATR.
        b[f"eraw{lag}"] = es_body.reindex(b.index - pd.Timedelta(minutes=5 * lag)).to_numpy() / b.es_atr.to_numpy()
    calendar = pd.DatetimeIndex([d for d in pd.to_datetime(grid.ts) if C.normal_cash(d)])
    rollfree = frozenset(d for d in calendar if not C.roll_guard(d))
    b["rollfree"] = b.date.isin(rollfree)
    es["rollfree"] = es.date.isin(rollfree)
    # Independent own-source normalizer samples; all three fits below share rows.
    nq_cols = ["raw_y", "q0", "q1", "q2", "atr"]
    nq_train = b[b.j.between(525, 840) & b.rollfree
                 & np.isfinite(b[nq_cols]).all(axis=1) & b.atr.gt(0)]
    es_train = es[es.j.between(515, 840) & es.rollfree
                  & np.isfinite(es[["raw_y", "atr"]]).all(axis=1) & es.atr.gt(0)]
    b = b[b.j.between(525, 845)].copy()
    daymap = {pd.Timestamp(d): i for i, d in enumerate(grid.ts)}
    output = {name: [] for name in MODELS}
    records = []
    for k, date in enumerate(calendar):
        if k % 100 == 0:
            print("common-market fit", date.date(), "days done", k, flush=True)
        if k < 20 or date not in rollfree:
            continue
        prior = calendar[k - 20:k]
        n_hist = nq_train[nq_train.date.isin(prior)]
        e_hist = es_train[es_train.date.isin(prior)]
        if len(n_hist) < 600 or n_hist.date.nunique() < 15:
            continue
        fn, fe = _season(n_hist), _season(e_hist)
        if fn.empty or fe.empty:
            continue
        history = _normalize(n_hist, fn, fe)
        if len(history) < 600 or history.date.nunique() < 15:
            continue
        assert history.date.max() < date
        assert e_hist.empty or e_hist.date.max() < date
        fitted, admitted = _fits(history)
        fit_last = str(history.date.max().date())
        fn_hash = hashlib.sha256(fn.to_json().encode()).hexdigest()
        fe_hash = hashlib.sha256(fe.to_json().encode()).hexdigest()
        for name, fit in fitted.items():
            records.append(dict(date=str(date.date()), model=name, training_rows=len(history),
                                training_dates=int(history.date.nunique()),
                                fit_first=str(history.date.min().date()), fit_last=fit_last,
                                feature_columns=["intercept"] + list(FEATURES[name]),
                                beta=fit["beta"].tolist(), rms=fit["rms"], rank=fit["rank"],
                                admitted_common=admitted, nq_normalization_slots=len(fn),
                                es_normalization_slots=len(fe), nq_season_sha256=fn_hash,
                                es_season_sha256=fe_hash))
        if not admitted:
            continue
        today = _normalize(b[(b.date == date) & b.j.between(540, 840)], fn, fe)
        for stamp, row in today.iterrows():
            confirmation_time = stamp + pd.Timedelta(minutes=5)
            if confirmation_time not in b.index:
                continue
            conf = b.loc[confirmation_time]
            if conf.date != date:
                continue
            for name, fit in fitted.items():
                values = np.array([1.] + [float(row[c]) for c in FEATURES[name]])
                score = float((row.y - values @ fit["beta"]) / fit["rms"])
                if not np.isfinite(score) or abs(score) < 2:
                    continue
                side = -int(np.sign(score))
                if not (side * (conf.close - conf.open) > 0 and side * (conf.close - row.close) > 0):
                    continue
                decision = int(conf.j)
                stop = min(row.low, conf.low) - .25 if side > 0 else max(row.high, conf.high) + .25
                output[name].append(dict(date=date, day=daymap[date], signal_j=decision,
                                         event_j=int(row.j), side=side, stop_price=float(stop),
                                         max_stop=float(.15 * row.atr), target_R=.3,
                                         exit_j=min(decision + 31, 895), z=score, model=name,
                                         fit_last_date=fit_last, input_last_time=confirmation_time))
    audit = dict(nq_input=minutes.attrs.get("input_audit", {}), es_input=es_minutes.attrs.get("input_audit", {}),
                 es_five_minute=es_bar_audit, models=list(MODELS), selectable=["FULL"],
                 nq_season="08:45--14:00, own prior20 normal-cash slots, rolls excluded without replacement, min15 perclock",
                 es_season="08:35--14:00, own prior20 normal-cash slots, rolls excluded without replacement, min15 perclock",
                 es_lags="current-day shifted priorATR_ES and each lag's actual clock seasonal factor",
                 common_training_rows=True, current_day_fit=False,
                 limits="ES is a common-market conditioning input, not an executed hedge; cross-feed receipt, roll and native micro parity remain unverified")
    return ({name: pd.DataFrame(rows, columns=SIGNAL_COLUMNS) for name, rows in output.items()},
            pd.DataFrame(records), calendar, audit)


def run(prereg, *, out=OUT, root=ROOT):
    """Frozen actual-design runner; never reads 2023+ outcomes."""
    out, root = Path(out), Path(root)
    paths = [PLAN, EVIDENCE] + CODE + [NATIVE_MANIFEST]
    for name in paths:
        frozen = subprocess.check_output(["git", "show", f"{prereg}:{name}"], cwd=ROOT)
        if frozen != (ROOT / name).read_bytes():
            raise ValueError(f"Protocol/code not frozen: {name}")
    if (out / "results.json").exists():
        raise ValueError("Existing outcomes cannot be overwritten")
    out.mkdir(parents=True, exist_ok=True)
    _dump(out / "binding.json", dict(prereg=prereg, files={p: sha(ROOT / p) for p in paths},
                                     models=list(MODELS), selectable=["FULL"], new_economic_definitions=3,
                                     prior_failed_families_retained=True, validation_outcomes_read=False))
    minutes = I.load_design_native(root=root)
    es_minutes, es_audit = J.load_es_minutes(root)
    es_minutes.attrs["input_audit"] = es_audit
    grid = I.make_grid(minutes)
    signals, fits, calendar, audit = model_signals(minutes, grid, es_minutes)
    _dump(out / "input_and_feature_audit.json", audit)
    _csv(out / "daily_fits.csv.gz", fits)
    summaries, tables = {}, []
    for name in MODELS:
        _csv(out / f"{name}_signals.csv.gz", signals[name])
        trades, execution = E.replay(signals[name], grid=grid, max_trades=4)
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
    p = summaries["FULL"]; s = p["summary"]
    gates = dict(trades=s["trades"] >= 150, long_count=p["long_trades"] >= 25,
                 short_count=p["short_trades"] >= 25, net=s["total"] > 0,
                 trade_t=s["t_trade"] >= 2, daily_nw5=s["t_nw5"] >= 1.5,
                 profit_factor=s["profit_factor"] >= 1.2, years=p["positive_years"] >= 4,
                 micro_net=p["micro"]["total"] > 0, stress_net=p["stress"]["total"] > 0,
                 stop_first_net=p["stop_first"]["total"] > 0,
                 held_paths=p["execution"]["unknown_held_path_trades"] == 0)
    result = dict(prereg=prereg, stats=summaries, basic_gates=gates, basic_pass=all(gates.values()),
                  selected=None, design_gate_complete=False, validation_allowed=False,
                  new_economic_definitions=3, selectable=["FULL"],
                  prior_families="Failed NQ-only impact/fades, learned payoffs and passive-entry attempts remain in selection history; this is a related common-input extension")
    _dump(out / "results.json", result)
    print(pd.DataFrame({name: value["summary"] for name, value in summaries.items()}).T.to_string(), flush=True)
    print(json.dumps({"basic_gates": gates, "basic_pass": result["basic_pass"]}, indent=2), flush=True)
    return result


def self_check():
    """Only invented regressions/seasonal tables, never actual prices or returns."""
    rng = np.random.default_rng(20261110)
    h = pd.DataFrame(rng.normal(size=(2000, 6)), columns=FEATURES["FULL"])
    exact = np.array([.1, .7, -.2, -.1, 1.1, .2, -.15])
    h["y"] = np.column_stack([np.ones(len(h)), h[list(FEATURES["FULL"])]]) @ exact + rng.normal(0, .01, len(h))
    fitted, admitted = _fits(h)
    assert admitted and fitted["FULL"]["rank"] == 7
    np.testing.assert_allclose(fitted["FULL"]["beta"], exact, atol=.002)
    assert all(v["rms"] > 0 for v in fitted.values())
    row = pd.DataFrame(dict(j=[540], raw_y=[6.], eraw0=[8.], eraw1=[8.], eraw2=[8.], q0=[.1], q1=[.2], q2=[.3]))
    n = _normalize(row, pd.Series({540: 2.}), pd.Series({530: 4., 535: 2., 540: 1.}))
    np.testing.assert_allclose(n[["y", "e0", "e1", "e2"]].iloc[0].to_numpy(), [3., 8., 4., 2.])
    dates = pd.bdate_range("2020-01-01", periods=20)
    history = pd.DataFrame([dict(date=d, j=j, raw_y=value) for d in dates for j, value in ((535, 2.), (540, 4.))])
    season = _season(history)
    np.testing.assert_allclose(season.loc[[535, 540]], [2 / 3, 4 / 3])
    history = history[~((history.j == 535) & (history.date.isin(dates[:6])))]
    assert 535 not in _season(history).index
    return dict(passed=True, real_inputs_or_outcomes_read=False,
                checks=["shared_row_OLS_and_positive_impact_gates", "lag_specific_ES_clock_factors",
                        "own_clock_season_medians", "minimum15_dates_perclock"],
                models=list(MODELS), selectable=["FULL"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["self-check", "design"], required=True)
    parser.add_argument("--prereg")
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    if args.phase == "self-check":
        print(json.dumps(self_check(), indent=2))
    elif not args.prereg:
        parser.error("--prereg required before actual inputs/forecasts/returns")
    else:
        run(args.prereg, out=args.out, root=args.root)
