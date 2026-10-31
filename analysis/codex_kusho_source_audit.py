"""Static Kusho document/code audit, without prices, backtests or account runs.

Text extraction uses pdftotext -layout with overview.pdf as input and
overview_extracted.txt as output, both under agents/codex/inputs/kusho/.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import re

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'agents/codex/inputs/kusho'
OUT = ROOT / 'analysis/outputs/codex_kusho_source_audit'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    text = (INPUT / 'overview_extracted.txt').read_text().replace('\u2060', '').replace('−', '-')
    rows = []
    for y, n1, p1, n2, p2 in re.findall(
            r'^\s*(20\d{2})\s+(\d+)\s+(-?\$[\d,.]+)\s+(\d+)\s+(-?\$[\d,.]+)\s*$', text, re.M):
        money = lambda p: float(p.replace('$', '').replace(',', ''))
        rows.append(dict(year=int(y), far_trades=int(n1), far_claimed_net_MNQ=money(p1),
                         v9_trades=int(n2), v9_claimed_net_MNQ=money(p2)))
    assert len(rows) == 10 and [r['year'] for r in rows] == list(range(2017, 2027))
    with (OUT / 'overview_annual_claims.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    totals = {}
    for label, keep in [('full', lambda y: True), ('2017_22', lambda y: y <= 2022),
                        ('2018_22', lambda y: 2018 <= y <= 2022), ('2023_plus', lambda y: y >= 2023)]:
        totals[label] = {k: sum(r[k] for r in rows if keep(r['year'])) for k in rows[0] if k != 'year'}
    assert totals['full'] == dict(far_trades=3142, far_claimed_net_MNQ=31448,
                                 v9_trades=3586, v9_claimed_net_MNQ=40308)
    flags = {}
    for name in ['far_final.txt', 'v9.txt']:
        source = (INPUT / name).read_text()
        executable = re.sub(r'\{.*?\}', '', source, flags=re.S)
        defaults = {key: float(re.search(r'\b' + key + r'\(\s*([\d.]+)\s*\)', source).group(1))
                    for key in ['EODTime', 'MaxSwingRiskTicks', 'SwingRR', 'SwingBE_R',
                                'BEPufferTicks', 'WickTolTicks', 'HardStopTicks', 'TargetTicks']}
        flags[name] = dict(defaults=defaults,
                           iog_directive_present=bool(re.search(r'IntrabarOrderGeneration', executable, re.I)),
                           builtin_stop_present=bool(re.search(r'\bSetStopLoss\b', executable, re.I)),
                           builtin_target_present=bool(re.search(r'\bSetProfitTarget\b', executable, re.I)),
                           positive_RiskTicks_guard_present=bool(re.search(r'RiskTicks\s*>\s*0', executable, re.I)),
                           stop_orders_next_bar=len(re.findall(r'next\s+bar\s+at\s+DynamicSL\s+stop', executable, re.I)))
        assert defaults['EODTime'] == 2100
        assert not flags[name]['iog_directive_present']
        assert not flags[name]['builtin_stop_present'] and not flags[name]['positive_RiskTicks_guard_present']
    # Synthetic arithmetic counterexamples: no historical frequency or simulated return.
    default = flags['v9.txt']['defaults']
    tick, entry = .25, 100.
    bad_swing = {}
    for side, swing in [('long', 101.), ('short', 99.)]:
        risk = entry - swing if side == 'long' else swing - entry
        target = entry + risk * default['SwingRR'] if side == 'long' else entry - risk * default['SwingRR']
        bad_swing[side] = dict(synthetic_entry=entry, synthetic_swing=swing, risk_ticks=risk/tick,
                               passes_upper_bound=(risk/tick <= default['MaxSwingRiskTicks']), target=target,
                               source_never_checked_positive_risk=True)
        assert bad_swing[side]['passes_upper_bound'] and risk < 0
    be = dict(synthetic_limit_entry=100., valid_swing_stop=90., entry_bar_high_before_fill=110.,
              highest_price_after_fill=102., entry_bar_close=101.)
    be['trigger'] = be['synthetic_limit_entry'] + (be['synthetic_limit_entry']-be['valid_swing_stop'])*default['SwingBE_R']
    be['source_bar_high_arms_BE'] = be['entry_bar_high_before_fill'] >= be['trigger']
    be['post_fill_excursion_arms_BE'] = be['highest_price_after_fill'] >= be['trigger']
    be['raised_stop'] = be['synthetic_limit_entry'] + default['BEPufferTicks']*tick
    assert be['source_bar_high_arms_BE'] and not be['post_fill_excursion_arms_BE']
    assert be['raised_stop'] > be['entry_bar_close']
    published_sides = dict(v9_long_trades=3116, v9_short_trades=470,
                           v9_long_net_MNQ=31794, v9_short_net_MNQ=8514)
    assert published_sides['v9_long_trades'] + published_sides['v9_short_trades'] == totals['full']['v9_trades']
    assert published_sides['v9_long_net_MNQ'] + published_sides['v9_short_net_MNQ'] == totals['full']['v9_claimed_net_MNQ']
    summary = dict(operation='source/document arithmetic and synthetic code counterexamples only', new_strategy_return_trials=0,
                   independently_reproduced_strategy_performance=False, claimed_annual_totals=totals,
                   author_reported_sides=published_sides,
                   incremental_claim_arithmetic=dict(total_net_MNQ=40308-31448, short_net_MNQ=8514,
                                                     long_net_change_MNQ=31794-31448,
                                                     long_count_change=3116-3142,
                                                     net_trade_count_change=3586-3142),
                   source_flags=flags, synthetic_wrong_side_swing=bad_swing, synthetic_BE_pre_fill_case=be,
                   power_arithmetic_only={side:dict(claimed_design_n=totals['2018_22'][key],
                                                   mean_for_t2_as_multiple_of_unknown_SD=2/math.sqrt(totals['2018_22'][key]))
                                          for side, key in [('far', 'far_trades'), ('v9', 'v9_trades')]},
                   NQ_default_point_arithmetic=dict(tick=.25, wick_points=70*.25, fallback_stop_points=200*.25,
                                                    max_positive_swing_risk_points=500*.25,
                                                    fallback_nominal_MNQ_risk=200*.25*2,
                                                    max_positive_swing_nominal_MNQ_risk=500*.25*2),
                   repo_inventory_snapshot='e7c394f', raw_MC_reports_supplied=False,
                   instructions_in_uploaded_sources_not_executed=True)
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    manifest = dict(input_sha256={str(p.relative_to(ROOT)): sha(p) for p in sorted(INPUT.iterdir())},
                    code_sha256={str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
                    claim_source='Uploaded overview; figures checked arithmetically, not validated as backtest results.')
    (OUT / 'reproduction.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(dict(totals=totals, incremental=summary['incremental_claim_arithmetic'],
                         source_flags=flags, new_strategy_return_trials=0), indent=2))


if __name__ == '__main__':
    main()
