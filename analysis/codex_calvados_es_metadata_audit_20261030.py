"""Reproduce the Calvados ES follow-up's input/clock metadata, never strategy returns.

Raw inputs stay outside Git. Optional --acquire-samples uses only the three frozen
public GitHub files and preserves inherited proxy/TLS settings. No full chain fetch.
Example:
 python analysis/codex_calvados_es_metadata_audit_20261030.py --raw-dir /workspace/calvados_data_prior \
   --owned-data-dir /workspace/thebeginning/data --output-dir /tmp/es_metadata
"""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

import pandas as pd

COMMIT = '180fb127d0249827d415a3f5d298006a08ff7a31'
SAMPLES = {
    'ESH2018.csv': ('a1ddd89703aa3dab2083bf5226777f0b36006d63', 7474897),
    'ESM2018.csv': ('71a17dc9960628306210d2405f84dcc58eb7fa22', 8159197),
    'ESZ2022.csv': ('2b968da7491d0170e985eeee35b6a036da6cc07a', 7831549),
}


def owned_metadata(owned_dir):
    out = []
    for year in range(2017, 2023):
        p = owned_dir / f'ES_1min_{year}.csv'
        b = p.read_bytes()
        lines = b.splitlines()
        header = lines[0].decode().split(',')
        out.append(dict(file=str(p), bytes=len(b), sha256=hashlib.sha256(b).hexdigest(),
            header=header, rows=len(lines)-1,
            first_datetime=lines[1].decode().split(',')[:2],
            last_datetime=lines[-1].decode().split(',')[:2],
            contract_id_column=any('contract' in x.lower() or 'symbol' in x.lower() for x in header),
            settlement_column=any('settle' in x.lower() for x in header)))
    return out


def clock_hypotheses(df, fn, owned_dir):
    year = '2018' if fn == 'ESH2018.csv' else '2022'
    owned = pd.read_csv(owned_dir / f'ES_1min_{year}.csv')
    ox = pd.to_datetime(owned.date.astype(str)+owned.time.astype(str).str.zfill(4), format='%Y%m%d%H%M')
    close = owned.set_index(ox).close
    lo, hi = ('2018-01-02','2018-01-10') if year == '2018' else ('2022-11-01','2022-11-10')
    sample = df[(df.ts >= lo) & (df.ts < hi)].copy()
    out = []
    for assumption in ['UTC', 'America/Chicago']:
        tt = pd.DatetimeIndex(sample.ts).tz_localize(assumption, ambiguous='NaT', nonexistent='NaT').tz_convert('America/Chicago').tz_localize(None)
        for shift in [-1, 0, 1]:
            labels = tt + pd.Timedelta(minutes=shift)
            found = close.reindex(labels).to_numpy()
            valid = pd.notna(found)
            out.append(dict(assumption=assumption, label_shift_minutes=shift,
                paired_rows=int(valid.sum()),
                exact_close_matches=int((found[valid] == sample['<CLOSE>'].to_numpy()[valid]).sum())))
    return out


def run(args):
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    outputs, receipts = [], []
    for fn, (blob, expected_bytes) in SAMPLES.items():
        p = args.raw_dir / ('es_sample_'+fn)
        url = f'https://raw.githubusercontent.com/yakki-minati/US.Index.Futures.Data/{COMMIT}/ES/{fn}'
        status = None
        if not p.exists():
            if not args.acquire_samples:
                raise FileNotFoundError(f'{p}: provide pinned raw sample or use --acquire-samples')
            with urllib.request.urlopen(url, timeout=30) as response:
                status = response.status
                b = response.read(expected_bytes+1)
            if len(b) != expected_bytes:
                raise ValueError(f'Wrong length for {fn}')
            p.write_bytes(b)
        b = p.read_bytes()
        actual_blob = hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
        if actual_blob != blob or len(b) != expected_bytes:
            raise ValueError(f'Raw input hash/length mismatch: {fn}')
        df = pd.read_csv(p, sep='\t')
        ts = pd.to_datetime(df['<DATE>']+' '+df['<TIME>'], format='%Y.%m.%d %H:%M:%S')
        df['ts'] = ts
        dt = ts.diff().dt.total_seconds()
        daily = df.groupby(df.ts.dt.strftime('%Y-%m-%d')).agg(
            bars=('ts','size'), first=('ts','min'), last=('ts','max'),
            real_volume=('<VOL>','sum'), tick_volume=('<TICKVOL>','sum'))
        daily.to_csv(args.output_dir / ('es_sample_'+fn[:-4]+'_daily_metadata.csv'))
        cols = ['<OPEN>','<HIGH>','<LOW>','<CLOSE>']
        invalid = ((df[cols] <= 0).any(axis=1) | (df['<HIGH>'] < df['<LOW>']) |
            (df['<HIGH>'] < df[['<OPEN>','<CLOSE>']].max(axis=1)) |
            (df['<LOW>'] > df[['<OPEN>','<CLOSE>']].min(axis=1)))
        meta = dict(file=fn, rows=len(df), first=str(ts.min()), last=str(ts.max()),
            timestamp_timezone='unstated; naive labels only', session_dates=len(daily),
            weekday_dates=int((pd.to_datetime(daily.index).dayofweek < 5).sum()),
            duplicate_timestamps=int(ts.duplicated().sum()), not_increasing_steps=int((dt <= 0).sum()),
            one_minute_steps=int((dt == 60).sum()),
            steps_2min_to_1hour=int(((dt > 60) & (dt <= 3600)).sum()),
            steps_gt1hour=int((dt > 3600).sum()), invalid_ohlc_rows=int(invalid.sum()),
            zero_VOL_rows=int((df['<VOL>'] == 0).sum()), negative_VOL_rows=int((df['<VOL>'] < 0).sum()),
            zero_TICKVOL_rows=int((df['<TICKVOL>'] == 0).sum()), negative_TICKVOL_rows=int((df['<TICKVOL>'] < 0).sum()),
            zero_SPREAD_rows=int((df['<SPREAD>'] == 0).sum()), positive_SPREAD_rows=int((df['<SPREAD>'] > 0).sum()),
            SPREAD_units='unstated', sample_weekdays=daily[pd.to_datetime(daily.index).dayofweek < 5].head(2).reset_index().to_dict('records'))
        if fn in ['ESH2018.csv','ESZ2022.csv']:
            meta['clock_hypothesis_vs_owned_front_ES'] = clock_hypotheses(df, fn, args.owned_data_dir)
        outputs.append(meta)
        receipts.append(dict(url=url, http_status_if_fetched_now=status, bytes=len(b),
            git_blob_sha=actual_blob, sha256=hashlib.sha256(b).hexdigest(), header=list(df.columns[:-1]),
            records=len(df), first_date_label=str(ts.min()), last_date_label=str(ts.max())))
    (args.output_dir/'es_three_sample_audit.json').write_text(json.dumps(outputs,indent=2,default=str))
    (args.output_dir/'owned_es_metadata.json').write_text(json.dumps(owned_metadata(args.owned_data_dir),indent=2))
    (args.output_dir/'es_reproduced_sample_receipts.json').write_text(json.dumps(receipts,indent=2))
    print(json.dumps(dict(scope='Metadata only; no candidate signals/returns',samples=len(outputs),
        blob_hashes_verified=len(receipts),output_dir=str(args.output_dir)),indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir',type=Path,required=True)
    parser.add_argument('--owned-data-dir',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--acquire-samples',action='store_true')
    run(parser.parse_args())
