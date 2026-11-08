#!/usr/bin/env python3
"""Offline cloud review of transferred primary data. No network or strategy returns."""
import argparse
from collections import Counter, defaultdict
import csv
import datetime as dt
from decimal import Decimal as D
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import urllib.parse
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / 'agents/codex/inputs/new_data_primary_local_20261108'
SECONDARY = REPO / 'agents/codex/inputs/new_data_20261108/audit/normalized'


def safe_path(root, value):
    # Source manifests/HTTP receipts were generated on Windows. Preserve originals.
    path = PurePosixPath(value.replace('\\', '/'))
    if path.is_absolute() or '..' in path.parts or ':' in str(path):
        raise ValueError('Unsafe transport path: ' + value)
    return root.joinpath(*path.parts)


def require(value, message):
    if not value:
        raise ValueError(message)


def json_read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def raw(root, relative):
    return gzip.decompress(safe_path(root, 'transport/' + relative + '.gz').read_bytes())


def raw_json(root, relative):
    return json.loads(raw(root, relative))


def csv_rows(data):
    return list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'))))


def csv_file(path):
    return csv_rows(path.read_bytes())


def iso_date(value):
    return dt.datetime.strptime(value, '%m/%d/%Y').date().isoformat()


def canon(rows):
    return Counter(json.dumps(row, sort_keys=True, ensure_ascii=False) for row in rows)


def audit(root):
    result = {'status': 'PASS_TRANSPORT_AND_RECONCILIATION_ONLY',
              'strategy_trials': 0, 'network_requests': 0,
              'historical_information_clock_admitted': False}
    manifests = json_read(root / 'transport_manifest.json') + json_read(root / 'supplement_manifest.json')
    paths, byte_totals = set(), Counter()
    for i, entry in enumerate(manifests, 1):
        path = safe_path(root, entry['path'])
        relative = path.relative_to(root).as_posix()
        require(relative not in paths, 'Duplicate manifest path: ' + relative)
        paths.add(relative)
        compressed = path.read_bytes()
        require(len(compressed) == entry['compressed_bytes'], 'Compressed size: ' + relative)
        require(hashlib.sha256(compressed).hexdigest() == entry['compressed_sha256'], 'Compressed hash: ' + relative)
        size, digest = 0, hashlib.sha256()
        with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b''):
                size += len(chunk)
                digest.update(chunk)
        require(size == entry['original_bytes'], 'Original size: ' + relative)
        require(digest.hexdigest() == entry['original_sha256'], 'Original hash: ' + relative)
        byte_totals.update(compressed=len(compressed), original=size)
        if i % 200 == 0:
            print(json.dumps({'transport_verified': i, 'total': len(manifests)}), flush=True)
    actual = {p.relative_to(root).as_posix() for p in (root / 'transport').rglob('*.gz')}
    require(paths == actual, 'Unlisted or missing transport file')
    result['transport'] = dict(files=len(paths), **byte_totals)

    primary_receipts = []
    for group in ('primary', 'macro'):
        entries = raw_json(root, group + '/acquisition_receipt.json')['requests']
        require(all(e['status'] == 'DOWNLOADED_NOT_ADMITTED' for e in entries), 'Failed original request')
        for entry in entries:
            data = raw(root, group + '/' + entry['path'].replace('\\', '/'))
            require(len(data) == entry['bytes'] and hashlib.sha256(data).hexdigest() == entry['sha256'],
                    'HTTP source receipt mismatch: ' + entry['id'])
        primary_receipts += entries
    result['primary_http_receipts_verified'] = len(primary_receipts)

    result['funds'] = {}
    for ticker in ('UGL', 'GLL', 'UCO', 'SCO', 'BOIL', 'KOLD'):
        original = csv_rows(raw(root, f'primary/raw/proshares/{ticker}-historical_nav.csv'))
        normalized = csv_file(root / 'normalized' / (ticker + '.csv'))
        old = {r['date']: r for r in csv_file(SECONDARY / (ticker + '_nav_assets_shares.csv'))}
        expected, bad, zeros, differences = {}, 0, 0, Counter()
        max_difference = defaultdict(lambda: D(0))
        bad_design = 0
        for row in original:
            day = iso_date(row['Date'])
            require(day not in expected, 'Duplicate fund date: ' + ticker)
            nav, shares, assets = D(row['NAV']), D(row['Shares Outstanding (000)']) * 1000, D(row['Assets Under Management'])
            require(nav.is_finite() and shares.is_finite() and assets.is_finite(), 'Nonfinite fund data')
            error = abs(nav * shares / assets - 1) if assets else D(1)
            expected[day] = {'nav_usd_source_basis': nav, 'shares_outstanding_source_basis': shares,
                             'net_assets_usd': assets, 'relative_identity_error': error,
                             'prior_nav_usd_source_basis': D(row['Prior NAV']),
                             'nav_change_percent': D(row['NAV Change (%)']),
                             'nav_change_usd': D(row['NAV Change ($)']),
                             'shares_outstanding_000_source': D(row['Shares Outstanding (000)'])}
            bad += error > D('.01')
            bad_design += error > D('.01') and '2018-01-01' <= day <= '2022-12-31'
            zeros += shares <= 0
            require(day in old, 'New unmatched fund date; review separately: ' + ticker)
            for key in ('nav_usd_source_basis', 'shares_outstanding_source_basis', 'net_assets_usd'):
                delta = abs(expected[day][key] - D(old[day][key]))
                differences[key] += delta != 0
                max_difference[key] = max(max_difference[key], delta)
        require(len(normalized) == len(expected), 'Fund normalization dropped rows: ' + ticker)
        require([r['date'] for r in normalized] == sorted(expected), 'Fund date order/duplicate mismatch')
        for row in normalized:
            require(row['available_at'] == '', 'Invented historical fund clock')
            require(all(D(row[k]) == v for k, v in expected[row['date']].items()), 'Fund numeric conversion mismatch: ' + ticker)
        result['funds'][ticker] = {'rows': len(expected), 'first': min(expected), 'last': max(expected),
                                   'identity_errors_above_1pct': bad, 'zero_or_negative_shares': zeros,
                                   'design_identity_failures': bad_design,
                                   'secondary_differing_fields': dict(differences),
                                   'secondary_max_abs_difference': {k: str(v) for k, v in max_difference.items()}}

    result['indices'] = {}
    for ticker in ('VVIX', 'SKEW', 'VIX9D', 'GVZ', 'OVX'):
        original = csv_rows(raw(root, f'primary/raw/cboe/{ticker}_History.csv'))
        expected = {}
        for row in original:
            day, value = iso_date(row['DATE']), D(row.get(ticker) or row['CLOSE'])
            require(day not in expected and value.is_finite() and value > 0, 'Bad index row: ' + ticker)
            expected[day] = value
        normalized = csv_file(root / 'normalized' / (ticker + '.csv'))
        require(len(normalized) == len(expected), 'Index row loss')
        require({r['date']: D(r['close_index_points']) for r in normalized} == expected, 'Changed primary index close')
        require(all(r['available_at'] == '' for r in normalized), 'Invented index release clock')
        old_path = SECONDARY / (ticker + '_daily_close.csv')
        old = csv_file(old_path) if old_path.exists() else []
        require(all(r['date'] in expected and D(r['close_index_points']) == expected[r['date']] for r in old),
                'Cached index close mismatch')
        result['indices'][ticker] = {'rows': len(expected), 'first': min(expected), 'last': max(expected),
                                     'cached_overlaps_matching': len(old)}

    operations, rates, annual = [], [], {}
    for year in range(2017, 2027):
        op = raw_json(root, f'macro/raw/nyfed/treasury_results_{year}.json')['treasury']['auctions']
        rr = raw_json(root, f'macro/raw/nyfed/reference_rates_{year}.json')['refRates']
        require(all(str(year) <= r['operationDate'] < str(year + 1) for r in op), 'Wrong operation year')
        require(all(str(year) <= r['effectiveDate'] < str(year + 1) for r in rr), 'Wrong rate year')
        operations.extend(op)
        rates.extend(rr)
        annual[('operations', year)] = op
        annual[('rates', year)] = rr
    for name, expected in [('nyfed_operations.json', operations), ('nyfed_rates.json', rates)]:
        normalized = json_read(root / 'normalized' / name)
        require(all(r.get('available_at') == '' for r in normalized), 'Invented NYFed receipt')
        require(canon([{k: v for k, v in r.items() if k != 'available_at'} for r in normalized]) == canon(expected),
                'NYFed normalized data differ from raw')
    keys = [(r['operationId'], r['operationDate']) for r in operations]
    require(len(keys) == len(set(keys)), 'Duplicate NYFed event')
    rate_keys = [(r['type'], r['effectiveDate']) for r in rates]
    require(len(rate_keys) == len(set(rate_keys)), 'Duplicate NYFed rate')
    require(max(r['operationDate'] for r in operations) <= '2026-11-08', 'Future operation included')
    require(max(r['effectiveDate'] for r in rates) <= '2026-11-08', 'Future rate included')
    supplement = raw_json(root, 'supplement/receipt.json')
    partitions = defaultdict(list)
    documents, valid_xml, valid_pdf = {}, 0, 0
    for entry in supplement:
        require(entry['status'] == 'SAVED', 'Failed supplemental request')
        data = raw(root, 'supplement/' + entry['path'])
        require(len(data) == entry['bytes'] and hashlib.sha256(data).hexdigest() == entry['sha256'], 'Supplement source hash')
        if entry['kind'] != 'doc':
            j = json.loads(data)
            rows = j['treasury']['auctions'] if entry['kind'] == 'operations' else j['refRates']
            partitions[(entry['kind'], entry['year'])].extend(rows)
        else:
            documents[entry['url']] = data
            extension = PurePosixPath(urllib.parse.urlparse(entry['url']).path).suffix.lower()
            if extension == '.xml':
                ET.fromstring(data)
                valid_xml += 1
            elif extension == '.pdf':
                require(data.startswith(b'%PDF'), 'Non-PDF body saved as PDF')
                valid_pdf += 1
    require(set(partitions) == set(annual), 'Missing annual/half-year pair')
    require(all(canon(partitions[k]) == canon(v) for k, v in annual.items()), 'Partition record mismatch')
    result['nyfed'] = {'operations': len(operations), 'security_detail_rows': sum(len(r.get('details', [])) for r in operations),
                       'rate_records': len(rates), 'annual_partition_checks': len(partitions),
                       'operation_types': dict(Counter(r['operationType'] for r in operations)),
                       'releaseTime_label_is_not_publication_certification': True}

    result['buybacks'] = {}
    for kind in ('operations', 'security_details'):
        files = sorted((root / 'transport/macro/raw/treasury').glob(f'buybacks_{kind}_page*.json.gz'))
        pages = [json.loads(gzip.decompress(p.read_bytes())) for p in files]
        rows = [row for page in pages for row in page['data']]
        require(len(files) == int(pages[0]['meta']['total-pages']), 'Buyback pages missing')
        require(len(rows) == int(pages[0]['meta']['total-count']), 'Buyback count mismatch')
        normalized = csv_file(root / 'normalized' / f'buybacks_{kind}.csv')
        require(all(r['available_at'] == '' for r in normalized), 'Invented buyback clock')
        require(canon([{k: v for k, v in r.items() if k != 'available_at'} for r in normalized]) == canon(rows), 'Buyback normalization mismatch')
        require(all(r['operation_date'] <= '2026-11-08' for r in rows), 'Future buyback outcome')
        result['buybacks'][kind] = {'rows': len(rows), 'first': min(r['operation_date'] for r in rows),
                                     'last': max(r['operation_date'] for r in rows),
                                     '2018_22_rows': sum('2018-01-01' <= r['operation_date'] <= '2022-12-31' for r in rows),
                                     '2024_onward_rows': sum(r['operation_date'] >= '2024-01-01' for r in rows)}
    clock_rows = csv_file(root / 'normalized/buyback_document_clocks.csv')
    expected_urls = {url for url in documents if url.endswith('.xml') and 'preanre' in url}
    require(len(clock_rows) == len(expected_urls) and {r['url'] for r in clock_rows} == expected_urls, 'Missing/duplicate XML clock row')
    fields = {'operation_status': 'operationStatus', 'announcement_DTM_source': 'announcementDTM',
              'operation_start_DTM_source': 'operationStartDTM', 'operation_close_DTM_source': 'operationCloseDTM',
              'settlement_date': 'settlementDT'}
    before, after, absent = Counter(), Counter(), Counter()
    for row in clock_rows:
        xml = ET.fromstring(documents[row['url']])
        values = {e.tag.split('}')[-1]: e.text for e in xml if e.text}
        require(all(row[k] == values.get(v, '') for k, v in fields.items()), 'XML source clock changed')
        require(row['result_DTM_source'] == values.get('resultsDTM', values.get('resultDTM', '')), 'Invented result clock')
        require(row['available_at'] == '', 'Invented public first receipt')
        status = row['operation_status']
        start, announcement = row['operation_start_DTM_source'], row['announcement_DTM_source']
        if not (start and announcement):
            absent[status] += 1
        elif dt.datetime.fromisoformat(announcement) < dt.datetime.fromisoformat(start):
            before[status] += 1
        else:
            after[status] += 1
    result['documents'] = {'supplement_requests': len(supplement), 'valid_xml': valid_xml, 'valid_pdf_signatures': valid_pdf,
                            'clock_rows': len(clock_rows), 'operation_start_offsets': dict(Counter(r['operation_start_DTM_source'][-6:] for r in clock_rows)),
                            'source_announcement_before_operation_by_document_status': dict(before),
                            'source_announcement_at_or_after_operation_by_document_status': dict(after),
                            'source_announcement_or_start_missing': dict(absent),
                            'result_publication_field_present': sum(bool(r['result_DTM_source']) for r in clock_rows)}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=PACKAGE)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'Output exists; choose a new audit receipt')
    result = audit(args.package)
    result['audited_at_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write('\n')
    print(json.dumps({'status': result['status'], 'files': result['transport']['files'], 'output': str(args.output)}))


if __name__ == '__main__':
    main()
