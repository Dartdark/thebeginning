"""Schema/provenance inventory only. Does not compute returns, signals or rankings."""
from pathlib import Path
import csv
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'agents/codex/inputs/scout_20261102/owned_input_inventory.json'

def main():
    files = []
    for symbol in ('ES','NQ','GC','CL','6E'):
        for year in (2018,2022):
            p = ROOT / f'data/{symbol}_1min_{year}.csv'
            if not p.exists():
                files.append({'path':str(p.relative_to(ROOT)), 'exists':False})
                continue
            with p.open(encoding='utf-8-sig',newline='') as f:
                header = next(csv.reader(f))
            files.append(dict(path=p.relative_to(ROOT).as_posix(),exists=True,bytes=p.stat().st_size,
                              columns=header,sha256=hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),
                              history_status='filename_and_schema_only; calendar/roll/clock admission not implied',permission='owned_export'))
    ng = json.loads((ROOT/'agents/codex/inputs/ng_corrected_20261031/manifest.json').read_text())
    for row in ng:
        if row['year'] not in (2018,2022):continue
        p=ROOT/row['archive']
        with gzip.open(p,'rt') as f:header=next(csv.reader(f))
        actual=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
        files.append(dict(path=row['archive'],exists=True,columns=header,bytes=p.stat().st_size,sha256=actual,
                          matches_manifest=actual==row['archive_sha256'],permission=row['permission'],
                          provenance=row['provenance'],history_status='schema/archive-hash check; not native clock/roll admission'))
    p=ROOT/'data/OF_1min_2018_1.csv'
    with p.open(newline='') as f:header=next(csv.reader(f))
    files.append(dict(path=p.relative_to(ROOT).as_posix(),columns=header,bytes=p.stat().st_size,
                      availability='NQ minute aggregates only; no cross-asset20-market tick OFI, 10ms tape, or quote-event clock is inferred'))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(dict(scope='input schema/hash only',market_returns_computed=False,
        note='Selected 2018/2022 files locate owned fields; existence is not proof of complete design coverage or quote/fill/native permission.',files=files),indent=2)+'\n')
    print(f'Saved {len(files)} schema entries; zero returns or economic definitions.')

if __name__=='__main__':main()
