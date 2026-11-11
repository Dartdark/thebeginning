"""Post-result reporting only. Never fits, selects, replays or reads recent prices."""
from pathlib import Path
import hashlib
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_pressure_study_20261110'
SOURCES = [
 ('impact', 'codex_pressure_build_20261110/batch1_design_qa2', {'RESID2'}),
 ('payoff', 'codex_pressure_learning_20261110', {'RIDGE', 'HGB'}),
 ('resting', 'codex_pressure_build_20261110/passive_design', {'L1', 'L2'}),
 ('common_market', 'codex_pressure_market_20261110', {'FULL'}),
 ('archived_book', 'codex_pressure_book_learning_20261110', {'HGB_BOOK', 'RIDGE_BOOK'}),
 ('long_memory', 'codex_pressure_memory_20261110', {'HGB_MEMORY', 'RIDGE_MEMORY'}),
]


def main():
    rows, receipt = [], {}
    for family, rel, selectable in SOURCES:
        path = ROOT / 'analysis/outputs' / rel / 'results.json'
        if not path.exists():
            if family == 'long_memory':
                continue  # Reserved only; not reported as a completed trial.
            raise FileNotFoundError(path)
        result = json.loads(path.read_text())
        receipt[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        for name, item in result['stats'].items():
            s = item['summary']
            rows.append(dict(batch=family, variant=name, selectable=name in selectable,
                             trades=int(s['trades']), win_percent=100*s['win'],
                             net_per_NQ=s['total'], net_per_MNQ_proxy=item['micro']['total'],
                             gross_per_NQ=s['gross'], cost_per_NQ=s['cost'],
                             net_per_trade_NQ=s['avg'], profit_factor=s['profit_factor'],
                             max_closed_trade_dd_NQ=s['max_dd'], t_trade=s['t_trade'],
                             t_daily_nw5=s['t_nw5'], sharpe=s['sharpe'], sortino=s['sortino'],
                             calmar=s['calmar'], ulcer=s['ulcer'],
                             positive_years=item['positive_years'],
                             four_tick_net_NQ=item.get('stress', {}).get('total'),
                             passive_entry_tick_net_NQ=item.get('entry_tick_stress', {}).get('total'),
                             stop_first_net_NQ=item.get('stop_first', {}).get('total'),
                             selected=False, source_result=str(path.relative_to(ROOT)),
                             prereg=result.get('prereg')))
    table = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT / 'all_definitions.csv', index=False)
    (OUT / 'report_receipt.json').write_text(json.dumps(dict(
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        source_sha256=receipt, definitions_reported=len(table), selected=None,
        period='2018-2022 chronological design', recent_outcomes_read=False,
        account_simulation_run=False, new_economic_definitions=0,
        passive_stress_is_not_four_tick_market_stress=True), indent=2)+'\n')
    print(table[['batch','variant','trades','win_percent','net_per_NQ','profit_factor']].to_string(index=False))


if __name__ == '__main__': main()
