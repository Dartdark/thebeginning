"""Reproduce the rejected covariance-risk-budget report from frozen saved artifacts."""
import argparse
import json
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'analysis'))
import codex_t6_study_support as S

C = S.C
OUT = ROOT / 'analysis/outputs/codex_correlation_risk_budget'
NAME = 'NQ Correlation Risk Budget'
REPORT = 'agents/codex/results/correlation_risk_budget.md'


def read(name):
    return json.loads((OUT / name).read_text())


def main(update_program=False):
    gate = read('design_complete_gate.json')
    if gate['selected'] is not None:
        raise ValueError('Rejected-design report cannot replace a passing candidate')
    m = pd.read_csv(OUT / 'design_metrics.csv')
    primary = m[(m.model == 'CRB005') & (m.period == '2018-22') & (m.side == 'all')].iloc[0]
    ref = pd.read_csv(OUT / 'design_daily_reference_audit.csv', parse_dates=['date'])
    events = pd.read_csv(OUT / 'design_RP30_event_audit.csv', parse_dates=['date'])
    daily = pd.read_csv(OUT / 'design_daily.csv', parse_dates=['date'])
    ledgers = {name: pd.read_csv(OUT / f'design_{name}_trades.csv', parse_dates=['date'])
               for name in m.model.unique()}
    pd.testing.assert_frame_equal(ledgers['CRB005'], ledgers['CRB0025'], check_exact=True)
    pd.testing.assert_frame_equal(pd.read_csv(OUT / 'design_CRB005_signals.csv'),
                                  pd.read_csv(OUT / 'design_CRB0025_signals.csv'), check_exact=True)
    correction = dict(id='crb_0025_equivalent_005', prereg='5678dde',
                      prior_evaluations=55, prior_unique=54, new_evaluations=5, new_unique=4,
                      cumulative_evaluations=60, corrected_cumulative_unique=58,
                      original_prereg_and_gate_projected_unique=59,
                      reason='abs(F)>=0.01 and abs(K)>=0.5*abs(F) already imply abs(K)>=0.005; the 0.0025 threshold is algebraically redundant with 0.005, not merely empirically equal.',
                      all_failed_evaluations_retained=True, original_artifacts_unchanged=True)
    C.dump(OUT / 'design_trial_count_audit.json', correction)
    C.dump(OUT / 'design_resampling_manifest.json', dict(
        uniform_seed=int(C.SEED), stratified_seed=20261026, paths_per_model=1000,
        uniform_file='design_uniform_draws.json', stratified_file='design_stratified_drops.json',
        strata=['year', 'equity_sign', 'equity_magnitude_bin', 'vol_sign'],
        magnitude_bin_edges=[0, 1, 2, 'infinity'],
        original_runner_and_draws_unchanged=True))
    gaps = pd.concat([t[t.unobserved_held_minutes > 0].assign(model=name)
                      for name, t in ledgers.items()], ignore_index=True)
    C.csv(OUT / 'design_held_gap_tickets.csv', gaps)
    strata = {name: {k: v for k, v in values.items() if k not in ('random_net_totals', 'random_dd')}
              for name, values in read('design_stratified_drops.json').items()}
    execution = read('design_verified_execution.json')
    audit = dict(price_intake=read('design_price_intake.json'),
                 reference_exclusions={k: int(v) for k, v in ref.reason.value_counts().items()},
                 first_design_date_with_60_prior_observations=str(events[events.prior_observations.ge(60)].date.min().date()),
                 event_and_execution_counts=read('design_counts.json'))
    report = f'''# NQ Correlation Risk Budget: REJECT; continue distinct research

Summary: All three frozen candidates failed 2018–22 design. Primary 30-minute rule: {int(primary.trades)} trades,
net ${primary.total:,.2f}/NQ, trade t {primary.t_trade:.3f}, daily Newey-West(5) t {primary.t_nw5:.3f}.
The filter removed profitable trades and lost against matched controls. No 2023+ returns were tested.
All 60 evaluations retained; 58 unique rules after a disclosed redundant threshold. No milestone event.

Plan: agents/codex/plans/correlation_risk_budget.md, commit 5678dde before raw return execution.
Scripts: analysis/codex_correlation_risk_budget.py and analysis/codex_correlation_risk_budget_report.py.
Outputs: analysis/outputs/codex_correlation_risk_budget/. Five evaluations: three candidate labels and two
unselectable controls. Prior program:55 evaluations/54 unique, plus unknown much larger older searches.

## Rule as tested

At the 14:30 CT 30-minute close, model a US stock–bond portfolio from ES/ZN returns. An uncentred EWMA
second-moment matrix uses lambda0.94 after 60 admissible daily returns; initialize from their mean outer
product. At each date the state contains only strictly prior observations. Prices come from exact immediately
preceding cash-date 15:00 closes; missing/early/guarded dates are not stretched to older available closes.

For each covariance matrix, inverse-volatility weights give equal risk in two assets. Leverage targets 8%
annualized risk and caps at2. Update with today's partial return through14:30. Compare the new equity target
with a counterfactual using the SAME updated marginal variances and prior correlation. K is their difference.
Full flow F is new target minus prior model exposure drifted by today's equity and bond returns/NAV.
V is the corresponding frozen-correlation rebalance. These model outputs are signal inputs, not traded
portfolio returns. Actual AUM, allocation, orders and a mandatory execution clock are not observed.

Shared eligibility requires |F|>=0.01NAV,V!=0, finite model values and a positive prior NQ ATR. Trade sign(F)
when sign(K) agrees, |K|>=0.5|F| and |K|>=0.005(primary CRB005),0.0025(CRB0025),or0.01(CRB010).
RP30 omits K gates. VOL30 uses sign(V) on the same eligible dates and is unselectable. Only NQ is traded.

Native CT close labels; valid complete positive OHLC/nonnegative volume at14:01–14:30 in all three inputs;
normal cash dates only, no July3/Dec24. Both daily endpoints and decision/prior dates avoid the existing equity
roll window and the last12Monday–Friday dates of February/May/August/November. The latter buffers typical
Treasury rolls but does not establish exact vendor switch dates. Fixed |rES|>5% or |rZN|>3% input jumps are
unavailable; no repair or forward-return selection. ES2017 beginsJanuary, ZN2017 onlyDecember. Actual
60-observation readiness begins {audit['first_design_date_with_60_prior_observations']}.

Entry at native14:32-labelled open, one extra whole minute after the decision. One contract/date, no reentry,
stop0.10prior15weekdayATR,target0.20 rounded up to0.25, active entry-bar protection, flat15:00CT.
Shared grid._walk/F.replay handles target1point-through and worse-open stop gaps. NQ$7.25RT plus$5 per
market/stop fill; nativeMNQ independently$1.24RT plus$0.50 per such fill. Fixed four-tick stress retained.
No old ticket series, signal basket, fitted return combination, sizing or return rescaling.

## Design results

2018–22 only. Daily cash grid {daily.date.min().date()}–{daily.date.max().date()}, {len(daily)} sessions including
zero-return days. NQ dollars except native net_mnq rows. Whole/long/short/every year, initial-zero drawdown,
shared standard metrics, trade t, NW5/NW20, native micro costs and four-tick slippage follow.

'''+S.table(m)+'''

## Actual filter and counterfactual controls

Each candidate is an exact executable RP30 subset, with identical entry/side/brackets/exits/costs. Base,
kept and removed totals, removed mean/t and1,000 uniform matched-size subsets:

```json
'''+json.dumps(read('design_filter_diagnostics.json'), indent=2)+'''
```

The same uniform draws reconcile to the shared helper and are saved in design_uniform_draws.json.
Another1,000 subsets preserve kept count within (year,equity-return sign,equity standardized-magnitude bin,
frozen-correlation-flow sign); bins are[0,1),[1,2),[2,infinity). Full arrays are in design_stratified_drops.json;
cells and summary follow. These are random-drop diagnostics, not selected strategies.

```json
'''+json.dumps(strata, indent=2)+'''
```

VOL30 on the identical candidate dates uses the same contract count, bracket distances, time limit and cost
MODEL, with a possibly different side. Actual exits/fill costs can differ. This is a matched whole-rule
counterfactual, not a removed-trade ledger. Candidate results are worse than their matched counterfactual:

```json
'''+json.dumps(read('design_frozen_correlation_comparison.json'), indent=2)+'''
```

No candidate passed the >=100/positive-net/t>=2/NW5>=1.5/PF>=1.20/four-positive-year/native-micro/stress
gate, let alone the total-profit/random-drop and matched-counterfactual gates. The near-zero VOL30 result,
or positive side/year subsets, cannot be nominated after seeing returns. Complete frozen gates:

```json
'''+json.dumps(gate, indent=2)+'''
```

## Trial accounting correction

The lower threshold was redundant at preregistration: |F|>=0.01 and |K|>=0.5|F| already require |K|>=0.005.
CRB0025 and CRB005 are algebraically the same rule. I should have caught this before execution. Their saved
signal and ticket ledgers reconcile exactly. All five evaluations remain counted; the actual new unique count
is four. Original preregistration and gate's projected59-unique field are preserved, not silently rewritten.
The authoritative correction is design_trial_count_audit.json and progress now records60evaluations/58unique.
Selection/multiple-testing lower bounds continue to use all60 evaluations, not the smaller unique count.

```json
'''+json.dumps(correction, indent=2)+'''
```

## Data, clocks, remaining limitations and decision

```json
'''+json.dumps(audit, indent=2)+f'''
```

Daily reference audit retains every cash date from2017, including missing/roll/jump exclusions. All design
cash dates have per-model event reasons; raw hashes and all signal features are saved. No conflicting or exact
duplicate native keys, missing scheduled entries, invested/cap suppression or held gaps occurred in the saved
ledgers ({len(gaps)} held-gap tickets). Synthetic and pre-return code reviews found no blocking spec mismatch;
they had maker context and are not an independent raw-spec promotion verdict.

The model is not a replication of ECB's European four-asset analysis. NQ transmission, current fund AUM,
calibration and14:30execution timing remain unverified. Covariance can become stale through guarded/missing
intervals. Input jump guards and calendar buffers do not prove original-contract continuity or receipt latency.
There are too few candidate events and negative net evidence, including both primary sides. Do not weaken
guards or magnitude/attribution thresholds to rescue this family.

No2023+historical validation, post-pass random-side/time placebos, expensive resampling/MC, independent
promotion, account tests or PowerLanguage followed rejection. No invented account pass/payout improvement.
Continue a DISTINCT mechanism. This failure emits no milestone, crosses no4.5/5/6 threshold and does not
pause the research continuation or change the read-only watcher.
Actual raw-data execution: {execution['started_utc']} to {execution['completed_utc']}.
Claude review path: {REPORT}.
'''
    (ROOT / REPORT).write_text(report)
    if update_program:
        p = ROOT / 'agents/codex/research/t6_progress.json'
        q = json.loads(p.read_text())
        n = q['new_standalone_economic_configurations_tested']
        if n not in (55, 60) or (n == 60 and q['latest_completed_hypothesis'] != NAME):
            raise ValueError('Newer/concurrent state; report saved but program update refused')
        q.update(status='researching', goal_met=False, latest_completed_hypothesis=NAME,
            latest_result=f'All three frozen candidates failed 2018–22; primary44trades, net${primary.total:,.2f}/NQ, trade t{primary.t_trade:.3f}, NW5{primary.t_nw5:.3f}. No2023+tested; continue DISTINCT research. One redundant threshold retained in all60evaluations.',
            new_standalone_economic_configurations_tested=60, unique_economic_configurations=58,
            trial_count_note='60 conservative evaluations include one repeated source-control nomination and one algebraically redundant covariance threshold;58 unique economic rules. All failures/evaluations retained;larger unknown older searches remain relevant.',
            last_report=REPORT,
            next_action='Formulate a DISTINCT mechanism after checking prior studies and actual input feasibility. Commit evidence and <=5 configurations before new returns. Do not rescue covariance risk-budget thresholds/clock/guards/direction or nominate its controls/sides.')
        corrections = q.setdefault('configuration_count_corrections', [])
        if not any(item.get('id') == correction['id'] for item in corrections):
            corrections.append({**correction, 'evidence': 'analysis/outputs/codex_correlation_risk_budget/design_trial_count_audit.json', 'report': REPORT})
        q['research_continuation']['last_verified_execution'] = {
            **execution, 'hypothesis': NAME, 'phase': 'design', 'models_tested': 5, 'report': REPORT,
            'execution_marker': 'analysis/outputs/codex_correlation_risk_budget/design_verified_execution.json'}
        # Preserve every earlier milestone/event record. No new event for rejection.
        p.write_text(json.dumps(q, indent=2) + '\n')
        p = ROOT / 'agents/codex/research/t6_program.md'
        text = p.read_text()
        if '| NQ Correlation Risk Budget |' not in text:
            text = text.replace('The repository has hundreds',
                f'| {NAME} | Rejected |5evaluations/4newunique;primary44trades,t{primary.t_trade:.3f},NW5{primary.t_nw5:.3f};no2023+tested;program60/58unique;redundant threshold disclosed |\n\nThe repository has hundreds')
            text = text.replace('\n\n| NQ Correlation Risk Budget |', '\n| NQ Correlation Risk Budget |')
        p.write_text(text)
    print('Rejected design saved; all60evaluations retained;58unique;no milestone. Program update:', update_program)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--update-program', action='store_true')
    args = parser.parse_args()
    main(args.update_program)
