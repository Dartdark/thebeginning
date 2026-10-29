"""Hash and inventory acquired research files. No market returns are calculated."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'agents/codex/inputs/scout_acquisition_20261029'


def inventory():
    files = []
    for path in sorted(BASE.rglob('*')):
        if not path.is_file() or 'licensed_raw' in path.relative_to(BASE).parts:
            continue
        if not path.resolve().is_relative_to(BASE.resolve()):
            raise ValueError('Acquisition file is a symlink outside its bundle')
        record = {'path': path.relative_to(ROOT).as_posix(), 'bytes': path.stat().st_size,
                  'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        if path.suffix == '.csv':
            with path.open(encoding='utf-8-sig', newline='') as handle:
                reader = csv.DictReader(handle)
                record['columns'] = reader.fieldnames
                record['rows'] = sum(1 for _ in reader)
        elif path.suffix == '.json':
            json.loads(path.read_text(encoding='utf-8'))
        files.append(record)
    return {'schema_version': 1, 'recorded_at': datetime.now(timezone.utc).isoformat(),
            'bundle': BASE.relative_to(ROOT).as_posix(),
            'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'files': files,
            'limits': 'File/row counts and hashes only. A CSV may be a specification, retrospective example or '
                      'secondary inventory; counts must not be pooled as usable signal observations. '
                      'No source truth, historical availability, financial eligibility or economic result is certified.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = inventory()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'inventoried_files': len(result['files']), 'output': str(args.output),
                      'scope': 'input-file metadata only; no returns'}))
