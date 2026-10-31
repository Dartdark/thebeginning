"""Render the frozen filter experiment from saved derived results, never prices."""
import json
from pathlib import Path
import pandas as pd
import codex_choch_filters as study


def table(rows, columns):
    def fmt(x):
        if isinstance(x,float):return f'{x:,.3f}'
        return str(x)
    return '\n'.join(['| '+' | '.join(columns)+' |','| '+' | '.join(['---']*len(columns))+' |']+
                     ['| '+' | '.join(fmt(row.get(c,'')) for c in columns)+' |' for row in rows])


def render():
    d=study.OUT/'design';s=json.loads((d/'summary.json').read_text())
    primary=s['models'];out=[]
    out.append('# Hourly two-candle CHoCH filters: '+('design survivor needs next gates' if s['survivors'] else 'no filter earns advancement'))
    out.append('Summary: Five frozen configurations were evaluated on 2018–22, including the same-coverage baseline. '+
        ('Design survivors: '+', '.join(s['survivors'])+'.' if s['survivors'] else 'None passed all registered economic, removal, matched-subset and complete-data gates.')+
        ' These are one-MNQ research results, not book/trading approval. No 2023+ returns were inspected in this phase.')
    out.append(f"Plan: [preregistration](../plans/choch_h1_r2_filters_20261028.md), public commit `{s['preregistration_commit']}`. "
        f"Implementation commit `{s['implementation_commit']}`; code hashes and source hashes in [summary](../../../analysis/outputs/codex_choch_filters_20261028/design/summary.json). "
        'Scripts: [study](../../../analysis/codex_choch_filters.py), [execution](../../../analysis/codex_choch_filters_execution.py), '
        '[matched subsets](../../../analysis/codex_choch_filters_subsets.py), [report](../../../analysis/codex_choch_filters_report.py).')
    out.append('## Rule and clocks')
    out.append('The frozen hourly R=2 CHoCH foundation trades both directions: two completed candles on each side confirm a strict swing; a completed-hour close breaking the opposing swing after a structural trend triggers entry. '
        'Executable entry is OPEN(signal+2), stop at the prior confirmed opposite swing, gross target twice entry-to-stop risk. '
        'Normal decisions 09:00–14:00 CT, flatten at OPEN of close-labelled 15:58; early 09:00/10:00, flatten OPEN 11:30. One position at a time. '
        'No overnight holds or later 15:59 exits. 1:2 applies only when the target is reached; timed exits have variable payoffs.')
    out.append('F1/F1_5 require decision-close target distance <=1.0/1.5 times median remaining high–low range in the immediately prior 20 normal cash-calendar sessions. '
        'Same-clock history ends at the planned liquidation open; no later liquidation-minute extremes. Every prior window must be complete; missing windows are not replaced by older ones. '
        'A4 requires the same direction as the latest fully completed, R=2 confirmed four-hour structure state, including causal CHoCH flips and missing-bar resets. '
        'F1_A4 combines strict feasibility and alignment. Full 4h windows are anchored 17:00 CT; incomplete 13–16 stub unused. '
        'Both features are known at the signal close; the future fill does not determine acceptance.')
    out.append('## Coverage and reproducibility')
    out.append(f"Raw hourly signals {s['raw_signals']}; intraday-eligible {s['eligible_signals']}; common feature-known eligible {s['common_signals']}. "
        f"Range unavailable {s['range_unknown']}; 4h context unavailable {s['alignment_unknown']}; these can overlap. "
        'All five primary runs use the common feature-known universe. Feature availability uses only past information, never future path completeness. '
        'Warm-up/coverage exclusions are disclosed separately, not called filter alpha. Original full baseline reproduced to numerical tolerance; corrected full baseline also retained.')
    out.append(table([dict(model=m['model'],trades=m['trades'],net=m['net_total'],trade_t=m['trade_t'],NW5=m['daily_NW5'],maxDD=m['max_dd'],unresolved=m['unresolved']) for m in s['references']],['model','trades','net','trade_t','NW5','maxDD','unresolved']))
    out.append(f"Unknown-feature full-baseline attribution: `{s['coverage_exclusions']}`. Different opportunity sets can alter later entries; attribution is not an executable return series. "
        f"Dates {s['design_dates']['start']} through {s['design_dates']['end']}, full weekday daily clock including zero days. 2017 warm-up has no RTH source and can make initial historical ranges unavailable. "
        'The reconciled DAY/ON inputs and clock/calendar/source audits are hash-bound to the prior RR2 design; raw user CSVs stay local. Missing expected minutes retain unknown execution states, never zero P&L.')
    out.append('## Executable primary results / USD per MNQ')
    out.append(table([dict(model=m['model'],trades=m['trades'],win_pct=m['win']*100,net=m['net_total'],trade_t=m['trade_t'],NW5=m['daily_NW5'],Sharpe=m['sharpe'],Sortino=m['sortino'],PF=m['profit_factor'],Calmar=m['calmar'],Ulcer=m['ulcer'],maxDD=m['max_dd'],unresolved=m['unresolved'],pass_all=m['filter_design_pass']) for m in primary],['model','trades','win_pct','net','trade_t','NW5','Sharpe','Sortino','PF','Calmar','Ulcer','maxDD','unresolved','pass_all']))
    out.append('By year, net:')
    out.append(table([dict(model=m['model'],**{str(y['year']):y['net_mnq'] for y in m['years']}) for m in primary],['model','2018','2019','2020','2021','2022']))
    out.append('Both sides, same daily calendar:')
    out.append(table([dict(model=m['model'],side=x['side'],trades=x['trades'],win_pct=x['win']*100,net=x['net_total'],trade_t=x['trade_t'],Sharpe=x['sharpe'],Sortino=x['sortino'],PF=x['profit_factor'],Calmar=x['calmar'],Ulcer=x['ulcer'],maxDD=x['max_dd']) for m in primary for x in m['sides']],['model','side','trades','win_pct','net','trade_t','Sharpe','Sortino','PF','Calmar','Ulcer','maxDD']))
    out.append('## Fixed-BASE attribution and 1,000 matched random subsets per filter')
    out.append('Filters were first applied to eligible signals and execution rerun; removed signals can free later entries. Separately, filter masks were applied to resolved common BASE trade IDs. '
        'Those fixed-trade kept/removed sets and random subsets retain original exits and costs; they are diagnostic overlaps, not executable portfolios. '
        'Match exactly year × direction × signal hour and kept counts in every stratum; seed 20261028, 1,000 draws each. '
        'Profit p counts random profit >=observed; DD p counts randomDD<=observed; joint counts both; plus-one denominator1001, ties retained. '
        'Full summaries, retained memberships and daily paths are in the matched_subsets directory/archive.')
    out.append(table([dict(model=name,base=q['base_net'],kept=q['kept_net'],removed=q['removed_net'],removed_mean=q['removed']['net_mean'],removed_t=q['removed']['trade_t'],profit_p=q['p_profit'],DD_p=q['p_dd'],joint_p=q['p_joint'],unique_paths=q['unique_daily_paths'],random_strata=q['strata_with_random_choice']) for name,q in s['filter_diagnostics'].items()],['model','base','kept','removed','removed_mean','removed_t','profit_p','DD_p','joint_p','unique_paths','random_strata']))
    out.append('## Costs, execution and stress')
    out.append('Native one-MNQ cost is $1.24 round-trip commission plus one 0.25-point tick per fill ($1.00 total slippage): $2.24/trade. '
        'Gross gate requires >$4.48 mean gross. A market fill at/beyond stop now exits immediately at its fill open and pays costs; prior zero-fee deletion is preserved only as a historical reference. '
        'Same shared grid minute walker: active entry-bar protection, worse stop gaps and 1-point target-through. The nearest-extreme same-minute collision assumption is stress-tested stop-first, not selected afterward.')
    rows=[]
    for m in primary:
        t=pd.read_csv(d/(m['model']+'_trades.csv'));known=t[t.state.eq('resolved')]
        rows.append(dict(model=m['model'],gross=m['gross_total'],commission=float(known.commission_mnq.sum()),slippage=float(known.slippage_mnq.sum()),gross_mean=m['gross_mean'],extra_cost_breakeven=m['breakeven_extra_cost_per_trade'],double_cost_net=m['extra_cost_net'],stop_first_net=m['stop_first']['net_total'],collisions=m['collision_count'],entry_gap_stops=m['entry_gap_stop_count']))
    out.append(table(rows,['model','gross','commission','slippage','gross_mean','extra_cost_breakeven','double_cost_net','stop_first_net','collisions','entry_gap_stops']))
    out.append('Every original/corrected full reference, primary ledger, stop-first ledger, daily series, signal-feature table and 4h state table is retained. '
        'Synthetic checks include core-state parity, prefix/mirror/as-of/reset behavior, previous20-session clocks and missing-history rejection, future-fill invariance, entry gap charging, active stops, target-through, collision stress and early-close/time-open liquidation. '
        'Resolved trade P&L reconciles to daily P&L. Gaps not affecting known signals can still affect the full opportunity set; observed-subset performance is not a claim of a complete executable track record.')
    out.append('Independent saved-artifact checks reconciled all five ledgers, feature masks, costs, trade t/daily NW5 and all 4,000 random paths reconstructed from packed memberships. '
        'Cent-rounded comparisons change no p-values or ties. This is an artifact review, not a fresh raw-price/spec rebuild. '
        'The full derived [evidence archive](../../../analysis/outputs/codex_choch_filters_20261028/evidence.zip) includes the long selected-ID CSVs and all NPZ paths; '
        '[artifact manifest](../../../analysis/outputs/codex_choch_filters_20261028/artifact_manifest.json) records their hashes. No uploaded raw CSV is in this archive. '
        'A4 kept117 fixed-BASE trades but executed118 after signals were freed; the corresponding $1,038.92 subset and $1,048.18 executable totals are intentionally separate.')
    out.append('## Gates, selection history and five plan homes')
    out.append('Registered advancement requires >=30 resolved trades, trade t>=2, netpositive, gross hurdle, >=3/5 positive years and no unresolved paths; '
        'fixed-BASE kept total must exceed BASE, removed total negative, matched-subset profit and DD p<=.05; '
        'rerun executable total must improve BASE with no larger DD and positive stop-first/double-cost net. '
        'A prettier per-trade average, selected side/year or lower DD by itself cannot pass.')
    out.append('Five primary definitions inspected (reused BASE plus four active filters); four new active economic filter definitions. '
        'Six prior structural configurations/twelve prior economic definitions including ideal-close controls remain in family history: 16 active economic/control definitions after this phase, '
        'plus separately retained coverage, source rerun, entry-gap correction and execution stress references. '
        'The bounded Hunt v2/t6 budgets/programs stay closed. 4,000 matched diagnostic draws are selection diagnostics; all family selection history remains counted.')
    if not s['survivors']:
        out.append(table([dict(home=home,verdict='No earned slot',evidence=why) for home,why in [
            ('Personal19','Filter design gates fail; paired ADD/REPLACE/EMPTY benches not run.'),
            ('50K funded','Design fails; current T_ONESIDE-fade book and valid paired account paths not tested.'),
            ('150K funded','Design fails; valid paired funded bootstrap not run.'),
            ('50K evaluation','Design fails; synchronized joint intraday account paths not tested.'),
            ('150K evaluation','Design fails; synchronized joint intraday account paths not tested.')]],['home','verdict','evidence']))
        out.append('The stop rule applies before plan benches, Monte Carlo at plan size, random-time/random-side placebos or historical validation. '
            'No measured harm to every plan is claimed; the candidate has not earned those tests. Current personal/funded/evaluation source context is saved in [book review](../research/choch_filters_book_context.md).')
    else:
        out.append('Design survivor requires the preregistered immediate current-book bench before robustness/2023+; this report alone does not establish a slot in any of the five plans.')
    out.append('## Limitations and verdict')
    out.append('The filter choices were motivated by previously observed weak baseline results and share price information; they have no identified forced participant. '
        'No full 2018–26 t, selection-adjusted promotion, dependence/placebo pass, fresh independent raw-spec rebuild, forward evidence or account pass/payout benefit is established. '
        'Independent code review before outcomes was completed, but is not an independent financial replication. No PowerLanguage or live deployment was produced.')
    out.append('Verdict: '+('Continue only the frozen survivor through its remaining registered gates.' if s['survivors'] else 'Reject these four frozen filters as advancement candidates; stop this approved filter experiment without retuning.'))
    out.append('For Claude: review `agents/codex/results/choch_h1_r2_filters_20261028.md` and the retained ledgers/subset paths. Reproduce with `python -B analysis/codex_choch_filters.py --design` only in a clean output destination with the hash-bound local source mount; the script refuses to overwrite the original design. Render with `python -B analysis/codex_choch_filters_report.py`.')
    path=study.ROOT/'agents/codex/results/choch_h1_r2_filters_20261028.md'
    path.write_text('\n\n'.join(out)+'\n');print(path)


if __name__=='__main__':render()
