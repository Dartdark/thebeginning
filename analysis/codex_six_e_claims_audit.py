"""Audit the supplied 6E note's arithmetic and local data headers only.

No price values, signals, strategy returns, backtests or account paths are read
or computed. Reported performance remains an unverified author claim.
"""
from pathlib import Path
import csv
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'agents/codex/inputs/six_e_cross_asset_20261027/research_note.txt'
OUT = ROOT / 'analysis/outputs/codex_six_e_cross_asset_20261027'


def main():
    note = SOURCE.read_text()
    # Values explicitly transcribed from the supplied note; these are not
    # independently reconstructed market results.
    annual = {2018:3266, 2019:1559, 2020:-18, 2021:4022, 2022:6901,
              2023:3341, 2024:1206, 2025:2469, 2026:849}
    legs = {'macro':(2,440), 'rsi':(1,170), 'weekly':(1,270),
            'macro_shock':(2,310), 'stock_shock':(1,210), 'gold_shock':(2,260)}
    assert all(f'{y}' in note for y in annual)
    total = sum(annual.values())
    data = []
    for p in sorted((ROOT/'data').glob('6E_1min_*.csv')):
        with p.open() as f:
            reader=csv.reader(f); header=next(reader); first=next(reader)
        with p.open('rb') as f:
            f.seek(max(0,p.stat().st_size-8192)); last=f.read().decode().splitlines()[-1]
        data.append(dict(path=str(p.relative_to(ROOT)), columns=header,
            first_date_time=first[:2],last_date_time=last.split(',')[:2],
            note='Time labels are native CSV values; timezone not independently inferred from headers.'))
    result=dict(source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        author_reported_annual_pnl=annual, sum_reported_annual_pnl=total,
        author_2022_share=annual[2022]/total,
        weighted_sum_rounded_author_annual_leg_pnl=sum(q*avg for q,avg in legs.values()),
        reported_package_annual=2680,
        official_contract_math=dict(m6e_eur_size=12500,m6e_tick_price=.0001,
            m6e_tick_dollars=12500*.0001, six_e_tick_price=.00005,
            six_e_tick_scaled_to_m6e_dollars=12500*.00005,
            one_native_m6e_tick_each_side_roundtrip_dollars=2*12500*.0001),
        approximate_design_event_counts_and_t2_mean_hurdle_in_sd={
            k:dict(assumed_events_per_year=n, five_year_opportunities=n*5,
                   t2_mean_over_sd=2/math.sqrt(n*5))
            for k,n in [('macro_shock',27),('stock_shock',8),('gold_shock',12)]},
        caveats=['Frequency counts are approximations before warm-up/overlap; effective n may be smaller.',
            'The t=2 calculation is an iid planning illustration, not a promotion gate or measured t statistic.',
            'Aggregate claims do not determine realized trade P&L, drawdown, margin, costs or account contribution.'],
        local_6e_headers_and_edge_dates=data,
        new_strategy_return_trials=0, candidate_returns_computed=False,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'claims_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['sum_reported_annual_pnl','author_2022_share',
        'weighted_sum_rounded_author_annual_leg_pnl','official_contract_math','new_strategy_return_trials']},indent=2))


if __name__=='__main__':
    main()
