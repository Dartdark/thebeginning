"""Audit existing input identities and headers; never calculate market outcomes."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
BASELINE = 'agents/codex/inputs/scout_20261107/owned_input_inventory.json'


def inventory():
    old = json.loads((ROOT / BASELINE).read_text())
    files = []
    for prior in old['prior_selected_files']:
        path = ROOT / prior['path']
        row = dict(prior, exists=path.is_file())
        row['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        row['matches_previous_hash'] = row['sha256'] == prior['sha256']
        files.append(row)
    metadata = []
    for relative in [
        'data/macro_proxies_daily.csv',
        'agents/codex/inputs/scout_acquisition_20261029/fx_calendar/primary_release_calendar_2018_2022.csv',
    ]:
        path = ROOT / relative
        with path.open() as handle:
            header = handle.readline().strip().split(',')
        metadata.append(dict(path=relative, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), columns=header))
    return dict(scope='Selected existing raw-file identity and macro/calendar header recheck only; no signals, returns or source-specific admission.',
                market_returns_computed=False, baseline=BASELINE, files=files, macro_calendar_headers=metadata,
                limitation='Market-price proxies and release-date facts contain neither the source Bloomberg median consensus nor actual first-release values/receipt timestamps. No missing observations filled.')


if __name__ == '__main__':
    print(json.dumps(inventory(), indent=2))
