"""Audit source claims and identities only; no PSX or CME return backtest."""
from pathlib import Path
import hashlib
import json
import numpy as np


def main():
    root = Path('agents/codex/inputs/kse_sentinel_7102818')
    out = Path('analysis/outputs/codex_kse_sentinel_7102818')
    out.mkdir(parents=True, exist_ok=True)
    p, payoff = .3915, 3.9
    trades = np.array([3., -1., -1., 4., -2.])
    assert trades.sum() == trades[::-1].sum()
    a = {
        'kind': 'author-claim transcription and constructed arithmetic; no financial replication',
        'return_trials': 0,
        'canonical_author_results': {'trades': 1009, 'win_rate': p, 'profit_factor': 2.51,
            'PKR_cagr': .0747, 'USD_cagr': -.0296, 'sharpe': 2.08, 'max_drawdown': -.0291},
        'five_percent_risk_author_results': {'trades': 602, 'win_rate': .3937,
            'PKR_cagr': .0553, 'sharpe': 2.09, 'max_drawdown': -.0268},
        'implied_profit_factor_using_rounded_payoff': p * payoff / (1-p),
        'payoff_implied_by_profit_factor': 2.51 * (1-p) / p,
        'DSR': 'literal source placeholder: [to be confirmed from run_fresh_dsr_analysis.py output]',
        'source_trial_floor': 4,
        'cost_ambiguity': 'abstract: 22.5 bp per leg; section 3.4: 22.5 bp in round-trip costs per leg; 45 vs 22.5 bp total cannot be resolved from prose',
        'illustrative_shuffle_total_invariance': {'original_total': float(trades.sum()),
            'reordered_total': float(trades[::-1].sum()), 'scope': 'Reordering fixed outcomes cannot test whether their sum is positive. Sign flipping tests a different null; source implementation unknown.'},
        'finite_randomization_example': {'exceedances': 0, 'assumed_draws': 1000,
            'plus_one_p_estimate': 1/1001, 'scope': 'Illustration only; actual source number of draws and statistic undisclosed'},
        'source_link_check': {'url': 'https://shorturl.at/n9GTR', 'http_status': 403,
            'result': 'no destination, code, API schema or rule specification obtained'},
    }
    (out/'audit.json').write_text(json.dumps(a, indent=2)+'\n')
    m = {'title': 'KSE Sentinel: A Rule-Based Trend-Continuation Strategy for the Pakistan Stock Exchange (PSX)',
        'author': 'Ertiza Abbas', 'source_date': 'July 2026', 'uploaded_filename': 'ssrn-7102818.pdf',
        'pages': 13, 'pdf_sha256': hashlib.sha256((root/'source.pdf').read_bytes()).hexdigest(),
        'version_caution': 'Public search also found SSRN7093159 with matching title; not substituted for the uploaded version.',
        'table_source': 'Visually transcribed embedded tables on PDF pages 7 and 8',
        'review_date': '2026-11-08', 'network_receipt': 'shortlink_http_receipt.txt',
        'scope': 'full text, rendered tables, bounded public source-link search and arithmetic, no model or return replication'}
    (root/'manifest.json').write_text(json.dumps(m, indent=2)+'\n')
    print(json.dumps(a, indent=2))


if __name__ == '__main__':
    main()
