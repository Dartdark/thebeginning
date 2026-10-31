"""H05 pure adapter around shared grid.execute; imports load no source data.

No shared file/global is mutated. A private function clone replaces only its
walker: one shared _walk.py_func call, with a declared stop-first override if
that first target bar also touches the stop. Brackets are active on entry.
The shared scan ends890; copied c890 is the native OPEN891 time endpoint.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
import hashlib
import json
import math
from pathlib import Path
import sys
from types import FunctionType, SimpleNamespace

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import grid as shared_grid

SCAN_END_J, NATIVE_TIME_EXIT_J = 890, 891
MNQ_POINT_VALUE, COMMISSION_RT, MARKET_STOP_SLIP = 2.0, 1.24, .50
TICK = Decimal("0.25")
_SHARED_WALK_PY = getattr(shared_grid._walk, "py_func", shared_grid._walk)


def _rounded_brackets(entry, atr15, side):
    price, atr = Decimal(str(entry)), Decimal(str(atr15))
    stop_raw = price - side * Decimal("0.20") * atr
    target_raw = price + side * Decimal("0.10") * atr
    stop_mode = ROUND_FLOOR if side > 0 else ROUND_CEILING
    target_mode = ROUND_CEILING if side > 0 else ROUND_FLOOR
    stop = (stop_raw / TICK).to_integral_value(rounding=stop_mode) * TICK
    target = (target_raw / TICK).to_integral_value(rounding=target_mode) * TICK
    return float(stop), float(target)


def _private_execute(audit):
    def conservative_walk(o, h, l, c, j0, jend, side, stop_px, tgt_px, fill_through):
        if fill_through != 1.0:
            raise ValueError("Frozen H05 target-through must equal1NQpoint.")
        result = _SHARED_WALK_PY(o, h, l, c, j0, jend, side, stop_px, tgt_px, fill_through)
        exit_j, px, kind, worst = result
        stop_hit = math.isfinite(stop_px) and (l[exit_j] <= stop_px if side > 0 else h[exit_j] >= stop_px)
        override = kind == 1 and stop_hit
        if override:
            prior_worst = o[j0]
            for j in range(j0, exit_j):
                if not np.isnan(o[j]):
                    prior_worst = min(prior_worst, l[j]) if side > 0 else max(prior_worst, h[j])
            worst = min(prior_worst, stop_px) if side > 0 else max(prior_worst, stop_px)
            px, kind = stop_px, 0
        # The synthetic shared close890 time endpoint is native OPEN891.
        # Include that actual exit in excursion, including an adverse gap.
        worst = min(worst, px) if side > 0 else max(worst, px)
        audit.append(dict(shared_result_exit_j=int(result[0]), shared_result_exit=float(result[1]),
            shared_result_kind=int(result[2]), shared_result_worst=float(result[3]),
            stop_first_override=bool(override), adapter_exit_j=int(exit_j), adapter_exit=float(px),
            adapter_kind=int(kind), adapter_worst=float(worst), stop_price=float(stop_px) if math.isfinite(stop_px) else None,
            target_price=float(tgt_px) if math.isfinite(tgt_px) else None,
            fill_through=float(fill_through), shared_walker_calls=1, numba_compiled_path_used=False))
        return exit_j, px, kind, worst
    private_globals = dict(shared_grid.execute.__globals__)
    private_globals["_walk"] = conservative_walk
    return FunctionType(shared_grid.execute.__code__, private_globals,
        name="H05_private_shared_execute", argdefs=shared_grid.execute.__defaults__,
        closure=shared_grid.execute.__closure__)


def execute_native_models(grid, entries_with_row_j_side_entry_ATR15):
    """Return PROTECTED_HW and TIME_CONTROL native-MNQ trade DataFrames.

    Required input columns: row,entry_j,side,entry,atr15. Additional entry
    metadata are retained. The caller owns source/ATR/hash admission. No cache,
    source file, outcome, model selection or account operation occurs here.
    """
    entries = entries_with_row_j_side_entry_ATR15.copy()
    needed = ("row", "entry_j", "side", "entry", "atr15")
    if any(name not in entries for name in needed):
        raise ValueError("Native execution entries require:" + ",".join(needed))
    if entries["row"].duplicated().any():
        raise ValueError("H05 freezes at most one entry per native date.")
    adapted_close = grid.c.copy()
    prepared = []
    for _, record in entries.iterrows():
        row, j, side = int(record["row"]), int(record["entry_j"]), int(record["side"])
        entry, atr = float(record["entry"]), float(record["atr15"])
        if row != record["row"] or j != record["entry_j"] or side != record["side"]:
            raise ValueError("Native row/minute/side must be exact integers.")
        if not (0 <= row < len(grid.o) and 0 <= j <= SCAN_END_J and side in (-1, 1)):
            raise ValueError("Invalid native entry row/minute/side.")
        if not (math.isfinite(entry) and entry > 0 and math.isfinite(atr) and atr > 0):
            raise ValueError("Native entry and admitted ATR15 must be finite positive.")
        if grid.o[row, j] != entry:
            raise ValueError("Entry differs from exact admitted native next-minute OPEN.")
        if not (grid.last_j[row] >= NATIVE_TIME_EXIT_J and math.isfinite(grid.o[row, NATIVE_TIME_EXIT_J])
                and grid.o[row, NATIVE_TIME_EXIT_J] > 0):
            raise ValueError("Exact native OPEN891 endpoint is unavailable; no fallback.")
        # This copy is only consumed after protection through890 fails to exit.
        adapted_close[row, SCAN_END_J] = grid.o[row, NATIVE_TIME_EXIT_J]
        stop_price, target_price = _rounded_brackets(entry, atr, side)
        prepared.append(dict(day=row, dj=j - 1, side=side, stop=(entry - stop_price) * side,
            target=(target_price - entry) * side, exit_j=SCAN_END_J, qty=1.0,
            frozen_stop_price=stop_price, frozen_target_price=target_price))
    adapted = SimpleNamespace(o=grid.o, h=grid.h, l=grid.l, c=adapted_close,
        ts=grid.ts, last_j=grid.last_j.copy())
    definitions = {}
    for model in ("PROTECTED_HW", "TIME_CONTROL"):
        signals = pd.DataFrame(prepared, columns=("day", "dj", "side", "stop", "target", "exit_j", "qty", "frozen_stop_price", "frozen_target_price"))
        if model == "TIME_CONTROL":
            signals["stop"], signals["target"] = np.inf, np.inf
        calls = []
        engine_trades = _private_execute(calls)(adapted, signals, max_trades=1, max_losses=99, name=model)
        if len(engine_trades) != len(entries) or len(calls) != len(entries):
            raise ValueError("Shared engine omitted an admitted entry; no silent deletion.")
        records = []
        by_row = {int(record["row"]): record.to_dict() for _, record in entries.iterrows()}
        brackets = {int(record["day"]): record for record in prepared}
        for call_index, engine in enumerate(engine_trades.to_dict("records")):
            row, entry_j, engine_j1, kind = int(engine["day"]), int(engine["j0"]), int(engine["j1"]), int(engine["kind"])
            side, entry, exit_price = int(engine["side"]), float(engine["entry"]), float(engine["exit"])
            exit_j = NATIVE_TIME_EXIT_J if kind == 2 else engine_j1
            gross = (exit_price - entry) * side * MNQ_POINT_VALUE
            exit_slip = 0.0 if kind == 1 else MARKET_STOP_SLIP
            native_record = dict(by_row[row])
            native_record.update(dict(model=model, entry_j=entry_j, exit_j=exit_j,
                entry=entry, side=side, exit=exit_price, kind=kind,
                engine_j0=entry_j, engine_j1=engine_j1, engine_exit=exit_price,
                engine_pnl_nq=float(engine["pnl"]), engine_net_nq_ignored=float(engine["net"]),
                engine_mae_nq=float(engine["mae"]), engine_qty=float(engine["qty"]),
                source_engine_point_value=float(shared_grid.POINT_VALUE), engine_net_used_for_native=False,
                stop_price=brackets[row]["frozen_stop_price"] if model == "PROTECTED_HW" else None,
                target_price=brackets[row]["frozen_target_price"] if model == "PROTECTED_HW" else None,
                gross_mnq=gross, commission_mnq=COMMISSION_RT, entry_slippage_mnq=MARKET_STOP_SLIP,
                exit_slippage_mnq=exit_slip, costs_mnq=COMMISSION_RT + MARKET_STOP_SLIP + exit_slip,
                net_mnq=gross - COMMISSION_RT - MARKET_STOP_SLIP - exit_slip,
                shared_walk_audit=calls[call_index], time_endpoint_is_exact_OPEN891=kind == 2,
                original_native_grid_mutated=False))
            records.append(native_record)
        frame = pd.DataFrame(records)
        frame.attrs.update(model=model, shared_execution="privateFunctionTypeclone;one_shared_walk.py_func_pertrade",
            source_grid_modified=False, native_point_value=MNQ_POINT_VALUE,
            protection_scan_end_j=SCAN_END_J, native_time_exit_j=NATIVE_TIME_EXIT_J,
            target_through_NQpoints=1.0, costs_native_not_engine_net_rescaling=True)
        definitions[model] = frame
    return definitions


def fixtures():
    def fixture(side=1, atr=100., entry=100.):
        shape = (1, 1440)
        arrays = {name: np.full(shape, entry) for name in ("o", "h", "l", "c")}
        grid = SimpleNamespace(**arrays, ts=np.array([np.datetime64("2020-01-02")]), last_j=np.array([1439]))
        entries = pd.DataFrame([dict(row=0, entry_j=521, side=side, entry=entry, atr15=atr, event_id="ARTIFICIAL")])
        return grid, entries
    # Stop is active on the entry minute.
    grid, entries = fixture(); grid.l[0, 521] = 79
    result = execute_native_models(grid, entries)["PROTECTED_HW"].iloc[0]
    assert result.kind == 0 and result.exit_j == 521 and result.exit == 80 and result.net_mnq == -42.24
    # Subsequent worse opening gap gets the open, not the nominal stop.
    grid, entries = fixture(); grid.o[0, 522] = 70; grid.l[0, 522] = 69
    result = execute_native_models(grid, entries)["PROTECTED_HW"].iloc[0]
    assert result.kind == 0 and result.exit_j == 522 and result.exit == 70
    # Shared nearer-high path would target first; declared override chooses stop.
    grid, entries = fixture(); grid.h[0, 521] = 111; grid.l[0, 521] = 79
    result = execute_native_models(grid, entries)["PROTECTED_HW"].iloc[0]
    assert result.kind == 0 and result.exit == 80 and result.shared_walk_audit["stop_first_override"]
    assert result.shared_walk_audit["shared_result_kind"] == 1
    # Target touch is insufficient; first1pointthrough fills exact target.
    grid, entries = fixture(); grid.h[0, 521] = 110; grid.h[0, 522] = 111
    result = execute_native_models(grid, entries)["PROTECTED_HW"].iloc[0]
    assert result.kind == 1 and result.exit_j == 522 and result.exit == 110 and result.net_mnq == 18.26
    # Time OPEN891 has priority: no891 high/low stop or target inspection.
    grid, entries = fixture(); grid.o[0, 891] = 105; grid.h[0, 891] = 200; grid.l[0, 891] = 1
    before = {name: getattr(grid, name).copy() for name in ("o", "h", "l", "c", "last_j")}
    models = execute_native_models(grid, entries)
    for frame in models.values():
        item = frame.iloc[0]
        assert item.kind == 2 and item.engine_j1 == 890 and item.exit_j == 891 and item.exit == 105
        assert item.gross_mnq == 10 and item.net_mnq == 7.76 and item.engine_net_used_for_native == False
    assert all(np.array_equal(getattr(grid, name), value, equal_nan=True) for name, value in before.items())
    # Protect through the preceding completed minute, including890.
    grid, entries = fixture(); grid.l[0, 890] = 79; grid.o[0, 891] = 105
    assert execute_native_models(grid, entries)["PROTECTED_HW"].iloc[0].exit_j == 890
    # Conservative quarter-point rounding is mirrored on both sides.
    assert _rounded_brackets(100, 10.1, 1) == (97.75, 101.25)
    assert _rounded_brackets(100, 10.1, -1) == (102.25, 98.75)
    grid, entries = fixture(side=-1); grid.l[0, 521] = 89; grid.h[0, 521] = 121
    item = execute_native_models(grid, entries)["PROTECTED_HW"].iloc[0]
    assert item.kind == 0 and item.exit == 120 and item.net_mnq == -42.24
    grid, entries = fixture(side=-1); grid.o[0, 522] = 130; grid.h[0, 522] = 131
    assert execute_native_models(grid, entries)["PROTECTED_HW"].iloc[0].exit == 130
    # No favorable limit improvement even when a bar opens past the target.
    grid, entries = fixture(); grid.o[0, 522] = 115; grid.h[0, 522] = 116; grid.l[0, 522] = 114
    assert execute_native_models(grid, entries)["PROTECTED_HW"].iloc[0].exit == 110
    # TIME_CONTROL exactly reconciles the frozen raw endpoint for each side.
    for side in (-1, 1):
        grid, entries = fixture(side=side); grid.o[0, 891] = 103.25
        item = execute_native_models(grid, entries)["TIME_CONTROL"].iloc[0]
        assert item.gross_mnq == (103.25 - 100) * side * 2
        assert abs(item.net_mnq - (item.gross_mnq - 2.24)) < 1e-12
    # An adverse time-open gap belongs to MAE even though891 protection is off.
    for side, exit_open in ((1, 70.0), (-1, 130.0)):
        grid, entries = fixture(side=side); grid.o[0, 891] = exit_open
        models = execute_native_models(grid, entries)
        for frame in models.values():
            item = frame.iloc[0]
            assert item.kind == 2 and item.engine_j1 == 890 and item.exit_j == 891 and item.exit == exit_open
            assert item.engine_mae_nq == 600 and item.shared_walk_audit["adapter_worst"] == exit_open
            assert item.gross_mnq == -60 and item.net_mnq == -62.24
    assert shared_grid.execute.__globals__["_walk"] is shared_grid._walk
    assert _private_execute([]).__globals__ is not shared_grid.execute.__globals__
    return dict(passed=True, actual_market_gross_or_CSV_rows_read=False, compiled_numba_cache_created=False,
        checks=["entrybarprotection", "worsegapstopsbothsides", "stopfirstambiguousbaroverridesharedtargetpath",
            "1NQpointtargetthrough/nolimitgapimprovement", "timeOPEN891priority/protectionthrough890",
            "conservativebothsidestickrounds", "nativeMNQfees/slippage/notengineNQnetrescaling",
            "TIME_CONTROLrawendpointreconciliation", "adverseOPEN891includedinMAEbothsides/allmodels",
            "privatefunctionglobals/nooriginalgridmutation"],
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__ == "__main__":
    result = fixtures()
    output = Path(__file__).resolve().parent / "outputs/codex_hunt_v2_highwin_confirmation" / f"execution_synthetic_checks_{result['script_sha256'][:12]}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as handle:
        json.dump(result, handle, indent=2, allow_nan=False); handle.write("\n")
    print(json.dumps(result, allow_nan=False))
