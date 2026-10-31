"""No-return schema audit for a potential two-maturity futures strategy."""
import csv
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    records = []
    for path in sorted((ROOT / 'data').glob('*_1min_2018.csv')):
        with path.open(encoding='utf-8-sig', newline='') as f:
            fields = next(csv.reader(f))
        names = {x.strip().lower() for x in fields}
        records.append({'path': path.relative_to(ROOT).as_posix(), 'columns': fields,
                        'has_contract_identifier': bool(names & {'contract', 'contract_id',
                            'contractname', 'symbol', 'security_id', 'instrument_id'}),
                        'has_bid_ask_fields': any(re.search(r'(^|_)bid($|_)', x) for x in names)
                            and any(re.search(r'(^|_)ask($|_)', x) for x in names)})
    cot = []
    for filename in ('deacot2018.zip', 'fut_fin_txt_2018.zip'):
        path = ROOT / 'data/cot' / filename
        with zipfile.ZipFile(path) as z:
            member = z.namelist()[0]
            with z.open(member) as f:
                fields = next(csv.reader([f.readline().decode('utf-8-sig')]))
        cot.append({'path': path.relative_to(ROOT).as_posix(), 'member': member,
                    'column_count': len(fields),
                    'has_index_trader_field': any('index' in f.lower() for f in fields)})
    result = {'schema_version': 1, 'scope': 'Names/headers only; no market rows/returns',
              'named_2018_exports': records, 'cot_schemas': cot,
              'return_eligibility': 'NEEDS DATA', 'return_tests_executed': False,
              'new_economic_definitions': 0,
              'limit': 'Schema observations do not certify contract identity, history coverage, '
                       'absence of differently named data, permissions or economic value.',
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    path = ROOT / 'analysis/outputs/codex_spread_strategy_inputs_20261029.json'
    path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'exports_inspected': len(records), 'cot_schemas': len(cot),
                      'return_tests_executed': False, 'eligibility': 'NEEDS DATA'}))


if __name__ == '__main__':
    main()
