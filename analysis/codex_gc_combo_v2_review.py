"""GC_COMBO_v2 source, input-format and reported-arithmetic audit only.

Never runs a strategy, reads market-price grids, estimates new returns or simulates an account.
Author-reported figures are transcribed from the supplied five-page research note.
"""
import csv
from datetime import date, datetime, timedelta
from decimal import Decimal as D
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'agents/codex/inputs/gc_combo_v2'
OUT = ROOT / 'analysis/outputs/codex_gc_combo_v2_review'


def main():
    source = (INPUT / 'strategy.txt').read_text()
    note = (INPUT / 'report_extracted.txt').read_text()
    with (INPUT / 'GCCOMBO.txt').open(newline='') as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        rows = list(reader)
    dates = [datetime.strptime(r['Date'], '%m/%d/%Y').date() for r in rows]
    assert dates == sorted(dates) and len(dates) == len(set(dates))
    weekdays = set()
    d = dates[0]
    while d <= dates[-1]:
        if d.weekday() < 5:
            weekdays.add(d)
        d += timedelta(days=1)
    opens = sorted({D(r['Open']) for r in rows})
    closes = sorted({D(r['Close']) for r in rows})
    invalid_ohlc = sum(not (D(r['Low']) <= min(D(r['Open']), D(r['Close']))
                               <= max(D(r['Open']), D(r['Close'])) <= D(r['High'])) for r in rows)
    data = dict(rows=len(rows), first_date=str(dates[0]), last_date=str(dates[-1]),
                columns=columns, timestamps=sorted({r['Time'] for r in rows}),
                open_values=list(map(str, opens)), close_values=list(map(str, closes)),
                volumes=sorted({r['Volume'] for r in rows}), duplicate_dates=0,
                non_weekdays=sum(x.weekday() >= 5 for x in dates),
                missing_weekdays=len(weekdays-set(dates)), invalid_ohlc=invalid_ohlc,
                encoded_decouple_values=[str(v-D(10)) for v in opens],
                encoded_gld_values=[str(v-D(10)) for v in closes],
                timestamp_is_publication_evidence=False)
    assert data['rows'] == 2605 and not invalid_ohlc and data['missing_weekdays'] == 0
    assert opens == [D(10), D(11)] and closes == [D(9), D(10), D(11)]
    flags = dict(
        default_gld_and_decouple_on='UseVoteGLD(true)' in source and 'UseVoteDecouple(true)' in source,
        data3_date_gate='if Date of data3 = Date then begin' in source,
        blend_continues_without_data3='if MarketPosition = 0 and stretchSig = false and blendAllowed and blQty >= 1 then begin' in source,
        blend_dollar_stop_off='UseDollarStop(false)' in source,
        risk_sizing_off='UseRiskSizing(false)' in source,
        optional_risk_budget_5000='MaxLossUSD(5000)' in source,
        stretch_stop_prearmed='if sleeve = 2 or stretchSig then begin' in source,
        optional_blend_cap_post_position='if sleeve = 1 and UseDollarStop and MarketPosition <> 0 then begin' in source,
        blend_exact_clock_exit='if sleeve = 1 and tET = BlendExitET then begin' in source,
        stretch_exact_clock_exit='if sleeve = 2 and tET = StretchExitET then BuyToCover' in source,
        explicit_early_close_code=any(k.lower() in source[source.index('inputs:'):].lower()
                                      for k in ['IsEarlyClose', 'EarlyFlatten', 'Holiday']),
        stretch_range_is_mean_session_hl='rngs[1] = sessHi - sessLo;' in source and 'atrPts = atrPts / AtrLen;' in source,
        data1_up_down_flow='flowSum = flowSum + UpTicks - DownTicks;' in source,
        true_bid_ask_signed_data_supplied=False,
        gld_and_decouple_generator_supplied=False,
    )
    assert all(flags[k] for k in ['default_gld_and_decouple_on','data3_date_gate',
        'blend_continues_without_data3','blend_dollar_stop_off','risk_sizing_off','optional_risk_budget_5000',
        'stretch_stop_prearmed','optional_blend_cap_post_position','blend_exact_clock_exit',
        'stretch_exact_clock_exit','stretch_range_is_mean_session_hl','data1_up_down_flow'])
    assert not flags['explicit_early_close_code']
    inputs = source.split('inputs:', 1)[1].split('variables:', 1)[0]
    names = ['ETminusChart','MinScore','ConvictionScore','BaseQty','ConvictionQty','AnchorET','DecisionET',
             'BlendExitET','OilZ','OilLen','StretchQty','StretchK','StopATR','TargetR','AtrLen',
             'StretchStartET','StretchEndET','StretchExitET','MaxSigPerSess','SigGapBars',
             'UseDollarStop','MaxLossUSD','UseRiskSizing','WorstMovePct']
    defaults = {name:re.search(r'\b'+name+r'\(\s*([^)]*)\)', inputs).group(1).strip() for name in names}
    # A static score example, not a market return: dropping C/E changes entry eligibility.
    vote_example = dict(A=1, B=1, C=-1, D=0, E=0)
    assert vote_example['E'] in (0, vote_example['A'])
    vote_example['five_vote_score'] = sum(vote_example.values())
    vote_example['score_without_data3'] = vote_example['A']+vote_example['B']+vote_example['D']
    assert vote_example['five_vote_score'] == 1 and vote_example['score_without_data3'] == 2
    reported = dict(all_trades=1204, net_usd='225916', average_usd='187.64', win_rate='0.525',
                    pf='1.37', max_drawdown_usd='43747', is_trades=974, is_average_usd='163.71',
                    oos_trades=230, oos_average_usd='288.98', oos_win_rate='0.465',
                    is_gross_bp='7.5', oos_gross_bp='4.4', oos_t_gross_bp='0.9',
                    programme_trials=10831, author_says_dsr_fails=True,
                    direction_pairs_claimed=884, lucid_pass='0.90', lucid_bust='0.049')
    for s in ['1,204', '225,916', '187.64', '1.37', '43,747', '163.71', '288.98', '10,831', 't 0.9']:
        assert s in note, 'Reported figure absent from extracted note: '+s
    by_year_counts = {'2017':29,'2018':122,'2019':136,'2020':123,'2021':133,
                      '2022':156,'2023':119,'2024':156,'2025':157,'2026':73}
    assert sum(by_year_counts.values()) == reported['all_trades']
    assert sum(n for y,n in by_year_counts.items() if int(y) <= 2024) == reported['is_trades']
    weighted = D(reported['is_trades'])*D(reported['is_average_usd'])+D(reported['oos_trades'])*D(reported['oos_average_usd'])
    rounding_tolerance = D(reported['all_trades'])*D('.005')
    arithmetic = dict(
        counts_reconcile=reported['is_trades']+reported['oos_trades']==reported['all_trades'],
        year_counts_reconcile=sum(by_year_counts.values())==reported['all_trades'],
        weighted_net_from_rounded_period_means=str(weighted),
        difference_from_reported_net=str(weighted-D(reported['net_usd'])),
        mean_rounding_tolerance=str(rounding_tolerance),
        rounded_means_consistent=abs(weighted-D(reported['net_usd'])) <= rounding_tolerance,
        reported_2018_2022_trades=sum(n for y,n in by_year_counts.items() if 2018<=int(y)<=2022),
        mfe_mae_daily_paths_and_net_return_sd_supplied=False)
    assert arithmetic['rounded_means_consistent']
    # Contract arithmetic only; 1 GC -> 1 MGC with the same count/path before micro fee differences.
    scaling = dict(gc_multiplier=100, mgc_multiplier=10, gc_tick_usd=10, mgc_tick_usd=1,
                   commission_per_gc_side='2.30', two_one_tick_sides_gc_cost=str(D('2.30')*2+D(10)*2),
                   illustrative_same_count_mgc_dd=str(D(reported['max_drawdown_usd'])/10),
                   apex_initial_eod_trail_usd=2000,
                   is_account_simulation=False, is_measured_mgc_result=False,
                   changing_data1_to_mgc_also_changes_flow_and_vwap_inputs=True)
    out = dict(scope='Source/previously reported arithmetic only',
               verdict='WATCH / NEEDS DATA; no current-plan addition established',
               claude_ref='a67035be4189b493098c80f1def979348520fd5d',
               codex_parent='df70a580bfcd906f90a4ff4f176a7cc84acdb81b',
               new_strategy_return_trials=0, account_simulations=0,
               input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted(INPUT.iterdir()) if p.is_file()},
               script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               companion_file=data, source_flags=flags, source_defaults=defaults, static_missing_data_example=vote_example,
               author_reported=reported, by_year_counts=by_year_counts, arithmetic=arithmetic,
               contract_arithmetic=scaling,
               repo_gc_header=(ROOT/'data/GC_1min_2018.csv').open().readline().strip(),
               author_preregistry_trade_list_settings_and_generator_supplied=False,
               next_evidence=['Point-in-time Data3 generator and dated raw inputs',
                   'GC up/down trade-volume history matching chart/vendor',
                   'Exact-source MultiCharts settings and timestamped trade/daily-path export',
                   'Original freeze and predeclared marks / selection ledger',
                   'Holiday and signal-vs-execution symbol specification'],
               sources=['https://www.cmegroup.com/education/lessons/product-gold',
                        'https://www.cmegroup.com/education/lessons/micro-gold-and-micro-silver-futures-product-overview'])
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'summary.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['verdict','new_strategy_return_trials','account_simulations','arithmetic','contract_arithmetic']},indent=2))


if __name__ == '__main__':
    main()
