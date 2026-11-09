"""Audit discovery/checkpoint integrity. This does not admit data or verify alpha."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = 'a0a70dad120439aa35611c7c40b8146e88f30214'
BASE = 'agents/codex/inputs/scout_20261109'
RUN = 'agents/codex/research/scout/runs/20261109_owned_source.json'


def read(path):
    return json.loads((ROOT / path).read_text())


def prior(path):
    return subprocess.check_output(['git', 'show', f'{PARENT}:{path}'], cwd=ROOT)


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def audit():
    progress_path = 'agents/codex/research/scout/progress.json'
    p, old = read(progress_path), json.loads(prior(progress_path))
    mutable = {'seen', 'last_run', 'run_history'}
    assert {k: v for k, v in p.items() if k not in mutable} == {
        k: v for k, v in old.items() if k not in mutable
    }, 'Budget, trials, notification, ownership or unrelated state changed'
    run = read(RUN)
    assert p['seen'][:len(old['seen'])] == old['seen']
    assert p['run_history'][:-1] == old['run_history']
    assert p['last_run'] == p['run_history'][-1] == run
    assert (p['hypotheses_started'], p['economic_definitions'], p['lease']) == (4, 10, None)
    canonical = json.dumps(p['trials'], sort_keys=True, separators=(',', ':')).encode()
    assert hashlib.sha256(canonical).hexdigest() == run['trial_history_sha256'] == (
        '466ad0eaa585dc809ae92c1f2e4c346ba3ad7b4d5d44330fa9f96c4dd2cedaba')
    assert sha('TRIALS.csv') == run['root_trials_sha256'] == (
        '40597f5c61a99f0fb913c53067b630b4a2583af2643dcc44a0b567e9a372af4e')
    assert run['checked_parent'] == PARENT
    assert run['new_full_reviews'] == run['new_hypotheses'] == run['new_economic_definitions'] == 0
    assert run['return_tests_executed'] is False
    assert run['lease'] is run['active_reservation'] is None
    assert not run['notification']['actionable'] and not run['notification']['key_created']

    paths = run['record_paths']
    assert len(paths) == len(set(paths)) == run['new_paper_records'] == 16
    assert len(p['seen']) == len(old['seen']) + len(paths)
    assert {s['record_path'] for s in p['seen'][len(old['seen']):]} == set(paths)
    records = [read(path) for path in paths]
    assert len({r['id'] for r in records}) == len(records)
    for r in records:
        for key in ['about', 'findings', 'mechanism', 'build_on', 'can_strategy_code_be_made',
                    'reading_scope', 'source_version', 'economic_family', 'owned_input_mapping']:
            assert isinstance(r[key], str) and r[key].strip(), (r['id'], key)
        assert r['full_text_read'] is False and r['source_artifact'] is r['source_sha256'] is None
        assert r['return_eligibility'] == 'NOT_TEST'
        assert r['new_economic_trials'] == r['new_economic_definitions'] == 0
        assert len(r['summary'].splitlines()) <= 5
        assert (ROOT / r['report_path']).is_file() and (ROOT / r['access_receipt']).is_file()
    selected = sum(r['evidence_level'] == 'selected_primary_sections' for r in records)
    assert selected == run['selected_primary_section_records'] == 2
    old_paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', PARENT,
                                         'agents/codex/research/scout/records'], cwd=ROOT, text=True).splitlines()
    assert len(old_paths) == 197
    for path in old_paths:
        assert (ROOT / path).read_bytes() == prior(path), f'Earlier record changed: {path}'
    all_paths = list((ROOT / 'agents/codex/research/scout/records').glob('*.json'))
    assert len(all_paths) == len(old_paths) + len(paths)
    all_records = [json.loads(path.read_text()) for path in all_paths]
    norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
    for r in records:
        assert sum(o['id'] == r['id'] for o in all_records) == 1
        assert sum(norm(o.get('title', '')) == norm(r['title']) for o in all_records) == 1

    q = read(f'{BASE}/queries.json')
    assert len(q['queries']) == q['query_count'] == run['query_count'] == 95
    assert len(set(q['queries'])) == q['unique_query_count']
    before = json.loads(prior('agents/codex/research/scout/continuation.json'))
    assert q['queries'][:3] == [r['query'] for r in before['next_distinct_discovery_routes']]
    access = read(f'{BASE}/access.json')
    assert access['return_tests_executed'] is False and access['source_bytes_acquired'] is False
    calls = read(f'{BASE}/discovery_receipts.json')['calls']
    assert len(calls) == access['calls'] == 34
    assert [c['sequence'] for c in calls] == list(range(1, 35))
    assert sum(c['kind'] == 'search' for c in calls) == q['search_batches'] == run['search_batches'] == 24
    assert [query for c in calls for query in c['queries']] == q['queries']
    for c in calls:
        assert c['receipt_type'] == 'access_metadata_only' and len(c['reader_result_sha256']) == 64
        assert not c['body_retained'] and not c['source_bytes_acquired']
        assert not {'response_text', 'content', 'reader_result_utf8_for_hash'}.intersection(c)
        for m in c['metadata']:
            assert len(m['header']) == 1
            assert not re.search(r'L[0-9]+(?:@P[0-9]+)?:', m['header'][0])

    inventory = read(f'{BASE}/owned_input_inventory.json')
    assert inventory['market_returns_computed'] is False
    assert len(inventory['prior_files']) == 13
    assert all(r['exists'] and r['matches_previous_hash'] for r in inventory['prior_files'])
    assert len(inventory['macro_files']) == len(inventory['native_files']) == 5
    assert all(r['matches_manifest'] for r in inventory['macro_files'] + inventory['native_files'])
    assert not inventory['macro_admitted'] and inventory['native_status'] == 'PACKAGED_NOT_RESEARCH_ADMITTED'
    assert len(inventory['macro_series_ids']) == 15
    assert len(inventory['missing_source_1920401_ten_am_release_families']) == 7
    for row in inventory['prior_files'] + inventory['macro_files'] + inventory['native_files'] + inventory['sidecars']:
        assert sha(row['path']) == row['sha256'], row['path']
    replay = json.loads(subprocess.check_output([
        '/workspace/venvs/thebeginning/bin/python', 'analysis/codex_scout_source_inventory_20261109.py'], cwd=ROOT))
    assert replay == inventory

    c = read('agents/codex/research/scout/continuation.json')
    for key in ['program', 'automation_id', 'global_counts', 'do_not_resume', 'lease', 'active_test_reservation']:
        assert c[key] == before[key], key
    for key in ['parked_not_next_tasks', 'retained_input_cautions']:
        assert c[key][:len(before[key])] == before[key]
    assert c['report_path'] == run['report_path'] and c['last_run_receipt'] == RUN
    assert len(c['next_distinct_discovery_routes']) == 3
    prior_queries = set(q['queries'])
    for path in (ROOT / 'agents/codex/inputs').glob('scout_*/queries.json'):
        obj = json.loads(path.read_text())
        if isinstance(obj, dict) and isinstance(obj.get('queries'), list):
            prior_queries.update(s for s in obj['queries'] if isinstance(s, str))
    assert not prior_queries.intersection(r['query'] for r in c['next_distinct_discovery_routes'])
    for path in ['TODO.md', 'agents/codex/EXECUTION_REFERENCES.md']:
        assert (ROOT / path).read_bytes().startswith(prior(path)), path
        assert all(identity in (ROOT / path).read_text() for identity in ['3360787', '4388560'])
    report = (ROOT / run['report_path']).read_text()
    assert len(report.split('Summary: ', 1)[1].split('\n\n', 1)[0].splitlines()) <= 5
    for question in ['What is it about?', 'What does it find?', 'Why might it make money?',
                     'Can we build on it?', 'Can strategy code be made?']:
        assert report.count(f'**{question}**') == len(records)
    manifest = read(f'{BASE}/artifact_manifest.json')
    for path, expected in manifest['sha256'].items():
        assert sha(path) == expected, f'Artifact hash differs: {path}'
    return dict(status='PASS', scope='Discovery/checkpoint integrity only; not source/data admission or economic verification',
                queries=q['query_count'], batches=q['search_batches'], records=len(records),
                selected_source_checks=selected, earlier_records_preserved=len(old_paths),
                prior_raw_hashes_matching=13, macro_snapshot_hashes_matching=5,
                native_compressed_and_original_hash_pairs_matching=5,
                full_reviews=0, new_hypotheses=0, new_definitions=0, return_tests=0,
                budget=dict(hypotheses=4, definitions=10), lease=None)


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
