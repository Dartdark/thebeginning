"""Convert temporary connected-reader observations to metadata-only receipts.

Usage: python analysis/codex_scout_access_receipts_20261109.py TEMP_JSON
Reader bodies are not saved in the committed package. Hashes identify tool-result
JSON (canonical UTF8), not original PDF bytes or historical source vintages.
"""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'agents/codex/inputs/scout_20261109'


def convert(source):
    calls = json.loads(Path(source).read_text())
    output, queries = [], []
    for i, call in enumerate(calls, 1):
        result = call['result']
        canonical = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
        parts = result.get('content', []) if isinstance(result, dict) else []
        texts = [p.get('text', '') for p in parts if isinstance(p, dict)]
        metadata = []
        for text in texts:
            for section in text.split('\n--------------------------------------------------------------------------------\n'):
                lines = section.splitlines()
                if lines:
                    # Header only: title, URL/ref, access status. Never retain article lines/body.
                    head = lines[:1]
                    statuses = [s.strip() for s in lines if s.startswith(('URL ', 'Failed to fetch '))]
                    requests = re.findall(r'Source: ([^\n]+)', section)
                    refs = re.findall(r'【(turn[^】]+)】', section[:500])
                    metadata.append(dict(header=head, reader_refs=refs, status=statuses,
                                         source_requests=requests))
        row = dict(sequence=i, kind=call['kind'], batch=call.get('batch'),
                   queries=call.get('queries', []), request=call.get('request'),
                   requested_urls=call.get('urls'), receipt_type='access_metadata_only',
                   reader_result_sha256=hashlib.sha256(canonical).hexdigest(),
                   reader_hash_format='canonical JSON sort_keys=True separators comma/colon ensure_ascii=False UTF8',
                   body_retained=False, source_bytes_acquired=False, metadata=metadata)
        queries.extend(row['queries'])
        output.append(row)
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / 'discovery_receipts.json').write_text(json.dumps(dict(
        scope='Actual connected-reader call sequence. Titles/URLs/access headers only; full-paper bytes not acquired. Present-day retrieval is not historical availability.',
        calls=output), indent=2) + '\n')
    (DEST / 'queries.json').write_text(json.dumps(dict(
        queries=queries, query_count=len(queries), unique_query_count=len(set(queries)),
        search_batches=sum(c['kind'] == 'search' for c in output),
        access_method='Connected public indexed search; shell policy excludes Crossref/publisher hosts. No Crossref API request or exhaustive-index claim.'), indent=2) + '\n')
    (DEST / 'access.json').write_text(json.dumps(dict(
        calls=len(calls), receipt_path='agents/codex/inputs/scout_20261109/discovery_receipts.json',
        source_bytes_acquired=False, full_reviews=0, return_tests_executed=False,
        policy='No purchases/accounts/keys/login/CAPTCHA/403 bypass. No shell publisher request. Reader access failures retained and passed over.',
        replication='INFORMS supplementary page lists13parts; part1redirect inspected; no dataset payload/README/ZIP acquired. Reader inaccessible is not proof of a paywall.',
        correction='An unverified OUP article-path probe failed. It supplies no paper evidence. The actual returned DOI hhae044 was then opened once and returned a non-retryable redirected reader error.'), indent=2) + '\n')
    return dict(calls=len(calls), search_batches=sum(c['kind'] == 'search' for c in output), query_count=len(queries))


if __name__ == '__main__':
    print(json.dumps(convert(sys.argv[1]), indent=2))
