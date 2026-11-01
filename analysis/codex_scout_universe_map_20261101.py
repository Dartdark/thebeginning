"""Map source2671165's named27commodities to the new public panel.

Names/coverage only: no price transformations, rankings or strategy outcomes.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'agents/codex/inputs/scout_20261101/free_daily_panel'
# Accepted manuscriptp8 (PDFp9), original universe. No substitutes for missing contracts.
SOURCE = {
    'cocoa': 'CC1 Comdty', 'coffee C': 'KC1 Comdty', 'corn': 'C 1 Comdty',
    'cotton no2': 'CT1 Comdty', 'frozen concentrated orange juice': None,
    'oats': None, 'rough rice': None, 'soybean meal': 'SM1 Comdty',
    'soybean oil': 'BO1 Comdty', 'soybeans': 'S 1 Comdty',
    'sugar no11': 'SB1 Comdty', 'wheat': 'W 1 Comdty',
    'electricity': None, 'gasoline': 'XB1 Comdty', 'heating oil no2': 'HO1 Comdty',
    'light sweet crude oil': 'CL1 Comdty', 'natural gas': 'NG1 Comdty',
    'feeder cattle': 'FC1 Comdty', 'frozen pork bellies': None,
    'lean hogs': 'LH1 Comdty', 'live cattle': 'LC1 Comdty',
    'copper': 'HG1 Comdty', 'gold': 'GC1 Comdty', 'palladium': 'PA1 Comdty',
    'platinum': 'PL1 Comdty', 'silver': 'SI1 Comdty', 'random length lumber': None,
}


def main():
    acquisition = json.loads((INPUT / 'acquisition_and_coverage.json').read_text())
    with (INPUT / 'local/tf_system_data_descriptive_df.csv').open() as f:
        metadata = {row['ticker']: row for row in csv.DictReader(f)}
    missing = [name for name, key in SOURCE.items() if key is None or key not in metadata]
    matched = {name: {'ticker': key, 'coverage': acquisition['coverage'][key],
                     'mapping_status': 'tentative economic name, not native contract certification'}
               for name, key in SOURCE.items() if key in metadata}
    result = {'source_id': 'ssrn:2671165', 'source_version': 'Accepted manuscript dated2017-06-21,p8',
              'source_universe_count': len(SOURCE), 'tentative_matches': len(matched),
              'missing': missing, 'matched': matched,
              'source_input_gap': 'Source rolls from front to second one month before maturity; acquired panel has no separately identified delivery legs or dated roll ledger. HO2 and gasoline historical specification transitions not certified.',
              'disposition': 'NOT ADMITTED. No survivor-only subset or synthetic missing contracts were tested.',
              'economic_hypotheses_added': 0, 'economic_definitions_added': 0,
              'returns_computed': False}
    out = ROOT / 'analysis/outputs/codex_scout_universe_map_20261101'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'source_universe_map.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'matched'}, indent=2))


if __name__ == '__main__':
    main()
