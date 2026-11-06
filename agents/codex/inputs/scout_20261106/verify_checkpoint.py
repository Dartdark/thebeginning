"""Read-only source-checkpoint audit; does not compute market returns."""
from pathlib import Path
import hashlib
import json
import subprocess


ROOT = Path(__file__).resolve().parents[4]
PARENT = 'b1985f3f74bb8687c0abaef0dae6d809e220d3f7'
BASE = Path('agents/codex/inputs/scout_20261106')


def read(path):
    return json.loads((ROOT / path).read_text())


def prior(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{PARENT}:{path}'], cwd=ROOT))


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    progress_path = 'agents/codex/research/scout/progress.json'
    p, old = read(progress_path), prior(progress_path)
    mutable = {'seen', 'last_run', 'run_history'}
    assert {k: v for k, v in p.items() if k not in mutable} == {
        k: v for k, v in old.items() if k not in mutable
    }, 'Budget, trials, notifications, ownership or prior program state changed'
    assert p['seen'][:len(old['seen'])] == old['seen']
    assert p['run_history'][:-1] == old['run_history']
    run = p['last_run']
    assert p['run_history'][-1] == run
    assert run == read('agents/codex/research/scout/runs/20261106_owned_source.json')
    assert (p['hypotheses_started'], p['economic_definitions'], p['lease']) == (4, 10, None)
    trial_hash = hashlib.sha256(json.dumps(p['trials'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert trial_hash == run['trial_history_sha256']
    assert sha('TRIALS.csv') == run['root_trials_sha256']
    assert run['return_tests_executed'] is False
    assert run['new_full_reviews'] == run['new_hypotheses'] == run['new_economic_definitions'] == 0
    assert not run['notification']['actionable'] and not run['notification']['key_created']
    assert run['checked_parent'] == PARENT

    records = run['record_paths']
    assert len(records) == len(set(records)) == run['new_paper_records'] == 20
    assert len(p['seen']) == len(old['seen']) + len(records)
    assert {s['record_path'] for s in p['seen'][len(old['seen']):]} == set(records)
    for path in records:
        record = read(path)
        for key in ('about', 'findings', 'mechanism', 'build_on', 'can_strategy_code_be_made'):
            assert isinstance(record[key], str) and record[key].strip(), (path, key)
        assert len(record['summary'].splitlines()) <= 5
        assert record['full_text_read'] is False and record['source_artifact'] is None
        assert record['return_eligibility'] == 'NOT_TEST'
        assert record['new_economic_trials'] == record['new_economic_definitions'] == 0
        assert (ROOT / record['report_path']).is_file()
        assert (ROOT / record['access_receipt']).is_file()
    assert sum(read(path)['evidence_level'] == 'selected_primary_sections' for path in records) == 6

    queries = read(BASE / 'queries.json')
    assert len(queries['queries']) == queries['query_count'] == run['query_count'] == 103
    assert len(set(queries['queries'])) == queries['unique_query_count']
    access = read(BASE / 'access.json')
    assert len(access['reader_receipts']) == 44
    for path in access['reader_receipts']:
        receipt = read(path)
        assert receipt['receipt_type'] == 'access_metadata_only'
        assert len(receipt['reader_result_sha256']) == 64
        assert 'content' not in receipt
    inventory = read(BASE / 'owned_input_inventory.json')
    assert inventory['market_returns_computed'] is False and len(inventory['files']) == 13
    for item in inventory['files']:
        assert item['exists'] and item['matches_previous_hash']
        assert sha(item['path']) == item['sha256'], item['path']

    c = read('agents/codex/research/scout/continuation.json')
    before = prior('agents/codex/research/scout/continuation.json')
    assert c['program'] == before['program'] and c['automation_id'] == before['automation_id']
    assert c['global_counts'] == before['global_counts']
    assert c['do_not_resume'] == before['do_not_resume']
    assert c['parked_not_next_tasks'][:len(before['parked_not_next_tasks'])] == before['parked_not_next_tasks']
    assert c['lease'] is None and c['active_test_reservation'] is None
    summary = (ROOT / run['report_path']).read_text().split('Summary: ', 1)[1].split('\n\n', 1)[0]
    assert len(summary.splitlines()) <= 5

    manifest = read(BASE / 'artifact_manifest.json')
    for path, expected in manifest['sha256'].items():
        assert sha(path) == expected, f'Artifact mismatch: {path}'
    print(json.dumps({'status': 'PASS', 'audit_scope': 'Source/checkpoint integrity only; no economic verification',
          'records': len(records), 'selected_source_records': 6, 'query_submissions': 103,
          'input_hashes_matched': 13, 'return_tests_executed': False,
          'trial_history_sha256': trial_hash, 'budget': [4, 10],
          'prior_history_notifications_and_lease_preserved': True,
          'manifest_files': len(manifest['sha256'])}, indent=2))


if __name__ == '__main__':
    main()
