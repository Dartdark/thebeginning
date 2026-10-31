"""No-return input/access census for the uploaded WASDE volume paper."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_wasde_4841490_gate'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    matches = []
    for path in sorted((ROOT / 'data').rglob('*')):
        if path.is_file() and re.search(
            r'(^|[/_])(ZC|ZS|ZW|ZL|ZM|ZO|CORN|SOYBEANS|WHEAT|COTTON|WASDE)([/_.]|$)',
            str(path.relative_to(ROOT)), re.I
        ):
            matches.append(str(path.relative_to(ROOT)))
    access = []
    for url in [
        'https://www.usda.gov/oce/commodity/wasde',
        'https://www.cmegroup.com/market-data/volume-open-interest/agriculture-commodities.html',
    ]:
        row = {'url': url, 'purpose': 'public source/product feasibility, not historical-data completeness'}
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Research source feasibility'})
            with urllib.request.urlopen(req, timeout=20) as response:
                data = response.read(250000)
                row.update(status=response.status, final_url=response.url,
                           sampled_bytes=len(data), sampled_sha256=hashlib.sha256(data).hexdigest())
        except Exception as exc:
            row.update(error_type=type(exc).__name__, error=str(exc))
        access.append(row)
    pdf = ROOT / 'agents/codex/inputs/ssrn4841490/source.pdf'
    result = dict(checked_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                  source_pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
                  owned_filename_matches=matches, access=access,
                  limitations='Filename census only; no contract-level futures/options volume panel verified. '
                              'Public page availability would not establish a historical dataset or licence.',
                  economic_trials=0, verdict='NEEDS DATA AND SPECIFICATION; no return test')
    (OUT / 'gate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
