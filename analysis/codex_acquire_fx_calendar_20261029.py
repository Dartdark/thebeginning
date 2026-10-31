"""Build sourced release-calendar facts, with unknown historical knowledge times empty.

Offline construction from acquired government calendar/header evidence. No prices,
returns, event selection for a strategy, or source-paper universe are inferred.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'agents/codex/inputs/scout_acquisition_20261029/fx_calendar'
MONTHS = ('January February March April May June July August September October November December').split()
DATE_PATTERN = re.compile(r'\b(' + '|'.join(MONTHS) + r')\s+([1-9]\d?)(?!\d)')
FIELDS = ('event_id agency release_family release_title release_date local_time timezone event_time_utc '
          'event_time_kind clock_evidence source_url source_locator source_retrieved_on '
          'source_printed_issue_date original_schedule_publication_at original_schedule_available_at '
          'actual_feed_receipt_at actual_release_at_verified historical_pre_event_schedule_verified '
          'calendar_status notes').split()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row_base(agency, family, title, date, clock, source_url, locator, kind, evidence, status, notes=''):
    zone = ZoneInfo('America/New_York')
    stamp = datetime.fromisoformat(date + 'T' + clock).replace(tzinfo=zone)
    key = '|'.join((agency, family, title, date, clock, source_url, kind))
    return dict(event_id=hashlib.sha256(key.encode()).hexdigest()[:20], agency=agency,
                release_family=family, release_title=title, release_date=date,
                local_time=clock, timezone='America/New_York', event_time_utc=stamp.astimezone(ZoneInfo('UTC')).isoformat(),
                event_time_kind=kind, clock_evidence=evidence, source_url=source_url, source_locator=locator,
                source_retrieved_on='2026-10-29', source_printed_issue_date='',
                original_schedule_publication_at='', original_schedule_available_at='', actual_feed_receipt_at='',
                actual_release_at_verified='false', historical_pre_event_schedule_verified='false',
                calendar_status=status, notes=notes)


def bls_rows():
    facts = json.loads((BASE / 'bls_annual_schedule_facts.json').read_text(encoding='utf-8'))
    output = []
    names = [('Consumer Price Index for', 'CPI'), ('Employment Situation for', 'EMPLOYMENT_SITUATION'),
             ('Producer Price Index for', 'PPI'), ('Job Openings and Labor Turnover Survey for', 'JOLTS'),
             ('U.S. Import and Export Price Indexes for', 'IMPORT_EXPORT_PRICES'),
             ('Employment Cost Index for', 'EMPLOYMENT_COST_INDEX'), ('Productivity and Costs ', 'PRODUCTIVITY_COSTS')]
    for item in facts['rows']:
        date = datetime.strptime(item['date_text'], '%A, %B %d, %Y')
        assert date.strftime('%A') == item['date_text'].split(',')[0]
        assert date.year == item['year']
        clock = datetime.strptime(item['time_text'], '%I:%M %p').strftime('%H:%M')
        family = next((family for prefix, family in names if item['release_title'].startswith(prefix)), 'BLS_OTHER_TIMED')
        output.append(row_base('BLS', family, item['release_title'], date.date().isoformat(), clock,
                               item['source_url'], 'reader line ' + str(item['source_line']),
                               'scheduled_as_displayed_in_current_official_archive',
                               'Official annual schedule prints time; page explicitly says Eastern Time.',
                               'official_schedule_fact_not_original_vintage',
                               'Original announcement/receipt and actual release confirmation not obtained.'))
    return output


def bea_rows():
    acquired = json.loads((BASE / 'bea_calendar_source_evidence.json').read_text(encoding='utf-8'))
    output = {}
    for source in acquired['sources']:
        lines = {int(k): v for k, v in source['lines'].items()}
        year = source['year']
        printed = next((v.split('|')[-1].strip() for v in lines.values() if v.startswith('Volume ')), '')
        for number, text in sorted(lines.items()):
            text = re.sub(r'\^\{([^}]+)\}', r'\1', text)
            if text.startswith('Personal Income and Outlays,'):
                family = 'PERSONAL_INCOME_OUTLAYS'
            elif re.match(r'^(?:Initial )?Gross Domestic Product(?:,| \()', text):
                family = 'GDP_NATIONAL_ESTIMATE'
            else:
                continue
            pieces = []
            match = None
            end_line = number
            for end_line in range(number, number + 6):
                piece = re.sub(r'\^\{([^}]+)\}', r'\1', lines.get(end_line, '')).strip()
                piece = re.sub(r'Page \d of \d.*$', '', piece).strip()
                match = DATE_PATTERN.search(piece)
                if match:
                    pieces.append(piece[:match.start()].rstrip(' |'))
                    break
                pieces.append(piece)
            if not match:
                raise ValueError('No explicit date for BEA target row: ' + str((year, number, pieces)))
            title = re.sub(r'\s+', ' ', ' '.join(pieces)).strip(' |')
            date = datetime(year, MONTHS.index(match.group(1)) + 1, int(match.group(2))).date().isoformat()
            clock = '08:30'
            evidence = 'Official source general08:30 Eastern policy; explicit exceptions override.'
            following = lines.get(end_line + 1, '').strip()
            inline = lines[end_line][match.end():].strip()
            time_match = re.search(r'(\d{1,2})(?::(\d\d))?\s*(a\.?m\.?|p\.?m\.?)', inline, re.I)
            next_match = re.fullmatch(r'(\d{1,2})(?::(\d\d))?\s*(a\.?m\.?|p\.?m\.?)', following, re.I)
            explicit = time_match or next_match
            if explicit:
                h, minute = int(explicit.group(1)), int(explicit.group(2) or 0)
                if explicit.group(3).lower().startswith('p') and h < 12:
                    h += 12
                if explicit.group(3).lower().startswith('a') and h == 12:
                    h = 0
                clock = f'{h:02d}:{minute:02d}'
                evidence = 'Official schedule explicit row time, with named-zone agency context.'
            if year == 2019 and family == 'PERSONAL_INCOME_OUTLAYS' and date in ('2019-11-27', '2019-12-20'):
                clock = '10:00'
                evidence = 'Official2019 schedule footnote3 explicitly10:00AM EST.'
            notes = 'Current copy of a dated schedule; actual release and original announcement/receipt not certified.'
            if year == 2019:
                notes += ' Page explicitly incorporates shutdown-rescheduled dates; printedDecember2018 issue date does not establish when edits were known.'
                if date == '2019-02-28' and family == 'GDP_NATIONAL_ESTIMATE':
                    notes += ' Initial estimate replaces originally scheduled2019-01-30advance and second estimate; no extra event is imputed.'
                if date == '2019-03-01' and family == 'PERSONAL_INCOME_OUTLAYS':
                    notes += ' December2018PIO was originally scheduled2019-01-31; this combined event includes January2019income but not Januaryoutlays.'
            if year == 2018:
                evidence += '2018 PDF does not print zone; America/New_York context is supported by2018 primary PCE headers, not each individual header.'
            row = row_base('BEA', family, title, date, clock, source['url'], f'reader lines{number}–{end_line}',
                           'dated_official_schedule_current_copy', evidence,
                           'official_schedule_fact_not_original_vintage', notes)
            row['source_printed_issue_date'] = printed
            output[(family, date, title, source['url'])] = row
    return list(output.values())


def fomc_rows():
    source = json.loads((BASE / 'fomc_facts.json').read_text(encoding='utf-8'))
    output = []
    for item in source['rows']:
        row = row_base('FED', item['release_family'], item['release_title'], item['date'], item['local_time'],
                       item['source_url'], item['source_reader_ref'], item['event_time_kind'], item['source_clock_text'],
                       item['event_status'], item['notes'] + ' ' + item['schedule_class'])
        assert datetime.fromisoformat(row['event_time_utc']).astimezone(ZoneInfo(item['timezone'])).tzname() == item['printed_timezone']
        output.append(row)
    return output


def snapshot_secondary(repo):
    """Extract unprotected date facts only; never run/copy external source code."""
    import subprocess
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
    names = ['us_cpi', 'us_nfp', 'us_ppi', 'us_gdp', 'us_gdp_later', 'us_claims', 'us_retail', 'fomc']
    files = []
    for name in names:
        relative = 'midas/data/calendar/' + name + '.txt'
        path = repo / relative
        dates, excluded = [], []
        for line in path.read_text(encoding='utf-8').splitlines():
            if re.fullmatch(r'20\d\d-\d\d-\d\d', line) and '2018-01-01' <= line <= '2022-12-31':
                dates.append(line)
            if line.startswith('#'):
                excluded.extend(d for d in re.findall(r'20\d\d-\d\d-\d\d', line) if '2018-01-01' <= d <= '2022-12-31')
        files.append({'path': relative, 'sha256': digest(path), 'series': name, 'dates': dates,
                      'commented_date_mentions': sorted(set(excluded)),
                      'curation_note': 'Secondary inventory excludes selected events; commented dates are context, not automatically valid exclusions for our study.'})
    return {'repository': 'https://github.com/chris-cheshire/project-midas-mk7', 'commit': commit,
            'retrieved_on': '2026-10-29', 'license_note': 'No repository license found. Only factual dates extracted with attribution; no code or expressive notes copied.',
            'clock_note': 'Secondary headers report08:30NewYork forUSseries. FOMC times are leftunknown here. This is not primary verification of each clock.',
            'files': files}


def secondary_rows():
    facts = json.loads((BASE / 'midas_calendar_date_facts.json').read_text(encoding='utf-8'))
    families = {'us_cpi': 'CPI', 'us_nfp': 'EMPLOYMENT_SITUATION', 'us_ppi': 'PPI', 'us_gdp': 'GDP_ADVANCE',
                'us_gdp_later': 'GDP_LATER_ESTIMATE', 'us_claims': 'INITIAL_CLAIMS', 'us_retail': 'RETAIL_SALES', 'fomc': 'FOMC_SCHEDULED_SUBSET'}
    output = []
    for item in facts['files']:
        url = facts['repository'] + '/blob/' + facts['commit'] + '/' + item['path']
        for date in item['dates']:
            row = {field: '' for field in FIELDS}
            family = families[item['series']]
            row.update(event_id=hashlib.sha256((family + date + url).encode()).hexdigest()[:20],
                       agency='secondary_inventory', release_family=family, release_title=family,
                       release_date=date, timezone='America/New_York', event_time_kind='secondary_curated_date_inventory',
                       source_url=url, source_locator=item['path'], source_retrieved_on='2026-10-29',
                       actual_release_at_verified='false', historical_pre_event_schedule_verified='false',
                       calendar_status='secondary_fact_requires_primary_check', notes=item['curation_note'])
            if item['series'] != 'fomc':
                row['local_time'] = '08:30'
                row['clock_evidence'] = 'Secondary file header reports08:30NY; not individually primary-verified.'
            output.append(row)
    return output


def build():
    primary = bls_rows() + bea_rows() + fomc_rows()
    primary.sort(key=lambda row: (row['release_date'], row['local_time'], row['agency'], row['release_title']))
    secondary = secondary_rows()
    for name, rows in [('primary_release_calendar_2018_2022.csv', primary), ('secondary_calendar_inventory_2018_2022.csv', secondary)]:
        with (BASE / name).open('w', encoding='utf-8', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator='\n')
            writer.writeheader(); writer.writerows(rows)
    assert len({r['event_id'] for r in primary}) == len(primary)
    for year in range(2018, 2023):
        for family in ['CPI', 'EMPLOYMENT_SITUATION']:
            selected = [r for r in primary if r['agency'] == 'BLS' and r['release_family'] == family and r['release_date'].startswith(str(year))]
            assert len(selected) == 12, (year, family, len(selected))
    assert all(not row['original_schedule_available_at'] and not row['actual_feed_receipt_at'] for row in primary + secondary)
    corroboration = []
    for family in ['CPI', 'EMPLOYMENT_SITUATION', 'PPI']:
        direct = {r['release_date'] for r in primary if r['agency'] == 'BLS' and r['release_family'] == family}
        other = {r['release_date'] for r in secondary if r['release_family'] == family}
        corroboration.append({'family': family, 'official_schedule_dates': len(direct), 'secondary_dates': len(other),
                              'common': len(direct & other), 'official_only': sorted(direct - other), 'secondary_only': sorted(other - direct)})
    manifest = {'schema_version': 1, 'acquired_on': '2026-10-29', 'primary_rows': len(primary), 'secondary_rows': len(secondary),
                'primary_counts_by_agency': dict(Counter(r['agency'] for r in primary)),
                'primary_counts_by_family': dict(Counter(r['release_family'] for r in primary)),
                'secondary_counts_by_family': dict(Counter(r['release_family'] for r in secondary)),
                'primary_by_year_agency': {str(year): dict(Counter(r['agency'] for r in primary if r['release_date'].startswith(str(year)))) for year in range(2018, 2023)},
                'BEA_nonstandard_10am_events': [{k: r[k] for k in ['release_date', 'release_family', 'local_time', 'source_url']} for r in primary if r['agency']=='BEA' and r['local_time']=='10:00'],
                'secondary_crosscheck': corroboration,
                'hashes': {p.name: digest(p) for p in BASE.glob('*') if p.is_file()},
                'script_sha256': digest(Path(__file__)), 'return_trials': 0,
                'ready_for_exact_paper_test': False,
                'limits': ['Paper5207418 full specification/event universe remains unverified.',
                           'Schedules retrieved now are not original historical vintages or actual feed receipt logs.',
                           'BEA2019page incorporates shutdown changes; source issue date is not edit availability.',
                           'Secondary curated dates remain separate; exclusions are not inherited as our event-selection rule.',
                           'FOMC rows are42 publishedstatementdocuments, not42 scheduledmeetings.',
                           'ADP/ISMmanufacturing/ConferenceBoard source calendars not acquired; no series assumed a paper requirement.',
                           'The separate claims-calendar acquisition belongs to the parent task; secondary claims here are not primary-verified history.',
                           'No prices, missing returns, trading rule, PnL or account inference.']}
    out = ROOT / 'analysis/outputs/codex_fx_calendar_acquisition_20261029.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: manifest[k] for k in ['primary_rows','secondary_rows','primary_counts_by_agency','primary_counts_by_family','BEA_nonstandard_10am_events','secondary_crosscheck','return_trials']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot-secondary-from', type=Path)
    args = parser.parse_args()
    if args.snapshot_secondary_from:
        (BASE / 'midas_calendar_date_facts.json').write_text(json.dumps(snapshot_secondary(args.snapshot_secondary_from), indent=2) + '\n', encoding='utf-8')
    build()
