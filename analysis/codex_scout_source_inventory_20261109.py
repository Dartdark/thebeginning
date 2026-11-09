"""Recheck source-specific owned inputs without constructing signals or returns."""
from pathlib import Path
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
PRIOR = 'agents/codex/inputs/scout_20261108/owned_input_inventory.json'
MACRO = 'agents/codex/inputs/eval_focus_20261109/macro_intake'
NATIVE = 'agents/codex/inputs/bridge_native_2018_22_20261108'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads((ROOT / path).read_text())


def inventory():
    previous = read(PRIOR)
    files = []
    for before in previous['files']:
        path = ROOT / before['path']
        row = dict(before, exists=path.is_file())
        row['sha256'] = digest(path) if path.is_file() else None
        row['matches_previous_hash'] = row['sha256'] == before['sha256']
        files.append(row)
    macro = read(f'{MACRO}/manifest.json')
    macro_files = []
    for name, expected in macro['files'].items():
        relative = f'{MACRO}/snapshot/{name}'
        path = ROOT / relative
        actual = digest(path)
        macro_files.append(dict(path=relative, bytes=path.stat().st_size, sha256=actual,
                                matches_manifest=actual == expected['sha256']))
    catalog = read(f'{MACRO}/snapshot/metadata/series-catalog.json')
    native = read(f'{NATIVE}/transfer_manifest.json')
    native_files = []
    for name, expected in native['files'].items():
        relative = f'{NATIVE}/{name}'
        path = ROOT / relative
        raw = gzip.decompress(path.read_bytes())
        actual = digest(path)
        raw_hash = hashlib.sha256(raw).hexdigest()
        native_files.append(dict(path=relative, sha256=actual, uncompressed_sha256=raw_hash,
                                 columns=raw.splitlines()[0].decode('utf-8-sig').split(','),
                                 matches_manifest=actual == expected['compressed_sha256'] and
                                 raw_hash == expected['original_sha256']))
    sidecars = []
    for relative in [
        f'{MACRO}/manifest.json', f'{NATIVE}/transfer_manifest.json',
        'agents/codex/inputs/eval_focus_20261109/macro_reconciliation/manifest.json',
        'agents/codex/inputs/eval_focus_20261109/macro_reconciliation/clock_sidecar.csv',
        'agents/codex/inputs/eval_focus_20261109/macro_reconciliation/coverage.csv',
        'agents/codex/inputs/gold_clocks_20261108/evidence_matrix.json',
        'agents/codex/inputs/gold_clocks_20261108/design_clock_sidecar.csv',
        'agents/codex/inputs/new_data_20261108/README.md',
    ]:
        path = ROOT / relative
        sidecars.append(dict(path=relative, bytes=path.stat().st_size, sha256=digest(path)))
    return dict(
        scope='Byte identities, header/catalog mapping and existing admission receipts only. No signal or return work.',
        market_returns_computed=False, prior_inventory=PRIOR, prior_files=files,
        macro_files=macro_files, native_files=native_files, sidecars=sidecars,
        macro_series_ids=[row['id'] for row in catalog],
        macro_admitted=macro['admitted_for_strategy_returns'], native_status=native['status'],
        native_clock=native['bar_timestamp'], native_timezone=native['timezone'],
        missing_source_1920401_ten_am_release_families=[
            'consumer confidence', 'ISM/NAPM', 'leading economic indicators', 'factory orders',
            'new home sales', 'construction spending', 'business inventories'],
        mapping_caution='None of those seven source families occurs in the15-series catalog. JOLTS and08:30 releases are not replacements. Source-vintage/receipt admission remains open.',
        other_cautions=[
            'NQ buyer/seller aggregates are not participant identities, event-level orders, LOB depth or PowerLanguage uptick Volume.',
            'UGL/GLL policy clock sidecars are not actual per-date NAV/asset/share publication or reset execution receipts.',
            'BOIL is quarantined; current holdings and synthetic Cboe OHLC do not supply historical futures weights or intraday option surfaces.'])


if __name__ == '__main__':
    print(json.dumps(inventory(), indent=2))
