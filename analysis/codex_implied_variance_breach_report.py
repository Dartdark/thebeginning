"""Reproduce the rejected design report; optional guarded program-state update.

Never reruns return variants or advances a failed design to historical validation.
"""
import argparse
from pathlib import Path
import json
import sys
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'analysis'))
import codex_t6_study_support as S
C=S.C;OUT=ROOT/'analysis/outputs/codex_implied_variance_breach'
NAME='NQ Implied Variance Budget Breach'


def main(update_program=False):
    gate=json.loads((OUT/'design_complete_gate.json').read_text())
    if gate['selected'] is not None:raise ValueError('This report is for a rejected design; do not overwrite a passing study with a failure template')
    m=pd.read_csv(OUT/'design_metrics.csv');f=json.loads((OUT/'design_filter_diagnostics.json').read_text())
    ac=json.loads((OUT/'design_actual_base_comparison.json').read_text());times=json.loads((OUT/'design_conditional_time_placebos.json').read_text())
    intake=json.loads((OUT/'design_NQ_intake.json').read_text());qi=json.loads((OUT/'design_VXN_intake.json').read_text())
    counts=json.loads((OUT/'design_counts.json').read_text());execution=json.loads((OUT/'design_verified_execution.json').read_text())
    primary=m[(m.model=='IVB5_2')&(m.side=='all')&(m.period=='2018-22')].iloc[0]
    summaries={k:{kk:vv for kk,vv in v.items() if kk not in ('random_net_totals','random_dd')} for k,v in times.items()}
    gaps=[]
    for name in m.model.unique():
        t=pd.read_csv(OUT/f'design_{name}_trades.csv',parse_dates=['date']);bad=t[t.unobserved_held_minutes>0].copy();bad.insert(0,'model',name);gaps.append(bad)
    gap=pd.concat(gaps,ignore_index=True);C.csv(OUT/'design_held_gap_tickets.csv',gap)
    report=f'''# NQ Implied Variance Budget Breach: REJECT; research continues

Summary: All three frozen candidates lost after costs in2018-22. Primary5min:{int(primary.trades)}trades,
net${primary.total:,.2f}/NQ,trade t{primary.t_trade:.3f},dailyNW5 t{primary.t_nw5:.3f}; no candidate passed.
The variance-surprise gate removes profitable signals and fails conditional random timing. No2023+returns tested.
Program45counted evaluations/44unique rules retained; no t4.5/t5/t6 milestone. Continue a distinct mechanism.

Plan: agents/codex/plans/implied_variance_breach.md, prereg ea36af6.
Scripts: analysis/codex_implied_variance_breach.py and analysis/codex_implied_variance_breach_report.py.
Outputs: analysis/outputs/codex_implied_variance_breach/.
Five models:3candidates+2unselectable price controls. Prior40counted evaluations/39unique; plus unknown much
larger older repository/author searches. Overlapping-window returns and random paths below are additional
NON-SELECTABLE diagnostic return paths, not extra selected strategies or executable capitalized portfolios.

## Rule as tested

At completed5/15min closes09:00--13:30CT, compare cumulative squared one-minute log returns since08:31open
with a lagged option-implied variance budget. Prior cash-market day's EXACT VXNclose, converted to daily
variance by(VXN/100)^2/252, is multiplied by a prior60normal-date median realized/implied cash-variance
calibration and prior20normal-date median intraday variance share. At least60past dates,45valid scale and
15valid shape observations. Missing past dates keep their chronological window positions. Today's final
variance/completeness enters history only after today's decisions. No current/future VXN or full-day mask.

Long if cumulative move>=0.20prior15weekdayATR and close>runningcashVWAP; short mirrored. Require variance
ratio>=2(primary5min/15min)or3(one5minvariant). Price controls omit the ratio gate but retain its input/history
eligibility. Take FIRST qualifying window/date only, even if its scheduled open is missing; no later retry.
Entry at j+2nativeopen(oneextra whole minute), stop0.15ATR,target0.45ATR,ceilto0.25,activeentrybar,flat14:55.
One position/trade/day; noBE/trail/overnight/old trade list or return rescaling. Normalcash dates, noJuly3/Dec24.
NQ$7.25RT plus1tick($5)/market-stopfill; MNQ$1.24RT+$0.50/fill independently. Target needs1pointthrough;
worse-open stopgaps and fixed4tickfill stress. Sharedgrid._walk via first-signal adapter; no shared engine edits.

VXN's30-day expected-volatility interpretation is a source fact; a directional continuation edge is our unproven
hypothesis. Source:[Cboe methodology](https://cdn.cboe.com/api/global/us_indices/governance/Volatility_Index_Methodology_Selected_Broad_Based_Index_Equity_and_ETF_Volatility_Indices.pdf).
The252-day projection and causal cash-session calibration are model conventions, not a Cboe daily forecast.

## Design results

2018-22 only. Dollars/NQ except net_mnq rows in nativeMNQ. Cash-market-day zeros, initialzeroDD, all/side/year
standard shared metrics and NW5/NW20. Native gross/cost units are consistent. No2023+oraccountclaim.

'''+S.table(m)+'''

## Actual strategy vs price-only controls

The actual one/day ledgers are NOT nested: their first qualifying times differ. The following is an executable
whole-strategy comparison, not a falsely matched kept/removed trade ledger.

```json
'''+json.dumps(ac,indent=2)+'''
```

## Independent-window filter diagnostics

All potential price windows versus all budget-qualified windows, brackets/timeexit unchanged. These overlap
and are NON-EXECUTABLE diagnostics. Base/kept/removed totalnet, removedmean/t and1000matched-size random
subsets are shown. Their sums/DD cannot be presented as account or capped-strategy performance.

```json
'''+json.dumps(f,indent=2)+'''
```

## Conditional random timing

1000one-window-per-day paths on the actual candidate's EX-POST selected event dates. Windows come from
that date's eligible price-only set with original bracket/14:55exit and costs. This isolates timing conditional
on event days; it does not give an implementable advance calendar. All random totals/DD are retained in
 design_conditional_time_placebos.json; no placebo was selected for trading.

```json
'''+json.dumps(summaries,indent=2)+f'''
```

## Data, engineering and limits

NQintake {intake['rows']:,}rows,{intake['exact_duplicates']}exactduplicates,{intake['conflicting_keys']}conflictingkeys;
VXNintake {qi['rows']:,}rows,{qi['exact_duplicates']}exactduplicates,{qi['conflicting_dates']}conflictingdates.
Intake includes pre2018source metadata; actual design grids/calibration start2018 without2017warm-up.
Clock: native CT minute close labels; exact previous cash-date VXN. Daily closing-value receive/revision
vintages and live marketability during stress are unverified. Retained held-gap tickets:{len(gap)} across all
actual candidate/control ledgers, listed in design_held_gap_tickets.csv. No incomplete ticket deleted.

Engineering passed exact prior-date/holiday checks, missing exact quote rejection,60/20date warm-up,
variance-vs-sigma units, later-price/completeness mutation invariance of earlier features, first-signal/no-retry
behavior, extra-minute delay, and shared entrybar/gap/through tests. Features, calibration history, window/
selection/missingentry counts and raw-input/source hashes are retained. These checks do not prove an edge.

No candidate cheap/complete gate passes. No2023+returns, expensive post-pass placebos/resampling/MC,
accountbench, independent promotion orPowerLanguage. Positive unfiltered controls remain unselectable;
do not nominate them after seeing this loss or retune a failed family. Option-implied variance may forecast
volatility without a directional underreaction that survives costs, consistent with this rejected test.

Actual raw-data research execution is recorded in design_verified_execution.json, completed
{execution['completed_utc']}. A GitHub read or automation schedule alone is not counted as research.
Next: preserve the failure, leave research continuation enabled, and preregister a DISTINCT mechanism.
Claude review path: agents/codex/results/implied_variance_breach.md.
'''
    (ROOT/'agents/codex/results/implied_variance_breach.md').write_text(report)
    if update_program:
        p=ROOT/'agents/codex/research/t6_progress.json';q=json.loads(p.read_text());n=q['new_standalone_economic_configurations_tested']
        if n not in (40,45) or (n==45 and q['latest_completed_hypothesis']!=NAME):
            raise ValueError('Newer/concurrent program state; report saved, refusing to rewind or race it')
        q.update(status='researching',goal_met=False,latest_completed_hypothesis=NAME,
            latest_result=f"All3candidates failed2018-22;primary{int(primary.trades)}trades net${primary.total:,.2f}/NQ,trade t{primary.t_trade:.3f},NW5 {primary.t_nw5:.3f}. No2023+tested. Continue distinct research.",
            new_standalone_economic_configurations_tested=45,unique_economic_configurations=44,
            trial_count_note='45conservative configuration evaluations include one repeated source-control nomination;44unique economic rules. Unknown older searches and diagnostic paths remain relevant.',
            last_report='agents/codex/results/implied_variance_breach.md',
            next_action='Check prior research, formulate a DISTINCT mechanism, write evidence and commit <=5-model preregistration before new returns; do not retune failed families or select their controls.')
        q['research_continuation']['last_verified_execution']={**execution,'hypothesis':NAME,'phase':'design','models_tested':5,
            'report':'agents/codex/results/implied_variance_breach.md','execution_marker':'analysis/outputs/codex_implied_variance_breach/design_verified_execution.json'}
        # Preserve milestone history and any undelivered earlier event. This rejected
        # design creates no event, crosses no threshold and never pauses the worker.
        p.write_text(json.dumps(q,indent=2)+'\n')
        p=ROOT/'agents/codex/research/t6_program.md';text=p.read_text()
        if '| NQ Implied Variance Budget Breach |' not in text:
            text=text.replace('The repository has hundreds',f'| {NAME} | Rejected |5models;primary{int(primary.trades)}trades,t{primary.t_trade:.3f},NW5 {primary.t_nw5:.3f};no2023+tested;program45/44unique |\n\nThe repository has hundreds')
            text=text.replace('\n\n| NQ Implied Variance Budget Breach |','\n| NQ Implied Variance Budget Breach |')
        p.write_text(text)
    print('Saved report; rejected design; no milestone event. Program-state update:',update_program)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--update-program',action='store_true');a=p.parse_args();main(a.update_program)
