"""Source/count/input-integrity checks only: no financial return calculations.

Run from the repository with the configured Python. Does not simulate the strategy,
certify data availability or independently verify author performance claims.
"""
from pathlib import Path
import gzip
import hashlib
import json
import re
import subprocess

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'agents/codex/inputs/ng_informed_2826684'
PARENT = '186adf3afb0b4f0740c4d4907877ad460aeac8a2'
SOURCE_SHA = '44131ff279db2c545c08758f8f94db889fc97c66a049ee1ab14b55941e69829b'


def read(path):
    return json.loads((ROOT / path).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prior(path):
    return subprocess.check_output(['git', 'show', f'{PARENT}:{path}'], cwd=ROOT)


def input_gate():
    rows = []
    manifest_path = ROOT / 'agents/codex/inputs/ng_corrected_20261031/manifest.json'
    for expected in json.loads(manifest_path.read_text()):
        path = ROOT / expected['archive']
        data = path.read_bytes()
        original = gzip.decompress(data)
        rows.append(dict(path=expected['archive'], year=expected['year'], bytes=len(data),
                         sha256=hashlib.sha256(data).hexdigest(),
                         original_sha256=hashlib.sha256(original).hexdigest(),
                         archive_hash_matches=hashlib.sha256(data).hexdigest() == expected['archive_sha256'],
                         original_hash_matches=hashlib.sha256(original).hexdigest() == expected['raw_sha256'],
                         columns=original.splitlines()[0].decode('utf-8-sig').split(',')))
    catalog_path = 'agents/codex/inputs/eval_focus_20261109/macro_intake/snapshot/metadata/series-catalog.json'
    catalog = read(catalog_path)
    supplement = 'agents/codex/inputs/dot_free_input_acquisition_20261110/acquisition_manifest.json'
    name_census = sorted(str(p.relative_to(ROOT)) for base in [ROOT / 'data', ROOT / 'agents/codex/inputs']
                         for p in base.rglob('*') if p.is_file() and
                         not p.is_relative_to(BASE) and any(
                             word in p.name.lower() for word in ['forecast', 'consensus', 'analyst', 'ranking']))
    return dict(scope='Existing manifest bytes, NG archive/original identities, header/catalog and filename census only; no price outcomes.',
                market_returns_computed=False, ng_manifest_sha256=sha(manifest_path), ng_files=rows,
                macro_catalog=dict(path=catalog_path, sha256=sha(ROOT / catalog_path),
                                   ids=[r['id'] for r in catalog],
                                   missing='No natural-gas storage survey or individual analyst/rank fields in this15-series catalog.'),
                dot_supplement=dict(path=supplement, sha256=sha(ROOT / supplement),
                                    scope='FOMC schedule, COT and petroleum EIA calendar; not NG analyst forecasts.'),
                forecast_named_files=name_census,
                conclusion='No authenticated source-matched pre-entry NG analyst forecast/previous-week rank/consensus receipt panel identified. Filename census is not proof none can exist.',
                return_eligibility='NEEDS_DATA', paid_or_external_contact=False)


def audit():
    assert sha(BASE / 'source.pdf') == SOURCE_SHA
    pdf = PdfReader(BASE / 'source.pdf')
    assert len(pdf.pages) == 43
    table = pdf.pages[36].extract_text()
    for text in ['271', '153', '0.84', '1.26', '1.40', '2.12', '90', '5']:
        assert text in table, text
    claims = json.loads((BASE / 'source_tables.json').read_text())
    assert claims['sample']['announcements'] - claims['sample']['excluded_same_day_petroleum'] == claims['sample']['retained'] == 334
    assert claims['sample']['retained'] - claims['sample']['zero_predictor'] == claims['sample']['nonzero_predictor'] == 271
    assert claims['table_XIII']['large_predictor']['events'] == 153
    assert claims['table_XIII']['reported_net_profit'] is None
    text = (BASE / 'source.txt').read_text()
    assert len(re.findall(r'=== PDF PAGE \d+ ===', text)) == 43
    inventory = input_gate()
    assert len(inventory['ng_files']) == 10
    assert all(r['archive_hash_matches'] and r['original_hash_matches'] for r in inventory['ng_files'])
    assert len(inventory['macro_catalog']['ids']) == 15
    (BASE / 'owned_input_gate.json').write_text(json.dumps(inventory, indent=2) + '\n')

    path = 'agents/codex/research/scout/progress.json'
    p, old = read(path), json.loads(prior(path))
    # Upload source upgrades must preserve all return/ownership/notification state and earlier runs.
    allowed = {'seen', 'last_run', 'run_history'}
    assert {k: v for k, v in p.items() if k not in allowed} == {k: v for k, v in old.items() if k not in allowed}
    assert p['seen'][:len(old['seen'])] == old['seen']
    assert p['run_history'][:-1] == old['run_history']
    assert p['last_run'] == p['run_history'][-1]
    assert (p['hypotheses_started'], p['economic_definitions'], p['lease']) == (4, 10, None)
    assert (ROOT / 'TRIALS.csv').read_bytes() == prior('TRIALS.csv')
    assert (ROOT / 'agents/codex/research/scout/continuation.json').read_bytes() == prior('agents/codex/research/scout/continuation.json')
    record_path = 'agents/codex/research/scout/records/2826684.json'
    old_record = json.loads(prior(record_path))
    assert json.loads((BASE / 'previous_record.json').read_text()) == old_record
    r = read(record_path)
    assert old_record in r['review_history'] and r['full_text_read'] is True
    assert r['verdict'] == 'needs_data' and r['return_eligibility'] == 'NOT_TEST'
    assert r['new_economic_trials'] == r['new_economic_definitions'] == 0
    assert r['source_artifact']['sha256'] == SOURCE_SHA
    assert len(r['summary'].splitlines()) <= 5
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', PARENT,
                                     'agents/codex/research/scout/records'], cwd=ROOT, text=True).splitlines()
    for path in paths:
        if path != record_path:
            assert (ROOT / path).read_bytes() == prior(path), path
    for path in ['TODO.md', 'agents/codex/DATA_NEEDED.md', 'agents/codex/EXECUTION_REFERENCES.md']:
        assert (ROOT / path).read_bytes().startswith(prior(path)), path
        assert '2826684' in (ROOT / path).read_text()
    return dict(status='PASS', scope='Source/count and input/state preservation checks only; not economic verification or TEST admission',
                source_pages=43, source_sha256=SOURCE_SHA, prior_record_preserved=True,
                other_prior_records_unchanged=len(paths) - 1, ng_archive_original_pairs_matching=10,
                source_count_checks=['387-53=334', '334-63=271', 'TableXIII271/153and0.84/1.26and1.40/2.12'],
                full_reviews=1, new_hypotheses=0, new_definitions=0, return_tests=0,
                market_returns_computed=False, independent_economic_verification='not_performed',
                budget=dict(hypotheses=4, definitions=10), lease=None,
                trial_history_sha256=hashlib.sha256(json.dumps(p['trials'], sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                root_trials_sha256=sha(ROOT / 'TRIALS.csv'))


if __name__ == '__main__':
    result = audit()
    (BASE / 'checks.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
