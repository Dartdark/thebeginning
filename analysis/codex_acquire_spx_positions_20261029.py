"""Audit the public SPX acquisition packet; never fetches paid data or runs returns.

The single rounded publisher example is a retrospective illustration, not an
intraday dealer book. This checker cannot promote it into a strategy input.
"""
import argparse
import csv
from datetime import date
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = Path('agents/codex/inputs/scout_acquisition_20261029/spx_positions')


def audit(root=ROOT):
    root = Path(root)
    directory = root / PACKET
    access = json.loads((directory / 'vendor_access.json').read_text(encoding='utf-8'))
    sources = json.loads((directory / 'sources.json').read_text(encoding='utf-8'))
    with (directory / 'public_approx_eod_example.csv').open(encoding='utf-8', newline='') as handle:
        examples = list(csv.DictReader(handle))
    for row in examples:
        if (row['approximate'] != 'true' or row['is_raw_capacity_record'] != 'false' or
                row['is_reconstructed_inventory'] != 'false' or row['is_intraday_received_signal'] != 'false'):
            raise ValueError('A rounded public illustration cannot be treated as raw/as-of dealer inventory')
        if int(row['mm_buy_contracts_approx']) - int(row['mm_sell_contracts_approx']) != int(row['mm_net_contracts_approx']):
            raise ValueError('Public illustration arithmetic differs')
        if date.fromisoformat(row['publication_date']) <= date.fromisoformat(row['event_date']) or row['available_at']:
            raise ValueError('This retrospective illustration must not acquire a fabricated pre-entry clock')
    with (directory / 'required_fields.csv').open(encoding='utf-8', newline='') as handle:
        requirements = list(csv.DictReader(handle))
    if len({row['field'] for row in requirements}) != len(requirements):
        raise ValueError('Duplicate required fields')
    if not all(row['status'] == 'required_not_acquired' for row in requirements):
        raise ValueError('Changed acquisition status needs a separate evidence review')
    offer = access['free_sample_offer']
    if offer['period_start'] != '2022-07-01' or offer['period_end'] != '2022-12-31' or offer['is_any_selectable_six_months']:
        raise ValueError('Current fixed-period sample terms were changed')
    if any([offer['activated'], access['contacts_sent'], access['orders_placed'], access['paid_trials_started'],
            access['new_accounts_or_keys'], access['money_spent_usd']]):
        raise ValueError('This packet must not imply an account, contact, entitlement or purchase')
    raw_files = [p for p in (directory / 'licensed_raw').rglob('*') if p.is_file()]
    if raw_files:
        raise ValueError('New licensed raw files require separate entitlement, provenance and data review')
    files = [p for p in sorted(directory.iterdir()) if p.is_file()]
    return {
        'schema_version': 1,
        'status': 'NEEDS DATA',
        'acquired_raw_capacity_rows': 0,
        'acquired_reconstructed_book_rows': 0,
        'public_rounded_eod_example_rows': len(examples),
        'return_eligible_rows': 0,
        'required_fields_not_acquired': len(requirements),
        'no_return_calculations': True,
        'no_accounts_contacts_orders_or_purchases': True,
        'source_count': len(sources['new_public_sources']),
        'source_dates_are_not_receipt_times': True,
        'fixed_trial_period': [offer['period_start'], offer['period_end']],
        'sha256': {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'limits': 'Arithmetic/schema/provenance audit only. One publisher example is not a raw inventory dataset. '
                  'No source truth, complete history, actual delivery, signed book or economic merit is independently certified.'
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    rendered = json.dumps(audit(), indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding='utf-8')
    else:
        print(rendered, end='')
