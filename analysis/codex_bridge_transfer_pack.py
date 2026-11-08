"""Package the five already-audited Bridge research exports without altering them.

Python 3.7+ stdlib only. No network, strategy engine, DLL, config or trading access.
Destination must be new. Hashes must match the committed acquisition receipt.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / 'analysis/outputs/codex_bridge_history_20261108_audit.json'
NAMES = ['NQ_1min_native_ET_close_%d.csv' % y for y in range(2018, 2023)]


def digest(path, compressed=False):
    h = hashlib.sha256()
    opener = gzip.open if compressed else open
    with opener(str(path), 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def package(source, destination, expected, receipt_sha):
    source, destination = Path(source), Path(destination)
    if destination.exists():
        raise FileExistsError('Refusing existing destination: %s' % destination)
    # Validate all originals before creating output. Missing/wrong input leaves no output directory.
    for name in NAMES:
        p = source / name
        if p.stat().st_size != expected[name]['bytes'] or digest(p) != expected[name]['sha256']:
            raise ValueError('Source differs from committed audit: %s' % name)
    destination.mkdir(parents=True, exist_ok=False)
    records = {}
    for name in NAMES:
        src, dst = source / name, destination / (name + '.gz')
        with src.open('rb') as inp, dst.open('xb') as raw:
            with gzip.GzipFile(filename='', mode='wb', fileobj=raw, compresslevel=6, mtime=0) as out:
                shutil.copyfileobj(inp, out, 1024 * 1024)
        if digest(dst, compressed=True) != expected[name]['sha256']:
            raise ValueError('Compressed round-trip mismatch: %s' % name)
        if digest(src) != expected[name]['sha256']:
            raise ValueError('Source changed during packaging: %s' % name)
        records[dst.name] = {'compressed_sha256': digest(dst), 'compressed_bytes': dst.stat().st_size,
                            'original_sha256': expected[name]['sha256'], 'original_bytes': expected[name]['bytes']}
    manifest = {'status': 'PACKAGED_NOT_RESEARCH_ADMITTED', 'acquisition_receipt_sha256': receipt_sha,
                'symbol': 'NQ.v.0 as reported by source', 'timezone': 'America/New_York',
                'bar_timestamp': 'minute close; do not add another minute', 'calendar_years': [2018, 2019, 2020, 2021, 2022],
                'fields': ['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'UpVol', 'DownVol'],
                'source_claim': 'Volume total; UpVol buyer-initiated; DownVol seller-initiated, per acquisition manual',
                'limits': ['roll/build provenance unverified', 'historical receipt/corrections unknown',
                           'session gaps retained', 'not native PowerLanguage up-tick Volume', 'no returns computed'],
                'files': records}
    with (destination / 'transfer_manifest.json').open('x') as f:
        json.dump(manifest, f, indent=2)
        f.write('\n')
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default=r'C:\CodexRepo\scratch_data\codex_bridge_20261108_01')
    parser.add_argument('--destination', default=str(ROOT / 'agents/codex/inputs/bridge_native_2018_22_20261108'))
    args = parser.parse_args()
    receipt = json.loads(RECEIPT.read_text())
    manifest = package(args.source, args.destination, receipt['exports'], digest(RECEIPT))
    print('Packaged %d verified research files into %s' % (len(manifest['files']), args.destination))
    print('No original file changed. Review and commit only this new research directory.')


if __name__ == '__main__':
    main()
