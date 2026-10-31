"""Independent S03 source, feature, execution and fixed-null diagnostics.

Import is inert. No grid or historical result is opened by this module. The
root orchestrator must enforce the published preregistration and stage gates.
Synthetic fixtures use a separately constructed in-memory grid and explicit
expected arithmetic; none imports noise_band_chuk_test (which runs on import).
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

try:
    import codex_s03_replay as replay
    from codex_s03_calendar import calendar_status
    from metrics import perf
    from resampling import _stats, bootstrap, max_dd, permutation
except ImportError:
    from analysis import codex_s03_replay as replay
    from analysis.codex_s03_calendar import calendar_status
    from analysis.metrics import perf
    from analysis.resampling import _stats, bootstrap, max_dd, permutation

ROOT = Path(__file__).resolve().parents[1]
SEED = 20261024
SIDE_SEED = SEED + 10000
TIME_SEED = SEED + 20000
PROFILES = {
    "V2": dict(stop_sigma=.4, anchor=831, slip_ticks=1.),
    "V1": dict(stop_sigma=0., anchor=831, slip_ticks=1.),
    "C2": dict(stop_sigma=.4, anchor=830, slip_ticks=1.),
    "E2": dict(stop_sigma=.4, anchor=831, slip_ticks=3.),
}


def null_comparator_metadata(family):
    """Interpretation fixed for the already-run registered comparators."""
    if family == "time":
        return dict(causal_policy=False, retrospective_only=True,
            future_information="The same-date permutation can move directions from later raw signals to earlier checks, using a proposal count and direction mixture only known later that date.",
            comparison_scope="Future-informed retrospective comparator; not a causal random-entry strategy.",
            standalone_entry_edge_falsifier=False,
            causal_entry_timing_test="OPEN",
            interpretation="Its p-values cannot establish that causal entry timing fails or that the strategy has zero edge.")
    if family == "side":
        return dict(causal_policy=True, retrospective_only=False,
            isolated_direction_test=False,
            comparison_scope="Joint direction, reversal, occupancy, turnover and execution-cost policy comparison.",
            interpretation="Random opposite proposals create additional reversals and much higher filled trade counts; the result does not isolate direction prediction at matched turnover or costs.")
    raise ValueError("unknown registered comparator")


def _dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, default=str, allow_nan=True) + "\n")


def _digest(path):
    p = Path(path)
    if not p.exists():
        return None
    h = hashlib.sha256()
    with p.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def _grid(dates):
    dates = pd.DatetimeIndex(dates)
    g = SimpleNamespace(ts=dates.to_numpy(), dates=dates.strftime("%Y%m%d").astype(int).to_numpy(),
                        D=len(dates), trading=np.flatnonzero(dates.dayofweek < 5))
    for k in "ohlcv":
        setattr(g, k, np.full((len(dates), 1440), np.nan))
    return g


def _session(g, d, price=100., first=511, last=901):
    for k in "ohlc":
        getattr(g, k)[d, first:last + 1] = price
    g.v[d, first:last + 1] = 1.


def _features(g, proposals, sigma=.013, closes=None):
    rows = []
    closes = closes or {}
    for d in range(g.D):
        for j in tuple(range(540, 871, 30)) + (900,):
            rows.append(dict(bar_index=len(rows), day=d, j=j, date=pd.Timestamp(g.ts[d]),
                global_close=d * 1440 + j, close=closes.get(j, float(g.c[d, j])),
                sigma=sigma, signal_side=proposals.get(j, 0), feature_ready=True,
                timing_ok=j < 900, calendar_eligible=True, calendar_kind="normal",
                decision_observed=bool(np.isfinite(g.c[d, j])), long_exit=False,
                short_exit=False, observed_minutes=j - 510, expected_minutes=j - 510,
                upper=101., lower=99., vwap=100.))
    f = pd.DataFrame(rows)
    f.attrs.update(anchor=831, lookback=14)
    return f


def independent_synthetic_checks(output=None):
    """Independent selected fixtures; no historical file or engine fixture reused."""
    checks = []

    # Fourteen previous complete normal dates; a half day updates PC only.
    dates = pd.date_range("2020-01-01", periods=22, freq="B")
    g = _grid(dates)
    for d in range(g.D):
        _session(g, d, first=510)
        g.c[d, 540] = 100. + d
        g.h[d, 540] = 100. + d
        g.o[d, 510] = 50.
    half = 5
    def cal(value):
        d = dates.get_loc(pd.Timestamp(value))
        return dict(kind="early" if d == half else "normal", cash_close_j=720 if d == half else 900)
    g.c[half, 720] = 107.
    g.c[2, 600] = np.nan
    f = replay.prepare_features(g, calendar=cal)
    d = 17
    past = [i for i in range(d) if i not in (2, half)][-14:]
    r = f[(f.day == d) & (f.j == 540)].iloc[0]
    assert r.win_count == 14 and np.isclose(r.sigma, np.mean(past) / 100.)
    assert r.history_end == dates[d - 1] and r.history_start == dates[past[0]]
    rhalf = f[(f.day == half + 1) & (f.j == 540)].iloc[0]
    assert rhalf.prior_close == 107. and rhalf.prior_close_kind == "early"
    checks.append("prior14_completed_full_sessions_excludes_current_and_gapped_and_half_session")
    checks.append("immediately_previous_half_cash_close_updates_prior_close")

    # Changing only today's later data cannot remove or alter its 09:00 row.
    before = f[(f.day == d) & (f.j == 540)].iloc[0].copy()
    g.c[d, 830] = np.nan
    after = replay.prepare_features(g, calendar=cal).query("day == @d and j == 540").iloc[0]
    pd.testing.assert_series_equal(before, after)
    checks.append("current_future_missing_bar_does_not_filter_earlier_decision")

    # Source clock ambiguity changes cash open and the same-minute history.
    other = replay.prepare_features(g, anchor=830, calendar=cal)
    a = other[(other.day == d) & (other.j == 540)].iloc[0]
    assert before.session_open == 100. and a.session_open == 50.
    assert np.isclose(a.sigma, np.mean([(100. + i) / 50. - 1. for i in past]))
    checks.append("831_actual_cash_open_versus_declared_830_inclusive_anchor")

    for side in (-1, 1):
        # Stop distance uses decision close and sigma, then raw entry and inward
        # tick rounding; both fill and stop are on the exact entry minute.
        g = _grid(["2020-01-02"])
        _session(g, 0)
        g.o[0, 541] = 101.
        g.h[0, 541] = 104.
        g.l[0, 541] = 98.
        f = _features(g, {540: side}, sigma=.013, closes={540: 123.})
        t, _ = replay.run(g, years=(2020, 2020), features=f)
        r = t.iloc[0]
        dist = .4 * .013 * 123.
        raw_stop = 101. - side * dist
        stop = (np.ceil(raw_stop * 4) if side == 1 else np.floor(raw_stop * 4)) / 4
        assert len(t) == 1 and r.j0 == r.j1 == 541 and r.raw_exit == stop
        assert np.isclose(r.stop_distance, dist) and r.stop == stop and r.raw_entry == 101.
        assert np.isclose(r.net, (stop - 101.) * side * 20. - 17.25)
        assert r.entry == 101. + side * .25 and r.slips == 0
    checks.append("symmetric_entry_bar_stop_fixed_from_signal_sigma_close_and_rounded_to_raw_entry")

    # Stop stays frozen despite later sigma; market reversal closes once and
    # opens exactly one opposing trade, charging two distinct round trips.
    g = _grid(["2020-01-02"])
    _session(g, 0)
    f = _features(g, {540: 1, 570: -1})
    f.loc[f.j == 570, "sigma"] = .5
    for k in "ohlc":
        getattr(g, k)[0, 571:902] = 98.
    t, _ = replay.run(g, years=(2020, 2020), features=f)
    assert len(t) == 2 and t.side.tolist() == [1, -1]
    assert t.iloc[0].stop == 99.5 and t.iloc[0].raw_exit == 98.
    assert t.iloc[0].kind == 0 and t.iloc[0].exit_phase == "open"
    assert t.iloc[0].j1 == t.iloc[1].j0 == 571
    assert (t.attrs["orders"].status == "cancelled_flat_after_stop").sum() == 1
    assert np.isclose(t.net.sum(), -40. - 2 * 17.25)
    checks.append("frozen_stop_gap_precedes_pending_reversal_without_duplicate_close_or_new_entry")

    # The same raw geometry and no stop makes reversal independent of gap rule.
    t, _ = replay.run(g, years=(2020, 2020), features=f, stop_sigma=0)
    assert len(t) == 2 and t.iloc[0].why == "S03.ReverseX"
    assert t.iloc[0].j1 == t.iloc[1].j0 == 571 and np.isclose(t.net.sum(), -74.5)
    checks.append("market_reversal_next_observed_open_and_separate_costs")

    # A price crossing an exit threshold between checks has no market effect;
    # only the registered 09:30 close creates the next-open trailing exit.
    g = _grid(["2020-01-02"])
    _session(g, 0)
    g.c[0, 550] = 90.
    f = _features(g, {540: 1})
    f.loc[f.j == 570, "long_exit"] = True
    t, _ = replay.run(g, years=(2020, 2020), features=f, stop_sigma=0)
    assert len(t) == 1 and t.iloc[0].j1 == 571 and t.iloc[0].why == "S03.BandVwapX"
    checks.append("band_vwap_exit_at_checks_only_next_open_fill")

    f = _features(g, {540: 1, 570: 1, 600: 1})
    t, _ = replay.run(g, years=(2020, 2020), features=f, stop_sigma=0)
    assert len(t) == 1 and t.iloc[0].j1 == 901 and t.iloc[0].exit_decision_j == 900
    assert t.iloc[0].net == -17.25 and t.attrs["execution_complete"]
    checks.append("same_direction_never_adds_and_1500_flat_decision_fills_1501_open")

    # Unknown held minute remains in a closed trade; an unavailable endpoint
    # stays censored instead of receiving a fabricated final observed close.
    for k in "ohlc":
        getattr(g, k)[0, 560] = np.nan
    t, _ = replay.run(g, years=(2020, 2020), features=f, stop_sigma=0)
    assert len(t) == 1 and t.iloc[0].unknown_held_minutes == 1
    assert not t.attrs["execution_complete"] and not t.attrs["day_audit"].iloc[0].account_eligible
    checks.append("closed_trade_unknown_held_minute_blocks_account_even_when_net_reconciles")
    for k in "ohlc":
        getattr(g, k)[0, 899:] = np.nan
    t, _ = replay.run(g, years=(2020, 2020), features=f, stop_sigma=0)
    assert t.empty and len(t.attrs["censored"]) == 1 and not t.attrs["execution_complete"]
    checks.append("missing_flatten_endpoint_censored_without_fictitious_last_price_trade")

    # Null shuffles operate on raw proposals, independently of future filled
    # occupancy. Each time permutation keeps proposed count and directions.
    g = _grid(["2020-01-02", "2020-01-03"])
    for d in range(g.D):
        _session(g, d)
    f = _features(g, {540: 1, 570: -1, 600: 1})
    f["entry_eligible"] = f.feature_ready & f.timing_ok
    for family in ("side", "time"):
        proposal, counts = null_proposals(f, family, SIDE_SEED if family == "side" else TIME_SEED)
        assert len(proposal) == len(f) and np.isin(proposal, (-1, 0, 1)).all()
        assert counts.raw_proposals.sum() == 6 and counts.null_proposals.sum() == 6
        if family == "side":
            assert np.array_equal(proposal != 0, f.signal_side.to_numpy() != 0)
        else:
            for _, q in f.groupby("date"):
                assert sorted(proposal[q.index]) == sorted(q.signal_side.to_numpy())
    checks.append("nulls_randomize_raw_proposals_without_future_occupancy_conditioning")

    result = dict(passed=True, checks=len(checks), fixtures=checks,
                  independence="Own in-memory grids and expected prices/arithmetic; no replay.synthetic_checks reused",
                  market_files_opened=False)
    if output:
        Path(output).mkdir(parents=True, exist_ok=True)
        _dump(Path(output) / "independent_synthetic_checks.json", result)
    return result


def source_execution_audit(output=None):
    """Document source claims versus frozen reconstruction, without prices."""
    source = ROOT / "agents/codex/inputs/s03_noisearea/source.html"
    expected = "05a176b0c4f6804d48d427ad484175076d125a61b62122736c34c6797c0d2b52"
    actual = _digest(source)
    if actual != expected:
        raise AssertionError("archived source HTML hash differs")
    rows = [
        ("Original signal/engine/data", "HTML references PL SIGNAL, s03_engine.py, ofb_bars_NQ.csv; absent", "Bounded OHLC reconstruction; exact author parity unavailable", "open source concern"),
        ("Cash-open anchor", "open(09:30 ET) wording with close-stamped bars", "V2/V1/E2 open of 09:31 ET bar; C2 includes 09:30 bar", "frozen assumption"),
        ("Noise", "Previous14 full sessions at same minute", "Prior14 completed normal sessions with all anchor..15:00 OHLCV; current day excluded", "independent synthetic and data audit"),
        ("Prior cash close", "Prior close; early-day meaning unspecified", "Immediately preceding normal/early cash-session exact close; absent endpoint unavailable", "frozen assumption"),
        ("VWAP", "Confirmation specified; formula unspecified", "Cumulative typical price * total native volume from anchor; nonpositive cumulative volume unavailable", "frozen assumption"),
        ("Current gaps", "Two source dates SetExitOnClose, missing session-template code", "No future whole-day filter; held gaps retained; next observed pending market; censor unresolved holds", "independent synthetic and audit; account block"),
        ("Fixed stop", "0.4 * sigma(signal) * close(signal), active fill bar; rounding toward entry", "Raw next-open anchor; long ceil / short floor at0.25; adverse opening gap before pending market", "independent symmetric synthetic and data audit"),
        ("Market decisions", "Half-hour10:00..15:30 ET; trailing exits same checks", "09:00..14:30 CT strict comparisons, next native open; opposite reversal closes/opens separately", "independent synthetic and order audit"),
        ("Flatten", "16:00 ET decision /16:01 open", "15:00 CT close schedules next open; catchup real later close then open by15:59; missing held paths block", "independent synthetic and audit"),
        ("Costs", "5USD RT +1tick each side (15USD)", "7.25USD RT +1tick each side (17.25USD); E2 3ticks each side (37.25USD)", "independent raw/slipped/net reconciliation"),
        ("Intrabar path", "Source provisional minute-OHLC replica, not tick validated", "Shared grid._walk convention, entry-bar stop active; source/tick validation still open", "promotion concern"),
        ("Trial history", "At least12 author StopSigma values and chosen2017-26 history", "One local idea/four fixed return profiles;2023+ historical replication", "selection limitation"),
        ("Accounts", "Third-party Lucid examples", "Current documented Apex/personal engines; exact MNQ costs/counts; no second slippage", "separate gated accounting check"),
        ("Timing comparator", "Registered same-date permutation of raw proposed directions", "Later raw directions can move earlier: future-informed retrospective comparator; clean causal entry-timing test remains OPEN", "WITH CONCERNS; no standalone entry-edge falsification"),
        ("Side comparator", "Registered random directions at raw proposal check bars", "Opposite signals change reversals, occupancy, filled counts, turnover and costs jointly", "joint policy/cost comparison; not isolated direction prediction"),
    ]
    result = dict(source_sha256=actual, expected_source_sha256=expected,
                  replay_sha256=_digest(Path(replay.__file__)), checker_sha256=_digest(__file__),
                  exact_source_parity=False, tick_validation=False,
                  implementation_review="PASS", source_tick_data_causal_timing_review="WITH_CONCERNS",
                  time_comparator_policy=null_comparator_metadata("time"),
                  side_comparator_policy=null_comparator_metadata("side"),
                  clean_causal_entry_timing_test="OPEN",
                  independent_review_path="agents/codex/results/s03_noisearea_independent_review.md",
                  independent_review_sha256=_digest(ROOT/"agents/codex/results/s03_noisearea_independent_review.md"),
                  source_review="Source text and prior audit read; original code/data absent",
                  rows=[dict(item=a, source=b, reconstruction=c, status=d) for a,b,c,d in rows])
    if output:
        Path(output).mkdir(parents=True, exist_ok=True)
        _dump(Path(output) / "source_execution_audit.json", result)
        pd.DataFrame(result["rows"]).to_csv(Path(output) / "source_reconstruction_differences.csv", index=False)
    return result


def audit_replay(g, trades, features, *, profile="V2", calendar=None, output=None):
    """Independently rebuild feature values and audit every filled trade.

    Today's data completeness is used only when updating tomorrow's history.
    This checker never calls prepare_features or run to derive expected values.
    It accepts incomplete observed paths as disclosed research outputs while
    identifying the exact account blockers separately.
    """
    cfg = PROFILES[profile]
    anchor = 511 if cfg["anchor"] == 831 else 510
    calfun = calendar or calendar_status
    groups = {int(d): q for d, q in features.groupby("day", sort=False)}
    history, previous = [], (np.nan, pd.NaT, "unavailable")
    failures = []
    comparisons = 0
    def eq(name, actual, expected, context):
        nonlocal comparisons
        comparisons += 1
        if isinstance(expected, (bool, str)):
            ok = actual == expected
        elif pd.isna(expected):
            ok = pd.isna(actual)
        elif isinstance(expected, pd.Timestamp):
            ok = pd.Timestamp(actual) == expected
        else:
            ok = np.isclose(float(actual), float(expected), rtol=1e-11, atol=1e-9)
        if not ok:
            failures.append(dict(check=name, actual=str(actual), expected=str(expected), **context))
    last = int(features.day.max()) if len(features) else -1
    for d in range(last + 1):
        date = pd.Timestamp(g.ts[d]).normalize()
        status = calfun(date)
        if status["kind"] == "weekend":
            continue
        op = g.o[d, anchor]
        validity = np.isfinite(np.stack([getattr(g, k)[d, anchor:901] for k in "ohlcv"])).all(0)
        validity &= g.v[d, anchor:901] >= 0
        for r in groups.get(d, pd.DataFrame()).itertuples():
            j = int(r.j)
            ctx = dict(date=str(date.date()), j=j)
            eq("session_open", r.session_open, op, ctx)
            eq("prior_close", r.prior_close, previous[0], ctx)
            eq("prior_close_date", r.prior_close_date, previous[1], ctx)
            eq("prior_close_kind", r.prior_close_kind, previous[2], ctx)
            sigma = float(np.mean([abs(g.c[h, j] / g.o[h, anchor] - 1.) for h in history[-14:]])) if len(history) >= 14 else np.nan
            eq("sigma", r.sigma, sigma, ctx)
            eq("win_count", r.win_count, min(14, len(history)), ctx)
            if len(history):
                eq("history_end", r.history_end, pd.Timestamp(g.ts[history[-1]]).normalize(), ctx)
                eq("history_start", r.history_start, pd.Timestamp(g.ts[history[-14:][0]]).normalize(), ctx)
            use = validity[:j-anchor+1] & (g.v[d, anchor:j+1] > 0)
            v = g.v[d, anchor:j+1][use]
            p = (g.h[d, anchor:j+1][use] + g.l[d, anchor:j+1][use] + g.c[d, anchor:j+1][use]) / 3.
            vw = float(np.sum(p * v) / v.sum()) if v.sum() > 0 else np.nan
            upper = max(op, previous[0]) * (1. + sigma) if np.isfinite(op) and np.isfinite(previous[0]) else np.nan
            lower = min(op, previous[0]) * (1. - sigma) if np.isfinite(op) and np.isfinite(previous[0]) else np.nan
            ready = status["kind"] == "normal" and bool(validity[j-anchor]) and op > 0 and np.isfinite([previous[0], sigma, vw]).all()
            eq("vwap", r.vwap, vw, ctx)
            eq("upper", r.upper, upper, ctx)
            eq("lower", r.lower, lower, ctx)
            eq("feature_ready", r.feature_ready, bool(ready), ctx)
            expected_side = (1 if r.close > upper and r.close > vw else (-1 if r.close < lower and r.close < vw else 0)) if ready and j < 900 else 0
            source_side = getattr(r, "source_signal_side", r.signal_side)
            eq("raw_signal", source_side, expected_side, ctx)
            eq("long_exit", r.long_exit, bool(ready and r.close < max(upper, vw)), ctx)
            eq("short_exit", r.short_exit, bool(ready and r.close > min(lower, vw)), ctx)
        if status["kind"] == "normal" and op > 0 and validity.all():
            history.append(d)
        if status["kind"] in ("normal", "early"):
            endpoint = int(status.get("cash_close_j", 900))
            previous = (float(g.c[d, endpoint]), date, status["kind"])
    feature_lookup = {(int(r.day), int(r.j)): r for r in features.itertuples()}
    for i, r in enumerate(trades.itertuples()):
        ctx = dict(trade=i, date=str(pd.Timestamp(r.date).date()), j=int(r.j0))
        eq("entry_native_open", r.raw_entry, g.o[int(r.day), int(r.j0)], ctx)
        eq("slipped_entry", r.entry, r.raw_entry + r.side * .25 * cfg["slip_ticks"], ctx)
        eq("slipped_exit", r.exit, r.raw_exit - r.side * .25 * cfg["slip_ticks"], ctx)
        eq("net_final", r.net, (r.raw_exit-r.raw_entry)*r.side*20.-7.25-10.*cfg["slip_ticks"], ctx)
        eq("raw_pnl", r.pnl, (r.raw_exit-r.raw_entry)*r.side*20., ctx)
        eq("no_double_slips", r.slips, 0, ctx)
        eq("no_cross_day", r.cross_date, False, ctx)
        eq("entry_after_decision", r.global_entry > r.global_decision, True, ctx)
        eq("exit_by1559", r.j1 <= 959, True, ctx)
        distance = cfg["stop_sigma"] * r.signal_sigma * r.signal_close
        eq("fixed_distance", r.stop_distance, distance, ctx)
        expected_stop = (np.ceil((r.raw_entry-r.side*distance)*4) if r.side == 1 else np.floor((r.raw_entry-r.side*distance)*4))/4 if cfg["stop_sigma"] else np.nan
        eq("raw_anchored_stop", r.stop, expected_stop, ctx)
        signal = feature_lookup[(int(r.decision_day), int(r.decision_j))]
        eq("entry_decision_is_registered_check", int(r.decision_j) in replay.CHECKS, True, ctx)
        eq("entry_signal_side", r.side, signal.signal_side, ctx)
        eq("entry_signal_sigma", r.signal_sigma, signal.sigma, ctx)
        eq("entry_signal_close", r.signal_close, signal.close, ctx)
        oo, hh, ll, cc = (getattr(g, key)[int(r.day)] for key in "ohlc")
        native = np.isfinite(np.stack([oo, hh, ll, cc])).all(0)
        fills = np.flatnonzero(native & (np.arange(1440) > int(r.decision_j)))
        eq("entry_first_next_native_open", r.j0, fills[0] if len(fills) else np.nan, ctx)
        held = np.arange(int(r.j0), int(r.j1) + (r.exit_phase != "open"))
        eq("unknown_held_count", r.unknown_held_minutes, int((~native[held]).sum()), ctx)
        if cfg["stop_sigma"]:
            # Independent vector scan of the entire held interval: no shared
            # grid._walk call and no future bar after the executable market exit.
            scan_end = int(r.j1) + int(r.kind == 0)
            scan = np.arange(int(r.j0), scan_end)
            adverse = ll[scan] <= expected_stop if r.side == 1 else hh[scan] >= expected_stop
            hits = scan[native[scan] & adverse]
            if len(hits):
                first = int(hits[0])
                opening = first > int(r.j0) and (oo[first] <= expected_stop if r.side == 1 else oo[first] >= expected_stop)
                px = oo[first] if opening else expected_stop
                eq("first_fixed_stop_exit_kind", int(r.kind), 0, ctx)
                eq("first_fixed_stop_exit_minute", r.j1, first, ctx)
                eq("first_fixed_stop_exit_price", r.raw_exit, px, ctx)
            else:
                eq("no_untriggered_stop_exit", int(r.kind) != 0, True, ctx)
            if r.kind != 0 and r.exit_phase == "open":
                gap = oo[int(r.j1)] <= expected_stop if r.side == 1 else oo[int(r.j1)] >= expected_stop
                eq("market_exit_has_no_priority_gap_stop", bool(gap), False, ctx)
        if r.exit_phase == "open":
            eq("open_exit_native_price", r.raw_exit, g.o[int(r.exit_day), int(r.j1)], ctx)
            later = np.flatnonzero(native & (np.arange(1440) > int(r.exit_decision_j)))
            eq("market_exit_first_next_native_open", r.j1, later[0] if len(later) else np.nan, ctx)
        elif r.kind == 0:
            eq("intrabar_stop_price", r.raw_exit, expected_stop, ctx)
    common = trades.sort_values(["global_entry", "global_exit"]) if len(trades) else trades
    if len(common) > 1:
        overlap = common.global_entry.to_numpy()[1:] < common.global_exit.to_numpy()[:-1]
        if overlap.any():
            failures.append(dict(check="one_position_no_overlap", trades=np.flatnonzero(overlap).tolist()))
    blockers = dict(censored=len(trades.attrs.get("censored", [])),
                    unknown_held_minutes=len(trades.attrs.get("unknown_held_minutes", [])),
                    unmatched_orders=len(trades.attrs.get("unmatched_orders", [])),
                    delayed_orders=len(trades.attrs.get("delayed_orders", [])))
    day_audit = trades.attrs.get("day_audit", pd.DataFrame())
    no_data = []
    if len(day_audit) and "no_cash_data" in day_audit:
        absent = (day_audit.calendar_kind == "normal") & day_audit.no_cash_data.astype(bool)
        no_data = [str(pd.Timestamp(d).date()) for d in day_audit.loc[absent,"date"]]
    blockers["normal_dates_without_cash_data"] = no_data
    result = dict(profile=profile, passed=not failures, comparisons=comparisons,
                  features_checked=len(features), trades_checked=len(trades), failures=failures,
                  account_blockers=blockers, source_exact_parity=False, tick_validation=False,
                  has_some_observed_cash_data_on_each_normal_date=not no_data,
                  cash_data_presence_definition="Every predetermined normal date has at least one observed valid OHLCV minute from selected anchor through15:00. This does not assert full minute or scheduled-decision coverage and does not clear the account gate.",
                  observed_path_completeness_is_not_full_calendar_proof=True,
                  checker="Separate raw-array feature reconstruction and direct trade arithmetic; own synthetic execution fixtures")
    if output:
        Path(output).mkdir(parents=True, exist_ok=True)
        _dump(Path(output) / f"independent_{profile}_audit.json", result)
    if failures:
        raise AssertionError(f"{profile} independent audit failed ({len(failures)}): {failures[:3]}")
    return result


def daily_net(trades, dates):
    """Final slipped trade net, including zero cash dates, with exact reconciliation."""
    dates = pd.DatetimeIndex(dates).normalize()
    trades = pd.DataFrame(trades)  # pandas concat cannot compare DataFrame-valued attrs
    daily = trades.groupby(pd.to_datetime(trades.exit_date).dt.normalize()).net.sum() if len(trades) else pd.Series(dtype=float)
    daily = daily.reindex(dates, fill_value=0.).astype(float)
    if not np.isclose(daily.sum(), trades.net.sum(), rtol=0, atol=1e-6):
        raise AssertionError("trade net escaped supplied full daily calendar")
    return daily


def paired_stop_comparison(v2, v1, daily_v2, daily_v1, *, output=None, n=3000, block=20, seed=SEED):
    """Paired whole-calendar bootstrap of the full exit intervention and reentries."""
    v2, v1 = pd.DataFrame(v2), pd.DataFrame(v1)
    a, b = pd.Series(daily_v2, dtype=float).align(pd.Series(daily_v1, dtype=float), join="outer", fill_value=0.)
    x, y = a.to_numpy(), b.to_numpy()
    if len(x) < block:
        raise ValueError("paired bootstrap needs at least one complete20-session block")
    rng = np.random.default_rng(seed)
    chunks = {k: [] for k in ("net_change", "sharpe_change", "max_dd_reduction")}
    for start in range(0, n, 250):
        m = min(250, n-start)
        starts = rng.integers(0, len(x)-block+1, (m, int(np.ceil(len(x)/block))))
        idx = (starts[:, :, None]+np.arange(block)).reshape(m,-1)[:, :len(x)]
        sx, sy = _stats(x[idx], 50000.), _stats(y[idx], 50000.)
        chunks["net_change"].append((x[idx]-y[idx]).sum(1))
        chunks["sharpe_change"].append(sx["sharpe"]-sy["sharpe"])
        chunks["max_dd_reduction"].append(sy["max_dd"]-sx["max_dd"])
    actual_a, actual_b = _stats(x[None],50000.), _stats(y[None],50000.)
    actual = dict(net_change=float((x-y).sum()), sharpe_change=float(actual_a["sharpe"][0]-actual_b["sharpe"][0]),
                  max_dd_reduction=float(actual_b["max_dd"][0]-actual_a["max_dd"][0]))
    rows = []
    for k, values in chunks.items():
        z = np.concatenate(values)
        rows.append(dict(metric=k, actual=actual[k], p5=float(np.nanpercentile(z,5)),
                         p50=float(np.nanpercentile(z,50)), p95=float(np.nanpercentile(z,95))))
    ci = pd.DataFrame(rows).set_index("metric")
    key = ["global_decision", "side"]
    if v2.duplicated(key).any() or v1.duplicated(key).any():
        raise AssertionError("ambiguous repeated decision/side trade mapping")
    cols = key + ["net", "global_entry", "global_exit", "why"]
    match = v2[cols].merge(v1[cols], on=key, how="outer", suffixes=("_V2","_V1"), indicator=True)
    common = match._merge == "both"
    extra = match._merge == "left_only"
    missing = match._merge == "right_only"
    match["net_delta"] = match.net_V2.fillna(0.)-match.net_V1.fillna(0.)
    summary = dict(bootstrap_draws=n, block=block, seed=seed, interval="90% paired moving20-session blocks; zero dates included",
        common_entries=int(common.sum()), added_reentries_V2=int(extra.sum()), missing_entries_V2=int(missing.sum()),
        common_entry_net_delta=float(match.loc[common,"net_delta"].sum()), added_reentries_net=float(match.loc[extra,"net_V2"].sum()),
        missing_V1_entry_net=float(match.loc[missing,"net_V1"].sum()), total_net_delta=float(match.net_delta.sum()),
        V2_stop_count=int((v2.kind == 0).sum()), V2_stop_trade_net=float(v2.loc[v2.kind == 0,"net"].sum()),
        stop_gain_attribution="Matched entry net changes plus added/missing entries; stop-trade PnL alone is not causal stop gain",
        improves=bool(actual["max_dd_reduction"] > 0 and actual["net_change"] > 0 and
                      (ci.loc["net_change","p5"] > 0 or ci.loc["sharpe_change","p5"] > 0)))
    denominator = actual["net_change"]
    for k in ("common_entry_net_delta", "added_reentries_net"):
        summary[k+"_share_of_gain"] = summary[k]/denominator if denominator else np.nan
    summary["missing_V1_entry_contribution_share_of_gain"] = -summary["missing_V1_entry_net"]/denominator if denominator else np.nan
    if not np.isclose(summary["total_net_delta"], actual["net_change"], rtol=0, atol=1e-6):
        raise AssertionError("matched trade intervention differs from paired daily net")
    if output:
        Path(output).mkdir(parents=True, exist_ok=True)
        ci.to_csv(Path(output)/"paired_stop_bootstrap.csv")
        match.to_csv(Path(output)/"common_entry_stop_mapping.csv",index=False)
        _dump(Path(output)/"paired_stop_summary.json",summary)
    return ci, summary, match


def tail_diagnostics(trades, output=None, profile="V2"):
    trades = pd.DataFrame(trades)
    total = float(trades.net.sum())
    best = trades.nlargest(min(25,len(trades)),"net").copy()
    result = dict(profile=profile, total_net=total,
        top_shares={str(k): float(trades.nlargest(min(k,len(trades)),"net").net.sum()/total) if total else np.nan for k in (1,10,25)},
        diagnostic_only=True, deletion_rule_selected=False)
    if output:
        Path(output).mkdir(parents=True, exist_ok=True)
        best.to_csv(Path(output)/f"{profile}_largest25_winners.csv",index=False)
        trades.nsmallest(min(25,len(trades)),"net").to_csv(Path(output)/f"{profile}_largest25_losses.csv",index=False)
        trades.assign(year=pd.to_datetime(trades.date).dt.year).groupby(["year","side"]).net.agg(["count","sum","mean"]).to_csv(Path(output)/f"{profile}_year_side.csv")
        _dump(Path(output)/f"{profile}_tail_concentration.json",result)
    return result


def null_proposals(features, family, seed):
    """Return one raw proposal vector; all occupancy is left to full replay."""
    if family not in ("side", "time"):
        raise ValueError("null family must be side or time")
    f = features.reset_index(drop=True)
    eligible = f.entry_eligible.to_numpy(dtype=bool)
    source = f.signal_side.to_numpy(dtype=np.int64)
    source = np.where(eligible, source, 0)
    out = np.zeros(len(f), dtype=np.int64)
    rng = np.random.default_rng(int(seed))
    if family == "side":
        proposed = np.flatnonzero(source)
        out[proposed] = rng.choice(np.array([-1,1]), len(proposed))
    else:
        for _, q in f.loc[eligible].groupby("date",sort=True):
            idx = q.index.to_numpy()
            out[idx] = rng.permutation(source[idx])
    rows = []
    for date, q in f.loc[eligible].groupby("date",sort=True):
        idx = q.index.to_numpy()
        rows.append(dict(date=date, eligible_checks=len(idx), raw_proposals=int(np.count_nonzero(source[idx])),
                         null_proposals=int(np.count_nonzero(out[idx]))))
    return out, pd.DataFrame(rows)


def run_nulls(g, features, dates, observed, *, years=(2018,2022), allow_post2022=False,
              output=None, n=100, progress=None, families=("side","time"), seed_start=0):
    """Full state replay of100 fixed side and100 fixed same-date time nulls.

    No filled-count matching, stop optimization or occupancy feasibility
    selection. Standard costs/exits/stops remain unchanged. ``seed_start``
    permits deterministic batches;100 seeds are offsets0..99 exactly.
    """
    f = features.reset_index(drop=True).copy()
    if "entry_eligible" not in f:
        in_period = pd.to_datetime(f.date).dt.year.between(*years)
        f["entry_eligible"] = in_period & f.feature_ready & f.timing_ok
    observed_daily = daily_net(observed, dates)
    real = perf(observed_daily, observed.net)
    real["net"] = float(observed.net.sum())
    results = []
    for family in families:
        for offset in range(seed_start,seed_start+n):
            seed = (SIDE_SEED if family == "side" else TIME_SEED) + offset
            proposals, counts = null_proposals(f,family,seed)
            begin = time.monotonic()
            t, _ = replay.run(g,years=years,stop_sigma=.4,anchor=831,slip_ticks=1.,
                              allow_post2022=allow_post2022,features=f,
                              signal_override=proposals,record_orders=False)
            d = daily_net(t,dates)
            row = perf(d,t.net)
            row.update(family=family,seed=seed,offset=offset,net=float(t.net.sum()),
                raw_proposals=int(counts.raw_proposals.sum()), null_proposals=int(counts.null_proposals.sum()),
                filled_count=int(len(t)), observed_filled_count=len(observed),
                execution_complete=bool(t.attrs["execution_complete"]),
                unknown_held_minutes=len(t.attrs.get("unknown_held_minutes",[])),
                censored=len(t.attrs.get("censored",[])),
                unmatched=len(t.attrs.get("unmatched_orders",[])), seconds=time.monotonic()-begin)
            results.append(row)
            if progress:
                progress(f"{family} null {offset+1}/100 seed={seed}, filled={len(t)}, elapsed={row['seconds']:.1f}s")
    table = pd.DataFrame(results)
    summary = {}
    for family, q in table.groupby("family"):
        summary[family] = dict(draws=len(q), seed_first=int(q.seed.min()),seed_last=int(q.seed.max()),
            actual_net=real["net"],actual_sharpe=real["sharpe"],actual_max_dd=real["max_dd"],
            p_net_ge_actual=float((1+(q.net >= real["net"]).sum())/(len(q)+1)),
            p_sharpe_ge_actual=float((1+(q.sharpe >= real["sharpe"]).sum())/(len(q)+1)),
            p_drawdown_le_actual=float((1+(q.max_dd <= real["max_dd"]).sum())/(len(q)+1)),
            null_net_p5=float(q.net.quantile(.05)),null_net_median=float(q.net.median()),null_net_p95=float(q.net.quantile(.95)),
            filled_count_min=int(q.filled_count.min()),filled_count_median=float(q.filled_count.median()),filled_count_max=int(q.filled_count.max()),
            source_proposal_count=int(q.raw_proposals.iloc[0]),actual_filled_count=len(observed),
            complete_paths=int(q.execution_complete.sum()),
            null_streams_with_unknown_held_minutes=int((q.unknown_held_minutes > 0).sum()),
            null_unknown_held_minutes_total=int(q.unknown_held_minutes.sum()),
            null_streams_with_censoring=int((q.censored > 0).sum()),
            observed_unknown_held_minutes=int(observed.unknown_held_minutes.sum()),
            observed_censored_positions=len(observed.attrs.get("censored",[])),
            observed_held_order_paths_complete=bool(q.execution_complete.all() and observed.attrs.get("execution_complete",not observed.unknown_held_minutes.sum())),
            data_hole_policy="All null outcomes retained; no gap day excluded or filled. Closed-ledger p-values remain descriptive when observed/null held paths contain unknown prices or censored positions.",
            conditioning="Raw proposals and their same-calendar active dates conditioned on observed price signals; no future occupancy or filled-count conditioning",
            execution="Full replay.run for each null; unchanged fixed stop, band/VWAP check exits, reversal, flatten and final costs")
    for family in summary:
        summary[family].update(null_comparator_metadata(family))
    if output:
        Path(output).mkdir(parents=True, exist_ok=True)
        name = "nulls" if seed_start == 0 and n == 100 else f"nulls_{seed_start}_{seed_start+n-1}"
        table.to_csv(Path(output)/(name+".csv"),index=False)
        _dump(Path(output)/(name+"_summary.json"),summary)
    return table,summary



def annotate_null_path_coverage(summary, table, observed):
    """Expose holes in every saved null stream without excluding outcomes."""
    for family,q in table.groupby("family"):
        summary[family].pop("full_path_comparison_valid", None)
        summary[family].update(null_comparator_metadata(family))
        summary[family].update(
            null_streams_with_unknown_held_minutes=int((q.unknown_held_minutes > 0).sum()),
            null_unknown_held_minutes_total=int(q.unknown_held_minutes.sum()),
            null_streams_with_censoring=int((q.censored > 0).sum()),
            observed_unknown_held_minutes=int(observed.unknown_held_minutes.sum()),
            observed_censored_positions=len(observed.attrs.get("censored",[])),
            observed_held_order_paths_complete=bool(q.execution_complete.all() and observed.attrs.get("execution_complete",not observed.unknown_held_minutes.sum())),
            data_hole_policy="All null outcomes retained; no gap day excluded or filled. Closed-ledger p-values remain descriptive when observed/null held paths contain unknown prices or censored positions.")
    return summary

def recent_resampling(daily, trades=None, *, output=None, label=None):
    """Registered recent bootstrap/permutation including native zero dates."""
    b = bootstrap(daily,n=3000,block=20,seed=SEED)
    p = permutation(daily,n=3000,seed=SEED)
    b.loc["net",:] = b.loc["annual",:] * (len(daily)/252.)
    if trades is not None:
        # Resample full dates and their individual winning/losing trade totals,
        # rather than labelling the profit factor of net days as trade PF.
        t = pd.DataFrame(trades)
        day = pd.to_datetime(t.exit_date).dt.normalize()
        gp = t.net.clip(lower=0).groupby(day).sum().reindex(daily.index,fill_value=0.).to_numpy()
        gl = (-t.net.clip(upper=0)).groupby(day).sum().reindex(daily.index,fill_value=0.).to_numpy()
        rng = np.random.default_rng(SEED)
        values = []
        for start in range(0,3000,250):
            m = min(250,3000-start)
            starts = rng.integers(0,len(daily)-20+1,(m,int(np.ceil(len(daily)/20))))
            idx = (starts[:,:,None]+np.arange(20)).reshape(m,-1)[:,:len(daily)]
            with np.errstate(divide="ignore",invalid="ignore"):
                values.append(gp[idx].sum(1)/gl[idx].sum(1))
        q = np.concatenate(values)
        actual = gp.sum()/gl.sum() if gl.sum() else np.inf
        b.loc["profit_factor_trade",:] = [actual,*np.nanpercentile(q,[5,50,95])]
    if output:
        Path(output).mkdir(parents=True,exist_ok=True)
        prefix = f"recent_{label}" if label else "recent"
        b.to_csv(Path(output)/f"{prefix}_bootstrap.csv")
        p.update(bootstrap_draws=3000, bootstrap_block=20, seed=SEED,
                 zero_dates_included=True, bootstrap_probability_sharpe_le_0=b.attrs.get("p_sharpe_le_0"))
        _dump(Path(output)/f"{prefix}_permutation.json",p)
    return b,p



def run_saved_stage(stage, *, prereg_commit, gate_file=None,
                    output_root=ROOT/"analysis/outputs/codex_s03_noisearea",
                    cache=ROOT/"scratch_data/g24.pkl", nulls=False, progress=print):
    """Reproduce diagnostics from root-gated saved profiles and native grid."""
    import pickle
    try:
        from codex_s03_run import PREREG_COMMIT, PLAN_SHA256
    except ImportError:
        from analysis.codex_s03_run import PREREG_COMMIT, PLAN_SHA256
    if prereg_commit != PREREG_COMMIT:
        raise ValueError("diagnostics preregistration differs from published root")
    if _digest(ROOT/"agents/codex/plans/s03_noisearea.md") != PLAN_SHA256:
        raise ValueError("frozen preregistration plan differs")
    if stage not in ("design","recent"):
        raise ValueError("stage must be design or recent")
    output_root=Path(output_root)
    if stage == "recent":
        if gate_file is None:
            raise ValueError("recent diagnostics require saved root design PASS")
        gate=json.loads(Path(gate_file).read_text())
        if gate.get("passed") is not True or gate.get("prereg_commit",gate.get("prereg_sha")) != PREREG_COMMIT:
            raise ValueError("recent diagnostics require matching explicit passing root gate")
    manifest=json.loads((output_root/f"{stage}_manifest.json").read_text())
    if manifest["prereg_commit"] != PREREG_COMMIT:
        raise ValueError("saved profile manifest has wrong preregistration")
    if _digest(cache) != manifest["cache_sha256"]:
        raise ValueError("native cache hash differs from saved root replay")
    # Opening the owned cache does not construct any features beyond this stage.
    # All audit loops are bounded by saved feature max day / frozen stage dates.
    with Path(cache).open("rb") as stream:
        g=pickle.load(stream)
    years=tuple(manifest["years"])
    dates=pd.DatetimeIndex(g.ts[np.asarray(g.trading)]).normalize()
    dates=dates[(dates.year >= years[0]) & (dates.year <= years[1])]
    output=output_root/f"diagnostics_{stage}"
    output.mkdir(parents=True,exist_ok=True)
    source_execution_audit(output)
    independent_synthetic_checks(output)
    primary=pd.read_pickle(output_root/f"{stage}_features.pkl")
    alternate=pd.read_pickle(output_root/f"{stage}_C2_features.pkl")
    ledgers={}
    audits={}
    for profile in PROFILES:
        prefix=f"{stage}_{profile}"
        ledger=output_root/f"{prefix}.csv"
        audit=json.loads((output_root/f"{prefix}_audit.json").read_text())
        if _digest(ledger) != audit["ledger_sha256"]:
            raise ValueError(f"{profile} saved ledger hash differs")
        t=pd.read_csv(ledger,parse_dates=["date","entry_date","exit_date","decision_date"])
        attrs=dict(audit["replay_attrs"])
        if audit["prereg_commit"] != PREREG_COMMIT or audit["parameters"] != PROFILES[profile]:
            raise ValueError(f"{profile} metadata differs from frozen rule")
        for key, info in attrs.pop("audit_tables").items():
            path=Path(info["path"])
            if not path.is_absolute():
                path=ROOT/path
            if _digest(path) != info["sha256"]:
                raise ValueError(f"{profile} {key} audit hash differs")
            attrs[key]=json.loads(path.read_text()) if key == "censored" else pd.read_csv(path)
        t.attrs.update(attrs)
        ledgers[profile]=t
        audits[profile]=audit_replay(g,t,alternate if profile == "C2" else primary,profile=profile,output=output)
        tail_diagnostics(t,output,profile)
        if progress:
            progress(f"{stage} {profile} independent audit PASS ({audits[profile]['comparisons']} checks)")
    daily={k:daily_net(t,dates) for k,t in ledgers.items()}
    _, paired, _=paired_stop_comparison(ledgers["V2"],ledgers["V1"],daily["V2"],daily["V1"],output=output)
    if stage == "recent":
        recent_resampling(daily["V2"],ledgers["V2"],output=output)
        for side, label in ((1,"long"),(-1,"short")):
            selected = pd.DataFrame(ledgers["V2"])
            selected = selected.loc[selected.side == side]
            recent_resampling(daily_net(selected,dates),selected,output=output,label=label)
    null_summary=None
    prior_null_summary=output/"nulls_summary.json"
    if prior_null_summary.exists():
        null_summary=json.loads(prior_null_summary.read_text())
        prior_nulls=output/"nulls.csv"
        if prior_nulls.exists():
            annotate_null_path_coverage(null_summary,pd.read_csv(prior_nulls),ledgers["V2"])
            _dump(prior_null_summary,null_summary)
    if nulls:
        _,null_summary=run_nulls(g,primary,dates,ledgers["V2"],years=years,
            allow_post2022=stage=="recent",output=output,progress=progress)
    summary=dict(stage=stage,prereg_commit=PREREG_COMMIT,plan_sha256=PLAN_SHA256,
                 manifest_sha256=_digest(output_root/f"{stage}_manifest.json"),
                 checker_sha256=_digest(__file__),all_independent_audits_passed=all(q["passed"] for q in audits.values()),
                 observed_held_order_paths_complete=all(t.attrs["execution_complete"] for t in ledgers.values()),
                 has_some_observed_cash_data_on_each_normal_date=all(q["has_some_observed_cash_data_on_each_normal_date"] for q in audits.values()),
                 cash_data_presence_definition="Every predetermined normal date has at least one observed valid OHLCV minute from selected anchor through15:00. This does not assert full minute or scheduled-decision coverage and does not clear the account gate.",
                 entirely_unobserved_normal_cash_dates={k:q["account_blockers"]["normal_dates_without_cash_data"] for k,q in audits.items()},
                 account_gate_authorized=False,
                 implementation_review="PASS", source_tick_data_causal_timing_review="WITH_CONCERNS",
                 clean_causal_entry_timing_test="OPEN",
                 independent_review_path="agents/codex/results/s03_noisearea_independent_review.md",
                 independent_review_sha256=_digest(ROOT/"agents/codex/results/s03_noisearea_independent_review.md"),
                 audit_comparisons={k:v["comparisons"] for k,v in audits.items()},paired_stop=paired,nulls=null_summary)
    _dump(output/"diagnostics_summary.json",summary)
    return summary


if __name__ == "__main__":
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--synthetic",action="store_true")
    mode.add_argument("--stage",choices=("design","recent"))
    parser.add_argument("--prereg-commit")
    parser.add_argument("--gate-file",type=Path)
    parser.add_argument("--nulls",action="store_true")
    parser.add_argument("--output-root",type=Path,default=ROOT/"analysis/outputs/codex_s03_noisearea")
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    if args.synthetic:
        target=args.output or args.output_root/"diagnostics_design"
        source_execution_audit(target)
        print(json.dumps(independent_synthetic_checks(target),indent=2))
    else:
        if not args.prereg_commit:
            parser.error("--stage requires --prereg-commit")
        print(json.dumps(run_saved_stage(args.stage,prereg_commit=args.prereg_commit,
            gate_file=args.gate_file,output_root=args.output_root,nulls=args.nulls),indent=2,default=str))
