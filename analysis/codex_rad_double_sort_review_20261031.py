"""Source arithmetic and header-only input audit; NO market-return or account test.

Run with /workspace/venvs/thebeginning/bin/python analysis/codex_rad_double_sort_review_20261031.py
Only the uploaded source claims and constructed mathematical examples enter the arithmetic.
Owned market CSVs are opened only to read headers; no price observations or returns are read.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'agents/codex/inputs/rad_double_sort_20261031'
OUTPUT = ROOT / 'analysis/outputs/codex_rad_double_sort_20261031'


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    claims = json.loads((INPUT / 'claims.json').read_text())
    baseline = claims['baseline']
    total = baseline['sum_reported_returns_pct'] / 100
    years = (date.fromisoformat(claims['data_end']) -
             date.fromisoformat(claims['first_reported_portfolio_day'])).days / 365.2425
    whole = next(x for x in claims['overlays'] if x['name'] == 'whole portfolio cumulative 5%')
    arithmetic = {
        'evidence_status': 'Deterministic checks only; no historical returns reproduced',
        'source_sum_in_decimal_units': total,
        'one_plus_source_sum': 1 + total,
        'reported_chart_endpoint': baseline['reported_dollar_one_endpoint'],
        'exponential_of_source_sum_if_valid_portfolio_log_returns': math.exp(total),
        'calendar_years_approx': years,
        'chart_endpoint_implied_cagr_pct_if_actual_wealth':
            (baseline['reported_dollar_one_endpoint'] ** (1 / years) - 1) * 100,
        'warning': 'Neither the exponential nor endpoint CAGR is a corrected strategy backtest; '
                   'a self-financing contract/cash/fee ledger is absent.',
        'whole_portfolio_stop_author_claim_deltas': {
            'annual_excess_return_pp': whole['annual_excess_return_pct'] - baseline['annual_excess_return_pct'],
            'annual_vol_pp': whole['annual_vol_pct'] - baseline['annual_vol_pct'],
            'annual_vol_relative_pct': (whole['annual_vol_pct'] / baseline['annual_vol_pct'] - 1) * 100,
            'var_30day_99_pp': whole['var_30day_99_pct'] - baseline['var_30day_99_pct'],
            'var_30day_99_relative_pct': (whole['var_30day_99_pct'] / baseline['var_30day_99_pct'] - 1) * 100,
        },
        'carry_example_actual_log_ratio_pct':
            math.log(claims['carry_example']['front'] / claims['carry_example']['deferred']) * 100,
        'constructed_identity_examples_not_trading_results': {
            'equal_weight_long_simple_returns': [0.10, -0.10],
            'actual_one_period_portfolio_log_return': math.log(1 + 0.5 * 0.10 + 0.5 * -0.10),
            'weighted_instrument_log_returns': 0.5 * math.log(1.10) + 0.5 * math.log(0.90),
            'negative_underlying_log_return_if_underlying_gains_ten_pct': -math.log(1.10),
            'log_of_collateral_after_one_times_notional_short_loses_ten_pct': math.log(0.90),
        },
        'new_economic_definitions': 0,
        'new_return_trials': 0,
        'account_simulations': 0,
    }
    headers = []
    for path in sorted((ROOT / 'data').rglob('*.csv')):
        with path.open(newline='', encoding='utf-8-sig', errors='replace') as handle:
            header = next(csv.reader(handle), [])
        headers.append({'path': str(path.relative_to(ROOT)), 'fields': header})
    commodities = {}
    for symbol in ('CL', 'GC'):
        paths = sorted((ROOT / 'data').glob(f'{symbol}_1min_*.csv'))
        commodities[symbol] = {
            'files': [str(p.relative_to(ROOT)) for p in paths],
            'years_in_filenames_not_coverage_verification': [p.stem.rsplit('_', 1)[-1] for p in paths],
            'headers': sorted({tuple(x['fields']) for x in headers if x['path'] in
                               {str(p.relative_to(ROOT)) for p in paths}}),
            'identified_front_second_panel': False,
        }
    inventory = {
        'scope': 'All CSV headers under repository data/; no prices read. Other named workspace '
                 'data roots and paired-contract filename hits were checked separately in the access receipt.',
        'commodity_outright_files': commodities,
        'all_csv_headers': headers,
        'limitations': 'Filename years do not prove complete sessions, clocks or usable history. '
                      'OHLCV without maturity IDs/expiry/front-second quotes cannot supply the carry signal. '
                      'This audit does not assert that no suitable data exist anywhere.',
    }
    source_manifest = {
        'checked_codex_head_at_start': 'dac4c32c0fbaf60703e7f2fc5d89ff471b92f398',
        'python': sys.version,
        'python_executable': sys.executable,
        'run_code_sha256': sha256(Path(__file__)),
        'run_parent_commit': subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'files': {str(p.relative_to(ROOT)): {'bytes': p.stat().st_size, 'sha256': sha256(p)}
                  for p in sorted(INPUT.iterdir()) if p.is_file()},
        'source_permission': 'owned_upload',
        'source_provenance': 'User upload sediment://file_00000000bba88230be98dccd0617e41f',
        'full_text_read': True,
        'page_count': 56,
        'visually_checked_pdf_pages': [22, 26, 28, 47],
        'not_a_preregistration_or_return_run': True,
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, obj in [('arithmetic.json', arithmetic), ('owned_headers.json', inventory),
                      ('manifest.json', source_manifest)]:
        (OUTPUT / name).write_text(json.dumps(obj, indent=2) + '\n')
    print(json.dumps({'one_plus_sum': arithmetic['one_plus_source_sum'],
                      'exp_sum_not_verified_wealth': math.exp(total),
                      'endpoint_implied_cagr_pct_not_corrected_result':
                          arithmetic['chart_endpoint_implied_cagr_pct_if_actual_wealth'],
                      'whole_stop_claim_deltas': arithmetic['whole_portfolio_stop_author_claim_deltas'],
                      'carry_example_log_ratio_pct': arithmetic['carry_example_actual_log_ratio_pct'],
                      'csv_headers_inspected': len(headers), 'economic_trials': 0}, indent=2))


if __name__ == '__main__':
    main()
