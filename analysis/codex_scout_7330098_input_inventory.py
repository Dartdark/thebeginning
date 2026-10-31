"""Reproduce the expiry-paper input inventory; no price/return calculations."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ('data/GEX_1min_*.csv', 'data/GEXOI_*.csv', 'data/OF_1min_*.csv')
BOUNDARIES = ('data/GEX_1min_2022.csv', 'data/GEX_1min_2023.csv',
              'data/GEX_1min_2026.csv', 'data/GEXOI_2022.csv', 'data/GEXOI_2026.csv')
HASH_PATHS = ('data/GEX_1min_2022.csv', 'data/GEXOI_2022.csv', 'data/OF_1min_2018_1.csv',
              'tools/exporters/OFB_GexOI_Exporter.txt', 'tools/exporters/OFB_Gamma_Exporter.txt',
              'agents/codex/results/flow_evidence_sheets.md', 'analysis/spx_gex_sample_test.py')


def inventory(root=ROOT):
    root = Path(root)
    families = []
    for pattern in FAMILIES:
        schemas = {}
        count = 0
        for path in sorted(root.glob(pattern)):
            with path.open(encoding='utf-8-sig', newline='') as handle:
                columns = tuple(next(csv.reader(handle)))
            schemas.setdefault(columns, []).append(path.relative_to(root).as_posix())
            count += 1
        families.append({'glob': pattern, 'file_count': count,
                         'schemas': [{'columns': list(columns), 'files': paths} for columns, paths in schemas.items()]})
    boundaries = []
    for relative in BOUNDARIES:
        with (root / relative).open(encoding='utf-8-sig', newline='') as handle:
            rows = csv.DictReader(handle)
            first = last = None
            count = 0
            for row in rows:
                stamp = [row['date'], row['time']]
                if first is None:
                    first = stamp
                last = stamp
                count += 1
        boundaries.append({'path': relative, 'rows': count, 'first': first, 'last': last})
    return {'families': families, 'selected_boundaries': boundaries,
            'selected_file_sha256': {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in HASH_PATHS},
            'options_sample_directory_present': (root / 'scratch_data/options_sample').is_dir(),
            'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'python': sys.executable,
            'limits': 'Headers, date/time boundaries and hashes only. No numeric prices, returns or economic tests. '
                      'Schema inventory does not certify field provenance or dealer inventory semantics.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    rendered = json.dumps(inventory(), indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding='utf-8')
    else:
        print(rendered, end='')
