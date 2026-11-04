"""Audit existing frozen case artifacts; never generate/replay a strategy.

Recounts CSVs and independently reproduces the prespecified paired bootstrap.
No market prices, new definitions, accounts or allocation changes are run.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import subprocess
from collections import Counter
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
RUNTIME = ROOT / "agents/codex/runtime/eval_audit_20261104"
FOLDER = RUNTIME / "validation_amended"
STATUSES = ["pass", "fail", "expire", "unknown"]
CT = ZoneInfo("America/Chicago")


def sha(p):
    with Path(p).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":"),
        allow_nan=False, default=str).encode()).hexdigest()


def load(p):
    return json.loads(Path(p).read_text())


def cases(p):
    with Path(p).open(newline="") as f:
        return list(csv.DictReader(f))


def close(a, b):
    assert np.allclose(a, b, rtol=0, atol=1e-10), (a, b)


def recount(rows, reported):
    counts = {s: sum(r["status"] == s for r in rows) for s in STATUSES}
    n = len(rows)
    assert sum(counts.values()) == n == reported["n"]
    assert counts == reported["counts"]
    close(reported["pass_lower"], counts["pass"] / n)
    close(reported["pass_upper"], (counts["pass"] + counts["unknown"]) / n)
    close(reported["fail_lower"], counts["fail"] / n)
    close(reported["fail_upper"], (counts["fail"] + counts["unknown"]) / n)
    times = [float(r["calendar_days"]) for r in rows if r["status"] == "pass"]
    if times:
        close(reported["conditional_pass_median_time"], np.median(times))
    else:
        assert reported["conditional_pass_median_time"] is None
    return counts


def check_bootstrap(a, b, observed):
    assert [r["start_id"] for r in a] == [r["start_id"] for r in b]
    n = len(a); block = observed["block_starts"]
    assert observed["n"] == n == 180
    assert observed["n_reps"] == 5000 and observed["seed"] == 20261104
    assert observed["quantiles"] == [.05, .95] and block in [4, 8]
    x = np.array([[r["status"] == s for s in STATUSES] for r in a], float)
    y = np.array([[r["status"] == s for s in STATUSES] for r in b], float)
    known = x - y
    d = np.column_stack([known, x[:, 0]-y[:, 0]-y[:, 3], x[:, 0]+x[:, 3]-y[:, 0],
        x[:, 1]-y[:, 1]-y[:, 3], x[:, 1]+x[:, 3]-y[:, 1]])
    names = STATUSES + ["pass_difference_lower", "pass_difference_upper",
                        "fail_difference_lower", "fail_difference_upper"]
    rng = np.random.default_rng(20261104); out = np.empty((5000, 8)); h = hashlib.sha256()
    for start in range(0, 5000, 250):
        ix = (rng.integers(0, n-block+1, size=(250, math.ceil(n/block)))[:, :, None]
              + np.arange(block)).reshape(250, -1)[:, :n]
        h.update(ix.astype("<i8", copy=False).tobytes())
        out[start:start+250] = d[ix].mean(axis=1)
    assert h.hexdigest() == observed["resample_index_sha256"]
    ci = np.quantile(out, [.05, .95], axis=0)
    for i, name in enumerate(names):
        close(d.mean(axis=0)[i], observed["point_delta"][name])
        close(ci[:, i], observed["ci"][name])
    close(observed["identified_effect_ci"]["pass_difference"], [ci[0, 4], ci[1, 5]])
    close(observed["identified_effect_ci"]["fail_difference"], [ci[0, 6], ci[1, 7]])
    return {"pass_ci90": [float(ci[0, 4]), float(ci[1, 5])],
            "fail_ci90": [float(ci[0, 6]), float(ci[1, 7])]}


def main():
    frozen_path = BASE / "amended_frozen_validation_selection.json"
    frozen = load(frozen_path)
    selection_commit = subprocess.check_output(["git", "rev-parse", "588e6b6"], cwd=ROOT, text=True).strip()
    assert subprocess.check_output(["git", "show", f"{selection_commit}:{frozen_path.relative_to(ROOT)}"], cwd=ROOT) == frozen_path.read_bytes()
    old = load(BASE / "policies.json")["candidates"]
    refs = [p for p in old if p["label"] in ["CURRENT", "EMPTY"]]
    policies = {p["candidate_id"]: p for p in refs + frozen["nominees"]}
    assert len(policies) == 8 and len(frozen["nominees"]) == 4
    assert all(p["governor"]["risk_fraction"] == 0 for p in frozen["nominees"])
    receipt = load(RUNTIME / "fixed_arm/tape/prepare_receipt.json")
    cfgsha = sha(BASE / "config.json")
    context = digest({"amendment_commit": frozen["amendment_commit"],
        "selection_commit": selection_commit, "selection_sha256": sha(frozen_path)})
    study = digest({"preregistration_commit": frozen["preregistration_commit"],
        "config_sha256": cfgsha, "tape_receipt": receipt, "selection_sha256": context})
    costs = {"low": (1.04, 1.), "main": (1.24, 1.), "stress": (2.48, 2.)}
    fractions = {"fresh": 1., "quarter_cushion": .25, "half_cushion": .5, "three_quarter_cushion": .75}
    checked, report_hashes, first_calendar = [], {}, None
    csv_hashes, total_rows, bootstrap_checks = {}, 0, 0
    for scenario, (commission, ticks) in costs.items():
        for state, fraction in fractions.items():
            report_path = FOLDER / f"report_{scenario}_{state}.json"
            pool_path = FOLDER / f"completed_{scenario}_{state}.json"
            report, pool = load(report_path), load(pool_path)
            report_hashes[str(report_path.relative_to(ROOT))] = sha(report_path)
            assert report["scenario"] == scenario and report["initial_state"] == state
            assert pool["preregistration_commit"] == frozen["preregistration_commit"]
            assert pool["study_fingerprint"] == study and pool["candidate_count"] == 8
            assert {r["candidate_id"] for r in pool["results"]} == set(policies)
            calendar = pool["calendar"]
            assert len(calendar) == len(set(calendar)) == 896 and calendar == sorted(calendar)
            if first_calendar is None: first_calendar = calendar
            assert calendar == first_calendar
            data, summaries = {}, {}
            for result in pool["results"]:
                pid = result["candidate_id"]; policy = policies[pid]
                path = ROOT / result["csv_path"]
                assert sha(path) == result["csv_sha256"]
                csv_hashes[str(path.relative_to(ROOT))] = result["csv_sha256"]
                expected = digest({"study": study, "policy": policy, "calendar": calendar,
                    "scenario": scenario, "costs": {"round_trip_commission": commission, "slippage_ticks": ticks}, "state": state})
                assert result["fingerprint"] == expected
                rows = cases(path); total_rows += len(rows)
                assert [r["start_id"] for r in rows] == calendar
                count = recount(rows, result["summary"])
                summary = report["accounts"][f"{policy['account']}K"][pid]["cohorts"]
                recount(rows, summary["all2023plus"])
                for cohort, group in [("2023through2025", [r for r in rows if 2023 <= int(r["start_year"]) <= 2025]),
                                      ("2026", [r for r in rows if int(r["start_year"]) == 2026])]:
                    recount(group, summary[cohort])
                for row in rows:
                    assert row["candidate_id"] == pid and row["cost_scenario"] == scenario and row["initial_state"] == state
                    start = datetime.fromisoformat(row["start_id"]).date()
                    purchase = datetime.fromisoformat(row["purchase_ct"])
                    expiry = datetime.fromisoformat(row["expiry_ct"])
                    assert purchase.date() == start-timedelta(days=1) and (purchase.hour, purchase.minute) == (16, 30)
                    assert expiry.date() == purchase.date()+timedelta(days=30) and (expiry.hour, expiry.minute) == (17, 0)
                    assert start.year >= 2023 and start.weekday() < 5
                    assert float(row["last_epoch"]) <= expiry.timestamp()
                    close(float(row["initial_equity"]), policy["account"]*1000.)
                    close(float(row["initial_floor"]), policy["account"]*1000.-(2000. if policy["account"] == 50 else 4000.)*fraction)
                    if row["total_modeled_cost"]:
                        close(float(row["total_modeled_cost"]), sum(float(row[k]) for k in ["commission", "source_fill_slippage", "liquidation_cost"]))
                        assert float(row["max_net_micro_exposure"]) <= (60 if policy["account"] == 50 else 120)
                summary_keys = {'n', 'counts', 'pass_lower', 'pass_upper', 'fail_lower', 'fail_upper',
                    'unknown_share', 'conditional_pass_median_time', 'conditional_pass_mean_time',
                    'pass_time_coverage', 'fee_normalization'}
                data[pid] = rows
                summaries[pid] = {cohort: {k: v for k, v in value.items() if k in summary_keys}
                    for cohort, value in summary.items()}
                if policy["label"] == "EMPTY":
                    assert count["expire"] == 896 and count["pass"] == count["fail"] == count["unknown"] == 0
            pairs = {}
            assert {p["candidate_id"] for p in report["paired"]} == {p["candidate_id"] for p in frozen["nominees"]}
            for paired in report["paired"]:
                pid, bid = paired["candidate_id"], paired["baseline_id"]
                assert policies[bid]["label"] == "CURRENT" and policies[pid]["account"] == policies[bid]["account"]
                a = [r for r in data[pid] if int(r["start_weekday"]) == 0]
                b = [r for r in data[bid] if int(r["start_weekday"]) == 0]
                checks = {k: check_bootstrap(a, b, v) for k, v in paired["bootstrap"].items()}
                bootstrap_checks += len(checks)
                # Necessary interval conditions from the frozen recommendation gates.
                efficiency = all(v["pass_ci90"][0] > 0 for v in checks.values())
                safety = all(v["fail_ci90"][1] < 0 for v in checks.values())
                point = paired["bootstrap"]["4"]["point_delta"]
                ap = sum(r['status'] == 'pass' for r in a)/len(a)
                bp_upper = sum(r['status'] in ['pass', 'unknown'] for r in b)/len(b)
                fee_ratio_upper = bp_upper/ap if ap else None
                at = [float(r['calendar_days']) for r in a if r['status'] == 'pass']
                bt = [float(r['calendar_days']) for r in b if r['status'] == 'pass']
                known_delay = float(np.median(at)-np.median(bt)) if at and bt else None
                pairs[pid] = {"baseline_id": bid, "identified_intervals": checks,
                    "scope": "180 paired Monday starts; both prespecified4/8weekly-start sensitivities",
                    "identified_point_pass_difference": [point['pass_difference_lower'], point['pass_difference_upper']],
                    "identified_point_fail_difference": [point['fail_difference_lower'], point['fail_difference_upper']],
                    "efficiency_interval_prerequisite": efficiency,
                    "safety_interval_prerequisite": safety,
                    "efficiency_conditions": {
                        "identified_pass_gain_at_least_3pp": point['pass_difference_lower'] >= .03,
                        "identified_90pct_pass_lower_above_zero_both_blocks": efficiency,
                        "identified_failure_increase_no_more_than_1pp": point['fail_difference_upper'] <= .01},
                    "safety_conditions": {
                        "identified_failure_reduction_at_least_5pp": point['fail_difference_upper'] <= -.05,
                        "identified_90pct_failure_upper_below_zero_both_blocks": safety,
                        "identified_pass_point_loss_no_more_than_2pp": point['pass_difference_lower'] >= -.02,
                        "identified_90pct_pass_lower_at_least_minus5pp_both_blocks": all(v['pass_ci90'][0] >= -.05 for v in checks.values()),
                        "identified_fee_per_pass_ratio_upper": fee_ratio_upper,
                        "identified_fee_increase_no_more_than5pct": fee_ratio_upper is not None and fee_ratio_upper <= 1.05,
                        "known_pass_only_median_delay_calendar_days": known_delay,
                        "complete_baseline_pass_time_distribution_known": not any(r['status'] == 'unknown' for r in b),
                        "delay_requirement": "<=10calendar days cannot be certified from baseline's known-pass subset"},
                    "efficiency_gate": ("INTERVAL_PREREQUISITE_ONLY: other gates still required" if efficiency else
                        "NOT_EARNED: required positive identified pass lower bound fails"),
                    "safety_gate": ("INTERVAL_PREREQUISITE_ONLY: other gates still required" if safety else
                        "NOT_EARNED: required negative identified failure upper bound fails")}
            checked.append({"scenario": scenario, "state": state,
                "summaries": summaries, "recommendation_gates": pairs})
    output = {"status": "PASS_existing_artifact_integrity_no_replacement_recommendation_earned",
        "selection_commit": selection_commit, "amendment_commit": frozen["amendment_commit"],
        "original_commit": frozen["preregistration_commit"], "frozen_selection_sha256": sha(frozen_path),
        "scenarios": len(checked), "policies_per_scenario": 8, "case_rows_verified": total_rows,
        "paired_bootstrap_checks": bootstrap_checks, "calendar": {"starts": 896,
            "first": first_calendar[0], "last": first_calendar[-1], "monday_starts": 180,
            "2026_starts": sum(s.startswith('2026') for s in first_calendar)},
        "scenario_results": checked, "report_sha256": report_hashes, "case_sha256": csv_hashes,
        "new_definitions_or_replays": False, "allocation_change": False,
        "governor_design_limit": "Frozen riskfraction>0 code rejects missing NaN stop risk as zero quantity. Missing-ATR LDF/ONBML cap cases with244expiries/0failures are data-rejection outcomes, not clean safety evidence. All4validatednominees have riskfraction0; known-stopFC2Bcaps are a separate valid but expiration-heavy tradeoff.",
        "independent_native_economic_verification": "pending"}
    (BASE / "final_results_review.json").write_text(json.dumps(output, indent=2)+'\n')
    print(f"PASS: {len(checked)}scenarios, {total_rows}existing case rows and {bootstrap_checks}paired bootstrap checks; no new strategy/account replay")


if __name__ == "__main__": main()
