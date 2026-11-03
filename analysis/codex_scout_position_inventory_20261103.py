"""Owned COT field/coverage inventory only; no signals, prices or return tests."""
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'agents/codex/inputs/scout_20261103/position_inventory.json'
MARKETS = {
    'CL': ('067651', 'CRUDE OIL, LIGHT SWEET - NEW YORK MERCANTILE EXCHANGE'),
    'GC': ('088691', 'GOLD - COMMODITY EXCHANGE INC.'),
    'NG': ('023651', 'NATURAL GAS - NEW YORK MERCANTILE EXCHANGE'),
}
FIELDS = ['Open Interest (All)', 'Commercial Positions-Long (All)',
          'Commercial Positions-Short (All)', 'Noncommercial Positions-Long (All)',
          'Noncommercial Positions-Short (All)']


def main():
    receipts = []
    for year in range(2018, 2023):
        p = ROOT / f'data/cot/deacot{year}.zip'
        item = dict(path=p.relative_to(ROOT).as_posix(), exists=p.exists())
        if not p.exists():
            receipts.append(item)
            continue
        item.update(bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
        with zipfile.ZipFile(p) as z:
            item['archive_members'] = z.namelist()
            if z.namelist() != ['annual.txt']:
                raise ValueError(f'Unexpected archive schema: {p}')
            with z.open('annual.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                item['columns'] = reader.fieldnames
                assert set(FIELDS).issubset(reader.fieldnames)
                rows = list(reader)
        item['markets'] = []
        for symbol, (code, name) in MARKETS.items():
            selected = [r for r in rows if r['CFTC Contract Market Code'].strip() == code]
            dates = sorted(r['As of Date in Form YYYY-MM-DD'].strip() for r in selected)
            invalid = sum(not math.isfinite(float(r[k].replace(',', ''))) or
                          float(r[k].replace(',', '')) < 0 for r in selected for k in FIELDS)
            item['markets'].append(dict(symbol=symbol, reference_name_2018=name, rows=len(selected),
                observed_names=sorted({r['Market and Exchange Names'].strip() for r in selected}),
                date_min=dates[0] if dates else None, date_max=dates[-1] if dates else None,
                unique_dates=len(set(dates)), duplicate_dates=len(dates)-len(set(dates)),
                market_codes=sorted({r['CFTC Contract Market Code'].strip() for r in selected}),
                invalid_selected_numeric_cells=invalid))
        item['release_or_receipt_field'] = [c for c in item['columns']
            if any(w in c.lower() for w in ('release', 'publish', 'receipt'))]
        receipts.append(item)
    result = dict(scope='owned schema, archive hash and position-date coverage only',
        signals_computed=False, market_returns_computed=False, economic_definitions=0,
        fields=FIELDS, files=receipts,
        limits=['Position dates do not establish actual public-release or receipt dates.',
                'Legacy aggregate futures-only reports do not identify individual orders, option positions or DCOT groups.',
                'Three overlapping markets are not the source 26-market portfolio.',
                'No dated futures legs, source roll construction or native cash/fill ledger admitted.'])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'archives':len(receipts), 'market_rows':sum(m['rows'] for r in receipts
        for m in r.get('markets', [])), 'returns_computed':False, 'out':str(OUT.relative_to(ROOT))}))


if __name__ == '__main__':
    main()
