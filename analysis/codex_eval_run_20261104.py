"""Committed, resumable research orchestration for the November4 eval audit.

There are no import-time market reads. ``prepare`` is the first market command;
all market/account commands require an exact full preregistration commit. Initial
design, derived-governor design, frozen nomination, and historical validation are
separate commands so their evidence/selection artifacts can be committed between
stages. This code never changes a trading plan or an installed strategy.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta
import gc
import fcntl
import hashlib
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import tempfile
from zoneinfo import ZoneInfo
import zipfile

import numpy as np

import codex_eval_engine_20261104 as engine
import codex_eval_paths_20261104 as paths
import codex_eval_policies_20261104 as policies
import codex_eval_selection_20261104 as selection

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "agents/codex/inputs/eval_audit_20261104"
DEFAULT_CONFIG = BASE / "config.json"
DEFAULT_RUNTIME = ROOT / "agents/codex/runtime/eval_audit_20261104"
SCRIPT = "analysis/codex_eval_run_20261104.py"
IMPLEMENTATION = [SCRIPT, "analysis/codex_eval_engine_20261104.py",
    "analysis/codex_eval_paths_20261104.py", "analysis/codex_eval_extra_ledgers_20261104.py",
    "analysis/codex_eval_policies_20261104.py", "analysis/codex_eval_selection_20261104.py",
    "analysis/grid24.py", "agents/codex/inputs/eval_audit_20261104/policies.json"]
CT = ZoneInfo("America/Chicago")
MAX_DEFINITIONS = 3000
MAX_DERIVED = 30
DESIGN_YEARS = (2018, 2019, 2020, 2021, 2022)
COSTS = {"main": {"round_trip_commission": 1.24, "slippage_ticks": 1.},
         "low": {"round_trip_commission": 1.04, "slippage_ticks": 1.},
         "stress": {"round_trip_commission": 2.48, "slippage_ticks": 2.}}
STATE_FRACTIONS = {"fresh": 1., "quarter_cushion": .25,
                   "half_cushion": .5, "three_quarter_cushion": .75}
CASE_FIELDS = ["candidate_id", "account", "label", "start_id", "start_year",
    "start_weekday", "purchase_ct", "expiry_ct", "expiry_epoch", "status", "reason",
    "last_epoch", "calendar_days", "observed_trading_sessions", "equity", "cash",
    "floor", "minimum_equity", "minimum_equity_lower_bound", "minimum_equity_scope",
    "max_net_micro_exposure", "fill_count", "rejected_entries", "trimmed_entries",
    "dll_pauses", "forced_cutoff_flats", "commission", "source_fill_slippage",
    "liquidation_cost", "total_modeled_cost", "open_virtual_positions",
    "skipped_raw_rows", "cost_scenario", "initial_state", "initial_equity", "initial_floor"]


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
        allow_nan=False, default=str).encode()).hexdigest()


def finite_json(value):
    """Encode unavailable statistics as null, never invented numeric values."""
    if isinstance(value, dict):
        return {str(k): finite_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [finite_json(v) for v in value]
    if isinstance(value, np.ndarray):
        return finite_json(value.tolist())
    if isinstance(value, (np.integer, np.bool_)):
        return value.item()
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    return value


def atomic_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(finite_json(value), indent=2, sort_keys=True,
        allow_nan=False, default=str) + "\n")
    os.replace(tmp, path)


def read_json(path):
    return json.loads(Path(path).read_text())


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT))


def verify_file_at_commit(path, commit):
    if not commit or len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise ValueError("An exact, full lowercase commit SHA is required")
    subprocess.run(["git", "merge-base", "--is-ancestor", commit, "HEAD"],
        cwd=ROOT, check=True, capture_output=True)
    p = Path(path).resolve()
    before = subprocess.check_output(["git", "show", f"{commit}:{relative(p)}"], cwd=ROOT)
    if before != p.read_bytes():
        raise ValueError("Committed artifact changed: " + relative(p))


def guard(config_path, commit):
    """Verify exact code/config bytes and every registered owned input hash."""
    if subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() != "codex/work":
        raise ValueError("Research writes are restricted to codex/work")
    cfg = paths.verify_preregistration(config_path, commit)
    for name in IMPLEMENTATION:
        verify_file_at_commit(ROOT / name, commit)
    registry = read_json(BASE / "policies.json")
    rows = registry["candidates"]
    if len(rows) != registry["initial_definitions"] or len(rows) + MAX_DERIVED > MAX_DEFINITIONS:
        raise ValueError("Definition count/reservation does not match frozen budget")
    if registry.get("max_economic_definitions") != MAX_DEFINITIONS:
        raise ValueError("Unexpected economic-definition budget")
    ids = [p["candidate_id"] for p in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate registered candidate IDs")
    # These are methods, not tuneable CLI options. Config may state them but
    # cannot silently replace them after the registered study was constructed.
    if cfg.get("costs", COSTS) != COSTS:
        raise ValueError("Unexpected cost scenarios")
    return cfg, rows


@dataclass
class Window:
    start_id: str
    year: int
    weekday: int
    first_session: int
    last_session: int
    a: int
    b: int
    node_a: int
    node_b: int
    purchase: int
    expiry: int


def make_windows(tape, phase):
    """Fixed common start calendar; complete expiry, no truncated tail outcomes.

    Design uses Monday starts whose entire account window expires in2018--22.
    Validation uses all weekday starts in2023+, including previously seen years.
    Observed market-session availability is a metric, not a way to drop starts.
    """
    if phase not in ("design", "validation"):
        raise ValueError("Unknown phase")
    windows = []
    for s, raw in enumerate(tape.dates):
        day = datetime.strptime(str(int(raw)), "%Y%m%d").date()
        if (phase == "design" and (day.year not in DESIGN_YEARS or day.weekday() != 0)) or (
            phase == "validation" and (day.year < 2023 or day.weekday() >= 5)):
            continue
        bought = day - timedelta(days=1)
        purchase = int(datetime(bought.year, bought.month, bought.day, 16, 30, tzinfo=CT).timestamp())
        expiry = engine.modeled_expiry(datetime.fromtimestamp(purchase, CT), 30)
        if phase == "design" and expiry >= datetime(2023, 1, 1, tzinfo=CT).timestamp():
            continue
        # A start is admitted only if its entire expiry boundary exists. No
        # start-dependent missing-return clipping or partial-window successes.
        if expiry > tape.times[-1]:
            continue
        a = int(np.searchsorted(tape.session, s, side="left"))
        erow = int(np.searchsorted(tape.times, expiry, side="left"))
        if a >= len(tape.times) or erow >= len(tape.times):
            continue
        na = int(np.searchsorted(tape.node_rows, a))
        nb = int(np.searchsorted(tape.node_rows, erow))
        if na >= len(tape.node_rows) or nb >= len(tape.node_rows) or tape.node_rows[na] != a:
            raise ValueError("Window boundary is absent from segment index")
        b = int(tape.node_rows[nb]) + 1
        last_session = int(tape.session[b - 1])
        windows.append(Window(day.isoformat(), day.year, day.weekday(), s, last_session,
            a, b, na, nb, purchase, expiry))
    if not windows:
        raise ValueError("No full-expiry windows for " + phase)
    return windows


def requested_events(tape, policy):
    """One precomputed integer request per source entry and allocation policy.

    A missing/invalid signal-time stop becomes -1 (UNKNOWN when encountered),
    not a zero-sized observation. Unallocated keys have no events whatsoever.
    Source unit ticket quantities are replaced, not multiplied a second time.
    """
    book = policy["book"]
    unknown = set(book) - set(tape.keys)
    if unknown:
        raise ValueError("Book keys absent from source universe: " + repr(unknown))
    key_ids = [tape.keys.index(k) for k in book]
    events = tape.events[np.isin(tape.events[:, 2].astype(np.int64), key_ids)].copy()
    pv = np.asarray(tape.metadata["point_values"], float)
    for key, allocation in book.items():
        mask = (events[:, 2] == tape.keys.index(key)) & (events[:, 4] == 1)
        value = float(allocation["value"])
        if not np.isfinite(value) or value < 0:
            raise ValueError("Invalid allocation")
        if allocation["kind"] == "lots":
            events[mask, 8] = math.floor(value)
        elif allocation["kind"] == "risk":
            rows = np.flatnonzero(mask)
            unit_risk = events[rows, 7] * pv[events[rows, 3].astype(np.int64)]
            good = np.isfinite(unit_risk) & (unit_risk > 0)
            qty = np.full(len(rows), -1., dtype=float)
            qty[good] = np.floor(value / unit_risk[good])
            events[rows, 8] = qty
        else:
            raise ValueError("Unknown allocation kind")
    return events


def load_tape(folder, config_path, commit):
    folder = Path(folder)
    receipt = read_json(folder / "prepare_receipt.json")
    if receipt["preregistration_commit"] != commit or receipt["config_sha256"] != sha(config_path):
        raise ValueError("Prepared tape belongs to another frozen study")
    for name, expected in receipt["artifacts"].items():
        if sha(folder / name) != expected:
            raise ValueError("Prepared tape artifact changed: " + name)
    metadata = read_json(folder / "metadata.json")
    if metadata["preregistration_commit"] != commit or metadata["config_sha256"] != sha(config_path):
        raise ValueError("Tape metadata/config mismatch")
    z = np.load(folder / "tape.npz", allow_pickle=False)
    names = ["prices", "times", "session", "events", "node_rows", "segment_min",
        "segment_max", "segment_missing", "eod", "cutoff", "session_start", "dates", "coverage", "trading_day"]
    fields = {name: z[name] for name in names}
    z.close()
    # Trade/quality source tables stay on disk; they are not needed by simulator.
    tape = paths.Tape(**fields, markets=tuple(metadata["markets"]), keys=tuple(metadata["keys"]),
        trades=None, quality=None, metadata=metadata)
    if set(tape.keys) != set(policies.ALL_KEYS):
        raise ValueError("Prepared tape must cover the frozen18-key universe")
    return tape, receipt


def prepare(args):
    cfg, _ = guard(args.config, args.commit)
    dest = args.runtime / "tape"
    if (dest / "prepare_receipt.json").exists():
        _, receipt = load_tape(dest, args.config, args.commit)
        print(json.dumps({"reused_prepared_tape": True, "receipt": receipt}))
        return
    # Builder's frozen adapter hook normalizes the four extras while its NQ
    # grid is already loaded. Do not construct/read a duplicate full grid here.
    tape = paths.build(args.config, args.commit, dest)
    receipt = {"preregistration_commit": args.commit, "config_sha256": sha(args.config),
        "artifacts": {name: sha(dest / name) for name in ["tape.npz", "metadata.json", "trades.csv", "quality.csv"]},
        "rows": len(tape.times), "source_events": len(tape.events),
        "status": "conditional common-OHLC research tape; independent raw-spec/broker verification pending"}
    atomic_json(dest / "prepare_receipt.json", receipt)
    print(json.dumps(receipt))


def _case_base(policy, w, scenario, state, rules):
    row = {field: "" for field in CASE_FIELDS}
    row.update(candidate_id=policy["candidate_id"], account=f"{policy['account']}K", label=policy["label"],
        start_id=w.start_id, start_year=w.year, start_weekday=w.weekday,
        purchase_ct=datetime.fromtimestamp(w.purchase, CT).isoformat(),
        expiry_ct=datetime.fromtimestamp(w.expiry, CT).isoformat(), expiry_epoch=w.expiry,
        cost_scenario=scenario, initial_state=state, initial_equity=rules.nominal_start,
        initial_floor=rules.nominal_start - rules.trail * STATE_FRACTIONS[state])
    return row


def run_window(tape, events, policy, w, scenario="main", state="fresh", record_logs=False):
    gov = policy["governor"]
    base_rules = engine.EOD50 if int(policy["account"]) == 50 else engine.EOD150
    rules = replace(base_rules, target_guard=bool(gov.get("target_guard", False)))
    row = _case_base(policy, w, scenario, state, rules)
    if policy["book"]:
        ki = [tape.keys.index(k) for k in policy["book"]]
        if not tape.coverage[ki, w.first_session:w.last_session + 1].all():
            row.update(status="unknown", reason="source_sampling_does_not_cover_full_window",
                last_epoch=w.purchase, calendar_days=0., observed_trading_sessions=0)
            return row, np.empty((0, 8))
    left = np.searchsorted(events[:, 0], w.a) if len(events) else 0
    right = np.searchsorted(events[:, 0], w.b) if len(events) else 0
    ev = events[left:right].copy()
    ev[:, 0] -= w.a
    ticks = np.asarray(tape.metadata["ticks"], float)
    fees = np.full(len(ticks), COSTS[scenario]["round_trip_commission"] / 2.)
    slippage = ticks * COSTS[scenario]["slippage_ticks"]
    # Construct once per loaded tape, rather than scan the full multi-year
    # indicator tape separately for every historical account start.
    if not hasattr(tape, "_cutoff_times"):
        tape._cutoff_times = np.zeros(len(tape.dates), dtype=np.int64)
        cr = np.flatnonzero(tape.cutoff)
        tape._cutoff_times[tape.session[cr]] = tape.times[cr].astype(np.int64)
    cutoff = tape._cutoff_times
    result, logs = engine.simulate(tape.prices[w.a:w.b], tape.times[w.a:w.b],
        tape.session[w.a:w.b], ev, tape.metadata["point_values"], fees, slippage,
        cutoff, w.expiry, rules=rules, initial_equity=rules.nominal_start,
        initial_floor=row["initial_floor"], risk_fraction=gov.get("risk_fraction", 0.),
        aggregate_stop_fraction=gov.get("aggregate_stop_fraction", 1.),
        cushion_buffer=gov.get("cushion_buffer", 0.), aggregate_stop_reserve=True,
        node_rows=tape.node_rows[w.node_a:w.node_b + 1] - w.a,
        segment_min=tape.segment_min[w.node_a:w.node_b],
        segment_max=tape.segment_max[w.node_a:w.node_b],
        segment_missing=tape.segment_missing[w.node_a:w.node_b], record_logs=record_logs)
    status = {"expired": "expire", "active_at_tape_end": "unknown"}.get(result["status_name"], result["status_name"])
    r = max(0, min(w.b - w.a - 1, int(result["last_row"])))
    last = float(tape.times[w.a + r])
    end_session = int(tape.session[w.a + r])
    observed = int(tape.trading_day[w.first_session:end_session + 1].sum())
    row.update({k: result[k] for k in CASE_FIELDS if k in result})
    row.update(status=status, reason=result["reason_name"], last_epoch=last,
        calendar_days=(last - w.purchase) / 86400., observed_trading_sessions=observed,
        total_modeled_cost=result["commission"] + result["source_fill_slippage"] + result["liquidation_cost"])
    if record_logs and len(logs):
        logs = logs.copy(); logs[:, 0] += w.a
    return row, logs


def read_cases(path):
    with Path(path).open(newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for key in ("calendar_days", "last_epoch", "equity", "cash", "floor", "total_modeled_cost"):
            if row.get(key) != "":
                row[key] = float(row[key])
        row["start_year"] = int(row["start_year"])
        row["start_weekday"] = int(row["start_weekday"])
    return rows


def annual_summaries(rows, policy):
    result = []
    for year in sorted(set(r["start_year"] for r in rows)):
        result.append(selection.summarize_outcomes([r for r in rows if r["start_year"] == year],
            time_key="calendar_days", start_key="start_id", candidate_id=policy["candidate_id"],
            account=f"{policy['account']}K", year=int(year)))
    return result


_WORK = {}


def _candidate_job_locked(policy):
    ctx = _WORK
    folder = ctx["folder"] / ctx["scenario"] / ctx["state"]
    folder.mkdir(parents=True, exist_ok=True)
    stem = folder / policy["candidate_id"]
    path = stem.with_suffix(".csv")
    meta_path = stem.with_suffix(".json")
    partial = stem.with_suffix(".partial.csv")
    signature_path = stem.with_suffix(".pending.json")
    fingerprint = digest({"study": ctx["fingerprint"], "policy": policy,
        "calendar": [w.start_id for w in ctx["windows"]], "scenario": ctx["scenario"],
        "costs": COSTS[ctx["scenario"]], "state": ctx["state"]})
    expected = [w.start_id for w in ctx["windows"]]
    if path.exists():
        if not meta_path.exists():
            raise ValueError("Completed CSV without completion receipt: " + str(path))
        receipt = read_json(meta_path)
        if receipt["fingerprint"] != fingerprint or receipt["csv_sha256"] != sha(path):
            raise ValueError("Completed case definition/outcomes changed; refusing rerun: " + str(path))
        rows = read_cases(path)
        if [r["start_id"] for r in rows] != expected:
            raise ValueError("Completed case calendar mismatch")
        return receipt
    # Completion receipt is durable BEFORE atomic CSV publication. A crash in
    # between those operations is recovered without observing outcomes again.
    if meta_path.exists():
        receipt = read_json(meta_path)
        if receipt["fingerprint"] != fingerprint or not partial.exists() or receipt["csv_sha256"] != sha(partial):
            raise ValueError("Unpublished completion receipt does not match partial outcomes")
        if [r["start_id"] for r in read_cases(partial)] != expected:
            raise ValueError("Unpublished complete case calendar mismatch")
        os.replace(partial, path)
        return receipt
    if signature_path.exists():
        if read_json(signature_path)["fingerprint"] != fingerprint:
            raise ValueError("Partial case definitions changed; refusing resumed return work")
    else:
        if partial.exists():
            raise ValueError("Partial CSV without pre-outcome signature")
        atomic_json(signature_path, {"fingerprint": fingerprint, "policy": policy,
            "expected_starts": expected, "scenario": ctx["scenario"], "state": ctx["state"]})
    rows = read_cases(partial) if partial.exists() else []
    done = [r["start_id"] for r in rows]
    if done != expected[:len(done)]:
        raise ValueError("Partial outcome sequence changed, duplicated or not a calendar prefix")
    events = requested_events(ctx["tape"], policy)
    with partial.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CASE_FIELDS)
        if not rows:
            writer.writeheader(); f.flush(); os.fsync(f.fileno())
        for w in ctx["windows"][len(done):]:
            row, _ = run_window(ctx["tape"], events, policy, w, ctx["scenario"], ctx["state"])
            writer.writerow(row); f.flush()
            rows.append(row)
        os.fsync(f.fileno())
    receipt = {"candidate_id": policy["candidate_id"], "account": f"{policy['account']}K",
        "label": policy["label"], "fingerprint": fingerprint, "csv_sha256": sha(partial),
        "csv_path": relative(path), "n": len(rows), "status": "complete",
        "cost_scenario": ctx["scenario"], "initial_state": ctx["state"],
        "summary": selection.summarize_outcomes(rows, time_key="calendar_days", start_key="start_id",
            candidate_id=policy["candidate_id"], account=f"{policy['account']}K"),
        "annual": annual_summaries(rows, policy)}
    atomic_json(meta_path, receipt)
    os.replace(partial, path)
    return receipt


def _candidate_job(policy):
    """Do not let another writer replay or append this same candidate window."""
    folder = _WORK["folder"] / _WORK["scenario"] / _WORK["state"]
    folder.mkdir(parents=True, exist_ok=True)
    lock_path = folder / (policy["candidate_id"] + ".lock")
    with lock_path.open("a") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("Another writer owns candidate " + policy["candidate_id"]) from exc
        return _candidate_job_locked(policy)


def run_pool(tape, receipt, registry, windows, folder, args, scenario="main", state="fresh", selection_sha=None):
    global _WORK
    _WORK = {"tape": tape, "windows": windows, "folder": Path(folder), "scenario": scenario,
        "state": state, "fingerprint": digest({"preregistration_commit": args.commit,
            "config_sha256": sha(args.config), "tape_receipt": receipt,
            "selection_sha256": selection_sha})}
    # Populate before forking so workers share this read-only setup by COW.
    if not hasattr(tape, "_cutoff_times"):
        tape._cutoff_times = np.zeros(len(tape.dates), dtype=np.int64)
        cr = np.flatnonzero(tape.cutoff)
        tape._cutoff_times[tape.session[cr]] = tape.times[cr].astype(np.int64)
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True)
    results = []
    def save(result):
        results.append(result)
        atomic_json(folder / f"progress_{scenario}_{state}.json", {
            "preregistration_commit": args.commit, "expected_candidates": len(registry),
            "completed_candidates": len(results), "completed": [r["candidate_id"] for r in results],
            "scenario": scenario, "state": state})
        print(json.dumps({"phase_folder": relative(folder), "completed": len(results),
            "of": len(registry), "candidate_id": result["candidate_id"],
            "counts": result["summary"]["counts"]}), flush=True)
    if args.workers == 1:
        for policy in registry:
            save(_candidate_job(policy))
    else:
        if "fork" not in mp.get_all_start_methods():
            raise ValueError("Parallel execution requires fork; use --workers1 on this platform")
        with mp.get_context("fork").Pool(args.workers) as pool:
            for result in pool.imap_unordered(_candidate_job, registry, chunksize=1):
                save(result)
    results.sort(key=lambda r: r["candidate_id"])
    output = {"preregistration_commit": args.commit, "scenario": scenario, "state": state,
        "candidate_count": len(registry), "calendar": [w.start_id for w in windows],
        "study_fingerprint": _WORK["fingerprint"], "results": results,
        "independent_economic_verification": "pending"}
    atomic_json(folder / f"completed_{scenario}_{state}.json", output)
    return output


def check_committed_selection(args, path):
    verify_file_at_commit(path, args.selection_commit)
    obj = read_json(path)
    if obj["preregistration_commit"] != args.commit:
        raise ValueError("Selection belongs to another preregistration")
    return obj


def checked_derived(args, initial):
    """Reconstruct the reserved second-stage menu without reading outcomes."""
    obj = check_committed_selection(args, BASE / "derived_policies.json")
    initial_selection = check_committed_selection(args, BASE / "design_selection_initial.json")
    if obj["initial_selection_sha256"] != sha(BASE / "design_selection_initial.json"):
        raise ValueError("Derived registry is not attached to the committed initial nomination")
    by_id = {r["candidate_id"]: r for r in initial}
    nominees = initial_selection["nominees"]
    if any(sum(p["account"] == a for p in nominees) > 3 for a in (50, 150)):
        raise ValueError("Initial nomination cap exceeded")
    if len({p["candidate_id"] for p in nominees}) != len(nominees):
        raise ValueError("Duplicate initial nominees")
    for policy in nominees:
        if policy["candidate_id"] not in by_id or digest(policy) != digest(by_id[policy["candidate_id"]]):
            raise ValueError("Initial nominee is not an exact registered definition")
    expected = policies.derived_governors(nominees, initial)
    if digest(obj["candidates"]) != digest(expected):
        raise ValueError("Derived registry differs from the predeclared deterministic governor menu")
    if obj["initial_definitions"] != len(initial) or obj["derived_definitions"] != len(expected) or obj["total_definitions"] != len(initial) + len(expected):
        raise ValueError("Derived registry budget accounting mismatch")
    if len(expected) > MAX_DERIVED or len(initial) + len(expected) > MAX_DEFINITIONS:
        raise ValueError("Derived definition reservation exceeded")
    return obj


def screen(args):
    _, initial = guard(args.config, args.commit)
    tape, receipt = load_tape(args.runtime / "tape", args.config, args.commit)
    selection_sha = None
    if args.pool == "initial":
        registry = initial
    else:
        derived_path = BASE / "derived_policies.json"
        obj = checked_derived(args, initial)
        registry = obj["candidates"]
        if len(registry) > MAX_DERIVED or len(initial) + len(registry) > MAX_DEFINITIONS:
            raise ValueError("Derived definition reservation exceeded")
        selection_sha = sha(derived_path)
    if registry:
        run_pool(tape, receipt, registry, make_windows(tape, "design"),
            args.runtime / f"design_{args.pool}", args, selection_sha=selection_sha)
    else:
        atomic_json(args.runtime / f"design_{args.pool}" / "completed_main_fresh.json", {
            "preregistration_commit": args.commit, "candidate_count": 0, "results": [],
            "scenario": "main", "state": "fresh", "calendar": [w.start_id for w in make_windows(tape, "design")]})


def metadata_for(registry):
    output = {}
    for row in registry:
        vector = {key: 0. for key in policies.ALL_KEYS}
        vector.update(row["exposure_vector"])
        gov = row["governor"]
        vector.update(__risk_fraction=float(gov.get("risk_fraction", 0.)),
            __aggregate_fraction=float(gov.get("aggregate_stop_fraction", 1.)),
            __buffer=float(gov.get("cushion_buffer", 0.)) / (2000. if row["account"] == 50 else 4000.),
            __target_guard=float(bool(gov.get("target_guard", False))))
        output[row["candidate_id"]] = {"family_id": row["family_id"], "exposure_vector": vector,
            "book_id": "+".join(sorted(row["book"])), "eligible": row["label"] != "EMPTY"}
    return output


def verified_pool_receipts(path, registry, args, selection_sha=None):
    obj = read_json(path)
    if obj["preregistration_commit"] != args.commit or obj["candidate_count"] != len(registry):
        raise ValueError("Design pool incomplete or from another preregistration")
    expected = {r["candidate_id"] for r in registry}
    if {r["candidate_id"] for r in obj["results"]} != expected:
        raise ValueError("Design pool candidate set mismatch")
    fingerprint = digest({"preregistration_commit": args.commit, "config_sha256": sha(args.config),
        "tape_receipt": read_json(args.runtime / "tape/prepare_receipt.json"),
        "selection_sha256": selection_sha})
    if registry and obj.get("study_fingerprint") != fingerprint:
        raise ValueError("Design pool settings/input fingerprint changed")
    by_id = {r["candidate_id"]: r for r in registry}
    annual = []
    for result in obj["results"]:
        if sha(ROOT / result["csv_path"]) != result["csv_sha256"]:
            raise ValueError("Design outcome CSV changed")
        policy = by_id[result["candidate_id"]]
        wanted = digest({"study": fingerprint, "policy": policy, "calendar": obj["calendar"],
            "scenario": "main", "costs": COSTS["main"], "state": "fresh"})
        if result["fingerprint"] != wanted:
            raise ValueError("Design candidate definition/input fingerprint mismatch")
        rows = read_cases(ROOT / result["csv_path"])
        if [r["start_id"] for r in rows] != obj["calendar"]:
            raise ValueError("Design candidate start calendar changed")
        recomputed = annual_summaries(rows, policy)
        if digest(recomputed) != digest(result["annual"]):
            raise ValueError("Design annual summaries disagree with saved outcomes")
        annual.extend(recomputed)
    return obj, annual


def select(args):
    _, initial = guard(args.config, args.commit)
    _, annual = verified_pool_receipts(args.runtime / "design_initial/completed_main_fresh.json", initial, args)
    registry = initial[:]
    if args.stage == "final":
        derived = checked_derived(args, initial)["candidates"]
        _, extra_annual = verified_pool_receipts(args.runtime / "design_derived/completed_main_fresh.json", derived,
            args, selection_sha=sha(BASE / "derived_policies.json"))
        registry += derived; annual += extra_annual
    ranked = selection.rank_design(annual, candidate_metadata=metadata_for(registry), max_nominees=3)
    by_id = {r["candidate_id"]: r for r in registry}
    nominees = [by_id[r["candidate_id"]] for account in ranked["accounts"].values() for r in account["nominees"]]
    output = {"preregistration_commit": args.commit, "stage": args.stage,
        "selection_years": list(DESIGN_YEARS), "selection_outcome_scope": "Monday starts; full expiry strictly before2023-01-01",
        "definitions_observed": len(registry), "nominees": nominees, "ranking": ranked,
        "annual_summary_sha256": digest(annual), "independent_economic_verification": "pending"}
    if args.stage == "initial":
        atomic_json(BASE / "design_selection_initial.json", output)
        derived = policies.derived_governors(nominees, initial)
        if len(derived) > MAX_DERIVED:
            raise ValueError("Reserved derived-definition count exceeded")
        atomic_json(BASE / "derived_policies.json", {"preregistration_commit": args.commit,
            "initial_selection_sha256": sha(BASE / "design_selection_initial.json"),
            "initial_definitions": len(initial), "derived_definitions": len(derived),
            "candidates": derived, "total_definitions": len(initial) + len(derived)})
    else:
        output["derived_registry_sha256"] = sha(BASE / "derived_policies.json")
        atomic_json(BASE / "frozen_validation_selection.json", output)
    print(json.dumps({"stage": args.stage, "definitions_observed": len(registry),
        "nominees": [{"candidate_id": r["candidate_id"], "account": r["account"], "label": r["label"]} for r in nominees],
        "next_boundary": "Commit generated selection artifacts before the next return stage."}))


def fee_metrics(summary, account):
    lo, hi = summary["pass_lower"], summary["pass_upper"]
    result = {"normalized_fee_per_pass_identified_lower": 1. / hi if hi > 0 else None,
        "normalized_fee_per_pass_identified_upper": 1. / lo if lo > 0 else None,
        "meaning": "fee/P(pass), descriptive renewal normalization; not an independent-retry forecast"}
    if int(account) == 150:
        result["conditional_249_fee_per_pass_lower"] = 249. / hi if hi > 0 else None
        result["conditional_249_fee_per_pass_upper"] = 249. / lo if lo > 0 else None
        result["fee_assumption"] = "Conditional150K purchase-price scenario only; excludes activation/reset/other charges."
    else:
        result["fee_assumption"] = "50K actual purchase price unverified; normalized cost only."
    return result


def validation_report(folder, registry, scenario, state):
    by_account = {}
    cases = {}
    for policy in registry:
        rows = read_cases(Path(folder) / scenario / state / f"{policy['candidate_id']}.csv")
        cases[policy["candidate_id"]] = rows
        cohorts = {}
        for label, group in [("all2023plus", rows),
            ("2023through2025", [r for r in rows if 2023 <= r["start_year"] <= 2025]),
            ("2026", [r for r in rows if r["start_year"] == 2026])]:
            if not group:
                cohorts[label] = {"n": 0, "status": "no_complete_expiry_starts"}; continue
            summary = selection.summarize_outcomes(group, time_key="calendar_days", start_key="start_id",
                candidate_id=policy["candidate_id"], account=f"{policy['account']}K")
            summary["fee_normalization"] = fee_metrics(summary, policy["account"])
            cohorts[label] = summary
        by_account.setdefault(f"{policy['account']}K", {})[policy["candidate_id"]] = {
            "label": policy["label"], "cohorts": cohorts}
    paired = []
    for policy in registry:
        if policy["label"] in ("CURRENT", "EMPTY"):
            continue
        baseline = next(p for p in registry if p["account"] == policy["account"] and p["label"] == "CURRENT")
        # Four/eight WEEKLY start observations, not four/eight weekdays. All
        # weekday point estimates remain above; no bar/return resampling occurs.
        c = [r for r in cases[policy["candidate_id"]] if r["start_weekday"] == 0]
        b = [r for r in cases[baseline["candidate_id"]] if r["start_weekday"] == 0]
        paired.append({"candidate_id": policy["candidate_id"], "baseline_id": baseline["candidate_id"],
            "scope": "Monday starts only; paired4/8weekly-start moving blocks;5000resamples",
            "bootstrap": selection.paired_block_bootstrap_sensitivity(c, b, blocks=(4, 8), n_reps=5000,
                seed=20261104, time_key="calendar_days", start_key="start_id")})
    report = {"historical_scope": "Previously seen2023+ historical validation, not fresh OOS",
        "scenario": scenario, "initial_state": state, "accounts": by_account, "paired": paired,
        "independent_economic_verification": "pending",
        "limits": ["Common OHLC chronology is a model, not recovered tick/broker order.",
            "Target/DLL liquidations use observed modeled marks and costs; no threshold snap fills.",
            "Unknown outcomes retained in denominators and identification bounds.",
            "Thin-cushion states are fresh synthetic states with zero initial profit, not live accounts."]}
    atomic_json(Path(folder) / f"report_{scenario}_{state}.json", report)
    return report


def validate(args):
    _, initial = guard(args.config, args.commit)
    frozen_path = BASE / "frozen_validation_selection.json"
    frozen = check_committed_selection(args, frozen_path)
    derived = checked_derived(args, initial)["candidates"]
    if sha(BASE / "derived_policies.json") != frozen["derived_registry_sha256"]:
        raise ValueError("Derived registry changed after frozen nomination")
    selected = frozen["nominees"]
    if any(sum(p["account"] == a for p in selected) > 3 for a in (50, 150)):
        raise ValueError("Nominee cap exceeded")
    registered = {p["candidate_id"]: p for p in initial + derived}
    if len({p["candidate_id"] for p in selected}) != len(selected):
        raise ValueError("Duplicate frozen nominees")
    for policy in selected:
        if policy["candidate_id"] not in registered or digest(policy) != digest(registered[policy["candidate_id"]]):
            raise ValueError("Frozen nominee is not an exact previously reserved definition")
    references = [r for r in initial if r["label"] in ("CURRENT", "EMPTY")]
    registry = {r["candidate_id"]: r for r in references + selected}
    registry = list(registry.values())
    tape, receipt = load_tape(args.runtime / "tape", args.config, args.commit)
    windows = make_windows(tape, "validation")
    folder = args.runtime / "validation"
    # Reference baselines use identical costs/state/calendar for each paired
    # comparison. Only frozen nominees are new strategies exposed to validation.
    scenarios = ["main", "low", "stress"] if selected else ["main"]
    states = list(STATE_FRACTIONS) if selected else ["fresh"]
    for scenario in scenarios:
        for state in states:
            run_pool(tape, receipt, registry, windows, folder, args, scenario, state,
                selection_sha=sha(frozen_path))
            validation_report(folder, registry, scenario, state)


def archive(args):
    guard(args.config, args.commit)
    files = sorted(p for p in args.runtime.rglob("*") if p.is_file() and
        p.suffix in (".csv", ".json") and "raw_links" not in p.parts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in files:
            z.write(p, str(p.relative_to(args.runtime)))
    atomic_json(args.output.with_suffix(".manifest.json"), {"preregistration_commit": args.commit,
        "archive_sha256": sha(args.output), "archive_bytes": args.output.stat().st_size,
        "files": {str(p.relative_to(args.runtime)): sha(p) for p in files},
        "note": "Exact case outcomes/receipts; tape arrays excluded, input/algorithm receipts retained."})


def selftest():
    """Synthetic allocation/window/receipt tests only; no owned market reads."""
    from types import SimpleNamespace
    fake = SimpleNamespace(keys=("VB", "EOS"), metadata={"point_values": [2.]},
        events=np.array([[0, 0, 0, 0, 1, 1, 100, 10, 99, 0],
                         [1, 1, 1, 0, 1, 1, 100, np.nan, 99, 0],
                         [2, 2, 1, 0, 1, 1, 100, 20, 99, 0]], float))
    p = {"book": {"VB": {"kind": "lots", "value": 3}, "EOS": {"kind": "risk", "value": 100}}}
    ev = requested_events(fake, p)
    assert ev[:, 8].tolist() == [3., -1., 2.]
    assert len(requested_events(fake, {"book": {}})) == 0
    assert requested_events(fake, {"book": {"VB": {"kind": "lots", "value": 2}}})[:, 2].tolist() == [0.]
    sample = [{"candidate_id": "x", "account": 50, "family_id": "a", "label": "EMPTY", "book": {},
        "exposure_vector": {}, "governor": {"target_guard": False}}]
    m = metadata_for(sample)["x"]
    assert not m["eligible"] and len(m["exposure_vector"]) == 22
    assert fee_metrics({"pass_lower": .4, "pass_upper": .5}, 50).get("conditional_249_fee_per_pass_lower") is None
    assert fee_metrics({"pass_lower": .4, "pass_upper": .5}, 150)["conditional_249_fee_per_pass_lower"] == 498.
    assert finite_json({"x": np.nan, "y": np.int64(2)}) == {"x": None, "y": 2}
    # Synthetic boundary-only calendar: no owned prices, ledgers or returns.
    days = [date(2018, 4, 2) + timedelta(days=i) for i in range((date(2026, 7, 7) - date(2018, 4, 2)).days + 1)]
    tt, ss, cc = [], [], []
    for d, day in enumerate(days):
        prior = day - timedelta(days=1)
        for stamp, cut in [(datetime(prior.year, prior.month, prior.day, 17, tzinfo=CT), False),
            (datetime(day.year, day.month, day.day, 15, 59, tzinfo=CT), True),
            (datetime(day.year, day.month, day.day, 17, tzinfo=CT), False)]:
            tt.append(stamp.timestamp()); ss.append(d); cc.append(cut)
    t = SimpleNamespace(dates=np.array([int(d.strftime("%Y%m%d")) for d in days]),
        session=np.array(ss), times=np.array(tt), node_rows=np.arange(len(tt)),
        prices=np.full((len(tt), 1), np.nan), cutoff=np.array(cc),
        segment_min=np.full((len(tt)-1, 1), np.nan), segment_max=np.full((len(tt)-1, 1), np.nan),
        segment_missing=np.ones((len(tt)-1, 1), bool), keys=tuple(policies.ALL_KEYS),
        events=np.empty((0, 10)), coverage=np.ones((18, len(days)), bool),
        trading_day=np.array([d.weekday() < 5 for d in days]),
        metadata={"ticks": [.25], "point_values": [2.]})
    design = make_windows(t, "design"); validation = make_windows(t, "validation")
    assert design[-1].start_id == "2022-11-28" and all(w.weekday == 0 for w in design)
    assert validation[-1].start_id == "2026-06-08"
    empty = {"candidate_id": "synthetic", "account": 50, "label": "EMPTY", "book": {}, "governor": {}}
    row, _ = run_window(t, np.empty((0, 10)), empty, design[0])
    assert row["status"] == "expire" and row["equity"] == 50000. and row["fill_count"] == 0
    assert row["calendar_days"] > 30. and row["observed_trading_sessions"] > 0
    print("runner selftest: PASS (synthetic inputs only; no owned market outcomes)")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("prepare", "screen", "select", "validate", "archive", "selftest"))
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--commit", help="Full exact frozen preregistration commit; required for all market commands")
    p.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    p.add_argument("--workers", type=int, choices=(1, 2, 3, 4), default=4)
    p.add_argument("--pool", choices=("initial", "derived"), default="initial")
    p.add_argument("--stage", choices=("initial", "final"), default="initial")
    p.add_argument("--selection-commit", help="Full commit containing exact generated/frozen selection artifacts")
    p.add_argument("--output", type=Path, default=ROOT / "agents/codex/results/eval_audit_20261104_cases.zip")
    args = p.parse_args()
    if args.command == "selftest":
        selftest(); return
    if not args.commit:
        p.error("--commit must identify the committed preregistration BEFORE any market work")
    if ((args.command == "screen" and args.pool == "derived") or
        (args.command == "select" and args.stage == "final") or args.command == "validate") and not args.selection_commit:
        p.error("--selection-commit is required at this committed selection boundary")
    globals()[args.command](args)


if __name__ == "__main__":
    main()
