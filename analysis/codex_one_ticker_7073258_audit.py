"""Published-table arithmetic and source receipt; no historical returns or strategy fit."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'agents/codex/inputs/one_ticker_7073258'
OUT = ROOT / 'analysis/outputs/codex_one_ticker_7073258'


def main():
    assert subprocess.check_output(['pdftotext', '-layout', str(SOURCE/'paper.pdf'), '-']) == (SOURCE/'paper.txt').read_bytes()
    rows = [dict(universe=26, sharpe=1.36, cagr_pct=34.1, max_dd_pct=-18.6,
                 ex_nvda_sharpe=1.13, ex_nvda_cagr_pct=23.0, ex_nvda_dd_pct=-19.2),
            dict(universe=99, sharpe=1.53, cagr_pct=41.3, max_dd_pct=-13.4,
                 ex_nvda_sharpe=1.05, ex_nvda_cagr_pct=23.2, ex_nvda_dd_pct=-16.7)]
    for row in rows:
        row['cagr_edge_with_nvda_pp'] = round(row['cagr_pct']-20.8, 2)
        row['cagr_edge_without_nvda_pp'] = round(row['ex_nvda_cagr_pct']-20.8, 2)
        assert row['ex_nvda_sharpe'] < 1.30
    # Derived from Appendix A.1, without executing its strategy or price data:
    # first scheduled rebalance is index[window]; all earlier targets become zero.
    warmup_rows = {window: window for window in [20, 100, 250]}
    files = [SOURCE/'paper.pdf', SOURCE/'paper.txt', Path(__file__)]
    receipt = {
        'title': "One Ticker Deep: The Trend Strategy That Passed Every Test and Still Shouldn't Be Believed",
        'author': 'Prashant Malan', 'source_draft': 'July 2026',
        'source_file_id': 'file_000000002f0481fda3754fe3376ca4a1',
        'review_date': '2026-11-08 America/Los_Angeles', 'pages': 20,
        'scope': 'All extracted narrative, tables and appendices read; code statically inspected, not executed; figure captions read, figures not independently digitized',
        'hashes': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        'author_reported_walk_forward_not_reproduced': rows,
        'SPY_same_OOS_reported': dict(sharpe=1.30, cagr_pct=20.8, max_dd_pct_approx=-24),
        'appendix_A1_initial_all_cash_rows_derived': warmup_rows,
        'author_grid_cells': 9*4,
        'source_assumed_cost_per_unit_gross_turnover': .0005,
        'source_in_sample_counterexamples': dict(worst_grid_dd_pct=-35.7, SPY_full_sample_dd_pct=-33.8,
                                                 broad_high_vol_bucket_dd_pct=-38.6,
                                                 original_medium_vol_sharpe=.84, SPY_full_sample_sharpe=.76),
        'new_economic_trials': 0, 'strategy_returns_computed': False,
        'verdict': 'ATTRIBUTION_METHOD_REFERENCE_NO_NEW_ALPHA_ADMISSION',
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'source_audit.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({'source_integrity': 'PASS', 'reported_ex_NVDA_below_SPY': True, 'return_trials': 0}))


if __name__ == '__main__':
    main()
