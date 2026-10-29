"""SSRN metadata scout. No PDF scraping, model calls, return tests, or arbitrary URLs.

Crossref supplies metadata for SSRN's DOI prefix. Scores are routing heuristics,
never evidence of profitability. Paper text still needs source-level review.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from html import unescape
import json
import math
import os
from pathlib import Path
import re
import tempfile
import threading
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

SCHEMA_VERSION = 1
LOCK = threading.RLock()
MAX_RESPONSE_BYTES = 2_000_000
MAX_PAPERS = 5000
TIMEOUT_SECONDS = 8
QUERIES = (
    'equity index futures scheduled flows rebalancing',
    'index options expiration dealer hedging futures',
    'market close auction imbalance transaction costs',
    'overnight futures risk portfolio diversification',
)
API_ROOT = 'https://api.crossref.org/prefixes/10.2139/works'
SSRN_RE = re.compile(r'(?:ssrn(?:\.com/abstract=|[^\d]{0,12})|abstract_?id=)([1-9]\d{3,9})', re.I)


def _clock(now=None):
    value = now() if callable(now) else now
    value = value or datetime.now(timezone.utc)
    if isinstance(value, str): value = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if value.tzinfo is None: raise ValueError('Scout timestamps require an explicit timezone')
    return value.astimezone(timezone.utc)


def _timestamp(now=None): return _clock(now).isoformat()


def _blank():
    return {'schema_version': SCHEMA_VERSION, 'revision': 0, 'papers': [], 'seen_ids': [], 'runs': [],
            'config': {'provider': 'Crossref SSRN DOI metadata', 'doi_prefix': '10.2139',
                       'queries': list(QUERIES), 'lookback_days': 365, 'max_results': 20,
                       'evidence_level': 'metadata_only', 'automatic_backtests': False}}


def _read(runtime):
    path = Path(runtime) / 'scout.json'
    if not path.exists(): return _blank()
    state = json.loads(path.read_text(encoding='utf-8'))
    if state.get('schema_version') != SCHEMA_VERSION: raise ValueError('Unsupported scout state version')
    if not isinstance(state.get('papers'), list) or not isinstance(state.get('runs'), list):
        raise ValueError('Invalid scout state')
    return state


@contextmanager
def _locked(runtime):
    """Thread and process exclusion; a busy scan is not mistaken for a second job."""
    runtime = Path(runtime)
    runtime.mkdir(parents=True, exist_ok=True)
    with LOCK:
        lock = runtime / 'scout.lock'
        try: fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as e: raise ValueError('A scout scan is already running; wait before retrying') from e
        try:
            with os.fdopen(fd, 'w') as file: file.write(str(os.getpid()))
            yield
        finally: lock.unlink(missing_ok=True)


def _write(runtime, state):
    runtime = Path(runtime)
    runtime.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=runtime, prefix='.scout-', delete=False) as file:
            name = Path(file.name)
            json.dump(state, file, ensure_ascii=False, indent=2, allow_nan=False)
            file.write('\n'); file.flush(); os.fsync(file.fileno())
        name.replace(runtime / 'scout.json')
    finally:
        if name is not None: name.unlink(missing_ok=True)


def _text(value, limit):
    if isinstance(value, list): value = value[0] if value else ''
    if not isinstance(value, (str, int)): return ''
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]*>', ' ', str(value)))).strip()[:limit]


def _published(item):
    value = item.get('published') or item.get('published-print') or item.get('published-online') or {}
    if isinstance(value, dict):
        parts = value.get('date-parts', [[]])
        try:
            p = list(parts[0]); p += [1] * (3-len(p))
            return date(*p[:3]).isoformat()
        except (ValueError, TypeError, IndexError): return None
    if isinstance(value, str):
        try: return date.fromisoformat(value[:10]).isoformat()
        except ValueError: return None
    return None


def normalize_candidate(item):
    """Accept Crossref or a minimal offline record, ignoring supplied verdicts/returns."""
    if not isinstance(item, dict): raise ValueError('Candidate must be a metadata object')
    doi = _text(item.get('DOI', item.get('doi', '')), 180).lower()
    doi = re.sub(r'^https?://(?:dx\.)?doi\.org/', '', doi)
    match = re.fullmatch(r'10\.2139/ssrn\.([1-9]\d{3,9})', doi)
    supplied_id = str(item.get('ssrn_id', '')).strip()
    if match:
        ssrn_id = match.group(1)
        if supplied_id and supplied_id != ssrn_id: raise ValueError('DOI and SSRN ID disagree')
    elif not doi and re.fullmatch(r'[1-9]\d{3,9}', supplied_id): ssrn_id = supplied_id
    else: raise ValueError('An SSRN 10.2139/ssrn DOI or numeric SSRN ID is required')
    title = _text(item.get('title', ''), 500)
    if not title: raise ValueError('Paper title is required')
    authors = []
    source_authors = item.get('author') or item.get('authors') or []
    if isinstance(source_authors, (str, dict)): source_authors = [source_authors]
    if not isinstance(source_authors, list): raise ValueError('Authors must be a list or author name')
    for author in source_authors[:20]:
        if isinstance(author, dict):
            name = ' '.join(v for v in [_text(author.get('given', ''), 100), _text(author.get('family', ''), 100)] if v)
        else: name = _text(author, 200)
        if name: authors.append(name)
    return {'id': 'ssrn:' + ssrn_id, 'ssrn_id': ssrn_id, 'doi': '10.2139/ssrn.' + ssrn_id,
            'title': title, 'authors': authors, 'abstract': _text(item.get('abstract', ''), 8000),
            'published': _published(item), 'url': 'https://ssrn.com/abstract=' + ssrn_id,
            'evidence_level': 'metadata_only'}


def classify(candidate):
    """Transparent topic routing, not a merit/return classifier."""
    text = (candidate['title'] + ' ' + candidate['abstract']).lower()
    markets = [p for p in ['futures', 's&p 500', 's&p500', 'nasdaq', 'equity index', 'index futures', 'e-mini'] if p in text]
    mechanisms = [p for p in ['rebalanc', 'forced flow', 'forced trading', 'index inclusion', 'index rebalance',
                              'expiration', 'option expir', 'dealer hedg', 'leveraged etf', 'volatility control',
                              'payroll', 'closing auction', 'market-on-close', 'scheduled flow'] if p in text]
    execution = [p for p in ['execution', 'transaction cost', 'market impact', 'bid-ask', 'order book',
                             'queue priority', 'slippage', 'auction imbalance', 'liquidity provision'] if p in text]
    methods = [p for p in ['tail risk', 'value-at-risk', 'expected shortfall', 'backtest overfitting',
                           'look-ahead', 'walk-forward', 'out-of-sample', 'risk model'] if p in text]
    unrelated = [p for p in ['individual stocks', 'cross-sectional stock', 'corporate bond', 'credit default', 'esg'] if p in text]
    score = min(100, len(markets)*8 + len(mechanisms)*13 + len(execution)*6 + len(methods)*4)
    if unrelated and not markets: score = max(0, score-15)
    if mechanisms and markets: category = 'strategy'
    elif execution: category = 'execution'
    elif methods: category = 'methods'
    else: category = 'low_relevance'
    reasons = []
    if markets: reasons.append('Market terms: ' + ', '.join(markets))
    if mechanisms: reasons.append('Possible flow/event terms: ' + ', '.join(mechanisms))
    if execution: reasons.append('Execution terms: ' + ', '.join(execution))
    if methods: reasons.append('Method/risk terms: ' + ', '.join(methods))
    if unrelated: reasons.append('Transfer caution: ' + ', '.join(unrelated))
    reasons.append('Metadata routing only; the source and reported results still require review.')
    return category, score, reasons


def _repository_index(root):
    root = Path(root)
    paths = []
    for folder in ['agents/codex/results', 'agents/codex/evidence', 'agents/codex/plans']:
        paths.extend((root / folder).glob('*.md'))
    paths += [root / p for p in ['TIER_LIST.md', 'WATCHLIST.md', 'TODO.md', 'agents/codex/EXECUTION_REFERENCES.md']]
    primary, mentions = {}, {}
    for path in paths:
        if not path.is_file(): continue
        text = path.read_text(encoding='utf-8', errors='replace')[:250000]
        relative = str(path.relative_to(root)).replace(os.sep, '/')
        ids = set(SSRN_RE.findall(text))
        ids.update(re.findall(r'10\.2139/ssrn\.([1-9]\d{3,9})', text, re.I))
        for paper_id in ids: mentions.setdefault(paper_id, set()).add(relative)
        if path.parent.name == 'results':
            # Most source-only reviews identify their primary source before the first numbered section.
            head = re.split(r'\n## ', text, maxsplit=1)[0]
            primary_ids = set(SSRN_RE.findall(head)) | set(re.findall(r'10\.2139/ssrn\.([1-9]\d{3,9})', head, re.I))
            for paper_id in primary_ids: primary.setdefault(paper_id, set()).add(relative)
        elif path.name == 'TIER_LIST.md':
            for paper_id in ids: primary.setdefault(paper_id, set()).add(relative)
    return primary, mentions


def _refresh(paper, primary, mentions):
    paper_id = paper['ssrn_id']
    reviewed = sorted(primary.get(paper_id, []), key=lambda p: (not p.startswith('agents/codex/results/'), p))
    paper['reviewed_in'] = reviewed
    paper['review_path'] = reviewed[0] if reviewed else None
    paper['repository_mentions'] = sorted(mentions.get(paper_id, []))
    category, score, reasons = classify(paper)
    paper.update(category=category, score=score, reasons=reasons)
    paper['status'] = 'already_reviewed' if reviewed else ('needs_full_text' if category != 'low_relevance' else 'metadata_only')
    # Explicitly reset these on every read/import; external metadata cannot assert completed analysis.
    paper['evidence_level'] = 'metadata_only'
    return paper


def list_state(root, runtime):
    state = _read(runtime)
    primary, mentions = _repository_index(root)
    state['papers'] = [_refresh(p, primary, mentions) for p in state['papers']]
    state['papers'].sort(key=lambda p: (p['status'] == 'already_reviewed', -p['score'], p['id']))
    return state


def _merge(root, state, candidates, stamp, source):
    primary, mentions = _repository_index(root)
    papers = {p['id']: p for p in state['papers']}
    seen = set(state.get('seen_ids', []))
    counts = dict(received=0, added=0, seen_again=0, already_reviewed=0, invalid=0)
    errors = []
    batch_seen = set()
    for item in candidates:
        counts['received'] += 1
        try: paper = normalize_candidate(item)
        except (ValueError, TypeError) as e:
            counts['invalid'] += 1
            if len(errors) < 10: errors.append(str(e))
            continue
        if paper['id'] in batch_seen: continue
        batch_seen.add(paper['id'])
        old = papers.get(paper['id'])
        if old:
            paper['first_seen'] = old['first_seen']
            paper['discovered_at'] = old.get('discovered_at', old['first_seen'])
            # Sparse metadata updates must not erase a previously available abstract.
            if not paper['abstract']: paper['abstract'] = old.get('abstract', '')
            counts['seen_again'] += 1
        else:
            if len(papers) >= MAX_PAPERS:
                counts['invalid'] += 1; errors.append('Scout store is full; no unseen record was discarded silently')
                continue
            paper['first_seen'] = stamp
            paper['discovered_at'] = stamp
            counts['added'] += 1
        paper['last_seen'] = stamp
        paper['source'] = source
        _refresh(paper, primary, mentions)
        if paper['status'] == 'already_reviewed': counts['already_reviewed'] += 1
        papers[paper['id']] = paper
        seen.add(paper['id'])
    state['papers'] = sorted(papers.values(), key=lambda p: (p['status'] == 'already_reviewed', -p['score'], p['id']))
    state['seen_ids'] = sorted(seen)
    return counts, errors


def import_candidates(root, runtime, candidates, *, now=None, source='agent'):
    """Import discovered metadata from a cloud run without importing its executable instructions."""
    if not isinstance(candidates, list) or len(candidates) > 100: raise ValueError('Import at most 100 metadata records')
    stamp = _timestamp(now)
    with _locked(runtime):
        state = _read(runtime)
        counts, errors = _merge(root, state, candidates, stamp, _text(source, 120) or 'agent')
        state['revision'] += 1
        receipt = dict(id=f"import-{state['revision']}", started_at=stamp, finished_at=stamp,
                       status='partial' if errors else 'completed', provider='provided metadata',
                       errors=errors, counts=counts, network_requests=0, return_trials=0)
        state['runs'] = (state['runs'] + [receipt])[-100:]
        _write(runtime, state)
        return state


class _StrictRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlsplit(newurl)
        if parsed.scheme != 'https' or parsed.hostname != 'api.crossref.org' or parsed.port not in (None, 443):
            raise ValueError('Crossref redirected outside the allowed metadata host')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _open(request, timeout): return build_opener(_StrictRedirect()).open(request, timeout=timeout)


def discover(root, runtime, max_results=20, *, opener=None, now=None):
    """Bounded recent-SSRN metadata scan. Network failures remain explicit receipts."""
    if isinstance(max_results, bool) or not isinstance(max_results, int) or not 1 <= max_results <= 30:
        raise ValueError('max_results must be between 1 and 30')
    clock = _clock(now)
    started = clock.isoformat()
    opener = opener or _open
    with _locked(runtime):
        state = _read(runtime)
        items, attempts, errors = [], [], []
        stop_reason = None
        since = (clock.date() - timedelta(days=365)).isoformat()
        rows = min(30, max(5, math.ceil(max_results/len(QUERIES))*2))
        for query in QUERIES:
            url = API_ROOT + '?' + urlencode({'query': query, 'rows': rows, 'filter': 'from-pub-date:'+since,
                                              'sort': 'published', 'order': 'desc'})
            if stop_reason:
                attempts.append(dict(query=query, url=url, status='skipped', reason=stop_reason))
                continue
            request = Request(url, headers={'User-Agent': 'BeginningResearchTerminal/0.2 (SSRN metadata research)',
                                            'Accept': 'application/json'})
            attempt = dict(query=query, url=url, status='failed')
            try:
                with opener(request, timeout=TIMEOUT_SECONDS) as response:
                    raw = response.read(MAX_RESPONSE_BYTES+1)
                if len(raw) > MAX_RESPONSE_BYTES: raise ValueError('Crossref response exceeded the metadata size limit')
                payload = json.loads(raw)
                records = payload.get('message', {}).get('items')
                if not isinstance(records, list): raise ValueError('Crossref response did not contain an items list')
                attempt.update(status='completed', returned=len(records))
                items.extend(records)
            except (HTTPError, URLError, TimeoutError, OSError, ValueError, TypeError, AttributeError) as e:
                detail = f'HTTP {e.code}' if isinstance(e, HTTPError) else str(e)
                attempt['error'] = detail[:400]
                errors.append(f'{query}: {detail[:400]}')
                hard_http = isinstance(e, HTTPError) and e.code in (401, 403, 429)
                proxy_denial = isinstance(e, URLError) and re.search(
                    r'forbidden|proxy.*403|403.*proxy|tunnel.*403', detail, re.I)
                if hard_http or proxy_denial:
                    stop_reason = 'rate_limited' if isinstance(e, HTTPError) and e.code == 429 else 'access_denied'
                    attempt['stop_reason'] = stop_reason
            attempts.append(attempt)
        # Normalize/rank in memory before the run cap; never execute metadata, URLs, or source code.
        valid, invalid = {}, 0
        for item in items:
            try:
                candidate = normalize_candidate(item)
                existing = valid.get(candidate['id'])
                if not existing or len(candidate['abstract']) > len(existing['abstract']): valid[candidate['id']] = candidate
            except (ValueError, TypeError): invalid += 1
        ranked = sorted(valid.values(), key=lambda p: (-classify(p)[1], p['id']))[:max_results]
        counts, import_errors = _merge(root, state, ranked, started, 'Crossref SSRN DOI metadata')
        counts['invalid_from_provider'] = invalid
        counts['unique_returned'] = len(valid)
        errors.extend(import_errors)
        successful = sum(a['status'] == 'completed' for a in attempts)
        status = 'completed' if successful == len(QUERIES) and not errors else ('partial' if successful else 'failed')
        state['revision'] += 1
        state['config']['max_results'] = max_results
        state['runs'] = (state['runs'] + [dict(id=f"scan-{state['revision']}", started_at=started,
                         finished_at=_timestamp(now), status=status, provider='Crossref SSRN DOI metadata',
                         counts=counts, attempts=attempts, errors=errors,
                         network_requests=sum(a['status'] != 'skipped' for a in attempts),
                         stop_reason=stop_reason, return_trials=0)])[-100:]
        _write(runtime, state)
        return state
