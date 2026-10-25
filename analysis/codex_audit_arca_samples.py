"""No-return inventory of the two explicitly collected July 2026 Arca TAQ samples.

No ES input, forward returns, parameter selection or trading. Raw SPY extracts stay
in ignored research inputs. Reject unknown type-105 widths; never sort bad input.
"""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import gzip
import hashlib
import json
from pathlib import Path
import re
import statistics
import sys
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / 'agents/codex/inputs/auction_data_sources_20261025/nyse_samples'
OUT = REPO / 'analysis/outputs/codex_auction_sample_intake'
# Observed physical CSV positions. TAQ v2.4a section 10 skips ordinal 4 in
# its table, but the actual sample contains 24, not 25, CSV fields.
FIELDS = ('message_type sequence source_time symbol symbol_sequence reference_price '
          'paired_qty total_imbalance_qty market_imbalance_qty auction_time auction_type '
          'imbalance_side continuous_book_clearing_price auction_interest_clearing_price '
          'ssr_filing_price indicative_match_price upper_collar lower_collar auction_status '
          'freeze_status num_extensions unpaired_qty unpaired_side significant_imbalance').split()
QUANTITIES = ('paired_qty', 'total_imbalance_qty', 'market_imbalance_qty', 'unpaired_qty')
PRICES = ('reference_price', 'continuous_book_clearing_price', 'auction_interest_clearing_price',
          'ssr_filing_price', 'indicative_match_price', 'upper_collar', 'lower_collar')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def time_ns(value):
    if not re.fullmatch(r'\d{2}:\d{2}:\d{2}\.\d{9}', value):
        raise ValueError('Expected HH:MM:SS.nnnnnnnnn')
    hour, minute, second, nano = map(int, re.split(r'[:.]', value))
    if hour > 23 or minute > 59 or second > 59:
        raise ValueError('Invalid source time')
    return ((hour * 60 + minute) * 60 + second) * 10**9 + nano


def parse_imbalance(row):
    if len(row) != len(FIELDS) or row[0] != '105':
        raise ValueError('Unsupported type-105 CSV layout')
    data = dict(zip(FIELDS, row))
    data['source_ns'] = time_ns(data['source_time'])
    for name in ('sequence', 'symbol_sequence', 'num_extensions') + QUANTITIES:
        if not re.fullmatch(r'\d+', data[name]):
            raise ValueError('Invalid unsigned integer: ' + name)
        data[name] = int(data[name])
    for name in PRICES:
        try:
            value = Decimal(data[name])
        except InvalidOperation:
            raise ValueError('Invalid decimal: ' + name)
        if not value.is_finite() or value < 0:
            raise ValueError('Invalid nonnegative price: ' + name)
    if data['imbalance_side'] not in ('B', 'S', ' '):
        raise ValueError('Unknown total-imbalance side')
    if data['auction_type'] not in ('O', 'M', 'H', 'C', 'R', 'P'):
        raise ValueError('Unknown auction type')
    if not re.fullmatch(r'\d{4}', data['auction_time']):
        raise ValueError('Invalid projected auction time')
    h, m = int(data['auction_time'][:2]), int(data['auction_time'][2:])
    if h > 23 or m > 59:
        raise ValueError('Invalid projected auction time')
    if data['auction_status'] not in ('0', '1', '2', '3'):
        raise ValueError('Unknown auction status')
    if data['freeze_status'] not in ('0', '1'):
        raise ValueError('Unknown freeze status')
    # Only the total imbalance has an explicit side in Arca. Do not sign the
    # market imbalance with it, or treat NYSE-only UnpairedQty as Arca demand.
    return data


def clock_views(day, source):
    local = datetime.strptime(day + ' ' + source[:8], '%Y%m%d %H:%M:%S')
    local = local.replace(tzinfo=ZoneInfo('America/New_York'))
    return dict(source_time_raw=source, assumed_et=local.isoformat(),
                assumed_ct=local.astimezone(ZoneInfo('America/Chicago')).isoformat(),
                assumed_utc=local.astimezone(timezone.utc).isoformat(),
                conversion_precision='seconds; raw source retains all nine fractional digits')


def audit(day):
    path = ROOT / ('EQY_US_ARCA_REF_IMBALANCES_' + day + '.gz')
    manifest = json.loads(path.with_suffix('.manifest.json').read_text())
    actual_hash = digest(path)
    if actual_hash != manifest['sha256'] or path.stat().st_size != manifest['bytes']:
        raise ValueError('Original no longer matches acquisition manifest')
    counts, widths, auction_types, bad = Counter(), Counter(), Counter(), Counter()
    spy, raw_spy, examples = [], [], []
    total_bytes = 0
    with gzip.open(path, 'rb') as stream:
        for line_number, line in enumerate(stream, 1):
            total_bytes += len(line)
            if total_bytes > 10_000_000_000 or len(line) > 100_000:
                raise ValueError('Unexpected expansion or oversized row')
            row = line.decode('ascii').rstrip('\r\n').split(',')
            counts[row[0]] += 1
            if row[0] != '105':
                continue
            widths[len(row)] += 1
            if len(row) != 24:
                raise ValueError('Unknown type-105 width at line ' + str(line_number))
            if row[3] != 'SPY':
                continue
            raw_spy.append(row)
            auction_types[row[10]] += 1
            try:
                data = parse_imbalance(row)
            except ValueError as exc:
                bad[str(exc)] += 1
                if len(examples) < 10:
                    examples.append(dict(line=line_number, error=str(exc)))
                continue
            spy.append(data)
    if total_bytes != manifest['uncompressed_bytes']:
        raise ValueError('Expansion size differs from acquisition manifest')
    close = [row for row in spy if row['auction_type'] == 'C']
    seqs = [row['sequence'] for row in spy]
    symbol_seqs = [row['symbol_sequence'] for row in spy]
    times = [row['source_ns'] for row in spy]
    close_gaps = [(b['source_ns'] - a['source_ns']) / 1e9 for a, b in zip(close, close[1:])]
    nonzero_sides = [row['imbalance_side'] for row in close if row['total_imbalance_qty'] > 0]
    minute_counts = Counter(row['source_time'][:5] for row in close)
    after_close = sum(row['source_time'][:8] >= row['auction_time'][:2] + ':' + row['auction_time'][2:] + ':00'
                      for row in close)
    issues = dict(bad_spy_fields=sum(bad.values()),
                  duplicate_spy_sequence=len(seqs) - len(set(seqs)),
                  duplicate_spy_symbol_sequence=len(symbol_seqs) - len(set(symbol_seqs)),
                  spy_sequence_reversals=sum(b < a for a, b in zip(seqs, seqs[1:])),
                  spy_symbol_sequence_reversals=sum(b < a for a, b in zip(symbol_seqs, symbol_seqs[1:])),
                  spy_time_reversals=sum(b < a for a, b in zip(times, times[1:])),
                  nonzero_total_without_side=sum(row['total_imbalance_qty'] > 0 and row['imbalance_side'] == ' ' for row in close),
                  zero_total_with_side=sum(row['total_imbalance_qty'] == 0 and row['imbalance_side'] != ' ' for row in close))
    parsed = ROOT.parent / 'parsed'
    parsed.mkdir(exist_ok=True)
    extract = parsed / ('SPY_105_' + day + '.csv')
    # Derived extraction may be regenerated; compressed original is never changed.
    with extract.open('w', newline='', encoding='ascii') as f:
        writer = csv.writer(f)
        writer.writerow(FIELDS)
        writer.writerows(raw_spy)
    result = dict(date=day, original_path=path.relative_to(REPO).as_posix(),
                  original_sha256=actual_hash, compressed_bytes=path.stat().st_size,
                  uncompressed_bytes=total_bytes, message_counts=dict(counts),
                  type105_field_counts=dict(widths), spy_type105_rows=len(raw_spy),
                  spy_auction_type_counts=dict(auction_types), spy_closing_rows=len(close),
                  spy_closing_projected_times=dict(Counter(row['auction_time'] for row in close)),
                  spy_closing_side_counts=dict(Counter(row['imbalance_side'] for row in close)),
                  spy_closing_zero_total_rows=sum(row['total_imbalance_qty'] == 0 for row in close),
                  spy_closing_rows_at_or_after_projected_auction=after_close,
                  spy_closing_nonzero_side_changes=sum(a != b for a, b in zip(nonzero_sides, nonzero_sides[1:])),
                  spy_closing_minute_counts=dict(sorted(minute_counts.items())),
                  spy_closing_gap_seconds=dict(max=max(close_gaps, default=None),
                                              median=statistics.median(close_gaps) if close_gaps else None),
                  spy_closing_freeze_counts=dict(Counter(row['freeze_status'] for row in close)),
                  first_freeze_source_time=next((row['source_time'] for row in close if row['freeze_status'] == '1'), None),
                  spy_closing_status_counts=dict(Counter(row['auction_status'] for row in close)),
                  spy_closing_distinct_reference_prices=len(set(row['reference_price'] for row in close)),
                  spy_closing_distinct_indicative_prices=len(set(row['indicative_match_price'] for row in close)),
                  spy_closing_distinct_quantities=len(set(row['total_imbalance_qty'] for row in close)),
                  sample_checks=issues, bad_field_counts=dict(bad), bad_examples=examples,
                  first_close=clock_views(day, close[0]['source_time']) if close else None,
                  last_close=clock_views(day, close[-1]['source_time']) if close else None,
                  raw_spy_extract_path=extract.relative_to(REPO).as_posix(),
                  raw_spy_extract_sha256=digest(extract),
                  schema_scope='physical positions checked; quantity-definition era unresolved',
                  timezone_scope='ET interpretation consistent with auction schedule; vendor confirmation still required',
                  sample_format_gate='PASS' if close and not any(issues.values()) else 'CONCERNS',
                  study_data_gate='NEEDS DATA', return_trials=0)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dates', nargs='+', choices=['20260701', '20260702'], default=['20260701', '20260702'])
    args = parser.parse_args()
    results = [audit(day) for day in args.dates]
    OUT.mkdir(parents=True, exist_ok=True)
    result = dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),
                  interpreter=sys.executable, python_version=sys.version, caches_rebuilt=False,
                  packages_installed=False, return_trials=0, status='NEEDS DATA',
                  parser_sha256=digest(Path(__file__)), samples=results,
                  unresolved=['2018-22 SPY history and completeness', 'historical schema/rule eras',
                              'TAQ versus real-time quantity definitions after 2025-11-13',
                              'customer receipt timestamps and defensible lag',
                              'SPY auction results and corrections', 'synchronized SPY NBBO and ES quotes',
                              'price, licence and executable costs', 'effective design opportunity census'])
    (OUT / 'sample_audit.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps([dict(date=s['date'], spy_closing_rows=s['spy_closing_rows'],
                           sample_format_gate=s['sample_format_gate'], issues=s['sample_checks']) for s in results], indent=2))


if __name__ == '__main__':
    main()
