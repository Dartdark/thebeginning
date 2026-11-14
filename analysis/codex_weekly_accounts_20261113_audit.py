"""Pinned weekly account review: synthetic accounting only, no strategy imports.

Run from any directory. Source modules are parsed and individual pure definitions
are extracted; their module-level bench/research code is never executed.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import copy
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

PIN = "7b0caeff98ead324ecc492375659b0b89db13d9f"
BASE = "fe35af99"
FILES = [
    "analysis/bench150.py", "analysis/funded_sim150.py", "analysis/funded_lab.py",
    "analysis/funded_bootstrap.py", "analysis/funded_resize150.py",
    "analysis/funded_speed150.py", "analysis/funded_ldf_int150.py",
    "analysis/plan150_integer_test.py", "analysis/plan_150k_test.py",
    "analysis/portfolio.py", "analysis/twin_continuation_bench.py",
    "analysis/dual_thrust_bench.py", "analysis/overnight_tick_bench.py",
    "analysis/jump_fade_paths.py", "analysis/eval_size_live.py",
    "analysis/eval_size_combo.py", "analysis/resize_book.py",
    "analysis/eval_levers150.py", "analysis/eval_finish150_plateau.py",
    "analysis/copier_finish_bench.py", "analysis/active_scan_eval.py",
    "analysis/cl_sunday_fade_bench.py", "analysis/fc_2b_bench.py",
    "analysis/real_fee_bench.py", "analysis/build_lab.py", "analysis/grid24.py",
    "analysis/bridge_noise_15m_test.py", "funded_strategies/FUNDED_PLAN.md",
    "funded_strategies/README.md", "apex_strategies/README.md",
    "apex_strategies/NQ_Overnight_Bias_ADX30.txt",
    "apex_strategies/Twin_Continuation_150K.txt",
    "funded_strategies/NQ_Dual_Thrust.txt", "funded_strategies/NQ_Late_Day_Flow.txt",
    "funded_strategies/NQ_Monday_Long.txt", "live/expected_setup.json",
    "analysis/outputs/funded_resize150_output.txt",
    "analysis/outputs/funded_speed150_output.txt",
    "analysis/outputs/funded_ldf_int150_output.txt",
    "analysis/outputs/resize_book_output.txt",
    "analysis/outputs/eval_size_live_output.txt",
    "analysis/outputs/eval_levers150_output.txt",
    "analysis/outputs/copier_finish_bench_output.txt",
]


def git(source: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(source), *args], text=True).strip()


def tree(source: Path, rel: str) -> ast.Module:
    return ast.parse((source / rel).read_text(), filename=str(source / rel))


def function(source: Path, rel: str, name: str, namespace: dict):
    node = next(n for n in tree(source, rel).body if isinstance(n, ast.FunctionDef) and n.name == name)
    node = copy.deepcopy(node)
    node.decorator_list = []
    module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    exec(compile(module, str(source / rel), "exec"), namespace)
    return namespace[name]


def funded_plan(source: Path) -> dict:
    # Only these literal/dict/lambda assignments; no source imports or setup().
    names = {"PLAN_LEGACY", "PLAN", "sc", "LIVE_FUNDED"}
    nodes = []
    for n in tree(source, "analysis/bench150.py").body:
        if isinstance(n, ast.Assign):
            t = n.targets[0]
            if isinstance(t, ast.Name) and t.id in names:
                nodes.append(copy.deepcopy(n))
            elif isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name) and t.value.id == "LIVE_FUNDED":
                nodes.append(copy.deepcopy(n))
    ns = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), "funded_plan_assignments", "exec"), ns)
    return ns["LIVE_FUNDED"]


def duration_fixture(source: Path, corrected: bool = False) -> list[dict]:
    records = []
    class FakeLab:
        D = 500
        W = {"TOY": np.zeros((500, 2))}
        C = {"TOY": np.zeros(500)}
        def _base(self, plan):
            return list(plan), np.ones((len(plan), self.D))
    def simulate(W, C, base, **kw):
        records.append({"requested": kw["horizon"], "actual": W.shape[1]})
        return {"paid": [0], "blown": [0], "payouts": [0]}
    ns = {"np": np, "BASE_FUNDED": {"TOY": 1}, "F": SimpleNamespace(simulate_sized=simulate)}
    bench = function(source, "analysis/bench150.py", "funded_bench", ns)
    ctx = {"lab": FakeLab(), "dts": pd.date_range("2018-01-01", periods=500, freq="B")}
    out = []
    for horizon in (250, 500):
        start = len(records)
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            bench(ctx, {}, H=horizon)
        calls = records[start:]
        actual = sorted({r["actual"] for r in calls})
        assert len(calls) == 600
        assert actual == [horizon if corrected else (240 if horizon == 250 else 500)]
        if corrected:
            assert f" {horizon}d $" in captured.getvalue()
            assert " 2y $" not in captured.getvalue()
        out.append({"requested_days": horizon, "actual_days": actual, "calls": len(calls),
                    "row_label": f"{horizon}d" if corrected else "2y (original constant)"})
    # Formula control; there is deliberately no strategy or payout re-run here.
    for horizon in (250, 500):
        blocks = (horizon + 20 - 1) // 20
        assert len(np.zeros((blocks, 20)).ravel()[:horizon]) == horizon
    return out


def integer_fixture(source: Path, plan: dict, corrected: bool = False) -> dict:
    # Evaluate the simulator's actual quantity expression on scalar fixtures.
    run = next(n for n in tree(source, "analysis/funded_sim150.py").body
               if isinstance(n, ast.FunctionDef) and n.name == "run_pa_sized")
    assign = next(n for n in ast.walk(run) if isinstance(n, ast.Assign)
                  and isinstance(n.targets[0], ast.Subscript)
                  and isinstance(n.targets[0].value, ast.Name) and n.targets[0].value.id == "q")
    expression = compile(ast.Expression(body=assign.value), "exact_quantity_expression", "eval")
    doc = (source / "funded_strategies/FUNDED_PLAN.md").read_text()
    assert "Monday Long 1, EOS risk" in doc and "Bridge Monday 1, CL Sunday" in doc
    rows = []
    for cushion in (1500, 2000, 2250, 2999, 3000):
        f = min(1, max(0.5, cushion / 3000))
        q = lambda b: int(eval(expression, {"np": np}, {"base": np.array([[b]]), "f": f, "k": 0, "d": 0}))
        rows.append({"cushion": cushion, "f": f, "bench_monday": q(plan["MON_MC"]),
                     "bench_bridge": q(plan["MON_BR_MC"]), "documented_each": q(1)})
    assert plan["MON_MC"] == plan["MON_BR_MC"] == (1 if corrected else 1.5)
    differences = [r["bench_monday"] - r["documented_each"] for r in rows]
    assert differences == ([0] * len(rows) if corrected else [0, 1, 1, 1, 0])
    return {"base_values": {k: plan[k] for k in ("MON_MC", "MON_BR_MC")}, "rows": rows,
            "quantity_expression_line": assign.lineno}


def proposal_fixture(source: Path, proposal: Path, original_plan: dict) -> dict:
    """Apply only inside a disposable source subset; never edit either worktree."""
    required = ("analysis/bench150.py", "analysis/funded_sim150.py", "funded_strategies/FUNDED_PLAN.md")
    pinned_hashes = {rel: hashlib.sha256((source / rel).read_bytes()).hexdigest() for rel in required}
    write_tree_bench = Path(__file__).resolve().parent / "bench150.py"
    write_tree_hash = hashlib.sha256(write_tree_bench.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="codex_weekly_funded_20261113_", dir="/tmp") as td:
        temporary = Path(td)
        for rel in required:
            target = temporary / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / rel, target)
        check = subprocess.run(["git", "apply", "--check", "--whitespace=error", str(proposal)],
                               cwd=temporary, check=True, capture_output=True, text=True)
        subprocess.run(["git", "apply", "--whitespace=error", str(proposal)],
                       cwd=temporary, check=True, capture_output=True, text=True)
        patched_hash = hashlib.sha256((temporary / "analysis/bench150.py").read_bytes()).hexdigest()
        patched_plan = funded_plan(temporary)
        assert set(patched_plan) == set(original_plan)
        assert {k for k in original_plan if original_plan[k] != patched_plan[k]} == {"MON_MC", "MON_BR_MC"}
        assert patched_plan["LDF_MC"] == original_plan["LDF_MC"] == 4.0
        durations = duration_fixture(temporary, corrected=True)
        integers = integer_fixture(temporary, patched_plan, corrected=True)
    assert pinned_hashes == {rel: hashlib.sha256((source / rel).read_bytes()).hexdigest() for rel in required}
    assert hashlib.sha256(write_tree_bench.read_bytes()).hexdigest() == write_tree_hash
    return {
        "status": "offline proposal; not deployed or applied to either worktree",
        "patch": str(proposal), "patch_sha256": hashlib.sha256(proposal.read_bytes()).hexdigest(),
        "git_apply_check": "PASS", "git_apply_check_output": check.stdout + check.stderr,
        "pinned_bench_sha256": pinned_hashes["analysis/bench150.py"],
        "temporary_patched_bench_sha256": patched_hash,
        "safe_write_worktree_bench_sha256_unchanged": write_tree_hash,
        "funded_horizon_fixture": durations, "funded_integer_fixture": integers,
        "all_other_funded_plan_values_preserved": True, "LDF_MC_preserved": patched_plan["LDF_MC"],
        "temporary_copy_removed": True, "actual_strategy_or_payout_returns_computed": False,
    }


def eval_roster(source: Path) -> dict:
    n = next(n for n in tree(source, "analysis/bench150.py").body if isinstance(n, ast.Assign)
             and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "LIVE_EVAL")
    live = ast.literal_eval(n.value)
    setup = json.loads((source / "live/expected_setup.json").read_text())
    tags = {"ONB30": "ONB150-5", "MON_BR": "MON_BR150-5", "TWIN": "TW150-5", "DT": "DT150-5",
            "JF": "JF150-5", "NBL": "NBL150-5", "LDF": "LDF150-5"}
    checks = {}
    for k, tag in tags.items():
        chart = setup["charts"][tag]
        v = live[k]
        checks[k] = (chart["risk"] == v[1]) if isinstance(v, tuple) else (chart["qty"] == v)
    assert all(checks.values()) and set(live) == set(tags)
    return {"composition_and_nominal_sizes_match": checks,
            "scope": "Nominal roster only; this does not assert finish/entry-level behavior parity.",
            "account_target": setup["accounts"]["#5"]["target"], "bench_target": 159000}


def floor_control(source: Path) -> dict:
    ev = function(source, "analysis/plan_150k_test.py", "evaluation", {"np": np})
    W = np.zeros((21, 1440)); R = np.zeros_like(W)
    for d, value in enumerate((6000, -3500, -2500, 7000)):
        W[d, -1] = value; R[d, -1] = value
    rules = dict(st=150000, dd=4000, dll=2000, lock=150100, tgt=9000)
    current = ev(W, R, 0, 21, rules)
    old = ev(W, R, 0, 21, rules, pa_lock=True)
    assert current == ("fail", 3) and old == ("pass", 4)
    return {"current": current, "old_pa_lock_control": old,
            "meaning": "Previously reported evaluation floor bug is corrected in this source; synthetic fixture only."}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, default=Path("/workspace/thebeginning_weekly_source_20261113"))
    p.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "outputs/codex_weekly_cross_review_20261113/accounts_audit.json")
    p.add_argument("--proposal", type=Path, default=Path(__file__).resolve().parent.parent / "agents/codex/proposals/weekly_20261113_funded_bench.patch")
    args = p.parse_args()
    source = args.source.resolve()
    assert git(source, "rev-parse", "HEAD") == PIN
    status = git(source, "status", "--porcelain")
    assert not status, "Pinned source worktree must remain clean."
    plan = funded_plan(source)
    payload = {
        "assessment": "independent; frozen before same-week Claude cross-review/Friday conclusions",
        "source_head": PIN, "baseline": git(source, "rev-parse", BASE),
        "source_status_before": status,
        "method": "Static source and saved text accounting; AST-extracted synthetic fixtures. No strategy module imports, market backtests, parameter search, live operations, or external messages.",
        "funded_horizon_fixture": duration_fixture(source),
        "funded_integer_fixture": integer_fixture(source, plan),
        "live_funded_nominal_base": plan,
        "eval_roster_fixture": eval_roster(source),
        "evaluation_floor_fix_control": floor_control(source),
        "offline_proposal_verification": proposal_fixture(source, args.proposal.resolve(), plan),
        "limits": [
            "No market-data performance rerun: actual direction and size of corrected funded differences remain unmeasured.",
            "Existing DLL exact-limit liquidation and 21-trading-day proxy for the actual calendar clock remain inherited assumptions.",
            "Existing scaled micro commission, missing-minute marks, whole-night worst proxies, and intraminute adverse-extreme aggregation remain qualifications, not newly quantified regressions.",
            "The new nominal LIVE_EVAL roster matches expected_setup; eval_size_combo/resize_book still use fixed full-size paths while ONB/Twin/DT have default real-time finish sizing. No live-policy parity or changed ranking claimed.",
            "Funded live cushion guards sample entry equity and cap each stop; this shared simulator uses day-start fractional cushion sizing. No funded account is currently live.",
        ],
    }
    payload["source_provenance"] = [{"path": rel, "bytes": (source / rel).stat().st_size,
                                     "lines": len((source / rel).read_text().splitlines()),
                                     "sha256": hashlib.sha256((source / rel).read_bytes()).hexdigest()}
                                    for rel in FILES]
    payload["review_metrics"] = {
        "explicit_scope_files_hashed": len(FILES),
        "scope_text_lines": sum(x["lines"] for x in payload["source_provenance"]),
        "same_week_review_conclusion_files_read": 0,
        "synthetic_checks": 6,
        "market_backtests_or_searches": 0,
        "mutated_source_files": 0,
        "diff_numstat_for_hashed_files": git(source, "diff", "--numstat", BASE + "..HEAD", "--", *FILES).splitlines(),
    }
    payload["source_status_after"] = git(source, "status", "--porcelain")
    assert payload["source_status_after"] == status
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"output": str(args.out), "checks": "PASS", "findings": 2,
                      "source_head": PIN, "source_clean": not payload["source_status_after"]}))


if __name__ == "__main__":
    main()
