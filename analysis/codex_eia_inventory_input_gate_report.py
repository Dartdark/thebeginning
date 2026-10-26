"""Report an EIA source-intake research iteration without inventing a return test."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_eia_inventory_input_gate'
REPORT = 'agents/codex/results/eia_inventory_input_gate.md'
PLAN = 'agents/codex/plans/eia_inventory_input_gate.md'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(update_program=False):
    coverage = json.loads((OUT / 'coverage.json').read_text())
    calendar = json.loads((OUT / 'calendar_audit.json').read_text())
    access = json.loads((OUT / 'access_gate.json').read_text())
    audit = pd.read_csv(OUT / 'design_component_audit.csv')
    panel = pd.read_csv(OUT / 'design_components.csv')
    dates = pd.to_datetime(panel.release_date)
    columns = ['crude_ex_spr_change_mb', 'gasoline_change_mb', 'distillate_change_mb']
    frequency = []
    for year in range(2018, 2023):
        values = panel.loc[dates.dt.year.eq(year), columns].to_numpy(float)
        signs = np.sign(values)
        frequency.append(dict(year=year, complete_source_triples=len(values),
            all_three_increase=int((signs == 1).all(axis=1).sum()),
            all_three_decrease=int((signs == -1).all(axis=1).sum()),
            aggregate_increase=int((values.sum(axis=1) > 0).sum()),
            aggregate_decrease=int((values.sum(axis=1) < 0).sum()),
            aggregate_unchanged=int((values.sum(axis=1) == 0).sum())))
    pd.DataFrame(frequency).to_csv(OUT / 'design_input_frequency.csv', index=False)
    notices = []
    for path in sorted((OUT / 'serial_sources').glob('*.json')):
        record = json.loads(path.read_text())
        text = record.get('issue_document_text') or ''
        text = re.sub(r'^L\d+:\s*', '', text, flags=re.M)
        text = re.sub(r'\s+', ' ', text)
        for match in re.finditer(r'\b(?:corrected|correction|revised|revision)\b', text, flags=re.I):
            notices.append(dict(source_key=record.get('source_key', path.stem),
                                source_filename=str(path.relative_to(ROOT)),
                                matched_word=match[0], context=text[max(0, match.start()-100):match.end()+150]))
    pd.DataFrame(notices, columns=['source_key', 'source_filename', 'matched_word', 'context']).to_csv(
        OUT / 'design_issue_notice_scan.csv', index=False)
    activity = dict(kind='source_intake_and_audit', completed_utc=datetime.now(timezone.utc).isoformat(),
        workspace=str(ROOT), actual_source_data_processing=True, futures_price_files_opened=False,
        strategy_return_tests_run=False, new_economic_configuration_evaluations=0,
        expected_design_editions=coverage['expected_editions'],
        serial_sources_present=coverage['serial_source_files_present'],
        identities_verified=coverage['identities_verified'], complete_component_triples=coverage['complete_triples'],
        unresolved_component_rows=len(coverage['excluded_source_keys']),
        parser='analysis/codex_eia_inventory_input_gate.py', parser_sha256=digest(ROOT / 'analysis/codex_eia_inventory_input_gate.py'),
        source_calendar_sha256=digest(OUT / 'design_archive_calendar.csv'),
        coverage='analysis/outputs/codex_eia_inventory_input_gate/coverage.json', report=REPORT)
    (OUT / 'research_activity.json').write_text(json.dumps(activity, indent=2) + '\n')
    report = f'''# CL inventory components: NEEDS DATA; source intake only

Summary: Acquired and audited a new EIA fundamentals input; no strategy returns were calculated.
The design calendar has {calendar['editions']} editions on {calendar['distinct_release_dates']} dates; {coverage['complete_triples']} component triples pass source/text checks.
{len(coverage['excluded_source_keys'])} editions remain excluded; historical exception clocks, revisions and native execution inputs need review.
Program remains 60 evaluations/58 unique rules. No design-pass or t4/4.5/5/6 milestone; continue research.

Plan: {PLAN}, source-intake commit5723c95. This is not an economic preregistration.
Scripts: analysis/codex_eia_inventory_input_gate.py and analysis/codex_eia_inventory_input_gate_report.py.
Outputs: analysis/outputs/codex_eia_inventory_input_gate/. New economic/return trials:0.

## New input and what was actually done

Official EIA archived Highlights contain weekly commercial crude inventories excluding SPR, total motor
gasoline and distillate fuel changes, all in million barrels. Those components could distinguish total-stock
tightening from crude transferred into refined products. The older CL tests used calendars, price reactions
and sweep patterns. No claim of a compulsory order, consensus surprise, slow pricing or profitable trade
has been established. No entry/exit/threshold family has been selected from returns.

The calendar was reconstructed from the official archive's release-date and data-ending columns, not from
a Wednesday shortcut. Every week ending {calendar['first_week_ending']}–{calendar['last_week_ending']} appears once.
There are223Wednesday,33Thursday and5Friday editions. June29,2022 has two distinct editions, including the
delayed June17 data. A date alone is not a unique key. Calendar dates do not prove exact intraday availability.

The source collector followed actual issue/Highlights links through the connected web app. Converted source
blocks, canonical URLs, captureUTC and explicit unknowns are retained. Original PDF bytes were not downloaded;
the stored SHA256 values identify converted-source JSON, not raw PDF bytes or first-publication files.
Concurrent web reference resolution initially returned some wrong editions. Those failed attempts remain in
acquired/ and verified_sources/ with their audits; the ingestion code ignores both directories. The admitted
panel is rebuilt only from serial_sources/ after independent identity checks. No wrong source is backfilled
from a later edition, current time series, sample value or price move.

## Source identity, parsing and complete coverage audit

Before extracting values, the script checks calendar sourcekey/release/week identifiers, the actual converted
document header URLs, exact same-issue Highlights path, one-page PDF metadata and first PDF week-ending.
The delayed June2022 edition has its own source path. A malformed2019-01-09HTML week header is flagged;
PDF/index agreement remains mandatory. Missing, mismatched and ambiguous sources have explicit audit rows.

The parser uses signed weekly change sentences, with exact inventory subjects, million-barrel units and
last-week/previous-week scope. It rejects annual wording, missing/duplicate amounts and ambiguous unchanged
language. It does not subtract rounded stock levels: the2022-12-29crude change is+0.7, even though rounded
levels419.0−418.2give+0.8. Five actual saved sample responses across2018–22 reconcile numerically. Synthetic
tests include units, weekly scope, wrong URLs/weeks, duplicate editions and distinguishing ordinary5,403data
from an actualHTTP403 error.

```json
'''+json.dumps(coverage, indent=2)+'''
```

All261calendar rows—including failures—are retained in design_component_audit.csv. The usable observations
and per-source hashes are in design_components.csv. design_input_frequency.csv contains fundamental-only
counts, not trade counts or P&L; no rule is selected from these counts. A keyword scan of observed issue
notices is retained in design_issue_notice_scan.csv; it is not proof that every correction is identified.

## Remaining gates before any strategy return test

The original2018/2022AppendixB describes normal Highlights publication at10:30Eastern, earlier than the
full report. Actual historical receipt, holiday/disruption clocks and field-specific corrections require their
own handling. The2018June27issue documents an updated production statistic; that alone does not establish
an inventory-field correction. A2026notice records an inventory-summary sign corrected after initial release.
That2026example is source-review evidence, not a design observation. Archived dated files are not established
as immutable first vintages. No retrospective timestamp or corrected value has been called an observed live input.

CL/MCL execution also needs explicit instrument parameters. Shared grid._walk is reusable, but NQ-specific
grid.execute/F.replay hardcode the wrong point value/costs/target-through. Do not use the old CL-net-divided-
by-ten bench as native-MCL evidence. Fees, listing history, native price parity, the energy session calendar,
continuous-contract roll treatment and missing/negative-price coverage remain scoped preflight items.
See agents/codex/research/eia_cl_execution_preflight.md. No proxy-derived account improvement is claimed.

## Scoped source-access blocker and prepared next action

The connected web tool explicitly stopped further calls after its capacity limit. The direct-fetch preflight
confirms that www.eia.gov is absent from this executor's restricted host policy. No direct network request,
proxy change, policy bypass, broker setting or API configuration change was attempted. Existing workspace
and raw futures data remain available; this blocker concerns the new EIA input acquisition.

analysis/codex_eia_inventory_fetch.py is prepared for bounded official-source downloads after reviewed host
access. Its --check-access run made zero network requests and found pdftotext available. It preserves current
PDF bytes/HTML/text and hashes, refuses unapproved hosts, and stops on401/403/429; native captures would
still need identity/parity/vintage review before admission. It is not a trading implementation.

Required action to finish this acquisition: allow www.eia.gov through the managed cloud environment's reviewed
network configuration. The runtime skill says: “Configuration changes require the environment configuration
workflow and its user review.” No such setting was changed here. access_gate.json retains the actual tool-stop
message and source-file hash. Do not repeatedly alert while this scoped blocker is unchanged.

Resume the committed source intake first: resolve excluded editions, audit clock/revision notices and source
parity, then decide whether the evidence merits TEST. Only then commit an economic plan with<=5configurations
before2018–22returns. No2023+strategy validation, trade ledgers, t statistic, promotion check, account bench or
PowerLanguage was produced here. Input work does not complete t6 or create an intermediate t milestone.
The separate source-access blocker requires the action above; the research continuation remains enabled.
Last completed strategy-return experiment remains the rejected
Correlation Risk Budget study; its execution marker and all prior performance/milestone history are preserved.
Claude review path: '''+REPORT+'''.
'''
    (ROOT / REPORT).write_text(report)
    if update_program:
        path = ROOT / 'agents/codex/research/t6_progress.json'
        progress = json.loads(path.read_text())
        if (progress['new_standalone_economic_configurations_tested'] != 60 or
                progress['latest_completed_hypothesis'] != 'NQ Correlation Risk Budget'):
            raise ValueError('Newer/concurrent program state; report saved but update refused')
        progress['active_work'] = dict(name='CL Inventory Components', stage='source_intake_access_blocked',
            plan=PLAN, plan_commit='5723c95', evidence='agents/codex/evidence/eia_inventory_components.md',
            report=REPORT, output='analysis/outputs/codex_eia_inventory_input_gate/',
            new_return_trials=0, component_triples=coverage['complete_triples'],
            excluded_editions=len(coverage['excluded_source_keys']), economic_preregistration_committed=False)
        progress['next_action'] = ('Resume committed EIA component source intake5723c95: verify reviewed www.eia.gov '
            'network access before running the prepared bounded fetcher; never bypass the policy or repeat web calls '
            'after an explicit capacity stop. Keep this blocker quiet while unchanged and keep distinct research active. '
            'resolve excluded editions listed in coverage.json, audit historical clocks/revisions and nativeCL/MCL '
            'execution inputs. No returns until TEST evidence and a separately committed<=5-configuration economic plan. '
            'Keep other distinct research available; no rescue of failed families.')
        progress['research_continuation']['last_verified_research_activity'] = activity
        event = dict(id=access['event_id'], type='genuine_input_access_blocker',
            scope=access['scope'], hypothesis='CL Inventory Components', symbol='CL / MCL',
            strategy_timeframe_minutes=None, economic_rule_frozen=False, new_trade_t=None, new_daily_nw5_t=None,
            measured_strategy_costs=None, validated_component_triples=coverage['complete_triples'],
            expected_editions=coverage['expected_editions'],
            user_action=access['action'], costs_and_execution_limitations='CL/MCL native fees/parity/session/roll checks unfinished; no return test.',
            report=REPORT, report_url='https://github.com/Dartdark/thebeginning/blob/codex/work/' + REPORT,
            evidence='analysis/outputs/codex_eia_inventory_input_gate/access_gate.json',
            reported_in_current_chat=True, phone_delivery_verified=False,
            keep_quiet_while_unchanged=True, research_continuation_paused=False)
        current = progress.get('notification_event')
        if current is not None and (not isinstance(current, dict) or current.get('id') != event['id']):
            raise ValueError('Preserve another pending notification; program update refused')
        progress['notification_event'] = event
        history = progress.setdefault('notification_event_history', [])
        if not any(item.get('id') == event['id'] for item in history):
            history.append(event)
        # Completed returns/trial counts and every intermediate milestone remain unchanged.
        path.write_text(json.dumps(progress, indent=2) + '\n')
        path = ROOT / 'agents/codex/research/t6_program.md'
        text = path.read_text()
        start, end = '<!-- EIA_INPUT_WORK_START -->', '<!-- EIA_INPUT_WORK_END -->'
        block = f'''{start}
## Work in progress: EIA component input gate

Committed source-intake plan5723c95: agents/codex/plans/eia_inventory_input_gate.md.
Current report: agents/codex/results/eia_inventory_input_gate.md. Source-only research:261editions,
{coverage['complete_triples']}verified component triples,{len(coverage['excluded_source_keys'])}excluded editions. NEEDS DATA for clocks/revisions/execution inputs;
no economic preregistration or new strategy returns. Counts remain60/58unique. Scoped EIA source-access
blocker recorded once; all t milestones unchanged. Network host www.eia.gov needs reviewed access.
Resume this source intake before new return experiments; continue the program without pausing it.
{end}

'''
        if start in text:
            a, remainder = text.split(start, 1)
            _, b = remainder.split(end, 1)
            text = a + block + b.lstrip('\n')
        else:
            text = text.replace('## Operating boundaries', block + '## Operating boundaries')
        path.write_text(text)
    print(json.dumps(dict(report=REPORT, new_strategy_return_trials=0,
                          complete_triples=coverage['complete_triples'], excluded=len(coverage['excluded_source_keys']),
                          program_updated=update_program, notification_event_id=access['event_id'])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--update-program', action='store_true')
    args = parser.parse_args()
    main(args.update_program)
