"""Bounded public reference collection, not licensed trading history or vendor APIs.

Default: list only. --download collects exact official documents/SDK fixture below.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / 'agents/codex/inputs/auction_data_sources_20261025'
OUT = REPO / 'analysis/outputs/codex_auction_sample_intake'
PIN = '82f76c1de6f5c8a1f4b3711fac423f88a3f91d67'
SOURCES = {
    'taq_spec_2.4a.pdf': 'https://www.nyse.com/publicdocs/nyse/data/TAQ_XDP_Products_Client_Spec_v2.4a.pdf',
    'imbalance_feed_spec_2.2n.pdf': 'https://www.ice.com/publicdocs/nyse/data/NYSE_Pillar_Order_Imbalances_Client_Specification_v2.2n.pdf',
    'nyse_calendar_2026.pdf': 'https://www.nyse.com/publicdocs/nyse/ICE_NYSE_2026_Yearly_Trading_Calendar.pdf',
    'databento_test_data.imbalance.dbn': 'https://raw.githubusercontent.com/databento/dbn/' + PIN + '/tests/data/test_data.imbalance.dbn',
    'databento_dbn_LICENSE.txt': 'https://raw.githubusercontent.com/databento/dbn/' + PIN + '/LICENSE',
    'bmll_auction_schema.pdf': 'https://www.bmlltech.com/files/documents/BMLL-Auction-Imbalance.pdf',
    'spiderrock_imbalance_schema.html': 'https://docs.spiderrockconnect.com/docs/HistoricalData/Data%20Dictionaries/StockExchImbalance/',
    'databento_arca_schema.html': 'https://databento.com/docs/datasets/arcx-pillar',
    'bmll_sample_index.html': 'https://www.bmlltech.com/products/bmll-data-feed/documentation',
    'massive_noi_schema.html': 'https://massive.com/docs/websocket/stocks/imbalances',
}
FIXTURE_HASHES = {
    'databento_test_data.imbalance.dbn': 'bbdec3ce93e1aea8f2c971aa55dcccd765fd82579c782d5650bfa99cfff7fc8e',
    'databento_dbn_LICENSE.txt': 'd3174ad63e721d4c9dccb8ad4320848992d314369bc46319720b5802c9153fe9',
}


def collect(download=False, names=None):
    records = []
    for name, url in SOURCES.items():
        if names and name not in names:
            continue
        record = dict(url=url, name=name, purpose='reference only; not SPY research history')
        if download:
            folder = ROOT / ('fixtures' if name.startswith('databento') else 'documents')
            folder.mkdir(parents=True, exist_ok=True)
            dest = folder / name
            if dest.exists():
                data = dest.read_bytes()
                record['acquisition'] = 'existing original preserved'
            else:
                try:
                    with urllib.request.urlopen(url, timeout=30) as response:
                        data = response.read(10_000_001)
                except (OSError, ValueError) as exc:
                    record.update(acquisition='not downloaded', error=str(exc))
                    records.append(record)
                    continue
                if len(data) > 10_000_000:
                    raise ValueError('Reference exceeds 10MB limit')
                if name.endswith('.pdf') and not data.startswith(b'%PDF-'):
                    raise ValueError('Expected a PDF: ' + url)
                digest = hashlib.sha256(data).hexdigest()
                if name in FIXTURE_HASHES and digest != FIXTURE_HASHES[name]:
                    raise ValueError('Pinned fixture hash mismatch')
                with dest.open('xb') as f:
                    f.write(data)
                record['acquisition'] = 'downloaded'
            digest = hashlib.sha256(data).hexdigest()
            if name in FIXTURE_HASHES and digest != FIXTURE_HASHES[name]:
                raise ValueError('Existing pinned fixture hash mismatch; original preserved')
            dest.chmod(0o444)
            record.update(path=dest.relative_to(REPO).as_posix(), bytes=len(data),
                          sha256=digest, original_read_only=True,
                          checked_at_utc=datetime.now(timezone.utc).isoformat())
        else:
            record['acquisition'] = 'located only'
        records.append(record)
    if download:
        OUT.mkdir(parents=True, exist_ok=True)
        manifest = OUT / 'reference_manifest.json'
        previous = json.loads(manifest.read_text(encoding='utf-8'))['sources'] if manifest.exists() else []
        combined = {r['name']: r for r in previous}
        combined.update({r['name']: r for r in records})
        manifest.write_text(json.dumps(dict(return_trials=0, sources=list(combined.values())), indent=2) + '\n', encoding='utf-8')
    return records


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--names', nargs='+', choices=sorted(SOURCES))
    args = parser.parse_args()
    print(json.dumps(collect(args.download, args.names), indent=2))
