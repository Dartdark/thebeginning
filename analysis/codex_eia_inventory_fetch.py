"""Fetch missing public EIA source documents only after the executor allows the host.

No price files, strategy signals or return tests. No policy/proxy/credential changes.
Current PDF bytes are preserved; they are not claimed to be first-publication vintages.
"""
import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'analysis'))
from codex_eia_inventory_input_gate import expected_urls

OUT = ROOT / 'analysis/outputs/codex_eia_inventory_input_gate'
HOST = 'www.eia.gov'


def readiness():
    policy = json.loads(Path('/etc/codex/network-policy.json').read_text())
    network = policy.get('http_network_policy', {})
    allowed = network.get('type') == 'unrestricted' or HOST in [r.get('host') for r in network.get('egress_rules', [])]
    return dict(host=HOST, host_allowed=allowed, policy_mode=network.get('type'),
                pdftotext_available=shutil.which('pdftotext') is not None,
                network_requests_made=0, strategy_return_trials=0)


class HighlightsLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href', '')
            if href.split('?', 1)[0].endswith('/highlights.pdf'):
                self.links.append(href)


def validate_archive_url(url):
    parsed = urlparse(url)
    if (parsed.scheme != 'https' or parsed.hostname != HOST or parsed.port not in (None, 443) or
            parsed.username is not None or parsed.password is not None or
            not parsed.path.startswith('/petroleum/supply/weekly/archive/')):
        raise ValueError('Only approved official HTTPS archive URLs may be fetched')


class SameArchiveRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        validate_archive_url(new_url)  # Reject BEFORE urllib sends a redirected request.
        return super().redirect_request(request, response, code, message, headers, new_url)


def fetch(url):
    validate_archive_url(url)
    request = Request(url, headers={'User-Agent': 'Historical research source audit (public EIA archive)'})
    # urllib preserves the runtime HTTPS proxy and TLS verification defaults.
    with build_opener(SameArchiveRedirect()).open(request, timeout=30) as response:
        validate_archive_url(response.url)
        data = response.read(4 * 1024 * 1024 + 1)
        if len(data) > 4 * 1024 * 1024:
            raise ValueError('Unexpectedly large source document')
        return data, response.url


def main(check_only, maximum):
    state = readiness()
    if check_only or not state['host_allowed'] or not state['pdftotext_available']:
        print(json.dumps(state, indent=2))
        return 0 if state['host_allowed'] and state['pdftotext_available'] else 2
    if maximum < 1 or maximum > 20:
        raise ValueError('--max-reports must be1..20; source collection stays bounded')
    calendar = pd.read_csv(OUT / 'design_archive_calendar.csv', dtype=str)
    audit = pd.read_csv(OUT / 'design_component_audit.csv', dtype={'source_key': str})
    pending = set(audit.loc[~audit.retained_component_triple, 'source_key'])
    rows = calendar[calendar.source_key.isin(pending)].iloc[:maximum]
    for row in rows.itertuples():
        directory = OUT / 'native_sources' / row.source_key
        if directory.exists():
            raise ValueError(f'Existing source snapshot preserved: {directory}; audit it before another acquisition')
        directory.mkdir(parents=True)
        issue_url, expected_pdf = expected_urls(row.source_key, row.release_date)
        result = dict(source_key=row.source_key, release_date=row.release_date, week_ending=row.week_ending,
                      capture_utc=datetime.now(timezone.utc).isoformat(), raw_pdf_downloaded=False,
                      actual_historical_receipt_verified=False, immutable_first_vintage_verified=False,
                      new_strategy_return_trials=0)
        try:
            html, actual_issue = fetch(issue_url)
            (directory / 'issue.html').write_bytes(html)
            parser = HighlightsLinks()
            parser.feed(html.decode('utf-8', errors='strict'))
            links = {urljoin(actual_issue, link) for link in parser.links}
            if links != {expected_pdf}:
                raise ValueError(f'Actual Highlights links differ from expected same-issue archive URL: {sorted(links)}')
            pdf, actual_pdf = fetch(next(iter(links)))
            if not pdf.startswith(b'%PDF-'):
                raise ValueError('Source did not return PDF bytes')
            pdf_path = directory / 'highlights.pdf'
            pdf_path.write_bytes(pdf)
            text = subprocess.check_output(['pdftotext', '-layout', str(pdf_path), '-'], text=True)
            (directory / 'highlights.txt').write_text(text)
            result.update(status='native_source_captured_REQUIRES_IDENTITY_AND_PARITY_AUDIT',
                          canonical_issue_url=actual_issue, canonical_highlights_url=actual_pdf,
                          raw_pdf_downloaded=True, current_pdf_sha256=hashlib.sha256(pdf).hexdigest(),
                          issue_html_sha256=hashlib.sha256(html).hexdigest(),
                          extracted_text_sha256=hashlib.sha256(text.encode()).hexdigest(),
                          admitted_as_strategy_input=False)
        except HTTPError as error:
            result.update(status='HTTP_source_failure', http_status=error.code, error=str(error))
            (directory / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
            if error.code in (401, 403, 429):
                print(json.dumps(result))
                return 2  # No retry, changed proxy, alternate route or policy bypass.
        except (URLError, ValueError, UnicodeError, subprocess.CalledProcessError) as error:
            result.update(status='source_or_extraction_failure', error=str(error))
        (directory / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({k: result.get(k) for k in ('source_key', 'status', 'error')}), flush=True)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-access', action='store_true')
    parser.add_argument('--max-reports', type=int, default=10)
    args = parser.parse_args()
    raise SystemExit(main(args.check_access, args.max_reports))
