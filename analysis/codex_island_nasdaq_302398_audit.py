"""Source transcriptions and synthetic measurement checks, not a trading backtest."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'agents/codex/inputs/island_nasdaq_302398'


def main():
    coarse, fine = 1/16, 1/256
    external_ask = 100 + coarse
    true_ask = external_ask - fine
    displayed_ask = math.ceil(true_ask / coarse) * coarse
    assert true_ask < external_ask and displayed_ask == external_ask
    # Invented passive buy/sell fills. Future midpoint is a label, never an input.
    signed_markout = lambda side, price, future_mid: side * (future_mid - price)
    assert abs(signed_markout(1, 100, 100.02) - .02) < 1e-10
    assert abs(signed_markout(-1, 100, 99.98) - .02) < 1e-10
    assert signed_markout(1, 100, 99.98) < 0
    # The model identifies theta=c+pi, not the two terms independently.
    spread, markout, rebate = .10, .03, .001
    alpha = spread - 2 * markout
    theta = markout + rebate
    decompositions = [[.01, theta-.01], [.03, theta-.03]]
    assert all(abs(c + rent - theta) < 1e-12 for c, rent in decompositions)
    report = {
        'review_local_date': '2026-11-07',
        'source_claims': {
            'sample_stocks': ['COMS','CSCO','DELL','INTC','MSFT','QCOM','SUNW'],
            'sample_windows': ['2000-03-08 through 2000-03-14 (5 sessions)',
                               '2001-06-18 through 2001-06-22 (5 sessions)'],
            'partial_session': '2000-03-10 feed ends14:30 instead of16:00',
            'nasdaq_spreads_dollars': [.079, .014],
            'island_spreads_dollars': [.198, .0648],
            'table4_pooled_theta': [.02, .00], 'table4_pooled_theta_t': [2.49, 1.53],
            'table6_rejections_at_5pct_by_year': [5,6],
            'island_passive_rebate_dollars_per_share': .001,
            'island_immediate_fee_dollars_per_share': .0025,
        },
        'rounding_fixture': {'true_ask': true_ask, 'displayed_ask': displayed_ask,
                             'external_ask': external_ask, 'hidden_improvement': fine},
        'spread_reductions_pct': {
            'nasdaq': 100*(1-.014/.079), 'island': 100*(1-.0648/.198)},
        'identification_fixture': {'spread':spread, 'markout':markout, 'alpha':alpha,
                                   'theta':theta, 'cost_rent_pairs':decompositions},
        'checks': ['rounding can erase price improvement', 'passive markout side symmetry',
                   'cost/rent decomposition nonunique'],
        'historical_returns_reproduced': False, 'new_financial_return_trials': 0,
        'hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(BASE.rglob('*')) if p.is_file()},
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (ROOT / 'analysis/outputs/codex_island_nasdaq_302398/source_audit.json').write_text(
        json.dumps(report, indent=2) + '\n')
    print(json.dumps({'checks':'PASS', 'hidden_quote_improvement':fine, 'theta_nonunique':True,
                      'financial_return_trials':0}))


if __name__ == '__main__':
    main()
