"""Extract author-reported Table8; no market-data reads, trades or return tests."""
from pathlib import Path
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'agents/codex/inputs/ng_paper_3575861'
OUT = ROOT / 'analysis/outputs/codex_ng_3575861_source_audit'


def main():
    text = (SOURCE / 'paper.txt').read_text()
    table = text.split('Table 8: Returns on Investment Strategy', 1)[1].split('5.3 Limits to Arbitrage', 1)[0]
    rows = []
    pattern = r'Raw(?P<cost> \(-90,30\)| \+ TC \+ FC| \+ TC)\s+(?P<ret>-?\d+\.\d+)\s+\((?P<p>\d+\.\d+)\)\s+(?P<sr>-?\d+\.\d+)'
    for panel, period in [('A', 'Whole Sample'), ('B', 'Before 2011'), ('C', 'After 2011')]:
        section = table.split(f'Panel {panel}: {period}', 1)[1].split('Panel ', 1)[0]
        for match in re.finditer(pattern, section):
            rows.append(dict(panel=panel, period=period, costs=match['cost'].strip(),
                             reported_annual_return_pct=float(match['ret']),
                             reported_pvalue=float(match['p']), reported_sharpe=float(match['sr']),
                             evidence='author_reported_not_reproduced', pdf_page=19))
    assert len(rows) == 9
    recent = [r for r in rows if r['panel'] == 'C' and r['costs'] == '+ TC + FC'][0]
    assert recent['reported_annual_return_pct'] == -0.97
    assert recent['reported_sharpe'] == -0.17
    OUT.mkdir(exist_ok=True, parents=True)
    with (OUT / 'author_table8.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    record = dict(source_pdf_sha256=hashlib.sha256((SOURCE / 'paper.pdf').read_bytes()).hexdigest(),
                  source_text_sha256=hashlib.sha256((SOURCE / 'paper.txt').read_bytes()).hexdigest(),
                  author_table8_rows=len(rows), latest_panel=recent, new_economic_trials=0,
                  market_data_read=False, strategy_returns_computed=False,
                  disposition='DONT_TEST_source_evidence_gate',
                  limits=['Author estimates are not independently reproduced',
                          'Negative later estimate is not proof of negative expected returns today',
                          'After2011 is the author label; sample ends December2018',
                          'No native contract/cost or portfolio benefit inferred'])
    (OUT / 'source_audit.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
