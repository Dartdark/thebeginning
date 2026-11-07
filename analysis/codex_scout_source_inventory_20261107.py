"""Read-only input identity/schema audit. Never calculate signals or market returns."""
from pathlib import Path
import csv
import hashlib
import io
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory():
    baseline = json.loads((ROOT / 'agents/codex/inputs/scout_20261106/owned_input_inventory.json').read_text())
    common = []
    for old in baseline['files']:
        path = ROOT / old['path']
        row = dict(old, exists=path.is_file())
        if row['exists']:
            row.update(bytes=path.stat().st_size, sha256=sha(path))
            row['matches_previous_hash'] = row['sha256'] == old['sha256']
        else:
            row['matches_previous_hash'] = False
        common.append(row)
    archives = []
    required = ['Open_Interest_All', 'Lev_Money_Positions_Long_All', 'Lev_Money_Positions_Short_All']
    for year in range(2018, 2023):
        path = ROOT / f'data/cot/fut_fin_txt_{year}.zip'
        with zipfile.ZipFile(path) as archive:
            names = [n for n in archive.namelist() if n.lower().endswith('.txt')]
            assert len(names) == 1, names
            with archive.open(names[0]) as handle:
                reader = csv.DictReader(io.TextIOWrapper(handle, encoding='utf-8-sig'))
                columns = reader.fieldnames
                matched = [row for row in reader if row['CFTC_Contract_Market_Code'].strip() in {'133741', '1330E1'}]
        venues = []
        for code, venue in [('133741', 'CME'), ('1330E1', 'CBOE')]:
            selected = [row for row in matched if row['CFTC_Contract_Market_Code'].strip() == code]
            dates = [row['Report_Date_as_YYYY-MM-DD'].strip() for row in selected]
            venues.append(dict(code=code, venue=venue, rows=len(selected), unique_snapshot_dates=len(set(dates)),
                               first_snapshot=min(dates) if dates else None, last_snapshot=max(dates) if dates else None,
                               market_names=sorted({row['Market_and_Exchange_Names'].strip() for row in selected})))
        archives.append(dict(path=str(path.relative_to(ROOT)), sha256=sha(path), archive_member=names[0],
                             venues=venues, required_fields_present=all(c in columns for c in required),
                             actual_publication_timestamp_field_present=any('publish' in c.lower() or 'release' in c.lower() for c in columns)))
    prices = []
    for year in range(2018, 2023):
        path = ROOT / f'data/BTC_1min_{year}.csv'
        with path.open() as handle:
            columns = handle.readline().strip().split(',')
        prices.append(dict(path=str(path.relative_to(ROOT)), sha256=sha(path), bytes=path.stat().st_size, columns=columns))
    return dict(scope='Identity/schema/snapshot-date audit only. No signals, price outcomes, native contract/roll completeness or publication-vintage admission.',
                market_returns_computed=False, prior_selected_files=common, bitcoin_cot_archives=archives, bitcoin_price_files=prices,
                source_identity_caution='Baur/Smales Section2.2 combines CME and size-adjusted CBOE positions. These separate venue counts are not a reconstructed combined signal. Micro-BTC is excluded.',
                publication_clock_evidence='agents/codex/inputs/scout_20261103/access.json: holiday/backlog releases prevent a universal Tuesday+3 rule.')


if __name__ == '__main__':
    print(json.dumps(inventory(), indent=2))
