"""Audit the extended-data refresh; optionally rebuild with open report rows excluded.

Run from the repository root:
  python3 analysis/codex_refresh_audit.py --rebuild
Writes only scratch_data/ and analysis/outputs/codex_refresh_audit/.
No live changes, report edits, parameter searches or strategy promotion.
"""
import argparse
import json
from pathlib import Path
import pickle
import runpy
import subprocess
import sys
import warnings

import numpy as np
import pandas as pd

import portfolio
from build_lab import REPORTS
from bridge_monday_confirm import F as BRIDGE_REPORT
from combine_levers_test import ONB30

ORIGINAL_LOAD_MC = portfolio.load_mc
OUT = Path("analysis/outputs/codex_refresh_audit")


def report_rows(path):
    raw = pd.read_excel(path, sheet_name="List of Trades", header=2)
    entries = raw[raw.Type.astype(str).str.startswith("Entry")].reset_index(drop=True)
    exits = raw[raw.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
    if len(entries) != len(exits):
        raise ValueError(f"Unpaired report rows: {path}")
    return entries, exits


def closed_report_mask(g, entries, exits):
    """Mirror load_mc's date selection; exclude only explicit `open` sentinels.

    Do not guess a close for unfinished positions or silently discard other errors.
    """
    if len(entries) != len(exits):
        raise ValueError("Unpaired report rows")
    dates = pd.to_datetime(entries.Date).dt.strftime("%Y%m%d").astype(int).to_numpy()
    rows = np.searchsorted(g.dates, dates)
    keep = (rows < g.D) & (g.dates[np.minimum(rows, g.D - 1)] == dates)
    is_open = exits.Signal.fillna("").astype(str).str.strip().str.casefold().eq("open").to_numpy()
    return ~is_open[keep]


def load_closed_mc(g, path):
    entries, exits = report_rows(path)
    trades = ORIGINAL_LOAD_MC(g, path)
    mask = closed_report_mask(g, entries, exits)
    if len(mask) != len(trades):
        raise ValueError(f"Report alignment changed: {path}")
    return trades.loc[mask].reset_index(drop=True)


def rebuild(scratch):
    """Use the original builder and its tools with a scoped importer adapter."""
    old_argv = sys.argv[:]
    try:
        portfolio.load_mc = load_closed_mc
        sys.argv = ["analysis/build_lab.py", str(scratch)]
        runpy.run_path("analysis/build_lab.py", run_name="__main__")
    finally:
        portfolio.load_mc = ORIGINAL_LOAD_MC
        sys.argv = old_argv


def audit(scratch):
    OUT.mkdir(parents=True, exist_ok=True)
    with (scratch / "g24.pkl").open("rb") as f:
        g = pickle.load(f)
    reports = {k: p for k, (p, _) in REPORTS.items()}
    reports.update(ONB30=ONB30, MON_BR_MC=BRIDGE_REPORT)
    coverage = []
    excluded = []
    for name, path in reports.items():
        entries, exits = report_rows(path)
        settings = pd.read_excel(path, sheet_name="Settings", header=None)
        end = settings.loc[settings[0].astype(str).eq("End Date"), 1]
        opened = exits.Signal.fillna("").astype(str).str.strip().str.casefold().eq("open")
        for i in np.flatnonzero(opened):
            excluded.append(dict(strategy=name, report=path, entry=str(entries.Date[i]),
                                 exit_label=str(exits.Date[i]), signal=str(exits.Signal[i]),
                                 marked_pnl=float(entries["Profit ($)"].iloc[i])))
        coverage.append(dict(strategy=name, report=path,
                             report_end=str(end.iloc[0]) if len(end) else None,
                             last_closed_exit=str(pd.to_datetime(exits.loc[~opened, "Date"]).max()),
                             closed_trades=int((~opened).sum()), open_positions=int(opened.sum())))
    pd.DataFrame(coverage).to_csv(OUT / "report_coverage.csv", index=False)
    pd.DataFrame(excluded).to_csv(OUT / "excluded_open_positions.csv", index=False)
    cache = json.loads(Path("analysis/outputs/dashboard/bt_cache.json").read_text())
    summary = dict(raw_grid_end=str(pd.Timestamp(g.ts[-1]).date()),
                   source_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                   raw_last_trading_date=str(pd.Timestamp(g.ts[g.trading[-1]]).date()),
                   dashboard_daily_end=max(cache["daily"]),
                   dashboard_last_trade={k: max(v["day"], default=None) for k, v in cache["bt"].items()},
                   lab_rebuilt=(scratch / "lab.pkl").exists(),
                   report_coverage=coverage, excluded_open_positions=excluded,
                   limitation="New raw bars do not create new MC trades. Do not label uncovered days as no-signal days.")
    summary["logged_files"] = [str(p) for p in sorted(Path("live/trades").glob("*.csv"))]
    summary["review_window"] = {"start": "2026-10-12", "end": "2026-10-28"}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch", type=Path, default=Path("scratch_data"))
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    if args.rebuild:
        rebuild(args.scratch)
    audit(args.scratch)


if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        main()
