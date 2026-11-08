"""Source-claim transcription, arithmetic and prior-file receipts; no market-return test."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'agents/codex/inputs/delgado_7323419'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = (BASE / 'full_text.txt').read_text()
    for term in ('1,989', '2110.6%', '38.49%', '40.87%', '99.999986796%', '0.809'):
        assert term in source, term
    partitions = math.comb(10, 5)
    # Consistency only; not a reproduction of CSCV rankings or DSR without daily series.
    assert round(100 * 97 / partitions, 2) == 38.49
    assert round(100 * 103 / partitions, 2) == 40.87
    previous = ['analysis/beat_the_market_es_test.py',
        'analysis/outputs/beat_the_market_es_test_output.txt',
        'agents/codex/results/s03_v2.md', 'agents/codex/results/s03_noisearea.md',
        'agents/codex/results/s03_noisearea_independent_review.md',
        'agents/codex/results/noise15_20261103.md']
    report = {'scope': 'SOURCE CLAIMS AND PRIOR EVIDENCE ONLY; NO NEW BACKTEST',
        'financial_trials': 0, 'new_strategy_code_built': False,
        'source_written': '2026-08-20', 'ssrn_posted': '2026-08-21',
        'source_claims': {
            'original_paper_window': {'start': '2007-05', 'end': '2024-04',
                'independent_total_return_pct': 1989., 'annual_return_pct': 19.6,
                'sharpe': 1.317, 'max_dd_pct': -24.5, 'trades': 7742,
                'convention': 'Closest paper match omits dividend adjustment; not final engine'},
            'exact_post_publication': {'start': '2024-05-13', 'end': '2025-08-29',
                'total_return_pct': 23.3, 'sharpe': 1.284},
            'recent_weak': {'start': '2025-09-02', 'end': '2026-08-14',
                'total_return_pct': -8.1, 'sharpe': -.461, 'max_dd_pct': -17.4},
            'full_baseline': {'total_return_pct': 3753.5, 'cagr_pct': 14.7,
                'sharpe': .996, 'max_dd_pct': -24.6},
            'selected_retrospective': {'start_valid': '2000-01-25', 'end': '2026-08-14',
                'total_return_pct': 2110.6, 'cagr_pct': 12.4, 'sharpe': 1.274,
                'max_dd_pct': -14.8, 'entries': 4170, 'clean_holdout': False},
            'search': {'all_ledger_rows': 129, 'spy_selection_alternatives': 80,
                'pre_fix': 31, 'corrected': 49, 'reconstructed_daily_series': 70,
                'pbo_scope': '25-point PRE_VWAP_FIX grid only, not selected 80-trial adaptive search',
                'pbo_historical_pct': 38.49, 'pbo_common_valid_pct': 40.87,
                'selected_dsr_pct': 99.999986796, 'dsr_reproduced_here': False},
            'qqq_sharpe': {'base': .987, 'spy_config_j': .809, 'spy_volume': .913,
                           'spy_performance_overlay': .967},
            'iwm_base_sharpe': .450},
        'arithmetic_only': {'cscv_partitions': partitions, 'historical_pbo_implied_count': 97,
                           'common_valid_pbo_implied_count': 103},
        'prior_evidence_transcription': {
            'es_proxy_sharpe_lb14_paper_costs': 1.30,
            'es_proxy_sharpe_lb14_futures_costs': .83,
            's03_v2_50k_funded_add1_year1_change_usd': -348.5,
            's03_v2_personal_equal_dd_profit_change_usd': -484,
            'warning': 'Different strategies/conventions and historical books; not tests of Delgado final'},
        'owned_minute_equity_filename_candidates': [str(p.relative_to(ROOT)) for p in (ROOT/'data').rglob('*')
            if p.is_file() and any(t in p.name.lower() for t in ('spy', 'qqq', 'iwm'))
            and any(t in p.name.lower() for t in ('1min', 'minute', 'intraday'))],
        'input_hashes': {str(p.relative_to(ROOT)): digest(p) for p in BASE.iterdir() if p.is_file()},
        'prior_hashes': {name: digest(ROOT / name) for name in previous},
        'code_sha256': digest(Path(__file__))}
    output = ROOT / 'analysis/outputs/codex_delgado_7323419/source_audit.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'financial_trials': 0, 'source_claims_only': True,
                      'owned_minute_filename_candidates': report['owned_minute_equity_filename_candidates']}))


if __name__ == '__main__':
    main()
