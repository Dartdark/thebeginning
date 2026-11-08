#!/usr/bin/env python3
"""Free research-data acquisition and offline audit; no signals, returns or trading.

Python standard library only. Outputs must be new directories. See the local task
for clock, primary-reconciliation and benchmark gates before any strategy test.
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import math
import sys
from pathlib import Path, PurePosixPath
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'agents/codex/inputs/new_data_20261108'
FUNDS = ('UGL', 'GLL', 'UCO', 'SCO', 'BOIL', 'KOLD')
INDICES = ('VVIX', 'SKEW', 'VIX9D')


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n')


def relative(root, name):
    parts = PurePosixPath(name)
    if parts.is_absolute() or '..' in parts.parts:
        raise ValueError('Unsafe relative path')
    return root.joinpath(*parts.parts)


def git_blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def csv_write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def audit(source, output):
    """Verify original bytes, pagination and identities; normalize without imputation."""
    manifest = json.loads((source / 'secondary_sources.json').read_text())
    checksums = []
    for entry in manifest['files']:
        raw = relative(source, entry['local_path']).read_bytes()
        if len(raw) != entry['bytes'] or git_blob(raw) != entry['git_blob_sha']:
            raise ValueError('Changed source blob: ' + entry['local_path'])
        checksums.append({'path': entry['local_path'], 'bytes': len(raw),
                          'sha256': hashlib.sha256(raw).hexdigest(),
                          'git_blob_sha': git_blob(raw)})
    stats = {'audit_utc': now(), 'source_files': len(checksums),
             'source_bytes': sum(x['bytes'] for x in checksums),
             'status': 'SECONDARY_ONLY_PRIMARY_AND_CLOCK_REVIEW_PENDING',
             'trials_run': 0, 'funds': [], 'indices': []}
    fund_dates = {}
    for ticker in FUNDS:
        folder = source / 'raw/daggerok/api/proshares/funds' / ticker
        meta = json.loads((folder / 'meta.json').read_text())
        paths = sorted((folder / 'history').glob('*.json'))
        pages = [json.loads(p.read_text()) for p in paths]
        if [p.name for p in paths] != [PurePosixPath(p).name for p in meta['history']['pages']]:
            raise ValueError('History pages disagree with metadata: ' + ticker)
        if [p['page'] for p in pages] != list(range(1, len(pages) + 1)):
            raise ValueError('Nonconsecutive pages: ' + ticker)
        total = pages[0]['totalRows']
        if any(p['ticker'] != ticker or p['totalRows'] != total for p in pages):
            raise ValueError('Page identity/count mismatch: ' + ticker)
        raw_rows = [r for p in pages for r in p['rows']]
        if len(raw_rows) != total or meta['history']['totalRows'] != total:
            raise ValueError('Incomplete history: ' + ticker)
        rows, dates, errors = [], [], []
        for row in raw_rows:
            date = dt.datetime.strptime(row['Date'], '%b %d %Y').date().isoformat()
            nav, shares, assets = [float(row[c]) for c in ('NAV', 'Shares Outstanding', 'Total Net Assets')]
            if not all(math.isfinite(x) for x in (nav, shares, assets)):
                raise ValueError('Nonfinite history: ' + ticker)
            error = abs(nav * shares / assets - 1) if assets > 0 else None
            flags = []
            if min(nav, shares, assets) <= 0:
                flags.append('NONPOSITIVE_VALUE')
            if error is None or error > .01:
                flags.append('NAV_SHARES_ASSETS_MISMATCH')
            rows.append({'date': date, 'nav_usd_source_basis': nav,
                         'shares_outstanding_source_basis': shares, 'net_assets_usd': assets,
                         'nav_times_shares_relative_error': error,
                         'row_quality': '|'.join(flags) or 'BASIC_IDENTITY_PASS_PRIMARY_PENDING',
                         'available_at': ''})
            dates.append(date)
            errors.append(error)
        if dates != sorted(dates) or len(set(dates)) != len(dates):
            raise ValueError('Dates duplicate or unordered: ' + ticker)
        if dates[-1] > dt.date.today().isoformat():
            raise ValueError('Future history row: ' + ticker)
        bad = [r for r in rows if r['row_quality'] != 'BASIC_IDENTITY_PASS_PRIMARY_PENDING']
        design = [r for r in rows if '2018-01-01' <= r['date'] <= '2022-12-31']
        holdings = [json.loads((folder / p.removeprefix('./')).read_text())
                    for p in meta['holdings']['pages']]
        position_rows = [r for p in holdings for r in p['rows']]
        if len(position_rows) != meta['holdings']['totalRows']:
            raise ValueError('Incomplete current holdings: ' + ticker)
        stat = {'ticker': ticker, 'rows': len(rows), 'first': dates[0], 'last': dates[-1],
                'design_2018_22_rows': len(design), 'duplicate_dates': 0,
                'nonpositive_rows': sum('NONPOSITIVE_VALUE' in r['row_quality'] for r in rows),
                'identity_errors_above_1pct': sum(e is None or e > .01 for e in errors),
                'max_identity_relative_error': max(e for e in errors if e is not None),
                'design_flagged_rows': sum(r in bad for r in design),
                'current_holdings_rows': len(position_rows),
                'current_holdings_asof': meta['holdings']['asOf'],
                'current_benchmark': meta['identifiers']['indexName'],
                'status': 'QUARANTINED_IDENTITY_OR_ZERO_VALUE' if bad else 'BASIC_QA_PASS_SECONDARY_ONLY'}
        stats['funds'].append(stat)
        fund_dates[ticker] = set(r['date'] for r in design)
        # Retain bad rows explicitly, never fill/reconstruct them using the identity.
        csv_write(output / 'normalized' / (ticker + '_nav_assets_shares.csv'), rows)
        if bad:
            csv_write(output / 'quarantine' / (ticker + '_flagged_rows.csv'), bad)
    for stat in stats['funds']:
        missing = sorted(fund_dates['UGL'] - fund_dates[stat['ticker']])
        extra = sorted(fund_dates[stat['ticker']] - fund_dates['UGL'])
        stat['design_dates_missing_vs_UGL_not_exchange_calendar'] = missing
        stat['design_dates_extra_vs_UGL_not_exchange_calendar'] = extra
    for ticker in INDICES:
        path = source / 'raw/gianni04/data' / (ticker + '.csv')
        raw_rows = list(csv.DictReader(path.read_text().splitlines()))
        rows = []
        for r in raw_rows:
            date = dt.date.fromisoformat(r['date']).isoformat()
            close = float(r['close'])
            if not math.isfinite(close) or close <= 0:
                raise ValueError('Invalid index close: ' + ticker)
            rows.append({'date': date, 'close_index_points': close, 'available_at': ''})
        dates = [r['date'] for r in rows]
        if dates != sorted(set(dates)) or dates[-1] > dt.date.today().isoformat():
            raise ValueError('Invalid index dates: ' + ticker)
        design_dates = set(d for d in dates if '2018-01-01' <= d <= '2022-12-31')
        stats['indices'].append({'index': ticker, 'rows': len(rows),
                                'first': dates[0], 'last': dates[-1],
                                'design_2018_22_rows': len(design_dates),
                                'duplicate_dates': 0,
                                'close_min': min(r['close_index_points'] for r in rows),
                                'close_max': max(r['close_index_points'] for r in rows),
                                'design_dates_missing_vs_UGL_not_exchange_calendar': sorted(fund_dates['UGL'] - design_dates),
                                'synthetic_ohlc_dropped': all(r['open'] == r['high'] == r['low'] == r['close'] for r in raw_rows),
                                'status': 'BASIC_QA_PASS_SECONDARY_ONLY'})
        csv_write(output / 'normalized' / (ticker + '_daily_close.csv'), rows)
    dump(output / 'source_checksums.json', checksums)
    dump(output / 'qa_summary.json', stats)
    return stats


def read_url(url, timeout):
    request = urllib.request.Request(url, headers={'User-Agent': 'Codex-Free-Research-Data/1.0',
                                                  'Accept': '*/*'})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read(30_000_001)
        if len(raw) > 30_000_000:
            raise ValueError('Response exceeds 30MB acquisition limit')
        return raw, dict(response.headers), response.geturl()


def payload_info(raw, kind):
    text = raw.decode('utf-8-sig')
    if not text.strip():
        raise ValueError('Empty response')
    if kind not in ('html_document', 'spec_document') and text.lstrip().lower().startswith(('<!doctype html', '<html')):
        raise ValueError('HTML response instead of data')
    if kind.startswith('fiscal'):
        j = json.loads(text)
        if not isinstance(j.get('data'), list) or not j['data']:
            raise ValueError('Empty/missing Fiscal Data records')
        return {'rows': len(j['data']), 'total_pages': int(j['meta']['total-pages']),
                'total_count': int(j['meta']['total-count']), 'fields': list(j['data'][0])}
    if kind == 'json_data':
        j = json.loads(text)
        def record_count(value):
            if isinstance(value, list):
                return sum(isinstance(v, dict) for v in value)
            if isinstance(value, dict):
                return sum(record_count(v) for v in value.values())
            return 0
        count = record_count(j)
        if not count or (isinstance(j, dict) and any(k in j for k in ('error', 'errors'))):
            raise ValueError('Empty record set or JSON API error')
        return {'keys': list(j) if isinstance(j, dict) else [],
                'nested_record_count_not_unique_events': count,
                'completeness': 'Not certified; inspect schema, limits and coverage before use'}
    if kind.endswith('csv'):
        records = list(csv.reader(io.StringIO(text)))
        if len(records) < 3:
            raise ValueError('Too few CSV rows')
        if kind == 'nav_csv' and not any('NAV' in row and 'Date' in row for row in records[:30]):
            raise ValueError('Missing NAV history header')
        if kind == 'index_csv' and not any('DATE' in [x.upper().strip() for x in row] for row in records[:10]):
            raise ValueError('Missing index date header')
        return {'physical_csv_rows': len(records), 'not_yet_normalized': True}
    return {'document_only_not_data': True, 'characters': len(text)}


def fetch_primary(manifest, output, timeout, only):
    jobs = json.loads(manifest.read_text())['files']
    if only:
        requested = set(only.split(','))
        jobs = [j for j in jobs if j['id'] in requested or j['group'] in requested]
        if not jobs:
            raise ValueError('No acquisition jobs match --only')
    receipts = []
    for job in jobs:
        page, total, collected = 1, 1, 0
        while page <= total:
            url = job['url']
            if job['kind'].startswith('fiscal'):
                url += '&' + urllib.parse.urlencode({'page[number]': page})
            record = {'id': job['id'], 'url': url, 'requested_at_utc': now(), 'page': page}
            try:
                raw, headers, final_url = read_url(url, timeout)
                record.update({'received_at_utc': now(), 'final_url': final_url,
                               'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                               'http_headers': {k: v for k, v in headers.items()
                                                if k.lower() in ('date', 'last-modified', 'etag', 'content-type')}})
                try:
                    info = payload_info(raw, job['kind'])
                except (ValueError, KeyError, TypeError) as error:
                    rejected = relative(output / 'rejected', job['file'])
                    rejected.parent.mkdir(parents=True, exist_ok=True)
                    rejected.write_bytes(raw)
                    record['rejected_payload'] = str(rejected.relative_to(output))
                    raise ValueError('Payload validation failed: ' + str(error)) from error
                filename = job['file']
                if job['kind'].startswith('fiscal'):
                    total = info['total_pages']
                    if total > 100 or total < 1:
                        raise ValueError('Unexpected Fiscal Data page count')
                    collected += info['rows']
                    filename = str(PurePosixPath(filename).with_suffix('')) + f'_page{page:03d}.json'
                    if page == total and collected != info['total_count']:
                        raise ValueError('Fiscal Data row count mismatch; snapshot may have moved')
                target = relative(output / 'raw', filename)
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('xb') as handle:
                    handle.write(raw)
                record.update({'status': 'DOWNLOADED_NOT_ADMITTED', 'path': str(target.relative_to(output)), 'validation': info})
            except Exception as error:
                record.update({'status': 'FAILED', 'error': str(error)})
                receipts.append(record)
                print(json.dumps({'id': job['id'], 'page': page, 'status': 'FAILED', 'error': str(error)}), flush=True)
                break
            receipts.append(record)
            print(json.dumps({'id': job['id'], 'page': page, 'status': record['status'], 'bytes': record['bytes']}), flush=True)
            page += 1
    dump(output / 'acquisition_receipt.json', {'created_at_utc': now(),
          'notice': 'Receipt time is not historical publication time. Primary reconciliation and clock gates remain.',
          'requests': receipts})
    return {'downloaded': sum(r['status'] == 'DOWNLOADED_NOT_ADMITTED' for r in receipts),
            'failed': sum(r['status'] == 'FAILED' for r in receipts)}


def fetch_secondary(source, output, timeout):
    manifest = json.loads((source / 'secondary_sources.json').read_text())
    for e in manifest['files']:
        raw, _, _ = read_url(e['url'], timeout)
        if len(raw) != e['bytes'] or git_blob(raw) != e['git_blob_sha']:
            raise ValueError('Secondary blob mismatch: ' + e['path'])
        p = relative(output, e['local_path'])
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('xb') as handle:
            handle.write(raw)
    dump(output / 'secondary_sources.json', manifest)
    return {'files': len(manifest['files']), 'status': 'SECONDARY_ONLY'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('audit', 'fetch-primary', 'fetch-secondary'))
    parser.add_argument('--source', type=Path, default=PACKAGE)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=25)
    parser.add_argument('--only', help='Comma-separated primary job IDs or groups')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    if args.mode == 'audit':
        result = audit(args.source, args.output)
        print(json.dumps({k: v for k, v in result.items() if k not in ('funds', 'indices')}))
    elif args.mode == 'fetch-primary':
        result = fetch_primary(args.source / 'primary_sources.json', args.output, args.timeout, args.only)
        print(json.dumps(result))
        if result['failed']:
            sys.exit(1)
    else:
        print(json.dumps(fetch_secondary(args.source, args.output, args.timeout)))


if __name__ == '__main__':
    main()
