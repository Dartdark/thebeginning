"""Arithmetic checks on manually transcribed, visually checked source tables.

Not an independent replication of the estimates, return test or cost calibration.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    pdf = ROOT / "agents/codex/inputs/ssrn754946/source.pdf"
    spreads = []
    for market, floor, screen in (("Japanese Yen", 22.01, 18.22),
                                  ("British Pound", 23.07, 17.54),
                                  ("Euro FX", 21.74, 15.94)):
        spreads.append(dict(market=market, floor=floor, screen=screen,
                            floor_minus_screen=round(floor-screen, 2)))
    # Preserve inconsistent printed values rather than silently repairing them.
    yen = dict(table="3.C", label="March 2004 Yen: mean information-share midpoint",
               floor_printed=.4932, globex_printed=.5860,
               globex_lower=.2447, globex_upper=.7689)
    yen["printed_midpoint_sum"] = yen["floor_printed"] + yen["globex_printed"]
    yen["midpoint_from_printed_globex_bounds"] = (yen["globex_lower"]+yen["globex_upper"])/2
    euro = dict(table="5.B", label="September 2003 Euro: mean common-factor weights",
                floor_printed=.3019, globex_printed=.6891)
    euro["printed_weight_sum"] = euro["floor_printed"] + euro["globex_printed"]
    assert abs(yen["printed_midpoint_sum"] - 1) > .01
    assert abs(euro["printed_weight_sum"] - 1) > .001
    result = dict(source_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
        source_version="May 2005, SSRN754946", source_pdf_pages=54,
        sample="2003-01-02 through 2004-03-05",
        source_table1_all_contracts_estimated_spreads_usd_per_contract=spreads,
        source_common_factor_globex_weights=dict(
            yen_march2003=.2865, yen_march2004=.5011,
            euro_march2003=.5427, euro_march2004=.7377),
        visually_confirmed_printed_table_inconsistencies=[yen, euro],
        interpretation="Internal arithmetic discrepancies, potentially printing errors; not evidence that all underlying estimates are wrong",
        new_strategy_return_trials=0, estimates_independently_reproduced=False,
        native_execution_savings_measured=False)
    out = ROOT / "analysis/outputs/codex_ssrn754946"
    out.mkdir(parents=True, exist_ok=True)
    (out / "source_checks.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
