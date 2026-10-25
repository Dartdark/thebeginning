"""Synthetic parser failures and clock checks; no market returns or strategy trials."""
import json
from pathlib import Path
from codex_audit_arca_samples import parse_imbalance, time_ns, clock_views


def main():
    row = '105,100,15:59:59.123456789,SPY,90,100.25,1000,250,50,1600,C,B,100.24,100.26,0,100.25,1100000,900000,0,1,0,0, , '.split(',')
    parsed = parse_imbalance(row)
    checks = {'physical_field_positions': parsed['symbol'] == 'SPY' and parsed['total_imbalance_qty'] == 250,
              'nanoseconds_preserved': parsed['source_ns'] % 10**9 == 123456789,
              'no_invented_market_imbalance_sign': 'signed_market_imbalance' not in parsed}
    invalid = [('extra_column', row + ['0']), ('missing_column', row[:-1])]
    for label, index, value in [('unknown_side', 11, 'X'), ('negative_qty', 7, '-1'),
                                 ('fractional_qty', 7, '1.2'), ('nan_price', 5, 'NaN'),
                                 ('bad_time', 2, '25:00:00.000000001'),
                                 ('bad_auction_time', 9, '1660'), ('bad_freeze', 19, '3')]:
        changed = row.copy()
        changed[index] = value
        invalid.append((label, changed))
    for label, changed in invalid:
        try:
            parse_imbalance(changed)
        except ValueError:
            checks['reject_' + label] = True
        else:
            checks['reject_' + label] = False
    zero = row.copy()
    zero[7], zero[11] = '0', ' '
    checks['zero_is_not_missing'] = parse_imbalance(zero)['total_imbalance_qty'] == 0
    checks['one_nanosecond_order'] = time_ns('15:00:00.000000002') - time_ns('15:00:00.000000001') == 1
    checks['summer_utc_offset'] = clock_views('20260701', row[2])['assumed_utc'].endswith('19:59:59+00:00')
    checks['winter_utc_offset'] = clock_views('20260105', row[2])['assumed_utc'].endswith('20:59:59+00:00')
    checks['summer_ct_offset'] = clock_views('20260701', row[2])['assumed_ct'].endswith('14:59:59-05:00')
    result = dict(return_trials=0, checks=checks, passed=all(checks.values()))
    out = Path(__file__).resolve().parents[1] / 'analysis/outputs/codex_auction_sample_intake'
    out.mkdir(exist_ok=True, parents=True)
    (out / 'synthetic_checks.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    assert result['passed'], 'Intake checks failed'


if __name__ == '__main__':
    main()
