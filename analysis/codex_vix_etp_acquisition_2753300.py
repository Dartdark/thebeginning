"""Audit acquired public inputs for SSRN2753300; no strategy signals or returns.

Raw third-party inputs stay outside Git. This audits the pinned archive and public table snapshot,
not source authenticity, redistribution rights, historical availability or executable fills.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

import pandas as pd

ARCHIVE_SHA = "71dc39799b8290e608b1fca8c62b55e6c58fc1d9975ad4ba41a34f42d4fe330b"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path("/workspace/vix2753300_acquisition"))
    args = p.parse_args()
    root = args.root
    out = Path("analysis/outputs/codex_vix_etp_acquisition_2753300")
    out.mkdir(parents=True, exist_ok=True)
    archive = root / "Pustak-007_ml_risk_overlay_7a8df4089664c339de9a4c5900cecdbe9d5b954e.zip"
    if digest(archive) != ARCHIVE_SHA:
        raise ValueError("Pinned archive hash mismatch")
    rows = []
    raw = root / "raw_vx"
    raw.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            if "/data/raw/vix_futures_data/" not in name or not name.endswith(".csv"):
                continue
            b = z.read(name)
            (raw / Path(name).name).write_bytes(b)
            lines = b.decode("utf-8-sig").splitlines()
            headers = [i for i, line in enumerate(lines) if line.startswith("Trade Date,Futures,")]
            if len(headers) != 1:
                raise ValueError(f"Ambiguous native header: {name}")
            d = pd.read_csv(io.BytesIO(b), skiprows=headers[0])
            dates = pd.to_datetime(d["Trade Date"], format="mixed", errors="raise")
            rows.append(dict(file=Path(name).name, bytes=len(b), sha256=hashlib.sha256(b).hexdigest(),
                             git_blob_sha=hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest(),
                             rows=len(d), first=str(dates.min().date()), last=str(dates.max().date()),
                             preface_lines=headers[0], zero_settles=int((d.Settle <= 0).sum()),
                             zero_opens=int((d.Open <= 0).sum()), high_below_low=int((d.High < d.Low).sum()),
                             label=str(d.Futures.iloc[-1])))
    census = pd.DataFrame(rows)
    census.to_csv(out / "vx_file_census.csv", index=False)
    snapshots = []
    for name in ["xiv_public_table_snapshot.csv", "xjcarter_VXX.csv"]:
        path = root / name
        d = pd.read_csv(path)
        dc = next(c for c in d if c.casefold() == "date")
        dates = pd.to_datetime(d[dc])
        snapshots.append(dict(file=name, sha256=digest(path), rows=len(d), first=str(dates.min().date()),
                              last=str(dates.max().date()), duplicate_dates=int(dates.duplicated().sum()),
                              columns=list(d.columns)))
    summary = dict(archive_sha256=ARCHIVE_SHA, archive_bytes=archive.stat().st_size,
                   archive_url="https://codeload.github.com/Pustak-007/ml_risk_overlay/zip/7a8df4089664c339de9a4c5900cecdbe9d5b954e",
                   raw_monthly_VX_files=len(census), rows=int(census.rows.sum()),
                   earliest_native_observation=min(census["first"]), latest_native_observation=max(census["last"]),
                   zero_settles=int(census.zero_settles.sum()), zero_opens=int(census.zero_opens.sum()),
                   high_below_low=int(census.high_below_low.sum()), preface_files=int((census.preface_lines > 0).sum()),
                   snapshots=snapshots, raw_redistributed=False, economic_trials=0,
                   admission="PARTIAL ACQUISITION ONLY; not ready for economic replay",
                   remaining=["complete original XIV and original VXX market-price histories and adjustments",
                              "source 2006-14 prelaunch indicative series for exact original replication",
                              "VX pre-2007 units, native expiries/rolls, source parity and publication clocks",
                              "causal fill protocol and product lifecycle/redemption treatment"])
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
