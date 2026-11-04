"""Explicit, committed fixed-lot/DT-input amendment to the original eval audit.

Original a087708 code, inputs and2485design definitions remain immutable. This
wrapper adds a separately preregistered finite fixed-lot menu and factual source
exit-clock overlay. It does not turn missing ATR inputs into zero returns or
usable risk estimates. No amended market work is permitted without --commit.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace

import numpy as np

import codex_eval_run_20261104 as original
import codex_eval_fixed_arm_20261104 as fixed
import codex_eval_policies_20261104 as policies
import codex_eval_selection_20261104 as selection

ROOT = original.ROOT
BASE = original.BASE
ORIGINAL_COMMIT = "a087708b13697df4c3dd0b0814f98cb53a2b254a"
SCRIPT = "analysis/codex_eval_amended_run_20261104.py"
REGISTRY = BASE / "fixed_policies.json"
INITIAL = BASE / "amended_design_selection_initial.json"
DERIVED = BASE / "amended_derived_policies.json"
FINAL = BASE / "amended_frozen_validation_selection.json"
AMENDMENT_FILES = [SCRIPT, "analysis/codex_eval_fixed_arm_20261104.py",
    "analysis/codex_eval_source_overlay_20261104.py", str(REGISTRY.relative_to(ROOT)),
    "agents/codex/plans/eval_audit_fixed_arm_20261104.md",
    "agents/codex/evidence/eval_audit_fixed_arm_20261104.md"]
TAPE_FIELDS = ["prices", "times", "session", "events", "node_rows", "segment_min",
    "segment_max", "segment_missing", "eod", "cutoff", "session_start", "dates", "coverage", "trading_day"]


def original_args(args):
    return SimpleNamespace(config=args.config, commit=ORIGINAL_COMMIT, runtime=args.runtime,
        workers=args.workers, selection_commit=args.selection_commit)


def guard(args):
    _, initial = original.guard(args.config, ORIGINAL_COMMIT)
    for name in AMENDMENT_FILES:
        original.verify_file_at_commit(ROOT / name, args.commit)
    obj = original.read_json(REGISTRY)
    expected = fixed.generate(initial)
    if original.digest(obj) != original.digest(expected):
        raise ValueError("Fixed registry differs from deterministic amended generator")
    extra = obj["candidates"]
    ids = [r["candidate_id"] for r in initial + extra]
    if len(set(ids)) != len(ids):
        raise ValueError("Original and amended registry IDs overlap")
    if len(initial) + len(extra) + original.MAX_DERIVED > original.MAX_DEFINITIONS:
        raise ValueError("Shared original+amended+derived budget exceeds3000")
    return initial, extra


def load_overlay(args):
    dest = args.runtime / "fixed_arm/tape"
    tape, receipt = original.load_tape(dest, args.config, ORIGINAL_COMMIT)
    if receipt.get("amendment_commit") != args.commit:
        raise ValueError("Overlay tape belongs to another amendment")
    if receipt["original_prepare_receipt_sha256"] != original.sha(args.runtime / "tape/prepare_receipt.json"):
        raise ValueError("Original prepare receipt changed after overlay")
    for name, expected in receipt["source_overlay_artifacts"].items():
        if original.sha(args.runtime / "fixed_arm/source_overlay" / name) != expected:
            raise ValueError("Source overlay receipt changed: " + name)
    return tape, receipt


def overlay_receipt(args):
    """Hash check without loading market arrays, for source-free selection."""
    folder = args.runtime / "fixed_arm/tape"
    obj = original.read_json(folder / "prepare_receipt.json")
    if obj["preregistration_commit"] != ORIGINAL_COMMIT or obj["amendment_commit"] != args.commit:
        raise ValueError("Overlay receipt commit mismatch")
    if obj["config_sha256"] != original.sha(args.config):
        raise ValueError("Overlay receipt configuration changed")
    for name, expected in obj["artifacts"].items():
        if original.sha(folder / name) != expected:
            raise ValueError("Overlay artifact changed: " + name)
    for name, expected in obj["source_overlay_artifacts"].items():
        if original.sha(args.runtime / "fixed_arm/source_overlay" / name) != expected:
            raise ValueError("Source overlay evidence changed")
    if obj["original_prepare_receipt_sha256"] != original.sha(args.runtime / "tape/prepare_receipt.json"):
        raise ValueError("Original prepare receipt changed")
    return obj


def prepare(args):
    guard(args)
    dest = args.runtime / "fixed_arm/tape"
    if (dest / "prepare_receipt.json").exists():
        _, receipt = load_overlay(args)
        print(original.digest(receipt)); return
    from codex_eval_source_overlay_20261104 import repair_dt_time_exits
    source_dir = args.runtime / "tape"
    tape, _ = original.load_tape(source_dir, args.config, ORIGINAL_COMMIT)
    evidence_dir = args.runtime / "fixed_arm/source_overlay"
    tape, manifest = repair_dt_time_exits(tape, args.commit, evidence_dir, source_directory=source_dir)
    # A new tape is published; no original source/array/case file is overwritten.
    dest.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(dest / "tape.npz", **{n: getattr(tape, n) for n in TAPE_FIELDS})
    meta = dict(tape.metadata)
    meta.update(preregistration_commit=ORIGINAL_COMMIT, amendment_commit=args.commit,
        config_sha256=original.sha(args.config), markets=list(tape.markets), keys=list(tape.keys),
        rows=len(tape.times), source_events=len(tape.events), segments=len(tape.node_rows)-1)
    original.atomic_json(dest / "metadata.json", meta)
    receipt = {"preregistration_commit": ORIGINAL_COMMIT, "amendment_commit": args.commit,
        "config_sha256": original.sha(args.config), "original_prepare_receipt_sha256": original.sha(source_dir / "prepare_receipt.json"),
        "artifacts": {n: original.sha(dest / n) for n in ("tape.npz", "metadata.json")},
        "source_overlay_artifacts": {str(p.relative_to(evidence_dir)): original.sha(p)
            for p in sorted(evidence_dir.rglob("*")) if p.is_file()},
        "source_overlay_manifest_sha256": original.digest(manifest),
        "status": "Original inputs retained; factual DT clock correction applies to new arm/earned derivatives only; conditional model."}
    original.atomic_json(dest / "prepare_receipt.json", receipt)
    print(original.digest(receipt))


def context_sha(args, pool):
    obj = {"amendment_commit": args.commit, "pool": pool, "fixed_registry_sha256": original.sha(REGISTRY)}
    if pool == "derived":
        obj.update(derived_registry_sha256=original.sha(DERIVED), initial_selection_sha256=original.sha(INITIAL))
    return original.digest(obj)


def committed_artifact(args, path):
    original.verify_file_at_commit(path, args.selection_commit)
    obj = original.read_json(path)
    if obj["preregistration_commit"] != ORIGINAL_COMMIT or obj["amendment_commit"] != args.commit:
        raise ValueError("Selection artifact belongs to another original study/amendment")
    return obj


def checked_derived(args, joint):
    selected = committed_artifact(args, INITIAL)
    derived = committed_artifact(args, DERIVED)
    if derived["initial_selection_sha256"] != original.sha(INITIAL):
        raise ValueError("Derived registry is detached from its committed initial selection")
    by_id = {r["candidate_id"]: r for r in joint}
    nominees = selected["nominees"]
    if any(sum(r["account"] == a for r in nominees) > 3 for a in (50, 150)):
        raise ValueError("Nominee cap exceeded")
    if len({r["candidate_id"] for r in nominees}) != len(nominees):
        raise ValueError("Duplicate nominees")
    for policy in nominees:
        if policy["candidate_id"] not in by_id or original.digest(policy) != original.digest(by_id[policy["candidate_id"]]):
            raise ValueError("Initial nominee not an exact reserved policy")
    expected = policies.derived_governors(nominees, joint)
    if original.digest(expected) != original.digest(derived["candidates"]):
        raise ValueError("Amended derived menu is not the deterministic reserved menu")
    if derived["registered_before_derived"] != len(joint) or derived["derived_definitions"] != len(expected) or derived["total_definitions"] != len(joint)+len(expected):
        raise ValueError("Amended derived budget accounting mismatch")
    if len(expected) > original.MAX_DERIVED or len(joint)+len(expected) > original.MAX_DEFINITIONS:
        raise ValueError("Shared derived budget exceeded")
    return expected


def screen(args):
    initial, added = guard(args)
    rows = added if args.pool == "fixed" else checked_derived(args, initial+added)
    tape, receipt = load_overlay(args)
    windows = original.make_windows(tape, "design")
    folder = args.runtime / ("fixed_arm" if args.pool == "fixed" else "design_derived_amended")
    if rows:
        original.run_pool(tape, receipt, rows, windows, folder, original_args(args),
            selection_sha=context_sha(args, args.pool))
    else:
        original.atomic_json(folder / "completed_main_fresh.json", {
            "preregistration_commit": ORIGINAL_COMMIT, "candidate_count": 0, "results": [],
            "scenario": "main", "state": "fresh", "calendar": [w.start_id for w in windows]})


def verified_new_pool(args, registry, pool):
    folder = args.runtime / ("fixed_arm" if pool == "fixed" else "design_derived_amended")
    obj = original.read_json(folder / "completed_main_fresh.json")
    if obj["preregistration_commit"] != ORIGINAL_COMMIT or obj["candidate_count"] != len(registry):
        raise ValueError("Amended design pool incomplete/from another study")
    by_id = {r["candidate_id"]: r for r in registry}
    if {r["candidate_id"] for r in obj["results"]} != set(by_id):
        raise ValueError("Amended design candidate set mismatch")
    context = context_sha(args, pool)
    expected = original.digest({"preregistration_commit": ORIGINAL_COMMIT,
        "config_sha256": original.sha(args.config), "tape_receipt": overlay_receipt(args), "selection_sha256": context})
    if registry and obj["study_fingerprint"] != expected:
        raise ValueError("Amended pool source/settings fingerprint mismatch")
    annual = []
    for result in obj["results"]:
        policy = by_id[result["candidate_id"]]
        wanted = original.digest({"study": expected, "policy": policy, "calendar": obj["calendar"],
            "scenario": "main", "costs": original.COSTS["main"], "state": "fresh"})
        path = ROOT / result["csv_path"]
        if result["fingerprint"] != wanted or original.sha(path) != result["csv_sha256"]:
            raise ValueError("Amended candidate definition/outcome hash mismatch")
        cases = original.read_cases(path)
        if [r["start_id"] for r in cases] != obj["calendar"]:
            raise ValueError("Amended candidate start calendar mismatch")
        recomputed = original.annual_summaries(cases, policy)
        if original.digest(recomputed) != original.digest(result["annual"]):
            raise ValueError("Amended annual summaries disagree with preserved cases")
        annual.extend(recomputed)
    return obj, annual


def select(args):
    initial, added = guard(args)
    old_obj, annual = original.verified_pool_receipts(args.runtime / "design_initial/completed_main_fresh.json", initial, original_args(args))
    new_obj, new_annual = verified_new_pool(args, added, "fixed")
    if old_obj["calendar"] != new_obj["calendar"]:
        raise ValueError("Original and amended design calendars differ")
    joint = initial + added
    annual += new_annual
    registry = joint[:]
    if args.stage == "final":
        derived = checked_derived(args, joint)
        _, derivative_annual = verified_new_pool(args, derived, "derived")
        registry += derived; annual += derivative_annual
    ranked = selection.rank_design(annual, candidate_metadata=original.metadata_for(registry), max_nominees=3)
    by_id = {r["candidate_id"]: r for r in registry}
    nominees = [by_id[r["candidate_id"]] for account in ranked["accounts"].values() for r in account["nominees"]]
    output = {"preregistration_commit": ORIGINAL_COMMIT, "amendment_commit": args.commit,
        "stage": args.stage, "original_definitions_preserved": len(initial), "new_fixed_definitions": len(added),
        "definitions_observed": len(registry), "nominees": nominees, "ranking": ranked,
        "annual_summary_sha256": original.digest(annual), "overlay_prepare_receipt_sha256": original.sha(args.runtime / "fixed_arm/tape/prepare_receipt.json"),
        "source_scope": "Original design outcomes retained unchanged; newfixed/derived arm uses committed factualDTclockoverlay.",
        "independent_economic_verification": "pending"}
    if args.stage == "initial":
        original.atomic_json(INITIAL, output)
        derived = policies.derived_governors(nominees, joint)
        original.atomic_json(DERIVED, {"preregistration_commit": ORIGINAL_COMMIT,
            "amendment_commit": args.commit, "initial_selection_sha256": original.sha(INITIAL),
            "registered_before_derived": len(joint), "derived_definitions": len(derived),
            "total_definitions": len(joint)+len(derived), "candidates": derived})
    else:
        output["derived_registry_sha256"] = original.sha(DERIVED)
        original.atomic_json(FINAL, output)
    print(original.digest(output))


def validate(args):
    initial, added = guard(args)
    derived = checked_derived(args, initial+added)
    frozen = committed_artifact(args, FINAL)
    if frozen["derived_registry_sha256"] != original.sha(DERIVED):
        raise ValueError("Amended derived registry changed after final selection")
    if frozen["overlay_prepare_receipt_sha256"] != original.sha(args.runtime / "fixed_arm/tape/prepare_receipt.json"):
        raise ValueError("Source overlay changed after final selection")
    nominees = frozen["nominees"]
    registry = {p["candidate_id"]: p for p in initial+added+derived}
    if len({p["candidate_id"] for p in nominees}) != len(nominees) or any(sum(p["account"] == a for p in nominees)>3 for a in (50,150)):
        raise ValueError("Frozen nominee count/uniqueness failed")
    for policy in nominees:
        if policy["candidate_id"] not in registry or original.digest(policy) != original.digest(registry[policy["candidate_id"]]):
            raise ValueError("Final nominee differs from exact reserved definition")
    references = [p for p in initial if p["label"] in ("CURRENT", "EMPTY")]
    rows = list({p["candidate_id"]: p for p in references+nominees}.values())
    tape, receipt = load_overlay(args)
    windows = original.make_windows(tape, "validation")
    folder = args.runtime / "validation_amended"
    context = original.digest({"amendment_commit": args.commit, "selection_commit": args.selection_commit,
        "selection_sha256": original.sha(FINAL)})
    scenarios = list(original.COSTS) if nominees else ["main"]
    states = list(original.STATE_FRACTIONS) if nominees else ["fresh"]
    for scenario in scenarios:
        for state in states:
            original.run_pool(tape, receipt, rows, windows, folder, original_args(args), scenario, state, selection_sha=context)
            original.validation_report(folder, rows, scenario, state)


def selftest():
    # Registry construction only; no raw data, prepared tape or outcomes read.
    initial = original.read_json(BASE / "policies.json")["candidates"]
    added = fixed.generate(initial)["candidates"]
    assert len(initial)==2485 and len(added)==460 and len(initial)+len(added)+30==2975
    assert len({p["candidate_id"] for p in initial+added})==2945
    assert all(v["kind"]=="lots" for p in added for v in p["book"].values())
    assert all(not p["governor"]["target_guard"] for p in added)
    vector = original.metadata_for(added)
    assert all(len(m["exposure_vector"])==22 for m in vector.values())
    print("amendment wrapper synthetic/schema tests: PASS; no market/outcome reads")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "screen", "select", "validate", "archive", "selftest"))
    parser.add_argument("--commit", help="Full NEW amendment preregistration SHA; originala087guard also applies")
    parser.add_argument("--selection-commit")
    parser.add_argument("--config", type=Path, default=original.DEFAULT_CONFIG)
    parser.add_argument("--runtime", type=Path, default=original.DEFAULT_RUNTIME)
    parser.add_argument("--workers", type=int, choices=(1,2,3,4), default=4)
    parser.add_argument("--pool", choices=("fixed", "derived"), default="fixed")
    parser.add_argument("--stage", choices=("initial", "final"), default="initial")
    parser.add_argument("--output", type=Path, default=ROOT / "agents/codex/results/eval_audit_20261104_cases.zip")
    args=parser.parse_args()
    if args.command=="selftest":
        selftest(); return
    if not args.commit:
        parser.error("--commit must identify the exact committed NEW amendment before its market work")
    if (args.command=="validate" or (args.command=="screen" and args.pool=="derived") or (args.command=="select" and args.stage=="final")) and not args.selection_commit:
        parser.error("This phase requires exact --selection-commit")
    if args.command=="archive":
        guard(args)
        obj=original_args(args);obj.output=args.output
        original.archive(obj)
    else:
        globals()[args.command](args)


if __name__=="__main__":
    main()
