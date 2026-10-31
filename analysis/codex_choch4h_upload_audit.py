"""Audit uploaded CSV coverage without parsing OHLC or calculating returns."""
import argparse
import hashlib
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()


def audit(paths):
    rows = []
    for path in paths:
        x = pd.read_csv(path, usecols=['date', 'time'])
        original = ROOT / 'data' / path.name
        checksum = digest(path)
        rows.append(dict(
            filename=path.name, sha256=checksum, rows=len(x),
            first_date=int(x.date.min()), last_date=int(x.date.max()),
            min_time=int(x.time.min()), max_time=int(x.time.max()),
            rows_1701=int(x.time.eq(1701).sum()),
            rows_after_1700=int(x.time.gt(1700).sum()),
            existing_identical=original.exists() and digest(original) == checksum,
            prices_parsed=False, new_return_trials=0,
        ))
    return pd.DataFrame(rows).sort_values('filename')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', type=Path, nargs='+')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.files)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        result.to_csv(stream, index=False)
    print(result.to_string(index=False))
