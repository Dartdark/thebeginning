"""Preregistration inventory only: fund input checks, entry-date counts and assumed power.

No strategy prices, exits, P&L, candidate features, returns, caches or account tools.
Fund history is read from immutable git blobs; only the MC Type/Date columns are read.
"""
from __future__ import annotations

import hashlib
import io
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

SOURCE = "c23fc02"
OUT = Path("analysis/outputs/codex_ldf_flow_prereg")
REPORT = Path("mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Late Day Flow.xlsx")
ASSUMED_SD = 810.0  # Claude's evidence-sheet assumption; never estimated from returns here.


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    funds = []
    for ticker, leverage in (("TQQQ", 3), ("SQQQ", -3), ("QLD", 2), ("QID", -2)):
        path = f"data/letf/{ticker}.csv"
        blob = subprocess.check_output(["git", "show", f"{SOURCE}:{path}"])
        x = pd.read_csv(io.BytesIO(blob), usecols=["Date", "NAV", "Shares Outstanding (000)", "Assets Under Management"])
        d = pd.to_datetime(x.Date, format="%m/%d/%Y")
        a = pd.to_numeric(x["Assets Under Management"], errors="raise")
        nav = pd.to_numeric(x.NAV, errors="raise")
        shares = pd.to_numeric(x["Shares Outstanding (000)"], errors="raise") * 1000
        err = abs(nav * shares / a - 1)
        study = d >= "2017-01-01"  # Includes warmup; earlier history is inventoried but never used.
        assert not d.duplicated().any() and (a > 0).all() and (nav > 0).all()
        assert (shares[study] > 0).all() and err[study].max() <= .01
        funds.append(dict(ticker=ticker, leverage=leverage, reset_coefficient=leverage*(leverage-1),
                          source=f"{SOURCE}:{path}", sha256=hashlib.sha256(blob).hexdigest(),
                          rows=len(x), first=str(d.min().date()), last=str(d.max().date()),
                          rows_2018_to_2026_10_09=int(d.between("2018-01-02", "2026-10-09").sum()),
                          validation_start="2017-01-01", max_aum_identity_relative_error_2017_on=float(err[study].max()),
                          zero_share_rows_before_2017=int(((shares <= 0) & ~study).sum()),
                          publication_time_verified=False,
                          historical_vintages_verified=False))
    pd.DataFrame(funds).to_csv(OUT / "fund_input_inventory.csv", index=False)

    entries = pd.read_excel(REPORT, sheet_name="List of Trades", header=2, usecols=["Type", "Date"])
    dates = pd.to_datetime(entries.loc[entries.Type.astype(str).str.startswith("Entry"), "Date"])
    dates = dates[dates >= "2018-01-01"]
    beyond_cutoff = int((dates >= "2026-10-10").sum())
    dates = dates[dates < "2026-10-10"]
    dates.dt.year.value_counts().sort_index().rename_axis("year").rename("entry_count").to_csv(OUT / "entry_counts_by_year.csv")
    n = int(dates.between("2018-01-01", "2022-12-31 23:59:59").sum())
    per_tercile = n // 3
    contrast_se = ASSUMED_SD * np.sqrt(2.0 / per_tercile)
    power = dict(design_entry_count=n, all_entry_count=len(dates), excluded_entries_after_2026_10_09=beyond_cutoff,
                 nominal_entries_per_extreme_tercile=per_tercile,
                 assumed_full_nq_trade_sd=ASSUMED_SD,
                 iid_extreme_tercile_gap_for_t2=2.0*contrast_se,
                 iid_extreme_tercile_gap_for_approx_80pct_power=2.8*contrast_se,
                 formula="sd * sqrt(1/n_high + 1/n_low); t2 multiplier 2; approximate 80% power multiplier 2.8",
                 caveat="Illustrative IID planning bounds only; missing inputs, controls and serial dependence reduce effective power.")
    (OUT / "power_assumptions.json").write_text(json.dumps(power, indent=2) + "\n")
    manifest = dict(source_commit=SOURCE, report=str(REPORT), report_sha256=hashlib.sha256(REPORT.read_bytes()).hexdigest(),
                    read_mc_columns=["Type", "Date"], return_trials=0, candidate_features_calculated=False,
                    candidate_returns_calculated=False, account_simulations_run=False, research_caches_built=False,
                    publication_timing_and_revision_risk="UNRESOLVED", assumed_sd_source="Claude 1_letf_dollar_flow.md")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(power, indent=2))
    print("Fund identity checks passed. No candidate feature, return or account test executed.")


if __name__ == "__main__":
    main()
