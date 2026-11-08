"""Source arithmetic and invented fixtures; no historical strategy returns."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "agents/codex/inputs/nasdaq_dealer_486642"


def hhi(shares):
    assert abs(sum(shares) - 1) < 1e-12 and all(s >= 0 for s in shares)
    return 10000 * sum(s * s for s in shares)


def main():
    assert hhi([.25] * 4) == 2500
    assert hhi([.7, .1, .1, .1]) > hhi([.25] * 4)
    shares = [.7, .1, .1, .1]
    variance = sum((s - .25) ** 2 for s in shares) / 4
    assert abs(hhi(shares) - 10000 * (1/4 + 4 * variance)) < 1e-10
    # Printed Eq5 has no 1/Q before the sum of squared quote midpoints.
    mids = [100., 100., 100.]
    mu = sum(mids) / len(mids)
    printed = (sum(m*m for m in mids) - mu*mu) / (mu*mu)
    normalized = (sum(m*m for m in mids) / len(mids) - mu*mu) / (mu*mu)
    assert printed == 2 and normalized == 0
    # Source's Eq1 is a doubled distance from midpoint (full effective spread).
    midpoint, fill = 100., 100.01
    full_spread = 2 * abs(fill - midpoint)
    impact_pp = .257 * (2000 - 1000) / 1000
    cents = 17.92 * impact_pp / 100 * 100
    out = {
        "review_local_date": "2026-11-07",
        "source_claims": {"sample": "1995-05 through 2000-12", "rent_cents": 8.76,
            "rent_pct_price": .5434, "conditional_half_life_months": 20.3,
            "observed_half_life_pct": 79.4, "monthly_hhi_coefficient": .257},
        "sample_months_inclusive": (2000-1995)*12 + 12-5+1,
        "hhi_equal_four": hhi([.25]*4), "hhi_concentrated_four": hhi(shares),
        "effective_equal_dealer_count_at_mean_hhi": 10000/2133,
        "hhi_formula_uses_fractional_share_population_variance": True,
        "source_price_impact_example": {"percentage_points": impact_pp, "cents": cents,
            "pct_of_mean_effective_spread": cents/30.75*100},
        "eq5_constant_midpoint_fixture": {"literal_printed": printed, "variance_normalized": normalized,
            "limitation": "Printed equation issue only; original code/data unavailable"},
        "spread_fixture": {"full_effective_spread": full_spread,
            "one_way_distance_from_midpoint": abs(fill-midpoint)},
        "half_life_unobserved_pct": round(100 - 79.4, 1),
        "historical_strategy_return_trials": 0,
        "hashes": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in BASE.rglob('*') if p.is_file()},
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    p = ROOT / "analysis/outputs/codex_nasdaq_dealer_486642/source_audit.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({"months": out['sample_months_inclusive'], "source_example_cents": cents,
                      "eq5_counterexample": "PASS", "strategy_trials": 0}))


if __name__ == '__main__':
    main()
