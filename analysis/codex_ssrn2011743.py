"""Check source-claim arithmetic, not historical returns or loss probabilities."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / "agents/codex/inputs/ssrn2011743/source.pdf"
    result = {
        "paper": "Doguc and Erdogan, March 2006, SSRN 2011743",
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "scope": "Arithmetic on author-reported balances and explicitly hypothetical exposures",
        "new_strategy_return_trials": 0,
        "historical_returns_independently_verified": False,
        "author_claims": {
            "DJI30": {"initial": 100000, "final": 223500},
            "ISE100": {"initial": 100000, "final": 141380000},
        },
        "hypothetical_risk_arithmetic": {
            "margin_fraction_of_equity": .6,
            "notional_per_margin": 10,
            "notional_per_equity": .6 * 10,
            "underlying_adverse_move": .07,
            "equity_loss_fraction_before_costs": .6 * 10 * .07,
            "no_stop_reserve_model_fraction": .2 * 1.5 + .2 * .25,
            "limit": "Linear fixed-exposure illustration only; no gaps, liquidation, hedges, fees or financing modeled. Reserve arithmetic is not a guaranteed maximum loss.",
        },
        "period_warning": "Text alternates 2000-2005 and beginning-2000/end-2004 while calling the result four years; no CAGR inferred.",
    }
    for claim in result["author_claims"].values():
        claim["growth_multiple"] = claim["final"] / claim["initial"]
        claim["total_return_percent"] = (claim["growth_multiple"] - 1) * 100
    assert round(result["author_claims"]["DJI30"]["total_return_percent"], 1) == 123.5
    assert round(result["author_claims"]["ISE100"]["total_return_percent"]) == 141280
    out = ROOT / "analysis/outputs/codex_ssrn2011743"
    out.mkdir(parents=True, exist_ok=True)
    (out / "source_arithmetic.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
