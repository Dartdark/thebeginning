"""Reproduce the failed auction-demand design report from saved ledgers only."""
import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'analysis'))
import codex_t6_study_support as S
from codex_auction_demand_confirmation import tenor

C = S.C
OUT = ROOT / 'analysis/outputs/codex_auction_demand_confirmation'
NAME = 'NQ Auction Demand Confirmation'
REPORT = 'agents/codex/results/auction_demand_confirmation.md'
BASE = {'ADC15': 'ZN15', 'ADC5': 'ZN5', 'ADC15_D05': 'ZN15'}


def export_source_exclusions(intake):
    """Fill a row-level intake audit omission without changing any tested signal."""
    source = ROOT / 'data/treasury_auctions.csv'
    binding = json.loads((OUT / 'result_source_binding.json').read_text())
    if C.sha(source) != binding['sha256']:
        raise ValueError('Auction source changed after execution')
    raw = pd.read_csv(source, dtype={'cusip': str})
    raw['date'] = pd.to_datetime(raw.auction_date, errors='raise')
    raw = raw[raw.date <= pd.Timestamp('2022-12-31')].copy()
    deadline = raw.closing_time_comp.astype(str).str.replace(' ', '', regex=False).str.upper()
    tests = dict(unsupported_security=raw.security_type.isin(['Note', 'Bond']),
                 inflation_linked=raw.inflation_index_security.eq('No'),
                 floating_rate=raw.floating_rate.eq('No'),
                 wrong_deadline=deadline.eq('01:00PM'),
                 invalid_reopening=raw.reopening.isin(['Yes', 'No']),
                 invalid_cusip=raw.cusip.str.fullmatch(r'[A-Za-z0-9]{9}', na=False))
    raw['exclusion_reasons'] = [';'.join(k for k, mask in tests.items() if not bool(mask.loc[i]))
                                for i in raw.index]
    structural = raw.exclusion_reasons.eq('')
    unsupported_tenor = structural & raw.security_term.map(tenor).isna()
    raw.loc[unsupported_tenor, 'exclusion_reasons'] = 'unsupported_or_ambiguous_tenor'
    excluded = raw[raw.exclusion_reasons.ne('')].copy()
    assert len(excluded) == intake['structural_exclusions'] + intake['unsupported_tenor_rows']
    C.csv(OUT / 'design_auction_source_exclusions.csv', excluded)


def export_uniform_draws(ledgers, days, diagnostics):
    """Archive the shared filter helper's same seeded draws, verifying its summary."""
    draws = {}
    for name, base_name in BASE.items():
        candidate, base = ledgers[name], ledgers[base_name]
        rng = np.random.default_rng(C.SEED)
        totals, dds = [], []
        for _ in range(1000):
            sub = base.iloc[np.sort(rng.choice(len(base), len(candidate), replace=False))]
            totals.append(float(sub.net.sum()))
            dds.append(C.R.max_dd(sub.groupby('date').net.sum().reindex(days, fill_value=0.)))
        net = float(candidate.net.sum())
        dd = C.R.max_dd(candidate.groupby('date').net.sum().reindex(days, fill_value=0.))
        a, b = np.asarray(totals), np.asarray(dds)
        observed = [a.mean(), (a >= net).mean(), ((a < net) & (b > dd)).mean()]
        saved = diagnostics[name]
        expected = [saved['random_net_mean'], saved['p_random_net_ge_kept'], saved['p_kept_better_net_and_dd']]
        np.testing.assert_allclose(observed, expected, rtol=0, atol=1e-8)
        draws[name] = dict(seed=C.SEED, runs=1000, shared_summary_reconciled=True,
                           random_net_totals=totals, random_dd=dds)
    C.dump(OUT / 'design_uniform_draws.json', draws)


def main(update_program=False):
    gate = json.loads((OUT / 'design_complete_gate.json').read_text())
    if gate['selected'] is not None:
        raise ValueError('This rejected-design report cannot replace a passing result')
    m = pd.read_csv(OUT / 'design_metrics.csv')
    uniform = json.loads((OUT / 'design_filter_diagnostics.json').read_text())
    strata = json.loads((OUT / 'design_stratified_drops.json').read_text())
    auction_intake = json.loads((OUT / 'design_auction_intake.json').read_text())
    price_intake = json.loads((OUT / 'design_price_intake.json').read_text())
    counts = json.loads((OUT / 'design_counts.json').read_text())
    execution = json.loads((OUT / 'design_verified_execution.json').read_text())
    daily = pd.read_csv(OUT / 'design_daily.csv', parse_dates=['date'])
    ledgers = {name: pd.read_csv(OUT / f'design_{name}_trades.csv', parse_dates=['date'])
               for name in m.model.unique()}
    export_source_exclusions(auction_intake)
    export_uniform_draws(ledgers, pd.DatetimeIndex(daily.date), uniform)
    gaps = pd.concat([t[t.unobserved_held_minutes > 0].assign(model=name)
                      for name, t in ledgers.items()], ignore_index=True)
    C.csv(OUT / 'design_held_gap_tickets.csv', gaps)
    primary = m[(m.model == 'ADC15') & (m.side == 'all') & (m.period == '2018-22')].iloc[0]
    stripped = {k: {kk: vv for kk, vv in v.items() if kk not in ('random_net_totals', 'random_dd')}
                for k, v in strata.items()}
    report = f'''# NQ Auction Demand Confirmation: REJECT; continue distinct research

Summary: All three candidates failed 2018–22 design. Primary 15-minute rule: {int(primary.trades)} trades,
net ${primary.total:,.2f}/NQ, trade t {primary.t_trade:.3f}, daily Newey-West(5) t {primary.t_nw5:.3f}.
Both 5-minute and stricter demand variants also lost money; all failed matched random-drop gates.
No 2023+ returns tested. Program: 55 counted evaluations / 54 unique rules; no t4.5/t5/t6 milestone.

Plan: agents/codex/plans/auction_demand_confirmation.md, preregistration 3db3857 (amends d03cdcb before returns).
Scripts: analysis/codex_auction_demand_confirmation.py and analysis/codex_auction_demand_confirmation_report.py.
Outputs: analysis/outputs/codex_auction_demand_confirmation/.
Five models: three candidates and two unselectable same-clock ZN price-confirmation controls.
Prior program: 50 evaluations / 49 unique rules, plus unknown larger repository and author searches.
Uniform and stratified random subsets are nonselectable diagnostics, not extra economic configurations.

## Trade as tested

Use nominal, non-FRN Treasury Note/Bond auctions closing at 13:00 ET (12:00 CT). Map terms to the nearest
2/3/5/7/10/20/30-year tenor within half a year; reject equal-distance ties. Separate reopening and original
issues. The reference is the median of the exact six strictly prior results in that group, requiring at least
four positive finite observations. Missing results retain their history slots. Prior December 2017 auction
metadata can seed references, but all price execution starts in 2018. Multiple simultaneous eligible events
would skip that date. No such design-period date occurred.

D = published bid-to-cover / prior reference − 1. This is a historical deviation, not a consensus surprise,
when-issued yield tail, observed dealer inventory or forced next-day hedge. The proposed mechanism was that
an auction-demand result and same-direction bond repricing might leave further equity adjustment after entry.
The design result does not support that mechanism.

At 12:15 CT (ADC15 primary) or 12:05 (ADC5), measure ZN's close change from the exact 11:59 close.
Buy NQ if both D and the ZN change are positive; sell if both are negative. ADC15_D05 additionally requires
|D| >= 0.05. A zero D or ZN change produces no candidate. ZN15/ZN5 controls omit the demand sign/size gate
and keep identical reference, date and data eligibility. Only NQ is traded; ZN is an input.

On shared-calendar normal cash dates, require exact NQ/ZN mapping and complete positive, valid OHLC and
nonnegative volume from 11:59 through the decision close. No forward fill or future-day completeness mask.
Decision j enters at native open j+2: 12:17/12:07 close-labelled minute, one additional whole minute after
the decision. One contract and at most one trade per event date. Stop 0.15 of prior 15-weekday calendar ATR,
target 0.30, rounded up to 0.25 point; entry-bar protection active; exit at 12:55 CT. No overnight holding,
retrigger, break-even, trailing stop or return rescaling.

Shared grid._walk/F.replay execution charges NQ $7.25 round trip plus one tick ($5) per market/stop fill.
Native MNQ is priced independently at $1.24 round trip plus $0.50 per such fill. Target needs one NQ point
through; stop gaps fill at the worse native open. Fixed four-tick slippage is a nonselectable stress test.

## Design results

2018–22 only. Daily grid: {daily.date.min().date()} through {daily.date.max().date()}, {len(daily)} cash sessions
including zero-return days. Dollars are per NQ except native net_mnq rows. Shared metrics include all trades,
both sides, every year, NW5/NW20, initial-zero drawdown, costs, native micro costs and fill stress.

'''+S.table(m)+'''

## Filter falsifiers and selection gate

Because there is at most one event per date, candidate ledgers are actual executable subsets of the matching
same-clock controls: identical entry, side, brackets, exits and costs. There is no overlapping virtual-book
profit being called executable. The table below preserves base/kept/removed total profits, removed mean/t,
and 1,000 uniformly sampled matched-size subsets. design_uniform_draws.json archives the shared helper's
same seeded draws; all three summary values reconcile exactly within numerical tolerance.

```json
'''+json.dumps(uniform, indent=2)+'''
```

Another 1,000 subsets preserve kept count within each (year, tenor, reopening) cell, without replacement.
Cells and summary follow; all random totals/DD are saved in design_stratified_drops.json. No cell, direction,
threshold or subset was chosen after returns.

```json
'''+json.dumps(stripped, indent=2)+'''
```

The frozen basic gate required >=100 trades, positive net, trade t>=2, daily NW5>=1.5, PF>=1.20, at least four
positive years, positive native-MNQ net and positive four-tick stress net. Filter gates additionally required
removed mean<0, kept total>=base total, p(random net>=kept)<=0.10, and better profit/DD than at least 90% of
both uniform and stratified subsets. No candidate passed the basic or complete gate. The primary's positive
short-side total is not a whole-strategy pass and is not nominated as a new rule.

```json
'''+json.dumps(gate, indent=2)+'''
```

## Data, clocks and limits

```json
'''+json.dumps(dict(auction_source=auction_intake, price_sources=price_intake, event_and_execution_counts=counts), indent=2)+f'''
```

Auction intake includes five December 2017 reference-only events: 373 eligible source events in total,
368 in design, 326 with valid prior references before price checks. Reference-ready counts for 2018–22
are 40/62/68/78/78. No conflicting or exact duplicate source keys occurred. Six primary/three 5-minute
events failed the known-price window; no scheduled entries were missing. No held-minute gaps occurred
in any saved ledger ({len(gaps)} held-gap tickets). Input hashes, eligible features, event exclusions,
synthetic checks, and every failed candidate/control ledger are retained.
The completion review found that initial intake stored only aggregate structural exclusions. The report
script now archives all 152 excluded source rows with their frozen-rule reasons in
design_auction_source_exclusions.csv, checking the source hash and original exclusion count. Signals,
returns, selection and the original input binding were not changed.

Synthetic checks cover tenor/reopening references, current/future result invariance, missing history slots,
duplicate conflicts, summer/winter ET-to-CT conversion, matching candidate/control directions, extra delay,
shared calendar, entry-bar stops, worse stop gaps and target-through. Pre-return reviewers inspected intake
and code only; that is not a fresh raw-spec independent performance check.

Treasury's public policy says results become available after auction conclusion and its results page updates
in real time as results are available. It does not verify this CSV's historical publication, receipt or revision
timestamps. Availability by 12:15/12:05 CT remains an assumption. Source continuity/roll-switch timing and
original-contract parity are not independently established. Bid-to-cover is confounded by offering size,
tenor, reopening and bidding behavior. No favorable inference removes those limits.

No 2023+ validation, post-pass random-side/time placebos, expensive resampling/Monte Carlo, independent
promotion, account comparisons or PowerLanguage followed the failed gate. There is no account pass/payout
claim. Do not flip directions, promote the short side or controls, or tune this family after rejection.
Continue a distinct mechanism. This failure creates no milestone alert and does not pause research.
Actual raw-data execution: {execution['started_utc']} to {execution['completed_utc']}.
Claude review path: {REPORT}.
'''
    (ROOT / REPORT).write_text(report)
    if update_program:
        p = ROOT / 'agents/codex/research/t6_progress.json'
        q = json.loads(p.read_text())
        n = q['new_standalone_economic_configurations_tested']
        if n not in (50, 55) or (n == 55 and q['latest_completed_hypothesis'] != NAME):
            raise ValueError('Newer/concurrent program state; report saved but program update refused')
        q.update(status='researching', goal_met=False, latest_completed_hypothesis=NAME,
                 latest_result=f'All three candidates failed 2018–22; primary 199 trades, net ${primary.total:,.2f}/NQ, trade t {primary.t_trade:.3f}, NW5 {primary.t_nw5:.3f}. No 2023+ tested; continue DISTINCT research.',
                 new_standalone_economic_configurations_tested=55, unique_economic_configurations=54,
                 trial_count_note='55 conservative configuration evaluations include one repeated source-control nomination; 54 unique economic rules. Unknown older searches and diagnostic paths remain relevant.',
                 last_report=REPORT,
                 next_action='Formulate a DISTINCT mechanism, checking available inputs and previous studies. Commit evidence and <=5-model preregistration before returns. Do not invert auction direction, promote its sides/controls, or tune failed-family exits/thresholds.')
        q['research_continuation']['last_verified_execution'] = {
            **execution, 'hypothesis': NAME, 'phase': 'design', 'models_tested': 5,
            'report': REPORT, 'execution_marker': 'analysis/outputs/codex_auction_demand_confirmation/design_verified_execution.json'}
        # Preserve every prior notification event/threshold/history record; no failure alert.
        p.write_text(json.dumps(q, indent=2) + '\n')
        p = ROOT / 'agents/codex/research/t6_program.md'
        text = p.read_text()
        if '| NQ Auction Demand Confirmation |' not in text:
            text = text.replace('The repository has hundreds',
                                f'| {NAME} | Rejected | 5 models; primary 199 trades, t{primary.t_trade:.3f}, NW5 {primary.t_nw5:.3f}; no 2023+ tested; program55/54 unique |\n\nThe repository has hundreds')
            text = text.replace('\n\n| NQ Auction Demand Confirmation |', '\n| NQ Auction Demand Confirmation |')
        p.write_text(text)
    print('Rejected design report saved; no milestone event. Program update:', update_program)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--update-program', action='store_true')
    args = parser.parse_args()
    main(args.update_program)
