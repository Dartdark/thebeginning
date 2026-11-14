"""Read-only accounting audit of the pinned 2026-11-13 research snapshot.

This reads existing trade ledgers, reports, and git objects. It does not import
strategy modules, generate returns, search parameters, or modify the source tree.
Run from any directory with Python 3 and openpyxl:
  python3 analysis/codex_weekly_research_20261113_audit.py
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import subprocess
from pathlib import Path

from openpyxl import load_workbook

PIN = "7b0caeff98ead324ecc492375659b0b89db13d9f"
BASE = "fe35af99"


def git(source, *args):
    return subprocess.check_output(
        ["git", "-C", str(source), *args], text=True
    ).strip()


def metrics(values):
    x = list(values)
    m = statistics.mean(x)
    sd = statistics.stdev(x) if len(x) > 1 else 0.0
    loss = -sum(v for v in x if v < 0)
    return {
        "n": len(x), "net_total": sum(x), "net_mean": m,
        "trade_t": m / sd * math.sqrt(len(x)) if sd else None,
        "profit_factor": sum(v for v in x if v > 0) / loss if loss else None,
        "win_rate": sum(v > 0 for v in x) / len(x),
    }


def ledger(source, rel):
    with (source / rel).open(newline="") as f:
        return list(csv.DictReader(f))


def split_stats(rows):
    def get(part):
        return metrics(float(r["net"]) for r in part)
    return {
        "all": get(rows),
        "design": get(r for r in rows if r["date"] < "2023-01-01"),
        "historical_holdout": get(r for r in rows if r["date"] >= "2023-01-01"),
    }


def mc_entries(source, rel):
    book = load_workbook(source / rel, read_only=True, data_only=True)
    rows = book["List of Trades"].iter_rows(min_row=3, values_only=True)
    keys = next(rows)
    entries = []
    for row in rows:
        d = dict(zip(keys, row))
        if str(d.get("Type")).startswith("Entry"):
            entries.append(d)
    book.close()
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=Path("/workspace/thebeginning_weekly_source_20261113"))
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).resolve().parent / "outputs" /
                        "codex_weekly_cross_review_20261113" / "research_accounting.json")
    args = parser.parse_args()
    source = args.source.resolve()
    assert git(source, "rev-parse", "HEAD") == PIN
    before = git(source, "status", "--porcelain")
    used = set()

    def rows(rel):
        used.add(rel)
        return ledger(source, rel)

    result = {
        "scope": "Saved-output accounting and chronology only; no new strategy returns",
        "source_head": PIN, "week_base": git(source, "rev-parse", BASE),
        "independent_before_claude_review": True,
        "new_material_research_disagreements": [],
    }
    chronology = {}
    for name, commits in {
        "jump_original_four": ["ed9973c6", "2e12bab1"],
        "edge_hunt_seven_then_amendment": ["e16a51d9", "07cd8898", "733a66b1"],
        "noise_other_markets": ["bc311d3e", "cd562876"],
        "jump_onb_other_markets": ["e9526bfd", "832d28b6"],
        "diversified_trend": ["332e60a3", "e3a4af96"],
        "nfp_v2": ["98db14f5", "6c6947d0", "0284da90"],
    }.items():
        chronology[name] = [git(source, "show", "-s", "--format=%H %aI %s", c)
                            for c in commits]
        # Confirm each later commit descends from the previous preregistration.
        for a, b in zip(commits, commits[1:]):
            subprocess.run(["git", "-C", str(source), "merge-base", "--is-ancestor", a, b],
                           check=True)
    result["chronology"] = chronology

    jump = {tag: split_stats(rows(f"checks/candidates/jump5/trades_{tag}.csv"))
            for tag in ("P1", "P2", "P3", "P4")}
    assert jump["P3"]["all"]["n"] == 1475
    assert abs(jump["P3"]["all"]["net_mean"] - 13.1) < 0.1
    assert jump["P1"]["historical_holdout"]["net_mean"] < 0
    assert jump["P2"]["historical_holdout"]["net_mean"] < 0
    assert jump["P4"]["historical_holdout"]["net_mean"] < 0
    result["original_jump_saved_ledgers"] = jump
    p3 = rows("checks/candidates/jump5/trades_P3.csv")
    result["rlc_two_published_entry_examples"] = [
        r for r in p3 if r["date"] == "2020-03-12" and
        (float(r["entry"]), int(r["side"])) in ((7754.75, 1), (7454.0, -1))
    ]
    assert len(result["rlc_two_published_entry_examples"]) == 2

    edge = {}
    for tag in ("H1a", "H1b", "H2", "H3", "H4", "H5", "H6", "H6b"):
        data = rows(f"checks/candidates/edge_hunt_1113/trades_{tag}.csv")
        de = metrics(float(r["net"]) for r in data if r["date"] < "2023-01-01")
        entry = {"design": de, "design_gate_pass": de["net_mean"] > 0 and de["trade_t"] >= 2}
        if tag == "H6b":
            entry["historical_holdout"] = metrics(float(r["net"]) for r in data
                                                   if r["date"] >= "2023-01-01")
            assert entry["historical_holdout"]["net_mean"] < 0
        else:
            assert not entry["design_gate_pass"]
            entry["historical_holdout"] = "not inspected; failed design gate"
        edge[tag] = entry
    assert edge["H6b"]["design_gate_pass"]
    result["edge_hunt_saved_ledgers"] = edge

    mc = {}
    for name, expected in (("NQ_Jump_Fade_v3.xlsx", 436), ("NQ_Noise_Longs.xlsx", 2581)):
        rel = "mc_reports/" + name
        used.add(rel)
        data = mc_entries(source, rel)
        assert len(data) == expected
        raw = metrics(float(r["Profit ($)"]) for r in data)
        mc[name] = {k.replace("net_", "gross_"): v for k, v in raw.items()}
        mc[name]["basis"] = "Raw workbook profit; this audit deducts no costs"
    result["multicharts_workbook_accounting"] = mc

    mc_noise = mc_entries(source, "mc_reports/NQ_Noise_Longs.xlsx")
    lo = min(r["Date"] for r in mc_noise).strftime("%Y-%m-%d")
    hi = max(r["Date"] for r in mc_noise).strftime("%Y-%m-%d")
    py_noise = [r for r in rows("analysis/outputs/bridge_noise_15m_trades_rth_longs.csv")
                if lo <= r["date"] <= hi]
    mc_map = {r["Date"].strftime("%Y%m%d%H%M"): float(r["Profit ($)"]) for r in mc_noise}
    py_map = {r["date"].replace("-", "") + f'{int(r["t0"]):04d}':
              (float(r["exit"]) - float(r["entry"])) * 20 for r in py_noise}
    common = sorted(mc_map.keys() & py_map.keys())
    assert len(common) == 2509 and len(py_noise) == 2557
    result["noise_matched_saved_trades"] = {
        "mc_n": len(mc_noise), "python_n": len(py_noise), "matched": len(common),
        "mc_only": len(mc_map.keys() - py_map.keys()),
        "python_only": len(py_map.keys() - mc_map.keys()),
        "matched_pnl_correlation": statistics.correlation(
            [mc_map[k] for k in common], [py_map[k] for k in common]),
        "note": "Python prices already include entry and market/stop slippage; this is not a missing-cost finding",
    }

    # Preserve exact saved claims/provenance without importing any research script.
    excerpts = {}
    for rel, needles in {
        "analysis/outputs/jump_tuning_demo_output.txt": ("[provenance]", "4368 rule versions", "Pick the 20 best"),
        "analysis/outputs/jump_fade_v3_mc_check_output.txt": ("[provenance]", "same entry minute", "MC only"),
        "analysis/outputs/diversified_trend_test_output.txt": ("[provenance]", "TSMOM, 9 markets", "C1 long-only", "PASS RULE"),
        "analysis/outputs/nfp_fade_v2_test_output.txt": ("[provenance]", "BASE our", "V2 two legs", "DISAGREE"),
        "analysis/outputs/nfp_v2_funded_bench_output.txt": ("[provenance]", "funded base:", "V2:", "no NFP"),
        "analysis/outputs/ingredient_combos_test_output.txt": ("random-skip placebo:",),
    }.items():
        used.add(rel)
        excerpts[rel] = [{"line": i, "text": line}
                         for i, line in enumerate((source / rel).read_text().splitlines(), 1)
                         if any(n in line for n in needles)]
    result["saved_output_claims"] = excerpts
    used.update({"TIER_LIST.md", "WATCHLIST.md", "DEVELOPMENT_PROCESS.md", "analysis/checker.py",
                 "analysis/invariance.py", "analysis/roll_adjust.py", "analysis/diversified_trend_test.py",
                 "analysis/jump_study.py", "analysis/jump_generic.py", "analysis/bridge_noise_15m_test.py",
                 "checks/candidates/jump5/PREREG.md", "checks/candidates/nfp_fade/PREREG_v2.md",
                 "checks/candidates/edge_hunt_1113/PREREG.md"})
    result["sha256_of_used_artifacts"] = {r: hashlib.sha256((source / r).read_bytes()).hexdigest()
                                            for r in sorted(used)}
    assert git(source, "status", "--porcelain") == before
    result["source_status_unchanged"] = True
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "material_findings": 0,
                      "assertions": "passed", "source_status_unchanged": True}))


if __name__ == "__main__":
    main()
