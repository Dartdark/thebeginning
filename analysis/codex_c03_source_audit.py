"""Static C03 source audit and illustrative order-state cases; no strategy replay.

The examples show code-permitted conditions, not measured fills or performance.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'agents/codex/inputs/c03/source.txt'
OUT = ROOT / 'analysis/outputs/codex_c03_source_audit'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    source = SOURCE.read_text()
    code = re.sub(r'\{.*?\}', '', source, flags=re.S)
    block = re.search(r'Inputs:(.*?)Variables:', code, re.S | re.I).group(1)
    defaults = {}
    for key, value in re.findall(r'(\w+)\(\s*([\d.]+|true|false)\s*\)', block, re.I):
        defaults[key] = value.lower() == 'true' if value.lower() in ('true', 'false') else float(value)
    assert defaults['FlatTime'] == 1545 and defaults['ATRLen'] == 20
    entry_block = code.split('If MarketPosition = 0 and Armed then begin')[1].split('PosPrev =')[0]
    arm_block = code.split('Armed = false;')[2].split('If MarketPosition <> 0 then begin')[0]
    flags = dict(explicit_IOG_off=bool(re.search(r'IntrabarOrderGeneration\s*=\s*false', code, re.I)),
                 builtin_protective_stop=bool(re.search(r'\bSetStopLoss\b', code, re.I)),
                 positive_swing_risk_guard='RiskPts > 0 and RiskPts <=' in code,
                 excludes_fill_minute_extremes='If CurrentBar > EntryBarNum then begin' in code,
                 explicit_delayed_protection='ProtOn = false;' in code and 'ProtOn = true;' in code,
                 this_bar_on_close_count=len(re.findall(r'this\s+bar\s+on\s+close', code, re.I)),
                 entry_submission_has_deadline_guard=bool(re.search(r'FlatSM|EntryTd|CalOpen|SessMin', entry_block)),
                 source_has_NQ_point_value_guard=bool(re.search(r'AbsValue\(BPVal - 20\)', code)))
    assert flags['explicit_IOG_off'] and flags['positive_swing_risk_guard']
    assert flags['excludes_fill_minute_extremes'] and not flags['builtin_protective_stop']
    assert not flags['entry_submission_has_deadline_guard']
    assert 'FlatSMEff' not in arm_block and 'CalOpen' not in arm_block
    # Assume all non-clock signal conditions are satisfied on the terminal slot.
    early = dict(scheduled_close_hhmm=1200, qualifying_signal_hhmm=1200, market_position=0,
                 effective_flat_hhmm=min(defaults['FlatTime'], 1200),
                 signal_clock_allows=defaults['SigFirstTime'] <= 1200 <= defaults['SigLastTime'],
                 open_position_exit_block_runs=False,
                 code_can_arm_next_bar_limit=True,
                 next_observed_bar_may_be_evening=True,
                 actual_fill_requires_platform_session_TIF_validation=True)
    assert early['signal_clock_allows'] and early['effective_flat_hhmm'] == early['qualifying_signal_hhmm']
    cases = dict(
        early_close_pending_entry=early,
        missing_slot_end=dict(limit_intended_slot_end='09:15', last_observed_bar='09:14',
                              missing_bar='09:15', next_observed_bar='09:16',
                              source_processes_fill_before_late_expiry=True,
                              note='Possible source path; no historical order fill or count asserted.'),
        ordinary_delayed_protection=dict(fill_minute_stamp='09:01', protective_orders_generated_at_stamp='09:15',
                                         first_eligible_protective_order_bar_stamp='09:16',
                                         note='With ordinary uninterrupted data; not a simulated fill result.'),
        native_symbol_guard=dict(NQ_point_value=20, native_MNQ_point_value=2,
                                 rejects_native_MNQ=(abs(2-20) > .000001)),
        nonpositive_risk=dict(example_signed_R=-1, accepted_as_swing=(-1 > 0 and -1 <= 3*10),
                              source_uses_fallback_instead=True))
    summary = dict(operation='static source/conditional order-state review', new_strategy_return_trials=0,
                   compiler_or_MultiCharts_run=False, raw_MC_report_supplied=False,
                   prior_Kusho_flattening_results_attributable_to_C03=False,
                   defaults=defaults, source_flags=flags, synthetic_cases=cases,
                   inventory_snapshot='e7c394f', uploaded_source_instructions_not_executed=True)
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    manifest = dict(input_sha256={str(SOURCE.relative_to(ROOT)): sha(SOURCE)},
                    code_sha256={str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
                    inspected_comparison_sources={
                        p: sha(ROOT/p) for p in ['agents/codex/inputs/kusho/far_final.txt',
                                                'agents/codex/inputs/kusho/v9.txt',
                                                'agents/codex/inputs/kusho/overview_extracted.txt']})
    (OUT / 'reproduction.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(dict(source_flags=flags, synthetic_cases=cases, new_strategy_return_trials=0), indent=2))


if __name__ == '__main__':
    main()
