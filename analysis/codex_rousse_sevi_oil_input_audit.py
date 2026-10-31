"""No-return schema/clock audit for uploaded SSRN 2874907; run from repo root."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import pandas as pd


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    args = parser.parse_args()
    out = Path("analysis/outputs/codex_rousse_sevi_oil_input_audit")
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in sorted(Path("data").glob("CL_1min_*.csv")):
        header = pd.read_csv(path, nrows=0).columns.tolist()
        dates = pd.read_csv(path, usecols=["date"])["date"]
        rows.append(dict(path=str(path), columns=header, rows=len(dates),
                         first_date=int(dates.min()), last_date=int(dates.max()),
                         has_trade_sequence=False, has_survey_panel=False))
    component_path = Path("analysis/outputs/codex_eia_inventory_input_gate/design_components.csv")
    components = pd.read_csv(component_path)
    clock = components.actual_release_clock_verified.astype(str).str.lower().eq("true")
    vintage = components.immutable_first_publication_verified.astype(str).str.lower().eq("true")
    # Name-based discovery is deliberately not a claim to have inspected every file's contents.
    matches = sorted(str(p) for p in Path("data").rglob("*") if p.is_file() and
                     any(s in p.name.casefold() for s in ("bloomberg", "consensus", "forecast", "survey")))
    result = dict(source_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                  paper_sha256=hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
                  price_schemas=rows, data_name_matches_for_survey=matches,
                  component_file=str(component_path), component_columns=components.columns.tolist(),
                  component_rows=len(components), verified_release_clock_rows=int(clock.sum()),
                  verified_first_publication_rows=int(vintage.sum()),
                  author_sample=dict(announcements=402, positive_3sigma=43, negative_3sigma=47,
                                     first="2007-02-07", last="2014-10-22"),
                  power_assumptions=dict(design_weeks=260, unchanged_positive_frequency=43 / 402,
                                         expected_positive_events=260 * 43 / 402,
                                         hypothetical_trade_sd_pct=0.5,
                                         t2_required_net_mean_pct=2 * 0.5 / (260 * 43 / 402) ** 0.5),
                  economic_trials=0, price_returns_read=False,
                  verdict="NEEDS DATA for exact replication; DON'T TEST hindsight-conditioned pre-release rule",
                  missing=["point-in-time Bloomberg individual forecasts/median and cross-sectional dispersion",
                           "first-publication matching actuals and exceptional release/receipt clocks",
                           "same-contract sequenced CL transactions for the source tick-rule OI",
                           "a causal, frozen trading rule with adequate power and native costs"],
                  limitations=["Schema and date audit only; raw CL prices were not loaded or tested.",
                               "Filename discovery cannot establish the absence of differently named inputs.",
                               "Author event counts and assumed SD are not measured 2018-22 trade results."])
    (out / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "price_schemas"}, indent=2))


if __name__ == "__main__":
    main()
