"""Audit inputs to the extended-data rebuild without changing caches or live files.

Run from the repository root: python3 analysis/codex_rebuild_readiness.py
This checks coverage and report integrity; it does not generate expected trades.
"""
import csv
import json
import subprocess
from pathlib import Path

import pandas as pd


OUT = Path("analysis/outputs/codex_rebuild_readiness")
REPORTS = {
    "VB": "Backtesting Strategy Performance Report VB v1.xlsx",
    "ONB30": "Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx",
    "MON_BR": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes Bridge Monday Longs.xlsx",
    "EOS": "Backtesting Strategy Performance Report EOS v1.xlsx",
    "ONB_ML2_MC": "Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx",
}


def report_input(name, filename):
    path = Path("mc_reports") / filename
    settings = pd.read_excel(path, sheet_name="Settings", header=None)
    settings = dict(zip(settings[0].astype(str), settings[1].astype(str)))
    raw = pd.read_excel(path, sheet_name="List of Trades", header=2)
    types = raw.Type.astype(str)
    entries = raw[types.str.startswith("Entry")].reset_index(drop=True)
    exits = raw[types.str.startswith("Exit")].reset_index(drop=True)
    issues = []
    for i in range(min(len(entries), len(exits))):
        entry, exit_ = entries.iloc[i], exits.iloc[i]
        et, xt = pd.Timestamp(entry.Date), pd.Timestamp(exit_.Date)
        marker = str(exit_.Signal).strip().lower() == "open"
        if marker or xt < et:
            issues.append(dict(strategy=name, pair=i, entry_time=str(et),
                               exit_time=str(xt), exit_signal=str(exit_.Signal),
                               unfinished=marker, exit_before_entry=xt < et))
    return dict(strategy=name, path=str(path), entries=len(entries), exits=len(exits),
                report_end=settings.get("End Date"),
                last_entry=str(pd.to_datetime(entries.Date).max()),
                last_exit=str(pd.to_datetime(exits.Date).max()),
                issues=len(issues)), issues


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    reports, issues = [], []
    for name, filename in REPORTS.items():
        summary, found = report_input(name, filename)
        reports.append(summary)
        issues.extend(found)
    data = []
    for filename in ("NQ_1min_2026.csv", "NQ_1min_ON_2026.csv"):
        path = Path("data") / filename
        bars = pd.read_csv(path, usecols=["date", "time"])
        keys = bars.date * 10000 + bars.time
        data.append(dict(path=str(path), rows=len(bars), first_key=int(keys.min()),
                         last_key=int(keys.max()), duplicate_keys=int(keys.duplicated().sum())))
    logs = []
    for path in sorted(Path("live/trades").glob("*.csv")):
        with path.open() as stream:
            rows = list(csv.reader(stream))
        closes = [tuple(row) for row in rows if row and row[0] == "CLOSE"]
        logs.append(dict(path=str(path), close_rows=len(closes),
                         unique_close_rows=len(set(closes))))
    payload = dict(source_commit=subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True).strip(), data=data,
        reports=reports, report_issues=issues, chart_logs=logs,
        limitations=["Report End Date is coverage; last trade is not a coverage end.",
                     "Chart CLOSE rows do not establish broker fills.",
                     "A fresh price grid does not extend saved report trade lists.",
                     "No expected-trade replay, cache refresh, plan bench, or trading change performed."])
    (OUT / "audit.json").write_text(json.dumps(payload, indent=2) + "\n")
    pd.DataFrame(reports).to_csv(OUT / "report_coverage.csv", index=False)
    pd.DataFrame(issues).to_csv(OUT / "report_issues.csv", index=False)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
