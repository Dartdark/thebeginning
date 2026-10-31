"""H09 native MES execution on admitted CT minute arrays, source/synthetic only.

Caller owns frozen parent/source/count/gross admission. Import opens no data.
Shared execute is cloned with private globals; shared _walk uses the ORIGINAL
raw path. Only the cloned entry OPEN is adverse-filled to anchor the stop.
An entry already through that stop exits at the worse RAW entry OPEN. Native
net is direct executed cashflow, not ES net /10 or a second slippage charge.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
from numbers import Real
import os
from pathlib import Path
import sys
from types import FunctionType, SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_hunt_v2_mes_affordability"
CACHE = OUT / "cache/numba"
sys.dont_write_bytecode = True
os.environ["NUMBA_CACHE_DIR"] = str(CACHE)
sys.path.insert(0, str(ROOT / "analysis"))
import numpy as np
import pandas as pd
import grid as shared_grid

DECISION_J, ENTRY_J, EXIT_J = 890, 891, 900
POINT_VALUE, COMMISSION_RT, TICK = 5.0, 1.24, .25
PRIMARY_RT_COST = COMMISSION_RT + 2 * TICK * POINT_VALUE
_SHARED_WALK = getattr(shared_grid._walk, "py_func", shared_grid._walk)


def stop_distance(atr, *, atr_exact=None):
    """Conservative native .25-point ceiling of .25 times admitted parent ATR."""
    value = float(atr)
    if not math.isfinite(value) or value <= 0: raise ValueError("ATR must be finite positive.")
    exact = Fraction(atr_exact) if atr_exact is not None else Fraction(str(atr))
    if exact <= 0 or not math.isclose(float(exact), value, rel_tol=0, abs_tol=1e-10):
        raise ValueError("Exact and display ATR must identify the same parent reference.")
    # (.25*ATR)/native_tick equals ATR. Use the parent's exact rational when
    # supplied; never let a rounded float choose a different native ceiling.
    return float(math.ceil(exact) * Fraction(1, 4))


def _integer(value, name):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real) or not math.isfinite(float(value)) or int(value) != value:
        raise ValueError(name + " must be an exact numeric integer.")
    return int(value)


def _tick_prices(values):
    values = np.asarray(values, dtype=float)
    return np.isfinite(values) & (values > 0) & np.isclose(values / TICK, np.rint(values / TICK), rtol=0, atol=1e-8)


def _admitted_signals(grid, signals, slippage_ticks):
    ticks = _integer(slippage_ticks, "slippage_ticks")
    if ticks not in (1, 4): raise ValueError("Only primary1tick or fixed4tick stress is registered.")
    required = ("day", "dj", "side", "atr", "stop_points", "exit_j")
    if any(name not in signals for name in required): raise ValueError("Signals require:" + ",".join(required))
    arrays = {name: np.asarray(getattr(grid, name)) for name in ("o", "h", "l", "c", "v")}
    shape = arrays["o"].shape
    if len(shape) != 2 or shape[1] != 1440 or any(a.shape != shape for a in arrays.values()):
        raise ValueError("Exact common CT close-label day-by1440 native grid required.")
    if len(grid.ts) != shape[0] or len(grid.last_j) != shape[0]: raise ValueError("Grid date/last-bar axis differs.")
    prepared, seen_days, seen_dates = [], set(), set()
    for original in signals.to_dict("records"):
        row = dict(original)
        day, dj, side, exit_j = (_integer(row[name], name) for name in ("day", "dj", "side", "exit_j"))
        qty = _integer(row.get("qty", 1), "qty")
        if not (0 <= day < shape[0]) or side not in (-1, 1) or qty not in (1, 2):
            raise ValueError("Only one/two whole MES on a valid row/side is supported.")
        if (dj, exit_j) != (DECISION_J, EXIT_J): raise ValueError("Frozen decision/entry/exit clock changed.")
        if not EXIT_J <= _integer(grid.last_j[day], "last_j") < 1440:
            raise ValueError("Reported native coverage ends before exact C900.")
        native_date = pd.Timestamp(grid.ts[day])
        if pd.isna(native_date) or native_date.tzinfo is not None or native_date != native_date.normalize():
            raise ValueError("Exact unzoned native calendar date required.")
        if day in seen_days or native_date in seen_dates: raise ValueError("One consumed parent decision per native date.")
        seen_days.add(day); seen_dates.add(native_date)
        if "date" in row and pd.Timestamp(row["date"]) != native_date: raise ValueError("Signal/native date mismatch.")
        if "entry_label_j" in row and _integer(row["entry_label_j"], "entry_label_j") != ENTRY_J:
            raise ValueError("Parent entry label is not891.")
        distance = stop_distance(row["atr"], atr_exact=row.get("atr_exact"))
        supplied = float(row["stop_points"])
        if not math.isfinite(supplied) or abs(supplied - distance) > 1e-10:
            raise ValueError("Stop must be exactly the frozen native-ceiled quarter ATR.")
        if "stop_points_exact" in row and Fraction(row["stop_points_exact"]) != Fraction(str(distance)):
            raise ValueError("Parent exact stop-distance identity differs.")
        if "stop" in row and float(row["stop"]) != supplied: raise ValueError("Conflicting stop aliases.")
        if "target" in row and not np.isposinf(float(row["target"])): raise ValueError("No target is registered.")
        # Exact raw endpoint/path; shared last-close fallback and NaN skipping
        # cannot repair an unadmitted held minute or missing C900.
        o, h, l, c, v = (arrays[name][day, ENTRY_J:EXIT_J + 1] for name in ("o", "h", "l", "c", "v"))
        price_valid = np.logical_and.reduce([_tick_prices(a) for a in (o, h, l, c)])
        valid = price_valid & np.isfinite(v) & (v >= 0) & (l <= np.minimum(o, c)) & (h >= np.maximum(o, c)) & (l <= h)
        if not valid.all(): raise ValueError("Every exact entry/held/time minute must be valid; no fallback.")
        if not _tick_prices([arrays["c"][day, DECISION_J]]).all(): raise ValueError("Exact completed C890 decision quote missing.")
        raw_entry = float(arrays["o"][day, ENTRY_J])
        executed_entry = raw_entry + side * ticks * TICK
        anchor = executed_entry - side * distance
        if not _tick_prices([executed_entry, anchor]).all(): raise ValueError("Executed entry/stop is invalid on native grid.")
        row.update(day=day, dj=dj, side=side, exit_j=exit_j, qty=qty, date=native_date,
            stop_points=distance, entry_j=ENTRY_J, raw_entry_quote=raw_entry,
            executed_entry=executed_entry, stop_price=anchor, slippage_ticks=ticks)
        prepared.append(row)
    return arrays, prepared


def _private_execute(raw, calls):
    """One ticket's private entry array; all stop walks inspect raw quotes."""
    def guarded_walk(o, h, l, c, j0, jend, side, stop_px, tgt_px, fill_through):
        if (j0, jend) != (ENTRY_J, EXIT_J): raise ValueError("Shared engine changed the frozen interval.")
        expected_target = np.inf if side > 0 else -np.inf
        if tgt_px != expected_target: raise ValueError("Unexpected target; target-through is inapplicable.")
        raw_open = float(raw["o"][j0])
        through_at_entry = raw_open <= stop_px if side > 0 else raw_open >= stop_px
        # Shared _walk omits its gap test at j0. Compute its unchanged result
        # then override only this explicitly known entry-through case.
        original = _SHARED_WALK(raw["o"], raw["h"], raw["l"], raw["c"], j0, jend,
            side, stop_px, tgt_px, fill_through)
        result = (j0, raw_open, 0, raw_open) if through_at_entry else original
        exit_j, raw_exit, kind, worst = result
        if kind not in (0, 2) or (kind == 2 and exit_j != EXIT_J): raise ValueError("Unexpected target/fallback exit.")
        if through_at_entry and kind != 0: raise ValueError("Entry-through protection must be active.")
        raw_exit_open = float(raw["o"][exit_j])
        later_gap = bool(kind == 0 and exit_j > j0 and (raw_exit_open <= stop_px if side > 0 else raw_exit_open >= stop_px))
        calls.append(dict(raw_entry_open=raw_open, private_engine_entry_open=float(o[j0]), stop_price=float(stop_px),
            entry_already_through_stop=bool(through_at_entry), entry_raw_open_override=bool(through_at_entry),
            later_open_gap_stop=later_gap, shared_result_exit_j=int(original[0]), shared_result_exit=float(original[1]),
            shared_result_kind=int(original[2]), adapter_exit_j=int(exit_j), adapter_raw_exit=float(raw_exit),
            adapter_kind=int(kind), raw_worst_price=float(worst), shared_walk_calls=1,
            original_raw_path_used=True, compiled_numba_path_used=False))
        return result
    private_globals = dict(shared_grid.execute.__globals__)
    private_globals.update(_walk=guarded_walk, POINT_VALUE=POINT_VALUE, COST=COMMISSION_RT)
    return FunctionType(shared_grid.execute.__code__, private_globals,
        name="H09_private_shared_execute", argdefs=shared_grid.execute.__defaults__, closure=shared_grid.execute.__closure__)


def execute_mes(grid, signals, *, slippage_ticks=1):
    """Return native per-contract/total trade ledger and local execution audit.

    Signals: day,dj=890,side,atr,stop_points,exit_j=900; optional qty is1or2.
    Other parent metadata are retained. Caller first admits source/calendar/
    support and exact date-row mapping. This function never reads input files.
    Costs and net_mes are per contract; *_total_mes includes integer qty.
    Fixed4tick stress changes fills/stop anchoring and must be an explicitly
    counted unselectable definition, never a replacement chosen from outcomes.
    """
    arrays, prepared = _admitted_signals(grid, signals, slippage_ticks)
    records, audits = [], []
    for row in prepared:
        day, side, qty = row["day"], row["side"], row["qty"]
        raw = {name: np.array(arrays[name][day], dtype=float, copy=True) for name in ("o", "h", "l", "c")}
        executed_open = raw["o"].copy(); executed_open[ENTRY_J] = row["executed_entry"]
        private_grid = SimpleNamespace(o=executed_open[None, :], h=raw["h"][None, :],
            l=raw["l"][None, :], c=raw["c"][None, :], ts=np.array([grid.ts[day]]), last_j=np.array([EXIT_J]))
        native_signal = pd.DataFrame([dict(day=0, dj=DECISION_J, side=side, stop=row["stop_points"], target=np.inf, exit_j=EXIT_J, qty=qty)])
        calls = []
        result = _private_execute(raw, calls)(private_grid, native_signal, max_trades=1, max_losses=1, name="H09_MES")
        if len(result) != 1 or len(calls) != 1: raise ValueError("Shared engine suppressed an admitted parent ticket.")
        engine = result.iloc[0]
        if int(engine.j0) != ENTRY_J or engine.entry != row["executed_entry"] or int(engine.side) != side:
            raise ValueError("Shared private entry identity changed.")
        call = calls[0]; exit_j, kind = int(engine.j1), int(engine.kind)
        raw_exit = float(engine.exit); slip_points = row["slippage_ticks"] * TICK
        executed_exit = raw_exit - side * slip_points
        if not _tick_prices([executed_exit]).all(): raise ValueError("Executed exit is invalid on native grid.")
        executed_gross = (executed_exit - row["executed_entry"]) * side * POINT_VALUE
        raw_quote_gross = (raw_exit - row["raw_entry_quote"]) * side * POINT_VALUE
        fill_cost = slip_points * POINT_VALUE; costs = COMMISSION_RT + 2 * fill_cost
        native_net = executed_gross - COMMISSION_RT
        np.testing.assert_allclose(native_net, raw_quote_gross - costs, rtol=0, atol=1e-10)
        np.testing.assert_allclose(engine.pnl, (raw_exit - row["executed_entry"]) * side * POINT_VALUE * qty, rtol=0, atol=1e-10)
        np.testing.assert_allclose(engine.net, engine.pnl - COMMISSION_RT * qty, rtol=0, atol=1e-10)
        record = dict(row)
        record.update(exit_j=exit_j, kind=kind, raw_exit_quote=raw_exit, executed_exit=executed_exit,
            raw_quote_gross_mes=raw_quote_gross, executed_gross_mes=executed_gross,
            gross_mes=raw_quote_gross, commission_mes=COMMISSION_RT, entry_slippage_mes=fill_cost,
            exit_slippage_mes=fill_cost, costs_mes=costs, net_mes=native_net,
            gross_total_mes=raw_quote_gross * qty, commission_total_mes=COMMISSION_RT * qty,
            entry_slippage_total_mes=fill_cost * qty, exit_slippage_total_mes=fill_cost * qty,
            costs_total_mes=costs * qty, net_total_mes=native_net * qty,
            stop_anchored_on_executed_entry=True, entry_already_through_stop=call["entry_already_through_stop"],
            later_open_gap_stop=call["later_open_gap_stop"], time_exit_exact_C900=kind == 2,
            private_engine_pnl_before_exit_slippage_mes=float(engine.pnl),
            private_engine_net_before_exit_slippage_mes=float(engine.net),
            shared_walk_audit=call, no_ES_net_rescaling=True, original_grid_mutated=False,
            per_trade_excursion_is_not_joint_account_path=True)
        records.append(record); audits.append(dict(day=day, date=row["date"].date().isoformat(), side=side, qty=qty, **call))
    ledger = pd.DataFrame(records)
    audit = dict(input_tickets=len(prepared), output_tickets=len(records), one_consumed_decision_per_date=True,
        decision_j=DECISION_J, entry_j=ENTRY_J, time_exit_j=EXIT_J, native_point_value=POINT_VALUE,
        native_tick=TICK, commission_RT_per_contract=COMMISSION_RT, slippage_ticks=int(slippage_ticks),
        per_contract_two_fill_cost=COMMISSION_RT + 2 * int(slippage_ticks) * TICK * POINT_VALUE,
        source_grid_mutated=False, shared_globals_mutated=False, private_execute=True,
        raw_entry_open_used_for_entry_through_stop=True, exact_path_no_forwardfill_no_endpoint_fallback=True,
        target_exists=False, target_through="N/A", executed_cashflow_no_double_slippage=True,
        actual_MES_liquidity_or_historical_listing_verified=False, funded_or_joint_account_path_claim=False,
        compiled_numba_path_used=False, permitted_runtime_cache=str(CACHE), tickets=audits)
    return ledger, audit


def fixtures():
    def fixture(side=1, atr=4., qty=1):
        shape = (1, 1440)
        arrays = {name: np.full(shape, 100.) for name in ("o", "h", "l", "c")}
        grid = SimpleNamespace(**arrays, v=np.ones(shape), ts=np.array([np.datetime64("2020-01-02")]), last_j=np.array([1439]))
        signal = pd.DataFrame([dict(day=0, dj=890, side=side, atr=atr, stop_points=stop_distance(atr), exit_j=900, qty=qty, event_id="INVENTED")])
        return grid, signal
    checks = []
    assert stop_distance(4.) == 1. and stop_distance(4.1) == 1.25 and stop_distance(.1) == .25
    assert stop_distance(8.01, atr_exact="801/100") == 2.25
    assert stop_distance(8., atr_exact="8000000000000000001/1000000000000000000") == 2.25
    assert PRIMARY_RT_COST == 3.74
    checks.append("nativeceilquarterATR_and3_74RT")
    # Both sides: time cashflows charge adverse entry and exit exactly once.
    for side in (-1, 1):
        grid, sig = fixture(side)
        grid.c[0, 900] = 100. + side * .5
        grid.h[0, 900] = max(100., grid.c[0, 900]); grid.l[0, 900] = min(100., grid.c[0, 900])
        item = execute_mes(grid, sig)[0].iloc[0]
        assert item.kind == 2 and item.exit_j == 900 and item.net_mes == -1.24
        assert item.raw_quote_gross_mes == 2.5 and item.costs_mes == 3.74
        assert item.executed_gross_mes == 0.
    checks.append("bothside_time_exit_direct_cashflow_single_cost_bridge")
    for side in (-1, 1):
        grid, sig = fixture(side)
        if side > 0: grid.l[0, 891] = 99.
        else: grid.h[0, 891] = 101.
        item = execute_mes(grid, sig)[0].iloc[0]
        assert item.kind == 0 and item.exit_j == 891
        assert item.stop_price == 100. - side * .75 and abs(item.net_mes + 7.49) < 1e-10
        assert not item.entry_already_through_stop
    checks.append("bothside_active_entrybar_stop_anchors_executed_entry_no_extra_entry_charge")
    # Four-tick stress can put the raw entry already beyond the newly anchored
    # stop. Nominal stop or modified entry would be an optimistic exit.
    for side in (-1, 1):
        grid, sig = fixture(side, atr=1.)
        item = execute_mes(grid, sig, slippage_ticks=4)[0].iloc[0]
        assert item.kind == 0 and item.exit_j == 891 and item.entry_already_through_stop
        assert item.raw_exit_quote == 100. and item.executed_exit == 100. - side * 1.
        assert item.executed_entry == 100. + side * 1. and abs(item.net_mes + 11.24) < 1e-10
        assert item.raw_exit_quote != item.stop_price and item.raw_exit_quote != item.executed_entry
    checks.append("bothside_entryalreadythrough_uses_WORSE_RAW_OPEN_not_stop_or_execOPEN")
    # The fixed execution stress may change which stop is reached. It is not
    # identical-path repricing: the stop stays attached to the actual fill.
    for side in (-1, 1):
        grid, sig = fixture(side, atr=8.)
        if side > 0: grid.l[0, 891] = 98.5
        else: grid.h[0, 891] = 101.5
        primary = execute_mes(grid, sig)[0].iloc[0]
        stress = execute_mes(grid, sig, slippage_ticks=4)[0].iloc[0]
        assert primary.kind == 2 and abs(primary.net_mes + 3.74) < 1e-10
        assert stress.kind == 0 and abs(stress.net_mes + 16.24) < 1e-10
    checks.append("fourtick_full_execution_stress_can_change_exit_not_samepath_repricing")
    for side in (-1, 1):
        grid, sig = fixture(side)
        gap = 100. - side * 3.
        for name in ("o", "h", "l", "c"): getattr(grid, name)[0, 892] = gap
        item = execute_mes(grid, sig)[0].iloc[0]
        assert item.kind == 0 and item.exit_j == 892 and item.raw_exit_quote == gap and item.later_open_gap_stop
        assert abs(item.net_mes + 18.74) < 1e-10
    checks.append("bothside_later_worse_RAW_open_gaps_sharedwalk")
    grid, sig = fixture()
    grid.l[0, 900] = 99.
    item = execute_mes(grid, sig)[0].iloc[0]
    assert item.kind == 0 and item.exit_j == 900 and not item.time_exit_exact_C900
    checks.append("protection_through_final900minute_before_exact_C900_exit")
    grid, sig = fixture(qty=2)
    snapshots = {name: getattr(grid, name).copy() for name in ("o", "h", "l", "c", "v", "last_j")}
    original_globals = (shared_grid._walk, shared_grid.POINT_VALUE, shared_grid.COST)
    one = execute_mes(grid, sig.assign(qty=1))[0].iloc[0]
    two, audit = execute_mes(grid, sig); item = two.iloc[0]
    assert item.net_total_mes == 2 * one.net_mes and item.commission_total_mes == 2.48
    assert all(np.array_equal(value, getattr(grid, name), equal_nan=True) for name, value in snapshots.items())
    assert original_globals == (shared_grid._walk, shared_grid.POINT_VALUE, shared_grid.COST)
    assert audit["shared_globals_mutated"] is False and audit["funded_or_joint_account_path_claim"] is False
    checks.append("integer_quantity_nativefees_input_grid_and_shared_globals_unchanged")
    for missing in (891, 895, 900):
        grid, sig = fixture(); grid.c[0, missing] = np.nan
        try: execute_mes(grid, sig)
        except ValueError: pass
        else: raise AssertionError("Missing endpoint/held bar silently repaired")
    grid, sig = fixture(); grid.last_j[0] = 899
    try: execute_mes(grid, sig)
    except ValueError: pass
    else: raise AssertionError("Truncated last_j silently repaired")
    checks.append("missing_entry_held_or_timeclose_rejects_no_shared_fallback")
    for mutate in (lambda s: pd.concat([s, s], ignore_index=True), lambda s: s.assign(qty=.5),
                   lambda s: s.assign(dj=889), lambda s: s.assign(exit_j=899), lambda s: s.assign(stop_points=.75),
                   lambda s: s.assign(target=1.), lambda s: s.assign(qty=0)):
        grid, sig = fixture()
        try: execute_mes(grid, mutate(sig))
        except ValueError: pass
        else: raise AssertionError("Unregistered execution variant admitted")
    checks.append("one_day_whole_contract_fixedclock_stop_and_no_target_protocol")
    return dict(passed=True, checks=checks,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        actual_raw_workbook_feature_marker_or_outcome_values_read=False,
        actual_financial_study_run=False, compiled_numba_cache_created=False,
        permitted_runtime_cache=str(CACHE))


if __name__ == "__main__":
    print(json.dumps(fixtures(), allow_nan=False))
