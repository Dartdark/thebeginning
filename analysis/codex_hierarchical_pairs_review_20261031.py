"""Source-only arithmetic and schema receipts. No historical price/return calculation."""
from pathlib import Path
import csv
import hashlib
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'agents/codex/inputs/hierarchical_pairs_20261031'
OUT = ROOT / 'analysis/outputs/codex_hierarchical_pairs_review_20261031'


def main():
    claims = json.loads((SOURCE / 'claims.json').read_text())
    experimental = claims['experimental']
    sample = [1., 2., 3., 4.]
    mean = sum(sample) / len(sample)
    audit = {
        'evidence': 'Source arithmetic and invented mathematical examples; not an economic test',
        'five_calendar_year_cagr_pct_if_cumulative_claim_is_wealth':
            ((1 + experimental['cumulative_return_pct']/100)**(1/5)-1)*100,
        'years_implied_if_annual_return_claim_is_cagr':
            math.log1p(experimental['cumulative_return_pct']/100) /
            math.log1p(experimental['annual_return_pct']/100),
        'warning': 'Exact experimental start and annualization convention need a daily ledger; '
                   'these are conditional consistency checks, not corrected backtest returns.',
        'constructed_standard_deviation_example': {
            'values': sample, 'mean': mean,
            'sqrt_mean_unsquared_deviations': math.sqrt(sum(x-mean for x in sample)/len(sample)),
            'actual_population_sd': math.sqrt(sum((x-mean)**2 for x in sample)/len(sample))},
        'constructed_covariance_parameter_example': {
            'delta_not_author_setting': 0.1,
            'printed_delta_over_delta_minus_one': 0.1/(0.1-1),
            'note': 'Negative multiple of identity is not a covariance; actual author code unknown'},
        'new_return_trials': 0, 'account_simulations': 0,
        'constructed_hedge_reestimation_example': {
            'X_previous_and_current': 100, 'Y_previous_and_current': 100,
            'beta_previous': 1, 'beta_current': 0.9,
            'residual_previous': 0, 'residual_current': 10,
            'held_book_price_pnl_before_costs': 0,
            'note': 'A redefined residual can move without any held-position gain. '
                    'This is not an allegation about the unavailable author implementation.'},
    }
    headers = {}
    for name in ('NQ_1min_2018.csv', 'ES_1min_2018.csv', 'GC_1min_2018.csv', 'CL_1min_2018.csv', 'ZN_1min_2018.csv'):
        path = ROOT / 'data' / name
        with path.open() as f: headers[name] = next(csv.reader(f))
    inventory = {'scope': 'Owned data/ filenames and representative CSV headers only; no price rows read',
                 'filenames': [str(p.relative_to(ROOT)) for p in sorted((ROOT/'data').rglob('*')) if p.is_file()],
                 'representative_headers': headers,
                 'matching_selected_chinese_exchange_files': [],
                 'limits': 'No CCFX/XSGE/XDCE/XZCE selected panel identified. ZN in our data is US Treasury, '
                           'not the source ZN8888.XSGE zinc contract. No cross-venue substitute admitted.'}
    manifest = {'python': sys.version, 'python_executable': sys.executable,
                'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'files': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(SOURCE.iterdir()) if p.is_file()},
                'full_text_read': True, 'pdf_pages': 38, 'visually_checked_pages': [19,20,23,26,31],
                'source_permission': 'owned_upload',
                'source_pointer': 'sediment://file_00000000ed1c823087e08340b9bd47e0'}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, obj in [('arithmetic.json', audit), ('owned_input_receipt.json', inventory), ('manifest.json', manifest)]:
        (OUT/name).write_text(json.dumps(obj, indent=2)+'\n')
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    main()
