"""Collect only named free NYSE samples; default is a dry listing. No vendor APIs or trading.

python analysis/codex_collect_auction_samples.py --download-nyse --dates 20260701
Outputs stay in a research input directory, never a live trading path.
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import urllib.request

BASE = 'https://ftp.nyse.com/Historical%20Data%20Samples/TAQ%20NYSE%20ARCA%20ORDER%20IMBALANCES/'
EXPECTED = {'20260701': 115017342, '20260702': 126487758}
MAX_BYTES = 200_000_000


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def check_gzip(path):
    # Bounded expansion protects against a corrupt or unexpected compressed file.
    total = 0
    with gzip.open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            total += len(chunk)
            if total > 10_000_000_000:
                raise ValueError('Unexpected gzip expansion exceeds 10GB')
    return total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download-nyse', action='store_true')
    parser.add_argument('--dates', nargs='+', choices=sorted(EXPECTED), default=['20260701'])
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1] / 'agents/codex/inputs/auction_data_sources_20261025/nyse_samples'
    for day in args.dates:
        name = f'EQY_US_ARCA_REF_IMBALANCES_{day}.gz'
        url = BASE + name
        if not args.download_nyse:
            print(json.dumps(dict(url=url, listed_bytes=EXPECTED[day],
                                  status='dry listing; no download requested',
                                  local_file_exists=(root / name).exists())))
            continue
        root.mkdir(parents=True, exist_ok=True)
        dest = root / name
        partial = root / (name + '.part')
        if not dest.exists():
            if partial.exists():
                raise FileExistsError('Existing partial file preserved: ' + str(partial))
            try:
                with urllib.request.urlopen(url, timeout=30) as response:
                    length = response.headers.get('Content-Length')
                    if length and int(length) > MAX_BYTES:
                        raise ValueError('File exceeds 200MB download limit')
                    with partial.open('xb') as f:
                        count = 0
                        for chunk in iter(lambda: response.read(1024 * 1024), b''):
                            count += len(chunk)
                            if count > MAX_BYTES:
                                raise ValueError('File exceeds 200MB download limit')
                            f.write(chunk)
                if partial.stat().st_size != EXPECTED[day]:
                    raise ValueError('Size differs from inspected NYSE listing; review source before retry')
                expanded = check_gzip(partial)
                partial.replace(dest)
            except Exception:
                # Python 3.7 is still the default interpreter on the research PC.
                try:
                    partial.unlink()
                except FileNotFoundError:
                    pass
                raise
        else:
            if dest.stat().st_size != EXPECTED[day]:
                raise ValueError('Existing file size mismatch; original preserved')
            expanded = check_gzip(dest)
        dest.chmod(0o444)
        record = dict(url=url, bytes=dest.stat().st_size, sha256=sha256(dest),
                      checked_at_utc=datetime.now(timezone.utc).isoformat(),
                      gzip_integrity='passed', uncompressed_bytes=expanded,
                      original_read_only=True,
                      symbol_and_schema_validation='not performed; see separate intake audit', return_trials=0)
        manifest = dest.with_suffix('.manifest.json')
        manifest.write_text(json.dumps(record, indent=2) + '\n')
        print(json.dumps(record))


if __name__ == '__main__':
    main()
