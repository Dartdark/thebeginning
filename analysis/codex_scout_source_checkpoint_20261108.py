"""Validate source-checkpoint integrity; never run a strategy or certify alpha."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = '386e3d7d0fdc24d79da5512c6b76de6ff9270c0a'
BASE = 'agents/codex/inputs/scout_20261108'


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
    }, 'Unrelated state, budget, trials, notifications or ownership changed'
    assert p['seen'][:len(old['seen'])] == old['seen']
    assert p['run_history'][:-1] == old['run_history']
    run = read('agents/codex/research/scout/runs/20261108_owned_source.json')
    assert p['last_run'] == p['run_history'][-1] == run
    assert (p['hypotheses_started'], p['economic_definitions'], p['lease']) == (4, 10, None)
    trial_hash = hashlib.sha256(json.dumps(p['trials'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert trial_hash == run['trial_history_sha256'] == '466ad0eaa585dc809ae92c1f2e4c346ba3ad7b4d5d44330fa9f96c4dd2cedaba'
    assert sha('TRIALS.csv') == run['root_trials_sha256'] == '40597f5c61a99f0fb913c53067b630b4a2583af2643dcc44a0b567e9a372af4e'
    assert run['checked_parent'] == PARENT
    assert run['new_full_reviews'] == run['new_hypotheses'] == run['new_economic_definitions'] == 0
    assert run['return_tests_executed'] is False
    assert run['lease'] is run['active_reservation'] is None
    assert not run['notification']['actionable'] and not run['notification']['key_created']

    paths = run['record_paths']
    assert len(paths) == len(set(paths)) == run['new_paper_records'] == 14
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
    assert selected == run['selected_primary_section_records'] == 4
    old_paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', PARENT,
                                         'agents/codex/research/scout/records'], cwd=ROOT, text=True).splitlines()
    for path in old_paths:
        assert (ROOT / path).read_bytes() == prior(path), f'Earlier record changed: {path}'
    assert len(list((ROOT / 'agents/codex/research/scout/records').glob('*.json'))) == len(old_paths) + len(paths)

    q = read(f'{BASE}/queries.json')
    assert len(q['queries']) == q['query_count'] == run['query_count'] == 90
    assert len(set(q['queries'])) == q['unique_query_count']
    before = json.loads(prior('agents/codex/research/scout/continuation.json'))
    assert q['queries'][:3] == [r['query'] for r in before['next_distinct_discovery_routes']]
    access = read(f'{BASE}/access.json')
    assert access['return_tests_executed'] is False and access['source_bytes_acquired'] is False
    assert len(access['reader_receipts']) == access['calls'] == 34
    calls = [read(path) for path in access['reader_receipts']]
    assert [c['sequence'] for c in calls] == list(range(1, 35))
    assert sum(c['kind'] == 'search' for c in calls) == q['search_batches'] == run['search_batches'] == 23
    assert [query for c in calls for query in c['queries']] == q['queries']
    for c in calls:
        assert c['receipt_type'] == 'access_metadata_only' and len(c['reader_result_sha256']) == 64
        assert not c['body_retained'] and not c['source_bytes_acquired']
        assert not {'response_text', 'content', 'reader_result_utf8_for_hash'}.intersection(c)

    inventory = read(f'{BASE}/owned_input_inventory.json')
    assert inventory['market_returns_computed'] is False
    assert len(inventory['files']) == 13
    assert all(r['exists'] and r['matches_previous_hash'] for r in inventory['files'])
    assert len(inventory['macro_calendar_headers']) == 2
    for row in inventory['files'] + inventory['macro_calendar_headers']:
        assert sha(row['path']) == row['sha256'], row['path']
    replay = json.loads(subprocess.check_output([
        '/workspace/venvs/thebeginning/bin/python', 'analysis/codex_scout_source_inventory_20261108.py'], cwd=ROOT))
    assert replay == inventory

    c = read('agents/codex/research/scout/continuation.json')
    for key in ['program', 'automation_id', 'global_counts', 'do_not_resume', 'lease', 'active_test_reservation']:
        assert c[key] == before[key], key
    for key in ['parked_not_next_tasks', 'retained_input_cautions']:
        assert c[key][:len(before[key])] == before[key]
    assert c['report_path'] == run['report_path']
    assert len(c['next_distinct_discovery_routes']) == 3
    prior_queries = set(q['queries'])
    for path in (ROOT / 'agents/codex/inputs').glob('scout_*/queries.json'):
        obj = read(path.relative_to(ROOT))
        if isinstance(obj, dict) and isinstance(obj.get('queries'), list):
            prior_queries.update(s for s in obj['queries'] if isinstance(s, str))
    assert not prior_queries.intersection(r['query'] for r in c['next_distinct_discovery_routes'])
    assert (ROOT / 'agents/codex/EXECUTION_REFERENCES.md').read_bytes().startswith(prior('agents/codex/EXECUTION_REFERENCES.md'))
    for path in ['TODO.md', 'agents/codex/DATA_NEEDED.md']:
        assert '1920401' in (ROOT / path).read_text()
    report = (ROOT / run['report_path']).read_text()
    assert len(report.split('Summary: ', 1)[1].split('\n\n', 1)[0].splitlines()) <= 5
    manifest = read(f'{BASE}/artifact_manifest.json')
    for path, expected in manifest['sha256'].items():
        assert sha(path) == expected, f'Artifact hash differs: {path}'
    return dict(status='PASS', scope='Source/checkpoint integrity only; no economic verification',
                queries=q['query_count'], batches=q['search_batches'], records=len(records),
                selected_source_checks=selected, earlier_records_preserved=len(old_paths),
                selected_input_hashes_matching=13, full_reviews=0, new_hypotheses=0,
                new_definitions=0, return_tests=0, budget=[4, 10], lease=None)


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
