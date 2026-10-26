"""Reproduce rejected turnover-switch design report; optional guarded program update."""
import argparse
import json
from pathlib import Path
import sys
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'analysis'))
import codex_t6_study_support as S
C=S.C;OUT=ROOT/'analysis/outputs/codex_relative_turnover_switch';NAME='NQ Relative Turnover Switch'


def main(update_program=False):
    gate=json.loads((OUT/'design_complete_gate.json').read_text())
    if gate['selected'] is not None:raise ValueError('Rejected-design report template cannot replace a passing candidate')
    m=pd.read_csv(OUT/'design_metrics.csv');uniform=json.loads((OUT/'design_filter_diagnostics.json').read_text())
    strata=json.loads((OUT/'design_stratified_drops.json').read_text());actual=json.loads((OUT/'design_actual_base_comparison.json').read_text())
    intake=json.loads((OUT/'design_intake.json').read_text());mapping=json.loads((OUT/'design_mapping.json').read_text())
    audit=json.loads((OUT/'native_volume_source_audit.json').read_text());execution=json.loads((OUT/'design_verified_execution.json').read_text())
    primary=m[(m.model=='CTS5_15')&(m.side=='all')&(m.period=='2018-22')].iloc[0]
    summary={k:{kk:vv for kk,vv in v.items() if kk not in ('random_net_totals','random_dd')} for k,v in strata.items()}
    gap=[]
    for name in m.model.unique():
        t=pd.read_csv(OUT/f'design_{name}_trades.csv',parse_dates=['date']);bad=t[t.unobserved_held_minutes>0].copy();bad.insert(0,'model',name);gap.append(bad)
    gaps=pd.concat(gap,ignore_index=True);C.csv(OUT/'design_held_gap_tickets.csv',gaps)
    report=f'''# NQ Relative Turnover Switch: REJECT; continue distinct research

Summary: None of the three candidates passed2018-22 design. Primary5min:{int(primary.trades)}trades,
net${primary.total:,.2f}/NQ,trade t{primary.t_trade:.3f},dailyNW5 t{primary.t_nw5:.3f}. Other candidates had25/20trades.
The switch fails uniform and own-volume/time-stratified random-drop checks. No2023+returns tested.
Program50counted evaluations/49unique rules retained; no t4.5/t5/t6 event. Continue a DISTINCT mechanism.

Plan: agents/codex/plans/relative_turnover_switch.md, prereg9d82548.
Scripts: analysis/codex_relative_turnover_switch.py and analysis/codex_relative_turnover_switch_report.py.
Outputs: analysis/outputs/codex_relative_turnover_switch/.
Five models:3candidates+2unselectable own-volume/price controls. Prior45evaluations/44unique; plus unknown
larger repository/author searches. Overlapping windows and random subsets are additional NON-SELECTABLE
return diagnostics, not capitalized portfolios or fresh independent trials. All controls remain unselectable.

## Trade as tested

At5/15min closes09:00--14:00CT, R=Vnq*20*Cnq/(Ves*50*Ces). Normalize each clock bar by the median R on
exact prior20normal research dates,min15valid joint observations,excluding today. Previous bar must have
its own normalized ratio<=1; current>=1.5(primary5min/15min)or2(one5minvariant). OwnNQrelativevolume>=1,
ES>=0.5, same-clock prior medians. Current NQ body>=50%range and close in top25%(long)orbottom25%(short).

OnlyNQtraded; ES quantity is a reference. No price residual, old strategy ticket, VXNforecast or OPPpathfilter.
Entryj+2nativeopen(oneextra minute),stop0.10prior15weekdayATR,target0.20,ceilto0.25,activeentrybar;
exitmin(j+45,14:55),max4/day,oneposition,no stale/sameclose signals/BE/trail/overnight/resizing.
NQ$7.25RT+1tick($5)/market-stopfill; nativeMNQ$1.24RT+$0.50/fill independently. Target1pointthrough,
worse-open stop gaps and fixed4tickfill stress. Calendar-normal dates,noJuly3/Dec24,standardquarterlyrollguard.
Complete bothmarkets/current+previous bars; no current-day future-completeness mask or forwardfill.

Controls retain current-candle price/own-volume conditions and all data/history eligibility but omit both
peer-switch tests. A shift in relative turnover is a quantity proxy, not net buying or observed institutional
rotation. The proposed continuation mechanism was unproven and fails this screen.

## Design results

2018-22 only; dollars/NQ except net_mnq rows in nativeMNQ. Standard shared metrics, cashdayzeros,initialzeroDD,
all/long/short/year,NW5/NW20,cost/native/stress. Signal features and execution counts preserved.

'''+S.table(m)+'''

## Actual capped controls

Actual capped ledgers are not nested; these totals/DD compare whole strategies. No fabricated actual removed
trade list is inferred by joining different execution paths.

```json
'''+json.dumps(actual,indent=2)+'''
```

## Independent-window diagnostics: uniform dropping

All qualified windows retain original brackets/timeexits/costs but overlap. These are explicitly NON-EXECUTABLE
sums and DD. Base/kept/removed totals, removedmean/t, and1000matched-size random subsets follow:

```json
'''+json.dumps(uniform,indent=2)+'''
```

## Own-volume and time-matched dropping

1000random subsets keep the candidate's count in each signalhour x NQrelativevolume bin([1,1.5),[1.5,2),[2,inf)).
This controls some own-volume/time concentration; it neither proves causality nor makes overlapping windows
an executable portfolio. Full1000totals/DD arrays are in design_stratified_drops.json. No placebo/cell selected.

```json
'''+json.dumps(summary,indent=2)+'''
```

## Data, clocks and remaining limits

```json
'''+json.dumps(dict(intake=intake,date_mapping=mapping),indent=2)+f'''
```

Current generic exporter emits Ticks. Intake-only2018OFcorroboration has{audit['matched_rows']:,}matched minute
rows; nativeNQquantity equals aggressive-buy+sell sum on{audit['fraction_native_equals_up_plus_down']:.4%},
versus{audit['fraction_native_equals_up_only']:.4%}matching buys alone. This supports total-quantity interpretation
in that sample, NOT all-year/ES/export-vintage/contract parity. OF fields do not enter the strategy. Exporter/
audit source hashes are retained. Native source roll-switch timing is not independently verified.

Synthetic checks passed notional units, long/short price symmetry, current/previous switch and own-volume
guards, prior-only medians invariant to current/future mutation, exact missing-data windows without stretching,
and shared calendar/entrybar/gap/through/delay checks. Source hashes, all eligible signal features, rolls/date
mapping and suppression/missing-entry counts are preserved. Held-gap tickets acrossactual ledgers:{len(gaps)},
retained in design_held_gap_tickets.csv, never deleted. All rawdata/reference checks have their stated limits.

No basic/complete candidate pass. No2023+validation, expensive post-pass placebos/resampling/MC, accountbench,
independent promotion orPowerLanguage. Positive small-count variants are not t4.5/t5/t6; do not lower thresholds,
flip direction, tune exits or nominate controls after seeing this failure. Continue a distinct mechanism.
Actual raw-data execution completed{execution['completed_utc']}; see design_verified_execution.json.
Claude review path: agents/codex/results/relative_turnover_switch.md.
'''
    (ROOT/'agents/codex/results/relative_turnover_switch.md').write_text(report)
    if update_program:
        p=ROOT/'agents/codex/research/t6_progress.json';q=json.loads(p.read_text());n=q['new_standalone_economic_configurations_tested']
        if n not in (45,50) or (n==50 and q['latest_completed_hypothesis']!=NAME):raise ValueError('Newer/concurrent state; report saved, program update refused')
        q.update(status='researching',goal_met=False,latest_completed_hypothesis=NAME,
            latest_result=f"All3candidates failed2018-22;primary{int(primary.trades)}trades net${primary.total:,.2f}/NQ,trade t{primary.t_trade:.3f},NW5 {primary.t_nw5:.3f};others25/20tickets. No2023+tested; continue DISTINCT research.",
            new_standalone_economic_configurations_tested=50,unique_economic_configurations=49,
            trial_count_note='50conservative configuration evaluations include one repeated source-control nomination;49unique economic rules. Unknown older searches and diagnostic paths remain relevant.',
            last_report='agents/codex/results/relative_turnover_switch.md',
            next_action='Formulate a DISTINCT mechanism after reviewing prior research. Commit evidence and <=5-model preregistration before returns. Do not lower failed peer-turnover thresholds, flip direction, tune exits or nominate their controls.')
        q['research_continuation']['last_verified_execution']={**execution,'hypothesis':NAME,'phase':'design','models_tested':5,
            'report':'agents/codex/results/relative_turnover_switch.md','execution_marker':'analysis/outputs/codex_relative_turnover_switch/design_verified_execution.json'}
        # Rejecting another family does not erase earlier milestone history,
        # create an alert or pause the continuation task.
        p.write_text(json.dumps(q,indent=2)+'\n')
        p=ROOT/'agents/codex/research/t6_program.md';s=p.read_text()
        if '| NQ Relative Turnover Switch |' not in s:
            s=s.replace('The repository has hundreds',f'| {NAME} | Rejected |5models;primary{int(primary.trades)}trades,t{primary.t_trade:.3f},NW5 {primary.t_nw5:.3f};no2023+tested;program50/49unique |\n\nThe repository has hundreds')
            s=s.replace('\n\n| NQ Relative Turnover Switch |','\n| NQ Relative Turnover Switch |')
        p.write_text(s)
    print('Report saved. Rejected design; no milestone event. Program update:',update_program)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--update-program',action='store_true');a=p.parse_args();main(a.update_program)
