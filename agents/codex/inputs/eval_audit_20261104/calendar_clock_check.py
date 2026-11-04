"""Timestamp-only CME closure audit. No OHLC, signals, P&L or account results.

Run with the configured Python from the repository root. This writes only the
companion calendar_clock_counts.json, and reads only date/time CSV fields.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).with_name("calendar_clock_counts.json")
TIMES = [0, 1, 2, 3, 759, 1515, *range(1516, 1531), 1531, 1559,
         1600, 1601, 1630, 1659, 1700, 1701, 1702, 1703]


def main():
    rows = []
    for market in ["NQ", "ES"]:
        for year in range(2018, 2027):
            name = f"{market}_1min_{'ON_' if market == 'NQ' else ''}{year}.csv"
            path = ROOT / "data" / name
            df = pd.read_csv(path, usecols=["date", "time"])
            counts = df.time.value_counts()
            interval = df[(df.time >= 1516) & (df.time <= 1530)]
            old = interval[interval.date < 20210628]
            with path.open("rb") as handle:
                digest = hashlib.file_digest(handle, "sha256").hexdigest()
            rows.append({
                "path": str(path.relative_to(ROOT)), "sha256": digest,
                "date_min": int(df.date.min()), "date_max": int(df.date.max()),
                "rows": len(df),
                "clock_counts": {str(t).zfill(4): int(counts.get(t, 0)) for t in TIMES},
                "first_observed_1516_to_1530_on_or_after_transition": (
                    int(interval.loc[interval.date >= 20210628, "date"].min())
                    if (interval.date >= 20210628).any() else None),
                "pretransition_observed_halt_rows": old.to_dict("records"),
            })
    sample_days = {}
    for date in [20180108, 20190107, 20200106, 20210104, 20210621, 20210628, 20220110]:
        got = set()
        for name in [f"NQ_1min_{date // 10000}.csv", f"NQ_1min_ON_{date // 10000}.csv"]:
            df = pd.read_csv(ROOT / "data" / name, usecols=["date", "time"])
            got.update(df.loc[df.date == date, "time"].tolist())
        expected = [h * 100 + m for h in range(16) for m in range(60)]
        sample_days[str(date)] = [str(t).zfill(4) for t in expected if t not in got]
    # A known source Bridge ticket's timestamp range, supplied by the builder.
    # Dates/times are audited without reading the trade's P&L or OHLC prices.
    got = set()
    for name in ["NQ_1min_2018.csv", "NQ_1min_ON_2018.csv"]:
        df = pd.read_csv(ROOT / "data" / name, usecols=["date", "time"])
        for date, time in df[df.date.isin([20180429, 20180430])].itertuples(index=False, name=None):
            got.add(pd.Timestamp(str(date)) + pd.Timedelta(hours=time // 100, minutes=time % 100))
    expected = pd.date_range("2018-04-29 19:00", "2018-04-30 15:55", freq="min")
    missing = [str(ts) for ts in expected if ts not in got]
    OUT.write_text(json.dumps({
        "purpose": "Timestamp counts only; no return or portfolio test",
        "clock_basis": "Repository Grid24 close-labeled local Chicago wall-clock; exchange schedule interpreted in America/Chicago, not fixed UTC-6",
        "input_columns": ["date", "time"], "files": rows,
        "sample_missing_close_labels_0000_through1559": sample_days,
        "bridge_timestamp_sample": {
            "start": str(expected[0]), "end": str(expected[-1]),
            "missing": missing,
            "known_pause_labels": [f"2018-04-30 15:{m:02d}:00" for m in range(16, 31)],
            "unresolved": [ts for ts in missing if not ts.startswith("2018-04-30 15:")],
        },
    }, indent=2) + "\n")
    print(f"Wrote {OUT.relative_to(ROOT)}; no returns computed")


if __name__ == "__main__":
    main()
