"""Bounded replay engineering reproduction, not another portfolio selection.

Only the frozen CURRENT50K policy and the first design Monday (2018-04-02)
are permitted. A canonical completed/partial screen CSV must already contain
that case. Reproduce the same case without segment skipping, check native
source-order costs and record conditional OHLC/source limits. No2023outcomes.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "analysis"))
import codex_eval_run_20261104 as run
import codex_eval_engine_20261104 as engine

PREREG = "a087708b13697df4c3dd0b0814f98cb53a2b254a"
START = "2018-04-02"
POLICY_ID = "E50_7ba98d03398338e0"
HERE = Path(__file__).resolve().parent


def same_number(a, b):
    return np.isclose(float(a), float(b), rtol=1e-11, atol=1e-7, equal_nan=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical-cases", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, default=run.DEFAULT_RUNTIME)
    args = parser.parse_args()
    # The source policy/case is immutable; no outcome-dependent candidate or
    # date choice can be made by this engineering script.
    for name in run.IMPLEMENTATION + ["agents/codex/inputs/eval_audit_20261104/config.json"]:
        run.verify_file_at_commit(ROOT / name, PREREG)
    rows = run.read_cases(args.canonical_cases)
    canonical = [r for r in rows if r["candidate_id"] == POLICY_ID and r["start_id"] == START]
    if len(canonical) != 1:
        raise ValueError("Existing canonical CURRENT50K first-design-Monday case required")
    canonical = canonical[0]
    assert canonical["cost_scenario"] == "main" and canonical["initial_state"] == "fresh"
    registry = run.read_json(run.BASE / "policies.json")
    policy = next(p for p in registry["candidates"] if p["candidate_id"] == POLICY_ID)
    assert policy["account"] == 50 and policy["label"] == "CURRENT"
    assert policy["governor"] == dict(risk_fraction=0., aggregate_stop_fraction=1., cushion_buffer=0., target_guard=False)
    tape, prepared = run.load_tape(args.runtime / "tape", run.DEFAULT_CONFIG, PREREG)
    window = next(w for w in run.make_windows(tape, "design") if w.start_id == START)
    assert window.year == 2018 and window.expiry < 1546322400  # January2019CT; no later-year outcomes.
    event_rows = (tape.events[:, 0] >= window.a) & (tape.events[:, 0] < window.b)
    original_events = tape.events
    tape.events = original_events[event_rows]
    try:
        requested = run.requested_events(tape, policy)
    finally:
        tape.events = original_events
    events = requested.copy()
    events[:, 0] -= window.a
    ticks = np.asarray(tape.metadata["ticks"], float)
    pv = np.asarray(tape.metadata["point_values"], float)
    fees = np.full(len(ticks), .62)
    cutoff = np.zeros(len(tape.dates), dtype=np.int64)
    cr = np.flatnonzero(tape.cutoff)
    cutoff[tape.session[cr]] = tape.times[cr].astype(np.int64)
    raw, logs = engine.simulate(tape.prices[window.a:window.b], tape.times[window.a:window.b],
        tape.session[window.a:window.b], events, pv, fees, ticks, cutoff, window.expiry,
        rules=replace(engine.EOD50, target_guard=False), record_logs=True)
    actual_status = {"expired": "expire", "active_at_tape_end": "unknown"}.get(raw["status_name"], raw["status_name"])
    checks = {"status": actual_status == canonical["status"], "reason": raw["reason_name"] == canonical["reason"]}
    numeric = ["cash", "equity", "floor", "max_net_micro_exposure", "fill_count", "rejected_entries",
        "trimmed_entries", "dll_pauses", "forced_cutoff_flats", "commission", "source_fill_slippage",
        "liquidation_cost", "open_virtual_positions"]
    for key in numeric:
        checks["canonical_" + key] = same_number(raw[key], canonical[key])
    last_epoch = float(tape.times[window.a + int(raw["last_row"])])
    checks["canonical_last_epoch"] = same_number(last_epoch, canonical["last_epoch"])
    # This is the same frozen policy. A raw walk supplies the exact modeled
    # visited-price minimum; the saved fast value/bound need only enclose it.
    checks["fast_bound_encloses_raw_minimum"] = float(canonical["minimum_equity_lower_bound"]) <= raw["minimum_equity"] + 1e-7
    checks["fast_visited_minimum_not_below_raw"] = float(canonical["minimum_equity"]) >= raw["minimum_equity"] - 1e-7
    checks["all_requests_native_integer"] = bool(np.equal(events[:, 8], np.floor(events[:, 8])).all())
    # Independent source-cost identity from accepted source orders, rather than
    # trusting the core's aggregate counters. DLL log rows have action -2 and
    # are excluded; their total liquidation cost is reported separately.
    event_map = {(int(e[0]), int(e[1]), int(e[4])): e for e in events}
    source_logs = logs[np.isin(logs[:, 2], [-1, 1]) & (logs[:, 7] == 0)]
    source_fees = 0.; source_slippage = 0.; cost_rows = []
    for log in source_logs:
        event = event_map[(int(log[0]), int(log[1]), int(log[2]))]
        asset = int(event[3]); qty = log[3]
        expected_slip = 0. if event[9] == 1 else ticks[asset]
        order_side = event[5] if event[4] == 1 else -event[5]
        expected_fill = event[6] + order_side * expected_slip
        checks[f"source_fill_{len(cost_rows)}"] = same_number(log[4], expected_fill)
        checks[f"source_fee_{len(cost_rows)}"] = same_number(log[5], qty * .62)
        source_fees += qty * .62
        source_slippage += qty * abs(log[4] - event[6]) * pv[asset]
        cost_rows.append(dict(row=int(log[0]), trade_id=int(log[1]), action=int(log[2]),
            key=tape.keys[int(event[2])], quantity=int(qty), raw_fill=float(event[6]),
            modeled_fill=float(log[4]), source_known_stop_points=float(event[7]),
            native_point_value=float(pv[asset]), per_side_commission=float(log[5])))
    checks["source_fee_sum"] = same_number(source_fees, raw["commission"])
    checks["source_slippage_sum"] = same_number(source_slippage, raw["source_fill_slippage"])
    for e in events[events[:, 4] == 1]:
        key = tape.keys[int(e[2])]
        if key == "VB":
            checks["VB_fixed75_source_stop"] = checks.get("VB_fixed75_source_stop", True) and same_number(e[7], 75.)
            checks["VB_requested8_micros"] = checks.get("VB_requested8_micros", True) and e[8] == 8
        if key == "BRIDGE":
            checks["BRIDGE_no_invented_stop"] = checks.get("BRIDGE_no_invented_stop", True) and bool(np.isposinf(e[7]))
            checks["BRIDGE_requested2_micros"] = checks.get("BRIDGE_requested2_micros", True) and e[8] == 2
        if key in ("ONB30", "EOS") and np.isfinite(e[7]) and e[7] > 0:
            budget = 1100. if key == "ONB30" else 500.
            name = f"{key}_native_risk_floor"
            checks[name] = checks.get(name, True) and e[8] == np.floor(budget / (e[7] * pv[int(e[3])]))
    receipt = dict(scope="One previously completed2018CURRENT50K reference, same-rule raw-vs-fast engineering reproduction; no new hypothesis/definition or2023outcomes.",
        preregistration_commit=PREREG, start=START, candidate_id=POLICY_ID,
        canonical_cases_path=str(args.canonical_cases.resolve().relative_to(ROOT)),
        canonical_cases_sha256=run.sha(args.canonical_cases), prepare_receipt=prepared,
        policy=policy, checks=checks, checks_pass=bool(all(checks.values())),
        raw_result=raw, canonical_result=canonical, native_source_order_checks=cost_rows,
        source_cost_check_exercised=bool(len(cost_rows)),
        limits=["Frozen common-OHLC phase path and source-fill insertions remain conditional, not native tick chronology.",
                "Most account core source was written by this reviewer; this reproduces engineering identities, not a fully independent economic implementation.",
                "One reference case cannot establish calibrated pass probabilities, data sufficiency or optimality.",
                "No2023portfolio validation was inspected or computed."])
    run.atomic_json(HERE / "postexecution_engineering_review.json", receipt)
    summary = "PASS" if receipt["checks_pass"] else "FAIL"
    text = f"""# Postexecution account engineering review: {summary}

Summary: Reproduced only CURRENT50K on2018-04-02 from an already saved canonical design case.
The same frozen policy was walked without segment skipping; {sum(checks.values())}/{len(checks)} engineering checks passed.
Account outcome: {actual_status} ({raw['reason_name']}); source fill count {int(raw['fill_count'])}; source-cost checks exercised: {bool(len(cost_rows))}.
No new portfolio definition, strategy variant,2023outcome or selection was created.
This is conditional OHLC engineering reproduction; native/source economic verification remains pending.

Preregistration: `{PREREG}`. Exact details and source-order cost checks:
`postexecution_engineering_review.json`; reproduction: `postexecution_engineering_check.py`.

The input policy has target_guard=False, unchanged CURRENT sizing and main costs$1.24RT per micro
plus one adverse tick per market/stop side. Native integer requests, source stops, accepted order fills,
source commissions/slippage, full-clock outcome, account floor and fast/raw parity are checked directly.
The raw walk's minimum is exact for this frozen conditional tape; the fast minimum/bound is compared
with its stated scope. This single case is not an investment result or an estimate of optimal pass odds.

This first case has no admitted fills: its source-cost sum identities are vacuous, so they do not independently
verify a historical native fill or cost application. The missing-risk request correctly stops the dependent replay.
The core's author performed this check, so it does not replace independent raw-spec replication or
Claude's verification. Source-report minute phases, continuous-contract identity, common OHLC sequencing,
other-asset synchronization and actual target-guard installation remain material qualifications.
"""
    (HERE / "postexecution_engineering_review.md").write_text(text)
    print(json.dumps(dict(status=summary, checks=len(checks), source_fills=len(cost_rows),
        reference_status=actual_status, output=str(HERE / "postexecution_engineering_review.json"))))
    if not receipt["checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
