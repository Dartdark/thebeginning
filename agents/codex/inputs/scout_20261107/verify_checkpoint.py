"""Read-only checkpoint integrity audit; does not compute signals or market returns."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[4]
PARENT = 'a6b0a8ecc420c9f51d1917db11cadb5d679115e5'
BASE = Path('agents/codex/inputs/scout_20261107')


def read(path):
    return json.loads((ROOT / path).read_text())


def prior_bytes(path):
    return subprocess.check_output(['git', 'show', f'{PARENT}:{path}'], cwd=ROOT)


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    progress_path = 'agents/codex/research/scout/progress.json'
    p = read(progress_path)
    old = json.loads(prior_bytes(progress_path))
    mutable = {'seen', 'last_run', 'run_history'}
    assert {k: v for k, v in p.items() if k not in mutable} == {
        k: v for k, v in old.items() if k not in mutable
    }, 'Budget/trials/ownership/notification or unrelated program state changed'
    assert p['seen'][:len(old['seen'])] == old['seen']
    assert p['run_history'][:-1] == old['run_history']
    run = read('agents/codex/research/scout/runs/20261107_owned_source.json')
    assert p['run_history'][-1] == p['last_run'] == run
    assert (p['hypotheses_started'], p['economic_definitions'], p['lease']) == (4, 10, None)
    trial_hash = hashlib.sha256(json.dumps(p['trials'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert trial_hash == run['trial_history_sha256'] == '466ad0eaa585dc809ae92c1f2e4c346ba3ad7b4d5d44330fa9f96c4dd2cedaba'
    assert sha('TRIALS.csv') == run['root_trials_sha256'] == '40597f5c61a99f0fb913c53067b630b4a2583af2643dcc44a0b567e9a372af4e'
    assert run['return_tests_executed'] is False
    assert run['new_full_reviews'] == run['new_hypotheses'] == run['new_economic_definitions'] == 0
    assert not run['notification']['actionable'] and not run['notification']['key_created']
    assert run['checked_parent'] == PARENT and run['lease'] is None and run['active_reservation'] is None

    records = run['record_paths']
    assert len(records) == len(set(records)) == run['new_paper_records'] == 21
    assert len(p['seen']) == len(old['seen']) + len(records)
    assert {s['record_path'] for s in p['seen'][len(old['seen']):]} == set(records)
    ids = []
    for path in records:
        record = read(path)
        ids.append(record['id'])
        for key in ('about', 'findings', 'mechanism', 'build_on', 'can_strategy_code_be_made', 'reading_scope', 'owned_input_mapping'):
            assert isinstance(record[key], str) and record[key].strip(), (path, key)
        assert len(record['summary'].splitlines()) <= 5
        assert record['full_text_read'] is False and record['source_artifact'] is None
        assert record['source_sha256'] is None and record['return_eligibility'] == 'NOT_TEST'
        assert record['new_economic_trials'] == record['new_economic_definitions'] == 0
        assert (ROOT / record['report_path']).is_file() and (ROOT / record['access_receipt']).is_file()
    assert len(ids) == len(set(ids)) and not set(ids).intersection(s['id'] for s in old['seen'] if 'id' in s)
    assert sum(read(path)['evidence_level'] == 'selected_primary_sections' for path in records) == run['selected_primary_section_records'] == 5

    # Every committed earlier paper record remains byte-for-byte unchanged, including the rediscovered NG climate paper.
    old_paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', PARENT, 'agents/codex/research/scout/records'], cwd=ROOT, text=True).splitlines()
    for path in old_paths:
        assert (ROOT / path).read_bytes() == prior_bytes(path), path
    assert len(list((ROOT / 'agents/codex/research/scout/records').glob('*.json'))) == len(old_paths) + len(records)

    queries = read(BASE / 'queries.json')
    assert len(queries['queries']) == queries['query_count'] == run['query_count'] == 83
    assert len(set(queries['queries'])) == queries['unique_query_count']
    before = json.loads(prior_bytes('agents/codex/research/scout/continuation.json'))
    assert queries['queries'][:3] == [row['query'] for row in before['next_distinct_discovery_routes']]
    access = read(BASE / 'access.json')
    assert len(access['reader_receipts']) == 36 and access['return_tests_executed'] is False
    for path in access['reader_receipts']:
        receipt = read(path)
        assert receipt['receipt_type'] == 'access_metadata_only'
        assert len(receipt['reader_result_sha256']) == 64
        assert not {'content', 'reader_result_utf8_for_hash'}.intersection(receipt)

    inventory = read(BASE / 'owned_input_inventory.json')
    assert inventory['market_returns_computed'] is False
    common = inventory['prior_selected_files']
    assert len(common) == 13 and all(row['exists'] and row['matches_previous_hash'] for row in common)
    archives, prices = inventory['bitcoin_cot_archives'], inventory['bitcoin_price_files']
    assert len(archives) == len(prices) == 5
    for item in common + archives + prices:
        assert sha(item['path']) == item['sha256'], item['path']
    assert all(row['required_fields_present'] and not row['actual_publication_timestamp_field_present'] for row in archives)
    assert [v['rows'] for v in archives[0]['venues']] == [39, 53]
    rerun = json.loads(subprocess.check_output([
        '/workspace/venvs/thebeginning/bin/python', 'analysis/codex_scout_source_inventory_20261107.py'], cwd=ROOT))
    assert rerun == inventory, 'Inventory reproduction differs'

    c = read('agents/codex/research/scout/continuation.json')
    assert c['program'] == before['program'] and c['automation_id'] == before['automation_id']
    assert c['global_counts'] == before['global_counts'] and c['do_not_resume'] == before['do_not_resume']
    assert c['parked_not_next_tasks'][:len(before['parked_not_next_tasks'])] == before['parked_not_next_tasks']
    assert c['retained_input_cautions'][:len(before['retained_input_cautions'])] == before['retained_input_cautions']
    assert c['lease'] is None and c['active_test_reservation'] is None
    execution = 'agents/codex/EXECUTION_REFERENCES.md'
    assert (ROOT / execution).read_bytes().startswith(prior_bytes(execution))
    summary = (ROOT / run['report_path']).read_text().split('Summary: ', 1)[1].split('\n\n', 1)[0]
    assert len(summary.splitlines()) <= 5
    manifest = read(BASE / 'artifact_manifest.json')
    for path, expected in manifest['sha256'].items():
        assert sha(path) == expected, f'Artifact mismatch: {path}'
    print(json.dumps(dict(status='PASS', audit_scope='Source/checkpoint integrity only; no economic verification',
                         records=len(records), earlier_records_preserved=len(old_paths), selected_source_records=5,
                         query_submissions=83, input_hashes_matched=13, additional_input_hashes_pinned=10,
                         return_tests_executed=False, trial_history_sha256=trial_hash,
                         budget=[4, 10], prior_history_notifications_and_lease_preserved=True,
                         manifest_files=len(manifest['sha256'])), indent=2))


if __name__ == '__main__':
    main()
