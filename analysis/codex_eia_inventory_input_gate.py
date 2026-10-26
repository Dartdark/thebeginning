"""Rebuild a no-return EIA archive calendar and source-coverage audit.

Inputs are saved official-source observations from the connected web app.
This script never opens a futures price file or calculates strategy P&L.
Captured converted text has its own hash; it is not an original-PDF-byte hash.
"""
from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import math
from pathlib import Path
import re
from types import SimpleNamespace

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_eia_inventory_input_gate'
MONTHS = {name: n for n, name in enumerate(calendar.month_name) if name}
FIELDS = ['crude_ex_spr_change_mb', 'gasoline_change_mb', 'distillate_change_mb']
DATE_WORDS = r'([A-Za-z]+\s+\d{1,2},\s*\d{4})'
SAMPLE_EXPECTED = {
    '2018-01-04': ('2017-12-29', -7.4, 4.8, 8.9),
    '2019-01-09': ('2019-01-04', -1.7, 8.1, 10.6),
    '2020-07-08': ('2020-07-03', 5.7, -4.8, 3.1),
    '2021-04-07': ('2021-04-02', -3.5, 4.0, 1.5),
    '2022-12-29': ('2022-12-23', .7, -3.1, .3),
}


class SourceGateError(ValueError):
    def __init__(self, reason, detail):
        self.reason = reason
        super().__init__(detail)


def clean_document(text):
    text = re.sub(r'^\s*L\d+(?:@P\d+(?:-\d+)?)?:\s*', '', text, flags=re.M)
    return re.sub(r'\s+', ' ', text).replace('−', '-')


def iso_date(value):
    return str(pd.Timestamp(value).date())


def date_words(value):
    try:
        return str(pd.to_datetime(value, format='%B %d, %Y').date())
    except (ValueError, TypeError) as error:
        raise SourceGateError('unparseable_document_date', f'Unparseable document date:{value!r}') from error


def header_url(text, title):
    first = text.splitlines()[0] if text else ''
    match = re.fullmatch(re.escape(title) + r' \((https://www\.eia\.gov/[^\s)]+)\)', first)
    if not match:
        raise SourceGateError('invalid_document_header', f'Missing exact official {title} header')
    return match[1]


def pdf_identity(text, expected_url, expected_week):
    try:
        url = header_url(text, 'Weekly Petroleum Status Report')
    except SourceGateError:
        # One observed source has a blank PDF metadata title. Its internal official
        # title must independently agree before accepting the exact URL header.
        first = text.splitlines()[0] if text else ''
        blank = re.fullmatch(r' \((https://www\.eia\.gov/[^\s)]+)\)', first)
        internal = re.search(r'^L0@P0:\s*(?:[ivxlcdm]+\s+)?Weekly Petroleum Status Report/Energy Information Administration\s*$',
                             text, flags=re.M | re.I)
        if not blank or not internal:
            raise
        url = blank[1]
    if url != expected_url:
        raise SourceGateError('wrong_highlights_url', f'Actual{url}; expected{expected_url}')
    pdf_headers = re.findall(r'^(?:Weekly Petroleum Status Report)? \((https://www\.eia\.gov/[^\s)]+)\)$', text, flags=re.M)
    if pdf_headers != [expected_url]:
        raise SourceGateError('multiple_pdf_document_blocks', 'Expected one converted Highlights document')
    meta = text.split('L0@P', 1)[0]
    pages = re.search(r'Content type:\s*application/pdf;\s*Number of pages:\s*(\d+)\b', meta)
    if not pages or int(pages[1]) != 1:
        raise SourceGateError('not_one_page_highlights', 'Converted source must identify a one-page PDF')
    first_week = re.search(r'\bweek end(?:ing|ed)\s+' + DATE_WORDS, clean_document(text), flags=re.I)
    if not first_week:
        raise SourceGateError('missing_pdf_week_ending', 'PDF first week-ending statement is unavailable')
    actual_week = date_words(first_week[1])
    if actual_week != expected_week:
        raise SourceGateError('wrong_pdf_week_ending', f'Actual{actual_week}; expected{expected_week}')
    return actual_week


def expected_urls(source_key, release):
    stem = release.replace('-', '_')
    # The index publishes this delayed edition onJune29 under its data-week folder.
    if source_key == '2022-06-29__2022-06-17':
        stem = '2022_06_17_data'
    directory = f'https://www.eia.gov/petroleum/supply/weekly/archive/{release[:4]}/{stem}'
    return f'{directory}/wpsr_{stem}.php', f'{directory}/pdf/highlights.pdf'


def source_identity(record, row):
    release, week = iso_date(row.release_date), iso_date(row.week_ending)
    for key, expected in (('source_key', row.source_key), ('release_date', release), ('week_ending', week)):
        if record.get(key) != expected:
            raise SourceGateError('record_calendar_id_mismatch', f'{key}:actual{record.get(key)!r}; expected{expected!r}')
    issue = record.get('issue_document_text')
    highlights = record.get('highlights_document_text')
    if not isinstance(issue, str) or not isinstance(highlights, str):
        raise SourceGateError('missing_document_text', 'Expected exact converted issue and Highlights text blocks')
    if re.search(r'(?:\bHTTP(?:/\S+)?\s+403\b|\(403\)|\b403\s+Forbidden\b|access denied)',
                 issue + '\n' + highlights, flags=re.I):
        raise SourceGateError('explicit_access_denial', 'Converted response contains an explicit access-denial error')
    if record.get('error'):
        raise SourceGateError('recorded_acquisition_error', str(record['error']))
    expected_issue, expected_highlights = expected_urls(row.source_key, release)
    actual_issue = header_url(issue, 'Weekly Petroleum Status Report Archives')
    if actual_issue != expected_issue or record.get('canonical_issue_url') != actual_issue:
        raise SourceGateError('wrong_issue_url', f'Actual{actual_issue}; expected{expected_issue}')
    if record.get('canonical_highlights_url') != expected_highlights:
        raise SourceGateError('record_highlights_url_mismatch', 'Record Highlights URL differs from expected same-issue URL')
    if len(re.findall(r'^Weekly Petroleum Status Report Archives \(', issue, flags=re.M)) != 1:
        raise SourceGateError('multiple_issue_document_blocks', 'Expected one converted issue document')
    body = clean_document(issue)
    release_match = re.search(r'\bRelease Date:\s*' + DATE_WORDS, body, flags=re.I)
    if not release_match or date_words(release_match[1]) != release:
        raise SourceGateError('wrong_html_release_date', 'Issue release date does not match the archive calendar')
    html_week = re.search(r'\bData for week ending\s+([^|]+)\|', body, flags=re.I)
    parsed_html_week, warning = None, ''
    if html_week and re.fullmatch(DATE_WORDS, html_week[1].strip()):
        parsed_html_week = date_words(html_week[1].strip())
        if parsed_html_week != week:
            raise SourceGateError('wrong_html_week_ending', f'Actual{parsed_html_week}; expected{week}')
    else:
        # The actual2019Jan9issue omits the day; PDF/index agreement remains mandatory.
        warning = 'HTML week-ending header missing/malformed; PDF and archive index agree'
    pdf_week = pdf_identity(highlights, expected_highlights, week)
    return dict(observed_issue_url=actual_issue, observed_highlights_url=expected_highlights,
                observed_html_week_ending=parsed_html_week, observed_pdf_week_ending=pdf_week,
                issue_header_warning=warning,
                pdf_metadata_title_warning=('Blank metadata title; internal official title/URL/page/week verified'
                                            if highlights.startswith(' (') else ''),
                identity_verified=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def index_records(lines):
    years, month = None, None
    records = []
    for raw in lines:
        number = int(re.match(r'^L(\d+):', raw).group(1))
        line = re.sub(r'^L\d+:\s*', '', raw)
        section = re.fullmatch(r'(20\d\d)\s*-\s*(20\d\d)', line)
        if section:
            years = [int(x) for x in section.groups()]
            month = None
            continue
        if years is None or '【' not in line:
            continue
        fields = [x.strip() for x in line.split('|')]
        if len(fields) < 5:
            raise ValueError(f'Incomplete archive row at line{number}')
        if fields[0] in MONTHS:
            month = MONTHS[fields[0]]
        if month is None:
            raise ValueError(f'Missing month context at line{number}')
        for column, year in enumerate(years):
            if not 2018 <= year <= 2022:
                continue
            entry = fields[1 + 2*column]
            match = re.fullmatch(r'【(\d+)†(\d+)】', entry)
            if not match:
                if entry.strip():
                    raise ValueError(f'Unparsed entry at line{number}: {entry!r}')
                continue
            link_id, day = [int(x) for x in match.groups()]
            release = pd.Timestamp(year=year, month=month, day=day)
            data = fields[2 + 2*column]
            if re.fullmatch(r'\d{1,2}/\d{1,2}', data):
                data_month, data_day = [int(x) for x in data.split('/')]
            elif re.fullmatch(r'\d{1,2}', data):
                data_month, data_day = month, int(data)
                if data_day > day:
                    data_month = 12 if month == 1 else month - 1
            else:
                raise ValueError(f'Ambiguous data-ending token at line{number}: {data!r}')
            data_year = year - int(data_month > month)
            ending = pd.Timestamp(year=data_year, month=data_month, day=data_day)
            if ending >= release or ending.dayofweek != 4:
                raise ValueError(f'Invalid release/week-ending pair: {release}/{ending}')
            records.append(dict(source_key=f'{release.date()}__{ending.date()}', release_date=release,
                                week_ending=ending, release_weekday=release.day_name(),
                                calendar_lag_days=(release-ending).days, archive_link_id=link_id,
                                source_index_line=number,
                                exact_release_clock_verified=False,
                                original_first_publication_bytes_verified=False))
    frame = pd.DataFrame(records).sort_values(['release_date', 'week_ending']).reset_index(drop=True)
    if frame.source_key.duplicated().any() or frame.week_ending.duplicated().any():
        raise ValueError('Conflicting/duplicate archive key or week-ending')
    return frame


def prose_change_details(text):
    """Normalize explicit weekly source quantities; retain their amounts and units."""
    text = clean_document(text)
    starts = {
        'crude_ex_spr_change_mb': r'U\.S\. commercial crude oil inventories\s*\(excluding[^)]*Strategic Petroleum Reserve\)',
        'gasoline_change_mb': r'Total motor gasoline inventories',
        'distillate_change_mb': r'Distillate fuel inventories',
    }
    subjects = {**starts, 'crude_ex_spr_change_mb': r'U\.S\. commercial crude oil inventories'}
    details = {}
    number = r'(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?|\.\d+)'
    for name, start in starts.items():
        if len(re.findall(subjects[name], text, flags=re.I)) != 1:
            raise ValueError(f'Missing/duplicate inventory subject: {name}')
        weekly = r'(?:from\s+(?:the\s+)?(?:previous|prior|last)\s+week|last\s+week)\b'
        pattern = (start + r'\s+(increased|decreased)\s+by\s+(' + number +
                   r')\s+((?:(?:million|thousand)\s+)?barrels)\s+(' + weekly + ')' +
                   r'(?=$|[.;]|\s*,?\s+(?:and|but)\s+are\b)')
        matches = list(re.finditer(pattern, text, flags=re.I))
        if len(matches) != 1:
            raise ValueError(f'Missing/ambiguous published inventory-change sentence: {name}')
        direction, reported, unit, scope = matches[0].groups()
        amount = float(reported.replace(',', ''))
        if not math.isfinite(amount):
            raise ValueError(f'Nonfinite published inventory change:{name}')
        unit = unit.lower()
        denominator = {'million barrels': 1., 'thousand barrels': 1000., 'barrels': 1000000.}[unit]
        scale = 1. / denominator
        value = amount / denominator * (1 if direction.lower() == 'increased' else -1)
        details[name] = dict(value_mb=value, reported_amount=reported, reported_unit=unit,
                             factor_to_million_barrels=scale, direction=direction.lower(),
                             weekly_scope=scope, matched_source_text=matches[0][0])
    return details


def prose_changes(text):
    """Fail closed: no stock-level subtraction or ambiguous unchanged-to-zero fill."""
    return {name: value['value_mb'] for name, value in prose_change_details(text).items()}


def sample_parity():
    """Check known parsed facts against actual saved, converted five-year sample responses."""
    directory = OUT / 'samples'
    checked = {}
    for release, (week, crude, gasoline, distillate) in SAMPLE_EXPECTED.items():
        record = json.loads((directory / f'{release}_record.json').read_text())
        response = directory / record['converted_web_response_file']
        if sha(response) != record['converted_web_response_sha256']:
            raise ValueError(f'Sample converted-response hash mismatch:{release}')
        source = json.loads(response.read_text())
        text = '\n'.join(block['text'] for block in source['content'] if block.get('type') == 'text')
        blocks = re.split(r'\n-{15,}\n', text)
        _, url = expected_urls(f'{release}__{week}', release)
        matches = [block.strip() for block in blocks
                   if block.strip().startswith(f'Weekly Petroleum Status Report ({url})\n')]
        if len(matches) != 1:
            raise ValueError(f'Sample needs one exact canonical PDF block:{release}')
        pdf_identity(matches[0], url, week)
        values = prose_changes(matches[0])
        expected = dict(zip(FIELDS, (crude, gasoline, distillate)))
        if values != expected:
            raise ValueError(f'Sample published changes mismatch:{release}: {values}/{expected}')
        checked[release] = dict(week_ending=week, **values)
    return checked


def component_ingestion(frame):
    """Only serial_sources may supply panel observations; old attempts never backfill it."""
    directory = OUT / 'serial_sources'
    audits, components = [], []
    expected_files = {row.source_key + '.json' for row in frame.itertuples()}
    for row in frame.itertuples():
        path = directory / (row.source_key + '.json')
        relative = str(path.relative_to(ROOT))
        audit = dict(source_key=row.source_key, release_date=iso_date(row.release_date),
                     week_ending=iso_date(row.week_ending), release_weekday=row.release_weekday,
                     calendar_lag_days=int(row.calendar_lag_days), source_filename=relative,
                     source_exists=path.exists(), converted_source_sha256='', identity_verified=False,
                     published_changes_parsed=False, retained_component_triple=False,
                     reason='missing_serial_source', detail='', issue_header_warning='', pdf_metadata_title_warning='',
                     actual_release_clock_verified=False, immutable_first_publication_verified=False)
        if not path.exists():
            audits.append(audit)
            continue
        audit['converted_source_sha256'] = sha(path)
        try:
            record = json.loads(path.read_text())
        except (ValueError, UnicodeError) as error:
            audit.update(reason='invalid_source_json', detail=str(error))
            audits.append(audit)
            continue
        if not isinstance(record, dict):
            audit.update(reason='invalid_source_record_type', detail='Serial source must be a JSON object')
            audits.append(audit)
            continue
        audit['recorded_acquisition_status'] = record.get('acquisition_status', '')
        try:
            audit.update(source_identity(record, row))
        except SourceGateError as error:
            audit.update(reason=error.reason, detail=str(error))
            audits.append(audit)
            continue
        try:
            quantity_details = prose_change_details(record['highlights_document_text'])
            values = {name: value['value_mb'] for name, value in quantity_details.items()}
        except ValueError as error:
            audit.update(reason='published_weekly_change_parse_failure', detail=str(error))
            audits.append(audit)
            continue
        audit.update(published_changes_parsed=True, retained_component_triple=True,
                     reason='verified_archived_component_triple', **values)
        components.append(dict(source_key=row.source_key, release_date=iso_date(row.release_date),
                               week_ending=iso_date(row.week_ending), **values,
                               source_filename=relative, converted_source_sha256=audit['converted_source_sha256'],
                               canonical_issue_url=audit['observed_issue_url'],
                               canonical_highlights_url=audit['observed_highlights_url'],
                               captured_utc=record.get('captured_utc', record.get('captureUTC', '')),
                               source_quantity_trace=json.dumps(quantity_details, sort_keys=True),
                               raw_pdf_downloaded=bool(record.get('raw_pdf_downloaded', False)),
                               actual_release_clock_verified=False,
                               immutable_first_publication_verified=False))
        audits.append(audit)
    audit_frame = pd.DataFrame(audits)
    columns = ['source_key', 'release_date', 'week_ending'] + FIELDS + [
        'source_filename', 'converted_source_sha256', 'canonical_issue_url', 'canonical_highlights_url',
        'captured_utc', 'source_quantity_trace', 'raw_pdf_downloaded', 'actual_release_clock_verified', 'immutable_first_publication_verified']
    component_frame = pd.DataFrame(components, columns=columns)
    excluded = audit_frame[~audit_frame.retained_component_triple]
    available = audit_frame[audit_frame.source_exists]
    coverage = dict(stage='source_intake_only', strategy_return_trials=0,
        expected_editions=len(frame), serial_source_files_present=len(available),
        identities_verified=int(audit_frame.identity_verified.sum()),
        complete_triples=len(component_frame), all_expected_identities_verified=bool(audit_frame.identity_verified.all()),
        complete_component_panel=bool(audit_frame.retained_component_triple.all()),
        missing_source_keys=audit_frame.loc[~audit_frame.source_exists, 'source_key'].tolist(),
        excluded_source_keys=excluded.source_key.tolist(),
        exclusion_reasons={str(k): int(v) for k, v in excluded.reason.value_counts().items()},
        retained_by_release_year={str(k): int(v) for k, v in component_frame.groupby(component_frame.release_date.str[:4]).size().items()},
        html_header_warning_keys=audit_frame.loc[audit_frame.issue_header_warning.ne(''), 'source_key'].tolist(),
        pdf_metadata_title_warning_keys=audit_frame.loc[audit_frame.pdf_metadata_title_warning.ne(''), 'source_key'].tolist(),
        extra_serial_source_filenames=sorted(path.name for path in directory.glob('*.json') if path.name not in expected_files),
        ignored_diagnostic_directories=['acquired', 'verified_sources'],
        no_backfill_from_samples_or_diagnostic_attempts=True,
        hash_basis='SHA256 of each saved serial-source JSON file, containing exact converted web text; NOT raw PDF bytes.',
        immutable_original_vintages_verified=False, actual_release_clocks_verified=False,
        economic_preregistration_authorized=False,
        known_clock_revision_limits=[
            'Normal Highlights publication policy10:30Eastern is not historical client receipt evidence.',
            'Holiday/disruption clocks and multiple-edition dates require independent handling before strategy tests.',
            'Archived dated files may contain later corrections; original first-publication bytes are not established.',
            '2018June27updated production statistic does not itself prove an inventory-field correction.',
            '2026August26summary-text sign correction does not specifically identify Highlights PDF; it is source-review evidence, not a design observation.'])
    if len(audit_frame) != len(frame) or audit_frame.source_key.duplicated().any():
        raise ValueError('Every calendar edition must have exactly one component audit row')
    return component_frame, audit_frame, coverage


def engineering():
    text = ('L14@P0: U.S. commercial crude oil inventories (excluding those in the Strategic Petroleum Reserve) '
            'decreased by 7.4 million barrels from the previous week.\nL18@P0: Total motor gasoline inventories increased by 4.8 million '
            'barrels last week.\nL21@P0: Distillate fuel inventories increased by 8.9 million barrels last week.')
    assert prose_changes(text) == dict(crude_ex_spr_change_mb=-7.4, gasoline_change_mb=4.8, distillate_change_mb=8.9)
    assert prose_changes(text.replace('7.4 million', '.8 million'))['crude_ex_spr_change_mb'] == -.8
    assert prose_changes(text.replace('7.4 million', '400 thousand'))['crude_ex_spr_change_mb'] == -.4
    assert prose_changes(text.replace('7.4 million', '249,000'))['crude_ex_spr_change_mb'] == -.249
    for broken in (text.replace('million barrels', 'billion barrels'), text + text,
                   text.replace('7.4 million', '24,90'),
                   text.replace('million barrels', 'barrels per day'),
                   text.replace('decreased by 7.4', 'were unchanged'),
                   text.replace('from the previous week', 'last week from a year ago'),
                   text.replace('from the previous week', 'from the previous week per day'),
                   text + ' Total motor gasoline inventories were virtually unchanged last week.',
                   text + ' Total motor gasoline inventories decreased by an unspecified amount last week.',
                   text.replace('from the previous week', 'from the previous year').replace('last week', 'last year'),
                   text.replace(' from the previous week', '').replace(' last week', '')):
        try:
            prose_changes(broken)
        except ValueError:
            pass
        else:
            raise AssertionError('Ambiguous/unsupported prose must fail closed')
    lines = ['L176: 2022 - 2023', 'L180: January | 【177†5】 | 12/31 | 【178†5】 | 12/30',
             'L201: June | 【219†2】 | 5/27 | 【220†1】 | 5/26',
             'L204: | 【225†29】 | 17 | 【226†22】 | 16',
             'L205: | 【227†29】 | 24 | 【228†28】 | 23']
    test = index_records(lines)
    assert len(test) == 4 and test.release_date.duplicated(keep=False).sum() == 2
    assert test.iloc[0].week_ending == pd.Timestamp('2021-12-31')
    row = SimpleNamespace(source_key='2018-01-10__2018-01-05', release_date='2018-01-10', week_ending='2018-01-05')
    issue_url, pdf_url = expected_urls(row.source_key, row.release_date)
    issue = (f'Weekly Petroleum Status Report Archives ({issue_url})\n'
             'L0: Data for week ending January 5, 2018 | Release Date: January 10, 2018 | full report')
    pdf = (f'Weekly Petroleum Status Report ({pdf_url})\n'
           'Content type: application/pdf; Number of pages: 1; Source: synthetic identity check\n'
           'L0@P0: During the week ending January 5, 2018. Production 5,403.\n' + text)
    record = dict(source_key=row.source_key, release_date=row.release_date, week_ending=row.week_ending,
                  canonical_issue_url=issue_url, canonical_highlights_url=pdf_url,
                  issue_document_text=issue, highlights_document_text=pdf, error=None)
    assert source_identity(record, row)['identity_verified']
    for replacement in (
            dict(source_key='2018-01-18__2018-01-12'),
            dict(highlights_document_text=pdf.replace('/pdf/highlights.pdf', '/pdf/table1.pdf')),
            dict(highlights_document_text=pdf.replace('Number of pages: 1', 'Number of pages: 2')),
            dict(highlights_document_text=pdf.replace('week ending January 5, 2018', 'week ending January 12, 2018')),
            dict(issue_document_text=issue.replace('Release Date: January 10', 'Release Date: January 18'))):
        try:
            source_identity({**record, **replacement}, row)
        except SourceGateError:
            pass
        else:
            raise AssertionError('Edition/date/URL/page mismatches must fail before numeric parsing')
    malformed = {**record, 'issue_document_text': issue.replace('week ending January 5, 2018', 'week ending January, 2018')}
    assert source_identity(malformed, row)['issue_header_warning']
    blank_title = (f' ({pdf_url})\nContent type: application/pdf; Number of pages: 1;\n'
                   'L0@P0: v Weekly Petroleum Status Report/Energy Information Administration\n'
                   'L1@P0: During the week ending January 5, 2018.\n' + text)
    assert source_identity({**record, 'highlights_document_text': blank_title}, row)['pdf_metadata_title_warning']
    try:
        source_identity({**record, 'highlights_document_text': blank_title.replace(
            'Weekly Petroleum Status Report/Energy Information Administration', 'Unrelated source')}, row)
    except SourceGateError:
        pass
    else:
        raise AssertionError('Blank metadata title requires independently matching internal official title')
    assert '2022_06_17_data' in expected_urls('2022-06-29__2022-06-17', '2022-06-29')[0]
    return dict(passed=True, checks=['published signed weekly changes and exact units',
        'leading decimals/thousands/comma-barrels normalized with literal quantity trace',
        'annual/missing scope and missing/unchanged/duplicate prose fail closed',
        'weekly scope termination and contradictory nonnumeric duplicate subjects fail closed',
        'release versus data-ending year rollover', 'two same-day editions remain distinct',
        'calendar IDs/canonical URLs/one-page PDF/first-week-ending identity before numbers',
        'malformed HTML week header flagged; PDF/index agreement still required',
        'blank PDF metadata title requires matching internal title/URL/page/week',
        'ordinary5,403 data is not an HTTP403 error',
        'five actual saved sample PDFs match canonical identity/week-ending/numeric changes',
        'no price or strategy-return inputs'], five_sample_parity=sample_parity())


def offline_review():
    """Reconcile this dated offline repair against its preserved156-row baseline."""
    directory = OUT / 'offline_review_20261026'
    manifest = json.loads((directory / 'baseline_manifest.json').read_text())
    for name, expected_hash in manifest['files'].items():
        if sha(directory / ('baseline_' + name)) != expected_hash:
            raise ValueError(f'Preserved baseline hash mismatch:{name}')
    baseline = pd.read_csv(directory / 'baseline_design_components.csv')
    current = pd.read_csv(OUT / 'design_components.csv')
    before_audit = pd.read_csv(directory / 'baseline_design_component_audit.csv').fillna('')
    after_audit = pd.read_csv(OUT / 'design_component_audit.csv').fillna('')
    fields = ['source_key', 'source_exists', 'converted_source_sha256']
    pd.testing.assert_frame_equal(before_audit[fields], after_audit[fields], check_exact=True)
    common = ['source_key'] + FIELDS + ['converted_source_sha256']
    old = baseline[common].sort_values('source_key').reset_index(drop=True)
    now = current[current.source_key.isin(baseline.source_key)][common].sort_values('source_key').reset_index(drop=True)
    pd.testing.assert_frame_equal(old, now, check_exact=True)
    expected = json.loads((directory / 'expected_recoveries.json').read_text())['expected']
    added = current[~current.source_key.isin(baseline.source_key)]
    if set(added.source_key) != set(expected):
        raise ValueError('Offline recovery must match every independently reviewed source, with no other admissions')
    qualitative_keys = {'2018-06-27__2018-06-22', '2018-12-28__2018-12-21',
                        '2019-01-04__2018-12-28', '2021-02-03__2021-01-29', '2021-02-24__2021-02-19'}
    qualitative = after_audit[after_audit.source_key.isin(qualitative_keys)]
    if (len(qualitative) != 5 or qualitative.retained_component_triple.any() or
            not qualitative.reason.eq('published_weekly_change_parse_failure').all()):
        raise ValueError('All five qualitative unchanged reports must retain their explicit parse exclusion')
    records = []
    for row in added.itertuples():
        target = expected[row.source_key]
        actual = [getattr(row, field) for field in FIELDS]
        if actual != target['values_mb'] or row.converted_source_sha256 != target['unchanged_raw_source_sha256']:
            raise ValueError(f'Independent offline source/value parity failed:{row.source_key}')
        records.append(dict(source_key=row.source_key, values_mb=actual,
                            unchanged_raw_source_sha256=row.converted_source_sha256,
                            quantity_trace=json.loads(row.source_quantity_trace)))
    result = dict(baseline_commit=manifest['baseline_commit'], preserved_baseline_hashes_verified=True,
                  baseline_triples=len(baseline), current_triples=len(current), recovered_triples=len(added),
                  every_original_value_unchanged=True, all_captured_source_hashes_and_presence_unchanged=True,
                  recovered_source_keys=sorted(expected), ambiguous_unchanged_still_excluded=True,
                  network_requests=0, futures_price_files_opened=False, new_strategy_return_trials=0,
                  details=records)
    (directory / 'recovery_audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'details'}, indent=2))


def run():
    snapshot = OUT / 'archive_index_webtext.json'
    saved = json.loads(snapshot.read_text())
    frame = index_records(saved['lines'])
    expected = pd.date_range(frame.week_ending.min(), frame.week_ending.max(), freq='W-FRI')
    missing_weeks = sorted(set(expected) - set(frame.week_ending))
    if len(frame) != 261 or missing_weeks:
        raise ValueError('The committed2018–22archive snapshot must reproduce261editions and a complete weekly sequence')
    checks = engineering()
    components, component_audit, coverage = component_ingestion(frame)
    coverage['five_sample_parity'] = checks['five_sample_parity']
    frame.to_csv(OUT / 'design_archive_calendar.csv', index=False)
    components.to_csv(OUT / 'design_components.csv', index=False, float_format='%.12g')
    component_audit.to_csv(OUT / 'design_component_audit.csv', index=False, float_format='%.12g')
    (OUT / 'coverage.json').write_text(json.dumps(coverage, indent=2) + '\n')
    summary = dict(stage='source_intake_only', strategy_return_trials=0, source_snapshot=snapshot.name,
                   source_snapshot_sha256=sha(snapshot), hash_basis=saved['representation'],
                   editions=len(frame), distinct_release_dates=int(frame.release_date.nunique()),
                   by_release_year={str(k): int(v) for k, v in frame.groupby(frame.release_date.dt.year).size().items()},
                   release_weekdays={str(k): int(v) for k, v in frame.release_weekday.value_counts().items()},
                   missing_week_ending_dates=[str(d.date()) for d in missing_weeks],
                   first_week_ending=str(frame.week_ending.min().date()),
                   last_week_ending=str(frame.week_ending.max().date()),
                   multiple_edition_release_dates=[str(d.date()) for d in frame.loc[frame.release_date.duplicated(keep=False), 'release_date'].drop_duplicates()],
                   exceptional_lags=frame[frame.calendar_lag_days.gt(7)][['source_key', 'calendar_lag_days']].to_dict('records'),
                   no_actual_release_clock_inferred_from_calendar=True,
                   full_component_panel_collected=coverage['complete_component_panel'], immutable_original_vintages_verified=False,
                   economic_preregistration_authorized=False)
    (OUT / 'calendar_audit.json').write_text(json.dumps(summary, indent=2) + '\n')
    (OUT / 'parser_engineering_checks.json').write_text(json.dumps(checks, indent=2) + '\n')
    print(json.dumps(dict(calendar=summary, components=coverage), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-check', action='store_true')
    parser.add_argument('--offline-review', action='store_true')
    args = parser.parse_args()
    if args.self_check:
        print(engineering())
    elif args.offline_review:
        offline_review()
    else:
        run()
