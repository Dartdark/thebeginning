"""Report/reconcile frozen output ledgers only; no market inputs or new policies."""
from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np
import pandas as pd
import metrics as M
from codex_fast_alpha_books_20261108 import daily, tstat

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'agents/codex/inputs/fast_alpha_books_20261108'
OUT=ROOT/'analysis/outputs/codex_fast_alpha_books_20261108'


def money(x):return f'${x:,.2f}'


def main():
    cfg=json.loads((BASE/'config.json').read_text());s=pd.read_csv(OUT/'design_summary.csv')
    disp=json.loads((OUT/'design_dispositions.json').read_text());days=pd.bdate_range(cfg['design_start'],cfg['design_end'])
    assert len(disp)==24 and all(d['status']=='stop_design' for d in disp)
    old=pd.read_csv(OUT/'attempt1/design_summary.csv');unchanged=[]
    for key in sorted(set(old.parent)-{'PT','KUSHO'}):
        pd.testing.assert_frame_equal(old[old.parent==key].reset_index(drop=True),s[s.parent==key].reset_index(drop=True),check_dtype=False)
        unchanged.append(key)
    table=[];metrics=[];quality=[];risk=[]
    for spec in cfg['parents']:
        k=spec['key'];st=s[s.parent==k].set_index('profile');assert len(st)==3
        streams={v:pd.read_csv(OUT/f'{k}_{v}_tickets.csv',parse_dates=['entry_at','exit_at']) for v in ['BASE','ENTRY','BOTH']}
        mask=np.logical_and.reduce([t.unknown.eq(0).to_numpy() for t in streams.values()])
        for v,t in streams.items():
            q=t[mask];fills=q[q.status=='filled'];assert np.isclose(q.net.sum(),st.loc[v,'total'])
            assert np.isclose(q.net.sum(),q.gross.sum()-q.fee.sum()-q.slippage.sum())
            for side,label in [(0,'whole'),(1,'long'),(-1,'short')]:
                for year in ['design',2018,2019,2020,2021,2022]:
                    qq=q if not side else q[q.side==side]
                    dd=days if year=='design' else days[days.year==year]
                    if year!='design':qq=qq[qq.exit_at.dt.year==year]
                    actual=qq[qq.status=='filled'];d=daily(qq,dd)
                    metrics.append(dict(parent=k,profile=v,side=label,period=year,
                        source_opportunities=len(qq),actual_fills=len(actual),missed=int(qq.missed.sum()),
                        trade_t=tstat(actual.net),**M.perf(d,actual.net)))
            for reason,n in t.status.value_counts().items():quality.append(dict(parent=k,profile=v,status=reason,tickets=int(n)))
        table.append(dict(parent=k,market=spec['market'],books=','.join(spec['books']),tickets=int(st.loc['BASE','source_tickets']),
            resolved=int(mask.sum()),unknown=int((~mask).sum()),base_total=st.loc['BASE','total'],entry_total=st.loc['ENTRY','total'],both_total=st.loc['BOTH','total'],
            entry_effect=st.loc['ENTRY','effect_total'],both_effect=st.loc['BOTH','effect_total'],
            exit_increment=st.loc['BOTH','total']-st.loc['ENTRY','total'],entry_t=st.loc['ENTRY','paired_daily_t'],both_t=st.loc['BOTH','paired_daily_t'],
            entry_missed=int(st.loc['ENTRY','missed']),both_missed=int(st.loc['BOTH','missed']),any_gate_pass=False))
        e,b=streams['ENTRY'],streams['BOTH'];ok=mask&e.status.eq('filled').to_numpy()&b.status.eq('filled').to_numpy()
        extra=b.loc[ok,'max_adverse'].to_numpy()-e.loc[ok,'max_adverse'].to_numpy()
        risk.append(dict(parent=k,paired_filled_tickets=int(ok.sum()),largest_extra_adverse_native_micro=float(max(0.,extra.max())) if len(extra) else None,
            additional_exit_minutes_max=float(b.loc[mask,'exit_delay'].max()) if mask.any() else None,
            note='Conservative observed minute-adverse measure; not tick-order or account drawdown verification.'))
    tab=pd.DataFrame(table);tab.to_csv(OUT/'parent_comparison.csv',index=False)
    pd.DataFrame(metrics).to_csv(OUT/'actual_fill_metrics.csv',index=False)
    pd.DataFrame(quality).to_csv(OUT/'quality_counts.csv',index=False)
    pd.DataFrame(risk).to_csv(OUT/'deferred_exit_risk.csv',index=False)
    full=tab[tab.unknown==0];assert len(full)==6 and (full.entry_effect<0).all() and (full.both_effect<0).all()
    assert not s.cheap_pass.eq(True).any()
    outcomes=[]
    for book,keys in cfg['books'].items():
        q=tab[tab.parent.isin(keys)];outcomes.append(dict(home=book,streams=len(keys),clean_streams=int((q.unknown==0).sum()),
            passed=0,portfolio_tests_run=False,placement='No overlay earned advancement; no account benefit demonstrated.',
            reason='All candidates fail frozen design gates; material unknown paths and source/quantity/roster limitations also block native book certification.'))
    pd.DataFrame(outcomes).to_csv(OUT/'book_placement.csv',index=False)
    checks=dict(preregistration='d06d6eaeb069edc5c15fb8d44a9908661878936a',clock_amendment='3b22c7e94e281dd79c45edc5ef75c08a44a3411b',
        parent_streams=len(tab),parent_tickets=int(tab.tickets.sum()),common_resolved_tickets=int(tab.resolved.sum()),
        executed_definitions=72,reserved_cap=120,unused_null_definitions=48,unchanged_parent_summaries=unchanged,
        source_clock_corrections=['Kusho explicit2017-12-01index origin','PT five-minute next-market-open clock minus4minutes'],
        full_path_streams=full.parent.tolist(),positive_paired_effects_too_weak_or_incomplete=tab[(tab.entry_effect>0)|(tab.both_effect>0)].parent.tolist(),
        strategy_control_or_recent_or_account_stages_earned=False,source_or_native_independent_verification=False,
        subset_warning='Common resolved tickets are a selected subset. Target qualification can remove winners, so neither its source baseline nor its effect is a full-strategy estimate.',
        metrics_denominator='Original standard_metrics uses all resolved opportunities including missed zero contributions. actual_fill_metrics separates actual fills; total and paired opportunity effect are unchanged.',
        script=subprocess.check_output(['git','hash-object',str(Path(__file__).relative_to(ROOT))],cwd=ROOT,text=True).strip())
    (OUT/'reconciliation.json').write_text(json.dumps(checks,indent=2)+'\n')
    text='''# Fast-alpha execution across the current books: no candidate earns advancement

Summary: Screened24frozen instrument/version streams spanning all five current book types; none passed design.
On all six fully resolved streams, delayed entry and combined entry/exit timing reduced net profit.
Positive conditional effects in VB/Kusho/NBL were weak and incomplete; S30/CL have especially limited path coverage.
No controls,2023+validation or account backtests were earned; no portfolio gain or live change is claimed.

Plan: [frozen protocol](../plans/fast_alpha_books_20261108.md), committed before returns at `d06d6eaeb069edc5c15fb8d44a9908661878936a`.
Clock-only amendment: `3b22c7e94e281dd79c45edc5ef75c08a44a3411b`; original attempt preserved.
[Evidence](../evidence/fast_alpha_books_20261108.md), [paper/five questions](fast_alpha_paper_20261108.md),
[runner](../../../analysis/codex_fast_alpha_books_20261108.py), [report/reconciliation code](../../../analysis/codex_fast_alpha_books_20261108_report.py).
Inputs and exact Claude roster source are in[config](../inputs/fast_alpha_books_20261108/config.json).

## What was tested

Design2018-04-02–2022-12-30; own2017–22raw one-minute NQ/ES/CL only. Each result is one native micro:
MNQ$2/point, MES$5/point, MCL$100/point. Main commission$1.24RT plus one adverse native tick on market/stop
fills; stress$2.48/two ticks. MES/MCL commission is assumed. Targets need source-consistent trade-through.
No SPY fee/fractional-share or zero-slippage assumptions transferred to futures.

BASE preserves the original virtual parent's intended levels and state. ENTRY waits for the first complete
five-minute close-to-close return against the direction, then fills at the next executable minute open.
If the parent exits first, the entry is canceled; no hindsight-best fill or guaranteed price improvement.
BOTH adds favorable-countermove liquidation after a stop/discretionary exit request. Target/time/holiday exits
are preserved. Actual holdings can suppress subsequent parent entries. This is an explicitly specified
**fixed virtual-parent execution wrapper**, not a regenerated parent alpha with newly entry-anchored brackets.
Its source clocks/intent reconstruction and OHLC fills remain conditional until independent native review.

ENTRY−BASE isolates the entry policy; BOTH−ENTRY is the incremental exit policy conditional on those entries.
It is not a separate exit-only experiment. No15/30/60wait search, new streak, side filter or optimized stop.
All source tickets, missed orders and UNKNOWNs remain in the saved ledgers. Missing/changed-roll intervals
were not imputed. The old fast-alpha search and all parent selection histories remain in multiplicity.

## Fully resolved execution streams: every tested delay lost money

The following rows have no unresolved tickets across BASE/ENTRY/BOTH under this declared replay model.
Amounts are **total design-period net dollars per one micro**, not annual income, actual book sizing or payouts.

|Strategy|Tickets|Immediate BASE|Delayed entry|Entry + deferred exit|Combined change|
|---|---:|---:|---:|---:|---:|
'''
    for r in full.itertuples():text+=f'|{r.parent}|{r.tickets}|{money(r.base_total)}|{money(r.entry_total)}|{money(r.both_total)}|{money(r.both_effect)}|\n'
    text+='''
These are direct negative execution comparisons, not failures caused only by absent data. LDF's fixed
14:00flow and ES MOC's short window lose opportunities while waiting. The latter misses77of117tickets.
This timing explanation follows the frozen participant/time mechanism; it is not a new fitted time filter.
No claim of full native-platform or independent economic verification follows even for these clean paths.

## Every parent, including incomplete cases

This table uses the **same jointly resolved tickets** for all three profiles within each parent. It preserves
comparability but does not make the omitted observations ignorable. Qualified target fills/missing paths can
disproportionately remove winners. A negative conditional BASE does not establish that the adopted strategy lost
money. The full table must not be summed into a portfolio or scaled into payouts.

|Parent|Market|Resolved / source|Unknown|ENTRY change|BOTH change|Paired t ENTRY / BOTH|
|---|---|---:|---:|---:|---:|---:|
'''
    for r in tab.itertuples():
        values=['—','—'] if not r.resolved else [money(r.entry_effect),money(r.both_effect)]
        paired = f'{r.entry_t:.2f} / {r.both_t:.2f}' if r.resolved else '—'
        text+=f'|{r.parent}|{r.market}|{r.resolved}/{r.tickets}|{r.unknown}|{values[0]}|{values[1]}|{paired}|\n'
    text+='''
VB's positive entry effect has t≈1.08; Kusho t≈1.20; NBL's combined effect t≈1.68. None approaches the
prespecified multiple-testing threshold (conservative10,000prior-definition floor plus120reserved and58older
fast-alpha looks), and their full path gates fail. NBL/Kusho conditional BASE remains negative on this restricted
subset. S30 has only5NQ/2ESresolved tickets; no inference is warranted. CL has zero jointly resolved paths:
its zero sum in machine output means **no identified result**, not a flat/no-trade/profitable strategy.

The source-clock checks fixed two adapters without changing rules: every Kusho date/index pair identifies
December1,2017as its origin; PT next-bar market entries on five-minute reports map to the first constituent
minute OPEN, four minutes before the report stamp. Exact OPEN matching is required, not a favorable-price
search. The first attempt and diagnostics are retained; all22unaffected parent summaries reproduce exactly.
No additional economic variant or performance-based data relaxation was introduced.

## Stops, accounting and statistical limits

Deferring liquidation can extend loss beyond the original stop. Saved[deferred-exit risk](../../../analysis/outputs/codex_fast_alpha_books_20261108/deferred_exit_risk.csv)
reports paired observed adverse excursions and extra held minutes at one micro. These are conservative minute
measures, not verified tick chronology or account floor replay; no later rebound guarantees survival.
Market orders following pullbacks remain aggressive, and pending actual positions can suppress later intents.

The daily series is **closed-ticket, common-complete contribution**, not full MTM equity. Overnight marking,
unresolved trades, aggregate netting and current account quantities prevent using it as a funded/eval proxy.
Source-ticket quantities are normalized to one micro only for this cheap diagnostic. Actual book sizes,
inverse-vol weights and signal-time funded cushion sizing were not fabricated from these curves.

All gross−fee−slippage totals reconcile to net and daily contributions. Original standard_metrics.csv counts
resolved opportunities, including canceled orders;[actual-fill metrics](../../../analysis/outputs/codex_fast_alpha_books_20261108/actual_fill_metrics.csv)
separately reports actual trade count/win/average/t, whole/long/short and every design year. Total paired effects
retain zero missed-trade contributions; dropping profitable unfilled tickets is not called a higher average edge.
Sharpe/Sortino/PF/Calmar/Ulcer/DD are in the CSVs, with the same conditional, closed-ticket limitation.

Cheap gates required at least30complete tickets, no unresolved paths, positive total/stressed net and incremental
total, adjusted paired t, DSR>=.95and4/5positive years. **No candidate passed.** Significance is not inferred
from a favorable average or source paper, and the conservative selection floor is not a complete census of
unknown author trials. Conditional effect estimates and repeated/overlapping strategy streams are dependent.

## All five placement homes

|Home|Mapped streams|Passed|BASE/ADD/REPLACE/EMPTY outcome|
|---|---:|---:|---|
'''
    for r in outcomes:text+=f"|{r['home']}|{r['streams']}|0|Not earned; no demonstrated overlay allocation|\n"
    text+='''
The source personal roster has20named pieces but21instrument legs because S30 includes NQ and ES. The latest
150K evaluation/funded rosters add capped Twin separately from personal Twin. Shared parents were tested once,
then mapped to every book that uses them. The exact five-home coverage is in[book_placement.csv](../../../analysis/outputs/codex_fast_alpha_books_20261108/book_placement.csv).

None earned random-delay/drop controls,2023+historical validation, independent raw-spec review or native account
comparisons. Those stages were **not run**, rather than manufactured after a failed design. This is not a
measured claim that every possible portfolio-risk metric worsens or that the current plans are optimal.
Current source roster/cushion inconsistencies and earlier account-model defects also remain binding limits.

## Five paper questions and decision

1. **About:** fast SPY mean reversion as a timing overlay on slower ATR intraday breakouts.
2. **Findings:** authors report about200bp CAGR gain and Sharpe0.86(body)/0.87(abstract)to0.99; commissions included,
   zero slippage. Our24-stream futures design finds no passing overlay, with six fully resolved negative comparisons.
3. **Why money:** possible better execution of slow alpha without standalone fast turnover; missed exposure and
   deferred-stop risk can outweigh it. Neither the paper nor these conditional screens establishes live savings.
4. **Build on it:** the requested bounded execution question is tested; no profile earns deeper/account work.
   Retain the negative evidence, not a new waiting-window rescue or an unverified strategy queue candidate.
5. **Can strategy code be made:** yes, the committed Python execution wrapper exists. It is research code,
   not installed MultiCharts signals or broker-tested native execution. No passing rule is available to deploy.

**Recommendation: keep existing execution timing.** This project establishes no approved change in any book.
Independent economic/native verification remains pending. No root tier/trading plan, allocation, live strategy,
VPS, broker setting or API key changed. The autonomous scout/paused programs and their budgets were preserved.

For Claude: `agents/codex/results/fast_alpha_books_20261108.md`; verify the fixed-parent interpretation, source
clock amendments, native costs, path/target qualification and all negative/incomplete dispositions before any reuse.

To regenerate these tables from the saved ledgers, run
`/workspace/venvs/thebeginning/bin/python analysis/codex_fast_alpha_books_20261108_report.py`.
This reads no raw market data and creates no new economic definition. The original design commands and checked
commits are recorded in run.json and progress.json; a new design execution requires the frozen code/inputs,
a valid committed lease and checked remote head. The completed project's lease is released, so merely
rerunning its design command from the final commit is intentionally not permitted by the admission guard.
'''
    # Editorial spacing only; frozen execution code and saved economic outputs are unchanged.
    for before, after in {
        'Screened24frozen':'Screened 24 frozen', 'controls,2023+validation':'controls, 2023+ validation',
        'in[config]':'in [config]', 'Design2018':'Design 2018', 'own2017–22raw':'owned 2017–22 raw',
        'MNQ$2':'MNQ $2', 'MES$5':'MES $5', 'MCL$100':'MCL $100', 'commission$1.24RT':'commission $1.24 RT',
        'stress$2.48':'stress $2.48', 'No15/30/60wait':'No 15/30/60-minute wait',
        '14:00flow':'14:00 flow', 'misses77of117tickets':'misses 77 of 117 tickets',
        'conservative10,000prior-definition':'conservative 10,000 prior-definition',
        'plus120reserved and58older':'plus 120 reserved and 58 older',
        'only5NQ/2ESresolved':'only 5 NQ / 2 ES resolved', 'December1,2017as':'December 1, 2017 as',
        'all22unaffected':'all 22 unaffected', 'Saved[deferred-exit':'Saved [deferred-exit',
        'orders;[actual-fill':'orders; [actual-fill', 'least30complete':'least 30 complete',
        'DSR>=.95and4/5positive':'DSR >= .95 and 4/5 positive',
        'has20named pieces but21instrument':'has 20 named pieces but 21 instrument',
        'in[book_placement':'in [book_placement', 'controls,2023+historical':'controls, 2023+ historical',
        'about200bp':'about 200 bp', 'Sharpe0.86(body)/0.87(abstract)to0.99':'Sharpe 0.86 (body) / 0.87 (abstract) to 0.99',
        'Our24-stream':'Our 24-stream',
    }.items():
        text = text.replace(before, after)
    text = text.replace('measures, not verified tick chronology',
        'measures (for example, Kusho added up to $660.50 adverse exposure and 60 held minutes), not verified tick chronology')
    (ROOT/'agents/codex/results/fast_alpha_books_20261108.md').write_text(text)
    print(json.dumps(dict(parent_streams=len(tab),source_tickets=int(tab.tickets.sum()),resolved=int(tab.resolved.sum()),clean_streams=full.parent.tolist(),passed=0,controls_and_validation_and_accounts=False)))


if __name__=='__main__':main()
