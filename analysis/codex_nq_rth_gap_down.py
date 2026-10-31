"""Fixed independent gap-down reconstruction. Imports read no market files."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import FunctionType, SimpleNamespace
import warnings

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_nq_rth_gap_down_20261027"
PLAN = "agents/codex/plans/nq_rth_gap_down_20261027.md"
os.environ["NUMBA_CACHE_DIR"] = str(OUT / "cache/numba")
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "analysis"))
import numpy as np
import pandas as pd
import grid as shared
from grid24 import Grid24, jof
import metrics as M
import resampling as R
from codex_s03_calendar import calendar_status
from codex_hunt_v2_ldf_delta import tstat, valid_ohlcv
from codex_hunt_v2_ldf_delta_design import nw_t

FIELDS = ("open", "high", "low", "close", "volume")
OPEN_J, ENTRY_J, STOP_POINTS = 511, 512, 100.


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def safe(x):
    if isinstance(x, dict): return {str(k): safe(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [safe(v) for v in x]
    if isinstance(x, np.generic): return safe(x.item())
    if isinstance(x, float) and not np.isfinite(x): return None
    return x


def dump(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f: json.dump(safe(value), f, indent=2, allow_nan=False); f.write("\n")


def csv(path, frame):
    with Path(path).open("x") as f: frame.to_csv(f, index=False, float_format="%.12g")


def execute(g, signals):
    """Shared execution, isolated native point value and zero internal fees."""
    env = dict(shared.execute.__globals__, POINT_VALUE=2., COST=0.)
    fn = FunctionType(shared.execute.__code__, env, "native_MNQ_execute",
                      shared.execute.__defaults__, shared.execute.__closure__)
    return fn(g, signals, max_trades=1, max_losses=1, name="fixed_gap_reconstruction")


def complete_until_exit(valid, row, first, last):
    return bool(valid[row, first:last + 1].all())


def synthetic():
    def fixture():
        o = np.full((1, 6), 500.); h = o + 1; l = o - 1; c = o.copy(); c[0, -1] = 510; h[0, -1] = 511
        return SimpleNamespace(o=o, h=h, l=l, c=c, last_j=np.array([5]), ts=np.array([np.datetime64("2030-01-02")]))
    sig = pd.DataFrame([dict(day=0, dj=0, side=1, stop=100., target=np.inf, exit_j=5)])
    a = fixture(); t = execute(a, sig); assert len(t) == 1 and t.iloc[0].kind == 2 and t.iloc[0].exit == 510
    a = fixture(); a.l[0, 1] = 400.; t = execute(a, sig); assert t.iloc[0].kind == 0 and t.iloc[0].j1 == 1
    assert np.isclose(t.iloc[0].pnl - 2.24, -202.24)
    a = fixture(); a.o[0, 2] = 380; a.h[0, 2] = 381; a.l[0, 2] = 379; a.c[0, 2] = 380
    t = execute(a, sig); assert t.iloc[0].exit == 380 and t.iloc[0].j1 == 2
    a = fixture(); a.l[0, 0] = 300; t = execute(a, sig); assert t.iloc[0].kind == 2
    v = np.ones((1, 6), bool); v[0, 3] = False
    assert complete_until_exit(v, 0, 1, 2) and not complete_until_exit(v, 0, 1, 5)
    assert calendar_status("2024-11-29")["cash_close_j"] == 720
    assert calendar_status("2025-01-09")["kind"] == "holiday"
    assert OPEN_J == int(jof(831)) and ENTRY_J == int(jof(832))
    return dict(checks=9, passed=True, actual_market_inputs=False,
                entry_active=True, worse_gap_fill=True, exact_touch=True,
                pre_entry_low_ignored=True, unknown_held_path_not_repaired=True)


def verify(prereg, phase, reconstruction=False):
    if subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() != "codex/work":
        raise ValueError("Only codex/work")
    subprocess.check_call(["git", "merge-base", "--is-ancestor", prereg, "HEAD"], cwd=ROOT)
    if subprocess.check_output(["git", "show", prereg + ":" + PLAN], cwd=ROOT) != (ROOT / PLAN).read_bytes():
        raise ValueError("Preregistered plan changed")
    if subprocess.check_output(["git", "show", "HEAD:analysis/codex_nq_rth_gap_down.py"], cwd=ROOT) != Path(__file__).read_bytes():
        raise ValueError("Commit exact implementation before market values")
    destination = OUT / (("reconstruction_" if reconstruction else "") + phase)
    if destination.exists(): raise ValueError("Retained phase exists; no overwrite or alternate retry directory")
    if phase == "validation" and not (OUT / "validation_authorization.json").is_file():
        raise ValueError("Commit the unchanged design disposition before validation")
    amendment = "agents/codex/research/nq_rth_gap_down_replication_scope.md"
    if reconstruction:
        if subprocess.check_output(["git", "show", "HEAD:" + amendment], cwd=ROOT) != (ROOT / amendment).read_bytes():
            raise ValueError("Commit explicit post-gross scope amendment before stopped outcomes")
        original = json.loads((OUT / "design/completed.json").read_text())
        if original["status"] != "REJECT_GROSS": raise ValueError("Preserved gross rejection required")
    years = range(2018, 2023) if phase == "design" else range(2023, 2027)
    paths = ([ROOT / "agents/codex/inputs/ob_v2_bench/NQ_1min_2017.csv"] if phase == "design"
             else [ROOT / "data/NQ_1min_2022.csv"])
    paths += [ROOT / f"data/NQ_1min_{y}.csv" for y in years]
    for p in paths:
        if not p.is_file(): raise FileNotFoundError(p)
    deps = [PLAN, "analysis/codex_nq_rth_gap_down.py", "analysis/grid.py", "analysis/grid24.py",
            "analysis/metrics.py", "analysis/resampling.py", "analysis/codex_s03_calendar.py",
            "analysis/replica.py", "analysis/codex_hunt_v2_ldf_delta.py",
            "analysis/codex_hunt_v2_ldf_delta_design.py"]
    return paths, dict(preregistration_commit=prereg, implementation_commit=subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        files={str(p.relative_to(ROOT)): dict(sha256=sha(p), bytes=p.stat().st_size) for p in paths},
        code={p: sha(ROOT / p) for p in deps}, phase=phase,
        started_utc=datetime.now(timezone.utc).isoformat(), future_data_loaded_in_design=False,
        post_failed_gross_source_reconstruction=reconstruction,
        scope_amendment_sha256=sha(ROOT / amendment) if reconstruction else None)


def load_grid(paths, phase, dest):
    frames = []
    for source in paths:
        x = pd.read_csv(source, usecols=["date", "time", *FIELDS])
        x["source"] = str(source.relative_to(ROOT)); x["source_line"] = np.arange(len(x)) + 2
        frames.append(x)
    raw = pd.concat(frames, ignore_index=True)
    duplicates = raw[raw.duplicated(["date", "time"], keep=False)].copy()
    different = duplicates.groupby(["date", "time"])[list(FIELDS)].nunique(dropna=False).gt(1).any(axis=1)
    bad_keys = set(different[different].index.tolist())
    clean = raw.drop_duplicates(["date", "time"], keep="first").sort_values(["date", "time"])
    valid = valid_ohlcv(*(clean[f].to_numpy(float) for f in FIELDS))
    valid &= np.array([(d, t) not in bad_keys for d, t in zip(clean.date, clean.time)])
    csv(dest / "duplicates.csv", duplicates)
    csv(dest / "invalid_observations.csv", clean[~valid])
    cache = OUT / "cache" / phase; cache.mkdir(parents=True, exist_ok=True)
    for path in paths:
        link = cache / path.name
        if link.is_symlink():
            if link.resolve() != path.resolve(): raise ValueError("Unexpected cached source symlink")
        elif link.exists(): raise ValueError("Unexpected nonlink cache file")
        else: link.symlink_to(path)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        g = Grid24(str(cache / "*.csv"), night_pattern="")
    presence = np.zeros_like(g.o, dtype=bool)
    rr, jj = np.searchsorted(g.dates, clean.date.to_numpy()), jof(clean.time.to_numpy()).astype(int)
    if not ((jj >= 0) & (jj < 1440)).all(): raise ValueError("Invalid native HHMM")
    presence[rr, jj] = valid
    for name, attr in zip(FIELDS, "ohlcv"):
        if not np.allclose(getattr(g, attr)[rr, jj], clean[name].to_numpy(float), equal_nan=True):
            raise ValueError("Shared Grid24 source parity failure:" + name)
    for attr in "ohlcv": getattr(g, attr)[~presence] = np.nan
    return g, presence, dict(input_rows=len(raw), unique_rows=len(clean), duplicate_rows=len(duplicates),
        conflicting_keys=len(bad_keys), invalid_or_conflicting_observations=int((~valid).sum()),
        no_forward_fill=True, exporter_timestamp_contract="existing repo close-labelled CT; original author parity unavailable",
        continuous_contract_roll_identity="unverified; no price adjustment or outcome-selected roll filter")


def calendar_events(g, valid, phase):
    start = pd.Timestamp("2018-01-01" if phase == "design" else "2023-01-01")
    end = pd.Timestamp("2022-12-31") if phase == "design" else min(pd.Timestamp(g.ts[-1]), pd.Timestamp("2026-10-27"))
    index = {int(d): i for i, d in enumerate(g.dates)}
    rows = []; previous = None
    for date in pd.date_range(start - pd.Timedelta(days=14), end):
        status = calendar_status(date)
        if status["kind"] not in ("normal", "early"): continue
        if date >= start:
            key = int(date.strftime("%Y%m%d")); r = index.get(key)
            prev = index.get(int(previous.strftime("%Y%m%d"))) if previous is not None else None
            pj = calendar_status(previous)["cash_close_j"] if previous is not None else None
            ref_ok = prev is not None and pj is not None and valid[prev, pj]
            open_ok = r is not None and valid[r, OPEN_J]
            entry_ok = r is not None and valid[r, ENTRY_J]
            known = bool(ref_ok and open_ok and entry_ok)
            record = dict(date=date.date().isoformat(), year=date.year, row=r, kind=status["kind"],
                exit_j=status["cash_close_j"], previous_cash_date=previous.date().isoformat() if previous is not None else None,
                previous_close_j=pj, reference_known=bool(ref_ok), opening_known=bool(open_ok), entry_known=bool(entry_ok),
                signal_known=known, gap_down=None, gap_points=None, raw_endpoint_known=False,
                known_before_entry_calendar=True, entry_bar_close_label="08:32CT", entry_physical_time="08:31CT")
            if known:
                record["gap_points"] = float(g.o[r, OPEN_J] - g.c[prev, pj])
                record["gap_down"] = bool(record["gap_points"] < 0)
                record["raw_endpoint_known"] = bool(valid[r, record["exit_j"]])
            rows.append(record)
        previous = date
    return pd.DataFrame(rows)


def native_trades(g, valid, events, *, entry=ENTRY_J, only_gap=False):
    eligible = events[events.signal_known].copy()
    if only_gap: eligible = eligible[eligible.gap_down.astype(bool)]
    signals = pd.DataFrame(dict(day=eligible.row.astype(int), dj=entry - 1, side=1,
                               stop=STOP_POINTS, target=np.inf, exit_j=eligible.exit_j.astype(int)))
    t = execute(g, signals)
    if t.empty: return t
    t = t.merge(eligible[["row", "gap_down", "gap_points", "kind", "exit_j"]].rename(columns={"kind": "calendar_kind"}),
                left_on="day", right_on="row", validate="one_to_one")
    t["resolved"] = [complete_until_exit(valid, int(a), int(b), int(c)) and
                     (int(k) != 2 or int(c) == int(expected))
                     for a, b, c, k, expected in zip(t.day, t.j0, t.j1, t.kind, t.exit_j)]
    t["event_id"] = ["GAP_" + pd.Timestamp(d).strftime("%Y%m%d") for d in t.date]
    t["year"] = pd.DatetimeIndex(t.date).year
    t["gross_mnq"] = t.pnl
    t["commission_mnq"] = 1.24; t["entry_slippage_mnq"] = .50; t["exit_slippage_mnq"] = .50
    t["net_mnq"] = t.gross_mnq - 2.24
    t["net_nq_native"] = t.gross_mnq * 10 - 17.25
    t["net_nq_source_cost"] = t.gross_mnq * 10 - 20
    t["net_mnq_severe"] = t.gross_mnq - 1.24 - 6. - t.kind.eq(0) * 6.
    t["net_nq_author_severe"] = t.gross_mnq * 10 - 70. - t.kind.eq(0) * 60.
    for col in ("pnl", "net", "mae", "gross_mnq", "net_mnq", "net_nq_native", "net_nq_source_cost", "net_mnq_severe", "net_nq_author_severe"):
        t.loc[~t.resolved, col] = np.nan
    t["entry_utc"] = [((pd.Timestamp(d) + pd.Timedelta(minutes=int(j) - 1)).tz_localize("America/Chicago").tz_convert("UTC").isoformat()) for d, j in zip(t.date, t.j0)]
    t["exit_utc"] = [((pd.Timestamp(d) + pd.Timedelta(minutes=int(j) - (k != 2))).tz_localize("America/Chicago").tz_convert("UTC").isoformat()) for d, j, k in zip(t.date, t.j1, t.kind)]
    t["exit_clock_precision"] = np.where(t.kind.eq(2), "scheduled close", "within stated one-minute interval; tick time unavailable")
    return t


def measurements(trades, days, model, value="net_mnq"):
    selected = trades[trades.resolved].copy()
    if model.startswith("GAP"): selected = selected[selected.gap_down.astype(bool)]
    daily = selected.groupby("date")[value].sum().reindex(days, fill_value=0.)
    # One initial-equity observation seeds shared drawdown metrics, not a trading day.
    m = M.perf(np.r_[0., daily.to_numpy()], selected[value])
    actual = M.perf(daily, selected[value])
    for k in ("annual", "sharpe", "sortino"): m[k] = actual[k]
    m["calmar"] = m["annual"] / m["max_dd"] if m["max_dd"] > 0 else None
    m.update(model=model, dates=len(days), total=float(selected[value].sum()),
             trade_t=tstat(selected[value]), daily_NW5_t=nw_t(daily.to_numpy()),
             DSR_N326=M.deflated_sharpe(selected[value], 326) if len(selected) >= 10 else None,
             DSR_N1000_scenario=M.deflated_sharpe(selected[value], 1000) if len(selected) >= 10 else None,
             statistic_unit=value, side="long", short_trades=0,
             known_calendar_only=True, initial_equity_seed=True)
    return m, daily


def run(phase, prereg, reconstruction=False):
    paths, binding = verify(prereg, phase, reconstruction)
    dest = OUT / (("reconstruction_" if reconstruction else "") + phase); dest.mkdir(parents=True)
    dump(dest / "pre_value_binding.json", binding)
    dump(dest / "synthetic_checks.json", synthetic())
    g, valid, audit = load_grid(paths, phase, dest)
    events = calendar_events(g, valid, phase); csv(dest / "calendar_events.csv", events)
    dump(dest / "source_audit.json", audit)
    eligible = events[events.signal_known & events.gap_down.eq(True) & events.raw_endpoint_known].copy()
    eligible["gross_mnq"] = [(g.c[int(r), int(j)] - g.o[int(r), ENTRY_J]) * 2 for r, j in zip(eligible.row, eligible.exit_j)]
    gross_rows = []
    for period in ("all", *map(str, sorted(eligible.year.unique()))):
        x = eligible if period == "all" else eligible[eligible.year.eq(int(period))]
        gross_rows.append(dict(period=period, side="long", events=len(x), total=x.gross_mnq.sum(),
                               mean=x.gross_mnq.mean(), t=tstat(x.gross_mnq)))
    csv(dest / "gross_events.csv", eligible); csv(dest / "gross_summary.csv", pd.DataFrame(gross_rows))
    gross_pass = len(eligible) >= 100 and eligible.gross_mnq.mean() >= 4.48
    dump(dest / "gross_gate.json", dict(passed=bool(gross_pass), events=len(eligible),
        mean_mnq=eligible.gross_mnq.mean(), t=tstat(eligible.gross_mnq), hurdle=4.48,
        native_RT=2.24, costs_subtracted=False, phase=phase))
    if phase == "design" and not gross_pass and not reconstruction:
        dump(dest / "completed.json", dict(status="REJECT_GROSS", gross_pass=False,
             completed_utc=datetime.now(timezone.utc).isoformat(), no_stopped_design_or_account_tests=True))
        return
    trades = native_trades(g, valid, events)
    if trades.empty: raise ValueError("No execution paths")
    csv(dest / "all_long_trades.csv", trades)
    primary = trades[trades.gap_down.astype(bool)].copy(); csv(dest / "gap_trades.csv", primary)
    diagnostic = native_trades(g, valid, events, entry=OPEN_J, only_gap=True)
    csv(dest / "opening_print_diagnostic.csv", diagnostic)
    bad_outcome = set(pd.to_datetime(trades.loc[~trades.resolved, "date"]))
    good_days = pd.DatetimeIndex(pd.to_datetime(events.loc[events.signal_known, "date"]))
    good_days = good_days[~good_days.isin(bad_outcome)]
    rows, daily_values = [], {}
    for name, value in (("GAP_NATIVE", "net_mnq"), ("ALL_LONG_NATIVE", "net_mnq"),
                        ("GAP_SOURCE_COST", "net_nq_source_cost"), ("GAP_SEVERE_COST", "net_mnq_severe")):
        for period in ("all", *map(str, sorted(set(good_days.year)))):
            d = good_days if period == "all" else good_days[good_days.year == int(period)]
            sub = trades[trades.date.isin(d)]
            m, ds = measurements(sub, d, name, value); rows.append(dict(period=period, **m))
            if period == "all": daily_values[name] = ds
    csv(dest / "metrics.csv", pd.DataFrame(rows))
    daily_frame = pd.DataFrame(daily_values).rename_axis("date").reset_index()
    csv(dest / "daily.csv", daily_frame)
    primary_m = next(x for x in rows if x["model"] == "GAP_NATIVE" and x["period"] == "all")
    years_positive = sum(x["total"] > 0 for x in rows if x["model"] == "GAP_NATIVE" and x["period"] != "all")
    indicated = (primary_m["trades"] >= 100 and primary_m["total"] > 0 and
                 (primary_m["trade_t"] or 0) >= 2 and (primary_m["daily_NW5_t"] or 0) >= 2 and years_positive >= 4)
    cache = OUT / "cache" / (phase + "_grid.npz")
    np.savez_compressed(cache, o=g.o, h=g.h, l=g.l, c=g.c, dates=g.dates, valid=valid, ts=g.ts)
    summary = dict(status=("SOURCE_RECONSTRUCTION_ONLY" if reconstruction else
                          "DESIGN_INDICATION" if indicated else "REJECT_DESIGN"), gross_pass=bool(gross_pass),
        preserved_original_gross_rejection=reconstruction, promotion_authorized=False,
        indicated_design_gate_pass=bool(indicated), primary=primary_m, positive_years=years_positive,
        expected_cash_dates=len(events), unknown_signal_dates=int((~events.signal_known).sum()),
        unresolved_primary_paths=int((~primary.resolved).sum()), unresolved_all_long_paths=int((~trades.resolved).sum()),
        observed_known_statistic_dates=len(good_days), source_complete=bool(events.signal_known.all() and trades.resolved.all()),
        cache_sha256=sha(cache), cache_path=str(cache.relative_to(ROOT)),
        counts=dict(primary_path=1, always_long_control=1, nonexecutable_opening_print_path=1,
                    frozen_economic_cost_definitions=5, hunt_v2_added_evaluations=0),
        t_threshold_N326=M.t_threshold(326), author_trials="UNKNOWN; side/stop/threshold selection retained",
        completed_utc=datetime.now(timezone.utc).isoformat(), input_binding_sha256=sha(dest / "pre_value_binding.json"))
    dump(dest / "completed.json", summary)
    print(json.dumps(safe(summary), indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--phase", choices=("design", "validation")); p.add_argument("--prereg")
    p.add_argument("--synthetic", action="store_true"); p.add_argument("--source-reconstruction", action="store_true"); a = p.parse_args()
    if a.synthetic: print(json.dumps(synthetic()))
    elif a.phase and a.prereg: run(a.phase, a.prereg, a.source_reconstruction)
    else: p.error("Select synthetic or phase/prereg")
