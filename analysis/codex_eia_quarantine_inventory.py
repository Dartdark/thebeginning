"""Inventory saved, quarantined EIA captures without admitting or changing sources.

This source-only forensic audit opens no futures prices and computes no returns.
Actual converted-document headers and content identify observations; filenames and
declared/requested metadata are recorded only for comparison. JSON/text hashes do
not authenticate native PDF bytes or first-publication vintages.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'analysis/outputs/codex_eia_inventory_input_gate'
OUT = ROOT / 'analysis/outputs/codex_eia_quarantine_inventory'
REPORT = ROOT / 'agents/codex/results/eia_quarantine_inventory.md'
PARSER = ROOT / 'analysis/codex_eia_inventory_input_gate.py'
HEADER = re.compile(
    r'^(?P<title>Weekly Petroleum Status Report(?: Archives)?|) '
    r'\((?P<url>https://www\.eia\.gov/[^\s)]+)\)[ \t]*$', re.M)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return str(path.relative_to(ROOT))


def strings(value, location='$'):
    if isinstance(value, str):
        yield location, value
    elif isinstance(value, dict):
        for key in sorted(value):
            yield from strings(value[key], f'{location}.{key}')
    elif isinstance(value, list):
        for number, item in enumerate(value):
            yield from strings(item, f'{location}[{number}]')


def document_blocks(value):
    """Retain each distinct observed block and all of its JSON locations."""
    blocks = {}
    for location, text in strings(value):
        headers = list(HEADER.finditer(text))
        for number, match in enumerate(headers):
            end = headers[number + 1].start() if number + 1 < len(headers) else len(text)
            block = text[match.start():end]
            # A tool separator belongs to the envelope, not the preceding document.
            block = re.sub(r'\n-{15,}\s*$', '', block).rstrip('\r\n')
            item = blocks.setdefault(block, dict(title=match['title'], url=match['url'], json_locations=[]))
            item['json_locations'].append(location)
    return [(block, metadata) for block, metadata in blocks.items()]


def write_csv(path, rows, fields):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    started = datetime.now(timezone.utc).isoformat()
    spec = importlib.util.spec_from_file_location('eia_input_gate', PARSER)
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    calendar_path = SOURCE / 'design_archive_calendar.csv'
    panel_path = SOURCE / 'design_components.csv'
    with calendar_path.open(newline='') as stream:
        calendar = list(csv.DictReader(stream))
    with panel_path.open(newline='') as stream:
        panel = list(csv.DictReader(stream))
    admitted = {row['source_key'] for row in panel}
    admitted_values = {row['source_key']: tuple(float(row[column]) for column in parser.FIELDS) for row in panel}
    issue_calendar, pdf_calendar = {}, {}
    for row in calendar:
        issue_url, pdf_url = parser.expected_urls(row['source_key'], row['release_date'])
        if issue_url in issue_calendar or pdf_url in pdf_calendar:
            raise ValueError('Calendar document URLs must be unique across editions')
        issue_calendar[issue_url], pdf_calendar[pdf_url] = row, row
    files = sorted(path for folder in ('acquired', 'verified_sources') for path in (SOURCE / folder).glob('*.json'))
    inputs = files + [calendar_path, panel_path, PARSER]
    original_hashes = {relative(path): sha(path) for path in inputs}
    inventories, documents, pairs = [], [], []
    value_columns = parser.FIELDS
    for path in files:
        record = json.loads(path.read_text())
        if not isinstance(record, dict):
            raise ValueError(f'Unexpected non-object diagnostic JSON: {relative(path)}')
        file_row = dict(source_filename=relative(path), raw_json_sha256=sha(path),
            diagnostic_directory=path.parent.name, declared_source_key=record.get('source_key', ''),
            declared_release_date=record.get('release_date', ''), declared_week_ending=record.get('week_ending', ''),
            declared_issue_url=record.get('canonical_issue_url', ''),
            declared_highlights_url=record.get('canonical_highlights_url', ''),
            acquisition_status=record.get('acquisition_status', ''),
            recorded_error=record.get('error', ''),
            capture_utc=record.get('captured_utc', record.get('captureUTC', '')))
        file_docs = []
        for number, (text, metadata) in enumerate(document_blocks(record)):
            title, url = metadata['title'], metadata['url']
            kind = 'issue' if title == 'Weekly Petroleum Status Report Archives' else (
                'highlights' if url.endswith('/pdf/highlights.pdf') else 'other_official_document')
            row = dict(source_filename=relative(path), raw_json_sha256=file_row['raw_json_sha256'],
                document_number=number, document_kind=kind, observed_header_url=url,
                converted_block_sha256=hashlib.sha256(text.encode()).hexdigest(),
                json_locations=json.dumps(sorted(set(metadata['json_locations']))),
                declared_source_key=file_row['declared_source_key'],
                url_calendar_key='', verified_actual_edition_key='', observed_release_date='', observed_week_ending='',
                identity_status='unsupported_document_kind', identity_detail='', numeric_status='not_applicable',
                numeric_detail='', admitted_current_panel=False, current_panel_value_match='',
                declared_key_matches_actual='', quantity_trace='')
            row.update({column: '' for column in value_columns})
            expected = (issue_calendar if kind == 'issue' else pdf_calendar).get(url)
            if kind not in ('issue', 'highlights'):
                file_docs.append(row)
                continue
            if expected is None:
                row['identity_status'] = 'observed_url_not_design_calendar'
                file_docs.append(row)
                continue
            row['url_calendar_key'] = expected['source_key']
            try:
                if kind == 'issue':
                    if parser.header_url(text, 'Weekly Petroleum Status Report Archives') != url:
                        raise ValueError('Actual issue header changed during extraction')
                    if len(re.findall(r'^Weekly Petroleum Status Report Archives \(', text, re.M)) != 1:
                        raise ValueError('Multiple issue document headers')
                    body = parser.clean_document(text)
                    release = re.search(r'\bRelease Date:\s*' + parser.DATE_WORDS, body, re.I)
                    if not release:
                        raise ValueError('Issue release date is missing')
                    row['observed_release_date'] = parser.date_words(release[1])
                    if row['observed_release_date'] != expected['release_date']:
                        raise ValueError('Observed issue release date conflicts with its actual URL/calendar')
                    week = re.search(r'\bData for week ending\s+([^|]+)\|', body, re.I)
                    if week and re.fullmatch(parser.DATE_WORDS, week[1].strip()):
                        row['observed_week_ending'] = parser.date_words(week[1].strip())
                        if row['observed_week_ending'] != expected['week_ending']:
                            raise ValueError('Observed issue week-ending conflicts with actual URL/calendar')
                    else:
                        row['identity_detail'] = 'HTML week header missing/malformed; any pair still requires PDF/index agreement'
                    row['identity_status'] = 'issue_url_release_verified'
                else:
                    row['observed_week_ending'] = parser.pdf_identity(text, url, expected['week_ending'])
                    row['identity_status'] = 'pdf_url_page_first_week_verified'
                row['verified_actual_edition_key'] = expected['source_key']
                row['admitted_current_panel'] = expected['source_key'] in admitted
                row['declared_key_matches_actual'] = file_row['declared_source_key'] == expected['source_key']
            except ValueError as error:
                row['identity_status'] = 'identity_failure'
                row['identity_detail'] = str(error)
            if kind == 'highlights':
                if row['verified_actual_edition_key']:
                    try:
                        quantities = parser.prose_change_details(text)
                        row.update({column: quantities[column]['value_mb'] for column in value_columns})
                        row['quantity_trace'] = json.dumps(quantities, sort_keys=True)
                        row['numeric_status'] = 'explicit_weekly_triple_verified'
                        if row['admitted_current_panel']:
                            row['current_panel_value_match'] = tuple(row[column] for column in value_columns) == admitted_values[expected['source_key']]
                    except ValueError as error:
                        row['numeric_status'] = 'numeric_failure'
                        row['numeric_detail'] = str(error)
                else:
                    row['numeric_status'] = 'not_parsed_failed_identity'
            file_docs.append(row)
        documents.extend(file_docs)
        issue_keys = {row['verified_actual_edition_key'] for row in file_docs if row['document_kind'] == 'issue'
                      and row['identity_status'] == 'issue_url_release_verified'}
        pdf_keys = {row['verified_actual_edition_key'] for row in file_docs if row['document_kind'] == 'highlights'
                    and row['numeric_status'] == 'explicit_weekly_triple_verified'}
        for key in sorted(issue_keys & pdf_keys):
            pdfs = [row for row in file_docs if row['verified_actual_edition_key'] == key
                    and row['numeric_status'] == 'explicit_weekly_triple_verified']
            values = {tuple(row[column] for column in value_columns) for row in pdfs}
            pair = dict(source_filename=relative(path), raw_json_sha256=file_row['raw_json_sha256'],
                declared_source_key=file_row['declared_source_key'], observed_actual_edition_key=key,
                declared_key_matches_actual=file_row['declared_source_key'] == key,
                issue_document_numbers=json.dumps([row['document_number'] for row in file_docs
                    if row['document_kind'] == 'issue' and row['verified_actual_edition_key'] == key]),
                highlights_document_numbers=json.dumps([row['document_number'] for row in pdfs]),
                status='matching_actual_documents' if len(values) == 1 else 'conflicting_numeric_documents',
                admitted_current_panel=key in admitted,
                new_eligible_edition=len(values) == 1 and key not in admitted)
            pair.update(dict(zip(value_columns, next(iter(values)) if len(values) == 1 else ('', '', ''))))
            pairs.append(pair)
        file_row.update(observed_issue_urls=json.dumps(sorted({row['observed_header_url'] for row in file_docs if row['document_kind'] == 'issue'})),
            observed_highlights_urls=json.dumps(sorted({row['observed_header_url'] for row in file_docs if row['document_kind'] == 'highlights'})),
            observed_verified_edition_keys=json.dumps(sorted({row['verified_actual_edition_key'] for row in file_docs if row['verified_actual_edition_key']})),
            observed_document_blocks=len(file_docs), complete_pair_count=sum(pair['source_filename'] == relative(path) for pair in pairs),
            status='observed_documents_retained' if file_docs else 'no_converted_document_headers')
        inventories.append(file_row)
    highlights = [row for row in documents if row['document_kind'] == 'highlights']
    quantified = [row for row in highlights if row['numeric_status'] == 'explicit_weekly_triple_verified']
    valid_pairs = [row for row in pairs if row['status'] == 'matching_actual_documents']
    new_keys = sorted({row['observed_actual_edition_key'] for row in valid_pairs if row['new_eligible_edition']})
    summary = dict(stage='offline_quarantine_feasibility_only',
        expected_calendar_editions=len(calendar), currently_admitted_component_triples=len(admitted),
        diagnostic_json_files=len(files), acquired_json_files=sum(path.parent.name == 'acquired' for path in files),
        verified_sources_json_files=sum(path.parent.name == 'verified_sources' for path in files),
        observed_document_blocks=len(documents),
        observed_issue_document_blocks=sum(row['document_kind'] == 'issue' for row in documents),
        observed_highlights_document_blocks=len(highlights),
        other_official_document_blocks=sum(row['document_kind'] == 'other_official_document' for row in documents),
        files_without_observed_document_headers=sum(not row['observed_document_blocks'] for row in inventories),
        identity_failure_document_blocks=sum(row['identity_status'] == 'identity_failure' for row in documents),
        numeric_failure_highlights_blocks=sum(row['numeric_status'] == 'numeric_failure' for row in highlights),
        declared_key_mismatch_verified_documents=sum(row['declared_key_matches_actual'] is False for row in documents),
        unique_observed_highlights_urls=len({row['observed_header_url'] for row in highlights}),
        unique_quantified_pdf_editions=len({row['verified_actual_edition_key'] for row in quantified}),
        unique_quantified_pdf_editions_already_admitted=len({row['verified_actual_edition_key'] for row in quantified if row['admitted_current_panel']}),
        quantified_pdf_editions_conflicting_with_current_values=sorted({row['verified_actual_edition_key'] for row in quantified
            if row['admitted_current_panel'] and not row['current_panel_value_match']}),
        unique_nonquantified_pdf_editions=sorted({row['verified_actual_edition_key'] for row in highlights
            if row['verified_actual_edition_key'] and row['numeric_status'] != 'explicit_weekly_triple_verified'}),
        matching_actual_document_pairs=len(valid_pairs),
        unique_matching_actual_document_editions=len({row['observed_actual_edition_key'] for row in valid_pairs}),
        unique_matching_actual_document_editions_already_admitted=len({row['observed_actual_edition_key'] for row in valid_pairs if row['admitted_current_panel']}),
        new_eligible_edition_keys=new_keys, new_eligible_editions=len(new_keys),
        source_policy_amendment_justified_by_additional_coverage=bool(new_keys),
        sources_admitted=0, source_policy_changed=False, sources_rekeyed_or_copied=False,
        network_requests=0, futures_price_files_opened=False, new_strategy_return_trials=0,
        hash_basis='SHA256 of saved converted-source JSON and extracted text; not original PDF bytes or first-vintage proof')
    if {relative(path): sha(path) for path in inputs} != original_hashes:
        raise ValueError('An input changed during the read-only forensic audit; refuse to publish mixed evidence')
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / 'file_inventory.csv', inventories, list(inventories[0]))
    write_csv(OUT / 'document_inventory.csv', documents, list(documents[0]))
    write_csv(OUT / 'matching_document_pairs.csv', pairs, list(pairs[0]))
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    marker = dict(started_utc=started, completed_utc=datetime.now(timezone.utc).isoformat(),
        workspace=str(ROOT), interpreter=sys.executable, script=relative(Path(__file__).resolve()),
        script_sha256=sha(Path(__file__).resolve()), actual_offline_source_processing=True,
        all_input_hashes_unchanged=True, input_sha256=original_hashes,
        network_requests=0, futures_price_files_opened=False, new_strategy_return_trials=0,
        sources_admitted=0, source_policy_changed=False, sources_rekeyed_or_copied=False)
    (OUT / 'source_only_execution.json').write_text(json.dumps(marker, indent=2) + '\n')
    verdict = 'no additional eligible editions' if not new_keys else 'additional source candidates require separate review'
    recommendation = ('No source-policy amendment is justified by additional coverage in these captures.' if not new_keys
                      else 'Additional candidates require separate source-policy review; none is admitted here.')
    unquantified_description = ', '.join(summary['unique_nonquantified_pdf_editions']) or 'none'
    mismatches = [row for row in documents if row['document_kind'] == 'highlights'
                  and row['verified_actual_edition_key'] and row['declared_key_matches_actual'] is False]
    if mismatches:
        example = mismatches[0]
        mismatch_description = (f"For example, {example['source_filename']} declares "
            f"{example['declared_source_key']} but contains an actual Highlights document for "
            f"{example['verified_actual_edition_key']}; the current-panel relation is retained in the inventory.")
    else:
        mismatch_description = 'No declared-key/verified-Highlights-edition mismatch was found.'
    REPORT.write_text(f'''# EIA quarantine inventory: {verdict}

Summary: Actual document headers/content in quarantined captures add {len(new_keys)} eligible editions.
The admitted panel remains {len(admitted)}/{len(calendar)}; this is source forensics, not strategy performance.
{recommendation} No new returns or t milestone.

Plan: agents/codex/plans/eia_inventory_input_gate.md, commit5723c95; source intake only.
Script: analysis/codex_eia_quarantine_inventory.py.
Output: analysis/outputs/codex_eia_quarantine_inventory/. Economic/return trials:0.

## Observed evidence

Inspected {summary['acquired_json_files']} acquired/ JSONs and {summary['verified_sources_json_files']} verified_sources/ JSONs.
Actual converted text contains {summary['unique_observed_highlights_urls']} distinct Highlights URLs.
{summary['unique_quantified_pdf_editions']} editions have strict PDF URL/page/week identity and explicit weekly triples;
{summary['unique_quantified_pdf_editions_already_admitted']} are already admitted,
with {len(summary['quantified_pdf_editions_conflicting_with_current_values'])} conflicting-value editions.
Identified PDF editions without a quantified triple: {unquantified_description}. Exact numeric failures
remain in document_inventory.csv; no qualitative change was assigned a numeric value.
Matching actual issue URL/release and same-edition PDF URL/page/week/numeric evidence gives
{summary['unique_matching_actual_document_editions']} distinct complete pairs, of which
{summary['unique_matching_actual_document_editions_already_admitted']} are already admitted.

The file inventory retains every diagnostic JSON, its SHA256, declared/requested metadata and observed URLs.
The document inventory retains every detected block, its JSON locations, actual identity/numeric results,
failures and current-panel relation. Matching pairs are diagnostic metadata, not admitted source records.
Filename/requested-date mismatches are retained; they never identify an observation.
{mismatch_description}

## Limits and continuation

No source file was changed, copied, rekeyed or admitted. All input hashes match before/after execution.
The existing ingestion policy still ignores acquired/ and verified_sources/. No network, futures-price file,
return calculation, validation, account comparison or PowerLanguage was used. This adds zero economic trials.
JSON/text hashes preserve these converted snapshots; they do not establish native PDF authenticity,
immutable first-publication values or historical receipt clocks. The remaining {len(calendar)-len(admitted)} missing or ambiguous editions,
clock/vintage review, source-access requirement and native CL/MCL execution gates remain unresolved.
Continue the wider research program; do not repeat the already delivered access-blocker notification.
''')
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()
