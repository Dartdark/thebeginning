"""Fetch pinned public replication inputs; inspect coverage only, never returns.

Raw vendor-derived data stay local and Git-ignored. No third-party code executes.
Public package availability is not independent certification of vendor rights,
roll construction, historical clocks, native sizing or executable prices.
"""
from pathlib import Path
import csv
import hashlib
import json
import urllib.request
import datetime as dt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'agents/codex/inputs/scout_20261101/free_daily_panel'
REF = '8994f98bc31e954fa65c76c006e59eda266de745'
BASE = 'https://raw.githubusercontent.com/ArturSepp/TrendFollowingSystems/' + REF + '/'
FILES = ['LICENSE', 'README.md', 'src/trendfollowing/universe.py',
         'src/trendfollowing/resources/futures/tf_system_data_descriptive_df.csv',
         'src/trendfollowing/resources/futures/tf_system_data_prices.csv']


def main():
    local = OUT / 'local'
    local.mkdir(parents=True, exist_ok=True)
    receipts = []
    for path in FILES:
        url = BASE + path
        dest = local / Path(path).name
        # One normal permitted HTTPS request; no retry, proxy or credential logic.
        with urllib.request.urlopen(url, timeout=45) as response:
            data = response.read(32 * 1024 * 1024 + 1)
            if len(data) > 32 * 1024 * 1024:
                raise ValueError('size cap')
            dest.write_bytes(data)
            receipts.append({'url': url, 'file': str(dest.relative_to(ROOT)),
                             'status': response.status, 'bytes': len(data),
                             'sha256': hashlib.sha256(data).hexdigest()})
    coverage = {}
    previous = None
    duplicates = 0
    rows = 0
    with (local / 'tf_system_data_prices.csv').open(newline='') as file:
        reader = csv.reader(file)
        header = next(reader)
        for key in header[1:]:
            coverage[key] = {'first_date': None, 'last_date': None, 'nonempty': 0, 'design_nonempty': 0}
        for row in reader:
            day = row[0][:10]
            duplicates += int(day == previous)
            previous = day
            rows += 1
            for key, value in zip(header[1:], row[1:]):
                if value.strip() and value.strip().lower() not in {'nan', 'na', 'null'}:
                    cell = coverage[key]
                    if cell['first_date'] is None: cell['first_date'] = day
                    cell['last_date'] = day
                    cell['nonempty'] += 1
                    cell['design_nonempty'] += int('2018-01-01' <= day <= '2022-12-31')
    result = {'retrieved_at': dt.datetime.now(dt.timezone.utc).isoformat(),
              'repository': 'ArturSepp/TrendFollowingSystems', 'commit': REF,
              'scope': 'public research acquisition and nonempty/date coverage only; NO return calculation or screening',
              'rights': 'Repository MIT software licence and explicit documented public research purpose retained; vendor-derived history not independently licensed/certified. Raw data not redistributed.',
              'raw_files_git_tracked': False, 'return_tests_executed': False,
              'rows': rows, 'columns': len(coverage), 'adjacent_duplicate_date_rows': duplicates,
              'files': receipts, 'coverage': coverage,
              'admission': 'NOT admitted: continuous daily panel; no individual delivery curves, roll ledger, settlement clocks, native contract multipliers/quotes or intraday adverse paths certified.'}
    (OUT / 'acquisition_and_coverage.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ['commit', 'rows', 'columns', 'return_tests_executed', 'admission']}))


if __name__ == '__main__':
    main()
