"""No-return owned-input schema/date audit for the uploaded VIX ETP paper."""
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
    rows = []
    for filename in ["VIX_daily.csv", "VIXY_daily.csv", "SPY_daily.csv", "VIX3M_daily.csv"]:
        path = Path("data") / filename
        columns = pd.read_csv(path, nrows=0).columns.tolist()
        date_column = next(c for c in columns if c.casefold() == "date")
        dates = pd.read_csv(path, usecols=[date_column])[date_column]
        rows.append(dict(path=str(path), columns=columns, rows=len(dates),
                         first_date=str(dates.min()), last_date=str(dates.max()),
                         sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    source_panel = Path("/workspace/calvados_data_prior/archive_7a8df408/data/raw/vix_futures_data")
    result = dict(source_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                  paper_sha256=hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
                  owned_schema_dates=rows,
                  prior_dated_VX_scratch_exists=source_panel.exists(),
                  prior_dated_VX_manifest="agents/codex/inputs/calvados_2379985_20261030/downloaded_panel_manifest.json",
                  candidate_ETP_filenames=sorted(str(p) for p in Path("data").glob("*")
                                                 if p.is_file() and any(s in p.name.casefold()
                                                                       for s in ["xiv", "vxx", "svxy", "vxz"])),
                  economic_trials=0, price_returns_read=False,
                  limitation="Filename/schema/date audit, not an exhaustive inventory or source reproduction.")
    out = Path("analysis/outputs/codex_vix_etp_2753300")
    out.mkdir(parents=True, exist_ok=True)
    (out / "owned_input_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
