"""Source integrity and reported-table arithmetic only; no return backtest."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'agents/codex/inputs/crossover_6684499'
OUT = ROOT / 'analysis/outputs/codex_crossover_6684499'


def main():
    assert subprocess.check_output(['pdftotext', '-layout', str(SOURCE/'paper.pdf'), '-']) == (SOURCE/'paper.txt').read_bytes()
    files = [SOURCE/name for name in ['paper.pdf', 'paper.txt', 'table3.png']] + [Path(__file__)]
    receipt = {
        'title': 'Backtesting and Analysis of a Quantitative Trading Strategy: A Case Study in Moving Average Crossovers and Portfolio Diversification',
        'author': 'Zachary B. Arnold', 'source_date': 'April 27, 2026',
        'source_file_id': 'file_00000000104c81fd9df094afec11896d',
        'review_date': '2026-11-08 America/Los_Angeles', 'pages': 34,
        'scope': 'All extracted narrative, tables and references read; Table3 visually inspected; remaining charts not independently digitized; no original code/data or empirical replication',
        'hashes': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        'author_reported_table3_not_reproduced': dict(strategy_annual_return_pct=12.04, benchmark_annual_return_pct=17.27,
            strategy_sharpe=.779, benchmark_sharpe=.849, strategy_max_dd_pct=-25.79, benchmark_max_dd_pct=-35.23,
            daily_difference_t=-2.169, p_value=.030, positive_day_rate_pct=52.10),
        'arithmetic': dict(annual_return_gap_pp=round(12.04-17.27, 2), shallower_drawdown_pp=round(35.23-25.79, 2)),
        'author_table5_OOS_sharpe_pairs_strategy_benchmark': {'AAPL': [.900, 1.112], 'MSFT': [1.120, .982],
            'JPM': [.329, .541], 'XOM': [.580, .487], 'JNJ': [-.163, .332]},
        'assumed_source_fee_per_side_decimal': .001,
        'source_return_definition': '(1 + mean daily return)^252 - 1; not geometric path CAGR',
        'new_economic_trials': 0, 'strategy_returns_computed': False,
        'verdict': 'DONT_TEST_RETAIN_NEGATIVE_EVIDENCE',
    }
    assert receipt['arithmetic']['annual_return_gap_pp'] == -5.23
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'source_audit.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({'source_integrity': 'PASS', 'annual_return_gap_pp': -5.23, 'return_trials': 0}))


if __name__ == '__main__':
    main()
