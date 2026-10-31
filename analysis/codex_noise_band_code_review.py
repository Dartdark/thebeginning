"""Static audit and synthetic examples for uploaded CODE.txt; no price replay or returns.

Standard library only. Run from repository root. NQ/MNQ multipliers follow the
repository contract specifications. Toy history records illustrate sampling only.
"""
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "agents/codex/inputs/noise_band_code/source.txt"
OUT = ROOT / "analysis/outputs/codex_noise_band_code_review"
CLAUDE = "8f6b75cc1c6044f712c3ad5f1a774de60dd14859"


def main():
    code = SOURCE.read_text(encoding="utf-8-sig")
    inputs = code.split("Inputs:", 1)[1].split("Vars:", 1)[0]
    defaults = {}
    for name, value in re.findall(r"\b(\w+)\(\s*(-?\d+(?:\.\d+)?|true|false)\s*\)", inputs):
        defaults[name] = value == "true" if value in ("true", "false") else float(value)
    assert defaults["StopLossPoints"] == 50 and defaults["DollarPerPoint"] == 20
    assert defaults["FixedRiskDollars"] == 2000 and defaults["LookbackDays"] == 20
    qty = math.floor(defaults["FixedRiskDollars"] / (defaults["StopLossPoints"] * defaults["DollarPerPoint"]))
    stop_usd = defaults["StopLossPoints"] * defaults["DollarPerPoint"] * qty
    target_usd = stop_usd * defaults["RewardRisk"]
    distances = [dict(symbol=symbol, assumed_actual_big_point_value=bpv,
                      contracts_with_unchanged_inputs=qty, position_stop_usd=stop_usd,
                      position_target_usd=target_usd, actual_stop_points=stop_usd/(qty*bpv),
                      actual_target_points=target_usd/(qty*bpv))
                 for symbol, bpv in (("NQ", 20), ("MNQ", 2))]
    lookback = int(defaults["LookbackDays"])
    history = [0.01] * lookback
    before = sum(history) / lookback
    # Synthetic percentage-move observations; no historical prices or P&L.
    history = [0.03] + history[:-1]
    after = sum(history) / lookback
    assert abs(before - 0.01) < 1e-12 and abs(after - 0.011) < 1e-12
    history_example = dict(scope="toy observations only, not strategy returns",
                           interval_minutes=5, slot_labels=[900, 905, 910],
                           records_per_day_in_bucket=3, prior_records=lookback,
                           average_before_0900_update=before,
                           new_0900_move=0.03, average_seen_at_0905=after,
                           reason="current-day earlier bar is included after append; no future price required")
    anchors = {}
    for name, token in {
        "date_reset": "if Date <> Date[1] then",
        "today_open": "TodayOpen = Open;",
        "previous_close": "PrevClose = Close[1];",
        "stop_count": "if PositionProfit(1) <= -ActualStopDollars then",
        "slot_assignment": "(CurrentMinutes - FirstMinutes) / 15",
        "slot_read": "if SlotCount[Slot] >= LookbackDays then",
        "history_shift": "for ShiftLoop = 100 downto 2",
        "history_append": "MoveToday;",
        "flat_rule": "if Time = FlatSignalTime then",
        "position_stop": "SetStopPosition;",
    }.items():
        anchors[name] = [i+1 for i, line in enumerate(code.splitlines()) if token in line]
        assert anchors[name], name
    prior = {}
    for name in ("TIER_LIST.md", "analysis/outputs/noise_band_bench_output.txt"):
        text = subprocess.check_output(["git", "show", f"{CLAUDE}:{name}"], cwd=ROOT).decode("utf-8")
        keep = [line for line in text.splitlines() if (
            "| Noise-band intraday momentum on NQ" in line or
            "| Noise-area momentum, long only" in line or
            line.startswith("current plan") or line.startswith("+ noise-band") or
            line.startswith("VB 0 / 0, NB 1") or line.startswith("VB 0 / 0, nothing"))]
        prior[name] = dict(commit=CLAUDE, published_rows=keep)
    old_engine = subprocess.check_output(
        ["git", "show", f"{CLAUDE}:analysis/noise_band_chuk_test.py"], cwd=ROOT).decode("utf-8")
    old_cost = float(re.search(r"\(\$([\d.]+) round trip\)", old_engine).group(1))
    grid = (ROOT / "analysis/grid.py").read_text(encoding="utf-8-sig")
    commission = float(re.search(r"^COST\s*=\s*([\d.]+)", grid, re.M).group(1))
    result = dict(
        verdict="REJECT plan promotion on supplied evidence; profitability unknown",
        source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        source_lines=len(code.splitlines()), literal_defaults=defaults,
        new_strategy_return_trials=0, new_account_simulations=0,
        instrument_arithmetic=distances, nominal_stop_multiple_of_2000_trail=stop_usd/2000,
        three_full_nominal_stops_usd=3*stop_usd,
        target_stop_only_gross_breakeven_win_rate=stop_usd/(stop_usd+target_usd),
        target_stop_example_limit="EMA/reversal/time exits mean this is not a required overall win rate",
        history_sampling_example=history_example,
        missing_flat_bar_example=dict(bar_labels=[1425,1435,1440,1555],
                                      any_exact_1430_trigger=False, market_prices_used=False),
        source_line_anchors=anchors, prior_family_context=prior,
        cost_context=dict(prior_noise_nq_roundtrip=old_cost,
                          repo_commission=commission, two_market_stop_fill_ticks_nq=10,
                          repo_two_market_stop_fills_nq_roundtrip=commission+10),
        limits=["No declared instrument, timeframe, session or performance report supplied",
                "Actual chart settings determine anchor and sampling behavior",
                "Dollar stop is nominal; fees, slippage, gaps and external liquidation are not included",
                "PositionProfit is total realized currency P&L on MultiCharts; no units mismatch is alleged",
                "No same-bar reversal double sizing or lack of built-in entry protection is established"],
        primary_sources=["https://www.multicharts.com/trading-software/index.php?title=PositionProfit",
                         "https://www.multicharts.com/trading-software/index.php?title=SetStopPosition",
                         "https://www.multicharts.com/trading-software/index.php?title=BigPointValue",
                         "https://www.multicharts.com/trading-software/index.php?title=How_Scripts_Work"],
    )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(instrument_arithmetic=distances, history_example=history_example,
                         new_return_trials=0), indent=2))


if __name__ == "__main__":
    main()
