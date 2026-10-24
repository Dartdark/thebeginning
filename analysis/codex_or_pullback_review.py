"""Review supplied ORPullback sources and published tables; no strategy/price replay.

Run from repo root with pypdf. Checks table tokens and aggregate arithmetic only.
All original performance values remain author-reported, not independently validated.
"""
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "agents/codex/inputs/or_pullback"
OUT = ROOT / "analysis/outputs/codex_or_pullback_review"
CLAUDE = "a67035be4189b493098c80f1def979348520fd5d"


def git_text(path):
    return subprocess.check_output(["git", "show", f"{CLAUDE}:{path}"], cwd=ROOT).decode("utf-8")


def main():
    pages = [p.extract_text() or "" for p in PdfReader(INPUT / "report.pdf").pages]
    (INPUT / "report_extracted.txt").write_text(
        "\n\n".join(f"=== PAGE {i+1} ===\n{s}" for i, s in enumerate(pages)), encoding="utf-8")
    rows = [
        dict(period="2021-23 selection", trades=902, win_percent=45, pf=1.25, mean=13.35, net=12046, dd=1540, t=3.04),
        dict(period="2024-Jul2025 test", trades=477, win_percent=40, pf=1.17, mean=9.58, net=4568, dd=1868, t=1.54),
        dict(period="Aug2025-Jul2026 claimed sealed holdout", trades=286, win_percent=42, pf=1.27, mean=15.51, net=4434, dd=1428, t=1.86),
        dict(period="2021-26 all", trades=1665, win_percent=43, pf=1.23, mean=12.64, net=21048, dd=1868, t=3.83),
        dict(period="2021-26 longs", trades=883, win_percent=44, pf=1.24, mean=13.06, net=11530, dd=1344, t=2.93),
        dict(period="2021-26 shorts", trades=782, win_percent=42, pf=1.21, mean=12.17, net=9518, dd=1876, t=2.48),
    ]
    # Verify every transcribed numeric field against the relevant PDF page.
    for row in rows:
        for key in ("trades", "net", "dd"):
            assert f"{row[key]:,}" in pages[2], (row["period"], key)
        for key in ("pf", "mean", "t"):
            assert f"{row[key]:.2f}" in pages[2], (row["period"], key)
        assert f"{row['win_percent']}%" in pages[2]
        row["pdf_page"] = 3
        row["status"] = "author_reported_not_recomputed"
    assert sum(r["trades"] for r in rows[:3]) == rows[3]["trades"]
    assert sum(r["net"] for r in rows[:3]) == rows[3]["net"]
    assert rows[4]["trades"] + rows[5]["trades"] == rows[3]["trades"]
    assert rows[4]["net"] + rows[5]["net"] == rows[3]["net"]
    exits = dict(stop=887, target=495, time=283)
    for value in exits.values():
        assert str(value) in pages[2]
    assert sum(exits.values()) == rows[3]["trades"]
    old = dict(period="2010-20", trades=2693, pf=0.94, mean=-1.4, t=-1.1,
               status="author_reported_not_recomputed", pdf_page=4)
    assert "2,693" in pages[3] and "0.94" in pages[3] and "1.4" in pages[3] and "1.1" in pages[3]
    code = (INPUT / "source.txt").read_text(encoding="utf-8-sig")
    plain = re.sub(r"//[^\n]*", "", code)
    input_text = plain.split("Inputs:", 1)[1].split("Variables:", 1)[0]
    inputs = {}
    for key, value in re.findall(r"\b(\w+)\(\s*(-?\d+(?:\.\d+)?|true|false)\s*\)", input_text):
        inputs[key] = value == "true" if value in ("true", "false") else float(value)
    assert inputs["StopPts"] == 50 and inputs["TargetPts"] == 100
    assert not inputs["ChartIsCentral"] and not inputs["PriceScaled"]
    anchors = {}
    for name, token in {
        "rth_reset": "if inRTH and (Time[1] <= tOR0 or Date <> Date[1])",
        "long_trigger": "if armedL and doneL = false",
        "long_arm": "if Close > orH then armedL = true;",
        "close_entry": 'Buy ("F9b.L")',
        "long_exit_branch": "if MarketPosition = 1 then begin",
        "long_stop": 'Sell ("F9b.LS") next bar at EntryPrice - stp stop;',
        "time_exit": 'if Time >= tFlat then Sell ("F9b.LX")',
        "session_exit": "SetExitOnClose;",
    }.items():
        anchors[name] = [i+1 for i, line in enumerate(code.splitlines()) if token in line]
        assert anchors[name], name
    plan_output = git_text("analysis/outputs/real_fee_bench_output.txt")
    current_plan_row = next(line for line in plan_output.splitlines() if line.startswith("plan @ $1.04"))
    combine_row = next(line for line in plan_output.splitlines() if "fee $1.040 per MNQ" in line)
    prior_tier = git_text("TIER_LIST.md")
    prior_pullback = next(line for line in prior_tier.splitlines() if "| VWAP pullback after a 30-min" in line)
    arithmetic = dict(
        scope="arithmetic on nominal inputs and rounded report facts, not return or account replay",
        one_mnq_stop=inputs["StopPts"]*2, one_mnq_target=inputs["TargetPts"]*2,
        one_nq_stop=inputs["StopPts"]*20, one_nq_target=inputs["TargetPts"]*20,
        two_mnq_stops=2*inputs["StopPts"]*2, two_nq_stops=2*inputs["StopPts"]*20,
        reported_max_dd_fraction_of_nominal_2000_trail=rows[3]["dd"]/2000,
        report_roundtrip_cost_mnq=2.00, latest_assumed_fee_mnq=1.04,
        two_market_stop_fill_slips_mnq=1.00, fee_plus_two_slips_mnq=2.04,
        two_extra_ticks_each_side_extra_mnq=2.00,
        extra_slip_fraction_of_reported_mean=2.00/rows[3]["mean"],
        account_limit="closed-equity DD is not breach probability; starting cushion, trail lock, other legs and intraday path matter",
    )
    result = dict(
        verdict="WATCH as research; no current-plan addition or replacement justified yet",
        user_scope="Against current plan overall; no compulsory ONB head-to-head",
        new_strategy_return_trials=0, new_account_simulations=0,
        inputs={p.name: dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size)
                for p in (INPUT/"source.txt", INPUT/"report.pdf")},
        pdf_pages=len(pages), source_lines=len(code.splitlines()), literal_defaults=inputs,
        reported_periods=rows, reported_old_period=old, reported_exit_counts=exits,
        source_line_anchors=anchors, arithmetic=arithmetic,
        normalized_ct=dict(opening_range="08:30-08:45", earliest_possible_trigger="08:55 on full intended 5-minute bars",
                           entry_cutoff="14:30", normal_flatten="14:55"),
        current_plan_context=dict(commit=CLAUDE, path="analysis/outputs/real_fee_bench_output.txt",
                                  funded_baseline_row=current_plan_row, evaluation_baseline_row=combine_row,
                                  warning="ORPullback is absent; these rows are not its incremental effect"),
        distinct_prior_family=dict(commit=CLAUDE, row=prior_pullback,
                                   warning="VWAP/30minOR/swing exits differ from this source"),
        author_eval_claim=dict(model="standalone LucidFlex-style, 2 MNQ, 60-day horizon",
                               selection_pass_percent=41, test_pass_percent=35, holdout_pass_percent=44,
                               status="author_reported_not_an_Apex_combined_plan_test"),
        limits=["Original ledger, search registry, sealed-holdout provenance and exact MC parity export absent",
                "First full post-entry bar lacks generated explicit brackets under ordinary declared IOG-off evaluation",
                "Close fills are assumptions and holidays lack an explicit early-close rule",
                "Switch-off rule in note is not present in supplied source",
                "PriceScaled is a separate optional configuration, not an adopted repair",
                "Latest real-micro-fee and Twin daily-mark checks are recorded as closed in current brief"],
    )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/"summary.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    with (OUT/"reported_periods.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    print(json.dumps(dict(new_return_trials=0, source_lines=len(code.splitlines()),
                         pdf_pages=len(pages), reported_totals_reconcile=True,
                         arithmetic=arithmetic, current_plan=result["current_plan_context"]), indent=2))


if __name__ == "__main__":
    main()
