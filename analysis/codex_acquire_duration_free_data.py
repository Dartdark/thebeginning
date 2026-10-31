"""Validate sourced duration facts and materialize partial CSV inputs. No returns.

Acquisition uses public PDF-reader/manual numeric transcription recorded in
observations.json. This script checks that transcription's internal arithmetic
and records provenance/hashes; it does not assert source or publication truth.
"""
import argparse
import csv
from datetime import date
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = Path('agents/codex/inputs/scout_acquisition_20261029/duration')
FIELDS = ['observation_id', 'index_month', 'effective_date', 'index_duration_as_of',
          'reported_change_years', 'current_duration_years', 'new_duration_years',
          'document_date', 'benchmark_source_label', 'source_type', 'data_kind',
          'original_publication_at', 'available_at', 'point_in_time_eligible',
          'source_url', 'source_page', 'source_pdf_sha256', 'access_method', 'accessed_at', 'notes']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def next_month(month):
    year, number = map(int, month.split('-'))
    return date(year + (number == 12), number % 12 + 1, 1).isoformat()


def write_csv(path, fields, rows):
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows({field: row.get(field) for field in fields} for row in rows)


def build(root=ROOT):
    root = Path(root).resolve()
    directory = root / DIRECTORY
    source = directory / 'observations.json'
    data = json.loads(source.read_text(encoding='utf-8'))
    rows = data['observations']
    assert len({r['observation_id'] for r in rows}) == len(rows), 'Duplicate IDs'
    provider, quotes = [], []
    for row in rows:
        date.fromisoformat(row['index_month'] + '-01')
        assert row['source_url'].startswith('https://') and row['source_page'] >= 1
        amount = Decimal(row['reported_change_years'])
        assert amount.is_finite() and abs(amount) < 5, 'Units/value sanity failure'
        # No historical clock is promoted from a filename, as-of date or issue date.
        assert row['available_at'] is None and row['original_publication_at'] is None
        assert row['point_in_time_eligible'] is False and row['source_pdf_sha256'] is None
        if row['source_type'].startswith('original_provider_'):
            assert row['data_kind'] == 'forecast_table'
            assert row['effective_date'] == next_month(row['index_month'])
            current = Decimal(row['current_duration_years'])
            new = Decimal(row['new_duration_years'])
            assert abs((new - current) - amount) <= Decimal('0.015'), 'Rounded table bridge fails'
            assert row['index_duration_as_of'] < row['effective_date']
            provider.append(row)
        else:
            assert row['source_type'] == 'institutional_quote_of_provider'
            assert row['data_kind'] in {'post_event_quote', 'retrospective_reference', 'current_estimate_quote'}
            assert not row['current_duration_years'] and not row['new_duration_years']
            quotes.append(row)
    provider_path = directory / 'provider_forecasts.csv'
    quote_path = directory / 'institutional_quotes.csv'
    write_csv(provider_path, FIELDS, provider)
    write_csv(quote_path, FIELDS, quotes)
    coverage = []
    for year in range(2018, 2023):
        for month in range(1, 13):
            key = f'{year}-{month:02d}'
            p = sum(r['index_month'] == key for r in provider)
            q = sum(r['index_month'] == key for r in quotes)
            coverage.append({'index_month': key, 'provider_rows': p, 'institutional_quote_rows': q,
                             'availability_status': 'unknown', 'test_eligible': False,
                             'coverage_status': 'provider_table_clock_unknown' if p else
                                                ('quote_only_not_source_parity' if q else 'missing')})
    coverage_path = directory / 'coverage_2018_2022.csv'
    write_csv(coverage_path, list(coverage[0]), coverage)
    summary = {
        'schema_version': 1, 'source_id': 'ssrn:7601879',
        'status': 'partial_source_data_not_test_ready',
        'provider_forecast_rows': len(provider), 'institutional_quote_rows': len(quotes),
        'distinct_source_urls': len({r['source_url'] for r in rows}),
        'design_months': len(coverage),
        'design_months_with_original_provider_table': sum(r['provider_rows'] > 0 for r in coverage),
        'design_months_with_any_numeric_observation': sum(r['provider_rows'] + r['institutional_quote_rows'] > 0 for r in coverage),
        'design_months_missing_original_provider_forecast': sum(r['provider_rows'] == 0 for r in coverage),
        'provider_rows_outside_design': sum(not ('2018-01' <= r['index_month'] <= '2022-12') for r in provider),
        'verified_original_available_at_rows': 0, 'test_eligible_months': 0,
        'source_pdf_bytes_obtained': 0, 'paper_full_text_obtained': False,
        'new_return_trials': 0,
        'file_sha256': {p.relative_to(root).as_posix(): digest(p) for p in
                        [source, provider_path, quote_path, coverage_path]},
        'script_path': Path(__file__).relative_to(root).as_posix(),
        'script_sha256': digest(Path(__file__)), 'python': sys.executable,
        'reproduction': 'python analysis/codex_acquire_duration_free_data.py',
        'limits': ['CSV facts were manually transcribed from connected-reader sources; source PDFs are not redistributed.',
                   'As-of dates, issue dates and market-table update clocks do not prove original publication/receipt.',
                   'A retrospective August2020 reference stays known from its November2020 source, never backdated.',
                   'No missing month, original publication time, forecast or return is imputed.',
                   'Mixed source types remain in separate CSVs; partial facts are not a historical source-parity panel.'],
    }
    (directory / 'manifest.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    output = root / 'analysis/outputs/codex_duration_acquisition_20261029.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(json.dumps(build(), indent=2))
