"""Produce a metadata-only shopping list. No networking, keys, SDK, market data or returns.

This is an acquisition specification, not a trading-rule preregistration.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / 'analysis/outputs/codex_auction_vendor_comparison'


def main():
    common = dict(dataset='ARCX.PILLAR', symbols=['SPY'], schema='imbalance',
                  stype_in='raw_symbol')
    design = dict(common, start='2018-01-01T00:00:00Z', end='2023-01-01T00:00:00Z')
    sample = dict(common, start='2026-07-01T00:00:00Z', end='2026-07-03T00:00:00Z')
    requests = [dict(method='metadata.get_dataset_range', parameters=dict(dataset='ARCX.PILLAR'),
                     purpose='Inspect schema.imbalance start/end; not proof of SPY completeness'),
                dict(method='metadata.get_dataset_condition', parameters=dict(
                    dataset='ARCX.PILLAR', start_date='2018-01-01', end_date='2022-12-31'),
                     purpose='Dataset-level quality calendar; not a SPY event census')]
    for name, query in [('design_all_day', design), ('matched_public_sample_days', sample)]:
        for method in ('metadata.get_record_count', 'metadata.get_cost'):
            requests.append(dict(method=method, parameters=query.copy(), scope=name,
                                 purpose='Estimate only, not a download or paid batch job'))
    with (REPO / 'analysis/outputs/codex_spy_close_evidence/budget.json').open() as stream:
        budget = json.load(stream)
    result = dict(status='NEEDS DATA', return_trials=0, api_calls_executed=0,
                  credentials_read=False, accounts_created=False, purchases=False,
                  scope='unexecuted metadata request specifications only',
                  requests=requests,
                  periods_are_acquisition_scopes_not_strategy_parameters=True,
                  time_scope='All-day SPY for simple estimates; intraday cuts need calendar/DST-aware requests',
                  price_scope='No verified Databento, BMLL or SpiderRock SPY quote',
                  nyse_commercial_reference=dict(per_content_month=budget['recorded_list_per_month'],
                     design_months=60, design_2018_2022=budget['recorded_design_list_cost']),
                  quote_requirements=[
                      'SPY listing on Arca; original disseminated closing updates, not final snapshots',
                      'History beginning 2018-01-01; enumerate unavailable months before any purchase',
                      'All-in one-time price, minimum spend, subscription, licence, retention and research-use rights',
                      'Exchange and vendor capture timestamps; customer receipt is a different clock',
                      'Sequence fields, historical mappings, quantity basis and auction-time timezone corrections',
                      'Separate cost for SPY auction results/corrections, SPY NBBO and ES executable quotes',
                      'Free comparison sample if offered; no automatic sample purchase or trial'
                  ])
    assert all(r['parameters'].get('symbols', ['SPY']) == ['SPY'] for r in requests)
    assert all(r['method'].startswith('metadata.') for r in requests)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'quote_spec.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('Wrote unexecuted SPY-only metadata specifications; no network, credentials or returns.')


if __name__ == '__main__':
    main()
