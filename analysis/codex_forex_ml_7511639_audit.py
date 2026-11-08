"""Source receipt and reported-number reconciliation only; no market data or returns."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'agents/codex/inputs/forex_ml_7511639'
OUT = ROOT / 'analysis/outputs/codex_forex_ml_7511639'


def main():
    pdf = SOURCE / 'paper.pdf'
    extracted = subprocess.check_output(['pdftotext', '-layout', str(pdf), '-'])
    assert extracted == (SOURCE / 'paper.txt').read_bytes()
    text = extracted.decode()
    assert '0.9987' in text and '0.9873' in text
    info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
    pages = int(next(line.split(':', 1)[1] for line in info.splitlines() if line.startswith('Pages:')))
    reported_r = 0.9987
    reported_univariate_r2 = 0.9873
    record = {
        'title': 'Machine Learning versus Econometric Forecasting in the Forex Market: Evidence from EUR/USD, GBP/USD, and USD/CAD',
        'author': 'Shadia Saeed Alqahtani',
        'review_date_utc': '2026-11-08',
        'source_version': 'User upload; no manuscript version date printed; PDF metadata creation 2026-09-23 is not a publication date',
        'source_file_id': 'file_00000000d95c81fda93959940bfeaa82',
        'pages': pages,
        'scope': 'All extracted narrative, tables and references read; figure captions read, figure pixels not independently audited; no cited-study or empirical replication',
        'hashes': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in [pdf, SOURCE / 'paper.txt', Path(__file__)]},
        'reported_claims_not_reproduced': {
            'RF_volume_classification_accuracy_pct': {'EUR/USD': 85, 'GBP/USD': 82, 'USD/CAD': 78},
            'GBM_risk_reduction_pct': {'EUR/USD': 20, 'GBP/USD': 18, 'USD/CAD': 15},
            'ARIMA_accuracy_range_pct': [48, 65],
        },
        'arithmetic_reconciliation': {
            'source': 'Section 4.3: Open versus 26-day moving average',
            'reported_correlation': reported_r,
            'correlation_squared': reported_r ** 2,
            'reported_univariate_R_squared': reported_univariate_r2,
            'absolute_gap': abs(reported_r ** 2 - reported_univariate_r2),
            'condition': 'Same observations and ordinary simple regression with intercept imply R squared equals Pearson r squared; unexplained sample/estimator differences could change the comparison',
        },
        'new_economic_trials': 0,
        'strategy_returns_computed': False,
        'verdict': 'DONT_TEST_SOURCE_EVIDENCE_INSUFFICIENT',
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'source_audit.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'pages': pages, 'correlation_squared': reported_r ** 2,
                      'reported_R_squared': reported_univariate_r2, 'return_trials': 0}))


if __name__ == '__main__':
    main()
