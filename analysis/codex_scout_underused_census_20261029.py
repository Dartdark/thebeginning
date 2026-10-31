"""Reproduce this scout cycle's source counts and filename census; never read prices."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SCOUT = ROOT / 'agents/codex/research/scout'
RECEIPT = SCOUT / 'runs/20261029_underused_access.json'


def main():
    receipt = json.loads(RECEIPT.read_text(encoding='utf-8'))
    records = [json.loads((ROOT / p).read_text(encoding='utf-8'))
               for p in receipt['paper_records']]
    assert all(r['new_economic_trials'] == 0 for r in records)
    assert all(r['return_eligibility'] != 'TEST' for r in records)
    assert sum(r['full_text_read'] for r in records) == receipt['full_source_reviews']
    # Filenames only, including ignored owned inputs. COT archives are not contract prices.
    candidates = []
    pattern = re.compile(r'^(?:LE|HE|ZC|ZS|GF|CT|KC|SB|CC)[_.-]', re.I)
    for base in (ROOT / 'data', ROOT / 'agents/codex/inputs'):
        for path in base.rglob('*'):
            if path.is_file() and pattern.search(path.name):
                candidates.append(path.relative_to(ROOT).as_posix())
    progress = json.loads((SCOUT / 'progress.json').read_text(encoding='utf-8'))
    files = [RECEIPT, Path(__file__)] + [ROOT / p for p in receipt['paper_records']]
    result = {
        'schema_version': 1,
        'run_id': receipt['run_id'],
        'source_full_reviews': sum(r['full_text_read'] for r in records),
        'metadata_only_records': sum(not r['full_text_read'] for r in records),
        'return_tests_executed': False,
        'economic_definitions_executed': sum(r['new_economic_trials'] for r in records),
        'named_underused_input_matches': sorted(candidates),
        'filename_census_limit': 'Prefix search only; no price/return values read. Does not '
                                'certify all possible aliases, data completeness or permissions.',
        'program_hypotheses_started': progress['hypotheses_started'],
        'program_economic_definitions': progress['economic_definitions'],
        'prior_trial_history_sha256': hashlib.sha256((ROOT / 'TRIALS.csv').read_bytes()).hexdigest(),
        'retained_metadata_hashes': {
            p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in files
        },
        'source_original_hash_limit': 'Metadata hashes are not original PDF/data hashes or economic verification.',
    }
    output = ROOT / 'analysis/outputs/codex_scout_underused_census_20261029.json'
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('source_full_reviews', 'metadata_only_records',
                     'return_tests_executed', 'economic_definitions_executed',
                     'named_underused_input_matches')}))


if __name__ == '__main__':
    main()
