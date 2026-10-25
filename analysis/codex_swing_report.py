"""Render and verify the frozen Swing Target evidence; no new strategy runs."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scratch_data/codex_deps'))
sys.path.insert(0,str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import codex_swing_target as H
import resampling as R

OUT=H.OUT
money=lambda x:f'-${-x:,.2f}' if x<0 else f'${x:,.2f}'
number=lambda x:f'{x:.2f}'
pct=lambda x:f'{x:.1%}'
integer=lambda x:str(int(x))

def table(frame,cols):
    rows=['| '+' | '.join(c[1] for c in cols)+' |','| '+' | '.join('---' for c in cols)+' |']
    for _,r in frame.iterrows():rows.append('| '+' | '.join(fmt(r[key]) for key,_,fmt in cols)+' |')
    return '\n'.join(rows)

def main():
    _,days,pc=H.setup()
    manifest=json.loads((OUT/'manifest.json').read_text())
    assert all(H.sha(ROOT/p)==v for p,v in manifest['hashes'].items())
    m=pd.read_csv(OUT/'metrics.csv');boot=pd.read_csv(OUT/'bootstrap.csv');sig=pd.read_csv(OUT/'significance.csv')
    placebo=pd.read_csv(OUT/'placebo_summary.csv');stress=pd.read_csv(OUT/'execution_stress.csv');risk=pd.read_csv(OUT/'native_daily_mc.csv')
    gates=json.loads((OUT/'cheap_gate.json').read_text())
    assert all(g['cheap_pass'] and not g['apex_source_eligible'] for g in gates['models'])
    assert (placebo.status=='complete').all() and (placebo.runs==500).all()
    assert len(placebo)==12
    author=[];timing=[];personal=[];joint=[];fee_sensitivity=[]
    (OUT/'personal/.gitignore').write_text('*.npy\n*.npz\n',encoding='utf-8')
    for model in ['CODE','CODE_BE']:
        t=pd.read_csv(OUT/(model+'_trades.csv'),parse_dates=['date','exit_date'])
        a=t[t.date.between('2018-02-01','2026-07-31')]
        native=a.native_net_per_mnq
        months=a.groupby(a.exit_date.dt.to_period('M')).native_net_per_mnq.sum().reindex(pd.period_range('2018-02','2026-07',freq='M'),fill_value=0.)
        author.append(dict(model=model,trades=len(a),win=float((native>0).mean()),
            avg_win=float(native[native>0].mean()),avg_loss=float(-native[native<0].mean()),
            profit_factor=float(native[native>0].sum()/-native[native<0].sum()),
            max_dd=R.max_dd(H.daily(a,days[(days>='2018-02-01')&(days<='2026-07-31')],col='native_net_per_mnq')),
            max_mae=float(a.mae.max()/10),target=int(a.reason.eq('target').sum()),time=int(a.reason.eq('time').sum()),
            stop=int(a.reason.eq('stop').sum()),breakeven=int(a.reason.eq('breakeven').sum()),
            average_mae=float(a.mae.mean()/10),worst_month=float(months.min()),positive_month_share=float(months.gt(0).mean()),
            median_hold_minutes=float(np.median((a.exit_day-a.day)*1440+a.j1-a.j0)),
            author_cost_total=float(a.author_cost_per_mnq.sum())))
        x=t[t.apex_flat_violation]
        for _,r in x.iterrows():timing.append(dict(model=model,entry_date=str(r.date.date()),entry_label=f'{int(r.j0)//60:02d}:{int(r.j0)%60:02d}',
            exit_date=str(r.exit_date.date()),exit_label=f'{int(r.j1)//60:02d}:{int(r.j1)%60:02d}',reason=r.reason))
        totals=m.query("model==@model and period=='all' and side=='all'").iloc[0]
        assert len(t)==totals.trades and np.isclose(t.net.sum(),totals.total)
        assert np.isclose(H.daily(t,days).sum(),t.net.sum())
        for fee in ['1.24','1.04']:
            p=OUT/'personal'/model/('fee_'+fee)
            effect=pd.read_csv(p/'paired_effects.csv')
            selected=effect[(effect.cohort=='2023_plus')&effect.config.str.endswith('__ADD')&effect.reference.str.endswith('__BASE')].copy()
            selected['model']=model
            selected['fee']=float(fee)
            if fee=='1.24':
                personal.extend(selected.to_dict('records'))
                j=pd.read_csv(p/'joint_losses.csv');j['model']=model;joint.extend(j.to_dict('records'))
            else:fee_sensitivity.extend(selected[selected.config=='FULL__ADD'].to_dict('records'))
    author=pd.DataFrame(author);personal=pd.DataFrame(personal);joint=pd.DataFrame(joint)
    author.to_csv(OUT/'author_window_comparison.csv',index=False)
    personal.to_csv(OUT/'personal_addition_compact.csv',index=False)
    baseline_checks=json.loads((OUT/'personal_baseline_crosscheck.json').read_text()) if (OUT/'personal_baseline_crosscheck.json').exists() else {}
    for model in ['CODE','CODE_BE']:
        b=boot[(boot.model==model)&(boot.period=='2023+')&(boot.side=='all')&(boot.metric=='max_dd')].iloc[0]
        r=m[(m.model==model)&(m.period=='2023+')&(m.side=='all')].iloc[0]
        assert np.isclose(b.actual,r.max_dd)
    review=json.loads((OUT/'independent_engine_review.json').read_text())
    checks=json.loads((OUT/'diagnostic_checks.json').read_text())
    checks.update(diagnostic_script_sha256=H.sha(ROOT/'analysis/codex_swing_diagnostics.py'),
        initial_zero_bootstrap_wrapper='analysis/codex_swing_bootstrap.py',
        null_requested_and_closed_per_family_per_model=500*int(m.query("model=='CODE' and period=='all' and side=='all'").iloc[0].trades),
        random_time_null_conditions_on_later_revealed_side=True)
    H.dump('diagnostic_checks.json',checks)
    H.dump('report_checks.json',dict(primary_input_hashes_match=True,all_trade_price_cost_daily_totals_reconcile=True,
        all_500_null_runs_closed=True,initial_zero_bootstrap_matches_point_dd=True,
        requested_contexts=['50K evaluation','150K evaluation','50K funded','150K funded','personal A-D','personal FULL18'],
        no_trade_deletions=True,personal_fee_sensitivity=fee_sensitivity,report_script_sha256=H.sha(Path(__file__)),
        latest_tier_source='62e82a0:TIER_LIST.md',latest_tier_sha256=H.sha(ROOT/'agents/codex/inputs/swing_target/tier_list_latest.md')))
    mainrows=m[m.period.isin(['2018-22','2023+','all'])]
    combined=mainrows[mainrows.side=='all']
    yearly=m[(m.side=='all')&m.period.str.fullmatch(r'20\d\d')]
    ci=boot[(boot.side=='all')&(boot.period=='2023+')&boot.metric.isin(['sharpe','sortino','pf_day','max_dd'])].copy()
    ci['interval']=ci.apply(lambda r:f'{r.p5:,.2f} to {r.p95:,.2f}',axis=1)
    full=m[(m.period=='all')&(m.side=='all')].copy()
    full['native_annual']=full.annual*full.native_net_per_mnq/full.total
    whole_sig=sig[(sig.period=='all')&(sig.side=='all')]
    code_sig=whole_sig[whole_sig.model=='CODE'].iloc[0]
    be_sig=whole_sig[whole_sig.model=='CODE_BE'].iloc[0]
    selectedstress=stress[(stress.period=='2023+')&stress.scenario.isin(['opposite_minute_path','extra_tick'])]
    fulljoint=joint[joint.group=='FULL']
    personal['historical_ci']=personal.apply(lambda r:f'[{money(r.historical_annual_mean_lo)}, {money(r.historical_annual_mean_hi)}]',axis=1)
    losses=table(fulljoint,[('model','Model',str),('correlation','Full-book daily corr',number),('joint_loss_days','Joint losing days',integer),('candidate_net_on_baseline_loss_days','Candidate net on full-book loss days',money)])
    corecols=[('model','Model',str),('period','Period',str),('side','Side',str),('trades','Trades',integer),('win','Win',pct),
       ('avg','Net/trade NQ',money),('t','t',number),('sharpe','Sharpe',number),('sortino','Sortino',number),('profit_factor','PF',number),
       ('calmar','Calmar',number),('ulcer','Ulcer',number),('max_dd','EOD DD/NQ',money)]
    text=f'''# Swing Target NQ: WATCH for personal research; REJECT as supplied for Apex

Summary: Broad economics reproduce:602 trades, PF1.62 CODE /1.70 CODE_BE; both eras and all9 years positive after repo costs.
The author's matching window gives591 trades rather than584; exact MultiCharts parity is unverified.
At1MNQ,2023+ personal-full addition adds mean annual $2,484/$2,743, with DD95 increases $461/$170; replacement evidence is inconclusive.
Both source versions carry3 holiday trades across dates, so neither belongs on50K/150K evaluation/funded as supplied.
It diversifies the existing book but loses on book-loss days. No new filter, ranking, live change or deployment follows.

Plan: [`swing_target.md`](../plans/swing_target.md), **{pc[:7]}**, committed before real returns. Two fixed economic models; no optimization.
Source: `agents/codex/inputs/swing_target/Swing_Target_NQ.txt`, preserved byte-for-byte. User authorized both BE/no-BE and unknown-template full-session proxy.
Scripts: `analysis/codex_swing_target.py`, `codex_swing_engine.py`, `codex_swing_diagnostics.py`, `codex_swing_accounts.py`, `codex_swing_report.py`.
Outputs: `analysis/outputs/codex_swing_target/`. Current plan source pinned at **62e82a0**; existing caches reused without rebuilding.

## Rule, source/prose differences and execution

CODE follows the uploaded defaults: previous2 stored RTH highs/lows; prior20 stored-session average range; .35 target/.70 stop;
inside opening boundaries, disarm on strict break through08:45; one trade/day. CODE_BE adds only causal entry-price BE after+.30 range.
The file has **no BE rule**; CODE_BE isolates that missing rule and leaves the other source/prose discrepancies visible.
1-minute CT close stamps:08:45 decision=>08:46-labeled entry bar; inclusive14:29 decision permits14:30 entry;
14:59 exit decision fills next bar open, normally the15:00-labeled bar (14:59 wall time), not the cash-close price.
No source rewrite, holiday repair, side-specific setting or fitted regime filter was added.

Use the nearer-extreme OHLC path, worse-open stop gaps and one-point target-through, with entry-bar protection and post-entry-only MAE.
Both resting entries cancel after first fill. A fixed opposite-path stress checks intrabar ambiguity. Price distances are unrounded,
as in the repo engine; tick rounding, true tick paths, limit queues, the author's session template and MNQ prices remain unverified.
The new engine extends the shared market-entry simulator for paired stop entries and causal BE. Independent source/engine review and
synthetic long/short, BE, gap, timing and missing-close checks pass; this is not an independent full-data replica or MC parity pass.
Review: [`swing_target_engine_review.md`](swing_target_engine_review.md).

History: cached2017-12-01–2026-10-09; source history initializes before2018. Run2018–22 before2023+ for both fixed versions.
2023+ was already examined by the author, whose header says many start times were inspected in both eras; prior trial count is unknown.
This is historical replication, not fresh holdout. The declared15-minute rule is not preregistered economic discovery.

## Standalone results

NQ tables pay$7.25 RT plus1 tick at stop entry and stop/BE/time exit; target exits no extra slip.
Native MNQ uses$1.24 RT plus$.50 per market/stop fill, with$1.04 sensitivity. Never divide NQ commission by10.
All/long/short tables include verified strategy-no-trade days, realized P&L on actual exit dates and initial zero for DD.
Ulcer uses the repo's$50,000 reference. Every side/year and trade/EOD DD remain in `metrics.csv`.

{table(mainrows,corecols)}

{table(yearly,[('model','Model',str),('period','Year',str),('trades','Trades',integer),('win','Win',pct),('native_net_per_mnq','Net/1MNQ',money),('profit_factor','PF/NQ costs',number)])}

2026 is throughOctober9. At native costs, the full-history one-micro risk/return scale is:

{table(full,[('model','Model',str),('native_annual','Annualized net/1MNQ',money),('native_max_trade_dd','Closed-trade DD/1MNQ',money),('max_mae_per_mnq','Worst open MAE/1MNQ',money)])}

Wide nominal stops do not equal the average realized loss: most trades exit by target/time, and the added BE trims some tails.
This explains why Swing's realized win/loss mix can differ from Vault Break's fixed40/75 payoff. It does not ensure smooth future equity.

## Author's February2018–July2026 claims

The user's claim is584 trades,62% wins, PF1.79,$129 average win/$117 average loss,$1,442 DD,$660 worst MAE;
exits262 target/245 EOD/46 stop/31 BE. On that same calendar slice:

{table(author,[('model','Model',str),('trades','Trades',integer),('win','Native win',pct),('profit_factor','Native PF',number),('avg_win','Avg win/1MNQ',money),('avg_loss','Avg loss/1MNQ',money),('max_dd','DD/1MNQ',money),('target','Targets',integer),('time','Time',integer),('stop','Stops',integer),('breakeven','BE',integer)])}

Our BE version reproduces the262 target count and broadly similar payoff/DD shape, but seven extra trades and differing exits remain.
At native fees, its worst month is{money(author[author.model=='CODE_BE'].iloc[0].worst_month)},
{author[author.model=='CODE_BE'].iloc[0].positive_month_share:.1%} of months are positive, average open MAE is
{money(author[author.model=='CODE_BE'].iloc[0].average_mae)}/MNQ and median hold{author[author.model=='CODE_BE'].iloc[0].median_hold_minutes:.0f} minutes.
No author MC export was supplied, so the claimed571/584 matching days cannot be checked; no fake trade match or exact reproduction claim.
Author$1 zero-slippage cost totals and our native costs are kept separate in `author_window_comparison.csv` and the ledgers.

## Uncertainty, nulls and execution stress

2023+5,000-run10-session block-bootstrap90% intervals (PF here is daily PF):

{table(ci,[('model','Model',str),('metric','Metric',str),('actual','Actual',number),('interval','90% interval',str)])}

The initial-zero wrapper reuses repo block paths/statistics and prepends the bookkeeping zero to every path; it does not resample it as a market day.
Permutation and10,000-trade-bootstrap outputs are saved, plus full/validation and all/long/short statistics.
The latest pinned ranked-item count is{int(code_sig.ranked_item_plus_two)-2}; plus2 gives{int(code_sig.ranked_item_plus_two)},
t bar{code_sig.t_threshold:.2f}. CODE full t{code_sig.t:.2f}/DSR{code_sig.dsr:.3f}; CODE_BE t{be_sig.t:.2f}/DSR{be_sig.dsr:.3f}.
The local older tier list had274 items; significance was refreshed from the pinned62e82a0 list before publication, without changing returns or selecting parameters.
This ranked-item count is a lower bound on all historical searches; previous VB bracket trials and unknown author filters/timing searches remain disclosed.
No side is promoted or dropped from its isolated result; short-side strength does not authorize a newly selected short-only strategy.

{table(placebo[placebo.side=='all'],[('model','Model',str),('family','Null',str),('actual_avg','Actual net/trade NQ',money),('null_avg','Null mean',money),('tail_at_least_actual','Null >=actual',pct)])}

All500 runs/family/model closed, with exact signal-count checks. Random direction at the selected time is weaker (p≈.002).
The random-time benchmark retains the **later revealed breakout direction and selected trade day**; entries before that information was
known use hindsight. It beats the actual entry but is not an executable alternative or a causal test of entry timing.
We therefore do not claim a clean entry-time placebo pass, or that the15-minute filter adds edge. No after-the-fact replacement null was searched.

{table(selectedstress,[('model','Model',str),('scenario','Fixed execution stress',str),('total','2023+ net/NQ',money),('profit_factor','PF',number)])}

Opposite-path and extra-tick results remain profitable; these are execution scenarios, not extra economic models or selected parameters.
Standalone252-session EOD-trail illustrations at1MNQ have2023+ hit frequencies10.8% CODE /5.3% CODE_BE and DD95$2,527/$2,133.
They omit intraday account breaches/portfolio rules and do not override the actual Apex source incompatibility.

## Account placement and session failure

{table(pd.DataFrame(timing),[('model','Model',str),('entry_date','Entry date',str),('entry_label','Entry label',str),('exit_date','Exit date',str),('exit_label','Exit label',str),('reason','Exit',str)])}

Exact15:00 range storage/termination and14:59 exit submission miss holiday/shortened sessions. All1,201 unobserved held minutes
occur on these three spans; they overlap scheduled closures and must not be called1,201 lost-feed minutes. No ordinary intraday trade
has an unobserved held minute. We retain these trades; deleting them or repairing them after results would change the strategy.

| Requested plan | As-supplied conclusion, both models |
| --- | --- |
| 50K evaluation | REJECT as supplied:3 source flat/session violations; no invalid account backtest |
| 150K evaluation | Same concrete source violation; cannot infer legality/survivability from larger drawdown limit |
| 50K funded | REJECT as supplied; no payout recommendation |
| 150K funded | REJECT as supplied; no payout recommendation |
| Personal A–D / full18 | Positive historical addition, higher drawdown; WATCH pending parity, independent replication and forward evidence |

All eight model/Apex-context limits are saved in `apex_operational_limits.json`. No hypothetical holiday-safe strategy was fitted.

## Current personal portfolio: addition, VB replacement and empty slot

Current18 legs/starter ladders are pinned to62e82a0, including OT and newer Kusho/S47/S30/BB_MRM. The baseline separately reproduces
the published1.275-fee annual$38,004 and$5,803 DD before the frozen native-fee repricing. Candidate is1MNQ at the book's common leg scale.
Retain all trades, including observed16:00 marks across carries; no equity is backdated to entry day. Use1,000 paired252-session paths,
10-day blocks. Below is **2023+ source pool**, mean annual addition and **95% historical annual-mean interval** (different from90% above):

{table(personal,[('model','Model',str),('config','Ladder/full addition',str),('mean_profit_delta','Mean annual increment',money),('historical_ci','95% historical mean CI',str),('dd95_delta','Change in DD95',money)])}

For FULL, VB replacement adds only about$267/$525 mean annual and its historical intervals cross zero. The empty-VB control is included;
there is no reliable evidence to replace VB. Exact BASE/ADD/EMPTY/REPLACE tables and full/year statistics are saved per model/fee.
Starter-ladder drawdown increases are materially larger than FULL, so a FULL benefit is not a blanket small-account recommendation.

{losses}

Correlation≈.20 does not make it a hedge. It adds NQ breakout exposure and is negative in aggregate when the current book loses.
Author correlations with Twin/ORB/RelStr/Kusho/KOS10/VWAP/Midday are not all reproducible from the supplied material; our table is our current book.
For a hedge, require positive conditional P&L and timely offsets on book-failure paths, not just low unconditional correlation.
Research directions are a genuinely different risk driver (non-equity scheduled flow) or a separately preregistered failed-breakout reversal;
neither is an established edge here. Avoid adding another overlapping breakout merely because its average correlation is low.

Personal caveats: published fee/day approximations undercount some reentries; MOC/S30 booking approximations and the existing Twin v1-marked
ledger remain. Current OT source endsJuly7,2026; post-source zero columns are missing baseline evidence, not verified no-trade activity.
Thus portfolio conclusions are conditional historical comparisons, not complete current execution/margin/liquidation evidence.
The inherited funded OT whole-night adverse approximation is documented but no Apex performance conclusion was taken from it.

## Decision and next evidence

The strategy merits further personal research; its broad edge is not explained by a high win rate alone. No regime filter or alternative
price stop was optimized. The Howard [primary abstract](https://ssrn.com/abstract=6350238) concerns ES volume-profile breakout events,
January2025–January2026 and a first30-minute effect; it does not validate this NQ prior2day level or15-minute cutoff, nor establish0DTE causation.
Full paper returned403, with no bypass. Wide/open risk can be reduced in dollars by size and portfolio risk budgets, but any exit/filter
change needs a frozen test of return lost versus risk saved. The described BE is already compared here; it improves the later risk shape
without proving optimality. Exact platform parity and a known session/holiday definition are the cheapest next evidence.

The user-requested Vault Break rerun is now an unchecked item in `TODO.md`. No live chart, VPS, broker/API setting, shared cache,
ranking or allocation was changed. Data, code, trial logs and source hashes are saved for Claude's independent review.

Reproduce from repo root using the installed scientific interpreter recorded in the manifest:

```powershell
$swingPython = '{sys.executable}'
& $swingPython -B analysis/codex_swing_target.py --phase design
& $swingPython -B analysis/codex_swing_target.py --phase validation
& $swingPython -B analysis/codex_swing_diagnostics.py
foreach ($swingModel in 'CODE','CODE_BE') {{
  foreach ($swingFee in '1.24','1.04') {{
    & $swingPython -B analysis/codex_swing_accounts.py --personal --ledger "analysis/outputs/codex_swing_target/${{swingModel}}_trades.csv" --prereg a4064ac --fee $swingFee
  }}
}}
& $swingPython -B analysis/codex_swing_report.py
```

Claude review path: `agents/codex/results/swing_target.md`.
'''
    (ROOT/'agents/codex/results/swing_target.md').write_text(text,encoding='utf-8')
    print('Report saved; source totals, uncertainty DD and all requested placement contexts checked.')

if __name__=='__main__':main()
