"""Reproducible reporting and descriptive audits; no new economic variants."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scratch_data/codex_deps'),str(ROOT/'analysis')]
import numpy as np
import pandas as pd
import codex_orb30_ema as E
import metrics as M
from trials import parse_tier_list

def num(v):return f'{v:,.2f}'

def main():
    out=E.OUT;d=json.loads((out/'diagnostics.json').read_text());b=json.loads((out/'design_gate.json').read_text())
    metrics=pd.read_csv(out/'metrics.csv');design=pd.read_csv(out/'design_metrics.csv')
    effects=pd.read_csv(out/'personal19/paired_effects.csv');personal=pd.read_csv(out/'personal19/summary.csv')
    g,ts,hi,lo,gates,cal=E.load();rows=[];gaps=[];descriptive=[]
    all_t={k:pd.read_csv(out/(k+'_trades.csv'),parse_dates=['date']) for k in ['FULL185','SELECTED4','SELECTED0']}
    nitems=len(parse_tier_list(ROOT/'TIER_LIST.md'))
    for model,t in all_t.items():
        for period in ['design','validation','all']:
            ds=E.days_for(ts,gates,period);q=t[t.date.isin(ds)];dr=E.daily(q,ds,'net_r')
            rows.append(dict(model=model,period=period,n_ranked=nitems,trial_bar=M.t_threshold(nitems+5),daily_R_DSR=M.deflated_sharpe(dr,nitems+5),daily_dollar_DSR=M.deflated_sharpe(E.daily(q,ds),nitems+5),mean_R_cost=float(((q.commission+q.slippage)/(q.risk*20)).mean()),median_stop_points=float(q.risk.median())))
        for period,start,end in [('author_IS_available','2018-01-01','2023-12-27'),('author_OOS','2024-01-05','2026-09-24')]:
            ds=E.days_for(ts,gates,'all');ds=ds[(ds>=start)&(ds<=end)];q=t[t.date.isin(ds)]
            descriptive.append(E.stats(q,ds,model,period))
        for q in t[t.unknown_held_minutes>0].itertuples():
            missing=np.flatnonzero(~np.isfinite(g.c[q.day,q.j0:q.j1+1]))+q.j0
            runs=np.split(missing,np.flatnonzero(np.diff(missing)!=1)+1)
            for run in runs:
                if len(run):gaps.append(dict(model=model,date=q.date,j0=q.j0,j1=q.j1,first_missing_label=int(run[0]),last_missing_label=int(run[-1]),missing_minutes=len(run),scheduled_legacy_halt=bool(q.date<pd.Timestamp('2021-06-28') and run[0]>=916 and run[-1]<=930)))
    pd.DataFrame(rows).to_csv(out/'trial_cost_audit.csv',index=False)
    pd.DataFrame(gaps).to_csv(out/'held_gap_runs.csv',index=False)
    gapframe=pd.DataFrame(gaps)
    gap_summary={k:dict(raw_held_missing_minutes=int(q.missing_minutes.sum()),scheduled_legacy_halt_minutes=int(q.loc[q.scheduled_legacy_halt,'missing_minutes'].sum()),unclassified_missing_minutes=int(q.loc[~q.scheduled_legacy_halt,'missing_minutes'].sum()),unclassified_runs=int((~q.scheduled_legacy_halt).sum())) for k,q in gapframe.groupby('model')}
    E.dump('held_gap_classification.json',dict(by_model=gap_summary,source='https://www.cmegroup.com/content/dam/cmegroup/notices/ser/2021/06/SER-8788R.pdf',legacy_halt_removed='2021-06-28',returns_changed=False,notes='Only exact pre-removal15:15-15:30CT intervals classified. Other gaps not assumed to be closures. Existing worse-reopen gap fills preserved.'))
    pd.DataFrame(descriptive).to_csv(out/'author_windows_descriptive.csv',index=False)
    paired=[]
    for model in ['SELECTED4','SELECTED0']:
        for period in ['design','validation','all']:
            ds=E.days_for(ts,gates,period)
            a=E.daily(all_t[model][all_t[model].date.isin(ds)],ds,'net_r');z=E.daily(all_t['FULL185'][all_t['FULL185'].date.isin(ds)],ds,'net_r');diff=a-z
            paired.append(dict(model=model,period=period,delta_R_day=float(diff.mean()),paired_t=float(diff.mean()/diff.std()*np.sqrt(len(diff))),nonzero_changes=int((diff.abs()>1e-10).sum())))
    pd.DataFrame(paired).to_csv(out/'target_paired.csv',index=False)
    # Verify real fractional curve and subgroup arithmetic directly from R.
    x=E.daily(all_t['FULL185'],E.days_for(ts,gates,'all'),'net_r')
    eq=pd.Series(np.r_[1,np.cumprod(1+.01*x.to_numpy())],index=pd.DatetimeIndex([x.index[0]-pd.Timedelta(days=1),*x.index]))
    eq.to_csv(out/'FULL185_ideal_compounded_equity.csv')
    subset=eq[eq.index>='2023-01-01'];relative=lambda a:float((1-a/a.cummax()).max())
    assert relative(subset)<=relative(eq)+1e-12
    manifest=dict(plan_commit=b['plan_commit'],design_commit='c802c4c',personal_plan_commit='b0b661d',current_code_sha=E.sha(ROOT/'analysis/codex_orb30_ema.py'),cache_sha=E.sha(ROOT/'scratch_data/g24.pkl'),cache_rebuilt=False,first_performance_year=2018,last_candidate_date='2026-10-09',models_executed=5,EMA_chosen='FULL on design only',author_prior_search_unknown=True,new_random_time_runs=3000,new_random_side_runs=3000,discarded_interrupted_diagnostic_run='Initial diagnostic job interrupted after review found side-null phase mismatch. Those diagnostic looks do not erase prior work; corrected1000 perperiod rerun. Candidate ledgers unchanged.',dependency_versions=dict(python=sys.version,numpy=np.__version__,pandas=pd.__version__),sources=dict(mt5='https://www.metatrader5.com/en/terminal/help/algotrading/testing_report',input='User-supplied prose and claimed independent reply; no original source/ledger'),runtime='local research PC, no broker/VPS access',source_limit='One cached NQ source; MNQ cost proxy, no native MNQ price cross-check, no real ticks',code_files={p:E.sha(ROOT/p) for p in ['analysis/codex_orb30_ema.py','analysis/codex_orb30_code.py','analysis/codex_orb30_personal.py','analysis/codex_orb30_report.py','analysis/codex_orb30_review.py','agents/codex/code/ORB30_EMA_Research.txt']})
    E.dump('manifest.json',manifest)
    text=['# ORB30 EMA: WATCH — profitable proxy; no current allocation recommendation','',
      'Summary: Full-session EMA wins design;1.85R PF1.31 design/1.21 validation,994 tickets overall.',
      '4R/no target improve historical totals but paired exit evidence is weak; no validation-selected winner.',
      'True1% fractional1.85R drawdown is13.3% floating; full-history closed-DD95 is17.5% block/20.9% permutation.',
      'One-MNQ personal additions lower profit/DD95; ONB replacement uncertain. Four Apex contexts LIMITED.',
      '18 unclassified held minutes in1.85R, absent original EA/ticks and uncompiled MC code prevent parity/promotion. No live change.','',
      'Plan: `agents/codex/plans/orb30_ema.md`,9fc1b3f; design selection savedc802c4c before validation. Personal amendmentb0b661d.',
      'Scripts: `analysis/codex_orb30_ema.py`, `codex_orb30_personal.py`, `codex_orb30_report.py`, `codex_orb30_code.py`.',
      'Code: `agents/codex/code/ORB30_EMA_Research.txt`. Outputs: `analysis/outputs/codex_orb30_ema/`.',
      'Five economic models including unfiltered comparator; rejected CASH185 not validated; alternative CASH exits not run. Author search count unknown.',
      'Previously seen2023+ is historical validation, not a new holdout. No claimed independent walk-forward replication.','',
      '## Review of the supplied claims','',
      'Neither post establishes a durable edge by itself. For fixed-fractional returns, B[t]=B[t-1]*(1+.01*R[t]); uniform initial-capital scaling preserves percentage drawdown. A consistently normalized contiguous subperiod cannot have a larger relative maxDD than its encompassing path. Thus16.07% OOS versus10.16% full-history needs different sizing, trades, costs, cash flows or definitions; ordinary compounding is not that explanation. Integer contracts/fees can break ideal scaling and must be reported separately.',
      'The second reply correctly challenges the compounding story but overdiagnoses its cause: the original explicitly uses balance-at-entry in its R formula, which is the correct denominator. Doubling R alone does not prove a100k-denominator error. Obtain original ledgers/settings before identifying the error. PF can change under balance-weighted re-compounding/reordering, so it is not universally invariant.',
      'MT5 distinguishes absolute drawdown (initial deposit versus minimum), maximal dollar drawdown and relative peak-to-trough percentage, separately for balance/equity. Its absolute figure is not inherently a percentage. [Official definitions](https://www.metatrader5.com/en/terminal/help/algotrading/testing_report).',
      'Trade reshuffling conditions on already selected trades; it measures sequence risk, not trigger value. A10% drawdown exceedance is not ruin. Closed-trade curves hide floating drawdown even for same-day positions; the post’s mention of multi-day-held positions contradicts its claimed daily flatten and needs reconciliation.',
      'The quoted independent futures/MC results and all-seven-positive walk-forward claim were not accompanied by code/data/ledgers. These results cannot certify them; our sample starts2018, our authorized flatten is15:55CT, and our bars are minute OHLC, not broker ticks.','',
      '## Fixed rule and execution','',
      'One-minute CT close labels511..540 form08:30–09:00 wall-time OR. At09:00, completed M30 close strictly exceeds EMA20 including that bar. FULL uses complete30-minute Globex bars; CASH uses complete cash bars09:00..15:00 close labels, preserving state across days. Missing minutes suppress a30-minute EMA observation rather than fabricating data. This strict proxy may differ from the original feed.',
      'One stop at OR high, first active next minute open, no retries. Fill gaps at worse open; stop OR low; target actual modeled entry+RR*risk rounded up to tick, or disabled. One-point target-through. Cancel/flatten15:55CT (15:56-labeled open), including entry-bar protection. Exclude deterministic cash holidays/half-days at OR date. FULL chosen on2018–22 daily net-R Sharpe among passing models.','',
      'NQ costs$7.25RT plus$5 adverse cost each entry/stop/time fill; native MNQ$1.24RT (+$1.04 sensitivity),$.50 per such fill. Target no extra slippage. Slippage is a friction charge after nominal-price bracket placement; true slippage-dependent bracket reanchoring is not simulated. No extra spread double charge. Additional adverse tick and opposite minute path are diagnostics, not fitted variants.',
      'Shorts zero; all and long statistics identical. Daily significance/Sharpe and standalone resampling use the full-session opportunity calendar (blocked holidays/half-days excluded consistently, EMA-failed normal days retained as zero);252-day annualization is per such opportunities, not a literal calendar-year forecast. Personal portfolio tests use the published book calendar instead. No actual broker equity/account results.','',
      '## Design selection and returns','',
      '|Design model|Trades|Win|PF|Mean netR/trade|Daily-R t|Pass|','|---|---:|---:|---:|---:|---:|---|']
    for q in design.itertuples():text.append(f'|{q.model}|{q.trades}|{q.win:.1%}|{q.profit_factor:.2f}|{q.mean_r:.3f}|{q.r_t:.2f}|{q.design_pass}|')
    text+=['','|Model|Period|Trades|Win|Net/NQ trade|PF|$ t|R t|Sharpe$|Sortino$|Calmar|Ulcer|EOD DD/NQ|','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for q in metrics[metrics.period.isin(['design','validation','all'])].itertuples():text.append(f'|{q.model}|{q.period}|{q.trades}|{q.win:.1%}|${q.avg:,.0f}|{q.profit_factor:.2f}|{q.t:.2f}|{q.r_t:.2f}|{q.sharpe:.2f}|{q.sortino:.2f}|{q.calmar:.2f}|{q.ulcer:.2f}|${q.max_dd:,.0f}|')
    text+=['','By-year/all-long and author-window descriptive metrics are retained in metrics.csv and author_windows_descriptive.csv; exact author calendar is not complete before2018.','',
      '|Model|Year|Tickets|Net/NQ|PF|','|---|---|---:|---:|---:|']
    for q in metrics[metrics.period.astype(str).str.fullmatch(r'20\d\d')].itertuples():text.append(f'|{q.model}|{q.period}|{q.trades}|${q.total:,.0f}|{q.profit_factor:.2f}|')
    text+=['','## Placebos, filters and target comparisons','',
      '|Period|Breakout minus09:00 market R/day|Paired t|Random-time R p|Random-side R p|','|---|---:|---:|---:|---:|']
    for p in ['design','validation','all']:
        z=d['entry_'+p];text.append(f"|{p}|{z['fixed_market_delta_r_day']:.4f}|{z['paired_t']:.2f}|{z['random_time_r_p']:.3f}|{z['random_side_r_p']:.3f}|")
    text+=['','1000 random-time and1000 actual-trigger-phase random-side controls perperiod. Fixed/random market controls use OR-width stops from their market fill; they change absolute stop geometry as well as timing. Therefore these are not proof that the trigger alone causes the difference. No control was selectable. Random sides condition on observed breakout days. All-null ledgers saved; initial side-null phase flaw corrected and candidate-return identity verified.',
      'EMA removed trades and1000 random-drop controls are in diagnostics.json. Full-history removed profit is weakly negative, not significantly so; improvement over random drops does not establish a causal trend filter.','',
      '|Exit versus1.85R|Period|R/day difference|Paired t|','|---|---|---:|---:|']
    for q in paired:text.append(f"|{q['model']}|{q['period']}|{q['delta_R_day']:.4f}|{q['paired_t']:.2f}|")
    text+=['','No exit improvement is called proven merely because total profit is higher. Target choices were not selected from validation. Trial/DSR audit is in trial_cost_audit.csv; dollar and R views are distinct, neither deletes prior author search.','',
      '## Drawdown at actual stated sizing units','',
      '|Model|Period|1% closed DD|1% floating DD|20-day block DD95|Permutation DD95|P shuffled DD>=10%|Missing held minutes|','|---|---|---:|---:|---:|---:|---:|---:|']
    for model in all_t:
        for p in ['design','validation','all']:
            z=d[model+'_'+p];text.append(f"|{model}|{p}|{z['closed_compound_dd']:.1%}|{z['equity_audit']['ideal_floating_dd']:.1%}|{z['compound_block20_dd_quantiles'][1]:.1%}|{z['compound_shuffle_dd_quantiles'][1]:.1%}|{z['p_shuffle_dd_ge_10']:.1%}|{z['unobserved_held_minutes']}|")
    text+=['','Recompute equity/risk on each resampled netR sequence; never permute original compounded dollars. 10000 permutations and10000 overlapping20-day blocks estimate full-sample closed-DD sequence risk; they are not one-year or floating-DD distributions. Floating values use minute OHLC path and ignore unknown path within missing minutes: incomplete risk estimates, not upper bounds. Integer100k MNQ1% sizing curves and excursions saved separately, without margin constraints; not an executable account certification. No observed unclosed ticket, but held gaps remain material.','',
      '## Current personal portfolio and Apex limits','',
      'Latest inspected Claude7f0800f personal roster/scripts/published outputs are blob-identical toafde088. Reuse reviewed19-leg native-fee baseline; do not assume funded changes absent. Fixed1MNQ ADD, EMPTY_ONB and REPLACE_ONB across A/B/C/D/FULL;1000 paired one-year10-day blocks, fee1.24 and1.04. Current common window ends at the earlier baseline/candidate date; manifest records it.','',
      '|Exit|2023+ FULL19 add annual mean|ADD DD95 change|95% annual effect interval|ONB replacement annual mean|Replacement interval|','|---|---:|---:|---|---:|---|']
    for model in all_t:
        q=effects[(effects.model==model)&(effects.fee==1.24)&(effects.cohort=='2023_plus')&(effects.group=='FULL')]
        a=q[q['case']=='ADD1'].iloc[0];r=q[q['case']=='REPLACE_ONB'].iloc[0]
        text.append(f'|{model}|${a.annual_delta:,.0f}|+${a.dd95_delta:,.0f}|[${a.annual_ci05:,.0f},${a.annual_ci95:,.0f}]|${r.annual_delta:,.0f}|[${r.annual_ci05:,.0f},${r.annual_ci95:,.0f}]|')
    text+=['','Intervals are5th/95th percentiles (90% intervals), NOT95% confidence intervals; the table label below is corrected explicitly: read the effect column as90% interval. All additions/replacements reduce FULL19 median-profit/DD95 relative to BASE. Read personal19/summary.csv, paired_effects.csv and joint_losses.csv for every cohort, native fee and joint-loss observation. Published book has approximate per-day fees, inherited Twin marks, pre2018 ledger booking and incomplete OT tail; no intraday margin or guaranteed hedge-delivery claim.',
      '50K evaluation: LIMITED. 150K evaluation: LIMITED. 50K funded: LIMITED. 150K funded: LIMITED. Prepared baseline Bridge/OT/CLS paths do not establish causal joint overnight account exposure; source/native-platform parity is also absent. No new full-account pass/payout/blow-up numbers are invented. Standalone1MNQ EOD-only trail bootstrap is retained in diagnostics.json and is NOT a full-plan or intraday-breach estimate.','',
      '## Held-gap classification','',
      'Source audit after the initial raw-gap count: [CME SER8788R](https://www.cmegroup.com/content/dam/cmegroup/notices/ser/2021/06/SER-8788R.pdf), section5, removes the daily15:15-15:30CT equity-index halt effective2021-06-28. Exactly3150 of3168 FULL185 held missing minutes match that scheduled pre-removal break; they are not missing tradable bars. The engine already preserves the position and takes worse reopening stop gaps; no returns or signals changed. Four other runs total18 minutes (2020-03-18:13;2025-04-02:1;2025-11-14:3;2026-08-06:1). Their cause remains unverified, including whether any was a regulatory halt. Do not fill them or label every absence bad data. held_gap_runs.csv and held_gap_classification.json retain all models and source mapping.',
      'The table’s raw missing count includes scheduled halts. Floating OHLC equity still cannot certify latent liquidation/gap exposure or quote execution; sizing remains conditional on observed prices.',
      '## Code and remaining checks','',
      'Generated PowerLanguage: agents/codex/code/ORB30_EMA_Research.txt; all code lives in research paths. User explicitly requested a code prototype before proof. Default full-session EMA20/RR1.85/integer1% sizing on100k strategy balance; UsePercentRisk=false uses fixed1contract for ledger reconciliation. CASH EMA and RR4/0 are explicit inputs. Use1-minute CENTRAL full-session chart, IOG and appropriate Bar Magnifier, with pre2018 history for warm-up. Native compiler/backtest unavailable here: code is NOT compiled or MC-confirmed.',
      'Static review fixed midnight M30 continuity, preserved carried-position anchors across a missing flatten and blocked OR rebuild/entries until emergency exit; these cannot guarantee timer exits or broker acknowledgments. Built-in brackets initialize on entry bar and reanchor on observed actual fill; atomic gap behavior remains unverified. Code MaxContracts100 caps the otherwise uncapped Python integer diagnostic. Missing-bar carry guard exits at first available platform tick; Python instead flags an unclosed path. Author timer versus completed-minute flatten, native fills versus OHLC path, and entry-slip reanchoring are explicit differences.',
      'Independent implementation review: agents/codex/results/orb30_ema_implementation_review.md;14 execution fixtures,2 midnight-counter fixtures,100 scaling/DD arithmetic paths. No independent raw-data replication, platform parity or promotion verdict.',
      'Next: compile/replay the research code with exact session/input settings and export trades; repair/audit missing held minutes and roll-adjusted EMA provenance. No new target search, ranking or allocation change.']
    # Correct interval heading without leaving ambiguous prose in final artifact.
    text=[s.replace('95% annual effect interval','90% annual effect interval').replace('Intervals are5th/95th percentiles (90% intervals), NOT95% confidence intervals; the table label below is corrected explicitly: read the effect column as90% interval. ','Intervals are5th/95th percentiles (90% intervals). ') for s in text]
    (ROOT/'agents/codex/results/orb30_ema.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    print(pd.DataFrame(paired).to_string(index=False))
    print(pd.DataFrame(rows)[['model','period','daily_R_DSR','daily_dollar_DSR','trial_bar','mean_R_cost']].to_string(index=False))
    for p in ['design','validation','all']:print(p,d['entry_'+p])

if __name__=='__main__':main()
