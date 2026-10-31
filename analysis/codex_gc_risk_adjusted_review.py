"""Static source/risk/clock arithmetic only. No market data or strategy returns.

Run from the repository root. Standard library only. Contract multipliers are from
CME sources cited in the review, not inferred from chart symbol metadata.
"""
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "agents/codex/inputs/gc_risk_adjusted/source.txt"
OUTPUT = ROOT / "analysis/outputs/codex_gc_risk_adjusted_review"
CLAUDE = "b1256664232722b25afefc0004e6f9e04c1976ae"


def main():
    code = SOURCE.read_text(encoding="utf-8-sig")
    no_comments = re.sub(r"\{.*?\}", "", code, flags=re.S)
    inputs = no_comments.split("inputs:", 1)[1].split("variables:", 1)[0]
    defaults = {}
    for name, value in re.findall(r"\b(\w+)\(\s*(-?\d+(?:\.\d+)?|true|false)\s*\)", inputs):
        defaults[name] = value == "true" if value in ("true", "false") else float(value)
    assert defaults["RiskPerTradeUSD"] == 20000
    assert defaults["MaxContracts"] == 20
    assert defaults["LongStopADRPct"] == defaults["ShortStopADRPct"] == 140
    assert not defaults["ForceMinOneContract"]
    anchors = {}
    for name, token in {
        "risk_budget": "RiskPerTradeUSD( 20000 )",
        "daily_adr": "adrD = Average( High - Low, ADRLen ) of data2;",
        "window": "inWindow = (Time >= adjRangeStart) or (Time < adjRangeEnd);",
        "adr_lock": "adrLock  = adrD;",
        "drift": "driftRatio = AbsValue( slope )",
        "long_quantity": "qtyL = IntPortion( RiskPerTradeUSD / riskPerCtrL )",
        "long_entry": 'Buy       ( "Asia_long"',
        "short_entry": 'SellShort ( "Asia_short"',
        "long_exit_branch": "if MarketPosition = 1 then begin",
        "long_stop": "SetStopLoss( stopDistL * BigPointValue * CurrentContracts );",
        "time_exit": "if Time >= adjExitTime then begin",
    }.items():
        anchors[name] = [i + 1 for i, line in enumerate(code.splitlines()) if token in line]
        assert anchors[name], name
    examples = []
    # Illustrations, not observed historical ADR or trade risk.
    for adr in (10, 50, 100):
        for symbol, point_value in (("GC", 100), ("MGC", 10)):
            stop_points = adr * defaults["LongStopADRPct"] / 100
            per_contract = stop_points * point_value
            quantity = min(int(defaults["MaxContracts"]), math.floor(defaults["RiskPerTradeUSD"] / per_contract))
            examples.append(dict(illustrative_adr_points=adr, symbol=symbol,
                                 stop_points=stop_points, stop_dollars_per_contract=per_contract,
                                 contracts=quantity, nominal_stop_dollars=quantity * per_contract,
                                 measured_historical_risk=False))
    def hhmm(minutes):
        return (minutes // 60) * 100 + minutes % 60
    included = [m for m in range(0, 1440, 5)
                if hhmm(m) >= defaults["RangeStart"] or hhmm(m) < defaults["RangeEnd"]]
    assert min(included) == 1200 and max(included) == 1435 and len(included) == 48
    source_rows = {}
    for path, query in (("WATCHLIST.md", "| 6 | Gold Asian-range"),
                        ("TIER_LIST.md", "| Gold Asian-range breakout on gold"),
                        ("TIER_LIST.md", "| Gold and bitcoin follow-ups")):
        text = subprocess.check_output(["git", "show", f"{CLAUDE}:{path}"], cwd=ROOT).decode("utf-8")
        row = next(line for line in text.splitlines() if query in line)
        source_rows[query] = dict(path=path, commit=CLAUDE, row=row)
    result = dict(
        verdict="REJECT supplied configuration for current plan; exact-version profitability unverified",
        new_strategy_return_trials=0, new_account_simulations=0,
        source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        source_bytes=SOURCE.stat().st_size, source_lines=len(code.splitlines()),
        literal_defaults=defaults, source_line_anchors=anchors,
        nominal_risk_budget_multiple_of_2000_trail=defaults["RiskPerTradeUSD"] / 2000,
        cme_point_values=dict(GC=100, MGC=10),
        sizing_examples=examples,
        gross_bracket_reward_to_risk=dict(
            long=defaults["LongTargetADRPct"] / defaults["LongStopADRPct"],
            short=defaults["ShortTargetADRPct"] / defaults["ShortStopADRPct"]),
        clock_diagnostic=dict(assumption="5-minute bars stamped at close, timeshift 0",
                              included_labels="20:00 through 23:55", count=len(included),
                              represented_intervals="19:55 through 23:55",
                              first_excluded_lock_bar_label="00:00",
                              first_order_bar_label="00:05; may activate on next tick around 00:00, not necessarily a five-minute delay"),
        prior_research=source_rows,
        primary_sources=["https://www.cmegroup.com/education/lessons/product-gold",
                         "https://www.cmegroup.com/education/lessons/micro-gold-and-micro-silver-futures-product-overview.html",
                         "https://www.multicharts.com/trading-software/index.php?title=Realtime-History_Matching",
                         "https://www.multicharts.com/trading-software/index.php?title=SetStopLoss",
                         "https://www.multicharts.com/trading-software/index.php?title=How_Scripts_Work"],
        limits=["Synthetic examples are not current ADR readings or historical trades",
                "Stops exclude commissions, slippage and gaps; account risk includes all positions",
                "No original performance report, trade ledger, chart properties or selection history supplied",
                "Unlagged Data2 does not by itself prove look-ahead",
                "Entry protection and OCO behavior require platform-specific evidence, not this arithmetic script"],
    )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"new_return_trials": 0, "risk_budget_multiple_of_trail": 10,
                      "illustrative_adr_50": [row for row in examples if row["illustrative_adr_points"] == 50],
                      "clock": result["clock_diagnostic"]}, indent=2))


if __name__ == "__main__":
    main()
