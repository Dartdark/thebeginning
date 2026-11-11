"""Input-only NQ adapter: hashes, minute bars and complete five-minute aggregation.

No signals, labels, price-return calculations or execution outcomes. Import is inert.
Native 2018--22 is the primary bar/flow source. Later legacy input is explicit and
must only be requested after the caller's design gate permits historical validation.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NATIVE_DIR = Path("agents/codex/inputs/bridge_native_2018_22_20261108")
OHLC = ["open", "high", "low", "close"]
FIELDS = OHLC + ["volume", "buy", "sell"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _clock(date, time, source_zone):
    stamp = pd.to_datetime(date.astype(str) + " " + time.astype(str), errors="raise")
    return pd.DatetimeIndex(stamp).tz_localize(source_zone, ambiguous="raise", nonexistent="raise").tz_convert("America/Chicago").tz_localize(None)


def _deduplicate(frame, label):
    duplicate = frame.index.duplicated(keep=False)
    if duplicate.any():
        changed = frame[duplicate].groupby(level=0).nunique(dropna=False).gt(1).any(axis=1)
        if changed.any():
            raise ValueError(f"{label}: {int(changed.sum())} conflicting minute keys")
    count = int(frame.index.duplicated().sum())
    return frame[~frame.index.duplicated()].sort_index(), count


def _validate(frame, require_flow=True):
    cols = FIELDS if require_flow else OHLC + ["volume"]
    values = frame[cols].to_numpy(float)
    if not np.isfinite(values).all():
        raise ValueError("Nonfinite required input values")
    if (frame.volume < 0).any():
        raise ValueError("Negative volume")
    if not ((frame.low <= frame.open) & (frame.low <= frame.close) & (frame.high >= frame.open) & (frame.high >= frame.close) & (frame.low <= frame.high)).all():
        raise ValueError("Invalid OHLC geometry")
    if not np.allclose(frame[OHLC].to_numpy(float) * 4, np.round(frame[OHLC].to_numpy(float) * 4), rtol=0, atol=1e-8):
        raise ValueError("OHLC not on NQ quarter-point ticks")
    if require_flow:
        qty = frame[["volume", "buy", "sell"]].to_numpy(float)
        if (qty < 0).any() or not np.allclose(qty, np.round(qty), rtol=0, atol=1e-8):
            raise ValueError("Invalid native contract quantities")
        if not np.array_equal(frame.volume.to_numpy(), (frame.buy + frame.sell).to_numpy()):
            raise ValueError("Native total != buy + sell")
    if (frame.index.second != 0).any() or (frame.index.microsecond != 0).any():
        raise ValueError("Input is not minute-close aligned")


def load_design_native(root=ROOT, years=range(2018, 2023), with_audit=False):
    """Return minutes, indexed by naive CT minute-close wall time.

    ``minutes.attrs['input_audit']`` carries the receipt; ``with_audit=True``
    returns ``(minutes, audit)`` for callers that prefer an explicit tuple.

    Exact compressed AND decompressed hashes are required. No old NQ export is
    spliced into native OHLCV. No missing minute is filled. Native flow is a vendor
    aggressor-category claim, not independently reconstructed exchange tape.
    """
    root = Path(root)
    directory = root / NATIVE_DIR
    manifest_path = directory / "transfer_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    frames, files = [], {}
    for year in years:
        name = f"NQ_1min_native_ET_close_{int(year)}.csv.gz"
        meta = manifest["files"][name]
        path = directory / name
        compressed = path.read_bytes()
        raw = gzip.decompress(compressed)
        if len(compressed) != meta["compressed_bytes"] or hashlib.sha256(compressed).hexdigest() != meta["compressed_sha256"]:
            raise ValueError(f"Compressed source changed: {name}")
        if len(raw) != meta["original_bytes"] or hashlib.sha256(raw).hexdigest() != meta["original_sha256"]:
            raise ValueError(f"Original source changed: {name}")
        source = pd.read_csv(io.BytesIO(raw), dtype={"Date": str, "Time": str})
        if source.columns.tolist() != manifest["fields"]:
            raise ValueError(f"Native schema changed: {name}")
        stamp = pd.to_datetime(source.Date + " " + source.Time, format="%m/%d/%Y %H:%M", errors="raise")
        index = pd.DatetimeIndex(stamp).tz_localize("America/New_York", ambiguous="raise", nonexistent="raise").tz_convert("America/Chicago").tz_localize(None)
        frame = source[["Open", "High", "Low", "Close", "Volume", "UpVol", "DownVol"]].copy()
        frame.columns = FIELDS
        frame.index = index
        _validate(frame)
        frames.append(frame)
        files[str(path.relative_to(root))] = dict(rows=len(frame), compressed_sha256=meta["compressed_sha256"], original_sha256=meta["original_sha256"])
    if not frames:
        raise ValueError("No native years requested")
    frame, duplicates = _deduplicate(pd.concat(frames), "Native source")
    # The packaged native source was verified to have no duplicates. Treat any new
    # duplicate, including an exact one, as an unexpected native-package change.
    if duplicates:
        raise ValueError(f"Unexpected duplicate native keys: {duplicates}")
    audit = dict(files=files, transfer_manifest_sha256=sha(manifest_path), rows=len(frame),
                 first=str(frame.index.min()), last=str(frame.index.max()),
                 timestamp="America/New_York close -> America/Chicago close; no extra minute added",
                 duplicate_keys=duplicates, missing_minutes_filled=0,
                 total_volume="native Volume, verified equal to UpVol+DownVol",
                 provenance_limits=manifest["limits"], source="native 2018--22, no price/flow splicing")
    frame.attrs["input_audit"] = audit
    return (frame, audit) if with_audit else frame


def aggregate_complete(frame, minutes=5, require_flow=True):
    """Right-closed bars: 09:00 contains native closes 08:56 through 09:00.

    A bar needs every constituent minute. Shared Grid24.bars uses nan aggregators,
    so it must not itself decide signal-bar completeness. Midnight bars may use the
    preceding date's final minutes. Zero-volume complete bars remain zero-volume.
    """
    if minutes <= 0 or 1440 % minutes:
        raise ValueError("Bar size must divide a calendar day")
    if frame.index.has_duplicates or not frame.index.is_monotonic_increasing:
        raise ValueError("Unique sorted minute index required")
    required = FIELDS if require_flow else OHLC + ["volume"]
    usable = np.isfinite(frame[required]).all(axis=1)
    clean = frame.loc[usable, required]
    rule = f"{minutes}min"
    spec = dict(open="first", high="max", low="min", close="last", volume="sum")
    if require_flow:
        spec.update(buy="sum", sell="sum")
    groups = clean.resample(rule, closed="right", label="right", origin="start_day")
    bars = groups.agg(spec)
    count = groups.size()
    complete = count.eq(minutes)
    bars = bars[complete].copy()
    bars["minute_count"] = minutes
    if require_flow and not np.array_equal(bars.volume.to_numpy(), (bars.buy + bars.sell).to_numpy()):
        raise ValueError("Aggregated quantity identity failed")
    audit = dict(bar_minutes=minutes, complete_bars=len(bars), incomplete_nonempty_bins=int(((count > 0) & ~complete).sum()),
                 empty_bins=int((count == 0).sum()), invalid_input_minutes=int((~usable).sum()),
                 construction="complete, right-closed/right-labelled, anchored to midnight; no fill or interpolation",
                 empty_bin_note="Includes scheduled closures/weekends; not an outage count")
    return bars, audit


def complete5min_ohlcv(frame):
    """Parent-facing DataFrame API: only complete five-minute bars survive.

    Extra columns count/valid identify the admitted constituent count. The full
    missingness census is available in ``bars.attrs['input_audit']``.
    """
    bars, audit = aggregate_complete(frame, minutes=5, require_flow=True)
    bars["count"] = bars["minute_count"]
    bars["valid"] = True
    bars.attrs["input_audit"] = audit
    return bars


def to_grid(frame):
    """Grid24 instance built from admitted native minute data, without its CSV loader.

    The shared Grid24 methods (daily_atr, bars, jof) remain available. Weekday
    calendar slots are preserved even when missing, rather than selecting today's
    trading membership from later intraday observations. Caller chooses admitted
    calendar/sessions and separately enforces complete execution paths.
    """
    from grid24 import Grid24, jof
    dates = pd.date_range(frame.index.min().normalize(), frame.index.max().normalize(), freq="D")
    grid = Grid24.__new__(Grid24)
    grid.ts = dates.to_numpy()
    grid.dates = dates.strftime("%Y%m%d").to_numpy(dtype=int)
    grid.D = len(dates)
    day = dates.get_indexer(frame.index.normalize())
    minute = frame.index.hour.to_numpy() * 60 + frame.index.minute.to_numpy()
    for name, key in [("open", "o"), ("high", "h"), ("low", "l"), ("close", "c"), ("volume", "v"), ("buy", "buy"), ("sell", "sell")]:
        arr = np.full((grid.D, 1440), np.nan)
        if name in frame:
            arr[day, minute] = frame[name].to_numpy(float)
        setattr(grid, key, arr)
    has = np.isfinite(grid.c)
    grid.last_j = np.where(has.any(axis=1), 1439 - np.argmax(has[:, ::-1], axis=1), -1)
    grid.trading = np.flatnonzero(dates.dayofweek < 5)
    grid.jof = jof
    return grid


def recent_input_paths(root=ROOT, years=range(2023, 2027)):
    """Discovery only: no later price values or outcomes read."""
    root = Path(root)
    years = set(map(int, years))
    prices = [root / "data" / f"NQ_1min_{suffix}{year}.csv" for year in sorted(years) for suffix in ("", "ON_")]
    flow = sorted(p for p in (root / "data").glob("OF_1min_*.csv") if int(p.name.split("_")[2]) in years)
    return dict(prices=[str(p) for p in prices if p.exists()], flow=[str(p) for p in flow],
                price_clock="CT minute close", flow_clock="ET minute close, convert to CT",
                warning="Legacy OF volume is BUY volume, not total. Reconstruct total=upvol+downvol; finite flow/source-close match required. Later full-session native package not present here.")


make_grid = to_grid


def self_check():
    idx = pd.date_range("2020-01-01 23:56", periods=10, freq="min")
    f = pd.DataFrame({"open": 100., "high": 101., "low": 99., "close": 100., "volume": 10., "buy": 6., "sell": 4.}, index=idx)
    b, _ = aggregate_complete(f)
    assert list(b.index) == [pd.Timestamp("2020-01-02 00:00"), pd.Timestamp("2020-01-02 00:05")]
    assert list(b.volume) == [50, 50] and list(b.buy - b.sell) == [10, 10]
    c, _ = aggregate_complete(f.drop(f.index[2]))
    assert list(c.index) == [pd.Timestamp("2020-01-02 00:05")]
    f.iloc[2, f.columns.get_loc("buy")] = np.nan
    c, _ = aggregate_complete(f)
    assert list(c.index) == [pd.Timestamp("2020-01-02 00:05")]
    return {"passed": True, "scope": "invented complete/missing/nonfinite/midnight aggregation; no signals or returns"}


if __name__ == "__main__":
    if "--design-intake" in sys.argv:
        minutes, audit = load_design_native(with_audit=True)
        _, counts = aggregate_complete(minutes)
        print(json.dumps({"minutes": audit, "bars5": counts}, indent=2))
    else:
        print(json.dumps(self_check(), indent=2))
