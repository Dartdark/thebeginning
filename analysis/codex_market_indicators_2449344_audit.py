"""Source receipt and reported Sharpe units; no market data, fitted model or returns."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'agents/codex/inputs/market_indicators_2449344'
OUT = ROOT / 'analysis/outputs/codex_market_indicators_2449344'


def main():
    assert subprocess.check_output(['pdftotext', '-layout', str(SOURCE/'paper.pdf'), '-']) == (SOURCE/'paper.txt').read_bytes()
    files = [SOURCE/name for name in ['paper.pdf', 'paper.txt', 'table13.png']] + [Path(__file__)]
    rows = {
        'NYSE total short sales, robust Table13': dict(frequency='weekly', n=1788, buy_hold_display=-.17, strategy_display=2.47, sharpe_difference_t=1.89, alpha_t=1.99),
        'NYSE weekly advances, robust Appendix4': dict(frequency='weekly', n=1843, buy_hold_display=2.01, strategy_display=3.54, sharpe_difference_t=2.16, alpha_t=2.31),
        'NYSE weekly net new highs, robust Appendix4': dict(frequency='weekly', n=1929, buy_hold_display=2.52, strategy_display=4.35, sharpe_difference_t=2.42, alpha_t=2.57),
    }
    for row in rows.values():
        row['source_sharpe_multiplier'] = .01
        row['buy_hold_period_sharpe'] = row['buy_hold_display']*.01
        row['strategy_period_sharpe'] = row['strategy_display']*.01
    assert abs(rows['NYSE total short sales, robust Table13']['strategy_period_sharpe']-.0247) < 1e-12
    receipt = {
        'title': 'Technical Market Indicators: An Overview',
        'authors': ['Jiali Fang', 'Yafeng Qin', 'Ben Jacobsen'],
        'source_file_id': 'file_000000007fcc81fda18ade14a36cf0d1',
        'source_version': 'Undated uploaded manuscript; PDF metadata created 2014-10-23, not an authenticated publication date',
        'review_date': '2026-11-08 America/Los_Angeles', 'pages': 64,
        'scope': 'Main narrative Sections1-7, selected methods/results tables and Appendix4 inspected; Table13 visually inspected; not every table/figure/reference independently audited',
        'hashes': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        'author_reported_OLS_screen_counts': {'indicators': 93, 'full_sample_p_lt_0_10': 30, 'both_halves': 10, 'stable_indication': 8, 'economic_outperformance': 0},
        'author_assumed_switch_cost_decimal': .001,
        'selected_reported_exceptions_not_reproduced': rows,
        'new_economic_trials': 0, 'strategy_returns_computed': False,
        'verdict': 'DONT_TEST_WEAK_SELECTED_EXCEPTIONS_RETAIN_NEGATIVE_EVIDENCE',
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'source_audit.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({'source_integrity': 'PASS', 'Table13_weekly_Sharpe': .0247, 'return_trials': 0}))


if __name__ == '__main__':
    main()
