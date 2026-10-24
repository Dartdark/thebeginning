"""Pinned current-plan adapter for the preregistered ORPullback comparison.

Importing this module does not load prices, replay strategies, or score accounts.
``prepare_sources`` materializes exact Git blobs in the ignored task runtime.
``build_current_plan`` is an explicitly gated return-producing operation: call it
only after the preregistration commit, using the parent's authorization.

The adapter reuses Claude's fast_plan_lab, add_moc_mes, Relative Strength replay,
Lab.real_fees and funded account simulator from one pinned revision. It never
calls a research helper's __main__ block or rebuilds a grid cache.
"""
from __future__ import annotations

import ast
import contextlib
import hashlib
import importlib
import importlib.abc
import importlib.util
import json
import pickle
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PINNED_REF = "a67035be4189b493098c80f1def979348520fd5d"
DEFAULT_RUNTIME = ROOT / "agents/codex/runtime/or_pullback_plan_analysis"
CURRENT_PLAN = {
    "VB_N": 2, "VB_F": 1, "ONB_ML2_MC": ("risk", 400),
    "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2,
    "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2,
    "MOC_MES": 2, "RS_L": 1,
}
SEED_MODULES = (
    "fc_2b_bench", "funded_bootstrap", "funded_lab", "funded_sim",
    "portfolio", "grid", "grid24", "relative_strength_test",
    "s_rank_es_round1_test", "cl_forced_flows_test",
)
BASELINE_LIMITS = [
    "CLS retains fast_plan_lab's whole-Monday constant adverse-path approximation.",
    "MOC_MES retains add_moc_mes's close-based intraday path approximation.",
    "Real-fee increments follow Lab.real_fees: each day's total fee is present from its first entry.",
    "RS uses the unchanged pinned Python baseline, independently reconciled with its committed ledger.",
]


def _git(*args, root=ROOT):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def prepare_sources(runtime=DEFAULT_RUNTIME, *, root=ROOT, ref=PINNED_REF):
    """Copy only the transitive Python dependencies, without importing them.

    Exact bytes and Git blob IDs are recorded. Standard-library/third-party
    imports are left to the configured Python environment. This performs no
    market-data reads and is safe before the return gate opens.
    """
    runtime = Path(runtime).resolve()
    root = Path(root).resolve()
    if not runtime.is_relative_to(root / "agents/codex/runtime"):
        raise ValueError("Pinned runtime must remain under agents/codex/runtime")
    names = _git("ls-tree", "-r", "--name-only", ref, "analysis", root=root).decode().splitlines()
    available = {Path(p).stem: p for p in names
                 if p.startswith("analysis/") and p.count("/") == 1 and p.endswith(".py")}
    runtime.mkdir(parents=True, exist_ok=True)
    pending, manifest = list(SEED_MODULES), {}
    while pending:
        name = pending.pop()
        if name in manifest:
            continue
        source_path = available[name]
        data = _git("show", f"{ref}:{source_path}", root=root)
        tree = ast.parse(data.decode("utf-8-sig"), filename=source_path)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        pending.extend(sorted(imports.intersection(available).difference(manifest)))
        (runtime / f"{name}.py").write_bytes(data)
        manifest[name] = {
            "repository_path": source_path,
            "git_blob": _git("rev-parse", f"{ref}:{source_path}", root=root).decode().strip(),
            "sha256": _sha(data), "bytes": len(data),
        }
    inputs = {}
    for source_path in ("checks/candidates/relative_strength/RelStrength_v3.txt",
                        "checks/candidates/relative_strength/trades.csv"):
        data = _git("show", f"{ref}:{source_path}", root=root)
        target = "RS_source.txt" if source_path.endswith(".txt") else "RS_reference.csv"
        (runtime / target).write_bytes(data)
        inputs[target] = {"repository_path": source_path, "sha256": _sha(data),
                          "git_blob": _git("rev-parse", f"{ref}:{source_path}", root=root).decode().strip()}
    result = {"ref": ref, "modules": manifest, "inputs": inputs}
    (runtime / "manifest.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


class _PinnedFinder(importlib.abc.MetaPathFinder):
    def __init__(self, directory, names):
        self.directory, self.names = Path(directory), set(names)

    def find_spec(self, fullname, path=None, target=None):
        if fullname in self.names:
            return importlib.util.spec_from_file_location(fullname, self.directory / f"{fullname}.py")
        return None


@contextlib.contextmanager
def pinned_imports(runtime, scratch):
    """Enforce the pin even when legacy modules prepend 'analysis' to sys.path.

    Canonical module names are temporarily replaced so old grid/lab pickles use
    the pinned class definitions. Imported module objects remain usable in the
    returned bundle; the caller's prior sys.modules/path/argv state is restored.
    """
    runtime, scratch = Path(runtime), Path(scratch)
    manifest = json.loads((runtime / "manifest.json").read_text(encoding="utf-8"))
    if manifest["ref"] != PINNED_REF:
        raise ValueError("Unexpected current-plan source revision")
    for name, meta in manifest["modules"].items():
        if _sha((runtime / f"{name}.py").read_bytes()) != meta["sha256"]:
            raise ValueError(f"Pinned dependency was edited: {name}")
    for name, meta in manifest["inputs"].items():
        if _sha((runtime / name).read_bytes()) != meta["sha256"]:
            raise ValueError(f"Pinned baseline input was edited: {name}")
    names = set(manifest["modules"])
    previous_modules = {name: sys.modules.pop(name) for name in names if name in sys.modules}
    previous_path, previous_argv = sys.path[:], sys.argv
    finder = _PinnedFinder(runtime, names)
    sys.meta_path.insert(0, finder)
    sys.path.insert(0, str(runtime))
    sys.argv = [str(Path(__file__)), str(scratch)]
    try:
        yield manifest
    finally:
        sys.meta_path.remove(finder)
        sys.path[:] = previous_path
        sys.argv = previous_argv
        for name in names:
            sys.modules.pop(name, None)
        sys.modules.update(previous_modules)


def funded_plans(candidate="ORPB"):
    """Frozen main family: add 1/2 MNQ; replace the whole VB slot; empty control."""
    base = dict(CURRENT_PLAN)
    empty = {k: v for k, v in base.items() if k not in ("VB_N", "VB_F")}
    return {
        "BASE": base,
        "ADD_ORPB_1": {**base, candidate: 1},
        "ADD_ORPB_2": {**base, candidate: 2},
        "EMPTY_VB": empty,
        "REPLACE_VB_ORPB_2": {**empty, candidate: 2},
    }


def _reconcile_rs(replay, reference, last_date):
    """Check frozen dates/sides/kinds/prices/net; no silent exceptions."""
    a = replay.copy()
    a["date"] = pd.to_datetime(a.date).dt.normalize()
    a = a[(a.date >= "2018-01-01") & (a.date <= last_date)].copy()
    a["net"] = a.pnl
    b = pd.read_csv(reference, parse_dates=["date"])
    b = b[(b.date >= "2018-01-01") & (b.date <= last_date)].copy()
    if a.date.duplicated().any() or b.date.duplicated().any():
        raise ValueError("RS baseline unexpectedly has multiple same-date entries")
    fields = ["date", "side", "kind", "entry", "exit", "net"]
    joined = a[fields].merge(b[fields], on="date", how="outer", suffixes=("_replay", "_reference"), indicator=True)
    both = joined._merge == "both"
    good = both.copy()
    for key in ("side", "kind"):
        good &= joined[f"{key}_replay"] == joined[f"{key}_reference"]
    for key in ("entry", "exit", "net"):
        good &= np.isclose(joined[f"{key}_replay"], joined[f"{key}_reference"], rtol=0, atol=1e-7)
    audit = {"replay_rows": len(a), "reference_rows": len(b), "matched_rows": int(both.sum()),
             "exact_rows": int(good.sum()), "mismatch_rows": int((~good).sum()),
             "last_cache_date": str(pd.Timestamp(last_date).date()), "tolerance": 1e-7}
    return a, audit, joined[~good].copy()


def _count_metadata(lab, name, trades):
    """Recover fee counts for legacy caches without rebuilding stored paths."""
    total_rows = len(lab.g.ts)
    qty = trades["qty"].to_numpy() if "qty" in trades else np.ones(len(trades))
    day = trades.day.to_numpy(int)
    lab.N[name] = np.bincount(day, weights=qty, minlength=total_rows)[lab.tr]
    first = np.full(total_rows, lab.W[name].shape[1], dtype=int)
    np.minimum.at(first, day, trades.j0.to_numpy(int))
    lab.J0[name] = first[lab.tr]


def build_current_plan(scratch, *, preregistration_commit, authorized_returns=False,
                       runtime=DEFAULT_RUNTIME, audit_dir=None, fee=1.04, plan_cache=None):
    """Construct only the frozen current roster, using existing ignored caches.

    No candidate is replayed here. RS is the unchanged baseline reconstruction
    authorized by the preregistration; it must reconcile before account scoring.
    Cache files are never rewritten. Price-producing helpers run only past the
    explicit gate below. audit_dir is strongly recommended for the final record.
    """
    if not authorized_returns:
        raise PermissionError("Return gate is closed; commit preregistration and obtain parent authorization first")
    if not preregistration_commit:
        raise ValueError("A committed preregistration is required")
    _git("cat-file", "-e", f"{preregistration_commit}^{{commit}}")
    scratch, runtime = Path(scratch).resolve(), Path(runtime).resolve()
    for name in ("lab.pkl", "g24.pkl", "ge.pkl", "cl.pkl", "s_rank_gap2.pkl", "single_print_sessions.pkl"):
        if not (scratch / name).is_file():
            raise FileNotFoundError(f"Required existing cache missing; do not rebuild automatically: {scratch / name}")
    if not (runtime / "manifest.json").is_file():
        prepare_sources(runtime)
    out = Path(audit_dir) if audit_dir else None
    if out:
        out.mkdir(parents=True, exist_ok=True)
    with pinned_imports(runtime, scratch) as manifest:
        fast = importlib.import_module("fc_2b_bench")
        fb = importlib.import_module("funded_bootstrap")
        fl = importlib.import_module("funded_lab")
        pf = importlib.import_module("portfolio")
        fs = importlib.import_module("funded_sim")
        build = importlib.import_module("build_lab")
        rs = importlib.import_module("relative_strength_test")
        rs.SP = str(scratch) + "/"
        rs.CODE = str(runtime / "RS_source.txt")
        days, nq, es = rs.load()
        replay = rs.trades(days, nq, rs.signals(days, nq, es))
        with (scratch / "g24.pkl").open("rb") as handle:
            grid = pickle.load(handle)
        last_date = pd.DatetimeIndex(grid.ts[grid.trading]).max().normalize()
        replay, rs_audit, mismatch = _reconcile_rs(replay, runtime / "RS_reference.csv", last_date)
        if out:
            replay.to_csv(out / "baseline_rs_replay.csv", index=False)
            mismatch.to_csv(out / "baseline_rs_mismatches.csv", index=False)
            (out / "baseline_rs_audit.json").write_text(json.dumps(rs_audit, indent=2) + "\n", encoding="utf-8")
        del days, nq, es, grid
        if rs_audit["mismatch_rows"]:
            raise ValueError(f"Frozen RS baseline mismatch; audit and preregister exceptions before continuing: {rs_audit}")
        lab = fast.fast_plan_lab(str(scratch) + "/")
        fb.add_moc_mes(lab, str(scratch) + "/")
        replay["kind"] = replay.kind.map({"stop": 0, "target": 1, "flat": 2})
        if replay.kind.isna().any():
            raise ValueError("Unknown frozen RS exit kind")
        lab.add("RS_L", replay[replay.side > 0].reset_index(drop=True))
        # Older lab.pkl versions lack N/J0. Recover exact trade counts from the
        # same MC lists, rather than incorrectly charge one fee per traded day.
        recovered = []
        for name in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC"):
            if name not in lab.N:
                _count_metadata(lab, name, pf.load_mc(lab.g, build.REPORTS[name][0]))
                recovered.append(name)
        dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
        flags = pd.read_pickle(scratch / "single_print_sessions.pkl").flag.reindex(dates).fillna(False).to_numpy(bool)
        for name, use in (("VB_F", flags), ("VB_N", ~flags)):
            lab.N[name] = lab.N["VB"] * use
            lab.J0[name] = lab.J0["VB"].copy()
        fee_totals = {}
        for name in CURRENT_PLAN:
            baseline_fee = 0.50 if name == "MOC_MES" else 0.725
            fee_totals.update(lab.real_fees(float(fee) - baseline_fee, [name]))
        provenance = {"ref": PINNED_REF, "preregistration_commit": preregistration_commit,
                      "fee_per_micro_round_trip": fee, "sources": manifest,
                      "rs_reconciliation": rs_audit, "legacy_fee_count_metadata_recovered": recovered,
                      "extra_fee_totals_per_micro": fee_totals, "baseline_limits": BASELINE_LIMITS,
                      "plan": CURRENT_PLAN, "cache_files_rewritten": False}
        if out:
            (out / "current_plan_manifest.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
        if plan_cache:
            target = Path(plan_cache).resolve()
            if not target.is_relative_to(ROOT / "agents/codex/runtime"):
                raise ValueError("Reconstructed plan cache must remain in ignored task runtime")
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("wb") as handle:
                pickle.dump(lab, handle, protocol=4)
        return SimpleNamespace(lab=lab, base=dict(CURRENT_PLAN), bootstrap=fb,
                               funded_sim=fs, portfolio=pf, funded_lab=fl,
                               source_manifest=provenance)


def load_prepared_plan(plan_cache, *, scratch, runtime=DEFAULT_RUNTIME, manifest_path):
    """Read the task's prepared lab with its pinned classes; do not replay it."""
    provenance = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if provenance["ref"] != PINNED_REF:
        raise ValueError("Prepared plan revision mismatch")
    with pinned_imports(runtime, scratch):
        fl = importlib.import_module("funded_lab")
        fb = importlib.import_module("funded_bootstrap")
        fs = importlib.import_module("funded_sim")
        pf = importlib.import_module("portfolio")
        with Path(plan_cache).open("rb") as handle:
            lab = pickle.load(handle)
        return SimpleNamespace(lab=lab, base=dict(CURRENT_PLAN), bootstrap=fb,
                               funded_sim=fs, portfolio=pf, funded_lab=fl,
                               source_manifest=provenance)


def evaluation_parts(scratch, *, preregistration_commit, authorized_returns=False,
                     runtime=DEFAULT_RUNTIME, fee=1.04, grid=None):
    """The unchanged latest real_fee_bench.combine baseline as reusable pieces.

    Returns per-one-MNQ adverse/closed paths and the plan's fixed/risk quantities.
    The caller may add its preregistered candidate and reuse challenge(). No
    challenge, variant search or candidate replay is executed by this helper.
    """
    if not authorized_returns or not preregistration_commit:
        raise PermissionError("Committed preregistration and return authorization required")
    _git("cat-file", "-e", f"{preregistration_commit}^{{commit}}")
    scratch = Path(scratch).resolve()
    with pinned_imports(runtime, scratch):
        pf = importlib.import_module("portfolio")
        fl = importlib.import_module("funded_lab")
        build = importlib.import_module("build_lab")
        bridge = importlib.import_module("bridge_monday_confirm")
        combine = importlib.import_module("combine_levers_test")
        if grid is None:
            with (scratch / "g24.pkl").open("rb") as handle:
                grid = pickle.load(handle)
        tr = grid.trading
        atr = grid.daily_atr(15)[tr]
        old_cost = pf.COST
        pf.COST = fee * 10.0
        try:
            ledgers = {
                "VB": fl.with_slippage(pf.load_mc(grid, build.REPORTS["VB"][0])),
                "ONB30": fl.with_slippage(pf.load_mc(grid, combine.ONB30)),
                "MON_BR": bridge.load_bridge_mc(grid),
                "EOS": fl.with_slippage(pf.load_mc(grid, build.REPORTS["EOS"][0])),
            }
            parts = {name: tuple(a[tr] / 10.0 for a in pf.paths(grid, ledger))
                     for name, ledger in ledgers.items()}
        finally:
            pf.COST = old_cost
        def risk(dollars, multiplier):
            return np.floor(dollars / (np.nan_to_num(multiplier * atr, nan=1e12) * 2.0))[:, None]
        quantity = {"VB": 8.0, "ONB30": risk(1100, 0.25),
                    "MON_BR": 2.0, "EOS": risk(500, build.REPORTS["EOS"][1])}
        return SimpleNamespace(g=grid, tr=tr, dates=pd.DatetimeIndex(grid.ts[tr]),
                               parts=parts, quantities=quantity, challenge=combine.challenge,
                               max_days=combine.MAXD, source_ref=PINNED_REF, fee=fee)
