"""Reproduce selected theoretical calculations in the uploaded June 2005 draft.

No price data, signal construction, strategy return test or execution calibration.
"""
import hashlib
import json
from math import exp, isclose
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def model(rho_t, permanent_share):
    # Normalize X0=q=T=1. lambda=permanent_share/q; kappa=1/q-lambda.
    a = rho_t
    lam = permanent_share
    kappa = 1 - lam
    uniform = lam / 2 + kappa * (a - (1 - exp(-a))) / a**2
    optimal = lam / 2 + kappa / (a + 2)
    block = 1 / (a + 2)
    continuous = a / (a + 2)
    assert isclose(2 * block + continuous, 1)
    assert optimal <= uniform + 1e-12
    return dict(rho_T=a, lambda_q=lam, initial_fraction=block,
                middle_fraction=continuous, final_fraction=block,
                normalized_uniform_impact_cost=uniform,
                normalized_optimal_impact_cost=optimal,
                impact_cost_saving_percent=100 * (uniform - optimal) / uniform)


def main():
    out = ROOT / "analysis/outputs/codex_ssrn666541"
    out.mkdir(parents=True, exist_ok=True)
    rows = [model(a, l) for a in (.5, 1, 2, 4, 10, 300) for l in (.5, 0)]
    for lam, expected in ((.5, 4.32), (0, 11.92)):
        r = model(2, lam)
        assert abs(r["impact_cost_saving_percent"] - expected) < .005
        assert r["initial_fraction"] == r["final_fraction"] == .25
        assert r["middle_fraction"] == .5
    source = ROOT / "agents/codex/inputs/ssrn666541/ssrn-666541.pdf"
    result = dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        source_version="June 8, 2005 uploaded draft, SSRN 666541",
        scope="Selected Proposition 3 / Section 7.2 model arithmetic only",
        new_strategy_return_trials=0, market_data_calibration=False,
        native_execution_savings_measured=False,
        cost_denominator="Price impact only; excludes initial ask-value term, spread and commissions",
        table2_rho2_reproduced_to_printed_precision=True, rows=rows)
    (out / "model_arithmetic.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
