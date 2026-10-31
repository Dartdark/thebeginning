"""Build a sourced claims-date/embargo ledger; never generate release weekdays or returns."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'agents/codex/inputs/scout_acquisition_20261029/claims_calendar'


def rows_of(value):
    return value.get('verified_rows', value.get('verified', value.get('rows', [])))


def write_csv(path, rows, columns):
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def acquire(base=BASE):
    base = Path(base)
    secondary = json.loads((base / 'secondary_dates.json').read_text(encoding='utf-8'))
    candidates = set(secondary['secondary_dates'])
    assert len(candidates) == len(secondary['secondary_dates'])
    for value in candidates:
        parsed = date.fromisoformat(value)
        assert 2018 <= parsed.year <= 2022
    facts, date_facts, artifacts = {}, {}, []
    for path in sorted(base.glob('primary_*.json')):
        content = json.loads(path.read_text(encoding='utf-8'))
        source_rows = rows_of(content)
        artifacts.append({'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                          'header_rows': len(source_rows), 'date_only_rows': len(content.get('date_only_rows', []))})
        for item in content.get('date_only_rows', []):
            assert item.get('embargo_time_et') is None
            assert item['release_date'] in candidates
            if item.get('reference_week_ending'):
                assert 0 < (date.fromisoformat(item['release_date']) - date.fromisoformat(item['reference_week_ending'])).days <= 8
            assert item.get('original_schedule_available_at') is None
            assert item['source_url'].startswith(('https://www.dol.gov/', 'https://oui.doleta.gov/'))
            date_facts[item['release_date']] = dict(item, source_fact_file=str(path.relative_to(ROOT)))
        for item in source_rows:
            release = date.fromisoformat(item['release_date'])
            assert 2018 <= release.year <= 2022
            if item.get('reference_week_ending'):
                reference = date.fromisoformat(item['reference_week_ending'])
                assert 0 < (release - reference).days <= 8
            assert item['timezone'] == 'America/New_York'
            assert item.get('source_url', '').startswith(('https://www.dol.gov/', 'https://oui.doleta.gov/'))
            assert item.get('original_schedule_available_at') is None
            clock = item['embargo_time_et']
            if len(clock) == 5:
                clock += ':00'
            parsed_clock = datetime.strptime(clock, '%H:%M:%S').time()
            method = 'indexed_primary_header' if 'index' in item['evidence_method'].lower() else 'direct_pdf_header'
            stamp = datetime.combine(release, parsed_clock, ZoneInfo('America/New_York'))
            fact = {
                'release_date': release.isoformat(), 'release_time_et': clock,
                'timezone': 'America/New_York', 'embargo_lift_utc': stamp.astimezone(timezone.utc).isoformat(),
                'reference_week_ending': item.get('reference_week_ending') or '',
                'source_url': item['source_url'], 'evidence_method': method,
                'source_location': item.get('source_location', 'Official release embargo header'),
                'web_ref': item.get('web_ref') or '', 'source_fact_file': str(path.relative_to(ROOT)),
                'original_schedule_available_at': '', 'actual_publication_or_receipt_at': '',
                'return_eligible': False,
            }
            previous = facts.get(release.isoformat())
            if previous:
                assert previous['release_time_et'] == clock
                if previous['reference_week_ending'] and fact['reference_week_ending']:
                    assert previous['reference_week_ending'] == fact['reference_week_ending']
                if previous['evidence_method'] == 'direct_pdf_header':
                    continue
            facts[release.isoformat()] = fact
    dates = sorted(candidates | set(facts))
    calendar = []
    for value in dates:
        fact = facts.get(value)
        date_fact = date_facts.get(value)
        calendar.append({
            'release_family': 'INITIAL_CLAIMS', 'release_date': value,
            'release_time_et': fact['release_time_et'] if fact else '',
            'timezone': fact['timezone'] if fact else '',
            'embargo_lift_utc': fact['embargo_lift_utc'] if fact else '',
            'reference_week_ending': fact['reference_week_ending'] if fact else (date_fact.get('reference_week_ending') or '' if date_fact else ''),
            'primary_release_date_corroborated': bool(fact or date_fact),
            'primary_header_corroborated': bool(fact),
            'source_url': fact['source_url'] if fact else (date_fact['source_url'] if date_fact else secondary['source_url']),
            'evidence_method': fact['evidence_method'] if fact else ('indexed_primary_date_only' if date_fact else 'secondary_date_fact_only'),
            'source_fact_file': fact['source_fact_file'] if fact else (date_fact['source_fact_file'] if date_fact else str((base / 'secondary_dates.json').relative_to(ROOT))),
            'original_schedule_available_at': '', 'actual_publication_or_receipt_at': '',
            'return_eligible': False,
        })
    primary = sorted(facts.values(), key=lambda row: row['release_date'])
    write_csv(base / 'primary_embargo_headers.csv', primary, list(primary[0]))
    write_csv(base / 'claims_calendar_2018_2022.csv', calendar, list(calendar[0]))
    coverage = []
    for year in range(2018, 2023):
        selected = [row for row in calendar if row['release_date'].startswith(str(year))]
        coverage.append({'year': year, 'sourced_dates': len(selected),
                         'primary_release_dates': sum(row['primary_release_date_corroborated'] for row in selected),
                         'primary_embargo_headers': sum(row['primary_header_corroborated'] for row in selected),
                         'unknown_embargo_times': sum(not row['release_time_et'] for row in selected),
                         'original_schedule_available_at_known': 0, 'return_eligible_rows': 0})
    write_csv(base / 'coverage_2018_2022.csv', coverage, list(coverage[0]))
    counts = Counter(row['evidence_method'] for row in primary)
    result = {'schema_version': 1, 'secondary_dates': len(candidates), 'sourced_date_union': len(dates),
              'primary_release_date_rows': len(set(facts) | set(date_facts)),
              'primary_embargo_header_rows': len(primary), 'unknown_embargo_time_rows': len(dates) - len(primary),
              'primary_evidence_methods': dict(counts), 'coverage': coverage,
              'restored_secondary_omissions': sorted(set(facts) - candidates),
              'original_schedule_available_at_known': 0, 'actual_receipt_known': 0,
              'return_eligible_rows': 0, 'return_trials': 0,
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'source_fact_artifacts': artifacts,
              'limits': ['Source-date universe is a pinned secondary archive-date collection plus separately verified official repairs; no Thursdays generated.',
                         'A printed embargo timestamp is not a measured actual release/receipt or original advance schedule announcement.',
                         'Direct PDF parsing and indexed official headers remain distinguished; no local PDF bytes or PDF hashes claimed.',
                         'Calendar completeness beyond the sourced universe and pre-entry availability remain unverified. No source-paper trading universe or returns defined.']}
    for path in [base / 'primary_embargo_headers.csv', base / 'claims_calendar_2018_2022.csv', base / 'coverage_2018_2022.csv']:
        result.setdefault('outputs', []).append({'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    (base / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'analysis/outputs/codex_claims_calendar_acquisition_20261029.json')
    args = parser.parse_args()
    result = acquire()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ['sourced_date_union', 'primary_embargo_header_rows', 'unknown_embargo_time_rows', 'primary_evidence_methods', 'restored_secondary_omissions', 'return_trials']}, indent=2))
