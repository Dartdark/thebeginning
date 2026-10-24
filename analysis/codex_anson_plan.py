"""Pinned Apex plan adapters for the Anson source review.

Import and prepare_sources perform no return calculation. Loading the prepared
50K lab reuses existing paths. New RS-both/DT baseline paths and evaluation
paths are explicitly gated by a committed preregistration and authorization.
Personal-account loading is owned by the separate personal adapter.
"""
from __future__ import annotations

import ast
import contextlib
import importlib
import json
import pickle
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import codex_or_pullback_plan as P

ROOT = P.ROOT
sys.path.insert(0, str(ROOT / "agents/codex/runtime/or_pullback_python"))
PIN = "e34d71cd3537a9f019d2521e280fc92f3ffdb4c6"
RUNTIME = ROOT / "agents/codex/runtime/anson_plan_analysis"
BASE_CACHE = ROOT / "agents/codex/runtime/or_pullback_current_lab.pkl"
BASE_SHA = "699057ea248172f91ee64f7f3c4aad72347434063e64fab836576da53877067b"
BASE_MANIFEST = ROOT / "analysis/outputs/codex_or_pullback/baseline/current_plan_manifest.json"
RS_REPLAY = ROOT / "analysis/outputs/codex_or_pullback/baseline/baseline_rs_replay.csv"
ADDITIONS = ROOT / "agents/codex/runtime/anson_plan_additions.pkl"
EXTRA_MODULES = ("funded_sim150", "plan_150k_test", "dual_thrust_test", "dual_thrust_bench")
INPUTS = {"DT_reference.csv": "checks/candidates/dual_thrust/trades.csv",
          "DT_timed.csv": "checks/candidates/dual_thrust/trades_replica.csv",
          "funded_plan.md": "funded_strategies/FUNDED_PLAN.md"}


def file_sha(path):
    import hashlib
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def dump(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, default=str)+"\n", encoding="utf-8")


def prepare_sources(runtime=RUNTIME):
    """Snapshot exact current sources; verify all 27 cached-plan dependencies."""
    runtime = Path(runtime).resolve()
    old = json.loads(BASE_MANIFEST.read_text(encoding="utf-8"))
    manifest = P.prepare_sources(runtime, ref=PIN)
    checks = []
    for name, meta in old["sources"]["modules"].items():
        current = manifest["modules"].get(name)
        same = current is not None and current["git_blob"] == meta["git_blob"]
        checks.append(dict(module=name, older_blob=meta["git_blob"],
                           current_blob=current["git_blob"] if current else None, unchanged=same))
    if len(checks) != 27 or not all(x["unchanged"] for x in checks):
        raise ValueError("Prepared 50K baseline dependencies changed")
    for name, meta in old["sources"]["inputs"].items():
        if manifest["inputs"][name]["git_blob"] != meta["git_blob"]:
            raise ValueError("Frozen RS source/reference changed")
    paths = P._git("ls-tree", "-r", "--name-only", PIN, "analysis").decode().splitlines()
    available = {Path(p).stem: p for p in paths if p.count("/") == 1 and p.endswith(".py")}
    pending = list(EXTRA_MODULES)
    while pending:
        name = pending.pop()
        if name in manifest["modules"]:
            continue
        path = available[name]
        data = P._git("show", f"{PIN}:{path}")
        imports = set()
        for node in ast.walk(ast.parse(data.decode("utf-8-sig"))):
            if isinstance(node, ast.Import):
                imports.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        pending += sorted(imports.intersection(available).difference(manifest["modules"]))
        (runtime / f"{name}.py").write_bytes(data)
        manifest["modules"][name] = dict(repository_path=path, bytes=len(data), sha256=P._sha(data),
            git_blob=P._git("rev-parse", f"{PIN}:{path}").decode().strip())
    for name, path in INPUTS.items():
        data = P._git("show", f"{PIN}:{path}")
        (runtime / name).write_bytes(data)
        manifest["inputs"][name] = dict(repository_path=path, sha256=P._sha(data),
            git_blob=P._git("rev-parse", f"{PIN}:{path}").decode().strip())
    manifest["prepared_baseline_dependencies"] = checks
    manifest["baseline_rebuilt"] = False
    dump(runtime / "manifest.json", manifest)
    return manifest


@contextlib.contextmanager
def pinned_imports(scratch, runtime=RUNTIME):
    """Enforce the latest exact source pin for legacy import names/pickles."""
    runtime = Path(runtime)
    manifest = json.loads((runtime / "manifest.json").read_text(encoding="utf-8"))
    if manifest["ref"] != PIN:
        raise ValueError("Unexpected Anson plan pin")
    for name, meta in manifest["modules"].items():
        if file_sha(runtime / f"{name}.py") != meta["sha256"]:
            raise ValueError(f"Edited pinned module {name}")
    for name, meta in manifest["inputs"].items():
        if file_sha(runtime / name) != meta["sha256"]:
            raise ValueError(f"Edited pinned input {name}")
    names = set(manifest["modules"])
    prior = {n: sys.modules.pop(n) for n in names if n in sys.modules}
    previous_path, previous_argv = sys.path[:], sys.argv
    finder = P._PinnedFinder(runtime, names)
    sys.meta_path.insert(0, finder)
    sys.path.insert(0, str(runtime))
    sys.argv = [str(Path(__file__)), str(Path(scratch).resolve())]
    try:
        yield manifest
    finally:
        sys.meta_path.remove(finder)
        sys.path[:] = previous_path
        sys.argv = previous_argv
        for name in names:
            sys.modules.pop(name, None)
        sys.modules.update(prior)


def authorize(preregistration_commit, authorized_returns):
    if not authorized_returns or not preregistration_commit:
        raise PermissionError("Committed preregistration and parent authorization required")
    P._git("cat-file", "-e", f"{preregistration_commit}^{{commit}}")


def funded_plans():
    """Current published rosters; actual integer rounding stays in simulators.

    150K retains the published bench's fractional full-size bases (e.g. flagged
    VB 1.5), then floor(base*f). This is explicit rather than silently rounding
    all full-size inputs before applying the cushion multiplier.
    """
    fifty = dict(P.CURRENT_PLAN)
    onefifty = {k: (("risk", v[1]*1.5) if isinstance(v, tuple) else v*1.5)
                for k, v in fifty.items() if k != "RS_L"}
    onefifty.update(RS=1, DT=2)
    return {"50K_funded": fifty, "150K_funded": onefifty}


def _dt_reconcile(t, reference, last_date):
    a = t[(t.date >= "2018-01-01") & (t.date <= last_date)].copy()
    b = pd.read_csv(reference, parse_dates=["date"])
    b = b[(b.date >= "2018-01-01") & (b.date <= last_date)].copy()
    if a.date.duplicated().any() or b.date.duplicated().any():
        raise ValueError("DT baseline unexpectedly has multiple daily trades")
    fields = ["date", "side", "entry", "exit", "kind", "net"]
    joined = a[fields].merge(b[fields], on="date", how="outer", suffixes=("_replay", "_reference"), indicator=True)
    ok = joined._merge == "both"
    for key in ("side", "kind"):
        ok &= joined[f"{key}_replay"] == joined[f"{key}_reference"]
    for key in ("entry", "exit", "net"):
        ok &= np.isclose(joined[f"{key}_replay"], joined[f"{key}_reference"], rtol=0, atol=1e-7)
    audit = dict(replay_rows=len(a), reference_rows=len(b), exact_rows=int(ok.sum()),
                 mismatch_rows=int((~ok).sum()), tolerance=1e-7)
    return a, audit, joined.loc[~ok]


def load_funded(scratch, *, preregistration_commit, authorized_returns=False,
                runtime=RUNTIME, cache=BASE_CACHE, additions_cache=ADDITIONS,
                audit_dir=None, fee=1.04, plan_cache=None):
    """Reuse prepared 50K paths, add only immutable current RS-both/DT pieces.

    The committed timed DT replica must match its committed reference in every
    listed field. No DT signal rerun or price-matched timestamps are needed.
    Cached additions avoid repeating that baseline path construction.
    """
    authorize(preregistration_commit, authorized_returns)
    scratch, runtime, cache = Path(scratch).resolve(), Path(runtime).resolve(), Path(cache).resolve()
    if file_sha(cache) != BASE_SHA:
        raise ValueError("Prepared current-plan cache changed")
    if not (runtime / "manifest.json").is_file():
        prepare_sources(runtime)
    with pinned_imports(scratch, runtime) as manifest:
        fs = importlib.import_module("funded_sim")
        fs150 = importlib.import_module("funded_sim150")
        fb = importlib.import_module("funded_bootstrap")
        with cache.open("rb") as handle:
            lab = pickle.load(handle)
        additions_cache = Path(additions_cache).resolve()
        signature = dict(ref=PIN, prepared_cache=BASE_SHA, rs_replay=file_sha(RS_REPLAY),
                         dt_reference=file_sha(runtime / "DT_reference.csv"),
                         dt_timed_ledger=file_sha(runtime / "DT_timed.csv"), fee=1.04)
        if additions_cache.is_file():
            with additions_cache.open("rb") as handle:
                extra = pickle.load(handle)
            if extra["signature"] != signature:
                raise ValueError("Cached baseline additions belong to another frozen context")
            for name in ("RS", "DT"):
                for field in ("W", "C", "N", "J0"):
                    getattr(lab, field)[name] = extra[field][name]
            audit = extra["audit"]
            cached = True
        else:
            rs = pd.read_csv(RS_REPLAY, parse_dates=["date"])
            rs["kind"] = rs.kind.map({"stop": 0, "target": 1, "flat": 2})
            if rs.kind.isna().any():
                raise ValueError("Unknown frozen RS kind")
            lab.add("RS", rs)
            lab.real_fees(1.04-.725, ["RS"])
            expected_rs = np.bincount(rs.day.to_numpy(int), weights=rs.net.to_numpy()/10-.315,
                                     minlength=len(lab.g.ts))[lab.tr]
            np.testing.assert_allclose(lab.C["RS"], expected_rs, rtol=0, atol=1e-7)
            dt = importlib.import_module("dual_thrust_test")
            t = pd.read_csv(runtime / "DT_timed.csv", parse_dates=["date"])
            t, audit, mismatch = _dt_reconcile(t, runtime / "DT_reference.csv",
                                              pd.DatetimeIndex(lab.g.ts[lab.tr]).max())
            audit["source"] = "committed timed replica, no signal rerun or price matching"
            entry_hm, signal_hm = t.entry_time.to_numpy(int), t.sig_time.to_numpy(int)
            np.testing.assert_array_equal(entry_hm//100*60+entry_hm%100,
                                          signal_hm//100*60+signal_hm%100+1)
            if audit_dir:
                Path(audit_dir).mkdir(parents=True, exist_ok=True)
                mismatch.to_csv(Path(audit_dir) / "dt_baseline_mismatches.csv", index=False)
                t.to_csv(Path(audit_dir) / "dt_baseline_replay.csv", index=False)
                dump(Path(audit_dir) / "dt_baseline_audit.json", audit)
            if audit["mismatch_rows"]:
                raise ValueError(f"DT baseline mismatch: {audit}")
            lab.add("DT", dt.lab_trades(lab.g, t))
            lab.real_fees(1.04-.725, ["DT"])
            mapped = pd.Index(lab.g.ts).get_indexer(t.date)
            if (mapped < 0).any():
                raise ValueError("DT date is absent from existing grid")
            expected_dt = np.bincount(mapped, weights=t.net.to_numpy()/10-.315,
                                     minlength=len(lab.g.ts))[lab.tr]
            np.testing.assert_allclose(lab.C["DT"], expected_dt, rtol=0, atol=1e-7)
            audit["daily_real_fee_C_matches_committed_ledger"] = True
            extra = dict(signature=signature, audit=audit,
                         **{f: {k: getattr(lab, f)[k] for k in ("RS", "DT")}
                            for f in ("W", "C", "N", "J0")})
            if not additions_cache.is_relative_to(ROOT / "agents/codex/runtime"):
                raise ValueError("Baseline additions must stay in ignored task runtime")
            additions_cache.parent.mkdir(parents=True, exist_ok=True)
            with additions_cache.open("wb") as handle:
                pickle.dump(extra, handle, protocol=4)
            cached = False
        if fee != 1.04:
            lab.real_fees(float(fee)-1.04, list(set(P.CURRENT_PLAN) | {"RS", "DT"}))
        metadata = dict(ref=PIN, prepared_base_sha256=BASE_SHA, additions_signature=signature,
                        additions_cache_sha256=file_sha(additions_cache), reused_additions=cached,
                        fee=fee, dt_reconciliation=audit, plan=funded_plans(),
                        cushion={"50K_funded": dict(fmin=.5, fmax=1., ref=1500.),
                                 "150K_funded": dict(fmin=.5, fmax=1., ref=3000.)},
                        baseline_limits=P.BASELINE_LIMITS,
                        integer_rule="floor(base_quantity*cushion_multiplier+1e-9)")
        if audit_dir:
            dump(Path(audit_dir) / "funded_baseline_manifest.json", metadata)
        if plan_cache:
            target = Path(plan_cache).resolve()
            if not target.is_relative_to(ROOT / "agents/codex/runtime"):
                raise ValueError("Prepared baseline must stay in ignored task runtime")
            with target.open("wb") as handle:
                pickle.dump(lab, handle, protocol=4)
        return SimpleNamespace(lab=lab, plans=funded_plans(), funded50=fs, funded150=fs150,
                               bootstrap=fb, metadata=metadata, sources=manifest)


def evaluation_parts(scratch, *, preregistration_commit, authorized_returns=False,
                     runtime=RUNTIME, fee=1.04, grid=None):
    """Per-MNQ shared components and correctly integer-sized 50K/150K plans.

    Correct 150K inputs are VB20, Bridge5, ONB2750 and EOS1250 risk; risk
    quantities floor after scaling dollars. Older studies instead multiplied
    already-floored 50K quantities by2.5; retain that size audit explicitly.
    """
    authorize(preregistration_commit, authorized_returns)
    # The prepared helper's 27 source dependencies are byte-identical to PIN.
    fifty = P.evaluation_parts(scratch, preregistration_commit=preregistration_commit,
        authorized_returns=True, fee=fee, grid=grid)
    with pinned_imports(scratch, runtime):
        ev150 = importlib.import_module("plan_150k_test")
        build = importlib.import_module("build_lab")
        atr = fifty.g.daily_atr(15)[fifty.tr]
        def risk(dollars, multiplier):
            return np.floor(dollars/(np.nan_to_num(multiplier*atr, nan=1e12)*2))[:, None]
        q150 = dict(VB=20., ONB30=risk(2750, .25), MON_BR=5.,
                    EOS=risk(1250, build.REPORTS["EOS"][1]))
        legacy = {k: v*2.5 for k, v in fifty.quantities.items()}
        size_audit = {k: dict(different_days=int(np.count_nonzero(q150[k] != legacy[k])),
                             legacy_fractional_days=int(np.count_nonzero(legacy[k] % 1)),
                             max_absolute_difference=float(np.abs(q150[k]-legacy[k]).max()))
                      for k in ("ONB30", "EOS")}
        contexts = {
            "50K_evaluation": SimpleNamespace(parts=fifty.parts, quantities=fifty.quantities,
                challenge=fifty.challenge, max_days=21, dates=fifty.dates,
                tie_policy="inherited pass-first same-minute tie"),
            "150K_evaluation": SimpleNamespace(parts=fifty.parts, quantities=q150,
                challenge=ev150.evaluation, rules=ev150.R150, max_days=21, dates=fifty.dates,
                tie_policy="inherited breach-first same-minute tie"),
        }
        return SimpleNamespace(g=fifty.g, tr=fifty.tr, dates=fifty.dates, contexts=contexts,
                               fee=fee, source_ref=PIN, integer_size_audit=size_audit,
                               old_fractional_return_reference="analysis/outputs/dual_thrust_150k_output.txt")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-baseline", action="store_true")
    ap.add_argument("--preregistration")
    ap.add_argument("--scratch", default="scratch_data")
    args = ap.parse_args()
    result = prepare_sources()
    if args.build_baseline:
        out = ROOT / "analysis/outputs/codex_anson/baseline"
        target = ROOT / "agents/codex/runtime/anson_plan.pkl"
        bundle = load_funded(args.scratch, preregistration_commit=args.preregistration,
                             authorized_returns=True, audit_dir=out, plan_cache=target)
        evaluation = evaluation_parts(args.scratch, preregistration_commit=args.preregistration,
                                      authorized_returns=True, grid=bundle.lab.g)
        rows = pd.DataFrame(index=evaluation.dates)
        for name, context in evaluation.contexts.items():
            for leg, q in context.quantities.items():
                rows[f"{name}__{leg}"] = np.broadcast_to(q, (bundle.lab.D, 1)).ravel()
        rows.to_csv(out / "evaluation_quantities.csv", index_label="date")
        dump(out / "evaluation_size_audit.json", evaluation.integer_size_audit)
        meta = dict(bundle.metadata, expanded_cache=str(target), expanded_cache_sha256=file_sha(target),
                    preregistration=args.preregistration,
                    sources_manifest_sha256=file_sha(RUNTIME / "manifest.json"),
                    evaluation_integer_size_audit=evaluation.integer_size_audit)
        dump(out / "prepared_manifest.json", meta)
        print(json.dumps(dict(prepared_cache=str(target), DT=bundle.metadata["dt_reconciliation"],
                              evaluation_integer_size_audit=evaluation.integer_size_audit)))
    else:
        print(json.dumps(dict(ref=result["ref"], modules=len(result["modules"]),
                              unchanged_prepared_dependencies=len(result["prepared_baseline_dependencies"]),
                              new_returns=False)))
