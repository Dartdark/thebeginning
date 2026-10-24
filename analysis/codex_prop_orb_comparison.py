"""Literal source comparison and synthetic arithmetic; no historical returns/replay.

Standard library only. Run from repo root. Baseline objects are pinned Git blobs.
"""
import hashlib
import json
import re
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "agents/codex/inputs/prop_orb_comparison/source.txt"
OUT = ROOT / "analysis/outputs/codex_prop_orb_comparison"
CLAUDE = "8f6b75cc1c6044f712c3ad5f1a774de60dd14859"


def git_text(path):
    return subprocess.check_output(["git", "show", f"{CLAUDE}:{path}"], cwd=ROOT).decode("utf-8")


def defaults(code):
    plain = re.sub(r"\{.*?\}|//[^\n]*", "", code, flags=re.S)
    text = re.split(r"(?i)inputs:", plain, maxsplit=1)[1]
    text = re.split(r"(?i)(?:variables|vars):", text, maxsplit=1)[0]
    result = {}
    for name, value in re.findall(r"\b(\w+)\(\s*(-?\d+(?:\.\d+)?|true|false)\s*\)", text):
        result[name] = value == "true" if value in ("true", "false") else float(value)
    return result


def main():
    code = INPUT.read_text(encoding="utf-8-sig")
    new = defaults(code)
    assert new["SLPoints"] == 70 and new["EntryMode"] == 2 and new["ExtraBias"] == 3
    paths = {"evaluation_onb": "apex_strategies/NQ_Overnight_Bias_ADX30.txt",
             "funded_onb": "funded_strategies/NQ_Overnight_Bias_ML.txt",
             "merged_orb_anomaly": "checks/candidates/overnight_anomaly/Overnight_Anomaly_BiaisORB.txt"}
    baseline = {}
    for name, path in paths.items():
        text = git_text(path)
        baseline[name] = dict(path=path, commit=CLAUDE, defaults=defaults(text),
                              git_blob=subprocess.check_output(
                                  ["git", "rev-parse", f"{CLAUDE}:{path}"], cwd=ROOT).decode().strip())
    val_path = ROOT / "agents/codex/inputs/valeris_848/source.txt"
    baseline["valeris_848"] = dict(path=str(val_path.relative_to(ROOT)),
                                   source_sha256=hashlib.sha256(val_path.read_bytes()).hexdigest(),
                                   defaults=defaults(val_path.read_text(encoding="utf-8-sig")))
    anchors = {}
    for label, token in {
        "predecessor_claim": "VALIDATION (predecessor config SL75:",
        "date_reset": "If Date <> Date[1] then begin",
        "overnight_reset": "ONHigh = High;  ONLow = Low;",
        "vwap_date_reset": "If Date <> vwDate then begin",
        "vwap_weight": "VWgt = Volume;",
        "or_reference_update": "else ORMedApprox = ORMedApprox +",
        "canwork": "CanWork = ORDone and RegimeOK and ADXOK",
        "long_bracket_anchor": "StopPx = Close - SLPoints;",
        "long_entry": 'Buy ("ORB_L")',
        "long_exit_branch": "If MarketPosition = 1 then begin",
        "long_stop_order": 'Sell ("L-SL") next bar at StopPx stop;',
        "session_exit": "SetExitOnClose;",
    }.items():
        anchors[label] = [i+1 for i, line in enumerate(code.splitlines()) if token in line]
        assert anchors[label], label
    examples = []
    for adverse in (0, 10):
        risk = new["SLPoints"] + adverse
        reward = new["SLPoints"] * new["TakeProfitRR"] - adverse
        examples.append(dict(kind="invented adverse entry, not a historical trade", adverse_points=adverse,
                             stop_distance_points=risk, target_distance_points=reward,
                             reward_to_risk=reward/risk,
                             stop_dollars_one_nq=risk*20, stop_dollars_one_mnq=risk*2))
    old_ranges = [10] * 19 + [100]
    prior_ema = 10
    updated_ema = prior_ema + (2/(new["ORMedianDays"]+1)) * (100-prior_ema)
    result = dict(
        verdict="Do not replace current ONB/ORB on source/header evidence",
        baseline_assumption="Current plan ONB ADX30/evaluation and ONB ML/funded; Valeris separate; clarification pending when recorded",
        new_strategy_return_trials=0, new_account_simulations=0,
        source_sha256=hashlib.sha256(INPUT.read_bytes()).hexdigest(), source_lines=len(code.splitlines()),
        literal_defaults=new, baselines=baseline, source_line_anchors=anchors,
        normalized_ct=dict(opening_range="08:30-08:45", first_default_15min_decision="09:00",
                           last_decision="12:00", flatten_signal="14:30",
                           claimed_overnight_start="17:00", actual_date_reset="23:00, including close-stamped bar ending then",
                           chart_timezone="ET per supplied header"),
        nominal_fixed_size_risk=dict(one_nq=70*20, one_mnq=70*2,
                                     four_stops_nq=4*70*20, four_stops_mnq=4*70*2,
                                     limit="nominal signal-anchored brackets only, not a loss bound"),
        entry_examples=examples,
        or_reference_example=dict(kind="invented ranges, no historical returns", last_20_median=statistics.median(old_ranges),
                                  ema_after_large_range=updated_ema,
                                  detail="EMA and rolling median differ even with same nominal lookback"),
        predecessor_claim=dict(stop_points=75, trades=1179, win_percent=59.03, net_nq_approx=241000,
                               max_drawdown_nq_approx=13600, status="unverified header claim for predecessor, not delivered SL70"),
        implementation_limits=["Declared ordinary IOG-off setup does not pre-generate entry-bar explicit brackets",
                               "Bar Magnifier does not generate exits absent from main-bar calculation",
                               "Date reset is not the header's 18:00 ET session anchor",
                               "Volume and total-volume Ticks differ on MultiCharts intraday bars",
                               "No exact SL70 report, fill trace or matched account evidence supplied",
                               "Header production/trading directions are not user instructions"],
        primary_sources=["https://www.multicharts.com/trading-software/index.php?title=How_Scripts_Work",
                         "https://www.multicharts.com/trading-software/index.php?title=Why_is_Data_Playback_strategy_performance_different_from_Backtesting_results%3F",
                         "https://www.multicharts.com/trading-software/index.php?title=SetExitOnClose",
                         "https://www.multicharts.com/trading-software/index.php?title=Volume",
                         "https://www.multicharts.com/trading-software/index.php?title=Ticks"],
    )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(new_defaults=new, normalized_ct=result["normalized_ct"],
                         entry_examples=examples, new_return_trials=0), indent=2))


if __name__ == "__main__":
    main()
