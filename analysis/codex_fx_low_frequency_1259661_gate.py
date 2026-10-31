"""Bounded no-return source/data feasibility census; never scores price signals."""
from pathlib import Path
import csv
import datetime as dt
import hashlib
import io
import json
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_fx_low_frequency_1259661_gate'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    owned = [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'data').rglob('*'))
             if p.is_file() and re.search(r'(^|/)(6[ABCEJSN]|FX|DEX|EXCHANGE)[_.]',
                                         str(p.relative_to(ROOT)), re.I)]
    access = []
    urls = [
        'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXUSEU',
        'https://raw.githubusercontent.com/datasets/exchange-rates/main/data/daily.csv',
        'https://data.bis.org/topics/CBPOL',
        'https://raw.githubusercontent.com/datasets/exchange-rates/main/README.md',
    ]
    for i, url in enumerate(urls):
        row = dict(url=url, purpose='public metadata/data sample only; no strategy returns')
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'Research data feasibility'})
            with urllib.request.urlopen(request, timeout=20) as response:
                data = response.read(24000001)
                row.update(status=response.status, final_url=response.url,
                           sampled_bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                           content_type=response.headers.get('Content-Type'),
                           truncated=len(data) > 24000000)
                path = OUT / f'access_{i}.sample'
                path.write_bytes(data)
                row['sample_path'] = str(path.relative_to(ROOT))
                if i == 1:
                    rows = list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'))))
                    row['columns'] = list(rows[0]) if rows else []
                    date_col = next((c for c in row['columns'] if c.lower() == 'date'), None)
                    if date_col:
                        dates = [r[date_col] for r in rows if r.get(date_col)]
                        row.update(min_date=min(dates) if dates else None,
                                   max_date=max(dates) if dates else None,
                                   rows=len(rows))
                    countries = sorted({r.get('Country', '') for r in rows})
                    row['country_date_coverage'] = {}
                    for country in countries:
                        dates = [r[date_col] for r in rows if r.get('Country') == country and r.get(date_col)]
                        row['country_date_coverage'][country] = dict(rows=len(dates), first=min(dates), last=max(dates))
        except Exception as exc:
            row.update(error_type=type(exc).__name__, error=str(exc))
        access.append(row)
    result = dict(checked_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                  source_pdf_sha256=hashlib.sha256((ROOT / 'agents/codex/inputs/ssrn1259661/source.pdf').read_bytes()).hexdigest(),
                  owned_fx_filename_matches=owned, access=access, economic_trials=0,
                  limitations='Filename census and bounded public-source intake only. Public reference spots and policy rates '
                              'are not the original Reuters spots and Datastream money-market carry. No matched '
                              '1986 warm-up, nine-currency spot/carry execution panel verified.',
                  verdict='NEEDS DATA AND SOURCE CONVENTIONS')
    (OUT / 'gate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
