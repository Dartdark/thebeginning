"""One bounded public acquisition of oats/OJ histories; no return calculations.

These bytes are NOT a source-compatible22market portfolio or admitted execution
history. Keep them local; contract clocks, fields and roll meaning need review.
"""
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'agents/codex/inputs/scout_20261101/free_daily_panel'
REF = '164328bd76d2937d3dd61491377704c488283bc2'
FILES = {'OATIES.csv': 'b0a0887e5d965c8633fa738cfdac43272eea1ec8',
         'OJ.csv': '788df7aff828f13749fa1178a705a14ea7b74c9e'}


def main():
    out = OUT / 'local/carver'
    out.mkdir(parents=True, exist_ok=True)
    receipts = []
    for name, expected in FILES.items():
        url = f'https://raw.githubusercontent.com/pst-group/pysystemtrade/{REF}/data/futures/multiple_prices_csv/{name}'
        with urllib.request.urlopen(url, timeout=40) as response:
            data = response.read(8 * 1024 * 1024 + 1)
            if len(data) > 8 * 1024 * 1024: raise ValueError('size cap')
            blob = hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
            if blob != expected: raise ValueError('source blob hash changed')
            dest = out / name
            dest.write_bytes(data)
        with dest.open(newline='') as file:
            reader = csv.reader(file)
            header = next(reader)
            rows = 0
            first = last = None
            missing = [0] * len(header)
            for row in reader:
                if first is None: first = row[0]
                last = row[0]
                rows += 1
                for i, cell in enumerate(row):
                    missing[i] += int(not cell.strip() or cell.strip().lower() in {'nan', 'na', 'null'})
        receipts.append({'name': name, 'url': url, 'local_path': str(dest.relative_to(ROOT)),
                         'bytes': len(data), 'git_blob_sha1': blob, 'sha256': hashlib.sha256(data).hexdigest(),
                         'rows': rows, 'first_label': first, 'last_label': last,
                         'columns': header, 'empty_cells': dict(zip(header, missing))})
    result = {'retrieved_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'commit': REF,
              'repository': 'pst-group/pysystemtrade', 'files': receipts,
              'scope': 'schema/date/missing-cell counts only; no returns or signal calculations',
              'raw_files_git_tracked': False,
              'admission': 'NOT ADMITTED: do not splice publishers or assume native clocks, return construction, contract definitions, data rights, complete22market history or successful strategy.'}
    (OUT / 'missing_commodity_acquisition.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
