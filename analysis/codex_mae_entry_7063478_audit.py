"""Source arithmetic and invented counterexamples only; never a market backtest.

No raw prices, existing trade ledgers, signal engine or candidate sweep is read.
The eight source thresholds are transcribed author looks, not new local trials.
"""
import csv
import datetime as dt
import hashlib
import itertools
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'agents/codex/inputs/ssrn7063478_20261108'
OUT = ROOT / 'analysis/outputs/codex_ssrn7063478_20261108'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    text = (BASE / 'paper.txt').read_text()
    assert 'Purvang Gandhi' in text and 'July 2026' in text
    assert '3,908' in text and '6.02 basis points' in text
    rows = [
        (0, 3908, 100, 12.3, 1.38, -11.6),
        (.05, 3744, 96, 22.3, 2.37, -11.2),
        (.10, 3466, 89, 28.2, 2.91, -11.0),
        (.15, 3163, 81, 31.1, 3.25, -10.9),
        (.20, 2775, 71, 31.2, 3.27, -10.9),
        (.25, 2448, 63, 31.9, 3.33, -10.8),
        (.30, 2094, 54, 30.2, 3.26, -10.8),
        (.40, 1541, 39, 24.7, 3.13, -10.6),
        (.50, 1107, 28, 19.1, 2.68, -10.5),
    ]
    with (OUT / 'author_table1.csv').open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['theta_pct', 'retained', 'retained_pct_rounded', 'author_cagr_pct',
                    'author_sharpe', 'author_max_drawdown_pct'])
        w.writerows(rows)
    checks = []
    # A losing trade need not reach the resting limit. No sampled market evidence.
    entry, theta, cost = 100., .0025, 6.02 / 10000
    low, exit_price = 99.80, 99.90
    mae = (entry - low) / entry
    net = (exit_price - entry) / entry - cost
    assert mae < theta and net < 0
    checks.append(dict(case='unfilled_can_be_gross_loser', original_entry=entry,
        minimum_price=low, original_exit=exit_price, mae_pct=100 * mae,
        limit=entry * (1-theta), baseline_net_pct=100 * net,
        conclusion='MAE below threshold does not imply the foregone trade was profitable.'))
    low, exit_price = 99.90, 100.03
    gross = (exit_price-entry)/entry
    assert (entry-low)/entry < theta and gross > 0 and gross-cost < 0
    checks.append(dict(case='unfilled_small_gross_winner_can_lose_after_fees',
        original_entry=entry, minimum_price=low, original_exit=exit_price,
        gross_pct=100*gross, net_pct=100*(gross-cost)))
    # Identical aggregate entry/exit/MAE/MFE; different first passage and post-fill exposure.
    paths = [[100., 99.5, 101., 100.6, 100.5], [100., 101., 100.6, 99.5, 100.5]]
    limit = entry*(1-theta)
    passages = [next(i for i,p in enumerate(path) if p < limit) for path in paths]
    signatures = [(p[0], p[-1], min(p), max(p)) for p in paths]
    assert signatures[0] == signatures[1] and passages == [1, 3]
    assert max(paths[0][passages[0]:]) != max(paths[1][passages[1]:])
    checks.append(dict(case='same_aggregate_excursions_different_execution_path',
        invented_paths=paths, first_passage_step=passages,
        invented_expiry_step=2, fills_before_expiry=[i <= 2 for i in passages],
        conclusion='Even MFE plus MAE does not identify fill time, time-in-force eligibility, calendar marks or post-fill path.'))
    touch_path = [100., 99.75, 100.5]
    assert min(touch_path) == limit and not any(p < limit for p in touch_path)
    checks.append(dict(case='threshold_touch_not_trade_through', invented_path=touch_path,
        threshold_eligible=True, strict_trade_through=False,
        conclusion='A price touch does not establish queue fill; equality in MAE >= theta is weaker than trade-through.'))
    # Denominator changes when percentage return is defined relative to the actual entry.
    r = .005
    long_return = ((100.5-limit)/limit)
    short_entry = entry*(1+theta)
    short_return = (short_entry-99.5)/short_entry
    assert math.isclose(long_return,(r+theta)/(1-theta))
    assert math.isclose(short_return,(r+theta)/(1+theta))
    checks.append(dict(case='percentage_denominator_is_side_specific', theta_pct=100*theta,
        original_gross_pct=100*r, revised_long_gross_pct=100*long_return,
        revised_short_gross_pct=100*short_return,
        conclusion='Price improvement is mechanical, but adding theta to a percentage return is not exact; position/notional and fee conventions matter.'))
    fixed = [.01, -.005, .02]
    compounds = [math.prod(1+r for r in order) for order in itertools.permutations(fixed)]
    assert all(math.isclose(x,compounds[0]) for x in compounds)
    checks.append(dict(case='reordering_fixed_selected_returns_is_not_selection_validation',
        invented_returns=fixed, permutations=len(compounds), terminal_wealth=compounds[0],
        conclusion='Under fixed-fraction compounding, order leaves terminal wealth unchanged. Drawdown permutations do not validate fill rules, threshold selection or future edge.'))
    point_cost = [2/p*10000 for p in (5000.,25000.)]
    assert math.isclose(point_cost[0],4.) and math.isclose(point_cost[1],.8)
    checks.append(dict(case='fixed_points_are_not_fixed_basis_points',
        illustrative_index_levels=[5000,25000], two_point_cost_bp=point_cost,
        conclusion='A flat 6.02 bp allowance including two points is a source modeling convention; it is not a dated all-in fee reconstruction across fivefold prices.'))
    scout = ROOT/'agents/codex/research/scout/progress.json'
    p = json.loads(scout.read_text())
    prior = ROOT/'analysis/outputs/limit_entry_test_output.txt'
    result = dict(
        source=dict(id='ssrn:7063478', title='Entry-Timing Confirmation via Maximum Adverse Excursion: An Empirical Test on a Systematic Index Futures Strategy',
            author='Purvang Gandhi, MTS Institute', version='July 2026', pages=12,
            path=str((BASE/'paper.pdf').relative_to(ROOT)), sha256=sha(BASE/'paper.pdf'),
            permission='owned_upload', provenance='User attachment file_00000000433081fda9a1bc724b534f89',
            access_method='pdftotext -layout; full 12-page text read; Table 1 visually inspected'),
        checked_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        checked_codex_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        claude_ref=subprocess.check_output(['git','rev-parse','origin/claude/nq-trading-strategy-params-5h9d20'],cwd=ROOT,text=True).strip(),
        author_sample='Nifty 50 futures, hourly, 2010-04-13 to 2026-01-30',
        author_main_threshold_pct=.25, author_sample_trades=3908, author_retained_trades=2448,
        author_unfilled=3908-2448, exact_retained_fraction=2448/3908,
        author_sharpe_relative_increase_pct=(3.33/1.38-1)*100,
        author_total_table_profiles=len(rows), author_nonzero_thresholds=len(rows)-1,
        author_cost_bp_round_trip=6.02,
        synthetic_checks_passed=len(checks), synthetic_checks=checks,
        prior_limit_output=dict(path=str(prior.relative_to(ROOT)),sha256=sha(prior)),
        scout_preserved=dict(sha256=sha(scout),hypotheses=p['hypotheses_started'],definitions=p['economic_definitions'],lease=p['lease']),
        root_trials_sha256=sha(ROOT/'TRIALS.csv'),
        new_economic_trials=0, market_data_loaded=False, candidate_return_tests=False,
        disposition='dont_test', independent_economic_verification=False,
        interpretation='No exact proprietary-signal replication. Source assumptions and same-sample selection do not establish a distinct qualified edge for a new cross-book sweep. Preserve existing negative/qualified timing evidence.'
    )
    (OUT/'source_and_mechanics.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(synthetic_cases_passed=len(checks),market_data_loaded=False,
                         economic_trials=0,author_retained_fraction=2448/3908)))


if __name__ == '__main__':
    main()
