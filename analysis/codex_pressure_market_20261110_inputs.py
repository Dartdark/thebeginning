"""Input-only NQ/ES alignment for a preregistered pressure-model investigation.

No price changes, model fits, signals, trades or trading outcomes are computed.
Owned ES year files already contain the full session; NQ requires day + ON.
The clock is the repository's assumed Chicago minute-close convention, not a
new authentication of vendor/export settings or native contract/roll identity.
"""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
import pandas as pd

YEARS = (2018, 2019, 2020, 2021, 2022)
FIELDS = ["open", "high", "low", "close", "volume"]
SCHEMA = ["date", "time", *FIELDS]
CLOCK = "America/Chicago"
ES_EXPECTED_SHA256 = {
    "data/ES_1min_2018.csv": "ad4027b8230de0a91f83d1b6f3b798933f92cedebc39e56fe9223447c4b9d751",
    "data/ES_1min_2019.csv": "b9c09d6c9a702e560119bd33770cc71e05423fc0a7a227fcc046e73bf22f22c5",
    "data/ES_1min_2020.csv": "c22514904bd19b8ee9e3611bcd8af4017290730550b4799b9d92da73f8e7d550",
    "data/ES_1min_2021.csv": "67cd2dee366b86f555d09d45fb4cb9f6163347531b4f3f230f73704a1fff8096",
    "data/ES_1min_2022.csv": "00db614dd10674f7fe2f14940ae43f523b57ac48db1b0619b0eb084c5f50f601",
}
ES_POINT_VALUE, MES_POINT_VALUE, ES_TICK_SIZE = 50.0, 5.0, 0.25


def load_minute_panel(root, market, years=YEARS, expected_sha256=None):
    """Read exact owned files, reject duplicates/schema faults, return minutes + metadata.

    expected_sha256 maps repository-relative paths to frozen SHA256 strings.
    Omitting it fingerprints inputs but does not establish admission or source rights.
    """
    root = Path(root)
    if market not in ("NQ", "ES"):
        raise ValueError("This intake only admits the explicitly specified NQ/ES inputs")
    if not years or any(int(y) not in range(2017, 2023) for y in years):
        raise ValueError("Only design years 2018-22 and explicitly requested 2017 warmup")
    frames, receipts = [], []
    for year in years:
        prefixes = ("NQ_1min_", "NQ_1min_ON_") if market == "NQ" else ("ES_1min_",)
        for prefix in prefixes:
            relative = f"data/{prefix}{int(year)}.csv"
            path = root / relative
            raw = path.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            if expected_sha256 is not None and expected_sha256.get(relative) != digest:
                raise ValueError(f"Unfrozen or changed input: {relative}")
            frame = pd.read_csv(path)
            if frame.columns.tolist() != SCHEMA:
                raise ValueError(f"Unexpected schema: {relative}")
            values = frame[SCHEMA].to_numpy(float)
            if not np.isfinite(values).all():
                raise ValueError(f"Nonfinite input: {relative}")
            if not np.equal(values[:, :2], np.floor(values[:, :2])).all():
                raise ValueError(f"Noninteger date/time: {relative}")
            hm = frame.time.to_numpy()
            if ((hm < 0) | (hm > 2359) | (hm % 100 >= 60)).any():
                raise ValueError(f"Invalid HHMM: {relative}")
            bad = (frame.high < frame.low) | (frame.high < frame[["open", "close"]].max(axis=1))
            bad |= frame.low > frame[["open", "close"]].min(axis=1)
            bad |= (frame[["open", "high", "low", "close"]] <= 0).any(axis=1) | (frame.volume < 0)
            if bad.any():
                raise ValueError(f"Invalid OHLCV rows: {relative}; count={int(bad.sum())}")
            if frame.duplicated(["date", "time"]).any():
                raise ValueError(f"Duplicate date/time rows: {relative}")
            labels = pd.to_datetime(frame.date.astype(str) + frame.time.astype(str).str.zfill(4), format="%Y%m%d%H%M")
            if not labels.is_monotonic_increasing:
                raise ValueError(f"Nonchronological file: {relative}")
            index = pd.DatetimeIndex(labels).tz_localize(CLOCK, ambiguous="raise", nonexistent="raise")
            frames.append(frame[FIELDS].set_axis(index))
            receipts.append(dict(path=relative, sha256=digest, bytes=len(raw), rows=len(frame),
                                 first=str(index[0]), last=str(index[-1]), duplicate_keys=0))
    joined = pd.concat(frames).sort_index()
    if joined.index.duplicated().any():
        raise ValueError(f"Overlapping {market} files; no silent duplicate precedence")
    joined.index.name = "close_time_ct"
    return joined, receipts


def load_es_minutes(root, years=YEARS, expected_sha256=None):
    """Parent model API: naive CT minute-CLOSE OHLCV frame and an input audit.

    Uses frozen ES_EXPECTED_SHA256 by default. No legacy NQ data are read and no
    buy/sell fields are invented. Compatible with the native package's grid and
    strict aggregation adapters. ES is a common-market observation, not a hedge
    execution claim. A separately preregistered clock/roll/session policy remains
    necessary for any economic use.
    """
    expected = ES_EXPECTED_SHA256 if expected_sha256 is None else expected_sha256
    minutes, receipts = load_minute_panel(root, "ES", years, expected)
    minutes.index = minutes.index.tz_localize(None)
    minutes.index.name = "close_time_ct"
    if minutes.index.duplicated().any():
        raise ValueError("Duplicate naive CT labels after timezone removal")
    audit = dict(scope="Frozen ES input-only OHLCV for common-market feature",
                 source_files=receipts, rows=len(minutes), duplicate_keys=0,
                 clock="Naive Chicago minute-CLOSE labels by repository convention; original export clock unverified",
                 separate_overnight_file_needed=False, full_session_export=True,
                 native_contract_or_roll_ids_present=False, original_vendor_rights_verified=False,
                 es_point_value=ES_POINT_VALUE, mes_point_value=MES_POINT_VALUE, tick_size=ES_TICK_SIZE,
                 execution_costs="No ES execution in feature-only model; legacy $5/ES RT ($0.50/MES scaled) is not native fee verification",
                 synthetic_aggressor_fields_added=False, price_returns_or_signals_computed=False)
    return minutes, audit


def complete_five_minute(minutes):
    """Bins ending :00,:05,...; require all five exact, finite minute observations.

    A bin ending 08:35 contains minute-close labels 08:31..08:35. A bin ending
    00:00 contains the preceding date's 23:56..23:59 plus 00:00. Empty bins are
    absent; partial bins remain explicitly incomplete with OHLCV masked.
    """
    if minutes.index.tz is None or str(minutes.index.tz) != CLOCK:
        raise ValueError("Expected named Chicago close-label clock")
    if minutes.index.duplicated().any() or not minutes.index.is_monotonic_increasing:
        raise ValueError("Minute observations must be unique and ordered")
    sampler = minutes.resample("5min", label="right", closed="right", origin="start_day")
    bars = sampler.agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars["count"] = sampler.close.count()
    bars = bars[bars["count"] > 0].copy()
    bars["complete"] = bars["count"].eq(5) & np.isfinite(bars[FIELDS]).all(axis=1)
    bars.loc[~bars.complete, FIELDS] = np.nan
    return bars


def load_aligned_five_minute(root, years=YEARS, expected_sha256=None):
    """Legacy NQ comparison receipt only; do not use for the native-NQ model.

    Return outer-aligned legacy NQ/ES bars and no-return structural metadata.
    Native-NQ economics must call load_es_minutes and join their own native NQ.
    """
    nq, nq_receipts = load_minute_panel(root, "NQ", years, expected_sha256)
    es, es_receipts = load_minute_panel(root, "ES", years, expected_sha256)
    nq5, es5 = complete_five_minute(nq), complete_five_minute(es)
    panel = pd.concat([nq5.add_prefix("nq_"), es5.add_prefix("es_")], axis=1).sort_index()
    for market in ("nq", "es"):
        panel[f"{market}_complete"] = panel[f"{market}_complete"].astype("boolean").fillna(False).astype(bool)
    panel["joint_complete"] = panel.nq_complete & panel.es_complete
    common_minutes = nq.index.intersection(es.index)
    by_year = {}
    for y in years:
        mask = panel.index.year == int(y)
        by_year[str(y)] = dict(nq_occupied_bins=int((mask & panel.nq_count.notna()).sum()),
                              es_occupied_bins=int((mask & panel.es_count.notna()).sum()),
                              nq_complete_bins=int((mask & panel.nq_complete).sum()),
                              es_complete_bins=int((mask & panel.es_complete).sum()),
                              joint_complete_bins=int((mask & panel.joint_complete).sum()))
    receipt = dict(scope="Input structure, fingerprints and label/coverage alignment only",
                   clock="Assumed repository America/Chicago minute-close labels; vendor/export clock not authenticated",
                   raw_contract_and_roll_ids_present=False, original_vendor_rights_verified=False,
                   native_execution_or_fee_claim=False, source_files=nq_receipts + es_receipts,
                   minute_counts=dict(nq=len(nq), es=len(es), common=len(common_minutes),
                                      nq_without_es=len(nq.index.difference(es.index)), es_without_nq=len(es.index.difference(nq.index))),
                   five_minute_by_year=by_year, signals_or_price_returns_computed=False)
    return panel, receipt


def fixtures():
    ix = pd.date_range("2020-01-02 08:31", periods=5, freq="min", tz=CLOCK)
    frame = pd.DataFrame(dict(open=100., high=101., low=99., close=100., volume=1.), index=ix)
    full = complete_five_minute(frame)
    assert len(full) == 1 and full.index[0].strftime("%H:%M") == "08:35"
    assert full.complete.iloc[0] and full.volume.iloc[0] == 5
    partial = complete_five_minute(frame.drop(ix[2]))
    assert not partial.complete.iloc[0] and partial[FIELDS].isna().all(axis=None)
    try:
        complete_five_minute(pd.concat([frame, frame.iloc[[0]]]).sort_index())
    except ValueError:
        pass
    else:
        raise AssertionError("Duplicate row admitted")
    midnight = frame.set_axis(pd.date_range("2020-01-02 23:56", periods=5, freq="min", tz=CLOCK))
    b = complete_five_minute(midnight)
    assert b.index[0].strftime("%Y-%m-%d %H:%M") == "2020-01-03 00:00" and b.complete.iloc[0]
    return dict(checks=4, passed=True, signals_or_price_returns_computed=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--fixtures-only", action="store_true")
    args = parser.parse_args()
    checks = fixtures()
    if args.fixtures_only:
        print(json.dumps(checks))
    else:
        _, result = load_aligned_five_minute(args.root)
        result["fixtures"] = checks
        if args.receipt:
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            args.receipt.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({k: v for k, v in result.items() if k != "source_files"}, indent=2))
