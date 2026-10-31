"""No-return audit of user NG exports; does not compute signals or P&L."""
from pathlib import Path
from collections import Counter
import gzip
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'agents/codex/inputs/ng_upload_20261031'
OUT = ROOT / 'analysis/outputs/codex_ng_upload_audit_20261031'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    raw_dir = INPUT / 'raw'
    raw_dir.mkdir(exist_ok=True)
    paths = json.loads((INPUT / 'upload_paths.json').read_text())['files']
    rows, windows, manifests = [], [], []
    for spec in sorted(paths, key=lambda x: x['year']):
        original = Path(spec['path'])
        archive = raw_dir / f"NG_1min_{spec['year']}.csv.gz"
        if original.exists():
            payload = original.read_bytes()
            archive.write_bytes(gzip.compress(payload, mtime=0))
        else:
            payload = gzip.decompress(archive.read_bytes())
        import io
        raw = pd.read_csv(io.BytesIO(payload), dtype=str)
        assert list(raw.columns) == ['date', 'time', 'open', 'high', 'low', 'close', 'volume']
        df = raw.apply(pd.to_numeric, errors='coerce')
        times = df.time // 100 * 60 + df.time % 100
        stamps = pd.to_datetime(raw.date + raw.time.str.zfill(4), format='%Y%m%d%H%M', errors='coerce')
        prices = df[['open', 'high', 'low', 'close']].to_numpy()
        text_prices = raw[['open', 'high', 'low', 'close']].to_numpy().ravel()
        precision = Counter(len(v.split('.')[1]) if '.' in v else 0 for v in text_prices)
        counts = df.groupby('date').size()
        bad_ohlc = (df.high < df[['open', 'close', 'low']].max(axis=1)) | (df.low > df[['open', 'close', 'high']].min(axis=1))
        duplicate = df.duplicated(['date', 'time'], keep=False)
        rows.append(dict(year=int(spec['year']), rows=len(df), dates=int(df.date.nunique()),
                         first_timestamp=str(stamps.min()), last_timestamp=str(stamps.max()),
                         minimum_clock=int(df.time.min()), maximum_clock=int(df.time.max()),
                         bars_per_date_min=int(counts.min()), bars_per_date_median=float(counts.median()),
                         bars_per_date_max=int(counts.max()), invalid_timestamp_rows=int(stamps.isna().sum()),
                         invalid_numeric_cells=int(df.isna().sum().sum()),
                         duplicate_timestamp_rows=int(duplicate.sum()), bad_ohlc_rows=int(bad_ohlc.sum()),
                         zero_volume_rows=int((df.volume == 0).sum()),
                         serialized_price_decimal_places=dict(precision),
                         prices_off_001_grid=int(np.count_nonzero(~np.isclose(prices * 1000, np.round(prices * 1000), atol=1e-7, rtol=0))),
                         prices_off_01_grid=int(np.count_nonzero(~np.isclose(prices * 100, np.round(prices * 100), atol=1e-7, rtol=0)))))
        # Provisional regular Thursdays only. Not an authoritative release calendar.
        for date, frame in df.groupby('date'):
            dt = pd.Timestamp(str(int(date)))
            if dt.dayofweek != 3:
                continue
            js = set((frame.time // 100 * 60 + frame.time % 100).astype(int))
            expected = set(range(480, 601))
            windows.append(dict(year=int(spec['year']), date=dt.date().isoformat(),
                                has_0800=480 in js, has_1000=600 in js,
                                missing_0800_through_1000=len(expected-js)))
        manifests.append(dict(year=int(spec['year']), filename=original.name, raw_bytes=len(payload),
                              raw_sha256=hashlib.sha256(payload).hexdigest(), archive=str(archive.relative_to(ROOT)),
                              archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                              permission='owned_upload', provenance='User attached NG CSV on2026-10-31; export conventions pending'))
    pd.DataFrame(rows).to_csv(OUT / 'yearly_quality.csv', index=False)
    frame = pd.DataFrame(windows)
    frame.to_csv(OUT / 'provisional_thursday_coverage.csv', index=False)
    design = frame[frame.year.between(2018, 2022)]
    summary = dict(return_tests_executed=False, authoritative_calendar=False, files=len(rows),
                   rows=sum(x['rows'] for x in rows), price_cells=sum(x['rows'] * 4 for x in rows),
                   price_cells_off_01_grid=sum(x['prices_off_01_grid'] for x in rows),
                   duplicate_timestamp_rows=sum(x['duplicate_timestamp_rows'] for x in rows),
                   bad_ohlc_rows=sum(x['bad_ohlc_rows'] for x in rows),
                   invalid_timestamp_rows=sum(x['invalid_timestamp_rows'] for x in rows),
                   invalid_numeric_cells=sum(x['invalid_numeric_cells'] for x in rows),
                   design_regular_thursdays_present=len(design),
                   design_thursdays_with_both_provisional_endpoints=int((design.has_0800 & design.has_1000).sum()),
                   design_thursdays_with_complete_provisional_window=int((design.missing_0800_through_1000 == 0).sum()),
                   first_timestamp=min(x['first_timestamp'] for x in rows), last_timestamp=max(x['last_timestamp'] for x in rows),
                   native_tick=0.001, exported_observed_price_grid=0.01,
                   nearest_rounding_assumption_max_endpoint_error=0.005,
                   nearest_rounding_assumption_max_two_fill_pnl_error_usd_per_NG=100.0,
                   nearest_rounding_assumption_max_two_fill_pnl_error_usd_per_MNG=10.0,
                   quality_status='NOT_ADMITTED: precision, clock/session, contract/roll conventions and full source/calendar unresolved',
                   limits=['No price returns or strategy statistics computed',
                           'Two-fill error bounds assume nearest-cent rounding; exporter behavior is unverified',
                           'Provisional Thursday presence is not release coverage; holiday exceptions excluded from this assertion',
                           'No inference that absent overnight minutes defeat a complete intraday event window'],
                   files_detail=rows)
    assert summary['nearest_rounding_assumption_max_two_fill_pnl_error_usd_per_NG'] == 2 * 0.005 * 10000
    (INPUT / 'manifest.json').write_text(json.dumps(manifests, indent=2) + '\n')
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k:v for k,v in summary.items() if k != 'files_detail'}, indent=2))


if __name__ == '__main__':
    main()
